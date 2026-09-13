"""Q2 temperature/moisture field heatmaps from immutable saved samples.

Only graphics are generated. No PDE solver, numerical time integrator, fitting,
or parameter-scenario code is imported or run. Radial interpolation is solely
for the displayed heatmap, and original samples are neither changed nor saved.
"""
from pathlib import Path
import json
import platform
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import fitz

import build_ch6_assets as style

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/q2_heatmap'
EVIDENCE = BASE / 'evidence/q2_heatmap_20260913'
BASELINE = '1b84c827ae72353b37549715ff4da5513cc61ea1'
SOURCE = ROOT / 'q4_complete_delivery/v1/q123_closeout/output/q23_unified.npz'
EXPECTED_SHA = '80bd0a8ee77ac04189646a89e2dd78c2843344d9538923e402bef993b980c6f4'
OLD_FIGURE = BASE / 'figures/font_revision/q2_profiles.pdf'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    style.configure()
    style.OUT = OUT
    plt.rcParams.update({'font.size': 10.8, 'axes.labelsize': 10.8,
                         'xtick.labelsize': 10.2, 'ytick.labelsize': 10.2,
                         'svg.hashsalt': 'q2-heatmap-20260913'})
    before = style.sha(SOURCE)
    old_sha = style.sha(OLD_FIGURE)
    assert before == EXPECTED_SHA
    with np.load(SOURCE, allow_pickle=False) as archive:
        select = archive['time_s'] <= 10800
        t = archive['time_s'][select].copy()
        r = archive['radius_cm'].copy()
        samples = archive['profile_TC'][select].copy()
    assert np.array_equal(t, np.arange(10801, dtype=float))
    assert np.array_equal(r, np.linspace(0, 2, 21))
    assert samples.shape == (10801, 21, 2)

    # A linear display grid in r, with every original time sample retained.
    # The original r nodes are a subset of this grid and must agree exactly.
    display_r = np.linspace(0, 2, 101)
    display_r[::5] = r
    left_index = np.clip(np.searchsorted(r, display_r, side='right')-1, 0, len(r)-2)
    fraction = (display_r-r[left_index]) / (r[left_index+1]-r[left_index])
    display = (samples[:, left_index, :]*(1-fraction[None, :, None])
               + samples[:, left_index+1, :]*fraction[None, :, None])
    assert np.array_equal(display[:, ::5, :], samples)
    assert float(np.max(np.abs(display[:, ::5, :]-samples))) == 0.

    end = samples[-1, [0, -1], :]
    delta_T = float(end[1, 0]-end[0, 0])
    delta_C = float(end[0, 1]-end[1, 1])
    assert [f'{v:.4f}' for v in end[:, 0]] == ['49.8495', '49.9664']
    assert [f'{v:.4f}' for v in end[:, 1]] == ['1.7662', '1.0081']
    assert f'{delta_T:.4f}' == '0.1169' and f'{delta_C:.4f}' == '0.7581'

    dimensions = [16.4, 8.1]
    with fitz.open(OLD_FIGURE) as previous:
        old_dimensions = [previous[0].rect.width*2.54/72,
                          previous[0].rect.height*2.54/72]
    assert np.allclose(dimensions, old_dimensions, atol=1e-6, rtol=0)
    fig = plt.figure(figsize=(dimensions[0]/2.54, dimensions[1]/2.54))
    panel_data, aligned_titles, footers, contour_label_texts = [], [], [], []
    contour_label_axes_pairs = []
    specs = [
        {'component': 0, 'title': '(a) 径向温度场', 'unit': '温度 T / °C',
         'cmap': 'YlOrBr', 'clim': [28., 50.], 'ticks': [28, 36, 44, 50],
         'levels': [32., 40., 48.], 'color': ['#713C20', '#713C20', '#FFF2DB'],
         'positions': [(.50, .58), (1.00, 1.03), (1.84, 1.44)],
         'first_line': '3 h轴心 / 表面：49.8495 / 49.9664 °C',
         'second_line': '末时温差 ΔT = 0.1169 K'},
        {'component': 1, 'title': '(b) 径向干基含水率场',
         'unit': '干基含水率 C / (kg/kg)', 'cmap': 'YlGnBu',
         'clim': [1., 2.55], 'ticks': [1., 1.5, 2., 2.55],
         'levels': [1.2, 1.8, 2.4], 'color': ['#356177', '#E6F1F0', '#E6F1F0'],
         'positions': [(2.65, 1.81), (1.45, 1.02), (.62, .60)],
         'first_line': '3 h轴心 / 表面：1.7662 / 1.0081 kg/kg',
         'second_line': '末时含水率差 ΔC = 0.7581 kg/kg'},
    ]
    for col, spec in enumerate(specs):
        left, width = .078 + .492*col, .382
        ax = fig.add_axes([left, .275, width, .49])
        component = spec['component']
        grid = display[:, :, component].T
        mesh = ax.pcolormesh(t/3600, display_r, grid, shading='nearest',
                             cmap=spec['cmap'], vmin=spec['clim'][0],
                             vmax=spec['clim'][1], rasterized=True,
                             antialiased=False, edgecolors='none')
        assert np.array_equal(np.asarray(mesh.get_array()), grid)
        ax.set(xlim=(0, 3), ylim=(0, 2), xlabel='时间 t / h', ylabel='径向位置 r / cm')
        ax.set_xticks([0, 1, 2, 3])
        ax.set_yticks([0, 1, 2])
        ax.tick_params(direction='out', length=3, pad=3)
        ax.xaxis.labelpad = 4
        ax.yaxis.labelpad = 4
        for spine in ax.spines.values():
            spine.set_color('#6D7A80')
            spine.set_linewidth(.65)
        cs = ax.contour(t/3600, r, samples[:, :, component].T,
                        levels=spec['levels'], colors=spec['color'],
                        linewidths=.68)
        labels = []
        for level, position in zip(spec['levels'], spec['positions']):
            placed = ax.clabel(cs, levels=[level], inline=True,
                              inline_spacing=4, fontsize=10.2,
                              fmt=('%d' if component == 0 else '%.1f'),
                              manual=[position], rightside_up=True)
            labels.append(placed[-1])
        for lab in labels:
            lab.set_bbox({'facecolor': '#FFFFFF', 'edgecolor': 'none',
                          'alpha': .86, 'pad': .45})
            lab.set_color('#32434A')
            contour_label_texts.append(lab)
            contour_label_axes_pairs.append((lab, ax))
        for y, name in [(.94, '表面'), (.055, '轴心')]:
            ax.text(.027, y, name, transform=ax.transAxes, ha='left', va='center',
                    fontsize=10.4, color='#303C43',
                    bbox={'facecolor': 'white', 'edgecolor': 'none',
                          'alpha': .86, 'pad': 1.1})
        cax = fig.add_axes([left, .850, width, .024])
        cb = fig.colorbar(mesh, cax=cax, orientation='horizontal', ticks=spec['ticks'])
        cb.outline.set_visible(False)
        cb.ax.tick_params(length=2.3, pad=2.7, labelsize=10.2)
        if component == 1:
            cb.ax.set_xticklabels(['1.00', '1.50', '2.00', '2.55'])
        if cb.solids is not None:
            cb.solids.set_rasterized(True)
        title = fig.text(left+width/2, .957, spec['title'], ha='center', va='center',
                         fontsize=11.5)
        aligned_titles.append((title, left+width/2))
        fig.text(left, .905, spec['unit'], ha='left', va='center', fontsize=10.8)
        for y, key in [(.125, 'first_line'), (.060, 'second_line')]:
            text = fig.text(left+width/2, y, spec[key], ha='center', va='center',
                            fontsize=10.6)
            footers.append((text, left-.018, left+width+.018))
        panel_data.append({
            'title': spec['title'], 'stored_component': component,
            'stored_field': 'temperature_degC' if component == 0 else 'dry_basis_moisture_kg_per_kg',
            'source_samples': style.signature(samples[:, :, component]),
            'heatmap_array': style.signature(grid),
            'mesh_coordinates': style.signature(mesh.get_coordinates()),
            'all_10801_saved_time_samples_used': True,
            'source_radius_count': 21, 'display_radius_count': 101,
            'original_radial_nodes_exactly_preserved': True,
            'cmap': spec['cmap'], 'colour_limits': spec['clim'],
            'colourbar_ticks': spec['ticks'],
            'contour_levels': spec['levels'],
            'contour_colours': spec['color'],
            'contour_source': 'Original 10801 x 21 saved samples; Matplotlib linearly interpolates contour crossings within the sample grid.',
            'displayed_contour_labels': [lab.get_text() for lab in labels],
            'contour_paths': [style.signature(path.vertices) for path in cs.get_paths()],
            'annotations': [spec['first_line'], spec['second_line']],
        })
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for title, expected_x in aligned_titles:
        box = title.get_window_extent(renderer)
        assert abs((box.x0+box.x1)/2-expected_x*fig.bbox.width) < .5
    for text, xmin, xmax in footers:
        box = text.get_window_extent(renderer)
        assert box.x0 >= xmin*fig.bbox.width and box.x1 <= xmax*fig.bbox.width, (text.get_text(), box.bounds)
    label_boxes = [label.get_window_extent(renderer) for label in contour_label_texts]
    for label, ax in contour_label_axes_pairs:
        box = label.get_window_extent(renderer)
        frame = ax.get_window_extent(renderer)
        assert box.x0 > frame.x0 and box.x1 < frame.x1 and box.y0 > frame.y0 and box.y1 < frame.y1, label.get_text()
    for first in range(len(label_boxes)):
        for second in range(first+1, len(label_boxes)):
            assert not label_boxes[first].overlaps(label_boxes[second]), (first, second)
    result = style.save(fig, 'q2_fields', dimensions)
    after = style.sha(SOURCE)
    assert after == before
    assert style.sha(OLD_FIGURE) == old_sha
    with fitz.open(OUT / 'q2_fields.pdf') as document:
        fonts = document[0].get_fonts(full=True)
        assert any('SimSun' in font[3] for font in fonts)
        assert any('TimesNewRoman' in font[3] for font in fonts)
        pdf_fonts = [list(font) for font in fonts]
    result.update({
        'baseline_commit': BASELINE,
        'builder': Path(__file__).relative_to(ROOT).as_posix(),
        'builder_sha256': style.sha(__file__),
        'source': SOURCE.relative_to(ROOT).as_posix(),
        'source_sha256_before': before, 'source_sha256_after': after,
        'source_byte_unchanged': True,
        'source_keys': ['time_s', 'radius_cm', 'profile_TC'],
        'source_time_s': style.signature(t), 'source_radius_cm': style.signature(r),
        'display_radius_cm': style.signature(display_r),
        'source_shape': list(samples.shape), 'time_window_s': [0, 10800],
        'display_transformation': 'All saved one-second times retained; linear interpolation along radius from 21 to 101 nodes only for displayed colour fields. The original 21 radii remain identical. No time interpolation, smoothing, PDE solve, or source write. Nearest-colour cells on the fine display grid are rasterized at 600 dpi; contours use the original sample grid.',
        'contour_scope': 'Display guides interpolated between saved samples, not rigorous threshold boundaries or new numerical field solutions.',
        'endpoint_values_3h': {'axis_T_degC': float(end[0, 0]), 'surface_T_degC': float(end[1, 0]),
                             'axis_C_kg_per_kg': float(end[0, 1]), 'surface_C_kg_per_kg': float(end[1, 1]),
                             'surface_minus_axis_T_K': delta_T, 'axis_minus_surface_C_kg_per_kg': delta_C},
        'panels': panel_data,
        'old_figure': OLD_FIGURE.relative_to(ROOT).as_posix(),
        'old_figure_sha256_unchanged': old_sha,
        'old_dimensions_cm': old_dimensions,
        'same_dimensions_as_replaced_figure': True,
        'panel_titles_centered_over_axes': True,
        'contour_label_pair_overlap_check': 'No pairwise label overlap.',
        'contour_labels_inside_own_axes': True,
        'font_files': {name: font_manager.findfont(name, fallback_to_default=False)
                       for name in style.FAMILIES},
        'pdf_fonts': pdf_fonts,
        'pdf_font_check': 'SimSun and Times New Roman are embedded Type0 subsets.',
        'source_font_sizes_pt': {'panel_titles': 11.5, 'axes_and_units': 10.8,
                                 'endpoint_annotations': 10.6, 'axis_surface_tags': 10.4,
                                 'ticks_and_contour_labels': 10.2},
        'intended_tex_width_cm': 14.1,
        'minimum_final_font_size_pt_at_intended_width': 10.2*14.1/16.4,
        'PDE_solvers_or_parameter_scenarios_run': False,
        'runtime': {'python': sys.version, 'numpy': np.__version__,
                    'matplotlib': matplotlib.__version__, 'platform': platform.platform()},
    })
    (EVIDENCE / 'figure_provenance.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'dimensions_cm': dimensions, 'source_unchanged': after == before,
                      'max_source_node_difference_after_display_interpolation': 0.,
                      'endpoint_annotations': [f'{delta_T:.4f}', f'{delta_C:.4f}']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
