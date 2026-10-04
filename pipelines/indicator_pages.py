# -*- coding: utf-8 -*-
"""R-45 - VERIFY EVERY WHITELIST ROW AGAINST ITS TE INDICATOR PAGE.

Jeff, 2026-09-14: "I've caught so many stale data in the report. Do I need to
validate each item or you can help me pinpoint stale items in our macro
economic data?"

No. He should not have to, and until now he did - because every guard in this
repo verifies against the CALENDAR CAPTURE, and the calendar is a rolling
window that holds roughly a month. Measured on 2026-09-14:

    VERIFIED   30 of 70 rows   a captured print matched
    NO EVENT   36 of 70 rows   never appeared in any capture at all

Per currency the gap is worse than the total suggests - USD rests on 10
unverifiable rows out of 12, GBP 7 of 8. Those rows were typed in from a TE
country page at some point and NOTHING HAS CHECKED THEM SINCE.

    R-40/R-41 ANSWER "IS THIS ROW STALE AGAINST WHAT WE CAPTURED?"
    THIS ANSWERS "IS THIS ROW STALE AGAINST WHAT TE PUBLISHES?"

THE SOURCE IS DIFFERENT, AND THAT IS THE POINT. TE's per-indicator pages
(e.g. /united-states/retail-sales-annual) carry a release history table -
release date, reference month, actual, previous, consensus - that the calendar
does not keep. That is how F-121's three GBP rows were recovered by hand. This
module does that sweep for every row instead of one at a time.

WHAT IT COMPARES. Value AND reference month, the F-123 lesson: US CPI printed
Aug/26 at 3.4% while we held Jul/26 at 3.4%, and every value-only check called
that fresh. A repeated number is not freshness.

WHAT IT WILL NOT DO. It does not write to the fact tables. A slug that
resolves to the wrong series would silently rewrite good data with a
plausible-looking number, and that failure is undetectable from inside the
repo (F-37 and F-119 are the same lesson from both ends). It reports, with
the URL it read and the exact row text, and Jeff or I apply the change.

    python pipelines/indicator_pages.py            # sweep every row
    python pipelines/indicator_pages.py USD GBP    # only these currencies
    python pipelines/indicator_pages.py --stale    # only rows that disagree
"""
import io
import os
import datetime as dt
import re
import sys
import time
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import score_model as sm

CACHE = os.path.join(REPO, 'data/raw/indicators')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120 Safari/537.36')

COUNTRY = {'USD': 'united-states', 'EUR': 'euro-area', 'GBP': 'united-kingdom',
           'JPY': 'japan', 'AUD': 'australia', 'NZD': 'new-zealand',
           'CAD': 'canada', 'CHF': 'switzerland'}

MONTHS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
          'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

# TE's URL slug rarely equals our row name. These are the ones that differ,
# each confirmed by reading the page and checking the series it returns.
# A row absent here falls back to a slug derived from its name.
SLUG = {
    'Inflation Rate YoY': 'inflation-cpi',
    'Inflation Rate YoY Final': 'inflation-cpi',
    'Retail Sales YoY': 'retail-sales-annual',
    'Retail Sales Ex Fuel YoY': 'retail-sales-ex-fuel',
    'Electronic Retail Card Spending YoY': 'retail-sales-annual',
    'Industrial Production YoY': 'industrial-production',
    'Manufacturing Production YoY': 'manufacturing-production',
    'Industrial Production YoY Final': 'industrial-production',
    # F-132: the YoY series has its own page; /machinery-orders is MoM.
    'Machinery Orders YoY': 'machinery-orders-yoy',
    'Machine Tool Orders YoY': 'machine-tool-orders',
    'Non Farm Payrolls': 'non-farm-payrolls',
    'Unemployment Rate': 'unemployment-rate',
    'Employment Change': 'employment-change',
    'Claimant Count Change': 'claimant-count-change',
    'Balance of Trade': 'balance-of-trade',
    'Building Permits MoM': 'building-permits',
    'Building Permits MoM Final': 'building-permits',
    'Building Permits YoY Final': 'building-permits',
    'CB Consumer Confidence': 'consumer-confidence',
    'GfK Consumer Confidence': 'consumer-confidence',
    'Consumer Confidence': 'consumer-confidence',
    'NAB Business Confidence': 'business-confidence',
    'Business NZ PMI': 'manufacturing-pmi',
    'Personal Spending MoM': 'personal-spending',
    'Household Spending YoY': 'household-spending',
    'Durable Goods Ex Transp MoM': 'durable-goods-orders-ex-transportation',
    'ANZ-Indeed Job Ads MoM': 'job-advertisements',
    # Probed and confirmed to return a release table, 2026-09-21.
    'ANZ Business Confidence': 'business-confidence',
    'ANZ Roy Morgan Consumer Conf': 'consumer-confidence',
    'Westpac Consumer Conf Change': 'consumer-confidence',
    'S&P Global Mfg PMI Final': 'manufacturing-pmi',
}


def slug(name):
    if name in SLUG:
        return SLUG[name]
    s = name.lower()
    s = re.sub(r'\b(yoy|mom|qoq|final|prel|change)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def fetch(ccy, name, refresh=False):
    """The indicator page text, cached on disk (provenance, LD-3)."""
    sl = slug(name)
    url = 'https://tradingeconomics.com/%s/%s' % (COUNTRY[ccy], sl)
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    path = os.path.join(CACHE, '%s_%s.html' % (ccy, sl))
    if refresh or not os.path.exists(path):
        subprocess.run(['curl', '-sL', '--max-time', '45', '-A', UA,
                        url, '-o', path], check=False)
        time.sleep(0.4)          # be a decent client
    try:
        h = io.open(path, encoding='utf-8', errors='replace').read()
    except Exception:
        return url, None
    if len(h) < 2000:
        return url, None
    t = re.sub(r'<script.*?</script>', ' ', h, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return url, re.sub(r'\s+', ' ', t)


ROW = re.compile(
    r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}\s*(?:AM|PM))\s+'
    r'(.+?)\s+(' + '|'.join(MONTHS) + r')\s+'
    r'([^\s]+)\s+([^\s]+)', re.I)


def releases(text):
    """[(date, series, month, actual, previous)] from the Calendar table."""
    if not text:
        return []
    i = text.find('Calendar GMT Reference')
    if i < 0:
        return []
    seg = text[i:i + 1200]
    out = []
    for m in ROW.finditer(seg):
        d, tm, series, mon, act, prev = m.groups()
        out.append((d, tm, series.strip(), mon.lower()[:3], act, prev))
    return out


def latest(text, name, today=None):
    """The newest release on the page whose series matches `name`.

    *** ONLY RELEASES THAT HAVE ACTUALLY HAPPENED. The first run of this
    module reported 10 of 12 USD rows stale, citing release dates of
    2026-09-18, 2026-10-02 and 2026-10-06 - all in the FUTURE. TE pre-fills
    the Actual column of a scheduled row with its own forecast, so a
    forward row looks exactly like a printed one.

        A FORECAST IN THE ACTUAL COLUMN IS NOT A RELEASE.

    That is LD-3 restated: the calendar (and the indicator page's forward
    rows) are a SCHEDULE authority, never a VALUE authority for something
    that has not happened. Filtering on release date <= today is the whole
    fix, and without it this guard would have rewritten eight correct rows
    with TE's forecasts.
    """
    # *** COMPARE TIMESTAMPS, NOT DATES. The first fix filtered on
    # release DATE <= today, and at 01:00 PHT on 14 Sep that still admitted
    # JPY Industrial Production (12:30 PHT) and CAD CPI (20:30 PHT) - both
    # hours away, both reported as proof our rows were stale. The page
    # carries a GMT time; LD-115 says read it as UTC and convert. A release
    # is a release only once its moment has passed.
    import datetime as _dt
    import phtime as _pt
    now = _dt.datetime.now(_pt.PHT)
    # *** FINAL IS PART OF THE SERIES IDENTITY, NOT NOISE (F-37).
    # Stripping it made "Inflation Rate YoY Final" match the FLASH print and
    # "Industrial Production YoY Final" match the PREL - both newer, both a
    # DIFFERENT SERIES, and both reported as our row being stale. A revision
    # series and its first estimate are not interchangeable; that is exactly
    # the confusion F-37 blocked in the calendar matcher, reappearing here
    # because this module wrote its own matching.
    want = set(re.sub(r'[^a-z0-9 ]', ' ', name.lower()).split())
    want -= {'the', 'of', 'rate', 'index'}
    is_final = 'final' in want
    # *** F-132 - THE TRANSFORM IS PART OF THE SERIES, LIKE 'Final' IS.
    # 'Retail Sales Ex Fuel YoY' matched the MoM row on the same page and
    # 'Machinery Orders YoY' matched Machinery Orders MoM. Both were then
    # reported as UNIT - a harmless presentation difference - when the value
    # belonged to a DIFFERENT SERIES. Exactly F-37 and the Final/Prel fix,
    # one axis over.
    xform = ({'yoy'} & want) or ({'mom'} & want) or ({'qoq'} & want)
    best = None
    for d, tm, series, mon, act, prev in releases(text):
        got = set(re.sub(r'[^a-z0-9 ]', ' ', series.lower()).split())
        # A FINAL row is satisfied only by a Final print, and a non-final row
        # is never satisfied by one.
        if is_final != ('final' in got):
            continue
        if xform:
            other = {'yoy', 'mom', 'qoq'} - xform
            if (xform & got) != xform or (other & got):
                continue
        if not is_final and ('prel' in got or 'flash' in got):
            continue
        if not want or len(want & got) < max(1, len(want) - 1):
            continue
        if act in ('-', ''):          # scheduled, not yet printed
            continue
        when = _pt.te_pht(d, tm)      # the page's GMT cell is UTC (LD-115)
        if when is None or when > now:
            continue                  # a FORECAST, not a release
        if best is None or d > best[0]:
            best = (d, mon, act, prev, series)
    return best


def sweep(only=None, refresh=False):
    """[(ccy, row, held, held_ref, page, verdict)] for every whitelist row."""
    out = []
    for cat, iso, name, act, prev, ref, thr, v in sm.ROWS:
        ccy = sm.LABEL[iso]
        if name == 'GDP Growth Rate QoQ':
            continue
        if only and ccy not in only:
            continue
        url, text = fetch(ccy, name, refresh)
        hit = latest(text, name)
        if hit is None:
            out.append((ccy, name, act, ref, url, None, 'NO PAGE'))
            continue
        d, mon, pact, pprev, series = hit
        # *** A PARSE THAT YIELDS NONSENSE IS NOT A FINDING. Two rows came
        # back with actual='2026' and previous='Capital'/'Job' - the regex
        # matching stray page text on indicator pages that carry no standard
        # release table. Reporting those as data disagreements would train
        # Jeff to skim the section that matters. Unreadable is NO PAGE.
        if sm._num(pact) is None or re.match(r'^(19|20)\d\d$', str(pact)):
            out.append((ccy, name, act, ref, url, None, 'NO PAGE'))
            continue
        ours = MONTHS.get(str(ref).strip().lower()[:3])
        theirs = MONTHS.get(mon)
        same_val = sm._num(act) is not None and sm._num(pact) is not None \
            and abs(sm._num(act) - sm._num(pact)) < 1e-9
        if ours and theirs and theirs > ours:
            verdict = 'STALE'
        elif not same_val:
            # *** F-132b - 'SAME MONTH, DIFFERENT NUMBER' IS NOT A UNIT
            # DIFFERENCE WHEN BOTH SIDES ARE PLAIN PERCENTAGES. USD Retail
            # Sales YoY held 5% while the page said 6% for the same August,
            # and it was filed under UNIT - the bucket the report tells Jeff
            # to ignore. UNIT exists for a genuine transform mismatch (MoM %
            # vs a level in millions); two percentages that disagree are a
            # wrong value.
            _pct = ('%' in str(act)) and ('%' in str(pact))
            verdict = ('DIFFERS' if _pct
                       else ('UNIT' if (ours and theirs and ours == theirs)
                             else 'DIFFERS'))
        else:
            verdict = 'OK'
        out.append((ccy, name, act, ref, url,
                    (d, mon, pact, pprev, series), verdict))
    return out


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    only = set(a.upper() for a in args) or None
    refresh = '--refresh' in sys.argv
    rows = sweep(only, refresh)

    bad = [r for r in rows if r[6] in ('STALE', 'DIFFERS')]
    unit = [r for r in rows if r[6] == 'UNIT']
    none = [r for r in rows if r[6] == 'NO PAGE']
    ok = [r for r in rows if r[6] == 'OK']

    print('R-45 INDICATOR-PAGE SWEEP   %d rows' % len(rows))
    print('  OK       held value and vintage match the page : %d' % len(ok))
    print('  STALE    the page has a LATER reference month  : %d'
          % len([r for r in rows if r[6] == 'STALE']))
    print('  DIFFERS  same month, different value           : %d'
          % len([r for r in rows if r[6] == 'DIFFERS']))
    print('  UNIT     vintage current, page uses another unit: %d' % len(unit))
    print('  NO PAGE  slug did not resolve - check by hand  : %d' % len(none))
    print()

    if bad:
        print('=' * 78)
        print('*** ROWS TO FIX')
        print('=' * 78)
        for ccy, name, held, ref, url, page, verdict in bad:
            d, mon, pact, pprev, series = page
            print('  %-4s %-32s %s' % (ccy, name[:32], verdict))
            print('        we hold  %-12s %s' % (held, ref))
            print('        TE says  %-12s %s/26   prev %s   released %s'
                  % (pact, mon.title(), pprev, d))
            print('        %s' % url)
        print()

    if unit and '--stale' not in sys.argv:
        print('UNIT - vintage is CURRENT; the page just leads with another')
        print('  transform of the same series. No action unless you disagree.')
        for ccy, name, held, ref, url, page, verdict in unit:
            print('  %-4s %-30s we hold %-11s page %s'
                  % (ccy, name[:30], held, page[2]))
        print()

    # *** F-133 - "NO PAGE" WAS REPORTED AS A DEAD END WHEN MOST OF THOSE
    # ROWS ARE VERIFIABLE FROM THE CAPTURE. 21 rows had no indicator page,
    # and the report told Jeff to "check by hand" - but 15 of them are
    # matched by R-40/R-41 against a captured print. Reporting 49 of 70
    # verified, when the true figure across both sources is 64 of 70,
    # overstates the blind spot and buries the SIX rows that really have
    # no check at all.
    try:
        import coverage_check as _cc
        _ver, _st, _fmt, _noev, _unm = _cc.scan()
        # *** F-143 - "VERIFIED AGAINST A CAPTURED PRINT" WAS NOT A CHECK.
        #
        # Jeff, 2026-10-04: "PMIs are not updated. example AUD S&P Global Mfg
        # PMI Final 52.0" - and then "Do I need to check the data again 1 by
        # 1?"
        #
        # AUD's PMI printed 49.6 on 30 Sep. This block reported it as VERIFIED
        # because it matched a captured event - the AUGUST print, from a 1 SEP
        # CAPTURE. A capture reaches ~26 days, so matching an OLD print proves
        # only that the row was right a month ago.
        #
        # F-133 added this block to stop overstating the blind spot. It then
        # understated it, which is worse: a row nobody checked was listed under
        # a heading that says "they are not unchecked". That is how a stale
        # value survives three staleness checks and gets caught by the reader.
        #
        # A CAPTURE MATCH ONLY COUNTS IF THE CAPTURE IS RECENT ENOUGH TO HAVE
        # SEEN THE LATEST PRINT. Anything older is reported as what it is -
        # unverified - and the number next to TRUE COVERAGE shrinks to match.
        _FRESH_DAYS = 21
        _cut = (dt.date.today() - dt.timedelta(days=_FRESH_DAYS)).isoformat()
        _cap = set((c, n) for c, n, cat, a, act, ds, ev in _ver + _fmt
                   if (ds or '') >= _cut)
        _old = sorted(set((c, n) for c, n, cat, a, act, ds, ev in _ver + _fmt
                          if (ds or '') < _cut))
        _both = [r for r in none if (r[0], r[1]) in _cap]
        _dark = [r for r in none if (r[0], r[1]) not in _cap]
        if _both:
            print('NO INDICATOR PAGE, BUT VERIFIED AGAINST A CAPTURED PRINT')
            print('  (R-40/R-41 cover these - they are not unchecked)')
            for ccy, name, held, ref, url, page, verdict in sorted(_both):
                print('  %-4s %-34s held %s' % (ccy, name[:34], held))
            print()
        if _old:
            print('CAPTURE MATCH TOO OLD TO COUNT (>%d days) - NOT VERIFIED'
                  % _FRESH_DAYS)
            print('  (F-143: matching a month-old print proves nothing about'
                  ' the latest one)')
            for c, n in _old:
                print('  %-4s %s' % (c, n[:40]))
            print()
        none = _dark
        print('  TRUE COVERAGE: %d of %d rows checked by one source or the'
              ' other.' % (len(ok) + len(unit) + len(_both), len(rows)))
        print()
    except Exception as _e:
        print('  (capture cross-check unavailable: %s)' % _e)

    if none and '--stale' not in sys.argv:
        print('NO PAGE AND NO CAPTURED PRINT - genuinely unchecked.')
        print('  These need a SLUG entry in indicator_pages.py, or a hand check.')
        for ccy, name, held, ref, url, page, verdict in none:
            print('  %-4s %-32s %s' % (ccy, name[:32], url))
        print()

    if bad:
        print('*** %d ROW(S) DISAGREE WITH TE.' % len(bad))
        if '--raise' in sys.argv:
            sys.exit(1)
    elif not none:
        print('  every row matches its indicator page')
