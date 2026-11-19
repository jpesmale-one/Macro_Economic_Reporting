# -*- coding: utf-8 -*-
"""Replay each real historical failure against run_daily's gates.

Operates ONLY on a scratchpad copy of the bar files. data/raw/ is never
touched - it is immutable (CLAUDE.md section 6), and an earlier version of
this script edited it directly, which was wrong.

The gates read bars via daily_report.TXT, so the copy is installed by
repointing that module attribute. That also means the FIRST version of this
replay proved nothing: it corrupted data/raw/bars/*.json, which no gate
reads, and reported "DID NOT BITE" about a gate it had never exercised.
"""
import io
import os
import sys
import glob
import shutil

import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
WORK = os.path.join(tempfile.gettempdir(), 'macro_gate_replay')

sys.path.insert(0, HERE)
os.chdir(REPO)

import daily_report as dr
import run_daily as rd

# *** DERIVED, NEVER PINNED. F-188's rule is that a session is closed only
# once the NEXT session's bar has opened, so the newest closed session is the
# SECOND-NEWEST bar, and it moves every time bars are pulled. The first
# version of this replay pinned the newest bar's own date as its clean
# baseline, and reported a FALSE ALARM against a gate that was answering
# correctly - the test was wrong, not the gate. A pinned date here would also
# rot exactly the way F-170 and F-183 did.
def newest_closed():
    b = dr.bars('EURUSD')
    return b[-2][0]


def fresh():
    """Reset the working copy and point the reader at it.

    The copy is taken from the LIVE bar files each time, so this test needs
    no fixture checked in and no scratchpad that cleanup can clear. It never
    writes to them: dr.TXT is repointed at the copy, and only the copy is
    ever edited. data/raw/ is immutable (CLAUDE.md section 6) and is not
    involved at all - these bars live beside the pipelines as .txt.
    """
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    for p in glob.glob(os.path.join(HERE, '*.txt')):
        shutil.copy(p, WORK)
    dr.TXT = WORK


def rows(pair):
    p = os.path.join(WORK, pair + '.txt')
    return io.open(p, encoding='utf-8').read().splitlines()


def write(pair, lines):
    io.open(os.path.join(WORK, pair + '.txt'), 'w',
            encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


def say(name, bites, ok, detail):
    verdict = ('BITES' if not ok else '*** DID NOT BITE') if bites else \
              ('PASSES' if ok else '*** FALSE ALARM')
    print('  %-26s %-18s %s' % (name, verdict, detail[:84]))
    return (not ok) == bites


fresh()
SESSION = newest_closed()
OPEN_SESSION = dr.bars('EURUSD')[-1][0]

results = []
print('GATE REPLAY against the real historical failures')
print('  bar copy: %s' % WORK)
print('  newest closed session: %s' % SESSION)
print()

# --- baseline: a clean grid must pass every gate. A gate that always fires
# is not a gate, so this is tested first and counts as a result.
fresh()
results.append(say('clean grid', False, *rd.g_grid_complete({'session': SESSION})))
results.append(say('clean bars', False, *rd.g_bars_are_price({'session': SESSION})))
results.append(say('closed session', False, *rd.g_session_closed({'session': SESSION})))
print()

# --- F-190: the real corrupt pull. 44% of bars had `open` overwritten by the
# low or the high. That flipped four of ten session states while every number
# on the page stayed internally consistent.
fresh()
ls = rows('EURUSD')
k = int(len(ls) * 0.44)
out = []
for i, ln in enumerate(ls):
    x = ln.split()
    if i < k and len(x) >= 5:
        x[1] = x[3]                      # open := low, the real signature
    out.append(' '.join(x))
write('EURUSD', out)
results.append(say('F-190 44% corrupt pull', True,
                   *rd.g_bars_are_price({'session': SESSION})))

# below threshold must NOT fire - the 20% line sits above real doji noise
fresh()
ls = rows('EURUSD')
k = int(len(ls) * 0.13)                  # the top of the real clean range
out = []
for i, ln in enumerate(ls):
    x = ln.split()
    if i < k and len(x) >= 5:
        x[1] = x[3]
    out.append(' '.join(x))
write('EURUSD', out)
results.append(say('F-190 13% (real noise)', False,
                   *rd.g_bars_are_price({'session': SESSION})))

# --- R-50: the real 17 Oct condition. CHF and NZD had ONE counterpart each,
# so breadth measured 40 of 40 BROAD-ish and NARROW could never fire.
fresh()
for f in ('EURCHF', 'GBPCHF', 'AUDCHF', 'CADCHF', 'CHFJPY',
          'EURNZD', 'GBPNZD', 'NZDCAD'):
    os.remove(os.path.join(WORK, f + '.txt'))
results.append(say('R-50 thin grid (17 Oct)', True,
                   *rd.g_grid_complete({'session': SESSION})))

# --- R-50 ragged: one cross a day behind the rest. This is the silent shrink
# that does not error - the file exists, it is just short.
fresh()
ls = rows('NZDCHF')
write('NZDCHF', ls[:-1])
results.append(say('R-50 one cross behind', True,
                   *rd.g_grid_complete({'session': SESSION})))

# --- F-188: the real 3 Nov failure. Reporting a session whose bar is still
# being written. Published GBPNZD as DRIFT when it was CLEAN at 1.152x ATR.
fresh()
results.append(say('F-188 open session', True,
                   *rd.g_session_closed({'session': OPEN_SESSION})))

shutil.rmtree(WORK)
print()
bad = results.count(False)
if bad:
    print('*** %d of %d replays gave the WRONG verdict' % (bad, len(results)))
else:
    print('all %d replays verdict-correct' % len(results))
sys.exit(1 if bad else 0)
