# -*- coding: utf-8 -*-
"""LD-73 - SELECTION GATES: event risk and room to move.

Jeff, 2026-08-29:

    "I did not give a hard rule that we should immediately match top vs
     bottom. Ideally this is the best bet but if Top 8 for example have high
     impact news on the upcoming week then there's really no way of telling
     where the price would go... That's where the Technical Analysis would
     come in. Once you have a candidate pair we can check if the price is
     still have the bandwidth to move. for example GBPUSD and our bias is Long
     (favoring GBP) but we see its already near resistance there's a very good
     chance that it would reverse first before continuing the upside or
     completely reverse. In such cases we may want to look for other pairs
     with the same or a little bit lesser conviction than GBPUSD but with room
     to move in the favor of our bias."

WHY THIS EXISTS. On 2026-08-23 GBPUSD was selected on a macro spread of 3.50
and LOST 110.9 pips - the worst of the four. At selection it sat at 94.4% of
its 45-bar range while the bias was LONG. It had 30 pips of room to its high
and 1,259 pips of room to its low. THE ROOM WAS ALL IN THE WRONG DIRECTION and
nothing in the process asked.

TWO GATES, applied AFTER the macro spread ranks candidates:

  ROOM TO MOVE   how much of the 45-bar range lies in the bias direction.
                 A LONG at 95% of range has almost none; a LONG at 30% has
                 plenty. This is the gate that would have caught GBPUSD.

  EVENT RISK     how many high-impact whitelist releases hit either leg in
                 the coming week. This does NOT veto a pair - Jeff was
                 explicit: "I'm not saying also that we should avoid top vs
                 bottom with upcoming high impact news its such that we need
                 to be more careful with these kind of set-ups." It DOWNGRADES
                 confidence so a crowded pair must earn its place on room.

NEITHER GATE OVERRIDES THE MACRO SPREAD. They re-rank candidates the spread
has already produced, which is what "same or a little bit lesser conviction
but with room to move" means.
"""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Events that reprice a currency on their own. Weighted 2; everything else 1.
HIGH_IMPACT = (
    'interest rate decision', 'non farm payrolls', 'inflation rate',
    'unemployment rate', 'gdp growth', 'employment change',
)


def room_to_move(price, lo, hi, direction):
    """Fraction of the 45-bar range available IN THE BIAS DIRECTION, 0..1.

    LONG  at 30% of range -> 0.70 of the range above it   -> plenty
    LONG  at 95% of range -> 0.05                         -> almost none
    SHORT at 95% of range -> 0.95                         -> plenty
    """
    if hi is None or lo is None or hi <= lo:
        return None
    pos = (price - lo) / (hi - lo)
    pos = max(0.0, min(1.0, pos))
    return (1.0 - pos) if direction == 'LONG' else pos


def room_verdict(r):
    if r is None:
        return 'UNKNOWN'
    if r >= 0.60:
        return 'AMPLE'
    if r >= 0.35:
        return 'ADEQUATE'
    if r >= 0.20:
        return 'TIGHT'
    return 'NONE'


def event_risk(ccy_a, ccy_b, events):
    """Weighted count of whitelist events hitting either leg this week.

    events: iterable of (ccy, indicator_name).
    """
    hits = []
    for ccy, name in events:
        if ccy not in (ccy_a, ccy_b):
            continue
        w = 2 if any(k in name.lower() for k in HIGH_IMPACT) else 1
        hits.append((ccy, name, w))
    return sum(h[2] for h in hits), hits


def risk_verdict(score):
    if score >= 6:
        return 'CROWDED'
    if score >= 3:
        return 'BUSY'
    if score >= 1:
        return 'LIGHT'
    return 'QUIET'


def gate(pair, direction, price, lo, hi, ccy_a, ccy_b, events):
    """Both gates for one candidate. Returns a dict for the table."""
    r = room_to_move(price, lo, hi, direction)
    risk, hits = event_risk(ccy_a, ccy_b, events)
    pos = None if (hi is None or lo is None or hi <= lo) else \
        max(0.0, min(1.0, (price - lo) / (hi - lo)))
    return {
        'pair': pair, 'dir': direction, 'price': price,
        'range_pos': pos, 'room': r, 'room_verdict': room_verdict(r),
        'risk': risk, 'risk_verdict': risk_verdict(risk), 'events': hits,
    }
