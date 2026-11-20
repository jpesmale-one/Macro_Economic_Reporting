"""R-53 - NO WHITELIST ROW MAY BE SCORED BY A HAND-TYPED VERDICT (F-194).

    python pipelines/test_frozen_rows.py

*** THE DEFECT THIS EXISTS FOR, AND WHY NOTHING ELSE SAW IT.

derive_scores.score_row() ends with

    return {'GOOD': 1, 'BAD': -1, 'NEUTRAL': 0}.get(verdict)

- the verdict somebody TYPED into score_model.ROWS. Every rule above it is
reached by matching the row's THRESHOLD TEXT. So a threshold no rule
recognises does not raise, does not warn, and does not score: it returns a
constant, and the row is FROZEN. The actual can change by any amount in
either direction and the score does not move.

On 2026-11-20, three of 78 rows were frozen:

    GBP Claimant Count Change   '<0 (LD-58)'
    AUD Employment Change       'LD-151 three legs'
    CAD Employment Change       'LD-151 three legs'

GBP's was the expensive one. claimant_grade() had implemented Jeff's rule
CORRECTLY since 2026-08-24; score_row simply never called it. Measured by
substitution:

    actual=30.3K -> -1   actual=-50K  -> -1   actual=0 -> -1
    actual=33.2K -> -1   actual=+500K -> -1

A 50K FALL in claimants - unambiguously good, and the exact reading LD-58
was written to fix - scored BAD. The row read -1 for the right answer on
the held value, which is LUCK, not correctness. That is F-184's lesson
one table over: a score that happens to be right is not a score that is
being computed.

*** WHY A SUBSTITUTION TEST AND NOT AN EYEBALL.

A frozen row is INVISIBLE in every existing check. R-37/R-40/R-45 compare
the VALUE against TE and pass - the value was never wrong. The render
guards check shape and pass - the cell is populated. test_inflation covers
the inflation rows only. Reading the board tells you nothing, because the
number displayed is plausible.

The only thing that exposes it is asking the row to score something it has
never seen. This feeds each row a spread of actuals spanning both signs
and FAILS if the score never moves.

*** THE TWO ROWS THAT ARE STILL FROZEN ARE DECLARED, NOT FIXED.

AUD and CAD Employment Change carry 'LD-151 three legs'. LD-151 is
documented in score_model.py and implemented nowhere, AND TE's indicator
page carries only the HEADLINE - never the FT/PT split the rule needs. So
they cannot be fixed by wiring alone; they need a source for the legs
(the open ABS item). They are listed in KNOWN_FROZEN below so this guard
reports them every run instead of going quiet about them.

    A declared gap stays visible. An undeclared one becomes a habit.

Adding a row to KNOWN_FROZEN is a decision to publish a hand-typed score
for it. Do not do that to make this guard pass.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import score_model as sm
import derive_scores as ds


# (category, currency, indicator) -> why it is still scored from a verdict.
# F-194: these are DEFECTS awaiting a source or an implementation, not
# approved behaviour. Each one publishes a number nobody computed.
KNOWN_FROZEN = {
    ('Employment', 'AUD', 'Employment Change'):
        'LD-151 not implemented AND TE gives no FT/PT split (needs ABS)',
    ('Employment', 'CAD', 'Employment Change'):
        'LD-151 not implemented AND TE gives no FT/PT split (needs StatCan)',
}


# *** THE PROBE SPREAD MUST STRADDLE THE ROW'S OWN REFERENCE POINT.
#
# The first version of this guard fed every row the same fixed ladder
# (-500 .. +500) and reported THREE false positives: AUD Westpac Consumer
# Conf Change, JPY Balance of Trade and CAD Inflation. None was frozen.
#
#   JPY trade is '>Prev' against -1111.9B, so EVERY probe in that ladder
#   beat it and all seven scored +1. A constant score because the probes
#   never crossed the comparison point looks exactly like a constant score
#   because no rule ran.
#
# So probes are derived from the row's OWN previous value: well below it,
# just below, equal, just above, well above, plus a zero crossing for the
# sign rules. A guard whose probe set is blind to the rule it tests
# manufactures the finding it claims to detect - which is F-73 again, in
# the test harness instead of the report.
def probes(held, previous):
    """Actuals that straddle `previous`, in the row's own units."""
    s = str(held)
    unit = '%' if '%' in s else ('K' if 'K' in s.upper() else '')
    p = sm._num(previous)
    if p is None:
        p = sm._num(held)
    if p is None:
        p = 0.0
    span = max(abs(p), 1.0)
    pts = [p - span * 10, p - span, p - 0.1, p, p + 0.1,
           p + span, p + span * 10, 0.0]
    out = []
    for v in pts:
        out.append('%g%s' % (round(v, 4), unit))
    # the corridor rules (LD-155) key off absolute level, not the prior
    if unit == '%':
        out += ['0%', '1.9%', '2.1%', '3.5%', '8%', '-1%']
    return out


def main():
    print('R-53  NO ROW MAY BE SCORED BY A HAND-TYPED VERDICT (F-194)')
    print('=' * 72)
    frozen = []
    checked = 0
    for cat, iso, name, act, prev, ref, thr, verdict in sm.ROWS:
        ccy = sm.LABEL[iso]
        # The rate row is computed by rate_model for the whole currency and
        # the GDP row by a fixed band; neither reads the threshold text.
        if cat in ('GDP', 'Interest_Rate'):
            continue
        # *** LD-165 MAKES AN INFLATION ROW CORRECTLY INSENSITIVE TO ITS
        # ACTUAL, AND THAT IS NOT A FROZEN ROW.
        #
        # When TE carries a consensus or forecast for the NEXT print, the
        # expectation IS the reading (Jeff: "we're trading the expectations
        # not the result"), so score_row ignores the fact table's actual by
        # design. On 2026-11-20 CAD had a scheduled 14 Dec print at 3.3%,
        # so every probe returned +1 - the override firing, exactly as
        # specified. Scoring that as a defect would pressure the next
        # reader to "fix" a working rule.
        #
        # So an inflation row is probed with the override SUPPRESSED
        # (_autoload_inf=False, the same switch test_inflation uses). What
        # is being tested here is whether the row can score AT ALL from its
        # own value, not which authority wins when both exist. R-44 owns
        # the before/after precedence.
        checked += 1
        scores = set()
        if cat == 'Inflation':
            for v in probes(act, prev):
                try:
                    scores.add(ds.score_row(cat, ccy, name, v,
                                            _autoload_inf=False))
                except Exception as e:
                    scores.add('RAISED:%s' % e)
            if len(scores) == 1:
                frozen.append((cat, ccy, name, thr, scores.pop()))
            continue
        for v in probes(act, prev):
            try:
                scores.add(ds.score_row(cat, ccy, name, v))
            except Exception as e:          # a rule that raises is also a bug
                scores.add('RAISED:%s' % e)
        if len(scores) == 1:
            frozen.append((cat, ccy, name, thr, scores.pop()))

    undeclared = []
    for cat, ccy, name, thr, sc in frozen:
        key = (cat, ccy, name)
        if key in KNOWN_FROZEN:
            print('  known   %-4s %-30s thr=%-20s -> always %s' % (
                ccy, name[:30], str(thr)[:20], sc))
            print('          %s' % KNOWN_FROZEN[key])
        else:
            undeclared.append((cat, ccy, name, thr, sc))

    print('-' * 72)
    for cat, ccy, name, thr, sc in undeclared:
        print('*** FROZEN %-4s %-30s thr=%-20s -> always %s' % (
            ccy, name[:30], str(thr)[:20], sc))

    print('rows probed                  : %d' % checked)
    print('frozen, declared in this file: %d' % (len(frozen) - len(undeclared)))
    print('frozen, UNDECLARED           : %d' % len(undeclared))
    print()

    # *** THE LD-58 ROW IS CHECKED AGAINST JEFF'S WORDS, NOT JUST FOR MOVEMENT.
    # A row can be unfrozen and still score backwards, which is the defect
    # LD-58 itself fixed. Jeff, 2026-11-20: "Actual > 0 is Bad, Actual < 0 is
    # Good, Actual = 0 is Neutral. Also the latest release for Oct data is
    # 33.2K which should be scored as Bad or -1."
    print('LD-58 GBP Claimant Count Change, against Jeff 2026-11-20')
    ld58 = [('33.2K', -1), ('30.3K', -1), ('0', 0), ('-2K', 1),
            ('-11K', 1), ('-50K', 1), ('500K', -1)]
    bad = 0
    for v, want in ld58:
        got = ds.score_row('Employment', 'GBP', 'Claimant Count Change', v)
        ok = got == want
        if not ok:
            bad += 1
        print('  %-6s %-8s got=%-5s want=%-5s' % (
            'PASS' if ok else '*** FAIL', v, got, want))
    print()

    if undeclared:
        print('%d UNDECLARED FROZEN ROW(S) - a score nobody computed is '
              'being published.' % len(undeclared))
        print('Wire the rule into derive_scores.score_row, or declare it in')
        print('KNOWN_FROZEN with the reason. Do not declare it to pass.')
        return 1
    if bad:
        print('%d LD-58 CASE(S) FAIL - the row moves but reads wrong.' % bad)
        return 1
    print('No undeclared frozen rows. LD-58 matches Jeff\'s ruling.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
