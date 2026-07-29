import numpy as np
import pytest

from jhtdb_terminal_benchmark import wavenumbers, project_divergence_free
from terminal_operator_forcing_aware import (
    gamma_baseline, gamma_candidate_forcing_aware, TerminalEnergySplit, IS_CANDIDATE_MODEL,
)


def _synthetic_uh(n=16, seed=0):
    rng = np.random.default_rng(seed)
    kx, ky, kz = wavenumbers(n, 2 * np.pi)
    raw = rng.normal(size=(3, n, n, n)) + 1j * rng.normal(size=(3, n, n, n))
    return project_divergence_free(raw, kx, ky, kz), kx, ky, kz


def test_candidate_is_marked_explicitly():
    assert IS_CANDIDATE_MODEL is True


def test_h1_weak_forcing_consistency_candidate_reduces_to_baseline():
    """H1: as Phi_l -> 0, the candidate model must reduce EXACTLY to the
    original (unmodified) terminal operator."""
    uh, kx, ky, kz = _synthetic_uh()
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s = 4.0, 0.5, 0.7, 4, 3, 1.0, 1.0

    base = gamma_baseline(uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s)
    cand_zero = gamma_candidate_forcing_aware(
        uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s, phi_l=0.0, theta_f=1.0
    )
    np.testing.assert_allclose(cand_zero["gamma"], base["gamma"])
    assert cand_zero["terminal_power"] == pytest.approx(base["terminal_power"])


def test_candidate_diverges_from_baseline_for_strong_forcing():
    uh, kx, ky, kz = _synthetic_uh()
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s = 4.0, 0.5, 0.7, 4, 3, 1.0, 1.0

    base = gamma_baseline(uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s)
    cand_strong = gamma_candidate_forcing_aware(
        uh, kmag, kc, beta, alpha_s, n_shape, m_shape, c_gamma, tau_s, phi_l=1000.0, theta_f=10.0
    )
    assert not np.allclose(cand_strong["gamma"], base["gamma"])
    assert cand_strong["candidate_model"] is True


def test_candidate_correction_is_bounded():
    uh, kx, ky, kz = _synthetic_uh()
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    cand = gamma_candidate_forcing_aware(
        uh, kmag, 4.0, 0.5, 0.7, 4, 3, 1.0, 1.0, phi_l=1e12, theta_f=1e12, kappa=0.5
    )
    # correction = 1 + kappa*tanh(...)*f(theta_f), bounded by 1+kappa since tanh<1, f<1
    assert cand["correction_applied"] <= 1.5 + 1e-9


def test_terminal_energy_split_extra_channels_default_zero():
    split = TerminalEnergySplit.from_incompressible_newtonian(heat_power=2.0, return_power=1.0)
    assert split.e_wave == 0.0
    assert split.e_compressive == 0.0
    assert split.e_surface == 0.0
    assert split.e_internal == 0.0
    assert split.e_terminal == pytest.approx(3.0)
