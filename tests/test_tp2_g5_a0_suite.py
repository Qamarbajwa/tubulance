"""Worker checks for TP2-G5-A0 domain, scaling, and research-contract guards."""
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = (ROOT / "TP2_G5_A0_XI_IDENTITY_AND_DOMAIN.md").read_text(encoding="utf-8")
CONTRACT = (ROOT / "TP2_G5_A0_RESEARCH_CONTRACT.md").read_text(encoding="utf-8")
NOVELTY = (ROOT / "TP2_G5_A0_NOVELTY_AUDIT.md").read_text(encoding="utf-8")
FLOW = (ROOT / "TP2_G5_A0_EXACT_FLOW_TEST_BENCH.md").read_text(encoding="utf-8")


def test_t1_xi_state_taxonomy_is_frozen():
    for state in ("X1", "X2", "X3", "X4"):
        assert state in IDENTITY
    assert "factorization is valid" in IDENTITY


def test_t2_r_zero_iff_omega_zero_for_invertible_d():
    D = np.diag([2.0, 1.0, 0.5])
    for w in (np.zeros(3), np.array([1.0, -2.0, 3.0])):
        assert np.isclose(np.linalg.norm(D @ w), 0.0) == np.isclose(np.linalg.norm(w), 0.0)
    assert "|D_s\\omega|=0\\iff \\omega=0" in IDENTITY


def test_t3_xi_zero_on_nonzero_omega_zero_gradient():
    D = np.diag([2.0, 1.0, 0.5])
    omega = np.array([1.0, 0.0, 0.0])
    J = np.zeros((3, 3))
    assert np.sum((D @ J) ** 2) / np.sum((D @ omega) ** 2) == 0.0
    assert "exactly `0`" in IDENTITY


def test_t4_reject_xi_at_zero_vorticity_without_extension():
    assert "algebraically `0/0`, undefined" in IDENTITY
    assert "no silent extension" in IDENTITY


def test_t5_zero_vorticity_histories_have_zero_mu_weight():
    assert "zero `mu_s` weight" in IDENTITY
    assert "mu_s" in IDENTITY


def test_t6_xi_scaling_is_lambda_squared():
    assert "Xi -> lambda^2 Xi" in IDENTITY
    assert "Q/S -> lambda^2" in IDENTITY


def test_t7_factorization_is_restricted_to_valid_domain():
    assert "On X1 only" in IDENTITY
    assert "not asserted on X2 or X3" in IDENTITY


def test_t8_stochastic_cauchy_novelty_is_rejected():
    report = (ROOT / "TP2_G5_A0_STOCHASTIC_CAUCHY_LITERATURE.md").read_text(encoding="utf-8")
    assert "known" in report.lower()
    assert "does not supply the" in report and "G5 relative density" in report


def test_t9_direction_theorem_to_xi_transfer_is_rejected():
    geo = (ROOT / "TP2_G5_A0_GEOMETRIC_REGULARITY_LITERATURE.md").read_text(encoding="utf-8")
    assert "can be translated into an Xi theorem" in geo


def test_t10_inverse_length_scale_is_not_xi_without_bridge():
    audit = (ROOT / "TP2_G5_A0_INVERSE_LENGTH_SCALE_AUDIT.md").read_text(encoding="utf-8")
    assert "not simply an Eulerian inverse length" in audit
    assert "would require a theorem" in audit


def test_t11_exact_flow_benchmarks_are_taxonomized():
    for family in ("Periodic shear", "Beltrami", "ABC-type", "Burgers-tube"):
        assert family in FLOW


def test_t12_d_realizability_does_not_imply_joint_jet_realizability():
    report = (ROOT / "TP2_G5_A0_JOINT_JET_REALIZATION_AUDIT.md").read_text(encoding="utf-8")
    assert "D-only theorem" in report
    assert "does not state a theorem jointly prescribing arbitrary" in report
    assert "JOINT_JET_REALIZATION_PROBLEM" in report


def test_t13_n2_cannot_become_n3():
    assert "no N3/N4 assigned" in NOVELTY
    assert "N2_NOT_FOUND_IN_AUDITED_SOURCES" in NOVELTY


def test_t14_preprint_status_cannot_become_accepted_automatically():
    geo = (ROOT / "TP2_G5_A0_GEOMETRIC_REGULARITY_LITERATURE.md").read_text(encoding="utf-8")
    assert "PREPRINT_RESULT" in geo
    assert "No peer-reviewed status was independently confirmed" in geo


def test_t15_contract_blocks_premature_a1_or_collision_drift():
    assert "A1 is not executed in A0" in CONTRACT
    assert "Hard exclusions" in CONTRACT
    assert "XI_CONFIRMED_AS_PRIMARY_G5_OBJECT" in CONTRACT
