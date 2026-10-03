# -*- coding: utf-8 -*-
"""GRADE A BIAS BY WHETHER IT REACHED A TYPICAL DAY'S RANGE (LD-128).

Jeff, 2026-09-13:

    "to really determine if the market really favors our bias is not by the
     closing price of each day. Instead we need to determine first what is
     the average daily pips movement of each pairs each day. Then if we hit
     that for the day in our bias then it's already a win. Because if the
     market just reversed then it would mean that should have already Taken
     profit already. A trader will not wait for a market reversal before
     closing the trade."

WHY CLOSE-TO-CLOSE IS THE WRONG YARDSTICK, and he is right about this. A
read that runs 117 pips your way and finishes at +48 is graded a partial
win by the close, when the market in fact did everything the read asked of
it. Nobody watches a move reach a typical day's range and then sits through
the reversal. The close measures WHEN YOU STOPPED LOOKING, not whether the
bias described the day.

    EURAUD  reached +117.4 on Thursday and closed the week at +48.6
    EURUSD  never exceeded +30.6 on any day and closed -14.1

Both look like "one win, one loss" on the close. Only one of them had a day
where the market moved a full session's worth in the direction of the read.

*** THE SCOPE LINE, AND IT MATTERS HERE (LD-4). ***

This module computes an OBSERVATION - how far a pair typically travels in a
session, and whether the bias covered that distance. It does NOT set a
target, an entry, an exit or a stop, and nothing here instructs a trade.
"Did the move reach a typical day's range" is a question about the READ.
"Take profit at one ATR" would be a question about the TRADE, and that
sentence does not get written in this repo.

METHOD

  ATR(14) from the sessions ENDING BEFORE the week being graded. Using the
  graded week's own bars to set its benchmark is hindsight - the same shape
  as F-83 and the CHF vintage error: a week cannot be scored against a
  yardstick built from its own outcome.

  For each session, the FAVOURABLE EXCURSION is measured from THAT DAY'S
  OPEN, not from Monday's. A bias is a claim about direction that stands
  each day it is held, and a pair already 100 pips onside should not be
  credited a second time for the same distance.

  A day where favourable excursion >= 1.0 ATR is a day the market delivered
  a full session's travel in the direction of the read.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


# LD-129 - THE TARGET IS 0.75 ATR. Jeff, 2026-09-13: "let's set to 0.75 ATR
# target for now."
#
# WHY NOT 1.0. A full ATR in ONE session is a demanding bar - it asks the day
# to deliver its entire typical range in a single direction. On the 7-11 Sep
# week, 1.0 graded 2 of 4 and left AUDCHF at 0.90x, three and a half pips
# short of a day it had effectively earned. At 0.75 it is 3 of 4.
#
# WHY NOT LOWER. 0.50 graded 4 of 4 that week - every bias "won", which makes
# the measure useless. A yardstick that never fails is not measuring.
#
# *** THIS IS A DAY TARGET, NOT A SWING TARGET. *** Jeff read 0.75 as "closer
# to Swing, the middle ground". It is not, and the distinction matters for how
# the grade is read. 0.75 of a DAILY range is BY CONSTRUCTION a day-sized move,
# and the tape agrees: on 7-11 Sep all three winners reached it WITHIN A SINGLE
# SESSION, measured from that session's own open. None needed a multi-day hold.
#
# For contrast, a genuinely swing-sized target - 0.75 of a WEEKLY range, taking
# the standard sqrt(5) scaling - is roughly 2.2x larger:
#
#     EURUSD   day 35 pips    swing ~78
#     AUDJPY   day 59 pips    swing ~132
#
# So the grade answers "did the bias deliver a normal day's travel", which is
# the right question for an intraday trader. It does NOT answer "would a swing
# hold have paid", and must not be read as though it did.
TARGET = 0.75


def pip_factor(pair):
    """JPY crosses quote to 3 decimals; everything else to 5."""
    return 100 if pair.endswith('JPY') else 10000


def atr(bars, n=14, factor=10000):
    """ATR(n) in pips from [(high, low, close)], oldest first.

    True range is max(H-L, |H-prevC|, |L-prevC|) - the gap-inclusive range,
    so an overnight jump counts as travel the session actually covered.
    Needs n+1 bars; uses the last n true ranges available.
    """
    if len(bars) < 2:
        return None
    trs = []
    for i in range(1, len(bars)):
        h, l, c = bars[i]
        pc = bars[i - 1][2]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)) * factor)
    trs = trs[-n:]
    return sum(trs) / len(trs) if trs else None


def grade_day(bias, day_open, high, low, factor, atr_pips, target=TARGET):
    """(favourable, adverse, fraction_of_atr, hit) for one session.

    Both excursions are measured from THAT DAY'S OPEN and returned as
    positive pip counts - favourable is distance travelled the way the bias
    points, adverse is distance travelled against it.
    """
    if bias == 'LONG':
        fav, adv = (high - day_open) * factor, (day_open - low) * factor
    else:
        fav, adv = (day_open - low) * factor, (high - day_open) * factor
    frac = (fav / atr_pips) if atr_pips else 0.0
    return fav, adv, frac, frac >= target


# LD-148 - THE ADVERSE SIDE IS GRADED AGAINST THE SAME TARGET.
#
# Jeff, 2026-10-03: "if our target is 59 pips then we should know if it
# reaches 59 on the low side. If it hits the opposite side and just reversed
# it does not automatically mean bad but its a sign that the bias is weakening
# or struggling. We can have more insight using that."
#
# THE ADVERSE EXCURSION WAS ALREADY COMPUTED AND THROWN AWAY. grade_day has
# returned `adv` since LD-128 and every renderer dropped it, so the grid could
# not tell a session that drifted our way from one that was beaten back:
#
#     GBPAUD Mon 28   fav 0.56x   adv 0.52x   -> leaned our way, finished nothing
#     GBPUSD Tue 29   fav 0.01x   adv 0.86x   -> ran a full day AGAINST us
#
# Both rendered as an identical blank cell. That is the defect this closes.
#
# FIVE STATES, one target, both directions:
#
#     CLEAN     fav >= target, adv < target    delivered, never threatened
#     EARNED    fav >= target, adv >= target   delivered through a real fight
#     BEATEN    fav < target,  adv >= target   the OPPOSITE side paid out
#     DRIFT     fav < target,  adv < target    neither side completed
#
# *** BEATEN IS NOT A LOSS AND THE NAMING MATTERS. Jeff: "it does not
# automatically mean bad but its a sign that the bias is weakening". A session
# that runs a full ATR against us and closes back near the open told us
# something real - the bias is being contested - without the week being wrong.
# Calling it LOSS would collapse exactly the distinction this rule exists to
# surface.
#
# THE WEEK VERDICT IS UNCHANGED (LD-128): a pair wins if any session reaches
# target on the favourable side. LD-148 adds a SECOND, independent reading -
# how hard the week fought back - and never overrides the first.
# LD-149 - THE WEEK VERDICT IS THE RATIO OF SUMMED EXCURSIONS.
#
# Jeff, 2026-10-03: "Our current criteria LD-128 'a pair wins if any session
# reaches target on the favourable side' is too forgiving. If we add all days
# high vs all days low then we can really tell if the pair has won or loss
# that week."
#
# HE IS RIGHT, AND THE NUMBER IS WORSE THAN THE HUNCH. Measured over 3192
# pair-weeks - 28 pairs, a year of OANDA daily bars, every week graded in BOTH
# directions - LD-128's "any session reaches target" fires on 69% OF RANDOM
# PAIR-WEEKS. A verdict that calls seven coin-flips in ten a WIN is measuring
# that markets move, not that the bias was right.
#
#     WEEK_RATIO = sum(favourable excursions) / sum(adverse excursions)
#
# Both sums are over the five sessions, each measured from THAT session's own
# open (LD-128's measurement rule is untouched - only the VERDICT changes).
#
# *** THE RATIO, NOT THE NET. Net pips are not comparable across pairs: a
# GBPAUD week (ATR ~79) and a GBPUSD week (ATR ~64) producing the same net
# are not the same result. The ratio is unitless, and its pooled median over
# 3192 weeks is EXACTLY 1.000 - which is the sanity check that grading both
# directions makes the null symmetric by construction.
#
# THE BANDS ARE MEASURED, NOT CHOSEN. I first proposed 0.80/1.20 by eye and
# Jeff asked how I arrived at them. I had not - they were round numbers. The
# distribution says otherwise:
#
#     RATIO BAND      N     % CLOSED POSITIVE    MEDIAN CLOSE
#     < 0.60         738           1%              -96.5
#     0.60 - 0.70    235           9%              -47.7
#     0.70 - 0.80    223          17%              -30.1     <- belongs with LOSS
#     0.80 - 0.90    204          27%              -23.8
#     0.90 - 1.00    196          46%               -5.5
#     1.00 - 1.10    179          53%               +4.9
#     1.10 - 1.20    142          68%              +18.7
#     1.20 - 1.30    140          78%              +24.9     <- 1.20 is too generous
#     1.30 - 1.40    125          86%              +31.6
#     1.40 - 1.60    219          89%              +43.7
#     > 1.60         791          99%              +90.1
#
# Monotonic across all eleven bands, no reversals.
#
# OUT-OF-SAMPLE: fitted on the first half of the year, scored on the second.
# WIN 97.1% positive, LOSS 2.6% positive, CONTESTED 48.8% - matching in-sample
# within a point. The thresholds hold on data they never saw, which is the
# check my first (in-sample, one-pair) 97% figure could not make.
#
# THE ASYMMETRY IS REAL AND IS NOT ROUNDED AWAY. 0.70 on the downside, 1.40 on
# the upside. Tidying them to 0.80/1.20 costs accuracy in both directions.
#
# *** CONTESTED IS A RESULT, NOT A FAILURE TO DECIDE. At 48.8% positive it is
# an honest "this week carried no information", which beats a WIN label that is
# wrong one time in five.
#
# LD-128 IS NOT REPEALED - IT IS DEMOTED. "Did any session hand us a complete
# day" is still worth knowing and still published beside the verdict: a pair
# can post a 1.3x ratio from five mediocre sessions without ever offering a
# clean one, and those are different weeks.
#
# WITHDRAWAL CONDITION, recorded with the rule: if by the 31 Oct retrospective
# the CONTESTED band is catching nearly everything or nearly nothing, the
# boundaries move. One year is one regime (2025-26), weeks overlap across
# pairs sharing a leg, and the bands are fitted to the CLOSE - so this
# validates "does the ratio describe the week", never "does the board predict
# the ratio".
LOSS_AT, WIN_AT = 0.70, 1.40

# the measured sample behind the bands, so the page can cite it
CALIB = {'pair_weeks': 3192, 'pairs': 28, 'window': '2025-08-28..2026-09-28',
         'oos_win_pos': 97.1, 'oos_loss_pos': 2.6, 'oos_contested_pos': 48.8,
         'ld128_fires_on_random': 69}


def week_ratio(rows):
    """sum(favourable) / sum(adverse) over grade_week's rows, or None."""
    sf = sum(r[1] for r in rows)
    sa = sum(r[2] for r in rows)
    return (sf / sa) if sa > 0 else None


def verdict(rows):
    """('WIN'|'CONTESTED'|'LOSS'|None, ratio) for a week (LD-149)."""
    r = week_ratio(rows)
    if r is None:
        return None, None
    if r >= WIN_AT:
        return 'WIN', r
    if r < LOSS_AT:
        return 'LOSS', r
    return 'CONTESTED', r


def classify(fav, adv, atr_pips, target=TARGET):
    """'CLEAN' | 'EARNED' | 'BEATEN' | 'DRIFT' for one session."""
    if not atr_pips:
        return 'DRIFT'
    f, a = fav / atr_pips, adv / atr_pips
    if f >= target:
        return 'EARNED' if a >= target else 'CLEAN'
    return 'BEATEN' if a >= target else 'DRIFT'


def pressure(rows, atr_pips, target=TARGET):
    """(clean, earned, beaten, drift, worst_adverse_fraction) for a week.

    `rows` is grade_week's output: [(label, fav, adv, frac, hit)].
    """
    n = {'CLEAN': 0, 'EARNED': 0, 'BEATEN': 0, 'DRIFT': 0}
    worst = 0.0
    for _, fav, adv, _, _ in rows:
        n[classify(fav, adv, atr_pips, target)] += 1
        worst = max(worst, (adv / atr_pips) if atr_pips else 0.0)
    return n['CLEAN'], n['EARNED'], n['BEATEN'], n['DRIFT'], worst


def grade_week(pair, bias, week_bars, atr_pips, target=TARGET):
    """[(label, fav, adv, frac, hit)] plus a week verdict.

    week_bars: [(label, open, high, low)] in session order.
    Returns (rows, hit_any, best_fraction).
    """
    f = pip_factor(pair)
    rows = []
    for label, o, h, l in week_bars:
        fav, adv, frac, hit = grade_day(bias, o, h, l, f, atr_pips, target)
        rows.append((label, fav, adv, frac, hit))
    best = max((r[3] for r in rows), default=0.0)
    return rows, any(r[4] for r in rows), best


def report(pair, bias, gap, week_bars, atr_pips, target=TARGET):
    rows, hit, best = grade_week(pair, bias, week_bars, atr_pips, target)
    print('%-8s %-6s gap %+5.2f   ATR(14) %.0f pips   target %.2f ATR'
          % (pair, bias, gap, atr_pips, target))
    print('   %-8s %11s %11s %9s   %s'
          % ('SESSION', 'FAVOURABLE', 'ADVERSE', 'OF ATR', ''))
    for label, fav, adv, frac, h in rows:
        print('   %-8s %+11.1f %11.1f %8.2fx   %s'
              % (label, fav, adv, frac, 'REACHED' if h else ''))
    print('   -> %s   (best day %.2f x ATR)'
          % ('WIN - the market delivered a full session in our direction'
             if hit else 'no session reached a typical day\'s range', best))
    return hit, best


if __name__ == '__main__':
    print(__doc__.split('METHOD')[0].rstrip())
    print()
    print('Bars come from a TradingView read at review time - this module')
    print('owns the METHOD, never stored prices.')
