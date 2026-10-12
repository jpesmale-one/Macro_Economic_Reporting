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


def _evmatch(ev, name):
    """Does a TE event stem match our whitelist name? Conservative.

    SERIES IDENTITY IS LOAD-BEARING (F-29/F-37): 'Final' and the transform
    (YoY/MoM/QoQ) are part of the name, so a PREL must not satisfy a FINAL
    row and a MoM must not satisfy a YoY one.
    """
    import re as _re
    w = set(_re.sub(r'[^a-z0-9 ]', ' ', name.lower()).split())
    g = set(_re.sub(r'[^a-z0-9 ]', ' ', ev.lower()).split())
    for tag in ('final', 'prel', 'flash', 'core'):
        if (tag in w) != (tag in g):
            return False
    for x in ('yoy', 'mom', 'qoq'):
        if (x in w) != (x in g):
            return False
    # *** THE FIRST VERSION ALLOWED A SUBSET MATCH IN EITHER DIRECTION, AND
    # THAT PRODUCED A FALSE POSITIVE IMMEDIATELY - exactly the failure F-37
    # exists to prevent. 'goods trade balance adv aug' satisfied our 'Balance
    # of Trade' row because {balance, trade} is a subset of {goods, trade,
    # balance, adv}, and the guard then reported USD Balance of Trade as
    # scoring off a wrong previous using a number from a DIFFERENT SERIES
    # (the advance goods figure, $-118.8B, against the real $-88.6B).
    #
    # A FALSE POSITIVE IS WORSE THAN THE GAP IT CLOSED: it sends the reader
    # to correct a row that is right. So the match is now EXACT on the
    # significant words, and any extra qualifier in the TE event - adv, goods,
    # ex, excluding - disqualifies it.
    DROP = {'the', 'of', 'rate', 'index'}
    w -= DROP
    g -= DROP
    if g - w:
        return False          # the TE event carries a qualifier we do not
    return bool(w) and w == g


_BYMON = {}


def audit():
    """([(ccy,ind,held,want,scores)], [unverified])"""
    idx = te_previous()
    if not _BYMON:
        _BYMON.update(te_previous_by_month())
    bad, unv = [], []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        ccy = sm.LABEL[iso]
        want = VERIFIED.get((ccy, name))
        if want is None:
            e = idx.get((ISO[ccy], str(act).split(' (')[0].strip()))
            want = e[2] if e else None
        if not want:
            # F-155 - SECOND CHANCE BEFORE EXCUSING THE ROW. Try the ref
            # month against rows that carry a `previous` whether or not they
            # have an actual: a SCHEDULED row states the previous of the print
            # we hold, and that is the row the released-only index missed.
            mon = _refmon(ref)
            if mon:
                for (i2, m2, ev), (d2, e2, pv2) in _BYMON.items():
                    if i2 != ISO[ccy] or m2 != mon:
                        continue
                    if not _evmatch(ev, name):
                        continue
                    want = pv2
                    break
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
# ---------------------------------------------------------------- F-155 ---
# *** THE INDEX ONLY MATCHED **RELEASED** ROWS, SO A ROW WHOSE PRINT WE HOLD
# BUT NEVER CAPTURED FELL INTO "UNVERIFIED" AND PASSED.
#
# Jeff, 2026-10-12: "AUD ANZ-Indeed Job Ads MoM 2.2% 1.9% Sep/26 >0.5%
# -- Previous data is wrong as per TE can you check?"
#
# He was right, and R-48 had reported that row as UNVERIFIED rather than as
# wrong - the second time this session a guard's SILENCE read as a pass
# (F-152 was the first). The mechanism:
#
#   te_previous() keys on (iso, OUR HELD ACTUAL) and only indexes rows that
#   HAVE an actual. We hold 2.2% for Sep/26. No capture contains an AU job-ads
#   row with actual 2.2%, because the 6 Oct release was never captured with
#   its result - we only have the SCHEDULED row from before it printed. So the
#   lookup missed and the row was excused.
#
# *** THE ANSWER WAS SITTING IN THAT SCHEDULED ROW. TE publishes `previous`
# on a row BEFORE it releases:
#
#     2026-09-07  job ads mom AUG   actual 2.5%   previous 1.9%
#     2026-10-06  job ads mom SEP   actual  -     previous 2.5%   <- this one
#     2026-11-02  job ads mom OCT   actual  -     previous 2.2%
#
# The 6 Oct row states the previous of the very print we hold. We held 1.9% -
# the AUGUST release's previous - so the actual had advanced 2.5% -> 2.2%
# while prev stayed behind. Identical shape to F-154's JPY Consumer
# Confidence, which is why it must be CHECKED and not merely corrected.
#
# SO THE INDEX NOW ALSO KEYS ON (iso, event-month) FROM SCHEDULED ROWS. A
# scheduled row's `previous` is as authoritative as a released row's - more
# useful here, because it is published the moment the event is calendared.
MONTHS = ('jan', 'feb', 'mar', 'apr', 'may', 'jun',
          'jul', 'aug', 'sep', 'oct', 'nov', 'dec')


def _refmon(ref):
    """'Sep/26' -> 'sep', or None. Quarterly refs ('Jun/26 (Q)') too."""
    r = (ref or '').strip().lower()
    return r[:3] if r[:3] in MONTHS else None


def te_previous_by_month():
    """{(iso, 3-letter ref month): (date, event, previous)} from ANY row.

    Includes rows with NO actual - a scheduled row publishes `previous`, and
    that is precisely the row F-155 needed. Latest capture date wins, so a
    revision supersedes the first publication.
    """
    idx = {}
    for f in sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json'))):
        try:
            rows = json.load(io.open(f, encoding='utf-8'))
        except Exception:
            continue
        for r in rows if isinstance(rows, list) else []:
            pv = (r.get('previous') or '').strip()
            if not pv:
                continue
            e = (r.get('event') or '').lower().split()
            mon = e[-1][:3] if e and e[-1][:3] in MONTHS else None
            if not mon:
                continue
            k = (r.get('iso'), mon, ' '.join(e[:-1]))
            d = r.get('date', '')
            if k not in idx or d > idx[k][0]:
                idx[k] = (d, r.get('event', ''), pv)
    return idx


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