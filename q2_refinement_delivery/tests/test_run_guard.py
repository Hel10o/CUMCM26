"""Scoped management tests: toy files test reuse, not physical predictions.
One separate 60-s FV calculation checks that copied numerical kernels are unchanged.
"""
import importlib.util,json,os,shutil,sys,tempfile,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'runtime/source'))
from q2_run_guard import RunGuard,STAGES,SOURCES,DEPS

def load_module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fixture(root):
 (root/'source').mkdir(parents=True);(root/'inputs').mkdir()
 (root/'run_all.py').write_text('driver: end=10800, n=[1280,2560], rtol=2e-12')
 for name in sorted({n for v in SOURCES.values() for n in v}):(root/'source'/name).write_text(name+' original')
 (root/'inputs/env.xlsx').write_bytes(b'original environment')
 (root/'inputs/template.xlsx').write_bytes(b'original template')
 return root/'inputs/env.xlsx',root/'inputs/template.xlsx'

def main():
 records=[]
 def record(name,condition,details=None):
  assert condition,name
  records.append({'test':name,'passed':True,'details':details})
 def expect_error(name,f):
  try:f()
  except (ValueError,FileExistsError,RuntimeError) as e:record(name,True,str(e));return
  raise AssertionError(name+' unexpectedly accepted')
 with tempfile.TemporaryDirectory(prefix='q2_guard_') as td:
  tmp=Path(td);root=tmp/'runtime';inp,templ=fixture(root);out=tmp/'work'
  opts={'root':root,'out':out,'input_path':inp,'template':templ,'versions':{'python':'test','numpy':'test','scipy':'test','matplotlib':'test'}}
  g=RunGuard(**opts)
  for s in STAGES:
   g.begin(s);f=out/(s+'.fixture');f.write_text('software fixture '+s);g.finish(s,[f])
  record('new_owned_workspace_and_dependency_order',all(g.valid(s) for s in STAGES))
  g=RunGuard(**opts,resume=True)
  record('unchanged_resume_accepts_all_stages',all(g.valid(s) for s in STAGES))
  expect_error('nonempty_without_resume_rejected',lambda:RunGuard(**opts))
  # Changing one plotting module must not invalidate any PDE stage.
  p=root/'source/q2_report.py';p.write_text('modified plotting only')
  h=RunGuard(**opts,resume=True)
  bad=[s for s in STAGES if not h.valid(s)]
  record('plot_change_invalidates_report_audit_only',bad==['report','audit'],bad)
  p.write_text('q2_report.py original')
  # Template changes apply only to exporter and downstream audit.
  templ.write_bytes(b'new template')
  h=RunGuard(**opts,resume=True);bad=[s for s in STAGES if not h.valid(s)]
  record('template_change_invalidates_excel_audit_only',bad==['excel','audit'],bad)
  templ.write_bytes(b'original template')
  # Physical source and actual hardcoded solver/domain driver changes cannot pass.
  p=root/'source/q2_core.py';p.write_text('modified boundary or properties')
  h=RunGuard(**opts,resume=True)
  record('physics_source_change_invalidates_all',all(not h.valid(s) for s in STAGES))
  p.write_text('q2_core.py original')
  p=root/'run_all.py';orig=p.read_text();p.write_text(orig.replace('10800','14400'))
  h=RunGuard(**opts,resume=True)
  record('driver_time_grid_tolerance_change_invalidates_all',all(not h.valid(s) for s in STAGES))
  p.write_text(orig)
  h=RunGuard(**opts,resume=True,config={'end_s':14400,'rtol':1e-9})
  record('explicit_extra_configuration_changes_invalidate_all',all(not h.valid(s) for s in STAGES))
  inp.write_bytes(b'changed environment')
  h=RunGuard(**opts,resume=True)
  record('environment_bytes_change_invalidates_all',all(not h.valid(s) for s in STAGES))
  inp.write_bytes(b'original environment')
  # Tampered reference affects assembly/export/report/audit, not finite-volume solve.
  (out/'reference.fixture').write_text('corruption')
  h=RunGuard(**opts,resume=True);bad=[s for s in STAGES if not h.valid(s)]
  record('tampered_stage_file_invalidates_its_dependents',bad==['reference','assemble','excel','report','audit'],bad)
  expect_error('assemble_refuses_invalid_prerequisite',lambda:h.begin('assemble'))
  h.begin('reference');f=out/'reference.fixture';f.write_text('software fixture reference');h.finish('reference',[f])
  record('restored_stage_can_be_reused',h.valid('reference'))
  h.begin('time');h.fail('time','injected interruption')
  record('failed_stage_never_reused',not RunGuard(**opts,resume=True).valid('time'))
  dirty=tmp/'dirty';dirty.mkdir();(dirty/'anything.txt').write_text('must keep')
  dirtyopts={**opts,'out':dirty}
  expect_error('arbitrary_nonempty_output_rejected',lambda:RunGuard(**dirtyopts))
  expect_error('legacy_cache_not_adopted',lambda:RunGuard(**dirtyopts,resume=True))
  expect_error('resume_of_nonexistent_workspace_rejected',lambda:RunGuard(**{**opts,'out':tmp/'new'},resume=True))
  for p in [root/'source'/'out',root/'inputs'/'nested',tmp/'q1_complete_delivery'/'new',tmp/'q2_final_delivery'/'new',tmp/'review_q2_20260911'/'new']:
   expect_error('protected_path_'+str(p.relative_to(tmp)),lambda p=p:RunGuard(**{**opts,'out':p}))
  copy=tmp/'moved';shutil.copytree(out,copy)
  expect_error('copied_owner_marker_rejected',lambda:RunGuard(**{**opts,'out':copy},resume=True))
  (out/'link').symlink_to(inp)
  expect_error('internal_output_symlink_rejected',lambda:RunGuard(**opts,resume=True));(out/'link').unlink()
  protected=tmp/'q2_final_delivery';protected.mkdir(exist_ok=True);alias=tmp/'alias';alias.symlink_to(protected,target_is_directory=True)
  expect_error('symlink_resolving_into_accepted_output_rejected',lambda:RunGuard(**{**opts,'out':alias/'new'}))
 # Real numerical spot test: original and copied core, unchanged hash, short solve only.
 accepted=BASE/'reused/q2_final_delivery'
 orig_core=BASE/'reused/q2_core_original.py'
 a=load_module('q2_original_scoped',orig_core);b=load_module('q2_copied_scoped',BASE/'runtime/source/q2_core.py')
 record('scientific_core_sha256_unchanged',sha(orig_core)==sha(BASE/'runtime/source/q2_core.py'))
 import numpy as np
 data,_=a.load_environment(accepted/'inputs/附件1.xlsx')
 tic=time.perf_counter()
 s1=a.solve_fv(a.Environment(data),n=40,end=60.,rtol=1e-9,atol_T=1e-11,atol_C=1e-12,max_step=5.)
 s2=b.solve_fv(b.Environment(data),n=40,end=60.,rtol=1e-9,atol_T=1e-11,atol_C=1e-12,max_step=5.)
 diffs={k:float(np.max(abs(s1[k]-s2[k]))) for k in ('temperature_degC','moisture_dry_basis')}
 record('copied_numerics_60s_bitwise_match',all(v==0 for v in diffs.values()),diffs)
 for k in ('temperature_degC','moisture_dry_basis'):assert np.isfinite(s2[k]).all()
 out=BASE/'tests/results';out.mkdir(exist_ok=True)
 np.savez_compressed(out/'kernel_regression_60s.npz',time_s=s1['time_s'],radius_cm=s1['radius_cm'],**{k:s1[k] for k in ('temperature_degC','moisture_dry_basis')})
 payload={'scope':'Run-management regression and 60-s copied-kernel equality only; not a new 3-h validation or full ten-stage patched run.',
          'all_passed':True,'tests':records,'count':len(records),'kernel_elapsed_s':time.perf_counter()-tic,'runtime':{'python':sys.version,'numpy':np.__version__}}
 (out/'guard_tests.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
 print('PASSED',len(records),'management/kernel checks',diffs)
if __name__=='__main__':main()
