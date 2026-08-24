# -*- coding: utf-8 -*-
"""
Reconcile score_model.ROWS against TradingEconomics country indicator pages.

WHY THIS EXISTS - F-35, 2026-08-23. Jeff: "can you double check our indicator
Results against TE? make sure we don't have cases like this."

SEVEN of 70 rows were wrong. Two had been wrong since the model was built on
2026-08-19; five went stale as newer prints landed and nothing re-read the
source. The 20 and 21 Aug editions re-scored the same wrong numbers and every
check passed.

THE ROOT CAUSE, and it is the reason this file exists: EVERY OTHER CHECK IN
THIS REPO VERIFIES ARITHMETIC ON THE ROWS. P2 recompute, score_model.compute,
the LD-39 row-count guard, the LD-17 token diff - all four are CLOSED LOOPS
that take the rows as input and test what happens downstream. All four pass
on wrong data. A row is arithmetically perfect right up until you compare it
to the world.

This module is the only thing in the repo that compares a row to the world.

USAGE
  Fetch (8 requests, one per country - each page carries every series):
      python pipelines/audit_te.py --fetch
  Report:
      python pipelines/audit_te.py
  Programmatic (used by render_edition.py's LD-50 staleness gate):
      from audit_te import stale_rows, capture_age_days

DATA + COMPARISON ONLY. It never edits score_model.py. A TE value that differs
is a QUESTION, not an instruction - the EUR Consumer Confidence row differs
because TE lists the August FLASH while the whitelist names the FINAL, and
"fixing" it would re-commit F-29. Every difference is triaged by hand.
"""
import re, io, html, os, sys, time, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CACHE = os.path.join(REPO, 'data', 'raw', 'te_audit')
sys.path.insert(0, HERE)

SLUG = {'US': 'united-states', 'EA': 'euro-area', 'GB': 'united-kingdom',
        'JP': 'japan', 'AU': 'australia', 'NZ': 'new-zealand',
        'CA': 'canada', 'CH': 'switzerland'}

# Rows where OUR presentation legitimately differs from TE's. Each needs a
# reason - this list is not a way to silence a mismatch (F-35).
KNOWN_DIFFERENT = {
    ('US', 'Balance of Trade'): 'we carry $bn, TE carries the bare number',
    ('JP', 'Balance of Trade'): 'we carry JPY bn, TE rounds',
    ('NZ', 'Balance of Trade'): 'we carry NZ$ bn, TE carries millions',
    ('CH', 'Balance of Trade'): 'we carry CHF bn, TE carries millions',
    ('AU', 'Employment Change'): 'we carry thousands, TE carries persons',
    ('EA', 'Balance of Trade'): 'LD-55 - we carry bn, TE carries millions',
    ('GB', 'Balance of Trade'): 'LD-55 - we carry bn, TE carries millions',
    ('AU', 'Balance of Trade'): 'LD-55 - we carry bn, TE carries millions',
    ('CA', 'Balance of Trade'): 'LD-55 - we carry bn, TE carries millions',
    ('CH', 'Non Farm Payrolls'): 'we carry millions, TE carries thousands',
    ('JP', 'Machine Tool Orders YoY'): 'we carry YoY%, TE lists the level',
    ('AU', 'Building Permits YoY Final'): 'we carry YoY%, TE lists the level',
}

# Rows where TE's page shows a DIFFERENT SERIES than the whitelist names, so a
# newer TE reference period does NOT mean our row is stale. Kept separate from
# KNOWN_DIFFERENT because this exempts the REFERENCE-PERIOD check, which is the
# stronger exemption and must stay short.
KNOWN_SERIES_GAP = {
    ('EA', 'S&P Global Mfg PMI Final'): 'TE lists the monthly FLASH first; '
        'the whitelist names the FINAL (F-29 rule)',
    ('GB', 'S&P Global Mfg PMI Final'): 'TE lists the FLASH; whitelist = FINAL',
    ('JP', 'S&P Global Mfg PMI Final'): 'TE lists the FLASH; whitelist = FINAL',
    ('AU', 'S&P Global Mfg PMI Final'): 'TE lists the FLASH; whitelist = FINAL',
    ('NZ', 'Electronic Retail Card Spending YoY'): 'aliased to TE retail sales '
        'yoy as the nearest series; the card-spending series is not on the '
        'country page. Value sourced from Stats NZ directly (F-34).',
    ('US', 'Building Permits MoM Final'):
        'TE lists the LEVEL (1443, Jul) and the Jul MoM PREL; the whitelist '
        'names the MoM FINAL, whose current value is the JUN Final -2.6%. '
        'The Jul Final releases Tue 25 Aug. Updating this row to TE would '
        're-commit F-40 (a preliminary published as a final).',
    ('EA', 'Consumer Confidence Final'):
        'TE lists the monthly FLASH; the whitelist names the FINAL, which '
        'releases later in the month. Updating this row to TE would '
        're-commit F-29 (a flash published as a final).',
}



# F-38: rows whose whitelist name does not fuzzy-match TE's own series name.
# WITHOUT AN ALIAS A ROW IS NEVER CHECKED AT ALL - 11 of 71 rows (15%) were
# silently unaudited while the tool reported "all rows agree with TE".
# Map whitelist name -> the exact TE series key.
TE_ALIAS = {
    ('AU', 'Westpac Consumer Conf Change'): 'consumer confidence mom',
    ('AU', 'ANZ-Indeed Job Ads MoM'): 'job advertisements',
    ('US', 'Durable Goods Ex Transp MoM'): 'durable goods orders ex transportation',
    ('EA', 'S&P Global Mfg PMI Final'): 'manufacturing pmi',
    ('GB', 'S&P Global Mfg PMI Final'): 'manufacturing pmi',
    ('JP', 'S&P Global Mfg PMI Final'): 'manufacturing pmi',
    ('AU', 'S&P Global Mfg PMI Final'): 'manufacturing pmi',
    ('CA', 'S&P Global Mfg PMI'): 'manufacturing pmi',
    ('CH', 'Procure.ch-UBS Mfg PMI'): 'manufacturing pmi',
    ('NZ', 'Business NZ PMI'): 'manufacturing pmi',
    ('NZ', 'Electronic Retail Card Spending YoY'): 'retail sales yoy',
}


def fetch(verbose=True):
    """Pull the 8 country indicator pages into data/raw/te_audit/."""
    import subprocess
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    ua = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    for iso, slug in sorted(SLUG.items()):
        dst = os.path.join(CACHE, slug + '.html')
        r = subprocess.run(['curl', '-s', '--compressed', '--max-time', '30',
                            '-H', 'User-Agent: ' + ua,
                            '-H', 'Accept: text/html,*/*;q=0.8',
                            '-o', dst, '-w', '%{http_code} %{size_download}',
                            'https://tradingeconomics.com/%s/indicators' % slug],
                           capture_output=True, text=True)
        if verbose:
            print('  %-16s %s' % (slug, r.stdout.strip()))


def capture_age_days():
    """Age of the newest cached page, in days. None if never fetched."""
    if not os.path.isdir(CACHE):
        return None
    files = [os.path.join(CACHE, f) for f in os.listdir(CACHE) if f.endswith('.html')]
    if not files:
        return None
    return (time.time() - max(os.path.getmtime(f) for f in files)) / 86400.0


def parse(path):
    """TE indicator rows -> {name_lower: (last, previous, reference)}."""
    if not os.path.exists(path):
        return {}
    s = io.open(path, encoding='utf-8', errors='ignore').read()
    out = {}
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', s, re.S):
        cells = [html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c))).strip()
                 for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
        cells = [c for c in cells if c]
        if len(cells) >= 4 and re.match(r'^[A-Za-z]', cells[0]):
            ref = ''
            for c in cells[::-1]:
                if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Q[1-4])', c):
                    ref = c
                    break
            nums = [c for c in cells[1:] if re.match(r'^-?[\d.,]+%?$', c)]
            unit = ''
            for c in cells:
                if c.lower() in ('percent', 'points', 'index points'):
                    unit = c.lower()
                    break
            if nums:
                out[cells[0].lower()] = (nums[0], nums[1] if len(nums) > 1 else '',
                                         ref, unit)
    return out


def _norm(n):
    n = n.lower()
    for junk in (' final', ' prel', ' flash', ' yoy', ' mom', ' qoq', ' rate',
                 ' change', ' index', ' s&p global', ' ism', ' anz', ' gfk',
                 ' cb ', ' nab ', ' westpac', ' rba ', ' procure.ch-ubs'):
        n = n.replace(junk, ' ')
    return re.sub(r'\s+', ' ', n).strip()



_MON = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}


def _refkey(ref):
    """Sortable key for a TE reference period: 'Jul/26', 'Aug 2026', 'Q2/26'."""
    r = (ref or '').lower().strip()
    m = re.match(r'q([1-4])', r)
    yr = re.search(r'(\d{2,4})', r)
    y = int(yr.group(1)) if yr else 0
    if y and y < 100:
        y += 2000
    if m:
        return (y, int(m.group(1)) * 3)
    for name, num in _MON.items():
        if r.startswith(name):
            return (y, num)
    return (0, 0)


def _num(x):
    m = re.search(r'-?[\d.]+', (x or '').replace(',', ''))
    return float(m.group(0)) if m else None


def stale_rows():
    """Rows whose value differs from TE and is NOT a known presentation gap.

    Returns [(ccy, indicator, ours, our_ref, te_value, te_ref)].
    """
    import score_model as sm
    out, unmatched = [], []
    cache = {}
    for r in sm.ROWS:
        cat, iso, name, act, prev, ref, thr, score = r
        exempt_value = ((iso, name) in KNOWN_DIFFERENT
                        or (iso, name) in KNOWN_SERIES_GAP)
        if iso not in cache:
            cache[iso] = parse(os.path.join(CACHE, SLUG[iso] + '.html'))
        te = cache[iso]
        if not te:
            continue
        key = TE_ALIAS.get((iso, name))
        if key and key not in te:
            key = None
        if not key:
            key = name.lower() if name.lower() in te else None
        if not key:
            cand = difflib.get_close_matches(_norm(name), [_norm(k) for k in te],
                                             n=1, cutoff=0.86)
            if cand:
                key = next((k for k in te if _norm(k) == cand[0]), None)
        if not key:
            # F-38: AN UNMATCHED ROW IS NOT A PASSING ROW. Until 2026-08-24
            # these were skipped silently and the audit still printed "all
            # comparable rows agree with TE" - 11 of 71 rows (15% of the
            # whitelist) were never checked at all, including the Westpac row
            # that was reading the wrong series the whole time.
            unmatched.append((sm.LABEL[iso], name, act, ref, '-', 'NO TE MATCH'))
            continue
        tl, tp, tref, tunit = te[key]

        # REFERENCE PERIOD IS CHECKED FOR EVERY ROW, INCLUDING EXEMPT ONES.
        # A units exemption must never hide a stale figure - on 2026-08-23 the
        # first version of this gate let a month-old CHF Balance of Trade row
        # through because that row is exempt from the VALUE comparison.
        if (ref and tref and (iso, name) not in KNOWN_SERIES_GAP
                and _refkey(tref) > _refkey(ref)):
            out.append((sm.LABEL[iso], name, act, ref, tl,
                        tref + ' NEWER'))
            continue
        # F-38 UNIT CONSISTENCY. An indicator whose NAME says it measures a
        # CHANGE (a rate, in percent) must not carry a TE row published in
        # POINTS - that is an INDEX, a different series. The audit compared
        # values and both 88.9 (the index) and 6.0 (the change) are REAL TE
        # numbers, so a value comparison can never see this. TE publishes the
        # unit and we never used it.
        wants_pct = bool(re.search(r'change|mom|yoy|qoq|rate',
                                   name, re.I))
        if wants_pct and tunit == 'points':
            out.append((sm.LABEL[iso], name, act, ref, tl,
                        tunit + ' WRONG SERIES'))
            continue
        if exempt_value:
            continue
        a, t = _num(act), _num(tl)
        if a is not None and t is not None and abs(a - t) >= 0.06:
            out.append((sm.LABEL[iso], name, act, ref, tl, tref))
    return out, unmatched


if __name__ == '__main__':
    if '--fetch' in sys.argv:
        print('Fetching TE country indicator pages...')
        fetch()
        print()
    age = capture_age_days()
    print('=' * 76)
    print('WHITELIST RECONCILIATION vs TradingEconomics')
    print('capture age: %s' % ('never fetched' if age is None else '%.1f days' % age))
    print('=' * 76)
    bad, unmatched = stale_rows()
    if not bad:
        print('\nAll comparable rows agree with TE.')
    else:
        print('\n%d ROW(S) DIFFER FROM TE - triage each by hand:\n' % len(bad))
        print('%-4s %-34s %-12s %-8s %-12s %-8s'
              % ('CCY', 'INDICATOR', 'OURS', 'OUR REF', 'TE', 'TE REF'))
        for row in bad:
            print('%-4s %-34s %-12s %-8s %-12s %-8s' % row)
        print('\nA TE value that differs is a QUESTION, not an instruction.')
        print('Newer print -> update. Different presentation -> add to')
        print('KNOWN_DIFFERENT with a reason. Never edit a row to silence this.')
    if unmatched:
        print('\n*** %d ROW(S) COULD NOT BE MATCHED TO ANY TE SERIES ***'
              % len(unmatched))
        print('These are NOT verified - the audit cannot see them at all,')
        print('and until 2026-08-24 it still reported "all rows agree".')
        print('Add a TE_ALIAS entry so they get checked.\n')
        for ccy, name, act, ref, _, _ in unmatched:
            print('   %-4s %-36s ours %-10s (%s)' % (ccy, name[:36], act, ref))
    print('\n%d exempt on presentation, %d on series definition, %d UNMATCHED.'
          % (len(KNOWN_DIFFERENT), len(KNOWN_SERIES_GAP), len(unmatched)))
