"""
Assembles Milestone 5.7 campaign shards (written by run_milestone_5_7_chunk.py)
into the final JSON + Markdown report.

Usage:
  python assemble_milestone_5_7_report.py --shard-dir runs/milestone_5_7/shards \
      --output runs/milestone_5_7 --grid-tiers-requested 32 64 128 --grid-tiers-executed 32 64

Milestone 5.7a audit fix (item 6)
----------------------------------
The original run produced 189 rows from 35 shard files with NO deduplication
at assembly time: any two shards covering the same (case, grid_n, group,
material) combination -- e.g. because a chunk was rerun into a differently
-named shard file after an interrupted earlier attempt, without deleting the
stale shard -- silently double-counted. Confirmed root cause via direct shard
inspection: `g32_A_highvisc.json` (14 rows, one full pass over all cases) and
`g32_A_highvisc_actual.json` (3 rows) both contain `weak_isotropic`,
`moderate_steady_isotropic`, `strong_isotropic` at grid_n=32/group=A/
material=high_viscosity_newtonian_liquid -- 3 genuine stale-shard duplicates,
not a resolution or physics effect. `--dedup` (default True) now drops
repeats of the same identity key, keeping the first-seen row and reporting
what was dropped. This explains the 189 vs n_runs_expected=84 discrepancy in
full: 84 (grid32, 6 groups, incompressible_newtonian_liquid) + 84 (grid64, 6
groups, same material, chunked across multiple numbered shards with no
case overlap) + 1 (grid128 group A spot check) + 14 (grid32 group A,
high_viscosity_newtonian_liquid, first pass) + 3 (stale-shard duplicate
rerun of 3 of those 14 cases) + 3 (one-off material_not_implemented probes
for generic_compressible_gas/low_mach_newtonian_gas/simplified_viscoelastic_
candidate placeholders, each correctly blocked and contributing exactly 1
row) = 189. n_runs_expected=84 was simply the wrong constant to compare
against a multi-material, multi-grid-tier run -- not evidence the campaign
itself was broken -- but the 3 stale-shard duplicates ARE a real dedup bug,
now fixed here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from stress_test_report import generate_stress_test_reports_from_rows


def _row_identity(row: dict) -> tuple:
    """Dedup key: prefer the deterministic run_id (rows produced by 5.7a-era
    code); fall back to (case_name, grid_n, group, material, forcing_type)
    for older rows that predate run_id -- sufficient to catch the confirmed
    stale-shard duplication (identical case+grid+group+material reran into a
    differently-named shard file)."""
    if row.get("run_id"):
        return ("run_id", row["run_id"])
    return ("legacy", row["case_name"], row["grid_n"], row["group"], row["material"], row.get("forcing_type"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--shard-dir", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--grid-tiers-requested", nargs="+", type=int, default=[32, 64, 128])
    p.add_argument("--grid-tiers-executed", nargs="+", type=int, default=[32, 64])
    p.add_argument("--n-runs-expected", type=int, default=None)
    p.add_argument("--dedup", action="store_true", default=True)
    p.add_argument("--no-dedup", dest="dedup", action="store_false")
    args = p.parse_args()

    shard_dir = Path(args.shard_dir)
    shard_files = sorted(shard_dir.glob("*.json"))
    raw_rows = []
    for sf in shard_files:
        data = json.loads(sf.read_text())
        raw_rows.extend(data["rows"])

    print(f"loaded {len(raw_rows)} rows from {len(shard_files)} shards")

    rows = raw_rows
    n_dropped = 0
    if args.dedup:
        seen = {}
        deduped = []
        dropped = []
        for row in raw_rows:
            key = _row_identity(row)
            if key in seen:
                dropped.append((key, row["case_name"], row["grid_n"], row["group"], row["material"]))
                continue
            seen[key] = row
            deduped.append(row)
        rows = deduped
        n_dropped = len(dropped)
        if dropped:
            print(f"dedup: dropped {n_dropped} stale-shard duplicate row(s):")
            for key, case_name, grid_n, group, material in dropped:
                print(f"   duplicate of {case_name} grid_n={grid_n} group={group} material={material}")
        print(f"after dedup: {len(rows)} rows")

    jp, mp = generate_stress_test_reports_from_rows(
        args.output, rows, grid_tiers_requested=args.grid_tiers_requested,
        grid_tiers_executed=args.grid_tiers_executed,
        n_runs_expected=args.n_runs_expected if args.n_runs_expected is not None else len(raw_rows) - n_dropped,
        shards_used=[sf.name for sf in shard_files],
    )
    print(f"wrote {jp}")
    print(f"wrote {mp}")


if __name__ == "__main__":
    main()
