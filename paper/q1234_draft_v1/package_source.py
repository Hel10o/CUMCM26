"""Create an editable paper archive; this is not the final competition support ZIP."""
from pathlib import Path
import hashlib
import json
import zipfile

BASE = Path(__file__).resolve().parent
OUT = BASE / "四问论文LaTeX源稿_v1.zip"
roots = ["main.tex", "ai_details.tex", "AI工具使用详情.pdf", "body_preview.tex", "build.ps1",
         "build_assets.py", "build_dimension_reduction.py", "build_visual_assets.py", "build_refined_assets.py", "build_workflow_spacing.py", "build_font_assets.py", "build_question_workflows.py", "build_ch6_assets.py", "figures/dimension_reduction.png", "validate_paper.py", "package_source.py", "README.md"]
files = [BASE / name for name in roots]
files.append(BASE / 'build_q1_legibility.py')
files.append(BASE / 'build_q2_revision_assets.py')
files.append(BASE / 'build_q2_heatmap.py')
files.append(BASE / 'build_q3_intro_workflow.py')
files.append(BASE / 'build_q3_white.py')
files.extend((BASE / 'figures' / 'q3_white').glob('*.png'))
files.extend((BASE / 'figures' / 'q3_intro').glob('*.png'))
files.extend((BASE / 'figures' / 'q2_heatmap').glob('*.png'))
files.extend((BASE / 'figures' / 'q2_revision').glob('*.png'))
files.extend((BASE / 'figures' / 'q1_legibility').glob('*.png'))
files.extend((BASE / "figures" / "visual_revision").glob("*.png"))
files.extend((BASE / "figures" / "visual_refinement").glob("*.png"))
files.extend((BASE / "figures" / "workflow_spacing").glob("*.png"))
files.extend((BASE / "figures" / "font_revision").glob("*.png"))
files.extend((BASE / "figures" / "question_workflows").glob("*.png"))
files.extend((BASE / "figures" / "ch6_revision").glob("*.png"))
for path in (BASE / "evidence").rglob("*"):
    if path.is_file() and path.suffix in {".md", ".json", ".txt", ".pdf", ".html"} and path.name != "source_package.json":
        files.append(path)
for directory in ["sections", "tables", "figures", "support", "visual_revision", "visual_refinement", "workflow_spacing"]:
    for path in (BASE / directory).rglob("*"):
        if not path.is_file() or any(p in {"__pycache__", ".venv", "output", "validation"} for p in path.relative_to(BASE).parts):
            continue
        if path.suffix in {".pyc", ".log", ".png"}:
            continue
        files.append(path)
files = sorted(set(files))
assert all(path.is_file() for path in files), "A required source file is missing"
manifest = {path.relative_to(BASE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files:
        archive.write(path, path.relative_to(BASE).as_posix())
    archive.writestr("SOURCE_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(OUT) as archive:
    assert archive.testzip() is None
    for name, sha in manifest.items():
        assert hashlib.sha256(archive.read(name)).hexdigest() == sha
evidence = {"purpose": "Editable LaTeX source archive, not the final competition support package",
            "file_count": len(files), "bytes": OUT.stat().st_size,
            "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
            "members_verified": len(manifest), "sources": manifest}
(BASE / "evidence" / "source_package.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
OUT.with_suffix(".zip.sha256").write_text(evidence["sha256"] + "  " + OUT.name + "\n", encoding="utf-8")
print(json.dumps({k:v for k,v in evidence.items() if k != "sources"}, ensure_ascii=False))
