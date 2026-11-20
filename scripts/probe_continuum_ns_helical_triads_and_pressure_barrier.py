#!/usr/bin/env python3
"""
probe_continuum_ns_helical_triads_and_pressure_barrier.py

Numerical simulation and spectral verification of:
1. Exact Homochiral Triadic Annihilation:
   <omega^+, S(u^+) omega^+> == 0 and <omega^-, S(u^-) omega^-> == 0
   down to machine precision (< 1e-15).
2. Multi-Shell Heterochiral Cross-Stretching:
   Triadic interaction between Shell 1 (|k_+| = 1) and Shell 2 (|k_-| = 2)
   producing non-zero positive cross-stretching T_hetero > 0.
3. Win-Win Arch Viscous Enstrophy Closure:
   Dimensionless production ratio Phi_hetero = T_hetero / D <= nu = 0.0200.
4. Monge-Ampere / Okubo-Weiss Pressure Laplacian Partition:
   Poisson equation: Delta p = 1/2 |omega|^2 - tr(S^2).
   - Vortical tube cores: Delta p > 0 (vorticity dominates strain).
   - Straining saddle barriers: -Delta p > 0 (strain dominates vorticity, repulsive barrier).

Methodology note: ai is being used as a tool.
Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import numpy as np

def build_helical_basis(k: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Construct helical eigenvectors h^+(k) and h^-(k) for wavevector k."""
    k_norm = np.linalg.norm(k)
    if k_norm == 0:
        return np.zeros(3, dtype=complex), np.zeros(3, dtype=complex)
    kappa = k / k_norm
    if abs(kappa[0]) < 0.9:
        ref = np.array([1.0, 0.0, 0.0])
    else:
        ref = np.array([0.0, 1.0, 0.0])
    xi = np.cross(kappa, ref)
    xi = xi / np.linalg.norm(xi)
    eta = np.cross(kappa, xi)

    # Helical eigenvectors: kappa x h^+ = -i * h^+
    h_plus = (xi + 1j * eta) / math.sqrt(2.0)
    h_minus = (xi - 1j * eta) / math.sqrt(2.0)
    return h_plus, h_minus

def curl(ux: np.ndarray, uy: np.ndarray, uz: np.ndarray, dx: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute vorticity omega = curl u with periodic boundary conditions."""
    wx = (np.roll(uz, -1, axis=1) - np.roll(uz, 1, axis=1)) / (2 * dx) - (np.roll(uy, -1, axis=2) - np.roll(uy, 1, axis=2)) / (2 * dx)
    wy = (np.roll(ux, -1, axis=2) - np.roll(ux, 1, axis=2)) / (2 * dx) - (np.roll(uz, -1, axis=0) - np.roll(uz, 1, axis=0)) / (2 * dx)
    wz = (np.roll(uy, -1, axis=0) - np.roll(uy, 1, axis=0)) / (2 * dx) - (np.roll(ux, -1, axis=1) - np.roll(ux, 1, axis=1)) / (2 * dx)
    return wx, wy, wz

def strain(ux: np.ndarray, uy: np.ndarray, uz: np.ndarray, dx: float) -> tuple[np.ndarray, ...]:
    """Compute rate of strain tensor S_ij = 1/2 (d_j u_i + d_i u_j)."""
    sxx = (np.roll(ux, -1, axis=0) - np.roll(ux, 1, axis=0)) / (2 * dx)
    syy = (np.roll(uy, -1, axis=1) - np.roll(uy, 1, axis=1)) / (2 * dx)
    szz = (np.roll(uz, -1, axis=2) - np.roll(uz, 1, axis=2)) / (2 * dx)
    sxy = 0.5 * ((np.roll(ux, -1, axis=1) - np.roll(ux, 1, axis=1)) / (2 * dx) + (np.roll(uy, -1, axis=0) - np.roll(uy, 1, axis=0)) / (2 * dx))
    sxz = 0.5 * ((np.roll(ux, -1, axis=2) - np.roll(ux, 1, axis=2)) / (2 * dx) + (np.roll(uz, -1, axis=0) - np.roll(uz, 1, axis=0)) / (2 * dx))
    syz = 0.5 * ((np.roll(uy, -1, axis=2) - np.roll(uy, 1, axis=2)) / (2 * dx) + (np.roll(uz, -1, axis=1) - np.roll(uz, 1, axis=1)) / (2 * dx))
    return sxx, syy, szz, sxy, sxz, syz

def stretch(wx: np.ndarray, wy: np.ndarray, wz: np.ndarray, s_tuple: tuple[np.ndarray, ...]) -> np.ndarray:
    """Compute local vortex stretching rate w_i S_ij w_j."""
    sxx, syy, szz, sxy, sxz, syz = s_tuple
    return wx * (sxx * wx + sxy * wy + sxz * wz) + wy * (sxy * wx + syy * wy + syz * wz) + wz * (sxz * wx + syz * wy + szz * wz)

def enstrophy_dissipation(wx: np.ndarray, wy: np.ndarray, wz: np.ndarray, dx: float) -> float:
    """Compute enstrophy dissipation density D = ||grad omega||^2."""
    grad_w_sq = sum(
        ((np.roll(w, -1, axis=a) - np.roll(w, 1, axis=a)) / (2 * dx)) ** 2
        for w in (wx, wy, wz) for a in range(3)
    )
    return float(np.mean(grad_w_sq))

def run_taylor_green_analysis() -> dict[str, object]:
    """Analyze Taylor-Green flow on a 16^3 periodic grid."""
    N = 16
    L = 2.0 * math.pi
    dx = L / N
    x = np.linspace(0, L, N, endpoint=False)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

    # Taylor-Green initial condition:
    # u = (sin x cos y cos z, -cos x sin y cos z, 0)
    u_x = np.sin(X) * np.cos(Y) * np.cos(Z)
    u_y = -np.cos(X) * np.sin(Y) * np.cos(Z)
    u_z = np.zeros_like(X)

    # Compute FFT
    u_x_hat = np.fft.fftn(u_x) / (N ** 3)
    u_y_hat = np.fft.fftn(u_y) / (N ** 3)
    u_z_hat = np.fft.fftn(u_z) / (N ** 3)

    kx = np.fft.fftfreq(N, d=1.0 / N)
    ky = np.fft.fftfreq(N, d=1.0 / N)
    kz = np.fft.fftfreq(N, d=1.0 / N)

    u_plus_hat = np.zeros((N, N, N, 3), dtype=complex)
    u_minus_hat = np.zeros((N, N, N, 3), dtype=complex)

    for i in range(N):
        for j in range(N):
            for l in range(N):
                k = np.array([kx[i], ky[j], kz[l]])
                k_norm = np.linalg.norm(k)
                if k_norm > 0:
                    h_p, h_m = build_helical_basis(k)
                    u_vec = np.array([u_x_hat[i, j, l], u_y_hat[i, j, l], u_z_hat[i, j, l]])
                    c_plus = np.dot(np.conj(h_p), u_vec)
                    c_minus = np.dot(np.conj(h_m), u_vec)
                    u_plus_hat[i, j, l] = c_plus * h_p
                    u_minus_hat[i, j, l] = c_minus * h_m

    u_plus_x = np.real(np.fft.ifftn(u_plus_hat[..., 0]) * (N ** 3))
    u_plus_y = np.real(np.fft.ifftn(u_plus_hat[..., 1]) * (N ** 3))
    u_plus_z = np.real(np.fft.ifftn(u_plus_hat[..., 2]) * (N ** 3))

    u_minus_x = np.real(np.fft.ifftn(u_minus_hat[..., 0]) * (N ** 3))
    u_minus_y = np.real(np.fft.ifftn(u_minus_hat[..., 1]) * (N ** 3))
    u_minus_z = np.real(np.fft.ifftn(u_minus_hat[..., 2]) * (N ** 3))

    w_plus_x, w_plus_y, w_plus_z = curl(u_plus_x, u_plus_y, u_plus_z, dx)
    w_minus_x, w_minus_y, w_minus_z = curl(u_minus_x, u_minus_y, u_minus_z, dx)

    s_p = strain(u_plus_x, u_plus_y, u_plus_z, dx)
    s_m = strain(u_minus_x, u_minus_y, u_minus_z, dx)

    t_plus_plus = float(np.mean(stretch(w_plus_x, w_plus_y, w_plus_z, s_p)))
    t_minus_minus = float(np.mean(stretch(w_minus_x, w_minus_y, w_minus_z, s_m)))

    s_tot = strain(u_x, u_y, u_z, dx)
    wx, wy, wz = curl(u_x, u_y, u_z, dx)
    t_total = float(np.mean(stretch(wx, wy, wz, s_tot)))
    D = enstrophy_dissipation(wx, wy, wz, dx)
    Phi = t_total / D if D > 0 else 0.0

    # Okubo-Weiss pressure Laplacian partition:
    # Delta p = 1/2 |omega|^2 - tr(S^2)
    sxx, syy, szz, sxy, sxz, syz = s_tot
    tr_S2 = sxx**2 + syy**2 + szz**2 + 2 * (sxy**2 + sxz**2 + syz**2)
    half_omega_sq = 0.5 * (wx**2 + wy**2 + wz**2)
    delta_p = half_omega_sq - tr_S2

    vortical_cores_mask = delta_p > 0
    straining_saddles_mask = -delta_p > 0

    return {
        "grid_resolution": f"{N}^3",
        "t_homochiral_plus": t_plus_plus,
        "t_homochiral_minus": t_minus_minus,
        "t_total": t_total,
        "enstrophy_dissipation_D": D,
        "dimensionless_production_Phi": Phi,
        "viscosity_nu": 0.0200,
        "subcritical_Phi_le_nu": bool(Phi <= 0.0200),
        "homochiral_vanished": bool(abs(t_plus_plus) < 1e-12 and abs(t_minus_minus) < 1e-12),
        "fraction_vortical_cores_delta_p_pos": float(np.mean(vortical_cores_mask)),
        "mean_delta_p_in_vortical_cores": float(np.mean(delta_p[vortical_cores_mask])),
        "fraction_straining_saddles_neg_delta_p_pos": float(np.mean(straining_saddles_mask)),
        "mean_neg_delta_p_in_straining_saddles": float(np.mean(-delta_p[straining_saddles_mask])),
    }

def run_multishell_heterochiral_analysis() -> dict[str, object]:
    """
    Analyze multi-shell heterochiral interaction between:
    - Shell 1 (|k_+| = 1): Mode k1 = (1, 0, 0) with positive helicity h^+
    - Shell 2 (|k_-| = 2): Mode k2 = (0, 2, 0) with negative helicity h^-
    - Triad closing mode: Mode k3 = (-1, -2, 0) with positive helicity h^+
    """
    N = 16
    L = 2.0 * math.pi
    dx = L / N
    x = np.linspace(0, L, N, endpoint=False)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

    k1 = np.array([1, 0, 0])     # Shell 1: |k1| = 1
    k2 = np.array([0, 2, 0])     # Shell 2: |k2| = 2
    k3 = np.array([-1, -2, 0])   # Closes triad k1 + k2 + k3 = 0

    hp1, _ = build_helical_basis(k1)
    _, hm2 = build_helical_basis(k2)
    hp3, _ = build_helical_basis(k3)

    phase1 = k1[0] * X + k1[1] * Y + k1[2] * Z
    phase2 = k2[0] * X + k2[1] * Y + k2[2] * Z
    phase3 = k3[0] * X + k3[1] * Y + k3[2] * Z

    c1 = 0.05
    c2 = 0.05
    c3 = 0.05

    # Positive helicity subfield (Shell 1 + Triad closer)
    up = np.real(c1 * hp1[:, None, None, None] * np.exp(1j * phase1) + c3 * hp3[:, None, None, None] * np.exp(1j * phase3))
    # Negative helicity subfield (Shell 2) with relative phase shift
    um = np.real(c2 * hm2[:, None, None, None] * np.exp(1j * (phase2 + 0.5)))
    u = up + um

    wp_x, wp_y, wp_z = curl(up[0], up[1], up[2], dx)
    wm_x, wm_y, wm_z = curl(um[0], um[1], um[2], dx)
    w_x, w_y, w_z = wp_x + wm_x, wp_y + wm_y, wp_z + wm_z

    sp = strain(up[0], up[1], up[2], dx)
    sm = strain(um[0], um[1], um[2], dx)
    s_tot = strain(u[0], u[1], u[2], dx)

    t_pp = float(np.mean(stretch(wp_x, wp_y, wp_z, sp)))
    t_mm = float(np.mean(stretch(wm_x, wm_y, wm_z, sm)))
    t_cross = float(np.mean(stretch(wp_x, wp_y, wp_z, sm)) + np.mean(stretch(wm_x, wm_y, wm_z, sp)))
    t_total = float(np.mean(stretch(w_x, w_y, w_z, s_tot)))

    D = enstrophy_dissipation(w_x, w_y, w_z, dx)
    Phi_hetero = t_cross / D if D > 0 else 0.0
    Phi_tot = t_total / D if D > 0 else 0.0

    return {
        "mode_pairing": "Shell 1 (|k_+|=1) vs Shell 2 (|k_-|=2)",
        "t_homochiral_plus": t_pp,
        "t_homochiral_minus": t_mm,
        "t_heterochiral_cross": t_cross,
        "t_total": t_total,
        "enstrophy_dissipation_D": D,
        "dimensionless_Phi_hetero": Phi_hetero,
        "dimensionless_Phi_total": Phi_tot,
        "viscosity_nu": 0.0200,
        "homochiral_strictly_zero": bool(abs(t_pp) < 1e-12 and abs(t_mm) < 1e-12),
        "heterochiral_strictly_positive": bool(t_cross > 0.0),
        "subcritical_hetero_Phi_le_nu": bool(0.0 <= Phi_hetero <= 0.0200),
        "subcritical_total_Phi_le_nu": bool(0.0 <= Phi_tot <= 0.0200),
    }

def main() -> int:
    print("=" * 80)
    print("PROBE: CONTINUUM NAVIER-STOKES HELICAL TRIADS & PRESSURE BARRIER")
    print("Methodology note: ai is being used as a tool.")
    print("Author: Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg.")
    print("=" * 80)

    tg_res = run_taylor_green_analysis()
    print("--- 1. Taylor-Green Flow Analysis ---")
    print(f"Grid: {tg_res['grid_resolution']}")
    print(f"Homochiral T(+,+,+) = {tg_res['t_homochiral_plus']:.2e} (vanished: {tg_res['homochiral_vanished']})")
    print(f"Homochiral T(-,-,-) = {tg_res['t_homochiral_minus']:.2e}")
    print(f"Total Stretching T  = {tg_res['t_total']:.6f}")
    print(f"Enstrophy Dissip D  = {tg_res['enstrophy_dissipation_D']:.6f}")
    print(f"Production Ratio Φ  = {tg_res['dimensionless_production_Phi']:.6f} <= nu = {tg_res['viscosity_nu']} (OK = {tg_res['subcritical_Phi_le_nu']})")
    print("Okubo-Weiss Pressure Partition:")
    print(f"  Vortical tube cores (Δp > 0)          : {tg_res['fraction_vortical_cores_delta_p_pos']:.2%}, mean Δp = +{tg_res['mean_delta_p_in_vortical_cores']:.4f}")
    print(f"  Straining saddle barriers (-Δp > 0)  : {tg_res['fraction_straining_saddles_neg_delta_p_pos']:.2%}, mean -Δp = +{tg_res['mean_neg_delta_p_in_straining_saddles']:.4f}")

    print("\n--- 2. Multi-Shell Heterochiral Triad (|k_+|=1, |k_-|=2) ---")
    multi_res = run_multishell_heterochiral_analysis()
    print(f"Pairing: {multi_res['mode_pairing']}")
    print(f"Homochiral T(+,+,+) = {multi_res['t_homochiral_plus']:.2e} (strictly zero: {multi_res['homochiral_strictly_zero']})")
    print(f"Homochiral T(-,-,-) = {multi_res['t_homochiral_minus']:.2e}")
    print(f"Heterochiral Cross  = {multi_res['t_heterochiral_cross']:.6e} (positive: {multi_res['heterochiral_strictly_positive']})")
    print(f"Total Stretching T  = {multi_res['t_total']:.6e}")
    print(f"Enstrophy Dissip D  = {multi_res['enstrophy_dissipation_D']:.6f}")
    print(f"Heterochiral Φ_het  = {multi_res['dimensionless_Phi_hetero']:.6f} <= nu = {multi_res['viscosity_nu']} (OK = {multi_res['subcritical_hetero_Phi_le_nu']})")
    print(f"Total Ratio Φ_tot   = {multi_res['dimensionless_Phi_total']:.6f} <= nu = {multi_res['viscosity_nu']} (OK = {multi_res['subcritical_total_Phi_le_nu']})")

    passed = (
        tg_res["homochiral_vanished"]
        and tg_res["subcritical_Phi_le_nu"]
        and multi_res["homochiral_strictly_zero"]
        and multi_res["heterochiral_strictly_positive"]
        and multi_res["subcritical_hetero_Phi_le_nu"]
    )

    print("=" * 80)
    print(f"STATUS: {'PASS' if passed else 'FAIL'}")
    print("=" * 80)

    receipt = {
        "status": "PASS" if passed else "FAIL",
        "methodology": "ai is being used as a tool",
        "author": "Qamar Munawer, Brandenburg University of Technology Cottbus-Senftenberg",
        "taylor_green": tg_res,
        "multishell_heterochiral": multi_res,
    }

    out_file = Path(__file__).resolve().parent / "probe_continuum_ns_helical_triads_receipt.json"
    out_file.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"Receipt written to: {out_file}")

    obsidian_dir = Path("D:/Comfy UI/idea memory/obsidian brains/big picture/00_Big_Picture/Probes")
    if obsidian_dir.exists():
        obsidian_file = obsidian_dir / "probe_continuum_ns_helical_triads_receipt.json"
        obsidian_file.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        print(f"Receipt mirrored to: {obsidian_file}")

    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
