"""Read-only numerical validation. Synthetic probes are never physical evidence."""
from pathlib import Path
import json,sys,hashlib,subprocess
sys.dont_write_bytecode=True
import numpy as np
from dataclasses import replace
from scipy.integrate import solve_ivp,simpson
from model import Config,Model,Environment,psat,R,H,T0,C0,CL,CD
ROOT=Path(__file__).resolve().parents[1]
VDEST=None
def dump(path,data):
 text=json.dumps(data,indent=2,ensure_ascii=False,default=lambda x: x.item() if isinstance(x,np.generic) else x.tolist())
 if VDEST is None:print(path.name,text)
 else:(VDEST/path.name).write_text(text)
def tests():
 env=Environment(np.loadtxt(ROOT/'inputs/environment_extracted.csv',delimiter=',',skiprows=1));m=Model(Config(nr=8,nz=12,question=1),env)
 out=[]
 def test(name,value,limit):
  out.append(dict(name=name,value=float(value),limit=limit,passed=bool(abs(value)<=limit),evidence='synthetic software or analytic limit, not original material prediction'))
 test('full-cylinder volume',m.V.sum()-np.pi*R**2*2*H,1e-16)
 test('side exchange area',m.side.sum()-2*np.pi*R*2*H,1e-15)
 test('two end faces area',m.end.sum()-2*np.pi*R**2,1e-15)
 Ta,W=env(0);pv=101325*W/(.621945+W);ce=m.K*pv/(psat(Ta)-pv)
 j,drive,*_=m.surface(0,np.array([Ta]),np.array([ce]));test('zero chemical driving',j[0],1e-15)
 for C,name,sgn in [(2.55,'evaporation',1),(.01,'condensation',-1)]:
  j,drv,*_=m.surface(0,np.array([Ta]),np.array([C]));out.append(dict(name=name,j_kgm2s=float(j[0]),driving_Pa=float(drv[0]),passed=bool(j[0]*sgn>0 and drv[0]*sgn>0),evidence='synthetic direction probe'))
 for label,cfg in [('adiabatic_no_flow',Config(question=1,nr=8,nz=12,hT=0)),('impermeable',Config(question=1,nr=8,nz=12,gas_multiplier=0))]:
  op=Model(cfg,env);y0=op.initial();s=solve_ivp(op.rhs,(0,600),y0,method='BDF',jac_sparsity=op.sparsity,rtol=1e-8,atol=1e-10)
  if not s.success:raise RuntimeError(s.message)
  test(label+'_water_invariance',np.max(abs(s.y[1::2,-1]-C0)),1e-10)
  if label.startswith('adiabatic'):test(label+'_temperature_invariance',np.max(abs(s.y[::2,-1]-T0)),1e-10)
 try:
  y=m.initial();y[1]=np.nan;m.rhs(0,y);raised=False
 except FloatingPointError:raised=True
 out.append(dict(name='NaN rejected',passed=raised,evidence='synthetic invalid-input probe'))
 dump(ROOT/'validation/synthetic_tests.json',out)
 # Actual paired PDE reduction from initial data, no end exchange.
 if not (ROOT/'output/q23_limit_closed_ends_2D/solution.npz').exists():
  dump(ROOT/'validation/closed_end_reduction.json',{'status':'not run in this root'})
  return out
 a=np.load(ROOT/'output/q23_limit_closed_ends_1D/solution.npz');b=np.load(ROOT/'output/q23_limit_closed_ends_2D/solution.npz')
 reduction=dict(evidence='new original-environment PDE runs, same nr24 and time tolerances; end exchange disabled',max_T_difference=float(np.max(abs(a['midplane_T']-b['midplane_T']))),max_C_difference=float(np.max(abs(a['midplane_C']-b['midplane_C']))))
 dump(ROOT/'validation/closed_end_reduction.json',reduction)
 return out

def physical(names):
 rows=[]
 for name in names:
  p=ROOT/'output'/name;d=np.load(p/'solution.npz');prov=json.loads((p/'provenance.json').read_text());cfg=Config(**prov['config']);meta=json.loads((p/'result.json').read_text());r=d['r'];z=d['z']
  rf=np.r_[0,(r[:-1]+r[1:])/2,R];wr=np.diff(rf**2)/2
  zf=np.r_[0,(z[:-1]+z[1:])/2,H] if len(z)>1 else np.array([0.,H]);wz=np.diff(zf)
  V=4*np.pi*wr[:,None]*wz[None,:];rho=(820 if cfg.question==1 else 976.4)/3.55
  fields=d['fields'];mw=np.einsum('ij,tij->t',V,rho*fields[:,:,:,1]);hh=np.einsum('ij,tij->t',V,rho*(CD+CL*fields[:,:,:,1])*(fields[:,:,:,0]-T0))
  times=d['field_time'];ix=np.searchsorted(d['time'],times);assert np.max(abs(d['time'][ix]-times))<1e-5
  cols={k:i for i,k in enumerate(d['metric_names'])};M=d['metrics'];rates=d['rates'];cumulative=np.array(meta['cumulative'])
  phase_from_components=(2.501e6-2361*T0)*(cumulative[0]+cumulative[4])-2361/CL*(cumulative[3]+cumulative[7])
  row=dict(case=name,fields_finite=bool(np.isfinite(fields).all()),C_positive=bool((fields[:,:,:,1]>0).all()),independent_volume_minus_saved=float(np.max(abs(V-d['volume']))),independent_Mw_vs_metrics_kg=float(np.max(abs(mw-M[ix,cols['Mwater']]))),independent_H_vs_metrics_J=float(np.max(abs(hh-M[ix,cols['enthalpy']]))),dry_mass_drift_kg=float(np.ptp(M[:,cols['Mdry']])),pressure_direction_all=bool((M[:,cols['pressure_law_sign_ok']]==1).all()),minimum_js_kgm2s=float(M[:,cols['js_min']].min()),maximum_condensing_area_fraction=float(M[:,cols['condensation_area_fraction']].max()),physical_latent_J=phase_from_components,latent_identity_residual_J=float(phase_from_components-cumulative[2]-cumulative[6]) if cfg.latent else None,omitted_energy_J=float(phase_from_components) if not cfg.latent else 0.)
  # Shift water reference enthalpy by 1 MJ/kg, shift carried enthalpy together.
  beta=1e6
  E0=meta['energy_residual_gauss5'];Rm=meta['mass_residual_gauss5']
  Eshift=E0+beta*((meta['final']['Mwater']-meta['initial']['Mwater'])+cumulative[0]+cumulative[4])
  row.update(reference_shift_Jkg=beta,energy_residual_original_J=E0,energy_residual_shifted_J=Eshift,gauge_identity_error_J=float(Eshift-E0-beta*Rm))
  if meta['event_equal_s'] is not None:
   row.update(event_equal_s=meta['event_equal_s'],execution_s=meta['execution_s'],genuinely_integrated_margin_s=meta['t_final']-meta['event_equal_s'],execution_in_raw_time_domain=bool(abs(d['time'][-1]-meta['execution_s'])<1e-7),strict_C_margin=.15-meta['final']['maxC'])
  rows.append(row)
 dump(ROOT/'validation/independent_budget_checks.json',rows)
 return rows
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--report-root');args=ap.parse_args()
 if args.report_root:
  VDEST=Path(args.report_root).resolve();VDEST.mkdir(parents=True,exist_ok=False)
 tests()
 names=['q1_F00_r96_z0_v2','q1_F01_r96_z0_v2','q1_F10_r96_z128_v2','q1_F11_r96_z128_v2','q23_F00_r96_z0_v2','q23_F01_r96_z0_v2','q23_F10_r96_z128_retry','q23_F11_r96_z128_v2']
 physical(names)
