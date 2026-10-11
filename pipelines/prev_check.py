# -*- coding: utf-8 -*-
"""R-48 - THE prev COLUMN HAS NO AUTHORITY AND NOTHING WATCHED IT.

Jeff, 2026-10-12, after finding two bad rows by eye:

    "JPY Consumer Confidence -- can you verify in TE the previous seems to be
     having a different value"
    "CHF Procure.ch-UBS Mfg PMI 55.3 53.2 Sep/26 -- scan the report fully.
     I saw another error. Every week we are facing the same issue again and
     again"

HE IS RIGHT THAT IT RECURS, AND THE REASON IS STRUCTURAL. sync_score_model.py
says so in its own header:

    "The CSVs carry Currency, Indicator and the month columns. They do NOT
     carry `prev`, `ref` or `threshold`, which exist only in the literal."

So refresh_rows advances the ACTUAL, roll_month rolls the CSV columns, and
sync_score_model copies the actual and the ref month across - AND NOTHING
TOUCHES prev. It keeps whatever it held when the row was last hand-edited,
which is the value from the PREVIOUS release. Every refresh leaves it one
vintage behind. That is why it comes back every week: the refresh path has no
step that owns it.

*** WHAT THE 2026-10-12 SCAN FOUND: 26 of 41 matchable rows had a prev that
disagreed with TE. Only THREE changed a score, because most thresholds are
BANDS (>50.5, >0.5%) that never read prev - CHF's PMI is one of those, which
is why its wrong 53.2 was cosmetic. But the table PRINTS prev beside the
score, so a wrong value there is the F-151 defect exactly: a column that
invites a reader to check the working and then shows them the wrong working.

THE THREE THAT SCORED:
    JPY Consumer Confidence   34.9 -> 35.5   +1 -> -1
    JPY Unemployment Rate     2.5% -> 2.4%    0 -> -1
    EUR Unemployment Rate     6.3% -> 6.4%   -1 ->  0
JPY went +0.87 -> -1.47 on the FINAL, sixth to seventh, below CHF.

THIS GUARD compares each row's prev against the TE 'previous' of the release
its ACTUAL came from, using the capture history. A row whose actual advanced
while its prev stayed put is an INCONSISTENT PAIR and fails. Rows the captures
cannot match are reported as UNVERIFIED rather than silently passed - the
F-152 lesson: silence is not a pass.

    python pipelines/prev_check.py
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import score_model as sm
import derive_scores as ds

ISO = {'USD': 'US', 'EUR': 'EA', 'GBP': 'GB', 'JPY': 'JP',
       'AUD': 'AU', 'NZD': 'NZ', 'CAD': 'CA', 'CHF': 'CH'}

# Rows verified by direct TE page read on 2026-10-12, where the capture
# history carries no released row to match against. Each is the value TE
# shows as 'Previous' beside the actual we hold.
VERIFIED = {
    ('USD', 'Unemployment Rate'): '4.1%',     # TE: Sep 4.2, Aug 4.1
    ('NZD', 'Unemployment Rate'): '5.4%',     # TE: Q2 5.6, Q1 5.4 (revised)
    ('JPY', 'Consumer Confidence'): '35.5',   # TE: Actual 35.40 Previous 35.50
    ('NZD', 'ANZ Business Confidence'): '53.7',   # TE: Sep 51.9, Aug 53.7
}


def _norm(v):
    return (v or '').replace(' \u00ae', '').replace(',', '').strip()


def te_previous():
    """{(iso, actual): (date, event, previous)} from every capture."""
    idx = {}
    for f in sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json'))):
        try:
            rows = json.load(io.open(f, encoding='utf-8'))
        except Exception:
            continue
        for r in rows if isinstance(rows, list) else []:
            a = (r.get('actual') or '').strip()
            if not a:
                continue
            k = (r.get('iso'), a)
            d = r.get('date', '')
            if k not in idx or d > idx[k][0]:
                idx[k] = (d, r.get('event', ''), (r.get('previous') or '').strip())
    return idx


def audit():
    """([(ccy,ind,held,want,scores)], [unverified])"""
    idx = te_previous()
    bad, unv = [], []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        ccy = sm.LABEL[iso]
        want = VERIFIED.get((ccy, name))
        if want is None:
            e = idx.get((ISO[ccy], str(act).split(' (')[0].strip()))
            want = e[2] if e else None
        if not want:
            unv.append((ccy, name, act, prev))
            continue
        if _norm(prev) == _norm(want):
            continue
        # does it change the score?
        s1 = ds.prev_score(act, prev, thr)
        s2 = ds.prev_score(act, want, thr)
        bad.append((ccy, name, prev, _norm(want), s1, s2, thr))
    return bad, unv


# ---------------------------------------------------------------- F-154 ---
# *** JEFF FOUND THE ROOT CAUSE I MISSED, AND IT IS SIMPLER THAN MINE.
#
# He selected the CSV line and asked: "What's bugging me is that in CVS file
# the numbers are correct. look at this
#     CHF,Procure.ch-UBS Mfg PMI,Monthly,57.1,57.1,55.3
# Then why are you printing a different value in the report?"
#
# HE IS RIGHT. The CSV held 57.1 in the prior column - the correct previous -
# while score_model.ROWS held 53.2. I had just spent a whole pass verifying
# that value against TE pages when IT WAS SITTING IN THE ADJACENT COLUMN of
# the file the board already reads.
#
# THAT IS F-141 AGAIN, ON A DIFFERENT FIELD. score_model.ROWS is a
# hand-written second copy of data the CSVs own. F-141 fixed the ACTUAL
# drifting and F-141b fixed the REF month drifting; prev was the third field
# and nobody looked, because sync_score_model's header says the CSVs "do NOT
# carry prev" - which is true of a COLUMN NAMED prev and false of the DATA:
# the previous print is the column to the left.
#
# *** BUT THE NAIVE RULE IS WRONG, which is why this derives rather than
# copies. roll_month COPIES A NON-PRINTING SERIES FORWARD, so the prior
# column is often the SAME print as the current one:
#
#     CHF Balance of Trade   Aug CHF8.1B | Sep CHF5.6B | Oct CHF5.6B
#                                              ^^^^^^^^^^^^^^^^^^ same print
#
# Reading Sep as "previous" there compares the print to ITSELF and scores a
# false NEUTRAL. Tested across the board: of the 12 rows where the prior
# column disagreed with score_model, TEN were carried duplicates. So the rule
# is LAST DISTINCT VALUE, and None when the 3-month window holds none.
#
# AND THE CSV IS NOT THE FINAL AUTHORITY EITHER. It stores the print AS FIRST
# PUBLISHED (LD-112) and TE revises: USD NFP's August print is 162K in the CSV
# and 133K on TE today. Both score -1 against 29K, so the SCORE is robust -
# but the held -23K was JULY's print and scored +1. That was the real defect.
#
# SO THIS GUARD READS BOTH: the CSV for the vintage CHAIN (which print is the
# previous one) and TE for the VALUE (LD-3). They answer different questions.
# Rows where the CSV and TE legitimately disagree because TE REVISED the
# previous print. Both point at the SAME MONTH, so this is a value question,
# not a vintage one, and LD-3 settles it: the indicator page owns the VALUE.
# Listing a row here asserts THE MONTH IS RIGHT and the difference is a
# revision - it is not a way to silence a wrong-month row.
REVISED = {
    ('EUR', 'Unemployment Rate'): 'Jul/26: CSV 6.3% as first published, '
                                  'TE 6.4% revised. Same month.',
    ('USD', 'Non Farm Payrolls'): 'Aug/26: CSV 162K as first published, '
                                  'TE 133K revised. Same month.',
}


COLS = ['Aug-26', 'Sep-26', 'Oct-26']


def _csv():
    import fact_tables as ft
    t = {}
    for cat in ('Production', 'Spending', 'Trade', 'Employment', 'Inflation'):
        for r in ft.load(cat):
            t[(r['Currency'].strip(), r['Indicator'].strip())] = r
    return t


def csv_prev(ccy, name, tbl=None):
    """The last DISTINCT value before the current month, or None.

    Skips carried duplicates - roll_month copies a non-printing series
    forward, so prior == current means the series did not re-print and that
    column is NOT a previous print.
    """
    tbl = tbl if tbl is not None else _csv()
    r = tbl.get((ccy, name))
    if not r:
        return None
    vals = [(c, (r.get(c) or '').strip()) for c in COLS]
    cur = vals[-1][1]
    for c, v in reversed(vals[:-1]):
        if v and v != cur:
            return v
    return None


def csv_audit():
    """[(ccy, name, held, csv_says, s_held, s_csv, thr)] - prev vs the CSV."""
    tbl = _csv()
    out = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        ccy = sm.LABEL[iso]
        cp = csv_prev(ccy, name, tbl)
        if cp is None or _norm(prev) == _norm(cp):
            continue
        out.append((ccy, name, prev, cp,
                    ds.prev_score(act, prev, thr),
                    ds.prev_score(act, cp, thr), thr))
    return out


def main():
    bad, unv = audit()
    print('R-48 prev AUDIT   score_model.prev vs the TE previous of that '
          'release')
    print()
    scoring = [b for b in bad if b[4] != b[5]]
    if bad:
        print('  %-4s %-30s %-11s %-11s %s'
              % ('CCY', 'INDICATOR', 'held', 'TE says', 'score'))
        for ccy, nm, held, want, s1, s2, thr in bad:
            flag = ('%+d -> %+d  *** SCORES' % (s1 or 0, s2 or 0)
                    if s1 != s2 else 'cosmetic (thr %s)' % thr)
            print('  %-4s %-30s %-11s %-11s %s'
                  % (ccy, nm[:30], str(held)[:11], want[:11], flag))
        print()
    print('  %d row(s) disagree with TE, %d of them change a score'
          % (len(bad), len(scoring)))
    print('  %d row(s) UNVERIFIED - no released capture row to match'
          % len(unv))
    # F-154 - AND AGAINST THE CSV, which is where Jeff found it. The vintage
    # CHAIN lives there; a disagreement that changes a score means prev is
    # pointing at the wrong PRINT, not merely an unrevised value.
    ca = csv_audit()
    cflip = [c for c in ca if c[4] != c[5] and (c[0], c[1]) not in REVISED]
    crev = [c for c in ca if c[4] != c[5] and (c[0], c[1]) in REVISED]
    print()
    print('  vs the CSV vintage chain: %d differ, %d change a score, '
          '%d are known revisions' % (len(ca), len(cflip), len(crev)))
    for ccy, nm, held, want, s1, s2, thr in cflip:
        print('      *** %-4s %-28s held %-11s csv %-11s %+d -> %+d'
              % (ccy, nm[:28], str(held)[:11], str(want)[:11], s1 or 0, s2 or 0))
    if unv:
        for ccy, nm, a, p in unv[:40]:
            print('      %-4s %-30s act=%-11s prev=%s'
                  % (ccy, nm[:30], str(a)[:11], p))
    # A prev that CHANGES A SCORE is a failure. A cosmetic one is reported
    # but does not block a build - it is a display defect, not a wrong board.
    if scoring or cflip:
        print()
        print('  *** %d row(s) scoring off a wrong previous (TE), %d (CSV)'
              % (len(scoring), len(cflip)))
        return 1
    print()
    print('  no row is scoring off a wrong previous')
    return 0


if __name__ == '__main__':
    sys.exit(main())