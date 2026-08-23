# -*- coding: utf-8 -*-
"""
Extract next week's WHITELIST events from a persisted TE calendar capture.

WHY THIS EXISTS - F-36, 2026-08-23. Jeff: "Theres an update for USD Building
Permits on Tuesday can you check?"

He was right. US Building Permits MoM Final is a whitelist row, it lands Tue
25 Aug, and section 4.0 did not carry it. THE CAUSE: the calendar capture has
an EMPTY TIME FIELD for that event, and my hand-written extraction sorted by
timestamp - so every blank-time row silently fell out of the sort. One event
lost, and nothing said so.

The fix is not "remember to handle blanks". It is to make the extraction
COUNT WHAT IT DROPS and report it, so a silent loss becomes a visible one.
That is the same lesson as F-15 (a missing section is invisible to a content
check) applied to a data pipeline.

DATA + FILTERING ONLY. This module does not fetch; feed it a capture.
"""
import json, io, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CCY = {'US': 'USD', 'EA': 'EUR', 'DE': 'EUR', 'FR': 'EUR', 'IT': 'EUR',
       'ES': 'EUR', 'GB': 'GBP', 'JP': 'JPY', 'AU': 'AUD', 'NZ': 'NZD',
       'CA': 'CAD', 'CH': 'CHF'}


def pht(date, t):
    """TE calendar times are UTC. PHT = UTC+8 (F-2: verify every run)."""
    t = (t or '').strip()
    if not t:
        return None
    try:
        d = datetime.datetime.strptime(date + ' ' + t, '%Y-%m-%d %I:%M %p')
    except ValueError:
        return None
    return d + datetime.timedelta(hours=8)


def whitelist_events(capture_path, start, end):
    """Whitelist events in [start, end] (ISO dates), oldest first.

    Returns (events, no_time) where each event is
    (pht_datetime_or_None, ccy, whitelist_name, raw_event, iso_date).

    NO EVENT IS EVER DROPPED. Rows with no time land in `no_time` and the
    caller must publish them - F-36 happened because a sort silently
    discarded them.
    """
    import score_model as sm
    wl = {}
    for r in sm.ROWS:
        wl.setdefault(sm.LABEL[r[1]], []).append(r[2])

    data = json.load(io.open(capture_path, encoding='utf-8'))
    timed, no_time, seen = [], [], set()
    for e in data:
        if not (start <= e.get('date', '') <= end):
            continue
        ccy = CCY.get(e.get('iso'))
        if not ccy:
            continue
        ev = (e.get('event') or '').lower()
        hit = None
        for name in wl.get(ccy, []):
            n = name.lower()
            if ev == n or (len(ev) > 6 and (ev in n or n in ev)):
                hit = name
                break
        if not hit:
            continue
        key = (ccy, hit)
        if key in seen:
            continue
        seen.add(key)
        p = pht(e['date'], e.get('time'))
        rec = (p, ccy, hit, e.get('event'), e['date'])
        (timed if p else no_time).append(rec)

    timed.sort(key=lambda r: r[0])
    no_time.sort(key=lambda r: r[4])
    return timed, no_time


if __name__ == '__main__':
    cap = sys.argv[1] if len(sys.argv) > 1 else None
    start = sys.argv[2] if len(sys.argv) > 2 else '2026-08-24'
    end = sys.argv[3] if len(sys.argv) > 3 else '2026-08-28'
    if not cap:
        import glob
        caps = sorted(glob.glob(os.path.join(
            os.path.dirname(HERE), 'data', 'raw', 'calendar', '*.json')))
        cap = caps[-1] if caps else None
    if not cap:
        raise SystemExit('no calendar capture found')
    timed, no_time = whitelist_events(cap, start, end)
    print('capture: %s' % os.path.basename(cap))
    print('window : %s .. %s (PHT)' % (start, end))
    print()
    print('%-16s %-5s %s' % ('WHEN (PHT)', 'CCY', 'WHITELIST INDICATOR'))
    for p, ccy, name, raw, d in timed:
        print('%-16s %-5s %s' % (p.strftime('%a %d %H:%M'), ccy, name))
    if no_time:
        print()
        print('*** %d EVENT(S) WITH NO TIME IN THE CAPTURE - PUBLISH THESE TOO ***'
              % len(no_time))
        for p, ccy, name, raw, d in no_time:
            print('%-16s %-5s %s   (calendar: "%s")' % (d, ccy, name, raw))
    print()
    print('TOTAL WHITELIST EVENTS: %d  (%d timed, %d untimed)'
          % (len(timed) + len(no_time), len(timed), len(no_time)))
