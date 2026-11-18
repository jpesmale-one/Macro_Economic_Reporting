# -*- coding: utf-8 -*-
"""Temporal queries over the observations archive.

*** THIS MODULE IS THE POINT OF THE DATABASE.

Everything here is a question the file-based pipeline could not ask, because
each capture is a snapshot and load_inflation() reads one. These read across
all 43 vintages at once.

    python pipelines/db_query.py history JP "Inflation Rate YoY" 2026-10-22
    python pipelines/db_query.py expect  JP "Inflation Rate YoY" 2026-10-22
    python pipelines/db_query.py asof    2026-10-20
"""
import os
import sys
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DB = os.environ.get('MACRO_DB') or os.path.join(REPO, 'data/macro.db')


def con(db=None):
    return sqlite3.connect(db or DB)


def history(iso, indicator, event_date, db=None):
    """Every sighting of one print, oldest first. The revision trail."""
    c = con(db)
    try:
        return c.execute("""
            select captured_at, actual, consensus, forecast, previous,
                   source, capture_file
              from observations
             where iso=? and indicator=? and event_date=?
             order by captured_at""",
            (iso, indicator, event_date)).fetchall()
    finally:
        c.close()


def expectation(iso, indicator, event_date, db=None):
    """(consensus, forecast) as held when the print landed, or (None, None).

    *** THE CUTOFF IS THE FIRST SIGHTING THAT CARRIES AN ACTUAL, NOT MIDNIGHT
    ON THE PRINT DATE. This was got wrong once and the error is instructive.
    NZ's Q3 CPI was dated 2026-10-21; the consensus 3.8% first appeared in the
    capture taken 2026-10-21 14:03, hours before the release. A cutoff of
    "before the event date" discarded it and fell back to a stale 3.7%
    forecast, which scores GOOD where the true answer is BAD.
    An expectation is an expectation for exactly as long as the row has no
    actual. That is the definition, and it is what this implements.

    Consensus is returned alongside forecast, not merged: LD-155 makes
    consensus supersede forecast, and that precedence belongs to the scorer
    (inflation_decision), not to this lookup.
    """
    c = con(db)
    try:
        first = c.execute("""
            select min(captured_at) from observations
             where iso=? and indicator=? and event_date=?
               and actual is not null
            """, (iso, indicator, event_date)).fetchone()[0]
        q = """select consensus, forecast from observations
                where iso=? and indicator=? and event_date=?
                  and (consensus is not null or forecast is not null)"""
        args = [iso, indicator, event_date]
        if first:
            q += ' and captured_at <= ?'
            args.append(first)
        q += ' order by captured_at desc limit 1'
        r = c.execute(q, args).fetchone()
        return r if r else (None, None)
    finally:
        c.close()          # Windows will not delete an open sqlite file


def as_of(moment, db=None):
    """Every indicator's latest known value as of a moment - F-183b's question.

    Rebuilding a published edition must use what we knew THEN. This is the
    query that makes that mechanical instead of a matter of finding the right
    capture file.
    """
    c = con(db)
    try:
        return c.execute("""
        select o.iso, o.indicator, o.event_date, o.actual,
               o.consensus, o.forecast, o.captured_at
          from observations o
          join (select iso, indicator, event_date, max(captured_at) mc
                  from observations
                 where captured_at <= ? and indicator is not null
                 group by iso, indicator, event_date) m
            on o.iso=m.iso and o.indicator=m.indicator
           and o.event_date=m.event_date and o.captured_at=m.mc
         where o.actual is not null
         order by o.iso, o.event_date""", (moment,)).fetchall()
    finally:
        c.close()


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 1
    cmd = a[0]
    if cmd == 'history' and len(a) >= 4:
        rows = history(a[1], a[2], a[3])
        print('%-26s %-8s %-9s %-9s %-8s %s'
              % ('captured_at', 'actual', 'consensus', 'forecast', 'prev',
                 'capture'))
        for r in rows:
            print('%-26s %-8s %-9s %-9s %-8s %s'
                  % (r[0], r[1] or '-', r[2] or '-', r[3] or '-',
                     r[4] or '-', r[6][:22]))
        print()
        print('%d sighting(s)' % len(rows))
    elif cmd == 'expect' and len(a) >= 4:
        cons, fc = expectation(a[1], a[2], a[3])
        print('consensus=%r  forecast=%r' % (cons, fc))
    elif cmd == 'asof' and len(a) >= 2:
        rows = as_of(a[1] if 'T' in a[1] else a[1] + 'T23:59+08:00')
        print('%d indicator value(s) known as of %s' % (len(rows), a[1]))
        for r in rows[:40]:
            print('  %-3s %-32s %s  act=%-8s (seen %s)'
                  % (r[0], r[1][:32], r[2], r[3], r[6][:16]))
        if len(rows) > 40:
            print('  ... %d more' % (len(rows) - 40))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
