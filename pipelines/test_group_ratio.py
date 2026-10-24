# -*- coding: utf-8 -*-
"""LD-169 / F-163 guards. Run: python -B pipelines/test_group_ratio.py"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atr_grade as ag
import group_ratio as gr

FAIL = []


def ck(name, got, want, tol=1e-9):
    ok = (abs(got - want) <= tol) if isinstance(want, float) else (got == want)
    print('  %-58s %s' % (name, 'PASS' if ok else 'FAIL got=%r want=%r'
                          % (got, want)))
    if not ok:
        FAIL.append(name)


print('*** THE DECIDER - B must reproduce LD-149 when nothing is grouped.')
print('    If this ever fails, LD-149 bands no longer calibrate the stat.')
un = {'EURUSD': (100., 80.), 'GBPJPY': (120., 90.),
      'AUDCAD': (70., 110.), 'NZDCHF': (90., 95.)}
pooled = (sum(v[0] for v in un.values()) / sum(v[1] for v in un.values()))
r, _ = gr.set_ratio(un)
ck('uncorrelated set equals LD-149 pooled ratio', round(r, 9),
   round(pooled, 9))
rows = [('d', v[0], v[1], 0, False) for v in un.values()]
ck('and equals atr_grade.week_ratio on the same pips',
   round(r, 9), round(ag.week_ratio(rows), 9))

print()
print('*** F-163 - grouping must not depend on input order.')
S = ['CADCHF', 'NZDCHF', 'GBPCHF', 'GBPAUD']
seen = set(repr(gr.groups(list(o))) for o in itertools.permutations(S))
ck('one grouping across all 24 orderings', len(seen), 1)
ck('the CHF view groups, GBPAUD stays single',
   gr.groups(S), [['CADCHF', 'GBPCHF', 'NZDCHF'], ['GBPAUD']])

print()
print('*** no transitive collapse - a chain must not become one blob.')
ck('GBPAUD not swallowed via GBP->GBPCHF->CHF',
   len(gr.groups(S)), 2)

print()
print('*** correlated legs count ONCE, and nothing is discarded.')
w = {'CADCHF': (120., 80.), 'NZDCHF': (118., 82.),
     'GBPCHF': (125.1, 87.9), 'GBPAUD': (220.2, 262.2)}
v, r, det = gr.set_verdict(w)
ck('19-23 Oct set ratio under LD-169', round(r, 3), 0.988)
ck('CHF view ratio preserved', round(det[0][3], 3), 1.453)
ck('GBPAUD ratio preserved', round(det[1][3], 3), 0.840)
ck('losers are kept (3 CHF pairs in the group)', len(det[0][0]), 3)

print()
print('*** a dead pair must not cancel a live one (Method A failure).')
r2, _ = gr.set_ratio({'EURUSD': (100., 50.), 'AUDCAD': (1., 2.)})
ck('pips dominate, not ratios', r2 > 1.5, True)

print()
print('*** bias-aware: a LONG CHF and a SHORT CHF are different views.')
b = {'CADCHF': 'long', 'NZDCHF': 'long', 'GBPCHF': 'short',
     'GBPAUD': 'long'}
g = gr.groups(S, b)
ck('opposite CHF sides are not averaged together',
   all(not ({'CADCHF', 'GBPCHF'} <= set(x)) for x in g), True)

print()
print('*** degenerate input must not raise.')
ck('empty set', gr.set_ratio({})[0], None)
ck('single pair', round(gr.set_ratio({'EURUSD': (10., 5.)})[0], 3), 2.0)
ck('zero adverse', gr.set_ratio({'EURUSD': (10., 0.)})[0], None)

print()
print('FAILURES: %d' % len(FAIL))
sys.exit(1 if FAIL else 0)
