# -*- coding: utf-8 -*-
"""Capture the economic calendar from biquote, in our capture format.

*** WHY THIS EXISTS. Trading Economics locked past and future data, which is
the source every _cal_full.json capture came from. That did not just stop new
captures - it ended the only path to the EXPECTATION a print was scored
against, which is the F-185/186/187 defect class.

biquote (https://biquote.io/api/calendar) is free, keyless, returns all eight
of our currencies, carries `forecast` BEFORE a print lands, and has history
back beyond August with ~96% of scorable rows holding an actual. Measured,
not assumed - see the coverage table in the 17 Nov research.

*** WHAT THIS DELIBERATELY DOES NOT DO.

It does not re-implement whitelist matching. week_ahead.match() carries F-36,
F-37 and F-49 - token-set matching, the _NOT list, and the national-release
rule that stops Spain's 'retail sales yoy' becoming EUR Retail Sales YoY.
Those were paid for in published errors. This module hands rows to that
matcher in the shape it already expects.

It writes the SAME format as capture_calendar.py: a list of dicts with
iso/event/date/time/actual/consensus/forecast/previous. Every consumer
(25 modules read captures directly) keeps working unchanged.

*** ONE FIELD WE DO NOT HAVE, AND MUST NOT FAKE.

TE distinguished `consensus` (a survey of economists) from `forecast` (TE's
own model). biquote returns ONE field, `forecast`, and its docs do not say
which it is. LD-155 says consensus supersedes forecast, so writing biquote's
number into `consensus` would silently promote an unknown quantity to the
higher authority.

So it goes into `forecast` and `consensus` stays empty. inflation_decision()
already falls back to forecast when consensus is absent, which is exactly
the correct behaviour here. Nothing is invented and nothing is promoted.

    python pipelines/capture_biquote.py                 # dry run, last 30d + 30d
    python pipelines/capture_biquote.py --write         # write the capture
    python pipelines/capture_biquote.py --from 2026-08-01 --to 2026-11-17 --write
"""
import io
import os
import sys
import json
import time
import datetime as dt
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phtime as pt

API = 'https://biquote.io/api/calendar'
OUT = os.path.join(REPO, 'data/raw/calendar')

# biquote country code -> our ISO. The Eurozone is 'EU' there and 'EA' here.
# DE/FR/ES/IT are SEPARATE codes at biquote, so filtering to EU already
# excludes the national prints that F-37's guard had to catch after the fact.
CODE = {'US': 'US', 'EU': 'EA', 'GB': 'GB', 'JP': 'JP',
        'AU': 'AU', 'NZ': 'NZ', 'CA': 'CA', 'CH': 'CH'}
WANT = ','.join(sorted(CODE))

# biquote caps a response at 200 rows and gives no pagination parameter, so
# a wide range is walked in slices small enough to stay under the cap.
# MEASURED, not guessed: 10-day slices over the eight countries returned 196
# and 200 rows in Nov 2026 - the second was AT the cap and had lost its tail.
# 5 days runs ~100, which leaves headroom for a heavy release week. The
# truncation check below is the real guard; this is just a sensible default.
SLICE_DAYS = 5
CAP = 200


def fetch(frm, to, tries=3):
    """One slice, as a list of raw biquote rows."""
    url = '%s?from=%s&to=%s&countries=%s' % (API, frm, to, WANT)
    last = None
    for n in range(tries):
        try:
            r = urllib.request.urlopen(url, timeout=45)
            return json.loads(r.read().decode('utf-8'))
        except Exception as e:                     # transient - back off
            last = e
            time.sleep(1.5 * (n + 1))
    raise RuntimeError('biquote fetch failed for %s..%s: %s' % (frm, to, last))


def num(v):
    """biquote returns numbers; our captures hold strings. None stays None.

    F-73: an absent value is absent. It must never become '0' or ''.
    """
    if v is None:
        return ''
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


# *** F-191 - SOURCE-SPECIFIC SERIES NAMES, FIXED AT THE SOURCE.
#
# Switzerland publishes a seasonally adjusted unemployment rate AND an
# n.s.a. one. We have always scored the N.S.A. figure (fact table 3%, and
# every TE capture that carried an actual gave 3%); the adjusted series
# printed 3.1 the same day.
#
# biquote names them 'unemployment rate' (ADJUSTED) and 'unemployment rate
# n.s.a.'. TE named the n.s.a. one 'unemployment rate oct'. So the BARE name
# means opposite things in the two sources, and week_ahead's _NOT list
# cannot tell them apart - there is no token to exclude.
#
# Renaming it here keeps the knowledge where the ambiguity is (this source's
# vocabulary) instead of pushing a source quirk into the shared matcher.
RENAME = {
    ('CH', 'unemployment rate'): 'unemployment rate s.a.',

    # --- F-193 / R-52. GROUP A: the same series, spelled differently.
    # biquote says 'cpi y/y' where TE said 'inflation rate yoy'. Nothing
    # about the measurement changed, only the words, so these are spelling
    # repairs and carry no identity risk.
    ('AU', 'cpi y/y'): 'inflation rate yoy',
    ('CA', 'cpi y/y'): 'inflation rate yoy',
    ('CH', 'cpi y/y'): 'inflation rate yoy',
    ('JP', 'cpi y/y'): 'inflation rate yoy',
    ('NZ', 'cpi y/y'): 'inflation rate yoy',
    ('US', 'cpi y/y'): 'inflation rate yoy',
    ('EA', 'cpi y/y'): 'inflation rate yoy final',

    ('AU', 'gdp q/q'): 'gdp growth rate qoq',
    ('CA', 'gdp q/q'): 'gdp growth rate qoq',
    ('CH', 'gdp q/q'): 'gdp growth rate qoq',
    ('EA', 'gdp q/q'): 'gdp growth rate qoq',
    ('GB', 'gdp q/q'): 'gdp growth rate qoq',
    ('JP', 'gdp q/q'): 'gdp growth rate qoq',
    ('NZ', 'gdp q/q'): 'gdp growth rate qoq',
    ('US', 'gdp q/q'): 'gdp growth rate qoq',

    ('CH', 'retail sales y/y'): 'retail sales yoy',
    ('EA', 'retail sales y/y'): 'retail sales yoy',
    ('JP', 'retail sales y/y'): 'retail sales yoy',
    ('US', 'retail sales y/y'): 'retail sales yoy',

    ('EA', 'industrial production y/y'): 'industrial production yoy',
    ('JP', 'industrial production y/y'): 'industrial production yoy final',
    ('JP', 'household spending y/y'): 'household spending yoy',
    ('JP', 'machine tool orders y/y'): 'machine tool orders yoy',
    ('US', 'personal spending m/m'): 'personal spending mom',
    ('CA', 'building permits m/m'): 'building permits mom',
    ('US', 'building permits m/m'): 'building permits mom final',

    # 'fed industrial production y/y' IS the series we have always scored -
    # a source prefix, not a different measurement. This was in the first
    # Group B draft as needing a ruling; the capture shows the YoY is
    # published (2.2 on 16 Oct, 2.1 on 17 Nov), so it is Group A.
    ('US', 'fed industrial production y/y'): 'industrial production yoy',

    # --- GROUP B: different NAME, same series. Each of these is an identity
    # ruling by Jeff (R-41, F-3), not a spelling repair.
    #
    # Spacing only, but the source also carries 'private nonfarm payrolls'.
    # The headline print is the bare name, which is the one we score.
    ('US', 'nonfarm payrolls'): 'non farm payrolls',
    # No Flash/Final split at this source; the single PMI print is the Final.
    ('AU', 's&p global manufacturing pmi'): 's&p global mfg pmi final',
    ('EA', 's&p global manufacturing pmi'): 's&p global mfg pmi final',
    # au Jibun Bank sponsors the S&P Global Japan PMI - same survey, same
    # compiler, sponsor's name in front.
    ('JP', 'au jibun bank manufacturing pmi'): 's&p global mfg pmi final',
    ('AU', 'westpac-mi consumer sentiment m/m'): 'westpac consumer conf change',
    # Indeed left the sponsorship; ANZ still compiles the same job ads series.
    ('AU', 'anz job advertisements m/m'): 'anz-indeed job ads mom',
    ('CH', 'consumer climate'): 'consumer confidence',
    ('NZ', 'businessnz manufacturing index'): 'business nz pmi',
    ('NZ', 'gdt price index'): 'global dairy trade price index',
    # Our row says 'Final' because TE split a flash and a final estimate.
    # This source publishes ONE euro-area consumer confidence print, named
    # 'consumer confidence index' - so the single print IS the final, the
    # same ruling already applied to the Mfg PMI rows above. Without this
    # the row stays unreadable on a missing 'final' token, which is a
    # vocabulary artefact and not a real absence.
    ('EA', 'consumer confidence index'): 'consumer confidence final',
}

# *** THE ROWS LEFT DELIBERATELY UNREADABLE (F-193 group C), AND WHY.
#
# A visible gap is honest. A wrong map is not - it makes the whitelist
# readable again by substituting a DIFFERENT indicator, and the score then
# computes, looks fine, and measures something else. That is the invented
# presence LD-59 forbids, arriving through the front door instead of through
# the matcher. Each of these was offered a candidate and REFUSED:
#
#   US Durable Goods Ex Transp MoM   source has 'excl. defense m/m'
#                                    ex-DEFENSE is not ex-TRANSPORT.
#   JP Machinery Orders YoY          source has 'core machinery orders y/y'
#                                    core excludes volatile items; we score
#                                    the headline.
#   NZD ANZ Roy Morgan Consumer Conf source has 'anz business confidence'
#                                    a BUSINESS survey is not a CONSUMER one.
#   AU Building Permits YoY Final    source has 'building approvals m/m'
#   CA Retail Sales YoY              source has 'retail sales m/m'
#   NZ Electronic Retail Card Spend  source has '... m/m' and a y/y
#   US Manufacturing Production YoY  source has 'fed ... production m/m'
#
# *** WHY THE m/m SUBSTITUTIONS WERE DECLINED, WITH THE NUMBERS.
# A MoM and a YoY are different MEASUREMENTS of the same data, not two
# names for one series, and score_model's thresholds are tuned to YoY
# magnitudes. Measured on one release date, 17 Nov 2026:
#
#     US industrial production    -0.4 m/m   vs   +2.1 y/y
#     NZ electronic card sales    -0.7 m/m   vs   +0.3 y/y
#
# Opposite signs, several times apart. Feeding a MoM into a YoY row does not
# degrade a score, it INVERTS it - a confident BAD where the series says
# GOOD. So these stay unreadable until the source publishes the YoY, or
# Jeff adds a MoM row to the closed set with its own thresholds.
#
#   AU Household Spending YoY   genuinely absent from the source
#   NZ Building Permits MoM     NZ publishes 'building consents m/m'; the
#                               consents/permits identity is Jeff's to rule
#                               on and has not been ruled.


def convert(raw):
    """biquote row -> our capture row, or None if it is not ours."""
    iso = CODE.get(raw.get('countryCode'))
    if iso is None:
        return None
    t = str(raw.get('time') or '')
    if len(t) < 10:
        return None
    date = t[:10]
    # biquote times are ISO with a timezone; our captures hold a local-ish
    # 'HH:MM AM/PM' string that phtime parses. Keep the clock, drop the zone.
    hhmm = ''
    if len(t) >= 16 and 'T' in t:
        try:
            h, m = int(t[11:13]), int(t[14:16])
            ap = 'AM' if h < 12 else 'PM'
            h12 = h % 12 or 12
            hhmm = '%02d:%02d %s' % (h12, m, ap)
        except ValueError:
            hhmm = ''
    ev = str(raw.get('name') or '').strip().lower()
    ev = RENAME.get((iso, ev), ev)              # F-191
    return {
        'iso': iso,
        'event': ev,
        'date': date,
        'time': hhmm,
        'actual': num(raw.get('actual')),
        # *** consensus LEFT EMPTY ON PURPOSE - see the module docstring.
        'consensus': '',
        'forecast': num(raw.get('forecast')),
        'previous': num(raw.get('previous')),
        'source': str(raw.get('source') or 'biquote'),
        'source_url': str(raw.get('sourceUrl') or ''),
        'importance': str(raw.get('importance') or ''),
    }


def capture(frm, to, write=False):
    days = (dt.date(*map(int, to.split('-')))
            - dt.date(*map(int, frm.split('-')))).days
    rows = []
    seen = set()
    truncated = []
    cur = dt.date(*map(int, frm.split('-')))
    end = dt.date(*map(int, to.split('-')))
    while cur <= end:
        stop = min(cur + dt.timedelta(days=SLICE_DAYS - 1), end)
        # *** biquote returns HTTP 400 when from == to. A range whose length
        # divides exactly by SLICE_DAYS leaves a one-day remainder and the
        # whole capture died on the last slice. Verified: from==to is 400,
        # any two-day span is 200. Widening by a day costs nothing - the
        # overlap is de-duplicated on (iso, event, date) below.
        if stop == cur:
            cur = cur - dt.timedelta(days=1)
        batch = fetch(cur.isoformat(), stop.isoformat())
        # *** IF A SLICE COMES BACK AT THE CAP IT IS TRUNCATED AND WE SAY SO.
        # Silently losing the tail of a slice is exactly the shape of R-50:
        # no error, just fewer rows than the world has.
        if len(batch) >= CAP:
            truncated.append('%s..%s' % (cur.isoformat(), stop.isoformat()))
        for raw in batch:
            r = convert(raw)
            if r is None:
                continue
            k = (r['iso'], r['event'], r['date'])
            if k in seen:                 # slices overlap at boundaries
                continue
            seen.add(k)
            rows.append(r)
        print('  %s..%s  %3d raw  %4d kept' % (cur.isoformat(),
                                               stop.isoformat(),
                                               len(batch), len(rows)))
        cur = stop + dt.timedelta(days=1)

    rows.sort(key=lambda r: (r['date'], r['iso'], r['event']))

    print()
    per = {}
    for r in rows:
        per[r['iso']] = per.get(r['iso'], 0) + 1
    print('  TOTAL %d rows over %d days' % (len(rows), days + 1))
    for iso in sorted(CODE.values()):
        n = per.get(iso, 0)
        print('    %-4s %4d rows %s' % (iso, n, '*** ZERO ***' if not n else ''))
    gap = [i for i in CODE.values() if not per.get(i)]
    if gap:
        print()
        print('  *** COVERAGE GAP: %s ***' % ', '.join(sorted(gap)))
    else:
        print()
        print('  COVERAGE COMPLETE - every whitelisted currency has rows.')

    if truncated:
        print()
        print('  *** %d SLICE(S) HIT THE %d-ROW CAP - rows were lost:'
              % (len(truncated), CAP))
        for s in truncated:
            print('      %s' % s)
        print('      Lower SLICE_DAYS and re-run.')

    scor = [r for r in rows if r['date'] < dt.date.today().isoformat()]
    act = sum(1 for r in scor if r['actual'])
    fc = sum(1 for r in rows if r['forecast'])
    print()
    print('  past rows %d, with actual %d (%d%%)'
          % (len(scor), act, 100 * act // max(len(scor), 1)))
    print('  all rows %d, with forecast %d (%d%%)'
          % (len(rows), fc, 100 * fc // max(len(rows), 1)))

    if not write:
        print()
        print('  DRY RUN - pass --write to save the capture.')
        return rows

    if not rows:
        # An empty capture is worse than none: it reads as a real vintage
        # holding no events, which is how a blocked fetch poisons the
        # archive. Refuse rather than write it.
        print()
        print('  *** REFUSING TO WRITE AN EMPTY CAPTURE ***')
        return rows

    stamp = dt.datetime.now(pt.PHT).strftime('%Y-%m-%d_%H%M') + 'PHT'
    path = os.path.join(OUT, '%s_cal_full.json' % stamp)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    print()
    print('  written %s' % os.path.basename(path))
    return rows


def main():
    a = sys.argv[1:]
    today = dt.date.today()

    def opt(flag, default):
        return a[a.index(flag) + 1] if flag in a else default

    frm = opt('--from', (today - dt.timedelta(days=30)).isoformat())
    to = opt('--to', (today + dt.timedelta(days=30)).isoformat())
    print('BIQUOTE CAPTURE  %s .. %s' % (frm, to))
    print('  %s' % API)
    print()
    capture(frm, to, write='--write' in a)
    return 0


if __name__ == '__main__':
    sys.exit(main())
