"""Actual 72h evolution with zero exchange along a uniform shrinking state."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.integrate import solve_ivp
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'source'))
from q4_common import Radius,read_numeric
from q4_spectral import Reference
r=Radius(read_numeric(B/'inputs/attachment2.xlsx',2)[1]);n=12;op=Reference(n,r)
env=lambda t:np.array([28.,2.55]);y0=np.tile([28.,2.55],n);times=np.linspace(0,259200,433)
sol=solve_ivp(lambda t,y:op.evaluate(t,y,env),(0.,259200.),y0,method='Radau',jac=lambda t,y:op.evaluate(t,y,env,True),t_eval=times,rtol=1e-10,atol=1e-12,max_step=600.)
assert sol.success
full=np.array([op.surface(t,y.reshape(n,2),env) for t,y in zip(sol.t,sol.y.T)])
R=np.array([r(t) for t in sol.t]);V=np.pi*R**2*.25;rho_d0=1.;rho_d=rho_d0*(.02/R)**2;J=(R/.02)**2
md=rho_d*V;mw=md*full[:,0,1];loss=2/R*8e-7*(full[:,-1,1]-2.55)
result={'case':'Uniform state, shrinking measured radius, equal boundary environment; true relative exchange is zero throughout actual ODE evolution.','duration_s':259200.,'n':n,'method':'Radau','outputs':len(sol.t),'nfev':sol.nfev,'nlu':sol.nlu,'radius_initial_final_m':[float(R[0]),float(R[-1])],'rho_d0_arbitrary_normalization_kg_dry_m3':1.,'max_C_departure':float(abs(full[:,:,1]-2.55).max()),'max_T_departure_C':float(abs(full[:,:,0]-28.).max()),'max_relative_dry_mass_change':float(abs(md/md[0]-1).max()),'max_relative_water_mass_change':float(abs(mw/mw[0]-1).max()),'max_rho_d_J_minus_rho_d0':float(abs(rho_d*J-rho_d0).max()),'max_mean_C_boundary_rate_abs_s1':float(abs(loss).max()),'final_current_volume_water_concentration_kg_m3':float(rho_d[-1]*full[-1,0,1]),'initial_current_volume_water_concentration_kg_m3':2.55,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [B/'source/q4_spectral.py',B/'source/q4_common.py']}}
result['pass']=result['max_C_departure']<1e-10 and result['max_T_departure_C']<1e-10 and result['max_relative_dry_mass_change']<1e-12 and result['max_relative_water_mass_change']<1e-12
np.savez_compressed(B/'validation/pure_shrinkage_evolution.npz',time_s=sol.t,radius_m=R,full_TC=full,rho_d=rho_d,jacobian=J,dry_mass=md,water_mass=mw,relative_boundary_rate=loss)
(B/'validation/pure_shrinkage_evolution.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
