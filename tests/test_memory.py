"""Tests for navier3d.memory: field/matrix/solver memory accounting."""
import numpy as np
import pytest
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from navier3d.memory import (
    HAS_PSUTIL,
    MemoryReport,
    estimate_field_memory,
    estimate_matrix_memory,
    estimate_solver_matrix_memory,
    measure_direct_factorization_memory,
    measure_matrix_memory,
    measure_process_rss_delta,
)
from navier3d.mesh import StructuredMesh3D


def mesh(n: int = 16) -> StructuredMesh3D:
    return StructuredMesh3D(nx=n, ny=n, nz=n, lx=1.0, ly=1.0, lz=1.0, n_ghost=1)


# --------------------------------------------------------------------------
# Field memory
# --------------------------------------------------------------------------

def test_field_memory_matches_actual_array_sizes() -> None:
    from navier3d.fields import FlowState
    m = mesh(10)
    state = FlowState.zeros(m)
    report = estimate_field_memory(m, n_temporary_velocity_fields=0)
    actual_p = state.pressure.data.nbytes
    actual_v = sum(c.data.nbytes for c in state.velocity.components())
    assert report.categories["pressure_field_p"] == actual_p
    assert report.categories["velocity_fields_uvw"] == actual_v


def test_field_memory_scales_with_resolution() -> None:
    small = estimate_field_memory(mesh(8))
    large = estimate_field_memory(mesh(16))
    assert large.total_bytes > small.total_bytes
    # ~8x cells at 2x resolution in 3D -> roughly 8x memory (allow slack for ghosts)
    ratio = large.total_bytes / small.total_bytes
    assert 5.0 < ratio < 10.0


def test_temporary_fields_multiply_velocity_bytes() -> None:
    m = mesh(10)
    base = estimate_field_memory(m, n_temporary_velocity_fields=0)
    with_temps = estimate_field_memory(m, n_temporary_velocity_fields=5)
    assert with_temps.categories["temporary_velocity_fields"] == 5 * base.categories["velocity_fields_uvw"]


# --------------------------------------------------------------------------
# Matrix memory: measured vs analytical
# --------------------------------------------------------------------------

def test_measured_matrix_memory_matches_scipy_arrays() -> None:
    A = sp.random(200, 200, density=0.05, format="csr")
    measured = measure_matrix_memory(A)
    expected = A.data.nbytes + A.indices.nbytes + A.indptr.nbytes
    assert measured == expected


def test_analytical_matrix_estimate_scales_with_stencil_and_rows() -> None:
    est_7pt = estimate_matrix_memory(1000, stencil_width=7)
    est_3pt = estimate_matrix_memory(1000, stencil_width=3)
    assert est_7pt > est_3pt
    est_more_rows = estimate_matrix_memory(2000, stencil_width=7)
    assert est_more_rows > est_7pt


def test_analytical_estimate_is_reasonable_upper_bound_for_real_pressure_matrix() -> None:
    """The analytical 7-point estimate should be in the right ballpark
    (same order of magnitude, and an over-estimate since boundary rows
    have fewer than 7 nonzeros) compared to a REAL assembled pressure
    matrix."""
    from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
    from navier3d.pressure import PressurePoissonSystem

    m = mesh(12)
    p = FaceBoundaryCondition(velocity_type=VelocityBCType.PERIODIC, pressure_type=PressureBCType.PERIODIC)
    bcs = BoundaryConditionSet(x_min=p, x_max=p, y_min=p, y_max=p, z_min=p, z_max=p)
    system = PressurePoissonSystem(m, bcs, solver="cg", rhs_compatibility="mean_removal")

    measured = measure_matrix_memory(system.matrix)
    n_cells = m.nx * m.ny * m.nz
    estimated = estimate_matrix_memory(n_cells, stencil_width=7)
    assert measured <= estimated
    assert measured > 0.5 * estimated  # not a wild over-estimate either


# --------------------------------------------------------------------------
# Direct factorization fill-in
# --------------------------------------------------------------------------

def test_measured_factorization_memory_is_positive_and_at_least_matrix_size() -> None:
    n = 300
    diag = np.full(n, 4.0)
    off = np.full(n - 1, -1.0)
    A = sp.diags([diag, off, off], [0, 1, -1], format="csc")
    lu = spla.splu(A)
    fill_bytes = measure_direct_factorization_memory(lu)
    matrix_bytes = measure_matrix_memory(A.tocsr())
    assert fill_bytes is not None
    assert fill_bytes > 0
    assert fill_bytes >= matrix_bytes * 0.5  # L+U together store at least as much as A itself, roughly


# --------------------------------------------------------------------------
# Combined solver-matrix report
# --------------------------------------------------------------------------

def test_solver_matrix_report_analytical_default() -> None:
    m = mesh(10)
    report = estimate_solver_matrix_memory(m)
    assert report.categories["pressure_matrix"] > 0
    assert report.categories["diffusion_matrices"] > 0
    assert report.total_bytes > 0


def test_solver_matrix_report_uses_measured_when_provided() -> None:
    from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType
    from navier3d.pressure import PressurePoissonSystem

    m = mesh(10)
    # Dirichlet (not periodic): boundary rows genuinely have fewer than 7
    # nonzeros, so the measured matrix differs from the 7-point analytical
    # estimate (periodic rows are all exactly 7-wide, which would make
    # this comparison a coincidental no-op).
    d = FaceBoundaryCondition(velocity_type=VelocityBCType.PRESSURE_OUTLET, pressure_type=PressureBCType.DIRICHLET, pressure_value=0.0)
    bcs = BoundaryConditionSet(x_min=d, x_max=d, y_min=d, y_max=d, z_min=d, z_max=d)
    system = PressurePoissonSystem(m, bcs, solver="direct")

    analytical = estimate_solver_matrix_memory(m)
    measured = estimate_solver_matrix_memory(m, measured={"pressure": system.matrix})
    assert measured.categories["pressure_matrix"] == measure_matrix_memory(system.matrix)
    assert measured.categories["pressure_matrix"] != analytical.categories["pressure_matrix"]
    # diffusion still falls back to analytical since not supplied
    assert measured.categories["diffusion_matrices"] == analytical.categories["diffusion_matrices"]


def test_solver_matrix_report_uses_measured_diffusion_matrices_when_provided() -> None:
    from navier3d.diffusion import VelocityDiffusionSystem
    from navier3d.boundary_conditions import BoundaryConditionSet, FaceBoundaryCondition, PressureBCType, VelocityBCType

    m = mesh(10)
    w = FaceBoundaryCondition(velocity_type=VelocityBCType.NO_SLIP, pressure_type=PressureBCType.NEUMANN)
    bcs = BoundaryConditionSet(x_min=w, x_max=w, y_min=w, y_max=w, z_min=w, z_max=w)
    systems = [VelocityDiffusionSystem(m, bcs, axis, nu=0.1, dt=0.01, theta=0.5) for axis in range(3)]

    analytical = estimate_solver_matrix_memory(m)
    measured = estimate_solver_matrix_memory(m, measured={
        "diffusion_u": systems[0].matrix, "diffusion_v": systems[1].matrix, "diffusion_w": systems[2].matrix,
    })
    expected = sum(measure_matrix_memory(s.matrix) for s in systems)
    assert measured.categories["diffusion_matrices"] == expected
    assert measured.categories["diffusion_matrices"] != analytical.categories["diffusion_matrices"]
    # pressure still falls back to analytical since not supplied
    assert measured.categories["pressure_matrix"] == analytical.categories["pressure_matrix"]


# --------------------------------------------------------------------------
# bytes-per-cell and formatting
# --------------------------------------------------------------------------

def test_bytes_per_pressure_cell_is_positive() -> None:
    m = mesh(10)
    report = estimate_field_memory(m)
    per_cell = report.bytes_per_pressure_cell(m)
    assert per_cell > 0


def test_format_report_lists_all_categories() -> None:
    m = mesh(8)
    report = estimate_field_memory(m)
    text = report.format_report()
    assert "pressure_field_p" in text
    assert "TOTAL" in text
    assert "MB" in text


def test_empty_report_format() -> None:
    assert "no memory data" in MemoryReport().format_report()


# --------------------------------------------------------------------------
# psutil-based process memory (skipped if not installed)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not installed")
def test_process_rss_delta_measures_a_real_allocation() -> None:
    def build():
        # np.zeros() pages may be lazily committed by the OS (zero-fill
        # on demand) and not show up in RSS until touched -- fill with a
        # nonzero value to force real physical-page commitment, matching
        # what actually happens when a solver's real (non-all-zero)
        # arrays are populated.
        arr = np.empty(50_000_000 // 8, dtype=np.float64)
        arr.fill(1.0)
        return arr

    delta = measure_process_rss_delta(build)
    assert delta is not None
    # allow generous slack for allocator/OS behavior, just confirm it's
    # measuring something real and roughly the right order of magnitude
    assert delta > 5_000_000


def test_process_rss_delta_none_without_psutil(monkeypatch) -> None:
    import navier3d.memory as memmod
    monkeypatch.setattr(memmod, "HAS_PSUTIL", False)
    assert measure_process_rss_delta(lambda: [0] * 1000) is None
