"""Create a selected, commit-pinned input archive; never run submitted code or PDEs."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
COMMIT = 'c46bef5d128ee506a9934b843f6cde93a3658995'
PREFIX = 'q123_physics_offline_inputs/'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

def main():
    names = {n.decode('utf-8') for n in git('ls-tree', '-rz', '--name-only', COMMIT).split(b'\0') if n}
    manifest = json.loads(git('show', f'{COMMIT}:q123_physics_pro_handoff/source_manifest.json'))
    selected = {v['path'] for v in manifest['files']}
    prefixes = [
        'readable/', 'q123_physics_pro_handoff/', 'q3_refinement_delivery/',
        'review_q123_physics_20260911/', 'q1_complete_delivery/q1_delivery/source/',
        'q1_complete_delivery/q1_delivery/input/', 'q2_final_delivery/source/',
        'q2_final_delivery/inputs/', 'paper/q1_q2_stage/sections/',
        'q3_final_delivery/source/', 'review_q3_20260911/model/']
    selected.update(n for n in names if any(n.startswith(p) for p in prefixes))
    extras = [
        'README.md', 'AGENTS.md', 'q3_final_delivery/requirements.txt',
        'q1_complete_delivery/q1_delivery/requirements.txt', 'q1_complete_delivery/q1_delivery/run_all.py',
        'q1_complete_delivery/q1_delivery/output/run.json',
        'q1_complete_delivery/q1_delivery/output/validation/validation.json',
        'q1_complete_delivery/q1_delivery/output/validation/conditional_latent_T.npz',
        'q2_final_delivery/requirements.txt', 'q2_final_delivery/run_all.py',
        'q2_final_delivery/output/validation/validation.json',
        'q2_final_delivery/output/result_metadata.json',
        'q2_final_delivery/output/第二问论文正文.md',
        'q2_final_delivery/output/validation/axisymmetric_20_40.json',
        'q2_final_delivery/output/validation/axisymmetric_20_80.json',
        'q2_final_delivery/output/validation/axisymmetric_40_80.json',
        'review_q1_20260910/第一问审核报告.md',
        'q3_pro_handoff/evidence/literature_review.md',
        '分析与文献/1-s2.0-S0260877414002118-main.pdf',
        '分析与文献/foods-09-01577.pdf']
    missing = set(extras) - names
    if missing:
        raise FileNotFoundError(sorted(missing))
    selected.update(extras)
    payload = {name: git('show', f'{COMMIT}:{name}') for name in sorted(selected)}
    for item in manifest['files']:
        if sha(payload[item['path']]) != item['sha256']:
            raise ValueError(f'Baseline source changed: {item["path"]}')
    handoff = 'q123_physics_pro_handoff/前三问物理闭合与修正计算_Pro交接文档.md'
    targets = []
    import posixpath
    for target in re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', payload[handoff].decode('utf-8')):
        u = urlsplit(target)
        if u.scheme or not u.path:
            continue
        rel = posixpath.normpath(posixpath.join(posixpath.dirname(handoff), unquote(u.path)))
        if rel not in payload and not any(n.startswith(rel.rstrip('/') + '/') for n in payload):
            raise FileNotFoundError(f'Handoff linked input absent: {rel}')
        targets.append(rel)
    start = '''# 从这里开始：离线恢复输入包

这是原项目的精选输入快照，不是新修正结果。解压后先运行：

python verify_inputs.py

校验通过后读取 q123_physics_pro_handoff/前三问物理闭合与修正计算_Pro交接文档.md。
仓库来源提交：c46bef5d128ee506a9934b843f6cde93a3658995；其任务书引用的原材料基准：15cc3bf4afad748ab08e87bb3030ef606b1c9b9a。

本包允许以离线文件作为本轮实际读取来源，不要求先联网成功。文件哈希核验、打包方声明的Git来源、你亲自完成的在线核验必须分开记录。继续尝试GitHub时保留原始失败记录，不能将失败当作材料不存在。

范围：完整任务书直接引用的本地输入、原题与附件、Q1/Q2核心源码和未舍入基线、完整新版Q3包与最新物理审核、已有几何说明、可读论文、Adrover与da Silva原PDF。原程序保留原样且有已记录的工具缺陷，请阅读runtime审核，不直接在冻结输入目录运行会写回的旧入口。

省略：完整.git历史、大量重复网格数组、完整论文构建资产、旧交接ZIP、Chupawa约120MiB原PDF及未直接需要的其他原PDF。本包仍有Chupawa的逐页文本与原件哈希；未看到关键原页时不得声称完成该文逐式核验。任务书直接链接已检查，历史README进一步链接不保证全部离线存在。

不要运行或采信 runtime/candidate_51mekupf/untrusted_checkpoint.npz 为物理解：它属于原审核明确保留的失败合成软件夹具。

先核对题意及参数，再完成最小相容质量—能量对照。a_w或界面系数缺标定时交付有依据的条件情景，不编造唯一答案。二维与一维须在同一物理闭合和匹配网格下比较；旧几何结果不自动适用于潜热修正模型。
'''
    verifier = '''from pathlib import Path
import json, hashlib
r=Path(__file__).resolve().parent
m=json.loads((r/'INPUT_MANIFEST.json').read_text(encoding='utf-8'))
for item in m['files']:
    p=(r/item['path']).resolve()
    if not p.is_relative_to(r): raise ValueError(item['path'])
    b=p.read_bytes()
    if len(b)!=item['bytes'] or hashlib.sha256(b).hexdigest()!=item['sha256']:
        raise ValueError('Hash mismatch: '+item['path'])
print('PASS',len(m['files']),'files; declared source commit',m['declared_source_commit'])
print('This verifies file integrity, not independent online Git provenance or model correctness.')
'''
    payload['START_HERE.md'] = start.encode('utf-8')
    payload['verify_inputs.py'] = verifier.encode('utf-8')
    inventory = [{'path': name, 'bytes': len(data), 'sha256': sha(data),
                  'source': 'git:' + COMMIT if name in selected else 'recovery-generated'}
                 for name, data in sorted(payload.items())]
    payload['INPUT_MANIFEST.json'] = json_bytes({'declared_source_commit': COMMIT,
        'original_material_baseline': manifest['baseline_commit'], 'files': inventory})
    archive = OUT / 'q123_physics_offline_inputs.zip'
    if archive.exists():
        raise FileExistsError('Refusing to overwrite completed archive')
    with ZipFile(archive, 'x', compression=ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in sorted(payload.items()):
            info = ZipInfo(PREFIX + name, (2026, 9, 11, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            z.writestr(info, data)
    with ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        for name, data in payload.items():
            if z.read(PREFIX + name) != data:
                raise ValueError(name)
    report = {'status': 'pass', 'source_commit': COMMIT, 'source_files': len(selected),
              'archive_entries': len(payload), 'input_manifest_files': len(inventory),
              'direct_handoff_links_checked': len(targets),
              'zip_bytes': archive.stat().st_size, 'zip_sha256': sha(archive.read_bytes()),
              'uncompressed_bytes': sum(map(len, payload.values())),
              'scope': 'Packaging and byte verification only; no PDE or submitted script execution.'}
    (OUT / 'recovery_checks.json').write_bytes(json_bytes(report))
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
