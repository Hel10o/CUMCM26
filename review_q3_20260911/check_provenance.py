"""Read-only integrity checks for the received Q3 delivery and its source bundle."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PKG = ROOT / 'q3_final_delivery'


def digest(b):
    return hashlib.sha256(b).hexdigest()


def entries(path):
    return [line.split('  ', 1) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def main():
    checks = []

    def check(name, passed, detail):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))

    manifest = entries(PKG / 'MANIFEST.sha256')
    mismatches = [name for expected, name in manifest if not (PKG / name).is_file() or digest((PKG / name).read_bytes()) != expected]
    actual = {p.relative_to(PKG).as_posix() for p in PKG.rglob('*') if p.is_file()}
    covered = {name for _, name in manifest} | {'MANIFEST.sha256'}
    check('received_delivery_manifest', not mismatches and len(manifest) == len(set(n for _, n in manifest)), {'entries': len(manifest), 'mismatches': mismatches})
    check('received_delivery_manifest_coverage', actual == covered, {'files': len(actual), 'unlisted': sorted(actual-covered), 'missing': sorted(covered-actual)})
    source = json.loads((PKG / 'source_access.json').read_text(encoding='utf-8'))
    bundle = ROOT / source['source_zip']
    check('upstream_bundle_sha256', digest(bundle.read_bytes()) == source['source_zip_sha256'], {'actual': digest(bundle.read_bytes()), 'expected': source['source_zip_sha256']})
    up = entries(PKG / 'inputs/UPSTREAM_MANIFEST.sha256')
    with zipfile.ZipFile(bundle) as z:
        mismatches = [name for expected, name in up if name not in z.namelist() or digest(z.read(name)) != expected]
        check('upstream_bundle_all_entries', not mismatches, {'entries': len(up), 'mismatches': mismatches})
    copied = []
    for p in (PKG / 'inputs/upstream').rglob('*'):
        if p.is_file():
            key = p.relative_to(PKG / 'inputs/upstream').as_posix()
            expected = dict((name, sha) for sha, name in up).get(key)
            copied.append({'path': key, 'passed': expected is not None and digest(p.read_bytes()) == expected})
    check('retained_upstream_copies', all(x['passed'] for x in copied), {'files': len(copied), 'mismatches': [x for x in copied if not x['passed']]})
    mappings = {
        'inputs/problem.pdf': 'A题/A题.pdf',
        'inputs/attachment1.xlsx': 'A题/附件/附件1.xlsx',
        'inputs/result3_blank.xlsx': 'A题/附件/附件3/result3.xlsx',
        'inputs/q2_unrounded.npz': 'q2_final_delivery/output/q2_unrounded.npz',
    }
    for local, original in mappings.items():
        check('original_input:' + local, digest((PKG/local).read_bytes()) == digest((ROOT/original).read_bytes()), {'repository_path': original, 'sha256': digest((PKG/local).read_bytes())})
    pinned = source['pinned_commit']
    for path, expected in [('README.md', source['git_api_reads'][0]['blob_sha1']), ('readable/README.md', source['git_api_reads'][2]['blob_sha1']), ('q3_pro_handoff/MANIFEST.sha256', source['manifest_git_blob_sha1'])]:
        result = subprocess.run(['git', 'rev-parse', f'{pinned}:{path}'], cwd=ROOT, capture_output=True, text=True, check=False)
        check('pinned_git_blob:' + path, result.returncode == 0 and result.stdout.strip() == expected, {'pinned_commit': pinned, 'expected': expected, 'actual': result.stdout.strip()})
    frozen = json.loads((OUT/'original_delivery_hashes.json').read_text(encoding='utf-8'))
    # Accommodate the explicit snapshot wrapper used when this audit was opened.
    frozen_files = frozen.get('files', frozen)
    if isinstance(frozen_files, list):
        frozen_files = {x['path']: x['sha256'] for x in frozen_files}
    if isinstance(frozen_files, dict) and all(isinstance(x, str) for x in frozen_files.values()):
        changed = [name for name, sha in frozen_files.items() if not (PKG/name).is_file() or digest((PKG/name).read_bytes()) != sha]
        check('unchanged_since_review_opened', not changed and actual == set(frozen_files), {'files': len(frozen_files), 'changed': changed})
    else:
        raise ValueError('Inspect unexpected snapshot schema instead of assuming preservation')
    result = {'checks': checks, 'all_pass': all(c['passed'] for c in checks)}
    (OUT/'provenance_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['all_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
