"""Memory accounting (Milestone 7 Part J).

Two kinds of numbers are reported, and kept clearly labeled as such
throughout:

* **Analytical estimates** -- computed from array shapes / matrix
  stencil widths alone, valid at any resolution (including ones too
  large to actually allocate, e.g. a hypothetical 128^3 case on a
  memory-constrained workstation -- the review: "Do not allocate a
  128^3 test merely to prove the formula if memory is constrained;
  analytical size estimates are acceptable").
* **Measured** -- read directly from a real, already-allocated
  ``scipy.sparse`` matrix's ``.data``/``.indices``/``.indptr`` arrays
  (exact, not approximated) or a real ``splu`` factorization's ``.nnz``
  (the true L+U fill-in for that specific matrix, not a generic
  estimate) or the OS-reported process RSS delta around a real build
  (via ``psutil``, optional dependency -- ``pip install -e ".[perf]"``).

Sparse-matrix byte accounting convention (used throughout): CSR/CSC
storage is ``nnz`` float64 values (8 bytes each) + ``nnz`` int32 column/
row indices (4 bytes each, SciPy's default index dtype for matrices
under 2^31 nonzeros) + ``(n_rows+1)`` int32 pointers -- i.e.
``12*nnz + 4*(n+1)`` bytes, matching what ``.data.nbytes +
.indices.nbytes + .indptr.nbytes`` would report for a real matrix.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .mesh import StructuredMesh3D

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:  # pragma: no cover - exercised only when psutil is absent
    psutil = None
    HAS_PSUTIL = False

_BYTES_PER_FLOAT64 = 8
_BYTES_PER_INDEX = 4  # scipy's default int32 index dtype


@dataclass
class MemoryReport:
    """Byte counts per category (see module docstring for analytical vs.
    measured). ``total_bytes`` is the sum of every category present."""

    categories: Dict[str, int] = field(default_factory=dict)

    @property
    def total_bytes(self) -> int:
        return sum(self.categories.values())

    def bytes_per_pressure_cell(self, mesh: StructuredMesh3D) -> float:
        n_cells = mesh.nx * mesh.ny * mesh.nz
        return self.total_bytes / n_cells if n_cells > 0 else 0.0

    def format_report(self) -> str:
        if not self.categories:
            return "(no memory data recorded)"
        rows = sorted(self.categories.items(), key=lambda kv: kv[1], reverse=True)
        name_width = max(len(k) for k, _ in rows)
        lines = [f"{k:<{name_width}}  {v / 1e6:8.2f} MB" for k, v in rows]
        lines.append(f"{'TOTAL':<{name_width}}  {self.total_bytes / 1e6:8.2f} MB")
        return "\n".join(lines)


def _padded_scalar_elements(mesh: StructuredMesh3D) -> int:
    ng = mesh.n_ghost
    return (mesh.nx + 2 * ng) * (mesh.ny + 2 * ng) * (mesh.nz + 2 * ng)


def _padded_face_elements(mesh: StructuredMesh3D, normal_axis: int) -> int:
    ng = mesh.n_ghost
    sizes = [mesh.nx + 2 * ng, mesh.ny + 2 * ng, mesh.nz + 2 * ng]
    sizes[normal_axis] += 1
    return sizes[0] * sizes[1] * sizes[2]


def estimate_field_memory(mesh: StructuredMesh3D, *, n_temporary_velocity_fields: int = 5) -> MemoryReport:
    """Analytical estimate (exact given the shapes -- these ARE the
    array sizes `fields.py` allocates, not an approximation) for one
    :class:`~navier3d.fields.FlowState`'s own storage plus a rough
    accounting of same-sized temporaries a single
    :meth:`~navier3d.time_integrators.ThetaSchemeIntegrator.step` call
    allocates and discards (predictor ``u*``, AB2/Heun-startup
    convection fields, the projection's corrected velocity and pressure
    gradient -- ``n_temporary_velocity_fields=5`` is a representative
    count for a centered/upwind-convection step with AB2 already
    started; the *first* step allocates one or two more for the Heun
    startup probe, a small, one-time, bounded difference not worth a
    separate code path here)."""
    p_bytes = _padded_scalar_elements(mesh) * _BYTES_PER_FLOAT64
    velocity_bytes = sum(_padded_face_elements(mesh, axis) for axis in range(3)) * _BYTES_PER_FLOAT64

    report = MemoryReport()
    report.categories["pressure_field_p"] = p_bytes
    report.categories["velocity_fields_uvw"] = velocity_bytes
    report.categories["temporary_velocity_fields"] = velocity_bytes * n_temporary_velocity_fields
    return report


def measure_matrix_memory(matrix) -> int:
    """**Measured** (not estimated): exact bytes of a real, already-built
    ``scipy.sparse`` CSR/CSC matrix's storage arrays."""
    return int(matrix.data.nbytes + matrix.indices.nbytes + matrix.indptr.nbytes)


def estimate_matrix_memory(n_rows: int, stencil_width: int) -> int:
    """**Analytical estimate**: a structured-grid discrete-operator
    matrix with a fixed ``stencil_width`` (7 for the 3-D Poisson/velocity
    Laplacian stencils this package assembles -- center + 6 neighbors,
    fewer at boundaries, so this is a slight over-estimate, documented as
    such) has at most ``stencil_width * n_rows`` nonzeros."""
    nnz = stencil_width * n_rows
    return nnz * (_BYTES_PER_FLOAT64 + _BYTES_PER_INDEX) + (n_rows + 1) * _BYTES_PER_INDEX


def measure_direct_factorization_memory(lu) -> Optional[int]:
    """**Measured**: the true L+U fill-in nonzero count of a real
    ``scipy.sparse.linalg.splu`` factorization (``lu.nnz``), converted to
    bytes using the same float64+int32 convention as
    :func:`measure_matrix_memory`. Returns ``None`` if ``lu`` doesn't
    expose ``.nnz`` (unexpected for SciPy's ``SuperLU`` object, but
    guarded rather than assumed)."""
    nnz = getattr(lu, "nnz", None)
    if nnz is None:
        return None
    return int(nnz) * (_BYTES_PER_FLOAT64 + _BYTES_PER_INDEX)


def estimate_solver_matrix_memory(mesh: StructuredMesh3D, *, measured: Optional[dict] = None) -> MemoryReport:
    """Combine pressure + 3 diffusion matrices' memory into one report.
    Analytical by default (7-point stencil estimate, valid at any
    resolution); pass ``measured={"pressure": <matrix>, "diffusion_u":
    <matrix>, ...}`` (real scipy sparse matrices) to use exact measured
    sizes instead wherever supplied."""
    n_cells = mesh.nx * mesh.ny * mesh.nz
    report = MemoryReport()

    if measured and "pressure" in measured:
        report.categories["pressure_matrix"] = measure_matrix_memory(measured["pressure"])
    else:
        report.categories["pressure_matrix"] = estimate_matrix_memory(n_cells, stencil_width=7)

    sizes = (mesh.nx, mesh.ny, mesh.nz)
    diffusion_total = 0
    for axis, name in enumerate(("diffusion_u", "diffusion_v", "diffusion_w")):
        if measured and name in measured:
            diffusion_total += measure_matrix_memory(measured[name])
        else:
            component_sizes = list(sizes)
            component_sizes[axis] += 1  # this component's own normal axis has n_cells+1 faces
            n_component = component_sizes[0] * component_sizes[1] * component_sizes[2]
            diffusion_total += estimate_matrix_memory(n_component, stencil_width=7)
    report.categories["diffusion_matrices"] = diffusion_total

    return report


def measure_process_rss_delta(build_fn) -> Optional[int]:
    """**Measured**: OS-reported resident-set-size delta (bytes) around
    calling ``build_fn()`` -- the review's "at least one moderate case
    should be measured with actual process memory where practical".
    Returns ``None`` if ``psutil`` is not installed (optional
    dependency) rather than raising, so callers can fall back to the
    analytical estimates above."""
    if not HAS_PSUTIL:
        return None
    import gc
    process = psutil.Process()
    gc.collect()
    before = process.memory_info().rss
    result = build_fn()
    gc.collect()
    after = process.memory_info().rss
    del result
    return int(after - before)
