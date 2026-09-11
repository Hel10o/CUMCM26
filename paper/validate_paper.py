"""Check the rendered paper against frozen Q1 sources; no PDE rerun or data edit."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PDF = HERE / '第一问论文阶段稿.pdf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assets = json.loads((HERE/'evidence/asset_manifest.json').read_text(encoding='utf-8'))
    checks = {p: sha(ROOT/p) == h for p,h in assets['sourceSHA256'].items()}
    asset_checks = {p: sha(ROOT/p) == info['sha256'] for p,info in assets['outputs'].items()}
    assert all(asset_checks.values()), 'An included figure or table changed after asset validation.'
    with (HERE/'evidence/claim_evidence.csv').open(encoding='utf-8-sig',newline='') as stream:
        claims = list(csv.DictReader(stream))
    assert all((ROOT/r['evidence_path']).exists() for r in claims), 'Missing claim evidence.'
    pro = json.loads((ROOT/'q1_physical_review_evidence/calculations/physical_audit.json').read_text(encoding='utf-8'))
    for p,h in pro['original_file_sha256'].items():
        full = ROOT/'q1_complete_delivery/q1_delivery'/p
        checks[str(full.relative_to(ROOT)).replace('\\','/')] = sha(full) == h
    assert all(checks.values()), 'Frozen source changed; audit dependency must be refreshed.'
    extracted = HERE/'build/extracted.txt'
    subprocess.run(['pdftotext','-layout','-enc','UTF-8',str(PDF),str(extracted)],check=True)
    text = extracted.read_text(encoding='utf-8')
    rows = []
    pattern = r'^\s*(100|300|600|900|1200|1500|1800)\s+((?:\d+\.\d{4}\s+){4}\d+\.\d{4})\s*$'
    for line in text.splitlines():
        match = re.fullmatch(pattern,line)
        if match:
            rows.append([match[1]] + match[2].split())
    expected = []
    for name in ('temperature','moisture'):
        path = ROOT/f'q1_complete_delivery/q1_delivery/output/table_{name}.csv'
        with path.open(encoding='utf-8-sig',newline='') as stream:
            expected += list(csv.reader(stream))[1:]
    assert rows == expected, 'PDF table extraction differs from formal table values.'
    for number in ('33.5753','36.7856','3.2102','2.5500','1.5102','34.20','2368.89','81010.11','0.6044','0.8095','33.3008'):
        assert number in text, f'Missing key result {number}'
    assert '??' not in text and '\ufffd' not in text
    assert '本稿已完成第一问' in text and '阶段记录' in text
    doc = PdfReader(PDF)
    pages = []
    for i,page in enumerate(doc.pages,1):
        w,h = float(page.mediabox.width),float(page.mediabox.height)
        assert abs(w-595.28)<1 and abs(h-841.89)<1, 'Page is not A4.'
        s = page.extract_text()
        assert len(s)>100, 'Empty or non-text page.'
        pages.append({'page':i,'characters':len(s),'width_pt':w,'height_pt':h})
    log = (HERE/'build/main.log').read_text(encoding='utf-8',errors='replace')
    blockers = re.findall(r'^.*(?:Overfull \\[hv]box|undefined references|(?:Reference|Citation).+undefined|Missing character:|^! ).*$',log,re.M)
    assert not blockers, blockers
    inputs = [HERE/'main.tex',*sorted((HERE/'sections').glob('*.tex')),*sorted((HERE/'tables').glob('*.tex'))]
    labels = re.findall(r'\\label\{([^}]+)\}','\n'.join(p.read_text(encoding='utf-8') for p in inputs))
    assert len(labels)==len(set(labels))
    report = {
        'status':'PASS: numerical tables and document structure checked; visual inspection recorded separately',
        'pdf': str(PDF.relative_to(ROOT)).replace('\\','/'), 'pdf_sha256':sha(PDF),
        'page_count':len(pages),'pages':pages,'pdf_table_values_checked':70,
        'pdf_tables_exact_four_decimal_match':True,'frozen_source_hash_checks':checks,
        'figure_and_table_hash_checks':asset_checks,'claim_evidence_rows':len(claims),
        'undefined_or_overfull_or_missing_character_warnings':blockers,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in inputs},
        'scope':'Partial paper: Q1 and preliminary sections; not complete competition submission',
        'production_model_rerun':False,
    }
    (HERE/'evidence/paper_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'PASS','pages':len(pages),'pdf_table_values':70,'all_frozen_sources_unchanged':True},ensure_ascii=False))

if __name__ == '__main__':
    main()
