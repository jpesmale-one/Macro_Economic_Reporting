# -*- coding: utf-8 -*-
"""Regenerate section 4 - every indicator with its working - from live data.

*** WHY THIS IS NEEDED AND WHY IT IS NOT A HAND-TYPED TABLE. gen_page.py
emits sections 1, 2, 3 and 5 but NOT 4, so a page assembled from its body
alone silently loses the evidence table that F-134 checks against. F-134
caught exactly that: 44 whitelist values absent from the published page.

Every cell here is read from score_model.ROWS at build time - the same
source the guards read - so the table cannot drift from what R-44, R-45 and
R-48 verify. Nothing is typed.

The category order and weights come from fact_tables.WEIGHT, so if a weight
changes the headings follow it rather than describing the old one (F-122's
lesson applied to structure instead of prose).
"""
import io
import os
import sys

REPO = 'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting'
sys.path.insert(0, os.path.join(REPO, 'pipelines'))
os.chdir(REPO)

import score_model as sm
import fact_tables as ft

SP = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
      'c--Users-jpesm-OneDrive-Documents-GitHub/'
      '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/')

ISO2CCY = dict(sm.LABEL)          # 'US' -> 'USD'
ORDER = ('Production', 'Spending', 'Trade', 'Employment', 'Inflation',
         'Interest_Rate')

ESC = ((u'&', u'&amp;'), (u'<', u'&lt;'), (u'>', u'&gt;'))


def esc(x):
    s = u'%s' % (x if x is not None else u'')
    for a, b in ESC:
        s = s.replace(a, b)
    return s


def cls(score):
    if score is None:
        return 'zero', '&mdash;'
    if score > 0:
        return 'pos', '+%d' % score
    if score < 0:
        return 'neg', '%d' % score
    return 'zero', '0'


o = []
A = o.append

A('<section>')
A('  <h2>&sect;4 Every indicator, with its working</h2>')
A('  <p class="sub">%d rows &mdash; the evidence behind every category '
  'score.</p>' % len(sm.ROWS))
A('')
A('  <p><strong>Read a row left to right:</strong> the <em>actual</em> is '
  'measured against the <em>threshold</em>, which gives the <strong>score'
  '</strong>. The category total is the mean of its rows, times the '
  'category weight.</p>')
A('')
A('  <div class="note"><strong>A Ref ending in (Q) is a QUARTERLY '
  'series.</strong> NZD publishes Unemployment and Inflation quarterly, so '
  'those rows move once a quarter and are current between prints.</div>')
A('  <div class="note flag">')
A('    <span class="lbl">&#9888; DIRECTION OF GOODNESS IS NOT UNIFORM</span>')
A('    <strong>Unemployment and claimant counts score +1 when they FALL'
  '</strong> &mdash; they reach the currency through the economy. '
  '<strong>Inflation scores on a corridor, not a direction</strong> '
  '(LD-155), and <strong>the policy rate scores its PATH, not its level'
  '</strong> (LD-166). The threshold column states which rule applies to '
  'each row.</div>')

for cat in ORDER:
    rows = [r for r in sm.ROWS if r[0] == cat]
    if not rows:
        continue
    w = ft.WEIGHT.get(cat, 1)
    role = 'LEADING' if cat in ft.LEADING else 'CONFIRMING'
    good = sum(1 for r in rows if r[7] == 'GOOD')
    bad = sum(1 for r in rows if r[7] == 'BAD')
    neu = len(rows) - good - bad
    A('')
    A('  <h3>%s <span class="wt">weight %d &middot; %s</span></h3>'
      % (cat.replace('_', ' '), w, role))
    A('  <p class="cnt">%d rows &mdash; %d good &middot; %d neutral '
      '&middot; %d bad</p>' % (len(rows), good, neu, bad))
    A('  <div class="scroll">')
    A('  <table class="ind">')
    A('    <thead><tr><th>CCY</th><th>Indicator</th>'
      '<th class="num">Actual</th><th class="num">Previous</th>'
      '<th>Ref</th><th>Threshold</th><th class="num">Score</th></tr></thead>')
    A('    <tbody>')
    for c, iso, name, act, prev, ref, thr, v in sorted(
            rows, key=lambda r: (ISO2CCY.get(r[1], r[1]), r[2])):
        sc = sm.graded_signed(act, prev, thr, v)
        k, txt = cls(None if sc is None else
                     (1 if sc > 0 else (-1 if sc < 0 else 0)))
        A('      <tr class="grp">')
        A('        <td class="ccy">%s</td>' % esc(ISO2CCY.get(iso, iso)))
        A('        <td>%s</td>' % esc(name))
        A('        <td class="num v">%s</td>' % esc(act))
        A('        <td class="num v dim">%s</td>' % esc(prev))
        A('        <td class="dim sm">%s</td>' % esc(ref))
        A('        <td class="dim sm">%s</td>' % esc(thr))
        A('        <td class="num %s">%s</td>' % (k, txt))
        A('      </tr>')
    A('    </tbody>')
    A('  </table>')
    A('  </div>')

A('</section>')

io.open(SP + 's4.html', 'w', encoding='utf-8', newline='\n').write(
    '\n'.join(o) + '\n')
print('s4.html: %d lines, %d rows' % (len(o), len(sm.ROWS)))
counts = {}
for r in sm.ROWS:
    counts[r[0]] = counts.get(r[0], 0) + 1
for cat in ORDER:
    if cat in counts:
        print('  %-14s %2d rows' % (cat, counts[cat]))
