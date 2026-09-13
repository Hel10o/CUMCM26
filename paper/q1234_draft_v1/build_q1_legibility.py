"""Enlarge Q1 heatmap typography using frozen arrays; no numerical solver runs."""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.patches import Rectangle
import build_ch6_assets as common

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/q1_legibility'
EVIDENCE = BASE / 'evidence/q1_legibility_20260913'
BASELINE = 'c516364c6934721b07c10533d9e878cff3db0aff'


def white_workflow():
    """Preserve existing Q1 workflow geometry/text, using white box interiors."""
    dimensions = [15.0, 3.2]
    fig, ax = common.canvas(*dimensions)
    common.label(ax, 7.5, 2.96, '统一传热传质模型 → 问题一条件与参数代入', size=9.6)
    specs = [
        (.15, .56, 2.65, 1.64, '几何与初态\n环境记录\n附录2物性'),
        (3.45, 1.76, 3.05, .84, '常热物性导热方程'),
        (3.45, .18, 3.05, .99, '非线性水分扩散\nD(C)'),
        (7.09, 1.70, 3.34, .96, '圆环有限体积\nBDF隐式积分'),
        (7.09, .19, 3.34, .97, '圆环有限体积\nBDF隐式积分'),
        (11.03, 1.70, 3.82, .96, '0–1800 s\n径向温度场'),
        (11.03, .19, 3.82, .97, '0–1800 s\n径向含水率场'),
    ]
    boxes = []
    for x, y, w, h, value in specs:
        box = Rectangle((x, y), w, h, edgecolor=common.LINE, facecolor='white', lw=.8, zorder=3)
        ax.add_patch(box)
        common.label(ax, x+w/2, y+h/2, value, size=9.2, linespacing=1.2)
        boxes.append(box)
    common.arrow(ax, [(2.8, 1.38), (3.13, 1.38), (3.13, 2.18), (3.45, 2.18)])
    common.arrow(ax, [(2.8, 1.38), (3.13, 1.38), (3.13, .675), (3.45, .675)])
    for y in (2.18, .675):
        common.arrow(ax, [(6.5, y), (7.09, y)])
        common.arrow(ax, [(10.43, y), (11.03, y)])
    assert all(box.get_facecolor() == (1., 1., 1., 1.) for box in boxes)
    result = common.save(fig, 'q1_workflow', dimensions)
    result.update({'box_count': len(boxes), 'all_box_interiors_white': True,
                   'geometry_text_arrows_and_fonts_preserved': True})
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    common.configure()
    plt.rcParams.update({'axes.labelsize': 11.3, 'xtick.labelsize': 11,
                         'ytick.labelsize': 11})
    data_path = ROOT / 'q1_complete_delivery/q1_delivery/output/q1_unrounded.npz'
    data_sha = common.sha(data_path)
    with np.load(data_path, allow_pickle=False) as z:
        data = {k: z[k].copy() for k in
                ('time_s', 'radius_cm', 'temperature_degC', 'moisture_dry_basis')}
    prior = json.loads((BASE / 'evidence/ch6_revision_20260913/figure_sources.json').read_text(encoding='utf-8'))['figures']['q1_profiles']
    dimensions = [16.4, 7.1]
    fig = plt.figure(figsize=(dimensions[0] / 2.54, dimensions[1] / 2.54))
    plots, titles, note_artists = [], [], []
    for col, (key, cmap, title, unit, lo, hi, ticks) in enumerate([
        ('temperature_degC', 'YlOrBr', '(a) 热响应的时空演化', '温度 / °C', 28, 37, [28, 31, 34, 37]),
        ('moisture_dry_basis', 'YlGnBu', '(b) 失水的时空演化', '干基含水率 / (kg/kg)', 1.5, 2.55, [1.5, 1.85, 2.2, 2.55]),
    ]):
        left, width = .092 + col * .49, .357
        center = left + width / 2
        ax = fig.add_axes([left, .290, width, .432])
        mesh = ax.pcolormesh(data['time_s'] / 60, data['radius_cm'], data[key].T,
                            shading='nearest', cmap=cmap, vmin=lo, vmax=hi,
                            rasterized=True, antialiased=False, edgecolors='none')
        ax.set(xlim=(0, 30), ylim=(0, 2), xlabel='时间 / min', ylabel='径向距离 / cm')
        ax.set_xticks([0, 10, 20, 30])
        ax.set_yticks([0, .5, 1, 1.5, 2])
        ax.spines[['top', 'right']].set_visible(False)
        for s in ax.spines.values():
            s.set_color('#74808A')
        ax.tick_params(direction='out', length=2.7, pad=2.7)
        ax.xaxis.labelpad = 3
        ax.yaxis.labelpad = 3
        for y, name in [(.93, '表面'), (.07, '轴心')]:
            ax.text(.025, y, name, transform=ax.transAxes, ha='left', va='center',
                    color=common.INK, fontsize=11,
                    bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .84, 'pad': 1.2})
        ca = fig.add_axes([left, .813, width, .026])
        cb = fig.colorbar(mesh, cax=ca, orientation='horizontal', ticks=ticks)
        cb.outline.set_visible(False)
        cb.ax.tick_params(length=2, pad=2, labelsize=11)
        if cb.solids is not None:
            cb.solids.set_rasterized(True)
        heading = fig.text(center, .956, title, fontsize=12.2, color=common.INK,
                           ha='center', va='center')
        legend = fig.text(center, .885, unit, fontsize=11.3, color=common.INK,
                          ha='center', va='center')
        titles.append((ax, heading, legend))
        old = prior['plots'][col]
        for y, value in zip([.099, .029], old['endpoint_texts']):
            # Center the unchanged endpoint strings within each half of the
            # canvas so the longer temperature line can use the side margins.
            note_artists.append(fig.text(.252 + col * .49, y, value,
                                        fontsize=11, color=common.INK,
                                        ha='center', va='center'))
        array, geometry = common.signature(mesh.get_array()), common.signature(mesh.get_coordinates())
        assert array == old['display_array']
        assert geometry == old['mesh_coordinates']
        assert [lo, hi] == old['colour_limits'] and cmap == old['cmap']
        plots.append({'key': key, 'source_array': common.signature(data[key]),
                      'display_array': array, 'mesh_coordinates': geometry,
                      'colour_limits': [lo, hi], 'cmap': cmap,
                      'endpoint_texts': old['endpoint_texts'],
                      'arrays_geometry_colours_text_equal_to_baseline': True})
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    centers = []
    for ax, heading, legend in titles:
        center = (ax.bbox.x0 + ax.bbox.x1) / 2
        for artist in (heading, legend):
            bounds = artist.get_window_extent(renderer)
            error = abs((bounds.x0 + bounds.x1) / 2 - center)
            assert error < .01
            centers.append({'text': artist.get_text(), 'horizontal_alignment': 'center',
                            'center_error_px': error})
    # Explicitly check same-row endpoint strings for collision.
    for a, b in [(note_artists[0], note_artists[2]), (note_artists[1], note_artists[3])]:
        assert a.get_window_extent(renderer).x1 < b.get_window_extent(renderer).x0
    font_sizes = sorted({a.get_fontsize() for a in fig.findobj(Text)
                         if a.get_visible() and a.get_text()})
    common.OUT = OUT
    output = common.save(fig, 'q1_profiles', dimensions)
    common.configure()
    workflow = white_workflow()
    assert common.sha(data_path) == data_sha
    record = {'baseline_commit': BASELINE, 'script_sha256': common.sha(__file__),
              'input_file': data_path.relative_to(ROOT).as_posix(),
              'input_sha256': data_sha, 'input_unchanged': True,
              'solver_runs': 0, 'plots': plots, 'title_alignment_checks': centers,
              'font_sizes_pt': font_sizes,
              'font_contract': {'Chinese': 'SimSun', 'Latin_digits': 'Times New Roman'},
              'figure': output, 'workflow': workflow,
              'scope': 'Heatmap typography/text positions and workflow white box interiors only; exact canvas sizes, numerical arrays, grid, limits, colormaps, labels and endpoint strings preserved.'}
    (EVIDENCE / 'figure_check.json').write_bytes((json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'font_sizes_pt': font_sizes, 'title_centers_checked': len(centers),
                      'data_unchanged': True, 'output': str(OUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
