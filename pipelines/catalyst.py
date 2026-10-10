# -*- coding: utf-8 -*-
"""WHY DID THIS CURRENCY MOVE? - THE WHOLE CALENDAR, NOT OUR WHITELIST.

Jeff, 2026-10-11:

    "let's not limit it on the indicators we tracked. the goal of this report
     is to find explanation if there's no news important to us happened on
     that day then my question is why it is strong/weak? what could have
     caused it? Answer this on the report always not just based on the
     indicators we tracked"

*** THE MEASURED GAP. The daily reported Monday 5 Oct as "nothing scheduled"
for every currency. The captures hold SIXTY-NINE ROWS for that date - four ECB
speeches including Lane and Schnabel, US ISM Services, euro-area PPI, the
Australian TD-MI inflation gauge, NZIER business confidence, and a wall of
European services PMIs. We had the data and were filtering it out, because
releases_by_day() keeps only the 78 whitelist rows.

THE WHITELIST EXISTS TO SCORE, NOT TO EXPLAIN. LD-23 requires an input to be
available for all eight currencies on equal terms before it can move a NUMBER.
Nothing of the sort applies to asking what happened - a speech by one ECB
member explains a euro move perfectly well without needing a counterpart in
Switzerland.

FOUR TIERS, strongest evidence first, because "what moved it" deserves an
ordering rather than a list:

  1. SURPRISE   a release whose actual missed or beat its forecast, ranked by
                how far. This is the only tier that can be measured.
  2. CB SPEAK   central bank speeches and minutes. Named, never scored - we
                cannot read tone (LD-107) but we can say who spoke.
  3. SCHEDULED  anything else that landed, as context.
  4. NOTHING    said plainly, with what we checked, so the reader knows the
                silence was looked for rather than assumed.

*** TIER 4 IS STILL AN ANSWER AND IT MUST STAY HONEST. If 69 rows landed and
none of them touches this currency, the report says so AND says what it
cannot see - positioning, yields, cross-asset flow. That is a better answer
than a borrowed narrative, and it is the discipline that kept the 5-9 Oct
retrospective truthful when TE's own commentary was not.
"""
import io
import os
import re
import sys
import glob
import json
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# TE iso -> our currency. The capture carries dozens of other countries;
# those are context for the BLOC, not for a currency.
ISO = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}

# a euro-area currency is moved by its members' data too
BLOC = {'DE': 'EUR', 'FR': 'EUR', 'IT': 'EUR', 'ES': 'EUR', 'NL': 'EUR'}

CB = re.compile(r'\b(speech|speaks|minutes|testimony|press conference|'
                r'statement|remarks|fed|ecb|boe|boj|rba|rbnz|boc|snb)\b', re.I)

NOISE = re.compile(r'\b(bill auction|bond auction|btf|bubill|t-bill|'
                   r'rig count|wasde|redbook|api |eia )\b', re.I)


def _num(v):
    if v is None:
        return None
    m = re.findall(r'-?\d+\.?\d*', str(v).replace(',', ''))
    return float(m[0]) if m else None


def all_rows(day):
    """Every captured row for one date, deduped across captures.

    Reads EVERY capture: TE rolls a row forward once the next occurrence is
    scheduled, so an actual released early in the week is gone from a later
    capture (F-95).
    """
    if isinstance(day, dt.date):
        day = day.isoformat()
    seen = {}
    for f in sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json'))):
        try:
            with io.open(f, encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get(
            'events', data.get('rows', []))
        for r in rows:
            if not isinstance(r, dict) or (r.get('date') or '') != day:
                continue
            k = (r.get('iso'), r.get('event'))
            # a later capture carrying an ACTUAL supersedes an earlier blank
            if k not in seen or (not (seen[k].get('actual') or '').strip()
                                 and (r.get('actual') or '').strip()):
                seen[k] = r
    return list(seen.values())


def for_currency(day, ccy):
    """(surprises, cb_speak, scheduled, n_total) for one currency.

    `surprises` is [(abs_pct, event, actual, forecast, direction)] sorted by
    how far the print missed, so the biggest surprise leads.
    """
    rows = all_rows(day)
    mine, surp, speak, sched = [], [], [], []
    for r in rows:
        iso = r.get('iso')
        if ISO.get(iso) != ccy and BLOC.get(iso) != ccy:
            continue
        ev = str(r.get('event') or '')
        if NOISE.search(ev):
            continue
        mine.append(r)
        act = (r.get('actual') or '').strip()
        fc = (r.get('forecast') or r.get('consensus') or '').strip()
        a, f = _num(act), _num(fc)
        if a is not None and f is not None and a != f:
            rel = abs(a - f) / (abs(f) if f else 1.0)
            surp.append((rel, ev, act, fc, 'BEAT' if a > f else 'MISS'))
        elif CB.search(ev) and not act:
            speak.append(ev)
        else:
            sched.append((ev, act or '-'))
    surp.sort(reverse=True)
    return surp, speak, sched, len(rows)


def explain(day, ccy, move):
    """One honest line on why a currency moved. Never invents a reason."""
    surp, speak, sched, total = for_currency(day, ccy)
    big = abs(move) >= 0.25

    if surp:
        rel, ev, act, fc, d = surp[0]
        agree = (d == 'BEAT') == (move > 0)
        tail = '' if len(surp) == 1 else ' (+%d more)' % (len(surp) - 1)
        return '%s %s %s vs %s%s - %s' % (
            ev[:34], d, act, fc, tail,
            'consistent' if agree else 'AGAINST the move')

    if speak:
        return '%s%s - not scored, tone unread (LD-107)' % (
            speak[0][:40], '' if len(speak) == 1 else
            ' +%d more' % (len(speak) - 1))

    if sched:
        return '%d release(s), none surprised: %s' % (
            len(sched), sched[0][0][:36])

    if big:
        return ('UNEXPLAINED - %d rows landed that day, none for %s. '
                'Cause is outside the calendar.' % (total, ccy))
    return 'quiet - nothing for %s in %d captured rows' % (ccy, total)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    day = a[0] if a else (dt.date.today() - dt.timedelta(days=1)).isoformat()
    print('CATALYST SCAN   %s   (%d captured rows that date)'
          % (day, len(all_rows(day))))
    print()
    for c in ('USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF'):
        s, sp, sc, n = for_currency(day, c)
        print('  %-4s %d surprise(s), %d CB speak, %d other'
              % (c, len(s), len(sp), len(sc)))
        print('       %s' % explain(day, c, 0.5))
