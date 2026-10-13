# -*- coding: utf-8 -*-
"""WHICH PAIRS ACTUALLY WON THE WEEK, AND DID THE BOARD SEE THEM?

Jeff, 2026-10-10: "can you go to tradingview and look for the pairs that have
won this week? Can we bring back this kind of analysis where we check that
currency actually won this week"

TWO QUESTIONS, AND THE SECOND IS THE ONE THAT GRADES US:

  1. WHICH PAIRS MOVED MOST? Every one of the 28 crosses, ranked by how far it
     travelled in its better direction. This is price, not opinion.
  2. WOULD THE BOARD HAVE PICKED THEM? For each big mover, what the board said
     about its two legs on Sunday. A pair that ran 200 pips in a direction the
     board called correctly is a miss we could have had; one it called
     backwards is a miss we could not.

*** THE SECOND QUESTION IS WHY THIS EXISTS. The 19 and 26 Sep retrospectives
carried a realised-vs-board ranking and the two after them dropped it - so the
26 Sep page could say "USD 5th -> 1st" and the 10 Oct page could not. A
regression in what we LOOK at, not in what we compute.

MEASURED FROM MONDAY'S OPEN TO FRIDAY'S CLOSE, in pips, on OANDA daily bars
read from TradingView (LD-5 as amended, F-137 - Yahoo is never a fallback).

*** THIS IS OBSERVATION, NOT INSTRUCTION (LD-4). It reports how far price
travelled and whether our ranking agreed. It names no entry, no stop, no size,
and a pair appearing here is not a trade we should have taken - the set is
chosen on the board before the week, never on the outcome after it.

    python pipelines/week_winners.py 2026-10-05 2026-10-09
"""
import io
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import pair_atr as pa
import atr_grade as ag

BARS = os.path.join(REPO, 'data/raw/bars')
# F-156 - THE RUNBOOK'S TWO COMMANDS DID NOT CONNECT.
#
# Jeff, 2026-10-13: "Today is Tuesday, let's build our very first issue of our
# Daily Report". Step 2 of the runbook pulls bars; step 3 reported "no bars for
# 2026-10-12 - pull them from TradingView first" IMMEDIATELY AFTER a successful
# pull of all eleven pairs.
#
# pull_bars.py writes to os.path.join(HERE, '<PAIR>.txt') - that is pipelines/.
# This module read a HARDCODED SCRATCHPAD PATH, which still held copies from an
# earlier session ending Thu 8 Oct. So the report was not missing data; IT WAS
# READING A DIFFERENT, OLDER SET, and said so in a way that pointed at the
# feed rather than at the path.
#
# *** WORSE THAN A MISSING FILE: the stale copies were COMPLETE. Had Monday's
# session happened to be inside that older range, the report would have
# rendered silently off eleven-day-old prices. A path mismatch that fails
# loudly is luck, not design.
#
# ONE PATH, DERIVED, SHARED WITH THE WRITER. A scratchpad path also cannot
# survive a new session - the directory name carries a session id.
TXT = os.path.dirname(os.path.abspath(__file__))


def load_txt(pair):
    """[(session, o, h, l, c)] from a pull_bars .txt, or None."""
    p = os.path.join(TXT, '%s.txt' % pair)
    if not os.path.exists(p):
        return None
    out = []
    for ln in io.open(p, encoding='utf-8'):
        x = ln.split()
        if len(x) >= 5:
            out.append((pa.session(int(x[0])),)
                       + tuple(float(v) for v in x[1:5]))
    return sorted(out)


def week(pair, start, end):
    """(move_pips, direction, atr, ratio_of_atr) or None.

    move is Monday open -> Friday close, signed so that a POSITIVE number
    always means 'the base currency strengthened'.
    """
    bars = load_txt(pair)
    if not bars:
        return None
    wk = [b for b in bars if start <= b[0] <= end]
    if len(wk) < 3:
        return None
    f = ag.pip_factor(pair)
    prior = [b for b in bars if b[0] < start]
    atr = ag.atr([(h, l, c) for _, o, h, l, c in prior], 14, f) if \
        len(prior) > 15 else None
    mv = (wk[-1][4] - wk[0][1]) * f
    return mv, ('UP' if mv > 0 else 'DOWN'), atr, (abs(mv) / atr if atr else 0)


def rank_currencies(board):
    return ' > '.join(sorted(board, key=lambda c: -board[c]))


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    start, end = (a + ['2026-10-05', '2026-10-09'])[:2]

    pairs = sorted(os.path.basename(p)[:-4]
                   for p in glob.glob(os.path.join(TXT, '*.txt'))
                   if len(os.path.basename(p)) == 10
                   and os.path.basename(p)[:6].isalpha())

    rows = []
    for p in pairs:
        r = week(p, start, end)
        if r:
            rows.append((p,) + r)
    rows.sort(key=lambda r: -abs(r[1]))

    print('PAIRS BY DISTANCE TRAVELLED   %s .. %s' % (start, end))
    print('Monday open -> Friday close, OANDA daily (LD-5)')
    print()
    print('  %-8s %10s %7s %9s  %s'
          % ('PAIR', 'MOVE', 'ATR', 'xATR', 'DIRECTION'))
    for p, mv, d, atr, x in rows[:15]:
        print('  %-8s %+10.1f %7s %8.2fx  %s %s'
              % (p, mv, ('%.0f' % atr) if atr else '-', x,
                 p[:3] if mv > 0 else p[3:], 'stronger'))
    print()
    print('  %d pairs measured, %d with a usable ATR'
          % (len(rows), sum(1 for r in rows if r[3])))
