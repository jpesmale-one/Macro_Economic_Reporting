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

    UNIONS EVERY CAPTURE ON DISK, newest first (F-73).

    Jeff, 2026-08-31: "USD CB Consumer Confidence - This is scheduled Sept 29
    10pm PHT ... I think you're missing Sept 29 - 30"

    He was right. TE serves roughly 26 days forward from the fetch date, so a
    single capture taken on 31 Aug simply ENDS at 25 Sep - and reading only
    the newest capture threw away everything the older ones knew. Worse, the
    horizon is a MOVING WALL: 29 Sep enters the window around 4 Sep, so the
    rows Jeff named will appear on their own in a few days and their absence
    today looks identical to a matching failure.

    The union does two things: it keeps what earlier captures saw, and it
    makes the wall visible - `horizon()` reports the furthest date ANY
    capture reaches, so "not scheduled" can be qualified honestly rather
    than implying the event does not exist.

    Only events STRICTLY AFTER today count. A print that already landed today
    is not due - it is done, and 2.0 has it.
    """
    caps = sorted(glob.glob(os.path.join(CAL, '*_cal_full.json')))
    if capture is not None:
        caps = [capture]
    if not caps:
        raise SystemExit('no capture found')
    if today is None:
        today = (dt.datetime.now(dt.timezone.utc)
                 .astimezone(dt.timezone(dt.timedelta(hours=8))).date())

    wl = {}
    for r in sm.ROWS:
        wl.setdefault(sm.LABEL[r[1]], []).append(r[2])

    best = {}
    for path in caps:
        try:
            rows = json.load(io.open(path, encoding='utf-8'))
        except ValueError:
            continue
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


def horizon():
    """The furthest date ANY capture on disk reaches (F-73).

    TE's calendar is a MOVING WALL about 26 days ahead of the fetch. Beyond
    it, "not scheduled" means "past our horizon", NOT "does not exist" - and
    the report must say which.
    """
    caps = sorted(glob.glob(os.path.join(CAL, '*_cal_full.json')))
    far = ''
    for path in caps:
        try:
            rows = json.load(io.open(path, encoding='utf-8'))
        except ValueError:
            continue
        for r in rows:
            if r.get('date', '') > far:
                far = r['date']
    return far


def label(entry, far=None):
    """'W1 \u00b7 Thu 3 Sep' - the cell that goes in a \u00a72 table.

    F-73: when there is no scheduled print, say WHY. TE's calendar is a
    MOVING WALL about 26 days past the fetch date, so an absence usually
    means "past our horizon", NOT "does not exist".

    Jeff, 2026-08-31, naming four rows we showed as unscheduled: "USD CB
    Consumer Confidence - This is scheduled Sept 29 10pm PHT ... I think
    you're missing Sept 29 - 30". He was right, and 'not scheduled' read as
    a claim about the calendar when it was a fact about our window.

    LD-39 still applies - this is never a bare em dash.
    """
    if entry is None:
        if far:
            try:
                d = dt.datetime.strptime(far, '%Y-%m-%d')
                return 'beyond %d %s' % (d.day, d.strftime('%b'))
            except ValueError:
                pass
        return 'beyond horizon'
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
    far = horizon()
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
            print('    %-4s %-40s %s' % (ccy, name[:40], label(e, far)))
        print()
    print('  %d of %d rows have a scheduled next print in the capture'
          % (have, len(sm.ROWS)))
    print('  HORIZON: %s - the furthest date any capture reaches.' % far)
    print('  A row marked "beyond" releases past that wall, which moves')
    print('  forward every day (F-73). It is NOT a claim that the event')
    print('  does not exist - Jeff named four rows on 29-30 Sep that had')
    print('  simply not entered the window yet.')


if __name__ == '__main__':
    main()
