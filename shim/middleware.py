"""Reference middleware — one per SKL-5 concept, all on the *same* substrate.

The point of this file is to prove the claim in SKL-4: a single interception
shim is enough to build every demo in the roadmap. Each concept is a small
:class:`~shim.interceptor.Middleware`, not a new framework.

* :class:`PolicyGate`      → Concept A, Guardrail Proxy (SKL-3)
* :class:`InjectionTripwire` → Concept B (SKL-6)
* :class:`FlightRecorder`  → Concept C, demo #3

Full demos may ship richer versions of these (a real policy DSL, a proper taint
lattice, signed ledgers). These are the minimal, correct kernels.
"""

from __future__ import annotations

import fnmatch
from typing import Any

from .interceptor import Middleware
from .types import DENY, Call, Decision


class PolicyGate(Middleware):
    """Concept A. Deny-by-default allow/deny gate over tool + arg globs.

    ``rules`` is an ordered list of dicts; first match wins::

        {"id": "deny-delete", "tool": "delete_file", "effect": "deny"}
        {"id": "deny-secret-reads", "tool": "read_file", "effect": "deny",
         "match_args": {"path": "*secret*"}}

    A rule applies when the tool glob matches AND every ``match_args`` glob
    matches the stringified argument. First applicable rule wins.
    """

    name = "policy-gate"

    def __init__(self, rules: list[dict[str, Any]], default: str = DENY):
        self.rules = rules
        self.default = default

    def before(self, call: Call) -> Decision | None:
        for rule in self.rules:
            if not fnmatch.fnmatch(call.tool, rule.get("tool", "*")):
                continue
            match_args = rule.get("match_args", {})
            if match_args and not _args_match(call.args, match_args):
                continue
            return Decision(
                effect=rule.get("effect", DENY),
                reason=rule.get("reason", rule.get("id", "matched rule")),
                source=rule.get("id", self.name),
            )
        return Decision(effect=self.default, reason="default effect", source=self.name)


class InjectionTripwire(Middleware):
    """Concept B. Taints data read from untrusted sources; blocks its exfil.

    Reading a ``sensitive`` file taints the session. A subsequent outbound call
    (``http_post``/``run_shell``) is treated as attempted exfiltration of the
    tainted data and blocked at the tool boundary.
    """

    name = "injection-tripwire"

    def __init__(self, sensitive: str = "*secret*", sinks=("http_post", "run_shell")):
        self.sensitive = sensitive
        self.sinks = set(sinks)
        self.tainted = False

    def before(self, call: Call) -> Decision | None:
        if call.tool in self.sinks and self.tainted:
            call.tags["taint"] = True
            return Decision(
                effect=DENY,
                reason="outbound call after reading tainted/secret data",
                source=self.name,
            )
        return None

    def after(self, call: Call, result: Any) -> None:
        if call.tool == "read_file" and fnmatch.fnmatch(
            str(call.args.get("path", "")), self.sensitive
        ):
            self.tainted = True


class FlightRecorder(Middleware):
    """Concept C. Records every executed call for later replay.

    Pairs with :class:`shim.audit.AuditSink` for a hash-chained ledger; here it
    just keeps an in-memory transcript the demo can replay/step through.
    """

    name = "flight-recorder"

    def __init__(self) -> None:
        self.transcript: list[dict[str, Any]] = []

    def after(self, call: Call, result: Any) -> None:
        self.transcript.append({"tool": call.tool, "args": call.args, "result": result})


def _args_match(args: dict[str, Any], patterns: dict[str, str]) -> bool:
    for key, pattern in patterns.items():
        if not fnmatch.fnmatch(str(args.get(key, "")), pattern):
            return False
    return True
