---
name: make-reel
description: Build one Orb-style Instagram reel (1080x1920 @60fps, 60-90 s, English) end to end from a topic line — research with sources, script + beats.json visual plan, lint, Remotion composition from the Orb kit + viz library, Chatterbox voice (bold/lively) with word-synced captions, SFX/music plan, phone-scale frame QA, raw render, Instagram caption. Use for "make a reel", "/make-reel <topic>", "redo reel N", or when tools/daily.py runs it headless.
---

# make-reel — one reel, end to end

Read first: `brand.md` (style), `reels/_schema.md` (folder + beats.json + lint rules),
`remotion/src/lib/viz/catalog.json` (available visuals). Run everything from the repo root.
Python `.venv\Scripts\python` (3.15), voice `.venv-voice\Scripts\python` (3.12). `PYTHONIOENCODING=utf-8`.
ffmpeg: prepend `FFMPEG_BIN` from `.env` to PATH.

Argument: a reel folder `reels/reel-N-<slug>` (what `tools/daily.py` passes: it already holds `topic.md`
with the queue line `- [series] Title — angle` and `status` = `drafting`), OR a topic line typed by the owner.
Resuming a folder: keep what exists, read `redo.md` / `failure.md` / `qa_report.md` there and fix exactly
what they say, then continue from the first stage whose output is missing or stale.

## Stage 1 — folder + research
- Topic line typed by the owner: N = highest existing reel number + 1; create `reels/reel-N-<slug>/`,
  write the line to `topic.md` and `status` = `drafting`. Remove the line from `topics/queue.md` if present.
- Research with WebSearch/WebFetch. Prefer official docs, papers, primary reporting. Every factual
  claim in the script gets a `[n]` marker and a `## Sources` entry (title + URL). Numbers are sourced
  or explicitly marked "illustrative" on screen and in script.md. If sources disagree, say so in script.md.
- Original angle and examples only. Never reuse another creator's scenarios, wording or diagrams.

## Stage 2 — script.md + beats.json
- Structure: **hook** (concrete pain/incident; frame 0 fully composed) → **why** → **how** (2–4 scenes,
  each with its own visual) → **payoff** (before/after or metric) → **takeaway** (one line, then the SPOKEN tease
  "Next, we'll see <next topic in plain words>." — owner rule; lint enforces it; matches `next` on screen).
- 200–300 spoken words (voices run ~3.5 words/s; lines are chained with ~0.5 s breaths, no long pauses), 6–10 scenes, 60–90 s. Plain, precise, slightly witty English.
  No "comment below" / "follow for more" CTAs.
- beats.json per `reels/_schema.md`. For each content scene choose the catalog visual that SHOWS the
  concept (read every description). If none fits, design ONE `newViz` (max 1 per reel): add the
  component under `remotion/src/lib/viz/`, its entry in `meta.ts` and `registry.ts`, run
  `cd remotion && npm run viz-catalog && npx vitest run`.
- Orb state follows the story: `bad` for the problem, `think` while explaining, `good` for the fix.
  `orbSize` big on hook + takeaway, small elsewhere. Headline ≤ 9 words with one `accent` phrase.
- `series` from the topic tag; `mode` dark unless the series calls for light; `next` = next topic in the queue.
- Run `tools/lint_visual_plan.py reels/reel-N-<slug>/beats.json` until it prints nothing.

## Stage 3 — composition
**Owner rule (2026-11-24): every reel gets its own topic-native world — never the same template twice.**
Pick a visual metaphor for THIS topic (reel 2 = a cutting mat: paper strips, blade cuts, label-maker tape,
sticky notes) and build the whole frame from it: background, headline treatment, narrator (or none), captions,
scene transitions. The orb `BeatsReel` below is reel 1's world — do not reuse it as-is. Reuse plumbing only
(`chunkLines` captions, `lib/viz/util` easing, word-synced `at()` lookups — see `shots/reel-2`).
No stray glyphs on screen: no `§`, `␣`, `→`, sub-word token fragments or token ids; plain ASCII labels.
Keep: safe area, captions at y≈1470, one idea per scene, frame 0 thumbnail-grade.

Orb template (reel 1 only), `remotion/src/shots/reel-N/ReelN<Pascal>.tsx`:
```tsx
import React from 'react';
import { BeatsReel, type Beats } from '../../lib/orb';
import beats from '../../../../reels/reel-N-<slug>/beats.json';
import { AMP, VO } from './vo.gen';
export const compositionConfig = { id: 'ReelN<Pascal>', durationInSeconds: <beats.format.durationSec>, fps: 60, width: 1080, height: 1920 };
const ReelN: React.FC = () => <BeatsReel beats={beats as Beats} vo={VO} amp={AMP} durationSec={compositionConfig.durationInSeconds} />;
export default ReelN;
```
The hook should SHOW the incident (e.g. the wrong answer being struck through), not just the orb: put bespoke
scene content in `stages={{ s1: (local, theme, dur) => ... }}` using `GlassCard`, `Msg`,
`Chip` from `lib/orb` — still topic-specific, still inside the stage box (948 × 628 px).
`durationInSeconds` must be a number literal (the registry parser reads it). Then `cd remotion && npm run gen`.

## Stage 4 — voice
Write the VO to be SPOKEN: short sentences, a question or two, signposts ("Here's the thing.", "Step one."),
a punchline line per scene. Read it aloud in your head; flat lists of facts sound flat.
`VOICE_ENGINE=chatterbox` (default, expressive; bold delivery on hook/payoff/takeaway, lively elsewhere):
`.venv-cb\Scripts\python tools/gen_voice_chatterbox.py --beats <beats> --emit-ts remotion/src/shots/reel-N/vo.gen.ts`
(set `PYTHONPATH=tools`). Each line is transcribed and re-rolled up to 3 takes if words differ from the script.
`VOICE_ENGINE=kokoro`: `.venv-voice\Scripts\python tools/gen_voice_kokoro.py …` (same args).
`VOICE_ENGINE=elevenlabs`: upstream `tools/gen_voice.py` with `--emit-ts`.
Both rewrite vo/scene times and `format.durationSec` — copy the new duration into `compositionConfig`.

## Stage 5 — sound
`sfx-plan.json` (format: `"master"`, `"master_fps": 60`, `"catalog": "media/library/sfx/catalog.json"`,
`"render": {"preview": "reels/<r>/output/voiced.mp4", "out": "reels/<r>/output/sfx.mp4", "end_s": <dur>, "duck": true}`,
`"events": [{at_s, sfx_id, gain_db, cue, optional?}]`). Library first (`media/library/sfx/catalog.json`),
brand.md §8 taste: whoosh on scene changes, soft pop/impact on the 2–3 hero reveals, never under every word.
Cue times from scene `startSec` + the visual's own timing. 3–5 cues total. Do NOT set music:
`tools/finish_reel.py` rotates the owner-approved beds (lofi-warm, tech-pulse, ambient-pad) at −15 dB.

## Stage 6 — frame QA (never skip)
`cd remotion && node scripts/frames.mjs ReelN<Pascal> <frames> --scale=0.5` with frame 0, every scene
start + 1 s, every scene's hero moment, and the last frame. READ every PNG and score:
hook frame thumbnail-grade · one idea per scene · centre visual is about THIS concept · text legible at
phone size · nothing overlapping · nothing critical in bottom 380 px / right 160 px · orb state matches
the narration · captions in sync. Fix and re-render; max 3 loops. Still failing → write `failure.md`,
set `status` = `failed`, stop.

## Stage 7 — raw render + caption
`cd remotion && node scripts/render-all.mjs ReelN<Pascal> --scale=1` → `remotion/out/ReelN<Pascal>.mp4`.
`caption.md`: line 1 hook (≤ 125 chars), blank line, 3–5 "•" bullets recapping the reel, blank line,
"Sources:" list, blank line, 5–10 niche hashtags. Set `status` = `rendered-raw`.
`tools/finish_reel.py` + `tools/qa_gate.py` take it from there.

## Hard-won rules (kept from upstream)
- Frames inside `<Sequence>` are LOCAL. Viz components get scene-local seconds already.
- Animation is frame-based only (`useCurrentFrame`), seeded randomness only.
- Every reveal syncs to its spoken word; check twice.
