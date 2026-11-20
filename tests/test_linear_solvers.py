"""Tests for navier3d.linear_solvers: LinearSolver, create_linear_solver."""
import numpy as np
import pytest
import scipy.sparse as sp

from navier3d.linear_solvers import (
    HAS_PYAMG,
    LinearSolver,
    LinearSolverError,
    create_linear_solver,
)


def _spd_matrix(n: int = 20, seed: int = 0) -> sp.csr_matrix:
    rng = np.random.default_rng(seed)
    B = rng.uniform(-1.0, 1.0, size=(n, n))
    A = B @ B.T + n * np.eye(n)  # guaranteed SPD
    return sp.csr_matrix(A)


def _nonsymmetric_matrix(n: int = 20, seed: int = 1) -> sp.csr_matrix:
    rng = np.random.default_rng(seed)
    A = rng.uniform(-1.0, 1.0, size=(n, n)) + n * np.eye(n)  # diagonally dominant, not symmetric
    return sp.csr_matrix(A)


# --------------------------------------------------------------------------
# Basic direct/CG/BiCGSTAB/GMRES correctness
# --------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["direct", "cg", "bicgstab", "gmres"])
def test_spd_matrix_all_methods_agree(method: str) -> None:
    A = _spd_matrix()
    x_exact = np.arange(A.shape[0], dtype=np.float64)
    b = A @ x_exact
    solver = create_linear_solver(A, method=method, matrix_kind="spd", rtol=1e-12)
    result = solver.solve(b)
    assert result.converged
    np.testing.assert_allclose(result.x, x_exact, atol=1e-6)
    assert result.relative_residual < 1e-8


@pytest.mark.parametrize("method", ["direct", "bicgstab", "gmres"])
def test_general_matrix_nondirect_methods(method: str) -> None:
    A = _nonsymmetric_matrix()
    x_exact = np.arange(A.shape[0], dtype=np.float64)
    b = A @ x_exact
    solver = create_linear_solver(A, method=method, matrix_kind="general", rtol=1e-12)
    result = solver.solve(b)
    assert result.converged
    np.testing.assert_allclose(result.x, x_exact, atol=1e-6)


# --------------------------------------------------------------------------
# Matrix-property-driven selection: CG on GENERAL must be rejected
# --------------------------------------------------------------------------

def test_cg_rejected_for_general_matrix_kind() -> None:
    A = _nonsymmetric_matrix()
    with pytest.raises(LinearSolverError, match="not valid"):
        create_linear_solver(A, method="cg", matrix_kind="general")


def test_cg_allowed_for_spd_matrix_kind() -> None:
    A = _spd_matrix()
    solver = create_linear_solver(A, method="cg", matrix_kind="spd")
    assert solver.method.value == "cg"


# --------------------------------------------------------------------------
# Diagnostics structure
# --------------------------------------------------------------------------

def test_result_diagnostics_fields() -> None:
    A = _spd_matrix()
    x_exact = np.ones(A.shape[0])
    b = A @ x_exact
    solver = create_linear_solver(A, method="cg", matrix_kind="spd", rtol=1e-10)
    result = solver.solve(b)
    assert result.iterations > 0
    assert result.initial_residual >= result.final_residual
    assert result.setup_time >= 0.0
    assert result.preconditioner_time >= 0.0
    assert result.solve_time >= 0.0
    assert result.method == "cg"
    assert result.preconditioner is None


def test_shape_property_matches_matrix_shape() -> None:
    A = _spd_matrix(n=15)
    solver = create_linear_solver(A, method="direct", matrix_kind="spd")
    assert solver.shape == A.shape


def test_direct_method_reports_one_iteration_and_converged() -> None:
    A = _spd_matrix()
    b = A @ np.ones(A.shape[0])
    solver = create_linear_solver(A, method="direct", matrix_kind="spd")
    result = solver.solve(b)
    assert result.converged
    assert result.iterations == 1
    assert result.method == "direct"


# --------------------------------------------------------------------------
# Jacobi preconditioning
# --------------------------------------------------------------------------

def test_jacobi_preconditioner_reduces_iterations() -> None:
    n = 60
    rng = np.random.default_rng(2)
    diag_scale = rng.uniform(1.0, 1000.0, size=n)  # ill-conditioned diagonal
    B = rng.uniform(-0.1, 0.1, size=(n, n))
    A_dense = np.diag(diag_scale) + (B + B.T)
    A_dense += n * np.eye(n) * np.max(diag_scale)  # keep SPD
    A = sp.csr_matrix(A_dense)
    x_exact = np.ones(n)
    b = A @ x_exact

    plain = create_linear_solver(A, method="cg", matrix_kind="spd", rtol=1e-10).solve(b)
    jacobi = create_linear_solver(A, method="cg", matrix_kind="spd", preconditioner="jacobi", rtol=1e-10).solve(b)
    assert plain.converged and jacobi.converged
    np.testing.assert_allclose(plain.x, x_exact, atol=1e-6)
    np.testing.assert_allclose(jacobi.x, x_exact, atol=1e-6)
    assert jacobi.iterations <= plain.iterations


def test_preconditioner_rejected_for_direct() -> None:
    A = _spd_matrix()
    with pytest.raises(LinearSolverError, match="not applicable"):
        create_linear_solver(A, method="direct", matrix_kind="spd", preconditioner="jacobi")


def test_unknown_preconditioner_rejected() -> None:
    A = _spd_matrix()
    with pytest.raises(LinearSolverError, match="unknown preconditioner"):
        create_linear_solver(A, method="cg", matrix_kind="spd", preconditioner="not_a_preconditioner")


# --------------------------------------------------------------------------
# Warm starts
# --------------------------------------------------------------------------

def test_warm_start_reduces_iterations_for_nearby_rhs() -> None:
    A = _spd_matrix(n=80)
    x1 = np.ones(A.shape[0])
    b1 = A @ x1
    solver = create_linear_solver(A, method="cg", matrix_kind="spd", rtol=1e-10)
    cold = solver.solve(b1)

    x2 = x1 + 1e-4 * np.sin(np.arange(A.shape[0]))  # a nearby solution
    b2 = A @ x2
    warm = solver.solve(b2, x0=cold.x)
    cold2 = solver.solve(b2)  # zero initial guess, for comparison
    assert warm.converged and cold2.converged
    assert warm.iterations <= cold2.iterations


# --------------------------------------------------------------------------
# PyAMG (optional; skipped if not installed)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_PYAMG, reason="pyamg not installed")
def test_amg_preconditioner_matches_reference() -> None:
    A = _spd_matrix(n=100)
    x_exact = np.arange(A.shape[0], dtype=np.float64) / A.shape[0]
    b = A @ x_exact
    result = create_linear_solver(A, method="cg", matrix_kind="spd", preconditioner="amg", rtol=1e-10).solve(b)
    assert result.converged
    np.testing.assert_allclose(result.x, x_exact, atol=1e-6)
    assert result.preconditioner == "amg"


def test_amg_without_pyamg_raises_clear_error(monkeypatch) -> None:
    import navier3d.linear_solvers as ls
    monkeypatch.setattr(ls, "HAS_PYAMG", False)
    A = _spd_matrix()
    with pytest.raises(LinearSolverError, match="pyamg"):
        create_linear_solver(A, method="cg", matrix_kind="spd", preconditioner="amg")


# --------------------------------------------------------------------------
# Non-convergence and validation
# --------------------------------------------------------------------------

def test_non_convergence_reported_not_raised_by_solver() -> None:
    """LinearSolver itself reports non-convergence via .converged=False --
    it is the CALLER's (pressure.py/diffusion.py) responsibility to raise
    on that, consistent with the rest of this project's "never silently
    continue" convention applied one layer up."""
    A = _spd_matrix(n=50)
    b = A @ np.ones(A.shape[0])
    solver = create_linear_solver(A, method="cg", matrix_kind="spd", rtol=1e-14, max_iterations=1)
    result = solver.solve(b)
    assert not result.converged


def test_rejects_non_square_matrix() -> None:
    A = sp.csr_matrix(np.ones((3, 4)))
    with pytest.raises(LinearSolverError, match="square"):
        create_linear_solver(A, method="direct", matrix_kind="general")


def test_jacobi_rejects_zero_diagonal() -> None:
    A = sp.csr_matrix(np.array([[0.0, 1.0], [1.0, 0.0]]))
    with pytest.raises(LinearSolverError, match="nonzero diagonal"):
        create_linear_solver(A, method="cg", matrix_kind="spd", preconditioner="jacobi")
