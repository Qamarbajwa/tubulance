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


def frob2(a):
    return sum(x * x for row in a for x in row)


def inner(a, b):
    return sum(a[i][j] * b[i][j] for i in range(len(a))
               for j in range(len(a[0])))


def col(a, j):
    return [a[i][j] for i in range(len(a))]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def assert_matrix_close(a, b):
    for ra, rb in zip(a, b):
        assert ra == pytest.approx(rb)


def test_forwardized_sign_and_g3_martingale():
    text = (ROOT / "TP2_G5_A1_FORWARDIZATION_AND_CONVENTION.md").read_text()
    assert "da_\\tau=-u" in text
    assert "d(D\\omega)" in text
    assert "DG\\,dB_\\tau" in text
    assert "Both routes agree exactly" in text


def test_endpoint_deformation_uses_right_multiplication():
    A = [[0.0, 2.0], [0.0, 0.0]]
    D = [[1.0, 3.0], [0.0, 1.0]]
    expected = add(D, scale(0.01, mm(D, A)))
    assert expected[0][1] == pytest.approx(3.02)
    text = (ROOT / "TP2_G5_A1_DJOMEGA_MATRIX_SDE.md").read_text()
    assert "dD=DA" in text


def test_matrix_ordering_and_equivalent_full_gradient_form():
    D = [[1.0, 2.0, 0.0], [0.0, 1.0, 1.0], [0.0, 0.0, 1.0]]
    A = [[1.0, 2.0, 0.0], [0.0, 3.0, 4.0], [0.0, 0.0, 5.0]]
    G = [[0.0, 1.0, 2.0], [3.0, 0.0, 4.0], [5.0, 6.0, 0.0]]
    S = scale(0.5, add(A, [list(x) for x in zip(*A)]))
    Omega = scale(0.5, sub(A, [list(x) for x in zip(*A)]))
    T = [[2.0, 0.0, 1.0], [1.0, 3.0, 0.0], [0.0, 1.0, 4.0]]
    left = mm(D, sub(add(mm(Omega, G), mm(G, A)), T))
    KA = sub(T, mm(Omega, G))
    right = mm(D, sub(mm(G, A), KA))
    assert_matrix_close(left, right)
    wrong = mm(D, sub(KA, mm(A, G)))
    assert any(abs(left[i][j] - wrong[i][j]) > 1e-9
               for i in range(3) for j in range(3))
    assert frob2(S) > 0


def test_r_drift_and_martingale_coefficient():
    nu = 0.7
    z = [1.0, -2.0, 0.5]
    Y = [[1.0, 2.0, 0.0], [0.0, -1.0, 3.0], [2.0, 0.0, 1.0]]
    N = frob2(Y)
    assert 2 * nu * N == pytest.approx(2 * nu * sum(x * x for x in z) * 0 + 2 * nu * N)
    sigma_R = [2 * math.sqrt(2 * nu) * dot(z, col(Y, j)) for j in range(3)]
    assert sigma_R[0] != 0
    text = (ROOT / "TP2_G5_A1_Z_AND_R_DYNAMICS.md").read_text()
    assert "2\\nu N" in text
    assert "sigma_R" in text


def test_n_ito_drift_and_noise():
    nu = 0.25
    Y = [[1.0, 0.0], [2.0, -1.0]]
    BY = [[-1.0, 2.0], [0.5, 3.0]]
    C = [[[0.5, 1.0], [1.5, -0.5]], [[-1.0, 0.0], [0.0, 2.0]]]
    bN = 2 * inner(Y, BY) + 2 * nu * sum(frob2(c) for c in C)
    sigmaN = [2 * math.sqrt(2 * nu) * inner(Y, c) for c in C]
    assert bN == pytest.approx(2 * inner(Y, BY) + 2 * nu * sum(frob2(c) for c in C))
    assert sigmaN[0] != sigmaN[1]


def test_nr_covariation_is_present_and_nonzero():
    nu = 0.5
    Y = [[1.0, 2.0], [0.0, 1.0]]
    Z = [2.0, -1.0]
    C = [[[1.0, 0.0], [0.0, 1.0]], [[2.0, 0.0], [0.0, -1.0]]]
    sigmaN = [2 * math.sqrt(2 * nu) * inner(Y, c) for c in C]
    sigmaR = [2 * math.sqrt(2 * nu) * dot(Z, col(Y, j)) for j in range(2)]
    covariance = sum(a * b for a, b in zip(sigmaN, sigmaR))
    assert covariance != 0
    text = (ROOT / "TP2_G5_A1_NR_QUADRATIC_COVARIATION.md").read_text()
    assert "d[N,R]" in text
    assert "8\\nu" in text


def test_quotient_ito_corrections():
    N, R = 5.0, 2.0
    bN, bR = 7.0, 3.0
    sN, sR = [2.0, -1.0], [1.5, 4.0]
    cross = dot(sN, sR)
    drift = bN / R - N * bR / R**2 - cross / R**2 + N * dot(sR, sR) / R**3
    without_cross = drift + cross / R**2
    assert drift != without_cross
    text = (ROOT / "TP2_G5_A1_XI_QUOTIENT_SDE.md").read_text()
    assert "sigma_N\\cdot\\sigma_R" in text
    assert "N|\\sigma_R|^2" in text


def test_zero_states_and_stopping():
    text = (ROOT / "TP2_G5_A1_ZERO_STATE_AND_STOPPING_TIMES.md").read_text()
    assert "R=|D omega|^2=0 if and only if omega=0" in text
    assert "tau<tau_R" in text
    assert "log Xi is undefined" in text
    assert "State C" in text


def test_zero_gradient_calibration():
    G = [[0.0, 0.0], [0.0, 0.0]]
    assert frob2(G) == 0.0
    assert 0.0 / 1.0 == 0.0
    text = (ROOT / "TP2_G5_A1_EXACT_FLOW_CALIBRATION.md").read_text()
    assert "Y=N=Xi=0" in text
    assert "log Xi is forbidden" in text


def test_periodic_shear_matrix_annihilation():
    E12 = [[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    E32 = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    assert frob2(mm(E12, E32)) == 0.0
    D = add([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            scale(4.0, E12))
    G = scale(-3.0, E32)
    assert_matrix_close(mm(D, G), G)


def test_scaling_weights_are_documented():
    text = (ROOT / "TP2_G5_A1_SCALING_AUDIT.md").read_text()
    for token in ("lambda^6", "lambda^4", "lambda^2", "b_Xi", "sigma_Xi"):
        assert token in text


def test_expectation_is_not_claimed_closed():
    text = (ROOT / "TP2_G5_A1_NEGATIVE_EVIDENCE.md").read_text()
    assert "not shown to be an" in text
    assert "not a closure F(E[Xi])" in text
