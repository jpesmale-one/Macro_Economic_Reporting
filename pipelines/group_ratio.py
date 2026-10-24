# -*- coding: utf-8 -*-
"""LD-169 - CORRELATED PAIRS COUNT ONCE, BUT NOTHING IS DISCARDED.

Jeff, 2026-10-24:

    "what if we average our correlated pairs first before including the
     others? this way we still account everything winners and losers"

THE PROBLEM HE IS SOLVING. The 19-23 Oct set held three CHF shorts and one
non-CHF pair. LD-149 pools pips across all four, so ONE CURRENCY VIEW was
counted THREE TIMES and the single diversified pair was drowned. The week
published 1.139 CONTESTED; the three CHF shorts alone ran 1.453 and GBPAUD
ran 0.840. The verdict described the CHF view, not the set.

WHY HIS METHOD BEATS MY EARLIER SUGGESTION. I proposed taking the BEST of
the three CHF pairs. That uses hindsight - keep the winner, bin the losers -
and inflates every number we report. His average keeps winners AND losers;
it only stops one view voting three times.

*** AND I PICKED THE AVERAGING METHOD ON EVIDENCE, NOT TASTE (he asked me
to choose). Two candidates, tested in test_group_ratio.py:

  METHOD A  average each group's RATIOS, then average the groups
  METHOD B  average each group's PIPS, then take ONE ratio   <- CHOSEN

Three tests decided it:

  1. A LETS A DEAD PAIR CANCEL A LIVE ONE. Group of fav 100/adv 50 beside a
     pair that moved 1 pip favourable and 2 adverse: A reads 1.250, B reads
     1.942. A 3-pip pair should not erase a 150-pip pair.

  2. A IS UNBOUNDED. A pair with a tiny adverse leg (fav 50 / adv 1) has
     ratio 50.0 and drags the average to 25.3 on a week that did nothing.
     B reads 1.089. Ratios of small numbers explode; pips do not.

  3. *** THE DECIDER - B REPRODUCES LD-149 EXACTLY WHEN NO PAIRS ARE
     GROUPED. Four uncorrelated pairs: LD-149 pooled = 1.013, B = 1.013,
     A = 1.042. A would silently restate every week we have ever published,
     including weeks with no correlation at all. B changes ONLY what it is
     meant to change, so the 3,192 pair-weeks behind LD-149's bands still
     calibrate the same statistic.

LD-149's bands (0.70 / 1.40) are therefore still valid under B. They would
NOT be under A.

LD-4 HOLDS: this grades what price did. No entries, exits, stops or targets.
"""
import atr_grade as ag


def groups(pairs, bias=None):
    """[[pair, ...]] - pairs expressing the SAME currency view, grouped.

    *** F-163 - MY FIRST CUT OF THIS WAS BROKEN AND THE TEST CAUGHT IT.
    I grouped on "shares any currency", which failed two ways:

      1. ORDER DEPENDENT. {CADCHF, GBPAUD, GBPCHF, NZDCHF} gave
         [[CADCHF,GBPCHF,NZDCHF],[GBPAUD]] in sorted order but ONE group of
         four if GBPAUD came first - because GBPAUD shares GBP with GBPCHF,
         which shares CHF with CADCHF. Same set, different verdict.
      2. TRANSITIVE COLLAPSE. Chaining "shares a currency" merges almost
         any real set into a single blob, which defeats the purpose.

    THE FIX IS TO GROUP ON THE REPEATED VIEW, NOT ON ANY SHARED LETTER. A
    "view" is one currency the set takes the same side of more than once:
    three CHF shorts are the CHF view three times. GBPAUD is not part of
    that view just because it contains GBP - GBP there is the OTHER leg,
    a different bet.

    The DOMINANT currency is the one appearing in the most pairs. Pairs
    containing it form one group; the rest are ungrouped singles. This is
    deterministic (ties broken alphabetically) and order independent.

    bias: optional {pair: 'long'|'short'}. When given, a currency only
    counts as one view where the pairs take the SAME side of it, so a long
    CHF and a short CHF are not averaged into each other.
    """
    pairs = sorted(pairs)
    if len(pairs) < 2:
        return [[p] for p in pairs]

    def side(p, c):
        """'long' | 'short' - which way this pair bets on c."""
        if bias is None:
            return ''
        d = bias.get(p)
        if d is None:
            return ''
        if p[:3] == c:
            return d
        return 'short' if d == 'long' else 'long'

    best, members = None, []
    counts = {}
    for p in pairs:
        for c in (p[:3], p[3:]):
            counts.setdefault(c, []).append(p)
    for c in sorted(counts):
        ps = counts[c]
        if bias is not None:
            by = {}
            for p in ps:
                by.setdefault(side(p, c), []).append(p)
            ps = max(by.values(), key=lambda v: (len(v), sorted(v)))
        if len(ps) < 2:
            continue
        if best is None or len(ps) > len(members):
            best, members = c, sorted(ps)

    if best is None:
        return [[p] for p in pairs]
    rest = [p for p in pairs if p not in members]
    return [members] + [[p] for p in rest]


def set_ratio(per_pair, bias=None):
    """(ratio, detail) for a whole set. per_pair: {pair: (fav, adv)}.

    Method B: each group contributes its MEAN fav and MEAN adv, then one
    ratio over those contributions.
    """
    gs = groups(sorted(per_pair), bias)
    F = A = 0.0
    detail = []
    for g in gs:
        gf = sum(per_pair[p][0] for p in g) / len(g)
        ga = sum(per_pair[p][1] for p in g) / len(g)
        F += gf
        A += ga
        detail.append((tuple(g), gf, ga, (gf / ga) if ga > 0 else None))
    return ((F / A) if A > 0 else None), detail


def set_verdict(per_pair, bias=None):
    """('WIN'|'CONTESTED'|'LOSS'|None, ratio, detail) under LD-149 bands."""
    r, detail = set_ratio(per_pair, bias)
    if r is None:
        return None, None, detail
    if r >= ag.WIN_AT:
        return 'WIN', r, detail
    if r < ag.LOSS_AT:
        return 'LOSS', r, detail
    return 'CONTESTED', r, detail


def report(per_pair, bias=None):
    v, r, detail = set_verdict(per_pair, bias)
    out = ['LD-169 SET VERDICT  %s  ratio %.3f'
           % (v or 'n/a', r if r is not None else float('nan')),
           '  %-26s %8s %8s %8s' % ('view (grouped pairs)', 'mean fav',
                                    'mean adv', 'ratio')]
    for g, gf, ga, gr in detail:
        out.append('  %-26s %8.1f %8.1f %8s'
                   % ('+'.join(g), gf, ga,
                      ('%.3f' % gr) if gr is not None else '-'))
    return '\n'.join(out)
