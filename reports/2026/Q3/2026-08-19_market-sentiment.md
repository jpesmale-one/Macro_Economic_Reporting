---
edition: 2026-08-19
revision: 5 (supersedes r1-r4 - see CORRECTIONS)
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

**WHITELIST ONLY.** Every row below is an indicator named in
`Idea_dump/Macro_economic_indicators.txt`, for one of the 8 listed
currencies. Values are the LATEST RELEASED print per TradingEconomics
country pages (read 2026-08-19 14:12 PHT). Off-list countries (DE, ZA, CN,
FR…) and off-list indicators do not appear here — they may inform the
narrative in §1, but they are never scored rows.

### 2.1 PRODUCTION

| Ccy | Indicator | Actual | Prev | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| US | ISM Manufacturing PMI | 53.9 | 53.9 | Jul/26 | >50.5 | **GOOD** |
| US | Industrial Production YoY | 1.1% | 1.29% | Jul/26 | >0.5% | **GOOD** |
| US | Durable Goods Ex Transp MoM | 0.6% | 1.8% | Jun/26 | >0.5% | **GOOD** |
| EA | S&P Global Mfg PMI | 51.9 | 51.4 | Jul/26 | >50.5 | **GOOD** |
| EA | Industrial Production YoY | 0.1% | −0.1% | Jun/26 | 0–0.5% | NEUTRAL |
| CA | S&P Global Mfg PMI | 53.5 | 53.0 | Jul/26 | >50.5 | **GOOD** |
| AU | S&P Global Mfg PMI | 52.0 | 51.5 | Jul/26 | >50.5 | **GOOD** |
| NZ | Business NZ PMI | 54.3 | 60.1 | Jul/26 | >50.5 | **GOOD** (falling hard) |
| NZ | Global Dairy Trade Price Index | 2.3% | 0.1% | Aug/26 | >0.5% | **GOOD** |
| JP | Industrial Production YoY | 4.9% | −2.1% | Jun/26 | >0.5% | **GOOD** |
| JP | Machinery Orders YoY | 16.9% | −1.9% | Jun/26 | >0.5% | **GOOD** |
| JP | Machine Tool Orders YoY | 50.4% | 52.8% | Jul/26 | >0.5% | **GOOD** |
| JP | S&P Global Mfg PMI Final | 54.5 | 54.8 | Jul/26 | >50.5 | **GOOD** |
| GB | S&P Global Mfg PMI | 51.9 | 52.5 | Jul/26 | >50.5 | **GOOD** |
| GB | Industrial Production YoY | −0.2% | 1.0% | Jun/26 | <0% | **BAD** |
| GB | Manufacturing Production YoY | 0.5% | 2.0% | Jun/26 | 0–0.5% | NEUTRAL |
| CH | procure.ch–UBS Manufacturing PMI | 53.2 | 54.3 | Jul/26 | >50.5 | **GOOD** |
| CH | Industrial Production YoY | −7.1% | −0.4% | Mar/26 | <0% | **BAD** (Q1 — stale) |

**Read:** JP production is the standout — Industrial Production +4.9% from
−2.1% and Machinery Orders +16.9% from −1.9%, both sharp reversals. GB is
the weak leg: PMI still expanding but Industrial Production has turned
negative. CH Industrial Production is **Mar/26 — five months stale** and
carries little weight.

**All named Production indicators are present.** JP Machine Tool Orders
+50.4% YoY (Jul) after +52.8% in Jun — two consecutive months above +50%.
JP Manufacturing PMI Final 54.5, its seventh straight month of expansion.
The Swiss PMI row IS `procure.ch–UBS`, the indicator named in the list —
r4 wrongly described it as a generic substitute (see C-8).

### 2.2 SPENDING

| Ccy | Indicator | Actual | Prev | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| US | Building Permits MoM | +5.0% | −2.6% | Jul/26 | >0.5% | **GOOD** |
| US | Retail Sales YoY | 5.0% | 6.8% | Jul/26 | >0.5% | **GOOD** (decelerating) |
| US | CB Consumer Confidence | 51.0 | 55.2 | Aug/26 | >Prev | **BAD** |
| US | Personal Spending MoM | 0.3% | 0.9% | Jun/26 | 0–0.5% | NEUTRAL |
| EA | Retail Sales YoY | 0.7% | 1.9% | Jun/26 | >0.5% | **GOOD** (decelerating) |
| EA | Consumer Confidence | −15.9 | −17.6 | Jul/26 | >Prev | **GOOD** |
| CA | Retail Sales YoY | 5.9% | 3.6% | May/26 | >0.5% | **GOOD** |
| CA | Building Permits MoM | +18.5% | −3.0% | Jun/26 | >0.5% | **GOOD** |
| AU | Household Spending YoY | 6.0% | — | Jun/26 | >0.5% | **GOOD** |
| AU | Building Permits YoY | 8.9% | 5.5% | Jun/26 | >0.5% | **GOOD** |
| AU | Westpac Consumer Conf | 88.9 | 83.9 | Aug/26 | >Prev | **GOOD** |
| AU | NAB Business Confidence | −6 | −6 | Jul/26 | >Prev | NEUTRAL |
| NZ | Building Permits MoM | −3.6% | −4.9% | Jun/26 | <0% | **BAD** |
| NZ | Electronic Retail Card Spending | 0.9% | 0.9% | Q1/26 | >0.5% | **GOOD** |
| NZ | ANZ Business Confidence | 56.1 | 36.6 | Jul/26 | >Prev | **GOOD** |
| NZ | ANZ Roy Morgan Consumer Conf | 99.3 | 91.3 | Jul/26 | >Prev | **GOOD** |
| JP | Household Spending YoY | −3.3% | −0.4% | Jun/26 | <0% | **BAD** |
| JP | Consumer Confidence | 34.9 | 33.8 | Jul/26 | >Prev | **GOOD** |
| JP | Retail Sales YoY | 0.5% | 5.0% | Jun/26 | 0–0.5% | NEUTRAL (sharp drop) |
| GB | GfK Consumer Confidence | −17 | −23 | Jul/26 | >Prev | **GOOD** |
| GB | Retail Sales YoY | 4.2% | 3.5% | Jun/26 | >0.5% | **GOOD** |
| CH | Consumer Confidence | −35 | −36 | Jul/26 | >Prev | **GOOD** |
| CH | Retail Sales YoY | 1.5% | 3.4% | Jun/26 | >0.5% | **GOOD** (decelerating) |

**Read:** CAD spending is the strongest on the board — Retail Sales 5.9%
and Building Permits +18.5%. US is split: permits and retail strong, but
**CB Consumer Confidence dropped to 51.0 from 55.2**, the clearest
forward-looking warning in this category. JP Retail Sales collapsed from
5.0% to 0.5%.

**All named Spending indicators are present** (r4 wrongly listed six of
these as unavailable — see C-8). Two stand out: **NZ ANZ Business
Confidence surged 36.6 → 56.1**, the strongest since February, and
**JP Household Spending fell −3.3% YoY**, its seventh straight month of
contraction and the sharpest of the run.

### 2.3 TRADE

| Ccy | Indicator | Actual | Prev | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| US | Balance of Trade | −$73.26B | −$77.65B | Jun/26 | >Prev | **GOOD** |
| EA | Balance of Trade | €8,600M | €−9,000M | Jun/26 | >Prev | **GOOD** |
| CA | Balance of Trade | C$3,860M | C$3,700M | Jun/26 | >Prev | **GOOD** |
| AU | Balance of Trade | A$1,929M | A$−2,367M | Jun/26 | >Prev | **GOOD** |
| NZ | Balance of Trade | NZ$23M | NZ$577M | Jun/26 | <Prev | **BAD** |
| JP | Balance of Trade | ¥−407B | ¥−392B | Jun/26 | <Prev | **BAD** |
| GB | Balance of Trade | £−5,537M | £−3,464M | Jun/26 | <Prev | **BAD** |
| CH | Balance of Trade | CHF3,800M | CHF5,530M | Jun/26 | <Prev | **BAD** |

**Read:** A clean 4–4 split. **EA swung from −€9.0B to +€8.6B** — the
largest single improvement in this category. AU also flipped positive.
GB's deficit widened sharply; NZ's surplus nearly vanished (NZ$577M →
NZ$23M).

### 2.4 EMPLOYMENT

| Ccy | Indicator | Actual | Prev | Ref | Threshold | Score |
|---|---|---|---|---|---|---|
| US | Non Farm Payrolls | **−23K** | 20K | Jul/26 | >Consensus | **BAD** |
| US | Unemployment Rate | 4.1% | 4.2% | Jul/26 | <Prev | **GOOD** |
| EA | Unemployment Rate | 6.3% | 6.3% | Jun/26 | unchanged | NEUTRAL |
| CA | Unemployment Rate | 6.4% | 6.5% | Jul/26 | <Prev | **GOOD** |
| CA | Full Time Employment Chg | 38.6K | 0.6K | Jul/26 | >Prev | **GOOD** |
| CA | Part Time Employment Chg | 36.6K | 17.5K | Jul/26 | <Prev | **BAD** |
| AU | ANZ-Indeed Job Ads MoM | +0.8% | −0.1% | Jul/26 | >0.5% | **GOOD** |
| AU | Unemployment Rate | 4.4% | 4.4% | Jun/26 | unchanged | NEUTRAL |
| NZ | Unemployment Rate | 5.6% | 5.4% | Jun/26 | >Prev | **BAD** |
| JP | Unemployment Rate | 2.5% | 2.5% | Jun/26 | unchanged | NEUTRAL |
| GB | Claimant Count Change | **−11K** | −6.4K | Jul/26 | <Prev | **GOOD** |
| CH | Unemployment Rate | 3.0% | 2.9% | Jul/26 | >Prev | **BAD** |

**Read:** **US NFP at −23K is the worst print on the entire board** — the
first negative headline this cycle, against a 20K prior. Unemployment
falling to 4.1% is a participation effect, not strength. **CAD employment
is the mirror image**: Full Time +38.6K from +0.6K, which your framework
weights heavier than part-time by design.

**AU Employment Change is NOT in this table.** TE displays 76.3K, but the
July print releases **Thu 20 Aug 09:30 PHT** — the latest *released* AU
employment is Jun/26. See §0.

### 2.5 INFLATION

| Ccy | Indicator | Actual | Prev | Ref | Rule | Score |
|---|---|---|---|---|---|---|
| GB | Inflation Rate YoY | **2.9%** | 2.6% | Jul/26 | >2% & rising | **HIKE-LEANING** |
| EA | Inflation Rate YoY | 2.9% | 2.8% | Jul/26 | >2% & rising | **HIKE-LEANING** |
| CA | Inflation Rate YoY | 3.0% | 2.8% | Jul/26 | >2% & rising | **HIKE-LEANING** |
| NZ | Inflation Rate YoY | **4.1%** | 3.1% | Jun/26 | >2% & rising | **HIKE-LEANING** |
| US | Inflation Rate YoY | 3.4% | 3.5% | Jul/26 | >2% & falling | NEUTRAL (hold) |
| AU | Inflation Rate YoY | 3.8% | 4.0% | Jun/26 | >2% & falling | NEUTRAL (hold) |
| JP | Inflation Rate YoY | 1.7% | 1.5% | Jun/26 | <2% & rising | NEUTRAL (hold) |
| CH | Inflation Rate YoY | 0.4% | 0.5% | Jul/26 | <2% & falling | **CUT-LEANING** |

**Read — the decisive category.** Four currencies are hike-leaning under
your rule. **NZ is the most extreme: 4.1% from 3.1%, a full point jump**,
and the RBNZ already hiked in July. GB, EA and CA are all rising above
target. **CHF is the only cut-leaning currency at 0.4% and falling** —
which, against a 0.00% policy rate, means the SNB has nowhere to go.

> **CORRECTION TO r2 (C-6).** r2 reported EA inflation *falling* to 2.8%
> from 2.9% off the "Inflation Rate YoY Final JUL" calendar row. The EA
> country-page series shows **2.9% from 2.8% — rising**. EA is
> **hike-leaning, not cooling**, which inverts r2's GBP/EUR divergence
> call. Root cause: the calendar row was read without cross-checking the
> series page.

### Model tally — all whitelist indicators (net = GOOD − BAD)

| Ccy | GOOD | BAD | NEUTRAL | Net | vs r4 |
|---|---|---|---|---|---|
| **AUD** | 6 | **0** | 3 | **+6** | **+3 → +6** |
| **CAD** | 7 | 1 | 0 | **+6** | unchanged |
| **USD** | 7 | 2 | 2 | **+5** | unchanged |
| **EUR** | 5 | **0** | 2 | **+5** | unchanged |
| **GBP** | 5 | 2 | 1 | **+3** | unchanged |
| **JPY** | 5 | 2 | 3 | **+3** | +2 → +3 |
| **NZD** | 6 | 3 | 0 | **+3** | +1 → +3 |
| **CHF** | 3 | 4 | 0 | **−1** | unchanged |

**Three currencies moved** once the missing rows landed (C-8). **AUD is the
big one: +3 → +6, now tied with CAD at the top and one of only two
currencies with ZERO bad scores.** The three rows that did it — Household
Spending +6.0%, Westpac Consumer Confidence 88.9 from 83.9, ANZ-Indeed Job
Ads +0.8% — were all published and all missed.

**The tally is the model's raw output, not the ranking.** §4 weights it
against policy direction (§3) and live news (§1) — USD scores +5 on the
model yet carries the worst single print on the board (NFP −23K) and a
cutting central bank, so it does not rank 2nd.

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

Derived from §2's whitelist model tally, weighted by §3 policy direction
and §1 news. Where the raw tally and the ranking differ, the reason is
stated — a model score is an input, not a verdict.

| # | Ccy | Model net | Lean | Driving evidence |
|---|---|---|---|---|
| **1** | **AUD** | **+6** | **Strong** | **Tied top of the model with ZERO bad scores.** Household Spending +6.0%, Building Permits +8.9%, Westpac Consumer Confidence 88.9 from 83.9, ANZ-Indeed Job Ads +0.8%, Balance of Trade flipped **−A$2.4B → +A$1.9B**, Mfg PMI 52.0. **Plus Hauser warned of a hike today**, naming Middle East / AI boom / productivity. Only drags: flat wages (3.2%) and China youth unemployment at 17.9%. |
| **2** | **CAD** | **+6** | **Strong** | Employment: Full Time **+38.6K from +0.6K**, unemployment 6.4% from 6.5%. Spending: Retail Sales 5.9%, Building Permits **+18.5%**. Inflation 3.0% from 2.8%, hike-leaning. Plus **oil's 4th straight up day** and the **50% tariff pause**. Ranked below AUD only on the one BAD score (part-time skew). |
| **3** | **EUR** | **+5** | **Strengthening** | The other **zero-BAD** currency. Balance of Trade swung **−€9.0B → +€8.6B**. Consumer Confidence −15.9 from −17.6. Inflation **2.9% from 2.8%, rising**. |
| **4** | **GBP** | **+3** | **Firm** | CPI **2.9% from 2.6%**, core 2.6% beating consensus — the strongest inflation acceleration among released prints. Claimant Count **−11K vs +11.2K expected**. Offset: Industrial Production −0.2%, trade deficit widened to £5.5B. |
| **5** | **NZD** | **+3** | **Firm but split** | Re-rated up from r4's +1. **ANZ Business Confidence surged 36.6 → 56.1**, strongest since February; Retail Card Spending +0.9%. **Inflation 4.1% from 3.1% is the largest jump on the board** and the RBNZ already hiked 25bp on 8 Jul. But 3 BAD scores remain: unemployment 5.6%, permits −3.6%, trade surplus nearly gone. |
| **6** | **JPY** | **+3** | **Mixed** | Production is exceptional — Industrial Production **+4.9%**, Machinery Orders **+16.9%**, **Machine Tool Orders +50.4%** (two months >+50%), PMI Final 54.5 on seven straight expansion months. **But the consumer is contracting**: Household Spending **−3.3% YoY**, seventh straight decline and the sharpest; Retail Sales collapsed 5.0% → 0.5%. Inflation 1.7% still below target. Factory strong, household weak. |
| **7** | **USD** | **+5** | **Weak — model overstates it** | **The tally says +5; the ranking says 7th, and the gap is the point.** The model counts breadth, not severity: **NFP −23K is the first negative headline print this cycle**, and CB Consumer Confidence fell to 51.0 from 55.2. Inflation is *falling* (3.4% from 3.5%) with the Fed at 3.50–3.75% and a cut bias. |
| **8** | **CHF** | **−1** | **Weakest** | Only negative model score. Inflation **0.4% and falling — the only cut-leaning currency**, against a policy rate already at **0.00%**, so the SNB has no room. Unemployment rose to 3.0%, trade surplus shrank CHF5.5B → CHF3.8B. procure.ch–UBS PMI 53.2, down from 54.3 and the weakest since February. |

**Model-vs-ranking disagreement (the line worth reading twice):** USD
scores **+5** on breadth yet ranks **7th**. A tally counts how many
indicators are good; it cannot see that one of them (NFP) is a
regime-defining print while three others are second-tier production
readings. This is exactly why the ranking is not the tally.

### 1. AUD/CHF — top vs bottom of the model

- **Alignment:** AUD #1 (**+6, zero BAD scores**, broad-based across
  spending, employment and trade) against CHF #8 (**−1**, the only
  cut-leaning currency, at a 0.00% floor with no room). Plus Hauser
  explicitly flagging hike risk today against an SNB that cannot cut.
- **Conviction:** **Highest on the fundamental spread.**
- **⚠ EVENT-GATED:** **AU Employment releases Thu 09:30 PHT.** See the AUD
  block below — TE is showing a phantom 76.3K. The alignment is sound on
  released data; the event is the risk, not the thesis.
- **Technical:** AUDCHF not read this run. **No levels published.**
- **Falsifier:** AU employment printing materially below the 15.0K
  consensus tomorrow, or a genuine haven bid returning to CHF.

### 2. CAD/CHF — same short leg, no event gate

- **Alignment:** CAD #2 (+6, strongest employment and spending, oil
  tailwind, tariff pause) against CHF #8. **Materially the same spread as
  #1 without tomorrow's event risk.**
- **Conviction:** **Highest of the ungated set** — every input is
  released data.
- **Technical:** CADCHF not read this run. **No levels published.**
- **Falsifier:** Hormuz de-escalation. Oil gives back the four-day gain and
  CAD's news leg is gone within a session — the model leg (+6) survives,
  but conviction drops to moderate.

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
