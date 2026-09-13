"""Prototype: re-serialize result2 with a shared-string table.

Measures whether the full-time workbook can be pushed under the 20 MB
submission cap. Writes only to the scratch output directory.
"""
from pathlib import Path
import re
import zipfile

import slim_result2 as S

SS_RE = re.compile(r"<x:v>([^<]*)</x:v>")


def build(source, target, names):
    source, target = Path(source), Path(target)
    with zipfile.ZipFile(source) as archive:
        sheets = [archive.read(sheet).decode("utf-8") for sheet in S.SHEETS]

    scratch = target.parent / "sst_parts"
    scratch.mkdir(parents=True, exist_ok=True)
    parts = []
    for index, xml in enumerate(sheets, start=1):
        table, lookup = [], {}
        rows_out = scratch / ("sheet%d.xml" % index)
        with rows_out.open("w", encoding="utf-8", newline="") as out:
            out.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            out.write('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')
            out.write('<sheetData>')
            for number, cells in S.source_rows(xml):
                out.write('<row r="%d">' % number)
                for column, value in cells:
                    if value is None:
                        out.write('<c r="%s%d"/>' % (column, number))
                        continue
                    slot = lookup.get(value)
                    if slot is None:
                        slot = lookup[value] = len(table)
                        table.append(value)
                    out.write('<c r="%s%d" t="s"><v>%d</v></c>' % (column, number, slot))
                out.write("</row>")
            out.write("</sheetData></worksheet>")
        sst_out = scratch / ("sst%d.xml" % index)
        sst_out.write_text(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="%d" uniqueCount="%d">'
            % (sum(1 for _ in table), len(table))
            + "".join("<si><t>%s</t></si>" % v for v in table)
            + "</sst>",
            encoding="utf-8",
        )
        parts.append((rows_out, "xl/worksheets/sheet%d.xml" % index))
        parts.append((sst_out, "xl/sharedStrings%d.xml" % index))

    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
        + "".join(
            '<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (n, i + 1, i + 1)
            for i, n in enumerate(names)
        )
        + "</sheets></workbook>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
        "</Relationships>"
    )
    types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        out.writestr("[Content_Types].xml", types)
        out.writestr("_rels/.rels", S.ROOT_RELS)
        out.writestr("xl/workbook.xml", workbook)
        out.writestr("xl/_rels/workbook.xml.rels", rels)
        for path, name in parts:
            out.write(path, name)
    for path, _ in parts:
        path.unlink()
    scratch.rmdir()
    with zipfile.ZipFile(target) as check:
        for info in check.infolist():
            print("   %-30s raw=%8.2fMB zip=%7.2fMB" % (info.filename, info.file_size / 1048576, info.compress_size / 1048576))
    return target.stat().st_size


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    src = Path(r"D:\Desktop\CUMCM26\q4_complete_delivery\v1\q123_closeout\result2.xlsx")
    size = build(src, base / "out" / "result2_sst.xlsx", ["温度", "水分浓度"])
    print("sst 变体总大小 %.2f MB" % (size / 1048576))
