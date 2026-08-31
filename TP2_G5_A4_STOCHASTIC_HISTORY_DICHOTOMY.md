# TP2-G5-A4 — Stochastic-History Dichotomy

The sequence \(J_n(a)\) is nonnegative. Regard it in the compactification \([0,\infty]\). From every subsequence one may extract a further subsequence with a limit \(J_*\in[0,\infty]\).

* **Branch D (DECOHERENT):** if \(J_*>0\), including \(J_*=\infty\), choose \(0<\delta<J_*\) (or any finite \(\delta>0\) in the infinite case). Then eventually \(J_n\ge\delta\), so \(\chi_n\le e^{-\delta}\) and the relative variance is at least \(e^\delta-1\).
* **Branch R (RIGID):** if \(J_*=0\), then \(J_n\to0\), \(\chi_n\to1\), and the relative variance tends to zero.
* **OSCILLATORY:** the original sequence need not satisfy either global limit. Alternating positive and zero clusters is resolved only after subsequence extraction.

Hence the exact candidate result is a subsequence-qualified scale-critical stochastic-history dichotomy, not a singularity theorem. It classifies accumulated relative quadratic-variation production versus relative \(L^2\) history concentration.

