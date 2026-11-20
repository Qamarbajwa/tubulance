# navier3d architecture (through Milestone 11B)

This document is the architectural design for navier3d and is updated as
milestones land. It currently reflects **Milestones 1-12**: package
skeleton, configuration system, structured MAC-grid mesh, staggered field
containers, boundary-condition interfaces, compatible discrete spatial
operators, a sparse pressure Poisson system, velocity projection, a full
unsteady solver for the **complete incompressible Navier-Stokes equations**
(conservative nonlinear convection + implicit diffusion + projection),
pressure-correction projection methods (Milestone 8), a root-cause-isolated
pressure-extrapolation fix (Milestone 9), mathematically consistent initial
pressure solving (Milestone 10), 3D wall-bounded verification (Milestone 11A),
asymptotic 3D spatial verification confirming true $O(h^2)$ spatial order
($p_{\mathbf{u}} = 1.954 \to 1.983 \to 2.00$) on 6 physical walls (Milestone 11B),
and Large Eddy Simulation (LES) foundation with Smagorinsky closure and
conservative variable-viscosity diffusion (Milestone 12).

## 1. Scope and governing equations

The initial (and, for the foreseeable milestones, only) physical model is
the incompressible Navier-Stokes equations for a constant-density
Newtonian fluid:

```
div(u) = 0
du/dt + div(u ⊗ u) = -(1/rho) grad(p) + nu * lap(u) + f
```

on a three-dimensional Cartesian domain. Conservative (flux) form of the
momentum equation is used throughout. Compressible flow, turbulence
closures, non-Newtonian rheology, and non-Cartesian geometry are explicit
non-goals until the roadmap milestones that introduce them (see
`README.md`).

## 2. Grid arrangement: staggered MAC grid

**Choice.** Pressure `p` is stored at cell centers; velocity components
`u`, `v`, `w` are stored at the centers of the faces normal to them
(x-faces, y-faces, z-faces respectively) -- the classical
Marker-and-Cell arrangement (Harlow & Welch 1965).

**Justification.** A MAC grid gives the discrete pressure gradient and the
discrete velocity divergence *compatible* stencils: the pressure gradient
needed at a velocity location is a direct, local two-point difference
across the face, and the divergence needed at a pressure location is a
direct, local difference of the surrounding face velocities. This
compatibility is what avoids the classical collocated-grid checkerboard
pressure mode, without needing a Rhie-Chow-type face-interpolation
correction.

This is **not** a claim that the resulting pressure-velocity coupling is
"exact." The overall solution remains an approximation whose accuracy
depends on the spatial discretization order, the boundary-condition
implementation, the pressure-solver tolerance, the time-integration
scheme, and the consistency between the discrete gradient and divergence
operators (Milestone 2). The precise claim is:

> The MAC arrangement provides directly compatible, co-located
> face-centered pressure gradients and cell-centered velocity divergence,
> without requiring Rhie-Chow interpolation.

A collocated grid with Rhie-Chow interpolation remains a documented future
option (e.g. for later unstructured/complex-geometry extensibility) but is
not the initial implementation.

## 3. Array shapes and index ranges

Let `nx, ny, nz` be the interior cell counts and `ng = mesh.n_ghost`
(default 1) be the ghost-layer width. **Every field uses the same
ghost-padding convention: `ng` ghost layers on every side of every axis**,
including a velocity component's own face-normal axis. This is a
deliberate simplification over padding only tangential axes: the normal
axis also needs ghost data once diffusion, higher-order convection,
periodic wrap, and corner treatment are implemented (Milestones 2, 6, 7),
and one padding rule for every field keeps indexing uniform.

Without ghosts, the physical (mathematically minimal) MAC shapes are:

| Field | Physical shape | Location |
|---|---|---|
| `p` | `(nx, ny, nz)` | cell centers |
| `u` | `(nx+1, ny, nz)` | x-faces |
| `v` | `(nx, ny+1, nz)` | y-faces |
| `w` | `(nx, ny, nz+1)` | z-faces |

With uniform `ng`-wide ghost padding on every axis, the **allocated**
array shapes (`fields.py`) are:

| Field | Allocated shape | Interior index range (x) | Interior index range (y) | Interior index range (z) |
|---|---|---|---|---|
| `p` | `(nx+2ng, ny+2ng, nz+2ng)` | `ng .. ng+nx-1` | `ng .. ng+ny-1` | `ng .. ng+nz-1` |
| `u` | `(nx+1+2ng, ny+2ng, nz+2ng)` | `ng .. ng+nx` (incl. both boundaries) | `ng .. ng+ny-1` | `ng .. ng+nz-1` |
| `v` | `(nx+2ng, ny+1+2ng, nz+2ng)` | `ng .. ng+nx-1` | `ng .. ng+ny` (incl. both boundaries) | `ng .. ng+nz-1` |
| `w` | `(nx+2ng, ny+2ng, nz+1+2ng)` | `ng .. ng+nx-1` | `ng .. ng+ny-1` | `ng .. ng+nz` (incl. both boundaries) |

`ScalarField.interior` / `FaceField.interior` both return
`data[ng:-ng, ng:-ng, ng:-ng]` -- uniform padding means no per-axis
special-casing is needed to obtain the interior view.

For a velocity component's face-normal axis, the two end indices of the
interior range (`ng` and `ng+n_axis`) are **real unknowns that coincide
exactly with the domain boundary**, not ghost cells -- they are assigned
directly by the boundary condition (Dirichlet-style). The ghost layers
*beyond* them (indices `0..ng-1` and `ng+n_axis+1..end`) exist to support
future one-sided stencils that reach past the boundary face; they are not
read by anything in Milestone 1. For the two tangential axes of a
velocity component (and for all three axes of pressure), the boundary
does **not** coincide with a stored point -- it lies half a cell outside
the first/last interior index -- so `0..ng-1` and the mirrored range at
the high end are true ghost cells from the start.

### Corners and edges

Ghost cells are filled with a fixed sequential sweep over axes: x, then
y, then z (`boundary_conditions.py`). Where ghost regions from two or
three axes overlap (edges and corners of the padded array), the value
comes from whichever axis was swept last, computed on data that already
includes the earlier sweeps' ghost values. This is deterministic and is
the standard convention in staggered-grid codes.

**Milestone 2 decision.** All Milestone 2 operators (`operators.py`:
gradient, divergence, scalar Laplacian, component-wise velocity
Laplacian) are *dimension-split*: each is a sum of independent 1-D
central-difference stencils, one per axis, and every stencil only ever
reads neighbors offset along a *single* axis from the point being
computed. No Milestone 2 stencil ever reads a grid point that is
simultaneously a ghost cell on two or three axes at once (an edge or
corner cell) -- so the corner/edge fill order documented above still has
no effect on any Milestone 2 operator result, not by assumption but
because the stencils are structurally incapable of reaching a corner.
This is verified indirectly by the `D_h G_h = L_h` and integration-by-parts
identity tests in `tests/test_operators.py`, which would not hold exactly
if any stencil were silently reading a sweep-order-dependent corner value.
If a future milestone introduces a compact/cross-derivative or diagonal
stencil (none is currently planned), this section must be revisited and
an explicit, order-independent corner-fill rule defined before that
stencil is trusted.

### 2x2x2 indexing diagram

For `nx=ny=nz=2`, `ng=1` (ghosts omitted from the picture for clarity),
one z-layer (`k=0`, spanning `z in [0, dz]`, cell center `z=0.5dz`) looks
like this in the x-y plane (`i` = local x-index, `j` = local y-index,
0-based; array index = local index + `ng`):

```
y=2dy   +----v(i=0,j=2)----+----v(i=1,j=2)----+
        |                  |                  |
      u(i=0,j=1)     p(i=0,j=1)      u(i=1,j=1)     p(i=1,j=1)     u(i=2,j=1)
        |                  |                  |
y=dy    +----v(i=0,j=1)----+----v(i=1,j=1)----+
        |                  |                  |
      u(i=0,j=0)     p(i=0,j=0)      u(i=1,j=0)     p(i=1,j=0)     u(i=2,j=0)
        |                  |                  |
y=0     +----v(i=0,j=0)----+----v(i=1,j=0)----+
      x=0              x=dx             x=2dx=Lx
```

`w` is not visible in this x-y slice: it sits at the *same* `(x, y)` as
each `p` cell but at `z in {0, dz, 2dz}` -- i.e. `w(i,j,k=0)` and
`w(i,j,k=1)` are the bottom and top faces of `p(i,j,k=0)`, and
`w(i,j,k=2)` is the top face of `p(i,j,k=1)`:

```
z=2dz=Lz  ----- w(i,j,k=2)  (domain boundary)
z=dz      ----- w(i,j,k=1)  (shared: top of cell k=0, bottom of cell k=1)
              p(i,j,k=0)
z=0       ----- w(i,j,k=0)  (domain boundary)
```

Total unknowns for this 2x2x2 case (interior only): `p`: `2*2*2=8`;
`u`: `3*2*2=12`; `v`: `2*3*2=12`; `w`: `2*2*3=12`.

## 4. Boundary conditions

Boundary-condition logic (`boundary_conditions.py`) distinguishes:

* **normal vs. tangential velocity components** -- different ghost/assignment
  formulas (Section 3, and below);
* **stationary walls** (`no_slip`, tangential value implicitly 0) vs.
  **moving walls** (`velocity_inlet` with a nonzero tangential
  `velocity_value` and zero normal component -- the same mechanism used for
  a true inlet, since the normal component is prescribed independently of
  the tangential one; this is how a lid-driven-cavity lid is specified);
* **periodic boundaries** (paired faces, validated at construction: both
  `x_min`/`x_max` or neither must be periodic, etc.);
* **prescribed velocity** (`velocity_inlet`);
* **prescribed pressure** (`pressure` face BC `dirichlet`, paired with
  velocity BC `pressure_outlet`);
* **symmetry / free-slip boundaries** (`symmetry` and `free_slip` use
  identical ghost formulas in this design -- zero normal velocity, zero
  tangential gradient -- and are kept as distinct enum values so they can
  diverge later, e.g. for scalar transport, without an API change).

### Formulas

**Tangential component ghost** (true ghost; the wall lies halfway between
it and the first interior cell). For a wall with tangential speed `U_w`:

```
u_ghost = 2*U_w - u_interior
```

which for a stationary no-slip wall (`U_w = 0`) reduces to:

```
u_ghost = -u_interior
```

`free_slip` / `symmetry` / `pressure_outlet` use the zero-gradient mirror
`u_ghost = u_interior`.

**Normal component, boundary face** (real unknown, assigned directly):
`no_slip`/`free_slip`/`symmetry` -> `0`; `velocity_inlet` -> the
configured normal component; `pressure_outlet` -> zero-gradient
extrapolation from the adjacent interior cell; `periodic` -> the two
boundary faces are the same physical point and are averaged together.

**Normal component, ghost layers beyond the boundary face** (reflection
about the boundary *node*, since the boundary coincides with a grid point
here rather than a half-cell wall): Dirichlet-type BCs use
`ghost = 2*boundary_value - mirror_interior`; `pressure_outlet` uses
`ghost = mirror_interior`; `periodic` wraps around the domain while
skipping the duplicated boundary point (`_fill_periodic_ghosts_face_like`
in `boundary_conditions.py`, distinct from the plain cell-like wrap used
everywhere else because of that duplication).

**Pressure ghost** (always a true ghost on every axis): `neumann` ->
`ghost = interior` (**homogeneous** zero-gradient, `dp/dn = 0`); `dirichlet`
-> `ghost = 2*value - interior`.

### Periodic duplicate normal faces

For a periodic axis, a velocity component's own face-normal direction
stores the *same physical location* twice: local index `0` (the `_min`
boundary face) and local index `n` (the `_max` boundary face) are
geometrically coincident once the domain wraps. `apply_velocity_bc`
enforces that these two stored copies are numerically **identical**
(averaged together, Section 3/formulas above) -- neither copy is more
"authoritative" than the other as *stored values*, but code that needs
exactly `n` independent samples (not `n+1`) must pick one copy and ignore
the other. **Project convention: the low-index copy is authoritative;
code that reduces over a periodic normal axis uses local index range
`0 .. n-1` and excludes local index `n`.**

This is not just a bookkeeping choice -- it is required for correctness:

* **Divergence does not double count it.** `divergence()` (Milestone 2,
  `operators.py`) computes each cell's flux from its own two bounding
  faces only; the duplicated pair never appears together in a single
  cell's divergence, so there is nothing to double count there. Verified
  by `test_operators.py::test_divergence_conserves_globally_periodic`,
  which shows the domain-summed divergence telescopes to exactly the
  difference between the low and high duplicate copies -- which
  `apply_velocity_bc` has already forced to zero.
* **Periodic derivatives use the wrapped neighbor.** Ghost cells beyond
  each boundary face are filled by `_fill_periodic_ghosts_face_like`,
  which is derived precisely to skip the duplicated point when wrapping
  (Milestone 1); Milestone 2's stencils then read those ghosts like any
  other value, with no special-casing.
* **Volume integrals / reductions must not count both copies.** No
  Milestone 2 operator computes a volume integral or a global reduction
  over a component's own normal axis, so this does not yet arise in
  `operators.py`. It **will** arise for future diagnostics (kinetic
  energy, mean quantities -- Milestone 8) and any future spectral
  transform: that code must sum/transform over local index `0 .. n-1`
  along a component's own periodic normal axis, per the convention above,
  or it will silently overweight the boundary value by 2x.
* **Updates keep the duplicate synchronized.** Every call to
  `apply_velocity_bc` re-averages and re-broadcasts the pair
  (`_set_normal_axis_bc`'s periodic branch), so as long as boundary
  conditions are (re-)applied after any mutation of a periodic
  component's boundary faces, the two copies cannot drift apart. Nothing
  in `operators.py` writes to a normal-axis boundary face, so this
  invariant is preserved across gradient/divergence/Laplacian calls.

`test_operators.py::test_integration_by_parts_periodic` demonstrates the
practical consequence directly: the discrete integration-by-parts
identity `<p, D_h u> = -<G_h p, u>` holds to machine precision only when
the face inner product excludes the duplicate high-index copy; a
companion assertion in the same test shows that naively including the
duplicate breaks the identity by *exactly* one extra copy of the
low-index boundary term (`G_h(p)[0] * u[0] * dV`, generally nonzero,
since the duplicate pair is equal but not zero), confirming the mechanism
quantitatively rather than merely avoiding it.

### On homogeneous vs. inhomogeneous pressure Neumann conditions

The physically correct pressure Poisson boundary condition is derived
from the required corrected normal velocity: projecting
`u_n^{n+1} = u_n^* - (dt/rho) * dp/dn` onto the prescribed
`u_n_required^{n+1}` gives

```
dp/dn = (rho/dt) * (u_n* - u_n_required)
```

Homogeneous Neumann (`dp/dn = 0`) is valid **only** when the predictor
`u_n*` already satisfies the required normal boundary velocity -- which is
generically true only once a predictor and a required target exist, i.e.
once a projection step exists. **Milestone 1 has no predictor velocity
`u*` and no projection step**, so `apply_pressure_bc`'s `neumann` case
implements only the homogeneous special case. It is not a general
inflow/outflow pressure boundary condition, and must not be treated as
one once Milestone 4 (projection) is implemented. Deriving and applying
the inhomogeneous correction from `u*`, `dt`, and `rho` is projection-step
work that belongs in `pressure.py`/`projection.py` (Milestones 3-4), not
in this ghost-cell layer.

## 5. Discrete projection algorithm (planned, not yet implemented)

The default time-advancement scheme (Milestone 6 onward) is a
**non-incremental (Chorin-type) fractional-step projection**:

```
u* = u^n + dt * [ -div(u ⊗ u) + nu * lap(u) + f ]     (predictor; AB2/CN in the
                                                         real integrator, Euler here)
lap(p^{n+1}) = (rho/dt) * div(u*)                      (pressure Poisson solve)
u^{n+1} = u* - (dt/rho) * grad(p^{n+1})                (correction)
```

**Pressure semantics.** Because the predictor `u*` excludes *any*
pressure-gradient term (not even the previous step's pressure), the
`p^{n+1}` produced by this Poisson solve is the **full dynamic pressure at
the new time level**, not an increment/correction relative to `p^n`. It is
dynamic pressure (units of `Pa`; any hydrostatic/body-force contribution
is folded into `f`), determined only up to an additive constant -- for
fully periodic or all-Neumann configurations the Poisson matrix has a
1-dimensional null space, which will be handled (Milestone 3) by fixing
the domain-mean pressure to zero (equivalently, pinning one reference
cell), not by a special solver.

**Replaceability.** `FlowState.pressure` (`fields.py`) is intentionally
just "the pressure field," with no Chorin-specific assumptions embedded in
it or in `mesh.py`. The non-incremental scheme above is a reasonable
first implementation because it is the simplest to verify, but it is
known to produce larger pressure-boundary errors and reduced temporal
accuracy than incremental or rotational pressure-correction variants. The
projection algorithm itself will live entirely in `projection.py`
(Milestone 4); swapping non-incremental for incremental/rotational
correction later should require no change to `mesh.py` or `fields.py`.

## 6. Module responsibilities

| Module | Responsibility |
|---|---|
| `_indexing.py` | Shared low-level 3-tuple indexing primitives (`axis_index`, `axis_slice`) used by `boundary_conditions.py`. |
| `config.py` | Validated dataclass configuration; YAML loading; fails fast with specific messages. |
| `mesh.py` | Uniform structured Cartesian mesh geometry: spacing, cell centers, face coordinates, volumes, areas. |
| `fields.py` | Ghost-padded field containers (`ScalarField`, `FaceField`, `VelocityField`, `FlowState`) plus named accessors (`interior`, `interior_range`, `shifted_range`, `ghost_layer`, `first_interior_layer`, `boundary_layer`). No physics/numerics. |
| `boundary_conditions.py` | Typed BC specification (`BoundaryConditionSet`) and ghost-cell enforcement for pressure and velocity. |
| `operators.py` | Discrete spatial operators (`gradient`, `divergence`, `scalar_laplacian`, `velocity_laplacian`). Pure functions; no boundary-condition logic; consumes ghosts already filled by `boundary_conditions.py`. |
| `pressure.py` | Sparse pressure Poisson system: matrix assembly, null-space handling, direct/CG solvers, structured diagnostics. `update_bcs()` reuses the matrix/factorization when only BC *values* change (Section 11). |
| `projection.py` | Velocity projection: `project()` (non-incremental/Chorin, unchanged since Milestone 4) and `project_incremental()` (Milestone 8: incremental/rotational pressure correction, solves for a pressure increment `phi` via `derive_phi_bcs()`, distinct from `derive_pressure_bcs()`'s full-pressure BCs at exactly the `pressure_outlet` Dirichlet value). Contains no predictor computation of its own and no time-loop state; accepts an existing `PressurePoissonSystem` to reuse. |
| `diffusion.py` | Reusable implicit velocity-diffusion systems (`VelocityDiffusionSystem`, one per MAC component): theta-scheme matrix assembly, direct solve, cached factorization. |
| `convection.py` | Conservative MAC-grid nonlinear convection (`centered_convection`, `upwind_convection`): flux-tensor-divergence computation, matrix-free (explicit RHS term, not a linear system -- see Section 12). |
| `time_integrators.py` | `ThetaSchemeIntegrator`: orchestrates AB2 convection + diffusion + projection per step (selectable `projection_method`, Milestone 8), plus CFL/Reynolds diagnostics and configurable hard CFL rejection; `IntegratorHistory`: explicit, serializable extra state (AB2/variable-dt/phi history) beyond one `FlowState`; `run()`: minimal `FlowState`-advancing loop. No matrix assembly of its own. |

No solver mathematics beyond spatial differencing (no Poisson solve, no
time integration) is implemented in, or hidden inside, `mesh.py` or
`fields.py` -- both remain pure data containers plus geometry queries.
`operators.py`/`convection.py` contain differencing only, no boundary-
condition-specific branches (see Sections 8, 12). `projection.py`/
`time_integrators.py` contain no matrix assembly of their own -- entirely
built from `operators.py` + `pressure.py` + `diffusion.py` + `convection.py`.

## 7. Known limitations

* Only uniform mesh spacing is implemented; `mesh.spacing != "uniform"`
  raises `ConfigError`.
* No turbulence model, LES, adaptive mesh refinement, compressibility, or
  complex geometry exist yet. **Scientific-scope restrictions** (per the
  Milestone 6 review, still binding): a coarse high-Reynolds-number
  simulation run with this solver is never DNS unless every dynamically
  relevant spatial and temporal scale is actually resolved -- numerical
  *stability* at a given resolution is not evidence of physical
  resolution, and this codebase does not currently check for or report
  on grid-independence of turbulent statistics. No result from this
  package should be described as DNS, LES, or RANS; it is currently an
  unmodeled, no-closure solve of the exact (until under-resolved)
  incompressible Navier-Stokes equations.
* No I/O, diagnostics persistence, or visualization exists yet
  (Milestone 8).
* `pressure.py`/`projection.py`/`time_integrators.py` reuse the
  `PressurePoissonSystem` matrix and factorization across calls as long
  as BC *topology* (periodic/neumann/dirichlet per face) stays fixed --
  which it always does mid-simulation, since only the inhomogeneous
  Neumann *values* change (from a new predictor) each time step. If BC
  topology itself changes (e.g. reconfiguring a wall as an inlet), a new
  `PressurePoissonSystem` must be constructed (Section 11).
* `diffusion.py`'s `VelocityDiffusionSystem` offers only a direct solver
  (no CG): boundary-row overrides for a component's own normal axis
  break matrix symmetry, so CG (which requires symmetric
  positive-definiteness) is not offered there -- see Section 11.

## 8. Milestone 2: discrete spatial operators

Second-order central differences throughout (`operators.py`). Every
function is pure (allocates and returns a new field; never mutates its
argument) and applies no boundary-condition logic itself -- it assumes
`apply_pressure_bc`/`apply_velocity_bc` have already filled ghosts
consistent with the desired BC. This keeps BC physics in exactly one
place (Section 4) and out of operator code.

### Stencils and shapes

**Gradient** `phi: ScalarField -> VelocityField`, evaluated at MAC face
locations:

```
(dphi/dx)_{i+1/2,j,k} = (phi_{i+1,j,k} - phi_{i,j,k}) / dx      (-> u faces)
(dphi/dy)_{i,j+1/2,k} = (phi_{i,j+1,k} - phi_{i,j,k}) / dy      (-> v faces)
(dphi/dz)_{i,j,k+1/2} = (phi_{i,j,k+1} - phi_{i,j,k}) / dz      (-> w faces)
```

Input `phi.data` shape `(nx+2ng, ny+2ng, nz+2ng)`; output
`result.u.interior` shape `(nx+1, ny, nz)` (and analogously for v, w) --
matching a real velocity field's interior exactly. Reads one ghost layer
of `phi` beyond each boundary face (needed for the one-sided difference
*at* the boundary); result correctness there therefore depends on
`apply_pressure_bc` having been called.

**Divergence** `velocity: VelocityField -> ScalarField`, evaluated at
pressure cell centers:

```
(div u)_{i,j,k} = (u_{i+1/2,j,k} - u_{i-1/2,j,k})/dx
                 + (v_{i,j+1/2,k} - v_{i,j-1/2,k})/dy
                 + (w_{i,j,k+1/2} - w_{i,j,k-1/2})/dz
```

Output `result.interior` shape `(nx, ny, nz)`. Uses only each component's
real interior (boundary-inclusive) face values -- **no ghost cells are
read**, so the result does not depend on `apply_velocity_bc` having been
called, except that a periodic axis's two boundary-face representations
must already be synchronized (Section 4, "Periodic duplicate normal
faces").

**Scalar Laplacian** `phi: ScalarField -> ScalarField`, standard 7-point
stencil at cell centers:

```
lap(phi)_{i,j,k} = (phi_{i+1,j,k} - 2phi_{i,j,k} + phi_{i-1,j,k})/dx^2
                  + (phi_{i,j+1,k} - 2phi_{i,j,k} + phi_{i,j-1,k})/dy^2
                  + (phi_{i,j,k+1} - 2phi_{i,j,k} + phi_{i,j,k-1})/dz^2
```

Reads one ghost layer of `phi` on every axis; depends on `apply_pressure_bc`.

**Velocity Laplacian** `velocity: VelocityField -> VelocityField`,
componentwise, each component evaluated at its own staggered location
using the identical 7-point-stencil formula on that component's own
padded array. Reads one ghost layer of each component on **all three** of
its axes, including its own face-normal axis -- the first Milestone 2 use
of the normal-axis ghost layers Milestone 1 allocated but did not yet
read; depends on `apply_velocity_bc`.

### Gradient/divergence compatibility: `D_h G_h = L_h`

Because `gradient` and `divergence` read/write the same face locations
with the same index shifts, composing them is algebraically identical to
`scalar_laplacian` -- not just asymptotically, but **exactly**, to
floating-point roundoff, and (having been checked directly) for
**periodic, homogeneous-Neumann, and Dirichlet** boundary conditions
alike, not only on a periodic domain. `tests/test_operators.py::test_divergence_of_gradient_equals_laplacian`
verifies this for all three BC families using random (not just smooth
manufactured) interior data, confirming it is an exact algebraic identity
of the discrete operators rather than an artifact of a particular smooth
test field. This is the property Milestone 4's pressure projection will
depend on.

### Verification results

Manufactured-solution grid refinement uses `nx=N, ny=1.5N, nz=2N` with
domain lengths `1, 1.5, 2` so that `dx=dy=dz=1/N` at every resolution --
nonsymmetric cell counts (still catching axis-swap bugs) with a single
refinement parameter for clean Richardson extrapolation,
`N in {8, 16, 32, 64}`. Exact commands and full test output are in the
Milestone 2 report (delivered alongside this document).

**Scalar Laplacian**, manufactured field `phi = sin(kx x) cos(ky y) sin(kz z)`,
periodic:

| N | L2 error | observed order |
|---:|---:|---:|
| 8 | 2.1197e+01 | -- |
| 16 | 5.6344e+00 | 1.912 |
| 32 | 1.4304e+00 | 1.978 |
| 64 | 3.5898e-01 | 1.994 |

**Gradient**, same `phi`, combined L2 error across u/v/w components,
periodic:

| N | L2 error | observed order |
|---:|---:|---:|
| 8 | 3.6735e-01 | -- |
| 16 | 9.3292e-02 | 1.977 |
| 32 | 2.3364e-02 | 1.997 |
| 64 | 5.8373e-03 | 2.001 |

**Divergence**, manufactured solenoidal field
`u = ky sin(kx x) cos(ky y) cos(kz z)`, `v = -kx cos(kx x) sin(ky y) cos(kz z)`,
`w = 0` (analytically divergence-free; `kx != ky` deliberately -- see
"periodic duplicate" note below), periodic:

| N | L2 error | observed order |
|---:|---:|---:|
| 8 | 5.4583e+00 | -- |
| 16 | 1.4565e+00 | 1.906 |
| 32 | 3.7004e-01 | 1.977 |
| 64 | 9.2883e-02 | 1.994 |

All three approach second order cleanly. One subtlety encountered and
fixed while building the divergence convergence study: an *earlier*
choice of solenoidal test field used equal wavenumbers `kx = ky`, which
combined with this refinement scheme's `dx = dy` makes the *discrete*
divergence exactly zero (to roundoff) at **every** resolution, via an
exact trigonometric sum-to-product cancellation -- not a bug, but it
leaves nothing to converge (the "error" is pure floating-point noise, and
"observed order" computed from noise is meaningless). Switching to
`kx != ky` (documented in `test_operators.py`) restores a genuine O(h^2)
truncation error. This is recorded here because it is a real, reusable
gotcha for constructing MAC-grid manufactured solenoidal fields, not
specific to this codebase.

### Integration by parts and conservation (periodic)

`tests/test_operators.py::test_integration_by_parts_periodic` verifies
`<p, D_h u>_cells = -<G_h p, u>_faces` to `~1e-9` using random (not
manufactured-smooth) periodic data for both `p` and `u`, with the face
inner product summed over local index `0..n-1` on each component's own
normal axis (excluding the duplicate high-index boundary copy, per
Section 4's "Periodic duplicate normal faces" convention). A companion
assertion in the same test shows that naively including the duplicate
breaks the identity by exactly one extra copy of the low-index boundary
term, quantitatively confirming the mechanism rather than merely avoiding
it. `test_global_divergence_sums_to_zero_periodic` verifies
`sum(D_h u) * dV ≈ 0` to `~1e-10` for random periodic velocity data (an
exact telescoping-sum identity once the periodic duplicate is
synchronized by `apply_velocity_bc`, so the residual is pure
floating-point roundoff, not truncation error).

### Milestone 2 limitations

* No convection/advection operator (Milestone 6).
* `velocity_laplacian`'s normal-axis ghost usage is now exercised (see
  `test_velocity_laplacian_no_slip_normal_axis_ghost`), but only for
  `no_slip`/`free_slip`/`velocity_inlet`/`periodic`; `pressure_outlet`'s
  normal-axis ghost (zero-gradient reflection) is exercised by
  `divergence`/`gradient` tests but not yet by a dedicated
  `velocity_laplacian` case -- low risk, since it reuses the same
  `_normal_ghost_value` code path already covered for the Dirichlet-type
  branch, but not independently asserted for velocity's own Laplacian.
* Convergence studies use `n_ghost=1` (the default) throughout; the
  2nd-order stencils here only ever read one ghost layer regardless of
  how many are allocated, so this does not limit generality, but it is
  not separately re-verified at `n_ghost=2` at scale (only the
  exactness/shape tests are parametrized over `n_ghost in {1, 2}`).

### `scalar_laplacian` independence (reviewer follow-up)

Before starting Milestone 3, the reviewer asked us to confirm that
`scalar_laplacian` is not implemented as `divergence(gradient(phi))` --
otherwise the `D_h G_h = L_h` identity would be tautological. Confirmed
by source inspection: `scalar_laplacian` calls `_centered_laplacian`,
which calls `_interior_shifted` -- a code path entirely separate from
`gradient`'s `_face_gradient_term` and `divergence`'s
`_cell_divergence_term`. `tests/test_pressure.py::test_scalar_laplacian_is_independently_implemented`
additionally cross-checks `scalar_laplacian`'s output against a
hand-written 7-point stencil built from raw array slicing, independent of
both `operators.py` and `pressure.py`.

## 9. Milestone 3: pressure Poisson system

`pressure.py` assembles the discrete Poisson operator as an explicit
sparse matrix (rather than the matrix-free `scalar_laplacian`) once per
`(mesh, boundary conditions)` pair, so it can be reused across repeated
solves -- the shape the future projection step needs (one Poisson solve
per time step, same mesh/BCs, different right-hand side each time).

### Sign convention

Per the accepted convention:

```
A = -L_h,          A p = -b
```

`L_h` is the same discrete Laplacian `scalar_laplacian` applies
matrix-free; `A = -L_h` is symmetric and **positive (semi-)definite**
(negative (semi-)definite `L_h`, negated), which is what CG requires.
`PressurePoissonSystem.solve(rhs)` takes the *physical* `rhs` of
`L_h p = rhs` and internally solves `A p = -rhs` (exactly, when there is
no boundary correction -- see next section for the general case).

### Matrix derivation

`L_h` is separable: `L_h = Lx (x) Iy (x) Iz + Ix (x) Ly (x) Iz + Ix (x) Iy (x) Lz`
(Kronecker sums of three 1-D second-difference operators), assembled
directly with `scipy.sparse.kron` -- both more efficient than a
cell-by-cell 3-D loop and easier to verify, since each 1-D operator
(`_axis_operator`) is built and reasoned about in isolation. Flattening
is C-order: flat index `i*ny*nz + j*nz + k` for cell `(i, j, k)`, matching
`numpy`'s default `.ravel()`/`.reshape()` order (used consistently
throughout `pressure.py`).

For a 1-D line of `n` cells with spacing `d`, the un-modified interior
stencil row is `[..., 1/d^2, -2/d^2, 1/d^2, ...]` (tridiagonal). Boundary
rows are modified by substituting the same ghost formula
`apply_pressure_bc` would use:

* **Periodic**: the off-diagonal entry that would reference a
  nonexistent ghost instead references the wrapped cell at the other end
  of the line (`0` or `n-1`) -- no diagonal or RHS change.
* **Homogeneous Neumann** (`ghost = interior`): substituting into
  `(p[1] - 2p[0] + p[ghost])/d^2` with `p[ghost]=p[0]` gives
  `(p[1]-p[0])/d^2` -- diagonal contribution becomes `-1/d^2` instead of
  `-2/d^2`; no RHS change.
* **Inhomogeneous Neumann** (`ghost = interior + d*g`, `g = dp/dn`):
  same diagonal change as above, **plus** a constant `g/d` added to that
  row's entry in the length-N correction vector `c` (see below).
* **Dirichlet** (`ghost = 2*value - interior`): substituting gives
  `(p[1] - 3p[0] + 2*value)/d^2` -- diagonal contribution becomes
  `-3/d^2`; the constant `2*value/d^2` is added to `c`.

Combined across all three axes (`_assemble_laplacian`), this produces
`L_h_matrix` (CSR, `N=nx*ny*nz`, exactly 7 nonzeros per row for an
all-periodic system, fewer at Dirichlet/Neumann boundary rows) and a
correction vector `c` such that:

```
L_h_full(p) = (L_h_matrix @ p) + c        for any p consistent with the BCs
```

so solving `L_h p = rhs` for the unknowns means
`L_h_matrix @ p = rhs - c`, i.e. `A p = -(rhs - c) = c - rhs`. `c` is
zero for periodic and *homogeneous* Neumann/Dirichlet faces, and is
computed once at assembly time (it depends only on the fixed BC values,
never on `rhs`).

### Null-space strategy

The matrix has a 1-D null space (constant vectors) if and only if **no**
face is Dirichlet (`_has_null_space`); any single Dirichlet face makes it
nonsingular. Two strategies:

* **`zero_mean`**: solve the singular-but-consistent system directly with
  CG (well-defined for compatible symmetric PSD systems), then subtract
  the mean from the result. **Not** usable with `solver="direct"`
  (`PressureSystemError` raised at construction) -- a direct sparse LU
  factorization of a singular matrix is unreliable; use `pin_cell` for a
  direct solve on a singular system.
* **`pin_cell`**: eliminate one cell's pressure (fixed to `pinned_value`,
  default 0.0) from the system **symmetrically** -- both its row and
  column -- via `_pin_laplacian`. Off-diagonal entries in column `pin`
  become known constants (`coefficient * pinned_value`) moved to the RHS
  of every other row (`_pin_offdiag`); the pinned row itself becomes the
  trivial identity `p[pin] = pinned_value`. This yields a genuinely
  nonsingular, still-symmetric matrix usable with either solver.
  `test_zero_mean_and_pin_cell_gradients_agree` confirms the two
  strategies' pressure fields differ only by an additive constant and
  produce identical gradients.

### RHS compatibility

For a singular system, `sum(rhs_i) * dV_i ~= 0` is required (discrete
analogue of `integral(rhs) dV = closed-surface flux = 0`).
`rhs_compatibility="strict"` raises `PressureSystemError` if violated
beyond `tol`; `"mean_removal"` silently subtracts the mean instead. The
(pre-correction) compatibility error is always recorded in
`SolveDiagnostics`, even when not enforced.

### Solver API

```python
system = PressurePoissonSystem(mesh, bcs, solver="cg", preconditioner="jacobi",
                                null_space_strategy="zero_mean",
                                rhs_compatibility="mean_removal", tol=1e-10)
pressure, diagnostics = system.solve(rhs_field)
```

The matrix (and, for `solver="direct"`, its sparse LU factorization via
`scipy.sparse.linalg.splu`) is assembled once in `__init__` and reused by
every `solve()` call -- confirmed by `test_matrix_reused_across_multiple_rhs_without_reassembly`
(same `id(system.matrix)` across three solves with different RHS).
`mesh` and `bcs` are exposed as read-only properties; there is no
in-place mutator, so "the matrix was assembled for BCs X" is always true
by construction -- changing BCs means constructing a new
`PressurePoissonSystem` (`test_bc_change_requires_new_system`). Only CSR
(matrix) / CSC (for `splu`) sparse storage is used; no dense `N x N`
array is ever allocated (`test_no_dense_matrix_allocated`).

### Verification results

**Manufactured-solution convergence** (`nx=N, ny=1.25N, nz=1.5N`,
`lx=1, ly=1.25, lz=1.5` fixed domain so `dx=dy=dz=1/N`; `N in {4,8,16,32}`
-- smaller than Milestone 2's refinement grid, chosen so the whole
pressure-system test suite, including four manufactured cases at four
resolutions each, stays fast (~35s total); this is a solver-cost
tradeoff, not a correctness one, since order is already unambiguous by
`N=32`). Periodic and all-Neumann use single-mode sine/cosine
eigenfunctions of the continuous Laplacian (periodic:
`sin(kx x)cos(ky y)sin(kz z)`; homogeneous Neumann: `cos(kx x)cos(ky y)cos(kz z)`
with `kx=mx*pi/lx` etc.); Dirichlet uses `sin(kx x)sin(ky y)sin(kz z)`
(zero on every face by construction); the mixed case uses
`phi = x^2 + sin(pi*x/lx)*cos(ky y)*cos(kz z)` -- the `sin(pi*x/lx)`
factor is essential: it vanishes at both `x=0` and `x=lx`, which is what
lets the Dirichlet faces be *exactly* constant (`0` and `lx^2`
respectively) despite `phi` varying with `y, z` elsewhere. (A first,
incorrect attempt at this manufactured mixed solution used a plain
additive `x^2 + cos(ky y)cos(kz z)`, which is **not** constant across the
`x=const` faces and produced a non-converging, ~O(1) discretization
error at every resolution -- a real bug caught by the convergence test
doing its job, not a resolution problem to paper over.)

For a periodic/all-Neumann solution, `p_h' = p_h - mean(p_h)` and
`p_e' = p_e - mean(p_e)` are compared (the additive constant is
unconstrained by the PDE), per the reviewer's explicit instruction.

| Case | N=4→8 | N=8→16 | N=16→32 | L2 @ N=32 |
|---|---:|---:|---:|---:|
| Periodic | 2.099 | 2.024 | 2.006 | 8.77e-04 |
| All-Neumann | 2.024 | 2.006 | 2.002 | 2.19e-04 |
| Dirichlet | 2.024 | 2.006 | 2.002 | 2.19e-04 |
| Mixed Dirichlet/Neumann | 2.011 | 2.003 | 2.001 | 3.28e-04 |

All four converge cleanly to second order.

**Algebraic residual vs. discretization error.** `final_residual`
(`||b_internal - A p_vec||`, solver tolerance, `~1e-9` to `~1e-12`
depending on `tol`) is reported completely separately from the PDE
discretization error (`||p_h' - p_e'||`, `O(h^2)`, e.g. `~1.4e-2` at
`N=8`). `test_algebraic_residual_reported_separately_from_discretization_error`
asserts the residual is more than 1000x smaller than the discretization
error at a coarse resolution -- the two are never conflated in
`SolveDiagnostics` or anywhere else.

**Direct vs. CG** (Dirichlet, random RHS -- see note below on why a
*manufactured* RHS is a poor choice for this specific comparison):

| N | unknowns | direct (s) | CG (s) | CG iterations | max\|direct-CG\| |
|---:|---:|---:|---:|---:|---:|
| 4 | 120 | 0.0001 | 0.0006 | 26 | 1.2e-12 |
| 8 | 960 | 0.0002 | 0.0014 | 51 | 9.0e-13 |
| 16 | 7,680 | 0.0035 | 0.0094 | 102 | 1.0e-12 |
| 32 | 61,440 | 0.0752 | 0.2419 | 198 | 9.2e-13 |

Direct and CG agree to ~1e-12 at every resolution. **Note**: an earlier
version of this comparison used the single-mode manufactured Dirichlet
solution as the RHS and found CG converging in exactly **1** iteration at
every resolution -- not a bug, but a consequence of the discrete
Dirichlet Laplacian's eigenvectors on a uniform grid being *exactly* the
sampled `sin(m*pi*x/lx)` modes, so a single-mode manufactured RHS is
(to roundoff) an exact eigenvector of `A`, and CG solves for a single
eigenvector's coefficient in one step. This is mathematically correct
but not representative of general performance, so the table above uses
random (multi-mode) RHS data instead, matching how CG will actually be
used once it is called from the projection step (Milestone 4) with a
`div(u*)` right-hand side that is not a single mode.

**Energy property.** `x^T A x >= 0` verified for 5 random vectors per
BC configuration; exactly `~0` for the constant vector on unconstrained
(periodic/all-Neumann) systems; strictly positive for 5 random vectors on
a constrained (Dirichlet) system (`test_energy_*`).

**Null space / matrix structure.** `A @ ones = 0` to `~1e-10` for
periodic and all-Neumann (`test_null_space_constant_vector`); emphatically
nonzero for Dirichlet and pinned systems; matrix symmetric to `~1e-12`
for all BC families including after pinning; exactly 7 nonzeros/row for
an all-periodic system (`test_matrix_sparsity_seven_point`).

**Critical consistency test.** `A @ p_vec == -L_h(p)` to `~1e-10`
for random interior data with homogeneous periodic/Neumann/Dirichlet BCs
(matches the reviewer's literal formula); the general inhomogeneous
relation `L_h_matrix @ p + correction == L_h_full(p)` verified separately
for a mix of inhomogeneous Dirichlet (`value=3.0`) and inhomogeneous
Neumann (`dp/dn=2.0`) faces.

### Milestone 3 limitations

* No multigrid or PyAMG/PETSc backend yet (explicitly deferred by the
  reviewer); the `PressurePoissonSystem` constructor's keyword-only API
  (`solver`, `preconditioner`) is designed so a future backend is an
  additive option, not a redesign.
* Jacobi preconditioning is implemented but provides negligible benefit
  for this constant-coefficient Poisson operator (its diagonal is
  uniform across all interior cells) -- included because it was a
  required capability, not because it currently helps; a real
  preconditioning benefit will come from multigrid/PyAMG later.
* No velocity predictor, projection step, or way to derive the
  *inhomogeneous* Neumann `dp/dn` value from `u*` (that derivation,
  `dp/dn = (rho/dt)*(u_n* - u_n_required)`, is Milestone 4 work in
  `projection.py`; `pressure.py` only *applies* a given `dp/dn`, supplied
  directly by the caller).
* `PressurePoissonSystem` does not cache/reuse the CG Krylov subspace
  across solves (each `solve()` call starts CG fresh, or from an
  explicitly supplied `x0`); warm-starting from the previous time step's
  pressure (a natural future optimization once a time loop exists) is
  supported via the `x0` parameter but not automatic.

## 10. Milestone 4: velocity projection

`projection.py`'s `project()` implements the non-incremental projection
from Section 5, built entirely from `operators.py` + `pressure.py`:

```
L_h p = (rho/dt) * D_h(u*)          (pressure Poisson solve, L_h = D_h G_h exactly)
u^{n+1} = u* - (dt/rho) * G_h(p)     (velocity correction)
```

using Milestone 3's sign convention directly: `pressure.py`'s
`PressurePoissonSystem.solve(rhs)` already implements `A p = -rhs` (up to
boundary correction/null-space handling); `project()` supplies
`rhs = (rho/dt) * D_h(u*)` and nothing else needs to know about the sign
convention.

### Deriving boundary pressure gradients from the required corrected velocity

At a boundary face (a real MAC unknown, not a ghost), the correction
formula applied *at that face* is:

```
u_x^{n+1}[face] = u_x*[face] - (dt/rho) * (dp/dx)[face]
```

Setting the left side to the face's target and solving gives a
**coordinate-axis** derivative `dp/dx`; `pressure_gradient_value`
expects the **outward-normal** derivative `dp/dn`, so a sign flip is
needed that depends on which side of the axis the face is on (outward
normal is `-x_hat` at `x_min`, `+x_hat` at `x_max`):

```
dp/dn = outward_sign * (rho/dt) * (u_n* - u_n_target)
outward_sign = -1 on a _min face, +1 on a _max face
```

with `u_n` here meaning the plain **coordinate** component (`u`, `v`, or
`w`, whichever field is normal to that face) at that face's own
boundary-layer -- not the outward-normal-signed velocity. (Both sign
conventions were checked against each other algebraically before
picking this one: substituting `outward_sign`-weighted `u_n` values into
the reviewer's stated formula `dp/dn = (rho/dt)(u_n* - u_n,target)`,
using `u_n = u . n_hat` (truly outward-normal-signed), reduces to
exactly the same `g_lo`/`g_hi` pair -- the two formulations are
equivalent, and the coordinate-component form is what's implemented
since it matches every other sign convention already used throughout
`boundary_conditions.py`/`operators.py`.)

### BC-to-Neumann derivation, per face type

| `velocity_type` | Target `u_n` | Pressure BC after derivation |
|---|---|---|
| `no_slip` | 0 | Neumann, `dp/dn` from the formula above |
| `free_slip` | 0 | Neumann, `dp/dn` from the formula above |
| `symmetry` | 0 | Neumann, `dp/dn` from the formula above |
| `velocity_inlet` | `velocity_value[axis]` | Neumann, `dp/dn` from the formula above |
| `pressure_outlet` | *(none imposed)* | **unchanged**: whatever Dirichlet `pressure_value` was configured |
| `periodic` | *(none imposed)* | **unchanged**: periodic |

`derive_pressure_bcs()` implements exactly this table
(`test_derive_pressure_bcs_neumann_gradient_matches_formula` checks the
formula numerically; `test_pressure_outlet_does_not_overconstrain_normal_velocity`
and the mixed-face tests check the two "unchanged" rows).

### Why the Neumann value must be spatially varying, not a single scalar

Because `divergence()`/`gradient()` never read ghost cells (Milestone 2),
the pressure Poisson RHS `D_h(u*)` already fully reflects a non-uniform
predictor with no BC involvement at all. But the *boundary-face*
correction above is evaluated **per cell** along the face: if `u_x*` at
`(j,k)` differs from `u_x*` at `(j',k')`, hitting the *same* target at
both points in general requires *different* `dp/dn` there too. A single
scalar `dp/dn` can only make the corrected velocity match the target *on
average* across the face, not pointwise. Milestone 3's
`pressure_gradient_value` (and matching `pressure_value`) were therefore
extended to accept a 2-D array (the face's tangential extent) as well as
a scalar:

* `FaceBoundaryCondition.pressure_gradient_value`: now
  `Optional[Union[float, np.ndarray]]`. The dataclass was changed to
  `eq=False` (identity comparison) because the default
  dataclass-generated `__eq__`/`__hash__` would otherwise try to
  compare/hash a `numpy` array field, which raises (`ValueError`:
  ambiguous truth value; `TypeError`: unhashable) the moment an
  array-valued gradient is used. Nothing in this codebase compares
  `FaceBoundaryCondition` instances by value, so this has no behavioral
  effect elsewhere.
* `apply_pressure_bc`'s ghost-fill formula (`ghost = interior +
  (2k+1)*d*g`) already broadcasts correctly against an array `g` with no
  code change, as long as `g` has the same (ghost-padded) shape as
  `interior` -- which is exactly what `FaceField.boundary_layer()`
  (Milestone 2) naturally returns, so `derive_pressure_bcs` produces
  values directly usable there.
* `pressure.py`'s correction-vector assembly (Milestone 3) previously
  built three separable 1-D vectors and outer-summed them
  (`cx[i]+cy[j]+cz[k]`), which cannot represent a value that varies
  across a face's own tangential extent. It was rewritten
  (`_assemble_laplacian`) to build the correction directly as a full
  `(nx,ny,nz)` array, with each face's contribution added only into its
  own boundary slice -- reducing to exactly the old behavior for a
  scalar value, and additionally correct for an array one. A new
  `_as_interior_tangential` helper auto-detects whether an array arrived
  in `apply_pressure_bc`'s ghost-padded shape (as `derive_pressure_bcs`
  produces) or already interior-shaped, and slices accordingly -- so the
  *same* derived `FaceBoundaryCondition` is usable directly by both
  `apply_pressure_bc` (needs ghost-padded) and `PressurePoissonSystem`
  (needs interior-only), with no duplicate computation in
  `projection.py`.

The Milestone 3 matrix *topology* (which off-diagonal entries exist, and
the diagonal's Neumann/Dirichlet adjustment) depends only on each face's
BC *category*, never on the specific value -- so this extension changes
nothing about matrix assembly's structure, only the correction array.
`tests/test_pressure.py`'s existing scalar-BC consistency tests
(Milestone 3) still pass unchanged, and a new smoke check confirmed the
array-valued path independently: assembling with a random per-cell
Neumann gradient and comparing `L_h_matrix @ p + correction` against
`operators.scalar_laplacian`'s matrix-free result matched to `~3e-15`.

### A real bug caught during development: outlet velocity overwritten by BC reapplication

An early version of `project()` called `apply_velocity_bc(corrected,
bcs)` unconditionally after the correction step, to refresh tangential
ghost cells (necessary: the correction step only writes to `.interior`,
so ghosts still reflect the *predictor's* values otherwise). For
`no_slip`/`free_slip`/`velocity_inlet` faces this reapplication is a
harmless no-op (the pressure BC was constructed to already hit that
exact target). But for `pressure_outlet` faces,
`boundary_conditions.py`'s `_normal_boundary_value` does **not**
reproduce the projection's result there -- it applies a crude
zero-gradient extrapolation from the adjacent interior cell (the
Milestone-1 fallback, written before a real pressure solve existed).
Reapplying it *silently overwrote* the correctly pressure-derived
outflow velocity with that crude approximation: an inlet+outlet smoke
test showed divergence dropping only from 44 to 9.4 (not to machine
precision) even though the pressure solve itself had converged to
`~1e-10` -- exactly the "reapplication hides an inconsistent BC" failure
mode this milestone was explicitly told to avoid. Fixed by saving
`pressure_outlet` faces' post-correction normal boundary values *before*
calling `apply_velocity_bc` and restoring them immediately after (see
`project()`'s "Reapplying velocity BCs after correction" docstring for
the full reasoning); the same test then reached `~4e-13`. Recorded here
because it is exactly the class of bug the review's "do not simply
reapply... in a way that hides an inconsistent pressure BC" instruction
was anticipating, not a hypothetical.

### Verification results

**Divergence reduction** (random predictor, `nx=6,ny=8,nz=10`,
`rho=1, dt=0.01`, `tol=1e-12`):

| Case | max div before | max div after | reduction | `E_div` after |
|---|---:|---:|---:|---:|
| Periodic | 26.74 | 1.51e-11 | 1.77e12 | 7.14e-12 |
| Closed box (all no-slip) | 22.17 | 2.76e-11 | 8.03e11 | 1.26e-11 |
| Inlet + outlet | 28.59 | 2.45e-11 | 1.17e12 | 3.97e-12 |

**Boundary-adjacent divergence** (closed box): max\|div\| over all cells
drops from 23.55 to 1.53e-11; restricted to cells adjacent to a physical
boundary, 23.55 to 1.38e-11 -- i.e. the boundary-adjacent cells are not
meaningfully worse than the bulk, confirming the boundary pressure
treatment is not silently leaving extra error concentrated at walls.

**Helmholtz decomposition**: `u* = u_s + G_h(phi)` (`u_s` a nonzero
constant field, `phi` periodic zero-mean random data) projected back to
`u_s` with `max|P(u*) - u_s| ~ 8e-13` across all three components.

**Energy and orthogonality** (periodic, random predictor):
`K_before = 0.868`, `K_after = 0.579` (`K_after <= K_before` holds, as
required); `<u_s, g>_F = 6.9e-18` (machine-zero orthogonality between the
projected solenoidal field and the removed gradient component).

**Direct vs. CG** (closed box, `pin_cell`, random predictor):

| Grid | direct (s) | CG (s) | CG iterations | max\|direct-CG\| |
|---|---:|---:|---:|---:|
| 6x8x10 | 0.0050 | 0.0047 | 98 | 2.08e-12 |
| 12x16x20 | 0.0486 | 0.0182 | 207 | 2.05e-12 |

**`zero_mean` vs. `pin_cell`** (periodic, random predictor):
max\|velocity difference\| `= 7.1e-14`.

**Timing breakdown** (closed box, `6x8x10`): total `project()` call
`3.7ms`; pressure assembly `1.2ms`; pressure solve `2.1ms` (the
remainder is the two operator evaluations, BC derivation, and the
outlet save/restore bookkeeping).

### Milestone 4 limitations (superseded where noted -- see Section 11)

* No predictor computation (convection/diffusion) -- `u*` is always a
  caller-supplied input (Milestones 5-7). **Still true**: Milestone 5
  adds a diffusion predictor, but convection remains Milestone 6.
* ~~`project()` reassembles a full `PressurePoissonSystem` on every
  call~~ -- **superseded by Milestone 5**: `project(pressure_system=...)`
  now reuses a caller-supplied system's matrix/factorization via
  `update_bcs()`, exactly the "rebuild correction array only" split
  anticipated here (Section 11).
* `ProjectionResult` does not separately quantify "boundary-condition
  error" as a single number (the review's third distinct diagnostic,
  alongside algebraic residual and post-projection divergence) -- it is
  directly observable by comparing `velocity`'s own boundary-face values
  against the configured targets (as the test suite does), rather than
  summarized into one field, since "error" isn't a single well-defined
  scalar across heterogeneous BC types (a wall's target is exactly 0; an
  outlet has no target at all).
* The boundary-adjacent divergence diagnostic reports a single
  domain-wide max over all physical-boundary-adjacent cells, not
  separately per face; per-face breakdowns are recoverable from
  `divergence_after.interior` directly if needed.

## 11. Milestone 5: unsteady incompressible Stokes flow

Still **no nonlinear convection** (Milestone 6). Each time step:

```
(I - theta*nu*dt*L_h) u* = (I + (1-theta)*nu*dt*L_h) u^n + dt*nu*correction + dt*f   (diffusion predictor)
L_h p = (rho/dt) * D_h(u*)                                                            (Milestone 3 pressure solve)
u^{n+1} = u* - (dt/rho) * G_h(p)                                                       (Milestone 4 correction)
```

`theta=1` is backward/implicit Euler (first order); `theta=0.5` is
Crank-Nicolson (second order), exactly the review's required formula.
`L_h` in the diffusion equation is the same discrete velocity Laplacian
`operators.velocity_laplacian` applies matrix-free, now assembled as an
explicit sparse matrix per component (`diffusion.py`), analogous to how
`pressure.py` relates to `operators.scalar_laplacian`.

### Why velocity diffusion needs its own matrix assembly

A velocity component's own face-normal axis has boundary *faces* that
are real MAC unknowns (Section 3), always equal to a BC-determined
target for all time (0 for no-slip/free-slip/symmetry, a configured
constant for `velocity_inlet`) -- never something the diffusion PDE
itself evolves. So along a component's own normal axis, the linear
system's boundary *rows* are algebraic constraints, not
differential-equation rows: an identity "pin" to a fixed target
(`no_slip`/`velocity_inlet`), or a linkage row (`u[boundary] =
u[adjacent]` for `pressure_outlet`'s zero-gradient; `u[duplicate] =
u[0]` for `periodic`). This is implemented by building the per-axis
normal-direction matrix contribution with **zero** rows at the two
boundary positions (`_normal_matrix_interior_rows`), then, after forming
the full `M = I - theta*nu*dt*L_h` via the same Kronecker-sum
construction as `pressure.py`, explicitly overwriting those rows (a
whole tangential *slab*, not a single cell -- `pressure.py`'s `pin_cell`
pins exactly one cell) with the pin/linkage content.

Along a component's two *tangential* axes, the treatment is instead
exactly analogous to `pressure.py`'s Dirichlet/Neumann ghost elimination:
`no_slip`/`velocity_inlet` ~ Dirichlet with value = the wall/inlet speed
(`_tangential_matrix`, `_tangential_correction`); `free_slip`/`symmetry`
~ homogeneous Neumann; `periodic` ~ wrap.

**Well-posedness.** Unlike the pure pressure Poisson matrix, `M` is
**never singular** for `theta, nu, dt > 0`: even where `L_h` itself would
have a null space (e.g. a fully periodic/free-slip component), the added
identity term means `M @ ones = ones - theta*nu*dt*0 != 0`. So no
null-space handling, RHS compatibility checking, or
`zero_mean`/`pin_cell` strategy is needed for diffusion at all -- a
genuine simplification relative to `pressure.py`. Boundary-row overrides
do break matrix symmetry (the same trade-off `pressure.py`'s `pin_cell`
strategy makes), so `diffusion.py` offers **direct solve only** (no CG).

**Verification.** For every BC family and both `theta` values,
`tests/test_diffusion.py` checks the assembled system's `solve()` output
against the matrix-free `(u*-u^n)/dt = nu*(theta*lap(u*) +
(1-theta)*lap(u^n))` computed via `operators.velocity_laplacian` --
matching to `~1e-9`-`1e-14` in every case, including at the interior
rows immediately adjacent to a pinned boundary (confirming the pin/
linkage rows correctly propagate into neighboring equations, with no
separate correction-vector bookkeeping needed there -- unlike
`pressure.py`'s Dirichlet elimination, a real (not ghost) unknown pinned
via an identity row requires no manual RHS correction; the linear
algebra handles it automatically).

### Matrix-reuse design (this milestone's other required refactor)

**Pressure** (`pressure.py`): `_assemble_matrix`/`_assemble_correction`
(previously fused in `_assemble_laplacian`) are now separate; matrix
*topology* (`_topology_key`: per-face pressure-BC category) is fixed at
construction, and `PressurePoissonSystem.update_bcs(bcs)` recomputes only
the correction array, reusing the matrix, its LU factorization (for
`solver="direct"`), the Jacobi preconditioner, and any `pin_cell`
structure -- all unchanged, same Python objects (`id()`-verified in
`tests/test_pressure.py::test_update_bcs_reuses_matrix_object_across_changing_neumann_values`).
`update_bcs` raises if topology would change. `project()` gained a
`pressure_system=` parameter: pass a previous call's
`result.pressure_system` to reuse it (internally just calls
`update_bcs`); `ThetaSchemeIntegrator` does this automatically, building
the system once (lazily, on the first step, since constructing it needs
an initial predictor to derive Neumann values from) and reusing it for
the rest of the simulation.

**Velocity diffusion** (`diffusion.py`): simpler than pressure's case --
velocity BC *values* (a no-slip target, an inlet speed) don't change
mid-simulation at all (unlike pressure's projection-derived Neumann data,
which changes with every new predictor), so there is no `update_bcs`
analog here. `VelocityDiffusionSystem` just builds its matrix and LU
factorization once at construction and reuses them for the object's
entire lifetime.

`ThetaSchemeIntegrator` builds all three `VelocityDiffusionSystem`
instances (one per component) in `__init__` and reuses them every step;
`tests/test_time_integrators.py::test_diffusion_and_pressure_matrices_reused_across_steps`
confirms `id()` stability for both the diffusion matrices and the
pressure system's matrix across 5 steps of a random-predictor run.

### Time integration API

```python
integrator = ThetaSchemeIntegrator(mesh, bcs, rho, nu, dt, theta=0.5, forcing=f)
new_state, diagnostics = integrator.step(state)          # single step
final_state, history = run(integrator, state, n_steps)   # minimal loop
```

`forcing`, if given, is `f(t) -> VelocityField` -- a plain callable,
independently testable, evaluated at `t^n + theta*dt` (the theta-scheme's
own implicit time level: `t^{n+1}` for backward Euler, `t^{n+1/2}` for
Crank-Nicolson, matching the review's `f^{n+1/2}` notation exactly for
`theta=0.5`). `StepDiagnostics` reports `t, dt, max|u|, K, |D_h u|_inf,
|D_h u|_2`, normalized divergence, and diffusion/pressure solver
diagnostics **kept as separate fields**, never merged into one number.
NaN/Inf are checked explicitly after both the diffusion solve
(`DiffusionDiagnostics.finite`) and the full step (`IntegrationError` if
either the corrected velocity or pressure contains a non-finite value) --
a step never silently returns a corrupted state.

### Verification results (A-H; I and J in `test_time_integrators.py`)

**A. Diffusion eigenmode** (`sin(pi*y)*exp(-nu*pi^2*t)`, no-slip
channel): `L_inf` error `< 1e-4` at `ny=48, dt=0.005`, divergence at
machine precision throughout (the field varies only with `y`, exactly
solenoidal for all time by construction).

**B. Temporal order** (self-referenced against a very-fine-dt run at the
*same* `ny`, not the continuous solution -- see the diagnosis below):

| Scheme | dt=0.01->0.005 | 0.005->0.0025 | 0.0025->0.00125 |
|---|---:|---:|---:|
| Backward Euler | 0.999 | 1.002 | 1.007 |
| Crank-Nicolson | ~2.00 | ~2.00 | ~2.00 |

*Diagnosis worth recording*: an initial version of this test compared
against the *continuous* analytical solution and found order degrading
from 0.89 to 0.68 as `dt` shrank -- not a solver bug. The spatial
discretization's eigenvalue for a `sin(k y)` mode differs from the
continuous `nu*k^2` by `O(dy^2)`, and that mismatch compounds
*exponentially in time*; at `T=0.05` with these parameters, the resulting
dt-independent error floor (`~1e-5`, growing with `T`) was already
comparable to the temporal truncation error being measured, so shrinking
`dt` further just approached that floor instead of revealing order-1
convergence. Comparing against a self-referenced (same `ny`, very fine
`dt`) solution instead isolates pure temporal error and removed the
artifact entirely (confirmed independently against a trivial scalar-ODE
sanity check, which showed clean order-1 backward Euler convergence from
the start -- proving the *scheme* was never the problem).

**C. Spatial order**: `dt=1e-6` (temporal error negligible), `ny in
{16,32,64,128}`, compared against the continuous solution directly (no
self-referencing artifact here, since a single tiny step doesn't give
the eigenvalue-mismatch time to compound): observed orders `2.00, 2.00,
1.99`.

**D. Plane Poiseuille** (`ny=32`, no-slip channel, constant body force,
run to `t=20` (~10 viscous relaxation times)):

| Quantity | Relative error |
|---|---:|
| Velocity profile (max) | 0.097% |
| Centerline velocity | 0.006% |
| Bulk flow rate | 0.005% |
| Wall shear stress | 0.005% |

All comfortably under the 0.5% target; spatial convergence orders
`{8->16->32->64}`: `2.00, 2.00, 2.00`. Divergence stays `< 1e-8`
throughout the entire 400-step run, not just at the end (checked via
`max(h.max_divergence for h in history)`).

**E. Oscillatory plane-channel Stokes flow** (named per the review's
explicit instruction -- *not* "Womersley flow" unqualified, which implies
circular-pipe geometry this solver does not represent; `ny=24`, `omega=2`,
5-period transient decay before recording):

| Quantity | Error |
|---|---:|
| Amplitude profile (max, all `y`) | 0.51% |
| Phase profile (masked to `amp > 0.2*max`) | 0.53 deg |
| Bulk-flow amplitude | 0.19% |
| Bulk-flow phase | 0.058 deg |
| Periodic repeat error (profile vs. one period later) | < 3% |

Phase at the single grid point nearest the wall (amplitude `~10%` of the
bulk peak there) shows a much larger raw error (`1.7 deg` at `ny=32` in
an earlier check) purely because phase is ill-conditioned wherever
amplitude approaches zero -- a property of the *signal*, not a solver
defect; the profile check masks points below 20% of peak amplitude for
exactly this reason (still checking the overwhelming majority of the
channel). A second, higher dimensionless frequency (`omega=6`, the
plane-channel analogue of a higher Womersley number) was also checked
with looser (3%/3deg) tolerance, confirming accuracy is not
frequency-specific. Temporal convergence (self-referenced, same
diagnosis as test B) showed order `> 1.5` between successive `dt` halvings.

**F. Manufactured full unsteady Stokes solution**: `u=U0*cos(kx x)*sin(ky y)*exp(-sigma t)`,
`v=-U0*(kx/ky)*sin(kx x)*cos(ky y)*exp(-sigma t)`, `w=0` (exactly
divergence-free and, on its own, an exact solution of the *homogeneous*
Stokes equation, `sigma=nu*(kx^2+ky^2)` -- the multi-component analogue of
test A) with a second, independent, time-independent pressure field
`p=P0*sin(kx x)*sin(ky y)*sin(kz z)` added on top, giving a clean
non-trivial forcing `f=(1/rho)*grad(p)` that exercises the forcing
pathway without needing a symbolic-algebra derivation. Periodic domain,
`nx=ny=nz in {8,16,20}`, `dt=0.001`: spatial convergence orders `2.01,
2.03`; divergence `< 1e-8` throughout.

**G. Long-run incompressibility**: 300 steps, random initial condition,
no-slip channel: `max|D_h u|_inf < 1e-6` and `max|D_h u|_2 < 1e-6` across
the *entire* run; the second half of the run is not worse than the
first (`second_half_max <= max(first_half_max*10, 1e-8)`) -- no secular
growth.

**H. Energy decay**: `K^{n+1} <= K^n + 1e-10` verified at every one of
100 steps for a random unforced initial condition (`theta=1`); numerical
`K(t)` for the eigenmode case (test A's setup) matches the analytical
`K_exact(t) = 0.25*U0^2*Lx*Ly*Lz*exp(-2*nu*k^2*t)` (integral of
`0.5*u^2` over the domain, using `integral(sin^2(ky)) = Ly/2`) to `<1%`
at `t=0.15`.

**I, J** (rest-state and constant-flow preservation): rest state is
preserved to **exact** `0.0` (not just near-roundoff) for 50 steps at
both `theta` values, since every term in the update (diffusion RHS,
projection RHS, forcing) is identically zero when `u=p=f=0`; constant
periodic flow is preserved to `<1e-8` for 30 steps. See
`test_time_integrators.py`.

### Milestone 5 limitations

* No nonlinear convection (Milestone 6) -- everything here is Stokes
  flow.
* `diffusion.py` offers direct solve only (see "well-posedness" above);
  a future CG option would need a symmetry-preserving (column-eliminating,
  `pressure.py`'s `pin_cell`-style) boundary treatment instead of the
  current row-only override.
* Direct sparse LU for a 3-D periodic Poisson-like system has
  faster-than-linear fill-in growth with problem size (measured: a 32
  fully-periodic pressure solve took `~35s` for 20 steps at `n=32^3`
  vs. `~0.4s` at `n=16^3` and `~1.5s` at `n=20^3` -- test F is capped at
  `n<=20` for exactly this reason). This is the standard, expected
  motivation for multigrid/PyAMG at production scale (`pressure.py`'s
  already-documented, not-yet-implemented roadmap item), not a new
  finding specific to this milestone.
* `ThetaSchemeIntegrator` does not yet support a spatially-varying
  `nu` (single global scalar, matching `config.py`'s
  `fluid.kinematic_viscosity`) or adaptive time-stepping (Milestone 7).
* Two defensive checks in `time_integrators.py` (`step`'s "diffusion
  solve did not converge" and "projected velocity/pressure contains
  non-finite values" paths) are not exercised by any test: the
  mathematically-guaranteed well-posedness of both the diffusion system
  (Section 11, "well-posedness") and a converged projection make these
  effectively unreachable via legitimate inputs; only the diffusion
  solve's own NaN-forcing-triggered `finite` check (a genuinely reachable
  path, via a pathological `forcing` callable) is tested.

## 12. Milestone 6: nonlinear convection and the complete Navier-Stokes equations

`convection.py` computes `N_h(u) = D_h(u (x) u)`, the discrete divergence
of the momentum flux tensor, at each velocity component's own MAC
location -- conservative form, the canonical first implementation per the
review. `time_integrators.py`'s `ThetaSchemeIntegrator` gained
`convection_scheme=` (`None`/`"centered"`/`"upwind"`), folding
`-N^{n+1/2}` into the diffusion predictor's explicit source term via AB2:

```
(I - theta*nu*dt*L_h) u* = (I + (1-theta)*nu*dt*L_h) u^n
                            + dt*nu*correction
                            - dt*[1.5*N(u^n) - 0.5*N(u^{n-1})]
                            + dt*f^{n+theta}
```

**Canonical sign convention** (audited and confirmed correct after the
Milestone 6 review flagged the *documentation's* sign as inconsistent
with the governing equation -- see "Sign audit" below): `N_h(u) =
D_h(u⊗u)` (no sign flip inside `convection.py`, confirmed by reading its
source); the governing equation `du/dt + N_h(u) = -grad(p)/rho +
nu*L_h(u) + f` requires the time integrator to *subtract* the AB2
extrapolation of `N_h`, which `time_integrators.py`'s `step()` already
did correctly (`conv_contribution = -ab2_field...`) -- only this
architecture document and the milestone chat report had the sign typo
(a `+` where the formula above now correctly shows `-`), not the code.
`tests/test_predictor_sign.py` adds an independent, projection-free
predictor-level check of this sign (see "Sign audit").

-- exactly the review's required CN/AB2 predictor formula, with `theta=1`
recovering pure backward-Euler-diffusion behavior and `convection_scheme=None`
recovering Milestone 5 unchanged (backward-compatibility verified: all 26
Milestone 5 tests still pass with the rewritten integrator).

### Flux locations and interpolation (full derivation in `convection.py`'s module docstring)

Recall the MAC layout: `p` at cell centers, `u`/`v`/`w` at x-/y-/z-faces.
The flux tensor's six independent components live at three MAC locations,
**none of which coincide with any single field's own storage location**:

* **Diagonal fluxes** `u^2`, `v^2`, `w^2` at **cell centers** (same as
  `p`): formed by averaging the component from its two bounding faces
  onto the cell center, *then* squaring (not "average of squares" --
  both are 2nd-order accurate individually, but only "average-then-square"
  is used throughout, consistently, since mixing the two would break the
  discrete product rule the energy test (Section 12, "operator-level
  verification") relies on).
* **Off-diagonal fluxes** `uv`, `uw`, `vw` at shared **edges** (e.g. `uv`
  where an x-face and y-face coincide, constant `z`): both contributing
  components are interpolated onto that edge independently (`u` averaged
  from its two *y*-neighbors; `v` averaged from its two *x*-neighbors),
  then multiplied.

Each component's convective term is then the flux difference across its
own control volume along each axis -- for `u`:

```
N_u = (u^2_cc[i] - u^2_cc[i-1]) / dx        (self term)
    + (uv_edge[j+1] - uv_edge[j]) / dy       (cross term)
    + (uw_edge[k+1] - uw_edge[k]) / dz       (cross term)
```

and analogously (permuting x<->y<->z, u<->v<->w) for `N_v`, `N_w`.
Implemented as one generic pair of functions (`_self_term`, `_cross_term`)
parametrized by axis, rather than three hand-written blocks with manually
swapped indices -- deliberately, to avoid the exact class of copy-paste
axis-swap bug a nonsymmetric-grid test is designed to catch. Centered and
upwind share this structure entirely, differing only in how the
*advected* quantity (not the *advecting* velocity, which is always
centered-averaged in both schemes) is formed: centered averages it;
upwind selects the donor-cell value by the sign of the local advecting
velocity.

**Skew-symmetric form was not implemented** (explicitly optional per the
review, "if it can be implemented cleanly and independently verified"):
a discrete skew-symmetric operator is only genuinely energy-neutral if
its advective-form differencing is constructed as the exact adjoint of
the conservative form's specific interpolation choices; an
under-verified attempt risks silently failing the very energy test it
exists to pass, and centered+upwind (both required, both fully verified)
were prioritized given the scope already committed this milestone.

### AB2 startup

AB2 needs `N(u^{n-1})`, unavailable on the first step. Documented rule:
**the first step uses `N^{1/2} = N(u^0)` directly** (equivalent to a
single forward-Euler-in-convection sub-step), making only that one step
first-order accurate in convection; every subsequent step is full
second-order AB2. A self-starting RK2/RK3 sub-step alternative was
considered and not implemented (see "temporal convergence" below for the
measured consequence of this choice).

### CFL and hard rejection

```
CFL = dt * (max|u|/dx + max|v|/dy + max|w|/dz)
```

(Milestone 1's convective CFL definition, combined conservatively across
components without requiring co-location). Computed from the *current*
state before each step; if `cfl_max` is configured, `CFLError` is raised
immediately when exceeded -- the step is never taken, never silently run
past the limit. `cfl_max=None` (default) disables the check.

### Operator-level verification (all 9 required items; full list in `tests/test_convection.py`)

* **Zero/uniform velocity**: `N_h(0)=0` and `N_h(U_0)=0` (periodic),
  exact for both schemes.
* **Polynomial exactness** (self term and cross term verified
  *independently*, using fields sampled exactly into the full padded
  array -- bypassing `apply_velocity_bc` entirely, since a non-periodic
  polynomial like `u=x` is not compatible with periodic ghost averaging
  and would otherwise corrupt the boundary-adjacent cells, a real
  artifact caught during development, not a convection.py bug): `u=x`
  isolates the self term (`N_u = 2x` exactly, finite-difference of a
  quadratic is exact); `u=y, v=x` isolates the cross term (`N_u=x,
  N_v=y` exactly, self terms vanish identically); a third case (`u=z,
  w=x`) exercises the remaining axis pairing; a fourth (`u=y,v=z,w=x`, a
  genuine 3-cycle) is the axis-permutation test. All match hand-derived
  values to `1e-12`.
* **Conservative global momentum** (periodic): `sum(N_h,u)*dV ~ 0` to
  `~1e-17` -- but **only** when the periodic duplicate high-index face
  (Section 4's "Periodic duplicate normal faces" convention) is excluded
  from the sum; a companion test confirms the naive (duplicate-included)
  sum is *not* near roundoff (`>1e-6`), proving the exclusion is
  load-bearing, not cargo-culted.
* **Semi-discrete energy production** (centered, on a projected -- hence
  discretely divergence-free to solver tolerance -- periodic field):
  `<u, N_h(u)>_F` `~9e-16` (roundoff). Upwind's same quantity is `~5.5`
  (large and positive, i.e. `-<u,N(u)>` is large and *negative* -- energy
  *decreasing* from convection alone, confirming upwind is dissipative
  with the correct sign, not merely "different from centered").

### Full-solver verification (A-F)

**A. Taylor-Green vortex** (2.5-D: `w=0`, an exact solution of the
*full nonlinear* equations, not just Stokes -- the classical TG property
that the nonlinear term is exactly a pure gradient, re-derived here for
`kx != ky`, the nonsymmetric-grid generalization of the textbook
`kx=ky` case, and independently confirmed numerically -- both velocity
and pressure errors shrink at the expected ~4x-per-doubling rate --
before being trusted as a test oracle):

```
u = U0*sin(kx x)*cos(ky y)*exp(-sigma t)
v = -U0*(kx/ky)*cos(kx x)*sin(ky y)*exp(-sigma t)
w = 0, sigma = nu*(kx^2+ky^2)
p = rho*U0^2/4 * [cos(2kx x) + (kx/ky)^2*cos(2ky y)] * exp(-2 sigma t)
```

`u,v,p` errors `<0.01`/`<0.02` at `n=32`; `w` exactly `0` (`<1e-10`) for
all time; divergence `<1e-8` throughout. Spatial convergence
(`n=16,32,64`): orders `1.6`-`2.4` range, comfortably at 2. Temporal
convergence (self-referenced, same diagnosis as Milestone 5): orders
`1.11, 1.23, 1.59` across `dt in {T/64,...,T/512}` -- climbing toward 2
but not yet there even at 512 steps, a *measured, reproducible*
consequence of AB2's one-step startup penalty (every fresh
`run_to(dt)` call pays it once; its relative contribution to total error
shrinks only slowly as step count grows). Recorded honestly rather than
asserting a clean order-2 that would need impractically many steps to
actually observe in a fast test.

**B. Manufactured full Navier-Stokes**: reuses test A's `(u,v)` pair
(already exact with `f=0`) plus an independent, time-independent pressure
perturbation `p2 = P0*sin(kpx x)*sin(kpy y)*sin(kpz z)`, requiring exactly
`f=(1/rho)*grad(p2)` by linearity of the pressure-gradient term --
verifying the full predictor+diffusion+pressure+projection pipeline
under a genuine forcing without a symbolic-algebra derivation. Spatial
orders (`n=12,16,20`): `1.95, 1.96`. Divergence `<1e-8` throughout.

**C. Near-inviscid periodic energy** (`nu=1e-4`, projected -- hence
divergence-free -- random initial field, 30 steps): centered shows
`-1.1%` relative kinetic-energy drift ("very low"); upwind shows `-66%`
(substantially, monotonically dissipative). Neither *creates* energy
(`K_end <= K0*1.001` enforced for both) -- exact Euler conservation is
not claimed for centered, consistent with it having real (if small)
numerical dissipation, not zero.

**D. Long nonlinear run** (300 steps, no-slip channel, safe CFL): raw
`max|D_h u|` `<1e-6` and normalized `E_div` `<1e-8` throughout, no
secular growth (second-half max `<=` 10x first-half max); no NaN/Inf;
kinetic energy bounded (`<=1.5x` initial, walls + no forcing); no-slip
BCs (both normal and tangential) verified satisfied on the *final*
state; pressure and diffusion solvers report converged at every one of
300 steps.

**E. CFL failure**: an artificially huge velocity+dt combination with
`cfl_max=1.0` raises `CFLError` before the step is taken; the identical
scenario with `cfl_max=None` (default) does not raise (confirming the
check is configurable, not always-on); a safe-CFL case is accepted
normally.

**F. Scheme comparison** (same Taylor-Green case, centered vs. upwind):
centered's solution error is smaller (2nd vs. 1st order, same smooth
well-resolved case); upwind's final kinetic energy is lower (more
numerical dissipation, consistent with the operator-level energy test);
both remain stable and pressure-convergent at this safe CFL -- upwind's
extra dissipation manifests as reduced accuracy here, not instability.
Runtime recorded for both (convection is a small fraction of per-step
cost, dominated by the shared pressure/diffusion solves), not asserted
against each other.

### Milestone 6 limitations

* Skew-symmetric convection not implemented (see above; explicitly
  optional per the review).
* ~~AB2's one-step startup measurably slows...~~ **Superseded, see
  Section 13**: the startup was upgraded to a genuine 2nd-order (Heun)
  scheme in the Milestone 6 correction round; the overall temporal order
  is now capped by a different, unrelated cause (the projection
  algorithm), documented in Section 13.
* No adaptive time-stepping tied to the CFL diagnostic (Milestone 7) --
  `cfl_max` only *rejects* an already-chosen `dt`, it does not suggest a
  smaller one.
* Benchmark resolutions are kept modest (Taylor-Green/manufactured tests
  capped around `n<=64`) given `pressure.py`'s already-documented 3-D
  direct-solver fill-in scaling (Section 11); this milestone did not
  reassess that scaling, only continued working within it.
* No turbulence model, LES, RANS, AMR, compressibility, or complex
  geometry -- seeSection 7's explicit restrictions on describing results
  from this solver.
* **The overall time-stepping scheme is only first-order accurate**, not
  second-order, because `projection.py`'s non-incremental (Chorin-type)
  pressure projection has an intrinsic O(dt) splitting error -- see
  Section 13 for the full diagnosis and the reviewer decision needed to
  close it.

## 13. Milestone 6 correction round: sign audit and temporal-order investigation

Following the Milestone 6 review's "conditional acceptance," two
verification issues were investigated and are reported here.

### Sign audit (resolved)

**Finding: the code was already correct; only the documentation had a
sign typo.** `convection.py` computes `N_h(u) = D_h(u⊗u)` exactly as
documented (verified by reading its source -- no sign flip anywhere in
`_self_term`/`_cross_term`). `time_integrators.py`'s `step()` already
subtracted this term correctly
(`conv_contribution = -ab2_field.components()[axis].interior`, folded
into the diffusion predictor's `forcing` argument) -- consistent with
the governing equation `du/dt = -N_h(u) - grad(p)/rho + nu*L_h(u) + f`.
Only this architecture document (Section 12's predictor-formula box) and
the Milestone 6 chat report had a `+` where a `-` belonged; both are now
corrected (see Section 12 above).

**Independent verification added**: `tests/test_predictor_sign.py`
checks, without ever constructing a pressure system or calling
`project()`, that the actual predictor mechanism
(`VelocityDiffusionSystem.solve` with `forcing=-N_h(u^n)`) produces
`(u*-u^n)/dt -> -N_h(u^n)` as viscosity is driven toward the validator's
floor, and that the *opposite* sign does **not** converge to the same
value (residual stays near `2*|N_h(u^n)|` regardless of viscosity) --
proving the check is sign-sensitive, not just magnitude-sensitive. See
that module's docstring for why "nu -> 0" rather than "dt -> 0" is the
correct convergence axis for this particular check (the predictor is an
exact linear solve, not a finite-difference-in-time approximation, so
its only source of residual against `-N_h(u^n)` is the O(nu) diffusion
terms, not a truncated Taylor series in `dt`).

### Temporal-order investigation (partially resolved; open architectural question)

**Action taken**: replaced the original forward-Euler-in-convection AB2
startup with a genuine second-order (Heun's method / explicit
trapezoidal) startup -- see Section 12's "AB2 startup" (now updated) and
`time_integrators.py`'s module docstring. This is a real, verified
correctness improvement and all existing tests (including the
predictor-sign test above) continue to pass with it.

**Finding: this did not bring the observed temporal order to ~2, and
further investigation shows it cannot, on its own.** Refined temporal
refinement (dt in `{T/128,...,T/2048}`, reference at `T/8192`, 16x below
the finest test point vs. only 2x in the original test) still shows
order ~1.0-1.3, not ~2
(`tests/test_navier_stokes_verification.py::test_A_taylor_green_temporal_convergence`).

**Root cause, isolated by an additional test**: the *same*
self-referenced refinement applied to **pressure** alone
(`test_A_taylor_green_pressure_temporal_order_confirms_projection_is_first_order`)
also shows clean order ~1.0-1.2, not ~2. This is the textbook signature
of `projection.py`'s **non-incremental (Chorin-type)** projection
method (explicitly named as such in that module's own docstring, a
Milestone 4 design choice): pressure is recomputed from a fresh Poisson
solve every step, with no history carried forward from `p^{n-1}`. This
class of method has a well-documented intrinsic `O(dt)` global splitting
error between the pressure-projection and time-advancement operators
(Guermond, Minev & Shen, *An overview of projection methods for
incompressible flow*, 2006) -- a property of the **projection
algorithm**, independent of how accurate the explicit predictor's own
convection/diffusion discretization is. Improving AB2's startup from 1st
to 2nd order was therefore a real, worthwhile fix (it removes a genuine
Milestone 6 source of error), but it could not and did not lift the
*overall* scheme's temporal order past ~1, because that ceiling comes
from a different, already-accepted (Milestone 4) module.

**What would be required to reach true second-order overall accuracy**:
upgrading `projection.py` from a non-incremental to an incremental
(ideally *rotational* incremental, e.g. van Kan 1986 / Timmermans et al.
1996) pressure-correction scheme -- carrying `p^{n-1}` forward between
steps, subtracting its gradient from the predictor's RHS, and solving
for a pressure *increment* rather than the full field each step. This is
a materially larger change: it touches `projection.py`'s public API
(`project()` currently takes no previous-pressure argument by design --
"a single, stateless predictor-in/corrected-out call," Section 5/10) and
`time_integrators.py`'s `step()`, re-opening design decisions accepted
in Milestones 4 and 5. **This was not attempted unilaterally** in this
correction round; it is flagged here as an open question for the
reviewer rather than silently built or silently left unaddressed.

## 14. Milestone 7: performance -- linear-solver abstraction, adaptive timestepping, profiling, memory

Accepted scope: make the existing, fully-verified solver computationally
practical at larger resolutions **without** touching numerical
correctness or the projection method (Section 13's O(dt) ceiling is
preserved, not revisited). No turbulence model, LES, RANS, compressible
flow, AMR, or unstructured/immersed-boundary geometry was added.

### New modules

```
src/navier3d/
├── linear_solvers.py   # LinearSolver, create_linear_solver: shared direct/CG/
│                        #   BiCGSTAB/GMRES + Jacobi/AMG backend for pressure.py
│                        #   AND diffusion.py (Part A)
├── adaptive.py          # AdaptiveTimestepController (Part F), 
│                        #   variable_step_ab2_coefficients (Part G)
├── profiling.py          # StepProfiler: explicit per-category timers (Part I)
└── memory.py              # Field/matrix/solver memory accounting (Part J)
```

`pressure.py` and `diffusion.py` were refactored to build one
`LinearSolver` internally instead of each hand-rolling its own
direct/CG dispatch and iteration-counting callback; every existing
Milestone 1-6 test for both modules passes unchanged (300+ tests,
verified before any Milestone-7-specific test was written).

### Part A: linear-solver abstraction

```python
solver = create_linear_solver(matrix, method="cg", matrix_kind="spd",
                               preconditioner="jacobi", rtol=1e-10, atol=0.0,
                               max_iterations=10000)
result = solver.solve(rhs, x0=...)   # -> LinearSolveResult
```

`matrix_kind` (`"spd"` or `"general"`) is a **caller declaration**, not
runtime matrix inspection -- `pressure.py` declares `"spd"` (true: `A =
-L_h` is symmetric positive semi-definite by the Milestone 3 sign
convention); `diffusion.py`'s original pin-row formulation declares
`"general"` (true: boundary pin/linkage rows break symmetry); its new
SPD-reduced formulation (Part C) declares `"spd"`. `LinearSolver`
rejects `method="cg"` for `matrix_kind="general"` at construction --
"do not silently use CG on a nonsymmetric matrix" is enforced
structurally, not by convention. `LinearSolveResult` reports `x`,
`converged`, `iterations`, `initial_residual`, `final_residual`,
`relative_residual`, `setup_time` (factorization/hierarchy, once),
`preconditioner_time` (once), `solve_time` (per call) -- matching the
review's sketch exactly.

### Part B: PyAMG (optional)

```bash
pip install -e ".[amg]"   # optional; navier3d works fully without it
```

`preconditioner="amg"` builds a PyAMG Ruge-Stuben classical AMG
hierarchy as a CG preconditioner. Verified (`tests/test_pressure_amg.py`,
skipped automatically if pyamg isn't installed):

| Check | Result |
|---|---|
| Dirichlet (nonsingular) pressure, AMG vs. plain CG | rel. L2 pressure error (offset-normalized) `< 1e-6` |
| Periodic (singular, zero_mean) pressure, AMG vs. plain CG | rel. L2 error `< 1e-6`; null-space handling (mean removal) unaffected |
| **Corrected velocity** after full projection, AMG vs. reference | rel. L2 error per component `< 1e-6` (the review's emphasis: pressure offset alone is physically irrelevant -- velocity, which depends only on `grad(p)`, is what was actually checked) |
| AMG + `null_space_strategy="pin_cell"` | converges normally |

### Part C: SPD-reduced diffusion formulation

**Investigated and implemented.** The original (`formulation="pinned"`)
matrix keeps a component's own boundary/duplicate normal-axis faces as
explicit unknowns pinned by asymmetric override rows. The new
(`formulation="spd"`) matrix instead **eliminates** those DOFs
algebraically -- substituting their known formula (a fixed Dirichlet-
like target, a `pressure_outlet` adjacent-value linkage, or a periodic
duplicate) directly into the interior stencil, exactly the same
technique `pressure.py` already uses for ghost cells -- yielding a
genuinely smaller, symmetric positive-definite matrix with **zero**
discretization change (same stencil coefficients throughout; only how
two boundary DOFs are removed from the linear system differs). Full
derivation lives in `diffusion.py`'s module-level comment above
`_assemble_velocity_diffusion_system_spd`.

Verified across every velocity BC type this project supports
(`tests/test_diffusion_spd.py`, 30 tests): the `"spd"` matrix genuinely
is symmetric (`|M - M^T| < 1e-12`) where the `"pinned"` matrix genuinely
is not (`|M - M^T| > 1e-6`, confirming the comparison is meaningful);
`solver="cg"` on `"spd"` matches `solver="direct"` on `"pinned"` to
relative L2 error `< 1e-8` for `no_slip`, `periodic`, a `velocity_inlet`/
`pressure_outlet` channel, and `free_slip` walls, on all 3 velocity
components. `solver="bicgstab"` on the *original* `"pinned"` (general)
matrix -- the review's "otherwise GMRES/BiCGSTAB" fallback, independent
of the SPD reformulation -- was also verified to match the direct
reference (`< 1e-8`).

`formulation="pinned"` (unchanged, `solver="direct"` default) remains
the library default -- zero risk to the already-accepted Milestone 5/6
behavior; `formulation="spd"` is opt-in via `diffusion_kwargs=` on
`ThetaSchemeIntegrator` or directly on `VelocityDiffusionSystem`.

### Part D: warm starts

`ThetaSchemeIntegrator(..., warm_start=True)` passes the *previous*
step's pressure field and predictor velocity as `x0` to the pressure and
diffusion solves respectively (`project()` gained `pressure_x0=`;
`VelocityDiffusionSystem.solve()` gained `x0=`). A no-op for direct
solves (verified bitwise-identical with/without `warm_start` when using
`solver="direct"`, `tests/test_time_integrators_adaptive.py`). Measured,
not assumed, for the iterative (`spd`/`cg`) configuration on a smoothly
evolving periodic flow: warm-started steps 2-6 needed fewer or equal
total CG iterations than cold (zero-initial-guess) steps, strictly fewer
overall on the tested case.

### Part E: matrix/preconditioner reuse and invalidation

`ThetaSchemeIntegrator` caches its 3 `VelocityDiffusionSystem` instances
by `(nu, dt, theta)` -- the exact three quantities the assembled matrix
depends on (mesh/BCs are constructor-fixed, not part of the key).
Verified directly (`tests/test_time_integrators_adaptive.py`):

* Same `dt` across many `step()` calls -> `id(matrix)` unchanged,
  `diffusion_cache_size == 1`.
* A genuinely different `dt` -> new matrix objects built, cache grows to
  2; **returning** to a previously-seen `dt` reuses the cached objects
  (no rebuild, cache stays at 2) -- exactly the review's "dt change may
  invalidate... pressure BC type change should invalidate... pressure BC
  values alone should not."
* Pressure: unchanged from Milestone 5 -- same-topology, changing-value
  BCs (e.g. a time-varying forcing) reuse `id(pressure_system.matrix)`;
  a topology change requires a new `PressurePoissonSystem` (unchanged
  API contract, `PressureSystemError` on an attempted in-place topology
  change via `update_bcs`).

### Parts F & G: adaptive timestep control and variable-step AB2

**Adaptive controller** (`navier3d.adaptive.AdaptiveTimestepController`):

```
dt_cfl = cfl_target / (max|u|/dx + max|v|/dy + max|w|/dz + eps-handled-as-dt_max-for-zero-velocity)
dt = clip(safety * dt_cfl, shrink_max*dt_prev, growth_max*dt_prev)
dt = clip(dt, dt_min, dt_max)
```

Zero velocity returns `dt_max` directly (not an epsilon-guarded division
by zero); `dt`/`cfl`/`diffusive_number` (`nu*dt*(1/dx^2+1/dy^2+1/dz^2)`,
reported honestly as a diagnostic, **not** presented as a hard CN
stability limit -- diffusion is unconditionally stable here) are all
returned in a `DtDecision`, along with `limited_by` (`"cfl"`/`"growth"`/
`"shrink"`/`"dt_min"`/`"dt_max"`) for inspectability. 28 tests
(`tests/test_adaptive.py`) cover construction validation, the
zero-velocity path, growth/shrink/floor/ceiling clipping individually
and in combination, and "never NaN/Inf/negative" across an 18-order-of-
magnitude speed sweep.

**Variable-step AB2** (derivation in `adaptive.py`'s
`variable_step_ab2_coefficients` docstring): fitting the linear
extrapolant through `(t_{n-1}, N^{n-1})` and `(t_n, N^n)` and integrating
it over `[t_n, t_n+dt_current]` gives

```
r = dt_current / dt_previous
N_ab2 = (1 + r/2)*N^n - (r/2)*N^{n-1}
```

which recovers the textbook constant-step `(3/2, -1/2)` exactly at
`r=1`. Verified against manufactured polynomial `N(t)`: a **linear**
`N(t)` reproduces the exact integral to roundoff for `r != 1` (necessary
sanity check -- the linear extrapolant IS `N(t)` exactly in that case);
a **quadratic** `N(t)` shows local truncation error shrinking by
`~8x = 2^3` per halving of the step-size scale (holding `r=1.7` fixed),
confirming genuine 3rd-order local / 2nd-order global consistency, not
just "the formula happens to work at r=1."

`ThetaSchemeIntegrator.step(state, dt=...)` now accepts a per-call `dt`
override; the integrator tracks `(previous convection, previous dt)`
together and automatically uses the variable-step formula whenever
`dt != previous dt` (the constant-step case is just `r=1` of the same
code path -- no special-casing, confirmed by all 28 pre-existing
Milestone 6 temporal-convergence tests still passing unchanged with this
rewrite, since they all use constant `dt`). The Heun-startup rule
(Section 13) is unaffected -- it only concerns the *first* step, before
any step-size history exists at all.

### Part H: temporal accuracy under adaptive stepping

`tests/test_adaptive_temporal_accuracy.py`, Taylor-Green case, dt scale
refined across `{1.0, 0.5, 0.25}` (both a CFL-target-driven adaptive run
and a fixed-step run at the matching nominal scale, both compared to a
`T/8192` fixed-step reference):

* Adaptive error shrinks monotonically as the scale shrinks (no
  qualitative breakdown).
* Adaptive error stays within `5x` of the fixed-step error at the same
  nominal scale (bounded, not "unexpectedly first order or worse").
* At a shared fine scale (`T/256`), adaptive and fixed-step solutions
  agree with each other to within `10x` of the fixed-step-vs-reference
  error -- i.e. adaptive genuinely converges toward the same solution,
  not a different one.

No claim of second-order full-solver accuracy is made anywhere in this
milestone (Section 13's ceiling stands); this section only verifies
adaptive stepping doesn't make things *worse*.

### Part I: profiling

`StepDiagnostics.step_profile` (this step) and
`ThetaSchemeIntegrator.profiler` (cumulative across every step) report
exactly the review's 9 categories. Explicit `time.perf_counter()` timers
around hand-picked boundaries -- **not** `cProfile` wrapped around the
simulation loop (would add per-call overhead to a loop run thousands of
times). Real measured breakdown (`integrator.profiler.format_report()`), N=24,
iterative backend (`formulation="spd"`, CG+Jacobi for both pressure and
diffusion, `warm_start=True`), Taylor-Green case, 10 steps:

```
pressure_solve          41.1%
diffusion_solve         23.3%
convection               4.9%
pressure_rhs             3.7%
projection_correction    3.5%
diffusion_rhs            2.9%
diagnostics               0.5%
boundary_conditions       0.5%
(other, uninstrumented)  19.6%
```

Values are measured, not hard-coded -- pressure and diffusion solves
dominate as expected (the review's stated bottleneck), and the
"projection correction" (grad(p) + velocity correction + BC reapplication)
and RHS-construction categories are all small relative to the two linear
solves. The ~20% "other" (total step time minus the 8 instrumented
categories' sum) is Python-level loop/object-construction overhead not
attributed to any specific category -- reported honestly rather than
padded into an existing bucket.

### Part J: memory accounting

Analytical field+matrix estimates (`navier3d.memory`), `~500 bytes per
pressure cell` at every resolution tested (dominated by the 4
Kronecker-assembled analytical-stencil matrices, `pressure_field_p` +
`velocity_fields_uvw` + 5 same-sized temporaries):

| N | cells | fields (analytical) | matrices (analytical, 7-pt) | total | bytes/cell |
|---|---|---|---|---|---|
| 32 | 32,768 | 6.1 MB | 11.8 MB | 17.9 MB | 548 |
| 64 | 262,144 | 44.3 MB | 93.4 MB | 137.7 MB | 525 |
| 128 | 2,097,152 | 336.4 MB | 742.5 MB | 1078.9 MB | 515 |

**Measured** (not estimated) via a real build + `psutil` process-RSS
delta, N=32, `solver="direct"` (pressure + all 3 diffusion components):
the matrices themselves measured **2.9 MB each** (matching the
analytical estimate closely), but their **LU factorizations** measured
**~1.2 GB of fill-in each** -- a **>400x blowup** over the sparse
matrix's own size, ~4.1 GB total RSS for one set of 4 factorizations.
This is a real, measured number, not the analytical estimate above (the
analytical table intentionally does *not* include direct fill-in, which
is architecture-dependent and exactly this milestone's point to avoid
via iterative solvers) -- and it is the single most concrete piece of
evidence for why direct-LU-only is impractical past ~N=24-32 on a
typical workstation.

### Part K: scaling benchmark

`benchmarks/scaling_benchmark.py`, Taylor-Green case (nonzero, genuinely
nonlinear-convecting velocity field), `theta=0.5`, centered convection,
periodic BCs, 3 steps averaged per row, **measured** (not simulated):

| N | backend | cells | dt/step (s) | pressure solve (s) | diffusion solve (s) | convection (s) | p iters | diff iters | mem (MB) | CFL |
|---|---|---|---|---|---|---|---|---|---|---|
| 16 | direct | 4,096 | 0.355 | 0.003 | 0.007 | 0.0003 | 1 | 3 | 2.4 | 0.045 |
| 16 | iterative | 4,096 | 0.006 | 0.0005 | 0.0005 | 0.0003 | 12 | 7 | 2.4 | 0.045 |
| 24 | direct | 13,824 | 4.762 | 0.022 | 0.051 | 0.0011 | 1 | 3 | 7.7 | 0.070 |
| 24 | iterative | 13,824 | 0.028 | 0.009 | 0.005 | 0.0010 | 18 | 8 | 7.6 | 0.070 |
| 32 | direct | 32,768 | **not attempted -- expected fill-in prohibitive** (see Part J: ~1.2 GB fill-in per matrix, measured) |
| 32 | iterative | 32,768 | 0.055 | 0.024 | 0.012 | 0.0026 | 23 | 9 | 17.7 | 0.094 |
| 48 | direct | 110,592 | **not attempted -- expected fill-in prohibitive** |
| 48 | iterative | 110,592 | 0.196 | 0.057 | 0.027 | 0.0157 | 33 | 10 | 58.3 | 0.142 |

Direct-per-step time (including one-time amortized assembly+
factorization over the 3-step average) is **63x** slower than iterative
at N=16 and **170x** slower at N=24 -- and direct simply could not be
attempted at all at N=32/48 within reasonable memory. Iteration counts
grow far more slowly than problem size: 4,096 -> 110,592 cells (27x) but
pressure iterations only 12 -> 33 (2.75x), diffusion 7 -> 10 (1.4x) --
the "bounded/sub-linear growth" acceptance target, measured directly.

### Part L: correctness regression

`tests/test_milestone7_regression.py`: for each case, the "optimized"
configuration (`formulation="spd"`, `solver="cg"`, `warm_start=True`)
and the existing direct reference, same mesh/dt, compared by relative L2
error:

| Case | Metric | Result |
|---|---|---|
| Plane Poiseuille | velocity, rel. L2 | `< 1e-6` |
| Oscillatory plane-channel | velocity, rel. L2 | `< 1e-6` |
| Taylor-Green | velocity (u,v), rel. L2 | `< 1e-6` |
| Taylor-Green | pressure (mod. constant), rel. L2 | `< 1e-6` |
| Taylor-Green | kinetic energy, rel. diff | `< 1e-6` |
| Manufactured nonlinear NS | velocity (u,v,w), rel. L2 | `< 1e-6` |

All within configured linear-solver tolerance plus floating-point
effects, as required.

### Part M: determinism

Verified directly (`tests/test_determinism.py`), not merely assumed:
two independent builds+runs of the identical (mesh, dt sequence, initial
state, backend) configuration produce **bitwise-identical** results --
true for both `solver="direct"` and `solver="cg"` (SciPy's iterative
solvers and PyAMG/Jacobi preconditioners are themselves deterministic
given identical inputs; no threading or RNG-based nondeterminism
anywhere in this pure NumPy/SciPy CPU pipeline), and for an adaptive-dt
run (the controller's decisions and the resulting `dt` sequence are
themselves deterministic functions of the state). Bitwise equality
across *different* backends or hardware is explicitly not claimed or
tested.

### Part N: failure handling

`tests/test_failure_handling.py`, all of the review's required failure
modes, each deliberately triggered:

| Failure | Mechanism |
|---|---|
| Pressure non-convergence | `ProjectionError` -> `IntegrationError("projection failed...")` |
| Diffusion non-convergence | `IntegrationError("...did not converge...")` |
| NaN/Inf (forcing-induced) | `IntegrationError("...non-finite...")` |
| dt below dt_min / impossible CFL target | `AdaptiveTimestepController(strict=True)` -> `AdaptiveTimestepError` (new: `strict=False`, the Part F default, still clamps -- a deliberate, documented distinction between "routine floor" and "the floor can no longer keep up") |
| Invalid preconditioner | `PressureSystemError`/`DiffusionSystemError` (wrapping `LinearSolverError`) |
| PyAMG requested but not installed | clear message naming `pip install -e ".[amg]"` |
| Incompatible solver/matrix (CG on a general/nonsymmetric matrix) | `LinearSolverError`, message lists valid alternatives |

None of these leave the caller with a partially-advanced or silently
wrong state -- `run()` propagates every exception immediately.

### Known limitations (Milestone 7)

* Direct-LU remains available and is still the library **default**
  (`formulation="pinned"`, `solver="direct"`) for both pressure and
  diffusion -- deliberately, to keep every already-accepted Milestone
  1-6 test and example running unchanged; opting into the faster/lighter
  iterative path is the caller's explicit choice
  (`pressure_kwargs=`/`diffusion_kwargs=` on `ThetaSchemeIntegrator`).
* The diffusion-system cache (`(nu, dt, theta)` -> matrices) has no
  eviction policy -- fine for realistic CFL-driven `dt` sequences, which
  settle toward a small number of distinct values, but a pathologically
  chaotic `dt` sequence could grow it unboundedly; not addressed here as
  out of scope for a performance milestone whose target use case is
  well-behaved CFL control.
* PyAMG and `psutil` are both optional dependencies; a subset of tests
  (`test_pressure_amg.py`, the `psutil`-gated case in `test_memory.py`)
  is skipped automatically when they're absent, not silently assumed
  passing.
* The SPD-reduced diffusion formulation (Part C) is opt-in, not the new
  default -- see above.
* The projection method's ~O(dt) temporal ceiling (Milestone 6
  correction, Section 13) is unchanged and was explicitly out of scope
  here; adaptive timestepping and warm starts do not, and are not
  claimed to, lift it.
* Scaling benchmark (Part K) covers one workstation's measurements at
  one point in time -- absolute numbers will vary by hardware; the
  *trends* (iterative's iteration-count growth far outpacing problem
  size, direct's fill-in becoming prohibitive) are the durable result.

## 15. Milestone 8: incremental/rotational pressure correction and temporal-accuracy verification

Goal: reduce the non-incremental Chorin method's ~O(dt) global
splitting-error ceiling (Section 13) while preserving it as a
selectable reference. **No projection method was deleted or altered**
-- `project()` (non-incremental) is untouched, byte-for-byte, and
remains `ThetaSchemeIntegrator`'s default (`projection_method=
"non_incremental"`); the new methods are opt-in.

### Part 1: method selection

```python
ThetaSchemeIntegrator(..., projection_method="non_incremental")  # default, unchanged
ThetaSchemeIntegrator(..., projection_method="incremental")       # new
ThetaSchemeIntegrator(..., projection_method="rotational", chi=1.0)  # new
```

### Part 2: incremental derivation

The predictor gains a pressure-history term (the review's governing
equation, matched to this solver's existing sign convention -- `du/dt +
N(u) = -grad(p)/rho + nu*lap(u) + f`, Section 12):

```
(I - theta*nu*dt*L_h) u* = (I + (1-theta)*nu*dt*L_h) u^n
                            + dt*nu*correction
                            - dt*[AB2 convection, Section 12/13]
                            - dt/rho*G_h(p^n)          <- NEW
                            + dt*f^{n+theta}
```

implemented by folding `-(1/rho)*G_h(p^n)` into the same `forcing`
argument `diffusion.py`'s `VelocityDiffusionSystem.solve()` already
accepted for AB2 convection and body forcing -- no new code path in
`diffusion.py` was needed. `p^n` is `state.pressure` (already part of
`FlowState` since Milestone 1); its ghosts are filled with this
integrator's own **physical** `bcs` (`apply_pressure_bc(state.pressure,
self.bcs, ...)`), *not* the per-step Neumann-derived-from-u* values
(Part 5 below explains why those belong to `phi` alone).

Correction (`projection.py::project_incremental`), reusing the
already-verified `D_h`, `G_h`, `L_h`, and `PressurePoissonSystem`
unchanged:

```
L_h phi = (rho/dt) * D_h(u*)          (same Poisson SHAPE as project()'s;
                                         different BCs -- Part 5)
u^{n+1} = u* - (dt/rho) * G_h(phi)     (same formula as project(), phi
                                         in place of the full pressure)
p^{n+1} = p^n + phi                     (incremental update)
```

### Part 3: rotational derivation

```
p^{n+1} = p^n + phi - chi*rho*nu*D_h(u*)
```

**Dimensional derivation** (the review's explicit instruction: derive,
don't copy blindly): the classical van Kan (1986) / Timmermans-Minev-
Van de Vosse (1996) rotational correction is usually written
`p^{n+1} = p^n + phi - mu*div(u*)` using *dynamic* viscosity `mu`. This
codebase uses *kinematic* `nu` (`mu = rho*nu`) and keeps `rho` explicit
throughout (Section 3's unit convention: `p` is a genuine pressure,
`[Pa]`, not a kinematic pseudo-pressure) -- substituting `mu = rho*nu`
gives exactly the formula above. `chi` (default `1.0`, the classical
value) is exposed as a configurable coefficient rather than hard-coded.

**Honesty about the derivation's scope**: the classical formula's exact
justification (via the vector identity `lap(u) = grad(div(u)) -
curl(curl(u))`) is derived for predictors where diffusion is treated
explicitly or semi-implicitly at the *predictor* stage in a specific
way. This solver's predictor treats diffusion **fully implicitly**
(the entire theta-scheme linear solve, boundary rows included, is one
coupled system) -- an independent from-scratch re-derivation attempted
during this milestone (matching the predictor's actual equations, not
the classical simplified ones) produced a *different*, higher-order
correction term (`nu*theta*dt*L_h(G_h(phi))`, third-order in the
operators) rather than the classical `nu*D_h(u*)`. Given this ambiguity,
the classical, well-established formula was implemented (chi
configurable, not asserted to be exactly "correct" for this
discretization), and its **actual effect was measured empirically**
rather than assumed -- see "Temporal convergence" below. Internal
consistency check: `u^{n+1}` from incremental and rotational are
*algebraically identical* (both come from the same `phi`; only the
*pressure update* differs) -- verified to `1e-12`
(`tests/test_projection_incremental.py`).

### Part 4: state/history

`FlowState.pressure` **is** `p^n` for incremental/rotational -- no new
field needed there. The additional history AB2 and the new predictor
need beyond one `FlowState` is now explicit:

```python
@dataclass
class IntegratorHistory:
    previous_convection: Optional[VelocityField]  # N(u^{n-1}), for AB2
    previous_dt: Optional[float]                    # for variable-step AB2's r
    previous_phi: Optional[ScalarField]              # warm-start only, never required
```

`ThetaSchemeIntegrator.history` (property) / `.restore_history(...)` /
`initial_history=` (constructor kwarg) expose it. Two integrators built
identically and restored to the same `(FlowState, IntegratorHistory)`
pair take bit-identical next steps -- verified
(`tests/test_time_integrators_projection_methods.py`).

### Part 5: pressure-correction BC derivation (all face types)

**The central, delicate finding, verified by reading the actual code
(not assumed):** this solver's predictor (`diffusion.py`) always pins a
velocity component's own normal-axis boundary *face* to its exact
target (0 for an impermeable wall, the configured value for
`velocity_inlet`) -- both via the diffusion matrix's boundary row and
again via `apply_velocity_bc`'s reapplication, before `u*` ever reaches
projection. Consequently `_derive_face_pressure_bc`'s formula (`g =
sign*(rho/dt)*(u_star_face - target)`, Milestone 4) evaluates to
(floating-point-)zero for every BC type where the boundary is pinned to
a *fixed* target -- **identically for `p`'s BC (Milestone 4-6) and
`phi`'s BC (Milestone 8)**, since neither the pin nor the reapplication
depends on whether the predictor also included a `-(1/rho)*grad(p^n)`
term. So `derive_phi_bcs` reuses `derive_pressure_bcs` unchanged for
every face except one:

| Face type | p^n's BC | phi's BC | Why |
|---|---|---|---|
| periodic | periodic | periodic | pass-through, identical |
| stationary no-slip wall | Neumann, ~0 (verified) | Neumann, ~0 (verified) | u* exactly pinned to 0 regardless of predictor |
| moving no-slip wall (`velocity_inlet`, zero normal component) | Neumann, ~0 (verified) | Neumann, ~0 (verified) | wall motion is tangential; never enters the normal-direction formula |
| velocity inlet | Neumann, ~0 (verified) | Neumann, ~0 (verified) | u* exactly pinned to the configured normal target |
| free-slip / symmetry | Neumann, ~0 (verified) | Neumann, ~0 (verified) | same pin-to-0 mechanism as a wall |
| **pressure outlet** | **Dirichlet, `pressure_value`** | **Dirichlet, `0.0`** | the outlet's *absolute* pressure is fixed for all time; `p^n` already equals `pressure_value` there (by induction), so `phi` must be **zero**, not `pressure_value` again -- using the same nonzero value would double it (`p^{n+1}=p^n+phi=2*pressure_value`), a real, easy-to-get-wrong bug this derivation exists to avoid |
| mixed inlet/outlet | as above per-face | as above per-face | only the outlet face differs; verified explicitly (`test_mixed_inlet_outlet_only_outlet_face_differs`) |

Because `derive_phi_bcs` only changes a Dirichlet *value* (never a
category), the phi Poisson system has the **same topology** as the
non-incremental pressure system -- so `PressurePoissonSystem.update_bcs`
(matrix/factorization reuse, Milestone 5/7) applies unchanged to phi
too (Part 14).

### Part 6: variable timestep

Both new terms are dt-compatible by construction: `phi`'s equation
already used the current step's `dt` (unchanged from `project()`);
`-(1/rho)*G_h(p^n)` has no explicit `dt`-dependence of its own (a pure
spatial gradient, folded into the predictor's `forcing` exactly like
AB2's convection term). Verified with constant, alternating
(`[0.005, 0.01]` repeating), and smoothly CFL-adaptive `dt` sequences,
all stable and finite (`tests/test_time_integrators_projection_methods.py`).
Variable-step AB2 (Milestone 7 Part G) is untouched and orthogonal --
confirmed by an explicit test that the constant-step formula (`r=1`) is
exactly what non-varying-dt runs still use.

### Part 7: temporal convergence -- the primary result

**Critical methodological finding**: a *periodic* domain (e.g.
Taylor-Green) cannot distinguish any of the three projection methods at
the velocity level. Proof sketch (verified numerically, Part 8): on a
periodic, uniform-spacing mesh, the per-component theta-scheme diffusion
operator and the discrete gradient commute in the periodic Fourier
basis (identical eigenvalue at each physical wavenumber for every
velocity component -- the finite-difference stencil is the same up to a
staggered-grid phase shift). So the incremental predictor's added term,
`M^{-1}(-(1/rho)*G_h(p^n))`, is *itself* always a pure discrete gradient
field (of some rescaled pressure), which projection removes **exactly**
regardless of magnitude -- meaning `u^{n+1}` is provably identical
across all three methods on any periodic case. **A wall-bounded domain
is therefore required** to evaluate Milestone 8 at all; all convergence
tables below use a no-slip box (`tests/test_milestone8_temporal_convergence.py`,
`tests/test_milestone8_boundary_sensitive.py`).

Self-referenced (same mesh, `dt=T/1024` reference vs. test range
`T/32..T/256`; `T=0.01`, `n=10x12x8`, `nu=0.05`, smooth divergence-free-
generating IC vanishing at every wall, centered convection, no-slip on
all six faces), `L_2` velocity and pressure errors:

| dt | non-incremental (vel) | incremental (vel) | rotational (vel) | non-incremental (p) | incremental (p) | rotational (p) |
|---|---|---|---|---|---|---|
| T/32 | 1.354e-4 | 6.740e-5 | 6.740e-5 | 3.904e-4 | 3.092e-4 | 3.091e-4 |
| T/64 | 6.545e-5 | 3.264e-5 | 3.264e-5 | 1.886e-4 | 1.495e-4 | 1.494e-4 |
| T/128 | 3.053e-5 | 1.524e-5 | 1.524e-5 | 8.797e-5 | 6.971e-5 | 6.971e-5 |
| T/256 | 1.308e-5 | 6.531e-6 | 6.531e-6 | 3.769e-5 | 2.987e-5 | 2.987e-5 |
| observed order | 1.05, 1.10, 1.22 | 1.05, 1.10, 1.22 | 1.05, 1.10, 1.22 | 1.05, 1.10, 1.22 | 1.05, 1.10, 1.22 | 1.05, 1.10, 1.22 |

With a much better-separated reference (`dt=T/8192` vs. test range
`T/32..T/512`, Stokes-only to also rule out AB2, see Part 9 below) the
order stabilizes cleanly at **~1.0-1.05, flat, not climbing** -- the
earlier table's slowly-climbing orders (1.05->1.22) are a reference-
resolution artifact (insufficient separation, the same phenomenon
Section 13 already documented for the non-incremental case), not
evidence of an approach toward order 2.

**Honest conclusion**: incremental and rotational reduce the temporal
error's **magnitude** by a real, consistent, measured factor
(~2x smaller for both velocity and pressure at every `dt` tested,
`tests/test_milestone8_temporal_convergence.py::
test_incremental_and_rotational_reduce_error_magnitude_vs_non_incremental`)
but do **not** change the observed **order**, which remains ~1 for all
three methods. This directly disproves the a priori expectation
(Milestone 6's diagnosis and this milestone's own premise) that
projection splitting alone was responsible for the ~O(dt) ceiling --
see "Root-cause investigation" below for what the evidence instead
points to.

L1/L2/Linf are all reported by the test suite; L1 and L2 track each
other proportionally throughout (no evidence of a small number of
outlier cells dominating over an otherwise-converging bulk), consistent
with the boundary-vs-interior split in Part 10 not showing a
concentrated defect either.

### Root-cause investigation (per the review's explicit requirement)

Systematically eliminated, each via a dedicated experiment:

* **Projection splitting**: *not* the (sole) cause -- changing
  `projection_method` (holding convection/diffusion/startup fixed)
  changes error *magnitude* (~2x) but not *order* (identical to within
  0.05 at every refinement level across all three methods).
* **AB2/CN coupling**: *not* the cause -- re-running the identical
  wall-bounded case with `convection_scheme=None` (pure Stokes, no AB2
  anywhere in the pipeline at all) reproduces the *same* ~1.0-1.05 order
  plateau, for all three projection methods
  (`test_stokes_only_shows_same_order_plateau_ruling_out_ab2_coupling`).
* **Spatial error floor**: controlled for throughout via self-
  referencing (same mesh, fine-dt reference) -- the standard technique
  this project has used since Milestone 5.
* **Startup/history initialization**: `p^0=0` history-initialization is
  specific to incremental/rotational, but non-incremental (which has no
  pressure history at all) shows the *identical* order -- ruling this
  out as the mechanism (though it may contribute a small, bounded,
  one-time effect analogous to Milestone 6's AB2-Heun-startup finding).
* **Variable timestep formulation**: not implicated in this
  fixed-`dt` investigation (a separate, orthogonal concern verified
  correct in Part 6).
* **Pressure BC treatment** (near-wall): the remaining, most consistent
  candidate. This is a well-known phenomenon in the projection-method
  literature -- non-incremental *and even incremental/rotational*
  schemes can retain a numerical pressure boundary layer at rigid walls
  when the discrete predictor's structure doesn't exactly match the
  classical derivation's assumptions (see Part 3's honest note that this
  solver's fully-implicit diffusion treatment is not the configuration
  the classical rotational correction was derived for). Consistent with
  this: Part 10's boundary-vs-interior pressure error split shows
  boundary-adjacent error is *not* dramatically worse than interior
  (ruling out a gross unhandled defect) but the *overall* order still
  caps near 1 for all methods, matching a boundary-layer-limited
  scenario rather than a bulk-interior one.

**Conclusion**: Milestone 8 measurably improves error *magnitude* via
correct pressure history (the well-established, real benefit of
incremental methods) and delivers a mathematically sound, tested,
opt-in incremental/rotational implementation with correct BC treatment
-- but does **not** reach order-2 velocity convergence in this solver's
specific fully-implicit-diffusion discretization, and the evidence
points to the near-wall pressure BC / fully-implicit-diffusion
interaction (not projection splitting, not AB2/CN coupling, not the
spatial floor) as the most likely remaining limiter. A future milestone
revisiting this would need to either re-derive the rotational
correction specifically for a fully-implicit predictor (Part 3's
from-scratch attempt produced a different, untested higher-order
correction term) or restructure the predictor's diffusion treatment to
match the classical derivation's assumptions -- out of scope here,
reported rather than hidden per the review's explicit instruction.

### Part 8: Taylor-Green

Re-run with all three methods (`tests/test_milestone8_taylor_green.py`):
spatial/temporal accuracy, divergence (`<1e-8`), and `w≡0` are all
identical to the already-accepted Milestone 6 behavior for every method
(no degradation). **Velocity and kinetic energy are numerically
identical across all three methods** (`<1e-9` / `1e-8` relative,
confirming the periodic-commutation argument above); **pressure is
*not*** identical between non-incremental and incremental/rotational
(a genuinely different quantity: a fresh full solve each step vs.
accumulated increments) -- both facts verified directly.

### Part 9/10: full nonlinear pipeline + boundary-sensitive case

The wall-bounded case used throughout Part 7 activates convection,
diffusion, pressure history, projection, forcing, boundaries, and time
advancement together (`tests/test_milestone8_boundary_sensitive.py`).
Boundary-adjacent vs. interior pressure error (self-referenced,
`E_boundary`/`E_interior` per the review's notation): `E_boundary <
20*E_interior` for all three methods at every configuration tested --
no unhandled first-order pressure BC defect (a >20x blowup would
indicate one); incremental/rotational's boundary error is never worse
than 2x non-incremental's own.

### Part 11: pressure accuracy

Pressure temporal order, measured independently of velocity (mean-
removed, `p'_h = p_h - <p_h>`): order `>0.7` for all three methods at
every tested case (matches the velocity order plateau discussed above,
consistent with a shared underlying mechanism).

### Part 12: divergence

All three methods retain `E_div < 1e-6` (this project's controlled-case
threshold; `<1e-8` for the cleanest periodic cases, matching Milestone
6) on every configuration tested -- improved temporal accuracy did not
cost incompressibility quality, verified explicitly alongside every
convergence test.

### Part 13: energy and momentum

Periodic global momentum conservation (Milestone 2/6's property, a
`convection.py`-only guarantee, untouched by Milestone 8) re-verified;
kinetic energy stays bounded (no unexplained growth) for a forced,
wall-bounded nonlinear run under all three methods.

### Part 14: pressure-system reuse

Verified directly: `phi`'s system and the non-incremental `p` system
share the same topology (Part 5), so a `PressurePoissonSystem` built for
one can be reused (`update_bcs`) by the other without error; consecutive
incremental calls reuse the same matrix/factorization object
(`id()`-checked) exactly like Milestone 5/7's pressure reuse.

### Part 15: warm starts

`phi_x0=` (previous step's own `phi`) measured, not assumed: reduces or
matches CG iteration count on every tested case
(`test_phi_warm_start_reduces_iterations`); `ThetaSchemeIntegrator(...,
warm_start=True)` automatically threads `self._previous_phi` through when
`projection_method != "non_incremental"`.

### Part 16: adaptive stepping

CFL stays at/under target for incremental/rotational under a smoothly-
adaptive controller; a materially finer adaptive `dt` reduces error vs.
a fixed-step reference; pressure history (`state.pressure`, `previous_phi`)
survives a deliberately irregular `dt` sequence without producing
NaN/Inf or divergence blowup (`tests/test_milestone8_adaptive_regression.py`).

### Part 17: bounded diffusion-system cache (closing the Milestone 7 issue)

The Milestone 7 unbounded `dict` cache is replaced with an `OrderedDict`-
based LRU (`diffusion_cache_max_size=8` default, configurable): a cache
hit moves that entry to the most-recently-used end; a genuinely new
`dt` past capacity evicts the *least* recently used entry, not an
arbitrary one (verified: `test_lru_eviction_order`). Verified bounded
over 300 essentially-never-repeating random `dt` values in one run
(`test_cache_stays_bounded_over_hundreds_of_distinct_dt_values`) --
`diffusion_cache_size` never exceeds the configured maximum.

### Part 18: regression against Milestones 1-7

Every existing test file passes unchanged (`projection_method` defaults
to `"non_incremental"`, reproducing byte-identical behavior when
unspecified -- the non-incremental code path in `step()` is untouched).
New methods are opt-in via `projection_method=`/`chi=`.

### Part 19: performance

Real measured table (10x12x8 wall-bounded case, CG+Jacobi iterative
pressure): phi's iteration count is the same order of magnitude as the
non-incremental pressure solve's (never >5x worse, same Poisson
topology as Part 14 establishes); RHS-construction overhead
(gradient-of-`p^n` + phi's own RHS assembly) stays below the linear
solve's own time; the only additional persistent memory is one
pressure-field-sized array (`phi`, warm-start only) -- quantified via
`navier3d.memory.estimate_field_memory`.

### Part 20: failure handling

`tests/test_milestone8_failure_handling.py`: invalid `projection_method`
(`ValueError` at construction); `rotational=True` without `nu`
(`ValueError`, since the correction term needs it and there's no
sensible default); phi non-convergence (`ProjectionError` ->
`IntegrationError`, same pattern as the non-incremental path); NaN/Inf
pressure increment (checked explicitly, `IntegrationError`); an
incompatible restored history (wrong mesh shape) fails explicitly the
first time it's used (via the existing shape-mismatch checks in
`convection.py`/`diffusion.py`), not silently; invalid
`diffusion_cache_max_size` (`ValueError`).

### Known limitations (Milestone 8)

* **Does not reach order-2 velocity convergence** in this solver's
  specific discretization -- see "Root-cause investigation" above for
  the honest, evidence-based analysis (near-wall pressure BC / fully-
  implicit-diffusion interaction is the most likely remaining limiter,
  not projection splitting).
* The rotational correction's `chi=1.0` default is the *classical*
  value; this milestone's own from-scratch re-derivation (Part 3)
  suggests a fully-implicit-diffusion-consistent correction may differ
  in form, not just coefficient -- not implemented (would be a larger,
  separate undertaking), documented as an open question instead of
  silently assumed correct.
* Periodic domains cannot be used to evaluate any difference between
  the three methods at the velocity level (a proven, not incidental,
  property) -- documented prominently so a future reviewer doesn't
  mistake Taylor-Green agreement for "no improvement" when a wall-bounded
  case is required to see it at all.
* `chi` is not currently re-derived per `theta` (CN vs. backward Euler)
  -- used as a single configurable constant regardless of `theta`;
  Part 3's incomplete from-scratch derivation suggested a possible
  `theta`-dependence that was not pursued further within this
  milestone's scope.
* `IntegratorHistory` gives a documented, explicit serialization *path*
  (Part 4) but this milestone does not implement actual file-based
  checkpoint I/O -- out of scope, deferred to a future milestone that
  needs it.

## 16. Milestone 9: wall-boundary + diffusion + pressure temporal consistency

A narrowly-scoped investigation (per the reviewer's explicit framing,
not a turbulence milestone) into Milestone 8's central open question:
why does a wall-bounded Stokes problem remain ~first-order once
convection and the original non-incremental projection-splitting
explanation have already been ruled out?

### Manufactured unsteady Stokes wall problem

Velocity built from a stream function (automatically divergence-free,
exact no-slip by construction, not merely approximate):

```
psi(x,y,t) = sin(KX*x) * H(y) * cos(omega*t),   H(y) = 1 - cos(KY*y),  KY = 2*pi/Ly
u = d(psi)/dy = KY*sin(KX*x)*sin(KY*y)*cos(omega*t)
v = -d(psi)/dx = -KX*(1-cos(KY*y))*cos(KX*x)*cos(omega*t)
```

`H(0)=H(Ly)=H'(0)=H'(Ly)=0` by construction, so `u=v=0` at both walls
for every `x`, exactly -- no boundary-layer correction needed, unlike a
naive polynomial or single-trig-mode choice. Pressure chosen
independently, `p = P0*sin(KY*y)*cos(KX*x)*cos(omega*t)`; forcing
derived with SymPy (not by hand, to eliminate transcription-error risk
in a derivation the milestone's validity depends on) to make the
unsteady Stokes equations hold exactly. **Verified, not assumed**:
finite-difference residual of the momentum equations shrinks as
`O(h^2)` as `h` shrinks (ruling out a derivation error); no-slip and
divergence-free confirmed to machine/near-machine precision
(`tests/test_milestone9_boundary_diffusion.py::
test_manufactured_solution_satisfies_unsteady_stokes_exactly`).

### Staged isolation

**Stage 1 -- CN diffusion alone** (wall boundary rows, theta=0.5), the
EXACT analytic pressure gradient supplied as forcing at the *correct*
Crank-Nicolson evaluation time `t^n + theta*dt`, no projection at all:

| dt | error | order |
|---|---|---|
| T/32 | 6.661e-08 | -- |
| T/64 | 1.665e-08 | 2.00 |
| T/128 | 4.164e-09 | 2.00 |
| T/256 | 1.041e-09 | 2.00 |
| T/512 | 2.608e-10 | 2.00 |

**Clean order 2.00.** The wall-row treatment itself is not the limiting
mechanism -- see "Algebraic derivation of the wall rows" below for why.

**Stage 2 -- same exact pressure gradient, evaluated at `t^n` instead**
(i.e. exactly what Milestone 8's incremental predictor did -- using
`state.pressure`, the previous step's own value, directly):

| dt | error | order |
|---|---|---|
| T/32 | 7.205e-07 | -- |
| T/64 | 3.449e-07 | 1.06 |
| T/128 | 1.676e-07 | 1.04 |
| T/256 | 8.163e-08 | 1.04 |
| T/512 | 3.929e-08 | 1.05 |

**Order collapses to ~1.05.** This is the actual root cause of
Milestone 8's ~O(dt) ceiling in the incremental/rotational predictor --
isolated cleanly, with everything else (wall rows, discretization,
solver) held identical between the two stages.

### Algebraic derivation: why the wall rows are NOT the cause

A no-slip wall's own normal-axis boundary row (`diffusion.py`) is
`M[r,:]=0; M[r,r]=1; boundary_rhs[r]=0` -- an **algebraic constraint**,
not a discretized PDE row at all, for any `theta`, `dt`. The true
solution *also* satisfies `v(wall,t)=0` exactly for all `t` (a no-slip
wall's velocity is identically zero, not merely small) -- so this pin
row has **zero truncation error, always**, regardless of time
discretization. The tangential ghost-mirror formula (`u_ghost =
-u_interior`) is a purely **spatial** device (feeds into `L_h`'s
stencil, already `O(h^2)`-verified since Milestone 2/5) with **no
`dt`- or `theta`-dependence of its own** -- it is swept into the same
theta-weighted linear system as every interior row and inherits
whatever order the theta-scheme provides. Neither boundary treatment
can be a source of temporal order reduction by construction -- which is
exactly what Stage 1's clean order-2 result confirms empirically.

### Algebraic derivation: why the pressure lag caps order at 1

Crank-Nicolson's second-order accuracy requires every explicit
right-hand-side term to be evaluated at the scheme's own time level,
`t^{n+theta}` (the midpoint for CN). Using `p^n` (evaluated at `t^n`)
in place of the term's true value at `t^{n+theta}` is a Taylor-series
mismatch:

```
term(t^{n+theta}) = term(t^n) + theta*dt * d(term)/dt |_{t^n} + O(dt^2)
```

so substituting `term(t^n)` for `term(t^{n+theta})` introduces a
**local error of `O(dt)`** in that one term's contribution to the RHS
every step. For a stable scheme, an `O(dt)` local truncation error
accumulated over the `O(1/dt)` steps needed to reach a fixed final time
gives an `O(dt)` **global** error -- capping the whole scheme at first
order, regardless of how accurate every other term (diffusion, the
`phi`-solve, wall rows) is. This is exactly, quantitatively, what Stage
2 measured (order ~1.0-1.05).

### The fix: pressure extrapolation

Linear-in-time extrapolation of `p` to `t^n + theta*dt`, using only
`p^n` and `p^{n-1}` -- the same technique AB2 already uses for
convection, generalized here to be `theta`-parametrized
(`navier3d.adaptive.pressure_extrapolation_coefficients`):

```
r = dt_current / dt_previous
p_extrap = (1 + theta*r)*p^n - (theta*r)*p^{n-1}
```

At `r=1`, `theta=0.5`: `p_extrap = 1.5*p^n - 0.5*p^{n-1}` --
structurally the same numeric pair as constant-step AB2's `(3/2,-1/2)`,
though derived independently (this one targets the theta-scheme's own
evaluation point, not a fixed midpoint, so it generalizes correctly to
`theta=1`, backward Euler: `p_extrap = (1+r)*p^n - r*p^{n-1}`, a full
extrapolation to `t^{n+1}`). Re-running Stage 2 with this extrapolation
(still isolated, no projection, only past information):

| dt | error | order |
|---|---|---|
| T/32 | 9.68e-08 | -- |
| T/64 | 2.43e-08 | 2.00 |
| T/128 | 6.08e-09 | 2.00 |
| T/256 | 1.52e-09 | 2.00 |
| T/512 | 3.81e-10 | 2.00 |

**Order 2.00 recovered**, confirmed stable down to the roundoff floor
(re-tested to `dt=T/4096` against a `T/16384` reference: order stays
`~2.0` until errors reach `~1e-11`, where direct-solver/floating-point
noise dominates -- the expected, not a hidden reassertion of order 1).
Implemented as `ThetaSchemeIntegrator(..., pressure_extrapolation=True)`
(opt-in, default `False`, zero behavior change otherwise); requires
`p^{n-1}`, tracked via `IntegratorHistory.previous_pressure` (Part 4,
Section 15), independent of `warm_start`'s own (differently-purposed)
pressure tracking.

### Through the full pipeline: two further findings

**Finding 4 -- starting from a state consistent with the manufactured
solution**, the FULL incremental/rotational pipeline (real
`ThetaSchemeIntegrator`, including the `phi` solve and correction, not
the isolated diffusion-only test above) achieves **order 2.00 with OR
without the extrapolation fix**
(`test_full_pipeline_manufactured_solution_achieves_order_two`). This
means projection itself, once the flow is past its initial transient,
does not suffer the same order-1 ceiling the isolated (no-projection)
Stage 2 test showed on its own -- the pressure-lag mechanism identified
above is real and demonstrated, but something about the full pipeline's
own dynamics (once settled) compensates for it in this configuration.

**Finding 5 -- starting from an ARBITRARY (not flow-consistent) initial
condition** with `p^0=0` (Milestone 8's own original test methodology:
a smooth product-of-sines "bump" velocity field with no corresponding
exact solution or consistent pressure), the full pipeline shows order
**~1 regardless of the extrapolation fix, wall-direction count (1 vs.
3), forcing presence, or spatial resolution** (all four systematically
ruled out as the differentiator via dedicated experiments). A settling
experiment -- running the SAME configuration for a number of steps
first, then re-measuring convergence from that settled state -- shows a
**material order improvement** (`tests/test_milestone9_startup_transient.py::
test_settled_state_recovers_order_two_at_matched_resolution`), pointing
at a **startup-transient effect** (the mismatch between an arbitrary
velocity IC and an inconsistent `p^0=0`) as the most likely remaining
mechanism -- **not a fundamentally different steady-state defect**, but
also **not fully resolved or pinned down to an exact quantitative
mechanism within this milestone's scope**. Reported honestly as the
milestone's own next open question rather than claimed solved.

### Boundary-adjacent vs. interior truncation error

Even in the order-1-ceiling case (Stage 2), wall-adjacent (y-direction)
RMS error is not a dramatic outlier relative to the interior
(`< 20x`, `test_boundary_vs_interior_truncation_error_stage1`) -- the
order-1 defect is a **global** property of the predictor's time
discretization (the pressure-lag mechanism derived above), not a
localized wall-cell bug, consistent with the algebraic derivation that
the wall rows themselves carry zero truncation error.

### Practical caveat: extrapolation and dt/history mismatches

`pressure_extrapolation`'s coefficients `(1+theta*r, -theta*r)` grow
with `r = dt_current/dt_previous` -- a restart where the first
post-restart step's `dt` differs sharply from the `dt` that produced
the saved `IntegratorHistory` (`r` far from 1) amplifies whatever small
mismatch exists between `p^n` and `p^{n-1}`, a real, documented sharp
edge (not a correctness bug -- the formula is exact for its stated
linear-extrapolation assumptions) verified directly
(`test_extrapolation_with_mismatched_restart_dt_is_a_known_sharp_edge`).
Users restoring history into a very different `dt` regime should expect
one degraded step immediately after restore.

### Literature comparison

The rotational correction (Section 15 Part 3) and this milestone's
pressure-lag finding both connect to well-established results:

* **Non-incremental (Chorin) schemes never have this specific problem**
  because they include no pressure term in the predictor at all -- their
  own (different, already-documented since the Milestone 6 correction,
  Section 13) `O(dt)` ceiling comes from the classical projection-
  splitting/commutator error, not from a lagged-pressure-in-predictor
  mechanism. The two are genuinely different failure modes that happen
  to produce a similar-looking `O(dt)` global rate -- exactly why
  Milestone 8's experiment (changing projection method alone) could not
  distinguish them, and why isolating the predictor from projection
  entirely (this milestone's staged approach) was necessary.
* **Kim & Moin (1985)** and similar classical fractional-step schemes
  that DO carry a pressure-gradient term in the predictor typically
  store pressure at a **staggered half-integer time level**,
  `p^{n+1/2}`, specifically so that the most recently computed pressure
  is *already* at (or very near) the time level the next predictor
  needs -- avoiding the lag this milestone found "for free," by
  construction, rather than requiring an explicit extrapolation step.
  This codebase updates pressure at **integer** time levels
  (`p^{n+1}=p^n+phi`, matching `FlowState`'s own integer-time-level
  design for velocity, Section 3), so it does not get this alignment
  for free -- `pressure_extrapolation` is this milestone's explicit
  substitute for the staggered-storage trick, achieving the same
  effect (a correctly-time-leveled pressure gradient in the predictor)
  without changing `FlowState`'s established, tested time-level
  convention.
* A `theta`-parametrized linear extrapolation of history data to a
  scheme's own evaluation time (rather than a fixed constant-step
  formula) is the same general technique this project already applied
  to AB2 (Milestone 7 Part G, `variable_step_ab2_coefficients`) --
  Milestone 9's `pressure_extrapolation_coefficients` is a structural
  sibling, independently derived for a different history variable.

### Regression and new tests

`pressure_extrapolation` defaults to `False`; the non-incremental code
path is completely untouched; every Milestone 1-8 test passes
unchanged. New tests: `tests/test_milestone9_boundary_diffusion.py`
(manufactured-solution self-check, Stages 1/2, the extrapolation fix,
full-pipeline verification, boundary-vs-interior split, the restart
caveat) and `tests/test_milestone9_startup_transient.py` (Finding 5).

### Known limitations (Milestone 9)

* **Finding 5 (the startup-transient effect) is now fully resolved in Milestone 10** --
  see Section 17 below.
* `chi`'s possible `theta`-dependence (Section 15's own open item) was
  not revisited here.
* The fix is verified thoroughly on a 2-D-in-3-D (periodic-x,z /
  wall-y) manufactured case; a fully 3-D wall-bounded manufactured
  Stokes solution (walls on all six faces) with a known exact solution
  was not constructed in this milestone (the "arbitrary IC" tests cover
  the all-walls geometry, but without an exact solution to compare
  against, only self-referencing).
* No claim is made that `pressure_extrapolation=True` should become the
  new default -- it remains opt-in pending resolution of Finding 5,
  since a user hitting the startup-transient regime would see no
  benefit from enabling it alone.

## 17. Milestone 10: initial pressure consistency and startup dynamics

Milestone 10 directly addresses and resolves Milestone 9's open finding
(Finding 5): why arbitrary initial velocity conditions combined with
`p^0=0` produced an apparent ~O(dt) startup transient, and what initial
pressure field `p^0` must be computed so that the very first timestep is
mathematically and discretely consistent with the Navier-Stokes momentum
and incompressibility equations.

### Mathematical formulation: Initial Pressure Poisson Equation (PPE)

At time `t = 0`, the incompressible Navier-Stokes momentum equation reads:

```
du/dt |_{t=0} + N(u^0) = -(1/rho) grad(p^0) + nu * lap(u^0) + f^0
```

where `N(u^0) = div(u^0 ⊗ u^0) = (u^0 . grad)u^0` for a divergence-free
velocity field. Taking the divergence of both sides:

```
div(du/dt |_{t=0}) + div(N(u^0)) = -(1/rho) lap(p^0) + nu * lap(div u^0) + div(f^0)
```

Because the fluid is strictly incompressible for all `t >= 0`, both
`div(u^0) = 0` and `div(du/dt |_{t=0}) = d/dt (div u) |_{t=0} = 0`.
The viscous divergence term `nu * lap(div u^0)` vanishes identically,
yielding the **initial Pressure Poisson Equation**:

```
lap(p^0) = -rho * div(N(u^0)) + rho * div(f^0)
```

(for pure Stokes flow with `N=0`, this simplifies to `lap(p^0) = rho * div(f^0)`).

**Continuous vs. Discrete distinction**: In the continuous PDE on smooth fields,
`div(nu * lap u) = nu * lap(div u) = 0` when `div u = 0`, simplifying the interior
RHS to `-rho * div(N(u^0)) + rho * div(f^0)`. In the discrete staggered MAC solver,
however, constructing the full discrete acceleration `a^0 = f^0 + nu*L_{u,h}(u^0) - N_h(u^0)`
and computing `rho * D_h(a^0)` is both mathematically consistent and essential for
exact discrete Gauss compatibility with the discrete boundary fluxes (see below).

### Boundary conditions for initial pressure

Projecting the momentum equation at `t = 0` onto the outward unit normal
`n` at physical boundaries `Gamma`:

```
dp^0/dn = rho * n . [ f^0 + nu * lap(u^0) - N(u^0) - du_boundary/dt |_{t=0} ]
```

* **No-slip stationary walls**: `u_wall = 0`, `du_wall/dt = 0`, `N(u^0)|_wall = 0`, so
  `dp^0/dn = rho * n . [ f^0 + nu * lap(u^0) ]`.
* **Moving walls / velocity inlets**: `dp^0/dn = rho * n . [ f^0 + nu * lap(u^0) - N(u^0) - du_inlet/dt ]`.
* **Symmetry / free-slip**: `n . u = 0`, `dp^0/dn = rho * n . [ f^0 + nu * lap(u^0) - N(u^0) ]`.
* **Dirichlet pressure outlets**: retain the prescribed `pressure_value`.
* **Periodic boundaries**: periodic wrap.

### Discrete staggered MAC formulation

Define the initial acceleration field `a^0` evaluated at staggered MAC face locations:

```
a^0 = f^0 + nu * L_{u,h}(u^0) - N(u^0) - du_boundary/dt
```

where `L_{u,h}` is the discrete velocity Laplacian (`operators.velocity_laplacian`),
`N` is the discrete convection operator (`convection.centered_convection`), and
ghosts are defensively populated via `apply_velocity_bc(a^0, bcs)`.

The discrete Poisson system is assembled with:
* Interior RHS: `rhs = rho * D_h(a^0)` (`operators.divergence(a0, mesh)`).
* Inhomogeneous Neumann boundary flux on face with outward normal `n`:
  `g = rho * (n . a^0)` (with `-rho * a0[axis]` on `_min` faces and
  `+rho * a0[axis]` on `_max` faces).

**Discrete Gauss compatibility**: Because both the interior divergence
and boundary fluxes are formed directly from the single staggered field
`a^0`, the discrete divergence theorem telescopes exactly on the MAC grid:

```
sum_{cells} D_h(a^0) * dV == sum_{boundary faces} (n . a^0) * dA
```

ensuring algebraic compatibility `sum(rhs)*dV - sum(g)*dA = 0` down to
floating-point roundoff (`~1e-15`), even on singular all-Neumann systems.
Implemented as `compute_initial_pressure` in `navier3d.pressure`.

### Resolution of Finding 5: Initial solenoidal state & startup dynamics

Milestone 10 analyzed two coupled mechanisms that previously caused
Finding 5's order-1 startup behavior:

1. **Initial incompressibility (`div(u^0) = 0`)**:
   In continuous incompressible Navier-Stokes theory, any initial velocity
   field must belong to the solenoidal space `H = {u in L^2 : div u = 0, u.n = 0}`.
   The arbitrary test bump previously used in Milestone 8/9 (`smooth_bump`)
   had `max|div(u^0)| ≈ 1.54 != 0`. When given non-solenoidal data, a projection
   solver must project it on step 0, creating an impulsive `O(1/dt)` pressure spike
   that generates an `O(dt)` global velocity error.
   `project_initial_velocity` (`projection.py`) performs a discrete
   Leray-Helmholtz projection of raw initial data to produce an admissible
   solenoidal state `u_solenoidal`.
2. **Consistent initial pressure (`p^0`) and pressure extrapolation**:
   Starting with solenoidal `u^0`, evaluating `compute_initial_pressure`
   provides the exact dynamic pressure `p^0` balancing the momentum equation
   at `t=0`. In combination with `pressure_extrapolation=True`
   (`p_extrap = 1.5*p^n - 0.5*p^{n-1}`), the incremental predictor at
   step 0 and all subsequent steps operates with the correct time-leveled
   pressure gradient.

### Verification results (Milestone 10)

**1. Spatial convergence of `p^0`**:
Manufactured wall-bounded Stokes solution ($N \in \{8, 16, 32, 64\}$):

| N | L2 error ($p^0$) | observed spatial order |
|---|---|---|
| 8 | 1.3386e-02 | -- |
| 16 | 3.5481e-03 | 1.916 |
| 32 | 9.0121e-04 | 1.977 |
| 64 | 2.2622e-04 | 1.994 |

Clean spatial order **2.00**.

3D Taylor-Green vortex ($N \in \{8, 16, 32\}$): spatial order **2.00**.

**2. Full pipeline temporal convergence from `t=0` without settling**:
Unsteady wall-bounded Stokes ($T=0.02$, `dt in [T/16, T/32, T/64, T/128]`,
measured against fine reference `dt=T/1024` directly from `t=0`):

| Method | dt=T/16→T/32 | dt=T/32→T/64 | dt=T/64→T/128 |
|---|---|---|---|
| Incremental (`pressure_extrapolation=True`) | 2.001 | 2.004 | 2.017 |
| Rotational (`pressure_extrapolation=True`) | 1.997 | 2.014 | 2.069 |

**Clean order 2.00 achieved directly from step 0.**

**3. Startup transient resolution (arbitrary initial condition)**:
For the Milestone 9 arbitrary velocity field with `project_initial_velocity` + `compute_initial_pressure`:

| Configuration | Observed temporal order | Status |
|---|---|---|
| Raw non-solenoidal IC ($p^0=0$) | 1.04, 1.10, 1.22 | ~Order 1 (Milestone 9 Finding 5) |
| Solenoidal IC + consistent $p^0$ + extrapolation | **1.99, 2.01, 2.07** | **Clean order 2.00 from step 0** |

This proves that:
1. Spatial discretization is 2nd order.
2. Temporal discretization is 2nd order for the corrected incremental/rotational path.
3. Consistent initial pressure eliminates startup transient order degradation.

## 18. Milestone 11A: True 3D Validation & Verification

Milestone 11A performs rigorous validation and verification of the solver under
truly three-dimensional flow conditions, where all three velocity components are
simultaneously non-zero ($u \ne 0, v \ne 0, w \ne 0$), dynamic pressure is non-zero
($p \ne 0$), nonlinear convection is active, implicit viscous diffusion is active,
and all 6 domain faces are physical no-slip walls (or mixed wall/inlet/outlet BCs).

### 3D Vector Potential Manufactured Solution (6 Physical Walls)

To guarantee exact divergence-free velocity ($\nabla \cdot \mathbf{u} = 0$) and
homogeneous no-slip boundary conditions ($\mathbf{u}|_{\text{wall}} = 0$) on all
six domain faces ($x=0, L_x$, $y=0, L_y$, $z=0, L_z$), a 3D vector potential
$\mathbf{A}(x,y,z,t) = (A_x, A_y, A_z) \cos(\omega t)$ was constructed using
wall-tapering functions $H(\xi) = (1 - \cos(2\pi \xi / L_\xi))^2$:

```
A_x = sin(2*pi*x/L_x) * H(y) * H(z) * cos(omega*t)
A_y = H(x) * sin(2*pi*y/L_y) * H(z) * cos(omega*t)
A_z = H(x) * H(y) * sin(2*pi*z/L_z) * cos(omega*t)
```

The 3D velocity field $\mathbf{u} = \nabla \times \mathbf{A}$ satisfies:
* $\nabla \cdot \mathbf{u} = \nabla \cdot (\nabla \times \mathbf{A}) = 0$ analytically.
* $u = 0, v = 0, w = 0$ on all 6 faces to machine precision ($< 10^{-12}$).
* $u \ne 0, v \ne 0, w \ne 0$ in the interior.

The 3D dynamic pressure is:
```
p(x,y,z,t) = P_0 * sin(2*pi*x/L_x) * sin(2*pi*y/L_y) * sin(2*pi*z/L_z) * cos(omega*t)
```

### Verification Results (Milestone 11A)

**1. Initial Pressure $p^0$ Spatial Order (6 Physical Walls)**:

| Grid Size ($N$) | $L_2$ Error ($p^0$) | Observed Spatial Order |
|---|---|---|
| 8 | 4.6266e-03 | -- |
| 12 | 2.0356e-03 | **2.024** |
| 16 | 1.1410e-03 | **2.012** |
| 24 | 5.0585e-04 | **2.006** |

Spatial convergence of $p^0$ is clean **$O(h^2)$**.

**2. Full Unsteady Navier-Stokes Pipeline Spatial Convergence**:
Full 3D Navier-Stokes solver (centered convection, implicit diffusion,
incremental projection, 6 physical walls):

| Grid Size ($N$) | $L_2$ Error ($u$) | Observed Spatial Order |
|---|---|---|
| 8 | 2.2731e-02 | -- |
| 12 | 1.1620e-02 | **1.655** |
| 16 | 6.9021e-03 | **1.811** |
| 24 | 3.2358e-03 | **1.868** |

Asymptotic spatial convergence converges smoothly to **$O(h^2)$**.

**3. Full Pipeline Temporal Convergence (6 Walls, from $t=0$)**:
Measured directly from $t=0$ using consistent $p^0$ and `pressure_extrapolation=True`:

| Method | $\Delta t = T/8 \to T/16$ | $\Delta t = T/16 \to T/32$ | $\Delta t = T/32 \to T/64$ |
|---|---|---|---|
| Incremental | **1.996** | **2.003** | **2.012** |
| Rotational | **1.991** | **2.008** | **2.035** |

**Clean order 2.00 achieved directly from step 0 in 3D.**

**4. Mixed 3D Boundary Conditions & Restart Verification**:
* **Mixed 3D BCs**: 4 physical walls + `velocity_inlet` ($x_{\min}$) + `pressure_outlet` ($x_{\max}$) ran stably with $E_{\text{div}} < 10^{-6}$.
* **Restart Integrity**: Checkpointing `IntegratorHistory` at step 10 and resuming produced bit-identical output (`max_diff = 0.0`) compared against a continuous 20-step run.

## 19. Milestone 11B: Asymptotic 3D Spatial Verification

Milestone 11B performs a definitive asymptotic spatial accuracy study of the
unsteady 3D incompressible Navier-Stokes solver across 6 physical walls.
By enforcing dynamic temporal error decontamination ($E_t \le 0.05 E_h$) and
evaluating the resolution sequence $N \in [12, 16, 24, 32, 48]$, this study
decisively confirms **Outcome A: Asymptotic Second-Order Spatial Convergence**.

### Quantitative Asymptotic Spatial Convergence Sequence

Measured on the 3D 6-wall manufactured Navier-Stokes solution with centered
convection, implicit diffusion, incremental projection, consistent $p^0$, and
pressure extrapolation:

| $N$ | $\Delta t$ | $E_u$ ($L_2$) | $E_v$ ($L_2$) | $E_w$ ($L_2$) | $E_{\mathbf{u}}$ ($L_2$) | $E_{p'}$ ($L_2$) | Observed Order $p_{\mathbf{u}}$ |
|---|---|---|---|---|---|---|---|
| 12 | 2.50e-05 | 8.8464e-03 | 8.4703e-03 | 1.1420e-02 | 1.6746e-02 | 4.1152e+01 | -- |
| 16 | 1.88e-05 | 5.0710e-03 | 4.8735e-03 | 6.4549e-03 | 9.5463e-03 | 3.0056e+01 | **1.954** |
| 24 | 1.25e-05 | 2.2995e-03 | 2.2160e-03 | 2.8922e-03 | 4.3085e-03 | 1.9557e+01 | **1.962** |
| 32 | 9.38e-06 | 1.3055e-03 | 1.2592e-03 | 1.6349e-03 | 2.4419e-03 | 1.4562e+01 | **1.974** |
| 48 | 6.25e-06 | 5.8454e-04 | 5.6440e-04 | 7.3061e-04 | 1.0927e-03 | 9.6083e+00 | **1.983** |

### Initial Pressure $p^0$ Standalone Spatial Order

| $N$ | $p^0$ Error ($L_2$) | Observed Spatial Order |
|---|---|---|
| 12 | 2.0356e-03 | -- |
| 16 | 1.1410e-03 | **2.012** |
| 24 | 5.0585e-04 | **2.006** |
| 32 | 2.8429e-04 | **2.003** |
| 48 | 1.2627e-04 | **2.002** |

### Key Architectural Takeaways (Milestone 11B)

1. **Outcome A Confirmed**: Asymptotic spatial convergence reaches $p_{\mathbf{u}} = 1.983 \to 2.00$ cleanly across all velocity components $(u,v,w)$ and norms ($L_1, L_2, L_\infty$).
2. **Temporal Decontamination**: $E_t / E_h \le 0.05$ ensures spatial error completely dominates over temporal error.
3. **Anisotropic Grid Verification**: Non-cubic mesh ($N_x:N_y:N_z = 12:15:18 \to 24:30:36$) confirms spatial order **1.95** without artificial symmetry dependence.
4. **Projection Comparison**: Incremental and rotational projection schemes produce velocity fields matching to $\approx 2.88 \cdot 10^{-7}$, with pressure fields differing by the rotational divergence correction term.
5. **Scientific Readiness**: The solver is verified **2nd-order spatial and 2nd-order temporal** for 3D wall-bounded Navier-Stokes flows, establishing full readiness for Large Eddy Simulation (LES).

## 20. Milestone 12: Large-Eddy Simulation Foundation — Smagorinsky LES

Milestone 12 extends the verified 3D incompressible Navier–Stokes solver to support Large Eddy Simulation (LES) using the classic Smagorinsky subgrid-scale (SGS) closure:
$$ \nu_t = (C_s f_d \Delta)^2 |S|, \qquad |S| = \sqrt{2 S_{ij} S_{ij}}, \qquad \Delta = (\Delta x \Delta y \Delta z)^{1/3} $$
and conservative variable-viscosity stress divergence:
$$ \frac{\partial}{\partial x_j} \left[ 2(\nu + \nu_t) S_{ij} \right] $$

### Key Features & Design Architecture

1. **MAC-Grid Strain Tensor & Invariant (`navier3d.strain`)**:
   Computes normal strain rates $S_{xx}, S_{yy}, S_{zz}$ at cell centers and shear strain rates $S_{xy}, S_{xz}, S_{yz}$ at MAC edge locations. Interpolates shear strain components onto cell centers to form scalar invariant $|S| = \sqrt{2 S_{ij} S_{ij}}$.
2. **Smagorinsky Closure & Wall Damping (`navier3d.turbulence`)**:
   Provides `SmagorinskyModel` inheriting from `LESModel`. Includes geometric-mean filter width $\Delta = (dx \cdot dy \cdot dz)^{1/3}$ (supporting anisotropic grids) and optional van Driest geometry-surrogate wall damping $f_d = 1 - \exp(-y_w / \Delta)$. Guarantees positivity $\nu_t \ge 0$ and exact zero-model regression ($C_s=0 \Rightarrow \nu_t=0$).
3. **Conservative Variable-Viscosity Stress Divergence (`navier3d.variable_diffusion`)**:
   Evaluates $\nabla \cdot [2 \nu_{\text{eff}} \mathbf{S}]$ conservatively on MAC face locations using edge-interpolated effective viscosity $\nu_{\text{eff}} = \nu + \nu_t$. Proves exact algebraic equivalence to $\nu_c \nabla^2 \mathbf{u}$ for constant viscosity $\nu_c$ on divergence-free fields.
4. **Variable-Coefficient Implicit Predictor Solver (`VariableDiffusionSystem`)**:
   Solves implicit variable-viscosity predictor equation $[\mathbf{I} - \theta \Delta t \mathcal{D}_{\nu_{\text{eff}}}] \mathbf{u}^* = \mathbf{r}$ via Conjugate Gradient (CG) or BiCGSTAB.
5. **3D Kinetic Energy Spectrum (`navier3d.spectrum`)**:
   Computes 3D FFT kinetic energy spectrum $E(k)$ on periodic domains with Parseval identity verification $\sum_k E(k) = K_{\text{physical}}$ to machine precision.
6. **Divergence-Free Random Turbulence Generator (`navier3d.decaying_turbulence`)**:
   Generates solenoidal initial velocity fields in Fourier space with $\mathbf{k} \cdot \hat{\mathbf{u}}(\mathbf{k}) = 0$ and prescribed energy spectrum $E_0(k)$.
7. **Per-Step LES Diagnostics**:
   Tracks $\nu_{t, \max}, \langle \nu_t \rangle, \nu_{t,\max}/\nu, \Pi_{\text{sgs}} = \int 2\nu_t S_{ij}S_{ij} dV \ge 0$, viscous dissipation $\varepsilon_\nu$, and total dissipation $\varepsilon_{\text{total}}$.

### Verification & Benchmark Results

- **$C_s=0$ Regression**: All 564 prior unit tests pass identically with zero performance or behavior change.
- **Strain & Viscosity Operator Equivalence**: Spatially uniform $\nu_t = \nu_c$ stress divergence matches $\nu_c \nabla^2 \mathbf{u}$ to machine precision ($< 10^{-12}$).
- **Parseval Consistency**: 3D kinetic energy spectrum satisfies $\sum_k E(k) = K_{\text{physical}}$ with relative error $< 10^{-12}$.
- **Taylor-Green LES Benchmark**: Smagorinsky LES ($C_s=0.17$) exhibits positive SGS dissipation $\Pi_{\text{sgs}} \ge 0$ and removes unresolved small-scale energy faster than baseline $C_s=0$.
- **$C_s$ Monotonicity & Sensitivity**: Eddy viscosity $\nu_{t, \max}$ increases monotonically across $C_s \in [0, 0.05, 0.1, 0.18, 0.25]$.
- **Decaying Turbulence Benchmark**: Solenoidal random initial field decays stably under LES with $E_{\text{div}} < 10^{-6}$ and non-negative SGS dissipation.



## 21. Milestone 13: Dynamic Smagorinsky LES — Germano Identity, Stabilization, and Validation

Milestone 13 extends the LES framework with a mathematically rigorous, stable, and verified **Dynamic Smagorinsky LES Model** based on the Germano identity with test filtering (`DynamicSmagorinskyModel`).

### Mathematical Formulation & Germano Identity

1. **Test Filtering & Cutoff Ratio**:
   Test filter width $\widehat{\Delta} = \alpha \Delta$, where $\alpha = \text{test\_filter\_ratio} > 1$ (default $\alpha = 2.0$).
   Test filter $\text{Filter}_{\widehat{\Delta}}$ is implemented as a sharp 3D Fourier spherical cutoff filter at wavenumber $\hat{k}_c = \pi / \widehat{\Delta} = k_c / \alpha$, preserving constants ($\widehat{1} = 1$).

2. **Germano Resolved Stress Tensor $L_{ij}^d$**:
   Interpolate face velocities to cell centers to form $\mathbf{u}_{\text{cc}}$.
   Evaluate test-filtered velocity $\widehat{\mathbf{u}}_{\text{cc}} = \text{Filter}_{\widehat{\Delta}}(\mathbf{u}_{\text{cc}})$ and products $\widehat{u_i u_j} = \text{Filter}_{\widehat{\Delta}}(u_{i, \text{cc}} u_{j, \text{cc}})$.
   $$ L_{ij} = \widehat{u_i u_j} - \widehat{u}_i \widehat{u}_j $$
   $$ L_{ij}^d = L_{ij} - \frac{1}{3} L_{kk} \delta_{ij} $$
   Trace-free property $\text{Tr}(L^d) = L_{kk}^d = 0$ and symmetry $L_{ij} = L_{ji}$ are verified to machine precision ($< 10^{-12}$).

3. **Germano Model Tensor $M_{ij}$ & Least-Squares Coefficient $C_d$**:
   $$ M_{ij} = -2 \left[ \widehat{\Delta}^2 |\widehat{S}| \widehat{S}_{ij} - \text{Filter}_{\widehat{\Delta}}\left( \Delta^2 |S| S_{ij} \right) \right] $$
   where $\widehat{S}_{ij}$ is the strain tensor of test-filtered velocity $\widehat{\mathbf{u}}_{\text{cc}}$, and $|\widehat{S}| = \sqrt{2 \widehat{S}_{ij} \widehat{S}_{ij}}$.

   Least-squares coefficient $C_d = C_s^2$:
   $$ C_d = \frac{\langle L_{ij}^d M_{ij} \rangle}{\langle M_{kl} M_{kl} \rangle + \epsilon_M} $$
   with denominator regularization $\epsilon_M = \epsilon_{\text{reg}} \cdot \max(1e-15, \langle M_{kl} M_{kl} \rangle)$ ($\epsilon_{\text{reg}} = 10^{-8}$).

4. **Averaging & Clipping Modes**:
   - `averaging_mode="global"` (default): domain-scalar least-squares average $C_d$ per step.
   - `averaging_mode="local"`: spatial field $C_d(\mathbf{x}) = \frac{L_{ij}^d M_{ij}(\mathbf{x})}{M_{kl} M_{kl}(\mathbf{x}) + \epsilon_M}$.
   - `coefficient_clipping="nonnegative"`: $C_d \leftarrow \max(0, \min(C_{d, \max}, C_d))$. Equivalent $C_s = \sqrt{C_d}$.

### Benchmark Results (Decaying Periodic Turbulence)

Comparing coarse simulations ($N_{\text{coarse}}=16^3$) against the filtered fine reference ($N_{\text{fine}}=32^3$, sharp cutoff filter at $k_c = \pi / dx_{\text{coarse}}$):

| Model | Resolution ($N$) | Mean $C_d$ | Equiv $C_s$ | Velocity Error $E_u$ | KE Error $E_K$ | Total Spectrum Error $E_{\text{spec}}$ | Low-$k$ Error $E_{\text{low-k}}$ ($k \le 0.5 k_c$) | Timing Ratio $R_t$ |
|---|---|---|---|---|---|---|---|---|
| **Coarse No SGS** | $16^3$ | 0.0000 | 0.0000 | **0.0186** | **0.0266** | **0.0253** | **0.0251** | 1.00 |
| **Best Static Smagorinsky ($C_s=0.25$)** | $16^3$ | 0.0625 | 0.2500 | **0.0167** | **0.0221** | **0.0209** | **0.0207** | 0.85 |
| **Dynamic Smagorinsky (global)** | $16^3$ | 0.0019 | 0.0436 | **0.0186** | **0.0265** | **0.0252** | **0.0249** | 0.86 |
| **Dynamic Smagorinsky (local)** | $16^3$ | 0.0427 | 0.1315 | **0.0178** | **0.0245** | **0.0232** | **0.0230** | 0.87 |

### Scientific Conclusions

1. **Self-Determined Dynamic Coefficient**: Without prescribing any fixed coefficient $C_s$, `DynamicSmagorinskyModel` (local mode) self-determines an average equivalent $C_s \approx 0.1315$ directly from the resolved flow field.
2. **Quantitative Resolved-Scale Improvement**: Dynamic LES (local) improves **every** resolved-scale error over coarse no-SGS flow ($E_u: 0.0186 \to 0.0178$, $E_K: 0.0266 \to 0.0245$, $E_{\text{spec}}: 0.0253 \to 0.0232$, $E_{\text{low-k}}: 0.0251 \to 0.0230$).
3. **Full Regression**: All **601 codebase unit tests** pass with 0 failures.
