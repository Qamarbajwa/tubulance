"""
Phase 3 Analysis: 4D Matrix Gauge Model Scaling to the Continuum.
Simulates a 4D Yang-Mills matrix model on the chiral product fuzzy manifold
S^2_{n,L} x S^2_{n,R} under the chiral split so(4) = su(2)_L + su(2)_R.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Date: 2026-11-22
Methodology Note: ai is being used as a tool
Epistemic Boundary: status: verified-finite, open_horizon_lock: STRICTLY OPEN.

For matrix dimension N = n^2 in {4, 9, 16} with n in {2, 3, 4}:
Each su(2) factor has spin j = (n - 1) / 2 and exact quadratic Casimir:
C_2(j) = j * (j + 1) = (n^2 - 1) / 4 = (N - 1) / 4.
The physical derivative metric factor is theta^-2 = (N - 1) / (4 * R^2).
The unscaled matrix gap is Delta_N = 4 / (N - 1).
The product theta^-2 * Delta_N = 1 / R^2 is representation-theoretically exact.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
import numpy as np

def get_su2_generators(j):
    """
    Construct standard su(2) spin-j representation matrices (J_x, J_y, J_z).
    Dimension n = 2j + 1.
    """
    n = int(2 * j + 1)
    m_values = np.linspace(j, -j, n)
    
    J_z = np.diag(m_values)
    J_plus = np.zeros((n, n), dtype=complex)
    J_minus = np.zeros((n, n), dtype=complex)
    
    for i, m in enumerate(m_values[:-1]):
        val = math.sqrt(j * (j + 1) - m * (m - 1))
        J_minus[i + 1, i] = val
        J_plus[i, i + 1] = val
        
    J_x = 0.5 * (J_plus + J_minus)
    J_y = -0.5j * (J_plus - J_minus)
    
    return J_x, J_y, J_z

def construct_4d_fuzzy_geometry(N):
    """
    Construct the 4D chiral product fuzzy manifold S^2_{n,L} x S^2_{n,R}.
    Total matrix dimension N = n^2.
    For n in {2, 3, 4}, N in {4, 9, 16}.
    Left su(2)_L acts on the first tensor factor.
    Right su(2)_R acts on the second tensor factor.
    """
    n = int(round(math.sqrt(N)))
    assert n * n == N, "Matrix dimension N must be a square n^2 for S^2_L x S^2_R"
    
    j = (n - 1) / 2.0
    Jx, Jy, Jz = get_su2_generators(j)
    
    # Exact Casimir of each su(2) factor: C_2 = (n^2 - 1)/4 = (N - 1)/4
    casimir_exact = (N - 1) / 4.0
    theta = 1.0 / math.sqrt(casimir_exact) if casimir_exact > 0 else 1.0
    
    # Left chiral coordinates (L_1, L_2)
    L1 = np.kron(Jx, np.eye(n)) * theta
    L2 = np.kron(Jy, np.eye(n)) * theta
    # Right chiral coordinates (R_1, R_2)
    R1 = np.kron(np.eye(n), Jx) * theta
    R2 = np.kron(np.eye(n), Jy) * theta
    
    return [L1, L2, R1, R2], theta

def compute_fluctuation_spectrum(matrices):
    """
    Compute the kinetic fluctuation super-operator L(A) = Sum [X_mu, [X_mu, A]].
    Acting on the N^2-dimensional Hilbert-Schmidt matrix space.
    Returns sorted eigenvalues.
    """
    N = matrices[0].shape[0]
    dim = N * N
    
    L_matrix = np.zeros((dim, dim), dtype=complex)
    I_N = np.eye(N, dtype=complex)
    
    for X in matrices:
        ad_X = np.kron(I_N, X) - np.kron(X.T, I_N)
        L_matrix += ad_X @ ad_X
        
    eigenvalues = np.linalg.eigvalsh(L_matrix)
    eigenvalues = np.sort(np.real(eigenvalues))
    
    return eigenvalues

def run_phase3_scaling():
    print("=" * 75)
    print("PHASE 3: 4D CHIRAL PRODUCT FUZZY MANIFOLD S^2_L x S^2_R SCALING")
    print("Author: Qamar Munawer | BTU Cottbus-Senftenberg | 2026-11-22")
    print("ai is being used as a tool | status: verified-finite")
    print("=" * 75)
    
    N_list = [4, 9, 16]
    results = []
    
    for N in N_list:
        matrices, theta = construct_4d_fuzzy_geometry(N)
        evals = compute_fluctuation_spectrum(matrices)
        
        zero_modes = np.sum(np.isclose(evals, 0.0, atol=1e-8))
        non_zero_evals = evals[evals > 1e-6]
        
        if len(non_zero_evals) > 0:
            spectral_gap = non_zero_evals[0]
            max_eval = evals[-1]
        else:
            spectral_gap = 0.0
            max_eval = 0.0
            
        uv_ir_ratio = max_eval / spectral_gap if spectral_gap > 0 else 0.0
        
        results.append({
            "N": N,
            "theta": theta,
            "zero_modes": zero_modes,
            "spectral_gap": spectral_gap,
            "max_eval": max_eval,
            "uv_ir_ratio": uv_ir_ratio
        })
        
        print(f"Matrix Dimension N = {N:2d} (n = {int(math.sqrt(N))}) | State Space: {N*N:3d} | theta = {theta:.4f}")
        print(f"  * Unique Vacuum Stillness (Zero Modes): {zero_modes}")
        print(f"  * Unscaled Matrix Gap Delta_N = 4 / (N - 1): {spectral_gap:.6f}")
        print(f"  * Intrinsic UV Cutoff Lambda_max: {max_eval:.6f}")
        print(f"  * Physical Gap Delta_phys = theta^-2 * Delta_N = 1 / R^2: {theta**(-2) * spectral_gap:.4f} / R^2")
        print("-" * 75)
        
    return results

if __name__ == "__main__":
    run_phase3_scaling()
