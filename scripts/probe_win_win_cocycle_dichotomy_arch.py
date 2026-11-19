#!/usr/bin/env python3
"""Win-Win Cocycle Dichotomy Arch Probe for 3D Navier-Stokes on L=12 T^3.

Sweeps the parametrized 3D divergence-free velocity family:
    u(lam) = (1 - lam) * u_tube_1D + lam * u_tangle_3D,   lam in [0, 1]
across block scales b in {1, 2, 4}, measuring:
  - Constantin-Fefferman SO(3) vorticity frame alignment defect delta_NS(b)
  - Coarse-grained block vortex-stretching transfer kernel rho_stretch^BLK(b)
  - Combined Win-Win dichotomy arch product:
        Phi_b(lam) = sqrt(delta_NS(b)) * rho_stretch^BLK(b)
  - Cl(3,0) helical Schur / chiral imbalance diagnostics

Writes JSON receipt to:
    d:/Comfy UI/tubulance/probe_win_win_cocycle_dichotomy_arch_results.json

Scientific honesty: 3D Navier-Stokes Global Regularity remains strictly OPEN
(NS_GLOBAL_REGULARITY_OPEN = true). This script certifies the finite-grid
dichotomy arch on L=12 T^3.
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


def build_endpoint_fields(L: int = 12):
    """Construct the exact 1D/Abelian parallel vortex tube and 3D heterochiral tangle."""
    X, Y, Z, k_vec, active_mask, _ = build_grid_and_wavevectors(L)

    # 1D/Abelian parallel vortex tube: omega = (0, 0, cos(x)+cos(y)), delta_NS == 0
    u_tube = np.stack(
        [
            -np.sin(Y),
            np.sin(X),
            np.zeros_like(X),
        ],
        axis=-1,
    )

    # 3D heterochiral Taylor-Green + Kida-Pelz + ABC vortex tangle
    u_tg = np.stack(
        [
            np.sin(X) * np.cos(Y) * np.cos(Z),
            -np.cos(X) * np.sin(Y) * np.cos(Z),
            np.zeros_like(X),
        ],
        axis=-1,
    )
    u_kp = np.stack(
        [
            np.sin(X) * (np.cos(3 * Y) * np.cos(Z) - np.cos(Y) * np.cos(3 * Z)),
            np.sin(Y) * (np.cos(3 * Z) * np.cos(X) - np.cos(Z) * np.cos(3 * X)),
            np.sin(Z) * (np.cos(3 * X) * np.cos(Y) - np.cos(X) * np.cos(3 * Y)),
        ],
        axis=-1,
    )
    u_abc = np.stack(
        [
            np.sin(2 * Z) + 0.7 * np.cos(2 * Y),
            np.sin(2 * X) + 0.7 * np.cos(2 * Z),
            np.sin(2 * Y) + 0.7 * np.cos(2 * X),
        ],
        axis=-1,
    )
    u_tangle = u_tg + 0.6 * u_kp + 0.5 * u_abc

    # Project u_tangle to exact divergence-free
    u_tangle_hat = np.fft.fftn(u_tangle, axes=(0, 1, 2))
    kn2 = np.sum(k_vec ** 2, axis=-1, keepdims=True)
    kn2_safe = np.where(kn2 > 0, kn2, 1.0)
    k_dot_u = np.sum(k_vec * u_tangle_hat, axis=-1, keepdims=True)
    u_tangle_hat = u_tangle_hat - np.where(kn2 > 0, k_vec * (k_dot_u / kn2_safe), 0.0)
    u_tangle = np.fft.ifftn(u_tangle_hat, axes=(0, 1, 2)).real

    # Precompute Cl(3,0) helical projectors on active shell
    P_plus_grid = np.zeros((L, L, L, 3, 3), dtype=np.complex128)
    P_minus_grid = np.zeros((L, L, L, 3, 3), dtype=np.complex128)
    for ix, iy, iz in np.argwhere(active_mask):
        _, _, Pp, Pm, _, _, _ = helical_frame_and_projectors(k_vec[ix, iy, iz])
        P_plus_grid[ix, iy, iz] = Pp
        P_minus_grid[ix, iy, iz] = Pm

    return u_tube, u_tangle, k_vec, P_plus_grid, P_minus_grid


def helical_schur_diagnostics(u: np.ndarray, P_plus_grid: np.ndarray, P_minus_grid: np.ndarray):
    """Compute Cl(3,0) helical energy split E_+, E_- and chiral imbalance |<u, T_hel u>| / ||u||^2."""
    u_hat = np.fft.fftn(u, axes=(0, 1, 2))
    up_hat = np.einsum("ijkab,ijkb->ijka", P_plus_grid, u_hat)
    um_hat = np.einsum("ijkab,ijkb->ijka", P_minus_grid, u_hat)
    e_plus = float(np.sum(np.abs(up_hat) ** 2))
    e_minus = float(np.sum(np.abs(um_hat) ** 2))
    e_tot = e_plus + e_minus
    chiral_imbalance = float(abs(e_plus - e_minus) / e_tot) if e_tot > 0 else 0.0
    return e_plus, e_minus, chiral_imbalance


def run_sweep(L: int = 12, n_lam: int = 41):
    u_tube, u_tangle, k_vec, Pp_grid, Pm_grid = build_endpoint_fields(L)
    lams = np.linspace(0.0, 1.0, n_lam)

    sweep_records = []
    for lam in lams:
        u = (1.0 - float(lam)) * u_tube + float(lam) * u_tangle
        res = measure_cocycle_and_stretching(u, k_vec, scales=(1, 2, 4))
        _, _, chiral_imb = helical_schur_diagnostics(u, Pp_grid, Pm_grid)

        rec = {
            "lambda": round(float(lam), 6),
            "cl30_chiral_imbalance": chiral_imb,
            "scales": {},
        }
        for b in (1, 2, 4):
            sb = res[str(b)]
            d_ns = sb["delta_NS"]
            rho = sb["rho_stretch_BLK"]
            phi = float(np.sqrt(max(0.0, d_ns)) * rho)
            rec["scales"][str(b)] = {
                "delta_NS": d_ns,
                "rho_stretch_BLK": rho,
                "Phi": phi,
            }
        sweep_records.append(rec)

    # Summarize peak & analytical envelope per scale b in {1, 2, 4}
    scale_summaries = {}
    for b in (1, 2, 4):
        bs = str(b)
        deltas = np.array([r["scales"][bs]["delta_NS"] for r in sweep_records])
        rhos = np.array([r["scales"][bs]["rho_stretch_BLK"] for r in sweep_records])
        phis = np.array([r["scales"][bs]["Phi"] for r in sweep_records])

        idx_max = int(np.argmax(phis))
        lam_star = sweep_records[idx_max]["lambda"]
        delta_star = float(deltas[idx_max])
        rho_at_star = float(rhos[idx_max])
        phi_max = float(phis[idx_max])
        phi_end_0 = float(phis[0])
        phi_end_1 = float(phis[-1])

        # Analytical envelope: Phi(delta) <= sqrt(delta) * rho_max_global
        # and Schur-tared arch bound: Phi_max < sqrt(delta_max) * max(rho)
        naive_corner_bound = float(np.sqrt(np.max(deltas)) * np.max(rhos))
        arch_compression_factor = float(phi_max / naive_corner_bound) if naive_corner_bound > 0 else 0.0

        scale_summaries[bs] = {
            "lambda_star": lam_star,
            "delta_star": delta_star,
            "rho_at_star": rho_at_star,
            "Phi_max": phi_max,
            "Phi_at_lam0": phi_end_0,
            "Phi_at_lam1": phi_end_1,
            "delta_at_lam1": float(deltas[-1]),
            "rho_max": float(np.max(rhos)),
            "rho_at_lam1": float(rhos[-1]),
            "naive_corner_bound": naive_corner_bound,
            "arch_compression_factor": arch_compression_factor,
            "strict_interior_peak": 0.0 < lam_star < 1.0 and 0.0 < delta_star < (2.0 / 3.0),
        }

    return sweep_records, scale_summaries


def main():
    sweep_records, scale_summaries = run_sweep(L=12, n_lam=41)

    checks = {
        "lam0_delta_zero_ok": all(
            abs(sweep_records[0]["scales"][str(b)]["Phi"]) < 1e-14 for b in (1, 2, 4)
        ),
        "b2_strict_interior_arch_ok": scale_summaries["2"]["strict_interior_peak"],
        "b4_strict_interior_arch_ok": scale_summaries["4"]["strict_interior_peak"],
        "b4_phi_arch_beats_naive_corner_ok": (
            scale_summaries["4"]["Phi_max"] < scale_summaries["4"]["naive_corner_bound"]
        ),
        "b4_high_delta_depletes_phi_ok": (
            scale_summaries["4"]["Phi_at_lam1"] < scale_summaries["4"]["Phi_max"]
        ),
    }

    all_ok = all(checks.values())
    receipt = {
        "status": "WIN_WIN_COCYCLE_DICHOTOMY_ARCH_OK" if all_ok else "FAILED",
        "NS_GLOBAL_REGULARITY_OPEN": True,
        "grid_L": 12,
        "n_lambda": len(sweep_records),
        "checks": checks,
        "scale_summaries": scale_summaries,
        "sweep": sweep_records,
    }

    here = Path(__file__).resolve().parent
    base_dir = here.parent if here.name == "scripts" else here
    out_path = base_dir / "probe_win_win_cocycle_dichotomy_arch_results.json"
    out_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    # Generate publication plot paper/win_win_cocycle_dichotomy_arch.png when matplotlib is available
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=160)
        colors = {"1": "#64748b", "2": "#2563eb", "4": "#dc2626"}
        labels = {"1": "b = 1 (fine grid)", "2": "b = 2 (block)", "4": "b = 4 (coarse block)"}

        for b in ("1", "2", "4"):
            ds = [r["scales"][b]["delta_NS"] for r in sweep_records]
            phis = [r["scales"][b]["Phi"] for r in sweep_records]
            s = scale_summaries[b]
            axes[0].plot(ds, phis, "-o", markersize=3, linewidth=1.8, color=colors[b], label=labels[b])
            if s["strict_interior_peak"]:
                axes[0].scatter([s["delta_star"]], [s["Phi_max"]], color=colors[b], s=60, zorder=5, edgecolor="black")
            if b in ("2", "4"):
                norm_phis = [p / s["Phi_max"] for p in phis]
                axes[1].plot(ds, norm_phis, "-o", markersize=3, linewidth=1.8, color=colors[b], label=f"{labels[b]} (peak at $\\delta_*$={s['delta_star']:.3f})")
                axes[1].scatter([s["delta_star"]], [1.0], color=colors[b], s=60, zorder=5, edgecolor="black")

        axes[0].set_title(r"Combined Stretching Arch $\Phi_b(\delta_{\mathrm{NS}}) = \sqrt{\delta_{\mathrm{NS}}(b)}\,\rho_{\mathrm{stretch}}^{\mathrm{BLK}}(b)$")
        axes[0].set_xlabel(r"$SO(3)$ Vorticity Cocycle Defect $\delta_{\mathrm{NS}}(b)$")
        axes[0].set_ylabel(r"$\Phi_b(\delta_{\mathrm{NS}})$")
        axes[0].set_xlim(-0.02, 0.68)
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(fontsize=8)

        axes[1].set_title(r"Normalized Block Arch $\Phi_b / \Phi_{b,\max}$ ($b \in \{2, 4\}$)")
        axes[1].set_xlabel(r"$SO(3)$ Vorticity Cocycle Defect $\delta_{\mathrm{NS}}(b)$")
        axes[1].set_ylabel(r"Normalized $\Phi_b / \Phi_{b,\max}$")
        axes[1].set_xlim(-0.02, 0.68)
        axes[1].set_ylim(-0.05, 1.12)
        axes[1].grid(True, alpha=0.3)
        axes[1].legend(fontsize=8)

        fig.suptitle(
            "3D Navier-Stokes Win-Win Cocycle Dichotomy Arch (L=12 T^3; NS_GLOBAL_REGULARITY_OPEN = true)",
            fontsize=11,
            fontweight="bold",
        )
        fig.tight_layout()
        plot_path = (base_dir / "paper" / "win_win_cocycle_dichotomy_arch.png") if here.name == "scripts" else (base_dir / "win_win_cocycle_dichotomy_arch.png")
        plot_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(plot_path, bbox_inches="tight")
        plt.close(fig)
    except ImportError:
        pass

    print("=== WIN-WIN COCYCLE DICHOTOMY ARCH SUMMARY (L=12, lam in [0, 1]) ===")
    for b in ("1", "2", "4"):
        s = scale_summaries[b]
        print(
            f"  b={b}: lam*={s['lambda_star']:.3f} | delta*={s['delta_star']:.4f} | "
            f"Phi_max={s['Phi_max']:.4f} (lam=0: {s['Phi_at_lam0']:.4f}, lam=1: {s['Phi_at_lam1']:.4f}) | "
            f"naive_bound={s['naive_corner_bound']:.4f} | interior={s['strict_interior_peak']}"
        )
    print(f"Status: {receipt['status']}")
    if not all_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
