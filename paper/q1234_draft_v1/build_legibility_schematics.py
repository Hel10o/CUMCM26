"""Enlarge four existing schematic figures without changing their content.

Only existing diagram functions/specifications are used. No data files,
numerical solvers, workbook exporters, or historical assets are modified.
"""
from pathlib import Path
import hashlib
import json
import platform
from collections import Counter

import fitz
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib import font_manager

import build_ch6_assets as style
import build_q1_legibility as q1
import build_q2_revision_assets as q2
import build_question_workflows as workflows

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/legibility_schematics'
EVIDENCE = BASE / 'evidence/figure_legibility_20260913/schematics'
BASELINE = '4f09fdad4182b6f220e801af54dffd0be37ad04c'
SOURCE_FIGURES = {
    'q1_workflow': 'figures/q1_legibility/q1_workflow.pdf',
    'q1_boundary': 'figures/ch6_revision/q1_boundary.pdf',
    'q2_workflow': 'figures/q2_revision/q2_workflow.pdf',
    'q4_workflow': 'figures/question_workflows/q4_workflow.pdf',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(builder):
    """Capture an old figure in memory; intercept its save, so no old writes."""
    captured = {}
    original_save = style.save
    def keep(fig, name, dimensions):
        captured.update(fig=fig, name=name, dimensions=dimensions)
        return {}
    try:
        style.save = keep
        builder()
    finally:
        style.save = original_save
    return captured


def q4_workflow(enlarge_input_boxes=False):
    """Use the current Q4 specification and the original connector function."""
    fig, ax = style.canvas(workflows.WIDTH, workflows.HEIGHT)
    spec = workflows.specifications()['q4_workflow']
    if enlarge_input_boxes:
        for node in spec['nodes']:
            if node['kind'] == 'input':
                node['w'], node['h'] = 2.90, 1.08
    nodes = {node['id']: node for node in spec['nodes']}
    for source, target, kind in spec['edges']:
        workflows.connect(ax, nodes[source], nodes[target], kind)
    for node in spec['nodes']:
        boxstyle = ('round,pad=0,rounding_size=0.42'
                    if node['kind'] == 'input' else 'square,pad=0')
        ax.add_patch(FancyBboxPatch(
            (node['x']-node['w']/2, node['y']-node['h']/2),
            node['w'], node['h'], boxstyle=boxstyle, lw=.8,
            edgecolor=workflows.LINE, facecolor='white', zorder=3))
        ax.text(node['x'], node['y'], node['text'], ha='center', va='center',
                fontsize=workflows.FONT_SIZE, linespacing=1.22,
                color=workflows.INK, zorder=4)
    return {'fig': fig, 'name': 'q4_workflow', 'dimensions': [15.0, 3.2],
            'specification': spec}


def content_signature(fig):
    """Excludes font sizes, includes every displayed string and diagram shape."""
    axes = []
    for ax in fig.axes:
        axes.append({
            'position': list(ax.get_position().bounds),
            'limits': [list(ax.get_xlim()), list(ax.get_ylim())],
            'lines': [
                {'xy': style.signature(line.get_xydata()),
                 'color': line.get_color(), 'width': line.get_linewidth(),
                 'marker': line.get_marker()}
                for line in ax.lines],
            'patches': [
                {'type': type(patch).__name__,
                 'path': style.signature(patch.get_path().vertices),
                 'transform': style.signature(patch.get_transform().get_matrix()),
                 'facecolor': list(patch.get_facecolor()),
                 'edgecolor': list(patch.get_edgecolor())}
                for patch in ax.patches],
        })
    texts = [
        {'text': item.get_text(), 'position': list(item.get_position()),
         'ha': item.get_ha(), 'va': item.get_va(), 'color': item.get_color(),
         'rotation': item.get_rotation()}
        for item in fig.findobj(Text) if item.get_visible() and item.get_text()]
    return {'canvas_inches': list(fig.get_size_inches()), 'axes': axes, 'texts': texts}


def node_checks(fig, name):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax = fig.axes[0]
    boxes = [patch for patch in ax.patches
             if isinstance(patch, (Rectangle, FancyBboxPatch))]
    if name == 'q1_boundary':
        return []
    texts = [item for item in ax.texts
             if item.get_text() and not item.get_text().startswith('统一传热传质模型')]
    assert len(boxes) == len(texts), (name, len(boxes), len(texts))
    checks = []
    for box, item in zip(boxes, texts):
        a = box.get_window_extent(renderer)
        b = item.get_window_extent(renderer)
        fits = (b.x0 > a.x0 + .5 and b.x1 < a.x1 - .5 and
                b.y0 > a.y0 + .5 and b.y1 < a.y1 - .5)
        assert fits, (name, item.get_text(), a.bounds, b.bounds)
        if isinstance(box, FancyBboxPatch):
            path = box.get_path().transformed(box.get_transform())
            corners = [(b.x0, b.y0), (b.x0, b.y1), (b.x1, b.y0), (b.x1, b.y1)]
            assert all(path.contains_point(point) for point in corners), (name, item.get_text())
        assert box.get_facecolor() == (1., 1., 1., 1.)
        checks.append({'text': item.get_text(), 'text_inside_node': bool(fits),
                       'node_facecolor': 'white',
                       'minimum_box_clearance_px': min(
                           b.x0-a.x0, a.x1-b.x1, b.y0-a.y0, a.y1-b.y1)})
    return checks


def text_spacing_check(fig):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = [item for item in fig.findobj(Text)
             if item.get_visible() and item.get_text()]
    checked = 0
    for index, first in enumerate(texts):
        a = first.get_window_extent(renderer)
        for second in texts[index+1:]:
            b = second.get_window_extent(renderer)
            overlap_x = min(a.x1, b.x1) - max(a.x0, b.x0)
            overlap_y = min(a.y1, b.y1) - max(a.y0, b.y0)
            assert overlap_x <= .2 or overlap_y <= .2, (
                first.get_text(), second.get_text(), overlap_x, overlap_y)
            checked += 1
    return {'text_pair_count': checked, 'no_text_bounding_box_overlap': True}


def pdf_stats(path):
    with fitz.open(path) as doc:
        page = doc[0]
        spans = [span for block in page.get_text('dict')['blocks']
                 for line in block.get('lines', []) for span in line.get('spans', [])
                 if span['text'].strip()]
        fonts = sorted({span['font'] for span in spans})
        assert any('SimSun' in name for name in fonts), fonts
        assert any('TimesNewRoman' in name for name in fonts), fonts
        return {
            'page_count': len(doc), 'page_size_pt': list(page.rect[2:]),
            'fonts': fonts,
            'font_size_pt_counts': dict(sorted(Counter(
                f"{span['size']:.4f}" for span in spans).items())),
            'spans': [{'text': span['text'], 'font': span['font'],
                       'size_pt': span['size']} for span in spans],
            'nonwhitespace_glyph_counts': dict(sorted(Counter(
                char for char in page.get_text() if not char.isspace()).items())),
        }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    files = [Path(module.__file__) for module in (style, q1, q2, workflows)]
    files += [BASE / path for path in SOURCE_FIGURES.values()]
    sources = {path.relative_to(ROOT).as_posix(): sha(path) for path in files}
    style.configure()
    plt.rcParams['svg.hashsalt'] = 'schematic-legibility-20260913'
    style.OUT = OUT
    records = {}
    builders = [lambda: capture(q1.white_workflow), lambda: capture(style.boundary),
                lambda: capture(q2.workflow), q4_workflow]
    for builder in builders:
        item = builder()
        fig, name = item['fig'], item['name']
        fig.canvas.draw()
        before = content_signature(fig)
        layout_adjustment = None
        if name == 'q4_workflow':
            old_spec = item['specification']
            plt.close(fig)
            item = q4_workflow(enlarge_input_boxes=True)
            fig = item['fig']
            assert old_spec['edges'] == item['specification']['edges']
            assert [node['text'] for node in old_spec['nodes']] == [
                node['text'] for node in item['specification']['nodes']]
            layout_adjustment = {
                'scope': 'Two rounded input boxes only: widths 2.80 to 2.90 cm, '
                         'heights 0.94 to 1.08 cm; outgoing connector starts follow box edges.',
                'node_centres_unchanged': True,
                'all_node_text_and_edge_topology_unchanged': True,
                'before': old_spec, 'after': item['specification'],
            }
        old_sizes = []
        new_sizes = []
        for text in fig.findobj(Text):
            if not text.get_visible() or not text.get_text():
                continue
            old_sizes.append(text.get_fontsize())
            heading = (text.get_text().startswith('统一传热传质模型') or
                       text.get_text().startswith('(a)') or
                       text.get_text().startswith('(b)'))
            equation = name == 'q1_boundary' and text.get_fontsize() == 10.1
            text.set_fontsize(10.5 if heading or equation else 10.0)
            text.set_fontfamily(style.FAMILIES)
            new_sizes.append(text.get_fontsize())
        checks = node_checks(fig, name)
        spacing = text_spacing_check(fig)
        after = content_signature(fig)
        if name != 'q4_workflow':
            assert before == after, name
        else:
            assert before['texts'] == after['texts']
            assert before['canvas_inches'] == after['canvas_inches']
        saved = style.save(fig, name, item['dimensions'])
        old_pdf = pdf_stats(BASE / SOURCE_FIGURES[name])
        new_pdf = pdf_stats(OUT / (name + '.pdf'))
        assert old_pdf['nonwhitespace_glyph_counts'] == new_pdf['nonwhitespace_glyph_counts']
        records[name] = {
            'prior_asset': SOURCE_FIGURES[name],
            'old_font_sizes_pt': sorted(set(old_sizes)),
            'new_font_sizes_pt': sorted(set(new_sizes)),
            'insertion_width_cm': 15,
            'actual_main_text_size_in_paper_pt': sorted(set(new_sizes)),
            'font_note': 'Natural mathematical subscripts retain the math font scale.',
            'content_and_geometry_before': before,
            'all_text_positions_colours_and_canvas_exactly_unchanged': True,
            'geometry_exactly_unchanged': name != 'q4_workflow',
            'layout_adjustment': layout_adjustment,
            'node_checks': checks,
            'text_spacing_check': spacing,
            'all_exported_pdf_text_characters_and_counts_unchanged': True,
            'old_pdf': old_pdf,
            'new_pdf': new_pdf,
            'output': saved,
        }
    assert sources == {path.relative_to(ROOT).as_posix(): sha(path) for path in files}
    record = {
        'baseline_commit': BASELINE,
        'scope': 'Font-size increase in existing figures 1, 2, 4 and 9. '
                 'Canvas dimensions, text, arrow topology and colours unchanged. '
                 'Only Q4 rounded input boxes are slightly enlarged to maintain inner padding.',
        'builder': Path(__file__).relative_to(ROOT).as_posix(),
        'builder_sha256': sha(__file__),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'font_contract': {'Chinese': 'SimSun', 'Latin_and_digits': 'Times New Roman'},
        'font_files': {name: font_manager.findfont(name, fallback_to_default=False)
                       for name in style.FAMILIES},
        'source_hashes': sources, 'source_files_byte_unchanged': True,
        'numerical_data_files_read': 0, 'PDE_or_scenario_runs': 0,
        'figures': records,
        'visual_review': 'Not implied by script assertions; recorded separately after viewing.',
    }
    (EVIDENCE / 'schematic_font_check.json').write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'figures': list(records), 'content_unchanged': True,
                      'main_font_sizes_pt': [10, 10.5]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
