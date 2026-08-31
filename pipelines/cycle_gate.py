# -*- coding: utf-8 -*-
"""LD-86 - THE CYCLE GATE: 2.0b stops being decorative.

Jeff, 2026-08-31: "2.0b Cycle position - you're pointing this out earlier.
I'd say let's give it a go."

THE PROBLEM IT FIXES. Selection ranked on the 2.0 tally alone. 2.0b was
computed, published, and read by nobody downstream - LD-74 required it to be
PRESENT on a selecting edition, and no code consumed it.

NZDJPY is the case that exposed it. On 2026-08-30 the two views disagreed
about the same pair and we acted on one while printing the other:

    2.0  tally  NZD +4.65 vs JPY +0.53 -> spread 4.12, SELECT IT
    2.0b cycle  NZD IN THE PAST, nothing upstream feeding it

The cycle view was right. Decomposing the pair later showed JPY ahead of NZD
on Production, Spending AND Employment; NZD's entire lead came from Inflation
and Rate - the CONFIRMING half - resting on Jun/26 quarterly data two months
old, while every fresh NZD print was negative.

WHY THE TALLY IS BLIND TO THIS. The weights are Inflation 3 and Rate 3
against Production/Spending/Trade at 1 each, so the tally is dominated 6:3 by
the END of Jeff's causal chain. A currency whose rate case has already played
out scores HIGHEST exactly when its remaining upside is SMALLEST. 2.0b is the
correction for that, which is why leaving it unconsumed wasted the fix.

THE GATE. Same shape as event risk (LD-73) - it RE-RANKS, never vetoes:

    BUILDING     upstream ahead of confirming, gap > +0.40   -> favourable
    aligned      the two halves agree                        -> neutral
    IN THE PAST  gap < -0.40, nothing upstream feeding it    -> unfavourable

    cycle_tilt(pair) = (position of the LONG leg
                        - position of the SHORT leg) / 2      in [-1, +1]

A LONG on a BUILDING currency against an IN THE PAST one scores +1. The
reverse scores -1. Anything else lands between.

NOT A VETO, AND NOT A SPREAD SUBSTITUTE. Jeff, 2026-08-29: "I did not give a
hard rule that we should immediately match top vs bottom." The macro spread
still ranks; this re-ranks what the spread produced, exactly as room and event
risk do. A currency IN THE PAST can still be selected - it just has to earn it.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_model as sm
import section2

BUILDING, ALIGNED, PAST = 'BUILDING', 'aligned', 'IN THE PAST'
GAP_BUILDING = 0.40
GAP_PAST = -0.40
POS = {BUILDING: 1, ALIGNED: 0, PAST: -1}


def positions():
    """{ccy: (position, leading, confirming, gap)} - the 2.0b numbers."""
    cs, tot = sm.compute()
    lead_max = float(sum(sm.W[c] for c in section2.LEADING))
    conf_max = float(sum(sm.W[c] for c in section2.CONFIRMING))
    out = {}
    for iso in tot:
        lead = sum(cs.get((c, iso), (0.0,))[0]
                   for c in section2.LEADING) / lead_max
        conf = sum(cs.get((c, iso), (0.0,))[0]
                   for c in section2.CONFIRMING) / conf_max
        gap = lead - conf
        pos = (BUILDING if gap > GAP_BUILDING
               else PAST if gap < GAP_PAST else ALIGNED)
        out[sm.LABEL[iso]] = (pos, lead, conf, gap)
    return out


def cycle_tilt(base, quote, direction, pos=None):
    """Cycle advantage IN THE BIAS DIRECTION, in [-1, +1] (LD-86)."""
    if pos is None:
        pos = positions()
    lng, sht = (base, quote) if direction == 'LONG' else (quote, base)
    if lng not in pos or sht not in pos:
        return 0.0
    return (POS[pos[lng][0]] - POS[pos[sht][0]]) / 2.0


def verdict(tilt):
    if tilt >= 0.5:
        return 'CYCLE FAVOURS'
    if tilt <= -0.5:
        return 'CYCLE AGAINST'
    return 'cycle neutral'


def explain(base, quote, direction, pos=None):
    """One line naming both legs' positions - for the report, not a number."""
    if pos is None:
        pos = positions()
    lng, sht = (base, quote) if direction == 'LONG' else (quote, base)
    t = cycle_tilt(base, quote, direction, pos)
    return '%s long %s / short %s \u2014 %s' % (
        verdict(t), pos.get(lng, ('?',))[0], pos.get(sht, ('?',))[0], '%+.2f' % t)


# LD-86 - HOW THE TILT ENTERS CONFLUENCE.
#
# Two shapes were costed against the live board on 2026-08-31:
#
#   4-TERM      (spread/8 + room + inv_risk + cycle) / 4
#   MULTIPLIER  core * (1 + 0.25 * tilt), bounded 0.75..1.25
#
# THE MULTIPLIER WINS, and not on results - both produced the same three
# pairs. It wins because the 4-term shape DILUTES ROOM from a third of the
# score to a quarter, and F-69 plus criterion 4 of docs/SELECTION_CRITERIA.md
# both say room is the term that must not weaken. The multiplier scales a
# setup the core has already judged; it cannot rescue a pair with no room.
#
# BOUNDED AT +/-25% so the cycle re-ranks without dominating - the same
# restraint as k=0.50 in LD-85.
CYCLE_WEIGHT = 0.25


def apply_tilt(confluence, tilt, weight=CYCLE_WEIGHT):
    """Scale a confluence score by the cycle tilt (LD-86)."""
    return confluence * max(1 - weight, min(1 + weight, 1.0 + weight * tilt))


if __name__ == '__main__':
    p = positions()
    print('CYCLE POSITIONS (LD-86 / 2.0b)')
    for c in sorted(p, key=lambda x: -p[x][3]):
        pos, lead, conf, gap = p[c]
        print('  %-4s lead %+5.2f  conf %+5.2f  gap %+5.2f  %s'
              % (c, lead, conf, gap, pos))
    print()
    print('TILT FOR THE LOCKED SET')
    for pair, b, q, d in (('GBPAUD', 'GBP', 'AUD', 'LONG'),
                          ('CADCHF', 'CAD', 'CHF', 'LONG'),
                          ('NZDJPY', 'NZD', 'JPY', 'LONG')):
        print('  %-8s %s' % (pair, explain(b, q, d, p)))
