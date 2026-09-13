"""Draw the Q3 introductory workflow from committed paper text only.

The two-row layout follows the user's screenshot. Its repeated placeholder
labels are not used. No numerical arrays, PDE solvers, integrators, or parameter
scenarios are read or executed.
"""
from pathlib import Path
import copy
import hashlib
import json
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
import fitz

import build_ch6_assets as style
import build_question_workflows as original

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/q3_intro'
EVIDENCE = BASE / 'evidence/q3_intro_workflow_20260913'
BASELINE = '2206ae259332121e6392f0543fe8e7759595912f'
SOURCE_PATH = 'paper/q1234_draft_v1/sections/q3.tex'
REFERENCE = Path('C:/Users/libai/AppData/Local/Temp/codex-clipboard-1cfa6cb9-e87b-42c5-b7c8-a8795bc42d92.png')
WIDTH, HEIGHT = 15.0, 3.2
FONT_SIZE = 10.0
LINE_SPACING = 1.18


def committed_source():
    raw = subprocess.check_output(['git', 'show', BASELINE+':'+SOURCE_PATH], cwd=ROOT)
    text = raw.decode('utf-8')
    lines = text.splitlines()
    anchors = [
        ('shared_trajectory_and_threshold', '问题三要求药材各处的干基含水率严格低于', 15),
        ('node_crossing_then_radial_reconstruction', '实际程序先以内部节点事件', 7),
        ('empirical_margin_and_upward_selection', '一维模型的临界根为', 24),
        ('scope_of_margin', '这里的经验余量用于当前方程的数值选择', 3),
        ('radial_output_and_independent_checks', '完整的\\texttt{result3.xlsx}', 10),
    ]
    excerpts = []
    for name, anchor, count in anchors:
        candidates = [i for i, line in enumerate(lines) if anchor in line]
        assert len(candidates) == 1, (name, candidates)
        start = candidates[0]
        excerpts.append({'purpose': name, 'start_line': start+1,
                         'end_line': min(start+count, len(lines)),
                         'text': '\n'.join(lines[start:start+count])})
    assert '57.4741' in text and '0.15\\unit{kg/kg}' in text
    return {'commit': BASELINE, 'path': SOURCE_PATH,
            'sha256': hashlib.sha256(raw).hexdigest(), 'excerpts': excerpts}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    source = committed_source()
    style.configure()
    style.OUT = OUT
    plt.rcParams['svg.hashsalt'] = 'q3-intro-workflow-20260913'
    specification = copy.deepcopy(original.specifications()['q3_workflow'])
    expected_edges = [('trajectory', 'candidate', 'direct'),
                      ('candidate', 'root', 'direct'),
                      ('checks', 'margin', 'direct'),
                      ('margin', 'execution', 'direct'),
                      ('root', 'execution', 'down'),
                      ('execution', 'output', 'merge')]
    assert specification['edges'] == expected_edges
    fills = {'trajectory': '#F8DDE2', 'candidate': '#DFEEF5', 'root': '#E1F0D8',
             'checks': '#F1BAC5', 'margin': '#BFE3F0', 'execution': '#C2E4AD',
             'output': '#FFF3CC'}
    letters = {'trajectory': 'A', 'candidate': 'B', 'root': 'C', 'checks': 'D',
               'margin': 'E', 'execution': 'F', 'output': 'G'}
    for node in specification['nodes']:
        node['h'] = 1.55 if node['id'] == 'output' else 1.06
        node['fill'] = fills[node['id']]
        node['reference_letter'] = letters[node['id']]
    nodes = {node['id']: node for node in specification['nodes']}
    assert len(nodes) == 7
    assert [src for src, dst, _ in expected_edges if dst == 'output'] == ['execution']
    fig, ax = style.canvas(WIDTH, HEIGHT)
    edges = []
    for src, dst, kind in expected_edges:
        points = original.connect(ax, nodes[src], nodes[dst], kind)
        edges.append({'from': src, 'to': dst,
                      'from_letter': letters[src], 'to_letter': letters[dst],
                      'kind': kind, 'points': points})
    texts = []
    for node in specification['nodes']:
        x, y, w, h = node['x'], node['y'], node['w'], node['h']
        ax.add_patch(Rectangle((x-w/2, y-h/2), w, h, facecolor=node['fill'],
                               edgecolor='#263C4C', lw=.85, zorder=3))
        t = ax.text(x, y, node['text'], ha='center', va='center', fontsize=FONT_SIZE,
                    linespacing=LINE_SPACING, color='#101820', zorder=4)
        texts.append((node, t))
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    checks = []
    for node, text in texts:
        b = text.get_window_extent(renderer)
        a, c = ax.transData.transform([(node['x']-node['w']/2, node['y']-node['h']/2),
                                      (node['x']+node['w']/2, node['y']+node['h']/2)])
        inside = bool(b.x0 >= a[0]+1 and b.x1 <= c[0]-1 and
                      b.y0 >= a[1]+1 and b.y1 <= c[1]-1)
        assert inside, (node['id'], node['text'], b.bounds, a, c)
        centered = bool(abs((b.x0+b.x1)/2-(a[0]+c[0])/2) < .5)
        assert centered
        checks.append({'node': node['id'], 'text_inside_node': inside,
                       'text_centered': centered, 'font_pt': FONT_SIZE,
                       'line_spacing': LINE_SPACING,
                       'text_width_px': float(b.width), 'text_height_px': float(b.height),
                       'node_width_px': float(c[0]-a[0]), 'node_height_px': float(c[1]-a[1])})
    result = style.save(fig, 'q3_workflow', [WIDTH, HEIGHT])
    with fitz.open(OUT / 'q3_workflow.pdf') as document:
        fonts = document[0].get_fonts(full=True)
        assert any('SimSun' in font[3] for font in fonts)
        assert any('TimesNewRoman' in font[3] for font in fonts)
        assert len(document) == 1
        pdf_fonts = [list(font) for font in fonts]
    result.update({
        'baseline_commit': BASELINE, 'source': source,
        'script': Path(__file__).relative_to(ROOT).as_posix(),
        'script_sha256': style.sha(__file__),
        'reused_layout_builder': {'path': 'paper/q1234_draft_v1/build_question_workflows.py',
                                  'sha256': style.sha(BASE / 'build_question_workflows.py'),
                                  'used': 'Q3 specification, node columns and centers, and six-edge connector implementation.'},
        'style_helper': {'path': 'paper/q1234_draft_v1/build_ch6_assets.py',
                         'sha256': style.sha(BASE / 'build_ch6_assets.py'),
                         'used': 'Font configuration, canvas, text-bounds verification, deterministic vector/PDF/PNG save.'},
        'font_size_pt': FONT_SIZE, 'line_spacing': LINE_SPACING,
        'fonts': {name: font_manager.findfont(name, fallback_to_default=False)
                  for name in style.FAMILIES},
        'pdf_fonts': pdf_fonts,
        'pdf_font_check': 'SimSun and Times New Roman embedded as Type0 font subsets.',
        'nodes': specification['nodes'], 'edges': edges, 'node_text_checks': checks,
        'only_execution_point_feeds_output': True,
        'meaning': specification['meaning'],
        'scope': 'Schematic of the existing one-dimensional event procedure. Empirical margin is not an experimental safety bound or a strict error bound. The final node reports the existing model time and radial output.',
        'no_numerical_array_reads': True,
        'PDE_solvers_integrators_or_parameter_scenarios_run': False,
        'reference_image': {'path': str(REFERENCE),
                            'sha256': style.sha(REFERENCE) if REFERENCE.exists() else None,
                            'adopted': 'Two rows of three pastel rectangular nodes merging into a pale-yellow final node.',
                            'not_adopted': 'Repeated placeholder text; actual labels and edges come from committed Q3 text.'},
    })
    (EVIDENCE / 'workflow_sources.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Q3 workflow generated: 7 nodes, 6 edges; 10 pt labels fit; no numerical data or solvers accessed.')


if __name__ == '__main__':
    main()
