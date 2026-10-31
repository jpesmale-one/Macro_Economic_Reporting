# -*- coding: utf-8 -*-
"""Recompute every figure on the 26-30 Oct retro and fail on any mismatch.

A retrospective is hand-authored prose around machine numbers. The prose is
mine; the numbers must not be. This re-derives the set from the graders and
asserts each figure appears on the page, so a typo cannot survive the build.

R-46 step 8 scans DATE PAIRS and is blind to prose month names - F-168 rode
that blind spot for six weeks - so this also checks the window text and the
<title>, which F-171 showed the Artifact platform reads as the page's name.
"""
import io
import os
import re
import sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import daily_report as dr
import atr_grade as ag
import risk_index as RI

DAYS = ['2026-10-26', '2026-10-27', '2026-10-28', '2026-10-29', '2026-10-30']
PAGE = os.path.join(REPO, 'reports', '2026', 'Q4', '2026-10-31_retro.html')

fails = []
oks = []


def check(name, cond, detail=''):
    (oks if cond else fails).append((name, detail))


def bars(pair):
    out = []
    for ln in io.open(os.path.join(HERE, '%s.txt' % pair), encoding='utf-8'):
        x = ln.split()
        if len(x) >= 5:
            d = (dt.datetime(1970, 1, 1)
                 + dt.timedelta(seconds=int(x[0]) + 12 * 3600)).date()
            out.append((d.isoformat(),) + tuple(float(v) for v in x[1:5]))
    return sorted(out)


h = io.open(PAGE, encoding='utf-8').read()
board, picks = dr.load_edition()

# --- 1. the set is the EDITION's set, not a re-pick -----------------------
check('set is the published edition (LD-97)',
      [p for p, s in picks] == ['CADCHF', 'GBPAUD', 'AUDJPY'],
      str(picks))

# --- 2. per-pair fav/adv/ratio -------------------------------------------
setf = seta = 0.0
for pair, side in picks:
    bb = bars(pair)
    f = ag.pip_factor(pair)
    atr = ag.atr([(hi, lo, c) for d, o, hi, lo, c in bb if d < DAYS[0]], 14, f)
    F = A = 0.0
    for day in DAYS:
        row = [x for x in bb if x[0] == day]
        if not row:
            fails.append(('%s has no bar for %s' % (pair, day), ''))
            continue
        _, o, hi, lo, c = row[0]
        fav, adv, _fr, _hit = ag.grade_day(side, o, hi, lo, f, atr)
        F += fav
        A += adv
    setf += F
    seta += A
    # F-177 again: anchor on THIS pair's own row, not the whole document.
    prow = re.search(r'<td class="ccy">%s</td>(.*?)</tr>' % pair, h, re.S)
    check('%s row present in §1' % pair, bool(prow))
    if prow:
        pc = [re.sub('<[^>]*>', '', c).strip()
              for c in re.findall(r'<td[^>]*>(.*?)</td>', prow.group(1), re.S)]
        for val in ('%.1f' % F, '%.1f' % A, '%.2f' % (F / A)):
            check('%s row carries %s' % (pair, val), val in pc,
                  'row=%s' % pc[:4])
        band = ('WIN' if F / A >= 1.40
                else ('LOSS' if F / A < 0.70 else 'CONTESTED'))
        check('%s verdict %s in its own row' % (pair, band), band in pc, band)

# --- 3. the set total and its LD-149 verdict ------------------------------
# *** F-177 - "IS THE NUMBER ON THE PAGE" IS NOT A CHECK. My first version
# asserted `val in h` for every figure, and a mutation test caught it dead:
# changing the SET TOTAL cell from 1.07 to 1.17 left all 35 checks passing,
# because 1.07 also appears in the dek, two notes and §6 - six other copies
# kept the substring satisfied while the table told a lie.
# This is the F-171/F-172 shape for the third time: a substring test passes
# on text that happens to contain the token. The fix is the same one that
# worked there - ANCHOR ON THE STRUCTURE, here the cell that must carry the
# value, so each figure is checked where it is actually claimed.
ratio = setf / seta
row = re.search(r'<td colspan="2"><strong>SET TOTAL</strong></td>(.*?)</tr>',
                h, re.S)
check('SET TOTAL row present', bool(row))
if row:
    cells = re.findall(r'<td[^>]*>(.*?)</td>', row.group(1), re.S)
    plain = [re.sub('<[^>]*>', '', c).strip() for c in cells]
    for val in ('%.1f' % setf, '%.1f' % seta, '%.2f' % ratio):
        check('SET TOTAL cell carries %s' % val, val in plain,
              'cells=%s' % plain[:3])

# and the dek must agree with the table rather than merely mention a number
dek = re.search(r'<p class="dek">(.*?)</p>', h, re.S)
check('dek states the computed set ratio',
      bool(dek) and ('%.2f' % ratio) in dek.group(1),
      '%.2f' % ratio)

verdict = 'WIN' if ratio >= 1.40 else ('LOSS' if ratio < 0.70 else 'CONTESTED')
check('set verdict %s stated' % verdict,
      '<strong>%s</strong>' % verdict in h, verdict)

# --- 4. LD-169 must agree when nothing is grouped -------------------------
import group_ratio as gr
per = {}
bias = {}
for pair, side in picks:
    bb = bars(pair)
    f = ag.pip_factor(pair)
    atr = ag.atr([(hi, lo, c) for d, o, hi, lo, c in bb if d < DAYS[0]], 14, f)
    F = A = 0.0
    for day in DAYS:
        row = [x for x in bb if x[0] == day]
        if row:
            _, o, hi, lo, c = row[0]
            fav, adv, _fr, _hit = ag.grade_day(side, o, hi, lo, f, atr)
            F += fav
            A += adv
    per[pair] = (F, A)
    bias[pair] = side
gratio, _detail = gr.set_ratio(per, bias)
check('LD-169 grouped ratio equals plain ratio this week',
      abs(gratio - ratio) < 5e-3, '%.4f vs %.4f' % (gratio, ratio))

# --- 5. index tone per session -------------------------------------------
for day in DAYS:
    t = RI.tone(day)
    lab = {1.0: 'RISK ON', 0.5: 'mild RISK ON',
           -1.0: 'RISK OFF', -0.5: 'mild RISK OFF'}.get(t[1])
    if lab:
        check('%s tone %s on page' % (day, lab), lab in h, lab)

# --- 6. the window, the title, and the stale-dek trap (F-168 / F-171) ----
check('window named in prose (F-168)',
      '26&ndash;30 October 2026' in h or '26-30 October 2026' in h)
check('eyebrow dated this Saturday',
      'Saturday 31 Oct 2026' in h)
title = re.search(r'<title>(.*?)</title>', h)
check('title is this edition, not inherited (F-171)',
      bool(title) and title.group(1) != 'The Week The Hedge Paid',
      title.group(1) if title else 'NO TITLE')
for stale in ('14&ndash;18 September', '19&ndash;23 Oct', '20 Oct', '24 Oct'):
    check('no stale window text: %s' % stale, stale not in h)

# --- 7. LD-4 ---------------------------------------------------------------
low = h.lower()
check('LD-4 no money path',
      not any(w in low for w in ('stop loss', 'take profit', 'lot size',
                                 'position size', 'entry at', 'risk per trade')))

# --- 8. markup -------------------------------------------------------------
for t in ('div', 'section', 'table', 'tr', 'td', 'p'):
    a = len(re.findall('<%s[ >]' % t, h))
    b = h.count('</%s>' % t)
    check('<%s> balanced' % t, a == b, '%d/%d' % (a, b))

css = re.search(r'<style>(.*?)</style>', h, re.S).group(1)
used = set()
for m in re.finditer(r'class="([^"]+)"', h):
    used.update(m.group(1).split())
defined = set(re.findall(r'\.([A-Za-z][\w-]*)', css))
check('no undefined CSS classes', used <= defined,
      ' '.join(sorted(used - defined)))

print('RETRO CHECK  26-30 Oct')
for n, d in oks:
    print('  PASS  %s %s' % (n, ('(%s)' % d) if d else ''))
for n, d in fails:
    print('  FAIL  %s %s' % (n, ('(%s)' % d) if d else ''))
print()
if fails:
    raise SystemExit('*** %d CHECK(S) FAILED - do not publish' % len(fails))
print('all %d checks passed' % len(oks))
