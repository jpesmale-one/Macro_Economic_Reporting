# PROPOSAL — LD-140: an interest rate decision wins its day

**Status: AWAITING JEFF'S APPROVAL. No scoring code has been changed.**

Jeff, 2026-09-19: *"In my point of view we need to prioritize Interest Rate in
the calibrator in the succeeding report over other indicators. We can do
Interest Rate > GDP > All Others. What do you think?"*

Asked which of two forms he wanted, he chose **rate-only, the narrowest
override**, and **calibrator only** — the base weights do not move.

---

## 1. The failure this fixes (F-126)

Three central banks moved inside the 14–18 Sep week. **All three were visible in
the capture the edition was built from, with consensus and previous on file:**

```
2026-09-17 02:00 PHT   US  fed interest rate decision   cons=4%      prev=3.75%
2026-09-17 19:00 PHT   GB  boe interest rate decision   cons=3.75%   prev=3.75%
2026-09-18 11:00 PHT   JP  boj interest rate decision   cons=1.25%   prev=1%
```

The Fed **hiked to 4.00%** and raised its projections. **USD finished +0.74%, the
only currency up against the basket — ranked 4th on our board.** The calibrator
scored 20 rows that week: Machinery Orders, Building Permits, Dairy Trade. Not
one of the three decisions.

The week graded **0 of 3 biases, 0 of 15 pair-days**.

---

## 2. Why it happened, precisely

Two separate reasons, and only the second is what this proposal changes.

**(a) Rate decisions are not whitelist rows.** `week_ahead.whitelist_events()`
matches against `score_model.ROWS`, and no rate decision is in it. The
calibrator therefore never sees them at all — they are not outranked, they are
absent.

**(b) LD-23 is why.** *No input that cannot be sourced for all eight currencies
on equal terms.* A rate decision publishes no uniform numeric "actual" the way
CPI does, so Interest Rate Expectations was parked as its own category.

> **THE PARKING DECISION WAS RIGHT AND ITS COST IS NOW MEASURED.** LD-23 exists
> because unequal inputs let one currency be scored on evidence another cannot
> have. That reasoning still holds. What has changed is that we can now price
> the omission: the single largest driver of a graded week was invisible.

---

## 3. LD-23 is satisfied, on its own terms

A rate decision **does** carry a numeric surprise, and TE publishes it for every
one of the eight:

```
surprise (bp) = actual − consensus
```

Both fields are present in our own capture for all three September decisions
above. This is not a new data source and not a special case for one currency —
it is the same `actual` vs `consensus` comparison every other calibrator row
already uses, applied to a row type we were excluding.

**That satisfies LD-23 as written.** The rule bars inputs that *cannot* be
sourced equally; this one can.

---

## 4. What changes

### 4a. The row enters the calibrator whitelist

A new whitelist entry per currency, matched with **`decision_history.is_decision()`**
— the existing matcher, which already handles TE's short-form/long-form naming
trap (F-73's shape, and it cost an hour on 2026-09-10).

**Reusing that matcher is deliberate.** F-120 happened because a one-off script
re-implemented matching and disagreed with the scorer about what a row *is*.

### 4b. Scored by surprise, with LD-90 intact

```
actual > consensus   → +1   hawkish surprise
actual = consensus   →  0   fully priced (LD-90)
actual < consensus   → −1   dovish surprise
```

**LD-90 is not weakened — it is honoured.** A decision that lands exactly on
consensus scores **0**, not +1, because the market already holds it. The BoJ
hiked to 1.25% on consensus and JPY still finished last that week; this rule
would have scored that day 0, which is correct.

### 4c. Day precedence — the only change to LD-98

```
1.  an INTEREST RATE DECISION        → wins its day outright
2.  everything else                  → latest reference month (LD-119, unchanged)
```

**GDP keeps competing on reference month exactly as LD-119 says.** Jeff's words
then: *"I'm taking back the B decision. Let's keep the prioritization rule
intact. So if GDP release date have other Indicator release which have more
latest data then we still focus on that one Rather than the GDP."* That ruling
stands untouched.

---

## 5. What this contradicts, stated plainly

**LD-98 — "the day is the unit, no weights."** This is a genuine exception and
the first one. The justification is not that rate decisions are *more
important* in the abstract — that is the reasoning that produced LD-113 (GDP
weighted in the base) and was withdrawn a day later for ranking nothing. It is
that a rate decision **sets the price of the currency itself**, which is the
quantity the board is trying to rank. Every other row is evidence *about* where
that price is heading.

**LD-134 — "a caution, not a weight."** The high-impact flag deliberately
changed no score. This proposal does change a score, for one row type only.

> **IF THIS RANKS NOTHING, WITHDRAW IT.** LD-113 is the precedent: a category
> weighted for importance rather than measured evidence lasted one day. The test
> is the 21–25 Sep retrospective — if rho does not improve and the rate rows do
> not explain the weeks they appear in, this comes out.

---

## 6. Measured effect on the graded week

Recomputed on the 13 Sep capture, 14–18 Sep window:

| Day | Row | Actual | Consensus | Score |
|---|---|---|---|---:|
| Thu 17 | **USD Fed Interest Rate Decision** | 4.00% | 4.00% | **0** |
| Thu 17 | GBP BoE Interest Rate Decision | 3.75% | 3.75% | 0 |
| Fri 18 | JPY BoJ Interest Rate Decision | 1.25% | 1.25% | 0 |

> **⚠ THE HONEST RESULT: ALL THREE LANDED ON CONSENSUS, SO ALL THREE SCORE 0.**
>
> **This proposal would NOT have changed the 14–18 Sep board.** Under LD-90 a
> fully-priced decision carries no surprise, and every September decision was
> fully priced.
>
> What it *would* have changed is the day's **precedence**: USD Thursday and JPY
> Friday would have been scored by the decision rather than by Industrial
> Production and CPI. Both would read 0 instead of +1, which *lowers* USD's
> calibrator — and USD was the week's strongest currency.
>
> **So on the one week we can test it against, this change makes the board
> slightly worse.** I am proposing it anyway, because the mechanism is right and
> one week is not evidence — but you should approve it knowing that, not
> discovering it later.

---

## 7. What it does not do

- **No base weight change.** `Interest_Rate` stays at 1. Jeff chose calibrator
  only so the next retrospective can attribute any change to one cause.
- **No carry tilt.** That was tested separately across 13 weeks and the
  forward-looking regime signal failed; it stays a measured column.
- **No new category.** Interest Rate Expectations remains parked.

---

## 8. If approved, the build

1. `calibrator.py` — add `RATE_NAMES`, score by surprise, give it day precedence
2. `week_ahead.py` — admit decision rows via `decision_history.is_decision()`
3. `test_inflation.py` (R-44) — add LD-140 cases including the on-consensus zero
4. `docs/REPORT_SPEC.md` — record LD-140 with section 6 above intact
5. Rebuild and republish the 21–25 Sep edition from it

**Approval needed before any of that runs.**
