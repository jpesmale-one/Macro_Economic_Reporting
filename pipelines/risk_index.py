# -*- coding: utf-8 -*-
"""LD-174 - RISK TONE FROM INDICES, NOT FROM THE CURRENCIES.

Jeff, 2026-10-28:

    "did you based the Risk On and Risk Off on the currencies? I think it's
     better if we look at Indices for this one instead of the currencies"

*** HE IS RIGHT, AND THE PROBLEM IS CIRCULARITY, NOT JUST TASTE.
LD-173 derived the tone from the currency baskets themselves - commodity
strength minus haven strength - and then graded currency pairs against that
tone. The measure and the thing being measured came from the same 28 bars.
So the validation I published (CADCHF 1.50 / 1.00 / 0.77 by tone) was partly
measuring that CAD went up on days CAD went up. The slope was real but the
test could not distinguish a risk effect from an arithmetic identity.

AN INDEX BASKET IS EXTERNAL. Equities and volatility are priced by different
participants in different markets; if FX pairs line up with them, that is
information rather than restatement.

*** JEFF CHOSE THE WIDER CROSS-ASSET BASKET over SPX+VIX alone, and the
reason is sound: FX trades around the clock, so a session that Asia or
Europe leads is invisible in a US-only read.

    TVC:SPX     S&P 500          United States
    TVC:NI225   Japan 225        Asia
    XETR:DAX    DAX              Europe
    TVC:VIX     volatility       the fear leg, inverted

*** THE ONE VENDOR ASYMMETRY, STATED NOT HIDDEN. Three series are TVC; DAX
is not listed there at all, so it comes from XETR - the official German
exchange, which is a better source than a broker CFD but a different vendor.
LD-23 still holds because this is ONE GLOBAL STATE applied to all eight
currencies identically; there is no per-currency asymmetry to argue about.

*** AND THE HARD LIMIT, WHICH IS JEFF'S OWN POINT TURNED AROUND: THESE
INDICES DO NOT SHARE A TRADING WINDOW. A daily bar for NI225 closes before
the US session opens; DAX closes mid-US-afternoon. So a single calendar date
is three different windows, and an index "day" is not the FX day it is
compared against. This is why each leg is reported separately and the
headline is a MEAN OF SIGNS rather than a sum of percentages - a mean of
directions is robust to the windows not lining up, where a weighted sum
would quietly let whichever index moved most set the tone.

*** WHAT THE EXTERNAL MEASURE FOUND, MEASURED BEFORE SHIPPING IT.
Graded real pairs across every session on disk, by INDEX tone:

    pair           category   riskON   MIXED  riskOFF
    AUDJPY LONG    RISK ON      1.23    0.90     0.66   correct slope
    AUDJPY SHORT   RISK OFF     0.82    1.11     1.51   correct slope
    NZDCHF LONG    RISK ON      1.27    0.74     0.78   correct slope
    CADCHF LONG    RISK ON      0.93    0.91     1.48   *** INVERTED
    GBPAUD LONG    EITHER       0.66    0.91     1.35   behaves risk-OFF

*** AND THESE NUMBERS ARE MUCH SMALLER THAN THE CURRENCY VERSION'S, WHICH
IS THE POINT RATHER THAN A DISAPPOINTMENT. LD-173 had AUDJPY LONG at
3.12 / 0.85 / 0.25, which is close to an arithmetic identity: AUD-up,
JPY-down days ARE the days the commodity basket beat the haven basket,
because AUD and JPY are IN those baskets. The index version cannot cheat
that way, so its slopes are weaker and believable.

*** THE CADCHF INVERSION IS NOT NOISE - CAD DOES NOT TRADE AS A COMMODITY
CURRENCY. Mean currency strength by index tone, over the same sessions:

    AUD  +0.139 on / -0.072 off   spread +0.211   high-beta
    NZD  +0.082 / -0.078          +0.161          high-beta
    GBP  +0.007 / +0.013          -0.006          neutral
    CHF  -0.042 / +0.005          -0.046          haven-like
    EUR  -0.042 / +0.048          -0.090          haven-like
    JPY  -0.076 / +0.014          -0.090          haven-like
    CAD  -0.068 / +0.071          -0.139          HAVEN-LIKE
    USD  -0.089 / +0.125          -0.214          haven-like

CAD is classed Commodity by ft.ROLE and trades more defensively than CHF
does. So CADCHF LONG is not a risk-on expression at all - it is haven
against haven, which is exactly why it has no clean tilt. EUR likewise
trades haven-like while classed Cyclical.

*** THAT IS F-3 TERRITORY AND IS REPORTED, NOT CHANGED. ft.ROLE and
pair_select.CATEGORY are Jeff's closed set; this module measures against
them and says where price disagrees. Changing a role would silently restate
every historical category.

LD-5 AS AMENDED: TradingView is the authority. Yahoo is NEVER a fallback.
LD-4: describes what prices did. No entries, exits, stops or targets.
F-73: a session without data returns None, never a guessed NEUTRAL.
"""
import io
import os
import json
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, 'data', 'raw', 'indices')

# (key, symbol, label, region, invert)
# invert=True means a RISE is risk-OFF (volatility).
SERIES = (
    ('SPX', 'TVC:SPX', 'S&P 500', 'United States', False),
    ('NI225', 'TVC:NI225', 'Japan 225', 'Asia', False),
    ('DAX', 'XETR:DAX', 'DAX', 'Europe', False),
    ('VIX', 'TVC:VIX', 'Volatility (VIX)', 'global', True),
)

KEYS = tuple(s[0] for s in SERIES)
EQUITY = tuple(s[0] for s in SERIES if not s[4])

# A leg counts as moving only beyond this, so a flat index does not vote.
# Equities in %, VIX in % of its own level.
DEADBAND = 0.10

# Bands on the mean-of-signs score, which runs -1 .. +1.
# With four legs the attainable values are 0, +/-0.25, +/-0.5, +/-0.75, +/-1.
CLEAR = 0.74      # at least 3 of 4 legs agreeing, none against
MILD = 0.24       # a net tilt of at least one leg


def session_of(epoch):
    """ISO date of the trading session this bar belongs to.

    *** F-174 - A SINGLE SHIFT CANNOT DATE FOUR DIFFERENT MARKETS, and
    copying the yields' +12h convention here silently lost a whole leg.
    These bars are stamped at each market's own open, in UTC:
        NI225  00:00   (Tokyo)
        DAX    07:00/08:00  (Frankfurt, moves with DST)
        VIX    07:15
        SPX    13:30   (New York)
    The +12h shift that correctly carries Tokyo's 00:00 onto its own date
    ALSO carries New York's 13:30 onto the NEXT date. So SPX dated Friday's
    bar as Saturday, Monday's as Tuesday, and 2026-10-26 had no SPX bar at
    all - the tone then ran on three legs and reported a vote of 0 for the
    largest market in the basket.
    THE SYMPTOM WAS A GAP IN A SEQUENCE: 10-24 then 10-27, skipping 26.
    Worth remembering as a tell - a daily series that skips a weekday is
    usually a dating bug, not a market holiday.

    THE FIX IS TO DATE A BAR BY ITS OWN UTC DAY and only shift the bars
    that genuinely open before midnight UTC. Asia opens at 00:00 UTC, which
    is already the correct date, so NOTHING needs shifting here - every one
    of these four markets opens at or after 00:00 UTC on its own trading
    day. The yields needed +12h because TVC stamps some of those at 21:00
    UTC the PREVIOUS day; these do not.
    F-77 applies: the epoch is stored beside the date it produced, so this
    is auditable rather than asserted.
    """
    return (dt.datetime(1970, 1, 1)
            + dt.timedelta(seconds=int(epoch))).date().isoformat()


def path(key):
    return os.path.join(OUT, '%s.json' % key)


def save(key, symbol, bars, note=''):
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    rows = []
    for b in bars:
        t = int(b['time'])
        rows.append({'session': session_of(t), 'epoch': t,
                     'open': b['open'], 'high': b['high'],
                     'low': b['low'], 'close': b['close']})
    rows.sort(key=lambda r: r['session'])
    doc = {'key': key, 'symbol': symbol, 'note': note,
           'pulled': dt.datetime.now().isoformat(timespec='seconds'),
           'source': 'TradingView (LD-5 as amended); Yahoo is never used',
           'role': 'risk-tone leg (LD-174)',
           'bars': rows}
    with io.open(path(key), 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(doc, indent=1, sort_keys=True))
    return len(rows)


def load(key):
    p = path(key)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding='utf-8') as f:
        return json.load(f)


def series(key):
    d = load(key)
    if not d:
        return None
    return dict((b['session'], b) for b in d['bars'])


def _pct(key, day):
    """Open-to-close % for one leg on one session, or None.

    OPEN TO CLOSE, not close-to-close, to match how the daily measures
    currency strength - the question is what THAT SESSION did.
    """
    s = series(key)
    if not s or day not in s:
        return None
    b = s[day]
    if not b['open']:
        return None
    return (b['close'] - b['open']) / b['open'] * 100.0


def legs(day):
    """{key: (pct, vote)} - vote is +1 risk-on, -1 risk-off, 0 flat/absent."""
    out = {}
    for key, sym, lbl, region, inv in SERIES:
        p = _pct(key, day)
        if p is None:
            out[key] = (None, 0)
            continue
        if abs(p) < DEADBAND:
            out[key] = (p, 0)
            continue
        v = 1 if p > 0 else -1
        if inv:
            v = -v            # VIX up = risk off
        out[key] = (p, v)
    return out


def tone(day):
    """(label, score, detail) - score is the MEAN OF SIGNS, -1 .. +1.

    A mean of DIRECTIONS rather than a weighted sum of percentages, because
    the four legs do not share a trading window and are not on a common
    scale (VIX moves percent-wise far more than an equity index). A sum
    would let the most volatile leg set the tone; a mean of signs asks the
    simpler and more robust question - how many legs agree?
    """
    lg = legs(day)
    votes = [v for _p, v in lg.values()]
    have = [k for k in lg if lg[k][0] is not None]
    if not have:
        return None, None, {}
    score = sum(votes) / float(len(SERIES))
    if score >= CLEAR:
        lbl = 'RISK ON'
    elif score >= MILD:
        lbl = 'mild RISK ON'
    elif score <= -CLEAR:
        lbl = 'RISK OFF'
    elif score <= -MILD:
        lbl = 'mild RISK OFF'
    else:
        lbl = 'MIXED'
    return lbl, score, {'legs': lg, 'have': have,
                        'agree': sum(1 for v in votes if v > 0),
                        'against': sum(1 for v in votes if v < 0),
                        'flat': sum(1 for v in votes if v == 0)}


def aligns(pair_category, label):
    """'ALIGNED' | 'AGAINST' | 'n/a'. Same contract as risk_tone.aligns."""
    if not label or label == 'MIXED' or pair_category not in ('RISK ON',
                                                              'RISK OFF'):
        return 'n/a'
    on = label.endswith('RISK ON')
    return 'ALIGNED' if on == (pair_category == 'RISK ON') else 'AGAINST'


def status():
    out = []
    for key, sym, lbl, region, inv in SERIES:
        d = load(key)
        if not d or not d['bars']:
            out.append((key, sym, 0, '-'))
            continue
        out.append((key, sym, len(d['bars']), d['bars'][-1]['session']))
    return out


def report(day):
    lbl, sc, d = tone(day)
    if lbl is None:
        return 'RISK TONE (indices) %s: no data' % day
    L = ['RISK TONE (indices)   %s' % day,
         '  %s   score %+.2f   (%d for, %d against, %d flat)'
         % (lbl, sc, d['agree'], d['against'], d['flat']),
         '',
         '  %-6s %-11s %9s %6s  %s'
         % ('leg', 'region', 'move', 'vote', 'symbol')]
    for key, sym, name, region, inv in SERIES:
        p, v = d['legs'][key]
        L.append('  %-6s %-11s %9s %6s  %s'
                 % (key, region,
                    ('%+.2f%%' % p) if p is not None else '-',
                    ('%+d' % v) if v else '0',
                    sym + ('  (inverted)' if inv else '')))
    return '\n'.join(L)


if __name__ == '__main__':
    import sys
    day = sys.argv[1] if len(sys.argv) > 1 else (
        dt.date.today() - dt.timedelta(days=1)).isoformat()
    print(report(day))
