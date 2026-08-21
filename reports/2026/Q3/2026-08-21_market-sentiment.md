---
edition: 2026-08-21
revision: 13 (SEALED FULL; T4 RESOLVED - three causal readings corrected, figures unchanged)
generated: 2026-08-21 07:00 PHT
data_asof: 2026-08-21 16:40 PHT (macro 06:50 + 16:37; charts 16:40)
horizon: WEEKLY selection (Fri - last edition of the week, Mon 17 - Fri 21)
seal: SEALED (FULL) - Jeff, 2026-08-21; T4 amendments (F-15); T4 RESOLVED (F-17)
seal_tier: FULL (LD-12: Friday, last edition of the week Mon 17 - Fri 21 Aug)
artifact_url: https://claude.ai/code/artifact/eee6e597-8644-4c5d-b69b-db6879803abc
prior_edition: 2026-08-20 (r11, UNSEALED)
---

# Daily Market Sentiment — Friday 21 August 2026

> ## ✅ T4 RESOLVED — three causal readings corrected (F-17)
>
> **The 19 Aug US Treasury buyback announcement was missing from this edition.**
> §1's two mandated news sources had never been fetched. **Three conclusions
> sealed as "cause not identified" now have their cause** — see **§0c**.
>
> **Every figure stands. EF-1, EF-3, EF-4, EF-5 stand. EF-2's observation
> stands** — only its absent mechanism is now supplied, which is precisely why
> it was sealed as an observation.
>
> Corrected: **EF-2** (the USD leg was primary, not CHF) · **§5 Gold** (yields
> *fell* on 19 Aug — wrong premise) · **§6 BTC** (not decoupled — the same
> buyback liquidity as gold). **Original text is preserved below each
> correction**, per the FAIL protocol.

> ## ⚠ T4 — SEALED EDITION AMENDED
>
> **This edition was sealed FULL at 16:45 PHT. It was amended at 16:55 PHT
> because §1 was missing its Market-structure block entirely** — CNN Fear &
> Greed, which the spec (§2.3) makes mandatory and which both prior editions
> carried. **Jeff caught it, not me.**
>
> **What was wrong:** when §1 was rebuilt this morning I wrote the new US data,
> carried the central-bank items, and simply did not write the market-structure
> subsection. It degraded across three editions — **9 mentions on 08-19, 1 on
> 08-20, 0 here.**
>
> **What changed:** §1 now **opens** with the block, in the r9 (2026-08-19)
> format Jeff preferred — horizon table with deltas, per-component PHT
> timestamps, and a falsifier. Pulled fresh at 16:41 PHT. **No score, no band,
> no carried pair, no trade falsifier changed** — F&G is context, not a scored
> input.
>
> **The seal stands.** Per CLAUDE.md §2 this is a T4 revision to a sealed
> edition, so it is disclosed here rather than silently patched, and the
> omission is recorded as **F-15**.

**All times Philippine Standard Time (UTC+8).**
**TE calendar is UTC → PHT = UTC + 8h — re-verified this run.**

---

## Pre-flight — both guards run, plus the new span assertion

| Guard | Result |
|---|---|
| **Timezone (F-2)** | **PASS.** Anchor: US initial jobless claims, released 08:30 ET = **12:30 UTC**; TE row showed `12:30 PM`; +8h = **20:30 PHT**, which is when it landed. |
| **Span assertion (F-13, new)** | **PASS.** Dated endpoint `?dates=2026-08-17/2026-08-21` returned **541 rows spanning 17–30 Aug** — covers the Mon–Fri window with room. *(Yesterday's undated URL started at Wed 19 and silently dropped Mon–Tue.)* |
| **Phantom-Actual (F-1)** | **NULL, not a pass.** 315 whitelist-currency rows, **0 carry any Actual value** — values load by XHR, so the guard could not fire. Same as yesterday. Values taken from series pages instead. |

---

## §0 — YESTERDAY GRADED

**This is the first edition to grade its own prior call. Both results are
reported, including the one that went against the method.**

### The carried trades: 4 of 4 worked

Thursday's daily bar has **closed**. Wed close → Thu close:

| Pair | Dir | Wed close | **Thu close** | Move | Result |
|---|---|---|---|---|---|
| CADJPY | LONG | 114.544 | **115.366** | **+82.2 pips** (+0.72%) | ✅ |
| EURJPY | LONG | 184.688 | **185.768** | **+108.0 pips** (+0.58%) | ✅ |
| GBPJPY | LONG | 215.192 | **216.823** | **+163.1 pips** (+0.76%) | ✅ |
| AUDCAD | SHORT | 0.98369 | **0.98081** | **−28.8 pips** (−0.29%) | ✅ |

**All three JPY longs broke above the resistance zones published yesterday.**
CADJPY cleared 114.992–115.203 and closed 16.3 pips above it; GBPJPY cleared
215.890–216.222. Those zones are now **support, not resistance**.

#### ⚠ CORRECTION TO THE SCORECARD: "4 of 4" overstates the evidence

**Three of the four carried pairs shared the JPY leg.** They are not three
tests of the model — they are **one currency call expressed three times**, and
the returns prove it: **+0.72%, +0.76%, +0.58% — a 0.18pp spread.** They moved
as a single position. Had JPY strengthened instead, all three would have lost
together.

A fourth overlap I also missed: **AUDCAD short is long CAD**, and CADJPY long
is *also* long CAD — **CAD sat on the long side twice.**

| What the scorecard said | What was actually tested |
|---|---|
| 4 trades, 4 worked | **2 independent bets** — "JPY weak" and "AUD weak vs CAD" |
| | Under the corrected selection rule (below): **1 bet** |

**The method looked 4× better than the evidence supports.** Fixed for every
future edition by **LD-19 (leg-disjoint selection)**, applied in §4.3 below.
Recorded here rather than quietly corrected, because the inflated scorecard is
what a reader would otherwise carry forward.

### The rejected CHF trades: both would have worked

| Pair | Dir rejected | Wed close | Thu close | Move | |
|---|---|---|---|---|---|
| CADCHF | LONG | 0.57747 | 0.58056 | **+30.9 pips** | ❌ **the reject cost a gain** |
| USDCHF | LONG | 0.79725 | 0.80048 | **+32.3 pips** | ❌ **same** |

**The structure filter was wrong on these two, and the honest reading is that
it was wrong for a defensible reason.** CADCHF had broken down through an
8-touch resistance zone with nothing beneath it; the filter rejected a trade
whose chart had just failed. It reversed the next day. **One day is not a
verdict on the filter** — but it is recorded rather than buried, and if the
pattern repeats the filter needs re-examining, not defending.

### The CHF bid is fading — the anomaly is resolving

19 Aug: CHF gained ~1.35% against a five-cross basket.
20 Aug: **CADCHF +30.9 pips, USDCHF +32.3 pips** — CHF gave ground back.
**CADCHF has recovered 42.9% of the 19 Aug drop** (`0.00309 / 0.00720`).

**CORRECTED (T4/F-17): the explanation is the 19 Aug Treasury buyback.** The
dollar fell 0.8% on the announcement and later hit a three-month low; CHF and
gold both rallied **against a falling dollar**. The USD leg was primary, not a
CHF-specific bid. *Source: investing.com, "Dollar hits three-month low as
Treasury buybacks sink yields"; Treasury sb0607.*

~~*"The read that CHF was bid for an unexplained reason still has no
explanation"*~~ — **retained per the FAIL protocol.** It was sealed as an
observation without a mechanism, and the mechanism was published the same day.

No CHF release lands this week, so the −3.00 score cannot correct — but that
is no longer the interesting part. **The resolution came from the dollar side.**

---

## §0b — AFTERNOON UPDATE, 16:40 PHT

**This edition was built at 06:55 PHT. Ten hours have passed and three Friday
releases have landed.** Re-run rather than left stale.

### The week's projections are now fully graded

| CCY | Indicator | Expected | Projected | **Actual** | Scored | Grade |
|---|---|---|---|---|---|---|
| GBP | GfK Consumer Confidence | −18 | **BAD** | **−14** | GOOD | ❌ **WRONG** |
| JPY | Inflation Rate YoY | 1.7% | NEUTRAL | **1.9%** | NEUTRAL | ✅ |
| GBP | Retail Sales YoY | 2.2–3.7 | **GOOD** | **1.6%** | GOOD | ✅ *(but missed the range low by 0.6pp)* |

**WEEK TOTAL: 10 correct, 3 wrong — 77% on 13 graded.**

### The error is one-directional, and now it is a pattern

**All three misses were BAD projections that printed GOOD.** Never once the
reverse:

| Miss | Type |
|---|---|
| AUD Westpac Consumer Confidence | survey |
| GBP Claimant Count Change | survey-adjacent |
| GBP GfK Consumer Confidence | survey |

**3 of 3 misses are sentiment/survey indicators, not hard data.** The method is
systematically **pessimistic on surveys** — it takes the consensus at face value
where surveys have been beating. Three instances is not proof, but it is no
longer noise. **Carried as a finding about the method, not a correction to it**
— the fix is to keep grading, not to add a fudge factor now.

### Score impact: JP inflation moved, the tally did not

**JP Inflation Rate YoY: 1.7% → 1.9%** (Jun → Jul, released 07:30 PHT).
It stays **NEUTRAL** — 1.9% is still below the BoJ's 2% floor while rising —
so neither the Inflation category nor the rate leg changes.

**Worth watching: 1.9% is 0.1pp from target.** The next print could flip JPY's
rate leg from 0.00 to +0.25 and lift JPY off the floor of the board.

**Tally unchanged: CAD +8.38 · EUR +6.25 · GBP +5.75 · NZD +3.75 · USD +2.25 ·
AUD +2.08 · JPY +0.00 · CHF −3.38.**

### Carried pairs — all three intact, none near a falsifier

Friday's daily bar is **still forming** (closes 05:00 PHT Saturday).

| Pair | Thu close | Fri 16:40 | Fri high | vs Thu | Falsifier | Status |
|---|---|---|---|---|---|---|
| **CADJPY** | 115.366 | 115.347 | **115.579** *(new high)* | −1.9 pips | close below 114.992 | **INTACT** |
| **EURCHF** | 0.93479 | **0.93567** | **0.93614** *(highest since the 19 Aug break)* | **+8.8 pips** | close below 0.93071 | **INTACT** |
| **GBPUSD** | 1.36308 | **1.36507** | 1.36556 | **+19.9 pips** | close below 1.35197 | **INTACT** |

**None is within reach of its falsifier.** CADJPY printed a new high then eased
back — flat on the day, not weak.

### ⚠ F-14 — THE TE CALENDAR WINDOW ROLLS, AND MONDAY IS ALREADY GONE

**The F-13 span assertion FIRED on this run — correctly.**

| Fetch | Rows | Span |
|---|---|---|
| 06:50 PHT | 541 | **2026-08-17** → 2026-08-30 |
| 16:37 PHT | 532 | **2026-08-18** → 2026-08-31 |

**Monday 17 Aug: 47 rows this morning, 0 rows now.** The endpoint serves a
rolling ~14-day window from *today* and **ignores the `dates` start parameter**
— requesting `2026-08-15/2026-08-21` returned the same 18–31 Aug window.

**Consequence: the week-ahead table cannot be rebuilt from the calendar after
the fact.** Monday's CAD inflation print survives in this edition only because
it was captured at 06:50. **The morning capture is the sole record.**

**This is why the span assertion exists.** Without it the table would have
silently re-published with Monday missing — exactly the F-13 failure, one day
later, from a different cause. Logged as **F-14**: calendar captures must be
**persisted per edition**, because the source does not keep them.

## §0c — T4 RESOLVED: the missing news, and what it corrects

**Raised at wrap 2026-08-21, resolved 20:25 PHT. Three causal readings in this
sealed edition were wrong. The figures were not.**

### What was missing

**US Treasury, press release `sb0607`, 19 August 2026** *(primary —
home.treasury.gov, captured to `data/raw/news/`)*:

> "The U.S. Department of the Treasury is **increasing, by at least double, the
> size of liquidity support buyback operations** for longer-dated nominal coupon
> securities (the 10-year to 20-year sector and the 20-year to 30-year sector).
> The current maximum size of **$2 billion per operation will be at least $4
> billion per operation.** This change is effective **September 9, 2026** and
> will be in effect for the remainder of this refunding quarter (through
> **November 4, 2026**)."

Treasury's stated reason: *"greater liquidity support in longer-dated nominal
sectors where there is consistent strong sponsorship."* Context the feeds add:
it followed the **30-year yield hitting a 19-year high**, and was **unscheduled**
— two weeks after the quarter's buyback schedule had already been published.

**Market reaction on the 19 Aug bar:** 10y **−5bp to 4.647%**, 30y **−9bp to
5.196%**, **dollar −0.8%** against a basket, later **a three-month low**.

### The three corrections

| # | Sealed text | Correction | Evidence |
|---|---|---|---|
| **1** | **EF-2:** "a **CHF-specific** bid plus broad USD weakness… cause unidentified" | **The USD leg was primary, not the CHF leg.** An unscheduled USD-negative shock; CHF and gold both rallied *against a falling dollar* | *"Dollar hits three-month low as Treasury buybacks sink yields"* — investing.com |
| **2** | **§5 Gold:** "real yields rose 25–30bp… **Gold rose anyway — that is the signal**" | **Wrong premise.** Those 25–30bp were the FOMC *intermeeting* move. **On 19 Aug yields FELL.** Gold rose *with* falling yields on a debasement trade | *"Gold's oversized reaction to Treasury buyback reflects debasement trade"* — investinglive.com |
| **3** | **§6 BTC:** "**DECOUPLED** — and now decisively… cause not established" | **Not decoupled.** The same buyback liquidity that lifted gold | *"Why gold and Bitcoin surged together: What Treasury buybacks teach investors about dollar debasement"* — investinglive.com |

**A fourth item the news adds, not previously flagged:** *"Canadian dollar rises
to new highs after Trump's tariff TACO, US Treasury announcement"* and *"Canadian
dollar hits near three-month high."* **CAD's strength — the basis of the #1
carried trade — was partly a USD-side move**, not purely the +8.38 fundamental
score. That does not void CADJPY (a JPY cross, no USD leg), but it means the
CAD read was better sourced than the report showed.

### What does NOT change

**Every figure in this edition stands.** All prices, pips, scores, bands,
zones, touch counts and falsifiers were independently sourced and recomputed;
none depended on the missing news. **EF-1, EF-3, EF-4 and EF-5 stand unchanged.**

**EF-2's observation stands** — the arithmetic of the 19 Aug move is unaffected.
Only its *mechanism* is now identified, and EF-2 was deliberately sealed as an
observation **without** a mechanism. That distinction is what makes this a
correction to an interpretation rather than a retraction of a fact.

### Why it happened, and what changed as a result

§1's two mandated sources — `investinglive.com`, `investing.com` — **had never
been fetched in any edition.** §1 was built from TradingEconomics and
federalreserve.gov: **calendar and agency sources, which can only report what
was already scheduled.** An unscheduled announcement is invisible to them by
construction.

**Both return 200 with a browser User-Agent** — step 2 of the F-6 ladder.
Nothing more was ever needed.

**The rule that follows (LD-26): an unexplained price move is a research
trigger, not a finding.** All three readings were hedged, careful, and
well-reasoned — and the hedging substituted for looking. That reads as rigour,
which is worse than being plainly wrong. Recorded as **F-17**.

---

## §1 — Headline Alerts, News & Current Events

### 📊 Sentiment — CNN Fear &amp; Greed Index

<!--FNG-->

**Direction.** Down **11.83** from a week ago (greed → neutral) but still
**+8.77** above a month ago (fear). Drifting down through neutral.

**Falsifier.** Junk Bond Demand dropping below **~70** would confirm credit
repricing to match equity stress, turning this divergence into broad risk-off.
Stock Price Strength recovering above **50** would resolve it the other way.

*Source: `production.dataviz.cnn.io/index/fearandgreed/graphdata` — browser
headers + Referer. The article page returns HTTP 451 (geo-blocked) and the
endpoint returns 418 to a plain fetch. Capture persisted at
`data/raw/fng/2026-08-21_1641PHT.json`; the chart is generated from it by
`pipelines/fng_block.py`, so the figures cannot drift from the source.*

### Overnight US data — strong, and it matters for the USD read

| Release | Actual | Consensus | Previous | Read |
|---|---|---|---|---|
| **Philadelphia Fed Mfg Index** (Aug) | **47.4** | 25 | 41.4 | **Massive beat** — nearly double consensus |
| **Initial Jobless Claims** (Aug/15) | **206K** | 210K | 212K | Beat; claims falling |

*Source: TradingEconomics series pages, released Thu 20:30 PHT.*
**Neither is a whitelist indicator, so neither scores** (spec §2, closed set).
They inform the USD narrative only — and that narrative is now firmly
constructive: three hawkish FOMC dissents, a September hike fully priced, a
labour market not deteriorating, and regional manufacturing running hot.

**Consequence for the NZDUSD near-miss** (§4): USD's *fundamental score* is
unchanged at **+2.25** because none of this is on the whitelist. But **NZD rose
to +3.75** on the new rate leg, so the spread widened **+0.75 → +1.50** and
**now clears the 1.00 floor.** It qualifies on spread for the first time — on
NZD strength, not USD weakness. **The qualitative USD case strengthened while
its score did not move**, and that divergence is still worth watching.

### Central banks

**ECB Monetary Policy Meeting Accounts** were due 19:30 PHT Thursday. Not yet
retrieved this run — **flagged as an open item, not reported as absent.**

Carried from Thursday, unchanged: FOMC minutes 9–3 with three dissents **for a
hike** (Hammack, Kashkari, Logan); BoE Vote Hike 3/9; RBNZ hiked to 2.50%
8 Jul; **Jackson Hole 27–29 Aug**, now six days out.

> **STILL UNVERIFIED, carried:** the FOMC voting list names **Kevin Warsh** in
> the Chair's position with Powell voting as a member. Not confirmed against a
> second source. §3 names no Chair.

---

## §2 — Macro Economic Indicators

**All 70 whitelist indicators, published in full every edition** — including
the ones that did not move. A score you cannot see is a score you cannot check.

**No whitelist indicator released since yesterday's cut.** 26 whitelist-currency
events landed overnight — jobless claims, Philly Fed, Canadian PPI, auctions,
mortgage rates — and **not one is on the 70-name closed set**, so not one
scores. The tables below are therefore identical in value to r11's, and that is
the finding: *the scores did not move because nothing that scores was released.*

Generated by `pipelines/score_model.py`, recomputed this run — tables and tally
cannot drift apart.

### 2.0 Category tally — weighted (LD-13 + LD-23)

Weights: **Inflation 3 · Interest Rate 3 · Employment 2 · Production/Spending/Trade 1 each.**
Within a category a currency's N indicators split the weight evenly. GOOD `+w/N`,
BAD `−w/N`, NEUTRAL `0`. **Range +11.00 to −11.00** *(was ±8.00 before Interest
Rate became category 6 this edition).*

| CCY | TOTAL | Prod | Spend | Trade | Empl | Infl | **Rate** |
|---|---|---|---|---|---|---|---|
| **CAD** | **+8.38** | +1.00 | +1.00 | +1.00 | +2.00 | +3.00 | **+0.38** |
| **EUR** | **+6.25** | +0.50 | +1.00 | +1.00 | +0.00 | +3.00 | **+0.75** |
| **GBP** | **+5.75** | +0.00 | +1.00 | -1.00 | +2.00 | +3.00 | **+0.75** |
| **NZD** | **+3.75** | +1.00 | +0.50 | -1.00 | -2.00 | +3.00 | **+2.25** |
| **USD** | **+2.25** | +1.00 | +0.25 | +1.00 | +0.00 | +0.00 | **+0.00** |
| **AUD** | **+2.08** | +1.00 | +0.75 | +1.00 | -0.67 | +0.00 | **+0.00** |
| **JPY** | **+0.00** | +1.00 | +0.00 | -1.00 | +0.00 | +0.00 | **+0.00** |
| **CHF** | **-3.38** | +0.00 | +1.00 | -1.00 | +0.00 | -3.00 | **-0.38** |

**INTEREST RATE IS SCORED FROM THIS EDITION (LD-23).** It was defined as
category 6 in the Idea_dump — *"the core indicator which tells the strength of a
currency"* — but had never fed the tally. The causal chain the model draws
(Production/Spending/Trade → Employment/Inflation → **Interest Rate** → currency
strength) stopped one step short of its own conclusion.

**What changed:** **NZD +1.50 → +3.75, up two ranks** — the only currency
actively hiking, with inflation above its ceiling and rising. **USD and AUD each
drop one rank**, both because their inflation is above target but *falling*,
which is hold-leaning on the same test every currency faces.

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

### 2.6 Interest Rate (weight 3) — NEW, category 6

**Score = (realised + expected) / 2 × 3.** *Realised* is the Idea_dump rule on the last decision (hiked +1.0, held 0.0, cut −1.0). *Expected* is **inflation versus the bank's own mandate** — and nothing else.

| CCY | Rate | Last decision | CPI | Own mandate | vs mandate | Realised | Expected | **Score** |
|---|---|---|---|---|---|---|---|---|
| **NZD** | 2.50% | **HIKED +25bp 8 Jul** | 4.1% | 1–3% | above 1-3% ceiling and RISING | +1.0 | +0.50 | **+2.25** |
| **EUR** | 2.40% | HELD 23 Jul | 2.9% | 2% point | above 2% point ceiling and RISING | +0.0 | +0.50 | **+0.75** |
| **GBP** | 3.75% | HELD 30 Jul | 2.9% | 2% point | above 2% point ceiling and RISING | +0.0 | +0.50 | **+0.75** |
| **CAD** | 2.25% | HELD 15 Jul | 3.0% | 1–3% | inside 1-3%, rising | +0.0 | +0.25 | **+0.38** |
| **USD** | 3.50-3.75% | HELD 29 Jul (9–3) | 3.4% | 2% point | above 2% point ceiling but falling | +0.0 | +0.00 | **+0.00** |
| **JPY** | 1.00% | HELD 31 Jul | 1.7% | 2% point | below 2% point floor but rising | +0.0 | +0.00 | **+0.00** |
| **AUD** | 4.35% | HELD 11 Aug | 3.8% | 2–3% | above 2-3% ceiling but falling | +0.0 | +0.00 | **+0.00** |
| **CHF** | 0.00% | HELD 18 Jun | 0.4% | 0–2% | inside 0-2%, falling | +0.0 | -0.25 | **-0.38** |

---

## §3 — Interest Rates

Ordered by policy pressure, not alphabetically. **Source order:** the central
bank's own site where the value is machine-readable, TradingEconomics as a
labelled fallback. **No policy decision has occurred since r11** — the values
below are unchanged, and are republished in full so the rate picture can be
read without opening a prior edition.

| CCY / Rate | Last decision | Bias | Next meeting (PHT) | Expectation |
|---|---|---|---|---|
| **USD 3.50–3.75%** | HELD 29 Jul, **9–3** — Hammack, Kashkari, Logan dissent for **+25bp** *(federalreserve.gov, primary)* | **HIKE RISK** | **15–16 Sep** | The minutes are the story: three hawkish dissents, market **fully priced for +25bp by September**, against a Desk survey seeing **no move until a 2028 cut**. Thursday's data reinforced it — Philly Fed **47.4** vs 25, claims **206K** vs 210K. **Jackson Hole 27–29 Aug** is the next signal. |
| **NZD 2.50%** | **HIKED +25bp** 8 Jul *(TE)* | **TIGHTENING** | **2 Sep** | The only currency in an active hiking cycle. TE forecasts **2.75%**. Inflation 4.1% and rising does the work; employment (−2.00) is the counterweight. |
| **GBP 3.75%** | HELD 30 Jul, **Vote Hike 3/9** (was 2/9), Vote Cut 0/9 *(TE — bankofengland.co.uk rate table is JS-rendered)* | **SPLIT** | **17 Sep** | Hawkish drift in the vote with CPI at 2.9% and rising. **No cut votes at all.** |
| **EUR 2.40%** | HELD 23 Jul *(TE)* | **CPI DECIDES** | **10 Sep** | Inflation finalised **2.9%**, above target and rising. **Meeting Accounts released Thu 19:30 PHT — not yet retrieved this run** (§9 open item). |
| **CAD 2.25%** | HELD 15 Jul *(bankofcanada.ca, primary)* | **FLOORED** | **2 Sep** | Held at 2.25% since April. A perfect **+8.00** fundamental score against the lowest policy rate in the G10 ex-JPY/CHF — the divergence is the interesting part. |
| **AUD 4.35%** | HELD 11 Aug *(TE)* | **CPI DECIDES** | **29 Sep** | Highest policy rate in the set. Inflation 3.8% and **falling** caps hike risk, and **employment just deteriorated** (−15.8K, unemployment 4.5%). **AU inflation Wed 26 Aug** is the weight-3 category, currently 0.00. |
| **JPY 1.00%** | HELD 31 Jul; prior hike to 1% on 16 Jun *(TE)* | **REPRICING** | **18 Sep** | Out of ZIRP and hiking, but inflation 1.7% is still below target and **the trade deficit just doubled** to ¥−634.5B. |
| **CHF 0.00%** | HELD 18 Jun *(TE)* | **TRAPPED** | **24 Sep** | At zero with inflation **0.4% and falling** — the only deflation-leaning currency. −3.00, weakest in the set, **and no CHF release lands this week**, so the score cannot correct. |

**Market-implied odds.** The only sourced instrument-and-date figure remains the
FOMC's own record: markets priced ~**1-in-3** for a July hike and were **fully
priced for +25bp by September** *(Desk manager's report, 28–29 Jul meeting)*.
**Every other currency is deliberately shown without odds** rather than given a
guessed number.

---

## §4 — Conviction Playbook — week of Mon 17 – Fri 21 Aug

### 4.0 — Week ahead: the week's projections, now nearly fully graded

**Friday is the last session of this week**, so the table below closes out
Mon–Fri. Projections are forecasts of a score, never scores.

| When (PHT) | CCY | Indicator | Previous | Expected | Projected | Actual | Scored |
|---|---|---|---|---|---|---|---|
| Mon 17 12:30 | JPY | Industrial Production YoY Final | −2.1% | 4.2% | GOOD | 4.9% | GOOD ✓ |
| Mon 17 20:30 | CAD | Inflation Rate YoY | 2.8% | 2.9% | GOOD | 3.0% | GOOD ✓ |
| Tue 18 08:30 | AUD | Westpac Consumer Conf Change | 83.9 | 81.7 | BAD | 88.9 | **GOOD ✗** |
| Tue 18 14:00 | GBP | Claimant Count Change | −6.4K | 9.0–11.2K | BAD | −11K | **GOOD ✗** |
| Tue 18 21:15 | USD | Industrial Production YoY | 1.29% | 1.0% | GOOD | 1.1% | GOOD ✓ |
| Wed 19 07:50 | JPY | Machinery Orders YoY | −1.9% | 7.8–9.5% | GOOD | 16.9% | GOOD ✓ |
| Wed 19 14:00 | GBP | Inflation Rate YoY | 2.6% | 2.8–2.9% | GOOD | 2.9% | GOOD ✓ |
| Wed 19 17:00 | EUR | Inflation Rate YoY Final | 2.8% | 2.9% | GOOD | 2.9% | GOOD ✓ |
| Thu 20 07:50 | JPY | Balance of Trade | ¥−409.9B | −680 to −500B | BAD | ¥−634.5B | BAD ✓ |
| **Thu 20 09:30** | **AUD** | **Employment Change** | 76.3K | 15K | **BAD** | **−15.8K** | **BAD ✓** |
| **Thu 20 09:30** | **AUD** | **Unemployment Rate** | 4.4% | 4.4–4.5 | **SPLIT** | **4.5%** | **BAD ✓** |
| Thu 20 09:30 | AUD | Full Time Employment Chg | 29.3K | *none* | UNSCORED | +16.3K | BAD |
| Fri 21 07:00 | AUD | S&P Global Mfg PMI Flash | 52.0 | *none* | UNSCORED | *awaiting TE* | — |
| Fri 21 07:01 | GBP | GfK Consumer Confidence | −17 | −18 | **BAD** | *awaiting TE* | — |
| Fri 21 07:30 | JPY | Inflation Rate YoY | 1.7% | 1.7% | NEUTRAL | *awaiting TE* | — |
| Fri 21 14:00 | GBP | Retail Sales YoY | 4.2% | 2.2–3.7 | **GOOD** | *pending* | — |
| Fri 21 20:30 | CAD | Retail Sales YoY | 5.9% | 3.1% | **GOOD** | *pending* | — |
| Fri 21 22:00 | EUR | Consumer Confidence Flash | −15.9 | −16.7 to −16.3 | **BAD** | *pending* | — |

**Scorecard: 8 correct, 2 wrong.** Both misses were **BAD projections that
printed GOOD** — the method's error is one-directional so far (too
pessimistic), on a sample far too small to call a bias.

**Three Friday events released 07:00–07:30 PHT but TE has not posted values
yet.** Recorded as *awaiting*, not as missing — they will grade in the next
edition.

### 4.1 Currency bands

Cut on the **+11 / −11 scale** (widened this edition — Interest Rate is now
category 6). Cuts held proportional to the old ±8 scale:
**STRONG ≥ +5.50 · NEUTRAL +0.01 to +5.49 · WEAK ≤ 0.00**

| Band | CCY | Score | Group | Category detail (Prod · Spend · Trade · Empl · Infl · **Rate**) |
|---|---|---|---|---|
| **STRONG** | **CAD** | **+8.38** | Commodity | +1.00 · +1.00 · +1.00 · +2.00 · +3.00 · **+0.38** |
| **STRONG** | **EUR** | **+6.25** | Risk-corr | +0.50 · +1.00 · +1.00 · +0.00 · +3.00 · **+0.75** |
| **STRONG** | **GBP** | **+5.75** | Risk-corr | +0.00 · +1.00 · -1.00 · +2.00 · +3.00 · **+0.75** |
| NEUTRAL | NZD | +3.75 | Commodity | +1.00 · +0.50 · -1.00 · -2.00 · +3.00 · **+2.25** |
| NEUTRAL | USD | +2.25 | Safe haven | +1.00 · +0.25 · +1.00 · +0.00 · +0.00 · **+0.00** |
| NEUTRAL | AUD | +2.08 | Commodity | +1.00 · +0.75 · +1.00 · -0.67 · +0.00 · **+0.00** |
| **WEAK** | **JPY** | **+0.00** | Safe haven | +1.00 · +0.00 · -1.00 · +0.00 · +0.00 · **+0.00** |
| **WEAK** | **CHF** | **-3.38** | Safe haven | +0.00 · +1.00 · -1.00 · +0.00 · -3.00 · **-0.38** |

**Group standings** — Safe haven: USD +2.25 › JPY +0.00 › CHF −3.38 ·
Commodity: CAD +8.38 › NZD +3.75 › AUD +2.08 · Risk-correlated: EUR +6.25 › GBP +5.75

**NZD moved up two ranks this edition** on the new rate leg (+2.25 — the only
currency actively hiking, inflation above its 1–3% ceiling and rising). **AUD
and USD each dropped one**, both scoring 0.00 on rate: inflation above target
but *falling*, which is hold-leaning on the same test every currency faces.

### 4.2 All candidate pairings

Grouped by type, tradable first. Minimum spread **1.00**.
✅ carried · ⬜ no edge · ❌ rejected

| Pair | Dir | Type | Spread | Thu close | Structure verdict |
|---|---|---|---|---|---|
| **CADJPY** | LONG | **RISK-ON** | **8.38** | 115.366 | ✅ **broke resistance, closed +82.2 pips** |
| **GBPJPY** | LONG | **RISK-ON** | **5.75** | 216.823 | ✅ **broke resistance, closed +163.1 pips** |
| **EURJPY** | LONG | **RISK-ON** | **6.25** | 185.768 | ✅ **new highs, +108.0 pips** |
| **CADCHF** | LONG | RISK-ON | **11.76** | 0.58056 | ⚠️ **recovering — 42.9% of the 19 Aug drop retraced** |
| EURCHF | LONG | RISK-ON | 8.50 | — | ⬜ not re-read this run |
| GBPCHF | LONG | RISK-ON | 8.00 | — | ⬜ not re-read this run |
| **AUDCAD** | SHORT | **COMM** | **6.30** | 0.98081 | ✅ **closed −28.8 pips, still low in range** |
| NZDCAD | SHORT | COMM | 6.50 | — | ❌ 5-touch support held it Thursday |
| AUDNZD | LONG | COMM | 0.58 | — | ⬜ below the 1.00 floor |
| USDCHF | LONG | SAFE | 5.25 | 0.80048 | ⚠️ **bounced +32.3 pips off the 21-day low** |
| CHFJPY | SHORT | SAFE | 3.00 | — | ⬜ not re-read this run |
| USDJPY | LONG | SAFE | 2.25 | — | ⬜ not re-read this run |

**RISK-OFF: still nil.** The 3×3 haven-minus-commodity matrix is unchanged
because no whitelist score moved — not one cell reaches +1.00, and the binding
case was **USD +2.25 failing to clear NZD +1.50 by a full point (+0.75)**.
**THAT HAS NOW CHANGED** — see below. It did not close on the US data night,
precisely
because neither jobless claims nor Philly Fed is a whitelist indicator.

### 4.3 CARRIED — three leg-disjoint pairs, with confidence

**These are HIGH-PROBABILITY reads from fundamentals plus structure. They are
not guarantees and nothing here is a prediction.** Every one carries a
falsifier; if it fires, the read was wrong and that is the point of stating it.

**Selection:** spread floor 1.00 → structure filter → leg-disjoint (LD-19).
**Confidence (LD-20)** is a tally of independent supports, not a probability —
the arithmetic is shown so you can disagree with any line of it.

| Rank | Pair | Dir | Conf | Spread | Thu close | Thu move | Falsifier |
|---|---|---|---|---|---|---|---|
| **1** | **CADJPY** | LONG | **HIGH (+6)** | **8.38** | **115.366** | **+82.2 pips** | close below **114.992** |
| **2** | **EURCHF** | LONG | **MEDIUM (+3)** | **9.62** | **0.93479** | **+37.5 pips** | close below **0.93071** |
| **3** | **GBPUSD** | LONG | **LOW (+1)** | **3.50** | **1.36308** | **+27.5 pips** | close below **1.35197** |

**Net exposure: long CAD · EUR · GBP, short JPY · CHF · USD.** Six currencies,
each used once. **Three independent tests of the model** — if one fails while
another holds, that is information. Yesterday's four could not do that.

#### Why each one scores what it scores

| | **CADJPY — HIGH (+6)** | **EURCHF — MEDIUM (+3)** | **GBPUSD — LOW (+1)** |
|---|---|---|---|
| Spread | **+2** — 8.00 | **+2** — 8.50 | **0** — 2.75, thin |
| Structure | **+2** — broke a 4-touch zone and closed above it | **+1** — 72.7% of range | **+1** — 94.4% of range |
| Last bar | **+1** — +82.2 pips with the read | **+1** — +37.5 pips with the read | **+1** — +27.5 pips with the read |
| Fresh driver | **+1** — JP trade deficit doubled Thu | **+1** — EUR CPI finalised 2.9% rising | **+1** — GBP CPI 2.9% + 3/9 hike votes |
| Against | — | **−2** — **CHF leg; the model has been wrong on CHF all week** | **−1** score vs hot US data · **−1** thinnest spread |
| **Total** | **+6 HIGH** | **+3 MEDIUM** | **+1 LOW** |

#### Zones (LD-5 — observations of structure, never entry/stop/target roles)

| Pair | Support | Resistance | TV |
|---|---|---|---|
| CADJPY | 113.852–114.352 · 5 touches | *cleared 114.992–115.203; now support* | `Zxu0GY` `WmQ0Wi` |
| EURCHF | **0.93071–0.93126** · 19–20 Aug lows | **0.93849–0.94120** · pre-break shelf, **unrepaired** | `l7UNac` `1k2MtZ` |
| GBPUSD | **1.35197–1.35712** · 3 touches · 17–19 Aug | 1.36306–1.36598 · 45-day high zone | `JWFjte` `G9Zla7` |

**Read the ranking as focus order, not as a quality gate.** LOW does not mean
bad — GBPUSD confirms on every technical input it has. It scores low because
the fundamental gap is thin *and* the score disagrees with Thursday's US data.
**Know which of the three you are least sure about, and why.**

### 4.3b CORRELATED — the same bet, available as a secondary entry

Structure passed; each shares a leg with a carried pair, so carrying it would
be doubling the same currency call rather than adding a test.

| Pair | Dir | Spread | Same bet as | Thu move | Use |
|---|---|---|---|---|---|
| **GBPJPY** | LONG | 5.00 | CADJPY **via JPY** | **+163.1 pips** | **short-JPY at a different entry** |
| **EURJPY** | LONG | 5.50 | CADJPY **via JPY** | **+108.0 pips** | short-JPY, same |
| AUDCAD | SHORT | 5.92 | CADJPY **via CAD** | −28.8 pips | long-CAD at a different entry |
| AUDCHF | LONG | 5.08 | EURCHF **via CHF** | +13.4 pips | short-CHF, weakest of the CHF set |

**Their reads still stand.** If a carried pair has already run and the entry
looks extended, its correlated sibling is the same thesis on a different
chart — **but understand that taking both is one position at double size, not
two positions.** That is the whole reason they are listed separately.

### 4.4 REJECTED — with yesterday's rejects graded

| Pair | Dir | Spread | Status |
|---|---|---|---|
| **CADCHF** | LONG | **11.00** | **Rejected yesterday; the trade would have gained 30.9 pips.** Price has retraced 42.9% of the 19 Aug break. **Not re-carried today** — one recovery day does not rebuild an 8-touch zone that broke. **Watch:** a daily close above **0.58467** (the 18 Aug close) restores the structure. |
| **USDCHF** | LONG | 5.25 | **Rejected yesterday; would have gained 32.3 pips.** Bounced off the 21-day low. Same reasoning, same watch level: **0.81242**. |
| NZDCAD | SHORT | 6.50 | 5-touch support 0.81244–0.81662 held through Thursday. Reject stands. |
| EURCHF · GBPCHF · CHFJPY · USDJPY | — | — | Not re-read this run — **stated as unread, not as rejected on fresh evidence.** |

### 4.5 Week summary — the week that was

| Carry | **CADJPY (HIGH) · EURCHF (MEDIUM) · GBPUSD (LOW)** — three independent bets, ranked by confidence |
|---|---|
| **Yesterday** | All four positions worked, but they were **2 bets, not 4** (three shared JPY; CAD sat long twice). Corrected in §0. |
| **Theme confirmed** | **JPY weakness.** The three JPY crosses gained 82–163 pips in one session — but as **one** call, not three. That it paid is real; that the scorecard said 4/4 was not. |
| **Theme fading** | **The CHF bid.** 42.9% retraced in one session. The −3.00 score never corrected — price did. |
| **Watch into next week** | **NZDUSD SHORT — now +1.50, clears the floor** (needs a structure read) · **Jackson Hole 27–29 Aug** · **AU inflation Wed 26 Aug** — AUD's weight-3 category, currently 0.00 |

---

## §5 — Gold (XAUUSD)

**Re-read this run on closed bars.** OANDA:XAUUSD, D1, 21-bar window
(2026-04-22 → 2026-08-20). Thursday's bar is **CLOSED**; Friday's is forming.

### Drivers

| | Detail |
|---|---|
| **Driver (CORRECTED — T4/F-17)** | **The 19 Aug Treasury buyback.** Yields **FELL** that day — 10y −5bp, 30y −9bp — and the dollar fell 0.8%. Gold rose **with** falling yields on a **debasement trade**, not against rising ones. *Source: investinglive.com, "Gold's oversized reaction to Treasury buyback reflects debasement trade"; Treasury sb0607.* |
| **Headwind** | Real yields **+25–30bp** over the FOMC intermeeting period; three hawkish dissents; Thursday's US data ran hot (Philly Fed 47.4 vs 25, claims 206K vs 210K). |
| **Tailwind** | Haven demand. F&G safe-haven-demand component **68.0 (greed)**. |
| ~~The signal~~ | ~~*"Gold went up anyway, and then held. A market that shrugs off a hawkish repricing and strong data is being bought for a reason the rate story does not explain."*~~ **WRONG PREMISE — retained per the FAIL protocol.** The 25–30bp was the FOMC *intermeeting* move; it was not what happened on the 19 Aug bar. |

### Levels — recomputed, naming the bars

| Level | Value | Formed | Recompute |
|---|---|---|---|
| 21-day high | **4,541.045** | **Thu 20 Aug** | **new window high**, taking out 4,524.34 (19 Aug) |
| 21-day low | 3,996.055 | 12 May | — |
| **Thu close** | **4,518.955** | Thu 20 Aug (closed) | Wed 4,523.050 → Thu **−4.095 (−0.09%)**, volume 851,042 |
| Range | 544.990 | — | `4,541.045 − 3,996.055` |
| **Position in range** | **95.9%** | — | `(4,518.955 − 3,996.055) / 544.990` |
| Fri (forming) | 4,527.875 · high 4,544.01 | Fri 21 Aug | thin session, **extending above Thursday's high** |

### Read

**The breakout is holding, not fading.** 19 Aug broke out on 920,849 volume
(1.34× average); Thursday printed a **higher high** on 851,042 and closed
essentially flat (−0.09%) — that is consolidation at the top of the range, not
rejection. **95.9% of range.**

**Confidence: MEDIUM.** The structure is constructive and the volume supports
it, but Gold is rising *against* its main fundamental driver (real yields up),
which means the move rests on haven demand this report cannot source to a
specific cause. **An unexplained bid is a reason for less conviction, not more**
— the same discipline applied to CHF.

**Falsifier:** a daily close below **4,436.23** (the 18 Aug high, the level the
19 Aug breakout cleared) marks the move as a spike rather than a trend.

---

## §6 — BTC (BTCUSD)

**Re-read this run on closed bars.** OANDA:BTCUSD, D1, same 21-bar window.

### Levels

| Level | Value | Formed | Recompute |
|---|---|---|---|
| 21-day high | **72,989.5** | **Thu 20 Aug** | new window high |
| 21-day low | 62,203.0 | 2 Jun | — |
| **Thu close** | **72,657.0** | Thu 20 Aug (closed) | Wed 69,098.5 → Thu **+3,558.5 (+5.15%)** |
| Volume | **119,927** | Thu | **1.52× Wednesday's 78,798** — highest in the window |
| Range | 10,786.5 | — | `72,989.5 − 62,203.0` |
| **Position in range** | **96.9%** | — | `(72,657.0 − 62,203.0) / 10,786.5` |
| Fri (forming) | 74,609.0 · high 74,991.0 | Fri 21 Aug | **still extending** |

### The two-day move is the story

`Tue 64,551.5 → Thu 72,657.0 = +8,105.5 = **+12.56% in two sessions**`

### With risk, or decoupled? **DECOUPLED — and now decisively**

Yesterday this was a question. Thursday answered it:

| Evidence | Reading |
|---|---|
| BTC **+5.15%** Thursday on 1.52× volume | Strong bid |
| Gold **flat** at the top of its range, CHF **giving back** ground | Haven flow was *unwinding*, not building |
| F&G equity internals **weak** — stock strength 26.2, momentum 44.8 | Not tracking equity breadth either |
| US data **hot**, yields up | Not a liquidity/easing story |

**BTC rose on a day when the haven trade faded, equity breadth stayed weak, and
rates repriced hawkish. It is not tracking risk assets, havens, or the rate
path.** Whatever is driving it is idiosyncratic to crypto — and this report has
no sourced explanation for it, so none is offered.

**Confidence: LOW as an analytical read, despite the strong move.** A price
move this size with no identifiable driver is exactly what the report should
flag rather than narrate. **The move is a fact; the cause is not established.**

**Falsifier:** a daily close below **69,098.5** (Wednesday's close, the base of
the two-day advance) voids the decoupling read and puts BTC back with risk
assets.

---

## §7 — Method notes

| # | Note |
|---|---|
| 1 | **The F-13 span assertion ran and passed** — first use. The dated endpoint returned 17–30 Aug; the undated one yesterday started at Wed 19. The fix works. |
| 2 | **The F-9 recipe worked on a cold start.** CDP had dropped overnight; `TvMsixLaunch.exe` restored it first try. Second independent confirmation. |
| 3 | **The chart was on `VANTAGE:CADJPY`** when this run connected — Jeff's own state. Every read below set `OANDA:` explicitly, because levels do not transfer between feeds. |
| 4 | **Yesterday's rejects were graded, including the two that would have paid.** Recorded in §4.4 rather than quietly dropped. |
| 5 | **Falsifiers were raised on two breakouts** — a judgement call, flagged as such. |
| 6 | **§5 and §6 were RE-READ, not republished.** Carrying Thursday's Gold/BTC figures under a Friday date would have been stale-publishing; instead both were pulled fresh on closed bars. **BTC had moved +12.56% in two sessions** — republishing yesterday's 69,488 would have been materially wrong, not merely old. |

## §8 — Findings

**Two new findings this edition — F-14 and F-15.** Detail in STATE.md; the report cites IDs.

| ID | One line | Status |
|---|---|---|
| **F-15** | **A mandatory section silently vanished across three editions.** §1's market-structure block (CNN Fear & Greed, spec §2.3) went 9 mentions → 1 → **0**. Nothing failed; §1 was rebuilt each day and the block was simply not re-written. **Caught by Jeff after the seal.** | **NEW** — T4 amendment; needs a section-presence check |
| **F-14** | **The TE calendar window ROLLS.** Same URL returned 17–30 Aug at 06:50 and 18–31 Aug at 16:37; Monday went 47 rows → 0 in ten hours, and the `dates` start parameter is ignored. **A week cannot be rebuilt after the fact.** | **NEW** — captures now persisted immutably under `data/raw/calendar/` |
| **F-13** | Span assertion — the week table silently dropped Mon–Tue. | **FIX VERIFIED** — the assertion fired correctly on its first real test, catching F-14 |
| **F-1** | TE publishes unreleased figures in the ACTUAL field. | OPEN — the guard is procedure, not tooling |
| **F-7** | `batch_run` defective (retested on a valid call, 3/3 failed). | OPEN |
| **F-10** | RBA needs a *same-origin* Referer, and its page is JS-rendered anyway. | OPEN |
| **F-11** | A 200 response is not proof of data. **Fired again today** — AU S&P Global Mfg PMI served without a calendar table. | OPEN |
| **F-9** | TradingView CDP unreachable on a Store-installed app. | **CLOSED** — `TvMsixLaunch.exe`; worked again on a cold start this morning |

## §9 — Publish gate — FULL SEAL CANDIDATE (LD-12, Friday)

| Gate | Status |
|---|---|
| **P1 SOURCED** | **PASS** — 70/70 whitelist indicators with source, reference period and release status. 8/8 policy rates. Both guards documented, and the F-13 span assertion **fired correctly** (see F-14). Zones carry venue-prefixed symbol, timeframe, touch count and dates. |
| **P2 RECOMPUTED** | **PASS** — tally from `score_model.py` + `rate_model.py`, recomputed this run; F&G seven-mean to 4dp (0.0000 diff); every zone shows range and position arithmetic; every move shows open → close in pips and percent; the confidence tally shows every point. |
| **P3 — explicit pass over the week** | **SEALED.** Jeff, 2026-08-21: *"Seal"*. Verified before recording: tally reproduced from `score_model.py` + `rate_model.py`, all 70 whitelist indicators present in the deliverable, md/html agreement checked on key figures, falsifier published for every carried pair. |

### What a FULL seal commits to

It promotes this week's conclusions into STATE.md's **established-facts ledger**,
where later work cites them as settled. Two items I would seal narrowly:

| Item | Seal as | Do NOT seal as |
|---|---|---|
| **The CHF anomaly** | The **observation** — CHF gained ~1.35% against a five-cross basket on 19 Aug, also beat JPY (+0.97%), and has since retraced 42.9%. The arithmetic is solid. | Any **mechanism**. The cause is unidentified and no SNB action explains it. |
| **The projection method** | A **finding about the method** — 10 correct / 3 wrong, and **all 3 misses were BAD-projected surveys that printed GOOD**. | A **validated tool**. 13 observations is not a track record. |

### Still open at seal time — disclosure, not blockers

| # | Item |
|---|---|
| 1 | **Friday's daily bar is still forming**, closing 05:00 PHT Saturday. The three carried pairs are intact but their Friday closes are not final. |
| 2 | **AU S&P Global Mfg PMI Flash has no TE value** — page served without a calendar table (F-11 shape). Projection stays UNSCORED. |
| 3 | **CAD Retail Sales (20:30) and EUR Consumer Confidence (22:00) have not released** — both still pending tonight. |
| 4 | **ECB Meeting Accounts never retrieved** this week. |
| 5 | **Fed Chair unverified** — the minutes list Warsh in the Chair's voting position. Flagged, never asserted; §3 names no Chair. |
| 6 | **12 of 21 watchlist pairs unread.** Nine read. `batch_run` confirmed defective (F-7). |
| 7 | **NZDUSD SHORT now clears the 1.00 floor (+1.50)** on the new rate leg but **has had no structure read** — it is a watch item, not a carried pair. |

**Structurally complete** — bias *and* key levels per LD-4, all ten sections
published in full. The seven items above are stated so the seal covers what was
actually done, not what a reader might assume.
