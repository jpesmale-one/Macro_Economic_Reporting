# News captures — immutable raw (CLAUDE.md section 6)

Section 1's MANDATED sources per docs/REPORT_SPEC.md and Idea_dump/Sources.txt:
`investinglive.com` and `investing.com`. Both return **403 on a plain fetch and
200 with a browser User-Agent** — step 2 of the F-6 ladder. Nothing more is
needed.

News feeds are rolling: a headline visible today is gone next week. Captures
are therefore persisted per edition as `YYYY-MM-DD_HHMMPHT_<source>.html`,
alongside any primary document they point to.

F-17: these sources were never fetched across the first three editions, and
section 1 was built from calendar sources instead. A calendar can only report
what was scheduled — it cannot report an unscheduled announcement. Three sealed
conclusions were written as "cause not identified" while the cause sat here.

RAW IS IMMUTABLE. Never edit a file in this directory.
