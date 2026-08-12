# Report template (lean track)

Copy to `reports/YYYY-MM-DD_<topic>.md`. A sealed edition is NEVER
rewritten in place — a revision is a new edition that names what changed.

The three publish-gate steps (CLAUDE.md section 3) map onto the sections
below: P1 SOURCED = the data table, P2 RECOMPUTED = the arithmetic column
and the workings, P3 SEALED = the seal line at the bottom.

---

# {{TOPIC}} — {{YYYY-MM-DD}}

**Edition:** {{EDITION}}
**Data as-of:** {{DATA_ASOF}}
**Status:** DRAFT (unsealed — not citable by later work)

## Bottom line
Two or three sentences. What the data says and what it means for
positioning. No hedging filler; state the confidence explicitly.

**Confidence:** {{high / medium / low}}
**Falsifier:** the specific observation that would change this
conclusion. Required — a read with no falsifier does not get published.

## The data (P1 — sourced)

| Series | ID | Release date | As-of | Value | Prior | Unit |
|---|---|---|---|---|---|---|
| | | | | | | |

Every row traceable to a release. Estimates, consensus figures, and own
derivations are labelled as such in the Value column — never dressed as
prints.

## The arithmetic (P2 — recomputed)

Show inputs, not just results. One line per derived figure:
- `<figure> = <inputs> = <result>` with the unit named.

Units declared: percent vs percentage point vs basis point; SA vs NSA;
monthly vs annualized. Rounding stated, applied once at presentation.

## What the data shows (signal)
Statements that are true of the data alone. No interpretation here.

## What I infer (narrative — labelled)
Interpretation, transmission channels, regime caveats. Any asserted
mechanism names what would break it. Correlation is not presented as
mechanism.

## What did NOT happen (absence checks)
Explicit checks for what is not there, with the range checked. An
unexamined absence is an assumption, not a finding.

## Changes vs prior edition
What moved, what was revised at the source, and whether any prior
conclusion is affected. A revision touching a SEALED conclusion fires T4.

## Open questions / next data
What would sharpen this, and the next release that bears on it.

---
**SEAL:** unsealed. Jeff seals with an explicit word; only then do this
edition's conclusions become carry-forward facts in STATE.md.
