# -*- coding: utf-8 -*-
"""R-36 - the surprise term, graded by hand first (LD-90).

Jeff, 2026-09-02: "A central bank decision moves price by its surprise
component only. Level of rates -> already discounted. Change in the expected
path -> that's the tradable variable. This is why you'll see currencies fall
on hikes and rally on cuts more often than beginners expect."

Every case below was reasoned from that sentence BEFORE it was run.

    python pipelines/test_surprise.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rate_surprise import surprise, verdict

# (label, actual, consensus, expected surprise, why)
CASES = [
    ('RBNZ 2026-09-02 - the case that prompted this',
     '2.75%', '2.75%', 0.0,
     'hiked exactly on consensus; NZD fell 108 pips. Zero new information.'),
    ('hike when a hold was priced',
     '2.75%', '2.50%', +1.0, 'the tradable case for a hawkish surprise'),
    ('hold when a hike was priced',
     '2.50%', '2.75%', -1.0,
     'THE CURRENCY FALLS ON A HOLD - the beginner-surprising case Jeff named'),
    ('cut when a hold was priced',
     '2.25%', '2.50%', -1.0, 'dovish surprise'),
    ('cut when a deeper cut was priced',
     '2.25%', '2.00%', +1.0,
     "A CUT THAT RALLIES THE CURRENCY - the other half of the point"),
    ('50bp when 25 was priced',
     '3.00%', '2.75%', +1.0, 'clamped at the standard-move ceiling'),
    ('a 10bp miss on a 25bp scale',
     '2.85%', '2.75%', +0.4, 'partial surprise scales, it is not binary'),
    ('no consensus published',
     '2.75%', None, None,
     'UNMEASURABLE is not zero - zero would assert the market was unsurprised'),
]


def main():
    print('R-36 DECISION SURPRISE (LD-90)')
    print('=' * 74)
    bad = 0
    for label, a, c, want, why in CASES:
        got = surprise(a, c)
        ok = (got is None and want is None) or (
            got is not None and want is not None and abs(got - want) < 0.005)
        if not ok:
            bad += 1
        print('%-46s %7s %7s %s'
              % (label[:46], ('%+.2f' % got) if got is not None else 'None',
                 ('%+.2f' % want) if want is not None else 'None',
                 'OK' if ok else '** MISMATCH **'))
        if not ok:
            print('       expected because: %s' % why)
    print('=' * 74)
    if bad:
        raise SystemExit('%d of %d WRONG. A decision moves price by its '
                         'SURPRISE only (LD-90).' % (bad, len(CASES)))
    print('All %d surprise cases correct.' % len(CASES))
    print()
    print('NOTE: this scores the DECISION surprise only. The FORWARD TRACK -')
    print('which Jeff correctly identifies as the live variable - is not')
    print('sourceable for all eight currencies, so LD-23 keeps it out of the')
    print('score and 3 carries it as commentary.')


if __name__ == '__main__':
    main()
