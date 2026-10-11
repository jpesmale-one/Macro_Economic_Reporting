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
# F-105: THIS WAS A HARDCODED SIX AND GDP NEVER APPEARED.
# LD-113 added the GDP category to fact_tables.WEIGHT on 2026-09-09; this
# page kept iterating its own frozen tuple, so the board totals it printed
# INCLUDED GDP while the per-category working it showed DID NOT - the page
# could not be reconciled against itself.
# Derive from the weight table, the one authority on which categories exist.
CATS = tuple(sorted(ft.WEIGHT, key=lambda c: (c in ft.CONFIRMING, c)))
ORDER = ('CHF', 'EUR', 'GBP', 'AUD', 'CAD', 'USD', 'JPY', 'NZD')
ISO = {'USD': 'US', 'EUR': 'EA', 'GBP': 'GB', 'JPY': 'JP',
       'AUD': 'AU', 'NZD': 'NZ', 'CAD': 'CA', 'CHF': 'CH'}

VALS = {}
for cat, iso, name, a, p, ref, thr, v in sm.ROWS:
    VALS[(sm.LABEL[iso], name)] = dict(actual=a, prev=p, ref=ref,
                                       thr=thr, verdict=v)

# GDP has no score_model.ROWS entry - its actual lives in the fact table
# (LD-112/LD-113), so its detail is joined from there instead. Without this
# the eight GDP rows render with every value blank.
# LD-117: GDP LEFT THE BASE on 2026-09-10 and is now a CALIBRATOR row, so it
# has no fact-table CSV to join here. The join that used to sit at this line
# was added on 2026-09-09 when GDP was briefly a base category (LD-113) and
# is removed with it - the GDP evidence now belongs in the calibrator section,
# where the consensus-forecast RANGE is the whole input (Jeff: "we're trading
# the expectations not the result").

import derive_scores as _derive

RATE = rate_model.compute()
CELL = {'1': ('pos', '+1'), '-1': ('neg', '\u22121'), '0': ('zero', '0')}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rate_detail(ccy):
    """A rate row's evidence, with EVERY term that produced its score.

    F-99: the table showed rate, CPI and mandate only - so after LD-107 both
    USD and JPY scored +1 ENTIRELY on the expected-path term and the row
    gave no hint why. Two of eight rows were unauditable, which is the exact
    failure this section exists to prevent.
    """
    d = RATE[ISO[ccy]]
    lo, hi = d['mandate']
    band = ('%g–%g%%' % (lo, hi)) if lo != hi else ('%g%%' % lo)
    arrow = 'rising' if d['rising'] else 'falling'
    bits = []
    if d['realised']:
        bits.append('realised %+.2f' % d['realised'])
    if d['expected']:
        bits.append('expected %+.2f' % d['expected'])
    if d['surprise'] is not None:
        bits.append('surprise %+.2f' % d['surprise'])
    if d['path'] is not None:
        # *** F-148 - path_bp IS NOW ALWAYS None. LD-154 replaced
        # path_score's forecast-minus-current basis-point test with
        # decision_score, which reports a SOURCE ('consensus' / 'forecast' /
        # 'actual') rather than a bp distance, and set bp = None. This line
        # still formatted it with %d and crashed the whole section-4 build on
        # the first edition after LD-154 landed. A rule change that leaves a
        # renderer reading a retired field is the F-135 shape; name the source
        # instead, which is the thing LD-154 actually produces.
        src = d.get('path_src')
        if d.get('path_bp') is not None:
            bits.append('path %+.2f (%+dbp)' % (d['path'], d['path_bp']))
        else:
            bits.append('path %+.2f (%s)' % (d['path'], src or 'LD-154'))
    # LD-109: name the weight each live term carried, renormalised
    w = d.get('weights', {})
    tot = sum(w.values()) or 1.0
    wtxt = ' · '.join('%s %.0f%%' % (k, w[k] / tot * 100)
                          for k in ('realised', 'expected', 'surprise',
                                    'path') if k in w)
    why = d['why']
    if d['path'] is not None:
        why += ' · ' + d['path_why']
    return dict(actual=d['rate'], prev='CPI %.1f%%' % d['cpi'],
                ref=arrow, thr='mandate ' + band, verdict=why,
                terms=' + '.join(bits) or 'all terms zero',
                weights=wtxt, raw=d['score'])


out = []
A = out.append

A('<section>')
A('  <h2>\u00a74 Every indicator, with its working</h2>')
# F-105b: hardcoded, and stale the moment GDP landed - this said 78 rows
# while rendering 85. A count in prose is a figure; figures are derived.
A('  <p class="sub">%d rows \u2014 the evidence behind all %d category '
  'scores.</p>' % (sum(len(ft.load(c)) for c in CATS), len(CATS) * 8))
A('')
A('  <p><strong>Read a row left to right:</strong> the <em>actual</em> is '
  'measured against the <em>threshold</em>, which gives the binary '
  '<strong>+1 / 0 / \u22121</strong>. A category score is the <strong>mean of '
  'that currency\'s rows in it, times the category weight</strong>.</p>')
A('')
A('  <div class="note"><strong>A Ref ending in (Q) is a QUARTERLY series.</strong> '
  'NZD publishes Unemployment and Inflation quarterly, so those rows sit two '
  'months behind the monthly ones around them — <strong>that is the cadence, '
  'not a stale row</strong>.</div>')
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

    # F-111: this counted raw cells against '1'/'0'/'-1'. Since LD-112 the
    # cell holds an ACTUAL, so every bucket was empty and each category
    # reported "0 good \u00b7 0 neutral \u00b7 0 bad" under a table of real scores.
    tally = collections.Counter()
    for r in rows:
        _v = _derive.score_row(cat, r['Currency'].strip(),
                               r['Indicator'].strip(),
                               (r.get(MONTH) or '').strip())
        if _v is None:
            tally['none'] += 1
        else:
            tally['good' if _v > 0 else 'bad' if _v < 0 else 'neutral'] += 1
    summary = '%d rows \u2014 %d good \u00b7 %d neutral \u00b7 %d bad' % (
        len(rows), tally['good'], tally['neutral'], tally['bad'])

    A('')
    A('  <h3>%s <span class="wt">weight %d \u00b7 %s</span></h3>' % (label, w, lead))
    A('  <p class="cnt">%s</p>' % summary)
    A('  <div class="scroll">')
    A('  <table class="ind">')
    if cat == 'Interest_Rate':
        # F-99: the rate rows are scored from four TERMS, not from an
        # actual against a threshold. Show the terms, or the score cannot
        # be audited - USD and JPY score +1 purely on the path.
        A('    <thead><tr><th>CCY</th><th>Bank</th><th class="num">Rate</th>'
          '<th class="num">CPI</th><th>CPI trend</th>'
          '<th>Terms averaged</th><th class="num">Raw</th>'
          '<th class="num">Cell</th><th class="num">Category</th>'
          '</tr></thead>')
    else:
        A('    <thead><tr><th>CCY</th><th>Indicator</th>'
          '<th class="num">Actual</th>'
          '<th class="num">Previous</th><th>Ref</th><th>Threshold</th>'
          '<th class="num">Score</th><th class="num">Category</th>'
          '</tr></thead>')
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
            # F-111: the CSV holds an ACTUAL since LD-112, not a verdict, so
            # CELL.get('54.6') missed on EVERY row and the whole Score column
            # rendered as em-dashes - 107 of them - while the category totals
            # beside it stayed correct. Derive the score the same way
            # fact_tables does.
            _sc = _derive.score_row(cat, ccy, nm, cell)
            k, txt = CELL.get('' if _sc is None else str(int(round(_sc)))
                              if float(_sc).is_integer() else '',
                              ('dash', '—'))
            if _sc is not None and not float(_sc).is_integer():
                k, txt = ('pos' if _sc > 0 else 'neg' if _sc < 0 else 'zero',
                          '%+.2f' % _sc)
            v = (rate_detail(ccy) if cat == 'Interest_Rate'
                 else VALS.get((ccy, nm), {}))
            first = i == 0
            A('      <tr%s>' % (' class="grp"' if first else ''))
            A('        <td class="ccy">%s</td>' % (ccy if first else ''))
            A('        <td>%s</td>' % esc(nm))
            A('        <td class="num v">%s</td>' % esc(v.get('actual', '—')))
            A('        <td class="num v dim">%s</td>'
              % esc(v.get('prev', '—')))
            _ref = v.get('ref', '—')
            # LD-106: a REF ending in '(Q)' is a QUARTERLY series, so an
            # old-looking month is its cadence and not a stale row.
            _q = _ref.endswith('(Q)')
            A('        <td class="dim sm%s"%s>%s</td>'
              % (' q' if _q else '',
                 ' title="Quarterly series - this is its cadence, not a'
                 ' stale row"' if _q else '', esc(_ref)))
            if cat == 'Interest_Rate':
                # F-99: show the terms that were averaged, and the RAW score
                # before it is flattened to +1/0/-1 - CHF's +0.25 and NZD's
                # +1.50 both render as '+1' in the cell.
                A('        <td class="sm terms">%s<br><span class="wt2">'
                  '%s</span></td>'
                  % (v.get('terms', ''), v.get('weights', '')))
                A('        <td class="num v">%+.2f</td>' % v.get('raw', 0.0))
            else:
                A('        <td class="dim sm">%s</td>'
                  % esc(v.get('thr', '—')))
            A('        <td class="num %s">%s</td>' % (k, txt))
            if first:
                A('        <td class="num %s tot" rowspan="%d">%+.2f</td>'
                  % (cls, len(rs), sc))
            A('      </tr>')
    A('    </tbody>')
    A('  </table>')
    A('  </div>')

    if cat == 'Interest_Rate':
        A('  <div class="note"><strong>The rate rows are scored from FOUR '
          'WEIGHTED TERMS, not from an actual against a threshold.</strong> '
          '<code>score = Σ(term × weight) / Σ(weight)</code> over the '
          'terms that exist — <strong>realised 20% · expected 30% · '
          'surprise 20% · path 30%</strong>. <strong>60% sits on the '
          'forward half</strong> (expected + path), which is the point of a '
          'model built to foresee a move rather than report one.</div>')
        A('  <div class="note">A missing term <strong>drops out and the '
          'weights renormalise</strong> — a currency between meetings has '
          'no surprise, one whose next meeting is beyond the calendar '
          'horizon has no path. It is not scored 0, which would assert '
          '“no surprise” when the truth is that we cannot see one. The '
          'second line of each Terms cell shows the weights actually '
          'used.</div>')

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
A('  <p><strong>Weights: leading \u00d7 2, confirming \u00d7 1.</strong> '
  'The %d category cells in each row sum to that currency\'s base '
  'score, and the base plus the calibrator is the FINAL in \u00a71.</p>'
  % len(CATS))
A('')
# THE OLD NOTE HERE DESCRIBED A GAP THAT IS NOW CLOSED. It read: 'A
# reader cannot audit those scores from the CSVs alone, because they
# record the verdict and not the evidence.' Jeff read that on 2026-09-09
# and fixed it the same day (LD-112). Leaving it up would advertise a
# defect the repo no longer has - the mirror of letting a real one go
# unrecorded, and just as misleading to the next reader.
A('  <div class="note">')
A('    <strong>Every cell above is the ACTUAL AS PUBLISHED, and the '
  'score beside it is DERIVED from it</strong> \u2014 so this table '
  'can be audited against the source without trusting a verdict anyone '
  'typed. <strong>Until 2026-09-09 the fact tables stored the verdict '
  'while the actual lived elsewhere</strong>, which is what produced '
  'F-91, F-94 and F-95: one release written into two places, with '
  'nothing keeping them in step. Storing the actual once removed that '
  'class of bug rather than guarding against it (LD-112).')
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
