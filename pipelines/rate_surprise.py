# -*- coding: utf-8 -*-
"""LD-90 - A CENTRAL BANK DECISION MOVES PRICE BY ITS SURPRISE ONLY.

Jeff, 2026-09-02, after the RBNZ hiked to 2.75% and NZD fell 108 pips:

    "The market is always forward looking. The hike itself wasn't news. What
     the market trades is the gap between what happened and what was already
     priced - and on that measure this was a dovish event."

    "A central bank decision moves price by its surprise component only.
     Level of rates -> already discounted. Change in the expected path ->
     that's the tradable variable. This is why you'll see currencies fall on
     hikes and rally on cuts more often than beginners expect."

THE EVIDENCE, from our own capture and chart:

    RBNZ actual 2.75%   consensus 2.75%   forecast 2.75%
    NZDJPY 94.409 (07:40 PHT) -> 93.331 (14:15) = -107.8 pips

A perfect match against expectations, and the currency sold off all session.
Swaps had ~95% odds, all 21 economists in the Bloomberg poll had it, ASB and
Westpac both called 25bp. Zero new information = zero reason to buy.

WHAT WAS BROKEN. rate_model scores REALISED (hiked +1 / held 0 / cut -1) plus
EXPECTED (inflation vs mandate). Both describe the LEVEL and the DIRECTION of
what already happened. Neither knows what was PRICED. So after today the
realised term stays +1.00 and 2.6 would score NZD MORE POSITIVELY for an
event that cost 108 pips.

WHAT THIS ADDS, AND WHAT IT DELIBERATELY DOES NOT

  ADDS - the DECISION surprise: actual vs consensus, sourceable from TE for
  all eight currencies on equal terms. A decision that lands exactly on
  consensus scores ZERO for the currency, not +1.

  DOES NOT ADD - the FORWARD TRACK, which Jeff correctly identifies as the
  thing that was actually live (the OCR track came in flatter than market
  pricing). TE publishes no OCR track, no terminal rate, no priced path. LD-23
  already rejected exactly these inputs because they cannot be sourced for
  all eight on equal terms, on Jeff's own instruction:

      "if we cannot find an equilibrium for Steps 2,3,4 then I'd say let's
       just used Step 1 in the scoring. this way we are not nit-picking and
       create a unfavorable bias for other currencies."

  So the PATH is published as COMMENTARY in 3 and never scored. Scoring a
  path we can only source for one or two currencies would recreate exactly
  the bias LD-23 was built to avoid.

THE FORMULA

    rate_score = (REALISED + EXPECTED) / 2 * 3        <- unchanged
    surprise   = SURPRISE_WEIGHT * (actual - consensus) / 0.25

  in basis points of a standard 25bp move, clamped to [-1, +1], then folded
  in at the same weight-3 scale. A 25bp hike when a hold was priced scores
  +1; a hike that was fully priced scores 0; a hold when a hike was priced
  scores -1.

  SURPRISE_WEIGHT is 1.0 - a full-magnitude surprise carries the same weight
  as the realised decision itself. That is deliberate: Jeff's whole point is
  that the surprise is the tradable component, not a modifier on it.

WHAT IT WOULD HAVE DONE TODAY. NZD realised +1.00, expected +0.50, surprise
0.00 -> the score stops RISING on a hike that was fully priced. It does not
go negative, because the LEVEL genuinely did improve; it simply stops paying
for news that was not news.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SURPRISE_WEIGHT = 1.0
STANDARD_MOVE = 0.25          # one 25bp click


def _bp(v):
    """'2.75%' -> 2.75, or None."""
    if v is None:
        return None
    import re
    m = re.search(r'-?\d+\.?\d*', str(v).replace(',', ''))
    return float(m.group()) if m else None


def surprise(actual, consensus, forecast=None):
    """Decision surprise in [-1, +1], or None when it cannot be measured.

    None means UNMEASURABLE - no consensus published - and an unmeasurable
    surprise scores nothing rather than defaulting to zero, which would be a
    claim that the market was unsurprised.
    """
    a = _bp(actual)
    c = _bp(consensus)
    if c is None:
        c = _bp(forecast)
    if a is None or c is None:
        return None
    d = (a - c) / STANDARD_MOVE
    return max(-1.0, min(1.0, d))


def verdict(s):
    if s is None:
        return 'UNPRICED - no consensus to measure against'
    if s > 0.20:
        return 'HAWKISH SURPRISE'
    if s < -0.20:
        return 'DOVISH SURPRISE'
    return 'FULLY PRICED - no surprise, no reason to buy'


def explain(ccy, actual, consensus, forecast=None):
    s = surprise(actual, consensus, forecast)
    if s is None:
        return '%s: %s' % (ccy, verdict(s))
    return ('%s: actual %s vs consensus %s -> surprise %+.2f - %s'
            % (ccy, actual, consensus or forecast, s, verdict(s)))


def priced_read(previous, consensus, forecast=None):
    """What 4.0 should say about a rate decision BEFORE it lands (LD-91).

    Jeff, 2026-09-02: "now that we have the picture for Interest Rate news
    how do we score it in 4.0 - Week ahead?"

    The old cell restated 2.6's score, which is a number about the PAST. A
    forward-looking row has to say what the market must see to be SURPRISED,
    because that is the only part that moves price (LD-90).

    Returns (label, note):
      HIKE PRICED    consensus above the current rate - a hike is the
                     baseline, so delivering one is NOT news. The tradable
                     outcomes are a hold (dovish shock) or a bigger move.
      CUT PRICED     the mirror.
      HOLD PRICED    consensus equals the rate. Any move at all is a surprise.
      UNPRICED       no consensus - we cannot say what is expected, and
                     saying nothing is the honest answer.
    """
    pv, c = _bp(previous), _bp(consensus)
    if c is None:
        c = _bp(forecast)
    if pv is None or c is None:
        return ('UNPRICED', 'no consensus - the surprise cannot be measured')
    d = c - pv
    if abs(d) < 0.01:
        return ('HOLD PRICED',
                'a hold is the baseline - ANY move is the surprise')
    if d > 0:
        return ('HIKE PRICED %+.2fpp' % d,
                'delivering it is NOT news; a hold is the dovish shock')
    return ('CUT PRICED %+.2fpp' % d,
            'delivering it is NOT news; a hold is the hawkish shock')


if __name__ == '__main__':
    print('LD-90 SURPRISE TERM')
    print()
    for ccy, a, c in (('NZD today', '2.75%', '2.75%'),
                      ('hike when hold priced', '2.75%', '2.50%'),
                      ('hold when hike priced', '2.50%', '2.75%'),
                      ('50bp when 25 priced', '3.00%', '2.75%'),
                      ('no consensus', '2.75%', None)):
        print('  %-24s %s' % (ccy, explain(ccy, a, c)))
