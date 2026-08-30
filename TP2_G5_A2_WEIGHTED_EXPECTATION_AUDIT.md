# TP2-G5-A2 — Mu-Weighted Expectation Audit

Let \(S_\tau={\mathbb E}R_\tau\) and \(\rho_\tau=R_\tau/S_\tau\), on the
admissible support where the accepted mu-weight is defined. The weight evolves
as
\[
d\rho=\left(\frac{b_R}{S}-\frac{R S'}{S^2}\right)d\tau
+\frac{\sigma_R}{S}\cdot dB,\qquad
S'={\mathbb E}b_R=2\nu{\mathbb E}N.
\]
Product Ito gives the honest weighted derivative:
\[
\frac{d}{d\tau}{\mathbb E}_{\mu}[\Xi]
={\mathbb E}_{\mu}[b_\Xi]
+\frac1S{\mathbb E}[\Xi b_R]
-\frac{S'}S{\mathbb E}_{\mu}[\Xi]
+\frac1S{\mathbb E}[\sigma_R\cdot\sigma_\Xi],
\]
when stopped martingales are integrable. The last three terms are the
time-dependent-weight correction. Therefore it is invalid to write only
\({\mathbb E}_{\mu}[b_\Xi]\).
Under the accepted support identity \(R\Xi=N\), the same calculation can be
written
\[
\frac{d}{d\tau}{\mathbb E}_{\mu}[\Xi]
=\frac{{\mathbb E}b_N}{S}
-\frac{{\mathbb E}N}{S^2}(2\nu{\mathbb E}N),
\]
but this still is not closed in \({\mathbb E}_{\mu}[\Xi]\). State C requires
the A0 zero-weight convention or a separately proved null contribution.
Classification: WEIGHTED_DYNAMICS_NOT_CLOSED.
