# -*- coding: utf-8 -*-
"""
Two checks the repo never had, both asked for by Jeff on 2026-08-24:

  1. REVISION DETECTION - "There are instances where the Previous Actual value
     gets updated, are we capturing these changes?"
  2. CADENCE STALENESS - "We also need see if there are indicator if its
     getting stalled. Meaning not being updated on a Monthly basis. Of course
     with exception of Quarterly data"

WHY BOTH MATTER, and why neither existed:

REVISIONS. LD-3 flagged this on the repo's FIRST DAY - "Trading Economics ...
its Previous column is revised in place and sits adjacent to Actual". Nothing
was ever built to detect it. Three revisions were hit in one session and all
three were caught by reading, not by tooling:
    JPY Inflation      previous 1.7% -> revised 1.6%   (Statistics Bureau)
    NZD Balance of Trade  Jun previous 577M -> -0.24B  (TE series page)
    USD Manufacturing Production  country page's "1.5" was the FORECAST
A revised Previous silently changes a DIRECTION claim. "2.9% from 2.8%,
rising" becomes "2.9% from 3.0%, falling" - same Actual, opposite read. That
is F-4 exactly, and F-4 cost a withdrawn conclusion.

STALENESS. LD-50 checks the age of the TE CAPTURE - whether we re-read the
source. It does NOT check whether a SERIES has stopped producing prints. An
indicator can sit at Jun/26 through August with a perfectly fresh capture,
because the capture faithfully reports that nothing new arrived. LD-49 made
this a manual sort; this makes it a check.

CADENCE IS INFERRED, NEVER ASSUMED. NZD Unemployment and Inflation carry
month-style labels ("Jun/26") but are QUARTERLY by construction - LD-13 says
so, and reading the label alone misclassifies them. Cadence comes from the
KNOWN_QUARTERLY set plus the reference-period style, in that order.

DATA + ARITHMETIC ONLY. Never edits score_model.py.
"""
import re, io, os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SNAP = os.path.join(REPO, 'data', 'raw', 'whitelist_snapshots')
sys.path.insert(0, HERE)

MON = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
       'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

# Series that are QUARTERLY regardless of how their reference period is
# written. NZ employment and inflation are quarterly by construction (LD-13
# already flags them as "late by construction"); Swiss payrolls and industrial
# production are quarterly releases.
KNOWN_QUARTERLY = {
    ('NZ', 'Unemployment Rate'), ('NZ', 'Inflation Rate YoY'),
    ('NZ', 'Employment Change'), ('CH', 'Non Farm Payrolls'),
    ('CH', 'Industrial Production YoY'), ('AU', 'Inflation Rate YoY'),
    ('GB', 'GDP Growth Rate QoQ'), ('EA', 'GDP Growth Rate QoQ'),
}


def parse_ref(ref):
    """('M'|'Q'|None, year, month-of-period-end)."""
    r = (ref or '').lower().strip()
    y = re.search(r'(\d{2,4})', r)
    yy = int(y.group(1)) if y else 0
    if yy and yy < 100:
        yy += 2000
    m = re.match(r'q([1-4])', r)
    if m:
        return ('Q', yy, int(m.group(1)) * 3)
    for k, v in MON.items():
        if r.startswith(k):
            return ('M', yy, v)
    return (None, 0, 0)


def cadence(iso, name, ref):
    if (iso, name) in KNOWN_QUARTERLY:
        return 'Q'
    return parse_ref(ref)[0]


def months_behind(ref, now_y, now_m):
    kind, yy, mm = parse_ref(ref)
    if not kind:
        return None
    return (now_y - yy) * 12 + (now_m - mm)


def snapshot(path=None):
    """Persist today's whitelist so the NEXT run can detect revisions.

    A revision is only visible by comparing two points in time. Nothing in
    this repo ever stored the previous state, which is the mechanical reason
    revisions went undetected.
    """
    import score_model as sm
    if not os.path.isdir(SNAP):
        os.makedirs(SNAP)
    import datetime
    stamp = datetime.date.today().isoformat()
    path = path or os.path.join(SNAP, stamp + '.json')
    rows = {'%s|%s' % (r[1], r[2]): {'actual': r[3], 'previous': r[4],
                                     'ref': r[5], 'score': r[7]}
            for r in sm.ROWS}
    io.open(path, 'w', encoding='utf-8').write(
        json.dumps(rows, indent=1, sort_keys=True))
    return path, len(rows)


def revisions():
    """Rows whose PREVIOUS, REF or SCORE changed since the last snapshot.

    Returns (found, snapshot_name). `found` is a list of
    (ccy, indicator, field, was, now).
    """
    import score_model as sm
    snaps = sorted(glob.glob(os.path.join(SNAP, '*.json')))
    if not snaps:
        return [], None
    old = json.load(io.open(snaps[-1], encoding='utf-8'))
    out = []
    for r in sm.ROWS:
        key = '%s|%s' % (r[1], r[2])
        if key not in old:
            out.append((sm.LABEL[r[1]], r[2], 'NEW ROW', '-', r[3]))
            continue
        o = old[key]
        for field, idx in (('previous', 4), ('actual', 3), ('ref', 5), ('score', 7)):
            if o.get(field if field != 'ref' else 'ref') != r[idx]:
                out.append((sm.LABEL[r[1]], r[2], field,
                            o.get(field if field != 'ref' else 'ref'), r[idx]))
    return out, os.path.basename(snaps[-1])


def stalled(now_y=2026, now_m=8):
    """Series that have stopped producing prints, cadence-aware.

    A MONTHLY series more than 2 reference months behind is stalled: one month
    is normal reporting lag, two is the edge, three means prints are being
    missed. A QUARTERLY series is allowed 5 months.
    """
    import score_model as sm
    out = []
    for r in sm.ROWS:
        cat, iso, name, act, prev, ref, thr, score = r
        cad = cadence(iso, name, ref)
        if not cad:
            continue
        beh = months_behind(ref, now_y, now_m)
        if beh is None:
            continue
        limit = 5 if cad == 'Q' else 2
        if beh > limit:
            out.append((sm.LABEL[iso], name, ref, cad, beh, limit))
    out.sort(key=lambda x: -x[4])
    return out


if __name__ == '__main__':
    print('=' * 74)
    print('FRESHNESS CHECK - revisions and cadence staleness')
    print('=' * 74)

    rev, snap_name = revisions()
    print('\n1. REVISIONS since %s' % (snap_name or 'NO PRIOR SNAPSHOT'))
    if snap_name is None:
        print('   No snapshot yet - today establishes the baseline.')
    elif not rev:
        print('   No row changed.')
    else:
        print('   %d change(s) - a revised PREVIOUS can flip a direction claim '
              '(F-4):\n' % len(rev))
        for ccy, name, field, was, now in rev:
            print('   %-4s %-32s %-9s %-12s -> %s' % (ccy, name[:32], field,
                                                      was, now))

    st = stalled()
    print('\n2. STALLED SERIES (monthly > 2 months behind, quarterly > 5)')
    if not st:
        print('   None. Every series is producing prints on its cadence.')
    else:
        print('   %d series:\n' % len(st))
        for ccy, name, ref, cad, beh, lim in st:
            print('   %-4s %-32s %-8s %s  %d months behind (limit %d)'
                  % (ccy, name[:32], ref, cad, beh, lim))
    print()
    if '--snapshot' in sys.argv:
        p, n = snapshot()
        print('Snapshot written: %s (%d rows)' % (os.path.basename(p), n))
    else:
        print('Run with --snapshot after reconciling, to set the baseline for '
              'the next edition.')
