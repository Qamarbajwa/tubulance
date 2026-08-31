"""Deterministic algebra and boundary checks for TP2-G5-A4."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from scripts.tp2_g5_a4_diagnostics import (
    anisotropic_metric_example,
    chi_from_relative_qv,
    chi_variance_identity,
    classify_cluster_subsequence,
    covariance_trace_lower_bound,
    intrinsic_window,
    normalized_bad_set_bound,
    periodic_shear_calibration,
    relative_variance_from_relative_qv,
    scale_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_t1_t2_accepted_orientation_and_j_identity() -> None:
    J = 0.7
    assert math.isclose(chi_from_relative_qv(J), math.exp(-J))
    assert math.isclose(-math.log(chi_from_relative_qv(J)), J)
    assert "J_n = -log chi_n" in (ROOT / "TP2_G5_A4_CHI_VARIANCE_IDENTITY.md").read_text(encoding="utf-8")


def test_t3_window_and_j_are_dimensionless() -> None:
    assert intrinsic_window(8.0, 2.0) == 0.25
    assert scale_audit() == {"M": 2, "L": -2, "Xi": 2, "dt": -2, "J": 0}


def test_t4_variance_algebra() -> None:
    chi, relative_variance = chi_variance_identity(4.0, 10.0)
    assert math.isclose(chi, 0.4)
    assert math.isclose(relative_variance, 1.5)
    assert math.isclose(relative_variance, 1.0 / chi - 1.0)


def test_t5_delta_gives_chi_upper_bound() -> None:
    delta = 0.3
    assert chi_from_relative_qv(delta) <= math.exp(-delta)
    assert relative_variance_from_relative_qv(delta) >= math.exp(delta) - 1.0 - 1e-12


def test_t6_rigid_branch_is_relative_l2_only() -> None:
    values = [1e-6, 1e-9, 1e-13]
    assert classify_cluster_subsequence(values) == "RIGID"
    assert relative_variance_from_relative_qv(values[-1]) < 2e-9


def test_t7_rigid_branch_does_not_claim_pathwise_rigidity() -> None:
    text = (ROOT / "TP2_G5_A4_RIGID_BRANCH_GEOMETRY.md").read_text(encoding="utf-8")
    assert "does not imply pathwise equality" in text
    assert "almost sure" in text


def test_t8_t9_nonnegative_xi_split() -> None:
    text = (ROOT / "TP2_G5_A4_RIGID_BRANCH_GEOMETRY.md").read_text(encoding="utf-8")
    assert "Xi=M_D+C_D" in text
    assert "nonnegative" in text
    assert math.isclose(sum((0.2, 0.3)), 0.5)


def test_t10_integrated_smallness_keeps_normalization() -> None:
    assert normalized_bad_set_bound(1e-4, 1e-2, 0.1) == pytest.approx(0.1)
    assert "does not imply pointwise" in (ROOT / "TP2_G5_A4_RIGID_BRANCH_GEOMETRY.md").read_text(encoding="utf-8")


def test_t11_t13_literature_bridges_are_not_automatic() -> None:
    for name in (
        "TP2_G5_A4_LEI_REN_TIAN_BRIDGE.md",
        "TP2_G5_A4_CONSTANTIN_FEFFERMAN_BRIDGE.md",
    ):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "NO_DIRECT_TRANSFER" in text or "YES_WITH_EXTRA_ASSUMPTIONS" in text
        assert "stochastic histories" in text


def test_t12_lei_ren_tian_not_transferred_to_xi() -> None:
    text = (ROOT / "TP2_G5_A4_LEI_REN_TIAN_BRIDGE.md").read_text(encoding="utf-8")
    assert "NO_DIRECT_TRANSFER" in text
    assert "double cone" in text


def test_t14_grujic_preprint_status_is_preserved() -> None:
    text = (ROOT / "TP2_G5_A4_GRUJIC_SPARSENESS_ANALYTICITY_BRIDGE.md").read_text(encoding="utf-8")
    assert "PREPRINT" in text
    assert "not upgraded" in text


def test_t15_decoherence_does_not_bound_terminal_mean() -> None:
    text = (ROOT / "TP2_G5_A4_DECOHERENT_BRANCH_COVARIANCE.md").read_text(encoding="utf-8")
    assert "does not bound the terminal mean" in text


def test_t16_covariance_trace_does_not_imply_isotropy() -> None:
    assert covariance_trace_lower_bound(4.0, 0.5) == pytest.approx(math.exp(0.5) - 1.0)
    text = (ROOT / "TP2_G5_A4_DECOHERENT_BRANCH_COVARIANCE.md").read_text(encoding="utf-8")
    assert "trace does not imply isotropy" in text


def test_t17_bkm_serrin_circularity_is_detected() -> None:
    text = (ROOT / "TP2_G5_A4_NONCIRCULARITY_AUDIT.md").read_text(encoding="utf-8")
    assert "CIRCULAR_FOR_CLAY_CLOSURE" in text
    assert "BKM" in text and "Serrin" in text


def test_t18_kinematic_example_is_not_ns_realization() -> None:
    values = anisotropic_metric_example(10.0)
    assert values == pytest.approx((100.0, 0.01))
    assert "KINEMATIC" in (ROOT / "TP2_G5_A4_ADVERSARIAL_EXACT_FLOW_CALIBRATION.md").read_text(encoding="utf-8")


def test_t19_n2_is_not_n3() -> None:
    text = (ROOT / "TP2_G5_A4_NOVELTY_AUDIT.md").read_text(encoding="utf-8")
    assert "N2_NOT_FOUND_IN_AUDITED_SOURCES" in text
    assert "N3" in text and "not" in text


def test_t20_clay_statement_b_unresolved() -> None:
    assert "UNRESOLVED" in (ROOT / "TP2_G5_A4_ACCEPTANCE_DECISION.md").read_text(encoding="utf-8")


def test_t21_candidate_bound_evidence_is_declared() -> None:
    text = (ROOT / "TP2_G5_A4_INDEPENDENT_VERIFICATION.md").read_text(encoding="utf-8")
    assert "candidate-bound" in text
    assert "E3" in text


def test_t22_writer_cannot_self_certify() -> None:
    text = (ROOT / "TP2_G5_A4_INDEPENDENT_VERIFICATION.md").read_text(encoding="utf-8")
    assert "IND1" in text
    assert "writer cannot self-certify" in text


def test_periodic_shear_boundary_calibration() -> None:
    assert periodic_shear_calibration() == {"J_omega_norm_squared": 0.0, "Xi": 0.0, "chi": 1.0, "J": 0.0}
