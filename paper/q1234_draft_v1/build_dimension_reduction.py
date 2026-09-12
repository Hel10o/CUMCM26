"""Draw the added reduction-evidence figure from six frozen NPZ files only.

This script does not import or execute any solver or time integrator.  It needs
the full repository's frozen geometry arrays; the paper source ZIP supplies the
finished figure and the extracted plotting data, not a new PDE calculation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = ROOT / "q4_complete_delivery/v1/validation/geometry"
EVIDENCE = HERE / "evidence/content_finalization_20260912"
FIGURES = HERE / "figures"
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#666666"]
CASES = (
    ("q1", "问题一", "q1_80x128", "q1_80x0", 1800., "7.2533", ("2.274929", "2.293532")),
    ("q23", "问题二", "q23_80x256_integral", "q23_80x0_integral", 10800., "4.7118", ("1.327482", "1.382492")),
    ("q4", "问题四", "q4_80x128_integral", "q4_80x0_integral", 21600., "2.7379", ("1.024545", "1.065198")),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def style():
    # The font choice, sizes, colors and line styles follow build_assets.py.
    available = {item.name for item in font_manager.fontManager.ttflist}
    selected = next((s for s in ("Microsoft YaHei", "SimSun") if s in available), None)
    if selected is None:
        raise RuntimeError("Chinese plotting font not found")
    plt.rcParams.update({"font.family": selected, "font.size": 8.5, "axes.labelsize": 8.5,
        "axes.titlesize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5,
        "axes.linewidth": .65, "lines.linewidth": 1.3, "axes.unicode_minus": False,
        "pdf.fonttype": 42, "ps.fonttype": 42, "figure.facecolor": "white", "savefig.dpi": 300})
    return selected


def exact_index(values, wanted):
    indices = np.flatnonzero(np.isclose(values, wanted, rtol=0, atol=1e-8))
    assert len(indices) == 1, (wanted, indices)
    return int(indices[0])


def extract(path, wanted):
    if not path.is_file():
        raise FileNotFoundError(f"Frozen repository array required, no solve fallback: {path}")
    before = sha(path)
    with np.load(path, allow_pickle=False) as archive:
        data = {key: archive[key] for key in archive.files}
    assert sha(path) == before
    t = data["snapshot_times_s"]
    selected = np.flatnonzero(t <= wanted)
    end = exact_index(t, wanted)
    assert selected[-1] == end
    field = data["snapshots"][selected, :, :, 1]
    weights = data["weights"]
    assert np.all(weights > 0) and weights.size == np.prod(field.shape[1:])
    # Arrays cover a half-cylinder, measured outward from its symmetry plane.
    # The old executed source explicitly obtains mid from u[0], not u[nz//2].
    mid_index = exact_index(data["z_m"], 0.)
    assert mid_index == 0
    profile = data["snapshots"][end, mid_index, :, 1]
    time_index = exact_index(data["time_s"], wanted)
    radius = float(data["radius_m"][time_index])
    r0 = float(data["reference_r_m"][-1])
    r_current = data["reference_r_m"] * radius / r0
    assert len(profile) == len(r_current) == 81
    # mid is an independently stored 21-point resampling, not the 81-node field.
    assert data["mid"].shape[1] == 21
    np.testing.assert_allclose(profile[[0, -1]], data["mid"][time_index, [0, -1], 1], rtol=0, atol=1e-12)
    mean = field.reshape(len(selected), -1) @ weights / weights.sum()
    return {
        "path": rel(path), "sha256": before, "snapshot_shape": list(data["snapshots"].shape),
        "mid_shape": list(data["mid"].shape), "weight_sum": float(weights.sum()),
        "midplane_index": mid_index, "midplane_z_m": float(data["z_m"][mid_index]),
        "z_max_m": float(data["z_m"][-1]), "profile_time_s": wanted,
        "reference_radius_m": r0, "current_radius_m": radius,
        "time_s": t[selected].tolist(), "mean_C_kg_per_kg": mean.tolist(),
        "profile_current_r_cm": (r_current * 100).tolist(), "profile_C_kg_per_kg": profile.tolist(),
        "stored_mid_endpoint_check": True,
    }


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    font = style()
    table_text = (HERE / "sections/validation_limits.tex").read_text(encoding="utf-8")
    table_match = re.search(r"\\label\{tab:wholebody\}(.*?)\\end\{table\}", table_text, re.S)
    assert table_match, "tab:wholebody not found"
    table_text = table_match.group(1)
    records = []
    for case, title, name_2d, name_1d, target, percent, expected_means in CASES:
        two = extract(GEOMETRY / (name_2d + ".npz"), target)
        one = extract(GEOMETRY / (name_1d + ".npz"), target)
        assert two["time_s"] == one["time_s"]
        np.testing.assert_array_equal(two["profile_current_r_cm"], one["profile_current_r_cm"])
        c0 = two["mean_C_kg_per_kg"][0]
        assert abs(c0 - 2.55) < 1e-12 and abs(one["mean_C_kg_per_kg"][0] - c0) < 1e-12
        means = tuple(f"{d['mean_C_kg_per_kg'][-1]:.6f}" for d in (two, one))
        increase = 100 * ((c0 - two["mean_C_kg_per_kg"][-1]) / (c0 - one["mean_C_kg_per_kg"][-1]) - 1)
        assert means == expected_means and f"{increase:.4f}" == percent
        assert "&".join((*expected_means, percent)) in table_text
        records.append({"case": case, "title": title, "time_s": target, "two_d": two, "one_d": one,
            "loss_increase_percent_unrounded_postprocessing": increase,
            "loss_increase_percent_display": percent, "table_mean_display": list(means),
            "tab_wholebody_display_match": True})

    fig, axes = plt.subplots(2, 3, figsize=(16.4 / 2.54, 11.5 / 2.54))
    fig.subplots_adjust(left=.102, right=.98, bottom=.115, top=.87, hspace=.70, wspace=.48)
    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#D7DCE0", lw=.5, alpha=.8)
        ax.set_axisbelow(True)
        ax.tick_params(direction="out", pad=2)
    for col, record in enumerate(records):
        title, target = record["title"], record["time_s"]
        a, b = record["two_d"], record["one_d"]
        upper, lower = axes[:, col]
        for data, color, linestyle, label in ((a, COLORS[0], "-", "二维"), (b, COLORS[1], "--", "配对一维")):
            upper.plot(data["profile_current_r_cm"], data["profile_C_kg_per_kg"], color=color, ls=linestyle, label=label)
            lower.plot(np.asarray(data["time_s"]) / 3600, data["mean_C_kg_per_kg"], color=color, ls=linestyle,
                       marker="o", ms=2.0, markeredgewidth=0)
        timing = "1800 s" if col == 0 else f"{target / 3600:g} h"
        upper.set(title=f"({chr(97 + col)}) {title}，{timing}", xlabel="当前径向距离 / cm",
                  xlim=(0, a["profile_current_r_cm"][-1]))
        lower.set(title=f"({chr(100 + col)}) {title}整根均值", xlabel="时间 / h", xlim=(0, target / 3600 * 1.03))
        upper.set_xticks([0, .5, 1, 1.5, 2] if col < 2 else [0, .5, 1])
        lower.set_xticks(([0, .25, .5], [0, 1, 2, 3], [0, 2, 4, 6])[col])
        lower.fill_between(np.asarray(a["time_s"]) / 3600, a["mean_C_kg_per_kg"], b["mean_C_kg_per_kg"],
                           color="#CCCCCC", alpha=.4, linewidth=0)
        midpoint = (a["mean_C_kg_per_kg"][-1] + b["mean_C_kg_per_kg"][-1]) / 2
        lower.annotate("失水增加 " + record["loss_increase_percent_display"] + "%",
                       xy=(target / 3600, midpoint), xytext=(.30, .77), textcoords="axes fraction",
                       ha="left", va="center", fontsize=7.5,
                       arrowprops={"arrowstyle": "-", "lw": .6, "color": "#555555"})
    axes[0, 0].set_ylabel("中截面含水率 / (kg/kg)")
    axes[1, 0].set_ylabel("体积加权平均 / (kg/kg)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.55, .995), ncol=2, frameon=False, handlelength=3.)
    outputs = []
    for suffix in ("pdf", "png"):
        path = FIGURES / ("dimension_reduction." + suffix)
        if suffix == "pdf":
            fig.savefig(path, metadata={"CreationDate": None, "ModDate": None})
        else:
            fig.savefig(path, dpi=300)
        outputs.append(path)
    plt.close(fig)
    data_path = EVIDENCE / "dimension_reduction_plot_data.json"
    data_path.write_text(json.dumps({"schema_version": 1, "cases": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs.append(data_path)

    dependencies = {}
    for record in records:
        for key in ("two_d", "one_d"):
            entry = record[key]
            assert sha(ROOT / entry["path"]) == entry["sha256"]
            dependencies[entry["path"]] = {"sha256": entry["sha256"], "purpose": "frozen field, snapshot times, reference weights and geometry"}
    for path, purpose in ((HERE / "build_assets.py", "copied plotting style; source read only, not executed"),
                          (ROOT / "q4_complete_delivery/v1/source/geometry_solver_executed.py", "read-only coordinate interpretation; lines 141 and 198; never imported or executed")):
        dependencies[rel(path)] = {"sha256": sha(path), "purpose": purpose}
    manifest = {
        "schema_version": 1, "git_commit_read": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script": rel(Path(__file__)), "script_sha256": sha(Path(__file__)),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "matplotlib": matplotlib.__version__, "font": font, "executable": sys.executable},
        "scope": "Read six frozen NPZ files, sum saved field values with saved weights, and draw; no PDE solve, time integration, state interpolation or parameter scenario.",
        "dependencies": dependencies,
        "methods": {
            "midplane": "z_m=0, index 0 of a saved half-cylinder; full 81-node snapshot radial profile. mid contains 21 resampled nodes and is used only to check the two endpoints.",
            "current_radius": "reference_r_m * saved radius_m(t) / reference_r_m[-1]; q4 at 21600 s has R=0.013740000000000002 m.",
            "mean": "sum(flatten(snapshots[..., C]) * weights) / sum(weights). Half-cylinder symmetry and common circumference factors cancel. Q4 affine current-volume factor q(t)^2 also cancels in the normalized mean.",
            "mass_interpretation": "体积加权平均在空间均匀干密度假设下等于干质量加权平均。",
            "curve_sampling": "Only stored snapshots at or before the indicated time; plotted lines connect saved points, with markers. No new time states or smoothed interpolation.",
            "loss_increase": "100 * ((C0 - mean_2D) / (C0 - mean_1D) - 1), C0=2.55. This is not the relative error of mean moisture.",
            "display": "Exactly 7.2533%, 4.7118%, 2.7379%, and the six corresponding mean values match tab:wholebody; extra unrounded arithmetic is confined to evidence.",
            "caption_max_differences": "Q1 0-1800 s midplane sampled maximum C difference 4.09e-9; Q2 0-10800 s 2.24706e-5. Existing body figures, not newly claimed end-profile maxima. No Q4 maximum difference is added.",
        },
        "checks": {"all_six_input_hashes_unchanged": True, "all_exact_snapshot_times_found": True,
            "paired_times_and_current_radii_match": True, "all_saved_mid_endpoints_match": True,
            "all_three_table_percentages_and_six_means_match": True},
        "source_zip_dependency": "Regenerating this figure requires the listed frozen repository arrays and the build style source; the source ZIP includes completed figures and extracted plotting data. Missing arrays raise an error, never a solver fallback.",
        "outputs": {rel(p): {"sha256": sha(p), "bytes": p.stat().st_size} for p in outputs},
    }
    (EVIDENCE / "figure_sources.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: 6 frozen arrays unchanged; 3 percentages and 6 means match tab:wholebody; figure PDF/PNG and data provenance written.")


if __name__ == "__main__":
    main()
