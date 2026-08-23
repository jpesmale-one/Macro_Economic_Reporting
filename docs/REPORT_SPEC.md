# Daily Market Sentiment Report — SPEC

The build spec for the daily report described in
`Idea_dump/Project_Plan.txt`. The Idea_dump files are Jeff's INPUT and are
never edited; this file is the derived, authoritative spec. Where this spec
and the draft differ, **this spec wins and says why** (LD-7).

Governed by: LD-4 (no money path), LD-5 (levels are observations),
LD-7 (§4 reshaped), LD-8 (carry is a tiebreak), LD-9 (TE + phantom guard).

---

## 0. What this report is

A daily market-sentiment read combining fundamental and technical analysis
across the watchlist, refreshed at the start of Jeff's trading session.
Its output is a **bias with key levels and a falsifier** — never an order.

**All times Philippine Standard Time (UTC+8).** Every source timestamp is
converted, and the conversion is stated. TradingView must be on UTC+8; if
not, set it before reading any chart.

**THE TRADINGECONOMICS CALENDAR COLUMN IS UTC. PHT = UTC + 8h.**
Established 2026-08-19 by proof, after r1 of the first edition wrongly
assumed ET (UTC-4) and applied +12h, putting every schedule 4 hours late.
Proof: UK CPI released 07:00 BST = 06:00 UTC; the TE row showed `06:00`;
06:00 UTC + 8h = 14:00 PHT, which is when it landed.
**VERIFY THIS EACH RUN** against one known release rather than assuming it
- Jeff may change the TE display timezone, which would change the offset.
Pick a release that has already happened, convert it, and confirm the
result matches the time it actually landed.

---

## 1. THE SCOPE LINE (read before writing a single line of §4)

LD-4 stands. Jeff was offered the chance to loosen it for this report and
**declined** (LD-7). The draft's §4a ("including their entry and target
levels") and §4c (monitor open trades) are therefore NOT built as written.

Per line of output, apply this test:

> Does this sentence **describe what the market has done**, or **instruct
> what to do about it**?

| Ships | Does not ship |
|---|---|
| "AUDCAD: fundamental AUD-strong / CAD-weak, price holding above the 0.8850 swing low (4 touches since Jul 2)" | "Buy AUDCAD at 0.8850, target 0.8950" |
| "0.8950 is the range high, rejected twice" | "Target 0.8950" |
| "Alignment voids below 0.8850" (a falsifier) | "Stop at 0.8850" |

The *same number* is fine or forbidden depending on the **role** the
sentence gives it. Levels are published; execution roles are not.

---

## 2. Data gathering — order of operations

Run in this order. Later steps depend on earlier ones.

### 2.1 Calendar + macro prints — TradingEconomics (LD-9)

**STEP ZERO — CONFIRM THE CALENDAR TIMEZONE.** Take one release that has
already happened today, convert it, and check the result against the time
it actually landed. As of 2026-08-19 the column is **UTC (PHT = +8h)**.
Do not assume it; a display-timezone change would silently shift every
schedule in the report.

**THE PHANTOM-ACTUAL GUARD IS MANDATORY AND RUNS FIRST.**

For every row read from TradingEconomics:

1. Read the row's **scheduled release date/time**, converted to PHT.
2. Compare to **now**.
3. If the scheduled release is **in the future** but an Actual is shown:
   that Actual is the **PREVIOUS period's print**, not the current one.
   Use it as Previous. Label it. Never report it as a new release.
4. State release status explicitly in the report: **RELEASED** (with print)
   or **NOT YET RELEASED** (forecast/consensus only).

This is F-1, reproduced daily. It is a source defect, not a reading error —
checking that you read the "Actual" column does **not** catch it, because
the phantom value matches the forecast by construction. The schedule check
is the only defence.

Fetch per indicator: **Actual, Previous**, and Consensus/Forecast **as a
range**.

### 2.2 Interest rates + policy language — central bank sites

Authoritative for rate decisions and tone; TE is not.

| CCY | Source |
|---|---|
| USD | federalreserve.gov |
| EUR | ecb.europa.eu |
| GBP | bankofengland.co.uk |
| JPY | boj.or.jp |
| AUD | rba.gov.au |
| NZD | rbnz.govt.nz |
| CAD | bankofcanada.ca |
| CHF | snb.ch |

### 2.3 News + sentiment
- **investinglive.com** and **investing.com** — the PRIMARY feed for §1.
  Pull geopolitical events, disasters, central bank speeches, trade and
  tariff actions, and market-structure moves. These are news sources, so
  they are authoritative for *what happened*, never for a macro print's
  value.
- **CNN Fear & Greed Index** — use the **dataviz JSON endpoint**, not the
  article page:

  ```
  https://production.dataviz.cnn.io/index/fearandgreed/graphdata
  ```

  The article page (`edition.cnn.com/markets/fear-and-greed`) returns
  **HTTP 451** (geo-restricted). The endpoint returns **HTTP 418** to a
  plain fetch but serves normally **with browser headers** — send at
  minimum a desktop `User-Agent` and a `Referer` of the article page.

  It returns the index plus **all seven components** (junk bond demand,
  safe haven demand, stock price breadth, market volatility/VIX, put/call
  options, market momentum S&P 500, stock price strength), each with its
  own score, rating and timestamp, plus previous close / 1 week / 1 month
  / 1 year.

  **PUBLISH THE COMPONENTS, NOT JUST THE HEADLINE.** The index is a
  **simple average of the seven** — verified 2026-08-19: the mean matched
  the published score to the decimal. That means a neutral headline can
  average a badly split market, and the split is the tradeable
  information. Report the spread between the highest and lowest component
  whenever it is wide (>40 points), and say which side is stretched.

### 2.4 Technicals — TradingView MCP (LD-5, LD-6)
- **OANDA** exchange for all forex pairs.
- Verify chart timezone is UTC+8 first.
- Read-only tools plus drawing. `alert_create`/`alert_delete`,
  `replay_trade`, Pine/watchlist/layout mutators, and raw `ui_*` are
  **denied in project settings** (LD-6).

---

## 3. The fundamental scoring model

From `Idea_dump/Macro_economic_indicators.txt`. Eight currencies
(USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF) × six categories.

**The stated causal chain:**

```
Production → ┐
Spending  → ├→ Employment ─┐
Trade     → ┘   Inflation ─┴→ INTEREST RATE → currency strength
```

Categories 1–3 forecast Employment and Inflation. Categories 4–5 forecast
the rate decision. Category 6 is the decision itself — the core driver.

### Category weights (LD-13, amended by LD-23)

Categories are weighted by distance from the rate decision:

| Category | Weight |
|---|---|
| **Inflation** | **3** |
| **Interest Rate** | **3** |
| **Employment** | **2** |
| Production / Spending / Trade | 1 each |

**SIX categories, range +11.00 to −11.00.** LD-23 added Interest Rate as
category 6 at weight 3, scored on inflation vs the bank's **own mandate**
only. The earlier five-category ±8.00 model is superseded — any figure on
the old scale (e.g. a "+8.00 perfect score") is not comparable.

**Within a category, a currency's N indicators split the weight evenly** —
each is worth `weight / N`. GOOD `+weight/N`, BAD `−weight/N`, NEUTRAL `0`.

Generated by `pipelines/score_model.py` and `pipelines/rate_model.py` so
tables and tally cannot drift.

A currency with one indicator in a category stakes the full weight on it;
one with three spreads the risk. That is a real property of data coverage
and is left visible, not smoothed.

**ALL 70 NAMED INDICATORS ARE PUBLISHED EVERY EDITION.** An indicator that
cannot be sourced is published with score **NOT FOUND** so Jeff can verify
it — never dropped. A silent omission is unverifiable; a flagged gap is not.

Implementation: `pipelines/score_model.py`. §2's tables and the tally are
**generated from it**, so they cannot drift apart.

**Scoring thresholds** (as specified in the source file):

| Type | Good | Bad | Neutral |
|---|---|---|---|
| PMI | > 50.5 | < 49.5 | 49.5 – 50.5 |
| Growth-rate (YoY/MoM) | > 0.5% | < 0% | 0 – 0.5% |
| Confidence indices | > Previous | < Previous | unchanged |
| Balance of Trade | > Previous | < Previous | unchanged |
| Unemployment Rate | < Previous | > Previous | unchanged |
| NFP | > Consensus | < Consensus | — |
| Employment Change | > Previous, **full-time weighted heavier than part-time** | < Previous | unchanged |
| Inflation YoY | > 2% **and** rising → hike-leaning | < 2% **and** falling → cut-leaning | mixed → hold-leaning |
| Rate Decision | > Previous | < Previous | unchanged |

**Currency groupings** (carried from the source, used in risk-tone reads):
- **Safe haven:** USD, JPY, CHF, Gold
- **Commodity:** AUD, NZD, CAD
- **Risk-correlated:** EUR, GBP

**Known data-lag caveats**, stated in the source and repeated in output
whenever they matter: NZ employment and inflation are **quarterly** — late
by construction. Any NZD read must say so rather than treating stale
quarterly data as current.

**Scoring is P2 evidence.** Every category score shows the prints that
produced it — indicator, Actual, Previous, and the threshold applied. A
bare "AUD: Production = Good" is not publishable.

---

## 3b. THE BUILD ORDER — run this on every refresh (LD-43)

Jeff's process flow, 2026-08-23. **Section 2 above is the DATA-GATHERING
order; this is the BUILD order.** They are different documents: one says
what to fetch, this says what to write and in what sequence.

**Not a hard rule — but a deviation should be a decision, not an
accident.** If a step is skipped, the edition says which and why.

### STEP 0 — the guards, before any figure is used

Non-negotiable and it comes first (F-1, F-2). §2 cannot be built on
unverified values.

1. **Timezone** — convert one already-released event and check it against
   when it actually landed. Never assume UTC+8.
2. **Phantom Actual** — for every TE figure, confirm the issuing agency
   has actually released it. A phantom matches the forecast by
   construction, so column-checking cannot see it.
3. **Provisional check** (F-27/F-29) — is this figure FINAL, or a flash /
   advance / preliminary estimate? A provisional figure is labelled as
   such and never silently replaces the whitelist row.

### STEP 1 — §2 Macro Economic Indicators, and the currency strength read

**Fetch the calendar ONCE here** and keep the capture (F-14 — the window
rolls; two pulls minutes apart can disagree). This single pull serves
both §2 and §4.0.

- Pull all 70 whitelist rows from the country series pages, never from
  the calendar (F-3).
- Regenerate §2 with `pipelines/section2.py`; regenerate the tally with
  `score_model.py` + `rate_model.py`.
- **Analyse currency strength** — the bands come from the tally, and §2.0
  carries both so a band can never disagree with the score behind it.

### STEP 2 — §0 Week to Date Progress

**Weekend →** summarise the whole week. **Grade anything that was still
pending at Friday's seal (LD-44)** — those late prints are the one place
a weekend edition adds genuinely new data, and they completed the week's
scorecard that falsified EF-4 (F-21).

**Weekday →** track the locked set. Per carried pair: bias, Monday's
open, now, move in pips, favouring YES/NO/FLAT, falsifier state.

### STEP 3 — §1 News and §3 Central Banks

- §1 per LD-30: summarise to **impact**, not the article. Sources are a
  floor, not a ceiling. US items read against **USD, Gold AND BTC**.
- §3 forward-looking: what each bank does next and what would change it.

### STEP 4 — §4.0 projections, then the playbook

**Publish §4.0 from the step-1 capture** — whitelist indicators only
(LD-41). Off-list events go in the narrative block and score nothing.

**4a. Weekend, or the first run after a weekend →** build the Conviction
Playbook. Re-derive the **full board** (§4.2), apply the structure filter,
then leg-disjointness (LD-19 — ordering is load-bearing), then confidence
including the §4.0 projection term (LD-40). Nothing rolls over: a repeat
is a **re-proposal**, labelled with its week count (LD-42).

**4b. Weekday, set already selected →** monitor §4.0 only. **Keep the
rest of §4 intact** — no re-derivation, no re-ranking (LD-29).

> **If a weekday print changes a band (LD-43):** §2 re-scores and
> **publishes the new band**, but **§4's selection stays locked**. A pair
> leaves only when its falsifier fires. Where a carried leg has weakened,
> **§0 states the tension explicitly** — "AUD moved to WEAK, the set is
> locked until Monday" — rather than hiding it. The score is current; the
> selection is weekly. Both are true and the edition says so.

### STEP 5 — §5 Gold and §6 BTC

Read last, because both take the dollar and rate picture from §2 and §3.
Drivers in plain language showing the chain (LD-31); §6 mirrors §5.

**Then the bias is formed** from all three inputs together — §2 macro,
technical structure, and §4.0 projections (LD-40) — never from any one
of them alone.

## 4. Report structure

Seven sections. §0 was never specified and grew to 27% of the edition
across three builds (R-8); it is specified here.

### THE PROSE RULE (LD-27) — applies to EVERY section

**This report carries ANALYSIS, not commentary, and never process.**

Every prose sentence must do one of four things:
1. carry a **figure, level, or date**,
2. name a **source**,
3. state **what would change the read** (a falsifier), or
4. state **what the data means for the bias**.

A sentence that only re-describes a table row is **deleted** — the row
already said it. A sentence about **how the report was built** — guards
run, tools that failed, revisions, method rationale — goes to **STATE.md**,
never into the edition. The edition is the finding; STATE.md is the
reasoning.

**Target: prose under 15% of lines.** Measured on the rendered `.md`.
Tables and figures are never cut to hit it (LD-17) — compression is
prose-to-table, never figure-deletion.

### TYPOGRAPHY — headers outrank body (LD-28)

Section and sub-section headers must render **larger and heavier** than
the body text beneath them. Analysis notes, caveats and parentheticals
render **smaller** than body prose, not larger. Before this rule the
`.md` body ran ~1rem against `.68rem` uppercase headers — body text 40%
larger than the header above it, inverted at every level.

### §0 — Week to Date Progress

**Purpose: is the market favouring the bias we published?**

§4 selects the week's high-conviction pairs **on Monday and holds them
all week** (LD-29). §0 tracks that fixed set daily. §4 is the kitchen;
§0 is the scoreboard.

Per carried pair, one table row:

| Pair | Bias | Mon open | Now | Move (pips) | Favouring? | Falsifier |
|---|---|---|---|---|---|---|

- **Favouring?** — `YES` / `NO` / `FLAT`, judged against the published
  bias direction, not against profit. There is no money path (LD-4).
- **Falsifier** — the §4 observation that voids the read, and whether it
  has fired. A fired falsifier is stated plainly and the pair is marked
  **VOID** for the rest of the week; it is **not** re-selected (LD-29).
- **Move** — recomputed from the Monday open, naming the source bars.

Then **at most three sentences** of analysis: what the set is doing as a
whole, and any pair approaching its falsifier.

**On Monday** §0 carries the **week-that-was summary** for the *prior*
week — absorbed from the old §4.5, which is deleted. **If a WEEKEND PREP
edition ran (§4b), it already carried that summary and Monday's §0 cites
it rather than repeating it.** Monday's §0 grades
the closed week; Tuesday–Friday's §0 tracks the open one.

**§0 NEVER carries:** guard results, tool failures, revision history,
corrections to method, or any narrative about building the report. Those
are STATE.md's. The `§0b` / `§0c` sub-sections that appeared in earlier
editions are **abolished**.

### §1 — Headline Alerts, News & Current Events
**NOT a data table** — this is genuine news. Wars, geopolitical
escalation, disasters, pandemics, trade/tariff actions, central bank
speeches and commentary, and market-structure events (equity selloffs,
yield moves, oil moves) affecting the 8 currencies, Gold, and BTC.

**Opens with the CNN Fear & Greed Index** — the r9 bar chart with all 7
components, generated from a persisted capture (LD-25). Format is fixed;
do not redesign it.

**Sourced from investinglive.com and investing.com AT MINIMUM, and NOT
limited to them** (LD-30). Where those two do not explain a move, go
wider — the issuing agency, the wire services, the primary release. An
unexplained price move is a research trigger, not a finding (LD-26).

**Summarize to IMPACT, never reproduce the article.** Each item answers
one question: **"how does this move the currency?"** Record time (PHT),
what happened, the instrument it moves, and the source — then the impact
sentence. Grouped by kind — Geopolitical / Central banks / Risk events.

**US news is scored against three markets, not one.** Central bank
action, fiscal/Treasury operations and war/geopolitics move **USD, Gold
AND BTC**. Every US item states its read for all three or says explicitly
that it is FX-only.

A central bank *speech* belongs here; the *rate* belongs in §3.

### §2 — Macro Economic Indicators

**THE INDICATOR LIST IS A CLOSED SET. `Idea_dump/Macro_economic_indicators.txt`
is the WHITELIST, not a starting point.**

- **Only the 8 currencies** in the list appear: USD, EUR (EA), GBP, JPY,
  AUD, NZD, CAD, CHF. **DE, FR, IT, ES, ZA, CN, IN and every other country
  are NOT reportable rows** — even when TradingEconomics serves them and
  even when they look relevant.
- **Only the named indicators** for each currency appear. If the list says
  US Production = ISM Manufacturing PMI, Industrial Production YoY, Durable
  Goods Orders Ex Transp MoM, then Housing Starts and Pending Home Sales do
  **not** belong in §2 — they were never specified.
- **A missing indicator is reported as MISSING**, with its next scheduled
  release. It is never substituted with a similar-sounding one. "No US
  Production data released this week" is a valid and useful row.
- **BUT "MISSING" MUST BE PROVEN, NOT ASSUMED.** Before writing that an
  indicator is unavailable, fetch **its own TradingEconomics page** -
  `tradingeconomics.com/<country>/<indicator-slug>`. A country-page summary
  omitting it is NOT evidence it is unpublished; those summaries are
  partial by design. On 2026-08-19 nine indicators were wrongly declared
  unavailable off summary fetches, and all nine were published - the
  correction moved AUD from +3 to +6 and changed the top alignment.
- **CHECK THE VENDOR'S NAME FOR THE SERIES BEFORE CALLING IT A
  SUBSTITUTE.** TE often lists an indicator under a generic title while its
  page text names the exact series - "Manufacturing PMI" on the Swiss page
  is the `procure.ch-UBS Manufacturing PMI`. Read the page text before
  declaring a mismatch: a false substitution warning invents a data gap.
- **The absence claim is an ABSENCE-TYPE assertion** and carries the same
  burden as any must-NOT row: say what was checked and where. "Not on the
  country summary" is not a check; "its own page shows no print since
  <date>" is.
- The list is Jeff's specification of what drives his bias. Filling the
  tables with whatever the calendar happened to serve produces a different
  analysis than the one he asked for.

**Off-list data may still inform the READ** — a German PPI print or a China
number can legitimately shape the EUR or AUD narrative. When it does, it
goes in **§1 (news/context)** or in the category's prose read, clearly
labelled as context. It never becomes a scored row in a §2 table.

**ONE TABLE PER CATEGORY**, in the causal order of the model:
**2.1 Production · 2.2 Spending · 2.3 Trade · 2.4 Employment ·
2.5 Inflation.**

Every row carries: **scheduled time in PHT**, currency, event, Actual,
Previous, Consensus, the threshold applied, and the resulting score
(GOOD / BAD / NEUTRAL per §3's table).

**Not-yet-released rows are visually distinct and scored `NOT RELEASED`**
— never given a GOOD/BAD score off a phantom Actual. Each category closes
with a one-paragraph read naming which currency it favours.

Interest Rate is category 6 in the model but gets its own section (§3),
so it is not repeated here.

### §3 — Interest Rates

**Format (locked r7, from Jeff's reference layout).** One row per currency,
**ordered by policy pressure, not alphabetically**. Columns:

| Column | Content |
|---|---|
| **Ccy / Rate** | Current policy rate |
| **Last decision** | Action + date + **vote split** where published (6–3, 8–1, dissent names) |
| **Bias** | A short chip naming the pressure: HIKE RISK / CPI DECIDES / TRAPPED / FLOORED / TIGHTENING / REPRICING / SPLIT |
| **Next meeting** | Date, PHT |
| **Expectation** | One paragraph naming **what actually decides it next** — the pending release, the odds, the internal conflict |

The Expectation column is the point of the section. It is not a summary of
the rate; it is the answer to "what would move this."

**Source order:** the central bank's own site FIRST, TradingEconomics as
fallback. State which was used. Meeting dates come from the bank's own
calendar where reachable — `federalreserve.gov` publishes the FOMC calendar
and is authoritative for it.

**ALL EIGHT CENTRAL BANK SITES ARE REACHABLE** (established 2026-08-19,
F-6). `federalreserve.gov` works on a plain fetch; `rbnz.govt.nz` and
`snb.ch` need browser headers; `rba.gov.au` needs browser headers **plus a
`Referer`**. The recipes are in **`pipelines/fetch_headers.md`** — follow
that ladder before recording any source as unavailable, and say which step
failed. A 403 from a default fetch is a fact about our headers, not about
the source.

**A date from a secondary source is labelled as such**, and an unconfirmed
date says "unconfirmed" rather than being asserted.

**MARKET-IMPLIED ODDS REQUIRE A NAMED INSTRUMENT AND A DATE.** "~31% hike
(CME FedWatch, 14 Aug)" is publishable. "~70% priced" is not. Where no
sourced number exists, **omit the odds and say so** — every currency without
odds should be visibly without them, so the gap is not mistaken for
certainty. Analyst-consensus pricing may be used but must be labelled as
weaker evidence than a single named instrument.

**Times are PHT (UTC+8)** — convert and say so. A reference layout carrying
another timezone (PST, ET) is converted, never copied.

### §4 — Conviction Playbook  *(reshaped per LD-7, method per LD-16)*

**This is where the week's high-probability pairs are cooked.** Inputs:
§2's category scores, TradingView technical structure, and the week-ahead
projections. Output: a small set of pairs with a direction and a
falsifier.

**SELECTION IS WEEKLY, NOT DAILY (LD-29).** §4 selects on **Monday** and
the set **holds all week**.

**NOTHING ROLLS OVER BETWEEN WEEKS (LD-42).** A set is selected for one
week and ends with it. Monday re-derives the **full board** — a pair that
ran last week has no standing and must win its place again on current
evidence. When the same pair is selected again it is marked a
**re-proposal** with its consecutive-week count (`W2`, `W3`…), and last
week's result is shown as **history that scores nothing**. Crediting a
repeat would let confidence accrue to selection history rather than to
evidence — EF-3's error in the time dimension. Tuesday–Friday §4 does **not** re-derive the
pairs — it publishes the bands and any *change* in structure, and §0
carries the tracking. Re-deriving the same three pairs five times was a
primary noise source (R-8). A pair leaves the set mid-week only by its
falsifier firing, and is not replaced until the next Monday.

**Method, in order (LD-16):**
1. **Band** the 8 currencies from §2's tally — STRONG ≥ +4.00, NEUTRAL
   +0.01…+3.99, WEAK ≤ 0.00. Bands cut on the **scale** (±11.00 since
   LD-23), never on rank.
2. **Pair** STRONG vs WEAK in correct quote convention. Precedence
   EUR>GBP>AUD>NZD>USD>CAD>CHF>JPY sets base/quote; strong-as-base =
   LONG, strong-as-quote = SHORT. Never emit a non-standard symbol.
3. Also pair **haven vs haven** (USD/JPY/CHF) and **commodity vs
   commodity** (CAD/AUD/NZD) on relative ranking.
4. Do **not** enumerate every combination — prioritise conviction.
5. **Structure filter:** check D and H4 support/resistance on the
   shortlist. Carry only where fundamentals **and** structure agree.
   **Publish the rejects with their reason** — a rejected high-spread
   pair is the most informative row in the section.
6. **Leg-disjoint** (LD-19): structure filter FIRST, then disjointness.
   Ordering is load-bearing.
7. **Confidence** (LD-20, amended by LD-40): HIGH/MEDIUM/LOW with its
   arithmetic. **THREE INPUTS — §2 macro, technical structure, AND the
   §4.0 week-ahead projections.** The first two are realised evidence;
   the projection term scores what is *scheduled*, at **half weight**,
   because a forecast of a score must never outrank a print:
   **+1** a scored projection supports the favoured leg · **−1** it
   opposes the favoured leg · **−1** an unscorable but price-moving
   event (LD-3 speech, intervention risk) lands on either leg.
   A tally built only on realised evidence ranks a pair by what has
   already happened and ignores what is about to.
   **THREE IS THE FLOOR, NOT THE TARGET (LD-35).** Carry **every** pair
   that clears conviction and is leg-disjoint from those already carried
   — four, five, six if they qualify. Do **not** stop at three. Fewer
   than three means searching further down the spread ranking; more than
   three means the week offered more, which is information, not excess.
   Binding language — high-probability reads, **never** guarantees.
8. **Draw** the zones on the OANDA chart, record entity IDs for clearing
   next run, never touch Jeff's own drawings.

**FOUR IS A HARD CEILING (LD-35)** — 8 currencies, each claimable once,
so 4 leg-disjoint pairs is the arithmetic maximum. A qualifying fifth
pair goes to **4.3b CORRELATED** naming the pair it duplicates: visible,
chartable, available as a secondary entry (LD-21), but **not counted as
an independent test**. The carried count is the scorecard's denominator —
N carried must mean N independent tests of the model. Reporting a shared
leg as a separate test overstated the 2026-08-20 evidence **4×** (EF-3).

**Sub-sections:** 4.0 week-ahead projections · 4.1 currency bands ·
4.2 candidate pairings · 4.3 CARRIED with confidence and zones ·
4.3b CORRELATED as secondary entries (LD-21) · 4.4 REJECTED with reasons.

**4.5 is DELETED** — the week-that-was summary moved to §0 (LD-29).

**Zones are observations of structure** (LD-5): timeframe, lookback, type,
touch count with dates, venue-prefixed symbol. Never entry, stop, target
or size. "LONG/SHORT" names the **direction of the bias** — it is not an
order (LD-4).

**Notes and caveats render SMALLER than body prose**, never larger.

### §5 — Gold (XAUUSD)

**WHY THESE TWO SECTIONS EXIST (LD-45).** Gold and BTC are **monitored
continuously**, not selected weekly like the §4 pairs. The core logic is
simple and it is the reason they earn their own sections:

> **If the dollar is weak, Gold and/or BTC are strong — and that is an
> opportunity worth naming.**

Both are **dollar-priced and non-yielding**. A falling dollar lifts their
quoted price mechanically, before demand changes at all, and falling
yields cut the cost of holding an asset that pays no interest. One force,
two instruments. **They are therefore ONE signal, not two** — reading
BTC's strength as independent confirmation of Gold's double-counts the
same driver (EF-3's error in a different dimension).

**EVERY §5 AND §6 OPENS WITH THE DOLLAR CHECK**, both readings side by
side:

| | Source |
|---|---|
| **USD fundamental score** | §2's tally and band |
| **USD price direction** | DXY / the USD pairs, from TradingView |

- **Agreement** — score weak *and* price falling — is the strong case.
  Say so.
- **Disagreement is a PUBLISHED FINDING, not a footnote.** State it
  plainly, then **read the price**, because Gold and BTC respond to the
  dollar that *trades*, not the dollar that *scores*. Say why they differ:
  §2's 70 rows are monthly prints and lag; price is continuous.

**Measured 2026-08-23:** USD scored **+2.25 NEUTRAL** while trading at
**three-month lows**, and Gold rose 1.85% with BTC up 20% in three
sessions. **The score alone would have produced no signal at all.** That
is the case this check exists to catch.

**Drivers — written in PLAIN LANGUAGE, showing the CHAIN (LD-31).**
Do not name a driver and stop. Walk the mechanism from the event to the
gold price in ordinary words, one step at a time.

> *Not:* "Treasury buyback expansion, 30y −9bp, supportive."
> *But:* "Treasury said it will buy back at least twice as many long-dated
> bonds. More buying pushes bond prices up, which pushes their yields
> down — the 30-year fell 9bp. Gold pays no interest, so when bonds pay
> less, holding gold costs less by comparison. That, plus a dollar
> falling 0.8%, is why gold rose."

Standing drivers to cover: **real yields, the dollar, haven demand,
geopolitics, central bank buying**. Each gets the chain, not the label.

**Headwinds and tailwinds get the same treatment** — name the force, then
say **through what mechanism** it reaches the gold price, and **what
would have to happen** for it to stop mattering.

Then **technical structure** and **key levels to the LD-5 standard**
(timeframe, lookback, type, touch count with dates, venue-prefixed
symbol), and **what would change the read**.

Where CHF/JPY haven behaviour diverges from Gold, say so.

### §6 — BTC (BTCUSD)

**Mirror §5 exactly (LD-31)** — same structure, same plain-language
standard, same depth, **including the dollar check (LD-45)**. BTC is not
a lesser section.

**BTC carries one extra question Gold does not:** it can trade on the
dollar/liquidity channel *or* on the equity risk channel, and the two
point different ways. State which is driving it, with the evidence — a
decoupling claim needs the correlation stated, never asserted.

- **Drivers with the chain spelled out:** liquidity conditions, dollar
  direction, risk appetite, NAS100 correlation, flows. Where the same
  event drives Gold and BTC (dollar debasement, liquidity), say so and
  say why — on 19 Aug the Treasury buyback moved both, and calling BTC
  "decoupled" that day was wrong.
- **Headwinds and tailwinds**, mechanism named.
- **Technical structure and key levels**, LD-5 standard.
- **With risk, or decoupled?** — state which, with the evidence. It
  flips, and the answer changes the read. A decoupling claim needs the
  correlation stated, not asserted.
- **Falsifier.**

## 4b. EDITION TYPES — the weekly cycle (LD-32)

The report is not one shape repeated five times. It is a **cycle** with
three edition types, and the reader's job differs in each.

| Type | When | Selects? | Job |
|---|---|---|---|
| **WEEKEND PREP** | Sat **or** Sun | **PROPOSES** the coming week | reader charts and prepares while markets are shut |
| **MONDAY** | Mon | **CONFIRMS or REVISES**, then locks | the set for the week is fixed |
| **DAILY** | Tue–Fri | no | §0 tracks the locked set |

### The WEEKEND PREP edition (LD-32)

**Why it exists.** The bias for the coming week is already known at
Friday's close. Holding it until Monday hands the reader their own
analysis at the moment they have least time to use it. The weekend is
**the only window with the bias in hand and the market shut** — the
reader can chart the levels, run their own analysis, and disagree before
a single pip moves. **The value is LEAD TIME on data that already
exists, not new data.**

**MANDATORY HONESTY LINE, top of the edition, every time:**

> **No market has traded since Friday's close.** Every price, level and
> score in this edition is Friday's, republished here for preparation.
> Nothing below is new price data. The bias is **PROPOSED** — Monday's
> edition confirms or revises it against the real open.

**A weekend edition MUST NOT:**
- present Friday's prices as if newly observed, or re-date them;
- re-pull the 70 macro indicators — nothing publishes on a weekend, and
  re-pulling invites the phantom-Actual failure (F-1) for zero gain;
- claim a score, band or zone has *changed* since Friday;
- **LOCK the selection.** The weekend proposes; **Monday locks** (LD-29).

**A weekend edition CONTAINS:**

1. **§0 — Week that was.** The closed week graded: carried pairs and
   their outcome, the projection scorecard, what the falsifiers did.
   This is the old §4.5, and the weekend is its natural home.

2. **§4 — PROPOSED for the coming week.** The heart of the edition, and
   it stays in **§4** where the playbook always lives — the reader should
   not have to learn a new section number on a weekend.
   **Up to FOUR pairs** (LD-35) — publish every leg-disjoint qualifier,
   not just three; the reader has two days to chart them. Marked
   **PROPOSED**, never carried.
   Per proposed pair: **direction, the §2 score driving it, the zones
   with touch counts and dates, the falsifier level, and confidence with
   its arithmetic** — everything the reader needs to chart it. Marked
   **PROPOSED**, never carried.

3. **§0L — Late Friday grades.** Events that released before Friday's
   seal but had not posted values yet are graded here. This is **genuinely new
   information** and the one place a weekend edition adds data.

4. **§1 — Weekend news sweep.** Two days of headlines price in at once
   at Monday's open with no intervening discovery. Per LD-30: summarize
   to impact, sources are a floor not a ceiling, US items read against
   **USD, Gold AND BTC**.

5. **§2/§3 — republished unchanged**, explicitly labelled *as at Friday
   close*. Self-contained per LD-22.

6. **The week ahead.** The Mon–Fri calendar with each event's projected
   score, **and what would change the proposed bias** if it prints
   otherwise. Name the events that can void a proposal before it is ever
   locked.

7. **§5/§6 — Gold and BTC**, drivers per LD-31, levels as at Friday.

**Seal tier: NONE.** A weekend edition is **never sealed** and never
promotes to the established-facts ledger (LD-12 unchanged: light daily,
full weekly). It is a preparation document. Monday's edition is what
seals.

**Saturday or Sunday, reader's choice.** Sunday carries more weekend news
and is closer to the open; Saturday gives more preparation time. Both are
valid; the edition states which day it is and that the other was
available.

## 5. Confluence inputs (context, never ranked)

From `Watch_list.txt`, explicitly "to strengthen analysis":
**USOIL** (CAD), **SPI200** (AUD), **NIKKEI225** (JPY), **DJI / SPX /
NAS100** (USD, risk tone), **STOXX50** (EUR), **FTSE** (GBP).

These inform the read. They are **not** watchlist instruments and never
appear in §4.

---

## 6. Chart hygiene (draft requirement, LD-5/LD-6 bound)

The draft is explicit: *"Don't let any outdated level/s stale and clear the
chart as necessary when updating."*

- Levels drawn on a refresh **supersede** the prior session's.
- Stale levels are **removed**, not left to accumulate.
- Removal uses `draw_remove_one` / `draw_clear` — and **only for levels
  this report drew**. Jeff's own drawings, indicators, and layouts are his;
  the MCP drives his live chart, not a scratchpad (LD-5).
- Say what was cleared and what was drawn.

---

## 7. Output, storage, and the publish gate

### 7.1 Deliverable and storage (LD-10)

Each edition ships as an **HTML artifact** and is **saved in the repo**:

```
reports/YYYY/QN/YYYY-MM-DD_market-sentiment.md     <- sealed SOURCE OF TRUTH
reports/YYYY/QN/YYYY-MM-DD_market-sentiment.html   <- rendered deliverable
```

The `.md` is what P3 seals; the `.html` is what Jeff reads. If they ever
disagree, the `.md` wins and the HTML is re-rendered from it.

Each edition is a **new artifact with its own URL** — a daily report is a
dated record, not a living page, so it is never republished over
yesterday's URL. Record the URL in the `.md` front matter.

### 7.2 Seal tiers (LD-12)

| | **LIGHT seal** — every daily | **FULL seal** — weekly (Friday / last edition) |
|---|---|---|
| P1 SOURCED | **Mandatory** | **Mandatory** |
| P2 RECOMPUTED | **Mandatory** | **Mandatory** |
| P3 | Jeff's acknowledgement in-session | Explicit pass over the week |
| Citable by later work | Yes, marked `LIGHT` | Yes |
| Promotes to ESTABLISHED FACTS | No | **Yes** |

- **P1 SOURCED** — every figure carries source, indicator name, release
  date, as-of. Release status explicit.
- **P2 RECOMPUTED** — every derived number shows its arithmetic. For a
  **level**, the recompute is *naming the bars that formed it*.

**The tier changes the ceremony, never the evidence.** A daily may not
publish an unsourced figure, an unrecomputed derivation, or a bare level.

**T4 escalation:** any daily that would change a previously sealed
conclusion takes a **FULL** seal regardless of the day. Revisions never get
the light path.

### 7.3 Quarterly compaction (LD-11) — nothing is ever deleted

At the close of each quarter, manually and on Jeff's trigger:

1. **Write** `reports/YYYY/QN/_QN_SUMMARY.md` — what the quarter
   established: regime calls that held, calls that broke, falsifiers that
   fired, recurring anomalies, scoring thresholds that misfired.
2. **Promote** durable conclusions into STATE.md's established-facts
   ledger, with source and vintage. Sealed editions only.
3. **Gzip** the quarter's `.html` files in place. The `.md` sources stay
   uncompressed and readable forever.
4. **Confirm** every edition's `.md` is present and sealed. A missing or
   unsealed edition is a finding.

Measured before deciding: ~68 KB per edition, ~24 MB/year raw, ~5 MB/year
in git. **Storage is not the constraint — readability is.** Deletion was
rejected: git keeps deleted files in history anyway, so it reclaims nothing
while destroying the citation trail.

---

## 8. Open items this spec does not settle

- ~~**O-1**~~ — **RESOLVED by LD-10**: HTML artifact + repo copy, both.
- ~~**O-3**~~ — **RESOLVED by LD-12**: light seal daily, full seal weekly.
- **O-5** — whether data pulls run automated. Automation fires **T1 + T3**
  and pulls the whole thing onto the full gate ladder. Manual-driven for
  now — and the quarterly compaction job (LD-11) is manual for the same
  reason.
- **P-1** — standing coverage/cadence beyond the daily.
- **P-4** — ForexFactory access method (schedule role only, LD-3).
- **F-1** — stays **OPEN**. The phantom-Actual guard is a procedure I run,
  not tooling. It closes only on an automated schedule-vs-now check.
