# Calendar captures — immutable raw (CLAUDE.md section 6)

The TradingEconomics calendar serves a ROLLING ~14-day window from the request
date and IGNORES the `dates` start parameter. On 2026-08-21 a 06:50 PHT fetch
returned 17-30 Aug; a 16:37 PHT fetch the same day returned 18-31 Aug. Monday
17 Aug went from 47 rows to ZERO in ten hours.

**A week's calendar cannot be rebuilt after the fact.** Every edition's capture
is therefore persisted here, named `YYYY-MM-DD_HHMMPHT_cal_<span>.json`.

RAW IS IMMUTABLE. Never edit a file in this directory. Corrections land as a
new capture alongside, and the change is noted in STATE.md.

Finding: F-14.


## F-57 — the capture must include EVERY whitelisted currency

TE's GLOBAL calendar page omits Switzerland and New Zealand entirely. The
2026-08-23 capture held 22 countries and neither was among them, while we ran
short CHF via EURCHF and long NZD via AUDNZD — **both legs of locked pairs were
invisible to §4.0 for a week.**

`pipelines/capture_calendar.py` fetches the global page for breadth AND the
CH/NZ **country** pages for completeness, then merges. It prints a per-currency
row count and refuses to claim success while any whitelisted currency has zero.

**Two parser bugs found building it, both worth remembering:**

1. Splitting on `<tr` cut every row in half. Each TE row contains a **nested
   `<table><tr>`** for the country flag, so the time `<td>` was orphaned in one
   chunk and the event cells landed in the next — the row was then discarded by
   a `len(tds) < 3` filter. **0 times parsed from a page containing 407.**
   Split on `<tr(?=[^>]*data-event)` instead.
2. The time is inside a `<span class="calendar-date-N">`, so the cell text is
   not *only* a time. Search the cell, do not full-match it.

Finding: F-57. Guard: R-20 (`week_ahead.coverage_gaps`).
