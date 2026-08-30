# TP2-G5-A1 — Exact Quotient SDE for Xi

On R>0 set Xi=N/R. Applying Ito to f(N,R)=N R^{-1} gives
\[
d\Xi=b_\Xi d\tau+\sigma_\Xi\cdot dB_\tau,
\]
\[
\boxed{b_\Xi=\frac{b_N}{R}-\frac{Nb_R}{R^2}
-\frac{\sigma_N\cdot\sigma_R}{R^2}
+\frac{N|\sigma_R|^2}{R^3}},
\qquad
\boxed{\sigma_\Xi=\frac{\sigma_N}{R}-\frac{N\sigma_R}{R^2}}.
\]
Here b_R=2nu N. With C_ell=D(partial_ell G) and y_ell=Y e_ell:
\[
\boxed{\begin{aligned}
b_\Xi={}&\frac{2\langle Y,B_Y\rangle_F+2\nu\sum_\ell||C_\ell||_F^2}{R}
-\frac{2\nu N^2}{R^2}\\
&-\frac{8\nu\sum_\ell\langle Y,C_\ell\rangle_F(Z^TYe_\ell)}{R^2}
+\frac{8\nu N\sum_\ell(Z^TYe_\ell)^2}{R^3}.
\end{aligned}}
\]
The explicit martingale coefficient is
\[
\boxed{(\sigma_\Xi)_\ell=2\sqrt{2\nu}
\left[\frac{\langle Y,C_\ell\rangle_F}{R}
-\frac{N(Z^TYe_\ell)}{R^2}\right].}
\]
The cross-covariation and denominator Ito correction are both present.
