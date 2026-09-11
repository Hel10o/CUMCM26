"""Independent stdlib OOXML readback: numeric values, decimal formats and all endpoints."""
from __future__ import annotations
import argparse,json,zipfile,re
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from q2_core import NS,read_workbook_values,file_hashes
from q2_finalize import dec4

def audit(out,require_paper=True):
    out=Path(out);path=out/'result2.xlsx';z=np.load(out/'q2_unrounded.npz',allow_pickle=False)
    sheets=read_workbook_values(path);assert list(sheets)==['温度','水分浓度']
    with zipfile.ZipFile(path) as arc:
        assert arc.testzip() is None
        styles=ET.fromstring(arc.read('xl/styles.xml'))
    custom={int(a.attrib['numFmtId']):a.attrib['formatCode'] for a in styles.findall('s:numFmts/s:numFmt',NS)}
    xfs=[int(a.attrib.get('numFmtId',0)) for a in styles.find('s:cellXfs',NS)]
    report={'all_passed':False,'sheet_names':list(sheets),'total_result_values':0,'sheets':{},'xlsx_hash':file_hashes(path)}
    cols=[chr(i) for i in range(ord('B'),ord('V')+1)];t=z['time_s'][1:];r=z['radius_cm']
    for name,key in [('温度','temperature_degC'),('水分浓度','moisture_dry_basis')]:
        a=sheets[name];d=a['values'];nt=len(t)
        assert len(d)==(nt+1)*22,(name,len(d))
        assert isinstance(d['A1'],str) and 's' in d['A1'] and 'cm' in d['A1']
        assert np.array_equal([d[f'A{i+2}'] for i in range(nt)],t)
        assert np.allclose([d[c+'1'] for c in cols],r,rtol=0,atol=1e-14)
        allvals=np.array([[d[f'{c}{j}'] for c in cols] for j in range(2,nt+2)],float)
        assert np.isfinite(allvals).all()
        addresses=(f'{c}{j}' for j in range(2,nt+2) for c in cols)
        for address in addresses:
            assert a['types'][address]=='n',(name,address,'nonnumeric')
            assert custom.get(xfs[a['styles'][address]],'')=='0.0000',(name,address,'bad number format')
        expected=dec4(z[key][1:]);assert np.array_equal(allvals,expected)
        maxround=float(np.max(abs(allvals-z[key][1:])));assert maxround<=.00005+1e-12
        for ti in (1800,3600,5400,7200,9000,10800):
            for ri in (0,5,10,15,20):assert allvals[ti-1,ri]==dec4(z[key][ti,ri])
        report['total_result_values']+=allvals.size
        report['sheets'][name]={'result_rows':nt,'result_columns':21,'first_time_s':d['A2'],
            'last_time_s':d[f'A{nt+1}'],'first_radius_cm':d['B1'],'last_radius_cm':d['V1'],
            'top_left_result':d['B2'],'bottom_right_result':d[f'V{nt+1}'],
            'all_numeric_finite':True,'all_result_formats_0000':True,'exact_rounded_raw_match':True,
            'maximum_rounding_difference':maxround,'no_missing_ellipsis_or_formulas':True}
    assert report['total_result_values']==453600
    for name,key in [('temperature','temperature_degC'),('moisture','moisture_dry_basis')]:
        c=np.loadtxt(out/f'table_{name}.csv',delimiter=',',skiprows=1)
        assert np.array_equal(c[:,0],np.arange(.5,3.01,.5))
        assert np.array_equal(c[:,1:],dec4(z[key][np.ix_(np.arange(1800,10801,1800),np.arange(0,21,5))]))
    paper=out/'第二问论文正文.md';report['paper_tables_checked']=False
    if require_paper:
        text=paper.read_text(encoding='utf-8')
        for section,key in [('### 表3','temperature_degC'),('### 表4','moisture_dry_basis')]:
            body=text.split(section,1)[1]
            lines=[s for s in body.splitlines() if re.match(r'^\| [0-9]+\.[0-9] \|',s)][:6]
            assert len(lines)==6
            vals=np.array([[float(x.strip()) for x in line.strip('|').split('|')] for line in lines])
            assert np.array_equal(vals[:,1:],dec4(z[key][np.ix_(np.arange(1800,10801,1800),np.arange(0,21,5))]))
        report['paper_tables_checked']=True;report['paper_values_checked']=60
    report['all_passed']=True
    (out/'excel_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('AUDIT PASSED',report['total_result_values'],'values; paper checked:',report['paper_tables_checked'],flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--before-paper',action='store_true')
    a=p.parse_args();audit(a.out,not a.before_paper)
