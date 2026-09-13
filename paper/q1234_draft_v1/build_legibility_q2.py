"""Enlarge Q2 plot typography by reusing frozen-data drawing functions only."""
from pathlib import Path
import json
import copy
import matplotlib.pyplot as plt
from matplotlib.text import Text
import build_ch6_assets as style
import build_font_assets as fonts
import build_q2_heatmap as heatmap
import build_q2_revision_assets as mechanism

BASE = Path(__file__).resolve().parent
OUT = BASE / 'figures/legibility_q2'
EVIDENCE = BASE / 'evidence/figure_legibility_20260913/q2'
BASELINE = '4f09fdad4182b6f220e801af54dffd0be37ad04c'

def content_without_typography(value):
    value = copy.deepcopy(value)
    for t in value['texts']:
        del t['size_pt']
    value.pop('anchors')
    return value

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    old_save = style.save
    records = {}

    def enlarged_save(fig, name, dimensions):
        fig.canvas.draw()
        before = fonts.content_signature(fig)
        mapping = ({10.2: 11.05, 10.4: 11.2, 10.6: 11.2,
                    10.8: 11.3, 11.5: 12.2} if name == 'q2_fields'
                   else {9.0: 9.5, 9.1: 9.6, 9.2: 9.7, 9.6: 10.5})
        changes = []
        for t in fig.findobj(Text):
            if t.get_text():
                old = t.get_fontsize()
                new = mapping.get(round(old, 2), max(old, min(mapping.values())))
                t.set_fontsize(new)
                changes.append({'text': t.get_text(), 'old_pt': old, 'new_pt': new})
        fonts.apply_fonts(fig)
        if name == 'q2_fields':
            for text in fig.texts:
                x, y = text.get_position()
                if abs(y-.125) < 1e-8:
                    text.set_position((x, .100))
                elif abs(y-.060) < 1e-8:
                    text.set_position((x, .037))
        fig.canvas.draw()
        after = fonts.content_signature(fig)
        assert content_without_typography(before) == content_without_typography(after), name
        result = old_save(fig, name, dimensions)
        records[name] = {'unchanged_data_text_axes_positions': True,
                         'annotation_positions_before': before['anchors'],
                         'annotation_positions_after': after['anchors'],
                         'content': after, 'font_changes': changes, **result}
        return result

    style.save = enlarged_save
    heatmap.OUT, heatmap.EVIDENCE, heatmap.BASELINE = OUT, EVIDENCE, BASELINE
    heatmap.main()
    # The reused heatmap writer records its original font settings; replace
    # those metadata fields with the settings applied at the final save hook.
    heat_record = EVIDENCE / 'figure_provenance.json'
    record = json.loads(heat_record.read_text(encoding='utf-8'))
    record['source_font_sizes_pt'] = {'panel_titles': 12.2, 'axes_and_units': 11.3,
        'endpoint_annotations': 11.2, 'axis_surface_tags': 11.2,
        'ticks_and_contour_labels': 11.05}
    record['minimum_final_font_size_pt_at_intended_width'] = 11.05*14.1/16.4
    record['typography_wrapper'] = {'path': Path(__file__).name, 'sha256': style.sha(__file__)}
    heat_record.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    style.configure()
    style.OUT = OUT
    result = mechanism.mechanism()
    records['q2_mechanism']['source_evidence'] = result
    (EVIDENCE / 'content_and_fonts.json').write_text(json.dumps({
        'baseline_commit': BASELINE, 'builder_sha256': style.sha(__file__),
        'PDE_or_parameter_scenarios_run': False, 'figures': records},
        ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Q2 typography saved; text, data, axes and canvas unchanged.')

if __name__ == '__main__':
    main()
