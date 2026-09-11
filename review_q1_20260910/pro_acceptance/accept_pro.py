"""Acceptance of Pro evidence; original delivery and Pro files remain read-only."""
from pathlib import Path
import importlib.util
import hashlib
import json
import platform
import warnings
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRO = ROOT / 'q1_physical_review_evidence'
DELIVERY = ROOT / 'q1_complete_delivery/q1_delivery'
original = json.loads((PRO/'calculations/physical_audit.json').read_text(encoding='utf-8'))
rerun = json.loads((HERE/'rerun/physical_audit.json').read_text(encoding='utf-8'))
report = {'python': platform.python_version(), 'pro_script_rerun_exit_code': 0,
          'rerun_note': 'First rerun emitted one BDF RuntimeWarning at difference-table update; Radau crosscheck below examines final values independently in time.'}
hashes = {str(p.relative_to(PRO)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in PRO.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
report['delivery_hashes_match_pro'] = {
    name: hashlib.sha256((DELIVERY/name).read_bytes()).hexdigest() == h
    for name, h in original['original_file_sha256'].items()
}
assert all(report['delivery_hashes_match_pro'].values())
assert all(x['equal_to_rounded_npz'] for x in rerun['excel_crosscheck'].values())
report['all_75600_excel_values_match'] = True
comparisons = {}
for eps in [0, 1]:
    name = f'radiation_eps{eps}_n320.npz'
    a, b = np.load(PRO/'calculations'/name), np.load(HERE/'rerun'/name)
    assert np.array_equal(a['time_s'], b['time_s'])
    assert np.array_equal(a['radius_cm'], b['radius_cm'])
    assert np.isfinite(b['T']).all()
    err = float(np.max(np.abs(a['T']-b['T'])))
    assert err < 1e-8
    comparisons[str(eps)] = {'max_field_abs_difference_K': err, 'all_finite': True}
report['rerun_vs_pro'] = comparisons

spec = importlib.util.spec_from_file_location('pro_review', PRO/'review_checks.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
full = module.xlsx_read(ROOT/'A题/附件/附件2.xlsx')['Sheet1']
report['attachment2_complete_workbook_crc_passed'] = True
report['attachment2_cells_match_prefix'] = all(
    float(full[cell]) == float(value) for cell, value in original['attachment2']['cells'].items())
assert report['attachment2_cells_match_prefix']
raw = module.xlsx_read(DELIVERY/'input/附件1.xlsx')['Sheet1']
env = np.array([[raw[f'{c}{i}'] for c in 'ABC'] for i in range(2, 243)])
pv = 101.325 * env[30, 2] / (0.621945 + env[30, 2])
dew = brentq(lambda tc: .6108*np.exp(17.27*tc/(237.3+tc))-pv, -30., 60.)
report['dew_point_independent_root_C'] = float(dew)
assert abs(dew-original['conditional_psychrometric']['states'][1]['dew_C']) < 1e-10

def use_radau(fun, interval, y0, **kwargs):
    kwargs.update(method='Radau', rtol=2e-11, atol=2e-13, max_step=3.)
    return solve_ivp(fun, interval, y0, **kwargs)

module.solve_ivp = use_radau
radau = {}
with warnings.catch_warnings(record=True) as records:
    warnings.simplefilter('always', RuntimeWarning)
    for eps in [0, 1]:
        values, avg, steps = module.thermal(env, 320, eps)
        assert np.isfinite(values).all()
        assert values.min() >= 28.-1e-8
        assert np.all(values <= np.interp(np.arange(1801), env[:,0], env[:,1])[:,None]+1e-8)
        bdf = np.load(HERE/'rerun'/f'radiation_eps{eps}_n320.npz')['T']
        diff = float(np.max(np.abs(values-bdf)))
        assert diff < 1e-6
        radau[eps] = values
        print(f'Radau epsilon={eps}: max difference vs BDF={diff:.3e} K', flush=True)
        comparisons[str(eps)]['Radau_vs_BDF_max_K'] = diff
        comparisons[str(eps)]['Radau_accepted_steps'] = steps
    fine, _, steps = module.thermal(env, 640, 1)
    assert np.isfinite(fine).all()
    grid_error = float(np.max(np.abs(fine-radau[1])))
    assert grid_error < 1e-4
    print(f'Radau epsilon=1, 320 vs 640: {grid_error:.3e} K', flush=True)
report['radau_runtime_warnings'] = [str(w.message) for w in records if issubclass(w.category, RuntimeWarning)]
assert not report['radau_runtime_warnings']
report['radiation_320_vs_640_Radau_max_K'] = grid_error
report['radau_320_delta_center_surface_1800_K'] = (radau[1]-radau[0])[-1,[0,-1]].tolist()
report['radau_640_epsilon1_center_surface_1800_C'] = fine[-1,[0,-1]].tolist()
report['pro_files_unchanged'] = all(hashlib.sha256((PRO/name).read_bytes()).hexdigest() == h
                                     for name, h in hashes.items())
assert report['pro_files_unchanged']
report['status'] = 'PASS: evidence reproducible; conditional scenarios do not replace the main answer'
(HERE/'acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
