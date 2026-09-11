"""Read-only numerical and paper-table evidence comparison for Q2 audit."""
from pathlib import Path
import json, re
import numpy as np
from independent_radial import comparison

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORIGINAL=ROOT/'q2_final_delivery'/'output'
FRESH=ROOT/'review_q2_20260911'/'reproduced'/'validation'
KEYS=('temperature_degC','moisture_dry_basis')
TABLE_TIMES=np.arange(1800,10801,1800)
RADII=np.arange(21)/10


def load(path):
    with np.load(path) as z:return {key:z[key] for key in KEYS}


def compare(a,b):
    return {key:comparison(a[key][1:],b[key][1:],np.arange(1,len(a[key])),RADII) for key in KEYS}


def main():
    delivery=load(ORIGINAL/'q2_unrounded.npz')
    radial=load(HERE/'direct_r_n96_t10800.npz')
    report={'independence':'New direct-r collocation, expanded PDE, Radau and new input parser; no Pro numerical RHS imported.',
            'new_reference_vs_original_delivery':compare(delivery,radial),
            'paper_tables':{},'raw_60_values_vs_reference':{},'independent_startup_convergence':{}}
    paper=(ORIGINAL/'第二问论文正文.md').read_text(encoding='utf-8')
    for number,key,name in [(3,KEYS[0],'temperature'),(4,KEYS[1],'moisture')]:
        text=paper.split(f'### 表{number}',1)[1]
        rows=[]
        for line in text.splitlines():
            if re.match(r'^\|\s*[0-9]+\.[0-9]+\s*\|',line):
                fields=[float(v.strip()) for v in line.strip().strip('|').split('|')]
                if len(fields)==6:rows.append(fields)
                if len(rows)==6:break
        table=np.array(rows)
        csv=np.loadtxt(ORIGINAL/f'table_{name}.csv',delimiter=',',skiprows=1)
        assert table.shape==(6,6) and np.array_equal(table,csv)
        assert np.array_equal(table[:,0]*3600,TABLE_TIMES)
        report['paper_tables'][key]=comparison(table[:,1:],radial[key][TABLE_TIMES][:,::5],TABLE_TIMES,RADII[::5])
        report['paper_tables'][key]['paper_equals_csv']=True
        report['paper_tables'][key]['max_abs_difference_meaning']='Four-decimal displayed table versus unrounded reference; includes ordinary rounding error, not a solver error estimate.'
        report['raw_60_values_vs_reference'][key]=comparison(delivery[key][TABLE_TIMES][:,::5],radial[key][TABLE_TIMES][:,::5],TABLE_TIMES,RADII[::5])
    startup={n:load(HERE/f'direct_r_n{n}_t60.npz') for n in (64,128,160)}
    for coarse,fine in [(64,128),(128,160)]:
        report['independent_startup_convergence'][f'{coarse}_to_{fine}']=compare(startup[coarse],startup[fine])
    report['startup_first_second_surface']={str(n):float(z[KEYS[1]][1,-1]) for n,z in startup.items()}
    report['startup_first_second_surface']['delivery']=float(delivery[KEYS[1]][1,-1])
    report['all_453600_independent_four_decimal_results_equal']=all(
        value['four_decimal_mismatches']==0 for value in report['new_reference_vs_original_delivery'].values())
    report['all_60_paper_values_equal_independent_rounding']=all(
        value['four_decimal_mismatches']==0 for value in report['paper_tables'].values())
    expected=['fv_n640.npz','fv_n1280.npz','fv_n2560.npz','fv_n1280_time_tight.npz','cheb_n128.npz','cheb_n192.npz']
    if all((FRESH/file).exists() for file in expected):
        fv640,fv1280,fv2560,tt,sp128,sp192=[load(FRESH/file) for file in expected]
        richfine={k:(4*fv2560[k]-fv1280[k])/3 for k in KEYS}
        richcoarse={k:(4*fv1280[k]-fv640[k])/3 for k in KEYS}
        report['fresh_parent_arrays_recomputed_metrics']={
            'note':'Parent executed Pro code in a new directory; these metrics are independently recomputed here without importing its audit/finalization code. This section is a reproduction check, not a new numerical method.',
            'original_vs_reconstructed_richardson':compare(delivery,richfine),
            'richardson_to_new_spectral_192':compare(richfine,sp192),
            'richardson_1280_to_2560':compare(richcoarse,richfine),
            'spectral_128_to_192':compare(sp128,sp192),
            'time_at_fixed_fv1280':compare(fv1280,tt),
            'new_independent_direct_r96_to_new_pro_spectral192':compare(radial,sp192),
        }
        report['startup_first_second_surface']['fresh_Pro_spectral192']=float(sp192[KEYS[1]][1,-1])
        report['startup_first_second_surface']['fresh_FV1280']=float(fv1280[KEYS[1]][1,-1])
        report['startup_first_second_surface']['fresh_FV2560']=float(fv2560[KEYS[1]][1,-1])
        report['startup_first_second_surface']['fresh_Richardson']=float(richfine[KEYS[1]][1,-1])
        report['startup160_vs_Pro192']=compare(startup[160],{k:sp192[k][:61] for k in KEYS})
    else:report['fresh_parent_arrays_recomputed_metrics']='Not all requested intermediate arrays present yet.'
    (HERE/'independent_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
