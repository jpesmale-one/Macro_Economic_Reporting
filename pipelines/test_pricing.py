# -*- coding: utf-8 -*-
"""R-26 - market_pricing() must respect the DIRECTION OF GOODNESS (F-66).

Jeff, 2026-08-30, once the consensus column finally had values in it:
"now we have the consensus 1. why is it still unscored?"

Grading all 26 rows to answer that surfaced two backwards results:

    USD Unemployment Rate   prev 4.1%  cons 4.2%  -> GOOD   (WRONG)
    JPY Household Spending  prev -3.3% cons -1.6% -> GOOD   (right, wrong reason)

market_pricing() returned GOOD whenever previous < consensus, for EVERY
indicator. BELOW is only good where LOWER IS BETTER. Consensus expecting US
unemployment to rise 4.1% -> 4.2% is BAD for USD.

That is F-62/LD-71 again: A COMPARISON IS NOT A DIRECTION. graded_signed()
exists for exactly this reason and market_pricing() predated the lesson.

F-66b: '<' in the threshold column means two different things.
    '<Prev'  -> comparison against the last print; lower IS better
    '<0%'    -> a STATE description, "currently negative"; says nothing
                about direction. JPY Household Spending -3.3% -> -1.6% is a
                SMALLER contraction, an improvement.

Every case below was graded BY HAND first, then checked against the code -
never the other way round.

    python pipelines/test_pricing.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from week_ahead import market_pricing
import score_model as sm

THR = {}
for _cat, _iso, _name, _a, _p, _r, _thr, _v in sm.ROWS:
    THR[(sm.LABEL[_iso], _name)] = _thr


def num(v):
    """A TE value cell -> float. Handles %, K/M/B, currency prefixes."""
    if not v:
        return None
    v = v.replace('\u2212', '-').replace(',', '')
    m = re.search(r'-?\d+\.?\d*', v)
    if not m:
        return None
    x = float(m.group())
    # Anchor the suffix to the DIGITS, not the end of string, and strip
    # markdown first. '**75.1K**' defeated a '$'-anchored suffix test, so it
    # parsed as 75.1 while a plain '15.8K' parsed as 15800 - inverting the
    # comparison and grading a sharp deceleration as GOOD.
    suf = v[m.end():m.end() + 1].upper()
    if suf == 'B':
        x *= 1e9
    elif suf == 'M':
        x *= 1e6
    elif suf == 'K':
        x *= 1e3
    if v.strip().startswith('-') or '-$' in v:
        x = -abs(x)
    return x


# (ccy, indicator, previous, consensus, forecast, expected, why)
CASES = [
    # --- the two that were WRONG before F-66 -------------------------
    ('USD', 'Unemployment Rate', '4.1%', '4.2%', '4.2%', 'BAD',
     'unemployment RISING is bad for the currency - was GOOD before F-66'),
    ('JPY', 'Household Spending YoY', '-3.3%', '-1.6%', '-1.0%', 'GOOD',
     'a SMALLER contraction is a recovery - F-66b, <0% is state not direction'),
    # --- direction-sensitive rows ------------------------------------
    ('CAD', 'Unemployment Rate', '6.4%', '6.4%', '6.4%', 'NEUTRAL',
     'unchanged'),
    ('USD', 'Non Farm Payrolls', '-23K', '45K', '12.0K', 'GOOD',
     '-23K -> +45K is a large improvement'),
    ('CAD', 'Employment Change', '75.1K', '15.8K', '10.0K', 'BAD',
     'sharp deceleration'),
    # --- PMIs: higher is better --------------------------------------
    ('USD', 'ISM Manufacturing PMI', '55.6', '55.3', '55', 'BAD',
     'expected to soften'),
    ('EUR', 'S&P Global Mfg PMI Final', '51.9', '52.8', '52.8', 'GOOD',
     'expansion improving'),
    ('GBP', 'S&P Global Mfg PMI Final', '51.9', '51.5', '51.5', 'BAD',
     'softening'),
    ('AUD', 'S&P Global Mfg PMI Final', '52.0', '52.0', '52.0', 'NEUTRAL',
     'flat'),
    ('CHF', 'Procure.ch-UBS Mfg PMI', '53.2', '53.5', '52.8', 'NEUTRAL',
     '53.2 sits inside the 52.8-53.5 band'),
    # --- trade balances: a shrinking surplus is BAD ------------------
    ('AUD', 'Balance of Trade', 'A$1.929B', 'A$1.39B', 'A$1.1B', 'BAD',
     'surplus shrinking'),
    ('CAD', 'Balance of Trade', 'C$3.86B', 'C$3.2B', 'C$2.2B', 'BAD',
     'surplus shrinking'),
    ('USD', 'Balance of Trade', '-73.3B', '-86.4B', '-91.2B', 'BAD',
     'deficit widening'),
    # --- spending / confidence ---------------------------------------
    ('JPY', 'Retail Sales YoY', '0.5%', '3%', '1.0%', 'GOOD',
     'acceleration'),
    ('JPY', 'Consumer Confidence', '34.9', '35', '35', 'GOOD', 'improving'),
    ('CHF', 'Retail Sales YoY', '1.5%', '1.3%', '2.0%', 'NEUTRAL',
     '1.5 sits inside the 1.3-2.0 band'),
    ('EUR', 'Unemployment Rate', '6.3%', '6.3%', '6.3%', 'NEUTRAL',
     'unchanged'),
    # --- F-74: a RELEASE is graded against CONSENSUS, not against the
    # --- previous print. JPY Mfg PMI printed 54.9 on a 55.1 consensus,
    # --- up from 54.5. The series improved AND the market was
    # --- disappointed - both true, and only the second moves price.
    ('JPY', 'S&P Global Mfg PMI Final', '55.1', '54.9', '', 'BAD',
     'consensus 55.1, actual 54.9 - a MISS even though prev was 54.5'),
    ('AUD', 'S&P Global Mfg PMI Final', '52.0', '52.0', '', 'NEUTRAL',
     'actual equals consensus - in line'),
    # --- F-70: INFLATION IS RATE SUPPORT, not consumer harm. Jeff,
    # --- 2026-08-31: "The inflation of CHF is expected to increase from
    # --- 0.4% to 0.7% why is it bad for the currency?" It is not. Rising
    # --- inflation builds the rate case (LD-23). LOWER_IS_BETTER used to
    # --- contain 'inflation rate' - the CONSUMER's sign - so every
    # --- rising-inflation forecast graded BAD for every currency.
    ('CHF', 'Inflation Rate YoY', '0.4%', '0.7%', '', 'GOOD',
     'rising off the SNB floor toward the band is rate support'),
    ('GBP', 'Inflation Rate YoY', '2.6%', '2.9%', '', 'GOOD',
     'rising above a 2% target hardens the hike case'),
    # --- but NOT unconditional: far above the ceiling it stops helping
    ('AUD', 'Inflation Rate YoY', '3.5%', '5.5%', '', 'BAD',
     'RBA band is 2-3%; 5.5% is a policy problem, not rate support'),
    # --- F-68: the THRESHOLD column must encode DIRECTION, not the
    # --- last observed move. On 2026-08-31 NZD ANZ Business Confidence
    # --- fell 56.1 -> 53.7 and the row was written "<Prev" to DESCRIBE
    # --- that fall. lower_is_better() reads "<Prev" as "lower is better",
    # --- so the MISS graded as a BEAT. A confidence index is always
    # --- ">Prev"; the VERDICT column carries what happened.
    ('NZD', 'ANZ Business Confidence', '56.1', '53.7', '', 'BAD',
     'a confidence index FALLING is bad - threshold is direction, not history'),
    # --- MARKDOWN-WRAPPED cells: the table passes these verbatim ------
    # This is the exact pair that broke: '**75.1K**' vs '15.8K'. With a
    # '$'-anchored suffix test the first parsed as 75.1 and the second as
    # 15800, so a 59K DECELERATION graded GOOD.
    ('CAD', 'Employment Change', '**75.1K**', '15.8K', '10.0K', 'BAD',
     'markdown must not change the NUMBER - bold defeated the K suffix'),
    ('USD', 'Non Farm Payrolls', '**−23K**', '45K', '12.0K', 'GOOD',
     'bold + typographic minus must still parse as -23000'),
    # --- no consensus: must return None, never a guess ---------------
    ('NZD', 'Building Permits MoM', '-3.6%', '', '2.5%', None,
     'no consensus - must be None, not assumed neutral'),
]


def _s(x):
    """Console-safe. Windows cp1252 cannot encode U+2212 and the test must
    not die printing its own fixtures."""
    return str(x).replace('−', '-')


def main():
    print('R-26 PRICING DIRECTION (F-66)')
    print('=' * 78)
    bad = 0
    for ccy, ind, p, c, f, want, why in CASES:
        got = market_pricing(num(p), num(c), num(f), name=ind,
                             threshold=THR.get((ccy, ind), ''),
                             ccy=ccy)
        ok = got == want
        if not ok:
            bad += 1
        print('%-4s %-26s %-9s %-9s %-8s %-8s %s'
              % (ccy, ind[:26], _s(p), _s(c) or '-', _s(got), _s(want),
                 'OK' if ok else '** MISMATCH **'))
        if not ok:
            print('       expected because: %s' % why)
    print('=' * 78)
    if bad:
        raise SystemExit('%d of %d WRONG - a comparison is not a direction '
                         '(F-62, F-66).' % (bad, len(CASES)))
    print('All %d pricing cases correct.' % len(CASES))
    print()
    print('NOTE: these grade what the market PRICES, never a released value.')
    print('LD-3 - the actual print still comes from the issuing agency.')


if __name__ == '__main__':
    main()
