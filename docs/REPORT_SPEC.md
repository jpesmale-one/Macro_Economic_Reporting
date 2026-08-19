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

### Category weights (LD-13)

Categories are weighted by distance from the rate decision:

| Category | Weight |
|---|---|
| **Inflation** | **3** |
| **Employment** | **2** |
| Production / Spending / Trade | 1 each |

**Within a category, a currency's N indicators split the weight evenly** —
each is worth `weight / N`. GOOD `+weight/N`, BAD `−weight/N`, NEUTRAL `0`.
Range **+8.00 to −8.00**.

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

## 4. Report structure

Six sections, following the draft's numbering.

### §1 — Headline Alerts, News & Current Events
**NOT a data table** — this is genuine news. Wars, geopolitical
escalation, disasters, pandemics, trade/tariff actions, central bank
speeches and commentary, and market-structure events (equity selloffs,
yield moves, oil moves) affecting the 8 currencies, Gold, and BTC.

Sourced from **investinglive.com** and **investing.com** (Sources.txt),
corroborated where possible. Each item: time (PHT), what happened, and
which instrument it moves. Grouped by kind — Geopolitical / Central banks
/ Risk events — not by currency.

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

Known blocked (HTTP 403 to automated fetch, observed 2026-08-19):
`rba.gov.au`, `rbnz.govt.nz`, `snb.ch`. Known working: `federalreserve.gov`.
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

### §4 — Conviction Playbook  *(reshaped per LD-7)*

Opens with the **currency strength ranking** — all 8 ranked with the
evidence driving each, derived from §2's category scores plus §1's news
and §3's policy leaning. Where the model and price disagree, say so; that
disagreement is usually the most interesting line on the page.

Then the alignments: instruments where **fundamental bias and technical
structure agree**.

Per instrument:
- **Alignment** — the fundamental read, the technical structure, and the
  direction they agree on.
- **Conviction** — ranked, with reasoning.
- **Key levels** — to the LD-5 standard: timeframe, lookback, type
  (swing/range/round/gap), touch count with dates, venue-prefixed symbol
  (`OANDA:AUDCAD`). Published as **structure**, never as entry/target.
- **Carry** (swing horizon only, LD-8) — sign and holding-cost direction,
  from the §2 rates. A **tiebreak between similar-conviction candidates,
  never a filter.** When carry breaks a tie, the report says so.
- **Falsifier** — the observation that voids the alignment. Required.

**Cadence:**
- **Monday–Friday (EVERY DAY)** — **intraday-horizon** alignments (H1/M15
  structure, session flow and event risk dominant). No carry — nothing is
  held overnight.
- **Monday, ADDITIONALLY** — **swing-horizon** alignments (daily/H4
  structure, policy divergence dominant). Carry shown (LD-8).
- **Daily** — **thesis status review** (replaces draft §4c): for each
  prior alignment, does it **still hold**, has the structure broken, has
  the falsifier fired? This is analysis of a thesis, not tracking of a
  position — the distinction is what keeps §4 inside LD-4.

So **Monday carries two blocks** — swing and intraday — kept visually
separate, because they answer different questions on different timeframes
and must never be read as one list.

**MONDAY INTRADAY CAVEAT — state it in the report, do not skip it.**
Monday intraday is structurally different from Tuesday–Friday and the read
must say so rather than treating Monday like a Wednesday:
- **Weekend gap.** Price has not traded since Friday's close. Any level
  derived from Friday's structure may be invalidated at the open, and a gap
  can leave a level untested on the new side. Say whether the open gapped
  and by how much.
- **Thin Asian liquidity.** The Monday Asian session is the thinnest of the
  week. Structure formed in it is lower-confidence and breaks more readily;
  weight London/NY structure higher on Mondays.
- **Accumulated weekend news.** Two days of headlines price in at once with
  no intervening discovery. Check for weekend events (geopolitics, central
  bank speakers, elections, China data) before reading Monday price action
  as a clean technical signal.
- **Consequence for conviction:** a Monday intraday alignment resting only
  on Asian-session structure is flagged **lower confidence** and says why.
  If the weekend produced a material headline, the fundamental read leads
  and the technical read confirms — not the reverse.

### §5 — Gold (XAUUSD), intraday approach
Drivers (real yields, DXY, haven demand, geopolitics), technical
structure, key levels to the LD-5 standard, and what would change the
read. Where CHF/JPY haven behaviour diverges from Gold, say so — the
reference artifact flagged a sustained CHF anomaly worth carrying forward.

### §6 — BTC (BTCUSD), intraday approach
Drivers (risk appetite, liquidity, NAS100 correlation, flows), technical
structure, key levels, falsifier. State whether BTC is trading **with**
risk assets or **decoupled** — it flips, and the answer changes the read.

---

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
