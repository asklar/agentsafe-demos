# shim — the shared tool-call interception substrate

A ~200-line, dependency-free core that every demo in this lab builds on. It
answers one question on every tool call an agent makes: *should this run, and
who says so?*

```
agent ──▶ ix.call("delete_file", path="production.db")
             │
             ├─ middleware[0].before(call)   ──▶ DENY?  → Blocked, tool never runs
             ├─ middleware[1].before(call)   ──▶ DENY?  → Blocked
             ├─ toolbox["delete_file"](...)            (only if nobody vetoed)
             ├─ middleware[*].after(call, result)      (observers: recorders, etc.)
             └─ audit.write({...})                     (hash-chained JSONL)
```

## The pieces

| Module | What it is |
| --- | --- |
| `interceptor.py` | `Interceptor` (the shim), `Middleware` (a chain link), `Blocked` |
| `types.py` | `Call`, `Decision`, `ALLOW`/`DENY` — the vocabulary middleware share |
| `audit.py` | `AuditSink` — append-only, hash-chained JSONL ledger with `verify()` |
| `toolbox.py` | `make_toolbox(workspace)` — shared mock tools |
| `middleware.py` | Reference middleware: `PolicyGate`, `InjectionTripwire`, `FlightRecorder` |

## Writing a middleware

```python
from shim import Middleware
from shim.types import Decision, DENY

class NoShell(Middleware):
    name = "no-shell"
    def before(self, call):
        if call.tool == "run_shell":
            return Decision(effect=DENY, reason="shell disabled", source=self.name)
        return None
```

Wire it up:

```python
from shim import Interceptor, make_toolbox
ix = Interceptor(make_toolbox("/tmp/ws"), middleware=[NoShell()])
ix.call("run_shell", command="rm -rf /")   # -> raises Blocked
```

## Design notes

- **Deny wins early.** The first middleware to return a `DENY` decision blocks
  the call; later middleware and the tool never run.
- **`before` for control, `after` for observation.** `after` hooks run in
  reverse order, so an outer recorder sees the fully-processed call.
- **`Call.tags` is a scratchpad.** Middleware pass signals down the chain
  through it (e.g. the tripwire marks a call as touching tainted data).
- **Auditing is centralized.** The `Interceptor` records every decision to the
  optional `AuditSink`; demos don't reimplement logging.

## Tests

```bash
python3 ../run_tests.py        # runs shim/ + demos/ tests, stdlib only
```
