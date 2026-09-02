# -*- coding: utf-8 -*-
"""R-35 - every section must MOVE between editions (F-80).

Jeff, 2026-09-02: "Didn't I asked that every section should be revisited and
refreshed everytime we build a new edition? is there any other sections of
the report still stale?"

He asked for this on 26 Aug and it is in CLAUDE.md. I had been refreshing the
sections I happened to touch and letting the rest carry. Measuring it:

    0   41% same   REFRESHED
    1   59%        REFRESHED
    3   29%        REFRESHED
    2   96%        partial
    5   90%        partial
    6   89%        partial
    4   99.2%      CARRIED VERBATIM   <- the selection playbook
    7  100.0%      CARRIED VERBATIM   <- guard results from yesterday's run
    8  100.0%      CARRIED VERBATIM
    9  100.0%      CARRIED VERBATIM

4 was the expensive one. 4.3 published SUNDAY's room and clear-by figures
as though current - GBPAUD room 0.92 when 4.2 in the SAME EDITION said 0.56.
4.1 counted event risk on twelve rows that had already released, leaving NZD
reading CROWDED on printed events. 4.5's bench was three sessions old. And
7 said "Market CLOSED, Friday's bars are FINAL" on a Wednesday.

WHAT THIS GUARD DOES NOT DO. It cannot tell a section that legitimately
did not change from one that was forgotten - 8 (findings ledger) and 9
(gate status) often genuinely repeat. So it REPORTS rather than blocks, and
names what carried verbatim so the omission is visible rather than silent.

    python pipelines/section_drift.py <today.md> <previous.md>
"""
import io, os, re, sys, difflib

# Sections where a verbatim carry is legitimate: 8 is a findings ledger and
# 9 a gate table - both change only when something happens.
QUIET = ('8', '9')


def sections(md):
    out, cur, buf = {}, None, []
    for line in md.split(chr(10)):
        m = re.match(r'^##\s*§(\d+[a-z]?)', line)
        if m:
            if cur:
                out[cur] = chr(10).join(buf)
            cur, buf = m.group(1), [line]
        elif cur is not None:
            buf.append(line)
    if cur:
        out[cur] = chr(10).join(buf)
    return out


def drift(today_md, prev_md):
    """[(section, same_ratio, verdict)] for every section, worst first."""
    A, B = sections(prev_md), sections(today_md)
    rows = []
    for k in sorted(B, key=lambda x: float(re.sub(r'[a-z]', '', x) or 0)):
        if k not in A:
            rows.append((k, 0.0, 'NEW'))
            continue
        r = difflib.SequenceMatcher(None, A[k], B[k]).ratio()
        if r >= 0.995:
            v = 'CARRIED VERBATIM' + ('' if k in QUIET else '  <-- CHECK')
        elif r >= 0.97:
            v = 'barely moved' + ('' if k in QUIET else '  <-- CHECK')
        elif r >= 0.75:
            v = 'partial'
        else:
            v = 'refreshed'
        rows.append((k, r, v))
    return rows


def report(today_md, prev_md):
    rows = drift(today_md, prev_md)
    print('R-35 SECTION DRIFT (F-80)')
    print('  Jeff, 2026-08-26: "Everytime we build a new edition we should be')
    print('  looking if every parts of the report have moved."')
    print()
    print('  %-5s %8s  %s' % ('SEC', 'SAME', 'VERDICT'))
    print('  ' + '-' * 44)
    flagged = 0
    for k, r, v in rows:
        if 'CHECK' in v:
            flagged += 1
        print('  %-5s %7.1f%%  %s' % (k, r * 100, v))
    print()
    if flagged:
        print('  %d section(s) flagged. A section that did not move is not' %
              flagged)
        print('  automatically wrong - but it must be a DECISION, not an')
        print('  oversight. 4.3 carried Sunday room figures for three days')
        print('  and contradicted 4.2 in the same edition (F-80).')
    else:
        print('  Every section moved, or carried by design.')
    return flagged


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit('usage: section_drift.py <today.md> <previous.md>')
    report(io.open(sys.argv[1], encoding='utf-8').read(),
           io.open(sys.argv[2], encoding='utf-8').read())
