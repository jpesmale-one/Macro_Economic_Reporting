# WEEKLY REPORT REVAMP — build spec

**Source:** `Idea_dump/Weekly_Market_Sentiment_Revamp.txt`, Jeff, 2026-09-04.
Committed verbatim as input and never edited (the LD-7 rule for his drafts).

**Status: SPEC AGREED, NOT YET BUILT.** Five questions were put to Jeff on
2026-09-04 and answered; they are recorded as **LD-94 .. LD-98** below.
**§4 is now fully specified and unblocked.**

> *"We're already down 2 weeks. And I think we need to revamp the report …
> Basically this is a total revamp so our current process is up for change."*

---

## Why this supersedes the retrospective

**The 2026-09-04 retrospective closed with zero changes shipped** and two
named defects it declined to fix on one week of evidence. **This revamp fixes
both by construction**, on Jeff's authority rather than on my rank
correlations:

| Retro finding | What the revamp does |
|---|---|
| **73% of the score is lagging** (agenda item 6) | **Leading categories get weight 2, confirming 1.** Decided, not tuned. Item 6 is CLOSED. |
| **The room gate inverted** — ranked our winner last, a failing pair 2nd (item 7) | **Room and event-risk are removed from selection entirely.** Item 7 is CLOSED. |
| §4.0 priced only **3 of 11** rows correctly (item 1) | Week-ahead scoring is rebuilt on a different basis — **re-measure from scratch.** |
| **The three-pair floor forced a 324-pip loser** (item 4) | **LD-96: the floor is dropped.** |

**Item 5 (LD-90, the surprise term) was the one thing validated and it
survives** — a decision still scores by its surprise, not its direction.

---

## 1. Scope — weekly separates from daily

**This file specifies the WEEKLY report.** Daily monitoring becomes a separate,
lighter artefact and is **not** specified here.

**§5 Gold and §6 BTC are REMOVED.** Jeff: *"Currently I want to focus on Forex
first. These sections adds complications in our routine."*

**LD-97 — the weekly report is the DECISION ONLY.** §0, §1, §3, §7, §8 and §9
are dropped alongside §5/§6. The weekly is: **macro + week ahead → currency
ranking → the pairs.**

> **⚠ RECORDED OBJECTION, overruled by Jeff.** §1 is where the BoJ rate-check
> surfaced on 2026-09-04 — the single largest macro event of that week
> (JPY +2.87%, ~7× the next currency), which **no whitelist indicator could
> register** and which drove most of NZDJPY's −324 pips. Stripping §1 removes
> the only place that read can appear. **Jeff chose decision-only; this note
> exists so the cost is known, not to relitigate it.**

---

## 2. The fact tables (§2 of the draft)

**Six CSVs under `data/macro_indicators/`**, one per category, already created
by Jeff:

| File | Rows |
|---|---|
| `Production_Macro_Indicators.csv` | 19 |
| `Spending_Macro_Indicators.csv` | 23 |
| `Trade_Macro_Indicators.csv` | 8 |
| `Employment_Macro_Indicators.csv` | 12 |
| `Inflation_Macro_Indicators.csv` | 8 |
| `Interest_Rate_Macro_Indicators.csv` | 8 |

**Schema:** `Currency, Indicator, Frequency, <Mon-YY>, <Mon-YY>, …` — one
column per month, appended as the year runs.

**These replace `score_model.ROWS` as the source of truth.** That matters
beyond tidiness: **F-88 happened because §2.5 and §2.6 read the same indicator
from two hand-maintained places and disagreed inside one edition.** A single
keyed table makes that class of bug structural rather than vigilance-dependent.

**⚠ Header inconsistency to fix on first write:** `Production` uses `Aug-26`,
the other five use `26-Aug`. Normalise to one form — **`Aug-26`** — or every
lookup needs two code paths.

---

## 3. Base scoring — binary, leading-weighted

**Per indicator: +1 GOOD · 0 NEUTRAL · −1 BAD.**

**Per category, per currency:**

```
category_score = (sum of that currency's indicator scores / count) × weight
```

| Category | Weight | Role |
|---|---|---|
| **Production** | **2** | LEADING |
| **Spending** | **2** | LEADING |
| **Trade** | **2** | LEADING |
| Employment | 1 | confirming |
| Inflation | 1 | confirming |
| Interest Rate | 1 | confirming |

**Worked example (Jeff's own):** USD Production has 4 indicators scoring
`+1, +1, −1, 0` → `(1+1−1+0)/4 = 0.5` → `× 2 = +1.00`.

**Range: −9.00 to +9.00** (6 categories, max 2+2+2+1+1+1 = 9).

**Every (category, currency) cell has at least one indicator** — verified
2026-09-04 across all 48 cells, so the divisor is never zero.

### LD-94 — direction of goodness keeps the current channel logic

**Binary scoring changes the SCALE, not the question "which way is good".**
The existing rules are ported unchanged:

- **Unemployment / claimant counts: LOWER is better** for the currency.
- **Inflation runs through the RATE channel** — higher is better *until it
  passes the bank's own mandate ceiling* (F-70), each bank against its own
  band (LD-23). The SNB's is 0–2%, not 2%.
- **Everything else grades against CONSENSUS** where one exists (F-74), not
  against the previous print.
- **A released rate decision scores by its SURPRISE** (LD-90), not its
  direction. A fully-priced hike is not news.

**Why this is not negotiable-by-default:** F-66, F-68 and F-70 were all
direction-of-goodness bugs, and F-70 ran for days grading every rising-inflation
forecast as BAD for its currency. **The channel logic is the accumulated fix.**

---

## 4. Week-ahead scoring — the calibrator

### LD-98 — THE DAY IS THE UNIT, NOT THE CATEGORY

**Jeff, 2026-09-04:** *"In here we are scoring the day not the category. It can perceive as 'Does USD (for example) is positive or negative on Monday?' We don't look at it as the usual category separation."*

**§4 asks ONE question per currency per day: is this currency positive or negative today?** Categories do not enter it. **There is NO weight multiplier anywhere in §4** — the `× 1` in Jeff's JPY example is not a category weight, it is the day's score standing as itself.

**Category weights live ONLY in §3**, the base scoring off the fact tables. **Two separate scales that meet at the tally**, which is what "base + calibrator" means.

### The rules

**Each indicator scores +1 / 0 / −1 by subjecting the Cons–Fcst range to that indicator's own macro criterion** — the same channel logic as §3 (LD-94). e.g. `USD PMI Cons–Fcst > 50.5 → +1`.

**Then one score per currency per day:**

1. **Same day, DIFFERENT reference months → the LATEST month wins.** It is the more current read of the economy. Jeff's example: EUR Unemployment **JUL** and S&P Mfg PMI Final **AUG** on the same Monday → **the PMI carries the day**, and the JUL row is not counted.

2. **Same day, SAME reference month → they share the day, averaged.** Jeff's example: JPY Mfg PMI **AUG** and Consumer Confidence **AUG** → `(+1 +1)/2 = +1.00`. **No weight applied**, even though those two sit in different categories (Production and Spending).

3. **Week total = the sum of the five daily scores.** Jeff's example: USD `0, +1, +1, −1, +1` → **+2**.

**Range: −5 to +5** — five trading days, each capped at ±1.

### Why this shape is right

**It bounds the calibrator against the base.** §3 spans −9 to +9 and §4 spans −5 to +5, so **the week ahead can re-rank the board but cannot overturn it** — a currency needs a genuinely lopsided week to move more than a few places.

**And it makes a busy day worth no more than a quiet one.** A currency with four releases on Thursday scores that Thursday **once**, not four times. **That is the correct treatment**: a day is a day, and the alternative would let a crowded calendar outvote the macro base by accident.

## 5. The tally

```
FINAL = base (macro fact tables) + calibrator (week ahead)
```

Jeff: *"The result from the Macro Economic Indicators will be our base line.
Then the score from the Week ahead will serve as calibrator."*

**Example:** USD base +2, week-ahead +2 → **USD total +4.**

**Note this replaces LD-85's `k = 0.50` damping with a straight sum.** The
retrospective measured §4.0's old pre-release calls at **3 right of 11** —
worse than chance — so **the new week-ahead basis must be re-measured from
scratch** rather than inheriting that verdict either way.

---

## 6. Currency roles

| Role | Currencies | Bid when |
|---|---|---|
| **Safe haven** | USD, JPY, CHF | Risk **OFF** |
| **Commodity** | AUD, CAD, NZD | Risk **ON** |
| **Cyclical** | GBP, EUR | Either — *"majority they move with Risk On"* |

### LD-95 — Strong / Neutral / Weak is RANK-based: top 3 / middle 2 / bottom 3

**Not fixed thresholds.** Rank-based always yields tradeable currencies on both sides, which the pairing in §7 requires.

**The evidence:** on 2026-09-04 the whole board sat inside NEUTRAL (+0.83 to +5.31) under fixed bands — **8 of 8 NEUTRAL, and no pair could have been formed at all.**

---

## 7. Pair selection

### LD-99 — RISK REGIME IS AN OUTPUT, NOT A FORECAST

**Jeff, 2026-09-04:** *"We're not gonna try to forecast if the week ahead is going to be a Risk On or a Risk Off Week. It will come naturally in the result of our tally … Let's treat them as a category to fill not a forecast."*

**Nothing determines the regime. The regime DESCRIBES what the board permits.** Read the roles present in each band, then fill whichever categories the ranking makes available:

| Category | Formed when | Direction |
|---|---|---|
| **Risk OFF** | a **Safe haven** ranks above a **Commodity** | long the haven / short the commodity |
| **Risk ON** | a **Commodity or Cyclical** ranks above a **Safe haven** | long the cyclical-or-commodity / short the haven |
| **Either** | a **Cyclical** ranks above a **Commodity** | long the cyclical / short the commodity |

**This removes the circularity I flagged when the spec was drafted.** A regime *input* would have had to come from somewhere — Fear & Greed, or the board itself — and the second is circular: the regime could never disagree with the ranking it was meant to interpret. **Treating it as a label solves that by not asking the question.**

### Conviction ranks by the SCORE GAP

**Jeff:** *"let's utilize the rankings to identify which Risk Off pairs do we see as with the Highest Conviction. By combining Strong vs Weak, Strong vs Neutral, Neutral vs Weak…"*

| Tier | Combination | Why |
|---|---|---|
| **1 — highest** | **STRONG vs WEAK** | the widest score gap on the board |
| 2 | STRONG vs NEUTRAL | strong long leg, unremarkable short |
| 2 | NEUTRAL vs WEAK | unremarkable long, weak short |

**Conviction is the SCORE GAP, not the category.** A Risk Off pair is not inherently better than a Risk On one — **the spread between the two legs is what ranks them**, and that is the one term of the old confluence formula that survives this revamp.

### LD-96 — leg-disjoint SURVIVES, the three-pair floor is DROPPED

**No currency may be used twice** (LD-19 stands). **EF-3 is the reason:** on 2026-09-04 a single yen move would have hit three JPY-short pairs at once.

**But the minimum of three is gone.** Take the pairs that qualify — **two, or one, or none.**

**The evidence, and it is the cleanest of the week:** LD-35 demanded three pairs. Only two cleared. The forced third was **NZDJPY**, which §4.4 called *"the weakest of the three … if one pair should be dropped, it is this one"* **in writing, before the week started** — and it lost **324 pips**, more than the other two combined.

**This closes the open decision the retrospective referred to Jeff.**

---
## 8. What carries over unchanged

**These are not up for revision and the revamp does not touch them:**

- **LD-4 / NO MONEY PATH.** No lot sizes, entries, stops, targets, orders.
  Key levels are OBSERVATIONS of structure only.
- **LD-5.** Jeff's own TradingView drawings are never touched; check
  `draw_list` before clearing anything.
- **LD-3.** Calendars are SCHEDULE authorities, never VALUE authorities for a
  released actual.
- **LD-23.** No input that cannot be sourced for all eight currencies on equal
  terms. This is why the rate PATH stays unscored.
- **LD-42.** Weekly independence — nothing rolls over.
- **LD-48.** A falsifier fires on a real bar CLOSE only.
- **F-3.** The indicator list is a CLOSED SET; amendments are Jeff's call.
- **Format changes require Jeff's approval in advance** (R-27 enforces this).

---

## 9. Open before the first build

**✓ CLOSED 2026-09-04 — §4's shared-day weight.** Answered by LD-98: there is no weight in §4 at all. **The week-ahead pipeline is unblocked.**

**Still open, and none of these blocks the scoring pipeline:**

1. **CSV header format** — `Production` uses `Aug-26`, the other five use `26-Aug`. **I will normalise to `Aug-26` unless told otherwise**; it is a data-hygiene call, not a modelling one.

2. **Back-population** — do the six CSVs get filled from the existing 71 whitelist rows plus the capture history, or start empty from the next release? **Recommendation: back-populate.** The current rows are already reconciled against TE (LD-50, 0 unmatched on 2026-09-04), and starting empty means the first weekly has no base score at all.

3. **⚠ RISK-ON / RISK-OFF IS UNDETERMINED, AND §7 BRANCHES ON IT.** The pairing rules need to know the regime and **nothing in the draft says what sets it.** This is the one remaining gap with real modelling consequences.

   **Candidates, in the order I would rank them:**

   | Source | For | Against |
   |---|---|---|
   | **CNN Fear & Greed** | Already captured daily; explicit risk gauge; moved 55.40 → 35.26 in the week just ended | US-equity-centric, and it is one vendor's index |
   | **The board itself** | No new source — if safe havens rank top, that IS risk-off | Circular: the regime then cannot disagree with the ranking it is meant to interpret |
   | **Neither — publish all three scenarios** | Honest about uncertainty; Jeff's own example lists Risk On, Risk Off and Either side by side | Does not narrow the candidate list, which is what selection needs |

   **Jeff's draft actually implies the third** — his worked example shows all three buckets populated at once. **If that is the intent, say so and §7 becomes a presentation rule rather than a branch.**
