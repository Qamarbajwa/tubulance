# Source Package Inventory: Universal Governance Minimal v4.0.3

**Distribution Package:** `UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3`  
**Archive Source:** `D:\Comfy UI\idea memory\obsidian brains\Coding language\master prompts\UNIVERSAL_GOVERNANCE_MINIMAL_v4.0.3.zip`  
**Archive SHA-256:** `FE57DB5BD07E8A422283E5908599907736A670E5375342EC104C667F7B80E0FB`  
**Staging Directory:** `governance/packet/v4.0.3/`  
**Integrity Verification:** `PASS (8/8 files matching MANIFEST.sha256.json)`  

---

## 1. Archived Distribution Files and SHA-256 Hashes

The distribution staging directory `governance/packet/v4.0.3/` contains 9 physical files in total:
- 1 manifest metadata file: `MANIFEST.sha256.json` (the cryptographic root of trust)
- 8 payload and tooling files explicitly indexed and hashed within `MANIFEST.sha256.json`.

All 8 indexed files were verified using Node.js crypto against `MANIFEST.sha256.json`:


| File Path | Byte Size | SHA-256 Checksum | Operational Role in v4.0.3 |
|---|---|---|---|
| `ADOPTION_PROMPT.md` | 3,852 | `100438c7159cb030a514d86b9ea20aeebaa8d5ef66432b40fecefdc6cbdd3f49` | Copyable bounded adoption instructions and migration contract |
| `EVIDENCE_AND_MIGRATION.md` | 5,850 | `a4929c29e612f0f85806653e1a0694f420e6f6631e5f80ba13203f193f608759` | Delegated evidence dimensions (E1–E5), receipt schema, and 12 state-transition tests |
| `README.md` | 4,252 | `f3ee9fa5580004ff97bcfe4965df6e3b52d9a9cb256b823e20e8b6b1fcb4e339` | Package introduction, release notes (v4.0.1 -> v4.0.3), authority entry point definitions |
| `governance/GOVERNANCE.md` | 19,944 | `085437882e7e3bf73770e0f3b0e3be538466100236a2818fdf7d1bb3972620dc` | Universal operational rules (Sections 1–12) and Section 13 project binding template |
| `governance/PROJECT_DIRECTION.md` | 4,418 | `7251ea73fb9873a4b6b66804bb7ae67b36f75347f98ee52bb0ee614995f9c4bf` | Intended scope, contracts, architecture, and delegated technical source map |
| `governance/PROJECT_STATE.yaml` | 1,702 | `00ff14a27320b92db9822a578a8bc5bf1a50c6bf23d42e20ff36b0cfa0b86a87` | Inactive template for live state, revision tracking, and hard gates |
| `tools/verify-package.mjs` | 2,481 | `8638ae6085a66a1a72d7f872ae3ee3b290cb6e4c76b92750e3262fa22e118991` | Standalone deterministic package manifest verifier |
| `tools/verify-package.test.mjs` | 2,086 | `cbdd9908cf67b2d56e793d508930fae3ee3165b4ee3c23945c71d2bfe603cf36` | Conformance test suite for distribution integrity |

---

## 2. Verification Execution

Execution of the distribution tools produced:
1. `node tools/verify-package.mjs`:
   ```
   INTEGRITY PASS: 8 files. Not project acceptance or authenticity proof.
   ```
2. `node tools/verify-package.test.mjs`:
   ```
   ✔ valid package (3.7ms)
   ✔ reject changed bytes (3.2ms)
   ✔ reject unlisted files (2.8ms)
   ✔ reject parent traversal (2.9ms)
   ✔ reject case-insensitive duplicate paths (3.2ms)
   ✔ reject missing files (2.0ms)
   ✔ reject malformed digest (1.7ms)
   ✔ reject unknown version (1.7ms)
   ℹ tests 8, pass 8, fail 0
   ```

---

## 3. Preservation Invariant

The original distribution in `governance/packet/v4.0.3/` is sealed and preserved verbatim. Project-specific bindings are authored strictly in the active repository locations (`governance/GOVERNANCE.md`, `governance/PROJECT_DIRECTION.md`, `governance/PROJECT_STATE.yaml`).
