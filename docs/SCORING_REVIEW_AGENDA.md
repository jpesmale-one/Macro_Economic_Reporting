# SCORING REVIEW — agenda for the 2026-09-05 retrospective

**Jeff, 2026-08-31:** *"let's give it a go. then we put all our scoring logic
for review coming the market close retro review"*

**Four scoring changes shipped between 30 Aug and 31 Aug.** Every one is a
judgement call made mid-week on a live set, and **every one is graded against
what actually printed** — §4.0 recorded the projections in advance, which is
the whole reason that section exists.

**This file is the agenda, not the answer.** It is written BEFORE the outcomes
are known so the questions cannot be retrofitted to them.

---

## 1. LD-85 — the forward adjustment, k = 0.50

`adjusted = base + k × Σ(verdict × category weight)`

**The claim being tested:** k=0.50 is the largest value at which no currency's
rank is decided by a single forecast.

**Grade it on:**
- For each priced row, did the ACTUAL land in the direction §4.0 predicted?
  A GOOD row that printed BAD is a wrong call, not just a miss.
- **Did the forward score beat the base score at ranking the week's movers?**
  If base ranked them just as well, k should fall toward 0.
- **CHF is the stress case.** One w3 inflation print carried its entire
  −1.50/+1.50 swing. Did that single forecast earn a 3-point influence?
- **USD's NFP +2 and Unemployment −2 annihilated.** Was net-zero the honest
  read of that report, or did the two prints deserve different weights?

## 2. LD-86 — the cycle gate, ±25% multiplier

**The claim being tested:** a currency whose rate case has already played out
(IN THE PAST) is a worse long than its tally score suggests.

**Grade it on:**
- **NZDJPY is the origin case.** §2.0 said select it; §2.0b said NZD is IN THE
  PAST. **Which view was right by Friday?**
- **GBPAUD took the worst tilt on the board (−1.00) and was kept on room.**
  Did room carry it, or did the cycle call it correctly?
- **Not one candidate scored positive on cycle this week.** If that repeats,
  the thresholds (±0.40) are miscalibrated rather than the board being
  unusual.
- Is ±25% the right size? It re-ranked the top two without changing the set.

## 3. Confluence itself — the formula nobody has ever tested

`(spread/8 + room + inverted risk) / 3`, equal weights.

**This has never been graded against outcomes.** It was called *"a first
formulation, not a tuned one"* when written and has been carried unchanged
since.

**Grade it on:**
- **Equal weights are an assumption, not a finding.** Did room predict better
  than spread this week? F-69 suggests room deserves more than a third.
- **The spread term reaches 0.87 while room caps at 1.00** — a wide spread can
  outvote a room problem 4:1. That is how GBPCHF reached #1 with 63 pips.
- **Should room GATE rather than contribute?** Criterion 4 reads like a filter
  (*"look for other pairs … with room"*), not a weighted term.

## 4. The three-pair floor vs the room floor

**Discovered while costing k and never resolved.** On Sunday's board only TWO
pairs cleared a 0.20 room floor, and only ONE cleared 0.35. **LD-35 says three
is the minimum, so the floor and the minimum are in direct conflict** — and
the current formula resolves it silently by selecting pairs with no room.

**The question for Jeff:** hold three and accept a thin third pick, or let the
set shrink when the board is thin? **This is his call, not a tuning decision.**

**Related, and also open:** the third pick is often FORCED rather than chosen.
Once two pairs claim four currencies, LD-19 frequently leaves exactly one
eligible candidate — EURCHF landed in the set twice this way during costing,
on 41 pips of room. **A forced pick should probably be labelled as one.**

---

## 5. LD-90 — the SURPRISE term, and the path we cannot score

**Added 2026-09-02, from the live case Jeff called out.**

**RBNZ hiked to 2.75% exactly on consensus and NZD fell 108 pips.** Before
LD-90, §2.6 would have scored NZD **more positively** for that event.

**Grade it on:**
- **Did the surprise term improve the read on any OTHER decision this week?**
  BoC lands 21:45 tonight priced to hold — a hold scores 0.00 surprise, and
  the question is whether CAD moves anyway.
- **Is SURPRISE_WEIGHT = 1.0 right?** It currently counts equally with the
  realised decision. Jeff's argument says the surprise IS the tradable
  component, which argues for equal or higher — but one event is one event.
- **⚠ THE OPEN GAP: the forward track.** Jeff's fuller point is that the
  tradable variable was the **OCR track versus what was priced** — ~95bp of
  tightening to Jun 2027 against the RBNZ's own 25bp. **We score none of
  that**, because TE publishes no track and LD-23 forbids an input we can
  only source for one or two currencies.

  **The question for Jeff: is a path read worth carrying as COMMENTARY in
  §3 for the currencies where it exists, accepting that it will never be a
  number?** That is a different trade-off from the one LD-23 settled — that
  was about SCORING, this is about SAYING.

---
## 6. ⚠ THE HEADLINE ITEM — is the model LEADING or LAGGING? (LD-92, LD-93)

**Jeff, 2026-09-02:** *"the whole point of this report is to foresee if the
central bank will Hike before it happen. If we can predict that the currency
is getting strong we can price in early and trade it … probably our scoring
makes things lagging instead of leading."*

**This is the biggest open question in the model and it leads the review.**

### The measurement that prompted it

| Stage | Weight | Share |
|---|---|---|
| LEADING — Production, Spending, Trade | 3 | **27%** |
| CONFIRMING — Employment, Inflation | 5 | 45% |
| RATE — the decision | 3 | 27% |

**73% of the score is the thing being predicted. 27% is the thing that
predicts it.**

### What shipped on 2 Sep, and what did NOT

**SHIPPED — LD-92:** cycle tilt **±25% → ±50%**. Strengthens the leading read
without touching the weights. **Reversible on one line.**

**SHIPPED — LD-93:** §2.0d publishes CURRENT, EQUAL and LEADING-TILT side by
side. **Selection still ranks on CURRENT.** The others accumulate a record.

**NOT SHIPPED — the weights themselves.** On n=3 that is tuning to noise.

### Grade it on

- **Which scheme ranked the week's movers best?** §2.0d has a daily record by
  Saturday. **Current and Leading both went 2 of 3 on Wednesday; Equal went
  1 of 3.**
- **NZD is the test case.** 4th under CURRENT, **LAST under LEADING**. It was
  the week's only losing leg and §2.0b called it IN THE PAST on Sunday.
- **CHF is the counter-test.** −0.28 under CURRENT, **+5.85 under LEADING** —
  a six-place jump. **We are SHORT CHF in the week's best pair.** If CADCHF
  keeps winning, LEADING is wrong about CHF and the record must say so.
- **Did ±50% help or overshoot?** It moved CADJPY to the top of §4.2 and
  GBPAUD to the bottom — **and GBPAUD made +15.5 this week.**

### The structural argument against EQUAL

**Flattening Inflation 3 → 1 strips out the rate-differential signal**, which
is the actual transmission channel to price. **Jeff's own chain says rates
decide strength** (2026-08-21). EQUAL denies the mechanism the report is
built on — it is on the sheet for completeness, not as a live candidate.

---
## 7. ⚠ ADDED 2026-09-04 — the ROOM gate inverted, and nobody designed for it

**This was not on the agenda when the agenda was written.** It surfaced on the
last day of the lock and it is the cleanest single defect the week produced.

### What happened

| Pair | Room | Confluence rank | Actual result |
|---|---|---|---|
| **NZDJPY** | **0.91** | **2nd of 8** | **−324.4 pips, 32.7 from its falsifier** |
| **CADCHF** | **0.10** | **8th of 8, last** | **+33.2 pips, the only winner** |

**The gate ranked our worst pair second and our best pair last.**

### Why

**Room measures the fraction of the 45-bar range lying in the bias direction.**
NZDJPY had fallen to **8.7% of its range**, so almost the whole range sits
"above" a LONG — **the gate reports the 324 pips already lost as opportunity
ahead.** CADCHF *rose* to 89.6% of its range, so it scores as having nowhere
to go **because it worked**.

### The distinction the gate cannot draw

**A pair with room ahead of it and a pair in free fall look identical from the
bottom of a range.** F-69 built this gate to catch GBPUSD — a LONG at 94% of
range with 30 pips of headroom — and **it still does that job correctly.** The
failure is at the other end of the scale, which was never tested.

### Grade it on

**1. Does room predict anything at all?** n=3 this week, plus the 4 pairs of
2026-08-24 and the 3 of 2026-08-31. **~10 observations — thin, but it is what
exists.**

**2. Would a DIRECTION filter fix it or break it?** e.g. room only counts when
price is not making new lows against the bias. **Costed against every past
selection before it ships**, because the same change would have removed
GBPAUD from this week's set (it also gained room by falling) — and GBPAUD is
not the pair that failed.

**3. Or is room simply mis-weighted rather than wrong?** It is a third of
confluence. **F-69 and criterion 4 both say it must not weaken**, which is
exactly the constraint that made LD-86 a multiplier rather than a fourth term.

### ⚠ The trap

**Do not fix this by down-weighting room.** The one pair that made money this
week scored 0.10 on room, so **a naive reading says room should be inverted**
— and that reading is drawn from a single week in which the yen repriced 292
pips on a central bank that did not meet. **One event drove three of the
eight rows.**

---
## What NOT to do at the retro

**Do not tune six things at once.** Four changes shipped in two days; if all
four move again on one week of evidence, nothing is learnable. **Change the
one with the clearest verdict and leave the rest for another week.**

**One week is one week.** n=3 pairs over 5 sessions discriminates between
variants; it does not validate one. Say so plainly in the retro rather than
reporting a small sample as a result.
