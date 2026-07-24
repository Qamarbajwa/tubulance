"""
DNS-vs-model shell-wise energy-transfer comparison
====================================================

The forward-model validation stage described in README.md: given two DNS
snapshots at a *confirmed* time separation, compare the terminal-layer
operator's predicted shell-wise energy removal (evaluated once, on the
first snapshot) against the DNS's own measured shell-wise energy evolution
over that interval.

This is still an a-priori-style comparison, not a closed-loop forward
simulation: the model is evaluated once at t1 and its instantaneous
predicted rate is compared to the DNS's finite-difference rate over
[t1, t2]. It does not integrate the model forward in time -- that is a
further stage on top of this one.

This script has two hard requirements and raises immediately, before doing
any spectral work, if either is not met:

1. A CONFIRMED Delta-t -- see measure_transfer.TimeCoordinate /
   measure_transfer.resolve_dt. Adjacent local-export frame indices do not
   count.
2. A resolution-adequate terminal layer -- see
   jhtdb_terminal_benchmark.validate_terminal_layer. A cutoff too close to
   Nyquist, or a terminal layer with too few populated shells, makes the
   comparison physically meaningless (see README.md "Open validation
   blockers").

Per AGENTS.md: never tune model constants (beta, alpha_s, n_shape, m_shape,
gp, gi) using the same snapshot pair this script reports as a validation
result. Keep calibration and validation snapshots disjoint
(Config.calibration_snapshots / Config.validation_snapshots).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from jhtdb_terminal_benchmark import (
    Config,
    InsufficientResolutionError,
    compute_terminal_layer,
    estimate_tau_s,
    terminal_operator,
    validate_terminal_layer,
)
from comparison_metrics import region_metrics, shell_collapse_gamma_alpha
from measure_transfer import TemporalMetadataError, TimeCoordinate, resolve_dt
from spectral_fields import dns_and_filtered_shells


def compare(
    velocity_1: np.ndarray,
    velocity_2: np.ndarray,
    t1: TimeCoordinate,
    t2: TimeCoordinate,
    cfg: Config,
    output_dir: str,
) -> dict:
    # Hard requirement 1: confirmed Delta-t.
    dt = resolve_dt(t1, t2)  # raises TemporalMetadataError if unconfirmed

    _, uh_ref1, kx, ky, kz, kmag, shells, e_dns1, e_ref1, kc, nyquist = dns_and_filtered_shells(
        velocity_1, cfg
    )
    _, _, _, _, _, _, _, _, e_ref2, _, _ = dns_and_filtered_shells(velocity_2, cfg, kc=kc)

    # Hard requirement 2: resolution-adequate terminal layer.
    delta_k = 2.0 * np.pi / cfg.domain_length
    layer = compute_terminal_layer(kc, delta_k, cfg)
    failures = validate_terminal_layer(layer, nyquist, shells, e_dns1, cfg)
    if failures:
        raise InsufficientResolutionError(
            "Cannot run the DNS-vs-model comparison: " + "; ".join(failures)
        )
    ks = layer.ks

    # Measured DNS shell-wise tendency. This is a finite-difference
    # energy-evolution measurement, not an isolated cascade transfer --
    # see module docstring and AGENTS.md.
    edot_dns = (e_ref2 - e_ref1) / dt

    # Model prediction, evaluated once on t1 (not integrated forward).
    tau_s = estimate_tau_s(uh_ref1, kmag, ks)
    c_gamma = 1.0
    op = terminal_operator(
        uh_ref1, kmag, kc, layer.beta_effective, cfg.alpha_s, cfg.n_shape, cfg.m_shape, c_gamma, tau_s
    )
    gamma_shell, alpha_shell = shell_collapse_gamma_alpha(uh_ref1, kmag, op["gamma"], op["alpha"])

    edot_model_total = -gamma_shell * e_ref1
    edot_model_heat = -alpha_shell * gamma_shell * e_ref1
    edot_model_return = -(1.0 - alpha_shell) * gamma_shell * e_ref1

    permitted = (shells > 0) & (shells <= kc)
    terminal_region = (shells >= ks) & (shells <= kc)
    ordinary_region = (shells > 0) & (shells < ks)
    kc_floor = int(np.floor(kc))
    final_two_before_kc = np.isin(shells, [kc_floor - 1, kc_floor])

    regions = {
        "ordinary_resolved_region": region_metrics(edot_dns, edot_model_total, ordinary_region),
        "terminal_region": region_metrics(edot_dns, edot_model_total, terminal_region),
        "final_two_shells_before_kc": region_metrics(edot_dns, edot_model_total, final_two_before_kc),
        "all_permitted": region_metrics(edot_dns, edot_model_total, permitted),
    }

    model_terminal_power = float((-edot_model_total[terminal_region]).sum())
    dns_terminal_power = float((-edot_dns[terminal_region]).sum())
    terminal_power_ratio = (
        model_terminal_power / dns_terminal_power if dns_terminal_power != 0 else float("nan")
    )

    total_energy_below_kc_t1 = float(e_ref1[shells <= kc].sum())
    total_energy_above_kc_t1 = float(e_dns1[shells > kc].sum())

    permitted_dns = edot_dns[permitted]
    positive_fraction = float(np.mean(permitted_dns > 0)) if permitted_dns.size else float("nan")
    negative_fraction = float(np.mean(permitted_dns < 0)) if permitted_dns.size else float("nan")
    if positive_fraction > 0 and negative_fraction > 0:
        transfer_character = "mixed: both energy-losing and energy-gaining resolved shells present"
    elif negative_fraction > 0:
        transfer_character = (
            "net loss at every resolved shell (consistent with, but not proof of, forward transfer -- "
            "see AGENTS.md on not over-interpreting finite differences as cascade flux)"
        )
    elif positive_fraction > 0:
        transfer_character = (
            "net gain at every resolved shell (consistent with, but not proof of, backscatter -- "
            "see AGENTS.md on not over-interpreting finite differences as cascade flux)"
        )
    else:
        transfer_character = "no measurable shell-wise change"

    result = {
        "dataset": cfg.dataset,
        "t1": t1.__dict__,
        "t2": t2.__dict__,
        "delta_t": dt,
        "grid_n": int(np.round(kmag.shape[0])),
        "kc": kc,
        "ks": ks,
        "n_t": layer.n_t,
        "beta_configured": cfg.beta,
        "beta_effective": layer.beta_effective,
        "terminal_layer_source": layer.source,
        "regions": regions,
        "terminal_power_ratio": terminal_power_ratio,
        "model_terminal_power": model_terminal_power,
        "dns_terminal_power": dns_terminal_power,
        "total_energy_below_kc_t1": total_energy_below_kc_t1,
        "total_energy_above_kc_t1": total_energy_above_kc_t1,
        "dns_transfer_character": transfer_character,
        "measurement_label": (
            "shell-wise finite-difference DNS tendency vs. single-evaluation "
            "model prediction -- NOT a closed-loop forward-model validation"
        ),
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "model_vs_dns_summary.json").write_text(json.dumps(result, indent=2))

    per_shell = pd.DataFrame(
        {
            "k": shells,
            "E_t1": e_ref1,
            "E_t2": e_ref2,
            "edot_dns": edot_dns,
            "edot_model_total": edot_model_total,
            "edot_model_heat": edot_model_heat,
            "edot_model_return": edot_model_return,
        }
    )
    per_shell.to_csv(output / "model_vs_dns_per_shell.csv", index=False)

    plt.figure(figsize=(8, 5))
    valid = shells > 0
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.plot(shells[valid], edot_dns[valid], marker="o", label="DNS (measured)")
    plt.plot(shells[valid], edot_model_total[valid], marker="s", label="Model (predicted)")
    plt.axvline(ks, linestyle=":", color="gray", label="terminal start")
    plt.axvline(kc, linestyle="--", color="gray", label="cutoff")
    plt.xlabel("Wavenumber")
    plt.ylabel("dE/dt(k)")
    plt.title("DNS vs. terminal-operator shell-wise energy tendency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "model_vs_dns.png", dpi=180)
    plt.close()

    return result


def main() -> None:
    """Demonstrates the hard-fail behavior against the local, unconfirmed-dt
    16^3 cutouts. Do not fill in a guessed dt_confirmed=True here -- rerun
    this against real SciServer data with a confirmed time separation once
    both open blockers in README.md are resolved.
    """
    from measure_transfer import load_local_timestep, local_h5_time_coordinate

    cfg = Config(cutoff_fraction=0.50)
    path = "isotropic1024coarse (1).h5"
    v1 = load_local_timestep(path, 1)
    v2 = load_local_timestep(path, 5)
    t1 = local_h5_time_coordinate(path, 1)
    t2 = local_h5_time_coordinate(path, 5)

    try:
        compare(v1, v2, t1, t2, cfg, output_dir="jhtdb_terminal_benchmark")
    except TemporalMetadataError as exc:
        print("MODEL-VS-DNS COMPARISON BLOCKED (confirmed Delta-t required):")
        print(f"  {exc}")
    except InsufficientResolutionError as exc:
        print("MODEL-VS-DNS COMPARISON BLOCKED (resolution requirement not met):")
        print(f"  {exc}")


if __name__ == "__main__":
    main()
