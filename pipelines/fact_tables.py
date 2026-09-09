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
CELLS   THE ACTUAL AS PUBLISHED (LD-112), or empty for not-yet-released.
        The +1/0/-1 is derived by derive_scores.py and written, for the
        record only, to data/derived/scores.csv.

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

# LD-113 - GDP joins the board at weight 1 (Jeff, 2026-09-09):
#   "lets build a category for GDP. Give them a category score of 1."
#
# CONFIRMING, and the most confirming series on the board. Q2 GDP is
# published in September; by the time it prints, the quarter it measures
# has been over for two months and every leading series has already moved.
# Weight 1 is the right price for it - it corroborates, it does not lead.
#
# THE RANGE WIDENS: -9..+9 becomes -10..+10. The calibrator's -5..+5 is
# unchanged, so the forward half of the model now carries proportionally
# less of the total. That is a real consequence of adding a backward-looking
# category and it is recorded here rather than discovered later.
WEIGHT = {'Production': 2, 'Spending': 2, 'Trade': 2,
          'Employment': 1, 'Inflation': 1, 'Interest_Rate': 1,
          'GDP': 1}

LEADING = ('Production', 'Spending', 'Trade')
CONFIRMING = ('Employment', 'Inflation', 'Interest_Rate', 'GDP')

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

    THE CELL HOLDS AN ACTUAL, NOT A SCORE (LD-112). Jeff, 2026-09-09: "we
    need to store the actuals not our scores in them." So the score is
    DERIVED here on every read, from the actual plus the rule that owns it,
    rather than looked up from a number somebody typed.

    That is what closes F-91/F-94/F-95: there is no longer a second copy of
    the verdict to drift away from the first.

    score is already weighted. Empty cells drop out of the divisor.
    """
    import derive_scores
    month = month or latest_month()
    vals = []
    total = 0
    for r in load(cat):
        if r['Currency'].strip() != ccy:
            continue
        total += 1
        cell = (r.get(month) or '').strip()
        if not cell:
            continue
        v = derive_scores.score_row(cat, ccy, r['Indicator'].strip(), cell)
        if v is not None:
            vals.append(float(v))
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
    """LD-100 - three bands by rank, but A TIE IS NEVER SPLIT.

    Jeff, 2026-09-08: "As much as possible I don't want to put a strict
    number of currencies in Strong, Weak, and Neutral. so if one of them
    qualify as Strong but since boundary calls the other to be pushed to
    Neutral then I'd say tak off that boundary and just put both of them in
    Strong."

    SUPERSEDES LD-95, which banded strictly top 3 / middle 2 / bottom 3.
    That rule split USD and EUR at +4.00 apiece on 2026-09-08 and the
    selector duly emitted EURUSD SHORT on a gap of +0.00 (F-90) - a coin
    flip wearing a conviction label.

    The target shape is still 3 / 2 / 3. A boundary only MOVES when the
    currencies either side of it are TIED, and then the band absorbs every
    currency on that score. So bands can come out 4/1/3, 3/3/2, or on a
    heavily tied board 8/0/0 - the sizes report what the scores support
    rather than forcing a shape onto them.

    THIS ALSO REMOVES THE NEED FOR A MINIMUM GAP. A zero-gap pair can no
    longer straddle a boundary, because equal scores now share a band and
    same-band pairings are not eligible.
    """
    order = sorted(scores, key=lambda c: -scores[c])

    def cut(at):
        """Extend a cut past any currency tied with the last one inside it."""
        while at < len(order) and scores[order[at]] == scores[order[at - 1]]:
            at += 1
        return at

    hi = cut(3)                      # STRONG absorbs ties on the 3rd score
    lo = cut(max(hi, 5))             # NEUTRAL ends after the 5th, ties absorbed
    out = {}
    for i, c in enumerate(order):
        out[c] = 'STRONG' if i < hi else ('NEUTRAL' if i < lo else 'WEAK')
    return out, order


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
