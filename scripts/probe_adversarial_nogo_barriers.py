#!/usr/bin/env python3
"""Grand Plan Stage 5 Probe: Adversarial No-Go Barrier Stress-Test on L=12 T^3.

Tests the Win-Win Cocycle Arch against three adversarial regimes:
  1. High-amplitude 1D/Abelian Burgers-type parallel tube (5x amplitude)
  2. Pure homochiral (u_+ only) vs. heterochiral (u_+ + u_-) Beltrami tangle
  3. High-k UV-shell random divergence-free noise (maximizing delta_NS -> 2/3)

Writes JSON receipt to:
    d:/Comfy UI/tubulance/probe_adversarial_nogo_barriers_results.json

Scientific honesty: NS_GLOBAL_REGULARITY_OPEN = true.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from probe_cl30_helical_schur_and_vorticity_cocycle import (
    build_grid_and_wavevectors,
    helical_frame_and_projectors,
    measure_cocycle_and_stretching,
)


def main():
    L = 12
    X, Y, Z, k_vec, active_mask, _ = build_grid_and_wavevectors(L)

    # Precompute Cl(3,0) helical projectors
    P_plus_grid = np.zeros((L, L, L, 3, 3), dtype=np.complex128)
    for ix, iy, iz in np.argwhere(active_mask):
        _, _, Pp, _, _, _, _ = helical_frame_and_projectors(k_vec[ix, iy, iz])
        P_plus_grid[ix, iy, iz] = Pp

    # Adversary 1: 5x amplitude 1D/Abelian parallel vortex tube
    u_tube_5x = 5.0 * np.stack([-np.sin(Y), np.sin(X), np.zeros_like(X)], axis=-1)
    res_tube = measure_cocycle_and_stretching(u_tube_5x, k_vec, scales=(1, 2, 4))

    # Adversary 2: Multi-mode homochiral (u_+ only) vs heterochiral random field
    rng = np.random.default_rng(20261120)
    raw = rng.standard_normal((L, L, L, 3))
    raw_hat = np.fft.fftn(raw, axes=(0, 1, 2))
    # Restrict to k in [1, 3] shell
    kn = np.linalg.norm(k_vec, axis=-1)
    low_mask = active_mask & (kn >= 1.0) & (kn <= 3.0)
    u_hetero_hat = np.where(low_mask[..., None], raw_hat, 0.0)
    k2 = np.sum(k_vec ** 2, axis=-1, keepdims=True)
    k2_safe = np.where(k2 > 0, k2, 1.0)
    u_hetero_hat = u_hetero_hat - np.where(k2 > 0, k_vec * (np.sum(k_vec * u_hetero_hat, axis=-1, keepdims=True) / k2_safe), 0.0)
    u_hetero = np.fft.ifftn(u_hetero_hat, axes=(0, 1, 2)).real
    u_hetero_hat = np.fft.fftn(u_hetero, axes=(0, 1, 2))
    u_homo_hat = np.einsum("ijkab,ijkb->ijka", P_plus_grid, u_hetero_hat)
    u_homo = np.fft.ifftn(u_homo_hat, axes=(0, 1, 2)).real

    res_homo = measure_cocycle_and_stretching(u_homo, k_vec, scales=(1, 2, 4))
    res_hetero = measure_cocycle_and_stretching(u_hetero, k_vec, scales=(1, 2, 4))

    # Adversary 3: High-k UV-shell random divergence-free noise (4 <= |k| <= 5.5)
    uv_mask = active_mask & (kn >= 4.0) & (kn <= 5.5)
    u_uv_hat = np.where(uv_mask[..., None], raw_hat, 0.0)
    u_uv_hat = u_uv_hat - np.where(k2 > 0, k_vec * (np.sum(k_vec * u_uv_hat, axis=-1, keepdims=True) / k2_safe), 0.0)
    u_uv = np.fft.ifftn(u_uv_hat, axes=(0, 1, 2)).real
    res_uv = measure_cocycle_and_stretching(u_uv, k_vec, scales=(1, 2, 4))

    def _phi(res_dict, b):
        d = res_dict[str(b)]["delta_NS"]
        r = res_dict[str(b)]["rho_stretch_BLK"]
        return float(np.sqrt(max(0.0, d)) * r)

    summary = {
        "adversary_1_tube_5x": {
            "delta_b4": res_tube["4"]["delta_NS"],
            "Phi_b4": _phi(res_tube, 4),
        },
        "adversary_2_homochiral_u_plus": {
            "delta_b1": res_homo["1"]["delta_NS"],
            "delta_b4": res_homo["4"]["delta_NS"],
            "Phi_b1": _phi(res_homo, 1),
            "Phi_b4": _phi(res_homo, 4),
        },
        "adversary_2_heterochiral": {
            "delta_b1": res_hetero["1"]["delta_NS"],
            "delta_b4": res_hetero["4"]["delta_NS"],
            "Phi_b1": _phi(res_hetero, 1),
            "Phi_b4": _phi(res_hetero, 4),
        },
        "adversary_3_uv_shell_noise": {
            "delta_b1": res_uv["1"]["delta_NS"],
            "delta_b4": res_uv["4"]["delta_NS"],
            "rho_b4": res_uv["4"]["rho_stretch_BLK"],
            "Phi_b1": _phi(res_uv, 1),
            "Phi_b4": _phi(res_uv, 4),
        },
    }

    checks = {
        "adv1_tube_5x_zero_ok": summary["adversary_1_tube_5x"]["Phi_b4"] < 1e-14,
        "adv2_homo_b4_depleted_ok": summary["adversary_2_homochiral_u_plus"]["Phi_b4"] < summary["adversary_2_homochiral_u_plus"]["Phi_b1"],
        "adv2_hetero_b4_depleted_ok": summary["adversary_2_heterochiral"]["Phi_b4"] < summary["adversary_2_heterochiral"]["Phi_b1"],
        "adv3_uv_noise_high_delta_ok": summary["adversary_3_uv_shell_noise"]["delta_b1"] > 0.55,
        "adv3_uv_noise_b4_collapsed_ok": summary["adversary_3_uv_shell_noise"]["Phi_b4"] < 0.02,
    }
    all_ok = all(checks.values())
    receipt = {
        "status": "ADVERSARIAL_NOGO_BARRIERS_OK" if all_ok else "FAILED",
        "NS_GLOBAL_REGULARITY_OPEN": True,
        "checks": checks,
        "summary": summary,
    }
    out_path = Path(r"d:/Comfy UI/tubulance/probe_adversarial_nogo_barriers_results.json")
    out_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
