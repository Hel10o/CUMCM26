"""Package selected Q3 handoff evidence without changing earlier deliveries."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / 'q3_pro_handoff'
MANIFEST = HANDOFF / 'MANIFEST.sha256'
ARCHIVE = ROOT / '第三问_Pro分析交付包.zip'


def selected_files():
    files = {p for p in HANDOFF.rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and p != MANIFEST}
    fixed = [
        'A题/A题.pdf', 'A题/附件/附件1.xlsx', 'A题/附件/附件3/result3.xlsx',
        'readable/README.md', 'readable/QUALITY.md',
        'q2_final_delivery/README.md', 'q2_final_delivery/analysis_decisions.md',
        'q2_final_delivery/run_all.py',
        'q2_final_delivery/inputs/附件1.xlsx',
        'q2_final_delivery/output/q2_unrounded.npz',
        'q2_final_delivery/output/table_temperature.csv',
        'q2_final_delivery/output/table_moisture.csv',
        'q2_final_delivery/output/第二问论文正文.md',
        'q2_final_delivery/output/validation/validation.json',
        'review_q2_20260911/第二问验收报告.md',
        'review_q2_20260911/acceptance_checks.json',
        'review_q2_20260911/independent_numeric/independent_radial.py',
        'review_q2_20260911/independent_numeric/独立数值核查.md',
        'review_q2_20260911/model_audit/model_audit.md',
    ]
    files.update(ROOT / p for p in fixed)
    files.update((ROOT / 'q2_final_delivery/source').glob('*.py'))
    for page in [2, 3, 4]:
        files.add(ROOT / f'q2_final_delivery/evidence/problem-page-{page}.png')
    for folder in ['readable/problem', 'readable/papers/da-silva-2014',
                   'readable/papers/chupawa-2022', 'readable/papers/adrover-2020']:
        files.update(p for p in (ROOT / folder).rglob('*')
                     if p.is_file() and p.suffix in {'.md', '.txt', '.json'})
    missing = [str(p.relative_to(ROOT)) for p in files if not p.is_file()]
    if missing:
        raise FileNotFoundError(missing)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def main():
    files = selected_files()
    records = [(p.relative_to(ROOT).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
               for p in files]
    MANIFEST.write_text(''.join(f'{digest}  {path}\n' for path, digest in records), encoding='utf-8')
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in [*files, MANIFEST]:
            z.write(p, p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(files) + 1
        assert len(set(z.namelist())) == len(z.namelist())
        for path, digest in records:
            b = z.read(path)
            assert hashlib.sha256(b).hexdigest() == digest, path
            assert b == (ROOT / path).read_bytes(), path
        assert z.read(MANIFEST.relative_to(ROOT).as_posix()) == MANIFEST.read_bytes()
    print(json.dumps({'archive': str(ARCHIVE), 'bytes': ARCHIVE.stat().st_size,
                      'file_count': len(files) + 1, 'manifest_entries_verified': len(records),
                      'crc_verified': True,
                      'sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
