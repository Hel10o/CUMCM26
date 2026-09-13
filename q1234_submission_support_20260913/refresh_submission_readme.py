"""Refresh the existing submission ZIP guide; preserve all numerical members."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import zipfile
import re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PAPER = ROOT / 'paper/q1234_draft_v1'
ZIP = BASE / 'out/A题_支撑材料.zip'
EVIDENCE = BASE / 'evidence/submission_zip_delivery_20260913'
BASELINE = '13d939f07722bce4ee1d19a94992a91c83dce88f'
EXPECTED = '031872a5738d2568803722b318c87c7842e51418aca08fdcf7d25cb10c778e2e'
MEMBER = '支撑材料/support/README.md'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    old_bytes = ZIP.read_bytes()
    assert sha(old_bytes) == EXPECTED, 'ZIP baseline changed; inspect before updating'
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    current_report = BASE / 'evidence/package_report.json'
    prior = json.loads(current_report.read_text(encoding='utf-8'))
    assert prior['zip_sha256'] == EXPECTED
    (EVIDENCE / 'prior_report.json').write_bytes(current_report.read_bytes())
    with zipfile.ZipFile(BytesIO(old_bytes)) as archive:
        assert archive.testzip() is None
        old = {info.filename: archive.read(info.filename) for info in archive.infolist()}
        infos = {info.filename: info for info in archive.infolist()}
    updated = dict(old)
    updated[MEMBER] = (PAPER / 'support/README.md').read_bytes()
    assert [n for n in old if old[n] != updated[n]] == [MEMBER]
    # Verify every live code/support file, figure and the AI PDF, without any
    # solver, workbook export, array regeneration or numerical recalculation.
    support_paths = [p for p in (PAPER/'support').rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc']
    for path in support_paths:
        assert updated['支撑材料/'+path.relative_to(PAPER).as_posix()] == path.read_bytes()
    figures = set()
    for source in [PAPER/'main.tex', *sorted((PAPER/'sections').glob('*.tex'))]:
        figures.update(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',
                                  source.read_text(encoding='utf-8')))
    assert len(figures) == 12
    for rel in figures:
        assert updated['支撑材料/'+rel] == (PAPER/rel).read_bytes()
    assert updated['支撑材料/AI工具使用详情.pdf'] == (PAPER/'AI工具使用详情.pdf').read_bytes()
    for item in prior['unchanged_numerical_members']:
        assert sha(updated[item['name']]) == item['sha256']
    assert len(updated) == 94
    temporary = ZIP.with_suffix('.delivery.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(updated.items()):
            info = infos[name]
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(temporary) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(updated)
        assert all(archive.read(name) == data for name, data in updated.items())
        members = [{'name': i.filename, 'bytes': i.file_size, 'zip_bytes': i.compress_size}
                   for i in archive.infolist()]
    assert temporary.stat().st_size < 20_000_000
    assert ZIP.read_bytes() == old_bytes, 'Concurrent ZIP change; do not overwrite'
    temporary.replace(ZIP)
    report = {
        'operation': 'Refresh submission guide and verify existing ZIP; no numerical rerun',
        'baseline_commit': BASELINE, 'baseline_zip_sha256': EXPECTED,
        'changed_existing_members': [MEMBER], 'unchanged_member_count': 93,
        'unchanged_numerical_members': prior['unchanged_numerical_members'],
        'figure_count': 12, 'support_files_matched_to_current': len(support_paths),
        'all_figures_match_current_paper_bytes': True, 'AI_pdf_matches_current': True,
        'member_count': len(members), 'members': members, 'zip_crc_check': 'passed',
        'all_members_read_back': True, 'pde_or_parameter_scenarios_run': False,
        'workbooks_or_arrays_reexported': False,
        'zip_bytes': ZIP.stat().st_size, 'zip_sha256': sha(ZIP.read_bytes()),
        'zip_decimal_mb': round(ZIP.stat().st_size/1_000_000, 2),
        'zip_mib': round(ZIP.stat().st_size/1048576, 2),
        'prior_checks': 'Historical identity and numerical checks remain in prior_report.json; not rerun.'}
    encoded = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
    current_report.write_text(encoded, encoding='utf-8')
    (EVIDENCE/'verification.json').write_text(encoded, encoding='utf-8')
    ZIP.with_suffix('.zip.sha256').write_text(report['zip_sha256']+'  '+ZIP.name+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['members','unchanged_numerical_members']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
