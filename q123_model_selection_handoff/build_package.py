"""Build the new scoped handoff atop the verified earlier input snapshot. No PDE run."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
from urllib.parse import urlsplit, unquote
import hashlib
import json
import posixpath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
BASE = '1feb7686a371179bc6f545217e229f388a9bc379'
OLD = ROOT / 'q123_physics_recovery_20260911/q123_physics_offline_inputs.zip'
OLD_SHA = '290dfab4e78d6489cc794d3428cd48bde8ff43a74fac1956ccd5c490ac49ec59'
OLD_PREFIX = 'q123_physics_offline_inputs/'
NEW_PREFIX = 'q123_model_selection_inputs/'
TASK = 'q123_model_selection_handoff/前三问二维与潜热影响评估及最终建模路线_Pro任务书.md'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def main():
    if sha(OLD.read_bytes()) != OLD_SHA:
        raise ValueError('Previous input archive hash mismatch')
    if git('rev-parse', '--show-object-format').strip() != b'sha1':
        raise ValueError('This source comparison expects Git SHA-1 object format')
    tree = {}
    for entry in git('ls-tree', '-rz', BASE).split(b'\0'):
        if not entry:
            continue
        meta, path = entry.split(b'\t', 1)
        mode, kind, oid = meta.split()
        if kind == b'blob':
            tree[path.decode('utf-8')] = oid.decode('ascii')
    with ZipFile(OLD) as z:
        if z.testzip() is not None:
            raise ValueError('Previous ZIP CRC failure')
        old_manifest = json.loads(z.read(OLD_PREFIX + 'INPUT_MANIFEST.json'))
        payload = {}
        refreshed = []
        for item in old_manifest['files']:
            data = z.read(OLD_PREFIX + item['path'])
            if len(data) != item['bytes'] or sha(data) != item['sha256']:
                raise ValueError(item['path'])
            if item['source'].startswith('git:'):
                oid = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
                if tree.get(item['path']) != oid:
                    data = git('show', BASE + ':' + item['path'])
                    oid = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
                    if tree.get(item['path']) != oid:
                        raise ValueError('Git object mismatch: ' + item['path'])
                    refreshed.append(item['path'])
                payload[item['path']] = data
    verified_sources = len(payload)
    origins = {name: 'git:' + BASE for name in payload}
    overlays = ['README.md', 'AGENTS.md', TASK,
                'q123_model_selection_handoff/README.md',
                'q123_model_selection_handoff/发给Pro的提示词.txt']
    for name in overlays:
        payload[name] = (ROOT / name).read_bytes()
        origins[name] = 'new-handoff-overlay; committed after baseline'
    targets = []
    for target in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', payload[TASK].decode('utf-8')):
        u = urlsplit(target)
        if u.scheme or not u.path:
            continue
        name = posixpath.normpath(posixpath.join(posixpath.dirname(TASK), unquote(u.path)))
        if name not in payload and not any(p.startswith(name.rstrip('/') + '/') for p in payload):
            raise FileNotFoundError('Task-linked input missing: ' + name)
        targets.append(name)
    start = '''# 当前任务：二维、潜热与最终建模选择

本包是精选输入与新任务书，不是新的物理修正结果。先运行：

python verify_inputs.py

然后完整读取 q123_model_selection_handoff/前三问二维与潜热影响评估及最终建模路线_Pro任务书.md。

本轮目标是量化前三问二维端面交换、潜热和二者共同作用，再明确推荐各问最终模型。旧q123_physics_pro_handoff任务书仅作技术背景；不沿用其中立即交付全套正式Excel和论文定稿的范围要求。先给可靠对照和建模思路。

资料基准提交：1feb7686a371179bc6f545217e229f388a9bc379。新任务书、提示词及根README/AGENTS为后续交接增补，INPUT_MANIFEST.json逐项区分来源。核验离线文件不等于独立验证了在线Git提交；联网失败也不阻止使用已校验的包内材料。

所有输入保持原件或明确标记增补。已有任务中间结果和旧程序存在历史限制，请先读runtime审核，在新输出目录运行。包内 review_q123_physics_20260911/runtime/candidate_51mekupf/untrusted_checkpoint.npz 是旧审核保存的失败合成夹具，不能当作物理解。

保留原题附件、核心求解器、未舍入基线、最新物理审核、匹配几何证据、可读论文、Adrover与da Silva的原PDF。省略完整.git、很多重复网格产物、完整论文构建资产、Chupawa约120MiB原PDF等；它的逐页文本仍在，未看原页不得声称该文公式均已核验。最新任务书的直接本地链接已检查；历史README的进一步链接未保证全部离线存在。

参考输入不变的情况下不必重跑全部旧套件。新四组对照的数值必须真实运行，未知参数使用有依据的条件情景，不冒充唯一真值。共享模型F的1D/2D、无/有潜热四组保持其余配置一致，B到F的闭合调整单列。
'''
    verifier = '''from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
m=json.loads((r/'INPUT_MANIFEST.json').read_text(encoding='utf-8'))
seen=set()
for item in m['files']:
    if item['path'] in seen: raise ValueError('Duplicate path')
    seen.add(item['path'])
    p=(r/item['path']).resolve()
    if not p.is_relative_to(r): raise ValueError('Path outside package')
    b=p.read_bytes()
    if len(b)!=item['bytes'] or hashlib.sha256(b).hexdigest()!=item['sha256']:
        raise ValueError('Hash mismatch: '+item['path'])
print('PASS',len(seen),'files; declared baseline',m['declared_source_commit'])
print('File integrity verified; not independent online provenance or model accuracy.')
'''
    payload['START_HERE.md'] = start.encode('utf-8')
    payload['verify_inputs.py'] = verifier.encode('utf-8')
    origins.update({'START_HERE.md': 'new-handoff-generated', 'verify_inputs.py': 'new-handoff-generated'})
    inventory = [{'path': name, 'bytes': len(data), 'sha256': sha(data), 'source': origins[name]}
                 for name, data in sorted(payload.items())]
    payload['INPUT_MANIFEST.json'] = encode_json({'declared_source_commit': BASE,
        'scope': 'Selected baseline inputs with explicit new task overlays; not full repository.',
        'files': inventory})
    archive = OUT / 'q123_model_selection_inputs.zip'
    if archive.exists():
        raise FileExistsError('Refusing to overwrite a completed archive')
    with ZipFile(archive, 'x', compression=ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in sorted(payload.items()):
            item = ZipInfo(NEW_PREFIX + name, (2026, 9, 11, 0, 0, 0))
            item.compress_type = ZIP_DEFLATED
            z.writestr(item, data)
    with ZipFile(archive) as z:
        if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('ZIP integrity failure')
        for name, data in payload.items():
            if z.read(NEW_PREFIX + name) != data:
                raise ValueError('ZIP bytes differ: ' + name)
    report = {'status': 'pass', 'input_baseline_commit': BASE, 'previous_archive_sha256': OLD_SHA,
              'old_manifest_files_checked': len(old_manifest['files']),
              'baseline_sources_verified_against_git_objects': verified_sources,
              'prior_archive_inputs_refreshed_from_selected_baseline': refreshed,
              'new_handoff_overlay_paths': overlays,
              'new_task_local_links_checked': len(targets),
              'archive_entries': len(payload), 'manifest_entries': len(inventory),
              'zip_bytes': archive.stat().st_size, 'zip_sha256': sha(archive.read_bytes()),
              'scope': 'Handoff and package verification only; no 2D or latent PDE run.'}
    (OUT / 'package_checks.json').write_bytes(encode_json(report))
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
