# -*- coding: utf-8 -*-
"""Build a calendar capture that includes EVERY whitelisted currency (F-57).

WHY THIS EXISTS. Jeff, 2026-08-27: "CHF NFP is going to be out today, why is
it not in our radar 4.0"

Because the capture contained NO SWISS ROWS AT ALL - not "no payrolls row", no
Switzerland whatsoever. 22 countries were in it and CH was not one of them.
Neither was NZ. Both are legs of locked pairs: we run short CHF via EURCHF and
long NZD via AUDNZD.

TE's GLOBAL calendar page does not carry them. TE's COUNTRY pages do. So this
fetches the global page for breadth AND each missing country page for
completeness, then merges.

R-20 (week_ahead.coverage_gaps) fails loud when a whitelisted currency has zero
rows. This is the tool that fixes what R-20 reports.

USAGE
    python pipelines/capture_calendar.py            # capture, print summary
    python pipelines/capture_calendar.py --write    # ... and save the JSON

SCHEMA (F-65): date / time / iso / event / actual / previous /
consensus / forecast. The four value columns were present in TE's HTML
from the start and simply never parsed - section 4.0 showed '- / -' on
every row for days as a result.
"""
import io, os, re, sys, json, subprocess, datetime as dt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, 'data', 'raw', 'calendar')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')
TAG = re.compile(r'<[^>]+>')
VAL_FIELDS = ('actual', 'previous', 'consensus', 'forecast')

# TE country pages for currencies the global calendar omits or under-reports.
# Add a country here the moment R-20 names it.
# F-67. Every whitelisted currency gets its COUNTRY page, not just the two
# the global page omitted entirely.
#
# The global page spans only ~10 days. The country pages span a MONTH. That
# asymmetry is why 33 of 71 whitelist rows "matched nothing" on 2026-08-30:
# they were not unmatchable, they simply release LATER IN THE MONTH than the
# global page reaches. CAD had 4 distinct dates; CH and NZ, which already had
# country pages, had 10 and 13.
#
# Jeff, 2026-08-30: "please please make sure we capture the data completely
# in TE".
COUNTRY_PAGES = {
    'CH': 'https://tradingeconomics.com/switzerland/calendar',
    'NZ': 'https://tradingeconomics.com/new-zealand/calendar',
    'US': 'https://tradingeconomics.com/united-states/calendar',
    'GB': 'https://tradingeconomics.com/united-kingdom/calendar',
    'JP': 'https://tradingeconomics.com/japan/calendar',
    'AU': 'https://tradingeconomics.com/australia/calendar',
    'CA': 'https://tradingeconomics.com/canada/calendar',
    'EA': 'https://tradingeconomics.com/euro-area/calendar',
}
GLOBAL_PAGE = 'https://tradingeconomics.com/calendar'

MONTHS = {m: i + 1 for i, m in enumerate(
    ['January', 'February', 'March', 'April', 'May', 'June', 'July',
     'August', 'September', 'October', 'November', 'December'])}


def txt(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.S | re.I)
    s = TAG.sub(' ', s)
    for a, b in (('&nbsp;', ' '), ('&amp;', '&'), ('&#39;', "'"),
                 ('&quot;', '"')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()


def fetch(url, cache):
    """Fetch a page, keeping the raw HTML alongside the capture (LD provenance)."""
    subprocess.run(['curl', '-sL', '--max-time', '45', '-A', UA,
                    '-H', 'Referer: https://tradingeconomics.com/',
                    url, '-o', cache], check=False)
    if not os.path.exists(cache) or os.path.getsize(cache) < 5000:
        return None
    return io.open(cache, encoding='utf-8', errors='replace').read()


def iso_date(heading):
    """'Thursday August 27 2026' -> '2026-08-27'."""
    if not heading:
        return None
    m = re.search(r'([A-Z][a-z]+)\s+(\d{1,2})\s+(\d{4})', heading)
    if not m or m.group(1) not in MONTHS:
        return None
    return '%04d-%02d-%02d' % (int(m.group(3)), MONTHS[m.group(1)],
                               int(m.group(2)))


def clean_val(v):
    """A TE value cell -> a bare figure, or '' if the cell is empty.

    TE writes '49.2', '-0.3%', '1.433M', 'A$1.93B' and sometimes a bare '-'
    for 'no value'. A literal '-' must become '' or it reads downstream as a
    minus sign with no digits (F-65).
    """
    v = (v or '').strip()
    if v in ('', '-', '\u2013', '\u2014', 'N/A'):
        return ''
    return v


def parse(html, force_iso=None):
    """Rows from a TE calendar page. force_iso for country pages, whose rows
    carry no country column."""
    out, cur = [], None
    # Split on the OUTER row only. Each TE calendar row contains a NESTED
    # <table><tr> holding the country flag and ISO code, so splitting on every
    # '<tr' cut the row in half: the time <td> was orphaned in one chunk
    # (len(tds) == 1, discarded by the filter below) and the event cells landed
    # in the next. That is why the first run parsed 0 times from a page
    # containing 407. The outer rows are the ones carrying data-event.
    for chunk in re.split(r'<tr(?=[^>]*data-event)', html):
        dm = re.search(r'<th[^>]*>(.*?)</th>', chunk, re.S | re.I)
        if dm:
            d = iso_date(txt(dm.group(1)))
            if d:
                cur = d
        # F-72. THE ROW CARRIES ITS OWN DATE - use it, never the running
        # <th> heading. Jeff, 2026-08-31: "How TE is wrong when I can see
        # the screen August 31, 2026 9AM?"
        #
        # He was right and I had blamed TE. Each date heading appears TWICE
        # on a country page, so the running `cur` advanced a day before the
        # rows beneath it were read, and NZ ANZ Business Confidence landed on
        # 1 Sep when its own cell says class=' 2026-08-31'.
        #
        # I then "proved" TE wrong from capture history (F-71) and re-dated a
        # row that was never mis-dated at TE. THE TELL I WALKED PAST: three
        # other rows on the same screen converted cleanly at UTC+8 and only
        # this one was off by a whole day. When one row disagrees and its
        # neighbours agree, suspect the parser, not the source.
        rowm = re.search(r"class='\s*(\d{4}-\d{2}-\d{2})'", chunk)
        row_date = rowm.group(1) if rowm else None

        iso = force_iso
        if not iso:
            im = re.search(r'calendar-iso"?>([A-Z]{2,3})', chunk)
            if im:
                iso = im.group(1)
        if not iso or not cur:
            continue
        tds_raw = re.findall(r'<td\b([^>]*)>(.*?)</td>', chunk,
                              re.S | re.I)
        tds = [b for _a, b in tds_raw]
        if len(tds) < 3:
            continue
        cells = [txt(t) for t in tds]
        # The time sits inside <span class="calendar-date-N"> in the FIRST
        # cell, so the cell text is not JUST a time - it may carry whitespace
        # and sibling markup. Searching rather than full-matching is the fix;
        # full-matching returned zero times across 491 rows.
        time = ''
        for c in cells[:3]:
            m = re.search(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM)?)\b', c, re.I)
            if m:
                time = m.group(1).strip()
                break
        ev, ev_i = '', None
        for i, c in enumerate(cells[:4]):
            if len(c) > 4 and not re.fullmatch(r'[\d:.\sAPM%,-]*', c):
                ev, ev_i = c, i
                break
        # F-65/F-65b. The four value columns are the <td> cells carrying
        # class="calendar-item ...", in TE's header order:
        #     Actual | Previous | Consensus | Forecast
        # THE FIRST ONE IS OFTEN EMPTY AND THAT IS THE POINT - an unreleased
        # event has a BLANK Actual. The first cut of this dropped leading
        # blanks and shifted every column one left, so Previous was read as
        # Actual and every unreleased event gained a print it never had.
        # That is F-1 manufactured by our own parser. Never strip a blank
        # here; map positionally and let the empty cell mean 'not released'.
        vals = {'actual': '', 'previous': '', 'consensus': '', 'forecast': ''}
        vcells = [b for a, b in tds_raw if 'calendar-item' in a
                  and 'calendar-iso' not in a and '<table' not in b.lower()]
        for k, v in zip(VAL_FIELDS, vcells):
            vals[k] = clean_val(txt(v))
        if ev:
            r = {'date': row_date or cur, 'time': time, 'iso': iso,
                 'event': ev.lower()}
            r.update(vals)
            out.append(r)
    return out


def capture(write=False):
    stamp = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    tag = stamp.strftime('%Y-%m-%d_%H%MPHT')
    rows, seen = [], {}

    sources = [('GLOBAL', GLOBAL_PAGE, None)]
    sources += [(iso, url, iso) for iso, url in sorted(COUNTRY_PAGES.items())]

    for name, url, force in sources:
        cache = os.path.join(OUT_DIR, '%s_cal_%s.html' % (tag, name.lower()))
        html = fetch(url, cache)
        if html is None:
            print('  %-8s FETCH FAILED - %s' % (name, url))
            continue
        got = parse(html, force_iso=force)
        added = 0
        for r in got:
            k = (r['date'], r['iso'], r['event'])
            if k in seen:
                # F-65. A country page often carries values the global page
                # leaves blank. Keep the RICHER row rather than the first one.
                prev = seen[k]
                if sum(1 for f in VAL_FIELDS if r.get(f)) > \
                   sum(1 for f in VAL_FIELDS if prev.get(f)):
                    prev.update({f: r[f] for f in VAL_FIELDS if r.get(f)})
                continue
            seen[k] = r
            rows.append(r)
            added += 1
        print('  %-8s %4d rows parsed, %4d new' % (name, len(got), added))

    rows.sort(key=lambda r: (r['date'], r['time'] or 'zz', r['iso']))

    # ---- the check this tool exists for ----
    sys.path.insert(0, os.path.join(REPO, 'pipelines'))
    import score_model as sm
    from week_ahead import CCY
    want = set(sm.LABEL[r[1]] for r in sm.ROWS)
    have = set(CCY.get(r['iso']) for r in rows) - {None}
    gaps = sorted(want - have)

    print()
    print('  TOTAL %d rows, %d countries'
          % (len(rows), len(set(r['iso'] for r in rows))))
    for c in sorted(want):
        n = len([r for r in rows if CCY.get(r['iso']) == c])
        print('    %-4s %4d rows %s' % (c, n, '*** ZERO ***' if n == 0 else ''))
    print()
    if gaps:
        print('  *** COVERAGE GAP REMAINS: %s ***' % ', '.join(gaps))
    else:
        print('  COVERAGE COMPLETE - every whitelisted currency has rows.')

    if write:
        path = os.path.join(OUT_DIR, '%s_cal_full.json' % tag)
        io.open(path, 'w', encoding='utf-8').write(
            json.dumps(rows, ensure_ascii=False, indent=1))
        print()
        print('  written %s' % os.path.basename(path))
    return rows, gaps


if __name__ == '__main__':
    print('CALENDAR CAPTURE (F-57) - global page + country pages')
    print('=' * 66)
    capture(write='--write' in sys.argv)
