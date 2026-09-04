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
    'NZ': ('2.75%', +1.0, 4.1, True,  'HIKED 2 Sep to 2.75%, exactly on consensus - fully priced, NZD -108 pips (LD-90)', 0.0),
    'US': ('3.50-3.75%', 0.0, 3.4, False, 'CPI as proxy; the Fed targets PCE', None),
    'EA': ('2.40%', 0.0, 2.9, True,  'HICP final', None),
    'GB': ('3.75%', 0.0, 2.9, True,  '', None),
    'JP': ('1.00%', 0.0, 1.9, True,  'Jul/26 print, released 07:30 PHT 21 Aug', None),
    'AU': ('4.35%', 0.0, 3.8, False, '', None),
    # LD-90: BoC HELD 2 Sep at 2.25%, exactly on consensus. A fully-priced
    # hold is not news either - the surprise term pays 0.00 rather than
    # being absent. NZD's row already recorded this; CAD's did not.
    'CA': ('2.25%', 0.0, 3.0, True,  'HELD 2 Sep at 2.25%, exactly on consensus - fully priced, CAD +53 pips (LD-90)', 0.0),
    # F-88: this row still carried 0.4% FALLING after CHF inflation
    # printed 0.8% RISING on 3 Sep. Section 2.5 updated on that print and
    # 2.6 did not, so the same indicator drove two categories in opposite
    # directions in one edition. Inside-band and rising is +0.25, not
    # -0.25 - a 0.75 swing on a weight-3 category.
    'CH': ('0.00%', 0.0, 0.8, True,  'Aug/26 print, 0.8% vs 0.5% consensus - inside the SNB 0-2% band and RISING', None),
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
        exp, why = expected(ccy, cpi, ris)
        terms = [real, exp]
        if surp is not None:
            terms.append(surp)
        raw = sum(terms) / float(len(terms))
        out[ccy] = {'rate': rate, 'realised': real, 'expected': exp,
                    'surprise': surp, 'raw': raw, 'score': raw * W_RATE,
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
