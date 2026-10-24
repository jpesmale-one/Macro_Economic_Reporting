# -*- coding: utf-8 -*-
"""LD-171 / LD-172 guards. Run: python -B pipelines/test_shrink.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shrink as sk
import pull_yields as py
import fact_tables as ft

FAIL = []


def ck(name, got, want):
    ok = got == want if not isinstance(want, float) else abs(got - want) < 1e-9
    print('  %-58s %s' % (name, 'PASS' if ok else 'FAIL got=%r' % (got,)))
    if not ok:
        FAIL.append(name)


B = dict((c, v['total']) for c, v in ft.base_scores().items())

print('*** LD-167 - the live board must be UNCHANGED until Jeff says so.')
ck('SHRINK_K is 0.0 (frozen logic)', sk.SHRINK_K, 0.0)
ck('shrink() at default is byte-identical to the board', sk.shrink(B), B)

print()
print('*** the property that makes shrinkage safe: ORDER NEVER MOVES.')
for k in (0.1, 0.25, 0.5, 0.6, 0.9):
    ck('order preserved at k=%.2f' % k, sk.order_preserved(B, k), True)

print()
print('*** and the spread must actually shrink, or it does nothing.')
s0 = sk.spread(B)
s5 = sk.spread(sk.shrink(B, 0.5))
ck('k=0.5 halves the spread', round(s5 / s0, 6), 0.5)
ck('k=0 leaves the spread alone', sk.spread(sk.shrink(B, 0.0)), s0)

print()
print('*** degenerate input must not raise.')
ck('empty board', sk.shrink({}), {})
ck('single currency', sk.shrink({'USD': 3.0}, 0.5), {'USD': 3.0})
ck('all equal stays equal', sk.shrink({'A': 2.0, 'B': 2.0}, 0.5),
   {'A': 2.0, 'B': 2.0})

print()
print('*** LD-171 - all eight yields present, aligned, and NOT scored.')
st = py.status()
ck('eight currencies tracked', len(st), 8)
ck('every one has bars', all(r[2] > 0 for r in st), True)
ck('all on one session (F-166)', len(set(r[3] for r in st)), 1)
ck('EUR is flagged as a proxy', py.load('EUR')['note'] != '', True)
ck('nothing is marked scored', all(py.load(r[0])['scored'] is False
                                  for r in st), True)

print()
print('*** F-166 - Asian opens must not fall on the previous date.')
ck('JPY 21:00 UTC epoch dates forward', py.session_of(1792702800),
   '2026-10-23')
ck('CAD 10:00 UTC epoch stays put', py.session_of(1792749600),
   '2026-10-23')

print()
print('*** spreads compute and carry the right sign.')
sp = py.spread('AUD', 'CHF')
ck('AUD 2y is above CHF 2y', sp > 0, True)
ck('and the reverse is its negative', round(py.spread('CHF', 'AUD'), 6),
   round(-sp, 6))
print('    AUD-CHF 2y spread = %+.3f pp' % sp)

print()
print('FAILURES: %d' % len(FAIL))
sys.exit(1 if FAIL else 0)
