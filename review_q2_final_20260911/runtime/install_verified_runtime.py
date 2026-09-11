"""Create an independent runtime copy and apply only the reviewed run guard.

Existing destinations are always refused. No original delivery is edited.
This installs files only; it does not start a numerical calculation.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def install(destination):
    source=PROJECT/'q2_refinement_delivery/runtime'
    overlay=HERE/'overlay/source/q2_run_guard.py'
    target=Path(destination).resolve()
    if target.exists():raise FileExistsError(f'Existing destination refused: {target}')
    frozen=[PROJECT/'q2_refinement_delivery',PROJECT/'q2_final_delivery',PROJECT/'q1_complete_delivery']
    if any(target.is_relative_to(p) or p.is_relative_to(target) for p in frozen):
        raise ValueError('Destination must be independent of the preserved deliveries')
    for p in target.parents:
        if p.exists() and (p.is_symlink() or p.is_junction()):raise ValueError('Destination alias refused')
    shutil.copytree(source,target)
    shutil.copy2(overlay,target/'source/q2_run_guard.py')
    unchanged=[]
    for p in sorted((source/'source').glob('*.py')):
        if p.name=='q2_run_guard.py':continue
        assert sha(p)==sha(target/'source'/p.name)
        unchanged.append({'name':p.name,'sha256':sha(p)})
    assert sha(source/'run_all.py')==sha(target/'run_all.py')
    report={'scope':'Only runtime run guard was replaced; no PDE run or full-stage validation performed by installer.',
        'original_runtime':str(source),'guard_sha256':sha(overlay),'unchanged_scientific_source':unchanged,
        'files':{p.relative_to(target).as_posix():sha(p) for p in sorted(target.rglob('*')) if p.is_file()}}
    (target/'VERIFIED_RUNTIME_PROVENANCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'installed_to':str(target),'scientific_modules_unchanged':len(unchanged),'numerical_calculation_started':False},ensure_ascii=False,indent=2))
    return target

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,default=PROJECT/'q2_runtime_verified')
    install(parser.parse_args().destination)
