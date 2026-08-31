# -*- coding: utf-8 -*-
"""R-28 - the THRESHOLD column encodes DIRECTION, never the last move (F-68).

Jeff's Monday edition, 2026-08-31. NZD ANZ Business Confidence fell 56.1 ->
53.7 and I wrote the row's threshold as "<Prev" to DESCRIBE that fall. But
lower_is_better() reads "<Prev" as "for this series, LOWER IS BETTER" - so a
confidence MISS graded as a BEAT.

THE THRESHOLD COLUMN DOES ONE JOB: which direction favours the currency.
The VERDICT column carries what actually happened. Conflating them silently
inverts the grade, and it did so within a day of F-66 fixing the same class.

This checks every whitelist row whose threshold names the previous print,
against what the SERIES is known to want. A confidence index, a PMI, or a
payrolls number is always ">Prev"; unemployment and claimant counts are
always "<Prev".

    python pipelines/audit_direction.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_model as sm

# Series where a HIGHER print favours the currency, by name fragment.
HIGHER = ('confidence', 'pmi', 'sentiment', 'payrolls', 'employment change',
          'job ads', 'retail sales', 'gdp', 'production', 'spending',
          'business', 'permits', 'balance of trade', 'dairy')
# Series where a LOWER print favours the currency.
LOWER = ('unemployment', 'claimant', 'jobless')


def expected(name):
    n = name.lower()
    for k in LOWER:
        if k in n:
            return '<'
    for k in HIGHER:
        if k in n:
            return '>'
    return None


def channel_check():
    """Every whitelist row must sit in the right CHANNEL (F-70).

    Jeff, 2026-08-31: "decreasing unemployment is better for the economy. But
    in Inflation we want it increasing because it poses for Interest Rate
    Hike"

    Two routes to the currency, opposite signs:
      ECONOMIC-HEALTH  unemployment, claimant, jobless   -> LOWER better
      RATE             inflation, cpi, ppi               -> HIGHER better

    Both read as "bad news" in plain language, which is exactly how one flat
    "lower is better" list came to invert every inflation forecast.
    """
    import week_ahead as wa
    problems = []
    for cat, iso, name, act, prev, ref, thr, verd in sm.ROWS:
        n = name.lower()
        in_health = any(k in n for k in wa.LOWER_IS_BETTER)
        in_rate = wa.rate_channel(name)
        if in_health and in_rate:
            problems.append((sm.LABEL[iso], name,
                             'sits in BOTH channels - the sign is ambiguous'))
        if cat == 'Inflation' and not in_rate:
            problems.append((sm.LABEL[iso], name,
                             'is an Inflation row but not in the RATE channel'
                             ' - a rising print would grade backwards'))
        if in_health and cat == 'Inflation':
            problems.append((sm.LABEL[iso], name,
                             'an Inflation row in the ECONOMIC-HEALTH list'
                             ' - this is F-70 exactly'))
    return problems


def main():
    bad = []
    checked = 0
    for cat, iso, name, act, prev, ref, thr, verd in sm.ROWS:
        t = thr.strip().lower()
        if 'prev' not in t:
            continue
        checked += 1
        want = expected(name)
        if want is None:
            continue
        got = '<' if t.startswith('<') else '>' if t.startswith('>') else '?'
        if got != want:
            bad.append((sm.LABEL[iso], name, thr, verd, want))
    print('R-28 THRESHOLD DIRECTION AUDIT (F-68)')
    print('  %d rows use a *Prev threshold; %d checked against series type'
          % (checked, checked))
    print()
    if bad:
        for c, n, thr, verd, want in bad:
            print('  ** %-4s %-38s threshold %r verdict %s'
                  % (c, n[:38], thr, verd))
            print('     expected %sPrev - %s'
                  % (want, 'lower is better' if want == '<'
                     else 'higher is better'))
        raise SystemExit(
            chr(10) + '%d row(s) have a threshold pointing the WRONG WAY.'
            % len(bad) + chr(10)
            + 'The THRESHOLD says which direction favours the currency.'
            + chr(10)
            + 'The VERDICT says what happened. Do not write the threshold'
            + chr(10) + 'to describe the last move - that inverts the grade'
            + chr(10) + '(F-68: a confidence MISS graded as a BEAT).')
    print('  Every *Prev threshold points the way its series does.')
    print()
    ch = channel_check()
    if ch:
        print('  ** CHANNEL PROBLEMS (F-70) **')
        for c, n, why in ch:
            print('    %-4s %-38s %s' % (c, n[:38], why))
        raise SystemExit('%d row(s) in the wrong channel. Economic-health'
                         ' series want LOWER; rate-channel series want'
                         ' HIGHER.' % len(ch))
    print('  Every row sits in the right channel (F-70).')


if __name__ == '__main__':
    main()
