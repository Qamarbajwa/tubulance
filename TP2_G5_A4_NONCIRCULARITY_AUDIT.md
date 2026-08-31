# TP2-G5-A4 — Non-Circularity Audit

The exact identities are valid conditionally on the accepted smooth stochastic-Cauchy domain. They do not assume a singularity exists. The dangerous sequence uses a continuation theorem only when explicitly stated; \(M_n\to\infty\) is not silently built in.

| Proposed exclusion | Classification | Reason |
|---|---|---|
| Use \(J_n\to0\) to prove regularity | OPEN / not proved | It is only integrated weighted rigidity. |
| Use \(J_n\ge\delta\) to prove regularity | OPEN / not proved | Relative variance does not bound the terminal mean. |
| Add bounded \(\|\omega\|_\infty\), BKM, Serrin, or critical velocity norm | CIRCULAR_FOR_CLAY_CLOSURE | These are continuation-critical assumptions. |
| Add bounded strain, \(\operatorname{Cond}(D)\), controlled high derivatives, or an analyticity radius | CIRCULAR_FOR_CLAY_CLOSURE unless independently a-priori | They can contain the target control. |
| Use \(\Xi=M_D+C_D\) and nonnegative integrals | VALID_CONDITIONAL | Only separate integrated consequences follow. |
| Use Markov/Chebyshev history estimates | POTENTIALLY_APRIORI | Exact normalized bound retains \(1/L_n\); no uniform conclusion follows. |
| Transfer a literature direction theorem | YES_WITH_EXTRA_ASSUMPTIONS at best | The missing history-to-space bridge is explicit. |

