# -*- coding: utf-8 -*-
"""R-52 - can our matcher still READ the newest capture? (F-193)

*** THE DEFECT THIS EXISTS FOR. biquote replaced TE as the calendar source.
The adapter was validated on all eight currencies, forward expectations, and
history to August at 92-96% actuals - every check passed, and every one of
them is a property of THE SOURCE. Not one asked whether our own whitelist
matcher could still read it.

It could not. biquote names the same series differently:

    inflation rate yoy   MATCHES        cpi y/y    -> None
    gdp growth rate qoq  MATCHES        gdp q/q    -> None
    retail sales mom     MATCHES        retail sales m/m -> None

Whitelist coverage fell from 68-73 of 78 across five TE captures to 33 of 78
on the first biquote capture. The capture held MORE rows than TE ever served
(1,536 vs ~900), so every count I took looked better.

*** A SOURCE SWAP IS NOT A DATA CHANGE, IT IS A VOCABULARY CHANGE. The rows
were all present. What changed was whether we could name them.

*** WHY A RATIO AND NOT A FIXED FLOOR. Coverage legitimately varies with the
capture window - TE's own captures ranged 68 to 73 - so an absolute threshold
either passes a real break or cries wolf on a quiet week. What is NOT normal
is a sudden DROP against the captures before it. So this compares the newest
capture to the median of the previous ones and fails on a cliff.

*** THIS GUARD DOES NOT FIX ANYTHING, AND MUST NOT. The repair is a table of
named equivalences ('cpi y/y' IS 'Inflation Rate YoY'), and each pair asserts
an identity. The repo never rules on identity (R-41, F-3) - it reports the
gap and names the candidates. LD-59 also forbids loosening the matcher: a
fuzzy bridge would bind AUD 'Inflation Rate YoY' to 'TD-MI Inflation Gauge',
and a loose match does not report an absence, it invents a presence.

    python pipelines/capture_vocab.py           # report
    python pipelines/capture_vocab.py --raise   # non-zero on a cliff
"""
import io
import os
import sys
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import week_ahead as wa
import score_model as sm

CAPS = os.path.join(REPO, 'data/raw/calendar/*_cal_full.json')
CCY = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}
ISO = dict((v, k) for k, v in CCY.items())

# A drop of more than this fraction below the recent median is a cliff.
# 0.85 passes TE's own 68..73 spread (68/71 = 0.958) with room, and fails
# the biquote break (33/71 = 0.465) by a wide margin.
FLOOR = 0.85


# *** THE VOCABULARY DIFFERENCES, AS A TABLE OF SUBSTITUTIONS.
#
# These are not equivalences and they do not map anything - they are the
# spelling changes needed to turn OUR name into a SEARCH KEY for this
# source, so the operator is shown the right row to rule on. The identity
# ruling itself is Jeff's (R-41, F-3), and the accepted result belongs in
# capture_biquote.RENAME, not here.
SPELL = (
    ('inflation rate', 'cpi'),
    ('gdp growth rate', 'gdp'),
    ('yoy', 'y/y'),
    ('mom', 'm/m'),
    ('qoq', 'q/q'),
)


def candidates(name, events):
    """Capture events worth comparing to a whitelist row, best first.

    Exact-key matches only, after spelling substitution. A near neighbour is
    deliberately NOT offered: the point is to name the row Jeff should rule
    on, not to rank the vaguely similar.
    """
    k = name.lower()
    for a, b in SPELL:
        k = k.replace(a, b)
    k = k.replace(' final', '').replace(' fin', '').strip()
    hits = [e for e in events if e == k]
    if not hits:
        # the same key with a qualifier attached, e.g. 'cpi y/y' vs ours
        hits = [e for e in sorted(events) if e.startswith(k + ' ')
                or e == k.replace(' y/y', '')]
    return hits


def whitelist():
    """{ccy: [row name]} - the closed set, per currency (F-3)."""
    out = {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        out.setdefault(CCY[iso], []).append(name)
    return out


def matched(path, names):
    """{ccy: set(row names this capture can be read as)}."""
    raw = json.load(io.open(path, encoding='utf-8'))
    rows = raw if isinstance(raw, list) else raw.get(
        'rows', raw.get('events', []))
    per = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        iso = r.get('iso')
        if iso not in CCY:
            continue
        hit = wa.match(str(r.get('event') or '').lower(),
                       names.get(CCY[iso], []), iso)
        if hit:
            per.setdefault(CCY[iso], set()).add(hit)
    return per, len(rows)


def total(per):
    return sum(len(v) for v in per.values())


def main():
    names = whitelist()
    size = sum(len(v) for v in names.values())
    caps = sorted(glob.glob(CAPS))
    if len(caps) < 2:
        print('need at least two captures to compare')
        return 0

    print('R-52 CAPTURE VOCABULARY   can the whitelist still read the source?')
    print('  whitelist size: %d rows' % size)
    print()

    hist = []
    for p in caps[-6:]:
        per, n = matched(p, names)
        hist.append((os.path.basename(p), n, total(per), per))
        print('  %-34s rows=%-5d matched=%2d of %d'
              % (hist[-1][0][:34], n, hist[-1][2], size))

    newest = hist[-1]
    prior = sorted(h[2] for h in hist[:-1])
    if not prior:
        return 0
    med = prior[len(prior) // 2]
    ratio = (newest[2] / float(med)) if med else 1.0

    print()
    print('  newest: %d matched   recent median: %d   ratio %.2f (floor %.2f)'
          % (newest[2], med, ratio, FLOOR))

    if ratio >= FLOOR:
        print('  the matcher can still read the source.')
        return 0

    print()
    print('  *** VOCABULARY BREAK - %d rows went unreadable, not missing.'
          % (med - newest[2]))
    print('      The capture may hold MORE rows than before; what changed is')
    print('      whether we can NAME them. Do NOT loosen the matcher (LD-59).')
    print()
    print('  UNREADABLE WHITELIST ROWS, and candidates in the capture:')

    raw = json.load(io.open(caps[-1], encoding='utf-8'))
    rows = raw if isinstance(raw, list) else raw.get(
        'rows', raw.get('events', []))
    evs = {}
    for r in rows:
        if isinstance(r, dict) and r.get('iso') in CCY:
            evs.setdefault(r['iso'], set()).add(
                str(r.get('event') or '').lower())

    for ccy in sorted(names):
        got = newest[3].get(ccy, set())
        for n in names[ccy]:
            if n in got:
                continue
            # A CANDIDATE IS A SUGGESTION FOR A HUMAN, NEVER AN AUTO-MAP.
            # Shown so Jeff can rule on identity; the repo does not.
            #
            # *** THE FIRST VERSION SUGGESTED BY HEAD TOKEN AND MISLED.
            # 'Inflation Rate YoY' searched on 'inflation', which found AUD
            # 'mi inflation expectations' - a SURVEY of expected inflation,
            # not the CPI print - while missing 'cpi y/y' entirely, and
            # reported CAD and CHF inflation as "absent from source" when
            # both publish 'cpi y/y'. A suggestion that names the wrong
            # series is worse than none: it invites exactly the identity
            # error R-41 exists to prevent, and it does it in the voice of
            # a guard. So candidates now come from a SYNONYM table of known
            # vocabulary differences, and anything with no synonym entry is
            # reported as "no candidate" - our ignorance, not the source's
            # silence (F-73).
            cand = candidates(n, evs.get(ISO[ccy], ()))
            print('    %-4s %-30s %s' % (
                ccy, n[:30], ', '.join(cand[:2]) or '(no candidate - check by hand)'))

    print()
    print('  THE REPAIR IS A TABLE OF NAMED EQUIVALENCES in')
    print('  capture_biquote.RENAME, where source-vocabulary knowledge')
    print('  already lives. Each entry asserts two names are the SAME')
    print('  series, which is a judgement about identity - and identity is')
    print('  Jeff\'s call, never the repo\'s (R-41, F-3).')
    return 1 if '--raise' in sys.argv else 0


if __name__ == '__main__':
    sys.exit(main())
