"""
Backscatter-placement strategies (Milestone 5, preregistered)
================================================================

The terminal operator specifies WHAT fraction of removed energy is
"returned" (1 - alpha(k)) but not WHERE it is spectrally reinjected.
Milestone 4 implemented only the algebraic control case (`local_
cancellation`). This module adds three more candidate placement rules,
preregistered here -- with their functional form fixed BEFORE being run
against real data -- so a later "best fit" cannot be mistaken for a
physical discovery. Only `parent_band_energy_weighted` takes free
parameters (`c1`, `c2`), and those must be supplied explicitly by the
caller (Config.parent_band_c1/c2); there is no default, precisely so a
band can't be quietly tuned after seeing results.

Each strategy returns T_return(k), a per-shell array satisfying (up to
floating-point tolerance)

    sum_k T_return(k) == P_return == sum_k (1-alpha(k))*gamma(k)*E(k)

Violating this is a bug or an unusable configuration (e.g. an empty
return band) -- see verify_placement_conservation().

Strategies:

  local_cancellation
    T_return(k) = (1-alpha(k))*gamma(k)*E(k)          [same shell]
    T_model(k) reduces to -alpha(k)*gamma(k)*E(k) (heat only). This is
    reduced effective damping, NOT a modeled inverse cascade to larger
    scales -- see README.md / AGENTS.md.

  parent_band_energy_weighted
    Returns energy to a band [c1*ks, c2*ks] (0 < c1 < c2 < 1) below the
    terminal layer, distributed proportional to existing energy E(k) in
    that band.

  turnover_weighted
    Returns energy to all resolved shells below ks, weighted by
    E(k)/tau(k) with tau(k) ~ [k^3 E(k)]^(-1/2) (eddy turnover time) --
    faster-turnover, more energetic shells absorb more of the return.

  dns_oracle_diagnostic
    Distributes return energy proportional to the DNS's own positive
    T(k) (net local gain) below ks. DIAGNOSTIC ONLY: it uses the answer
    (real DNS transfer) to place the model's return, so it cannot be a
    deployable predictive model. Its only legitimate use is as an upper
    bound on how well *some* placement could do if the true return
    destination were known -- never report it as, or alongside, a
    predictive-performance claim.
"""

from __future__ import annotations

import numpy as np


class PlacementConfigError(ValueError):
    """Raised when a placement strategy is selected without the
    parameters it requires (e.g. parent_band_energy_weighted without
    c1/c2), or with parameters that don't satisfy their constraints."""


class PlacementConservationError(RuntimeError):
    """Raised when a placement strategy's output does not conserve
    total returned power (or the full T_model does not conserve to
    -total_heat) within tolerance -- see Part C in README.md."""


DIAGNOSTIC_ONLY = frozenset({"dns_oracle_diagnostic"})


def _total_return_power(alpha_shell: np.ndarray, gamma_shell: np.ndarray, e_ref: np.ndarray) -> float:
    return float(((1.0 - alpha_shell) * gamma_shell * e_ref).sum())


def local_cancellation(
    shells: np.ndarray, e_ref: np.ndarray, gamma_shell: np.ndarray, alpha_shell: np.ndarray, *, ks: float, **_
) -> np.ndarray:
    return (1.0 - alpha_shell) * gamma_shell * e_ref


def parent_band_energy_weighted(
    shells: np.ndarray,
    e_ref: np.ndarray,
    gamma_shell: np.ndarray,
    alpha_shell: np.ndarray,
    *,
    ks: float,
    c1: float | None = None,
    c2: float | None = None,
    **_,
) -> np.ndarray:
    if c1 is None or c2 is None:
        raise PlacementConfigError(
            "parent_band_energy_weighted requires Config.parent_band_c1 and "
            "parent_band_c2 to be set explicitly -- preregistered before running, "
            "not tuned after seeing results."
        )
    if not (0.0 < c1 < c2 < 1.0):
        raise PlacementConfigError(f"require 0 < c1 < c2 < 1, got c1={c1}, c2={c2}")

    kr1, kr2 = c1 * ks, c2 * ks
    band = (shells >= kr1) & (shells <= kr2)
    total_return = _total_return_power(alpha_shell, gamma_shell, e_ref)

    t_return = np.zeros_like(e_ref)
    band_energy = float(e_ref[band].sum())
    if band_energy > 0:
        t_return[band] = total_return * e_ref[band] / band_energy
    # else: leave t_return as zero -- conservation will correctly fail,
    # signalling this band is unusable for this snapshot/resolution
    # rather than silently dropping the returned energy.
    return t_return


def turnover_weighted(
    shells: np.ndarray, e_ref: np.ndarray, gamma_shell: np.ndarray, alpha_shell: np.ndarray, *, ks: float, **_
) -> np.ndarray:
    region = (shells > 0) & (shells < ks)
    # tau(k) ~ [k^3 E(k)]^(-1/2)  =>  1/tau(k) ~ [k^3 E(k)]^(1/2)
    k_safe = np.maximum(shells, 1e-12)
    e_safe = np.maximum(e_ref, 0.0)
    inv_tau = np.sqrt(k_safe ** 3 * e_safe)
    weight = e_ref * inv_tau

    total_return = _total_return_power(alpha_shell, gamma_shell, e_ref)
    t_return = np.zeros_like(e_ref)
    region_weight_sum = float(weight[region].sum())
    if region_weight_sum > 0:
        t_return[region] = total_return * weight[region] / region_weight_sum
    return t_return


def dns_oracle_diagnostic(
    shells: np.ndarray,
    e_ref: np.ndarray,
    gamma_shell: np.ndarray,
    alpha_shell: np.ndarray,
    *,
    ks: float,
    t_dns: np.ndarray | None = None,
    **_,
) -> np.ndarray:
    if t_dns is None:
        raise PlacementConfigError(
            "dns_oracle_diagnostic requires the real DNS transfer t_dns -- it is a "
            "diagnostic-only placement, not a deployable model."
        )
    region = (shells > 0) & (shells < ks)
    positive = np.where(region, np.clip(t_dns, 0.0, None), 0.0)

    total_return = _total_return_power(alpha_shell, gamma_shell, e_ref)
    t_return = np.zeros_like(e_ref)
    positive_sum = float(positive.sum())
    if positive_sum > 0:
        t_return[region] = total_return * positive[region] / positive_sum
    return t_return


PLACEMENT_STRATEGIES = {
    "local_cancellation": local_cancellation,
    "parent_band_energy_weighted": parent_band_energy_weighted,
    "turnover_weighted": turnover_weighted,
    "dns_oracle_diagnostic": dns_oracle_diagnostic,
}


def compute_t_return(
    placement: str,
    shells: np.ndarray,
    e_ref: np.ndarray,
    gamma_shell: np.ndarray,
    alpha_shell: np.ndarray,
    *,
    ks: float,
    c1: float | None = None,
    c2: float | None = None,
    t_dns: np.ndarray | None = None,
) -> np.ndarray:
    if placement not in PLACEMENT_STRATEGIES:
        raise PlacementConfigError(
            f"Unknown backscatter_placement {placement!r}; choose one of "
            f"{sorted(PLACEMENT_STRATEGIES)}."
        )
    fn = PLACEMENT_STRATEGIES[placement]
    return fn(shells, e_ref, gamma_shell, alpha_shell, ks=ks, c1=c1, c2=c2, t_dns=t_dns)


def verify_placement_conservation(
    t_return: np.ndarray,
    t_remove: np.ndarray,
    alpha_shell: np.ndarray,
    gamma_shell: np.ndarray,
    e_ref: np.ndarray,
    *,
    tolerance: float = 1e-6,
) -> dict:
    """Part C: sum_k T_return(k) == P_return, and sum_k T_model(k) == -total_heat.
    Both residuals are reported; raise PlacementConservationError if either
    exceeds `tolerance` relative to the total processed power.
    """
    total_return_expected = _total_return_power(alpha_shell, gamma_shell, e_ref)
    total_return_actual = float(t_return.sum())
    total_heat = float((alpha_shell * gamma_shell * e_ref).sum())
    t_model = t_remove + t_return
    shell_summed_model_transfer = float(t_model.sum())

    total_processed = float((gamma_shell * e_ref).sum())
    scale = max(total_processed, 1e-30)

    return_residual = (total_return_actual - total_return_expected) / scale
    model_residual = (shell_summed_model_transfer + total_heat) / scale

    report = {
        "total_return_expected": total_return_expected,
        "total_return_actual": total_return_actual,
        "return_conservation_relative_residual": return_residual,
        "total_heat": total_heat,
        "shell_summed_model_transfer": shell_summed_model_transfer,
        "model_conservation_relative_residual": model_residual,
        "tolerance": tolerance,
        "passes": abs(return_residual) <= tolerance and abs(model_residual) <= tolerance,
    }
    if not report["passes"]:
        raise PlacementConservationError(
            f"Placement conservation check failed: return_residual={return_residual:.3g}, "
            f"model_residual={model_residual:.3g}, tolerance={tolerance:.3g}. Report: {report}"
        )
    return report
