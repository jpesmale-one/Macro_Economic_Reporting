# -*- coding: utf-8 -*-
"""LD-67 / R-18: the WHOLE-EDITION SWEEP.

Jeff, 2026-08-26: "Everytime we build a new edition we should be looking if
every parts of the report have moved. we should be looking at it wholistically
and not just look at the moving parts"

Four defects that day lived in parts nobody re-read:
  F-46  a score carried into 5/6 that contradicted 2.0
  F-51  a Fear & Greed block 5 days stale, blaming the source
  F-52  4.4 calling a LOCKED pair REJECTED, carried 3 editions
  F-53  4.5 using a 5-day high as a 45-bar high, inverting a ranking

The other guards check what CHANGES. This checks what DOESN'T - which is
where staleness hides.

DESIGN NOTES, both earned by false positives during development:
 1. Comparing every number a pair carries flags normal structure (lock ref,
    falsifier, Monday close and Tuesday close differ BY DESIGN). Only compare
    LIKE AGAINST LIKE - the same named column across sections.
 2. A row may legitimately record a past verdict beside a current one
    ("REJECTED then, LOCKED now"). Read the row's LAST cell for its current
    status, not any occurrence of the word.
"""
import io, os, re, sys

REPO = r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting'
CCY = r'(?:USD|EUR|GBP|JPY|CHF|CAD|AUD|NZD)'
PAIR = re.compile(r'\b(' + CCY + CCY + r')\b')
NUM = re.compile(r'^\d+\.\d{3,5}$')

# Column headers that mean "the price as of THIS edition". Only these are
# compared against each other.
#
# The day name is matched generically - hardcoding "tue close" meant that on
# 2026-08-27 the guard compared section 0's PRIOR-day column against 4.5's
# CURRENT-day column and reported three false contradictions. A column naming
# an EARLIER session is legitimate history and must not be compared to a
# current one; only the newest day-labelled column in the edition counts.
PRICE_COL = re.compile(
    r'(mon|tue|wed|thu|fri) close|current|now$|live', re.I)
DAYS = ['mon', 'tue', 'wed', 'thu', 'fri']


def sections(md):
    out, cur, buf = [], 'PREAMBLE', []
    for line in md.split(chr(10)):
        if line.startswith('## ') or line.startswith('### '):
            out.append((cur, chr(10).join(buf)))
            cur, buf = line.strip('# ').strip(), []
        else:
            buf.append(line)
    out.append((cur, chr(10).join(buf)))
    return out


def _cells(line):
    return [c.strip().replace('*', '').replace('\u2212', '-')
            for c in line.strip().strip('|').split('|')]


def _tables(body):
    """Yield (header_cells, [row_cells]) for each markdown table."""
    rows, hdr = [], None
    for line in body.split(chr(10)):
        if not line.strip().startswith('|'):
            if hdr and rows:
                yield hdr, rows
            hdr, rows = None, []
            continue
        c = _cells(line)
        if set(''.join(c)) <= set('-: '):
            continue
        if hdr is None:
            hdr = c
        else:
            rows.append(c)
    if hdr and rows:
        yield hdr, rows


def sweep(md):
    secs = sections(md)
    problems = []

    # ---- 1. LOCKED vs REJECTED: a pair cannot currently be both ----
    locked, rejected = set(), set()
    for head, body in secs:
        h = head.lower()
        if '4.3' in h and 'locked' in h:
            for line in body.split(chr(10)):
                if line.startswith('|'):
                    locked |= set(PAIR.findall(line))
        if '4.4' in h and 'reject' in h:
            for line in body.split(chr(10)):
                if not line.startswith('|') or line.startswith('|---'):
                    continue
                c = _cells(line)
                if len(c) >= 2 and 'REJECT' in c[-1].upper():
                    rejected |= set(PAIR.findall(line))
    for p in sorted(locked & rejected):
        problems.append(('CONTRADICTION',
                         '%s is LOCKED in 4.3 and REJECTED in 4.4' % p))

    # ---- 2. the FALSIFIER must be identical wherever it appears ----
    fals = {}
    for head, body in secs:
        for line in body.split(chr(10)):
            if not line.startswith('|') or 'close' not in line:
                continue
            ps = PAIR.findall(line)
            m = re.search(r'close [<>] \*{0,2}(\d+\.\d+)', line)
            if len(ps) == 1 and m:
                fals.setdefault(ps[0], {}).setdefault(m.group(1), []).append(head)
    for pair, vals in sorted(fals.items()):
        if len(vals) > 1:
            problems.append(('FALSIFIER DRIFT', '%s: %s' % (
                pair, '; '.join('%s in %s' % (v, ks[0])
                                for v, ks in sorted(vals.items())))))

    # ---- 3. the CURRENT PRICE must agree across sections ----
    # Only columns whose HEADER says it is a current price are compared, and
    # only for the LATEST session the edition names. A "Tue close" column
    # sitting beside a "Wed close" column is history, not a contradiction.
    latest = -1
    for head, body in secs:
        for hdr, _rows in _tables(body):
            for h in hdr:
                m = re.search(r'(mon|tue|wed|thu|fri) close', h, re.I)
                if m:
                    latest = max(latest, DAYS.index(m.group(1).lower()))

    price = {}
    for head, body in secs:
        for hdr, rows in _tables(body):
            idx = []
            for i, h in enumerate(hdr):
                if not PRICE_COL.search(h):
                    continue
                m = re.search(r'(mon|tue|wed|thu|fri) close', h, re.I)
                if m and latest >= 0 and DAYS.index(m.group(1).lower()) < latest:
                    continue          # an earlier session - history, skip
                idx.append(i)
            if not idx:
                continue
            for r in rows:
                ps = PAIR.findall(' '.join(r))
                if len(set(ps)) != 1:
                    continue
                for i in idx:
                    if i < len(r) and NUM.match(r[i]):
                        price.setdefault(ps[0], {}).setdefault(r[i], []
                                                               ).append(head)
    for pair, vals in sorted(price.items()):
        if len(vals) > 1:
            problems.append(('PRICE DRIFT', '%s: %s' % (
                pair, '; '.join('%s in %s' % (v, ks[0].split('\u2014')[0].strip()[:20])
                                for v, ks in sorted(vals.items())))))
    return problems


def report(path):
    md = io.open(path, encoding='utf-8').read()
    probs = sweep(md)
    print('WHOLE-EDITION SWEEP (LD-67) - %s' % os.path.basename(path))
    print('=' * 72)
    if not probs:
        print('  No cross-section contradictions found.')
    for kind, msg in probs:
        print('  %-18s %s' % (kind, msg))
    print()
    print('%d problem(s)' % len(probs))
    return probs


if __name__ == '__main__':
    os.chdir(REPO)
    report(sys.argv[1] if len(sys.argv) > 1
           else 'reports/2026/Q3/2026-08-26_market-sentiment.md')
