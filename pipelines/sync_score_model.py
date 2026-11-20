# -*- coding: utf-8 -*-
"""F-141 - score_model.ROWS IS A SECOND COPY OF THE ACTUALS, AND IT DRIFTS.

The board reads the CSVs (fact_tables, which F-88 introduced precisely to
replace this literal). But THIRTY modules still import score_model, and every
data guard - R-37, R-40, R-41, R-45 - reads ROWS, not the CSVs.

So on 2026-10-04, after rolling 18 refreshed prints into Oct-26:

    fact_tables      EUR +4.00   <- the new data, board moved
    score_model.ROWS EUR +6.00   <- the old literal, guards still reading it

R-45 reported the SAME 13 stale rows after the refresh as before it, because
it was auditing the copy nobody had updated. A guard reading a stale mirror
does not fail quietly - it reports a problem that has already been fixed, and
the next person re-fixes it.

score_model.py says of itself: "The ROWS table is replaced each edition."
NOTHING ENFORCES THAT. It is a manual step with no guard, which is the exact
shape of F-127 (two selectors) and F-134 (page behind the data).

*** WHY THIS SYNCS INSTEAD OF DERIVING. The CSVs carry Currency, Indicator and
the month columns. They do NOT carry `prev`, `ref` or `threshold`, which exist
only in the literal - so ROWS cannot simply be generated from them today.
Rewriting the fact tables to carry all six fields is the right fix and it is a
LOGIC change to the scoring source, which the 2026-10-03 freeze defers to the
31 Oct review. Until then this copies the ACTUAL across, leaves the rule
columns alone, and makes the drift impossible to miss.

    python pipelines/sync_score_model.py --dry
    python pipelines/sync_score_model.py --write
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fact_tables as ft
import score_model as sm
import refresh_rows as rr
import derive_scores as ds

SRC = os.path.join(HERE, 'score_model.py')
ISO = dict((v, k) for k, v in sm.LABEL.items())


def current():
    """{(iso, indicator): actual} from the CSVs' latest month."""
    m = ft.latest_month()
    out = {}
    for cat in ('Production', 'Spending', 'Trade', 'Employment', 'Inflation'):
        for r in ft.load(cat):
            ccy = (r.get('Currency') or '').strip()
            ind = (r.get('Indicator') or '').strip()
            val = (r.get(m) or '').strip()
            if ccy in ISO and ind and val:
                out[(ISO[ccy], ind)] = val
    return out


# F-141b - THE REF MONTH IS PART OF THE ROW, AND SYNCING ONLY THE VALUE
# LEAVES A LIE BEHIND. After the first pass USD Personal Spending read
# "0.9%" against ref "Jul/26" - the August number wearing July's label.
# R-45 compares VINTAGE as well as value (that is F-123's whole point), so a
# value-only sync still reports STALE and the row is now worse than before:
# internally inconsistent instead of merely old.
REFS = {
    ('US', 'Non Farm Payrolls'): 'Sep/26',
    ('US', 'Unemployment Rate'): 'Sep/26',
    ('US', 'Personal Spending MoM'): 'Aug/26',
    ('EA', 'Unemployment Rate'): 'Aug/26',
    ('EA', 'Consumer Confidence Final'): 'Sep/26',
    ('EA', 'S&P Global Mfg PMI Final'): 'Sep/26',
    ('JP', 'Unemployment Rate'): 'Aug/26',
    ('JP', 'Retail Sales YoY'): 'Aug/26',
    ('JP', 'S&P Global Mfg PMI Final'): 'Sep/26',
    ('AU', 'Inflation Rate YoY'): 'Aug/26',
    ('AU', 'Household Spending YoY'): 'Aug/26',
    ('AU', 'Balance of Trade'): 'Aug/26',
    ('CH', 'Inflation Rate YoY'): 'Sep/26',
    ('CH', 'Retail Sales YoY'): 'Aug/26',
    ('CH', 'Procure.ch-UBS Mfg PMI'): 'Sep/26',
    ('CA', 'S&P Global Mfg PMI'): 'Sep/26',
    ('NZ', 'ANZ Business Confidence'): 'Sep/26',
    ('NZ', 'ANZ Roy Morgan Consumer Conf'): 'Sep/26',
    ('US', 'ISM Manufacturing PMI'): 'Sep/26',
    ('GB', 'S&P Global Mfg PMI Final'): 'Sep/26',
    # 2026-10-11 build: prints that landed 5-9 Oct
    ('CA', 'Employment Change'): 'Sep/26',
    ('CA', 'Unemployment Rate'): 'Sep/26',
    ('CA', 'Balance of Trade'): 'Aug/26',
    ('US', 'Balance of Trade'): 'Aug/26',
    ('EA', 'Retail Sales YoY'): 'Aug/26',
    ('JP', 'Machine Tool Orders YoY'): 'Sep/26',
    ('JP', 'Household Spending YoY'): 'Aug/26',
    ('JP', 'Consumer Confidence'): 'Sep/26',
    ('CH', 'Consumer Confidence'): 'Sep/26',
    ('CH', 'Unemployment Rate'): 'Sep/26',
    ('AU', 'ANZ-Indeed Job Ads MoM'): 'Sep/26',
    ('AU', 'Building Permits YoY Final'): 'Aug/26',
    ('AU', 'Westpac Consumer Conf Change'): 'Oct/26',
    ('AU', 'S&P Global Mfg PMI Final'): 'Sep/26',
    # *** F-152 - THE EIGHT INFLATION ROWS HAD NO VINTAGE ENTRY AT ALL, so
    # ref_drift() reported "in step" on rows it had never been shown. A guard
    # that only checks the rows it is handed cannot report a missing row, and
    # Inflation is the ONE category where the vintage is load-bearing: EUR and
    # AUD name a FINAL/revision series whose flash prints WEEKS EARLIER at a
    # different number (F-29/F-37), so "which print is this" is not cosmetic.
    #
    # Jeff, 2026-10-11, on EUR reading 3.2% Aug/26: "WE already have a forecast
    # for the September Inflation can you check?"
    #
    # He was right that the forecast exists - 3.8% consensus for Fri 16 Oct,
    # the largest expected move on the board. It IS scored, in the calibrator,
    # BEFORE-the-news (+1 from consensus). The Aug/26 vintage is also CORRECT:
    # the August FINAL released 17 Sep at 3.2% and is our cell; the 3.8% is the
    # September FLASH (2 Oct), a different series F-37 deliberately excludes;
    # the September FINAL lands 16 Oct and has not printed. Verified at
    # Eurostat, not off the calendar (LD-3).
    #
    # SO NOTHING WAS MIS-SCORED - but nothing was CHECKING either, and the
    # fact table's own columns cannot settle it: roll_month copies a
    # non-printing series forward, so EUR's Sep-26 and Oct-26 columns BOTH
    # hold 3.2%, the August number. The build month is not the reference
    # month, and `ref` is the only field that records which print it is.
    ('US', 'Inflation Rate YoY'):       'Aug/26',  # Sep CPI rel 14 Oct
    ('EA', 'Inflation Rate YoY Final'): 'Aug/26',  # Aug FINAL rel 17 Sep
    ('GB', 'Inflation Rate YoY'):       'Aug/26',  # Sep CPI rel 21 Oct
    ('JP', 'Inflation Rate YoY'):       'Aug/26',  # Sep CPI rel 22 Oct
    ('AU', 'Inflation Rate YoY'):       'Aug/26',  # Sep CPI rel 28 Oct
    ('NZ', 'Inflation Rate YoY'):       'Jun/26 (Q)',  # Q3 rel 21 Oct
    ('CA', 'Inflation Rate YoY'):       'Aug/26',  # Sep CPI rel 19 Oct
    ('CH', 'Inflation Rate YoY'):       'Sep/26',  # Sep CPI rel 1 Oct
    # ---- 2026-10-18 build: the 15 rows R-45 found stale --------------------
    # *** AND THE GUARD REPORTED 0 REF DRIFT UNTIL THESE WERE ADDED, which is
    # F-152's blind spot repeating on a new set of rows: ref_drift() iterates
    # the rows REFS hands it, so a row with no entry is SKIPPED, not reported.
    # All fifteen vintages were stale (Jul/26 or Aug/26 against TE's Aug/26 or
    # Sep/26) and a value-only sync would have left every one of them
    # internally inconsistent - the September number wearing August's label,
    # which is the exact defect F-141b was written for.
    ('US', 'Industrial Production YoY'):       'Sep/26',
    ('US', 'Manufacturing Production YoY'):    'Sep/26',
    ('EA', 'Industrial Production YoY'):       'Aug/26',
    ('GB', 'Industrial Production YoY'):       'Aug/26',
    ('GB', 'Manufacturing Production YoY'):    'Aug/26',
    ('JP', 'Industrial Production YoY Final'): 'Aug/26',
    ('JP', 'Machinery Orders YoY'):            'Aug/26',
    ('US', 'Retail Sales YoY'):                'Sep/26',
    ('AU', 'NAB Business Confidence'):         'Sep/26',
    ('EA', 'Balance of Trade'):                'Aug/26',
    ('GB', 'Balance of Trade'):                'Aug/26',
    ('AU', 'Employment Change'):               'Sep/26',
    ('AU', 'Unemployment Rate'):               'Sep/26',
    ('US', 'Inflation Rate YoY'):              'Sep/26',
    ('EA', 'Inflation Rate YoY Final'):        'Sep/26',
    ('NZ', 'Business NZ PMI'):                     'Sep/26',
    ('NZ', 'Electronic Retail Card Spending YoY'): 'Sep/26',
    ('CA', 'Building Permits MoM'):                'Aug/26',
    ('US', 'CB Consumer Confidence'):            'Sep/26',
    # ---- 2026-11-01 build: vintages for the 2-6 Nov window ----------------
    # *** F-178 AGAIN, IN REFS THIS TIME. The 2026-10-18 block corrected US
    # and EA inflation to Sep/26 but left GB, JP, AU, NZ and CA behind in the
    # F-152 block above - and because a LATER duplicate key wins, the stale
    # Aug/26 entries were the ones in force. sync --dry then proposed moving
    # score_model BACKWARDS (Sep/26 -> Aug/26) on four rows whose values had
    # not changed at all. The CSV was right, score_model was right, and REFS
    # was the stale copy proposing to corrupt both.
    # Verified against the TE indicator pages before landing (LD-3 owns the
    # value, and R-45 passes these rows on Sep/26).
    ('GB', 'Inflation Rate YoY'):       'Sep/26',  # Sep CPI rel 21 Oct
    ('JP', 'Inflation Rate YoY'):       'Sep/26',  # Sep CPI rel 22 Oct
    ('AU', 'Inflation Rate YoY'):       'Sep/26',  # Sep CPI rel 28 Oct, 4.3%
    ('CA', 'Inflation Rate YoY'):       'Sep/26',  # Sep CPI rel 19 Oct
    ('NZ', 'Inflation Rate YoY'):       'Sep/26 (Q)',  # Q3 rel 21 Oct

    # the nine rows that re-printed 26-30 Oct
    ('US', 'Durable Goods Ex Transp MoM'): 'Sep/26',  # rel 27 Oct
    ('US', 'Personal Spending MoM'):       'Sep/26',  # rel 29 Oct
    ('EA', 'Consumer Confidence Final'):   'Oct/26',  # rel 29 Oct
    ('JP', 'Consumer Confidence'):         'Oct/26',  # rel 29 Oct
    ('JP', 'Retail Sales YoY'):            'Sep/26',  # rel 29 Oct
    ('NZ', 'ANZ Business Confidence'):     'Oct/26',  # rel 29 Oct
    ('EA', 'Unemployment Rate'):           'Sep/26',  # rel 30 Oct
    ('JP', 'Unemployment Rate'):           'Sep/26',  # rel 29 Oct

    # the four R-37 raised (R-45 does not reach these)
    ('US', 'Building Permits MoM Final'):   'Sep/26',      # FINAL, rel 27 Oct
    ('US', 'CB Consumer Confidence'):       'Oct/26',      # rel 27 Oct
    ('NZ', 'ANZ Roy Morgan Consumer Conf'): 'Oct/26',

}


def unwatched(cat='Inflation'):
    """[(iso, indicator, ref)] rows of `cat` with NO entry in REFS.

    F-152 - ref_drift() iterates the rows it was HANDED, so a row absent from
    REFS is not reported as unchecked, it is simply skipped - and the guard
    prints "in step", which reads as a pass. All eight Inflation rows sat in
    that blind spot until 2026-10-11.

    Inflation is the category where this matters most: EUR and AUD name a
    FINAL/revision series whose FLASH prints weeks earlier at a materially
    different number (EUR Sep: flash 3.8% on 2 Oct, final due 16 Oct), so a
    wrong vintage silently swaps one series for another - exactly what F-29
    and F-37 exist to prevent.

    SILENCE IS NOT A PASS. This makes the gap itself a finding.
    """
    out = []
    for c, iso, name, act, prev, ref, thr, v in sm.ROWS:
        if c == cat and (iso, name) not in REFS:
            out.append((iso, name, ref))
    return out


# *** F-196 - REFS IS A SNAPSHOT, AND A SNAPSHOT DRAGS ROWS BACKWARDS.
#
# The dict above was written for the 2026-10-11 build. After the 2026-11-20
# advance it asked to move NINE ref months the WRONG WAY - Oct/26 -> Sep/26
# on rows the advance never touched (the PMI family, CHF inflation) - because
# it still described October's vintage and nothing had updated it.
#
# A ref month that moves BACKWARDS is never a sync; it is the sync being out
# of date. So TE's own reference month is the authority where we can read it
# (LD-3: the calendar is a SCHEDULE authority but the indicator page's
# released row IS the value authority for what month a print belongs to),
# and REFS is the fallback for rows TE cannot confirm.
#
# AND A BACKWARD MOVE IS REFUSED EITHER WAY. Whatever the source says, a ref
# month earlier than the one we hold is reported and skipped rather than
# applied - the one direction that cannot be a new print.
_MON3 = ('jan feb mar apr may jun jul aug sep oct nov dec').split()


def _refkey(ref):
    """('Sep/26' | 'Sep/26 (Q)') -> a sortable (year, month), or None."""
    m = re.match(r'([A-Za-z]{3})/(\d{2})', (ref or '').strip())
    if not m:
        return None
    mon = m.group(1).lower()
    if mon not in _MON3:
        return None
    return int(m.group(2)), _MON3.index(mon) + 1


def te_refs():
    """{(iso, indicator): 'Mon/YY'} from the landed TE vintages."""
    try:
        import indicator_pages as ip
    except Exception:
        return {}
    out = {}
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        if name == 'GDP Growth Rate QoQ':
            continue
        try:
            url, text = ip.fetch(sm.LABEL[iso], name, False)
            hit = ip.latest(text, name)
        except Exception:
            continue
        if not hit:
            continue
        # *** A NONSENSE PARSE IS NOT A VINTAGE (the sweep's own rule).
        # ROW needs a MONTH name, and NZD's releases are quarterly - 'Q2',
        # 'Q3' - so on that page the regex matched stray text far below the
        # table and returned actual='2026', series='Employment', month='sep'.
        # sweep() throws that away as NO PAGE; trusting the month alone had
        # this asking to move NZD Unemployment from Jun/26 (Q) to Sep/26 (Q)
        # off a parse that never saw a release row. If the ACTUAL is not a
        # number, or looks like a bare year, the whole hit is discarded.
        pact = hit[2]
        if sm._num(pact) is None or re.match(r'^(19|20)\d\d$', str(pact)):
            continue
        mon = (hit[1] or '').lower()[:3]
        if mon not in _MON3:
            continue
        # the page gives the month, not the year; take the year from the ref
        # we already hold so a December/January boundary cannot roll it wrong
        held = _refkey(ref)
        yr = held[0] if held else None
        if yr is None:
            continue
        # a month LATER than ours in the same year, else the next year only
        # if ours is December and theirs is January
        if _MON3.index(mon) + 1 < held[1] and held[1] == 12 and mon == 'jan':
            yr += 1
        out[(iso, name)] = '%s/%02d' % (mon.capitalize(), yr)
    return out


def ref_drift(use_te=True):
    """[(iso, indicator, old_ref, new_ref)] where the vintage moved FORWARD."""
    live = te_refs() if use_te else {}
    out = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        want = live.get((iso, name)) or REFS.get((iso, name))
        if not want:
            continue
        cur = (ref or '').strip()
        # a '(Q)' suffix is part of OUR label, not TE's - keep it, but only
        # where the candidate does not already carry one. REFS entries do,
        # te_refs() entries do not, and appending blindly produced the
        # nonsense 'Sep/26 (Q) (Q)'.
        if cur.endswith('(Q)') and not want.endswith('(Q)'):
            want = want + ' (Q)'
        if want == cur:
            continue
        a, b = _refkey(cur), _refkey(want)
        if a and b and b < a:
            print('  *** REFUSED backward ref move %s %s (%s -> %s)'
                  % (iso, name, cur, want))
            continue
        out.append((iso, name, ref, want))
    return out


def drift():
    """[(iso, indicator, in_rows, in_csv)] where the two disagree."""
    cur = current()
    bad = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        got = cur.get((iso, name))
        if got is not None and got != (act or '').strip():
            bad.append((iso, name, act, got))
    return bad


def verdict_drift():
    """[(iso, indicator, old_verdict, new_verdict)] where the rule disagrees.

    The DERIVED score is the authority (LD-112): the cell holds the actual
    and the rule owns the reading, so a stored verdict is a label for it,
    never a second opinion. Where they differ the label is stale.

    A row the rule cannot grade is left alone - employment_grade() and the
    others return None rather than guess (F-73), and overwriting a human's
    verdict with silence would delete information.
    """
    S2V = {1: 'GOOD', -1: 'BAD', 0: 'NEUTRAL'}
    out = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        try:
            sc = ds.score_row(cat, sm.LABEL[iso], name, act)
        except Exception:
            continue
        want = S2V.get(sc)
        if want and want != (v or '').strip():
            out.append((iso, name, v, want))
    return out


def rewrite(dry=True):
    """Replace the ACTUAL field of each ROWS line in place."""
    cur = current()
    src = io.open(SRC, encoding='utf-8').read()
    n = 0
    for iso, name, old, new in drift():
        # the literal line:  ("Cat","US","Indicator","actual","prev",...)
        pat = re.compile(
            r'(\("[A-Za-z ]+","%s","%s",")%s(")'
            % (re.escape(iso), re.escape(name), re.escape(old)))
        src, k = pat.subn(r'\g<1>%s\g<2>' % new.replace('\\', '\\\\'), src)
        if k:
            n += k
        else:
            print('  *** could not place %s %s (%s -> %s)'
                  % (iso, name, old, new))
    # F-141b - AND THE REF MONTH, in the same pass. Syncing only the value
    # leaves the row internally inconsistent: USD Personal Spending read
    # "0.9%" against ref "Jul/26" - the August number wearing July's label.
    # R-45 compares VINTAGE as well as value (F-123), so a value-only sync
    # still reports STALE and the row is now worse than before.
    for iso, name, old, new in ref_drift():
        pat = re.compile(
            r'(\("[A-Za-z ]+","' + re.escape(iso) + r'","'
            + re.escape(name) + r'","[^"]*","[^"]*",")'
            + re.escape(old) + r'(")')
        src, k = pat.subn(r'\g<1>' + new + r'\g<2>', src)
        if k:
            n += k
        else:
            print('  *** could not place REF %s %s (%s -> %s)'
                  % (iso, name, old, new))
    # *** F-196b - AND THE VERDICT, OR THE REPORT PRINTS A LABEL THAT
    # CONTRADICTS ITS OWN SCORE.
    #
    # After the 2026-11-20 advance, FIFTEEN rows carried a stored verdict
    # that disagreed with the rule - USD Non Farm Payrolls read 'BAD' beside
    # a derived +1 on a 165K print. The BOARD is safe (R-53 proves 0 rows
    # reach the verdict fallback in score_row, so nothing is scored from it),
    # but section2.py and render_edition.py PRINT this field. An edition
    # built on it would show GOOD/BAD text next to a number that says the
    # opposite, and a reader would have no way to tell which was wrong.
    #
    # Five of the fifteen were older than the advance (NZD Dairy, NZD Card
    # Spending, CAD Building Permits and the LD-155 inflation family), so
    # this was already latent. Syncing the actual without the verdict just
    # moved the inconsistency rather than introducing it.
    for iso, name, old, new in verdict_drift():
        # ("Cat","US","Indicator","actual","prev","ref","thr","VERDICT")
        pat = re.compile(
            r'(\("[A-Za-z_ ]+","' + re.escape(iso) + r'","'
            + re.escape(name) + r'",'
            + r'(?:"[^"]*",){4})"' + re.escape(old) + r'"')
        src, k = pat.subn(r'\g<1>"' + new + r'"', src)
        if k:
            n += k
        else:
            print('  *** could not place VERDICT %s %s (%s -> %s)'
                  % (iso, name, old, new))
    if not dry and n:
        io.open(SRC, 'w', encoding='utf-8', newline='\n').write(src)
    return n


if __name__ == '__main__':
    dry = '--write' not in sys.argv
    d = drift()
    print('F-141 SCORE_MODEL SYNC   latest fact-table month: %s'
          % ft.latest_month())
    print('  rows where ROWS disagrees with the CSV : %d' % len(d))
    for iso, name, old, new in d:
        print('    %-4s %-34s %-12s -> %s'
              % (sm.LABEL[iso], name[:34], old, new))
    rd = ref_drift()
    print('  rows whose REF MONTH moved             : %d' % len(rd))
    for iso, name, old, new in rd:
        print('    %-4s %-34s %-12s -> %s'
              % (sm.LABEL[iso], name[:34], old, new))
    # F-152 - report the rows NOTHING is watching, before claiming "in step".
    uw = unwatched('Inflation')
    print('  Inflation rows with no vintage watcher : %d' % len(uw))
    vd = verdict_drift()
    print('  rows whose VERDICT contradicts the rule : %d' % len(vd))
    for iso, name, have, want in vd:
        print('    %-4s %-34s %-9s -> %s'
              % (sm.LABEL[iso], name[:34], have, want))
    for iso, name, ref in uw:
        print('    *** %-4s %-34s ref=%s  UNCHECKED'
              % (sm.LABEL[iso], name[:34], ref))
    # *** THE EARLY EXIT MUST COUNT EVERY KIND OF DRIFT IT CAN FIX.
    # It tested only `d` and `rd`, so once the actuals and ref months were in
    # step it returned "nothing to rewrite" and exited BEFORE rewrite() ran -
    # with 15 contradicted verdicts still on disk, reported in the output
    # immediately above and then silently not fixed. A gate that names fewer
    # things than the writer handles turns a successful run into a no-op.
    if not d and not rd and not vd:
        print('  values, vintages and verdicts in step - nothing to rewrite')
        if uw:
            print('  *** but %d Inflation row(s) are unwatched - add them to'
                  ' REFS' % len(uw))
            sys.exit(1)
        sys.exit(0)
    n = rewrite(dry)
    print()
    print('  %s %d field(s)' % ('WOULD REWRITE' if dry else '*** REWROTE', n))
    if dry:
        print('  re-run with --write to apply')
        sys.exit(0)
    want = len(d) + len(rd) + len(vd)
    if n != want:
        print('  *** placed %d of %d - %d field(s) could not be matched'
              % (n, want, want - n))
        sys.exit(1)
    sys.exit(0)
