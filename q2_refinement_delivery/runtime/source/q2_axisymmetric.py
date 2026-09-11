"""Finite-cylinder axisymmetric *coupled* Q2 scenario; z=0 is midplane.
The same hT/hm act at both side and end (additional geometric scenario).
This is not the infinite-cylinder Bessel test used for Q1.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import coo_matrix
from q2_core import P,properties,harmonic_with_derivatives,save_solution

class AxisymmetricFV:
    def __init__(self,nr,nz,p=P,end_transfer=True):
        self.nr,self.nz,self.p=nr,nz,p;self.m=(nr+1)*(nz+1)
        self.r=np.linspace(0,p.R,nr+1);self.z=np.linspace(0,p.L/2,nz+1)
        rf=np.r_[0,(self.r[:-1]+self.r[1:])/2,p.R];zf=np.r_[0,(self.z[:-1]+self.z[1:])/2,p.L/2]
        wr=np.diff(rf**2)/2;wz=np.diff(zf)
        self.w=(wz[:,None]*wr[None,:]).ravel();self.vol=self.w.sum()
        idx=np.arange(self.m).reshape(nz+1,nr+1)
        ir=idx[:,:-1].ravel();jr=idx[:,1:].ravel()
        iz=idx[:-1,:].ravel();jz=idx[1:,:].ravel()
        sr=(wz[:,None]*rf[None,1:-1]/(p.R/nr)).ravel()
        sz=np.broadcast_to(wr[None,:]/(p.L/2/nz),(nz,nr+1)).ravel()
        self.i=np.r_[ir,iz];self.j=np.r_[jr,jz];self.s=np.r_[sr,sz]
        self.area=np.zeros((nz+1,nr+1));self.area[:,-1]+=p.R*wz
        if end_transfer:self.area[-1,:]+=wr
        self.area=self.area.ravel();self.end_transfer=end_transfer
        self.rows=[];self.cols=[]
        for rn in (self.i,self.j):
            for cn in (self.i,self.j):
                for a in range(2):
                    for b in range(2):self.rows.append(2*rn+a);self.cols.append(2*cn+b)
        nodes=np.arange(self.m)
        self.rows += [2*nodes,2*nodes,2*nodes+1]
        self.cols += [2*nodes+1,2*nodes,2*nodes+1]
        self.rows=np.concatenate(self.rows);self.cols=np.concatenate(self.cols)
    def evaluate(self,t,y,env,jac=False):
        u=y.reshape(self.m,2);T,C=u.T;i,j=self.i,self.j
        S,k,D,Sc,kc,Dt,Dc=properties(T,C,True)
        kf,kl,kr=harmonic_with_derivatives(k[i],k[j]);df,dl,dr=harmonic_with_derivatives(D[i],D[j])
        deltaT=T[i]-T[j];deltaC=C[i]-C[j]
        q=self.s*kf*deltaT;v=self.s*df*deltaC
        f=np.empty_like(u)
        f[:,0]=np.bincount(j,weights=q,minlength=self.m)-np.bincount(i,weights=q,minlength=self.m)
        f[:,1]=np.bincount(j,weights=v,minlength=self.m)-np.bincount(i,weights=v,minlength=self.m)
        e=env(t);f[:,0]-=self.area*self.p.hT*(T-e[0]);f[:,1]-=self.area*self.p.hm*(C-e[1])
        storage=np.column_stack([self.w*S,self.w]);f/=storage
        if not jac:return f.ravel()
        left=np.empty((len(i),2,2));right=np.empty_like(left)
        left[:,0,0]=self.s*kf;right[:,0,0]=-self.s*kf
        left[:,0,1]=self.s*kl*kc[i]*deltaT;right[:,0,1]=self.s*kr*kc[j]*deltaT
        left[:,1,0]=self.s*dl*Dt[i]*deltaC;right[:,1,0]=self.s*dr*Dt[j]*deltaC
        left[:,1,1]=self.s*(df+dl*Dc[i]*deltaC);right[:,1,1]=self.s*(-df+dr*Dc[j]*deltaC)
        vals=[]
        for rn,sign in ((i,-1.),(j,1.)):
            for mat in (left,right):
                for a in range(2):
                    for b in range(2):vals.append(sign*mat[:,a,b]/storage[rn,a])
        vals += [-f[:,0]*Sc/S,-self.area*self.p.hT/storage[:,0],-self.area*self.p.hm/storage[:,1]]
        return coo_matrix((np.concatenate(vals),(self.rows,self.cols)),shape=(2*self.m,2*self.m)).tocsc()

def solve_axisymmetric(env,nr=40,nz=160,p=P,end=10800.,end_transfer=True,rtol=1e-9,atol=1e-11,max_step=30.,verbose=False,resume_path=None):
    if nr%20:raise ValueError('nr divisible by 20')
    op=AxisymmetricFV(nr,nz,p,end_transfer);y=np.tile([p.T0,p.C0],op.m)
    times=np.arange(int(end)+1,dtype=float);oi=np.arange(21)*(nr//20)
    out=np.empty((len(times),21,2));out[0,:,0]=p.T0;out[0,:,1]=p.C0
    avg=np.empty((len(times),2));avg[0]=[p.T0,p.C0]
    endpoint=np.empty((len(times),21,2));endpoint[0]=out[0]
    snapshots=[y.reshape(nz+1,nr+1,2).copy()];st=[0.]
    cuts=np.unique(np.r_[0.,env.knots[(env.knots>0)&(env.knots<end)],end])
    tic=time.perf_counter();stats={'nr':nr,'nz':nz,'end_s':end,'end_transfer':end_transfer,'rtol':rtol,'atol':atol,
       'nfev':0,'njev':0,'nlu':0,'geometry':'z in [0,L/2], coupled r-z finite cylinder','max_step_s':max_step}
    # Optional checkpoint for execution environments with hard per-call limits.
    # Each segment already restarts BDF; resuming at an existing knot preserves this method.
    restart_time=0.;prior_elapsed=0.
    token=json.dumps({'nr':nr,'nz':nz,'end':end,'rtol':rtol,'atol':atol,'max_step':max_step,
      'end_transfer':end_transfer,'parameters':vars(p),'environment':env.data.tolist()},sort_keys=True)
    if resume_path is not None:
        resume_path=Path(resume_path)
        if resume_path.exists():
            ck=np.load(resume_path,allow_pickle=False)
            if str(ck['token'])!=token:raise ValueError('Checkpoint parameters/input do not match')
            restart_time=float(ck['restart_time']);jstop=int(restart_time)+1
            y=ck['y'];out[:jstop]=ck['out'];avg[:jstop]=ck['avg'];endpoint[:jstop]=ck['endpoint']
            snapshots=list(ck['snapshots']);st=list(ck['snapshot_times'])
            old=json.loads(str(ck['stats']));prior_elapsed=float(old.get('elapsed_s',0.))
            for key in ('nfev','njev','nlu'):stats[key]=old[key]
            print('RESUME',nr,nz,restart_time,flush=True)
    for a,b in zip(cuts[:-1],cuts[1:]):
        if a<restart_time:continue
        sol=solve_ivp(lambda t,y:op.evaluate(t,y,env),(a,b),y,method='BDF',
          jac=lambda t,y:op.evaluate(t,y,env,True),rtol=rtol,atol=atol,
          dense_output=True,max_step=max_step,first_step=min(1e-3,b-a))
        if not sol.success:raise RuntimeError(sol.message)
        if not np.isfinite(sol.y).all() or np.any(sol.y[1::2]<=0):raise FloatingPointError('Invalid 2D accepted state')
        for k in ('nfev','njev','nlu'):stats[k]+=int(getattr(sol,k))
        mask=(times>a)&(times<=b+1e-8);u=sol.sol(times[mask]).reshape(nz+1,nr+1,2,-1)
        out[mask]=u[0,oi].transpose(2,0,1);endpoint[mask]=u[-1,oi].transpose(2,0,1)
        avg[mask]=np.einsum('i,ijt->tj',op.w,u.reshape(op.m,2,-1))/op.vol
        y=sol.y[:,-1]
        if b in (1800,3600,5400,7200,9000,10800):snapshots.append(y.reshape(nz+1,nr+1,2).copy());st.append(b)
        if resume_path is not None and int(b)%1800==0:
            resume_path.parent.mkdir(parents=True,exist_ok=True)
            stats['elapsed_s']=prior_elapsed+time.perf_counter()-tic
            np.savez_compressed(resume_path,token=token,restart_time=b,y=y,out=out[:int(b)+1],
              avg=avg[:int(b)+1],endpoint=endpoint[:int(b)+1],snapshots=np.array(snapshots),
              snapshot_times=np.array(st),stats=json.dumps(stats))
        if verbose and int(b)%1800==0:print('AXISYMMETRIC',nr,nz,b,flush=True)
    stats['elapsed_s']=prior_elapsed+time.perf_counter()-tic
    return {'time_s':times,'radius_cm':np.linspace(0,2,21),'temperature_degC':out[:,:,0],
      'moisture_dry_basis':out[:,:,1],'average_temperature_degC':avg[:,0],
      'average_moisture_dry_basis':avg[:,1],'end_temperature_degC':endpoint[:,:,0],
      'end_moisture_dry_basis':endpoint[:,:,1],'r_m':op.r,'z_m':op.z,'volume_weights':op.w,
      'snapshot_times_s':np.array(st),'temperature_snapshots_2d':np.array(snapshots)[:,:,:,0],
      'moisture_snapshots_2d':np.array(snapshots)[:,:,:,1],'stats':stats}
