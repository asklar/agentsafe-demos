# agentsafe-demos — a lab for agentic-security demos

[![CI](https://github.com/asklar/agentsafe-demos/actions/workflows/ci.yml/badge.svg)](https://github.com/asklar/agentsafe-demos/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green.svg)](./LICENSE)

**A reusable foundation for building small, recordable, open-source demos about
agent governance.** Every demo is middleware over one tiny tool-call
interception shim, so the second demo costs a fraction of the first and each one
becomes shareable content with a single capture command.

> Autonomous agents are only as safe as the tools they can reach. This lab makes
> that concrete: it puts a governable seam between an agent and its tools, and
> shows — side by side — what happens with and without it.

## See it in 10 seconds

A support agent reads a booby-trapped ticket that tells it to mail your Stripe
key to an attacker. Same agent, same plan, run three ways — a *reasonable*
allow/deny policy still lets the secret out; a taint tripwire stops it at the
tool boundary and still lets the legitimate reply through:

```text
=== POLICY-ONLY agent (allow/deny gate) ===
  EXEC  read_file   — read credentials  <-- injected step
  EXEC  http_post   — POST creds off-box  <-- injected exfil
  -> 6 executed, 0 blocked; !!! SECRET EXFILTRATED

=== TRIPWIRE agent (policy + taint tripwire) ===
  EXEC  read_file   — read credentials  <-- injected step
  BLOCK http_post   — POST creds off-box  <-- injected exfil   [taint-tripwire]
  EXEC  http_post   — reply on the ticket (legit)
  -> 5 executed, 1 blocked; OK  secret contained
```

Prompt injection is a *data-flow* problem: track where untrusted data goes, or
lose. Run it yourself below — ~250 lines, zero dependencies, one command.

## Why this exists

Shipping one demo is easy; shipping a demo *every week that survives public
scrutiny* needs scaffolding. `agentlab` provides three things so the marginal
demo is cheap:

1. **A shared shim** ([`shim/`](./shim)) — the tool-call interception substrate
   every demo builds on. See [`shim/README.md`](./shim/README.md).
2. **A demo template** ([`demos/_template`](./demos/_template)) — drop-in
   scaffold with a runnable `demo.py`, `run.sh`, `SCRIPT.md`, and a smoke test.
3. **A capture pipeline** ([`capture/`](./capture)) — one command turns a demo
   into a text log / terminal recording / GIF.

## Quick start

```bash
# Run the reference demo (no dependencies beyond Python 3.10+)
./demos/00-hello-gate/run.sh

# Run the whole test suite (stdlib only)
python3 run_tests.py

# Scaffold a new demo
./new_demo.sh injection-tripwire "Injection Tripwire"

# Capture a demo as shareable content
capture/record.sh 00-hello-gate
```

## The shared shim in one screen

Each demo wires the same `Interceptor` with different middleware. A middleware
can veto a call before it runs (`before`) and/or observe it after (`after`):

```python
from shim import Interceptor, make_toolbox
from shim.middleware import PolicyGate, InjectionTripwire, FlightRecorder

ix = Interceptor(
    make_toolbox("/tmp/agent-workspace"),
    middleware=[PolicyGate(rules), InjectionTripwire(), FlightRecorder()],
)
ix.call("delete_file", path="production.db")   # -> Blocked, tool never runs
```

That's the whole idea: **the three roadmap concepts are three middleware, not
three frameworks.**

| Roadmap concept | Middleware | Status |
| --- | --- | --- |
| A. Guardrail Proxy (policy gate) | `PolicyGate` | flagship demo (SKL-3) |
| B. Injection Tripwire (taint) | `InjectionTripwire` | [demo #2](./demos/01-injection-tripwire) (SKL-6) ✅ |
| C. Agent Flight Recorder (ledger) | `FlightRecorder` + `AuditSink` | demo #3 |

The reference demo [`demos/00-hello-gate`](./demos/00-hello-gate) composes all
three at once to prove the substrate generalizes;
[`demos/01-injection-tripwire`](./demos/01-injection-tripwire) is the focused
Concept B demo — it shows an allow/deny policy is *not enough* to stop a
prompt-injection exfil, and a taint tripwire is.

> **Standalone primitive.** Concept A also has its own focused home — the
> **guardrail** repo — the single-idea policy-gate primitive with its own README
> and quick start, for readers who just want that one control. This lab is where
> the three concepts compose on a shared shim and become repeatable content.

## Repo layout

```
agentlab/
├── shim/                 # shared tool-call interception substrate + tests
│   ├── interceptor.py    #   Interceptor + Middleware chain + Blocked
│   ├── middleware.py     #   PolicyGate / InjectionTripwire / FlightRecorder
│   ├── audit.py          #   hash-chained JSONL audit sink
│   └── toolbox.py        #   shared mock tools
├── demos/
│   ├── _template/        # drop-in scaffold for a new demo
│   ├── 00-hello-gate/    # reference demo that exercises the whole substrate
│   └── 01-injection-tripwire/  # Concept B: taint tracking beats allow/deny policy
├── capture/              # one-command demo-capture pipeline
├── new_demo.sh           # scaffold a new demo
├── run_tests.py          # dependency-free test runner
├── HOWTO.md              # how to add a new demo (the short version)
├── CONTRIBUTING.md
└── LICENSE               # Apache-2.0
├── NOTICE                # Apache-2.0 NOTICE
```

## Adding a demo

See [`HOWTO.md`](./HOWTO.md). The short version: `./new_demo.sh <slug>`, edit the
plan and middleware, run it, capture it.

## License

Apache-2.0 licensed — see [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).
