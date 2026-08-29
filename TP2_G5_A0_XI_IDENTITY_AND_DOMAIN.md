# TP2-G5-A0 — Xi Identity and Domain Contract

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G5-A0`  
**Constitution:** Mathematical Research Constitution v1.0.1  
**Status:** A0 frozen; no A1 dynamics derived here.

## Frozen objects

For a classical periodic Navier–Stokes history and a fixed terminal point,

\[
 Z_s=D_s\omega(A_s,s),\qquad S_s=\mathbb E|Z_s|^2,
\]
\[
 Q_s=2\nu\,\mathbb E\|D_sJ_\omega(A_s,s)\|_F^2,
 \qquad d\mu_s=\frac{|Z_s|^2}{S_s}\,d\mathbb P
\]

whenever `S_s > 0`. The primary object is

\[
 \Xi_s=\frac{\|D_sJ_\omega(A_s,s)\|_F^2}{|D_s\omega(A_s,s)|^2}.
\]

The accepted G4 identity is

\[
 \partial_s\log\chi_s=\frac{Q_s}{S_s}
 =2\nu\,\mathbb E_{\mu_s}[\Xi_s].
\]

The identity is a weighted identity on its declared domain, not a pointwise
lower bound and not a regularity theorem.

## State taxonomy

| State | Condition | Xi | Measure/identity treatment |
|---|---|---|---|
| `X1` | `omega != 0`, `J_omega != 0` | finite and nonnegative | factorization is valid |
| `X2` | `omega != 0`, `J_omega = 0` | exactly `0` | denominator is positive because `D` is invertible; `Theta` is undefined |
| `X3` | `omega = 0` | algebraically `0/0`, undefined | `|Z|^2=0` on that history, hence zero `mu_s` weight; no silent extension |
| `X4` | `S_s=0` | measure undefined | `Z_s=0` a.s.; `mu_s` and `Q_s/S_s` are not formed |

Because `D_s` is invertible,

\[
 |D_s\omega|=0\iff \omega=0.
\]

Also, `S_s=0` iff `Z_s=0` almost surely. For a nonzero terminal vorticity,
`E Z_s = omega(x,T) != 0`, so `S_s>0`; X4 can occur only in the zero-mean
degenerate branch. G3's corrected chi taxonomy distinguishes zero mean with
positive variance (`chi=0`) from zero second moment (`chi` undefined).

## Factorization audit

On X1 only,

\[
 \kappa_\omega^2=\frac{\|J_\omega\|_F^2}{|\omega|^2},\qquad
 A_{\rm grad}=\frac{\|DJ_\omega\|_F^2}{\|J_\omega\|_F^2},\qquad
 A_\omega=\frac{|D\omega|^2}{|\omega|^2},
\]
\[
 \Theta=\frac{A_{\rm grad}}{A_\omega},\qquad
 \Xi=\kappa_\omega^2\Theta.
\]

`Xi` is the `PRIMARY_RELATIVE_QV_DENSITY`; `kappa_omega^2` is the
`LOCAL_INVERSE_VORTICITY_LENGTH_FACTOR`; `Theta` is the
`DIMENSIONLESS_RELATIVE_ORIENTATION_FACTOR`. The factors are not substitutes
for Xi, and the factorization is not asserted on X2 or X3.

## Scaling audit

Under `u_lambda(x,t)=lambda u(lambda x,lambda^2 t)`, with the usual induced
parabolic bookkeeping,

\[
 \omega\mapsto\lambda^2\omega,\qquad
 J_\omega\mapsto\lambda^3J_\omega,
 \qquad D\mapsto D,
\]
so `Xi -> lambda^2 Xi`. Likewise `Q/S -> lambda^2` and
`2 nu E_mu[Xi] -> lambda^2`. Thus `Xi` is a scale-critical *rate density* in
the precise dimensional/parabolic sense used by G4. This does not imply
regularity. On the fixed unit torus this is a formal/local scaling dimension,
not exact invariance of the fixed-domain problem; the fixed-torus obstruction
is supplied separately by the exact periodic shear family.

## A1 stopping contract

A1 may only form `N/R` after stopping or restricting away from the relevant
zero sets:

\[
 \tau_\omega=\inf\{\tau:|\omega|=0\},\quad
 \tau_N=\inf\{\tau:N=0\},\quad
 \tau_R=\inf\{\tau:R=0\},
\]

and, where spectral projectors are used, away from loss of the declared
isolated spectral cluster. Since `R=|D omega|^2`, `tau_R=tau_omega` under
invertibility of `D`. A1 must prefer the coupled variables `N`, `R`, and
`Xi=N/R`; it must not use `log Xi` on X2 or any zero set.
