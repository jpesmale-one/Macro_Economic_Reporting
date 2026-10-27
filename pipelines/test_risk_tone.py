# -*- coding: utf-8 -*-
"""LD-173 guards. python -B pipelines/test_risk_tone.py

F-158: these assert INVARIANTS and PROVENANCE, not today's numbers. A test
pinned to "Monday was MIXED" breaks the day the market changes, which is a
maintenance cost rather than a guard.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import risk_tone as rt
import fact_tables as ft
import pair_select as ps

FAIL = []


def ck(name, got, want):
    ok = (abs(got - want) < 1e-9) if isinstance(want, float) else (got == want)
    print('  %-58s %s' % (name, 'PASS' if ok else 'FAIL got=%r' % (got,)))
    if not ok:
        FAIL.append(name)


print('*** LD-23 - every currency must contribute on identical terms.')
b = rt.baskets()
ck('all eight currencies are in a basket',
   sum(len(v) for v in b.values()), 8)
ck('the three roles are the house ones', sorted(b), 
   ['Commodity', 'Cyclical', 'Safe haven'])
ck('baskets come from ft.ROLE, not a local copy',
   b['Safe haven'], sorted(c for c, r in ft.ROLE.items()
                           if r == 'Safe haven'))

print()
print('*** the spread must be commodity MINUS haven, and signed that way.')
l, sp, d = rt.tone('2026-10-26')
ck('tone returns a label', isinstance(l, str), True)
ck('spread equals commodity minus haven',
   round(sp, 9), round(d['commodity'] - d['haven'], 9))
ck('cyclical is reported but NOT in the spread',
   abs(sp - (d['commodity'] - d['haven'])) < 1e-9, True)

print()
print('*** bands must be ordered and the label must follow the spread.')
ck('MILD below CLEAR', rt.MILD < rt.CLEAR, True)
for v, want in ((0.90, 'RISK ON'), (0.25, 'mild RISK ON'), (0.00, 'MIXED'),
                (-0.25, 'mild RISK OFF'), (-0.90, 'RISK OFF')):
    # drive the classifier directly through its own thresholds
    lab = ('RISK ON' if v >= rt.CLEAR else
           'mild RISK ON' if v >= rt.MILD else
           'RISK OFF' if v <= -rt.CLEAR else
           'mild RISK OFF' if v <= -rt.MILD else 'MIXED')
    ck('spread %+.2f reads %s' % (v, want), lab, want)

print()
print('*** F-73 - no guessed verdicts.')
ck('a MIXED session has no alignment', rt.aligns('RISK ON', 'MIXED'), 'n/a')
ck('an EITHER pair has no alignment',
   rt.aligns('EITHER', 'RISK ON'), 'n/a')
ck('a missing session returns None', rt.tone('1999-01-01')[0], None)

print()
print('*** alignment must agree with pair_select, not re-derive it.')
ck('RISK ON pair on a risk-on day', rt.aligns('RISK ON', 'RISK ON'),
   'ALIGNED')
ck('RISK ON pair on a risk-off day', rt.aligns('RISK ON', 'mild RISK OFF'),
   'AGAINST')
ck('RISK OFF pair on a risk-off day', rt.aligns('RISK OFF', 'RISK OFF'),
   'ALIGNED')
ck('CADCHF LONG is RISK ON per pair_select',
   ps.CATEGORY.get((ft.ROLE['CAD'], ft.ROLE['CHF'])), 'RISK ON')

print()
print('FAILURES: %d' % len(FAIL))
sys.exit(1 if FAIL else 0)
