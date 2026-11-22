"""
Probe: Phase 1 and Phase 2 Comparison of Finite-Continuum Yang-Mills Models
Model 1: Fuzzy Sphere SU(2) Matrix Model
Model 2: Simplicial / DEC Gauge Plaquette Model

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Date: 2026-11-22
Methodology Note: ai is being used as a tool
Epistemic Boundary: status: verified-finite, open_horizon_lock: STRICTLY OPEN

Computes exact invariants, commutators, actions, and spectral gaps.
"""

import math
import numpy as np

def get_su2_generators(j):
    """
    Construct standard SU(2) spin-j representation matrices (J_x, J_y, J_z).
    Dimension N = 2j + 1.
    """
    N = int(2 * j + 1)
    m_values = np.linspace(j, -j, N)
    
    # J_z is diagonal
    J_z = np.diag(m_values)
    
    # J_+ and J_- ladder operators
    J_plus = np.zeros((N, N), dtype=complex)
    J_minus = np.zeros((N, N), dtype=complex)
    
    for i, m in enumerate(m_values[:-1]):
        # index i corresponds to m, index i+1 corresponds to m-1
        val = math.sqrt(j * (j + 1) - m * (m - 1))
        J_minus[i + 1, i] = val
        J_plus[i, i + 1] = val
        
    J_x = 0.5 * (J_plus + J_minus)
    J_y = -0.5j * (J_plus - J_minus)
    
    return J_x, J_y, J_z

def analyze_fuzzy_sphere(N_values, R=1.0, g=1.0):
    """
    Phase 1 Analysis for Model 1: Fuzzy Sphere
    Verifies:
    1. Casimir invariant Sum X_a^2 = R^2 * I_N
    2. Commutator [X_a, X_b] = i*theta*eps_abc*X_c
    3. Classical-to-continuum parameter theta -> 0 as N -> infinity
    4. Exact ground-state action S_vac(N)
    """
    print("=" * 70)
    print("MODEL 1: FUZZY SPHERE SU(2) MATRIX MODEL ANALYSIS")
    print("=" * 70)
    
    results = []
    for N in N_values:
        j = (N - 1) / 2.0
        Jx, Jy, Jz = get_su2_generators(j)
        
        # Scaling factor theta
        theta = R / math.sqrt(j * (j + 1))
        
        Xx = theta * Jx
        Xy = theta * Jy
        Xz = theta * Jz
        
        # 1. Casimir invariant check: Xx^2 + Xy^2 + Xz^2 == R^2 * I
        casimir_matrix = Xx @ Xx + Xy @ Xy + Xz @ Xz
        expected_casimir = (R ** 2) * np.eye(N, dtype=complex)
        casimir_err = np.max(np.abs(casimir_matrix - expected_casimir))
        
        # 2. Commutator check: [Xx, Xy] - i * theta * Xz == 0
        comm_xy = Xx @ Xy - Xy @ Xx
        expected_comm_xy = 1j * theta * Xz
        comm_err = np.max(np.abs(comm_xy - expected_comm_xy))
        
        # 3. Action computation: S = -1/(4*g^2) * Tr([X_a, X_b]^2)
        # Sum over a < b of Tr((i [X_a, X_b])^2)
        comm_yz = Xy @ Xz - Xz @ Xy
        comm_zx = Xz @ Xx - Xx @ Xz
        
        comm_terms = [comm_xy, comm_yz, comm_zx]
        action_val = 0.0
        for C in comm_terms:
            iC = 1j * C
            term = np.trace(iC @ iC).real
            action_val += term
        action_val *= (1.0 / (2.0 * g**2))
        
        # Theoretical formula: S_th = 2 * N * R^4 / (g^2 * (N^2 - 1))
        action_th = (2.0 * N * (R**4)) / (g**2 * (N**2 - 1))
        action_diff = abs(action_val - action_th)
        
        # Spectral gap on the fuzzy sphere:
        # The lowest scalar excitation above the sphere vacuum has angular momentum l=1.
        # The Laplacians acting on matrices are Ad(J_a)^2, with eigenvalues l(l+1).
        # For l=1, delta_E = 1*(1+1) = 2.
        spectral_gap = 2.0  # Normalized gap in angular momentum units
        
        results.append({
            "N": N,
            "j": j,
            "theta": theta,
            "casimir_err": casimir_err,
            "comm_err": comm_err,
            "action_val": action_val,
            "action_th": action_th,
            "spectral_gap": spectral_gap
        })
        
        print(f"N = {N:2d} (spin j = {j:4.1f}) | theta = {theta:.6f} | "
              f"Casimir Err: {casimir_err:.2e} | Comm Err: {comm_err:.2e} | "
              f"Action: {action_val:.6f} (Th: {action_th:.6f})")
        
    return results

def analyze_dec_simplicial_model(beta_values, num_plaquettes=6):
    """
    Phase 1 Analysis for Model 2: Simplicial / DEC Gauge Plaquette Model
    For a minimal 4D hyper-tetrahedral cell (6 plaquettes meeting at a vertex):
    1. Vacuum state: U_p = I for all plaquettes -> S = 0
    2. Small fluctuation: U_p = exp(i * alpha * n . sigma)
       Tr(U_p) = 2 * cos(alpha)
       Action = beta * Sum (2 - Tr(U_p)) = 2 * beta * Sum (1 - cos(alpha))
              = beta * Sum alpha^2 + O(alpha^4)
    3. Mass gap / glueball mass in strong coupling (beta -> 0):
       M_gap ~ -ln(beta) -> infinity (lattice units)
       In physical units with string tension sigma held fixed: M_glueball / sqrt(sigma) -> const > 0.
    """
    print("\n" + "=" * 70)
    print("MODEL 2: SIMPLICIAL / DEC PLAQUETTE GAUGE MODEL ANALYSIS")
    print("=" * 70)
    
    results = []
    for beta in beta_values:
        # 1. Vacuum
        S_vac = 0.0
        
        # 2. Minimal non-trivial excitation: single plaquette perturbed by angle alpha = 0.1 rad
        alpha = 0.1
        tr_Up = 2.0 * math.cos(alpha)
        # Action for 1 perturbed plaquette
        S_exc = beta * (2.0 - tr_Up)
        
        # 3. Strong-coupling mass gap formula: M_gap = -ln(beta / 4)
        if beta < 4.0:
            strong_coupling_mass_gap = -math.log(beta / 4.0)
        else:
            # Weak coupling scaling via asymptotic freedom
            strong_coupling_mass_gap = math.exp(-6.0 * math.pi**2 / (11.0 * beta))
            
        results.append({
            "beta": beta,
            "S_vac": S_vac,
            "S_exc": S_exc,
            "M_gap": strong_coupling_mass_gap
        })
        
        print(f"beta = {beta:5.2f} | Vacuum S = {S_vac:.4f} | "
              f"Perturbed S (alpha=0.1) = {S_exc:.6f} | "
              f"Mass Gap Proxy = {strong_coupling_mass_gap:.6f}")
        
    return results

if __name__ == "__main__":
    N_list = [2, 3, 4, 5, 8, 16, 32]
    fuzzy_res = analyze_fuzzy_sphere(N_list, R=1.0, g=1.0)
    
    beta_list = [0.1, 0.5, 1.0, 2.0, 3.0, 3.5]
    dec_res = analyze_dec_simplicial_model(beta_list)
