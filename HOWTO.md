# HOWTO — add a new demo (the one-paragraph version)

Run `./new_demo.sh <slug> "Title"` to copy `demos/_template` into
`demos/NN-<slug>/` with placeholders filled in. Open `demo.py`, edit two things:
the `AGENT_PLAN` (the tool calls your agent attempts, mixing legit and risky
steps) and `build_governed()` (which middleware from `shim.middleware` — or your
own `Middleware` subclass — you wire onto the shared `Interceptor`). Run it with
`./demos/NN-<slug>/run.sh` to see the ungoverned-vs-governed output, fill the
expected output into the demo's `README.md`, flesh out `SCRIPT.md` for the 60–90s
walkthrough, and run `python3 run_tests.py` to confirm the smoke test passes.
Finally, `capture/record.sh NN-<slug>` produces the shareable text log / cast /
GIF. That's it — a new demo is a new middleware, not a new project.

---

## A bit more detail

- **New behavior = new middleware.** Subclass `shim.interceptor.Middleware` and
  implement `before()` (return a `DENY` `Decision` to block a call) and/or
  `after()` (observe an executed call). Keep it small and reviewable.
- **Reuse the toolbox.** `shim.make_toolbox(workspace)` gives you the shared
  mock tools; add tools only if your demo needs them.
- **Reuse the audit sink.** Pass `audit=AuditSink(path)` to the `Interceptor`
  for a hash-chained JSONL ledger you get for free.
- **Keep it dependency-free.** Python 3.10+ stdlib only, so `./run.sh` works for
  anyone with zero setup.
- **Ship the text capture.** Commit `capture/out/<demo>/run.txt` (or paste it
  into the README); keep big GIFs out of git.
