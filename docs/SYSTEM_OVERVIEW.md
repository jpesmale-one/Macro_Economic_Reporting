# SYSTEM OVERVIEW — how the bias gets built

**Written 2026-09-03**, from the live repo rather than from memory: every
figure below was pulled by running the pipelines, not recalled.

**What this file is for.** `REPORT_SPEC.md` is 2,500 lines of findings and
decisions in the order they happened. **This is the same system read
forwards** — what feeds it, what it computes, what it refuses to publish, and
what it currently gets wrong. Start here; go there for the why behind any
single rule.

| | |
|---|---|
| Whitelist rows | **71** across 8 currencies |
| Pipelines | **29** |
| Blocking guards | **15** numbered R-rules |
| Editions published | **15**, 19 Aug – 3 Sep |
| Findings recorded | **35** (F-nn) |
| Decisions recorded | **79** (LD-nn) |

---

## 1. The thesis

The report exists to answer one question early: **is a central bank going to
move, and which way?** Everything else is machinery in service of that.

> *"Production, Spending and Trade tends to predict the result of Employment
> and Inflation. And Employment and Inflation tends to predict what would be
> the Interest rate decision. Because the Interest Rate dictates if the
> Currency is Strong or Weak."* — **Jeff, 2026-08-29**

**That chain is the spine of the scoring.** Six categories ordered by how
early they speak. A currency whose upstream data is improving has a rate case
**forming**; one whose inflation is already high has a case that has **already
happened** — and the second is worth less, because the market has traded it.

---

## 2. Build sequence

**Every edition runs this order. Nothing downstream is written until the step
above it passes.**

| # | Step | Tools |
|---|---|---|
| 1 | **Capture the calendar** — TE global page plus all eight country pages (~900 rows with actual/previous/consensus/forecast) | `capture_calendar.py` |
| 2 | **Reconcile against the source** — the only check that compares our data to the world | `audit_te.py` `audit_schedule.py` `audit_times.py` `freshness.py` |
| 3 | **Score the eight currencies** — 71 rows → six weighted categories → one number on a ±11.00 scale | `score_model.py` `rate_model.py` `rate_surprise.py` |
| 4 | **Price the week ahead** — each release graded on expectation vs last print, folded in at half weight | `week_ahead.py` `forward_adjust.py` `next_due.py` |
| 5 | **Rank, gate and select** — spread ranks, room/risk/cycle re-rank, leg-disjoint filters | `selection_gates.py` `cycle_gate.py` `select_pairs.py` |
| 6 | **Render, or refuse** — 15 guards before a byte is written | `whole_edition.py` `render_edition.py` |

**The global page spans ~10 days; the country pages span a month.** Fetching
all eight took coverage from 38 to 66 of 71 rows (F-67). **A row that matches
nothing is usually a WINDOW problem, not a NAME problem** — and the horizon is
a moving wall about 26 days out, so "not scheduled" is a claim about us, not
about the calendar (F-73).

---

## 3. Fundamental analysis

### 3.1 The whitelist is a closed set

**71 named indicators across 8 currencies.** Nothing is added without an
explicit decision (F-3). **A loose match does not report an absence — it
invents a presence**, which is why matching stays exact and expectancy is
handled by `release_week.py` instead (F-67).

| Category | Rows | Weight | Stage | What it answers |
|---|---|---|---|---|
| Production | 19 | 1 | leading | Is output expanding? |
| Spending | 23 | 1 | leading | Is demand holding up? |
| Trade | 8 | 1 | leading | Is external demand paying? |
| Employment | 13 | 2 | confirming | Has it reached the labour market? |
| Inflation | 8 | 3 | confirming | Has it reached prices? |
| **Rate** | 8 | 3 | decided | Did the bank act — and was it a surprise? |

*Rate is scored by `rate_model.py` against each bank's own mandate, not from
the whitelist. Mandates are not all 2% (LD-23).*

### 3.2 Each row returns a graded magnitude

**Not GOOD/BAD. 52 of 71 rows** carry a rule returning a number in
−1.00 … +1.00. The remaining **19 have no rule pattern** and fall back to a
three-state verdict — Jeff's hand-curated rows (LD-57/58/59) — **marked with a
dagger** so a full mark earned from a rule is never confused with a full mark
taken by default (LD-88).

**Why graded (LD-71).** Two rows both reading GOOD could differ by a factor of
five — JPY Industrial Production **+1.00** against USD Industrial Production
**+0.20**. **26 of 48 category slots sat pinned at their ceiling**, and a
maxed slot cannot register good news, only bad.

**Magnitude comes from the rule; SIGN comes from the verdict column** —
`graded_signed()`. `>Prev` and `<Prev` describe a COMPARISON, not a direction
of goodness (F-62).

### 3.3 Direction of goodness is never assumed

**Two channels reach a currency and they carry opposite signs (F-70):**

| Channel | Series | Route | Sign |
|---|---|---|---|
| **Economic health** | unemployment, claimant count, jobless claims | directly | **lower is better** |
| **Rate** | inflation, CPI, PPI | through the central bank | **higher is better** |

**Both read as "bad news" in plain language**, which is exactly how one flat
"lower is better" list once inverted every inflation forecast. **The
destination is the same; the ROUTE decides the sign.**

Inflation is not unconditionally good — past the bank's own ceiling it becomes
a policy problem, so the rule is mandate-aware with a 1.5pp overshoot
tolerance.

### 3.4 A rate decision is scored on its SURPRISE

> *"A central bank decision moves price by its surprise component only. Level
> of rates → already discounted. Change in the expected path → that's the
> tradable variable."* — **Jeff, 2026-09-02**

**This week proved it twice. Both decisions landed exactly on consensus and
neither carried information:**

| Decision | Consensus | Actual | Surprise | Currency did |
|---|---|---|---|---|
| **RBNZ** hiked | 2.75% | 2.75% | **+0.00** | **NZD −108 pips** |
| **BoC** held | 2.25% | 2.25% | **+0.00** | **CAD +53 pips** |

```
rate_score = (REALISED + EXPECTED + SURPRISE) / n * 3
surprise   = clamp((actual - consensus) / 0.25, -1, +1)
```

**A fully-priced hike earns nothing extra.** Before LD-90 the model would have
scored the RBNZ **+1.00 on a session that cost 108 pips**. A surprise of None
is UNMEASURABLE and drops out of the average — scoring it zero would assert
the market was unsurprised.

**⚠ What is deliberately NOT scored: the forward track.** That is what
actually moved NZD — markets had ~95bp of tightening priced to June 2027
against the bank's own 25bp. **No calendar publishes an OCR track for all
eight currencies**, and LD-23 forbids an input we can source for only one or
two. **It is commentary in §3, never a number.**

### 3.5 The forward adjustment

**§2.0c prices the week in rather than waiting for it (LD-85):**

```
adjusted = base + 0.50 * SUM( verdict * category_weight )
```

**Weighted, not flat** — through the tally's own weights, so a forecast in a
heavy category moves the score more than one in a light category. **k = 0.50
is the largest value at which no currency's rank is decided by a single
forecast**, and it is testable: §4.0 records the projections in advance.

**Released rows are excluded** — they are already in the base via the
whitelist, and adjusting them too would double-count. **The base is never
overwritten**; both numbers publish side by side.

---

## 4. Technical analysis

**The macro score RANKS candidates. It does not select them.**

> *"Once you have a candidate pair we can check if the price is still have the
> bandwidth to move … we may want to look for other pairs with the same or a
> little bit lesser conviction than GBPUSD but with room to move in the favor
> of our bias."* — **Jeff, 2026-08-29**

| Gate | What it measures | Effect |
|---|---|---|
| **Room to move** (LD-73) | fraction of the 45-bar daily range lying IN the bias direction | re-ranks |
| **Event risk** (LD-73) | weighted count of what is STILL AHEAD on either leg — CB 3, high-impact 2, other 1 | downgrades, never vetoes |
| **Cycle position** (LD-86) | leading vs confirming, normalised; bounded ±50% | re-ranks |
| **Leg-disjoint** (LD-19) | no currency appears twice | filters |

```
confluence = (spread/8 + room + inverted_risk) / 3
             then scaled by the cycle tilt, bounded +/-50%
```

**Room exists because a pair was once selected at 94.4% of range with a LONG
bias and lost 110.9 pips** (F-32). **A multiplier, not a fourth term** — a
fourth term would dilute room from a third of the score to a quarter, and room
is the term that must not weaken (F-69).

**Every selected pair is charted** (LD-79) — entry reference, falsifier, and
the structure it is aiming into, on the `OANDA:` daily, with entity IDs
recorded in §4.3. **R-23 fails the render if it is skipped.**

**A pair leaves only on its FALSIFIER** (LD-29): a real bar **close** beyond a
level set more than one ATR away (LD-48). **Never on conviction, never on a
bad session.** A narrowing edge is a reason to watch, not to exit.

**Selection criteria in full: `docs/SELECTION_CRITERIA.md`** — seven rules,
six in Jeff's own words and one (the cycle gate) he ratified rather than
authored, flagged as such.

---

## 5. Where it stands, 2026-09-03

| CCY | Tally | Cycle gap | Position |
|---|---|---|---|
| CAD | +6.46 | −0.19 | aligned |
| GBP | +5.31 | −1.15 | IN THE PAST |
| EUR | +4.73 | −0.10 | aligned |
| NZD | +3.06 | −0.69 | IN THE PAST |
| AUD | +1.97 | +0.70 | BUILDING |
| JPY | +0.83 | −0.15 | aligned |
| USD | +0.59 | +0.60 | BUILDING |
| CHF | −0.28 | +1.28 | BUILDING |

**The locked set, four sessions in:**

| Pair | Move | Room | To falsifier | Read |
|---|---|---|---|---|
| GBPAUD long | −77.5 | 0.66 | 281 | reversed 93 pips in one session |
| CADCHF long | **+53.0** | **0.02** | 223 | the only winner — and out of room |
| NZDJPY long | −163.5 | 0.60 | 194 | lost ground every session |
| **SUM** | **−188.0** | | | direction, not P&L (LD-4) |

**All three falsifiers intact — nearest is 2.0 ATR clear. The set stays
locked.**

---

## 6. The open problem

**The model is built to see a hike coming. Measured against its own weights,
it mostly sees one that has already arrived.**

| Stage | Weight | Share |
|---|---|---|
| LEADING — Production, Spending, Trade | 3 | **27%** |
| CONFIRMING — Employment, Inflation | 5 | 45% |
| RATE — the decision | 3 | 27% |

**73% of the score is the thing being PREDICTED. 27% is the thing that
predicts it.**

**Rather than re-weight on three sessions, §2.0d publishes three schemes side
by side (LD-93) and selection continues to rank on CURRENT:**

| CCY | Current | Equal | Leading-tilt | What it says |
|---|---|---|---|---|
| **NZD** | +3.06 | +0.43 | **−0.34** | 4th → **last**. The week's only losing leg. |
| **CHF** | −0.28 | +1.64 | **+5.85** | last → **2nd**. And we are SHORT it in the only winner. |

**Two rows, opposite conclusions.** The leading scheme called NZD correctly —
it has fallen every session. It also says CHF is the second-strongest currency
on the board, while the pair that is short CHF is the only one earning.
**One of those is wrong, and a week of parallel record will say which.**

**EQUAL is on the sheet for completeness, not as a live candidate.**
Flattening Inflation 3 → 1 strips out the rate-differential signal, which is
the transmission channel the whole report rests on.

**This is the headline item on the 2026-09-05 review** —
`docs/SCORING_REVIEW_AGENDA.md`.

---

## 7. What the report refuses to publish

**Fifteen numbered guards run before a byte is written. Each exists because
something shipped wrong once.**

| Guard | Blocks | Because |
|---|---|---|
| R-7 | a missing mandated section | the week-ahead table went missing and nothing noticed |
| R-16 | a score quoted outside §2.0 that contradicts it | one edition shipped two different values for USD |
| R-17 | a sentiment capture more than 2 days old | a stalled index restated as current |
| R-18 | any cross-section contradiction | — |
| R-19 | a released event still previewed as upcoming | "CPI lands in three hours" — after it landed |
| R-22 | build narrative sitting in the market read | *"I got tired of complaining so I just accepted it"* |
| R-23 | a selected pair with no line on the chart | three pairs selected, nothing drawn |
| R-24 | a locked table whose columns changed | §4.0 changed shape four editions running |
| R-27 | **any new table, anywhere** | content being asked for is not permission to restructure |
| R-29 | a bench ranked without the room gate | the alternates were ranked on half the criteria |
| R-31 | a cycle column carrying prose instead of a tilt | §2.0b was computed and read by nobody for two days |
| R-32 | a §4.0 time that disagrees with `pht(capture)` | both central banks published eight hours early |
| R-33 | generated markup pasted into the body | the F&G block rendered twice, once as tag soup |
| R-34 | a forward phrase beside a date that has passed | a section kept its verbs while its dates went stale |
| R-35 | **any section that did not move since the last edition** | the playbook carried Sunday's measurements for three days |

**R-35 has an escape hatch, and it is the point.** A section with genuinely
nothing new writes *"unchanged since \<date\>: \<why\>"* and the guard accepts
it — **turning a silent carry into a published claim someone can check.**

### ⚠ The limit, stated plainly

**Guards check an edition's SHAPE, never its JUDGEMENT.** These shipped past
every gate and were caught by Jeff reading:

- **F-33** — a falsifier at 114.992 that **no bar ever printed**
- **F-32** — every published level sat at or below price; "resistance" was
  Friday's own high
- **F-27/F-29/F-36** — a **provisional** figure under a **final's** name,
  three times

**Recompute every derived figure and name the bar that produced it (LD-48).**

---

## 8. Standing constraints

**LD-4 — NO MONEY PATH.** No lot sizes, entries, stops, targets, orders. Key
levels are OBSERVATIONS of structure. *"4,435 is the swing high, rejected
twice"* is in scope; *"stop above 4,435"* is not. **Same number, and the
second one is an instruction.**

**LD-3 — calendars are SCHEDULE authorities, never VALUE authorities.** A
released print comes from the issuing agency. **This does NOT limit how much a
FORECAST may move a forward-looking bias** — that was a misuse of the rule
(LD-85).

**LD-5 — Jeff's own chart drawings are never touched.** Check `draw_list`
before clearing anything.

**LD-42 — weekly independence.** Sunday selects, Monday revalidates,
Saturday reviews. **A week's bias is not inherited from the last one.**

**LD-81 — a finding is not recorded until it is in the SPEC.** Every finding
lands in three places in the same commit: the edition's §8, `REPORT_SPEC.md`,
and a guard. **The commit message is the fourth, not the first.**

---

## Where to go next

| Question | File |
|---|---|
| Why is any single rule the way it is? | `REPORT_SPEC.md` |
| How is a pair chosen? | `SELECTION_CRITERIA.md` |
| How is a currency scored? | `SCORING_BASELINE.md` |
| What is open for review? | `SCORING_REVIEW_AGENDA.md` |
| Which table shapes are locked? | `LAYOUT_LOCK.md` |
| How do I work with Jeff? | `CLAUDE.md` |
