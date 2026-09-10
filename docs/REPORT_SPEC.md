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

**§2.0 IS GENERATED AND SORTED BY SCORE, DESCENDING (LD-61).** Build
it with `section2.tally_table()`; never patch a cell in place. It sets
the BANDS every other section reads, and a mis-sorted tally drifts
**silently** because every number in it is still correct.

**WHITELIST AMENDMENTS (LD-51).** The list is a closed set (F-3), but Jeff
may amend it. An amendment is recorded HERE — `Idea_dump/` is committed
verbatim as historical input and is never edited (LD-1).

| Date | Indicator | Change | Why |
|---|---|---|---|
| 2026-08-23 | **GBP** Retail Sales YoY → **Retail Sales Ex Fuel YoY** | replaced | Jeff's call. Ex-fuel strips the volatile fuel component and reads underlying consumer demand, which is what the Spending category is for. |
| 2026-08-24 | **USD** Manufacturing Production YoY | **added** | Jeff's call. USD Production carried ISM PMI (a survey), Industrial Production (all output incl. mining and utilities) and Durable Goods. **None was manufacturing output specifically** — the segment that leads the cycle. GBP's Production block already carries this indicator, so the convention was set. |

**ALL 71 NAMED INDICATORS ARE PUBLISHED EVERY EDITION.** An indicator that
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

**§4.0 READS MARKET POSITIONING, NOT A FORECAST SCORE (LD-63).** One
test for every whitelist indicator, **regardless of category**:

| Consensus/Forecast range vs the CURRENT ACTUAL | Reads |
|---|---|
| range entirely **above** the current actual | **GOOD** — market prices improvement |
| range entirely **below** | **BAD** — market prices deterioration |
| current actual **inside** the range | **NEUTRAL** |

The range is **[Consensus, Forecast]** — TE publishes both columns and
the pair is the band. **Three sourced numbers, none derived**; that is
what removes the F-40 error class, where a Jul PREL, a Jun FINAL and a
consensus were conflated into one row.

**The CURRENT ACTUAL is the last released FINAL**, never a preliminary.

**§4.0 feeds §4.3's confidence (LD-64).** A pair whose short leg is
priced to strengthen carries a headwind the realised tally cannot see,
and the edition states it per pair.

**Publish §4.0 from the step-1 capture** — whitelist indicators only
(LD-41). Off-list events go in the narrative block and score nothing.
**Sort DATE → TIME → CCY (LD-52)** — chronological, because that is the
order the week is lived. Generate with `pipelines/week_ahead.py`, which
also reports any event the capture carries with **no time**, so an
untimed row can never fall out of a sort (F-36).

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
Each **opens with the dollar check** (LD-45): USD score and USD price
side by side, disagreement named. Drivers in plain language showing the
chain (LD-31); §6 mirrors §5.

**Then the bias is formed** from all three inputs together — §2 macro,
technical structure, and §4.0 projections (LD-40) — never from any one
of them alone.

### STEP 6 — DRAW THE LEVELS, EVERY REFRESH (LD-46)

**Not optional and not the reader's job.** Clear what the prior edition
drew — by its recorded entity IDs, nothing else — then draw the levels
this edition publishes: **XAUUSD, BTCUSD, and each carried or proposed
pair**, the falsifier always distinguishable.

Record the new entity IDs in the edition so the next run can clear
exactly what it owns. Full procedure in §6.

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

**§1 MUST COVER EVERY CURRENCY THE EDITION SAYS MOVED (LD-65).** A
currency flagged in §0 with a gap, an unexplained move, or a NO in the
favouring column **needs its catalyst looked for**. LD-30 says how to
write a news item; this says which ones are required.

**Not all eight every edition** — that forces empty headings on a quiet
day and LD-27 bans filler. The trigger is what the edition **itself**
identifies as moving.

**Search by the MOVE, not by the country.** On 2026-08-24 §0 diagnosed
a CAD gap, §1 covered Japan — the leg just ruled *out* — and the
catalyst was a 50% tariff regime going live. The morning sweep asked for
"Canada" headlines and the story was filed under trade war. **A currency
move is not always filed under the currency.**

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
1. **Band** the 8 currencies from §2's tally — **STRONG ≥ +5.50, NEUTRAL
   +0.01…+5.49, WEAK ≤ 0.00** (LD-76, confirmed by Jeff 2026-08-30).
   Bands cut on the **scale** (±11.00), never on rank. **5.50 is exactly half
   the scale** — a geometric split, recorded in `docs/SCORING_BASELINE.md`.
   *(This step read +4.00 until 2026-08-30 — a stale band in the METHOD is
   worse than a stale one in a table.)*
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
8. **CHART EVERY SELECTED PAIR — see the requirement below.** This is not
   optional and it is not the last thing on a list: **R-23 fails the render**
   if a selecting edition records no entity IDs in §4.3.

#### REQUIREMENT — chart every newly selected pair (LD-79)

**Jeff, 2026-08-30:** *"we should make it as a part of the requirement to chart
the pairs everytime we select a new pairs"*

**A pair that is selected but not charted is half-delivered.** The report computed
the levels; the reader should not have to re-plot them by hand to see where the
week is being tracked from.

**Every selected pair gets AT LEAST three lines, on its `OANDA:` daily chart:**

| Line | What it is |
|---|---|
| **Entry reference** | the close the week is graded from |
| **Falsifier** | the level that voids the read — a real printed bar beyond 1 ATR (LD-48) |
| **Structure ahead** | what price meets next IN THE BIAS DIRECTION — the room the read is aiming into (LD-47) |

**Draw a fourth when a constraint needs to be visible.** GBPAUD on 2026-08-30
carried its 45-bar low as a fourth line **because that low sits inside 1 ATR and
therefore CANNOT serve as the falsifier** — on the chart the constraint is
obvious; in prose it is a footnote.

**Each line carries a LABEL stating what it is and its evidence** (LD-5): the bar
that formed it, its distance from price, and for a falsifier the ATR check.

**Record every entity ID in §4.3**, so the next selection can clear them
(LD-16 step 6) without touching Jeff's own drawings.

**⚠ CHECK `draw_list` AND `draw_get_properties` BEFORE DRAWING** (LD-5). On
2026-08-30 CADCHF carried **9** of Jeff's rectangles and NZDJPY **4** of his
rectangles and trend lines. **Ours are labelled; his are not.** Never clear a
drawing you did not create.

**Enforced by R-23.** A WEEKEND edition must record ≥ 3 entity IDs in §4.3 or
the render fails. **The rule existed as step 8 and was skipped anyway on
2026-08-30** — which is why it is now a named requirement with a guard behind
it rather than a trailing line in a list.

**FOUR IS A HARD CEILING (LD-35)** — 8 currencies, each claimable once,
so 4 leg-disjoint pairs is the arithmetic maximum. A qualifying fifth
pair goes to **4.3b CORRELATED** naming the pair it duplicates: visible,
chartable, available as a secondary entry (LD-21), but **not counted as
an independent test**. The carried count is the scorecard's denominator —
N carried must mean N independent tests of the model. Reporting a shared
leg as a separate test overstated the 2026-08-20 evidence **4×** (EF-3).

**§4.5 CORRELATED is a POSITIONING list, not a warning list (LD-60),
and it covers EVERY carried pair — not just the top one.** A parent is
extended when it is extended; which one that happens to be changes week
to week, so all of them get a family.
It answers one question: *if a carried pair has already run, which
sibling offers the better entry on the same call?* Each correlated pair
publishes **live price, range position, distance to its next resistance,
and distance to support** — the parent's figures alongside, so they can
be compared. The double-size warning (LD-21) stays, but a list of names
with no prices cannot answer the question it exists for.

**Every alternative names what it costs.** A sibling with more room
is not a free switch — it trades one problem for another, and the
edition says which. Run any candidate through
`select_pairs.exposure()` against the carried set before recommending
it: on 2026-08-24 USDCHF was the least extended short-CHF expression by
a wide margin, and adding it would have left **USD net flat** while
**doubling CHF**, both at once.

**Report the counter-intuitive case when it occurs.** Range position and
distance-to-resistance are different measures and can point opposite
ways: on 2026-08-24 CADJPY sat at 97.8% of range yet had **19 pips** to
resistance while both siblings had **5–6**. The parent was the least
extended by the measure that matters.

**§4.1 CURRENCY BANDS IS DELETED (LD-62).** The bands live in **§2.0**,
which generates them from the tally that produces them. A second copy in
§4 was a duplicate that could disagree with its source — and did, until
LD-61 generated §2.0. **One table, one place.**

**Sub-sections:** 4.0 week-ahead projections ·
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

## 6. Chart hygiene — DRAWING IS A STEP, NOT AN EXTRA (LD-46)

**Idea_dump/Project_Plan.txt line 10, from the original request:**
*"Use the OANDA exchange then plot Key levels for entries and targets.
**Update these levels as we refresh the report.** Don't let any outdated
level/s stale and clear the chart as necessary when updating."*

**Two requirements. The spec carried only the second one until 2026-08-23,**
so drawing happened ad hoc instead of every refresh (F-31).

### 6.1 Plot every refresh — mandatory

**Every edition draws the levels it publishes.** A level that appears in a
§4/§5/§6 table and not on the chart is half-delivered: the reader has to
re-plot by hand what the report already computed.

**What gets drawn, every refresh:**

| Instrument | When | What |
|---|---|---|
| **XAUUSD** | every edition | resistance, support, **the falsifier**, major base |
| **BTCUSD** | every edition | resistance, support, **the falsifier**, major base |
| **Each carried/proposed pair** | on selection, then when structure changes | zones with touch counts, **the falsifier** |

**The falsifier is always drawn and always distinguishable** — it is the one
level whose breach voids the published read.

**Scope (LD-4, LD-5, LD-7).** The draft says "entries and targets"; LD-7
reshaped that and the reshaping stands. **Drawn levels are OBSERVATIONS OF
STRUCTURE — never an entry, stop, target or size.** A falsifier line marks
where the *read* is wrong, not where a position would exit. The drawing
requirement survived LD-7; the entry/target framing did not.

**Before drawing, always:**
1. `draw_list` on the symbol — **count what is already there.**
2. Sanity-check the feed: pull bars and confirm the values are plausible
   for the instrument (F-30 — a desynced MCP returns another symbol's
   prices under the right label). **Never draw a level from a feed you have
   not just checked.**

### 6.2 Clear the stale — mandatory

- Levels drawn on a refresh **supersede** the prior session's.
- Stale levels are **removed**, not left to accumulate.
- Removal uses `draw_remove_one` / `draw_clear` — and **only for levels
  this report drew**, by the entity IDs the prior edition recorded. Jeff's
  own drawings, indicators and layouts are his; the MCP drives his live
  chart, not a scratchpad (LD-5). AUDCAD carried **seven** of his drawings
  on 2026-08-20 — the check is not theoretical.
- **Every edition records the entity IDs it created**, so the next run can
  clear exactly what it owns and nothing else.
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

---

### LD-91 · LD-92 · LD-93 — making the model LEADING instead of LAGGING

**Jeff, 2026-09-02:** *"Trading the news is one thing. But the whole point of
this report is to foresee if the central bank will Hike before it happen …
probably our scoring makes things lagging instead of leading. Instead of
putting weight into the lagging indicators we probably want to focus more on
the leading side or see all of them as equal."*

#### The measurement

| Stage | Weight | Share |
|---|---|---|
| LEADING — Production, Spending, Trade | 3 | **27%** |
| CONFIRMING — Employment, Inflation | 5 | 45% |
| RATE — the decision | 3 | 27% |

**73% of the score is the thing being PREDICTED; 27% is the thing that
PREDICTS it.** For a model whose stated job is to foresee a hike, that is
backwards.

**One thing I checked and got wrong first:** I claimed the heavy categories
were also the stalest, so the lag compounded. **They are not** — Production
1.9mo, Inflation 2.1mo, and Trade is the OLDEST at 2.6mo carrying weight 1.
**The ages are flat. It is the weights, and only the weights.**

#### LD-91 — §4.0 scores a rate decision by its SURPRISE

**Jeff:** *"now that we have the picture for Interest Rate news how do we
score it in §4.0?"*

The cell used to restate §2.6's score — **a number about the past, sitting in
a forward-looking table.** It now says what the market must SEE to be
surprised:

```
AHEAD     HIKE PRICED +0.25pp - delivering it is NOT news; a hold is the shock
          HOLD PRICED        - a hold is the baseline, ANY move is the surprise
          UNPRICED           - no consensus, the surprise cannot be measured
RELEASED  surprise +0.00     - FULLY PRICED, no surprise, no reason to buy
```

**RBNZ today reads FULLY PRICED. BoC tonight reads HOLD PRICED.**

#### LD-92 — cycle tilt ±25% → ±50%

**§2.0b already computed the lead-vs-confirm gap and called NZD IN THE PAST on
30 Aug — correctly.** NZDJPY went on to be the week's only loser. **The
leading signal was never missing; it sat downstream of a tally that outvotes
it 8:3.**

**Raising the tilt strengthens it WITHOUT touching the weights** — the cheaper
lever, and reversible on one line.

**It reshuffled §4.2: CADJPY to the top** (the only cycle-neutral pair) **and
GBPAUD to the bottom** on its −1.00 tilt — **and GBPAUD made +15.5 this week.**
That tension is the review's job, not mine to resolve on n=3.

#### LD-93 — §2.0d publishes three weightings in parallel

**Selection still ranks on CURRENT. Nothing changes today.** EQUAL and
LEADING-TILT accumulate a record beside it so **Saturday decides on a week of
evidence rather than three sessions.**

| CCY | Current | Equal | Leading | |
|---|---|---|---|---|
| **NZD** | +3.31 (4th) | +0.68 | **+0.41 (LAST)** | the week's only losing leg |
| **CHF** | −0.28 (last) | +1.64 | **+5.85 (2nd)** | and we are SHORT it in the best pair |

**Those two rows are the whole argument, and they point opposite ways.**

**EQUAL is on the sheet for completeness, not as a live candidate.**
Flattening Inflation 3 → 1 strips the rate-differential signal, **which is the
transmission channel the whole report rests on** — Jeff, 2026-08-21: *"the
Interest Rate dictates if the Currency is Strong or Weak."* It scored **1 of
3** against this week's moves; CURRENT and LEADING both scored 2.

**THE WEIGHTS THEMSELVES ARE NOT CHANGED.** On n=3 that is tuning to noise.
**It is the headline item on the 2026-09-05 agenda.**

---
### LD-90 — a decision moves price by its SURPRISE only

**Jeff, 2026-09-02, after the RBNZ hiked to 2.75% and NZD fell 108 pips:**

> *"The market is always forward looking. The hike itself wasn't news. What
> the market trades is the gap between what happened and what was already
> priced — and on that measure this was a dovish event."*

> *"A central bank decision moves price by its surprise component only. Level
> of rates → already discounted. Change in the expected path → that's the
> tradable variable. This is why you'll see currencies fall on hikes and rally
> on cuts more often than beginners expect."*

#### The evidence, from our own capture and chart

```
RBNZ  actual 2.75%   consensus 2.75%   forecast 2.75%
NZDJPY 94.409 (07:40 PHT) -> 93.331 (14:15) = -107.8 pips
```

**~95% swap odds. 21 of 21 economists. ASB and Westpac both at 25bp.** A
decision that well telegraphed is in the price days before. **Zero new
information = zero reason to buy.**

#### What was broken

**`rate_model` scored REALISED (hiked +1 / held 0 / cut −1) plus EXPECTED
(inflation vs mandate). Both describe the LEVEL and DIRECTION of what already
happened. Neither knows what was PRICED.**

**So §2.6 would have scored NZD MORE POSITIVELY for an event that cost 108
pips.** That is the flaw stated at its sharpest.

#### The fix

```
score = (REALISED + EXPECTED + SURPRISE) / n * 3
surprise = clamp((actual - consensus) / 0.25, -1, +1)
```

**NZD: realised +1.00, expected +0.50, surprise 0.00 → rate score +2.25 →
+1.50, tally +4.29 → +3.31.** The level still earns credit; **the news that
was not news earns nothing.**

**A surprise of None is UNMEASURABLE and drops out of the average entirely** —
scoring it zero would assert the market was unsurprised, which is a claim we
cannot make without a consensus.

#### What is deliberately NOT scored

**The forward track — which Jeff correctly identifies as the variable that was
actually live.** Markets priced **~95bp of tightening to June 2027** against
the RBNZ's own **25bp over three quarters**; the track came in flatter and the
Kiwi sold off with it.

**TE publishes no OCR track, no terminal rate, no priced path**, and **LD-23
already rejected exactly these inputs** on Jeff's own instruction: *"if we
cannot find an equilibrium for Steps 2,3,4 then I'd say let's just used Step 1
in the scoring. this way we are not nit-picking and create a unfavorable bias
for other currencies."*

**So the path is COMMENTARY in §3 and never a number.** Scoring a path
sourceable for one or two currencies would recreate the bias LD-23 exists to
prevent. **This is on the 2026-09-05 agenda as an open question: worth
carrying as commentary where it exists, or not at all?**

**R-36 `test_surprise.py` — 8 cases graded by hand first**, including the two
counter-intuitive ones Jeff named: **a hold that sinks the currency** and **a
cut that rallies it.**

---
### LD-89 — R-35 BLOCKS: every section must move, or say why not

**Jeff, 2026-09-02:** *"can we make sure we visit every section everytime we
build a new report moving forward?"*

**R-35 shipped as a REPORT and that was not enough.** A report I have to
remember to read is exactly what failed on 26 Aug, when he first asked for
this. **It now fails the render.**

#### The escape hatch is the point

**A section that genuinely has nothing new says so IN THE SECTION** —
*"unchanged since \<date\>: \<why\>"* — and the guard accepts it.

**That converts a silent carry into a published claim someone can check.**
Same principle as F-73: say what you know, and say that you know it. **§8
(findings ledger) and §9 (gate status) are exempt** — they legitimately repeat.

#### What it found the moment it blocked

Run against the three most recent editions, it failed two of them:

| Edition | Carried verbatim |
|---|---|
| **31 Aug** | **§3 and §7**, 100% identical |
| **1 Sep** | **§7**, 100% identical |
| 2 Sep | clean after the F-80 fix |

**§7 was carried on BOTH days** — a guard table reporting an older run, which
is worse than no table because it reads as evidence.

**And clearing R-35 exposed three more defects in those editions**, each
caught by a guard written after they published:

- **R-34** — the same *"Jackson Hole is the next signal"* line, still live
- **R-33** — the pasted F&G block and a pre-escaped `&amp;`
- **R-32** — both central banks eight hours early

**All three editions now render clean under every guard.** The carries are
declared rather than back-filled with invented content — the history says what
happened, and the guard that would have caught it did not exist yet.

---
### F-80 · R-35 — §4 carried Sunday's measurements for three days

**Jeff, 2026-09-02:** *"Didn't I asked that every section should be revisited
and refreshed everytime we build a new edition? is there any other sections of
the report still stale?"*

**He asked for this on 26 Aug and it is in CLAUDE.md.** I had been refreshing
the sections I happened to touch and letting the rest carry. **Measuring it
settled the question in one table:**

| § | Same as yesterday | |
|---|---|---|
| 0, 1, 3 | 29–59% | refreshed |
| 2, 5, 6 | 89–96% | partial |
| **4** | **99.2%** | **carried verbatim** — the selection playbook |
| **7** | **100%** | **carried verbatim** — yesterday's guard results |
| 8, 9 | 100% | legitimately quiet |

#### What §4 was actually publishing

**§4.3 showed SUNDAY's room and clear-by figures as though current**, and
**contradicted §4.2 in the same edition** — GBPAUD room **0.92** in one table
and **0.56** in the other. Entry ref and falsifier are correctly frozen; **room
and distance are live measurements and were not.**

**§4.1 counted event risk on twelve rows that had already released**, leaving
NZD reading **CROWDED** on events that had printed.

**§4.5's bench was three sessions old** — 199/322/146 pips, none re-measured.

**And §4.2 itself turned out to be the stale one of the pair**: built with
Tuesday 13:05 prices and never refreshed. **CADCHF's real room is 0.11, not
the 0.20 it had been showing.**

#### §7 said the market was closed

*"Market status: CLOSED — Friday's bars are FINAL"* on a **Wednesday**, plus
the 28 Aug Fear & Greed and a TE line from a different run. **A guard table
that reports yesterday's run is worse than no guard table** — it reads as
evidence.

#### The guard, and its limit

**R-35 `pipelines/section_drift.py`** diffs each section against the previous
edition and names anything that carried verbatim.

**It REPORTS rather than blocks, deliberately.** It cannot distinguish a
section that legitimately did not change from one that was forgotten — §8 (the
findings ledger) and §9 (gate status) often genuinely repeat. **The point is to
make a carry VISIBLE so it is a decision rather than an oversight.**

**After the fix: §4 99.2% → 93.4%, §7 100% → 82.4%**, and only §8/§9 carry.

---
### F-79 · R-34 — a carried section keeps its VERBS, and the verbs go stale first

**Jeff, 2026-09-02:** *"§3 — is this updated? I can see this note Jackson Hole
27–29 Aug is the next signal. but this is already in the past"*

**§3 was carrying FOUR dead references at once:**

| Claim | Reality |
|---|---|
| *"Jackson Hole 27–29 Aug is the next signal"* | **five days past** |
| *"No policy decision has occurred this week — the next is NZD on 2 Sep"* | **it was 2 Sep** |
| *"AU inflation Wed 26 Aug is the weight-3 category"* | **a week past** |
| *"No CHF release next week — the score cannot correct"* | **CHF released twice on 1 Sep** |

**And §5/§6 carried Jackson Hole as a LIVE headwind in five more places** —
"a hawkish Jackson Hole is the event most likely to cause it" — while its
outcome was already in the price.

**Also wrong: the Fed row read "15–16 Sep"**, the US local date. `pht()` on
the capture gives **Thu 17 Sep 02:00 PHT**.

#### Why a carried section rots this way

**Numbers get refreshed because a guard checks them. Verbs do not.** R-16
catches a stale SCORE, R-19 catches a released event still previewed in §4.0,
LD-50 catches a stale VALUE — **nothing looked at tense.** So §3 kept its
rates current and its outlook frozen in late August.

**R-34 `assert_no_dead_signal()`** fails the render when a forward phrase
(*next signal*, *the next is*, *upcoming*, *next meeting*, *still ahead*) sits
beside a date that has already passed.

**F-79b — scope it to the CLAUSE, not the line.** The first version matched
across a whole §3 table row, which is 300 characters wide and legitimately
holds *"HELD 29 Jul"* in one cell and *"next meeting"* in another. **It
flagged two rows that were entirely correct.** Splitting on `|`, em-dash and
sentence boundaries fixed it — **and then it caught the real one still sitting
in the 1 Sep edition.**

**§3 is now rebuilt from the capture**: every meeting time is `pht()`, and
every row names what actually released this week.

---
### F-78 · R-33 — a generated block was PASTED as well as generated

**Jeff, 2026-09-02, with a screenshot:** *"Our Fear and Greed index is not
rendering correctly. can you check?"*

**It rendered TWICE.** Once correctly from `<!--FNG-->`, then again as an
escaped paragraph of visible tag soup — `&lt;div class="fng-head"&gt;` and the
whole block, printed as text below the chart.

**The renderer BUILDS that block from the marker alone.** A previous build had
pasted the generated HTML into the markdown right after the marker, so the
file carried a duplicate that markdown then escaped. **15 escaped copies of
every `fng-*` class in the output.**

**This is LD-38's other half.** LD-38 catches a generated block REPLACED by
hand-written markdown; this catches one DUPLICATED by hand-pasted HTML. **Same
root cause: treating a generated block as editable text.**

#### The second defect in the same screenshot

**The heading read `CNN Fear &amp; Greed Index`.** The markdown source carried
a pre-escaped `&amp;`, and **the renderer escapes on output**, so it became
`&amp;amp;` and the reader saw the entity. **Front-matter is exempt — it is
HTML by design — but the body must carry a literal `&`.**

**R-33 `assert_no_raw_generated_html()`** fails the render on either: pasted
`fng-*` markup in the body, or a pre-escaped `&amp;`/`&lt;`/`&gt;`/`&quot;`.
**Verified against both defects.**

**Both September editions were affected and both are corrected** — the block
is 4 KB smaller with the duplicate gone.

---
### F-77 · R-32 — I converted a converted time, twice

**Jeff, 2026-09-02:** *"Every time we fetch Data can you always verify the
Time first? as per TE RBNZ is scheduled 10AM today roughly in 1 Hr"*

**He was right. §4.0 published the RBNZ at 02:00 PHT; `pht()` on the same
capture row returns 10:00** — exactly what his screen showed.

#### Two errors compounding

**1. The §4.0 builder's `EV` list carried HAND-TYPED times.** They were never
checked against the capture, so once one was wrong it survived every rebuild.
**Both central banks were eight hours early** — RBNZ 02:00 for 10:00, BoC
13:45 for 21:45.

**2. I then read "02:00 PHT" off the RENDERED TABLE and converted it BACKWARDS
to 18:00 UTC** to argue the decision had already passed. **The cell was the
LABEL — already converted.** I converted twice, concluded the RBNZ was five
hours overdue, and wrote an entire section about its silence.

#### Why it survived my own checks

**Price appeared to confirm it.** NZDUSD ranged 9 pips and AUDNZD 16 pips
across the window I examined — which I read as proof no decision had been
delivered. **It was flat because the decision had not happened yet.**

**A false premise that agrees with the evidence is the most expensive kind.**
I had two independent confirmations of a conclusion that was wrong at the
root, and the confirmations were real.

**This is F-72's rule, third instance:** *when our data disagrees with what
Jeff sees on screen, we are wrong until proven otherwise.* **I had the rule
written down in CLAUDE.md and did not apply it** — because the disagreement
was with a number I had produced, and it looked like a TE defect.

#### The fix

**§4.0's When cell is now COMPUTED from `pht(capture)`** — the hand-typed
times are out of the trust path entirely.

**R-32 `pipelines/audit_times.py`** fails the render when any §4.0 time
disagrees with the capture row it names. **Verified: passes on 19 of 19 rows,
fires on the RBNZ row when reset to 02:00.**

**Run it on every edition** — it is in the pre-edition list, and it is the
answer to Jeff's actual question: *verify the time first.*

---
### F-76 — a fuzzy matcher picks; it does not report an ambiguity

**Found building the 2026-09-02 edition.** LD-50 reported **USD ISM
Manufacturing PMI: ours 53.2, TE 53.9** — same reference period, no NEWER
flag. **A disagreement that did not exist.**

**The US publishes TWO manufacturing PMIs fifteen minutes apart.** Our row
names the **ISM**; TE's indicator page key `manufacturing pmi` is **S&P
Global's**. With no alias, `difflib.get_close_matches` matched them at 0.86
and compared our ISM figure against S&P Global's.

**This is F-65c in a second module.** §4.0 got a `PIN` map for exactly this
collision on 2026-08-30; `audit_te.py` kept fuzzy-matching.

#### The fix is NOT an alias

**The first attempt pinned `ISM Manufacturing PMI` → `ism manufacturing pmi`.
That key does not exist.** TE's united-states indicator page carries every ISM
**sub-index** — employment, new orders, prices, production, inventories — **but
not the ISM headline.** It lives only on the CALENDAR.

**So the row is genuinely unreconcilable against that page**, and it now sits
in `KNOWN_SERIES_GAP` saying so. **The value is verified against the calendar
capture instead** (54.6 Aug/26), which is where the series actually lives.

**The lesson generalises: a fuzzy matcher does not report an ambiguity, it
picks one** — and then the mismatch it prints is noise that trains you to skim
the audit. Same conclusion as F-67, from the opposite direction: there the
reflex was to loosen matching, here the damage came from matching that was
already too loose.

---
### LD-88 — §2.1–2.5 publish the GRADED SCORE, not the verdict

**Jeff, 2026-09-01:** *"on 2.1 to 2.5 in the score instead of Good Neutral
Bad, can you put in the actual score? kinda similar to 2.6"*

**§2.6 has published a signed number since LD-23. §2.1–2.5 published
GOOD/NEUTRAL/BAD — and since LD-71 those tables have been HIDING a real
number.**

| Row | Old cell | Actual score |
|---|---|---|
| JPY Industrial Production YoY | GOOD | **+1.00** |
| USD Industrial Production YoY | GOOD | **+0.20** |
| USD ISM Manufacturing PMI | GOOD | **+0.54** |
| USD Durable Goods Ex Transp | BAD | **−0.03** |

**Two rows reading GOOD can differ by a factor of five**, and §2.0's totals
were always built from the numbers rather than the labels. **The tables were
showing less than the model knew.**

#### The dagger

**51 of 71 rows have a graded rule. The other 20 have no pattern and score
exactly +1 / −1 / 0 from the verdict** — Jeff's hand-curated rows (LD-57,
LD-58, LD-59), which stay untouched by design.

**Those carry †**, so a full mark earned from a rule is never mistaken for a
full mark taken by default. **The distinction matters: −1.00† on CHF
Inflation is a three-state verdict, while −0.03 on USD Durable Goods is a
measured near-miss.**

#### Verified by reconstruction

**Every published row score was summed back into §2.0's totals** — category
weight divided by that currency's row count in that category, plus §2.6's rate
score. **All eight currencies reconcile to within 0.006**, which is the
2-decimal display rounding and nothing else.

**The first attempt at that check failed on all eight** because it divided the
category weight by the CATEGORY's row count rather than the CURRENCY's. **The
checker was wrong, not the table** — worth recording, because a reconciliation
that fails is only evidence once you have verified the reconciler.

**No layout change:** the column set is untouched, so R-24 and R-27 pass
without re-blessing. Only cell CONTENT moved.

---
### F-74 — a RELEASE is graded against CONSENSUS, not against the previous print

**Found building the 2026-09-01 edition.** JPY S&P Global Mfg PMI printed
**54.9 against a 55.1 consensus**, up from 54.5. **§4.0 graded it BEAT.**

**It is a MISS.** The row compared the actual to the PREVIOUS figure, so any
improvement on last month scored as a beat regardless of what the market
expected.

**Both statements are true and only one moves price:**

| Comparison | Result | Moves price? |
|---|---|---|
| 54.9 vs previous 54.5 | the series improved | no |
| 54.9 vs consensus 55.1 | **the market was disappointed** | **yes** |

**A SURPRISE IS MEASURED AGAINST WHAT WAS EXPECTED.** That is the whole
premise of §4.6 (LD-68, direction × surprise) and of LD-85's forward
adjustment — both of which grade against consensus. **§4.0's own release
column was the one place still comparing to the previous print.**

**Fix:** grade against CONSENSUS when one exists; fall back to previous only
when the week was never priced, and **say which** — an unpriced release now
reads *up vs prev* rather than borrowing the language of a beat.

**Same family as F-66/F-68/F-70:** all four are the wrong REFERENCE POINT for
a comparison. F-66 took the direction from the wrong place, F-68 read history
as direction, F-70 used the consumer's sign, **F-74 used the wrong baseline.**

**Pricing regressions now 26**, including the JPY PMI case and an in-line AUD
print.

---
### F-73 — "not scheduled" was a claim we could not make

**Jeff, 2026-08-31, within minutes of LD-87 shipping:**

> *"USD CB Consumer Confidence — This is scheduled Sept 29 10pm PHT. USD
> Personal Spending MoM — Sept 30 8:30pm PHT. EUR Consumer Confidence Final —
> Sept 29 5:00 pm PHT. JPY Retail Sales YoY — Sept 30 7:50 am PHT. I think
> you're missing Sept 29 – 30"*

**He was right on all four.** The capture **hard-stops at 25 Sep** — zero rows
beyond it. **TE serves roughly 26 days forward from the fetch date**, and that
horizon is a **MOVING WALL**, not a published limit.

#### Two defects, one symptom

**1. The label lied.** Rendering an absent row as `not scheduled` states
something about TE's calendar. **What we actually knew was something about OUR
WINDOW.** Those four events exist and are scheduled; we simply could not see
them. **A guard cannot catch this — the cell was populated, non-blank, and
wrong.**

**2. `next_due` read only the NEWEST capture** and discarded every earlier
one, throwing away schedule knowledge we had already paid to fetch. It now
**unions every capture on disk** — which is what `release_week.py` (LD-83) had
been doing all along.

#### The fix

| Was | Now |
|---|---|
| `not scheduled` | **`beyond 25 Sep`** — names OUR horizon |
| newest capture only | **union of every capture** |
| horizon invisible | **`horizon()` reports the wall** |

**Trying to fetch further does not work.** `?startdate=`, `?dates=`, `?d1=`
and a path form were all probed: **TE ignores them and serves its default
window.** The range is an ASP.NET postback, not a URL parameter.

**The horizon rolls on its own.** 29 Sep enters the window around 4 Sep, 30
Sep around the 5th. **Daily captures plus the union close the gap without any
extra fetching** — which is precisely why raw captures are kept rather than
overwritten.

#### The lesson

**Say what you know, not what you infer from its absence.** An empty result
has at least two causes — the thing does not exist, or we could not see it —
**and only one of them is a fact about the world.** Same shape as F-65 (a
field empty on every row is a fact about US) and F-72 (when our data disagrees
with what Jeff sees, we are wrong until proven otherwise).

---
### LD-87 — NEXT DUE in §2: when is each indicator retested?

**Jeff, 2026-08-31:** *"For each indicators in §2 we put which week these news
will come out. in TE the whole schedule for September is already out. so we
can check on which week in September these indicators will come out."*

**§2.1–2.5 gain a NEXT DUE column** carrying the scheduled date and its week
of month — `W1 · Thu 3 Sep`.

#### Why this is not LD-83

| | Answers | Source |
|---|---|---|
| **LD-83** `release_week.py` | *"this series usually lands in W1"* | **inferred** from capture history |
| **LD-87** `next_due.py` | *"this row's next print is Thu 3 Sep"* | **read** from TE's schedule |

**Both are worth having** — LD-83 powers the `--due` gap check, LD-87 states a
fact. **But where TE publishes the calendar, look it up rather than infer it.**

#### What it adds to the read

**A GOOD score with a print due Thursday is not the same thing as a GOOD score
with nothing until the 24th.** The first is about to be tested; the second is
being carried. **That distinction was invisible in §2**, and it is the same
blind spot that let NZD hold +4.29 on Jun/26 quarterly data while every fresh
print ran the other way.

**First run, 2026-08-31:** 60 of 71 rows have a scheduled print in the window
(28 Aug – 25 Sep). **W1 carries 25 of them, the densest week of the month.**

**And the finding that matters this week: NZD Inflation is not retested until
Fri 18 Sep, and NZD Unemployment is not scheduled at all.** Both quarterly,
both Jun/26, **neither refreshes inside this week's lock.**

#### Two guards moved

**LD-39 rejected the first attempt**, which used an em dash for an unscheduled
row — correctly, because *"not scheduled"* and *"we failed to look"* must not
render identically. **It now reads `not scheduled`: a claim about the calendar
that can be checked.**

**R-24 now locks §2.1–2.5.** `docs/LAYOUT_LOCK.md` documented those headers
from the start but the guard never enforced them — **5 locked tables became
10.**

---
### LD-86 · R-31 — the CYCLE GATE: §2.0b finally feeds selection

**Jeff, 2026-08-31:** *"2.0b Cycle position — you're pointing this out earlier.
I'd say let's give it a go"*, then *"I mean we're talking about adding it to
the selection criteria."*

**Now criterion 7 of `docs/SELECTION_CRITERIA.md`** — and flagged there as the
one criterion Jeff RATIFIED rather than AUTHORED, which is why it leads the
2026-09-05 review agenda.

#### What it fixes

**§2.0b was computed, published, and consumed by nothing for two days.** LD-74
required it to be PRESENT on a selecting edition; no code read it.

**NZDJPY is the case.** On 2026-08-30 the two views disagreed about one pair
and we acted on one while printing the other — §2.0 said spread 4.12, select
it; §2.0b said NZD is **IN THE PAST**. **The cycle view was right:** JPY leads
NZD on Production, Spending AND Employment, and NZD's whole lead came from
Inflation and Rate on Jun/26 data two months old.

**The tally is structurally blind to this.** Its weights are Inflation 3 and
Rate 3 against Production/Spending/Trade at 1 each — **dominated 6:3 by the END
of Jeff's causal chain**, so a currency scores highest exactly when its move is
finished.

#### The rule

```
tilt = (long leg's position − short leg's) / 2      in [−1, +1]
       BUILDING +1 · aligned 0 · IN THE PAST −1
confluence = core × (1 + 0.25 × tilt)               bounded ±25%
```

**A MULTIPLIER, not a fourth term — and the reason is F-69.** Both shapes were
costed and produced the same three pairs, but **a fourth term dilutes ROOM
from a third of the score to a quarter.** Criterion 4 is the term that must
not weaken. **The multiplier scales a setup the core has already judged; it
cannot rescue a pair with no room.**

#### The finding on first run

**Not one candidate scored positive.** The three BUILDING currencies are CHF,
AUD and USD — **every one of which we are short or not using.** The
distribution is a healthy 3/3/2, so this is a fact about the week rather than
a miscalibrated gate. **If it repeats, the ±0.40 thresholds are wrong.**

**GBPAUD takes the worst tilt on the board (−1.00)** — long GBP (IN THE PAST)
against AUD (BUILDING) — **and survives on room**, 462 favourable pips, the
most of any candidate. **That is criterion 4 doing exactly what Jeff
described: a lesser case with room beating a better one without it.**

#### The guard

**R-31 `assert_cycle_gate_live()`** fails the render if §4.2's Cycle column
carries prose instead of a signed tilt. **A descriptive cycle column is
precisely what §2.0b looked like while feeding nothing** — the guard exists so
that state cannot return silently. Verified: fires on all 8 rows when the
tilts are stripped.

---
### F-72 — I blamed TE for my own off-by-one. **F-71 WITHDRAWN.**

**Jeff, 2026-08-31, with a screenshot:** *"How TE is wrong when I can see the
screen August 31, 2026 9AM?"*

**TE was never wrong.** His screen showed `Monday August 31 2026` with ANZ
Business Confidence at 09:00. Our capture stored it as 1 September. **The
parser was a day out.**

#### The bug

`parse()` tracked the date from a running `<th>` heading. **On a TE country
page every date heading appears TWICE**, so `cur` advanced to the next day
before the rows beneath it were read. Meanwhile **each row carries its own
date in its first cell** — `class=' 2026-08-31'` — which we ignored.

**Fix: read the row's own date; fall back to the heading only if absent.**

#### What I got wrong, and the tell I walked past

**I had already "proven" TE wrong from capture history** — the actual appeared
between two captures, 23 hours before TE's stated time, therefore the date
must be stale. **The logic was sound and the premise was mine.** I never
questioned the stored date because I had written the code that produced it.

**THE TELL: three other rows on the same screen converted cleanly at UTC+8 and
only this one was off by a whole day.** When one row disagrees and its
neighbours agree, **suspect the parser, not the source.** A source-wide defect
shows up source-wide.

**F-71 is WITHDRAWN.** There was no TE scheduling defect. The four rows R-30
flagged — two "stale date", two "F-1 suspects, do not use" — **were all the
same parser bug**, and the two I told Jeff not to trust (CAD budget balance,
CHF KOF) were sound all along. After the fix: **8 of 8 rows match his screen
exactly, and R-30 reports no anomalies at all.**

#### R-30 is KEPT, on its merits

The audit itself is correct — an actual really cannot predate its own release,
and that check has value. **What was wrong was the conclusion I drew from it.**
R-30 now stands as a genuine cross-check rather than as evidence against TE,
**and its first honest run is a clean one.**

**Third time in this session that a "source defect" turned out to be ours
(F-45, F-63, F-72).** The prior should be: *when our data disagrees with what
Jeff can see on screen, we are wrong until proven otherwise.*

---
### F-70 — TWO CHANNELS reach the currency, and they carry OPPOSITE SIGNS

**Jeff, 2026-08-31:** *"The inflation of CHF is expected to increase from
0.4% to 0.7% why is it bad for the currency?"*

**It is not.** And when I confirmed the fix he stated the whole principle in
one sentence:

> *"USD Unemployment Rate 4.1% → 4.2% BAD. This is correct because decreasing
> unemployment is better for the economy. **But in Inflation we want it
> increasing because it poses for Interest Rate Hike**"*

| Channel | Series | Route to the currency | Sign |
|---|---|---|---|
| **ECONOMIC HEALTH** | unemployment, claimant count, jobless claims | **directly** | **LOWER is better** |
| **RATE** | inflation, CPI, PPI | **through the central bank** | **HIGHER is better** |

**Both read as "bad news" in plain language.** That is exactly how a single
flat `LOWER_IS_BETTER` list came to hold both — and **inverted every
rising-inflation forecast for every currency.**

**The destination is the same; the ROUTE decides the sign.**

#### The whitelist always knew

```
EUR 2.9%  >2% & rising   GOOD     CHF 0.4%  <2% & falling  BAD
GBP 2.9%  >2% & rising   GOOD
NZD 4.1%  >2% & rising   GOOD
CAD 3.0%  >2% & rising   GOOD
```

**CHF's BAD describes its CURRENT STATE** — 0.4% and falling, below the SNB's
0–2% floor. **0.4% → 0.7% is rising off the floor toward the mandate, which
is rate support.** This is Jeff's causal chain (2026-08-29, LD-72): inflation
predicts the rate decision, and the rate decides strength.

#### Not unconditional

**Inflation helps only while it argues for tightening.** Far above a bank's
own ceiling it becomes a policy problem — stagflation is not currency-
positive. The fix is **mandate-aware**, using `rate_model.MANDATE` (LD-23:
*"MANDATES ARE NOT ALL 2%"*) plus a 1.5pp overshoot tolerance. **AUD 3.5% →
5.5% against a 2–3% band correctly grades BAD.**

#### What it cost

**CHF's forward score swung −2.14 → +0.86, a 3-point correction**, landing on
pairs that matter:

| Pair | Wrong forward spread | Corrected |
|---|---|---|
| **CADCHF** (held) | 6.70 | **3.70** |
| **GBPCHF** (re-run ranked #1) | 6.95 | **3.95** |
| EURCHF | 8.19 | 5.19 |

**GBPCHF's #1 ranking was built on a spread 3 points too wide.** And CADCHF's
case is materially weaker than reported an hour earlier — **the bug was
flattering a pair we hold.**

**BASE scores are untouched.** CHF's −0.64 comes from released data (0.4%,
falling) and is correct; F-70 only ever affected the FORWARD adjustment.

#### The guard

**R-28 gained a CHANNEL CHECK.** Every whitelist row must sit in exactly one
channel: an Inflation-category row that is not in the rate channel, or any row
in both, fails the audit. **Verified by reintroducing the bug — 16 problems on
8 inflation rows.**

**Pricing regressions now 24**, including CHF rising off the floor, GBP rising
above target, and the AUD overshoot that must still grade BAD.

---
### LD-85 — the FORWARD-ADJUSTED tally (§2.0c), k = 0.50

**Jeff, 2026-08-31:** *"the market is forward looking. if we react after the
data has released then we are already late. that's the whole point of this
market Sentiment. To be able to foresee where the price is going. not
following the price … isn't it better to price in early than to react after?"*

#### I argued against this and I was wrong

**I cited LD-3 — "the release is truth, the forecast is a prediction" — to
resist weighting the forecast. That misuses the rule.** LD-3 is a SOURCING
rule: never dress a forecast as a print, always name the issuing agency for a
released value. **It says nothing about how much a forecast should move a
forward-looking bias.** Recorded here because the next session will meet the
same temptation.

#### The formula

```
adjusted(ccy) = base(ccy) + k × Σ( verdict × category_weight )
```

**Weighted, not flat — Jeff's second point:** *"not all indicators do have the
same weight so we need to consider balancing the scores in that sense."* The
first costing was flat and let a Mfg PMI (w1) move the tally as much as an
Inflation print (w3). **The adjustment now runs through the tally's OWN
weights** — Inflation 3, Rate 3, Employment 2, Production/Spending/Trade 1 —
so one taxonomy governs both halves.

#### Why k = 0.50

**It is the largest value at which no currency's rank is decided by a single
forecast.**

| k | Largest single-row move | Effect |
|---|---|---|
| 0.25 | 0.75 | re-scores, never re-ranks — barely worth having |
| **0.50** | **1.50** | **EUR takes the top; JPY clears AUD** |
| 0.75 | 2.25 | CHF's lone inflation print drops it past USD alone |
| 1.00 | 3.00 | a forecast counts as much as a release; NZDJPY inverts |

**This is a testable claim, not a preference.** §4.0 records the projections in
advance, so **Saturday's retrospective grades k against what actually
printed.** Jeff: *"we can revisit it later after this week's market close."*
**Revisit after 2026-09-04.**

#### Rules that keep it honest

1. **The base is never overwritten.** §2.0c shows Base and Forward side by
   side, so the forecast's contribution is always visible.
2. **Released rows are EXCLUDED** from the adjustment — once a print lands it
   is in the base via `score_model`, and adjusting it too double-counts.
   Monday: JPY Retail Sales and NZD ANZ Business Confidence dropped out.
3. **Selection still ranks on the BASE** until Jeff says otherwise. §2.0c is
   published and read; it does not silently re-rank pairs.

#### The board on 2026-08-31

| CCY | Base | Forward | Driver |
|---|---|---|---|
| EUR | +5.05 | **+6.05** | PMI + retail sales, both w1 |
| CAD | +6.56 | **+4.56** | −4: employment change is w2 |
| JPY | +0.86 | **+2.36** | +3 from three w1 rows — broad but light |
| CHF | −0.64 | **−2.14** | **one inflation print, w3, carries all of it** |

**CHF is the row to watch.** A single w3 forecast moves it 1.50 at k=0.50 and
would move it 3.00 at k=1.00. **A weighted adjustment concentrates risk in
exactly the rows most likely to surprise.**

**USD's two employment prints annihilate** — NFP +2 and Unemployment −2, both
w2, same release, same minute. Net zero, which is arguably the honest reading
of a mixed report.

#### Interaction with R-16

**A forward score quoted bare in prose FIRES R-16**, which knows only base
values. **That is the right default — it forces the label.** R-16's message now
says so explicitly, so the next session labels the number instead of changing
it to silence the guard.

---
### F-69 · R-29 · LD-84 — the BENCH was ranked on half the criteria

**Jeff, 2026-08-31:** *"did we look at the technicals of the benched pairs?"*

**We had not.** §4.5 ranked alternates on **macro spread and event risk**. Its
`Conf` column carried **no room, no falsifier, no structure** — criterion 4 of
LD-84, the technical gate, was never applied to the bench at all.

**This is LD-73 reproduced one week after it was fixed.** GBPUSD was selected
at 94.4% of range with a LONG bias and lost 110.9 pips; the room gate was
built so it could not happen again — **and then was wired into the primaries
only.**

#### What the gate found

| Pair | Bias | In range | Room | Against | R:R | Old rank |
|---|---|---|---|---|---|---|
| **AUDCAD** | SHORT | 88.9% | **199** | 25 | **7.98** | 3rd |
| GBPJPY | LONG | 68.0% | 322 | 682 | 0.47 | **1st** |
| CADJPY | LONG | 74.2% | 146 | 419 | 0.35 | 4th |
| GBPCHF | LONG | 80.3% | **63** | 257 | 0.25 | **2nd** |
| EURCHF | LONG | 82.3% | **41** | 193 | 0.21 | 5th |

**The two highest-ranked bench pairs were the two with the least room.**
**GBPCHF carried the BEST macro spread on the bench (+5.95) and sat at 80% of
range with a LONG bias** — the GBPUSD setup exactly, and the old ranking would
have offered it as the first replacement.

**A bench pair is entered MID-WEEK, with less time to work than a primary. It
deserves MORE scrutiny, not less.** Ranking it on half the criteria inverted
that.

**R-29 `assert_bench_room_gated()`** fails the render when §4.5's table has no
Room column. It checks that the gate was APPLIED, not that the numbers are
good — grading them is reading, not running.

#### LD-84 — why the criteria now live in one file

**Jeff:** *"let us review what was the criteria I told you about selecting
high probability pairs? Can you pull up some history where I specifically
instructed on how do we select our primary and seconday pairs?"*

**Pulled from the transcripts, USER messages only, quoted verbatim.** Six
rules stated across eleven days, and **they are internally consistent** — the
problem was never contradiction, it was dispersion. They lived across LD-19,
LD-29, LD-73 and LD-75, and **nobody could read the whole at once.**

**That dispersion IS the root cause of F-69.** A rule you cannot see whole is
a rule you apply in pieces.

**`docs/SELECTION_CRITERIA.md`** now holds all six with their dates and the
order of operations — plus a section recording **what Jeff has NOT said**, so
the numeric room bands stay labelled as MY proposal rather than hardening into
his rule by repetition.

**The one-line version, in his words:** *"other pairs with the same or a
little bit lesser conviction … but with room to move in the favor of our
bias."* **A lesser spread with room beats a better spread without it.**

---
### F-68 · R-28 — the THRESHOLD column is DIRECTION, never history

**Found while building the 2026-08-31 edition — one day after F-66 fixed the
same class.**

NZD ANZ Business Confidence fell **56.1 → 53.7**, and I updated the row's
threshold to `<Prev` **to describe that fall**. But `lower_is_better()` reads
`<Prev` as *"for this series, LOWER IS BETTER"* — so **a confidence MISS
graded as a BEAT.**

**THE THRESHOLD COLUMN DOES ONE JOB: which direction favours the currency.**
**The VERDICT column carries what actually happened.** Conflating them
silently inverts the grade.

| Column | Answers | For ANZ Business Confidence |
|---|---|---|
| `threshold` | which way is GOOD? | `>Prev` — confidence rising is good, **always** |
| `verdict` | what happened? | `BAD` — it fell |

#### It was not one row

**R-28 `pipelines/audit_direction.py` checked all 23 `*Prev` rows and found
SIX more with the same defect** — every one written to describe the last move:

```
GBP/JPY/NZD Balance of Trade     '<Prev'  ->  '>Prev'  (a bigger surplus is good)
AUD/NZD/CHF Unemployment Rate    '>Prev'  ->  '<Prev'  (lower unemployment is good)
```

**The pattern was systematic, not an accident.** Writing the threshold to
match the direction a series happened to move reads naturally and is wrong
every time the series reverses.

**Scores were unaffected** — verdicts drive the tally, thresholds document the
grading — **which is exactly why it survived undetected.** Nothing in §2
moved; only §4.0's release grading inverted.

**Run `audit_direction.py` whenever a whitelist row is updated.**

---

### R-27 v2 — one blessed shape PER EDITION TYPE

**Jeff's call, 2026-08-31**, after R-27 fired on Monday's §0.

**That firing was the guard working, and the finding underneath is real:**
§0 legitimately differs by edition type. **A WEEKEND edition GRADES the
expired week** (`Pair | Bias | Lock ref | Fri close | Week | Outcome`); **a
MONDAY edition TRACKS the live set** (`Pair | Bias | Entry ref | Now | Move |
Falsifier | Distance`). Same section number, two purposes.

**Rejected: forcing one shape**, which would have put a live Monday price
under a column headed *Fri close*. **Rejected: exempting §0**, which is where
the pair table lives and is the section most worth protecting.

**`docs/LAYOUT_LOCK.json` now keys on the frontmatter `type:`.** An edition is
checked against its OWN type's blessed shape, so **WEEKEND cannot drift into
MONDAY and neither can drift at all.** Verified: drift within a type still
fires.

---
### LD-82 · R-27 — the SHAPE of the whole edition is locked

**Jeff, 2026-08-30, for the SECOND time in one session:** *"again don't
change the report format wihtout my approval. if there's a need to change
then let me know."*

**R-24 worked — §4.0's columns held. And the format changed anyway**, because
§4.6 **GAINED TWO TABLES** and §4.6 was not in `LOCKED_TABLES`.

**A lock that lists the tables which already broke is a patch over one
incident, not a lock.** What was asked for is that the report LOOK THE SAME
unless Jeff approves otherwise — so the guard has to notice a table that did
not exist before, ANYWHERE, not only a column changing in a table already
thought about.

**The content was requested; the tables were not.** *"isn't there any changes
to the Bias?"* is a question about the bias. It is not permission to
restructure the section that answers it. **Same distinction as LD-80:
highlighting is not restructuring.**

**R-27 `pipelines/layout_shape.py`** records every section's shape — how many
tables and each one's columns — in `docs/LAYOUT_LOCK.json`, and fails the
render when it changes. **Verified against the real defect:**

```
FATAL (R-27/LD-82): the report SHAPE changed.
  §4.6 GAINED a table: CCY | Good | Bad | Neutral | No cons. | Net
```

**Re-blessing is a separate deliberate command** (`--bless`), never a render
side effect, so a baseline cannot be silently rewritten by the thing it
guards.

---

### F-67 · LD-83 — coverage is a WINDOW problem, not a NAME problem

**Jeff, 2026-08-30:** *"please please make sure we capture the data
completely in TE if we need to do a fuzzy matching due to the mismatches then
let's take a look on it."*

**33 of 71 whitelist rows matched nothing.** The reflex reading is a NAME
problem — loosen the matcher. **That reading was wrong.**

**TE's GLOBAL page spans about 10 days. The COUNTRY pages span a month.**
CH and NZ already had country pages and showed 10 and 13 distinct dates;
**CAD had 4.** The unmatched rows release LATER IN THE MONTH than the global
page reaches. They were not unmatchable — **they were not in the capture at
all**, verified by searching the raw rows for each one.

**F-67: fetch every whitelisted currency's country page**, not just the two
the global page omitted entirely. **505 → 915 rows; coverage 38 → 66 of 71.**
USD went 92 → 276 rows, CAD 17 → 61.

#### Why NOT fuzzy matching

**The one row that genuinely looked like a name problem is the argument
against it.** AUD `Inflation Rate YoY` matches nothing, while the capture
holds **TD-MI Inflation Gauge MoM** and **Consumer Inflation Expectations**.
A fuzzy matcher binds our CPI row to one of those.

**That is LD-59 exactly** — *"they are 2 different indicator. So they have 2
different reading."* **A loose match does not report an absence; it INVENTS a
presence**, and a wrong value is worse than a missing one because nothing
downstream can tell.

**Matching stays exact.** The remaining 5 rows were each checked by hand and
are genuine absences — quarterly or monthly series outside even the
month-long window.

#### LD-83 — expectancy carries the load instead

**Jeff:** *"one thing that could help us determine the usual schedule of the
indicator in TE is by putting when the indicator is usually released in the
Month. for example PMI. it's always being released during Week 1."*

**Confirmed by the data — every manufacturing PMI we track lands W1.**

`pipelines/release_week.py` reduces observed release dates to a week-of-month
(days 1–7 = W1 … 29+ = W5) across every capture kept on disk. **It is a
histogram of what we have SEEN, not a schedule TE publishes** — it sharpens
as captures accumulate, and a row seen once is labelled low-confidence.

**`--due` is the view that earns its keep before an edition:** an indicator
whose usual week is NOW but which is absent from the newest capture. **A
prompt to look, never proof of a gap** — schedules move.

**This is the durable answer to the coverage question.** Knowing a row is DUE
is what makes an empty slot legible as a gap rather than a quiet week — which
is precisely what a looser matcher would have destroyed.

---
### F-66 · R-26 — a COMPARISON is not a DIRECTION (again)

**Jeff, 2026-08-30, once F-65 had put real numbers in the consensus column:**
*"now we have the consensus 1. why is it still unscored?"*

Fair question, and answering it required grading all 26 rows — at which
point two came out backwards:

```
USD Unemployment Rate   prev 4.1%   cons 4.2%   -> GOOD    WRONG
```

**`market_pricing()` returned GOOD whenever `previous < consensus`, for every
indicator.** But BELOW is only good where LOWER IS BETTER. **Consensus
expecting US unemployment to RISE is BAD for USD**, and the function called
it GOOD.

**THIS IS F-62 / LD-71 A SECOND TIME.** `graded_signed()` exists precisely
because `>Prev`/`<Prev` describe the COMPARISON, not the direction of
goodness. `market_pricing()` was written before that lesson and never
received it. **When a lesson is learned in one function, go and look for the
same shape in every other function that compares two numbers.**

**The whitelist already knew the answer** — the threshold column encodes it:

```
("Employment","US","Unemployment Rate", ..., "<Prev","GOOD")
("Employment","AU","Unemployment Rate", ..., ">Prev","BAD")
```

So the fix is not new judgement. **It is consulting what we already wrote
down.**

#### F-66b — `<` means two different things

| Threshold | Meaning | Carries direction? |
|---|---|---|
| `<Prev`, `>Prev` | a COMPARISON against the last print | **YES** |
| `<0%`, `<2% & falling` | a STATE description — "currently negative" | **NO** |

**JPY Household Spending −3.3% → −1.6% is a SMALLER contraction — a
recovery.** Reading `<0%` as "lower is better" grades that improvement as
BAD. Only a threshold naming the PREVIOUS PRINT carries direction; everything
else falls through to the series name.

#### F-66c — markdown changed a NUMBER

**`'**75.1K**'` parsed as 75.1 while a plain `'15.8K'` parsed as 15800.** The
K/M/B suffix test was anchored with `$`, which the trailing `**` defeated. A
**59K deceleration graded GOOD** because the two sides of the comparison were
scaled differently.

**Same class as F-65b: a formatting artefact silently changing a VALUE, not
just its display.** The suffix is now anchored to the digits and markdown is
stripped before parsing.

#### The guard

**`pipelines/test_pricing.py` (R-26) — 20 cases, every one graded BY HAND
first and then checked against the code, never the reverse.** It covers both
reversed rows, both markdown forms, the trade balances, and the
must-return-`None` case where no consensus exists.

**Run it whenever `market_pricing()`, the threshold column, or §4.0's number
formatting changes.**

---
### F-65 — consensus and forecast were never parsed at all

**Jeff, 2026-08-30:** *"can you check again the consensus and forcast in TE?
its very unsual that we can't get any data considering these news will be out
tomorrow"*

**He was right to disbelieve it, and my explanation had been wrong.** §4.0
showed `— / —` in nearly every Cons / Fcst cell and I explained it away as TE
not having published consensus yet. **The columns were in the HTML we had
already saved.** `capture_calendar.parse()` read `cells[:4]` to find the event
NAME and stopped; `Actual`, `Previous`, `Consensus` and `Forecast` sit
immediately to the right and were discarded before anything downstream could
see them. The capture schema had four fields: date, time, iso, event.

**The tell:** `— / —` on EVERY row is not data, it is a parser returning
nothing. **A field empty for one event is a fact about that event; a field
empty for all 505 is a fact about US.**

#### F-65b — the blank Actual cell is the signal, and the first fix deleted it

The first cut stripped leading empty cells before mapping the four columns.
**Wrong in the most dangerous possible direction:** TE emits an EMPTY
`<td class="calendar-item">` for Actual when an event has NOT released.
Dropping it shifted every column one left, so **PREVIOUS was read as ACTUAL**
and every unreleased event acquired a print it never had — **F-1 manufactured
by our own parser rather than by TE.** It briefly showed ISM Manufacturing
with an actual of 55.6 for a release that is still two days away.

**Fix:** select the value cells by their `calendar-item` class and map
positionally **without dropping blanks**. An empty Actual is data.

```
ISM Manufacturing PMI, 1 Sep, from the saved HTML:
  calendar-item ''      <- Actual, EMPTY, not yet released
  calendar-item '55.6'  <- Previous
  calendar-item '55.3'  <- Consensus
  calendar-item '55'    <- Forecast
```

#### F-65c — ISM and S&P Global are two different surveys

**§4.0 published `ISM Manufacturing PMI` carrying 53.2. That is the S&P
Global Mfg PMI's consensus.** ISM's previous is **55.6** — a 2.4-point error
on the single highest-impact US print of Tuesday. Both release on 1 Sep,
fifteen minutes apart, and token matching cannot separate them because
"manufacturing pmi" is a substring of both.

**`PIN` in the §4.0 rebuild maps the ambiguous names to exact event keys.**
Where two surveys share a name fragment, the row names the survey.

#### What this changed in the published edition

**25 of 26 `Current actual` cells were already correct** — they match TE's
Previous. The defect was almost entirely in Cons / Fcst, plus the one ISM
conflation. **28 cells changed.** Several matter for the week's bias:

| Event | Previous | Consensus | Reading |
|---|---|---|---|
| **USD Non Farm Payrolls** | −23K | **45K** | consensus expects a large positive swing |
| **USD Unemployment Rate** | 4.1% | **4.2%** | a rise is expected |
| **CAD Employment Change** | 75.1K | **15.8K** | sharp deceleration expected |
| **JPY Retail Sales YoY** | 0.5% | **3%** | a big acceleration is priced |
| **USD ISM Manufacturing** | 55.6 | **55.3** | roughly flat |

**These are what §4.6 grades a surprise against.** With the column empty, a
surprise could not be measured at all — which is why every row read UNSCORED.

**LD-3 still holds:** TE is the SCHEDULE and CONSENSUS authority. **The actual
value of a released print still comes from the issuing agency.**

---
### LD-80 · R-24 — an approved layout is LOCKED

**Jeff, 2026-08-30:** *"4.0 why we change the format of the table? I only
asked to highlight high impact news why we're changing table formats again and
again? once the report layout is approve we should lock it up and not just
changing the report format every now and then. It's important for an analyst
to consistently look at standard report."*

**The evidence is worse than the complaint.** §4.0's header changed in **four
consecutive editions**, and the fourth dropped from seven columns to four —
**silently taking `Current actual`, `Cons / Fcst` and `Market priced` with it,
which is the entire LD-63 pricing read.** Nothing flagged the loss.

| Edition | §4.0 columns |
|---|---|
| 27 Aug | `When · CCY · Indicator · Current actual · Cons / Fcst · Market priced · Status` |
| 28 Aug | same seven, **all four right-hand headings renamed** |
| 29 Aug | same, **Outcome** bolded |
| **30 Aug** | **`When · CCY · Indicator · Note`** — **four columns** |

**THE RULE: content changes freely; STRUCTURE DOES NOT.** Column count, order
and headings are fixed until Jeff approves a change. **A request to HIGHLIGHT
something is not a request to RESTRUCTURE it** — highlighting is a renderer
concern (LD-77), the column set is a layout concern.

**`docs/LAYOUT_LOCK.md` holds the locked headers** for §2.0, §2.0b, §2.1–2.5,
§4.0, §4.3 and §4.5, and the procedure for changing one (ask Jeff; update that
file in the same commit).

**R-24 `assert_layout_locked()`** compares each locked table's first header row
against `LOCKED_TABLES` and fails the render on a mismatch. A prefix match — a
table may gain trailing columns, never lose, reorder or rename. **Verified
against the live defect** rather than trusting a pass:

```
FATAL (R-24/LD-80): §4.0 table header changed.
  locked: When (PHT) | CCY | Indicator | Current actual | Cons / Fcst | Market priced | Status
  found : When (PHT) | CCY | Indicator | Note
```

**Every one of the four variants was written in good faith while doing
something else.** That is precisely why it needs a guard and not a resolution.

---
### F-62 · F-63 · F-64 — three source-alignment defects, 2026-08-30

**All three were found by Jeff, not by a guard.** Recorded here because the
first two were previously recorded ONLY in commit messages, and Jeff's
observation was exact: *"TI happened already before and it happened again
now."* A finding that lives in `git log` is not documented.

#### F-62 — the row held the FORECAST, not the actual

**USD Building Permits MoM Final read 5.0%. TE's actual is 4.3%; 5.0% is its
CONSENSUS AND FORECAST column.**

**The tell I walked past:** our "sourced" figure matched the published
consensus EXACTLY. **When a value you claim to have sourced from an agency
lands precisely on the forecast, re-verify it** — that is the inverse of
F-1 and it deserves the same reflex.

**Still unresolved, and the exemption says so instead of asserting:** Census
CB26-127 of 18 Aug states 1,443,000 / "5.0 percent above"; TE's calendar
carries a Final on 25 Aug at 1.433M / 4.3%. Both are internally consistent
against a June of 1,374,000 — they differ only on the July level. **The row
follows TE's ACTUAL because that release demonstrably happened.**

#### F-63 — a UTC date filtered against a PHT window

**The capture stores UTC; the LD-66 window is PHT.** `whitelist_events()`
filtered the raw date and converted afterwards, so **every event after 16:00
UTC — the entire Asian session — fell on the next PHT day and was dropped**
before conversion. JPY Retail Sales at 23:50 UTC Sun is 07:50 PHT Mon.

**Convert first, filter second.**

#### F-64 — "Mfg" never matches "manufacturing"

**Our whitelist writes `Mfg`; every calendar writes `manufacturing`.** Token
matching needs each whitelist word present, so **seven of eight PMI rows were
invisible to §4.0.**

**This is F-38 again** — 11 rows that matched nothing, four days earlier.
**Same defect, same discovery route: Jeff reading.**

| Mechanism | Purpose |
|---|---|
| `week_ahead._SYN` | expands abbreviations WE introduced (`mfg`, `svcs`, `chg`, `conf`, `prel`, `ex`) |
| `week_ahead._DROP` | drops vendor words the calendar omits (CHF's `UBS`) |
| **`pipelines/coverage_audit.py`** | **R-25 — proves every row is matchable, rather than waiting to be told** |

**A synonym list only fixes abbreviations already tripped over.** The audit is
the durable answer: over a wide window, **a row that matches NOTHING is not
quiet — it is unmatchable.** Run it whenever the whitelist changes or a
source renames a series.

**First run, 2026-08-30:** 37 of 71 matched in a 28-day window; **zero
unmatchable**. Six apparent misses were verified by hand as `_NOT` filters
working correctly (MoM vs YoY, prel vs Final, BRC vs ONS).

---

### LD-81 — a finding is not recorded until it is in the SPEC

**Jeff, 2026-08-30:** *"are we documenting these changes and corrections? TI
happened already before and it happened again now."*

**F-62, F-63 and F-64 existed only in commit messages — zero occurrences in
`REPORT_SPEC.md` or `CLAUDE.md`.** A session resuming next week reads the
spec and the handover, not `git log`. **A finding in a commit message is a
receipt, not documentation.**

**Every finding lands in THREE places, in the same commit:**

1. **The edition's §8** — what happened, that week
2. **`docs/REPORT_SPEC.md`** — the durable rule, if it changes behaviour
3. **A guard or an audit** — so it cannot recur silently

**The commit message is the fourth, not the first.**

---
### LD-77 · LD-78 — high-impact events are visible at a glance

**Jeff, 2026-08-30:** *"can you highlight the High Impact news in 4.0? So that I
can get a sense even if I just scan the report"* and *"make our Market Sentiment
report more lively Aesthetically"*.

**§4.0 was a flat table** — a central bank decision and a consumer-confidence print
looked identical, so the reader had to READ every row to find the two that can
reprice a currency.

| Tier | Matches | Treatment |
|---|---|---|
| **CRITICAL** | interest rate decision, rate statement | **red left rule + tinted row** |
| **HIGH** | NFP, inflation rate, unemployment rate, employment change, GDP | **amber left rule + tinted row** |
| normal | everything else on the whitelist | plain |

**The tiers match the weights `selection_gates.py` already uses (LD-73)**, so the
table and the event-risk score cannot disagree about what counts as high impact.

**Scoped to §4.0 only.** Elsewhere an *"inflation rate"* row is a DATA row, not a
scheduled event — tagging it there would be noise. A legend is emitted once,
under the §4.0 heading.

**LD-78** is the general lift: rounded table wrappers, uppercase mono column heads,
very light zebra striping, row hover, more section rhythm. **No new hues** — the
palette that already existed is simply used properly.

---

### LD-71 · LD-72 — scoring v1 GRADED (see `docs/SCORING_BASELINE.md`)

**The full specification lives in `docs/SCORING_BASELINE.md`** — weights, the four
graded rules and their divisors, the worked example, the baseline board, and
the numbered list of what v1 does not do. **That file is the starting line: every
future scoring change is measured against it.**

The short version:

- **LD-71** — an indicator returns a MAGNITUDE in [−1,+1], not GOOD/NEUTRAL/BAD.
  **The rule gives the magnitude; the VERDICT COLUMN gives the sign.** Ceiling slots
  fell 26 → 13. **21 rows keep three-state on purpose** — several are Jeff's
  hand-specified rules (LD-57, LD-58) and LD-59 governs them.
- **LD-72** — §2.0b publishes the causal chain as a VIEW: LEADING (Production,
  Spending, Trade) against CONFIRMING (Employment, Inflation), each normalised
  to its own maximum. **A positive gap means the rate case is BUILDING; negative
  means the strength has ALREADY HAPPENED.**

---

### LD-70 — the weekly RETROSPECTIVE is its own artifact

**Jeff, 2026-08-29:** *"§10 the retrospective shouldn't be there. I like the
Week One Retrospective template so let's keep it for our weekly review."*

**The daily edition ends at §9.** A retrospective is not a section of a day's
report — it reviews a WEEK, it is written once a week, and it has a different
audience question: *how did we do*, not *where is price going*.

**It also duplicated badly.** On 2026-08-29 §10 carried 5,676 characters of
retrospective that was a WEAKER copy of the standalone artifact published the
same day — the artifact had the day-by-day tables, the gold/BTC lens and the
correlation work; the section had none of them.

| | Daily edition | **Weekly retrospective** |
|---|---|---|
| Cadence | every session | **once, Saturday** |
| Sections | §0–§9 (+ folded §11) | **its own template, no § numbering** |
| Question | where is price going | **how did we do** |
| Form | `reports/YYYY/Qn/DATE_market-sentiment.md` → render | **standalone HTML artifact** |

**The template is the "Week One Retrospective" published 2026-08-29** and it
covers two categories, four questions each:

**1. The report build** — (a) what went well, (b) problems seen and resolved,
(c) what to improve, (d) what to continue.

**2. The market analysis** — (a) the selection process and the factors behind
the bias, (b) the day-by-day record from lock to close **in three lenses: FX,
gold, BTC** — with WHY it moved for and against, (c) how to foresee direction
better, (d) best practices to continue.

**Rules that make it worth reading:**

- **Recompute every figure before publishing it** — the 29 Aug retrospective
  verified all sixteen against the bars before it went out.
- **State the honest scoreboard first**, before any explanation of it.
- **Directional pips are NOT P&L** (LD-4). Say so in the footer, every time.
- **Small-sample statistics are labelled as descriptive**, never as evidence.
- **Name what the user caught that the guards did not.** That list is the
  most useful part of the review.

---

### LD-69 — process narrative belongs in §7, not in the read

**Jeff, 2026-08-29:** *"I asked for the report to be clean and less process
narrative. But I got tired of complaining so I just accepted it. Why don't we
do this then, let's place your process narrative comments in a dedicated
section of the report that can be folded."*

**§0–§6 are the MARKET READ.** Prices, figures, drivers, bias. A finding is
named there ONLY when it changes what a number IS — *"the row held June's
figure; corrected to +5.0%"* — and then in one clause, never a paragraph.

**§7 METHOD NOTES carries everything else** — what broke, what was fixed,
which guard fired, what was not re-derived and why, pipeline changes. **It
already exists and it already FOLDS**, alongside §8.

**A §11 was built for this and then removed the same session.** Jeff: *"why
we can't put it in §7 though?"* — because §7 already IS this section:
*guards run before any figure was used*, *sourcing this run*, *not done, stated
plainly*. **Inventing §11 would have produced THREE folded build sections
with fuzzy borders instead of one clear one.** The fix was a placement rule,
not a new container.

**Why LD-27 never caught this.** It measured prose VOLUME as a share of all
blocks. **Its own docstring recorded the failure**: the edition Jeff called too
noisy scored **13.0%**, the one he was happy with scored **15.1%**. The metric
was measuring the wrong thing for six days while he stopped complaining.

**R-22 measures PLACEMENT instead** — build language (F-numbers, guard names,
pipeline filenames) appearing inside §0–§6. On 2026-08-29 that was **26 lines,
worst §4 with 10**. **Advisory, not blocking**: the line between a finding that
changes a number and a build log is editorial.

---

### LD-68 — direction × surprise: where the price is going

**Jeff, 2026-08-26:** *"my goal for this report is to somehow sense where the
price is going based on cobining our Macro indicators results and upcoming news"*

**§2 and §4.0 answer different questions. Price follows the second one.**

| | Question | AU CPI, 26 Aug |
|---|---|---|
| **§2** | which way is the data **moving** vs a fixed threshold | 3.8 → 3.5, cooling → **NEUTRAL**, tally unchanged |
| **§4.0** | how does it compare to **what was priced** | 3.5 vs 3.3/3.2 → **HOTTER** |

**The data cooled while beating expectations. AUDNZD +54 pips and held.**
**Price followed the SURPRISE, not the DIRECTION.**

| Direction | Surprise | Reading |
|---|---|---|
| supportive | hotter | **ALIGNED BID** — cleanest |
| supportive | colder | TENSION |
| weakening/neutral | hotter | TENSION — *AUD on 26 Aug* |
| weakening | colder | **ALIGNED OFFER** — cleanest |

**ALIGNED = the move is most likely to run. TENSION = the market must choose**
**which engine to trade**, and on 26 Aug it chose the surprise.

Computed by `pipelines/directional.py`; published as **§4.6**.

**⚠ IT DOES NOT FEED THE TALLY OR THE SELECTION.** It is a reading aid that
states a **LEAN, never a forecast**, and **every output carries its sample size.**
As at 2026-08-26 that sample is **n = 1** — the mechanism is standard FX, but
our own evidence is one observation. **Score every future release against it
and publish the record whether it confirms or not.**

---

### LD-67 — look at the WHOLE edition, not just the moving parts

**Jeff, 2026-08-26:** *"Everytime we build a new edition we should be looking
if every parts of the report have moved. we should be looking at it wholistically
and not just look at the moving parts."*

**Every edition, audit EVERY section — including the ones you expect to be
static.** On 26 Aug, **7 of 14 sections were carried and only 4 re-derived**, and
three of that day's four defects were in carried sections.

| Section | What must be re-derived EVERY run | What may carry |
|---|---|---|
| §0 | all prices, moves, distances | — |
| §1 | news sweep, **F&G capture** (R-17) | — |
| §2 | all 71 rows via `audit_te.py --fetch` | — |
| §2.6/§3 | **the rate figures if a bank has met** | policy commentary |
| §4.0 | events + consensus, **current week only** (LD-66) | — |
| §4.3 | **prices, distances** | the SELECTION (LD-29) |
| §4.4/§4.5 | **prices, range positions** | the ranking logic |
| §5/§6 | **prices, and any SCORE quoted** (R-16) | drawn levels, drivers |

**THE RULE FOR A CARRIED SECTION: REFRESH THE PRICES, KEEP THE ANALYSIS.**
Selection logic stays locked mid-week; the numbers under it never do.

**A carried section can go WRONG, not merely stale.** §4.4 called a LOCKED pair
REJECTED for three editions (F-52). §4.5 used a 5-day high as a 45-bar high and
**inverted a family ranking** (F-53). Neither was visible to any guard, because
**every guard checked a section against itself or its source — none compared
sections to each other.**

**`pipelines/whole_edition.py` (R-18) now does**, and fails the render on:
a pair both LOCKED and REJECTED, a falsifier that differs between sections,
or a current price that disagrees across tables.

---

### LD-66 — §4.0's window is THIS WEEK ONLY, and it rolls on Sunday

**§4.0 lists the whitelist events of the CURRENT Monday–Friday and nothing else.**
On **Sunday** the window rolls forward to the coming Mon–Fri: on **Sun 30 Aug**
§4.0 becomes **31 Aug – 4 Sep**.

**Why this is a rule and not a preference (F-48, 2026-08-26).** The 25 Aug
edition listed **EUR Retail Sales** and **EUR Unemployment** under Fri 28 Aug.
TE puts them on **4 Sep** and **1 Sep**. Both published as *UNSCORED — no
consensus*, and the missing consensus was read as a sourcing problem.

**It was not. TE had no consensus because the events were not in that week.**
Consensus firms up as a release approaches; an event two weeks out has none
yet. **Reaching past the current week manufactures exactly the empty cells
that then look like a data-quality defect.**

| Symptom | Wrong reading | **Right reading** |
|---|---|---|
| Row has no consensus | "source it from somewhere else" | **"is this event even in this week?"** |
| Row has no consensus AND no forecast | mark UNSCORED, publish | **WINDOW ERROR — investigate before publishing** |

**A row with neither consensus nor forecast in the current window is a window
error to investigate, never a row to mark UNSCORED and ship.**

**Corollary — the weekly cadence.** We monitor news **week by week**, not
open-endedly forward. The lookahead beyond Friday belongs in the WEEKEND PREP
edition, which is where the next week is scoped.

---

## LD-112 - THE FACT TABLES HOLD ACTUALS, THE SCORES ARE DERIVED

**Jeff, 2026-09-09:** *"I noticed that you were putting category scores in
our CSV rather than the Actual scores of these indicators. I would say we
need to store the actuals not our scores in them. If you want you can create
a separate CSV for your scoring."*

**HE FOUND THE ROOT CAUSE OF THREE FINDINGS.** F-91, F-94 and F-95 were all
the same failure with different names: a release had to be written into
**two** places - the ACTUAL into `score_model.ROWS`, the VERDICT into the
fact table - and nothing kept them in step. R-37 was built to compare those
two copies. **Storing the actual once and deriving the verdict removes the
gap rather than guarding it.**

| File | Holds | Status |
|---|---|---|
| `data/macro_indicators/*.csv` | **ACTUALS**, as published | SOURCE OF TRUTH |
| `data/derived/scores.csv` | +1 / 0 / -1 | **DERIVED, never hand-edited** |

**WHY A THRESHOLD ALONE CANNOT GRADE A ROW.** `>Prev` says which comparison
to make, never which direction is GOOD - lower unemployment is good, a lower
trade balance is not (F-70: two channels, opposite signs). `score_model`'s
VERDICT column carries that polarity and Jeff curated it row by row (LD-57,
LD-58, LD-59). So the derivation is:

    actual (fact table) x threshold + polarity (score_model) -> score

**That is still one authority per fact.** The actual lives in exactly one
place; the RULE lives in exactly one place; neither is a copy of the other.

**77 cells migrated, 0 unresolved.** The 8 Interest_Rate rows had no entry in
`score_model.ROWS` - their actual is the POLICY RATE, which `rate_model`
owns.

**BOTH R-37 CHECKS WERE RETARGETED, NOT DELETED.** The verdict check now
compares the fact table's actual against `score_model`'s actual; the rate
check compares the cell against the policy rate. The duplication has shrunk
but not vanished - `ROWS` still carries an actual - so the guard still has
work. **Proven by injecting a wrong actual: it fired.**

---

## LD-113 - THE GDP CATEGORY (weight 1)

**Jeff, 2026-09-09:** *"lets build a category for GDP. Give them a category
score of 1. Scoring would be: Actual > 0.5% is Good, < 0% is Bad. Actual in
between 0.5 - 0 is Neutral. Let's create a separate CSV file for this."*

**SOURCE:** TE `gdp growth rate qoq`. **LD-23 clears** - verified present for
all eight currencies across the capture archive.

**A FACT-CHECK CAUGHT MY OWN EARLIER CLAIM.** I had recorded GDP as "verified
available for all eight". Against the 8 Sep capture only **five** appeared,
and AU/CA/CH showed nothing. Widening to the whole archive found all three -
**the misses were TE's ~26-day horizon, not absence** (F-73). The claim was
right; the evidence I had cited for it was not.

**VINTAGE, for the 2026-09-06 edition.** Five of the eight Q2 prints landed
**before the capture archive begins (2026-08-17)**, so their actual is taken
from TE's PREVIOUS column on the scheduled revision. **That is a published
value, not a schedule row** - LD-3 forbids reading a value off an unreleased
row's FORECAST, which this is not.

| CCY | Actual | Released | Source |
|---|---|---|---|
| USD | 2.1% | 2026-07-30 | prev on final Q2 (30 Sep) |
| EUR | 0.6% | 2026-09-07 | 3rd est Q2 |
| GBP | 0.6% | 2026-08-14 | prev on final Q2 (30 Sep) |
| JPY | 0.4% | 2026-09-07 | final Q2 |
| AUD | 0.4% | 2026-09-02 | Q2 |
| NZD | 0.8% | 2026-06-18 | prev on Q2 (16 Sep) |
| CAD | 0.8% | 2026-08-28 | Q2 |
| CHF | 1.5% | 2026-09-03 | final Q2 |

**WEIGHT 1, AND CONFIRMING.** Q2 GDP publishes in September - by the time it
prints, the quarter it measures ended two months ago and every leading series
has already moved. It corroborates a read; it does not lead one.

**THE RANGE WIDENS: -9..+9 becomes -10..+10.** The calibrator is unchanged at
-5..+5, so **the forward half of the model now carries proportionally less of
the total.** Recorded here rather than discovered later.

**Spec amended under LD-105** with Jeff's wording inline. R-38 re-run: 0
disagreements.

---

## F-100 - INTEREST RATE CARRIED AN EFFECTIVE WEIGHT OF 3, NOT 1

The revamp set `Interest_Rate` to **weight 1** in `fact_tables.WEIGHT`. But
the fact table stored `raw x W_RATE` with `W_RATE = 3` - a **pre-revamp
leftover** - and `fact_tables` then applied its own weight of 1 to that
already-tripled number. **The category has been scoring at 3x the specified
weight since the revamp shipped.**

**INVISIBLE UNTIL THE ACTUALS MIGRATION.** While the CSV held a score,
nothing compared it against what the model would compute. Deriving the score
from the actual surfaced the factor of three **on the first run** - seven
rate rows, every one of them exactly 3x.

**This is precisely the class of bug LD-112 was requested to fix**, found by
the fix itself. `W_RATE` is now 1.

---

## F-101 - F-92 SURVIVED IN ONE FACT-TABLE ROW

`USD Durable Goods Ex Transp MoM`: actual **0.4%**, threshold **`>0.5%`**,
stored verdict **BAD**.

**0.4 sits between 0 and 0.5.** Jeff's band for this threshold shape - stated
four times in this session (JPY Machine Tool Orders, EUR Retail Sales, JPY
Household Spending, and now GDP) - is **above the line GOOD, below zero BAD,
in between NEUTRAL**. The stored BAD graded DIRECTION (0.4 < 0.5) on a rule
that tests **where the print sits**.

**F-92 was fixed in the calibrator and never reached the fact table.** The
two graded the same threshold shape in opposite ways for three days. Corrected
to NEUTRAL; USD Production moves -1.00 -> +0.00.

---

## F-102 - THE RBNZ GAP: A RATE SCORE THAT IS 100% BACKWARD-LOOKING

**Jeff, 2026-09-09:** *"NZD fell because the RBNZ statement read softer...
The tone should impact the score so we can recalibrate the rankings early.
If we need to create a another category for Interest Rate Expectations then
let's take a look on it."*

**THE DIAGNOSIS IS REAL AND IT IS NOT STALENESS.** NZD scored **+0.500, the
highest rate score on the board**, on three terms - REALISED, EXPECTED,
SURPRISE - that are **three views of ONE event**, the 2 Sep hike. PATH was
absent because the next meeting sat beyond TE's horizon, so a single
delivered decision took 100% of the weight through three separate doors.
The score was not old. It was **narrow**.

### Four options were considered. Three were unbuildable, and the reason matters

| Option | Why it failed |
|---|---|
| **Separate Expectations category** | TE schedules CB speeches/statements but publishes **no numeric actual for any of them** - verified 0 of 20 rows. Scoring it means reading prose, on all eight, every week |
| **Decay the REALISED term** | Needs each bank's **last decision date**. Visible for **2 of 8** |
| **Carry the last PATH forward** | Needs a prior forecast. Same horizon wall |
| **Log it and revisit** | **CHOSEN** |

**ALL THREE FIXES FAIL LD-23 IDENTICALLY** - an input available to some
currencies and not others. That is the same rule that rejected speech tone,
and the same shape as LD-101, where my own watchlist hid the entire yen bloc.

**DECAY WOULD ALSO HAVE FIRED BACKWARDS.** NZ and CA are the only two whose
last decision is visible, and it was **four days old** - the freshest on the
board. A decay rule would have penalised the two most recent decisions while
leaving six stale ones untouched, because their dates cannot be seen.

**THE SCORING WAS LEFT ALONE.** Renormalising over live terms asserts "we
cannot see the path", which is TRUE. Every alternative asserts something
stronger that cannot be sourced evenly. **No fix here was better than the
current behaviour**, and one week with n=1 is not grounds to change scoring
(LD-111: a component defect is n=1, a RANKING question needs three weeks -
this is the second kind).

**NEW: `pipelines/decision_history.py`.** Reports each bank's last and next
decision, days elapsed, and which currencies have no forward meeting. It
**changes no score**. It exists so the question can be answered on evidence
for eight currencies instead of two.

---

## F-103 - I CLAIMED TE's COUNTRY PAGES SPAN FIVE MONTHS. THEY DO NOT.

While trying to backfill decision history I reported that TE's country pages
carry roughly five months (2026-05-06 .. 2026-10-06) and that our three-week
archive was the only limit.

**The raw HTML does contain those dates. No table row does.** The page
renders ~37 rows and **every one is forward of today**; the May date is page
furniture - a filter widget. **A fresh capture backfilled nothing.**

**I read a date range off a file without checking it belonged to a row.**
That is the same error shape as the GDP coverage claim the day before: the
conclusion I was reaching for was right, the evidence I cited for it was not.
**Twice in two days, and both times the check caught it rather than the
output.**

**CONSEQUENCE:** decision history can only accumulate **going forward**, from
captures we take. `decision_history.py` is therefore a **weekly** run, not a
one-off - in roughly six weeks it will hold a timeline for all eight
currencies and the F-102 question becomes answerable.

---

## F-106 - A DAILY BAR IS NOT A DAY. I READ THE WRONG BAR AND REVERSED A SIGN.

**Claim I made, 2026-09-10:** *"AUDNZD fell 11.6 pips on AUD's GDP day."*
**Jeff:** *"Can you fact check this with TE and Trading View?"*

**HE WAS RIGHT TO ASK. THE CLAIM WAS FALSE, AND BACKWARDS.**

| | |
|---|---|
| TE says | AUD GDP Q2 released **2026-09-01 17:30 UTC** (02 Sep 01:30 PHT), **actual 0.4% vs 0.2% forecast - a BEAT** |
| I read | the daily bar TradingView labels **2 Sep**, close-to-close: -11.6 pips |
| The tape says | **+111.6 pips in the four hours after the release** |

**THE ERROR: OANDA's daily bars open at 21:00 UTC**, so a 17:30 UTC release
falls inside the bar labelled **1 Sep**. The "+126 pips on Tue 1 Sep" I had
attributed to something else IS the GDP move. One event, counted on the wrong
side of a bar boundary, and the sign flipped.

**THIS IS F-77's SHAPE, THIRD TIME.** F-77 was reading a RENDERED time and
re-converting it. LD-48 says recompute a derived figure and NAME THE BAR that
produced it. **A close-to-close daily change is a derived figure**, and I did
not check which bar contained the timestamp before quoting it.

**RULE: before attributing a move to a release, convert the release timestamp
into the FEED's bar convention and name the bar.** For an intraday event,
read intraday bars - a daily bar answers a question about a day, not about an
event.

**WHAT THE ERROR COST THE ARGUMENT.** I used the false claim to argue GDP does
not move price even in its release week, and preferred precedence option A
over B partly on it. **That reason is void.** What survives is independent of
price: as a BASE category GDP scores 6 GOOD / 2 NEUTRAL / 0 BAD with a range
of 1.00, adding a near-constant to the board rather than ranking anything.
**The calibrator case is now stronger than I argued** - the surprise (0.4 vs
0.2) moved the pair 111.6 pips in four hours.

---

## F-107 - THE CAPTURE STORES TE's TIME VERBATIM. IT IS UTC, NOT PHT.

**Jeff, 2026-09-10:** *"can you verify the timezone where you're looking at
JPY GDP release? Mine is at UTC+8 and the release was Sept 8 7:50 AM"*

**HE WAS RIGHT. I HAD THE OFFSET BACKWARDS.**

| | |
|---|---|
| Capture stores | `date=2026-09-07  time=11:50 PM` |
| I assumed | that string is **PHT**, so UTC = 15:50 on 7 Sep |
| It is actually | **UTC**. 23:50 UTC + 8h = **08 Sep 07:50 PHT** - exactly Jeff's screen |
| So I analysed | bars **eight hours before** the release |

**THE PARSER NEVER CONVERTS.** `capture_calendar.parse()` stores TE's time
cell as text; **only the FILENAME is PHT** (`stamp.strftime('%Y-%m-%d_%H%MPHT')`).
Reading the stored time as PHT is reading a UTC value in the wrong zone, and
converting it "to UTC" then moves it a further 8 hours the wrong way.

**WHAT IT COST - THE FINDING REVERSED:**

| JPY GDP, 4h after release | |
|---|---|
| Reported (wrong bars) | **-7.2 pips** - "the theory does not replicate" |
| Actual | **+83.0 pips**, peak +127.4 |

**BOTH GDP BEATS MOVED PRICE HARD**: AUD +111.6 pips / 4h, JPY +83.0 / 4h.
The theory REPLICATES. I had reported the opposite.

**TWO CLAIMS WITHDRAWN, both built on the artefact:**
1. *"A final revision carries little information"* - JPY's WAS a Final and
   moved 83 pips. The hypothesis was explaining a reading error.
2. *"The JPY case weakens option B"* - I said GDP would have claimed the day
   and contributed nothing. **It contributed 83 pips.**

**THIS IS THE SECOND TIMEZONE-SHAPED ERROR IN TWO TURNS** (F-106: bar
boundary; F-107: offset applied backwards) and **LD-114 was written between
them and did not prevent it.** Naming the bar is not enough if the TIMESTAMP
feeding it is in an unverified zone.

**RULE: establish the SOURCE's timezone before converting anything.** For
this repo's captures the answer is now recorded: **TE's stored `time` is UTC.
The `PHT` in the filename refers only to when WE fetched it.**

---
