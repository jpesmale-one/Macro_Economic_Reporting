---
paths:
  - "reports/**"
  - "docs/**"
  - "data/**"
  - "pipelines/**"
---

# Key levels & the TradingView MCP (LD-5)

Loads when working on reports, data, or pipelines. The scope boundary in
CLAUDE.md (LD-4/LD-5) and the publish gate always apply — this file is the
detail, not the authority.

## The scope line, restated because this is where drift happens

A LEVEL is an observation about price structure. In scope.
An EXECUTION ROLE for that level is an instruction. Out of scope.

| In scope | Out of scope |
|---|---|
| "4,435 is the swing high, rejected twice (Mon, Tue)" | "Stop above 4,435" |
| "4,373 is the prior consolidation floor, 5 touches" | "Enter on a break of 4,373" |
| "Price is between the Aug 4 low and the Aug 11 high" | "Target 4,500, risk 20 pts" |

Same numbers. The right column assigns a trading role, and this repo does
not do that. Watch for the words that smuggle it in: stop, entry, target,
trigger, risk, invalidation-as-a-stop-level. Describing a level as "where
the thesis would be wrong" is FINE — that is a falsifier, which the
protocol requires. Describing it as "where to exit" is not.

## A level is evidence, not an opinion (P2 applies)

Never publish a bare level. Every published level carries:
- **Timeframe** it was derived from (D1, H4, …) and the **lookback window**.
- **Type**: swing high/low, prior day/week/month H-L, round number, gap
  edge, consolidation boundary, session/VWAP anchor.
- **What happened there**: touch count with dates, and whether it held or
  broke on each test.
- **Source**: the symbol as quoted, including the venue prefix
  (`OANDA:XAUUSD`), because feeds differ. A level from one feed does not
  transfer silently to another.

"Support at 4,373" alone is unauditable. The recompute for a level is
naming the bars that formed it — that is P2 for price data, exactly as
recomputing a YoY from index levels is P2 for macro data.

Distinguish an OBSERVED level (price actually turned there) from a
DERIVED one (round number, projection, indicator output). Label which.

## MCP usage — read freely, draw carefully, never act

**READ — no restriction.** `data_get_ohlcv`, `quote_get`, `symbol_info`,
`symbol_search`, chart state, indicator/study values, `capture_screenshot`.
This is the evidence-gathering path.

**DRAW — allowed.** Horizontal lines, trend lines, rectangles, text for
levels and annotation. Display-only; touches no account.

**NEVER without Jeff asking in the moment:**
- `alert_create` / `alert_delete` — an alert is an unattended action that
  outlives the session. It is also T3-shaped (scheduled/automated).
- `replay_trade` — places simulated orders; execution-shaped, and outside
  this repo's purpose regardless of being simulated.
- Anything that rewrites saved layouts, watchlists, or Pine scripts.

**It is Jeff's live workspace, not a scratchpad.** The MCP drives the chart
he is actually looking at. Do not reorganise panes, swap symbols, change
timeframes, or clear drawings beyond what was asked — and say what you
changed when you change it. If a read needs a different symbol or
timeframe, prefer restoring the prior state afterwards, or ask first.

## Data hygiene for prices

- A price snapshot pulled for a report is data: it lands with provenance
  (symbol with venue prefix, timeframe, bar timestamp, retrieval time).
- Quote the **bar close and its timestamp**, not "current price" with no
  time — an unstamped price is unauditable an hour later.
- Say whether a bar is CLOSED or still FORMING. A level derived from a
  forming bar can vanish; that must be visible in the artifact.
- Weekend/holiday gaps and session boundaries change what "prior day"
  means. Name the session convention when it matters.
