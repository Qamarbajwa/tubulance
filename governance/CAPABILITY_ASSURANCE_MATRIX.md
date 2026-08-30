# Capability Assurance Matrix — v3 migration scope

This project is a mathematical research program, not a product release candidate. The migration scope is limited to operational governance state and does not certify Navier–Stokes mathematics, publication readiness, community acceptance, or deployment.

| Requirement | Intent fidelity | Implementation conformance | Evidence | State |
|---|---|---|---|---|
| `GOV-V3-MIGRATION` | Preserve project intent, MRC v1.0.1, accepted A2, negative evidence, and remote truth | v3 state/envelope/receipt schemas, packet manifest checks, and conformance tests | `governance/evidence/NS-GOV-MIG-V300-001-packet.json` plus migration receipt | `ACCEPTED_WITH_DECLARED_LIMITATIONS` |

Known limitation: only IND1 fresh-context/system verification is available in this environment; no IND2/IND3 claim is made.
