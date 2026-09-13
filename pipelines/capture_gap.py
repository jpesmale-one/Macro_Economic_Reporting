# -*- coding: utf-8 -*-
"""R-42 - DID A RELEASE FALL THROUGH A GAP BETWEEN CAPTURES?

Jeff, 2026-09-13: "we cannot afford to have dirty data as we're doing
forecasting. We need to be accurate on the pulls"

WHAT WENT WRONG. GBP Industrial Production YoY and Manufacturing Production
YoY printed Fri 11 Sep. The board still carried Jun/26 values on 13 Sep, and
R-40 reported 0 stale - because R-40 can only compare against a print it can
SEE, and no capture we own contains those actuals.

    THE TE CALENDAR IS A ROLLING WINDOW, NOT AN ARCHIVE.

Every capture starts ~3 days BACK and runs ~30 days FORWARD. Watch the left
edge march across our own captures:

    04 Sep capture   window starts 2026-09-01   127 rows carry an actual
    08 Sep capture   window starts 2026-09-06    67
    10 Sep capture   window starts 2026-09-07    68
    13 Sep capture   window starts 2026-09-10    10

The GBP rows sat in the 10 Sep capture with act='-' (not yet released), then
printed on the 11th, and by the 13 Sep capture TE had ALREADY ROTATED THEM
OFF. They existed with a value for roughly 48 hours and nobody looked.

    A RELEASE IS LOST PERMANENTLY IF NO CAPTURE RUNS WHILE IT IS STILL
    INSIDE THE WINDOW. Capture cadence was 4 Sep -> 8 Sep (4 days) and
    10 Sep -> 13 Sep (3 days). The lookback is ~3 days. Anything landing
    in a gap wider than the lookback is gone.

WHY A GUARD RATHER THAN "CAPTURE MORE OFTEN". Capturing more often is the
remedy, but a remedy nobody is reminded of decays. This module measures the
ACTUAL lookback of each capture from its own contents rather than assuming 3
days, finds every inter-capture gap wider than that, and names the whitelist
rows scheduled inside it - the rows whose actual we can no longer recover from
the calendar.

RECOVERY IS STILL POSSIBLE - from the INDICATOR page, not the calendar. TE's
per-indicator pages (e.g. /united-kingdom/industrial-production) carry a small
history table with the release date, actual, previous and consensus. That is
how the 11 Sep GBP values were recovered. This module prints that URL for each
lost row so the recovery path is in hand, not remembered.

    python pipelines/capture_gap.py            # audit gaps in capture history
    python pipelines/capture_gap.py --raise    # exit 1 if a row was lost
"""
import io
import os
import re
import sys
import json
import glob
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phtime as pt
import week_ahead as wa
import score_model as sm

CCY = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}

# The TE indicator page that carries a release history for each row, so a
# value lost from the calendar can still be recovered. Slug per country.
SLUG = {'USD': 'united-states', 'EUR': 'euro-area', 'GBP': 'united-kingdom',
        'JPY': 'japan', 'AUD': 'australia', 'NZD': 'new-zealand',
        'CAD': 'canada', 'CHF': 'switzerland'}


def recovered():
    """{(ccy, row, date)} already recovered from a TE indicator page.

    A row lost to a gap can NEVER come back from the calendar - TE has moved
    past it - so R-42 would report it forever, even after the value is safely
    in the fact table. A guard that keeps crying about a closed issue trains
    you to skim it, which is how the next real one gets missed.

    data/raw/calendar/RECOVERED.md is the ledger: recording WHERE a value came
    from is provenance, not bookkeeping (LD-3 - the calendar is a SCHEDULE
    authority; the indicator page is the VALUE authority here).
    """
    out = {}
    f = os.path.join(REPO, 'data/raw/calendar/RECOVERED.md')
    if not os.path.exists(f):
        return out
    for line in io.open(f, encoding='utf-8'):
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 5 and re.match(r'\d{4}-\d{2}-\d{2}$', parts[2]):
            out[(parts[0], parts[1], parts[2])] = (parts[3], parts[4])
    return out


def _cap_date(path):
    m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{4})PHT', os.path.basename(path))
    if not m:
        return None
    return dt.datetime.strptime(m.group(1), '%Y-%m-%d').date()


def captures():
    """[(taken_date, window_start, window_end, path, per_ccy)] oldest first.

    *** THE WINDOW IS PER COUNTRY, AND IT MOVES. My first version took one
    window_start for the whole capture (its earliest row) and concluded the
    13 Sep capture could see back to 10 Sep - so the 11 Sep GBP release
    "should" have been covered. It was not. Measured per country:

        13 Sep capture    GB starts 2026-09-15   <- FOUR DAYS FORWARD
                          US starts 2026-09-14
                          JP starts 2026-09-10
                          CH starts 2026-09-11

    The aggregate 2026-09-10 came from JP/EA/AU/NZ. GB's own page had already
    rotated past the 11th. A whole-capture window is an average that hides the
    country that lost data, so `per_ccy` records each country's own reach and
    the reachability test uses THAT.
    """
    out = []
    for f in sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json'))):
        taken = _cap_date(f)
        if not taken:
            continue
        try:
            with io.open(f, encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception:
            continue
        ds, per = [], {}
        for r in (data if isinstance(data, list) else data.get('events', [])):
            if not isinstance(r, dict) or not r.get('date'):
                continue
            d = str(r['date'])[:10]
            if not re.match(r'\d{4}-\d{2}-\d{2}$', d):
                continue
            ds.append(d)
            iso = r.get('iso')
            if iso in CCY:
                c = CCY[iso]
                lo, hi = per.get(c, (d, d))
                per[c] = (min(lo, d), max(hi, d))
        if not ds:
            continue
        out.append((taken, min(ds), max(ds), f, per))
    return out


def gaps():
    """Windows where no capture could see a release. [(from, to, days)]."""
    caps = captures()
    out = []
    for i in range(1, len(caps)):
        prev_taken = caps[i - 1][0]
        taken, w_start = caps[i][0], caps[i][1]
        start = dt.datetime.strptime(w_start, '%Y-%m-%d').date()
        # This capture can see back to `start`. The previous capture saw
        # everything up to the day it ran. Anything strictly between is blind.
        if start > prev_taken + dt.timedelta(days=1):
            out.append((prev_taken + dt.timedelta(days=1),
                        start - dt.timedelta(days=1),
                        (start - prev_taken).days - 1, taken))
    return out


def lost():
    """Whitelist rows scheduled inside a blind window, with no actual held."""
    names = {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        names.setdefault(sm.LABEL[iso], []).append(name)

    # Every scheduled occurrence we ever saw, matched to a whitelist row.
    sched, have_act = {}, set()
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
            ccy = CCY[iso]
            hit = wa.match(str(r.get('event', '')).lower(),
                           names.get(ccy, []), iso)
            if not hit:
                continue
            when = pt.te_pht(r.get('date'), r.get('time'))
            ds = when.strftime('%Y-%m-%d') if when else str(r.get('date'))[:10]
            sched.setdefault((ccy, hit, ds), str(r.get('event')))
            if (r.get('actual') or '').strip():
                have_act.add((ccy, hit, ds))

    # A row is LOST when it was scheduled on a day that no capture could still
    # see AFTER it printed, and we never captured an actual for it.
    #
    # *** THE GBP CASE. My first version only looked inside the blind windows
    # between captures, and MISSED the very rows that prompted this module.
    # GBP Industrial Production was scheduled 11 Sep and WAS VISIBLE in the
    # 10 Sep capture - with act='-', because it had not printed yet. Being
    # visible before the release is worthless. What matters is whether any
    # capture ran while the row was BOTH released AND still in the window.
    #
    #     visible-before-release is not coverage. Only a capture taken
    #     ON OR AFTER the release, whose window still reaches back to it,
    #     can ever hold the actual.
    caps = captures()
    out = []
    for (ccy, row, ds), ev in sorted(sched.items()):
        if (ccy, row, ds) in have_act:
            continue
        try:
            d = dt.datetime.strptime(ds, '%Y-%m-%d').date()
        except ValueError:
            continue
        today = dt.datetime.now(pt.PHT).date()
        if d > today:
            continue                     # not released yet - not lost
        reachable = False
        for taken, w0, w1, f, per in caps:
            if ccy not in per:
                continue
            start = dt.datetime.strptime(per[ccy][0], '%Y-%m-%d').date()
            if taken >= d and start <= d:
                reachable = True         # a capture saw it, released, in window
                break
        if not reachable:
            out.append((ccy, row, ds, ev))
    return out


def outstanding():
    """Lost rows NOT yet recovered from an indicator page."""
    rec = recovered()
    return [x for x in lost() if (x[0], x[1], x[2]) not in rec]


if __name__ == '__main__':
    caps = captures()
    gs = gaps()
    ls = lost()

    print('R-42 CAPTURE GAP AUDIT   %d captures' % len(caps))
    print()
    print('  %-12s %-12s %-12s %s' % ('TAKEN', 'SEES FROM', 'SEES TO', 'LOOKBACK'))
    for taken, w0, w1, f, per in caps[-8:]:
        lb = (taken - dt.datetime.strptime(w0, '%Y-%m-%d').date()).days
        print('  %-12s %-12s %-12s %d days' % (taken, w0, w1, lb))
    print()

    if gs:
        print('BLIND WINDOWS - no capture could see a release landing here')
        for a, b, n, taken in gs:
            print('  %s .. %s   (%d day%s)' % (a, b, n, '' if n == 1 else 's'))
        print()

    rec = recovered()
    out = [x for x in ls if (x[0], x[1], x[2]) not in rec]
    done = [x for x in ls if (x[0], x[1], x[2]) in rec]

    if done:
        print('RECOVERED from the indicator page - gap closed by hand')
        for ccy, row, ds, ev in done:
            act, src = rec[(ccy, row, ds)]
            print('  %-4s %-32s %s  actual %s' % (ccy, row[:32], ds, act))
        print()

    if out:
        print('=' * 78)
        print('*** ROWS LOST TO A GAP - recover from the TE INDICATOR page')
        print('=' * 78)
        for ccy, row, ds, ev in out:
            slug = re.sub(r'[^a-z0-9]+', '-', row.lower()).strip('-')
            print('  %-4s %-32s scheduled %s' % (ccy, row[:32], ds))
            print('        https://tradingeconomics.com/%s/%s'
                  % (SLUG.get(ccy, '?'), slug))
            print('        then record it in data/raw/calendar/RECOVERED.md')
        print()
        print('*** %d ROW(S) CANNOT BE RECOVERED FROM THE CALENDAR.' % len(out))
        if '--raise' in sys.argv:
            sys.exit(1)
    elif ls:
        print('  every row lost to a gap has been recovered and recorded')
    else:
        print('  no whitelist row fell into a blind window')

    # The forward-looking half: when must the next capture run?
    if caps:
        last = caps[-1][0]
        lb = (last - dt.datetime.strptime(caps[-1][1], '%Y-%m-%d').date()).days
        due = last + dt.timedelta(days=max(1, lb))
        today = dt.datetime.now(pt.PHT).date()
        print()
        print('  last capture %s, lookback %d days -> NEXT CAPTURE DUE %s'
              % (last, lb, due))
        if today >= due:
            print('  *** OVERDUE as of %s - capture before trusting the board.'
                  % today)
