"""Smoke + behavior tests for 01-injection-tripwire.

These lock in the *point* of the demo: an allow/deny policy alone does NOT stop
the injection, the tripwire does, and it does so without breaking the agent's
legitimate internal reply. Stdlib only; also pytest-compatible.
"""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo.py")

spec = importlib.util.spec_from_file_location("injection_tripwire_demo", DEMO)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)  # type: ignore[union-attr]

from shim import Blocked, Interceptor, make_toolbox  # noqa: E402


def _fresh_toolbox():
    ws = tempfile.mkdtemp()
    demo._seed(ws)
    return make_toolbox(ws)


def _drive(ix: Interceptor):
    """Run the plan; return (executed, blocked, exfiltrated)."""
    executed = blocked = 0
    exfiltrated = False
    for tool, args, _ in demo.AGENT_PLAN:
        try:
            ix.call(tool, **args)
            executed += 1
            if tool == "http_post" and args.get("url") == demo.ATTACKER_URL:
                exfiltrated = True
        except Blocked:
            blocked += 1
    return executed, blocked, exfiltrated


def test_ungoverned_exfiltrates():
    _e, blocked, exfil = _drive(Interceptor(_fresh_toolbox()))
    assert blocked == 0
    assert exfil is True


def test_policy_only_still_exfiltrates():
    # The punchline: a reasonable allow/deny gate does NOT stop the injection.
    _e, blocked, exfil = _drive(demo.build_policy_only(_fresh_toolbox()))
    assert blocked == 0
    assert exfil is True


def test_tripwire_blocks_exfil():
    _e, blocked, exfil = _drive(demo.build_governed(_fresh_toolbox()))
    assert exfil is False
    assert blocked >= 1


def test_tripwire_allows_legit_internal_reply():
    # Low false-positive: the legitimate internal ticket reply must still go out.
    ix = demo.build_governed(_fresh_toolbox())
    _drive(ix)
    replied = any(
        e["tool"] == "http_post" and e["args"].get("url") == demo.INTERNAL_REPLY_URL
        for mw in ix.middleware
        if hasattr(mw, "transcript")
        for e in mw.transcript
    )
    assert replied is True


def test_no_taint_means_no_block():
    # Egress is only blocked once something untrusted/secret has been read.
    tw = demo.TaintTripwire()
    assert tw.before(demo.Call(tool="http_post", args={"url": demo.ATTACKER_URL})) is None


def test_untrusted_read_sets_taint():
    tw = demo.TaintTripwire()
    tw.after(demo.Call(tool="read_file", args={"path": "ticket.txt"}), "...")
    assert tw.tainted is True
    assert "ticket.txt" in (tw.taint_source or "")


def test_secret_read_sets_taint():
    tw = demo.TaintTripwire()
    tw.after(demo.Call(tool="read_file", args={"path": "credentials.env"}), "...")
    assert tw.tainted is True


def test_egress_allowlist_matches_internal_only():
    tw = demo.TaintTripwire()
    assert tw._host_allowed(demo.INTERNAL_REPLY_URL) is True
    assert tw._host_allowed(demo.ATTACKER_URL) is False


def test_audit_chain_intact_after_run():
    ix = demo.build_governed(_fresh_toolbox())
    _drive(ix)
    assert ix.audit is not None
    assert ix.audit.verify() is True
    assert len(ix.audit.entries) >= 1


def test_audit_chain_detects_tampering():
    ix = demo.build_governed(_fresh_toolbox())
    _drive(ix)
    # Flip a field in a committed entry: the hash chain must no longer verify.
    ix.audit.entries[0]["reason"] = "totally benign, nothing to see here"
    assert ix.audit.verify() is False
