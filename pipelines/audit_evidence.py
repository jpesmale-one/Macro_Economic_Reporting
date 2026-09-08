# -*- coding: utf-8 -*-
"""R-37: the fact-table SCORE and the score_model EVIDENCE must agree.

F-94. On 2026-09-08 nine rows were graded from TE and the +1/0/-1 written
into the CSVs - but score_model.ROWS, which holds actual/previous/ref, was
not updated for five of them. The audit view then rendered NFP as "-23K"
while scoring it +1 off the +162K print.

The scores were right. The published evidence contradicted them, and nothing
checked.

TWO CHECKS, and they catch different failures:

  VERDICT   score_model's GOOD/NEUTRAL/BAD must map to the CSV cell. Catches
            a cell updated without its evidence, or the reverse.

  VINTAGE   score_model's ref month must not lag the latest RELEASED row for
            that indicator in the capture. Catches F-91 - our row holding
            JUL after the AUG print landed - which the verdict check cannot
            see, because a stale row can still be internally consistent.

USAGE
    python pipelines/audit_evidence.py [capture.json]

THE REAL FIX IS STRUCTURAL. Both halves exist because a release has to be
written into two places. Put actual/previous/ref in the fact tables beside
the score and this whole class disappears.
"""
import io, os, re, sys, csv, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fact_tables as ft
import score_model as sm

VERDICT = {'GOOD': '1', 'NEUTRAL': '0', 'BAD': '-1'}
MONTHS = ('jan', 'feb', 'mar', 'apr', 'may', 'jun',
          'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
ISO = {'US': 'USD', 'GB': 'GBP', 'EA': 'EUR', 'JP': 'JPY',
       'CH': 'CHF', 'CA': 'CAD', 'AU': 'AUD', 'NZ': 'NZD'}


def month_key(text):
    """('Jul/26' | 'balance of trade aug') -> a sortable (year, month)."""
    t = (text or '').lower()
    q = re.search(r'\bq([1-4])[/ ]?(\d{2})?', t)
    if q:
        yr = int(q.group(2)) if q.group(2) else 0
        return (yr, int(q.group(1)) * 3)
    m = re.search(r'\b(%s)\b' % '|'.join(MONTHS), t)
    if not m:
        return None
    yr = re.search(r'/(\d{2})', t)
    return (int(yr.group(1)) if yr else 0, MONTHS.index(m.group(1)) + 1)


def verdict_check():
    """Every CSV cell must equal the verdict score_model records."""
    cells = {}
    for cat in ft.WEIGHT:
        if cat == 'Interest_Rate':
            continue                      # rate rows live in rate_model
        for r in ft.load(cat):
            cells[(r['Currency'].strip(), r['Indicator'].strip())] = \
                (r.get(ft.latest_month()) or '').strip()
    bad = []
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        k = (sm.LABEL[iso], name)
        if k not in cells:
            continue
        want = VERDICT.get(v, '')
        if cells[k] != want:
            bad.append((k[0], k[1], v, want, cells[k]))
    return bad, len(cells)


def vintage_check(capture):
    """Our ref month must not lag the latest RELEASED row in the capture."""
    raw = json.load(io.open(capture, encoding='utf-8'))
    import week_ahead as wa
    latest = {}
    for e in raw:
        if e.get('iso') not in ISO or not (e.get('actual') or '').strip():
            continue
        ccy = ISO[e['iso']]
        hit = wa.match(e.get('event', '').lower(),
                       [r[2] for r in sm.ROWS if sm.LABEL[r[1]] == ccy],
                       e.get('iso'))
        if not hit:
            continue
        mk = month_key(e.get('event', ''))
        if mk is None:
            continue
        # TE's event text carries no YEAR ('...pmi final aug'), so month_key
        # returns year 0 and every comparison against our 'Jul/26' fails -
        # the check passed vacuously and missed F-91. Take the year from the
        # row's own release date, stepping back one when the reference month
        # is ahead of it (a Dec print released in Jan).
        yr = int((e.get('date') or '0000')[2:4] or 0)
        rel_m = int((e.get('date') or '0000-01')[5:7] or 1)
        if mk[1] > rel_m:
            yr -= 1
        mk = (yr, mk[1])
        cur = latest.get((ccy, hit))
        if cur is None or mk > cur[0]:
            latest[(ccy, hit)] = (mk, e.get('actual'), e.get('date'))
    bad = []
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        k = (sm.LABEL[iso], name)
        if k not in latest:
            continue
        ours = month_key(ref)
        theirs = latest[k][0]
        if ours is not None and theirs > ours:
            bad.append((k[0], k[1], ref, a, latest[k][1], latest[k][2]))
    return bad, len(latest)


if __name__ == '__main__':
    cap = (sys.argv[1] if len(sys.argv) > 1 else
           sorted(glob.glob(os.path.join(
               REPO, 'data/raw/calendar/*_cal_full.json')))[-1])
    print('R-37 EVIDENCE AUDIT')
    print('  capture: %s' % os.path.basename(cap))
    print()

    bad, n = verdict_check()
    print('VERDICT vs CELL  (%d rows)' % n)
    if bad:
        for ccy, nm, v, want, got in bad:
            print('  *** %-4s %-34s verdict=%-8s cell=%s (want %s)'
                  % (ccy, nm[:34], v, got, want))
    else:
        print('  every cell matches its verdict')
    print()

    vb, vn = vintage_check(cap)
    print('VINTAGE  (%d rows matched in the capture)' % vn)
    if vb:
        for ccy, nm, ref, a, te_a, te_d in vb:
            print('  *** %-4s %-30s ours=%-9s (%s)  TE=%-9s released %s'
                  % (ccy, nm[:30], a, ref, te_a, te_d))
    else:
        print('  no row lags a released print')
    print()
    print('%d problem(s)' % (len(bad) + len(vb)))
    sys.exit(1 if (bad or vb) else 0)
