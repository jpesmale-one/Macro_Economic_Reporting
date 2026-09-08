# -*- coding: utf-8 -*-
"""2.1-2.6 rebuilt for AUDIT - every row with the values behind its score.

Jeff, 2026-09-09: "just reproduce the 2.1-2.6 like before I need to see if
we're following the logic correctly and if we're getting the right numbers"

So this shows the WORKING, not just the answer:

    ACTUAL vs THRESHOLD -> BINARY (+1/0/-1) -> category mean x weight

WHERE THE VALUES LIVE, AND WHY THAT IS A GAP. The fact tables store only the
derived +1/0/-1. The actual, previous, reference month and threshold sit in
score_model.ROWS (70 rows) and rate_model.ROWS (8 rate decisions). A reader
cannot audit a score from the CSVs alone - the CSVs record the VERDICT and
not the EVIDENCE.

That is worth fixing in the tables themselves. Until then this joins the two
so the arithmetic is checkable end to end.
"""
import io, os, sys, csv, glob, collections

os.chdir(r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting')
sys.path.insert(0, os.path.join(os.getcwd(), 'pipelines'))
NL = chr(10)
import fact_tables as ft
import score_model as sm
import rate_model

MONTH = ft.latest_month()
CATS = ('Production', 'Spending', 'Trade',
        'Employment', 'Inflation', 'Interest_Rate')
ORDER = ('CHF', 'EUR', 'GBP', 'AUD', 'CAD', 'USD', 'JPY', 'NZD')
ISO = {'USD': 'US', 'EUR': 'EA', 'GBP': 'GB', 'JPY': 'JP',
       'AUD': 'AU', 'NZD': 'NZ', 'CAD': 'CA', 'CHF': 'CH'}

VALS = {}
for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
    VALS[(sm.LABEL[iso], name)] = dict(actual=a, prev=p, ref=ref,
                                       thr=thr, verdict=v)

RATE = rate_model.compute()
CELL = {'1': ('pos', '+1'), '-1': ('neg', '\u22121'), '0': ('zero', '0')}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rate_detail(ccy):
    d = RATE[ISO[ccy]]
    lo, hi = d['mandate']
    band = ('%g\u2013%g%%' % (lo, hi)) if lo != hi else ('%g%%' % lo)
    arrow = 'rising' if d['rising'] else 'falling'
    return dict(actual=d['rate'], prev='CPI %.1f%%' % d['cpi'],
                ref=arrow, thr='mandate ' + band, verdict=d['why'])


out = []
A = out.append

A('<section>')
A('  <h2>\u00a75 Every indicator, with its working</h2>')
A('  <p class="sub">78 rows \u2014 the evidence behind all 48 category scores.</p>')
A('')
A('  <p><strong>Read a row left to right:</strong> the <em>actual</em> is '
  'measured against the <em>threshold</em>, which gives the binary '
  '<strong>+1 / 0 / \u22121</strong>. A category score is the <strong>mean of '
  'that currency\'s rows in it, times the category weight</strong>.</p>')
A('')
A('  <div class="note flag">')
A('    <span class="lbl">\u26a0 DIRECTION OF GOODNESS IS NOT UNIFORM</span>')
A('    <strong>Unemployment and claimant counts score +1 when they FALL</strong> '
  '\u2014 they reach the currency through the economy. <strong>Inflation scores '
  '+1 when it RISES</strong> \u2014 it reaches the currency through the central '
  'bank, and stops helping only past that bank\'s own ceiling. The two look '
  'alike in plain language and carry opposite signs, which is what to check '
  'first on any row that looks wrong.')
A('  </div>')

for cat in CATS:
    rows = ft.load(cat)
    by = collections.defaultdict(list)
    for r in rows:
        by[r['Currency'].strip()].append(r)
    w = ft.WEIGHT[cat]
    lead = 'LEADING' if cat in ft.LEADING else 'confirming'
    label = cat.replace('_', ' ')

    tally = collections.Counter()
    for r in rows:
        tally[(r.get(MONTH) or '').strip()] += 1
    summary = '%d rows \u2014 %d good \u00b7 %d neutral \u00b7 %d bad' % (
        len(rows), tally['1'], tally['0'], tally['-1'])

    A('')
    A('  <h3>%s <span class="wt">weight %d \u00b7 %s</span></h3>' % (label, w, lead))
    A('  <p class="cnt">%s</p>' % summary)
    A('  <div class="scroll">')
    A('  <table class="ind">')
    A('    <thead><tr><th>CCY</th><th>Indicator</th><th class="num">Actual</th>'
      '<th class="num">Previous</th><th>Ref</th><th>Threshold</th>'
      '<th class="num">Score</th><th class="num">Category</th></tr></thead>')
    A('    <tbody>')
    for ccy in ORDER:
        rs = by.get(ccy, [])
        if not rs:
            continue
        sc, n, tot = ft.category_score(cat, ccy, MONTH)
        cls = 'pos' if sc > 0 else ('neg' if sc < 0 else 'zero')
        for i, r in enumerate(rs):
            nm = r['Indicator'].strip()
            cell = (r.get(MONTH) or '').strip()
            k, txt = CELL.get(cell, ('dash', '\u2014'))
            v = (rate_detail(ccy) if cat == 'Interest_Rate'
                 else VALS.get((ccy, nm), {}))
            first = i == 0
            A('      <tr%s>' % (' class="grp"' if first else ''))
            A('        <td class="ccy">%s</td>' % (ccy if first else ''))
            A('        <td>%s</td>' % esc(nm))
            A('        <td class="num v">%s</td>' % esc(v.get('actual', '\u2014')))
            A('        <td class="num v dim">%s</td>' % esc(v.get('prev', '\u2014')))
            A('        <td class="dim sm">%s</td>' % esc(v.get('ref', '\u2014')))
            A('        <td class="dim sm">%s</td>' % esc(v.get('thr', '\u2014')))
            A('        <td class="num %s">%s</td>' % (k, txt))
            if first:
                A('        <td class="num %s tot" rowspan="%d">%+.2f</td>'
                  % (cls, len(rs), sc))
            A('      </tr>')
    A('    </tbody>')
    A('  </table>')
    A('  </div>')

    if cat == 'Interest_Rate':
        A('  <div class="note"><strong>The rate rows read differently.</strong> '
          '<em>Actual</em> is the policy rate, <em>previous</em> the CPI it is '
          'judged against, and <em>threshold</em> that bank\'s own mandate '
          '\u2014 <strong>not a common 2%</strong>. The SNB targets '
          '<strong>0\u20132%</strong>, so CHF at 0.8% and rising sits INSIDE its '
          'band; the RBNZ targets 1\u20133%, so NZD at 4.1% is above its ceiling '
          'and rising, which is why it scores highest.</div>')

A('')
A('  <h3>Reconciliation</h3>')
A('  <p class="cnt">Every category score, summed to the board.</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>CCY</th>'
  + ''.join('<th class="num">%s</th>' % c.replace('_', ' ')[:5] for c in CATS)
  + '<th class="num">Base</th></tr></thead>')
A('    <tbody>')
b = ft.base_scores(MONTH)
for ccy in ORDER:
    cells = []
    for cat in CATS:
        v = b[ccy]['cats'][cat]
        k = 'pos' if v > 0 else ('neg' if v < 0 else 'zero')
        cells.append('<td class="num %s">%+.2f</td>' % (k, v))
    t = b[ccy]['total']
    k = 'pos' if t > 0 else ('neg' if t < 0 else 'zero')
    A('      <tr><td class="ccy">%s</td>%s<td class="num %s tot">%+.2f</td></tr>'
      % (ccy, ''.join(cells), k, t))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('  <p><strong>Weights: Production, Spending and Trade \u00d7 2; Employment, '
  'Inflation and Interest Rate \u00d7 1.</strong> The six category cells in each '
  'row sum to that currency\'s base score, and the base plus the calibrator '
  'is the FINAL in \u00a71.</p>')
A('')
A('  <div class="note flag">')
A('    <span class="lbl">\u26a0 A GAP WORTH FIXING</span>')
A('    <strong>The fact tables store only the \u22121 / 0 / +1</strong> \u2014 the '
  'actual, previous, reference and threshold columns above are joined in '
  'from <code>score_model.py</code> and <code>rate_model.py</code>. '
  '<strong>A reader cannot audit a score from the CSVs alone</strong>, '
  'because they record the verdict and not the evidence. The tables should '
  'carry the values beside the score.')
A('  </div>')
A('</section>')

p = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
     'c--Users-jpesm-OneDrive-Documents-GitHub/'
     '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/indicators.html')
io.open(p, 'w', encoding='utf-8', newline=NL).write(NL.join(out))
print('wrote %d lines' % len(out))
miss = [(c, n) for (c, n) in [(r['Currency'].strip(), r['Indicator'].strip())
        for cat in CATS if cat != 'Interest_Rate' for r in ft.load(cat)]
        if (c, n) not in VALS]
print('rows with no joined values: %d %s' % (len(miss), miss or ''))
