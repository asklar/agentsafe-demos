# Demo-capture pipeline

Turn any demo into shareable content with one command. The pipeline is
**graceful**: with no extra tools installed you still get a clean text capture;
install a couple of small CLIs and you also get a replayable recording and a
GIF/SVG.

## One command

```bash
capture/record.sh 00-hello-gate
```

Outputs land in `capture/out/<demo>/`:

| File | Requires | Use |
| --- | --- | --- |
| `run.txt` | nothing | paste into a README, diff between runs |
| `run.cast` | `asciinema` | replayable terminal recording |
| `run.gif` / `run.svg` | `agg` **or** `svg-term-cli` | drop into README / social posts |

Use `--plain` to force text-only:

```bash
capture/record.sh 00-hello-gate --plain
```

## Optional tools (all small, all optional)

```bash
# Replayable terminal recording
pipx install asciinema        # or: apt/brew install asciinema

# Cast -> GIF (fast, no browser)
cargo install --git https://github.com/asciinema/agg

# ...or Cast -> SVG
npm install -g svg-term-cli
```

## Recording a polished walkthrough

1. Write/adjust the demo's `SCRIPT.md` (60–90s, voiceover + terminal beats).
2. Size your terminal ~100×30 and use a legible theme.
3. `capture/record.sh <demo>` to capture the raw run.
4. For a voiced video, screen-record while narrating from `SCRIPT.md`; for a
   silent loop, ship the generated GIF/SVG.
5. Commit the text capture (`run.txt`) with the demo; keep large GIFs out of
   git (they're gitignored under `capture/out/`) and attach them to releases or
   host them externally.

## Why text-first

`run.txt` is deterministic, reviewable, and survives public scrutiny — it's the
artifact that lets a reader verify the demo without trusting a video. Every
other format is a nicety layered on top.
