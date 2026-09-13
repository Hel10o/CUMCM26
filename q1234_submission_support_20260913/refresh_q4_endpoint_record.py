"""Include existing Q4 endpoint evidence without solving or exporting any model."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "q1234_submission_support_20260913"
PAPER = ROOT / "paper/q1234_draft_v1"
OUT = BASE / "out/A题_支撑材料.zip"
BASELINE_SHA256 = "34e9aab18b5f97661c1079feccf5aaa5ebf990d7277688cced322731d6818c71"
BASELINE_COMMIT = "fea3607783fee0ad946c45facd9e1a9926ebf5c8"
EVIDENCE = BASE / "evidence/q4_endpoint_record_20260913"
PREFIX = "支撑材料/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    original_bytes = OUT.read_bytes()
    assert sha(original_bytes) == BASELINE_SHA256, "Support ZIP changed; inspect the new baseline before refreshing."
    with zipfile.ZipFile(BytesIO(original_bytes)) as z:
        assert z.testzip() is None
        old = {n: z.read(n) for n in z.namelist()}
        infos = {i.filename: i for i in z.infolist()}
    assert len(old) == 94
    current_support = {
        PREFIX + f.relative_to(PAPER).as_posix(): f.read_bytes()
        for f in (PAPER / "support").rglob("*")
        if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc"
    }
    additions = sorted(set(current_support) - set(old))
    evidence_prefix = PREFIX + "support/evidence/q4_endpoint_20260912/"
    assert additions == sorted(evidence_prefix + n for n in
                               ("README.md", "MANIFEST.json", "endpoint_audit.json", "q4_direct_execution_field.npz"))
    support_changes = [n for n, data in current_support.items() if n in old and data != old[n]]
    assert support_changes == [PREFIX + "support/README.md"], support_changes
    mapping = json.loads(current_support[evidence_prefix + "MANIFEST.json"])
    for row in mapping["files"]:
        data = current_support[evidence_prefix + row["file"]]
        assert sha(data) == row["sha256"]
        assert data == (ROOT / row["source"]).read_bytes()
    for name in additions:
        if name.endswith((".md", ".json")):
            assert not re.search(r"(?i)\b(?:Hel10o|libai)\b|[A-Z]:[\\/]", current_support[name].decode("utf-8"))

    updated = old | current_support
    listing_name = PREFIX + "支撑材料文件列表.md"
    listing = old[listing_name].decode("utf-8")
    listing += "\n## 第四问二维终点既有核查记录\n\n正文第11.3节引用的记录见以下文件，均未重新计算：\n\n"
    listing += "\n".join("- `" + n.removeprefix(PREFIX) + "`" for n in additions) + "\n"
    updated[listing_name] = listing.encode("utf-8")
    changed = sorted(n for n in old if old[n] != updated[n])
    assert changed == sorted([PREFIX + "support/README.md", listing_name])
    for n in old:
        if n.startswith(PREFIX + "results/") or n.startswith(PREFIX + "figures/") or n.endswith("AI工具使用详情.pdf"):
            assert updated[n] == old[n]
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n, data in sorted(updated.items()):
            z.writestr(infos.get(n, n), data)
    final_bytes = buffer.getvalue()
    assert len(final_bytes) < 20_000_000
    with zipfile.ZipFile(BytesIO(final_bytes)) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(updated)
        assert all(z.read(n) == data for n, data in updated.items())
        members = [{"name": i.filename, "bytes": i.file_size, "zip_bytes": i.compress_size,
                    "sha256": sha(updated[i.filename])} for i in z.infolist()]
    report = {
        "operation": "Add unchanged saved Q4 endpoint evidence after removing detailed discussion from the main text",
        "baseline_commit": BASELINE_COMMIT, "baseline_zip_sha256": BASELINE_SHA256,
        "changed_members": changed, "added_members": additions,
        "preserved_original_members": len(old) - len(changed),
        "all_numerical_and_figure_members_byte_identical": True,
        "all_evidence_copies_byte_identical_to_sources": True,
        "all_current_support_members_match_directory": True,
        "zip_crc_check": "passed", "all_members_read_back": True,
        "pde_or_parameter_scenarios_run": False, "workbooks_or_arrays_reexported": False,
        "member_count": len(updated), "members": members,
        "zip_bytes": len(final_bytes), "zip_sha256": sha(final_bytes),
        "zip_decimal_mb": round(len(final_bytes) / 1e6, 2),
        "zip_mib": round(len(final_bytes) / 2**20, 2),
    }
    assert OUT.read_bytes() == original_bytes
    assert all((PAPER / n.removeprefix(PREFIX)).read_bytes() == data for n, data in current_support.items())
    EVIDENCE.mkdir(exist_ok=False)
    (EVIDENCE / "prior_package_report.json").write_bytes((BASE / "evidence/package_report.json").read_bytes())
    OUT.write_bytes(final_bytes)
    OUT.with_suffix(".zip.sha256").write_text(sha(final_bytes) + "  " + OUT.name + "\n", encoding="utf-8")
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    (EVIDENCE / "verification.json").write_text(payload, encoding="utf-8")
    (BASE / "evidence/package_report.json").write_text(payload, encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "members"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
