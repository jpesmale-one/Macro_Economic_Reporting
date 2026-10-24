# -*- coding: utf-8 -*-
"""LD-172 - THE BOARD OVERSTATES ITS OWN EXTREMES. SHRINK THEM.

Jeff, 2026-10-24: "we can also add that 2-year yields and shrinkage
calibration you're mentioning."

THE MEASUREMENT BEHIND IT. Over seven recorded sessions the board pinned
four currencies in the same place every single day, and all four drifted
toward the middle, 6 of 7 sessions each:

    GBP  board #1 every session  ->  traded #4.14   (drift -3.14)
    CAD  board #2 every session  ->  traded #3.57   (drift -1.57)
    AUD  board #6-8 every session -> traded #3.86   (drift +2.86)
    CHF  board #6-8 every session -> traded #4.71   (drift +2.29)

Meanwhile the four the board was UNSURE about - EUR, NZD, JPY, USD, whose
ranks actually moved - drifted +0.14, +0.14, +0.71 and -1.43: essentially
no systematic error. rho(board rank, drift) = +0.922, and a permutation
test against 20,000 shuffled boards put that at p = 0.0425, so it survives
the arithmetic bias that comes from board appearing on both sides.

*** SO THE BOARD IS NOT WRONG AND NOT BACKWARDS. IT IS OVER-CONFIDENT AT
THE EXTREMES. Its #1 trades like #4. Its #8 trades like #4. The middle is
where it is accurate.

WHAT THIS CHANGES, AND WHAT IT DELIBERATELY DOES NOT. Shrinking pulls each
score toward the board mean, so the ORDER IS UNTOUCHED - whatever was #1
is still #1. What changes is the SPREAD, i.e. how big a gap the board
claims between its top and bottom. That matters because the gap is what
LD-126's selector reads when it decides how much conviction a pair has.

*** SHRINKING IS NOT A PREDICTION THAT THE EXTREMES ARE WRONG. It is the
statement that a 7-rank-step claim has historically delivered about half a
step, so the claim should be sized to what it delivers. Two weeks of
evidence pointed opposite ways on concentration and neither settled it;
this is the one place the evidence is consistent.

LD-4 HOLDS: this reports a score. It sets no entry, exit, stop or target.
LD-167 - the live logic is FROZEN for the current edition, so nothing here
is wired into a build. SHRINK_K defaults to 0.0, which is EXACTLY the
board we publish today. Turning it on is Jeff's call.
"""

# 0.0 = no shrinkage, the published board, byte-identical.
# 0.5 = halve every distance from the mean, which is what the 7-session
#       drift measured. Kept OFF by default under LD-167.
SHRINK_K = 0.0

# The measurement this is calibrated from, recorded so the number is never
# a bare constant someone later "tidies up".
EVIDENCE = {
    'sessions': 7,
    'rho_board_vs_drift': 0.922,
    'permutation_p': 0.0425,
    'pinned': {'GBP': -3.14, 'CAD': -1.57, 'AUD': 2.86, 'CHF': 2.29},
    'unpinned': {'EUR': 0.14, 'NZD': 0.14, 'JPY': 0.71, 'USD': -1.43},
}


def shrink(scores, k=None):
    """{ccy: score} pulled k of the way toward the board mean.

    k = 0 returns the input unchanged (today's published board).
    k = 1 would collapse every currency onto the mean, which is useless -
    it destroys the ranking entirely. The useful range is 0 to ~0.6.
    """
    if k is None:
        k = SHRINK_K
    if not scores:
        return dict(scores)
    if k <= 0:
        return dict(scores)
    k = min(float(k), 1.0)
    mu = sum(scores.values()) / float(len(scores))
    return dict((c, mu + (v - mu) * (1.0 - k)) for c, v in scores.items())


# A board total is a sum of weighted fractions, so two genuinely equal
# currencies can differ in the last bit. Ties must be detected with a
# tolerance or the board silently ranks a tie as #7 and #8.
TIE = 1e-9


def ranks(scores, tie=TIE):
    """{ccy: rank}, 1 = strongest, average ranks on ties.

    *** F-167 - EXACT == SPLIT A REAL TIE AND I FOUND IT THROUGH MY OWN
    FAILING TEST. On the live board JPY and AUD are both -5/3, but
    base_scores sums their category weights in a different order, so they
    come back as
        JPY -1.66666666666666651864   (-0x1.aaaaaaaaaaaaap+0)
        AUD -1.66666666666666674068   (-0x1.aaaaaaaaaaaabp+0)
    a difference of 2.22e-16. Exact == therefore ranked them #7 and #8 -
    an arbitrary ordering of two identical currencies, decided by
    floating-point noise.
    The order_preserved test caught it by failing: shrink() is linear and
    kept the TRUE tie (both -0.229166...), so the shrunk board read 7.5/7.5
    while the original read 7/8. *** THE BUG WAS IN THE BASELINE, NOT THE
    SHRINKAGE - and without the test I would have "fixed" the wrong one.
    """
    order = sorted(scores, key=lambda c: (-scores[c], c))
    out, i = {}, 0
    while i < len(order):
        j = i
        while j + 1 < len(order)                 and abs(scores[order[j + 1]] - scores[order[i]]) <= tie:
            j += 1
        for x in range(i, j + 1):
            out[order[x]] = (i + j) / 2.0 + 1
        i = j + 1
    return out


def order_preserved(scores, k=None):
    """True if shrinking leaves every rank identical.

    *** THIS IS THE PROPERTY THAT MAKES SHRINKAGE SAFE TO ADOPT. A linear
    pull toward the mean cannot reorder anything, so a reader who trusts
    the board's ORDER loses nothing. If this ever returns False the
    implementation is broken, not the idea.
    """
    return ranks(scores) == ranks(shrink(scores, k))


def spread(scores):
    """Top-to-bottom distance, which is what the selector reads as gap."""
    if not scores:
        return 0.0
    return max(scores.values()) - min(scores.values())


def report(scores, k=0.5):
    """Side-by-side so the effect is visible before anything is adopted."""
    sh = shrink(scores, k)
    r0, r1 = ranks(scores), ranks(sh)
    L = ['LD-172 SHRINKAGE  k=%.2f   (live SHRINK_K=%.2f)' % (k, SHRINK_K),
         '  %-5s %9s %7s   %9s %7s' % ('CCY', 'board', 'rank',
                                       'shrunk', 'rank')]
    for c in sorted(scores, key=lambda c: r0[c]):
        L.append('  %-5s %+9.2f %7g   %+9.2f %7g'
                 % (c, scores[c], r0[c], sh[c], r1[c]))
    L.append('')
    L.append('  spread %.2f -> %.2f    order preserved: %s'
             % (spread(scores), spread(sh),
                'YES' if r0 == r1 else '*** NO - BUG'))
    return '\n'.join(L)
