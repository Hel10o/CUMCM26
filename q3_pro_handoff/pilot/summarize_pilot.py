"""Summarize existing pilot outputs; does not rerun any PDE."""
from pathlib import Path
import csv, hashlib, json, platform
import numpy as np
import scipy

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
cases=[json.loads((HERE/f'{kind}_n{n}.json').read_text(encoding='utf-8'))
       for kind in ['harmonic','kirchhoff'] for n in [128,256,512]]
lookup={(r['method'],r['n']):r for r in cases}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lookup['kirchhoff',512]
scenarios=[lookup['kirchhoff',256]]+[json.loads((HERE/f'kirchhoff_{s}_n256.json').read_text(encoding='utf-8'))
          for s in ['last_hour_mean','nominal_50_005']]
hist=np.genfromtxt(HERE/'kirchhoff_n256_trajectory.csv',delimiter=',',skip_header=1)[:3]
shared_history={s:bool(np.array_equal(hist,np.genfromtxt(HERE/f'kirchhoff_{s}_n256_trajectory.csv',delimiter=',',skip_header=1)[:3]))
               for s in ['last_hour_mean','nominal_50_005']}
with (HERE/'continuation_comparison.csv').open('w',newline='',encoding='utf-8') as fh:
    wr=csv.writer(fh);wr.writerow(['continuation','n','held_T_degC','held_C_kgkg','event_time_s','event_time_h','difference_vs_last_s','elapsed_wall_s'])
    for r in scenarios:
        held=r.get('held_environment_T_C_kgkg',r['last_environment'][1:])
        wr.writerow([r.get('continuation','hold_last'),r['n'],*held,r['event_time_s'],r['event_time_h'],
                     r['event_time_s']-lookup['kirchhoff',256]['event_time_s'],r['elapsed_wall_s']])
event_C_error_for_fourdecimal_h=abs(ref['event_C_center_slope_per_s'])*.00005*3600
with (HERE/'grid_comparison.csv').open('w',newline='',encoding='utf-8') as fh:
    w=csv.writer(fh)
    w.writerow(['method','n','dr_m','event_time_s','event_time_h','event_C_surface',
                'event_C_center_slope_per_s','min_D_accepted','elapsed_wall_s'])
    for r in cases:w.writerow([r[k] for k in ['method','n','dr_m','event_time_s','event_time_h',
               'event_C_surface','event_C_center_slope_per_s','min_D_accepted','elapsed_wall_s']])

summary={
 'scope':'Executed bounded Q3 reconnaissance only. No formal result3.xlsx or final four-decimal answer.',
 'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
 'delivered_code_sha256':{'run_pilot.py':sha(HERE/'run_pilot.py'),'summarize_pilot.py':sha(HERE/'summarize_pilot.py')},
 'input_and_reused_source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [
     ROOT/'q2_final_delivery/inputs/附件1.xlsx',ROOT/'q2_final_delivery/source/q2_core.py',
     ROOT/'q2_final_delivery/source/q2_spectral.py']},
 'six_cases_actually_executed_successfully':all(r['status']=='event_found' for r in cases),
 'additional_two_continuation_cases_successful':all(r['status']=='event_found' for r in scenarios[1:]),
 'additional_continuation_cases_total_wall_s':sum(r['elapsed_wall_s'] for r in scenarios[1:]),
 'continuation_saved_five_C_samples_at_0_3_4h_bitwise_equal':shared_history,
 'shared_history_verification_scope':'CSV values only: five C samples at r=0,0.5,1,1.5,2 cm at t=0,3,4 h; not all internal T/C states.',
 'last_hour_mean_definition':'arithmetic mean of all 61 records from t=10800 through t=14400 seconds inclusive; switched just after 4h',
 'all_cases_minimum_accepted_C_positive':all(r['min_C_accepted']>0 for r in cases),
 'total_case_wall_s_excludes_probe_and_first_n128_diagnostic_rerun':sum(r['elapsed_wall_s'] for r in cases),
 'boundary_after_4h':{'assumption':'last measured value held constant','T_degC':50.165,'C_kgkg':.04986},
 'integrated_flux_256_to_512_event_change_s':ref['event_time_s']-lookup['kirchhoff',256]['event_time_s'],
 'harmonic_256_to_512_event_change_s':lookup['harmonic',512]['event_time_s']-lookup['harmonic',256]['event_time_s'],
 'harmonic_minus_integrated_n512_event_s':lookup['harmonic',512]['event_time_s']-ref['event_time_s'],
 'illustrative_error_budget':{
     'event_slope_C_per_s':ref['event_C_center_slope_per_s'],
     'half_0.0001_h_in_s':.18,
     'approx_max_abs_C_error_for_0.18s_event_error':event_C_error_for_fourdecimal_h,
     'qualification':'linearized illustration, not achieved total error bound; report time precision from demonstrated evidence'},
 'harmonic_n128_local_increase_under_constant_boundary':lookup['harmonic',128]['max_temporal_increase_location'],
 'no_failures_encountered':True,
 'limitations':[
  'Three explicit continuation scenarios studied; external moisture basis remains the inherited effective-model assumption. Scenarios are not probability confidence intervals.',
  'No separate time-tolerance/max-step convergence study; no independent spatial discretization verification of the long-time endpoint.',
  'Kirchhoff and harmonic variants share thermal operator, surface half-volume, time integrator and imported material functions.',
  'C maximum is checked over all numerical nodes/accepted states, not a mathematical continuum maximum proof.',
  'Finite grid convergence evidence does not establish four-decimal final sampling stability.',
  'No 60-second full result3 export or template fill, no 2D long-time check, no shrinkage/latent-heat model.',
  'Only two extra continuations, both at n256; no exhaustive environmental extrapolation or interpolation study.',
  'The additional max_temporal_increase_location diagnostic was added after initial six runs; only harmonic n128 was rerun to locate its anomaly. Numeric formulas/settings were unchanged.'
 ],
 'reproduction_commands':['python -X utf8 -B q3_pro_handoff/pilot/run_pilot.py --case probes']+
    [f'python -X utf8 -B q3_pro_handoff/pilot/run_pilot.py --case {kind} --n {n}' for kind in ['harmonic','kirchhoff'] for n in [128,256,512]]+
    [f'python -X utf8 -B q3_pro_handoff/pilot/run_pilot.py --case kirchhoff --n 256 --continuation {s}' for s in ['last_hour_mean','nominal_50_005']]+
    ['python -X utf8 -B q3_pro_handoff/pilot/summarize_pilot.py']}
(HERE/'pilot_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
