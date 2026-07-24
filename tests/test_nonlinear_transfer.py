import numpy as np
import pytest

from jhtdb_terminal_benchmark import project_divergence_free, wavenumbers
from nonlinear_transfer import (
    divergence_hat,
    modal_transfer,
    shell_transfer,
    spectral_flux,
    verify_global_conservation,
)


def _index_of(k1d: np.ndarray, value: int) -> int:
    idx = np.nonzero(k1d == value)[0]
    assert idx.size == 1
    return int(idx[0])


def test_single_mode_pair_has_zero_transfer_everywhere():
    # A single Fourier mode pair (+-k0) has no self-transfer: the only sums
    # of two vectors from {k0, -k0} are 2*k0, 0, and -2*k0, none of which
    # equal k0 itself. Since T(k) = Re[conj(u_hat(k)) . N_hat_perp(k)] and
    # u_hat is zero everywhere except at +-k0, T(k) must be exactly zero
    # everywhere: the harmonics N_hat generates land on modes u_hat doesn't
    # occupy, so their dot product vanishes by construction, not by
    # cancellation.
    n, length = 16, 2.0 * np.pi
    kx, ky, kz = wavenumbers(n, length)
    k1d = kx[:, 0, 0]

    pos = (_index_of(k1d, 1), _index_of(k1d, 1), _index_of(k1d, 0))
    neg = (_index_of(k1d, -1), _index_of(k1d, -1), _index_of(k1d, 0))

    uh = np.zeros((3, n, n, n), dtype=complex)
    amplitude = np.array([1.0, -1.0, 0.0])  # perpendicular to k0=(1,1,0)
    uh[(slice(None),) + pos] = amplitude
    uh[(slice(None),) + neg] = amplitude  # real amplitude -> self-conjugate

    t_modal, _, _ = modal_transfer(uh, kx, ky, kz)

    assert np.max(np.abs(t_modal)) < 1e-10
    conservation = verify_global_conservation(t_modal)
    assert conservation["relative_residual"] == 0.0


def test_taylor_green_vortex_is_divergence_free_with_zero_transfer_at_t0():
    # The classic TG3D initial condition populates only odd-integer
    # wavevectors (+-1,+-1,+-1)-type. Any sum of two such vectors has
    # even-integer components (1+1=2, 1-1=0, -1-1=-2), so -- by the same
    # support argument as the single-mode-pair case above -- the nonlinear
    # term's harmonics never land back on the populated (odd) modes, and
    # the instantaneous transfer at every populated mode is exactly zero.
    n, length = 32, 2.0 * np.pi
    kx, ky, kz = wavenumbers(n, length)
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)

    coords = np.linspace(0.0, length, n, endpoint=False)
    x, y, z = np.meshgrid(coords, coords, coords, indexing="ij")
    u = np.stack(
        [
            np.cos(x) * np.sin(y) * np.sin(z),
            -np.sin(x) * np.cos(y) * np.sin(z),
            np.zeros_like(x),
        ]
    )
    uh = np.fft.fftn(u, axes=(1, 2, 3))
    uh = project_divergence_free(uh, kx, ky, kz)

    div = divergence_hat(uh, kx, ky, kz)
    assert np.max(np.abs(div)) < 1e-8

    t_modal, _, _ = modal_transfer(uh, kx, ky, kz)
    assert np.max(np.abs(t_modal)) < 1e-8
    conservation = verify_global_conservation(t_modal)
    assert conservation["relative_residual"] == 0.0

    shells, t_shell = shell_transfer(t_modal, kmag)
    pi = spectral_flux(t_shell)
    assert pi.shape == shells.shape


def test_resonant_triad_transfers_energy_and_conserves_it():
    # A minimal resonant triad k1+k2+k3=0, all three populated, DOES
    # produce genuine nonzero transfer among modes (unlike the two tests
    # above): (-k2)+(-k3)=k1 lands back on a populated mode, and likewise
    # for the other two pairings. This checks conservation on a case where
    # the transfer is not trivially zero.
    #
    # Amplitudes need a relative phase between the three modes: purely real
    # (in-phase) amplitudes are a degenerate special case (like a standing
    # wave) that forces Re[conj(u_hat).N_hat_perp] = 0 exactly at every
    # mode, same as the trivial cases above, even though N_hat_perp itself
    # is nonzero there. The `scale` factor just keeps the resulting
    # transfer well above floating-point noise for a small 16^3 test grid
    # (u_hat amplitude 1 corresponds to a real-space velocity of order
    # 1/n3, so transfer -- being higher order in velocity -- needs scaling
    # up to be numerically distinguishable from the exact-zero cases).
    n, length = 16, 2.0 * np.pi
    kx, ky, kz = wavenumbers(n, length)
    k1d = kx[:, 0, 0]

    def idx(vec):
        return tuple(_index_of(k1d, v) for v in vec)

    k1, k2, k3 = (1, 0, 0), (0, 1, 0), (-1, -1, 0)
    directions = {
        k1: np.array([0.0, 1.0, 0.0]),
        k2: np.array([1.0, 0.0, 0.0]),
        k3: np.array([1.0, -1.0, 0.0]),
    }
    phases = {k1: np.exp(1j * 0.3), k2: np.exp(1j * 1.1), k3: np.exp(1j * 2.0)}
    scale = 200.0

    uh = np.zeros((3, n, n, n), dtype=complex)
    for k, d in directions.items():
        amplitude = scale * phases[k] * d
        uh[(slice(None),) + idx(k)] = amplitude
        neg = tuple(-c for c in k)
        uh[(slice(None),) + idx(neg)] = np.conj(amplitude)

    t_modal, _, _ = modal_transfer(uh, kx, ky, kz)

    assert np.max(np.abs(t_modal)) > 1e-6  # genuine (non-trivial) transfer occurs
    conservation = verify_global_conservation(t_modal)
    assert conservation["relative_residual"] < 1e-8


def test_dealiasing_reduces_conservation_residual_for_broadband_field():
    n, length = 32, 2.0 * np.pi
    kx, ky, kz = wavenumbers(n, length)
    nyquist = float(np.max(np.abs(kx[:, 0, 0])))

    rng = np.random.default_rng(0)
    u = rng.normal(size=(3, n, n, n))
    uh = np.fft.fftn(u, axes=(1, 2, 3))
    uh = project_divergence_free(uh, kx, ky, kz)

    t_raw, _, _ = modal_transfer(uh, kx, ky, kz, dealias=False)
    t_dealiased, _, _ = modal_transfer(uh, kx, ky, kz, dealias=True, nyquist=nyquist)

    residual_raw = verify_global_conservation(t_raw)["relative_residual"]
    residual_dealiased = verify_global_conservation(t_dealiased)["relative_residual"]

    assert residual_dealiased < 1e-8
    assert residual_dealiased <= residual_raw + 1e-12


def test_spectral_flux_sign_convention():
    t_shell = np.array([1.0, -1.0, 2.0, -2.0])
    pi = spectral_flux(t_shell)
    assert pi == pytest.approx([-1.0, 0.0, -2.0, 0.0])
