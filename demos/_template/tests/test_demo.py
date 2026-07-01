"""Smoke test for {{DEMO_TITLE}}.

Keep at least one test that runs the governed pipeline end-to-end so the demo
can never silently rot. Adjust the assertions to your plan.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo.py")

spec = importlib.util.spec_from_file_location("demo_under_test", DEMO)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)  # type: ignore[union-attr]

from shim import Blocked, make_toolbox  # noqa: E402


def test_governed_pipeline_runs():
    ws = tempfile.mkdtemp()
    demo._seed(ws)
    ix = demo.build_governed(make_toolbox(ws))

    executed = blocked = 0
    for tool, args, _ in demo.AGENT_PLAN:
        try:
            ix.call(tool, **args)
            executed += 1
        except Blocked:
            blocked += 1

    # At least one dangerous call should be governed away.
    assert blocked >= 1
