"""Reproducible multi-process batch; logs and true exit codes are retained."""
import subprocess,sys,json,time,os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[1]
def run(p):
    p=Path(p);out=ROOT/'output'/p.stem
    if out.exists():return {'case':p.stem,'status':'already_exists_not_overwritten'}
    cmd=[sys.executable,str(ROOT/'source/run_case.py'),str(p),str(out)]
    start=time.time()
    with open(ROOT/'validation'/f'{p.stem}.log','w') as f:
        proc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
    info=dict(case=p.stem,command=cmd,exit_code=proc.returncode,elapsed_s=time.time()-start)
    (ROOT/'validation'/f'{p.stem}.execution.json').write_text(json.dumps(info,indent=2));return info
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as ex:
        for f in as_completed([ex.submit(run,p) for p in sys.argv[1:]]):print(json.dumps(f.result()),flush=True)
