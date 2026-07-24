"""
Nonlinear-transfer DNS-vs-model validation (Milestone 3)
===========================================================

The nonlinear-transfer stage described in README.md: compare the terminal
operator's predicted shell-wise removal against the DNS's *true*
instantaneous nonlinear spectral transfer T(k) (see nonlinear_transfer.py),
rather than the finite-difference dE/dt(k) used in compare_model_to_dns.py.

Unlike compare_model_to_dns.py, this does NOT require a confirmed Delta-t:
T(k) is computed directly from a single snapshot's velocity field, so only
one DNS snapshot is needed. It still has the same resolution requirement
(a resolution-adequate terminal layer) and raises immediately if that is
not met.

Even a fully successful result here is, at most, a-priori consistency
between the model and the true cascade -- not proof the model evolves
correctly in time. See run_classification.py for exactly what each
possible outcome does and does not claim.
"""

from __future__ import annotations

import json
import time
import tracemalloc
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from jhtdb_terminal_benchmark import (
    Config,
    InsufficientResolutionError,
    bin_shells,
    compute_terminal_layer,
    estimate_tau_s,
    spectral_relative_l2,
    terminal_operator,
    validate_terminal_layer,
)
from backscatter_placement import (
    DIAGNOSTIC_ONLY,
    PlacementConservationError,
    compute_t_return,
    verify_placement_conservation,
)
from comparison_metrics import extended_region_metrics, region_metrics, shell_collapse_gamma_alpha
from nonlinear_transfer import (
    modal_transfer,
    shell_transfer,
    spectral_flux,
    verify_global_conservation,
)
from run_classification import RunStages, classify_run, positive_result_bar
from run_metadata import SpatialOrigin, build_run_metadata
from spectral_fields import dns_and_filtered_shells


def validate(
    velocity: np.ndarray,
    cfg: Config,
    output_dir: str,
    *,
    dealias: bool = False,
    conservation_tolerance: float = 1e-6,
    spatial_origin: SpatialOrigin | None = None,
    time_coordinate: dict | None = None,
) -> dict:
    tracemalloc.start()
    t0 = time.perf_counter()

    uh_dns, uh_ref, kx, ky, kz, kmag, shells, e_dns, e_ref, kc, nyquist = dns_and_filtered_shells(
        velocity, cfg
    )

    delta_k = 2.0 * np.pi / cfg.domain_length
    layer = compute_terminal_layer(kc, delta_k, cfg)
    failures = validate_terminal_layer(layer, nyquist, shells, e_dns, cfg)
    if failures:
        tracemalloc.stop()
        raise InsufficientResolutionError(
            "Cannot run the nonlinear-transfer comparison: " + "; ".join(failures)
        )
    ks = layer.ks

    # True nonlinear transfer, computed on the FULL (unfiltered) DNS field
    # -- T(k) below kc is meaningful physics; content above kc is aliased
    # by the finite grid regardless of the terminal-layer model and is not
    # used for the comparison, only reported for completeness.
    t_modal, _, uh_work = modal_transfer(uh_dns, kx, ky, kz, dealias=dealias, nyquist=nyquist)
    dns_shells, t_dns = shell_transfer(t_modal, kmag)
    assert np.array_equal(dns_shells, shells)
    pi_dns = spectral_flux(t_dns)
    conservation = verify_global_conservation(t_modal)

    # Terminal-model prediction, evaluated on the filtered DNS field.
    tau_s = estimate_tau_s(uh_ref, kmag, ks)
    c_gamma = 1.0
    op = terminal_operator(
        uh_ref, kmag, kc, layer.beta_effective, cfg.alpha_s, cfg.n_shape, cfg.m_shape, c_gamma, tau_s
    )
    gamma_shell, alpha_shell = shell_collapse_gamma_alpha(uh_ref, kmag, op["gamma"], op["alpha"])

    # --- Complete predicted shell transfer -----------------------------
    # T_remove(k) = -gamma(k)E(k) is the TOTAL removal (heat + return
    # combined) leaving shell k. Only the heat fraction is a genuine net
    # kinetic-energy sink; the return (backscatter) fraction is redistributed,
    # not destroyed. Treating T_remove alone as "the model's transfer"
    # systematically penalizes the model for energy it intentionally
    # returns elsewhere -- see the module docstring and AGENTS.md.
    #
    # T_return(k) needs a spectral PLACEMENT (which shell(s) receive the
    # returned energy), which the terminal operator does not currently
    # specify beyond the aggregate heat/return split. cfg.backscatter_placement
    # selects one of the preregistered strategies in backscatter_placement.py
    # (default "local_cancellation": reinjection at the same shell, the
    # only placement consistent with having no other information -- under
    # it, T_model(k) reduces exactly to -alpha(k)*gamma(k)*E(k), heat only).
    t_model_remove = -gamma_shell * e_ref
    t_model_heat = -alpha_shell * gamma_shell * e_ref
    try:
        t_model_return = compute_t_return(
            cfg.backscatter_placement,
            shells,
            e_ref,
            gamma_shell,
            alpha_shell,
            ks=ks,
            c1=cfg.parent_band_c1,
            c2=cfg.parent_band_c2,
            t_dns=t_dns,
        )
    except Exception:
        tracemalloc.stop()
        raise
    t_model = t_model_remove + t_model_return
    pi_model = spectral_flux(t_model)

    # Part C: fail the run if either conservation identity is violated,
    # rather than silently reporting numbers that don't add up.
    try:
        conservation_report = verify_placement_conservation(
            t_model_return, t_model_remove, alpha_shell, gamma_shell, e_ref, tolerance=conservation_tolerance
        )
    except PlacementConservationError:
        tracemalloc.stop()
        raise
    model_transfer_conservation = {
        "total_removal": float(t_model_remove.sum()),
        "total_reinjection": conservation_report["total_return_actual"],
        "total_heat": conservation_report["total_heat"],
        "shell_summed_model_transfer": conservation_report["shell_summed_model_transfer"],
        "residual": conservation_report["model_conservation_relative_residual"],
        "return_conservation_relative_residual": conservation_report["return_conservation_relative_residual"],
        "backscatter_placement": cfg.backscatter_placement,
        "diagnostic_only": cfg.backscatter_placement in DIAGNOSTIC_ONLY,
    }

    # --- Regions (full-transfer comparison: T_DNS vs T_model) ----------
    forcing_available = cfg.forcing_kmax is not None
    if forcing_available:
        forcing_region = (shells > 0) & (shells <= cfg.forcing_kmax)
        inertial_region = (shells > cfg.forcing_kmax) & (shells < ks)
    else:
        forcing_region = np.zeros_like(shells, dtype=bool)
        inertial_region = (shells > 0) & (shells < ks)
    terminal_region = (shells >= ks) & (shells <= kc)
    permitted = (shells > 0) & (shells <= kc)
    kc_floor = int(np.floor(kc))
    final_two_before_kc = np.isin(shells, [kc_floor - 1, kc_floor])

    regions = {
        "forcing_region": (
            extended_region_metrics(shells, t_dns, t_model, forcing_region)
            if forcing_available
            else {"unavailable_reason": "Config.forcing_kmax not set -- see AGENTS.md"}
        ),
        "inertial_resolved_region": extended_region_metrics(shells, t_dns, t_model, inertial_region),
        "terminal_region": extended_region_metrics(shells, t_dns, t_model, terminal_region),
        "final_two_shells_before_kc": extended_region_metrics(shells, t_dns, t_model, final_two_before_kc),
    }

    # --- Removal-only comparison: T_DNS vs T_remove, DNS-net-loss shells only
    dns_net_loss = permitted & (t_dns < 0)
    removal_only_comparison = extended_region_metrics(shells, t_dns, t_model_remove, dns_net_loss)

    # --- Flux comparison: Pi_DNS vs Pi_model, plus the plateau below ks -
    denom = np.sqrt(np.sum(pi_dns[permitted] ** 2))
    flux_relative_l2_error = (
        float(np.sqrt(np.sum((pi_model[permitted] - pi_dns[permitted]) ** 2)) / denom)
        if denom > 0
        else float("nan")
    )
    flux_comparison = extended_region_metrics(shells, pi_dns, pi_model, permitted)
    flux_comparison["relative_l2_error"] = flux_relative_l2_error
    below_ks = (shells > 0) & (shells < ks)
    flux_plateau_error_below_ks = (
        float(np.mean(np.abs(pi_model[below_ks] - pi_dns[below_ks]))) if below_ks.any() else float("nan")
    )

    model_terminal_removal_power = float((-t_model_remove[terminal_region]).sum())
    dns_flux_at_kc = float(pi_dns[kc_floor]) if kc_floor < len(pi_dns) else float("nan")
    terminal_processing_to_dns_flux_ratio = (
        model_terminal_removal_power / dns_flux_at_kc if dns_flux_at_kc != 0 else float("nan")
    )

    terminal_t_dns = t_dns[terminal_region]
    fraction_terminal_shells_backscatter = (
        float(np.mean(terminal_t_dns > 0)) if terminal_t_dns.size else float("nan")
    )

    e_terminal_field = uh_ref * np.exp(-op["gamma"] * tau_s)
    n3 = np.prod(e_terminal_field.shape[1:])
    e_terminal_modal = 0.5 * np.sum(np.abs(e_terminal_field) ** 2, axis=0) / (n3 * n3)
    _, e_terminal_shell = bin_shells(e_terminal_modal, kmag)
    final_two_mean_terminal = float(np.mean(e_terminal_shell[final_two_before_kc]))
    final_two_mean_filtered_dns = float(np.mean(e_ref[final_two_before_kc]))
    bottleneck_ratio = (
        final_two_mean_terminal / final_two_mean_filtered_dns
        if final_two_mean_filtered_dns > 0
        else float("nan")
    )
    spectrum_relative_l2_terminal_region = spectral_relative_l2(e_ref, e_terminal_shell, terminal_region)

    # NOTE: energy above cutoff is checked on the FILTERED field, not raw
    # DNS -- raw DNS always has energy above kc (that's what filtering
    # removes); the pass criterion is that filtering/the operator actually
    # enforces zero energy there, same convention as
    # jhtdb_terminal_benchmark.py's energy_above_cutoff_filtered metric.
    energy_above_cutoff_filtered = float(e_ref[shells > kc].sum())
    energy_above_cutoff_terminal = float(e_terminal_shell[shells > kc].sum())
    populated_terminal_shells = int(
        np.sum(e_dns[terminal_region] > cfg.energy_floor)
    )

    passes_bar, bar_reasons = positive_result_bar(
        n_t=layer.n_t,
        min_terminal_shells=cfg.min_terminal_shells,
        populated_terminal_shells=populated_terminal_shells,
        min_populated_terminal_shells=cfg.min_populated_terminal_shells,
        conservation_relative_residual=conservation["relative_residual"],
        conservation_tolerance=conservation_tolerance,
        energy_above_cutoff=max(energy_above_cutoff_filtered, energy_above_cutoff_terminal),
        transfer_correlation=regions["terminal_region"]["correlation"],
    )

    stages = RunStages(
        pipeline_ok=True,
        resolution_ok=True,
        apriori_operator_ok=True,
        finite_difference_ok=False,
        nonlinear_transfer_ok=True,
        nonlinear_transfer_meets_positive_result_bar=passes_bar,
    )
    classification = classify_run(stages)

    runtime_seconds = time.perf_counter() - t0
    _current, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    run_metadata = build_run_metadata(
        cfg,
        layer,
        nyquist,
        runtime_seconds=runtime_seconds,
        peak_memory_mb=peak_bytes / (1024 * 1024),
        spatial_origin=spatial_origin,
        time_coordinate=time_coordinate,
        populated_terminal_shells=populated_terminal_shells,
    )

    result = {
        "run_metadata": run_metadata,
        "dataset": cfg.dataset,
        "grid_n": int(kmag.shape[0]),
        "kc": kc,
        "ks": ks,
        "n_t": layer.n_t,
        "beta_configured": cfg.beta,
        "beta_effective": layer.beta_effective,
        "terminal_layer_source": layer.source,
        "dealiased": dealias,
        "global_nonlinear_conservation": conservation,
        "model_transfer_conservation": model_transfer_conservation,
        "regions": regions,
        "removal_only_comparison": removal_only_comparison,
        "flux_comparison": flux_comparison,
        "flux_plateau_error_below_ks": flux_plateau_error_below_ks,
        "spectrum_relative_l2_terminal_region": spectrum_relative_l2_terminal_region,
        "flux_relative_l2_error": flux_relative_l2_error,
        "terminal_processing_to_dns_flux_ratio": terminal_processing_to_dns_flux_ratio,
        "fraction_terminal_shells_showing_local_backscatter": fraction_terminal_shells_backscatter,
        "bottleneck_ratio_relative_to_filtered_dns": bottleneck_ratio,
        "energy_above_cutoff_filtered": energy_above_cutoff_filtered,
        "energy_above_cutoff_terminal": energy_above_cutoff_terminal,
        "populated_terminal_shells": populated_terminal_shells,
        "positive_result_bar": {"passes": passes_bar, "failed_reasons": bar_reasons},
        "classification": classification,
        "classification_note": (
            "forward_validation_required means: this run meets the credible "
            "a-priori-consistency bar, and a real forward-in-time run is the "
            "next required step -- it is NOT full validation. See "
            "run_classification.py."
        ),
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "nonlinear_transfer_summary.json").write_text(json.dumps(result, indent=2))

    residual = t_model - t_dns
    per_shell = pd.DataFrame(
        {
            "k": shells,
            "E_dns": e_dns,
            "E_filtered_dns": e_ref,
            "E_terminal": e_terminal_shell,
            "T_dns": t_dns,
            "Pi_dns": pi_dns,
            "T_model_remove": t_model_remove,
            "T_model_heat": t_model_heat,
            "T_model_return": t_model_return,
            "T_model": t_model,
            "Pi_model": pi_model,
            "residual_T_model_minus_T_dns": residual,
        }
    )
    per_shell.to_csv(output / "nonlinear_transfer_per_shell.csv", index=False)

    _plot_dashboard(
        output / "nonlinear_transfer_comparison.png",
        shells=shells,
        e_dns=e_dns,
        e_ref=e_ref,
        t_dns=t_dns,
        pi_dns=pi_dns,
        t_model_remove=t_model_remove,
        t_model_heat=t_model_heat,
        t_model_return=t_model_return,
        t_model=t_model,
        pi_model=pi_model,
        residual=residual,
        ks=ks,
        kc=kc,
    )

    return result


def _plot_dashboard(
    path: Path,
    *,
    shells: np.ndarray,
    e_dns: np.ndarray,
    e_ref: np.ndarray,
    t_dns: np.ndarray,
    pi_dns: np.ndarray,
    t_model_remove: np.ndarray,
    t_model_heat: np.ndarray,
    t_model_return: np.ndarray,
    t_model: np.ndarray,
    pi_model: np.ndarray,
    residual: np.ndarray,
    ks: float,
    kc: float,
) -> None:
    valid = shells > 0
    fig, axes = plt.subplots(3, 2, figsize=(13, 13))

    ax = axes[0, 0]
    ax.semilogy(shells[valid], e_dns[valid] + 1e-30, label="DNS")
    ax.semilogy(shells[valid], e_ref[valid] + 1e-30, label="Filtered DNS")
    ax.axvline(ks, linestyle=":", color="gray")
    ax.axvline(kc, linestyle="--", color="gray")
    ax.set_ylabel("E(k)")
    ax.set_title("Energy spectra")
    ax.legend()

    ax = axes[0, 1]
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.plot(shells[valid], t_dns[valid], marker="o", label="T_DNS(k)")
    ax.plot(shells[valid], t_model[valid], marker="s", label="T_model(k)")
    ax.axvline(ks, linestyle=":", color="gray")
    ax.axvline(kc, linestyle="--", color="gray")
    ax.set_ylabel("T(k)")
    ax.set_title("Shell transfer: DNS vs. model")
    ax.legend()

    ax = axes[1, 0]
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.plot(shells[valid], pi_dns[valid], marker="o", label="Pi_DNS(k)")
    ax.plot(shells[valid], pi_model[valid], marker="s", label="Pi_model(k)")
    ax.axvline(ks, linestyle=":", color="gray")
    ax.axvline(kc, linestyle="--", color="gray")
    ax.set_ylabel("Pi(k)")
    ax.set_title("Cumulative spectral flux")
    ax.legend()

    ax = axes[1, 1]
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.plot(shells[valid], t_model_remove[valid], marker="o", label="T_remove(k) (total)")
    ax.plot(shells[valid], t_model_heat[valid], marker="s", label="T_heat(k) (net sink)")
    ax.plot(shells[valid], t_model_return[valid], marker="^", label="T_return(k) (reinjected)")
    ax.axvline(ks, linestyle=":", color="gray")
    ax.axvline(kc, linestyle="--", color="gray")
    ax.set_xlabel("Wavenumber")
    ax.set_title("Model components: removal / heat / return")
    ax.legend()

    ax = axes[2, 0]
    zoom = (shells >= max(1, ks - 2)) & (shells <= kc + 2)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.plot(shells[zoom], t_dns[zoom], marker="o", label="T_DNS(k)")
    ax.plot(shells[zoom], t_model[zoom], marker="s", label="T_model(k)")
    ax.axvline(ks, linestyle=":", color="gray", label="terminal start")
    ax.axvline(kc, linestyle="--", color="gray", label="cutoff")
    ax.set_xlabel("Wavenumber")
    ax.set_title("Terminal-layer zoom")
    ax.legend()

    ax = axes[2, 1]
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.bar(shells[valid], residual[valid])
    ax.axvline(ks, linestyle=":", color="gray")
    ax.axvline(kc, linestyle="--", color="gray")
    ax.set_xlabel("Wavenumber")
    ax.set_title("Residual: T_model(k) - T_DNS(k)")

    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    """Demonstrates the resolution hard-fail against the local, 16^3
    cutout. Rerun against real SciServer data once the resolution blocker
    in README.md is resolved.
    """
    from measure_transfer import load_local_timestep
    from run_metadata import spatial_origin_from_local_h5

    cfg = Config(cutoff_fraction=0.50)
    path = "isotropic1024coarse.h5"
    v1 = load_local_timestep(path, 1)
    origin = spatial_origin_from_local_h5(path)

    try:
        result = validate(v1, cfg, output_dir="jhtdb_terminal_benchmark", spatial_origin=origin)
        print(json.dumps(result, indent=2))
    except InsufficientResolutionError as exc:
        print("NONLINEAR-TRANSFER COMPARISON BLOCKED (resolution requirement not met):")
        print(f"  {exc}")


if __name__ == "__main__":
    main()
