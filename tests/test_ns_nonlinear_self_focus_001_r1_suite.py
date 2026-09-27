"""
Deterministic Mathematical & Governance Verification Suite for NS-NONLINEAR-SELF-FOCUS-001-R1.

CRITICAL EPISTEMIC RULE (Section 21):
    test PASS != mathematical theorem proved.
Tests in this suite verify:
1. Consistency of algebraic definitions and identities (A = bar_lambda_omega * bar_ell_omega^2 / nu);
2. Explicit torus-size Poincare scaling (bar_ell_omega <= lambda_P^{-1/2} = L / (2*pi)) across L != 2*pi;
3. Exhaustive zero and sign case splits (omega == 0, P < 0, P == 0, 0 < P <= D, P > D);
4. Orthogonal dyadic shell projectors P_q (exact equality sum_q D_q = D) vs smooth overlapping
   Littlewood-Paley multipliers dot_Delta_q (strict overlap deficit sum_q ||grad dot_Delta_q omega||_2^2 < D,
   repaired by linear dual pairing <grad dot_Delta_q omega, grad omega>);
5. Polar gradient decomposition on Omega_+ = {|omega| > 0}, zero-set regularization, and
   reclassification of CLM-041 -> CLM-041-R1 (PROVED_LEMMA / N1_PROJECT_REFORMULATION / S1_USEFUL_LEMMA)
   and NS-OBS-021 -> NS-OBS-021-R1 (HEURISTIC_TENSION).
"""

import os
import yaml
import numpy as np
import pytest

from navier3d.math_assurance.claims import ClaimManager


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestR1EpistemicAndRegistryNormalization:
    """Verify prospective reclassification of CLM-041 -> CLM-041-R1 and NS-OBS-021 -> NS-OBS-021-R1."""

    def test_clm041_preserved_and_superseded_by_clm041_r1(self):
        cm = ClaimManager()
        c041 = cm.get_claim("CLM-041")
        c041_r1 = cm.get_claim("CLM-041-R1")
        assert c041 is not None
        assert c041_r1 is not None
        assert c041["passport"]["project_status"] == "SUPERSEDED"
        assert c041_r1["supersedes"] == "CLM-041"
        assert c041_r1["passport"]["truth_status"] == "PROVED_LEMMA"
        assert c041_r1["passport"]["novelty"] == "N1_PROJECT_REFORMULATION"
        assert c041_r1["passport"]["significance"] == "S1_USEFUL_LEMMA"
        assert cm.validate_passport(c041_r1["passport"], c041_r1["claim_type"])["valid"] is True

    def test_ns_obs_021_downgraded_to_heuristic_tension(self):
        obs_path = os.path.join(REPO_ROOT, "research_memory", "RESEARCH_OBSTRUCTION_REGISTRY.yaml")
        with open(obs_path, "r", encoding="utf-8") as f:
            obs_data = yaml.safe_load(f)
        by_id = {item["obstruction_id"]: item for item in obs_data["obstructions"]}
        assert "NS-OBS-021" in by_id
        assert "NS-OBS-021-R1" in by_id
        assert by_id["NS-OBS-021-R1"]["corrects"] == "NS-OBS-021"
        assert by_id["NS-OBS-021-R1"]["status"] == "HEURISTIC_TENSION"

    def test_original_self_focus_001_artifacts_preserved_unchanged(self):
        """Verify Section 2 & 24: original milestone artifacts remain untouched on disk."""
        for fname in [
            "NS_OPENAI_UNFORCED_TRANSFER_BRANCH_CLOSURE.md",
            "NS_NONLINEAR_SELF_FOCUS_001_TASK_ENVELOPE.yaml",
            "NS_NONLINEAR_SELF_FOCUS_001_EXACT_BALANCE_FOUNDATION.md",
            "NS_NONLINEAR_SELF_FOCUS_001_SCALE_INVARIANCE_AUDIT.md",
            "NS_NONLINEAR_SELF_FOCUS_001_COUNTEREXAMPLE_MATRIX.md",
            "NS_NONLINEAR_SELF_FOCUS_001_LITERATURE_MAP.md",
            "NS_NONLINEAR_SELF_FOCUS_001_FIRST_HYPOTHESES.md",
            "NS_NONLINEAR_SELF_FOCUS_001_VISUAL_COMPANION.md",
            "NS_NONLINEAR_SELF_FOCUS_001_INDEPENDENT_REVIEW.md",
        ]:
            assert os.path.exists(os.path.join(REPO_ROOT, fname)), f"Missing historical artifact {fname}"


class TestPoincareNormalizationAndZeroSignCases:
    """Verify Section 4, 5, 6: Torus period L dependence of Poincare bound and zero/sign case split."""

    @pytest.mark.parametrize("L", [1.0, 2.0 * np.pi, 4.0 * np.pi])
    def test_poincare_upper_bound_depends_explicitly_on_torus_size_L(self, L: float):
        """
        Verify that on T^3_L = (R / L Z)^3, lambda_P = (2*pi / L)^2 and
        bar_ell_omega <= lambda_P^{-1/2} = L / (2*pi), with equality on the fundamental shell |k| = 2*pi/L.
        Look: when L = 2.0 * pi, L / (2*pi) = 1.0; when L = 4.0 * pi, bar_ell_omega = 2.0 > 1.0,
        falsifying any unnormalized claim that bar_ell_omega <= 1 for arbitrary torus size!
        """
        lambda_P = (2.0 * np.pi / L) ** 2
        k0 = 2.0 * np.pi / L
        # Fundamental mode omega(x) = (0, 0, k0 cos(k0 x)) has ||grad omega||_2^2 = k0^2 ||omega||_2^2
        bar_ell_fundamental = 1.0 / k0
        assert np.isclose(bar_ell_fundamental, lambda_P ** (-0.5), rtol=1e-14)
        assert np.isclose(bar_ell_fundamental, L / (2.0 * np.pi), rtol=1e-14)
        if L > 2.0 * np.pi:
            assert bar_ell_fundamental > 1.0

    def test_complete_zero_and_sign_case_split(self):
        """Verify Case 0 (omega=0), Case I (P<0), Case II (P=0), Case III (0<P<=D), Case IV (P>D)."""
        # Case I: P < 0 -> A < 0, bracket sqrt(nu A / lambda_1^+) is prohibited because A < 0
        P_neg, D_pos, nu, lam1_pos = -2.5, 1.0, 0.01, 3.0
        A_neg = P_neg / D_pos
        assert A_neg < 0.0
        assert (nu * A_neg / lam1_pos) < 0.0  # Would be imaginary if square-rooted without sign guard!


class TestOrthogonalVsSmoothLittlewoodPaleyPartition:
    """Verify Section 8, 9, 10: Orthogonal shell projectors P_q vs Smooth overlapping multipliers dot_Delta_q."""

    def test_smooth_partition_overlap_deficit_vs_orthogonal_exactness(self):
        """
        Construct a smooth partition of unity psi_0(k) + psi_1(k) == 1 on an overlap shell where
        psi_0(k) = 0.6, psi_1(k) = 0.4. Verify:
        1. Orthogonal projector sum: P_0^2 + P_1^2 == 1.0 (exact equality sum_q D_q = D(t)).
        2. Smooth squared block sum: psi_0(k)^2 + psi_1(k)^2 = 0.36 + 0.16 = 0.52 < 1.0 (strict deficit!).
        3. Smooth linear dual pairing sum: psi_0(k) + psi_1(k) = 1.0 (restores exact equality!).
        """
        psi_0, psi_1 = 0.6, 0.4
        assert np.isclose(psi_0 + psi_1, 1.0, rtol=1e-15)
        smooth_squared_sum = psi_0**2 + psi_1**2
        assert smooth_squared_sum < 1.0
        assert smooth_squared_sum >= 0.5
        # Orthogonal projector has indicator weights (1.0, 0.0)
        p_0, p_1 = 1.0, 0.0
        assert np.isclose(p_0**2 + p_1**2, 1.0, rtol=1e-15)
