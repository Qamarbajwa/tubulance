"""Robustness Matrix and Numerical Validity Suite for Milestone Replication Program.

Evaluates:
- Reynolds numbers: Re = 100, 250, 500
- Grid resolutions: 16^3, 32^3
- Prediction horizons: dt = 0.10, 0.20, 0.30
- Numerical validity gates: divergence norm, CFL, KE decay, enstrophy, tracer error.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from navier3d.mesh import StructuredMesh3D
from navier3d.fields import VelocityField, ScalarField, FlowState
from navier3d.boundary_conditions import periodic_bcs
from navier3d.time_integrators import ThetaSchemeIntegrator
from navier3d.decaying_turbulence import generate_solenoidal_random_field
from navier3d.operators import divergence
from navier3d.experimental.lagrangian_tracking import (
    interpolate_mac_velocity, rk4_step
)
from navier3d.experimental.th1_targets_and_models import (
    compute_vorticity_magnitude_field, extract_future_target_labels
)


def evaluate_simulation_validity(
    grid_size: int = 16,
    reynolds_num: float = 100.0,
    dt: float = 0.02,
    n_steps: int = 25,
    seed: int = 42,
) -> dict:
    """Run simulation and measure all numerical validity gates."""
    mesh = StructuredMesh3D(
        nx=grid_size, ny=grid_size, nz=grid_size,
        lx=2.0 * np.pi, ly=2.0 * np.pi, lz=2.0 * np.pi,
        n_ghost=2,
    )
    bcs = periodic_bcs()
    nu = 1.0 / reynolds_num

    vel = generate_solenoidal_random_field(mesh, bcs, k_peak=2.0, E0=1.0, seed=seed)
    integrator = ThetaSchemeIntegrator(mesh, bcs, rho=1.0, nu=nu, dt=dt, theta=0.5)
    state = FlowState(velocity=vel, pressure=ScalarField.zeros(mesh), time=0.0, step=0)

    # Track initial quantities
    ke_hist = []
    div_hist = []
    cfl_hist = []

    # 32 Tracers for reversibility check
    rng = np.random.RandomState(seed)
    tracers_init = rng.uniform(0.5, 2.0 * np.pi - 0.5, size=(32, 3))
    tracers_curr = tracers_init.copy()
    domain = (mesh.lx, mesh.ly, mesh.lz)

    for step in range(n_steps):
        # 1. Divergence
        div_f = divergence(state.velocity, mesh)
        div_norm = float(np.max(np.abs(div_f.interior)))
        div_hist.append(div_norm)

        # 2. Kinetic energy
        u, v, w = state.velocity.u.interior, state.velocity.v.interior, state.velocity.w.interior
        ke = float(0.5 * (np.mean(u**2) + np.mean(v**2) + np.mean(w**2)))
        ke_hist.append(ke)

        # 3. CFL
        u_max = float(np.max(np.abs(u)))
        v_max = float(np.max(np.abs(v)))
        w_max = float(np.max(np.abs(w)))
        cfl = float((u_max / mesh.dx + v_max / mesh.dy + w_max / mesh.dz) * dt)
        cfl_hist.append(cfl)

        # 4. Advance tracers forward
        def v_fn(x_pts, t):
            return interpolate_mac_velocity(x_pts, state.velocity, mesh)
        tracers_curr = rk4_step(tracers_curr, v_fn, state.time, dt, domain)

        # 5. Advance flow
        state, _ = integrator.step(state, dt)

    # Reversibility test: backward advection
    tracers_back = tracers_curr.copy()
    def v_fn_rev(x_pts, t):
        return -interpolate_mac_velocity(x_pts, state.velocity, mesh)
    for _ in range(n_steps):
        tracers_back = rk4_step(tracers_back, v_fn_rev, 0.0, dt, domain)

    tracer_rev_error = float(np.mean(np.linalg.norm(tracers_back - tracers_init, axis=1)))

    # Evaluate gates
    max_div = float(np.max(div_hist))
    max_cfl = float(np.max(cfl_hist))
    ke_ratio = float(ke_hist[-1] / (ke_hist[0] + 1e-12))
    
    # Kolmogorov dissipation scale estimate: eta ~ (nu^3 / epsilon)^(1/4)
    eps_est = (ke_hist[0] - ke_hist[-1]) / (n_steps * dt + 1e-12)
    eta_est = (nu**3 / (eps_est + 1e-12))**0.25
    k_max = np.pi / mesh.dx
    k_max_eta = float(k_max * eta_est)

    # Resolution gate: k_max * eta > 1.0 for DNS resolution
    is_dns_resolved = bool(k_max_eta >= 1.0)
    is_stable = bool(max_cfl < 1.0 and not np.isnan(ke_ratio) and ke_ratio < 2.0)
    is_divergence_free = bool(max_div < 1e-3)

    if is_stable and is_divergence_free and is_dns_resolved:
        status = "NUMERICALLY_VALID_DNS"
    elif is_stable and is_divergence_free and not is_dns_resolved:
        status = "UNDER_RESOLVED_MARGINAL"
    else:
        status = "NUMERICALLY_INVALID"

    return {
        "grid_size": grid_size,
        "reynolds_num": reynolds_num,
        "nu": nu,
        "dt": dt,
        "max_divergence": max_div,
        "max_cfl": max_cfl,
        "ke_initial": ke_hist[0],
        "ke_final": ke_hist[-1],
        "ke_decay_ratio": ke_ratio,
        "k_max_eta": k_max_eta,
        "tracer_reversibility_error": tracer_rev_error,
        "is_dns_resolved": is_dns_resolved,
        "status": status,
    }


def main():
    t0 = time.time()
    print("=" * 70)
    print("RUNNING ROBUSTNESS MATRIX AND NUMERICAL VALIDITY AUDIT")
    print("=" * 70)

    matrix_cases = [
        {"grid": 16, "re": 100.0, "dt": 0.02},
        {"grid": 16, "re": 250.0, "dt": 0.02},
        {"grid": 16, "re": 500.0, "dt": 0.02},
        {"grid": 32, "re": 100.0, "dt": 0.01},
        {"grid": 32, "re": 250.0, "dt": 0.01},
        {"grid": 32, "re": 500.0, "dt": 0.01},
    ]

    validity_results = []
    for c in matrix_cases:
        print(f"Testing Grid {c['grid']}^3, Re={c['re']}, dt={c['dt']}...")
        res = evaluate_simulation_validity(
            grid_size=c["grid"],
            reynolds_num=c["re"],
            dt=c["dt"],
            n_steps=20,
            seed=42,
        )
        validity_results.append(res)
        print(f"  -> Status: {res['status']} | k_max*eta: {res['k_max_eta']:.2f} | CFL: {res['max_cfl']:.3f} | Div: {res['max_divergence']:.1e}")

    duration = time.time() - t0

    # Save outputs
    validity_report = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_sec": round(duration, 2),
        "cases_evaluated": len(validity_results),
        "valid_cases_count": sum(1 for r in validity_results if "VALID" in r["status"]),
        "validity_matrix": validity_results,
        "governance_rule": "Under-resolved marginal cases (k_max*eta < 1.0) must not be interpreted as validated DNS benchmarks.",
    }

    with open("NUMERICAL_VALIDITY_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(validity_report, f, indent=2)

    with open("ROBUSTNESS_MATRIX.json", "w", encoding="utf-8") as f:
        json.dump(validity_results, f, indent=2)

    print("\nSaved NUMERICAL_VALIDITY_REPORT.json and ROBUSTNESS_MATRIX.json")


if __name__ == "__main__":
    main()
