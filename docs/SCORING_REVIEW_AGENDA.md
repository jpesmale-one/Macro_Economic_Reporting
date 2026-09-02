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
## What NOT to do at the retro

**Do not tune four things at once.** Four changes shipped in two days; if all
four move again on one week of evidence, nothing is learnable. **Change the
one with the clearest verdict and leave the rest for another week.**

**One week is one week.** n=3 pairs over 5 sessions discriminates between
variants; it does not validate one. Say so plainly in the retro rather than
reporting a small sample as a result.
