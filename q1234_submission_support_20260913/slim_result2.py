"""Re-serialize a result2 workbook with minimal ECMA-376 markup.

Values are copied verbatim from the source workbook; only the XML
serialization and the style table are rebuilt. The source workbook is
opened read-only and is never written.
"""
from pathlib import Path
import hashlib
import json
import re
import zipfile

NUMFMT_LABEL = 200  # 0.########  distances / times
NUMFMT_DATA = 201   # 0.0000      temperatures, moisture
STYLE_NONE, STYLE_DATA, STYLE_LABEL = 0, 1, 2

SHEETS = ["xl/worksheets/sheet1.xml", "xl/worksheets/sheet2.xml"]
ROW_RE = re.compile(r"<x:row[^>]*>(.*?)</x:row>", re.S)
CELL_RE = re.compile(r'<x:c r="([A-Z]+)(\d+)" s="(\d+)"(?: t="[^"]*")?\s*(?:/>|>(?:<x:v>([^<]*)</x:v>)?</x:c>)')
DIM_RE = re.compile(r'<x:dimension ref="([^"]+)"')


def source_rows(xml):
    """Yield (row_number, [(col, value_or_None), ...]) from a sheet XML string."""
    for match in ROW_RE.finditer(xml):
        body = match.group(1)
        cells = [(m.group(1), m.group(4)) for m in CELL_RE.finditer(body)]
        if cells:
            yield int(CELL_RE.search(body).group(2)), cells


def write_sheet(xml, out, width):
    """Serialise one sheet; column A and the header keep the label format."""
    out.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    out.write('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')
    out.write('<sheetViews><sheetView workbookViewId="0">'
              '<pane xSplit="1" ySplit="1" topLeftCell="B2" activePane="bottomRight" state="frozen"/>'
              '</sheetView></sheetViews>')
    out.write('<sheetFormatPr defaultRowHeight="14.1"/>')
    out.write('<cols><col min="1" max="1" width="19.625" customWidth="1"/>'
              '<col min="2" max="%d" width="9.625" customWidth="1"/></cols>' % width)
    out.write("<sheetData>")
    for number, cells in source_rows(xml):
        header = number == 1
        out.write('<row r="%d">' % number)
        for column, value in cells:
            if header and column == "A":
                out.write('<c r="A1" t="inlineStr"><is><t>%s</t></is></c>' % value)
                continue
            style = STYLE_LABEL if (header or column == "A") else STYLE_DATA
            if value is None:
                out.write('<c r="%s%d" s="%d"/>' % (column, number, style))
            else:
                out.write('<c r="%s%d" s="%d"><v>%s</v></c>' % (column, number, style, value))
        out.write("</row>")
    out.write("</sheetData></worksheet>")


STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<numFmts count="2">'
    '<numFmt numFmtId="200" formatCode="0.########"/>'
    '<numFmt numFmtId="201" formatCode="0.0000"/>'
    '</numFmts>'
    '<fonts count="1"><font><sz val="11"/><name val="宋体"/></font></fonts>'
    '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
    '<borders count="1"><border/></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="3">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="201" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="200" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '</cellXfs>'
    '<cellStyles count="1"><cellStyle name="常规" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>'
)


def workbook_xml(names):
    sheets = "".join(
        '<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (name, i + 1, i + 1)
        for i, name in enumerate(names)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>%s</sheets></workbook>" % sheets
    )


WORKBOOK_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
    '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    "</Relationships>"
)

ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
    "</Relationships>"
)

CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
    '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
    '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    "</Types>"
)


def value_digest(path):
    """Ordered digest over every cell value, used to prove numeric identity."""
    digest = hashlib.sha256()
    with zipfile.ZipFile(path) as archive:
        for sheet in SHEETS:
            xml = archive.read(sheet).decode("utf-8")
            for number, cells in source_rows(xml):
                for column, value in cells:
                    digest.update(("%d|%s|%s\n" % (number, column, value)).encode("utf-8"))
    return digest.hexdigest()


def build(source, target, names):
    source = Path(source)
    target = Path(target)
    with zipfile.ZipFile(source) as archive:
        sheets = [archive.read(sheet).decode("utf-8") for sheet in SHEETS]

    scratch = target.with_suffix(".work")
    scratch.mkdir(parents=True, exist_ok=True)
    written = []
    for index, xml in enumerate(sheets, start=1):
        path = scratch / ("sheet%d.xml" % index)
        with path.open("w", encoding="utf-8", newline="") as handle:
            write_sheet(xml, handle, len(CELL_RE.findall(ROW_RE.search(xml).group(1))))
        written.append((path, "xl/worksheets/sheet%d.xml" % index))

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        out.writestr("[Content_Types].xml", CONTENT_TYPES)
        out.writestr("_rels/.rels", ROOT_RELS)
        out.writestr("xl/workbook.xml", workbook_xml(names))
        out.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS)
        out.writestr("xl/styles.xml", STYLES)
        for path, name in written:
            out.write(path, name)

    for path, _ in written:
        path.unlink()
    scratch.rmdir()

    with zipfile.ZipFile(target) as check:
        assert check.testzip() is None
    return source.stat().st_size, target.stat().st_size


def main():
    base = Path(__file__).resolve().parent
    source = Path(r"D:\Desktop\CUMCM26\q4_complete_delivery\v1\q123_closeout\result2.xlsx")
    target = base / "out" / "result2_slim.xlsx"
    names = ["温度", "水分浓度"]
    before, after = build(source, target, names)
    src_digest = value_digest(source)
    new_digest = value_digest(target)
    report = {
        "source": str(source),
        "source_bytes": before,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "target": str(target),
        "target_bytes": after,
        "target_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "value_digest_source": src_digest,
        "value_digest_target": new_digest,
        "values_identical": src_digest == new_digest,
    }
    (base / "evidence" / "result2_slim.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    assert src_digest == new_digest, "value mismatch"


if __name__ == "__main__":
    main()
