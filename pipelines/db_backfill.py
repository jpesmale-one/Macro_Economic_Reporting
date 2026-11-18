# -*- coding: utf-8 -*-
"""Load every calendar capture on disk into the observations table.

*** WHAT THIS BUYS. Three months of vintage history become queryable. The
captures already hold it - 43 snapshots back to 29 August - but as whole
files, so the only way to ask "what did we expect before this print landed"
was to open each one in turn and hope the row was still in that window.
That is the F-187 mechanism, and it is a storage shape problem, not a data
problem.

*** THE CAPTURE TIMESTAMP IS THE VINTAGE, AND IT COMES FROM THE FILENAME.
2026-11-06_1557PHT_cal_full.json was read at 15:57 PHT on 6 Nov. That is
the only record of when we saw those values - the rows themselves carry no
such field - so the filename is load-bearing and a capture that cannot be
parsed is REFUSED rather than guessed at.

*** IDEMPOTENT. Re-running loads nothing new: the primary key is
(iso, event, event_date, captured_at) and every row from a given capture
carries that capture's timestamp. So this can be run after every capture
without special-casing, which is what makes it safe to automate later.

    python pipelines/db_backfill.py              # dry run, reports only
    python pipelines/db_backfill.py --write      # build/load data/macro.db
    python pipelines/db_backfill.py --write --db some/other.db
"""
import io
import os
import re
import sys
import json
import glob
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import week_ahead as wa
import score_model as sm

CAPS = os.path.join(REPO, 'data/raw/calendar/*_cal_full.json')
SCHEMA = os.path.join(REPO, 'db/schema.sql')
DEFAULT_DB = os.path.join(REPO, 'data/macro.db')

CCY = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}

# 2026-11-06_1557PHT_cal_full.json -> 2026-11-06T15:57+08:00
STAMP = re.compile(r'(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})PHT')


def vintage(path):
    """The moment this capture was taken, as sortable ISO text, or None."""
    m = STAMP.search(os.path.basename(path))
    if not m:
        return None
    return '%sT%s:%s+08:00' % (m.group(1), m.group(2), m.group(3))


def names_by_ccy():
    out = {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        out.setdefault(CCY[iso], []).append(name)
    return out


def rows_from(path, names):
    """Capture rows -> observation tuples. Returns (rows, skipped)."""
    cap = vintage(path)
    if cap is None:
        return None, 'unparseable timestamp'
    try:
        raw = json.load(io.open(path, encoding='utf-8'))
    except Exception as e:
        return None, 'unreadable: %s' % e
    rows = raw if isinstance(raw, list) else raw.get('events', [])
    if not rows:
        # *** AN EMPTY CAPTURE IS NOT A CAPTURE. A blocked fetch that still
        # wrote a file would otherwise land as a real vintage holding no
        # events, and every release in it would read as "no catalyst".
        return None, 'EMPTY - refused'

    base = os.path.basename(path)
    out = []
    seen = set()
    for r in rows:
        if not isinstance(r, dict):
            continue
        iso = r.get('iso')
        if iso not in CCY:
            continue
        ev = str(r.get('event') or '').strip().lower()
        date = str(r.get('date') or '')[:10]
        if not ev or len(date) != 10:
            continue
        k = (iso, ev, date)
        if k in seen:                       # a capture can repeat a row
            continue
        seen.add(k)
        hit = wa.match(ev, names.get(CCY[iso], []), iso)

        def val(key):
            # F-73: '' means we saw no value. Store null, never a zero.
            s = str(r.get(key) or '').strip()
            return s or None

        out.append((
            cap, base, str(r.get('source') or 'tradingeconomics'),
            iso, ev, date, str(r.get('time') or '') or None,
            hit,
            val('actual'), val('consensus'), val('forecast'), val('previous'),
            str(r.get('source_url') or '') or None,
            str(r.get('importance') or '') or None,
        ))
    return out, None


def main():
    a = sys.argv[1:]
    write = '--write' in a
    db = a[a.index('--db') + 1] if '--db' in a else DEFAULT_DB

    caps = sorted(glob.glob(CAPS))
    print('CAPTURE BACKFILL')
    print('  captures on disk: %d' % len(caps))
    print('  target: %s' % (db if write else '(dry run)'))
    print()

    names = names_by_ccy()
    allrows = []
    refused = []
    for p in caps:
        rows, err = rows_from(p, names)
        if err:
            refused.append((os.path.basename(p), err))
            print('  REFUSED %-34s %s' % (os.path.basename(p)[:34], err))
            continue
        allrows.extend(rows)

    print()
    print('  rows parsed: %d from %d captures'
          % (len(allrows), len(caps) - len(refused)))
    if refused:
        print('  captures refused: %d' % len(refused))

    matched = sum(1 for r in allrows if r[7])
    withact = sum(1 for r in allrows if r[8])
    withexp = sum(1 for r in allrows if r[9] or r[10])
    print('  matched to a whitelist indicator: %d (%d%%)'
          % (matched, 100 * matched // max(len(allrows), 1)))
    print('  carrying an actual:      %d' % withact)
    print('  carrying an expectation: %d' % withexp)

    if not write:
        print()
        print('  DRY RUN - pass --write to load.')
        return 0

    d = os.path.dirname(db)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    con = sqlite3.connect(db)
    con.executescript(io.open(SCHEMA, encoding='utf-8').read())
    before = con.execute('select count(*) from observations').fetchone()[0]
    con.executemany(
        'insert or ignore into observations ('
        'captured_at, capture_file, source, iso, event, event_date,'
        'event_time, indicator, actual, consensus, forecast, previous,'
        'source_url, importance) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        allrows)
    con.commit()
    after = con.execute('select count(*) from observations').fetchone()[0]
    print()
    print('  rows in table: %d (was %d, +%d)' % (after, before, after - before))
    vints = con.execute(
        'select count(distinct captured_at) from observations').fetchone()[0]
    span = con.execute(
        'select min(event_date), max(event_date) from observations').fetchone()
    print('  distinct vintages: %d' % vints)
    print('  event dates: %s .. %s' % span)
    con.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
