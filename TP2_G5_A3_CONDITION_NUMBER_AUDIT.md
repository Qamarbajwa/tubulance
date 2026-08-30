# TP2-G5-A3 — Condition-Number Envelope Audit

Let the singular values of invertible `D` be `sigma_1 >= sigma_2 >= sigma_3 > 0`. For every vector `v`,

`sigma_3^2 |v|^2 <= |D v|^2 <= sigma_1^2 |v|^2`.

Apply the bounds to each column of `G` in the numerator and to `omega` in the denominator:

`(sigma_3^2/sigma_1^2) ||G||_F^2/|omega|^2 <= Xi <= (sigma_1^2/sigma_3^2) ||G||_F^2/|omega|^2`.

Hence

`Cond(D)^(-2) kappa_omega^2 <= Xi <= Cond(D)^2 kappa_omega^2`.

The inequality is conditional on `D` being invertible and on `omega != 0`; it is an envelope, not an equivalence with uniform constants. If the condition number is uncontrolled, the envelope supplies no uniform control. Using a bound on `Cond(D)` that already requires a continuation norm would be circular for the Clay target.

No equality with `kappa_omega` is asserted except in special metric-isotropic cases such as `D^T D = c I`.
