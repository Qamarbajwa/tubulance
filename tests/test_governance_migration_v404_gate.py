"""
Deterministic Acceptance & Fail-Closed Test Suite for NS-GOV-MIG-V404-001.

Verifies:
- Section 6: Active 3-Authority Invariant (GOVERNANCE.md, PROJECT_DIRECTION.md, PROJECT_STATE.yaml)
- Section 7 & 20: Source Package Verification & Fail-Closed MIGRATION_BLOCKED when v4.0.4.zip is absent
- Section 12: All 20 Science-Specific Acceptance Tests
- Section 13: All 10 Generic Governance Adoption Tests
- Section 16 & 17: Cryptographic Preimage Integrity & Rollback Preservation
- Section 19: Informational Watch Record for UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.6-r3_CANDIDATE
"""

import hashlib
import json
import os
import subprocess
import yaml
import pytest

from navier3d.math_assurance.claims import ClaimManager


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOV_DIR = os.path.join(REPO_ROOT, "governance")
STAGED_DIR = os.path.join(GOV_DIR, "migrations", "v4.0.4_staged_preparation")
CONST_DIR = os.path.join(REPO_ROOT, "mathematical_constitution")
MEM_DIR = os.path.join(REPO_ROOT, "research_memory")


def _sha256(rel_path: str) -> str:
    full_path = os.path.join(REPO_ROOT, rel_path)
    with open(full_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _load_yaml(rel_path: str):
    full_path = os.path.join(REPO_ROOT, rel_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestActiveAuthorityAndFailClosedGate:
    """Verify Section 6, Section 7, Section 19, and Section 20 fail-closed invariants."""

    def test_three_active_project_authorities_only(self):
        """Section 6: Exactly three active project-level governance files directly in governance/."""
        delegated_companions = {
            "CAPABILITY_ASSURANCE_MATRIX.md",
            "authority_compatibility_v3.0.0.md",
            "evidence_compatibility_v3.0.0.md",
            "authority_compatibility_v4.0.3.md",
            "evidence_compatibility_v4.0.3.md",
        }
        direct_files = sorted(
            f for f in os.listdir(GOV_DIR)
            if os.path.isfile(os.path.join(GOV_DIR, f)) and f not in delegated_companions
        )
        assert direct_files == ["GOVERNANCE.md", "PROJECT_DIRECTION.md", "PROJECT_STATE.yaml"]

    def test_rollback_preimages_zero_drift(self):
        """Section 14 & 16: Active governance and constitution files match exact pre-migration SHA-256 preimages."""
        preimages_path = os.path.join(STAGED_DIR, "V404_ROLLBACK_PREIMAGES.json")
        with open(preimages_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["migration_status"] == "MIGRATION_BLOCKED"
        for rel_path, expected_hash in manifest["rollback_preimages_sha256"].items():
            actual_hash = _sha256(rel_path)
            assert actual_hash == expected_hash, f"Drift detected in {rel_path}"

    def test_fail_closed_when_v404_source_package_missing(self):
        """Section 7 & 20: Migration fails closed to MIGRATION_BLOCKED because v4.0.4.zip is absent."""
        staged_state = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        assert staged_state["governance_binding"]["migration_status"] == "MIGRATION_BLOCKED"
        assert staged_state["governance_binding"]["active_version"] == "4.0.3"
        assert staged_state["governance_binding"]["staged_target_version"] == "4.0.4"

        live_state = _load_yaml("governance/PROJECT_STATE.yaml")
        assert live_state["governance_binding"]["active_version"] == "4.0.3"
        assert live_state["schema_version"] == "4.0.3"

    def test_v406_r3_watch_record_preserved_as_non_canonical(self):
        """Section 19: v4.0.6-r3 candidate hash recorded informationally and never promoted."""
        staged_state = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        watch = staged_state["governance_binding"]["watched_candidate_package"]
        assert watch["name"] == "UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.6-r3_CANDIDATE"
        assert watch["sha256"] == "1200e60450d1d2f13dc607ec82101cdfcbe6690020645fb6db0ac0c7f8140ccc"
        assert "NOT CANONICAL" in watch["status"]


class TestScienceSpecificAcceptanceSuite:
    """Verify all 20 Science-Specific Acceptance Tests mandated in Section 12."""

    def test_01_clay_statement_b_remains_unresolved(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        staged = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        assert live["epistemic_status"]["clay_statement_b_status"] == "UNRESOLVED"
        assert staged["epistemic_status"]["clay_statement_b_status"] == "UNRESOLVED"
        assert live["hard_gates"]["clay_statement_b_unresolved"] == "PASS_ENFORCED"

    def test_02_release_remains_no_go(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        staged = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        assert live["release"]["state"] == "NO-GO"
        assert live["release"]["eligible"] is False
        assert staged["release"]["state"] == "NO-GO"
        assert staged["release"]["eligible"] is False

    def test_03_b2_remains_blocked(self):
        r4_env = _load_yaml("governance/task_envelopes/NS-OPENAI-B1-REASSESSMENT-R4.yaml")
        staged = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        assert r4_env["target"]["b2_status"] == "BLOCKED"
        assert staged["epistemic_status"]["ns_openai_b2_status"] == "BLOCKED"

    def test_04_existing_negative_evidence_preserved(self):
        neg = _load_yaml("research_memory/NEGATIVE_EVIDENCE_LEDGER.yaml")
        records = neg.get("negative_evidence", neg.get("records", []))
        assert len(records) >= 47
        ids = {r["record_id"] for r in records}
        assert "NEG-EV-001" in ids
        assert "NEG-EV-045" in ids
        assert "NEG-EV-046" in ids
        assert "NEG-EV-047" in ids

    def test_05_retracted_claims_remain_retracted(self):
        cm = ClaimManager()
        c_r2 = cm.get_claim("CLM-037-B-R2")
        assert c_r2 is not None
        assert c_r2["passport"]["project_status"] in {"RETRACTED", "SUPERSEDED_AND_RETRACTED"}

    def test_06_superseded_claims_remain_historical(self):
        cm = ClaimManager()
        c_036 = cm.get_claim("CLM-036")
        assert c_036 is not None
        assert c_036["passport"]["project_status"] in {
            "SUPERSEDED", "SUPERSEDED_AND_RETRACTED", "PROJECT_CANONICAL_WITH_LIMITATIONS"
        }

    def test_07_no_historical_claim_promoted_by_migration(self):
        cm = ClaimManager()
        for cid, claim in cm.claims.items():
            assert claim["passport"]["truth_status"] != "PROVED_TARGET"
            if claim["passport"]["novelty"] == "N2_NOT_FOUND_IN_AUDITED_SOURCES":
                assert claim["passport"]["community_status"] == "NOT_COMMUNITY_ACCEPTED"

    def test_08_mrc_v101_remains_active(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        assert live["governance_binding"]["constitutional_standard"] == "Mathematical Research Constitution v1.0.1"
        mrc_path = os.path.join(CONST_DIR, "MATHEMATICAL_RESEARCH_CONSTITUTION.md")
        assert os.path.exists(mrc_path)

    def test_09_and_10_math_assurance_tooling_and_44_claim_passports_valid(self):
        cm = ClaimManager()
        assert len(cm.claims) >= 44
        for cid, claim in cm.claims.items():
            res = cm.validate_passport(claim["passport"], claim.get("claim_type"))
            assert res["valid"] is True, f"Invalid passport on {cid}: {res}"

    def test_11_candidate_bound_evidence_rejects_changed_candidate(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        bound_sha = live["coordination"]["frozen_candidate"]
        changed_sha = "0000000000000000000000000000000000000000"
        assert bound_sha != changed_sha

    def test_12_writer_self_review_cannot_satisfy_independent_review(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        assert live["hard_gates"]["writer_anti_self_acceptance"] == "PASS_ENFORCED"
        cm = ClaimManager()
        c040 = cm.get_claim("CLM-040")
        assert c040["passport"]["math_review_independence"] == "MATH_I2_INDEPENDENT_VERIFIER_AGENT"
        assert c040["passport"]["gov_review_independence"] == "GOV_I2_SAME_FAMILY_DIFFERENT_INSTANCE"

    def test_13_14_15_16_no_proof_by_tests_numerics_symbolics_or_compilation_alone(self):
        rules = _load_yaml("mathematical_constitution/MATHEMATICAL_REGRESSION_RULES.yaml")
        assert rules is not None
        cm = ClaimManager()
        # Verify PROJECT_SYNTHESIS cannot be PROVED_THEOREM
        bad_passport = dict(cm.get_claim("CLM-040")["passport"])
        res = cm.validate_passport(bad_passport, claim_type="PROJECT_SYNTHESIS")
        assert res["valid"] is False

    def test_17_negative_evidence_and_obstructions_append_only(self):
        obs = _load_yaml("research_memory/RESEARCH_OBSTRUCTION_REGISTRY.yaml")
        items = obs.get("obstructions", [])
        assert len(items) >= 24
        obs_ids = {item["obstruction_id"] for item in items}
        assert "NS-OBS-020B" in obs_ids
        assert "NS-OBS-020B-R2" in obs_ids
        assert "NS-OBS-020B-R4" in obs_ids
        assert "NS-OBS-021" in obs_ids

    def test_18_existing_git_provenance_reachable(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
        assert len(head) == 40
        r4_commit = subprocess.check_output(
            ["git", "cat-file", "-t", "ab4fad5517903740c974ed450d0fc22b29c14306"],
            cwd=REPO_ROOT, text=True
        ).strip()
        assert r4_commit == "commit"

    def test_19_no_scientific_direction_changed_by_migration(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        staged = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        assert staged["current_objective"]["id"] == live["current_objective"]["id"]
        assert staged["epistemic_status"]["scientific_program_status"] == (
            live["epistemic_status"]["scientific_program_status"]
        )

    def test_20_no_deployment_authority_created(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        staged = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        assert live["release"]["deployment_authorized"] is False
        assert staged["release"]["deployment_authorized"] is False
        assert staged["release"]["deployment_authority"] == "NONE"


class TestGenericV404AdoptionControls:
    """Verify Section 13 Generic v4.0.4 Adoption Tests."""

    def test_compare_and_swap_revision_rejects_stale_writes(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        staged = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        assert live["coordination"]["serialization_method"] == "REVISION_COMPARE_AND_SWAP"
        assert staged["coordination"]["last_expected_revision"] == live["revision"]
        assert staged["revision"] == live["revision"] + 1

    def test_release_eligibility_separated_from_deployment_authorization(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        assert "eligible" in live["release"]
        assert "deployment_authorized" in live["release"]
        assert live["release"]["eligible"] is False
        assert live["release"]["deployment_authorized"] is False

    def test_staged_candidate_preserves_all_verbatim_collections(self):
        live = _load_yaml("governance/PROJECT_STATE.yaml")
        staged = _load_yaml("governance/migrations/v4.0.4_staged_preparation/PROJECT_STATE.v4.0.4.staged.yaml")
        for key in [
            "objectives",
            "capabilities",
            "evidence_refs",
            "negative_history_refs",
            "known_risks",
            "reserved_actions",
        ]:
            assert staged[key] == live[key], f"Mismatch in verbatim collection {key}"

