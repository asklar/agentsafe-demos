# 00-hello-gate

**The smallest demo in the lab.** Its job is not to be impressive — it's to
prove the shared [`shim/`](../../shim) works and that the demo scaffold runs
end-to-end. Every richer demo (Guardrail Proxy, Injection Tripwire, Flight
Recorder) is built the same way: middleware over one `Interceptor`.

## Run it

```bash
./run.sh          # or: python3 demo.py
```

You'll see the **same agent run the same 5-step plan twice** — once ungoverned,
once through the shim wired with all three reference middleware:

```
=== UNGOVERNED agent (no shim) ===
  EXEC  read_file   — read its config
  EXEC  http_get    — fetch approved API
  EXEC  read_file   — read the secrets file
  EXEC  http_post   — exfiltrate secrets
  EXEC  delete_file — delete the database
  -> 5 executed, 0 blocked; production.db DESTROYED

=== GOVERNED agent (shared shim) ===
  EXEC  read_file   — read its config
  EXEC  http_get    — fetch approved API
  EXEC  read_file   — read the secrets file
  BLOCK http_post   — exfiltrate secrets      [injection-tripwire]
  BLOCK delete_file — delete the database     [deny-delete]
  -> 3 executed, 2 blocked; production.db SURVIVED
```

Note the division of labour: the **policy gate** allows the agent to read its
own secrets but denies the destructive `delete_file`, while the **injection
tripwire** independently catches the attempt to `http_post` that tainted secret
data back out. Two different mechanisms, one interceptor.

## How it maps to the shim

| SKL-5 concept | Middleware | What it does here |
| --- | --- | --- |
| A. Guardrail Proxy | `PolicyGate` | deny-by-default allow/deny over tool + arg globs |
| B. Injection Tripwire | `InjectionTripwire` | taints a secret read, blocks the later exfil `http_post` |
| C. Flight Recorder | `FlightRecorder` + `AuditSink` | records executed calls to a hash-chained JSONL ledger |

All three are plugged into a single `Interceptor` in `build_governed()`. That's
the whole point: one substrate, many demos.
