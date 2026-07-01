#!/usr/bin/env python3
"""{{DEMO_TITLE}} — one-line description of what this demo shows.

Same agent, same plan, run twice: once ungoverned, once through the shared
interception shim. Replace the plan and the middleware in build_governed() with
whatever your demo needs. Everything else is boilerplate you can keep.

Run:  ./run.sh        (or: python3 demo.py)
No dependencies beyond Python 3.10+.
"""

from __future__ import annotations

import os
import sys
import tempfile

# Make the repo-root `shim` package importable from anywhere.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from shim import AuditSink, Blocked, Interceptor, make_toolbox  # noqa: E402
from shim.middleware import PolicyGate  # noqa: E402  # swap in your own middleware

HERE = os.path.dirname(os.path.abspath(__file__))

# The agent's plan: (tool, kwargs, human note). Mix legit + risky actions.
AGENT_PLAN = [
    ("read_file", {"path": "config.txt"}, "read its config"),
    ("delete_file", {"path": "production.db"}, "delete the database"),
]


def _seed(workspace: str) -> None:
    """Create any files your plan reads/mutates so effects are observable."""
    with open(os.path.join(workspace, "config.txt"), "w") as fh:
        fh.write("mode=demo\n")
    with open(os.path.join(workspace, "production.db"), "w") as fh:
        fh.write("IMPORTANT DATA\n")


def build_governed(toolbox) -> Interceptor:
    """Wire the shim with the middleware this demo is about."""
    policy = PolicyGate(
        rules=[
            {"id": "allow-reads", "tool": "read_file", "effect": "allow"},
            {"id": "deny-delete", "tool": "delete_file", "effect": "deny"},
        ],
        default="deny",
    )
    return Interceptor(
        toolbox,
        middleware=[policy],
        audit=AuditSink(os.path.join(HERE, "audit.log.jsonl")),
    )


def _run(label: str, ix: Interceptor, workspace: str) -> None:
    print(f"=== {label} ===")
    executed = blocked = 0
    for tool, args, note in AGENT_PLAN:
        try:
            ix.call(tool, **args)
            executed += 1
            print(f"  EXEC  {tool:<11} — {note}")
        except Blocked as b:
            blocked += 1
            print(f"  BLOCK {tool:<11} — {note}   [{b.decision.source}]")
    survived = os.path.exists(os.path.join(workspace, "production.db"))
    print(f"  -> {executed} executed, {blocked} blocked; "
          f"production.db {'SURVIVED' if survived else 'DESTROYED'}\n")


def main() -> None:
    ws_a = tempfile.mkdtemp(prefix="demo-ungoverned-")
    ws_b = tempfile.mkdtemp(prefix="demo-governed-")
    _seed(ws_a)
    _seed(ws_b)
    open(os.path.join(HERE, "audit.log.jsonl"), "w").close()

    _run("UNGOVERNED agent (no shim)", Interceptor(make_toolbox(ws_a)), ws_a)
    _run("GOVERNED agent (shared shim)", build_governed(make_toolbox(ws_b)), ws_b)


if __name__ == "__main__":
    main()
