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
