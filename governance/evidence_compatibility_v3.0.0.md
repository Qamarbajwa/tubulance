# Evidence Compatibility Map — v2.10.1/MRC to v3.0.0

v3 adds operational dimensions; it does not numerically reinterpret historical evidence labels.

| Historical namespace | Historical meaning | v3 treatment |
|---|---|---|
| `GOV_E*` | Governance evidence strength under v2 | Preserve in historical receipts; cite from new v3 receipts where relevant. |
| `MATH_E*` | Mathematical evidence strength under MRC | Preserve in Claim Passports; do not replace with operational `E*`. |
| `GOV_I*` | Governance independence/verification semantics | Preserve historically; record new v3 `IND0`–`IND3` independently. |
| `MATH_I*` | Mathematical independence/validation semantics | Preserve in the Mathematical Research Constitution layer. |
| v3 `E1`–`E5` | Operational evidence strength | New receipts only; E4/E5 require corresponding provenance. |
| v3 `ENVIRONMENT` | Reality/environment class | Required in new receipts; mock/simulated/local evidence is not live proof. |
| v3 `IND0`–`IND3` | Independence class | Required in new receipts; this migration records IND1, not IND2/IND3. |
| Candidate identity | Exact Git/artifact/state binding | Required for acceptance-relevant v3 evidence; stale evidence fails closed. |

The migration preserves the current remote state: local checkpoints are accepted, remote replication is blocked by external-destination review, and remote SHA is unverified.
