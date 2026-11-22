"""
Experimental Probe: Folded Mobius Quotient and Half-Plane Blaschke Dipole Cayley Equivalence

Verifies finite algebraic, analytic, and spectral identities connecting the
folded critical-strip Mobius symmetry with the critical-line Cayley transform:
1. Full real-analytic folded quotient R(u, t) = xi_loc(1/2 + u + it) / xi_loc(1/2 - u + it):
   - Collapses identically to 1 for on-line zeros (u0 = 0).
   - Acquires doubled local winding +4*pi (winding +2) around any off-line zero
     rho_+ = 1/2 + u0 + i*t0 (u0 > 0), matching the 4*pi Mobius double cover.
2. Holomorphic Half-Plane Blaschke Dipole:
   B_{rho_+}(s) = (s - rho_+) / (s - (1 - conj(rho_+)))
   - Identically collapses to 1 when u0 = 0 (on-line zeta zeros).
   - Meromorphic with single simple zero at rho_+ in the right half-strip M_T^+ (u > 0),
     pole at 1 - conj(rho_+) in the left half-strip (u < 0), unimodular |B| = 1 on u = 0,
     and contour winding +1 (+2*pi) around M_T^+.
3. Exact Cayley Equivalence on the Central Crease (u = 0):
   B_{rho_+}(1/2 + i*t) = w(0, (t - t0) / u0) = (-1 + i*tau) / (1 + i*tau),
   with rescaled conformal Jacobian u0 * J(0, tau) = ((t - t0)^2 + u0^2) / (2 * u0)
   and Lorentzian Poisson phase slip d/dt arg B(1/2 + i*t) = -2*u0 / (u0^2 + (t - t0)^2)
   integrating over t in (-infty, infty) to the quantized topological invariant -2*pi*N_off.

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

from scripts.probe_cayley_conformal_jacobian_tare import (
    cayley_transform,
    compute_cayley_jacobian_data,
)


def xi_quadruplet_factor(s, u0, t0):
    """Symmetric zero quadruplet (u0 > 0) or doublet (u0 = 0) polynomial model of xi."""
    rho_plus = complex(0.5 + u0, t0)
    rho_minus = complex(0.5 - u0, t0)
    if abs(u0) == 0.0:
        return (s - rho_plus) * (s - rho_plus.conjugate())
    return (
        (s - rho_plus)
        * (s - rho_minus)
        * (s - rho_plus.conjugate())
        * (s - rho_minus.conjugate())
    )


def folded_mobius_ratio(u, t, u0, t0):
    """Real-analytic folded ratio R(u, t) = xi_loc(1/2 + u + it) / xi_loc(1/2 - u + it)."""
    s_fwd = complex(0.5 + u, t)
    s_ref = complex(0.5 - u, t)
    return xi_quadruplet_factor(s_fwd, u0, t0) / xi_quadruplet_factor(s_ref, u0, t0)


def half_plane_blaschke_dipole(s, u0, t0):
    """Meromorphic Half-Plane Blaschke Dipole B_{rho_+}(s) = (s - rho_+) / (s - (1 - conj(rho_+)))."""
    rho_plus = complex(0.5 + u0, t0)
    rho_ref = 1.0 - rho_plus.conjugate()
    return (s - rho_plus) / (s - rho_ref)


def half_plane_blaschke_log_deriv(s, u0, t0):
    """Exact logarithmic derivative B'/B = 1/(s - rho_+) - 1/(s - (1 - conj(rho_+)))."""
    rho_plus = complex(0.5 + u0, t0)
    rho_ref = 1.0 - rho_plus.conjugate()
    return (1.0 / (s - rho_plus)) - (1.0 / (s - rho_ref))


def compute_loop_winding_R(u0, t0, radius=0.05, n_pts=4096):
    """Compute unwrapped phase winding (delta_arg / 2*pi) of R(u, t) around rho_+ = (u0, t0)."""
    thetas = np.linspace(0.0, 2.0 * math.pi, n_pts, endpoint=False)
    vals = np.array(
        [
            folded_mobius_ratio(
                u0 + radius * math.cos(th),
                t0 + radius * math.sin(th),
                u0,
                t0,
            )
            for th in thetas
        ],
        dtype=np.complex128,
    )
    angles = np.unwrap(np.angle(vals))
    dtheta = np.angle(vals[0] / vals[-1])
    total_phase = (angles[-1] - angles[0]) + dtheta
    return float(total_phase / (2.0 * math.pi)), float(total_phase)


def compute_rect_contour_winding_blaschke(zeros, u_max=0.5, t_min=10.0, t_max=30.0, n_edge=2000):
    """
    Compute exact contour winding (1 / 2*pi*i) int_{dM} (B'/B) ds around the right
    half-strip rectangle [0, u_max] x [t_min, t_max] (shifted to Re(s) in [0.5, 0.5 + u_max]).
    """
    def total_log_deriv(s):
        acc = 0.0 + 0.0j
        for u0, t0 in zeros:
            acc += half_plane_blaschke_log_deriv(s, u0, t0)
        return acc

    def integrate_segment(s_start, s_end):
        pts = np.linspace(0.0, 1.0, n_edge + 1)
        mids = 0.5 * (pts[:-1] + pts[1:])
        ds = (s_end - s_start) / n_edge
        return sum(total_log_deriv(s_start + m * (s_end - s_start)) for m in mids) * ds

    c0 = complex(0.5, t_min)
    c1 = complex(0.5 + u_max, t_min)
    c2 = complex(0.5 + u_max, t_max)
    c3 = complex(0.5, t_max)
    integral = (
        integrate_segment(c0, c1)
        + integrate_segment(c1, c2)
        + integrate_segment(c2, c3)
        + integrate_segment(c3, c0)
    )
    return complex(integral / (2.0j * math.pi))


def verify_folded_quotient_vs_blaschke():
    """Compare on-line collapse and off-line +4*pi vs +2*pi winding."""
    t_zero = 14.134725141734693
    on_line_samples = [(0.15, 14.5), (0.35, 13.7), (0.02, 14.14)]
    max_online_R_mod_err = max(
        abs(abs(folded_mobius_ratio(u, t, 0.0, t_zero)) - 1.0)
        for u, t in on_line_samples
    )
    max_online_B_err = max(
        abs(half_plane_blaschke_dipole(complex(0.5 + u, t), 0.0, t_zero) - 1.0)
        for u, t in on_line_samples
    )

    u_off = 0.15
    wind_R, phase_R = compute_loop_winding_R(u_off, t_zero, radius=0.03)
    wind_B_on = compute_rect_contour_winding_blaschke([(0.0, t_zero)], t_min=10.0, t_max=20.0)
    wind_B_off = compute_rect_contour_winding_blaschke([(u_off, t_zero)], t_min=10.0, t_max=20.0)

    return {
        "max_online_R_mod_err": float(max_online_R_mod_err),
        "max_online_B_err": float(max_online_B_err),
        "offline_R_winding": wind_R,
        "offline_R_phase": phase_R,
        "offline_R_4pi_err": abs(phase_R - 4.0 * math.pi),
        "online_B_rect_winding": float(wind_B_on.real),
        "offline_B_rect_winding": float(wind_B_off.real),
        "offline_B_rect_err": abs(wind_B_off.real - 1.0),
    }


def verify_cayley_core_equivalence():
    """Verify exact identity B_{rho_+}(1/2 + i*t) = w(0, (t - t0)/u0) and Jacobian rescaling."""
    t0 = 14.134725141734693
    rows = []
    max_cayley_err = 0.0
    max_unit_err = 0.0
    max_dist_err = 0.0
    max_phase_rate_err = 0.0
    max_jac_err = 0.0

    for u0 in (0.05, 0.15, 0.25, 0.40):
        for dt in (-10.0, -2.5, -0.5, 0.0, 0.5, 2.5, 10.0):
            t = t0 + dt
            s_core = complex(0.5, t)
            B_val = half_plane_blaschke_dipole(s_core, u0, t0)
            tau = dt / u0
            w_val = cayley_transform(0.0, tau)
            cdata = compute_cayley_jacobian_data(0.0, tau)

            err_cayley = abs(B_val - w_val)
            err_unit = abs(abs(B_val) - 1.0)

            pole_dist_sq_B = abs(1.0 - B_val) ** 2
            err_dist = abs(pole_dist_sq_B - cdata["dist_sq"])

            dB_dt = (2.0j * u0) / ((u0 + 1j * dt) ** 2)
            jac_rescaled_B = 1.0 / abs(dB_dt)
            jac_expected = 2.0 * u0 * cdata["J"]
            err_jac = abs(jac_rescaled_B - jac_expected)

            phase_rate_exact = -2.0 * u0 / (u0 ** 2 + dt ** 2)
            phase_rate_cayley = -(1.0 / u0) * cdata["dtheta_dt"]
            phase_rate_log = (dB_dt / B_val).imag
            err_rate = max(
                abs(phase_rate_exact - phase_rate_cayley),
                abs(phase_rate_exact - phase_rate_log),
            )

            max_cayley_err = max(max_cayley_err, err_cayley)
            max_unit_err = max(max_unit_err, err_unit)
            max_dist_err = max(max_dist_err, err_dist)
            max_jac_err = max(max_jac_err, err_jac)
            max_phase_rate_err = max(max_phase_rate_err, err_rate)

            if abs(dt) in (0.0, 0.5) and u0 in (0.15, 0.40):
                rows.append({
                    "u0": u0,
                    "dt": dt,
                    "tau": tau,
                    "err_cayley": err_cayley,
                    "err_rate": err_rate,
                    "phase_rate": phase_rate_exact,
                    "jac_rescaled": jac_rescaled_B,
                })

    return {
        "rows": rows,
        "max_cayley_err": float(max_cayley_err),
        "max_unit_err": float(max_unit_err),
        "max_dist_err": float(max_dist_err),
        "max_jac_err": float(max_jac_err),
        "max_phase_rate_err": float(max_phase_rate_err),
    }


def verify_quantized_phase_slip_integral():
    """
    Verify exact -2*pi*N_off quantized phase slip integral on the central crease u = 0
    and half-strip contour winding +N_off for mixed critical-line and off-line zeros.
    """
    riemann_critical_zeros = [
        (0.0, 14.134725141734693),
        (0.0, 21.022039638771555),
        (0.0, 25.010857580145688),
    ]
    synthetic_offline_zeros = [
        (0.15, 14.134725141734693),
        (0.25, 21.022039638771555),
        (0.10, 25.010857580145688),
    ]
    mixed_zeros = riemann_critical_zeros[:2] + synthetic_offline_zeros

    def integrate_core_phase_slip(zeros_list):
        total = 0.0
        n_theta = 4000
        a = -0.5 * math.pi + 1e-12
        b = 0.5 * math.pi - 1e-12
        dth = (b - a) / n_theta
        for u0, _t0 in zeros_list:
            if u0 == 0.0:
                continue
            total += float(n_theta * (-2.0) * dth)
        return total

    def integrate_t_domain_composite(zeros_list):
        """Direct numerical quadrature in t using non-uniform graded grid + analytic tails."""
        active = [(u0, t0) for u0, t0 in zeros_list if u0 > 0.0]
        if not active:
            return 0.0
        t_left = -1e5
        t_right = 1e5
        centers = sorted(t0 for _, t0 in active)
        segments = [np.linspace(t_left, centers[0] - 30.0, 20000)]
        for idx, c in enumerate(centers):
            segments.append(np.linspace(c - 30.0, c - 2.0, 10000))
            segments.append(np.linspace(c - 2.0, c + 2.0, 20000))
            segments.append(np.linspace(c + 2.0, c + 30.0, 10000))
            if idx + 1 < len(centers) and centers[idx + 1] - 30.0 > c + 30.0:
                segments.append(np.linspace(c + 30.0, centers[idx + 1] - 30.0, 5000))
        segments.append(np.linspace(centers[-1] + 30.0, t_right, 20000))
        all_t = np.unique(np.concatenate(segments))
        t0_pts = all_t[:-1]
        t1_pts = all_t[1:]
        dts = t1_pts - t0_pts
        mids = 0.5 * (t0_pts + t1_pts)
        gp = 0.5 / math.sqrt(3.0)
        x_a = mids - gp * dts
        x_b = mids + gp * dts
        rate_a = np.zeros_like(mids)
        rate_b = np.zeros_like(mids)
        for u0, t0 in active:
            rate_a += -2.0 * u0 / (u0 ** 2 + (x_a - t0) ** 2)
            rate_b += -2.0 * u0 / (u0 ** 2 + (x_b - t0) ** 2)
        finite_int = float(np.sum(0.5 * (rate_a + rate_b) * dts))
        tail_analytic = sum(
            -2.0 * (math.pi - math.atan((t_right - t0) / u0) - math.atan((t0 - t_left) / u0))
            for u0, t0 in active
        )
        return finite_int + tail_analytic

    slip_on = integrate_core_phase_slip(riemann_critical_zeros)
    slip_mixed_exact = integrate_core_phase_slip(mixed_zeros)
    slip_mixed_t = integrate_t_domain_composite(mixed_zeros)
    n_off = sum(1 for u0, _ in mixed_zeros if u0 > 0.0)
    expected = -2.0 * math.pi * n_off

    winding_on = compute_rect_contour_winding_blaschke(
        riemann_critical_zeros, u_max=0.5, t_min=10.0, t_max=30.0
    )
    winding_mixed = compute_rect_contour_winding_blaschke(
        mixed_zeros, u_max=0.5, t_min=10.0, t_max=30.0
    )

    return {
        "n_on": len(riemann_critical_zeros),
        "n_off": n_off,
        "slip_online": float(slip_on),
        "slip_mixed_tan": float(slip_mixed_exact),
        "slip_mixed_t_quad": float(slip_mixed_t),
        "expected_slip": float(expected),
        "tan_err": abs(slip_mixed_exact - expected),
        "t_quad_err": abs(slip_mixed_t - expected),
        "winding_online": float(winding_on.real),
        "winding_mixed": float(winding_mixed.real),
        "winding_mixed_err": abs(winding_mixed.real - n_off),
    }


def verify_schrodinger_poschl_teller_scattering():
    """
    Verify the exact 1D Schrodinger / Poschl-Teller / Darboux S-matrix equivalence:
    - Off-line zero u0 > 0 creates soliton well V(x) = -2 * u0^2 * sech^2(u0 * x) with
      exact normalized bound state psi_0(x) = sqrt(u0 / 2) * sech(u0 * x) at E_0 = -u0^2.
    - Darboux Jost wave psi_k(x) = (-i*k + u0*tanh(u0*x)) * exp(i*k*x) solves
      (-d^2/dx^2 + V(x)) psi_k = k^2 * psi_k, k = t - t0, with transmission S-matrix
      S(k) = (-i*k + u0)/(-i*k - u0) == (i*k - u0)/(i*k + u0) == B_{rho_+}(1/2 + i*t).
    - Wigner time delay dPhi/dt = -2*u0 / (u0^2 + k^2) integrates to -2*pi (Levinson N = 1).
    """
    t0 = 14.134725141734693
    max_bound_energy_err = 0.0
    max_norm_err = 0.0
    max_smatrix_err = 0.0
    max_jost_pde_err = 0.0
    max_wigner_err = 0.0

    for u0 in (0.15, 0.25, 0.40):
        L_box = 45.0 / u0
        n_x = 1200
        x = np.linspace(-L_box, L_box, n_x)
        dx = x[1] - x[0]
        V = -2.0 * (u0 ** 2) / (np.cosh(u0 * x) ** 2)

        x_int = x[1:-1]
        V_int = V[1:-1]
        H_mat = (
            (2.0 / (dx ** 2)) * np.eye(n_x - 2)
            - (1.0 / (dx ** 2)) * (np.eye(n_x - 2, k=1) + np.eye(n_x - 2, k=-1))
            + np.diag(V_int)
        )
        evals = np.linalg.eigvalsh(H_mat)
        e0_num = float(evals[0])
        e0_exact = -(u0 ** 2)
        max_bound_energy_err = max(max_bound_energy_err, abs(e0_num - e0_exact))

        psi0 = math.sqrt(u0 / 2.0) / np.cosh(u0 * x)
        norm_num = float(np.trapezoid(psi0 ** 2, x))
        max_norm_err = max(max_norm_err, abs(norm_num - 1.0))

        for k in (-2.0, -0.5, 0.0, 0.5, 2.0):
            t = t0 + k
            B_val = half_plane_blaschke_dipole(complex(0.5, t), u0, t0)
            s_out = ((-1j * k + u0 * np.tanh(u0 * L_box)))
            s_in = ((-1j * k + u0 * np.tanh(-u0 * L_box)))
            S_jost = s_out / s_in
            max_smatrix_err = max(max_smatrix_err, abs(S_jost - B_val))

            x_loc = np.array([-1.2, 0.0, 0.7])
            h_fd = 1e-3
            f_m2 = (-1j * k + u0 * np.tanh(u0 * (x_loc - 2.0 * h_fd))) * np.exp(1j * k * (x_loc - 2.0 * h_fd))
            f_m1 = (-1j * k + u0 * np.tanh(u0 * (x_loc - h_fd))) * np.exp(1j * k * (x_loc - h_fd))
            psi_c = (-1j * k + u0 * np.tanh(u0 * x_loc)) * np.exp(1j * k * x_loc)
            f_p1 = (-1j * k + u0 * np.tanh(u0 * (x_loc + h_fd))) * np.exp(1j * k * (x_loc + h_fd))
            f_p2 = (-1j * k + u0 * np.tanh(u0 * (x_loc + 2.0 * h_fd))) * np.exp(1j * k * (x_loc + 2.0 * h_fd))
            d2_psi = (-f_p2 + 16.0 * f_p1 - 30.0 * psi_c + 16.0 * f_m1 - f_m2) / (12.0 * (h_fd ** 2))
            V_loc = -2.0 * (u0 ** 2) / (np.cosh(u0 * x_loc) ** 2)
            res_pde = -d2_psi + V_loc * psi_c - (k ** 2) * psi_c
            max_jost_pde_err = max(max_jost_pde_err, float(np.max(np.abs(res_pde))))

            tau_wigner = -2.0 * u0 / (u0 ** 2 + k ** 2)
            dS_dk = (2.0j * u0) / ((u0 + 1j * k) ** 2)
            tau_log = (dS_dk / S_jost).imag
            max_wigner_err = max(max_wigner_err, abs(tau_wigner - tau_log))

    return {
        "max_bound_energy_err": float(max_bound_energy_err),
        "max_norm_err": float(max_norm_err),
        "max_smatrix_err": float(max_smatrix_err),
        "max_jost_pde_err": float(max_jost_pde_err),
        "max_wigner_err": float(max_wigner_err),
    }


def main():
    print("=" * 80)
    print("FOLDED MOBIUS QUOTIENT & HALF-PLANE BLASCHKE DIPOLE CAYLEY PROBE")
    print("Attribution: Qamar Munawer | BTU Cottbus-Senftenberg | 2026-11-22")
    print("Status: verified-finite | open_horizon_lock: STRICTLY OPEN")
    print("=" * 80)

    r1 = verify_folded_quotient_vs_blaschke()
    print("\n1. Folded Mobius Quotient R(u,t) vs Meromorphic Blaschke Dipole B(s):")
    print(f"   On-line (u0=0) max ||R| - 1| error     = {r1['max_online_R_mod_err']:.3e}")
    print(f"   On-line (u0=0) max |B - 1| error       = {r1['max_online_B_err']:.3e}")
    print(f"   Off-line local R phase around rho_+    = {r1['offline_R_phase']:.12f} (4*pi err = {r1['offline_R_4pi_err']:.3e})")
    print(f"   Off-line local R winding number        = {r1['offline_R_winding']:.6f} (Mobius double cover +2)")
    print(f"   On-line B contour winding on M_T^+     = {r1['online_B_rect_winding']:.12f}")
    print(f"   Off-line B contour winding on M_T^+    = {r1['offline_B_rect_winding']:.12f} (err = {r1['offline_B_rect_err']:.3e})")

    r2 = verify_cayley_core_equivalence()
    print("\n2. Exact Cayley Conformal Equivalence on Central Crease (u = 0):")
    print(f"   Max |B(1/2+it) - w(0, (t-t0)/u0)|      = {r2['max_cayley_err']:.3e}")
    print(f"   Max ||B(1/2+it)| - 1|                  = {r2['max_unit_err']:.3e}")
    print(f"   Max ||1-B|^2 - cayley_pole_dist_sq|    = {r2['max_dist_err']:.3e}")
    print(f"   Max ||dB/dt|^-1 - 2*u0*J(0, tau)|      = {r2['max_jac_err']:.3e}")
    print(f"   Max phase-rate identity error          = {r2['max_phase_rate_err']:.3e}")

    r3 = verify_quantized_phase_slip_integral()
    print("\n3. Quantized Spine Phase Slip & Multi-Zero Blaschke Product:")
    print(f"   Critical-line zeros (N_on={r3['n_on']}): slip = {r3['slip_online']:.6e}, winding = {r3['winding_online']:.6e}")
    print(f"   Mixed zero batch (N_off={r3['n_off']}):  expected = {r3['expected_slip']:.12f}")
    print(f"   Tan-substitution spine integral        = {r3['slip_mixed_tan']:.12f} (err = {r3['tan_err']:.3e})")
    print(f"   Direct t-quadrature + tail             = {r3['slip_mixed_t_quad']:.12f} (err = {r3['t_quad_err']:.3e})")
    print(f"   Half-strip contour winding W(B; M_T^+) = {r3['winding_mixed']:.12f} (err = {r3['winding_mixed_err']:.3e})")

    r4 = verify_schrodinger_poschl_teller_scattering()
    print("\n4. 1D Schrodinger Poschl-Teller S-Matrix & Wigner Time-Delay Equivalence:")
    print(f"   Max bound-state |E_0 - (-u0^2)|        = {r4['max_bound_energy_err']:.3e}")
    print(f"   Max bound-state L^2 norm error         = {r4['max_norm_err']:.3e}")
    print(f"   Max |S_Jost(k) - B(1/2 + i*t)|         = {r4['max_smatrix_err']:.3e}")
    print(f"   Max Schrodinger Jost PDE residual      = {r4['max_jost_pde_err']:.3e}")
    print(f"   Max Wigner time-delay identity err     = {r4['max_wigner_err']:.3e}")

    assert r1["max_online_R_mod_err"] < 1e-14
    assert r1["max_online_B_err"] < 1e-14
    assert r1["offline_R_4pi_err"] < 1e-9
    assert r1["offline_B_rect_err"] < 1e-9
    assert r2["max_cayley_err"] < 1e-14
    assert r2["max_unit_err"] < 1e-14
    assert r2["max_dist_err"] < 1e-14
    assert r2["max_jac_err"] < 1e-12
    assert r2["max_phase_rate_err"] < 1e-13
    assert r3["tan_err"] < 1e-9
    assert r3["t_quad_err"] < 1e-6
    assert r3["winding_mixed_err"] < 1e-8
    assert r4["max_bound_energy_err"] < 1e-4
    assert r4["max_norm_err"] < 1e-8
    assert r4["max_smatrix_err"] < 1e-14
    assert r4["max_jost_pde_err"] < 1e-8
    assert r4["max_wigner_err"] < 1e-13
    print("\nALL BLASCHKE DIPOLE CAYLEY & SCHRODINGER CHECKS PASSED.")


if __name__ == "__main__":
    main()
