# -*- coding: utf-8 -*-
"""R-38: every threshold must match Idea_dump/Macro_economic_indicators.txt.

F-96, F-97, F-98. Across three release syncs I rewrote SEVEN thresholds -
EUR Retail Sales, CAD Employment Change, USD NFP, JPY Household Spending,
and the USD/AUD/CAD Balance of Trade rows - each time while describing the
work as "updating a value".

WHY IT KEPT HAPPENING. When a release lands, TE hands over actual, previous
AND consensus. Writing that consensus into the threshold FEELS like
recording more information. It is not: the threshold column is the RULE Jeff
specified, and replacing it with the week's consensus silently swaps a
standing rule for a one-off comparison.

The cost was not cosmetic. Restoring the Balance of Trade rows flipped USD
and AUD from GOOD to BAD, moved both currencies 4.00 points, and changed all
three selected pairs.

Jeff's draft is the authority (F-3: the indicator list and its rules are his
call), it has been in the repo since 2026-08-19, and nothing compared
against it until now.

USAGE
    python pipelines/audit_spec.py
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import score_model as sm

SPEC = os.path.join(REPO, 'Idea_dump', 'Macro_economic_indicators.txt')

# Jeff's prose rules -> the threshold token the whitelist uses for them.
RULES = [
    (r'actual\s*>\s*previous is good.*?actual\s*<\s*previous is bad',
     '>Prev'),
    (r'actual\s*<\s*previous is good.*?actual\s*>\s*previous is bad',
     '<Prev'),
    (r'actual\s*>\s*0\.5%\s*is good.*?<\s*0%\s*is bad', '>0.5%'),
    (r'actual\s*>\s*50\.5\s*is good', '>50.5'),
    # LD-104 retired this form from the BASE - consensus now lives in the
    # calibrator only. Kept so an unamended copy of the draft still parses
    # and reports the disagreement rather than silently matching nothing.
    (r'actual\s*>\s*consensus/forecast is good', '>Cons'),
]

# A LATER LOCKED DECISION MAY LEGITIMATELY OVERRIDE THE DRAFT, and that is
# not drift. Each entry names the decision and why, so the exemption is a
# claim someone can check rather than a silent skip. Nothing goes in here
# because a row is inconvenient - only because Jeff changed the rule AFTER
# the draft and said so.
OVERRIDES = {
    # LD-117/LD-118 - GDP is a CALIBRATOR row scored on the
    # consensus-forecast RANGE, not a level threshold. The spec and the
    # code agree; they are simply not the same KIND of rule, so a string
    # comparison of thresholds cannot match. Jeff, 2026-09-10: "We're
    # trading the expectations not the result."
    ('USD', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),
    ('EUR', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),
    ('GBP', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),
    ('JPY', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),
    ('AUD', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),
    ('NZD', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),
    ('CAD', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),
    ('CHF', 'GDP Growth Rate QoQ'): ('>0 range (LD-117)', 'LD-117 - calibrator range rule scored on the consensus-forecast RANGE, not a level threshold'),

    ('GBP', 'Claimant Count Change'): (
        '<0 (LD-58)',
        'LD-58, Jeff 2026-08-24: the series measures the CHANGE in claimants, '
        'so the SIGN is the signal and the prior month is not. ">Prev" read '
        'backwards - claimants falling 2K after falling 11K graded BAD.'),
}

ISO_HDR = re.compile(r'^\s*[a-z]\.\s*(US|EA|GB|JP|AU|NZ|CA|CH)\s*$', re.I)
IND_HDR = re.compile(r'^\s*[ivx]+\.\s*(.+?)\s*$', re.I)


def parse_spec():
    """{(ccy, indicator): threshold-token} from Jeff's draft."""
    out = {}
    ccy = None
    ind = None
    with io.open(SPEC, encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            m = ISO_HDR.match(line.rstrip())
            if m:
                ccy = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
                       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD',
                       'CH': 'CHF'}[m.group(1).upper()]
                ind = None
                continue
            m = IND_HDR.match(line.rstrip())
            if m and ccy and not re.match(r'^\s*\d', m.group(1)):
                cand = m.group(1).strip()
                if cand and not cand[0].isdigit():
                    ind = cand
                continue
            if ccy and ind:
                low = line.lower()
                for pat, tok in RULES:
                    if re.search(pat, low, re.S):
                        out[(ccy, ind)] = tok
                        break
    return out


def check():
    spec = parse_spec()
    ours = {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        ours[(sm.LABEL[iso], name)] = thr.strip()
    bad, matched, unmatched = [], 0, []
    for k, want in sorted(spec.items()):
        if k not in ours:
            unmatched.append(k)
            continue
        matched += 1
        got = ours[k]
        if k in OVERRIDES and got == OVERRIDES[k][0]:
            continue                       # a later locked decision, not drift
        if got != want:
            bad.append((k[0], k[1], want, got))
    return bad, matched, unmatched, len(spec)


if __name__ == '__main__':
    bad, matched, unmatched, n = check()
    print('R-38 THRESHOLDS vs THE SOURCE SPEC')
    print('  spec: Idea_dump/Macro_economic_indicators.txt')
    print('  %d rules parsed, %d matched to whitelist rows' % (n, matched))
    print()
    if matched == 0:
        print('  *** MATCHED NO ROWS - this check proved NOTHING.')
        print('      The spec parser found no rule it could pair with a')
        print('      whitelist row. Fix the parser before trusting a pass.')
        sys.exit(1)
    if bad:
        for ccy, ind, want, got in bad:
            print('  *** %-4s %-32s spec=%-10s ours=%s' % (ccy, ind[:32],
                                                           want, got))
    else:
        print('  every matched threshold agrees with the spec')
    if OVERRIDES:
        print()
        print('  %d threshold(s) EXEMPT by a later locked decision:'
              % len(OVERRIDES))
        for (ccy, ind), (tok, why) in sorted(OVERRIDES.items()):
            print('      %-4s %-28s %s' % (ccy, ind[:28], tok))
            print('           %s' % why)
    if unmatched:
        # LD-105: a draft row with no whitelist row is EITHER harmless naming
        # drift OR a removal that never reached the root. LD-102 dropped CHF
        # Industrial Production from the code and the CSV and left it live in
        # the draft - exactly the two-authorities-diverging failure the rule
        # exists to prevent. A row explicitly marked REMOVED/WAS is accounted
        # for; anything else is listed for a human to judge.
        silent = [(c, i) for c, i in unmatched
                  if 'REMOVED' not in i.upper() and 'WAS:' not in i.upper()]
        marked = len(unmatched) - len(silent)
        print()
        print('  %d spec rule(s) name no whitelist row (%d marked REMOVED):'
              % (len(unmatched), marked))
        for ccy, ind in silent[:10]:
            print('      %-4s %s' % (ccy, ind[:44]))
        if silent:
            print('      -> naming drift, OR a removal that never reached the'
                  ' draft. Check before ignoring.')
    print()
    print('%d disagreement(s)' % len(bad))
    sys.exit(1 if bad else 0)
