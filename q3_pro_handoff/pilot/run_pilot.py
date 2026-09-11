"""Bounded Q3 numerical reconnaissance, NOT a certified result3 solution.

Run from repository root with its scientific Python runtime. Imported Q2 source
is read-only. Last-value environmental extension is an explicit scenario.
"""
from pathlib import Path
import csv, json, sys, time, hashlib, warnings
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import coo_matrix
from scipy.special import exp1
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'q2_final_delivery/source'))
from q2_core import CoupledFV, Environment, P, load_environment, properties, harmonic_with_derivatives
from q2_spectral import Spectral
OUT=Path(__file__).resolve().parent

def primitive(C):
    """Integral from 0 to C of exp(-0.45/u) du; derivative exp(-0.45/C)."""
    return C*np.exp(-.45/C)-.45*exp1(.45/C)

class KirchhoffFV(CoupledFV):
    """Same conservative dual volumes/thermal operator/Robin nodes as Q2 FV.

    Internal moisture flux: harmonic A(T) * [Phi(C_L)-Phi(C_R)].
    For D=A(T)*exp(-.45/C), this integrates C-dependence exactly at constant T.
    Temperature variation in one face interval still uses harmonic A(T).
    """
    def evaluate(self,t,y,env,with_jac=False):
        base=super().evaluate(t,y,env,with_jac)
        u=y.reshape(self.m,2);T,C=u.T
        _,_,D,_,_,Dt,Dc=properties(T,C,True)
        df,dl,dr=harmonic_with_derivatives(D[:-1],D[1:])
        A=.0024*np.exp(-3850/(T+273.15));At=A*3850/(T+273.15)**2
        af,al,ar=harmonic_with_derivatives(A[:-1],A[1:])
        dC=C[:-1]-C[1:];dPhi=np.diff(primitive(C))*-1
        correction=self.s*(af*dPhi-df*dC)
        if not with_jac:
            f=base.reshape(self.m,2).copy()
            f[:-1,1]-=correction/self.w[:-1]
            f[1:,1]+=correction/self.w[1:]
            return f.ravel()
        left=np.column_stack([self.s*(al*At[:-1]*dPhi-dl*Dt[:-1]*dC),
             self.s*(af*np.exp(-.45/C[:-1])-df-dl*Dc[:-1]*dC)])
        right=np.column_stack([self.s*(ar*At[1:]*dPhi-dr*Dt[1:]*dC),
             self.s*(-af*np.exp(-.45/C[1:])+df-dr*Dc[1:]*dC)])
        ii=np.arange(self.n);rows=[];cols=[];vals=[]
        for ro,sign in [(0,-1),(1,1)]:
            for co,der in [(0,left),(1,right)]:
                for b in range(2):
                    rows.append(2*(ii+ro)+1);cols.append(2*(ii+co)+b)
                    vals.append(sign*der[:,b]/self.w[ii+ro])
        extra=coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=base.shape).tocsc()
        return base+extra

def verify_new_operator():
    op=KirchhoffFV(24);r=op.r/P.R
    y=np.column_stack([45+5*r,.2-.14*r*r]).ravel()
    env=lambda t:np.array([50.165,.04986])
    J=op.evaluate(0,y,env,True).toarray()
    ref=np.zeros_like(J)
    for j in range(len(y)):
        h=1e-4 if j%2==0 else 2e-7
        yp=y.copy();ym=y.copy();yp[j]+=h;ym[j]-=h
        ref[:,j]=(op.evaluate(0,yp,env)-op.evaluate(0,ym,env))/(2*h)
    f=op.evaluate(0,y,env).reshape(-1,2)
    residual=float(op.w@f[:,1]+P.R*P.hm*(y[-1]-.04986))
    C=np.geomspace(.04986,2.55,100);h=1e-6
    pd=(primitive(C+h)-primitive(C-h))/(2*h)
    return {'analytic_jacobian_vs_central_relative_max':float(np.max(abs(J-ref))/np.max(abs(ref))),
       'moisture_conservation_rhs_residual':residual,
       'primitive_derivative_relative_max':float(np.max(abs(pd-np.exp(-.45/C))/np.exp(-.45/C)))}

def surface_roots_probe():
    """Synthetic uniform interior moisture with T=50.165, never actual states."""
    rows=[]
    for n in [32,64,96,160]:
        op=Spectral(n);factor=op.A*op.diag
        for near in [.08,.10,.15,.20,.30,.50]:
            def f(c):
                D=properties(50.165,c)[2]
                return factor*D*(c-near)+P.hm*(c-.04986)
            xx=np.linspace(.04986,near,30001);ff=f(xx);roots=[]
            for i in np.flatnonzero(ff[:-1]*ff[1:]<0):
                roots.append(brentq(f,xx[i],xx[i+1],xtol=1e-15))
            rows.append({'n':n,'synthetic_uniform_interior_C':near,'T_C':50.165,
                         'surface_equation_roots':roots,'root_count':len(roots)})
    return {'state_type':'synthetic uniform interior, not accepted Q2/Q3 trajectory',
       'equation':'(2/R)*G_NN*D(T,Cs)*(Cs-near)+hm*(Cs-Cenv)=0',
       'cases':rows}

def run_case(n,kind,rtol=2e-8,atol_T=2e-9,atol_C=2e-10,continuation='hold_last'):
    a,audit=load_environment(ROOT/'q2_final_delivery/inputs/附件1.xlsx')
    env=Environment(a,extension='hold_last')
    if continuation=='hold_last':held=a[-1,1:]
    elif continuation=='last_hour_mean':held=a[(a[:,0]>=10800)&(a[:,0]<=14400),1:].mean(axis=0)
    elif continuation=='nominal_50_005':held=np.array([50.,.05])
    else:raise ValueError(continuation)
    stem=f'{kind}_n{n}' if continuation=='hold_last' else f'{kind}_{continuation}_n{n}'
    op=(CoupledFV if kind=='harmonic' else KirchhoffFV)(n)
    y=np.tile([P.T0,P.C0],n+1);tic=time.perf_counter()
    duration_limit=180*3600.
    cuts=np.r_[a[:,0],np.arange(21600,duration_limit+1,21600)]
    def event(t,y):return float(y[1::2].max()-.15)
    event.terminal=True;event.direction=-1
    stat={'n':n,'method':kind,'dr_m':op.dr,'rtol':rtol,'atol_T':atol_T,'atol_C':atol_C,
      'environment_extension':f'{continuation} after 14400 s; scenario assumption, not observation',
      'continuation':continuation,'held_environment_T_C_kgkg':held.tolist(),
      'last_environment':a[-1].tolist(),'input_sha256':audit['sha256'],
      'nfev':0,'njev':0,'nlu':0,'accepted_steps':0,'min_C_accepted':P.C0,
      'min_D_accepted':float(properties(P.T0,P.C0)[2]),'max_C_radial_increase':0.,
      'max_C_temporal_increase_at_sampled_nodes':0.,'Cmax_node_always_center_with_tolerance':True,
      'max_rhs_C_during_accepted_steps':-float('inf'),'max_water_balance_segment_error':0.,
      'status':'running','formal_answer':False}
    rows=[[0.,0.,P.C0,P.C0,P.C0,P.C0,P.C0]]
    balance=0.;previous=y.copy();record_times=[]
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        # Keep all 0..4h history unchanged; use right-limit boundary on later segments.
        segment_env=env if hi<=14400 else lambda tt:np.broadcast_to(held,np.shape(tt)+(2,))
        fun=lambda t,z:op.evaluate(t,z,segment_env)
        jac=lambda t,z:op.evaluate(t,z,segment_env,True)
        maxstep=20. if hi<=14400 else 300.
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            sol=solve_ivp(fun,(lo,hi),y,method='BDF',jac=jac,rtol=rtol,
                atol=np.tile([atol_T,atol_C],n+1),max_step=maxstep,dense_output=True,
                events=event,first_step=min(.001,hi-lo))
        if ws:stat.setdefault('warnings',[]).extend(str(w.message) for w in ws)
        if not sol.success:raise RuntimeError(sol.message)
        C=sol.y[1::2];T=sol.y[::2]
        stat['min_C_accepted']=min(stat['min_C_accepted'],float(C.min()))
        stat['min_D_accepted']=min(stat['min_D_accepted'],float(properties(T,C)[2].min()))
        stat['max_C_radial_increase']=max(stat['max_C_radial_increase'],float(np.diff(C,axis=0).max()))
        cdiff=np.diff(C,axis=1)
        inc=float(cdiff.max(initial=0))
        if inc>stat['max_C_temporal_increase_at_sampled_nodes']:
            ni,ti=np.unravel_index(np.argmax(cdiff),cdiff.shape)
            stat['max_temporal_increase_location']={'r_m':float(op.r[ni]),'start_s':float(sol.t[ti]),
                'end_s':float(sol.t[ti+1]),'C_start':float(C[ni,ti]),'C_end':float(C[ni,ti+1])}
            stat['max_C_temporal_increase_at_sampled_nodes']=inc
        stat['Cmax_node_always_center_with_tolerance'] &= bool(np.all(C.max(axis=0)-C[0]<1e-10))
        # Independent surface flux quadrature using accepted dense output.
        gx,gw=np.polynomial.legendre.leggauss(4);jint=0.
        for aa,bb in zip(sol.t[:-1],sol.t[1:]):
            ts=(aa+bb)/2+(bb-aa)*gx/2;ss=sol.sol(ts)
            jint+=float((P.R*P.hm*(ss[-1]-segment_env(ts)[:,1]))@gw*(bb-aa)/2)
        balance=float(op.w@(sol.y[1::2,-1]-y[1::2])+jint)
        stat['max_water_balance_segment_error']=max(stat['max_water_balance_segment_error'],abs(balance)/op.v)
        for key in ('nfev','njev','nlu'):stat[key]+=int(getattr(sol,key))
        stat['accepted_steps']+=len(sol.t)-1
        y=sol.y[:,-1];end=float(sol.t[-1]);last=y.reshape(n+1,2)
        # Safe full-field time derivative diagnostic at segment endpoints.
        stat['max_rhs_C_during_accepted_steps']=max(stat['max_rhs_C_during_accepted_steps'],float(fun(end,y)[1::2].max()))
        if end%21600<1e-6 or end in [10800.,14400.] or len(sol.t_events[0]):
            vals=np.interp(np.linspace(0,P.R,5),op.r,last[:,1])
            rows.append([end,end/3600,*vals]);record_times.append(end)
            print(kind,n,'t_h',end/3600,'C_center_surface',last[0,1],last[-1,1],flush=True)
        if len(sol.t_events[0]):
            stat.update(status='event_found',event_time_s=end,event_time_h=end/3600,
                 event_C_center=float(last[0,1]),event_C_surface=float(last[-1,1]),
                 event_C_max=float(last[:,1].max()),event_max_radius_m=float(op.r[np.argmax(last[:,1])]),
                 event_C_center_slope_per_s=float(fun(end,y)[1]),
                 event_T_center=float(last[0,0]),event_T_surface=float(last[-1,0]),
                 event_D_center_surface=properties(last[[0,-1],0],last[[0,-1],1])[2].tolist(),
                 event_surface_D_over_hm_m=float(properties(last[-1,0],last[-1,1])[2]/P.hm))
            with (OUT/f'{stem}_event_profile.csv').open('w',newline='',encoding='utf-8') as fh:
                wr=csv.writer(fh);wr.writerow(['r_m','T_degC','C_kgkg']);wr.writerows(zip(op.r,last[:,0],last[:,1]))
            break
    else:stat['status']='no_event_by_180h'
    stat['elapsed_wall_s']=time.perf_counter()-tic
    stat['critical_time_interpretation']='first downward crossing of full discrete-field max C=0.15; strict < holds immediately after crossing'
    stat['temporal_diagnostic_note']='max_rhs_C is evaluated at segment endpoints; temporal increase checks use all accepted states'
    (OUT/f'{stem}.json').write_text(json.dumps(stat,indent=2,ensure_ascii=False),encoding='utf-8')
    with (OUT/f'{stem}_trajectory.csv').open('w',newline='',encoding='utf-8') as fh:
        wr=csv.writer(fh);wr.writerow(['time_s','time_h','C_r0cm','C_r0.5cm','C_r1cm','C_r1.5cm','C_r2cm']);wr.writerows(rows)
    print(json.dumps(stat),flush=True)
    return stat

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['harmonic','kirchhoff','probes'],required=True);ap.add_argument('--n',type=int,default=128)
    ap.add_argument('--continuation',choices=['hold_last','last_hour_mean','nominal_50_005'],default='hold_last')
    args=ap.parse_args()
    if args.case=='probes':
        data={'operator_verification':verify_new_operator(),'surface_roots':surface_roots_probe()}
        (OUT/'operator_and_surface_probe.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(data,ensure_ascii=False),flush=True)
    else:run_case(args.n,args.case,continuation=args.continuation)

if __name__=='__main__':main()
