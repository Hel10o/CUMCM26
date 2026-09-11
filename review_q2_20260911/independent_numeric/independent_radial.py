"""Independent Q2 reference: direct-r collocation, expanded PDE, Radau.

No q2_final_delivery or Q2-preflight numerical module is imported. Both boundary
values are eliminated: r=0 by a Neumann row; r=R by the coupled Robin equations.
The PDE is evaluated in expanded local derivatives, not the Pro FV flux RHS or
its x=(r/R)^2 spectral product derivative. A complex-step Jacobian is generated
from this implementation. Input values are independently decoded from OOXML.
"""
from pathlib import Path
import argparse, hashlib, json, platform, sys, time, warnings, zipfile
import xml.etree.ElementTree as ET
import numpy as np
import scipy
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'A题'/'附件'/'附件1.xlsx'
DELIVERY=ROOT/'q2_final_delivery'/'output'
R=.02; HT=25.; HM=8e-7
TABLE_T=np.arange(1800,10801,1800)


def read_input():
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(SOURCE) as z:
        assert z.testzip() is None
        book=ET.fromstring(z.read('xl/workbook.xml'))
        rel=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        sid=book.find('s:sheets',ns)[0].attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        target=next(item.attrib['Target'] for item in rel if item.attrib['Id']==sid)
        target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        values={}
        for cell in ET.fromstring(z.read(target)).findall('.//s:sheetData/s:row/s:c',ns):
            value=cell.find('s:v',ns)
            if value is not None and cell.attrib.get('t','n')=='n':values[cell.attrib['r']]=float(value.text)
    data=np.array([[values[f'{c}{i}'] for c in 'ABC'] for i in range(2,243)])
    assert np.array_equal(data[:,0],np.arange(0,14401,60)) and np.isfinite(data).all()
    return data


def coefficients(T,C):
    if np.any(np.real(C)<=0) or np.any(np.real(T)+273.15<=0):
        raise FloatingPointError('Invalid independent collocation trial state')
    rho=650+128*C
    cp=1450+2736*C/(1+C)
    k=.21+.38*C/(1+C)
    kc=.38/(1+C)**2
    diffusion=.0024*np.exp(-.45/C-3850/(T+273.15))
    dc=.45*diffusion/C**2
    dt=3850*diffusion/(T+273.15)**2
    return rho*cp,k,kc,diffusion,dc,dt


class DirectRadial:
    def __init__(self,n,data):
        self.n=n; self.m=n-1; self.data=data
        self.x=(1-np.cos(np.pi*np.arange(n+1)/n))/2
        bary=(-1.)**np.arange(n+1); bary[[0,-1]]*=.5
        delta=self.x[:,None]-self.x[None,:]
        g=np.zeros_like(delta)
        np.divide(bary[None,:]/bary[:,None],delta,out=g,where=delta!=0)
        np.fill_diagonal(g,-g.sum(axis=1))
        self.g=g; self.gg=g@g
        self.center_interior=-g[0,1:-1]/g[0,0]
        self.center_surface=-g[0,-1]/g[0,0]
        self.edge_interior=g[-1,1:-1]+g[-1,0]*self.center_interior
        self.edge_diagonal=g[-1,-1]+g[-1,0]*self.center_surface
        self.interp=np.empty((21,n+1))
        for i,xx in enumerate(np.arange(21)/20):
            dist=xx-self.x; nearest=np.argmin(abs(dist))
            if abs(dist[nearest])<1e-14:
                self.interp[i]=0; self.interp[i,nearest]=1
            else:
                terms=bary/dist; self.interp[i]=terms/terms.sum()
        self.jac_calls=0

    def ambient(self,t):
        return np.interp(t,self.data[:,0],self.data[:,1]),np.interp(t,self.data[:,0],self.data[:,2])

    def reconstruct(self,t,y):
        # Last dimension is a batch, also used by the complex-step Jacobian.
        yy=np.asarray(y)
        vector=yy.ndim==1
        if vector:yy=yy[:,None]
        interior=yy.reshape(self.m,2,-1)
        ti,ci=interior[:,0],interior[:,1]
        et,ec=self.ambient(t)
        anchor_t=ti[-1]; anchor_c=ci[-1]
        # Shift-invariant forms remove large constant cancellation in derivatives.
        gt=self.edge_interior@(ti-anchor_t)
        gc=self.edge_interior@(ci-anchor_c)
        diagonal=self.edge_diagonal
        cs=anchor_c-gc/diagonal
        for _ in range(8):
            k=.21+.38*cs/(1+cs); kc=.38/(1+cs)**2
            # g*Ti+d*Ts = g*(Ti-anchor)+d*(Ts-anchor); sum(g)=-d.
            b=gt+diagonal*(et-anchor_t)
            denominator=k*diagonal/R+HT
            ts=et-(k/R)*b/denominator
            ts_c=-(kc/R)*b*HT/denominator**2
            _,_,_,diff,dc,dt=coefficients(ts,cs)
            derivative_c=gc+diagonal*(cs-anchor_c)
            f=(diff/R)*derivative_c+HM*(cs-ec)
            fp=((dc+dt*ts_c)*derivative_c+diff*diagonal)/R+HM
            cs=cs-f/fp
        k=.21+.38*cs/(1+cs)
        ts=et-(k/R)*b/(k*diagonal/R+HT)
        full=np.empty((self.n+1,2,yy.shape[1]),dtype=yy.dtype)
        full[1:-1]=interior; full[-1,0]=ts; full[-1,1]=cs
        full[0,0]=anchor_t+self.center_interior@(ti-anchor_t)+self.center_surface*(ts-anchor_t)
        full[0,1]=anchor_c+self.center_interior@(ci-anchor_c)+self.center_surface*(cs-anchor_c)
        return full[:,:,0] if vector else full

    def rhs(self,t,y):
        full=self.reconstruct(t,y)
        vector=full.ndim==2
        if vector:full=full[:,:,None]
        temp,c=full[:,0],full[:,1]
        tx=self.g@(temp-temp[-1]); cx=self.g@(c-c[-1])
        txx=self.gg@(temp-temp[-1]); cxx=self.gg@(c-c[-1])
        s,k,kc,d,dc,dt=coefficients(temp[1:-1],c[1:-1])
        x=self.x[1:-1,None]
        tx,cx,txx,cxx=tx[1:-1],cx[1:-1],txx[1:-1],cxx[1:-1]
        ft=(k*(txx+tx/x)+kc*cx*tx)/(R**2*s)
        fc=(d*(cxx+cx/x)+dc*cx**2+dt*tx*cx)/R**2
        out=np.empty((2*self.m,full.shape[2]),dtype=full.dtype)
        out[0::2]=ft; out[1::2]=fc
        return out[:,0] if vector else out

    def jacobian(self,t,y):
        self.jac_calls+=1
        h=1e-25
        batch=y[:,None].astype(complex)+1j*h*np.eye(len(y))
        return self.rhs(t,batch).imag/h


def comparison(given,reference,times,radii):
    diff=np.abs(given-reference)
    at=np.unravel_index(diff.argmax(),diff.shape)
    rounded_given=np.array([format(float(v),'.4f') for v in given.flat]).reshape(given.shape)
    rounded_reference=np.array([format(float(v),'.4f') for v in reference.flat]).reshape(reference.shape)
    changes=np.argwhere(rounded_given!=rounded_reference)
    return {'max_abs_difference':float(diff[at]),'rms_difference':float(np.sqrt(np.mean(diff**2))),
            'max_at_time_s_radius_cm':[int(times[at[0]]),float(radii[at[1]])],
            'four_decimal_mismatches':len(changes),
            'first_mismatches':[{'time_s':int(times[i]),'radius_cm':float(radii[j]),
              'delivery':float(given[i,j]),'reference':float(reference[i,j])} for i,j in changes[:20]]}


def solve(n,end,rtol,maxstep):
    data=read_input(); operator=DirectRadial(n,data)
    # Basic independent polynomial derivative anchors.
    assert np.max(abs(operator.g@operator.x-1))<1e-9
    assert np.max(abs(operator.gg@(operator.x**2)-2))<1e-6
    y=np.tile([28.,2.55],n-1)
    times=np.arange(end+1)
    output=np.empty((end+1,21,2));output[0]=[28.,2.55]
    stats={'n':n,'end_s':end,'rtol':rtol,'atol_T':rtol*.05,'atol_C':rtol*.005,
           'max_step_s':maxstep,'method':'Direct-r Chebyshev, expanded nonlinear PDE, algebraic center and surface, Radau, independent complex-step Jacobian',
           'nfev':0,'njev':0,'nlu':0,'accepted_steps':0,'warnings':[]}
    started=time.perf_counter()
    for start in range(0,end,60):
        stop=min(start+60,end)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            sol=solve_ivp(operator.rhs,(start,stop),y,method='Radau',jac=operator.jacobian,
              rtol=rtol,atol=np.tile([rtol*.05,rtol*.005],n-1),max_step=maxstep,
              first_step=min(1e-5,stop-start),dense_output=True)
        if not sol.success:raise RuntimeError(sol.message)
        stats['warnings'].extend(str(w.message) for w in caught)
        query=np.arange(start+1,stop+1)
        state=sol.sol(query)
        # Boundary input varies with query time, so independently reconstruct each.
        for t,ys in zip(query,state.T):output[t]=operator.interp@operator.reconstruct(t,ys)
        y=sol.y[:,-1]
        for name in ('nfev','njev','nlu'):stats[name]+=int(getattr(sol,name))
        stats['accepted_steps']+=len(sol.t)-1
        if stop%1800==0:print(f'Radial independent n={n}: t={stop}, elapsed={time.perf_counter()-started:.2f}s',flush=True)
    stats['elapsed_s']=time.perf_counter()-started
    stats['warnings']=sorted(set(stats['warnings']))
    stats['jacobian_calls']=operator.jac_calls
    assert np.isfinite(output).all() and output[:,:,1].min()>0
    return output,stats


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--n',type=int,default=80)
    parser.add_argument('--end',type=int,default=10800);parser.add_argument('--rtol',type=float,default=2e-11)
    parser.add_argument('--max-step',type=float,default=15)
    args=parser.parse_args()
    output,stats=solve(args.n,args.end,args.rtol,args.max_step)
    name=f'direct_r_n{args.n}_t{args.end}'
    path=HERE/(name+'.npz')
    np.savez_compressed(path,time_s=np.arange(args.end+1),radius_cm=np.arange(21)/10,
                        temperature_degC=output[:,:,0],moisture_dry_basis=output[:,:,1])
    z=np.load(DELIVERY/'q2_unrounded.npz');tables=TABLE_T[TABLE_T<=args.end]
    report={'method':__doc__,'runtime':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform()},
            'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'stats':stats,
            'first_second_center_surface':output[1,[0,20]].tolist(),'comparisons':{}}
    for j,key in enumerate(('temperature_degC','moisture_dry_basis')):
        report['comparisons'][key]=comparison(z[key][1:args.end+1],output[1:,:,j],np.arange(1,args.end+1),np.arange(21)/10)
        if len(tables):report['comparisons'][key]['paper_table']=comparison(z[key][tables][:,::5],output[tables][:,::5,j],tables,np.arange(5)/2)
    (HERE/(name+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
