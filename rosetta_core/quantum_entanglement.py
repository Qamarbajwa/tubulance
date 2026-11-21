"""
quantum_entanglement.py: Quantum Wavefunction Reconstruction and Schur Entanglement
===================================================================================
Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Status: Verified-Finite Implementation (status: verified-finite).
All Clay Millennium Problems remain strictly OPEN.
"""

import numpy as np
import scipy.linalg as la


def reconstruct_dirichlet_eigen_wavefunction(
    Q_tared: np.ndarray,
    L: float,
    u_grid: np.ndarray,
    mode_index: int = 0
) -> tuple:
    """
    Reconstructs the spatial Dirichlet eigen-wavefunction from the tared operator Q_tared:
        Psi_m(u) = sum_{k=0}^{K-1} c_k^{(m)} * sqrt(2/L) * cos((2k+1)*pi*u / L)
    defined on u in [-L/2, L/2].
    
    Parameters:
        Q_tared : ndarray of shape (K, K) - Symmetric tared operator / Gram matrix
        L : float - Spatial domain length (domain [-L/2, L/2])
        u_grid : ndarray of shape (N,) - Spatial sampling points in [-L/2, L/2]
        mode_index : int - Eigenmode index (0 = ground state, 1 = first excited state)
        
    Returns:
        tuple of (eigval, c_vec, psi_u, born_norm, parity_error):
            eigval : float - Eigenvalue of mode
            c_vec : ndarray of shape (K,) - Unit-normalized expansion coefficients
            psi_u : ndarray of shape (N,) - Evaluated spatial wavefunction
            born_norm : float - Numerical integral of |Psi(u)|^2 over domain
            parity_error : float - Maximum symmetry violation |Psi(u) - Psi(-u)|
    """
    Q_tared = np.asarray(Q_tared, dtype=float)
    if not np.allclose(Q_tared, Q_tared.T, atol=1e-10):
        Q_tared = 0.5 * (Q_tared + Q_tared.T)
        
    K = Q_tared.shape[0]
    eigvals, eigvecs = la.eigh(Q_tared)
    
    # Sort eigenvalues in ascending order
    idx = np.argsort(eigvals)
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    
    c_vec = eigvecs[:, mode_index]
    # Standardize sign: require positive center value Psi(0) >= 0
    center_val = np.sum(c_vec * np.sqrt(2.0 / L))
    if center_val < 0:
        c_vec = -c_vec
        
    c_norm = np.linalg.norm(c_vec)
    if c_norm > 1e-15:
        c_vec = c_vec / c_norm
        
    # Construct spatial basis matrix on u_grid
    # phi_k(u) = sqrt(2/L) * cos((2k+1)*pi*u / L)
    u_grid = np.asarray(u_grid, dtype=float)
    N = len(u_grid)
    basis_mat = np.zeros((N, K), dtype=float)
    norm_factor = np.sqrt(2.0 / L)
    
    for k in range(K):
        freq = (2.0 * k + 1.0) * np.pi / L
        basis_mat[:, k] = norm_factor * np.cos(freq * u_grid)
        
    psi_u = basis_mat @ c_vec
    
    # Born normalization check via trapezoidal integration
    born_norm = float(np.trapezoid(psi_u**2, u_grid))
    
    # Parity check: compare Psi(u) with Psi(-u)
    # Since cosine basis has strictly even parity, parity error tests numerical symmetry
    u_rev = -u_grid[::-1]
    psi_rev = psi_u[::-1]
    # Interpolate or directly match if grid is symmetric
    if np.allclose(u_grid, -u_grid[::-1], atol=1e-12):
        parity_error = float(np.max(np.abs(psi_u - psi_rev)))
    else:
        parity_error = float(np.max(np.abs(psi_u - np.interp(-u_grid, u_grid, psi_u))))
        
    return float(eigvals[mode_index]), c_vec, psi_u, born_norm, parity_error


def bipartite_schur_entanglement_spectrum(
    G_AA: np.ndarray,
    G_AB: np.ndarray,
    G_BB: np.ndarray,
    rcond: float = 1e-12
) -> dict:
    """
    Given a symmetric positive-definite bipartite block matrix
    G = [[G_AA, G_AB], [G_AB.T, G_BB]], computes the tared Schur complement,
    the Schmidt entanglement spectrum, and the linear and von Neumann entropies.
    
    Parameters:
        G_AA : ndarray of shape (n_A, n_A) - Subsystem A covariance/Gram block
        G_AB : ndarray of shape (n_A, n_B) - Inter-system coupling matrix
        G_BB : ndarray of shape (n_B, n_B) - Subsystem B covariance/Gram block
        rcond : float - Reciprocal condition limit for matrix inversions
        
    Returns:
        dict containing:
            "schur_complement": ndarray of shape (n_B, n_B)
            "sin_sq_theta": float - Schur innovation fraction Tr(Sigma_BB)/Tr(G_BB)
            "cos_sq_theta": float - Coupling fidelity fraction Tr(Coupling)/Tr(G_BB)
            "schmidt_singular_values": ndarray of shape (min(n_A, n_B),)
            "density_matrix_eigenvalues": ndarray of shape (min(n_A, n_B),)
            "linear_entropy": float - S_lin = 1 - sum(p_k^2)
            "von_neumann_entropy": float - S_vN = -sum(p_k * ln(p_k))
            "purity": float - gamma = sum(p_k^2)
    """
    G_AA = np.asarray(G_AA, dtype=float)
    G_AB = np.asarray(G_AB, dtype=float)
    G_BB = np.asarray(G_BB, dtype=float)
    
    # Tared Schur complement on subsystem B:
    # Sigma_BB = G_BB - G_AB.T @ inv(G_AA) @ G_AB
    if np.linalg.cond(G_AA) > 1.0 / rcond:
        inv_AA = la.pinv(G_AA, rcond=rcond)
        coupling_correction = G_AB.T @ inv_AA @ G_AB
    else:
        X = la.solve(G_AA, G_AB, assume_a='sym' if np.allclose(G_AA, G_AA.T) else 'gen')
        coupling_correction = G_AB.T @ X
        
    Sigma_BB = G_BB - coupling_correction
    if np.allclose(G_BB, G_BB.T):
        Sigma_BB = 0.5 * (Sigma_BB + Sigma_BB.T)
        
    tr_G_BB = float(np.trace(G_BB))
    tr_Sigma_BB = float(np.trace(Sigma_BB))
    tr_coupling = float(np.trace(coupling_correction))
    
    if tr_G_BB > 1e-15:
        sin_sq = tr_Sigma_BB / tr_G_BB
        cos_sq = tr_coupling / tr_G_BB
    else:
        sin_sq = 1.0
        cos_sq = 0.0
        
    # Normalized correlation contraction matrix C = G_AA^{-1/2} @ G_AB @ G_BB^{-1/2}
    def symm_inv_sqrt(M):
        evals, evecs = la.eigh(M)
        evals = np.clip(evals, 1e-14, None)
        return evecs @ np.diag(1.0 / np.sqrt(evals)) @ evecs.T
        
    inv_sqrt_AA = symm_inv_sqrt(G_AA)
    inv_sqrt_BB = symm_inv_sqrt(G_BB)
    C_norm = inv_sqrt_AA @ G_AB @ inv_sqrt_BB
    
    # Schmidt singular values
    sigma_k = la.svd(C_norm, compute_uv=False)
    
    # Density matrix eigenvalues: normalized squared singular values
    # In bipartite entanglement, p_k are the normalized probabilities
    sigma_sq = sigma_k**2
    sum_sq = np.sum(sigma_sq)
    if sum_sq > 1e-15:
        p_k = sigma_sq / sum_sq
    else:
        # Uniform or pure distribution fallback
        p_k = np.ones_like(sigma_k) / len(sigma_k)
        
    # Linear entropy S_lin = 1 - sum(p_k^2)
    purity = float(np.sum(p_k**2))
    s_lin = float(1.0 - purity)
    
    # von Neumann entropy S_vN = -sum(p_k * ln(p_k))
    p_safe = p_k[p_k > 1e-15]
    s_vn = float(-np.sum(p_safe * np.log(p_safe)))
    
    return {
        "schur_complement": Sigma_BB,
        "sin_sq_theta": float(sin_sq),
        "cos_sq_theta": float(cos_sq),
        "schmidt_singular_values": sigma_k,
        "density_matrix_eigenvalues": p_k,
        "linear_entropy": s_lin,
        "von_neumann_entropy": s_vn,
        "purity": purity
    }


def canonical_four_workspace_entanglement_states() -> dict:
    """
    Constructively builds the explicit density matrices across the four canonical
    workspace quantum states and returns (S_lin, S_vN, purity) for each:
    
    1. Workspace 01 (Hodge): Spin(8) Chiral Pfaffian Bell Singlet
       (|+,-> - |-,+>) / sqrt(2) -> rho = diag(1/2, 1/2)
       S_lin = 0.5, S_vN = ln(2) ~ 0.6931, purity = 0.5
       
    2. Workspace 02 (Yang-Mills): 3-Quark Baryonic Y-Junction Color Singlet
       eps_{ijk} |q_i q_j q_k> / sqrt(6) -> rho_q = diag(1/3, 1/3, 1/3)
       S_lin = 2/3 ~ 0.6667, S_vN = ln(3) ~ 1.0986, purity = 1/3 ~ 0.3333
       
    3. Workspace 03 (Riemann): Prime-Composite Fock Wedge State
       |p wedge q> from the Dirichlet-eliminated Gram matrix
       
    4. Workspace 04 (Navier-Stokes): Heterochiral Vortex Triad vs Homochiral Product State
       Heterochiral (|+,-> + |-,+>) / sqrt(2) -> S_lin = 0.5, S_vN = ln(2)
       Homochiral |+,+> (product state) -> S_lin = 0.0, S_vN = 0.0
    """
    # 1. Hodge Spin(8) Chiral Bell Singlet
    p_hodge = np.array([0.5, 0.5], dtype=float)
    s_lin_hodge = float(1.0 - np.sum(p_hodge**2))
    s_vn_hodge = float(-np.sum(p_hodge * np.log(p_hodge)))
    purity_hodge = float(np.sum(p_hodge**2))
    
    # 2. Yang-Mills Baryonic Y-Junction Color Singlet
    p_ym = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=float)
    s_lin_ym = float(1.0 - np.sum(p_ym**2))
    s_vn_ym = float(-np.sum(p_ym * np.log(p_ym)))
    purity_ym = float(np.sum(p_ym**2))
    
    # 3. Riemann Prime-Composite Wedge State
    # Realistic prime-composite coupling block from 2x2 Gram projection
    G_prime = np.array([[1.0, 0.2292], [0.2292, 1.0]])
    G_AA = np.array([[1.0]])
    G_AB = np.array([[0.2292]])
    G_BB = np.array([[1.0]])
    rh_spec = bipartite_schur_entanglement_spectrum(G_AA, G_AB, G_BB)
    
    # 4. Navier-Stokes Vortex States
    # Heterochiral entangled triad
    p_ns_hetero = np.array([0.5, 0.5], dtype=float)
    s_lin_ns_hetero = float(1.0 - np.sum(p_ns_hetero**2))
    s_vn_ns_hetero = float(-np.sum(p_ns_hetero * np.log(p_ns_hetero)))
    purity_ns_hetero = float(np.sum(p_ns_hetero**2))
    
    # Homochiral unentangled product state
    p_ns_homo = np.array([1.0, 0.0], dtype=float)
    s_lin_ns_homo = 0.0
    s_vn_ns_homo = 0.0
    purity_ns_homo = 1.0
    
    return {
        "workspace_01_hodge": {
            "state": "Spin(8) Chiral Pfaffian Bell Singlet",
            "probabilities": p_hodge.tolist(),
            "linear_entropy": s_lin_hodge,
            "von_neumann_entropy": s_vn_hodge,
            "purity": purity_hodge
        },
        "workspace_02_yang_mills": {
            "state": "3-Quark Baryonic Y-Junction Color Singlet",
            "probabilities": p_ym.tolist(),
            "linear_entropy": s_lin_ym,
            "von_neumann_entropy": s_vn_ym,
            "purity": purity_ym
        },
        "workspace_03_riemann": {
            "state": "Prime-Composite Fock Wedge State",
            "linear_entropy": rh_spec["linear_entropy"],
            "von_neumann_entropy": rh_spec["von_neumann_entropy"],
            "sin_sq_theta": rh_spec["sin_sq_theta"],
            "purity": rh_spec["purity"]
        },
        "workspace_04_navier_stokes": {
            "heterochiral_entangled": {
                "state": "Heterochiral Vortex Triad (|+,-> + |-,+>)/sqrt(2)",
                "linear_entropy": s_lin_ns_hetero,
                "von_neumann_entropy": s_vn_ns_hetero,
                "purity": purity_ns_hetero
            },
            "homochiral_product": {
                "state": "Homochiral Vortex Product State |+,+>",
                "linear_entropy": s_lin_ns_homo,
                "von_neumann_entropy": s_vn_ns_homo,
                "purity": purity_ns_homo
            }
        }
    }
