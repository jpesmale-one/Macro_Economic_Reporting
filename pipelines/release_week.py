# -*- coding: utf-8 -*-
"""LD-83 - WHEN IN THE MONTH does each indicator usually release?

Jeff, 2026-08-30: "one thing that could help us determine the usual schedule
of the indicator in TE is by putting when the indicator is usually released in
the Month. for example PMI. it's always being released during Week 1 then lets
put it there in the report so that we have some kind of expectancy"

He is right, and it solves a problem fuzzy matching does NOT.

THE PROBLEM. On 2026-08-30, 33 of 71 whitelist rows "matched nothing" in the
capture. The reflex reading is a NAME problem - so loosen the matcher. That
reading was wrong. Those rows release LATER IN THE MONTH than TE's global
page reaches (~10 days), and the capture simply did not extend that far.
F-67 fixed the real cause by fetching every country page (~a month each), and
coverage went 38 -> 66 of 71.

WHY NOT FUZZY MATCHING. The one row that genuinely looked like a name problem
proves the danger. AUD "Inflation Rate YoY" matched nothing, but the capture
holds "TD-MI Inflation Gauge MoM" and "Consumer Inflation Expectations".
A fuzzy matcher binds our CPI row to one of those. They are DIFFERENT
INDICATORS with different readings - which is LD-59 exactly:

    "Claimant count is a Employment category while Consumer confidence is in
     Spending. they are 2 different indicator. So they have 2 different
     reading."

A loose match does not report an absence, it INVENTS a presence. So matching
stays exact, and EXPECTANCY carries the load instead: knowing an indicator is
DUE tells you an empty slot is a gap rather than a quiet week.

WHAT THIS BUILDS. Observed release dates per indicator across every capture we
have kept, reduced to a week-of-month (W1..W5). Days 1-7 are W1, 8-14 W2, and
so on. That is a HISTOGRAM OF WHAT WE HAVE SEEN, not a schedule TE publishes -
it sharpens as captures accumulate, and a row seen once says so.

    python pipelines/release_week.py            # the map
    python pipelines/release_week.py --due      # what is DUE and missing

The --due view is the one that earns its keep before an edition: an indicator
whose usual week is now, with no event in the capture, is worth a look.
"""
import io, os, sys, json, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_model as sm
from week_ahead import CCY, match

CAL = os.path.join(os.path.dirname(HERE), 'data', 'raw', 'calendar')


def week_of_month(iso_date):
    """1-7 -> W1, 8-14 -> W2, 15-21 -> W3, 22-28 -> W4, 29+ -> W5."""
    return min((int(iso_date.split('-')[2]) - 1) // 7 + 1, 5)


def observed(captures=None):
    """{(ccy, indicator): {iso_date, ...}} across every capture on disk."""
    if captures is None:
        captures = sorted(glob.glob(os.path.join(CAL, '*_cal_full.json')))
    wl = {}
    for r in sm.ROWS:
        wl.setdefault(sm.LABEL[r[1]], []).append(r[2])
    seen = collections.defaultdict(set)
    for path in captures:
        try:
            rows = json.load(io.open(path, encoding='utf-8'))
        except ValueError:
            continue
        for e in rows:
            c = CCY.get(e.get('iso'))
            if not c:
                continue
            m = match(e.get('event', ''), wl.get(c, []), e.get('iso'))
            if m:
                seen[(c, m)].add(e['date'])
    return seen


def weeks(seen):
    """{(ccy, indicator): [week, ...]} - the weeks each row has been seen in."""
    out = {}
    for k, dates in seen.items():
        out[k] = sorted(set(week_of_month(d) for d in dates))
    return out


def report(seen):
    wk = weeks(seen)
    print('RELEASE-WEEK MAP (LD-83)')
    print('  %d of %d whitelist rows have at least one observed date'
          % (len(wk), len(sm.ROWS)))
    print('  Days 1-7 = W1 ... 29+ = W5. Observed, not published by TE.')
    print()
    by_ccy = collections.defaultdict(list)
    for (c, name), ws in wk.items():
        by_ccy[c].append((name, ws, len(seen[(c, name)])))
    for c in sorted(by_ccy):
        print('  %s' % c)
        for name, ws, n in sorted(by_ccy[c]):
            tag = ','.join('W%d' % w for w in ws)
            note = '' if n > 1 else '   (seen once - low confidence)'
            print('    %-42s %s%s' % (name[:42], tag, note))
        print()
    missing = [(sm.LABEL[r[1]], r[2]) for r in sm.ROWS
               if (sm.LABEL[r[1]], r[2]) not in wk]
    if missing:
        print('  NEVER OBSERVED in any capture (%d):' % len(missing))
        for c, n in missing:
            print('    %-4s %s' % (c, n))
        print('  These need a wider capture window, not a looser matcher.')


def due(seen, today=None):
    """Rows whose usual week is NOW but which are absent from the newest capture.

    Not an alarm - a prompt to look. A release schedule shifts, and a row seen
    only once or twice has a weak claim to a 'usual' week at all.
    """
    import datetime as dt
    if today is None:
        today = dt.date.today()
    this_week = week_of_month(today.isoformat())
    caps = sorted(glob.glob(os.path.join(CAL, '*_cal_full.json')))
    if not caps:
        raise SystemExit('no capture found')
    latest = set()
    wl = {}
    for r in sm.ROWS:
        wl.setdefault(sm.LABEL[r[1]], []).append(r[2])
    for e in json.load(io.open(caps[-1], encoding='utf-8')):
        c = CCY.get(e.get('iso'))
        if not c:
            continue
        m = match(e.get('event', ''), wl.get(c, []), e.get('iso'))
        if m:
            latest.add((c, m))
    wk = weeks(seen)
    print('DUE THIS WEEK (W%d) BUT NOT IN THE NEWEST CAPTURE' % this_week)
    print('  capture: %s' % os.path.basename(caps[-1]))
    print()
    hits = 0
    for (c, name), ws in sorted(wk.items()):
        if this_week in ws and (c, name) not in latest:
            n = len(seen[(c, name)])
            print('    %-4s %-42s usually %s%s'
                  % (c, name[:42], ','.join('W%d' % w for w in ws),
                     '' if n > 1 else '  (seen once)'))
            hits += 1
    if not hits:
        print('    Nothing due-and-absent. Every W%d row is in the capture.'
              % this_week)
    print()
    print('  A row here is a PROMPT TO LOOK, not proof of a gap - schedules')
    print('  move, and a row seen once has a weak claim to a usual week.')


if __name__ == '__main__':
    s = observed()
    if '--due' in sys.argv:
        due(s)
    else:
        report(s)
