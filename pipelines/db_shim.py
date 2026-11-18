# -*- coding: utf-8 -*-
"""Serve capture-shaped data from the observations table.

*** THE MIGRATION PROBLEM THIS SOLVES. 27 modules read
data/raw/calendar/*_cal_full.json directly. Rewriting them all against SQL
would be a large, risky change to code that currently works, and every one
of those readers carries rules paid for in published errors (F-37, F-49,
F-95, F-186, F-187).

So nothing is rewritten. The four read functions all accept an INJECTABLE
SOURCE - a capture path, or a list of them:

    derive_scores.load_inflation(capture=...)
    derive_scores.load_landed_inflation(archive=[...])
    rate_model.load_scheduled(capture=...)
    daily_review.releases_by_day()            # globs internally

This module materialises those files FROM THE DATABASE. The consumers keep
their signatures, their parsing and their guards; only where the bytes come
from changes.

*** WHY MATERIALISE RATHER THAN RETURN OBJECTS. The functions parse JSON
from disk, and the parsing is part of what is being preserved. Handing them
a file they read exactly as before means the shim cannot change behaviour by
accident - the strongest form of "the migration did not alter the numbers",
which is the property we have to prove.

    python pipelines/db_shim.py                 # materialise, report
    python pipelines/db_shim.py --as-of 2026-10-20
"""
import io
import os
import sys
import json
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import db_connect as dbc

ISO = ('US', 'EA', 'GB', 'JP', 'AU', 'NZ', 'CA', 'CH')

# Columns in the order a capture row carries them.
COLS = ('iso', 'event', 'event_date', 'event_time',
        'actual', 'consensus', 'forecast', 'previous',
        'source', 'source_url', 'importance')


def _rows(where='', args=()):
    """Capture-shaped dicts from the archive, newest vintage order."""
    con, eng = dbc.connect()
    ph = '?' if eng == 'sqlite' else '%s'
    sql = ('select captured_at, iso, event, event_date, event_time,'
           ' actual, consensus, forecast, previous, source, source_url,'
           ' importance from observations')
    if where:
        sql += ' where ' + where.replace('?', ph)
    sql += ' order by captured_at, iso, event_date, event'
    try:
        cur = con.cursor()
        cur.execute(sql, args)
        return cur.fetchall()
    finally:
        con.close()


def _as_capture(rows):
    """Database rows -> the list-of-dicts a _cal_full.json holds.

    *** F-73 TRAVELS THROUGH THIS BOUNDARY. The database stores null for
    "we did not see it"; captures carry ''. The conversion must go
    null -> '' and NEVER null -> '0', so an absence stays an absence on the
    far side.
    """
    out = []
    for r in rows:
        (_cap, iso, event, edate, etime, actual, cons, fcst, prev,
         source, surl, imp) = r
        out.append({
            'iso': iso,
            'event': event,
            'date': str(edate)[:10],
            'time': etime or '',
            'actual': actual or '',
            'consensus': cons or '',
            'forecast': fcst or '',
            'previous': prev or '',
            'source': source or '',
            'source_url': surl or '',
            'importance': imp or '',
        })
    return out


def vintages(db=None):
    """Every captured_at in the archive, oldest first."""
    con, eng = dbc.connect()
    try:
        cur = con.cursor()
        cur.execute('select distinct captured_at from observations'
                    ' order by captured_at')
        return [str(r[0]) for r in cur.fetchall()]
    finally:
        con.close()


def materialise(outdir=None, as_of=None):
    """Write one JSON file per vintage. Returns [paths], oldest first.

    as_of trims the archive to what was known at a moment - F-183b's rule,
    so a rebuild of a published edition cannot silently use later data.
    """
    outdir = outdir or os.path.join(tempfile.gettempdir(), 'macro_shim')
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)

    vs = vintages()
    if as_of:
        vs = [v for v in vs if v <= as_of]

    paths = []
    for v in vs:
        rows = _rows('captured_at = ?', (v,))
        if not rows:
            continue
        # The filename carries the vintage, because several consumers parse
        # it out of the basename (F-183b pins an edition by capture name).
        stamp = str(v)[:10] + '_' + str(v)[11:16].replace(':', '') + 'PHT'
        p = os.path.join(outdir, '%s_cal_full.json' % stamp)
        io.open(p, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(_as_capture(rows), ensure_ascii=False, indent=1))
        paths.append(p)
    return paths


def main():
    a = sys.argv[1:]
    as_of = a[a.index('--as-of') + 1] if '--as-of' in a else None
    out = a[a.index('--out') + 1] if '--out' in a else None

    print('DB SHIM - materialising captures from the archive')
    print('  engine : %s' % ('postgres' if dbc.is_pg() else 'sqlite'))
    if as_of:
        print('  as of  : %s' % as_of)
    paths = materialise(out, as_of)
    print('  vintages written: %d' % len(paths))
    if paths:
        print('  oldest : %s' % os.path.basename(paths[0]))
        print('  newest : %s' % os.path.basename(paths[-1]))
        n = sum(len(json.load(io.open(p, encoding='utf-8'))) for p in paths)
        print('  rows   : %d' % n)
        print('  dir    : %s' % os.path.dirname(paths[0]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
