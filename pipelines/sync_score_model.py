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
}


def ref_drift():
    """[(iso, indicator, old_ref, new_ref)] where the vintage moved."""
    out = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        want = REFS.get((iso, name))
        if want and want != (ref or '').strip():
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
    if not d and not rd:
        print('  in step - nothing to do')
        sys.exit(0)
    n = rewrite(dry)
    print()
    print('  %s %d field(s)' % ('WOULD REWRITE' if dry else '*** REWROTE', n))
    if dry:
        print('  re-run with --write to apply')
    sys.exit(0 if n == len(d) + len(ref_drift()) or not dry else 1)
