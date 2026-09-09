# -*- coding: utf-8 -*-
"""ACTUALS in, SCORES out (LD-112).

Jeff, 2026-09-09:

    "I noticed that you were putting category scores in our CSV rather than
     the Actual scores of these indicators. I would say we need to store the
     actuals not our scores in them. If you want you can create a separate
     CSV for your scoring."

HE FOUND THE ROOT CAUSE OF THREE FINDINGS. F-91, F-94 and F-95 were all the
same failure: a release had to be written into TWO places - the ACTUAL into
score_model.ROWS, the VERDICT into the fact table - and nothing kept them in
step. R-37 exists ONLY to compare those two copies. Store the actual ONCE
and derive the verdict, and the whole class of bug stops being possible.

    data/macro_indicators/*.csv   ACTUALS, as published.  SOURCE OF TRUTH.
    data/derived/scores.csv       +1/0/-1, DERIVED.       NEVER hand-edited.

WHY THE THRESHOLD ALONE CANNOT GRADE A ROW. '>Prev' says which comparison
to make, never which direction is GOOD - lower unemployment is good, a lower
trade balance is not (F-70: two channels, opposite signs). score_model's
VERDICT column carries that polarity and Jeff has curated it row by row
(LD-57, LD-58, LD-59). So the derivation is:

    actual (fact table)  x  threshold + polarity (score_model)  ->  score

That is still ONE authority per fact. The actual lives in exactly one place;
the RULE lives in exactly one place; neither is a copy of the other.
"""
import io, os, csv, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fact_tables as ft
import score_model as sm

OUT = os.path.join(REPO, 'data', 'derived', 'scores.csv')

# LD-113 - the GDP rule, in Jeff's words 2026-09-09:
#   "Actual > 0.5% is Good, < 0% is Bad. Actual in between 0.5 - 0 is Neutral"
GDP_THRESHOLD = '>0.5%'


def _rule(ccy, indicator):
    """(threshold, verdict, previous) from score_model, or None."""
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        if sm.LABEL[iso] == ccy and name == indicator:
            return thr, v, p
    return None


def band(actual, thr):
    """LEVEL threshold -> +1 / 0 / -1 (F-92).

    A level test grades WHERE THE PRINT SITS, never which way it moved. The
    three-state band is Jeff's, stated for GDP and applied wherever a
    '>x%' level rule is in force:  above the line GOOD, below zero BAD,
    in between NEUTRAL.
    """
    a = sm._num(actual)
    if a is None:
        return None
    m = re.fullmatch(r'>\s*(\d+\.?\d*)%?', (thr or '').strip())
    if not m:
        return None
    line = float(m.group(1))
    floor = 50.0 if line >= 45 else (0.0 if line > 0 else line)
    if a > line:
        return 1
    if a < floor:
        return -1
    return 0


def score_row(cat, ccy, indicator, actual):
    """The derived score for one cell, or None if it cannot be graded."""
    if not (actual or '').strip():
        return None
    if cat == 'GDP':
        return band(actual, GDP_THRESHOLD)
    if cat == 'Interest_Rate':
        import rate_model
        iso = dict((v, k) for k, v in sm.LABEL.items())[ccy]
        return round(rate_model.compute()[iso]['raw'], 3)
    r = _rule(ccy, indicator)
    if r is None:
        return None
    thr, verdict, prev = r
    b = band(actual, thr)
    if b is not None:
        return b
    return {'GOOD': 1, 'BAD': -1, 'NEUTRAL': 0}.get(verdict)


def derive(month=None):
    """[(cat, ccy, indicator, actual, score)] for every fact-table row."""
    month = month or ft.latest_month()
    out = []
    for cat in sorted(ft.WEIGHT):
        for r in ft.load(cat):
            ccy = r['Currency'].strip()
            ind = r['Indicator'].strip()
            act = (r.get(month) or '').strip()
            out.append((cat, ccy, ind, act, score_row(cat, ccy, ind, act)))
    return out


def write(month=None):
    month = month or ft.latest_month()
    rows = derive(month)
    d = os.path.dirname(OUT)
    if not os.path.isdir(d):
        os.makedirs(d)
    fh = io.open(OUT, 'w', encoding='utf-8', newline=chr(10))
    w = csv.writer(fh, lineterminator=chr(10))
    w.writerow(['Month', 'Category', 'Currency', 'Indicator',
                'Actual', 'Score'])
    for cat, ccy, ind, act, sc in rows:
        w.writerow([month, cat, ccy, ind, act,
                    '' if sc is None else sc])
    fh.close()
    return rows


if __name__ == '__main__':
    m = ft.latest_month()
    rows = write(m)
    ungraded = [r for r in rows if r[3] and r[4] is None]
    print('DERIVED SCORES  %s   month=%s' % (OUT, m))
    print('  %d rows, %d with an actual, %d ungraded'
          % (len(rows), len([r for r in rows if r[3]]), len(ungraded)))
    for r in ungraded:
        print('   UNGRADED %-14s %-4s %s  actual=%s' % (r[0], r[1], r[2], r[3]))
