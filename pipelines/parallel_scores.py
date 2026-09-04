# -*- coding: utf-8 -*-
"""LD-93 - PARALLEL SCORING: three weightings, published side by side.

Jeff, 2026-09-02: "probably our scoring makes things lagging instead of
leading. Instead of putting weight into the lagging indicators we probably
want to focus more on the leading side or see all of them as equal"

MEASURED FIRST, as LD-71 was:

    LEADING    Production 1 + Spending 1 + Trade 1   = 3   27%
    CONFIRMING Employment 2 + Inflation 3            = 5   45%
    RATE       the decision                          = 3   27%

73% of the score is the thing being PREDICTED. 27% is the thing that
PREDICTS it. For a model whose stated job is to foresee a hike before it
happens, that is backwards.

WHY NOT JUST RE-WEIGHT NOW. Costed against this week's actual pip moves,
the three schemes split:

    CURRENT       GBPAUD yes  CADCHF yes  NZDJPY NO    2/3
    EQUAL         GBPAUD NO   CADCHF yes  NZDJPY NO    1/3
    LEADING-TILT  GBPAUD NO   CADCHF yes  NZDJPY YES   2/3

LEADING-TILT is the only scheme that had NZDJPY - the week's loser, the pair
2.0b called IN THE PAST - pointing the right way. But it breaks GBPAUD,
which made +15.5. One right answer traded for another, on n=3.

EQUAL is the clear loser and the reason is structural: flattening Inflation
3 -> 1 strips the rate-differential signal, which is the actual transmission
channel to price. Jeff's own chain says rates decide strength.

SO: PUBLISH ALL THREE, CHANGE NOTHING. Selection continues to rank on
CURRENT. The other two accumulate a record next to it, and the 2026-09-05
retrospective decides on a week of parallel evidence instead of three
sessions.

    python pipelines/parallel_scores.py
"""
import os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_model as sm
import rate_model as rm

SCHEMES = {
    'CURRENT': {'Production': 1, 'Spending': 1, 'Trade': 1,
                'Employment': 2, 'Inflation': 3, 'Rate': 3},
    'EQUAL': {'Production': 1, 'Spending': 1, 'Trade': 1,
              'Employment': 1, 'Inflation': 1, 'Rate': 1},
    'LEADING': {'Production': 3, 'Spending': 3, 'Trade': 2,
                'Employment': 2, 'Inflation': 1, 'Rate': 1},
}
LABEL = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
         'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}


def tally(weights):
    """Re-score every currency under one weighting. Same rows, different w."""
    by = collections.defaultdict(list)
    for r in sm.ROWS:
        by[(r[0], r[1])].append(r)
    rate = rm.compute()
    out = {}
    for iso in sm.CCYS:
        tot = 0.0
        for cat, w in weights.items():
            if cat == 'Rate':
                tot += rate[iso]['raw'] * w
                continue
            rows = by[(cat, iso)]
            if not rows:
                continue
            per = w / float(len(rows))
            for r in rows:
                g = sm.graded_signed(r[3], r[4], r[6], r[7])
                if g is not None:
                    tot += per * g
                elif r[7] == 'GOOD':
                    tot += per
                elif r[7] == 'BAD':
                    tot -= per
        out[LABEL[iso]] = tot
    return out


def table():
    """The 2.0d markdown block - three schemes, one row per currency."""
    nl = chr(10)
    t = dict((k, tally(w)) for k, w in SCHEMES.items())
    order = sorted(t['CURRENT'], key=lambda c: -t['CURRENT'][c])
    rows = ['| CCY | **Current** | Equal | Leading-tilt | Rank move |',
            '|---|---|---|---|---|']
    rc = {k: sorted(t[k], key=lambda c: -t[k][c]) for k in SCHEMES}
    for c in order:
        moves = []
        # F-82: k[:4].lower() rendered EQUAL as "equa" in every published
        # edition. Label the schemes explicitly rather than by truncation.
        for k, lbl in (('EQUAL', 'equal'), ('LEADING', 'lead')):
            d = rc['CURRENT'].index(c) - rc[k].index(c)
            if d:
                moves.append('%s %+d' % (lbl, d))
        rows.append('| **%s** | **%+.2f** | %+.2f | %+.2f | %s |'
                    % (c, t['CURRENT'][c], t['EQUAL'][c], t['LEADING'][c],
                       ' · '.join(moves) or '—'))
    return nl.join(rows)


if __name__ == '__main__':
    t = dict((k, tally(w)) for k, w in SCHEMES.items())
    print('PARALLEL SCORING (LD-93)')
    print('  Selection ranks on CURRENT. The others are evidence only.')
    print()
    for k in ('CURRENT', 'EQUAL', 'LEADING'):
        o = sorted(t[k], key=lambda c: -t[k][c])
        print('  %-9s %s' % (k, ' '.join('%s %+.2f' % (c, t[k][c])
                                         for c in o)))
