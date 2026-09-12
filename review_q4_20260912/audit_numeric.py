"""Targeted local Q4 audit. Frozen delivery is never modified; no full PDE rerun."""
from pathlib import Path
import ast
import hashlib
import json
import math
import platform
import sys
import numpy as np
import scipy
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'q4_complete_delivery/v1'
OUT = Path(__file__).resolve().parent / 'numeric'
sys.path.insert(0, str(BASE / 'source'))
from geometry_solver import GeometryFV, Inputs


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    z = np.load(BASE / 'output/main.npz')
    m = read(BASE / 'output/main.json')
    final = read(BASE / 'output/end_event.json')
    sources = list(BASE.rglob('*.py'))
    for path in sources:
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    report = {'scope': 'Frozen-array arithmetic and a new uniform-shrinkage ODE; no new full Q1-Q4 PDE solution.',
              'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
              'python_sources_parsed': len(sources), 'checks': {}}
    checks = report['checks']
    times = z['time_s']
    assert len(times) == 3067 and times[0] == 0 and np.all(np.diff(times) > 0)
    assert np.array_equal(times[:-1], np.arange(0, 183901, 60))
    assert times[-1] == final['execution_s']
    assert np.isfinite(z['full_TC']).all()
    assert np.all(z['full_TC'][:, :, 1] > 0)
    root = m['event']['critical_s']
    differences = {}
    for label in ['spectral80', 'spectral160', 'time120_bdf']:
        q = np.load(BASE / 'validation' / (label + '.npz'))
        d = read(BASE / 'validation' / (label + '.json'))
        common, a, b = np.intersect1d(times, q['time_s'], return_indices=True)
        err = z['sample_TC'][a] - q['sample_TC'][b]
        differences[label] = {'common_times': len(common), 'max_abs_T': float(np.nanmax(abs(err[:, :, 0]))),
                              'max_abs_C': float(np.nanmax(abs(err[:, :, 1]))), 'root_difference_s': d['event']['critical_s'] - root}
    checks['saved_space_time_comparison'] = differences
    assert max(v['max_abs_C'] for v in differences.values()) < 1e-8
    e = int(np.argmin(abs(z['event_time_s'] - final['execution_s'])))
    actual_max = float(z['event_full_TC'][e, :, 1].max())
    assert actual_max < .15 and actual_max == final['execution_max_C']
    assert np.array_equal(z['event_full_TC'][e], z['full_TC'][-1])
    pre = int(np.argmin(abs(z['event_time_s'] - (root - 1))))
    post = int(np.argmin(abs(z['event_time_s'] - (root + 1))))
    assert z['event_full_TC'][pre, :, 1].max() > .15 > z['event_full_TC'][post, :, 1].max()
    checks['event'] = {'critical_s': root, 'execution_s': times[-1], 'execution_max_C': actual_max,
                       'stored_event_and_last_state_identical': True, 'threshold_margin_C': .15 - actual_max,
                       'scope': 'Maximum of stored 1D nodes; continuous-polynomial and 2D scope reviewed separately.'}
    budget = math.ceil(2000 * max(final['discrepancies'].values())) / 1000
    assert budget == final['empirical_budget_s']
    assert .36 * math.ceil((root + budget) / .36) == final['execution_s']
    checks['execution_rounding'] = {'empirical_budget_s': budget, 'rigorous_bound': False}
    bal = z['balance']
    residual = float(np.max(abs(bal[:, 1] + bal[:, 2] - 2.55)))
    assert residual < 1e-10
    checks['saved_mass_ledger_arithmetic'] = {'max_abs_mean_C_residual': residual,
             'scope': 'Recomputes saved mean plus saved cumulative flux, not a new independent boundary integral.'}
    pair = {}
    for case, one, two in [('q4', 'q4_80x0_integral', 'q4_80x128_integral'),
                           ('q3', 'q23_80x0_integral', 'q23_80x256_integral')]:
        a = read(BASE / 'validation/geometry' / (one + '.json'))
        b = read(BASE / 'validation/geometry' / (two + '.json'))
        pair[case] = {'one_dimensional_grid_root_s': a['event_root_s'], 'two_dimensional_grid_root_s': b['event_root_s'],
                      'paired_shift_s': b['event_root_s'] - a['event_root_s']}
    checks['paired_geometry_arithmetic'] = pair
    fixed = read(BASE / 'validation/fixed80.json')['event']['critical_s']
    pchip = read(BASE / 'validation/pchip80.json')['event']['critical_s']
    checks['sensitivity_arithmetic'] = {'same_appendix_fixed_R_root_h': fixed / 3600,
             'shrinkage_reduction_percent': 100 * (fixed - root) / fixed,
             'pchip_minus_linear_s': pchip - root}
    # Second implementation of the uniform-state test: finite volumes, instead
    # of the delivered spectral pure-shrinkage script. No production data writes.
    inp = Inputs(BASE / 'inputs')
    op = GeometryFV(12, 0, 'q4', inp)
    y0 = np.tile([28., 2.55], op.m)
    same_environment = lambda t: np.array([28., 2.55])
    sol = solve_ivp(lambda t, y: op.rhs(t, y, same_environment), (0., 259200.), y0,
                    method='Radau', jac=lambda t, y: op.rhs(t, y, same_environment, True),
                    t_eval=np.arange(0., 259201., 600.), rtol=1e-10, atol=1e-12, max_step=600.)
    assert sol.success
    state = sol.y.T.reshape(-1, op.m, 2)
    radii = np.array([inp.radius(t) for t in sol.t])
    rho_d = (.02 / radii) ** 2
    dry = rho_d * np.pi * radii ** 2 * .25
    departure = np.max(abs(state - np.array([28., 2.55])), axis=(0, 1))
    assert np.max(departure) < 1e-10 and np.max(abs(dry / dry[0] - 1)) < 1e-12
    checks['new_uniform_shrinkage_fv_ode'] = {'duration_s': 259200, 'outputs': len(sol.t),
             'max_abs_T_C_departure': departure.tolist(), 'nfev': sol.nfev,
             'max_relative_dry_mass_change': float(np.max(abs(dry / dry[0] - 1))),
             'scope': 'Zero exchange in a uniform state only; does not validate general drying energy closure.'}
    report['source_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sources + [Path(__file__).resolve()]}
    report['pass'] = True
    (OUT / 'numeric_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
