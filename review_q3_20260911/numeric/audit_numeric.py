"""Independent read-only Q3 artifact/numeric audit. Only writes beside this file.
No project solver code is imported here. Full main solver is run separately.
"""
from pathlib import Path
import csv, hashlib, json, math, platform, re, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from scipy.interpolate import PchipInterpolator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DELIVERY=ROOT/'q3_final_delivery'
VAL=DELIVERY/'validation'
OUT=DELIVERY/'output'
checks=[]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,passed,**details): checks.append({'check':name,'passed':bool(passed),**details})
def compare(name,a,b,tol=0):
    a=np.asarray(a); b=np.asarray(b); same=a.shape==b.shape
    diff=float(np.max(np.abs(a.astype(float)-b.astype(float)))) if same and a.size else 0.0
    check(name,same and np.isfinite(a).all() and np.isfinite(b).all() and diff<=tol,shape=list(a.shape),max_abs_diff=diff,tolerance=tol)
    return diff
def col(n):
    s=''
    while n: n,r=divmod(n-1,26);s=chr(65+r)+s
    return s

def spreadsheet(path):
    # Independent OOXML reader; no Pro spreadsheet helper is imported.
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        check(path.name+'_crc',z.testzip() is None)
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets=ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',ns)
        check(path.name+'_one_sheet',len(sheets)==1 and sheets[0].attrib['name']=='Sheet1')
        rid=sheets[0].attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        target=rels[rid]; target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        root=ET.fromstring(z.read(target))
        records={}; types={}; styles={}; formulas=0
        for cell in root.findall('.//s:sheetData/s:row/s:c',ns):
            address=cell.attrib['r'];typ=cell.attrib.get('t','n');v=cell.find('s:v',ns)
            formulas+=cell.find('s:f',ns) is not None
            if typ=='s': value=strings[int(v.text)]
            elif typ=='inlineStr': value=''.join(cell.find('s:is',ns).itertext())
            elif v is None: value=None
            elif typ=='n': value=float(v.text)
            else: value=v.text
            records[address]=value;types[address]=typ;styles[address]=int(cell.attrib.get('s','0'))
        check(path.name+'_no_formulas',formulas==0,formula_count=formulas)
        formats={}
        if 'xl/styles.xml' in z.namelist():
            st=ET.fromstring(z.read('xl/styles.xml'))
            custom={int(f.attrib['numFmtId']):f.attrib['formatCode'] for f in st.findall('s:numFmts/s:numFmt',ns)}
            for i,xf in enumerate(st.findall('s:cellXfs/s:xf',ns)):
                n=int(xf.attrib['numFmtId']);formats[i]=custom.get(n,str(n))
        return records,types,styles,formats

info=read(OUT/'main.json');event=read(OUT/'end_event.json');summary=read(VAL/'summary.json')
raw=np.load(OUT/'main.npz',allow_pickle=False)
t=raw['time_s']; samples=raw['sample_TC']; radii=raw['radius_cm']; evtime=raw['event_time_s']; evstate=raw['event_fields_TC']
check('formal_state_shapes',t.shape==(3450,) and samples.shape==(3450,21,2))
compare('formal_time_grid',t,np.r_[np.arange(0,206881,60.),206906.76])
compare('formal_radii',radii,np.arange(21)/10,1e-15)
check('initial_state',np.all(samples[0,:,0]==28) and np.all(samples[0,:,1]==2.55))
check('finite_positive_sample_states',np.isfinite(samples).all() and np.all(samples[:,:,1]>0))
compare('event_times_report',evtime,event['saved_event_times_s'])
evmax=np.max(evstate[:,:,:,1],axis=(1,2))
compare('event_max_from_whole_mesh',evmax,event['global_max_from_saved_fields'])
check('strict_event_sides',evmax[0]>.15 and abs(evmax[1]-.15)<1e-15 and evmax[2]<.15 and evmax[3]<.15,whole_mesh_maxima=evmax.tolist())
argmax=[np.unravel_index(np.argmax(x[:,:,1]),x[:,:,1].shape) for x in evstate]
check('event_max_at_center',all(x==(0,0) for x in argmax),indices=[list(map(int,x)) for x in argmax])
compare('endpoint_21_C_vs_full_mesh',samples[-1,:,1],PchipInterpolator(raw['r_m']**2,evstate[-1,:,0,1])(np.linspace(0,.02,21)**2),1e-15)
budget=event['numerical_error_budget_s'];step=.36
end_quantized=step*math.ceil((event['critical_s']+budget)/step)
compare('execution_time_quantization',event['execution_s'],end_quantized,6e-11)
compare('root_hours_conversion',event['critical_h'],event['critical_s']/3600)
compare('execution_hours_conversion',event['execution_h'],event['execution_s']/3600)
check('root_rounding_budget_stable',f"{(event['critical_s']-budget)/3600:.4f}"==f"{(event['critical_s']+budget)/3600:.4f}")
check('previous_full_minute_not_qualified',samples[-2,:,1].max()>.15,max_C=float(samples[-2,:,1].max()),time_s=float(t[-2]))
check('final_all_nodes_strict',evstate[-1,:,:,1].max()<.15,margin_kgkg=float(.15-evstate[-1,:,:,1].max()))

cells,types,styles,formats=spreadsheet(DELIVERY/'result3.xlsx')
headers=np.array([cells[f'{col(j)}1'] for j in range(2,23)],dtype=float)
excel_time=np.array([cells[f'A{i}'] for i in range(2,3451)],dtype=float)
excel_C=np.array([[cells[f'{col(j)}{i}'] for j in range(2,23)] for i in range(2,3451)],dtype=float)
compare('xlsx_all_21_radius_headers',headers,radii,1e-15)
compare('xlsx_all_3449_times',excel_time,t[1:])
compare('xlsx_all_72429_water_values',excel_C,samples[1:,:,1])
check('xlsx_all_75878_data_values_numeric',all(types[f'{col(j)}{i}']=='n' for i in range(2,3451) for j in range(1,23)))
water_formats={formats[styles[f'{col(j)}{i}']] for i in range(2,3451) for j in range(2,23)}
check('xlsx_water_format_exact_0_0000',water_formats=={'0.0000'},formats=sorted(water_formats))
check('xlsx_no_leftover_template_rows',max(int(re.search(r'\d+',a)[0]) for a in cells)==3450 and len(cells)==3450*22,rows=3450,stored_cells=len(cells))
check('xlsx_no_ellipsis',not any(isinstance(v,str) and ('...' in v or '…' in v) for v in cells.values()))
compare('xlsx_final_center_equals_execution_max',excel_C[-1,0],event['execution_max'])
check('xlsx_display_zero_point_1500_but_strictly_less',f'{excel_C[-1,0]:.4f}'=='0.1500' and excel_C[-1,0]<.15)
csv_full=np.genfromtxt(OUT/'result3_unrounded.csv',delimiter=',',skip_header=1,encoding='utf-8-sig')
compare('result3_csv_all_values',csv_full,np.column_stack((t[1:],samples[1:,:,1])))
selection=np.r_[np.searchsorted(t,np.arange(21600,194401,21600)),len(t)-1]
table=np.column_stack((t[selection]/3600,samples[selection][:,::5,1]))
table_csv=np.genfromtxt(OUT/'table5.csv',delimiter=',',skip_header=1,encoding='utf-8-sig')
compare('table5_csv_10_times_50_C_values',table_csv,table)
compare('table5_summary_10_times_50_C_values',summary['table5'],table)
expected_table=[[f'{float(x):.4f}' for x in row] for row in table]
for path in [OUT/'table5.md',DELIVERY/'第三问分析与最终答案.md']:
    parsed=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'): continue
        values=[x.strip() for x in line.strip('|').split('|')]
        if len(values)==6 and re.fullmatch(r'\d+\.\d{4}',values[0]) and values[0] in [x[0] for x in expected_table]:
            parsed.append(values)
    check('table5_four_decimal_text_'+path.name,parsed==expected_table,rows_found=len(parsed),water_values=50)

# Full workbook versus independent saved references; compare the same endpoint.
reference_reports=[]
for name in ['reference80','reference160']:
    with np.load(VAL/f'{name}.npz',allow_pickle=False) as z:
        bt=z['time_s']; b=z['sample_TC']
    with np.load(VAL/f'{name}_official_endpoint.npz',allow_pickle=False) as z:
        target=float(z['time_s']); endpoint=z['profile_TC']; reference_full_endpoint=z['full_TC']
    compare(name+'_regular_times_match',bt[:-1],t[:-1])
    compare(name+'_endpoint_same_time',target,t[-1])
    aligned=np.concatenate((b[1:-1],endpoint[None]),axis=0)
    delta=aligned[:,:,1]-excel_C
    mismatch=np.round(aligned[:,:,1],4)!=np.round(excel_C,4)
    idx=np.argwhere(mismatch); details=[]
    for i,j in idx:
        v=float(excel_C[i,j]);refv=float(aligned[i,j,1]);scale=v*10000
        half=(math.floor(scale)+.5)/10000
        details.append({'xlsx_row':int(i+2),'xlsx_column':col(int(j+2)),'time_s':float(excel_time[i]),'radius_cm':float(radii[j]),'main_C':v,'reference_C':refv,'difference_reference_minus_main':refv-v,'main_display':f'{v:.4f}','reference_display':f'{refv:.4f}','nearest_half_rounding_boundary':half,'main_distance_to_rounding_boundary':abs(v-half),'reference_distance_to_rounding_boundary':abs(refv-half)})
    rinfo=read(VAL/f'{name}.json')
    reference_reports.append({'reference':name,'comparison_cells':int(excel_C.size),'common_regular_rows':len(b)-2,'aligned_endpoint_s':target,'max_abs_C_difference':float(abs(delta).max()),'max_abs_T_difference':float(abs(aligned[:,:,0]-samples[1:,:,0]).max()),'four_decimal_mismatch_count':len(details),'mismatches':details,'critical_s':rinfo['event']['critical_s'],'main_minus_reference_root_s':event['critical_s']-rinfo['event']['critical_s'],'strict_endpoint_max_C':float(reference_full_endpoint[:,1].max()),'all_final_21_four_decimal_match':bool(np.array_equal(np.round(endpoint[:,1],4),np.round(excel_C[-1],4)))})
    # This check is numerical closeness, not a false assertion of all-cell 4dp agreement.
    check(name+'_all_workbook_values_close',np.max(abs(delta))<1e-6,max_abs_C_difference=float(abs(delta).max()),four_decimal_mismatch_count=len(details))
    check(name+'_official_endpoint_strict',reference_full_endpoint[:,1].max()<.15)

if '--preview' in sys.argv:
    preview={'preview_only':True,'all_checks_passed':all(c['passed'] for c in checks),'checks':checks,'independent_reference_all_cells':reference_reports}
    (HERE/'readback_reference_preview.json').write_text(json.dumps(preview,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks_passed':preview['all_checks_passed'],'references':reference_reports},ensure_ascii=False,indent=2))
    sys.exit(0 if preview['all_checks_passed'] else 1)

# Convergence, scenarios, geometry and flux comparisons recomputed from raw runs.
convergence=read(VAL/'convergence.json')
seq=[read(VAL/f'integral{n}.json') for n in (256,512,1024,2048)]
roots=np.array([d['event']['critical_s'] for d in seq]); increments=roots[:-1]-roots[1:]
orders=np.log2(increments[:-1]/increments[1:])
compare('observed_grid_orders',convergence['observed_orders'],orders,1e-14)
check('grid_series_same_temporal_settings',all({k:d['config'][k] for k in ['rtol','atol_T','atol_C','max_step','early_step']}=={k:seq[0]['config'][k] for k in ['rtol','atol_T','atol_C','max_step','early_step']} for d in seq))
tight1024=read(VAL/'integral1024_tight.json')
space=(tight1024['event']['critical_s']-event['critical_s'])/3
time_shift=max(abs(tight1024['event']['critical_s']-roots[2]),abs(event['critical_s']-roots[3]))
compare('fine_spatial_estimate',convergence['estimated_fine_spatial_error_s'],space)
compare('time_setting_shift',convergence['measured_time_setting_change_s'],time_shift)
compare('Richardson_diagnostic',convergence['richardson_diagnostic_s'],event['critical_s']-space)
input_cells,_,_,_=spreadsheet(DELIVERY/'inputs/attachment1.xlsx')
environment=np.array([[input_cells[f'{c}{i}'] for c in 'ABC'] for i in range(2,243)])
tail=environment[environment[:,0]>=10800,1:]
future=tail.mean(axis=0)
compare('future_61_sample_arithmetic_mean',info['future'],future)
scenario_rows=[]
baseline=seq[1]['event']['critical_s']
for row in read(VAL/'scenario_comparison.json'):
    d=read(VAL/(row['case']+'.json')); difference=d['event']['critical_s']-baseline
    compare('scenario_difference_'+row['case'],row['change_from_same_grid_baseline_s'],difference)
    check('scenario_same_grid_'+row['case'],d['config']['n']==512 and d['config']['nz']==0)
    scenario_rows.append({'case':row['case'],'critical_s':d['event']['critical_s'],'delta_s':difference,'delta_minutes':difference/60,'delta_hours':difference/3600})
harmonic=[]
for n in (512,1024):
    hi=read(VAL/f'harmonic{n}.json');ii=read(VAL/f'integral{n}.json')
    harmonic.append(hi['event']['critical_s']-ii['event']['critical_s'])
hc=read(VAL/'harmonic_comparison.json')
compare('harmonic_event_differences',[r['same_mesh_flux_event_difference_s'] for r in hc['rows']],harmonic)
compare('harmonic_error_reduction_factor',hc['difference_reduction_factor'],harmonic[0]/harmonic[1])
geometry=[]
for row in read(VAL/'geometry_comparison.json'):
    d=read(VAL/(row['case']+'.json'));radial=read(VAL/f"radial{row['n_r']}.json")
    effect=d['event']['critical_s']-radial['event']['critical_s']
    compare('paired_geometry_effect_'+row['case'],row['end_effect_vs_matching_radial_s'],effect)
    geometry.append({'case':row['case'],'critical_s':d['event']['critical_s'],'matching_radial_s':radial['event']['critical_s'],'matched_end_effect_s':effect,'radial_discretization_vs_fine_main_s':radial['event']['critical_s']-event['critical_s'],'raw_geometry_vs_fine_main_s':d['event']['critical_s']-event['critical_s']})

# Saved complete states, all 60s mesh samples, balance, and mechanism values.
full=raw['full_TC']; weights=raw['weights'].ravel(); snaps=raw['snapshots'];st=raw['snapshot_time_s']
check('full_mesh_shape',full.shape==(3450,2049,1,2),shape=list(full.shape))
check('full_mesh_all_positive',np.isfinite(full).all() and np.all(full[:,:,:,1]>0),minimum_C=float(full[:,:,:,1].min()))
check('full_mesh_radial_C_nonincrease_up_to_roundoff',np.diff(full[:,:,:,1],axis=1).max()<1e-12,max_up=float(np.diff(full[:,:,:,1],axis=1).max()))
maxima=full[:,:,:,1].max(axis=(1,2))
check('full_mesh_only_execution_sample_strict',np.all(maxima[:-1]>.15) and maxima[-1]<.15)
mean=np.einsum('tr,r->t',full[:,:,0,1],weights)/weights.sum()
balance=raw['balance']; balance_indices=np.searchsorted(t,balance[:,0])
compare('balance_time_has_full_sample',t[balance_indices],balance[:,0])
compare('water_balance_reassembled',balance[:,1],mean[balance_indices]-2.55+balance[:,3],2e-14)
compare('water_balance_max',info['max_water_balance_kgkg'],np.max(abs(balance[:,1])))
compare('heat_balance_reassembled',balance[:,2],balance[:,4]+balance[:,5])
compare('heat_balance_max',info['max_effective_heat_balance_J_m3'],np.max(abs(balance[:,2])))
compare('heat_balance_relative',info['effective_heat_relative'],np.max(abs(balance[:,2]))/max(1,abs(balance[-1,4])))
mechanism=read(VAL/'mechanism.json')
for i,row in enumerate(mechanism['snapshots']):
    q=snaps[i,:,0];c=q[:,1];temp=q[:,0]
    diffusivity=.0024*np.exp(-.45/c)*np.exp(-3850/(temp+273.15))
    ce=np.interp(st[i],environment[:,0],environment[:,2]) if st[i]<=14400 else future[1]
    vals={'time_s':st[i],'center_C':c[0],'surface_C':c[-1],'volume_mean_C':weights@c/weights.sum(),'center_T':temp[0],'surface_T':temp[-1],'center_D':diffusivity[0],'surface_D':diffusivity[-1],'D_ratio':diffusivity.max()/diffusivity.min(),'outward_surface_water_flux_kgkg_m_s':8e-7*(c[-1]-ce)}
    for k,v in vals.items(): compare(f'mechanism_{i}_{k}',row[k],v,1e-12 if k=='D_ratio' else 1e-14)
compare('dry_tail_fraction_after_18h',mechanism['fraction_of_total_time_after_18h'],(event['critical_s']-64800)/event['critical_s'])
for key in ('surface','mean'):
    compare(key+'_crossing_hours',mechanism[key+'_015_time_s'],info[key+'_crossing_s'])

q2=np.load(ROOT/'q2_final_delivery/output/q2_unrounded.npz',allow_pickle=False)
mask=t<=10800;ix=t[mask].astype(int)
q2_reg={}
for j,key in enumerate(('temperature_degC','moisture_dry_basis')):
    diff=samples[mask,:,j]-q2[key][ix]
    q2_reg[key]={'max_abs_diff':float(abs(diff).max()),'four_decimal_mismatch_count':int(np.count_nonzero(np.round(samples[mask,:,j],4)!=np.round(q2[key][ix],4)))}
check('q2_regression_report_honest',q2_reg['temperature_degC']['four_decimal_mismatch_count']==1 and q2_reg['moisture_dry_basis']['four_decimal_mismatch_count']==3,details=q2_reg)

rerun={}
fresh_path=HERE/'main_reproduced.npz'
if fresh_path.exists():
    fresh_info=read(HERE/'main_reproduced.json')
    with np.load(fresh_path,allow_pickle=False) as fresh:
        compare('fresh_same_config',list(fresh_info['config'].keys())==list(info['config'].keys()),True)
        check('fresh_config_equal',fresh_info['config']==info['config'])
        compare('fresh_times',fresh['time_s'],t)
        ds=fresh['sample_TC']-samples
        for j,unit in [(0,'T_K'),(1,'C_kgkg')]:
            rerun['max_'+unit+'_difference']=compare('fresh_sample_'+unit,fresh['sample_TC'][:,:,j],samples[:,:,j],2e-10)
        rerun['event_delta_s']=fresh_info['event']['critical_s']-event['critical_s']
        compare('fresh_root',fresh_info['event']['critical_s'],event['critical_s'],1e-4)
        df=fresh['full_TC']-full
        rerun['full_T_max_difference']=float(np.max(abs(df[:,:,:,0])))
        rerun['full_C_max_difference']=float(np.max(abs(df[:,:,:,1])))
        check('fresh_full_mesh_agreement',rerun['full_T_max_difference']<2e-10 and rerun['full_C_max_difference']<2e-10,**{k:v for k,v in rerun.items() if k.startswith('full_')})
        rerun['four_decimal_C_mismatch_count']=int(np.count_nonzero(np.round(fresh['sample_TC'][1:,:,1],4)!=np.round(excel_C,4)))
        check('fresh_all_72429_C_four_decimal_agree',rerun['four_decimal_C_mismatch_count']==0)
        rerun['elapsed_solver_s']=fresh_info['elapsed_s'];rerun['execution_max']=fresh_info['event']['execution_max']
        rerun['balance_water_max']=fresh_info['max_water_balance_kgkg'];rerun['balance_heat_relative']=fresh_info['effective_heat_relative']
else:
    check('fresh_main_run_present',False)

report={'scope':'Independent numeric/OOXML audit and one true main N2048 replay; original sources unchanged; no full validation suite rerun.',
        'runtime':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
        'all_checks_passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [OUT/'main.npz',OUT/'main.json',DELIVERY/'result3.xlsx',OUT/'table5.csv',DELIVERY/'source/q3_solver.py',DELIVERY/'validation/configs/main.json']},
        'workbook':{'data_rows':len(excel_time),'water_values':int(excel_C.size),'max_readback_error':float(np.max(abs(excel_C-samples[1:,:,1]))),'number_formats':sorted(water_formats),'final_raw_center':float(excel_C[-1,0]),'final_display_center':f'{excel_C[-1,0]:.4f}'},
        'event':{'critical_s':event['critical_s'],'execution_s':event['execution_s'],'quantized_s':end_quantized,'critical_to_execution_s':event['execution_s']-event['critical_s'],'t206901_before_root_s':event['critical_s']-206901,'engineering_budget_s':budget,'strict_margin_C':float(.15-evmax[-1])},
        'independent_reference_all_cells':reference_reports,'grid_convergence':{'orders':orders.tolist(),'space_estimate_s':space,'time_setting_shift_s':time_shift},
        'scenarios':scenario_rows,'geometry_decomposition':geometry,'q2_regression':q2_reg,'fresh_main_run':rerun,
        'caveats':['The workbook readback is exact storage verification, not proof of four-decimal agreement against all independent solutions. Full independent mismatch coordinates are included.','The 0.03 s budget is an engineering discretization estimate, not an interval-arithmetic PDE certificate.','PCHIP in r squared bounds reconstruction between actual full-grid values.','Physical conclusion is conditional on effective fixed-cylinder radial model and the declared 61-sample arithmetic-mean future environment.']}
nominal=read(VAL/'scenario_nominal.json')['event']['critical_s']
report['comparison_to_206901']={
    'same_mean_model_continuation':read(HERE/'comparison_206901.json'),
    'alternative_nominal_50C_0_05_N512_root_s':nominal,
    'alternative_nominal_first_integer_second':math.ceil(nominal),
    'nominal_minus_matching_mean_N512_s':nominal-baseline,
    'interpretation':'206901 is consistent with rounding the nominal-platform scenario root upward to an integer second. This is a possible explanation, not evidence of the assumptions used by another person.',
    'geometry_warning':'The 80x64 isothermal-after-6h cylinder root is 206901.783371 s. Its raw difference from fine 1D combines about +3.049542 s radial discretization and -7.660840 s matched-grid end effect; do not attribute the combined difference entirely to geometry.'}
(HERE/'numeric_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps({'passed':report['all_checks_passed'],'checks':len(checks),'failed':[x for x in checks if not x['passed']],
                  'references':reference_reports,'rerun':rerun,'event':report['event']},ensure_ascii=False,indent=2))
sys.exit(0 if report['all_checks_passed'] else 1)
