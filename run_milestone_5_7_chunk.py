"""
Milestone 5.7 campaign chunk runner
========================================

Executes one bounded slice of the full stress-test campaign (a subset of
forcing cases, one grid_n, one comparison group, one material) and appends
the resulting rows to a JSON shard file. Exists purely so the campaign can
be executed across many short wall-clock chunks (this environment's tool
layer caps a single command at ~45s) without losing partial progress --
each shard is self-contained and `assemble_milestone_5_7_report.py` merges
however many shards exist.

Usage:
  python run_milestone_5_7_chunk.py --grid-n 32 --group A --cases all \
      --material incompressible_newtonian_liquid --n-steps 40 \
      --shard-dir runs/milestone_5_7/shards --shard-name g32_A
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from forcing_test_matrix import ALL_CASES
from milestone_5_7_stress_test import run_one, tune_controller_gains, DEFAULT_DOMAIN_LENGTH, DEFAULT_VISCOSITY, DEFAULT_DT
from material_state import get_material
from stress_test_report import _result_to_dict


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--grid-n", type=int, required=True)
    p.add_argument("--group", required=True)
    p.add_argument("--cases", nargs="+", required=True, help="case name(s), or 'all'")
    p.add_argument("--material", default="incompressible_newtonian_liquid")
    p.add_argument("--n-steps", type=int, default=40)
    p.add_argument("--dt", type=float, default=DEFAULT_DT)
    p.add_argument("--viscosity", type=float, default=DEFAULT_VISCOSITY)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--shard-dir", required=True)
    p.add_argument("--shard-name", required=True)
    p.add_argument(
        "--tuned-gains", nargs=2, type=float, default=None, metavar=("GP", "GI"),
        help="skip group B's calibration retune and use this precomputed (gp, gi) pair instead "
             "(must have been computed via tune_controller_gains on the calibration set for the "
             "same material/grid_n -- this flag only avoids recomputation, it does not change what "
             "'retuned on calibration' means).",
    )
    args = p.parse_args()

    if args.cases == ["all"]:
        cases = list(ALL_CASES)
    else:
        by_name = {c.name: c for c in ALL_CASES}
        cases = [by_name[n] for n in args.cases]

    tuned_gains = args.tuned_gains
    if args.group == "B" and tuned_gains is None:
        material = get_material(args.material)
        tuned_gains = tune_controller_gains(
            material, args.grid_n, domain_length=DEFAULT_DOMAIN_LENGTH, viscosity=args.viscosity,
            dt=args.dt, n_steps=max(args.n_steps // 2, 10), seed=args.seed,
        )

    rows = []
    for case in cases:
        r = run_one(
            case, args.material, args.grid_n, args.group, domain_length=DEFAULT_DOMAIN_LENGTH,
            viscosity=args.viscosity, n_steps=args.n_steps, dt=args.dt, seed=args.seed, tuned_gains=tuned_gains,
        )
        rows.append(_result_to_dict(r))
        print(f"  {case.name:32s} group={args.group} grid={args.grid_n} -> {r.classification.labels}")

    shard_dir = Path(args.shard_dir)
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard_path = shard_dir / f"{args.shard_name}.json"
    shard_path.write_text(json.dumps({"tuned_gains": tuned_gains, "rows": rows}, indent=2))
    print(f"wrote {shard_path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
