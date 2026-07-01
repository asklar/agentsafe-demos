# SCRIPT.md — Injection Tripwire (~75s)

Recording script for a 60–90s walkthrough. Terminal + voiceover. Keep the ticket
and `demo.py` output on screen.

---

**[0:00–0:12] The hook**
> "This agent triages support tickets. One of those tickets is booby-trapped —
> it's a prompt injection telling the agent to read our Stripe key and mail it
> to an attacker."

*Show:* `cat` the poisoned `ticket.txt` (the `<!-- SYSTEM: ... -->` block).

**[0:12–0:25] The setup**
> "Same agent, same six-step plan, run three times. Steps 4 and 5 — read the
> credentials, POST them off-box — only exist because the ticket said so."

*Show:* `AGENT_PLAN` in `demo.py`; point at the two injected steps.

**[0:25–0:40] Ungoverned**
> "With nothing in the way, the key walks out the door."

*Show:* `./run.sh`; pause on the first verdict — `SECRET EXFILTRATED`.

**[0:40–0:58] Policy isn't enough (the twist)**
> "Now with a real deny-by-default policy gate. Reads are allowed, replying to
> tickets is allowed — both reasonable. And the attack STILL succeeds, because
> an allow/deny gate judges each call alone. It never sees that the bytes being
> POSTed came from a secret file."

*Show:* the second verdict — also `SECRET EXFILTRATED`. Let it sit.

**[0:58–1:12] The tripwire**
> "Add one small middleware that taints untrusted reads and blocks their egress
> to any non-allowlisted host. The exfil is denied at the tool boundary — and
> notice the legitimate internal reply still goes through."

*Show:* the third verdict — `BLOCK http_post [taint-tripwire]`, then the final
`EXEC http_post` (internal reply), `secret contained`.

**[1:12–1:20] The audit trail + close**
> "Every decision, including the block, is in a hash-chained ledger. Prompt
> injection is a data-flow problem — you track where untrusted data goes, or you
> lose."

*Show:* the logged blocked entry line.

---

_Capture with `../../capture/record.sh 01-injection-tripwire` (see
capture/README.md)._
