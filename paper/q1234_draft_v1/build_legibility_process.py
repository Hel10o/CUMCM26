"""Enlarge figures 8 and 10 from frozen arrays; preserve data and wording.

The accepted geometry drawing module is reused. Only font sizes, text wrapping,
legend placement and axes layout are adjusted before saving new assets.
"""
from pathlib import Path
import copy
import json
import re

import matplotlib.pyplot as plt
from matplotlib.text import Text
import build_font_assets as fonts

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/legibility_process'
EVIDENCE = BASE / 'evidence/figure_legibility_20260913/process'
BASELINE = '4f09fdad4182b6f220e801af54dffd0be37ad04c'
WIDTHS_CM = {'q3_q4_drying': 13.95, 'q4_shrinkage': 13.8}


def canonical_content(fig):
    result = fonts.content_signature(fig)
    for ax, artist in zip(result['axes'],fig.axes):
        ax.pop('bounds')
        if not artist.axison:
            ax.pop('xticks')
            ax.pop('yticks')
    result['texts'] = sorted(re.sub(r'\s+', '', t['text']) for t in result['texts'])
    result.pop('anchors')
    return result


def common_sizes(fig):
    for text in fig.findobj(Text):
        text.set_fontsize(11.4)
    for ax in fig.axes:
        ax.xaxis.label.set_fontsize(11.55)
        ax.yaxis.label.set_fontsize(11.55)
        ax.title.set_fontsize(12.5)
        ax.tick_params(labelsize=11.4, pad=2.5)
    fonts.apply_fonts(fig)


def process_layout(fig):
    left, right, ruler_left, ruler_right = fig.axes
    for ax, x in [(left, .115), (right, .620)]:
        ax.set_position([x, .485, .345, .29])
        ax.xaxis.labelpad = 2
        ax.yaxis.labelpad = 3
        for text in ax.texts:
            if text.get_text().endswith(' h'):
                old = text.get_position()
                text.set_position((old[0]-5, .265))
    for ruler, x in [(ruler_left, .115), (ruler_right, .620)]:
        ruler.set_position([x, .288, .345, .036])
        for text in ruler.texts:
            text.set_text(text.get_text().replace('：', '：\n'))
            text.set_position((text.get_position()[0], -.68))
            text.set_va('top')
            text.set_linespacing(1.08)
    for text in fig.texts:
        value = text.get_text()
        if value.startswith('(a)') or value.startswith('(b)'):
            text.set_position((.2875 if value.startswith('(a)') else .7925, .81))
            text.set_fontsize(12.35)
        elif value.startswith('物性不同'):
            text.set_position((.54, .985))
            text.set_fontsize(12.35)
        elif value.startswith('执行最大值'):
            text.set_text(value.replace('执行最大值 ', '执行最大值\n'))
            text.set_position((.2875 if text.get_position()[0] < .5 else .7925, .087))
            text.set_ha('center')
            text.set_linespacing(1.05)
        elif value.startswith('下方仅'):
            text.set_position((.51, .012))
    legend = fig.legends[0]
    legend.set_bbox_to_anchor((.54, .905))


def shrinkage_layout(fig):
    fig.set_size_inches(16.4/2.54, 10.6/2.54)
    top, cax, profiles, comparison = fig.axes
    top.set_position([.105, .61, .76, .23])
    cax.set_position([.90, .61, .018, .23])
    top.xaxis.labelpad = 2
    top.yaxis.labelpad = 3
    top.title.set_position((.53, 1.33))
    top.get_legend().set_bbox_to_anchor((.52, 1.18))
    top.get_legend()._legend_box.sep = 8
    for text in top.texts:
        value = text.get_text()
        if value == '材料域外':
            text.set_position((19, 1.53))
        elif value == '仅观测半径':
            text.set_position((61, .63))
        elif value.startswith('执行 '):
            text.set_position((35, 1.53))
    cax.set_title('C / (kg/kg)\n对数色标', fontsize=11.4, pad=8)
    profiles.set_position([.105, .215, .455, .18])
    profiles.xaxis.labelpad = 2
    profiles.yaxis.labelpad = 3
    profiles.set_title('(b) 曲线止于各时刻的材料表面', fontsize=12.5, pad=0, y=1.34)
    handles, labels = profiles.get_legend_handles_labels()
    profiles.get_legend().remove()
    profiles.legend(handles, labels, loc='upper left', bbox_to_anchor=(-.015,1.29),
                    ncol=4, frameon=False, fontsize=11.4, columnspacing=.75,
                    handlelength=1.2, handletextpad=.45, borderaxespad=0)
    for text in profiles.texts:
        if text.get_text() == '0.15':
            text.set_position((1.47, .15))
            text.set_ha('left')
            text.set_va('center')
    comparison.set_position([.69, .255, .27, .16])
    comparison.xaxis.labelpad = 2
    for text in comparison.texts:
        value = text.get_text()
        text.set_position((0, 2))
        text.set_fontsize(11.4)
        text.set_linespacing(1.05)
    for text in fig.texts:
        value = text.get_text()
        if value.startswith('(c)'):
            text.set_text(value.replace(' 同物性', '\n同物性'))
            text.set_position((.825, .455))
            text.set_fontsize(12.5)
            text.set_linespacing(1.05)
        elif value.startswith('临界时间差'):
            text.set_position((.105, .069))
        elif value.startswith('模型临界时间缩短'):
            text.set_position((.57, .069))
            text.set_linespacing(1.05)
        elif value.startswith('条件对照包含'):
            text.set_position((.105, .017))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    common = fonts.load_module('common', BASE / 'visual_refinement/common.py')
    common.OUT, common.EVIDENCE, common.BASELINE = OUT, EVIDENCE, BASELINE
    original_save = common.Evidence.save
    records = {}

    def save(evidence, fig, name):
        fig.canvas.draw()
        before = copy.deepcopy(canonical_content(fig))
        before.pop('size_inches')
        before_fonts = [t.get_fontsize() for t in fig.findobj(Text) if t.get_text() and t.get_visible()]
        common_sizes(fig)
        (process_layout if name == 'q3_q4_drying' else shrinkage_layout)(fig)
        fonts.apply_fonts(fig)
        fig.canvas.draw()
        after = canonical_content(fig)
        after.pop('size_inches')
        assert before == after, f'Data or wording changed in {name}'
        renderer = fig.canvas.get_renderer()
        outside = []
        for text in fig.findobj(Text):
            if not text.get_visible() or not text.get_text():
                continue
            box = text.get_window_extent(renderer)
            if box.x0 < -.5 or box.y0 < -.5 or box.x1 > fig.bbox.width+.5 or box.y1 > fig.bbox.height+.5:
                outside.append({'text':text.get_text(),'bounds':list(box.bounds)})
        ratio = WIDTHS_CM[name] / 16.4
        assert not outside, f'Text extends outside canvas in {name}: {outside}'
        after_fonts = [t.get_fontsize() for t in fig.findobj(Text) if t.get_text() and t.get_visible()]
        records[name] = {
            'baseline_pdf': f'figures/font_revision/{name}.pdf',
            'baseline_pdf_sha256': fonts.sha(BASE/f'figures/font_revision/{name}.pdf'),
            'canvas_size_cm': (fig.get_size_inches()*2.54).tolist(),
            'original_canvas_size_cm': [16.4, 8.0 if name=='q3_q4_drying' else 9.2],
            'insertion_width_cm': WIDTHS_CM[name],
            'previous_visible_source_font_min_pt': min(before_fonts),
            'visible_source_font_min_pt': min(after_fonts),
            'visible_actual_font_min_pt': min(after_fonts)*ratio,
            'visible_actual_font_max_pt': max(after_fonts)*ratio,
            'data_axes_ranges_ticks_and_wording_unchanged': before == after,
            'canonical_content': after,
            'outside_canvas_texts': outside,
            'layout_adjustments': 'Font enlargement; moved axes, legends and annotations; inserted line breaks only. No deleted text, data samples, plotted lines or numerical results.',
        }
        original_save(evidence, fig, name)

    common.Evidence.save = save
    module = fonts.load_module('legibility_process_geometry', BASE/'visual_refinement/geometry.py')
    module.main()
    evidence = json.loads((EVIDENCE/'geometry_sources.json').read_text(encoding='utf-8'))
    evidence['font_wrapper'] = {'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':fonts.sha(__file__)}
    evidence['figures'] = records
    evidence['font_policy'] = {'chinese':'SimSun','latin_and_digits':'Times New Roman',
        'reference':'Figure 3 actual main text approximately 9.46-10.49 pt'}
    (EVIDENCE/'legibility_process_check.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:{x:v[x] for x in ['visible_actual_font_min_pt','visible_actual_font_max_pt','outside_canvas_texts']} for k,v in records.items()},ensure_ascii=False))


if __name__ == '__main__':
    main()
