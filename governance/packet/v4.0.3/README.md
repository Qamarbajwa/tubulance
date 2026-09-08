# Universal Governance Minimal v4.0.3 — owner-requested revision

Reusable, project-neutral revision prepared on 2026-09-07 from the supplied v4.0.1 packet. This is a new candidate distribution, not an upstream-certified release or independently accepted project migration.

## Use

1. Keep the original package unchanged. Extract this package into a new, non-active staging directory in the target project.
2. With Node.js 18 or newer, run `node tools/verify-package.mjs` from that directory. It checks packaging integrity, not correctness or acceptance.
3. Read `ADOPTION_PROMPT.md`. Give that prompt to the project's authorized implementation agent, together with the actual project path and owner authorization to prepare a bounded adoption candidate.
4. Customize the three templates from actual project sources. Preserve existing stronger rules, independent gates, product specifications, failures and release restrictions. Never copy another project's names, ports, model assignments or statuses.
5. Obtain required independent review and acceptance before activating the project-bound candidate. Each project needs its own binding and evidence; acceptance in one project transfers to none of the others.

## Contents and authority

- `governance/GOVERNANCE.md`: universal HOW plus the project's explicit operating binding.
- `governance/PROJECT_DIRECTION.md`: project WHAT/WHY, contracts, architecture and delegated specifications.
- `governance/PROJECT_STATE.yaml`: live state template, deliberately unbound and inactive.
- `ADOPTION_PROMPT.md`: bounded migration instructions; not automatically executable authority.
- `EVIDENCE_AND_MIGRATION.md`: delegated receipt/transition contract, read when implementing validators or migration.
- `tools/verify-package.mjs`, its tests and `MANIFEST.sha256.json`: distribution integrity support, not additional operational authorities.

The three operational files are the entry point, not a requirement to squeeze design specifications, code, tests or evidence into three giant files. Technical sources retain narrowly delegated roles. Existing bridge files point to the same active authority rather than duplicate it.

## Changes from v4.0.1

### v4.0.3 UI-system refinement (builds on preserved v4.0.2)

- Explicit tokens-to-journeys hierarchy and reuse → compose → extend → create rule.
- Applicable component variants/states, naming/ownership, content variability and concise usage/setup documentation.
- Minimum journey-driven foundations rather than speculative exhaustive UI-kit work.
- Role-specific surfaces and evidence-backed responsive/accessibility/failure-state coverage.
- Project-specific frameworks, brand/style/device choices remain in Direction; no fourth UI-governance authority.
- These are governance requirements, not a generated UI kit or proof of product readiness. Earlier v4.0.2 files and ZIP remain unchanged.

### Retained v4.0.2 improvements

- Explicit non-self-acceptance, configurable qualified roles, stronger inherited gate preservation, independent review of governance cutover.
- Safe staged migration and rollback instead of automatic broad archive moves.
- Versioned evidence semantics and exact candidate/environment/provenance binding.
- Single state-write ownership, revision checks and review freeze requirements.
- Retained detailed design/workflow specifications and bidirectional UI/backend verification.
- Measurable 10% routine governance-writing target, with honest exceptions and no weakened safety gates.
- Preserved NO-GO, unknowns, failed evidence and project-specific prohibited actions.
- Portable integrity checker and negative tests; no installer, database operation or automatic activation.

Source ZIP SHA-256: `C04A81EEF2B102030A3DC332E765890BAE856A0368834DE71BCD58B70058FC3D`.

## Limits

These instructions are not an enforcement service, browser, reviewer, supervisor or scheduler. The target project must connect its actual agents and checks. Passing the supplied package checker proves neither product behavior nor visual fidelity, review independence, safe deployment or governance conformance. The manifest detects accidental changes; without a trusted external checksum/signature it does not establish publisher authenticity.
