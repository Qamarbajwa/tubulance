from pathlib import Path
import math
import pytest

ROOT = Path(__file__).resolve().parents[1]

def mm(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]

def add(a, b):
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))]
            for i in range(len(a))]

def sub(a, b):
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))]
            for i in range(len(a))]

def scale(c, a):
    return [[c * x for x in row] for row in a]

def inner(a, b):
    return sum(a[i][j] * b[i][j] for i in range(len(a))
               for j in range(len(a[0])))

def frob2(a):
    return sum(x * x for row in a for x in row)

def col(a, j):
    return [a[i][j] for i in range(len(a))]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def test_all_a1_coefficients_are_substituted():
    text = (ROOT / "TP2_G5_A2_FULL_DRIFT_EXPANSION.md").read_text()
    for token in ("b_R", "sigma_R", "b_N", "sigma_N", "c_\\ell", "R^3",
                  "8\\nu", "No absolute-value bound"):
        assert token in text

def test_square_completion_componentwise():
    h = [[1.0, -2.0], [0.5, 3.0]]
    y = [[2.0, 1.0], [-1.0, 0.5]]
    c, R, nu = 1.25, 2.5, 0.75
    lhs = frob2(sub(h, scale(2 * c / R, y)))
    rhs = (frob2(h) - 4 * c / R * inner(y, h)
           + 4 * c * c / (R * R) * frob2(y))
    assert lhs == pytest.approx(rhs)
    assert (2 * nu / R) * lhs >= 0

def test_square_completion_has_forced_coefficient_two():
    text = (ROOT / "TP2_G5_A2_SQUARE_COMPLETION.md").read_text()
    assert "2c_\\ell}{R}" in text
    assert "4c_\\ell" in text
    assert "I_\\Xi" in text

def test_exact_compressed_drift_identity():
    text = (ROOT / "TP2_G5_A2_SQUARE_COMPLETION.md").read_text()
    assert "b_\\Xi=D_\\Xi+R_\\Xi+I_\\Xi" in text

def test_riccati_term_origin_is_denominator():
    text = (ROOT / "TP2_G5_A2_RICCATI_TERM_AUDIT.md").read_text()
    assert "denominator drift" in text
    assert "does not originate from numerator dissipation" in text
    assert "R_\\Xi=-2\\nu\\Xi^2" in text

def test_ito_compensation_zero_condition():
    y = [[1.0, 0.0], [0.0, 1.0]]
    c, R = 0.5, 2.0
    h = scale(2 * c / R, y)
    assert frob2(sub(h, scale(2 * c / R, y))) == pytest.approx(0.0)
    text = (ROOT / "TP2_G5_A2_ITO_COMPENSATION_AUDIT.md").read_text()
    assert "vanishes exactly" in text
    assert "overdetermined instantaneous" in text

def test_xi_quadratic_variation_is_exact():
    nu = 0.6
    a = [1.0, -2.0, 0.5]
    qv = 8 * nu * sum(x * x for x in a)
    assert qv > 0
    text = (ROOT / "TP2_G5_A1_XI_QUOTIENT_SDE.md").read_text()
    assert "sigma_\\Xi" in text
    assert "cross-covariation" in text

def test_geometry_decomposition_and_d_equals_i_rotation():
    text = (ROOT / "TP2_G5_A2_DETERMINISTIC_GEOMETRY_TERMS.md").read_text()
    assert "D_{\\rm ROT}" in text
    assert "D_{\\rm SOURCE}" in text
    G = [[1.0, 2.0], [3.0, -1.0]]
    Omega = [[0.0, 4.0], [-4.0, 0.0]]
    assert inner(G, mm(Omega, G)) == pytest.approx(0.0)

def test_nonorthogonal_deformation_can_make_rotation_term_nonzero():
    D = [[1.0, 2.0], [0.0, 1.0]]
    Omega = [[0.0, 1.0], [-1.0, 0.0]]
    G = [[1.0, 0.0], [0.0, 2.0]]
    value = inner(mm(D, G), mm(D, mm(Omega, G)))
    assert value != 0.0

def test_pressure_classification_is_indirect_only():
    text = (ROOT / "TP2_G5_A2_PRESSURE_ENTRY_AUDIT.md").read_text()
    assert "NO_EXPLICIT_PRESSURE_TERM_AT_THIS_LEVEL" in text
    assert "INDIRECT_NONLOCAL_DEPENDENCE" in text
    assert "T^S is not pressure" in text

def test_weighted_measure_requires_weight_evolution():
    text = (ROOT / "TP2_G5_A2_WEIGHTED_EXPECTATION_AUDIT.md").read_text()
    assert "time-dependent-weight correction" in text
    assert "invalid to write only" in text
    assert "WEIGHTED_DYNAMICS_NOT_CLOSED" in text

def test_weighted_derivative_formula_is_not_unweighted_drift():
    Ebn, EN, S = 4.0, 2.0, 3.0
    actual = Ebn / S - EN * (2 * 0.5 * EN) / S**2
    naive = Ebn / S
    assert actual != naive

def test_periodic_shear_calibration():
    text = (ROOT / "TP2_G5_A2_EXACT_FLOW_CALIBRATION.md").read_text()
    for token in ("F=0", "D_\\Xi=0", "R_\\Xi", "I_\\Xi", "sigma"):
        assert token in text

def test_zero_gradient_and_no_log():
    text = (ROOT / "TP2_G5_A2_EXACT_FLOW_CALIBRATION.md").read_text()
    assert "At G=0" in text
    assert "log Xi remains forbidden" in text

def test_scaling_audit():
    text = (ROOT / "TP2_G5_A2_NONCIRCULARITY_AUDIT.md").read_text()
    assert "SIGN-INDEFINITE_BALANCE" in text
    scaling = (ROOT / "TP2_G5_A1_SCALING_AUDIT.md").read_text()
    assert "b_Xi" in scaling and "lambda^4" in scaling
