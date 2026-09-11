"""Conservative axisymmetric, fixed-skeleton heat/water model.
C is kg water / kg dry matter. T is Celsius. SI otherwise.
F is a stated conditional model, not a fit to the old simulated trajectory.
"""
from dataclasses import dataclass, asdict
import numpy as np
from scipy.sparse import coo_matrix

@dataclass(frozen=True)
class Config:
    question: int = 23
    nr: int = 32
    nz: int = 0
    latent: bool = True
    baseline: bool = False
    ceq: float = 0.075
    grading_r: float = 1.5
    grading_z: float = 1.5
    end_factor: float = 1.0
    hT: float = 25.0
    hm: float = 8e-7
    pressure: float = 101325.
    gas_multiplier: float = 1.
    method: str = 'BDF'
    rtol: float = 2e-7
    atol_T: float = 2e-8
    atol_C: float = 2e-10
    max_step_early: float = 30.
    max_step_late: float = 900.
    horizon: float = 864000.
    event_margin: float = 600.
    nominal_future: bool = False
    face_rule: str = 'arithmetic'

R=.02
L=.25
H=L/2
C0=2.55
T0=28.
CD=1450.
CL=4186.

def psat(T):
    """FAO56 eq 11: Pa, T in Celsius; used in stated temperature range."""
    return 610.8*np.exp(17.27*T/(T+237.3))

def latent_heat(T):
    """FAO56 Annex3 lambda=2.501-0.002361*T MJ/kg."""
    return 2.501e6-2361.*T

class Environment:
    def __init__(self,a,nominal=False):
        self.a=np.asarray(a)
        if self.a.shape!=(241,3) or not np.isfinite(self.a).all():
            raise ValueError('Expected 241 finite environmental records')
        if not np.array_equal(self.a[:,0],np.arange(241)*60):
            raise ValueError('Time grid mismatch')
        self.future=np.array([50.,.05]) if nominal else self.a[180:,1:].mean(0)
    def __call__(self,t,future=False):
        if future or t>14400: return self.future
        return np.array([np.interp(t,self.a[:,0],self.a[:,k]) for k in (1,2)])

class Model:
    def __init__(self,cfg,env):
        self.cfg=cfg;self.env=env
        self.r=R*(1-(1-np.linspace(0,1,cfg.nr+1))**cfg.grading_r)
        self.z=H*(1-(1-np.linspace(0,1,cfg.nz+1))**cfg.grading_z) if cfg.nz else np.array([0.])
        rf=np.r_[0.,(self.r[1:]+self.r[:-1])/2,R]
        wr=np.diff(rf**2)/2
        zf=np.r_[0.,(self.z[1:]+self.z[:-1])/2,H] if cfg.nz else np.array([0.,H])
        wz=np.diff(zf)
        self.shape=(len(self.r),len(self.z)); self.n=np.prod(self.shape).item()
        ids=np.arange(self.n).reshape(self.shape)
        self.V=(4*np.pi*wr[:,None]*wz).ravel()
        left=[ids[:-1,:].ravel()];right=[ids[1:,:].ravel()]
        geo=[(4*np.pi*rf[1:-1,None]*wz/np.diff(self.r)[:,None]).ravel()]
        if cfg.nz:
            left.append(ids[:,:-1].ravel());right.append(ids[:,1:].ravel())
            geo.append((4*np.pi*wr[:,None]/np.diff(self.z)[None,:]).ravel())
        self.left=np.concatenate(left);self.right=np.concatenate(right);self.geo=np.concatenate(geo)
        side=np.zeros(self.shape);side[-1,:]=4*np.pi*R*wz
        end=np.zeros(self.shape)
        if cfg.nz:end[:,-1]=4*np.pi*wr*cfg.end_factor
        self.side=side.ravel();self.end=end.ravel()
        self.area=self.side+self.end
        self.bound=np.flatnonzero(self.area)
        self.rhod=(820. if cfg.question==1 else 650+128*C0)/(1+C0)
        rh=cfg.pressure*env.future[1]/(.621945+env.future[1])/psat(env.future[0])
        self.rh_future=float(rh)
        self.K=cfg.ceq*(1-rh)/rh
        if self.K<=0:raise ValueError('Scenario requires unsaturated future environment')
        row=[];col=[]
        for a,b in [(self.left,self.left),(self.right,self.left),(self.left,self.right),(self.right,self.right),(np.arange(self.n),np.arange(self.n))]:
            for i in (0,1):
                for j in (0,1):
                    row.append(2*a+i);col.append(2*b+j)
        self.sparsity=coo_matrix((np.ones(sum(len(v) for v in row)),(np.concatenate(row),np.concatenate(col))),shape=(2*self.n,2*self.n)).tocsc()
        self.future=False
    def initial(self):
        y=np.empty((self.n,2));y[:,0]=T0;y[:,1]=C0
        return y.ravel()
    def properties(self,T,C):
        if np.min(C)<=0 or not np.isfinite(C).all() or np.min(T)<=-200:
            raise FloatingPointError('Invalid state; no clipping or diffusivity floor')
        if self.cfg.question==1:
            k=np.full_like(C,.36);D=7e-9*np.exp(-.89/C)
            SB=np.full_like(C,820.*2600.)
        else:
            k=.21+.38*C/(1+C)
            D=.0024*np.exp(-3850/(T+273.15)-.45/C)
            SB=(650+128*C)*(1450+2736*C/(1+C))
        S=SB if self.cfg.baseline else self.rhod*(CD+CL*C)
        return S,k,D
    def surface(self,t,T,C):
        Ta,W=self.env(t,self.future)
        if self.cfg.baseline:
            js=self.rhod*self.cfg.hm*(C-W)
            return js,np.zeros_like(js),np.full_like(js,np.nan),Ta,W
        # Air is conditionally interpreted as humidity ratio. The given hm is
        # material-side conductance, not silently equated to gas-film velocity.
        pv=self.cfg.pressure*W/(.621945+W)
        # Lewis number = 1, ideal moist air. cp_vol is at bulk gas temperature.
        rho_da=(self.cfg.pressure-pv)/(287.055*(Ta+273.15))
        rho_v=pv/(461.5*(Ta+273.15))
        cp_vol=rho_da*1006.+rho_v*1850.
        kg=self.cfg.gas_multiplier*self.cfg.hT/cp_vol
        Kp=kg/(461.5*(Ta+273.15))
        A=self.rhod*self.cfg.hm
        b=Kp/A
        p=psat(T)
        u=C+b*pv
        v=u-self.K-b*p
        d=np.sqrt(v*v+4*u*self.K)
        Ci=np.where(v>=0,(v+d)/2,2*u*self.K/(d-v))
        js=A*(C-Ci)
        drive=Ci/(Ci+self.K)*p-pv
        return js,drive,Ci,Ta,W
    def evaluate(self,t,y,with_metrics=False):
        a=y.reshape(self.n,2);T=a[:,0];C=a[:,1]
        S,k,D=self.properties(T,C)
        l=self.left;r=self.right
        if self.cfg.face_rule=='harmonic':
            kf=2*k[l]*k[r]/(k[l]+k[r]);Df=2*D[l]*D[r]/(D[l]+D[r])
        else:
            kf=(k[l]+k[r])/2;Df=(D[l]+D[r])/2
        J=self.rhod*Df*(C[l]-C[r])*self.geo # kg/s left -> right
        Q=kf*(T[l]-T[r])*self.geo
        hlface=CL*((T[l]+T[r])/2-T0)
        F=Q if self.cfg.baseline else Q+hlface*J
        mw=np.bincount(r,weights=J,minlength=self.n)-np.bincount(l,weights=J,minlength=self.n)
        eh=np.bincount(r,weights=F,minlength=self.n)-np.bincount(l,weights=F,minlength=self.n)
        ib=self.bound
        js,drive,Ci,Ta,W=self.surface(t,T[ib],C[ib])
        qin=self.cfg.hT*(Ta-T[ib])
        qlat=(latent_heat(T[ib])*js if self.cfg.latent and not self.cfg.baseline else np.zeros_like(js))
        hs=CL*(T[ib]-T0)*js if not self.cfg.baseline else np.zeros_like(js)
        mw[ib]-=js*self.area[ib]
        eh[ib]+=(qin-qlat-hs)*self.area[ib]
        Ct=mw/(self.rhod*self.V)
        if self.cfg.baseline: Tt=eh/(self.V*S)
        else:Tt=(eh/self.V-self.rhod*CL*(T-T0)*Ct)/S
        out=np.column_stack((Tt,Ct)).ravel()
        if not with_metrics:return out
        rates=[]
        for area in (self.side[ib],self.end[ib]):
            rates.extend([np.dot(area,x) for x in (js,qin,qlat,hs)])
        energy=np.dot(self.V,self.rhod*(CD+CL*C)*(T-T0)) if not self.cfg.baseline else np.nan
        m=dict(Mdry=self.rhod*self.V.sum(),Mwater=self.rhod*np.dot(self.V,C),enthalpy=energy,
               meanT=np.dot(self.V,T)/self.V.sum(),meanC=np.dot(self.V,C)/self.V.sum(),
               maxC=C.max(),minC=C.min(),minT=T.min(),maxT=T.max(),
               max_index=int(np.argmax(C)),js_min=js.min(),js_max=js.max(),drive_min=drive.min(),drive_max=drive.max(),
               condensation_area_fraction=float(self.area[ib][js<0].sum()/self.area.sum()),
               pressure_law_sign_ok=bool(np.all(js*drive>=-1e-18)) if not self.cfg.baseline else True,
               rates=np.array(rates))
        return out,m
    def rhs(self,t,y):return self.evaluate(t,y)
    def summary(self,t,y):return self.evaluate(t,y,True)[1]
