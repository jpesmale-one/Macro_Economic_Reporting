# -*- coding: utf-8 -*-
"""
LD-19: carried pairs must be LEG-DISJOINT.

Two pairs that share a currency are not two tests of the model - they are one
currency call expressed twice. On 2026-08-20 three of four carried pairs were
JPY crosses; they returned +0.72/+0.76/+0.58%, a 0.18pp spread, and the
scorecard reported "4 of 4" for what was really 2 independent bets.

Selection rule:
  1. Rank all candidate pairings by spread (strong-vs-weak, haven-vs-haven,
     commodity-vs-commodity), floor 1.00.
  2. Walk the ranking; carry a pair only if NEITHER of its currencies already
     appears in a carried pair. Otherwise mark it CORRELATED and name the
     carried pair it duplicates.
  3. The structure filter then applies to the disjoint shortlist as before.

With 8 currencies the hard ceiling is 4 leg-disjoint pairs (8/2). In practice
the strong/weak split usually yields 2-3.
"""


def select_disjoint(cands):
    """cands: list of dicts with keys symbol, direction, base, quote, spread.
    Returns (carried, correlated) - correlated rows carry a 'blocked_by' key."""
    used = {}                       # currency -> symbol that claimed it
    carried, correlated = [], []
    for c in sorted(cands, key=lambda x: -x['spread']):
        clash = [ccy for ccy in (c['base'], c['quote']) if ccy in used]
        if clash:
            c = dict(c)
            c['blocked_by'] = ', '.join('%s (via %s)' % (used[x], x) for x in clash)
            c['shared'] = clash
            correlated.append(c)
        else:
            used[c['base']] = c['symbol']
            used[c['quote']] = c['symbol']
            carried.append(c)
    return carried, correlated


def exposure(carried):
    """Net currency exposure of a carried set - catches the same-side duplicate
    that leg-disjointness alone does not (e.g. long CAD twice)."""
    from collections import Counter
    lng, sht = Counter(), Counter()
    for c in carried:
        if c['direction'] == 'LONG':
            lng[c['base']] += 1; sht[c['quote']] += 1
        else:
            lng[c['quote']] += 1; sht[c['base']] += 1
    return lng, sht
