# reports/

Sealed editions of the Daily Market Sentiment report (LD-10).

## Layout

```
reports/YYYY/QN/YYYY-MM-DD_market-sentiment.md      sealed SOURCE OF TRUTH
reports/YYYY/QN/YYYY-MM-DD_market-sentiment.html    rendered deliverable
reports/YYYY/QN/_QN_SUMMARY.md                      written at quarter close
```

The `.md` is what gets sealed and cited. The `.html` is what gets read.
If they disagree, the `.md` wins and the HTML is re-rendered from it.

Each edition is published as its own artifact with its own URL — a daily
report is a dated record, not a living page, so it is never republished
over yesterday's URL. The URL is recorded in the `.md` front matter.

## Seal tiers (LD-12)

- **Daily → LIGHT seal.** P1 (sourced) and P2 (recomputed) are mandatory
  and never relaxed. P3 is Jeff's acknowledgement in-session. Citable,
  marked `LIGHT` in front matter.
- **Weekly → FULL seal.** Explicit pass over the week. Only a full seal
  promotes conclusions into STATE.md's established-facts ledger.
- Any edition revising a previously sealed conclusion fires **T4** and
  takes a FULL seal regardless of the day.

## Quarterly compaction (LD-11) — nothing is ever deleted

At quarter close, on Jeff's trigger: write `_QN_SUMMARY.md`, promote
durable conclusions to the facts ledger, gzip the quarter's `.html` files
in place (`.md` sources stay readable), and confirm every edition is
present and sealed.

Deletion was considered and rejected. Git retains deleted files in history
regardless, so removing them reclaims nothing while destroying the
citation trail that makes the facts ledger auditable. Measured: ~68 KB per
edition, ~24 MB/year raw, ~5 MB/year in git. Storage is not the
constraint; readability is.
