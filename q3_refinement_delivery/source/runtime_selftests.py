from __future__ import annotations
import json, shutil, sys, tempfile, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from validate_xlsx import validate
from q3_refined_reference import run as solve_run
from build_documents import fmt
from export_workbook import export_portable

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
ET.register_namespace('x',NS)

def mutate_sheet(src:Path,dst:Path,mode:str):
    with zipfile.ZipFile(src,'r') as zin,zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data=zin.read(info.filename)
            if info.filename=='xl/worksheets/sheet1.xml':
                root=ET.fromstring(data)
                if mode=='extra':
                    row=next(r for r in root.findall(f'.//{{{NS}}}row') if r.attrib.get('r')=='2')
                    c=ET.SubElement(row,f'{{{NS}}}c',{'r':'W2','t':'n'});v=ET.SubElement(c,f'{{{NS}}}v');v.text='999'
                    data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
                elif mode=='header':
                    c=next(c for c in root.findall(f'.//{{{NS}}}c') if c.attrib.get('r')=='A1')
                    for child in list(c):c.remove(child)
                    c.attrib['t']='inlineStr';isn=ET.SubElement(c,f'{{{NS}}}is');t=ET.SubElement(isn,f'{{{NS}}}t');t.text='时间/min\\到药材中心的距离/cm'
                    data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            zout.writestr(info,data)

def main():
    temp=Path(tempfile.mkdtemp(prefix='q3_refinement_tests_'))
    probes=[]
    try:
        xlsx=ROOT/'output/result3.xlsx';sol=ROOT/'output/solution.npz'
        probes.append({'name':'original_xlsx_accepts','passed':bool(validate(xlsx,sol)['passed'])})
        for mode in ['extra','header']:
            bad=temp/f'{mode}.xlsx';mutate_sheet(xlsx,bad,mode)
            rejected=False;reason=''
            try:validate(bad,sol)
            except Exception as e:rejected=True;reason=str(e)
            probes.append({'name':f'xlsx_{mode}_rejected','passed':rejected,'reason':reason})
        # Orphan-NPZ overwrite guard: check occurs before any PDE work.
        prefix=temp/'orphan';prefix.with_suffix('.npz').write_bytes(b'keep-me');before=prefix.with_suffix('.npz').read_bytes();rejected=False
        try:solve_run(n=4,out=prefix,input_file=ROOT/'inputs/attachment1.xlsx',method='BDF')
        except FileExistsError:rejected=True
        probes.append({'name':'orphan_npz_not_overwritten','passed':rejected and prefix.with_suffix('.npz').read_bytes()==before})
        # Exporter must reject an existing target.
        target=temp/'exists.xlsx';target.write_bytes(b'keep');before=target.read_bytes();rejected=False
        try:export_portable(ROOT,target)
        except FileExistsError:rejected=True
        probes.append({'name':'export_existing_target_rejected','passed':rejected and target.read_bytes()==before})
        # Dynamic report fixture: changing event to 60 h must change generated prose.
        fr=temp/'fixture';(fr/'output').mkdir(parents=True);(fr/'validation/scenarios').mkdir(parents=True);(fr/'validation/numeric').mkdir(parents=True);(fr/'validation').mkdir(exist_ok=True)
        for rel in ['output/end_event.json','validation/scenarios/scenario_comparison_refined.json','validation/numeric/rounding_stability.json','validation/xlsx_readback.json','output/table5.md']:
            d=fr/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,d)
        ev=json.loads((fr/'output/end_event.json').read_text(encoding='utf-8'));ev['critical_s']=216000.;ev['execution_s']=216000.36;ev['execution_max']=0.1499;(fr/'output/end_event.json').write_text(json.dumps(ev,ensure_ascii=False),encoding='utf-8')
        docs=fmt(fr);text=docs['README.md'];dynamic=('60.0000 h' in text and '206906.389932' not in text)
        probes.append({'name':'report_uses_current_event_data','passed':dynamic})
        obj={'passed':all(p['passed'] for p in probes),'probes':probes}
        print(json.dumps(obj,ensure_ascii=False,indent=2));return obj
    finally:shutil.rmtree(temp,ignore_errors=True)

if __name__=='__main__':
    obj=main();out=ROOT/'validation/runtime/selftests.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');raise SystemExit(0 if obj['passed'] else 1)
