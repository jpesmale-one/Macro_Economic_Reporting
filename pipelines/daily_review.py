# -*- coding: utf-8 -*-
"""DAY-BY-DAY performance for the live set, with each day's releases (LD-127).

Jeff, 2026-09-10:

    "it's better to look at it on a daily perspective so if price suddenly
     move against our bias we can zoom in to that day to see what is the
     catalyst for the move"

WHY THE WEEKLY NUMBER IS NOT ENOUGH. A pair that ends +149 might have gone
+200 on Monday and given half back, or drifted +37 a day. Those are different
weeks and only one is a bias that worked; MFE/MAE cannot tell them apart, and
neither can point at a DAY to investigate.

WHAT THIS ADDS: per-day move, best and worst excursion within that day, the
running total, and EVERY RELEASE THAT LANDED ON THAT DAY for either leg. When
price moves against the bias, the row that moved it is on the same line.

TWO RULES IT INHERITS, both learned the hard way:

  LD-115  every time is PHT. A release is matched to the day that CONTAINS
          it, never the day its TE date string names - 23% of major-currency
          rows land on a different calendar day once converted (F-108).

  F-106   a daily bar is not a calendar day. OANDA sessions open 21:00 UTC,
          so the bar holding Monday's trade opens Sunday 21:00 UTC. Bars are
          keyed by their PHT date, computed, never by their label.

USAGE
    python pipelines/daily_review.py                 # the live set
    python pipelines/daily_review.py 2026-09-07      # a specific week start
"""
import io, os, sys, json, glob
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phtime as pt

CCY = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}

# JPY crosses quote to 3 decimals; everything else to 5.
def pip_factor(pair):
    return 100 if pair.endswith('JPY') else 10000


def releases_by_day():
    """{(ccy, date): {event: (hh:mm PHT, actual, forecast)}} - actuals only.

    Every capture is read, because TE rolls a row forward once the next
    occurrence is scheduled and an actual released early in the week is gone
    from a later capture (F-95).
    """
    out = {}
    for f in sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json'))):
        try:
            with io.open(f, encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception:
            continue
        for r in (data if isinstance(data, list) else data.get('events', [])):
            if not isinstance(r, dict):
                continue
            iso = r.get('iso')
            if iso not in CCY:
                continue
            when = pt.te_pht(r.get('date'), r.get('time'))
            act = (r.get('actual') or '').strip()
            if when is None or not act:
                continue
            key = (CCY[iso], when.date())
            fc = (r.get('forecast') or r.get('consensus') or '').strip() or '-'
            out.setdefault(key, {})[str(r.get('event'))] = (
                when.strftime('%H:%M'), act, fc)
    return out


def review(pair, bias, gap, bars, events, entry=None):
    """Print one pair's week, day by day, with catalysts.

    bars: [(epoch, o, h, l, c)] in session order, oldest first.
    """
    f = pip_factor(pair)
    entry = bars[0][1] if entry is None else entry
    legs = (pair[:3], pair[3:])
    print('=' * 76)
    print('%s %s   gap %+.2f   entry %s' % (pair, bias, gap, entry))
    print('=' * 76)
    print('%-11s %9s %9s %9s %9s   %s'
          % ('DAY (PHT)', 'MOVE', 'BEST', 'WORST', 'RUNNING', 'catalysts'))
    rows = []
    for t, o, h, l, c in bars:
        day = pt.bar_pht(t).date()
        if bias == 'LONG':
            mv, best, worst = (c - o) * f, (h - o) * f, (l - o) * f
            run = (c - entry) * f
        else:
            mv, best, worst = (o - c) * f, (o - l) * f, (o - h) * f
            run = (entry - c) * f
        ev = []
        for leg in legs:
            for name, (tm, act, fc) in sorted(events.get((leg, day), {}).items()):
                ev.append('%s %s %s = %s (fcst %s)'
                          % (tm, leg, name[:30], act, fc))
        print('%-11s %+9.1f %+9.1f %+9.1f %+9.1f   %s'
              % (day.strftime('%a %d %b'), mv, best, worst, run,
                 ev[0] if ev else '-'))
        for extra in ev[1:]:
            print('%-11s %9s %9s %9s %9s   %s' % ('', '', '', '', '', extra))
        rows.append((day, mv, best, worst, run))

    # WHERE the move happened - the question a weekly figure cannot answer
    tot = rows[-1][4]
    if rows and abs(tot) > 1e-9:
        big = max(rows, key=lambda r: abs(r[1]))
        share = big[1] / tot * 100
        print()
        print('   biggest day: %s %+.1f pips (%.0f%% of the running total)'
              % (big[0].strftime('%a %d %b'), big[1], share))
        against = [r for r in rows if r[1] < 0]
        if against:
            w = min(against, key=lambda r: r[1])
            print('   worst day against the bias: %s %+.1f  <- zoom here'
                  % (w[0].strftime('%a %d %b'), w[1]))
    print()
    return rows


if __name__ == '__main__':
    print(__doc__.split('USAGE')[0].rstrip())
    print()
    print('No bar data is stored in this repo - pass it from a TradingView')
    print('read. This module owns the SHAPE of the review, not the prices.')
