"""
JHTDB terminal-layer benchmark harness
======================================

Run this in a Johns Hopkins SciServer "Essentials 4.0" container with the
Turbulence data volume mounted and the `giverny` package available.

The only site-specific section is `fetch_velocity_cutout()`, because Giverny's
exact cutout-call signature can change between releases. Replace its body with
the current official DEMO notebook's velocity-cutout call. The rest of the
benchmark is independent of the retrieval API.

Expected velocity array shape: (nz, ny, nx, 3), periodic cube.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Config:
    dataset: str = "isotropic1024coarse"
    time: float = 0.0
    start_xyz: tuple[int, int, int] = (1, 1, 1)
    size_xyz: tuple[int, int, int] = (128, 128, 128)
    stride_xyz: tuple[int, int, int] = (1, 1, 1)
    domain_length: float = 2.0 * np.pi

    # Model parameters developed in our experiments
    beta: float = 0.56
    alpha_s: float = 0.70
    n_shape: int = 4
    m_shape: int = 3
    gp: float = 24.0
    gi: float = 8.0

    # Analysis cutoff as fraction of Nyquist.
    cutoff_fraction: float = 0.50

    output_dir: str = "jhtdb_terminal_benchmark"


def fetch_velocity_cutout(cfg: Config) -> np.ndarray:
    """
    Fetch one velocity cutout from JHTDB.

    Replace this body with the matching call copied from the current official
    SciServer Giverny demo notebook. It must return velocity in the shape
    (nz, ny, nx, 3).

    Typical information needed by the official call:
      dataset=cfg.dataset
      variable='velocity'
      time=cfg.time
      start=cfg.start_xyz
      size=cfg.size_xyz
      stride=cfg.stride_xyz
    """
    raise RuntimeError(
        "Insert the current official Giverny velocity-cutout call here. "
        "Do not replace JHTDB data with random or synthetic velocity."
    )


def as_component_first(velocity: np.ndarray) -> np.ndarray:
    velocity = np.asarray(velocity, dtype=np.float64)
    if velocity.ndim != 4 or velocity.shape[-1] != 3:
        raise ValueError(f"Expected (nz, ny, nx, 3), got {velocity.shape}")
    return np.moveaxis(velocity, -1, 0)


def wavenumbers(n: int, length: float):
    dx = length / n
    k = 2.0 * np.pi * np.fft.fftfreq(n, d=dx)
    return np.meshgrid(k, k, k, indexing="ij")


def project_divergence_free(uh: np.ndarray, kx, ky, kz) -> np.ndarray:
    k2 = kx * kx + ky * ky + kz * kz
    safe = np.where(k2 == 0.0, 1.0, k2)
    dot = kx * uh[0] + ky * uh[1] + kz * uh[2]
    out = uh.copy()
    out[0] -= kx * dot / safe
    out[1] -= ky * dot / safe
    out[2] -= kz * dot / safe
    out[:, k2 == 0.0] = 0.0
    return out


def kinetic_energy_hat(uh: np.ndarray) -> float:
    n3 = np.prod(uh.shape[1:])
    return float(0.5 * np.sum(np.abs(uh) ** 2) / (n3 * n3))


def shell_spectrum(uh: np.ndarray, kmag: np.ndarray):
    n3 = np.prod(uh.shape[1:])
    modal = 0.5 * np.sum(np.abs(uh) ** 2, axis=0) / (n3 * n3)
    kmax = int(np.floor(kmag.max()))
    shells = np.arange(kmax + 1)
    spectrum = np.zeros_like(shells, dtype=float)
    for shell in shells:
        mask = (kmag >= shell - 0.5) & (kmag < shell + 0.5)
        spectrum[shell] = modal[mask].sum()
    return shells, spectrum


def spectral_filter(uh: np.ndarray, kmag: np.ndarray, kc: float) -> np.ndarray:
    return uh * (kmag <= kc)


def terminal_operator(
    uh: np.ndarray,
    kmag: np.ndarray,
    kc: float,
    beta: float,
    alpha_s: float,
    n_shape: int,
    m_shape: int,
    c_gamma: float,
    tau_s: float,
):
    ks = beta * kc
    q = np.zeros_like(kmag)
    layer = (kmag >= ks) & (kmag <= kc)
    q[layer] = (kmag[layer] - ks) / (kc - ks)

    gamma = np.zeros_like(kmag)
    gamma[layer] = (c_gamma / tau_s) * q[layer] ** n_shape
    gamma[kmag > kc] = c_gamma / tau_s

    alpha = np.ones_like(kmag)
    alpha[layer] = alpha_s + (1.0 - alpha_s) * q[layer] ** m_shape

    n3 = np.prod(uh.shape[1:])
    twice_modal_energy = np.sum(np.abs(uh) ** 2, axis=0) / (n3 * n3)
    removed_density = gamma * twice_modal_energy

    return {
        "gamma": gamma,
        "alpha": alpha,
        "terminal_power": float(removed_density.sum()),
        "heat_power": float((alpha * removed_density).sum()),
        "return_power": float(((1.0 - alpha) * removed_density).sum()),
    }


def vorticity_statistics(uh: np.ndarray, kx, ky, kz) -> dict[str, float]:
    wxh = 1j * (ky * uh[2] - kz * uh[1])
    wyh = 1j * (kz * uh[0] - kx * uh[2])
    wzh = 1j * (kx * uh[1] - ky * uh[0])
    omega = np.stack(
        [
            np.fft.ifftn(wxh).real,
            np.fft.ifftn(wyh).real,
            np.fft.ifftn(wzh).real,
        ]
    )
    mag = np.sqrt(np.sum(omega * omega, axis=0))
    return {
        "enstrophy": float(0.5 * np.mean(mag * mag)),
        "omega_mean": float(np.mean(mag)),
        "omega_rms": float(np.sqrt(np.mean(mag * mag))),
        "omega_p95": float(np.quantile(mag, 0.95)),
        "omega_p99": float(np.quantile(mag, 0.99)),
        "omega_max": float(np.max(mag)),
    }


def spectral_relative_l2(reference: np.ndarray, model: np.ndarray, mask: np.ndarray) -> float:
    denominator = np.sum(reference[mask] ** 2)
    if denominator <= 0:
        return float("nan")
    return float(np.sqrt(np.sum((model[mask] - reference[mask]) ** 2) / denominator))


def main() -> None:
    cfg = Config()
    output = Path(cfg.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    velocity = fetch_velocity_cutout(cfg)
    u = as_component_first(velocity)

    nz, ny, nx = u.shape[1:]
    if not (nx == ny == nz):
        raise ValueError("This first benchmark requires a cubic cutout.")

    kx, ky, kz = wavenumbers(nx, cfg.domain_length)
    kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
    uh_dns = np.fft.fftn(u, axes=(1, 2, 3))
    uh_dns = project_divergence_free(uh_dns, kx, ky, kz)

    nyquist = float(np.max(np.abs(kx[:, 0, 0])))
    kc = cfg.cutoff_fraction * nyquist
    ks = cfg.beta * kc

    # Reference resolved field: DNS filtered at the same cutoff.
    uh_ref = spectral_filter(uh_dns, kmag, kc)

    # Hard cutoff comparator.
    uh_hard = uh_ref.copy()

    # Terminal-layer a-priori transformation over one local turnover time.
    entry = (kmag >= ks - 0.5) & (kmag < ks + 0.5)
    k_entry = kinetic_energy_hat(uh_ref * entry)
    u_s = np.sqrt(max(2.0 * k_entry, 1e-14))
    ell_s = 2.0 * np.pi / ks
    tau_s = ell_s / max(u_s, 1e-12)

    # First a-priori test uses a neutral dimensionless strength. The forward
    # simulation should evolve C_gamma with the GP/GI controller.
    c_gamma = 1.0
    operator = terminal_operator(
        uh_ref,
        kmag,
        kc,
        cfg.beta,
        cfg.alpha_s,
        cfg.n_shape,
        cfg.m_shape,
        c_gamma,
        tau_s,
    )

    uh_terminal = uh_ref * np.exp(-operator["gamma"] * tau_s)

    shells, e_dns = shell_spectrum(uh_dns, kmag)
    _, e_ref = shell_spectrum(uh_ref, kmag)
    _, e_hard = shell_spectrum(uh_hard, kmag)
    _, e_terminal = shell_spectrum(uh_terminal, kmag)

    permitted = (shells > 0) & (shells <= kc)
    terminal_region = (shells >= ks) & (shells <= kc)

    metrics = {
        "grid_n": nx,
        "kc": kc,
        "ks": ks,
        "beta": cfg.beta,
        "tau_s": tau_s,
        "dns_kinetic": kinetic_energy_hat(uh_dns),
        "filtered_dns_kinetic": kinetic_energy_hat(uh_ref),
        "terminal_kinetic": kinetic_energy_hat(uh_terminal),
        "spectrum_relative_l2_permitted": spectral_relative_l2(
            e_ref, e_terminal, permitted
        ),
        "spectrum_relative_l2_terminal_region": spectral_relative_l2(
            e_ref, e_terminal, terminal_region
        ),
        "terminal_power": operator["terminal_power"],
        "terminal_heat_power": operator["heat_power"],
        "terminal_return_power": operator["return_power"],
        "predicted_return_fraction": operator["return_power"]
        / max(operator["terminal_power"], 1e-30),
        "energy_above_cutoff_dns": float(e_dns[shells > kc].sum()),
        "energy_above_cutoff_filtered": float(e_ref[shells > kc].sum()),
        "energy_above_cutoff_terminal": float(e_terminal[shells > kc].sum()),
    }
    metrics.update({f"dns_{k}": v for k, v in vorticity_statistics(uh_dns, kx, ky, kz).items()})
    metrics.update({f"filtered_{k}": v for k, v in vorticity_statistics(uh_ref, kx, ky, kz).items()})
    metrics.update({f"terminal_{k}": v for k, v in vorticity_statistics(uh_terminal, kx, ky, kz).items()})

    pd.DataFrame([metrics]).to_csv(output / "apriori_metrics.csv", index=False)
    pd.DataFrame(
        {
            "k": shells,
            "dns": e_dns,
            "filtered_dns": e_ref,
            "hard_cutoff": e_hard,
            "terminal_layer": e_terminal,
        }
    ).to_csv(output / "spectra.csv", index=False)

    plt.figure(figsize=(8, 5))
    valid = shells > 0
    plt.semilogy(shells[valid], e_dns[valid] + 1e-30, label="DNS")
    plt.semilogy(shells[valid], e_ref[valid] + 1e-30, label="Filtered DNS")
    plt.semilogy(shells[valid], e_terminal[valid] + 1e-30, label="Terminal operator")
    plt.axvline(ks, linestyle=":", label="terminal start")
    plt.axvline(kc, linestyle="--", label="cutoff")
    plt.xlabel("Wavenumber")
    plt.ylabel("E(k)")
    plt.title("JHTDB a-priori spectral comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "spectral_comparison.png", dpi=180)
    plt.close()

    print(pd.DataFrame([metrics]).T.to_string(header=False))


if __name__ == "__main__":
    main()
