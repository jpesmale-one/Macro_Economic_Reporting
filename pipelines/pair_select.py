# -*- coding: utf-8 -*-
"""Pair selection from the currency ranking (REVAMP, LD-96 + LD-99).

LD-99. THE RISK REGIME IS AN OUTPUT, NOT A FORECAST. Jeff, 2026-09-04:
"We're not gonna try to forecast if the week ahead is going to be a Risk On
or a Risk Off Week. It will come naturally in the result of our tally ...
Let's treat them as a category to fill not a forecast."

So nothing here decides a regime. The ROLES of the currencies in each band
decide which categories can be filled:

    Safe haven over Commodity            -> RISK OFF
    Commodity or Cyclical over Safe haven -> RISK ON
    Cyclical over Commodity              -> EITHER

CONVICTION IS THE SCORE GAP, not the category. A Risk Off pair is not
inherently better than a Risk On one - the spread between the legs ranks
them, and that is the one term of the old confluence formula that survives.

LD-96. Leg-disjoint SURVIVES; the three-pair floor does NOT. Take the pairs
that qualify - two, or one, or none. On 2026-09-04 the floor forced NZDJPY
into the set after 4.4 had already written "the weakest of the three ... if
one pair should be dropped, it is this one", and it lost 324 pips.

WHAT THIS DELIBERATELY DOES NOT DO (LD-4): no lot size, entry, stop or
target. A pair and a direction is a BIAS. Where it would be wrong is a
falsifier, which is structure, not an exit instruction.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fact_tables as ft

HAVEN, COMMODITY, CYCLICAL = 'Safe haven', 'Commodity', 'Cyclical'

# Idea_dump/Watch_list.txt - Jeff's 21 tradeable forex pairs, VERBATIM.
# THE WATCHLIST IS A HARD CONSTRAINT, NOT A PREFERENCE (F-89). The first run
# of this pipeline selected AUDJPY, and there is NO JPY PAIR ON THE LIST at
# all - so a currency can rank anywhere and still be untradeable. Scoring
# eight currencies while only 21 of their 28 combinations are tradeable is
# exactly the kind of gap that ships silently.
WATCHLIST = (
    'AUDCAD', 'AUDNZD', 'AUDUSD', 'AUDCHF', 'NZDCAD', 'NZDUSD', 'NZDCHF',
    'CADCHF', 'EURCHF', 'EURGBP', 'EURUSD', 'EURNZD', 'EURCAD', 'EURAUD',
    'USDCAD', 'USDCHF', 'GBPUSD', 'GBPCAD', 'GBPAUD', 'GBPNZD', 'GBPCHF',
)


def tradeable(lng, sht):
    """(symbol, direction) as the market quotes it, or None if not on the list.

    A LONG lng / SHORT sht view is expressed either as the pair lng+sht LONG,
    or as sht+lng SHORT. Only one of the two will be on the watchlist.
    """
    if lng + sht in WATCHLIST:
        return lng + sht, 'LONG'
    if sht + lng in WATCHLIST:
        return sht + lng, 'SHORT'
    return None

# (long role, short role) -> category label
CATEGORY = {
    (HAVEN, COMMODITY): 'RISK OFF',
    (HAVEN, CYCLICAL): 'RISK OFF',
    (COMMODITY, HAVEN): 'RISK ON',
    (CYCLICAL, HAVEN): 'RISK ON',
    (CYCLICAL, COMMODITY): 'EITHER',
}

TIER = {('STRONG', 'WEAK'): 1,
        ('STRONG', 'NEUTRAL'): 2,
        ('NEUTRAL', 'WEAK'): 2}

# F-90. RANK-BASED BANDS CAN SPLIT A TIE, AND A TIE IS NOT A VIEW.
# On 2026-09-08 USD and EUR both scored +4.00. LD-95 bands by RANK, so the
# sort put USD in STRONG and EUR in NEUTRAL - and the pipeline duly emitted
# EURUSD SHORT on a gap of +0.00. Two currencies the model cannot separate
# are not a trade; the band label made a coin flip look like a conviction.
# A pair must clear a real gap, not merely straddle a band boundary.
MIN_GAP = 0.50


def candidates(scores=None, band=None):
    """Every permitted pairing, richest gap first.

    Returns dicts: long, short, category, tier, gap, pair, direction.
    """
    if scores is None:
        b = ft.base_scores()
        scores = dict((c, b[c]['total']) for c in b)
    if band is None:
        band, _ = ft.bands(scores)

    out = []
    for lng in scores:
        for sht in scores:
            if lng == sht:
                continue
            t = TIER.get((band[lng], band[sht]))
            if t is None:
                continue
            cat = CATEGORY.get((ft.ROLE[lng], ft.ROLE[sht]))
            if cat is None:          # same role - no risk story to tell
                continue
            gap = scores[lng] - scores[sht]
            if gap < MIN_GAP:        # F-90 - a tie is not a view
                continue
            tr = tradeable(lng, sht)
            if tr is None:           # F-89 - not on Jeff's watchlist
                continue
            sym, direction = tr
            out.append(dict(long=lng, short=sht, category=cat, tier=t,
                            gap=gap, pair=sym, direction=direction))
    out.sort(key=lambda d: (d['tier'], -d['gap']))
    return out


def select(cands=None, max_pairs=None):
    """Leg-disjoint pick, richest gap first (LD-96).

    NO MINIMUM. Returns however many qualify - possibly zero.
    """
    cands = candidates() if cands is None else cands
    used, picked = set(), []
    for c in cands:
        if c['long'] in used or c['short'] in used:
            continue
        picked.append(c)
        used.add(c['long'])
        used.add(c['short'])
        if max_pairs and len(picked) >= max_pairs:
            break
    return picked


if __name__ == '__main__':
    b = ft.base_scores()
    sc = dict((c, b[c]['total']) for c in b)
    band, order = ft.bands(sc)

    print('THE BOARD - %s' % ft.latest_month())
    for c in order:
        tie = [o for o in order if o != c and abs(sc[o] - sc[c]) < 1e-9]
        note = ('   TIED with %s - band split is arbitrary (F-90)'
                % ', '.join(tie)) if tie else ''
        print('  %-7s %-4s %-12s %+6.2f%s'
              % (band[c], c, ft.ROLE[c], sc[c], note))

    print()
    for lbl in ('STRONG', 'NEUTRAL', 'WEAK'):
        grp = [c for c in order if band[c] == lbl]
        roles = ', '.join('%s (%s)' % (c, ft.ROLE[c][:4]) for c in grp)
        print('  %-8s %s' % (lbl, roles))

    cands = candidates(sc, band)
    print()
    print('CANDIDATES - %d permitted pairings' % len(cands))
    print('  %-8s %-6s %-9s %-5s %6s   %s'
          % ('PAIR', 'DIR', 'CATEGORY', 'TIER', 'GAP', 'long/short'))
    for c in cands:
        print('  %-8s %-6s %-9s %-5d %+6.2f   %s over %s'
              % (c['pair'], c['direction'], c['category'], c['tier'],
                 c['gap'], c['long'], c['short']))

    picked = select(cands)
    print()
    print('SELECTED - leg-disjoint, no minimum (LD-96)')
    for i, c in enumerate(picked, 1):
        print('  %d. %-8s %-6s %-9s gap %+.2f   long %s / short %s'
              % (i, c['pair'], c['direction'], c['category'], c['gap'],
                 c['long'], c['short']))
    used = set()
    for c in picked:
        used.add(c['long'])
        used.add(c['short'])
    print()
    print('  %d pair(s), %d currencies used, %s unused'
          % (len(picked), len(used),
             ' '.join(sorted(set(ft.CCYS) - used)) or 'none'))
