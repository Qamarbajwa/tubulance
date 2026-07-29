"""
Structural / anisotropy diagnostics (Milestone 5.7)
========================================================

H5 states that spectral agreement alone is insufficient to judge strong
directional forcing: it can produce alignment, sheets, columns, jets, and
persistent shear layers while leaving the isotropic spectrum looking
similar. This module adds the structural diagnostics the spec requires:
Reynolds-stress anisotropy tensor, directional (angle-resolved) spectra,
vorticity/strain distributions (vorticity_statistics already exists in
jhtdb_terminal_benchmark.py for the isotropic scalars; this module adds
strain and the angular/tensor pieces), and a simple connected-component
structure detector (size/intensity; lifetime tracking is explicitly out of
scope for a single-snapshot/short-run stress test and is not implemented
here -- see module docstring on structure_lifetime_distribution).
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

try:
    from scipy import ndimage as _ndimage
except ImportError:  # pragma: no cover
    _ndimage = None


def anisotropy_tensor(u: np.ndarray) -> np.ndarray:
    """b_ij = <u_i u_j>/<u_k u_k> - delta_ij/3, the normalized Reynolds-
    stress anisotropy tensor. u: (3, nz, ny, nx) real space. Returns (3,3).
    Isotropic turbulence has b_ij == 0; strong directional forcing biases
    the diagonal and/or introduces off-diagonal components."""
    reynolds = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            reynolds[i, j] = float(np.mean(u[i] * u[j]))
    trace = np.trace(reynolds)
    if trace <= 1e-30:
        return np.zeros((3, 3))
    b = reynolds / trace - np.eye(3) / 3.0
    return b


def anisotropy_invariants(b: np.ndarray) -> dict:
    """Second and third invariants of b_ij (Lumley triangle coordinates):
    II = -0.5*tr(b^2), III = det(b)/3 (using the trace(b^3)/3 convention).
    II == III == 0 is isotropic; larger magnitudes indicate stronger
    anisotropy."""
    ii = float(-0.5 * np.trace(b @ b))
    iii = float(np.trace(b @ b @ b) / 3.0)
    # anisotropy_magnitude = sqrt(tr(b^2)), a non-negative scalar regardless
    # of the sign convention used for the Lumley invariant II above (II is
    # reported separately, unmodified, for callers who want the triangle
    # coordinates specifically).
    magnitude = float(np.sqrt(max(np.trace(b @ b), 0.0)))
    return {"II": ii, "III": iii, "anisotropy_magnitude": magnitude}


def directional_spectrum(uh: np.ndarray, kmag: np.ndarray, kx, ky, kz, direction, *, n_bins: int = 8):
    """Energy spectrum resolved by angle between k and `direction`
    (cos(theta) binned into n_bins from -1 to 1), summed over all
    wavenumber shells -- a coarse but simple way to see whether energy is
    concentrated along/against the forcing direction rather than spread
    isotropically."""
    d = np.asarray(direction, dtype=float)
    d = d / (np.linalg.norm(d) + 1e-30)
    n3 = np.prod(uh.shape[1:])
    modal_energy = 0.5 * np.sum(np.abs(uh) ** 2, axis=0) / (n3 * n3)
    kmag_safe = np.where(kmag > 1e-12, kmag, 1.0)
    cos_theta = (kx * d[0] + ky * d[1] + kz * d[2]) / kmag_safe
    cos_theta = np.where(kmag > 1e-12, cos_theta, 0.0)
    bins = np.linspace(-1.0, 1.0, n_bins + 1)
    energy_per_bin = np.zeros(n_bins)
    for i in range(n_bins):
        mask = (cos_theta >= bins[i]) & (cos_theta < bins[i + 1] if i < n_bins - 1 else cos_theta <= bins[i + 1])
        energy_per_bin[i] = modal_energy[mask].sum()
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    return bin_centers, energy_per_bin


def directional_anisotropy_ratio(bin_centers: np.ndarray, energy_per_bin: np.ndarray) -> float:
    """max(E_bin)/mean(E_bin); 1.0 for a perfectly isotropic directional
    spectrum, larger values indicate concentration along particular
    directions (sheets/jets/columns)."""
    total = float(np.sum(energy_per_bin))
    if total <= 1e-30:
        return float("nan")
    mean_bin = total / len(energy_per_bin)
    if mean_bin <= 1e-30:
        return float("nan")
    return float(np.max(energy_per_bin) / mean_bin)


def strain_statistics(uh: np.ndarray, kx, ky, kz) -> dict[str, float]:
    """Strain-rate tensor S_ij = 0.5*(du_i/dx_j + du_j/dx_i), real space,
    reported the same way jhtdb_terminal_benchmark.vorticity_statistics
    reports vorticity: mean/rms/p95/p99/max of |S| = sqrt(2 S_ij S_ij)."""
    grad = np.zeros((3, 3) + uh.shape[1:], dtype=np.float64)
    k = (kx, ky, kz)
    for i in range(3):
        for j in range(3):
            grad[i, j] = np.fft.ifftn(1j * k[j] * uh[i]).real
    s = 0.5 * (grad + np.transpose(grad, (1, 0, 2, 3, 4)))
    mag = np.sqrt(2.0 * np.sum(s * s, axis=(0, 1)))
    return {
        "strain_mean": float(np.mean(mag)),
        "strain_rms": float(np.sqrt(np.mean(mag * mag))),
        "strain_p95": float(np.quantile(mag, 0.95)),
        "strain_p99": float(np.quantile(mag, 0.99)),
        "strain_max": float(np.max(mag)),
    }


@dataclass(frozen=True)
class StructurePopulation:
    n_structures: int
    sizes: tuple[int, ...]  # voxel counts
    intensities: tuple[float, ...]  # mean |field| within each structure
    threshold: float


# --- Milestone 5.7a audit item 9: isotropic-control ensemble ---------------
#
# The original Milestone 5.7 report flagged anisotropic_response_identified
# on 173/186 executable runs -- including isotropically-forced cases --
# because anisotropy_magnitude > 0.02 was treated as evidence on its own,
# with no comparison against how much anisotropy an ISOTROPIC control run
# shows purely from finite-sample/single-realization noise (short runs,
# small grids, one seed). This is the fix: compare a case's anisotropy
# against the mean+z*std of a small ensemble of matched isotropic-forcing
# control runs (same power/k_f/material/grid/duration, different seeds).


@dataclass(frozen=True)
class IsotropicControlBaseline:
    mean_anisotropy_magnitude: float
    std_anisotropy_magnitude: float
    n_seeds: int
    samples: tuple[float, ...]


def isotropic_control_baseline(anisotropy_magnitudes: list[float]) -> IsotropicControlBaseline:
    """Builds the baseline from a list of anisotropy_magnitude values, one
    per isotropic-control seed (caller runs the solver once per seed with
    isotropic_random forcing matched to the case under test and computes
    anisotropy_invariants on each final state -- see
    milestone_5_7_stress_test.run_isotropic_control_ensemble)."""
    if not anisotropy_magnitudes:
        raise ValueError("need at least one isotropic-control sample")
    arr = np.asarray(anisotropy_magnitudes, dtype=float)
    return IsotropicControlBaseline(
        mean_anisotropy_magnitude=float(np.mean(arr)),
        std_anisotropy_magnitude=float(np.std(arr)),
        n_seeds=len(arr),
        samples=tuple(anisotropy_magnitudes),
    )


def is_anisotropic_response_significant(
    case_anisotropy_magnitude: float, baseline: IsotropicControlBaseline, *, z: float = 2.0
) -> bool:
    """True only if the case's anisotropy exceeds mean + z*std of the
    isotropic-control ensemble -- not merely nonzero. With a single-seed
    baseline (std=0, n_seeds=1) this reduces to a strict inequality against
    that one sample, which is a weak test -- callers should use multiple
    seeds where computationally practical (the 5.7a spec's own
    recommendation) and this function does not pretend otherwise."""
    threshold = baseline.mean_anisotropy_magnitude + z * baseline.std_anisotropy_magnitude
    return case_anisotropy_magnitude > threshold


def detect_structures(scalar_field: np.ndarray, *, threshold_fraction: float = 0.5) -> StructurePopulation:
    """Simple connected-component structure detector on a nonnegative
    scalar field (e.g. vorticity magnitude or strain magnitude):
    thresholds at `threshold_fraction` of the field's max, labels connected
    components (periodic boundary via wraparound not applied -- a
    documented simplification), and reports each component's voxel count
    and mean intensity. Structure *lifetime* tracking (matching structures
    across time steps) is out of scope for this milestone's short synthetic
    runs and is not implemented -- callers needing it must track structures
    across snapshots themselves and should report `lifetime: not
    implemented` rather than fabricate a value.
    """
    if _ndimage is None:
        raise ImportError("scipy.ndimage is required for detect_structures()")
    peak = float(np.max(scalar_field))
    if peak <= 0:
        return StructurePopulation(n_structures=0, sizes=(), intensities=(), threshold=0.0)
    threshold = threshold_fraction * peak
    mask = scalar_field >= threshold
    labeled, n = _ndimage.label(mask)
    sizes = []
    intensities = []
    for i in range(1, n + 1):
        comp_mask = labeled == i
        sizes.append(int(comp_mask.sum()))
        intensities.append(float(scalar_field[comp_mask].mean()))
    return StructurePopulation(n_structures=n, sizes=tuple(sizes), intensities=tuple(intensities), threshold=threshold)
