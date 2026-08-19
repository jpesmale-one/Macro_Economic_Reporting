---
edition: 2026-08-19
generated: 2026-08-19 12:56 PHT
data_asof: 2026-08-19 12:56 PHT
horizon: INTRADAY (Wednesday - no swing block, no carry per LD-8)
seal: UNSEALED - DRAFT
seal_tier: LIGHT (per LD-12)
artifact_url: https://claude.ai/code/artifact/6ad31052-2b2c-4935-9573-908f00af2e7a
---

# Daily Market Sentiment — Wednesday 19 August 2026

**All times Philippine Standard Time (UTC+8).** Source timestamps converted
from ET (UTC-4) by +12h and from UTC by +8h.

> **STATUS: UNSEALED DRAFT.** Not citable by later work until sealed.
> This is the FIRST edition — the protocol has never been exercised before,
> and §7 records what broke.

---

## §0 — LEAD FINDING: the phantom-Actual guard fired, 13 times

**This is F-1 reproducing live, on the first run.** The guard specified in
LD-9 caught TradingEconomics displaying "Actual" values for **13 row-groups
whose scheduled release is still in the future**.

| Ccy | Event | TE shows "Actual" | Actually releases (PHT) |
|---|---|---|---|
| AU | Employment Change JUL | **76.3K** | Thu 20 Aug 13:30 |
| AU | Unemployment Rate JUL | 4.4% | Thu 20 Aug 13:30 |
| AU | Full/Part Time Emp Chg JUL | 29.3K / 47K | Thu 20 Aug 13:30 |
| CN | Loan Prime Rate 1Y/5Y | 3% / 3.5% | Thu 20 Aug 13:15 |
| US | Initial Jobless Claims | 209K | Fri 21 Aug 00:30 |
| US | Philadelphia Fed Mfg AUG | 41.4 | Fri 21 Aug 00:30 |
| US | Continuing Jobless Claims | 1777K | Fri 21 Aug 00:30 |
| JP | S&P Global Mfg PMI Flash AUG | 54.5 | Fri 21 Aug 12:30 |
| GB | Retail Sales MoM/YoY JUL | 1% / 4.2% | Fri 21 Aug 18:00 |
| EA | S&P Global Composite PMI AUG | 52.0 | Fri 21 Aug 20:00 |
| GB | S&P Global Composite PMI AUG | 52.2 | Fri 21 Aug 20:30 |
| CA | Retail Sales Ex Autos MoM JUN | 1.2% | Sat 22 Aug 00:30 |
| US | S&P Global Composite PMI AUG | 54.5 | Sat 22 Aug 01:45 |

**Why this matters more than any other line in this report.** The AU
Employment Change phantom reads **76.3K against a 15.0K consensus** — a
5x beat. Taken at face value it would have driven AUD to the top of the
strength table on the single strongest employment print on the board. It
has not happened yet. **Nothing in this edition uses any of these figures.**

Note the defect's exact shape: checking that you read the *Actual* column
does **not** catch it. Only comparing the row's scheduled release against
now does.

**F-1 remains OPEN.** The guard is a procedure I ran manually, not tooling.

---

## §1 — Headline Alerts, News & Fundamentals

### RELEASED — Tue 18 Aug

| Ccy | Event | Actual | Previous | Consensus | Read |
|---|---|---|---|---|---|
| GB | Claimant Count Change JUL | **−11K** | −6.4K | 11.2K | **GOOD** — fewer claimants; large consensus beat |
| GB | Unemployment Rate JUN | 4.9% | 4.9% | 4.8% | NEUTRAL — unchanged |
| GB | Avg Earnings incl. Bonus JUN | 4.1% | 4.4% | 4.1% | Cooling wage pressure |
| GB | Employment Change JUN | 83K | 147K | — | Slowing but positive |
| GB | HMRC Payrolls JUL | −13K | −13K | — | Weak, unchanged |
| GB | Labour Productivity QoQ Q2 | −0.8% | 1.1% | −0.5% | **BAD** — missed |
| EA | ZEW Economic Sentiment AUG | **31.4** | 23.4 | 25.4 | **GOOD** — beat, big jump |
| DE | ZEW Economic Sentiment AUG | 34.2 | 26.3 | 30.0 | **GOOD** — beat |
| DE | ZEW Current Conditions AUG | −61.1 | −77.6 | −69.5 | **GOOD** — improving |
| US | Building Permits Prel JUL | 1.443M | 1.374M | 1.37M | **GOOD** — beat |
| US | Building Permits MoM JUL | +5.0% | −2.6% | — | **GOOD** — >0.5% threshold |
| US | Housing Starts JUL | 1.239M | 1.415M | 1.35M | **BAD** — missed |
| US | Housing Starts MoM JUL | **−12.4%** | +19.7% | — | **BAD** — sharp reversal |
| US | Industrial Production MoM JUL | 0.2% | 0.3% | 0.3% | Slight miss |
| US | Industrial Production YoY JUL | 1.1% | 1.29% | — | **GOOD** — >0.5% but decelerating |
| US | Manufacturing Production YoY JUL | 1.2% | 1.1% | — | **GOOD** — >0.5%, improving |
| US | Capacity Utilization JUL | 76.3% | 76.2% | 76.3% | In line |
| US | Pending Home Sales MoM JUL | −2.3% | −4.8% | 0.3% | **BAD** — missed |
| US | Import Prices MoM JUL | −0.4% | −0.3% | 0.1% | Disinflationary |
| US | Export Prices MoM JUL | −1.3% | −0.7% | 0.2% | Disinflationary |
| CA | Housing Starts JUL | 229.1K | 240.8K | 248K | **BAD** — missed |

### RELEASED — Wed 19 Aug (today)

| Ccy | Event | Actual | Previous | Consensus | Read |
|---|---|---|---|---|---|
| AU | Wage Price Index QoQ Q2 | 0.8% | 0.8% | 0.8% | NEUTRAL — exactly in line |
| AU | Wage Price Index YoY Q2 | 3.2% | 3.2% | 3.2% | NEUTRAL — no acceleration |
| EA | Current Account s.a JUN | €25.1B | €22.1B | €24.7B | **GOOD** — improving |
| EA | Current Account JUN | €−6.2B | — | €32.0B | Large miss (non-s.a.) |
| ID | Interest Rate Decision AUG | 5.75% | 5.75% | 5.75% | Hold, as expected |
| US | MBA 30-Yr Mortgage Rate | 6.77% | — | — | Context |

### NOT YET RELEASED — the week ahead (forecast only)

| When (PHT) | Ccy | Event | Consensus | Previous |
|---|---|---|---|---|
| **Wed 19 Aug 18:00** | **GB** | **Inflation Rate YoY JUL** | **3.0%** | 2.9% |
| Wed 19 Aug 18:00 | GB | Core Inflation YoY JUL | 2.5% | 2.5% |
| Wed 19 Aug 21:00 | EA | Inflation Rate YoY Final JUL | 2.9% | 2.9% |
| Thu 20 Aug 13:00 | AU | Consumer Inflation Expectations | 4.4% | — |
| **Thu 20 Aug 13:30** | **AU** | **Employment Change JUL** | **15.0K** | 15K |
| Fri 21 Aug 11:01 | GB | GfK Consumer Confidence AUG | −18 | −18 |
| Fri 21 Aug 11:30 | JP | Core Inflation Rate YoY JUL | 1.7% | 1.8% |
| Fri 21 Aug 20:00–21:00 | EA/GB/US | Flash PMIs AUG | various | — |

**Today's dominant event: UK CPI at 18:00 PHT.** Consensus 3.0% vs 2.9%
prior — an *acceleration*, and against a BoE already at 3.75% with a
divided committee.

### Source gap (recorded, not substituted)

**CNN Fear & Greed Index unavailable** — `edition.cnn.com` returned
**HTTP 451 (geo-blocked)**. No sentiment index in this edition. I have not
substituted a number from elsewhere and labelled it CNN's.

---

## §2 — Interest Rates & Rate-Change Probability

| Ccy | Rate | As of | Inflation vs 2% | Lean |
|---|---|---|---|---|
| **AUD** | **4.35%** | Aug/26 | above | **HOLD** — wages flat at 3.2% YoY, no acceleration |
| **USD** | **3.75%** | Jul/26 | — | **HOLD/CUT** — housing rolling over, import/export prices deflating |
| **GBP** | **3.75%** | Jul/26 | 2.9% → 3.0% exp | **HOLD, hawkish risk** — CPI *accelerating* tonight |
| **EUR** | **2.40%** | Jul/26 | 2.9% | **HOLD** — ZEW jumped, sentiment recovering |
| **CAD** | **2.25%** | Jul/26 | — | **HOLD** — housing weak |
| **JPY** | **1.00%** | Jul/26 | 1.8% core | **HOLD, hike watch** — still below 2% |
| **CHF** | **0.00%** | Jun/26 | — | **HOLD** — at the floor |
| **NZD** | *see note* | — | — | — |

**⚠ SOURCE CONFLICT (LD-3 finding — recorded, not averaged).**
Two sources disagree materially on policy rates:

| | Fed | ECB | BoE | BoJ | RBA | Date |
|---|---|---|---|---|---|---|
| TradingEconomics | 3.75% | 2.40% | 3.75% | 1.00% | 4.35% | Jul–Aug/26 |
| UniRateAPI | 4.50% | 2.50% | 4.50% | 0.50% | 4.10% | **Apr/26** |

**Resolution: TradingEconomics used.** Its reference dates are Jul–Aug 2026;
UniRate's page is stamped 2026-04-20 and is four months stale. TE's figures
also match those carried in the prior reference artifact.

**NZD rate not confirmed.** UniRate shows 3.50% (April, stale); a search
result referenced 3.25% held on 9 July with a cut expected 20 Aug, but I
could not confirm this against **rbnz.govt.nz** in this run. **NZD is
excluded from §4 rather than ranked on an unverified rate.**

**No market-implied odds are quoted in this edition.** Per spec, odds
require a named source instrument (futures curve) at a stated time. I did
not obtain one, so the "Lean" column is derived from the inflation and
employment prints, not from pricing.

---

## §3 — Currency Strength Rankings

Derived from released data only (§1). Phantom rows excluded.

| # | Ccy | Lean | Driving evidence |
|---|---|---|---|
| **1** | **GBP** | **Strong** | Claimant Count −11K vs +11.2K consensus (large beat); CPI expected to *accelerate* to 3.0% tonight against a 3.75% Bank Rate. Employment is cooling but the *inflation* side dominates the rate path. |
| **2** | **EUR** | **Moderately strong** | ZEW Economic Sentiment 31.4 vs 25.4 consensus and 23.4 prior — a 8.0-point jump; German Current Conditions −61.1 from −77.6. Current account s.a. €25.1B improving. |
| 3 | JPY | Mild | Core inflation 1.8% still below the 2% target; hike watch alive but unconfirmed. No fresh JP data released this week. |
| 4 | CHF | Neutral | No CHF data this week. Rate at 0.00%. See haven note below. |
| 5 | CAD | Neutral/weak | Housing Starts 229.1K missed 248K consensus. No other CAD release this week. |
| **6** | **AUD** | **Weak-neutral** | Wage Price Index **exactly in line** at 0.8% QoQ / 3.2% YoY — no acceleration, which removes the hawkish case for the RBA at 4.35%. **The apparently strong employment number is a phantom (see §0).** |
| **7** | **USD** | **Weak** | Housing Starts −12.4% MoM (from +19.7%); Pending Home Sales −2.3% missing +0.3%; import prices −0.4% and export prices −1.3%, both deflationary. Building Permits +5% is the lone bright spot. |
| — | NZD | **NOT RANKED** | Policy rate unverified. Ranking it would breach P1. |

**Model-vs-price disagreement (the most interesting line here):**
The fundamental model puts **USD weak**, yet Gold is **down 1.11%** on the
session and BTC is **soft** — both of which usually accompany USD *strength*.
Two readings: either the USD-weak fundamentals have not transmitted yet, or
gold/BTC are falling for their own reasons (position unwind, risk-off in
crypto specifically). **This disagreement is unresolved and is the single
biggest caveat on today's directional reads.**

---

## §4 — Conviction Playbook — INTRADAY horizon

*Wednesday: intraday only. No swing block, no carry (LD-8).*
*Levels are STRUCTURE, never entries or targets (LD-4, LD-5, LD-7).*

### 1. GBP/CHF — strongest fundamental spread on the board

- **Alignment:** GBP ranked #1 (Claimant Count beat, CPI accelerating into
  a 3.75% Bank Rate) against CHF at 0.00% with no data and no catalyst.
  Widest fundamental gap available.
- **Conviction:** Highest of today's set — **but event-gated.**
- **Technical:** Not read this run (see §7). **No levels published.**
- **Falsifier:** UK CPI at 18:00 PHT printing **below 2.9%**. That removes
  the acceleration case and inverts the entire GBP thesis within the
  session.
- **⚠ Event risk:** UK CPI lands *inside* the intraday window. The thesis
  is unresolved until 18:00 PHT.

### 2. EUR/AUD — divergent data surprise

- **Alignment:** EUR #2 (ZEW beating hard, sentiment recovering) against
  AUD #6 (wages exactly in line, removing the hawkish RBA case).
- **Conviction:** Moderate.
- **Technical:** Not read this run. **No levels published.**
- **Falsifier:** AU Employment tomorrow 13:30 PHT printing materially above
  15.0K consensus. **Note the trap:** TE already displays 76.3K for this —
  a phantom (§0). If the *real* print lands near that, AUD strength returns
  and this alignment voids.

### 3. AUD/NZD — EXCLUDED

Not proposed. NZD's policy rate is unverified (§2) and RBNZ may be cutting
on **20 Aug**. Proposing a cross with an unverified leg into a possible rate
decision would breach P1.

### Observed structure (published as levels, no execution role)

**OANDA:AUDUSD** — D1, 20-bar lookback (22 Jul – 19 Aug)
- **0.71296** — 20-day high, set Mon 17 Aug. Range top.
- **0.69222** — 20-day low. Range floor.
- Current **0.70729**; range 0.02074 (~207 pips), position ~72% of range.

**OANDA:AUDNZD** — D1, 20-bar lookback
- **1.21216** — 20-day high. **1.19136** — 20-day low.
- Current **1.20460**, mid-range. Range 208 pips.

**OANDA:EURCHF** — D1, 20-bar lookback
- **0.94120** — 20-day high, set Fri 14 Aug; **four consecutive daily highs
  at 0.9410–0.9412** (14, 15, 18, 19 Aug) — a tested ceiling.
- **0.92719** — 20-day low.
- Current **0.93973**, just under the ceiling. **+1.11% over 20 days.**

---

## §5 — Gold (XAUUSD), intraday

**OANDA:XAUUSD — 4345.47** (M15 close 12:45 PHT), **−1.11% on the session**.

### Structure — D1, 30-bar lookback (10 Jul – 19 Aug)

| Level | Type | Evidence |
|---|---|---|
| **4449.83** | 30-day high | Set Mon 10 Aug |
| **4436.23** | Lower high | Tue 18 Aug — rejected 13.6 below the high |
| **4428.89** | Lower high | Mon 17 Aug |
| **4324.68** | Session low | Today, Wed 19 Aug |
| **3959.80** | 30-day low | Range floor |

**Three consecutive rejections in the 4429–4450 band** (10, 17, 18 Aug),
each lower than the last. Today's low 4324.68 is the weakest point since
that band formed.

### Read
Gold is **20 days up 6.65%** but has stalled: a descending sequence of
highs into a band it cannot clear, now with a −1.11% session. The
structure is **distribution under 4450**, not continuation.

**Falsifier:** a daily close above **4449.83** voids the lower-high
sequence entirely and re-opens the uptrend.

**Unresolved:** gold falling *with* a fundamentally weak USD (§3) is
contrary. Either real yields are doing the work, or this is position
unwind. Not resolved by this data.

---

## §6 — BTC (BTCUSD), intraday

**OANDA:BTCUSD — 64,254.5**, **−2.49% over 20 days**.

### Structure — D1, 20-bar lookback

| Level | Type | Evidence |
|---|---|---|
| **66,284** | 20-day high | Range top |
| **65,019** | Recent high | Mon 17 Aug |
| **62,203** | 20-day low | Range floor |
| **62,469–62,777** | Tested support | Twice, 12–13 Aug |

Current 64,254.5 sits **mid-range** — 50.3% of the 4,081-point band.
Recovered off the 62,469 test to 64,568 (14 Aug) but has not challenged
66,284.

### Read
**Range-bound, no directional edge.** Both boundaries are tested and
holding; price is at the midpoint. This is the least actionable instrument
on today's board.

**Risk correlation:** BTC soft *and* gold soft *and* USD fundamentally weak
is an unusual combination. BTC is **not** cleanly tracking risk-on/risk-off
today, so treating it as a risk proxy would be wrong.

**Falsifier:** a close outside 62,203 / 66,284 ends the range read.

---

## §7 — Method notes & what broke (first-run honesty)

**What the protocol caught:**
1. **13 phantom-Actual rows** (§0) — the guard's first live run, and it
   fired immediately. The AU employment phantom would have inverted the
   entire strength table.
2. **A source conflict on policy rates** (§2) — resolved by recency with
   the reasoning stated, not averaged away.
3. **An unverifiable NZD rate** — so NZD is excluded rather than guessed.

**What did not work:**
1. **`batch_run` failed** on both `quote` and `ohlcv` actions ("Unknown
   action or API not available"). Pairs had to be pulled one at a time by
   switching the chart symbol. **Consequence: only 5 of 21 watchlist pairs
   were read.** §4's top two alignments therefore carry **no technical
   levels at all** — they are fundamental-only, and are labelled as such.
   This is a genuine gap, not a stylistic choice.
2. **CNN Fear & Greed geo-blocked** (HTTP 451). No sentiment reading.
3. **Central bank sites not visited.** §2 leans on TradingEconomics.
   Spec §2.2 makes the CB sites authoritative for rates — that step was not
   executed this run.
4. **Chart symbol left on OANDA:BTCUSD**, timeframe on 1D. The chart was
   navigated for reads; **no levels were drawn**, so no cleanup was owed
   (LD-6 chart hygiene). Original symbol was OANDA:XAUUSD @ 15m.
5. **A date-parsing bug in my own guard script** (day/month transposed)
   threw on first run. Caught and fixed before any figure was used.

**Consequence for conviction:** every §4 alignment here is
**fundamental-only**. A real conviction call needs both halves. Treat this
edition as a **fundamental read with partial technical confirmation**, not
a complete playbook.

---

## Publish gate

- **P1 SOURCED** — ⚠ **PARTIAL.** Released figures carry source, event,
  period, and release status. Gaps: no CB-site verification, NZD rate
  unverified (excluded), no sourced rate odds.
- **P2 RECOMPUTED** — ✅ Levels name the bars that formed them, with
  lookback and dates. Ranges and percentages recomputed from OHLCV.
- **P3 SEALED** — ❌ **UNSEALED.**

**Recommendation: do not seal as-is.** With 16 of 21 pairs unread and the
CB verification step skipped, this is below the standard the spec sets.
It is a valid *first run* that proved the guard works — not a finished
edition.
