"""Small numerical helpers mirroring the TP2-G5-A3 algebra."""

from __future__ import annotations

import numpy as np


def amplitude_direction_decomposition(xi, grad_q, q, J_xi):
    if q <= 0:
        raise ValueError("q must be positive")
    xi = np.asarray(xi, dtype=float)
    grad_q = np.asarray(grad_q, dtype=float)
    J_xi = np.asarray(J_xi, dtype=float)
    G = np.outer(xi, grad_q) + q * J_xi
    lhs = float(np.sum(G * G))
    rhs = float(np.dot(grad_q, grad_q) + q * q * np.sum(J_xi * J_xi))
    return G, lhs, rhs


def xi_from_decomposition(D, xi, grad_log_q, J_xi):
    D = np.asarray(D, dtype=float)
    xi = np.asarray(xi, dtype=float)
    grad_log_q = np.asarray(grad_log_q, dtype=float)
    J_xi = np.asarray(J_xi, dtype=float)
    dxi = D @ xi
    denominator = float(dxi @ dxi)
    if denominator <= 0:
        raise ValueError("D xi must be nonzero")
    columns = D @ (J_xi + np.outer(xi, grad_log_q))
    return float(np.sum(columns * columns) / denominator)


def beta_terms(D, xi, J_xi):
    D = np.asarray(D, dtype=float)
    dxi = D @ np.asarray(xi, dtype=float)
    dJ = D @ np.asarray(J_xi, dtype=float)
    denominator = float(dxi @ dxi)
    if denominator <= 0:
        raise ValueError("D xi must be nonzero")
    return (dxi @ dJ) / denominator


def metric_split(D, xi, grad_log_q, J_xi):
    D = np.asarray(D, dtype=float)
    xi = np.asarray(xi, dtype=float)
    grad_log_q = np.asarray(grad_log_q, dtype=float)
    J_xi = np.asarray(J_xi, dtype=float)
    dxi = D @ xi
    norm_dxi = float(np.linalg.norm(dxi))
    if norm_dxi <= 0:
        raise ValueError("D xi must be nonzero")
    n_D = dxi / norm_dxi
    b = (D @ J_xi) / norm_dxi
    beta = n_D @ b
    parallel = grad_log_q + beta
    M_D = float(np.dot(parallel, parallel))
    perpendicular = b - np.outer(n_D, n_D @ b)
    C_D = float(np.sum(perpendicular * perpendicular))
    return M_D + C_D, M_D, C_D


def gamma_xi(D, G, q, xi):
    D = np.asarray(D, dtype=float)
    G = np.asarray(G, dtype=float)
    xi = np.asarray(xi, dtype=float)
    gamma = D.T @ D
    numerator = float(np.trace(gamma @ G @ G.T))
    denominator = float(q * q * (xi @ gamma @ xi))
    if denominator <= 0:
        raise ValueError("q and D xi must be nonzero")
    return numerator / denominator


def condition_number_bounds(D, kappa_squared):
    singular_values = np.linalg.svd(np.asarray(D, dtype=float), compute_uv=False)
    sigma_1 = float(np.max(singular_values))
    sigma_3 = float(np.min(singular_values))
    if sigma_3 <= 0:
        raise ValueError("D must be invertible")
    ratio = (sigma_1 / sigma_3) ** 2
    return kappa_squared / ratio, kappa_squared * ratio
