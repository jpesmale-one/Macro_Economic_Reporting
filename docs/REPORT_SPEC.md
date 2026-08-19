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

### 2.3 Sentiment + corroboration
- **edition.cnn.com** — Fear & Greed Index
- **investing.com**, **investinglive.com** — news, facts, confluence.
  Corroboration only, never a primary value.

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

### §1 — Headline Alerts, News & Fundamentals
Events affecting the 8 currencies, Gold, and BTC. Each item: what
happened, when (PHT), source, and why it matters. Release status
(RELEASED / NOT YET RELEASED) explicit on every scheduled item.

### §2 — Interest Rates & Rate-Change Probability
Per currency: current rate, last decision with date and vote split,
next meeting date (PHT), and hike/hold/cut leaning **with the inflation
and employment prints that justify it**. Market-implied odds are quoted
only with their source instrument; unsourced odds are unauditable and are
omitted rather than guessed.

### §3 — Currency Strength Rankings
All 8 ranked, each with its catalyst. The ranking is **derived from the §3
scoring model**, not from price action alone — and where the model and
price disagree, that disagreement is stated. It is usually the most
interesting thing on the page.

Per currency: rank, composite lean, the categories driving it, and the
single strongest catalyst.

### §4 — Conviction Playbook  *(reshaped per LD-7)*

Instruments where **fundamental bias and technical structure agree**.

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

## 7. Publish gate (per edition)

- **P1 SOURCED** — every figure carries source, series/indicator name,
  release date, as-of. Release status explicit.
- **P2 RECOMPUTED** — every derived number shows its arithmetic. For a
  **level**, the recompute is *naming the bars that formed it*.
- **P3 SEALED** — Jeff's explicit word. Only then do conclusions become
  carry-forward facts in STATE.md.

**Daily seal cadence is O-3 and still open** — sealing a full edition
every morning is a real cost. Options: light seal for dailies with full
sealing weekly, or seal every edition. Decide before the first run.

---

## 8. Open items this spec does not settle

- **O-1** — output format: HTML artifact, repo markdown, or both.
- **O-3** — daily seal cadence (above).
- **O-5** — whether data pulls run automated. Automation fires **T1 + T3**
  and pulls the whole thing onto the full gate ladder. Manual-driven for
  now.
- **P-1** — standing coverage/cadence beyond the daily.
- **P-4** — ForexFactory access method (schedule role only, LD-3).
- **F-1** — stays **OPEN**. The phantom-Actual guard is a procedure I run,
  not tooling. It closes only on an automated schedule-vs-now check.
