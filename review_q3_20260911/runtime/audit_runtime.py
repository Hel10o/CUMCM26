"""Postprocess one real reference run and isolate concrete runtime counterexamples.

No full suite, no original verify-in-place, and no changes to frozen Q3 delivery.
"""
from __future__ import annotations
import contextlib,csv,hashlib,importlib.util,io,json,os,shutil,sys,tempfile,zipfile
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
sys.dont_write_bytecode=True
import numpy as np
from scipy.integrate import solve_ivp

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DELIVERY=ROOT/'q3_final_delivery'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def round_strings(array):return np.fromiter((f'{v:.4f}' for v in np.asarray(array).ravel()),dtype='U24').reshape(np.asarray(array).shape)

def main():
    source_files=[*sorted((DELIVERY/'source').glob('*.py')),DELIVERY/'run_all.py',DELIVERY/'validation/configs/main.json',DELIVERY/'inputs/attachment1.xlsx',DELIVERY/'result3.xlsx']
    before={p.relative_to(DELIVERY).as_posix():sha(p) for p in source_files}
    # Copy code before running validation helpers: their default root is unsafe.
    copied=HERE/'source_copy'
    if not copied.exists():shutil.copytree(DELIVERY/'source',copied,ignore=shutil.ignore_patterns('__pycache__'))
    sys.path.insert(0,str(copied))
    import q3_reference as ref
    import q3_solver as solver
    import validate_results as validation
    import make_report
    info=json.loads((HERE/'reference80.json').read_text())
    original_info=json.loads((DELIVERY/'validation/reference80.json').read_text())
    main_info=json.loads((DELIVERY/'output/main.json').read_text())
    z=np.load(HERE/'reference80.npz');primary=np.load(DELIVERY/'output/main.npz')
    raw=solver.load_input(ROOT/'A题/附件/附件1.xlsx')
    target=float(primary['time_s'][-1]);start=float(z['snapshot_time_s'][-1]);n=info['n']
    assert 0<target-start<1
    env=solver.Environment(raw,'mean');op=ref.Reference(n);y=z['snapshots'][-1,:-1].ravel()
    sol=solve_ivp(lambda t,v:op.evaluate(t,v,env),(start,target),y,method='Radau',jac=lambda t,v:op.evaluate(t,v,env,True),rtol=2e-12,atol=np.tile([2e-12,2e-14],n),max_step=.05)
    assert sol.success
    final=op.surface(target,sol.y[:,-1].reshape(n,2),env);profile=op.profiles(final);ext=op.extrema(final)
    np.savez_compressed(HERE/'reference80_official_endpoint.npz',time_s=target,full_TC=final,profile_TC=profile,main_difference_TC=profile-primary['sample_TC'][-1])
    common=primary['time_s'][:-1]
    assert np.array_equal(common,z['time_s'][:-1])
    projected=np.concatenate([z['sample_TC'][:-1],profile[None]],axis=0)
    difference=projected-primary['sample_TC']
    regular=np.flatnonzero(np.isin(common,np.arange(21600,194401,21600)))
    rows=np.r_[regular,len(projected)-1];radii=[0,5,10,15,20]
    comparison={}
    def mismatch_record(i,j,col,rounded_main,rounded_ref):
        main_value=float(primary['sample_TC'][i+1,j,col]);reference_value=float(projected[i+1,j,col])
        boundary=(Decimal(str(rounded_main[i,j]))+Decimal(str(rounded_ref[i,j])))/2
        return {'time_s':float(primary['time_s'][i+1]),'radius_cm':float(primary['radius_cm'][j]),'main_unrounded':main_value,
            'reference_unrounded':reference_value,'main_display':str(rounded_main[i,j]),'reference_display':str(rounded_ref[i,j]),
            'decimal_rounding_midpoint':str(boundary),'main_signed_distance_to_midpoint':str(Decimal(str(main_value))-boundary),
            'reference_signed_distance_to_midpoint':str(Decimal(str(reference_value))-boundary)}
    for col,key in ((0,'temperature_K'),(1,'moisture_kgkg')):
        d=difference[1:,:,col];idx=np.unravel_index(np.argmax(abs(d)),d.shape)
        rounded_ref=round_strings(projected[1:,:,col]);rounded_main=round_strings(primary['sample_TC'][1:,:,col])
        mismatches=np.argwhere(rounded_ref!=rounded_main)
        comparison[key]={'maximum_abs':float(abs(d).max()),'maximum_time_s':float(primary['time_s'][idx[0]+1]),'maximum_radius_cm':float(primary['radius_cm'][idx[1]]),
            'all_exported_four_decimal_mismatches':len(mismatches),
            'mismatch_details':[mismatch_record(i,j,col,rounded_main,rounded_ref) for i,j in mismatches]}
    table=np.column_stack([primary['time_s'][rows]/3600,projected[rows][:,radii,1]])
    expected=np.loadtxt(DELIVERY/'output/table5.csv',delimiter=',',skiprows=1,encoding='utf-8-sig')
    assert table.shape==expected.shape==(10,6)
    np.savetxt(HERE/'reference80_table5.csv',table,delimiter=',',header='time_h,r0cm,r0.5cm,r1cm,r1.5cm,r2cm',comments='',fmt='%.17g')
    numerical={'scope':'One 80-degree independent collocation/Radau run from t=0 to threshold; short real continuation to the official endpoint. No full suite.',
        'input_original_sha256':sha(ROOT/'A题/附件/附件1.xlsx'),'input_bundled_sha256':sha(DELIVERY/'inputs/attachment1.xlsx'),
        'source_sha256':sha(DELIVERY/'source/q3_reference.py'),'n':n,'method':info['method'],'elapsed_s':info['elapsed_s'],
        'critical_s':info['event']['critical_s'],'critical_h':info['event']['critical_h'],
        'difference_from_delivered_reference_s':info['event']['critical_s']-original_info['event']['critical_s'],
        'difference_from_delivered_primary_s':info['event']['critical_s']-main_info['event']['critical_s'],
        'critical_h_four_decimal':f"{info['event']['critical_h']:.4f}",'root_bracket':info['event'],
        'official_endpoint':{'time_s':target,'elapsed_continuation_s':target-start,'nfev':sol.nfev,'polynomial_extrema':ext,'center_C':float(profile[0,1]),'surface_C':float(profile[-1,1]),
            'max_T_difference':float(abs(difference[-1,:,0]).max()),'max_C_difference':float(abs(difference[-1,:,1]).max()),'all_21_four_decimal_match':bool(np.array_equal(round_strings(profile[:,1]),round_strings(primary['sample_TC'][-1,:,1])))},
        'full_export_comparison':comparison,'table5':{'water_values':50,'max_C_difference':float(abs(table[:,1:]-expected[:,1:]).max()),'all_50_four_decimal_match':bool(np.array_equal(round_strings(table[:,1:]),round_strings(expected[:,1:])))},
        'independence':'Different global collocation space operator, primitive-gradient reconstruction, algebraic Robin surface, Radau time method; shares only input parser and Environment with q3_solver. This is a fresh run of the delivered independent algorithm, not a newly authored third implementation.',
        'fresh_reference_boundary_checks':{k:info[k] for k in ('min_scalar_boundary_derivative','max_boundary_residual','max_boundary_newton','boundary_fallbacks','dense_U_overshoot','global_C_min')}}
    dump(HERE/'reference_comparison.json',numerical)
    print(json.dumps({'reference_critical_h':numerical['critical_h'],'main_difference_s':numerical['difference_from_delivered_primary_s'],'endpoint_max_C':ext['max_C'],'table5':numerical['table5'],'full_export':comparison},ensure_ascii=False,indent=2),flush=True)

    probes=[]
    with tempfile.TemporaryDirectory(prefix='q3_runtime_probe_',dir=HERE) as td:
        sandbox=Path(td)
        fixture=sandbox/'xlsx_fixture';(fixture/'output').mkdir(parents=True);(fixture/'validation').mkdir()
        np.savez_compressed(fixture/'output/main.npz',time_s=primary['time_s'],sample_TC=primary['sample_TC'])
        shutil.copy2(DELIVERY/'output/end_event.json',fixture/'output/end_event.json')
        shutil.copy2(DELIVERY/'result3.xlsx',fixture/'result3.xlsx')
        baseline=validation.xlsx_check(fixture)
        probes.append({'name':'copied_original_xlsx_accepts','observed_accepted':True,'expected_accepted':True,'passed':True,'cells':baseline['water_cells_checked']})
        def mutate_workbook(label,change):
            path=fixture/(label+'.xlsx')
            with zipfile.ZipFile(DELIVERY/'result3.xlsx') as original,zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as modified:
                for item in original.infolist():
                    content=original.read(item.filename)
                    if item.filename=='xl/worksheets/sheet1.xml':
                        xml=ET.fromstring(content);change(xml);content=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
                    modified.writestr(item,content)
            try:result=validation.xlsx_check(fixture,path);accepted=True;reason=None
            except Exception as exc:accepted=False;reason=repr(exc)
            probes.append({'name':label,'observed_accepted':accepted,'expected_accepted':False,'passed':not accepted,'reason':reason})
        ns='{'+solver.NS['s']+'}'
        def extra_column(xml):
            row=xml.find('.//'+ns+'row'+'[@r="2"]');cell=ET.SubElement(row,ns+'c',{'r':'W2','t':'n'});ET.SubElement(cell,ns+'v').text='999'
        mutate_workbook('extra_column_W2',extra_column)
        def wrong_header(xml):
            cell=xml.find('.//'+ns+'c'+'[@r="A1"]');cell.clear();cell.set('r','A1');cell.set('t','inlineStr');inline=ET.SubElement(cell,ns+'is');ET.SubElement(inline,ns+'t').text='time/min; radius/m (wrong units)'
        mutate_workbook('wrong_A1_units',wrong_header)
        # No integration is performed for this zero-duration output-protection
        # fixture; it exercises the documented low-level solver's save path.
        prefix=sandbox/'existing_array';prefix.with_suffix('.npz').write_bytes(b'existing independent evidence')
        before_npz=sha(prefix.with_suffix('.npz'))
        output=io.StringIO()
        with contextlib.redirect_stdout(output):solver.solve(solver.Config(n=8,end_s=0),prefix,ROOT/'A题/附件/附件1.xlsx')
        probes.append({'name':'orphan_npz_must_not_be_overwritten','observed_overwritten':sha(prefix.with_suffix('.npz'))!=before_npz,'expected_overwritten':False,
            'passed':sha(prefix.with_suffix('.npz'))==before_npz,'note':'zero-duration isolated solver fixture; no PDE integration'})
        (HERE/'counterexample_solver.log').write_text(output.getvalue(),encoding='utf-8')
        # The report's introduction must use the event in its own summary.
        report_fixture=sandbox/'report_fixture';(report_fixture/'validation').mkdir(parents=True);(report_fixture/'output').mkdir()
        summary=json.loads((DELIVERY/'validation/summary.json').read_text())
        summary['event']['critical_h']=60.;summary['event']['execution_h']=60.0001
        dump(report_fixture/'validation/summary.json',summary)
        shutil.copy2(DELIVERY/'validation/xlsx_readback.json',report_fixture/'validation/xlsx_readback.json')
        make_report.generate(report_fixture)
        generated=(report_fixture/'第三问分析与最终答案.md').read_text(encoding='utf-8')
        probes.append({'name':'report_heading_uses_its_event_data','observed_old_time_remains':'**57.4740 h**' in generated.split('## 2')[0],
            'expected_old_time_remains':False,'passed':'**57.4740 h**' not in generated.split('## 2')[0],
            'fixture_event_h':60.,'note':'report-only synthetic fixture; not a claimed new physical solution'})
        (HERE/'counterexample_report_excerpt.txt').write_text(generated.split('## 2')[0],encoding='utf-8')
    after={p.relative_to(DELIVERY).as_posix():sha(p) for p in source_files}
    dump(HERE/'runtime_counterexamples.json',{'scope':'Copied code, isolated data mutations, no modification of original package','probes':probes,'original_selected_files_unchanged':before==after,'selected_original_sha256':before})
    print(json.dumps({'counterexamples':[x['name'] for x in probes if not x['passed']],'original_selected_files_unchanged':before==after},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
