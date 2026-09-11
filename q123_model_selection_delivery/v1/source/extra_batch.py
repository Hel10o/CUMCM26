from pathlib import Path
import subprocess,os,time,json,sys
p=Path(__file__).resolve().parents[1]
names=json.loads((p/'validation/extra_config_names.json').read_text())
for n in names:
 cmd=[sys.executable,str(p/'source/run_case.py'),str(p/'configs'/f'{n}.json'),str(p/'output'/n)]
 t=time.time()
 with (p/'validation'/f'{n}.log').open('w') as log:
  r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1'))
 d=dict(case=n,command=cmd,exit_code=r.returncode,elapsed_s=time.time()-t)
 (p/'validation'/f'{n}_execution.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
