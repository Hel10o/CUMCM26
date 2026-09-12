"""Build a selective review ZIP from the current workspace; verify every byte."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(__file__).resolve().parent
ZIP = DEST / '四问整体复审输入包.zip'
MANIFEST = DEST / 'INPUT_MANIFEST.json'
CHECKS = DEST / 'PACKAGE_CHECKS.json'
TEXT = {'.md', '.txt', '.json', '.py', '.mjs', '.tex', '.bib', '.toml', '.csv'}
SCOPES = ['A题', 'readable', '分析与文献', 'q4_complete_delivery', 'review_q4_20260912',
          'q1234_overall_review_handoff', 'q1_complete_delivery/q1_delivery', 'q2_final_delivery',
          'q2_refinement_delivery', 'q3_refinement_delivery', 'review_q1_20260910',
          'review_q2_final_20260911', 'review_q123_physics_20260911', 'q123_requirements_review_delivery/v1',
          'q123_model_selection_delivery/v1', 'paper/q1_q2_stage']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def select(path):
    rel = path.relative_to(ROOT).as_posix()
    if any(part in {'.venv', '__pycache__', 'node_modules', '.git'} for part in path.parts):
        return False, 'Local environment/cache; excluded from review and Git.'
    if path in [ZIP, MANIFEST, CHECKS]:
        return False, 'Package self-reference/control file; manifest is embedded separately.'
    if rel.startswith(('q1234_overall_review_handoff/', 'review_q4_20260912/')):
        return True, ''
    if rel.startswith(('readable/', 'A题/')):
        return True, ''
    if rel.startswith('分析与文献/'):
        if path.name == 'foods-11-04045-v2.pdf':
            return False, 'Large LFS paper; extracted full text included, original remains in Git LFS.'
        return True, ''
    if rel.startswith('q4_complete_delivery/'):
        if path.suffix.lower() in TEXT and path.stat().st_size < 6_000_000:
            return True, ''
        if path.suffix.lower() == '.xlsx':
            return True, ''
        if rel.endswith(('output/main.npz', 'output/q23_unified.npz', 'output/q2_unrounded.npz', 'output/solution.npz')):
            return True, ''
        if '/figures/' in rel and path.suffix.lower() == '.png':
            return True, ''
        if path.name in {'MANIFEST.sha256', 'problem.pdf'}:
            return True, ''
        return False, 'Selective review: secondary raw fields/logs/fonts/page previews remain in full repository.'
    if path.suffix.lower() in TEXT and path.stat().st_size < 1_000_000:
        return True, ''
    if rel in {'q1_complete_delivery/q1_delivery/output/result1.xlsx',
               'q1_complete_delivery/q1_delivery/output/q1_unrounded.npz',
               'q2_final_delivery/output/result2.xlsx', 'q2_final_delivery/output/q2_unrounded.npz',
               'q3_refinement_delivery/output/result3.xlsx', 'q3_refinement_delivery/output/solution.npz'}:
        return True, ''
    return False, 'Historical raw fields, binaries or large exports omitted; request only if needed at the recorded commit.'


def main():
    included, omitted = [], []
    candidates = set()
    for scope in SCOPES:
        candidates.update(p for p in (ROOT / scope).rglob('*') if p.is_file())
    for path in sorted(candidates):
        take, reason = select(path)
        rel = path.relative_to(ROOT).as_posix()
        if any(part in {'.venv', '__pycache__', 'node_modules', '.git'} for part in path.parts):
            continue
        record = {'path': rel, 'bytes': path.stat().st_size}
        if take:
            record['sha256'] = sha(path.read_bytes())
            included.append(record)
        elif path not in [ZIP, MANIFEST, CHECKS]:
            record['reason'] = reason
            omitted.append(record)
    base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(),
                'repository': 'https://github.com/Hel10o/libai',
                'base_commit_before_this_handoff': base,
                'final_commit_note': 'The final commit contains this manifest; obtain its SHA from the Git commit containing the handoff. No self-referential commit SHA is embedded.',
                'scope': 'Selective four-question model-review inputs, not a full clone or complete historical cold-start suite.',
                'original_q4_manifest_note': 'The original Q4 v1 manifest describes its entire frozen delivery; some secondary files are deliberately omitted from this ZIP.',
                'included_file_count': len(included), 'included_bytes': sum(r['bytes'] for r in included),
                'files': included, 'omitted_within_review_scopes': omitted,
                'out_of_scope_note': 'Other repository directories not in review_scopes are not enumerated; available in the repository.',
                'review_scopes': SCOPES,
                'manifest_self_excluded': True}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for record in included:
            archive.write(ROOT / record['path'], record['path'])
        archive.write(MANIFEST, MANIFEST.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ZIP) as archive:
        assert archive.testzip() is None
        for record in included:
            data = archive.read(record['path'])
            assert len(data) == record['bytes'] and sha(data) == record['sha256']
            assert data == (ROOT / record['path']).read_bytes()
        assert archive.read(MANIFEST.relative_to(ROOT).as_posix()) == MANIFEST.read_bytes()
        assert len(archive.namelist()) == len(included) + 1
    summary = {'passed': True, 'zip': ZIP.name, 'zip_bytes': ZIP.stat().st_size,
               'zip_sha256': sha(ZIP.read_bytes()), 'manifest_sha256': sha(MANIFEST.read_bytes()),
               'content_files_verified_byte_for_byte': len(included), 'extra_manifest_entries': 1,
               'zip_crc_passed': True, 'source_files_match_archive': True,
               'omitted_files_enumerated': len(omitted),
               'check_file_outside_zip_to_avoid_self_reference': True}
    CHECKS.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    assert ZIP.stat().st_size < 99_000_000, 'Review ZIP must remain below normal Git file limits.'


if __name__ == '__main__':
    main()
