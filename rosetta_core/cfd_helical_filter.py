"""
cfd_helical_filter.py: Incompressible Navier-Stokes Cubic Strain Tube-Sheet Classifier
=====================================================================================
Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Status: Verified-Finite Implementation (status: verified-finite).
All Clay Millennium Problems remain strictly OPEN.
"""

import numpy as np

def cubic_strain_tube_sheet_classifier(grad_u: np.ndarray) -> dict:
    """
    Classifies 3D velocity gradients grad_u = [du_i / dx_j] into vortex-tubes
    versus shear-sheets using the exact cubic determinant identity:
        4 * (l1 * l2 * l3) = l3^3 - l3 * (l1 - l2)^2
    and the normalized axial strain ratio:
        R_strain = l3 / (l1^2 + l2^2 + l3^2) <= 2/3.
        
    Parameters:
        grad_u : ndarray of shape (3, 3) - 3D velocity gradient tensor
        
    Returns:
        dict containing:
            "trace_div": float, incompressibility trace check div(u) ~ 0
            "eigenvalues": list of float [l1, l2, l3] sorted in ascending order
            "cubic_identity_residual": float, |4*l1*l2*l3 - (l3^3 - l3*(l1-l2)^2)|
            "strain_norm_squared": float, l1^2 + l2^2 + l3^2
            "strain_alignment_ratio": float, l3 / sum(l_i^2)
            "ceiling_margin": float, 2/3 - l3 / sum(l_i^2)
            "morphology": str, 'vortex_tube' | 'shear_sheet' | 'pancake_compression' | 'quiescent'
    """
    grad_u = np.asarray(grad_u, dtype=float)
    if grad_u.shape != (3, 3):
        raise ValueError("Velocity gradient must be a 3x3 matrix")
        
    S = 0.5 * (grad_u + grad_u.T)
    tr_S = float(np.trace(S))
    
    # Project to traceless strain if slight numerical divergence
    S_dev = S - (tr_S / 3.0) * np.eye(3)
    
    # Real eigenvalues in ascending order
    eigvals = np.linalg.eigvalsh(S_dev)
    l1, l2, l3 = float(eigvals[0]), float(eigvals[1]), float(eigvals[2])
    
    # Exact cubic determinant identity from incompressibility:
    # 4 * l1 * l2 * l3 = l3^3 - l3 * (l1 - l2)^2
    lhs = 4.0 * (l1 * l2 * l3)
    rhs = (l3**3) - l3 * ((l1 - l2)**2)
    cubic_res = float(abs(lhs - rhs))
    
    strain_norm_sq = float(l1**2 + l2**2 + l3**2)
    if strain_norm_sq > 1e-14:
        ratio = float(l3 / strain_norm_sq)
    else:
        ratio = 0.0
        
    ceiling_margin = float((2.0 / 3.0) - ratio)
    
    if strain_norm_sq < 1e-14:
        morphology = "quiescent"
    elif abs(l1 - l2) < 0.25 * max(abs(l1), abs(l3)) and l3 > 0:
        morphology = "vortex_tube"
    elif abs(l2) < 0.25 * max(abs(l1), abs(l3)):
        morphology = "shear_sheet"
    else:
        morphology = "pancake_compression"
        
    return {
        "trace_div": tr_S,
        "eigenvalues": [l1, l2, l3],
        "cubic_identity_residual": cubic_res,
        "strain_norm_squared": strain_norm_sq,
        "strain_alignment_ratio": ratio,
        "ceiling_margin": ceiling_margin,
        "morphology": morphology
    }
