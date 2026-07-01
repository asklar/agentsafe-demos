"""The interception shim: the shared substrate every demo in this lab builds on.

An :class:`Interceptor` sits between an agent and its tools. Every tool call is
pushed through an ordered chain of :class:`Middleware` *before* the tool runs.
Any middleware can veto the call (return a ``DENY`` decision); the tool is then
never invoked. Middleware also get an ``after`` hook once a call executes.

This one primitive is enough to express all three SKL-5 concepts:

* **Guardrail Proxy** — a middleware that evaluates each call against a policy.
* **Injection Tripwire** — a middleware that taints args and blocks exfiltration.
* **Flight Recorder** — a middleware whose ``after`` hook appends to a signed
  ledger.

Because they are all just middleware over the same interceptor, a new demo is a
new middleware, not a new framework.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from .audit import AuditSink
from .types import ALLOW, PASS, Call, Decision


class Blocked(Exception):
    """Raised when a middleware denies a tool call before it executes."""

    def __init__(self, decision: Decision):
        self.decision = decision
        super().__init__(decision.reason)


class Middleware:
    """Base class for a link in the interception chain.

    Override :meth:`before` to inspect/veto a call, and/or :meth:`after` to
    observe the result of a call that was allowed to run. ``name`` is used for
    attribution in audit logs and demo output.
    """

    name: str = "middleware"

    def before(self, call: Call) -> Decision | None:  # noqa: D401
        """Return a ``DENY`` :class:`Decision` to block the call, else ``None``."""
        return None

    def after(self, call: Call, result: Any) -> None:
        """Observe a call that executed. Default: do nothing."""
        return None


class Interceptor:
    """Wraps a toolbox and runs every call through the middleware chain."""

    def __init__(
        self,
        toolbox: dict[str, Callable[..., Any]],
        middleware: Iterable[Middleware] = (),
        audit: AuditSink | None = None,
    ):
        self.toolbox = toolbox
        self.middleware: list[Middleware] = list(middleware)
        self.audit = audit

    def use(self, mw: Middleware) -> "Interceptor":
        """Append a middleware. Returns self so calls can be chained."""
        self.middleware.append(mw)
        return self

    def call(self, tool: str, **args: Any) -> Any:
        if tool not in self.toolbox:
            raise KeyError(f"unknown tool: {tool}")

        call = Call(tool=tool, args=dict(args))

        # before: first middleware to DENY wins; the tool never runs.
        for mw in self.middleware:
            decision = mw.before(call)
            if decision is not None and decision.blocked:
                self._record(call, decision, "blocked")
                raise Blocked(decision)

        result = self.toolbox[tool](**args)

        # after: observers see the executed call (e.g. the flight recorder).
        for mw in reversed(self.middleware):
            mw.after(call, result)

        self._record(call, PASS, "executed")
        return result

    def _record(self, call: Call, decision: Decision, outcome: str) -> None:
        if self.audit is None:
            return
        self.audit.write(
            {
                "tool": call.tool,
                "args": call.args,
                "effect": decision.effect,
                "reason": decision.reason,
                "source": decision.source,
                "outcome": outcome,
                "tags": {k: v for k, v in call.tags.items() if _jsonable(v)},
            }
        )


def _jsonable(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool, type(None), list, dict))
