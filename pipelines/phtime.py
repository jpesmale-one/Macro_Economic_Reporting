# -*- coding: utf-8 -*-
"""EVERY TIME IN THIS REPO IS PHT (UTC+8) - LD-115.

Jeff, 2026-09-10:

    "Every time youre going to Trading Economics and Trading View can you
     always verify the Time Zone and make sure you're looking at UTC+8 so
     that it always fall on the same Timezone where I am."

WHY THIS IS A MODULE AND NOT A HABIT. Two timezone errors landed in two
consecutive turns, and LD-114 - written between them, telling me to verify
before asserting - did not stop the second:

    F-106  a 17:30 UTC release read against the daily bar LABELLED the next
           day. OANDA daily bars open 21:00 UTC, so the release sat in the
           PREVIOUS bar. Reported -11.6 pips; actual +111.6.
    F-107  TE's stored "11:50 PM" read as PHT and converted BACKWARDS to
           15:50 UTC. It IS UTC, so the release was 23:50 UTC = 08 Sep 07:50
           PHT. Analysed bars eight hours early. Reported -7.2 pips;
           actual +83.0.

Both reversed a SIGN and both survived my own review. A rule I have to
remember is not a control; a function I have to call is.

THE TWO SOURCE CONVENTIONS, each verified 2026-09-10 against a row Jeff
confirmed on his own screen:

    TRADING ECONOMICS   capture_calendar stores TE's time cell VERBATIM and
                        converts NOTHING. The string is UTC. The `PHT` in a
                        capture FILENAME is when WE FETCHED, never when the
                        event fires.
                            stored '2026-09-07 11:50 PM'
                            -> 2026-09-08 07:50 AM PHT   (Jeff's screen)

    TRADINGVIEW         OHLCV `time` is a UNIX epoch, i.e. UTC. A bar's
                        timestamp is its OPEN. OANDA daily bars open at
                        21:00 UTC, so a daily bar spans 21:00->21:00 and its
                        label is NOT the calendar day it mostly covers.

USAGE

    from phtime import te_pht, bar_pht, containing_bar, describe

    te_pht('2026-09-07', '11:50 PM')      -> aware datetime, PHT
    bar_pht(1788822000)                   -> aware datetime, PHT
    containing_bar(rel, bars, 3600)       -> the bar epoch holding a release
    describe(rel)                         -> one line, both zones, for print
"""
import datetime as dt

PHT = dt.timezone(dt.timedelta(hours=8), 'PHT')

# TradingView / OANDA daily bars open here. A "daily" bar is 21:00 -> 21:00
# UTC, which is why its LABEL cannot be trusted as the calendar day (F-106).
OANDA_DAILY_OPEN_UTC = 21


def te_utc(date_str, time_str):
    """A TE calendar row's (date, time) as an aware UTC datetime.

    The stored time is UTC (F-107). Returns None when TE published no time -
    an all-day or unscheduled row - rather than guessing midnight, because a
    guessed time produces a real-looking answer that is wrong.
    """
    if not date_str or not time_str or not str(time_str).strip():
        return None
    s = '%s %s' % (date_str, str(time_str).strip())
    for fmt in ('%Y-%m-%d %I:%M %p', '%Y-%m-%d %H:%M'):
        try:
            return dt.datetime.strptime(s, fmt).replace(tzinfo=dt.UTC)
        except ValueError:
            continue
    return None


def te_pht(date_str, time_str):
    """A TE calendar row's (date, time) in PHT - the zone Jeff reads."""
    u = te_utc(date_str, time_str)
    return u.astimezone(PHT) if u else None


def bar_pht(epoch):
    """A TradingView bar timestamp (its OPEN, UNIX/UTC) in PHT."""
    return dt.datetime.fromtimestamp(int(epoch), PHT)


def bar_utc(epoch):
    return dt.datetime.fromtimestamp(int(epoch), dt.UTC)


def containing_bar(release_epoch, bar_epochs, seconds):
    """The bar that CONTAINS a release - never the one that merely shares a
    label with its date (F-106).

    bar_epochs: the `time` values as returned by data_get_ohlcv.
    seconds:    bar width - 3600 for 60m, 86400 for D.
    Returns the bar's epoch, or None when the release is outside the data.
    """
    r = int(release_epoch)
    for b in sorted(int(x) for x in bar_epochs):
        if b <= r < b + seconds:
            return b
    return None


def describe(epoch_or_dt, label='time'):
    """One line showing BOTH zones, so a wrong one is visible on sight.

    Print this beside any figure derived from a timestamp. F-106 and F-107
    both survived review because only one zone was ever on screen.
    """
    if isinstance(epoch_or_dt, (int, float)):
        u = bar_utc(epoch_or_dt)
    else:
        u = epoch_or_dt.astimezone(dt.UTC)
    p = u.astimezone(PHT)
    return '%s: %s UTC  =  %s PHT' % (
        label, u.strftime('%a %d %b %Y %H:%M'), p.strftime('%a %d %b %Y %H:%M'))


def check(date_str, time_str, expect_pht=None):
    """Print the conversion, and assert it if an expectation is given.

    Used to pin the convention against a row Jeff has read on his own screen.
    """
    u = te_utc(date_str, time_str)
    if u is None:
        print('  TE %s %s -> NO TIME PUBLISHED' % (date_str, time_str))
        return None
    p = u.astimezone(PHT)
    got = p.strftime('%Y-%m-%d %I:%M %p')
    ok = '' if expect_pht is None else (
        '  OK' if got == expect_pht else '  *** MISMATCH, expected %s' % expect_pht)
    print('  TE "%s %s" (UTC) -> %s PHT%s' % (date_str, time_str, got, ok))
    if expect_pht is not None:
        assert got == expect_pht, 'PHT conversion drifted: %s != %s' % (got, expect_pht)
    return p


if __name__ == '__main__':
    print(__doc__.split('USAGE')[0].rstrip())
    print()
    print('SELF-CHECK against rows Jeff verified on his own screen:')
    # JPY GDP Final Q2 - Jeff: "the release was Sept 8 7:50 AM"
    check('2026-09-07', '11:50 PM', '2026-09-08 07:50 AM')
    # AUD GDP Q2 - TE 01:30 AM UTC
    check('2026-09-02', '01:30 AM', '2026-09-02 09:30 AM')
    print()
    print('TradingView bar timestamps are UNIX/UTC and mark the bar OPEN:')
    for e in (1788822000, 1788810000):
        print('  ' + describe(e, 'bar'))
    print()
    print('OANDA daily bars open %02d:00 UTC - a daily LABEL is not a '
          'calendar day (F-106).' % OANDA_DAILY_OPEN_UTC)
