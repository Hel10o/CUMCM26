"""Property-preserving candidate R_L: constitutive helpers, NOT a PDE solver.

This module deliberately does not supply an equilibrium isotherm or a default
C_eq. A user-supplied material-side equilibrium mapping is mandatory for the
Robin boundary. Its tests are synthetic interface tests, not drying predictions.
SI units except temperature_degC and dry-basis moisture (kg water / kg dry solid).
"""
from __future__ import annotations
from typing import Callable, Any
import numpy as np

R_M = 0.02
FULL_LENGTH_M = 0.25
INITIAL_T_DEGC = 28.0
INITIAL_C = 2.55
HT = 25.0
HM = 8e-7


def properties(question: int, temperature_degC: Any, moisture: Any) -> dict[str, np.ndarray]:
    """Return the original problem's rho, cp, S=rho*cp, k and D.

    rho is used as an effective capacity coefficient, not asserted to be the
    instantaneous physical wet density of a stationary, fixed-volume mixture.
    """
    t, c = np.broadcast_arrays(np.asarray(temperature_degC, float), np.asarray(moisture, float))
    if not np.isfinite(t).all() or not np.isfinite(c).all() or np.any(c <= 0) or np.any(t+273.15 <= 0):
        raise ValueError('Finite T_K>0 and C>0 required; no silent clipping.')
    if question == 1:
        rho = np.full_like(c, 820.0)
        cp = np.full_like(c, 2600.0)
        k = np.full_like(c, 0.36)
        d = 7e-9*np.exp(-0.89/c)
    elif question in (2, 3):
        rho = 650.0+128.0*c
        cp = 1450.0+2736.0*c/(1.0+c)
        k = 0.21+0.38*c/(1.0+c)
        d = 2.4e-3*np.exp(-0.45/c-3850.0/(t+273.15))
    else:
        raise ValueError('question must be 1, 2, or 3; Q4 is not borrowed.')
    return dict(rho=rho, cp=cp, S=rho*cp, k=k, D=d)


def reference_dry_density(question: int) -> float:
    """Additional assumption: given initial density is initial wet bulk density."""
    if question not in (1, 2, 3):
        raise ValueError('question must be 1, 2, or 3')
    wet0 = 820.0 if question == 1 else 650.0+128.0*INITIAL_C
    return wet0/(1.0+INITIAL_C)


def latent_heat(temperature_degC: Any) -> np.ndarray:
    """FAO56 Annex 3 (3-1), converted to J/kg, evaluated locally as an approximation.

    FAO labels its T as air temperature. Substitution of surface temperature here
    is our local interfacial approximation, NOT a material desorption fit.
    Restricted to 0..60 degC for this helper; this is a user-model validity gate,
    not a certified validity interval quoted from FAO. No extrapolation by default.
    """
    t = np.asarray(temperature_degC, float)
    if not np.isfinite(t).all() or np.any((t < 0) | (t > 60)):
        raise ValueError('Surface T outside the candidate normal-temperature gate [0,60] degC.')
    return 2.501e6-2361.0*t


def surface_fluxes(question: int, t: float, surface_T: Any, surface_C: Any,
                   air_T: float, air_value: float,
                   equilibrium: Callable[..., Any] | None, *, latent: bool = True) -> dict[str, np.ndarray]:
    """Single effective material-side Robin law; no extra serial gas film.

    equilibrium(t=..., surface_T=..., air_T=..., air_value=...) must return kg
    water/kg dry solid. It cannot be inferred by equating air_value to solid C.
    Treating HM as a material-equivalent coefficient is a declared interpretation
    requiring confirmation. This function does not validate that interpretation.
    """
    if equilibrium is None:
        raise ValueError('Missing material-side equilibrium mapping; no arbitrary C_eq default is permitted.')
    ts, cs = np.broadcast_arrays(np.asarray(surface_T, float), np.asarray(surface_C, float))
    properties(question, ts, cs)
    if not np.isfinite([t, air_T, air_value]).all() or air_value < 0:
        raise ValueError('Invalid time/environment input.')
    ce = np.asarray(equilibrium(t=t, surface_T=ts, air_T=air_T, air_value=air_value), float)
    ce = np.broadcast_to(ce, cs.shape)
    if not np.isfinite(ce).all() or np.any(ce < 0):
        raise ValueError('Equilibrium mapping must produce finite nonnegative dry-basis values.')
    js = reference_dry_density(question)*HM*(cs-ce)
    qconv = HT*(air_T-ts)
    qlat = latent_heat(ts)*js if latent else np.zeros_like(js)
    return dict(j_out=js, qconv_in=qconv, qlatent_out=qlat,
                qcond_in=qconv-qlat, material_Ce=ce)
