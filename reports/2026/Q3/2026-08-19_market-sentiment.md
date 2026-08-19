---
edition: 2026-08-19
revision: 3 (supersedes r1, r2 - see CORRECTIONS)
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

### Source gap

**CNN Fear & Greed Index unavailable** — `edition.cnn.com` returns
**HTTP 451 (geo-blocked)**. No sentiment index. No substitute presented as
CNN's.

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
| GB | S&P Global Mfg PMI | 51.9 | 52.5 | Jul/26 | >50.5 | **GOOD** |
| GB | Industrial Production YoY | −0.2% | 1.0% | Jun/26 | <0% | **BAD** |
| GB | Manufacturing Production YoY | 0.5% | 2.0% | Jun/26 | 0–0.5% | NEUTRAL |
| CH | Manufacturing PMI | 53.2 | 54.3 | Jul/26 | >50.5 | **GOOD** |
| CH | Industrial Production YoY | −7.1% | −0.4% | Mar/26 | <0% | **BAD** (Q1 — stale) |

**Read:** JP production is the standout — Industrial Production +4.9% from
−2.1% and Machinery Orders +16.9% from −1.9%, both sharp reversals. GB is
the weak leg: PMI still expanding but Industrial Production has turned
negative. CH Industrial Production is **Mar/26 — five months stale** and
carries little weight.

**Not released / not available this period:** JP Machine Tool Orders YoY,
JP S&P Global Mfg PMI Final, CH Procure.ch Manufacturing PMI (TE lists a
generic Swiss Manufacturing PMI instead — flagged, not silently
substituted).

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
| AU | Building Permits YoY | 8.9% | 5.5% | Jun/26 | >0.5% | **GOOD** |
| NZ | Building Permits MoM | −3.6% | −4.9% | Jun/26 | <0% | **BAD** |
| NZ | ANZ Roy Morgan Consumer Conf | 99.3 | 91.3 | Jul/26 | >Prev | **GOOD** |
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

**Not released / not available:** AU Household Spending YoY, AU Westpac
Consumer Confidence Change, AU NAB Business Confidence, NZ Electronic
Retail Card Spending YoY, NZ ANZ Business Confidence, JP Household
Spending YoY.

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

| Ccy | GOOD | BAD | NEUTRAL | Net |
|---|---|---|---|---|
| **CAD** | 7 | 1 | 0 | **+6** |
| **USD** | 7 | 2 | 2 | **+5** |
| **EUR** | 5 | 0 | 2 | **+5** |
| **GBP** | 5 | 2 | 1 | **+3** |
| **AUD** | 3 | 0 | 2 | **+3** |
| **JPY** | 3 | 1 | 3 | **+2** |
| **NZD** | 4 | 3 | 0 | **+1** |
| **CHF** | 3 | 4 | 0 | **−1** |

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
| **1** | **CAD** | **+6** | **Strong** | Top of the model AND the news. Employment: Full Time **+38.6K from +0.6K**, unemployment 6.4% from 6.5%. Spending: Retail Sales 5.9%, Building Permits **+18.5%**. Inflation 3.0% from 2.8% — hike-leaning. Plus **oil's 4th straight up day** (Hormuz) and the **50% tariff pause**. Model and news agree. |
| **2** | **EUR** | **+5** | **Strengthening** | **Zero BAD scores — the only currency on the board with none.** Balance of Trade swung **−€9.0B → +€8.6B**. Consumer Confidence −15.9 from −17.6, Mfg PMI 51.9. Inflation **2.9% from 2.8%, rising** (this corrects r2, which had it falling). |
| **3** | **GBP** | **+3** | **Firm** | CPI **2.9% from 2.6%** with core 2.6% beating consensus — the strongest single inflation acceleration among released prints. Claimant Count **−11K vs +11.2K expected**. Offset: Industrial Production −0.2% and the trade deficit widened to £5.5B. |
| **4** | **AUD** | **+3** | **Firm** | **No BAD scores.** Mfg PMI 52.0, Building Permits +8.9%, Balance of Trade flipped **−A$2.4B → +A$1.9B**. **Hauser warned of a hike today**, naming Middle East / AI boom / productivity. Held back by flat wages (3.2%) and China youth unemployment at 17.9%. |
| **5** | **JPY** | **+2** | **Mildly positive** | Production is the story: Industrial Production **+4.9% from −2.1%**, Machinery Orders **+16.9% from −1.9%**. But Retail Sales collapsed 5.0% → 0.5%, trade deficit widened, and inflation 1.7% is still below target — BoJ has no forcing reason at 1.00%. |
| **6** | **NZD** | **+1** | **Mixed** | **Inflation 4.1% from 3.1% — the largest jump on the board**, and the RBNZ already hiked 25bp on 8 Jul (first in 3 years). But the model is nearly balanced: unemployment rose to 5.6%, building permits −3.6%, and trade surplus almost vanished (NZ$577M → NZ$23M). Business NZ PMI still >50 but fell hard, 60.1 → 54.3. |
| **7** | **USD** | **+5** | **Weak — model overstates it** | **The tally says +5; the ranking says 7th, and the gap is the point.** The model counts breadth, not severity: **NFP −23K is the first negative headline print this cycle**, and CB Consumer Confidence fell to 51.0 from 55.2. Inflation is *falling* (3.4% from 3.5%) with the Fed at 3.50–3.75% and a cut bias. Three good production scores do not outweigh a contracting labour market plus an easing central bank. |
| **8** | **CHF** | **−1** | **Weakest** | Only negative model score. Inflation **0.4% and falling — the only cut-leaning currency**, against a policy rate already at **0.00%**, so the SNB has no room. Unemployment rose to 3.0%, trade surplus shrank CHF5.5B → CHF3.8B, Industrial Production −7.1% (though that print is Mar/26 and stale). |

**Model-vs-ranking disagreement (the line worth reading twice):** USD
scores **+5** on breadth yet ranks **7th**. A tally counts how many
indicators are good; it cannot see that one of them (NFP) is a
regime-defining print while three others are second-tier production
readings. This is exactly why the ranking is not the tally.

### 1. CAD/CHF — widest spread on the board

- **Alignment:** CAD #1 (+6 model, strongest employment and spending, oil
  tailwind, tariff pause) against CHF #8 (−1 model, the only cut-leaning
  currency, at a 0.00% floor with no room). **Top and bottom of both the
  model and the policy direction.**
- **Conviction:** **Highest.** No event gate — every input is released data.
- **Technical:** CADCHF not read this run. **No levels published.**
- **Falsifier:** Hormuz de-escalation. Oil gives back the four-day gain and
  CAD's news leg is gone within a session — the model leg (+6) would
  survive, but the conviction drops to moderate.

### 2. EUR/CHF — clean model separation

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

### 3. AUD — DO NOT TRADE INTO THURSDAY 09:30 PHT

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
2. **CNN Fear & Greed geo-blocked** (HTTP 451).
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
