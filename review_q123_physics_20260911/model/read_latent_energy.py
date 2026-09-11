"""Postprocess the frozen Q1 conditional latent diagnostic; no PDE is solved."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
source = ROOT / "q1_complete_delivery/q1_delivery/output/validation/conditional_latent_T.npz"
validation = ROOT / "q1_complete_delivery/q1_delivery/output/validation/validation.json"
with np.load(source) as a:
    mean_temperature = float(a["average"][-1])
    final_time = float(a["time_s"][-1])
    surface_temperature = float(a["values"][-1, -1])
stats = json.loads(validation.read_text(encoding="utf-8"))["tests"]["latent_conditional"]
volume = math.pi * .02**2 * .25
delta_u = 820 * 2600 * volume * (mean_temperature - 28)
result = {
    "scope": "Readback and approximate energy bookkeeping of an old one-way conditional diagnostic, not a newly solved coupled physical model.",
    "source_npz": str(source.relative_to(ROOT)),
    "source_npz_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "source_validation": str(validation.relative_to(ROOT)),
    "source_validation_sha256": hashlib.sha256(validation.read_bytes()).hexdigest(),
    "time_s": final_time,
    "old_conditional_mean_temperature_C": mean_temperature,
    "old_conditional_surface_temperature_C": surface_temperature,
    "fixed_volumetric_heat_capacity_J_m3_K": 820 * 2600,
    "volume_m3": volume,
    "old_conditional_sensible_change_J": delta_u,
    "old_baseline_sensible_change_J": stats["baseline_sensible_J"],
    "old_conditional_latent_from_original_moisture_loss_J": stats["implied_latent_J"],
    "approximately_implied_new_convection_J": delta_u + stats["implied_latent_J"],
    "old_latent_to_baseline_sensible_ratio": stats["ratio_latent_to_sensible"],
    "limitations": [
        "The thermal diagnostic used interpolated 1-second baseline surface moisture with a fixed outward-loss law.",
        "Its new temperature was not fed back to a temperature-dependent gas-solid equilibrium relation.",
        "Convection above is reconstructed from storage plus original-track latent energy, not independently integrated here.",
        "Original moisture loss and interpolated diagnostic boundary have different numerical representations; do not infer exact equality to a boundary quadrature.",
        "The temperature is not a calibrated prediction, and its energy bookkeeping does not resolve the gas-phase driving-force contradiction."
    ]
}
(HERE / "old_latent_energy_readback.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
