"""Isolated audit of BDF unused workspace; leaves the delivery and SciPy untouched."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import warnings
from dataclasses import replace
import numpy as np
from scipy.integrate._ivp.bdf import BDF

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'q2_final_delivery' / 'source'))
import q2_core as core

original_solve_ivp = core.solve_ivp
mode = 'natural'
events = []
initial_workspaces = []


class ProbeBDF(BDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if mode == 'zero_unused':
            self.D[2:] = 0
        elif mode == 'inject_snan_unused':
            # Diagnostic injection only: a signaling NaN in initially unused rows.
            self.D[2:].view(np.uint64)[:] = np.uint64(0x7ff0000000000001)
        initial_workspaces.append({
            'mode': mode,
            'D2_nonfinite': int(np.count_nonzero(~np.isfinite(self.D[2]))),
            'D2_first_bits_hex': hex(int(self.D[2].view(np.uint64)[0])),
        })
        self.audit_step = 0

    def _step_impl(self):
        self.audit_step += 1
        before = {
            'step': self.audit_step, 't': float(self.t), 'order': self.order,
            'n_equal_steps': self.n_equal_steps,
            'active_rows_finite': bool(np.isfinite(self.D[:self.order+1]).all()),
            'D_order_plus_1_nonfinite': int(np.count_nonzero(~np.isfinite(self.D[self.order+1]))),
        }
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', RuntimeWarning)
            result = super()._step_impl()
        if caught:
            events.append({
                'mode': mode, 'before': before,
                'warnings': [{'message': str(w.message), 'line': w.lineno, 'file': w.filename} for w in caught],
                'after': {'t': float(self.t), 'order': self.order,
                    'n_equal_steps': self.n_equal_steps,
                    'state_finite': bool(np.isfinite(self.y).all()),
                    'active_rows_finite': bool(np.isfinite(self.D[:self.order+1]).all()),
                    'D2_finite': bool(np.isfinite(self.D[2]).all()),
                    'D3_finite': bool(np.isfinite(self.D[3]).all())},
            })
        return result


def solve_ivp_with_probe(*args, **kwargs):
    if kwargs.get('method') == 'BDF':
        kwargs['method'] = ProbeBDF
    return original_solve_ivp(*args, **kwargs)


core.solve_ivp = solve_ivp_with_probe
constant = core.Environment(np.array([[0, 28, 2.55], [10800, 28, 2.55]], float))
closedp = replace(core.P, hT=0, hm=0)


def initial(r):
    return np.column_stack([np.full(r.size, 35.), 2 + .4*np.cos(np.pi*(r/core.P.R)**2)])


def run_case(case):
    if case == 'uniform_no_drive':
        return core.solve_fv(constant, n=80, end=600, quadrature=True)
    return core.solve_fv(constant, n=160, p=closedp, end=600, initial=initial, quadrature=True)


report = {'scipy_version': __import__('scipy').__version__, 'cases': {},
    'note': 'Signaling-NaN runs intentionally inject only initially unused BDF workspace. They demonstrate the source-level mechanism and are not evidence that a naturally emitted warning contained the same bit pattern.'}
for case in ['uniform_no_drive', 'closed_redistribution']:
    results = {}
    runs = []
    for current_mode in ['natural', 'zero_unused', 'inject_snan_unused']:
        mode = current_mode
        events.clear()
        initial_workspaces.clear()
        result = run_case(case)
        results[mode] = result
        runs.append({'mode': mode, 'initial_workspaces': list(initial_workspaces),
            'warning_events': list(events),
            'accepted_steps': result['stats']['accepted_steps'],
            'temperature_all_finite': bool(np.isfinite(result['temperature_degC']).all()),
            'moisture_all_finite': bool(np.isfinite(result['moisture_dry_basis']).all()),
            'heat_balance_abs_J_m3': result['stats']['effective_heat_balance_max_J_m3'],
            'water_balance_abs_kgkg': result['stats']['water_balance_max_kgkg']})
    checks = {}
    for compare in ['natural', 'inject_snan_unused']:
        checks[compare+'_versus_zero_unused'] = {
            key+'_max_abs': float(np.max(np.abs(results[compare][key] - results['zero_unused'][key])))
            for key in ['temperature_degC', 'moisture_dry_basis', 'balance_records']}
    report['cases'][case] = {'runs': runs, 'comparisons': checks}
report['passed'] = all(
    max(c.values()) == 0
    for case in report['cases'].values() for c in case['comparisons'].values())
destination = Path(__file__).with_suffix('.json')
destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
assert report['passed']
