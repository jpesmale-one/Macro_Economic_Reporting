# SCORING BASELINE v1 — locked 2026-08-30

**This is the starting line.** Every future change to how a currency is scored
is measured against this document. If a number in a report cannot be traced
back to a rule written here, that is a finding, not a mystery.

Jeff, 2026-08-30: *"make sure this is recorded so in the future we're not
guessing where it came from. Plus this is only our base line. In the future if
we saw some improvement point this is our starting line."*

---

## 0. What a currency score IS

A single number, roughly **−11.00 to +11.00**, expressing how strong a
currency's macro data is **relative to its own thresholds** — not relative to
other currencies, and **not a price forecast**.

**It answers one question: is this currency's data on the right side of the
lines we set?** It is deliberately slow. It is a baseline for a bias, and
§4.6 (direction × surprise) exists precisely because the tally alone does not
predict price.

---

## 1. THE CAUSAL MODEL (Jeff's, 2026-08-29)

```
Production · Spending · Trade  →  Employment · Inflation  →  Interest Rate  →  currency
        LEADING                        CONFIRMING              THE DRIVER
```

**"Production, Spending and Trade tends to predict the result of Employment and
Inflation. And Employment and Inflation tends to predict what would be the
Interest rate decision. Because the Interest Rate dictates if the Currency is
Strong or Weak."**

**The weights encode this, the arithmetic does not.** v1 sums six categories
side by side; it does not compute the rate *from* the others. **§2.0b (LD-72)
publishes the chain as a VIEW** so the cycle position is visible without the
model asserting a causal theory it has not yet tested. **Encoding the chain in
the arithmetic is option C and is deliberately NOT in v1** — see §6.

---

## 2. CATEGORY WEIGHTS (LD-13, locked 2026-08-19, unchanged in v1)

| Category | Weight | Stage | Why |
|---|---|---|---|
| Production | 1.0 | LEADING | early cycle, noisy |
| Spending | 1.0 | LEADING | early cycle, noisy |
| Trade | 1.0 | LEADING | early cycle, noisy |
| **Employment** | **2.0** | CONFIRMING | a central-bank mandate |
| **Inflation** | **3.0** | CONFIRMING | the other mandate, and the louder one |
| **Interest Rate** | **3.0** | THE DRIVER | what actually prices a currency |

**Scale: ±11.00.** The five scored categories in `score_model.W` sum to **8.0**;
**Rate is added separately in `compute()` at weight 3.0**, so the maximum is 11.0.
A reader checking `W` alone will see 8 and should not conclude the scale is wrong.

**Within a category the weight splits evenly across its rows.** USD Production
has 4 rows → each is worth 0.25. A currency with 1 row in a category puts the
whole weight on that row.

---

## 3. INDICATOR SCORING — v1 GRADED (LD-71, 2026-08-30)

### Why it changed

**Before v1, every indicator resolved to GOOD / NEUTRAL / BAD — three states.**

Measured on 2026-08-29, before any change: **26 of 48 category slots (54%) sat
AT THEIR CEILING.** A maxed slot cannot register good news, only bad. **CAD was
maxed in five of six categories and had ranked #1 for weeks while losing on
price** — its score had stopped being a signal and become a constant.

**Trade and Inflation carry ONE row per currency**, so those categories were
three-way switches — and **Inflation is the heaviest at weight 3.** It could
not distinguish *"2.9% and rising fast"* from *"2.1% and barely above target"*.

| | Before | **v1** |
|---|---|---|
| Ceiling slots | 26 of 48 | **13** |
| CAD maxed categories | 5 of 6 | **2** |

### The two halves of a score

**MAGNITUDE comes from the threshold rule. SIGN comes from the verdict column.**

That split exists because of a bug caught before v1 shipped: `>Prev` and
`<Prev` describe the **comparison**, not the direction of goodness. *Lower* is
good for unemployment and **bad** for a trade balance. NZ's trade balance
collapsed +0.02B → −1.95B, verdict **BAD**, and the rule scored it **+1.000**;
NZD jumped 4th → 1st on it.

**The verdict column carries polarity and Jeff has curated it row by row
(LD-57, LD-58, LD-59). It is the authority.** The rule says *how far*; the
verdict says *which way*.

### The four graded rules — cover 50 of 71 rows

| Pattern | Rows | Magnitude | Full marks at | Divisor |
|---|---|---|---|---|
| `>50.5` etc. (PMI) | 8 | distance from the 50-ish pivot | **5 points clear** | 5.0 |
| `>0.5%` etc. (level) | 19 | distance beyond the line | **3pp clear** | 3.0 |
| `>Prev` | 17 | relative change vs previous | **a 10% move** | 0.10 |
| `<Prev` | 6 | same, sign from verdict | **a 10% move** | 0.10 |

**All results clamp to [−1, +1].**

**⚠ THE DIVISORS ARE JUDGEMENT CALLS, NOT DERIVED VALUES.** 5 PMI points, 3
percentage points, a 10% relative move. They set how hard full marks are, and
they were chosen **conservatively on purpose** so an ordinary beat lands
mid-range and the category keeps headroom. **That headroom is the entire fix.**
**They have NOT been validated against outcomes.** They are the first thing to
revisit — see §6.

### The 21 rows that stay three-state, deliberately

Rows whose threshold has no graded pattern keep GOOD/NEUTRAL/BAD. Several are
**rules Jeff specified by hand**:

- **LD-57** — full-time employment change (AUD, CAD)
- **LD-58** — GBP claimant count change
- `0-0.5%` bands, `>2% & rising`, `>2% & falling`, `unchanged`, `>Cons`

**Silently regrading a hand-specified rule is exactly the drift LD-59 warns
against.** Any change here needs Jeff's word first.

---

## 4. WORKED EXAMPLE — USD, as at 2026-08-30

**Step 1 — each indicator gets a magnitude.**

| Indicator | Actual | Prev | Threshold | Verdict | Score |
|---|---|---|---|---|---|
| ISM Manufacturing PMI | 53.2 | 53.9 | `>50.5` | GOOD | **+0.540** |
| Industrial Production YoY | 1.1% | 1.29% | `>0.5%` | GOOD | **+0.200** |
| Manufacturing Production YoY | 1.2% | 1.1% | `>0.5%` | GOOD | **+0.233** |
| Durable Goods Ex Transp MoM | 0.4% | 0.6% | `>0.5%` | BAD | **−0.033** |

*Under the old model, Industrial Production (+0.200) and Building Permits
(+1.000) would BOTH have scored +1.00.*

**Step 2 — average within the category, apply the weight.**

Production has 4 rows, weight 1.0, so each row is worth 0.25:

```
+0.540 × 0.25 = +0.135
+0.200 × 0.25 = +0.050
+0.233 × 0.25 = +0.058
−0.033 × 0.25 = −0.008
                +0.235
```

**Step 3 — sum the six categories.**

| Category | Weight | USD |
|---|---|---|
| Production | 1.0 | +0.24 |
| Spending | 1.0 | +0.48 |
| Trade | 1.0 | +0.57 |
| Employment | 2.0 | −0.76 |
| Inflation | 3.0 | +0.00 |
| Rate | 3.0 | +0.00 |
| | | **+0.52** |

---

## 5. THE BASELINE BOARD — 2026-08-30

**The first board computed under v1. Every future scoring change is compared
to this.**

| CCY | v1 score | Old (3-state) | Leading | Confirming | Gap | Cycle |
|---|---|---|---|---|---|---|
| CAD | **+6.56** | +8.38 | +0.68 | +0.83 | −0.15 | aligned |
| GBP | **+5.31** | +5.75 | −0.15 | +1.00 | **−1.15** | IN THE PAST |
| EUR | **+5.05** | +6.25 | +0.43 | +0.60 | −0.17 | aligned |
| NZD | **+4.65** | +3.75 | +0.05 | +0.45 | −0.40 | IN THE PAST |
| AUD | **+1.97** | +2.75 | +0.68 | −0.02 | +0.70 | BUILDING |
| JPY | **+0.53** | +2.00 | −0.09 | +0.16 | −0.25 | aligned |
| USD | **+0.52** | +1.75 | +0.43 | −0.15 | +0.58 | BUILDING |
| CHF | **−0.64** | −0.38 | +0.69 | −0.47 | **+1.16** | BUILDING |

### The bands — CONFIRMED, not inherited (LD-76)

**STRONG ≥ +5.50 · NEUTRAL +0.01 to +5.49 · WEAK ≤ 0.00**

**5.50 is exactly half the ±11.00 scale.** Weights sum to 8 (1+1+1+2+3) and
Rate adds 3. It is a **geometric split**: top half STRONG, anything positive
NEUTRAL, zero or below WEAK. **It is not derived from a distribution of scores
and not validated against outcomes.**

**Jeff, 2026-08-30, asked where it came from, was told exactly this, and kept
it: _"The 5.5 is our benchmark for a strong currency then."_**

**That decision is the point.** Grading made full marks much harder to earn, so
**STRONG went from 3 currencies to 1 on an unchanged line** — GBP 5.75 → 5.31
and EUR 6.25 → 5.05 both crossed out. **The call is that a higher bar for
STRONG is the correct outcome, not a mis-calibration to be tuned away.**

**Two things to keep in view:**

- **±11.00 is still the maximum and the arithmetic guarantees it** — `graded()`
  clamps each indicator to [−1,+1], so a category with weight *w* and *n* rows
  returns exactly *w* when every row scores +1. **What changed is how hard
  that is**, not the ceiling.
- **The realistic range has compressed.** CAD leads at **+6.56** and is short
  **4.44** — of which **2.62 is the Rate category alone**, because
  `rate_model.py` scores inflation-vs-mandate only and was **not touched by
  LD-71**. **The heaviest-weighted category still runs on the old logic.**
  See improvement item #6.

**Nothing downstream selects on a band.** §4 selects on the **spread between
two currencies**. The band is a published label, which is why leaving it
unchanged carries no selection risk.

---

## 6. WHAT v1 DOES NOT DO — the improvement list

**Recorded so a future change starts from a known position rather than a
rediscovery.**

| # | Gap | Status |
|---|---|---|
| 1 | **The divisors (5 / 3 / 0.10) are unvalidated judgement calls** | first thing to revisit |
| 2 | ~~Bands not re-cut~~ | **DECIDED 2026-08-30 (LD-76)** — kept at 5.50; a higher bar for STRONG is the intended outcome |
| 3 | **The chain is a VIEW, not arithmetic** (option C) | needs evidence that leading actually predicts confirming **in our data** |
| 4 | **21 rows still three-state** | several are Jeff's hand-specified rules — needs his word |
| 5 | **Off-whitelist indicators are invisible** | US PCE moved the dollar twice in one week and §2 saw neither. A whitelist amendment is Jeff's call (F-3) |
| 6 | **Rate score is inflation-vs-mandate only AND was not regraded by LD-71** | `rate_model.py`. **The heaviest category (weight 3) still runs old logic** — it is 2.62 of CAD's 4.44 gap to the ceiling. Steps 2–4 (priced odds, vote splits, forward paths) were rejected; see that file |

**Before changing any of these, measure the current state first.** LD-71
happened because *54% of slots at ceiling* was measured, not guessed — and the
two bugs it nearly shipped were caught by tracing an implausible result rather
than trusting the output.

---

## 7. PROVENANCE

| What | Where |
|---|---|
| Weights and `compute()` | `pipelines/score_model.py` (LD-13) |
| Graded rules | `score_model.graded()` / `graded_signed()` (LD-71) |
| Cycle view | `section2.cycle_table()` (LD-72) |
| Rate score | `pipelines/rate_model.py` (LD-23) |
| Row values | `score_model.ROWS`, reconciled by `audit_te.py` (LD-50) |
| Selection gates | `pipelines/selection_gates.py` (LD-73) |

**Version history**

| Version | Date | Change |
|---|---|---|
| **v1 GRADED** | **2026-08-30** | **Graded magnitudes replace three-state for 50 of 71 rows (LD-71). Cycle view added (LD-72). Bands confirmed at 5.50 (LD-76). BASELINE.** |
| v0 three-state | 2026-08-19 | GOOD/NEUTRAL/BAD per indicator, weighted categories (LD-13) |
