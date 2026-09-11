"""Bounded, isolated runtime review. No PDE solves here: cold-start is a separate logged command."""
from __future__ import annotations
import copy, hashlib, json, os, platform, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import numpy as np

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
SOURCE=REPO/'q3_refinement_delivery'
PYTHON=sys.executable
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(root): return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
def save(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def command(args,name):
    p=subprocess.run([PYTHON,'-B','-X','utf8',*map(str,args)],env=ENV,capture_output=True,text=True,encoding='utf-8')
    (HERE/f'{name}.log').write_text(p.stdout+p.stderr,encoding='utf-8')
    return {'exit_code':p.returncode,'command':[PYTHON,'-B','-X','utf8',*map(str,args)],'log':f'{name}.log'}
def manifest(root):
    paths=[p for p in sorted(root.rglob('*')) if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts]
    (root/'MANIFEST.sha256').write_text(''.join(f'{sha(p)}  {p.relative_to(root).as_posix()}\n' for p in paths),encoding='utf-8')

before=json.loads((HERE/'original_snapshot.json').read_text(encoding='utf-8-sig'))
report={'runtime':{'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform(),'blas_threads':1},'original_file_count':len(before),
 'frozen_verify':{'exit_code':int((HERE/'frozen_verify_exit_code.txt').read_text().strip()),'log':'frozen_verify.log','failure':'Windows snapshot paths use backslashes while manifest uses forward slashes'}}
cold=HERE/'cold'
new=np.load(cold/'output/solution.npz'); formal=np.load(SOURCE/'output/solution.npz')
stats=json.loads((cold/'output/solution.json').read_text(encoding='utf-8'))
ev=json.loads((SOURCE/'output/end_event.json').read_text(encoding='utf-8'))
assert np.array_equal(new['time_s'],formal['time_s'])
diff=new['profile_TC']-formal['profile_TC']
def four_mismatches(a,b): return int(sum(f'{x:.4f}'!=f'{y:.4f}' for x,y in zip(a.flat,b.flat)))
table=np.genfromtxt(SOURCE/'output/table5.csv',delimiter=',',skip_header=1)
indices=[int(np.argmin(abs(new['time_s']-h*3600))) for h in table[:,0]]
table_new=new['profile_TC'][indices][:,[0,5,10,15,20],1]
comparison={
 'cold_algorithm':'N80 Chebyshev collocation, primitive-gradient moisture flux, BDF from uniform initial state t=0',
 'formal_source':json.loads((SOURCE/'validation/numeric/rounding_stability.json').read_text())['official_source'],
 'elapsed_s':stats['elapsed_s'],'critical_s':stats['event']['critical_s'],'critical_difference_s':stats['event']['critical_s']-ev['critical_s'],
 'execution_s':stats['event']['execution_s'],'execution_max':stats['event']['execution_max'],
 'execution_max_difference':stats['event']['execution_max']-ev['execution_max'],
 'times_exactly_equal':True,'moisture_workbook_cells':int(diff[1:,:,1].size),
 'max_abs_moisture_difference':float(abs(diff[1:,:,1]).max()),'max_abs_temperature_difference':float(abs(diff[1:,:,0]).max()),
 'workbook_four_decimal_mismatches':four_mismatches(new['profile_TC'][1:,:,1],formal['profile_TC'][1:,:,1]),
 'table5_values':int(table_new.size),'table5_max_abs_difference':float(abs(table_new-table[:,1:]).max()),'table5_four_decimal_mismatches':four_mismatches(table_new,table[:,1:]),
 'last_snapshot_polynomial_extrema':stats['extrema'][-1],
 'input_sha256':stats['input_sha256'],'solver_driver_sha256':stats['source_sha256'],
 'complete_source_hashes':{p.name:sha(p) for p in (SOURCE/'source').glob('*.py')},
 'cold_output_hashes':{p.name:sha(p) for p in (cold/'output').iterdir() if p.is_file()},
}
save(HERE/'cold_comparison.json',comparison);report['cold_comparison']=comparison
report['cold_export']=command([SOURCE/'source/export_workbook.py','--root',cold,'--out',cold/'output/result3.xlsx','--engine','portable'],'cold_export') if not (cold/'output/result3.xlsx').exists() else {'exit_code':0,'reused_completed_export':True,'log':'cold_export.log'}
report['cold_xlsx_readback']=command([SOURCE/'source/validate_xlsx.py','--xlsx',cold/'output/result3.xlsx','--solution',cold/'output/solution.npz','--json-out',HERE/'cold_xlsx_readback.json'],'cold_xlsx_readback')
assert report['cold_export']['exit_code']==0 and report['cold_xlsx_readback']['exit_code']==0

with tempfile.TemporaryDirectory(prefix='candidate_',dir=HERE) as tmp:
    candidate=Path(tmp)/'q3_refinement_delivery';shutil.copytree(SOURCE,candidate)
    report['original_selftests']=command([candidate/'source/runtime_selftests.py'],'original_selftests')
    report['selftests_result']=json.loads((candidate/'validation/runtime/selftests.json').read_text(encoding='utf-8'))
    verify=candidate/'source/verify_frozen.py'
    text=verify.read_text(encoding='utf-8');text=text.replace('str(p.relative_to(root))','p.relative_to(root).as_posix()')
    verify.write_text(text,encoding='utf-8');manifest(candidate)
    (HERE/'verify_frozen_as_posix.py').write_text(text,encoding='utf-8')
    report['candidate_posix_verify']=command([verify,'--root',candidate,'--audit-out',Path(tmp)/'verify_out'],'candidate_posix_verify')
    assert report['candidate_posix_verify']['exit_code']==0
    shutil.copy2(Path(tmp)/'verify_out/verify.json',HERE/'candidate_verify_result.json')
    sys.path.insert(0,str(candidate/'source'))
    import validate_xlsx as vx
    import build_documents as docs
    import q3_refined_reference as refined
    import future_scenarios_from_checkpoint as scenarios
    probes=[]
    ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    for mode in ('nan_moisture','nan_radius','duplicate_cell'):
        target=Path(tmp)/f'{mode}.xlsx'
        with zipfile.ZipFile(candidate/'output/result3.xlsx') as zi,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as zo:
            for info in zi.infolist():
                data=zi.read(info.filename)
                if info.filename=='xl/worksheets/sheet1.xml':
                    tree=ET.fromstring(data)
                    ref='B1' if mode=='nan_radius' else 'B2'
                    cell=next(c for c in tree.findall(f'.//{{{ns}}}c') if c.attrib['r']==ref)
                    if mode=='duplicate_cell':
                        row=next(r for r in tree.findall(f'.//{{{ns}}}row') if r.attrib['r']=='2');row.append(copy.deepcopy(cell))
                    else:cell.find(f'{{{ns}}}v').text='NaN'
                    data=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
                zo.writestr(info,data)
        try:result=vx.validate(target,candidate/'output/solution.npz');accepted=True;reason=result
        except Exception as e:accepted=False;reason=f'{type(e).__name__}: {e}'
        probes.append({'name':mode,'accepted':accepted,'result':reason})
    # A new event fixture must not leave old timing literals elsewhere in the report.
    fixture=Path(tmp)/'docs_fixture'
    for rel in ['output/end_event.json','validation/scenarios/scenario_comparison_refined.json','validation/numeric/rounding_stability.json','validation/xlsx_readback.json','output/table5.md']:
        out=fixture/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(candidate/rel,out)
    e=json.loads((fixture/'output/end_event.json').read_text(encoding='utf-8'));e.update(critical_s=216000.,execution_s=216000.36,execution_max=.1499)
    save(fixture/'output/end_event.json',e)
    generated=docs.fmt(fixture)
    probes.append({'name':'dynamic_documents_60h_fixture','new_critical_present':'60.0000 h' in generated['README.md'],
       'stale_execution_57_4741h_present':'57.4741h' in generated['README.md'],
       'stale_last_complete_minute_206880s_present':'206880s' in generated['第三问论文正文.md']})
    (HERE/'dynamic_document_fixture_excerpt.txt').write_text('\n'.join(line for text in generated.values() for line in text.splitlines() if '57.4741h' in line or '206880s' in line or '60.0000 h' in line),encoding='utf-8')
    # Controlled solve_ivp fixture exercises execution past the resolved segment.
    original_solve=refined.solve_ivp
    def fake_near_segment_end(fun,span,y,**kwargs):
        return SimpleNamespace(success=True,t=np.array(span),t_events=[np.array([span[1]-.005])],nfev=0,nlu=0)
    refined.solve_ivp=fake_near_segment_end
    try:
        refined.run(n=4,out=Path(tmp)/'cross_segment',input_file=candidate/'inputs/attachment1.xlsx',method='BDF')
        result={'accepted':True}
    except Exception as e:result={'accepted':False,'exception':type(e).__name__,'reason':str(e),'root_s':59.995,'segment_end_s':60.,'execution_s':refined.derive_execution_time(59.995,.03,.36)}
    finally:refined.solve_ivp=original_solve
    probes.append({'name':'refined_cross_segment_fixture',**result})
    # This is a software fixture, NOT a physical scenario solve.
    cp=Path(tmp)/'untrusted_checkpoint.npz';node_count=scenarios.Operator(scenarios.Config(n=2048)).size
    np.savez(cp,time_s=14400.,state_TC=np.tile([50.,.2],(node_count,1)))
    queries=[];root=206939.995
    def fake_scenario_solve(fun,span,y,**kwargs):
        def dense(t):
            queries.append({'t_s':float(t),'outside_span':not(span[0]<=t<=span[1])})
            return np.tile([50.,.15-(t-root)*1e-6],len(y)//2)
        return SimpleNamespace(success=True,message='success',t_events=[np.array([root])],sol=dense,nfev=0,njev=0,nlu=0)
    scenarios.solve_ivp=fake_scenario_solve
    scenario_path=Path(tmp)/'cross_scenario.json'
    scenarios.run(cp,candidate/'inputs/attachment1.xlsx','mean',scenario_path)
    scenario_result=json.loads(scenario_path.read_text(encoding='utf-8'))
    probes.append({'name':'scenario_execution_outside_integrated_span_fixture','accepted':True,'queries':queries,'event':scenario_result,
       'scope':'fake solve_ivp only; no physical scenario assertion; real Operator grid and checkpoint size validation retained'})
    # Coverage hashes alone do not establish table/solution semantic agreement.
    table_path=candidate/'output/table5.csv';table_text=table_path.read_text(encoding='utf-8');table_path.write_text(table_text.replace('1.01696835544296','9.01696835544296',1),encoding='utf-8');manifest(candidate)
    report['candidate_stale_table_verify']=command([verify,'--root',candidate,'--audit-out',Path(tmp)/'stale_verify_out'],'candidate_stale_table_verify')
    if report['candidate_stale_table_verify']['exit_code']==0:shutil.copy2(Path(tmp)/'stale_verify_out/verify.json',HERE/'candidate_stale_table_verify_result.json')
    probes.append({'name':'manifest_valid_but_wrong_table5','accepted':report['candidate_stale_table_verify']['exit_code']==0,'scope':'changed isolated table and regenerated isolated manifest; demonstrates absent cross-artifact semantic check'})
    report['probes']=probes
after=snapshot(SOURCE);report['original_unchanged']=before==after
report['original_snapshot_difference']={'added':sorted(set(after)-set(before)),'removed':sorted(set(before)-set(after)),'changed':[p for p in before if p in after and before[p]!=after[p]]}
assert report['original_unchanged']
report['limitations']=['No new N2048 scenario integrations; scoped cold-start BDF run only','No claim of mathematical error bounds','No source package edits; only one-line verifier candidate retained','Original full-package verify fails on Windows; candidate verifies after path normalization and candidate manifest regeneration','Cold-start and formal trajectory share the same spatial Reference operator; BDF vs Radau is a time-method cross-check, not independent physics']
save(HERE/'runtime_review.json',report)
print(json.dumps({'cold_comparison':comparison,'probes':report['probes'],'original_unchanged':report['original_unchanged']},ensure_ascii=False,indent=2))
