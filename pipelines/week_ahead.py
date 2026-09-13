# -*- coding: utf-8 -*-
"""
Extract next week's WHITELIST events from a persisted TE calendar capture.

WHY THIS EXISTS - F-36, 2026-08-23. Jeff: "Theres an update for USD Building
Permits on Tuesday can you check?"

He was right. US Building Permits MoM Final is a whitelist row, it lands Tue
25 Aug, and section 4.0 did not carry it. THE CAUSE: the calendar capture has
an EMPTY TIME FIELD for that event, and my hand-written extraction sorted by
timestamp - so every blank-time row silently fell out of the sort. One event
lost, and nothing said so.

The fix is not "remember to handle blanks". It is to make the extraction
COUNT WHAT IT DROPS and report it, so a silent loss becomes a visible one.
That is the same lesson as F-15 (a missing section is invisible to a content
check) applied to a data pipeline.

DATA + FILTERING ONLY. This module does not fetch; feed it a capture.
"""
import json, io, os, re, sys, datetime
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CCY = {'US': 'USD', 'EA': 'EUR', 'DE': 'EUR', 'FR': 'EUR', 'IT': 'EUR',
       'ES': 'EUR', 'GB': 'GBP', 'JP': 'JPY', 'AU': 'AUD', 'NZ': 'NZD',
       'CA': 'CAD', 'CH': 'CHF'}



# Words that carry no identifying weight - TE and the whitelist disagree on
# them freely ("Durable Goods Orders Ex Transp MoM" vs "Durable Goods Ex
# Transp MoM").
_NOISE = {'orders', 'rate', 'index', 'the', 'of', 'a'}

# F-37: a looser matcher creates FALSE POSITIVES, which is its own failure.
# Each entry: an event substring that must NOT be treated as the whitelist row.
_NOT = (
    ('Balance of Trade', 'goods trade balance'),   # advance GOODS-only, not the
                                                   # full balance of trade
    ('Inflation Rate YoY Final', 'prel'),          # FR/ES national prel prints
                                                   # are not the EA Final
    ('Non Farm Payrolls', 'revision'),            # F-50: the PRELIMINARY
                                                   # BENCHMARK REVISION (Fri
                                                   # 28 Aug 22:00 PHT, to Mar
                                                   # 2026 data) is NOT the
                                                   # monthly payrolls print.
                                                   # August payrolls land Fri
                                                   # 4 Sep 20:30 PHT - NEXT
                                                   # WEEK's window (LD-66).
    ('Non Farm Payrolls', 'benchmark'),
    # F-119 - A QUALIFIER WORD IN THE EVENT IS INVISIBLE TO SUBSET MATCHING.
    # Jeff, 2026-09-13: "I'm not seeing NZD inflation data being released on
    # Sept 18. They release inflation and employment data on a quarterly
    # basis so I don't think it is this month".
    #
    # He was right. 'Inflation Rate YoY' tokenises to {inflation, rate, yoy}
    # and NZ's 'FOOD inflation yoy aug' contains all three - the extra word
    # narrows the SERIES but cannot fail a subset test. The row scored +1 on
    # a food-price print standing in for a headline CPI that does not exist
    # this month: NZ publishes CPI QUARTERLY, next on 20 Oct.
    #
    # This is LD-59's rule ("NEVER fuzzy-match indicator names") reaching a
    # case the token matcher still let through. Two more were found by
    # testing every inflation-ish name in the archive rather than fixing only
    # the reported one:
    ('Inflation Rate YoY', 'food inflation'),      # NZ food prices
    ('Inflation Rate YoY', 'core inflation'),      # core is its own series
    ('Inflation Rate YoY', 'ex-food and energy'),  # JP core-core
    ('Inflation Rate MoM', 'food inflation'),
    ('Inflation Rate MoM', 'core inflation'),
    ('Inflation Rate YoY Final', 'core inflation'),
)

# National releases that must never satisfy a EUR-aggregate whitelist row.
_NATIONAL = {'DE', 'FR', 'IT', 'ES'}


# F-64 - ABBREVIATIONS THE CALENDAR DOES NOT USE.
# The whitelist writes 'Mfg'; every calendar writes 'manufacturing', so
# token matching failed on SEVEN OF EIGHT PMI rows and 4.0 showed none
# of them. Normalise both sides before comparing.
#
# Keep this list SMALL AND NAMED. F-37 established that loose fuzzy
# matching produces false positives - this is not fuzzy matching, it is
# a dictionary of abbreviations we ourselves introduced.
_SYN = {
    'mfg': 'manufacturing',
    'svcs': 'services',
    'chg': 'change',
    'conf': 'confidence',
    'prel': 'preliminary',
    'ex': 'excluding',
}


# F-64b - words in OUR row name that the calendar simply does not carry.
# CHF's row is 'Procure.ch-UBS Mfg PMI'; the calendar says 'procure.ch
# manufacturing pmi'. The vendor pairing is ours, not theirs. Same shape
# as audit_te.TE_ALIAS (F-38) and handled the same way: an explicit map,
# never looser matching.
_DROP = {
    ('CH', 'Procure.ch-UBS Mfg PMI'): {'ubs'},
}


def _norm(text):
    """Lower-case and expand our own abbreviations (F-64)."""
    out = []
    for w in re.findall(r'[a-z]+', (text or '').lower()):
        out.append(_SYN.get(w, w))
    return out


def match(ev, names, iso=None):
    """Return the whitelist name this calendar event IS, or None.

    F-36 used substring matching, which fails when the extra word sits in the
    MIDDLE: "durable goods ORDERS ex transp mom" against "durable goods ex
    transp mom". Token-set matching handles that - every meaningful word of
    the whitelist name must appear in the event.

    F-37: token matching alone is too loose. It matched "goods trade balance
    adv" to Balance of Trade, and French/Spanish preliminary CPI to the EA
    Inflation Rate Final. The _NOT list and the national-release rule are the
    stricter half, and BOTH halves are needed.
    """
    # F-49: THIS CHECK MUST COME FIRST. The exact-match shortcut below
    # used to run before it, so a national print whose name EXACTLY
    # equals the whitelist name skipped the guard entirely - Spain's
    # 'retail sales yoy' became EUR Retail Sales YoY and Germany's
    # 'unemployment rate' became EUR Unemployment Rate, both published
    # in the 2026-08-25 edition under Fri 28. TE puts the real EA
    # prints on 4 Sep and 1 Sep - NEXT WEEK AND THE WEEK AFTER.
    if iso in _NATIONAL:
        return None

    for name in names:
        n = name.lower()
        if ev == n:
            return name
        blocked = False
        for wl_name, bad in _NOT:
            if name == wl_name and bad in ev:
                blocked = True
                break
        if blocked:
            continue
        # AN EA-AGGREGATE ROW IS NEVER SATISFIED BY A NATIONAL PRINT.
        # The whitelist names euro-area figures; DE/FR/IT/ES releases are
        # inputs to them, not the thing itself. My first fix scoped this to
        # 'inflation' only and immediately produced a second false positive -
        # French unemployment BENEFIT CLAIMS matched EUR Unemployment Rate.
        # There is no EA-aggregate unemployment print this week at all.
        if iso in _NATIONAL:      # redundant since F-49, kept deliberately
            continue
        # F-64: normalise OUR abbreviations before comparing, or 'Mfg'
        # can never match 'manufacturing'.
        want = set(_norm(n)) - _NOISE - _DROP.get((iso, name), set())
        have = set(_norm(ev)) - _NOISE
        if want and want <= have:
            return name
    return None


# LD-63 - SECTION 4.0 SCORING: IS THE MARKET PRICING THIS CURRENCY TO IMPROVE?
# Jeff's rule, 2026-08-24. CATEGORY-INDEPENDENT - one test for every indicator,
# regardless of which category it sits in or what threshold section 2 uses.
#
#   consensus/forecast RANGE entirely ABOVE the current actual -> GOOD
#   range entirely BELOW the current actual                    -> BAD
#   current actual INSIDE the range                            -> NEUTRAL
#
# THE RANGE IS [consensus, forecast] - TE publishes BOTH as separate columns
# and Jeff's call is to treat the pair as the band. Where they are equal the
# range is a point and only exact equality reads NEUTRAL.
#
# WHY THIS IS A DIFFERENT QUESTION FROM SECTION 2. Section 2 asks "is this
# print good for the currency" against the indicator's own threshold. Section
# 4.0 now asks "IS THE MARKET PRICING AN IMPROVEMENT OR A DETERIORATION THIS
# WEEK" - a forward read on positioning, not a grade on a release. It feeds the
# proposed-pair selection (LD-64).
#
# It also removes the error class that produced this rule: the old 4.0 needed
# each indicator's own threshold and its own PREL/FINAL distinction, and the
# Building Permits row conflated a Jul PREL actual, a Jun FINAL previous and a
# consensus into one line. ONE TEST, THREE SOURCED NUMBERS, NO DERIVATION.
def coverage_gaps(capture_path):
    """Whitelisted currencies with NO calendar rows at all (R-20/F-57).

    Returns the sorted list of currency codes that appear in the
    whitelist but have ZERO rows of ANY kind in the capture.

    This is deliberately blunt. It does not ask whether a currency has
    an event THIS WEEK - a quiet week is normal. It asks whether the
    capture can see that country AT ALL. Zero rows across a whole
    capture is a feed defect, never a quiet calendar.
    """
    import score_model as sm
    data = json.load(io.open(capture_path, encoding='utf-8'))
    seen = set()
    for e in data:
        c = CCY.get(e.get('iso'))
        if c:
            seen.add(c)
    want = set(sm.LABEL[r[1]] for r in sm.ROWS)
    return sorted(want - seen)


def current_window(now=None):
    """The Mon-Fri window 4.0 must cover, rolling on SUNDAY (LD-66).

    Mon-Fri  -> this week's Mon..Fri (the week in progress).
    Sat      -> still this week (the week just ended is still the
                locked set's week).
    SUNDAY   -> ROLLS to the coming Mon..Fri. This is the WEEKEND PREP
                edition's window.

    F-48, 2026-08-26: the window used to be a hardcoded default
    ('2026-08-24'..'2026-08-28'), so 4.0 kept publishing one week's
    dates while the calendar moved on. Events from LATER weeks were
    listed under this week and showed up with no consensus - TE has
    none yet for an event that far out - which read as a sourcing
    defect when it was really a WINDOW defect.
    """
    if now is None:
        now = (dt.datetime.now(dt.timezone.utc)
               .astimezone(dt.timezone(dt.timedelta(hours=8))))
    d = now.date()
    wd = d.weekday()          # Mon=0 .. Sun=6
    if wd == 6:               # Sunday - roll forward
        mon = d + dt.timedelta(days=1)
    else:
        mon = d - dt.timedelta(days=wd)
    return mon.isoformat(), (mon + dt.timedelta(days=4)).isoformat()


# F-70. TWO CHANNELS REACH THE CURRENCY, AND THEY CARRY OPPOSITE SIGNS.
#
# Jeff, 2026-08-31, stating it exactly:
#   "USD Unemployment Rate 4.1% -> 4.2% BAD. This is correct because
#    decreasing unemployment is better for the economy. But in Inflation we
#    want it increasing because it poses for Interest Rate Hike"
#
#   ECONOMIC-HEALTH channel -> the currency DIRECTLY.
#       unemployment, claimant count, jobless claims.  LOWER is better.
#
#   RATE channel -> the currency THROUGH the central bank.
#       inflation, CPI, PPI.  HIGHER is better, because it forces the hike -
#       until it runs far past the bank's own ceiling, where more inflation
#       is a policy problem rather than rate support.
#
# Both look like "bad news" in plain language, which is why one list of
# "lower is better" collapsed them and inverted every inflation forecast.
# The DESTINATION is the same; the ROUTE decides the sign.
#
#
# Jeff, 2026-08-31: "The inflation of CHF is expected to increase from 0.4% to
# 0.7% why is it bad for the currency?" It is not. Rising inflation is RATE
# SUPPORT (LD-23, and Jeff's causal chain of 2026-08-29). This list used to
# contain 'inflation rate', 'cpi', 'ppi' - the CONSUMER's sign - so every
# rising-inflation forecast graded BAD for every currency.
#
# Only genuine currency-negatives belong here.
LOWER_IS_BETTER = (
    'unemployment rate', 'unemployment change', 'claimant count change',
    'jobless claims',
)

# Series where a HIGHER print supports the currency through the rate channel,
# but ONLY while inflation is still arguing for tightening. Above the bank's
# own ceiling, more inflation is a policy problem rather than rate support -
# stagflation is not currency-positive - so this is mandate-aware.
RATE_CHANNEL = (
    'inflation rate', 'core inflation rate', 'cpi', 'ppi', 'producer price',
)
# How far above a bank's ceiling inflation may run before extra inflation
# stops helping the currency. Percentage points.
OVERSHOOT_TOLERANCE = 1.5


def rate_channel(name):
    return any(k in (name or '').lower() for k in RATE_CHANNEL)


def inflation_is_good(ccy, expected):
    """Does MORE inflation help this currency at this level? (F-70)

    Uses the bank's OWN mandate band (LD-23 - mandates are not all 2%).
    Below or inside the band, rising inflation builds the rate case. Far
    above it, it stops being support and becomes a policy problem.
    """
    try:
        import rate_model
        iso = {'USD': 'US', 'EUR': 'EA', 'GBP': 'GB', 'JPY': 'JP',
               'AUD': 'AU', 'NZD': 'NZ', 'CAD': 'CA', 'CHF': 'CH'}.get(ccy)
        lo, hi = rate_model.MANDATE[iso]
    except Exception:
        return True
    if expected is None:
        return True
    return expected <= hi + OVERSHOOT_TOLERANCE


def lower_is_better(name, threshold=None, ccy=None, expected=None):
    """Does a LOWER print favour the CURRENCY for this series?

    F-66: the whitelist's threshold column answers this when it names the
    previous print - '<Prev' means lower is better.

    F-70: inflation is the exception that proves why the NAME fallback is
    dangerous. For a consumer, lower inflation is better. For a CURRENCY it
    is the reverse - inflation drives the rate decision, and the rate decides
    strength. Rising inflation was grading BAD for every currency because
    'inflation rate' sat in LOWER_IS_BETTER.
    """
    t = (threshold or '').strip().lower()
    # F-66b. '<Prev' is a COMPARISON and carries direction. '<0%' is a STATE
    # description and does not - it says the series is currently negative,
    # not which way is better.
    if 'prev' in t:
        return t.startswith('<')
    if rate_channel(name):
        # More inflation helps until it runs far past the bank's ceiling.
        return not inflation_is_good(ccy, expected)
    n = (name or '').lower()
    return any(k in n for k in LOWER_IS_BETTER)


def market_pricing(previous, consensus, forecast=None, name=None,
                   threshold=None, ccy=None):
    """Grade what the market is PRICING for a not-yet-released event.

    Returns GOOD / NEUTRAL / BAD for the CURRENCY, or None when there is no
    consensus to price against.

    previous  - the CURRENT ACTUAL (the last released print for the series)
    consensus - TE consensus column
    forecast  - TE forecast column; defaults to consensus when absent
    name      - the whitelist indicator name (direction of goodness)
    threshold - the whitelist threshold column, which ENCODES that direction

    F-66. THE BUG THIS FIXES: the original returned GOOD whenever
    previous < consensus, for EVERY indicator. That is only right where a
    LOWER print is better. Consensus expecting US unemployment to rise
    4.1% -> 4.2% is BAD for USD, and this function called it GOOD.

    Same defect as F-62/LD-71: a comparison is not a direction. The
    whitelist records the direction; read it rather than assuming.

    The sense is: does the market expect this series to move in the
    currency's FAVOUR (GOOD) or AGAINST it (BAD) relative to the last print?
    """
    if previous is None or consensus is None:
        return None
    hi = consensus if forecast is None else max(consensus, forecast)
    lo = consensus if forecast is None else min(consensus, forecast)
    if lo <= previous <= hi:
        return 'NEUTRAL'
    # The expected print sits ABOVE the last one when previous < lo.
    expected_higher = previous < lo
    if lower_is_better(name, threshold, ccy=ccy,
                       expected=(hi + lo) / 2.0):
        return 'BAD' if expected_higher else 'GOOD'
    return 'GOOD' if expected_higher else 'BAD'


def pht(date, t):
    """TE calendar times are UTC. PHT = UTC+8 (F-2: verify every run)."""
    t = (t or '').strip()
    if not t:
        return None
    try:
        d = datetime.datetime.strptime(date + ' ' + t, '%Y-%m-%d %I:%M %p')
    except ValueError:
        return None
    return d + datetime.timedelta(hours=8)


def whitelist_events(capture_path, start, end):
    """Whitelist events in [start, end] (ISO dates), oldest first.

    Returns (events, no_time) where each event is
    (pht_datetime_or_None, ccy, whitelist_name, raw_event, iso_date).

    NO EVENT IS EVER DROPPED. Rows with no time land in `no_time` and the
    caller must publish them - F-36 happened because a sort silently
    discarded them.
    """
    import score_model as sm
    wl = {}
    for r in sm.ROWS:
        wl.setdefault(sm.LABEL[r[1]], []).append(r[2])

    data = json.load(io.open(capture_path, encoding='utf-8'))
    timed, no_time, seen = [], [], set()
    for e in data:
        # F-63: CONVERT FIRST, FILTER SECOND. The capture stores UTC and the
        # LD-66 window is PHT, so filtering the raw date drops every event
        # after 16:00 UTC - which is the whole Asian session. JPY Retail
        # Sales at 23:50 UTC Sun 30 Aug IS 07:50 PHT Mon 31 Aug, inside the
        # window, and was being rejected before conversion.
        _p = pht(e.get('date', ''), e.get('time', ''))
        _d = _p.strftime('%Y-%m-%d') if _p else e.get('date', '')
        if not (start <= _d <= end):
            continue
        ccy = CCY.get(e.get('iso'))
        if not ccy:
            continue
        ev = (e.get('event') or '').lower()
        hit = match(ev, wl.get(ccy, []), e.get('iso'))
        if not hit:
            continue
        key = (ccy, hit)
        if key in seen:
            continue
        seen.add(key)
        p = pht(e['date'], e.get('time'))
        rec = (p, ccy, hit, e.get('event'), e['date'])
        (timed if p else no_time).append(rec)

    # LD-52: DATE -> TIME -> CCY. Chronological, because that is the order a
    # trading week is lived: you read down the list as events hit the tape.
    # Grouping by currency instead would break the day's sequence - Friday's
    # JPY 07:30 would print after EUR 17:00.
    timed.sort(key=lambda r: (r[0], r[1]))
    no_time.sort(key=lambda r: (r[4], r[1]))
    return timed, no_time


if __name__ == '__main__':
    cap = sys.argv[1] if len(sys.argv) > 1 else None
    _ws, _we = current_window()
    start = sys.argv[2] if len(sys.argv) > 2 else _ws
    end = sys.argv[3] if len(sys.argv) > 3 else _we
    if not cap:
        import glob
        caps = sorted(glob.glob(os.path.join(
            os.path.dirname(HERE), 'data', 'raw', 'calendar', '*.json')))
        cap = caps[-1] if caps else None
    if not cap:
        raise SystemExit('no calendar capture found')
    timed, no_time = whitelist_events(cap, start, end)
    print('capture: %s' % os.path.basename(cap))
    print('window : %s .. %s (PHT)   [LD-66 current week]' % (start, end))
    print()
    print('%-16s %-5s %s' % ('WHEN (PHT)', 'CCY', 'WHITELIST INDICATOR'))
    for p, ccy, name, raw, d in timed:
        print('%-16s %-5s %s' % (p.strftime('%a %d %H:%M'), ccy, name))
    if no_time:
        print()
        print('*** %d EVENT(S) WITH NO TIME IN THE CAPTURE - PUBLISH THESE TOO ***'
              % len(no_time))
        for p, ccy, name, raw, d in no_time:
            print('%-16s %-5s %s   (calendar: "%s")' % (d, ccy, name, raw))
    print()
    print('TOTAL WHITELIST EVENTS: %d  (%d timed, %d untimed)'
          % (len(timed) + len(no_time), len(timed), len(no_time)))

    gaps = coverage_gaps(cap)
    if gaps:
        print()
        print('*** COVERAGE GAP (R-20): %s HAVE NO CALENDAR ROWS AT ALL ***'
              % ', '.join(gaps))
        print('    Not "no event this week" - the capture cannot see these')
        print('    countries at all. Any event they have is INVISIBLE to 4.0.')
        print('    Hand-source them and say so in the edition.')
