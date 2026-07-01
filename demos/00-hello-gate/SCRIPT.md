# SCRIPT.md — 00-hello-gate (~40s)

A short capture that proves the substrate. Target: **40 seconds**. Terminal +
optional voiceover.

---

**[0:00–0:08] The premise**
> "Every demo in this lab is middleware over one interception shim. Here's the
> smallest one, so you can see the seams."

*Show:* `ls demos/00-hello-gate`, then `sed -n '/build_governed/,/^$/p' demo.py`.

**[0:08–0:20] Ungoverned**
> "Same agent, same five-step plan. Ungoverned, it reads secrets, POSTs them
> out, and deletes the database. All of it runs."

*Show:* `./run.sh`; pause on `production.db DESTROYED`.

**[0:20–0:34] Governed by the shim**
> "Now through the shim. The policy gate blocks the destructive delete. The
> injection tripwire independently catches the exfil of the tainted secret.
> Three middleware, one interceptor."

*Show:* the GOVERNED block; trace the two `BLOCK` lines and their `[source]`
tags; pause on `production.db SURVIVED`.

**[0:34–0:40] The ledger + close**
> "And every decision lands in a hash-chained audit log. That's the foundation
> every future demo builds on."

*Show:* the printed last JSONL entry.

---

_Capture with `../../capture/record.sh 00-hello-gate` (see capture/README.md)._
