"""
pfaffian_routing.py: 4-Spin Torus Pfaffian Crossing Routing
===========================================================
Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Status: Verified-Finite Implementation (status: verified-finite).
All Clay Millennium Problems remain strictly OPEN.
"""

import numpy as np

def pfaffian_skew(A: np.ndarray) -> float:
    """
    Computes the Pfaffian of a 2m x 2m skew-symmetric matrix A.
    Uses skew-symmetric Parlett-Reid factorization: Pf(A)^2 = det(A).
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if n % 2 != 0:
        return 0.0
    if not np.allclose(A, -A.T, atol=1e-12):
        raise ValueError("Matrix must be skew-symmetric")
        
    if n == 2:
        return float(A[0, 1])
    elif n == 4:
        return float(A[0, 1] * A[2, 3] - A[0, 2] * A[1, 3] + A[0, 3] * A[1, 2])
    else:
        A_work = A.copy()
        pf = 1.0
        for i in range(0, n - 2, 2):
            sub_col = np.abs(A_work[i, i + 1:])
            if len(sub_col) == 0:
                break
            p = i + 1 + int(np.argmax(sub_col))
            if np.abs(A_work[i, p]) < 1e-14:
                return 0.0
            if p != i + 1:
                A_work[[i + 1, p], :] = A_work[[p, i + 1], :]
                A_work[:, [i + 1, p]] = A_work[:, [p, i + 1]]
                pf = -pf
            val = A_work[i, i + 1]
            pf *= val
            for j in range(i + 2, n):
                mult = A_work[i, j] / val
                A_work[j, :] -= mult * A_work[i + 1, :]
                A_work[:, j] -= mult * A_work[:, i + 1]
        pf *= A_work[n - 2, n - 1]
        return float(pf)


def four_spin_torus_pfaffian_count(
    A_pp: np.ndarray, 
    A_pm: np.ndarray, 
    A_mp: np.ndarray, 
    A_mm: np.ndarray
) -> dict:
    """
    Computes the 4-spin torus Pfaffian linear combination:
        N_cross = (Pf(A_{++}) + Pf(A_{+-}) + Pf(A_{-+}) - Pf(A_{--})) / 2
    for non-planar crossing and topological embedding (e.g., K_{3,3} bipartite graph on torus).
    
    Parameters:
        A_pp : ndarray - Skew-symmetric adjacency matrix with periodic boundary (+, +)
        A_pm : ndarray - Skew-symmetric adjacency matrix with anti-periodic boundary (+, -)
        A_mp : ndarray - Skew-symmetric adjacency matrix with anti-periodic boundary (-, +)
        A_mm : ndarray - Skew-symmetric adjacency matrix with anti-periodic boundary (-, -)
        
    Returns:
        dict containing:
            "pf_pp": float
            "pf_pm": float
            "pf_mp": float
            "pf_mm": float
            "torus_crossing_count": float
            "resolved_crossing_parity": int
    """
    pf_pp = pfaffian_skew(A_pp)
    pf_pm = pfaffian_skew(A_pm)
    pf_mp = pfaffian_skew(A_mp)
    pf_mm = pfaffian_skew(A_mm)
    
    n_cross = (pf_pp + pf_pm + pf_mp - pf_mm) / 2.0
    
    return {
        "pf_pp": pf_pp,
        "pf_pm": pf_pm,
        "pf_mp": pf_mp,
        "pf_mm": pf_mm,
        "torus_crossing_count": float(n_cross),
        "resolved_crossing_parity": int(round(n_cross)) % 2
    }
