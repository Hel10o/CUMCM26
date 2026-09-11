#!/usr/bin/env python3
"""Reproduce Q3 in a new directory, or independently verify saved artifacts.

No network access, remote writes, or changes to the original inputs are needed.
Full reproduction runs the successful cases sequentially to limit memory use.
"""
from __future__ import annotations
import argparse
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

# Set before importing NumPy/SciPy in this process or its subprocesses.
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "source"))
CASES = (
    "integral256", "integral512", "integral1024", "integral2048",
    "integral1024_tight", "harmonic512", "harmonic1024",
    "scenario_last", "scenario_nominal", "hT_minus20", "hT_plus20",
    "hm_minus20", "hm_plus20", "iso6h1024", "radial40", "radial80",
    "cylinder40x64", "cylinder40x64_iso", "cylinder80x64_iso",
    "cylinder40x128_iso",
)

def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def basic_exports(root: Path) -> None:
    """Export main-only evidence without borrowing results from other runs."""
    import numpy as np
    from make_report import table
    a = np.load(root / "output/main.npz")
    stats = json.loads((root / "output/main.json").read_text())
    event = stats["event"]
    if event is None:
        raise RuntimeError("No threshold crossing in the computed interval")
    maxima = a["event_fields_TC"][..., 1].max(axis=(1, 2))
    if not (maxima[0] > .15 and maxima[2] < .15 and maxima[3] < .15):
        raise AssertionError("Saved full-field threshold bracket failed")
    save(root / "output/end_event.json", {
        **event, "global_max_from_saved_fields": maxima.tolist(),
        "saved_event_times_s": a["event_time_s"].tolist(),
        "scope": "main-only rerun; no new independent or geometry validation",
        "reconstruction": "bounded PCHIP in r^2, axial-uniform formal domain",
        "strict_PDE_interval_error_certificate": False,
    })
    ts = a["time_s"]; c = a["sample_TC"][..., 1]
    ix = np.flatnonzero((ts > 0) & ((np.mod(ts, 21600) == 0) | (np.arange(len(ts)) == len(ts)-1)))
    tab = np.column_stack([ts[ix]/3600, c[ix][:, [0, 5, 10, 15, 20]]])
    for path, header, values in (
        ("table5.csv", ["time_h", "r0cm", "r0.5cm", "r1cm", "r1.5cm", "r2cm"], tab),
        ("result3_unrounded.csv", ["time_s"]+[f"r{r:g}cm" for r in a["radius_cm"]], np.column_stack([ts[1:], c[1:]])),
    ):
        with (root/"output"/path).open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(header); w.writerows(values)
    (root/"output/table5.md").write_text(table(tab.tolist(), ["时间/h","0 cm","0.5 cm","1 cm","1.5 cm","2 cm"], [".4f"]*6), encoding="utf-8")


def verify(root: Path, full: bool) -> dict:
    from validate_results import operator_checks, cylinder_analytic, analyze, xlsx_check
    if full:
        operator_checks(root/"validation")
        cylinder_analytic(root/"validation")
        analyze(root)
    result = xlsx_check(root)
    return {"xlsx": result, "full_saved_evidence_reanalysis": full}


def execute(command: list[str], log: Path, record: dict) -> None:
    print("RUN", log.stem, flush=True)
    with log.open("w", encoding="utf-8") as f:
        proc = subprocess.run(command, stdout=f, stderr=subprocess.STDOUT, check=False)
    record["executed_cases"].append({"case": log.stem, "returncode": proc.returncode})
    if proc.returncode:
        raise RuntimeError(f"{log.stem} failed ({proc.returncode}); see {log}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scope", choices=["full", "main", "verify"], default="full")
    ap.add_argument("--out", type=Path, help="New output directory; must not exist")
    ap.add_argument("--excel-engine", choices=["portable", "artifact"], default="portable")
    args = ap.parse_args()
    record = {"scope": args.scope, "started_utc": datetime.now(timezone.utc).isoformat(), "executed_cases": []}
    if args.scope == "verify":
        if args.out:
            ap.error("verify reads this delivery; do not supply --out")
        record["checks"] = verify(BASE, full=True)
        from make_report import generate
        generate(BASE)
        record["finished_utc"] = datetime.now(timezone.utc).isoformat()
        record["status"] = "passed"
        save(BASE/"validation/unified_verify.json", record)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return
    if args.out is None:
        ap.error("--out is required for a new calculation")
    root = args.out.resolve()
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite {root}")
    root.mkdir(parents=True)
    for directory in ("inputs", "source", "literature"):
        shutil.copytree(BASE/directory, root/directory, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("run_all.py", "requirements.txt", "source_access.md", "source_access.json"):
        if (BASE/name).exists(): shutil.copy2(BASE/name, root/name)
    for directory in ("output", "validation/configs"):
        (root/directory).mkdir(parents=True)
    try:
        source = root/"source"
        input_file = root/"inputs/attachment1.xlsx"
        # Actual saved numerical configurations, not fitted event-time targets.
        if args.scope == "full":
            for case in CASES:
                config = json.loads((BASE/"validation"/(case+".json")).read_text())["config"]
                cpath = root/"validation/configs"/(case+".json"); save(cpath, config)
                execute([sys.executable, str(source/"q3_solver.py"), "--config", str(cpath), "--input", str(input_file), "--out", str(root/"validation"/case)], root/"validation"/(case+".log"), record)
            for n, method in ((80,"Radau"),(160,"BDF")):
                case=f"reference{n}"
                execute([sys.executable,str(source/"q3_reference.py"),"--n",str(n),"--method",method,"--rtol","2e-11","--input",str(input_file),"--out",str(root/"validation"/case)],root/"validation"/(case+".log"),record)
        cpath=root/"validation/configs/main.json"
        shutil.copy2(BASE/"validation/configs/main.json",cpath)
        execute([sys.executable,str(source/"q3_solver.py"),"--config",str(cpath),"--input",str(input_file),"--out",str(root/"output/main")],root/"output/main.log",record)
        if args.scope=="full":
            from validate_results import analyze
            analyze(root)
        else:
            basic_exports(root)
        # Export only after large numerical processes have exited.
        from export_workbook import export_artifact, export_portable
        record["excel_export"]=(export_artifact if args.excel_engine=="artifact" else export_portable)(root)
        record["checks"]=verify(root,full=args.scope=="full")
        from make_report import figures, generate
        figures(root)
        if args.scope=="full":
            generate(root)
        else:
            (root/"README_MAIN.md").write_text("# 主模型复算\n\n本目录已从附件重新求解主模型、生成表5及Excel并全量回读。未重跑独立参考、二维几何和参数情景，不将历史验证冒充本次验证。完整结果见output/main.json与end_event.json。\n",encoding="utf-8")
        record["status"]="passed"
    except Exception as exc:
        record["status"]="failed";record["exception"]=repr(exc)
        raise
    finally:
        record["finished_utc"]=datetime.now(timezone.utc).isoformat()
        save(root/"validation/run_record.json",record)
    print(f"Completed: {root}")

if __name__=="__main__":
    main()
