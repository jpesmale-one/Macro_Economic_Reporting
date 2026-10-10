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


# LD-136 - THE INFLATION RULE IS A TARGET TEST, NOT A DIRECTION TEST.
#
# Jeff, 2026-09-14: "Actual > 2% and Actual >= Previous is Good. Higher chance
# of Interest Rate Hike, Actual > 2% and Actual < Previous is Neutral.
# Probability to hold of the current Interest Rate, Actual < 2% and Actual <=
# Previous is Bad. Higher chance of Interest Rate Cut, Actual < 2% and Actual >
# Previous is Neutral. Probability to hold of the current Interest Rate."
#
# His reasoning, verbatim: "The target inflation is 2%, if the previous
# inflation is above 2% and the latest release shows inflation is not going
# down then it is a hawkish tone. Higher chance of increasing interest rate."
#
#     INFLATION IS SCORED FOR WHAT IT DOES TO THE POLICY RATE,
#     NOT FOR WHETHER IT IS "GOOD FOR THE ECONOMY".
#
# That is why above-target-and-sticky is GOOD for the CURRENCY: it forces the
# central bank hawkish. The old thresholds read ">2% & falling" -> GOOD, which
# scored the ECONOMY's comfort rather than the RATE PATH, and is backwards for
# a currency-strength model.
#
# *** THE EQUALS CASE IS THE POINT OF THE AMENDMENT. Idea_dump already carried
# a near-identical rule using strict > and <. Jeff's amendment moves the
# boundary to >= and <=, and that is precisely the case that prompted it:
# USD CPI printed 3.4% after 3.4%. Flat above target is NOT relief - the bank
# has not won yet - so it reads GOOD, not NEUTRAL. Confirmed by Jeff
# 2026-09-14 when asked which boundary stands.
INFLATION_TARGET = 2.0

# LD-143 - THE 1.5-2.5% CORRIDOR REACHES INFLATION TOO.
#
# Jeff, 2026-09-21, on JPY CPI 1.9% after 1.9%: "This should be Neutral since
# 1.9 is in between 1.5 to 2.5".
#
# LD-136 pivoted on the single 2% POINT, so 1.9% flat read as "below target
# and not rising" -> BAD. But 1.9% is within a rounding error of the mandate;
# calling it a cut risk asserts a precision the number does not carry.
#
# LD-142 had already introduced the corridor for the POLICY RATE a day
# earlier. This makes the two categories use ONE IDENTICAL BAND, which is
# worth more than either rule alone: the same 1.9% now reads the same way
# whether it arrives as a CPI print or as a policy rate.
#
# *** WHAT IT ALSO SILENCES, AND JEFF CHOSE THIS DELIBERATELY. The corridor
# neutralises prints between 2.0 and 2.5 that LD-136 scored:
#
#     CPI 2.4% after 2.1%   GOOD -> NEUTRAL   (rising, but inside)
#     CPI 1.7% after 1.9%   BAD  -> NEUTRAL   (falling, but inside)
#
# Asked whether that was intended, he took the full corridor over a narrower
# "neutral only when flat or moving toward 2%" variant. The band is the
# signal; direction only decides the sign OUTSIDE it.
LOW, HIGH = 1.5, 2.5


# LD-155 - INFLATION IS SCORED LIKE THE RATE PATH: LEVEL FIRST, THEN THE
# SURPRISE OVERRIDES IT (Jeff, 2026-10-10).
#
#   BEFORE THE NEWS                    AFTER THE NEWS
#     expectation > 2.2  -> GOOD         actual = expectation -> retain
#     expectation < 1.8  -> BAD          actual > expectation -> override GOOD
#     1.8 .. 2.2         -> NEUTRAL      actual < expectation -> override BAD
#
# SAME SHAPE AS LD-154, deliberately - Jeff asked for both on the same day and
# the two now read the same way. CONSENSUS SUPERSEDES FORECAST here too
# ("the same with IR we use Consensus over Forecast"), and `src` records which
# number scored the row so a rescore is visible rather than silent.
#
# *** TWO THINGS THIS CHANGES FROM LD-136/LD-143, BOTH DELIBERATE AND BOTH
# CONFIRMED BY JEFF BEFORE BUILDING:
#
#   1. THE CORRIDOR NARROWS, 1.5-2.5 -> 1.8-2.2. Live effect today is ONE row:
#      CHF at 1.0% was NEUTRAL inside 1.5-2.5 and is now BAD below 1.8. Every
#      other currency sits far enough above 2.2 to be unaffected.
#
#   2. THE PREVIOUS PRINT NO LONGER ENTERS IT - LD-136's DIRECTION TEST IS
#      RETIRED. LD-136 (Jeff, 14 Sep) said "if the previous inflation is above
#      2% and the latest release shows inflation is not going down then it is
#      a hawkish tone", so 3.2% after 3.5% scored 0 - above target but FALLING,
#      the bank winning. Under LD-155 that same print scores +1, because only
#      the level is read. Five of eight hand-built test cases flip; none of
#      them is live this month, so this is a quiet change today and a loud one
#      the first time inflation turns.
#
# *** THE OVERRIDE IGNORES THE LEVEL, AND JEFF CONFIRMED THAT IS INTENDED.
# A 1.2% print beating a 1.0% expectation scores GOOD even though 1.2% is
# deflationary by the level test. I raised it explicitly ("a 1.2% print
# beating a 1.0% forecast is still deflationary") and he answered "yes, this
# is intended". The reasoning is the same as the rate path: the market trades
# the SURPRISE, and a hot print is hawkish relative to what was priced
# whatever the absolute level.
#
# COVERAGE NOTE, and it is the same shape as LD-154b. TE publishes an
# inflation consensus only in the RELEASE WEEK, so BEFORE-the-news fires
# roughly one week in four per currency and AFTER-the-news governs the rest.
# The last print carries until the next is scheduled - the standing state,
# not stale data.
NEW_LOW, NEW_HIGH = 1.8, 2.2


def inflation_decision(previous=None, consensus=None, forecast=None,
                       actual=None):
    """LD-155 -> (score, src, label) or (None, None, why).

    `src` is 'consensus', 'forecast' or 'actual'. None when nothing readable -
    never a guessed 0 (F-73).
    """
    exp = sm._num(consensus) if (consensus or '').strip() else         sm._num(forecast)
    src = 'consensus' if (consensus or '').strip() else (
        'forecast' if (forecast or '').strip() else None)
    a = sm._num(actual) if (actual or '').strip() else None

    # with no expectation the actual IS the reading - the level test alone
    if exp is None:
        if a is None:
            return None, None, 'no expectation and no actual'
        exp, src = a, 'actual'

    if exp > NEW_HIGH:
        base, lbl = 1, 'expected %.2f%% above the %.1f ceiling' % (exp, NEW_HIGH)
    elif exp < NEW_LOW:
        base, lbl = -1, 'expected %.2f%% below the %.1f floor' % (exp, NEW_LOW)
    else:
        base, lbl = 0, 'expected %.2f%% inside %.1f-%.1f' % (exp, NEW_LOW, NEW_HIGH)

    if a is None:
        return base, src, 'BEFORE - ' + lbl
    if a > exp:
        return 1, 'actual', 'AFTER - %.2f%% beat the expected %.2f%%, override GOOD' % (a, exp)
    if a < exp:
        return -1, 'actual', 'AFTER - %.2f%% missed the expected %.2f%%, override BAD' % (a, exp)
    return base, 'actual', 'AFTER - %.2f%% exactly as expected, retain' % a


def inflation_score(actual, previous, target=INFLATION_TARGET):
    """LD-136. +1 / 0 / -1 from the print, its previous, and the 2% target.

        above target, not falling   -> +1  hike risk
        above target, falling       ->  0  hold
        below target, not rising    -> -1  cut risk
        below target, rising        ->  0  hold

    Returns None when either side is unreadable - never a guessed 0, so a
    missing previous shows up as ungraded rather than as a neutral verdict.
    """
    a, p = sm._num(actual), sm._num(previous)
    if a is None or p is None:
        return None
    if a > HIGH:
        return 1 if a >= p else 0
    if a < LOW:
        return -1 if a <= p else 0
    # LD-143: inside the corridor, no compulsion either way.
    return 0


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


# LD-137 - A ">Prev" ROW IS COMPUTED, NOT HAND-GRADED.
#
# Jeff, 2026-09-14: "AUD NAB Business Confidence - Why did we score this as
# neutral 0?"
#
# Because nothing computed it. band() cannot parse '>Prev', so every such row
# fell through to a HAND-WRITTEN verdict in the fact table. NAB printed -8
# after -6 - a FALL, plainly BAD under '>Prev' - and sat at NEUTRAL. An audit
# of all 34 Prev-relative rows found a second: CHF Unemployment 3% after 3%
# stored BAD, where Idea_dump says in terms "No change is Neutral".
#
#     34 ROWS WERE GRADED BY EYE. TWO WERE WRONG. NOTHING COULD SEE IT.
#
# Same structural hole as LD-136's inflation rows, and the same fix: state
# the rule in code so the fact table is checkable rather than trusted.
def prev_score(actual, previous, thr):
    """+1 / 0 / -1 for a '>Prev' or '<Prev' threshold, else None.

    Idea_dump is explicit on the boundary, for both directions:
    "Actual > Previous is Good, Actual < Previous is Bad. NO CHANGE IS
    NEUTRAL." A flat print is neutral here - unlike LD-136's inflation rule,
    where flat carries information because it is measured against a TARGET
    rather than against itself.
    """
    t = (thr or '').strip().lower()
    if not (t.startswith('>prev') or t.startswith('<prev')):
        return None
    a, p = sm._num(actual), sm._num(previous)
    if a is None or p is None:
        return None
    if a == p:
        return 0
    up = a > p
    return (1 if up else -1) if t.startswith('>') else (-1 if up else 1)


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
    if cat == 'Inflation':
        # LD-155 replaces LD-136/LD-143 here. The fact table stores the ACTUAL
        # and no expectation, so this is the after-the-news branch with the
        # print as its own reading: the LEVEL test against 1.8-2.2.
        sc, _src, _why = inflation_decision(actual=actual)
        if sc is not None:
            return sc
    sc = prev_score(actual, prev, thr)
    if sc is not None:
        return sc
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
