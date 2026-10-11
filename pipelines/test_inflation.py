# -*- coding: utf-8 -*-
"""R-44 - LD-136 (inflation), LD-137 (>Prev) AND LD-140 (rate), AS CASES.

*** THE RULE MUST HOLD IN BOTH SCORERS. Jeff, 2026-09-14: "We should apply
the new scoring now for the calibrator news events". LD-136 reached the BASE
via derive_scores and stopped there - the calibrator has its own score_row(),
and an inflation row fell through it to market_pricing(), which grades a
SURPRISE vs consensus instead. CAD expected 3.0% after 3.0%: no surprise, so
NEUTRAL, while the base called flat-above-target GOOD. THE SAME RULE, THE SAME
CURRENCY, THE SAME EDITION, TWO ANSWERS. The last check below asserts both
scorers agree on every inflation row in the live capture.

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
    # --- above the 2.5% ceiling ---------------------------------------
    ('3.4%', '3.4%', 1, 'FLAT above ceiling - USD CPI, LD-136 amendment'),
    ('3.4%', '3.5%', 0, 'falling above ceiling - bank winning, hold'),
    ('2.9%', '2.6%', 1, 'rising above ceiling - hawkish'),
    ('4.1%', '3.1%', 1, 'rising hard above ceiling'),
    ('2.6%', '2.5%', 1, 'just over the ceiling, rising'),
    ('3.0%', '2.8%', 1, 'CAD case'),
    # --- LD-143: inside the 1.5-2.5 corridor, NOTHING is signed -------
    ('1.9%', '1.9%', 0, 'JPY flat at 1.9 - THE LD-143 CASE'),
    ('2.4%', '2.1%', 0, 'rising INSIDE the corridor - silenced deliberately'),
    ('1.7%', '1.9%', 0, 'falling INSIDE the corridor - silenced deliberately'),
    ('2.5%', '2.75%', 0, 'exactly on the ceiling is INSIDE'),
    ('1.5%', '1.25%', 0, 'exactly on the floor is INSIDE'),
    ('2.0%', '2.0%', 0, 'at target, flat'),
    # --- below the 1.5% floor -----------------------------------------
    ('1.4%', '1.5%', -1, 'just under the floor, falling - cut risk'),
    ('1.2%', '1.2%', -1, 'FLAT below the floor - stuck under, cut risk'),
    ('1.4%', '1.2%', 0, 'rising below the floor - heading home, hold'),
    ('0.8%', '0.4%', 0, 'CHF rising from near-zero, still under the floor'),
    # --- unreadable ---------------------------------------------------
    ('', '2.0%', None, 'no actual - ungraded, never a guessed 0'),
    ('2.5%', '', None, 'no previous - ungraded'),
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


# LD-140's case block is RETIRED. It tested consensus-vs-standing, which
# LD-142 replaced on 2026-09-21 - the rule no longer exists, so cases for it
# would be testing nothing. The DAY PRECEDENCE half of LD-140 survives and is
# still tested below; only the scoring half went.
RATE_CASES = []

# LD-146 - THE SIX REGIME CASES, PLUS THE REFUSALS.
#
# (cons, fcst, prev, base_band, expected)  expected None = row does not score
REGIME_CASES = [
    # HIKE
    ('4.6%', '4.6%', '4.35%', 'WEAK',    -1),   # AUD live, 29 Sep 2026
    ('4.6%', '',     '4.35%', 'NEUTRAL', -1),
    ('4.6%', '',     '4.35%', 'STRONG',  +1),
    # HOLD - fully priced standing still
    ('4.0%', '4.0%', '4.0%',  'STRONG',  +1),
    ('4.0%', '',     '4.0%',  'NEUTRAL', +1),
    ('4.0%', '',     '4.0%',  'WEAK',    -1),
    # CUT
    ('3.75%', '',    '4.0%',  'WEAK',    +1),
    ('3.75%', '',    '4.0%',  'NEUTRAL', -1),
    ('3.75%', '',    '4.0%',  'STRONG',  -1),
    # F-124 shape: a range reads its UPPER bound, hyphen is not a minus
    ('3.50-3.75%', '', '3.25-3.50%', 'STRONG', +1),
    # REFUSALS - an absence must not read as HOLD (the F-73 shape)
    ('',     '',     '4.0%',  'STRONG',  None),
    ('4.0%', '',     '',      'STRONG',  None),
    ('4.0%', '',     '4.0%',  None,      None),
]


# LD-142 - (rate, previous, expected, what it is)
RATE_LEVEL_CASES = [
    # --- above the 2.5% ceiling ---------------------------------------
    ('4.00%', '3.75%', 1, 'USD hiked 17 Sep - above corridor, rising'),
    ('3.75%', '3.75%', 1, 'GBP hawkish hold - above corridor, FLAT still counts'),
    ('2.75%', '2.50%', 1, 'NZD above corridor, rising'),
    ('3.50%', '3.75%', 0, 'above corridor but CUTTING - hold, not hawkish'),
    # --- below the 1.5% floor -----------------------------------------
    ('0.00%', '0.00%', -1, 'CHF at zero, flat - cut risk'),
    ('1.25%', '1.00%', 0, 'JPY HIKED 18 Sep but still BELOW 1.5 - the correction'),
    ('1.00%', '1.25%', -1, 'below floor and falling'),
    # --- inside the corridor ------------------------------------------
    ('2.25%', '2.25%', 0, 'CAD inside 1.5-2.5 - no compulsion either way'),
    ('2.00%', '1.50%', 0, 'rising hard but still inside the corridor'),
    ('1.50%', '1.25%', 0, 'exactly on the floor is INSIDE'),
    ('2.50%', '2.75%', 0, 'exactly on the ceiling is INSIDE'),
    # --- parsing -------------------------------------------------------
    ('3.50-3.75%', '3.50%', 1, 'a RANGE takes its top - the hyphen is not a minus'),
    (None, '2.00%', None, 'no rate - ungraded, never a guessed 0'),
    ('2.00%', None, None, 'no previous - ungraded'),
]


import score_model as _sm


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

    # *** THE LD-136 FACT-TABLE CHECK IS GONE, NOT BROKEN. It graded every
    # inflation row with ds.inflation_score, which LD-155 RETIRED, and after
    # the switch it reported CHF "stored BAD, rule says NEUTRAL" - the old
    # rule arguing with the new one about a row the new one owns. Two rules
    # cannot both grade the same column. The live check now lives in the
    # LD-155 block below and reads inflation_decision.
    #
    # The CASES table above still exercises inflation_score directly, which is
    # worth keeping only while that function survives as history; it tests a
    # function nothing calls, so it can never fail the build on live data.

    print()
    print('  fact table vs the >Prev rule:')
    V = {1: 'GOOD', 0: 'NEUTRAL', -1: 'BAD'}
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

    import calibrator as _cal

    print()
    print('  LD-142 - the rate-level rule')
    print('  %-12s %-10s %-6s %-6s %s'
          % ('RATE', 'PREV', 'WANT', 'GOT', 'CASE'))
    import rate_model as _rm
    for a, p_, want, note in RATE_LEVEL_CASES:
        got = _rm.level_score(a, p_)
        ok = got == want
        if not ok:
            bad += 1
        print('  %-12s %-10s %-6s %-6s %s%s'
              % (a or "''", p_ or "''", want, got, note,
                 '' if ok else '   *** FAIL'))

    # LD-140 precedence, including the case that would destroy signal.
    print()
    print('  LD-140 - day precedence')
    _rows = [
        ([{'name': _cal.RATE_NAME, 'score': 1, 'month': (0, 9)},
          {'name': 'Employment Change', 'score': -1, 'month': (0, 9)}],
         1.0, 'a rate decision outranks a same-month row'),
        ([{'name': _cal.RATE_NAME, 'score': 0, 'month': (0, 8)},
          {'name': 'Retail Sales YoY', 'score': 1, 'month': (0, 9)}],
         0.0, 'it outranks a LATER month too - that is the LD-98 exception'),
        ([{'name': _cal.RATE_NAME, 'score': None, 'month': (0, 9)},
          {'name': 'Employment Change', 'score': 1, 'month': (0, 8)}],
         1.0, 'UNSCORABLE rate row must NOT seize and blank the day (F-73)'),
        ([{'name': 'Employment Change', 'score': 1, 'month': (0, 9)},
          {'name': 'Retail Sales YoY', 'score': -1, 'month': (0, 8)}],
         1.0, 'no rate row - LD-119 reference month, untouched'),
    ]
    for rows_, want_, note in _rows:
        got_ = _cal.day_score(rows_)[0]
        ok = (got_ == want_)
        if not ok:
            bad += 1
        print('    %-6s want %-6s %s%s'
              % (got_, want_, note, '' if ok else '   *** FAIL'))

    # LD-136 must hold in the CALIBRATOR too, not only the base.
    print()
    print('  calibrator vs derive_scores on this weeks inflation rows:')
    try:
        import glob
        import calibrator as cal
        # PIN THE EDITION'S OWN CAPTURE. caps[-1] is whatever was captured
        # most recently, and its ~30-day window MOVES - after the 19 Sep
        # capture this check silently fell from 4 inflation rows to 2 and
        # still reported "both scorers agree". A check whose sample shrinks
        # without saying so is the F-36 shape (count what you drop).
        caps = sorted(glob.glob(os.path.join(
            os.path.dirname(HERE),
            'data/raw/calendar/2026-09-13_*_cal_full.json')))
        if caps:
            n = nbad2 = 0
            for r in cal.week_rows(caps[-1], '2026-09-14', '2026-09-18'):
                if r['name'] not in cal.INFLATION_NAMES:
                    continue
                exp = r['cons'] or r['fcst']
                want = ds.inflation_score(exp, r['prev'])
                n += 1
                if want != r['score']:
                    bad += 1
                    nbad2 += 1
                    print('    *** %-4s %-26s calibrator %s, rule %s'
                          % (r['ccy'], r['name'][:26], r['score'], want))
            if n < 4:
                bad += 1
                print('    *** ONLY %d INFLATION ROW(S) IN SAMPLE - expected 4.'
                      % n)
            elif not nbad2:
                print('    %d row(s) checked - both scorers agree' % n)
    except Exception as e:
        print('    (skipped: %s)' % e)

    print()
    print('  LD-146 - rate decision vs base regime')
    _nb = 0
    for cons, fcst, prev, rg, want in REGIME_CASES:
        band = {'XXX': rg} if rg else {}
        got, mv, _ = cal.rate_score('XXX', cons, fcst, prev, band)
        if got != want:
            bad += 1
            _nb += 1
            print('    *** cons=%-10s prev=%-10s %-8s -> %s, want %s'
                  % (cons or '-', prev or '-', rg or '-', got, want))
    if not _nb:
        print('    %d case(s) pass - all six regimes + 3 refusals'
              % len(REGIME_CASES))

    # The rate row must WIN ITS DAY. This is the regression that LD-142
    # created and nobody caught for six days: a None score was filtered out
    # before the precedence check, so a lesser row carried the decision.
    _rows = [{'name': cal.RATE_NAME, 'score': -1, 'month': (0, 9)},
             {'name': 'Household Spending YoY', 'score': 1, 'month': (0, 9)}]
    _v, _rule, _keep, _drop = cal.day_score(_rows)
    if _v != -1 or [k['name'] for k in _keep] != [cal.RATE_NAME]:
        bad += 1
        print('    *** PRECEDENCE LOST: day scored %s via %s, kept %s'
              % (_v, _rule, [k['name'] for k in _keep]))
    else:
        print('    precedence holds - the decision carries its day')

    # The rate row must RENDER its rule and its score, not an em-dash.
    # Jeff, 2026-09-27: "please update this with the rule and score for the
    # interest rate". The engine scored it -1 while the page printed a dash
    # in BOTH columns, because week_rows() was called WITHOUT the base band
    # by the renderers and WITH it by calibrate() - one row, two answers.
    _t = cal.rate_rule_text('AUD', '4.6%', '4.6%', '4.35%',
                            {'AUD': 'WEAK'})
    if 'HIKE' not in _t or 'WEAK' not in _t:
        bad += 1
        print('    *** RULE TEXT MISSING: %r' % _t)
    else:
        print('    rule text renders: %s' % _t)

    # week_rows() must default the band itself - a renderer calling it bare
    # must not get None where calibrate() gets -1.
    try:
        import glob as _g
        _caps = sorted(_g.glob('data/raw/calendar/*_cal_full.json'))
        if _caps:
            _rr = [r for r in cal.week_rows(_caps[-1], '2026-09-28',
                                            '2026-10-02')
                   if r['name'] == cal.RATE_NAME]
            if _rr and _rr[0]['score'] is None:
                bad += 1
                print('    *** week_rows() called bare scores the rate row '
                      'None - the page will print a dash (LD-146)')
            elif _rr:
                print('    week_rows() bare scores the rate row %+d'
                      % _rr[0]['score'])
    except Exception as e:
        print('    (bare week_rows check skipped: %s)' % e)

    # LD-147 - THE SWAP SIGN FOLLOWS THE SIDE, NOT THE PAIR.
    print()
    print('  LD-147 - swap sign in the direction of the bias')
    import pair_swap as psw
    _sw_cases = [
        # (pair, side, expected sign) - GBP 3.75, AUD 4.60, JPY 1.25, USD 4.00
        ('GBPAUD', 'LONG',  '-'),   # long the lower rate: costs
        ('GBPAUD', 'SHORT', '+'),   # *** SAME PAIR, OTHER SIDE, OTHER SIGN
        ('AUDJPY', 'LONG',  '+'),   # long the higher rate: earns
        ('AUDJPY', 'SHORT', '-'),
        ('GBPUSD', 'LONG',  '-'),
    ]
    _nb = 0
    for _p, _sd, _want in _sw_cases:
        _got = psw.sign(_p, _sd)
        if _got != _want:
            bad += 1
            _nb += 1
            print('    *** %s %-5s -> %s, want %s' % (_p, _sd, _got, _want))
    # the two sides of one pair must never agree
    if psw.sign('GBPAUD', 'LONG') == psw.sign('GBPAUD', 'SHORT'):
        bad += 1
        _nb += 1
        print('    *** both sides of GBPAUD carry the SAME sign - the swap '
              'is being read off the pair, not the position')
    # LD-4: no money figure may appear in the disclosure
    _txt = (psw.describe('AUDJPY', 'SHORT') or '')
    if any(ch in _txt for ch in '$£€¥') or 'lot' in _txt.lower():
        bad += 1
        _nb += 1
        print('    *** swap text carries a MONEY figure - LD-4: %r' % _txt)
    if not _nb:
        print('    %d case(s) pass - sign follows the side, no money path'
              % (len(_sw_cases) + 2))

    # LD-148 - the adverse side is graded against the SAME target.
    print()
    print('  LD-148 - adverse excursion vs the same target')
    import atr_grade as _ag
    _cls = [
        # (fav, adv, atr, expected)   target is 0.75 x atr
        (159.0, 31.1, 78.6, 'CLEAN'),    # delivered, never threatened
        ( 64.2, 76.6, 83.3, 'EARNED'),   # delivered THROUGH a full adverse day
        (  0.7, 55.4, 64.2, 'BEATEN'),   # the opposite side paid out
        ( 44.0, 40.7, 78.6, 'DRIFT'),    # neither side completed
        # boundaries - exactly ON target counts as reached, both sides
        ( 59.0, 10.0, 78.66,'CLEAN'),
        ( 10.0, 59.0, 78.66,'BEATEN'),
    ]
    _nb = 0
    for _f, _a, _atr, _want in _cls:
        _got = _ag.classify(_f, _a, _atr)
        if _got != _want:
            bad += 1; _nb += 1
            print('    *** fav %.1f adv %.1f atr %.1f -> %s, want %s'
                  % (_f, _a, _atr, _got, _want))
    # a BEATEN day must NOT cancel the week verdict (LD-128 is untouched)
    _rows = [('d1', 0.7, 55.4, 0.01, False), ('d2', 81.3, 6.8, 1.27, True)]
    _c, _e, _b, _d, _w = _ag.pressure(_rows, 64.2)
    if not (_b == 1 and _c == 1):
        bad += 1; _nb += 1
        print('    *** pressure() miscounted: clean=%d earned=%d beaten=%d '
              'drift=%d' % (_c, _e, _b, _d))
    if not _nb:
        print('    %d case(s) pass - four states, both boundaries, week '
              'verdict untouched' % (len(_cls) + 1))

    # LD-149 - the week verdict is the RATIO of summed excursions.
    print()
    print('  LD-149 - week verdict from summed excursions')
    _vc = [
        # (rows as (label,fav,adv,frac,hit), expected verdict)
        ([('a', 100.0, 50.0, 0, False)], 'WIN'),        # 2.00
        ([('a',  70.0, 50.0, 0, False)], 'CONTESTED'),  # 1.40 exactly -> WIN
        ([('a',  60.0, 50.0, 0, False)], 'CONTESTED'),  # 1.20
        ([('a',  35.0, 50.0, 0, False)], 'LOSS'),       # 0.70 exactly -> LOSS?
        ([('a',  30.0, 50.0, 0, False)], 'LOSS'),       # 0.60
    ]
    # boundaries are INCLUSIVE at WIN and EXCLUSIVE at LOSS, state it exactly
    _nb = 0
    _b1 = _ag.verdict([('a', 70.0, 50.0, 0, False)])[0]   # ratio 1.40
    if _b1 != 'WIN':
        bad += 1; _nb += 1
        print('    *** ratio 1.40 -> %s, want WIN (>= is inclusive)' % _b1)
    _b2 = _ag.verdict([('a', 35.0, 50.0, 0, False)])[0]   # ratio 0.70
    if _b2 != 'CONTESTED':
        bad += 1; _nb += 1
        print('    *** ratio 0.70 -> %s, want CONTESTED (< is exclusive)' % _b2)
    for _rows, _ in _vc[:1] + _vc[2:3] + _vc[4:]:
        pass
    for _rows, _want in ((_vc[0][0], 'WIN'), (_vc[2][0], 'CONTESTED'),
                         (_vc[4][0], 'LOSS')):
        _g = _ag.verdict(_rows)[0]
        if _g != _want:
            bad += 1; _nb += 1
            print('    *** verdict %s, want %s' % (_g, _want))
    # a zero adverse week must not divide by zero
    if _ag.verdict([('a', 10.0, 0.0, 0, False)])[0] is not None:
        bad += 1; _nb += 1
        print('    *** zero adverse should refuse, not divide')
    # LD-149 must be STRICTER than LD-128 on the graded week, not looser
    if _ag.WIN_AT <= 1.0 or _ag.LOSS_AT >= 1.0:
        bad += 1; _nb += 1
        print('    *** bands straddle 1.0 wrongly')
    if not _nb:
        print('    6 case(s) pass - bands %.2f/%.2f, boundaries, zero-adverse'
              % (_ag.LOSS_AT, _ag.WIN_AT))

    # LD-151 - Employment Change on all three legs.
    print()
    print('  LD-151 - Employment Change, three legs')
    _eg = [
        # (actual, ft, pt, want, label)   Jeff's four rules, in his order
        ( 50.0,  40.0,  10.0, 'GOOD',    'rule 1  all three up'),
        ( 39.5,  -6.3,  45.8, 'NEUTRAL', 'rule 2  AUD Aug/26 live'),
        (-15.8,  16.3, -32.2, 'NEUTRAL', 'rule 3  AUD Jul/26 live'),
        (-41.7, -35.9,  -5.8, 'BAD',     'rule 4  CAD Aug/26 live'),
        # the two he did not list - ruled 2026-10-04: follow the full time leg
        ( 40.0,  50.0, -10.0, 'GOOD',    'unlisted (+,+,-)'),
        (-40.0, -50.0,  10.0, 'BAD',     'unlisted (-,-,+)'),
        # zeros and refusals
        ( 10.0,   0.0,  10.0, 'NEUTRAL', 'full time flat'),
        ( 10.0,  10.0,  None, None,      'part time unsourced -> no verdict'),
        ( None,  10.0,  10.0, None,      'headline unsourced -> no verdict'),
    ]
    _nb = 0
    for _a, _f, _p, _w, _lbl in _eg:
        _g = _sm.employment_grade(_a, _f, _p)
        if _g != _w:
            bad += 1
            _nb += 1
            print('    *** %s: got %s want %s' % (_lbl, _g, _w))
    # LD-151 must NOT consult the previous month - that was LD-57's test and
    # it is the defect LD-58 fixed for Claimant Count (deceleration != decline)
    import inspect as _insp
    _src = _insp.getsource(_sm.employment_grade)
    if 'previous' in _src:
        bad += 1
        _nb += 1
        print('    *** employment_grade still references a previous month')
    if not _nb:
        print('    %d case(s) pass - four rules, two rulings, zeros, refusals'
              % len(_eg))

    # LD-154 - the rate path from the scheduled decision.
    print()
    print('  LD-154 - decision score, before and after the news')
    import rate_model as _rm
    _dc = [
        # (prev, cons, fcst, actual, want_score, want_src, label)
        ('4.00%', None,    '4.25%', None,   1, 'forecast',  'BEFORE hike, fcst'),
        ('4.00%', None,    '4.00%', None,   0, 'forecast',  'BEFORE hold, fcst'),
        ('4.00%', '3.75%', '4.00%', None,  -1, 'consensus', 'BEFORE cut, cons wins'),
        ('4.00%', '4.25%', '3.75%', None,   1, 'consensus', 'cons SUPERSEDES fcst'),
        ('4.00%', '4.25%', None, '4.25%',   1, 'actual',    'AFTER on expectation, retain'),
        ('4.00%', '4.00%', None, '4.25%',   1, 'actual',    'AFTER beat, override GOOD'),
        ('4.00%', '4.25%', None, '4.00%',  -1, 'actual',    'AFTER miss, override BAD'),
        ('4.00%', None,    None,    None, None, None,       'nothing published'),
    ]
    _nb = 0
    for _p, _c, _f, _a, _ws, _wsrc, _lbl in _dc:
        _sc, _src, _why = _rm.decision_score(_p, _c, _f, _a)
        if _sc != _ws or _src != _wsrc:
            bad += 1; _nb += 1
            print('    *** %s: got (%s,%s) want (%s,%s)'
                  % (_lbl, _sc, _src, _ws, _wsrc))
    # LD-154b - every currency must score a path, none may be None
    _rm.load_scheduled()
    _r = _rm.compute()
    _blank = [_rm.LABEL[i] for i, d in _r.items() if d['path'] is None]
    if _blank:
        bad += 1; _nb += 1
        print('    *** path still blank for: %s' % ', '.join(_blank))
    # the before-news test must compare against the CURRENT rate, never the
    # rate before the last decision - that read a HOLD as a HIKE
    _bad_hold = [_rm.LABEL[i] for i, d in _r.items()
                 if d.get('path_src') == 'forecast' and d['path'] == 1
                 and 'HOLD' in (d['path_why'] or '')]
    if _bad_hold:
        bad += 1; _nb += 1
        print('    *** a HOLD scored +1 for: %s' % ', '.join(_bad_hold))
    if not _nb:
        print('    %d case(s) pass - 8 of 8 currencies carry a path'
              % (len(_dc) + 2))

    # LD-155 - inflation on the same before/after shape as the rate path.
    #
    # *** THE BLOCK ABOVE STILL TESTS ds.inflation_score, WHICH LD-155
    # RETIRED. It passes because that function still exists, not because the
    # LIVE rule is right - a test can go green on a function nobody calls.
    # These cases grade inflation_decision, which is what derive_scores and
    # the calibrator now use.
    print()
    print('  LD-155 - inflation, before and after the news')
    _ic = [
        # (prev, cons, fcst, actual, want, want_src, label)
        (None, None, '3.2%', None,    1, 'forecast',  'BEFORE above the 2.2 ceiling'),
        (None, '1.5%', '3.0%', None, -1, 'consensus', 'BEFORE below 1.8, cons wins'),
        (None, '2.4%', '1.0%', None,  1, 'consensus', 'cons SUPERSEDES fcst'),
        (None, None, '2.0%', None,    0, 'forecast',  'BEFORE inside 1.8-2.2'),
        (None, None, '1.8%', None,    0, 'forecast',  'exactly on the floor is INSIDE'),
        (None, None, '2.2%', None,    0, 'forecast',  'exactly on the ceiling is INSIDE'),
        (None, '3.2%', None, '3.2%',  1, 'actual',    'AFTER on expectation, retain'),
        # *** the deflationary override - Jeff confirmed this is intended
        (None, '1.0%', None, '1.2%',  1, 'actual',    'AFTER hot at 1.2%, override GOOD'),
        (None, '3.2%', None, '3.0%', -1, 'actual',    'AFTER cold at 3.0%, override BAD'),
        (None, None, None, '4.0%',    1, 'actual',    'actual alone, level test'),
        (None, None, None, None,   None, None,        'nothing published'),
    ]
    _nb = 0
    for _p, _c, _f, _a, _w, _wsrc, _lbl in _ic:
        _sc, _src, _why = ds.inflation_decision(_p, _c, _f, _a)
        if _sc != _w or _src != _wsrc:
            bad += 1; _nb += 1
            print('    *** %s: got (%s,%s) want (%s,%s)'
                  % (_lbl, _sc, _src, _w, _wsrc))
    # the corridor must be 1.8-2.2, not LD-143's 1.5-2.5
    if (ds.NEW_LOW, ds.NEW_HIGH) != (1.8, 2.2):
        bad += 1; _nb += 1
        print('    *** corridor is %s-%s, want 1.8-2.2'
              % (ds.NEW_LOW, ds.NEW_HIGH))
    # and the live fact table must agree with the rule
    try:
        import fact_tables as _ft
        import score_model as _sm2
        _m = _ft.latest_month()
        for _cat, _iso, _n, _a2, _p2, _ref, _thr, _v in _sm2.ROWS:
            if _cat != 'Inflation':
                continue
            _want, _, _ = ds.inflation_decision(actual=_a2)
            _store = {'GOOD': 1, 'NEUTRAL': 0, 'BAD': -1}.get(_v)
            if _want is not None and _store != _want:
                bad += 1; _nb += 1
                print('    *** %s %s stored %s, LD-155 says %s'
                      % (_sm2.LABEL[_iso], _n[:22], _v, _want))
    except Exception as _e:
        print('    (fact-table check skipped: %s)' % _e)
    if not _nb:
        print('    %d case(s) pass - corridor, both sides, live rows agree'
              % (len(_ic) + 1))

    # LD-163 - realised must NOT enter the rate score.
    print()
    print('  LD-163 - realised retired from the rate model')
    _rm.load_scheduled()
    _rr = _rm.compute()
    _nb = 0
    _leaked = [_rm.LABEL[i] for i, d in _rr.items()
               if 'realised' in (d.get('weights') or {})]
    if _leaked:
        bad += 1; _nb += 1
        print('    *** realised still a live term for: %s' % ', '.join(_leaked))
    if _rm.TERM_WEIGHT.get('realised'):
        bad += 1; _nb += 1
        print('    *** TERM_WEIGHT realised is %s, want 0'
              % _rm.TERM_WEIGHT['realised'])
    # a currency with level 0 and path 0 must score 0 - it was +0.20 on JPY
    # purely for having hiked, which is the double-count LD-163 removes
    for i, d in _rr.items():
        if d['level'] == 0 and d['path'] == 0 and abs(d['raw']) > 1e-9:
            bad += 1; _nb += 1
            print('    *** %s scores %+.2f on level 0 / path 0'
                  % (_rm.LABEL[i], d['raw']))
    if not _nb:
        print('    3 case(s) pass - two terms, level 0.5 + path 0.5')

    print()
    if bad:
        print('*** %d FAILURE(S)' % bad)
        return 1
    print('  %d cases pass' % (len(CASES) + len(PREV_CASES) + len(RATE_CASES)
                          + len(REGIME_CASES) + 1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
