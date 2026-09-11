from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PY=sys.executable

def run(cmd):
    env=os.environ.copy();env.setdefault('OPENBLAS_NUM_THREADS','1');env.setdefault('OMP_NUM_THREADS','1');env.setdefault('MKL_NUM_THREADS','1');env.setdefault('PYTHONDONTWRITEBYTECODE','1')
    subprocess.run(cmd,check=True,env=env)

def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest='scope',required=True)
    q=sp.add_parser('verify');q.add_argument('--audit-out',type=Path,required=True)
    q=sp.add_parser('scenario');q.add_argument('--name',choices=['mean','nominal','time_mean','last'],required=True);q.add_argument('--out',type=Path,required=True)
    q=sp.add_parser('cold-start');q.add_argument('--out',type=Path,required=True);q.add_argument('--method',choices=['BDF','Radau'],default='BDF');q.add_argument('--n',type=int,default=80)
    q=sp.add_parser('export');q.add_argument('--out',type=Path,required=True);q.add_argument('--engine',choices=['artifact','portable'],default='portable')
    sp.add_parser('docs')
    a=p.parse_args()
    if a.scope=='verify':
        run([PY,str(ROOT/'source/verify_frozen.py'),'--root',str(ROOT),'--audit-out',str(a.audit_out)])
    elif a.scope=='scenario':
        run([PY,str(ROOT/'source/future_scenarios_from_checkpoint.py'),'--checkpoint',str(ROOT/'validation/scenarios/checkpoint_4h_N2048.npz'),'--input',str(ROOT/'inputs/attachment1.xlsx'),'--scenario',a.name,'--out',str(a.out)])
    elif a.scope=='cold-start':
        run([PY,str(ROOT/'source/q3_refined_reference.py'),'--input',str(ROOT/'inputs/attachment1.xlsx'),'--out',str(a.out),'--n',str(a.n),'--scenario','mean','--method',a.method,'--rtol','2e-11','--atol-c','2e-13','--max-step','120','--budget-s','0.03','--quantum-s','0.36'])
    elif a.scope=='export':
        run([PY,str(ROOT/'source/export_workbook.py'),'--root',str(ROOT),'--out',str(a.out),'--engine',a.engine])
    elif a.scope=='docs':
        run([PY,str(ROOT/'source/build_documents.py'),'--root',str(ROOT)])

if __name__=='__main__':main()
