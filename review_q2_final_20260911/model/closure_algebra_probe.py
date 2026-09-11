"""Independent exact-arithmetic checks of the proposed Q2 closure identities.

This verifies algebra on synthetic states; it is not a PDE simulation, material
parameter identification, or experimental validation. It imports no Pro code.
"""
from fractions import Fraction as F
from pathlib import Path
import json


def main():
    counts = {"energy_mass_elimination": 0, "domain_reference_invariance": 0,
              "surface_total_flux": 0, "surface_reference_invariance": 0,
              "boundary_nonuniqueness_positive_b": 0,
              "density_derivative_identity": 0, "coefficient_basis_conversion": 0}
    for i in range(1, 65):
        rho = F(100 + i)
        temp, conc = F(300 + i, 1), F(i + 10, 40)
        temp_t, div_j, div_q = F(i, 30), F(2-i, 11), F(i-4, 17)
        conc_t = -div_j / rho
        # H = cd*T + cw*C*T + beta*C^2 + gamma*T*C^2.
        cd, cw, beta, gamma = F(1450), F(4200), F(-100), F(3, 5)
        H_T = cd + cw*conc + gamma*conc**2
        H_C = cw*temp + 2*beta*conc + 2*gamma*temp*conc
        j = [F(i, 7), F(3-i, 8), F(i+9, 13)]
        grad_T = [F(2, 3), F(i, 9), F(4-i, 3)]
        grad_C = [F(i, 100), F(-2, 3), F(3-i, 19)]
        grad_h = [(cw+2*gamma*conc)*a+(2*beta+2*gamma*temp)*b
                  for a, b in zip(grad_T, grad_C)]
        j_grad_h = sum(a*b for a, b in zip(j, grad_h))
        expanded = rho*(H_T*temp_t+H_C*conc_t)+div_q+H_C*div_j+j_grad_h
        reduced = rho*H_T*temp_t+div_q+j_grad_h
        assert expanded == reduced
        counts["energy_mass_elimination"] += 1
        A_water = F(1000+i)
        shifted = rho*(H_T*temp_t+(H_C+A_water)*conc_t)+div_q+(H_C+A_water)*div_j+j_grad_h
        assert shifted == expanded
        counts["domain_reference_invariance"] += 1
        h_v, js, conv, rad = F(2500000), F(i, 10**6), F(-i, 5), F(i+4, 7)
        qn = conv+rad+(h_v-H_C)*js
        assert qn+H_C*js == conv+rad+h_v*js
        counts["surface_total_flux"] += 1
        assert conv+rad+((h_v+A_water)-(H_C+A_water))*js == qn
        counts["surface_reference_invariance"] += 1
        # Two distinct positive transfer rates can reproduce the same flux with
        # admissible positive equilibrium values; no unrestricted negative b is needed.
        cs, qhat, hm1, hm2 = F(1), F(1, 10**7), F(8, 10**7), F(10, 10**7)
        b1, b2 = cs-qhat/hm1, cs-qhat/hm2
        assert b1 > 0 and b2 > 0 and b1 != b2
        assert hm1*(cs-b1) == hm2*(cs-b2) == qhat
        counts["boundary_nonuniqueness_positive_b"] += 1
        # Quotient-rule derivative of (650+128*C)/(1+C).
        d_rho_d = (128*(1+conc)-(650+128*conc))/(1+conc)**2
        assert d_rho_d == F(-522)/(1+conc)**2
        counts["density_derivative_identity"] += 1
        kg, K = F(3, 100), F(i, 100)
        h_eq = kg*K/rho
        b = F(1, 20)
        assert rho*h_eq*(conc-b) == kg*K*(conc-b)
        counts["coefficient_basis_conversion"] += 1
    result = {
        "status": "passed",
        "arithmetic": "fractions.Fraction; exact rational equalities",
        "independent_of_pro_code": True,
        "checks": counts,
        "scope": "Synthetic algebra checks only. No PDE, material calibration or physical accuracy claim.",
        "important_condition": "The same water enthalpy reference shift must be applied to both h_v and h_bar_w at the surface."
    }
    p = Path(__file__).with_suffix(".json")
    p.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
