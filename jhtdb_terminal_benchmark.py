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

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class InsufficientResolutionError(RuntimeError):
    """Raised when the terminal layer cannot be resolved with enough independent shells."""


class SnapshotSeparationError(RuntimeError):
    """Raised when a snapshot appears in both calibration and validation sets."""


@dataclass(frozen=True)
class Config:
    dataset: str = "isotropic1024coarse"
    time: float = 0.0
    start_xyz: tuple[int, int, int] = (1, 1, 1)
    size_xyz: tuple[int, int, int] = (128, 128, 128)
    stride_xyz: tuple[int, int, int] = (1, 1, 1)
    domain_length: float = 2.0 * np.pi

    # Local cache of a real JHTDB HDF5 cutout (exported via the JHTDB web
    # cutout service). When set, fetch_velocity_cutout() reads from this file
    # instead of requiring a live SciServer/Giverny session.
    local_h5_path: str | None = None
    local_h5_timestep: int = 1

    # Model parameters developed in our experiments. `beta` is a *preferred*
    # dimensionless target for ks/kc, not a fixed rule -- see
    # compute_terminal_layer(). The layer's actual width is resolution-aware.
    beta: float = 0.56
    alpha_s: float = 0.70
    n_shape: int = 4
    m_shape: int = 3
    gp: float = 24.0
    gi: float = 8.0

    # Analysis cutoff as fraction of Nyquist.
    cutoff_fraction: float = 0.50

    # Where backscattered ("return") energy is spectrally reinjected. The
    # terminal operator (terminal_operator()) only specifies a per-mode
    # heat/return SPLIT (alpha) of the total removal (gamma*E) -- it does
    # not specify a target shell for the returned portion. Preregistered
    # candidate strategies (see backscatter_placement.py):
    #   "local_cancellation"          -- reinjects at the same shell (the
    #                                    only placement consistent with
    #                                    "no information"; net transfer
    #                                    reduces to heat only -- reduced
    #                                    effective damping, not a modeled
    #                                    inverse cascade).
    #   "parent_band_energy_weighted" -- reinjects into [c1*ks, c2*ks],
    #                                    weighted by existing energy.
    #                                    Requires parent_band_c1/c2.
    #   "turnover_weighted"           -- reinjects below ks weighted by
    #                                    E(k)/tau(k).
    #   "dns_oracle_diagnostic"       -- reinjects proportional to real
    #                                    DNS positive transfer below ks.
    #                                    DIAGNOSTIC ONLY, never a
    #                                    deployable model -- see AGENTS.md.
    backscatter_placement: str = "local_cancellation"
    # Required only for "parent_band_energy_weighted"; preregister these
    # (set once, before running against real data) rather than tuning
    # after seeing results -- see backscatter_placement.py.
    parent_band_c1: float | None = None
    parent_band_c2: float | None = None

    # --- Resolution-aware terminal-layer requirements --------------------
    # N_T = (kc - ks) / delta_k must be at least min_terminal_shells for the
    # physical benchmark to be meaningful; preferred_terminal_shells is used
    # whenever the configured `beta` would produce too narrow a layer.
    min_terminal_shells: int = 6
    preferred_terminal_shells: int = 8
    # Of the shells inside [ks, kc], at least this many must contain
    # measurable DNS energy (> energy_floor), or heat/backscatter behavior
    # cannot be distinguished from plain filtering.
    min_populated_terminal_shells: int = 4
    energy_floor: float = 1e-20
    # Cutoff must stay comfortably below Nyquist to avoid aliasing artifacts
    # contaminating the terminal layer.
    max_cutoff_fraction_of_nyquist: float = 0.8

    # Forcing-range scale separation. isotropic1024coarse's forcing
    # wavenumber range is intentionally NOT hardcoded here -- it has not
    # been confirmed against official JHTDB documentation in this project.
    # Set explicitly (e.g. forcing_kmax=2.0) once confirmed to enable this
    # check; left as None it is skipped and recorded as unchecked rather
    # than silently assumed to pass.
    forcing_kmax: float | None = None
    min_forcing_terminal_gap_shells: float = 2.0

    # Calibration vs validation snapshot bookkeeping: (dataset, time) pairs.
    # A snapshot must never appear in both -- constants tuned against a
    # snapshot cannot also be reported as an independent validation of that
    # same snapshot.
    calibration_snapshots: tuple[tuple[str, float], ...] = ()
    validation_snapshots: tuple[tuple[str, float], ...] = ()

    output_dir: str = "jhtdb_terminal_benchmark"


def assert_snapshot_separation(cfg: Config) -> None:
    overlap = set(cfg.calibration_snapshots) & set(cfg.validation_snapshots)
    if overlap:
        raise SnapshotSeparationError(
            f"Snapshot(s) {sorted(overlap)} appear in both calibration_snapshots "
            "and validation_snapshots. Model constants tuned on a snapshot must "
            "not later be reported as validated against that same snapshot."
        )


@dataclass(frozen=True)
class TerminalLayer:
    kc: float
    ks: float
    delta_k: float
    n_t: float
    beta_effective: float
    source: str  # "beta" or "resolution_derived"


def compute_terminal_layer(kc: float, delta_k: float, cfg: Config) -> TerminalLayer:
    """Derive the terminal layer [ks, kc], preferring the configured `beta`
    but overriding it whenever that would produce fewer than
    `min_terminal_shells` independent shells. Two runs can share the same
    beta while representing the layer with radically different numbers of
    modes, so beta alone is not a sufficient spec -- N_T is reported too.
    """
    ks_from_beta = cfg.beta * kc
    n_t_from_beta = (kc - ks_from_beta) / delta_k
    if n_t_from_beta >= cfg.min_terminal_shells:
        ks = ks_from_beta
        source = "beta"
    else:
        ks = kc - cfg.preferred_terminal_shells * delta_k
        source = "resolution_derived"
    # Clamp: ks below 0 would mean "more terminal shells than exist between
    # the origin and kc" -- not a valid layer. Recompute n_t from the
    # clamped ks so validate_terminal_layer's shell-count check actually
    # catches this case instead of trusting the unclamped target width.
    ks = max(ks, 0.0)
    n_t = (kc - ks) / delta_k
    beta_effective = ks / kc if kc > 0 else float("nan")
    return TerminalLayer(
        kc=kc, ks=ks, delta_k=delta_k, n_t=n_t, beta_effective=beta_effective, source=source
    )


def validate_terminal_layer(
    layer: TerminalLayer, nyquist: float, shells: np.ndarray, e_dns: np.ndarray, cfg: Config
) -> list[str]:
    """Return human-readable blocking reasons; an empty list means the
    physical benchmark (not just the pipeline) may proceed."""
    failures: list[str] = []

    if layer.n_t < cfg.min_terminal_shells:
        failures.append(
            f"terminal layer spans N_T={layer.n_t:.2f} shells, below the "
            f"required minimum of {cfg.min_terminal_shells}"
        )

    terminal_region = (shells >= layer.ks) & (shells <= layer.kc)
    populated = int(np.sum(e_dns[terminal_region] > cfg.energy_floor))
    if populated < cfg.min_populated_terminal_shells:
        failures.append(
            f"only {populated} terminal shells contain measurable DNS energy "
            f"(> {cfg.energy_floor:g}), below the required minimum of "
            f"{cfg.min_populated_terminal_shells}"
        )

    if layer.kc > cfg.max_cutoff_fraction_of_nyquist * nyquist:
        failures.append(
            f"cutoff kc={layer.kc:.3f} exceeds "
            f"{cfg.max_cutoff_fraction_of_nyquist:.0%} of Nyquist "
            f"({nyquist:.3f}); too close to the aliasing limit"
        )

    if cfg.forcing_kmax is not None:
        gap = layer.ks - cfg.forcing_kmax
        min_gap = cfg.min_forcing_terminal_gap_shells * layer.delta_k
        if gap < min_gap:
            failures.append(
                f"insufficient scale separation between forcing range "
                f"(kmax={cfg.forcing_kmax:.3f}) and terminal layer start "
                f"(ks={layer.ks:.3f}): gap {gap:.3f} < required {min_gap:.3f}"
            )

    return failures


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
    if cfg.local_h5_path is not None:
        with h5py.File(cfg.local_h5_path, "r") as f:
            key = f"Velocity_{cfg.local_h5_timestep:04d}"
            if key not in f:
                available = [k for k in f.keys() if k.startswith("Velocity_")]
                raise KeyError(f"{key} not found in {cfg.local_h5_path}; available: {available}")
            return np.asarray(f[key])

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


def bin_shells(values: np.ndarray, kmag: np.ndarray):
    """Sum an arbitrary per-mode scalar field into integer wavenumber shells.
    Shared by shell_spectrum() (energy density) and nonlinear_transfer.py
    (transfer density) so both use identical binning.
    """
    kmax = int(np.floor(kmag.max()))
    shells = np.arange(kmax + 1)
    binned = np.zeros_like(shells, dtype=float)
    for shell in shells:
        mask = (kmag >= shell - 0.5) & (kmag < shell + 0.5)
        binned[shell] = values[mask].sum()
    return shells, binned


def shell_spectrum(uh: np.ndarray, kmag: np.ndarray):
    n3 = np.prod(uh.shape[1:])
    modal = 0.5 * np.sum(np.abs(uh) ** 2, axis=0) / (n3 * n3)
    return bin_shells(modal, kmag)


def spectral_filter(uh: np.ndarray, kmag: np.ndarray, kc: float) -> np.ndarray:
    return uh * (kmag <= kc)


def estimate_tau_s(uh_ref: np.ndarray, kmag: np.ndarray, ks: float) -> float:
    """Local turnover time at the terminal-layer entry shell ks, from the
    kinetic energy in a narrow band around ks. Shared by the a-priori
    benchmark and both DNS-vs-model comparison scripts.
    """
    entry = (kmag >= ks - 0.5) & (kmag < ks + 0.5)
    k_entry = kinetic_energy_hat(uh_ref * entry)
    u_s = np.sqrt(max(2.0 * k_entry, 1e-14))
    ell_s = 2.0 * np.pi / ks if ks > 0 else float("inf")
    return ell_s / max(u_s, 1e-12)


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

    assert_snapshot_separation(cfg)

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
    delta_k = 2.0 * np.pi / cfg.domain_length

    shells, e_dns = shell_spectrum(uh_dns, kmag)

    layer = compute_terminal_layer(kc, delta_k, cfg)
    failures = validate_terminal_layer(layer, nyquist, shells, e_dns, cfg)

    status = {
        "grid_n": nx,
        "kc": layer.kc,
        "ks": layer.ks,
        "delta_k": layer.delta_k,
        "n_t": layer.n_t,
        "beta_configured": cfg.beta,
        "beta_effective": layer.beta_effective,
        "terminal_layer_source": layer.source,
        "nyquist": nyquist,
        "forcing_separation_checked": cfg.forcing_kmax is not None,
        "failures": failures,
        "status": "blocked" if failures else "ok",
        "classification": (
            "Pipeline validation passed; physical validation inconclusive "
            "because of insufficient spectral resolution."
            if failures
            else "Pipeline and physical validation both proceeded; see "
            "apriori_metrics.csv for results."
        ),
    }
    (output / "run_status.json").write_text(json.dumps(status, indent=2))

    if failures:
        print("PHYSICAL BENCHMARK BLOCKED:")
        for reason in failures:
            print(f"  - {reason}")
        print(
            "\nPipeline validation only (fetch -> filter -> spectrum) is "
            "still meaningful; see run_status.json. Do not interpret this "
            "run as support for or against the terminal-layer theory."
        )
        _, e_hard = shell_spectrum(spectral_filter(uh_dns, kmag, kc), kmag)
        pd.DataFrame({"k": shells, "dns": e_dns, "filtered_dns": e_hard}).to_csv(
            output / "spectra.csv", index=False
        )
        return

    ks = layer.ks

    # Reference resolved field: DNS filtered at the same cutoff.
    uh_ref = spectral_filter(uh_dns, kmag, kc)

    # Hard cutoff comparator.
    uh_hard = uh_ref.copy()

    # Terminal-layer a-priori transformation over one local turnover time.
    tau_s = estimate_tau_s(uh_ref, kmag, ks)

    # First a-priori test uses a neutral dimensionless strength. The forward
    # simulation should evolve C_gamma with the GP/GI controller.
    c_gamma = 1.0
    operator = terminal_operator(
        uh_ref,
        kmag,
        kc,
        layer.beta_effective,
        cfg.alpha_s,
        cfg.n_shape,
        cfg.m_shape,
        c_gamma,
        tau_s,
    )

    uh_terminal = uh_ref * np.exp(-operator["gamma"] * tau_s)

    _, e_ref = shell_spectrum(uh_ref, kmag)
    _, e_hard = shell_spectrum(uh_hard, kmag)
    _, e_terminal = shell_spectrum(uh_terminal, kmag)

    permitted = (shells > 0) & (shells <= kc)
    terminal_region = (shells >= ks) & (shells <= kc)

    metrics = {
        "grid_n": nx,
        "kc": kc,
        "ks": ks,
        "n_t": layer.n_t,
        "beta_configured": cfg.beta,
        "beta_effective": layer.beta_effective,
        "terminal_layer_source": layer.source,
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
