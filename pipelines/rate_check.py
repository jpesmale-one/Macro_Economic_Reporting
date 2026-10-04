# -*- coding: utf-8 -*-
"""R-47 - DO THE EIGHT POLICY RATES MATCH TRADING ECONOMICS?

F-142. Jeff, 2026-10-04: "no we should be showing the latest data not the
stale ones."

The RBA hiked to 4.60% on 29 Sep. rate_model held 4.35% for FIVE DAYS, through
a published edition and a published retrospective, and NOTHING IN THE BUILD
NOTICED. R-46 step 6 verifies that the PAGE matches rate_model; it has never
verified that rate_model matches the WORLD. All eight cells could drift and
every guard would stay green.

*** WHY THIS ESCAPED A REPO FULL OF GUARDS. Every data check here - R-37, R-40,
R-41, R-45 - walks score_model.ROWS or the fact-table CSVs. Rate rows live in
NEITHER. They are hand-written literals in rate_model.ROWS, and the thing that
makes them invisible to the guards is the same thing that made them invisible
to hot() in F-135 and to day_score() in LD-146. Three findings, one cause.

*** AND I DEFERRED IT ONCE. On 2026-10-04 I named the stale cell in my own
summary and left it, calling it "a data change to a sealed vintage". That was
wrong on the facts: the decision landed 29 Sep, BEFORE the Sunday 4 Oct build,
so it was always inside what the edition may see. THE VINTAGE RULE KEEPS NEXT
WEEK'S PRINTS OUT, NEVER LAST WEEK'S. Naming a defect is not fixing it.

    python pipelines/rate_check.py            # cached pages
    python pipelines/rate_check.py --refresh  # re-fetch from TE

A rate that cannot be read is reported UNVERIFIED, never assumed correct -
an absence we cannot see is a fact about our reach, not about the world
(F-73).
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import rate_model as rm

CACHE = os.path.join(REPO, 'data/raw/rates')

# iso -> the TE page that carries the policy rate and its history
SLUG = {
    'US': 'united-states/interest-rate',
    'EA': 'euro-area/interest-rate',
    'GB': 'united-kingdom/interest-rate',
    'JP': 'japan/interest-rate',
    'AU': 'australia/interest-rate',
    'NZ': 'new-zealand/interest-rate',
    'CA': 'canada/interest-rate',
    'CH': 'switzerland/interest-rate',
}

LABEL = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
         'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}


def url(iso):
    return 'https://tradingeconomics.com/%s' % SLUG[iso]


def cached(iso):
    p = os.path.join(CACHE, '%s.txt' % iso)
    if not os.path.exists(p):
        return None
    return io.open(p, encoding='utf-8').read().strip()


def record(iso, rate, note=''):
    """Store a rate read from TE, with where and when it came from."""
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    p = os.path.join(CACHE, '%s.txt' % iso)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(
        '%s\n# %s\n# %s\n' % (rate, url(iso), note))


def held(iso):
    row = rm.ROWS.get(iso)
    return row[0] if row else None


def compare():
    """[(iso, held, te, verdict)] - verdict in MATCH / STALE / UNVERIFIED."""
    out = []
    for iso in sorted(SLUG):
        h = held(iso)
        c = cached(iso)
        te = c.split('\n')[0].strip() if c else None
        if te is None:
            out.append((iso, h, None, 'UNVERIFIED'))
        elif rm._num(te) == rm._num(h):
            out.append((iso, h, te, 'MATCH'))
        else:
            out.append((iso, h, te, 'STALE'))
    return out


if __name__ == '__main__':
    rows = compare()
    print('R-47 POLICY RATE CHECK   rate_model vs Trading Economics')
    print()
    print('  %-5s %10s %10s   %s' % ('CCY', 'WE HOLD', 'TE SAYS', ''))
    bad = unv = 0
    for iso, h, te, v in rows:
        if v == 'STALE':
            bad += 1
        if v == 'UNVERIFIED':
            unv += 1
        print('  %-5s %10s %10s   %s%s'
              % (LABEL[iso], h, te or '-', v,
                 '   %s' % url(iso) if v != 'MATCH' else ''))
    print()
    if bad:
        print('*** %d RATE(S) STALE. The base is scored on a superseded rate,'
              % bad)
        print('    and LD-146 reads the same cell for its regime test.')
        sys.exit(1)
    if unv:
        print('%d rate(s) UNVERIFIED - no cached read. Fetch the page and'
              % unv)
        print('record it with rate_check.record(iso, rate, note).')
        sys.exit(1)
    print('all 8 policy rates match TE')
