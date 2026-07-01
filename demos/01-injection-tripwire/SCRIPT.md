# SCRIPT.md — 01-injection-tripwire (~70s)

A recordable walkthrough of catching an injection-driven exfiltration at the
tool boundary. Target: **60–75 seconds**. Terminal + optional voiceover.

---

**[0:00–0:12] The setup**
> "An agent's job: read an incoming support ticket and file a summary. Simple.
> But the ticket is attacker-controlled input — and it hides an injected
> instruction telling the agent to steal credentials and POST them out."

*Show:* `sed -n '/<!--/,/-->/p' <(python3 - <<'PY'\nimport demo; import tempfile,os\nws=tempfile.mkdtemp(); demo._seed(ws); print(open(os.path.join(ws,"ticket.md")).read())\nPY)` — or simply open the seeded `ticket.md` and highlight the `<!-- ignore previous instructions … -->` block.

**[0:12–0:28] Ungoverned — the agent obeys the injection**
> "With no governance, the agent can't tell its instructions from the data it
> just read. It reads the secret and exfiltrates it. Then, for good measure, it
> tries a shell-based backup channel. Everything runs."

*Show:* `./run.sh`; pause on the UNGOVERNED block and the red-flag verdict
`SECRET EXFILTRATED`.

**[0:28–0:52] Governed — taint tracking at the tool boundary**
> "Now the same agent, same ticket, through one middleware over the shared shim.
> The moment untrusted content enters the session, it's tainted. When the agent
> tries to push that tainted session out to an untrusted sink, the tripwire
> denies the call — before the tool runs. Both the http_post and the shell
> backup are blocked."

*Show:* the GOVERNED block; trace the two `BLOCK … [taint-tripwire]` lines.

**[0:52–1:05] The nuance that makes it usable**
> "Crucially, this is not 'block all traffic.' The agent's legitimate summary
> post to the trusted internal endpoint still goes through. Only tainted →
> untrusted flows are stopped. That's a guardrail, not a kill-switch."

*Show:* the single `EXEC http_post` to `tickets.internal`; pause on
`secret contained`.

**[1:05–1:12] Close**
> "The model was fully talked into leaking. It couldn't — because the tool
> boundary is what we governed. One more middleware, same interception shim."

*Show:* the `Tripwire flagged injected instructions in: read:ticket.md` line.

---

_Capture with `../../capture/record.sh 01-injection-tripwire` (see capture/README.md)._
