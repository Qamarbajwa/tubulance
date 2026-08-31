# TP2-G5-A4 — Exact Chi / Variance Identity

For each terminal pair \((x_n,t_n)\), use only its own stochastic Cauchy history. Let \(Z_{n,s}=D_s\omega(A_s,s)\),

\[
m_n=E Z_{n,s_n}=\omega(x_n,t_n),\qquad S_n=E|Z_{n,s_n}|^2,
\]

and \(\chi_n=|m_n|^2/S_n\). The accepted orientation is

\[
\partial_s\log\chi_s=2\nu E_{\mu_s}[\Xi_s],\qquad \chi_{t_n}=1.
\]

Therefore

In plain notation, `J_n = -log chi_n` and `chi_n = exp(-J_n)`.

\[
J_n(a):=2\nu\int_{s_n}^{t_n}E_{\mu_r}^{(x_n,t_n)}[\Xi_r]dr
=-\log\chi_n,
\qquad \chi_n=e^{-J_n(a)}.
\]

Because \(S_n-|m_n|^2=E|Z_{n,s_n}-m_n|^2\),

\[
\boxed{\frac{E|Z_{n,s_n}-m_n|^2}{|m_n|^2}
=\frac{1-\chi_n}{\chi_n}=\frac1{\chi_n}-1=e^{J_n(a)}-1.}
\]

This is exact wherever the accepted stochastic identity and nonzero normalization apply. It is a relative \(L^2\) statement; it does not bound \(|m_n|\), prove pathwise convergence, or provide regularity.
