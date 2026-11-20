#!/usr/bin/env python3
"""Grand Plan Stage 3 Probe: Time-Evolved 3D Navier-Stokes Win-Win Cocycle Arch.

Integrates the 3D incompressible Navier-Stokes equations on L=16 T^3 via
dealiased pseudo-spectral RK4 (nu = 0.02, dt = 0.005, t in [0, 1.0]) starting
from the 3D heterochiral Taylor-Green + Kida-Pelz vortex tangle, tracking:
  - Enstrophy Z(t) = 0.5 * ||omega||^2 and palinstrophy P(t) = ||grad omega||^2
  - SO(3) vorticity cocycle defect delta_NS(b; t) at b in {1, 2, 4}
  - Coarse-grained block stretching rho_stretch^BLK(b; t) and Phi_b(t)

Writes JSON receipt to:
    d:/Comfy UI/tubulance/probe_ns_time_evolution_win_win_arch_results.json

Scientific honesty: NS_GLOBAL_REGULARITY_OPEN = true.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from probe_cl30_helical_schur_and_vorticity_cocycle import measure_cocycle_and_stretching
from probe_win_win_cocycle_dichotomy_arch import build_endpoint_fields


def _build_spectral_helpers(L: int):
    freqs = np.fft.fftfreq(L) * L
    kx, ky, kz = np.meshgrid(freqs, freqs, freqs, indexing="ij")
    k_vec = np.stack([kx, ky, kz], axis=-1)
    k2 = np.sum(k_vec ** 2, axis=-1)
    # 2/3-rule dealiasing mask
    kmax = L / 3.0
    dealias = (np.abs(kx) <= kmax) & (np.abs(ky) <= kmax) & (np.abs(kz) <= kmax)
    return k_vec, k2, dealias


def _rhs_ns(u_hat: np.ndarray, k_vec: np.ndarray, k2: np.ndarray, dealias: np.ndarray, nu: float) -> np.ndarray:
    """Pseudo-spectral 3D Navier-Stokes RHS in Fourier space: P(- (u.grad)u) - nu k^2 u_hat."""
    u = np.fft.ifftn(u_hat, axes=(0, 1, 2)).real
    # Rotational form: -(u . grad)u = u x omega - grad(|u|^2/2); Leray projection kills grad(|u|^2/2)
    omega_hat = np.cross(1j * k_vec, u_hat)
    omega = np.fft.ifftn(omega_hat, axes=(0, 1, 2)).real
    uxw = np.cross(u, omega)
    nl_hat = np.fft.fftn(uxw, axes=(0, 1, 2))
    nl_hat = np.where(dealias[..., None], nl_hat, 0.0)

    k2_safe = np.where(k2 > 0, k2, 1.0)[..., None]
    k_dot_nl = np.sum(k_vec * nl_hat, axis=-1, keepdims=True)
    proj_nl = nl_hat - np.where(k2[..., None] > 0, k_vec * (k_dot_nl / k2_safe), 0.0)
    return proj_nl - nu * k2[..., None] * u_hat


def main():
    L = 16
    nu = 0.02
    dt = 0.005
    n_steps = 200  # t in [0, 1.0]
    sample_every = 40  # t = 0.0, 0.2, 0.4, 0.6, 0.8, 1.0

    _, u0, k_vec, _, _ = build_endpoint_fields(L)
    k_vec, k2, dealias = _build_spectral_helpers(L)

    u_hat = np.fft.fftn(u0, axes=(0, 1, 2))
    u_hat = np.where(dealias[..., None], u_hat, 0.0)

    trajectory = []
    for step in range(n_steps + 1):
        if step % sample_every == 0:
            u = np.fft.ifftn(u_hat, axes=(0, 1, 2)).real
            omega_hat = np.cross(1j * k_vec, u_hat)
            omega = np.fft.ifftn(omega_hat, axes=(0, 1, 2)).real
            energy = float(0.5 * np.mean(np.sum(u ** 2, axis=-1)))
            enstrophy = float(0.5 * np.mean(np.sum(omega ** 2, axis=-1)))
            palinstrophy = float(np.mean(k2 * np.sum(np.abs(omega_hat) ** 2, axis=-1)) / (L ** 6))

            cocycle = measure_cocycle_and_stretching(u, k_vec, scales=(1, 2, 4))
            scales_out = {}
            for b in ("1", "2", "4"):
                d_ns = cocycle[b]["delta_NS"]
                rho = cocycle[b]["rho_stretch_BLK"]
                scales_out[b] = {
                    "delta_NS": d_ns,
                    "rho_stretch_BLK": rho,
                    "Phi": float(np.sqrt(max(0.0, d_ns)) * rho),
                }
            trajectory.append(
                {
                    "t": round(step * dt, 4),
                    "energy": energy,
                    "enstrophy": enstrophy,
                    "palinstrophy_norm": palinstrophy,
                    "scales": scales_out,
                }
            )

        if step < n_steps:
            k1 = _rhs_ns(u_hat, k_vec, k2, dealias, nu)
            k2_rk = _rhs_ns(u_hat + 0.5 * dt * k1, k_vec, k2, dealias, nu)
            k3_rk = _rhs_ns(u_hat + 0.5 * dt * k2_rk, k_vec, k2, dealias, nu)
            k4_rk = _rhs_ns(u_hat + dt * k3_rk, k_vec, k2, dealias, nu)
            u_hat = u_hat + (dt / 6.0) * (k1 + 2.0 * k2_rk + 2.0 * k3_rk + k4_rk)

    max_phi_b4 = max(pt["scales"]["4"]["Phi"] for pt in trajectory)
    max_phi_b1 = max(pt["scales"]["1"]["Phi"] for pt in trajectory)
    energy_monotone = all(
        trajectory[i + 1]["energy"] <= trajectory[i]["energy"] + 1e-12
        for i in range(len(trajectory) - 1)
    )
    all_finite = all(np.isfinite(pt["enstrophy"]) for pt in trajectory)
    b4_always_depleted = all(
        pt["scales"]["4"]["Phi"] < pt["scales"]["1"]["Phi"] for pt in trajectory
    )

    checks = {
        "energy_monotone_decay_ok": energy_monotone,
        "all_enstrophy_finite_ok": all_finite,
        "b4_phi_always_below_b1_ok": b4_always_depleted,
        "b4_arch_remains_small_ok": max_phi_b4 < 0.05,
    }
    all_ok = all(checks.values())
    receipt = {
        "status": "NS_TIME_EVOLUTION_WIN_WIN_ARCH_OK" if all_ok else "FAILED",
        "NS_GLOBAL_REGULARITY_OPEN": True,
        "L": L,
        "nu": nu,
        "dt": dt,
        "max_Phi_b1": max_phi_b1,
        "max_Phi_b4": max_phi_b4,
        "checks": checks,
        "trajectory": trajectory,
    }
    out_path = Path(r"d:/Comfy UI/tubulance/probe_ns_time_evolution_win_win_arch_results.json")
    out_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
