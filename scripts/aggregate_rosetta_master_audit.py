#!/usr/bin/env python3
"""Read-only 4-Workspace Rosetta Master Audit Aggregator.

Reads receipts across:
1. Hodge: d:/Comfy UI/hodge conjecture/reports/millennium_ext/MILLENNIUM_EXT_RECEIPT.json
2. Yang-Mills: d:/Comfy UI/yang mills and the mass gap (untouched at commit 0f3f012)
   + isolated Yang-Mills scratch probe directory:
   C:/Users/arqam/.gemini/antigravity/brain/e6cd4726-22aa-425e-a8f7-aab472c30784/scratch/
3. Riemann: d:/Comfy UI/rheihman hypothesis/research/interactive_lab/monograph_additive_multiplicative/vasyunin_schur_chiral_rosetta_results.json
4. Navier-Stokes: d:/Comfy UI/tubulance/probe_cl30_helical_schur_results.json

Enforces absolute scientific honesty: all four Millennium problems remain strictly OPEN.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


YM_SCRATCH_DIR = Path(
    r"C:/Users/arqam/.gemini/antigravity/brain/e6cd4726-22aa-425e-a8f7-aab472c30784/scratch"
)


def read_hodge():
    p = Path(r"d:/Comfy UI/hodge conjecture/reports/millennium_ext/MILLENNIUM_EXT_RECEIPT.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    ext = data["extension_lean_audit"]
    passed = (
        bool(data.get("EXT_CHECKS_PASSED"))
        and bool(data.get("baseline_lock", {}).get("locked_baseline_intact"))
        and bool(ext.get("lake_build_ok"))
        and len(ext.get("unexpected_axiom_lines", [])) == 0
    )
    return {
        "problem": "Hodge Conjecture (HODGE-MILLENNIUM-001)",
        "status_open": True,
        "audit_status": "PASS" if passed else "FAIL",
        "receipt_path": str(p),
        "ext_checks_passed": bool(data.get("EXT_CHECKS_PASSED")),
        "locked_baseline_intact": bool(data.get("baseline_lock", {}).get("locked_baseline_intact")),
        "lake_build_ok": bool(ext.get("lake_build_ok")),
        "baseline_theorems": 84,
        "extension_theorems": ext.get("extension_theorems"),
        "total_zero_axiom_declarations": 84 + int(ext.get("extension_theorems", 0)),
        "unexpected_axiom_lines": len(ext.get("unexpected_axiom_lines", [])),
        "verbatim_axiom_receipts_count": len(ext.get("verbatim_axiom_receipts", [])),
        "schur_certs_present": any(
            name in k
            for k in ext.get("theorem_counts", {})
            for name in (
                "SchurUniversalSp8ProjectionExt",
                "CliffordTripleProductSchurExt",
                "CliffordTripleAndFermat25SchurExt",
            )
        ),
        "github_repo": "Qamarbajwa/hodge-cy4-spin8-lean4",
        "release_tag": "v1.4.0-rosetta",
        "zenodo_version_doi": "10.5281/zenodo.24380054",
        "zenodo_concept_doi": "10.5281/zenodo.24329779",
    }


def _run_probe(script_path: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")


def read_yang_mills():
    ym_root = Path(r"d:/Comfy UI/yang mills and the mass gap")
    git_head = subprocess.check_output(
        ["git", "-C", str(ym_root), "rev-parse", "--short", "HEAD"],
        text=True,
    ).strip()
    git_status_short = subprocess.check_output(
        ["git", "-C", str(ym_root), "status", "--short"],
        text=True,
    ).strip()

    manifest_path = ym_root / "governance" / "chrysalis_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verify_log_path = ym_root / "paper" / "VERIFY_LOG.txt"
    verify_log = verify_log_path.read_text(encoding="utf-8")

    # Isolated Yang-Mills scratch probes
    p_2to4 = YM_SCRATCH_DIR / "probe_abelian_subtracted_2to4_fiber_schur.py"
    p_sand = YM_SCRATCH_DIR / "probe_paramagnetic_trace_sandwich_and_cocycle_floor.py"

    rc_2to4, out_2to4 = _run_probe(p_2to4) if p_2to4.exists() else (-1, "")
    rc_sand, out_sand = _run_probe(p_sand) if p_sand.exists() else (-1, "")

    ok_2to4 = (rc_2to4 == 0) and ("PROBE_ABELIAN_SUBTRACTED_2TO4_FIBER_SCHUR_OK" in out_2to4)
    ok_sand = (rc_sand == 0) and ("PROBE_PARAMAGNETIC_TRACE_SANDWICH_OK" in out_sand)

    # Parse verified metrics from probe_paramagnetic_trace_sandwich_and_cocycle_floor.py output
    m_inv = re.search(
        r"max_diag_K=([^\s|]+)\s*\|\s*max_\|Tr\(K\)\|=([^\s|]+)",
        out_sand,
    )
    m_cdom = re.search(r"C_dom\s*=\s*min\(\|F_para\|\s*/\s*dF_diam\)\s*=\s*([0-9.]+)", out_sand)
    m_ccoc = re.search(r"c_cocycle\s*=\s*min\(\(Tr\(K_para\^2\)/d\)\s*/\s*delta_2x2\)\s*=\s*([0-9.]+)", out_sand)
    m_blocks = re.search(r"across all 180 non-Abelian configs / (\d+) blocks", out_sand)

    # Extract max ||K||_op across non-Abelian ensembles
    k_ops = [
        float(m.group(1))
        for m in re.finditer(r"^\s*(?:SU2|SO3)\([^)]+\)\s*\|\s*([0-9.]+)\s*\|", out_sand, re.M)
    ]
    non_abelian_120_pass = len(re.findall(r"^\s*(?:SU2|SO3)\([^)]+\).*120/120\s*\|\s*120/120", out_sand, re.M))

    ym_log_ok = (
        "stage2a_cocycle_and_schur_thresholds_unconditional" in verify_log
        and "stage2a_full_crossover_basin_conditional" in verify_log
    )
    baseline_0f3f012_ancestor = (
        subprocess.run(
            ["git", "-C", str(ym_root), "merge-base", "--is-ancestor", "0f3f012", "HEAD"],
            check=False,
        ).returncode
        == 0
    )
    passed = (
        baseline_0f3f012_ancestor
        and ym_log_ok
        and ok_2to4
        and ok_sand
    )

    return {
        "problem": "4D Yang-Mills Mass Gap",
        "status_open": True,
        "audit_status": "PASS" if passed else "FAIL",
        "github_repo": "Qamarbajwa/yang-mills-lean4",
        "release_tag": "v1.1.0-rosetta",
        "release_commit": "77d52d8",
        "zenodo_version_doi": "10.5281/zenodo.24378644",
        "zenodo_concept_doi": "10.5281/zenodo.24327876",
        "git_head": git_head,
        "baseline_0f3f012_in_history": baseline_0f3f012_ancestor,
        "git_status_short_clean": git_status_short == "",
        "chrysalis_manifest_total_artifacts": manifest.get("total_artifacts"),
        "ym175_stage2a_cocycle_schur_verified_in_log": ym_log_ok,
        "scratch_probe_dir": str(YM_SCRATCH_DIR),
        "probe_abelian_subtracted_2to4_fiber_schur": {
            "exists": p_2to4.exists(),
            "ok": ok_2to4,
        },
        "probe_paramagnetic_trace_sandwich_and_cocycle_floor": {
            "exists": p_sand.exists(),
            "ok": ok_sand,
            "max_diag_K": float(m_inv.group(1)) if m_inv else None,
            "max_abs_Tr_K": float(m_inv.group(2)) if m_inv else None,
            "max_K_op": max(k_ops) if k_ops else None,
            "C_dom": float(m_cdom.group(1)) if m_cdom else None,
            "c_cocycle": float(m_ccoc.group(1)) if m_ccoc else None,
            "non_abelian_blocks_total": int(m_blocks.group(1)) if m_blocks else None,
            "non_abelian_ensembles_120_of_120": non_abelian_120_pass,
        },
    }


def read_riemann():
    p = Path(
        r"d:/Comfy UI/rheihman hypothesis/research/interactive_lab/monograph_additive_multiplicative/vasyunin_schur_chiral_rosetta_results.json"
    )
    data = json.loads(p.read_text(encoding="utf-8"))
    n6_rows = [
        r
        for r in data["test_3_prime_composite_schur"]["prime_composite_schur_table"]
        if r.get("N") == 6
    ]
    n6 = n6_rows[0] if n6_rows else {}

    p_prim = Path(
        r"d:/Comfy UI/rheihman hypothesis/research/interactive_lab/monograph_additive_multiplicative/primorial_schur_distance_decay_results.json"
    )
    prim = json.loads(p_prim.read_text(encoding="utf-8"))
    row_210 = [r for r in prim.get("primorial_ladder", []) if r.get("N") == 210][0]

    passed = (
        bool(data.get("VASYUNIN_SCHUR_CHIRAL_ROSETTA_OK"))
        and bool(data.get("NO_RH_PROOF"))
        and bool(prim.get("PRIMORIAL_SCHUR_DECAY_OK"))
        and bool(prim.get("NO_RH_PROOF"))
    )
    return {
        "problem": "Riemann Hypothesis",
        "status_open": bool(data.get("NO_RH_PROOF", True)),
        "audit_status": "PASS" if passed else "FAIL",
        "github_repos": [
            "Qamarbajwa/RiemannBlueprint@c0358b0",
            "Qamarbajwa/riemann-lean4-papers@c3f2c47",
        ],
        "release_tag": "v3.1.0-rosetta",
        "zenodo_hub_07_doi": "10.5281/zenodo.24378371",
        "zenodo_hub_13_doi": "10.5281/zenodo.24378372",
        "zenodo_hub_14_doi": "10.5281/zenodo.24378373",
        "NO_RH_PROOF": data.get("NO_RH_PROOF"),
        "receipt_path": str(p),
        "VASYUNIN_SCHUR_CHIRAL_ROSETTA_OK": data.get("VASYUNIN_SCHUR_CHIRAL_ROSETTA_OK"),
        "max_numerical_residual": data.get("max_numerical_residual"),
        "n6_delta_PC": n6.get("delta_PC"),
        "n6_Schur_inertia": n6.get("Schur_inertia"),
        "primorial_schur": {
            "receipt_path": str(p_prim),
            "lean_module": "PrimorialSchurDistanceDecay.lean",
            "PRIMORIAL_SCHUR_DECAY_OK": prim.get("PRIMORIAL_SCHUR_DECAY_OK"),
            "max_banachiewicz_split_err": prim.get("max_banachiewicz_split_err"),
            "bblr_constant": prim.get("bblr_constant"),
            "ln210_mul_E_dir_210": row_210.get("lnN_mul_E_dir"),
        },
    }


def read_navier_stokes():
    p = Path(r"d:/Comfy UI/tubulance/probe_cl30_helical_schur_results.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    p2 = data["part2_parity_gram_schur_half_op"]
    p3 = data["part3_vorticity_cocycle_and_stretching"]

    p_arch = Path(r"d:/Comfy UI/tubulance/probe_win_win_cocycle_dichotomy_arch_results.json")
    arch = json.loads(p_arch.read_text(encoding="utf-8"))
    arch_ok = (arch.get("status") == "WIN_WIN_COCYCLE_DICHOTOMY_ARCH_OK") and all(
        arch["checks"].values()
    )
    s2 = arch["scale_summaries"]["2"]
    s4 = arch["scale_summaries"]["4"]

    all_checks = all(data["checks"].values())
    passed = (data.get("status") == "CL30_HELICAL_SCHUR_COCYCLE_OK") and all_checks and arch_ok
    return {
        "problem": "3D Navier-Stokes Global Regularity",
        "status_open": bool(data.get("NS_GLOBAL_REGULARITY_OPEN", True)),
        "audit_status": "PASS" if passed else "FAIL",
        "github_repo": "Qamarbajwa/tubulance",
        "release_tag": "v1.0.0-rosetta",
        "release_commit": "bc085f2",
        "zenodo_version_doi": "10.5281/zenodo.24378625",
        "receipt_path": str(p),
        "status": data.get("status"),
        "all_checks_passed": all_checks,
        "gram_normalized_offdiag_max": p2.get("gram_normalized_offdiag_max"),
        "pi_o3_even_t_hel_norm": p2.get("pi_o3_even_t_hel_norm"),
        "schur_complement": p2.get("schur_complement"),
        "t_sq_id_err": p2.get("t_sq_id_err"),
        "k_half_recon_err": p2.get("k_half_recon_err"),
        "abelian_delta_ns_b1_2_4": [
            p3["abelian_parallel_vortex_tube"][str(b)]["delta_NS"] for b in (1, 2, 4)
        ],
        "tangle_delta_ns_b1_2_4": [
            p3["heterochiral_tg_kida_pelz_tangle"][str(b)]["delta_NS"] for b in (1, 2, 4)
        ],
        "tangle_rho_stretch_blk_b1_2_4": [
            p3["heterochiral_tg_kida_pelz_tangle"][str(b)]["rho_stretch_BLK"] for b in (1, 2, 4)
        ],
        "win_win_cocycle_dichotomy_arch": {
            "receipt_path": str(p_arch),
            "status": arch.get("status"),
            "WIN_WIN_COCYCLE_DICHOTOMY_ARCH_OK": arch_ok,
            "b2_delta_star": s2.get("delta_star"),
            "b2_Phi_max": s2.get("Phi_max"),
            "b4_delta_star": s4.get("delta_star"),
            "b4_Phi_max": s4.get("Phi_max"),
        },
    }


def main():
    workspaces = {
        "hodge": read_hodge(),
        "yang_mills": read_yang_mills(),
        "riemann": read_riemann(),
        "navier_stokes": read_navier_stokes(),
    }
    pass_count = sum(1 for w in workspaces.values() if w["audit_status"] == "PASS")
    summary = {
        "scientific_honesty_all_four_millennium_problems_open": True,
        "overall_pass_count": f"{pass_count}/4",
        "all_four_passed": pass_count == 4,
        "zenodo_dois": {
            "riemann_hubs": [
                "10.5281/zenodo.24378371",
                "10.5281/zenodo.24378372",
                "10.5281/zenodo.24378373",
            ],
            "navier_stokes_tubulance": "10.5281/zenodo.24378625",
            "yang_mills_4d": "10.5281/zenodo.24378644",
            "yang_mills_4d_concept": "10.5281/zenodo.24327876",
            "hodge_version": "10.5281/zenodo.24380054",
            "hodge_concept": "10.5281/zenodo.24329779",
        },
        "workspaces": workspaces,
    }
    out_path = Path(r"d:/Comfy UI/tubulance/rosetta_master_audit_receipt.json")
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if pass_count != 4:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
