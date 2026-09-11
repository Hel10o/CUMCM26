"""Read-only arithmetic audit of delivered Q3 scenarios; never integrates a PDE."""
from pathlib import Path
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VALIDATION = ROOT / "q3_final_delivery" / "validation"

def read(name):
    return json.loads((VALIDATION / name).read_text(encoding="utf-8"))

def critical(name):
    return read(name)["event"]["critical_s"]

summary = read("summary.json")
main = summary["event"]["critical_s"]
end = summary["event"]["execution_s"]
nominal = critical("scenario_nominal.json")
geometry = {row["case"]: row for row in read("geometry_comparison.json")}
g40 = geometry["cylinder40x64_iso"]["critical_s"]
g80 = geometry["cylinder80x64_iso"]["critical_s"]
g40z128 = geometry["cylinder40x128_iso"]["critical_s"]
r40 = critical("radial40.json")
r80 = critical("radial80.json")
dr40, dr80 = r40-main, r80-main
d40, d80, dz128 = g40-r40, g80-r80, g40z128-r40
out = {
    "scope": "Arithmetic from delivered JSON only; no PDE rerun or 2D extrapolated answer.",
    "main_1d_critical_s": main,
    "main_1d_execution_s": end,
    "main_execution_margin_s": end-main,
    "main_execution_0p03_budget_formula_s": .36*math.ceil((main+.03)/.36),
    "user_comparison_s": 206901,
    "main_critical_minus_user_s": main-206901,
    "main_execution_minus_user_s": end-206901,
    "nominal_512_critical_s": nominal,
    "nominal_512_next_integer_second_s": math.ceil(nominal),
    "nominal_512_next_integer_margin_s": math.ceil(nominal)-nominal,
    "nominal_512_same_grid_mean_critical_s": critical("integral512.json"),
    "nominal_minus_same_grid_mean_s": nominal-critical("integral512.json"),
    "radial40_bias_vs_main_s": dr40,
    "radial80_bias_vs_main_s": dr80,
    "radial_bias_ratio_40_over_80": dr40/dr80,
    "cylinder40x64_iso_critical_s": g40,
    "cylinder80x64_iso_critical_s": g80,
    "cylinder40x128_iso_critical_s": g40z128,
    "matched_40x64_end_effect_s": d40,
    "matched_80x64_end_effect_s": d80,
    "matched_40x128_end_effect_s": dz128,
    "matched_radial_refinement_change_s": d80-d40,
    "matched_axial_refinement_change_s": dz128-d40,
    "coarse_80x64_minus_main_s": g80-main,
    "coarse_80x64_identity_residual_s": (g80-main)-(dr80+d80),
    "projection_effect_40x64_s": g40-geometry["cylinder40x64"]["critical_s"],
    "not_an_answer_radial_bias_removed_80x64_s": main+d80,
    "not_an_answer_additive_missing80x128_diagnostic_s": main+d80+dz128-d40,
    "warning": "The last two values assume transferable radial bias and additive refinement corrections. They are not completed 2D solutions, validated Richardson limits, error bounds, or new official answers."
}
(HERE / "geometry_diagnostic.json").write_text(json.dumps(out, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
