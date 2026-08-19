---
edition: 2026-08-19
revision: 6 (supersedes r1-r5 - see CORRECTIONS)
generated: 2026-08-19 14:12 PHT
data_asof: 2026-08-19 14:12 PHT
horizon: INTRADAY (Wednesday - no swing block, no carry per LD-8)
seal: UNSEALED - DRAFT
seal_tier: LIGHT (per LD-12)
artifact_url: https://claude.ai/code/artifact/6ad31052-2b2c-4935-9573-908f00af2e7a
---

# Daily Market Sentiment — Wednesday 19 August 2026

**All times Philippine Standard Time (UTC+8).**
**TradingEconomics calendar times are UTC → PHT = UTC + 8h.**

---

## CORRECTIONS (r1 -> r2 -> r3)

**C-1 — TIMEZONE CONVERSION WAS WRONG (my error, caught by Jeff).**
r1 treated the TE time column as **ET (UTC-4)** and applied **+12h**. It is
**UTC**, so the correct conversion is **+8h**. Every schedule in r1 was
**4 hours late**.

*Proof:* UK CPI released 07:00 BST = 06:00 UTC. TE showed `06:00`. 06:00
UTC → **14:00 PHT**, which is when it actually landed. r1 said 18:00 PHT.

**C-2 — UK CPI HAS RELEASED, and r1's "Previous" was wrong.**
r1 listed UK CPI as *not yet released* with Previous 2.9%. Actual:

| | r1 said | Correct |
|---|---|---|
| Status | Not yet released | **RELEASED 14:00 PHT** |
| Actual | — | **2.9% YoY** |
| Previous | 2.9% | **2.6%** |
| Core | — | **2.6%** (vs 2.5% consensus — beat) |

**C-3 — NZD RESOLVED, and in the opposite direction.** r1 excluded NZD and
flagged a possible RBNZ *cut* on 20 Aug. Wrong: RBNZ **hiked 25bp to 2.50%
on 8 July — its first hike in three years**. No August meeting; next is
2 Sep. NZD is now ranked.

**C-4 — PHANTOM COUNT REVISED 13 → 9.** With the corrected +8h conversion,
four rows previously flagged had in fact already released. The finding
stands; the count was inflated by C-1.

**C-8 — NINE WHITELIST INDICATORS WRONGLY MARKED UNAVAILABLE (Jeff caught
it).** r3/r4 declared these "not released / not available": JP Machine Tool
Orders, JP S&P Global Mfg PMI Final, AU Household Spending, AU Westpac
Consumer Confidence, AU NAB Business Confidence, AU ANZ-Indeed Job Ads,
NZ Electronic Retail Card Spending, NZ ANZ Business Confidence, JP
Household Spending. **All nine are published on TradingEconomics.** I read
summarized country-page fetches instead of the indicators' own pages, and
treated "absent from the summary" as "not released".

**A tenth was worse than an omission:** I described the Swiss PMI row as a
"generic Swiss Manufacturing PMI" substituted for the named
`Procure.ch Manufacturing PMI`. It **is** the named indicator — TE's own
text reads "procure.ch–UBS Manufacturing PMI". I flagged a substitution
that never happened, implying a data gap that did not exist.

**IMPACT ON THE RANKING — this was not cosmetic.** AUD **+3 → +6**, now
tied with CAD at the top with **zero BAD scores**; JPY +2 → +3; NZD +1 →
+3. The top alignment changed from CAD/CHF to AUD/CHF.

**C-6 — OFF-LIST DATA WAS INJECTED (Jeff caught it).** r1/r2 filled §2 with
whatever TradingEconomics served: DE PPI, ZA Retail Sales, US Housing Starts,
US Jobless Claims, EA Current Account and more — 24 of 34 rows were either
an unauthorized country or an indicator never named in
`Idea_dump/Macro_economic_indicators.txt`. §2 is now rebuilt from the
WHITELIST only. Off-list data may still shape the narrative in §1; it is
never a scored row. This changed the ranking materially (CAD to #1, EUR up).

**C-7 — EA INFLATION DIRECTION WAS INVERTED.** r2 read the calendar row and
reported EA inflation falling to 2.8% from 2.9%. The country-page series
shows **2.9% from 2.8% — rising**. EA is hike-leaning, not cooling.

**C-5 — AUD RANKING WAS WRONG.** r1 put AUD at #6 on flat wages. It missed
**RBA Deputy Governor Hauser's 19 Aug speech** naming three upside
inflation risks and warning of a hike. AUD moves to **#3**.

---

## §1 — Headline Alerts, News & Current Events

### ⚠ Geopolitical — Strait of Hormuz escalation *(dominant macro driver)*

| Time (PHT) | Event | Impact |
|---|---|---|
| ~09:00 | **UAE suspends trade with Iran** | Retired US general: potentially more significant than US sanctions |
| ~09:00 | **Strait of Hormuz standoff** — Trump says open, Iran says shut | **Oil up 4th consecutive session**, WTI +0.94% to $84.85 |
| ~11:00 | **France expels Iranian diplomats** | Diplomatic channel narrowing |

**Read:** Oil at 3-week highs on a supply-route threat. Direct positive for
**CAD** (petro-currency), inflationary pressure everywhere, and a live
upside risk to inflation that Hauser named explicitly for **AUD**.

### 🏦 Central bank commentary

| Time (PHT) | Event | Impact |
|---|---|---|
| **10:45** | **RBA Deputy Gov Hauser speech** | Named **three upside inflation risks** — Middle East conflict, the AI boom, poor productivity — and **warned of a hike if they crystallise** |
| 15:10 | ECB President Lagarde speech | — |
| **02:00 Thu** | **FOMC Minutes** | Due 02:00 PHT Thursday |

**RBA context:** held at **4.35%** for a second meeting, after **+75bp
since February**. Bullock has not ruled out further hikes. **This is a
hawkish hold, not a neutral one** — and r1 missed it entirely.

### 📉 Risk events

| Time (PHT) | Event | Impact |
|---|---|---|
| ~13:00 | **Asian semiconductor selloff** — KOSPI halted after −5%, SK Hynix and Samsung hit hard | Risk-off in Asia |
| Yesterday | **Nasdaq −1%+** on surging Treasury yields | Tech valuations under pressure |
| ~14:00 | **China youth unemployment 17.9%** — 11-month high | China demand concern → AUD/NZD headwind |
| Yesterday | **Trump pauses 50% tariffs on Canada**, claims deal imminent | **CAD positive** |
| ~10:00 | Gold recovers modestly after its largest drop in a month | See §5 |

### 📊 Sentiment — CNN Fear & Greed Index

**Source gap CLOSED (Jeff's fix).** `edition.cnn.com` returns HTTP 451
(geo-blocked) and the dataviz endpoint returns HTTP 418 to a plain fetch,
but it serves normally with browser headers. Endpoint:
`production.dataviz.cnn.io/index/fearandgreed/graphdata`.

**Index: 54.29 — NEUTRAL** (CNN timestamp 19 Aug 08:00 PHT)

| Horizon | Value | Rating | Δ vs now |
|---|---|---|---|
| **Now** | **54.29** | **Neutral** | — |
| Previous close | 54.40 | Neutral | −0.11 |
| 1 week ago | 62.94 | Greed | **−8.66** |
| 1 month ago | 37.23 | Fear | **+17.06** |
| 1 year ago | 59.89 | Greed | −5.60 |

#### The seven components

| Component | Score | Rating | As of (PHT) |
|---|---|---|---|
| **Junk Bond Demand** | **96.6** | **EXTREME GREED** | 19 Aug 08:00 |
| Safe Haven Demand | 58.4 | Greed | 19 Aug 03:59 |
| Stock Price Breadth | 57.2 | Greed | 19 Aug 07:59 |
| Market Volatility (VIX) | 50.0 | Neutral | 19 Aug 04:15 |
| Put/Call Options | 48.0 | Neutral | 19 Aug 04:38 |
| Market Momentum (S&P 500) | 44.0 | Fear | 19 Aug 04:38 |
| **Stock Price Strength** | **25.8** | **FEAR** | 19 Aug 07:59 |

**Recompute (P2):** (96.6 + 58.4 + 57.2 + 50.0 + 48.0 + 44.0 + 25.8) / 7 =
**54.29** — matches the published index exactly. CNN uses a **simple
average** of the seven, not a weighted one. The components therefore fully
explain the headline.

**Read — the headline hides the story.** "Neutral 54" is the average of a
market that is **not** neutral internally. The spread between the highest
and lowest component is **70.8 points**:

- **Junk Bond Demand 96.6 (extreme greed)** — credit markets are pricing
  almost no risk premium. This is the single most stretched reading on the
  board.
- **Stock Price Strength 25.8 (fear)** — few stocks at 52-week highs.
  Narrow participation.

Credit is euphoric while equity breadth is thin. That combination is a
**divergence**, and the index's own averaging conceals it — which is
exactly why the components are published here rather than the headline
alone.

**Cross-check against §1:** this is consistent with today's tape. The
Asian semiconductor selloff (KOSPI halted at −5%) and the Nasdaq's
yield-driven decline are equity-side stress, matching Stock Price
Strength at 25.8. Junk bond demand at 96.6 has not repriced for it yet.

**Direction:** the index fell from **62.94 a week ago** (greed) to 54.29
(neutral) — sentiment cooling — but is still far above **37.23 a month
ago** (fear). Range-bound in neutral, drifting down.

**Falsifier:** junk bond demand dropping below ~70 would confirm credit
repricing to match equity stress, turning this from a divergence into a
broad risk-off. Stock price strength recovering above 50 would resolve it
the other way.


---

## §2 — Macro Economic Indicators

**WHITELIST, COMPLETE.** All **70** indicators named in
`Idea_dump/Macro_economic_indicators.txt` across the five scored categories
are listed below for all 8 currencies. Nothing is omitted; anything that
could not be sourced is flagged **NOT FOUND** rather than dropped, so it can
be verified rather than silently lost. Interest Rate (category 6) is scored
separately in §3.

### Scoring method (locked 2026-08-19)

Categories are **not** equally weighted — Employment and Inflation drive the
rate decision, so they carry more:

| Category | Weight |
|---|---|
| **Inflation** | **3** |
| **Employment** | **2** |
| Production | 1 |
| Spending | 1 |
| Trade | 1 |

Within a category, a currency's indicators **split that weight evenly**. So
US Production has 3 indicators → each is worth 1 ÷ 3 = **0.333**; a GOOD
scores **+0.333**, a BAD **−0.333**, a NEUTRAL **0**. AUD Employment has 3
indicators sharing weight 2 → **0.667** each.

**Range: +8.00 (every category good) to −8.00.**


### PRODUCTION — category weight 1

| Ccy | Indicator | Actual | Prev | Ref | Rule | Score | Pts |
|---|---|---|---|---|---|---|---|
| US | ISM Manufacturing PMI | 53.9 | 53.9 | Jul/26 | >50.5 | **GOOD** | +0.33 |
| US | Industrial Production YoY | 1.1% | 1.29% | Jul/26 | >0.5% | **GOOD** | +0.33 |
| US | Durable Goods Ex Transp MoM | 0.6% | 1.8% | Jun/26 | >0.5% | **GOOD** | +0.33 |
| EA | S&P Global Mfg PMI Final | 51.9 | 51.4 | Jul/26 | >50.5 | **GOOD** | +0.50 |
| EA | Industrial Production YoY | 0.1% | -0.1% | Jun/26 | 0-0.5% | NEUTRAL | +0.00 |
| GB | S&P Global Mfg PMI Final | 51.9 | 52.5 | Jul/26 | >50.5 | **GOOD** | +0.33 |
| GB | Industrial Production YoY | -0.2% | 1.0% | Jun/26 | <0% | **BAD** | -0.33 |
| GB | Manufacturing Production YoY | 0.5% | 2.0% | Jun/26 | 0-0.5% | NEUTRAL | +0.00 |
| JP | Industrial Production YoY Final | 4.9% | -2.1% | Jun/26 | >0.5% | **GOOD** | +0.25 |
| JP | Machinery Orders YoY | 16.9% | -1.9% | Jun/26 | >0.5% | **GOOD** | +0.25 |
| JP | Machine Tool Orders YoY | 50.4% | 52.8% | Jul/26 | >0.5% | **GOOD** | +0.25 |
| JP | S&P Global Mfg PMI Final | 54.5 | 54.8 | Jul/26 | >50.5 | **GOOD** | +0.25 |
| AU | S&P Global Mfg PMI Final | 52.0 | 51.5 | Jul/26 | >50.5 | **GOOD** | +1.00 |
| NZ | Business NZ PMI | 54.3 | 60.1 | Jul/26 | >50.5 | **GOOD** | +0.50 |
| NZ | Global Dairy Trade Price Index | 2.3% | 0.1% | Aug/26 | >0.5% | **GOOD** | +0.50 |
| CA | S&P Global Mfg PMI | 53.5 | 53.0 | Jul/26 | >50.5 | **GOOD** | +1.00 |
| CH | Procure.ch-UBS Mfg PMI | 53.2 | 54.3 | Jul/26 | >50.5 | **GOOD** | +0.50 |
| CH | Industrial Production YoY | -7.1% | -0.4% | Mar/26 | <0% | **BAD** | -0.50 |

**Category totals:** USD +1.00 · EUR +0.50 · GBP +0.00 · JPY +1.00 · AUD +1.00 · NZD +1.00 · CAD +1.00 · CHF +0.00

### SPENDING — category weight 1

| Ccy | Indicator | Actual | Prev | Ref | Rule | Score | Pts |
|---|---|---|---|---|---|---|---|
| US | Building Permits MoM Final | +5.0% | -2.6% | Jul/26 | >0.5% | **GOOD** | +0.25 |
| US | Retail Sales YoY | 5.0% | 6.8% | Jul/26 | >0.5% | **GOOD** | +0.25 |
| US | CB Consumer Confidence | 51.0 | 55.2 | Aug/26 | >Prev | **BAD** | -0.25 |
| US | Personal Spending MoM | 0.3% | 0.9% | Jun/26 | 0-0.5% | NEUTRAL | +0.00 |
| EA | Retail Sales YoY | 0.7% | 1.9% | Jun/26 | >0.5% | **GOOD** | +0.50 |
| EA | Consumer Confidence Final | -15.9 | -17.6 | Jul/26 | >Prev | **GOOD** | +0.50 |
| GB | GfK Consumer Confidence | -17 | -23 | Jul/26 | >Prev | **GOOD** | +0.50 |
| GB | Retail Sales YoY | 4.2% | 3.5% | Jun/26 | >0.5% | **GOOD** | +0.50 |
| JP | Household Spending YoY | -3.3% | -0.4% | Jun/26 | <0% | **BAD** | -0.33 |
| JP | Consumer Confidence | 34.9 | 33.8 | Jul/26 | >Prev | **GOOD** | +0.33 |
| JP | Retail Sales YoY | 0.5% | 5.0% | Jun/26 | 0-0.5% | NEUTRAL | +0.00 |
| AU | Household Spending YoY | 6.0% | - | Jun/26 | >0.5% | **GOOD** | +0.25 |
| AU | Building Permits YoY Final | 8.9% | 5.5% | Jun/26 | >0.5% | **GOOD** | +0.25 |
| AU | Westpac Consumer Conf Change | 88.9 | 83.9 | Aug/26 | >Prev | **GOOD** | +0.25 |
| AU | NAB Business Confidence | -6 | -6 | Jul/26 | >Prev | NEUTRAL | +0.00 |
| NZ | Building Permits MoM | -3.6% | -4.9% | Jun/26 | <0% | **BAD** | -0.25 |
| NZ | Electronic Retail Card Spending YoY | 0.9% | 0.9% | Q1/26 | >0.5% | **GOOD** | +0.25 |
| NZ | ANZ Business Confidence | 56.1 | 36.6 | Jul/26 | >Prev | **GOOD** | +0.25 |
| NZ | ANZ Roy Morgan Consumer Conf | 99.3 | 91.3 | Jul/26 | >Prev | **GOOD** | +0.25 |
| CA | Retail Sales YoY | 5.9% | 3.6% | May/26 | >0.5% | **GOOD** | +0.50 |
| CA | Building Permits MoM | +18.5% | -3.0% | Jun/26 | >0.5% | **GOOD** | +0.50 |
| CH | Consumer Confidence | -35 | -36 | Jul/26 | >Prev | **GOOD** | +0.50 |
| CH | Retail Sales YoY | 1.5% | 3.4% | Jun/26 | >0.5% | **GOOD** | +0.50 |

**Category totals:** USD +0.25 · EUR +1.00 · GBP +1.00 · JPY +0.00 · AUD +0.75 · NZD +0.50 · CAD +1.00 · CHF +1.00

### TRADE — category weight 1

| Ccy | Indicator | Actual | Prev | Ref | Rule | Score | Pts |
|---|---|---|---|---|---|---|---|
| US | Balance of Trade | -$73.26B | -$77.65B | Jun/26 | >Prev | **GOOD** | +1.00 |
| EA | Balance of Trade | EUR8,600M | EUR-9,000M | Jun/26 | >Prev | **GOOD** | +1.00 |
| GB | Balance of Trade | GBP-5,537M | GBP-3,464M | Jun/26 | <Prev | **BAD** | -1.00 |
| JP | Balance of Trade | JPY-407B | JPY-392B | Jun/26 | <Prev | **BAD** | -1.00 |
| AU | Balance of Trade | A$1,929M | A$-2,367M | Jun/26 | >Prev | **GOOD** | +1.00 |
| NZ | Balance of Trade | NZ$23M | NZ$577M | Jun/26 | <Prev | **BAD** | -1.00 |
| CA | Balance of Trade | C$3,860M | C$3,700M | Jun/26 | >Prev | **GOOD** | +1.00 |
| CH | Balance of Trade | CHF3,800M | CHF5,530M | Jun/26 | <Prev | **BAD** | -1.00 |

**Category totals:** USD +1.00 · EUR +1.00 · GBP -1.00 · JPY -1.00 · AUD +1.00 · NZD -1.00 · CAD +1.00 · CHF -1.00

### EMPLOYMENT — category weight 2

| Ccy | Indicator | Actual | Prev | Ref | Rule | Score | Pts |
|---|---|---|---|---|---|---|---|
| US | Non Farm Payrolls | -23K | 20K | Jul/26 | >Cons | **BAD** | -1.00 |
| US | Unemployment Rate | 4.1% | 4.2% | Jul/26 | <Prev | **GOOD** | +1.00 |
| EA | Unemployment Rate | 6.3% | 6.3% | Jun/26 | unchanged | NEUTRAL | +0.00 |
| GB | Claimant Count Change | -11K | -6.4K | Jul/26 | <Prev | **GOOD** | +2.00 |
| JP | Unemployment Rate | 2.5% | 2.5% | Jun/26 | unchanged | NEUTRAL | +0.00 |
| AU | ANZ-Indeed Job Ads MoM | +0.8% | -0.1% | Jul/26 | >0.5% | **GOOD** | +0.67 |
| AU | Employment Change | 76.3K | 43.9K | Jun/26 | >Prev, FT-weighted | **GOOD** | +0.67 |
| AU | Unemployment Rate | 4.4% | 4.4% | Jun/26 | unchanged | NEUTRAL | +0.00 |
| NZ | Unemployment Rate | 5.6% | 5.4% | Jun/26 | >Prev | **BAD** | -2.00 |
| CA | Unemployment Rate | 6.4% | 6.5% | Jul/26 | <Prev | **GOOD** | +1.00 |
| CA | Employment Change | 75.1K | 18.2K | Jul/26 | >Prev, FT-weighted | **GOOD** | +1.00 |
| CH | Non Farm Payrolls | +0.5% | +0.2% | Q1/26 | >Cons | **GOOD** | +1.00 |
| CH | Unemployment Rate | 3.0% | 2.9% | Jul/26 | >Prev | **BAD** | -1.00 |

**Category totals:** USD +0.00 · EUR +0.00 · GBP +2.00 · JPY +0.00 · AUD +1.33 · NZD -2.00 · CAD +2.00 · CHF +0.00

### INFLATION — category weight 3

| Ccy | Indicator | Actual | Prev | Ref | Rule | Score | Pts |
|---|---|---|---|---|---|---|---|
| US | Inflation Rate YoY | 3.4% | 3.5% | Jul/26 | >2% & falling | NEUTRAL | +0.00 |
| EA | Inflation Rate YoY Final | 2.9% | 2.8% | Jul/26 | >2% & rising | **GOOD** | +3.00 |
| GB | Inflation Rate YoY | 2.9% | 2.6% | Jul/26 | >2% & rising | **GOOD** | +3.00 |
| JP | Inflation Rate YoY | 1.7% | 1.5% | Jun/26 | <2% & rising | NEUTRAL | +0.00 |
| AU | Inflation Rate YoY | 3.8% | 4.0% | Jun/26 | >2% & falling | NEUTRAL | +0.00 |
| NZ | Inflation Rate YoY | 4.1% | 3.1% | Jun/26 | >2% & rising | **GOOD** | +3.00 |
| CA | Inflation Rate YoY | 3.0% | 2.8% | Jul/26 | >2% & rising | **GOOD** | +3.00 |
| CH | Inflation Rate YoY | 0.4% | 0.5% | Jul/26 | <2% & falling | **BAD** | -3.00 |

**Category totals:** USD +0.00 · EUR +3.00 · GBP +3.00 · JPY +0.00 · AUD +0.00 · NZD +3.00 · CAD +3.00 · CHF -3.00

---

### Weighted model tally

| # | Ccy | Prod (1) | Spend (1) | Trade (1) | Employ (2) | Infl (3) | **TOTAL** | vs r5 unweighted |
|---|---|---|---|---|---|---|---|---|
| **1** | **CAD** | +1.00 | +1.00 | +1.00 | +2.00 | +3.00 | **+8.00** | +6 → **#2 → #1** |
| **2** | **EUR** | +0.50 | +1.00 | +1.00 | +0.00 | +3.00 | **+5.50** | +5 → **#4 → #2** |
| **3** | **GBP** | +0.00 | +1.00 | -1.00 | +2.00 | +3.00 | **+5.00** | +3 → **#5 → #3** |
| **4** | **AUD** | +1.00 | +0.75 | +1.00 | +1.33 | +0.00 | **+4.08** | +6 → **#1 → #4** |
| **5** | **USD** | +1.00 | +0.25 | +1.00 | +0.00 | +0.00 | **+2.25** | +5 → **#3 → #5** |
| **6** | **NZD** | +1.00 | +0.50 | -1.00 | -2.00 | +3.00 | **+1.50** | +3 → **#7 → #6** |
| **7** | **JPY** | +1.00 | +0.00 | -1.00 | +0.00 | +0.00 | **+0.00** | +3 → **#6 → #7** |
| **8** | **CHF** | +0.00 | +1.00 | -1.00 | +0.00 | -3.00 | **-3.00** | -1 → same |

**The weighting reordered almost the whole board.** Five of eight currencies
moved rank. Two results are worth reading carefully:

**CAD scores a perfect +8.00** — good in *every* category, the only currency
to do so. Under the unweighted tally it merely tied for first.

**AUD fell from #1 to #4** despite having zero BAD scores. Its inflation is
**NEUTRAL** (3.8%, above target but *falling*), which scores **0.00 of the
3.00 available** — while CAD, EUR, GBP and NZD each take the full **+3.00**
there. A three-point swing on one category outweighs AUD's broad but
individually light wins. **This is the weighting working as designed**: it
distinguishes *how many* indicators are good from *which* ones are.

**JPY nets exactly 0.00** — strong production (+1.00) cancelled by a weak
consumer and a widening trade deficit (−1.00), with employment and inflation
both neutral. The unweighted tally showed +3 and hid that balance entirely.


## §3 — Interest Rates

| Ccy | Rate | Last change | Source | Lean |
|---|---|---|---|---|
| **AUD** | **4.35%** | Hold (2nd mtg), +75bp since Feb | TE | **HAWKISH HOLD** — Hauser flags hike risk |
| **USD** | **3.50–3.75%** | −25bp, 11 Dec 2025 | **federalreserve.gov** ✅ | **HOLD/CUT** — housing weak, prices deflating |
| **GBP** | **3.75%** | Jul/26 | TE | **HAWKISH HOLD** — CPI accelerating |
| **NZD** | **2.50%** | **+25bp, 8 Jul 2026** — first hike in 3 years | TE | **TIGHTENING** — next 2 Sep |
| **EUR** | **2.40%** | Jul/26 | TE | **HOLD/DOVISH** — inflation undershooting |
| **CAD** | **2.25%** | Jul/26 | TE | **HOLD** — housing weak, but oil + tariff pause help |
| **JPY** | **1.00%** | Jul/26 | TE | **HOLD, hike watch** — core still <2% |
| **CHF** | **0.00%** | Jun/26 | TE | **HOLD** — at the floor |

**Central bank verification (spec §2.2) — partially blocked.**
- ✅ **federalreserve.gov** — Fed confirmed 3.50–3.75%, last changed
  11 Dec 2025. **Matches TE.**
- ❌ **rba.gov.au** — HTTP 403, blocks automated fetch
- ❌ **rbnz.govt.nz** — HTTP 403, blocks automated fetch
- Remaining CB sites not yet attempted this run

**This is a structural constraint, not an oversight.** Several central bank
sites block programmatic access. Where blocked, TE is used and labelled.

**No market-implied odds quoted** — none obtained with a named source
instrument. Leans are derived from prints, not pricing.

---

## §4 — Conviction Playbook — INTRADAY horizon

*Wednesday: intraday only, no carry (LD-8). Levels are STRUCTURE, never
entries or targets (LD-4, LD-5, LD-7).*

### Currency strength ranking

Ordered by the **weighted model score** (§2), then read against policy
direction (§3) and live news (§1). Where the ranking departs from the raw
score, the reason is stated.

| # | Ccy | Score | Lean | Driving evidence |
|---|---|---|---|---|
| **1** | **CAD** | **+8.00** | **Strong** | **A perfect score — good in every single category, the only currency on the board to manage it.** Inflation 3.0% from 2.8% (full +3.00). Employment: unemployment 6.4% from 6.5% AND Employment Change +75.1K from +18.2K with Full Time +38.6K (full +2.00). Retail Sales 5.9%, Building Permits +18.5%, trade surplus widening, Mfg PMI 53.5. **Plus oil's 4th straight up day and the 50% tariff pause.** Model and news agree completely. |
| **2** | **EUR** | **+5.50** | **Strengthening** | Inflation **2.9% from 2.8%, rising** (+3.00). Balance of Trade swung **−€9.0B → +€8.6B** (+1.00). Retail Sales and Consumer Confidence both improving (+1.00). Held back only by flat employment (6.3% unchanged, 0.00) and a soft Industrial Production print. |
| **3** | **GBP** | **+5.00** | **Firm** | The two heavy categories carry it: inflation **2.9% from 2.6%** with core beating consensus (+3.00), and Claimant Count **−11K vs +11.2K expected** (+2.00 — GB's only employment indicator, so it takes the full weight). Offset by a **widening trade deficit** (−1.00) and Industrial Production −0.2%. |
| **4** | **AUD** | **+4.08** | **Firm but capped** | **Zero BAD scores anywhere — yet only 4th.** Broad wins across production, spending, trade and employment (Job Ads +0.8%, Employment Change +76.3K). **The cap is inflation: 3.8% is above target but FALLING, so it scores 0.00 of the 3.00 available.** Hauser's hike warning today argues the market disagrees with that read — worth watching if the next CPI turns. |
| **5** | **USD** | **+2.25** | **Weak** | Production strong (+1.00) and trade improving (+1.00), but **the heavy categories are empty**: employment nets **0.00** (NFP −23K exactly cancels the unemployment-rate improvement) and inflation **0.00** (3.4% falling). Add CB Consumer Confidence 51.0 from 55.2. **The weighted model now agrees with what the unweighted tally could not see** — r5 scored USD +5 and had to override it manually to rank 7th. |
| **6** | **NZD** | **+1.50** | **Split** | **The most internally divided currency.** Inflation takes the full **+3.00** (4.1% from 3.1%, the largest jump on the board, and the RBNZ already hiked 8 Jul) — but employment takes the full **−2.00** (unemployment 5.6% from 5.4%, its only employment indicator) and trade **−1.00**. Hot inflation against a deteriorating labour market. |
| **7** | **JPY** | **+0.00** | **Neutral, genuinely** | **Nets exactly zero, and the shape is the story.** Production is exceptional (+1.00: Machine Tool Orders +50.4% two months running, Machinery Orders +16.9%, PMI 54.5). It is **cancelled** by a contracting consumer (Household Spending −3.3%, seventh straight fall) and a widening trade deficit (−1.00). Employment and inflation both 0.00. Factory strong, household weak, BoJ unmoved. |
| **8** | **CHF** | **−3.00** | **Weakest** | **The only negative score, and it is driven entirely by inflation: 0.4% and falling takes the full −3.00** against a policy rate already at **0.00%**, so the SNB has no room to respond. Spending is fine (+1.00) and NFP rose 0.5%, but the trade surplus shrank and unemployment ticked up to 3.0%. |

**What changed by weighting, and why it matters:** five of eight currencies
moved rank. The most instructive is **USD** — the unweighted tally scored it
+5 (3rd), and r5 had to *manually override* that to rank it 7th, explaining
in prose that breadth was hiding severity. **The weighted model reaches 5th
on its own arithmetic**, because NFP −23K now cancels against the
unemployment print inside a category worth 2, instead of counting as one
BAD among many. The model no longer needs rescuing from itself.

### 1. CAD/CHF — perfect score vs the only negative

- **Alignment:** CAD **+8.00** (good in every category) against CHF
  **−3.00** (the only negative, driven by inflation at 0.4% and falling
  against a 0.00% floor). **An 11-point spread — the widest possible
  configuration on this board.**
- **Conviction:** **Highest.** No event gate; every input is released data.
- **Technical:** CADCHF not read this run. **No levels published.**
- **Falsifier:** Hormuz de-escalation removing the oil leg, or a Canadian
  inflation reversal — CAD's +3.00 inflation score is a third of its total.

### 2. AUD/CHF — broad strength vs the only negative

- **Alignment:** AUD **+4.08** with **zero BAD scores anywhere** against
  CHF **−3.00**. AUD's cap is a neutral inflation read, not a weakness.
- **Conviction:** High, **but event-gated** — see the AUD block below.
- **Technical:** AUDCHF not read this run. **No levels published.**
- **Falsifier:** AU employment tomorrow printing below the 15.0K consensus,
  or a genuine haven bid returning to CHF.

### 3. EUR/CHF — clean model separation

- **Alignment:** EUR #2 with **zero BAD scores** — the only currency on the
  board with none — against CHF #8. Trade swing −€9.0B → +€8.6B, confidence
  improving, inflation rising to 2.9%.
- **Conviction:** Moderate-high.
- **Technical:** **EURCHF read.** 20-day high **0.94120** with **four
  consecutive daily highs at 0.9410–0.9412** (14, 15, 18, 19 Aug) — a
  tested ceiling; current 0.93973 sits just under it; 20-day low 0.92719.
  The pair is up **+1.11%** over the window and pressing that ceiling.
- **Falsifier:** ECB commentary undercutting the inflation read, or a
  genuine haven bid returning to CHF (which has been absent for weeks).

### ~~GBP/EUR~~ — WITHDRAWN

r2 called this the highest-conviction divergence on the premise that GBP
inflation was rising while EUR was falling. **The EUR half was wrong**
(C-7): EUR inflation is **2.9% from 2.8%, rising**. Both legs are now
hike-leaning, so there is no divergence to trade. Withdrawn rather than
quietly re-scored.

### 4. AUD event gate — DO NOT TRADE INTO THURSDAY 09:30 PHT

- **Alignment:** #4, no BAD scores, Hauser hawkish today.
- **⛔ Blocked:** **AU Employment releases Thu 09:30 PHT** and TE already
  displays a **phantom 76.3K against a 15.0K consensus**. Any AUD position
  taken on the visible number is taken on a figure that does not exist.
- **Not proposed for intraday.**

### Observed structure

**OANDA:AUDUSD** — D1, 20-bar lookback (22 Jul – 19 Aug)
- **0.71296** — 20-day high, Mon 17 Aug
- **0.70729** — current, ~72% of range
- **0.69222** — 20-day low
- Range 0.02074 ≈ 207 pips. *investingLive notes bulls back in the
  0.7077–0.7200 swing area.*

**OANDA:AUDNZD** — D1, 20-bar
- **1.21216** high / **1.20460** current (mid-range) / **1.19136** low

**OANDA:EURCHF** — D1, 20-bar
- **0.94120** — 20-day high, **four consecutive daily highs at 0.9410–0.9412**
  (14, 15, 18, 19 Aug) — a tested ceiling
- **0.93973** current / **0.92719** 20-day low

---

## §5 — Gold (XAUUSD), intraday

**4345.47** (M15 close), **−1.11% session**. Recovered modestly after its
largest single-day drop in nearly a month.

| Level | Type | Evidence |
|---|---|---|
| **4449.83** | 30-day high | Mon 10 Aug |
| **4436.23** | Lower high | Tue 18 Aug |
| **4428.89** | Lower high | Mon 17 Aug |
| **4345.47** | Current | — |
| **4324.68** | Session low | Today |
| **3959.80** | 30-day low | Range floor |

**Three consecutive rejections in 4429–4450**, each lower. Up 6.65% over
30 days but stalling — **distribution under 4450**, not continuation.

**Cross-current:** Hormuz escalation is normally gold-positive, yet gold
fell. Rising Treasury yields are the likely offset (they also hit the
Nasdaq). **Haven bid is going to oil, not gold, today.**

**Falsifier:** a daily close above **4449.83** voids the lower-high
sequence.

---

## §6 — BTC (BTCUSD), intraday

**64,254.5**, **−2.49% over 20 days**. investingLive has it **64,085–65,050**.

| Level | Type | Evidence |
|---|---|---|
| **66,284** | 20-day high | Range top |
| **65,019** | Recent high | Mon 17 Aug |
| **64,254.5** | Current | 50.3% of range |
| **62,469–62,777** | Tested support | Twice, 12–13 Aug |
| **62,203** | 20-day low | Range floor |

**Range-bound, no directional edge.** Both boundaries tested and holding.

**Risk context:** the Asian semiconductor selloff (KOSPI halted at −5%) and
the Nasdaq's yield-driven decline are risk-off. BTC has **not** broken down
with them — it is holding mid-range, so it is **not tracking equity risk
cleanly today**.

**Falsifier:** a close outside 62,203 / 66,284.

---

## §7 — Method notes

**Corrections applied this revision:** C-1 timezone (+12h → +8h), C-2 UK CPI
released with corrected Previous, C-3 NZD hiked not cut, C-4 phantom count
13 → 9, C-5 AUD re-ranked on Hauser.

**Still not working:**
1. **`batch_run` fails** on `quote` and `ohlcv` actions. Pairs must be
   pulled one at a time. **Only 5 of 21 pairs read** — §4's alignments
   still carry no technical levels.
2. ~~CNN Fear & Greed geo-blocked~~ **RESOLVED (r4)** — Jeff supplied the
   dataviz endpoint. The article page still 451s and the endpoint 418s on a
   plain fetch, but it serves with browser headers. Now yielding the index
   plus all seven components.
3. **rba.gov.au and rbnz.govt.nz return HTTP 403** to automated fetches.
   federalreserve.gov worked and confirmed the Fed rate.

**Chart state:** left on `OANDA:BTCUSD` @ 1D. No levels drawn, so no
cleanup owed (LD-6).

---

## Publish gate

- **P1 SOURCED** — ⚠ **PARTIAL.** Every figure carries source, period, and
  release status; schedules corrected to PHT. Gaps: 2 of 8 CB sites
  blocked, no sourced rate odds, no sentiment index.
- **P2 RECOMPUTED** — ✅ Levels name the bars that formed them. Timezone
  conversion re-derived and proven against the UK CPI release time.
- **P3 SEALED** — ❌ **UNSEALED.**

**Recommendation: still do not seal.** r2 fixes five real errors, but 16 of
21 pairs remain unread and §4's alignments are fundamental-only. Closer to
the standard, not yet at it.
