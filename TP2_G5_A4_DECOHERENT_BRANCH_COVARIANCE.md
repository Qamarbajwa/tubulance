# TP2-G5-A4 — Decoherent Branch and Covariance

Branch D yields only

\[
\frac{\operatorname{tr}C_{s_n}}{|\omega(x_n,t_n)|^2}
=\frac{E|Z_{n,s_n}-m_n|^2}{|m_n|^2}
=e^{J_n}-1\ge e^\delta-1.
\]

This is **NONTRIVIAL_RELATIVE_STOCHASTIC_VARIANCE**. It does not bound \(|E Z|\) from above and does not reverse the previously rejected Jensen/amplitude closure. It supplies no direction distribution, amplitude-tail bound, higher-moment estimate, Cauchy-energy concentration theorem, or covariance eigenframe conclusion by itself.

In plain language, decoherence does not bound the terminal mean.

The trace is the sum of covariance eigenvalues. A fixed trace lower bound is compatible with isotropic dispersion, low-rank dispersion, or directional dispersion. Therefore the correct outcome is **INSUFFICIENT_INFORMATION**: covariance trace does not imply isotropy, a positive spectral gap, or any specified eigenvalue allocation.
