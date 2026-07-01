"""Core value types shared by every demo built on the interception shim.

These are deliberately tiny and dependency-free. A tool call is described by a
``Call``; the outcome of evaluating it is a ``Decision``. Middleware speaks only
in these terms, which is what lets a policy gate, a taint tripwire and an audit
recorder all plug into the *same* substrate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ALLOW = "allow"
DENY = "deny"


@dataclass
class Call:
    """A single tool invocation flowing through the interceptor.

    ``tags`` is a free-form scratchpad middleware can use to pass signals down
    the chain (e.g. a taint tracker marking that ``args`` contain secret data).
    """

    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    """The outcome of a middleware inspecting a call.

    ``effect`` is ``ALLOW`` or ``DENY``. ``source`` names the middleware /rule
    that produced the decision so audit logs and demo output can attribute it.
    """

    effect: str
    reason: str = ""
    source: str | None = None

    @property
    def blocked(self) -> bool:
        return self.effect == DENY


# A convenient, reusable "nothing objected" decision.
PASS = Decision(effect=ALLOW, reason="allowed", source=None)
