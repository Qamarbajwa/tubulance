"""Script to run the authoritative sealed TH1R Material-History Falsification Suite."""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from navier3d.experimental.th1_suite import run_th1r_reconciled_suite


def main():
    parser = argparse.ArgumentParser(description="Run TH1R Sealed Confirmatory Falsification Suite.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="evidence/th1r_confirmatory/run_th1r_sealed_01",
        help="Target output directory for authoritative artifacts.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="th1r_scientific_config.json",
        help="Path to frozen scientific configuration.",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("EXPERIMENTAL RESEARCH BRANCH TH1R: SEALED CONFIRMATORY EXECUTION")
    print("MATERIAL-HISTORY FALSIFICATION: GEOMETRY-ONLY LAGRANGIAN MEMORY")
    print("Protocol: Falsification-First, Zero-Leakage, Leave-One-Flow-Out")
    print("=" * 70)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    results = run_th1r_reconciled_suite(output_dir=output_dir, config_path=args.config)
    elapsed = time.time() - t0

    print(f"\nExecution completed in {elapsed:.2f} seconds.")
    print(f"Artifacts successfully written to: {output_dir.resolve()}")
    print(f"Classification: {results['decision']['classification']}")
    print(f"Verdict: {results['decision']['verdict']}")


if __name__ == "__main__":
    main()
