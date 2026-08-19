# Reference: the existing daily artifact (ShadowTradeMonitor Market Sentiment)

REFERENCE, NEVER SPEC. This records the daily product Jeff has been
producing before this repo existed, so its structure and its habits are
captured rather than half-remembered. Jeff has said this project will do
things DIFFERENTLY - so nothing here is adopted by default. Each element
below is tagged KEEP / CHANGE / OPEN, and every OPEN is a Gate 1 decision
that has not been made yet.

Sample read: "Market Sentiment - Wed 12 Aug 2026 (Early AM)", artifact
91b3b86c-7ad1-4e51-a7da-e67e036dd923. Single-page dark-themed HTML,
~19,000 characters of text, nine numbered sections, published daily.

---

## Structure as it stands

| § | Section | Content |
|---|---|---|
| masthead | Index chips | NAS100, SPX, DXY, OIL, GOLD with direction colouring |
| banners | 3-4 alert strips | Crisis / Fed / RBA / USD, colour-coded by type |
| §1 | Currency Strength Rankings | All 8 majors ranked by % move, bar chart, per-currency note |
| §2 | Interest Rates & Rate-Change Probability | Rate, next meeting date, implied odds bar, likely outcome |
| §3 | Why Each Currency Moves | One driver paragraph per currency, ranked |
| §4 | Headline Alerts | Tagged items (NFP / RBA / HORMUZ / CPI / TE-CALENDAR) |
| §5 | Pair by Pair Analysis | Mon open, current, delta, week H/L, bias, carry, analysis |
| §6 | Conviction Playbook | Strong-vs-weak pairings, BUY/SELL direction, standard pairs |
| §7 | How Do We Approach Gold Today? | Levels, scenarios, TradingView chart annotation |
| §8 | Session Playbook | Asian / London / London-NY overlap |
| §9 | News & Fundamentals + Monthly Calendar | Headlines, confirmed vs scheduled events |

## Habits already RIGHT (KEEP - these are protocol-compatible)

1. **KEEP - It catches the F-1 source defect and says so in the report.**
   §4 carries a standing TE-CALENDAR alert; §2 carries a caveat naming the
   specific false figure. It cross-checks against BLS's own schedule and
   states the conflict rather than resolving it silently. This is exactly
   what LD-3 and the release-occurred rule now require.
2. **KEEP - Confirmed vs scheduled is already distinguished.** The monthly
   calendar tags rows, and rate rows say "(confirmed)" with vote splits
   ("6-3 vote", "8-1 vote, 1 dissent Takata").
3. **KEEP - Timezone is declared once, loudly, at the top.** "ALL TIMES IN
   THIS REPORT ARE PHILIPPINE STANDARD TIME (UTC+8) - converted from source
   ET/UTC timestamps." Release-time boundary errors are a named matrix row
   family; this habit prevents them.
4. **KEEP - It corrects itself in public.** The sample's top banner is a
   correction notice: the report had been datelined Tuesday and called CPI
   "tomorrow"; both were stale, and the banner says so plainly rather than
   quietly editing. That is the FAIL protocol behaving correctly.
5. **KEEP - Revisions are surfaced, not buried.** NFP is reported with its
   revisions attached (June 57K->20K, May 129K->63K, combined -103K).
6. **KEEP - Baselines are stated.** "Monday open baseline", "Mon 10 Aug
   open -> Wed 12 Aug". A delta without a baseline is not auditable.
7. **KEEP - It flags its own thin evidence.** §1 carries a caveat that the
   table is "only ~1.5 trading days in, all moves within +/-0.2%".

## Habits that CHANGE under this repo's protocol

1. **CHANGE - Sourcing is narrative, not structural.** Figures appear with
   an attributed origin in prose ("per BLS's own schedule") but there is no
   series ID, no release timestamp, no as-of date carried with the number.
   P1 requires all three. Needs a source/vintage column or footnote.
2. **CHANGE - No arithmetic is shown.** Percentages, deltas, and odds
   changes (67%->44%) appear as results only. P2 requires inputs and the
   recomputation.
3. **CHANGE - Odds carry no source.** "77% hike odds priced for September",
   "~97% priced" - market-implied odds come from a specific instrument
   (futures curve) at a specific time. Unsourced, they are unauditable.
4. **CHANGE - Confidence and falsifier are absent.** The protocol requires
   both on every read. §7's scenario boxes are the closest existing thing
   and are the natural place to attach them.
5. **CHANGE - Signal and narrative are blended.** Sentences like CHF's
   "traditional haven role appears structurally broken this cycle, full
   stop" fuse observation with a strong structural claim. Protocol wants
   the observation stated, then the inference labelled - especially for a
   regime claim, which is not portable outside the regime it came from.
6. **CHANGE - Nothing is sealed and nothing persists.** Each day's artifact
   stands alone. There is no STATE.md, no established-facts ledger, no
   carry-forward. A two-week-old observation ("CHF anomaly sustained") is
   re-asserted from memory rather than cited to a sealed edition.
7. **CHANGE - It lives only as an artifact.** No repo copy, no git history,
   no data behind it. That is the gap this repo exists to close.

## OPEN - Gate 1 decisions not yet made

- **O-1: Does the daily continue as an HTML artifact, a repo markdown
  edition, or both?** Both is plausible - markdown edition sealed in
  `reports/`, artifact rendered from it for reading. Not decided.
- ~~**O-2: Does §6 Conviction Playbook fire T2?**~~ **RESOLVED 2026-08-12
  by LD-4.** NO. This project produces bias, not execution, and there is no
  money path in the repo. §6's directional BUY/SELL calls are pure bias -
  no size, no level, no order - so they stay IN SCOPE and LEAN.
  THE STANDING GUARD: §6 must not acquire entry, stop, or target columns.
  That is the specific way this repo would cross the line, and it would
  cross one column at a time, each addition looking reasonable on its own.
  If those columns are ever wanted, that is TRTM's job, not this repo's.
- **O-3: Daily cadence vs the seal ritual.** A daily edition sealed by
  explicit word is a real daily cost. Options: seal dailies lightly and
  reserve full sealing for weekly/thematic editions, or seal every one.
  Relates to P-1.
- ~~**O-4: Which of the nine sections survive?**~~ **RESOLVED 2026-08-19 by
  Jeff's project draft.** Superseded by the SIX sections specified in
  `Idea_dump/Project_Plan.txt` and built out in `docs/REPORT_SPEC.md`:
  (1) headline alerts/news, (2) interest rates + hike/cut likelihood,
  (3) currency strength rankings + catalysts, (4) conviction playbook
  (reshaped per LD-7), (5) Gold intraday, (6) BTC intraday.
  What carried over from the nine: strength rankings, rates+odds, drivers/
  catalysts, alerts, the playbook, and gold. What did NOT: pair-by-pair as a
  standalone table (folded into section 4), session playbook, and the
  news+monthly-calendar section as its own block (folded into section 1).
  BTC is NEW - it was not in the reference artifact at all.
- **O-5: Where do the index chips and pair prices come from?** The
  tradingview MCP server is already configured and could supply OHLCV
  directly, replacing manual entry. Fires T1 when automated.

---

## The one line worth carrying forward

The existing artifact already caught, and documented daily, the exact
source defect recorded as F-1 - before any protocol existed. The protocol
is not correcting this work; it is making an existing good instinct
enforceable and persistent.
