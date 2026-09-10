"""Independent, read-only Q1 result artifact audit. No project modules imported."""
from pathlib import Path
import csv, hashlib, json, re, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'q1_complete_delivery/q1_delivery'
OUT = BASE / 'output'
DEST = Path(__file__).resolve().parent
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def workbook(path):
    result = {}
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels = {x.get('Id'): x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        st = ET.fromstring(z.read('xl/styles.xml'))
        fmts = {int(x.get('numFmtId')): x.get('formatCode') for x in st.findall('s:numFmts/s:numFmt', NS)}
        xfs = list(st.find('s:cellXfs', NS))
        for sh in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS):
            path = rels[sh.get(RID)]
            path = path.lstrip('/') if path.startswith('/') else 'xl/' + path
            tree = ET.fromstring(z.read(path))
            values, styles, types = {}, {}, {}
            for c in tree.findall('s:sheetData/s:row/s:c', NS):
                addr, typ = c.get('r'), c.get('t', 'n')
                raw = c.find('s:v', NS)
                if typ == 's': value = shared[int(raw.text)]
                elif typ == 'inlineStr': value = ''.join(c.find('s:is', NS).itertext())
                elif raw is None: value = None
                elif typ == 'n': value = float(raw.text)
                else: value = raw.text
                values[addr], types[addr] = value, typ
                fmtid = int(xfs[int(c.get('s', 0))].get('numFmtId', 0))
                styles[addr] = fmts.get(fmtid, str(fmtid))
                assert c.find('s:f', NS) is None, (path, addr, 'formula')
            last_row = max(int(re.search(r'\d+$', a).group()) for a in values)
            last_col = max((re.match(r'[A-Z]+', a).group() for a in values), key=lambda x:(len(x), x))
            result[sh.get('name')] = {'values': values, 'styles': styles, 'types': types,
                'dimension': f'A1:{last_col}{last_row}',
                'merged': [x.get('ref') for x in tree.findall('s:mergeCells/s:mergeCell', NS)]}
    return result

def main():
    report = {'audit_python': sys.version, 'audit_numpy': np.__version__, 'production_rerun': False}
    srcs = [('附件1.xlsx', ROOT/'A题/附件/附件1.xlsx'),
            ('result1_template.xlsx', ROOT/'A题/附件/附件3/result1.xlsx')]
    report['input_preservation'] = {n: {'sha256': sha(BASE/'input'/n), 'original_sha256': sha(p),
        'byte_identical': (BASE/'input'/n).read_bytes() == p.read_bytes()} for n,p in srcs}
    assert all(x['byte_identical'] for x in report['input_preservation'].values())
    template = workbook(BASE/'input/result1_template.xlsx')
    book = workbook(OUT/'result1.xlsx')
    report['workbook_sha256'] = sha(OUT/'result1.xlsx')
    report['template'] = {k: {'dimension': v['dimension'], 'nonempty_cells': {a:b for a,b in v['values'].items() if b is not None}, 'merged': v['merged']} for k,v in template.items()}
    assert list(book) == list(template) == ['温度','水分浓度']
    z = dict(np.load(OUT/'q1_unrounded.npz'))
    assert np.array_equal(z['time_s'], np.arange(1801))
    assert np.allclose(z['radius_cm'], np.arange(21)/10, rtol=0, atol=1e-14)
    paper = (OUT/'第一问论文正文.md').read_text(encoding='utf-8')
    matched = re.findall(r'^\| (100|300|600|900|1200|1500|1800) \| (.+) \|$', paper, flags=re.M)
    assert len(matched) == 14, len(matched)
    times = np.array([100,300,600,900,1200,1500,1800])
    report['sheets'] = {}
    for k,(name,key,stub) in enumerate([('温度','temperature_degC','temperature'),('水分浓度','moisture_dry_basis','moisture')]):
        v, sty, typ = book[name]['values'], book[name]['styles'], book[name]['types']
        assert book[name]['dimension'] == 'A1:V1801'
        assert not book[name]['merged']
        assert np.array_equal([v[f'A{i}'] for i in range(2,1802)], np.arange(1,1801))
        assert np.allclose([v[f'{chr(j+66)}1'] for j in range(21)],np.arange(21)/10,rtol=0,atol=1e-14)
        addresses = [[f'{chr(j+66)}{i}' for j in range(21)] for i in range(2,1802)]
        arr = np.array([[v[a] for a in row] for row in addresses])
        assert arr.shape == (1800,21) and np.isfinite(arr).all()
        assert all(sty[a] == '0.0000' and typ[a] == 'n' for row in addresses for a in row)
        rounded = np.array([[float(f'{x:.4f}') for x in row] for row in z[key][1:]])
        assert np.array_equal(arr, rounded)
        assert not any(isinstance(value,str) and ('...' in value or '…' in value) for value in v.values())
        assert len([value for value in v.values() if value is not None]) == 39622
        raw_csv = np.loadtxt(OUT/f'{stub}_unrounded.csv', delimiter=',', skiprows=1)
        assert np.array_equal(raw_csv[:,0], z['time_s'])
        assert np.array_equal(raw_csv[:,1:], z[key])
        table_csv = np.loadtxt(OUT/f'table_{stub}.csv', delimiter=',', skiprows=1)
        assert np.array_equal(table_csv[:,0], times)
        assert np.array_equal(table_csv[:,1:], arr[times-1,::5])
        paper_rows = matched[k*7:(k+1)*7]
        assert np.array_equal([int(x[0]) for x in paper_rows],times)
        paper_values = np.array([[float(val.strip()) for val in row[1].split('|')] for row in paper_rows])
        assert all(re.fullmatch(r'\d+\.\d{4}',val.strip()) for row in paper_rows for val in row[1].split('|'))
        assert np.array_equal(paper_values,table_csv[:,1:])
        ref_path, ref_key = (('production_thermal_Bessel800.npz','temperature_degC') if k==0 else ('independent_cheb_N240.npz','C'))
        ref = np.load(OUT/'validation'/ref_path)[ref_key]
        ref_round = np.array([[float(f'{x:.4f}') for x in row] for row in ref[1:]])
        report['sheets'][name] = {'numeric_result_count': arr.size,'all_cells_correct_format': True,
            'time_s': [1,1800,1], 'radius_cm': [0,2,0.1], 'csv_raw_bitwise_equal_npz': True,
            'paper_table_directly_parsed_equal_excel_csv': True,
            'max_excel_rounding_difference': float(np.max(np.abs(arr-z[key][1:]))),
            'saved_independent_reference_four_decimal_mismatches': int(np.count_nonzero(arr != ref_round)),
            'saved_independent_reference_max_difference': float(np.max(np.abs(z[key]-ref))),
            'values_at_1800': arr[-1,::5].tolist()}
        assert np.array_equal(arr,ref_round)
    figure_links = re.findall(r'!\[[^\]]*\]\(([^)]+)\)',paper)
    assert len(figure_links)==8 and all((OUT/p).exists() for p in figure_links)
    figure_manifest=json.loads((OUT/'figures/figure_manifest.json').read_text(encoding='utf-8'))
    assert len(figure_manifest['files'])==8
    assert all((OUT/'figures'/f'{p}.{ext}').exists() for p in figure_manifest['files'] for ext in ['png','svg'])
    report['figures']={'markdown_image_links':8,'png_svg_pairs':8,'all_exist':True}
    manifest=json.loads((BASE/'evidence/delivery_manifest.json').read_text(encoding='utf-8'))
    report['delivery_manifest']={'file_count':len(manifest),'missing':[],'hash_mismatch':[]}
    for path,record in manifest.items():
        if not (BASE/path).exists(): report['delivery_manifest']['missing'].append(path)
        elif sha(BASE/path)!=record['sha256']:report['delivery_manifest']['hash_mismatch'].append(path)
    report['all_assertions_passed']=True
    (DEST/'artifact_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='template'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
