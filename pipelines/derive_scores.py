# -*- coding: utf-8 -*-
"""ACTUALS in, SCORES out (LD-112).

Jeff, 2026-09-09:

    "I noticed that you were putting category scores in our CSV rather than
     the Actual scores of these indicators. I would say we need to store the
     actuals not our scores in them. If you want you can create a separate
     CSV for your scoring."

HE FOUND THE ROOT CAUSE OF THREE FINDINGS. F-91, F-94 and F-95 were all the
same failure: a release had to be written into TWO places - the ACTUAL into
score_model.ROWS, the VERDICT into the fact table - and nothing kept them in
step. R-37 exists ONLY to compare those two copies. Store the actual ONCE
and derive the verdict, and the whole class of bug stops being possible.

    data/macro_indicators/*.csv   ACTUALS, as published.  SOURCE OF TRUTH.
    data/derived/scores.csv       +1/0/-1, DERIVED.       NEVER hand-edited.

WHY THE THRESHOLD ALONE CANNOT GRADE A ROW. '>Prev' says which comparison
to make, never which direction is GOOD - lower unemployment is good, a lower
trade balance is not (F-70: two channels, opposite signs). score_model's
VERDICT column carries that polarity and Jeff has curated it row by row
(LD-57, LD-58, LD-59). So the derivation is:

    actual (fact table)  x  threshold + polarity (score_model)  ->  score

That is still ONE authority per fact. The actual lives in exactly one place;
the RULE lives in exactly one place; neither is a copy of the other.
"""
import io, os, csv, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fact_tables as ft
import score_model as sm

OUT = os.path.join(REPO, 'data', 'derived', 'scores.csv')

# LD-113 - the GDP rule, in Jeff's words 2026-09-09:
#   "Actual > 0.5% is Good, < 0% is Bad. Actual in between 0.5 - 0 is Neutral"
GDP_THRESHOLD = '>0.5%'


def _rule(ccy, indicator):
    """(threshold, verdict, previous) from score_model, or None."""
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        if sm.LABEL[iso] == ccy and name == indicator:
            return thr, v, p
    return None


# *** LD-177 - `previous` COMES FROM OUR OWN TABLE (Jeff, 2026-11-20).
#
# Jeff: "we based it from the data we have captured before. Before we are
# getting data from TE. After this Biquote will populate our tables now.
# Nevertheless we get the previous data from the table itself no matter
# where it came from."
#
# A third of the board is scored `>Prev` - 26 of 78 cells - and `previous`
# used to come from score_model.ROWS, a hand-maintained literal that is a
# THIRD COPY of a number the fact table already holds. On 2026-11-20 it
# agreed with NEITHER the table's prior column NOR TE on 23 of 26 rows.
# CHF Balance of Trade was the worked case: ROWS said CHF5.4B (scoring -1)
# while the table's Oct-26 said CHF1.4B and TE's own previous said CHF1.2B
# (both scoring +1). A number with no source was setting a 4.00-point cell.
#
# MEASURED, NOT ASSUMED. Using TE's own published previous as the referee -
# does our score match the one TE's pair produces? - across the 22 rows
# where TE's previous is readable:
#
#     scored with ROWS.prev    -> agrees with TE on 15 of 22   (68%)
#     scored with the prior column -> agrees on 21 of 22       (95%)
#
# The single residual is EUR Unemployment, and it is NOT an error: TE
# revised August 6.4% -> 6.5%, our Oct-26 column holds August as FIRST
# PUBLISHED, and the two are different vintages of the same month. Jeff's
# rule deliberately holds our own prior, so 21 of 22 is the correct answer
# rather than a near miss.
#
# THE ORDER WAS FORCED AND IT IS WHY THIS COULD NOT SHIP EARLIER. Before
# the Nov-26 advance (F-196), Nov-26 and Oct-26 held the SAME value on 19
# of 26 rows - rows that had never been advanced - so this rule would have
# scored 19 rows 0 against themselves. The advance took that to 3, and all
# three are genuine flat prints (CHF unemployment 3% -> 3%) that correctly
# score 0. Advance first, derive second.
#
# THE COLUMNS ARE EDITION VINTAGES, NOT REFERENCE MONTHS. A print whose ref
# month is Sep/26 sits in the Nov-26 column, because the column says WHEN WE
# HELD IT, not what month it describes. So the prior column is "what this
# row read at the last edition" - exactly the comparison `>Prev` wants, and
# the reason a TE revision does not retroactively rewrite it.
def _prev_cell(cat, ccy, indicator):
    """The PRIOR month's cell for one row, or None if there is no prior.

    None - never a guessed value - when the row, the column or the cell is
    missing, so score_row falls back to ROWS.prev rather than scoring off a
    blank (F-73). A row that cannot be compared is ungraded, not neutral.
    """
    try:
        ms = ft.months()
        if len(ms) < 2:
            return None
        prior = ms[-2]
        for r in ft.load(cat):
            if (r['Currency'].strip() == ccy
                    and r['Indicator'].strip() == indicator):
                v = (r.get(prior) or '').strip()
                return v or None
    except Exception:
        return None
    return None


# *** THE LEGS TRAVEL INSIDE THE CELL (F-195). The Employment Change cell is
# written with its split inline, so the rule that needs three numbers reads
# one cell and no second source:
#
#     -39.3K (FT +34.4K, PT -73.7K)
#
# Both legs or neither. A cell carrying only one is NOT half-parsed into a
# guess: employment_grade() returns None without all three and the row falls
# through ungraded (F-73). Deriving the missing leg by subtraction belongs in
# capture_biquote.derive_part_time(), where it is MARKED as derived -
# computing it silently here would publish an unlabelled derived figure as
# though it were the agency print, which is the F-1 class of error.
_LEG = re.compile(r'\bFT\s*([+-]?[\d.,]+)\s*[KkMm]?.*?'
                  r'\bPT\s*([+-]?[\d.,]+)\s*[KkMm]?', re.S)


def _legs(actual):
    """(full_time, part_time) parsed from the cell, or (None, None)."""
    m = _LEG.search(str(actual or ''))
    if not m:
        return None, None
    return sm._num(m.group(1)), sm._num(m.group(2))


# LD-136 - THE INFLATION RULE IS A TARGET TEST, NOT A DIRECTION TEST.
#
# Jeff, 2026-09-14: "Actual > 2% and Actual >= Previous is Good. Higher chance
# of Interest Rate Hike, Actual > 2% and Actual < Previous is Neutral.
# Probability to hold of the current Interest Rate, Actual < 2% and Actual <=
# Previous is Bad. Higher chance of Interest Rate Cut, Actual < 2% and Actual >
# Previous is Neutral. Probability to hold of the current Interest Rate."
#
# His reasoning, verbatim: "The target inflation is 2%, if the previous
# inflation is above 2% and the latest release shows inflation is not going
# down then it is a hawkish tone. Higher chance of increasing interest rate."
#
#     INFLATION IS SCORED FOR WHAT IT DOES TO THE POLICY RATE,
#     NOT FOR WHETHER IT IS "GOOD FOR THE ECONOMY".
#
# That is why above-target-and-sticky is GOOD for the CURRENCY: it forces the
# central bank hawkish. The old thresholds read ">2% & falling" -> GOOD, which
# scored the ECONOMY's comfort rather than the RATE PATH, and is backwards for
# a currency-strength model.
#
# *** THE EQUALS CASE IS THE POINT OF THE AMENDMENT. Idea_dump already carried
# a near-identical rule using strict > and <. Jeff's amendment moves the
# boundary to >= and <=, and that is precisely the case that prompted it:
# USD CPI printed 3.4% after 3.4%. Flat above target is NOT relief - the bank
# has not won yet - so it reads GOOD, not NEUTRAL. Confirmed by Jeff
# 2026-09-14 when asked which boundary stands.
INFLATION_TARGET = 2.0

# LD-143 - THE 1.5-2.5% CORRIDOR REACHES INFLATION TOO.
#
# Jeff, 2026-09-21, on JPY CPI 1.9% after 1.9%: "This should be Neutral since
# 1.9 is in between 1.5 to 2.5".
#
# LD-136 pivoted on the single 2% POINT, so 1.9% flat read as "below target
# and not rising" -> BAD. But 1.9% is within a rounding error of the mandate;
# calling it a cut risk asserts a precision the number does not carry.
#
# LD-142 had already introduced the corridor for the POLICY RATE a day
# earlier. This makes the two categories use ONE IDENTICAL BAND, which is
# worth more than either rule alone: the same 1.9% now reads the same way
# whether it arrives as a CPI print or as a policy rate.
#
# *** WHAT IT ALSO SILENCES, AND JEFF CHOSE THIS DELIBERATELY. The corridor
# neutralises prints between 2.0 and 2.5 that LD-136 scored:
#
#     CPI 2.4% after 2.1%   GOOD -> NEUTRAL   (rising, but inside)
#     CPI 1.7% after 1.9%   BAD  -> NEUTRAL   (falling, but inside)
#
# Asked whether that was intended, he took the full corridor over a narrower
# "neutral only when flat or moving toward 2%" variant. The band is the
# signal; direction only decides the sign OUTSIDE it.
LOW, HIGH = 1.5, 2.5


# LD-155 - INFLATION IS SCORED LIKE THE RATE PATH: LEVEL FIRST, THEN THE
# SURPRISE OVERRIDES IT (Jeff, 2026-10-10).
#
#   BEFORE THE NEWS                    AFTER THE NEWS
#     expectation > 2.2  -> GOOD         actual = expectation -> retain
#     expectation < 1.8  -> BAD          actual > expectation -> override GOOD
#     1.8 .. 2.2         -> NEUTRAL      actual < expectation -> override BAD
#
# SAME SHAPE AS LD-154, deliberately - Jeff asked for both on the same day and
# the two now read the same way. CONSENSUS SUPERSEDES FORECAST here too
# ("the same with IR we use Consensus over Forecast"), and `src` records which
# number scored the row so a rescore is visible rather than silent.
#
# *** TWO THINGS THIS CHANGES FROM LD-136/LD-143, BOTH DELIBERATE AND BOTH
# CONFIRMED BY JEFF BEFORE BUILDING:
#
#   1. THE CORRIDOR NARROWS, 1.5-2.5 -> 1.8-2.2. Live effect today is ONE row:
#      CHF at 1.0% was NEUTRAL inside 1.5-2.5 and is now BAD below 1.8. Every
#      other currency sits far enough above 2.2 to be unaffected.
#
#   2. THE PREVIOUS PRINT NO LONGER ENTERS IT - LD-136's DIRECTION TEST IS
#      RETIRED. LD-136 (Jeff, 14 Sep) said "if the previous inflation is above
#      2% and the latest release shows inflation is not going down then it is
#      a hawkish tone", so 3.2% after 3.5% scored 0 - above target but FALLING,
#      the bank winning. Under LD-155 that same print scores +1, because only
#      the level is read. Five of eight hand-built test cases flip; none of
#      them is live this month, so this is a quiet change today and a loud one
#      the first time inflation turns.
#
# *** THE OVERRIDE IGNORES THE LEVEL, AND JEFF CONFIRMED THAT IS INTENDED.
# A 1.2% print beating a 1.0% expectation scores GOOD even though 1.2% is
# deflationary by the level test. I raised it explicitly ("a 1.2% print
# beating a 1.0% forecast is still deflationary") and he answered "yes, this
# is intended". The reasoning is the same as the rate path: the market trades
# the SURPRISE, and a hot print is hawkish relative to what was priced
# whatever the absolute level.
#
# COVERAGE NOTE, and it is the same shape as LD-154b. TE publishes an
# inflation consensus only in the RELEASE WEEK, so BEFORE-the-news fires
# roughly one week in four per currency and AFTER-the-news governs the rest.
# The last print carries until the next is scheduled - the standing state,
# not stale data.
#
# *** AND THAT COVERAGE IS WHY INFLATION CANNOT BE GRADED ON SURPRISE SIZE.
# MEASURED 2026-11-03 against data/raw/calendar/2026-11-01_1312PHT, not
# assumed - the note above says "one week in four" and that is exactly the
# number that kills the idea, so it is written here as a count:
#
#     inflation-rate rows in the capture        26
#     carrying a REAL consensus                  4
#     of the 8 YoY rows the board scores         2   (CHF 1.3%, EA flash 3.9%)
#
# Jeff asked on 2026-11-03 why the Score column was blank for inflation
# (F-182), and the obvious answer - give graded() a corridor branch so the
# rows carry a magnitude - was proposed, approved, and then WITHDRAWN TWICE
# on reading the data. Both routes fail, for different reasons:
#
#   1. CORRIDOR DISTANCE reinstates the LEVEL TEST LD-155 RETIRED. Scoring
#      "1.0% is 0.8pp below the floor" is LD-136 wearing a new scale. Jeff
#      settled this on 2026-10-10: a 1.2% print beating a 1.0% expectation
#      scores GOOD though 1.2% is deflationary - "yes, this is intended".
#      The level does not score once an actual exists. The SURPRISE does.
#   2. A CONSENSUS COLUMN IN score_model.ROWS fails LD-23. The surprise is
#      only computable where TE publishes an expectation, which is 2 of 8
#      in a given week, so six currencies would score ±1.00 from the verdict
#      while two scored a magnitude - the same category graded two different
#      ways, ROTATING BY RELEASE CALENDAR rather than by economics. LD-23 is
#      explicit: no input that cannot be sourced for all eight on equal
#      terms. A column that is empty six times out of eight is not an input.
#
# So the 8 inflation rows take the verdict fallback BY DESIGN, not by
# omission, and F-182 was correctly a DISPLAY fix. If this idea returns,
# the question to ask first is not "what scale?" but "what is the consensus
# coverage this week?" - and the answer above is where to start.
NEW_LOW, NEW_HIGH = 1.8, 2.2


def inflation_decision(previous=None, consensus=None, forecast=None,
                       actual=None):
    """LD-155 -> (score, src, label) or (None, None, why).

    `src` is 'consensus', 'forecast' or 'actual'. None when nothing readable -
    never a guessed 0 (F-73).
    """
    exp = sm._num(consensus) if (consensus or '').strip() else         sm._num(forecast)
    src = 'consensus' if (consensus or '').strip() else (
        'forecast' if (forecast or '').strip() else None)
    a = sm._num(actual) if (actual or '').strip() else None

    # with no expectation the actual IS the reading - the level test alone
    if exp is None:
        if a is None:
            return None, None, 'no expectation and no actual'
        exp, src = a, 'actual'

    if exp > NEW_HIGH:
        base, lbl = 1, 'expected %.2f%% above the %.1f ceiling' % (exp, NEW_HIGH)
    elif exp < NEW_LOW:
        base, lbl = -1, 'expected %.2f%% below the %.1f floor' % (exp, NEW_LOW)
    else:
        base, lbl = 0, 'expected %.2f%% inside %.1f-%.1f' % (exp, NEW_LOW, NEW_HIGH)

    if a is None:
        return base, src, 'BEFORE - ' + lbl
    if a > exp:
        return 1, 'actual', 'AFTER - %.2f%% beat the expected %.2f%%, override GOOD' % (a, exp)
    if a < exp:
        return -1, 'actual', 'AFTER - %.2f%% missed the expected %.2f%%, override BAD' % (a, exp)
    return base, 'actual', 'AFTER - %.2f%% exactly as expected, retain' % a


def inflation_score(actual, previous, target=INFLATION_TARGET):
    """LD-136. +1 / 0 / -1 from the print, its previous, and the 2% target.

        above target, not falling   -> +1  hike risk
        above target, falling       ->  0  hold
        below target, not rising    -> -1  cut risk
        below target, rising        ->  0  hold

    Returns None when either side is unreadable - never a guessed 0, so a
    missing previous shows up as ungraded rather than as a neutral verdict.
    """
    a, p = sm._num(actual), sm._num(previous)
    if a is None or p is None:
        return None
    if a > HIGH:
        return 1 if a >= p else 0
    if a < LOW:
        return -1 if a <= p else 0
    # LD-143: inside the corridor, no compulsion either way.
    return 0


def band(actual, thr):
    """LEVEL threshold -> +1 / 0 / -1 (F-92).

    A level test grades WHERE THE PRINT SITS, never which way it moved. The
    three-state band is Jeff's, stated for GDP and applied wherever a
    '>x%' level rule is in force:  above the line GOOD, below zero BAD,
    in between NEUTRAL.
    """
    a = sm._num(actual)
    if a is None:
        return None
    m = re.fullmatch(r'>\s*(\d+\.?\d*)%?', (thr or '').strip())
    if not m:
        return None
    line = float(m.group(1))
    floor = 50.0 if line >= 45 else (0.0 if line > 0 else line)
    if a > line:
        return 1
    if a < floor:
        return -1
    return 0


# LD-137 - A ">Prev" ROW IS COMPUTED, NOT HAND-GRADED.
#
# Jeff, 2026-09-14: "AUD NAB Business Confidence - Why did we score this as
# neutral 0?"
#
# Because nothing computed it. band() cannot parse '>Prev', so every such row
# fell through to a HAND-WRITTEN verdict in the fact table. NAB printed -8
# after -6 - a FALL, plainly BAD under '>Prev' - and sat at NEUTRAL. An audit
# of all 34 Prev-relative rows found a second: CHF Unemployment 3% after 3%
# stored BAD, where Idea_dump says in terms "No change is Neutral".
#
#     34 ROWS WERE GRADED BY EYE. TWO WERE WRONG. NOTHING COULD SEE IT.
#
# Same structural hole as LD-136's inflation rows, and the same fix: state
# the rule in code so the fact table is checkable rather than trusted.
def prev_score(actual, previous, thr):
    """+1 / 0 / -1 for a '>Prev' or '<Prev' threshold, else None.

    Idea_dump is explicit on the boundary, for both directions:
    "Actual > Previous is Good, Actual < Previous is Bad. NO CHANGE IS
    NEUTRAL." A flat print is neutral here - unlike LD-136's inflation rule,
    where flat carries information because it is measured against a TARGET
    rather than against itself.
    """
    t = (thr or '').strip().lower()
    if not (t.startswith('>prev') or t.startswith('<prev')):
        return None
    a, p = sm._num(actual), sm._num(previous)
    if a is None or p is None:
        return None
    if a == p:
        return 0
    up = a > p
    return (1 if up else -1) if t.startswith('>') else (-1 if up else 1)


# ---------------------------------------------------------------- LD-165 ---
# THE BASE NEVER READ A FORWARD CONSENSUS, SO LD-155's BEFORE-THE-NEWS HALF
# ONLY EVER RAN IN THE CALIBRATOR.
#
# Jeff, 2026-10-11: "in the TE calendar some Inflation already have
# consensus/forecast on future dates. they should be now scored according to
# that"
#
# LD-155 is a BEFORE/AFTER rule, exactly like LD-154 for rates. The AFTER half
# reached the base (the level test, from the fact table's actual) and the
# BEFORE half did not - score_row() called inflation_decision(actual=...) and
# nothing else, so every base inflation row reported src='actual' even when a
# consensus for that very series was sitting in the capture.
#
# *** THIS IS F-150 ALL OVER AGAIN, ONE CATEGORY ACROSS. There, LD-154's
# before-the-news half never reached a published edition because nothing in
# the build path called rate_model.load_scheduled(). Same shape here: the rule
# was implemented, tested, and unreachable from the product. A rule that only
# the calibrator applies is not the rule - it is half of it.
#
# SEVEN OF EIGHT CURRENCIES CARRY A FORWARD EXPECTATION right now (only CHF
# has none, having printed 1 Oct):
#
#     USD 3.4 -> 3.6 (14 Oct)   EUR 3.2 -> 3.8 (16 Oct)
#     CAD 3.0 -> 3.2 (19 Oct)   GBP 3.1 -> 3.4 (21 Oct)
#     NZD 4.1 -> 3.7 (21 Oct)   JPY 1.9 -> 1.8 (22 Oct)
#     AUD 4.0 -> 3.9 (28 Oct)
#
# Every one of them happens to score the SAME as its level today, so the board
# does not move. THAT IS LUCK, NOT CORRECTNESS, and JPY proves it: the level
# 1.9% and the expected 1.8% both read 0 only because NEW_LOW is inclusive.
# A 0.01pp forecast revision to 1.79% flips JPY to -1. The board was one
# rounding away from a score nothing would have explained.
#
# SERIES IDENTITY IS LOAD-BEARING HERE (F-29/F-37, LD-164). EA's row names the
# FINAL, so this must match 'inflation rate yoy final sep' and never the
# FLASH that prints two weeks earlier at a different number. The match is
# built from the WHITELIST NAME, not a substring, so a flash cannot satisfy a
# final row and a core print cannot satisfy a headline one.
SCHED_INF = {}

# {ccy: (consensus, forecast, actual, date, capture)} for a print that has
# ALREADY LANDED - the expectation it was scored against, recovered from the
# capture archive rather than from the newest capture alone.
LANDED_INF = {}


# *** F-187 - THE EXPECTATION A LANDED PRINT WAS SCORED AGAINST LIVES IN A
# CAPTURE WE NO LONGER READ.
#
# Jeff, 2026-11-04, on the JPY inflation row scoring 0: "I disagree on JPY it
# is not 0 due to the results", with a screenshot of the TE page showing
# 2.1% actual against a 2.3% FORECAST. Our score was 0.
#
# I had searched for JPY's expectation in the NEWEST capture, found the next
# scheduled print (20 Nov) blank on both columns, and reported that no
# forecast existed. What I had actually established was that no forecast was
# visible FROM THERE. The print that scores is the one that landed 22 Oct,
# and capture 2026-10-23_1022PHT holds it complete:
#
#     2026-10-22  act='2.1%'  prev='1.9%'  cons=''  fcst='2.3%'
#
# That is F-73 exactly - an absence we cannot see is a fact about our reach,
# not about the world - committed while quoting F-73 in the same session.
#
# *** THE WINDOW IS THE MECHANISM, AND IT IS NOT A JPY PROBLEM.
# TE's calendar window rolls forward faster than our capture cadence. The
# expectation appears in the capture BEFORE the print; the actual appears in
# the capture AFTER it; only the captures in between hold both. Once the row
# rolls off the back, load_inflation() - which reads ONE capture - can never
# see the pair again, and the row silently falls back to the LD-155 corridor
# level test. Three of eight rows were wrong this way:
#
#     JPY  2.1% vs fcst 2.3% (22 Oct)   scored  0, should be -1
#     NZD  3.7% vs cons 3.8% (21 Oct)   scored +1, should be -1
#     CAD  3.1% vs cons 3.2% (19 Oct)   scored +1, should be -1
#
# All three MISSED and all three were scored off the level instead. Every
# one of those expectations was in our own archive the whole time.
#
# So the fix is not another gate. The archive is append-only by nature - 39
# captures, nothing overwritten - and this reads the pair back out of it.
# The newest sighting that carries OUR actual is the authority, because a
# later capture may show the same row re-stated or rolled off entirely.
def load_landed_inflation(archive=None):
    """Fill LANDED_INF from the WHOLE capture archive. Returns rows found.

    For each currency's inflation row, find the newest capture that witnessed
    the print with an actual, and keep the expectation recorded alongside it.
    """
    import glob as _g
    import json as _j
    import os as _os
    import io as _io
    import re as _re
    import datetime as _dt           # F-187b - a passed date anchors a row
    if archive is None:
        archive = sorted(_g.glob(_os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json')))
    ISO = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
           'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}
    WANT = {}
    for _c, _i, _n, _a, _p, _r, _t, _v in sm.ROWS:
        if _c == 'Inflation':
            WANT[sm.LABEL[_i]] = _n
    n = 0
    for cap in archive:
        try:
            raw = _j.load(_io.open(cap, encoding='utf-8'))
        except Exception:
            continue
        rows = raw if isinstance(raw, list) else raw.get(
            'rows', raw.get('events', []))
        for r in rows:
            ccy = ISO.get(r.get('iso'))
            if not ccy or ccy not in WANT:
                continue
            e = (r.get('event', '') or '').lower()
            if not _re.match(r'^inflation rate yoy', e):
                continue
            if 'core' in e or 'mom' in e or 'qoq' in e:
                continue
            # series identity, exactly as load_inflation enforces it (F-37)
            if ('final' in e) != ('Final' in WANT[ccy]):
                continue
            cons = (r.get('consensus') or '').strip()
            fcst = (r.get('forecast') or '').strip()
            if not (cons or fcst):
                continue            # no expectation recorded - nothing to use
            act = (r.get('actual') or '').strip()
            # *** F-187b - A PRINT WE NEVER CAPTURED STILL HAS AN EXPECTATION.
            #
            # CHF inflation printed 1.5% on 2026-11-03. NO capture holds that
            # actual - our 3 Nov capture was taken at 12:26 PHT, before the
            # release, and the value was recovered from the agency under LD-3.
            # But both the 1 Nov and 3 Nov captures DO hold cons=1.3%, and
            # 1.5% beat it, so the row scores +1 under the override.
            #
            # F-186's date guard keeps a passed print out of SCHED_INF, which
            # is right - it is not "next". But the expectation it carried is
            # exactly what the actual was measured against, and dropping the
            # row entirely threw that away. So a row whose DATE HAS PASSED is
            # anchored here by date rather than by a matching actual: the
            # fact table owns the value, this owns what was expected of it.
            if not act:
                if (r.get('date') or '') >= _dt.date.today().isoformat():
                    continue        # genuinely upcoming - SCHED_INF's job
                act = None          # passed, uncaptured: anchor on date only
            # captures are walked oldest-first, so a later sighting of the
            # SAME print overwrites an earlier one - the latest reading of
            # a value wins, which is the same rule the fact tables use.
            prior = LANDED_INF.get(ccy)
            if prior and prior[3] > (r.get('date') or ''):
                continue            # keep the NEWER print, not an older one
            LANDED_INF[ccy] = (cons or None, fcst or None, act,
                               r.get('date') or '', _os.path.basename(cap))
            n += 1
    return n


def load_inflation_pages(refresh=False):
    """Fill SCHED_INF from the TE INDICATOR PAGES. Returns rows found.

    *** F-199, the inflation half. Same reasoning as
    rate_model.load_scheduled_pages: load_inflation() reads ONE calendar
    capture, whose window had reached only CAD's 14 Dec print on
    2026-11-20. The per-currency CPI page carries the rest.

    *** THE REACH IS SMALLER THAN IT LOOKS, AND BOTH REASONS ARE CORRECT.
    Eight pages carry a forward row; only TWO can be used:
      - five have a forward row with a BLANK TEForecast - the row exists,
        the number does not, so there is nothing to score (F-73: say what
        we know, not what we infer from a gap)
      - EUR's only forward row is the Inflation Rate YoY FLASH, and our row
        names the FINAL. F-37: a flash cannot satisfy a final row. The
        identity test refuses it, which is the whole point of having one.

    So this adds AUD and NZD. That is a small gain honestly obtained,
    rather than a large one taken by loosening a rule.
    """
    import indicator_pages as ip
    WANT = {}
    for _c, _i, _n, _a, _p, _r, _t, _v in sm.ROWS:
        if _c == 'Inflation':
            WANT[sm.LABEL[_i]] = _n
    n = 0
    for ccy, name in WANT.items():
        if ccy in SCHED_INF:
            continue                     # the capture already answered
        try:
            # *** THE PAGE IS FETCHED BY THE WHITELIST NAME, not a guess.
            # slug('Inflation Rate') resolves to 'inflation-rate', a page
            # that is not the CPI release history; only the whitelist names
            # ('Inflation Rate YoY', '... Final') map to 'inflation-cpi'
            # via SLUG. Passing a tidied-up name silently fetched the wrong
            # page and the loader found nothing - no error, just a quiet 0.
            html = ip.raw_html(ccy, name, refresh)
            s = ip.scheduled(html, name)
        except Exception:
            continue
        if not s:
            continue
        SCHED_INF[ccy] = (s['consensus'], s['forecast'], s['date'],
                          s['event'].lower())
        n += 1
    return n


def load_inflation(capture=None):
    """Fill SCHED_INF from a TE capture. Returns how many rows it found.

    {ccy: (consensus, forecast, date, event)} for UNRELEASED rows of OUR
    series only. A row with an actual is already history - the fact table
    carries it - so only forward-dated expectations land here.
    """
    import glob as _g
    import json as _j
    import os as _os
    import io as _io
    import re as _re
    import datetime as _dt               # F-186 - a passed date is not "next"
    if capture is None:
        c = sorted(_g.glob(_os.path.join(REPO,
                   'data/raw/calendar/*_cal_full.json')))
        if not c:
            return 0
        capture = c[-1]
    ISO = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
           'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}
    # the whitelist's own name per currency - the authority on which series
    # is ours (LD-164: EA names the FINAL, the other seven the headline)
    WANT = {}
    for _c, _i, _n, _a, _p, _r, _t, _v in sm.ROWS:
        if _c == 'Inflation':
            WANT[sm.LABEL[_i]] = _n
    raw = _j.load(_io.open(capture, encoding='utf-8'))
    rows = raw if isinstance(raw, list) else raw.get(
        'rows', raw.get('events', []))
    n = 0
    for r in rows:
        ccy = ISO.get(r.get('iso'))
        if not ccy or ccy not in WANT:
            continue
        e = (r.get('event', '') or '').lower()
        if not _re.match(r'^inflation rate yoy', e):
            continue
        if 'core' in e or 'mom' in e or 'qoq' in e:
            continue
        # *** FINAL IS PART OF THE SERIES IDENTITY (F-37). Our EA row names
        # the FINAL; the FLASH is a different series at a different number.
        if ('final' in e) != ('Final' in WANT[ccy]):
            continue
        if (r.get('actual') or '').strip():
            continue            # released - the fact table owns it
        # *** F-186 - A BLANK ACTUAL DOES NOT MEAN "NOT YET RELEASED".
        #
        # The test above is the only thing separating an UPCOMING print from
        # a LANDED one, and it reads a column that goes stale. CHF inflation
        # printed 1.5% on 2026-11-03; our capture that day was taken at
        # 12:26 PHT, BEFORE the release, so the actual is blank - and this
        # loop therefore filed a print that had ALREADY HAPPENED as the next
        # one scheduled. LD-165 then read the 1.3% consensus as the live
        # expectation and scored the row BEFORE-the-news at -1, when the
        # actual beat that consensus and scores +1. A 2-point error on a
        # WEIGHT-3 category, so 6 points of raw contribution.
        #
        # The capture can never self-heal it: the TE window rolls forward
        # faster than we capture, so the row falls off the back before the
        # number lands in it. Same mechanism as F-185, different table.
        #
        # So a date in the PAST disqualifies a row from being "scheduled",
        # whatever its actual column says. The fact table owns a print whose
        # date has passed - recovered from the indicator page under LD-3 if
        # no capture caught it.
        if (r.get('date') or '') < _dt.date.today().isoformat():
            continue
        cons = (r.get('consensus') or '').strip()
        fcst = (r.get('forecast') or '').strip()
        if not (cons or fcst):
            continue
        # earliest scheduled print wins - that is the NEXT one
        prior = SCHED_INF.get(ccy)
        if prior and prior[2] <= (r.get('date') or ''):
            continue
        SCHED_INF[ccy] = (cons or None, fcst or None,
                          r.get('date') or '', e)
        n += 1
    return n


def score_row(cat, ccy, indicator, actual, _autoload_inf=True):
    """The derived score for one cell, or None if it cannot be graded."""
    if not (actual or '').strip():
        return None
    if cat == 'GDP':
        return band(actual, GDP_THRESHOLD)
    if cat == 'Interest_Rate':
        import rate_model
        iso = dict((v, k) for k, v in sm.LABEL.items())[ccy]
        return round(rate_model.compute()[iso]['raw'], 3)
    r = _rule(ccy, indicator)
    if r is None:
        return None
    thr, verdict, prev = r
    if cat == 'Inflation':
        # LD-155 replaces LD-136/LD-143 here, and it is a BEFORE/AFTER rule.
        # LD-165 - WHEN A PRINT IS SCHEDULED, THE EXPECTATION IS THE READING.
        # Jeff: "in the TE calendar some Inflation already have consensus/
        # forecast on future dates. they should be now scored according to
        # that". The fact table's actual is the LAST print; where TE carries a
        # consensus for the NEXT one, that is what the market is trading
        # (Jeff, on the calibrator: "we're trading the expectations not the
        # result"). Consensus supersedes forecast (LD-154/LD-163).
        if _autoload_inf and not SCHED_INF:
            try:
                load_inflation()
            except Exception:
                pass
            # F-199 - then the PAGES for what the capture window missed.
            # Capture first: it is same-day and may carry a consensus the
            # page has not published yet, and consensus outranks forecast
            # (LD-154/LD-155).
            try:
                load_inflation_pages()
            except Exception:
                pass
        _s = SCHED_INF.get(ccy)
        if _s:
            sc, _src, _why = inflation_decision(
                previous=actual, consensus=_s[0], forecast=_s[1])
            if sc is not None:
                return sc
        # F-187 - NO SCHEDULED PRINT DOES NOT MEAN NO EXPECTATION.
        # Before falling back to the bare level test, ask the ARCHIVE what
        # this print was expected to be. The pair (expectation, actual) sits
        # in the captures between the two window positions; reading only the
        # newest capture loses it and silently reverts the row to a corridor
        # test LD-155's override is supposed to beat.
        if _autoload_inf and not LANDED_INF:
            try:
                load_landed_inflation()
            except Exception:
                pass
        _l = LANDED_INF.get(ccy)
        # _l[2] is the actual the ARCHIVE saw, or None when the print landed
        # between captures (F-187b) - then the fact table's actual is the
        # only one there is, and the archive supplies only the expectation.
        if _l and (_l[2] is None or _l[2] == (actual or '').strip()):
            sc, _src, _why = inflation_decision(
                consensus=_l[0], forecast=_l[1], actual=actual)
            if sc is not None:
                return sc
        # no expectation anywhere - the print is its own reading: the LEVEL
        # test against 1.8-2.2.
        sc, _src, _why = inflation_decision(actual=actual)
        if sc is not None:
            return sc
    # *** F-194 - A THRESHOLD NO RULE RECOGNISES SILENTLY FREEZES THE ROW.
    #
    # Jeff, 2026-11-20, restating LD-58 unprompted while ruling on the
    # Nov-26 advance: "Actual > 0 is Bad, Actual < 0 is Good, Actual = 0 is
    # Neutral. Also the latest release for Oct data is 33.2K which should be
    # scored as Bad or -1."
    #
    # score_model.claimant_grade() ALREADY implemented that rule, correctly,
    # since 2026-08-24. Nothing here ever called it. The threshold text
    # '<0 (LD-58)' matches neither prev_score (wants '>prev'/'<prev') nor
    # band (wants '> N'), so the row fell through to the LAST line of this
    # function - the verdict somebody TYPED into score_model.ROWS.
    #
    # THAT IS THE SECOND COPY OF THE SCORE LD-112 EXISTS TO REMOVE, and it
    # is worse than a stale number because it cannot be seen going wrong.
    # Measured by substitution before the fix, the row was INVARIANT:
    #
    #     actual=30.3K -> -1    actual=-50K  -> -1    actual=0 -> -1
    #     actual=33.2K -> -1    actual=+500K -> -1
    #
    # A 50K FALL IN CLAIMANTS - unambiguously good, and the exact case LD-58
    # was written to fix - scored BAD, because the score was not being
    # computed at all. It happened to read -1 for the right answer on the
    # held value, which is luck, not correctness: the same luck F-184 warned
    # about on the inflation rows.
    #
    # Routed on the THRESHOLD TEXT, not on a hardcoded 'GBP'. The whitelist
    # names the rule that owns the row (F-3: the list is the closed set and
    # the rule travels with it), so a second currency given this threshold
    # is scored by it automatically, and a row whose threshold is changed
    # stops being scored by it automatically. Hardcoding the currency here
    # would put the rule in two places and let them drift apart.
    if 'ld-58' in (thr or '').lower():
        g = sm.claimant_grade(sm._num(actual))
        sc = {'GOOD': 1, 'BAD': -1, 'NEUTRAL': 0}.get(g)
        if sc is not None:
            return sc
    # *** F-195 - THE SECOND HALF OF F-194, AND I GOT THE REASON WRONG.
    #
    # I reported AUD/CAD Employment Change as unfixable because "TE's
    # indicator page carries only the headline, never the FT/PT split".
    # Jeff, 2026-11-20: "I can see FT/PT split in TE why you can't get it?"
    #
    # HE IS RIGHT AND I HAD NOT LOOKED. The split is on the page, in the
    # Components table, as named series with their own reference month:
    #
    #     Full Time Employment Chg   -2948.00   35398.00  Persons  Oct 2026
    #     Part Time Employment Chg  -40583.00  -71797.00  Persons  Oct 2026
    #
    # I had only ever parsed the Calendar table, which carries the headline,
    # and stated the absence as a fact about TE. That is F-73 exactly - an
    # absence we cannot see is a fact about OUR REACH, not about the world -
    # and worse than the original F-194, because F-145 had ALREADY recorded
    # that TE publishes this split for CAD. The repo knew; I asserted over it.
    #
    # Reconciled before wiring (both currencies, latest vintage):
    #     AUD  headline -43.5K == FT -2.9K + PT -40.6K   diff 0.00K
    #     CAD  headline  -4.7K == FT -18.1K + PT +13.4K  diff 0.00K
    # and CAD's TE previous legs match our held Sep/26 legs to the decimal.
    #
    # employment_grade() already implemented LD-151 correctly, and R-44
    # already tested all six cases. Only the wiring was missing - the same
    # shape as the LD-58 defect above, in the same function, found the same
    # day. The legs are read from the CELL, which carries them inline:
    #
    #     -39.3K (FT +34.4K, PT -73.7K)
    #
    # so the rule needs no second source and no new fetch. A cell without
    # both legs returns None from employment_grade (never a guessed verdict,
    # F-73) and falls through - a row we cannot grade stays ungraded rather
    # than being scored on the headline alone, which is the F-145 defect.
    if 'ld-151' in (thr or '').lower():
        g = sm.employment_grade(sm._num(actual), *_legs(actual))
        sc = {'GOOD': 1, 'BAD': -1, 'NEUTRAL': 0}.get(g)
        if sc is not None:
            return sc
    # LD-177 - the table's own prior column is `previous`, and ROWS.prev is
    # only the fallback for a row the table cannot answer for (a row absent
    # from the CSV, or a first month with no prior column). Reading the
    # table FIRST is the whole rule: the literal is a third copy, and a
    # third copy of a number is a third chance to be wrong about it.
    sc = prev_score(actual, _prev_cell(cat, ccy, indicator) or prev, thr)
    if sc is not None:
        return sc
    b = band(actual, thr)
    if b is not None:
        return b
    # *** REACHING HERE IS A DEFECT, NOT A FALLBACK (F-194). Every row in
    # the whitelist should be answered by a RULE above. This line returns a
    # hand-typed verdict, so a row that lands here is frozen - the score
    # cannot respond to the actual. Two rows still reach it today, both
    # 'LD-151 three legs' (AUD/CAD Employment Change), because LD-151 is
    # documented in score_model and implemented nowhere, AND because TE's
    # indicator page carries only the headline, never the FT/PT split the
    # rule needs. They are KNOWN-FROZEN and reported as such, not quietly
    # scored. Do not add a row to this path to make it score.
    return {'GOOD': 1, 'BAD': -1, 'NEUTRAL': 0}.get(verdict)


def derive(month=None):
    """[(cat, ccy, indicator, actual, score)] for every fact-table row."""
    month = month or ft.latest_month()
    out = []
    for cat in sorted(ft.WEIGHT):
        for r in ft.load(cat):
            ccy = r['Currency'].strip()
            ind = r['Indicator'].strip()
            act = (r.get(month) or '').strip()
            out.append((cat, ccy, ind, act, score_row(cat, ccy, ind, act)))
    return out


def write(month=None):
    month = month or ft.latest_month()
    rows = derive(month)
    d = os.path.dirname(OUT)
    if not os.path.isdir(d):
        os.makedirs(d)
    fh = io.open(OUT, 'w', encoding='utf-8', newline=chr(10))
    w = csv.writer(fh, lineterminator=chr(10))
    w.writerow(['Month', 'Category', 'Currency', 'Indicator',
                'Actual', 'Score'])
    for cat, ccy, ind, act, sc in rows:
        w.writerow([month, cat, ccy, ind, act,
                    '' if sc is None else sc])
    fh.close()
    return rows


if __name__ == '__main__':
    m = ft.latest_month()
    rows = write(m)
    ungraded = [r for r in rows if r[3] and r[4] is None]
    print('DERIVED SCORES  %s   month=%s' % (OUT, m))
    print('  %d rows, %d with an actual, %d ungraded'
          % (len(rows), len([r for r in rows if r[3]]), len(ungraded)))
    for r in ungraded:
        print('   UNGRADED %-14s %-4s %s  actual=%s' % (r[0], r[1], r[2], r[3]))
