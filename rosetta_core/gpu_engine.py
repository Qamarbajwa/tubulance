"""
gpu_engine.py
GPU-Accelerated Guyan-Schur Static Condensation & Matrix Inversion Engine.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Boundary: All four Clay Millennium Problems remain strictly OPEN
(status: verified-finite, open_horizon_lock: STRICTLY OPEN).
"""

from __future__ import annotations

import time
import numpy as np

try:
    import torch
    HAS_TORCH = True
    HAS_CUDA = torch.cuda.is_available()
except ImportError:
    HAS_TORCH = False
    HAS_CUDA = False


def gpu_guyan_schur_tare(
    K_matrix: np.ndarray | "torch.Tensor",
    active_indices: list[int] | np.ndarray,
    device: str = "auto",
) -> dict:
    """
    Computes Guyan-Schur static condensation:
        Sigma_D = K_DD - K_DA @ inv(K_AA) @ K_AD
    utilizing PyTorch CUDA on GPU if available, else vectorized CPU fallback.
    """
    t0 = time.time()

    if isinstance(K_matrix, np.ndarray):
        K_np = K_matrix
    else:
        K_np = K_matrix.detach().cpu().numpy()

    n = K_np.shape[0]
    active_set = set(active_indices)
    omitted_indices = [i for i in range(n) if i not in active_set]
    active_indices = list(active_indices)

    k_active = len(active_indices)
    k_omitted = len(omitted_indices)

    # Determine execution device
    if device == "auto":
        target_device = "cuda:0" if HAS_CUDA else ("cpu" if HAS_TORCH else "numpy")
    else:
        target_device = device

    use_torch = HAS_TORCH and target_device != "numpy"
    vram_mb = 0.0

    if use_torch:
        dev = torch.device(target_device if (target_device.startswith("cuda") and HAS_CUDA) else "cpu")
        K_t = torch.tensor(K_np, dtype=torch.float64, device=dev)
        idx_D = torch.tensor(active_indices, dtype=torch.long, device=dev)
        idx_A = torch.tensor(omitted_indices, dtype=torch.long, device=dev)

        K_DD = K_t[idx_D][:, idx_D]
        K_AA = K_t[idx_A][:, idx_A]
        K_DA = K_t[idx_D][:, idx_A]
        K_AD = K_t[idx_A][:, idx_D]

        # Solve K_AA @ X = K_AD  =>  X = inv(K_AA) @ K_AD
        X = torch.linalg.solve(K_AA, K_AD)
        tare_correction = K_DA @ X
        Sigma_D_t = K_DD - tare_correction

        # Reconstruction error: || K_AA @ X - K_AD ||_inf
        res = K_AA @ X - K_AD
        max_err = float(torch.max(torch.abs(res)).cpu().item())
        Sigma_D = Sigma_D_t.detach().cpu().numpy()

        if dev.type == "cuda":
            vram_mb = float(torch.cuda.memory_allocated(dev)) / (1024.0 ** 2)
        device_used = f"torch-{dev.type}"
    else:
        # NumPy fallback
        K_DD = K_np[np.ix_(active_indices, active_indices)]
        K_AA = K_np[np.ix_(omitted_indices, omitted_indices)]
        K_DA = K_np[np.ix_(active_indices, omitted_indices)]
        K_AD = K_np[np.ix_(omitted_indices, active_indices)]

        X = np.linalg.solve(K_AA, K_AD)
        tare_correction = K_DA @ X
        Sigma_D = K_DD - tare_correction

        res = K_AA @ X - K_AD
        max_err = float(np.max(np.abs(res)))
        device_used = "numpy-cpu"

    elapsed = time.time() - t0

    return {
        "Sigma_D": Sigma_D,
        "device": device_used,
        "cuda_available": HAS_CUDA,
        "vram_allocated_mb": round(vram_mb, 4),
        "max_reconstruction_error": max_err,
        "elapsed_seconds": round(elapsed, 6),
        "total_dofs": n,
        "active_dofs": k_active,
        "omitted_dofs": k_omitted,
        "reconstruction_passed": bool(max_err < 1e-10),
    }
