from pathlib import Path
import subprocess,sys,json,os,time
p=Path(__file__).resolve().parents[1]
for q in [1,23]:
 for latent in [0,1]:
  orig=f'q{q}_F1{latent}_r48_z64_v2';n=f'q{q}_F1{latent}_r48_z128_axis'
  c=json.loads((p/'configs'/f'{orig}.json').read_text());c['nz']=128
  cfg=p/'configs'/f'{n}.json';cfg.write_text(json.dumps(c,indent=2));cmd=[sys.executable,str(p/'source/run_case_memory_safe.py'),str(cfg),str(p/'output'/n)];t=time.time()
  with (p/'validation'/f'{n}.log').open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1'))
  d=dict(case=n,command=cmd,elapsed_s=time.time()-t,exit_code=r.returncode);(p/'validation'/f'{n}_execution.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
