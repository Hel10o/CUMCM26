"""Verify this Markdown handoff and freeze its cited repository inputs; no PDE run."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
BASE = '15cc3bf4afad748ab08e87bb3030ef606b1c9b9a'
MAIN = OUT / '前三问物理闭合与修正计算_Pro交接文档.md'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def local_links(path):
    for target in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', path.read_text(encoding='utf-8')):
        parsed = urlsplit(target.strip('<>'))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield (path.parent / unquote(parsed.path)).resolve()


def main():
    # Only references outside this new handoff are frozen against the baseline.
    sources = set()
    for path in local_links(MAIN):
        if path.is_relative_to(OUT):
            continue
        if not path.exists():
            raise FileNotFoundError(path)
        if not path.is_relative_to(ROOT):
            raise ValueError(f'Outside repository: {path}')
        if path.is_dir():
            rel_dir = path.relative_to(ROOT).as_posix()
            tracked = subprocess.check_output(
                ['git', 'ls-tree', '-rz', '--name-only', BASE, '--', rel_dir], cwd=ROOT)
            sources.update(ROOT / name.decode('utf-8') for name in tracked.split(b'\0') if name)
        else:
            sources.add(path)
    entries = []
    for path in sorted(sources):
        rel = path.relative_to(ROOT).as_posix()
        actual = path.read_bytes()
        frozen = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=ROOT)
        if actual != frozen:
            raise ValueError(f'Working file differs from baseline bytes: {rel}')
        entries.append({'path': rel, 'bytes': len(actual), 'sha256': digest(actual),
                        'baseline_bytes_match': True,
                        'url': f'https://github.com/Hel10o/libai/blob/{BASE}/{quote(rel, safe="/")}'})
    write_json(OUT / 'source_manifest.json', {'baseline_commit': BASE,
        'scope': 'Cited local source files and original attachments. Not a full repository manifest.',
        'count': len(entries), 'files': entries})
    # These two files are generated below; allow only these specific future targets.
    future = {OUT / 'handoff_checks.json', OUT / 'MANIFEST.sha256'}
    checked = []
    for doc in sorted(OUT.glob('*.md')):
        for target in local_links(doc):
            if not target.exists() and target not in future:
                raise FileNotFoundError(f'{doc.name}: {target}')
            if not target.is_relative_to(ROOT):
                raise ValueError(f'Outside repository link: {target}')
            checked.append({'document': doc.name, 'target': target.relative_to(ROOT).as_posix()})
    write_json(OUT / 'handoff_checks.json', {
        'status': 'pass', 'baseline_commit': BASE,
        'source_files_verified_byte_for_byte': len(entries),
        'local_links_checked': len(checked), 'links': checked,
        'validation_scope': 'Document link targets and baseline source bytes only; no new physics simulation.',
        'independent_review': 'Separate physics reviewer inspected the task requirements; this script does not certify physical correctness.'})
    manifest = []
    for path in sorted(OUT.rglob('*')):
        if path.is_file() and path.name != 'MANIFEST.sha256':
            manifest.append(f'{digest(path.read_bytes())}  {path.relative_to(OUT).as_posix()}')
    (OUT / 'MANIFEST.sha256').write_text('\n'.join(manifest) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'pass', 'source_files': len(entries),
                      'local_links': len(checked), 'handoff_manifest_files': len(manifest)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
