# NS-NONLINEAR-SELF-FOCUS-002: Exact Dyadic Enstrophy Flux, Commutator Structure, and Operator Splitting

**Milestone:** `NS-NONLINEAR-SELF-FOCUS-002`  
**Parent Milestone:** `NS-NONLINEAR-SELF-FOCUS-001-R1`  
**Active Governance:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority:** `Mathematical Research Constitution v1.0.1`  
**Locked Problem:** $\mathbb{T}_L^3 = (\mathbb{R}/L\mathbb{Z})^3$, $\nu > 0$, $f = 0$  
**Immutable Gates:** `Clay Statement B = UNRESOLVED` | `Release = NO-GO` | `Deployment Authority = NONE` | `NS-OPENAI-B2 = BLOCKED` | `NS-GOV-MIG-V404-001 = MIGRATION_BLOCKED`

---

## 1. Fixed Frequency Decomposition: Option A (Sharp $L^2$-Orthogonal Fourier Shells)

To eliminate the quadratic overlap defect ($\sum_q \hat{\psi}_q(k)^2 \in [1/2, 1)$) documented in `NS-NONLINEAR-SELF-FOCUS-001-R1` (`NEG-EV-048`), `NS-NONLINEAR-SELF-FOCUS-002` locks **Option A — Disjoint $L^2$-Orthogonal Dyadic Fourier Shells** across the entire milestone.

Let $\mathbb{T}_L^3 = (\mathbb{R}/L\mathbb{Z})^3$ ($L > 0$) have fundamental wavenumber $k_0 := \frac{2\pi}{L} = \lambda_{\rm P}^{1/2}$ (with $k_0 = 1$ on $\mathbb{T}_{2\pi}^3$). For any mean-zero vector field $f \in L^2(\mathbb{T}_L^3; \mathbb{R}^3)$ with Fourier series
$$f(x) = \sum_{k \in k_0\mathbb{Z}^3 \setminus \{0\}} \widehat{f}(k) e^{i k \cdot x}, \qquad \widehat{f}(k) := \frac{1}{L^3}\int_{\mathbb{T}_L^3} f(x) e^{-i k \cdot x}\,dx,$$
define for each $q \in \mathbb{N}_0 = \{0, 1, 2, \dots\}$ the disjoint dyadic annulus:
$$\mathcal{C}_q := \left\{ k \in k_0\mathbb{Z}^3 \setminus \{0\} : k_0 2^q \le |k| < k_0 2^{q+1} \right\}, \qquad \bigsqcup_{q=0}^\infty \mathcal{C}_q = k_0\mathbb{Z}^3 \setminus \{0\}.$$
Define the orthogonal shell projection $P_q$ and low/high cutoff projections $P_{\le Q}, P_{>Q}$ ($Q \in \mathbb{N}_0$) by:
$$(P_q f)(x) := \sum_{k \in \mathcal{C}_q} \widehat{f}(k) e^{i k \cdot x}, \qquad P_{\le Q} f := \sum_{q=0}^Q P_q f, \qquad P_{>Q} f := \sum_{q=Q+1}^\infty P_q f = (I - P_{\le Q})f.$$

### 1.1 Exact Structural Properties of $P_q$ (`EXACT_IDENTITY`)
For all mean-zero $f, g \in H^1(\mathbb{T}_L^3; \mathbb{R}^3)$ and all $p, q \in \mathbb{N}_0$:
1. **Mutual $L^2$ and $\dot{H}^s$ Orthogonality**:
   $$\langle P_q f, P_p g \rangle_{L^2(\mathbb{T}_L^3)} = 0, \qquad \langle \nabla P_q f, \nabla P_p g \rangle_{L^2(\mathbb{T}_L^3)} = 0 \qquad (\forall q \neq p).$$
2. **Idempotence and Self-Adjointness**:
   $$P_q^2 = P_q, \qquad P_q^* = P_q, \qquad P_{\le Q} P_{>Q} = P_{>Q} P_{\le Q} = 0.$$
3. **Exact Quadratic Reconstruction**:
   $$\|f\|_{L^2}^2 = \sum_{q=0}^\infty \|P_q f\|_{L^2}^2 = \|P_{\le Q}f\|_{L^2}^2 + \|P_{>Q}f\|_{L^2}^2, \qquad \|\nabla f\|_{L^2}^2 = \sum_{q=0}^\infty \|\nabla P_q f\|_{L^2}^2 = \|\nabla P_{\le Q}f\|_{L^2}^2 + \|\nabla P_{>Q}f\|_{L^2}^2.$$
4. **Commutation with Constant-Coefficient Differential & Biot–Savart Operators**:
   $P_q$ commutes with $\partial_i$, $\Delta$, $\operatorname{curl}$, $\operatorname{div}$, and the Leray projector $\mathbb{P}$. Writing $\omega_q := P_q \omega$ and $u_q := P_q u$, we have $\nabla \cdot \omega_q = 0$, $\nabla \cdot u_q = 0$, $\omega_q = \nabla \times u_q$, and exact shell Bernstein bounds:
   $$k_0^2 2^{2q} \|\omega_q\|_{L^2}^2 \le \|\nabla \omega_q\|_{L^2}^2 < k_0^2 2^{2(q+1)} \|\omega_q\|_{L^2}^2, \qquad k_0^{-1} 2^{-(q+1)} \|\omega_q\|_{L^2} < \|u_q\|_{L^2} \le k_0^{-1} 2^{-q} \|\omega_q\|_{L^2}.$$

---

## 2. Exact Shellwise Vorticity Equation (Section 5)

Starting from the 3D unforced incompressible vorticity equation on $\mathbb{T}_L^3$:
$$\partial_t \omega + (u \cdot \nabla)\omega = (\omega \cdot \nabla)u + \nu \Delta \omega, \qquad \nabla \cdot u = 0, \quad \omega = \nabla \times u,$$
apply the orthogonal projector $P_q$ ($q \in \mathbb{N}_0$) and use $[P_q, \partial_t] = 0$, $[P_q, \Delta] = 0$:
$$\partial_t \omega_q + P_q((u \cdot \nabla)\omega) = P_q((\omega \cdot \nabla)u) + \nu \Delta \omega_q.$$
Taking the $L^2(\mathbb{T}_L^3)$ inner product with $\omega_q = P_q \omega$ and integrating $-\langle \Delta \omega_q, \omega_q \rangle = \|\nabla \omega_q\|_{L^2}^2$ by parts yields the **Exact Shellwise Enstrophy Balance** (`EXACT_IDENTITY`):
$$\boxed{\frac{1}{2}\frac{d}{dt}\|\omega_q\|_{L^2}^2 + \nu \|\nabla \omega_q\|_{L^2}^2 = \mathcal{T}_q + \mathcal{S}_q,}$$
where:
$$\mathcal{T}_q := -\langle P_q(u \cdot \nabla \omega), \omega_q \rangle = -\langle (u \cdot \nabla)\omega, \omega_q \rangle,$$
$$\mathcal{S}_q := \langle P_q(\omega \cdot \nabla u), \omega_q \rangle = \langle (\omega \cdot \nabla)u, \omega_q \rangle.$$

---

## 3. Advective Commutator Structure and Bounds (Section 6)

### 3.1 Exact Commutator Isolation (`EXACT_IDENTITY`)
Decompose the projected advection term by introducing the commutator $[P_q, u \cdot \nabla]\omega := P_q((u \cdot \nabla)\omega) - (u \cdot \nabla) P_q\omega$:
$$P_q((u \cdot \nabla)\omega) = (u \cdot \nabla)\omega_q + [P_q, u \cdot \nabla]\omega.$$
Because $\nabla \cdot u = 0$, the diagonal self-advection of shell $q$ vanishes identically upon integration by parts on $\mathbb{T}_L^3$:
$$\langle (u \cdot \nabla)\omega_q, \omega_q \rangle = \frac{1}{2}\int_{\mathbb{T}_L^3} u_i \partial_i |\omega_q|^2\,dx = -\frac{1}{2}\int_{\mathbb{T}_L^3} (\partial_i u_i)|\omega_q|^2\,dx = 0.$$
Substituting this into $\mathcal{T}_q = -\langle P_q(u \cdot \nabla \omega), \omega_q \rangle$ yields:
$$\boxed{\mathcal{T}_q = -\langle [P_q, u \cdot \nabla]\omega, \omega_q \rangle.}$$

Expanding $\omega = \sum_{p=0}^\infty \omega_p$ and using $\langle (u \cdot \nabla)\omega_q, \omega_q \rangle = 0$ exposes the shell-to-shell advective transfer matrix $T_{q \leftarrow p}^{\rm adv}$:
$$\mathcal{T}_q = \sum_{p=0}^\infty T_{q \leftarrow p}^{\rm adv}, \qquad T_{q \leftarrow p}^{\rm adv} := -\langle (u \cdot \nabla)\omega_p, \omega_q \rangle.$$
By $\nabla \cdot u = 0$, integration by parts gives $\langle (u \cdot \nabla)\omega_p, \omega_q \rangle = -\langle \omega_p, (u \cdot \nabla)\omega_q \rangle$, which proves exact **pairwise skew-symmetry**:
$$\boxed{T_{q \leftarrow p}^{\rm adv} = -T_{p \leftarrow q}^{\rm adv} \quad (\forall p, q \in \mathbb{N}_0), \qquad T_{q \leftarrow q}^{\rm adv} = 0.}$$

### 3.2 Rigorous Norm Bounds on the Advective Commutator (`KNOWN_THEOREM` / `PROVED_LEMMA`)
Using $\nabla \cdot u = 0$, write $(u \cdot \nabla)\omega = \partial_j (u_j \omega)$. In Fourier variables, for $m \in \mathcal{C}_q$ ($k_0 2^q \le |m| < k_0 2^{q+1}$),
$$\widehat{[P_q, u \cdot \nabla]\omega}(m) = \sum_{\substack{k + \ell = m \\ \ell \notin \mathcal{C}_q}} i (m \cdot \widehat{u}(k)) \widehat{\omega}(\ell) = \sum_{\substack{k + \ell = m \\ \ell \notin \mathcal{C}_q}} i (\ell \cdot \widehat{u}(k)) \widehat{\omega}(\ell) \quad (\text{since } k \cdot \widehat{u}(k) = 0).$$
This yields three rigorous bounds depending on the regularity norm applied:
1. **Divergence-Form $L^2$ Commutator Bound**:
   Since $\langle [P_q, u \cdot \nabla]\omega, \omega_q \rangle = \langle (u \cdot \nabla)\omega_{q^c}, \omega_q \rangle = -\langle u \otimes \omega_{q^c}, \nabla \omega_q \rangle$ where $\omega_{q^c} := (I - P_q)\omega$, Hölder's inequality and the sharp shell Bernstein upper bound $\|\nabla \omega_q\|_{L^2} \le k_0 2^{q+1}\|\omega_q\|_{L^2}$ give:
   $$|\mathcal{T}_q| = |\langle [P_q, u \cdot \nabla]\omega, \omega_q \rangle| \le \|u \otimes \omega_{q^c}\|_{L^2} \|\nabla \omega_q\|_{L^2} \le k_0 2^{q+1} \|u\|_{L^\infty} \|(I - P_q)\omega\|_{L^2} \|\omega_q\|_{L^2},$$
   and in $L^2$-norm:
   $$\|P_q [P_q, u \cdot \nabla]\omega\|_{L^2} \le k_0 2^{q+1} \|u\|_{L^\infty} \|(I - P_q)\omega\|_{L^2}.$$
2. **Agmon–Sobolev ($H^1 / H^2$) Commutator Bound**:
   Using Agmon's inequality on $\mathbb{T}_L^3$, $\|u\|_{L^\infty} \le C_{\rm Ag} \|\nabla u\|_{L^2}^{1/2} \|\Delta u\|_{L^2}^{1/2} = C_{\rm Ag} \|\omega\|_{L^2}^{1/2} \|\nabla \omega\|_{L^2}^{1/2}$:
   $$|\mathcal{T}_q| \le C_{\rm Ag} k_0 2^{q+1} \|\omega\|_{L^2}^{1/2} \|\nabla \omega\|_{L^2}^{1/2} \|(I - P_q)\omega\|_{L^2} \|\omega_q\|_{L^2}.$$
3. **Viscous Absorption Bound (Young's Inequality)**:
   Pairing directly against the shell dissipation $\nu \|\nabla \omega_q\|_{L^2}^2$:
   $$|\mathcal{T}_q| \le \|u\|_{L^\infty} \|(I - P_q)\omega\|_{L^2} \|\nabla \omega_q\|_{L^2} \le \frac{\nu}{4}\|\nabla \omega_q\|_{L^2}^2 + \frac{1}{\nu}\|u\|_{L^\infty}^2 \|(I - P_q)\omega\|_{L^2}^2.$$

---

## 4. Conservation and Cancellation Audit (Section 8)

### Proposition 4.1 (Exact Global Advective Cancellation and Stretching Reconstruction — `EXACT_IDENTITY`)
For any smooth divergence-free solution $u \in C^\infty([0, T] \times \mathbb{T}_L^3)$ and the sharp orthogonal projector family $\{P_q\}_{q=0}^\infty$:
1. **Advective Transport Sums Identically to Zero**:
   $$\boxed{\sum_{q=0}^\infty \mathcal{T}_q = 0 \quad \text{(exact equality, without dual-partition error)}.}$$
   *Proof:* Because $\sum_{q=0}^N \omega_q = P_{\le N}\omega \to \omega$ strongly in $H^1(\mathbb{T}_L^3)$ as $N \to \infty$, and $T_{q \leftarrow p}^{\rm adv} = -T_{p \leftarrow q}^{\rm adv}$,
   $$\sum_{q=0}^N \mathcal{T}_q = -\langle (u \cdot \nabla)\omega, P_{\le N}\omega \rangle \xrightarrow{N \to \infty} -\langle (u \cdot \nabla)\omega, \omega \rangle = 0.$$
2. **Stretching Production Sums Identically to Global $P(t)$**:
   $$\boxed{\sum_{q=0}^\infty \mathcal{S}_q = P(t) := \int_{\mathbb{T}_L^3} \omega \cdot S \omega\,dx \quad \text{(exact equality)}.}$$
   *Proof:* At every point $x \in \mathbb{T}_L^3$, decompose $(\nabla u)_{ij} = \partial_j u_i = S_{ij} + \Omega_{ij}$, where $S_{ij} = \frac{1}{2}(\partial_j u_i + \partial_i u_j)$ and $\Omega_{ij} = \frac{1}{2}(\partial_j u_i - \partial_i u_j) = -\frac{1}{2}\epsilon_{ijk}\omega_k$. Then:
   $$[(\omega \cdot \nabla)u]_i = \omega_j \partial_j u_i = (S\omega)_i + \Omega_{ij}\omega_j = (S\omega)_i + \frac{1}{2}(\omega \times \omega)_i = (S\omega)_i.$$
   Thus $(\omega \cdot \nabla)u = S\omega$ pointwise on $\mathbb{T}_L^3$. Consequently, for each shell $q$,
   $$\mathcal{S}_q = \langle (\omega \cdot \nabla)u, \omega_q \rangle = \langle S\omega, \omega_q \rangle,$$
   and summing over $q \in \mathbb{N}_0$ by $L^2$-completeness of $\{P_q\}_{q=0}^\infty$ gives
   $$\sum_{q=0}^\infty \mathcal{S}_q = \left\langle S\omega, \sum_{q=0}^\infty \omega_q \right\rangle = \langle S\omega, \omega \rangle = \int_{\mathbb{T}_L^3} \omega \cdot S \omega\,dx = P(t). \qquad \blacksquare$$

---

## 5. Real Forward Enstrophy Flux Across Cutoff $2^Q$ and Mechanism Split (Sections 9 & 10)

Fix a cutoff shell index $Q \in \mathbb{N}_0$ and write $\omega_{\le Q} := P_{\le Q}\omega$, $\omega_{>Q} := P_{>Q}\omega$. Define low-frequency and high-frequency enstrophy:
$$E_{\le Q}(t) := \frac{1}{2}\|P_{\le Q}\omega(t)\|_{L^2}^2 = \frac{1}{2}\sum_{q=0}^Q \|\omega_q(t)\|_{L^2}^2, \qquad E_{>Q}(t) := \frac{1}{2}\|P_{>Q}\omega(t)\|_{L^2}^2 = \frac{1}{2}\sum_{q=Q+1}^\infty \|\omega_q(t)\|_{L^2}^2.$$

Summing the exact shellwise equation over $q \in \{0, \dots, Q\}$ (and over $q \in \{Q+1, \dots, \infty\}$) gives the **Exact Low/High Enstrophy Balance** (`EXACT_IDENTITY`):
$$\boxed{\frac{d}{dt} E_{\le Q}(t) = -\Pi_Q^{\rm adv}(t) + P_{\le Q}^{\rm stretch}(t) - D_{\le Q}(t) + \mathcal{R}_Q(t),}$$
$$\boxed{\frac{d}{dt} E_{>Q}(t) = +\Pi_Q^{\rm adv}(t) + P_{>Q}^{\rm stretch}(t) - D_{>Q}(t) - \mathcal{R}_Q(t),}$$
where:
1. **Advective Interscale Enstrophy Flux Across $2^Q$ ($\Pi_Q^{\rm adv}$)**:
   $$\boxed{\Pi_Q^{\rm adv}(t) := -\sum_{q=0}^Q \mathcal{T}_q(t) = +\sum_{q=Q+1}^\infty \mathcal{T}_q(t) = -\langle (u \cdot \nabla)\omega_{\le Q}, \omega_{>Q} \rangle = +\langle (u \cdot \nabla)\omega_{>Q}, \omega_{\le Q} \rangle = \langle [P_{\le Q}, u \cdot \nabla]\omega, \omega_{\le Q} \rangle.}$$
   - **Sign Convention**: $\Pi_Q^{\rm adv}(t) > 0$ means net advective transfer of enstrophy **from low frequencies ($\le Q$) into high frequencies ($> Q$)**; $\Pi_Q^{\rm adv}(t) < 0$ means inverse/backward advective transfer from $>Q$ to $\le Q$.
2. **Low-Band and High-Band Stretching Production ($P_{\le Q}^{\rm stretch}, P_{>Q}^{\rm stretch}$)**:
   $$P_{\le Q}^{\rm stretch}(t) := \sum_{q=0}^Q \mathcal{S}_q(t) = \langle S\omega, \omega_{\le Q} \rangle, \qquad P_{>Q}^{\rm stretch}(t) := \sum_{q=Q+1}^\infty \mathcal{S}_q(t) = \langle S\omega, \omega_{>Q} \rangle.$$
3. **Low-Band and High-Band Viscous Dissipation ($D_{\le Q}, D_{>Q}$)**:
   $$D_{\le Q}(t) := \nu \|\nabla P_{\le Q}\omega(t)\|_{L^2}^2 = \nu \sum_{q=0}^Q \|\nabla \omega_q(t)\|_{L^2}^2, \qquad D_{>Q}(t) := \nu \|\nabla P_{>Q}\omega(t)\|_{L^2}^2 = \nu \sum_{q=Q+1}^\infty \|\nabla \omega_q(t)\|_{L^2}^2.$$
4. **Projector Remainder ($\mathcal{R}_Q$)**:
   $$\boxed{\mathcal{R}_Q(t) \equiv 0 \quad \text{identically for sharp orthogonal Fourier projectors } P_q.}$$

---

## 6. Fundamental Operator Split: Skew-Adjoint Advective Transport vs. Self-Adjoint Vortex Stretching (Section 10)

Sections 9 and 10 require a rigorous structural distinction between **Mechanism A (Spectral Transfer)** and **Mechanism B (Vortex Stretching)**.

### Theorem 6.1 (Skew-Adjoint vs. Self-Adjoint Cross-Scale Decomposition — `EXACT_IDENTITY`)
Let $\mathcal{A}_u := u \cdot \nabla$ be the advective transport operator and $\mathcal{M}_S := S\cdot$ be the strain multiplication operator on $L^2(\mathbb{T}_L^3; \mathbb{R}^3)$. Then:
1. **$\mathcal{A}_u^* = -\mathcal{A}_u$ (Skew-Adjointness of Advection)**:
   Because $\nabla \cdot u = 0$, $\langle \mathcal{A}_u f, g \rangle = -\langle f, \mathcal{A}_u g \rangle$ and $\langle \mathcal{A}_u f, f \rangle = 0$. Therefore, in the two-band decomposition $\omega = \omega_{\le Q} + \omega_{>Q}$, the intra-band terms vanish ($\langle \mathcal{A}_u \omega_{\le Q}, \omega_{\le Q} \rangle = \langle \mathcal{A}_u \omega_{>Q}, \omega_{>Q} \rangle = 0$) and the off-diagonal coupling has **opposite signs** in the low and high bands:
   $$-\langle \mathcal{A}_u \omega, \omega_{\le Q} \rangle = -\langle \mathcal{A}_u \omega_{>Q}, \omega_{\le Q} \rangle = -\Pi_Q^{\rm adv}(t), \qquad -\langle \mathcal{A}_u \omega, \omega_{>Q} \rangle = -\langle \mathcal{A}_u \omega_{\le Q}, \omega_{>Q} \rangle = +\Pi_Q^{\rm adv}(t).$$
   Thus $\Pi_Q^{\rm adv}(t)$ is a **purely conservative scale-transfer flux**.
2. **$\mathcal{M}_S^* = +\mathcal{M}_S$ (Self-Adjointness of Vortex Stretching)**:
   Because $S(x,t)^T = S(x,t)$ is symmetric at every $x \in \mathbb{T}_L^3$, $\langle S f, g \rangle = +\langle f, S g \rangle$. Therefore, decomposing $\omega = \omega_{\le Q} + \omega_{>Q}$ splits $P_{\le Q}^{\rm stretch}$ and $P_{>Q}^{\rm stretch}$ into intra-band stretching plus a **symmetric cross-cutoff co-production term** $P_Q^{\rm cross}(t)$ that enters **both** bands with the **same sign**:
   $$P_{\le Q}^{\rm stretch}(t) = \underbrace{\langle S\omega_{\le Q}, \omega_{\le Q} \rangle}_{P_{\le Q}^{\rm intra}(t)} + \underbrace{\langle S\omega_{\le Q}, \omega_{>Q} \rangle}_{P_Q^{\rm cross}(t)},$$
   $$P_{>Q}^{\rm stretch}(t) = \underbrace{\langle S\omega_{>Q}, \omega_{>Q} \rangle}_{P_{>Q}^{\rm intra}(t)} + \underbrace{\langle S\omega_{\le Q}, \omega_{>Q} \rangle}_{P_Q^{\rm cross}(t)},$$
   $$P_{\le Q}^{\rm stretch}(t) + P_{>Q}^{\rm stretch}(t) = P_{\le Q}^{\rm intra}(t) + 2 P_Q^{\rm cross}(t) + P_{>Q}^{\rm intra}(t) = P(t).$$
3. **Total Low-to-High Cross-Cutoff Nonlinear Input ($\Pi_Q^{\omega,\rm tot}$) and Beltrami Annihilation**:
   Combining the conservative advective transfer $\Pi_Q^{\rm adv}(t) = -\langle (u \cdot \nabla)\omega_{\le Q}, \omega_{>Q} \rangle$ with the cross-cutoff stretching transfer $P_Q^{\rm cross}(t) = \langle (\omega_{\le Q}\cdot \nabla)u, \omega_{>Q} \rangle$ yields the total nonlinear rate at which low-frequency vorticity $\omega_{\le Q}$ feeds high-frequency vorticity $\omega_{>Q}$:
   $$\boxed{\Pi_Q^{\omega,\rm tot}(t) := \Pi_Q^{\rm adv}(t) + P_Q^{\rm cross}(t) = \langle -(u \cdot \nabla)\omega_{\le Q} + (\omega_{\le Q}\cdot\nabla)u, \omega_{>Q} \rangle = \langle \nabla \times (u \times \omega_{\le Q}), \omega_{>Q} \rangle.}$$
   Then the high-mode enstrophy evolution is governed by:
   $$\frac{d}{dt} E_{>Q}(t) + D_{>Q}(t) = \Pi_Q^{\omega,\rm tot}(t) + P_{>Q}^{\rm intra}(t) = \Pi_Q^{\rm adv}(t) + P_Q^{\rm cross}(t) + P_{>Q}^{\rm intra}(t).$$
   Moreover, on **every single-eigenvalue Beltrami/ABC flow** ($\omega = \lambda u$), $(u \cdot \nabla)\omega = (\omega \cdot \nabla)u = \lambda \nabla(|u|^2/2)$ is a pure gradient, which is $L^2$-orthogonal to every divergence-free shell $\omega_q$. Hence on all single-eigenvalue Beltrami/ABC flows:
   $$\boxed{\mathcal{T}_q \equiv 0, \quad \mathcal{S}_q \equiv 0, \quad \Pi_Q^{\rm adv}(t) \equiv 0, \quad P_Q^{\rm cross}(t) \equiv 0, \quad \Pi_Q^{\omega,\rm tot}(t) \equiv 0 \qquad (\forall q, Q \in \mathbb{N}_0).}$$
