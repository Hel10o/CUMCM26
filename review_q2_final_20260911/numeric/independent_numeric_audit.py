"""Independent Q2 refinement audit. No source import or PDE execution.

Run from any directory. All writes stay beside this script. Requires NumPy.
Uses the original accepted trajectories, independently computed finite-difference
weights and previously reproduced seven parameter trajectories.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import platform
import sys
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
NEW = ROOT / 'q2_refinement_delivery'
OLD = ROOT / 'q2_final_delivery'
FRESH = ROOT / 'review_q2_20260911/reproduced/validation'

def read_json(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def arrays(p):
    with np.load(p, allow_pickle=False) as z:
        return {k:z[k] for k in z.files}

checks = []
# Preserve the first strict equality probe. Cross-platform libm and text newline
# changes are subsequently assessed numerically, never concealed as exact bytes.
if (OUT/'numeric_audit.json').exists() and not (OUT/'initial_strict_comparison.json').exists():
    (OUT/'initial_strict_comparison.json').write_bytes((OUT/'numeric_audit.json').read_bytes())
def record(name, passed, **details):
    checks.append(dict(check=name, passed=bool(passed), **details))

def compare(name, actual, expected, atol=0.0):
    actual=np.asarray(actual); expected=np.asarray(expected)
    shape=actual.shape == expected.shape
    finite=np.isfinite(actual).all() and np.isfinite(expected).all()
    delta=float(np.max(np.abs(actual.astype(float)-expected.astype(float)))) if shape and actual.size else 0.0
    record(name, shape and finite and delta <= atol, max_abs_diff=delta, tolerance=atol, shape=list(actual.shape))
    return delta

def derivative(y, h):
    """Interpolate a quartic on a one-sided or central 5-node interval.
    Solve monomial moment equations for derivative weights independently of
    Pro's hardcoded weights. Anchor values to reduce constant cancellation.
    """
    result=np.empty_like(y)
    cache={}
    for i in range(y.shape[0]):
        left=(i//60)*60
        right=min(left+60,y.shape[0]-1)
        if i == y.shape[0]-1:
            left=max(0,i-60)
        if i-2*h >= left and i+2*h <= right:
            offset=(-2,-1,0,1,2)
        elif i+4*h <= right:
            offset=(0,1,2,3,4)
        else:
            offset=(0,-1,-2,-3,-4)
        if offset not in cache:
            x=np.array(offset,dtype=float)
            rhs=np.array([0,1,0,0,0],dtype=float)
            cache[offset]=np.linalg.solve(np.stack([x**k for k in range(5)]),rhs)/h
        ix=i+h*np.array(offset)
        assert ix.min() >= left and ix.max() <= right
        result[i]=cache[offset] @ (y[ix]-y[i])
    return result

raw_path=OLD/'output/q2_unrounded.npz'
raw=arrays(raw_path)
pro=arrays(NEW/'data/mechanism_unrounded.npz')
projection=arrays(NEW/'reused/sensitivity_tracks.npz')
source_record=read_json(NEW/'reused/sensitivity_provenance.json')
claim=read_json(NEW/'data/mechanism_validation.json')
record('accepted_raw_byte_identity',sha(raw_path)==sha(NEW/'reused/q2_final_delivery/output/q2_unrounded.npz'),sha256=sha(raw_path))
record('projection_byte_identity',sha(NEW/'reused/sensitivity_tracks.npz')==source_record['projected_file']['sha256'],sha256=sha(NEW/'reused/sensitivity_tracks.npz'))
t=raw['time_s']; T=raw['temperature_degC'][:,[0,10,20]]; C=raw['moisture_dry_basis'][:,[0,10,20]]
Tk=T+273.15
logD=np.log(.0024)-.45/C-3850/Tk
logD0=np.log(.0024)-.45/2.55-3850/301.15
D=np.exp(logD); D0=float(np.exp(logD0)); H=3850*(1/301.15-1/Tk); M=.45*(1/2.55-1/C)
ratio=np.exp(logD-logD0)
compare('temperature_extraction',pro['T'],T)
compare('moisture_extraction',pro['C'],C)
compare('H_independent',pro['H'],H)
compare('M_independent',pro['M'],M)
compare('D_log_exp_independent',pro['D'],D,1e-21)
compare('D_ratio_log_exp_independent',pro['D_over_D0'],ratio,2e-14)
identity=float(np.max(np.abs(logD-logD0-H-M)))
record('log_decomposition_identity',identity<1e-13,max_abs_error=identity)

rates={}
td1=cd1=None
for h in (1,2,5):
    td=derivative(T,h); cd=derivative(C,h)
    ht=3850*td/Tk**2; mt=.45*cd/C**2
    rates[h]=ht+mt
    compare(f'independent_rate_h{h}',pro[f'rate_h{h}'],rates[h],2e-15)
    if h==1:
        td1=td; cd1=cd
        compare('independent_H_rate',pro['H_rate'],ht,2e-15)
        compare('independent_M_rate',pro['M_rate'],mt,2e-15)
err=np.maximum(np.abs(rates[1]-rates[2]),np.abs(rates[1]-rates[5]))
trusted=(t>=10)&(t<=10790)
threshold=np.maximum(5*err,1e-10)
sign=np.where(rates[1]>threshold,1,np.where(rates[1]<-threshold,-1,0))
sign[~trusted]=0
compare('rate_interpretable_mask',pro['rate_interpretable'],trusted)
compare('derivative_step_difference',pro['rate_step_difference'],err,2e-15)

matrix=np.genfromtxt(NEW/'data/mechanism_timeseries.csv',delimiter=',',names=True)
record('mechanism_csv_row_count',len(matrix)==10801*3,rows=len(matrix))
for j in range(3):
    block=matrix[j*len(t):(j+1)*len(t)]
    for column,expected in [('time_s',t),('radius_cm',np.full(len(t),j)),('temperature_degC',T[:,j]),('C_kgkg_dry',C[:,j]),('D_m2_s',D[:,j]),('H_log',H[:,j]),('M_log',M[:,j]),('D_over_D0',ratio[:,j]),('T_rate_K_s',td1[:,j]),('C_rate_kgkg_s',cd1[:,j]),('lnD_rate_s-1',rates[1][:,j]),('net_sign_certified',sign[:,j]),('rate_interpretable',trusted)]:
        # genfromtxt sanitizes minus signs in field names.
        column_clean=column.replace('-','')
        compare(f'csv_{j}_{column}',block[column_clean],expected,2e-14)

interval=np.genfromtxt(NEW/'data/interval_60s_contributions.csv',delimiter=',',skip_header=1)
interval_expected=[]
for j in range(3):
    for lo in range(0,10800,60):
        dh=H[lo+60,j]-H[lo,j]; dm=M[lo+60,j]-M[lo,j]
        interval_expected.append([lo,lo+60,j,dh,dm,dh+dm,dh/60,dm/60,(dh+dm)/60])
compare('sixty_second_endpoint_integrals_all_4860_values',interval,interval_expected)
half=[]
for j in range(3):
    for ti in range(0,10801,1800):
        half.append([ti/3600,j,T[ti,j],C[ti,j],H[ti,j],M[ti,j],D[ti,j],ratio[ti,j]])
compare('half_hour_table_all_values',np.genfromtxt(NEW/'data/mechanism_table.csv',delimiter=',',skip_header=1),half,2e-14)

locations=[]
for j in range(3):
    ratio_direct=pro['D_over_D0'][:,j]
    imin=int(np.argmin(D[:,j])); imax=int(np.argmax(D[:,j]))
    idx=np.flatnonzero((logD[:-1,j]<logD0)&(logD[1:,j]>=logD0))
    crossing=float(idx[0]+(logD0-logD[idx[0],j])/(logD[idx[0]+1,j]-logD[idx[0],j])) if len(idx) else None
    entry=dict(radius_cm=j,H_3h=float(H[-1,j]),M_3h=float(M[-1,j]),D_ratio_3h=float(ratio[-1,j]),global_sample_min_s=imin,global_sample_max_s=imax,D_ratio_min=float(ratio[imin,j]),D_ratio_max=float(ratio[imax,j]),last_half_hour_delta_H=float(H[-1,j]-H[9000,j]),last_half_hour_delta_M=float(M[-1,j]-M[9000,j]),last_half_hour_D_relative_change=float(np.expm1(logD[-1,j]-logD[9000,j])),return_to_initial_D_s_linear_between_samples=crossing,rate_positive_time_fraction_2to3h=float(np.mean(sign[7200:10800,j]>0)),rate_negative_time_fraction_2to3h=float(np.mean(sign[7200:10800,j]<0)),temperature_cooling_seconds_2to3h=int(np.count_nonzero(td1[7200:10800,j]<-1e-9)))
    for key,value in entry.items():
        if value is None:
            record(f'claimed_location_{j}_{key}',claim['locations'][j][key] is None)
        else:
            compare(f'claimed_location_{j}_{key}',claim['locations'][j][key],value,1e-9 if 'return_to' in key else 2e-14)
    locations.append(entry)

with (NEW/'data/parameter_sensitivity_timeseries.csv').open(encoding='utf-8',newline='') as f:
    sens_rows=list(csv.DictReader(f))
record('sensitivity_csv_row_count',len(sens_rows)==2*4*10801,rows=len(sens_rows))
sens_summary=[]
all_sensitivity_diffs={}
for par_index,par in enumerate(('hm','hT')):
    def expand(name,field):
        return np.column_stack((projection[name+'__'+field],projection[name+'__average_'+field]))
    cb=expand('baseline','moisture_dry_basis'); tb=expand('baseline','temperature_degC')
    cl=expand(par+'_0.8','moisture_dry_basis'); ch=expand(par+'_1.2','moisture_dry_basis')
    tl=expand(par+'_0.8','temperature_degC'); th=expand(par+'_1.2','temperature_degC')
    ec=(ch-cl)/(.4*cb); et=np.divide(th-tl,.4*(tb-28),out=np.full_like(tb,np.nan),where=tb-28>=.05)
    maxdiff=0.0; masks_ok=True
    for j,loc in enumerate(('axis','r1cm','surface','rdr_mean')):
        block=sens_rows[(par_index*4+j)*len(t):(par_index*4+j+1)*len(t)]
        expected=np.column_stack([t,cb[:,j],cl[:,j],ch[:,j],ec[:,j],tb[:,j],tl[:,j],th[:,j]])
        actual=np.array([[float(r[k]) for k in ('time_s','C_base','C_minus20','C_plus20','C_secant_elasticity','T_base','T_minus20','T_plus20')] for r in block])
        maxdiff=max(maxdiff,float(np.max(np.abs(actual-expected))))
        actual_t=np.array([float(r['T_rise_secant_elasticity_blank_if_rise_lt_0.05K']) if r['T_rise_secant_elasticity_blank_if_rise_lt_0.05K'] else np.nan for r in block])
        mask=np.isfinite(et[:,j]); masks_ok &= np.array_equal(np.isfinite(actual_t),mask)
        maxdiff=max(maxdiff,float(np.max(np.abs(actual_t[mask]-et[mask,j]))))
        record(f'sensitivity_labels_{par}_{loc}',all(r['parameter']==par and r['location']==loc for r in block))
        sens_summary.append(dict(parameter=par,location=loc,C_secant_elasticity=float(ec[-1,j]),T_rise_secant_elasticity=float(et[-1,j]),maximum_abs_T_change=float(max(np.max(np.abs(tl[:,j]-tb[:,j])),np.max(np.abs(th[:,j]-tb[:,j]))))))
    record(f'sensitivity_{par}_all_values_and_masks',maxdiff==0 and masks_ok,max_abs_diff=maxdiff,masks_match=masks_ok)

with (NEW/'data/parameter_sensitivity_3h.csv').open(encoding='utf-8',newline='') as f:
    end_rows=list(csv.DictReader(f))
for i,entry in enumerate(sens_summary):
    for key,value in entry.items():
        if isinstance(value,str):
            record(f'sensitivity_end_label_{i}_{key}',claim['sensitivity_3h'][i][key]==value and end_rows[i][key]==value)
        else:
            compare(f'sensitivity_end_claim_{i}_{key}',claim['sensitivity_3h'][i][key],value)
            compare(f'sensitivity_end_csv_{i}_{key}',float(end_rows[i][key]),value)

# Metadata and numbers of seven original-Pro projections against prior fresh rerun.
# Matching numeric projections does NOT make their source archive bytes present.
old_manifest=read_json(OLD/'evidence/delivery_manifest.json')
old_entries={d['path']:d for d in old_manifest['files']}
source_diffs=[]
for src in source_record['source_arrays']:
    name=src['name']; suffix=f'output/validation/sensitivity_{name}.npz'
    recorded=old_entries[suffix]
    record('pro_source_manifest_'+name,src['sha256']==recorded['sha256'],sha256=src['sha256'],original_array_present=(OLD/suffix).exists())
    fresh=arrays(FRESH/f'sensitivity_{name}.npz'); meta=read_json(FRESH/f'sensitivity_{name}.json')
    diffs={}
    for field in ('temperature_degC','moisture_dry_basis','average_temperature_degC','average_moisture_dry_basis','environment'):
        actual=projection[name+'__'+field]
        expected=fresh[field][:,[0,10,20]] if field in ('temperature_degC','moisture_dry_basis') else fresh[field]
        diffs[field]=compare(f'original_projection_vs_fresh_{name}_{field}',actual,expected,2e-11)
    same_grid=meta['n']==320 and meta['end_s']==10800 and np.array_equal(fresh['internal_radius_m'],arrays(FRESH/'sensitivity_baseline.npz')['internal_radius_m'])
    record('same_grid_metadata_'+name,same_grid,n=meta['n'],nodes=meta['nodes'],parameters=meta['parameters'],environment=meta['environment'],freeze=meta['freeze'])
    expected_parameters=dict(R=.02,L=.25,T0=28.,C0=2.55,hT=25.,hm=8e-7)
    if name.startswith(('hm_','hT_')):
        varied,factor=name.split('_'); expected_parameters[varied]*=float(factor)
    record('single_factor_parameters_'+name,meta['parameters']==expected_parameters and meta['freeze']==(name=='freeze_all_initial') and meta['environment']==('pchip' if name=='pchip_all241' else 'linear'),expected_parameters=expected_parameters)
    source_diffs.append(dict(name=name,max_abs_diffs=diffs,original_npz_available_here=(OLD/suffix).exists(),fresh_npz_sha256=sha(FRESH/f'sensitivity_{name}.npz'),source_identity='Pro hash agrees with old manifest; numerics independently corroborated by previous local fresh PDE run'))

repro=OUT/'reproduced'
csv_diffs=[]
for p in sorted((NEW/'data').glob('*.csv')):
    q=repro/'data'/p.name
    equal=p.read_bytes()==q.read_bytes()
    text_equal=p.read_text(encoding='utf-8')==q.read_text(encoding='utf-8')
    aa=list(csv.reader(p.read_text(encoding='utf-8').splitlines()))
    bb=list(csv.reader(q.read_text(encoding='utf-8').splitlines()))
    valid=len(aa)==len(bb); ndiff=0; maxdiff=0.0
    for ar,br in zip(aa,bb):
        valid &= len(ar)==len(br)
        for av,bv in zip(ar,br):
            if av==bv: continue
            try:
                af=float(av); bf=float(bv)
                delta=abs(af-bf); maxdiff=max(maxdiff,delta); ndiff+=1
                valid &= math.isclose(af,bf,rel_tol=2e-14,abs_tol=1e-14)
            except ValueError:
                valid=False
    record('reproduced_csv_semantic_'+p.name,valid,byte_identical=equal,newline_normalized_text_identical=text_equal,numeric_different_cells=ndiff,max_abs_numeric_diff=maxdiff)
    csv_diffs.append(dict(path=p.name,byte_identical=equal,newline_normalized_text_identical=text_equal,numeric_different_cells=ndiff,max_abs_numeric_diff=maxdiff))
for p in sorted((NEW/'data').glob('*.npz')):
    aa=arrays(p); bb=arrays(repro/'data'/p.name)
    record('reproduced_npz_keys_'+p.name,aa.keys()==bb.keys())
    for k in aa:
        tolerance=1e-21 if k=='D' else 2e-14 if k=='D_over_D0' else 0.0
        compare('reproduced_npz_array_'+k,aa[k],bb[k],tolerance)
rj=read_json(repro/'data/mechanism_validation.json')
cj=dict(claim); cj.pop('runtime'); rj.pop('runtime')
report_diffs=[]
def compare_report(a,b,p=''):
    if isinstance(a,dict):
        return a.keys()==b.keys() and all(compare_report(a[k],b[k],p+'/'+k) for k in a)
    if isinstance(a,list):
        return len(a)==len(b) and all(compare_report(x,y,p+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b)))
    if a==b:
        return True
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        report_diffs.append(dict(path=p,pro_value=a,local_value=b,max_abs_diff=abs(a-b)))
        return math.isclose(a,b,rel_tol=2e-14,abs_tol=1e-14)
    report_diffs.append(dict(path=p,pro_value=a,local_value=b))
    return False
report_match=compare_report(cj,rj)
record('reproduced_report_except_runtime',report_match,exact_match=cj==rj,numeric_differences=report_diffs)
figure_paths=[]
for p in sorted((NEW/'figures').iterdir()):
    if p.suffix in ('.png','.svg'):
        q=repro/'figures'/p.name
        valid=q.exists() and q.stat().st_size>1000
        record('figure_regenerated_'+p.name,valid)
        figure_paths.append(dict(path=p.name,bytes=q.stat().st_size if q.exists() else 0,sha256=sha(q) if q.exists() else None))

# The environmental file is checked against the original XLSX by Pro's actual
# rerun, with exact interpolation assertion. Independently integrate CSV here.
env=np.genfromtxt(NEW/'data/environment_original.csv',delimiter=',',skip_header=1)
tail=env[env[:,0]>=10800]
tail_mean=np.trapezoid(tail[:,1:],tail[:,0],axis=0)/(tail[-1,0]-tail[0,0])
compare('tail_time_mean',claim['time_scope']['tail_time_mean_linear_3to4h'],tail_mean)
compare('tail_sample_mean',claim['time_scope']['tail_sample_mean_3to4h'],tail[:,1:].mean(axis=0))
compare('tail_final_value',claim['time_scope']['last_environment_value'],tail[-1,1:])
rho_d0=(650+128*2.55)/(1+2.55)
rho_d=(650+128*C[-1])/(1+C[-1])
compare('density_diagnostic',claim['density_diagnostic']['implied_rho_d_3h_0_1_2cm'],rho_d)
V=np.pi*.02**2*.25
lost=rho_d0*V*(2.55-raw['average_moisture_dry_basis'][-1])
old_validation=read_json(OLD/'output/validation/validation.json')
Q=old_validation['balance']['net_heat_input_J_m3']*V
compare('conditional_lost_water',claim['density_diagnostic']['conditional_lost_water_kg_reference_dry_density'],lost)
compare('conditional_heat_input',claim['density_diagnostic']['reused_effective_heat_input_J'],Q)
compare('conditional_latent_scale',claim['density_diagnostic']['latent_equal_effective_heat_input_at_lambda_J_kg'],Q/lost)
for k,value in dict(radial_T_span_K=np.ptp(raw['temperature_degC'][-1]),max_T_lag_to_current_air_K=np.max(np.abs(raw['temperature_degC'][-1]-raw['environment'][-1,0])),radial_C_span_kgkg=np.ptp(raw['moisture_dry_basis'][-1]),remaining_effective_water_fraction=raw['average_moisture_dry_basis'][-1]/2.55).items():
    compare('full_radius_claim_'+k,claim['response_3h'][k],value)
q=8e-7*(C[:,2]-raw['environment'][:,1]); elas=-raw['environment'][:,1]/(C[:,2]-raw['environment'][:,1])
expected_flux=np.column_stack((t,C[:,2],raw['environment'][:,1],C[:,2]-raw['environment'][:,1],q,elas))
compare('boundary_fixed_state_diagnostic',np.genfromtxt(NEW/'data/boundary_identifiability_diagnostic.csv',delimiter=',',skip_header=1),expected_flux)

report=dict(scope='New postprocessing independently rerun; no full PDE rerun; original accepted result not changed.',runtime=dict(python=sys.version,numpy=np.__version__,platform=platform.platform()),all_checks_passed=all(c['passed'] for c in checks),check_count=len(checks),checks=checks,independent_locations=locations,independent_sensitivity_3h=sens_summary,source_projection_comparisons=source_diffs,reproduced_csvs=csv_diffs,regenerated_figures=figure_paths,notes=['Independent derivative weights solve quartic moment equations, not imported from Pro code.','Original seven full Pro sensitivity NPZ files remain absent locally; their claimed SHA matches old delivery manifest. All projected arrays agree with separate previously reproduced PDE results to recorded tolerance.','Figure bytes may differ because Matplotlib/platform rendering differs; the same figure source actually regenerates 20 nonempty artifacts from verified identical input arrays.','Three-hour numerical baseline remains accepted. Hypothetical true density, latent scale and fixed-state boundary sensitivity are diagnostics, not calibrated physical predictions.','Pointwise derivative sign criterion is diagnostic, not rigorous derivative error certification; 60 s contributions and half-hour declines independently verified.'])
(OUT/'numeric_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
failed=[c for c in checks if not c['passed']]
print(json.dumps(dict(all_checks_passed=report['all_checks_passed'],check_count=len(checks),failed=failed,locations=locations,source_projection_comparisons=source_diffs),ensure_ascii=False,indent=2))
sys.exit(0 if report['all_checks_passed'] else 1)
