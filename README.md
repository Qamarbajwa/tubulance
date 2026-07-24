# JHTDB terminal-layer benchmark

This folder contains the first real-data benchmark harness for the finite-scale
terminal-layer turbulence model.

## Why it must run on SciServer

The official JHTDB project recommends SciServer because its compute containers
are directly connected to the turbulence database and provide the Giverny
libraries and mounted data volumes. A local authorization token may also be
used, but the precise client call depends on the current Giverny release.

## Setup

1. Create a SciServer account.
2. Open **Compute** and create an **Essentials 4.0** container.
3. Mount the **Turbulence** data volume.
4. Download the current official `DEMO_SciServer_python_notebooks.zip`.
5. Copy the velocity-cutout call from the demo into
   `fetch_velocity_cutout()` in `jhtdb_terminal_benchmark.py`.
6. Run:

```bash
python jhtdb_terminal_benchmark.py
```

## First outputs

- `apriori_metrics.csv`
- `spectra.csv`
- `spectral_comparison.png`

## Pass/fail checks

The first test should report:

- zero energy above the selected cutoff for the filtered and terminal fields;
- spectral error below the cutoff;
- spectral error specifically inside the terminal layer;
- terminal heat and return fractions;
- DNS, filtered-DNS, and terminal-field vorticity statistics.

This is an **a-priori operator test**. It does not yet prove that the model
evolves correctly in time. After it passes, use two JHTDB snapshots separated
by a known interval to measure the actual sub-filter energy transfer, then run
the complete forward model for the same interval.
