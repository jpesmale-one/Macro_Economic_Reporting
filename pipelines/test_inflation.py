# -*- coding: utf-8 -*-
"""R-44 - LD-136 (inflation) AND LD-137 (>Prev), AS EXECUTABLE CASES.

Jeff, 2026-09-14: "we need to change the inflation scoring to this
Actual > 2% and Actual >= Previous is Good. Higher chance of Interest Rate
Hike, Actual > 2% and Actual < Previous is Neutral. Probability to hold of the
current Interest Rate, Actual < 2% and Actual <= Previous is Bad. Higher
chance of Interest Rate Cut, Actual < 2% and Actual > Previous is Neutral.
Probability to hold of the current Interest Rate."

And his reasoning, which is the part worth keeping: "The target inflation is
2%, if the previous inflation is above 2% and the latest release shows
inflation is not going down then it is a hawkish tone. Higher chance of
increasing interest rate."

    INFLATION IS SCORED FOR WHAT IT DOES TO THE POLICY RATE, NOT FOR
    WHETHER IT IS COMFORTABLE FOR THE ECONOMY.

The rule it replaced read ">2% & falling" -> GOOD. That scores the economy's
comfort, and for a CURRENCY-STRENGTH model it is backwards: falling inflation
removes the pressure to hike, which is bearish for the currency.

WHY A TEST RATHER THAN A COMMENT. The old rule was not implemented at all -
band() cannot parse ">2% & falling", so every inflation row fell through to a
HAND-WRITTEN verdict in the fact table. Eight rows graded by eye, with nothing
checking them. A rule that lives only in a threshold string is a rule nobody
can run.

THE BOUNDARY IS THE AMENDMENT. Idea_dump already carried a near-identical rule
using strict > and <. Jeff's change moves it to >= and <=, and that is exactly
the case that prompted it: USD CPI printed 3.4% after 3.4%. Flat above target
is not relief - the bank has not won - so it is GOOD, not NEUTRAL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import derive_scores as ds
import score_model as sm

# (actual, previous, expected, what it is)
CASES = [
    # --- above target -------------------------------------------------
    ('3.4%', '3.4%', 1, 'FLAT above target - the amendment itself (USD CPI)'),
    ('3.4%', '3.5%', 0, 'falling above target - bank is winning, hold'),
    ('2.9%', '2.6%', 1, 'rising above target - hawkish'),
    ('4.1%', '3.1%', 1, 'rising hard above target'),
    ('2.1%', '2.1%', 1, 'flat just above target still counts'),
    ('3.0%', '2.8%', 1, 'CAD case'),
    # --- below target -------------------------------------------------
    ('1.5%', '1.8%', -1, 'falling below target - cut risk'),
    ('1.5%', '1.5%', -1, 'FLAT below target - stuck under, still cut risk'),
    ('1.9%', '1.6%', 0, 'rising below target - heading home, hold'),
    ('0.8%', '0.4%', 0, 'CHF: rising from near-zero, still under target'),
    # --- exactly at target --------------------------------------------
    ('2.0%', '2.0%', 0, 'at target, flat - mandate met'),
    ('2.0%', '2.4%', 0, 'arrived at target from above'),
    ('2.0%', '1.7%', 0, 'arrived at target from below'),
    # --- unreadable ---------------------------------------------------
    ('', '2.0%', None, 'no actual - ungraded, never a guessed 0'),
    ('2.5%', '', None, 'no previous - ungraded, never a guessed 0'),
    ('n/a', '2.0%', None, 'unparseable actual'),
]


# LD-137 - (actual, previous, threshold, expected, what it is)
PREV_CASES = [
    ('-8', '-6', '>Prev', -1, 'AUD NAB: -8 after -6 is a FALL (the bug)'),
    ('-6', '-8', '>Prev', 1, 'the same pair the other way'),
    ('3%', '3%', '<Prev', 0, 'CHF unemployment: NO CHANGE IS NEUTRAL'),
    ('4.1%', '4.1%', '<Prev', 0, 'flat is neutral in both directions'),
    ('4.5%', '4.4%', '<Prev', -1, 'unemployment rising is BAD'),
    ('2.4%', '2.5%', '<Prev', 1, 'unemployment falling is GOOD'),
    ('-$88.6B', '-$71.2B', '>Prev', -1, 'F-124: deficit WIDENING is BAD'),
    ('$-88.6B', '-$71.2B', '>Prev', -1, 'same, sign on the other side'),
    ('162K', '-23K', '>Prev', 1, 'payrolls back above zero'),
    ('-', '-6', '>Prev', None, 'no actual - ungraded'),
    ('-8', '', '>Prev', None, 'no previous - ungraded'),
    ('-8', '-6', '>0.5%', None, 'not a Prev threshold - not our business'),
]


def main():
    bad = 0
    print('R-44 INFLATION RULE (LD-136)')
    print()
    print('  %-8s %-8s %-6s %-6s %s'
          % ('ACTUAL', 'PREV', 'WANT', 'GOT', 'CASE'))
    for a, p, want, note in CASES:
        got = ds.inflation_score(a, p)
        ok = got == want
        if not ok:
            bad += 1
        print('  %-8s %-8s %-6s %-6s %s%s'
              % (a or "''", p or "''", want, got, note,
                 '' if ok else '   *** FAIL'))

    print()
    print('  LD-137 - the >Prev rule')
    print('  %-10s %-10s %-8s %-6s %-6s %s'
          % ('ACTUAL', 'PREV', 'THR', 'WANT', 'GOT', 'CASE'))
    for a, p, thr, want, note in PREV_CASES:
        got = ds.prev_score(a, p, thr)
        ok = got == want
        if not ok:
            bad += 1
        print('  %-10s %-10s %-8s %-6s %-6s %s%s'
              % (a or "''", p or "''", thr, want, got, note,
                 '' if ok else '   *** FAIL'))

    # Every inflation row in the fact table must agree with the rule.
    print()
    print('  fact table vs the rule:')
    V = {1: 'GOOD', 0: 'NEUTRAL', -1: 'BAD'}
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        if cat != 'Inflation':
            continue
        sc = ds.inflation_score(act, prev)
        want = V.get(sc)
        if want != v:
            bad += 1
            print('    *** %-4s %-26s stored %-8s rule says %s'
                  % (sm.LABEL[iso], name[:26], v, want))
    if not bad:
        print('    every inflation row matches LD-136')

    print()
    print('  fact table vs the >Prev rule:')
    nbad = 0
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        sc = ds.prev_score(act, prev, thr)
        if sc is None:
            continue
        if V.get(sc) != v:
            bad += 1
            nbad += 1
            print('    *** %-4s %-26s stored %-8s rule says %s'
                  % (sm.LABEL[iso], name[:26], v, V.get(sc)))
    if not nbad:
        print('    every >Prev row matches LD-137')

    print()
    if bad:
        print('*** %d FAILURE(S)' % bad)
        return 1
    print('  %d cases pass' % (len(CASES) + len(PREV_CASES)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
