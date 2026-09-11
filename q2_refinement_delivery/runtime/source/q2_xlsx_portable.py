"""Optional standard-library OOXML serialization for machines without artifact_tool.
The delivered workbook was generated with the artifact_tool path. This separate
portable exporter is provided for local use; see execution scope in README.
It needs only NumPy and the already computed q2_unrounded.npz.
"""
from pathlib import Path
import zipfile
import numpy as np

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'

def export_portable(raw,out):
    z=np.load(raw,allow_pickle=False);out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    nt=len(z['time_s'])-1
    if nt!=10800 or not np.array_equal(z['time_s'],np.arange(10801)):
        raise ValueError('This formal workbook exporter is restricted to the declared Q2 3-hour contract')
    content='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'''
    rootrels='''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'''
    wb=f'''<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="{NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="温度" sheetId="1" r:id="rId1"/><sheet name="水分浓度" sheetId="2" r:id="rId2"/></sheets></workbook>'''
    rels='''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    styles=f'''<?xml version="1.0" encoding="UTF-8"?><styleSheet xmlns="{NS}"><numFmts count="1"><numFmt numFmtId="164" formatCode="0.0000"/></numFmts><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as arc:
        for path,text in [('[Content_Types].xml',content),('_rels/.rels',rootrels),('xl/workbook.xml',wb),('xl/_rels/workbook.xml.rels',rels),('xl/styles.xml',styles)]:arc.writestr(path,text.encode('utf-8'))
        for index,key in enumerate(['temperature_degC','moisture_dry_basis'],1):
            if z[key].shape!=(10801,21) or not np.isfinite(z[key]).all():raise ValueError('Invalid numeric field')
            with arc.open(f'xl/worksheets/sheet{index}.xml','w') as f:
                prefix=f'''<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="{NS}"><dimension ref="A1:V10801"/><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols><col min="1" max="1" width="23" customWidth="1"/><col min="2" max="22" width="11" customWidth="1"/></cols><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>时间/s；距离/cm</t></is></c>'''
                f.write(prefix.encode('utf-8'))
                f.write((''.join(f'<c r="{chr(66+j)}1" t="n"><v>{j/10:.1f}</v></c>' for j in range(21))+'</row>').encode())
                for t,row in enumerate(z[key][1:],1):
                    line=f'<row r="{t+1}"><c r="A{t+1}" t="n"><v>{t}</v></c>'
                    line+=''.join(f'<c r="{chr(66+j)}{t+1}" s="1" t="n"><v>{float(value):.4f}</v></c>' for j,value in enumerate(row))+'</row>'
                    f.write(line.encode())
                f.write(b'</sheetData></worksheet>')
    return {'engine':'portable stdlib OOXML','bytes':out.stat().st_size}
