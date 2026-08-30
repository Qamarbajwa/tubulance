# Authority Compatibility Map — v2.10.1 to v3.0.0

Historical labels remain historical. This table records their operational meaning for new v3 work without rewriting old receipts or acceptance decisions.

| Legacy concept or field | Meaning established in this project | v3 authority/state | Migration rule |
|---|---|---|---|
| `acceptance_authority` | Historical acceptance of bounded scientific increments | `VERIFICATION_AUTHORITY` plus explicit technical acceptance | Does not imply mathematical truth or release eligibility. |
| `owner approval` for technical work | Not found as an active owner queue item | `IMPLEMENTATION_AUTHORITY` under standing mandate | Routine eligible technical work does not require owner certification. |
| `human acceptance` | Historical review/acceptance wording | `TECHNICAL_ACCEPTANCE` only when candidate-bound evidence supports it | Never promotes a theorem or release state. |
| `approved` / `accepted` | Context-dependent historical labels | Typed state recorded by task, evidence, release, or deployment domain | No generic `approved: true` field is used in v3 state. |
| `release GO` | No current product-release authorization identified | `RELEASE_ELIGIBILITY_AUTHORITY` or `DEPLOYMENT_AUTHORITY` | Release eligibility is evidence-derived; deployment remains separately reserved. |
| `owner release SHA` | Not found | Machine-derived candidate identity | Owner does not certify candidate identity. |
| `technical authorization` | Historical governance dispatch language | `IMPLEMENTATION_AUTHORITY` | Technical sequencing derives from intent, dependencies, risk, and evidence. |
| Clay Statement B status | Scientific-domain status | Mathematical Research Constitution v1.0.1 | Remains `UNRESOLVED`; no project governance state can promote it. |
