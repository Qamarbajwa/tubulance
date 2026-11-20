"""Cryptographic Hash-Chained Research Ledger Validator.

Implements Sections 44, 45 of Milestone V1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List


class LedgerChainError(ValueError):
    """Raised when the hash chain of research_ledger.jsonl is broken or tampered with."""


def compute_entry_hash(prev_hash: str, entry_data: Dict[str, Any]) -> str:
    """Compute current_entry_hash = SHA256(prev_hash + canonical_json(entry_data))."""
    data_str = json.dumps(entry_data, sort_keys=True)
    combined = f"{prev_hash}::{data_str}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def append_chained_ledger_entry(
    entry_data: Dict[str, Any], ledger_path: str | Path = "research_ledger.jsonl"
) -> Dict[str, Any]:
    """Append a new hash-chained entry to research_ledger.jsonl."""
    ledger_path = Path(ledger_path)
    prev_hash = "GENESIS"

    if ledger_path.exists() and ledger_path.stat().st_size > 0:
        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_record = json.loads(lines[-1])
                prev_hash = last_record.get("current_entry_hash", "GENESIS")

    curr_hash = compute_entry_hash(prev_hash, entry_data)

    chained_record = {
        "previous_entry_hash": prev_hash,
        "data": entry_data,
        "current_entry_hash": curr_hash,
    }

    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(chained_record) + "\n")

    return chained_record


def validate_hash_chained_ledger(ledger_path: str | Path = "research_ledger.jsonl") -> bool:
    """Validate that research_ledger.jsonl maintains an unbroken cryptographic hash chain."""
    ledger_path = Path(ledger_path)
    if not ledger_path.exists() or ledger_path.stat().st_size == 0:
        return True

    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    expected_prev_hash = "GENESIS"
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except Exception as e:
            raise LedgerChainError(f"Ledger syntax error on line {line_no}: {e}")

        # Handle legacy V0 unchained entries
        if "previous_entry_hash" not in record:
            continue

        prev_hash = str(record.get("previous_entry_hash", ""))
        entry_data = record.get("data", {})
        curr_hash = str(record.get("current_entry_hash", ""))

        if prev_hash != expected_prev_hash and expected_prev_hash != "GENESIS":
            raise LedgerChainError(
                f"Ledger chain BROKEN on line {line_no}: expected prev_hash={expected_prev_hash[:10]}..., got {prev_hash[:10]}..."
            )

        computed_hash = compute_entry_hash(prev_hash, entry_data)
        if computed_hash != curr_hash:
            raise LedgerChainError(
                f"Ledger hash TAMPER DETECTED on line {line_no}: record hash={curr_hash[:10]}..., computed hash={computed_hash[:10]}..."
            )

        expected_prev_hash = curr_hash

    return True
