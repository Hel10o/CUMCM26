"""Read-only audit of stored Q1 fields; no solver functions are imported."""
from pathlib import Path
import json
import numpy as np

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'q1_complete_delivery/q1_delivery/output'
z = np.load(OUT / 'q1_unrounded.npz')
report = {}
for label, key, initial, outward_sign in [
    ('temperature', 'temperature_degC', 28., -1),
    ('moisture', 'moisture_dry_basis', 2.55, 1),
]:
    u = z[key]
    field = 'T' if label == 'temperature' else 'C'
    f = np.load(OUT / f'{field}_n10240.npz')
    r = f['internal_radius_m']
    s = f['internal_snapshots']
    h = r[1] - r[0]
    # Independent fourth-order backward derivative, at actual surface nodes.
    grad = (25*s[1:,-1]-48*s[1:,-2]+36*s[1:,-3]-16*s[1:,-4]+3*s[1:,-5])/(12*h)
    tt = f['snapshot_times_s'][1:].astype(int)
    ambient = z['environment'][tt, 0 if field == 'T' else 1]
    diffusion = 0.36 if field == 'T' else 7e-9*np.exp(-0.89/s[1:,-1])
    beta = 25. if field == 'T' else 8e-7
    internal_flux = -diffusion*grad
    boundary_flux = beta*(s[1:,-1]-ambient)
    dr = np.diff(u, axis=1)
    dt = np.diff(u, axis=0)
    violation_r = max(0., float(dr.max() if field == 'C' else -dr.min()))
    violation_t = max(0., float(dt.max() if field == 'C' else -dt.min()))
    metrics = {
        'shape': list(u.shape), 'all_finite': bool(np.isfinite(u).all()),
        'initial_max_abs_error': float(np.max(np.abs(u[0]-initial))),
        'min': float(u.min()), 'max': float(u.max()),
        'radial_monotonicity_violation': violation_r,
        'time_monotonicity_violation': violation_t,
        'boundary_max_abs_residual': float(np.max(np.abs(internal_flux-boundary_flux))),
        'boundary_max_relative_residual': float(np.max(np.abs((internal_flux-boundary_flux)/boundary_flux))),
        'boundary_residual_units': 'W/m^2' if field == 'T' else '(kg/kg)*m/s',
        'boundary_note': 'seven positive paper times; independently differentiated snapshots, finite-difference diagnostic',
        'boundary_flux_direction_correct': bool(np.all(outward_sign*boundary_flux > 0)),
        'snapshot_output_nodes_equal': bool(np.array_equal(s[:,::512],u[f['snapshot_times_s'].astype(int)])),
        'values_1800_at_0_0p5_1_1p5_2_cm': [float(v) for v in u[1800,::5]],
    }
    assert metrics['all_finite'] and metrics['initial_max_abs_error'] == 0
    assert violation_r < 1e-8 and violation_t < 1e-8
    assert metrics['boundary_flux_direction_correct'] and metrics['snapshot_output_nodes_equal']
    report[label] = metrics
path = Path(__file__).with_name('field_properties.json')
path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
