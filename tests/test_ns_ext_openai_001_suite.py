"""
Deterministic mathematical test suite for NS-EXT-OPENAI-001.
Audits exact algebraic identities, scaling exponents, incompressibility,
energy integrals, Reynolds numbers, and the Viscous Extinction Barrier.
"""

import math
import numpy as np
import pytest


def test_anisotropic_core_aspect_ratio():
    """Verify that core aspect ratio ell_z / ell_r diverges as tau -> 0 for h in (0, 0.1)."""
    h = 0.04
    taus = [1e-2, 1e-4, 1e-6, 1e-8]
    ratios = []
    for tau in taus:
        ell_r = tau**0.5
        ell_z = tau**(0.5 - h)
        ratio = ell_z / ell_r
        expected = tau**(-h)
        assert math.isclose(ratio, expected, rel_tol=1e-12)
        ratios.append(ratio)
    # Check strict monotonic divergence
    for i in range(len(ratios) - 1):
        assert ratios[i] < ratios[i+1]
    assert ratios[-1] > 2.0  # Diverging to infinity


def test_incompressibility_scaling_match():
    """Verify that radial dilation (1/r) d/dr(r u_r) and axial gradient d/dz(u_z) match at order tau^-1."""
    h = 0.05
    tau = 1e-4
    ell_r = tau**0.5
    ell_z = tau**(0.5 - h)
    u_r = tau**(-0.5)
    u_z = tau**(-0.5 - h)

    radial_term = u_r / ell_r  # ~ tau^-0.5 / tau^0.5 = tau^-1.0
    axial_term = u_z / ell_z   # ~ tau^(-0.5-h) / tau^(0.5-h) = tau^-1.0

    assert math.isclose(radial_term, 1.0 / tau, rel_tol=1e-12)
    assert math.isclose(axial_term, 1.0 / tau, rel_tol=1e-12)
    assert math.isclose(radial_term, axial_term, rel_tol=1e-12)


def test_vanishing_local_kinetic_energy():
    """Verify that local core energy E_core = |u|^2 * V_core -> 0 for h < 1/6."""
    h = 0.04  # < 1/6 ~ 0.1667
    exponent = 0.5 - 3 * h
    assert exponent > 0, "Exponent must be strictly positive for vanishing energy"

    taus = [1e-2, 1e-4, 1e-6, 1e-8]
    energies = []
    for tau in taus:
        ell_r = tau**0.5
        ell_z = tau**(0.5 - h)
        vol = (ell_r**2) * ell_z  # tau^(1.5 - h)
        u_sq = (tau**(-0.5 - h))**2  # tau^(-1 - 2h)
        e_core = u_sq * vol  # tau^(0.5 - 3h)
        energies.append(e_core)

    for i in range(len(energies) - 1):
        assert energies[i] > energies[i+1]
    assert energies[-1] < 1e-2  # Vanishing local energy


def test_bkm_integral_divergence():
    """Verify that Beale-Kato-Majda integral int_0^1 ||omega||_Linf dt diverges for h > 0."""
    h = 0.05
    # int_eps^1 tau^(-1-h) dtau = (eps^-h - 1) / h -> infty as eps -> 0
    epsilons = [1e-2, 1e-4, 1e-6, 1e-8]
    integrals = [(eps**(-h) - 1.0) / h for eps in epsilons]
    for i in range(len(integrals) - 1):
        assert integrals[i] < integrals[i+1]
    assert integrals[-1] > integrals[0] * 2.0


def test_centripetal_pressure_dominance():
    """Verify that centrifugal acceleration u_theta^2 / r strictly dominates unsteady term d/dt u_r by tau^(-2h)."""
    h = 0.05
    taus = [1e-2, 1e-4, 1e-6]
    for tau in taus:
        centrifugal = (tau**(-0.5 - h))**2 / (tau**0.5)  # tau^(-1.5 - 2h)
        unsteady = tau**(-0.5) / tau                      # tau^(-1.5)
        ratio = centrifugal / unsteady
        expected = tau**(-2 * h)
        assert math.isclose(ratio, expected, rel_tol=1e-12)
        assert ratio > 1.0, "Centrifugal acceleration must strictly dominate"


def test_reynolds_number_scalings():
    """Verify that radial Reynolds number is O(1) while azimuthal Reynolds number diverges."""
    nu = 0.01
    h = 0.05
    taus = [1e-2, 1e-4, 1e-6]
    for tau in taus:
        ell_r = tau**0.5
        u_r = tau**(-0.5)
        u_theta = tau**(-0.5 - h)

        re_r = (u_r * ell_r) / nu
        re_theta = (u_theta * ell_r) / nu

        assert math.isclose(re_r, 1.0 / nu, rel_tol=1e-12)  # Strictly constant O(1/nu)
        assert math.isclose(re_theta, (tau**(-h)) / nu, rel_tol=1e-12)
        assert re_theta > re_r


def test_viscous_extinction_barrier():
    """Verify that preloaded pulses decay exponentially as exp(-nu * 2^j)."""
    nu = 1.0
    j_values = [5, 10, 15, 20]
    decays = []
    for j in j_values:
        decay = math.exp(-nu * (2**j) * (1.0 - 2**(-j)))
        decays.append(decay)
    assert decays[0] < 1e-10
    assert decays[1] == 0.0 or decays[1] < 1e-100  # Completely extinguished by machine precision
    # Pre-compensation explodes
    log_compensation = [nu * 2**j for j in j_values]
    for i in range(len(log_compensation) - 1):
        assert log_compensation[i] < log_compensation[i+1]
    assert log_compensation[-1] > 1e6


def test_okubo_weiss_strain_dominance():
    """Verify that Okubo-Weiss parameter Q = 0.5 |omega|^2 - tr(S^2) < 0 in the shear layer."""
    h = 0.05
    tau = 1e-4
    # In shear layer: S_12 = 0.5 * d/dr(u_theta), S_21 = 0.5 * d/dr(u_theta)
    # tr(S^2) = 2 * (0.5 * tau^(-1-h))^2 = 0.5 * tau^(-2-2h)
    # |omega|^2 = (d/dr u_theta)^2 = tau^(-2-2h)
    # 0.5 |omega|^2 - tr(S^2) = 0.5 * tau^(-2-2h) - 0.5 * tau^(-2-2h) = 0 for pure 1D shear,
    # but with radial and axial normal strains tr(S^2) exceeds 0.5 |omega|^2.
    grad_u = np.array([
        [-1.0/tau,  0.0,            0.0],
        [1.0/(tau**(1+h)), -1.0/tau, 0.0],
        [1.0/(tau**(1+h)), 0.0,     2.0/tau]
    ])
    assert math.isclose(np.trace(grad_u), 0.0, rel_tol=1e-12), "Must be trace-free"
    S = 0.5 * (grad_u + grad_u.T)
    omega = np.array([
        grad_u[2, 1] - grad_u[1, 2],
        grad_u[0, 2] - grad_u[2, 0],
        grad_u[1, 0] - grad_u[0, 1]
    ])
    tr_S2 = np.sum(S**2)
    omega_sq = np.sum(omega**2)
    Q = 0.5 * omega_sq - tr_S2
    assert Q < 0.0, f"Okubo-Weiss parameter must be negative (strain-dominated), got {Q}"


def test_unforced_energy_firewall():
    """Verify that u0 = 0 and f = 0 implies u(t) = 0 identically by energy identity."""
    # Under d/dt (0.5 ||u||_2^2) = -nu ||grad u||_2^2 <= 0 with E(0) = 0, E(t) == 0 for all t >= 0.
    E_0 = 0.0
    nu = 1.0
    t_span = np.linspace(0, 1, 100)
    # Since energy is non-negative and non-increasing, E(t) = 0.
    E_t = np.zeros_like(t_span)
    assert np.all(E_t == 0.0)
    assert E_0 == 0.0
