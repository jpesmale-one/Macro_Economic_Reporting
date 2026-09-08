# -*- coding: utf-8 -*-
"""The six macro fact tables - load, score, rank (REVAMP, 2026-09-04).

Jeff, 2026-09-04: "It's time for us to store the data into a Fact tables so
that we have a data not just memory."

WHY THIS REPLACES score_model.ROWS. F-88 happened because 2.5 and 2.6 read
the same indicator from two hand-maintained places and disagreed inside one
edition - CHF inflation was 0.4% FALLING in one and 0.8% RISING in the
other. One keyed table makes that class of bug structural rather than
vigilance-dependent.

SCHEMA  Currency, Indicator, Frequency, <Mon-YY>, <Mon-YY>, ...
CELLS   +1 GOOD / 0 NEUTRAL / -1 BAD, or empty for not-yet-released.

THE MODEL (revamp 3, LD-94 for direction of goodness):

    category_score = (sum of that currency's scores / count) x weight

    Production  2 |  Employment    1
    Spending    2 |  Inflation     1
    Trade       2 |  Interest Rate 1

    LEADING gets 2, CONFIRMING gets 1 - Jeff's answer to the retrospective's
    headline item. The old scheme was 73% confirming+rate by weight, which
    is a model built to FORESEE a hike made three-quarters of the hike and
    its immediate precursors.

    Range -9.00 .. +9.00.

EMPTY CELLS DO NOT SCORE ZERO. They drop out of both the numerator AND the
divisor, so a currency is graded on what has actually printed. Scoring an
unreleased row as 0 would silently drag every average toward the middle -
the same shape as F-73, where an absence was published as a fact.
"""
import io, os, csv, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, 'data', 'macro_indicators')

WEIGHT = {'Production': 2, 'Spending': 2, 'Trade': 2,
          'Employment': 1, 'Inflation': 1, 'Interest_Rate': 1}

LEADING = ('Production', 'Spending', 'Trade')
CONFIRMING = ('Employment', 'Inflation', 'Interest_Rate')

CCYS = ('USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF')

ROLE = {'USD': 'Safe haven', 'JPY': 'Safe haven', 'CHF': 'Safe haven',
        'AUD': 'Commodity', 'CAD': 'Commodity', 'NZD': 'Commodity',
        'GBP': 'Cyclical', 'EUR': 'Cyclical'}


def _path(cat):
    return os.path.join(DATA, '%s_Macro_Indicators.csv' % cat)


def load(cat):
    """Rows for one category, as dicts. Raises if the file is missing."""
    with io.open(_path(cat), encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def months():
    """Month columns present, in file order, e.g. ['Aug-26', 'Sep-26']."""
    rows = load('Production')
    if not rows:
        return []
    return [k for k in rows[0].keys()
            if k not in ('Currency', 'Indicator', 'Frequency')]


def latest_month():
    """The rightmost month column that any cell is populated in."""
    ms = months()
    for m in reversed(ms):
        for cat in WEIGHT:
            for r in load(cat):
                if (r.get(m) or '').strip():
                    return m
    return ms[-1] if ms else None


def category_score(cat, ccy, month=None):
    """(score, n_scored, n_rows) for one currency in one category.

    score is already weighted. Empty cells drop out of the divisor.
    """
    month = month or latest_month()
    vals = []
    total = 0
    for r in load(cat):
        if r['Currency'].strip() != ccy:
            continue
        total += 1
        cell = (r.get(month) or '').strip()
        if cell:
            vals.append(float(cell))
    if not vals:
        return 0.0, 0, total
    return sum(vals) / len(vals) * WEIGHT[cat], len(vals), total


def base_scores(month=None):
    """{ccy: {'total', 'leading', 'confirming', 'cats': {cat: score}}}."""
    month = month or latest_month()
    out = {}
    for c in CCYS:
        cats, lead, conf = {}, 0.0, 0.0
        for cat in WEIGHT:
            s, n, tot = category_score(cat, c, month)
            cats[cat] = s
            if cat in LEADING:
                lead += s
            else:
                conf += s
        out[c] = {'total': sum(cats.values()), 'leading': lead,
                  'confirming': conf, 'cats': cats}
    return out


def coverage(month=None):
    """(scored, total) cells for the month - how much of the board is real."""
    month = month or latest_month()
    scored = total = 0
    for cat in WEIGHT:
        for r in load(cat):
            total += 1
            if (r.get(month) or '').strip():
                scored += 1
    return scored, total


def bands(scores):
    """LD-95 - RANK-based: top 3 STRONG, middle 2 NEUTRAL, bottom 3 WEAK.

    NOT fixed thresholds. On 2026-09-04 fixed bands put 8 of 8 currencies in
    NEUTRAL and no pair could have been formed at all.
    """
    order = sorted(scores, key=lambda c: -scores[c])
    return (dict([(c, 'STRONG') for c in order[:3]]
                 + [(c, 'NEUTRAL') for c in order[3:5]]
                 + [(c, 'WEAK') for c in order[5:]]), order)


if __name__ == '__main__':
    m = latest_month()
    sc, tot = coverage(m)
    print('FACT TABLES - %s   %d of %d cells scored' % (m, sc, tot))
    print()
    b = base_scores(m)
    tot_by = dict((c, b[c]['total']) for c in b)
    band, order = bands(tot_by)
    print('%-5s %-7s %-12s %7s %8s %10s   %s'
          % ('CCY', 'BAND', 'ROLE', 'TOTAL', 'LEADING', 'CONFIRM',
             'Prod Spend Trade  Empl Infl Rate'))
    for c in order:
        d = b[c]
        cells = ' '.join('%+5.2f' % d['cats'][k] for k in
                         ('Production', 'Spending', 'Trade',
                          'Employment', 'Inflation', 'Interest_Rate'))
        print('%-5s %-7s %-12s %+7.2f %+8.2f %+10.2f   %s'
              % (c, band[c], ROLE[c], d['total'], d['leading'],
                 d['confirming'], cells))
