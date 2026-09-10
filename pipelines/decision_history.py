# -*- coding: utf-8 -*-
"""WHEN DID EACH BANK LAST DECIDE, AND WHEN DOES IT DECIDE NEXT (F-102).

Jeff, 2026-09-09, on the RBNZ: "NZD fell because the RBNZ statement read
softer... The tone should impact the score so we can recalibrate the rankings
early."

WHY THIS EXISTS RATHER THAN A SCORING CHANGE. Four fixes were on the table -
decay the realised term, carry the last path forward, a separate Expectations
category, or leave it. Every one of the first three needed a fact the repo
COULD NOT PRODUCE: the date each bank last decided. The calendar archive
begins 2026-08-17, so six of eight currencies had no visible last decision
and any fix would have applied to NZ and CA alone.

THAT IS LD-23's FAILURE MODE - an input available to some currencies and not
others - and it is the same reason CB speech tone was rejected: TE schedules
those events but publishes NO NUMERIC ACTUAL for any of them (verified
2026-09-09: 0 of 20 rows in the capture carried one).

SO THE GAP WAS NEVER THE SCORING RULE. It is that we cannot see far enough
back to compute one, AND WE CANNOT FIX THAT BY FETCHING HARDER.

F-103, found while trying to. I claimed TE's country pages span five months
because the raw HTML carries dates from 2026-05-06. THEY DO NOT. The page
renders ~37 rows and every one of them is FORWARD of today; the May date is
page furniture - a filter widget - not a row. I read a range off the file
without checking it belonged to a table row, which is the same error shape as
the GDP coverage claim the day before: a true conclusion reached from
evidence that did not support it. A fresh capture backfilled NOTHING.

TE's free pages are forward-looking. Decision history is behind their API or
inside JS-rendered widgets, and LD-23 will not accept a source we can only
reach for some currencies.

THEREFORE THE HISTORY CAN ONLY ACCUMULATE GOING FORWARD, from captures we
take. That is what makes this file worth running WEEKLY rather than once: in
six weeks there will be a decision timeline for all eight currencies, and the
scoring question can be answered on evidence instead of on two currencies.

WHAT THIS DOES NOT DO. It does not change a single score. It reports the
decision timeline so that a future scoring decision can be made on evidence
for all eight currencies instead of two. Jeff, 2026-09-10: "lets do that
then" - log the gap, extend the reach, leave the scoring alone.

    python pipelines/decision_history.py            # report
    python pipelines/decision_history.py --write    # ... and save the JSON

NOTE ON MATCHING. TE does NOT spell these rows "Interest Rate Decision" on
the country pages - NZ's reads "RBNZ Interest Rate". Matching on the long
form returns ZERO and looks like an absence (F-73). Match on the bank name
plus 'interest rate', and on 'rate decision', and accept either.
"""
import io, os, re, sys, json, glob
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

OUT = os.path.join(REPO, 'data', 'derived', 'decision_history.json')

# The bank whose decision sets each currency's policy rate.
BANK = {'US': 'fed', 'EA': 'ecb', 'GB': 'boe', 'JP': 'boj',
        'AU': 'rba', 'NZ': 'rbnz', 'CA': 'boc', 'CH': 'snb'}

CCYS = ('USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF')
ISO = {'USD': 'US', 'EUR': 'EA', 'GBP': 'GB', 'JPY': 'JP',
       'AUD': 'AU', 'NZD': 'NZ', 'CAD': 'CA', 'CHF': 'CH'}


def is_decision(iso, event):
    """Does this row set the policy rate?

    TE's country pages use the SHORT form ('RBNZ Interest Rate'); the global
    page uses the long one ('RBNZ Interest Rate Decision'). Matching only the
    long form returns zero rows and reads as an absence rather than as a
    naming difference - F-73's exact shape, and it cost an hour on 2026-09-10.

    EXCLUDES speeches, minutes and press conferences: those are commentary
    ABOUT a decision, not the decision. 'RBNZ Silk Speech' also lives under
    /interest-rate on TE and would otherwise match.
    """
    e = (event or '').lower()
    bank = BANK.get(iso, '')
    if any(w in e for w in ('speech', 'minutes', 'press conf', 'statement',
                            'testimony', 'projections', 'bulletin')):
        return False
    if 'rate decision' in e:
        return True
    return bool(bank) and bank in e and 'interest rate' in e


def from_captures():
    """Every decision row across the whole capture archive, deduped.

    A row is keyed on (iso, date) and the RICHEST version wins - TE blanks an
    actual once the next occurrence is scheduled (F-95), so an older capture
    often holds a value the newest one has already dropped.
    """
    rows = {}
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
            iso, date = r.get('iso'), r.get('date')
            if not iso or not date or iso not in BANK:
                continue
            if not is_decision(iso, r.get('event')):
                continue
            k = (iso, date)
            cur = rows.setdefault(k, {'iso': iso, 'date': date,
                                      'event': r.get('event'),
                                      'actual': '', 'forecast': '',
                                      'previous': ''})
            for fld in ('actual', 'forecast', 'previous'):
                v = (r.get(fld) or '').strip()
                if v and not cur[fld]:
                    cur[fld] = v
    return rows


def timeline(asof=None):
    """{ccy: {'last', 'last_rate', 'next', 'next_forecast', 'days_since'}}.

    LAST is the most recent decision ON OR BEFORE asof that carries an
    ACTUAL. NEXT is the earliest decision AFTER asof. A decision dated on or
    before asof with no actual is neither - it is a row TE has scheduled and
    not yet filled, and calling it either would assert something we cannot
    see (F-73).
    """
    asof = asof or dt.date.today().isoformat()
    rows = from_captures()
    out = {}
    for ccy in CCYS:
        iso = ISO[ccy]
        mine = sorted([r for r in rows.values() if r['iso'] == iso],
                      key=lambda r: r['date'])
        past = [r for r in mine if r['date'] <= asof and r['actual']]
        future = [r for r in mine if r['date'] > asof]
        last = past[-1] if past else None
        nxt = future[0] if future else None
        days = None
        if last:
            a = dt.date(*map(int, last['date'].split('-')))
            b = dt.date(*map(int, asof.split('-')))
            days = (b - a).days
        out[ccy] = {
            'last': last['date'] if last else None,
            'last_rate': last['actual'] if last else None,
            'days_since': days,
            'next': nxt['date'] if nxt else None,
            'next_forecast': (nxt.get('forecast') or None) if nxt else None,
            'n_seen': len(mine),
        }
    return out


def report(asof=None):
    asof = asof or dt.date.today().isoformat()
    tl = timeline(asof)
    print('DECISION HISTORY   as of %s' % asof)
    print()
    print('%-4s %-12s %-9s %9s %-12s %-9s %s'
          % ('CCY', 'LAST', 'RATE', 'DAYS AGO', 'NEXT', 'FORECAST', 'ROWS'))
    for ccy in CCYS:
        t = tl[ccy]
        print('%-4s %-12s %-9s %9s %-12s %-9s %d'
              % (ccy,
                 t['last'] or '-',
                 t['last_rate'] or '-',
                 t['days_since'] if t['days_since'] is not None else '-',
                 t['next'] or 'beyond horizon',
                 t['next_forecast'] or '-',
                 t['n_seen']))
    blind = [c for c in CCYS if tl[c]['last'] is None]
    print()
    if blind:
        print('  *** NO LAST DECISION VISIBLE: %s' % ', '.join(blind))
        print('      Any rule keyed on decision age would apply to the other')
        print('      %d only - that is LD-23\'s failure mode, and it is why'
              % (len(CCYS) - len(blind)))
        print('      the scoring was LEFT ALONE rather than patched.')
    else:
        print('  every currency has a visible last decision - a rule keyed on')
        print('  decision age could now be applied on equal terms (LD-23).')
    no_path = [c for c in CCYS if tl[c]['next'] is None]
    if no_path:
        print()
        print('  NO FORWARD MEETING IN WINDOW: %s' % ', '.join(no_path))
        print('      These score PATH as ABSENT, so their rate score is 100%')
        print('      backward-looking. This is the RBNZ gap, reported rather')
        print('      than silently renormalised.')
    return tl


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    asof = args[0] if args else None
    tl = report(asof)
    if '--write' in sys.argv:
        d = os.path.dirname(OUT)
        if not os.path.isdir(d):
            os.makedirs(d)
        io.open(OUT, 'w', encoding='utf-8').write(
            json.dumps(tl, ensure_ascii=False, indent=1))
        print()
        print('  written %s' % OUT)
