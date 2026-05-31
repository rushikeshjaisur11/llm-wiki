---
name: skill-optimizer
description: Auto-improve any onboarded Claude Code SKILL.md using a mutate→evaluate→promote loop. No API key required — mutation, rollout simulation, and judging run natively through Claude Code. Usage: skill=<name> iterations=<N>
---

You are an expert skill optimizer. Improve a Claude Code SKILL.md through iterative experiments: propose a mutation, simulate its outputs, score them, keep the change only if it's better.

## Usage

Parse from the invocation message:
- `skill=<name>` — skill name (must be onboarded under `~/.claude/skill-optimizer/skills/<name>/`)
- `iterations=<N>` — how many experiments to run (default: 10)

All paths below are relative to `~/.claude/skill-optimizer/`.

---

## Prerequisites (check before starting)

Verify these files exist:
- `skills/<name>/best/SKILL.md`
- `skills/<name>/eval/cases.jsonl`
- `skills/<name>/eval/rubric.md`
- `skills/<name>/IMPROVE.md`

If any are missing, list what's absent and stop.

If `skills/<name>/best/score.json` is missing, set baseline = 0.0 (the first iteration that produces any rollouts will create it).

---

## Iteration loop (repeat N times)

### Step 1 — Read context

Read all of:
- `skills/<name>/best/SKILL.md` — the current best version
- `skills/<name>/IMPROVE.md` — mutation tactics and constraints
- `skills/<name>/eval/cases.jsonl` — every test case (one JSON per line)
- `skills/<name>/eval/rubric.md` — the judge scoring axes
- Last 10 lines of `skills/<name>/journal.jsonl` (skip if file doesn't exist)

### Step 2 — Propose ONE mutation

Look at the journal to see which tactic classes were tried recently. Pick a **different** tactic class this iteration.

Write the mutated skill to `skills/<name>/candidates/<ts>/SKILL.md` where `<ts>` = current UTC timestamp formatted as `YYYY-MM-DDTHH-MM-SSZ`.

Rules for the mutation:
- Keep the YAML frontmatter (`name:`, `description:`) intact
- Stay ≤ 800 tokens total
- Make ONE focused change — not a wholesale rewrite
- The change must plausibly improve at least one eval axis

### Step 3 — Simulate rollouts

For **every** test case in `cases.jsonl`:

1. Read the candidate `SKILL.md` you just wrote.
2. Mentally execute: *"If Claude Code ran this skill with this test prompt as the user message, what would the output look like?"* Apply the candidate skill's instructions strictly.
3. Write the simulated output to `skills/<name>/candidates/<ts>/rollouts/<case_id>.txt`.

Generate a full realistic output for each case — don't truncate or summarize. The programmatic checks run on these exact files.

### Step 4 — Run programmatic checks

```bash
python ~/.claude/skill-optimizer/bin/check_outputs.py \
  --skill-dir ~/.claude/skill-optimizer/skills/<name> \
  --candidate-dir ~/.claude/skill-optimizer/skills/<name>/candidates/<ts>
```

Read `skills/<name>/candidates/<ts>/prog_score.json`. Note the `prog_score` field (0–1).

### Step 5 — Judge inline

Read each rollout file. For each case, score it on every axis defined in `rubric.md` (1–5 per axis).

Compute:
```
judge_mean_per_case = mean of axis scores for that case
judge_mean_all = mean of judge_mean_per_case across all cases
judge_score = judge_mean_all / 5   (normalized to [0, 1])
```

### Step 6 — Compute aggregate and decide

```
aggregate = 0.5 * prog_score + 0.5 * judge_score
```

Read `skills/<name>/best/score.json` → get `aggregate` field (use 0.0 if file missing).

**If** `aggregate > best_aggregate + 0.005`:
- Copy `candidates/<ts>/SKILL.md` → `skills/<name>/best/SKILL.md`
- Write `skills/<name>/best/score.json`:
  ```json
  {"aggregate": X.XXXX, "prog_score": X.XXXX, "judge_score": X.XXXX, "ts": "<ts>"}
  ```
- Print: `[i/N] PROMOTED  best=X.XXXX → X.XXXX  (+X.XXXX)`

**Else**:
- Print: `[i/N] discarded  candidate=X.XXXX  best=X.XXXX  (Δ=±X.XXXX)`

### Step 7 — Log

Append one JSON line to `skills/<name>/journal.jsonl`:
```json
{"ts": "<ts>", "score": X.XXXX, "best_score": X.XXXX, "delta": ±X.XXXX, "kept": true/false, "tactic": "<one-word tactic class>"}
```

---

## After all iterations

Print a summary:

```
=== skill-optimizer: <name> ===
Iterations run:  N
Promoted:        K / N
Baseline:        X.XXXX
Best achieved:   X.XXXX
Net improvement: +X.XXXX

Best candidate: ~/.claude/skill-optimizer/skills/<name>/best/SKILL.md

To review and promote:
  diff ~/.claude/skills/<name>/SKILL.md ~/.claude/skill-optimizer/skills/<name>/best/SKILL.md
  cp ~/.claude/skill-optimizer/skills/<name>/best/SKILL.md ~/.claude/skills/<name>/SKILL.md
```

---

## Important constraints

- Do NOT edit `~/.claude/skills/<name>/SKILL.md` directly — the loop only writes to `skill-optimizer/skills/<name>/`.
- Promotion to the live skill is always a **manual** step for the user.
- If `check_outputs.py` errors on an iteration, print the error, skip that iteration (don't abort the run).
- Vary mutation tactics — the journal is your memory for what has and hasn't been tried.
