"""Validate and package this review. --check never solves PDE or writes files.

--build updates only this new review's provenance, validation, manifest and ZIP.
It must not be run on a frozen release without intentionally creating a version.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import unquote
import numpy as np

V1 = Path(__file__).resolve().parents[1]
REPO = V1.parents[1]
BASE = 'bbf7658ea020f45564f40f90153f91960a16a40c'
ARCHIVE = V1.parent / '四问整体复审报告_v1.zip'
XMLNS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def source_manifest():
    records = {}
    def add(path, scope, expected=None):
        path = path.replace('\\', '/')
        p = REPO / path
        assert p.is_file(), path
        # The root README is intentionally revised in this release; cite its
        # actually read baseline bytes, not the new overview written later.
        digest = hashlib.sha256(git('show', f'{BASE}:{path}')).hexdigest() if path == 'README.md' else sha(p)
        if expected:
            assert digest == expected, ('Changed source', path)
        item = records.setdefault(path, {'path': path, 'baseline_sha256': digest, 'read_scopes': []})
        assert item['baseline_sha256'] == digest
        if scope not in item['read_scopes']:
            item['read_scopes'].append(scope)
    paper = read_json(V1 / 'reviews/paper/来源清单.json')
    for rec in paper['source_files']:
        add(rec['path'], rec['read_scope'], rec['sha256'])
    physics = read_json(V1 / 'reviews/physics/sources.json')
    for rec in physics['local']:
        add(rec['path'], rec['actual_scope'], rec['sha256'])
    for rec in read_json(V1 / 'reviews/physics/saved_field_physics_diagnostics.json')['sources'].values():
        add(rec['path'], 'Used by saved-field algebra/quadrature diagnostics; no PDE solve', rec['sha256'])
    for path, digest in read_json(V1 / 'reviews/geometry/endpoint_audit.json')['sources'].items():
        add(path, 'Read full stored fields/statistics; used as targeted 2D continuation initial history', digest)
    for rec in read_json(V1 / 'reviews/geometry/saved_geometry_scope.json'):
        for path, digest in rec['source_sha256'].items():
            add(path, 'Read stored snapshots and volume weights for new integration', digest)
    for p in sorted((V1 / 'evidence/environment').glob('*.json')):
        rec = read_json(p)
        add(rec['source_npz'], 'Read frozen full 4 h T/C state for conditional continuation', rec['source_npz_sha256'])
        add(rec['operator_source'], 'Read and reused audited coupled spectral operator', rec['operator_sha256'])
    extra = {
        'A题/A题.pdf': 'Original PDF identity checked; full extracted text read and acquired original page 2-4 renders visually inspected; not all PDF pages visually re-read',
        'review_q4_20260912/problem_pages/problem-2.png': 'Visually read original problem page 2: Q2 full process, Q3 everywhere threshold and Q4 introduction',
        'review_q4_20260912/problem_pages/problem-3.png': 'Visually read original page 3: templates and Appendix 2 constants',
        'review_q4_20260912/problem_pages/problem-4.png': 'Visually read original page 4: Appendix 3/4 coefficients and Kelvin convention',
        'q1_complete_delivery/q1_delivery/source/q1_solver.py': 'Read parameter, boundary and PDE sections',
        'q2_final_delivery/source/q2_core.py': 'Read local coefficients, boundary and coupled PDE implementation',
        'q4_complete_delivery/v1/source/q4_common.py': 'Read Environment/Radius and input functions; loaded attachments',
        'q4_complete_delivery/v1/source/q4_spectral.py': 'Read complete main operator and extrema reconstruction',
        'q4_complete_delivery/v1/source/check_numerics.py': 'Read default output behavior; not executed',
        'q4_complete_delivery/v1/source/run_q4.py': 'Read solver and event pipeline; not re-executed',
        'q4_complete_delivery/v1/README.md': 'Read current Q4 version and pipeline status',
        'q4_complete_delivery/v1/q123_closeout/README.md': 'Read Q2/Q3 full-process closeout and source contract',
        'q4_complete_delivery/v1/validation/numeric_comparison.json': 'Read existing convergence and solver comparison evidence, not newly solved',
        'q4_complete_delivery/v1/validation/geometry/README.md': 'Read dimensional comparison contract and evidence index',
        'q4_complete_delivery/v1/validation/geometry/geometry_comparison.json': 'Read current paired dimensional comparison statistics',
        'review_q4_20260912/artifacts/artifact_audit.json': 'Read prior full-cell audit; this release rechecks frozen hashes and workbook headers only',
        'review_q4_20260912/numeric/numeric_audit.json': 'Read earlier local numerical unit/degeneration checks; not rerun as full PDE',
        'readable/papers/da-silva-2014/pages/003.md': 'Read local primary-paper extracted page; targeted equations',
        'readable/papers/da-silva-2014/pages/004.md': 'Read local primary-paper extracted page; targeted dry-basis/equilibrium sections'
    }
    for path, scope in extra.items():
        add(path, scope)
    official = [
        'q1_complete_delivery/q1_delivery/output/result1.xlsx',
        'q4_complete_delivery/v1/q123_closeout/result2.xlsx',
        'q3_refinement_delivery/output/result3.xlsx',
        'q4_complete_delivery/v1/output/result4.xlsx'
    ]
    for path in official:
        add(path, 'Current official workbook: baseline bytes checked; ZIP XML headers read this review, full-cell agreement relies on acquired earlier audit')
    return {'source_commit': BASE, 'repository': 'https://github.com/Hel10o/libai.git',
            'mode': 'Full local checkout; initially clean and matched origin/main; no input ZIP fallback used',
            'scope_note': 'Reading levels are per file. Source equality proves identity, not physical validity. New outputs are separately hashed by MANIFEST.',
            'sources': sorted(records.values(), key=lambda x: x['path']),
            'web_sources_from_physics_review': physics['web'],
            'additional_primary_lookup': [
                {'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7692062/', 'scope': 'Primary article excerpts available through search; direct open returned browser challenge, not a full online read'},
                {'url': 'https://www.sciencedirect.com/science/article/pii/S0260877414002118', 'scope': 'Publisher metadata/abstract from search; direct open 403. Used acquired local primary-paper pages for equations'}
            ], 'official_workbooks': official}


def workbook_headers(path):
    """Read workbook names and first two physical rows; not full-cell audit."""
    out = {'path': path.relative_to(REPO).as_posix(), 'sha256': sha(path), 'sheets': []}
    with zipfile.ZipFile(path) as z:
        tree = ET.fromstring(z.read('xl/workbook.xml'))
        out['sheet_names'] = [e.attrib['name'] for e in tree.iter(XMLNS + 'sheet')]
        for member in sorted(n for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+\.xml', n)):
            rows, dimension = [], None
            with z.open(member) as f:
                for _, e in ET.iterparse(f, events=('end',)):
                    if e.tag == XMLNS + 'dimension':
                        dimension = e.attrib.get('ref')
                    if e.tag == XMLNS + 'row':
                        rows.append({'r': e.attrib.get('r'), 'cells': [dict(ref=c.attrib.get('r'), type=c.attrib.get('t'), raw=''.join(c.itertext())) for c in e]})
                        if len(rows) == 2:
                            break
            out['sheets'].append({'xml': member, 'declared_dimension': dimension, 'first_two_rows_raw': rows})
    return out


def validate(sources):
    # Git may quote Unicode pathnames unless core.quotepath is disabled locally
    # for this query. NUL separators preserve exact paths without config edits.
    changed = git('diff', '--name-only', '-z', BASE).decode('utf-8').split('\0')
    unexpected = [x for x in changed if x and x not in ('README.md', '.gitattributes') and not x.startswith('q1234_overall_review_delivery/')]
    assert not unexpected, unexpected
    for rec in sources['sources']:
        path = rec['path']
        digest = hashlib.sha256(git('show', f'{BASE}:{path}')).hexdigest() if path == 'README.md' else sha(REPO / path)
        assert digest == rec['baseline_sha256'], path
    old = read_json(REPO / 'review_q4_20260912/artifacts/artifact_audit.json')
    old_files = old['manifest']['files']
    for rec in old_files:
        assert sha(REPO / 'q4_complete_delivery/v1' / rec['path']) == rec['sha256'], rec['path']
    ea = read_json(V1 / 'reviews/environment_check/environment_evidence_audit.json')
    assert ea['status'] == 'PASS' and ea['pairs_checked'] == 14
    for p in (V1 / 'evidence/environment').glob('*.json'):
        d = read_json(p)
        assert sha(V1 / 'source/environment_probe.py') == d['script_sha256']
        with np.load(p.with_suffix('.npz')) as z:
            assert np.isfinite(z['full_TC']).all()
            assert abs(z['event_full_TC'][:, 1].max() - .15) < 1e-11
            assert abs(z['official_full_TC'][:, 1].max() - d['Cmax_at_official_execution']) < 1e-11
    nested_checked = 0
    for manifest in sorted((V1 / 'reviews').rglob('*MANIFEST*.sha256')):
        for line in manifest.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            digest, rel = line.split('  ', 1)
            assert sha(manifest.parent / rel) == digest, (manifest, rel)
            nested_checked += 1
    py_count = 0
    for p in V1.rglob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
        py_count += 1
    links_checked, broken = 0, []
    for p in V1.rglob('*.md'):
        for target in re.findall(r'\]\(([^\n)]+)\)', p.read_text(encoding='utf-8')):
            target = target.strip('<>')
            if re.match(r'^[a-zA-Z]+://|^#', target):
                continue
            target = unquote(target.split('#')[0])
            if target.startswith('/D:/'):
                target = target[1:]
            target = re.sub(r':\d+$', '', target)
            resolved = Path(target) if Path(target).is_absolute() else p.parent / target
            links_checked += 1
            if not resolved.exists():
                broken.append((p.relative_to(V1).as_posix(), target))
    # Manifest and validation are first created at the end of --build.
    allowed_future = {'MANIFEST.sha256', 'evidence/delivery_validation.json', '来源清单.json'}
    broken = [x for x in broken if not (x[0] == 'README.md' and x[1] in allowed_future)]
    assert not broken, broken
    for p in V1.rglob('*'):
        assert '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo'), str(p)
    probes = [read_json(p) for p in (V1 / 'evidence/environment').glob('*.json')]
    return {'status': 'PASS', 'validated_utc': datetime.now(timezone.utc).isoformat(), 'source_commit': BASE,
            'scope': 'Artifact/source identity, prior frozen Q4 content hashes, raw workbook header read, new numerical records, nested manifests, Python syntax and Markdown targets. No PDE solve or full Excel cell re-audit.',
            'source_files_checked': len(sources['sources']), 'frozen_q4_manifest_entries_checked': len(old_files),
            'official_workbook_headers': [workbook_headers(REPO / p) for p in sources['official_workbooks']],
            'environment_pair_count': len(probes), 'environment_total_solver_elapsed_s': sum(p['elapsed_s'] for p in probes),
            'independent_environment_check': ea['status'], 'nested_manifest_entries_checked': nested_checked,
            'python_ast_files_checked': py_count, 'markdown_local_targets_checked': links_checked,
            'unexpected_changed_baseline_paths': unexpected, 'unresolved_model_work': ['Fine direct Q4 2D validation', 'Physical calibration and closure', 'New combined paper'],
            'model_review_complete_is_not_model_validation_complete': True}


def check_manifest():
    m = V1 / 'MANIFEST.sha256'
    lines = m.read_text(encoding='utf-8').splitlines()
    names = []
    for line in lines:
        digest, rel = line.split('  ', 1)
        assert sha(V1 / rel) == digest, rel
        names.append(rel)
    actual = {p.relative_to(V1).as_posix() for p in V1.rglob('*') if p.is_file() and p != m}
    assert set(names) == actual and len(names) == len(actual)
    if ARCHIVE.exists():
        prefix = V1.relative_to(REPO).as_posix() + '/'
        with zipfile.ZipFile(ARCHIVE) as z:
            expected = {prefix + n for n in actual | {'MANIFEST.sha256'}}
            assert set(z.namelist()) == expected
            for name in z.namelist():
                assert hashlib.sha256(z.read(name)).hexdigest() == sha(REPO / name), name
        digest = ARCHIVE.with_suffix('.zip.sha256').read_text(encoding='utf-8').split('  ', 1)[0]
        assert sha(ARCHIVE) == digest
    return len(names)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    assert args.build != args.check, 'Choose exactly one of --build or --check'
    if args.build:
        sources = source_manifest()
        save_json(V1 / '来源清单.json', sources)
        result = validate(sources)
        save_json(V1 / 'evidence/delivery_validation.json', result)
        m = V1 / 'MANIFEST.sha256'
        files = sorted(p for p in V1.rglob('*') if p.is_file() and p != m)
        m.write_text(''.join(f'{sha(p)}  {p.relative_to(V1).as_posix()}\n' for p in files), encoding='utf-8')
        with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for p in files + [m]:
                z.write(p, p.relative_to(REPO).as_posix())
        ARCHIVE.with_suffix('.zip.sha256').write_text(f'{sha(ARCHIVE)}  {ARCHIVE.name}\n', encoding='utf-8')
    else:
        result = validate(read_json(V1 / '来源清单.json'))
    result['manifest_entries_verified'] = check_manifest()
    result.pop('official_workbook_headers', None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
