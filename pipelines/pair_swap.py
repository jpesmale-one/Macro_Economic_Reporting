# -*- coding: utf-8 -*-
"""LD-147 - DOES THE SWAP PAY OR COST, IN THE DIRECTION WE ARE BIASED?

Jeff, 2026-09-30, on the set block: "Can we add here if the Swap is +/- in
the directional bias?"

THE QUESTION IS ABOUT THE DIRECTION, NOT THE PAIR. A pair has two swaps and
they have opposite signs; which one applies depends on the side taken. So
this asks: holding THIS pair on THIS side, does the rate differential work
for us or against us?

    LONG  XXXYYY   ->   rate(XXX) - rate(YYY)
    SHORT XXXYYY   ->   rate(YYY) - rate(XXX)

GBPAUD LONG is long GBP 3.75% against AUD 4.60%, so the differential is
-0.85pp: the position PAYS to be held. AUDJPY SHORT is short AUD 4.60%
against JPY 1.25%, so -3.35pp - the most expensive leg in the set, and the
one a reader would most want to see named.

*** THIS IS A DISCLOSURE, NOT A SCORE, AND IT MOVES NOTHING.

LD-8 settled carry's standing: "Carry is a swing-ranking TIEBREAK, never a
filter." This module is weaker still - it does not even tiebreak. It reports
a sign so that a reader holding a position for a week can see whether the
week costs them anything to hold. The set, the gaps and the board are
computed before this runs and are not consulted by it.

The reason for that restraint is LD-4 (NO MONEY PATH). A swap figure in
money - "$4.20 a night on a mini lot" - is a position-sizing input, and
position sizing is exactly what this report does not do. A SIGN and a
DIFFERENTIAL IN PERCENTAGE POINTS is a property of the two currencies, the
same class of fact as the interest rates already published in section 4.

*** WHAT THIS IS NOT. It is not a broker swap rate. Brokers quote swaps in
points per lot, set by their own funding and marked up; two brokers differ,
and the same broker differs between accounts. What is computed here is the
POLICY RATE DIFFERENTIAL, which is the economic force underneath a broker's
number, not the number itself. The report says so wherever it prints one -
claiming otherwise would be F-107's shape, a plausible figure with no
source behind it.

*** THE RATES COME FROM rate_model, WHICH IS HAND-MAINTAINED. 2026-09-30:
the RBA hiked to 4.60% on 29 Sep and rate_model still held 4.35% - no guard
compares those cells to TE. A swap sign built on a stale rate is wrong in
exactly the way that is hardest to notice, because the sign usually survives
a 25bp move and occasionally does not. R-47 is the fix; until it exists,
this module is only as current as the cells above it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import rate_model as rm
import score_model as sm

# LD-147 - THE SWAP READS THE LIVE RATE, THE BASE READS SUNDAY'S VINTAGE.
#
# Jeff, 2026-09-30, on the RBA hike landing mid-edition: keep the edition on
# Sunday's vintage, fix rate_model at Sunday's build. That is right for the
# BASE - an edition that quietly absorbed Tuesday's hike would be a backtest
# contaminated with hindsight, and the whole vintage discipline exists to
# stop that.
#
# But a SWAP SIGN is not a score. It answers "does this position cost me
# anything to hold, right now", and a reader asking that on Wednesday is
# asking about Wednesday's rate, not Sunday's. Printing -0.60pp on GBPAUD
# when the real differential is -0.85pp would be wrong in the one direction
# that matters: it understates the cost.
#
# So the two disagree ON PURPOSE, and the report says which is which
# wherever it prints one. An overlay, dated, never silent.
LIVE = {
    # ccy: (rate, as_of, why)
    'AUD': (4.60, '2026-09-29',
            'RBA hiked 25bp to 4.60%, exactly as priced. rate_model still '
            'holds 4.35% because the 28 Sep-2 Oct edition is sealed on '
            "Sunday's vintage - it is corrected at the next build."),
}

# 'USD' -> 'US', the inverse of score_model.LABEL
ISO = dict((v, k) for k, v in sm.LABEL.items())


def rate(ccy, live=True):
    """The standing policy rate for a 3-letter currency, as a float.

    `live=True` applies the LIVE overlay, so the swap sign reflects rates as
    they stand TODAY. `live=False` returns rate_model's cell, which is the
    edition's vintage - use it when comparing against a published score.
    """
    if live and ccy in LIVE:
        return LIVE[ccy][0]
    row = rm.ROWS.get(ISO.get(ccy))
    return rm._num(row[0]) if row else None


def overlaid(pair):
    """[(ccy, live, vintage, as_of, why)] for legs the overlay changes."""
    out = []
    for c in (pair[:3], pair[3:]):
        if c not in LIVE:
            continue
        v = rate(c, live=False)
        if v is not None and abs(v - LIVE[c][0]) >= 0.005:
            out.append((c, LIVE[c][0], v, LIVE[c][1], LIVE[c][2]))
    return out


def differential(pair, side):
    """(diff_pp, base, quote) for holding `pair` on `side`, or None.

    `diff_pp` is the annualised rate differential in PERCENTAGE POINTS,
    positive when the position earns and negative when it pays.
    """
    if not pair or len(pair) != 6:
        return None
    base, quote = pair[:3], pair[3:]
    a, b = rate(base), rate(quote)
    if a is None or b is None:
        return None
    d = (a - b) if str(side).upper().startswith('L') else (b - a)
    return d, base, quote


def sign(pair, side):
    """'+' when the differential earns, '-' when it costs, '0' when flat."""
    d = differential(pair, side)
    if d is None:
        return None
    if abs(d[0]) < 0.005:          # inside half a basis point is flat
        return '0'
    return '+' if d[0] > 0 else '-'


def describe(pair, side):
    """A one-line disclosure for the set block, or None.

    'POSITIVE +2.50pp - long GBP 3.75% vs AUD 1.25%'
    """
    r = differential(pair, side)
    if r is None:
        return None
    d, base, quote = r
    lng, sht = (base, quote) if str(side).upper().startswith('L') else (quote, base)
    word = 'FLAT' if sign(pair, side) == '0' else (
        'POSITIVE' if d > 0 else 'NEGATIVE')
    return '%s %+.2fpp — long %s %.2f%% vs %s %.2f%%' % (
        word, d, lng, rate(lng), sht, rate(sht))


def table(picks):
    """[(pair, side, diff, sign)] for a list of (pair, side) tuples."""
    out = []
    for pair, side in picks:
        r = differential(pair, side)
        out.append((pair, side, r[0] if r else None, sign(pair, side)))
    return out


if __name__ == '__main__':
    print('LD-147  SWAP SIGN IN THE DIRECTION OF THE BIAS')
    print('policy rate differentials, NOT broker swap rates')
    print()
    print('%-9s %-6s %9s  %s' % ('PAIR', 'SIDE', 'DIFF', 'READS'))
    args = sys.argv[1:]
    if args:
        picks = [(a.split(':')[0].upper(), a.split(':')[1])
                 for a in args if ':' in a]
    else:
        import pair_select as ps
        import fact_tables as ft
        import glob
        cap = sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json')))[-1]
        F = ps.final_scores(cap, '2026-09-28', '2026-10-02')
        SC = dict((c, F[c]['total']) for c in F)
        band, _ = ft.bands(SC)
        picks = [(p['pair'], p['direction'])
                 for p, _ in ps.the_set(ps.candidates(SC, band), band, SC)]
    for pair, side, d, sg in table(picks):
        if d is None:
            print('%-9s %-6s %9s  %s' % (pair, side, '-', 'NO RATE'))
            continue
        print('%-9s %-6s %+8.2fpp  %s' % (pair, side, d, describe(pair, side)))
    print()
    print('A NEGATIVE differential means the position COSTS to hold.')
    print('LD-8: carry is a tiebreak, never a filter. This does not even')
    print('tiebreak - it discloses, and moves nothing on the board.')
