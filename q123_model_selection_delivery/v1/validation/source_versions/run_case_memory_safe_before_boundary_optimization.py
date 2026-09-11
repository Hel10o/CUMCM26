"""One immutable run root, raw fields, independently integrated boundary ledger."""
import sys,json,time,hashlib,platform,traceback
from pathlib import Path
from dataclasses import asdict
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.special import roots_legendre
from model import Config,Model,Environment,T0,C0,CL,CD

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def serial(o):
    if isinstance(o,np.ndarray):return o.tolist()
    if isinstance(o,np.generic):return o.item()
    raise TypeError(type(o))
def main(config_path,output):
    started=time.time();output=Path(output);output.mkdir(parents=True,exist_ok=False)
    cfg=Config(**json.loads(Path(config_path).read_text()))
    inp=Path(__file__).resolve().parents[1]/'inputs/environment_extracted.csv'
    env=Environment(np.loadtxt(inp,delimiter=',',skiprows=1),cfg.nominal_future);m=Model(cfg,env)
    meta=dict(config=asdict(cfg),input_sha256=digest(inp),source_sha256={p.name:digest(p) for p in Path(__file__).parent.glob('*.py')},python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,start_unix=started,scenario_status='conditional',future=env.future,activity_K=m.K,relative_humidity_future=m.rh_future,command=sys.argv)
    (output/'provenance.json').write_text(json.dumps(meta,default=serial,indent=2))
    y=m.initial();t=0.;tcrit=None;cum=np.zeros(8);cum3=np.zeros(8)
    records=[];fields=[];fieldtimes=[];historyT=[];historyC=[];glob=[];ledger=[];nfev=njev=nlu=0
    def record(tt,yy):
        if records and abs(records[-1]-tt)<1e-7:return
        mm=m.summary(tt,yy);a=yy.reshape(m.shape+(2,));ii=mm.pop('max_index');ri,zi=np.unravel_index(ii,m.shape)
        mm['max_r']=m.r[ri];mm['max_z']=m.z[zi];mm['sideT']=a[-1,0,0];mm['sideC']=a[-1,0,1];mm['coreT']=a[0,0,0];mm['coreC']=a[0,0,1]
        mm['end_centerT']=a[0,-1,0];mm['end_centerC']=a[0,-1,1];mm['cornerT']=a[-1,-1,0];mm['cornerC']=a[-1,-1,1]
        records.append(tt);glob.append(mm);historyT.append(a[:,0,0].copy());historyC.append(a[:,0,1].copy())
    record(0.,y);fields.append(y.reshape(m.shape+(2,)).copy());fieldtimes.append(0.)
    initial=m.summary(0,y)
    bound=1800. if cfg.question==1 else cfg.horizon
    available_event=cfg.question!=1  # Check transient crossings even if equilibrium exceeds target.
    gx5,gw5=roots_legendre(5);gx3,gw3=roots_legendre(3)
    def event(tt,yy):return yy.reshape(-1,2)[:,1].max()-.15
    event.direction=-1;event.terminal=True
    snapshots=(np.arange(0,1801,300).tolist() if cfg.question==1 else sorted(set(np.arange(0,14401,1800).tolist()+np.arange(21600,bound+1,21600).tolist())))
    while t<bound-1e-8:
        if t<14400:
            end=min(bound,(int(t/1800+1e-7)+1)*1800.,14400.)
        else:end=min(bound,t+21600.)
        m.future=t>=14400-1e-8
        sol=solve_ivp(m.rhs,(t,end),y,method=cfg.method,rtol=cfg.rtol,atol=np.tile([cfg.atol_T,cfg.atol_C],m.n),jac_sparsity=m.sparsity,dense_output=True,max_step=cfg.max_step_late if m.future else cfg.max_step_early,events=event if available_event and tcrit is None else None)
        nfev+=sol.nfev;njev+=sol.njev;nlu+=sol.nlu
        if not sol.success:raise RuntimeError(sol.message)
        end=float(sol.t[-1])
        # Quadrature on solver-accepted intervals, not identity evaluation.
        for ta,tb in zip(sol.t[:-1],sol.t[1:]):
            tm=(ta+tb)/2;dh=(tb-ta)/2
            for gx,gw,cu in [(gx5,gw5,cum),(gx3,gw3,cum3)]:
                times=tm+dh*gx;ys=sol.sol(times)
                rr=np.array([m.summary(tx,ys[:,j])['rates'] for j,tx in enumerate(times)])
                cu+=dh*(gw@rr)
        if end<=1800:
            step=1.
        elif end<=14400:step=10.
        else:step=60.
        sample=np.arange(np.floor(t/step+1)*step,end+1e-8,step)
        if t==0:sample=np.unique(np.r_[.001,.01,.1,.3,sample])
        sample=sample[(sample>t)&(sample<=end)]
        for tt,yy in zip(sample,sol.sol(sample).T):record(tt,yy)
        for ts in snapshots:
            if ts>t+1e-7 and ts<=end+1e-7:
                fieldtimes.append(ts);fields.append(sol.sol(ts).reshape(m.shape+(2,)).copy())
        y=sol.y[:,-1].copy();t=end
        mm=m.summary(t,y)
        massres=mm['Mwater']-initial['Mwater']+cum[0]+cum[4]
        eres=mm['enthalpy']-initial['enthalpy']-cum[1]-cum[5]+cum[2]+cum[6]+cum[3]+cum[7]
        ledger.append(dict(t=t,cumulative5=cum.copy(),cumulative3=cum3.copy(),mass_residual=massres,energy_residual=eres,**{k:v for k,v in mm.items() if k!='rates'}))
        print(json.dumps(dict(t=t,maxC=mm['maxC'],minT=mm['minT'],mass_residual=massres,energy_residual=eres,nfev=nfev,elapsed=time.time()-started)),flush=True)
        if sol.status==1:
            tcrit=t;bound=tcrit+cfg.event_margin
            print('EVENT',tcrit,'continue genuinely to',bound,flush=True)
        if t>=bound-1e-8:break
        del sol  # Release dense interpolants before the next large solve.
    record(t,y)
    if fieldtimes[-1]!=t:fieldtimes.append(t);fields.append(y.reshape(m.shape+(2,)).copy())
    keys=[k for k in glob[0] if k!='rates'];metrics=np.array([[g[k] for k in keys] for g in glob],float)
    rates=np.array([g['rates'] for g in glob])
    np.savez_compressed(output/'solution.npz',time=np.array(records),r=m.r,z=m.z,volume=m.V.reshape(m.shape),midplane_T=np.array(historyT),midplane_C=np.array(historyC),metric_names=np.array(keys),metrics=metrics,rates=rates,field_time=fieldtimes,fields=np.array(fields),side_area=m.side.reshape(m.shape),end_area=m.end.reshape(m.shape))
    np.savetxt(output/'history.csv',np.column_stack([records,metrics,rates]),delimiter=',',header=','.join(['time_s']+keys+['side_water_kg_s','side_heat_W','side_latent_W','side_sensible_W','end_water_kg_s','end_heat_W','end_latent_W','end_sensible_W']),comments='')
    (output/'ledger.json').write_text(json.dumps(ledger,default=serial,indent=2))
    # Independent integration from saved history, a different temporal grid.
    from scipy.integrate import simpson
    integrated=np.array([simpson(rates[:,j],x=records) for j in range(8)])
    final=m.summary(t,y)
    postmass=final['Mwater']-initial['Mwater']+integrated[0]+integrated[4]
    postenergy=final['enthalpy']-initial['enthalpy']-integrated[1]-integrated[5]+integrated[2]+integrated[6]+integrated[3]+integrated[7]
    water_scale=max(abs(initial['Mwater']-final['Mwater']),1e-6)
    heat_scale=max(abs(cum[1]+cum[5]),1.)
    result=dict(initial=initial,final=final,t_final=t,event_equal_s=tcrit,execution_s=t if tcrit is not None else None,strict_pass=bool(final['maxC']<.15) if tcrit is not None else False,
                status='crossed_and_continued' if tcrit is not None else ('q1_complete' if cfg.question==1 else ('equilibrium_above_threshold_and_no_crossing_in_horizon' if cfg.ceq>=.15 and not cfg.baseline else 'not_crossed_in_horizon')),
                equilibrium_C=cfg.ceq if not cfg.baseline else float(env.future[1]),elapsed_s=time.time()-started,nfev=nfev,njev=njev,nlu=nlu,
                cumulative=cum,gauss3=cum3,posthoc_simpson=integrated,mass_residual_gauss5=massres,energy_residual_gauss5=eres,mass_residual_posthoc=postmass,energy_residual_posthoc=postenergy,
                mass_residual_rel=massres/water_scale,energy_residual_rel=eres/heat_scale,mass_posthoc_rel=postmass/water_scale,energy_posthoc_rel=postenergy/heat_scale,heat_scale=heat_scale,water_scale=water_scale,
                acceptance=dict(gauss_relative=2e-5,posthoc_relative=2e-3),run_complete=True)
    (output/'result.json').write_text(json.dumps(result,default=serial,indent=2))
    print('COMPLETE',json.dumps(result,default=serial),flush=True)
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('run_case.py CONFIG.json NEW_OUTPUT_DIRECTORY')
    try:main(sys.argv[1],sys.argv[2])
    except Exception:
        traceback.print_exc();raise
