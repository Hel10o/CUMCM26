"""Q2 preflight only: coupled local-state finite volumes, NOT final answers.

rho(C)*cp(C)*T_t = div(k(C)*grad(T)); C_t = div(D(C,T)*grad(C)).
Fixed radial cylinder, linear original environmental input, no latent heat or
shrinkage. Appendix 3 is applied from t=0, not spliced onto a Q1 terminal state.
Temperature storage uses Celsius but D always uses T+273.15 kelvin.

This is a preliminary effective-variable baseline. It does not resolve the
thermodynamic meaning of state-dependent density with fixed geometry, gas/solid
concentration mapping, or latent energy. No existing Q1 code is imported.
"""
from pathlib import Path
import hashlib
import json
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
import warnings

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGED_SOURCE = HERE.parent / 'inputs' / '附件1.xlsx'
SOURCE = PACKAGED_SOURCE if PACKAGED_SOURCE.exists() else ROOT / 'A题' / '附件' / '附件1.xlsx'
R, H_T, H_M = 0.02, 25.0, 8e-7
T_INITIAL, C_INITIAL = 28.0, 2.55
END = 10800
TABLE_SECONDS = np.arange(1800, END + 1, 1800)
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def original_environment():
    """Minimal independent OOXML numeric reader for the original attachment."""
    with zipfile.ZipFile(SOURCE) as archive:
        assert archive.testzip() is None
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheet = workbook.find('m:sheets', NS)[0]
        rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        rels = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        target = next(item.attrib['Target'] for item in rels if item.attrib['Id'] == rid)
        target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        values = {}
        for cell in ET.fromstring(archive.read(target)).findall('.//m:sheetData/m:row/m:c', NS):
            value = cell.find('m:v', NS)
            if value is not None and cell.attrib.get('t', 'n') == 'n':
                values[cell.attrib['r']] = float(value.text)
        data = np.array([[values[f'{col}{row}'] for col in 'ABC'] for row in range(2, 243)])
    assert np.array_equal(data[:, 0], np.arange(0, 14401, 60))
    assert np.isfinite(data).all()
    return data


def properties(c, temperature_c):
    kelvin = temperature_c + 273.15
    if np.any(c <= 0) or np.any(kelvin <= 0) or not np.isfinite(c).all() or not np.isfinite(kelvin).all():
        raise ValueError('Nonpositive/nonfinite trial state; preflight does not clip it.')
    rho = 650 + 128 * c
    cp = 1450 + 2736 * c / (c + 1)
    k = .21 + .38 * c / (c + 1)
    d = 2.4e-3 * np.exp(-.45 / c - 3850 / kelvin)
    return rho, cp, k, d


def parameter_scales():
    cases = [(28, 2.55), (50, 2.55), (50, 1.0), (50, .15), (50, .05), (28, .15), (28, .05)]
    output = []
    for tc, c in cases:
        tk = tc + 273.15
        rho, cp, k, d = properties(np.array(c), np.array(tc))
        alpha = k / (rho * cp)
        log10_ratio = (-3850 / tc + 3850 / tk) / np.log(10)
        output.append({
            'T_C': tc, 'T_K': tk, 'C_dry_basis': c,
            'rho_kg_m3': float(rho), 'cp_J_kgK': float(cp), 'k_W_mK': float(k),
            'rho_cp_J_m3K': float(rho * cp), 'D_m2_s': float(d), 'alpha_m2_s': float(alpha),
            'D_C_m2_s_per_dry_basis': float(d * .45 / c**2),
            'D_T_m2_sK': float(d * 3850 / tk**2),
            'Bi_T_using_R': float(H_T * R / k), 'Bi_C_using_R': float(H_M * R / d),
            'radial_heat_time_s': float(R**2 / alpha), 'radial_moisture_time_s': float(R**2 / d),
            'heat_diffusion_length_at_3h_cm': float(np.sqrt(alpha * END) * 100),
            'moisture_diffusion_length_at_3h_cm': float(np.sqrt(d * END) * 100),
            'D_if_Celsius_misused_over_correct_D': float(10**log10_ratio),
            'log10_wrong_over_correct_D': float(log10_ratio),
        })
    return {
        'scope': 'Representative local states, not measured trajectories or drying-time predictions.',
        'formula_visual_check': 'Original problem PDF page 4 image inspected; appendix 3 formulas and kelvin unit confirmed.',
        'derivatives': {'D_C': '(0.45/C^2)*D > 0 at C>0', 'D_T': '(3850/T_K^2)*D > 0 at T_K>0'},
        'interpretation': 'At fixed temperature, drying reduces D; at fixed C, heating increases D. Their combined trajectory is not assumed monotone.',
        'cases': output,
    }


def run_grid(data, n):
    started = time.perf_counter()
    dr = R / n
    radius = np.linspace(0, R, n + 1)
    edges = np.r_[0, (radius[:-1] + radius[1:]) / 2, R]
    weights = (edges[1:]**2 - edges[:-1]**2) / 2
    averages = 2 * weights / R**2
    # Interleave temperature and moisture at each vertex, then add accumulated
    # outward mean-moisture flux for an integrated discrete balance check.
    size = 2 * (n + 1) + 1
    pattern = lil_matrix((size, size), dtype=np.int8)
    for i in range(n + 1):
        for j in range(max(0, i-1), min(n, i+1) + 1):
            pattern[2*i:2*i+2, 2*j:2*j+2] = 1
    pattern[-1, 2*n+1] = 1
    pattern[-1, -1] = 1
    pattern = pattern.tocsr()

    def rhs(t, y):
        state = y[:-1].reshape(n + 1, 2)
        temp, c = state[:, 0], state[:, 1]
        rho, cp, k, d = properties(c, temp)
        ambient_t = np.interp(t, data[:, 0], data[:, 1])
        ambient_c = np.interp(t, data[:, 0], data[:, 2])
        k_face = 2 * k[:-1] * k[1:] / (k[:-1] + k[1:])
        d_face = 2 * d[:-1] * d[1:] / (d[:-1] + d[1:])
        flux_t = np.r_[0., edges[1:-1] * k_face * (temp[:-1] - temp[1:]) / dr,
                        R * H_T * (temp[-1] - ambient_t)]
        flux_c = np.r_[0., edges[1:-1] * d_face * (c[:-1] - c[1:]) / dr,
                        R * H_M * (c[-1] - ambient_c)]
        out = np.empty_like(y)
        out[:-1:2] = (flux_t[:-1] - flux_t[1:]) / (weights * rho * cp)
        out[1:-1:2] = (flux_c[:-1] - flux_c[1:]) / weights
        out[-1] = 2 * H_M / R * (c[-1] - ambient_c)
        return out

    y = np.r_[np.tile([T_INITIAL, C_INITIAL], n + 1), 0.]
    full_output = np.empty((END + 1, 21, 2))
    full_output[0] = [T_INITIAL, C_INITIAL]
    avg_c = np.empty(END + 1)
    avg_t = np.empty(END + 1)
    integrated_loss = np.empty(END + 1)
    avg_c[0], avg_t[0], integrated_loss[0] = C_INITIAL, T_INITIAL, 0.
    snapshot = {}
    accumulated = {'nfev': 0, 'njev': 0, 'nlu': 0, 'accepted_steps': 0}
    trial_warnings = []
    for start in range(0, END, 60):
        stop = start + 60
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            sol = solve_ivp(rhs, (start, stop), y, method='BDF', jac_sparsity=pattern,
                            rtol=1e-9, atol=1e-11, max_step=15., dense_output=True,
                            first_step=1e-3)
        trial_warnings.extend(str(item.message) for item in captured)
        if not sol.success:
            raise RuntimeError(f'N={n}, segment {start}-{stop}: {sol.message}')
        eval_times = np.arange(start + 1, stop + 1)
        yy = sol.sol(eval_times)
        fields = yy[:-1].T.reshape(60, n + 1, 2)
        assert np.isfinite(yy).all()
        full_output[eval_times] = fields[:, ::n//20]
        avg_t[eval_times] = fields[:, :, 0] @ averages
        avg_c[eval_times] = fields[:, :, 1] @ averages
        integrated_loss[eval_times] = yy[-1]
        y = sol.y[:, -1]
        if stop in TABLE_SECONDS:
            snapshot[str(stop)] = y[:-1].reshape(n+1, 2).copy()
        for name in ('nfev', 'njev', 'nlu'):
            accumulated[name] += int(getattr(sol, name))
        accumulated['accepted_steps'] += len(sol.t) - 1

    ending = full_output[-1]
    output_min = full_output.min(axis=(0,1))
    output_max = full_output.max(axis=(0,1))
    balance = np.max(np.abs(avg_c - C_INITIAL + integrated_loss))
    table = full_output[TABLE_SECONDS][:, ::5]
    result = {
        'status': 'PREFLIGHT_ONLY_NOT_FROZEN_ANSWER',
        'n_intervals': n, 'n_vertices': n+1, 'dr_m': dr,
        'method': 'Monolithic coupled MOL, vertex finite volumes, BDF with sparse finite-difference Jacobian pattern',
        'local_updates': 'rho(C), cp(C), k(C), D(C,T_K); harmonic face k and D; nodal heat capacity remains outside divergence.',
        'rtol': 1e-9, 'atol': 1e-11, 'max_step_s': 15, 'restart_interval_s': 60,
        'first_step_each_segment_s': 1e-3,
        'output_shape': list(full_output.shape),
        'time_s_1800_center_surface_T_C': full_output[1800, [0, -1]].tolist(),
        'time_s_10800_center_surface_T_C': ending[[0, -1]].tolist(),
        'mean_T_C_1800': [float(avg_t[1800]), float(avg_c[1800])],
        'mean_T_C_10800': [float(avg_t[-1]), float(avg_c[-1])],
        'sampled_min_T_C': output_min.tolist(), 'sampled_max_T_C': output_max.tolist(),
        'integrated_discrete_mean_moisture_balance_max_abs': float(balance),
        'balance_scope': 'Augmented integral of the same discrete boundary flux; consistency check, not independent model validation.',
        'table': {'time_s': TABLE_SECONDS.tolist(), 'radius_cm': [0, .5, 1, 1.5, 2],
                  'temperature_C': table[:, :, 0].tolist(), 'moisture_dry_basis': table[:, :, 1].tolist()},
        'warnings': sorted(set(trial_warnings)),
        'runtime_s': time.perf_counter() - started,
        **accumulated,
    }
    return full_output, avg_t, avg_c, result


def compare_grids(coarse, fine):
    delta = np.abs(coarse - fine)
    out = {'scope': 'Every integer second 1..10800 and 21 requested radii; not all internal vertices or a rigorous continuous-domain bound.'}
    for idx, field in enumerate(('temperature_C', 'moisture_dry_basis')):
        d = delta[1:, :, idx]
        at = np.unravel_index(d.argmax(), d.shape)
        out[field] = {'max_abs': float(d[at]), 'rms': float(np.sqrt(np.mean(d*d))),
                      'max_at_time_s_radius_cm': [int(at[0]+1), float(at[1]/10)],
                      'table_max_abs': float(delta[TABLE_SECONDS][:, ::5, idx].max())}
    return out


def main():
    overall_started = time.perf_counter()
    data = original_environment()
    scales = parameter_scales()
    (HERE / 'parameter_scales.json').write_text(json.dumps(scales, ensure_ascii=False, indent=2), encoding='utf-8')
    report = {
        'status': 'PRELIMINARY_NUMERICAL_SCALE_AND_IMPLEMENTATION_CHECK_ONLY',
        'do_not_use_as': ['final four-decimal answers', 'replacement of Q1', 'validated physical truth', 'Q3 drying duration'],
        'contract': __doc__,
        'original_input_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'input_rows': int(len(data)), 'input_range_s': data[[0,-1],0].tolist(),
        'environment_1800': data[data[:,0] == 1800][0].tolist(),
        'environment_10800': data[data[:,0] == 10800][0].tolist(),
        'runtime': {'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__},
        'grids': {}, 'grid_comparisons': {},
    }
    previous = None
    for n in (80, 160, 320):
        output, avg_t, avg_c, details = run_grid(data, n)
        report['grids'][str(n)] = details
        if previous is not None:
            report['grid_comparisons'][f'{n//2}_to_{n}'] = compare_grids(previous, output)
        print(json.dumps({'grid': n, 'seconds': details['runtime_s'],
                          'at_1800': details['time_s_1800_center_surface_T_C'],
                          'at_10800': details['time_s_10800_center_surface_T_C'],
                          'warnings': details['warnings']}, ensure_ascii=False), flush=True)
        previous = output
        # Preserve each completed preflight if a later grid encounters an issue.
        report['elapsed_s'] = time.perf_counter() - overall_started
        (HERE / 'preflight_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    np.savez_compressed(HERE / 'preflight_npz.npz', scope='PREFLIGHT N320 ONLY; NOT FINAL',
                        time_s=np.arange(END+1), radius_cm=np.arange(21)/10,
                        temperature_C=output[:,:,0], moisture_dry_basis=output[:,:,1],
                        average_T=avg_t, average_C=avg_c)
    report['elapsed_s'] = time.perf_counter() - overall_started
    report['execution_exit_status'] = 'completed_all_three_preflight_grids'
    (HERE / 'preflight_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'grid_comparisons': report['grid_comparisons'], 'elapsed_s': report['elapsed_s']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
