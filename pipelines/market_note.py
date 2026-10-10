# -*- coding: utf-8 -*-
"""TIER 5 - WHAT THE MARKET SAID, WHEN THE CALENDAR SAYS NOTHING.

Jeff, 2026-10-11: "can't we find anything on the net? earlier I asked this
question on the retro report and you gave an explanation on the AUD strength"

He is right that I did. For the 5-9 Oct retrospective I fetched TE's currency
page and it explained AUD's rise: US Treasury yields falling from 24-year
peaks, the dollar weakening broadly, RBA hike pricing down to 30% for
November. None of that is on any economic calendar and all of it was true.

*** AND IN THE SAME SESSION I MISUSED EXACTLY THIS SOURCE. I fetched TE's
euro-area page, read "markets priced only an 80% chance of another hike by
year-end, down from at least three additional moves by March 2027", and
restated it as a fact about where the ECB was going. Jeff caught it: the ECB's
own 10 September statement was HAWKISH and its forward guidance was UNCHANGED
from July, word for word. TE was describing MARKET PRICING, not ECB
communication, and I collapsed the two.

SO THIS MODULE EXISTS UNDER ONE RULE, AND THE RULE IS THE WHOLE POINT:

    A FETCHED NOTE IS AN ATTRIBUTED QUOTE, NEVER A FINDING.

Everything it returns is labelled with its source and rendered as commentary.
It never scores, never reaches the board, and never appears without the word
that says who said it. The report distinguishes:

    MEASURED   our own bars, our own calculation       - stated as fact
    RELEASED   an actual against a forecast            - stated as fact
    REPORTED   someone's explanation of a price move   - ATTRIBUTED, always

Financial commentary is written after the fact to explain a chart. It is
useful for naming things a calendar cannot see - yields, positioning,
politics - and worthless as evidence of causation. Both halves of that are
true at once, which is why the attribution is not optional politeness.

WHAT IT CANNOT DO: this module does not fetch. The MCP/WebFetch tools are not
callable from a script. The flow is the same shape as pair_atr's:

    1. gen_daily asks which currencies are UNEXPLAINED
    2. the session fetches those pages and calls record()
    3. the page renders them as attributed commentary

A currency with no recorded note still reports UNEXPLAINED. Silence is a
valid answer and is never filled in with guesswork.
"""
import io
import os
import sys
import json
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STORE = os.path.join(REPO, 'data/raw/market_notes')

# the TE currency page per currency - what a fetch should target
PAGE = {
    'USD': 'https://tradingeconomics.com/united-states/currency',
    'EUR': 'https://tradingeconomics.com/euro-area/currency',
    'GBP': 'https://tradingeconomics.com/united-kingdom/currency',
    'JPY': 'https://tradingeconomics.com/japan/currency',
    'AUD': 'https://tradingeconomics.com/australia/currency',
    'NZD': 'https://tradingeconomics.com/new-zealand/currency',
    'CAD': 'https://tradingeconomics.com/canada/currency',
    'CHF': 'https://tradingeconomics.com/switzerland/currency',
}


def _path(day):
    if isinstance(day, dt.date):
        day = day.isoformat()
    return os.path.join(STORE, '%s.json' % day)


def record(day, ccy, note, source='Trading Economics'):
    """Store an attributed market note for one currency on one session.

    `note` is the source's own words, trimmed. `source` is who said it and is
    NEVER blank - a note without attribution is the failure this guards.
    """
    if not note or not str(note).strip():
        return False
    if not source or not str(source).strip():
        raise ValueError('a market note MUST carry its source (see F-146)')
    if not os.path.isdir(STORE):
        os.makedirs(STORE)
    p = _path(day)
    data = {}
    if os.path.exists(p):
        data = json.load(io.open(p, encoding='utf-8'))
    data[ccy] = {'note': str(note).strip(), 'source': str(source).strip(),
                 'fetched': dt.date.today().isoformat()}
    io.open(p, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(data, indent=1, ensure_ascii=False))
    return True


def notes(day):
    """{ccy: {note, source, fetched}} for a session, or {}."""
    p = _path(day)
    if not os.path.exists(p):
        return {}
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return {}


def note_for(day, ccy):
    return notes(day).get(ccy)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    day = a[0] if a else (dt.date.today() - dt.timedelta(days=1)).isoformat()
    n = notes(day)
    print('MARKET NOTES   %s   (%d recorded)' % (day, len(n)))
    print()
    if not n:
        print('  none. Fetch the pages below and call record():')
        for c, u in sorted(PAGE.items()):
            print('    %-4s %s' % (c, u))
    for c, d in sorted(n.items()):
        print('  %-4s [%s, fetched %s]' % (c, d['source'], d['fetched']))
        print('       %s' % d['note'][:200])
