"""Shared DNS/filtered-field spectral setup, used by every comparison
script so the FFT -> divergence-free projection -> spectral filter ->
shell-energy pipeline is computed identically everywhere."""

from __future__ import annotations

import numpy as np

from jhtdb_terminal_benchmark import (
    Config,
    as_component_first,
    project_divergence_free,
    shell_spectrum,
    spectral_filter,
    wavenumbers,
)


def dns_and_filtered_shells(velocity: np.ndarray, cfg: Config, kc: float | None = None):
    """Returns (uh_dns, uh_ref, kx, ky, kz, kmag, shells, e_dns, e_ref, kc, nyquist)."""
    u = as_component_first(velocity)
    nz, ny, nx = u.shape[1:]
    if not (nx == ny == nz):
        raise ValueError("This benchmark requires a cubic cutout.")
    kx, ky, kz = wavenumbers(nx, cfg.domain_length)
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    uh_dns = np.fft.fftn(u, axes=(1, 2, 3))
    uh_dns = project_divergence_free(uh_dns, kx, ky, kz)
    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    if kc is None:
        kc = cfg.cutoff_fraction * nyquist
    uh_ref = spectral_filter(uh_dns, kmag, kc)
    shells, e_dns = shell_spectrum(uh_dns, kmag)
    _, e_ref = shell_spectrum(uh_ref, kmag)
    return uh_dns, uh_ref, kx, ky, kz, kmag, shells, e_dns, e_ref, kc, nyquist
