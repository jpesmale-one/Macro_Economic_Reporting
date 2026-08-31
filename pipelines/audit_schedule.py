# -*- coding: utf-8 -*-
"""R-30 - reconcile ACTUAL against the event's own scheduled time (F-71).

Jeff, 2026-08-31: "Tue 01 09:00 NZD ANZ Business Confidence - The schedule
is wrong."

An event whose date is in the FUTURE must not carry an ACTUAL. When one does,
exactly one of two things is true and they need opposite responses:

  F-1   TE populated ACTUAL before release. THE VALUE IS WRONG - it is a
        forecast wearing a print's label. Do not use it.
  F-71  The release happened and TE left the scheduled slot stale. THE DATE
        IS WRONG - the value is fine.

THE DISCRIMINATOR IS CAPTURE HISTORY. If the actual was BLANK in an earlier
capture and is POPULATED now, the release happened between them - that is
F-71. If the value has been sitting there unchanged since before any
plausible release, that is F-1.

This is why raw captures are kept rather than overwritten.

    python pipelines/audit_schedule.py
"""
import io, os, sys, json, glob, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from week_ahead import pht, CCY

CAL = os.path.join(os.path.dirname(HERE), 'data', 'raw', 'calendar')


def capture_time(path):
    """The PHT stamp encoded in the capture filename."""
    b = os.path.basename(path)
    try:
        d, t = b.split('_')[0], b.split('_')[1].replace('PHT', '')
        return dt.datetime.strptime(d + ' ' + t, '%Y-%m-%d %H%M')
    except Exception:
        return None


def load(path):
    try:
        return json.load(io.open(path, encoding='utf-8'))
    except ValueError:
        return []


def audit(verbose=True):
    caps = sorted(glob.glob(os.path.join(CAL, '*_cal_full.json')))
    if not caps:
        raise SystemExit('no capture found')
    latest, when = caps[-1], capture_time(caps[-1])
    rows = load(latest)

    # history: (iso, event) -> [(capture_time, actual), ...]
    hist = {}
    for c in caps[-8:]:
        ct = capture_time(c)
        for r in load(c):
            if 'actual' not in r:
                continue          # pre-F-65 schema
            hist.setdefault((r['iso'], r['event']), []).append(
                (ct, r.get('actual') or ''))

    f71, f1, ok = [], [], 0
    for r in rows:
        if not CCY.get(r.get('iso')):
            continue
        act = (r.get('actual') or '').strip()
        if not act:
            continue
        p = pht(r.get('date', ''), r.get('time', ''))
        if p is None or when is None:
            continue
        if p <= when:
            ok += 1
            continue
        # Future-dated AND carrying an actual. Which one is it?
        h = hist.get((r['iso'], r['event']), [])
        appeared = any(not a for _t, a in h[:-1]) and h and h[-1][1]
        row = (r['iso'], r['event'], r['date'], r.get('time'), act,
               p.strftime('%a %d %b %H:%M'))
        (f71 if appeared else f1).append(row)

    if verbose:
        print('R-30 SCHEDULE vs ACTUAL (F-71)')
        print('  capture: %s  (%s PHT)'
              % (os.path.basename(latest),
                 when.strftime('%Y-%m-%d %H:%M') if when else '?'))
        print('  %d released row(s) consistent with their own timestamp' % ok)
        print()
        if f71:
            print('  ** F-71: DATE IS STALE - the value is fine **')
            print('  These appeared between captures, so the release HAPPENED;')
            print('  TE left the scheduled slot in the future.')
            for iso, ev, d, t, a, ppt in f71:
                print('    %-3s %-42s TE says %s -> %s, actual %s'
                      % (iso, ev[:42], d, ppt, a))
            print()
        if f1:
            print('  ** F-1: VALUE IS SUSPECT - do NOT use it **')
            print('  Present since before any plausible release. A forecast')
            print('  wearing a print\'s label until proven otherwise.')
            for iso, ev, d, t, a, ppt in f1:
                print('    %-3s %-42s TE says %s -> %s, actual %s'
                      % (iso, ev[:42], d, ppt, a))
            print()
        if not f71 and not f1:
            print('  No future-dated row carries an actual.')
    return f71, f1


if __name__ == '__main__':
    audit()
