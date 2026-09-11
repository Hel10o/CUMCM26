"""Read preserved evidence and verify final Q2 refinement acceptance artifacts.

Writes only final_integrity_checks.json next to this script. No PDE computation.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def snapshot_check(base, snapshot):
    before = read(snapshot)
    after = {p.relative_to(base).as_posix(): digest(p)
             for p in base.rglob("*") if p.is_file()}
    return {"files": len(after), "unchanged": before == after,
            "changed_or_missing": [k for k, v in before.items() if after.get(k) != v],
            "added": sorted(set(after) - set(before))}

def main():
    new_base = ROOT / "q2_refinement_delivery"
    new = snapshot_check(new_base, HERE / "original_refinement_hashes.json")
    old = snapshot_check(ROOT / "q2_final_delivery",
                         ROOT / "review_q2_20260911/original_delivery_hashes.json")
    manifest = []
    for line in (new_base / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = (new_base / relative).resolve()
        ok = path.is_relative_to(new_base.resolve()) and path.is_file() and digest(path) == expected
        manifest.append({"path": relative, "matches": ok})
    numeric = read(HERE / "numeric/numeric_audit.json")
    algebra = read(HERE / "model/closure_algebra_probe.json")
    fixed = read(HERE / "runtime/fixed/runtime_audit.json")
    probes = fixed["probes"]
    result_sha = digest(ROOT / "q2_final_delivery/output/result2.xlsx")
    expected_sha = "99059fe86feff53b64f0f091585645962b3d4379b9b945d4bcb1dcbb3a7a0af0"
    required = ["第二问最终核查报告.md", "采纳与勘误.md", "numeric/numeric_audit.md",
                "model/model_audit.md", "model/overlay_review.md", "runtime/runtime_audit.md",
                "runtime/overlay/source/q2_run_guard.py", "runtime/install_verified_runtime.py"]
    output = {
        "scope": "Final preserved-byte check and evidence summary; no full PDE rerun.",
        "new_pro_delivery": new, "original_q2_delivery": old,
        "new_manifest_count": len(manifest),
        "new_manifest_matches": all(x["matches"] for x in manifest),
        "new_manifest_failures": [x for x in manifest if not x["matches"]],
        "formal_result2_sha256": result_sha,
        "formal_result2_preserved": result_sha == expected_sha,
        "numeric_check_count": numeric["check_count"],
        "numeric_checks_passed": numeric["all_checks_passed"],
        "algebra_passed": algebra["status"] == "passed",
        "runtime_fixed_probe_count": len(probes),
        "runtime_fixed_probes_passed": all(x["passed"] for x in probes),
        "runtime_fixed_bundled_processes": fixed["bundled_tests"],
        "runtime_skips": "Two ordinary symlink tests skipped for unavailable Windows privilege; junction and hardlink probes executed.",
        "required_artifacts_exist": all((HERE / x).is_file() for x in required),
    }
    output["all_final_checks_passed"] = all([
        new["unchanged"], old["unchanged"], output["new_manifest_matches"],
        output["formal_result2_preserved"], output["numeric_checks_passed"],
        output["algebra_passed"], output["runtime_fixed_probes_passed"],
        output["required_artifacts_exist"],
        all(x["exit_code"] == 0 for x in fixed["bundled_tests"]),
    ])
    (HERE / "final_integrity_checks.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k != "runtime_fixed_bundled_processes"},
                     ensure_ascii=False, indent=2))
    raise SystemExit(0 if output["all_final_checks_passed"] else 1)

if __name__ == "__main__":
    main()
