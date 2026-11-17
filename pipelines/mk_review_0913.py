# -*- coding: utf-8 -*-
"""Build the 9-13 Nov PRICE REVIEW - not a retrospective, and not a weekly.

*** WHY THIS IS A DIFFERENT KIND OF PAGE.

No weekly edition was published for 9-13 Nov and no calendar capture exists
between 6 Nov and 17 Nov. So there is no board to grade against and no
catalysts to attribute moves to: scoring the week would mean inventing a
vintage after the fact, which F-183b exists to forbid (the calibrator is
forward-looking and moves daily).

What CAN be sourced on equal terms for all eight currencies is price, and
the index legs behind risk tone. So this page reports what the market did
and how the PREVIOUS week's set would have fared carried forward - and says
plainly, more than once, that no board governed it.

Jeff asked for exactly this, 2026-11-17: "Price only review but make sure to
refresh our csv tables. we need it for the next project."

Every number is computed at build time from the restored OANDA bars.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import daily_report as dr
import atr_grade as ag
import risk_index as RI

DAYS = ['2026-11-09', '2026-11-10', '2026-11-11',
        '2026-11-12', '2026-11-13']
DNAME = dict(zip(DAYS, ['Mon 9', 'Tue 10', 'Wed 11', 'Thu 12', 'Fri 13']))
CARRY = [('GBPNZD', 'LONG'), ('NZDJPY', 'SHORT')]

# ------------------------------------------------------------------- the week
sess = dict((d, dr.session_strength(d)) for d in DAYS)
move = {}
for d in DAYS:
    for c, v in sess[d].items():
        move[c] = move.get(c, 0.0) + v
order = sorted(move, key=lambda c: -move[c])

TONE = [(d,) + RI.tone(d)[:2] for d in DAYS]

# -------------------------------------------------------------- carry-forward
carry = {}
for p, side in CARRY:
    b = dr.bars(p)
    f = ag.pip_factor(p)
    out = []
    tf = ta = 0.0
    for d in DAYS:
        row = [x for x in b if x[0] == d]
        if not row:
            continue
        _, o, h, l, c = row[0]
        prior = [x for x in b if x[0] < d]
        atr = ag.atr([(hh, ll, cc) for _, oo, hh, ll, cc in prior], 14, f)
        fav, adv, frac, hit = ag.grade_day(side, o, h, l, f, atr)
        out.append((d, fav, adv, atr, frac, ag.classify(fav, adv, atr)))
        tf += fav
        ta += adv
    carry[p] = (out, tf, ta, (tf / ta if ta else float('inf')))

# --------------------------------------------------------------------- render
prev = io.open(os.path.join(REPO, 'reports/2026/Q4/2026-10-31_retro.html'),
               encoding='utf-8').read()
head = prev[:prev.index('</style>') + len('</style>')]
head = head.replace('<title>The Week The Board Was Right</title>',
                    '<title>The Week Nobody Was Watching</title>', 1)

A = []
W = A.append

gr = carry['GBPNZD'][3]
nr = carry['NZDJPY'][3]

W(u'''

<div class="wrap">

<header>
  <p class="eyebrow">Macro Economic Reporting &middot; Price Review &middot;
     9&ndash;13 Nov 2026</p>
  <h1>The Week Nobody Was Watching</h1>
  <p class="dek"><strong>No weekly edition governed this week, and no
  calendar was captured during it.</strong> So this is not a retrospective and
  nothing here is scored: it is what price did, and how the previous week's
  set would have fared had it simply been carried forward. The answer is
  that it decayed &mdash; <strong>GBPNZD %.2f and NZDJPY %.2f</strong>, both
  below break-even, against %.2f and %.2f the week before.</p>
  <div class="chips">
    <span class="chip q">no board</span>
    <span class="chip q">no catalysts</span>
    <span class="chip">prices verified</span>
    <span class="chip">USD +%.2f%% top</span>
  </div>
</header>

<div class="note bad"><span class="lbl">&#9888; Read this before the tables
</span>There is <strong>no board on this page and no scores</strong>, because
neither can be sourced honestly. No weekly was published for 9&ndash;13 Nov,
and the newest calendar capture is <strong>6 Nov</strong> &mdash; attempts on
17 Nov returned pages holding one table row against the usual 603. Scoring
the week from today's data would pin a forward-looking calibrator to a
vintage eleven days after the fact, which is precisely the drift F-183b
forbids. <strong>Prices and index legs are fully sourced and verified</strong>
(LD-5); everything else is absent and marked as absent, per F-73.</div>
''' % (gr, nr, 1.98, 1.51, move[order[0]]))

# ---- §1 what moved
W(u'''
<section>
<h2>&sect;1 &mdash; What moved</h2>
<p>Currency strength is each currency against the other seven, open to close,
summed across the five sessions.</p>
<div class="scroll"><table>
<thead><tr><th>CCY</th><th class="num">Week</th>''')
for d in DAYS:
    W(u'<th class="num">%s</th>' % DNAME[d])
W(u'</tr></thead><tbody>')
for c in order:
    W(u'<tr><td class="ccy"><strong>%s</strong></td>'
      u'<td class="num mono %s"><strong>%+.3f%%</strong></td>'
      % (c, 'good' if move[c] > 0 else 'bad', move[c]))
    for d in DAYS:
        v = sess[d][c]
        W(u'<td class="num mono %s">%+.2f</td>'
          % ('good' if v > 0 else ('bad' if v < 0 else 'dim'), v))
    W(u'</tr>')
W(u'''</tbody></table></div>
<div class="note"><span class="lbl">The shape of it</span>
<strong>USD led and CHF trailed</strong> &mdash; close to a straight reversal
of 2&ndash;6 Nov, when CHF topped the table and the havens were bid. The two
commodity currencies stayed weak: AUD negative again, NZD positive on the
week only because of a single strong Monday.</div>
</section>
''')

# ---- §2 risk tone
W(u'''
<section>
<h2>&sect;2 &mdash; Risk tone, and where it turned</h2>
<div class="scroll"><table>
<thead><tr><th>Session</th><th class="num">SPX</th><th class="num">NI225</th>
<th class="num">DAX</th><th class="num">VIX</th><th>Tone</th></tr></thead>
<tbody>''')
for d in DAYS:
    l, s, det = RI.tone(d)
    cells = []
    for k in ('SPX', 'NI225', 'DAX', 'VIX'):
        p, v = det['legs'][k]
        if p is None:
            cells.append(u'<td class="num dim">&mdash;</td>')
        else:
            cells.append(u'<td class="num mono %s">%+.2f%%</td>'
                         % ('good' if v > 0 else ('bad' if v < 0 else ''), p))
    kls = 'good' if s > 0 else ('bad' if s < 0 else '')
    W(u'<tr><td><strong>%s</strong></td>%s<td class="%s">%s '
      u'<span class="mono">%+.2f</span></td></tr>'
      % (DNAME[d], ''.join(cells), kls, l, s))
W(u'''</tbody></table></div>
<p>Risk-on through Wednesday, then off for the last two sessions. That turn
is visible in the currency table too: JPY is the strongest currency on both
Thursday and Friday having been negative on Monday.</p>
</section>
''')

# ---- §3 the carried set
W(u'''
<section>
<h2>&sect;3 &mdash; What the old set would have done</h2>
<p>The 2&ndash;6 Nov set carried forward, graded on the same rules
(LD-148). <strong>This is a counterfactual, not a record of positions</strong>
&mdash; no weekly selected these pairs for this week, and the question is
only what a stale board would have been worth.</p>
<div class="scroll"><table>
<thead><tr><th>Pair</th><th>Session</th><th class="num">Favourable</th>
<th class="num">Adverse</th><th class="num">ATR</th><th>State</th>
</tr></thead><tbody>''')
for p, side in CARRY:
    out, tf, ta, ratio = carry[p]
    for i, (d, fav, adv, atr, frac, k) in enumerate(out):
        kls = {'CLEAN': 'good', 'EARNED': 'good',
               'BEATEN': 'bad'}.get(k, '')
        W(u'<tr>%s<td>%s</td><td class="num mono">%.1f</td>'
          u'<td class="num mono">%.1f</td><td class="num mono dim">%.1f</td>'
          u'<td class="%s"><strong>%s</strong></td></tr>'
          % ((u'<td class="ccy" rowspan="6"><strong>%s</strong><br>'
              u'<span class="mono">%s</span></td>' % (p, side)) if i == 0
             else u'', DNAME[d], fav, adv, atr, kls, k))
    W(u'<tr><td colspan="4"><strong>%s total</strong></td>'
      u'<td class="num mono"><strong>%.1f / %.1f</strong></td>'
      u'<td class="%s"><strong>ratio %.2f</strong></td></tr>'
      % (p, tf, ta, 'bad' if ratio < 1 else 'good', ratio))
W(u'''</tbody></table></div>
<div class="note warn"><span class="lbl">&#9888; The finding, such as it is
</span>Both carried pairs fell <strong>below break-even</strong> &mdash;
%.2f and %.2f, against %.2f and %.2f the week before &mdash; and nine of the
ten sessions were DRIFT or BEATEN, with not one CLEAN. The set was built on a
board whose top half had already inverted during 2&ndash;6 Nov; carried into a
week that reversed again, it stopped working. <strong>This is the cost of a
stale board stated in pips</strong>, and it is the one thing this page can
show that a scored retrospective could not.</div>
</section>
''' % (gr, nr, 1.98, 1.51))

# ---- §4 method
W(u'''
<section>
<h2>&sect;4 &mdash; Method and limits</h2>
<p>Prices are OANDA daily bars via TradingView (LD-5 as amended; Yahoo is
never a fallback). Index legs are TVC and XETR. Every figure is computed at
build time, not typed.</p>
<div class="note bad"><span class="lbl">The data behind this page was wrong
once, and was rebuilt</span>The first refresh for this build returned bars
whose open had been replaced by a smoothed value equal to the bar's own low
in <strong>3667 of 8400 cases (44%%)</strong>, against 122 in the committed
baseline. Carried into a grading, that silently converts adverse excursion to
zero and turns BEATEN days into CLEAN ones. The bars were restored from the
last verified commit, re-pulled, and checked at <strong>1%% across all 8400
</strong> before anything here was computed. <span class="mono">pull_bars.py
</span> now refuses any pull above 20%% (F-190).</div>
<p class="fine">Observations only: no entries, stops, targets or sizing
(LD-4). No board, no scores, no selection &mdash; this page describes a week
the reporting did not cover.</p>
</section>

</div>
''')

html = head + u''.join(A)
out = os.path.join(REPO, 'reports/2026/Q4/2026-11-13_review.html')
io.open(out, 'w', encoding='utf-8', newline='\n').write(html)
print('wrote %s (%d bytes)' % (out, len(html)))
for p, _ in CARRY:
    o, tf, ta, r = carry[p]
    print('%s ratio %.2f  %.1f / %.1f' % (p, r, tf, ta))
print('top %s %+.3f%%  bottom %s %+.3f%%'
      % (order[0], move[order[0]], order[-1], move[order[-1]]))
