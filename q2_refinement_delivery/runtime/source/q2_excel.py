"""Q2 XLSX: artifact_tool creates every result cell and its numeric format.
For memory-limited runtimes, generate one populated worksheet per temporary
package, then assemble the immutable OOXML worksheet parts after verifying
that the two style/shared-string tables are identical. No cell values or
format IDs are changed during this packaging step.
"""
from __future__ import annotations
import argparse,os,subprocess,sys,zipfile,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

FIELDS=[('温度','temperature_degC'),('水分浓度','moisture_dry_basis')]

def export_part(template,raw,out,field):
    from artifact_tool import Workbook,SpreadsheetFile
    from q2_core import read_workbook_values
    assert list(read_workbook_values(template))==[x[0] for x in FIELDS]
    z=np.load(raw,allow_pickle=False);w=Workbook.create();nt=len(z['time_s'])-1;last=nt+1
    for name,key in FIELDS:
        sh=w.worksheets.add(name)
        sh.get_range('A1:V1').values=[['时间/s；距离/cm']+[round(i/10,1) for i in range(21)]]
        sh.get_range(f'A2:A{last}').values=[[int(t)] for t in z['time_s'][1:]]
        sh.get_range('B1:V1').set_number_format('0.0')
        sh.get_range('B2').set_number_format('0.0000')
        sh.get_range('A1').format.column_width=23
        sh.get_range('B1:V1').format.column_width=11
        sh.freeze_panes.freeze_rows(1)
        if key==field:
            sh.get_range(f'B2:V{last}').values=[[float(format(float(a),'.4f')) for a in row] for row in z[key][1:]]
            sh.get_range(f'B2:V{last}').set_number_format('0.0000')
            print('BUILT',name,nt*21,flush=True)
    SpreadsheetFile.export_xlsx(w).save(str(out))
    print('EXPORTED PART',field,Path(out).stat().st_size,flush=True)

def worksheet_paths(archive):
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    rel={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
    answer={}
    for s in ET.fromstring(archive.read('xl/workbook.xml')).find('s:sheets',ns):
        target=rel[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        answer[s.attrib['name']]=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    return answer

def assemble_parts(temperature_part,moisture_part,out):
    with zipfile.ZipFile(temperature_part) as a,zipfile.ZipFile(moisture_part) as b:
        assert a.testzip() is None and b.testzip() is None
        for shared in ('xl/styles.xml','xl/sharedStrings.xml'):
            av=a.read(shared) if shared in a.namelist() else b''
            bv=b.read(shared) if shared in b.namelist() else b''
            if av!=bv:raise ValueError('Cannot assemble unlike style/string tables: '+shared)
        pa,pb=worksheet_paths(a),worksheet_paths(b)
        if list(pa)!=['温度','水分浓度'] or list(pb)!=list(pa):raise ValueError('Unexpected part sheets')
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dest:
            for info in a.infolist():
                payload=b.read(pb['水分浓度']) if info.filename==pa['水分浓度'] else a.read(info.filename)
                dest.writestr(info.filename,payload)
    return {'method':'artifact_tool worksheet generation + lossless OOXML package assembly',
      'styles_identical':True,'shared_strings_identical':True,'cell_xml_unchanged':True,'output_bytes':Path(out).stat().st_size}

def export_artifact(template,raw,out):
    out=Path(out);parts=out.parent/'.excel_parts';parts.mkdir(exist_ok=True,parents=True)
    env=os.environ.copy();env['CUA_DD_PYTHON_TOOL_WARM_SPREADSHEET_RUNTIME']='0'
    env.pop('ARTIFACT_TOOL_RPC_SOCKET',None);env['BUN_JSC_forceRAMSize']='1879048192'
    paths=[]
    for name,key in FIELDS:
        p=parts/(key+'.xlsx');paths.append(p)
        subprocess.run([sys.executable,str(Path(__file__).resolve()),'--template',str(template),'--raw',str(raw),
          '--out',str(p),'--field',key],env=env,check=True)
    audit=assemble_parts(*paths,out)
    (out.parent/'excel_packaging.json').write_text(json.dumps(audit,indent=2))
    print('EXPORTED',out,audit,flush=True)
    return audit

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--template',required=True);p.add_argument('--raw',required=True);p.add_argument('--out',required=True)
    p.add_argument('--field',choices=[x[1] for x in FIELDS]);a=p.parse_args()
    if a.field:export_part(a.template,a.raw,a.out,a.field)
    else:export_artifact(a.template,a.raw,a.out)
