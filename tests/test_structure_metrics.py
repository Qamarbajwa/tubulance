import numpy as np
import pytest

from structure_metrics import (
    anisotropy_tensor, anisotropy_invariants, directional_spectrum, directional_anisotropy_ratio,
    strain_statistics, detect_structures,
)
from jhtdb_terminal_benchmark import wavenumbers, project_divergence_free


def test_anisotropy_tensor_isotropic_field_is_near_zero():
    rng = np.random.default_rng(0)
    # equal-variance independent components approximate isotropic Reynolds stress
    u = rng.normal(size=(3, 24, 24, 24))
    b = anisotropy_tensor(u)
    assert np.abs(b).max() < 0.05  # small for a large enough isotropic sample


def test_anisotropy_tensor_directional_field_is_anisotropic():
    u = np.zeros((3, 8, 8, 8))
    u[0] = 5.0  # all energy in x-component
    b = anisotropy_tensor(u)
    inv = anisotropy_invariants(b)
    assert inv["anisotropy_magnitude"] > 0.3
    # b_xx should be the dominant (positive) component: 1 - 1/3 = 2/3
    assert b[0, 0] == pytest.approx(2.0 / 3.0)


def test_anisotropy_tensor_zero_field_returns_zero():
    u = np.zeros((3, 4, 4, 4))
    b = anisotropy_tensor(u)
    np.testing.assert_allclose(b, np.zeros((3, 3)))


def test_directional_spectrum_concentrates_along_forced_direction():
    n = 16
    kx, ky, kz = wavenumbers(n, 2 * np.pi)
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    # put all energy in modes aligned with the x-axis (ky=kz=0)
    raw = np.zeros((3, n, n, n), dtype=complex)
    mask = (np.abs(ky) < 1e-9) & (np.abs(kz) < 1e-9) & (kmag > 0)
    raw[1][mask] = 1.0  # y-component velocity, k along x -- divergence-free
    uh = project_divergence_free(raw, kx, ky, kz)
    centers, energy = directional_spectrum(uh, kmag, kx, ky, kz, direction=(1, 0, 0), n_bins=8)
    ratio = directional_anisotropy_ratio(centers, energy)
    assert ratio > 1.5  # concentrated, not spread evenly across angle bins


def test_strain_statistics_zero_for_uniform_field():
    n = 8
    kx, ky, kz = wavenumbers(n, 2 * np.pi)
    uh = np.zeros((3, n, n, n), dtype=complex)
    stats = strain_statistics(uh, kx, ky, kz)
    assert stats["strain_rms"] == pytest.approx(0.0, abs=1e-10)


def test_detect_structures_on_synthetic_blob():
    field = np.zeros((16, 16, 16))
    field[4:8, 4:8, 4:8] = 10.0
    pop = detect_structures(field, threshold_fraction=0.5)
    assert pop.n_structures == 1
    assert pop.sizes[0] == 4 * 4 * 4
    assert pop.intensities[0] == pytest.approx(10.0)


def test_detect_structures_empty_field():
    field = np.zeros((8, 8, 8))
    pop = detect_structures(field)
    assert pop.n_structures == 0
