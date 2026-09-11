"""Read-only probes of the delivered semidiscrete operators, not a PDE rerun."""
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "q2_final_delivery" / "source"))

import numpy as np
from q2_core import CoupledFV, Parameters
from q2_axisymmetric import AxisymmetricFV


class FixedEnvironment:
    def __call__(self, t):
        return np.array([41.0, 0.04])


def independent_capacity(c):
    return (650.0 + 128.0 * c) * (1450.0 + 4186.0 * c) / (1.0 + c)


def main():
    env = FixedEnvironment()
    p = Parameters()
    op = CoupledFV(20, p)
    x = op.r / p.R
    temp = 28.0 + 10.0 * x**2
    moisture = 2.55 - 0.8 * x**2
    y = np.column_stack([temp, moisture]).ravel()
    rhs = op.evaluate(400.0, y, env).reshape(-1, 2)
    expected_heat = -p.R * p.hT * (temp[-1] - 41.0)
    expected_mass = -p.R * p.hm * (moisture[-1] - 0.04)
    rng = np.random.default_rng(20260911)
    direction = rng.normal(size=y.size)
    jac = op.evaluate(400.0, y, env, True)
    complex_step = op.evaluate(400.0, y.astype(complex) + 1e-30j * direction, env).imag / 1e-30
    shifted = CoupledFV(20, p, temperature_offset=273.15)
    y_kelvin = y.copy()
    y_kelvin[::2] += 273.15
    results = {
        "scope": "manufactured smooth states; operator identities and directional Jacobian only; not an independent full solution",
        "radial_heat_balance_abs": float(abs(op.w @ (independent_capacity(moisture) * rhs[:, 0]) - expected_heat)),
        "radial_mass_balance_abs": float(abs(op.w @ rhs[:, 1] - expected_mass)),
        "radial_jacobian_relative_inf_error": float(np.max(abs(jac @ direction - complex_step)) / np.max(abs(complex_step))),
        "kelvin_rhs_max_abs_difference": float(np.max(abs(shifted.evaluate(400.0, y_kelvin, env) - rhs.ravel()))),
    }

    axis = AxisymmetricFV(20, 8, p)
    r, z = np.meshgrid(axis.r, axis.z)
    temp2 = 28.0 + 8.0 * (r / p.R)**2 + 3.0 * (z / (p.L / 2))**2
    moisture2 = 2.55 - 0.6 * (r / p.R)**2 - 0.2 * (z / (p.L / 2))**2
    y2 = np.stack([temp2, moisture2], axis=-1).ravel()
    rhs2 = axis.evaluate(400.0, y2, env).reshape(-1, 2)
    results["axis_heat_balance_abs"] = float(abs(
        axis.w @ (independent_capacity(moisture2.ravel()) * rhs2[:, 0])
        + np.sum(axis.area * p.hT * (temp2.ravel() - 41.0))))
    results["axis_mass_balance_abs"] = float(abs(
        axis.w @ rhs2[:, 1] + np.sum(axis.area * p.hm * (moisture2.ravel() - 0.04))))
    direction2 = rng.normal(size=y2.size)
    predicted = axis.evaluate(400.0, y2, env, True) @ direction2
    differences = []
    # np.bincount only accepts real weights, so central differences are used here.
    for step in (1e-4, 1e-5, 1e-6):
        measured = (axis.evaluate(400.0, y2 + step * direction2, env)
                    - axis.evaluate(400.0, y2 - step * direction2, env)) / (2 * step)
        differences.append({"step": step, "relative_inf_error": float(
            np.max(abs(predicted - measured)) / np.max(abs(measured)))})
    results["axis_jacobian_central_difference"] = differences
    assert results["radial_heat_balance_abs"] < 1e-12
    assert results["radial_mass_balance_abs"] < 1e-18
    assert results["radial_jacobian_relative_inf_error"] < 1e-12
    assert results["kelvin_rhs_max_abs_difference"] < 1e-10
    assert results["axis_heat_balance_abs"] < 1e-12
    assert results["axis_mass_balance_abs"] < 1e-18
    assert min(a["relative_inf_error"] for a in differences) < 1e-8
    results["passed"] = True
    output = Path(__file__).with_name("operator_spotcheck.json")
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
