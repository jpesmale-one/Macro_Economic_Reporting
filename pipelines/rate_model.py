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
    'NZ': ('2.50%', +1.0, 4.1, True,  'QUARTERLY series - stale by construction'),
    'US': ('3.50-3.75%', 0.0, 3.4, False, 'CPI as proxy; the Fed targets PCE'),
    'EA': ('2.40%', 0.0, 2.9, True,  'HICP final'),
    'GB': ('3.75%', 0.0, 2.9, True,  ''),
    'JP': ('1.00%', 0.0, 1.9, True,  'Jul/26 print, released 07:30 PHT 21 Aug'),
    'AU': ('4.35%', 0.0, 3.8, False, ''),
    'CA': ('2.25%', 0.0, 3.0, True,  ''),
    'CH': ('0.00%', 0.0, 0.4, False, ''),
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
    out = {}
    for ccy, (rate, real, cpi, ris, note) in ROWS.items():
        exp, why = expected(ccy, cpi, ris)
        raw = (real + exp) / 2.0
        out[ccy] = {'rate': rate, 'realised': real, 'expected': exp,
                    'raw': raw, 'score': raw * W_RATE, 'cpi': cpi,
                    'rising': ris, 'why': why, 'note': note,
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
