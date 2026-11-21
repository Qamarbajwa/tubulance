"""
schur_condensation.py: Guyan-Schur Static Condensation and Multi-Tier Sensor Taring
====================================================================================
Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Status: Verified-Finite Implementation (status: verified-finite).
All Clay Millennium Problems remain strictly OPEN.
"""

import numpy as np
import scipy.linalg as la

def guyan_schur_tare(K_AA: np.ndarray, K_AB: np.ndarray, K_BB: np.ndarray, rcond: float = 1e-12) -> np.ndarray:
    """
    Computes the Guyan-Schur static condensation / Schur complement:
        K_cond = K_AA - K_AB * K_BB^{-1} * K_AB^T
    Preserves symmetry and checks conditioning of the internal DOF block K_BB.
    
    Parameters:
        K_AA : ndarray of shape (n_A, n_A) - Primary/boundary stiffness or operator block
        K_AB : ndarray of shape (n_A, n_B) - Coupling matrix between primary and omitted DOFs
        K_BB : ndarray of shape (n_B, n_B) - Omitted/internal stiffness or operator block
        rcond : float - Reciprocal condition threshold for pseudo-inverse fallback
        
    Returns:
        K_cond : ndarray of shape (n_A, n_A) - Condensed operator block with internal bulk tared
    """
    K_AA = np.asarray(K_AA, dtype=float)
    K_AB = np.asarray(K_AB, dtype=float)
    K_BB = np.asarray(K_BB, dtype=float)
    
    cond_BB = np.linalg.cond(K_BB)
    if cond_BB > 1.0 / rcond:
        K_BB_inv = la.pinv(K_BB, rcond=rcond)
        correction = K_AB @ K_BB_inv @ K_AB.T
    else:
        is_sym = np.allclose(K_BB, K_BB.T)
        X = la.solve(K_BB, K_AB.T, assume_a='sym' if is_sym else 'gen')
        correction = K_AB @ X
        
    K_cond = K_AA - correction
    if np.allclose(K_AA, K_AA.T) and np.allclose(K_BB, K_BB.T):
        K_cond = 0.5 * (K_cond + K_cond.T)
        
    return K_cond


def three_tier_sub_gap_tare(Q: np.ndarray, omega: np.ndarray, gamma_gap: float) -> np.ndarray:
    """
    Multi-tier baseline taring subtracting sub-gap bulk modes while preserving
    active edge/interface states.
    
    Given a modal representation or measurement matrix Q with spectral frequencies omega,
    this function splits the response into:
      Tier 1: Deep sub-gap bulk modes (omega < gamma_gap / 2) -> Fully subtracted (weight = 0)
      Tier 2: Near-gap boundary layer (gamma_gap / 2 <= omega <= gamma_gap) -> Smooth Hermite rolloff
      Tier 3: Active supra-gap states (omega > gamma_gap) -> Fully preserved (weight = 1)
      
    Parameters:
        Q : ndarray - Sensor covariance, transfer matrix, or state matrix
        omega : ndarray of shape (n,) - Modal frequencies or eigenvalues corresponding to basis
        gamma_gap : float - Spectral gap threshold
        
    Returns:
        Q_tared : ndarray - Tared state matrix with deep bulk modes removed
    """
    omega = np.asarray(omega, dtype=float)
    weights = np.zeros_like(omega)
    
    half_gap = gamma_gap / 2.0
    t2_mask = (omega >= half_gap) & (omega <= gamma_gap)
    t3_mask = omega > gamma_gap
    
    weights[t3_mask] = 1.0
    if np.any(t2_mask):
        xi = (omega[t2_mask] - half_gap) / (gamma_gap - half_gap)
        weights[t2_mask] = 3.0 * (xi**2) - 2.0 * (xi**3)
        
    Q = np.asarray(Q, dtype=float)
    if Q.ndim == 1:
        return Q * weights
    elif Q.shape[1] == len(omega):
        return Q * weights[np.newaxis, :]
    elif Q.shape[0] == len(omega) and Q.shape[1] == len(omega):
        W = np.diag(weights)
        return W @ Q @ W
    else:
        raise ValueError(f"Dimension mismatch between Q {Q.shape} and omega {len(omega)}")
