"""A-priori SGS stress extraction, numerical truncation residual, and energy budget tools.

Provides:
1. `compute_exact_sgs_stress`: extracts exact resolved SGS stress tensor
   tau_ij^exact = <u_i u_j>_bar - u_i_bar * u_j_bar from fine reference flow.
2. `compute_sgs_apriori_diagnostics`: computes exact SGS energy transfer Pi_exact,
   modeled energy transfer Pi_model, transfer correlation rho_Pi, stress correlation rho_tau,
   and a-priori optimal eddy-viscosity coefficient C_d^opt / C_s^opt.
3. `compute_truncation_residuals`: computes coarse numerical advection truncation residual
   F_num vs exact SGS acceleration force F_SGS.
4. `compute_energy_budget`: computes discrete timestep kinetic energy budget and inferred
   numerical viscosity nu_num.
"""
from __future__ import annotations

import numpy as np

from .boundary_conditions import BoundaryConditionSet
from .fields import ScalarField, VelocityField
from .filtering import restrict_velocity_fine_to_coarse
from .mesh import StructuredMesh3D
from .strain import compute_strain_components


def compute_exact_sgs_stress(
    vel_fine: VelocityField,
    mesh_fine: StructuredMesh3D,
    mesh_coarse: StructuredMesh3D,
    bcs: BoundaryConditionSet | None = None,
) -> dict[str, np.ndarray]:
    """Extract exact resolved cell-centered SGS stress tensor from fine velocity field.

    tau_ij^exact = bar(u_i u_j) - bar(u_i) * bar(u_j)
    Returns dict containing 'xx', 'yy', 'zz', 'xy', 'xz', 'yz', and deviatoric components.
    """
    # 1. Coarse filtered velocities bar(u_i)
    vel_coarse = restrict_velocity_fine_to_coarse(vel_fine, mesh_fine, mesh_coarse, bcs)
    u_c = 0.5 * (vel_coarse.u.interior[:-1, :, :] + vel_coarse.u.interior[1:, :, :])
    v_c = 0.5 * (vel_coarse.v.interior[:, :-1, :] + vel_coarse.v.interior[:, 1:, :])
    w_c = 0.5 * (vel_coarse.w.interior[:, :, :-1] + vel_coarse.w.interior[:, :, 1:])

    # 2. Fine cell-centered velocity components and products
    u_f = 0.5 * (vel_fine.u.interior[:-1, :, :] + vel_fine.u.interior[1:, :, :])
    v_f = 0.5 * (vel_fine.v.interior[:, :-1, :] + vel_fine.v.interior[:, 1:, :])
    w_f = 0.5 * (vel_fine.w.interior[:, :, :-1] + vel_fine.w.interior[:, :, 1:])

    # Construct fine face fields for u^2, v^2, w^2, uv, uw, vw
    vel_uu = VelocityField.zeros(mesh_fine)
    vel_vv = VelocityField.zeros(mesh_fine)
    vel_ww = VelocityField.zeros(mesh_fine)
    vel_uv = VelocityField.zeros(mesh_fine)
    vel_uw = VelocityField.zeros(mesh_fine)
    vel_vw = VelocityField.zeros(mesh_fine)

    u_pad = np.pad(u_f * u_f, ((1, 1), (0, 0), (0, 0)), mode="wrap")
    vel_uu.u.interior[:] = 0.5 * (u_pad[:-1, :, :] + u_pad[1:, :, :])

    v_pad = np.pad(v_f * v_f, ((0, 0), (1, 1), (0, 0)), mode="wrap")
    vel_vv.v.interior[:] = 0.5 * (v_pad[:, :-1, :] + v_pad[:, 1:, :])

    w_pad = np.pad(w_f * w_f, ((0, 0), (0, 0), (1, 1)), mode="wrap")
    vel_ww.w.interior[:] = 0.5 * (w_pad[:, :, :-1] + w_pad[:, :, 1:])

    u_pad_uv = np.pad(u_f * v_f, ((1, 1), (0, 0), (0, 0)), mode="wrap")
    vel_uv.u.interior[:] = 0.5 * (u_pad_uv[:-1, :, :] + u_pad_uv[1:, :, :])

    u_pad_uw = np.pad(u_f * w_f, ((1, 1), (0, 0), (0, 0)), mode="wrap")
    vel_uw.u.interior[:] = 0.5 * (u_pad_uw[:-1, :, :] + u_pad_uw[1:, :, :])

    v_pad_vw = np.pad(v_f * w_f, ((0, 0), (1, 1), (0, 0)), mode="wrap")
    vel_vw.v.interior[:] = 0.5 * (v_pad_vw[:, :-1, :] + v_pad_vw[:, 1:, :])

    uu_c_field = restrict_velocity_fine_to_coarse(vel_uu, mesh_fine, mesh_coarse, bcs)
    vv_c_field = restrict_velocity_fine_to_coarse(vel_vv, mesh_fine, mesh_coarse, bcs)
    ww_c_field = restrict_velocity_fine_to_coarse(vel_ww, mesh_fine, mesh_coarse, bcs)
    uv_c_field = restrict_velocity_fine_to_coarse(vel_uv, mesh_fine, mesh_coarse, bcs)
    uw_c_field = restrict_velocity_fine_to_coarse(vel_uw, mesh_fine, mesh_coarse, bcs)
    vw_c_field = restrict_velocity_fine_to_coarse(vel_vw, mesh_fine, mesh_coarse, bcs)

    uu_c = 0.5 * (uu_c_field.u.interior[:-1, :, :] + uu_c_field.u.interior[1:, :, :])
    vv_c = 0.5 * (vv_c_field.v.interior[:, :-1, :] + vv_c_field.v.interior[:, 1:, :])
    ww_c = 0.5 * (ww_c_field.w.interior[:, :, :-1] + ww_c_field.w.interior[:, :, 1:])

    uv_c = 0.5 * (uv_c_field.u.interior[:-1, :, :] + uv_c_field.u.interior[1:, :, :])
    uw_c = 0.5 * (uw_c_field.u.interior[:-1, :, :] + uw_c_field.u.interior[1:, :, :])
    vw_c = 0.5 * (vw_c_field.v.interior[:, :-1, :] + vw_c_field.v.interior[:, 1:, :])

    # tau_ij^exact = bar(u_i u_j) - bar(u_i) * bar(u_j)
    tau_xx = uu_c - u_c * u_c
    tau_yy = vv_c - v_c * v_c
    tau_zz = ww_c - w_c * w_c

    tau_xy = uv_c - u_c * v_c
    tau_xz = uw_c - u_c * w_c
    tau_yz = vw_c - v_c * w_c

    tau_kk = tau_xx + tau_yy + tau_zz
    tau_dev_xx = tau_xx - (1.0 / 3.0) * tau_kk
    tau_dev_yy = tau_yy - (1.0 / 3.0) * tau_kk
    tau_dev_zz = tau_zz - (1.0 / 3.0) * tau_kk

    return {
        "xx": tau_xx, "yy": tau_yy, "zz": tau_zz,
        "xy": tau_xy, "xz": tau_xz, "yz": tau_yz,
        "dev_xx": tau_dev_xx, "dev_yy": tau_dev_yy, "dev_zz": tau_dev_zz,
        "dev_xy": tau_xy, "dev_xz": tau_xz, "dev_yz": tau_yz,
    }


def compute_sgs_apriori_diagnostics(
    tau_exact: dict[str, np.ndarray],
    vel_coarse: VelocityField,
    model_nu_t: ScalarField,
    mesh_coarse: StructuredMesh3D,
    bcs: BoundaryConditionSet | None = None,
) -> dict:
    """Evaluate a-priori diagnostics comparing exact SGS stress against model predictions."""
    # 1. Coarse grid strain components at cell centers
    strain = compute_strain_components(vel_coarse, mesh_coarse, bcs)
    S_xx = strain["s_xx"]
    S_yy = strain["s_yy"]
    S_zz = strain["s_zz"]

    s_xy_edge = strain["s_xy"]
    s_xz_edge = strain["s_xz"]
    s_yz_edge = strain["s_yz"]

    S_xy = 0.25 * (s_xy_edge[:-1, :-1, :] + s_xy_edge[1:, :-1, :] + s_xy_edge[:-1, 1:, :] + s_xy_edge[1:, 1:, :])
    S_xz = 0.25 * (s_xz_edge[:-1, :, :-1] + s_xz_edge[1:, :, :-1] + s_xz_edge[:-1, :, 1:] + s_xz_edge[1:, :, 1:])
    S_yz = 0.25 * (s_yz_edge[:, :-1, :-1] + s_yz_edge[:, 1:, :-1] + s_yz_edge[:, :-1, 1:] + s_yz_edge[:, 1:, 1:])

    S_mag = np.sqrt(2.0 * (S_xx**2 + S_yy**2 + S_zz**2 + 2.0 * S_xy**2 + 2.0 * S_xz**2 + 2.0 * S_yz**2))

    # 2. Exact SGS energy transfer Pi_exact = -tau_ij^{exact,d} * S_ij
    Pi_exact = -(
        tau_exact["dev_xx"] * S_xx + tau_exact["dev_yy"] * S_yy + tau_exact["dev_zz"] * S_zz
        + 2.0 * tau_exact["dev_xy"] * S_xy + 2.0 * tau_exact["dev_xz"] * S_xz + 2.0 * tau_exact["dev_yz"] * S_yz
    )

    # 3. Modeled SGS energy transfer Pi_model = 2 * nu_t * S_ij * S_ij = nu_t * S_mag^2
    nu_t = model_nu_t.interior
    Pi_model = nu_t * (S_mag ** 2)

    # Transfer correlation rho_Pi
    pi_ex_mean = np.mean(Pi_exact)
    pi_mod_mean = np.mean(Pi_model)
    std_ex = np.std(Pi_exact)
    std_mod = np.std(Pi_model)

    if std_ex > 1e-15 and std_mod > 1e-15:
        rho_Pi = float(np.mean((Pi_exact - pi_ex_mean) * (Pi_model - pi_mod_mean)) / (std_ex * std_mod))
    else:
        rho_Pi = 0.0

    E_Pi = float(np.linalg.norm(Pi_model - Pi_exact) / (np.linalg.norm(Pi_exact) + 1e-15))
    E_mean_Pi = float(abs(pi_mod_mean - pi_ex_mean) / (abs(pi_ex_mean) + 1e-15))

    # 4. Modeled deviatoric SGS stress tau_ij^{model,d} = -2 * nu_t * S_ij
    tau_mod_xx = -2.0 * nu_t * S_xx
    tau_mod_yy = -2.0 * nu_t * S_yy
    tau_mod_zz = -2.0 * nu_t * S_zz
    tau_mod_xy = -2.0 * nu_t * S_xy
    tau_mod_xz = -2.0 * nu_t * S_xz
    tau_mod_yz = -2.0 * nu_t * S_yz

    num_tau = np.sum(
        tau_mod_xx * tau_exact["dev_xx"] + tau_mod_yy * tau_exact["dev_yy"] + tau_mod_zz * tau_exact["dev_zz"]
        + 2.0 * tau_mod_xy * tau_exact["dev_xy"] + 2.0 * tau_mod_xz * tau_exact["dev_xz"] + 2.0 * tau_mod_yz * tau_exact["dev_yz"]
    )
    norm_mod = np.sum(
        tau_mod_xx**2 + tau_mod_yy**2 + tau_mod_zz**2
        + 2.0 * tau_mod_xy**2 + 2.0 * tau_mod_xz**2 + 2.0 * tau_mod_yz**2
    )
    norm_ex = np.sum(
        tau_exact["dev_xx"]**2 + tau_exact["dev_yy"]**2 + tau_exact["dev_zz"]**2
        + 2.0 * tau_exact["dev_xy"]**2 + 2.0 * tau_exact["dev_xz"]**2 + 2.0 * tau_exact["dev_yz"]**2
    )

    rho_tau = float(num_tau / (np.sqrt(norm_mod * norm_ex) + 1e-15))

    # 5. A-priori optimal eddy-viscosity coefficient C_d^opt
    delta = (mesh_coarse.dx * mesh_coarse.dy * mesh_coarse.dz) ** (1.0 / 3.0)
    delta_sq = delta ** 2

    M_ev_xx = -2.0 * delta_sq * S_mag * S_xx
    M_ev_yy = -2.0 * delta_sq * S_mag * S_yy
    M_ev_zz = -2.0 * delta_sq * S_mag * S_zz
    M_ev_xy = -2.0 * delta_sq * S_mag * S_xy
    M_ev_xz = -2.0 * delta_sq * S_mag * S_xz
    M_ev_yz = -2.0 * delta_sq * S_mag * S_yz

    num_opt = np.sum(
        tau_exact["dev_xx"] * M_ev_xx + tau_exact["dev_yy"] * M_ev_yy + tau_exact["dev_zz"] * M_ev_zz
        + 2.0 * tau_exact["dev_xy"] * M_ev_xy + 2.0 * tau_exact["dev_xz"] * M_ev_xz + 2.0 * tau_exact["dev_yz"] * M_ev_yz
    )
    den_opt = np.sum(
        M_ev_xx**2 + M_ev_yy**2 + M_ev_zz**2
        + 2.0 * M_ev_xy**2 + 2.0 * M_ev_xz**2 + 2.0 * M_ev_yz**2
    )

    c_d_opt = float(num_opt / (den_opt + 1e-15))
    c_s_opt = float(np.sqrt(abs(c_d_opt)))

    return {
        "Pi_exact_mean": float(pi_ex_mean),
        "Pi_model_mean": float(pi_mod_mean),
        "rho_Pi": rho_Pi,
        "E_Pi": E_Pi,
        "E_mean_Pi": E_mean_Pi,
        "rho_tau": rho_tau,
        "c_d_opt": c_d_opt,
        "c_s_opt": c_s_opt,
        "f_backscatter_exact": float(np.mean(Pi_exact < 0.0)),
    }


def compute_truncation_residuals(
    vel_fine: VelocityField,
    mesh_fine: StructuredMesh3D,
    mesh_coarse: StructuredMesh3D,
    bcs: BoundaryConditionSet,
) -> dict:
    """Compute coarse numerical advection truncation residual F_num vs exact SGS acceleration force F_SGS.

    F_num = N_h(bar(u)) - bar(N_fine(u_fine))
    F_SGS = -div(tau_exact)
    """
    from .convection import centered_convection

    # 1. Bar(u) on coarse grid
    vel_coarse = restrict_velocity_fine_to_coarse(vel_fine, mesh_fine, mesh_coarse, bcs)

    # 2. Coarse advection N_h(bar(u))
    conv_coarse = centered_convection(vel_coarse, mesh_coarse)

    # 3. Fine advection N_fine(u_fine) restricted to coarse scale bar(N_fine(u))
    conv_fine = centered_convection(vel_fine, mesh_fine)
    conv_fine_restricted = restrict_velocity_fine_to_coarse(conv_fine, mesh_fine, mesh_coarse, bcs)

    # Truncation residual F_num = N_h(bar(u)) - bar(N_fine(u))
    f_conv_u = conv_coarse.u.interior - conv_fine_restricted.u.interior
    f_conv_v = conv_coarse.v.interior - conv_fine_restricted.v.interior
    f_conv_w = conv_coarse.w.interior - conv_fine_restricted.w.interior

    norm_f_conv = float(np.sqrt(np.mean(f_conv_u**2) + np.mean(f_conv_v**2) + np.mean(f_conv_w**2)))

    # Viscous truncation F_visc = D_{nu,h}(bar(u)) - bar(D_{nu,fine}(u))
    from .operators import velocity_laplacian
    lap_coarse = velocity_laplacian(vel_coarse, mesh_coarse)
    lap_fine = velocity_laplacian(vel_fine, mesh_fine)
    lap_fine_restricted = restrict_velocity_fine_to_coarse(lap_fine, mesh_fine, mesh_coarse, bcs)

    f_visc_u = lap_coarse.u.interior - lap_fine_restricted.u.interior
    f_visc_v = lap_coarse.v.interior - lap_fine_restricted.v.interior
    f_visc_w = lap_coarse.w.interior - lap_fine_restricted.w.interior
    norm_f_visc = float(np.sqrt(np.mean(f_visc_u**2) + np.mean(f_visc_v**2) + np.mean(f_visc_w**2)))

    norm_f_num = norm_f_conv

    # 4. Exact SGS stress and acceleration force F_SGS = -div(tau_exact)
    tau_exact = compute_exact_sgs_stress(vel_fine, mesh_fine, mesh_coarse, bcs)
    dx, dy, dz = mesh_coarse.dx, mesh_coarse.dy, mesh_coarse.dz
    tau_xx = tau_exact["dev_xx"]
    tau_xy = tau_exact["dev_xy"]
    tau_xz = tau_exact["dev_xz"]

    d_tau_xx_dx = np.gradient(tau_xx, dx, axis=0)
    d_tau_xy_dy = np.gradient(tau_xy, dy, axis=1)
    d_tau_xz_dz = np.gradient(tau_xz, dz, axis=2)

    f_sgs_u = -(d_tau_xx_dx + d_tau_xy_dy + d_tau_xz_dz)
    norm_f_sgs = float(np.sqrt(np.mean(f_sgs_u**2)))

    ratio_num_sgs = float(norm_f_num / (norm_f_sgs + 1e-15))

    return {
        "norm_f_conv": norm_f_conv,
        "norm_f_visc": norm_f_visc,
        "norm_f_num": norm_f_num,
        "norm_f_sgs": norm_f_sgs,
        "ratio_num_sgs": ratio_num_sgs,
    }


def compute_energy_budget(
    vel_n: VelocityField,
    vel_np1: VelocityField,
    dt: float,
    mesh: StructuredMesh3D,
    bcs: BoundaryConditionSet,
    nu: float,
    nu_t: ScalarField | None = None,
) -> dict:
    """Compute discrete timestep kinetic energy budget and infer equivalent numerical viscosity nu_num.

    Delta K = K^{n+1} - K^n
    Delta K_visc = -dt * sum(2 nu S_ij S_ij dV)
    Delta K_sgs = -dt * sum(2 nu_t S_ij S_ij dV)
    nu_num ~ unexplained energy dissipation / (2 dt sum S_ij S_ij dV)
    """
    dV = mesh.cell_volume
    K_n = 0.5 * np.sum(vel_n.u.interior[:-1, :, :]**2 + vel_n.v.interior[:, :-1, :]**2 + vel_n.w.interior[:, :, :-1]**2) * dV
    K_np1 = 0.5 * np.sum(vel_np1.u.interior[:-1, :, :]**2 + vel_np1.v.interior[:, :-1, :]**2 + vel_np1.w.interior[:, :, :-1]**2) * dV
    delta_K = float(K_np1 - K_n)

    strain = compute_strain_components(vel_n, mesh, bcs)
    S_xx = strain["s_xx"]
    S_yy = strain["s_yy"]
    S_zz = strain["s_zz"]
    S_xy = strain["s_xy"]
    S_xz = strain["s_xz"]
    S_yz = strain["s_yz"]

    two_S_sq = np.sum(2.0 * (S_xx**2 + S_yy**2 + S_zz**2)) * dV + np.sum(4.0 * S_xy**2) * dV + np.sum(4.0 * S_xz**2) * dV + np.sum(4.0 * S_yz**2) * dV

    delta_K_visc = float(-dt * nu * two_S_sq)
    delta_K_sgs = float(-dt * np.sum(nu_t.interior * (S_xx**2 + S_yy**2 + S_zz**2)) * dV) if nu_t is not None else 0.0

    delta_K_unexplained = float(delta_K - (delta_K_visc + delta_K_sgs))

    nu_num = float(abs(delta_K_unexplained) / (2.0 * dt * max(1e-15, two_S_sq)))

    return {
        "delta_K": delta_K,
        "delta_K_visc": delta_K_visc,
        "delta_K_sgs": delta_K_sgs,
        "delta_K_unexplained": delta_K_unexplained,
        "nu_num": nu_num,
        "nu_num_over_nu": float(nu_num / max(1e-15, nu)),
    }
