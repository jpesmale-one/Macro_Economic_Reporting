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
A('  <h2>§4 Every indicator, with its working</h2>')
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

# *** JEFF, 2026-10-25: "the interest rate category in macro report is
# missing. why is that?" HE IS RIGHT, AND THE CAUSE IS A SPLIT SOURCE.
# Interest_Rate IS in the board math - it carries weight 1 and CAD, GBP and
# NZD each score +1.00 from it - but its rows live in rate_model, NOT in
# score_model.ROWS, so a section built from ROWS alone shows five categories
# out of six. The scores were right; the EVIDENCE for one of them was
# invisible, which is exactly what section 4 exists to prevent.
#
# AND THE COLUMNS HAVE TO DIFFER, because LD-166 scores something different.
# The other five categories test an ACTUAL against a THRESHOLD. The rate row
# scores the PATH - where the policy rate is going - so "actual vs
# threshold" would misdescribe it. Jeff, on LD-166: "for IR our concern is
# the change not on a particular target." The table therefore shows the
# rate, the expected next move, and where that expectation came from.
import rate_model as _rm
_rr = _rm.compute()
_w = ft.WEIGHT.get('Interest_Rate', 1)
_role = 'LEADING' if 'Interest_Rate' in ft.LEADING else 'CONFIRMING'
_g = sum(1 for d in _rr.values() if d['score'] > 0)
_b = sum(1 for d in _rr.values() if d['score'] < 0)
A('')
A('  <h3>Interest Rate <span class="wt">weight %d &middot; %s</span></h3>'
  % (_w, _role))
A('  <p class="cnt">%d rows &mdash; %d good &middot; %d neutral &middot; '
  '%d bad</p>' % (len(_rr), _g, len(_rr) - _g - _b, _b))
A('  <div class="note"><strong>This category scores the PATH, not the '
  'level</strong> (LD-166). A hike already delivered and fully priced scores '
  'nothing; what scores is the move the market expects NEXT. That is why '
  'AUD sits at 0 after four hikes this year, while CAD and GBP score +1 on '
  'holds &mdash; a hike is expected ahead of them.</div>')
A('  <div class="scroll">')
A('  <table class="ind">')
A('    <thead><tr><th>CCY</th><th>Decision</th><th class="num">Rate</th>'
  '<th>Expected next</th><th>Source</th><th class="num">Score</th>'
  '</tr></thead>')
A('    <tbody>')
for _iso in sorted(_rr, key=lambda i: (-_rr[i]['score'],
                                       _rm.LABEL.get(i, i))):
    _d = _rr[_iso]
    _k, _t = cls(int(_d['score']) if _d['score'] == int(_d['score'])
                 else _d['score'])
    _pw = (_d.get('path_why') or '').replace('BEFORE - ', '').replace(
        'AFTER - ', '')
    A('      <tr class="grp">')
    A('        <td class="ccy">%s</td>' % esc(_rm.LABEL.get(_iso, _iso)))
    A('        <td>%s</td>' % esc(_d.get('note') or ''))
    A('        <td class="num v">%s</td>' % esc(_d['rate']))
    A('        <td class="dim sm">%s</td>' % esc(_pw))
    A('        <td class="dim sm">%s</td>' % esc(_d.get('path_src') or ''))
    A('        <td class="num %s">%s</td>' % (_k, _t))
    A('      </tr>')
A('    </tbody>')
A('  </table>')
A('  </div>')

A('</section>')

# *** JEFF, 2026-10-26: "can you bring back the reconciliation table in
# section 4?" - AND HE IS RIGHT THAT I SHOULD NOT HAVE DROPPED IT.
# The 18 Oct page carried SEVEN tables in section 4: six category tables
# plus a RECONCILIATION that sums every category cell to the base score.
# When I rebuilt the section from score_model.ROWS I reproduced the six and
# lost the seventh, because ROWS has no concept of a category TOTAL.
#
# *** AND IT IS THE MOST AUDITABLE TABLE ON THE PAGE. The category tables
# show rows; this one shows that the rows ADD UP to the number the board
# publishes. Without it a reader can check every indicator and still not
# verify that section 2's base score follows from them.
#
# Computed from fact_tables.base_scores, which is what the board itself
# reads - so the row sums cannot disagree with section 2 by construction.
_bs = ft.base_scores()
_CATS = ('Production', 'Spending', 'Trade', 'Employment', 'Inflation',
         'Interest_Rate')
A('')
A('  <h3>Reconciliation</h3>')
A('  <p class="cnt">Every category score, summed to the board.</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>CCY</th>%s<th class="num">Base</th></tr></thead>'
  % ''.join('<th class="num">%s</th>' % c[:5] for c in _CATS))
A('    <tbody>')
for _c in sorted(_bs, key=lambda x: -_bs[x]['total']):
    _cells = []
    for _cat in _CATS:
        _v = _bs[_c]['cats'].get(_cat)
        _k, _ = cls(None if _v is None else
                    (1 if _v > 0 else (-1 if _v < 0 else 0)))
        _cells.append('<td class="num %s">%+.2f</td>'
                      % (_k, _v if _v is not None else 0.0))
    _t = _bs[_c]['total']
    _tk, _ = cls(1 if _t > 0 else (-1 if _t < 0 else 0))
    A('      <tr><td class="ccy">%s</td>%s'
      '<td class="num %s tot">%+.2f</td></tr>'
      % (_c, ''.join(_cells), _tk, _t))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('  <p><strong>Weights: leading &times; 2, confirming &times; 1.</strong> '
  'The %d category cells in each row sum to that currency&rsquo;s base '
  'score, and the base plus the calibrator is the FINAL in &sect;2.</p>'
  % len(_CATS))
A('  <div class="note">')
A('    <strong>Every cell above is the ACTUAL AS PUBLISHED, and the score '
  'beside it is DERIVED from it</strong> &mdash; so this table can be '
  'audited against the source without trusting a verdict anyone typed. '
  '<strong>Until 2026-09-09 the fact tables stored the verdict while the '
  'actual lived elsewhere</strong>, which is what produced F-91, F-94 and '
  'F-95: one release written into two places, with nothing keeping them in '
  'step. Storing the actual once removed that class of bug rather than '
  'guarding against it (LD-112).')
A('  </div>')

# *** F-172 - EVERY WEIGHTED CATEGORY MUST APPEAR, OR THIS FAILS LOUD.
# Jeff found Interest Rate missing from the published page by reading it.
# The category was in the board math the whole time - only its evidence was
# absent, because its rows live in rate_model rather than score_model.ROWS.
# A section that silently shows five of six categories is the same shape as
# every false green in this project: output that looks complete.
# fact_tables.WEIGHT is the authority on what counts, so compare against it.
_html = chr(10).join(o)
# *** AND MY FIRST VERSION OF THIS GUARD DID NOT FIRE EITHER - the same
# mistake I had just made on the <title> check (F-171). A bare substring
# test passed because the explanatory NOTE mentions "Interest Rate" in
# prose. Anchor on the <h3> HEADING, which only a real section emits.
_missing = [c for c in ft.WEIGHT
            if ('<h3>%s <span' % c.replace('_', ' ')) not in _html]

# *** F-173 - AND THE RECONCILIATION TABLE MUST BE HERE TOO.
# Jeff: "can you bring back the reconciliation table in section 4?" - I had
# dropped it when rebuilding the section, and F-172 did not catch it because
# F-172 only counts CATEGORIES. A guard that checks one kind of omission
# says nothing about another.
# This is the table that proves the category rows SUM to the published base
# score, so its absence is the difference between a reader being able to
# audit the board and merely being able to read it.
if '<h3>Reconciliation</h3>' not in _html:
    raise SystemExit('*** SECTION 4 HAS NO RECONCILIATION TABLE - the '
                     'category rows must be shown to sum to the base score '
                     '(F-173)')
if _missing:
    raise SystemExit('*** SECTION 4 IS MISSING A WEIGHTED CATEGORY: %s - '
                     'the board scores it, so the evidence must show it '
                     '(F-172)' % ', '.join(sorted(_missing)))

io.open(SP + 's4.html', 'w', encoding='utf-8', newline='\n').write(
    '\n'.join(o) + '\n')
print('s4.html: %d lines, %d rows' % (len(o), len(sm.ROWS)))
counts = {}
for r in sm.ROWS:
    counts[r[0]] = counts.get(r[0], 0) + 1
for cat in ORDER:
    if cat in counts:
        print('  %-14s %2d rows' % (cat, counts[cat]))
