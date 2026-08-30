# TP2-G5-A2 — Exact Square Completion

For every Brownian coordinate \(\ell\),
\[
\left\|H_\ell-\frac{2c_\ell}{R}Y\right\|_F^2
=||H_\ell||_F^2-\frac{4c_\ell}{R}\langle Y,H_\ell\rangle_F
+\frac{4c_\ell^2}{R^2}||Y||_F^2.
\]
Multiplying by \(2\nu/R\) and summing gives exactly the three stochastic
terms:
\[
\boxed{I_\Xi=\frac{2\nu}{R}\sum_\ell
\left\|H_\ell-\frac{2c_\ell}{R}Y\right\|_F^2\ge0.}
\]
Since \(||Y||_F^2=N\), the compressed drift is
\[
\boxed{b_\Xi=D_\Xi+R_\Xi+I_\Xi}
\]
with
\[
D_\Xi=\frac{2\langle Y,F\rangle_F}{R},\qquad
R_\Xi=-2\nu\Xi^2.
\]
The coefficient 2, the Frobenius norm, the column \(Ye_\ell\), and all R
powers are forced by componentwise expansion. This is exact algebraic
compensation, not a regularity estimate.
The exact zero condition is
\[
I_\Xi=0\iff H_\ell=\frac{2c_\ell}{R}Y\quad\text{for every }\ell.
\]
It is an instantaneous compatibility condition. Invariance and dynamical
realizability are not established.
