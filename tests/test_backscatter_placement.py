import numpy as np
import pytest

from backscatter_placement import (
    PlacementConfigError,
    PlacementConservationError,
    compute_t_return,
    verify_placement_conservation,
)


def _synthetic_shells():
    shells = np.arange(17, dtype=float)  # k = 0..16
    e_ref = np.where((shells > 0) & (shells <= 12), 1.0 / np.maximum(shells, 1.0), 0.0)
    ks, kc = 8.0, 12.0
    gamma_shell = np.zeros_like(shells)
    alpha_shell = np.zeros_like(shells)
    layer = (shells >= ks) & (shells <= kc)
    gamma_shell[layer] = 1.5
    alpha_shell[layer] = 0.6  # 60% heat, 40% return
    return shells, e_ref, gamma_shell, alpha_shell, ks


def test_local_cancellation_reinjects_at_same_shell():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    t_return = compute_t_return("local_cancellation", shells, e_ref, gamma_shell, alpha_shell, ks=ks)

    expected = (1.0 - alpha_shell) * gamma_shell * e_ref
    np.testing.assert_allclose(t_return, expected)


def test_parent_band_requires_c1_c2():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    with pytest.raises(PlacementConfigError):
        compute_t_return("parent_band_energy_weighted", shells, e_ref, gamma_shell, alpha_shell, ks=ks)


def test_parent_band_rejects_invalid_c1_c2_ordering():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    with pytest.raises(PlacementConfigError):
        compute_t_return(
            "parent_band_energy_weighted", shells, e_ref, gamma_shell, alpha_shell, ks=ks, c1=0.8, c2=0.3
        )


def test_parent_band_conserves_total_return_power():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    t_return = compute_t_return(
        "parent_band_energy_weighted", shells, e_ref, gamma_shell, alpha_shell, ks=ks, c1=0.3, c2=0.7
    )
    total_expected = float(((1.0 - alpha_shell) * gamma_shell * e_ref).sum())
    assert float(t_return.sum()) == pytest.approx(total_expected)

    kr1, kr2 = 0.3 * ks, 0.7 * ks
    outside = ~((shells >= kr1) & (shells <= kr2))
    assert np.all(t_return[outside] == 0.0)


def test_turnover_weighted_conserves_and_targets_below_ks():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    t_return = compute_t_return("turnover_weighted", shells, e_ref, gamma_shell, alpha_shell, ks=ks)

    total_expected = float(((1.0 - alpha_shell) * gamma_shell * e_ref).sum())
    assert float(t_return.sum()) == pytest.approx(total_expected)
    assert np.all(t_return[shells >= ks] == 0.0)
    assert np.all(t_return[shells == 0] == 0.0)


def test_dns_oracle_requires_t_dns():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    with pytest.raises(PlacementConfigError):
        compute_t_return("dns_oracle_diagnostic", shells, e_ref, gamma_shell, alpha_shell, ks=ks)


def test_dns_oracle_conserves_when_positive_transfer_exists_below_ks():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    t_dns = np.zeros_like(shells)
    t_dns[3] = 5.0
    t_dns[5] = 2.0
    t_dns[1] = -1.0  # negative shells should be excluded, not just clipped-then-included

    t_return = compute_t_return(
        "dns_oracle_diagnostic", shells, e_ref, gamma_shell, alpha_shell, ks=ks, t_dns=t_dns
    )
    total_expected = float(((1.0 - alpha_shell) * gamma_shell * e_ref).sum())
    assert float(t_return.sum()) == pytest.approx(total_expected)
    assert t_return[1] == 0.0
    assert t_return[3] > t_return[5] > 0.0  # proportional to the positive DNS transfer


def test_unknown_placement_raises():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    with pytest.raises(PlacementConfigError):
        compute_t_return("not_a_real_strategy", shells, e_ref, gamma_shell, alpha_shell, ks=ks)


def test_verify_placement_conservation_passes_for_local_cancellation():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    t_return = compute_t_return("local_cancellation", shells, e_ref, gamma_shell, alpha_shell, ks=ks)
    t_remove = -gamma_shell * e_ref

    report = verify_placement_conservation(t_return, t_remove, alpha_shell, gamma_shell, e_ref)
    assert report["passes"]
    assert abs(report["return_conservation_relative_residual"]) < 1e-9
    assert abs(report["model_conservation_relative_residual"]) < 1e-9


def test_verify_placement_conservation_raises_when_broken():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    t_remove = -gamma_shell * e_ref
    broken_t_return = np.zeros_like(e_ref)  # drops all returned power on the floor

    with pytest.raises(PlacementConservationError):
        verify_placement_conservation(broken_t_return, t_remove, alpha_shell, gamma_shell, e_ref)


def test_dns_oracle_conservation_fails_cleanly_when_no_positive_dns_transfer_below_ks():
    shells, e_ref, gamma_shell, alpha_shell, ks = _synthetic_shells()
    t_dns = -np.ones_like(shells)  # all negative -- oracle has nowhere to place energy
    t_return = compute_t_return(
        "dns_oracle_diagnostic", shells, e_ref, gamma_shell, alpha_shell, ks=ks, t_dns=t_dns
    )
    t_remove = -gamma_shell * e_ref

    with pytest.raises(PlacementConservationError):
        verify_placement_conservation(t_return, t_remove, alpha_shell, gamma_shell, e_ref)
