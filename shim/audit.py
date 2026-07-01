"""Reusable audit sink: a tamper-evident, append-only JSONL ledger.

Every demo wants the same thing — a durable record of what the agent tried and
what the shim decided. This provides it once. Each entry is hash-chained to the
previous one (``prev`` holds the SHA-256 of the last entry), so truncation or
edits are detectable: re-hash the chain and compare.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any


def _hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditSink:
    """Append-only, hash-chained JSONL log. Also keeps entries in memory."""

    def __init__(self, path: str | None = None):
        self.path = path
        self.entries: list[dict[str, Any]] = []
        self._prev = "0" * 64  # genesis

    def write(self, entry: dict[str, Any]) -> dict[str, Any]:
        record = {"ts": round(time.time(), 3), **entry, "prev": self._prev}
        record["hash"] = _hash(json.dumps(record, sort_keys=True))
        self._prev = record["hash"]
        self.entries.append(record)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
        return record

    def verify(self) -> bool:
        """Recompute the hash chain; return True iff intact."""
        prev = "0" * 64
        for record in self.entries:
            if record.get("prev") != prev:
                return False
            expected = {k: v for k, v in record.items() if k != "hash"}
            if _hash(json.dumps(expected, sort_keys=True)) != record.get("hash"):
                return False
            prev = record["hash"]
        return True
