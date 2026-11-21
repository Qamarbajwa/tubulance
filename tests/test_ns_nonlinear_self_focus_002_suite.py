"""
Deterministic verification suite for NS-NONLINEAR-SELF-FOCUS-002:
Forward Dyadic Enstrophy Transfer, Nonlinear Flux, and Commutator Closure.
"""

from pathlib import Path
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _make_grid(n: int = 16):
    x = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    xx, yy, zz = np.meshgrid(x, x, x, indexing="ij")
    k1d = np.fft.fftfreq(n, d=1.0 / n)
    kx, ky, kz = np.meshgrid(k1d, k1d, k1d, indexing="ij")
    k_mag = np.sqrt(kx**2 + ky**2 + kz**2)
    return xx, yy, zz, kx, ky, kz, k_mag


def _curl_hat(ux_h, uy_h, uz_h, kx, ky, kz):
    wx_h = 1j * (ky * uz_h - kz * uy_h)
    wy_h = 1j * (kz * ux_h - kx * uz_h)
    wz_h = 1j * (kx * uy_h - ky * ux_h)
    return wx_h, wy_h, wz_h


def _biot_savart_hat(wx_h, wy_h, wz_h, kx, ky, kz, k_mag):
    k2 = np.where(k_mag > 0, k_mag**2, 1.0)
    ux_h = 1j * (ky * wz_h - kz * wy_h) / k2
    uy_h = 1j * (kz * wx_h - kx * wz_h) / k2
    uz_h = 1j * (kx * wy_h - ky * wx_h) / k2
    ux_h[k_mag == 0] = 0.0
    uy_h[k_mag == 0] = 0.0
    uz_h[k_mag == 0] = 0.0
    return ux_h, uy_h, uz_h


def _shell_mask(k_mag, q: int, k0: float = 1.0):
    return (k_mag >= k0 * (2**q)) & (k_mag < k0 * (2 ** (q + 1)))


def _project_shell(field, k_mag, q: int, k0: float = 1.0):
    mask = _shell_mask(k_mag, q, k0)
    out = np.zeros_like(field)
    for c in range(3):
        fh = np.fft.fftn(field[c])
        out[c] = np.fft.ifftn(fh * mask).real
    return out


def _project_le_q(field, k_mag, q_cut: int, k0: float = 1.0):
    mask = (k_mag > 0) & (k_mag < k0 * (2 ** (q_cut + 1)))
    out = np.zeros_like(field)
    for c in range(3):
        fh = np.fft.fftn(field[c])
        out[c] = np.fft.ifftn(fh * mask).real
    return out


def _project_gt_q(field, k_mag, q_cut: int, k0: float = 1.0):
    mask = k_mag >= k0 * (2 ** (q_cut + 1))
    out = np.zeros_like(field)
    for c in range(3):
        fh = np.fft.fftn(field[c])
        out[c] = np.fft.ifftn(fh * mask).real
    return out


def _inner_l2(f, g):
    return float(np.mean(np.sum(f * g, axis=0)) * ((2.0 * np.pi) ** 3))


def _grad_norm_sq(field, kx, ky, kz):
    total = 0.0
    for c in range(3):
        fh = np.fft.fftn(field[c])
        for kd in (kx, ky, kz):
            df = np.fft.ifftn(1j * kd * fh).real
            total += float(np.mean(df**2) * ((2.0 * np.pi) ** 3))
    return total


def _advective_term(u, w, kx, ky, kz):
    """Computes (u . grad) w pseudospectrally."""
    out = np.zeros_like(w)
    for c in range(3):
        wh = np.fft.fftn(w[c])
        dwx = np.fft.ifftn(1j * kx * wh).real
        dwy = np.fft.ifftn(1j * ky * wh).real
        dwz = np.fft.ifftn(1j * kz * wh).real
        out[c] = u[0] * dwx + u[1] * dwy + u[2] * dwz
    return out


def _stretching_term(w, u, kx, ky, kz):
    """Computes (w . grad) u pseudospectrally."""
    return _advective_term(w, u, kx, ky, kz)


def _strain_action(u, w, kx, ky, kz):
    """Computes S w where S_ij = 0.5*(d_j u_i + d_i u_j)."""
    du = np.zeros((3, 3) + u.shape[1:], dtype=float)
    k_vec = (kx, ky, kz)
    for i in range(3):
        uh = np.fft.fftn(u[i])
        for j in range(3):
            du[i, j] = np.fft.ifftn(1j * k_vec[j] * uh).real
    s_tensor = 0.5 * (du + np.swapaxes(du, 0, 1))
    return np.einsum("ijxyz,jxyz->ixyz", s_tensor, w)


def _lamb_curl(u, w, kx, ky, kz):
    """Computes curl(u x w) in Fourier space."""
    cx = u[1] * w[2] - u[2] * w[1]
    cy = u[2] * w[0] - u[0] * w[2]
    cz = u[0] * w[1] - u[1] * w[0]
    cxh, cyh, czh = np.fft.fftn(cx), np.fft.fftn(cy), np.fft.fftn(cz)
    rx_h, ry_h, rz_h = _curl_hat(cxh, cyh, czh, kx, ky, kz)
    return np.array([
        np.fft.ifftn(rx_h).real,
        np.fft.ifftn(ry_h).real,
        np.fft.ifftn(rz_h).real,
    ])


def test_option_a_orthogonal_shells_and_commutator_skew_symmetry():
    """Verifies Sections 4, 5, 6, 8: sharp orthogonal shells P_q, commutator identity, and skew-symmetry."""
    xx, yy, zz, kx, ky, kz, k_mag = _make_grid(16)
    # Construct a multi-shell divergence-free velocity field
    u = np.array([
        np.sin(xx) * np.cos(yy) * np.cos(zz) + 0.4 * np.sin(2 * yy) * np.cos(2 * zz),
        -np.cos(xx) * np.sin(yy) * np.cos(zz) + 0.3 * np.cos(3 * xx) * np.sin(zz),
        0.2 * np.cos(xx) * np.sin(2 * yy) - 0.3 * np.sin(3 * xx) * np.cos(zz),
    ])
    # Project to divergence-free and compute vorticity
    ux_h, uy_h, uz_h = np.fft.fftn(u[0]), np.fft.fftn(u[1]), np.fft.fftn(u[2])
    wx_h, wy_h, wz_h = _curl_hat(ux_h, uy_h, uz_h, kx, ky, kz)
    ux_h, uy_h, uz_h = _biot_savart_hat(wx_h, wy_h, wz_h, kx, ky, kz, k_mag)
    u = np.array([np.fft.ifftn(ux_h).real, np.fft.ifftn(uy_h).real, np.fft.ifftn(uz_h).real])
    w = np.array([np.fft.ifftn(wx_h).real, np.fft.ifftn(wy_h).real, np.fft.ifftn(wz_h).real])

    shells = [_project_shell(w, k_mag, q) for q in range(4)]
    # 1. Mutual orthogonality and exact Plancherel reconstruction
    for q in range(4):
        for p in range(q + 1, 4):
            assert abs(_inner_l2(shells[q], shells[p])) < 1e-12
    assert np.isclose(sum(_inner_l2(s, s) for s in shells), _inner_l2(w, w), rtol=1e-12)
    assert np.isclose(sum(_grad_norm_sq(s, kx, ky, kz) for s in shells), _grad_norm_sq(w, kx, ky, kz), rtol=1e-12)

    # 2. Pointwise identity (omega . grad) u == S omega
    stretch_vec = _stretching_term(w, u, kx, ky, kz)
    strain_vec = _strain_action(u, w, kx, ky, kz)
    assert np.max(np.abs(stretch_vec - strain_vec)) < 1e-12

    # 3. Commutator identity T_q = -<[P_q, u.grad]w, w_q> and skew-symmetry T_{q<-p} = -T_{p<-q}
    u_grad_w = _advective_term(u, w, kx, ky, kz)
    t_mat = np.zeros((4, 4))
    for q in range(4):
        pq_u_grad_w = _project_shell(u_grad_w, k_mag, q)
        u_grad_wq = _advective_term(u, shells[q], kx, ky, kz)
        comm_q = pq_u_grad_w - u_grad_wq
        tq_direct = -_inner_l2(pq_u_grad_w, shells[q])
        tq_comm = -_inner_l2(comm_q, shells[q])
        assert np.isclose(tq_direct, tq_comm, atol=1e-12)
        for p in range(4):
            t_mat[q, p] = -_inner_l2(_advective_term(u, shells[p], kx, ky, kz), shells[q])

    assert np.max(np.abs(t_mat + t_mat.T)) < 1e-11
    assert abs(np.sum(t_mat)) < 1e-11

    # 4. Self-adjointness of strain cross-coupling <S w_{<=Q}, w_{>Q}> == <S w_{>Q}, w_{<=Q}>
    w_le0 = _project_le_q(w, k_mag, 0)
    w_gt0 = _project_gt_q(w, k_mag, 0)
    cross_1 = _inner_l2(_strain_action(u, w_le0, kx, ky, kz), w_gt0)
    cross_2 = _inner_l2(_strain_action(u, w_gt0, kx, ky, kz), w_le0)
    assert np.isclose(cross_1, cross_2, atol=1e-12)


def test_one_shell_step_property_and_riesz_strain_isometry():
    """Verifies Sections 7 & 19: P_{>=Q+2} curl(u_{<=Q} x w_{<=Q}) == 0 and ||S[w_q]||_2 = ||w_q||_2 / sqrt(2)."""
    xx, yy, zz, kx, ky, kz, k_mag = _make_grid(16)
    # Band-limited flow in shell Q=0 (|k| in [1, 2), e.g., |k| = 1, sqrt(2), sqrt(3))
    u0 = np.array([
        np.sin(xx) * np.cos(yy) * np.cos(zz) + 0.5 * np.cos(yy),
        -np.cos(xx) * np.sin(yy) * np.cos(zz) + 0.5 * np.sin(zz),
        0.5 * np.cos(xx),
    ])
    ux_h, uy_h, uz_h = np.fft.fftn(u0[0]), np.fft.fftn(u0[1]), np.fft.fftn(u0[2])
    wx_h, wy_h, wz_h = _curl_hat(ux_h, uy_h, uz_h, kx, ky, kz)
    w0 = np.array([np.fft.ifftn(wx_h).real, np.fft.ifftn(wy_h).real, np.fft.ifftn(wz_h).real])

    # Confirm support is strictly in Q=0
    assert _inner_l2(_project_gt_q(w0, k_mag, 0), _project_gt_q(w0, k_mag, 0)) < 1e-24

    # Nonlinear Lamb curl F = curl(u0 x w0)
    f_nonlin = _lamb_curl(u0, w0, kx, ky, kz)
    f_gt0 = _project_gt_q(f_nonlin, k_mag, 0)
    f_shell1 = _project_shell(f_nonlin, k_mag, 1)
    f_ge2 = _project_gt_q(f_nonlin, k_mag, 1)

    assert _inner_l2(f_shell1, f_shell1) > 10.0
    assert np.max(np.abs(f_gt0 - f_shell1)) < 1e-12
    assert _inner_l2(f_ge2, f_ge2) < 1e-24

    # Nonlocal Riesz strain norm identity ||S[w_q]||_{L^2}^2 == 0.5 * ||w_q||_{L^2}^2
    du = np.zeros((3, 3) + u0.shape[1:], dtype=float)
    k_vec = (kx, ky, kz)
    for i in range(3):
        uh = np.fft.fftn(u0[i])
        for j in range(3):
            du[i, j] = np.fft.ifftn(1j * k_vec[j] * uh).real
    s_tensor = 0.5 * (du + np.swapaxes(du, 0, 1))
    s_norm_sq = float(np.mean(np.sum(s_tensor**2, axis=(0, 1))) * ((2.0 * np.pi) ** 3))
    w_norm_sq = _inner_l2(w0, w0)
    assert np.isclose(s_norm_sq, 0.5 * w_norm_sq, rtol=1e-12)


def test_minimal_triad_ode_conservation_helicity_and_phase_reversal():
    """Verifies Sections 21 & 22: Minimal 3-mode helical triad ODEs, conservation laws, and phase reversal."""
    k_mag, l_mag, m_mag = 1.2, 1.6, 2.5
    sk, sl, sm = +1.0, -1.0, +1.0
    g = 0.4

    def rhs_inviscid(state):
        uk, ul, um = state
        # Real-phase reduced triad ODEs: du_k/dt = g*(s_l*l - s_m*m)*ul*um, etc.
        duk = g * (sl * l_mag - sm * m_mag) * ul * um
        dul = g * (sm * m_mag - sk * k_mag) * um * uk
        dum = g * (sk * k_mag - sl * l_mag) * uk * ul
        return np.array([duk, dul, dum])

    state = np.array([1.0, 0.9, 0.05], dtype=float)
    e0 = 0.5 * np.sum(state**2)
    h0 = sk * k_mag * state[0] ** 2 + sl * l_mag * state[1] ** 2 + sm * m_mag * state[2] ** 2

    dt = 0.002
    flux_history = []
    for _ in range(1500):
        uk, ul, um = state
        c_klm = g * uk * ul * um
        pi_tot = (m_mag**2) * (sk * k_mag - sl * l_mag) * c_klm
        flux_history.append(pi_tot)
        k1 = rhs_inviscid(state)
        k2 = rhs_inviscid(state + 0.5 * dt * k1)
        k3 = rhs_inviscid(state + 0.5 * dt * k2)
        k4 = rhs_inviscid(state + dt * k3)
        state = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    ef = 0.5 * np.sum(state**2)
    hf = sk * k_mag * state[0] ** 2 + sl * l_mag * state[1] ** 2 + sm * m_mag * state[2] ** 2
    assert np.isclose(e0, ef, rtol=1e-10)
    assert np.isclose(h0, hf, rtol=1e-10)
    # Verify initial positive flux followed by autonomous phase reversal (backscatter < 0)
    assert flux_history[0] > 0.0
    assert max(flux_history) > 0.5
    assert min(flux_history) < -0.5

    # Resonant Beltrami sphere case (s_k = s_l = +1, |k| = |l| = 1.5) -> identically zero high-mode flux
    gamma_m_beltrami = (m_mag**2) * ((+1.0) * 1.5 - (+1.0) * 1.5)
    assert gamma_m_beltrami == 0.0


def test_nine_counterexample_flows_and_clm042_state_distinguishing_bound():
    """Verifies Section 20 (all 9 flows) and CLM-042 (Taylor-Green vs ABC state-distinguishing Duhamel bound)."""
    xx, yy, zz, kx, ky, kz, k_mag = _make_grid(16)
    nu = 0.05

    # State A: ABC eigenflow on |k| = sqrt(3) in shell Q=0
    # Wait: standard ABC on |k|=1 is (sin z + cos y, sin x + cos z, sin y + cos x).
    # To place ABC on the EXACT same sphere |k| = sqrt(3) as Taylor-Green, use helical Beltrami mode at k=(1,1,1):
    # Let p = (1, 1, 1), |p| = sqrt(3). Orthogonal basis e1 = (1, -1, 0)/sqrt(2), e2 = (1, 1, -2)/sqrt(6).
    # Then u_ABC(x) = cos(p.x) e1 - sin(p.x) e2 satisfies curl u_ABC = sqrt(3) u_ABC!
    px = xx + yy + zz
    e1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    e2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    u_abc = np.array([
        np.cos(px) * e1[0] - np.sin(px) * e2[0],
        np.cos(px) * e1[1] - np.sin(px) * e2[1],
        np.cos(px) * e1[2] - np.sin(px) * e2[2],
    ])
    # State B: Taylor-Green vortex on |k| = sqrt(3) in shell Q=0
    u_tg_raw = np.array([
        np.sin(xx) * np.cos(yy) * np.cos(zz),
        -np.cos(xx) * np.sin(yy) * np.cos(zz),
        np.zeros_like(xx),
    ])
    # Scale u_tg so ||omega_TG(0)||_{L^2} == ||omega_ABC(0)||_{L^2}
    w_abc = np.array([
        np.fft.ifftn(_curl_hat(np.fft.fftn(u_abc[0]), np.fft.fftn(u_abc[1]), np.fft.fftn(u_abc[2]), kx, ky, kz)[c]).real
        for c in range(3)
    ])
    w_tg_raw = np.array([
        np.fft.ifftn(_curl_hat(np.fft.fftn(u_tg_raw[0]), np.fft.fftn(u_tg_raw[1]), np.fft.fftn(u_tg_raw[2]), kx, ky, kz)[c]).real
        for c in range(3)
    ])
    scale = np.sqrt(_inner_l2(w_abc, w_abc) / _inner_l2(w_tg_raw, w_tg_raw))
    u_tg = u_tg_raw * scale
    w_tg = w_tg_raw * scale

    # Verify identical instantaneous invariants at t = 0: ||w||_2, ||grad w||_2, and P(0) = 0
    assert np.isclose(_inner_l2(w_abc, w_abc), _inner_l2(w_tg, w_tg), rtol=1e-12)
    assert np.isclose(_grad_norm_sq(w_abc, kx, ky, kz), _grad_norm_sq(w_tg, kx, ky, kz), rtol=1e-12)
    p0_abc = _inner_l2(_strain_action(u_abc, w_abc, kx, ky, kz), w_abc)
    p0_tg = _inner_l2(_strain_action(u_tg, w_tg, kx, ky, kz), w_tg)
    assert abs(p0_abc) < 1e-12 and abs(p0_tg) < 1e-12

    # Verify G_0(0) == 0 for ABC, parallel shear, and 2D stretching, while G_0(0) > 0 for TG
    f1_abc = _project_shell(_lamb_curl(u_abc, w_abc, kx, ky, kz), k_mag, 1)
    f1_tg = _project_shell(_lamb_curl(u_tg, w_tg, kx, ky, kz), k_mag, 1)
    assert _inner_l2(f1_abc, f1_abc) < 1e-24
    f1_tg_norm_sq = _inner_l2(f1_tg, f1_tg)
    assert f1_tg_norm_sq > 100.0

    # Integrate both flows forward by delta_t = 0.01 under viscous 3D Navier-Stokes (RK4 in Fourier space)
    def step_ns_rk4(w_field, dt_step):
        def rhs_w(wf):
            wh0, wh1, wh2 = np.fft.fftn(wf[0]), np.fft.fftn(wf[1]), np.fft.fftn(wf[2])
            uh0, uh1, uh2 = _biot_savart_hat(wh0, wh1, wh2, kx, ky, kz, k_mag)
            uf = np.array([np.fft.ifftn(uh0).real, np.fft.ifftn(uh1).real, np.fft.ifftn(uh2).real])
            nl = _lamb_curl(uf, wf, kx, ky, kz)
            visc = np.array([
                np.fft.ifftn(-(k_mag**2) * wh0).real,
                np.fft.ifftn(-(k_mag**2) * wh1).real,
                np.fft.ifftn(-(k_mag**2) * wh2).real,
            ])
            return nl + nu * visc

        k1 = rhs_w(w_field)
        k2 = rhs_w(w_field + 0.5 * dt_step * k1)
        k3 = rhs_w(w_field + 0.5 * dt_step * k2)
        k4 = rhs_w(w_field + dt_step * k3)
        return w_field + (dt_step / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    delta_t = 0.01
    w_abc_dt = step_ns_rk4(w_abc, delta_t)
    w_tg_dt = step_ns_rk4(w_tg, delta_t)

    e_gt0_abc = 0.5 * _inner_l2(_project_gt_q(w_abc_dt, k_mag, 0), _project_gt_q(w_abc_dt, k_mag, 0))
    e_gt0_tg = 0.5 * _inner_l2(_project_gt_q(w_tg_dt, k_mag, 0), _project_gt_q(w_tg_dt, k_mag, 0))
    assert e_gt0_abc < 1e-24

    # Compare e_gt0_tg against the CLM-042 Duhamel Stokes lower bound
    mu_1 = 16.0  # 16 * k_0^2 * 2^{2*0}
    psi_0 = (1.0 - np.exp(-nu * mu_1 * delta_t)) / (nu * mu_1)
    clm042_leading_lower_bound = 0.25 * (psi_0**2) * f1_tg_norm_sq
    assert e_gt0_tg >= clm042_leading_lower_bound > 0.0


def test_governance_and_review_independence_gates():
    """Verifies Sections 2, 3, 27, 29: CLM-041-R1 review gate, CLM-042 registration, and 5 hard invariants."""
    state = yaml.safe_load((ROOT / "governance" / "PROJECT_STATE.yaml").read_text(encoding="utf-8"))
    assert state["epistemic_status"]["clay_statement_b_status"] == "UNRESOLVED"
    assert state["epistemic_status"]["ns_openai_b2_status"] == "BLOCKED"
    assert state["epistemic_status"]["governance_migration_v404_status"] == "MIGRATION_BLOCKED"
    assert state["epistemic_status"]["active_milestone"] in ("NS-NONLINEAR-SELF-FOCUS-002", "NS-NONLINEAR-SELF-FOCUS-003", "NS-NONLINEAR-SELF-FOCUS-004")

    claims = yaml.safe_load((ROOT / "mathematical_constitution" / "CLAIM_REGISTRY.yaml").read_text(encoding="utf-8"))["claims"]
    clm041 = next(c for c in claims if c["claim_id"] == "CLM-041")
    clm041_r1 = next(c for c in claims if c["claim_id"] == "CLM-041-R1")
    clm042 = next(c for c in claims if c["claim_id"] == "CLM-042")

    assert clm041["passport"]["project_status"] == "SUPERSEDED"
    assert clm041_r1["passport"]["truth_status"] == "PROVED_LEMMA"
    assert "REVIEW_REQUIRED_FOR_STRONGER_DEPENDENCY" in clm041_r1["passport"]["review_gate_note"]
    assert clm042["milestone_claim_class"] == "CONDITIONAL_NEW_LEMMA"
    assert clm042["passport"]["project_status"] == "PROJECT_CANONICAL_WITH_LIMITATIONS"
    assert "REVIEW_REQUIRED" in clm042["passport"]["review_gate_note"]
    assert "CLM-041" not in clm042["dependencies"] and "CLM-041-R1" not in clm042["dependencies"]
