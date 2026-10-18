# -*- coding: utf-8 -*-
"""R-40 - IS ANY WHITELIST ROW STALE AGAINST A RELEASE WE ALREADY HAVE?

Jeff, 2026-09-13: "AUD Westpac Consumer Conf Change -- We already have latest
data of this. in the previous report it is also in the calibrator so we should
be reflecting the new values now"

He was right: Westpac printed -5.2% on 8 Sep and the fact table still held
6.0% from Aug/26. AUD's Spending category was +1.50 when it should have been
+0.50 - the difference between AUD tying NZD and AUD being alone at the bottom.

*** F-120 - WHY THE HAND-ROLLED CHECK MISSED IT. *** The 13 Sep refresh was a
one-off script that matched names with a plain substring test. 'westpac
consumer conf change' is NOT a substring of 'westpac consumer confidence
change sep' - CONF vs CONFIDENCE. week_ahead.match() normalises exactly that
abbreviation (F-64) and would have found it.

    A VINTAGE CHECK THAT DISAGREES WITH THE SCORER ABOUT WHAT A ROW *IS*
    WILL ALWAYS MISS ROWS.

So this module calls week_ahead.match() - the same matcher the calibrator and
the edition use. It is not a second opinion about row identity; there is only
one opinion, and this asks it.

WHY IT IS A GUARD RATHER THAN A SCRIPT. R-37 compares the fact tables to
score_model and R-38 compares thresholds to the spec - both verify the repo
against ITSELF and pass happily on data that is a week old. This is the only
check that asks whether what we hold is what the world last published.

    python pipelines/vintage_check.py               # since the last edition
    python pipelines/vintage_check.py 2026-09-06    # since a given date
"""
import io
import os
import sys
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phtime as pt
import week_ahead as wa
import score_model as sm

CCY = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}

# Rows whose actual lives somewhere other than score_model.ROWS, so a blank
# held value is correct rather than stale.
NO_HELD = ('GDP Growth Rate QoQ',)          # LD-117: calibrator-only

# F-123 - A VALUE THAT REPEATS HIDES A STALE VINTAGE.
#
# Jeff, 2026-09-14: "USD Inflation Rate YoY -- This is stale"
#
# He was right, and every guard in this repo said otherwise. US CPI printed
# Aug/26 at 3.4% on 11 Sep. We held Jul/26 at 3.4%. THE VALUES ARE IDENTICAL,
# so a comparison on value alone reports no staleness - and R-40, R-41 and
# R-37's vintage section all compare on value alone.
#
#     WE WERE NOT HOLDING THE RIGHT NUMBER. WE WERE HOLDING AN OLD
#     NUMBER THAT HAPPENED TO MATCH.
#
# The difference is not cosmetic. CPI at 3.4% after 3.5% is FALLING; at 3.4%
# after 3.4% it has STOPPED falling, and the threshold is ">2% & falling".
# Same cell, opposite story. Seven more rows carried the same defect (AUD Job
# Ads, AUD Building Permits, AUD NAB, CHF Consumer Confidence, CHF
# Unemployment, JPY Machine Tool Orders, NZD Business NZ PMI) - all flagged by
# R-37 as VINTAGE and all read past by me because the values matched.
#
# So the check is on (value, reference month), never value alone.
MONTHS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
          'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}


def te_month(event):
    """The reference month TE names in an event title, e.g. '... yoy aug'."""
    for w in reversed(str(event).lower().replace('/', ' ').split()):
        if w[:3] in MONTHS and len(w) <= 4:
            return MONTHS[w[:3]]
    return None


def our_month(ref):
    """The reference month we record, e.g. 'Aug/26' or 'Jun/26 (Q)'."""
    m = str(ref).strip().lower()[:3]
    return MONTHS.get(m)


def stale(since, until=None):
    """[(ccy, row, held, released, date, te_event)] for rows we hold stale."""
    names, held, refs = {}, {}, {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        c = sm.LABEL[iso]
        names.setdefault(c, []).append(name)
        held[(c, name)] = a
        refs[(c, name)] = ref

    found = {}
    for f in sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json'))):
        try:
            with io.open(f, encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception:
            continue
        for r in (data if isinstance(data, list) else data.get('events', [])):
            if not isinstance(r, dict):
                continue
            iso = r.get('iso')
            act = (r.get('actual') or '').strip()
            if iso not in CCY or not act:
                continue
            when = pt.te_pht(r.get('date'), r.get('time'))
            ds = when.strftime('%Y-%m-%d') if when else (r.get('date') or '')
            if not ds or ds <= since or (until and ds > until):
                continue
            ccy = CCY[iso]
            hit = wa.match(str(r.get('event', '')).lower(),
                           names.get(ccy, []), iso)
            if not hit:
                continue
            key = (ccy, hit)
            if key not in found or ds > found[key][0]:
                found[key] = (ds, act, str(r.get('event')))

    out = []
    for (c, n), (ds, act, raw) in sorted(found.items()):
        if n in NO_HELD:
            continue
        # F-139 - A ROW THAT CARRIES ITS OWN SPLIT IS NOT STALE.
        #
        # AUD and CAD Employment Change store the headline AND the breakdown:
        # "39.5K (FT -6.3K, PT +45.8K)". That is deliberate - LD-57 grades the
        # FULL-TIME component, and F-138 was me reading the headline and
        # missing that full time had gone negative. The split has to be
        # visible in the cell.
        #
        # But R-40 compares strings exactly, so it read the annotated cell as
        # different from TE's bare "39.5K" and called a correctly-refreshed
        # row STALE. A guard that fires on its own house style teaches you to
        # skip it - the F-120 lesson from the other direction.
        # F-159 - AN ISO CODE AND ITS CURRENCY GLYPH ARE THE SAME VALUE.
        #
        # Same shape as F-139 above, one axis over. We store EUR Balance of
        # Trade as "EUR-16.1B" and GBP as "GBP-0.920B"; TE renders the GLYPH,
        # "EUR-16.1B" and "GBP-0.920B". The NUMBERS are identical and the
        # vintages agree, but R-40 compares strings and reported both rows as
        # "THE EDITION IS SCORED ON DATA THE WORLD HAS SUPERSEDED" - on the
        # very build that had just refreshed them correctly.
        #
        # WHY NOT RESTYLE THE CELLS INSTEAD: the house style is already MIXED
        # and pre-existing (USD "$", CAD "C$", AUD "A$", NZD "NZ$", CHF "CHF",
        # JPY "JPY", EUR/GBP the ISO code). The other six pass only because TE
        # happens to render them the way we store them. Rewriting live cells
        # mid-build to satisfy a string compare is the wrong direction - the
        # GUARD should know that a symbol is presentation, which is exactly
        # what F-139 established for the employment split.
        _CCY_GLYPH = {u'€': 'EUR', u'£': 'GBP', u'¥': 'JPY',
                      u'₣': 'CHF'}

        def _norm_ccy(v):
            v = v or ''
            for g, iso in _CCY_GLYPH.items():
                v = v.replace(g, iso)
            return v

        _h = (held.get((c, n)) or '')
        _hn, _an = _norm_ccy(_h), _norm_ccy(act)
        _same = (_hn == _an) or (_an and _hn.startswith(_an + ' ('))
        if not _same:
            out.append((c, n, held.get((c, n)), act, ds, raw))
            continue
        tm, om = te_month(raw), our_month(refs.get((c, n), ''))
        if tm and om and tm > om:
            out.append((c, n, '%s (%s)' % (held.get((c, n)), refs.get((c, n))),
                        '%s (%s)' % (act, raw.split()[-1][:3].title()),
                        ds, raw))
    return out, len(found)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args:
        since = args[0]
    else:
        hdr = io.open(os.path.join(REPO, 'STATE.md'),
                      encoding='utf-8').read()[:1200]
        since = ''
        for line in hdr.splitlines():
            if line.startswith('prev_edition:'):
                since = line.split(':', 1)[1].strip().split()[0]
                break
        since = since or '2026-09-06'

    rows, seen = stale(since)
    print('R-40 VINTAGE CHECK   releases after %s' % since)
    print('  whitelist rows with a print in the window : %d' % seen)
    print('  rows whose held value is STALE            : %d' % len(rows))
    print()
    if rows:
        print('%-4s %-34s %-12s %-12s %-11s %s'
              % ('CCY', 'ROW', 'HELD', 'RELEASED', 'WHEN', 'TE EVENT'))
        for c, n, old, new, ds, raw in rows:
            print('%-4s %-34s %-12s %-12s %-11s %s'
                  % (c, n[:34], old or '(blank)', new, ds, raw[:30]))
        print()
        print('  *** THE EDITION IS SCORED ON DATA THE WORLD HAS SUPERSEDED.')
        sys.exit(1)
    print('  every whitelist row holds the latest print we have captured')
