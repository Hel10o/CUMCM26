"""Independent 1-D cell-centred, H/C state, Radau reference.
Unlike main nodal T/C scheme, boundary surface T and C have zero storage
and are solved algebraically through half-cell + interface resistances.
The same stated constitutive scenario is used; no old numerical trajectory
is used as input or calibration. Refinement is required for surface gradients.
"""
from pathlib import Path
import json,time,sys,hashlib
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix
from model import Environment,psat,latent_heat,CD,CL,T0,C0,R,L

def main(n,ceq,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[1];env=Environment(np.loadtxt(root/'inputs/environment_extracted.csv',delimiter=',',skiprows=1))
    rho=(650+128*C0)/(1+C0);rh=101325*env.future[1]/(.621945+env.future[1])/psat(env.future[0]);K=ceq*(1-rh)/rh
    dr=R/n;r=(np.arange(n)+.5)*dr;rf=np.arange(n+1)*dr;V=np.pi*L*np.diff(rf**2);area=2*np.pi*R*L;ge=2*np.pi*L*rf[1:-1]/dr
    sp=lil_matrix((2*n,2*n))
    for i in range(n):
        for j in range(max(0,i-1),min(n,i+2)):sp[2*i:2*i+2,2*j:2*j+2]=1.
    future=False
    def surface(t,T,C,k,D):
        Ta,W=env(t,future);pv=101325*W/(.621945+W)
        cv=(101325-pv)/(287.055*(Ta+273.15))*1006+pv/(461.5*(Ta+273.15))*1850
        Kp=25/cv/(461.5*(Ta+273.15))
        A=1/(dr/(2*rho*D)+1/(rho*8e-7))
        b=Kp/A
        Ts=T
        # Strict scalar Newton with monotone heat balance; no temperature clipping.
        for it in range(15):
            p=psat(Ts);dp=p*17.27*237.3/(Ts+237.3)**2
            u=C+b*pv;v=u-K-b*p;disc=np.sqrt(v*v+4*u*K)
            Ci=(v+disc)/2 if v>=0 else 2*u*K/(disc-v)
            j=A*(C-Ci)
            dj=Kp*(Ci/(Ci+K))*dp/(1+b*p*K/(Ci+K)**2)
            f=k*2/dr*(Ts-T)-25*(Ta-Ts)+latent_heat(Ts)*j
            df=k*2/dr+25-2361*j+latent_heat(Ts)*dj
            step=f/df;Ts-=step
            if abs(step)<1e-10:break
        else:raise RuntimeError('Surface Newton failed')
        Cs=C-dr*j/(2*rho*D)
        return Ts,Cs,j,25*(Ta-Ts)
    def split(y):
        a=y.reshape(n,2);C=a[:,1];T=T0+a[:,0]/(rho*(CD+CL*C))
        if not np.isfinite(y).all() or C.min()<=0:raise FloatingPointError('Invalid independent state')
        k=.21+.38*C/(1+C);D=.0024*np.exp(-3850/(T+273.15)-.45/C)
        return T,C,k,D
    def rhs(t,y):
        T,C,k,D=split(y);jm=rho*(D[:-1]+D[1:])/2*(C[:-1]-C[1:])*ge
        fh=(k[:-1]+k[1:])/2*(T[:-1]-T[1:])*ge+CL*((T[:-1]+T[1:])/2-T0)*jm
        mc=np.zeros(n);eh=np.zeros(n);mc[:-1]-=jm;mc[1:]+=jm;eh[:-1]-=fh;eh[1:]+=fh
        Ts,Cs,j,q=surface(t,T[-1],C[-1],k[-1],D[-1]);mc[-1]-=j*area
        eh[-1]+=(q-latent_heat(Ts)*j-CL*(Ts-T0)*j)*area
        return np.column_stack([eh/V,mc/(rho*V)]).ravel()
    def event(t,y):
        C=y.reshape(n,2)[:,1];Caxis=(9*C[0]-C[1])/8
        return max(C.max(),Caxis)-.15
    event.direction=-1;event.terminal=True
    y=np.column_stack([np.zeros(n),np.full(n,C0)]).ravel();t=0.;start=time.time();stats=[];save=[];ft=[]
    while t<864000:
        future=t>=14400-1e-8;end=min((int(t/1800+1e-8)+1)*1800,14400) if not future else t+21600
        sol=solve_ivp(rhs,(t,end),y,method='Radau',jac_sparsity=sp.tocsc(),rtol=1e-8,atol=np.tile([.003,2e-11],n),max_step=20 if not future else 600,events=event,dense_output=False)
        if not sol.success:raise RuntimeError(sol.message)
        t=sol.t[-1];y=sol.y[:,-1];T,C,k,D=split(y);Ts,Cs,j,q=surface(t,T[-1],C[-1],k[-1],D[-1])
        stats.append(dict(t=float(t),maxC=float(C.max()),Caxis=float((9*C[0]-C[1])/8),Ts=float(Ts),Cs=float(Cs),mass=float(rho*np.dot(V,C)),enthalpy=float(np.dot(V,y.reshape(n,2)[:,0]))))
        if t<=14400 or sol.status==1:save.append(np.column_stack([T,C]));ft.append(t)
        print(json.dumps(dict(n=n,t=float(t),elapsed=time.time()-start)),flush=True)
        status=sol.status;del sol
        if status==1:break
    np.savez_compressed(out/'solution.npz',r=r,time=ft,fields=save)
    d=dict(n=n,ceq=ceq,event_equal_s=float(t) if status==1 else None,elapsed_s=time.time()-start,method='independent cell-centred conserved H/C Radau with algebraic zero-storage surface',stats=stats,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),input_sha256=hashlib.sha256((root/'inputs/environment_extracted.csv').read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(d,indent=2));print('COMPLETE',json.dumps(d),flush=True)
if __name__=='__main__':main(int(sys.argv[1]),float(sys.argv[2]),sys.argv[3])
