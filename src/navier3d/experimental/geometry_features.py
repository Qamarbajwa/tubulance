"""Pure geometry feature extraction, coordinate partitioning, and current-state-preserving past shuffle controls.

ZERO-LEAKAGE MANDATE:
- All features are computed exclusively from tracer coordinates x(t) and time.
- No explicit Eulerian physical fields (vorticity, strain rate, velocity gradients, pressure)
  may be calculated or passed into the geometry feature extractor.
- Three coordinate modes supported:
  1. 'intrinsic': Centroid/translation removed (pure deformation).
  2. 'phase_reduced': Homogeneous periodic phase removed (relative to initial position).
  3. 'absolute': Full Cartesian coordinates included.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import numpy as np

from .lagrangian_tracking import (
    Particle,
    MaterialThread,
    MaterialBundle,
    compute_geometry_deformation_gradient,
)


def _unwrap_trajectory(coords: np.ndarray, domain_size: Optional[Tuple[float, float, float]] = None) -> np.ndarray:
    """Unwrap periodic coordinate steps to maintain spatial continuity."""
    if domain_size is None:
        return coords.copy()
    unwrapped = coords.copy()
    for dim in range(3):
        L = domain_size[dim]
        d = np.diff(unwrapped[..., dim], axis=0)
        d_corr = d - L * np.round(d / L)
        unwrapped[1:, ..., dim] = unwrapped[0, ..., dim] + np.cumsum(d_corr, axis=0)
    return unwrapped


def _shuffle_past_prefix(arr: np.ndarray, seed: int = 42) -> np.ndarray:
    """Shuffle the past prefix arr[:-1] while keeping arr[-1] strictly intact."""
    if len(arr) <= 2:
        return arr.copy()
    rng = np.random.RandomState(seed)
    past = arr[:-1].copy()
    perm = rng.permutation(len(past))
    if np.array_equal(perm, np.arange(len(past))) and len(past) > 1:
        perm = np.roll(perm, 1)
    return np.concatenate([past[perm], [arr[-1]]])


def _reverse_past_prefix(arr: np.ndarray) -> np.ndarray:
    """Reverse the past prefix arr[:-1] while keeping arr[-1] strictly intact."""
    if len(arr) <= 2:
        return arr.copy()
    return np.concatenate([arr[:-1][::-1], [arr[-1]]])


# =========================================================================
# Representation P0: Particle Trajectories
# =========================================================================

def extract_particle_features(
    particle: Particle,
    obs_idx: int,
    tau_steps: int,
    domain_size: Optional[Tuple[float, float, float]] = None,
    coordinate_mode: str = "intrinsic",
    intrinsic_only: Optional[bool] = None,
    time_shuffled: bool = False,
    time_reversed: bool = False,
    seed: int = 42,
) -> Dict[str, np.ndarray]:
    """Extract instantaneous and ordered fixed-lag history features for Particle (P0)."""
    if intrinsic_only is not None:
        coordinate_mode = "intrinsic" if intrinsic_only else "absolute"

    start_idx = max(0, obs_idx - tau_steps)
    traj_window = particle.trajectory[start_idx : obs_idx + 1].copy()
    times_window = particle.times[start_idx : obs_idx + 1].copy()
    W = len(traj_window)

    unwrapped = _unwrap_trajectory(traj_window, domain_size)
    dt_arr = np.diff(times_window)
    dt_arr = np.where(dt_arr == 0.0, 1e-4, dt_arr)

    # 1. Compute true scalar velocity and acceleration sequence
    if W > 1:
        vel = np.diff(unwrapped, axis=0) / dt_arr[:, None]
        speeds = np.linalg.norm(vel, axis=1)
    else:
        vel = np.zeros((1, 3))
        speeds = np.zeros(1)

    if W > 2:
        acc = np.diff(vel, axis=0) / dt_arr[1:, None]
        acc_mags = np.linalg.norm(acc, axis=1)
        v_mid = 0.5 * (vel[:-1] + vel[1:])
        v_cross_a = np.cross(v_mid, acc)
        v_mag = np.linalg.norm(v_mid, axis=1)
        traj_curv = np.linalg.norm(v_cross_a, axis=1) / (v_mag**3 + 1e-6)
    else:
        acc_mags = np.zeros(1)
        traj_curv = np.zeros(1)

    # Instantaneous current state at t_obs (strictly preserved under past controls)
    inst_speed = float(speeds[-1]) if len(speeds) > 0 else 0.0
    inst_acc = float(acc_mags[-1]) if len(acc_mags) > 0 else 0.0
    inst_curv = float(traj_curv[-1]) if len(traj_curv) > 0 else 0.0

    # 2. Form ordered history sequence of speeds S = [s(t_0), ..., s(t_obs)]
    hist_speeds = speeds.copy()
    if time_shuffled:
        hist_speeds = _shuffle_past_prefix(hist_speeds, seed=seed)
    elif time_reversed:
        hist_speeds = _reverse_past_prefix(hist_speeds)

    lag_speeds = np.zeros(4, dtype=np.float64)
    n_lags = min(4, len(hist_speeds))
    if len(hist_speeds) > 0:
        lag_speeds[:n_lags] = hist_speeds[::-1][:n_lags]

    lag_increments = np.zeros(3, dtype=np.float64)
    if len(hist_speeds) > 1:
        d_spd = np.diff(hist_speeds)
        n_inc = min(3, len(d_spd))
        lag_increments[:n_inc] = d_spd[::-1][:n_inc]

    intrinsic_inst = np.array([inst_speed, inst_acc, inst_curv], dtype=np.float64)
    intrinsic_hist = np.concatenate([
        intrinsic_inst,
        lag_speeds[:4],
        lag_increments[:3],
    ])

    if coordinate_mode == "intrinsic":
        inst_final = intrinsic_inst
        hist_final = intrinsic_hist
    elif coordinate_mode == "phase_reduced":
        rel_pos = unwrapped[-1] - unwrapped[0]
        inst_final = np.concatenate([rel_pos, intrinsic_inst])
        hist_final = np.concatenate([rel_pos, intrinsic_hist])
    else:  # absolute
        curr_pos = unwrapped[-1]
        inst_final = np.concatenate([curr_pos, intrinsic_inst])
        hist_final = np.concatenate([curr_pos, intrinsic_hist])

    return {
        "instantaneous": inst_final,
        "history": hist_final,
        "raw_speeds": speeds,
    }


# =========================================================================
# Representation P1: Material Threads
# =========================================================================

def extract_thread_features(
    thread: MaterialThread,
    obs_idx: int,
    tau_steps: int,
    domain_size: Optional[Tuple[float, float, float]] = None,
    coordinate_mode: str = "intrinsic",
    intrinsic_only: Optional[bool] = None,
    time_shuffled: bool = False,
    time_reversed: bool = False,
    seed: int = 42,
) -> Dict[str, np.ndarray]:
    """Extract instantaneous and ordered fixed-lag history features for Material Thread (P1)."""
    if intrinsic_only is not None:
        coordinate_mode = "intrinsic" if intrinsic_only else "absolute"

    start_idx = max(0, obs_idx - tau_steps)
    traj_window = thread.trajectories[start_idx : obs_idx + 1].copy()
    times_window = thread.times[start_idx : obs_idx + 1].copy()
    W, N, _ = traj_window.shape

    lengths = []
    end_to_end = []
    mean_curvatures = []

    for w in range(W):
        pts = traj_window[w].copy()
        if domain_size is not None:
            for dim in range(3):
                L = domain_size[dim]
                d = np.diff(pts[:, dim])
                d_corr = d - L * np.round(d / L)
                pts[1:, dim] = pts[0, dim] + np.cumsum(d_corr)

        seg_vecs = np.diff(pts, axis=0)
        seg_lens = np.linalg.norm(seg_vecs, axis=1)
        L_t = float(np.sum(seg_lens))
        lengths.append(L_t)

        e2e = float(np.linalg.norm(pts[-1] - pts[0]))
        end_to_end.append(e2e)

        if N > 2:
            t_prev = seg_vecs[:-1] / (seg_lens[:-1, None] + 1e-8)
            t_next = seg_vecs[1:] / (seg_lens[1:, None] + 1e-8)
            ds_mid = 0.5 * (seg_lens[:-1] + seg_lens[1:])
            local_curv = np.linalg.norm(t_next - t_prev, axis=1) / (ds_mid + 1e-8)
            mean_curvatures.append(float(np.mean(local_curv)))
        else:
            mean_curvatures.append(0.0)

    lengths = np.array(lengths)
    end_to_end = np.array(end_to_end)
    mean_curvatures = np.array(mean_curvatures)

    L0 = thread.initial_length
    norm_lengths = lengths / L0
    tortuosity = float(lengths[-1] / (end_to_end[-1] + 1e-6))

    inst_norm_len = float(norm_lengths[-1])
    inst_tort = float(tortuosity)
    inst_curv = float(mean_curvatures[-1])

    hist_lengths = norm_lengths.copy()
    if time_shuffled:
        hist_lengths = _shuffle_past_prefix(hist_lengths, seed=seed)
    elif time_reversed:
        hist_lengths = _reverse_past_prefix(hist_lengths)

    lag_lengths = np.zeros(4, dtype=np.float64)
    n_lags = min(4, len(hist_lengths))
    if len(hist_lengths) > 0:
        lag_lengths[:n_lags] = hist_lengths[::-1][:n_lags]

    lag_dL = np.zeros(3, dtype=np.float64)
    if len(hist_lengths) > 1:
        dL = np.diff(hist_lengths)
        n_inc = min(3, len(dL))
        lag_dL[:n_inc] = dL[::-1][:n_inc]

    intrinsic_inst = np.array([inst_norm_len, inst_tort, inst_curv], dtype=np.float64)
    intrinsic_hist = np.concatenate([
        intrinsic_inst,
        lag_lengths[:4],
        lag_dL[:3],
    ])

    if coordinate_mode == "intrinsic":
        inst_final = intrinsic_inst
        hist_final = intrinsic_hist
    elif coordinate_mode == "phase_reduced":
        xc_curr = np.mean(traj_window[-1], axis=0)
        xc_init = np.mean(traj_window[0], axis=0)
        rel_pos = xc_curr - xc_init
        inst_final = np.concatenate([rel_pos, intrinsic_inst])
        hist_final = np.concatenate([rel_pos, intrinsic_hist])
    else:
        inst_xc = np.mean(traj_window[-1], axis=0)
        inst_final = np.concatenate([inst_xc, intrinsic_inst])
        hist_final = np.concatenate([inst_xc, intrinsic_hist])

    return {
        "instantaneous": inst_final,
        "history": hist_final,
        "raw_lengths": lengths,
    }


# =========================================================================
# Representation P2: Material Bundles
# =========================================================================

def extract_bundle_features(
    bundle: MaterialBundle,
    obs_idx: int,
    tau_steps: int,
    domain_size: Optional[Tuple[float, float, float]] = None,
    coordinate_mode: str = "intrinsic",
    intrinsic_only: Optional[bool] = None,
    time_shuffled: bool = False,
    time_reversed: bool = False,
    seed: int = 42,
) -> Dict[str, np.ndarray]:
    """Extract instantaneous and ordered fixed-lag history features for Material Bundle (P2)."""
    if intrinsic_only is not None:
        coordinate_mode = "intrinsic" if intrinsic_only else "absolute"

    start_idx = max(0, obs_idx - tau_steps)
    traj_window = bundle.trajectories[start_idx : obs_idx + 1].copy()
    times_window = bundle.times[start_idx : obs_idx + 1].copy()
    W, N, _ = traj_window.shape

    stretches_1 = []
    stretches_2 = []
    stretches_3 = []

    for w in range(W):
        current_pts = traj_window[w]
        F, det_F = compute_geometry_deformation_gradient(current_pts, bundle.initial_offsets, domain_size)
        C = F.T @ F
        eigvals = np.sort(np.linalg.eigvalsh(C))[::-1]
        sigmas = np.sqrt(np.maximum(1e-12, eigvals))

        stretches_1.append(sigmas[0])
        stretches_2.append(sigmas[1])
        stretches_3.append(sigmas[2])

    stretches_1 = np.array(stretches_1)
    stretches_2 = np.array(stretches_2)
    stretches_3 = np.array(stretches_3)

    inst_s1 = float(stretches_1[-1])
    inst_s2 = float(stretches_2[-1])
    inst_s3 = float(stretches_3[-1])

    hist_s1 = stretches_1.copy()
    if time_shuffled:
        hist_s1 = _shuffle_past_prefix(hist_s1, seed=seed)
    elif time_reversed:
        hist_s1 = _reverse_past_prefix(hist_s1)

    lag_s1 = np.zeros(4, dtype=np.float64)
    n_lags = min(4, len(hist_s1))
    if len(hist_s1) > 0:
        lag_s1[:n_lags] = hist_s1[::-1][:n_lags]

    lag_ds1 = np.zeros(3, dtype=np.float64)
    if len(hist_s1) > 1:
        ds1 = np.diff(hist_s1)
        n_inc = min(3, len(ds1))
        lag_ds1[:n_inc] = ds1[::-1][:n_inc]

    intrinsic_inst = np.array([inst_s1, inst_s2, inst_s3], dtype=np.float64)
    intrinsic_hist = np.concatenate([
        intrinsic_inst,
        lag_s1[:4],
        lag_ds1[:3],
    ])

    if coordinate_mode == "intrinsic":
        inst_final = intrinsic_inst
        hist_final = intrinsic_hist
    elif coordinate_mode == "phase_reduced":
        xc_curr = traj_window[-1, 0]
        xc_init = traj_window[0, 0]
        rel_pos = xc_curr - xc_init
        inst_final = np.concatenate([rel_pos, intrinsic_inst])
        hist_final = np.concatenate([rel_pos, intrinsic_hist])
    else:
        inst_xc = traj_window[-1, 0]
        inst_final = np.concatenate([inst_xc, intrinsic_inst])
        hist_final = np.concatenate([inst_xc, intrinsic_hist])

    return {
        "instantaneous": inst_final,
        "history": hist_final,
        "raw_stretches": stretches_1,
    }


def apply_random_history_swapping(
    history_matrix: np.ndarray,
    seed: int = 42,
) -> np.ndarray:
    """Assign history from an unrelated material object while keeping current object state."""
    rng = np.random.RandomState(seed)
    n_samples = len(history_matrix)
    shuffled_indices = rng.permutation(n_samples)

    controlled = history_matrix.copy()
    controlled[:, 3:] = history_matrix[shuffled_indices, 3:]
    return controlled
