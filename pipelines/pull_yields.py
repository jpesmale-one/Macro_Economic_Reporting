# -*- coding: utf-8 -*-
"""LD-171 - 2-YEAR GOVERNMENT YIELDS, LOGGED BUT NOT SCORED.

Jeff, 2026-10-24: "Let's keep our macro economic reporting for now and
gather more data. we can also add that 2-year yields and shrinkage
calibration you're mentioning."

WHY THE 2-YEAR, AND WHY IT IS NOT THE POLICY RATE. The policy rate is a
STOCK that changes eight times a year; the 2-year yield is the market's
PRICE of where that rate is going, and it moves every second. Jeff's own
intuition reached for this ("if you look at the RHO AUD mostly on top...
currently AUD has the higher IR in the list"), and the reason the carry
LEVEL test failed - rho(rate level, drift) = -0.293, the wrong sign - is
that a level everyone can see is already priced. It is the CHANGE in the
expected path that moves a currency.

*** AND THE LAG SCAN IS WHY THIS MATTERS. The macro board's best
agreement with price sits at offset -30 sessions (~6 weeks): it describes
the recent past, because monthly indicators print 2-6 weeks after their
reference period and we score the LEVEL of that stale print. A yield
CANNOT be stale by construction. That is the lag fixed by changing the
clock, not by cleverer scoring.

*** THIS FILE SCORES NOTHING. F-3 - the indicator list is a CLOSED SET and
amendments are Jeff's call alone. He authorised LOGGING, so this writes
data and stops. No fact table reads it, no board uses it, nothing in R-46
depends on it. When there are enough weeks to test, the test runs against
history that was recorded without knowing the answer.

LD-23 IS SATISFIED, VERIFIED NOT ASSUMED. All eight resolve on TVC with
the same vendor, same instrument class and same daily bars:
    TVC:US02Y  United States 2 Year Government Bonds Yield
    TVC:DE02Y  Germany 2 Year Government Bonds Yield      (EUR proxy)
    TVC:GB02Y  United Kingdom 2 Year Government Bonds Yield
    TVC:JP02Y  Japan 2 Year LSEG Government Bonds Yield
    TVC:AU02Y  Australia 2 Year Government Bonds Yield
    TVC:NZ02Y  New Zealand 2 Year Government Bonds Yield
    TVC:CA02Y  Canada 2 Year Government Bonds Yield
    TVC:CH02Y  Switzerland 2 Year Government Bonds Yield

*** THE ONE HONEST ASYMMETRY, STATED NOT HIDDEN: the euro area has no
single sovereign, so DE02Y (Germany) is a PROXY. It is the market's own
benchmark for EUR rates, but it is not "the EUR 2-year" the way US02Y is
the USD one. Under French fiscal stress the Bund is exactly the wrong leg
to read EUR from - which is itself the CHF/EUR haven story the board
already cannot see. Recorded here so the eventual test knows it.

LD-5 AS AMENDED: TradingView is the price authority. Yahoo is NEVER a
fallback - if TradingView will not start, say so and stop.
LD-4: this records what yields DID. No entries, exits, stops or targets.
"""
import io
import os
import json
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, 'data', 'raw', 'yields')

# ccy -> (symbol, description as the vendor states it, proxy note)
SYMBOLS = (
    ('USD', 'TVC:US02Y', 'United States 2 Year Government Bonds Yield', ''),
    ('EUR', 'TVC:DE02Y', 'Germany 2 Year Government Bonds Yield',
     'PROXY - no single euro-area sovereign; Bund is the EUR benchmark'),
    ('GBP', 'TVC:GB02Y', 'United Kingdom 2 Year Government Bonds Yield', ''),
    ('JPY', 'TVC:JP02Y', 'Japan 2 Year LSEG Government Bonds Yield', ''),
    ('AUD', 'TVC:AU02Y', 'Australia 2 Year Government Bonds Yield', ''),
    ('NZD', 'TVC:NZ02Y', 'New Zealand 2 Year Government Bonds Yield', ''),
    ('CAD', 'TVC:CA02Y', 'Canada 2 Year Government Bonds Yield', ''),
    ('CHF', 'TVC:CH02Y', 'Switzerland 2 Year Government Bonds Yield', ''),
)

CCYS = tuple(s[0] for s in SYMBOLS)


def session_of(epoch):
    """ISO date of the TRADING SESSION a daily bar belongs to.

    *** F-166 - A NAIVE UTC DATE SPLIT THE SAME TRADING DAY IN TWO, and my
    own R-50-style guard flagged it as staleness. TVC stamps each daily
    yield bar at that market's OWN session open, so 23 Oct reads:
        JPY/AUD/NZD 2026-10-22 21:00 UTC   (Asia opens previous UTC day)
        USD         2026-10-22 23:00 UTC
        EUR/CHF     2026-10-23 06:00 UTC
        GBP         2026-10-23 07:00 UTC
        CAD         2026-10-23 10:00 UTC
    All five epochs are ONE trading day. Dating them in UTC put Asia and
    the US on 10-22 and Europe on 10-23, so the alignment check reported
    "PRESENT BUT NOT ALIGNED" on a complete, current pull.

    THE FIX IS TO SHIFT INTO THE TRADING DAY before taking the date. +12h
    is enough to carry every Asian open forward and leaves the late CAD
    open on the same date. F-77 applies - the epoch is stored beside the
    date it produced, so this is auditable rather than asserted, and the
    raw epochs above are what proved the bars were never stale.
    """
    return (dt.datetime(1970, 1, 1)
            + dt.timedelta(seconds=int(epoch) + 12 * 3600)).date().isoformat()


def path(ccy):
    return os.path.join(OUT, '%s.json' % ccy)


def save(ccy, symbol, bars, note=''):
    """Write [{session, open, high, low, close}] plus provenance.

    Sessions are ISO dates derived from the vendor's epoch. F-77 applies:
    verify the time, never re-convert a rendered one - so the epoch is
    stored alongside the date it produced.
    """
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    rows = []
    for b in bars:
        t = int(b['time'])
        rows.append({'session': session_of(t),
                     'epoch': t,
                     'open': b['open'], 'high': b['high'],
                     'low': b['low'], 'close': b['close']})
    rows.sort(key=lambda r: r['session'])
    doc = {'currency': ccy, 'symbol': symbol, 'note': note,
           'pulled': dt.datetime.now().isoformat(timespec='seconds'),
           'source': 'TradingView (LD-5 as amended); Yahoo is never used',
           'scored': False,
           'scored_note': 'LD-171 - logged only. F-3: adding this to the '
                          'board is Jeff\'s call alone.',
           'bars': rows}
    with io.open(path(ccy), 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(doc, indent=1, sort_keys=True))
    return len(rows)


def load(ccy):
    p = path(ccy)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)


def series(ccy):
    """{session: close} or None."""
    d = load(ccy)
    if not d:
        return None
    return dict((b['session'], b['close']) for b in d['bars'])


def spread(a, b, session=None):
    """a's 2y minus b's 2y on a session (latest common if None)."""
    sa, sb = series(a), series(b)
    if not sa or not sb:
        return None
    if session is None:
        common = sorted(set(sa) & set(sb))
        if not common:
            return None
        session = common[-1]
    if session not in sa or session not in sb:
        return None
    return sa[session] - sb[session]


def status():
    """One line per currency: what is on disk and how current."""
    out = []
    for ccy, sym, desc, note in SYMBOLS:
        d = load(ccy)
        if not d:
            out.append((ccy, sym, 0, '-', 'MISSING'))
            continue
        bs = d['bars']
        out.append((ccy, sym, len(bs), bs[-1]['session'] if bs else '-',
                    'proxy' if d.get('note') else 'ok'))
    return out


def report():
    rows = status()
    L = ['LD-171  2-YEAR YIELDS ON DISK  (logged, NOT scored)',
         '  %-5s %-12s %7s %12s  %s' % ('CCY', 'symbol', 'bars',
                                        'latest', 'flag')]
    for ccy, sym, n, last, flag in rows:
        L.append('  %-5s %-12s %7d %12s  %s' % (ccy, sym, n, last, flag))
    have = [r for r in rows if r[2]]
    if len(have) == len(rows) and have:
        lasts = set(r[3] for r in have)
        L.append('')
        if len(lasts) == 1:
            L.append('  all 8 present and current to %s' % lasts.pop())
        else:
            L.append('  *** PRESENT BUT NOT ALIGNED: %s' % ', '.join(
                sorted(lasts)))
            L.append('      a stale leg silently corrupts every spread '
                     '(same shape as R-50)')
    return '\n'.join(L)


if __name__ == '__main__':
    print(report())
