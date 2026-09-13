# -*- coding: utf-8 -*-
"""R-40 - IS ANY WHITELIST ROW STALE AGAINST A RELEASE WE ALREADY HAVE?

Jeff, 2026-09-13: "AUD Westpac Consumer Conf Change -- We already have latest
data of this. in the previous report it is also in the calibrator so we should
be reflecting the new values now"

He was right: Westpac printed -5.2% on 8 Sep and the fact table still held
6.0% from Aug/26. AUD's Spending category was +1.50 when it should have been
+0.50 - the difference between AUD tying NZD and AUD being alone at the bottom.

*** F-120 - WHY THE HAND-ROLLED CHECK MISSED IT. *** The 13 Sep refresh was a
one-off script that matched names with a plain substring test. 'westpac
consumer conf change' is NOT a substring of 'westpac consumer confidence
change sep' - CONF vs CONFIDENCE. week_ahead.match() normalises exactly that
abbreviation (F-64) and would have found it.

    A VINTAGE CHECK THAT DISAGREES WITH THE SCORER ABOUT WHAT A ROW *IS*
    WILL ALWAYS MISS ROWS.

So this module calls week_ahead.match() - the same matcher the calibrator and
the edition use. It is not a second opinion about row identity; there is only
one opinion, and this asks it.

WHY IT IS A GUARD RATHER THAN A SCRIPT. R-37 compares the fact tables to
score_model and R-38 compares thresholds to the spec - both verify the repo
against ITSELF and pass happily on data that is a week old. This is the only
check that asks whether what we hold is what the world last published.

    python pipelines/vintage_check.py               # since the last edition
    python pipelines/vintage_check.py 2026-09-06    # since a given date
"""
import io
import os
import sys
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phtime as pt
import week_ahead as wa
import score_model as sm

CCY = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}

# Rows whose actual lives somewhere other than score_model.ROWS, so a blank
# held value is correct rather than stale.
NO_HELD = ('GDP Growth Rate QoQ',)          # LD-117: calibrator-only


def stale(since, until=None):
    """[(ccy, row, held, released, date, te_event)] for rows we hold stale."""
    names, held = {}, {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        c = sm.LABEL[iso]
        names.setdefault(c, []).append(name)
        held[(c, name)] = a

    found = {}
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
            act = (r.get('actual') or '').strip()
            if iso not in CCY or not act:
                continue
            when = pt.te_pht(r.get('date'), r.get('time'))
            ds = when.strftime('%Y-%m-%d') if when else (r.get('date') or '')
            if not ds or ds <= since or (until and ds > until):
                continue
            ccy = CCY[iso]
            hit = wa.match(str(r.get('event', '')).lower(),
                           names.get(ccy, []), iso)
            if not hit:
                continue
            key = (ccy, hit)
            if key not in found or ds > found[key][0]:
                found[key] = (ds, act, str(r.get('event')))

    out = []
    for (c, n), (ds, act, raw) in sorted(found.items()):
        if n in NO_HELD:
            continue
        if held.get((c, n)) != act:
            out.append((c, n, held.get((c, n)), act, ds, raw))
    return out, len(found)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args:
        since = args[0]
    else:
        hdr = io.open(os.path.join(REPO, 'STATE.md'),
                      encoding='utf-8').read()[:1200]
        since = ''
        for line in hdr.splitlines():
            if line.startswith('prev_edition:'):
                since = line.split(':', 1)[1].strip().split()[0]
                break
        since = since or '2026-09-06'

    rows, seen = stale(since)
    print('R-40 VINTAGE CHECK   releases after %s' % since)
    print('  whitelist rows with a print in the window : %d' % seen)
    print('  rows whose held value is STALE            : %d' % len(rows))
    print()
    if rows:
        print('%-4s %-34s %-12s %-12s %-11s %s'
              % ('CCY', 'ROW', 'HELD', 'RELEASED', 'WHEN', 'TE EVENT'))
        for c, n, old, new, ds, raw in rows:
            print('%-4s %-34s %-12s %-12s %-11s %s'
                  % (c, n[:34], old or '(blank)', new, ds, raw[:30]))
        print()
        print('  *** THE EDITION IS SCORED ON DATA THE WORLD HAS SUPERSEDED.')
        sys.exit(1)
    print('  every whitelist row holds the latest print we have captured')
