"""Independent OOXML readback and dry-mass interpretation diagnostics; no PDE run."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from scipy.special import exp1
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT/'q3_refinement_delivery'
OUT = Path(__file__).resolve().parent
NS = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def col(i):
    return chr(ord('A')+i)


def compare(a,b):
    assert a.shape == b.shape
    assert np.isfinite(a).all() and np.isfinite(b).all()
    return {'max_abs_difference':float(np.max(np.abs(a-b))), 'four_decimal_mismatches':sum(f'{x:.4f}'!=f'{y:.4f}' for x,y in zip(a.ravel(),b.ravel()))}


def main():
    z=np.load(PKG/'output/solution.npz')
    times=z['time_s']; a=z['profile_TC']; expected=a[1:,:,1]
    assert a.shape==(3450,21,2) and np.isfinite(a).all()
    assert np.array_equal(times[:-1],np.arange(0,206881,60))
    assert abs(times[-1]-206906.76)<1e-8
    with zipfile.ZipFile(PKG/'output/result3.xlsx') as f:
        assert f.testzip() is None
        sheets=ET.fromstring(f.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS)
        assert len(sheets)==1 and sheets[0].get('name')=='Sheet1'
        shared=[]
        if 'xl/sharedStrings.xml' in f.namelist():
            shared=[''.join(e.itertext()) for e in ET.fromstring(f.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        xml=ET.fromstring(f.read('xl/worksheets/sheet1.xml'))
        elements=xml.findall('s:sheetData/s:row/s:c',NS)
        cells={e.get('r'):e for e in elements}
        assert len(cells)==len(elements), 'Duplicate coordinates'
        allowed={f'{col(j)}{i}' for i in range(1,3451) for j in range(22)}
        assert set(cells)==allowed
        assert not xml.findall('.//s:f',NS)
        def value(coord):
            e=cells[coord];typ=e.get('t','n')
            if typ=='inlineStr':return ''.join(e.find('s:is',NS).itertext())
            s=e.find('s:v',NS).text
            if typ=='s':return shared[int(s)]
            if typ=='str':return s
            assert typ=='n', (coord,typ)
            v=float(s)
            assert np.isfinite(v),coord
            return v
        header=value('A1')
        assert header==r'时间/s\到药材中心的距离/cm'
        actual_times=np.array([value(f'A{i}') for i in range(2,3451)])
        actual_C=np.array([[value(f'{col(j)}{i}') for j in range(1,22)] for i in range(2,3451)])
        radii=np.array([value(f'{col(j)}1') for j in range(1,22)])
        assert np.array_equal(actual_times,times[1:])
        assert np.array_equal(actual_C,expected)
        assert np.allclose(radii,np.arange(21)*.1,rtol=0,atol=1e-15)
        styles=ET.fromstring(f.read('xl/styles.xml'))
        formats={int(e.get('numFmtId')):e.get('formatCode') for e in styles.findall('s:numFmts/s:numFmt',NS)}
        xfs=styles.findall('s:cellXfs/s:xf',NS)
        moisture_formats={formats.get(int(xfs[int(cells[f'{col(j)}{i}'].get('s','0'))].get('numFmtId'))) for i in range(2,3451) for j in range(1,22)}
        assert moisture_formats=={'0.0000'}
    refs={}
    for key,stem in [('historical160_BDF','reference160_bdf_historical'),('historical80_Radau','reference80_radau_historical')]:
        ref=np.load(PKG/f'validation/numeric/{stem}.npz')
        ep=np.load(PKG/f'validation/numeric/reference{160 if key.startswith("historical160") else 80}_official_endpoint_historical.npz')
        assert np.array_equal(ref['time_s'][:-1],times[:-1])
        arr=np.concatenate([ref['sample_TC'][:-1],ep['profile_TC'].reshape(1,21,2)])
        refs[key]=compare(expected,arr[1:,:,1])
        assert refs[key]['four_decimal_mismatches']==0
        if key=='historical80_Radau':assert np.array_equal(arr,a)
    fresh=np.load(PKG/'validation/numeric/fresh_reference80_bdf.npz')
    assert np.max(abs(fresh['time_s']-times))<1e-8
    refs['Pro_fresh80_BDF']=compare(expected,fresh['profile_TC'][1:,:,1])
    assert refs['Pro_fresh80_BDF']['four_decimal_mismatches']==0
    old=np.load(ROOT/'q3_final_delivery/output/main.npz')
    old_comparison=compare(expected,old['sample_TC'][1:,:,1])
    assert old_comparison['four_decimal_mismatches']==8
    event=json.loads((PKG/'output/end_event.json').read_text(encoding='utf-8'))
    assert abs(times[-1]-event['execution_s'])<1e-8 and np.max(z['execution_full_TC'][:,1])<.15
    V=np.pi*.02**2*.25;rd0=(650+128*2.55)/3.55; md0=V*rd0
    q2=[]
    for n in [1280,2560]:
        q=np.load(ROOT/f'review_q2_20260911/reproduced/validation/fv_n{n}.npz')
        i=np.flatnonzero(q['snapshot_times_s']==10800)[0]
        C=q['snapshots_moisture_dry_basis'][i]; w=q['internal_weights_rdr']
        mass=2*np.pi*.25*(w@((650+128*C)/(1+C)))
        q2.append({'N':n,'time_s':10800,'apparent_dry_mass_g':float(mass*1000),'gain_percent':float(100*(mass/md0-1))})
    def F(C):return C*np.exp(-.45/C)-.45*exp1(.45/C)
    C=z['execution_full_TC'][:,1]; n=len(C)-1
    x=(1-np.cos(np.arange(n+1)*np.pi/n))/2
    bary=(-1.)**np.arange(n+1);bary[[0,-1]]*=.5
    q3=[]
    for count in [128,256]:
        nodes,w=np.polynomial.legendre.leggauss(count); nodes=(nodes+1)/2;w=w/2
        weights=bary[None,:]/(nodes[:,None]-x[None,:]); weights/=weights.sum(axis=1)[:,None]
        U=weights@F(C)
        cq=np.array([brentq(lambda c:F(c)-u,1e-5,3,xtol=1e-14) for u in U])
        md=V*(w@((650+128*cq)/(1+cq)))
        q3.append({'gauss_nodes':count,'apparent_dry_mass_g':float(md*1000),'gain_percent':float(100*(md/md0-1))})
    assert abs(q3[0]['apparent_dry_mass_g']-q3[1]['apparent_dry_mass_g'])<1e-6
    out={'scope':'Fresh independent OOXML readback, stored trajectory comparisons and scalar spatial quadrature only; no PDE rerun.',
         'xlsx':{'header':header,'data_rows':3449,'moisture_cells':72429,'all_values_exact':True,'finite_unique_cells':True,'moisture_format':'0.0000'},
         'official_provenance':'Exact historical Radau trajectory plus historical real endpoint continuation; not a new physical model.',
         'references':refs,'old_FV_comparison':old_comparison,'initial_dry_mass_g':md0*1000,'q2_dry_mass':q2,'q3_dry_mass':q3,
         'mass_interpretation':'Diagnostic contradiction if empirical rho is actual wet bulk density in fixed volume; these are not actual dry material generation predictions. Q2 uses old full FV snapshots; Q3 uses the refined official full spectral endpoint, interpolating F(C) in x=(r/R)^2 then inverting F before integration.'}
    (OUT/'numeric_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
