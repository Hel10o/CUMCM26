#!/usr/bin/env python3
"""Read original Q2 XLSX inputs through OOXML, without editing any workbook.

Uses only Python's standard library. Run from any directory:
    python q2_pro_handoff/evidence/audit_inputs.py
The sole output is data_contract_audit.json beside this script.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import platform
import re
import statistics
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUNDLE_ROOT = HERE.parent
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
# Verbatim paragraph transcribed from the supplied local original-PDF extraction.
# Kept here so the evidence bundle remains readable without the enclosing repository.
Q2_PARAGRAPH = '''问题 2 烘干过程一般持续 2-3 天，预热平衡与恒温干燥阶段的参数有所不同。请建立
整个烘干过程药材温度和水分浓度变化规律的数学模型（为简化问题，相关经验公式统一采
用附录 3 中的公式），在论文中按表 3 和表 4 的格式分别给出 3 h 内每隔 0.5 h、到药材中心
距离 0、0.5、1、1.5、2 cm 处的结果，并将每隔 1 s、到药材中心距离每隔 0.1 cm 的完整结
果保存到文件 result2.xlsx 中（模板文件见附件 3）。'''
RESULT2_DESCRIPTION = '''在“温度”和“水分浓度”工作表中分别保存问题 2 要求的温度（单位：°C）和水分
浓度（单位：kg/kg），其中 A 列为时间（单位：s），第 1 行为到药材中心的距离（单位：
cm）。'''


def locate(packaged_name, original_repository_path, required=True):
    packaged = BUNDLE_ROOT / 'inputs' / packaged_name
    original = ROOT / original_repository_path
    if packaged.is_file():
        return packaged
    if original.is_file():
        return original
    if required:
        raise FileNotFoundError(f'Missing packaged input {packaged_name}; repository fallback also absent: {original_repository_path}')
    return None


def digest(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob_sha1': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}


def read_xlsx(path):
    """Resolve actual sheet relationships and shared/inline strings from ZIP XML."""
    sheets = {}
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, 'ZIP CRC failure'
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            for item in ET.fromstring(archive.read('xl/sharedStrings.xml')):
                strings.append(''.join(t.text or '' for t in item.findall('.//s:t', NS)))
        relations = {item.get('Id'): item.get('Target')
                     for item in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        book = ET.fromstring(archive.read('xl/workbook.xml'))
        for sheet in book.findall('s:sheets/s:sheet', NS):
            target = relations[sheet.get(RID)]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            tree = ET.fromstring(archive.read(target))
            cells = {}
            for cell in tree.findall('s:sheetData/s:row/s:c', NS):
                typ = cell.get('t', 'n')
                value_node = cell.find('s:v', NS)
                if typ == 's':
                    value = strings[int(value_node.text)]
                elif typ == 'inlineStr':
                    value = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
                elif value_node is None:
                    value = None
                elif typ == 'n':
                    value = float(value_node.text)
                else:
                    value = value_node.text
                if value is not None:
                    cells[cell.get('r')] = {'value': value, 'type': typ,
                                          'formula': cell.findtext('s:f', default=None, namespaces=NS)}
            dimension = tree.find('s:dimension', NS)
            sheets[sheet.get('name')] = {
                'xml_part': target, 'dimension': dimension.get('ref') if dimension is not None else None,
                'nonempty_cells': cells,
                'merged_ranges': [item.get('ref') for item in tree.findall('s:mergeCells/s:mergeCell', NS)],
            }
    return sheets


def window_summary(rows, start, stop):
    selected = [row for row in rows if start <= row[0] <= stop]
    assert selected and selected[0][0] == start and selected[-1][0] == stop
    output = {'closed_interval_s': [start, stop], 'sample_count_including_both_endpoints': len(selected),
              'first_record': selected[0], 'last_record': selected[-1]}
    for index, label in [(1, 'temperature_degC'), (2, 'environment_quantity_kg_kg')]:
        values = [row[index] for row in selected]
        trapezoid = sum((right[0] - left[0]) * (left[index] + right[index]) / 2
                        for left, right in zip(selected[:-1], selected[1:])) / (stop - start)
        output[label] = {'minimum': min(values), 'maximum': max(values),
                         'sample_arithmetic_mean': statistics.mean(values),
                         'piecewise_linear_time_average': trapezoid,
                         'first_to_last_change': values[-1] - values[0],
                         'sample_standard_deviation': statistics.stdev(values)}
    return output


def main():
    specs = {
        'attachment1': ('附件1.xlsx', 'A题/附件/附件1.xlsx', True),
        'result2_template': ('result2_template.xlsx', 'A题/附件/附件3/result2.xlsx', True),
        'problem_page2_extracted_text': ('problem_page2.md', 'readable/problem/pages/002.md', False),
        'problem_page3_extracted_text': ('problem_page3.md', 'readable/problem/pages/003.md', False),
    }
    inputs = {key: path for key, spec in specs.items() if (path := locate(*spec)) is not None}
    before_hashes = {key: digest(path) for key, path in inputs.items()}
    before = {}
    for key, path in inputs.items():
        packaged = path.is_relative_to(BUNDLE_ROOT)
        original = ROOT / specs[key][1]
        before[key] = {'path': path.relative_to(BUNDLE_ROOT if packaged else ROOT).as_posix(),
                       'path_base': 'evidence_bundle' if packaged else 'repository',
                       'original_repository_path': specs[key][1],
                       **before_hashes[key]}
        if packaged and original.is_file():
            before[key]['packaged_copy_hash_matches_repository_original'] = digest(path) == digest(original)
            assert before[key]['packaged_copy_hash_matches_repository_original']
    attachment = read_xlsx(inputs['attachment1'])
    assert list(attachment) == ['Sheet1']
    cells = attachment['Sheet1']['nonempty_cells']
    headers = [cells[f'{col}1']['value'] for col in 'ABC']
    assert headers == ['时间', '温度', '水分浓度']
    rows = [[cells[f'{col}{row}']['value'] for col in 'ABC'] for row in range(2, 243)]
    assert len(rows) == 241 and all(math.isfinite(value) for row in rows for value in row)
    times = [row[0] for row in rows]
    assert times == list(range(0, 14401, 60))
    template = read_xlsx(inputs['result2_template'])
    template_summaries = {}
    for name, sheet in template.items():
        nonempty = {key: item['value'] for key, item in sheet['nonempty_cells'].items()}
        ellipses = {key: value for key, value in nonempty.items()
                    if isinstance(value, str) and any(mark in value for mark in ['...', '…', '⋯', '„'])}
        ellipsis_rows = [int(re.search(r'\d+$', key).group()) for key in ellipses if key.startswith('A')]
        numeric_times = {key: value for key, value in nonempty.items()
                         if re.fullmatch(r'A\d+', key) and isinstance(value, (int, float))}
        post_ellipsis = {key: value for key, value in numeric_times.items()
                         if ellipsis_rows and int(key[1:]) > min(ellipsis_rows)}
        header_radii = {key: value for key, value in nonempty.items()
                        if re.fullmatch(r'[B-Z]+1', key)}
        header_ellipsis_columns = [key[:-1] for key in ellipses if re.fullmatch(r'[B-Z]+1', key)]
        post_radius_ellipsis = {key: value for key, value in header_radii.items()
                               if isinstance(value, (int, float)) and header_ellipsis_columns
                               and key[:-1] > min(header_ellipsis_columns)}
        template_summaries[name] = {
            'xml_part': sheet['xml_part'], 'dimension': sheet['dimension'],
            'nonempty_cell_count': len(nonempty), 'all_nonempty_cells': nonempty,
            'time_column_numeric_examples': numeric_times, 'radius_header_examples': header_radii,
            'ellipsis_cells': ellipses,
            'numeric_time_examples_after_time_column_ellipsis': post_ellipsis,
            'numeric_radius_examples_after_header_ellipsis': post_radius_ellipsis,
            'largest_numeric_time_example_s': max(numeric_times.values()) if numeric_times else None,
            'end_time_is_specified_by_template': False,
            'merged_ranges': sheet['merged_ranges'],
        }
    q2_text, template_text = Q2_PARAGRAPH, RESULT2_DESCRIPTION
    text_mode = 'embedded verbatim original-extraction excerpts; original text files unavailable in this standalone bundle'
    if 'problem_page2_extracted_text' in inputs and 'problem_page3_extracted_text' in inputs:
        page2 = inputs['problem_page2_extracted_text'].read_text(encoding='utf-8')
        q2_text = '问题 2 ' + page2.split('问题 2 ', 1)[1].split('表 3 3 小时', 1)[0].strip()
        page3 = inputs['problem_page3_extracted_text'].read_text(encoding='utf-8')
        template_text = page3.split('result2.xlsx 问题 2 的结果模板文件', 1)[1].split('result3.xlsx', 1)[0].strip()
        assert q2_text == Q2_PARAGRAPH and template_text == RESULT2_DESCRIPTION
        text_mode = 'current original-PDF extraction files, with embedded excerpts crosschecked verbatim'
    variations = {}
    for column, name in [(1, 'temperature_degC'), (2, 'environment_quantity_kg_kg')]:
        values = [row[column] for row in rows]
        differences = [b - a for a, b in zip(values[:-1], values[1:])]
        variations[name] = {'minimum': min(values), 'maximum': max(values),
                            'times_of_maximum_s': [rows[i][0] for i, value in enumerate(values) if value == max(values)],
                            'increase_step_count': sum(d > 0 for d in differences),
                            'decrease_step_count': sum(d < 0 for d in differences),
                            'unchanged_step_count': sum(d == 0 for d in differences),
                            'largest_positive_60s_change': max(differences),
                            'largest_negative_60s_change': min(differences)}
    result = {
        'scope': 'Read-only original OOXML data/output contract audit for Q2, no model solving or result2 generation',
        'runtime_python': platform.python_version(), 'source_files': before,
        'attachment1': {
            'zip_crc_passed': True, 'sheet_names': list(attachment),
            'schema': {'sheet': 'Sheet1', 'dimension': attachment['Sheet1']['dimension'],
                       'header_cells': {f'{col}1': cells[f'{col}1']['value'] for col in 'ABC'},
                       'units_from_problem_appendix1': {'A': 's', 'B': 'degC', 'C': 'kg/kg'},
                       'units_are_not_written_in_workbook_header': True},
            'record_count': len(rows), 'time_domain_s': [0, 14400], 'sample_interval_s': 60,
            'finite': True, 'strictly_increasing_unique_times': True,
            'records_at_key_times': {str(int(t)): row for row in rows for t in [0, 1800, 3600, 7200, 10800, 14400] if row[0] == t},
            'variation': variations,
            'windows': {
                'q1_0_to_1800': window_summary(rows, 0, 1800),
                'q2_first_3h_0_to_10800': window_summary(rows, 0, 10800),
                'full_input_0_to_14400': window_summary(rows, 0, 14400),
                'last_hour_of_available_input_10800_to_14400': window_summary(rows, 10800, 14400),
                'last_hour_of_3h_reporting_window_7200_to_10800': window_summary(rows, 7200, 10800),
            },
            'meaning_boundary': 'Room measurements are boundary inputs, not internal material observations; interpreting environmental kg/kg as an effective solid-basis driver is a model assumption.',
        },
        'result2_template': {'zip_crc_passed': True, 'sheet_names': list(template), 'sheets': template_summaries,
                            'is_populated_result': False, 'contains_placeholder_ellipses': any(s['ellipsis_cells'] for s in template_summaries.values())},
        'problem_contract': {
            'q2_exact_extracted_paragraph': q2_text,
            'appendix1_result2_exact_extracted_description': template_text,
            'source_reading_level': 'Local original PDF text extraction, Q2 paragraph and appendix1 template description; this script does not claim original PDF visual formula verification.',
            'text_source_mode_this_run': text_mode,
            'model_time_scope': 'The statement asks for a model of the entire drying process and says drying usually lasts 2-3 days.',
            'paper_reporting_horizon_s': 10800,
            'paper_times_h': [.5, 1., 1.5, 2., 2.5, 3.],
            'paper_times_s': [1800, 3600, 5400, 7200, 9000, 10800],
            'paper_radii_cm': [0, .5, 1., 1.5, 2.],
            'paper_result_values_per_field': 30,
            'paper_result_values_both_fields': 60,
            'if_exporting_3h': {'time_s_first_last': [1, 10800], 'time_step_s': 1, 'positive_time_rows_per_field': 10800,
                               'radius_cm_first_last': [0, 2], 'radius_step_cm': .1, 'radius_columns': 21,
                               'result_values_per_field': 226800, 'result_values_both_fields': 453600,
                               'worksheet_result_range': 'B2:V10801',
                               'including_t0_in_raw_arrays_shape_per_field': [10801, 21],
                               'not_1800_rows': '1800 s is only the first paper reporting time for Q2; Q1 had 1800 output seconds.'},
            'input_records_through_3h_including_endpoints': 181,
            'input_records_through_30min_including_endpoints': 31,
            'complete_result2_end_time_explicit_in_q2_sentence': False,
            'complete_result2_end_time_explicit_in_appendix1_description': False,
            'complete_result2_end_time_explicit_in_original_template': False,
            'template_time_column_evidence': 'Both sheets show A2=1, A3=2, A4=3, A5=ellipsis, with no nonempty time cell after A5. F1=2 is the radius endpoint after E1=ellipsis, not a time endpoint.',
            'interpretation_boundary': 'The 3 h requirement is explicit for the paper tables; the full-result sentence repeats sampling intervals but does not explicitly repeat an end time. The actual original template specifies no final time.',
        },
        'recommendations': [
            'Freeze 0-10800 s as the fully evidenced 3 h reporting/validation horizon, with 1-10800 s Excel rows if using the 3 h result2 convention.',
            'Explain explicitly whether result2 covers the 3 h table horizon or the entire drying process; the original template has no numeric time endpoint after its ellipsis.',
            'First 3 h requires interpolation within measured data, not extrapolation. Any full drying trajectory beyond 14400 s needs a stated room-boundary extension rule.',
            'Keep the raw measured room trace over 0-14400 s; a constant-temperature extension must be labelled as a new assumption, and last-value and last-hour-mean conventions must not be conflated.',
            'Retain 31 measurements only for the first 1800 s; Q2 first 3 h has 181 measured samples. Exporting 1 s values is interpolation/solution output, not 10800 original observations.',
        ],
    }
    result['original_files_unchanged'] = all(digest(path) == before_hashes[key] for key, path in inputs.items())
    assert result['original_files_unchanged']
    (HERE / 'data_contract_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps({'attachment1_records': len(rows), 'q2_3h_input_records': 181,
                      'last_available_record': rows[-1],
                      'last_hour_of_available_input': result['attachment1']['windows']['last_hour_of_available_input_10800_to_14400'],
                      'template': result['result2_template'], 'original_files_unchanged': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
