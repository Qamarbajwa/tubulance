# TP2-G5-A1 — Three-Level Understanding Gate

## Level 1

Xi's stochastic motion is controlled by the coupled endpoint-deformation,
vorticity-gradient, and correlated numerator-denominator Brownian noises.

## Level 2 — architecture

\[
Z=D\omega
\quad\longrightarrow\quad
R=|Z|^2,
\]
\[
DJ_\omega=Y
\quad\longrightarrow\quad
N=||Y||_F^2,
\]
\[
(N,R,[N,R])
\quad\longrightarrow\quad
\Xi=N/R.
\]

The first arrow is the accepted Cauchy martingale. The second carries the
matrix drift and spatial stochastic derivatives. The final arrow is a
stopped quotient with correlated noise; its load-bearing terms are the
numerator-denominator covariance and the denominator Hessian correction.

## Level 3 — derivation map

1. Forwardize with tau=T-s and freeze Convention M.
2. Use da=-u d tau+sqrt(2nu)dB and dD=DA d tau.
3. Differentiate vorticity transport to obtain
   dG=(-SG+GA-T^S)d tau+sqrt(2nu) sum partial_l G dB_l.
4. Product rule gives
   dY=D(Omega G+GA-T^S)d tau+sqrt(2nu) sum D partial_l G dB_l.
5. Frobenius Ito gives b_N and sigma_N.
6. Vector Ito gives b_R=2nu N and sigma_R.
7. The shared Brownian coordinates give d[N,R].
8. Quotient Ito gives the exact stopped Xi drift and martingale coefficient.
9. Stop at R=0; permit Xi=0 at N=0 but forbid log Xi there.
10. Retain coefficient-field dependence; no expectation closure is inferred.

The drift terms are recorded algebraically only. Favorable or unfavorable
classification is explicitly deferred to the prohibited-from-this-increment
A2 gate.
