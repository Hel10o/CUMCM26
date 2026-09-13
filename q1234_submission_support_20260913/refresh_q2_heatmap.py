"""Replace the Q2 profile figure with the approved heatmap without numerical rebuilds.

This narrowly scoped packaging step replaces the figure set and its source list
in the existing support ZIP. It never invokes solvers or workbook exporters.
"""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import re
import shutil
import zipfile

import fitz

import build_package as package


BASELINE_COMMIT = "1b84c827ae72353b37549715ff4da5513cc61ea1"
BASELINE_ZIP_SHA256 = "d703b922b87f88d7f08d1d3dd05cc2b46d4d486a725f2c1a2f444c7aaf5ab5c3"
EVIDENCE = package.BASE / "evidence" / "q2_heatmap_refresh_20260913"
SOURCE_LIST = "support/图表来源清单.md"
FROZEN_HEATMAP_SHA256 = "47fd500235089fddc27d421ead469e8ca59c268ad14d499f8b6dde9a051b4a0e"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert package.sha256(package.PAPER / "figures/q2_heatmap/q2_fields.pdf") == FROZEN_HEATMAP_SHA256
    old_zip_bytes = package.ZIP_PATH.read_bytes()
    assert digest(old_zip_bytes) == BASELINE_ZIP_SHA256, "refresh baseline changed; inspect before rebuilding"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    baseline_report = EVIDENCE / "prior_report.json"
    original_report = package.BASE / "evidence" / "package_report.json"
    if baseline_report.exists():
        assert json.loads(baseline_report.read_text(encoding="utf-8"))["zip_sha256"] == BASELINE_ZIP_SHA256
    else:
        shutil.copy2(original_report, baseline_report)

    with zipfile.ZipFile(BytesIO(old_zip_bytes)) as archive:
        assert archive.testzip() is None
        old = {info.filename: archive.read(info.filename) for info in archive.infolist()}
        infos = {info.filename: info for info in archive.infolist()}

    figure_prefix = package.TOP + "/figures/"
    old_figures = {name for name in old if name.startswith(figure_prefix)}
    current_figures = {
        package.TOP + "/" + path.relative_to(package.PAPER).as_posix(): path
        for path in package.paper_figures()
    }
    assert len(old_figures) == 12 and len(current_figures) == 12
    assert old_figures - current_figures.keys() == {package.TOP + "/figures/font_revision/q2_profiles.pdf"}
    assert current_figures.keys() - old_figures == {package.TOP + "/figures/q2_heatmap/q2_fields.pdf"}
    assert all(old[name] == path.read_bytes() for name, path in current_figures.items() if name in old_figures)
    assert all(path.suffix == ".pdf" for path in current_figures.values())

    # Only the figure source list is allowed to change under support/.
    support_prefix = package.TOP + "/support/"
    current_support = {
        package.TOP + "/" + path.relative_to(package.PAPER).as_posix(): path
        for path in (package.PAPER / "support").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    assert set(current_support) == {name for name in old if name.startswith(support_prefix)}
    support_changes = [name for name, path in current_support.items() if old[name] != path.read_bytes()]
    assert support_changes == [package.TOP + "/" + SOURCE_LIST], support_changes

    updated = {name: data for name, data in old.items() if name not in old_figures}
    updated.update({name: path.read_bytes() for name, path in current_figures.items()})
    updated[package.TOP + "/" + SOURCE_LIST] = (package.PAPER / SOURCE_LIST).read_bytes()
    listing_name = package.TOP + "/支撑材料文件列表.md"
    listing = old[listing_name].decode("utf-8")
    listing = re.sub(r"(?m)^- `figures/[^\r\n]+[\r\n]+", "", listing)
    new_lines = "\n".join("- `" + name.removeprefix(package.TOP + "/") + "`" for name in sorted(current_figures))
    marker = "- `literature/"
    assert marker in listing
    updated[listing_name] = listing.replace(marker, new_lines + "\n" + marker, 1).encode("utf-8")

    result_names = sorted(name for name in old if name.startswith(package.TOP + "/results/"))
    assert len(result_names) == 5
    assert all(updated[name] == old[name] for name in result_names)
    raw_findings = []
    pdf_metadata_findings = []
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
                        pdf_metadata_findings.append({"file": name, "needle": token})
    assert not raw_findings and not pdf_metadata_findings
    workbook_metadata = {}
    for name in result_names:
        if name.endswith(".xlsx"):
            with zipfile.ZipFile(BytesIO(updated[name])) as workbook:
                workbook_metadata[name] = [member for member in workbook.namelist() if member.startswith("docProps/")]
                assert not workbook_metadata[name]

    # Write only to the explicitly named output directory; no staging-tree delete.
    output_dir = package.ZIP_PATH.parent.resolve()
    assert output_dir.is_relative_to(package.BASE.resolve())
    temporary = output_dir / "A题_支撑材料.heatmap-refresh.tmp"
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
        assert {name for name in archive.namelist() if name.startswith(figure_prefix)} == set(current_figures)
        assert all(archive.read(name) == path.read_bytes() for name, path in current_figures.items())
        assert all(archive.read(name) == old[name] for name in result_names)
    assert temporary.stat().st_size <= 20 * 1024 * 1024
    temporary.replace(package.ZIP_PATH)

    report = {
        "operation": "Q2 figure 5 heatmap replacement and source-list packaging refresh only",
        "baseline_commit": BASELINE_COMMIT,
        "baseline_zip_sha256": BASELINE_ZIP_SHA256,
        "baseline_report": "q2_heatmap_refresh_20260913/prior_report.json",
        "paper_table_numerical_validation": "not rerun; historical checks retained in q2_figure_refresh_20260913/baseline_package_report.json",
        "full_trajectory_values": 8690094,
        "full_trajectory_validation": "not rerun; existing NPZ bytes retained exactly from baseline ZIP",
        "pde_or_parameter_scenarios_run": False,
        "workbooks_or_arrays_reexported": False,
        "figure_count": len(current_figures),
        "other_11_figures_byte_identical_to_prior_zip": True,
        "frozen_heatmap_sha256": FROZEN_HEATMAP_SHA256,
        "figures_match_current_paper_bytes": True,
        "removed_members": sorted(set(old) - set(updated)),
        "added_members": sorted(set(updated) - set(old)),
        "changed_existing_members": sorted(name for name in set(old) & set(updated) if old[name] != updated[name]),
        "unchanged_numerical_members": [{"name": name, "sha256": digest(old[name]), "bytes": len(old[name])} for name in result_names],
        "current_figure_hashes": [{"name": name, "sha256": digest(path.read_bytes())} for name, path in current_figures.items()],
        "identity_raw_binary_findings": raw_findings,
        "identity_pdf_metadata_findings": pdf_metadata_findings,
        "identity_scope": "literal token scan of all uncompressed member bytes plus PDF metadata; not OCR or a complete anonymity proof",
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
    main()
