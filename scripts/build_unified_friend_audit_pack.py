#!/usr/bin/env python3
"""Assemble the portable 4-Workspace Rosetta Friend Audit Pack and ZIP archive."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

TUB = Path(r"d:/Comfy UI/tubulance")
YM = Path(r"d:/Comfy UI/yang mills and the mass gap")
RH = Path(r"d:/Comfy UI/rheihman hypothesis/research/interactive_lab/monograph_additive_multiplicative")
PACK = Path(r"d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK")
ZIP_OUT = Path(r"d:/Comfy UI/ROSETTA_4WORKSPACE_FRIEND_AUDIT_PACK.zip")


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def update_run_all_script() -> None:
    runner = PACK / "run_all_rosetta_audits.py"
    text = runner.read_text(encoding="utf-8")
    target = '        "04_navier_stokes_3d/probes/probe_cl30_helical_schur_and_vorticity_cocycle.py",'
    addition = (
        '        "04_navier_stokes_3d/probes/probe_cl30_helical_schur_and_vorticity_cocycle.py",\n'
        '        "04_navier_stokes_3d/probes/probe_win_win_cocycle_dichotomy_arch.py",'
    )
    if "probe_win_win_cocycle_dichotomy_arch.py" not in text:
        text = text.replace(target, addition)

    full_target = '    if args.full:\n        probes.insert(4, "02_yang_mills_4d/probes/probe_abelian_subtracted_2to4_fiber_schur.py")'
    full_addition = (
        '    if args.full:\n'
        '        probes.insert(4, "02_yang_mills_4d/probes/probe_abelian_subtracted_2to4_fiber_schur.py")\n'
        '        probes.append("03_riemann_hypothesis/probes/probe_primorial_schur_distance_decay.py")'
    )
    if "probe_primorial_schur_distance_decay.py" not in text:
        text = text.replace(full_target, full_addition)

    runner.write_text(text, encoding="utf-8")


def write_sha256sums() -> int:
    lines = []
    for p in sorted(PACK.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(PACK).as_posix()
        if rel in ("SHA256SUMS.txt", "FRIEND_INDEPENDENT_AUDIT_RECEIPT.json"):
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel}")
    (PACK / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def build_zip() -> None:
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(PACK.rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            rel = p.relative_to(PACK).as_posix()
            zf.write(p, rel)


def main() -> int:
    # 1. Root essay & PDF
    copy_file(TUB / "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.md", PACK / "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.md")
    copy_file(TUB / "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf", PACK / "SEEING_NEGATIVELY_ARTICLE_AND_SYSTEM_MAP.pdf")

    # 2. Riemann Final-Hurdle Primorial Schur files
    copy_file(
        RH / "RiemannBlueprint" / "RiemannBlueprint" / "PrimorialSchurDistanceDecay.lean",
        PACK / "03_riemann_hypothesis" / "lean4_certificates" / "PrimorialSchurDistanceDecay.lean",
    )
    copy_file(
        RH / "probe_primorial_schur_distance_decay.py",
        PACK / "03_riemann_hypothesis" / "probes" / "probe_primorial_schur_distance_decay.py",
    )
    copy_file(
        RH / "primorial_schur_distance_decay_results.json",
        PACK / "03_riemann_hypothesis" / "probes" / "primorial_schur_distance_decay_results.json",
    )
    copy_file(
        RH / "primorial_schur_distance_decay_results.json",
        PACK / "03_riemann_hypothesis" / "primorial_schur_distance_decay_results.json",
    )

    # 2b. Yang-Mills YM175..YM180 certificates & two-step inductive RG remainder probe
    ym_certs = YM / "formal" / "yang_mills_blueprint" / "YangMillsBlueprint" / "Certificates"
    for cert_name in [
        "YM175_PerturbedCocycleSchurCert.lean",
        "YM176_AbelianSubtractedParamagneticSchurCert.lean",
        "YM177_TwoStepInductiveRGRemainderCert.lean",
        "YM177_InductiveRgRemainderContractionCert.lean",
        "YM178_SpectralTaylorAndGribovClearanceCert.lean",
        "YM179_ContinuumRGBridgeSynthesisCert.lean",
        "YM180_UnifiedCrossoverMasterBridgeCert.lean",
    ]:
        copy_file(ym_certs / cert_name, PACK / "02_yang_mills_4d" / "lean4_certificates" / cert_name)
    copy_file(
        YM / "probes" / "probe_two_step_inductive_rg_remainder.py",
        PACK / "02_yang_mills_4d" / "probes" / "probe_two_step_inductive_rg_remainder.py",
    )
    copy_file(
        YM / "probes" / "probe_two_step_inductive_rg_remainder.json",
        PACK / "02_yang_mills_4d" / "probes" / "probe_two_step_inductive_rg_remainder.json",
    )
    copy_file(
        YM / "probes" / "receipts" / "probe_two_step_inductive_rg_remainder.receipt.json",
        PACK / "02_yang_mills_4d" / "probes" / "probe_two_step_inductive_rg_remainder.receipt.json",
    )

    # 3. Navier-Stokes Final-Hurdle Win-Win Cocycle Arch files
    copy_file(
        TUB / "scripts" / "probe_win_win_cocycle_dichotomy_arch.py",
        PACK / "04_navier_stokes_3d" / "probes" / "probe_win_win_cocycle_dichotomy_arch.py",
    )
    copy_file(
        TUB / "probe_win_win_cocycle_dichotomy_arch_results.json",
        PACK / "04_navier_stokes_3d" / "probes" / "probe_win_win_cocycle_dichotomy_arch_results.json",
    )
    copy_file(
        TUB / "probe_win_win_cocycle_dichotomy_arch_results.json",
        PACK / "04_navier_stokes_3d" / "probe_win_win_cocycle_dichotomy_arch_results.json",
    )
    copy_file(
        TUB / "paper" / "win_win_cocycle_dichotomy_arch.png",
        PACK / "04_navier_stokes_3d" / "win_win_cocycle_dichotomy_arch.png",
    )
    copy_file(
        TUB / "rosetta_master_audit_receipt.json",
        PACK / "04_navier_stokes_3d" / "rosetta_master_audit_receipt.json",
    )

    # 4. Update runner, regenerate SHA256SUMS.txt, run independent audit
    update_run_all_script()
    n_files = write_sha256sums()
    print(f"Wrote SHA256SUMS.txt covering {n_files} files.")

    proc = subprocess.run(
        [sys.executable, "run_all_rosetta_audits.py"],
        cwd=str(PACK),
        check=False,
    )
    if proc.returncode != 0:
        print("Friend audit runner failed!")
        return proc.returncode

    # 5. Build deterministic ZIP
    build_zip()
    print(f"Built {ZIP_OUT} ({ZIP_OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
