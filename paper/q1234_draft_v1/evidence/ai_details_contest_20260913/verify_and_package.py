"""Copy deliverables, validate paper/AI PDFs, and refresh the support ZIP."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import fitz

ROOT = Path(r"D:\Desktop\CUMCM26")
PAPER = ROOT / "paper" / "q1234_draft_v1"
EVIDENCE = PAPER / "evidence" / "ai_details_contest_20260913"
SRC_AI = PAPER / "build" / "ai_details_contest_20260913" / "ai_details.pdf"
SRC_PAPER = PAPER / "build" / "main.pdf"
DELIV_AI = PAPER / "AI工具使用详情.pdf"
DELIV_PAPER = PAPER / "四问论文初稿_v1.pdf"
BUILD_AI = PAPER / "build" / "ai_details.pdf"
SUPPORT = ROOT / "q1234_submission_support_20260913"
ZIP_PATH = SUPPORT / "out" / "A题_支撑材料.zip"
STAGE_AI = SUPPORT / "stage" / "支撑材料" / "AI工具使用详情.pdf"
MARGIN_PT = 25 / 25.4 * 72
GLYPH_TOL = 2.0
IDENTITY = [
    "libai", "Hel10o", "github.com", r"D:\Desktop", r"C:\Users",
    "Desktop\\CUMCM26", "zcode",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_replace(src: Path, dst: Path) -> Path:
    data = src.read_bytes()
    try:
        dst.write_bytes(data)
        return dst
    except PermissionError:
        alt = dst.with_name(dst.stem + "_updated" + dst.suffix)
        alt.write_bytes(data)
        return alt


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_ai_pdf(path: Path) -> dict:
    report = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
    with fitz.open(path) as doc:
        report["pages"] = doc.page_count
        report["page_size"] = [round(doc[0].rect.width, 2), round(doc[0].rect.height, 2)]
        report["author"] = (doc.metadata or {}).get("author") or ""
        report["title"] = (doc.metadata or {}).get("title") or ""
        text = "\n".join(page.get_text() for page in doc)
        compact = "".join(text.split())
        required = {
            "title": "AI工具使用详情" in text,
            "tool_and_version": "工具" in text and ("版本" in text or "模型" in text),
            "purpose_or_stage": any(term in text for term in ("目的", "环节", "分工")),
            "input_and_interaction": "输入" in text and "交互" in text,
            "adoption_and_review": "采纳" in text and any(term in text for term in ("核验", "验证", "审核")),
            "chatgpt": "ChatGPT" in text,
            "model": "GPT-6 Astra" in text or "GPT6-Astra" in text,
            "code": "求解代码" in compact,
            "literature": "文献检索" in compact,
            "polish": "语言润色" in compact,
            "filename": "AI工具使用详情.pdf" in compact,
        }
        report["required"] = required
        identity = []
        for page in doc:
            page_text = page.get_text()
            for needle in IDENTITY:
                if needle.lower() in page_text.lower():
                    identity.append({"page": page.number + 1, "needle": needle})
        if report["author"].strip():
            identity.append({"page": "metadata", "needle": "author", "value": report["author"]})
        report["identity"] = identity
        bounds_bad = []
        footers_bad = []
        for pno, page in enumerate(doc, 1):
            page_w, page_h = page.rect.width, page.rect.height
            a4 = abs(page_w - 595.28) < 2 and abs(page_h - 841.89) < 2
            if not a4:
                bounds_bad.append({"page": pno, "reason": "not A4", "size": [page_w, page_h]})
            words = page.get_text("words")
            footers = [w for w in words if w[4].isdigit() and w[1] >= page_h - 100
                       and abs((w[0] + w[2]) / 2 - page_w / 2) < 45]
            if len(footers) != 1 or footers[0][4] != str(pno):
                footers_bad.append({"page": pno, "footers": [w[4] for w in footers]})
            for w in words:
                if w in footers:
                    continue
                bbox = w[:4]
                excess = max(MARGIN_PT - bbox[0], MARGIN_PT - bbox[1],
                             bbox[2] - (page_w - MARGIN_PT),
                             bbox[3] - (page_h - MARGIN_PT), 0)
                if excess > GLYPH_TOL:
                    bounds_bad.append({"page": pno, "text": w[4][:80], "excess_pt": round(excess, 3)})
        report["footers_bad"] = footers_bad
        report["bounds_bad"] = bounds_bad
        report["fonts_embedded"] = all(
            not font[1] for page in doc for font in page.get_fonts()
        )
        report["ok"] = (
            report["pages"] == 3
            and all(required.values())
            and not identity
            and not footers_bad
            and not bounds_bad
            and report["fonts_embedded"]
            and not report["author"].strip()
        )
    return report


def refresh_support_zip(ai_bytes: bytes) -> dict:
    old_bytes = ZIP_PATH.read_bytes()
    prior_sha = digest(old_bytes)
    member = "支撑材料/AI工具使用详情.pdf"
    with zipfile.ZipFile(BytesIO(old_bytes)) as archive:
        assert archive.testzip() is None
        old = {info.filename: archive.read(info.filename) for info in archive.infolist()}
        infos = {info.filename: info for info in archive.infolist()}
    assert member in old, sorted(old)
    unchanged = {name: data for name, data in old.items() if name != member}
    assert all(unchanged[name] == old[name] for name in unchanged)
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    STAGE_AI.parent.mkdir(parents=True, exist_ok=True)
    STAGE_AI.write_bytes(ai_bytes)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as out:
        for name, data in old.items():
            info = zipfile.ZipInfo(filename=name, date_time=infos[name].date_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = infos[name].external_attr
            payload = ai_bytes if name == member else data
            out.writestr(info, payload)
    new_bytes = buf.getvalue()
    ZIP_PATH.write_bytes(new_bytes)
    with zipfile.ZipFile(ZIP_PATH) as check:
        assert check.testzip() is None
        new = {info.filename: check.read(info.filename) for info in check.infolist()}
    assert set(new) == set(old)
    assert new[member] == ai_bytes
    for name in unchanged:
        assert new[name] == old[name], name
    identity = []
    for name, data in new.items():
        if name.lower().endswith((".pdf", ".npz", ".xlsx", ".png", ".jpg", ".zip")):
            continue
        try:
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            continue
        for needle in IDENTITY:
            if needle.lower() in text.lower():
                identity.append({"file": name, "needle": needle})
    report = {
        "operation": "Replace only 支撑材料/AI工具使用详情.pdf; keep all other members byte-identical",
        "prior_zip_sha256": prior_sha,
        "zip": str(ZIP_PATH),
        "zip_bytes": len(new_bytes),
        "zip_mb": round(len(new_bytes) / 1e6, 2),
        "zip_within_20mb": len(new_bytes) < 20 * 1024 * 1024,
        "zip_sha256": digest(new_bytes),
        "member_count": len(new),
        "changed_members": [member],
        "ai_pdf_sha256": digest(ai_bytes),
        "ai_pdf_bytes": len(ai_bytes),
        "other_members_byte_identical": True,
        "zip_crc_check": "passed",
        "identity_raw_binary_findings": identity,
        "pde_or_parameter_scenarios_run": False,
        "workbooks_or_arrays_reexported": False,
    }
    (SUPPORT / "evidence" / "package_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (EVIDENCE / "support_refresh.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    assert SRC_AI.is_file() and SRC_PAPER.is_file()
    copied = {
        "AI工具使用详情.pdf": copy_replace(SRC_AI, DELIV_AI),
        "build/ai_details.pdf": copy_replace(SRC_AI, BUILD_AI),
        "四问论文初稿_v1.pdf": copy_replace(SRC_PAPER, DELIV_PAPER),
    }
    expected_src = {
        "AI工具使用详情.pdf": SRC_AI,
        "build/ai_details.pdf": SRC_AI,
        "四问论文初稿_v1.pdf": SRC_PAPER,
    }
    for label, path in copied.items():
        assert path.read_bytes() == expected_src[label].read_bytes(), path

    sys.path.insert(0, str(PAPER))
    from validate_paper import Audit

    class Args:
        pdf = SRC_PAPER
        aux = PAPER / "build" / "main.aux"
        ai_pdf = SRC_AI
        expected = PAPER / "evidence" / "table_expected.json"
        output = EVIDENCE / "pdf_validation.json"
        body_only = False

    audit = Audit(Args())
    audit.run()
    validate_rc = audit.save()

    ai_report = check_ai_pdf(SRC_AI)
    (EVIDENCE / "ai_pdf_check.json").write_text(
        json.dumps(ai_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    support_report = refresh_support_zip(SRC_AI.read_bytes())

    summary = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "ai_pages": ai_report["pages"],
        "ai_ok": ai_report["ok"],
        "ai_sha256": ai_report["sha256"],
        "paper_sha256": sha256(SRC_PAPER),
        "paper_bytes": SRC_PAPER.stat().st_size,
        "validate_paper_rc": validate_rc,
        "support_zip_sha256": support_report["zip_sha256"],
        "support_zip_bytes": support_report["zip_bytes"],
        "copied": {label: {"path": str(path), "sha256": sha256(path)} for label, path in copied.items()},
    }
    (EVIDENCE / "validation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not ai_report["ok"]:
        print("AI PDF checks failed", json.dumps(ai_report, ensure_ascii=False)[:4000])
        return 1
    return 0 if validate_rc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
