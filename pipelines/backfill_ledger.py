# -*- coding: utf-8 -*-
"""Backfill a week into the per-session ledger (LD-170) from bars, with ATR.

Usage:  python backfill_ledger.py <week_start> PAIR:SIDE [PAIR:SIDE ...]

The ledger is the only thing that makes a week-by-week comparison possible,
and it is idempotent on (week, session, pair), so re-running a week is safe.

*** ATR IS NOW A FIELD, NOT A NOTE. The first ledger stored only frac_atr
(fav / ATR) and wrote the ATR into free text. That is enough to rank one
week and useless for comparing two products, because an ATR-normalised
measure needs the divisor itself. 16 of 26 historic rows were recoverable
by parsing the note; the rest are regraded here. F-73 - a value that cannot
be recovered is left BLANK, never guessed.
"""
import io
import os
import sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import atr_grade as ag
import session_log as SL


def bars(pair):
    p = os.path.join(HERE, '%s.txt' % pair)
    if not os.path.exists(p):
        return None
    out = []
    for ln in io.open(p, encoding='utf-8'):
        x = ln.split()
        if len(x) >= 5:
            d = (dt.datetime(1970, 1, 1)
                 + dt.timedelta(seconds=int(x[0]) + 12 * 3600)).date()
            out.append((d.isoformat(),) + tuple(float(v) for v in x[1:5]))
    return sorted(out)


def week_sessions(week_start):
    d0 = dt.date.fromisoformat(week_start)
    return [(d0 + dt.timedelta(days=i)).isoformat() for i in range(5)]


def run(week_start, picks):
    days = week_sessions(week_start)
    n = 0
    for pair, side in picks:
        bb = bars(pair)
        if not bb:
            print('  SKIP %s - no bars on disk' % pair)
            continue
        f = ag.pip_factor(pair)
        # LD-128/129: ATR from sessions ENDING BEFORE the graded week.
        prior = [(h, l, c) for d, o, h, l, c in bb if d < week_start]
        if len(prior) < 15:
            print('  SKIP %s - not enough prior bars for ATR' % pair)
            continue
        atr = ag.atr(prior, 14, f)
        for day in days:
            row = [x for x in bb if x[0] == day]
            if not row:
                continue
            _, o, hi, lo, c = row[0]
            fav, adv, frac, hit = ag.grade_day(side, o, hi, lo, f, atr)
            SL.append(week_start, day, pair, side, fav, adv,
                      frac=frac, hit=hit,
                      state=ag.classify(fav, adv, atr),
                      note='regraded from bars', atr=atr)
            n += 1
        print('  %-8s %-5s ATR %6.1f  %d sessions' % (pair, side, atr,
                                                      len(days)))
    return n


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    wk = sys.argv[1]
    picks = []
    for a in sys.argv[2:]:
        p, _, s = a.partition(':')
        picks.append((p.upper(), s.upper()))
    print('backfilling week %s' % wk)
    print('wrote %d rows' % run(wk, picks))
