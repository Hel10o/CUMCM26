"""Short real continuations from the saved t=206880 s whole-mesh main state.
Uses the accepted semidiscrete operator, never extrapolates a printed endpoint.
Only writes within this script's directory. No original files are changed.
"""
from pathlib import Path
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import hashlib,json,sys,time
import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'q3_final_delivery/source'
sys.path.insert(0,str(SOURCE))
from q3_solver import Operator,Config,load_input,Environment

mainfile=ROOT/'q3_final_delivery/output/main.npz'
info=json.loads((ROOT/'q3_final_delivery/output/main.json').read_text(encoding='utf-8'))
cfg=Config(**info['config']);op=Operator(cfg)
environment=Environment(load_input(ROOT/'q3_final_delivery/inputs/attachment1.xlsx'))
env=lambda t:environment.future
with np.load(mainfile,allow_pickle=False) as raw:
    start=float(raw['time_s'][-2]); target=float(raw['time_s'][-1])
    y0=raw['full_TC'][-2].ravel().copy()
    saved_final=raw['event_fields_TC'][-1].ravel().copy()
assert start==206880 and start<206901<target
times=np.array([start,206901.,info['event']['critical_s'],target])
records=[];fields=[]
for maxstep in (1.,.25):
    tic=time.perf_counter()
    def event(t,y):return np.max(y[1::2])-.15
    event.direction=-1;event.terminal=False
    sol=solve_ivp(lambda t,y:op.rhs(t,y,env),(start,target),y0,method='BDF',
                  jac=lambda t,y:op.rhs(t,y,env,True),rtol=2e-12,
                  atol=np.tile([2e-12,2e-14],op.size),max_step=maxstep,
                  dense_output=True,events=event)
    assert sol.success
    values=sol.sol(times).T.reshape(len(times),op.size,2)
    maximum=values[:,:,1].max(axis=1)
    assert maximum[1]>.15 and maximum[-1]<.15
    assert len(sol.t_events[0])==1
    fields.append(values)
    record={'max_step_s':maxstep,'method':'BDF with exact sparse coupled Jacobian',
            'rtol':2e-12,'atol_T':2e-12,'atol_C':2e-14,'success':sol.success,
            'start_s':start,'times_s':times.tolist(),'maximum_C':maximum.tolist(),
            'maximum_locations_r_m':op.r[values[:,:,1].argmax(axis=1)].tolist(),
            'critical_s':float(sol.t_events[0][0]),'critical_minus_original_s':float(sol.t_events[0][0]-info['event']['critical_s']),
            'max_endpoint_C_diff_vs_saved':float(np.max(abs(values[-1,:,1]-saved_final[1::2]))),
            'max_endpoint_T_diff_vs_saved':float(np.max(abs(values[-1,:,0]-saved_final[::2]))),
            'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'elapsed_s':time.perf_counter()-tic}
    records.append(record)
    print(json.dumps(record,ensure_ascii=False),flush=True)
diff=np.abs(fields[0]-fields[1])
report={'purpose':'Actual whole-state continuation to evaluate the proposed 206901 s time; not linear endpoint extrapolation.',
        'source_npz':'q3_final_delivery/output/main.npz','source_npz_sha256':hashlib.sha256(mainfile.read_bytes()).hexdigest(),
        'operator_sha256':hashlib.sha256((SOURCE/'q3_solver.py').read_bytes()).hexdigest(),
        'main_scenario':'future 61-sample last-hour arithmetic mean, fixed radial N2048 model',
        'runs':records,'step_refinement_max_C_difference':float(diff[:,:,1].max()),
        'step_refinement_max_T_difference':float(diff[:,:,0].max()),
        'C_206901':float(fields[1][1,:,1].max()),'excess_over_threshold_206901':float(fields[1][1,:,1].max()-.15),
        'main_critical_minus_206901_s':info['event']['critical_s']-206901,
        'scope':'This verifies the same discretized mean-boundary model; it does not identify assumptions used by another person.'}
(HERE/'comparison_206901.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
np.savez_compressed(HERE/'comparison_206901_states.npz',time_s=times,r_m=op.r,TC=np.array(fields),max_steps_s=np.array([1.,.25]))
