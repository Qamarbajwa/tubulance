# TP2-G5-A0 — Stochastic Cauchy Literature Foundation

**Audit date:** 2026-08-29  
**Scope:** primary and near-primary sources located through arXiv, publisher or
institutional records; periodic/whole-space versus boundary formulations kept
separate.

## Constantin–Iyer (2008)

**Source:** Constantin & Iyer, *A stochastic Lagrangian representation of the
three-dimensional incompressible Navier–Stokes equations*, CPAM 61 (2008),
330–345, DOI [10.1002/cpa.20192](https://doi.org/10.1002/cpa.20192),
[arXiv:math/0511067](https://arxiv.org/abs/math/0511067).

**Exact result:** for a classical solution, a backward stochastic flow driven by
uniform Brownian noise gives a probabilistic Weber representation of velocity;
curling it yields the stochastic Cauchy representation
`omega(x,t)=E[D_{t0,t} omega_0(A_{t0,t}(x))]` (with the project's Convention M).

**Domain:** periodic and decaying whole-space versions; boundaries require a
separate treatment. **Regularity:** classical/Hölder solution hypotheses and
differentiable stochastic flow maps. **Direction:** backward in time from the
terminal observation. **Flow/deformation:** inverse stochastic flow and its
spatial Jacobian, with determinant one in the incompressible setting.

**Variance information:** representation theorem itself does not supply the
G5 relative density, a covariance lower bound, or a cancellation estimate.
**Already proves:** stochastic transport/Cauchy representation. It does not
supply the G5 relative density. **Xi adds:** a
specific energy-weighted ratio comparing deformed vorticity-gradient energy to
deformed vorticity energy. **Xi does not add:** stochastic Cauchy transport or
an unconditional regularity conclusion.

## Constantin–Iyer (2011), domains with boundary

**Source:** *A stochastic-Lagrangian approach to the Navier–Stokes equations in
domains with boundary*, [CMU repository record](https://kilthub.cmu.edu/articles/journal_contribution/A_stochastic-Lagrangian_approach_to_the_Navier_Stokes_equations_in_domains_with_boundary/6476723).

This extends the representation with boundary-vorticity influence and local
time terms. It is not a wall-free periodic formula. It does not provide Xi or
its weighted expectation. G5 therefore uses the torus formula and records
boundary formulations as a distinct domain branch.

## Eyink–Gupta–Zaki (2020)

**Sources:** *Stochastic Lagrangian Dynamics of Vorticity I: General Theory*,
[arXiv:1912.06677](https://arxiv.org/abs/1912.06677), and Part II,
[arXiv:1912.06684](https://arxiv.org/abs/1912.06684); the journal version is
available through [NSF PAR](https://par.nsf.gov/servlets/purl/10204876).

**Exact result:** stochastic Cauchy invariants/contributions are conserved on
average backward in time for viscous incompressible flows; wall-bounded work
adds wall-vorticity flux and validates Monte Carlo statistics in channel DNS.
The papers report exponential backward variance growth and physical
cross-history cancellation in selected turbulent events.

**Domain/regularity:** wall-bounded and interior formulations, using smooth
flow fields and DNS evaluation. **Flow/deformation/vorticity:** stochastic
backward paths, deformation Jacobian, and transported vorticity contributions.
**Variance/covariance:** empirical/Monte Carlo variance and cancellation, not a
universal lower or upper bound for Xi or `E_mu[Xi]`.

**Already proves:** stochastic Cauchy transport and that mean conservation can
coexist with large path dispersion. **Xi adds:** a different normalized local
quadratic-gradient density. **Xi does not add:** a new Cauchy theorem, a
universal cancellation law, or regularity closure.

## Stochastic Kelvin and Cauchy-invariant context

Kelvin circulation and Euler Cauchy invariants are classical frozen-in laws;
the stochastic viscous extension is the Constantin–Iyer framework. The
literature supports calling the transport foundation known. No audited source
was found that states the exact G5 object `||D J_omega||_F^2/|D omega|^2`
under the Cauchy-energy weight.

## Boundary versus periodic decision

`TP2-G5` is restricted to smooth, unforced, periodic `T^3` histories unless an
artifact explicitly opens another domain. Boundary local-time and wall-flux
terms cannot be silently dropped. Weak-solution trajectory existence results
do not by themselves justify differentiable `D` and `J_omega` in the Xi
formula.
