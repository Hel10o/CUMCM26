"""Validate the actual Q1+Q2 stage PDF against frozen numerical evidence.

This reads existing outputs only. It never solves the PDE or modifies sources.
Run after build.ps1 has produced 第一二问论文阶段稿.pdf and build/main.log/aux.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PDF=HERE/'第一二问论文阶段稿.pdf'
EVIDENCE=HERE/'evidence'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path):return Path(path).relative_to(ROOT).as_posix()
def uncomment(text):return re.sub(r'(?<!\\)%[^\n]*','',text)
def compact(text):return re.sub(r'\s+','',text)

def collect_tex(entry):
    """Use reachable inputs; unused old files must not create fake labels."""
    result=[];seen=set()
    def visit(path):
        path=path.resolve()
        assert path.is_relative_to(HERE),'TeX input escapes the new stage directory'
        if path in seen:return
        assert path.is_file(),f'Missing TeX input: {path}'
        seen.add(path);result.append(path)
        text=uncomment(path.read_text(encoding='utf-8'))
        for name in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}',text):
            child=HERE/name
            if not child.suffix:child=child.with_suffix('.tex')
            visit(child)
    visit(entry)
    return result

def expected_rows(question):
    directory=(ROOT/'q1_complete_delivery/q1_delivery/output' if question==1 else ROOT/'q2_final_delivery/output')
    rows=[]
    for kind in ('temperature','moisture'):
        with (directory/f'table_{kind}.csv').open(encoding='utf-8-sig',newline='') as stream:
            rows += list(csv.reader(stream))[1:]
    return rows

def extracted_rows(text,question):
    time=r'(100|300|600|900|1200|1500|1800)' if question==1 else r'(0\.5|1\.0|1\.5|2\.0|2\.5|3\.0)'
    pattern=re.compile(r'^\s*'+time+r'\s+((?:\d+\.\d{4}\s+){4}\d+\.\d{4})\s*$')
    rows=[]
    for line in text.splitlines():
        match=pattern.fullmatch(line)
        if match:rows.append([match[1],*match[2].split()])
    return rows

def main():
    EVIDENCE.mkdir(exist_ok=True)
    report={'status':'RUNNING','scope':'Q1 and Q2 stage paper, not the complete four-question submission',
        'production_model_rerun':False,'checks':{},'validator_sha256':sha(Path(__file__))}
    def require(name,condition,details=None):
        report['checks'][name]={'passed':bool(condition),'details':details}
        assert condition,f'{name}: {details}'
    try:
        q1=EVIDENCE/'q1_asset_manifest.json'
        if not q1.exists():q1=EVIDENCE/'asset_manifest.json'
        manifests=[q1,EVIDENCE/'q2_asset_manifest.json']
        source_checks={};asset_checks={};manifest_hashes={}
        for path in manifests:
            obj=json.loads(path.read_text(encoding='utf-8'))
            manifest_hashes[relative(path)]=sha(path)
            require('manifest_has_sources_and_outputs_'+path.name,bool(obj.get('sourceSHA256')) and bool(obj.get('outputs')))
            for name,expected in obj['sourceSHA256'].items():
                p=(ROOT/name).resolve()
                source_checks[name]=p.is_file() and sha(p)==expected
            for name,info in obj['outputs'].items():
                p=(ROOT/name).resolve();expected=info if isinstance(info,str) else info['sha256']
                asset_checks[name]=p.is_file() and sha(p)==expected
                require('new_stage_asset_'+name,p.is_relative_to(HERE),str(p))
            builder=obj.get('generated_by')
            if builder and obj.get('builder_sha256'):
                p=ROOT/builder
                require('asset_builder_hash_'+path.name,p.is_file() and sha(p)==obj['builder_sha256'],builder)
        # Preserve the older Q1 physical audit's original-file commitment.
        physical=json.loads((ROOT/'q1_physical_review_evidence/calculations/physical_audit.json').read_text(encoding='utf-8'))
        for name,expected in physical['original_file_sha256'].items():
            p=ROOT/'q1_complete_delivery/q1_delivery'/name
            source_checks[relative(p)]=p.is_file() and sha(p)==expected
        # Q2 sources and official Excel are also pinned to the accepted snapshot.
        snapshot=json.loads((ROOT/'review_q2_20260911/original_delivery_hashes.json').read_text(encoding='utf-8'))
        required_q2=['output/q2_unrounded.npz','output/result2.xlsx','output/table_temperature.csv','output/table_moisture.csv']
        for name in required_q2:
            require('q2_snapshot_contains_'+name,name in snapshot)
            p=ROOT/'q2_final_delivery'/name
            source_checks[relative(p)]=p.is_file() and sha(p)==snapshot[name]
        require('frozen_source_hashes',all(source_checks.values()),[p for p,v in source_checks.items() if not v])
        require('figure_and_table_hashes',all(asset_checks.values()),[p for p,v in asset_checks.items() if not v])
        report.update(frozen_source_hash_checks=source_checks,figure_and_table_hash_checks=asset_checks,asset_manifest_sha256=manifest_hashes)
        previous=EVIDENCE/'previous_paper_hashes.json'
        if previous.exists():
            pinned=json.loads(previous.read_text(encoding='utf-8'))
            old_checks={name:(ROOT/name).is_file() and sha(ROOT/name)==expected for name,expected in pinned.items()}
            require('previous_q1_paper_assets_preserved',all(old_checks.values()),[p for p,v in old_checks.items() if not v])
            report['previous_q1_paper_hash_checks']=old_checks

        claims=[]
        for path in sorted(EVIDENCE.glob('*claim*evidence*.csv')):
            with path.open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.DictReader(stream))
            require('claim_paths_'+path.name,all(r.get('evidence_path') and (ROOT/r['evidence_path']).exists() for r in rows))
            claims.extend(rows)
        report['claim_evidence_rows']=len(claims)

        require('compiled_pdf_exists',PDF.is_file())
        extraction=EVIDENCE/'validation_support_extracted.txt'
        cmd=['pdftotext','-layout','-enc','UTF-8',str(PDF),str(extraction)]
        subprocess.run(cmd,check=True,capture_output=True)
        text=extraction.read_text(encoding='utf-8')
        pages_text=text.split('\f')
        if pages_text and not pages_text[-1].strip():pages_text.pop()
        table_report={}
        for question,count in ((1,70),(2,60)):
            actual=extracted_rows(text,question);expected=expected_rows(question)
            require(f'q{question}_pdf_table_exact_four_decimal_match',actual==expected,
                {'expected_rows':len(expected),'actual_rows':len(actual),'first_difference':next(({'row':i,'actual':a,'expected':b} for i,(a,b) in enumerate(zip(actual,expected),1) if a!=b),None)})
            require(f'q{question}_expected_value_count',sum(len(r)-1 for r in actual)==count)
            table_report[f'q{question}']={'value_count':count,'rows':actual,'exact_four_decimal_match':True}
        report.update(pdf_table_values_checked=130,pdf_table_values_by_question={'q1':70,'q2':60},pdf_tables_exact_four_decimal_match=True)
        (EVIDENCE/'validation_support_tables.json').write_text(json.dumps(table_report,ensure_ascii=False,indent=2),encoding='utf-8')

        key_q1=('33.5753','36.7856','3.2102','2.5500','1.5102','34.20','2368.89','81010.11','0.6044','0.8095','33.3008')
        key_q2=('49.8495','49.9664','1.7662','1.0081')
        mechanisms=('2.1957','1.8207','1.06','3.16')
        for number in (*key_q1,*key_q2,*mechanisms):
            require('pdf_key_number_'+number,bool(re.search(r'(?<![\d.])'+re.escape(number)+r'(?!\d)',text)))
        require('no_pdf_missing_glyph_or_unresolved_marker','??' not in text and '\ufffd' not in text)
        require('stage_disclosure','阶段记录' in text and '第三' in text and '第四' in text)
        first=compact(pages_text[0])
        require('abstract_fits_first_page','摘要' in first and '关键词' in first)
        require('q2_abstract_has_all_four_endpoints',all(n in first for n in key_q2))
        require('body_starts_after_abstract_page','问题重述与分析' not in first and any('问题重述与分析' in compact(s) for s in pages_text[1:3]))
        report['abstract_page']=1

        doc=PdfReader(PDF);pages=[]
        require('two_extractors_agree_page_count',len(doc.pages)==len(pages_text))
        for i,page in enumerate(doc.pages,1):
            width,height=float(page.mediabox.width),float(page.mediabox.height)
            require(f'a4_page_{i}',abs(width-595.28)<1 and abs(height-841.89)<1)
            s=page.extract_text() or ''
            require(f'text_page_{i}',len(s)>100,{'characters':len(s)})
            pages.append({'page':i,'characters':len(s),'width_pt':width,'height_pt':height})
        report.update(pdf=relative(PDF),pdf_sha256=sha(PDF),page_count=len(pages),pages=pages)

        log=(HERE/'build/main.log').read_text(encoding='utf-8',errors='replace')
        blockers=re.findall(r'^.*(?:Overfull \\[hv]box|undefined references|(?:Reference|Citation).+undefined|Missing character:|multiply[- ]defined labels|^! ).*$',log,re.M|re.I)
        require('no_overflow_missing_glyph_or_undefined_reference',not blockers,blockers)
        report['undefined_or_overfull_or_missing_character_warnings']=blockers
        inputs=collect_tex(HERE/'main.tex')
        source='\n'.join(uncomment(p.read_text(encoding='utf-8')) for p in inputs)
        labels=re.findall(r'\\label\s*\{([^}]+)\}',source)
        refs=re.findall(r'\\(?:ref|eqref|autoref|pageref)\*?\s*\{([^}]+)\}',source)
        require('tex_labels_unique',len(labels)==len(set(labels)))
        require('references_have_labels',set(refs)<=set(labels),sorted(set(refs)-set(labels)))
        bibkeys=re.findall(r'\\bibitem(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}',source)
        citations=[]
        for names in re.findall(r'\\(?:cite|citep|citet|autocite|parencite)\*?(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]+)\}',source):
            citations += [name.strip() for name in names.split(',')]
        require('bibliography_keys_unique',len(bibkeys)==len(set(bibkeys)))
        require('citations_have_bibliography_entries',bool(citations) and set(citations)<=set(bibkeys),sorted(set(citations)-set(bibkeys)))
        aux=(HERE/'build/main.aux').read_text(encoding='utf-8',errors='replace')
        aux_citations={k.strip() for values in re.findall(r'\\citation\{([^}]+)\}',aux) for k in values.split(',')}
        aux_bibkeys=re.findall(r'\\bibcite\{([^}]+)\}',aux)
        aux_labels=re.findall(r'\\newlabel\{([^}]+)\}',aux)
        require('compiled_citations_match_sources',set(citations)==aux_citations,{'source':sorted(set(citations)),'compiled':sorted(aux_citations)})
        require('compiled_bibliography_matches_sources',set(bibkeys)==set(aux_bibkeys))
        require('compiled_labels_include_all_source_labels',set(labels)<=set(aux_labels),sorted(set(labels)-set(aux_labels)))
        require('compiled_bibliography_unique',len(aux_bibkeys)==len(set(aux_bibkeys)))
        report['reference_checks']={'label_count':len(labels),'reference_count':len(refs),'bibliography_keys':bibkeys,
            'cited_keys':sorted(set(citations)),'unused_bibliography_entries':sorted(set(bibkeys)-set(citations)),
            'source_aux_correspondence':True}
        included_figures=[]
        for name in re.findall(r'\\includegraphics(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}',source):
            p=HERE/name
            if not p.suffix:p=p.with_suffix('.pdf')
            require('included_figure_has_verified_manifest_'+name,p.is_file() and relative(p) in asset_checks and asset_checks[relative(p)])
            included_figures.append(relative(p))
        report['included_figures']=included_figures
        report['source_sha256']={relative(p):sha(p) for p in inputs}
        report['status']='PASS: actual PDF numerical tables, frozen assets, abstract, layout log and citations checked; visual review is separate'
    except Exception as exc:
        report.update(status='FAIL',error=repr(exc))
        (EVIDENCE/'paper_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        raise
    (EVIDENCE/'paper_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'PASS','pages':report['page_count'],'pdf_table_values':130,'q1_values':70,'q2_values':60,
        'abstract_pages':1,'all_frozen_sources_unchanged':True,'references_correspond':True},ensure_ascii=False))

if __name__=='__main__':main()
