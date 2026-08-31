# -*- coding: utf-8 -*-
"""LD-87 - WHEN IS EACH \u00a72 INDICATOR NEXT DUE?

Jeff, 2026-08-31: "For each indicators in 2 we put which week these news will
come out. in TE the whole schedule for September is already out. so we can
check on which week in September these indicators will come out"

WHY THIS AND NOT LD-83. release_week.py builds a HISTOGRAM of weeks a row has
been SEEN in - inferred from history, sharpening as captures accumulate. This
reads the ACTUAL SCHEDULED DATE out of the capture. TE publishes September in
full, so there is no need to infer what can be looked up.

The two answer different questions and both are worth having:
    LD-83  "this series usually lands in W1"      -> expectancy, and the
                                                     --due check for gaps
    LD-87  "this row's next print is Thu 3 Sep"   -> a fact from the calendar

WHAT IT GIVES \u00a72. Every indicator row can now say when it is next refreshed.
A GOOD score with a print due Thursday is a different thing from a GOOD score
with nothing until the 24th - the first is about to be tested, the second is
carried. That distinction is invisible today, and it is the same blind spot
that let NZD's 2-month-old quarterly data sit at +4.29 unchallenged.

    python pipelines/next_due.py
"""
import io, os, sys, json, glob, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_model as sm
from week_ahead import CCY, match, pht

CAL = os.path.join(os.path.dirname(HERE), 'data', 'raw', 'calendar')


def week_of_month(iso_date):
    """1-7 -> W1, 8-14 -> W2, 15-21 -> W3, 22-28 -> W4, 29+ -> W5."""
    return min((int(iso_date.split('-')[2]) - 1) // 7 + 1, 5)


def next_due(capture=None, today=None):
    """{(ccy, indicator): (iso_date, week, pht_datetime)} - the NEXT print.

    Only events STRICTLY AFTER today are considered. A row whose print has
    already landed today is not 'due' - it is done, and 2.0 already has it.
    """
    caps = sorted(glob.glob(os.path.join(CAL, '*_cal_full.json')))
    if capture is None:
        if not caps:
            raise SystemExit('no capture found')
        capture = caps[-1]
    rows = json.load(io.open(capture, encoding='utf-8'))
    if today is None:
        today = (dt.datetime.now(dt.timezone.utc)
                 .astimezone(dt.timezone(dt.timedelta(hours=8))).date())

    wl = {}
    for r in sm.ROWS:
        wl.setdefault(sm.LABEL[r[1]], []).append(r[2])

    best = {}
    for e in rows:
        c = CCY.get(e.get('iso'))
        if not c:
            continue
        m = match(e.get('event', ''), wl.get(c, []), e.get('iso'))
        if not m:
            continue
        p = pht(e.get('date', ''), e.get('time', ''))
        d = p.strftime('%Y-%m-%d') if p else e.get('date', '')
        if d <= today.isoformat():
            continue
        k = (c, m)
        if k not in best or d < best[k][0]:
            best[k] = (d, week_of_month(d), p)
    return best


def label(entry):
    """'W1 \u00b7 Thu 3 Sep' - the cell that goes in a \u00a72 table."""
    if entry is None:
        # LD-39 rejects a bare em dash as an unverifiable blank, and it is
        # right to: "not scheduled in the captured window" and "we failed to
        # look" must not render identically. This is a CLAIM about the
        # calendar, and it can be checked.
        return 'not scheduled'
    d, w, p = entry
    try:
        day = dt.datetime.strptime(d, '%Y-%m-%d')
    except ValueError:
        return 'W%d \u00b7 %s' % (w, d)
    # %-d is not portable to Windows, where it raises rather than stripping
    # the leading zero - build the day number by hand.
    return 'W%d \u00b7 %s %d %s' % (w, day.strftime('%a'), day.day,
                                day.strftime('%b'))


def main():
    due = next_due()
    print('NEXT DUE PER WHITELIST ROW (LD-87)')
    print('  read from TE\'s published schedule, not inferred from history')
    print()
    have = 0
    for cat in ('Production', 'Spending', 'Trade', 'Employment', 'Inflation'):
        print('  %s' % cat.upper())
        for c2, iso, name, a, p, r, thr, v in sm.ROWS:
            if c2 != cat:
                continue
            ccy = sm.LABEL[iso]
            e = due.get((ccy, name))
            if e:
                have += 1
            print('    %-4s %-40s %s' % (ccy, name[:40], label(e)))
        print()
    print('  %d of %d rows have a scheduled next print in the capture'
          % (have, len(sm.ROWS)))
    print('  A row showing an em dash releases beyond the capture window,')
    print('  or on a schedule TE has not published yet.')


if __name__ == '__main__':
    main()
