#!/usr/bin/env python3
"""Build Q1 paper figures and tables from unchanged formal numerical outputs.

Run from any directory: python paper/build_assets.py
Dependencies: NumPy, Matplotlib; Microsoft YaHei or SimSun for Chinese labels.
This script does not import or rerun any production solver.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FORMAL = ROOT / 'q1_complete_delivery/q1_delivery/output'
TIMES = np.array([100, 300, 600, 900, 1200, 1500, 1800])
PROFILE_TIMES = [300, 600, 1200, 1800]
COLORS = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#D55E00']
STYLES = ['-', '--', '-.', (0, (1, 1.4)), (0, (5, 1, 1, 1))]
FIGURE_CM = [16.0, 6.9]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def configure_style() -> str:
    available = {item.name for item in font_manager.fontManager.ttflist}
    selected = next((name for name in ['Microsoft YaHei', 'SimSun'] if name in available), None)
    if selected is None:
        raise RuntimeError('Install Microsoft YaHei or SimSun before building Chinese figures.')
    plt.rcParams.update({
        'font.family': selected,
        'font.size': 8.5,
        'axes.labelsize': 8.5,
        'axes.titlesize': 9,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 7.7,
        'axes.linewidth': .65,
        'lines.linewidth': 1.3,
        'xtick.major.width': .6,
        'ytick.major.width': .6,
        'xtick.major.size': 3,
        'ytick.major.size': 3,
        'axes.unicode_minus': False,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'savefig.dpi': 400,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
    })
    return selected


def panels():
    fig, axes = plt.subplots(1, 2, figsize=(FIGURE_CM[0] / 2.54, FIGURE_CM[1] / 2.54))
    # Fixed dimensions are preserved in both PDF and PNG (no tight bounding-box crop).
    fig.subplots_adjust(left=.085, right=.960, bottom=.195, top=.88, wspace=.34)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', color='#D7DCE0', linewidth=.5, alpha=.7)
        ax.set_axisbelow(True)
        ax.tick_params(direction='out', pad=2)
    return fig, axes


def legend(ax, location, handlelength=2.8, **kwargs):
    ax.legend(loc=location, frameon=False, handlelength=handlelength, handletextpad=.6,
              borderaxespad=.4, labelspacing=.35, **kwargs)


def save_pair(fig, name):
    for ext in ['pdf', 'png']:
        target = HERE / 'figures' / f'{name}.{ext}'
        metadata = ({'CreationDate': None, 'ModDate': None, 'Title': name}
                    if ext == 'pdf' else {'Title': name, 'Source': 'formal Q1 unrounded output'})
        fig.savefig(target, metadata=metadata)
    plt.close(fig)


def history(raw):
    time = raw['time_s']
    fig, (heat, moisture) = panels()
    heat.plot(time, raw['temperature_degC'][:, 0], color=COLORS[0], linestyle='-', label='轴心')
    heat.plot(time, raw['temperature_degC'][:, -1], color=COLORS[4], linestyle='--', label='表面')
    heat.plot(time, raw['environment'][:, 0], color='#555555', linestyle='-.', label='烘房环境')
    heat.set(title='(a) 温度随时间变化', xlabel='时间 / s', ylabel='温度 / ℃',
             xlim=(0, 1800), ylim=(27.5, 42.2))
    heat.yaxis.set_major_locator(MultipleLocator(4))
    legend(heat, 'upper left')
    for j, index in enumerate(range(0, 21, 5)):
        moisture.plot(time, raw['moisture_dry_basis'][:, index], color=COLORS[j], linestyle=STYLES[j],
                      label=f'r = {raw["radius_cm"][index]:g} cm')
    moisture.set(title='(b) 干基含水率随时间变化', xlabel='时间 / s',
                 ylabel='干基含水率 / (kg/kg)', xlim=(0, 1800), ylim=(1.46, 2.62))
    moisture.yaxis.set_major_locator(MultipleLocator(.25))
    legend(moisture, 'center right')
    for ax in [heat, moisture]:
        ax.xaxis.set_major_locator(MultipleLocator(600))
    save_pair(fig, 'q1_history')


def profiles(snapshots):
    fig, (heat, moisture) = panels()
    for ax, field in [(heat, 'T'), (moisture, 'C')]:
        data = snapshots[field]
        for j, time in enumerate(PROFILE_TIMES):
            row = np.flatnonzero(data['snapshot_times_s'] == time)
            assert len(row) == 1
            ax.plot(data['internal_radius_m'] * 100, data['internal_snapshots'][row[0]],
                    color=COLORS[j], linestyle=STYLES[j], label=f't = {time} s')
        ax.set(xlabel='径向距离 / cm', xlim=(0, 2))
        ax.xaxis.set_major_locator(MultipleLocator(.5))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
    heat.set(title='(a) 温度径向分布', ylabel='温度 / ℃', ylim=(27.7, 37.2))
    heat.yaxis.set_major_locator(MultipleLocator(2))
    legend(heat, 'upper left', ncol=2, columnspacing=.6, handlelength=2.0, fontsize=7.4)
    moisture.set(title='(b) 干基含水率径向分布', ylabel='干基含水率 / (kg/kg)', ylim=(1.46, 2.62))
    moisture.yaxis.set_major_locator(MultipleLocator(.25))
    legend(moisture, 'lower left')
    save_pair(fig, 'q1_profiles')


def table(raw, key, stub, caption, label):
    rows = [[str(int(t))] + [f'{float(v):.4f}' for v in raw[key][t, ::5]] for t in TIMES]
    headers = ['time_s', '0_cm', '0.5_cm', '1_cm', '1.5_cm', '2_cm']
    with (FORMAL / f'table_{stub}.csv').open(encoding='utf-8', newline='') as stream:
        formal_rows = list(csv.reader(stream))
    assert formal_rows == [headers] + rows, f'{stub}: generated table differs from formal CSV'
    csv_path = HERE / 'tables' / f'q1_{stub}.csv'
    with csv_path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(headers)
        writer.writerows(rows)
    tex_lines = [
        r'\begin{table}[htbp]',
        r'  \centering',
        f'  \\caption{{{caption}}}',
        f'  \\label{{{label}}}',
        r'  \small',
        r'  \begin{tabular}{rrrrrr}',
        r'    \toprule',
        r'    时间 / s & \multicolumn{5}{c}{到轴心的径向距离 / cm} \\',
        r'    \cmidrule(lr){2-6}',
        r'    & 0 & 0.5 & 1 & 1.5 & 2 \\',
        r'    \midrule',
        *['    ' + ' & '.join(row) + r' \\' for row in rows],
        r'    \bottomrule',
        r'  \end{tabular}',
        r'\end{table}',
        '',
    ]
    (HERE / 'tables' / f'q1_{stub}.tex').write_text('\n'.join(tex_lines), encoding='utf-8')
    return {'label': label, 'times_s': TIMES.tolist(), 'radius_cm': raw['radius_cm'][::5].tolist(),
            'result_count': 35, 'decimal_places': 4, 'formal_csv_exact_text_cells_match': True}


def main():
    for directory in ['figures', 'tables', 'evidence']:
        (HERE / directory).mkdir(exist_ok=True)
    source_paths = [FORMAL / name for name in ['q1_unrounded.npz', 'T_n10240.npz', 'C_n10240.npz',
                                              'table_temperature.csv', 'table_moisture.csv']]
    source_hashes = {rel(path): sha(path) for path in source_paths}
    raw = dict(np.load(FORMAL / 'q1_unrounded.npz'))
    assert np.array_equal(raw['time_s'], np.arange(1801))
    assert np.allclose(raw['radius_cm'], np.arange(21) / 10, rtol=0, atol=1e-14)
    snapshots = {field: dict(np.load(FORMAL / f'{field}_n10240.npz')) for field in ['T', 'C']}
    for field, key in [('T', 'temperature_degC'), ('C', 'moisture_dry_basis')]:
        assert raw[key].shape == (1801, 21) and np.isfinite(raw[key]).all()
        snapshot = snapshots[field]
        assert snapshot['internal_snapshots'].shape[1] == 10241
        assert np.array_equal(snapshot['internal_snapshots'][:, ::512],
                              raw[key][snapshot['snapshot_times_s'].astype(int)])
    font = configure_style()
    history(raw)
    profiles(snapshots)
    tables = {
        'temperature': table(raw, 'temperature_degC', 'temperature',
                             '规定时刻药材中截面的温度（单位：℃）', 'tab:q1-temperature'),
        'moisture': table(raw, 'moisture_dry_basis', 'moisture',
                         '规定时刻药材中截面的干基含水率（单位：kg/kg）', 'tab:q1-moisture'),
    }
    rho, cp, radius, length, k, D0, a = 820., 2600., .02, .25, .36, 7e-9, .89
    alpha = k / (rho * cp)
    D_initial = D0 * np.exp(-a / 2.55)
    ts, tc = float(raw['temperature_degC'][-1, -1]), float(raw['temperature_degC'][-1, 0])
    final = {'time_s': 1800, 'center_temperature_degC': tc, 'surface_temperature_degC': ts,
             'surface_minus_center_temperature_K': ts - tc,
             'surface_minus_center_four_decimal_K': f'{ts-tc:.4f}',
             'center_moisture_kg_kg': float(raw['moisture_dry_basis'][-1, 0]),
             'surface_moisture_kg_kg': float(raw['moisture_dry_basis'][-1, -1]),
             'volume_weighted_average_temperature_degC': float(raw['average_temperature_degC'][-1]),
             'volume_weighted_average_moisture_kg_kg': float(raw['average_C'][-1]),
             'relative_average_moisture_decrease_percent': float(100 * (2.55 - raw['average_C'][-1]) / 2.55),
             'environment_temperature_degC': float(raw['environment'][-1, 0])}
    common = {'size_cm': FIGURE_CM, 'png_dpi': 400, 'formats': ['PDF vector', 'PNG'],
              'font': font, 'color_scheme': 'Okabe-Ito colors plus distinguishable line styles',
              'numerical_interpolation_for_plotting': 'none; connected original numerical samples',
              'model_scope': 'fixed cylinder midplane; effective Robin exchange; no explicit latent heat or radiation'}
    figure_contracts = {
        'q1_history': {**common,
            'data_source': rel(FORMAL / 'q1_unrounded.npz'),
            'question': 'How do center/surface temperatures and five radial moisture values evolve within 1800 s?',
            'x': {'name': 'time', 'unit': 's', 'range': [0, 1800], 'step': 1, 'sample_count': 1801},
            'left': {'unit': 'degC', 'series': {'center': {'color': COLORS[0], 'line': 'solid'},
                     'surface': {'color': COLORS[4], 'line': 'dashed'},
                     'environment': {'color': '#555555', 'line': 'dash-dot'}}},
            'right': {'unit': 'kg water/kg dry material', 'radii_cm': [0, .5, 1, 1.5, 2],
                      'series_colors': COLORS, 'line_styles': ['solid', 'dashed', 'dash-dot', 'dotted', 'long-short dash'],
                      'environment_moisture_plotted': False}},
        'q1_profiles': {**common,
            'data_source': [rel(FORMAL / 'T_n10240.npz'), rel(FORMAL / 'C_n10240.npz')],
            'question': 'How do radial temperature and moisture gradients differ at four specified times?',
            'x': {'name': 'radial distance from axis', 'unit': 'cm', 'range': [0, 2],
                  'step': 2 / 10240, 'sample_count': 10241},
            'times_s': PROFILE_TIMES, 'series_colors': COLORS[:4],
            'line_styles': ['solid', 'dashed', 'dash-dot', 'dotted'],
            'left_unit': 'degC', 'right_unit': 'kg water/kg dry material',
            'internal_snapshots_exactly_match_formal_21_output_nodes': True},
    }
    outputs = [HERE / 'figures' / f'{name}.{ext}' for name in ['q1_history', 'q1_profiles'] for ext in ['pdf', 'png']]
    outputs += [HERE / 'tables' / f'q1_{name}.{ext}' for name in ['temperature', 'moisture'] for ext in ['tex', 'csv']]
    assert all(sha(path) == source_hashes[rel(path)] for path in source_paths)
    manifest = {'generated_by': rel(Path(__file__)), 'builder_sha256': sha(Path(__file__)),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
        'sourceSHA256': source_hashes, 'formal_source_files_unchanged': True, 'production_solver_rerun': False,
        'final_1800_s': final,
        'scales': {'radius_m': radius, 'length_m': length, 'thermal_diffusivity_m2_s': alpha,
            'initial_moisture_diffusivity_m2_s': float(D_initial), 'thermal_time_scale_s': radius**2 / alpha,
            'initial_moisture_time_scale_s': float(radius**2 / D_initial),
            'thermal_diffusion_length_at_1800_cm': float(100 * np.sqrt(alpha * 1800)),
            'initial_moisture_diffusion_length_at_1800_cm': float(100 * np.sqrt(D_initial * 1800)),
            'thermal_Biot_radius': 25 * radius / k, 'moisture_Biot_radius_initial': float(8e-7 * radius / D_initial),
            'interpretation': 'R-based characteristic scales; diffusion length is a scale, not a finite propagation front'},
        'tables': tables, 'figures': figure_contracts,
        'outputs': {rel(path): {'sha256': sha(path), 'bytes': path.stat().st_size} for path in outputs}}
    (HERE / 'evidence/asset_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'assets': len(outputs), 'formal_csv_tables_match': True,
                      'source_files_unchanged': True, 'final_1800_s': final}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
