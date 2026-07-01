# Contributing

Thanks for looking. This is a demo lab, optimized for **small, reviewable,
reproducible** artifacts — not a production framework.

## Principles

- **Dependency-free.** Python 3.10+ stdlib only. If a demo needs a real
  dependency, isolate it in that demo and document it; never add one to `shim/`.
- **One command to run, one to capture.** Every demo ships a `run.sh` and works
  with `capture/record.sh`.
- **Deny by default, log every decision.** Governance demos should fail safe and
  leave an auditable trail.
- **Readable in one sitting.** If a file needs a diagram to understand, it's
  probably too big.

## Workflow

1. `./new_demo.sh <slug> "Title"` to scaffold.
2. Implement your `AGENT_PLAN` and middleware.
3. `python3 run_tests.py` — keep it green; add at least one smoke test.
4. Fill in `README.md` (with expected output) and `SCRIPT.md`.
5. `capture/record.sh <demo>` and commit `run.txt`.

## Code style

- Prefer clarity over cleverness; short docstrings that explain *why*.
- Keep the public shim API stable (`shim/__init__.py`); discuss changes first.
- No secrets, no real endpoints, no destructive actions outside a temp
  workspace.

## Reporting issues

Open an issue with the demo name, your Python version, and the `run.txt` output.
