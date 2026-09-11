"""Numerical and independent OOXML acceptance checks; exits nonzero on failure."""
from __future__ import annotations
import argparse,csv,hashlib,json,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.integrate import solve_ivp,quad
from scipy.optimize import brentq
from scipy.special import j0,j1,jn_zeros
from scipy.sparse import coo_matrix
from scipy.interpolate import PchipInterpolator
from q3_solver import Operator,Config,props,Fdiff,F,load_input,read_xlsx,NS
from q3_reference import Reference

def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def col(i):
 s=''
 while i:i,j=divmod(i-1,26);s=chr(65+j)+s
 return s

def operator_checks(out):
 rng=np.random.default_rng(20260911);records=[]
 for n,nz,flux in [(12,0,'integral'),(8,7,'integral'),(12,0,'harmonic')]:
  op=Operator(Config(n=n,nz=nz,flux=flux));env=lambda t:(48.,.05)
  u=np.column_stack([42+4*rng.random(op.size),.06+2*rng.random(op.size)]).ravel()
  J=op.rhs(1,u,env,True);v=rng.normal(size=u.size);eps=1e-6
  fd=(op.rhs(1,u+eps*v,env)-op.rhs(1,u-eps*v,env))/(2*eps);jv=J@v
  err=float(np.linalg.norm(fd-jv)/np.linalg.norm(jv))
  du=op.rhs(1,u,env).reshape(-1,2);q=u.reshape(-1,2);S=props(q[:,0],q[:,1])[0]
  water=float(op.w@du[:,1]+np.sum(op.bound*op.cfg.hm*(q[:,1]-.05)))
  heat=float(op.w@(S*du[:,0])+np.sum(op.bound*op.cfg.hT*(q[:,0]-48)))
  const=np.tile([48.,.05],op.size);zero=float(np.max(abs(op.rhs(1,const,env))))
  assert err<2e-7 and abs(water)<1e-18 and abs(heat)<1e-9 and zero==0
  records.append({'n':n,'nz':nz,'flux':flux,'directional_jacobian_relative_error':err,'water_operator_residual':water,'heat_operator_residual':heat,'constant_equilibrium_rhs_max':zero})
 ref=Reference(12);env=lambda t:(48.,.05)
 x=ref.x[:-1];y=np.column_stack([48-2*(1-x),.2+.12*(1-x)]).ravel();v=rng.normal(size=len(y));eps=1e-7
 fd=(ref.evaluate(1,y+eps*v,env)-ref.evaluate(1,y-eps*v,env))/(2*eps);jv=ref.evaluate(1,y,env,True)@v
 err=float(np.linalg.norm(fd-jv)/np.linalg.norm(jv));assert err<3e-7
 cases=[]
 for a,b in [(.05265,.05),(.15,.05),(2.55,.05),(.150000000001,.15),(.052,.052000000001)]:
  direct=float(Fdiff(np.array([a]),np.array([b]))[0]);q=quad(lambda c:np.exp(-.45/c),b,a,epsabs=1e-27,epsrel=5e-13)[0]
  rel=abs(direct-q)/max(1e-100,abs(q));assert rel<1e-10
  cases.append({'a':a,'b':b,'primitive_difference':direct,'independent_quad':q,'relative_error':rel})
 result={'finite_volume':records,'reference_jacobian_relative_error':err,'primitive_quad_checks':cases}
 dump(out/'operator_checks.json',result);return result

def cylinder_analytic(out):
 R=.02;D=1e-9;hm=8e-7;Bi=hm*R/D;tend=20000.
 zeros=np.r_[0,jn_zeros(0,90)]
 lam=np.array([brentq(lambda x:x*j1(x)-Bi*j0(x),a+1e-12,b-1e-12,xtol=1e-13) for a,b in zip(zeros[:-1],zeros[1:])])
 A=2*j1(lam)/(lam*(j0(lam)**2+j1(lam)**2));res=[]
 for n in (32,64,128):
  op=Operator(Config(n=n));l=op.left;r=op.right;v=op.geo*D
  rows=np.r_[l,l,r,r,np.arange(op.size)];cols=np.r_[l,r,l,r,np.arange(op.size)];vv=np.r_[-v,v,v,-v,-op.bound*hm]/op.w[rows]
  J=coo_matrix((vv,(rows,cols)),shape=(op.size,op.size)).tocsc()
  sol=solve_ivp(lambda t,y:J@y,(0,tend),np.ones(op.size),jac=J,method='BDF',rtol=1e-11,atol=1e-13)
  assert sol.success
  exact=j0(np.outer(op.r/R,lam))@(A*np.exp(-D*tend*lam**2/R**2));err=float(np.max(abs(sol.y[:,-1]-exact)))
  res.append({'n':n,'max_error':err,'center_numeric':float(sol.y[0,-1]),'center_exact':float(exact[0])})
 for i in (1,2):res[i]['observed_order']=float(np.log2(res[i-1]['max_error']/res[i]['max_error']))
 assert min(x['observed_order'] for x in res[1:])>1.8
 dump(out/'constant_cylinder_analytic.json',{'R_m':R,'D_m2_s':D,'hm_m_s':hm,'t_s':tend,'Bi':Bi,'root_count':len(lam),'results':res})
 return res

def reference_endpoint_checks(root):
 # Continue the independently saved complete state to the official endpoint.
 # This is a short actual integration, not interpolation from rounded output.
 a=np.load(root/'output/main.npz');target=float(a['time_s'][-1]);primary=a['sample_TC'][-1]
 raw=load_input(root/'inputs/attachment1.xlsx');envvals=raw[(raw[:,0]>=10800)&(raw[:,0]<=14400),1:3].mean(axis=0)
 env=lambda t:envvals;records=[]
 for name in ('reference80','reference160'):
  data=np.load(root/'validation'/(name+'.npz'));info=json.loads((root/'validation'/(name+'.json')).read_text());n=info['n'];op=Reference(n)
  start=float(data['snapshot_time_s'][-1]);full=data['snapshots'][-1];y=full[:-1].ravel()
  assert 0<target-start<1
  sol=solve_ivp(lambda t,v:op.evaluate(t,v,env),(start,target),y,method='Radau',jac=lambda t,v:op.evaluate(t,v,env,True),rtol=2e-12,atol=np.tile([2e-12,2e-14],n),max_step=.05)
  if not sol.success:raise RuntimeError(sol.message)
  final=op.surface(target,sol.y[:,-1].reshape(n,2),env);profile=op.profiles(final);extrema=op.extrema(final)
  diff=profile-primary
  assert extrema['max_C']<.15 and np.max(abs(diff[:,1]))<1e-7
  np.savez_compressed(root/'validation'/(name+'_official_endpoint.npz'),time_s=target,full_TC=final,radius_cm=np.linspace(0,2,21),profile_TC=profile,main_difference_TC=diff)
  records.append({'reference':name,'start_from_saved_time_s':start,'target_time_s':target,'method':'Radau','max_step_s':.05,'success':True,'nfev':int(sol.nfev),'polynomial_extrema':extrema,'max_T_difference_K':float(abs(diff[:,0]).max()),'max_C_difference_kgkg':float(abs(diff[:,1]).max()),'all_21_C_four_decimal_match':bool(np.array_equal(np.round(profile[:,1],4),np.round(primary[:,1],4)))})
 dump(root/'validation/independent_endpoint_comparison.json',records)
 return records

def analyze(root):
 reference_endpoint_checks(root)
 out=root/'validation';a=np.load(root/'output/main.npz');stats=json.loads((root/'output/main.json').read_text());C=a['sample_TC'][:,:,1];T=a['sample_TC'][:,:,0];ts=a['time_s'];evt=stats['event']
 q2=np.load(root/'inputs/q2_unrounded.npz');mask=ts<=10800;idx=ts[mask].astype(int)
 dT=T[mask]-q2['temperature_degC'][idx];dC=C[mask]-q2['moisture_dry_basis'][idx]
 reg={'times_count':int(mask.sum()),'radii_count':21,'max_temperature_error_K':float(abs(dT).max()),'max_moisture_error_kgkg':float(abs(dC).max()),'four_decimal_temperature_differences':int(np.sum(np.round(T[mask],4)!=np.round(q2['temperature_degC'][idx],4))),'four_decimal_moisture_differences':int(np.sum(np.round(C[mask],4)!=np.round(q2['moisture_dry_basis'][idx],4)))}
 sel=np.isin(ts,np.arange(1800,10801,1800));ri=np.array([0,5,10,15,20]);ti=ts[sel].astype(int)
 reg['q2_paper_60_values_four_decimal_match']=bool(np.array_equal(np.round(T[sel][:,ri],4),np.round(q2['temperature_degC'][ti][:,ri],4)) and np.array_equal(np.round(C[sel][:,ri],4),np.round(q2['moisture_dry_basis'][ti][:,ri],4)))
 assert reg['max_temperature_error_K']<2e-5 and reg['max_moisture_error_kgkg']<2e-6
 dump(out/'q2_regression.json',reg)
 ind=[]
 for name in ('reference80','reference160'):
  rr=json.loads((out/(name+'.json')).read_text());b=np.load(out/(name+'.npz'));count=min(len(ts),len(b['time_s']))-1
  assert np.array_equal(ts[:count],b['time_s'][:count])
  dif=a['sample_TC'][:count]-b['sample_TC'][:count]
  ix=np.flatnonzero(np.isin(ts[:count],np.arange(21600,194401,21600)))
  rec={'name':name,'critical_time_difference_s':evt['critical_s']-rr['event']['critical_s'],'maximum_T_difference_K':float(abs(dif[:,:,0]).max()),'maximum_C_difference_kgkg':float(abs(dif[:,:,1]).max()),'table5_regular_rows_C_max_error':float(abs(dif[ix][:,ri,1]).max()),'table5_regular_rows_four_decimal_match':bool(np.array_equal(np.round(a['sample_TC'][ix][:,ri,1],4),np.round(b['sample_TC'][ix][:,ri,1],4)))}
  ind.append(rec)
  assert abs(rec['critical_time_difference_s'])<.03 and rec['table5_regular_rows_C_max_error']<2e-6
 dump(out/'independent_comparison.json',ind)
 events=[]
 for name in ('integral256','integral512','integral1024','integral2048','integral1024_tight'):
  d=json.loads((out/(name+'.json')).read_text());events.append({'case':name,'n':d['config']['n'],'rtol':d['config']['rtol'],'critical_s':d['event']['critical_s'],'critical_h':d['event']['critical_h']})
 events.append({'case':'main2048_tight','n':2048,'rtol':2e-12,'critical_s':evt['critical_s'],'critical_h':evt['critical_h']})
 v=[e['critical_s'] for e in events[:4]];orders=[float(np.log2((v[i]-v[i+1])/(v[i+1]-v[i+2]))) for i in (0,1)]
 space=(events[-2]['critical_s']-events[-1]['critical_s'])/3
 time_err=max(abs(events[2]['critical_s']-events[-2]['critical_s']),abs(events[3]['critical_s']-events[-1]['critical_s']))
 cert={'events':events,'observed_orders':orders,'estimated_fine_spatial_error_s':space,'measured_time_setting_change_s':time_err,'richardson_diagnostic_s':evt['critical_s']-space,'engineering_numerical_error_budget_s':.03,'budget_is_interval_arithmetic_proof':False,'hours_four_decimal_rounding_stable_in_budget':round((evt['critical_s']-.03)/3600,4)==round((evt['critical_s']+.03)/3600,4),'execution_rule':'ceil((critical_s + 0.03)/0.36)*0.36','expected_execution_s':float(np.ceil((evt['critical_s']+.03)/.36)*.36)}
 assert cert['hours_four_decimal_rounding_stable_in_budget'] and abs(cert['expected_execution_s']-evt['execution_s'])<1e-8
 dump(out/'convergence.json',cert)
 harmonic=[]
 for n in (512,1024):
  h=json.loads((out/f'harmonic{n}.json').read_text());ii=json.loads((out/f'integral{n}.json').read_text())
  harmonic.append({'n':n,'harmonic_critical_s':h['event']['critical_s'],'integral_critical_s':ii['event']['critical_s'],'same_mesh_flux_event_difference_s':h['event']['critical_s']-ii['event']['critical_s']})
 dump(out/'harmonic_comparison.json',{'rows':harmonic,'difference_reduction_factor':harmonic[0]['same_mesh_flux_event_difference_s']/harmonic[1]['same_mesh_flux_event_difference_s'],'interpretation':'Both methods converge here; integral flux has smaller observed event bias. No observed temporal oscillations are claimed.'})
 # Endpoint evidence is independently recomputed from saved complete internal states.
 E=a['event_fields_TC'];emax=E[:,:,:,1].max(axis=(1,2));etime=a['event_time_s']
 assert np.isclose(etime[1],evt['critical_s']) and emax[0]>.15 and emax[2]<.15 and emax[3]<.15
 eventdoc={**evt,'global_max_from_saved_fields':emax.tolist(),'saved_event_times_s':etime.tolist(),'max_positions_r_m':[float(a['r_m'][np.unravel_index(np.argmax(e[:,:,1]),e[:,:,1].shape)[0]]) for e in E],'reconstruction':'PCHIP in r^2, bounded on every interval; formal axial-uniform domain. Thus reconstructed max equals max over all 2049 nodes.','threshold_kgkg':.15,'numerical_error_budget_s':.03,'strict_PDE_interval_error_certificate':False,'excel_final_row_definition':'strict execution time, not equality root and not first qualified minute','last_full_minute_s':float(ts[-2]),'first_qualified_full_minute_s':float(60*np.ceil(evt['critical_s']/60))}
 dump(root/'output/end_event.json',eventdoc)
 # Standard table/CSV exports, unrounded values are retained in this CSV.
 table_ix=np.flatnonzero((ts>0)&((np.mod(ts,21600)==0)|(np.arange(len(ts))==len(ts)-1)))
 table=np.column_stack([ts[table_ix]/3600,C[table_ix][:,ri]])
 with (root/'output/table5.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(['time_h','r0cm','r0.5cm','r1cm','r1.5cm','r2cm']);w.writerows(table)
 with (root/'output/result3_unrounded.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(['time_s']+[f'r{x:g}cm' for x in np.linspace(0,2,21)]);w.writerows(np.column_stack([ts[1:],C[1:]]))
 scenarios=[];base=json.loads((out/'integral512.json').read_text())['event']['critical_s']
 for name in ('integral512','scenario_last','scenario_nominal','hT_minus20','hT_plus20','hm_minus20','hm_plus20'):
  d=json.loads((out/(name+'.json')).read_text());scenarios.append({'case':name,'future':d['future'],'hT':d['config']['hT'],'hm':d['config']['hm'],'critical_s':d['event']['critical_s'],'critical_h':d['event']['critical_h'],'change_from_same_grid_baseline_s':d['event']['critical_s']-base})
 dump(out/'scenario_comparison.json',scenarios)
 geom=[]
 for name,radial in [('cylinder40x64','radial40'),('cylinder40x64_iso','radial40'),('cylinder80x64_iso','radial80'),('cylinder40x128_iso','radial40')]:
  if not (out/(name+'.json')).exists():continue
  d=json.loads((out/(name+'.json')).read_text());r=json.loads((out/(radial+'.json')).read_text());aa=np.load(out/(name+'.npz'));bb=np.load(out/(radial+'.npz'));count=min(len(aa['time_s']),len(bb['time_s']))-1
  dd=aa['sample_TC'][:count]-bb['sample_TC'][:count]
  geom.append({'case':name,'n_r':d['config']['n'],'n_z':d['config']['nz'],'critical_s':d['event']['critical_s'],'critical_h':d['event']['critical_h'],'end_effect_vs_matching_radial_s':d['event']['critical_s']-r['event']['critical_s'],'max_midplane_T_difference_K':float(abs(dd[:,:,0]).max()),'max_midplane_C_difference_kgkg':float(abs(dd[:,:,1]).max()),'event_max_index':d['event']['argmax_flat_index'],'projections':d['projections']})
 dump(out/'geometry_comparison.json',geom)
 # Measured constitutive/flux history and dry-tail duration.
 st=a['snapshots'];sT=a['snapshot_time_s'];w=a['weights'].ravel();avg=np.array([w@q[:,:,1].ravel()/w.sum() for q in st]);sc=[]
 for i,t in enumerate(sT):
  q=st[i,:,0,:];Dc=props(q[:,0],q[:,1])[2]
  sc.append({'time_s':float(t),'center_C':float(q[0,1]),'surface_C':float(q[-1,1]),'volume_mean_C':float(avg[i]),'center_T':float(q[0,0]),'surface_T':float(q[-1,0]),'center_D':float(Dc[0]),'surface_D':float(Dc[-1]),'D_ratio':float(Dc.max()/Dc.min()),'outward_surface_water_flux_kgkg_m_s':float(8e-7*(q[-1,1]-(load_input(root/'inputs/attachment1.xlsx')[-1,2] if t==14400 else (.04998754098360656 if t>14400 else np.interp(t,load_input(root/'inputs/attachment1.xlsx')[:,0],load_input(root/'inputs/attachment1.xlsx')[:,2])))))})
 diag=a['diagnostics'];ut,uidx=np.unique(diag[:,0],return_index=True);interp=PchipInterpolator(ut,diag[uidx,1]);milestones={str(v):float(brentq(lambda t:interp(t)-v,ut[0],ut[-1])) for v in (1.,.5,.3,.2)}
 mech={'snapshots':sc,'center_milestone_times_s':milestones,'surface_015_time_s':stats['surface_crossing_s'],'mean_015_time_s':stats['mean_crossing_s'],'center_015_time_s':evt['critical_s'],'fraction_of_total_time_after_18h':(evt['critical_s']-64800)/evt['critical_s']}
 dump(out/'mechanism.json',mech)
 # Package readable summary for report generation.
 summary={'event':evt,'table5':table.tolist(),'regression':reg,'independent':ind,'convergence':cert,'scenarios':scenarios,'geometry':geom,'balance':{k:stats[k] for k in ('max_water_balance_kgkg','max_effective_heat_balance_J_m3','effective_heat_relative')},'mechanism':mech,'excel_data_rows':len(ts)-1,'excel_rows_including_header':len(ts),'excel_water_cells':(len(ts)-1)*21}
 dump(out/'summary.json',summary);return summary

def xlsx_check(root,path=None):
 path=path or root/'result3.xlsx';a=np.load(root/'output/main.npz');ts=a['time_s'][1:];C=a['sample_TC'][1:,:,1]
 sheets=read_xlsx(path);assert list(sheets)==['Sheet1'];cells=sheets['Sheet1'];n=len(ts)+1
 header=[cells[f'{col(j)}1']['value'] for j in range(2,23)];assert np.allclose(header,np.linspace(0,2,21),rtol=0,atol=1e-15)
 rtimes=np.array([cells[f'A{i}']['value'] for i in range(2,n+1)]);rc=np.array([[cells[f'{col(j)}{i}']['value'] for j in range(2,23)] for i in range(2,n+1)])
 assert np.array_equal(ts,rtimes) and np.max(abs(C-rc))<5e-15
 assert all(cells[f'{col(j)}{i}']['type']=='n' for i in range(2,n+1) for j in range(1,23))
 assert not any(isinstance(v['value'],str) and ('...' in v['value'] or '…' in v['value']) for v in cells.values())
 assert all(int(''.join(filter(str.isdigit,k)))<=n for k in cells)
 with zipfile.ZipFile(path) as z:
  st=ET.fromstring(z.read('xl/styles.xml'));fmts={int(x.attrib['numFmtId']):x.attrib['formatCode'] for x in st.findall('s:numFmts/s:numFmt',NS)};xfs=st.findall('s:cellXfs/s:xf',NS)
  used={cells[f'{col(j)}{i}']['style'] for i in range(2,n+1) for j in range(2,23)}
  codes={fmts.get(int(xfs[ix].attrib['numFmtId']),str(xfs[ix].attrib['numFmtId'])) for ix in used};assert codes=={'0.0000'}
 report={'file':str(path.name),'sha256':sha(path),'zip_crc_pass':True,'sheet_names':list(sheets),'rows_including_header':n,'data_rows':len(ts),'water_cells_checked':int(C.size),'numeric_data_cells_checked':int(rc.size+len(ts)),'max_value_readback_error':float(np.max(abs(C-rc))),'all_display_4dp_match_npz':bool(np.array_equal(np.round(rc,4),np.round(C,4))),'all_water_number_formats':sorted(codes),'all_time_values_match':True,'last_regular_s':float(rtimes[-2]),'last_s':float(rtimes[-1]),'last_center_raw':float(rc[-1,0]),'last_center_display':f'{rc[-1,0]:.4f}','last_surface_raw':float(rc[-1,-1]),'end_row':n,'ellipsis_removed':True,'saved_event_and_final_row_agree':True}
 evt=json.loads((root/'output/end_event.json').read_text());assert rtimes[-1]==evt['execution_s'] and rc[-1,0]==evt['execution_max']
 dump(root/'validation/xlsx_readback.json',report);return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--xlsx-only',action='store_true');p.add_argument('--analyze-only',action='store_true');args=p.parse_args()
 if args.xlsx_only:print(json.dumps(xlsx_check(args.root),indent=2))
 else:
  if not args.analyze_only:operator_checks(args.root/'validation');cylinder_analytic(args.root/'validation')
  print(json.dumps(analyze(args.root),ensure_ascii=False,indent=2))
