"""Apply SimSun/Times typography to seven existing figures from frozen inputs.

Existing drawing modules are reused without editing their data or geometry.
Only font properties change immediately before saving to a new output directory.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text
import numpy as np

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/font_revision'
EVIDENCE = BASE / 'evidence/figure_fonts_20260912'
BASELINE = 'b314e2d0939623d68e916925582e73d18222e610'
FAMILIES = ['Times New Roman', 'SimSun']
GROUPS = [('visual_refinement', 'process'), ('visual_refinement', 'geometry'),
          ('visual_revision', 'validation'), ('workflow_spacing', 'workflow')]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def array_signature(values):
    values = np.ascontiguousarray(np.ma.filled(values, np.nan))
    return {'shape': list(values.shape), 'dtype': str(values.dtype),
            'sha256': hashlib.sha256(values.tobytes()).hexdigest()}


def content_signature(fig):
    """Record displayed strings and plotted values independent of glyph metrics."""
    axes = []
    for ax in fig.axes:
        collections = []
        for item in ax.collections:
            collections.append({
                'class': type(item).__name__,
                'array': None if item.get_array() is None else array_signature(item.get_array()),
                'offsets': array_signature(item.get_offsets()),
                'geometry': (array_signature(item.get_coordinates()) if hasattr(item, 'get_coordinates')
                             else [array_signature(p.vertices) for p in item.get_paths()]),
                'clim': item.get_clim(), 'cmap': item.get_cmap().name,
            })
        axes.append({'bounds': ax.get_position().bounds, 'xlim': ax.get_xlim(),
                     'ylim': ax.get_ylim(), 'xscale': ax.get_xscale(), 'yscale': ax.get_yscale(),
                     'xticks': ax.get_xticks().tolist(), 'yticks': ax.get_yticks().tolist(),
                     'lines': [array_signature(line.get_xydata()) for line in ax.lines],
                     'collections': collections})
    texts = [{'text': t.get_text(), 'size_pt': t.get_fontsize(),
              'weight': t.get_fontweight(),
              'rotation': t.get_rotation(), 'color': t.get_color()}
             for t in fig.findobj(Text) if t.get_text()]
    anchors = [{'text': t.get_text(), 'position': t.get_position()}
               for t in [*fig.texts, *(t for ax in fig.axes for t in ax.texts)]]
    return {'size_inches': fig.get_size_inches().tolist(), 'axes': axes, 'texts': texts, 'anchors': anchors}


def apply_fonts(fig):
    plt.rcParams.update({
        'font.family': FAMILIES, 'mathtext.fontset': 'custom',
        'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic',
        'mathtext.bf': 'Times New Roman:bold', 'mathtext.bfit': 'Times New Roman:bold:italic',
        'mathtext.sf': 'Times New Roman', 'mathtext.tt': 'Times New Roman',
        'mathtext.cal': 'Times New Roman:italic', 'mathtext.fallback': None,
    })
    for text in fig.findobj(Text):
        # Mathtext does not use the ordinary mixed-glyph fallback for outer CJK.
        # This existing title has only Chinese outside its dollar-delimited formula.
        mixed_math = '$' in text.get_text() and re.search(r'[\u4e00-\u9fff]', text.get_text())
        if mixed_math:
            outer = re.sub(r'\$[^$]*\$', '', text.get_text())
            assert not re.search(r'[A-Za-z0-9]', outer), text.get_text()
        text.set_fontfamily('SimSun' if mixed_math else FAMILIES)
        text.set_math_fontfamily('custom')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    font_files = {name: str(font_manager.findfont(name, fallback_to_default=False))
                  for name in FAMILIES}
    records = {}
    for directory, group in GROUPS:
        common = load_module('common', BASE / directory / 'common.py')
        common.OUT, common.EVIDENCE, common.BASELINE = OUT, EVIDENCE, BASELINE
        original_save = common.Evidence.save

        def save_with_fonts(evidence, fig, name, original_save=original_save, directory=directory):
            fig.canvas.draw()
            before = content_signature(fig)
            apply_fonts(fig)
            fig.canvas.draw()
            after = content_signature(fig)
            assert before == after, f'Non-font content changed: {name}'
            old = BASE / 'figures' / directory / (name + '.pdf')
            records[name] = {'prior_pdf': old.relative_to(BASE).as_posix(),
                             'prior_pdf_sha256': sha(old),
                             'font_only_content_check': True, 'content': after}
            original_save(evidence, fig, name)

        common.Evidence.save = save_with_fonts
        module = load_module('font_revision_' + group, BASE / directory / (group + '.py'))
        module.main()
        source_record = EVIDENCE / (group + '_sources.json')
        data = json.loads(source_record.read_text(encoding='utf-8'))
        data['font_wrapper'] = {'path': Path(__file__).relative_to(ROOT).as_posix(), 'sha256': sha(__file__)}
        data['details']['font'] = {'chinese': 'SimSun', 'latin_and_digits': 'Times New Roman',
                                   'mathtext': 'Times New Roman (custom regular/italic/bold)'}
        source_record.write_bytes(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    assert len(records) == 7
    result = {'baseline_commit': BASELINE, 'font_files': font_files,
              'font_file_sha256': {n: sha(p) for n, p in font_files.items()},
              'script_sha256': sha(__file__), 'figures': records,
              'scope': 'Saved inputs only. No solver or scenario execution. Text, values, positions, sizes and plot axes preserved.'}
    (EVIDENCE / 'font_content_check.json').write_bytes(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
    print('Seven figures saved with unchanged content and updated fonts.')


if __name__ == '__main__':
    main()
