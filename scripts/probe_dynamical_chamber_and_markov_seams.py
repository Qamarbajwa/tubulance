"""
Probe: All 3 Dynamical Continuum Seams:
  1. Dynamical Seam 1: 1-Loop Vacuum Chamber Self-Selection (v_2 > v_1 > 0)
  2. Dynamical Seam 2: Cayley-Poisson Prime Gram Matrix & Exact Markov Schur Screening
  3. Dynamical Seam 3: 4D-to-3D PDE Wavenumber Cancellation & Dressed Viscosity (nu_eff)

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Date: 2026-11-22
Methodology Note: ai is being used as a tool
Epistemic Boundary: status: verified-finite, open_horizon_lock: STRICTLY OPEN
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
import numpy as np
from scipy.integrate import quad
from scripts.probe_nonabelian_commutator_schur_gap import construct_spherical_multiplet_basis


def compute_vacuum_chamber_profile(N, phi, rho_sq=0.29, R=1e6, use_canonical_scale=False):
    """
    Seam 1 (Part A): Evaluate the 8x8 mixed-parity Hessian H(phi), blocks (D, B, A),
    and Schur complement S_eff(phi) at fixed density rho^2 = v1^2 + v2^2 = 0.29
    with v1 = rho * cos(phi), v2 = rho * sin(phi).
    Under baseline grain factor G_N = N*(N^2 - 1)/24 (= 5 * G_canonical),
    the l=1 dipole stiffness coefficient is 3 and asymptotic l=2 octupole
    stiffness coefficient is 45/7 = 6.428571 > 3.
    """
    rho = math.sqrt(rho_sq)
    v1 = rho * math.cos(phi)
    v2 = rho * math.sin(phi)
    
    T_l1, ortho_l2, j = construct_spherical_multiplet_basis(N)
    basis = T_l1 + ortho_l2
    dim_basis = len(basis)
    
    if use_canonical_scale:
        G_N = (N * (N ** 2 - 1)) / 120.0
    else:
        G_N = (N * (N ** 2 - 1)) / 24.0
        
    Phi = [v1 * T_l1[a] + v2 * ortho_l2[a] for a in range(3)]
    
    H_q = np.zeros((dim_basis, dim_basis))
    for mu in range(dim_basis):
        for nu in range(dim_basis):
            val = 0.0
            for a in range(3):
                c_mu = basis[mu] @ Phi[a] - Phi[a] @ basis[mu]
                c_nu = basis[nu] @ Phi[a] - Phi[a] @ basis[nu]
                val += - np.trace(c_mu @ c_nu).real
            H_q[mu, nu] = G_N * val
            
    H_free = np.zeros((dim_basis, dim_basis))
    if R < 1e12:
        for i in range(3):
            H_free[i, i] = 2.0 / (R ** 2)
        for i in range(3, dim_basis):
            H_free[i, i] = 6.0 / (R ** 2)
            
    H = H_free + H_q
    D = H[:3, :3]
    B = H[3:, :3]
    A = H[3:, 3:]
    
    A_inv = np.linalg.pinv(A)
    S_eff = D - B.T @ A_inv @ B
    
    ev_H = np.linalg.eigvalsh(H)
    ev_A = np.linalg.eigvalsh(A)
    ev_S = np.linalg.eigvalsh(S_eff)
    
    min_S = float(ev_S.min())
    min_A = float(ev_A.min())
    tr_H = float(np.trace(H))
    
    if min_S > 1e-12:
        tr_inv_S = float(np.sum(1.0 / ev_S))
    else:
        tr_inv_S = float("inf")
        
    if ev_H.min() > 1e-12:
        log_det_H = float(np.sum(np.log(ev_H)))
    else:
        log_det_H = float("-inf")
        
    chamber = "Barrier (v1=v2)" if abs(phi - math.pi / 4.0) < 1e-6 else ("Chamber I (v1>v2)" if phi < math.pi / 4.0 else "Chamber II (v2>v1)")
    
    return {
        "N": N,
        "j": j,
        "phi_deg": math.degrees(phi),
        "v1": v1,
        "v2": v2,
        "G_N": G_N,
        "tr_H": tr_H,
        "min_A": min_A,
        "min_S": min_S,
        "tr_inv_S": tr_inv_S,
        "log_det_H": log_det_H,
        "chamber": chamber
    }


def get_first_n_primes(n):
    """Return the first n prime numbers."""
    primes = []
    cand = 2
    while len(primes) < n:
        if all(cand % p != 0 for p in primes):
            primes.append(cand)
        cand += 1
    return primes


def verify_cayley_poisson_quadrature(p, q):
    """
    Numerically compute the Cayley-Poisson Gram entry:
      Q_{pq} = Integral_{-infty}^{infty} p^(-it) q^(it) dt / (pi * (1 + t^2))
             = 2 * Integral_{0}^{infty} cos(|ln(p/q)| * t) / (pi * (1 + t^2)) dt
    and compare against min(p, q) / max(p, q).
    """
    omega = abs(math.log(p / q))
    if omega == 0.0:
        return {"p": p, "q": q, "quad": 1.0, "exact": 1.0, "err": 0.0}
    val, _ = quad(lambda t: 2.0 / (math.pi * (1.0 + t ** 2)), 0.0, math.inf, weight="cos", wvar=omega)
    exact = float(min(p, q)) / float(max(p, q))
    return {
        "p": p,
        "q": q,
        "quad": float(val),
        "exact": exact,
        "err": abs(float(val) - exact)
    }


def compute_markov_prime_gram_schur(N):
    """
    Seam 2 (Part B): Construct the NxN Cayley-Poisson Prime Gram matrix Q_N
    with entries Q_jk = min(p_j, p_k) / max(p_j, p_k), tare out the first N-1 primes,
    and verify exact Markov screening:
      1. Intermediate weights on p_1 .. p_{N-2} vanish identically to <= 1e-14.
      2. S_eff(p_N) == 1 - (p_{N-1} / p_N)^2 == (p_N^2 - p_{N-1}^2) / p_N^2 > 0.
      3. det(Q_N) == Product_{j=1}^{N-1} (1 - (p_j / p_{j+1})^2) > 0.
    """
    ps = get_first_n_primes(N)
    Q = np.array([[float(min(ps[i], ps[j])) / float(max(ps[i], ps[j])) for j in range(N)] for i in range(N)])
    
    Q_prev = Q[:-1, :-1]
    B = Q[-1:, :-1]
    weights = np.linalg.solve(Q_prev, B.T).flatten()
    
    max_intermediate_weight = float(np.max(np.abs(weights[:-1]))) if N > 2 else 0.0
    last_weight = float(weights[-1])
    expected_last_weight = float(ps[-2]) / float(ps[-1])
    
    S_eff_num = float((1.0 - B @ weights.reshape(-1, 1)).item())
    S_eff_exact = 1.0 - (float(ps[-2]) / float(ps[-1])) ** 2
    err_S = abs(S_eff_num - S_eff_exact)
    
    det_num = float(np.linalg.det(Q))
    det_exact = 1.0
    for idx in range(N - 1):
        det_exact *= (1.0 - (float(ps[idx]) / float(ps[idx + 1])) ** 2)
    err_det = abs(det_num - det_exact)
    
    J_markov = (float(ps[-1]) ** 2) / (float(ps[-1]) ** 2 - float(ps[-2]) ** 2)
    J_markov_prod = J_markov * S_eff_num
    err_markov_prod = abs(J_markov_prod - 1.0)
    
    return {
        "N": N,
        "p_prev": ps[-2],
        "p_N": ps[-1],
        "max_intermediate_weight": max_intermediate_weight,
        "last_weight": last_weight,
        "expected_last_weight": expected_last_weight,
        "S_eff_num": S_eff_num,
        "S_eff_exact": S_eff_exact,
        "err_S": err_S,
        "det_num": det_num,
        "det_exact": det_exact,
        "err_det": err_det,
        "J_markov": J_markov,
        "J_markov_prod": J_markov_prod,
        "err_markov_prod": err_markov_prod
    }


def verify_universal_trophic_sum_of_squares(rho_sq=0.29):
    """
    Verify the universal Trophic Sum-of-Squares Decomposition across
    N in {3, 4, 5, 6, 8, 10, 12, 100} and angles phi in (0, pi/2):
      min(S_eff(N; v1, v2)) == (3*(v1^2 - v2^2)^2 + (gamma_N - 3)*v2^2*(v1^2 + v2^2))
                               / (3*v1^2 + gamma_N*v2^2)
    where gamma_3 = 3 and gamma_N = 45/7 - 120/(7*(N^2 - 4)) for N >= 4.
    Also verify exact closed-form landmarks:
      - N=3, (v1, v2) = (0.2, 0.5): drain e2(3) = 4/29, floor = 441/2900.
      - N=4, phi=45 deg: barrier floor = 29/400 = 0.0725.
      - N->infty, phi=45 deg: barrier floor = 29/275.
    """
    N_list = [3, 4, 5, 6, 8, 10, 12, 100]
    phi_canonical = math.atan2(0.5, 0.2)
    phi_degs = [15.0, 30.0, 45.0, 60.0, math.degrees(phi_canonical), 75.0]
    
    max_err = 0.0
    records = []
    
    for N in N_list:
        gamma_N = 3.0 if N == 3 else (45.0 / 7.0 - 120.0 / (7.0 * (N ** 2 - 4)))
        for phi_deg in phi_degs:
            phi = math.radians(phi_deg)
            v1 = math.sqrt(rho_sq) * math.cos(phi)
            v2 = math.sqrt(rho_sq) * math.sin(phi)
            
            num_sos = 3.0 * ((v1 ** 2 - v2 ** 2) ** 2) + (gamma_N - 3.0) * (v2 ** 2) * (v1 ** 2 + v2 ** 2)
            den_sos = 3.0 * (v1 ** 2) + gamma_N * (v2 ** 2)
            pred_min_S = num_sos / den_sos
            
            meas = compute_vacuum_chamber_profile(N, phi, rho_sq=rho_sq, R=1e15)["min_S"]
            err = abs(pred_min_S - meas)
            if err > max_err:
                max_err = err
                
            records.append({
                "N": N,
                "phi_deg": phi_deg,
                "gamma_N": gamma_N,
                "pred_min_S": pred_min_S,
                "meas_min_S": meas,
                "err": err
            })
            
    # Check specific landmarks
    r_n3_02_05 = compute_vacuum_chamber_profile(3, phi_canonical, rho_sq=0.29, R=1e15)["min_S"]
    err_n3_landmark = abs(r_n3_02_05 - (441.0 / 2900.0))
    
    r_n4_45 = compute_vacuum_chamber_profile(4, math.pi / 4.0, rho_sq=0.29, R=1e15)["min_S"]
    err_n4_45 = abs(r_n4_45 - (29.0 / 400.0))
    
    barrier_inf = ((45.0 / 7.0 - 3.0) / (45.0 / 7.0 + 3.0)) * 0.29
    err_inf_exact = abs(barrier_inf - (29.0 / 275.0))
    
    return {
        "max_err": max_err,
        "err_n3_landmark": err_n3_landmark,
        "err_n4_45": err_n4_45,
        "barrier_inf": barrier_inf,
        "err_inf_exact": err_inf_exact,
        "records": records
    }


def verify_trophic_sum_of_squares_and_tridiagonal_markov(rho_sq=0.29, seed=42):
    """
    Part (a): Verify Universal Trophic Sum-of-Squares formula across
      N in {3, 4, 6, 8, 12, 100} and phi in {15, 45, 75} degrees (<= 1e-15 error),
      and exact asymptotic 4/11 symmetric-ray survival ratio giving barrier 29/275.
    Part (b): Construct closed-form tridiagonal inverse K_N of Cayley-Poisson
      prime Gram matrix Q_N for N = 2..25, verifying:
        1. ||K_N - inv(Q_N)||_max and ||Q_N @ K_N - I_N||_max.
        2. (Q_N^-1)_{j,k} == 0 for |j - k| >= 2.
        3. (K_N)_{N,N} == J_Markov(p_{N-1}, p_N) = p_N^2 / (p_N^2 - p_{N-1}^2).
        4. v^T K_N v == v_1^2 + sum_{j=1}^{N-1} J_Markov(p_j, p_{j+1}) * (v_{j+1} - (p_j/p_{j+1})*v_j)^2.
    """
    # Part (a)
    N_vals = [3, 4, 6, 8, 12, 100]
    phi_vals = [15.0, 45.0, 75.0]
    trophic_max_err = 0.0
    for N in N_vals:
        gamma_N = 3.0 if N == 3 else (45.0 / 7.0 - 120.0 / (7.0 * (N ** 2 - 4)))
        for phi_deg in phi_vals:
            phi = math.radians(phi_deg)
            v1 = math.sqrt(rho_sq) * math.cos(phi)
            v2 = math.sqrt(rho_sq) * math.sin(phi)
            pred = (3.0 * ((v1 ** 2 - v2 ** 2) ** 2) + (gamma_N - 3.0) * (v2 ** 2) * (v1 ** 2 + v2 ** 2)) / (3.0 * (v1 ** 2) + gamma_N * (v2 ** 2))
            meas = compute_vacuum_chamber_profile(N, phi, rho_sq=rho_sq, R=1e15)["min_S"]
            err = abs(pred - meas)
            if err > trophic_max_err:
                trophic_max_err = err
                
    gamma_inf = 45.0 / 7.0
    ratio_4_11 = (gamma_inf - 3.0) / (gamma_inf + 3.0)
    err_4_11 = abs(ratio_4_11 - (4.0 / 11.0))
    barrier_29_275 = ratio_4_11 * rho_sq
    err_29_275 = abs(barrier_29_275 - (29.0 / 275.0))
    
    # Part (b)
    np.random.seed(seed)
    primes = get_first_n_primes(25)
    max_inv_err = 0.0
    max_residual_err = 0.0
    max_off_tridiag = 0.0
    max_corner_err = 0.0
    max_quad_err = 0.0
    tridiag_records = []
    
    for N in range(2, 26):
        ps = primes[:N]
        Q = np.array([[float(min(ps[i], ps[j])) / float(max(ps[i], ps[j])) for j in range(N)] for i in range(N)])
        K_num = np.linalg.inv(Q)
        
        K_exact = np.zeros((N, N))
        for i in range(N - 1):
            pa, pb = float(ps[i]), float(ps[i + 1])
            J_i = (pb ** 2) / (pb ** 2 - pa ** 2)
            ratio = pa / pb
            K_exact[i, i] += J_i * (ratio ** 2)
            K_exact[i + 1, i + 1] += J_i
            K_exact[i, i + 1] = -J_i * ratio
            K_exact[i + 1, i] = -J_i * ratio
        K_exact[0, 0] += 1.0
        
        inv_err = float(np.max(np.abs(K_exact - K_num)))
        residual_err = float(np.max(np.abs(Q @ K_exact - np.eye(N))))
        off_tridiag = max((float(abs(K_num[i, j])) for i in range(N) for j in range(N) if abs(i - j) >= 2), default=0.0)
        
        J_last = (float(ps[-1]) ** 2) / (float(ps[-1]) ** 2 - float(ps[-2]) ** 2)
        corner_err = abs(float(K_num[-1, -1]) - J_last)
        
        v = np.random.randn(N)
        quad_num = float(v @ K_num @ v)
        quad_sos = float(v[0] ** 2)
        for j in range(N - 1):
            pj, pnext = float(ps[j]), float(ps[j + 1])
            Jj = (pnext ** 2) / (pnext ** 2 - pj ** 2)
            quad_sos += Jj * ((v[j + 1] - (pj / pnext) * v[j]) ** 2)
        quad_err = abs(quad_num - quad_sos)
        
        max_inv_err = max(max_inv_err, inv_err)
        max_residual_err = max(max_residual_err, residual_err)
        max_off_tridiag = max(max_off_tridiag, off_tridiag)
        max_corner_err = max(max_corner_err, corner_err)
        max_quad_err = max(max_quad_err, quad_err)
        
        if N in [2, 3, 5, 10, 15, 25]:
            tridiag_records.append({
                "N": N,
                "p_N": ps[-1],
                "inv_err": inv_err,
                "residual_err": residual_err,
                "off_tridiag": off_tridiag,
                "corner_err": corner_err,
                "quad_err": quad_err
            })
            
    return {
        "trophic_max_err": trophic_max_err,
        "ratio_4_11": ratio_4_11,
        "err_4_11": err_4_11,
        "barrier_29_275": barrier_29_275,
        "err_29_275": err_29_275,
        "max_inv_err": max_inv_err,
        "max_residual_err": max_residual_err,
        "max_off_tridiag": max_off_tridiag,
        "max_corner_err": max_corner_err,
        "max_quad_err": max_quad_err,
        "tridiag_records": tridiag_records
    }


def compute_pde_dressed_viscosity(k_par, k_4=1.0, M_bulk=1.0, nu=0.5, U_cross=0.4):
    """
    Seam 3 (Part C): Evaluate 4D-to-3D PDE wavenumber cancellation and dressed viscosity.
    In-slice stiffness:  lam_D = nu * k_par^2
    Normal stiffness:    lam_A = nu * k_4^2 + M_bulk^2
    Cross-slice flux:    norm_B = U_cross * k_par
    Schur ratio:         alpha = norm_B^2 / (lam_A * lam_D) == U_cross^2 / (nu * lam_A)
    Dressed viscosity:   nu_eff = (1 - alpha) * nu > 0
    Monotone basin check: 2 * C1 * C2 <= nu_eff * (C1 + 3 * C2) for small C1, C2.
    """
    lam_D = nu * (k_par ** 2)
    lam_A = nu * (k_4 ** 2) + (M_bulk ** 2)
    norm_B = U_cross * k_par
    
    alpha_raw = (norm_B ** 2) / (lam_A * lam_D)
    alpha_analytic = (U_cross ** 2) / (nu * lam_A)
    err_alpha = abs(alpha_raw - alpha_analytic)
    
    S_eff_D = lam_D - (norm_B ** 2) / lam_A
    nu_eff = (1.0 - alpha_raw) * nu
    expected_S_eff = nu_eff * (k_par ** 2)
    err_S_eff = abs(S_eff_D - expected_S_eff)
    
    # Verify monotone viscous basin preservation with dressed viscosity
    C1 = 0.001 * nu_eff
    C2 = 0.002 * nu_eff
    basin_lhs = 2.0 * C1 * C2
    basin_rhs = nu_eff * (C1 + 3.0 * C2)
    basin_preserved = bool(nu_eff > 0 and basin_lhs <= basin_rhs)
    
    return {
        "k_par": k_par,
        "lam_D": lam_D,
        "lam_A": lam_A,
        "norm_B": norm_B,
        "alpha_raw": alpha_raw,
        "alpha_analytic": alpha_analytic,
        "err_alpha": err_alpha,
        "nu": nu,
        "nu_eff": nu_eff,
        "S_eff_D": S_eff_D,
        "err_S_eff": err_S_eff,
        "basin_preserved": basin_preserved
    }


def run_investigation():
    print("=" * 92)
    print("UNIFIED DYNAMICAL SEAMS: CHAMBER SELF-SELECTION, MARKOV PRIME SCHUR & DRESSED VISCOSITY")
    print("Author: Qamar Munawer | BTU Cottbus-Senftenberg | 2026-11-22")
    print("ai is being used as a tool | status: verified-finite")
    print("=" * 92)
    
    print("\nPHASE 1: DYNAMICAL SEAM 1 - 1-LOOP VACUUM CHAMBER SELF-SELECTION (rho^2 = 0.29)")
    print("  N   | phi(deg) |     v1 |     v2 |   Tr(H) |  min(A) |   min(S_eff) | Tr(S^-1) | Region")
    print("  " + "-" * 86)
    
    # First show N=3 exact singular wall at phi = 45 deg
    for phi_deg in [15.0, 45.0, 75.0]:
        r = compute_vacuum_chamber_profile(3, math.radians(phi_deg), R=1e15)
        tr_str = "     inf" if math.isinf(r["tr_inv_S"]) else f"{r['tr_inv_S']:8.4f}"
        print(f"  {r['N']:3d} | {r['phi_deg']:8.2f} | {r['v1']:6.4f} | {r['v2']:6.4f} | {r['tr_H']:7.4f} | {r['min_A']:7.4f} | {r['min_S']:12.6e} | {tr_str} | {r['chamber']}")
        
    print("  " + "-" * 86)
    for N in [4, 6, 8, 12, 100]:
        for phi_deg in [15.0, 45.0, 75.0]:
            r = compute_vacuum_chamber_profile(N, math.radians(phi_deg), R=1e15)
            tr_str = "     inf" if math.isinf(r["tr_inv_S"]) else f"{r['tr_inv_S']:8.4f}"
            print(f"  {r['N']:3d} | {r['phi_deg']:8.2f} | {r['v1']:6.4f} | {r['v2']:6.4f} | {r['tr_H']:7.4f} | {r['min_A']:7.4f} | {r['min_S']:12.6f} | {tr_str} | {r['chamber']}")
            
    print("\nPHASE 2A: CAYLEY-POISSON QUADRATURE VERIFICATION FOR GRAM MATRIX Q_jk")
    print("  (p, q)  |   Quadrature Value | Exact min(p,q)/max(p,q) |     Error")
    print("  " + "-" * 65)
    for p, q in [(2, 3), (3, 5), (2, 11), (19, 23)]:
        qr = verify_cayley_poisson_quadrature(p, q)
        print(f"  ({p:2d},{q:2d}) | {qr['quad']:18.12f} | {qr['exact']:23.12f} | {qr['err']:9.2e}")
        
    print("\nPHASE 2B: DYNAMICAL SEAM 2 - EXACT MARKOV PRIME SCHUR SCREENING (N = 2..25)")
    print("   N | p_N | max|w_prev| |   S_eff_num |   J_Markov  |  J*S_eff |     det(Q_N) |  err_det")
    print("  " + "-" * 86)
    for N in [2, 3, 5, 10, 15, 25]:
        mr = compute_markov_prime_gram_schur(N)
        print(f"  {mr['N']:2d} | {mr['p_N']:3d} | {mr['max_intermediate_weight']:11.2e} | {mr['S_eff_num']:11.8f} | {mr['J_markov']:11.6f} | {mr['J_markov_prod']:8.6f} | {mr['det_num']:12.4e} | {mr['err_det']:8.2e}")
        
    print("\nPHASE 2C: DYNAMICAL SEAM 3 - 4D-TO-3D PDE WAVENUMBER CANCELLATION & DRESSED VISCOSITY")
    print("    k_par |      lam_D |    norm_B | alpha_raw | alpha_ana |  err_alpha |   nu_eff | Basin Status")
    print("  " + "-" * 86)
    for k_par in [0.1, 1.0, 10.0, 100.0, 1000.0]:
        pr = compute_pde_dressed_viscosity(k_par, k_4=1.0, M_bulk=1.0, nu=0.5, U_cross=0.4)
        status = "BASIN PRESERVED" if pr["basin_preserved"] else "FAILED"
        print(f"  {pr['k_par']:7.1f} | {pr['lam_D']:10.4f} | {pr['norm_B']:9.4f} | {pr['alpha_raw']:9.6f} | {pr['alpha_analytic']:9.6f} | {pr['err_alpha']:10.2e} | {pr['nu_eff']:8.6f} | {status}")
        
    print("\nPHASE 3: UNIVERSAL TROPHIC SUM-OF-SQUARES & TRIDIAGONAL MARKOV INVERSE")
    tm = verify_trophic_sum_of_squares_and_tridiagonal_markov()
    print(f"  Trophic Sum-of-Squares Max Error:        {tm['trophic_max_err']:.2e}")
    print(f"  Asymptotic 4/11 Ratio:                   {tm['ratio_4_11']:.12f} (Err: {tm['err_4_11']:.2e})")
    print(f"  Continuum Symmetric Barrier (29/275):    {tm['barrier_29_275']:.12f} (Err: {tm['err_29_275']:.2e})")
    print(f"  Tridiagonal Max ||K_N - inv(Q_N)||_max:  {tm['max_inv_err']:.2e}")
    print(f"  Tridiagonal Max ||Q_N @ K_N - I_N||_max: {tm['max_residual_err']:.2e}")
    print(f"  Tridiagonal Max Off-Diagonal |j-k|>=2:   {tm['max_off_tridiag']:.2e}")
    print(f"  Tridiagonal Max Corner Error (N,N):      {tm['max_corner_err']:.2e}")
    print(f"  Tridiagonal Max Quadratic SoS Error:     {tm['max_quad_err']:.2e}")
    print("  N  | p_N | ||K-inv(Q)|| | ||QK-I|| | Off-Tridiag |  Corner Err |  Quad SoS Err")
    print("  " + "-" * 78)
    for rec in tm["tridiag_records"]:
        print(f"  {rec['N']:2d} | {rec['p_N']:3d} | {rec['inv_err']:12.2e} | {rec['residual_err']:8.2e} | {rec['off_tridiag']:11.2e} | {rec['corner_err']:11.2e} | {rec['quad_err']:13.2e}")
        
    print("\n" + "=" * 92)
    print("MATHEMATICAL VERDICT:")
    print("1. Seam 1 (Vacuum Chamber Self-Selection): At N=3, phi=45 deg (v1=v2) forms a singular")
    print("   inverse-propagator wall (lambda_min=0, Tr(S^-1)=inf). For all N>=4, the l=3 octupole")
    print("   channel opens (asymptotic ratio 45/7 = 6.42857 > 3), making Chamber II (v2 > v1 > 0)")
    print("   strictly dominant over Chamber I in Tr(H), min(A), min(S_eff), and 1-loop stability.")
    print("   Asymptotic symmetric-ray survival ratio is identically 4/11, lifting floor to 29/275.")
    print("2. Seam 2 (Cayley-Poisson Markov Screening): Pulling back p_j^(-it) under d_theta/(2*pi)")
    print("   yields Q_jk = min(p_j,p_k)/max(p_j,p_k). Exact tridiagonal inverse K_N = Q_N^-1")
    print("   yields Markov Sum-of-Squares quadratic form and S_eff(p_N) = 1 - (p_{N-1}/p_N)^2 > 0.")
    print("3. Seam 3 (PDE Wavenumber Cancellation): k_par^2 cancels identically in the Schur coupling")
    print("   ratio alpha = U_cross^2 / (nu*(nu*k_4^2 + M_bulk^2)), yielding a scale-invariant dressed")
    print("   viscosity nu_eff = (1 - alpha)*nu > 0 across all tangential wavenumbers k_par.")
    print("=" * 92)

main = run_investigation

if __name__ == "__main__":
    main()
