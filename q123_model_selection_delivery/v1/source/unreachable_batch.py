from pathlib import Path
import subprocess,os,sys,json,time
p=Path(__file__).resolve().parents[1]
for suffix in ['1D','paired1D','2D']:
 n='q23_sensitivity_eq0.200_'+suffix+'_eventchecked';t=time.time();cmd=[sys.executable,str(p/'source/run_case_memory_safe.py'),str(p/'configs'/f'{n}.json'),str(p/'output'/n)]
 with (p/'validation'/f'{n}.log').open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
 d=dict(case=n,command=cmd,exit_code=r.returncode,elapsed_s=time.time()-t);(p/'validation'/f'{n}_execution.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
