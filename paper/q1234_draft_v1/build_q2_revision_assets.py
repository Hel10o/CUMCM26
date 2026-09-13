"""Q2 diagrams and log-diffusivity plot from frozen per-second output only.

This is graphical postprocessing. It does not import a solver, integrate any
equations, fit parameters, or write numerical source/historical evidence files.
"""
from pathlib import Path
import json
import platform
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import font_manager
import fitz

import build_ch6_assets as style

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/q2_revision'
EVIDENCE = BASE / 'evidence/q2_revision_20260913'
BASELINE = '218d741426a87794fa00560d0631a918d68c7bf3'
SOURCE = ROOT / 'q4_complete_delivery/v1/q123_closeout/output/q23_unified.npz'
EXPECTED_SOURCE_SHA = '80bd0a8ee77ac04189646a89e2dd78c2843344d9538923e402bef993b980c6f4'


def workflow():
    dimensions = [15.0, 3.2]
    fig, ax = style.canvas(*dimensions)
    style.label(ax, 7.5, 2.97, '统一传热传质模型 → 问题二条件与参数代入', size=9.6)
    specs = [
        ('inputs', .12, .41, 2.72, 1.83, '几何与共同初态\n环境记录\n附录3物性'),
        ('coupled_system', 3.40, .40, 3.45, 1.84,
         '固定半径径向模型\n变物性温湿耦合\nRobin交换边界'),
        ('joint_integration', 7.42, .55, 3.02, 1.55,
         'Chebyshev配点\nRadau隐式积分\n温湿场联立求解'),
        ('first_3h', 11.04, 1.65, 3.82, .95, '前3 h规定表格\n径向温湿分布'),
        ('full_trajectory', 11.04, .12, 3.82, .95, '全程温湿轨迹\n供问题三终点判定'),
    ]
    texts = []
    for name, x, y, w, h, value in specs:
        ax.add_patch(Rectangle((x, y), w, h, edgecolor=style.LINE,
                               facecolor='white', lw=.8, zorder=3))
        t = style.label(ax, x+w/2, y+h/2, value, size=9.2, linespacing=1.14)
        texts.append((name, t, x, y, w, h))
    style.arrow(ax, [(2.84, 1.325), (3.40, 1.325)])
    style.arrow(ax, [(6.85, 1.325), (7.42, 1.325)])
    style.arrow(ax, [(10.44, 1.325), (10.73, 1.325), (10.73, 2.125), (11.04, 2.125)])
    style.arrow(ax, [(10.44, 1.325), (10.73, 1.325), (10.73, .595), (11.04, .595)])
    fig.canvas.draw()
    fits = []
    for name, t, x, y, w, h in texts:
        b = t.get_window_extent(fig.canvas.get_renderer())
        a, c = ax.transData.transform([[x, y], [x+w, y+h]])
        inside = bool(b.x0>a[0]+.5 and b.y0>a[1]+.5 and
                      b.x1<c[0]-.5 and b.y1<c[1]-.5)
        assert inside, (name, b.bounds, a, c)
        fits.append({'node': name, 'text_inside_node': inside,
                     'fill': 'white', 'font_pt': t.get_fontsize()})
    result = style.save(fig, 'q2_workflow', dimensions)
    result.update({'node_checks': fits,
                   'semantics': 'Common initial state and annex 3 properties specialize the fixed-radius coupled radial model. Joint temperature/moisture integration supplies the first-three-hour tables and the assumed-environment full trajectory reused by Q3.',
                   'no_continuation_from_q1_1800s': True,
                   'numerical_trajectory_displayed': False})
    return result


def mechanism():
    before = style.sha(SOURCE)
    assert before == EXPECTED_SOURCE_SHA
    with np.load(SOURCE, allow_pickle=False) as archive:
        mask = archive['time_s'] <= 10800
        t = archive['time_s'][mask].copy()
        radial_coordinates = archive['radius_cm'].copy()
        state = archive['profile_TC'][mask][:, [0, -1], :].copy()
    assert np.array_equal(t, np.arange(10801, dtype=float))
    assert state.shape == (10801, 2, 2)
    assert np.array_equal(radial_coordinates[[0, -1]], [0., 2.])
    TK = state[:, :, 0] + 273.15
    C = state[:, :, 1]
    H = 3850 * (1/301.15 - 1/TK)
    M = .45 * (1/2.55 - 1/C)
    total = H + M
    D0 = 2.4e-3 * np.exp(-3850/301.15 - .45/2.55)
    D = 2.4e-3 * np.exp(-3850/TK - .45/C)
    ratio = D / D0
    residual = float(np.max(np.abs(total - np.log(ratio))))
    assert residual < 5e-15
    peaks = np.argmax(ratio, axis=0)
    assert np.array_equal(peaks, [8856, 7262])
    assert [f'{value:.4f}' for value in ratio[-1]] == ['2.1957', '1.8207']
    assert int(np.argmin(ratio[:, 1])) == 144
    assert f'{np.min(ratio[:, 1]):.6f}' == '0.983282'

    dimensions = [15.0, 5.5]
    fig = plt.figure(figsize=(dimensions[0]/2.54, dimensions[1]/2.54))
    colors = ['#216779', '#AC6325', '#22282D']
    handles = []
    panel_checks = []
    titles = []
    for col, name in enumerate(['轴心', '表面']):
        left, width = .078 + .492*col, .382
        ax = fig.add_axes([left, .235, width, .572])
        for j, (values, line_style, width_pt) in enumerate(
                [(H[:, col], '-', 1.15), (M[:, col], '--', 1.15),
                 (total[:, col], '-', 1.55)]):
            handle, = ax.plot(t/3600, values, linestyle=line_style,
                              color=colors[j], lw=width_pt)
            if col == 0:
                handles.append(handle)
            assert np.array_equal(handle.get_xdata(), t/3600)
            assert np.array_equal(handle.get_ydata(), values)
        ax.axhline(0, color='#AAB3B8', lw=.55, zorder=0)
        ax.set(xlim=(0, 3), ylim=(-.34, 1.04))
        ax.set_xticks([0, 1, 2, 3])
        ax.set_yticks([-.25, 0, .25, .50, .75, 1.0])
        ax.set_yticklabels(['−0.25', '0', '0.25', '0.50', '0.75', '1.00'])
        ax.set_xlabel('时间 / h', fontsize=9.2, labelpad=3)
        ax.tick_params(length=2.5, width=.65, direction='out', pad=2.5, labelsize=9.0)
        ax.spines[['top', 'right']].set_visible(False)
        ax.spines[['bottom', 'left']].set_color('#63727A')
        peak_index = int(peaks[col])
        peak_xy = (float(t[peak_index]/3600), float(total[peak_index, col]))
        ax.plot(*peak_xy, marker='o', ms=3.7, mfc='white', mec=colors[2], mew=1.0)
        ann = ax.annotate(f'{peak_xy[0]:.2f} h', xy=peak_xy,
                         xytext=((1.53 if col == 0 else 1.22), .985),
                         ha='center', va='center', fontsize=9.2,
                         arrowprops={'arrowstyle': '-', 'lw': .65,
                                     'color': '#52636D', 'shrinkB': 3},
                         bbox={'facecolor': 'white', 'edgecolor': 'none', 'pad': .1})
        title = fig.text(left+width/2, .865, f'({"a" if col == 0 else "b"}) {name}',
                         ha='center', va='center', fontsize=9.6)
        titles.append((title, left+width/2))
        panel_checks.append({'location': name, 'radial_index': [0, -1][col],
                             'all_10801_per_second_points_plotted': True,
                             'sample_peak_time_s': float(t[peak_index]),
                             'sample_peak_time_h': peak_xy[0],
                             'sample_peak_annotation_h': f'{peak_xy[0]:.2f}',
                             'sample_peak_sum': peak_xy[1],
                             'D_over_D0_at_3h': float(ratio[-1, col]),
                             'decrease_percent_2_5h_to_3h': float(100*(1-ratio[-1, col]/ratio[9000, col])),
                             'H_negative_one_second_differences': int(np.count_nonzero(np.diff(H[:, col]) < 0)),
                             'state': style.signature(state[:, col, :]),
                             'H': style.signature(H[:, col]),
                             'M': style.signature(M[:, col]),
                             'H_plus_M': style.signature(total[:, col])})
    fig.legend(handles, ['温度项 H', '含水率项 M', '合计 H+M'],
               loc='upper center', bbox_to_anchor=(.505, 1.015),
               ncol=3, frameon=False, fontsize=9.1, columnspacing=1.5,
               handlelength=2.2, handletextpad=.5, borderaxespad=0)
    fig.text(.016, .521, '对数分解项', ha='center', va='center', rotation=90, fontsize=9.2)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for title, intended_x in titles:
        bounds = title.get_window_extent(renderer)
        error_px = abs((bounds.x0+bounds.x1)/2 - intended_x*fig.bbox.width)
        assert error_px < .5
    result = style.save(fig, 'q2_mechanism', dimensions)
    after = style.sha(SOURCE)
    assert after == before
    result.update({'source': SOURCE.relative_to(ROOT).as_posix(),
                   'source_sha256_before': before, 'source_sha256_after': after,
                   'source_byte_unchanged': True,
                   'source_keys_used': ['time_s', 'radius_cm', 'profile_TC'],
                   'time_s': style.signature(t),
                   'sample_count': int(len(t)),
                   'window_s': [0, 10800],
                   'temperature_conversion': 'T_K = stored profile_TC[..., 0] + 273.15',
                   'moisture_definition': 'stored dry-basis C = profile_TC[..., 1]',
                   'formulas': {'H': '3850*(1/301.15-1/T_K)',
                                'M': '0.45*(1/2.55-1/C)',
                                'D': '2.4e-3*exp(-3850/T_K-0.45/C)',
                                'D0': '2.4e-3*exp(-3850/301.15-0.45/2.55)'},
                   'D0_unrounded_for_identity': float(D0),
                   'D0_display_rounded_existing_paper': '5.64168037e-9',
                   'max_abs_log_identity_residual': residual,
                   'panel_titles_centered_over_axes': True,
                   'panels': panel_checks,
                   'surface_initial_sample_minimum': {
                       'time_s': 144, 'D_over_D0': float(ratio[144, 1])},
                   'peak_scope': 'Maxima among saved one-second samples during 0-3 h, not certified continuous-time extrema.',
                   'interpretation_boundary': 'Algebraic contributions along the saved coupled trajectory, not independent causal percentages. The surface curve initially dips and H is not asserted monotonic.'})
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    style.configure()
    style.OUT = OUT
    plt.rcParams['svg.hashsalt'] = 'q2-revision-20260913'
    result = {
        'baseline_commit': BASELINE,
        'operation': 'Diagram redraw and frozen-array graphical postprocessing only.',
        'PDE_solvers_or_parameter_scenarios_run': False,
        'builder': Path(__file__).relative_to(ROOT).as_posix(),
        'runtime': {'python': sys.version, 'platform': platform.platform(),
                    'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
        'font_files': {name: font_manager.findfont(name, fallback_to_default=False)
                       for name in style.FAMILIES},
        'figures': {'q2_workflow': workflow(), 'q2_mechanism': mechanism()},
    }
    for name, metadata in result['figures'].items():
        with fitz.open(OUT / f'{name}.pdf') as document:
            fonts = document[0].get_fonts(full=True)
            metadata['pdf_fonts'] = [list(font) for font in fonts]
            assert any('SimSun' in font[3] for font in fonts), fonts
            assert any('TimesNewRoman' in font[3] for font in fonts), fonts
            metadata['pdf_font_check'] = 'SimSun and Times New Roman embedded as Type0 font subsets.'
            assert len(document) == 1
    result['builder_sha256'] = style.sha(__file__)
    (EVIDENCE / 'figure_provenance.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'outputs': list(result['figures']),
                      'source_unchanged': result['figures']['q2_mechanism']['source_byte_unchanged'],
                      'max_log_identity_residual': result['figures']['q2_mechanism']['max_abs_log_identity_residual']},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
