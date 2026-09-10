# -*- coding: utf-8 -*-
"""R-39 - the timezone guard. Both real findings, reintroduced as tests.

A guard is only worth trusting once it has FAILED on the bug it was written
for. Each case below is an actual error from 2026-09-10, with the wrong
answer recorded beside the right one.

    python pipelines/test_phtime.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phtime as pt

FAIL = []


def ok(cond, label, got=None, want=None):
    if cond:
        print('  PASS  %s' % label)
    else:
        print('  FAIL  %s' % label)
        if want is not None:
            print('          got  %s' % got)
            print('          want %s' % want)
        FAIL.append(label)


print('R-39  TIMEZONE GUARD')
print()

# ---------------------------------------------------------------- F-107
# TE stores UTC. Jeff read "Sept 8 7:50 AM" on his own UTC+8 screen.
print('F-107  TE stored time is UTC, not PHT')
p = pt.te_pht('2026-09-07', '11:50 PM')
ok(p.strftime('%Y-%m-%d %I:%M %p') == '2026-09-08 07:50 AM',
   'JPY GDP -> 08 Sep 07:50 AM PHT (Jeff verified)',
   p.strftime('%Y-%m-%d %I:%M %p'), '2026-09-08 07:50 AM')

rel = pt.te_utc('2026-09-07', '11:50 PM')
hourly = [1788807600, 1788811200, 1788814800, 1788818400,
          1788822000, 1788825600, 1788829200]
b = pt.containing_bar(rel.timestamp(), hourly, 3600)
ok(b == 1788822000, 'containing 60m bar is 23:00 UTC', b, 1788822000)
ok(b != 1788793200, 'NOT the 15:00 UTC bar I originally used (8h early)')

# ---------------------------------------------------------------- F-106
# A daily bar's LABEL is not its calendar day. OANDA opens 21:00 UTC.
print()
print('F-106  a daily bar label is not a calendar day')
rel2 = pt.te_utc('2026-09-02', '01:30 AM')
daily = [1788210000, 1788296400, 1788382800, 1788469200]
b2 = pt.containing_bar(rel2.timestamp(), daily, 86400)
ok(b2 == 1788296400,
   'AUD GDP sits in the bar opening 01 Sep 21:00 UTC', b2, 1788296400)
ok(b2 != 1788382800,
   'NOT the bar I labelled "Wed 02 Sep" (the -11.6 pip one)')
ok(pt.bar_utc(b2).hour == pt.OANDA_DAILY_OPEN_UTC,
   'daily bars open at %02d:00 UTC' % pt.OANDA_DAILY_OPEN_UTC)

# ---------------------------------------------------------------- misc
print()
print('conventions')
ok(pt.te_utc('2026-09-02', '') is None,
   'a row with no published time returns None, never a guessed midnight')
ok(pt.bar_pht(1788822000).utcoffset().total_seconds() == 8 * 3600,
   'bar_pht returns UTC+8')
d = pt.describe(1788822000, 'bar')
ok('UTC' in d and 'PHT' in d, 'describe() shows BOTH zones on one line')

# ---------------------------------------------------------------- F-108
# I quoted TE's raw stored date instead of routing it through te_pht().
# 23% of major-currency rows land on a DIFFERENT calendar day in PHT.
print()
print('F-108  the raw stored date is NOT the PHT date')
p2 = pt.te_pht('2026-09-16', '10:45 PM')
ok(p2.strftime('%Y-%m-%d') == '2026-09-17',
   'NZ GDP stored 16 Sep -> Thu 17 Sep PHT (Jeff screenshot)',
   p2.strftime('%Y-%m-%d'), '2026-09-17')
ok(p2.strftime('%H:%M') == '06:45', 'at 06:45 PHT', p2.strftime('%H:%M'), '06:45')
# any TE time from 16:00 UTC onward rolls the PHT date forward
rolled = [t for t in ('04:00 PM', '10:45 PM', '11:50 PM')
          if pt.te_pht('2026-09-16', t).strftime('%Y-%m-%d') != '2026-09-16']
ok(len(rolled) == 3,
   'every TE time >= 16:00 UTC rolls the PHT date forward', len(rolled), 3)

print()
if FAIL:
    print('*** %d FAILURE(S): %s' % (len(FAIL), '; '.join(FAIL)))
    sys.exit(1)
print('all timezone checks pass')
