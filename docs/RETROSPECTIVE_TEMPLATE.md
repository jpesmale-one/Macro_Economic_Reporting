# WEEKLY RETROSPECTIVE — template, locked 2026-08-30 (LD-70)

**Jeff, 2026-08-30:** *"I like the Retrospective report we created yesterday.
let's keep that and follow the same for the succeeding retrospective reviews in
the future."*

**The reference implementation is the 23–29 August retrospective**, published
2026-08-29. Build every future one to this shape.

---

## What it is

**A standalone HTML artifact, published Saturday, reviewing the week that just
settled.** It is NOT a section of the daily edition (LD-70) — a retrospective
reviews a WEEK, is written once a week, and answers a different question:
*how did we do*, not *where is price going*.

- **Cadence:** Saturday, after the week's final bar
- **Form:** standalone artifact, its own template, no §-numbering
- **Never** a section of `YYYY-MM-DD_market-sentiment.md`

---

## Structure — two categories, four questions each

**Jeff's own framing, 2026-08-29. Keep the order and the headings.**

### 1 — The report build

| | Question |
|---|---|
| **1a** | What went well in building the report this week? |
| **1b** | What problems did we see and resolve? |
| **1c** | What can we improve on the build itself? |
| **1d** | What do we continue doing? |

### 2 — The market analysis

| | Question |
|---|---|
| **2a** | The selection process — how did we decide on the pairs? What factors formed the bias? |
| **2b** | Day by day: **did the market FAVOUR the bias?** Score each session against **0.75 of that pair's typical daily range** (LD-128/129), not the close. **Do we know WHY it did or did not?** |
| **2c** | How can we improve so we can **foresee** where the market wants to go? |
| **2d** | What best practices do we continue? |

### 2b is graded on a DAY'S RANGE, not the close (LD-128/129, amended 2026-09-13)

**Jeff, 2026-09-13:** *"we need to determine first what is the average daily
pips movement of each pairs each day. Then if we hit that for the day in our
bias then it's already a win... A trader will not wait for a market reversal
before closing the trade."*

| | |
|---|---|
| **Target** | **0.75 × ATR(14)**, per pair |
| **ATR window** | the sessions **ENDING BEFORE** the graded week — never its own bars |
| **Measured from** | **that session's own open**, not Monday's |
| **A day counts** | favourable excursion ≥ target |
| **A week counts** | at least one such day |

**Why it changed a verdict on first use:** AUDCHF closed the week at −24.1 and
reads as a clean loss. It reached **0.90×** on Thursday — the market travelled
nine-tenths of a normal day in the called direction. **The close was measuring
when we stopped looking.**

**Publish the grid, not just the count.** Five columns of `×ATR` per pair shows
whether a win was one lucky session or a sustained read — AUDJPY hit on **3 of
5 days**, which the weekly figure cannot say.

**Scope (LD-4):** this is an observation about how far price travelled, never
an instruction to exit there.

---

**Close with an honest verdict** — the reference edition's was *"the process
improved a great deal and the analysis was mostly wrong. Both are true and they
should not be blended."*

---

## The rules that make it worth reading

**These are not stylistic. Each one exists because the alternative produces a
document that flatters rather than informs.**

1. **RECOMPUTE EVERY FIGURE BEFORE PUBLISHING IT.** The 2026-08-29
   retrospective verified all sixteen against the bars first. A retrospective
   full of remembered numbers is worse than none.

2. **STATE THE HONEST SCOREBOARD FIRST**, before any explanation of it. The
   reference opened with **1 read in 4** and **−230.5 pips**, above the
   analysis of why.

3. **DIRECTIONAL PIPS ARE NOT P&L** (LD-4). Say so in the footer, every time.
   There is no sizing in this repo, so these are the moves the reads pointed
   at, summed — nothing more.

4. **LABEL SMALL-SAMPLE STATISTICS AS DESCRIPTIVE.** The reference computed
   `corr(DXY, gold) = −0.87` on **five daily observations** and said plainly
   that this describes the week and is not evidence of the mechanism.

5. **NAME WHAT JEFF CAUGHT THAT THE GUARDS DID NOT.** That list is the most
   useful part of the review. Three of the reference week's findings were
   caught by him reading, and every one lived in a part of the report nobody
   re-derived.

6. **STRESS-TEST YOUR OWN RECOMMENDATIONS BEFORE PUBLISHING THEM.** In the
   reference week, two of five improvement ideas did not survive contact with
   the data — adding PCE would not have changed the selection, and the
   "dollar concentration" claim was weaker than written. **Say so rather than
   shipping five confident bullets.**

7. **SEPARATE THE PROCESS VERDICT FROM THE ANALYSIS VERDICT.** They can point
   opposite ways in the same week, and blending them into one comfortable
   sentence destroys both.

---

## Design treatment

**Utilitarian-polished, not editorial.** It is a working document for someone
who reads it to decide, not a landing page.

| Element | Reference implementation |
|---|---|
| Type | **Newsreader** display, **IBM Plex Sans** body, **IBM Plex Mono** for all figures |
| Ground | `#12151C` dark / `#FAF9F7` light — both themes, tokens on `:root` |
| Accent | amber `#C88A2E` / `#A96C1B`, used once for structure |
| Semantic | green `#6FB287` good, red `#D2726E` bad — **separate from the accent** |
| Opening | a **scorecard strip** of 5–6 tiles: reads correct, directional sum, falsifiers fired, near misses, editions built, guard count |
| Tables | `tabular-nums`, right-aligned figures, `overflow-x:auto` on every wrapper |
| Callouts | left-rule notes for findings; red rule for a defect, green for something that worked |

**Title:** a short noun phrase naming the week's story — *"The week the dollar
decided everything"* — not "Weekly Retrospective".

---

## What to carry forward each week

**A retrospective that does not connect to the last one is a diary entry.**

- **Score §4.6's running record** (LD-68) — confirmed / contradicted / null,
  cumulative n. **Publish the nulls**; a record that only lists hits is a story.
- **Re-check last week's improvement list.** Which items shipped, which were
  dropped, and why. The reference week's 1c list became LD-69 through LD-76.
- **Track the guard count** and what each new guard was built to catch.

---

## Provenance

| What | Where |
|---|---|
| Rule | LD-70, `docs/REPORT_SPEC.md` |
| Reference | 23–29 Aug retrospective, published 2026-08-29 |
| Scoring context | `docs/SCORING_BASELINE.md` |
