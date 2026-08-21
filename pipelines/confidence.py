# -*- coding: utf-8 -*-
"""
LD-20: a stated confidence per carried pair.

NOT a probability and NOT a guarantee. It is a transparent tally of how many
independent supports a pair has, so Jeff can see which to focus on first. Every
input is a fact already published elsewhere in the edition.

  +2  spread >= 8.00        (wide fundamental gap)
  +1  spread 4.00-7.99
   0  spread 1.00-3.99      (thin - clears the floor, nothing more)
  +2  structure CONFIRMS with a broken level or a multi-touch zone behind it
  +1  structure CONFIRMS on range position alone
  +1  price moved WITH the read on the last closed bar
  +1  the fundamental leg CHANGED in our favour this week (fresh, not stale)
  -2  either leg is a currency the model is currently getting WRONG
  -1  score and news disagree on a leg
  -1  spread is the thinnest carried

  >= 5  HIGH      focus here first
  3-4   MEDIUM    valid, second look
  <= 2  LOW       carried, but the weakest of the set - know why
"""


def score(name, items):
    """items: list of (points, reason). Returns (total, band, lines)."""
    tot = sum(p for p, _ in items)
    band = 'HIGH' if tot >= 5 else ('MEDIUM' if tot >= 3 else 'LOW')
    return tot, band, items


def render(name, items):
    tot, band, _ = score(name, items)
    parts = ' · '.join('%+d %s' % (p, r) for p, r in items)
    return '%-8s %2d  %-6s  %s' % (name, tot, band, parts)


CARRIED = {
    'CADJPY': [
        (2, 'spread 8.00'),
        (2, 'broke a 4-touch resistance zone, closed above it'),
        (1, 'price +82.2 pips with the read'),
        (1, 'JPY trade deficit doubled Thu - fresh fundamental'),
    ],
    'GBPUSD': [
        (0, 'spread 2.75 - thin'),
        (1, 'structure confirms on position (94.4%)'),
        (1, 'price +27.5 pips with the read'),
        (1, 'GBP CPI 2.9% rising + 3/9 hike votes - fresh'),
        (-1, 'score says USD +2.25 but Thu US data ran hot'),
        (-1, 'thinnest spread carried'),
    ],
    'EURCHF': [
        (2, 'spread 8.50'),
        (1, 'structure confirms on position (72.7%)'),
        (1, 'price +37.5 pips with the read'),
        (1, 'EUR inflation finalised 2.9% rising - fresh'),
        (-2, 'CHF leg: the model has been WRONG on CHF all week'),
    ],
}

if __name__ == '__main__':
    print('CONFIDENCE (LD-20) - a tally of supports, not a probability\n')
    for k, v in CARRIED.items():
        print(render(k, v))
    print()
    for k, v in CARRIED.items():
        t, b, _ = score(k, v)
        print('  %-8s total %+d -> %s' % (k, t, b))
