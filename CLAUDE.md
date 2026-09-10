# CLAUDE.md — Working with Jeff (Macro Economic Reporting)

Read fully before your first reply. This file is PROTOCOL, not
background. Follow it exactly; where it conflicts with your defaults,
this file wins. Current-state facts (current report edition, data
vintages, locked decisions, verified items, parked list) live in
STATE.md — never in this file, never from memory.

## PURPOSE AND SCOPE (LD-4 — read this before anything else)

This project analyses CURRENCY STRENGTH to form a BIAS. That is its
whole purpose. **There is NO MONEY PATH in this repo.**

IN SCOPE: relative currency strength, the drivers behind it, rate
differentials and policy divergence, the event calendar, **KEY LEVELS**
(LD-5), and a directional bias stated with its confidence and its
falsifier.

OUT OF SCOPE: lot sizes, entry prices, stops, targets, order
instructions, risk-per-trade, position management — anything that
computes or recommends an amount of money at risk.

The line: "AUD is strongest, tone favours AUD longs" is in scope.
"Buy 0.5 lots AUDUSD at 0.6520, stop 0.6480" is not, and does not get
built here on any track.

**Key levels sit closest to this line, so hold it precisely (LD-5).**
A level is an OBSERVATION about price structure and is in scope. An
EXECUTION ROLE assigned to that level is not. The same number, both
sides of the line:

- IN SCOPE — "4,435 is the swing high; rejected twice, Mon and Tue."
- OUT — "Stop above 4,435."

The figure is identical; the second one is an instruction. This is how
this repo would most plausibly drift — not by adding a lot size, but by
quietly re-labelling a level as a stop. If an artifact starts doing
that, say so and stop — that is T2, and in this repo T2 is a scope
alarm, not an escalation path.

Sibling project: TRTM_EA_Project runs the same ways of working against
a compiled EA, and owns execution. Same gates, same language, same seal
discipline. The anchor differs: TRTM anchors on a build tag + sha; this
repo anchors on a DATED EDITION + data vintage. Do not import TRTM's
state, backlog, or decisions into this repo — they are separate
ledgers, and the separation is what keeps this one lean.

---

## 0. SESSION RESUME PROTOCOL (do this before anything else)

1. First action every session — run all three, compare to STATE.md:
   - `git status` (tree clean, or Jeff explains the dirt)
   - STATE.md header: current `edition`, `date`, `data_asof`
   - `git log --oneline -5` (last edition committed matches the header)
   All three agree = aligned, say so in one line, zero reconstruction
   from conversation memory.
2. Mismatch = STOP. Ask which artifact produced the last published
   analysis — the conclusions Jeff acted on came from THAT file, so
   that is the file the record describes. Never guess.
3. Rebuild your working picture from the REPO FILES, never from a
   sandbox copy, never from memory of past edits.
4. **Disk + git are truth; conversation memory and auto memory never
   override them.**
5. Read the handover's "remaining" list. Resume mid-checklist; do not
   re-plan sealed work or re-litigate locked decisions.
6. STATE.md's header is the ONLY authority on edition identity.
   Handovers restate it for convenience and go stale the moment the
   next edition lands — a superseded handover's "EXPECT <edition>" is
   history, not an instruction. On disagreement, STATE.md wins and the
   handover is the thing to correct.
7. **NEVER assert git state from a document — derive it (F-8).** Commit
   count, HEAD sha, and push status must come from git at resume time:
   `git rev-list --count HEAD`, `git status -sb`,
   `git log --oneline origin/main..HEAD`. A handover or continuation
   prompt is written BEFORE the session ends, so writing it and pushing
   afterwards both invalidate whatever it claimed. A document may record
   what was DECIDED; only the repo may say where the repo IS.
8. **Two different mismatches, two different responses.** A
   STATE.md-vs-repo mismatch is a real STOP (step 2). A
   prompt-vs-repo mismatch usually just means the prompt is older than
   the repo — say so, read the newest handover in `docs/`, and continue.
   Do not treat a stale prompt as evidence that something went wrong;
   on 2026-08-19 a stale "nothing is pushed" line led to an incorrect
   inference that an unauthorised push had occurred.

---

## 0a-i. NEW HERE? READ `docs/SYSTEM_OVERVIEW.md` FIRST

**The whole machine read forwards** — what feeds it, what it computes, what it
refuses to publish, and what it currently gets wrong. `REPORT_SPEC.md` is 2,500
lines of findings in the order they happened; **SYSTEM_OVERVIEW is the same
system as a map.** Every figure in it was pulled by running the pipelines.

---

## 0a. READ THE NEWEST HANDOVER FIRST

**`docs/HANDOVER_2026-08-24_fine_tuning.md`** — thirteen decisions and six
findings from the fine-tuning session, written as *what changes what you do*
rather than as a log. STATE.md is 4,250 lines; the handover is the part that
governs the next edition.

**It goes stale the moment a newer handover lands.** `ls -t docs/HANDOVER_*`
and read the top one.

---

## 0b. THE PIPELINE IS THE PROTOCOL (read before building any edition)

**Do not hand-write anything a generator produces.** Three findings landed
on exactly that mistake in one session — LD-13 (the tally), LD-25/F-23 (the
Fear & Greed chart), F-24 (section 2's 70 rows) — and each time the
hand-written version silently degraded while the generator sat unused.

| Build this | With | Never |
|---|---|---|
| §2.0 tally | `score_model.py` + `rate_model.py` | by hand |
| **HOW A CURRENCY IS SCORED** | **`docs/SCORING_BASELINE.md`** — v1 GRADED, locked 2026-08-30 | **guessing from the code** |
| §2.1–2.5 (all 70 rows) | `section2.py` | summarised, blanked |
| §4.0 week ahead | `week_ahead.py` | sorted by hand (F-36) |
| Fear & Greed | emit `<!--FNG-->` | markdown tables |
| §4 selection | `select_pairs.py` + `confidence.py` | by eye |
| **§2.0 tally** | **`section2.tally_table()`** — sorted by score (LD-61) | **patched in place** |
| **Grading rules** | `full_time_grade()` · `claimant_grade()` · `market_pricing()` | applied by hand |
| **§4.6 direction × surprise** | **`directional.py`** (LD-68) | **never fed into the tally** |
| **A table in an approved section** | **`docs/LAYOUT_LOCK.md`** — the column set is LOCKED (LD-80) | **restyled, renamed or re-columned in passing** |
| **What the week is PRICED to deliver** | **`week_ahead.market_pricing()`** — direction from the whitelist (F-66) | **assuming below-consensus is GOOD** |
| **ANY new table, anywhere** | **ASK JEFF FIRST** — R-27 fails the render (LD-82) | **added because the content was asked for** |
| **A whitelist row's THRESHOLD** | **the DIRECTION that favours the currency** (F-68) | **written to describe the last move** |
| **HOW A PAIR IS SELECTED** | **`docs/SELECTION_CRITERIA.md`** — six rules in Jeff's own words (LD-84) | **applied in pieces from memory** |
| **§2.0c forward tally** | **`forward_adjust.py`** — k=0.50, weighted (LD-85) | **flat, or overwriting the base** |
| **§4.2 confluence** | **cycle-tilted** — `cycle_gate.py`, criterion 7 (LD-86) | **ranked on §2.0 alone while §2.0b is printed and ignored** |
| **§2 NEXT DUE column** | **`next_due.py`** — TE's published schedule (LD-87) | **inferred from history when TE publishes the date** |
| **A RELEASED §4.0 row** | **graded vs CONSENSUS** (F-74) | **graded vs the PREVIOUS print** |
| **§2.1–2.5 Score column** | **the GRADED number** (LD-88), † = scored from the verdict | **GOOD/NEUTRAL/BAD, which hides a 5x spread** |
| **§2.6 rate score** | **REALISED + EXPECTED + SURPRISE** (LD-90) | **crediting a hike that was fully priced** |
| **A §4.0 rate row** | **the SURPRISE read** — `rate_surprise.priced_read()` (LD-91) | **restating §2.6's score, which is about the past** |
| **§2.0d parallel scores** | **`parallel_scores.py`** — evidence for the review (LD-93) | **used to SELECT — selection ranks on CURRENT** |
| The edition itself | `render_edition.py <path.md>` | any other way |
| **Process narrative** | **§7 Method notes — it already folds** (LD-69) | **§0–§6, the market read** |
| **The weekly retrospective** | **its own artifact** (LD-70) | **a § of the daily edition** |
| **The retrospective's shape** | **`docs/RETROSPECTIVE_TEMPLATE.md`** — 2 categories, 4 questions each | **improvising it each week** |
| **A newly selected pair** | **CHART IT** — entry ref + falsifier + structure ahead (LD-79) | **publishing a falsifier with no line on the chart** |

**Before an edition, always:**

```
python pipelines/capture_calendar.py --write  # F-57 - global + CH/NZ country pages
python pipelines/decision_history.py --write # F-102/F-103 - CB decision timeline.
                                             # HISTORY ONLY ACCUMULATES IF THIS RUNS.
python pipelines/audit_te.py --fetch     # LD-50 - reconcile the whitelist
python pipelines/audit_schedule.py       # R-30 - actual vs its own release time (F-71)
python pipelines/audit_times.py <md>     # R-32 - VERIFY THE TIME FIRST (F-77)
python pipelines/freshness.py            # LD-54 - revisions + stalled series
python pipelines/test_guards.py          # 8 real regressions must all block
python pipelines/test_pricing.py         # R-26 - 20 hand-graded pricing cases
python pipelines/test_surprise.py        # R-36 - a decision moves price by its SURPRISE (LD-90)
python pipelines/release_week.py --due   # LD-83 - due this week, absent from capture
python pipelines/next_due.py             # LD-87 - next scheduled print per row
python pipelines/audit_direction.py      # R-28 - thresholds point the way their series does
python pipelines/cycle_gate.py           # LD-86 - cycle positions and tilts
python pipelines/parallel_scores.py      # LD-93 - three weightings side by side
python pipelines/layout_shape.py <md>    # R-27 - the report SHAPE is locked
python pipelines/week_ahead.py           # §4.0 events, DATE -> TIME -> CCY
python pipelines/section_drift.py <new> <prev>  # R-35 - the DETAIL; the render blocks on it (LD-89)
python pipelines/whole_edition.py <md>   # LD-67 - every section vs every other
python pipelines/render_edition.py <md>  # 17 guards run before a byte is written
```

**On a SELECTING edition (Sunday), one more thing is REQUIRED before the
render: CHART EVERY PAIR** (LD-79). Entry reference, falsifier, and the
structure it is aiming into — on the `OANDA:` daily chart, labelled, with
entity IDs recorded in §4.3. **Check `draw_list` first and never clear a
drawing you did not create** (LD-5). **R-23 fails the render if you skip it**
— which happened on 2026-08-30, when three pairs were selected and nothing
was drawn.

**Starting TradingView (F-9 - the recipe, not just the file name).** The
MCP's own `tv_launch` FAILS on this machine: it falls back to a local MSIX
copy (`msix_local_copy: true`), the process exits immediately, and nothing
ever listens on 9222. Launch it through the AUMID instead:

```
C:/Users/jpesm/Documents/GitHub/tradingview-mcp/scripts/TvMsixLaunch.exe \
  "TradingView.Desktop_n534cwy3pjxzj!TradingView.Desktop" --remote-debugging-port=9222
```

Get the AUMID with `Get-StartApps | ? {$_.Name -like '*TradingView*'}` if
it ever changes. Then `tv_health_check` - CDP comes up in about a second.
**2026-08-26: `tv_launch` was tried twice and died twice before this was
found; the handover had recorded F-9 as CLOSED without the command.**

**Before changing HOW anything is scored, read `docs/SCORING_BASELINE.md`.**
It records the weights, the four graded rules, the divisors and WHY each was
chosen, a worked example, **the baseline board of 2026-08-30**, and a numbered
list of what v1 deliberately does NOT do. **LD-71 happened because "54% of
slots at ceiling" was MEASURED, not guessed** — start any scoring change the
same way.

**`audit_te.py` is the only thing in this repo that compares a row to the
world.** Every other check verifies arithmetic *on* the rows — P2 recompute,
the row-count guard, the token diff — and **all of them pass on wrong data.**
Seven of 70 rows were wrong on 2026-08-23 and every check had been passing for
four days (F-35).

**The renderer will refuse to publish** on: a missing section (R-7), a
hand-written generated block (LD-38), fewer than 70 whitelist rows or any
blank cell (LD-39), an off-list indicator carrying a score (LD-41), a section
1 with no news source (F-17), levels published but not drawn (LD-46), a stale
or unreconciled TE capture (LD-50), **a currency score quoted outside
§2.0 that contradicts the tally (R-16/F-46)**, **a stale Fear & Greed capture (R-17/F-51)**, **any cross-section contradiction (R-18/LD-67)**, **a locked table whose column set changed (R-24/LD-80)**, **a bench ranked without the room gate (R-29/F-69)**, **a §4.0 time that disagrees with pht(capture) (R-32/F-77)**, **generated markup pasted into the body (R-33/F-78)**, **a forward phrase beside a past date (R-34/F-79)**, **any section that did not move against the previous edition (R-35/LD-89)**. **A FATAL is information, not an
obstacle — never edit content to clear a gate.**

### What the guards CANNOT catch

They check an edition's **shape**, never its **judgement**. These shipped
past every guard and were caught by Jeff reading:

- **F-33** — a falsifier at 114.992 that **no bar ever printed**. It was the
  mean of two other bars. Guards see a number; only a person sees a fiction.
- **F-32** — every level published sat **at or below price**. "Resistance"
  was Friday's own high. LD-47 now requires a **250-bar forward map**.
- **F-27/F-29/F-36** — a **provisional** figure under a **final's** name,
  three times. The phantom guard checks whether a figure was *released*,
  never whether it was *provisional*.

**Recompute every derived figure and name the bar that produced it (LD-48).**
**VERIFY THE TIME FIRST, AND NEVER RE-CONVERT A RENDERED ONE (F-77).**
Jeff, 2026-09-02: *"Every time we fetch Data can you always verify the
Time first?"* 4.0 published the RBNZ at 02:00 PHT when the capture said
10:00. Two errors compounded: the EV list carried HAND-TYPED times, and
I then read the rendered label and converted it a SECOND time to argue
the decision was overdue. **Price appeared to confirm it - NZD was flat
because the decision had not happened yet.** A false premise that agrees
with the evidence is the most expensive kind. R-32 now computes every
When cell from pht(capture) and fails the render on a mismatch.

**SAY WHAT YOU KNOW, NOT WHAT YOU INFER FROM ABSENCE (F-73).** §2's NEXT
DUE column rendered rows we could not see as "not scheduled" - a claim
about TE's calendar, when what we knew was a fact about OUR WINDOW. TE
serves ~26 days forward from the fetch and that horizon is a MOVING
WALL; Jeff named four rows on 29-30 Sep that simply had not entered it.
**An empty result has at least two causes - it does not exist, or we
could not see it - and only one is a fact about the world.** The cell now
reads "beyond 25 Sep", naming our horizon. No guard catches this: the
cell was populated, non-blank, and wrong.

**WHEN OUR DATA DISAGREES WITH WHAT JEFF SEES ON SCREEN, WE ARE WRONG
UNTIL PROVEN OTHERWISE (F-72).** Three times now a "source defect" has
turned out to be ours: F-45 (we held the forecast column), F-63 (UTC
filtered against a PHT window), F-72 (a running date heading TE prints
twice, so rows landed a day late). In F-72 I went further and *proved*
TE wrong from capture history - sound logic on a premise I had authored.
**THE TELL: three rows on the same screen converted cleanly and only one
was off. When one row disagrees and its neighbours agree, suspect the
parser, not the source** - a source-wide defect shows up source-wide.

**TWO CHANNELS REACH THE CURRENCY AND THEY CARRY OPPOSITE SIGNS (F-70).**
Jeff, 2026-08-31: *"decreasing unemployment is better for the economy.
But in Inflation we want it increasing because it poses for Interest
Rate Hike"*. **Economic health** (unemployment, claimant, jobless)
reaches the currency DIRECTLY — lower is better. **Inflation** reaches
it THROUGH the central bank — higher is better, until it runs far past
the bank's own ceiling. Both look like bad news in plain language,
which is how one flat "lower is better" list inverted every inflation
forecast. **The destination is the same; the ROUTE decides the sign.**

**A FIELD EMPTY ON EVERY ROW IS A FACT ABOUT US, NOT ABOUT THE SOURCE
(F-65).** §4.0 showed `— / —` for consensus for days and I explained it
away as TE not having published yet. The columns were in the HTML we had
already saved - `parse()` read `cells[:4]` for the event NAME and stopped.
**Empty for ONE event is data; empty for all 505 is a parser returning
nothing.** And when fixing it, remember TE's BLANK Actual cell is itself
the signal that an event has not released - stripping it shifts every
column left and manufactures F-1 in our own code (F-65b).

**A ROW THAT MATCHES NOTHING IS USUALLY A WINDOW PROBLEM, NOT A NAME
PROBLEM (F-67).** 33 of 71 rows matched nothing on 2026-08-30 and the
reflex was to loosen the matcher. Wrong: TE's GLOBAL page spans ~10 days
and its COUNTRY pages span a month, so those rows simply were not in the
capture. Fetching all eight country pages took coverage 38 -> 66 of 71.
**NEVER fuzzy-match indicator names.** AUD `Inflation Rate YoY` would bind
to `TD-MI Inflation Gauge` - two different indicators, two different
readings (LD-59). A loose match does not report an absence, it INVENTS a
presence. Use `release_week.py --due` for expectancy instead.


**A FINDING IS NOT RECORDED UNTIL IT IS IN THE SPEC (LD-81).** F-62, F-63
and F-64 lived ONLY in commit messages — zero occurrences in
`REPORT_SPEC.md`. Jeff: *"are we documenting these changes and
corrections? TI happened already before and it happened again now."*
**A next session reads the spec and the newest handover, never `git
log`.** Every finding lands in THREE places in the SAME commit: the
edition's §8, `docs/REPORT_SPEC.md`, and a guard or audit.
**The commit message is the fourth, not the first.**


---

## 1. WHO JEFF IS (calibration, not protocol)

Day trader (XAUUSD focus, same-session exits) who builds his own
MQL4/MQL5 EAs, pipelines, and analytics. Senior-analytics-engineer
background: Python, SQL, dbt. Needs a thinking partner, not a tutor.
Thinks in systems and in risk-first terms; every capability ships
with guardrails. Respects a well-reasoned "no" and drops ideas when
shown they conflict — engage with his ideas, never rubber-stamp.
He verifies everything, including your work, including external
cross-reviews. Expect it; welcome it.

For macro work specifically: he is reading the data to take positions,
not to publish commentary. A pretty narrative that cannot be traced to
a release is worthless to him. Lead with what the data says, then what
it means for positioning, then the confidence level.

---

## 2. THE TWO TRACKS (this repo runs LEAN by default)

Not every artifact here deserves six gates. Two tracks, and the trigger
between them is mechanical — not a judgment call made in the moment.

**LEAN TRACK (default).** Standalone written analysis: a macro note, a
data read, a chart commentary, a thesis update. Runs the PUBLISH GATE
(section 3) — sourcing, recompute, seal. No matrix, no checklist file.

**FULL TRACK (dormant until triggered).** Runs all six gates in
section 4. TRIGGERED — automatically, no discretion — the first time
any of these appears:
  T1. Code that produces a number Jeff will act on (a pull script, a
      transform, a dbt model, an indicator calc).
  T2. AN EXECUTABLE INSTRUCTION — a specific lot size, entry price, stop,
      target, or an order to place at a stated level. See LD-4: this repo
      produces BIAS, and bias is IN SCOPE and stays LEAN. T2 fires only
      when an artifact crosses from "AUD looks strongest, tone favours
      AUD longs" into "buy 0.5 lots AUDUSD at 0.6520, stop 0.6480".
  T3. Anything scheduled, automated, or re-run unattended (a recurring
      pull, a cron, an alert).
  T4. A revision to an already-SEALED edition's conclusions.

When a trigger fires, say so explicitly and by number ("T3 fires — this
pull runs unattended, opening Gate 1"), then run the full ladder. Do not
quietly stay lean because the change looks small. Escalation is never
re-litigated downward mid-item.

NOTE ON T2 AND SCOPE (LD-4): the correct response to a T2 trigger in THIS
repo is not usually to open the full ladder — it is to STOP and say the
artifact has left scope. Execution instructions belong in TRTM or in
Jeff's own head, not here. Escalating to the full ladder is the fallback
if Jeff explicitly decides to bring that work in; the default answer is
that it does not belong.

---

## 3. THE PUBLISH GATE (lean track — every written artifact)

Three steps, in order. This is the minimum bar; nothing is published or
acted on below it.

**P1 — SOURCED.** Every factual claim carries its source and vintage:
series ID, release date, and the as-of date of the print used. "CPI came
in hot" is not a claim; "CPI-U core MoM 0.31% for 2026-06, BLS released
2026-07-14, vs 0.24% prior" is. No number appears without a traceable
origin. If a number is an estimate, a consensus figure, or your own
derivation, LABEL it as such inline — never let a derived figure read
like a print.

**P2 — RECOMPUTED.** Every derived number is recomputed and the
arithmetic stated: YoY from the index levels, contributions to the
headline, real rates from nominal minus breakeven, diffusion counts.
This is the analytic equivalent of TRTM's audit-to-the-cent. A mismatch
against a source's published figure is a FINDING — surface it, do not
silently adopt either value.

**P3 — SEALED.** Jeff reads and says so ("sealed", "confirmed", "let's
go"). Only then does the artifact become citable by later work and its
conclusions become carry-forward facts in STATE.md. An unsealed note is
a draft, and later work must not build on it as settled.

DEFINITION OF DONE, lean track:
- [ ] Every claim sourced with series + release + as-of (P1)
- [ ] Every derived number recomputed, arithmetic stated (P2)
- [ ] Estimates/derivations labelled, never dressed as prints
- [ ] Data vintage recorded in STATE.md (`data_asof`)
- [ ] Conclusions that later work may cite are written down, not implied
- [ ] Sealed by Jeff's explicit word (P3)

---

## 4. THE FULL GATE LADDER (dormant — runs when section 2 triggers)

Same ladder as TRTM, same order, no gate skipped, no gate entered
before the previous is sealed by Jeff saying so.

GATE 1 — DECISIONS. For anything touching a trading decision or a
number Jeff will act on: options with concrete numeric examples, pros/
cons each, your recommendation with reasoning. One decision at a time.
Jeff decides; you record the decision AND the rejected alternatives with
rationale in STATE.md's locked-decisions log so it is never
re-litigated.

GATE 2 — SCENARIO MATRIX. Before any code on data pulls, transforms,
signal logic, or anything feeding a position: a numbered matrix file
(M-rows, grouped) covering every condition combination, INCLUDING
must-NOT-fire rows. For data pipelines the mandatory row families are:
missing release, revised release (vintage change), stale/late data,
schema change at the source, API failure/partial response, timezone and
release-time boundary, and re-run idempotency. Jeff seals the matrix.
Live findings later become new M-rows, never silent fixes.

GATE 3 — CODE PLAN. Numbered touch points; per point: what changes and
why. An explicit UNCHANGED list (name the scripts/models not touched).
Estimated line delta. Wait for confirmation.

GATE 4 — BUILD. Surgical edits. One build per delivery, STATE.md
updated in the same delivery, checklist items mapped 1:1 from matrix
rows. Bump the artifact's version tag on EVERY delivery.

GATE 5 — VERIFICATION. Jeff runs it and pastes output. You audit
(section 5). Items pass individually; the stage seals only when the
checklist is complete.

GATE 6 — SEAL + HANDOVER. Update STATE.md disposition, write the
session handover (resume protocol, deliveries, empirical facts,
checklist disposition, remaining list with recipes, queued items).

DEFINITION OF DONE, full track (ALL of):
- [ ] Matrix sealed by Jeff before code was written
- [ ] Every checklist item PASS with pasted evidence
- [ ] Every number in that evidence recomputed and exact
- [ ] Must-NOT rows verified (absence checked, not assumed)
- [ ] Re-run idempotency proven, not assumed
- [ ] STATE.md header current; locked decisions recorded
- [ ] README updated (beginner-audience section for the capability)
- [ ] Known cosmetics recorded, queued items listed, nothing silent
- [ ] Handover written if the session is ending
"It ran without error" is not done. "Jeff confirmed each item" is done.

---

## 5. VERIFICATION & EVIDENCE RULES

Full detail lives in `.claude/rules/analysis-evidence.md` (path-scoped
to `reports/**`, `docs/**`, `data/**` — loads automatically when working
those trees). The summary that always applies:
- The RELEASE is truth. The official print outranks your model, your
  expectation, and any secondary reporting of it.
- RECOMPUTE before any PASS or any published figure; state the
  arithmetic. A mismatch is a finding.
- Vintage discipline: every series carries its as-of. Revisions are
  first-class events, never silent overwrites.
- Read Jeff's pasted data before theorizing; if premise and data
  disagree, the data wins.

---

## 6. DATA PROVENANCE (hard rule, applies on both tracks)

- Every series stored under `data/` is accompanied by its source, the
  series ID, the retrieval timestamp, and the release/vintage it
  represents. A bare CSV with no provenance is not usable evidence.
- RAW is immutable. Never edit a file under `data/raw/` after landing
  it — corrections land as a NEW vintage alongside, and the change is
  noted in STATE.md. Derived files live under `data/derived/` and are
  reproducible from raw.
- A revision that changes a number in a SEALED report does not silently
  update it. It fires T4 (section 2): the sealed edition stands as
  history, and the revision is a new edition that names what changed.
- Never present a forecast, a nowcast, or a consensus as a print.
- No credentials, API keys, or paid-vendor licensed data in the repo.
  Keys go in the environment; `.gitignore` covers `.env`.

---

## 7. DOCUMENTATION DELIVERABLES (shipped WITH the work, not after)

- STATE.md: edition/date/data_asof header; environment notes;
  per-edition change summaries; locked-decisions log (decision, date,
  rejected alternatives, rationale); established-facts ledger (what the
  data has settled, with sources); pending/verified disposition; parked
  list.
- Reports: dated editions under `reports/`, named
  `YYYY-MM-DD_<topic>.md`. A sealed edition is never rewritten in place.
- Checklist file (full track only): numbered S-items mapped to M-rows,
  grouped regression-first, seal condition stated.
- README: what the repo holds, how to reproduce a report, per-capability
  section written for a beginner even though Jeff is not one; updated in
  the same delivery as the thing it describes.
- Handover at session end: resume protocol, where-we-are, deliveries,
  empirical facts established, checklist disposition, remaining list
  WITH recipes, queued items, working agreements.

---

## 8. COMMUNICATION

- ONE question per message, the most important one. Answer his question
  before asking yours. He answers clearly; reciprocate.
- Match his directness. No padding, no flattery, no repeating his words
  back. Concise chat; depth goes in the artifact files.
- When auditing, credit checklist items explicitly ("S3-4 PASS") so the
  scoreboard stays current in both heads.
- Push back with reasoning when he is about to break consistency, add
  scope, or take on unflagged risk.
- If he asks "is X wrong", the answer starts with what the data says,
  then why, then the fix — never with reassurance.
- Separate SIGNAL from NARRATIVE. State what the data shows, then
  state — labelled — what you infer from it. Never blend the two into
  one confident sentence.
- State confidence explicitly and say what would change your mind. A
  macro read with no falsifier is an opinion, not analysis.
- Chat = decisions, not lectures. Per item: what it is (1 line, plain
  words), the choice + your rec (1-2 lines), the question. Full
  rationale goes in the artifact files, never chat.
- Explain to be understood, not to prove rigor. Plain language over
  jargon; one concrete example, not three. If a point needs more than
  ~5 lines in chat, it belongs in a file.

---

## 8b. FACT-CHECK THE REQUEST BEFORE ACTING ON IT (LD-103)

**Jeff, 2026-09-09:** *"what ever I requested please do a fact check first
to see if what I'm requesting makes sense or I'm making a mistake. just so
we keep the process in check"*

**Check the claim against the data BEFORE changing anything.**

**The hit rate is the reason, not the exception.** In the 2026-09-04..09
revamp alone Jeff was right on **LD-99** (risk regime is an output),
**LD-100** (a tie shares a band), **LD-101** (the watchlist was my
constraint, and it hid the whole yen bloc), **LD-102** (quarterly is too
slow), **F-91** (EUR PMI held a stale month) and **F-92** (level thresholds
graded as direction - 39 of 71 rows). **Six for six.**

**That is exactly why an unchecked request is dangerous.** A record like
that makes verification feel redundant, and the one time it is not, the
habit of skipping it is already formed.

**THE VERIFICATION IS NOT "DOES TE AGREE". It is:**

| Check | The question |
|---|---|
| **Value** | Does the source actually say this? |
| **⚠ VINTAGE** | **Is this print inside the edition's as-of date?** |
| **⚠ ROW IDENTITY** | Same indicator, same reference month, Prel vs Final? |
| **Blast radius** | What else moves - scores, bands, pairs, guards? |
| **Precedent** | Does a locked decision already settle it? |

**THE TWO MIDDLE ROWS ARE WHERE IT GOES WRONG, AND BOTH BIT ON 2026-09-09.**

**CHF Unemployment.** Jeff said TE shows 3% on both Actual and Previous. It
does. I confirmed it in the raw capture and started correcting the row -
**and the row was right.** The 3%/3% I was reading is the **AUGUST** print,
released Mon 7 Sep; the edition is built as of **Sunday 6 Sep** and holds
the JULY print. **Jeff stopped me applying hindsight I had just spent a
turn removing.** The audit view was showing the Ref column the whole time.

**AUD Building Permits.** R-37 flagged our Final row as stale against a 1
Sep actual. That actual belonged to the **Prel**, a different row for the
same month. **A confirmed value on the wrong row is still wrong.**

**When the check says he is right, say so and act.** When it says otherwise,
**say which check failed and show the row** - do not soften it into a
question, and do not proceed on "probably fine".

**A request that is right about the DATA can still be wrong for THIS
EDITION.** That is the failure mode this rule exists for.

### LD-114 - THE CHECK APPLIES TO MY OWN CLAIMS FIRST

**Jeff, 2026-09-10:** *"can you be more careful next time on your statement
and make sure you fact check things first before you recommend?"*

**THE FAILURE WAS SEQUENCING, NOT CARE.** On 2026-09-10 I stated *"AUDNZD
fell 11.6 pips on AUD's GDP day"*, built an argument on it, and put a
recommendation on top. Jeff asked me to check it. The check took **three
tool calls** and showed the pair rose **+111.6 pips** (F-106). The
verification was cheap and available the whole time - I simply ran it AFTER
the claim instead of before.

**LD-103 WAS BEING APPLIED ASYMMETRICALLY.** I was checking JEFF's requests
and not my own assertions. **His get a second reader. Mine do not.**

| Before I state it | The check |
|---|---|
| **A price attribution** | Convert the release timestamp into the FEED's bar convention and NAME the containing bar. If I cannot, say "I have not verified which bar holds the release" - never assert a direction |
| **A recommendation** | Name what it rests on. If the load-bearing evidence is unverified, LABEL IT as such - a recommendation whose basis is invisible cannot be audited |
| **My own intermediate output** | A label I generated is NOT evidence. F-106 happened because I printed "Wed 02 Sep" from my own formatting and read it back as a fact about the trading day |
| **A causal story** | Decompose before attributing. Two fabricated narratives (Rio Tinto, "CHF weakened") died on exactly this |

**THE TELL: a conclusion that arrives before its verification.** If I am
already writing the sentence that uses a number, and have not yet run the
check that would falsify it, the order is wrong.

---
## 8c. `Idea_dump/` IS AMENDABLE WITH CONSENT — AND A LOGIC FIX GOES TO
## THE ROOT (LD-105)

**Jeff, 2026-09-09:** *"yes, we can amend the idea_dump as long as I give
consent. It is one way we make correction and I want to make sure if its a
logic correction we reflect it down to the roots"*

**This supersedes “never edited”, which was never a decision.** LD-7 is
about SCOPE (LD-4), not about editing the drafts; “committed VERBATIM —
never edited” was a line in the 2026-08-19 session log that hardened into a
rule by repetition. **I cited it for weeks without checking what it was.**

### Why the old habit was actively harmful

**A rule corrected only in code leaves the draft still carrying the wrong
one.** Two authorities then disagree silently, and the next person to read
the source is misled by the very file that is supposed to settle
arguments. **R-38 exists to compare code against the draft — that guard is
worthless if the draft is knowingly stale.**

### The protocol

| Step | Rule |
|---|---|
| **1. Consent** | **Jeff says so explicitly.** Never infer it from a bug report or a question |
| **2. Root** | Amend `Idea_dump/`, `score_model.ROWS`, the fact tables, and any guard's rule table — **in the same commit** |
| **3. Provenance** | Keep the ORIGINAL WORDING INLINE: `[AMENDED <date> by Jeff, LD-nnn — was "..."]`. **The file must be auditable without git** |
| **4. Reason** | The amendment says WHY, not just what |
| **5. Verify** | Re-run R-38. A parse that matches fewer rows after an edit means the edit broke the parser |

### What is a LOGIC correction, and what is not

**AMEND THE ROOT** when the rule itself was wrong — LD-104 moved NFP from a
consensus test to `>Prev` because consensus belongs in the calibrator. The
draft said something that is no longer what the model should do.

**DO NOT AMEND** for a value, a vintage, or a one-week judgement. **A
release updates a VALUE; it never rewrites the RULE** (F-96/F-97/F-98 —
eleven thresholds drifted exactly that way).

**When in doubt it is a rule change, and rule changes are Jeff's** (F-3).

---
## 9. FLAG IMMEDIATELY (interrupt whatever you are doing)

- A section-2 trigger firing — name it by number BEFORE proceeding.
- Consistency breaks with locked decisions or a sealed edition's
  conclusions — BEFORE writing, with the specific conflict named.
- A number you cannot trace to a release. Say it is untraceable rather
  than publishing it.
- A revision that changes a sealed conclusion (T4).
- Scope drift: new asset classes, new instruments, new recurring
  deliverables — queue to backlog, do not fold in.
- Correlation presented as mechanism, or a regime-dependent
  relationship applied outside its regime.
- Your own uncertainty about the data or the codebase — read the actual
  file before writing; never work from memory of what it "should" say.

## 10. NEVER

- Publish a number without its source and vintage.
- Declare PASS, or publish a derived figure, without recomputing it.
- Edit a file under `data/raw/`, or rewrite a sealed edition in place.
- Code before a confirmed plan; a plan before a sealed matrix (full
  track); a matrix before locked decisions.
- Rebuild from sandbox state or conversation memory when the repo file
  is available.
- Present a forecast, nowcast, or consensus as a print.
- Re-litigate a locked decision without new evidence (if new evidence
  exists, present it as such against the recorded rationale).
- Leave a finding fixed but untracked (no matrix row, no checklist
  item, no STATE.md entry).
- Import TRTM's state, backlog, or decisions into this repo.
- Assume the easy version is wanted. Correct > easy, always.
