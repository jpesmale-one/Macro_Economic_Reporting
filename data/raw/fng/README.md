# CNN Fear & Greed captures — immutable raw (CLAUDE.md section 6)

The endpoint returns only a CURRENT snapshot; there is no historical query.
Each component carries its OWN timestamp, and they refresh independently — on
2026-08-21 VIX was stamped 16:41 while the others were 03:59–08:59, which is
what produced a 0.0286 recompute residual against an index computed moments
earlier.

**A capture cannot be reconstructed after the fact.** Every edition's pull is
persisted here as `YYYY-MM-DD_HHMMPHT.json`.

`pipelines/fng_block.py` builds the published bar chart FROM these files, so
the figures in the deliverable cannot drift from the source.

RAW IS IMMUTABLE. Never edit a file in this directory.

Related: LD-25 (the block format), F-14 (the same rolling-window problem on the
TE calendar).
