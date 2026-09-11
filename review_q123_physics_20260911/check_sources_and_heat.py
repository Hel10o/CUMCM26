"""Read-only source and energy-scale checks; no new drying PDE is solved."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PKG = ROOT / 'q3_refinement_delivery'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []
    lines = (PKG/'MANIFEST.sha256').read_text(encoding='utf-8-sig').splitlines()
    entries = [line.split('  ', 1) for line in lines if line.strip()]
    bad = [name for expected, name in entries if not (PKG/name).is_file() or sha(PKG/name) != expected]
    actual = {p.relative_to(PKG).as_posix() for p in PKG.rglob('*') if p.is_file()}
    checks.append({'check': 'delivery_manifest', 'passed': not bad, 'entries': len(entries), 'mismatches': bad})
    checks.append({'check': 'manifest_coverage', 'passed': actual == {name for _, name in entries} | {'MANIFEST.sha256'}, 'files': len(actual)})
    frozen = json.loads((OUT/'original_refinement_hashes.json').read_text(encoding='utf-8'))
    changed = [name for name, expected in frozen.items() if not (PKG/name).is_file() or sha(PKG/name) != expected]
    checks.append({'check': 'new_delivery_unchanged', 'passed': not changed and actual == set(frozen), 'changed': changed})
    mapping = {
        'inputs/attachment1.xlsx': 'A题/附件/附件1.xlsx',
        'inputs/problem.pdf': 'A题/A题.pdf',
        'inputs/result3_blank.xlsx': 'A题/附件/附件3/result3.xlsx',
        'validation/numeric/reference80_radau_historical.npz': 'q3_final_delivery/validation/reference80.npz',
        'validation/numeric/reference160_bdf_historical.npz': 'q3_final_delivery/validation/reference160.npz',
        'validation/numeric/reference80_official_endpoint_historical.npz': 'q3_final_delivery/validation/reference80_official_endpoint.npz',
        'validation/numeric/reference160_official_endpoint_historical.npz': 'q3_final_delivery/validation/reference160_official_endpoint.npz',
    }
    for local, old in mapping.items():
        checks.append({'check': 'source_identity:' + local, 'passed': sha(PKG/local) == sha(ROOT/old), 'original': old, 'sha256': sha(PKG/local)})
    result = {'checks': checks, 'all_pass': all(x['passed'] for x in checks), 'source_zip_limit': 'The archive hash quoted by Pro is retained as provenance; that exact archive is not separately present or verified here. Its retained numerical/input files are compared directly to the repository originals.'}
    (OUT/'source_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    p = ROOT/'q1_complete_delivery/q1_delivery/output/q1_unrounded.npz'
    with np.load(p) as z:
        t = z['time_s']; cbar = z['average_C']; Tbar = z['average_temperature_degC']
        Ts = z['temperature_degC'][:,-1]; Ta = z['environment'][:,0]
        R, L, rho, cp, ht, C0, T0 = .02, .25, 820., 2600., 25., 2.55, 28.
        volume = np.pi*R*R*L; area = 2*np.pi*R*L
        dry_density = rho/(1+C0); dry_mass = dry_density*volume
        water_loss = dry_mass*(C0-cbar[-1])
        latent = 2.45e6*water_loss
        sensible = rho*cp*volume*(Tbar[-1]-T0)
        # Diagnostic quadrature of the 1 s samples, separate from the solver's dense balance.
        convective_input = np.trapezoid(area*ht*(Ta-Ts), t)
        humidity_ratio = z['environment'][-1,1]
        pv = 101.325*humidity_ratio/(.621945+humidity_ratio)
        log_ratio = np.log(pv/.6108)
        dew = 237.3*log_ratio/(17.27-log_ratio)
        psat_diagnostic = .6108*np.exp(17.27*11.902627810118135/(11.902627810118135+237.3))
        heat = {
            'scope': 'Fresh postprocessing of frozen Q1 solution; no coupled latent-heat PDE run.',
            'solution_sha256': sha(p),
            'additional_assumptions': ['820 kg/m3 is initial wet bulk density', 'fixed dry density 820/(1+2.55)', 'all outward effective water loss evaporates at the surface', 'latent heat 2.45 MJ/kg used as a scale estimate'],
            'time_s': float(t[-1]), 'dry_density_kg_m3': dry_density,
            'dry_mass_kg': dry_mass, 'water_loss_kg': float(water_loss),
            'latent_J': float(latent), 'baseline_sensible_J': float(sensible),
            'baseline_convective_input_1s_trapezoid_J': float(convective_input),
            'convective_minus_sensible_J': float(convective_input-sensible),
            'latent_to_sensible': float(latent/sensible),
            'latent_to_baseline_convective_input': float(latent/convective_input),
            'lambda_temperature_range_20_50_C_J_kg': [2.501e6-2361*20, 2.501e6-2361*50],
            'conditional_air_check': {'assumptions': ['air value is kg vapor/kg dry air', 'pressure 101.325 kPa', 'FAO Tetens approximation'], 'pv_kPa': float(pv), 'dew_point_C': float(dew), 'historical_latent_only_surface_C': 11.902627810118135, 'saturation_pressure_at_that_surface_kPa': float(psat_diagnostic)},
            'interpretation': 'The latent estimate exceeds baseline heating, so omission is not demonstrably small under these assumptions. After coupling, both evaporation and surface temperature/convective heat change; baseline heating is not a fixed available-energy ceiling. A temperature below the conditional dew point with persistent outward evaporation diagnoses incompatible closures, not proof that latent heat is negligible.'
        }
    (OUT/'q1_heat_scale.json').write_text(json.dumps(heat, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'source': result, 'q1_heat_scale': heat}, ensure_ascii=False, indent=2))
    if not result['all_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
