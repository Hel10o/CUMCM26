"""Freeze actual input/config/source/result bindings and demonstrate read-only validation."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,time
P=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def canonical(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
versions={}
for base in [P/'source',P/'validation/source_versions']:
 for f in base.rglob('*.py'):
  versions.setdefault(sha(f),[]).append(f.relative_to(P).as_posix())
rows=[]
for out in sorted((P/'output').iterdir()):
 if not (out/'result.json').exists():continue
 res=json.loads((out/'result.json').read_text());pf=out/'provenance.json'
 row={'case':out.name,'result_sha256':sha(out/'result.json'),'solution_sha256':sha(out/'solution.npz'),'evidence':'new PDE run; see case-specific scope'}
 if pf.exists():
  pr=json.loads(pf.read_text());cfg=pr['config'];cf=P/'configs'/f'{out.name}.json'
  row.update(config_canonical_sha256=canonical(cfg),recorded_input_sha256=pr.get('input_sha256'),recorded_command=pr.get('command'),config_file=cf.relative_to(P).as_posix() if cf.exists() else None,config_file_sha256=sha(cf) if cf.exists() else None,config_matches_recorded=json.loads(cf.read_text())==cfg if cf.exists() else None)
  recorded=pr.get('source_sha256',{});entry=Path(pr.get('command',[''])[0]).name
  core={k:{'recorded_sha256':v,'preserved_paths':versions.get(v,[])} for k,v in recorded.items() if k in ['model.py',entry]}
  row['executed_core_source_bindings']=core
  row['other_source_snapshot_hashes']= {k:v for k,v in recorded.items() if k not in core}
  if not all(v['preserved_paths'] for v in core.values()):raise RuntimeError(('Missing core source version',out.name,core))
  if cf.exists() and not row['config_matches_recorded']:raise RuntimeError(('Config changed',out.name))
 else:
  row.update(config_canonical_sha256=canonical({'n':res.get('n'),'ceq':res.get('ceq'),'method':res.get('method')}),recorded_input_sha256=res.get('input_sha256'),executed_script_sha256=res.get('source_sha256'),preserved_script_paths=versions.get(res.get('source_sha256'),[]),note='Independent solver records its script and input hash in result.json; imported constitutive helper is included in source/ but was not separately hashed in that solver result.')
  if not row['preserved_script_paths']:raise RuntimeError(('Missing independent script',out.name))
 if row['recorded_input_sha256']!=sha(P/'inputs/environment_extracted.csv'):raise RuntimeError(('Input mismatch',out.name))
 rows.append(row)
(P/'validation/run_bindings.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
# Input/config/output files only: validation writes its stdout log outside this set.
protected=sorted(p for d in ['inputs','configs','output'] for p in (P/d).rglob('*') if p.is_file())
before={p.relative_to(P).as_posix():sha(p) for p in protected}
cmd=[sys.executable,str(P/'source/validate.py')];start=time.time()
with (P/'validation/read_only_validation.log').open('w') as log:
 r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
after={p.relative_to(P).as_posix():sha(p) for p in protected}
record={'command':cmd,'exit_code':r.returncode,'elapsed_s':time.time()-start,'protected_file_count':len(before),'all_unchanged':before==after,'before_sha256':before,'changed_files':[k for k,v in before.items() if after.get(k)!=v],'scope':'Actual validator rerun without report-root. Protected inputs/configs/results were independently hashed before and after.'}
(P/'validation/read_only_validation_integrity.json').write_text(json.dumps(record,indent=2,ensure_ascii=False))
if r.returncode or before!=after:raise RuntimeError(record)
print(json.dumps({'bound_runs':len(rows),'protected_files':len(before),'read_only_exit_code':r.returncode,'all_unchanged':before==after,'elapsed_s':record['elapsed_s']},indent=2))
