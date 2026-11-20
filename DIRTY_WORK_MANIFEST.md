# DIRTY WORK MANIFEST & BASELINE SNAPSHOT

**Program:** `NS-TRAJECTORY-PERSISTENCE-2`  
**Gate:** `TP2-G3-E4 (Independent Verification & Correction Audit)`  
**Governance Standard:** Autonomous Project Governance v2.9.3  
**Date:** 2026-08-24T11:04:00Z  

---

## 1. Git Repository State

- **Branch**: `main`
- **Base Commit SHA**: `2e9a4fb5dd6ddc5ec377328f9387c16acab1fe5f`
- **Tree Status**: Uncommitted candidate and verification artifacts present in working tree; no unrelated pre-existing dirty work corrupted.

---

## 2. Tracked vs Untracked Candidate Artifacts

All TP2 artifacts in the workspace are explicitly inventoried:

| Category | Artifact Path | SHA-256 Checksum | Purpose |
|---|---|---|---|
| **Candidate G3** | `TP2_G3_BACKWARD_ITO_DERIVATION.md` | `8f5914386955e2fece715ab4af2760d74c2bd7e92b9cef20e307b8d52a947ae5` | Worker derivation |
| **Candidate G3** | `TP2_G3_FORWARDIZED_MARTINGALE_CONTRACT.md` | `e55bfbb48fe2b9555e38ed4b7004e32fafb26eaa0fde6f7e9a6794c6c384c0c0` | Time-reversal SDE |
| **Candidate G3** | `TP2_G3_COVARIANCE_TENSOR_IDENTITY.md` | `c1d2504fe437c7569bc37383b90f1e201481a7b34583a008d84a5c407336b8bb` | Covariance equation |
| **Candidate G3** | `TP2_G3_VARIANCE_BUDGET.md` | `06d41758a0282f29ecf67e6e7b8a2e595f6ac7c49780c7209aa9180b5cdcd7dc` | Trace variance |
| **Candidate G3** | `TP2_G3_CHI_EVOLUTION.md` | `73985f56b2d63a84f9ad744346d221a92a288cce985d65b24aa87f90836f4e17` | Chi evolution |
| **Candidate G3** | `TP2_G3_SCALING_AUDIT.md` | `2098362f4472bb9ada49bdc177cc5757f84b122ec3b5507d486c995adbe3a564` | Scaling audit |
| **Candidate G3** | `TP2_G3_COUNTEREXAMPLE_LEDGER.md` | `543b976129664f5b4e836a7f0891fec372b804092237568447b3c614b98a53c4` | Couette example |
| **Candidate G3** | `TP2_G3_FINAL_REVIEW_PACKET.md` | `2b8921a5ab5e8b71bef870b5676c29794477a3e09c80d43e47ae891318f6268d` | Worker packet |
| **Candidate G3 Test** | `tests/test_tp2_g3_suite.py` | `90c83244e4cc7c1d55de846fe7fae58c58efb8d3e6bc48a41d36058241faa78e` | 9 worker unit tests |
| **Verifier Test** | `tests/test_tp2_g3_verifier_suite.py` | `9b5a0fb70be31bb0b6c68b6cf3dc4f8f01b54b2efc8fca3cfb2e67df146d9bfe` | 14 verifier tests (T1-T14) |
