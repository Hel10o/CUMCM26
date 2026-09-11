"""Actual artifact_tool export plus a standard-library portable serialization option.
The official workbook is created with export_artifact; no spreadsheet formulas
are used to approximate the PDE. Numeric doubles are stored with 0.0000 display.
"""
from __future__ import annotations
import argparse,io,json,os,zipfile
from pathlib import Path
import numpy as np

def payload(root):
 a=np.load(root/'output/main.npz');t=a['time_s'][1:];c=a['sample_TC'][1:,:,1]
 if c.shape!=(len(t),21) or not np.all(np.diff(t)>0) or not np.isfinite(c).all():raise ValueError('Invalid final data')
 if t[0]!=60 or not np.array_equal(t[:-1],np.arange(1,len(t))*60.):raise ValueError('Missing 60s rows')
 if c[-1].max()>=.15:raise ValueError('Final row is not strictly qualified')
 return t,c

def export_artifact(root,out=None,workbook=None,previews=False):
 os.environ.setdefault('ARTIFACT_TOOL_RPC_DAEMON_STARTUP_TIMEOUT_S','35')
 from artifact_tool import Blob,SpreadsheetFile
 root=Path(root);out=Path(out) if out else root/'result3.xlsx'
 if out.exists():raise FileExistsError(out)
 t,c=payload(root);n=len(t)+1
 wb=workbook if workbook is not None else SpreadsheetFile.import_xlsx(Blob.load(str(root/'inputs/result3_blank.xlsx')))
 sh=wb.worksheets.get_item('Sheet1')
 sh.get_range(f'A1:V{n}').values=[['时间/s\\到药材中心的距离/cm']+np.linspace(0,2,21).tolist()]+np.column_stack([t,c]).tolist()
 sh.get_range(f'A1:V{n}').format.font={'name':'Arial','size':10}
 sh.get_range(f'A1:V{n}').format.row_height=18
 sh.get_range(f'A1:V{n}').format.horizontal_alignment='center'
 sh.get_range(f'A1:A{n}').format.column_width=32
 sh.get_range(f'B1:V{n}').format.column_width=11
 sh.get_range('A1:V1').format.font={'bold':True,'size':10}
 sh.get_range('A1:V1').format.row_height=34
 sh.get_range('A1').format.wrap_text=True
 sh.get_range('B1:V1').set_number_format('0.0')
 sh.get_range(f'A2:A{n}').set_number_format('0.########')
 sh.get_range(f'B2:V{n}').set_number_format('0.0000')
 sh.get_range(f'A{n}:V{n}').format.font={'bold':True,'size':10}
 sh.freeze_panes.freeze_rows(1);sh.freeze_panes.freeze_columns(1)
 SpreadsheetFile.export_xlsx(wb).save(str(out))
 if previews:
  wb.render({'sheet_name':'Sheet1','range':'A1:H7','scale':1.5}).save(str(root/'output/result3_preview_head.png'))
  wb.render({'sheet_name':'Sheet1','range':f'A{n-4}:H{n}','scale':1.5}).save(str(root/'output/result3_preview_tail.png'))
 return {'engine':'artifact_tool','bytes':out.stat().st_size,'data_rows':len(t),'columns':22}

def portable_bytes(root):
 # Explicit OOXML with only standard-library zipfile. No Office, proprietary
 # service or additional spreadsheet package is required for local reproduction.
 t,c=payload(Path(root));n=len(t)+1;ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
 parts={
 '[Content_Types].xml':'''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>''',
 '_rels/.rels':'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''',
 'xl/workbook.xml':f'''<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>''',
 'xl/_rels/workbook.xml.rels':'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''',
 'xl/styles.xml':f'''<styleSheet xmlns="{ns}"><numFmts count="2"><numFmt numFmtId="164" formatCode="0.0000"/><numFmt numFmtId="165" formatCode="0.########"/></numFmts><fonts count="2"><font><sz val="10"/><name val="Arial"/></font><font><b/><sz val="10"/><name val="Arial"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="5"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/><xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center" wrapText="1"/></xf><xf numFmtId="164" fontId="1" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''}
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,text in parts.items():z.writestr(name,('<?xml version="1.0" encoding="UTF-8"?>'+text).encode())
  with z.open('xl/worksheets/sheet1.xml','w') as f:
   f.write((f'<worksheet xmlns="{ns}"><dimension ref="A1:V{n}"/><sheetViews><sheetView workbookViewId="0"><pane xSplit="1" ySplit="1" topLeftCell="B2" activePane="bottomRight" state="frozen"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="18"/><cols><col min="1" max="1" width="32" customWidth="1"/><col min="2" max="22" width="11" customWidth="1"/></cols><sheetData><row r="1" ht="34" customHeight="1"><c r="A1" t="inlineStr" s="3"><is><t>时间/s；到药材中心的距离/cm</t></is></c>'+''.join(f'<c r="{chr(66+j)}1" t="n" s="3"><v>{j/10:.1f}</v></c>' for j in range(21))+'</row>').encode())
   for i,(tt,cc) in enumerate(zip(t,c),2):
    st=4 if i==n else 1
    text=f'<row r="{i}"><c r="A{i}" t="n" s="2"><v>{float(tt):.17g}</v></c>'+''.join(f'<c r="{chr(66+j)}{i}" t="n" s="{st}"><v>{float(v):.17g}</v></c>' for j,v in enumerate(cc))+'</row>'
    f.write(text.encode())
   f.write(b'</sheetData></worksheet>')
 return b.getvalue()

def export_portable(root,out=None):
 root=Path(root);out=Path(out) if out else root/'result3.xlsx'
 if out.exists():raise FileExistsError(out)
 out.write_bytes(portable_bytes(root));return {'engine':'standard-library OOXML','bytes':out.stat().st_size}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--engine',choices=['artifact','portable'],default='portable');a=p.parse_args()
 print(json.dumps(export_artifact(a.root) if a.engine=='artifact' else export_portable(a.root)))
