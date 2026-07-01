"""agentlab shim — the shared tool-call interception substrate.

Public API::

    from shim import Interceptor, Middleware, Blocked, AuditSink, make_toolbox
    from shim.types import Call, Decision, ALLOW, DENY

Reference middleware (one per SKL-5 concept) live in :mod:`shim.middleware`.
"""

from __future__ import annotations

from .audit import AuditSink
from .interceptor import Blocked, Interceptor, Middleware
from .toolbox import make_toolbox
from .types import ALLOW, DENY, PASS, Call, Decision

__all__ = [
    "Interceptor",
    "Middleware",
    "Blocked",
    "AuditSink",
    "make_toolbox",
    "Call",
    "Decision",
    "ALLOW",
    "DENY",
    "PASS",
]
