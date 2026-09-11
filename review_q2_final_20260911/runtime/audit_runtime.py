"""Independent scoped audit; original delivery is never executed in place.

Only a private tempfile tree is mutated. Durable evidence lives beside this script.
The bundled test entry runs its tests stage, not the ten-stage full pipeline.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
DELIVERY = PROJECT / 'q2_refinement_delivery'
ORIGINAL = PROJECT / 'q2_final_delivery'
sys.dont_write_bytecode = True

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write_json(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    started = time.perf_counter()
    use_overlay = '--overlay' in sys.argv
    results_dir = HERE/'fixed' if use_overlay else HERE
    results_dir.mkdir(exist_ok=True)
    evidence = {'scope':'Copied package tests and isolated management counterexamples; no full ten-stage solve and no modification of original deliveries.',
                'python':sys.version, 'original_sources':[], 'bundled_tests':[], 'probes':[]}
    for p in sorted((ORIGINAL/'source').glob('*.py')):
        q = DELIVERY/'runtime/source'/p.name
        evidence['original_sources'].append({'name':p.name,'original_sha256':sha(p),'runtime_sha256':sha(q),'byte_identical':p.read_bytes()==q.read_bytes()})
    before = {p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()}
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONUTF8':'1', 'PYTHONIOENCODING':'utf-8'}
    with tempfile.TemporaryDirectory(prefix='q2_final_runtime_audit_') as td:
        tmp = Path(td)
        candidate = tmp/'candidate'
        shutil.copytree(DELIVERY, candidate)
        if use_overlay:
            shutil.copy2(HERE/'overlay/source/q2_run_guard.py',candidate/'runtime/source/q2_run_guard.py')
            # Two original tests require OS symlink privilege. Preserve their
            # assertions when available; report explicit skips on WinError 1314.
            test = candidate/'tests/test_run_guard.py'
            content = test.read_text(encoding='utf-8')
            start = content.index("  (out/'link').symlink_to(inp)")
            end = content.index(' # Real numerical spot test:',start)
            old = content[start:end]
            replacement = "  try:\n" + ' ' + old.splitlines(True)[0]
            replacement += "  except OSError as exc:\n   if getattr(exc,'winerror',None)!=1314:raise\n   skipped=[{'test':'internal_output_symlink_rejected','reason':'Windows lacks symlink creation privilege (WinError 1314)'},{'test':'symlink_resolving_into_accepted_output_rejected','reason':'Windows lacks symlink creation privilege (WinError 1314)'}]\n  else:\n"
            replacement += ''.join(' '+line for line in old.splitlines(True)[1:])
            content=content[:start]+replacement+content[end:]
            content=content.replace(' records=[]',' records=[];skipped=[]')
            content=content.replace("'all_passed':True,'tests':records", "'all_executed_checks_passed':True,'skipped_tests':skipped,'tests':records")
            test.write_text(content,encoding='utf-8')
            shutil.copy2(test,HERE/'test_run_guard_windows.py')
        for name in ('test_run_guard.py','check_entry.py'):
            cmd = [sys.executable, '-X','utf8','-B', str(candidate/'tests'/name)]
            tic = time.perf_counter()
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
            (results_dir/(Path(name).stem+'.log')).write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr,encoding='utf-8')
            evidence['bundled_tests'].append({'name':name,'command':cmd,'exit_code':proc.returncode,'elapsed_s':time.perf_counter()-tic})
            print(name,proc.returncode,flush=True)
        # Do not relabel bundled historical evidence as fresh results when an
        # original test aborted before writing its report.
        fresh_files=[]
        for result in evidence['bundled_tests']:
            if result['exit_code']!=0:continue
            fresh_files += (['guard_tests.json','kernel_regression_60s.npz'] if result['name']=='test_run_guard.py' else
                ['entry_first.log','entry_resume.log','entry_refused.log','entry_integration.json','entry_unit_tests.json','entry_geometry_unit_tests.json'])
        dest=results_dir/'candidate_test_results';dest.mkdir(exist_ok=True)
        for name in fresh_files:shutil.copy2(candidate/'tests/results'/name,dest/name)
        write_json(dest/'FRESH_FILES.json',{'written_by_current_successful_tests':fresh_files})
        spec=importlib.util.spec_from_file_location('guard_under_audit',candidate/'runtime/source/q2_run_guard.py')
        guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)

        fixture_counter=0
        def fixture(label):
            nonlocal fixture_counter
            fixture_counter+=1
            base=tmp/(f'fixture_{fixture_counter}_'+label);root=base/'runtime'
            (root/'source').mkdir(parents=True);(root/'inputs').mkdir()
            (root/'run_all.py').write_text('fixed driver',encoding='utf-8')
            for name in {n for names in guard.SOURCES.values() for n in names}:
                (root/'source'/name).write_text(name,encoding='utf-8')
            inp=root/'inputs/environment.xlsx';inp.write_bytes(b'original environment')
            tpl=root/'inputs/template.xlsx';tpl.write_bytes(b'original template')
            opts=dict(root=root,out=base/'work',input_path=inp,template=tpl,versions={'python':'fixture','numpy':'fixture','scipy':'fixture','matplotlib':'fixture'})
            return base,root,opts
        def record(name,observed,expected,details=None):
            evidence['probes'].append({'name':name,'observed':observed,'expected':expected,'passed':observed==expected,'details':details})

        base,root,opts=fixture('dependency_outputs')
        g=guard.RunGuard(**opts)
        for stage in guard.STAGES:
            g.begin(stage);f=g.out/(stage+'.fixture');f.write_text('version one '+stage);g.finish(stage,[f])
        g.begin('mesh');f=g.out/'mesh.fixture';f.write_text('version two same solver/config');g.finish('mesh',[f])
        resumed=guard.RunGuard(**opts,resume=True)
        record('same_signature_upstream_recomputed_with_different_bytes_invalidates_downstream',
               resumed.valid('assemble'),False,{'old_assemble_text':(g.out/'assemble.fixture').read_text(),'new_mesh_text':f.read_text(),'valid_stages':{s:resumed.valid(s) for s in guard.STAGES}})

        base,root,opts=fixture('case_names')
        for name in ('q2_final_delivery','Q2_FINAL_DELIVERY','review_q2_20260911','REVIEW_Q2_20260911','q2_refinement_delivery'):
            target=base/name/'new_output'
            try:
                obj=guard.RunGuard(**{**opts,'out':target});accepted=True;reason=None
            except (ValueError,FileExistsError) as exc:accepted=False;reason=str(exc)
            record('protected_name_'+name,accepted,False,{'output':str(target),'reason':reason})

        base,root,opts=fixture('partial_output_contract')
        g=guard.RunGuard(**opts);g.begin('mesh')
        (g.out/'validation').mkdir();partial=g.out/'validation/fv_n20.json';partial.write_text('{}')
        try:
            recognized=guard.stage_outputs('mesh',g.out)
            g.finish('mesh',recognized);accepted=g.valid('mesh');details={'recognized_outputs':[str(p.relative_to(g.out)) for p in recognized]}
        except RuntimeError as exc:accepted=False;details={'reason':str(exc)}
        record('single_json_is_not_a_complete_mesh_stage',accepted,False,details)

        base,root,opts=fixture('junction')
        g=guard.RunGuard(**opts);outside=base/'external_evidence';outside.mkdir()
        victim=outside/'unit_tests.json';victim.write_text('must remain unchanged')
        junction=g.out/'validation'
        proc=subprocess.run(['cmd','/c','mklink','/J',str(junction),str(outside)],capture_output=True,text=True,encoding='utf-8',errors='replace')
        if proc.returncode==0:
            try:g.check_no_symlinks();accepted=True
            except ValueError:accepted=False
            details={'is_symlink':junction.is_symlink(),'is_junction':junction.is_junction(),'resolved_target':str(junction.resolve())}
            if accepted:
                (junction/'unit_tests.json').write_text('simulated stage overwrote external evidence')
                details['outside_changed']=victim.read_text()!='must remain unchanged'
                try:g.finish('tests',[junction/'unit_tests.json']);details['finish_rejected_after_write']=False
                except ValueError:details['finish_rejected_after_write']=True
            record('junction_inside_owned_output_refused_before_stage_writes',accepted,False,details)
        else:
            evidence['probes'].append({'name':'junction_inside_owned_output_refused_before_stage_writes','passed':None,'unavailable':proc.stdout+proc.stderr})

        base,root,opts=fixture('hardlink')
        g=guard.RunGuard(**opts);outside=base/'external.xlsx';outside.write_bytes(b'original accepted evidence')
        link=g.out/'result2.xlsx';os.link(outside,link)
        try:g.check_no_symlinks();accepted=True
        except ValueError:accepted=False
        details={'is_symlink':link.is_symlink(),'link_count':link.stat().st_nlink}
        if accepted:
            link.write_bytes(b'new exporter output');details['outside_changed']=outside.read_bytes()!=b'original accepted evidence'
            g.finish('excel',[link]);details['finish_accepts_link']=True
        record('hardlink_to_external_file_refused_before_write',accepted,False,details)

        base,root,opts=fixture('same_directory_case')
        g=guard.RunGuard(**opts)
        mixed=Path(str(g.out).upper())
        try:guard.RunGuard(**{**opts,'out':mixed},resume=True);accepted=True;reason=None
        except ValueError as exc:accepted=False;reason=str(exc)
        record('same_windows_output_directory_can_resume_with_case_variant',accepted,True,{'reason':reason})

        if use_overlay:
            completed=PROJECT/'review_q2_20260911/reproduced'
            evidence['required_outputs_vs_accepted_full_reproduction']={s:len(guard.stage_outputs(s,completed)) for s in guard.STAGES}

    after = {p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()}
    evidence['original_delivery_unchanged']=before==after
    evidence['original_delivery_files']=len(before)
    evidence['elapsed_s']=time.perf_counter()-started
    write_json(results_dir/'runtime_audit.json',evidence)
    print(json.dumps({'original_sources_identical':all(r['byte_identical'] for r in evidence['original_sources']), 'original_delivery_unchanged':before==after,'bundled_tests':evidence['bundled_tests'],'counterexamples':[p['name'] for p in evidence['probes'] if p.get('passed') is False]},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
