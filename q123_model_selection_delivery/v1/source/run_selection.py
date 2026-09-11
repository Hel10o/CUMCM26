"""Cold-start workflow into a NEW root. No writes to the frozen delivery root."""
from pathlib import Path
import argparse,shutil,subprocess,json,time,os,sys

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run-root',required=True);ap.add_argument('--scope',choices=['main','all','smoke'],default='main');a=ap.parse_args()
 src=Path(__file__).resolve().parents[1];dest=Path(a.run_root).resolve()
 dest.mkdir(parents=True,exist_ok=False)
 for d in ['source','inputs','configs']:shutil.copytree(src/d,dest/d,ignore=shutil.ignore_patterns('__pycache__'))
 (dest/'output').mkdir();(dest/'validation').mkdir();results=[]
 if a.scope=='smoke':
  c=json.loads((dest/'configs/q1_F01_r48_z0_v2.json').read_text());c.update(nr=8,nz=0,rtol=1e-7)
  (dest/'configs/smoke.json').write_text(json.dumps(c,indent=2));names=['smoke']
 else:
  names=['q1_B_r512_v2','q1_F00_r96_z0_v2','q1_F10_r96_z128_v2','q1_F01_r96_z0_v2','q1_F11_r96_z128_v2','q23_B_r512_v2','q23_F00_r96_z0_v2','q23_F10_r96_z128_retry','q23_F01_r96_z0_v2','q23_F11_r96_z128_v2']
  if a.scope=='all':
   extra=[]
   for c in (dest/'configs').glob('*.json'):
    n=c.stem
    if ('_v2' in n and ('r48_' in n)) or any(s in n for s in ['_axis','_r192','_Radau','_limit_','_gas']):extra.append(n)
    if 'sensitivity' in n and ('0.200' not in n or n.endswith('eventchecked')):extra.append(n)
   names+=sorted(set(extra)-set(names))
 for n in names:
  cfg=dest/'configs'/f'{n}.json';out=dest/'output'/n;cmd=[sys.executable,str(dest/'source/run_case_memory_safe.py'),str(cfg),str(out)];start=time.time()
  with (dest/'validation'/f'{n}.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1'))
  row=dict(case=n,command=cmd,exit_code=r.returncode,elapsed_s=time.time()-start);results.append(row);(dest/'validation/workflow_execution.json').write_text(json.dumps(results,indent=2));print(json.dumps(row),flush=True)
  if r.returncode:raise SystemExit(r.returncode)
 if a.scope!='smoke':
  subprocess.run([sys.executable,str(dest/'source/analyse.py')],check=True)
 print('Completed run root:',dest)
if __name__=='__main__':main()
