#!/usr/bin/env python3
"""Build Q2 paper assets exclusively from unchanged accepted output arrays.

Run from any directory. This script neither imports nor reruns any PDE solver.
The Chinese font, palette, physical figure size and line widths follow the
frozen Q1 paper/build_assets.py. Formal CSV table cells are preserved verbatim.
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
ROOT = HERE.parents[1]
FORMAL = ROOT / 'q2_final_delivery/output'
REFINED = ROOT / 'q2_refinement_delivery'
COLORS = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#D55E00', '#555555']
STYLES = ['-', '--', '-.', (0, (1, 1.4)), (0, (5, 1, 1, 1)), (0, (7, 2))]
FIGURE_CM = [16.0, 6.9]
TIMES_S = np.arange(1800, 10801, 1800)
POSITIONS = [0, 10, 20]
LOCATION_LABELS = ['轴心', '半径1 cm处', '表面']
LOCATION_COLORS = [COLORS[0], COLORS[2], COLORS[4]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def load(path):
    with np.load(path, allow_pickle=False) as z:
        return {key: z[key] for key in z.files}


def configure_style():
    available = {item.name for item in font_manager.fontManager.ttflist}
    selected = next((name for name in ['Microsoft YaHei', 'SimSun'] if name in available), None)
    if selected is None:
        raise RuntimeError('Install Microsoft YaHei or SimSun before building Chinese figures.')
    plt.rcParams.update({
        'font.family': selected, 'font.size': 8.5, 'axes.labelsize': 8.5,
        'axes.titlesize': 9, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
        'legend.fontsize': 7.7, 'axes.linewidth': .65, 'lines.linewidth': 1.3,
        'xtick.major.width': .6, 'ytick.major.width': .6,
        'xtick.major.size': 3, 'ytick.major.size': 3,
        'axes.unicode_minus': False, 'pdf.fonttype': 42, 'ps.fonttype': 42,
        'savefig.dpi': 400, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
    })
    return selected


def panels():
    fig, axes = plt.subplots(1, 2, figsize=(FIGURE_CM[0] / 2.54, FIGURE_CM[1] / 2.54))
    fig.subplots_adjust(left=.085, right=.960, bottom=.195, top=.88, wspace=.34)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', color='#D7DCE0', linewidth=.5, alpha=.7)
        ax.set_axisbelow(True)
        ax.tick_params(direction='out', pad=2)
    return fig, axes


def legend(ax, location, **kwargs):
    ax.legend(loc=location, frameon=False, handlelength=2.8, handletextpad=.6,
              borderaxespad=.4, labelspacing=.35, **kwargs)


def common_time(axes):
    for ax in axes:
        ax.set(xlabel='时间 / h', xlim=(0, 3))
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))


def save_pair(fig, name):
    # A fixed presentation limit must never hide an accepted curve extremum.
    for ax in fig.axes:
        lower, upper = ax.get_ylim()
        for line in ax.lines:
            values = np.asarray(line.get_ydata(), dtype=float)
            assert np.isfinite(values).all()
            assert values.min() >= lower - 1e-12 and values.max() <= upper + 1e-12, f'{name}: clipped data'
    for ext in ['pdf', 'png']:
        metadata = ({'CreationDate': None, 'ModDate': None, 'Title': name}
                    if ext == 'pdf' else {'Title': name, 'Source': 'accepted Q2 arrays; no PDE rerun'})
        fig.savefig(HERE / 'figures' / f'{name}.{ext}', metadata=metadata)
    plt.close(fig)


def profiles(raw):
    fig, axes = panels()
    # One common six-entry legend avoids covering the nearly flat profiles.
    fig.subplots_adjust(top=.77)
    for ax, key in zip(axes, ['temperature_degC', 'moisture_dry_basis']):
        for j, t in enumerate(TIMES_S):
            ax.plot(raw['radius_cm'], raw[key][t], color=COLORS[j],
                    linestyle=STYLES[j], label=f'{t / 3600:g} h')
        ax.set(xlabel='径向距离 / cm', xlim=(0, 2))
        ax.xaxis.set_major_locator(MultipleLocator(.5))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
    axes[0].set(title='(a) 温度径向分布', ylabel='温度 / ℃', ylim=(30.8, 51.0))
    axes[0].yaxis.set_major_locator(MultipleLocator(5))
    axes[1].set(title='(b) 干基含水率径向分布', ylabel='干基含水率 / (kg/kg)', ylim=(.93, 2.63))
    axes[1].yaxis.set_major_locator(MultipleLocator(.4))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.51, 1.0),
               ncol=6, frameon=False, handlelength=2.2, columnspacing=1.2, fontsize=7.7)
    save_pair(fig, 'q2_profiles')


def history(raw):
    fig, axes = panels()
    for ax, key in zip(axes, ['temperature_degC', 'moisture_dry_basis']):
        for j, index in enumerate(POSITIONS):
            ax.plot(raw['time_s'] / 3600, raw[key][:, index],
                    color=LOCATION_COLORS[j], linestyle=STYLES[j], label=LOCATION_LABELS[j])
    axes[0].set(title='(a) 温度随时间变化', ylabel='温度 / ℃', ylim=(27, 52.0))
    axes[0].yaxis.set_major_locator(MultipleLocator(5))
    axes[1].set(title='(b) 干基含水率随时间变化', ylabel='干基含水率 / (kg/kg)', ylim=(.93, 2.64))
    axes[1].yaxis.set_major_locator(MultipleLocator(.4))
    common_time(axes)
    legend(axes[0], 'lower right')
    legend(axes[1], 'lower left')
    save_pair(fig, 'q2_history')


def mechanism(data):
    fig, axes = panels()
    time_h = data['time_s'] / 3600
    for j in range(3):
        axes[0].plot(time_h, data['D_over_D0'][:, j], color=LOCATION_COLORS[j],
                     linestyle=STYLES[j], label=LOCATION_LABELS[j])
    axes[0].axhline(1, color='#777777', linestyle=':', linewidth=.8)
    axes[0].set(title='(a) 局部扩散系数相对初值', ylabel=r'$D/D_0$（无量纲）', ylim=(.92, 2.3))
    for j, (values, label) in enumerate([
        (data['H'][:, 2], '温度累计项 H'),
        (data['M'][:, 2], '含水率累计项 M'),
        (data['H'][:, 2] + data['M'][:, 2], '净累计项 H+M'),
    ]):
        axes[1].plot(time_h, values, color=COLORS[j], linestyle=STYLES[j], label=label)
    axes[1].axhline(0, color='#777777', linestyle=':', linewidth=.8)
    axes[1].set(title='(b) 表面扩散系数的累计对数分解', ylabel='对数贡献（无量纲）', ylim=(-.34, .98))
    common_time(axes)
    legend(axes[0], 'lower right')
    legend(axes[1], 'center right', fontsize=7.2)
    save_pair(fig, 'q2_mechanism')


def sensitivity(tracks):
    fig, axes = panels()
    fig.subplots_adjust(top=.77)
    base = np.column_stack([tracks['baseline__moisture_dry_basis'], tracks['baseline__average_moisture_dry_basis']])
    labels = LOCATION_LABELS + [r'$r\,dr$加权平均']
    colors = LOCATION_COLORS + [COLORS[3]]
    verified_count = 0
    with (REFINED / 'data/parameter_sensitivity_timeseries.csv').open(encoding='utf-8', newline='') as stream:
        verified_rows = list(csv.DictReader(stream))
    assert len(verified_rows) == 2 * 4 * len(tracks['time_s'])
    final = {}
    ranges = {}
    for q, (ax, par) in enumerate(zip(axes, ['hm', 'hT'])):
        low = np.column_stack([tracks[par + '_0.8__moisture_dry_basis'], tracks[par + '_0.8__average_moisture_dry_basis']])
        high = np.column_stack([tracks[par + '_1.2__moisture_dry_basis'], tracks[par + '_1.2__average_moisture_dry_basis']])
        elasticity = (high - low) / (.4 * base)
        assert np.all(base > 0) and np.isfinite(elasticity).all()
        for j, loc in enumerate(['axis', 'r1cm', 'surface', 'rdr_mean']):
            block = verified_rows[(q * 4 + j) * len(base):(q * 4 + j + 1) * len(base)]
            assert all(row['parameter'] == par and row['location'] == loc for row in block)
            assert np.array_equal(np.array([float(row['C_secant_elasticity']) for row in block]), elasticity[:, j])
            verified_count += len(block)
            ax.plot(tracks['time_s'] / 3600, elasticity[:, j], color=colors[j], linestyle=STYLES[j], label=labels[j])
        final[par] = elasticity[-1].tolist()
        low_e, high_e = float(elasticity.min()), float(elasticity.max())
        margin = .08 * (high_e - low_e)
        ax.set_ylim(low_e - margin, high_e + margin)
        ranges[par] = {'data_range': [low_e, high_e], 'axis_range': list(ax.get_ylim())}
    axes[0].set(title=r'(a) 含水率对$h_m$的割线灵敏度', ylabel='归一化割线量（无量纲）')
    axes[1].set(title=r'(b) 含水率对$h_T$的割线灵敏度', ylabel='归一化割线量（无量纲）')
    axes[1].yaxis.set_major_locator(MultipleLocator(.01))
    common_time(axes)
    handles, display_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, display_labels, loc='upper center', bbox_to_anchor=(.51, 1.0),
               ncol=4, frameon=False, handlelength=2.6, columnspacing=1.5, fontsize=7.7)
    save_pair(fig, 'q2_sensitivity')
    return {'verified_against_accepted_csv_values': verified_count, 'final_3h': final,
            'plotted_ranges': ranges,
            'formula': '(C(1.2p)-C(0.8p))/(0.4*C(p))', 'baseline_grid_intervals': 320,
            'mask': 'none needed for moisture because all baseline C values are positive; no temperature-rise sensitivity plotted'}


def table(raw, stub, key, caption, label):
    source = FORMAL / f'table_{stub}.csv'
    with source.open(encoding='utf-8', newline='') as stream:
        formal_rows = list(csv.reader(stream))
    header, rows = formal_rows[0], formal_rows[1:]
    assert header == ['time_h', '0cm', '0.5cm', '1cm', '1.5cm', '2cm']
    assert len(rows) == 6 and all(len(row) == 6 for row in rows)
    expected = [[f'{t / 3600:.1f}'] + [f'{float(v):.4f}' for v in raw[key][t, ::5]] for t in TIMES_S]
    assert rows == expected, f'Formal {stub} CSV disagrees with accepted unrounded output'
    # Exact copy preserves all formal text cells and original decimal precision.
    (HERE / 'tables' / f'q2_{stub}.csv').write_bytes(source.read_bytes())
    tex = [r'\begin{table}[htbp]', r'  \centering', f'  \\caption{{{caption}}}',
           f'  \\label{{{label}}}', r'  \small', r'  \begin{tabular}{rrrrrr}',
           r'    \toprule', r'    时间 / h & \multicolumn{5}{c}{到轴心的径向距离 / cm} \\',
           r'    \cmidrule(lr){2-6}', r'    & 0 & 0.5 & 1 & 1.5 & 2 \\', r'    \midrule',
           *['    ' + ' & '.join(row) + r' \\' for row in rows], r'    \bottomrule',
           r'  \end{tabular}', r'\end{table}', '']
    (HERE / 'tables' / f'q2_{stub}.tex').write_text('\n'.join(tex), encoding='utf-8')
    return {'label': label, 'source': rel(source), 'times_h': [float(row[0]) for row in rows],
            'times_s': TIMES_S.tolist(), 'radius_cm': raw['radius_cm'][::5].tolist(),
            'result_count': 30, 'decimal_places': 4, 'formal_csv_exact_text_cells_match': True,
            'csv_byte_identical_to_formal': True}


def main():
    for directory in ['figures', 'tables', 'evidence']:
        (HERE / directory).mkdir(parents=True, exist_ok=True)
    source_paths = [FORMAL / 'q2_unrounded.npz', FORMAL / 'table_temperature.csv', FORMAL / 'table_moisture.csv',
                    REFINED / 'data/mechanism_unrounded.npz', REFINED / 'reused/sensitivity_tracks.npz',
                    REFINED / 'data/parameter_sensitivity_timeseries.csv', ROOT / 'paper/build_assets.py']
    hashes = {rel(path): sha(path) for path in source_paths}
    raw = load(source_paths[0]); mech = load(source_paths[3]); tracks = load(source_paths[4])
    assert np.array_equal(raw['time_s'], np.arange(10801))
    assert np.allclose(raw['radius_cm'], np.arange(21) / 10, rtol=0, atol=1e-14)
    for key in ['temperature_degC', 'moisture_dry_basis']:
        assert raw[key].shape == (10801, 21) and np.isfinite(raw[key]).all()
    assert np.array_equal(mech['time_s'], raw['time_s']) and np.array_equal(tracks['time_s'], raw['time_s'])
    assert np.array_equal(mech['radius_cm'], [0., 1., 2.])
    assert np.array_equal(mech['T'], raw['temperature_degC'][:, POSITIONS])
    assert np.array_equal(mech['C'], raw['moisture_dry_basis'][:, POSITIONS])
    assert np.max(np.abs(np.log(mech['D_over_D0']) - mech['H'] - mech['M'])) < 2e-13
    font = configure_style()
    profiles(raw); history(raw); mechanism(mech); sens = sensitivity(tracks)
    tables = {
        'temperature': table(raw, 'temperature', 'temperature_degC', '第二问规定时刻的中截面温度（单位：℃）', 'tab:q2-temperature'),
        'moisture': table(raw, 'moisture', 'moisture_dry_basis', '第二问规定时刻的中截面干基含水率（单位：kg/kg）', 'tab:q2-moisture'),
    }
    common = {'size_cm': FIGURE_CM, 'png_dpi': 400, 'formats': ['PDF vector', 'PNG'], 'font': font,
              'style_reference': 'paper/build_assets.py; same Chinese font/palette/line widths',
              'numerical_interpolation_for_plotting': 'none; connected original numerical samples',
              'model_scope': 'fixed cylinder midplane, accepted effective model, 0 to 3 h',
              'color_scheme': 'Q1 Okabe-Ito colors with distinguishable line styles; gray sixth profile'}
    contracts = {
        'q2_profiles': {**common, 'data_source': rel(source_paths[0]), 'times_s': TIMES_S.tolist(),
            'x': {'name': 'radial distance', 'unit': 'cm', 'range': [0, 2], 'sample_count': 21},
            'left_field': 'temperature_degC', 'left_unit': 'degC', 'right_field': 'moisture_dry_basis',
            'right_unit': 'kg water/kg dry material', 'series_colors': COLORS, 'mask': 'none'},
        'q2_history': {**common, 'data_source': rel(source_paths[0]), 'radii_cm': [0, 1, 2],
            'x': {'name': 'time', 'unit': 'h', 'range': [0, 3], 'sample_count': 10801, 'source_step_s': 1},
            'left_field': 'temperature_degC', 'right_field': 'moisture_dry_basis',
            'left_unit': 'degC', 'right_unit': 'kg water/kg dry material', 'mask': 'none'},
        'q2_mechanism': {**common, 'data_source': rel(source_paths[3]),
            'x': {'name': 'time', 'unit': 'h', 'range': [0, 3], 'sample_count': 10801},
            'left_field': 'D_over_D0 at radii 0,1,2 cm', 'right_field': 'H, M, H+M at surface 2 cm',
            'left_unit': 'dimensionless', 'right_unit': 'dimensionless',
            'interpretation': 'cumulative logarithmic identity; not instantaneous rates or causal percentages',
            'mask': 'none; instantaneous-rate masks do not apply to cumulative states'},
        'q2_sensitivity': {**common, 'data_source': [rel(source_paths[4]), rel(source_paths[5])], **sens,
            'x': {'name': 'time', 'unit': 'h', 'range': [0, 3], 'sample_count': 10801},
            'left_parameter': 'hm', 'right_parameter': 'hT', 'radii_cm': [0, 1, 2],
            'average': 'stored r dr weighted average on the same N320 grid',
            'left_unit': 'dimensionless', 'right_unit': 'dimensionless'},
    }
    outputs = [HERE / 'figures' / f'{name}.{ext}' for name in contracts for ext in ['pdf', 'png']]
    outputs += [HERE / 'tables' / f'q2_{stub}.{ext}' for stub in ['temperature', 'moisture'] for ext in ['csv', 'tex']]
    assert all(sha(path) == hashes[rel(path)] for path in source_paths), 'Frozen source changed during build'
    manifest = {'generated_by': rel(Path(__file__)), 'builder_sha256': sha(Path(__file__)),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
        'sourceSHA256': hashes, 'formal_source_files_unchanged': True, 'production_solver_rerun': False,
        'formal_result_count': 60, 'tables': tables, 'figures': contracts,
        'outputs': {rel(path): {'sha256': sha(path), 'bytes': path.stat().st_size} for path in outputs}}
    (HERE / 'evidence/q2_asset_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'assets': len(outputs), 'formal_csv_tables_match': True, 'formal_result_count': 60,
                      'source_files_unchanged': True, 'font': font, 'sensitivity_values_verified': sens['verified_against_accepted_csv_values']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
