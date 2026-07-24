"""
Shared DNS-vs-model comparison helpers
========================================

Used by both compare_model_to_dns.py (finite-difference stage) and
nonlinear_transfer_validation.py (true nonlinear-transfer stage) so region
metrics and the modal-to-shell collapse of the terminal operator's
gamma/alpha fields are computed identically in both places.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def shell_collapse_gamma_alpha(uh_ref: np.ndarray, kmag: np.ndarray, gamma_modal, alpha_modal):
    """Energy-weighted collapse of per-mode gamma/alpha into per-shell
    values, so the terminal operator (defined per-mode) can be compared
    against shell-aggregated DNS quantities."""
    n3 = np.prod(uh_ref.shape[1:])
    modal_energy = 0.5 * np.sum(np.abs(uh_ref) ** 2, axis=0) / (n3 * n3)
    kmax = int(np.floor(kmag.max()))
    gamma_shell = np.zeros(kmax + 1)
    alpha_shell = np.zeros(kmax + 1)
    for shell in range(kmax + 1):
        mask = (kmag >= shell - 0.5) & (kmag < shell + 0.5)
        e_shell = modal_energy[mask].sum()
        if e_shell > 0:
            gamma_shell[shell] = (gamma_modal[mask] * modal_energy[mask]).sum() / e_shell
            alpha_shell[shell] = (alpha_modal[mask] * modal_energy[mask]).sum() / e_shell
    return gamma_shell, alpha_shell


def region_metrics(dns_shell: np.ndarray, model_shell: np.ndarray, mask: np.ndarray) -> dict:
    """Correlation, relative L2 error, and sign-agreement fraction between
    a DNS-measured and model-predicted per-shell quantity, restricted to
    `mask`."""
    dns = dns_shell[mask]
    model = model_shell[mask]

    if dns.size == 0 or np.std(dns) == 0 or np.std(model) == 0:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(dns, model)[0, 1])

    denom = np.sqrt(np.sum(dns ** 2))
    rel_l2 = float(np.sqrt(np.sum((model - dns) ** 2)) / denom) if denom > 0 else float("nan")

    nonzero = dns != 0
    sign_agree = (
        float(np.mean(np.sign(model[nonzero]) == np.sign(dns[nonzero]))) if nonzero.any() else float("nan")
    )

    return {
        "n_shells": int(mask.sum()),
        "correlation": corr,
        "relative_l2_error": rel_l2,
        "sign_agreement_fraction": sign_agree,
    }


def extended_region_metrics(
    shells: np.ndarray, dns_shell: np.ndarray, model_shell: np.ndarray, mask: np.ndarray
) -> dict:
    """region_metrics() plus shape-vs-magnitude-separating metrics: Spearman
    rank correlation (shape agreement independent of scale), cosine
    similarity, normalized mean absolute error, and peak-shell location
    error. A model can have the right pattern with the wrong magnitude, or
    vice versa -- report them separately rather than collapsing to one
    score.
    """
    base = region_metrics(dns_shell, model_shell, mask)

    dns = dns_shell[mask]
    model = model_shell[mask]
    k_in_region = shells[mask]

    if dns.size < 2 or np.std(dns) == 0 or np.std(model) == 0:
        spearman = float("nan")
    else:
        spearman = float(stats.spearmanr(dns, model).correlation)

    dns_norm = float(np.linalg.norm(dns))
    model_norm = float(np.linalg.norm(model))
    cosine = float(np.dot(dns, model) / (dns_norm * model_norm)) if dns_norm > 0 and model_norm > 0 else float("nan")

    mean_abs_dns = float(np.mean(np.abs(dns))) if dns.size else 0.0
    normalized_mae = float(np.mean(np.abs(model - dns)) / mean_abs_dns) if mean_abs_dns > 0 else float("nan")

    if dns.size and np.any(dns != 0):
        peak_idx_dns = int(np.argmax(np.abs(dns)))
        peak_idx_model = int(np.argmax(np.abs(model))) if np.any(model != 0) else peak_idx_dns
        peak_shell_location_error = float(k_in_region[peak_idx_model] - k_in_region[peak_idx_dns])
    else:
        peak_shell_location_error = float("nan")

    base.update(
        {
            "spearman_correlation": spearman,
            "cosine_similarity": cosine,
            "normalized_mean_absolute_error": normalized_mae,
            "peak_shell_location_error": peak_shell_location_error,
        }
    )
    return base
