# -*- coding: utf-8 -*-
"""LD-145 - ATR AND TARGET FOR EVERY SELECTED PAIR, ON THE EDITION ITSELF.

Jeff, 2026-09-27: "on the next report for the selected pairs, lets put the ATR
and Target as well. I believe we already putting the Gap there"

He is right that Gap is already there, and right that the other two are not.
The three answer different questions and only together do they let a reader
check the model against the market:

    GAP     the MODEL's conviction - the two currencies' board scores
            subtracted. Never touches price. A score on a -9..+9 board.
    ATR     what the pair NORMALLY moves, in pips. Purely price.
    TARGET  0.75 x ATR - the distance a day has to cover to count (LD-128).

WHY THE GAP ALONE IS NOT ENOUGH. On 21-25 Sep:

    EURAUD  gap +5.10   2 of 5 days at target
    GBPAUD  gap +4.50   1 of 5
    AUDCHF  gap +1.20   2 of 5

The THINNEST conviction in the set delivered as often as the widest. And
without ATR the day-readings are not comparable: 1.06x on GBPAUD is 89 pips,
1.40x on AUDCHF is 45. A reader seeing only the multiples would rank those
backwards.

*** THE BARS COME FROM TRADINGVIEW, NEVER YAHOO (LD-5 as amended 2026-09-27).
F-137: two retrospectives were graded on Yahoo daily bars, whose sessions are
offset a day from OANDA's - a bar opening 21:00 UTC belongs to the NEXT
session. Jeff: "Make sure we get the technical analysis and prices from
TradingView. We need to be looking at the same source."

This module does NOT fetch. It cannot - the MCP chart tools are not callable
from a script. The Sunday flow is:

    1. compute the set          (board only, no price)
    2. for each pair: set OANDA:<PAIR>, timeframe D, read bars,
       and write them to data/raw/bars/<PAIR>.json
    3. python pipelines/pair_atr.py    <- this, reads those files

    python pipelines/pair_atr.py                 # every pair with bars on disk
    python pipelines/pair_atr.py EURAUD GBPAUD   # only these
"""
import io
import os
import sys
import json
import glob
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import atr_grade as ag

BARS = os.path.join(REPO, 'data/raw/bars')


def session(epoch):
    """The trading session an OANDA daily bar belongs to.

    An OANDA daily bar OPENS at 21:00 UTC, so its epoch names the evening
    BEFORE the session it covers. Adding 3h lands inside the session's own
    date. This is F-106, which cost a reversed sign on 2026-09-13 and two
    mis-dated retrospectives after that.
    """
    return (dt.datetime.fromtimestamp(epoch, dt.timezone.utc)
            + dt.timedelta(hours=3)).strftime('%Y-%m-%d')


def load(pair):
    """[(session, o, h, l, c)] oldest first, or None if not on disk."""
    p = os.path.join(BARS, '%s.json' % pair)
    if not os.path.exists(p):
        return None
    raw = json.load(io.open(p, encoding='utf-8'))
    rows = raw.get('bars', raw) if isinstance(raw, dict) else raw
    out = []
    for b in rows:
        if isinstance(b, dict):
            t, o, h, l, c = (b['time'], b['open'], b['high'],
                             b['low'], b['close'])
        else:
            t, o, h, l, c = b[:5]
        out.append((session(t), o, h, l, c))
    return sorted(out)


def atr_for(pair, before=None, n=14):
    """(atr_pips, target_pips, bars_used, last_session) or None.

    `before` is the first day of the week being TRADED; bars on or after it
    are excluded, because a yardstick built from the week it grades is
    hindsight (F-83, and the CHF vintage error).
    """
    bars = load(pair)
    if not bars:
        return None
    if before:
        bars = [b for b in bars if b[0] < before]
    if len(bars) < n + 1:
        return None
    f = ag.pip_factor(pair)
    a = ag.atr([(h, l, c) for _, o, h, l, c in bars], n, f)
    if not a:
        return None
    return a, a * ag.TARGET, len(bars), bars[-1][0]


def table(pairs, before=None):
    """[(pair, atr, target, n, last)] - missing pairs reported as None."""
    return [(p,) + (atr_for(p, before) or (None, None, None, None))
            for p in pairs]


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args:
        pairs = [a.upper() for a in args]
    else:
        pairs = sorted(os.path.basename(f)[:-5]
                       for f in glob.glob(os.path.join(BARS, '*.json')))
    if not pairs:
        print('no bars on disk. Pull them from TradingView first:')
        print('  chart_set_symbol OANDA:<PAIR> -> chart_set_timeframe D')
        print('  -> data_get_ohlcv -> save to data/raw/bars/<PAIR>.json')
        sys.exit(2)

    # default: exclude the week starting next Monday, i.e. grade on what is
    # already closed. A Sunday build wants bars up to and including Friday.
    today = dt.date.today()
    nxt = today + dt.timedelta(days=(7 - today.weekday()) % 7 or 7)
    if today.weekday() == 6:
        nxt = today + dt.timedelta(days=1)

    print('LD-145 ATR AND TARGET   bars strictly before %s' % nxt)
    print()
    print('%-9s %9s %9s %7s  %s'
          % ('PAIR', 'ATR(14)', 'TARGET', 'BARS', 'LAST SESSION'))
    miss = []
    for pair, a, t, n, last in table(pairs, nxt.isoformat()):
        if a is None:
            miss.append(pair)
            print('%-9s %9s %9s %7s  %s' % (pair, '-', '-', '-', 'NO BARS'))
            continue
        print('%-9s %9.1f %9.1f %7d  %s' % (pair, a, t, n, last))
    if miss:
        print()
        print('*** %d pair(s) have no usable bars: %s'
              % (len(miss), ', '.join(miss)))
        print('    Pull them from TradingView - Yahoo is not a source (F-137).')
        sys.exit(1)
