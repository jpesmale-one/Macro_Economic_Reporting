# -*- coding: utf-8 -*-
"""LD-173 - WAS THE SESSION RISK ON OR RISK OFF?

Jeff, 2026-10-27:

    "I think on the daily report we need to add wether yesterday was a Risk
     On or Risk Off day. CADCHF is a risk on trade let's see if the market
     sentiment is aligning with the move"

*** THE POINT IS ALIGNMENT, NOT A FORECAST. pair_select already classifies
every selected pair as RISK ON, RISK OFF or EITHER from the role of its two
legs - CADCHF LONG is long Commodity against Safe haven, so it is RISK ON.
What has been missing is the other half of that comparison: what the SESSION
actually was. A RISK ON pair paying on a risk-off day is paying for some
reason other than the one we selected it for, and that is worth knowing
before it is mistaken for the thesis working.

HOW IT IS DERIVED, AND WHY IT NEEDS NO NEW INPUT. ft.ROLE is a closed,
house-defined map: AUD/CAD/NZD are Commodity, GBP/EUR are Cyclical,
USD/JPY/CHF are Safe haven. The session already gives a USD-neutralised
strength per currency. So the tone is simply which basket outperformed:

    tone = mean(Commodity strength) - mean(Safe haven strength)

*** CYCLICAL IS DELIBERATELY EXCLUDED FROM THE SPREAD. GBP and EUR sit
between the two baskets - pair_select itself scores a Cyclical/Commodity
pair as EITHER rather than assigning it a side - so including them would
blur the very distinction being measured. They are reported separately so a
reader can see where they fell.

LD-23 IS SATISFIED: every currency contributes on identical terms, from the
same session bars, with no per-currency source.

*** AND THE USD CAVEAT IS STATED, NOT HIDDEN. USD is classed Safe haven
here, which is right for risk-off flows but makes the measure partly a USD
measure - and the session strength is already USD-neutralised, so a pure
dollar move cannot create tone on its own. That is a feature, but it also
means a day driven by Fed expectations rather than risk appetite can read as
tone when it is really rates. The daily names the catalyst beside this, so
the two can be read together.

LD-4: this describes what price did. No entries, exits, stops or targets.
F-73: an unavailable session returns None, never a guessed NEUTRAL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fact_tables as ft
import daily_report as dr

HAVEN = 'Safe haven'
COMMODITY = 'Commodity'
CYCLICAL = 'Cyclical'

# Bands in percentage points of basket spread, SET FROM THE ACTUAL
# DISTRIBUTION rather than guessed. Over the 300 sessions on disk the
# absolute spread runs:
#     25th pct 0.094   50th 0.190   75th 0.317   90th 0.481
#
# *** MY FIRST DRAFT ASSERTED THE MEDIAN WAS ~0.25pp AND IT IS 0.190. The
# bands happened to land in a defensible place anyway, but the stated reason
# was wrong, and a threshold justified by a number nobody checked is exactly
# the shape this project keeps finding. Measured, then written down.
#
# MILD at the 40th percentile and CLEAR at the 90th means roughly 40% of
# sessions read MIXED and 12% read unambiguous - which matches the intent:
# most days do not have a clean risk tone, and the label should say so
# rather than manufacture one.
# STILL A CONVENTION, not a finding. The number a reader should trust is the
# SPREAD, which is always printed beside the label.
CLEAR = 0.48
MILD = 0.15


def baskets():
    """{role: [ccy, ...]} from the house role map."""
    out = {}
    for c, r in ft.ROLE.items():
        out.setdefault(r, []).append(c)
    return dict((k, sorted(v)) for k, v in out.items())


def tone(day):
    """(label, spread, detail) for one session, or (None, None, {}).

    spread = mean Commodity strength - mean Safe haven strength, in
    percentage points. Positive is risk ON.
    """
    s = dr.session_strength(day)
    if not s:
        return None, None, {}
    b = baskets()
    com = [s[c] for c in b.get(COMMODITY, []) if c in s]
    hav = [s[c] for c in b.get(HAVEN, []) if c in s]
    cyc = [s[c] for c in b.get(CYCLICAL, []) if c in s]
    if not com or not hav:
        return None, None, {}
    mc = sum(com) / len(com)
    mh = sum(hav) / len(hav)
    sp = mc - mh
    if sp >= CLEAR:
        lbl = 'RISK ON'
    elif sp >= MILD:
        lbl = 'mild RISK ON'
    elif sp <= -CLEAR:
        lbl = 'RISK OFF'
    elif sp <= -MILD:
        lbl = 'mild RISK OFF'
    else:
        lbl = 'MIXED'
    detail = {'commodity': mc, 'haven': mh,
              'cyclical': (sum(cyc) / len(cyc)) if cyc else None,
              'per_ccy': s, 'baskets': b}
    return lbl, sp, detail


def aligns(pair_category, label):
    """Does a pair's category agree with the session tone?

    Returns 'ALIGNED', 'AGAINST', or 'n/a'. A pair classed EITHER has no
    side to agree with, and a MIXED session has no tone to agree with - both
    return 'n/a' rather than being forced into a verdict (F-73: never a
    guessed answer).
    """
    if not label or label == 'MIXED' or pair_category not in ('RISK ON',
                                                              'RISK OFF'):
        return 'n/a'
    on = label.endswith('RISK ON')
    want_on = (pair_category == 'RISK ON')
    return 'ALIGNED' if on == want_on else 'AGAINST'


def report(day):
    lbl, sp, d = tone(day)
    if lbl is None:
        return 'RISK TONE %s: no session data' % day
    L = ['RISK TONE   %s' % day,
         '  %s   basket spread %+.3f pp' % (lbl, sp),
         '',
         '  Commodity  %+.3f%%   (%s)'
         % (d['commodity'], ' '.join(d['baskets'].get(COMMODITY, []))),
         '  Safe haven %+.3f%%   (%s)'
         % (d['haven'], ' '.join(d['baskets'].get(HAVEN, []))),
         '  Cyclical   %s   (%s)  - excluded from the spread'
         % (('%+.3f%%' % d['cyclical']) if d['cyclical'] is not None
            else '  n/a ',
            ' '.join(d['baskets'].get(CYCLICAL, [])))]
    return '\n'.join(L)


if __name__ == '__main__':
    import datetime as dt
    day = sys.argv[1] if len(sys.argv) > 1 else (
        dt.date.today() - dt.timedelta(days=1)).isoformat()
    print(report(day))
