# -*- coding: utf-8 -*-
"""R-41 - WHICH WHITELIST ROWS CAN WE NOT VERIFY? RAISE THEM, DO NOT HIDE THEM.

Jeff, 2026-09-13: "if you cannot match an indicator raise it with me so I can
check"

WHY THIS EXISTS. R-40 (vintage_check) answers "is any row STALE against a
print we have captured?" and on 2026-09-13 it answered 0. That reads like
assurance and is not. It can only compare a held value against a print it can
SEE, and it could see actuals for 37 of 78 whitelist rows. For the other 41 it
had never seen a print at all, so it returned clean BY SILENCE.

    A CHECK THAT CANNOT SEE A ROW MUST SAY SO. IT MUST NOT PASS.

That is the same lesson as F-36 ("make the extraction COUNT WHAT IT DROPS")
applied one layer up: R-40 counted what it compared and never counted what it
could not reach.

THE THREE STATES A ROW CAN BE IN. R-40 collapsed the last two into "fine":

    VERIFIED    a captured print matched this row, and the held value agrees
    STALE       a captured print matched, and the held value DISAGREES  (R-40)
    UNVERIFIED  no captured print has ever matched this row       <-- RAISE IT

UNVERIFIED has two very different causes, and this module separates them
because the remedy differs:

    NO EVENT    no capture contains any event that matches this row. Either
                the row did not print in a capture window, or it prints on a
                cadence longer than our capture history. Remedy: re-read the
                TE country page.
    UNMATCHED   a capture DOES hold an event for this currency that looks like
                this row, but match() returned None for it. That is F-119's
                class - a matcher gap - and it is the dangerous one, because
                the data was in our hands and we walked past it.

An UNMATCHED row is raised with the CANDIDATE EVENT TEXT so Jeff can rule on
identity. The repo does not get to decide it matched; he does.

WHY IT DOES NOT AUTO-WIDEN THE MATCHER. F-37 and F-119 are the same lesson
from both ends: a looser matcher invents false positives, a stricter one drops
true ones. Neither failure is detectable by the repo. So this module makes no
matching decision - it surfaces the candidate and stops. LD-103.

    python pipelines/coverage_check.py            # full coverage report
    python pipelines/coverage_check.py --raise    # exit 1 if anything UNMATCHED
"""
import io
import os
import sys
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import phtime as pt
import week_ahead as wa
import score_model as sm

CCY = {'US': 'USD', 'EA': 'EUR', 'GB': 'GBP', 'JP': 'JPY',
       'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}

# Rows whose actual deliberately lives outside score_model.ROWS (LD-117: GDP
# is calibrator-only), so "no held value" is correct rather than a gap.
NO_HELD = ('GDP Growth Rate QoQ',)

# Tokens that make an event a plausible candidate for a whitelist row without
# matching it. Deliberately crude - this is a SUGGESTION to a human, not a
# match. Anything sharing the distinctive words is worth Jeff's eye.
_STOP = set(('rate', 'index', 'yoy', 'mom', 'qoq', 'final', 'prel', 'change',
             'the', 'of', 'a', 'and', 'ex', 'adv', 'growth', 'total', 'net',
             'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep',
             'oct', 'nov', 'dec', 'q1', 'q2', 'q3', 'q4'))


def _key(name):
    return set(w for w in wa._norm(name.lower()) if w not in _STOP)


def _num(s):
    """The NUMBER a TE cell carries, ignoring how it is dressed.

    The first run of this module raised two rows that were not wrong:

        JPY Retail Sales YoY   held '4.0%'      captured '4%'
        USD Balance of Trade   held '-$88.6B'   captured '$-88.6B'

    Same value, different typography - trailing zero, and sign inside vs
    outside the currency mark. A guard that cries wolf on presentation gets
    ignored on the day it is right, so the comparison is on the NUMBER and
    the alert says which kind of difference it found.
    """
    t = (s or '').strip().lower()
    if not t:
        return None
    neg = '-' in t or t.startswith('(')
    keep = ''.join(ch for ch in t if ch.isdigit() or ch == '.')
    if not keep or keep.count('.') > 1:
        return None
    try:
        v = float(keep)
    except ValueError:
        return None
    for suf, mul in (('k', 1e3), ('m', 1e6), ('b', 1e9), ('t', 1e12)):
        if suf in t:
            v *= mul
            break
    return -v if neg else v


def same_value(a, b):
    """True when two TE cells carry the same number (or the same text)."""
    if (a or '').strip() == (b or '').strip():
        return True
    na, nb = _num(a), _num(b)
    return na is not None and nb is not None and abs(na - nb) < 1e-9


def scan():
    """Return (verified, stale, no_event, unmatched) for every whitelist row."""
    names, held = {}, {}
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        c = sm.LABEL[iso]
        names.setdefault(c, []).append(name)
        held[(c, name)] = a

    # Every event we have ever captured, per currency.
    seen, events = {}, {}
    for f in sorted(glob.glob(os.path.join(
            REPO, 'data/raw/calendar/*_cal_full.json'))):
        try:
            with io.open(f, encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception:
            continue
        for r in (data if isinstance(data, list) else data.get('events', [])):
            if not isinstance(r, dict):
                continue
            iso = r.get('iso')
            if iso not in CCY:
                continue
            ccy = CCY[iso]
            ev = str(r.get('event', ''))
            act = (r.get('actual') or '').strip()
            when = pt.te_pht(r.get('date'), r.get('time'))
            ds = when.strftime('%Y-%m-%d') if when else (r.get('date') or '')[:10]
            events.setdefault(ccy, {}).setdefault(ev, (ds, act, iso))
            if not act:
                continue
            hit = wa.match(ev.lower(), names.get(ccy, []), iso)
            if not hit:
                continue
            k = (ccy, hit)
            if k not in seen or ds > seen[k][0]:
                seen[k] = (ds, act, ev)

    verified, stale, fmt, no_event, unmatched = [], [], [], [], []
    for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
        c = sm.LABEL[iso]
        k = (c, name)
        if name in NO_HELD:
            continue
        if k in seen:
            ds, act, ev = seen[k]
            row = (c, name, cat, held[k], act, ds, ev)
            if (held[k] or '').strip() == (act or '').strip():
                verified.append(row)
            elif same_value(held[k], act):
                fmt.append(row)          # same number, different typography
            else:
                stale.append(row)
            continue
        # Never matched. Is there a plausible candidate we walked past?
        # ONLY events that already carry an actual count: a scheduled row with
        # no print yet is not data we missed, it is data that does not exist.
        want = _key(name)
        cands = []
        for ev, (ds, act, eiso) in events.get(c, {}).items():
            if not act:
                continue
            got = _key(ev)
            if want and len(want & got) >= max(1, len(want) - 1):
                cands.append((ev, ds, act))
        if cands:
            unmatched.append((c, name, cat, held[k], ref, sorted(cands)[:3]))
        else:
            no_event.append((c, name, cat, held[k], ref))
    return verified, stale, fmt, no_event, unmatched


if __name__ == '__main__':
    ver, stale, fmt, no_ev, unm = scan()
    tot = len(ver) + len(stale) + len(fmt) + len(no_ev) + len(unm)
    print('R-41 COVERAGE CHECK   %d scorable whitelist rows' % tot)
    print('  VERIFIED   held value agrees with a captured print : %d' % len(ver))
    print('  FORMAT     same number, different typography       : %d' % len(fmt))
    print('  STALE      held value disagrees   (R-40 raises)    : %d' % len(stale))
    print('  UNMATCHED  candidate event in hand, match() missed : %d' % len(unm))
    print('  NO EVENT   never appeared in any capture           : %d' % len(no_ev))
    print()

    if stale:
        print('*** STALE - THE BOARD IS SCORED ON A SUPERSEDED VALUE')
        for c, n, cat, h, act, ds, ev in sorted(stale):
            print('  %-4s %-34s held %-12s captured %-12s %s'
                  % (c, n[:34], h, act, ds))
        print()

    if fmt:
        print('FORMAT ONLY - same value, no scoring impact')
        for c, n, cat, h, act, ds, ev in sorted(fmt):
            print('  %-4s %-34s held %-12s captured %-12s' % (c, n[:34], h, act))
        print()

    if unm:
        print('=' * 78)
        print('*** RAISE WITH JEFF - WE HELD THE DATA AND DID NOT MATCH IT')
        print('=' * 78)
        for c, n, cat, a, ref, cands in sorted(unm):
            print('  %-4s %-34s held %s  (%s)' % (c, n[:34], a, ref))
            for ev, ds, act in cands:
                print('        candidate: %-42s %s  actual %s'
                      % (ev[:42], ds, act or '(none yet)'))
        print()

    if no_ev:
        print('NO CAPTURED EVENT - cannot be verified from the repo at all')
        print('  (remedy: re-read the TE country page for these rows)')
        print()
        print('  %-4s %-34s %-12s %s' % ('CCY', 'ROW', 'HELD', 'REF'))
        for c, n, cat, a, ref in sorted(no_ev):
            print('  %-4s %-34s %-12s %s' % (c, n[:34], (a or '')[:12], ref))
        print()

    if unm:
        print('*** %d ROW(S) NEED JEFF TO RULE ON IDENTITY.' % len(unm))
        if '--raise' in sys.argv:
            sys.exit(1)
    elif not no_ev:
        print('  every scorable row is verified against a captured print')
