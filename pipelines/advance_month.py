"""Advance the fact tables one release: land TE's newer print, keep the old.

    python pipelines/advance_month.py            # DRY RUN - prints, writes nothing
    python pipelines/advance_month.py --write    # writes the six CSVs

*** WHY THIS IS A SCRIPT AND NOT A HAND EDIT.

Thirty-six cells across six files, each move touching TWO columns, with the
`>Prev` rule reading one of them. Done by hand that is thirty-six chances to
transpose a sign, and the result is unreviewable - a diff shows what changed
but not whether the rule that picked it was applied consistently. This runs
the same sweep the build check runs, applies one stated rule, and prints the
score consequence of every cell BEFORE anything is written.

*** THE RULE, STATED ONCE.

    Oct-26  <-  whatever Nov-26 currently holds   (the held print, preserved)
    Nov-26  <-  TE's newer print                  (the advance)

and ONLY for rows indicator_pages.sweep() calls STALE - "the page has a LATER
reference month". A row TE agrees with is left exactly as it is. The sweep
already enforces every identity rule that matters: Final vs Prel (F-37),
yoy/mom/qoq (F-132), and a release whose timestamp has not passed (LD-115),
so a forecast sitting in TE's Actual column can never be read as a print.

*** WHY THE PRIOR COLUMN HAS TO BE FILLED, NOT JUST THE NEW ONE.

A third of the board - 26 of 78 cells - is scored `>Prev`, and score_row
reads `previous` from score_model.ROWS, a hand-maintained third copy that
on 2026-11-20 agreed with NEITHER the fact table's prior column NOR TE on
23 of 26 rows. Jeff's rule: previous comes from OUR OWN table, whatever
populated it. That could not be applied, because Nov-26 and Oct-26 held
the SAME value on 19 of 26 rows - rows that had never been advanced - so
switching would have scored 19 rows as 0 against themselves.

This is what makes the prior column real. After it, 3 of 26 are self-equal,
and all three are genuine flat prints (CHF unemployment 3% -> 3%) that
correctly score 0.

*** THE EMPLOYMENT LEGS TRAVEL WITH THE HEADLINE (F-195, LD-151).

AUD and CAD Employment Change are graded on three legs, and the cell carries
them inline: '-43.5K (FT -2.9K, PT -40.6K)'. A headline written without its
legs would leave employment_grade() returning None and the row ungraded - so
for those two rows the new cell is assembled from indicator_pages.legs(),
which reads the page's COMPONENTS table, and the headline identity
(actual == FT + PT) is asserted before the cell is built. If the legs cannot
be read, THE ROW IS SKIPPED rather than written headline-only: scoring
Employment Change off the headline alone is the F-145 defect.

*** WHAT THIS DOES NOT DO.

It does not score, rank, select, or publish. It moves values and prints what
the board would become. LD-97: the weekly is the decision.
"""
import io
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import score_model as sm
import fact_tables as ft
import derive_scores as ds
import indicator_pages as ip

# The two rows whose cell must carry its FT/PT legs (LD-151).
LEGGED = {('AUD', 'Employment Change'), ('CAD', 'Employment Change')}


def plan(months=None):
    """[(cat, ccy, indicator, held, new, te_ref, te_date)] for STALE rows."""
    ms = months or ft.months()
    cur = ms[-1]
    out = []
    skipped = []
    rows = ip.sweep(None, False)          # newest landed vintage, no refetch
    hit = {}
    for ccy, name, held, ref, url, h, verdict in rows:
        hit[(ccy, name)] = (held, ref, h, verdict)
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        ccy = sm.LABEL[iso]
        k = (ccy, name)
        if k not in hit:
            continue
        held, hr, h, verdict = hit[k]
        if verdict != 'STALE' or not h:
            continue
        d, mon, pact, pprev, series = h
        new = pact
        if k in LEGGED:
            # *** THE LEGS OR NOTHING (F-145/F-195). A headline-only cell
            # leaves the row ungraded; writing one would look like progress
            # and silently remove the row from the board.
            url2, text = ip.fetch(ccy, name, False)
            hl, f, p, lref = ip.legs(text)
            if hl is None:
                skipped.append((cat, ccy, name, 'legs unreadable'))
                continue
            if abs(hl - (f + p)) > 0.15:
                skipped.append((cat, ccy, name,
                                'headline != FT+PT (%.1f vs %.1f)'
                                % (hl, f + p)))
                continue
            if abs(hl - (sm._num(pact) or 0)) > 0.15:
                # the components table is a LATER vintage than the calendar
                # (F-195); if they disagree the two tables are describing
                # different prints and the pair must not be mixed.
                skipped.append((cat, ccy, name,
                                'calendar %s != components %.1f'
                                % (pact, hl)))
                continue
            new = '%gK (FT %+gK, PT %+gK)' % (hl, f, p)
        out.append((cat, ccy, name, held, new, mon, d))
    return out, skipped, cur


def apply(rows, cur, prior, write=False):
    """Write the advance. Returns {cat: n_cells_changed}."""
    byfile = {}
    for cat, ccy, name, held, new, mon, d in rows:
        byfile.setdefault(cat, {})[(ccy, name)] = new
    touched = {}
    for cat, moves in sorted(byfile.items()):
        path = ft._path(cat)
        # *** PRESERVE THE FILE'S OWN LINE ENDINGS.
        # The first run wrote '\n' into files that hold '\r\n', so git showed
        # all 150 lines modified for 36 changed cells. The values were right
        # and the diff was unreadable - which is worse than it sounds: a
        # review that cannot see the change cannot catch a wrong one. Sniff
        # the ending from the bytes already on disk rather than assuming.
        raw = io.open(path, 'rb').read()
        nl = '\r\n' if raw.count(b'\r\n') else '\n'
        with io.open(path, encoding='utf-8') as fh:
            rd = csv.DictReader(fh)
            cols = list(rd.fieldnames)
            data = list(rd)
        n = 0
        for r in data:
            k = (r['Currency'].strip(), r['Indicator'].strip())
            if k not in moves:
                continue
            r[prior] = r.get(cur, '')      # preserve the held print
            r[cur] = moves[k]              # land the newer one
            n += 1
        touched[cat] = n
        if write:
            # newline='' stops Python translating again on top of
            # lineterminator, which would double every CR on Windows
            fh = io.open(path, 'w', encoding='utf-8', newline='')
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator=nl)
            w.writeheader()
            for r in data:
                w.writerow(r)
            fh.close()
    return touched


def board(rows, cur, prior):
    """(before, after) board totals, scored through the REAL path."""
    before = ft.base_scores(cur)
    NEW = dict(((c, y, n), v) for c, y, n, h, v, m, d in rows)
    real = ft.load

    def patched(cat):
        out = []
        for r in real(cat):
            y, n = r['Currency'].strip(), r['Indicator'].strip()
            if (cat, y, n) in NEW:
                r = dict(r)
                r[prior] = r.get(cur, '')
                r[cur] = NEW[(cat, y, n)]
            out.append(r)
        return out

    ft.load = patched
    try:
        after = ft.base_scores(cur)
    finally:
        ft.load = real
    return before, after


def main():
    write = '--write' in sys.argv
    ms = ft.months()
    cur, prior = ms[-1], ms[-2]
    rows, skipped, _ = plan(ms)

    print('ADVANCE  %s <- %s   (%s <- TE)' % (prior, cur, cur))
    print('=' * 100)
    print('%-11s %-4s %-30s %-11s %-11s %-5s %-5s %s' % (
        'CAT', 'CCY', 'INDICATOR', 'HELD', 'NEW', 'OLD', 'NEW', 'NOTE'))
    print('-' * 100)
    moves = []
    for cat, ccy, name, held, new, mon, d in rows:
        a = ds.score_row(cat, ccy, name, held)
        b = ds.score_row(cat, ccy, name, new)
        note = ''
        if a != b:
            note = 'MOVES %s->%s' % (a, b)
            if a is not None and b is not None and a * b < 0:
                note = 'SIGN FLIP %s->%s' % (a, b)
            moves.append((cat, ccy, name, a, b))
        print('%-11s %-4s %-30s %-11s %-11s %-5s %-5s %s' % (
            cat, ccy, name[:30], str(held)[:11], str(new)[:11], a, b, note))
    print()
    for cat, ccy, name, why in skipped:
        print('SKIPPED %-4s %-30s %s' % (ccy, name[:30], why))
    print('rows advanced: %d   score changes: %d   skipped: %d' % (
        len(rows), len(moves), len(skipped)))
    print()

    before, after = board(rows, cur, prior)
    rb = sorted(before, key=lambda c: -before[c]['total'])
    ra = sorted(after, key=lambda c: -after[c]['total'])
    print('%-4s %-9s %-9s %-8s %s' % ('CCY', 'BEFORE', 'AFTER', 'DELTA',
                                      'RANK'))
    print('-' * 46)
    for ccy in ft.CCYS:
        bt, at = before[ccy]['total'], after[ccy]['total']
        print('%-4s %+9.2f %+9.2f %+8.2f  %d -> %d' % (
            ccy, bt, at, at - bt, rb.index(ccy) + 1, ra.index(ccy) + 1))
    print()

    if not write:
        print('DRY RUN - nothing written. Re-run with --write to apply.')
        return 0
    touched = apply(rows, cur, prior, write=True)
    print('WRITTEN:')
    for cat in sorted(touched):
        print('   %-14s %d cells' % (cat, touched[cat]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
