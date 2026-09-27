"""
Deterministic Mathematical & Numerical Test Suite for NS-NONLINEAR-SELF-FOCUS-001.

Verifies:
1. Branch Closure & Task Envelope Governance Invariants:
   - OpenAI unforced linear-precursor branch closed as COMPLETED_NEGATIVE_RESEARCH_BRANCH
   - Clay Statement B = UNRESOLVED, Release = NO-GO, Deployment Authority = NONE, B2 = BLOCKED
   - NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED untouched
2. Parabolic Scale-Invariance Audit (Section 9, 11, 12):
   - Exact scaling weight w of u_lambda, omega_lambda, S_lambda, grad(omega_lambda), Delta(omega_lambda)
   - Scale invariance (lambda^0) of S_0(x,t) = |S omega| / (nu |Delta omega|)
   - Scale covariance (lambda^{-1}) of ell_omega(x,t) = |omega| / |grad omega|
   - Scale invariance (lambda^0) of R_omega = |S| ell_omega^2 / nu and R_{omega,signed} = lambda_omega ell_omega^2 / nu
   - Exact Inverse Length-Scale Decomposition: ell_omega^{-2} = |grad ln|omega||^2 + |grad xi|^2
3. Exact Local & Global Enstrophy Identities & CLM-041 (Section 7, 8, 10, 20):
   - A(t) = P(t)/D(t) = (bar_lambda_omega(t) * bar_ell_omega(t)^2) / nu
   - Mandatory Scale-Competition Lower Bound: lambda_1^+(t) * bar_ell_omega(t)^2 / nu >= A(t)
   - Dyadic High-Shell Dissipation Concentration: sum_{q >= Q_*(t)} D_q^omega >= (1/2) D(t)
   - Beltrami-Subtracted Lagrangian Identity: omega . S omega - (1/2)(u . grad)|omega|^2 = omega . curl(u x omega)
4. Falsification-First Counterexample Matrix & Spectral Numerical Diagnostics (Section 13, 21):
   - Pure Shear & 2D-in-3D Flow: R_omega >> 1 (false positive) vs S_eps == 0, R_{omega,signed} == 0, A(t) == 0
   - ABC Beltrami Flow (A,B,C != 0): pointwise omega . S omega != 0 (false positive) vs Beltrami-subtracted == 0 and global P(t) == 0
   - Taylor-Green Vortex: P(0) == 0, bar_ell_omega(0) == 1/sqrt(3), and forward spectral evolution to t > 0 produces P(t) > 0, A(t) > 1, and shrinking bar_ell_omega(t) < 1/sqrt(3)
   - Interacting Periodic Vortex Tubes: immediate P(0) > 0 and A(0) > 1 for nu < nu_crit
"""

import os
import yaml
import numpy as np
import pytest

from navier3d.math_assurance.claims import ClaimManager


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ═══════════════════════════════════════════════════════════════════════
# PSEUDO-SPECTRAL FOURIER CALCULUS HELPER ON T^3 = [0, 2*pi)^3
# ═══════════════════════════════════════════════════════════════════════

class SpectralTorus3D:
    """Exact pseudo-spectral vector calculus on T^3 = [0, 2*pi)^3."""

    def __init__(self, N: int = 16):
        self.N = N
        coords = np.linspace(0.0, 2.0 * np.pi, N, endpoint=False)
        self.X, self.Y, self.Z = np.meshgrid(coords, coords, coords, indexing="ij")
        k1d = np.fft.fftfreq(N, d=1.0 / N)
        self.KX, self.KY, self.KZ = np.meshgrid(k1d, k1d, k1d, indexing="ij")
        self.K2 = self.KX**2 + self.KY**2 + self.KZ**2
        self.dV = (2.0 * np.pi / N) ** 3

    def grad_scalar(self, f: np.ndarray) -> np.ndarray:
        f_hat = np.fft.fftn(f)
        df_dx = np.fft.ifftn(1j * self.KX * f_hat).real
        df_dy = np.fft.ifftn(1j * self.KY * f_hat).real
        df_dz = np.fft.ifftn(1j * self.KZ * f_hat).real
        return np.stack([df_dx, df_dy, df_dz], axis=0)

    def jacobian_vec(self, u: np.ndarray) -> np.ndarray:
        """Return J[i, j] = d u_i / d x_j of shape (3, 3, N, N, N)."""
        return np.stack([self.grad_scalar(u[i]) for i in range(3)], axis=0)

    def curl(self, u: np.ndarray) -> np.ndarray:
        J = self.jacobian_vec(u)
        w0 = J[2, 1] - J[1, 2]
        w1 = J[0, 2] - J[2, 0]
        w2 = J[1, 0] - J[0, 1]
        return np.stack([w0, w1, w2], axis=0)

    def div(self, u: np.ndarray) -> np.ndarray:
        J = self.jacobian_vec(u)
        return J[0, 0] + J[1, 1] + J[2, 2]

    def laplacian_vec(self, u: np.ndarray) -> np.ndarray:
        out = np.zeros_like(u)
        for i in range(3):
            u_hat = np.fft.fftn(u[i])
            out[i] = np.fft.ifftn(-self.K2 * u_hat).real
        return out

    def leray_project(self, v: np.ndarray) -> np.ndarray:
        v_hat = np.stack([np.fft.fftn(v[i]) for i in range(3)], axis=0)
        k_dot_v = self.KX * v_hat[0] + self.KY * v_hat[1] + self.KZ * v_hat[2]
        k2_safe = np.where(self.K2 == 0, 1.0, self.K2)
        K_vec = [self.KX, self.KY, self.KZ]
        p_hat = [v_hat[i] - (k_dot_v / k2_safe) * K_vec[i] for i in range(3)]
        for i in range(3):
            p_hat[i][self.K2 == 0] = 0.0
        return np.stack([np.fft.ifftn(p_hat[i]).real for i in range(3)], axis=0)

    def integrate(self, f: np.ndarray) -> float:
        return float(np.sum(f) * self.dV)

    def compute_diagnostics(self, u: np.ndarray, nu: float = 0.01, eps: float = 1e-12):
        omega = self.curl(u)
        J_u = self.jacobian_vec(u)
        S = 0.5 * (J_u + np.swapaxes(J_u, 0, 1))
        J_w = self.jacobian_vec(omega)
        lap_w = self.laplacian_vec(omega)

        # Pointwise norms
        w_sq = np.sum(omega**2, axis=0)
        w_norm = np.sqrt(w_sq)
        grad_w_sq = np.sum(J_w**2, axis=(0, 1))
        S_sq = np.sum(S**2, axis=(0, 1))
        S_norm = np.sqrt(S_sq)
        lap_w_norm = np.sqrt(np.sum(lap_w**2, axis=0))

        # S * omega vector
        S_omega = np.einsum("ijxyz,jxyz->ixyz", S, omega)
        S_omega_norm = np.sqrt(np.sum(S_omega**2, axis=0))
        w_dot_Sw = np.sum(omega * S_omega, axis=0)

        # Signed stretching rate lambda_omega = (omega . S omega) / |omega|^2
        lambda_omega = np.where(w_sq > eps, w_dot_Sw / np.maximum(w_sq, eps), 0.0)

        # Local length scale ell_omega^2 = (|omega|^2 + eps) / |grad omega|^2
        ell_w_sq = (w_sq + eps) / np.maximum(grad_w_sq, eps)

        # Candidate diagnostics
        S_diag = S_omega_norm / (nu * lap_w_norm + eps)
        R_unsigned = S_norm * ell_w_sq / nu
        R_signed = lambda_omega * ell_w_sq / nu

        # Beltrami-subtracted Lagrangian production: omega . S omega - (1/2) (u . grad)|omega|^2
        # Using exact Jacobian product rule: (1/2) d(|omega|^2)/dx_j = omega_i * J_w[i, j]
        grad_half_w_sq_vec = np.einsum("ixyz,ijxyz->jxyz", omega, J_w)
        u_dot_grad_half_w_sq = np.sum(u * grad_half_w_sq_vec, axis=0)
        lagrangian_prod = w_dot_Sw - u_dot_grad_half_w_sq

        # Exact solenoidal Lamb vector curl: curl(u x omega)_i = (omega . grad)u_i - (u . grad)omega_i
        w_dot_grad_u = np.einsum("jxyz,ijxyz->ixyz", omega, J_u)
        u_dot_grad_w = np.einsum("jxyz,ijxyz->ixyz", u, J_w)
        curl_lamb = w_dot_grad_u - u_dot_grad_w
        w_dot_curl_lamb = np.sum(omega * curl_lamb, axis=0)

        # Global quantities
        enstrophy = self.integrate(w_sq)
        palinstrophy = self.integrate(grad_w_sq)
        P_global = self.integrate(w_dot_Sw)
        D_global = nu * palinstrophy
        A_global = P_global / D_global if D_global > 0 else 0.0
        bar_ell_omega = np.sqrt(enstrophy / palinstrophy) if palinstrophy > 0 else 0.0
        bar_lambda_omega = P_global / enstrophy if enstrophy > 0 else 0.0

        return {
            "omega": omega,
            "S": S,
            "w_sq": w_sq,
            "w_norm": w_norm,
            "grad_w_sq": grad_w_sq,
            "w_dot_Sw": w_dot_Sw,
            "lambda_omega": lambda_omega,
            "ell_w_sq": ell_w_sq,
            "S_diag": S_diag,
            "R_unsigned": R_unsigned,
            "R_signed": R_signed,
            "lagrangian_prod": lagrangian_prod,
            "w_dot_curl_lamb": w_dot_curl_lamb,
            "enstrophy": enstrophy,
            "palinstrophy": palinstrophy,
            "P_global": P_global,
            "D_global": D_global,
            "A_global": A_global,
            "bar_ell_omega": bar_ell_omega,
            "bar_lambda_omega": bar_lambda_omega,
        }

    def rhs_ns(self, u: np.ndarray, nu: float) -> np.ndarray:
        """Exact pseudo-spectral RHS of unforced NS: P(u x omega) + nu Delta u."""
        omega = self.curl(u)
        u_cross_w = np.cross(u, omega, axis=0)
        conv_proj = self.leray_project(u_cross_w)
        return conv_proj + nu * self.laplacian_vec(u)

    def step_rk4(self, u: np.ndarray, dt: float, nu: float) -> np.ndarray:
        k1 = self.rhs_ns(u, nu)
        k2 = self.rhs_ns(u + 0.5 * dt * k1, nu)
        k3 = self.rhs_ns(u + 0.5 * dt * k2, nu)
        k4 = self.rhs_ns(u + dt * k3, nu)
        return self.leray_project(u + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4))


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1: Branch Closure & Task Envelope Governance Verification
# ═══════════════════════════════════════════════════════════════════════

class TestBranchClosureAndProgrammeGovernance:
    """Verify formal closure of OpenAI precursor branch and opening of NS-NONLINEAR-SELF-FOCUS-001."""

    def test_branch_closure_record_and_state(self):
        closure_path = os.path.join(REPO_ROOT, "NS_OPENAI_UNFORCED_TRANSFER_BRANCH_CLOSURE.md")
        assert os.path.exists(closure_path)
        with open(closure_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "COMPLETED_NEGATIVE_RESEARCH_BRANCH" in content
        assert "CLM-040" in content
        assert "NS-OBS-020B-R4" in content
        assert "NEG-EV-046" in content
        assert "NS-OPENAI-B2 = BLOCKED" in content

    def test_task_envelope_invariants(self):
        env_path = os.path.join(REPO_ROOT, "NS_NONLINEAR_SELF_FOCUS_001_TASK_ENVELOPE.yaml")
        assert os.path.exists(env_path)
        with open(env_path, "r", encoding="utf-8") as f:
            env = yaml.safe_load(f)
        assert env["task_id"] == "NS-NONLINEAR-SELF-FOCUS-001"
        assert env["predecessor_final_state"] == "COMPLETED_NEGATIVE_RESEARCH_BRANCH"
        assert env["governance"] == "UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3"
        assert env["mathematical_authority"] == "Mathematical Research Constitution v1.0.1"
        assert env["governance_migration_status"] == "NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED"
        assert env["target"]["clay_statement_b"] == "UNRESOLVED"
        assert env["target"]["release_state"] == "NO-GO"
        assert env["target"]["deployment_authority"] == "NONE"
        assert env["target"]["b2_status"] == "BLOCKED"
        assert env["verdict"] in env["allowed_verdicts"]

    def test_claim_041_passport_valid(self):
        cm = ClaimManager()
        c041 = cm.get_claim("CLM-041")
        assert c041 is not None
        res = cm.validate_passport(c041["passport"], c041.get("claim_type"))
        assert res["valid"] is True


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2: Parabolic Scale-Invariance & Inverse Length-Scale Decomposition
# ═══════════════════════════════════════════════════════════════════════

class TestParabolicScaleInvariance:
    """Verify exact homogeneous scaling under u_lambda(x,t) = lambda u(lambda x, lambda^2 t)."""

    def test_parabolic_rescaling_weights_and_invariance(self):
        spec = SpectralTorus3D(N=16)
        X, Y, Z = spec.X, spec.Y, spec.Z

        # Construct smooth 3D velocity field u_1(x) and its lambda=2 rescaled partner u_2(x) = 2 u_1(2x)
        def eval_u(x, y, z, scale_lam=1.0):
            lx, ly, lz = scale_lam * x, scale_lam * y, scale_lam * z
            u0 = scale_lam * (np.sin(lx) * np.cos(ly) * np.cos(lz))
            u1 = scale_lam * (-np.cos(lx) * np.sin(ly) * np.cos(lz))
            u2 = scale_lam * (0.5 * np.sin(2 * lx) * np.sin(ly) - 0.5 * np.cos(lx) * np.cos(ly) * np.sin(2 * lz))
            return np.stack([u0, u1, u2], axis=0)

        u_base = spec.leray_project(eval_u(X, Y, Z, scale_lam=1.0))
        u_scaled = spec.leray_project(eval_u(X, Y, Z, scale_lam=2.0))

        d1 = spec.compute_diagnostics(u_base, nu=0.02, eps=0.0)
        d2 = spec.compute_diagnostics(u_scaled, nu=0.02, eps=0.0)

        # Under lambda = 2 on T^3:
        # ||omega_2||_{L^\infty} = 2^2 ||omega_1||_{L^\infty} = 4 ||omega_1||_{L^\infty}
        assert np.isclose(np.max(d2["w_norm"]), 4.0 * np.max(d1["w_norm"]), rtol=1e-10)
        # Global active scale bar_ell_omega scales as lambda^{-1} = 1/2
        assert np.isclose(d2["bar_ell_omega"], 0.5 * d1["bar_ell_omega"], rtol=1e-10)
        # Global enstrophy-weighted stretching rate bar_lambda_omega scales as lambda^{+2} = 4
        assert np.isclose(d2["bar_lambda_omega"], 4.0 * d1["bar_lambda_omega"], rtol=1e-10)
        # Global amplification ratio A = (bar_lambda_omega * bar_ell_omega^2) / nu is STRICTLY INVARIANT (lambda^0)
        assert np.isclose(d2["A_global"], d1["A_global"], rtol=1e-10)

    def test_orthogonal_inverse_length_scale_decomposition(self):
        """Verify exact identity |grad omega|^2 / |omega|^2 == |grad ln|omega||^2 + |grad xi|^2."""
        spec = SpectralTorus3D(N=16)
        X, Y, Z = spec.X, spec.Y, spec.Z
        # Smooth divergence-free velocity field
        u = np.stack([
            np.sin(X) * np.cos(Y) + 0.7 * np.cos(Z),
            -np.cos(X) * np.sin(Y) + 0.7 * np.sin(Z),
            0.5 * np.sin(Y) * np.cos(Z) + 0.4 * np.cos(X)
        ], axis=0)
        u = spec.leray_project(u)
        omega = spec.curl(u)
        w_sq = np.sum(omega**2, axis=0)
        w_norm = np.sqrt(w_sq)
        mask = w_norm > 0.2

        # Exact Jacobian of trigonometric polynomial omega via FFT
        J_w = spec.jacobian_vec(omega)
        grad_w_sq = np.sum(J_w**2, axis=(0, 1))
        lhs = grad_w_sq[mask] / w_sq[mask]

        # By exact chain rule from J_w[i, j] = d omega_i / d x_j:
        # d |omega| / d x_j = xi_i * J_w[i, j], and d xi_i / d x_j = (J_w[i, j] - xi_i * (xi_k * J_w[k, j])) / |omega|
        xi = omega / np.maximum(w_norm[None, ...], 1e-15)
        grad_w_norm_exact = np.einsum("ixyz,ijxyz->jxyz", xi, J_w)
        grad_ln_w_sq = np.sum(grad_w_norm_exact**2, axis=0)[mask] / w_sq[mask]

        J_xi_exact = (J_w - xi[:, None, ...] * grad_w_norm_exact[None, :, ...]) / np.maximum(w_norm[None, None, ...], 1e-15)
        grad_xi_sq = np.sum(J_xi_exact**2, axis=(0, 1))[mask]

        np.testing.assert_allclose(lhs, grad_ln_w_sq + grad_xi_sq, rtol=1e-13, atol=1e-13)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3: Falsification-First Counterexamples & CLM-041 Verification
# ═══════════════════════════════════════════════════════════════════════

class TestFalsificationCounterexampleMatrix:
    """Verify all counterexample behaviors from NS_NONLINEAR_SELF_FOCUS_001_COUNTEREXAMPLE_MATRIX.md."""

    def test_pure_shear_and_2d_flow_falsify_unsigned_R_omega(self):
        """Pure shear has R_unsigned >> 1 (false positive) while S_diag == 0, R_signed == 0, A == 0."""
        spec = SpectralTorus3D(N=16)
        u_shear = np.stack([
            5.0 * np.sin(spec.Y),
            np.zeros_like(spec.Y),
            np.zeros_like(spec.Y),
        ], axis=0)
        d = spec.compute_diagnostics(u_shear, nu=0.01)

        # Unsigned R_omega is large (> 50)
        assert np.max(d["R_unsigned"]) > 50.0
        # Vector stretching S*omega, signed R_omega, and global A(t) are identically zero
        np.testing.assert_allclose(d["S_diag"], 0.0, atol=1e-13)
        np.testing.assert_allclose(d["R_signed"], 0.0, atol=1e-13)
        assert abs(d["A_global"]) < 1e-14

    def test_abc_beltrami_flow_falsifies_unsubtracted_pointwise_stretching(self):
        """
        On general ABC Beltrami flow (omega = u, A,B,C != 0), pointwise omega . S omega != 0
        (false positive for naive lambda_omega > 0), but Beltrami-subtracted Lagrangian production
        omega . S omega - (1/2)(u . grad)|omega|^2 == 0 everywhere and global P(t) == 0.
        """
        spec = SpectralTorus3D(N=16)
        X, Y, Z = spec.X, spec.Y, spec.Z
        A, B, C = 1.0, 0.7, 0.5
        u_abc = np.stack([
            A * np.sin(Z) + C * np.cos(Y),
            B * np.sin(X) + A * np.cos(Z),
            C * np.sin(Y) + B * np.cos(X),
        ], axis=0)

        # Verify strong Beltrami property curl(u_abc) == u_abc
        omega_abc = spec.curl(u_abc)
        np.testing.assert_allclose(omega_abc, u_abc, atol=1e-13)

        d = spec.compute_diagnostics(u_abc, nu=0.01)
        # Pointwise omega . S omega is NON-ZERO (> 0.2) because |u_abc|^2 is spatially varying
        assert np.max(d["w_dot_Sw"]) > 0.2
        assert np.max(d["S_diag"]) > 5.0
        assert np.max(d["R_signed"]) > 5.0

        # Yet Beltrami-subtracted Lagrangian production and global production vanish identically!
        np.testing.assert_allclose(d["lagrangian_prod"], 0.0, atol=1e-12)
        np.testing.assert_allclose(d["w_dot_curl_lamb"], 0.0, atol=1e-12)
        assert abs(d["P_global"]) < 1e-12
        assert abs(d["A_global"]) < 1e-12

    def test_taylor_green_transient_self_focusing_and_clm041_identities(self):
        """
        Verify Taylor-Green vortex at t=0 has P(0)=0, bar_ell_omega(0)=1/sqrt(3),
        and forward RK4 evolution to t=0.15 (at high amplitude / low nu=0.002) generates
        P(t)>0, A(t)>1, enstrophy growth, and shrinking bar_ell_omega(t) < 1/sqrt(3).
        Also verify CLM-041 Parts I, II, III, IV.
        """
        spec = SpectralTorus3D(N=16)
        X, Y, Z = spec.X, spec.Y, spec.Z
        u_tg0 = 2.0 * np.stack([
            np.sin(X) * np.cos(Y) * np.cos(Z),
            -np.cos(X) * np.sin(Y) * np.cos(Z),
            np.zeros_like(X),
        ], axis=0)

        nu = 0.002
        d0 = spec.compute_diagnostics(u_tg0, nu=nu)
        assert np.isclose(d0["bar_ell_omega"], 1.0 / np.sqrt(3.0), rtol=1e-12)
        assert abs(d0["P_global"]) < 1e-12
        assert abs(d0["A_global"]) < 1e-12

        # Forward evolve to t = 0.15 via RK4
        u = u_tg0.copy()
        dt = 0.025
        for _ in range(6):
            u = spec.step_rk4(u, dt=dt, nu=nu)

        dt_diag = spec.compute_diagnostics(u, nu=nu)

        # 1. Enstrophy increased and active scale bar_ell_omega shrank!
        assert dt_diag["enstrophy"] > d0["enstrophy"]
        assert dt_diag["bar_ell_omega"] < d0["bar_ell_omega"]
        assert dt_diag["P_global"] > 0.0
        assert dt_diag["A_global"] > 1.0

        # 2. Verify CLM-041 Part I exact identity: A(t) == bar_lambda_omega * bar_ell_omega^2 / nu
        clm041_rhs = (dt_diag["bar_lambda_omega"] * (dt_diag["bar_ell_omega"] ** 2)) / nu
        assert np.isclose(dt_diag["A_global"], clm041_rhs, rtol=1e-12)

        # 3. Verify CLM-041 Part II mandatory scale-competition lower bound
        lambda_1_plus = float(np.max(np.maximum(dt_diag["lambda_omega"], 0.0)))
        assert (lambda_1_plus * (dt_diag["bar_ell_omega"] ** 2)) / nu >= dt_diag["A_global"] > 1.0
        lower_bracket = np.sqrt(nu * dt_diag["A_global"] / lambda_1_plus)
        assert lower_bracket <= dt_diag["bar_ell_omega"] <= 1.0

        # 4. Verify CLM-041 Part III dyadic high-shell dissipation concentration (>= 50% of D(t))
        Q_star = max(0, int(np.floor(0.5 * np.log2(1.0 / (2.0 * (dt_diag["bar_ell_omega"] ** 2))))))
        w_hat = np.stack([np.fft.fftn(dt_diag["omega"][i]) for i in range(3)], axis=0)
        k_norm = np.sqrt(spec.K2)
        high_mask = k_norm >= (2.0 ** Q_star)
        parseval_factor = ((2.0 * np.pi) ** 3) / (spec.N ** 6)
        D_high = nu * parseval_factor * float(np.sum(spec.K2[None, ...] * (np.abs(w_hat) ** 2) * high_mask[None, ...]))
        assert D_high >= 0.5 * dt_diag["D_global"]

        # 5. Verify CLM-041 Part IV Beltrami-subtracted identity pointwise and globally
        np.testing.assert_allclose(dt_diag["lagrangian_prod"], dt_diag["w_dot_curl_lamb"], atol=1e-10)
        assert np.isclose(spec.integrate(dt_diag["w_dot_curl_lamb"]), dt_diag["P_global"], rtol=1e-8)

    def test_interacting_vortex_tubes_immediate_amplification(self):
        """
        Verify a multi-shell 3D resonant triad of periodic vortex tubes:
        k_1 = (1,0,0) [|k_1|^2=1], k_2 = (0,1,1) [|k_2|^2=2], k_3 = (1,1,1) [|k_3|^2=3]
        (spanning 3 distinct wavenumber shells so ||omega||_2^2 != const * ||u||_2^2)
        achieves P(0) > 0 and A(0) > 1 immediately at t=0 without backward heat reconstruction.
        """
        spec = SpectralTorus3D(N=16)
        X, Y, Z = spec.X, spec.Y, spec.Z
        # Multi-shell 3D triad: k_1 = (1,0,0), k_2 = (0,1,1), k_3 = (1,1,1) with k_1 + k_2 = k_3
        u_1 = np.stack([np.zeros_like(X), np.sin(X), np.cos(X)], axis=0)
        u_2 = np.stack([np.sin(Y + Z), np.cos(Y + Z), -np.cos(Y + Z)], axis=0)
        u_3 = np.stack([np.sin(X + Y + Z), -2.0 * np.sin(X + Y + Z), np.sin(X + Y + Z)], axis=0)
        u_init = spec.leray_project(3.0 * (u_1 + u_2 + u_3))

        d = spec.compute_diagnostics(u_init, nu=0.01)
        if d["P_global"] < 0:
            u_init = -u_init
            d = spec.compute_diagnostics(u_init, nu=0.01)

        assert d["P_global"] > 1.0
        assert d["A_global"] > 1.0
        assert np.isclose(d["A_global"], d["bar_lambda_omega"] * (d["bar_ell_omega"] ** 2) / 0.01, rtol=1e-12)

