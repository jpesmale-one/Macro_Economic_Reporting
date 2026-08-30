# -*- coding: utf-8 -*-
"""R-25 - whitelist coverage audit: can every row EVER be matched?

Jeff, 2026-08-30, after the same defect surfaced twice in four days:
"if TE is changing the names by abbreviations can we not just track both?"

F-38 (11 rows) and F-64 (7 PMI rows) were the same failure - a whitelist name
the calendar does not use, so the row never matched and never appeared in 4.0.
Both were found by Jeff reading, not by a guard.

A synonym map fixes the abbreviations we have already hit. THIS checks the
thing that actually matters: over the whole captured calendar, does every one
of the 71 rows match at least one event?

A row that matches NOTHING across a month is not quiet. It is UNMATCHABLE.

    python pipelines/coverage_audit.py
"""
import io, os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_model as sm
from week_ahead import CCY, match


def audit(capture=None):
    caps = sorted(glob.glob(os.path.join(
        os.path.dirname(HERE), 'data', 'raw', 'calendar', '*_cal_full.json')))
    if capture is None:
        if not caps:
            raise SystemExit('no full capture found - run capture_calendar.py')
        capture = caps[-1]
    rows = json.load(io.open(capture, encoding='utf-8'))

    wl = {}
    for r in sm.ROWS:
        wl.setdefault(sm.LABEL[r[1]], []).append(r[2])

    matched = set()
    for e in rows:
        c = CCY.get(e.get('iso'))
        if not c:
            continue
        m = match(e.get('event', ''), wl.get(c, []), e.get('iso'))
        if m:
            matched.add((c, m))

    missing = []
    for cat, iso, name, act, prev, ref, thr, verd in sm.ROWS:
        c = sm.LABEL[iso]
        if (c, name) not in matched:
            missing.append((c, name, ref))

    span = (min(r['date'] for r in rows), max(r['date'] for r in rows))
    print('WHITELIST COVERAGE AUDIT (R-25)')
    print('  capture: %s' % os.path.basename(capture))
    print('  window : %s .. %s' % span)
    print()
    print('  %d of %d rows matched at least one event' %
          (len(sm.ROWS) - len(missing), len(sm.ROWS)))
    print()
    if missing:
        print('  ROWS THAT MATCHED NOTHING:')
        for c, name, ref in missing:
            print('    %-4s %-38s (row holds %s)' % (c, name[:38], ref))
        print()
        print('  A row may be quiet in a SHORT window - check the span above')
        print('  before concluding. Over a MONTH, no match means the name is')
        print('  UNMATCHABLE: add the abbreviation to week_ahead._SYN, or the')
        print('  vendor word to _DROP, the way F-64 and F-64b did.')
    else:
        print('  Every whitelist row is matchable.')
    return missing


if __name__ == '__main__':
    audit(sys.argv[1] if len(sys.argv) > 1 else None)
