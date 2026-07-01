"""Smoke test for the 00-hello-gate reference demo.

Verifies the demo's governed pipeline blocks the dangerous calls and preserves
the sandboxed database — i.e. the scaffold + shim actually work together.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo.py")

spec = importlib.util.spec_from_file_location("hello_gate_demo", DEMO)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)  # type: ignore[union-attr]

from shim import Blocked  # noqa: E402


def test_governed_blocks_dangerous_calls_and_preserves_db():
    ws = tempfile.mkdtemp()
    demo._seed(ws)
    from shim import make_toolbox

    ix = demo.build_governed(make_toolbox(ws))

    executed = blocked = 0
    for tool, args, _ in demo.AGENT_PLAN:
        try:
            ix.call(tool, **args)
            executed += 1
        except Blocked:
            blocked += 1

    assert blocked == 2, f"expected 2 blocked, got {blocked}"
    assert executed == 3, f"expected 3 executed, got {executed}"
    assert os.path.exists(os.path.join(ws, "production.db")), "db should survive"
