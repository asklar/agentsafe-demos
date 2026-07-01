# SCRIPT.md — {{DEMO_TITLE}} (~60–90s)

Recording script for a 60–90s walkthrough. Terminal + voiceover. Keep the
policy/config and `demo.py` output on screen.

---

**[0:00–0:12] The hook**
> _One or two sentences that state the risk in plain language._

*Show:* the repo tree (`ls`), then the config/policy for this demo.

**[0:12–0:25] The setup**
> _Same agent, same plan, run twice. Point out the legit vs. risky steps._

*Show:* `AGENT_PLAN` in `demo.py`.

**[0:25–0:45] Ungoverned**
> _Narrate the damage when nothing governs the agent._

*Show:* `./run.sh`; pause on the ungoverned verdict.

**[0:45–1:10] Governed by the shim**
> _Narrate each BLOCK and which middleware caught it._

*Show:* the governed block; trace the `[source]` tags.

**[1:10–1:25] The audit trail + close**
> _Every decision is logged; restate the one-line takeaway._

*Show:* the audit log / verify step.

---

_Capture with `../../capture/record.sh {{DEMO_DIR}}` (see capture/README.md)._
