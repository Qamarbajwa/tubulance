# TP2-G5-A1 — Exact N Dynamics

Use N=tr(Y^T Y)=||Y||_F^2, B_Y=D(Omega G+GA-T^S), and
C_ell=D partial_ell G. Matrix Ito calculus gives
\[
\boxed{dN=b_Nd\tau+\sigma_N\cdot dB_\tau}
\]
with
\[
\boxed{b_N=2\langle Y,B_Y\rangle_F+
2\nu\sum_\ell||C_\ell||_F^2}
\]
and
\[
\boxed{(\sigma_N)_\ell=2\sqrt{2\nu}\langle Y,C_\ell\rangle_F.}
\]
The first term is deterministic transport/source drift and the second is
quadratic-variation production. A1 makes no favorable or unfavorable sign
classification; that belongs to A2.
