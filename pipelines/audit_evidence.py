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
    python pipelines/audit_evidence.py [capture.json] [YYYY-MM-DD as-of]

The as-of date matters for a BACK-DATED edition: the 2026-09-06 weekly holds
four rows at their August values on purpose, because they printed Mon 7 /
Tue 8. Without it the guard calls a correct vintage stale.

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


def vintage_check(capture, asof=None):
    """Our ref month must not lag the latest RELEASED row in the capture.

    ASOF is the build date. A back-dated edition must NOT be measured against
    prints that landed after it - the 2026-09-06 weekly deliberately holds
    four rows at their August values because they printed Mon 7 / Tue 8, and
    without this the guard reports them as stale when they are correct.
    """
    raw = json.load(io.open(capture, encoding='utf-8'))
    import week_ahead as wa
    latest = {}
    for e in raw:
        if e.get('iso') not in ISO or not (e.get('actual') or '').strip():
            continue
        if asof and (e.get('date') or '') > asof:
            continue                      # not knowable at the build date
        # PREL and FINAL are different rows for the same reference month.
        # Matching a Prel actual against a Final row reports a stale value
        # that is not stale - AUD Building Permits YoY Final was flagged off
        # the 1 Sep PREL while its own Final had not released.
        _ev = (e.get('event') or '').lower()
        _prel = ' prel' in _ev
        ccy = ISO[e['iso']]
        hit = wa.match(_ev,
                       [r[2] for r in sm.ROWS if sm.LABEL[r[1]] == ccy],
                       e.get('iso'))
        if not hit:
            continue
        if _prel and 'final' in hit.lower():
            continue                      # a Prel never supersedes a Final
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
    if len(sys.argv) > 2:
        print('  as of  : %s (later prints ignored)' % sys.argv[2])
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

    asof = sys.argv[2] if len(sys.argv) > 2 else None
    vb, vn = vintage_check(cap, asof)
    print('VINTAGE  (%d rows matched in the capture)' % vn)
    if vn == 0:
        # A check that matched nothing has PROVED nothing. This bit twice:
        # first when TE's year-less event text made every comparison false,
        # then when an as-of cutoff against a forward-looking capture left
        # no released rows at all. Say so rather than printing a green line.
        print('  *** MATCHED NO ROWS - this check proved NOTHING.')
        print('      A forward-looking capture holds few released rows, and')
        print('      an as-of cutoff can remove the rest. Point it at a')
        print('      capture taken ON or BEFORE the build date.')
        vb = list(vb) + [('*', 'vintage check matched no rows',
                          '-', '-', '-', '-')]
    elif vb:
        for ccy, nm, ref, a, te_a, te_d in vb:
            print('  *** %-4s %-30s ours=%-9s (%s)  TE=%-9s released %s'
                  % (ccy, nm[:30], a, ref, te_a, te_d))
    else:
        print('  no row lags a released print')
    print()
    print('%d problem(s)' % (len(bad) + len(vb)))
    sys.exit(1 if (bad or vb) else 0)
