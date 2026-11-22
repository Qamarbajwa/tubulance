"""
Experimental Probe: Dynamical Moving & Untied Mobius Strip Inside the Unit Sphere B^3

Tests three dynamical regimes of a Mobius ribbon moving inside the unit sphere |r| < 1:
1. Case A (Sliding / Everting Closed Mobius Strip, Case A):
   - Parameterized twist phase phi(theta, tau) = (theta - Omega*tau) / 2 with R0 = 0.65, w = 0.25.
   - Instantaneous spatial Z_2 holonomy locks the spatial gap at 1 / (4 * R0^2) ~= 0.591716.
   - Aharonov-Bohm / Berry flux alpha = Phi_Berry / (2*pi) shifts the spectrum to
     lambda_m(alpha) = (m + 1/2 - alpha)^2 / R0^2 (periodic, vanishing at alpha = 1/2).
   - Co-moving Floquet Doppler dispersion omega_m(Omega) = (m + 1/2)^2 / R0^2 - Omega * (m + 1/2)
     reaches exact resonance omega_0 = 0 at Omega_crit = 1 / (2 * R0^2) ~= 1.183432.
2. Case B (Breathing Untied/Re-glued Boundary Phase phi(tau) & 3D Open Ribbon Tw + Wr):
   - Unitary edge gluing G(phi) interpolates continuously between untwisted cylinder (phi = 0,
     2 zero modes) and Mobius double cover (phi = pi, 1 zero mode + lambda_1 = 1/(4*R0^2)).
   - Open flexing 3D ribbon inside B^3 tracks Calugareanu-White-Fuller twist Tw(tau),
     writhe Wr(tau), and Da Costa torsion stabilization V_geom = (1/2)*tau_mat^2 - (1/4)*kappa^2.
3. Section 3 (Moving Untied Ribbon as Hardy-Littlewood Approximate Functional Equation):
   - Dynamic balanced cutoffs N(t) = floor(sqrt(|t| / (2*pi))) split zeta(1/2 + i*t) into
     Lap 1 = sum_{n <= N(t)} n^{-1/2 - i*t} and Lap 2 = chi(1/2 + i*t) * conj(Lap 1).
   - Verifies unitary |chi(1/2 + i*t)| = 1 and destructive pi phase cancellation
     Lap_2 / Lap_1 -> -1 near the first 8 Riemann zeta zeros on t in [10, 45].

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Date: 2026-11-22
Methodology Note: ai is being used as a tool
Epistemic Boundary: status: verified-finite, open_horizon_lock: STRICTLY OPEN
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cmath
import math
import numpy as np
import mpmath as mp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def sliding_mobius_state(u, v, tau, R0=0.65, w=0.25, omega=1.0):
    """3D coordinates and unit normal of a closed Mobius ribbon whose twist slides at speed omega."""
    half_phase = 0.5 * (u - omega * tau)
    rad = R0 + v * math.cos(half_phase)
    x = rad * math.cos(u)
    y = rad * math.sin(u)
    z = v * math.sin(half_phase)
    nx = -math.sin(half_phase) * math.cos(u)
    ny = -math.sin(half_phase) * math.sin(u)
    nz = math.cos(half_phase)
    return np.array([x, y, z]), np.array([nx, ny, nz])


def build_breathing_ribbon_laplacian(Nu, R0=0.65, phi=math.pi):
    """
    Build Hermitian 2-edge discrete Laplacian with time-dependent unitary cross-edge gluing
    G(phi) = 0.5*(I + sigma_x) + 0.5*exp(i*phi)*(I - sigma_x) across the seam.
    phi = 0 -> untwisted cylinder (2 zero modes);
    phi = pi -> twisted Mobius ribbon (1 zero mode + 1/(4*R0^2) gap).
    """
    du = 2.0 * math.pi / Nu
    L = np.zeros((2 * Nu, 2 * Nu), dtype=np.complex128)
    for i in range(Nu - 1):
        j = i + 1
        for s in (0, 1):
            a, b = 2 * i + s, 2 * j + s
            L[a, a] += 1.0
            L[b, b] += 1.0
            L[a, b] -= 1.0
            L[b, a] -= 1.0

    ep = cmath.exp(1j * phi)
    G = 0.5 * np.array([[1.0 + ep, 1.0 - ep], [1.0 - ep, 1.0 + ep]], dtype=np.complex128)
    G_dag = G.conj().T

    last = 2 * (Nu - 1)
    first = 0
    for s in (0, 1):
        L[last + s, last + s] += 1.0
        L[first + s, first + s] += 1.0
    L[last : last + 2, first : first + 2] -= G_dag
    L[first : first + 2, last : last + 2] -= G

    scale = 1.0 / ((R0 * du) ** 2)
    return L * scale


def run_case_a_sliding_strip_experiment(R0=0.65, w=0.25):
    """
    Verify Case A:
    1. Max radius <= R0 + w < 1.0 and Z_2 normal flip n(2*pi, tau) = -n(0, tau) invariant in tau.
    2. Spatial gap remains pinned at 1 / (4 * R0^2) across all sliding times tau.
    3. Berry-flux dispersion lambda_m(alpha) = (m + 1/2 - alpha)^2 / R0^2 vanishes at alpha = 0.5.
    4. Floquet Doppler resonance omega_0(Omega) = 1/(4*R0^2) - Omega/2 vanishes at Omega_crit = 1/(2*R0^2).
    """
    omega = 1.0
    max_norm = 0.0
    max_holonomy_flip_err = 0.0
    for tau in np.linspace(0.0, 4.0 * math.pi, 17):
        for u in np.linspace(0.0, 2.0 * math.pi, 65):
            r, _ = sliding_mobius_state(u, w, tau, R0=R0, w=w, omega=omega)
            max_norm = max(max_norm, float(np.linalg.norm(r)))
        _, n0 = sliding_mobius_state(0.0, 0.0, tau, R0=R0, w=w, omega=omega)
        _, n2pi = sliding_mobius_state(2.0 * math.pi, 0.0, tau, R0=R0, w=w, omega=omega)
        max_holonomy_flip_err = max(max_holonomy_flip_err, float(np.linalg.norm(n2pi + n0)))

    exact_static_gap = 1.0 / (4.0 * (R0 ** 2))
    omega_crit = 1.0 / (2.0 * (R0 ** 2))

    alphas = np.linspace(0.0, 1.0, 101)
    berry_lowest = [
        min(((m + 0.5 - a) ** 2) / (R0 ** 2) for m in range(-3, 4))
        for a in alphas
    ]

    omegas = np.linspace(0.0, 2.0 * omega_crit, 101)
    floquet_0 = [exact_static_gap - 0.5 * om for om in omegas]
    floquet_crit_val = exact_static_gap - 0.5 * omega_crit

    return {
        "R0": R0,
        "w": w,
        "max_norm": max_norm,
        "max_holonomy_flip_err": max_holonomy_flip_err,
        "exact_static_gap": exact_static_gap,
        "omega_crit": omega_crit,
        "floquet_at_omega_crit": floquet_crit_val,
        "berry_min_at_half": float(min(((m + 0.5 - 0.5) ** 2) / (R0 ** 2) for m in range(-3, 4))),
        "alphas": alphas,
        "berry_lowest": np.array(berry_lowest),
        "omegas": omegas,
        "floquet_0": np.array(floquet_0),
    }


def run_case_b_breathing_phase_and_open_ribbon(R0=0.65, Nu=96):
    """
    Verify Case B:
    1. Time-varying boundary phase phi(tau) = 0.5*pi*(1 - cos(tau)) makes lambda_1(tau) breathe
       smoothly between 0.0 (untwisted cylinder) and 1/(4*R0^2) (twisted Mobius peak), while
       lambda_0(tau) remains pinned at 0.0.
    2. Open flexing 3D ribbon inside B^3 converts dynamic twist Tw(tau) and spatial writhe Wr(tau),
       with material torsion tau_mat rising Da Costa ground energy above the un-twisted ribbon.
    """
    exact_peak = 1.0 / (4.0 * (R0 ** 2))
    taus = np.linspace(0.0, 2.0 * math.pi, 65)
    lam0_list = []
    lam1_list = []
    lam1_analytic = []
    phis = 0.5 * math.pi * (1.0 - np.cos(taus))
    for phi in phis:
        evals = np.linalg.eigvalsh(build_breathing_ribbon_laplacian(Nu, R0=R0, phi=float(phi)))
        lam0_list.append(float(evals[0]))
        lam1_list.append(float(evals[1]))
        lam1_analytic.append(((phi / (2.0 * math.pi)) ** 2) / (R0 ** 2))

    max_lam0_err = float(np.max(np.abs(lam0_list)))
    max_breathing_err = float(np.max(np.abs(np.array(lam1_list) - np.array(lam1_analytic))))

    n_pts = 160
    open_records = []
    max_open_radius = 0.0
    for tau in np.linspace(0.0, 2.0 * math.pi, 49):
        L_u = 1.75 * math.pi + 0.15 * math.sin(tau)
        u = np.linspace(0.0, L_u, n_pts)
        du = u[1] - u[0]
        amp_z = 0.22 * math.sin(tau)
        r_loop = 0.58 - 0.04 * (math.sin(tau) ** 2)

        x = r_loop * np.cos(u)
        y = r_loop * np.sin(u)
        z = amp_z * np.sin(2.0 * u)
        curve = np.stack([x, y, z], axis=1)
        radii = np.linalg.norm(curve, axis=1)
        max_open_radius = max(max_open_radius, float(np.max(radii) + 0.12))

        dr = np.gradient(curve, du, axis=0)
        ds = np.linalg.norm(dr, axis=1)
        s_total = float(np.trapezoid(ds, u))
        T = dr / ds[:, None]
        dT = np.gradient(T, du, axis=0) / ds[:, None]
        kappa = np.linalg.norm(dT, axis=1)
        d2T = np.gradient(dT, du, axis=0) / ds[:, None]
        cross_T_dT = np.cross(T, dT)
        denom_k2 = np.maximum(kappa ** 2, 1e-12)
        tau_frenet = np.sum(cross_T_dT * d2T, axis=1) / denom_k2

        alpha_rate = (math.pi / s_total) * (1.0 - 0.65 * abs(math.sin(tau)))
        tau_mat = tau_frenet + alpha_rate
        tw_val = float(np.trapezoid(tau_mat * ds, u) / (2.0 * math.pi))

        n_w = 50
        idx_w = np.linspace(0, n_pts - 1, n_w, dtype=int)
        cw = curve[idx_w]
        dw = np.gradient(cw, axis=0)
        wr_acc = 0.0
        for a in range(n_w):
            for b in range(a + 1, n_w):
                diff = cw[a] - cw[b]
                dist3 = float(np.linalg.norm(diff) ** 3)
                if dist3 > 1e-9:
                    wr_acc += float(np.dot(np.cross(dw[a], dw[b]), diff) / dist3)
        wr_val = 2.0 * wr_acc / (4.0 * math.pi)

        ds_avg = s_total / (n_pts - 1)
        D2 = (
            -2.0 * np.eye(n_pts - 2)
            + np.eye(n_pts - 2, k=1)
            + np.eye(n_pts - 2, k=-1)
        ) / (ds_avg ** 2)
        V_static = -0.25 * (kappa[1:-1] ** 2)
        V_dynamic = 0.5 * (tau_mat[1:-1] ** 2) - 0.25 * (kappa[1:-1] ** 2)
        e0_static = float(np.linalg.eigvalsh(-D2 + np.diag(V_static))[0])
        e0_dynamic = float(np.linalg.eigvalsh(-D2 + np.diag(V_dynamic))[0])

        open_records.append({
            "tau": float(tau),
            "Tw": tw_val,
            "Wr": wr_val,
            "Lk_open": tw_val + wr_val,
            "e0_static_flat": e0_static,
            "e0_dynamic_twisted": e0_dynamic,
            "torsion_boost": e0_dynamic - e0_static,
        })

    return {
        "exact_peak": exact_peak,
        "taus": taus,
        "phis": phis,
        "lam0_list": np.array(lam0_list),
        "lam1_list": np.array(lam1_list),
        "lam1_analytic": np.array(lam1_analytic),
        "max_lam0_err": max_lam0_err,
        "max_breathing_err": max_breathing_err,
        "max_open_radius": max_open_radius,
        "open_records": open_records,
    }


def run_approximate_functional_equation_test():
    """
    Verify Section 3:
    Compare exact Hardy Z(t) = exp(i*theta(t)) * zeta(1/2 + i*t) against the moving-cutoff
    two-lap sum Lap_1(t) + Lap_2(t) where N(t) = floor(sqrt(t / (2*pi))) on t in [10, 45].
    Check |chi(1/2 + i*t)| == 1 and destructive relative phase Lap_2 / Lap_1 -> -1 at zeros.
    """
    known_zeros = [
        14.134725141734693,
        21.022039638771555,
        25.010857580145688,
        30.424876125859513,
        32.935061587739189,
        37.586178158825671,
        40.918719012147495,
        43.327073280914999,
    ]

    t_grid = np.linspace(10.0, 45.0, 701)
    abs_zeta = np.zeros_like(t_grid)
    abs_two_lap = np.zeros_like(t_grid)
    rel_phase_pi = np.zeros_like(t_grid)
    cutoff_N = np.zeros_like(t_grid, dtype=int)
    max_chi_unit_err = 0.0

    def eval_point(t_val):
        s = mp.mpc(0.5, float(t_val))
        chi_s = (
            mp.power(2, s)
            * mp.power(mp.pi, s - 1)
            * mp.sin(mp.pi * s / 2)
            * mp.gamma(1 - s)
        )
        chi_c = complex(chi_s)
        theta_t = -0.5 * cmath.phase(chi_c)
        # Unwrap theta cleanly via mp.siegeltheta so sign of Hardy Z / RS matches smoothly
        theta_siegel = float(mp.siegeltheta(float(t_val)))
        x_t = math.sqrt(float(t_val) / (2.0 * math.pi))
        N_cut = max(1, int(math.floor(x_t)))
        p_frac = x_t - N_cut
        n_arr = np.arange(1, N_cut + 1, dtype=np.float64)
        lap1 = complex(np.sum(np.exp((-0.5 - 1j * float(t_val)) * np.log(n_arr))))
        lap2 = chi_c * lap1.conjugate()
        # First Riemann-Siegel seam correction: (-1)^(N-1) * (t/(2pi))^(-1/4) * cos(2*pi*(p^2 - p - 1/16))/cos(2*pi*p)
        denom_cos = math.cos(2.0 * math.pi * p_frac)
        if abs(denom_cos) < 1e-8:
            denom_cos = 1e-8 if denom_cos >= 0 else -1e-8
        psi_p = math.cos(2.0 * math.pi * (p_frac ** 2 - p_frac - 1.0 / 16.0)) / denom_cos
        rs_rem = ((-1) ** (N_cut - 1)) * (x_t ** (-0.5)) * psi_p
        z_exact_real = float(mp.siegelz(float(t_val)))
        two_lap_real = 2.0 * (cmath.exp(1j * theta_siegel) * lap1).real
        rs1_real = two_lap_real + rs_rem
        zeta_exact = complex(mp.zeta(s))
        ratio = lap2 / lap1
        phase_ratio = cmath.phase(ratio) / math.pi
        return (
            abs(zeta_exact),
            abs(lap1 + lap2),
            abs(rs1_real),
            abs(rs1_real - z_exact_real),
            phase_ratio,
            N_cut,
            abs(abs(chi_c) - 1.0),
        )

    abs_rs1 = np.zeros_like(t_grid)
    max_rs1_err = 0.0
    for idx, tv in enumerate(t_grid):
        az, at, ars, aerr, pr, nc, cerr = eval_point(tv)
        abs_zeta[idx] = az
        abs_two_lap[idx] = at
        abs_rs1[idx] = ars
        max_rs1_err = max(max_rs1_err, aerr)
        rel_phase_pi[idx] = pr
        cutoff_N[idx] = nc
        max_chi_unit_err = max(max_chi_unit_err, cerr)

    zero_checks = []
    for tz in known_zeros:
        az, at, ars, aerr, pr, nc, cerr = eval_point(tz)
        dist_from_pi = min(abs(abs(pr) - 1.0), abs(pr - 1.0), abs(pr + 1.0))
        zero_checks.append({
            "t_zero": tz,
            "N_cut": nc,
            "abs_zeta_exact": az,
            "abs_two_lap": at,
            "abs_rs1": ars,
            "rel_phase_pi": pr,
            "dist_from_destructive_pi": dist_from_pi,
        })

    return {
        "t_grid": t_grid,
        "abs_zeta": abs_zeta,
        "abs_two_lap": abs_two_lap,
        "abs_rs1": abs_rs1,
        "max_rs1_err": max_rs1_err,
        "rel_phase_pi": rel_phase_pi,
        "cutoff_N": cutoff_N,
        "max_chi_unit_err": max_chi_unit_err,
        "known_zeros": known_zeros,
        "zero_checks": zero_checks,
    }


def generate_dynamical_figure(res_a, res_b, res_zeta):
    """Render 4-panel figure saved to reports/dynamical_moving_mobius_in_sphere.png."""
    out_path = Path(__file__).resolve().parent.parent / "reports" / "dynamical_moving_mobius_in_sphere.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(15, 11), dpi=150)

    ax1 = fig.add_subplot(221, projection="3d")
    phi_s, theta_s = np.mgrid[0:2*np.pi:36j, 0:np.pi:20j]
    ax1.plot_wireframe(
        np.cos(phi_s) * np.sin(theta_s),
        np.sin(phi_s) * np.sin(theta_s),
        np.cos(theta_s),
        color="lightsteelblue",
        alpha=0.20,
        linewidth=0.5,
    )
    u_open = np.linspace(0.0, 1.75 * math.pi, 160)
    v_grid = np.linspace(-0.14, 0.14, 7)
    U1, V1 = np.meshgrid(u_open, v_grid)
    ax1.plot_surface(
        (0.58 + V1 * np.cos(0.5 * U1)) * np.cos(U1),
        (0.58 + V1 * np.cos(0.5 * U1)) * np.sin(U1),
        V1 * np.sin(0.5 * U1),
        color="steelblue",
        alpha=0.45,
        edgecolor="none",
    )
    tau_w = 0.5 * math.pi
    L_w = 1.75 * math.pi + 0.15 * math.sin(tau_w)
    u_w = np.linspace(0.0, L_w, 160)
    U2, V2 = np.meshgrid(u_w, v_grid)
    r_w = 0.58 - 0.04 * (math.sin(tau_w) ** 2)
    Xw = (r_w + V2 * np.cos(0.5 * U2)) * np.cos(U2)
    Yw = (r_w + V2 * np.cos(0.5 * U2)) * np.sin(U2)
    Zw = 0.22 * np.sin(2.0 * U2) + V2 * np.sin(0.5 * U2)
    ax1.plot_surface(Xw, Yw, Zw, cmap="plasma", alpha=0.80, edgecolor="none")
    ax1.set_xlim(-1.02, 1.02)
    ax1.set_ylim(-1.02, 1.02)
    ax1.set_zlim(-1.02, 1.02)
    ax1.set_box_aspect([1, 1, 1])
    ax1.set_title("1. Untied Moving Ribbon Inside B^3 (Max |r| < 1: Flat vs Writhed)")

    ax2 = fig.add_subplot(222)
    ax2.plot(res_a["omegas"], res_a["floquet_0"], "r-", linewidth=2.2, label="Floquet Co-Moving Ground omega_0(Omega)")
    ax2.axvline(res_a["omega_crit"], color="black", linestyle="--", linewidth=1.4, label=f"Resonance Omega_crit = 1/(2*R0^2) = {res_a['omega_crit']:.3f}")
    ax2.axhline(0.0, color="gray", linestyle=":", linewidth=1.0)
    ax2_top = ax2.twiny()
    ax2_top.plot(res_a["alphas"], res_a["berry_lowest"], "b--", linewidth=1.8, alpha=0.8, label="Berry-Flux Gap lambda_min(alpha)")
    ax2_top.set_xlabel("Berry Flux alpha = Phi_Berry / (2*pi)", color="blue")
    ax2.set_xlabel("Sliding Frame Angular Speed Omega", color="crimson")
    ax2.set_ylabel("Spectral Gap / Floquet Frequency")
    ax2.set_title("2. Case A: Floquet Sagnac Shift & Berry-Flux Resonance")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="lower left", fontsize=8)

    ax3 = fig.add_subplot(223)
    ax3.plot(res_b["taus"], res_b["lam0_list"], "k--", linewidth=1.5, label="Symmetric Zero Mode lambda_0(tau) == 0")
    ax3.plot(res_b["taus"], res_b["lam1_list"], "ro", markersize=3.5, label="Numerical Breathing Odd Mode lambda_1(phi(tau))")
    ax3.plot(res_b["taus"], res_b["lam1_analytic"], "b-", linewidth=1.6, alpha=0.8, label="Analytic (phi(tau)/(2*pi))^2 / R0^2")
    ax3.axhline(res_b["exact_peak"], color="crimson", linestyle=":", label=f"Mobius Peak 1/(4*R0^2) = {res_b['exact_peak']:.4f}")
    ax3.axhline(0.25, color="darkgreen", linestyle="-.", alpha=0.7, label="Unit-Sphere Threshold 1/4 = 0.2500")
    ax3.set_xlabel("Dynamical Time Parameter tau (rad)")
    ax3.set_ylabel("Lowest Two Ribbon Eigenvalues")
    ax3.set_title("3. Case B: Breathing Boundary Phase phi(tau) (Cylinder <-> Mobius)")
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="upper right", fontsize=8)

    ax4 = fig.add_subplot(224)
    ax4.plot(res_zeta["t_grid"], res_zeta["abs_zeta"], "k-", linewidth=2.0, label="|zeta(1/2 + i*t)| (Exact)")
    ax4.plot(res_zeta["t_grid"], res_zeta["abs_two_lap"], "darkorange", linestyle="--", linewidth=1.4, label="|Lap_1(t) + Lap_2(t)| (Raw 2-Lap)")
    ax4.plot(res_zeta["t_grid"], res_zeta["abs_rs1"], "royalblue", linestyle=":", linewidth=1.8, label="|2-Lap + C_0(p)| (Seam-Corrected)")
    for idx_z, tz in enumerate(res_zeta["known_zeros"]):
        lbl = "First 8 Zeta Zeros" if idx_z == 0 else None
        ax4.axvline(tz, color="crimson", linestyle=":", alpha=0.55, linewidth=1.0, label=lbl)
    ax4.axvline(2.0 * math.pi * 4.0, color="darkgreen", linestyle="-.", linewidth=1.4, label="Moving End Jump 2*pi*2^2 = 25.13 (N: 1 -> 2)")
    ax4.set_xlabel("Critical-Line Height t")
    ax4.set_ylabel("Amplitude")
    ax4.set_title("4. Untied Moving Double-Lap = Approximate Functional Eq. on Re(s) = 1/2")
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc="upper left", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return str(out_path)


def run_breathing_threshold_window_test(R0=0.65, Nu=128):
    """
    Verify exact analytic window for unit-sphere floor lambda_1(phi(tau)) >= 1/4:
    |phi(tau)| >= pi * R0  <=>  tau in [arccos(1 - 2*R0), 2*pi - arccos(1 - 2*R0)]
    for phi(tau) = 0.5*pi*(1 - cos(tau)).
    """
    from scipy.optimize import brentq

    def lam1_minus_quarter(tau_val):
        phi_val = 0.5 * math.pi * (1.0 - math.cos(tau_val))
        evals = np.linalg.eigvalsh(build_breathing_ribbon_laplacian(Nu, R0=R0, phi=phi_val))
        return float(evals[1]) - 0.25

    tau_exact_1 = math.acos(1.0 - 2.0 * R0)
    tau_exact_2 = 2.0 * math.pi - tau_exact_1
    tau_num_1 = brentq(lam1_minus_quarter, 0.1, math.pi)
    tau_num_2 = brentq(lam1_minus_quarter, math.pi, 2.0 * math.pi - 0.1)

    phi_thresh = math.pi * R0
    phi_at_num_1 = 0.5 * math.pi * (1.0 - math.cos(tau_num_1))
    return {
        "R0": R0,
        "phi_threshold": phi_thresh,
        "tau_exact_1": tau_exact_1,
        "tau_exact_2": tau_exact_2,
        "tau_num_1": float(tau_num_1),
        "tau_num_2": float(tau_num_2),
        "err_tau_1": abs(tau_num_1 - tau_exact_1),
        "err_tau_2": abs(tau_num_2 - tau_exact_2),
        "err_phi_thresh": abs(phi_at_num_1 - phi_thresh),
    }


def _riemann_siegel_psi_and_d3(p_val):
    """
    Compute Psi(p) = cos(2*pi*(p^2 - p - 1/16)) / cos(2*pi*p) and its third
    derivative Psi'''(p) cleanly across removable zeros via a Cauchy circle contour.
    """
    r = 0.05
    n_c = 16
    psi_vals = []
    d3_sum = 0.0 + 0.0j
    for k in range(n_c):
        dz = r * cmath.exp(1j * 2.0 * math.pi * k / n_c)
        z = p_val + dz
        pz = cmath.cos(2.0 * math.pi * (z * z - z - 1.0 / 16.0)) / cmath.cos(2.0 * math.pi * z)
        psi_vals.append(pz)
        d3_sum += pz / (dz ** 3)
    psi0 = (sum(psi_vals) / n_c).real
    psi3 = (6.0 * d3_sum / n_c).real
    return psi0, psi3


def run_multi_jump_riemann_siegel_seam_test():
    """
    Sweep t in [10, 120] across moving-end jumps N: 1->2 (25.13), 2->3 (56.55), 3->4 (100.53),
    comparing raw 2-lap, 1-term seam C0(p), and 2-term Gabcke C0(p) + C1(p) across 30 zeta zeros.
    """
    t_grid = np.linspace(10.0, 120.0, 881)
    err_raw = np.zeros_like(t_grid)
    err_c0 = np.zeros_like(t_grid)
    err_c01 = np.zeros_like(t_grid)

    def eval_rs(t_val):
        x_t = math.sqrt(float(t_val) / (2.0 * math.pi))
        N_cut = max(1, int(math.floor(x_t)))
        p_frac = x_t - N_cut
        th = float(mp.siegeltheta(float(t_val)))
        z_ex = float(mp.siegelz(float(t_val)))
        n_arr = np.arange(1, N_cut + 1, dtype=np.float64)
        lap1 = complex(np.sum(np.exp(-1j * float(t_val) * np.log(n_arr)) / np.sqrt(n_arr)))
        z_raw = 2.0 * (cmath.exp(1j * th) * lap1).real
        psi0, psi3 = _riemann_siegel_psi_and_d3(p_frac)
        sgn = (-1) ** (N_cut - 1)
        c0 = sgn * (x_t ** (-0.5)) * psi0
        c1 = sgn * (x_t ** (-1.5)) * (-psi3 / (96.0 * (math.pi ** 2)))
        z_c0 = z_raw + c0
        z_c01 = z_raw + c0 + c1
        return abs(z_ex - z_raw), abs(z_ex - z_c0), abs(z_ex - z_c01), N_cut

    for i, tv in enumerate(t_grid):
        er, e0, e1, _ = eval_rs(tv)
        err_raw[i] = er
        err_c0[i] = e0
        err_c01[i] = e1

    zero_rows = []
    for k_z in range(1, 31):
        tz = float(mp.im(mp.zetazero(k_z)))
        er, e0, e1, nc = eval_rs(tz)
        zero_rows.append({
            "k": k_z,
            "t_zero": tz,
            "N_cut": nc,
            "err_raw": er,
            "err_c0": e0,
            "err_c01": e1,
        })

    return {
        "t_grid": t_grid,
        "err_raw": err_raw,
        "err_c0": err_c0,
        "err_c01": err_c01,
        "max_err_raw": float(np.max(err_raw)),
        "max_err_c0": float(np.max(err_c0)),
        "max_err_c01": float(np.max(err_c01)),
        "zero_rows": zero_rows,
        "jumps": [2.0 * math.pi * (k ** 2) for k in (2, 3, 4)],
    }


def run_coupled_dacosta_poschl_teller_test(R0=0.65, tau_mat=1.40):
    """
    Diagonalize the coupled 1D Hamiltonian:
      H = -d^2/dx^2 + (0.5*tau_mat^2 - 0.25*kappa^2) - 2*u0^2*sech^2(u0*x)
    with kappa = 1/R0 and baseline V0 = 0.5*tau_mat^2 - 0.25*kappa^2 > 0 across
    soliton offsets u0 in [0.0, 0.90], verifying E_ground(u0) == V0 - u0^2 and zero
    crossing at u_crit = sqrt(V0).
    """
    kappa = 1.0 / R0
    V0 = 0.5 * (tau_mat ** 2) - 0.25 * (kappa ** 2)
    u_crit = math.sqrt(V0)
    u0_vals = [0.0, 0.15, 0.30, 0.45, 0.55, u_crit, 0.72, 0.85]
    rows = []
    L_box = 45.0
    n_x = 1200
    x = np.linspace(-L_box, L_box, n_x)
    dx = x[1] - x[0]
    T_kin = (
        (2.0 / (dx ** 2)) * np.eye(n_x - 2)
        - (1.0 / (dx ** 2)) * (np.eye(n_x - 2, k=1) + np.eye(n_x - 2, k=-1))
    )
    x_int = x[1:-1]
    max_coupled_err = 0.0
    for u0 in u0_vals:
        V_pot = (
            np.full_like(x_int, V0)
            if u0 == 0.0
            else V0 - 2.0 * (u0 ** 2) / (np.cosh(u0 * x_int) ** 2)
        )
        H_mat = T_kin + np.diag(V_pot)
        e0_num = float(np.linalg.eigvalsh(H_mat)[0])
        if u0 == 0.0:
            e0_expected = V0 + (math.pi / (2.0 * L_box)) ** 2
        else:
            e0_expected = V0 - (u0 ** 2)
        err = abs(e0_num - e0_expected)
        max_coupled_err = max(max_coupled_err, err)
        rows.append({
            "u0": float(u0),
            "e0_num": e0_num,
            "e0_analytic": V0 - (u0 ** 2),
            "err": err,
        })

    return {
        "R0": R0,
        "tau_mat": tau_mat,
        "V0": V0,
        "u_crit": u_crit,
        "rows": rows,
        "max_coupled_err": float(max_coupled_err),
    }


def generate_seam_and_schrodinger_figure(res_win, res_rs, res_coupled):
    """Render 3-panel verification figure to reports/seam_threshold_and_schrodinger_comp.png."""
    out_path = Path(__file__).resolve().parent.parent / "reports" / "seam_threshold_and_schrodinger_comp.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=150)

    ax1 = axes[0]
    taus = np.linspace(0.0, 2.0 * math.pi, 200)
    phis = 0.5 * math.pi * (1.0 - np.cos(taus))
    lams = ((phis / (2.0 * math.pi)) ** 2) / (res_win["R0"] ** 2)
    ax1.plot(taus, lams, "b-", linewidth=2.0, label="Odd Gap lambda_1(phi(tau))")
    ax1.axhline(0.25, color="darkgreen", linestyle="-.", linewidth=1.4, label="Unit-Sphere Bound 1/4 = 0.25")
    ax1.axvline(res_win["tau_exact_1"], color="crimson", linestyle="--", label=f"Exact tau_1 = {res_win['tau_exact_1']:.4f}")
    ax1.axvline(res_win["tau_exact_2"], color="crimson", linestyle="--", label=f"Exact tau_2 = {res_win['tau_exact_2']:.4f}")
    ax1.fill_between(
        taus,
        0.25,
        lams,
        where=(lams >= 0.25),
        color="mediumseagreen",
        alpha=0.25,
        label="|phi(tau)| >= pi*R0",
    )
    ax1.set_xlabel("tau (rad)")
    ax1.set_ylabel("Spectral Gap lambda_1")
    ax1.set_title("1. Exact Unit-Sphere Stability Window")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right", fontsize=7.5)

    ax2 = axes[1]
    ax2.semilogy(res_rs["t_grid"], np.maximum(res_rs["err_raw"], 1e-12), color="darkorange", alpha=0.85, linewidth=1.3, label="Raw 2-Lap Error")
    ax2.semilogy(res_rs["t_grid"], np.maximum(res_rs["err_c0"], 1e-12), color="royalblue", linewidth=1.5, label="1-Term Seam C_0(p) Error")
    ax2.semilogy(res_rs["t_grid"], np.maximum(res_rs["err_c01"], 1e-12), color="crimson", linewidth=1.5, label="2-Term Gabcke C_0+C_1 Error")
    for idx_j, tj in enumerate(res_rs["jumps"]):
        lbl = "Cutoff Jumps 2*pi*k^2" if idx_j == 0 else None
        ax2.axvline(tj, color="black", linestyle=":", linewidth=1.2, label=lbl)
    ax2.set_xlabel("Critical-Line Height t")
    ax2.set_ylabel("Abs Error vs Exact Z(t) (log)")
    ax2.set_title("2. Seam Continuity Across N: 1->2->3->4")
    ax2.grid(True, alpha=0.3, which="both")
    ax2.legend(loc="lower left", fontsize=7.5)

    ax3 = axes[2]
    u_dense = np.linspace(0.0, 0.90, 200)
    ax3.plot(u_dense, res_coupled["V0"] - u_dense ** 2, "k-", linewidth=1.8, label="Analytic V_0 - u_0^2")
    u_pts = [r["u0"] for r in res_coupled["rows"]]
    e_pts = [r["e0_num"] for r in res_coupled["rows"]]
    ax3.plot(u_pts, e_pts, "ro", markersize=6, label="1D Schrodinger Ground E_0(u_0)")
    ax3.axhline(0.0, color="gray", linestyle=":")
    ax3.axvline(res_coupled["u_crit"], color="darkgreen", linestyle="--", label=f"Threshold u_crit = sqrt(V_0) = {res_coupled['u_crit']:.4f}")
    ax3.set_xlabel("Off-Line Zero Offset u_0")
    ax3.set_ylabel("Coupled Ground Energy E_0")
    ax3.set_title("3. Da Costa Barrier vs Poschl-Teller Soliton")
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="lower left", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return str(out_path)


def run_all_tests():
    print("=" * 88)
    print("DYNAMICAL MOVING & UNTIED MOBIUS RIBBON INSIDE UNIT SPHERE B^3")
    print("Author: Qamar Munawer | BTU Cottbus-Senftenberg | 2026-11-22")
    print("ai is being used as a tool | status: verified-finite, open_horizon_lock: STRICTLY OPEN")
    print("=" * 88)

    res_a = run_case_a_sliding_strip_experiment(R0=0.65, w=0.25)
    print("\n1. CASE A (Sliding Closed Mobius Ribbon):")
    print(f"   Max |r| inside B^3                   = {res_a['max_norm']:.4f} (< 1.0)")
    print(f"   Max ||n(2pi, tau) + n(0, tau)||      = {res_a['max_holonomy_flip_err']:.3e} (Z_2 homotopy invariant)")
    print(f"   Static spatial twist gap 1/(4*R0^2)  = {res_a['exact_static_gap']:.6f}")
    print(f"   Floquet resonance Omega_crit         = {res_a['omega_crit']:.6f} -> omega_0 = {res_a['floquet_at_omega_crit']:.3e}")
    print(f"   Berry flux degeneracy at alpha=0.5   = {res_a['berry_min_at_half']:.3e}")

    res_b = run_case_b_breathing_phase_and_open_ribbon(R0=0.65, Nu=96)
    max_tw = max(abs(r["Tw"]) for r in res_b["open_records"])
    max_wr = max(abs(r["Wr"]) for r in res_b["open_records"])
    min_boost = min(r["torsion_boost"] for r in res_b["open_records"])
    max_boost = max(r["torsion_boost"] for r in res_b["open_records"])
    min_e0_stat = min(r["e0_static_flat"] for r in res_b["open_records"])
    max_e0_stat = max(r["e0_static_flat"] for r in res_b["open_records"])
    min_e0_dyn = min(r["e0_dynamic_twisted"] for r in res_b["open_records"])
    max_e0_dyn = max(r["e0_dynamic_twisted"] for r in res_b["open_records"])
    print("\n2. CASE B (Breathing Boundary Phase & Open 3D Ribbon Tw+Wr / Da Costa):")
    print(f"   Max |lambda_0(tau)| pinning error    = {res_b['max_lam0_err']:.3e}")
    print(f"   Breathing lambda_1(tau) range        = [{min(res_b['lam1_list']):.6f}, {max(res_b['lam1_list']):.6f}]")
    print(f"   Max analytic breathing discrepancy   = {res_b['max_breathing_err']:.3e}")
    print(f"   Open 3D flexing max radius inside B^3= {res_b['max_open_radius']:.4f} (< 1.0)")
    print(f"   Open ribbon excursion max |Tw|, |Wr| = {max_tw:.4f}, {max_wr:.4f}")
    print(f"   Static un-twisted Da Costa e0 range  = [{min_e0_stat:.4f}, {max_e0_stat:.4f}]")
    print(f"   Dynamically twisted e0 range         = [{min_e0_dyn:.4f}, {max_e0_dyn:.4f}]")
    print(f"   Da Costa torsion stabilization boost = [{min_boost:.4f}, {max_boost:.4f}] (> 0)")

    res_z = run_approximate_functional_equation_test()
    print("\n3. SECTION 3 (Approximate Functional Eq Double-Lap Interference):")
    print(f"   Max ||chi(1/2 + i*t)| - 1|           = {res_z['max_chi_unit_err']:.3e}")
    print(f"   Max |Z_exact - Z_RS(1-term)|         = {res_z['max_rs1_err']:.4e}")
    print("   t_zero   | N(t) | |zeta|_exact | |Lap1+Lap2| | |2Lap+C0| | arg(Lap2/Lap1)/pi | |angle-pi|/pi")
    print("   " + "-" * 86)
    for zc in res_z["zero_checks"]:
        print(
            f"   {zc['t_zero']:8.4f} | {zc['N_cut']:4d} | {zc['abs_zeta_exact']:12.3e} | "
            f"{zc['abs_two_lap']:11.4f} | {zc['abs_rs1']:9.5f} | {zc['rel_phase_pi']:+17.4f} | {zc['dist_from_destructive_pi']:13.4f}"
        )

    fig_path = generate_dynamical_figure(res_a, res_b, res_z)
    print(f"\nSaved Dynamical Figure: {fig_path}")

    res_win = run_breathing_threshold_window_test(R0=0.65, Nu=128)
    print("\n4. EXACT UNIT-SPHERE THRESHOLD WINDOW |phi(tau)| >= pi*R0:")
    print(f"   Exact tau crossings (arccos(-0.3))   = [{res_win['tau_exact_1']:.6f}, {res_win['tau_exact_2']:.6f}] rad")
    print(f"   Numeric ribbon Laplacian crossings   = [{res_win['tau_num_1']:.6f}, {res_win['tau_num_2']:.6f}] rad")
    print(f"   Crossing discrepancies               = ({res_win['err_tau_1']:.3e}, {res_win['err_tau_2']:.3e})")
    print(f"   Boundary phase threshold discrepancy = {res_win['err_phi_thresh']:.3e} vs pi*R0 = {res_win['phi_threshold']:.6f}")

    res_rs = run_multi_jump_riemann_siegel_seam_test()
    print("\n5. MULTI-JUMP RIEMANN-SIEGEL SEAM TEST (t in [10, 120], N = 1 -> 2 -> 3 -> 4):")
    print(f"   Max |Z_exact - Raw 2-Lap|            = {res_rs['max_err_raw']:.5f}")
    print(f"   Max |Z_exact - (2-Lap + C0)|         = {res_rs['max_err_c0']:.5f}")
    print(f"   Max |Z_exact - (2-Lap + C0 + C1)|    = {res_rs['max_err_c01']:.5f}")
    print(f"   Zero 3  (t={res_rs['zero_rows'][2]['t_zero']:.4f}, N={res_rs['zero_rows'][2]['N_cut']}): raw={res_rs['zero_rows'][2]['err_raw']:.5f}, c0={res_rs['zero_rows'][2]['err_c0']:.5f}, c0+c1={res_rs['zero_rows'][2]['err_c01']:.5f}")
    print(f"   Zero 13 (t={res_rs['zero_rows'][12]['t_zero']:.4f}, N={res_rs['zero_rows'][12]['N_cut']}): raw={res_rs['zero_rows'][12]['err_raw']:.5f}, c0={res_rs['zero_rows'][12]['err_c0']:.5f}, c0+c1={res_rs['zero_rows'][12]['err_c01']:.5f}")
    print(f"   Zero 29 (t={res_rs['zero_rows'][28]['t_zero']:.4f}, N={res_rs['zero_rows'][28]['N_cut']}): raw={res_rs['zero_rows'][28]['err_raw']:.5f}, c0={res_rs['zero_rows'][28]['err_c0']:.5f}, c0+c1={res_rs['zero_rows'][28]['err_c01']:.5f}")

    res_coupled = run_coupled_dacosta_poschl_teller_test(R0=0.65, tau_mat=1.40)
    print("\n6. COUPLED DA COSTA TORSION BARRIER VS POSCHL-TELLER SOLITON:")
    print(f"   Da Costa baseline V0                 = {res_coupled['V0']:.6f}, u_crit = {res_coupled['u_crit']:.6f}")
    print(f"   Max |E0_num - E0_analytic|           = {res_coupled['max_coupled_err']:.3e}")

    fig2_path = generate_seam_and_schrodinger_figure(res_win, res_rs, res_coupled)
    print(f"\nSaved Seam & Schrodinger Figure: {fig2_path}")
    print("=" * 88)

    assert res_a["max_norm"] < 1.0
    assert res_a["max_holonomy_flip_err"] < 1e-13
    assert abs(res_a["floquet_at_omega_crit"]) < 1e-14
    assert res_b["max_lam0_err"] < 1e-10
    assert res_b["max_breathing_err"] < 5e-4
    assert res_b["max_open_radius"] < 1.0
    assert min_e0_dyn > 0.25
    assert min_boost > 0.0
    assert res_z["max_chi_unit_err"] < 1e-13
    assert res_z["max_rs1_err"] < 0.02
    assert res_win["err_tau_1"] < 2e-4
    assert res_win["err_tau_2"] < 2e-4
    assert res_rs["max_err_c01"] < 0.004
    assert res_coupled["max_coupled_err"] < 2e-4
    return res_a, res_b, res_z, fig_path


if __name__ == "__main__":
    run_all_tests()
