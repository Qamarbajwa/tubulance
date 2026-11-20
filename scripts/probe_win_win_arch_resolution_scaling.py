#!/usr/bin/env python3
"""Grand Plan Stage 2 Probe: Resolution Scaling (L=12 vs L=24) of the Win-Win Cocycle Arch.

Tests whether the coarse-grained block stretching arch
    Phi_b(delta_NS) = sqrt(delta_NS(b)) * rho_stretch^BLK(b)
remains bounded and continues to compress monotonically across block scales
as grid resolution doubles from L=12 to L=24 on T^3.

Writes JSON receipt to:
    d:/Comfy UI/tubulance/probe_win_win_arch_resolution_scaling_results.json

Scientific honesty: NS_GLOBAL_REGULARITY_OPEN = true.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from probe_cl30_helical_schur_and_vorticity_cocycle import measure_cocycle_and_stretching
from probe_win_win_cocycle_dichotomy_arch import build_endpoint_fields


def sweep_resolution(L: int, scales: tuple[int, ...], n_lam: int = 21):
    u_tube, u_tangle, k_vec, _, _ = build_endpoint_fields(L)
    lams = np.linspace(0.0, 1.0, n_lam)

    summaries = {}
    for b in scales:
        summaries[str(b)] = {"deltas": [], "rhos": [], "phis": []}

    for lam in lams:
        u = (1.0 - float(lam)) * u_tube + float(lam) * u_tangle
        res = measure_cocycle_and_stretching(u, k_vec, scales=scales)
        for b in scales:
            bs = str(b)
            d_ns = res[bs]["delta_NS"]
            rho = res[bs]["rho_stretch_BLK"]
            phi = float(np.sqrt(max(0.0, d_ns)) * rho)
            summaries[bs]["deltas"].append(d_ns)
            summaries[bs]["rhos"].append(rho)
            summaries[bs]["phis"].append(phi)

    out = {}
    for b in scales:
        bs = str(b)
        phis = np.array(summaries[bs]["phis"])
        deltas = np.array(summaries[bs]["deltas"])
        idx = int(np.argmax(phis))
        out[bs] = {
            "lambda_star": round(float(lams[idx]), 4),
            "delta_star": float(deltas[idx]),
            "Phi_max": float(phis[idx]),
            "Phi_at_lam1": float(phis[-1]),
            "strict_interior_peak": 0.0 < float(lams[idx]) < 1.0 and 0.0 < float(deltas[idx]) < (2.0 / 3.0),
        }
    return out


def main():
    s12 = sweep_resolution(12, scales=(1, 2, 4), n_lam=21)
    s24 = sweep_resolution(24, scales=(1, 2, 4, 8), n_lam=21)

    # Matched physical block scale: b/L in {1/12, 1/6, 1/3}
    # L=12: (1, 2, 4); L=24: (2, 4, 8)
    checks = {
        "l12_physical_monotone_ok": s12["1"]["Phi_max"] > s12["2"]["Phi_max"] > s12["4"]["Phi_max"],
        "l24_physical_monotone_ok": s24["2"]["Phi_max"] > s24["4"]["Phi_max"] > s24["8"]["Phi_max"],
        "l24_b4_and_b8_strict_interior_ok": s24["4"]["strict_interior_peak"] and s24["8"]["strict_interior_peak"],
        "uv_refinement_contracts_all_matched_scales_ok": (
            s24["2"]["Phi_max"] <= s12["1"]["Phi_max"]
            and s24["4"]["Phi_max"] <= s12["2"]["Phi_max"]
            and s24["8"]["Phi_max"] <= s12["4"]["Phi_max"]
        ),
    }
    all_ok = all(checks.values())
    receipt = {
        "status": "WIN_WIN_ARCH_RESOLUTION_SCALING_OK" if all_ok else "FAILED",
        "NS_GLOBAL_REGULARITY_OPEN": True,
        "checks": checks,
        "L12": s12,
        "L24": s24,
    }
    out_path = Path(r"d:/Comfy UI/tubulance/probe_win_win_arch_resolution_scaling_results.json")
    out_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
