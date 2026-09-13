# 本轮静态与页面一致性检查脚本

实际执行位置：`paper/q1234_draft_v1/build/assumptions_restructure/check_revision.py`。需完整Git仓库及本轮build目录中的基线/最终PDF，脚本仅作源文、哈希、引用和页面像素核对；不导入或运行求解器。以下为实际执行的最终脚本。

```python
from pathlib import Path
from collections import Counter
import hashlib, json, re, subprocess
import fitz

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE.parents[1]
BUILD = BASE / 'build/assumptions_restructure'
EVIDENCE = BASE / 'evidence/assumptions_restructure_20260913'
SHA = '167a27455a5f2655cf07dc30471febcb67bd7a12'
def old(path):
    return subprocess.check_output(['git', 'show', SHA + ':' + path.relative_to(ROOT).as_posix()], cwd=ROOT)
def h(data): return hashlib.sha256(data).hexdigest()
def text(path): return path.read_text(encoding='utf-8')
def region(s, a, b): return s.split(a, 1)[1].split(b, 1)[0]
pm = text(BASE/'sections/problem_model.tex')
vl = text(BASE/'sections/validation_limits.tex')
pm0 = old(BASE/'sections/problem_model.tex').decode('utf-8')
vl0 = old(BASE/'sections/validation_limits.tex').decode('utf-8')
main = text(BASE/'main.tex')
ass = region(pm, r'\section{模型假设}', r'\section{符号说明}')
ass0 = region(pm0, r'\section{模型假设}', r'\section{符号说明}')
items = re.findall(r'\\item (.*?)(?=\\item|\\end\{enumerate\})', ass, re.S)
paths = [BASE/'main.tex'] + sorted((BASE/'sections').glob('*.tex')) + sorted((BASE/'tables').glob('*.tex'))
alltex = '\n'.join(text(p) for p in paths)
body_paths = [p for p in paths if p.name != 'appendix.tex']
bodytex = '\n'.join(text(p) for p in body_paths)
aux = text(BUILD/'main.aux')
log = text(BUILD/'main.log')
eq = lambda s: next(x for x in re.findall(r'\\begin\{equation\}.*?\\end\{equation\}',s,re.S) if r'\label{eq:future}' in x)
lim0 = region(vl0, r'\label{sec:limitations}', r'\subsection{改进方向与数据需求}').strip()
lim = region(vl, r'\label{sec:limitations}', r'\subsection{改进方向与数据需求}').strip()
added_geo = '题表距离按中截面径向解释并作二维校核，并非题面指定的位置。'
lim_stripped = lim.replace(added_geo, '', 1).strip()
numbers = ['45.59','4.801','9.50','164.10','0.71952','0.89029','34.7454','28.0807']
labels = re.findall(r'\\label\{([^}]+)\}',alltex)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',alltex)
unresolved = sorted(set(refs)-set(labels))
duplicate = {k:v for k,v in Counter(labels).items() if v>1}
forbidden = ['能耗','节能','可忽略','题面指定中截面']
pdf = fitz.open(BUILD/'main.pdf')
pdf0 = fitz.open(BUILD/'baseline.pdf')
pages = [p.get_text() for p in pdf]
compact = re.sub(r'\s+', '', '\n'.join(pages))
pdf_hash = h((BUILD/'main.pdf').read_bytes())
unchanged = []
changed = []
page_hashes = []
for n in range(len(pdf)):
    a = pdf[n].get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False)
    b = pdf0[n].get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False)
    same = a.width==b.width and a.height==b.height and a.samples==b.samples
    (unchanged if same else changed).append(n+1)
    page_hashes.append({'page':n+1, 'same_as_baseline':same, 'new_raster_sha256':h(a.samples), 'baseline_raster_sha256':h(b.samples)})
appendix_match = re.search(r'\\newlabel\{appendix:start\}\{\{[^}]*\}\{(\d+)\}',aux)
body_match = re.search(r'\\newlabel\{body:start\}\{\{[^}]*\}\{(\d+)\}',aux)
appendix_start = int(appendix_match.group(1)); body_start = int(body_match.group(1))
pdf_validation = json.loads(text(EVIDENCE/'pdf_validation.json'))
validation_hash_match = pdf_validation['inputs']['pdf']['sha256']==pdf_hash
manuscript_frozen = []
for p in paths:
    if p.name not in ['problem_model.tex','validation_limits.tex']:
        manuscript_frozen.append({'path':p.relative_to(ROOT).as_posix(),'unchanged':old(p)==p.read_bytes(),'sha256':h(p.read_bytes())})
tab = lambda s: region(s,r'\caption{题给物性与本文使用方式}',r'\end{table}')
aux_line = lambda label: next(line for line in aux.splitlines() if line.startswith(r'\newlabel{'+label+'}'))
automated = {
 'baseline_commit':SHA,
 'source_hashes':{p.relative_to(BASE).as_posix():h(p.read_bytes()) for p in paths},
 'assumptions_old_count':ass0.count(r'\item'),
 'assumptions_new_count':len(items),
 'bold_leads':sum(x.startswith(r'\textbf{') for x in items),
 'hardcoded_assumption_refs':re.findall(r'假设\s*[0-9一二三四五六七八九十]+', alltex),
 'assumption_ref_aux':aux_line('ass:midsection'),
 'assumption_section_aux':aux_line('sec:assumptions'),
 'future_equation_exact_bytes_equal':eq(pm).encode()==eq(pm0).encode(),
 'future_equation_still_assumptions_item8':r'\label{eq:future}' in items[7],
 'future_label_count':alltex.count(r'\label{eq:future}'),
 'future_eqref_count':alltex.count(r'\eqref{eq:future}'),
 'future_aux':aux_line('eq:future'),
 'limitations_aux':aux_line('sec:limitations'),
 'data_needs_aux':aux_line('sec:data-needs'),
 'limitations_original_entire_body_exact_bytes_equal':lim0.encode()==lim_stripped.encode(),
 'limitations_original_body_sha256':h(lim0.encode()),
 'critical_numbers':{v:{'baseline_count':lim0.count(v),'current_count':lim.count(v)} for v in numbers},
 'limitations_number_sequence_equal':re.findall(r'\d+(?:\.\d+)?',lim0)==re.findall(r'\d+(?:\.\d+)?',lim),
 'coefficient_values_moved_to_parameters':all(x not in ass and x in region(pm,r'\subsection{分问物性与参数设置}',r'\subsection{求解方法的分问衔接}') for x in [r'h_T=25\unit{W/(m^2K)}',r'h_m=8\times10^{-7}\unit{m/s}']),
 'C_definition_moved_to_symbol_row':r'$C$&材料干基含水率，$C=m_w/m_d$&' in pm and 'C=m_w/m_d' not in ass,
 'S2_caption_and_cells_exact':tab(pm)==tab(pm0),
 'top_level_titles_equal':re.findall(r'\\section\{(.*?)\}',bodytex)==re.findall(r'\\section\{(.*?)\}','\n'.join(old(p).decode('utf-8') for p in body_paths)),
 'top_level_count':len(re.findall(r'\\section\{(.*?)\}',bodytex)),
 'title_count_scope':'Body only: excludes the separate appendix section.',
 'frozen_manuscript_sources':manuscript_frozen,
 'source_forbidden_counts':{w:alltex.count(w) for w in forbidden},
 'full_pdf_forbidden_counts':{w:compact.count(w) for w in forbidden},
 'unresolved_source_refs':unresolved,
 'duplicate_labels':duplicate,
 'bad_log_lines':[x for x in log.splitlines() if re.search(r'undefined|multiply defined|Overfull|Missing character|LaTeX Error',x,re.I)],
 'total_pages':len(pdf), 'abstract_pages':body_start-1, 'body_pages':appendix_start-body_start, 'appendix_pages':len(pdf)-appendix_start+1,
 'ai_before_references_source':main.index(r'\section*{AI工具使用声明}')<main.index(r'\input{sections/references}'),
 'ai_before_references_pdf':compact.index('AI工具使用声明')<compact.index('参考文献'),
 'main_tex_exact':old(BASE/'main.tex')==(BASE/'main.tex').read_bytes(),
 'abstract_pixels_identical':1 in unchanged,
 'appendix_pixels_identical':all(n in unchanged for n in range(appendix_start,len(pdf)+1)),
 'pdf_sha256':pdf_hash, 'validation_pdf_hash_matches_final':validation_hash_match,
 'not_run':['PDE solvers','parameter scenarios','plot generators','physical model revalidation','human factual review'],
}
checks = [
 ('1','八条编号及引用',len(items)==8 and automated['bold_leads']==8 and not automated['hardcoded_assumption_refs'] and '{{1}{3}' in automated['assumption_ref_aux']),
 ('2','环境等式原位及引用',automated['future_equation_exact_bytes_equal'] and automated['future_equation_still_assumptions_item8'] and automated['future_label_count']==1 and automated['future_eqref_count']==2 and not unresolved),
 ('4','限制量化内容不变',automated['limitations_original_entire_body_exact_bytes_equal'] and automated['limitations_number_sequence_equal']),
 ('6','禁用措辞零命中',not any(automated['source_forbidden_counts'].values()) and not any(automated['full_pdf_forbidden_counts'].values())),
 ('7','编译、引用、正文页数',not duplicate and not unresolved and not automated['bad_log_lines'] and automated['body_pages']<=30 and validation_hash_match),
 ('8','摘要保持',automated['main_tex_exact'] and automated['abstract_pixels_identical'] and automated['abstract_pages']==1),
 ('9','AI声明顺序',automated['ai_before_references_source'] and automated['ai_before_references_pdf']),
]
automated['automated_contract_checks']=[{'id':i,'name':n,'pass':bool(ok)} for i,n,ok in checks]
automated['manual_semantic_checks_note']='Items 3 and 5 require semantic_audit.md/json; not inferred merely from keyword matches.'
(EVIDENCE/'source_integrity.json').write_text(json.dumps(automated,ensure_ascii=False,indent=2),encoding='utf-8')
integrity={'baseline_commit':SHA,'baseline_pdf_sha256':h((BUILD/'baseline.pdf').read_bytes()),'final_pdf_sha256':pdf_hash,'raster_dpi':108,'comparison_includes_page_footers':True,'total_pages':len(pdf),'changed_pages':changed,'unchanged_pages':unchanged,'changed_page_count':len(changed),'abstract_unchanged':1 in unchanged,'all_127_appendix_pages_unchanged':all(n in unchanged for n in range(32,159)), 'visual_review':'pending separate rendered-page review','page_raster_hashes':page_hashes}
(EVIDENCE/'page_integrity.json').write_text(json.dumps(integrity,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':automated['automated_contract_checks'],'changed_pages':changed,'pages':len(pdf),'body_pages':automated['body_pages'],'forbidden_pdf':automated['full_pdf_forbidden_counts'],'bad_log_lines':automated['bad_log_lines'],'frozen_files':all(x['unchanged'] for x in manuscript_frozen)},ensure_ascii=False,indent=2))
assert all(ok for _,_,ok in checks)
assert all(x['unchanged'] for x in manuscript_frozen)
assert automated['top_level_count']==12 and automated['top_level_titles_equal']
assert automated['S2_caption_and_cells_exact'] and automated['coefficient_values_moved_to_parameters'] and automated['C_definition_moved_to_symbol_row']

```
