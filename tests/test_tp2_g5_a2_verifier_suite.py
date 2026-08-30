from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return (ROOT / name).read_text()

def test_a1_is_treated_as_immutable_input():
    text = read("TP2_G5_A2_FULL_DRIFT_EXPANSION.md")
    assert "accepted A1 variables" in text
    assert "No absolute-value bound or covariance deletion" in text

def test_mutation_wrong_square_coefficients_are_rejected():
    text = read("TP2_G5_A2_SQUARE_COMPLETION.md")
    assert "coefficient 2" in text
    assert "all R" in text
    assert "Frobenius norm" in text
    assert "column" in text

def test_mutation_wrong_quotient_terms_are_rejected():
    text = read("TP2_G5_A2_FULL_DRIFT_EXPANSION.md")
    assert "R^3" in text and "8\\nu" in text
    xi = read("TP2_G5_A1_XI_QUOTIENT_SDE.md")
    assert "denominator Ito correction" in xi or "denominator" in xi

def test_antisymmetric_omega_is_not_dropped():
    text = read("TP2_G5_A2_DETERMINISTIC_GEOMETRY_TERMS.md")
    assert "does not generally vanish" in text
    assert "need not commute" in text

def test_geometry_sign_is_not_promoted():
    text = read("TP2_G5_A2_DETERMINISTIC_GEOMETRY_TERMS.md")
    assert "sign-indefinite" in text
    assert "universally favorable" in text

def test_pressure_is_not_inserted_into_f():
    text = read("TP2_G5_A2_PRESSURE_ENTRY_AUDIT.md")
    assert "not pressure" in text
    assert "direct pressure-Hessian term" in text

def test_riccati_and_compensation_are_distinguished():
    ric = read("TP2_G5_A2_RICCATI_TERM_AUDIT.md")
    comp = read("TP2_G5_A2_ITO_COMPENSATION_AUDIT.md")
    assert "denominator drift" in ric
    assert "nonnegative" in comp

def test_weighted_mu_derivative_has_cross_term():
    text = read("TP2_G5_A2_WEIGHTED_EXPECTATION_AUDIT.md")
    assert "sigma_R\\cdot\\sigma_\\Xi" in text
    assert "S'" in text
    assert "not closed" in text

def test_no_bkm_or_target_promotion():
    text = read("TP2_G5_A2_NONCIRCULARITY_AUDIT.md")
    neg = read("TP2_G5_A2_NEGATIVE_EVIDENCE.md")
    assert "DIRECT_EVOLUTION_ROUTE_CIRCULAR" in text
    assert "POTENTIALLY_NONCIRCULAR" in text
    assert "BKM closure" in neg
    assert "A2 stops before G5-A3" in neg

def test_acceptance_forbids_global_claims_and_a3():
    text = read("TP2_G5_A2_ACCEPTANCE_DECISION.md")
    assert "ACCEPTED_WITH_LIMITATIONS" in text
    assert "A3 is not executed" in text
    assert "GLOBAL_REGULARITY" in text
    assert "UNRESOLVED" in text

def test_exact_flow_and_d_i_are_present():
    text = read("TP2_G5_A2_EXACT_FLOW_CALIBRATION.md")
    assert "Periodic shear" in text
    assert "Beltrami" in text
    assert "At D=I" in text
    assert "Kinematic SL(3)" in text

def test_reviewer_records_no_new_incident():
    text = read("TP2_G5_A2_INDEPENDENT_VERIFICATION.md")
    assert "No new proof incident was opened" in text
    assert "FINAL_E4_PASS_WITH_LIMITATIONS" in text

def test_understanding_gate_load_bearing_terms():
    text = read("TP2_G5_A2_UNDERSTANDING_GATE.md")
    assert "sign-indefinite" in text
    assert "negative denominator-Riccati" in text
    assert "nonnegative correlated-noise square" in text
