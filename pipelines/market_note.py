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

# LD-160 - MORE THAN ONE SOURCE, BECAUSE ONE SOURCE IS ONE POINT OF FAILURE.
#
# Jeff, 2026-10-11: "let's not limit our source to TE. there are other
# platforms like investinglive.com which we may find something that could
# explain what is happening"
#
# *** AND TE IS PRECISELY THE SOURCE THAT ALREADY MISLED ME ONCE - its
# euro-area page described MARKET PRICING and I read it as ECB intent
# (LD-158). A second source does not make either one true; it makes
# DISAGREEMENT VISIBLE, which is the only protection a quoted opinion can
# have.
#
# MEASURED ON THE 9 OCT SESSION, the two sources are not interchangeable:
#
#   TE      per-currency pages. Good on the currency in question, silent on
#           the others - its NZD page admitted it had no driver for the day.
#   invLive a DAILY FX WRAP covering every major in one post, with the
#           cross-market context TE's single-currency pages omit. It named
#           the CAD jobs miss (-68.3K vs +9.2K, two-month loss 110K), the
#           Michigan sentiment drop, and AUD as the dollar's weakest
#           counterpart - all three of which the calendar or TE missed.
#
# A NOTE MAY CARRY SEVERAL SOURCES. The page renders each with its own link,
# and when two sources disagree that disagreement is SHOWN rather than
# resolved - we are not in a position to arbitrate between two commentaries.
SOURCES = {
    'Trading Economics': {
        'USD': 'https://tradingeconomics.com/united-states/currency',
        'EUR': 'https://tradingeconomics.com/euro-area/currency',
        'GBP': 'https://tradingeconomics.com/united-kingdom/currency',
        'JPY': 'https://tradingeconomics.com/japan/currency',
        'AUD': 'https://tradingeconomics.com/australia/currency',
        'NZD': 'https://tradingeconomics.com/new-zealand/currency',
        'CAD': 'https://tradingeconomics.com/canada/currency',
        'CHF': 'https://tradingeconomics.com/switzerland/currency',
    },
    # not per-currency: one wrap covers the session for every major
    'investingLive': {'*': 'https://investinglive.com/'},
    # LD-161 - Jeff's own reading list. CNBC carries the YIELD and
    # RATE-EXPECTATION story, which is the gap every other source leaves:
    # on 9 Oct it gave the 10y at 5.244%, the 2y at 4.789%, and CME FedWatch
    # pricing 18% for October and 82% for December. None of that is on an
    # economic calendar and it is the mechanism behind both the EUR and AUD
    # misses this month.
    'CNBC': {'*': 'https://www.cnbc.com/world/?region=world'},
}

# *** TWO OF JEFF'S SOURCES CANNOT BE FETCHED DIRECTLY, AND SAYING SO IS PART
# OF THE RECORD RATHER THAN A FOOTNOTE:
#
#   CNBC            403 Forbidden to a direct fetch. REACHABLE BY SEARCH -
#                   WebSearch with allowed_domains=['cnbc.com'] returns the
#                   article text, so the source is usable, just not by URL.
#   CNN Fear&Greed  451 Unavailable For Legal Reasons on the page, and the
#                   production.dataviz.cnn.io graphdata endpoint answers
#                   "418 I'm a teapot. You're a bot." It is NOT fetchable
#                   from here at all today.
#
# data/raw/fng holds readings to 2026-09-04 and fng_block.py still renders
# them, so the capability exists and the SOURCE is what has closed. Jeff
# reads the page himself; the honest arrangement is that he pastes the
# reading and record() stores it with his attribution, rather than the report
# implying a fetch that did not happen.
BLOCKED = {
    'CNN Fear & Greed': 'https://edition.cnn.com/markets/fear-and-greed',
}

# kept for callers that predate SOURCES
PAGE = SOURCES['Trading Economics']


def _path(day):
    if isinstance(day, dt.date):
        day = day.isoformat()
    return os.path.join(STORE, '%s.json' % day)


def record(day, ccy, note, source='Trading Economics', url=None):
    """Store an attributed market note for one currency on one session.

    `note` is the source's own words, trimmed. `source` is who said it and
    `url` is WHERE, and both are REQUIRED.

    *** THE LINK IS NOT OPTIONAL. Jeff, 2026-10-11: "whenever you research
    around the internet kindly include the source link so I could check as
    well." A named source he cannot open is a claim he has to take on trust,
    and this whole tier exists BECAUSE I once took TE's euro commentary on
    trust and restated it as fact (LD-158). The reader checking the source is
    the control that failed that day; a page without links removes it.

    If no url is passed, PAGE[ccy] is used - it is the page a fetch would
    have targeted. Raising on a missing one would be worse than useless here,
    because the fallback is always correct for a TE currency note.
    """
    if not note or not str(note).strip():
        return False
    if not source or not str(source).strip():
        raise ValueError('a market note MUST carry its source (see LD-158)')
    url = url or PAGE.get(ccy)
    if not url:
        raise ValueError('a market note MUST carry a checkable link (LD-159)')
    if not os.path.isdir(STORE):
        os.makedirs(STORE)
    p = _path(day)
    data = {}
    if os.path.exists(p):
        data = json.load(io.open(p, encoding='utf-8'))
    # LD-160 - a currency may carry SEVERAL notes, one per source. Storing
    # a list rather than overwriting is what makes disagreement visible: two
    # commentaries that contradict each other both appear, and the reader
    # decides. Overwriting would silently privilege whichever was fetched
    # last, which is the opposite of the point.
    entry = {'note': str(note).strip(), 'source': str(source).strip(),
             'url': str(url).strip(),
             'fetched': dt.date.today().isoformat()}
    cur = data.get(ccy)
    if isinstance(cur, dict):          # migrate the old single-note shape
        cur = [cur]
    cur = [e for e in (cur or []) if e.get('source') != entry['source']]
    cur.append(entry)
    data[ccy] = cur
    io.open(p, 'w', encoding='utf-8', newline=chr(10)).write(
        json.dumps(data, indent=1, ensure_ascii=False))
    return True


def record_regime(day, reading, label, source='CNN Fear & Greed',
                  url='https://edition.cnn.com/markets/fear-and-greed'):
    """Store the session's risk-regime reading - a NUMBER, not commentary.

    LD-161. Fear & Greed is not an opinion about why a price moved; it is a
    measured index, and it belongs in its own slot rather than among the
    quoted notes. Jeff's own 3 Oct observation is the reason it earns a
    place: "I just checked the Fear and Grid Index last week and for the
    whole week we are at Fear Index. meaning Safe Haven are the ones people
    were looking at" - and that week the three havens rose and all three
    commodity currencies fell.

    CNN BLOCKS AUTOMATED READS (451 on the page, 418 on the dataviz
    endpoint), so this is stored from whatever Jeff reads off the page. It
    carries his attribution and the link, exactly like any other source.
    """
    return record(day, '_REGIME', '%s - %s' % (reading, label), source, url)


def regime(day):
    """The session's risk-regime note, or None."""
    v = note_for(day, '_REGIME')
    return v[0] if v else None


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
    """[{note, source, url, fetched}] - ALWAYS a list, even for one note."""
    v = notes(day).get(ccy)
    if v is None:
        return []
    return [v] if isinstance(v, dict) else v


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
        print('       %s' % d.get('url', '(no link)'))
        print('       %s' % d['note'][:200])
