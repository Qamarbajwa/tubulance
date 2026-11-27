"""Verify the Contravariant Dual System, Cubic Determinant Sign Split, and Two-Level External Schur Tare.

Saves JSON receipts to:
  - d:\\Comfy UI\\tubulance\\probe_contravariant_dual_and_cubic_sign_results.json
  - D:\\Comfy UI\\idea memory\\obsidian brains\\big picture\\00_Big_Picture\\Probes\\probe_contravariant_dual_and_cubic_sign_results.json
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import numpy as np


def run_contravariant_inverse_probe():
    """Verify 1 / (G_{DD} * (G^{-1})_{DD}) == sin^2 Theta across representative Gram states."""
    states = [
        {"name": "hodge_sp8_schur", "A": 16.0, "B": 0.0, "D": 1152.0},
        {"name": "ym_su2_cavity_tare", "A": 65.4505, "B": 12.0, "D": 15.67},
        {"name": "riemann_N211_eff", "A": 1.0, "B": math.sqrt(1.0 - 0.00862901), "D": 1.0},
        {"name": "riemann_N1000_eff", "A": 1.0, "B": math.sqrt(1.0 - 0.00656137), "D": 1.0},
    ]
    rows = []
    max_err = 0.0
    for st in states:
        A, B, D = st["A"], st["B"], st["D"]
        G = np.array([[A, B], [B, D]], dtype=np.float64)
        G_inv = np.linalg.inv(G)
        S_D = D - (B ** 2) / A
        sin_sq = S_D / D
        lhs = 1.0 / (D * float(G_inv[1, 1]))
        err = abs(lhs - sin_sq)
        max_err = max(max_err, err)
        # Verify inverse Schur complement recovers 1/A
        inv_schur = float(G_inv[0, 0]) - (float(G_inv[0, 1]) ** 2) / float(G_inv[1, 1])
        inv_A_err = abs(inv_schur - 1.0 / A)
        max_err = max(max_err, inv_A_err)
        rows.append(
            {
                "name": st["name"],
                "sin_sq": round(sin_sq, 10),
                "reciprocal_G_DD_Ginv_DD": round(lhs, 10),
                "sin_sq_err": err,
                "inv_schur_vs_inv_A_err": inv_A_err,
            }
        )
    return {"max_contravariant_err": max_err, "contravariant_ok": max_err < 1e-12, "states": rows}


def run_cubic_determinant_ns_l16_probe():
    """Measure positive-det axial tube vs. negative-det biaxial sheet across 4,096 cells of L=16 3D NS."""
    L = 16
    xs = np.linspace(0.0, 2.0 * math.pi, L, endpoint=False)
    X, Y, Z = np.meshgrid(xs, xs, xs, indexing="ij")
    # 3D Taylor-Green + helical perturbation (incompressible div u = 0)
    u = np.sin(X) * np.cos(Y) * np.cos(Z) + 0.25 * np.sin(2 * Z)
    v = -np.cos(X) * np.sin(Y) * np.cos(Z) + 0.25 * np.cos(2 * X)
    w = 0.25 * np.sin(2 * Y)
    k = np.fft.fftfreq(L, d=1.0 / L)
    KX, KY, KZ = np.meshgrid(k, k, k, indexing="ij")

    def d_axis(arr, K):
        return np.fft.ifftn(1j * K * np.fft.fftn(arr)).real

    ux, uy, uz = d_axis(u, KX), d_axis(u, KY), d_axis(u, KZ)
    vx, vy, vz = d_axis(v, KX), d_axis(v, KY), d_axis(v, KZ)
    wx, wy, wz = d_axis(w, KX), d_axis(w, KY), d_axis(w, KZ)

    # Symmetric strain tensor S_ij at all 4096 cells
    S = np.zeros((L, L, L, 3, 3), dtype=np.float64)
    S[..., 0, 0] = ux
    S[..., 1, 1] = vy
    S[..., 2, 2] = wz
    S[..., 0, 1] = S[..., 1, 0] = 0.5 * (uy + vx)
    S[..., 0, 2] = S[..., 2, 0] = 0.5 * (uz + wx)
    S[..., 1, 2] = S[..., 2, 1] = 0.5 * (vz + wy)

    # Subtract tiny discrete spectral trace if any so trace-free condition holds to machine precision
    tr = (S[..., 0, 0] + S[..., 1, 1] + S[..., 2, 2]) / 3.0
    S[..., 0, 0] -= tr
    S[..., 1, 1] -= tr
    S[..., 2, 2] -= tr

    eigs = np.linalg.eigvalsh(S.reshape(-1, 3, 3))  # sorted ascending: lam1 <= lam2 <= lam3
    dets = eigs[:, 0] * eigs[:, 1] * eigs[:, 2]
    # Verify 4 * lam1 * lam2 * lam3 == lam3^3 - lam3 * (lam1 - lam2)^2
    lhs = 4.0 * dets
    rhs = (eigs[:, 2] ** 3) - eigs[:, 2] * ((eigs[:, 0] - eigs[:, 1]) ** 2)
    max_cubic_err = float(np.max(np.abs(lhs - rhs)))

    tube_cells = int(np.sum(dets > 1e-12))
    sheet_cells = int(np.sum(dets < -1e-12))
    neutral_cells = int(4096 - tube_cells - sheet_cells)
    return {
        "grid_cells": 4096,
        "max_cubic_identity_err": max_cubic_err,
        "cubic_identity_ok": max_cubic_err < 1e-12,
        "positive_det_axial_tube_cells": tube_cells,
        "negative_det_biaxial_sheet_cells": sheet_cells,
        "neutral_cells": neutral_cells,
        "tube_fraction": round(tube_cells / 4096.0, 4),
        "sheet_fraction": round(sheet_cells / 4096.0, 4),
    }


def run_two_level_external_tare_probe():
    """Tabulate the two-level external Schur tare up to N=1000 from Riemann receipts."""
    src = Path(
        r"D:\Comfy UI\idea memory\obsidian brains\big picture\03_Riemann_Hypothesis\Probes\binary_compression_and_schur_trigonometry_N1000.json"
    )
    data = json.loads(src.read_text(encoding="utf-8"))
    t11 = data["test11_binary_compression_booster"]
    rows = []
    all_mono = True
    for r in t11:
        S_act = r["E_dir_sqf"]
        S_full = r["E_dir_full"]
        dS_P0 = S_act - S_full
        # Monotonicity S_inf (0 asymptotic target) <= S_full <= S_act
        mono = (0.0 <= S_full <= S_act) and (dS_P0 >= 0.0)
        all_mono = all_mono and mono
        rows.append(
            {
                "N": r["N"],
                "S_act_sqf": round(S_act, 8),
                "S_full": round(S_full, 8),
                "dS_P0_null_kernel_tare": round(dS_P0, 8),
                "monotonicity_holds": mono,
            }
        )
    return {"all_monotone": all_mono, "rows_up_to_N1000": rows}


def main() -> None:
    c_inv = run_contravariant_inverse_probe()
    cubic = run_cubic_determinant_ns_l16_probe()
    tare = run_two_level_external_tare_probe()

    passed = c_inv["contravariant_ok"] and cubic["cubic_identity_ok"] and tare["all_monotone"]
    payload = {
        "probe": "RosettaContravariantDualAndCubicSign",
        "epistemic_status": "verified-finite",
        "passed": passed,
        "contravariant_inverse_schur_sine": c_inv,
        "cubic_determinant_ns_l16": cubic,
        "two_level_external_tare_N1000": tare,
    }
    text = json.dumps(payload, indent=2)
    out1 = Path(r"d:\Comfy UI\tubulance\probe_contravariant_dual_and_cubic_sign_results.json")
    out2 = Path(
        r"D:\Comfy UI\idea memory\obsidian brains\big picture\00_Big_Picture\Probes\probe_contravariant_dual_and_cubic_sign_results.json"
    )
    out2.parent.mkdir(parents=True, exist_ok=True)
    out1.write_text(text, encoding="utf-8")
    out2.write_text(text, encoding="utf-8")
    print(f"CONTRAVARIANT_CUBIC_PASSED={passed}")
    print(f"MAX_CONTRAVARIANT_ERR={c_inv['max_contravariant_err']:.2e}")
    print(
        f"L16_CUBIC_ERR={cubic['max_cubic_identity_err']:.2e} | "
        f"tube={cubic['positive_det_axial_tube_cells']} ({cubic['tube_fraction']}) vs "
        f"sheet={cubic['negative_det_biaxial_sheet_cells']} ({cubic['sheet_fraction']})"
    )


if __name__ == "__main__":
    main()
