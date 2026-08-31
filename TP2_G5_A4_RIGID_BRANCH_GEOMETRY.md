# TP2-G5-A4 — Rigid Branch and Geometry

On the A3 domain \(q=|\omega|>0\), \(|D\xi|>0\), the accepted decomposition is

\[
\Xi=M_D+C_D,\quad M_D=\sum_j(\partial_j\log q+\beta_j)^2,\quad
C_D=\sum_j|P_\perp D(\partial_j\xi)/|D\xi||^2,
\]

with \(M_D,C_D\ge0\). Consequently, Branch R gives the separate conclusions

In plain notation, `Xi=M_D+C_D`; both pieces are nonnegative, and the two separate conclusions concern the integrated `E_mu[M_D]` and `E_mu[C_D]` terms.

\[
\int_{s_n}^{t_n}E_{\mu_r}[M_D]dr\to0,
\qquad
\int_{s_n}^{t_n}E_{\mu_r}[C_D]dr\to0.
\]

These are provisional **AMPLITUDE_METRIC_RIGIDITY** and **TRANSVERSE_DIRECTION_METRIC_RIGIDITY** statements: they are integrated and \(\mu_r\)-weighted. For \(\varepsilon>0\), the normalized history measure \(\bar\mu_n(B)=L_n^{-1}\int_{s_n}^{t_n}\mu_r(B_r)dr\) obeys

\[
\bar\mu_n\{M_D>\varepsilon\}\le
\frac{\int E_{\mu_r}M_Ddr}{\varepsilon L_n},
\quad
\bar\mu_n\{C_D>\varepsilon\}\le
\frac{\int E_{\mu_r}C_Ddr}{\varepsilon L_n}.
\]

Since \(L_n\) can itself tend to zero, \(J_n\to0\) alone does not force these normalized bad-set measures to vanish. It certainly does not imply pointwise, uniform, Euclidean, Lipschitz, Hölder, cone, sparseness, or analyticity control.

Relative \(L^2\) rigidity does not imply pathwise equality, almost sure equality, supremum convergence, or uniform trajectory convergence. A rare-history variable with large deviation and vanishing probability is a basic counterexample to that promotion.
