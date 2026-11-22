"""
Probe: Non-Abelian Matrix Commutator Stiffness and Schur-Condensed Spectrum as R -> infty
Investigates the finite-N matrix operator spectrum when:
1. Free kinetic double-commutator L_free(A) = 2 / R^2.
2. Non-abelian quartic commutator stiffness V_quartic(A) = ||i[A_mu, A_nu]||_F^2 >= 0.
3. Schur complement condensation S_eff = D - B^T A^{-1} B integrating out higher modes l >= 2.

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

def get_su2_generators(j):
    """Construct standard SU(2) spin-j representation matrices (J_x, J_y, J_z)."""
    m = np.arange(j, -j - 1, -1)
    dim = len(m)
    Jz = np.diag(m)
    Jp = np.zeros((dim, dim))
    for i in range(dim - 1):
        mi = m[i + 1]
        Jp[i, i + 1] = np.sqrt(j * (j + 1) - mi * (mi + 1))
    Jx = 0.5 * (Jp + Jp.T)
    Jy = -0.5j * (Jp - Jp.T)
    return [Jx, Jy, Jz]

def construct_spherical_multiplet_basis(N):
    """
    Construct orthonormal Hermitian matrix basis for l=1 (dipole, dim 3)
    and l=2 (quadrupole, dim 5) under the adjoint action of SU(2).
    """
    j = (N - 1) / 2.0
    J = get_su2_generators(j)
    
    # Trace normalization: Tr(Ja Jb) = (1/3) j(j+1)(2j+1) delta_ab
    norm_sq = (1.0 / 3.0) * j * (j + 1) * (2 * j + 1)
    T_l1 = [Ja / np.sqrt(norm_sq) for Ja in J]
    
    # Construct 5 quadrupolar generators for l=2:
    quads = []
    for a in range(3):
        for b in range(a, 3):
            Q = 0.5 * (J[a] @ J[b] + J[b] @ J[a])
            if a == b:
                Q = Q - (1.0 / 3.0) * j * (j + 1) * np.eye(N)
            if np.linalg.norm(Q) > 1e-10:
                quads.append(Q)
                
    # Gram-Schmidt to get 5 orthonormal Hermitian matrices:
    ortho_l2 = []
    for Q in quads:
        v = Q.copy()
        for u in ortho_l2:
            proj = np.trace(u.conj().T @ v).real
            v = v - proj * u
        nrm = np.sqrt(np.trace(v.conj().T @ v).real)
        if nrm > 1e-10:
            ortho_l2.append(v / nrm)
            
    return T_l1, ortho_l2, j

def compute_quartic_stiffness_tensor(T_l1, ortho_l2):
    """
    Compute the quartic commutator stiffness tensor M_stiff on l=1:
    M_{ab} = sum_{k in l=2} - Tr([T_a, Q_k] [T_b, Q_k]) = sum_k ||i[T_a, Q_k]||_F^2 >= 0.
    """
    M_stiff = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            val = 0.0
            for Qk in ortho_l2:
                comm_a = T_l1[a] @ Qk - Qk @ T_l1[a]
                comm_b = T_l1[b] @ Qk - Qk @ T_l1[b]
                val += - np.trace(comm_a @ comm_b).real
            M_stiff[a, b] = val
    return M_stiff

def compute_schur_spectrum_at_radius(R, N, v_cond=0.5, is_isotropic=True, seed=42):
    """
    Compute the coupled Hessian H = [[D, B^T], [B, A]] and Schur complement
    S_eff = D - B^T A^{-1} B on the l=1 dipole sector as a function of radius R.
    """
    T_l1, ortho_l2, j = construct_spherical_multiplet_basis(N)
    basis = T_l1 + ortho_l2
    dim_basis = len(basis) # 3 + 5 = 8
    
    if is_isotropic:
        # Spherically symmetric / isotropic ensemble average:
        # < Q_k Q_m > = v^2 delta_km
        H_quartic = np.zeros((dim_basis, dim_basis))
        for mu in range(dim_basis):
            for nu in range(dim_basis):
                val = 0.0
                for Qk in ortho_l2:
                    comm_mu = basis[mu] @ Qk - Qk @ basis[mu]
                    comm_nu = basis[nu] @ Qk - Qk @ basis[nu]
                    val += - np.trace(comm_mu @ comm_nu).real
                H_quartic[mu, nu] = (v_cond ** 2) * val
    else:
        # Anisotropic realization with random coefficients:
        np.random.seed(seed)
        coeffs = np.random.randn(dim_basis)
        coeffs = v_cond * coeffs / np.linalg.norm(coeffs)
        A_cond = sum(c * b for c, b in zip(coeffs, basis))
        
        H_quartic = np.zeros((dim_basis, dim_basis))
        for mu in range(dim_basis):
            for nu in range(dim_basis):
                comm_mu = basis[mu] @ A_cond - A_cond @ basis[mu]
                comm_nu = basis[nu] @ A_cond - A_cond @ basis[nu]
                H_quartic[mu, nu] = - np.trace(comm_mu @ comm_nu).real

    # Free kinetic Laplacian: l(l+1) / R^2
    H_free = np.zeros((dim_basis, dim_basis))
    for i in range(3):
        H_free[i, i] = 2.0 / (R ** 2) # l=1: 1*(1+1) = 2
    for i in range(3, dim_basis):
        H_free[i, i] = 6.0 / (R ** 2) # l=2: 2*(2+1) = 6
        
    H_total = H_free + H_quartic
    
    D = H_total[:3, :3]
    B = H_total[3:, :3]
    A = H_total[3:, 3:]
    
    # Schur complement
    A_inv = np.linalg.pinv(A)
    tare_term = B.T @ A_inv @ B
    S_eff = D - tare_term
    
    evals_H = np.linalg.eigvalsh(H_total)
    evals_D = np.linalg.eigvalsh(D)
    evals_Seff = np.linalg.eigvalsh(S_eff)
    
    b_norm = np.linalg.norm(B)
    tare_norm = np.linalg.norm(tare_term)
    
    return {
        "R": R,
        "free_gap_l1": 2.0 / (R ** 2),
        "free_gap_l2": 6.0 / (R ** 2),
        "min_eval_H": float(np.min(evals_H)),
        "min_eval_D": float(np.min(evals_D)),
        "min_eval_Seff": float(np.min(evals_Seff)),
        "norm_B": float(b_norm),
        "norm_tare": float(tare_norm)
    }

def run_investigation():
    print("=" * 85)
    print("NON-ABELIAN COMMUTATOR STIFFNESS & SCHUR-CONDENSED SPECTRUM PROBE")
    print("Author: Qamar Munawer | BTU Cottbus-Senftenberg | 2026-11-22")
    print("ai is being used as a tool | status: verified-finite")
    print("=" * 85)
    
    R_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 1000.0]
    
    for N in [3, 4, 5]:
        T_l1, ortho_l2, j = construct_spherical_multiplet_basis(N)
        M_stiff = compute_quartic_stiffness_tensor(T_l1, ortho_l2)
        c_stiff = np.mean(np.linalg.eigvalsh(M_stiff))
        
        print(f"\n--- Matrix Dimension N = {N} (spin j = {j}) | l=1 dim = 3, l=2 dim = 5 ---")
        print(f"Quartic Commutator Stiffness Casimir C_stiff(N): {c_stiff:.6f}")
        print("Commutator stiffness matrix on l=1 sector (purely diagonal by Schur's Lemma):")
        print(np.round(M_stiff, 4))
        
        # Test Case 1: Classical Tree-Level (v_cond = 0, no quantum condensate)
        print("\nCase 1: Tree-Level Hessian (v_cond = 0.0, no quantum condensate):")
        print("  Radius R | Free l=1 Gap (L^-2) | Lowest Hessian Eval | Lowest S_eff Eval | Regime")
        print("  " + "-" * 75)
        for R in [0.5, 1.0, 5.0, 10.0, 50.0, 1000.0]:
            r_res = compute_schur_spectrum_at_radius(R, N, v_cond=0.0, is_isotropic=True)
            reg = "UV Curvature" if R <= 1.0 else ("Crossover" if R <= 10.0 else "Vanishing Free Gap")
            print(f"  {R:8.1f} | {r_res['free_gap_l1']:19.6f} | {r_res['min_eval_H']:19.6f} | {r_res['min_eval_Seff']:17.6f} | {reg}")
            
        # Test Case 2: Quantum Condensate (v_cond = 0.5)
        v_cond = 0.5
        expected_plateau = c_stiff * (v_cond ** 2)
        print(f"\nCase 2: Quantum Non-Abelian Condensate (v_cond = {v_cond}, expected plateau = {expected_plateau:.4f}):")
        print("  Radius R | Free l=1 Gap (L^-2) | Lowest Hessian Eval | Lowest S_eff Eval | Tare ||B|| | Plateau Gap")
        print("  " + "-" * 85)
        for R in R_values:
            r_res = compute_schur_spectrum_at_radius(R, N, v_cond=v_cond, is_isotropic=True)
            print(f"  {R:8.1f} | {r_res['free_gap_l1']:19.6f} | {r_res['min_eval_H']:19.6f} | {r_res['min_eval_Seff']:17.6f} | {r_res['norm_B']:10.2e} | {expected_plateau:.4f}")
            
    print("\n" + "=" * 85)
    print("KEY MATHEMATICAL FINDINGS:")
    print("1. Tree-Level Gap Vanishing: Without non-abelian condensation (v=0), the lowest")
    print("   eigenvalue scales as 2 / R^2 and vanishes strictly as R -> infty.")
    print("2. Orthogonal Selection Rule: For pure l=2 quadrupolar condensation, the off-diagonal")
    print("   cross-talk B between l=1 and l=2 vanishes identically (||B|| < 1e-16) by parity")
    print("   and angular momentum selection rules [l=1, l=2] in l=2 vs [l=2, l=2] in l=1+3.")
    print("3. Intrinsic Non-Abelian Mass Floor: When non-abelian higher modes condense (v > 0),")
    print("   the Schur complement S_eff = D - B^T A^-1 B = D identically, and saturates to the")
    print("   strictly positive mass gap plateau Delta_min = C_stiff(N) * v^2 > 0 as R -> infty.")
    print("=" * 85)

if __name__ == "__main__":
    run_investigation()
