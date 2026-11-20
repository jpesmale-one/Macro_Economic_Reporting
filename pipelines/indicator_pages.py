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

# *** RAW IS IMMUTABLE (CLAUDE.md section 6), AND --refresh USED TO BREAK IT.
#
# The old fetch() wrote straight to data/raw/indicators/<CCY>_<slug>.html and
# --refresh overwrote it in place. That is a landed vintage being destroyed by
# the next fetch: 44 files were rewritten in one build-check run, and the only
# reason a real change was noticed (CHF Balance of Trade moving Sep -> Oct)
# was that the diffs happened to be read one by one before the restore.
#
#     AN OVERWRITE LOSES THE ONE THING RAW EXISTS TO KEEP - what the source
#     said AT A MOMENT. Without it there is no way to show a revision
#     happened, which is precisely the evidence a >Prev row is scored on.
#
# So a refresh now LANDS A NEW VINTAGE beside the old, named by the fetch
# date, and reads resolve to the newest vintage available. Nothing is ever
# rewritten. Captures already work this way (data/raw/calendar/<stamp>_...),
# and this just brings the indicator pages into line with them.
VINTAGE = os.path.join(CACHE, 'vintages')

# *** AN HONEST CLIENT, VERIFIED (2026-11-20).
#
# This used to send a spoofed Chrome User-Agent. Checked against TE today:
# robots.txt carries NO Disallow at all (just a Sitemap line), and all 36
# pages behind the stale rows return 200 with a full body to a plainly
# identified client. The spoof bought nothing and misrepresented what we are,
# so it is gone. If TE ever does refuse an honest client, that is a FINDING to
# report and a limit to respect - not a thing to disguise.
#
# The UA names the tool and carries no personal detail: no name, no email.
UA = 'macro-research-bot/1.0 (automated macro data collection; low volume)'

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


def vintages(ccy, sl):
    """Every landed vintage for one page, newest LAST. [(stamp, path)]."""
    out = []
    if os.path.isdir(VINTAGE):
        pre = '%s_%s.FETCHED-' % (ccy, sl)
        for f in os.listdir(VINTAGE):
            if f.startswith(pre) and f.endswith('.html'):
                out.append((f[len(pre):-5], os.path.join(VINTAGE, f)))
    return sorted(out)


def newest(ccy, sl):
    """The newest readable source for a page: a vintage, else the flat file.

    The flat data/raw/indicators/<CCY>_<slug>.html files are the PRE-VINTAGE
    landed copies. They are still raw and still immutable - they are read as
    the oldest vintage, never rewritten.
    """
    vs = vintages(ccy, sl)
    if vs:
        return vs[-1][1], vs[-1][0]
    flat = os.path.join(CACHE, '%s_%s.html' % (ccy, sl))
    return (flat, 'legacy') if os.path.exists(flat) else (None, None)


def fetch(ccy, name, refresh=False, stamp=None):
    """The indicator page text, read from the newest landed vintage (LD-3).

    refresh=True LANDS A NEW VINTAGE and never touches an existing file. If
    the download fails or comes back short, the new vintage is discarded and
    the previous one still answers - a failed fetch must not be able to
    destroy the good copy it was meant to replace.
    """
    sl = slug(name)
    url = 'https://tradingeconomics.com/%s/%s' % (COUNTRY[ccy], sl)
    path, vint = newest(ccy, sl)

    if refresh or path is None:
        if not os.path.isdir(VINTAGE):
            os.makedirs(VINTAGE)
        st = stamp or dt.datetime.now().strftime('%Y-%m-%d_%H%M')
        new = os.path.join(VINTAGE, '%s_%s.FETCHED-%s.html' % (ccy, sl, st))
        if os.path.exists(new):
            path, vint = new, st          # already landed this stamp
        else:
            tmp = new + '.part'
            subprocess.run(['curl', '-sL', '--max-time', '45', '-A', UA,
                            url, '-o', tmp], check=False)
            time.sleep(0.4)               # be a decent client
            good = os.path.exists(tmp) and os.path.getsize(tmp) >= 2000
            if good:
                os.rename(tmp, new)
                path, vint = new, st
            else:
                if os.path.exists(tmp):
                    os.remove(tmp)
                if path is None:
                    return url, None      # nothing to fall back to

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


# *** THE CALENDAR TABLE IS NOT THE WHOLE PAGE (F-195).
#
# Every parser in this module read ONE table - the Calendar - and I then
# reported what is not in it as absent from TE. Jeff, 2026-11-20: "I can
# see FT/PT split in TE why you can't get it?" It is on the page, in the
# SECOND table, which nothing here had ever looked at:
#
#     Related Last Previous Unit Reference
#     Employment Change          -43531.00  -36400.00  Persons  Oct 2026
#     Full Time Employment Chg    -2948.00   35398.00  Persons  Oct 2026
#     Part Time Employment Chg   -40583.00  -71797.00  Persons  Oct 2026
#
# F-73, stated as a fact about the world instead of about our reach - and
# the repo already knew better: F-145 recorded in October that TE publishes
# the CAD split. I asserted over our own finding.
#
# TWO THINGS THE CALENDAR CANNOT GIVE, BOTH LOAD-BEARING:
#   - the component SERIES (FT/PT legs, core prints, sub-indices)
#   - the REVISED value of a prior month. The Calendar keeps the number as
#     first published; this table carries the current one. AUD Sep/26 reads
#     -39.3K in the Calendar and -36.4K here, with legs revised 34.4/-73.7
#     -> 35.4/-71.8. Both are correct for what they are, so a caller MUST
#     say which it wants; silently mixing them manufactures a disagreement.
#
# 'Last' here is NOT filtered for release time the way latest() filters the
# Calendar - this table only ever carries printed values, never a forecast,
# so there is no forward row to exclude. The reference month is returned
# with every row so a caller can check vintage rather than assume it.
# The name is bounded on the LEFT by the end of the previous row (a
# reference month) or by the header, never left to run backwards into them.
# The first draft had no left anchor and produced two corrupt keys on the
# GBP page: 'Related Last Previous Unit Reference Consumer Price Index CPI'
# swallowed the header, and 'Oct 2026 GDP Deflator' swallowed the row above.
# Both looked like data and neither was a series TE publishes.
_MON = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
COMP = re.compile(
    r'(?:^|(?<=Reference)|(?<=\d{4}))\s*'
    r'([A-Z][A-Za-z0-9 /%\.\,\-]*?[A-Za-z\.])\s+'
    r'(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)\s+'
    r'((?:[A-Z]{3}[ /][A-Za-z]+|[A-Z]{3}|[A-Za-z]+(?: [A-Za-z]+)?)?)\s*'
    r'(' + _MON + r' \d{4})')


def components(text):
    """{series: (last, previous, unit, 'Mon YYYY')} from the second table.

    The component series TE publishes beside the headline. Keys are TE's own
    names, verbatim - never fuzzy-matched (LD-59), because 'Full Time
    Employment Chg' and 'Employment Change' are different series and a loose
    match would bind one to the other.

    The table is headed 'Components' on some pages and 'Related' on others,
    and SOME PAGES CARRY BOTH. Taking whichever appears FIRST is deliberate:
    searching for one and falling back to the other found 'Related' far
    down the GBP inflation page and parsed the wrong table, silently losing
    every row of the right one.
    """
    if not text:
        return {}
    heads = [text.find('%s Last Previous Unit Reference' % h)
             for h in ('Components', 'Related')]
    heads = [h for h in heads if h >= 0]
    if not heads:
        return {}
    i = min(heads)
    seg = text[i:i + 3000]
    out = {}
    for m in COMP.finditer(seg):
        name, last, prev, unit, ref = m.groups()
        name = name.strip()
        # a key that still carries the header or a month is a parse artefact,
        # not a series - drop it rather than publish a fictional name
        if re.search(r'Last Previous Unit Reference|%s \d{4}' % _MON, name):
            continue
        out[name] = (last, prev, unit.strip(), ref)
    return out


def legs(text):
    """(headline, full_time, part_time, ref) in THOUSANDS, or Nones.

    *** THE UNITS DIFFER BY COUNTRY AND THE CELL IS WRITTEN IN THOUSANDS.
    TE reports AUD in Persons (-43531.00) and CAD in Thousand (-4.70). Both
    become -43.5K and -4.7K. Reading the number without its unit is how a
    43-thousand print becomes a 43-million one.

    All three legs or nothing: employment_grade() needs the full triple and
    returns None without it (F-73), and a part-time leg derived here by
    subtraction would be an UNMARKED derived figure (F-1). Deriving it
    belongs in capture_biquote.derive_part_time(), which labels it.
    """
    c = components(text)
    want = ('Employment Change', 'Full Time Employment Chg',
            'Part Time Employment Chg')
    if not all(k in c for k in want):
        return None, None, None, None
    vals = []
    ref = None
    for k in want:
        last, _prev, unit, r = c[k]
        try:
            v = float(str(last).replace(',', ''))
        except ValueError:
            return None, None, None, None
        if 'Person' in unit:
            v = v / 1000.0
        vals.append(round(v, 1))
        ref = ref or r
        if r != ref:                  # legs from different months are not a
            return None, None, None, None   # print - they are two prints
    return vals[0], vals[1], vals[2], ref


# *** F-199 - THE FORWARD ROW MUST BE READ STRUCTURALLY, NOT BY POSITION.
#
# releases() flattens the Calendar table to text and splits on whitespace,
# which is fine for a LANDED row and unsafe for a forward one, because a
# BLANK CELL VANISHES. JPY's landed Oct row reads
#
#     2.3%  2.1%  2.0%
#
# - three values where the schema says four - because its Consensus is
# empty. Parsed by position that makes 2.0% look like the CONSENSUS when it
# is the TEForecast, and under LD-154 consensus OUTRANKS forecast, so the
# weaker number would be promoted to the stronger authority. Exactly the
# LD-59 failure one level down: the gap invents a presence.
#
# The rows ARE in the static HTML with id="actual" and id="previous"
# attributes and a fixed eight-column shape, so <td> POSITION is reliable:
#
#     date | time | event | reference | actual | previous | consensus | fcst
#
# This reads that. It never guesses a missing cell and never shifts a
# column to fill one.
CAL_TR = re.compile(r'<tr[^>]*\bdata-id=[^>]*>(.*?)</tr>', re.S)
CAL_TD = re.compile(r'<td\b[^>]*>(.*?)</td>', re.S)


def calendar_rows(html):
    """[{date,time,event,ref,actual,previous,consensus,forecast}] from RAW html.

    Takes the UNSTRIPPED html, not the text form - the whole point is the
    <td> boundaries that the text form destroys.
    """
    if not html:
        return []
    i = html.find('id="calendar"')
    if i < 0:
        return []
    body = html[i:]
    j = body.find('</table>')
    if j > 0:
        body = body[:j]
    out = []
    for tr in CAL_TR.finditer(body):
        tds = []
        for m in CAL_TD.finditer(tr.group(1)):
            txt = re.sub(r'<[^>]+>', ' ', m.group(1))
            tds.append(' '.join(txt.split()))
        if len(tds) < 7:
            continue
        tds += [''] * (8 - len(tds))
        out.append({'date': tds[0], 'time': tds[1], 'event': tds[2],
                    'ref': tds[3], 'actual': tds[4], 'previous': tds[5],
                    'consensus': tds[6], 'forecast': tds[7]})
    return out


def scheduled(html, name, today=None):
    """The NEXT unreleased row matching `name`, or None.

    Returns {date, previous, consensus, forecast, event} for the EARLIEST
    future row of OUR series that carries an expectation. None - never a
    guessed blank - when there is no such row, so a caller falls back to
    its standing reading rather than scoring off nothing (F-73).

    *** THREE REFUSALS, EACH ONE A BUG WE HAVE ALREADY HAD.
      - a row with an ACTUAL is history, not a schedule (F-186 / F-197b:
        load_scheduled filed the 5 Nov BoE decision as "next" and paid GBP
        +1 for a hike it had already made)
      - a row whose DATE HAS PASSED is not next whatever its actual says,
        because TE's window rolls forward faster than we capture (F-186)
      - a row with NEITHER consensus NOR forecast has nothing to score
    """
    import datetime as _dt
    import phtime as _pt
    now = _dt.datetime.now(_pt.PHT)
    want = set(re.sub(r'[^a-z0-9 ]', ' ', name.lower()).split())
    want -= {'the', 'of', 'rate', 'index'}
    is_final = 'final' in want
    xform = ({'yoy'} & want) or ({'mom'} & want) or ({'qoq'} & want)
    best = None
    for r in calendar_rows(html):
        if r['actual'].strip():
            continue                       # released - history owns it
        got = set(re.sub(r'[^a-z0-9 ]', ' ', r['event'].lower()).split())
        # the same identity tests latest() enforces (F-37, F-132, LD-59)
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
        if not (r['consensus'].strip() or r['forecast'].strip()):
            continue                       # nothing to score from
        when = _pt.te_pht(r['date'], r['time']) if r['time'] else None
        if when is not None and when <= now:
            continue                       # already happened
        if best is None or r['date'] < best['date']:
            best = r
    if best is None:
        return None
    return {'date': best['date'], 'previous': best['previous'] or None,
            'consensus': best['consensus'] or None,
            'forecast': best['forecast'] or None, 'event': best['event']}


def raw_html(ccy, name, refresh=False):
    """The UNSTRIPPED html for one indicator page, from the newest vintage."""
    sl = slug(name)
    if refresh:
        fetch(ccy, name, True)             # land a vintage, then read it
    path, vint = newest(ccy, sl)
    if path is None:
        return None
    try:
        return io.open(path, encoding='utf-8', errors='replace').read()
    except Exception:
        return None


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
