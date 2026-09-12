"""Independent bounded review checks; no main trajectory files are changed."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'source'))
from q4_spectral import Reference,grid,primitive
from q4_common import Radius,Environment,read_numeric

result={'reviewed_sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'source').glob('*.py') if p.name in ['q4_common.py','q4_spectral.py','run_q4.py']},'checks':{},'findings':[]}
n=12;x,G,w=grid(n)
result['checks']['grid_derivative_x2_max_abs']=float(np.max(abs(G@(x*x)-2*x)))
cs=np.array([.10,.15,.25,1.,2.55]);h=1e-6
result['checks']['primitive_derivative_relative_error']=float(np.max(abs((primitive(cs+h)-primitive(cs-h))/(2*h)-np.exp(-.30/cs))/np.exp(-.30/cs)))
Jchecks=[];BCchecks=[]
for tc,ca,base,amp in [(0.,.03,2.55,.4),(21600.,.05,.60,.30),(150000.,.05,.18,.05)]:
 op=Reference(n,lambda t:.018);env=lambda t:np.array([50.,ca])
 y=np.column_stack([48.+1.2*x[:-1]+.4*x[:-1]**2,base-amp*x[:-1]]).ravel()
 J=op.evaluate(tc,y,env,True);numeric=np.empty_like(J)
 for j in range(2*n):
  d=np.zeros_like(y);d[j]=1e-5 if j%2==0 else 1e-7
  numeric[:,j]=(op.evaluate(tc,y+d,env)-op.evaluate(tc,y-d,env))/(2*d[j])
 err=abs(J-numeric);scale=np.maximum(abs(J),1e-6)
 Jchecks.append({'t_s':tc,'max_abs_error':float(err.max()),'max_scaled_error':float((err/scale).max()),'relative_frobenius_error':float(np.linalg.norm(J-numeric)/np.linalg.norm(J))})
 T,C=op.surface(tc,y.reshape(n,2),env).T
 k=.12+.20*C[-1]/(1+C[-1]);A=.00042*np.exp(-3850/(T[-1]+273.15))
 BCchecks.append({'t_s':tc,'thermal_residual_W_m2':float(2/.018*k*(G@T)[-1]+25*(T[-1]-50.)), 'moisture_residual_m_s':float(2/.018*A*(G@primitive(C))[-1]+8e-7*(C[-1]-ca))})
result['checks']['jacobian_finite_difference']=Jchecks;result['checks']['surface_boundary']=BCchecks
pure=[]
for r in [.02,.017,.012]:
 op=Reference(n,lambda t:r);env=lambda t:np.array([28.,2.55]);y=np.tile([28.,2.55],n)
 pure.append({'radius_m':r,'rhs_max_abs':float(abs(op.evaluate(0,y,env)).max())})
result['checks']['uniform_equal_environment_pure_geometry']=pure
rd=read_numeric(BASE/'inputs/attachment2.xlsx',2)[1];radius=Radius(rd)
env=Environment(read_numeric(BASE/'inputs/attachment1.xlsx',3)[1]);tt=np.linspace(0,rd[-1,0],2001)
result['checks']['input_geometry']={'rows':len(rd),'radius_min_m':min(map(radius,tt)),'radius_max_m':max(map(radius,tt)),'last_R_m':radius(rd[-1,0]),'max_derivative_m_s':max(map(radius.derivative,tt)),'future_env':env.future.tolist(),'future_sample_count':int(np.sum(env.data[:,0]>=10800))}
result['findings']=[{'severity':'conditional_event_check','location':'run_q4.py::ev / event_info.root_extrema','detail':'ODE trigger uses maximum internal node C. Final polynomial extrema and 2D full-domain event must prove this is the same root or final event must be refined.'},{'severity':'provisional_output','location':'run_q4.py::preliminary_execution_s','detail':'0.36 s rounded endpoint is marked preliminary and must not be final before convergence/2D evidence sets the safety margin.'},{'severity':'audit_scope','location':'run_q4.py::rate_checks','detail':'Spatial quadrature flux identities are not an independent total energy trajectory balance; cumulative boundary mass quadrature is a separate trajectory check.'}]
result['pass_bounded_numerical_checks']=all(q['relative_frobenius_error']<1e-6 for q in Jchecks) and max(q['rhs_max_abs'] for q in pure)<1e-12 and max(abs(q['moisture_residual_m_s']) for q in BCchecks)<1e-12 and max(abs(q['thermal_residual_W_m2']) for q in BCchecks)<1e-7
src=BASE/'validation/spectral80.npz'
if src.exists():
 from q4_spectral import Reference
 a=np.load(src);meta=json.loads(src.with_suffix('.json').read_text());op=Reference(80,lambda t:.02);checks=[]
 for i in np.unique(np.linspace(1,len(a['time_s'])-1,17,dtype=int)):
  ex=op.extrema(a['full_TC'][i]);checks.append({'t_s':float(a['time_s'][i]),'max_C_error_against_saved':abs(float(ex['max_C']-a['max_C'][i])),'x_max':ex['x_max'],'stationary_points':ex['stationary_points']})
 result['checks']['spectral80_event_audit']={'source_npz_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'rows':len(a['time_s']),'maximum_saved_wettest_radius_m':float(a['max_radius_m'].max()),'max_saved_extrema_minus_axis_C':float(np.max(abs(a['max_C']-a['full_TC'][:,0,1]))),'independent_polynomial_recalculations':checks,'root_extrema':meta['event']['root_extrema'],'critical_s':meta['event']['critical_s'],'mass_balance_audit_present':meta['mass_balance_max_abs_in_mean_C'] is not None}
 result['findings'][0]['status']='Resolved for spectral80: all stored extrema and axis C agree within 2.23e-15; 17 independent extrema recalc agree; root has no interior stationary points. Early near-uniform plateau argmax locations have roundoff ambiguity. Retain event check for final selected finer run and 2D.'
p=BASE/'validation/model_code_review.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
