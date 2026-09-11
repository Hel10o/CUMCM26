"""Conservative, dependency-aware reuse and output protection for Q2.

This module contains no transport operator or numerical algorithm. A cache is
owned by one output directory. Failed/unsigned stages are rerun from their start.
Changing report code does not invalidate PDE stages. The full driver source is
included, so edits to hardcoded grids/tolerances/domain cannot reuse old solves.
"""
from __future__ import annotations
import hashlib,json,platform,uuid
from pathlib import Path
from importlib.metadata import version,PackageNotFoundError

STAGES=('mesh','reference','tests','time','sensitivity','geometry','assemble','excel','report','audit')
DEPS={s:() for s in STAGES}
DEPS.update(assemble=('mesh','reference','tests','time','sensitivity','geometry'),
            excel=('assemble',),report=('assemble',),audit=('assemble','excel','report'))
SOURCES={
 'mesh':('q2_core.py',),'reference':('q2_core.py','q2_spectral.py'),
 'tests':('q2_core.py','q2_spectral.py','q2_tests.py','q2_axisymmetric.py','q2_geometry_tests.py'),
 'time':('q2_core.py',),'sensitivity':('q2_core.py','q2_tests.py','q2_spectral.py'),
 'geometry':('q2_core.py','q2_axisymmetric.py'),
 'assemble':('q2_core.py','q2_finalize.py'),
 'excel':('q2_core.py','q2_excel.py','q2_xlsx_portable.py'),
 'report':('q2_report.py',),'audit':('q2_core.py','q2_audit.py')}
# These names identify preserved source/evidence trees, even outside runtime/.
PROTECTED_NAMES={'q1_delivery','q1_complete_delivery','q2_final_delivery',
                 'q2_refinement_readonly'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encode(obj):return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def atomic_json(path,obj):
 tmp=path.with_name(path.name+'.tmp');tmp.write_bytes(encode(obj));tmp.replace(path)
def package_versions(names):
 out={'python':platform.python_version()}
 for n in names:
  try:out[n]=version(n)
  except PackageNotFoundError:out[n]='not-installed'
 return out

def stage_outputs(stage,out):
 """The owner of mutable summaries is assemble/audit, not their producer tests."""
 patterns={
  'mesh':['validation/fv_n*.npz','validation/fv_n*.json'],
  'reference':['validation/cheb_n*.npz','validation/cheb_n*.json'],
  'tests':['validation/unit_tests.json','validation/geometry_unit_tests.json',
           'validation/constant_coefficient*','validation/kelvin_invariance*'],
  'time':['validation/fv_n1280_time_tight.npz','validation/fv_n1280_time_tight.json'],
  'sensitivity':['validation/sensitivity_*.npz','validation/sensitivity_*.json'],
  'geometry':['validation/axisymmetric_*.npz','validation/axisymmetric_*.json'],
  'assemble':['q2_unrounded.npz','*_unrounded.csv','table_*.csv','delivery_summary.json',
              'validation/validation.json','validation/sensitivity.json'],
  'excel':['result2.xlsx'],
  'report':['第二问论文正文.md','figures_manifest.json','figures/*.png','figures/*.svg'],
  'audit':['excel_audit.json']}
 files=sorted({p for pat in patterns[stage] for p in out.glob(pat) if p.is_file()})
 if stage=='mesh':files=[p for p in files if '_time_tight' not in p.name]
 if not files:raise RuntimeError(f'No output artifacts for {stage}')
 return files

class RunGuard:
 def __init__(self,root,out,input_path,template,*,resume=False,excel_engine='portable',
              config=None,versions=None):
  self.root=Path(root).resolve();self.out=Path(out).resolve()
  self.input=Path(input_path).resolve();self.template=Path(template).resolve()
  self.engine=excel_engine;self.config=config or {}
  self.versions=versions or package_versions(('numpy','scipy','matplotlib','artifact_tool'))
  self.marker=self.out/'.q2_run_guard.json';self._fingerprints={}
  protected=[self.root/'source',self.root/'inputs',self.root/'output',self.input,self.template]
  parts=self.out.parts
  if (any(x in PROTECTED_NAMES or x.startswith('review_q1_') or x.startswith('review_q2_') for x in parts)
      or any(self.out==x or self.out.is_relative_to(x) or x.is_relative_to(self.out) for x in protected)):
   raise ValueError('Protected original/source/input/evidence output location')
  if self.out.exists() and not self.out.is_dir():raise ValueError('Output is not a directory')
  nonempty=self.out.exists() and any(self.out.iterdir())
  if nonempty:
   if not resume:raise FileExistsError('Nonempty output: use a new directory, or explicit --resume for an owned run')
   if not self.marker.is_file():raise ValueError('Legacy/unowned nonempty output cannot be resumed')
   self.state=json.loads(self.marker.read_text(encoding='utf-8'))
   if self.state.get('schema')!=2 or self.state.get('owner_out')!=str(self.out) or not self.state.get('run_id'):
    raise ValueError('Cache ownership/schema mismatch; choose a new directory')
  else:
   if resume:raise ValueError('--resume requires an existing, managed nonempty directory')
   self.out.mkdir(parents=True,exist_ok=True)
   self.state={'schema':2,'owner_out':str(self.out),'run_id':str(uuid.uuid4()),'stages':{}}
  self.check_no_symlinks()
  atomic_json(self.marker,self.state)

 def check_no_symlinks(self):
  # Conservative: no symlink writes or external aliases inside a managed run.
  for x in self.out.rglob('*'):
   if x.is_symlink():raise ValueError(f'Symlink inside output refused: {x}')

 def fingerprint(self,stage):
  if stage in self._fingerprints:return self._fingerprints[stage]
  vkeys=['python','numpy','scipy']
  if stage=='report':vkeys+=['matplotlib']
  if stage=='excel' and self.engine=='artifact':vkeys+=['artifact_tool']
  src={n:sha(self.root/'source'/n) for n in SOURCES[stage]}
  payload={'schema':2,'driver_sha256':sha(self.root/'run_all.py'),
           'guard_sha256':sha(Path(__file__)), 'sources':src,
           'input':sha(self.input),'configuration':self.config,
           'runtime':{k:self.versions.get(k,'not-specified') for k in vkeys},
           'dependencies':{s:self.fingerprint(s) for s in DEPS[stage]}}
  if stage=='excel':payload.update(template_sha256=sha(self.template),excel_engine=self.engine)
  value=hashlib.sha256(encode(payload)).hexdigest();self._fingerprints[stage]=value
  return value

 def valid(self,stage):
  rec=self.state['stages'].get(stage,{})
  if not rec.get('passed') or rec.get('fingerprint')!=self.fingerprint(stage):return False
  if any(not self.valid(s) for s in DEPS[stage]):return False
  outputs=rec.get('outputs',{})
  if not outputs:return False
  for rel,h in outputs.items():
   p=self.out/rel
   if not p.resolve().is_relative_to(self.out) or p.is_symlink() or not p.is_file() or sha(p)!=h:return False
  return True

 def begin(self,stage):
  self.check_no_symlinks()
  missing=[s for s in DEPS[stage] if not self.valid(s)]
  if missing:raise RuntimeError(f'{stage} requires valid stages {missing}; run them or --stage all')
  # Do not trust or reuse individual outputs of interrupted or invalid stages.
  rec=self.state['stages'].get(stage,{})
  for rel in rec.get('outputs',{}):
   p=self.out/rel
   if p.resolve().is_relative_to(self.out) and p.is_file():p.unlink()
  self.state['stages'][stage]={'passed':False,'fingerprint':self.fingerprint(stage),'status':'running'}
  atomic_json(self.marker,self.state)

 def finish(self,stage,paths):
  self.check_no_symlinks();outputs={}
  for p in paths:
   p=Path(p).resolve()
   if not p.is_relative_to(self.out) or not p.is_file():raise ValueError('Stage output escapes owned directory or is missing')
   outputs[str(p.relative_to(self.out))]=sha(p)
  if not outputs:raise RuntimeError('A stage cannot pass without artifacts')
  self.state['stages'][stage]={'passed':True,'fingerprint':self.fingerprint(stage),'outputs':outputs}
  atomic_json(self.marker,self.state)

 def fail(self,stage,error):
  self.state['stages'][stage]={'passed':False,'fingerprint':self.fingerprint(stage),'error':error}
  atomic_json(self.marker,self.state)
