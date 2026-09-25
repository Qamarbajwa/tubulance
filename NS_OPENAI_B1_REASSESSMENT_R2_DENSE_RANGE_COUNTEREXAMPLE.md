# Dense Range of the Heat Semigroup: Counterexample to Unrestricted Q2 No-Go

**Programme**: `OPENAI_NAVIER_STOKES_UNFORCED_TRANSFER`  
**Milestone**: `NS-OPENAI-B1-REASSESSMENT-R2`  
**Active Governance**: `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Mathematical Authority**: `Mathematical Research Constitution v1.0.1`  
**Classification**: `PROSPECTIVE_CORRECTION`  
**Corrects**: R1 Three Questions document, Q2 verdict

---

## 1. The R1 Q2 Claim Under Examination

The R1 synthesis report (`NS_OPENAI_B1_REASSESSMENT_R1_SYNTHESIS_REPORT.md`) declared:

> **Q2: Approximate Profile Reachability — Status: NO-GO (Proved)**

This section demonstrates that the R1 Q2 verdict, as literally stated, is **mathematically incorrect** for the pure-heat operator. The error is conflating *existence* of an approximation with *bounded cost* of the approximation.

---

## 2. Theorem: Dense Range of the Heat Semigroup

**Theorem 2.1 (Dense Range)**:  
Let $\nu > 0$, $t > 0$. The range of the heat semigroup $e^{\nu t \Delta}$ is **dense** in $L^2(\mathbb{T}^3)$.

**Proof**:  
Let $W^\star \in L^2(\mathbb{T}^3)$ be arbitrary, with Fourier expansion:
$$W^\star(x) = \sum_{k \in \mathbb{Z}^3} \widehat{W^\star}(k) \, e^{ik \cdot x}.$$

For each integer cutoff $K \geq 1$, define the frequency-truncated target:
$$W_K(x) \equiv P_{\leq K} W^\star(x) = \sum_{|k| \leq K} \widehat{W^\star}(k) \, e^{ik \cdot x}.$$

**Step 1 — $W_K$ is in the exact semigroup range.**  
Since $W_K$ has finitely many non-zero Fourier modes, define:
$$w_0^{(K)}(x) = \sum_{|k| \leq K} \widehat{W^\star}(k) \, e^{\nu t |k|^2} \, e^{ik \cdot x}.$$
Then $w_0^{(K)} \in C^\infty(\mathbb{T}^3)$ (it is a trigonometric polynomial), and:
$$e^{\nu t \Delta} w_0^{(K)}(x) = \sum_{|k| \leq K} \widehat{W^\star}(k) \, e^{\nu t |k|^2} \, e^{-\nu t |k|^2} \, e^{ik \cdot x} = \sum_{|k| \leq K} \widehat{W^\star}(k) \, e^{ik \cdot x} = W_K(x).$$

So $e^{\nu t \Delta} w_0^{(K)} = W_K$ **exactly**.

**Step 2 — $W_K \to W^\star$ in $L^2$.**  
By Parseval's theorem:
$$\|W^\star - W_K\|_{L^2}^2 = \sum_{|k| > K} |\widehat{W^\star}(k)|^2 \to 0 \quad \text{as } K \to \infty,$$
since $W^\star \in L^2$ implies $\sum_k |\widehat{W^\star}(k)|^2 < \infty$.

**Step 3 — Conclusion.**  
For every $\varepsilon > 0$, choose $K$ large enough that $\|W^\star - W_K\|_{L^2} \leq \varepsilon$. Then $W_K = e^{\nu t \Delta} w_0^{(K)} \in \operatorname{Range}(e^{\nu t \Delta})$ and $\|W_K - W^\star\|_{L^2} \leq \varepsilon$.  
$\square$

---

## 3. What R1 Got Wrong

The R1 Q2 verdict conflates two distinct statements:

| Statement | Mathematical Content | Truth Value |
|-----------|---------------------|-------------|
| **Q2-existence** | $\exists w_0 : \|e^{\nu t \Delta} w_0 - W^\star\|_{L^2} \leq \varepsilon$ | **TRUE** (Theorem 2.1) |
| **Q2-bounded-cost** | $\exists w_0$ with $\|w_0\|_{L^2} \leq M$ such that $\|e^{\nu t \Delta} w_0 - W^\star\|_{L^2} \leq \varepsilon$ | **Depends on $M$ and $W^\star$** |

The R1 document stated Q2 = NO-GO, but what it actually proved was Q2-bounded-cost = NO-GO for a specific cost bound. The existence of an $L^2$-approximation is trivially guaranteed by the dense range.

### 3.1 The Cost of the Counterexample

The initial norm of $w_0^{(K)}$ is:
$$\|w_0^{(K)}\|_{L^2}^2 = \sum_{|k| \leq K} |\widehat{W^\star}(k)|^2 \, e^{2\nu t |k|^2}.$$

For a generic $W^\star \in L^2 \setminus \operatorname{Range}(e^{\nu t \Delta})$ (e.g. one with compact spatial support), this grows **without bound** as $K \to \infty$:
$$\|w_0^{(K)}\|_{L^2} \to +\infty.$$

But for each **fixed** $K$, $\|w_0^{(K)}\|_{L^2} < \infty$. The cost is large but always finite.

---

## 4. Corrected Q2 Framework

The properly stated Q2 question must include a cost constraint:

**Q2-corrected**: For a given $\varepsilon > 0$ and target $W_j^\star$, define the **minimum realization cost**:
$$\mathfrak{C}_\varepsilon(W_j^\star) \equiv \inf \left\{ \|w_0\|_{L^2} : \|\mathcal{U}(t_j, 0) w_0 - W_j^\star\|_{L^2} \leq \varepsilon \right\}.$$

The correct obstruction question is:

$$\boxed{\text{Does } \mathfrak{C}_\varepsilon(W_j^\star) \text{ remain bounded as } j \to \infty \text{ for any } \varepsilon > 0?}$$

- If $\mathfrak{C}_\varepsilon \to \infty$ for every $\varepsilon > 0$, then Q2-bounded-cost is genuinely obstructed.
- If $\mathfrak{C}_\varepsilon$ remains bounded for some $\varepsilon > 0$, then the barrier is merely a cost issue, not a structural impossibility.
- The R1 argument shows that $\mathfrak{C}_\varepsilon(W_j^\star)$ diverges **super-exponentially** as $j \to \infty$ for the compactly-supported OpenAI pulse targets — but this is a **cost divergence**, not a non-existence claim.

---

## 5. What Survives from R1

The following R1 results remain valid:

1. **Q1 exact compact no-go**: Compactly supported $W^\star \notin \operatorname{Range}(e^{\nu t \Delta})$. ✓ Correct.
2. **Gramian eigenvalue computation**: $\lambda_1 \asymp \nu 2^{-j(1+h)}$, $\lambda_\perp \asymp \nu 2^{-j(1+h)} e^{2 \cdot 2^{jh}}$. ✓ Correct for the affine benchmark.
3. **Spectral leakage lower bound**: $\delta_j \to 1$ for compactly supported targets. ✓ Correct.
4. **Cost divergence**: $\mathfrak{C}_\varepsilon(W_j^\star) \geq \exp(+c \exp(2^{jh}))$. ✓ Correct as a cost lower bound.

What does **not** survive:
- The unrestricted claim "Q2 = NO-GO (Proved)" interpreted as non-existence of any approximation.
- The conclusion that approximate reachability is impossible. It is possible; it is merely super-exponentially expensive.

---

## 6. Epistemic Classification

| Original R1 Claim | Corrected Status |
|---|---|
| Q2: NO-GO (Proved) | Q2-existence: OPEN_TRIVIALLY_TRUE. Q2-bounded-cost: SUPER-EXPONENTIAL_DIVERGENCE_PROVED |
| "Approximate Profile Reachability impossible" | **RETRACTED**. Approximate reachability exists; cost diverges. |
| CLM-038 scope | Must be narrowed to a COST BARRIER, not an EXISTENCE BARRIER |
