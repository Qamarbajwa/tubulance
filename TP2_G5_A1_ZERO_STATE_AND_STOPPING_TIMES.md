# TP2-G5-A1 — Zero States and Stopping Times

Because D is invertible, R=|D omega|^2=0 if and only if omega=0. Define
\[
\tau_{\omega=0}=\inf\{\tau:R_\tau=0\},\qquad
\tau_N=\inf\{\tau:N_\tau=0\},\qquad
\tau_R=\inf\{\tau:R_\tau=0\}.
\]
The quotient SDE is valid only for tau<tau_R. If spectral factors are used,
also stop at loss of the declared isolated spectral cluster; the raw Xi
equation itself needs no spectral gap.

| State | Condition | Safe statement |
|---|---|---|
| A | R>0, N>0 | Xi>0; log Xi may be used only here. |
| B | R>0, N=0 | Xi=0; log Xi is undefined. |
| C | R=0 | Xi is undefined; quotient SDE is stopped. |

State C has zero mu-weight in the accepted weighted identity when that
measure exists, but this does not permit an unstopped pathwise quotient.
At G=0 and omega nonzero, Y=N=Xi=0 instantaneously. No logarithmic extension
is introduced.
