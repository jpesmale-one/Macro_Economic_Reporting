# -*- coding: utf-8 -*-
"""
LD-23: Interest Rate is the SIXTH scored category, weight 3.

Jeff, 2026-08-21: "The increase in the Interest Rate means Good for the currency
because it will lessen the supply of that currency... That's why we are trying
to foresee if there will be a Hike or Cut in the Interest Rate."

score = (REALISED + EXPECTED) / 2 * 3

REALISED - the Idea_dump rule on the last decision:
    hiked +1.0 | held 0.0 | cut -1.0

EXPECTED - inflation vs THE BANK'S OWN MANDATE, and nothing else:

                        RISING    FALLING
    above ceiling        +0.5       0.0
    inside band         +0.25      -0.25
    below floor           0.0      -0.5

WHY ONLY INFLATION (Jeff's call, 2026-08-21):
Three other inputs were designed and REJECTED because they cannot be applied
to all eight currencies on equal terms:

  STEP 2 priced odds  - an instrument exists for all 8 (CME, SONIA, ESTR,
    CORRA, ASX RBA Tracker, NZ OIS, TONA, SARON) but only USD was ever
    sourced. Scoring it would have credited USD for evidence the other seven
    HAVE and I had not fetched. That is a sourcing gap masquerading as a
    signal.
  STEP 3 vote splits  - published by the Fed (12) and BoE (9), sometimes BoJ.
    The ECB, RBA, BoC and SNB publish NONE, ever. Six currencies could never
    score it.
  STEP 4 forward path - only the RBNZ publishes an OCR track. One of eight.

Jeff: "if we cannot find an equilibrium for Steps 2,3,4 then I'd say let's just
used Step 1 in the scoring. this way we are not nit-picking and create a
unfavorable bias for other currencies."

Those inputs still inform the section-3 Bias chip and the written expectation -
they are simply not allowed to move the NUMBER.

MANDATES ARE NOT ALL 2%. Four of eight target a RANGE. Scoring every currency
against a 2% point target penalised CHF for 0.4% inflation that sits INSIDE
the SNB's own 0-2% mandate. Each bank is judged against its own target.
"""

# LD-107 - THE EXPECTED PATH, a fourth term (Jeff, 2026-09-09):
#
#   "I think we need to inject Hawkish and Dovish tone in the score as market
#    moves prior the change then we might want to reflect the market
#    sentiment in the score for the Interest Rate"
#
# THE PROBLEM IT FIXES, and it is the most expensive gap this model has had.
# On 2026-09-03 the BoJ moved the yen 292 pips WITHOUT MEETING - Takata left
# the door open to back-to-back hikes and traders reported a rate check. JPY
# finished the week +2.87%, seven times the next currency, and 2.6 scored it
# 0.000. Every term in the old score describes a decision that has already
# happened; none of them can see a repricing between meetings.
#
# WHAT IS SCORED, and why it clears LD-23. TE publishes a FORECAST for each
# next decision. That forecast IS the market's hawkish/dovish expectation,
# expressed as a number instead of as prose - no sentiment reading, no
# subjective tone call. Verified 2026-09-09: ALL EIGHT currencies have
# carried one. NZD and CAD show none today only because they decided on 2
# Sep and their next meetings sit beyond TE's horizon.
#
#   path = forecast - current policy rate, in basis points
#
#     >= +25bp   HAWKISH   +0.5    a hike is priced
#     +1..+24    leaning   +0.25
#      0         NEUTRAL    0.0    no move priced
#     -1..-24    leaning   -0.25
#     <= -25bp   DOVISH    -0.5    a cut is priced
#
# THE SAME SCALE AS THE OTHER TERMS (+/-0.5), so path cannot outvote the
# realised level or the surprise - it re-weights, it does not dominate.
#
# WHY NOT A TONE READING OF SPEECHES, which is what "hawkish/dovish" usually
# means: the capture schedules CB speak for six currencies and ZERO for CAD
# and CHF. Scoring it would blank two currencies - the exact "unfavorable
# bias" Jeff ruled out for steps 2-4 above. A forecast is available to all
# eight and needs no interpretation.
#
# NONE means NO FORECAST PUBLISHED. Like SURPRISE, it drops out of the
# average rather than scoring 0, which would assert the market prices no
# move when the truth is that we cannot see one.

# LD-109 - THE TERMS ARE NOT EQUAL. Jeff, 2026-09-09:
#
#   "I think we should divide the score on your scoring criteria but giving
#    more weight to Expectancy (Expected and Path) ... Realised 20, Expected
#    30, Surprise 20, Path 30. This will give more forward looking narative"
#
# REALISED and SURPRISE describe a decision that has already been taken and
# already been traded. EXPECTED and PATH describe where policy is going -
# the inflation case building toward a move, and the move the market has
# priced for the next meeting. 60% of the score now sits on the forward
# half, which is the whole point of a model built to FORESEE a hike.
#
# RENORMALISED OVER LIVE TERMS ONLY. A currency between meetings has no
# SURPRISE; one whose next meeting is beyond TE's horizon has no PATH. The
# divisor is the sum of the weights that actually apply, so a missing term
# neither scores zero nor penalises the currency for the absence.
TERM_WEIGHT = {'realised': 0.20, 'expected': 0.30,
               'surprise': 0.20, 'path': 0.30}

W_RATE = 3

# ccy -> (low, high). A point target has low == high.
MANDATE = {
    'US': (2.0, 2.0),   # 2% PCE; CPI used as the published proxy, noted in-report
    'EA': (2.0, 2.0),   # 2% HICP, symmetric
    'GB': (2.0, 2.0),   # 2% CPI, +/-1pp letter threshold
    'JP': (2.0, 2.0),   # 2% CPI
    'AU': (2.0, 3.0),   # 2-3% band
    'NZ': (1.0, 3.0),   # 1-3% band
    'CA': (1.0, 3.0),   # 1-3% band
    'CH': (0.0, 2.0),   # 0-2%, "price stability"
}

# ccy -> (rate, realised, cpi, rising, cpi_note)
ROWS = {
    # LD-90. The 6th field is the DECISION SURPRISE, actual vs consensus.
    # NZD 2026-09-02: hiked to 2.75% exactly on consensus and FELL 108
    # pips. A fully-priced hike is not news, so it scores 0.00 - the
    # realised term still pays for the level, the surprise pays nothing.
    'NZ': ('2.75%', +1.0, 4.1, True,  'HIKED 2 Sep to 2.75%, exactly on consensus - fully priced, NZD -108 pips (LD-90)', 0.0, 2.50, None),
    'US': ('3.50-3.75%', 0.0, 3.4, False, 'CPI as proxy; the Fed targets PCE', None, 3.75, 4.00),
    'EA': ('2.40%', 0.0, 2.9, True,  'HICP final', None, 2.40, 2.65),
    'GB': ('3.75%', 0.0, 2.9, True,  '', None, 3.75, 3.75),
    'JP': ('1.00%', 0.0, 1.9, True,  'Jul/26 print, released 07:30 PHT 21 Aug', None, 1.00, 1.25),
    'AU': ('4.35%', 0.0, 3.8, False, '', None, 4.35, 4.35),
    # LD-90: BoC HELD 2 Sep at 2.25%, exactly on consensus. A fully-priced
    # hold is not news either - the surprise term pays 0.00 rather than
    # being absent. NZD's row already recorded this; CAD's did not.
    'CA': ('2.25%', 0.0, 3.0, True,  'HELD 2 Sep at 2.25%, exactly on consensus - fully priced, CAD +53 pips (LD-90)', 0.0, 2.25, None),
    # F-88: this row still carried 0.4% FALLING after CHF inflation
    # printed 0.8% RISING on 3 Sep. Section 2.5 updated on that print and
    # 2.6 did not, so the same indicator drove two categories in opposite
    # directions in one edition. Inside-band and rising is +0.25, not
    # -0.25 - a 0.75 swing on a weight-3 category.
    'CH': ('0.00%', 0.0, 0.8, True,  'Aug/26 print, 0.8% vs 0.5% consensus - inside the SNB 0-2% band and RISING', None, 0.00, 0.00),
}


def expected(ccy, cpi, rising):
    lo, hi = MANDATE[ccy]
    band = '%.0f-%.0f%%' % (lo, hi) if lo != hi else '%.0f%% point' % lo
    if cpi > hi:
        return (+0.5, 'above %s ceiling and RISING' % band) if rising \
            else (0.0, 'above %s ceiling but falling' % band)
    if cpi < lo:
        return (0.0, 'below %s floor but rising' % band) if rising \
            else (-0.5, 'below %s floor and FALLING' % band)
    return (+0.25, 'inside %s, rising' % band) if rising \
        else (-0.25, 'inside %s, falling' % band)


def path_score(current, forecast):
    """(score, bp, label) for the expected path, or (None, None, ...).

    current/forecast are percentages. A range like '3.50-3.75%' takes its
    UPPER bound, which is the rate the market quotes and the one TE's
    forecast is expressed against.
    """
    if current is None or forecast is None:
        return None, None, 'no forecast published'
    bp = round((forecast - current) * 100)
    if bp >= 25:
        return 0.5, bp, 'HAWKISH - a hike is priced'
    if bp > 0:
        return 0.25, bp, 'leaning hawkish'
    if bp == 0:
        return 0.0, bp, 'NEUTRAL - no move priced'
    if bp > -25:
        return -0.25, bp, 'leaning dovish'
    return -0.5, bp, 'DOVISH - a cut is priced'


def compute():
    """REALISED + EXPECTED + SURPRISE (LD-90).

    Jeff, 2026-09-02, after the RBNZ hiked exactly on consensus and NZD fell
    108 pips: "A central bank decision moves price by its surprise component
    only. Level of rates -> already discounted."

    REALISED and EXPECTED both describe what already happened. SURPRISE is
    the gap between the decision and what was priced, and it is the only one
    of the three that is forward-looking. A fully-priced hike now scores
    nothing extra rather than another +1.

    A surprise of None means UNMEASURABLE - no consensus published - and it
    is left out of the average entirely rather than counted as zero, which
    would assert the market was unsurprised.
    """
    out = {}
    for ccy, row in ROWS.items():
        rate, real, cpi, ris, note = row[:5]
        surp = row[5] if len(row) > 5 else None
        cur, fcst = (row[6], row[7]) if len(row) > 7 else (None, None)
        exp, why = expected(ccy, cpi, ris)
        path, bp, path_why = path_score(cur, fcst)
        # LD-109: weighted, renormalised over the terms that exist.
        terms = {'realised': real, 'expected': exp,
                 'surprise': surp, 'path': path}
        live = dict((k, v) for k, v in terms.items() if v is not None)
        wsum = sum(TERM_WEIGHT[k] for k in live)
        raw = (sum(v * TERM_WEIGHT[k] for k, v in live.items()) / wsum
               if wsum else 0.0)
        out[ccy] = {'weights': dict((k, TERM_WEIGHT[k]) for k in live),
                    'rate': rate, 'realised': real, 'expected': exp,
                    'surprise': surp, 'path': path, 'path_bp': bp,
                    'path_why': path_why, 'forecast': fcst,
                    'raw': raw, 'score': raw * W_RATE,
                    'cpi': cpi, 'rising': ris, 'why': why, 'note': note,
                    'mandate': MANDATE[ccy]}
    return out


if __name__ == '__main__':
    r = compute()
    print('INTEREST RATE - category 6, weight %d. Inflation-vs-own-mandate only.\n' % W_RATE)
    print('%-4s %-12s %-8s %-34s %8s %8s %8s' %
          ('CCY', 'RATE', 'CPI', 'VS OWN MANDATE', 'REALISED', 'EXPECTED', 'SCORE'))
    for c in sorted(r, key=lambda k: -r[k]['score']):
        d = r[c]
        print('%-4s %-12s %-8s %-34s %+8.1f %+8.2f %+8.2f' %
              (c, d['rate'], '%.1f%%' % d['cpi'], d['why'],
               d['realised'], d['expected'], d['score']))
