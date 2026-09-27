# -*- coding: utf-8 -*-
"""The WEEK-AHEAD CALIBRATOR - the second half of pair selection (LD-98).

Jeff, 2026-09-04: "In here we are scoring the day not the category. It can
perceive as 'Does USD (for example) is positive or negative on Monday?' We
don't look at it as the usual category separation."

THE DAY IS THE UNIT. One score per currency per day, summed across the week.
There is NO CATEGORY WEIGHT anywhere in this file - weights live only in the
base scoring (fact_tables.py). Two separate scales that meet at the tally:

    FINAL = base (-9 .. +9)  +  calibrator (-5 .. +5)

That bound is deliberate. The week ahead RE-RANKS the board but cannot
overturn it, and a busy day is worth no more than a quiet one - a currency
with four releases on Thursday scores that Thursday ONCE, not four times.
The alternative lets a crowded calendar outvote the macro base by accident.

THE TWO COLLISION RULES (Jeff's own examples):

  RULE 1  same day, DIFFERENT reference months -> the LATEST month wins.
          "EUR have Unemployment Rate JUL and S&P Global Manufacturing PMI
          Final AUG ... we give focus on the PMI for that day."

  RULE 2  same day, SAME reference month -> they SHARE the day, averaged.
          "JPY have S&P Global Manufacturing PMI Final AUG and Consumer
          Confidence AUG since both of them is for AUG month only then the
          score would be (+1+1)/2"

GRADING each row: subject the Cons-Fcst range to that indicator's own macro
criterion, through the SAME channel logic as the base scoring (LD-94) -
unemployment lower-is-better, inflation through the rate channel, everything
else against consensus where TE publishes one and forecast where it does not
(F-85). Direction of goodness is never re-derived here; week_ahead owns it.
"""
import io, os, sys, csv, glob, json, re
import collections
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import week_ahead as wa
from test_pricing import num
import fact_tables as ft

MONTHS = ('jan', 'feb', 'mar', 'apr', 'may', 'jun',
          'jul', 'aug', 'sep', 'oct', 'nov', 'dec')

# The whitelist threshold for each row, so direction survives (F-66/F-68).
def _thresholds():
    import score_model as sm
    out = {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        out[(sm.LABEL[iso], name)] = thr
    return out


THR = _thresholds()


def ref_month(raw_event):
    """The reference month a TE row is FOR, as a sortable key.

    'balance of trade aug' -> (0, 8). 'machinery orders yoy jul' -> (0, 7).
    A quarter ('q2') sorts by its last month. None when nothing is named -
    such a row cannot be compared and never wins RULE 1.
    """
    e = (raw_event or '').lower()
    q = re.search(r'\bq([1-4])\b', e)
    if q:
        return (0, int(q.group(1)) * 3)
    for i, m in enumerate(MONTHS, 1):
        if re.search(r'\b%s\b' % m, e):
            return (0, i)
    return None


def level_test(thr, expected):
    """Grade a LEVEL threshold: does the expected VALUE clear the bar?

    F-92. Jeff, 2026-09-09, on JPY Machine Tool Orders YoY: "This is Good
    because our criteria ... is Actual > 0.5% is Good, < 0% is Bad. Actual
    in between 0.5 - 0 is Neutral."

    The forecast was 43.0% - far above the >0.5% bar - and the calibrator
    scored it -1, because market_pricing() asks whether the series is
    RISING OR FALLING against its last print. 50.4% -> 43.0% is a fall, so
    it graded BAD.

    BUT A FALL FROM 50.4% TO 43.0% IS STILL 43.0%, AND THE RULE IS A LEVEL
    TEST. Deceleration inside a strong band is not weakness by this
    whitelist's own criterion.

    39 of 71 rows carry a level threshold - more than half - so this was
    not an edge case. Returns None for thresholds that are genuinely
    comparative ('>Prev', '>Cons ...'), which market_pricing still owns.

    Forms handled, all of them present in the whitelist:
        '>0.5%'   '>50.5'   '<0%'   '0-0.5%'   '<0 (LD-58)'
    Band forms ('>2% & rising') are mandate rules and stay with the rate
    channel - they need the direction term this function deliberately drops.
    """
    t = (thr or '').strip()
    if not t or expected is None:
        return None
    low = t.lower()
    if 'prev' in low or 'cons' in low or '&' in t or ';' in t:
        return None                      # comparative or compound - not ours

    m = re.match(r'^>\s*(-?[\d.]+)', t)
    if m:
        bar = float(m.group(1))
        # The BAD floor is not always zero. A growth series ('>0.5%') is bad
        # once it turns negative, so the floor is 0 and 0..0.5 is NEUTRAL.
        # A DIFFUSION INDEX ('>50.5') is bad below 50 - the expansion line -
        # so 49.0 is BAD, not NEUTRAL. Using 0 for both graded a contracting
        # PMI as merely unremarkable.
        floor = 50.0 if bar >= 45 else (0.0 if bar > 0 else bar)
        if expected > bar:
            return 'GOOD'
        if expected < floor:
            return 'BAD'
        return 'NEUTRAL'

    m = re.match(r'^<\s*(-?[\d.]+)', t)
    if m:
        bar = float(m.group(1))
        return 'BAD' if expected > bar else 'GOOD'

    m = re.match(r'^(-?[\d.]+)\s*-\s*(-?[\d.]+)', t)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if expected > hi:
            return 'GOOD'
        if expected < lo:
            return 'BAD'
        return 'NEUTRAL'
    return None


# LD-117 - GDP IS SCORED ON THE EXPECTATION RANGE ITSELF.
#
# Jeff, 2026-09-10: "GDP Consensus-Forecast is > 0 is Good ... < 0 is Bad.
# If ... a mix of positive and negative values then Neutral" and, on why:
# "Calibrator is forward looking and by the time we build the report we
# don't have the actual values yet. We're trading the expectations not the
# result."
#
# THIS IS NOT A SURPRISE TEST AND MUST NOT BE TURNED INTO ONE. Every other
# calibrator row asks "will the print beat its reference?". GDP asks "is the
# economy expected to GROW?" - a positive expected range is good for the
# currency whether or not the actual later beats it. That is scorable on
# SUNDAY, which is the whole point: the actual does not exist yet.
#
# QoQ ONLY (LD-116). QoQ and YoY disagree exactly where it matters - NZ
# 17 Sep is QoQ -0.1% BAD against YoY +1.6% GOOD - and YoY is structurally
# almost always positive, which would recreate the defect that got GDP
# thrown out of the base: a category that says GOOD for everyone ranks no
# one.
INFLATION_NAMES = ('Inflation Rate YoY', 'Inflation Rate YoY Final')
RATE_NAME = wa.RATE_NAME          # LD-140
GDP_NAME = 'GDP Growth Rate QoQ'


# LD-146 - A RATE DECISION IS SCORED AGAINST THE CURRENCY'S OWN REGIME.
#
# Jeff, 2026-09-27: "Interest rate decision will overturn everything on that
# day. And since the market moves in expectation, an interest rate hike on a
# weak economy can be perceived as Bad. This is because the market already
# know that the effect of this hike will bring down inflation so they will
# already priced in weeks before."
#
# *** THIS IS A CALIBRATOR RULE ONLY. Jeff, same session: "this is only for
# the calibrator just to be clear." rate_model's LEVEL term in the base is
# untouched by LD-146 and keeps scoring the 1.5-2.5 corridor exactly as
# LD-142 set it. The two are different questions about the same decision:
#
#     BASE (LD-142)      WHERE IS THE RATE?   level vs the corridor
#     CALIBRATOR (LD-146) DOES THE EXPECTED MOVE FIT THE REGIME?
#
# So a decision is scored twice, but never for the same reason - which is
# what LD-142's "one rule, one quantity" was protecting against. LD-142
# retired LD-140's SURPRISE test (cons vs standing). LD-146 does not bring
# it back: the move direction is only half the input, and the regime it
# lands in decides the sign.
#
# THE REGIME IS THE BASE BAND, NOT THE FINAL BAND. Jeff: "based on the
# currency's regime (based on the base score)". This is not a detail - the
# FINAL band already contains the calibrator, so reading it here would let
# the calibrator score itself. The base band is settled before this file
# runs. On 28 Sep-2 Oct the two disagree on three of eight currencies
# (CHF STRONG->NEUTRAL, JPY NEUTRAL->STRONG, USD NEUTRAL->WEAK), so the
# distinction changes answers rather than being cosmetic.
#
# THE SIX CASES, in Jeff's words:
#
#     HIKE    + weak or neutral   -> BAD    hiking into weakness
#     HIKE    + strong            -> GOOD   hiking from strength
#     HOLD    + strong or neutral -> GOOD   no pressure to move
#     HOLD    + weak              -> BAD    cannot afford to move
#     CUT     + weak              -> GOOD   relief where it is needed
#     CUT     + strong or neutral -> BAD    cutting away an advantage
#
# NEUTRAL SPLITS ACROSS THE THREE MOVES and that asymmetry is the rule's
# content, not an oversight: a neutral currency is scored BAD on a hike,
# GOOD on a hold, BAD on a cut. Only standing still is rewarded. There is
# no case that returns 0 - every combination commits.
HIKE, HOLD, CUT = 'HIKE', 'HOLD', 'CUT'

REGIME_RATE = {
    (HIKE, 'STRONG'): 1, (HIKE, 'NEUTRAL'): -1, (HIKE, 'WEAK'): -1,
    (HOLD, 'STRONG'): 1, (HOLD, 'NEUTRAL'): 1, (HOLD, 'WEAK'): -1,
    (CUT, 'STRONG'): -1, (CUT, 'NEUTRAL'): -1, (CUT, 'WEAK'): 1,
}


def rate_move(cons, fcst, prev):
    """HIKE / HOLD / CUT from the EXPECTED rate against the standing one.

    The expectation is cons where TE publishes one, else fcst (F-85). `prev`
    is the standing rate. Returns None when either side is unreadable - a
    missing expectation must not silently read as HOLD, which would score
    a currency on an absence (the F-73 shape).

    Uses rate_model._num so '3.50-3.75%' reads 3.75 and a leading minus is
    not lost to a currency mark (F-124).
    """
    import rate_model as rm
    exp = cons if (cons or '').strip() else fcst
    a, b = rm._num(exp), rm._num(prev)
    if a is None or b is None:
        return None
    if a > b:
        return HIKE
    if a < b:
        return CUT
    return HOLD


def rate_score(ccy, cons, fcst, prev, base_band):
    """LD-146 - (score, move, regime) or (None, move, regime).

    `base_band` is {ccy: 'STRONG'|'NEUTRAL'|'WEAK'} from the BASE scores.
    """
    mv = rate_move(cons, fcst, prev)
    rg = (base_band or {}).get(ccy)
    if mv is None or rg is None:
        return None, mv, rg
    return REGIME_RATE.get((mv, rg)), mv, rg


def gdp_score(lo, hi):
    """Jeff's range rule. Both bounds positive GOOD, both negative BAD,
    straddling zero NEUTRAL."""
    if lo is None or hi is None:
        return None
    if lo > 0:
        return 1
    if hi < 0:
        return -1
    return 0



def score_row(ccy, name, rec, base_band=None):
    """+1 / 0 / -1 for one scheduled row, or None if unscorable.

    Grades WHAT IS EXPECTED TO PRINT against that indicator's own criterion.

    TWO KINDS OF THRESHOLD, and they ask different questions (F-92):

      LEVEL       '>0.5%', '>50.5', '<0%', '0-0.5%' - does the expected
                  VALUE clear the bar? A fall from 50.4% to 43.0% is still
                  43.0%, and 43.0% > 0.5% is GOOD.

      COMPARATIVE '>Prev', '>Cons ...' - is the expected print better than
                  the reference? Only here does direction of change decide,
                  and market_pricing() owns it with all its channel logic
                  (F-66/F-68/F-70).
    """
    prev = num(rec.get('previous'))
    cons = num(rec.get('consensus'))
    fcst = num(rec.get('forecast'))
    if cons is None:
        cons = fcst            # F-85: forecast is the documented fallback
    if cons is None:
        return None
    if prev is None and name != GDP_NAME:
        return None          # LD-117: GDP needs no previous, only the range

    hi = cons if fcst is None else max(cons, fcst)
    lo = cons if fcst is None else min(cons, fcst)

    # LD-140 - A RATE DECISION SCORES ITS SURPRISE, IN BASIS POINTS.
    #
    #     actual > consensus  -> +1   hawkish surprise
    #     actual = consensus  ->  0   fully priced (LD-90)
    #     actual < consensus  -> -1   dovish surprise
    #
    # LD-90 IS HONOURED, NOT WEAKENED. A decision landing exactly on
    # consensus scores ZERO, because the market already holds it. Every
    # September 2026 decision did exactly that - Fed 4.00% vs 4.00%, BoE
    # 3.75% vs 3.75%, BoJ 1.25% vs 1.25% - which is why this rule would NOT
    # have rescued the 14-18 Sep board. That was stated in the proposal
    # before approval rather than discovered afterwards.
    #
    # BEFORE THE RELEASE there is no actual, so the row scores on the
    # EXPECTED move instead: consensus vs the standing rate (`prev`). A hike
    # that is fully priced still scores 0 - the currency already holds it.
    if name == RATE_NAME:
        # *** LD-146 SUPERSEDES THE 'return None' THAT STOOD HERE.
        #
        # LD-142 retired LD-140's surprise test and left the calibrator
        # scoring a rate decision NOTHING. That had a consequence nobody
        # chose: a None score is filtered out by day_score() before the
        # precedence check can see it, so on 29 Sep 2026 AUD Household
        # Spending YoY CARRIED THE RBA's DAY while the decision itself was
        # dropped as unscorable. The comment here promised the row "keeps
        # its day precedence"; the code did the opposite for six days.
        #
        # LD-146 scores it against the currency's BASE regime. See the
        # REGIME_RATE table above for the six cases.
        return rate_score(ccy, (rec or {}).get('consensus'),
                          (rec or {}).get('forecast'),
                          (rec or {}).get('previous'), base_band)[0]

    # LD-117: GDP scores the RANGE, not a threshold and not a surprise.
    if name == GDP_NAME:
        return gdp_score(lo, hi)

    thr = THR.get((ccy, name))
    # the expected print is the midpoint of the cons-fcst range
    expected = (hi + lo) / 2.0

    # LD-136 IN THE CALIBRATOR TOO.
    #
    # Jeff, 2026-09-14, on CAD Inflation Rate YoY landing Mon 14 20:30 PHT:
    # "We should apply the new scoring now for the calibrator news events"
    #
    # LD-136 reached the BASE via derive_scores and stopped there. The
    # calibrator has its own scorer, and an inflation row arriving here hit
    # level_test() with the threshold string 'vs 2% target & Prev', got None,
    # and fell through to market_pricing() - which grades a SURPRISE vs
    # consensus, a different question entirely.
    #
    #     CAD expects 3.0% after 3.0%. No surprise, so market_pricing
    #     said NEUTRAL. Under LD-136 flat ABOVE TARGET is GOOD - the
    #     bank has not won yet. The base and the calibrator disagreed
    #     about the same rule on the same currency in the same edition.
    #
    # ONE RULE, ONE IMPLEMENTATION. The calibrator asks it of the EXPECTED
    # print rather than a released one - that is the only difference, and it
    # is the calibrator's whole nature (Jeff: "we're trading the expectations
    # not the result"). Calling derive_scores keeps a second copy of the rule
    # from drifting, which is exactly how F-120 happened.
    if name in INFLATION_NAMES:
        import derive_scores as _ds
        sc = _ds.inflation_score('%s' % expected, '%s' % prev)
        if sc is not None:
            return sc

    v = level_test(thr, expected)
    if v is None:
        v = wa.market_pricing(prev, cons, fcst, name=name,
                              threshold=thr, ccy=ccy)
    return {'GOOD': 1, 'NEUTRAL': 0, 'BAD': -1}.get(v)


def _date_only(s):
    """TE's date string -> a date, or None (LD-133).

    Used when a row has a DATE but no TIME. No timezone shift is applied:
    with no clock there is nothing to convert, and inventing a time to
    convert would be F-107's shape - a guessed value that looks real. TE
    dates its untimed rows by the local session they belong to.
    """
    try:
        y, m, d = (int(x) for x in str(s).split('-'))
        return dt.date(y, m, d)
    except Exception:
        return None


def week_rows(capture, start, end, base_band=None):
    """Every whitelist row in the window, with its score and reference month."""
    raw = json.load(io.open(capture, encoding='utf-8'))
    ISO = {'US': 'USD', 'GB': 'GBP', 'EA': 'EUR', 'JP': 'JPY',
           'CH': 'CHF', 'CA': 'CAD', 'AU': 'AUD', 'NZ': 'NZD'}
    idx = {}
    for r in raw:
        if r['iso'] in ISO:
            idx[(r['date'], ISO[r['iso']], r['event'])] = r

    timed, untimed = wa.whitelist_events(capture, start, end)
    out = []
    for when, ccy, name, rawev, d in list(timed) + list(untimed):
        rec = idx.get((d, ccy, rawev), {})
        # LD-133 - A ROW WITH A DATE BUT NO TIME STILL HAS A DAY.
        # Jeff, 2026-09-13, on NZD Global Dairy Trade: "release date is Sept
        # 15 but no time yet. let's put it to Sept 15 Tuesday even without
        # time we're looking at the Day result anyway."
        #
        # `day` was derived from `when`, which only exists when TE publishes
        # a TIME. So a row TE had dated 2026-09-15 fell out of the calibrator
        # entirely - day None means it joins no day group and scores nothing.
        # THE DAY IS THE UNIT (LD-98), and the day was known all along.
        #
        # The date comes from TE's own row (`d`), so this is not an
        # assumption - it is the field we were already ignoring. A row with
        # NEITHER date nor time still yields None and is published as such.
        _day = when.date() if when else _date_only(d)
        out.append(dict(when=when, ccy=ccy, name=name, raw=rawev,
                        day=_day,
                        month=ref_month(rawev), score=score_row(ccy, name, rec, base_band),
                        cons=(rec.get('consensus') or '').strip(),
                        fcst=(rec.get('forecast') or '').strip(),
                        prev=(rec.get('previous') or '').strip()))
    return out


def day_score(rows):
    """One score for one currency on one day (LD-98 rules 1 and 2).

    Returns (score, rule, kept, dropped). Rows that cannot be scored drop
    out entirely - they are NOT counted as 0, which would dilute the day
    toward neutral on an absence (the F-73 shape).

    RULE 1a - A GAP IN LD-98, DECIDED HERE AND FLAGGED. Jeff's rule says the
    latest reference month wins the day. It does not say what happens when
    THE LATEST ROW IS UNSCORABLE and an earlier one is not - which is live
    on JPY, Wed 16 Sep: Balance of Trade AUG has no previous or consensus,
    while Machinery Orders YoY JUL scores -1.

    THE CHOICE MADE: precedence runs over SCORABLE rows only, so the JUL row
    carries the day. The alternative - the unscorable AUG row wins and
    blanks the day - throws away a real signal to honour a row that carries
    none. But it IS a choice, and Jeff has not ratified it.
    LD-119 - OPTION B WAS TAKEN BACK. Jeff, 2026-09-10: "I'm taking back
    the B decision. Let's keep the prioritization rule intact. So if GDP
    release date have other Indicator release which have more latest data
    then we still focus on that one Rather than the GDP."

    So GDP is an ORDINARY calibrator row. It enters the whitelist, it is
    scored by its own range rule (LD-117), and then it competes on
    reference month like everything else - a quarter ends in June, so any
    JUL or AUG row outranks it.

    THE MEASURED CONSEQUENCE, and a correction to my own earlier figure.
    I told Jeff GDP would survive Rule 1 on "1 of 5" release days. That
    counted EVERY TE calendar row, including crude oil stocks and car
    production - rows not on the whitelist, which never compete. Rule 1
    ranks WHITELIST rows only.

    Measured properly: GDP survives on 4 of 5 whitelist days.

        EUR Mon 07 Sep   +1  kept, alone on the day
        JPY Tue 08 Sep   +1  kept, alone on the day
        NZD Thu 17 Sep   -1  kept, alone on the day
        GBP Wed 30 Sep   +1  kept, alone on the day
        USD Wed 30 Sep   +1  DROPPED - Personal Spending MoM AUG (0)
                             outranks Q2, so the day scores 0.00

    The drop is the rule working as Jeff specified, not a defect. He wants
    a week of it before changing anything: "We'll do this first then let's
    see what will happen next week."
    """
    scored = [r for r in rows if r['score'] is not None]
    if not scored:
        return None, 'unscorable', [], list(rows)

    # LD-140 - AN INTEREST RATE DECISION WINS ITS DAY OUTRIGHT.
    #
    # Jeff, 2026-09-19, choosing the narrowest of two forms offered: RATE
    # ONLY. GDP keeps competing on reference month exactly as LD-119 says -
    # "if GDP release date have other Indicator release which have more
    # latest data then we still focus on that one Rather than the GDP."
    #
    # *** THIS IS THE FIRST EXCEPTION TO LD-98 ("the day is the unit, no
    # weights") AND IT IS A REAL CONTRADICTION, NOT AN EXTENSION.
    #
    # The justification is NOT that rate decisions are more important in the
    # abstract - that reasoning produced LD-113 (GDP weighted in the base)
    # and was withdrawn in a day for ranking nothing. It is that a rate
    # decision SETS THE PRICE OF THE CURRENCY ITSELF, which is the quantity
    # the board is trying to rank. Every other row is evidence ABOUT where
    # that price is heading.
    #
    # WITHDRAWAL CONDITION, recorded with the rule: if this ranks nothing by
    # the 21-25 Sep retrospective, it comes out. LD-113 is the precedent.
    # LD-146 - THE RATE ROW NOW ALWAYS CARRIES A SCORE, so this check is
    # reachable again. Under LD-142 it scored None, was filtered out by the
    # `scored` comprehension above, and never reached here - which is how
    # Household Spending came to carry the RBA's day on 29 Sep 2026.
    rate = [r for r in scored if r['name'] == RATE_NAME]
    if rate:
        val = sum(r['score'] for r in rate) / float(len(rate))
        return (val, 'rate decision' if len(rate) == 1 else 'rate shared',
                rate, [r for r in rows if r not in rate])

    dated = [r for r in scored if r['month'] is not None]
    if dated:
        top = max(r['month'] for r in dated)
        latest = [r for r in dated if r['month'] == top]
        undated = [r for r in scored if r['month'] is None]
        if len(latest) < len(dated) or undated:
            # RULE 1 - a later month supersedes; undated rows never win
            keep = latest
            rule = 'latest month'
        else:
            keep = latest
            rule = 'shared' if len(keep) > 1 else 'single'
    else:
        keep = scored
        rule = 'shared' if len(keep) > 1 else 'single'
    if len(keep) > 1:
        rule = 'shared'
    val = sum(r['score'] for r in keep) / float(len(keep))
    drop = [r for r in rows if r not in keep]
    return val, rule, keep, drop


# LD-144 - A DAY IS WORTH 0.2, NOT 1.0.
#
# Jeff, 2026-09-27: "I think the 1 point score per day is moving the ranking
# too much. Let's change it to 0.2 per day for our next iteration."
#
# A currency with three scoring days could swing +/-3.00 against a base that
# spans -9..+9, so one busy calendar week could move a currency a third of
# the board's full range on expectations alone. The 21-25 Sep edition is the
# case: the base ranked at +0.29 against realised strength and the FINAL at
# +0.12 - the calibrator (-0.29) actively pulled a ranking board down.
#
# THE DAY IS STILL THE UNIT (LD-98). This changes only what a day is WORTH.
# Rule 1 (latest reference month wins the day), rule 2 (same month shares it)
# and LD-140's rate precedence are all untouched - day_score() is not
# modified. Only the running total is scaled.
DAY_WEIGHT = 0.2


def calibrate(capture, start, end, base_band=None):
    """{ccy: {'total', 'days': {date: (score, rule, kept, dropped)}}}.

    `days` holds the RAW per-day score (+1/0/-1) so the page can show what
    each day said; `total` is the LD-144-weighted sum.
    """
    if base_band is None:
        # LD-146 needs the BASE regime, never the final one - the final band
        # already contains the calibrator, so reading it here would let the
        # calibrator score itself.
        _b = ft.base_scores()
        base_band = ft.bands(
            dict((c, _b[c]['total']) for c in _b))[0]
    rows = week_rows(capture, start, end, base_band)
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r['day'] is not None:
            by[r['ccy']][r['day']].append(r)
    out = {}
    for c in ft.CCYS:
        days = {}
        tot = 0.0
        for d, rs in sorted(by.get(c, {}).items()):
            val, rule, keep, drop = day_score(rs)
            if val is None:
                continue
            days[d] = (val, rule, keep, drop)
            tot += val * DAY_WEIGHT
        out[c] = {'total': tot, 'days': days}
    return out


if __name__ == '__main__':
    cap = sorted(glob.glob(os.path.join(
        REPO, 'data/raw/calendar/*_cal_full.json')))[-1]
    start = sys.argv[1] if len(sys.argv) > 2 else '2026-09-14'
    end = sys.argv[2] if len(sys.argv) > 2 else '2026-09-18'
    print('CALIBRATOR (LD-98)  %s .. %s' % (start, end))
    print('capture: %s' % os.path.basename(cap))
    print()
    res = calibrate(cap, start, end)
    for c in sorted(res, key=lambda x: -res[x]['total']):
        d = res[c]
        if not d['days']:
            print('  %-4s  %+5.2f   (no scheduled rows)' % (c, d['total']))
            continue
        print('  %-4s  %+5.2f' % (c, d['total']))
        for day, (val, rule, keep, drop) in sorted(d['days'].items()):
            names = ', '.join('%s %+d' % (r['name'][:26], r['score'])
                              for r in keep)
            print('        %s  %+5.2f  [%s]  %s'
                  % (day.strftime('%a %d'), val, rule, names))
            for r in drop:
                why = ('unscorable' if r['score'] is None
                       else 'superseded by a later month')
                print('              dropped: %-28s (%s)'
                      % (r['name'][:28], why))
