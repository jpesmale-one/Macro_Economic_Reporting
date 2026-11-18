# -*- coding: utf-8 -*-
"""Regression tests for the observations archive.

These assert the properties the table exists to provide, against REAL
history rather than fixtures. Run after any backfill or schema change:

    python pipelines/test_db.py
"""
import os
import sys
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import db_query as q
import derive_scores as ds

DB = os.path.join(REPO, 'data/macro.db')
fails = []


def check(name, ok, detail=''):
    print('  %-4s %-54s %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok:
        fails.append(name)


def main():
    if not os.path.exists(DB):
        print('no database - run db_backfill.py --write first')
        return 1
    con = sqlite3.connect(DB)
    print('OBSERVATIONS ARCHIVE TESTS')
    print()

    n = con.execute('select count(*) from observations').fetchone()[0]
    v = con.execute('select count(distinct captured_at) '
                    'from observations').fetchone()[0]
    check('archive is populated', n > 10000 and v >= 40,
          '%d rows, %d vintages' % (n, v))

    # *** F-73 - AN ABSENCE MUST BE NULL, NEVER A ZERO OR AN EMPTY STRING.
    bad = con.execute("""select count(*) from observations
                          where actual='' or consensus='' or forecast=''
                             or previous=''""").fetchone()[0]
    check('F-73: no empty-string values (null means absent)', bad == 0,
          '%d offending row(s)' % bad)

    # Append-only: a given (iso, event, event_date) may appear many times,
    # but never twice with the SAME captured_at. The primary key enforces it;
    # this proves the key is doing its job on real data.
    dup = con.execute("""select count(*) from (
                           select iso, event, event_date, captured_at
                             from observations
                            group by 1,2,3,4 having count(*) > 1)""").fetchone()[0]
    check('append-only: no duplicate sightings', dup == 0,
          '%d duplicate(s)' % dup)

    # Provenance is mandatory - LD-3 needs to know a calendar value from an
    # agency value, and F-183b needs the capture a figure came from.
    nop = con.execute("""select count(*) from observations
                          where source is null or source=''
                             or capture_file is null or capture_file=''
                       """).fetchone()[0]
    check('every row carries source and capture_file', nop == 0,
          '%d without provenance' % nop)

    # *** THE DEFECT CLASS THIS TABLE RETIRES. All four F-187/F-187b
    # corrections must reproduce from the archive alone. CHF is the strongest
    # of them: it originally needed an agency PDF read by hand because no
    # single capture held both the expectation and the actual.
    print()
    print('  F-187 corrections, derived from the archive:')
    cases = [('JP', 'Inflation Rate YoY', '2026-10-22', '2.1%', -1),
             ('NZ', 'Inflation Rate YoY', '2026-10-21', '3.7%', -1),
             ('CA', 'Inflation Rate YoY', '2026-10-19', '3.1%', -1),
             ('CH', 'Inflation Rate YoY', '2026-11-03', '1.5%', 1)]
    for iso, ind, date, act, want in cases:
        cons, fc = q.expectation(iso, ind, date, DB)
        sc, _s, _w = ds.inflation_decision(consensus=cons, forecast=fc,
                                           actual=act)
        check('%s %s -> %s' % (iso, date,
                               {1: 'GOOD', 0: 'NEUTRAL', -1: 'BAD'}.get(want)),
              sc == want,
              'cons=%s fc=%s got=%s' % (cons or '-', fc or '-', sc))

    # *** THE CUTOFF RULE, AND A TEST THAT ACTUALLY BITES.
    #
    # First attempt at this test deleted the single sighting that first
    # carried NZ's consensus (2026-10-21 14:03) and asserted the score
    # changed. It did not - the 22 Oct sighting carries the actual AND the
    # consensus together, so it satisfies "captured_at <= first_actual" on
    # its own. The rule is more robust than the test assumed, and a test
    # that cannot fail proves nothing.
    #
    # What DOES bite is reproducing the original F-187 condition: keep only
    # a late vintage, as reading one capture gave us. Then no expectation
    # survives, the level test takes over, and NZD scores GOOD (+1) instead
    # of BAD - the published bug, exactly.
    cons, fc = q.expectation('NZ', 'Inflation Rate YoY', '2026-10-21', DB)
    check('consensus recovered across vintages (LD-155)', cons == '3.8%',
          'consensus=%r' % cons)

    import tempfile
    import shutil
    tmp = os.path.join(tempfile.gettempdir(), 'macro_bite_test.db')
    try:
        shutil.copyfile(DB, tmp)
        t = sqlite3.connect(tmp)
        t.execute("""delete from observations
                      where iso='NZ' and indicator='Inflation Rate YoY'
                        and event_date='2026-10-21'
                        and captured_at < '2026-10-25'""")
        t.commit()
        t.close()
        c2, f2 = q.expectation('NZ', 'Inflation Rate YoY', '2026-10-21', tmp)
        s2, _a, _b = ds.inflation_decision(consensus=c2, forecast=f2,
                                           actual='3.7%')
        check('archive is load-bearing (single-vintage reverts to the bug)',
              s2 != -1,
              'stripped to one vintage -> score %s (the F-187 bug)' % s2)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    # The temporal rebuild F-183b needs.
    rows = q.as_of('2026-10-20T23:59+08:00', DB)
    isos = len(set(r[0] for r in rows))
    check('as-of rebuild covers all eight currencies', isos == 8,
          '%d values across %d currencies' % (len(rows), isos))

    # *** THE AS-OF COUNT MUST EQUAL THE NUMBER OF GROUPS HOLDING AN ACTUAL.
    # An invariant, not a magic number, because the first SQLite version
    # returned 93 against Postgres's 87: the primary key includes `event`,
    # so several source events can map to ONE whitelist indicator at the
    # same captured_at (AU Employment Change matched three variants), and a
    # join on max(captured_at) returned those groups more than once.
    # Only running BOTH engines exposed it - either one alone looked right.
    groups = con.execute(
        "select count(*) from ("
        " select iso, indicator, event_date from observations"
        "  where captured_at <= '2026-10-20T23:59+08:00'"
        "    and indicator is not null and actual is not null"
        "  group by 1,2,3)").fetchone()[0]
    check('as-of returns exactly one row per group', len(rows) == groups,
          '%d rows vs %d groups' % (len(rows), groups))

    print()
    if fails:
        print('*** %d FAILURE(S): %s' % (len(fails), ', '.join(fails)))
        return 1
    print('ALL TESTS PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
