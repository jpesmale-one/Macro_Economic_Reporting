# -*- coding: utf-8 -*-
"""R-32 - every 4.0 time must equal pht(capture) (F-77).

Jeff, 2026-09-02: "Every time we fetch Data can you always verify the Time
first? as per TE RBNZ is scheduled 10AM today roughly in 1 Hr"

He was right and the edition was wrong. 4.0 published "Wed 02 02:00" for the
RBNZ decision; pht() on the same capture row returns 10:00 - which is exactly
what his screen showed.

THE BUG WAS MINE, TWICE OVER:

  1. The EV list in the 4.0 builder carries HAND-TYPED times. They were
     never checked against the capture, so once one was wrong it stayed
     wrong through every rebuild.

  2. I then read "02:00 PHT" off the RENDERED TABLE and converted it
     BACKWARDS to 18:00 UTC to argue the decision had already passed. The
     cell was the LABEL - already converted. I converted twice, concluded
     the RBNZ was five hours late, and wrote a section about its silence.

Price "confirmed" it because NZD really was flat - the decision had not
happened yet. A wrong premise that agrees with the evidence is the most
expensive kind, and it is why F-72's rule exists: when our data disagrees
with what Jeff sees on screen, we are wrong until proven otherwise.

This guard removes the hand-typed times from the trust path entirely.

    python pipelines/audit_times.py <edition.md>
"""
import io, os, re, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from week_ahead import pht, CCY, match
import score_model as sm

CAL = os.path.join(os.path.dirname(HERE), 'data', 'raw', 'calendar')
ISO = {'USD': 'US', 'JPY': 'JP', 'AUD': 'AU', 'NZD': 'NZ', 'GBP': 'GB',
       'CAD': 'CA', 'CHF': 'CH', 'EUR': 'EA'}
DAY = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}


def capture_rows(path=None):
    caps = sorted(glob.glob(os.path.join(CAL, '*_cal_full.json')))
    if path is None:
        path = caps[-1]
    return json.load(io.open(path, encoding='utf-8'))


def check(md, rows=None):
    """Every 4.0 When-cell must match pht() on the capture row it names."""
    if rows is None:
        rows = capture_rows()
    idx = {}
    for r in rows:
        idx.setdefault(r['iso'], []).append(r)

    try:
        blk = md[md.index('| When (PHT) | CCY | Indicator |'):md.index('### 4.1')]
    except ValueError:
        return 'no 4.0 table'

    bad, checked = [], 0
    for line in blk.split(chr(10)):
        if not line.startswith('|') or 'When (PHT)' in line:
            continue
        if set(line.replace('|', '').strip()) <= set('- :'):
            continue
        c = [x.strip().replace('*', '') for x in line.strip('|').split('|')]
        if len(c) < 8:
            continue
        when = c[0]
        m = re.search(r'(\d{2}):(\d{2})', when)
        if not m:
            continue                      # untimed row
        ccy = c[1]
        ind = re.sub(r'^⚠\s*', '', c[2]).strip()
        key = ISO.get(ccy)
        if not key:
            continue
        toks = [t for t in re.findall(r'[a-z&.]+', ind.lower())
                if t not in ('the', 'of', 'a')]
        hit = None
        for r in idx.get(key, []):
            if all(t in r['event'] for t in toks):
                hit = r
                break
        if hit is None:
            continue                      # coverage is R-25's job, not this
        p = pht(hit.get('date', ''), hit.get('time', ''))
        if p is None:
            continue
        checked += 1
        want = '%s %02d %02d:%02d' % (DAY[p.weekday()], p.day, p.hour, p.minute)
        got = when.strip()
        if not got.startswith(want[:6]) or got[-5:] != want[-5:]:
            bad.append((ccy, ind, got, want))

    if bad:
        lines = ['FATAL (R-32/F-77): %d 4.0 time(s) disagree with the capture.'
                 % len(bad)]
        for ccy, ind, got, want in bad:
            lines.append('  %-4s %-34s table says %-16s capture says %s'
                         % (ccy, ind[:34], got, want))
        lines.append('The When cell is a LABEL. pht(capture) is the SOURCE.')
        lines.append('Never hand-type a time and never re-convert a rendered')
        lines.append('one - that is F-77, which had the RBNZ eight hours early')
        lines.append('and produced a whole section about a decision that had')
        lines.append('not happened yet.')
        raise SystemExit(chr(10).join(lines))
    return '%d 4.0 time(s) match pht(capture)' % checked


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src:
        raise SystemExit('usage: audit_times.py <edition.md>')
    print(check(io.open(src, encoding='utf-8').read()))
