# LAYOUT LOCK — locked 2026-08-30 (LD-80)

**Jeff, 2026-08-30:** *"4.0 why we change the format of the table? I only asked
to highlight high impact news why we're changing table formats again and again?
once the report layout is approve we should lock it up and not just changing
the report format every now and then. It's important for an analyst to
consistently look at standard report."*

**He is right, and the evidence is worse than the complaint.** The §4.0 header
changed in **four consecutive editions**:

| Edition | §4.0 columns |
|---|---|
| 27 Aug | `When · CCY · Indicator · Current actual · Cons / Fcst · Market priced · Status` |
| 28 Aug | `When · CCY · Indicator · Actual at lock · Cons / Fcst · Priced · Outcome` |
| 29 Aug | same, with **Outcome** bolded |
| **30 Aug** | **`When · CCY · Indicator · Note`** — **four columns; the pricing columns vanished** |

**A reader cannot build a scanning habit against a table that reshapes weekly.**
Worse, the 30 Aug version **silently dropped Current actual, Cons/Fcst and
Market priced** — the LD-63 pricing read — while nothing flagged the loss.

---

## THE RULE

**A section's COLUMN SET is locked. Changing it requires Jeff's word.**

- **Content changes freely** — new rows, new values, new highlighting.
- **Structure does not.** Column count, column order, and column headings are
  fixed until Jeff approves a change.
- **A request to highlight something is NOT a request to restructure it.**
  Highlighting is a rendering concern (LD-77); the table is a layout concern.

**Enforced by R-24**, which compares each locked table's header against this
file and fails the render on a mismatch.

---

## LOCKED HEADERS

### §2.0 — Category tally
```
| Band | CCY | **Score** | Group | Prod · Spend · Trade · Empl · Infl · **Rate** |
```

### §2.0b — Cycle position (LD-72)
```
| CCY | Leading | Confirming | **Gap** | Score | Cycle position |
```

### §2.1–2.5 — Indicator tables
```
| CCY | Indicator | Actual | Previous | Ref | Threshold | Score |
```

### §4.0 — Week ahead (LD-63)
```
| When (PHT) | CCY | Indicator | Current actual | Cons / Fcst | Market priced | Status |
```

**Seven columns, this order, always.** On a SELECTING (weekend) edition
`Current actual` carries the value the week starts from and `Status` reads
*ahead*; on a mid-week edition `Status` carries the outcome. **The COLUMNS do
not change — only what the cells say.**

### §4.3 — The locked set
```
| # | Pair | Bias | Entry ref | Room | Risk | Falsifier | Clear by |
```

### §4.5 — Bench (LD-75)
```
| Replaces | Alternate | Bias | Conf | Why it is the alternate |
```

---


### §2.0c — Forward-adjusted tally (LD-85, added 2026-08-31)
```
| CCY | Base | **Forward** | Change | What the week prices |
```
**Added on Jeff's approval 2026-08-31.** Base and Forward BOTH visible — the
base is never replaced by the forecast.

### §4.0 — v2 (LD-85, changed 2026-08-31)
```
| When (PHT) | CCY | Indicator | Previous | Cons / Fcst range | Actual | Market priced | Status |
```
**Changed on Jeff's instruction 2026-08-31**, three corrections: PREVIOUS is
frozen and never overwritten by a release; a release lands in its own ACTUAL
column; Cons/Fcst is a RANGE when both exist and the single figure when only
one does.

### §4.5 — Bench, room-gated (F-69, changed 2026-08-31)
```
| Replaces | Alternate | Bias | Spread | In range | Room | Against | R:R | Risk | Read |
```
**Changed on Jeff's approval 2026-08-31** after the bench was found ranked
without the room gate.

## WHAT IS *NOT* LOCKED

- **Row content, ordering within a table, and how many rows appear.**
- **Highlighting and styling** — impact tiers (LD-77), zebra striping,
  semantic colour. These are renderer concerns and never touch the columns.
- **Prose between tables.**
- **Sections that are narrative rather than tabular** (§1, §7, §8).

---

## CHANGING A LOCKED HEADER

1. **Ask Jeff first**, with the reason and the before/after.
2. On approval, update **this file** in the same commit as the change.
3. Add a row to the version history below.

**Do not "improve" a locked table in passing.** Every one of the four §4.0
variants above was written in good faith while doing something else.

---

## Version history

| Version | Date | Change |
|---|---|---|
| **v2** | **2026-08-31** | **§2.0c added; §4.0 v2 (Previous frozen, Actual column, Cons/Fcst range); §4.5 room-gated. All three approved by Jeff in advance.** |
| **v1** | **2026-08-30** | **Locked. §4.0 restored to its 27 Aug seven-column form after four editions of drift.** |
