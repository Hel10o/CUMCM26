"""Direct substitution of Appendix 3; scales are not drying-time predictions."""
from pathlib import Path
import json
import math


def state(T, C):
    rho = 650 + 128 * C
    cp = 1450 + 2736 * C / (1 + C)
    k = 0.21 + 0.38 * C / (1 + C)
    D = 0.0024 * math.exp(-0.45 / C - 3850 / (T + 273.15))
    alpha = k / (rho * cp)
    return dict(T_degC=T, C_kgkg=C, D_m2_s=D, alpha_m2_s=alpha,
                alpha_over_D=alpha / D, R2_over_D_h=0.02**2 / D / 3600,
                D_over_hm_m=D / 8e-7, Bi_m_R=8e-7 * 0.02 / D)


if __name__ == '__main__':
    result = {
        'source': 'A题/A题.pdf, Appendix 3; R=0.02 m and inherited hm=8e-7 m/s',
        'interpretation': 'Statewise diagnostic scales only; D/hm is an interface length scale, not a measured skin thickness, mesh requirement or final drying time.',
        'states': [state(28, 2.55), state(50, 2.55), state(50, 0.15),
                   state(50, 0.05), state(50.165, 0.04986)],
        'uniform_grid_dr_m': {str(n): 0.02 / n for n in [128, 256, 512, 1280, 2560]},
        'four_decimal_hour_quantum_s': 0.0001 * 3600,
        'rounding_half_quantum_s': 0.00005 * 3600,
    }
    target = Path(__file__).with_suffix('.json')
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
