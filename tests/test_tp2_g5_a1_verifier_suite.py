from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return (ROOT / name).read_text()


def test_acceptance_is_limited_and_stops_before_a2():
    text = read("TP2_G5_A1_ACCEPTANCE_DECISION.md")
    assert "ACCEPTED_WITH_LIMITATIONS" in text
    assert "A2 is not executed" in text
    assert "GLOBAL" in text and "REGULARITY result is asserted" in text


def test_matrix_sde_rejects_ag_swap():
    text = read("TP2_G5_A1_DJOMEGA_MATRIX_SDE.md")
    assert "exact order is GA, not AG" in text
    assert "D(GA-K^A)" in text


def test_covariance_and_quotient_mutations_are_named():
    cov = read("TP2_G5_A1_NR_QUADRATIC_COVARIATION.md")
    xi = read("TP2_G5_A1_XI_QUOTIENT_SDE.md")
    assert "invalid" in cov
    assert "denominator Ito correction" in xi
    assert "cross-covariation" in xi


def test_forbidden_log_and_denominator_extensions_are_rejected():
    text = read("TP2_G5_A1_ZERO_STATE_AND_STOPPING_TIMES.md")
    assert "quotient SDE is valid only" in text
    assert "No logarithmic extension" in text


def test_g3_orientation_regression_is_explicit():
    text = read("TP2_G5_A1_Z_AND_R_DYNAMICS.md")
    assert "dR_\\tau=2\\nu N_\\tau d\\tau" in text
    assert "partial_s" in text


def test_two_route_convention_audit_is_explicit():
    text = read("TP2_G5_A1_FORWARDIZATION_AND_CONVENTION.md")
    assert "Route A" in text and "Route B" in text
    assert "same sign" in text


def test_scaling_and_fixed_torus_qualification():
    text = read("TP2_G5_A1_SCALING_AUDIT.md")
    assert "[Xi]=lambda^2" in text
    assert "fixed torus" in text


def test_no_a2_sign_classification():
    text = read("TP2_G5_A1_N_DYNAMICS.md")
    assert "A1 makes no favorable or unfavorable sign" in text
    assert "belongs to A2" in text


def test_independent_review_scope_and_limitations():
    text = read("TP2_G5_A1_INDEPENDENT_VERIFICATION.md")
    assert "Independence is low" in text
    assert "FINAL_E4_PASS_WITH_LIMITATIONS" in text
    assert "No A2" in text


def test_exact_flow_benchmarks_cover_required_families():
    text = read("TP2_G5_A1_EXACT_FLOW_CALIBRATION.md")
    for family in ("Periodic shear", "Beltrami", "ABC", "Strained sheet",
                   "Burgers tube", "zero-gradient"):
        assert family.lower() in text.lower()
