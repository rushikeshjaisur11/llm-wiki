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
- 160–240 spoken words (Turbo narrator runs ~2.6 words/s incl. breaths; lines are chained with ~0.5 s breaths, no long pauses), 6–10 scenes, 60–90 s. Plain, precise, slightly witty English.
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
Something must always move: any 2 s fully-still stretch fails the QA gate's freeze check (reel 3's takeaway
hold did). Use a text-free background layer (slow drifting glow, particles, twinkle) — NOT a whole-frame
sub-pixel sway/translate: text snaps to pixels separately from lines, so labels visibly jitter (owner caught it
on reel 5's axis numbers). Animate continuous values (stroke dashoffset, transforms), never a growing point list.
**Owner rule (2026-11-24): no house style.** Use whatever animation the concept needs — motion graphics, 2D/3D
(`@remotion/three`), data viz (d3), kinetic type, code/terminal (`lib/terminal`), UI mockups (`lib/browser`),
Lottie, rough.js sketch, stick figures — and mix them inside one reel if that explains it better. No tool is
the default; don't lean on one style across reels.

**Owner rule (2026-11-25): reels 2–4 still read as one template — break it.** They all share the same skeleton:
progress scale/strip across the top, boxed headline under it, one card in the middle, caption plate at the
bottom, camera pan/feed between scenes. Concretely:
- **No top progress scale/ruler/barcode/strip.** It is not important; drop it. Series label (e.g. "RAG 04") only
  on frame 0, small, and part of the world (not a header bar).
- **No fixed scene skeleton.** Do not put a headline box at the top of every scene. Layout changes with the idea:
  full-bleed visual with no headline, one huge number, a split screen, a zoom INTO the object, a top-down
  diagram, kinetic type filling the frame. At most half the scenes may carry an on-screen headline.
- **Animation = the mechanism, accurately.** Each scene animates what really happens, step by step, in the
  right order, with real numbers computed in code — e.g. RRF: show each rank, compute 1/(60+rank) live, add the
  two scores, re-sort; cosine: rotate actual vectors and show the angle/number updating; chunking: real text split
  at real token counts. No decorative motion that doesn't map to a step; no "card pops in" as the whole visual.
  Every step lands on the word that names it. Illustrative data is fine (labelled), wrong mechanics are not.
- **Motion vocabulary per topic**, not reused: pick from morphs, path drawing, particle flows, physics (springs,
  collisions), 3D (`@remotion/three`), camera dolly/zoom into detail, masks/reveals, counters, graph re-layouts.
  Transitions come from the content (one object becomes the next), not a generic pan/feed.
- **Before coding, write `## Visual design` in script.md**: per scene — the shot (layout + what moves), which real
  step each motion shows, the word it syncs to, and one line "differs from reels N-1/N-2 because …".

**Stick-scene tool (optional, one of many)** (hand-drawn stick figure working a physical prop — lever, stamp,
filing cabinet, conveyor): fits only when a process or cause→result reads best as a physical metaphor. Follow `.claude/skills/stick-scene/SKILL.md` for the craft
(read its `references/craft.md` and the `examples/`; pitch 2–3 metaphors unless the owner said go; style rules:
ink `#141414`, white paper, one accent, few words, figure never hidden, show the result). Reel-specific
differences from that skill:
- Scene file goes in `remotion/src/shots/reel-N/stick/<id>.js` (template: `.claude/skills/stick-scene/templates/scene.js`).
  Render with `<StickScene scene="<id>" playAt={<local s of the spoken trigger word>} width={948} height={628} />`
  from `lib/stick`; import `lib/stick` first, then `'./stick/<id>.js'`. One stick scene = one beat; `playAt`
  per beat, and the scene's `dur` must fit inside the beat. `n` picks a play variant.
- Size for phone: drawing scale = min(h/230, w/width) — keep the scene `width` ≈ 330 for a 948×628 card
  (≈ 2.7×), so 9–11 px labels read at phone size. Put it on a white card (the scene is ink-on-paper).
- No `Math.random()` in scene code (Remotion renders frames out of order); derive variation from `S.n`/`S.t`.
- QA with this repo's `scripts/frames.mjs` (Stage 6); the skill's own `frames.mjs`/`motion.mjs` (need
  `playwright@1.56.1` in a scratch dir) are optional extra checks for joint jumps / arm-through-face.
- Demo: composition `StickDemo` (`shots/demo/StickDemo.tsx`). Runtime `lib/stick/stick.js` is vendored unchanged
  (nilbuild/stick-scene @ ca84311, MIT) — don't edit it; update by re-copying.

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

**Natural human delivery (owner, 2026-11-25; new reels only — never re-voice existing reels).** Talk like a person
explaining to a friend: contractions, "So…", "And…", "Here's the thing.", a trailing "…" before a reveal, a
rhetorical question then its answer. Emotion goes in an optional `vo[].say` (what gets spoken); `vo[].text`
stays the clean caption/lint text with the same words minus tags. Tags (Chatterbox Turbo, each verified to render
as sound or tone, never read out):
- sounds: `[sigh]` `[chuckle]` `[laugh]` (adds "haha") `[gasp]` `[groan]` (adds "uh") `[clear throat]` `[sniff]` `[cough]` `[shush]` (adds "shh")
- tone for the line that follows: `[happy]` `[surprised]` `[sarcastic]` `[dramatic]` `[whispering]` `[angry]` `[fear]` `[crying]` (`[narration]` = neutral reset; never `[advertisement]` — garbles words)
Nothing is compulsory: use a tag only where a real narrator would make that sound or shift tone — a sigh at
a frustrating failure, a chuckle at an ironic twist, `[surprised]` on a counter-intuitive number, `[whispering]`
for an aside/secret, `[happy]` on the fix landing. Put it at a sentence or clause break, never mid-phrase. Match
the emotion to the moment; a reel with zero tags is fine if none fits. Never two tags back to back.
**Owner (2026-11-25, reel 5): the `[sigh]` sounded "so much artificial".** Treat every sound tag as suspect:
carry emotion with wording, punctuation and rhythm first ("And the bot still says... no."). A sound tag ships
only after you render that exact line with and without it, listen-check (transcribe + duration), and offer the
owner both takes as an audition. Default: no sound tags.

`.venv-cb\Scripts\python tools/gen_voice_chatterbox.py --beats <beats> --emit-ts remotion/src/shots/reel-N/vo.gen.ts`
(set `PYTHONPATH=tools`). Default engine = Chatterbox Turbo cloned from `media/library/voice/narrator-ref.wav`
(owner pick, natural pace, no time-stretch: `TEMPO` 1.0). `--engine standard` = the reels 1–4 voice (pair with
`--tempo 0.9`). Runs on the NVIDIA GPU only. Each line is transcribed and re-rolled up to 3 takes if words differ from the script.
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
the narration · captions in sync. **Sameness check:** put 4 mid-scene frames of this reel next to 4 from each of
the previous two reels (`outbox/` masters, ffmpeg hstack). If a viewer could mistake them for the same series
template (same top strip, same headline-box + card + plate stack, same transition) → redesign, don't polish.
**Accuracy check:** for each scene, write in qa_report.md the step it shows and confirm the on-screen numbers
are what the code computes and the order matches the real algorithm. Fix and re-render; max 3 loops. Still failing → write `failure.md`,
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
