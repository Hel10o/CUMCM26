#!/usr/bin/env python3
"""Q2 complete reproducible entry. Defaults to a new output directory.
Run: python run_all.py --out reproduced --excel-engine artifact
Or on a local machine without artifact_tool: --excel-engine portable.
--stage permits the identical stages to run under a hard execution time limit.
--resume reuses complete managed stages only: source/config/input/output signatures are verified.
Legacy caches are not adopted. Numerical kernels are unchanged.
"""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
os.environ['CUA_DD_PYTHON_TOOL_WARM_SPREADSHEET_RUNTIME']='0'
import argparse,json,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source'))
import numpy as np
from q2_core import Environment,load_environment,file_hashes,solve_fv,save_solution
from q2_spectral import solve_spectral
from q2_tests import run_unit_tests,run_sensitivity
from q2_axisymmetric import solve_axisymmetric
from q2_geometry_tests import geometry_tests
from q2_finalize import finalize,comparison
from q2_run_guard import RunGuard, stage_outputs

STAGES=['mesh','reference','tests','time','sensitivity','geometry','assemble','excel','report','audit']

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'inputs/附件1.xlsx')
    p.add_argument('--template',type=Path,default=ROOT/'inputs/result2_template.xlsx')
    p.add_argument('--out',type=Path,default=ROOT/'reproduced')
    p.add_argument('--stage',choices=['all']+STAGES,default='all')
    p.add_argument('--resume',action='store_true')
    p.add_argument('--excel-engine',choices=['artifact','portable'],default='artifact')
    a=p.parse_args();out=a.out.resolve()
    guard=RunGuard(ROOT,out,a.input,a.template,resume=a.resume,excel_engine=a.excel_engine)
    inputs={str(q.name):file_hashes(q) for q in (a.input,a.template)}
    v=out/'validation';v.mkdir(exist_ok=True);log=out/'run_state.json'
    state={'input_hashes':inputs,'stages':{},'complete':False,
           'model_version':'q2-effective-local-v1','cache_schema':2,'excel_engine':a.excel_engine}
    for s in STAGES:
        if guard.valid(s):state['stages'][s]={'passed':True,'reused_verified':True}
    data,contract=load_environment(a.input);env=Environment(data)
    (out/'input_audit.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf-8')
    def done_npz(name):return False  # Only entire completed, signed stages can be reused.
    selected=STAGES if a.stage=='all' else [a.stage]
    for stage in selected:
        if guard.valid(stage):
            print('REUSE VERIFIED',stage,flush=True);continue
        guard.begin(stage)
        tic=time.perf_counter();print('START',stage,flush=True)
        try:
            if stage=='mesh':
                for n in (20,40,80,160,320,640,1280,2560):
                    name=f'fv_n{n}'
                    if not done_npz(name):save_solution(v/(name+'.npz'),solve_fv(env,n=n,rtol=2e-12,atol_T=2e-13,atol_C=2e-14,max_step=10.,quadrature=n==1280))
                    print('GRID COMPLETE',n,flush=True)
            elif stage=='reference':
                for n in (128,192):
                    name=f'cheb_n{n}'
                    if not done_npz(name):save_solution(v/(name+'.npz'),solve_spectral(env,n=n,rtol=3e-13,atol_T=2e-14,atol_C=2e-15,max_step=10.))
                    print('REFERENCE COMPLETE',n,flush=True)
            elif stage=='tests':run_unit_tests(env,v);geometry_tests(env,v)
            elif stage=='time':save_solution(v/'fv_n1280_time_tight.npz',solve_fv(env,n=1280,rtol=1e-12,atol_T=1e-13,atol_C=1e-14,max_step=5.))
            elif stage=='sensitivity':run_sensitivity(env,v)
            elif stage=='geometry':
                for nr,nz in ((20,40),(20,80),(40,80)):
                    name=f'axisymmetric_{nr}_{nz}'
                    if not done_npz(name):save_solution(v/(name+'.npz'),solve_axisymmetric(env,nr,nz,verbose=True,resume_path=None))
                    paired=f'axisymmetric_paired1d_{nr}'
                    if not done_npz(paired):save_solution(v/(paired+'.npz'),solve_fv(env,n=nr,rtol=1e-9,atol_T=1e-11,atol_C=1e-11,max_step=30.))
            elif stage=='assemble':finalize(a.input,out)
            elif stage=='excel':
                if a.excel_engine=='artifact':
                    from q2_excel import export_artifact
                    export_artifact(a.template,out/'q2_unrounded.npz',out/'result2.xlsx')
                else:
                    from q2_xlsx_portable import export_portable
                    export_portable(out/'q2_unrounded.npz',out/'result2.xlsx')
            elif stage=='report':
                from q2_report import paper,figures
                figures(out);paper(out)
            elif stage=='audit':
                from q2_audit import audit
                audit(out)
            guard.finish(stage,stage_outputs(stage,out))
            state['stages'][stage]={'passed':True,'elapsed_s':time.perf_counter()-tic}
        except Exception as e:
            guard.fail(stage,repr(e))
            state['stages'][stage]={'passed':False,'elapsed_s':time.perf_counter()-tic,'error':repr(e)}
            log.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');raise
        log.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');print('DONE',stage,state['stages'][stage],flush=True)
    assert inputs=={str(q.name):file_hashes(q) for q in (a.input,a.template)},'Original input modified'
    state['original_inputs_unchanged']=True
    state['complete']=all(guard.valid(s) for s in STAGES)
    if state['complete']:
        delivered=ROOT/'output/q2_unrounded.npz'
        if delivered.exists() and delivered.parent.resolve()!=out:
            aa=np.load(delivered);bb=np.load(out/'q2_unrounded.npz')
            state['compared_with_delivered']={k:comparison(aa[k][1:],bb[k][1:],aa['time_s'][1:],aa['radius_cm']) for k in ('temperature_degC','moisture_dry_basis')}
            assert all(t['four_decimal_mismatches']==0 for t in state['compared_with_delivered'].values())
    log.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    print('COMPLETE:',state['complete'],flush=True)

if __name__=='__main__':main()
