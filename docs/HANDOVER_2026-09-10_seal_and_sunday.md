# HANDOVER — 2026-09-10 — the 09-06 weekly is SEALED, and Sunday is the third data point

Written as *what changes what you do next*, not as a log.

---

## WHERE THINGS STAND

**`edition: 2026-09-06 (r5, SEALED 2026-09-10)`** — selection for the 7–11 Sep
cycle, built on Sunday 6 Sep vintage. STATE.md's header is the authority;
this file goes stale the moment the 14–18 Sep edition lands.

**Artifact:** https://claude.ai/code/artifact/2d7fcf52-02e2-4b24-829f-8c61dd55cc07
Published page, repo copy, and what the generators produce **all agree** —
verified before sealing by regenerating and comparing. Republishing to that
same URL keeps the link Jeff has bookmarked.

---

## THE ONE THING THAT MATTERS ON SUNDAY

### Conviction has ranked backwards twice. A third makes it a signal.

| Week / rule | rho (peak) |
|---|---|
| r1 gap-first | **−0.80** |
| r4 LD-126 category+currency | **−0.20** |

**LD-111: three consecutive inverted weeks is ~1-in-8 if the gap were
uninformative — a signal, not noise.** The 14–18 Sep build is the third
observation.

**Both weeks share a shape.** The widest gap did not produce the widest move;
the **narrowest** gap produced the **largest**:

- CADJPY **+0.41** → **+215.4** peak (r1) — the page had labelled it *"NOISE,
  NOT A VIEW"*
- AUDJPY **+3.35** → **+203.0** peak (r4)

**If Sunday makes it three, investigate the gap formula rather than waiting.**
Jeff, 2026-09-09: *"I don't have that much of time and capital for prolonged
trial and error."*

Run `python pipelines/outcome_log.py` — it groups by `(week, rule)` since
F-113, so a re-selected week reports one rho per rule instead of a blend.

---

## HOW THE SET IS BUILT NOW (LD-125 → LD-126)

The **union** of:
- the best **tier-1** pair in each risk category, and
- the best **tier-1** pair for each **STRONG currency**

**Leg-disjointness is deliberately dropped.** Jeff chose coverage knowing the
cost, after spotting that JPY was missing: CHF and JPY are both safe havens,
so every pair they make is RISK OFF and they compete for one slot.

**The page must keep printing the overlap.** This week AUD was short in 3 of 4
pairs — `leg_overlap()` feeds a flagged note, and a concentration warning
fires at 3+. These are separate reads, not a portfolio.

**Set size varies now.** LD-96 already dropped the three-pair floor.

---

## GDP — the rule as Jeff settled it, after two reversals

**In the CALIBRATOR, not the base** (LD-117). As a base category it scored
6 GOOD / 2 NEUTRAL / 0 BAD with a range of 1.00 — it ranked nobody.

**Scored on the expectation RANGE, not a surprise** (Jeff: *"Calibrator is
forward looking and by the time we build the report we don't have the actual
values yet. We're trading the expectations not the result"*):

```
range = [min(Consensus, Forecast), max(Consensus, Forecast)]
  both > 0 → GOOD   both < 0 → BAD   straddles 0 → NEUTRAL
```

**QoQ only** (LD-116). **Rule 1 applies to it like any other row** (LD-119 —
option B was proposed and withdrawn the same day).

**Live on Sunday: NZD GDP QoQ, Thu 17 Sep 06:45 PHT, forecast −0.1% → BAD.**
That is the first live call the rule makes.

---

## RULES THAT WILL BITE IF IGNORED

**LD-115 — every time is PHT.** `phtime.te_pht()` / `bar_pht()` /
`containing_bar()`. **Never quote TE's raw `date` or `time` field** — the
stored time is **UTC**, and 23% of major-currency rows land on a different
calendar day once converted. Three sign-reversing errors came from this in one
day (F-106, F-107, F-108). R-39 guards it.

**LD-114 — fact-check my own claims, not only Jeff's requests.** The tell is a
conclusion that arrives before its verification.

**The output layer is where defects hide now.** F-104 (stale furniture), F-110
(a section silently deleted), F-111 (a whole score column of em-dashes) — all
three survived because the numbers that *were* shown were correct. **A guard
that verifies the model cannot see a page that fails to render it.**

---

## WHAT TO RUN ON SUNDAY

```
python pipelines/capture_calendar.py --write   # fresh vintage
python pipelines/decision_history.py --write   # F-102/103 - accumulates only if run
python pipelines/audit_te.py --fetch
python pipelines/test_phtime.py                # R-39
python pipelines/audit_spec.py                 # R-38
python pipelines/audit_evidence.py             # R-37
python pipelines/build_weekly.py               # retarget START/END to 14-18 Sep
python pipelines/gen_page.py
python pipelines/gen_audit.py
```

`gen_page.py` pins `CAP` to the `2026-09-08` capture and `START/END` to
7–11 Sep — **both must move to the new week.**

Then `daily_review.py` on the sealed set to grade Friday's close, and log it
with the `rule` tag.

---

## STILL OPEN

- **Interest Rate Expectations as its own category** — parked. TE publishes no
  numeric actual for CB speeches (0 of 20 rows), so it fails LD-23. The RBNZ
  gap it came from is real: NZD/CAD score PATH as *absent* and are 100%
  backward-looking on rate (F-102).
- **A daily news monitor** for flashes the calendar misses.
- **Rule 1a still unratified** — fires on JPY Wed 16 Sep.
- **No guard suite for the new pipelines.** The old `render_edition.py` guards
  target the old section structure.
- **Historical columns are records, not boards** (LD-124): 29 of 70 rows use
  `>Prev`, and an old vintage's own previous was never stored. If scoreable
  history matters, store previous alongside actual **before** the next column.
