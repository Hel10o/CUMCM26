"""New Q1 chapter figures: text diagrams and unchanged stored heatmap arrays.

This script is graphical postprocessing only. It never imports a solver, calls
an integrator, fits parameters, exports workbooks, or writes historical files.
"""
from pathlib import Path
import hashlib
import json
import platform
import subprocess

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from matplotlib.text import Text

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/ch6_revision'
EVIDENCE = BASE / 'evidence/ch6_revision_20260913'
BASELINE = '0b402a4b372c8f46cebc74abe0b63186a805d520'
FAMILIES = ['Times New Roman', 'SimSun']
INK = '#141414'
TEAL = '#175F72'
AMBER = '#AD6222'
GREY = '#454D52'
LINE = '#273D4A'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def signature(array):
    array = np.ascontiguousarray(np.ma.filled(array, np.nan))
    return {'shape': list(array.shape), 'dtype': str(array.dtype),
            'sha256': hashlib.sha256(array.tobytes()).hexdigest()}


def configure():
    plt.rcParams.update({
        'font.family': FAMILIES, 'font.size': 9.1,
        'mathtext.fontset': 'custom', 'mathtext.rm': 'Times New Roman',
        'mathtext.it': 'Times New Roman:italic', 'mathtext.bf': 'Times New Roman:bold',
        'mathtext.bfit': 'Times New Roman:bold:italic', 'mathtext.sf': 'Times New Roman',
        'mathtext.tt': 'Times New Roman', 'mathtext.cal': 'Times New Roman:italic',
        'mathtext.fallback': None, 'pdf.fonttype': 42, 'ps.fonttype': 42,
        'svg.fonttype': 'path', 'svg.hashsalt': 'q1-ch6-20260913',
        'axes.unicode_minus': False, 'axes.linewidth': .7,
        'axes.labelsize': 9.2, 'xtick.labelsize': 9.0, 'ytick.labelsize': 9.0,
        'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': INK,
        'ytick.color': INK, 'figure.facecolor': 'white',
    })


def canvas(width, height):
    fig = plt.figure(figsize=(width/2.54, height/2.54))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, width), ylim=(0, height))
    ax.axis('off')
    return fig, ax


def label(ax, x, y, value, size=9.1, ha='center', color=INK, **kwargs):
    return ax.text(x, y, value, fontsize=size, ha=ha, va='center',
                   color=color, zorder=5, **kwargs)


def arrow(ax, points, color=LINE, width=.9):
    points = np.asarray(points, dtype=float)
    ax.plot(points[:, 0], points[:, 1], lw=width, color=color, zorder=1)
    a, b = points[-2:]
    direction = (b-a)/np.linalg.norm(b-a)
    ax.add_patch(FancyArrowPatch(b-.24*direction, b, arrowstyle='-|>',
                                mutation_scale=9.2, lw=width, color=color,
                                shrinkA=0, shrinkB=0, zorder=2))


def save(fig, name, dimensions):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    checks = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text():
            continue
        b = t.get_window_extent(renderer)
        inside = (b.x0 >= -.5 and b.y0 >= -.5 and
                  b.x1 <= fig.bbox.width+.5 and b.y1 <= fig.bbox.height+.5)
        assert inside, (name, t.get_text(), b.bounds, fig.bbox.bounds)
        checks.append({'text': t.get_text(), 'font_pt': t.get_fontsize(),
                       'inside_canvas': bool(inside)})
    outputs = {}
    for ext in ('pdf', 'svg', 'png'):
        p = OUT / f'{name}.{ext}'
        opts = {'dpi': 600}
        if ext == 'pdf':
            opts['metadata'] = {'CreationDate': None, 'ModDate': None,
                                'Title': name, 'Creator': 'Matplotlib graphical postprocessing'}
        elif ext == 'svg':
            opts['metadata'] = {'Date': None}
        fig.savefig(p, **opts)
        outputs[p.relative_to(ROOT).as_posix()] = {'sha256': sha(p), 'bytes': p.stat().st_size}
    plt.close(fig)
    return {'dimensions_cm': dimensions, 'text_bounds_checks': checks, 'outputs': outputs}


def workflow():
    dimensions = [15.0, 3.2]
    fig, ax = canvas(*dimensions)
    label(ax, 7.5, 2.96, '统一传热传质模型 → 问题一条件与参数代入', size=9.6)
    specs = [
        ('input', .15, .56, 2.65, 1.64, '几何与初态\n环境记录\n附录2物性', '#F1F5FA'),
        ('heat', 3.45, 1.76, 3.05, .84, '常热物性导热方程', '#FCF4E9'),
        ('water', 3.45, .18, 3.05, .99, '非线性水分扩散\nD(C)', '#EEF6F8'),
        ('heat_method', 7.09, 1.70, 3.34, .96, '圆环有限体积\nBDF隐式积分', '#F4F6F8'),
        ('water_method', 7.09, .19, 3.34, .97, '圆环有限体积\nBDF隐式积分', '#F4F6F8'),
        ('heat_output', 11.03, 1.70, 3.82, .96, '0–1800 s\n径向温度场', '#FCF4E9'),
        ('water_output', 11.03, .19, 3.82, .97, '0–1800 s\n径向含水率场', '#EEF6F8'),
    ]
    texts = []
    for name, x, y, w, h, value, fill in specs:
        ax.add_patch(Rectangle((x, y), w, h, edgecolor=LINE, facecolor=fill,
                               lw=.8, zorder=3))
        t = label(ax, x+w/2, y+h/2, value, size=9.2, linespacing=1.2)
        texts.append((name, t, x, y, w, h))
    arrow(ax, [(2.8, 1.38), (3.13, 1.38), (3.13, 2.18), (3.45, 2.18)])
    arrow(ax, [(2.8, 1.38), (3.13, 1.38), (3.13, .675), (3.45, .675)])
    for y in (2.18, .675):
        arrow(ax, [(6.5, y), (7.09, y)])
        arrow(ax, [(10.43, y), (11.03, y)])
    fig.canvas.draw()
    fits = []
    for name, t, x, y, w, h in texts:
        b = t.get_window_extent(fig.canvas.get_renderer())
        a, c = ax.transData.transform([[x, y], [x+w, y+h]])
        ok = b.x0>a[0]+.5 and b.y0>a[1]+.5 and b.x1<c[0]-.5 and b.y1<c[1]-.5
        assert ok, (name, b.bounds, a, c)
        fits.append({'node': name, 'text_inside_node': bool(ok)})
    r = save(fig, 'q1_workflow', dimensions)
    r.update({'node_checks': fits,
              'semantics': 'Input conditions specialize the unified model. Thermal and nonlinear moisture branches are integrated independently; no T-to-C or C-to-T arrow.',
              'numerical_trajectory_displayed': False})
    return r


def boundary():
    dimensions = [15.0, 4.3]
    fig, ax = canvas(*dimensions)
    label(ax, 2.51, 4.01, '(a) 中截面与通量方向', size=9.6)
    label(ax, 10.16, 4.01, '(b) 径向区间与边界条件', size=9.6)
    center = np.array([2.51, 2.27])
    radius = 1.03
    ax.add_patch(Circle(center, radius, edgecolor=LINE, facecolor='#F5F8FA', lw=1))
    ax.plot(*center, 'o', ms=2.6, color=LINE)
    radial_end = center + radius*np.array([.62, .7846018098])
    arrow(ax, [center, radial_end], color=LINE, width=.8)
    label(ax, 3.27, 3.21, r'$r$', size=10)
    label(ax, 2.27, 3.47, r'$R=2\ \mathrm{cm}$', size=9.3)
    label(ax, 2.48, 1.86, '轴心', size=9.0)
    arrow(ax, [(.18, 2.23), (1.45, 2.23)], color=AMBER, width=1.15)
    label(ax, .80, 2.64, '热量传入', color=AMBER)
    label(ax, .81, 1.78, r'$T_s<T_a(t)$', color=AMBER, size=9.0)
    arrow(ax, [(3.57, 2.23), (4.91, 2.23)], color=TEAL, width=1.15)
    label(ax, 4.23, 2.64, '水分迁出', color=TEAL)
    label(ax, 4.23, 1.78, r'$C_s>b(t)$', color=TEAL, size=9.0)
    label(ax, 2.52, .61, '箭头示意本问预热工况', size=9.0, color=GREY)

    # r is positive outward. There is no nonzero flux through the axis.
    arrow(ax, [(5.82, 3.24), (14.43, 3.24)], color=LINE, width=.85)
    for x in (6.05, 13.90):
        ax.plot([x, x], [3.11, 3.37], lw=.9, color=LINE)
    label(ax, 10.0, 3.56, r'$0\leq r\leq R$', size=9.3)
    label(ax, 14.62, 3.24, r'$r$', size=9.3)
    label(ax, 6.05, 2.86, '轴心', size=9.0)
    label(ax, 13.90, 2.86, '表面', size=9.0)
    label(ax, 5.82, 2.30, '轴心：', ha='left', size=9.1)
    label(ax, 7.0, 2.30, r'$T_r(0,t)=C_r(0,t)=0$', ha='left', size=10.1)
    label(ax, 5.82, 1.72, '表面：', ha='left', size=9.1)
    label(ax, 7.0, 1.72, r'$-k\,T_r(R,t)=h_T\,[T_s-T_a(t)]$', ha='left', size=10.1)
    label(ax, 7.0, 1.12, r'$-D(C_s)\,C_r(R,t)=h_m\,[C_s-b(t)]$', ha='left', size=10.1)
    label(ax, 5.82, .44, r'$T_s=T(R,t),\quad C_s=C(R,t)$', ha='left', size=9.1)
    label(ax, 11.60, .44, r'$b(t)$', ha='left', size=9.1)
    label(ax, 12.21, .44, '：有效边界值', ha='left', size=9.0)
    r = save(fig, 'q1_boundary', dimensions)
    r.update({'semantics': 'Schematic radial midsection and one-dimensional outward r. Inward heat is conditional on Ts<Ta; outward water is conditional on Cs>b. Robin conditions are not forced unidirectional fluxes.',
              'mass_flux_units_added': False, 'b_description': 'effective boundary value, not measured equilibrium moisture or relative humidity',
              'geometry_is_schematic_not_to_scale': True})
    return r


def heatmaps(q1, old):
    dimensions = [16.4, 7.1]
    fig = plt.figure(figsize=(dimensions[0]/2.54, dimensions[1]/2.54))
    assert np.array_equal(q1['time_s'], np.arange(1801))
    assert q1['radius_cm'].shape == (21,)
    records = []
    end_texts = []
    for col, (key, cmap, title, unit, lo, hi, ticks) in enumerate([
        ('temperature_degC', 'YlOrBr', '(a) 热响应的时空演化', '温度 / °C', 28, 37, [28,31,34,37]),
        ('moisture_dry_basis', 'YlGnBu', '(b) 失水的时空演化', '干基含水率 / (kg/kg)', 1.5, 2.55, [1.5,1.85,2.2,2.55]),
    ]):
        left = .086 + col*.49
        width = .372
        ax = fig.add_axes([left, .267, width, .470])
        grid = q1[key].T
        mesh = ax.pcolormesh(q1['time_s']/60, q1['radius_cm'], grid,
                             shading='nearest', cmap=cmap, vmin=lo, vmax=hi,
                             rasterized=True, antialiased=False, edgecolors='none')
        ax.set(xlim=(0,30), ylim=(0,2), xlabel='时间 / min', ylabel='径向距离 / cm')
        ax.set_xticks([0,10,20,30])
        ax.set_yticks([0,.5,1,1.5,2])
        ax.spines[['top','right']].set_visible(False)
        for s in ax.spines.values():
            s.set_color('#74808A')
        ax.tick_params(direction='out', length=2.7, pad=2.7)
        for y, name in [(.955, '表面'), (.045, '轴心')]:
            ax.text(.02, y, name, transform=ax.transAxes, ha='left', va='center',
                     color=INK, fontsize=9.0,
                     bbox={'facecolor':'white', 'edgecolor':'none','alpha':.84,'pad':1.2})
        ca = fig.add_axes([left, .815, width, .025])
        cb = fig.colorbar(mesh, cax=ca, orientation='horizontal', ticks=ticks)
        cb.outline.set_visible(False)
        cb.ax.tick_params(length=2, pad=2, labelsize=9.0)
        # Rasterize dense nearest cells at 600 dpi to avoid PDF viewer seams;
        # text, tick marks, axes, labels and both schematic figures stay vector.
        if cb.solids is not None:
            cb.solids.set_rasterized(True)
        fig.text(left+width/2, .955, title, fontsize=9.6, color=INK, ha='center')
        fig.text(left, .884, unit, fontsize=9.0, color=INK)
        values = q1[key][-1,[0,-1]]
        if col == 0:
            delta = values[1]-values[0]
            assert [f'{v:.4f}' for v in values] == ['33.5753', '36.7856']
            assert f'{delta:.4f}' == '3.2102'
            lines = [f'末时轴心 / 表面：{values[0]:.4f} / {values[1]:.4f} °C',
                     f'径向温差 ΔT = {delta:.4f} K']
        else:
            assert f'{values[0]:.7f}' == '2.5499924' and f'{values[1]:.4f}' == '1.5102'
            lines = [f'末时轴心 ≈ {values[0]:.7f} kg/kg',
                     f'末时表面：{values[1]:.4f} kg/kg']
        for y, value in zip([.103, .030], lines):
            fig.text(left, y, value, fontsize=9.0, color=INK)
        end_texts.extend(lines)
        prior = old['content']['axes'][col*2]['collections'][0]
        sig = signature(mesh.get_array())
        geometry = signature(mesh.get_coordinates())
        assert sig == prior['array'], (key, sig, prior['array'])
        assert geometry == prior['geometry'], (key, geometry, prior['geometry'])
        assert [lo,hi] == prior['clim'] and cmap == prior['cmap']
        assert np.array_equal(np.asarray(mesh.get_array()), grid)
        records.append({'key': key, 'source_array': signature(q1[key]),
                        'display_array': sig, 'mesh_coordinates': geometry,
                        'array_equal_to_frozen_data': True,
                        'array_and_geometry_match_prior_figure_signature': True,
                        'colour_limits': [lo,hi], 'cmap': cmap,
                        'nearest_no_smoothing': True, 'all_1801_by_21_samples_used': True,
                        'endpoint_texts': lines})
    old_strings = [t['text'] for t in old['content']['texts']]
    assert all(t in old_strings for t in end_texts)
    result = save(fig, 'q1_profiles', dimensions)
    result.update({'plots': records, 'endpoint_strings_exactly_match_prior_figure': True,
                   'change_scope': 'Font sizes, darker text, centered titles and compact layout only; stored array values, nearest mesh coordinates, bounds, colormaps and endpoint text unchanged.',
                   'pdf_heatmap_and_colourbars_rasterized': True,
                   'raster_layer_dpi': 600, 'pdf_text_and_axes_vector': True,
                   'raster_reason': 'Avoid dense-cell PDF viewer hairline artifacts; preserves the original rasterized nearest-mesh method.'})
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    configure()
    names = {
        'q1_complete_delivery/q1_delivery/output/q1_unrounded.npz': 'Only numerical source for heatmaps.',
        'q1_complete_delivery/q1_delivery/source/q1_solver.py': 'Read-only source text for Q1 independent integrations and Robin signs.',
        'paper/q1234_draft_v1/build_question_workflows.py': 'Read-only prior diagram style; not executed.',
        'paper/q1234_draft_v1/visual_refinement/process.py': 'Read-only prior heatmap contract and endpoint wording; not executed.',
        'paper/q1234_draft_v1/build_font_assets.py': 'Read-only font convention; not executed.',
        'paper/q1234_draft_v1/evidence/figure_fonts_20260912/font_content_check.json': 'Frozen numerical signatures and endpoint strings of prior heatmap.',
    }
    sources = {name: {'sha256':sha(ROOT/name), 'purpose':purpose} for name,purpose in names.items()}
    for name in names:
        if name.endswith('.py'):
            (ROOT/name).read_text(encoding='utf-8')
    data_path = ROOT/'q1_complete_delivery/q1_delivery/output/q1_unrounded.npz'
    with np.load(data_path, allow_pickle=False) as z:
        q1 = {k:z[k].copy() for k in ('time_s','radius_cm','temperature_degC','moisture_dry_basis')}
    original_signatures = {k:signature(v) for k,v in q1.items()}
    old = json.loads((BASE/'evidence/figure_fonts_20260912/font_content_check.json').read_text(encoding='utf-8'))['figures']['q1_profiles']
    paper_records = {}
    for section in ('q1','problem_model'):
        name = f'paper/q1234_draft_v1/sections/{section}.tex'
        raw = subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)
        lines = raw.decode('utf-8').splitlines()
        terms = ('初态','初始','独立','分别','热物性','非线性','外法向','边界','环境','扩散')
        paper_records[name] = {'commit':BASELINE,'sha256':hashlib.sha256(raw).hexdigest(),
                              'excerpts':[{'line':i+1,'text':s} for i,s in enumerate(lines) if any(t in s for t in terms)]}
    records = {'q1_workflow':workflow(), 'q1_boundary':boundary(), 'q1_profiles':heatmaps(q1,old)}
    assert original_signatures == {k:signature(v) for k,v in q1.items()}
    assert all(sha(ROOT/p) == item['sha256'] for p,item in sources.items())
    fonts = {name:font_manager.findfont(name, fallback_to_default=False) for name in FAMILIES}
    record = {'baseline_commit':BASELINE, 'scope':'New Q1 diagrams and frozen-array heatmap only. No solver imports, PDE runs, scenarios or workbook exports.',
              'script':Path(__file__).relative_to(ROOT).as_posix(),'script_sha256':sha(__file__),
              'runtime':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
              'fonts':{name:{'font_file_sha256':sha(p),'resolved_file_name':Path(p).name} for name,p in fonts.items()},
              'font_contract':{'chinese':'SimSun','latin_and_digits':'Times New Roman','mathtext':'Times New Roman custom','pdf_type42_embedding':True},
              'sources':sources,'baseline_paper_sources':paper_records,
              'input_arrays':original_signatures,'input_files_unchanged':True,'input_arrays_unchanged':True,
              'figures':records,
              'visual_review':'See final supplemental fields added only after actual view_image review. The script does not claim a visual pass by itself.'}
    (EVIDENCE/'figure_sources.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'figures':3,'outputs':9,'frozen_inputs':len(sources),
                      'input_arrays_unchanged':True,'prior_heatmap_arrays_and_geometry_match':True}))


if __name__ == '__main__':
    main()
