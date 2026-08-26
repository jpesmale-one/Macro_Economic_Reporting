# -*- coding: utf-8 -*-
"""LD-68 - WHERE IS THE PRICE GOING? Combining the two engines.

Jeff, 2026-08-26:

    "Look at the price now of AUD even though inflation is cooling it is
     still above the expectaions (consensus and forecast) this is an example
     of how news impact the price. and my goal for this report is to somehow
     sense where the price is going based on cobining our Macro indicators
     results and upcoming news"

THE INSIGHT. Section 2 and section 4.0 answer DIFFERENT QUESTIONS, and the
price follows the second one:

    Section 2   grades the DIRECTION of the data against a fixed threshold.
                AU inflation 3.8 -> 3.5 is ">2% & falling" -> NEUTRAL, and
                the tally DID NOT MOVE.

    Section 4.0 grades the SURPRISE - the actual against what was priced.
                3.5% came in ABOVE consensus 3.3 and forecast 3.2.

On 26 Aug the data COOLED (AUD-negative in direction) while coming in HOTTER
THAN PRICED (AUD-positive as a surprise). AUDNZD went 1.19853 -> 1.20398 and
HELD. PRICE FOLLOWED THE SURPRISE, NOT THE DIRECTION.

Both engines were right about their own question. Neither predicted the price.
What predicts the price is the RELATIONSHIP BETWEEN THEM - which nothing in
the report computed until this module.

THE FOUR STATES:

  direction | surprise | reading
  ----------|----------|--------------------------------------------------
  supportive| hawkish  | ALIGNED BID     - both point up, cleanest setup
  supportive| dovish   | TENSION         - trend up, market wanted more
  weakening | hawkish  | TENSION         - trend down, but less than priced
  weakening | dovish   | ALIGNED OFFER   - both point down, cleanest setup

ALIGNED states are where a move is most likely to run. TENSION states are
where the market must CHOOSE which engine to trade, and 26 Aug says it
chooses the surprise - at least on the day.

HONESTY ABOUT THE EVIDENCE (this matters more than the model). As at
2026-08-26 this rests on ONE clean observation. The mechanism is standard FX
- markets price expectations, then trade the deviation - but OUR sample is
n=1. The other candidates this week were untestable (Building Permits was
corrected five days late) or too small to read (CB Consumer Confidence, DXY
-8 pips). This module states a LEAN, never a forecast, and every output
carries the sample size.
"""

ALIGNED_BID = 'ALIGNED BID'
ALIGNED_OFFER = 'ALIGNED OFFER'
TENSION_UP = 'TENSION - surprise favours'
TENSION_DOWN = 'TENSION - surprise against'


def direction(sec2_grade):
    """Section 2's verdict, as a currency-direction sign."""
    if sec2_grade is None:
        return 0
    g = str(sec2_grade).upper()
    if g == 'GOOD':
        return +1
    if g == 'BAD':
        return -1
    return 0


def surprise(sec40_pricing):
    """Section 4.0's LD-63 verdict, as a SURPRISE sign for the currency.

    LD-63 grades the PRICED range against the current actual:
      GOOD = the range sits ABOVE the actual, i.e. improvement is priced in
      BAD  = the range sits BELOW the actual, i.e. deterioration is priced in

    So a BAD row that then MISSES to the upside is a HAWKISH surprise. The
    sign here is about the surprise once the print lands, which is why this
    takes the OUTCOME, not just the pricing.
    """
    if sec40_pricing is None:
        return 0
    g = str(sec40_pricing).upper()
    if g == 'GOOD':
        return +1
    if g == 'BAD':
        return -1
    return 0


def outcome_surprise(actual, consensus, forecast=None):
    """Did the PRINT beat what was priced? +1 hotter, -1 colder, 0 in range.

    This is the half that only exists AFTER a release. It is the thing that
    moved AUDNZD on 26 Aug.
    """
    if actual is None or consensus is None:
        return None
    hi = consensus if forecast is None else max(consensus, forecast)
    lo = consensus if forecast is None else min(consensus, forecast)
    if actual > hi:
        return +1
    if actual < lo:
        return -1
    return 0


def lean(dir_sign, surprise_sign):
    """Combine the two engines into a directional lean."""
    if dir_sign > 0 and surprise_sign > 0:
        return ALIGNED_BID
    if dir_sign < 0 and surprise_sign < 0:
        return ALIGNED_OFFER
    if surprise_sign > 0:
        return TENSION_UP
    if surprise_sign < 0:
        return TENSION_DOWN
    return 'NO SIGNAL'


def read(ccy, sec2_grade, actual, consensus, forecast=None, n=1):
    """Full read for one released indicator. Returns a dict for the table."""
    d = direction(sec2_grade)
    sp = outcome_surprise(actual, consensus, forecast)
    if sp is None:
        return None
    return {
        'ccy': ccy,
        'direction': {1: 'supportive', 0: 'neutral', -1: 'weakening'}[d],
        'surprise': {1: 'HOTTER than priced', 0: 'in line',
                     -1: 'COLDER than priced'}[sp],
        'lean': lean(d, sp),
        'n': n,
    }
