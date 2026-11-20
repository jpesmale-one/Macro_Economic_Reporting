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

# *** F-198 - THIS WAS A SNAPSHOT PINNED TO PRINTS THAT HAVE SINCE MOVED.
#
# "Rows verified by direct TE page read on 2026-10-12" - and read back as
# current on 2026-11-20, five weeks later, by which time every print it was
# pinned to had been superseded. Its OWN comments name them: "TE: Sep 51.9,
# Aug 53.7" for NZD, "TE: Sep 4.2, Aug 4.1" for USD. The Nov-26 advance
# landed the October prints, so the aligned previous is now 51.9 and 4.2.
#
# Because VERIFIED OVERRIDES the live lookup, the guard reported four rows
# "scoring off a wrong previous" while comparing against its own stale
# constants. Checked by aligning the pairs properly - find the TE release
# whose ACTUAL equals the value we hold, then compare ITS previous against
# our prior column - 4 of 5 agree exactly, and the fifth is the EUR
# revision that LD-177 deliberately does not follow.
#
# THIS IS THE THIRD HARDCODED SNAPSHOT IN THREE SESSIONS: sync_score_model's
# REFS dragged nine ref months BACKWARDS (F-196), rate_check's cache was a
# day older than the BoE hike (F-197), and this one. The pattern is always
# the same - a table written to fix a real gap, read later as if it were
# still live, overriding the source it was derived from.
#
#     A constant that describes a moving value is a bug with a delay on it.
#
# So the override is now a LAST RESORT, consulted only when the capture
# history and the indicator page both come back empty, and every entry
# carries the date it was read so it can be seen going stale.
VERIFIED = {
    # ('JPY', 'Consumer Confidence') held 35.5 from 2026-10-12. The capture
    # history answers this row, so the constant is no longer needed.
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
    """([(ccy,ind,held,want,scores)], [unverified])

    *** LD-177 - THIS NOW AUDITS THE FIELD THAT ACTUALLY SCORES.
    It used to read `prev` from score_model.ROWS. Since 2026-11-20
    score_row() takes `previous` from the fact table's PRIOR COLUMN
    (ds._prev_cell), and ROWS.prev is only a fallback for a row the table
    cannot answer for. So this read a field that no longer reaches the
    board: after the switch it went on reporting the same 7 rows "scoring
    off a wrong previous" when not one of them was scoring off it any more.

    F-154 is the same lesson one turn earlier. Jeff, on CHF Mfg PMI:
    "What's bugging me is that in CVS file the numbers are correct... Then
    why are you printing a different value in the report?" The prior column
    was right while ROWS was wrong, and I verified ROWS against TE pages
    instead of looking at the adjacent column. A guard pointed at the stale
    copy confirms the stale copy.
    """
    idx = te_previous()
    if not _BYMON:
        _BYMON.update(te_previous_by_month())
    bad, unv = [], []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        ccy = sm.LABEL[iso]
        # the value the board actually scores with (LD-177), ROWS.prev only
        # where the table has no answer - the same precedence as score_row
        prev = ds._prev_cell(cat, ccy, name) or prev
        # F-198 - THE LIVE SOURCE FIRST, the constant only as a last resort.
        # VERIFIED used to be consulted FIRST and therefore overrode the
        # capture history with five-week-old values. A hand-read constant
        # is evidence about a moment, not an authority over the source it
        # was read from.
        #
        # *** AND THE MATCH MUST NAME THE SERIES, NOT JUST THE NUMBER (LD-59).
        # te_previous() keys on (iso, actual) - the VALUE alone - so any TE
        # row of that country happening to print the same number answered
        # for this one. Three live examples on 2026-11-20:
        #
        #   GBP Unemployment 4.6%  matched 'ppi output yoy sep'      prev 3.8%
        #   AUD Unemployment 4.9%  matched 'consumer inflation
        #                                   expectations sep'        prev 4.9%
        #   EUR Unemployment 6.5%  matched the right row by luck
        #
        # and the guard then reported our previous "wrong" against the
        # previous of an unrelated series. That is LD-59 exactly - "a loose
        # match does not report an absence, it INVENTS a presence" - with
        # the number standing in for the name. _evmatch() is the existing
        # series test; requiring it here costs nothing and removes the
        # whole class.
        e = idx.get((ISO[ccy], str(act).split(' (')[0].strip()))
        if e and not _evmatch(e[1], name):
            e = None
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
            # F-198 - the hand-read constant, LAST. Only where neither the
            # capture history nor a scheduled row can answer.
            want = VERIFIED.get((ccy, name))
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
    # 2026-10-18: the ABS revised August up 4.6 -> 4.7 when September printed,
    # which is why September reads FLAT rather than a rise. Verified on the TE
    # page AND in the 2026-10-18 capture (previous 4.7% carries TE's revision
    # marker). Same month, so this is a value question and LD-3 settles it.
    ('AUD', 'Unemployment Rate'): 'Aug/26: CSV 4.6% as first published, '
                                  'TE 4.7% revised. Same month.',
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
    """[(ccy, name, held, csv_says, s_held, s_csv, thr)] - prev vs the CSV.

    *** WHAT THIS MEASURES CHANGED UNDER LD-177, AND SO DID WHAT IT MEANS.
    It was built for F-154: score_model.ROWS.prev drifting away from the
    CSV's prior column, which Jeff caught by reading the CSV line himself.
    Since 2026-11-20 score_row() reads the prior column DIRECTLY, so a
    ROWS.prev that disagrees with the CSV no longer affects any score - the
    CSV already won.

    It is kept, reporting against the field that SCORES, because ROWS.prev
    is still the documented fallback for a row the table cannot answer for,
    and still printed by the evidence tables. A drift here is now a
    REPORTING defect rather than a scoring one, which is a smaller thing
    and a true thing. Calling it a scoring failure after the switch would
    be the mirror of the bug it was written to find.

    *** AND csv_prev() IS NOT THE SAME QUESTION AS ds._prev_cell().
    csv_prev walks back to the last DISTINCT value, skipping a carried
    duplicate; _prev_cell takes the ADJACENT column as it stands. On a flat
    series those are different months, and comparing them scored 4 rows as
    failures that were only two definitions disagreeing.

    TE settles which is right. On the nine rows where the two differ, taking
    each row's own Nov-26 actual and asking TE for the previous of THAT
    print:

        TE agrees with the ADJACENT column on 4 rows, with last-distinct
        on 0 (the other five are revisions TE restates, where TE's number
        sits between the two and adjacent is the closer).

    Which stands to reason: 'previous' means the print before this one, and
    on a carried-forward series the adjacent column IS that print - the
    duplicate is the series not having re-printed, which is exactly the
    information `>Prev` needs to score 0. Skipping it reaches back two
    months and compares October against August. So this reports against
    _prev_cell, and csv_prev is left as the dedupe-aware view it was built
    to be rather than being promoted to the authority.
    """
    out = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        ccy = sm.LABEL[iso]
        live = ds._prev_cell(cat, ccy, name)
        if live is None or _norm(prev) == _norm(live):
            continue
        # ROWS.prev vs the column that actually scores. Both scores come
        # from the SAME definition of previous, so a difference here is a
        # stale literal and nothing else.
        out.append((ccy, name, prev, live,
                    ds.prev_score(act, prev, thr),
                    ds.prev_score(act, live, thr), thr))
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