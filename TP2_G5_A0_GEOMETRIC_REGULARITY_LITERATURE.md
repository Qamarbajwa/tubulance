# TP2-G5-A0 — Geometric and Regularity Literature

## Classical and established criteria

* Constantin–Fefferman, *Direction of vorticity and the problem of global
  regularity for the Navier–Stokes equations*, Indiana Univ. Math. J. 42
  (1993), 775–789, [journal record](https://iumj.org/article/3627/): high-
  vorticity vorticity-direction coherence prevents blowup.
* Beirão da Veiga–Berselli, *On the regularizing effect of the vorticity
  direction in incompressible fluid flows*, Differential and Integral
  Equations 15 (2002), 345–356, [PDF](https://people.dm.unipi.it/beiraodaveiga/pdf/hbv-79.pdf):
  weaker Sobolev/integrability directional hypotheses imply smoothness.
* Miller, *A regularity criterion ... involving only the middle eigenvalue of
  the strain tensor*, [arXiv:1710.05569](https://arxiv.org/abs/1710.05569):
  scale-critical necessary-and-sufficient blowup criteria in terms of the
  positive middle strain eigenvalue under its hypotheses.
* Grujić, *A geometric measure-type regularity criterion ...*, Nonlinearity
  26 (2013), 289–296, DOI [10.1088/0951-7715/26/1/289](https://doi.org/10.1088/0951-7715/26/1/289):
  local one-dimensional sparseness of intense superlevel sets at analyticity
  scales prevents singularity formation under the theorem's assumptions.

## 2025–2026 results audited separately

* Lei–Ren–Tian, *A geometric characterization of potential Navier–Stokes
  singularities*, [arXiv:2501.08976](https://arxiv.org/abs/2501.08976), is a
  preprint in this audit. For suitable weak solutions, a double-cone condition
  on high-vorticity directions implies regularity; equivalently, a potential
  singularity's direction set must meet every great circle. Its proof uses
  local vorticity flux and critical rescaling. This constrains direction
  geometry, not `kappa_omega^2`, `Theta`, `Xi`, or `E_mu[Xi]` directly.
* Grujić, *Logarithmic Depletion of Vortex Stretching and Singularity
  Evasion ...*, [arXiv:2607.08866](https://arxiv.org/abs/2607.08866), is
  treated as `PREPRINT_RESULT`. It proposes logarithmic BMO directional
  depletion, commutator cancellation, Lorentz–Zygmund improvement and a
  sparseness/analyticity closure. No peer-reviewed status was independently
  confirmed in this audit. It does not state the Xi identity.
* Miller's strain-eigenvalue line remains a conditional critical criterion;
  it is not an a-priori estimate forcing Xi. Analyticity-radius results give
  conditional spatial regularity scales and do not identify a deformation-
  relative density.

## Transfer matrix

| Literature input | `kappa_omega^2` | `Theta` | `Xi` | `E_mu[Xi]` | Type |
|---|---|---|---|---|---|
| Constantin–Fefferman | no direct bound | no | no | no | conditional geometric |
| Beirão da Veiga–Berselli | no direct bound | no | no | no | conditional geometric |
| Miller strain eigenvalue | no | no | no | no | conditional critical strain |
| Grujić sparseness/analyticity | indirect geometry only | no | no | no | local conditional |
| Lei–Ren–Tian 2025 | direction-set constraint | no | no | no | preprint, local conditional |
| Grujić 2026 logarithmic depletion | stretching depletion under hypothesis | no | no | no | preprint, conditional |

No direction theorem can be translated into an Xi theorem without a proved
deformation-gradient and weighting bridge. In particular, direction coherence
does not control the relative action of `D` on `J_omega` versus `omega`.

No peer-reviewed status was independently confirmed for the recent preprints
listed above.
