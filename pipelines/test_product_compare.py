# -*- coding: utf-8 -*-
"""Tests for LD-175, the week-by-week product comparison."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import product_compare as PC

fails = []


def ok(name, cond, detail=''):
    print('  %-58s %s' % (name, 'PASS' if cond else 'FAIL'))
    if not cond:
        fails.append((name, detail))


# 1 - the refusal is the feature
who, why = PC.verdict()
ok('verdict refuses below MIN_WEEKS', who is None, why)

# 2 - and it stops refusing once there is enough
fake = [{'week': 'w%d' % i, 'sessions': [1, 2, 3, 4],
         'macro': (0, 0.20, 3, 4, {}, 0), 'rates': (0, 0.05, 4, 4, {}, 0),
         'lead': 0.15} for i in range(PC.MIN_WEEKS)]
who, _ = PC.verdict(fake)
ok('verdict calls a winner at MIN_WEEKS', who == 'MACRO', str(who))

# 3 - F-73: a missing ATR is dropped, never treated as 1 or 0
wk = {'d1': [{'pair': 'X', 'fav_pips': '100', 'adv_pips': '0',
              'atr_pips': ''},
             {'pair': 'Y', 'fav_pips': '50', 'adv_pips': '0',
              'atr_pips': '50'}]}
s = PC.score(wk, ['d1'])
ok('row with no ATR is dropped (F-73)',
   s[2] == 1 and s[5] == 1 and abs(s[0] - 1.0) < 1e-9, str(s[:3]))

# 4 - common sessions must INTERSECT; a union would compare 5 days to 4
A = {'w': {'d1': [], 'd2': [], 'd3': []}}
B = {'w': {'d2': [], 'd3': [], 'd4': []}}
ok('common_sessions intersects, never unions',
   PC.common_sessions(A, B, 'w') == ['d2', 'd3'],
   str(PC.common_sessions(A, B, 'w')))

# 5 - the whole point: two instruments, same ATR-multiple
wk = {'d1': [{'pair': 'BIG', 'fav_pips': '128', 'adv_pips': '0',
              'atr_pips': '128'},
             {'pair': 'SML', 'fav_pips': '31', 'adv_pips': '0',
              'atr_pips': '31'}]}
s = PC.score(wk, ['d1'])
ok('ATR normalisation equalises instruments',
   abs(s[4]['BIG'] - s[4]['SML']) < 1e-9, str(s[4]))

# 6 - the live ledgers must reproduce the published retro
t = PC.table()
ok('live table has the 26 Oct week on 4 common sessions',
   len(t) == 1 and len(t[0]['sessions']) == 4,
   str([(w['week'], len(w['sessions'])) for w in t]))
ok('macro +0.78 ATR as published',
   t and abs(t[0]['macro'][0] - 0.78) < 0.02, str(t[0]['macro'][0] if t else None))
ok('rates -1.36 ATR as published',
   t and abs(t[0]['rates'][0] + 1.36) < 0.02, str(t[0]['rates'][0] if t else None))

# --- LD-176, the lock ------------------------------------------------------
ok('LD-176 check_lock passes while frozen values hold', PC.check_lock())

_orig = PC.MIN_WEEKS
try:
    PC.MIN_WEEKS = 1
    fired = False
    try:
        PC.verdict([{'week': 'w', 'sessions': [1],
                     'macro': (0, 0.2, 1, 1, {}, 0),
                     'rates': (0, 0.1, 1, 1, {}, 0), 'lead': 0.1}])
    except SystemExit:
        fired = True
    ok('LD-176 verdict() refuses to run on a moved MIN_WEEKS', fired)
finally:
    PC.MIN_WEEKS = _orig

ok('LD-176 LOCK records all three corrections',
   PC.LOCK['corrections'] == ('common-sessions', 'atr-normalised',
                             'per-pair-day'), str(PC.LOCK['corrections']))

print()
print('FAILURES: %d' % len(fails))
if fails:
    raise SystemExit(1)
