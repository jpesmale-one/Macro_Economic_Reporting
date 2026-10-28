# -*- coding: utf-8 -*-
"""LD-174 guards. python -B pipelines/test_risk_index.py

F-158: invariants and provenance, never today's numbers.
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import risk_index as RI
import fact_tables as ft
import pair_select as ps

FAIL = []


def ck(name, got, want):
    ok = (abs(got - want) < 1e-9) if isinstance(want, float) else (got == want)
    print('  %-58s %s' % (name, 'PASS' if ok else 'FAIL got=%r' % (got,)))
    if not ok:
        FAIL.append(name)


print('*** the basket must be EXTERNAL to the currencies it grades.')
ck('four legs declared', len(RI.SERIES), 4)
ck('no leg is an FX pair',
   all(len(s[1].split(':')[-1]) > 6 or not s[1].split(':')[-1].isalpha()
       or s[0] in ('SPX', 'VIX', 'DAX', 'NI225') for s in RI.SERIES), True)
ck('three regions plus a volatility leg',
   sorted(set(s[3] for s in RI.SERIES)),
   ['Asia', 'Europe', 'United States', 'global'])
ck('exactly one leg is inverted', sum(1 for s in RI.SERIES if s[4]), 1)
ck('and it is the volatility leg',
   [s[0] for s in RI.SERIES if s[4]], ['VIX'])

print()
print('*** F-174 - a US open must NOT date to the next day.')
#     SPX stamps 13:30 UTC; a +12h shift would roll it forward.
ck('SPX 13:30 UTC keeps its own date',
   RI.session_of(1793021400), '2026-10-26')
ck('Tokyo 00:00 UTC keeps its own date',
   RI.session_of(1792972800), '2026-10-26')
ck('Frankfurt 08:00 UTC keeps its own date',
   RI.session_of(1793001600), '2026-10-26')

print()
print('*** all four legs must be present, with history.')
st = RI.status()
ck('four series on disk', len(st), 4)
ck('every one has bars', all(r[2] > 0 for r in st), True)
ck('every one has 60+ bars', all(r[2] >= 60 for r in st), True)

print()
print('*** no weekday gaps in the equity legs (the F-174 tell).')
for key in ('SPX', 'DAX'):
    ds = sorted(RI.series(key))[-40:]
    gaps = []
    for a, b in zip(ds, ds[1:]):
        da, db = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
        n = (db - da).days
        if n > 1 and not (da.weekday() == 4 and n == 3):
            gaps.append('%s->%s' % (a, b))
    # a real holiday is allowed; more than two in 40 sessions is a bug
    ck('%s has at most 2 non-weekend gaps in 40' % key, len(gaps) <= 2, True)

print()
print('*** the score is a MEAN OF SIGNS, bounded and symmetric.')
lbl, sc, d = RI.tone(sorted(RI.series('DAX'))[-2])
ck('score within -1..+1', -1.0 <= sc <= 1.0, True)
ck('votes sum to the score',
   round(sc, 9),
   round(sum(v for _p, v in d['legs'].values()) / float(len(RI.SERIES)), 9))
ck('a flat leg does not vote',
   all(v == 0 for p, v in d['legs'].values()
       if p is not None and abs(p) < RI.DEADBAND), True)

print()
print('*** bands ordered, and the label follows the score.')
ck('MILD below CLEAR', RI.MILD < RI.CLEAR, True)
ck('CLEAR needs 3 of 4 legs', RI.CLEAR > 0.5, True)

print()
print('*** F-73 - no guessed verdicts.')
ck('a missing session returns None', RI.tone('1999-01-01')[0], None)
ck('MIXED has no alignment', RI.aligns('RISK ON', 'MIXED'), 'n/a')
ck('an EITHER pair has no alignment', RI.aligns('EITHER', 'RISK ON'), 'n/a')
ck('RISK ON on a risk-on day', RI.aligns('RISK ON', 'mild RISK ON'),
   'ALIGNED')
ck('RISK ON on a risk-off day', RI.aligns('RISK ON', 'RISK OFF'), 'AGAINST')

print()
print('*** alignment reads pair_select, it does not re-derive a category.')
ck('CADCHF LONG is RISK ON per the closed set',
   ps.CATEGORY.get((ft.ROLE['CAD'], ft.ROLE['CHF'])), 'RISK ON')

print()
print('FAILURES: %d' % len(FAIL))
sys.exit(1 if FAIL else 0)
