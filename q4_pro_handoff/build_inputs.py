"""Build a reviewable offline input bundle; never execute model code."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def first_sheet_rows(path: Path) -> list[list[object]]:
    """Read raw cell values from these supplied workbooks without recalculation."""
    with zipfile.ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("s:si", NS):
                strings.append("".join(t.text or "" for t in si.findall(".//s:t", NS)))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        sheet = wb.find("s:sheets/s:sheet", NS)
        rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = next(r.attrib["Target"] for r in rels if r.attrib["Id"] == rid)
        target = target.lstrip("/") if target.startswith("/") else "xl/" + target
        rows = []
        for row in ET.fromstring(z.read(target)).findall("s:sheetData/s:row", NS):
            cells = {}
            for cell in row.findall("s:c", NS):
                letters = re.match(r"[A-Z]+", cell.attrib["r"]).group()
                col = 0
                for char in letters:
                    col = col * 26 + ord(char) - 64
                if cell.find("s:f", NS) is not None:
                    raise ValueError(f"Unexpected formula in raw input: {path.name}, {cell.attrib['r']}")
                kind = cell.attrib.get("t")
                val = cell.find("s:v", NS)
                if kind == "inlineStr":
                    value = "".join(t.text or "" for t in cell.findall(".//s:t", NS))
                elif val is None:
                    value = None
                elif kind == "s":
                    value = strings[int(val.text)]
                elif kind in {"str", "e", "b"}:
                    value = val.text
                else:
                    value = float(val.text)
                if value is not None:
                    cells[col - 1] = value
            if cells:
                rows.append([cells.get(i) for i in range(max(cells) + 1)])
        return rows


def main() -> None:
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    paths: set[Path] = set()

    def add(rel: str) -> None:
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(rel)
        candidates = path.rglob("*") if path.is_dir() else [path]
        for p in candidates:
            if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}:
                paths.add(p)

    for rel in [
        "README.md", "AGENTS.md", "A题", "readable",
        "分析与文献/01_题目分析.md", "分析与文献/02_相关论文.md",
        "分析与文献/references.bib", "分析与文献/evidence/attachment_audit.json",
        "分析与文献/基于动网格的白萝卜热风干燥热质传递研究.pdf",
        "分析与文献/foods-09-01577.pdf",
        "分析与文献/1-s2.0-S0260877414002118-main.pdf",
        "q1_complete_delivery/q1_delivery/README.md",
        "q2_final_delivery/README.md", "q2_final_delivery/analysis_decisions.md",
        "q3_refinement_delivery/README.md", "q3_refinement_delivery/第三问最终复审与答案.md",
        "q3_refinement_delivery/output/table5.csv",
        "q3_refinement_delivery/output/end_event.json",
        "q3_refinement_delivery/output/result3.xlsx",
        "review_q2_final_20260911/第二问最终核查报告.md",
        "review_q2_final_20260911/采纳与勘误.md",
        "review_q123_physics_20260911/README.md",
        "review_q123_physics_20260911/前三问现状与物理闭合审核.md",
        "review_q123_physics_20260911/runtime/runtime_review.md",
        "q123_requirements_review_delivery/README.md",
        "q123_requirements_review_delivery/v1",
        "q4_pro_handoff/README.md", "q4_pro_handoff/发给Pro的提示词.txt",
        "q4_pro_handoff/第四问与前三问收尾_Pro交接提示词.md",
        "q4_pro_handoff/第四问论文阅读清单.md",
    ]:
        add(rel)
    for directory in ["q1_complete_delivery/q1_delivery", "q2_final_delivery", "q3_refinement_delivery"]:
        for suffix in ["source", "run_all.py", "requirements.txt"]:
            add(directory + "/" + suffix)
    for path in (ROOT / "q123_model_selection_delivery/v1").glob("*.md"):
        paths.add(path)
    add("q123_model_selection_delivery/v1/analysis/factorial_contrasts.csv")

    derived = HERE / "inputs"
    derived.mkdir(exist_ok=True)
    facts = {"scope": "Raw workbook read and input packaging only; no PDE or model validation.", "files": []}
    for name, output in [("附件1.xlsx", "environment_from_xlsx.csv"), ("附件2.xlsx", "radius_from_xlsx.csv")]:
        source = ROOT / "A题/附件" / name
        original = source.read_bytes()
        rows = first_sheet_rows(source)
        buf = io.StringIO(newline="")
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerows(rows)
        dest = derived / output
        dest.write_bytes(buf.getvalue().encode("utf-8-sig"))
        paths.add(dest)
        assert sha(source.read_bytes()) == sha(original)
        facts["files"].append({"source": source.relative_to(ROOT).as_posix(), "sha256": sha(original), "header": rows[0], "records": len(rows) - 1, "first": rows[1], "last": rows[-1], "csv": dest.relative_to(ROOT).as_posix()})
    template = ROOT / "A题/附件/附件3/result4.xlsx"
    facts["result4_template"] = {"source": template.relative_to(ROOT).as_posix(), "sha256": sha(template.read_bytes()), "rows": first_sheet_rows(template)}
    write_json(HERE / "input_facts.json", facts)
    paths.add(HERE / "input_facts.json")

    review_root = ROOT / "q123_requirements_review_delivery/v1"
    review_manifest = json.loads((review_root / "MANIFEST.json").read_text(encoding="utf-8"))
    for item in review_manifest["files"]:
        data = (review_root / item["path"]).read_bytes()
        assert len(data) == item["bytes"] and sha(data) == item["sha256"], item["path"]

    records = []
    blobs = {}
    tracked = set(subprocess.check_output(
        ["git", "ls-files", "--cached", "-z"], cwd=ROOT
    ).decode("utf-8").split("\0"))
    included_tracked = [p.relative_to(ROOT).as_posix() for p in sorted(paths)
                        if p.relative_to(ROOT).as_posix() in tracked]
    # Match the bytes that will be published, including Git's text normalization.
    # Refuse stale staged content instead of silently packaging an older revision.
    check = subprocess.run(["git", "diff", "--quiet", "--", *included_tracked], cwd=ROOT)
    if check.returncode:
        raise RuntimeError("Stage the updated input sources before rebuilding the bundle.")
    for p in sorted(paths):
        relative = p.relative_to(ROOT).as_posix()
        data = (subprocess.check_output(["git", "show", ":" + relative], cwd=ROOT)
                if relative in tracked else p.read_bytes())
        blobs[relative] = data
        records.append({"path": relative, "bytes": len(data), "sha256": sha(data)})
    manifest = {
        "purpose": "Inputs and selected references for Q4 completion and Q1-Q3 closeout",
        "repository": "https://github.com/Hel10o/libai.git",
        "base_commit_before_this_handoff": base,
        "version_note": "The base commit precedes this handoff; byte hashes identify exact bundled content. Record the actual GitHub commit when reading online.",
        "byte_policy": "Tracked inputs use Git index bytes after checking for unstaged input changes; untracked inputs use file bytes. Original received evidence is protected by -text attributes. Stage sources before rebuilding and verify the bundle against the final index before committing.",
        "excluded": ["Chupawa 2022 large LFS PDF (all readable text included)", "Historical full raw numerical fields and complete runtime environments", "Cache, bytecode, build products, the bundle itself"],
        "files": records,
    }
    write_json(HERE / "INPUT_MANIFEST.json", manifest)
    start = """# 第四问离线输入入口

先阅读 q4_pro_handoff/第四问与前三问收尾_Pro交接提示词.md 和论文阅读清单。
用户已选择题给物性、无显式潜热有效模型主线，完成第四问并收尾前三问。
INPUT_MANIFEST.json 列出原路径、字节数与SHA256；核对后使用包内原题/附件。
q4_pro_handoff/inputs 的CSV来自本轮直接读取原XLSX，仅为便读副本，原XLSX是输入原件。
附有三篇主要收缩论文PDF与四篇论文完整可读文本；第4篇大PDF从GitHub LFS按需读取。
源码用于参考与复用，不含全部历史场和运行环境，不能声称已完整复现历史套件。
网络失败时可独立完成新求解；记录实际来源，不伪称在线核验。新结果写入 q4_complete_delivery/v1/。
""".encode("utf-8")
    payload = {**blobs, "START_HERE.md": start, "INPUT_MANIFEST.json": (HERE / "INPUT_MANIFEST.json").read_bytes()}
    archive = HERE / "q4_inputs.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, content in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, content)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name, content in payload.items():
            assert z.read(name) == content, name
    # The summary is outside the archive because it contains that archive's hash.
    write_json(HERE / "package_checks.json", {
        "scope": "Source byte identity, raw XLSX input extraction, original review manifest, ZIP CRC and content checks only. No model execution.",
        "base_commit": base, "source_files": len(records), "zip_entries": len(payload),
        "zip_bytes": archive.stat().st_size, "zip_sha256": sha(archive.read_bytes()),
        "source_bytes": sum(r["bytes"] for r in records), "review_manifest_entries_matched": len(review_manifest["files"]),
        "crc_ok": True, "all_zip_payloads_match": True,
    })
    docs = [ROOT / "README.md", ROOT / "q123_requirements_review_delivery/README.md", *HERE.glob("*.md")]
    broken = []
    for p in docs:
        for target in re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            resolved = p.parent / unquote(target.split("#")[0])
            if not resolved.exists():
                broken.append({"file": str(p.relative_to(ROOT)), "target": target})
    assert not broken, broken
    print(json.dumps({"files": len(records), "zip_bytes": archive.stat().st_size, "zip_sha256": sha(archive.read_bytes()), "broken_links": broken, "scope": "No PDE run"}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
