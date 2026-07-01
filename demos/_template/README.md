# {{DEMO_TITLE}}

> One-sentence hook: the risk this demo makes tangible.

**What it shows.** _2–3 sentences. What does the agent try, what does the shim
do, and why should a viewer care?_

## Run it

```bash
./run.sh          # or: python3 demo.py
```

_Paste the expected before/after terminal output here so the README doubles as
a spec:_

```
=== UNGOVERNED agent (no shim) ===
  ...
=== GOVERNED agent (shared shim) ===
  ...
```

## How it maps to the shim

This demo is built on [`shim/`](../../shim): a single `Interceptor` with the
middleware wired up in `build_governed()`.

| Concern | Middleware | What it does here |
| --- | --- | --- |
| _e.g. policy_ | `PolicyGate` | _..._ |

## Recording

See [`SCRIPT.md`](./SCRIPT.md) for the 40–90s walkthrough, and
[`../../capture/README.md`](../../capture/README.md) for the capture pipeline.
