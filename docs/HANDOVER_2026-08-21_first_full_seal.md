# Handover — 2026-08-21 — first FULL seal, week of 17–21 Aug

> ## ⚠ NEXT SESSION STARTS WITH R-9, THEN R-8
>
> **R-9 — FETCH THE NEWS.** §1's two mandated sources (`investinglive.com`,
> `investing.com`) were **never fetched in any edition — zero references across
> all three.** Both return **200 at step 2 of the F-6 ladder** (a browser
> User-Agent, nothing more).
>
> **It cost three sealed conclusions.** The 19 Aug Treasury buyback — dollar
> −0.8%, 30y −9bp — explains the CHF anomaly (EF-2), Gold's move (§5), and
> BTC's (§6). All three were sealed as *"cause not identified"* while the cause
> sat on the front page of the site the spec named. See **F-17** in STATE.md.
>
> **R-8 (cut the noise) follows.** They are the same fix from two sides:
> interpretation expanded to fill the space where reporting should have been.

Session 3. Started with an unsealed 2026-08-19 edition and a stale continuation
prompt; ended with **two editions built and the week FULL-sealed**, eleven
decisions locked, and six facts promoted to the established-facts ledger.

**STATE.md's header is the authority on edition identity.** This file restates
it for convenience and goes stale the moment the next edition lands.

---

## 1. Resume protocol

Run these and compare against STATE.md's header — do **not** compare against a
hardcoded commit list (F-8):

```
git log --oneline -5
git rev-list --count HEAD
git status -sb
git log --oneline origin/main..HEAD    # unpushed count
```

Expect: edition **`2026-08-21` (r11, SEALED FULL)** — r9/r10/r11 are T4
amendments to a sealed edition, each disclosed in the edition itself, `data_asof`
**2026-08-21 16:40 PHT**, track **LEAN**.

**Read `docs/REPORT_SPEC.md` FIRST** — authoritative build spec. Then STATE.md.

⚠ **The spec is now BEHIND the implementation.** It still describes a
five-category model and an ±8.00 scale. LD-23 made Interest Rate category 6 and
the scale ±11.00. **Reconciling the spec is the first queued item (R-1).**

---

## 2. Where we are

**Two editions shipped this session:**

| Edition | State | Artifact |
|---|---|---|
| 2026-08-20 (r11) | UNSEALED | `a69403a7-a636-4ca2-8b41-1006e8c62806` |
| **2026-08-21 (r11)** | **SEALED (FULL)**, T4-amended ×3 | `eee6e597-8644-4c5d-b69b-db6879803abc` |

The 08-20 edition stays unsealed as history. It carries a staleness notice and
is superseded by 08-21.

**Blocked on nothing.** Commits are **unpushed** — derive the count with
`git log --oneline origin/main..HEAD` (F-8), never from this line. Pushing is
Jeff's call and he has not been asked.

---

## 3. Delivered this session

| Item | What |
|---|---|
| `reports/2026/Q3/2026-08-20_*` | Thursday edition, r11, unsealed |
| `reports/2026/Q3/2026-08-21_*` | **Friday edition, r8, SEALED FULL** |
| `pipelines/rate_model.py` | LD-23 — Interest Rate as category 6, inflation-vs-own-mandate |
| `pipelines/select_pairs.py` | LD-19 — leg-disjoint selection + net-exposure check |
| `pipelines/confidence.py` | LD-20 — the confidence tally |
| `pipelines/render_edition.py` | LD-24 — md → html with collapsible reference blocks |
| `pipelines/fng_block.py` | LD-25 — the F&G bar chart, generated from the capture |
| `data/raw/calendar/` | F-14 — immutable per-edition calendar captures |
| `data/raw/fng/` | LD-25 — immutable F&G captures (the endpoint has no history) |
| `STATE.md` | LD-14 … LD-25, F-13 … F-16, and the **established-facts ledger** |

---

## 4. Decisions locked (LD-14 … LD-25)

Full text with rejected alternatives is in STATE.md. The ones that bind daily
work:

| ID | Decision |
|---|---|
| **LD-14** | Week-ahead projections. Window is **Mon–Fri of the current week**, never rolling today+7d. |
| **LD-16** | Playbook is **weekly instrument selection** — bands → pairings → structure filter → zones. Replaces the swing/intraday split. |
| **LD-18** | Risk-off must be **enumerated every week even when nil**, and a nil category is proved on the **full matrix**, never on the extremes. |
| **LD-19** | Carried pairs must be **leg-disjoint**. Structure filter FIRST, then disjointness — **ordering is load-bearing**. |
| **LD-20** | Every carried pair states a **confidence** (HIGH/MEDIUM/LOW) with its arithmetic. Target ≥3 pairs. Language is binding: *high-probability reads, never guarantees*. |
| **LD-21** | Correlated pairs are a **secondary-entry list**, with the warning that taking a pair and its sibling is one position at double size. |
| **LD-22** | The edition is **self-contained** — §2, §3, §4.1, §5, §6 published in full every time, never by reference. |
| **LD-23** | **Interest Rate is category 6, weight 3.** Scored on inflation vs the bank's **own mandate** only. Scale is now **±11.00**. |
| **LD-24** | The HTML collapses **reference detail**, never the read. |
| **LD-25** | The F&G block is the **r9 bar chart**, opens §1, and is **generated from a persisted capture** so it cannot drift or silently degrade. |

---

## 5. Established facts (promoted by this seal)

**EF-1** market facts for the week · **EF-2** the CHF anomaly *as an
observation, not a mechanism* · **EF-3** correlated pairs inflate a scorecard
(measured at 4×) · **EF-4** the projection method *as a finding, not a validated
tool* · **EF-5** environment facts · **EF-6** what this seal explicitly does
**not** establish.

**Read EF-6 before citing anything.** It names the CHF cause, the method's
reliability, the Fed Chair, and Gold/BTC drivers as **not established**.

---

## 6. Open findings

| ID | Status |
|---|---|
| **F-1** | OPEN — the phantom guard is procedure, not tooling. Run it first, every run. |
| **F-7** | OPEN — `batch_run` defective, confirmed on a valid call. Single-symbol reads are the workaround. |
| **F-10** | OPEN — RBA needs a same-origin Referer; its page is JS-rendered anyway. |
| **F-11** | OPEN — **a 200 response is not proof of data.** Fired twice this week. |
| **F-13** | **FIX VERIFIED** — the span assertion fired correctly on its first real test. |
| **F-14** | **OPEN, NEW** — the TE calendar window rolls; a week cannot be rebuilt after the fact. Captures now persisted. |
| **F-15** | **OPEN, NEW** — a mandatory section (F&G) silently vanished across three editions and I sealed without it. **Every guard is a content check; absence is invisible to one.** Needs R-7. |
| ~~F-16~~ | **FIXED** — the renderer ate emphasis spanning a code span. Parser bug on the deliverable path. |
| ~~F-9~~ | **CLOSED** — `TvMsixLaunch.exe`, confirmed twice. |

---

## 7. Remaining — WITH RECIPES

**R-9. FETCH THE NEWS — §1 HAS NEVER USED A NEWS SOURCE.** *(first item)*
> *"we have bombarded the report with our interpretation and thoughts. But we
> are missing the news that could impact the currencies and other assets like
> Gold and BTC"*

**Recipe:** fetch `investinglive.com` and `investing.com/news/forex-news` with
a browser UA (step 2 of the F-6 ladder — verified working at wrap, 788KB and
1.2MB). Per item record **time (PHT) · what happened · which instrument it
moves · source**, grouped Geopolitical / Central banks / Risk events.
**An unexplained price move is a research trigger, not a finding** — search the
news for that date *before* writing "cause unidentified". Add a
source-presence assertion alongside R-7's section-presence one.

**R-8. CUT THE NOISE — DATA OVER INTERPRETATION.** *(second — and the same fix
from the other side)*
> *"there's a lot of noise and interpretations which I think can be compressed.
> let's focuse on Data not overflowing information"*

**Measured baseline, r11: 753 lines — 296 table rows (39%), 220 PROSE (29%).**
Full per-section breakdown and five specific cut proposals are in STATE.md
under `R-8`.

**The diagnosis, and it is mine to own:** §0 and §0b together carry **63 prose
lines — 29% of all prose in the edition — and none of it is market data.** It
is meta-commentary about the method. I have been writing the *reasoning* into
the deliverable instead of the *finding*.

**Target: prose under 15% of lines, tables and figures untouched.** Verify with
the LD-17 token diff — anything lost must be a reformat, never a figure.

**Resolve this tension explicitly when you write the rule:** LD-22 says publish
the data in full every edition; R-8 says cut. They do not conflict — **LD-22
protects DATA, R-8 targets INTERPRETATION.** A table row is data and stays; a
sentence explaining a table row must earn its place or move to STATE.md.

**R-1. RECONCILE `docs/REPORT_SPEC.md` WITH LD-23 … LD-25.** *(still critical)*
The spec describes 5 categories and ±8.00; the model is 6 and ±11.00. Also
fold in LD-19 through LD-24. **The spec is the authoritative build document and
it currently contradicts the code.**

**R-2. RUN MONDAY'S EDITION.** Monday carries **two blocks** — swing *and*
intraday — per the spec's cadence, and swing shows carry (LD-8).
Recipe: run both guards → **assert the calendar span** → capture the calendar
to `data/raw/calendar/` → pull the 70 whitelist rows from series pages →
re-score → grade the week-ahead projections → leg-disjoint selection →
confidence → draw zones → render → publish.
**Watch: AU inflation Wed 26 Aug** (AUD's weight-3 category, currently 0.00)
and **Jackson Hole 27–29 Aug**.

**R-3. GIVE NZDUSD A STRUCTURE READ.** It cleared the 1.00 floor at **+1.50**
for the first time on the new rate leg, and has never been charted. It is the
only risk-off candidate that has ever qualified.

**R-4. CLOSE THE 12-PAIR COVERAGE GAP.** Nine of 21 read. `chart_set_symbol`
then `data_get_ohlcv`, one symbol at a time — `batch_run` is defective (F-7).

**R-5. VERIFY THE FED CHAIR.** The 29 Jul minutes list Warsh in the Chair's
voting position. Never asserted; needs a second source before any edition names
a Chair.

**R-7. SECTION-PRESENCE ASSERTION IN THE RENDERER** *(from F-15)*.
The spec mandates §1–§6 plus the sub-blocks in spec §2.3. **Refuse to render an
edition missing any of them.** F-15 happened because every check is a *content*
check — a section that is absent has no figures to verify, so absence is
invisible. Only a manifest catches it.

**R-6. SOURCE PRICED ODDS FOR ALL EIGHT** *(optional, reopens LD-23 step 2)*.
An instrument exists for every currency — CME, SONIA, ESTR, CORRA, ASX RBA
Tracker, NZ OIS, TONA, SARON. Only USD was ever sourced, which is why the step
was dropped. Sourcing all eight would let it back in **on equal terms**.

---

## 8. Queued / parked

**P-1** standing coverage beyond the daily · **P-3** legacy pre-repo analysis ·
**P-4** ForexFactory access (retry with the F-6 header ladder) ·
**O-5** automated pulls — fires **T1+T3** and takes the full gate ladder.

---

## 9. Working agreements confirmed this session

- **Jeff catches what the method hides.** The correlated-pairs inflation
  (EF-3), the interest-rate gap (LD-23), the criteria that favoured USD, the
  missing Mon–Tue (F-13), **the vanished F&G section (F-15)**, and the
  downgraded F&G format (LD-25) — **all six were his catches, not mine.**
  Expect that and welcome it.
- **Content checks cannot see a missing section.** F-15 is the lesson: every
  verification in this repo asks "is this figure right?", none asks "is this
  section here?" A manifest is the only fix (R-7).
- **A nil result is a finding.** "No risk-off trade this week" is information —
  but it must be **proved on the full matrix**, not argued from the extremes.
- **Grade the method, don't patch it.** EF-4 records a one-directional error on
  surveys across three instances. The fix is more data, not a fudge factor.
- **Collapsing can hide staleness.** §8 said "no new findings" while F-14 was
  open in the same edition. Row counts on each summary help catch this.

---

## 10. Git state

Branch `main`, remote `origin` =
`https://github.com/jpesmale-one/Macro_Economic_Reporting.git`.

**FOUR COMMITS UNPUSHED as of this handover.** Derive the current state with
`git log --oneline origin/main..HEAD` — never from this line (F-8).
**Pushing is Jeff's call and he has not been asked this session.**
