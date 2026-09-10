"""Independent Q1 thermal verification: direct OOXML input + modal exact stepping.

No production module is imported. For theta = T - T_ambient,
theta_t = alpha * (theta_rr + theta_r/r) - T_ambient'(t), with
theta_r(R) + h/k * theta(R) = 0. The eigenfunctions are J0(beta*r/R),
beta*J1(beta) = Bi*J0(beta). Projection of the constant forcing is
b = 2*J1(beta)/(beta*(J0(beta)**2+J1(beta)**2)). Each modal coefficient
is advanced exactly on each one-second interval (all input knots are at
integer seconds), a_new = exp(-q)*a - b*slope*(1-exp(-q))/q.
"""
from pathlib import Path
import hashlib
import json
import sys
import time
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.special import j0, j1, jn_zeros

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL = ROOT / 'A题' / '附件' / '附件1.xlsx'
DELIVERY = ROOT / 'q1_complete_delivery' / 'q1_delivery' / 'output'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def read_workbook(path):
    """Read values directly from the ZIP package; separate from production parser."""
    with zipfile.ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            shared = [''.join(item.itertext()) for item in root]
        book = ET.fromstring(archive.read('xl/workbook.xml'))
        rels = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        targets = {item.attrib['Id']: item.attrib['Target'] for item in rels}
        out = {}
        for sheet in book.find('m:sheets', NS):
            rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = targets[rid]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            root = ET.fromstring(archive.read(target))
            data = {}
            for cell in root.findall('.//m:sheetData/m:row/m:c', NS):
                value = cell.find('m:v', NS)
                kind = cell.attrib.get('t', 'n')
                if kind == 'inlineStr':
                    data[cell.attrib['r']] = ''.join(cell.find('m:is', NS).itertext())
                elif value is not None:
                    if kind == 's':
                        data[cell.attrib['r']] = shared[int(value.text)]
                    elif kind == 'str':
                        data[cell.attrib['r']] = value.text
                    else:
                        data[cell.attrib['r']] = float(value.text)
            out[sheet.attrib['name']] = data
    return out


def formatted(array):
    # Match the specified four-decimal presentation by independently formatting.
    return np.array([format(float(value), '.4f') for value in array.flat]).reshape(array.shape)


def solve_heat(input_data, count):
    R, density, cp, conductivity, h = 0.02, 820.0, 2600.0, 0.36, 25.0
    diffusivity = conductivity / (density * cp)
    biot = h * R / conductivity
    zeros = jn_zeros(0, count)
    beta = np.empty(count)
    lower = 0.0
    for i, upper in enumerate(zeros):
        beta[i] = brentq(lambda b: b * j1(b) - biot * j0(b), lower, upper,
                         xtol=5e-14, rtol=9e-16)
        lower = upper
    projected_one = 2 * j1(beta) / (beta * (j0(beta)**2 + j1(beta)**2))
    q = diffusivity * beta**2 / R**2
    decay = np.exp(-q)
    forcing_gain = projected_one * (-np.expm1(-q)) / q
    output_times = np.arange(1801)
    radii = np.arange(21) / 1000.0
    ambient = np.interp(output_times, input_data[:, 0], input_data[:, 1])
    a = np.zeros((len(output_times), count))
    for i in range(1, len(output_times)):
        a[i] = decay * a[i-1] - forcing_gain * (ambient[i] - ambient[i-1])
    temperature = ambient[:, None] + a @ j0(beta[:, None] * radii[None, :] / R)
    average = ambient + a @ (2 * j1(beta) / beta)
    return temperature, average, beta


def differences(given, independent, times, radii, limit=100):
    delta = np.abs(given - independent)
    at = np.unravel_index(delta.argmax(), delta.shape)
    indices = np.argwhere(formatted(given) != formatted(independent))
    return {
        'cells': int(given.size), 'max_abs_error_degC': float(delta[at]),
        'rms_error_degC': float(np.sqrt(np.mean(delta**2))),
        'max_error_at': {'time_s': int(times[at[0]]), 'radius_cm': float(radii[at[1]])},
        'four_decimal_mismatches': len(indices),
        'mismatch_locations': [
            {'time_s': int(times[i]), 'radius_cm': float(radii[j]),
             'given': float(given[i, j]), 'independent': float(independent[i, j]),
             'given_four_decimal': format(float(given[i,j]), '.4f'),
             'independent_four_decimal': format(float(independent[i,j]), '.4f')}
            for i, j in indices[:limit]
        ],
    }


def main():
    started = time.perf_counter()
    original_sheet = next(iter(read_workbook(ORIGINAL).values()))
    input_data = np.array([[original_sheet[f'{c}{r}'] for c in 'ABC']
                          for r in range(2, 243)])
    assert np.array_equal(input_data[:, 0], np.arange(0, 14401, 60))
    assert input_data[0, 1] == 28.0
    assert np.isfinite(input_data).all()
    saved = np.load(DELIVERY / 'q1_unrounded.npz')
    expected_times = np.arange(1801)
    expected_radii_cm = np.arange(21) / 10
    assert np.array_equal(saved['time_s'], expected_times)
    assert np.allclose(saved['radius_cm'], expected_radii_cm, atol=1e-15, rtol=0)
    report = {
        'method': __doc__,
        'input_sha256': hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
        'runtime': {'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__},
        'parameters': {'rho_kg_m3': 820, 'cp_J_kgK': 2600, 'k_W_mK': .36,
                       'h_W_m2K': 25, 'R_m': .02, 'T0_degC': 28},
        'model_scope': '1D radial homogeneous cylinder, linear ambient interpolation, no latent heat',
        'modes': {},
    }
    previous = None
    for count in (200, 800, 3200):
        temperature, average, beta = solve_heat(input_data, count)
        checks = differences(saved['temperature_degC'][1:], temperature[1:],
                             expected_times[1:], expected_radii_cm)
        if previous is not None:
            checks['change_from_previous_modes_degC'] = float(np.max(np.abs(temperature - previous)))
            checks['four_decimal_changes_from_previous'] = int(np.count_nonzero(formatted(temperature[1:]) != formatted(previous[1:])))
        report['modes'][str(count)] = checks
        previous = temperature
        print(json.dumps({'modes': count, 'summary': checks}, ensure_ascii=False), flush=True)
    np.savez_compressed(HERE / 'independent_heat_3200.npz', time_s=expected_times,
                        radius_cm=expected_radii_cm, temperature_degC=temperature,
                        average_temperature_degC=average, roots=beta)
    report['average_temperature_max_abs_error_degC'] = float(np.max(np.abs(average - saved['average_temperature_degC'])))
    ambient = np.interp(expected_times, input_data[:, 0], input_data[:, 1])
    report['ambient_interpolation_max_abs_error_degC'] = float(np.max(np.abs(ambient - saved['environment'][:, 0])))
    delivered_book = read_workbook(DELIVERY / 'result1.xlsx')['温度']
    excel = np.array([[delivered_book[f'{chr(66+j)}{i+1}'] for j in range(21)] for i in range(1, 1801)])
    report['delivered_excel_vs_independent'] = differences(excel, temperature[1:], expected_times[1:], expected_radii_cm)
    sample_times = np.array([100, 300, 600, 900, 1200, 1500, 1800])
    table = temperature[sample_times][:, ::5]
    report['table_temperature_degC'] = {'time_s': sample_times.tolist(),
                                        'radius_cm': expected_radii_cm[::5].tolist(),
                                        'values_four_decimal': formatted(table).tolist()}
    np.savetxt(HERE / 'independent_table_temperature.csv', np.column_stack((sample_times, table)),
               delimiter=',', header='time_s,r0.0_cm,r0.5_cm,r1.0_cm,r1.5_cm,r2.0_cm',
               comments='', fmt=['%d'] + ['%.4f'] * 5)
    # Distances to the nearest half-unit rounding threshold can expose fragile digits.
    threshold_distance = np.abs((temperature[1:] * 10000) - (np.floor(temperature[1:] * 10000) + .5)) / 10000
    order = np.argsort(threshold_distance, axis=None)[:20]
    report['closest_rounding_thresholds'] = [
        {'time_s': int(i+1), 'radius_cm': float(expected_radii_cm[j]),
         'independent_degC': float(temperature[i+1, j]),
         'distance_to_threshold_degC': float(threshold_distance[i,j])}
        for i, j in zip(*np.unravel_index(order, threshold_distance.shape))
    ]
    report['elapsed_s'] = time.perf_counter() - started
    (HERE / 'heat_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
