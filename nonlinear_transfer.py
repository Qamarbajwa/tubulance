"""
Nonlinear spectral transfer (pseudospectral)
=============================================

Milestone 3 of the JHTDB terminal-layer validation project: the true,
instantaneous nonlinear energy transfer T(k) and cumulative spectral flux
Pi(k), computed directly from a single DNS snapshot's velocity field --
unlike the two-snapshot finite-difference diagnostics in measure_transfer.py
and compare_model_to_dns.py, this does NOT require a confirmed Delta-t.

Definitions and sign convention
--------------------------------

For incompressible velocity u, the (projected, dealiased-optional) nonlinear
term is

    N(x) = -(u . grad) u

Its Fourier transform is projected onto the divergence-free subspace (this
also removes the pressure-gradient contribution, since pressure enforces
incompressibility by cancelling exactly the compressible part of the
advective term):

    N_hat_perp(k) = (I - k k^T / |k|^2) N_hat(k)

The modal nonlinear transfer is

    T(k_vec) = Re[ conj(u_hat(k_vec)) . N_hat_perp(k_vec) ]  /  n3^2

using the same n3 = nx*ny*nz normalization as kinetic_energy_hat() and
shell_spectrum() in jhtdb_terminal_benchmark.py, so that in the absence of
forcing and viscosity, d/dt(shell kinetic energy) == shell_transfer(T(k)).

Shell-aggregated transfer:

    T(k) = sum over modes with |k_vec| in shell k of T(k_vec)

Cumulative spectral flux (energy flux THROUGH wavenumber k, from scales
<= k to scales > k; positive means a forward/direct cascade):

    Pi(k) = -sum_{p <= k} T(p)

Global conservation: for a closed (unforced, inviscid) incompressible
system the nonlinear term conserves total kinetic energy exactly, so
sum_k T(k) == 0 in the continuum. Discretely this holds only up to aliasing
error from the pseudospectral product; verify_global_conservation() reports
the residual so callers can judge whether that error is small enough to
trust the rest of the calculation. Dealiasing (2/3-rule truncation of the
fields entering the product, dealias=True) reduces this residual by
removing the aliased triads rather than by cancellation, so it should not
be treated as "cheating" -- it improves fidelity to the continuum property.
"""

from __future__ import annotations

import numpy as np

from jhtdb_terminal_benchmark import bin_shells, project_divergence_free


def dealias_mask(kx: np.ndarray, ky: np.ndarray, kz: np.ndarray, nyquist: float) -> np.ndarray:
    """Standard 2/3-rule truncation mask, applied per-axis (not by |k|)."""
    cutoff = (2.0 / 3.0) * nyquist
    return (np.abs(kx) <= cutoff) & (np.abs(ky) <= cutoff) & (np.abs(kz) <= cutoff)


def velocity_gradient_real(uh: np.ndarray, kx: np.ndarray, ky: np.ndarray, kz: np.ndarray) -> np.ndarray:
    """grad[i, j] = d(u_i)/dx_j, in real space. Shape (3, 3, nz, ny, nx)."""
    k = (kx, ky, kz)
    grad = np.zeros((3, 3) + uh.shape[1:], dtype=np.float64)
    for i in range(3):
        for j in range(3):
            grad[i, j] = np.fft.ifftn(1j * k[j] * uh[i]).real
    return grad


def nonlinear_term_hat(
    uh: np.ndarray, kx: np.ndarray, ky: np.ndarray, kz: np.ndarray
) -> np.ndarray:
    """Unprojected N_hat = FFT[-(u . grad) u], computed pseudospectrally from
    the (possibly already-dealiased) uh passed in."""
    u = np.fft.ifftn(uh, axes=(1, 2, 3)).real
    grad = velocity_gradient_real(uh, kx, ky, kz)
    advective = np.einsum("j...,ij...->i...", u, grad)
    n = -advective
    return np.fft.fftn(n, axes=(1, 2, 3))


def modal_transfer(
    uh: np.ndarray,
    kx: np.ndarray,
    ky: np.ndarray,
    kz: np.ndarray,
    *,
    dealias: bool = False,
    nyquist: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute the modal nonlinear transfer T(k_vec).

    Returns (T_modal, Nh_perp, uh_work) where uh_work is the (possibly
    dealiased) velocity actually used -- callers computing shell energies
    to compare against T(k) should use the same uh_work for consistency.
    """
    if dealias:
        if nyquist is None:
            nyquist = float(np.max(np.abs(kx[:, 0, 0])))
        mask = dealias_mask(kx, ky, kz, nyquist)
        uh_work = uh * mask
    else:
        uh_work = uh

    nh = nonlinear_term_hat(uh_work, kx, ky, kz)
    nh_perp = project_divergence_free(nh, kx, ky, kz)
    if dealias:
        nh_perp = nh_perp * mask

    n3 = np.prod(uh_work.shape[1:])
    t_modal = np.real(np.sum(np.conj(uh_work) * nh_perp, axis=0)) / (n3 * n3)
    return t_modal, nh_perp, uh_work


def shell_transfer(t_modal: np.ndarray, kmag: np.ndarray):
    """Bin modal transfer into integer wavenumber shells: T(k)."""
    return bin_shells(t_modal, kmag)


def spectral_flux(t_shell: np.ndarray) -> np.ndarray:
    """Pi(k) = -sum_{p<=k} T(p), the cumulative energy flux through k."""
    return -np.cumsum(t_shell)


def verify_global_conservation(t_modal: np.ndarray, scale_floor: float = 1e-12) -> dict:
    """Relative residual of sum_k T(k) against the typical transfer
    magnitude. A small residual supports (does not prove) that aliasing
    error is under control; a large one means the transfer calculation
    should not be trusted for this field/resolution/dealias setting.

    Some fields (e.g. a single Fourier mode, or the Taylor-Green vortex at
    t=0) have exactly zero transfer at every populated mode by a parity/
    support argument -- both the total and the per-mode magnitudes are then
    floating-point noise, and their ratio is meaningless. Below
    `scale_floor` the field is treated as trivially conserved (residual 0)
    rather than reporting a noisy or NaN ratio.
    """
    total = float(np.sum(t_modal))
    scale = float(np.sum(np.abs(t_modal)))
    relative_residual = abs(total) / scale if scale > scale_floor else 0.0
    return {
        "total_transfer": total,
        "sum_abs_transfer": scale,
        "relative_residual": relative_residual,
    }


def divergence_hat(uh: np.ndarray, kx: np.ndarray, ky: np.ndarray, kz: np.ndarray) -> np.ndarray:
    """i*(kx*uh_x + ky*uh_y + kz*uh_z); should be ~0 for a divergence-free field."""
    return 1j * (kx * uh[0] + ky * uh[1] + kz * uh[2])
