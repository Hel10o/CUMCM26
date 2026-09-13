"""Refresh ten enlarged-text figures and two lists, retaining baseline data bytes.

Run --freeze only after the paper figures and source list are finalized, then run
without arguments. Neither step calls a solver, workbook exporter, or AI builder.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import re
import shutil
import zipfile

import fitz

import build_package as package


BASELINE_COMMIT = "4f09fdad4182b6f220e801af54dffd0be37ad04c"
INTEGRATED_AI_COMMIT = "285f3d984190b0655e1a46b8cfffe91b656cc7ea"
BASELINE_ZIP_SHA256 = "8409a3c6358c994d5897cc023de809050e1dc37270d77f2384cde219e78662d8"
EVIDENCE = package.BASE / "evidence" / "figure_legibility_refresh_20260913"
SOURCE_LIST = "support/图表来源清单.md"
REPLACEMENTS = {
    "figures/q1_legibility/q1_workflow.pdf": "figures/legibility_schematics/q1_workflow.pdf",
    "figures/ch6_revision/q1_boundary.pdf": "figures/legibility_schematics/q1_boundary.pdf",
    "figures/q2_revision/q2_workflow.pdf": "figures/legibility_schematics/q2_workflow.pdf",
    "figures/q2_heatmap/q2_fields.pdf": "figures/legibility_q2/q2_fields.pdf",
    "figures/q2_revision/q2_mechanism.pdf": "figures/legibility_q2/q2_mechanism.pdf",
    "figures/font_revision/q3_q4_drying.pdf": "figures/legibility_process/q3_q4_drying.pdf",
    "figures/question_workflows/q4_workflow.pdf": "figures/legibility_schematics/q4_workflow.pdf",
    "figures/font_revision/q4_shrinkage.pdf": "figures/legibility_process/q4_shrinkage.pdf",
    "figures/font_revision/dimension_reduction.pdf": "figures/legibility_validation/dimension_reduction.pdf",
    "figures/font_revision/environment_sensitivity.pdf": "figures/legibility_validation/environment_sensitivity.pdf",
}
RETAINED = {"figures/q1_legibility/q1_profiles.pdf", "figures/q3_white/q3_workflow.pdf"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def member(path):
    return package.TOP + "/" + path


def current_body_figures():
    """Limit reference scanning to body files; never read ai_details.tex."""
    sources = [package.PAPER / "main.tex"] + sorted((package.PAPER / "sections").glob("*.tex"))
    names = []
    for source in sources:
        for name in re.findall(r"includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", source.read_text(encoding="utf-8")):
            if name not in names:
                names.append(name)
    figures = {}
    for name in names:
        for suffix in ("", ".pdf", ".png"):
            path = package.PAPER / (name + suffix)
            if path.is_file():
                figures[path.relative_to(package.PAPER).as_posix()] = path
                break
        else:
            raise FileNotFoundError(name)
    assert set(figures) == set(REPLACEMENTS.values()) | RETAINED
    assert len(figures) == 12 and all(path.suffix == ".pdf" for path in figures.values())
    return figures


def frozen_inputs():
    figures = current_body_figures()
    return {
        "baseline_commit": BASELINE_COMMIT,
        "integrated_ai_commit": INTEGRATED_AI_COMMIT,
        "baseline_zip_sha256": BASELINE_ZIP_SHA256,
        "concurrent_ai_isolation": "figure_legibility_refresh_20260913/concurrent_ai_isolation.json",
        "source_list_sha256": package.sha256(package.PAPER / SOURCE_LIST),
        "figure_sha256": {name: package.sha256(path) for name, path in sorted(figures.items())},
    }


def main(freeze=False):
    assert package.sha256(package.ZIP_PATH) == BASELINE_ZIP_SHA256, "support ZIP baseline changed; inspect before refreshing"
    freeze_path = EVIDENCE / "frozen_inputs.json"
    if freeze:
        assert not freeze_path.exists(), "inputs were already frozen; review any requested change explicitly"
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        freeze_path.write_text(json.dumps(frozen_inputs(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Frozen twelve paper figures and the source list; support ZIP unchanged.")
        return
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    assert frozen == frozen_inputs(), "paper inputs differ from the approved freeze"
    old_zip_bytes = package.ZIP_PATH.read_bytes()
    assert digest(old_zip_bytes) == BASELINE_ZIP_SHA256
    original_report = package.BASE / "evidence" / "package_report.json"
    baseline_report = EVIDENCE / "prior_report.json"
    assert json.loads(original_report.read_text(encoding="utf-8"))["zip_sha256"] == BASELINE_ZIP_SHA256
    assert not baseline_report.exists(), "refresh evidence already exists; inspect instead of overwriting"
    shutil.copy2(original_report, baseline_report)

    with zipfile.ZipFile(BytesIO(old_zip_bytes)) as archive:
        assert archive.testzip() is None
        old = {info.filename: archive.read(info.filename) for info in archive.infolist()}
        infos = {info.filename: info for info in archive.infolist()}
    figure_prefix = member("figures/")
    old_figures = {name for name in old if name.startswith(figure_prefix)}
    assert old_figures == {member(path) for path in set(REPLACEMENTS) | RETAINED}
    figures = current_body_figures()
    assert all(old[member(name)] == figures[name].read_bytes() for name in RETAINED)
    assert all(old[member(before)] != figures[after].read_bytes() for before, after in REPLACEMENTS.items())

    current_support = {
        member(path.relative_to(package.PAPER).as_posix()): path
        for path in (package.PAPER / "support").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    assert set(current_support) == {name for name in old if name.startswith(member("support/"))}
    support_changes = sorted(name for name, path in current_support.items() if old[name] != path.read_bytes())
    assert support_changes == [member(SOURCE_LIST)], support_changes
    updated = {name: data for name, data in old.items() if name not in old_figures}
    updated.update({member(name): path.read_bytes() for name, path in figures.items()})
    updated[member(SOURCE_LIST)] = (package.PAPER / SOURCE_LIST).read_bytes()
    listing_name = member("支撑材料文件列表.md")
    listing = old[listing_name].decode("utf-8")
    listing = re.sub(r"(?m)^- `figures/[^\r\n]+[\r\n]+", "", listing)
    new_lines = "\n".join("- `" + name + "`" for name in sorted(figures))
    marker = "- `literature/"
    assert marker in listing
    updated[listing_name] = listing.replace(marker, new_lines + "\n" + marker, 1).encode("utf-8")
    result_names = sorted(name for name in old if name.startswith(member("results/")))
    assert len(result_names) == 5
    retained_names = sorted(set(old) - old_figures - {member(SOURCE_LIST), listing_name})
    assert all(updated[name] == old[name] for name in retained_names)
    ai_name = member("AI工具使用详情.pdf")
    with fitz.open(stream=updated[ai_name], filetype="pdf") as ai_pdf:
        ai_pages = len(ai_pdf)
    assert ai_pages == 3

    raw_findings, metadata_findings, workbook_metadata = [], [], {}
    for name, data in updated.items():
        lower = data.lower()
        for token in package.IDENTITY:
            if token.lower().encode("utf-8") in lower:
                raw_findings.append({"file": name, "needle": token})
        if name.endswith(".pdf"):
            with fitz.open(stream=data, filetype="pdf") as document:
                metadata = json.dumps(document.metadata, ensure_ascii=False).lower()
                for token in package.IDENTITY:
                    if token.lower() in metadata:
                        metadata_findings.append({"file": name, "needle": token})
    assert not raw_findings and not metadata_findings
    for name in result_names:
        if name.endswith(".xlsx"):
            with zipfile.ZipFile(BytesIO(updated[name])) as workbook:
                workbook_metadata[name] = [part for part in workbook.namelist() if part.startswith("docProps/")]
                assert not workbook_metadata[name]
    assert len(updated) == 94
    output_dir = package.ZIP_PATH.parent.resolve()
    assert output_dir.is_relative_to(package.BASE.resolve())
    temporary = output_dir / "A题_支撑材料.figure-legibility-refresh.tmp"
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(updated.items()):
            info = zipfile.ZipInfo(name, (2026, 9, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = infos[name].external_attr if name in infos else 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(temporary) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(updated)
        assert all(archive.read(name) == data for name, data in updated.items())
        members = [{"name": info.filename, "bytes": info.file_size, "zip_bytes": info.compress_size} for info in archive.infolist()]
    assert temporary.stat().st_size <= 20 * 1024 * 1024
    assert frozen == frozen_inputs(), "paper inputs changed while packaging"
    assert package.sha256(package.ZIP_PATH) == BASELINE_ZIP_SHA256, "another task changed the support ZIP; do not replace it"
    temporary.replace(package.ZIP_PATH)
    report = {
        "operation": "Enlarge ten body figures; refresh only figure sources and the member list",
        "figure_reference_scope": "main.tex and sections/*.tex only; ai_details.tex not read",
        "baseline_commit": BASELINE_COMMIT,
        "integrated_ai_commit": INTEGRATED_AI_COMMIT,
        "baseline_zip_sha256": BASELINE_ZIP_SHA256,
        "baseline_scope": "Paper baseline commit precedes the concurrent AI-only ZIP update; the inspected newer ZIP is retained as input",
        "concurrent_ai_isolation": "figure_legibility_refresh_20260913/concurrent_ai_isolation.json",
        "baseline_report": "figure_legibility_refresh_20260913/prior_report.json",
        "frozen_inputs": "figure_legibility_refresh_20260913/frozen_inputs.json",
        "pde_or_parameter_scenarios_run": False,
        "workbooks_or_arrays_reexported": False,
        "paper_table_numerical_validation": "not rerun; preserved numerical members compared byte for byte",
        "figure_count": len(figures),
        "changed_figure_count": len(REPLACEMENTS),
        "retained_figures": [{"name": member(name), "sha256": digest(old[member(name)])} for name in sorted(RETAINED)],
        "all_figures_match_current_paper_bytes": True,
        "ai_pdf_byte_identical_to_baseline_zip": True,
        "ai_pdf_sha256": digest(old[ai_name]),
        "ai_pdf_page_count": ai_pages,
        "other_members_byte_identical_to_baseline_zip": True,
        "other_members_count": len(retained_names),
        "removed_members": sorted(set(old) - set(updated)),
        "added_members": sorted(set(updated) - set(old)),
        "changed_existing_members": sorted(name for name in set(old) & set(updated) if old[name] != updated[name]),
        "unchanged_numerical_members": [{"name": name, "sha256": digest(old[name]), "bytes": len(old[name])} for name in result_names],
        "current_figure_hashes": [{"name": member(name), "sha256": digest(path.read_bytes())} for name, path in sorted(figures.items())],
        "identity_raw_binary_findings": raw_findings,
        "identity_pdf_metadata_findings": metadata_findings,
        "identity_scope": "literal token scan of uncompressed members and PDF metadata; not OCR or a full anonymity proof",
        "workbook_docprops_members": workbook_metadata,
        "zip_crc_check": "passed",
        "zip": str(package.ZIP_PATH),
        "zip_bytes": package.ZIP_PATH.stat().st_size,
        "zip_mb": round(package.ZIP_PATH.stat().st_size / 1048576, 2),
        "zip_within_20mb": True,
        "zip_sha256": package.sha256(package.ZIP_PATH),
        "member_count": len(members),
        "members": members,
    }
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    original_report.write_text(encoded, encoding="utf-8")
    (EVIDENCE / "refresh_report.json").write_text(encoded, encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"members", "current_figure_hashes"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="freeze current figure/source-list hashes without changing the ZIP")
    main(parser.parse_args().freeze)
