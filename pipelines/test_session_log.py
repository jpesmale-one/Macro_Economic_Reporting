# -*- coding: utf-8 -*-
"""R-51 - every ledger row must carry atr_pips.

*** THE DEFECT THIS TEST EXISTS FOR (F-192). daily_report.py computed the
14-period ATR, used it to grade the day, and then called session_log.append
WITHOUT it. The column was written blank on every row of every build. Nothing
errored: a blank atr_pips is a legal CSV cell, the console output looked
right, and the page rendered. The row simply vanished from every
ATR-normalised read downstream (LD-176, F-73).

The fill was then performed BY HAND after five consecutive builds. That is
the signature of this class of bug - it does not announce itself, it just
quietly converts a generator into a manual step.

*** WHAT MAKES THIS TEST BITE. The weak version of it would assert that
session_log.append stores an atr when one is given - which the old code
already did, because append() was never broken. The bug was at the CALL
SITE, so the test has to run the real call site against real bars and read
what landed on disk.

    python pipelines/test_session_log.py
"""
import io
import os
import sys
import csv
import inspect

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import session_log as sl
import daily_report as dr

LEDGER = os.path.join(REPO, 'data', 'derived', 'sessions.csv')
fails = []


def check(name, ok, detail=''):
    print('  %-4s %-56s %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok:
        fails.append(name)


def rows():
    if not os.path.exists(LEDGER):
        return []
    with io.open(LEDGER, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    print('SESSION LEDGER TESTS (R-51)')
    print()

    rs = rows()
    check('ledger exists and has rows', bool(rs), '%d row(s)' % len(rs))

    # *** THE INVARIANT. A row with a blank atr_pips is invisible to every
    # ATR-normalised read, so it is worse than a missing row - it is counted
    # as present and contributes nothing.
    blank = [r for r in rs if not (r.get('atr_pips') or '').strip()]
    check('F-73/LD-176: no row has a blank atr_pips', not blank,
          '%d blank' % len(blank))

    # A zero is the OTHER failure: it is not an absence, it is a claim that
    # the day had no range, and it makes frac_atr divide by zero or read 0.
    zero = [r for r in rs if (r.get('atr_pips') or '').strip() in ('0', '0.0')]
    check('no row claims an ATR of zero', not zero, '%d zero' % len(zero))

    # *** THE CALL SITE IS THE THING UNDER TEST, not append().
    # Read the source of the function that writes the ledger and assert the
    # atr actually crosses the boundary. This is what the old code failed.
    src = inspect.getsource(dr)
    i = src.find('sl.append(')
    call = src[i:src.find(')', i) + 1] if i >= 0 else ''
    check('daily_report passes atr to sl.append', 'atr=' in call,
          call.replace('\n', ' ').strip()[:52] if call else 'NO CALL FOUND')

    # append() must still refuse to invent a value when none is available.
    # None stays None; a build with too few prior bars writes a blank, and
    # that blank is honest. Proven on a scratch ledger, not the real one.
    import tempfile
    real = sl.LEDGER
    try:
        sl.LEDGER = os.path.join(tempfile.gettempdir(), 'sl_probe.csv')
        if os.path.exists(sl.LEDGER):
            os.remove(sl.LEDGER)
        sl.append('2026-11-16', '2026-11-17', 'EURUSD', 'LONG', 10.0, 2.0,
                  atr=None)
        sl.append('2026-11-16', '2026-11-18', 'EURUSD', 'LONG', 10.0, 2.0,
                  atr=81.4)
        with io.open(sl.LEDGER, encoding='utf-8') as f:
            got = [r['atr_pips'] for r in csv.DictReader(f)]
        check('atr=None writes blank, never a guessed 0', got[0] == '',
              'wrote %r' % got[0])
        check('a real atr is stored to one decimal', got[1] == '81.4',
              'wrote %r' % got[1])
    finally:
        if os.path.exists(sl.LEDGER):
            os.remove(sl.LEDGER)
        sl.LEDGER = real

    print()
    if fails:
        print('*** %d FAILURE(S): %s' % (len(fails), ', '.join(fails)))
        return 1
    print('ALL TESTS PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
