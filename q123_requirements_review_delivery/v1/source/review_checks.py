#!/usr/bin/env python3
"""Read-only source/template inspection plus algebra and synthetic contract tests.
NOT a PDE rerun; NOT numerical verification of inherited drying results.
Output is refused if it already exists unless --overwrite is explicit.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, platform, sys, time, zipfile
from pathlib import Path
from decimal import Decimal as D
sys.dont_write_bytecode = True  # Also protects archived source paths on Windows.
import numpy as np
from given_model import properties, reference_dry_density, surface_fluxes

ROOT = Path(__file__).resolve().parents[1]
PIN = 'dc5d9cb5f47e783f57b78d07d6bac37cf269c658'
EXPECTED = {
    '模型推导与假设契约.md':'e5c102634f6fe528e2b590aeebc86a343e62fff9',
    '前三问二维与潜热影响评估.md':'af17e81b2df180e37793ebb4f160e1d141c5804f',
    '最终建模思路.md':'c2023686fa64be16717b18b48769322c563f3396',
    '参数与文献证据表.md':'d732bd5cef6de8440bda65b35002f52f8044f37c',
    '最终模型选择表.csv':'9344e49ba454b2190d65817ec23cc6fbd3071ce2',
    'source/model.py':'ef9bb86adec1a878aef1c6f3ef54af7d438f9fb5',
    'inputs/environment_extracted.csv':'d55880786a62ff55933c045998a6a7de033b83c5',
}

def hashes(p: Path) -> dict:
    b=p.read_bytes()
    return dict(bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
                git_blob_sha1=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest())


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--overwrite', action='store_true')
    ns=ap.parse_args()
    if ns.out.exists() and not ns.overwrite:
        raise FileExistsError(f'Refusing to overwrite {ns.out}')
    tic=time.perf_counter()
    before={str(p.relative_to(ROOT)):hashes(p) for p in (ROOT/'sources').rglob('*') if p.is_file()}
    verified=[]
    for rel, sha in EXPECTED.items():
        h=hashes(ROOT/'sources/previous_delivery'/rel)
        assert h['git_blob_sha1']==sha, rel
        verified.append(dict(path=rel, **h, github_blob_sha1=sha, matches=True))
    env=np.loadtxt(ROOT/'sources/previous_delivery/inputs/environment_extracted.csv', delimiter=',', skiprows=1)
    assert env.shape==(241,3) and np.array_equal(env[:,0], np.arange(241)*60.)
    environment=dict(records=len(env), time_range_s=[float(env[0,0]),float(env[-1,0])],
                     last_hour_61_sample_mean=env[180:,1:].mean(axis=0).tolist(),
                     status='Extracted CSV matched to current Git blob; original attachment1.xlsx NOT independently parsed this round.')
    # Recovered original template2; template1 has the SAME blob in GitHub metadata.
    xp=ROOT/'sources/result2_retrieved.xlsx'
    hx=hashes(xp)
    assert hx['git_blob_sha1']=='03cefc945518800f20cdec88f821ebc6c76edcfb'
    with zipfile.ZipFile(xp) as z:
        assert z.testzip() is None
    from artifact_tool import Blob, SpreadsheetFile
    w=SpreadsheetFile.import_xlsx(Blob.load(str(xp)))
    sheets=[json.loads(x) for x in w.inspect({'kind':'sheet','include':'id,name'}).ndjson.splitlines() if x.strip()]
    tables=[]
    for sh in sheets:
        lines=w.inspect({'kind':'table','range':f"{sh['name']}!A1:F5",'include':'values,formulas',
                         'table_max_rows':5,'table_max_cols':6}).ndjson.splitlines()
        tables.extend(json.loads(x) for x in lines if x.strip())
    for table in tables:
        assert table['values'][0]==['时间\\到药材中心的距离',0,0.1,0.2,'…',2]
        assert [r[0] for r in table['values'][1:]]==[1,2,3,'…']
    template=dict(**hx, zip_crc_pass=True, sheets=sheets, tables=tables,
                  findings=['No final time given in template', 'No z coordinate given',
                            'Example time rows start at 1, not 0',
                            'Result1/2 identical Git objects; only result2 retrieved as binary',
                            'Result3 metadata/text read; binary NOT independently parsed'])
    # Pure constitutive calls to the inherited model, no Model construction/PDE.
    spec=importlib.util.spec_from_file_location('inherited_review_model', ROOT/'sources/previous_delivery/source/model.py')
    old=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=old
    spec.loader.exec_module(old)
    property_comparison=[]
    for q in (1,2,3):
        obj=object.__new__(old.Model)
        obj.cfg=old.Config(question=1 if q==1 else 23, baseline=False)
        obj.rhod=reference_dry_density(q)
        cs=np.array([2.55,0.15]); ts=np.array([28.,50.])
        sf,kf,df=obj.properties(ts,cs)
        new=properties(q,ts,cs)
        assert np.array_equal(kf,new['k']) and np.allclose(df,new['D'], rtol=2e-14, atol=0)
        for i in range(2):
            property_comparison.append(dict(question=q,T_degC=float(ts[i]),C=float(cs[i]),
                S_given_J_m3_K=float(new['S'][i]), S_F_J_m3_K=float(sf[i]),
                ratio_F_to_given=float(sf[i]/new['S'][i]),
                rho_given=float(new['rho'][i]),cp_given=float(new['cp'][i]),
                k_equal=True,D_equal=True))
    c0=D('2.55'); cl=D('4186'); cp1=D('2600')
    cd_inferred=cp1*(1+c0)-cl*c0
    assert cd_inferred==D('-1444.30')
    identity=[]
    for c in [D('.15'),D('1'),c0]:
        assert (D('650')+D('128')*c)/(1+c) == D('128')+D('522')/(1+c)
        a=D('1450')+D('2736')*c/(1+c)
        b=(D('1450')+D('4186')*c)/(1+c)
        assert abs(a-b)<D('1e-22')
        identity.append(dict(C=str(c), dry_density_from_empirical=str((D('650')+D('128')*c)/(1+c)),
                             cp_equivalence_difference=str(a-b)))
    # Synthetic API tests: NOT drug-specific equilibrium data or drying simulations.
    synthetic=[]
    try:
        surface_fluxes(1,0.,28.,2.55,28.,.02,None)
        raise AssertionError('Missing mapping was silently accepted')
    except ValueError as exc:
        synthetic.append(dict(test='Missing equilibrium mapping rejected',passed=True,message=str(exc)))
    for label,ce in [('outward',2.4),('zero',2.55),('inward',2.7)]:
        f=surface_fluxes(1,0.,28.,2.55,28.,.02,lambda **kw:ce)
        j=float(f['j_out']); qlat=float(f['qlatent_out'])
        assert (j>0 if label=='outward' else j<0 if label=='inward' else j==0)
        assert j*qlat>=0
        synthetic.append(dict(test=label,passed=True,synthetic_Ce=ce,j_kg_m2_s=j,
                              latent_W_m2=qlat,status='Synthetic sign test only; NOT a material parameter'))
    after={str(p.relative_to(ROOT)):hashes(p) for p in (ROOT/'sources').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    before={k:v for k,v in before.items() if '__pycache__' not in k}
    assert before==after
    result=dict(scope='Source, template, constitutive algebra and synthetic API checks only. No PDE, no new drying time.',
       github_commit=PIN, python=sys.version, platform=platform.platform(), command=sys.argv,
       executed_source_hashes={str(p.relative_to(ROOT)):hashes(p) for p in [Path(__file__), ROOT/'source/given_model.py']},
       verified_sources=verified, environment=environment,template=template,
       algebra=dict(Q1_additive_dry_component_heat_capacity=str(cd_inferred),
                    status='Rejects only an imposed additive constant-free-water composition, not the given cp.',
                    identities=identity), property_comparison=property_comparison,synthetic_tests=synthetic,
       preserved_source_files=len(before),sources_unchanged=True, elapsed_s=time.perf_counter()-tic,
       current_PDE_run=False,inherited_PDE_results_revalidated=False)
    ns.out.parent.mkdir(parents=True, exist_ok=True)
    ns.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PASS',checks='source/template/algebra only',elapsed_s=result['elapsed_s'],
                         output=str(ns.out)),ensure_ascii=False))

if __name__=='__main__':
    main()
