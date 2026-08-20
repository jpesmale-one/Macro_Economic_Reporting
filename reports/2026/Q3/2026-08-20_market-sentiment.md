---
edition: 2026-08-20
revision: 11 (risk-off nil proved on the full 3x3, not on the extremes)
generated: 2026-08-20 09:40 PHT
data_asof: 2026-08-20 11:20 PHT (macro 10:00; charts 11:20) -- STALE, see STALENESS NOTICE
horizon: INTRADAY (Thursday - no swing block, no carry per LD-8)
seal: UNSEALED - DRAFT
seal_tier: LIGHT (per LD-12)
artifact_url: https://claude.ai/code/artifact/a69403a7-a636-4ca2-8b41-1006e8c62806
coverage: COMPLETE - fundamental + technical. Levels read OANDA via TradingView MCP.
---

# Daily Market Sentiment — Thursday 20 August 2026

**All times Philippine Standard Time (UTC+8).**
**TradingEconomics calendar times are UTC → PHT = UTC + 8h — RE-VERIFIED THIS RUN (see Pre-flight).**

---

## ⚠ STALENESS NOTICE — read before using this edition

**This is the THURSDAY 20 Aug edition. It is now Friday 21 Aug 06:45 PHT.**
Its `data_asof` is **2026-08-20 11:20 PHT** — roughly 19 hours old.

**What has happened since and is NOT in this edition:**

| Event | When (PHT) | Affects |
|---|---|---|
| US initial jobless claims + Philly Fed | Thu 20:30 | USD score — the **NZDUSD near-miss (+0.75)** turns on this |
| ECB Monetary Policy Meeting Accounts | Thu 19:30 | EUR policy read (§3) |
| Thursday's daily bar **CLOSED** | Fri 05:00 | **Every zone and falsifier below was read off a forming bar** |
| Friday's 6 projected events | Fri 07:00 onward | The §4.0 week table is not yet graded for them |

**Consequence.** The §2 tally, the §4 bands, and every zone are Thursday
figures. They are **history, not a current read**. Do not act on the §4.5
carry list without re-running: the fundamentals may have moved on the US
prints, and every falsifier level needs re-checking against Thursday's
**closed** bar rather than the forming one it was derived from.

**This edition stands as the sealed record of Thursday.** A Friday read is a
new edition, not a revision of this one.

---

## Pre-flight — both mandatory guards PASS

**Timezone (F-2).** UK CPI released 07:00 BST = 06:00 UTC; TE showed `06:00`;
+8h = 14:00 PHT, which is when it landed. **TE calendar is UTC, PHT = UTC+8**
— verified against a real release, not assumed. *(The page carries
`TIMEZONE SET FROM COOKIE`, so the offset is session state and genuinely can
shift. Verify every run.)*

**Phantom-Actual guard (F-1, LD-9).** Run at 08:01 PHT, 440 calendar rows
parsed, 255 whitelist-currency.

- **Calendar view: NULL, not a pass.** All 440 rows returned empty value
  fields (they load by XHR), so a guard asking "is an Actual present on a
  future row" could not have fired. Logged as a null result, not a clean bill.
- **Series pages + issuing agency: PASS.** The flagged AU "phantom 76.3K" was
  **June's real print** (released 23 Jul), correctly sitting as Previous for
  today's July release. **ABS confirmed** the July release was pending at
  09:30 PHT and has since landed. r9 already had this row labelled `Jun/26`.

*F-1 mechanism note logged in STATE.md — not applied on one observation.*

---

## §1 — Headline Alerts, News & Current Events

### Central banks

**FOMC MINUTES (Jul 28–29) — released 02:00 PHT today. HAWKISH, and the headline of this edition.**
*Source: federalreserve.gov (primary), `fomcminutes20260729.htm`*

| | |
|---|---|
| **Decision** | Held **3.50–3.75%**, vote **9–3** |
| **Dissents** | **Hammack, Kashkari, Logan — all for a 25bp HIKE** |
| **Language** | Retained June's "will deliver price stability"; almost all members agreed |
| **Assessment** | Unemployment largely unchanged · growth solid · inflation still elevated vs the 2% goal |
| **Market pricing** | ~**1-in-3** for a July hike; **fully priced for +25bp by September**, another by Q1 next year. Treasury yields +25–30bp over the intermeeting period, driven by real rates |
| **Countervailing** | Desk-survey median: **no change this year or next**, first cut early 2028 |

> **UNVERIFIED:** the voting list names **Kevin Warsh** in the Chair's position with Powell voting as a member. Not confirmed against a second source, **not asserted as fact**, and §3 does not name a Chair. Verify before any edition does.

| Other | Detail |
|---|---|
| **BoE** | Vote Hike **3/9** (was 2/9), Vote Cut 0/9, Bank Rate 3.75% held 30 Jul. *TE — bankofengland.co.uk rate table is JS-rendered* |
| **RBNZ** | **Hiked to 2.50%** from 2.25% on 8 Jul; TE forecasts **2.75%** on 2 Sep |
| **ECB** | Meeting Accounts due **19:30 PHT today**; rate 2.40% |
| **Jackson Hole** | **27–29 Aug** — principal USD event risk on the near horizon |

### Risk events

**JP trade deficit doubled.** Balance of Trade **¥−634.5B** (Jul) from ¥−409.9B — worse than TE's −500B forecast, better than the −680B consensus. Released 07:50 PHT today.

### Market structure — CNN Fear & Greed **56.34 (GREED)**

Prev close 54.40 · 1w 62.94 · 1m 37.23 · 1y 59.89.
*Source: `production.dataviz.cnn.io` graphdata endpoint, browser headers + Referer.*

| Component | Score | | Component | Score |
|---|---|---|---|---|
| Junk bond demand | **92.80** extreme greed | | Market volatility (VIX) | 50.00 neutral |
| Safe haven demand | 68.00 greed | | Market momentum S&P 500 | 44.80 fear |
| Stock price breadth | 57.60 greed | | Stock price strength | **26.20** fear |
| Put/call options | 55.00 neutral | | | |

**P2 recompute:** `394.40 / 7 = 56.3429` vs published **56.34** — difference **0.0000**. The index is a simple average of the seven, re-verified on fresh data.

**A 66.60-point internal spread** (junk bonds 92.8 vs stock strength 26.2): credit euphoric, equity breadth weak. Narrower than yesterday's 70.8, same structure. **The split is the information, not the headline.**

> *Payload trap:* the endpoint returns 10 scored keys — `market_momentum_sp125` and `market_volatility_vix_50` duplicate siblings, `fear_and_greed_historical` restates the index. The mean of all 10 is 54.55 and does **not** reproduce the score. Only the correct seven do.

---

## §2 — Macro Economic Indicators

**Whitelist: all 70 named indicators, closed set (spec §2, LD-13).**
Scores generated by `pipelines/score_model.py` — tables and tally cannot
drift apart.

**Changed since r9 (2026-08-19 14:12 PHT): three scored rows.**

| Row | r9 | Today | Score effect |
|---|---|---|---|
| **AUD Employment Change** | 76.3K / 43.9K (Jun) | **−15.8K / 76.3K (Jul)** | **GOOD → BAD** |
| **AUD Unemployment Rate** | 4.4% / 4.4% (Jun) | **4.5% / 4.4% (Jul)** | **NEUTRAL → BAD** |
| JPY Balance of Trade | ¥−407B / ¥−392B (Jun) | ¥−634.5B / ¥−409.9B (Jul) | BAD → BAD (no flip) |
| EUR Inflation YoY | 2.9% / 2.8% Flash | 2.9% / 2.8% **Final** | GOOD → GOOD |

**Still pending today, status NOT RELEASED:** US initial jobless claims +
Philly Fed **20:30 PHT**, ECB Meeting Accounts **19:30 PHT**.

### 2.1 Production (weight 1)

| CCY | Indicator | Actual | Previous | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| USD | ISM Manufacturing PMI | 53.9 | 53.9 | Jul/26 | >50.5 | GOOD |
| USD | Industrial Production YoY | 1.1% | 1.29% | Jul/26 | >0.5% | GOOD |
| USD | Durable Goods Ex Transp MoM | 0.6% | 1.8% | Jun/26 | >0.5% | GOOD |
| EUR | S&P Global Mfg PMI Final | 51.9 | 51.4 | Jul/26 | >50.5 | GOOD |
| EUR | Industrial Production YoY | 0.1% | -0.1% | Jun/26 | 0-0.5% | NEUTRAL |
| GBP | S&P Global Mfg PMI Final | 51.9 | 52.5 | Jul/26 | >50.5 | GOOD |
| GBP | Industrial Production YoY | -0.2% | 1.0% | Jun/26 | <0% | BAD |
| GBP | Manufacturing Production YoY | 0.5% | 2.0% | Jun/26 | 0-0.5% | NEUTRAL |
| JPY | Industrial Production YoY Final | 4.9% | -2.1% | Jun/26 | >0.5% | GOOD |
| JPY | Machinery Orders YoY | 16.9% | -1.9% | Jun/26 | >0.5% | GOOD |
| JPY | Machine Tool Orders YoY | 50.4% | 52.8% | Jul/26 | >0.5% | GOOD |
| JPY | S&P Global Mfg PMI Final | 54.5 | 54.8 | Jul/26 | >50.5 | GOOD |
| AUD | S&P Global Mfg PMI Final | 52.0 | 51.5 | Jul/26 | >50.5 | GOOD |
| NZD | Business NZ PMI | 54.3 | 60.1 | Jul/26 | >50.5 | GOOD |
| NZD | Global Dairy Trade Price Index | 2.3% | 0.1% | Aug/26 | >0.5% | GOOD |
| CAD | S&P Global Mfg PMI | 53.5 | 53.0 | Jul/26 | >50.5 | GOOD |
| CHF | Procure.ch-UBS Mfg PMI | 53.2 | 54.3 | Jul/26 | >50.5 | GOOD |
| CHF | Industrial Production YoY | -7.1% | -0.4% | Mar/26 | <0% | BAD |

### 2.2 Spending (weight 1)

| CCY | Indicator | Actual | Previous | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| USD | Building Permits MoM Final | +5.0% | -2.6% | Jul/26 | >0.5% | GOOD |
| USD | Retail Sales YoY | 5.0% | 6.8% | Jul/26 | >0.5% | GOOD |
| USD | CB Consumer Confidence | 51.0 | 55.2 | Aug/26 | >Prev | BAD |
| USD | Personal Spending MoM | 0.3% | 0.9% | Jun/26 | 0-0.5% | NEUTRAL |
| EUR | Retail Sales YoY | 0.7% | 1.9% | Jun/26 | >0.5% | GOOD |
| EUR | Consumer Confidence Final | -15.9 | -17.6 | Jul/26 | >Prev | GOOD |
| GBP | GfK Consumer Confidence | -17 | -23 | Jul/26 | >Prev | GOOD |
| GBP | Retail Sales YoY | 4.2% | 3.5% | Jun/26 | >0.5% | GOOD |
| JPY | Household Spending YoY | -3.3% | -0.4% | Jun/26 | <0% | BAD |
| JPY | Consumer Confidence | 34.9 | 33.8 | Jul/26 | >Prev | GOOD |
| JPY | Retail Sales YoY | 0.5% | 5.0% | Jun/26 | 0-0.5% | NEUTRAL |
| AUD | Household Spending YoY | 6.0% | - | Jun/26 | >0.5% | GOOD |
| AUD | Building Permits YoY Final | 8.9% | 5.5% | Jun/26 | >0.5% | GOOD |
| AUD | Westpac Consumer Conf Change | 88.9 | 83.9 | Aug/26 | >Prev | GOOD |
| AUD | NAB Business Confidence | -6 | -6 | Jul/26 | >Prev | NEUTRAL |
| NZD | Building Permits MoM | -3.6% | -4.9% | Jun/26 | <0% | BAD |
| NZD | Electronic Retail Card Spending YoY | 0.9% | 0.9% | Q1/26 | >0.5% | GOOD |
| NZD | ANZ Business Confidence | 56.1 | 36.6 | Jul/26 | >Prev | GOOD |
| NZD | ANZ Roy Morgan Consumer Conf | 99.3 | 91.3 | Jul/26 | >Prev | GOOD |
| CAD | Retail Sales YoY | 5.9% | 3.6% | May/26 | >0.5% | GOOD |
| CAD | Building Permits MoM | +18.5% | -3.0% | Jun/26 | >0.5% | GOOD |
| CHF | Consumer Confidence | -35 | -36 | Jul/26 | >Prev | GOOD |
| CHF | Retail Sales YoY | 1.5% | 3.4% | Jun/26 | >0.5% | GOOD |

### 2.3 Trade (weight 1)

| CCY | Indicator | Actual | Previous | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| USD | Balance of Trade | -$73.26B | -$77.65B | Jun/26 | >Prev | GOOD |
| EUR | Balance of Trade | EUR8,600M | EUR-9,000M | Jun/26 | >Prev | GOOD |
| GBP | Balance of Trade | GBP-5,537M | GBP-3,464M | Jun/26 | <Prev | BAD |
| JPY | Balance of Trade | JPY-634.5B | JPY-409.9B | Jul/26 | <Prev | BAD |
| AUD | Balance of Trade | A$1,929M | A$-2,367M | Jun/26 | >Prev | GOOD |
| NZD | Balance of Trade | NZ$23M | NZ$577M | Jun/26 | <Prev | BAD |
| CAD | Balance of Trade | C$3,860M | C$3,700M | Jun/26 | >Prev | GOOD |
| CHF | Balance of Trade | CHF3,800M | CHF5,530M | Jun/26 | <Prev | BAD |

### 2.4 Employment (weight 2)

| CCY | Indicator | Actual | Previous | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| USD | Non Farm Payrolls | -23K | 20K | Jul/26 | >Cons | BAD |
| USD | Unemployment Rate | 4.1% | 4.2% | Jul/26 | <Prev | GOOD |
| EUR | Unemployment Rate | 6.3% | 6.3% | Jun/26 | unchanged | NEUTRAL |
| GBP | Claimant Count Change | -11K | -6.4K | Jul/26 | <Prev | GOOD |
| JPY | Unemployment Rate | 2.5% | 2.5% | Jun/26 | unchanged | NEUTRAL |
| AUD | ANZ-Indeed Job Ads MoM | +0.8% | -0.1% | Jul/26 | >0.5% | GOOD |
| AUD | Employment Change | -15.8K | 76.3K | Jul/26 | <Prev, FT +16.3K vs 29.3K | BAD |
| AUD | Unemployment Rate | 4.5% | 4.4% | Jul/26 | >Prev | BAD |
| NZD | Unemployment Rate | 5.6% | 5.4% | Jun/26 | >Prev | BAD |
| CAD | Unemployment Rate | 6.4% | 6.5% | Jul/26 | <Prev | GOOD |
| CAD | Employment Change | 75.1K | 18.2K | Jul/26 | >Prev, FT-weighted | GOOD |
| CHF | Non Farm Payrolls | +0.5% | +0.2% | Q1/26 | >Cons | GOOD |
| CHF | Unemployment Rate | 3.0% | 2.9% | Jul/26 | >Prev | BAD |

### 2.5 Inflation (weight 3)

| CCY | Indicator | Actual | Previous | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| USD | Inflation Rate YoY | 3.4% | 3.5% | Jul/26 | >2% & falling | NEUTRAL |
| EUR | Inflation Rate YoY Final | 2.9% | 2.8% | Jul/26 | >2% & rising | GOOD |
| GBP | Inflation Rate YoY | 2.9% | 2.6% | Jul/26 | >2% & rising | GOOD |
| JPY | Inflation Rate YoY | 1.7% | 1.5% | Jun/26 | <2% & rising | NEUTRAL |
| AUD | Inflation Rate YoY | 3.8% | 4.0% | Jun/26 | >2% & falling | NEUTRAL |
| NZD | Inflation Rate YoY | 4.1% | 3.1% | Jun/26 | >2% & rising | GOOD |
| CAD | Inflation Rate YoY | 3.0% | 2.8% | Jul/26 | >2% & rising | GOOD |
| CHF | Inflation Rate YoY | 0.4% | 0.5% | Jul/26 | <2% & falling | BAD |

### 2.6 Category tally — weighted (LD-13)

Category weights: **Inflation 3 · Employment 2 · Production/Spending/Trade 1
each.** Within a category a currency's N indicators split the weight evenly
(each worth `weight/N`). GOOD `+w/N`, BAD `−w/N`, NEUTRAL `0`.
Range **+8.00 to −8.00**.

| CCY | TOTAL | Production | Spending | Trade | Employment | Inflation |
|---|---|---|---|---|---|---|
| **CAD** | **+8.00** | +1.00 | +1.00 | +1.00 | +2.00 | +3.00 |
| **EUR** | **+5.50** | +0.50 | +1.00 | +1.00 | +0.00 | +3.00 |
| **GBP** | **+5.00** | +0.00 | +1.00 | −1.00 | +2.00 | +3.00 |
| **USD** | **+2.25** | +1.00 | +0.25 | +1.00 | +0.00 | +0.00 |
| **AUD** | **+2.08** | +1.00 | +0.75 | +1.00 | **−0.67** | +0.00 |
| **NZD** | **+1.50** | +1.00 | +0.50 | −1.00 | −2.00 | +3.00 |
| **JPY** | **+0.00** | +1.00 | +0.00 | −1.00 | +0.00 | +0.00 |
| **CHF** | **−3.00** | +0.00 | +1.00 | −1.00 | +0.00 | −3.00 |

**AUD MOVED THIS REVISION: +4.08 → +2.08, 4th → 5th**, on the 09:30 PHT
employment print. Employment category `+1.33 → −0.67`. See §4.0a for the
release detail and the graded projection. No other currency changed.

**The tally is unchanged from r9.** The single scored change (JP trade) was
already BAD and stayed BAD, so no ranking moved. **That is the honest
result: today's new information is in the POLICY layer, not the indicator
layer.**

---

## §3 — Interest Rates

Ordered by policy pressure, not alphabetically.
**Source order:** central bank primary where the value is machine-readable,
TradingEconomics as labelled fallback.

| CCY / Rate | Last decision | Bias | Next meeting (PHT) | Expectation |
|---|---|---|---|---|
| **USD 3.50–3.75%** | HELD 29 Jul, **9–3** — Hammack, Kashkari, Logan dissent for **+25bp** *(fed primary)* | **HIKE RISK** | **15–16 Sep** (SEP mtg) | The minutes are the story. Three hawkish dissents plus market **fully pricing a 25bp hike by September** against a Desk survey seeing **no move until a 2028 cut**. Jackson Hole 27–29 Aug is the next signal. |
| **NZD 2.50%** | **HIKED +25bp** 8 Jul *(TE)* | **TIGHTENING** | **2 Sep** | Only currency in an active hiking cycle. TE forecasts **2.75%**. Inflation 4.1% and rising is doing the work; employment (−2.00) is the counterweight. |
| **GBP 3.75%** | HELD 30 Jul, **Vote Hike 3/9** (was 2/9), Vote Cut 0/9 *(TE)* | **SPLIT** | **17 Sep** | Hawkish drift in the vote with CPI at 2.9% and rising. No cut votes at all. |
| **EUR 2.40%** | HELD 23 Jul *(TE)* | **CPI DECIDES** | **10 Sep** | Inflation finalised 2.9%, above target and rising. **Meeting Accounts today 19:30 PHT** may move the read. |
| **CAD 2.25%** | HELD 15 Jul *(bankofcanada.ca primary)* | **FLOORED** | **2 Sep** | Held at 2.25% since April. Perfect +8.00 fundamental score sits against the lowest policy rate in the G10 ex-JPY/CHF — the divergence is the interesting part. |
| **AUD 4.35%** | HELD 11 Aug *(TE)* | **CPI DECIDES** | **29 Sep** | Highest policy rate in the set. Inflation 3.8% and **falling** caps hike risk. **Employment prints 09:30 PHT today** — the live variable. |
| **JPY 1.00%** | HELD 31 Jul, prior hike to 1% on 16 Jun *(TE)* | **REPRICING** | **18 Sep** | Out of ZIRP and hiking, but inflation 1.7% is still below target and the trade deficit just doubled. |
| **CHF 0.00%** | HELD 18 Jun *(TE)* | **TRAPPED** | **24 Sep** | At zero with inflation **0.4% and falling** — the only deflation-leaning currency. −3.00, weakest in the set. |

**Market-implied odds:** only one sourced instrument-and-date figure exists
this run — the FOMC minutes' own record that markets priced **~1-in-3** for
a July hike and were **fully priced for +25bp by September** *(Desk
manager's report, 28–29 Jul meeting)*. **Every other currency is
deliberately shown without odds** rather than given a guessed number.

---

## §4 — Conviction Playbook — week of Mon 17 – Fri 21 Aug

### 4.0 — Week ahead: Mon 17 – Fri 21 Aug

Consensus and forecast run through the §3 thresholds **as a range**, giving
each whitelist release a **projected** score, graded against the actual in
the same row. **Projections are forecasts of a score, never scores** — they
do not enter the §2 tally. **SPLIT** = the range straddles a threshold, so
the print can go either way; those are the week's high-information events.

| When (PHT) | CCY | Indicator | Previous | Expected | Projected | Actual | Scored |
|---|---|---|---|---|---|---|---|
| Mon 17 12:30 | JPY | Industrial Production YoY Final | −2.1% | 4.2% | GOOD | **4.9%** | GOOD ✓ |
| Mon 17 20:30 | **CAD** | **Inflation Rate YoY** | 2.8% | 2.9% | GOOD | **3.0%** | GOOD ✓ |
| Tue 18 08:30 | AUD | Westpac Consumer Conf Change | 83.9 | 81.7 | BAD | **88.9** | **GOOD ✗** |
| Tue 18 14:00 | GBP | Claimant Count Change | −6.4K | 9.0 – 11.2K | BAD | **−11K** | **GOOD ✗** |
| Tue 18 21:15 | USD | Industrial Production YoY | 1.29% | 1.0% | GOOD | **1.1%** | GOOD ✓ |
| Wed 19 07:50 | JPY | Machinery Orders YoY | −1.9% | 7.8 – 9.5% | GOOD | **16.9%** | GOOD ✓ |
| Wed 19 14:00 | GBP | Inflation Rate YoY | 2.6% | 2.8 – 2.9% | GOOD | **2.9%** | GOOD ✓ |
| Wed 19 17:00 | EUR | Inflation Rate YoY Final | 2.8% | 2.9% | GOOD | **2.9%** | GOOD ✓ |
| Thu 20 07:50 | JPY | Balance of Trade | ¥−409.9B | −680 to −500B | BAD | **¥−634.5B** | BAD ✓ |
| **Thu 20 09:30** | **AUD** | **Employment Change** | **76.3K** | **15K** | **BAD** | **−15.8K** | **BAD ✓** |
| **Thu 20 09:30** | **AUD** | **Unemployment Rate** | **4.4%** | **4.4 – 4.5** | **SPLIT** | **4.5%** | **BAD ✓** |
| Thu 20 09:30 | AUD | Full Time Employment Chg | 29.3K | *none* | UNSCORED | +16.3K | BAD |
| Thu 20 09:30 | AUD | Part Time Employment Chg | 47K | *none* | UNSCORED | *pending page* | — |
| Fri 21 07:00 | AUD | S&P Global Mfg PMI Flash | 52.0 | *none* | UNSCORED | *pending* | — |
| Fri 21 07:01 | GBP | GfK Consumer Confidence | −17 | −18 | **BAD** | *pending* | — |
| Fri 21 07:30 | JPY | Inflation Rate YoY | 1.7% | 1.7% | NEUTRAL | *pending* | — |
| Fri 21 14:00 | GBP | Retail Sales YoY | 4.2% | 2.2 – 3.7 | **GOOD** | *pending* | — |
| Fri 21 20:30 | CAD | Retail Sales YoY | 5.9% | 3.1% | **GOOD** | *pending* | — |
| Fri 21 22:00 | EUR | Consumer Confidence Flash | −15.9 | −16.7 to −16.3 | **BAD** | *pending* | — |

**19 events: 13 released, 6 pending — all remaining are Friday.**

**Projection scorecard: 8 correct, 2 wrong, 1 SPLIT resolved.** Both misses
were **BAD projections that printed GOOD** — AUD Westpac confidence (88.9 vs
81.7 expected) and GBP claimant count (−11K vs +9K to +11.2K expected).
**The method's error so far is one-directional: too pessimistic.** Two
misses is not a pattern; it is logged so a pattern can be seen if it forms.

**Week by currency**

| CCY | Released | Pending | Net |
|---|---|---|---|
| **AUD** | 1 GOOD, 3 BAD | 1 unscored | **DETERIORATING — employment cost 2.00 points** |
| **GBP** | 2 GOOD | 1 GOOD, 1 BAD | Firm, mixed Friday |
| **JPY** | 3 GOOD, 1 BAD | 1 NEUTRAL | Production strong, trade weak |
| **CAD** | 1 GOOD | 1 GOOD | **Firm — best week on the board** |
| **EUR** | 1 GOOD | 1 BAD | Flat |
| **USD** | 1 GOOD | none | Quiet |
| **NZD / CHF** | **none** | **none** | **No releases at all — scores frozen** |

**The frozen pair matters most.** CHF (−3.00) and NZD (+1.50) have nothing
on the calendar Mon–Fri, so their scores cannot correct this week. For CHF
that is the whole problem: price bid it **+1.35% against the basket on 19
Aug** while the score sits bottom of the board, and **no release this week
can close that gap.**

---

---

**Weekly instrument selection.** Currencies are banded from §2, paired by
risk scenario in correct quote convention, then filtered against D and H4
structure. **Only pairs where fundamentals AND structure agree are carried
as high conviction.** Zones are observations of price structure (LD-5), not
entry, stop or target instructions.

### 4.1 Currency bands (from the §2 tally)

Cut on the **+8 / −8 scale**, not on rank. **STRONG ≥ +4.00 · NEUTRAL +0.01–3.99 · WEAK ≤ 0.00**

| Band | Currencies | Group standings |
|---|---|---|
| **STRONG** | **CAD +8.00** · EUR +5.50 · GBP +5.00 | Safe haven: USD +2.25 › JPY +0.00 › CHF −3.00 |
| NEUTRAL | USD +2.25 · AUD +2.08 · NZD +1.50 | Commodity: CAD +8.00 › AUD +2.08 › NZD +1.50 |
| **WEAK** | JPY +0.00 · **CHF −3.00** | Risk-corr: EUR +5.50 › GBP +5.00 |

### 4.2 All candidate pairings

Correct quote convention throughout; direction expresses the strong currency.
**RISK-ON** = strong vs weak · **SAFE** = haven vs haven · **COMM** = commodity vs commodity.

Grouped by type; **tradable first** within each group, then by spread.
✅ carried · ⬜ unread / no edge · ❌ rejected
**Minimum spread to qualify: 1.00** — below one full indicator flip the ranking is inside the model's own noise.

**RISK-OFF: no valid trade this week.** A risk-off trade sells a commodity
currency and buys a haven, so it is valid only where a **haven outscores a
commodity** by at least the 1.00 floor. Tested across the full 3×3 — not
just the extremes:

| haven − commodity | CAD +8.00 | AUD +2.08 | NZD +1.50 |
|---|---|---|---|
| **USD +2.25** | −5.75 | +0.17 | **+0.75** ← closest |
| **JPY +0.00** | −8.00 | −2.08 | −1.50 |
| **CHF −3.00** | −11.00 | −5.08 | −4.50 |

**Not one of the nine cells reaches +1.00.** The binding case is not CAD or
CHF — it is that **USD (+2.25), the strongest haven, fails to clear NZD
(+1.50), the weakest commodity**, by a full point. *Delete CAD and CHF from
the board entirely and there is still no risk-off trade.*

Block means: **commodity +3.86 vs haven −0.25 — a 4.11 gap the wrong way.**
USD is the only haven that reaches into the commodity range at all, and only
at its bottom.

**Closest to qualifying: NZDUSD SHORT at +0.75**, 75% of the way there. NZD
has no release this week so its score is frozen; **USD has jobless claims and
Philly Fed tonight (20:30 PHT) and Jackson Hole 27–29 Aug.** A USD gain of
0.25 puts this trade live — it is the one to re-check, not a dead end.

| Pair | Dir | Type | Spread | D-range pos | Structure verdict |
|---|---|---|---|---|---|
| **CADJPY** | LONG | **RISK-ON** | 8.00 | 69.2% | ✅ **5-touch support 64 pips below** |
| **EURJPY** | LONG | **RISK-ON** | 5.50 | 69.1% | ✅ **no overhead resistance, new highs** |
| **GBPJPY** | LONG | **RISK-ON** | 5.00 | 60.0% | ✅ **4-touch support 83 pips below, 4-touch resistance 45 above** |
| **CADCHF** | LONG | RISK-ON | **11.00** | 60.3% | ❌ broke down through 8-touch resistance |
| EURCHF | LONG | RISK-ON | 8.50 | 42.8% | ❌ fell 1.00%, mid-range, no edge |
| GBPCHF | LONG | RISK-ON | 8.00 | 27.7% | ❌ fell 1.33% |
| **AUDCAD** | SHORT | **COMM** | 5.92 | 34.1% | ✅ **low in range, AUD downgraded today** |
| NZDCAD | SHORT | COMM | 6.50 | 72.9% | ❌ **rising into a 5-touch support that is holding** |
| AUDNZD | LONG | COMM | 0.58 | — | ⬜ spread too narrow to act on |
| USDCHF | LONG | SAFE | 5.25 | 8.6% | ❌ 21-day low printed 19 Aug |
| CHFJPY | SHORT | SAFE | 3.00 | 66.9% | ❌ CHF beat JPY +0.97% |
| USDJPY | LONG | SAFE | 2.25 | 37.1% | ❌ USD lost to both havens |

**Read the shape, not just the rows.** The split inside RISK-ON is **entirely CHF-leg vs JPY-leg**: all three JPY crosses carried, all three CHF crosses rejected. **COMM has one clean trade; SAFE has nothing tradable at all** — every haven pairing runs into the same unexplained CHF bid. Only AUDNZD is left unread, and only because a 0.58 spread is not worth a chart.

### 4.3 CARRIED — fundamentals and structure agree

Zones drawn on OANDA this session; entity IDs recorded for clearing next run.
**Zones are observations of structure (LD-5), never entry/stop/target roles.**

| | **CADJPY — LONG** | **EURJPY — LONG** | **GBPJPY — LONG** | **AUDCAD — SHORT** |
|---|---|---|---|---|
| **Rank / Spread** | **1 · 8.00** | 2 · 5.50 | 4 · 5.00 | 3 · 5.92 |
| **Type** | RISK-ON | RISK-ON | RISK-ON | COMMODITY |
| **Fundamental** | CAD +8.00 vs JPY +0.00 | EUR +5.50 vs JPY +0.00 | GBP +5.00 vs JPY +0.00 | CAD +8.00 vs AUD +2.08 |
| **Why this one** | Only top-spread pair with **no CHF leg** | Flat on 19 Aug (−0.05%) — did not join the CHF move | **Cleanest two-sided structure** — 4 touches each side | Spread widened 3.92→5.92 **this morning** |
| **Close** | 114.760 | 184.972 *(H4 high 185.126 today)* | 215.594 | 0.98200 |
| **Support zone** | **113.852–114.352** · 5 touches · 12,13,13,14,19 Aug · −64 pips | 183.926–184.120 · 2 touches · 17,19 Aug · −95 pips | **214.539–214.884** · 4 touches · 12,13,14,19 Aug · −83 pips | 0.97550–0.97800 · 45-day low zone |
| **Resistance zone** | 114.992–115.203 · 4 touches · 17–18 Aug · +24 pips | 187.000–187.478 · 45-day high | **215.890–216.222** · 4 touches · 14,17,18,19 Aug · +45 pips | **0.98565–0.98792** · 3 touches · 18–19 Aug · +36 pips |
| **D-range position** | 69.2% of 110.832–116.482 | 69.1% of 179.369–187.478 | 60.0% of 209.575–219.614 | 34.1% of 0.97550–0.99457 |
| **Falsifier** | daily close below **113.852** | daily close below **183.926** | daily close below **214.539** | daily close above **0.98792** |
| **TV entities** | `Zxu0GY` `WmQ0Wi` | `3HbwVj` `mBoNna` | `JNNCoC` `LCSHqY` | `On2g7x` `K1Yvlb` |

**All three JPY crosses carried.** GBP is the weakest of the three strong currencies (+5.00) but GBPJPY has the **most symmetrical structure on the board** — tested support 83 pips below, tested resistance 45 pips above, price mid-way. Lower spread, tighter structure.

⚠️ AUDCAD carries **7 rectangles of Jeff's own** — untouched; only the two above are mine.

### 4.4 REJECTED — the model says yes, price says no

| Pair | Dir | Spread | Reason |
|---|---|---|---|
| **CADCHF** | LONG | **11.00** | **Widest spread on the board.** Price broke **down** through an 8-touch resistance zone (0.58330–0.58645, tested 12–19 Aug) on 19 Aug, **no support beneath**. `ujBqUx` |
| EURCHF | LONG | 8.50 | Fell 1.00%; 42.8% of range — no edge either way |
| GBPCHF | LONG | 8.00 | 27.7% of range, fell 1.33% |
| USDCHF | LONG | 5.25 | 8.6% of range, printed its 21-day low on 19 Aug |
| CHFJPY | SHORT | 3.00 | CHF **beat** JPY +0.97% — short is directly against price |
| **NZDCAD** | SHORT | 6.50 | **Rising, not falling.** 72.9% of range, up 0.97% over 45 days, and a **5-touch support at 0.81244–0.81662** (12,13,17,18,19 Aug) is holding it up. Shorting into tested structure. `jWo9Jr` |

**Five of the six share one leg: CHF** (NZDCAD is the exception — a commodity cross rejected on its own structure). The model scores it −3.00 (last); price bid it **+1.35% against a five-cross basket** on 19 Aug and **it also beat JPY**, which rules out generic risk-off. **No CHF release lands Mon–Fri**, so the score cannot correct this week.

**The largest fundamental spread on the board is untradeable, and this section says so.** That is the structure filter working, not failing.

### 4.5 Week summary

| Carry | **CADJPY LONG · EURJPY LONG · GBPJPY LONG · AUDCAD SHORT** |
|---|---|
| **Watch** | CADCHF — a daily close back above **0.58467** puts it in play |
| **Avoid** | every CHF cross while the bid is unexplained |
| **Theme** | **JPY weakness is the broader trade** — all three JPY crosses carried, on three different strong currencies. **CAD strength** is the sharper one: perfect +8.00 and the best calendar week (inflation 3.0% Mon, retail sales projected GOOD Fri), in two of the four carried pairs |

---

## §5 — Gold (XAUUSD)

**Drivers.** Real yields **+25–30bp** over the FOMC intermeeting period and three hawkish dissents — both headwinds. **Gold rose anyway; that is the signal.** F&G safe-haven-demand component 68.0 (greed).

| Level | Value | Formed | Recompute |
|---|---|---|---|
| 21-day high | **4,524.34** | 19 Aug | breakout bar, volume **920,850 vs 685,763 avg = 1.34×** |
| 21-day low | 3,996.055 | in window | — |
| Close | 4,505.285 | 20 Aug *(forming)* | — |
| Range | 528.285 | — | 4,524.34 − 3,996.055 |
| **Position** | **96.4%** | — | (4,505.285 − 3,996.055) / 528.285 |

**Read:** +9.36% over the window, at the top of its band, today's forming bar holding the gain rather than giving it back. **Gold and CHF tell the same story; USD strength does not.**
**Falsifier:** daily close below **4,436.23** (18 Aug high, the level the breakout cleared) marks 19 Aug as a spike, not a trend.

## §6 — BTC (BTCUSD)

| Level | Value | Formed | Recompute |
|---|---|---|---|
| 21-day high | **70,029.5** | 20 Aug *(forming — provisional)* | — |
| 21-day low | 62,203.0 | in window | — |
| Close | 69,488.0 | 20 Aug *(forming)* | — |
| Range | 7,826.5 | — | 70,029.5 − 62,203.0 |
| **Position** | **93.1%** | — | (69,488.0 − 62,203.0) / 7,826.5 |

**With risk or decoupled? DECOUPLED — and that is the interesting part.** BTC rose **+7.04%** on the same 19 Aug bar that produced a CHF bid and a Gold breakout. Risk-off flow and BTC strength do not normally coexist; and with F&G equity internals weak (stock strength 26.2, momentum 44.8), BTC is not tracking equity breadth either.
**Falsifier:** daily close below **64,551.50** (18 Aug close, base of the 19 Aug move) voids the decoupling read.

---

## §7 — Method notes

**Corrections to earlier editions: none.** No figure published in r9 was found wrong this run; the AU "phantom" was already handled correctly there.

| # | Note |
|---|---|
| 1 | The phantom guard returned **NULL on the calendar view** and **PASS on the series pages** — reported as two results, not collapsed into one verdict. *A guard that cannot fire is not a guard that passed.* |
| 2 | The AU release was verified against the **issuing agency** (abs.gov.au), not just TE. That is what F-1 requires, and it worked. |
| 3 | RBA needed a **same-origin Referer** — see F-10. |
| 4 | Two TE slugs return **200 with zero data** — see F-11. Working slug: `/euro-area/inflation-cpi`. |
| 5 | The week table **silently dropped Mon–Tue** until Jeff caught it — see F-13. |

---

## §8 — Findings

Detail and evidence live in **STATE.md** (moved there 2026-08-20 — process
notes are not market analysis).

| ID | One line | Status |
|---|---|---|
| **F-1** | TE publishes unreleased figures in the ACTUAL field. Guard runs first, every run. | OPEN — a candidate mechanism correction is logged, not applied |
| **F-7** | `batch_run` defective — retested today on a valid call, 3/3 failed. | OPEN, now properly evidenced |
| **F-9** | TradingView CDP unreachable on a Store-installed app. | **CLOSED** — `TvMsixLaunch.exe`, recipe in STATE.md |
| **F-10** | RBA needs a *same-origin* Referer, not the Google one the ladder documents. | OPEN |
| **F-11** | A 200 response is not proof of data — two TE slugs serve 253KB and zero values. | OPEN |
| **F-13** | **The week table silently dropped Mon–Tue** — the undated TE calendar URL serves a forward window, and I filtered it without checking its span. 6 of 19 events missing. *Caught by Jeff.* | **FIXED r5** — use `?dates=from/to` and assert the span before filtering |
| **F-12** | **I called a denied tool (`ui_evaluate`).** No harm; finding re-derived through an allowed path. | Recorded |

## §9 — Publish gate

| Gate | Status |
|---|---|
| **P1 SOURCED** | **PASS** — 70/70 whitelist indicators with source, reference period, release status. 8/8 policy rates, primary where machine-readable else labelled fallback. Both guards documented. Zones carry venue-prefixed symbol, timeframe, touch count and dates. |
| **P2 RECOMPUTED** | **PASS** — tally from `score_model.py`; F&G seven-mean to 4dp (0.0000 diff); every zone shows range and position arithmetic; every move shows open → close in pips and percent. |
| **P3** | **UNSEALED** — awaiting Jeff |

**Open against a seal**

| # | Item |
|---|---|
| 1 | **Today's daily bar is still forming.** BTC's 21-day high sits on it and is provisional; other extremes are on closed bars. |
| 2 | **Fed Chair unresolved** — the minutes list Warsh in the Chair's voting position. Flagged, not asserted; §3 names no Chair. |
| 3 | **12 of 21 watchlist pairs unread.** Nine pulled. `batch_run` confirmed defective (F-7), so the rest need single-symbol reads. |
| 4 | **Friday's six events are pending** — the week's projections are not yet fully graded. |

**Structurally complete** — bias *and* key levels per LD-4. Defensible LIGHT seal; the four items above are disclosure, not blockers.
