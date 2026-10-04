# -*- coding: utf-8 -*-
"""ROLL THE FACT TABLES INTO A NEW MONTH COLUMN.

*** ONLY THE LATEST COLUMN CAN BE SCORED (LD-112, fact_tables' own rule), so a
new column must be FULLY populated - all 78 cells - before anything grades on
it. A half-filled column silently drops every missing row out of the board.

That is the whole reason this is a script and not a hand edit. On 2026-09-20
six rows were refreshed by hand and R-45 then found six MORE that had been
missed, because "refresh what changed" and "make the column complete" are
different jobs and only the second one is safe.

THE RULE, which is fact_tables' convention and not a new one:

    A month column holds WHAT THIS EDITION COULD SEE, not "that month's data".
    So Oct-26 = every row's latest print as of the Sunday build, whatever
    reference month that print carries.

So rolling is: COPY the previous column forward, then OVERWRITE the rows that
have since printed. A row that did not re-release keeps its value and its
vintage, which is correct - it is still the latest thing known about it.

    python pipelines/roll_month.py Oct-26 --dry     # show what would change
    python pipelines/roll_month.py Oct-26 --write

Refreshed values come from refresh_rows.py, which R-45 writes; this module
only moves them into the table.
"""
import io
import os
import sys
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

DIR = os.path.join(REPO, 'data/macro_indicators')
CATS = ('Production', 'Spending', 'Trade', 'Employment', 'Inflation',
        'Interest_Rate')


def path(cat):
    return os.path.join(DIR, '%s_Macro_Indicators.csv' % cat)


def read(cat):
    with io.open(path(cat), encoding='utf-8-sig', newline='') as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(cat, cols, rows):
    with io.open(path(cat), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def roll(target, updates, dry=True):
    """Fill `target` from the column before it, then apply `updates`.

    updates: {(CCY, Indicator): 'value'}  - the rows that have re-printed.
    Returns (filled, changed, missing_updates).
    """
    filled = changed = 0
    seen = set()
    for cat in CATS:
        if not os.path.exists(path(cat)):
            continue
        cols, rows = read(cat)
        if target not in cols:
            print('  %s has no %s column' % (cat, target))
            continue
        prev = cols[cols.index(target) - 1]
        for r in rows:
            key = ((r.get('Currency') or '').strip(),
                   (r.get('Indicator') or '').strip())
            if key in updates:
                new = updates[key]
                seen.add(key)
                changed += 1
            else:
                new = (r.get(prev) or '').strip()
                filled += 1
            if not dry:
                r[target] = new
        if not dry:
            write(cat, cols, rows)
    return filled, changed, sorted(set(updates) - seen)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--write' not in sys.argv
    if not args:
        print(__doc__)
        sys.exit(2)
    target = args[0]

    try:
        import refresh_rows as rr
        updates = rr.UPDATES
    except ImportError:
        print('no refresh_rows.py - nothing to apply, would copy forward only')
        updates = {}

    filled, changed, missing = roll(target, updates, dry)
    print('%s  %s' % (target, 'DRY RUN' if dry else '*** WRITTEN'))
    print('  carried forward unchanged : %d' % filled)
    print('  refreshed from TE         : %d' % changed)
    if missing:
        print()
        print('  *** %d UPDATE(S) MATCHED NO ROW - check the exact name:'
              % len(missing))
        for k in missing:
            print('      %s %s' % k)
        sys.exit(1)
    if dry:
        print()
        print('  re-run with --write to apply')
