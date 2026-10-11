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


def _sched_note():
    """F-152 - NAME THE SCHEDULED PRINTS, so this table is not read as the
    whole story.

    Jeff, 2026-10-11, reading EUR at 3.2% against Aug/26: "WE already have a
    forecast for the September Inflation can you check?"

    He was right, and the table gave him no way to see it. The 3.8% consensus
    for Fri 16 Oct IS scored - in the CALIBRATOR, before-the-news - but a
    reader of THIS table sees only "actual" under Scored from and reasonably
    concludes nothing newer is known. The footnote described the calibrator in
    the abstract; it never said a print for one of these very rows was hours
    away.

    THE LEVEL AND THE EXPECTATION CAN DISAGREE, which is the real reason this
    belongs on the page. Both read +1 for EUR this week, so nothing moved -
    but a currency at 2.4% with a 2.0% consensus scores +1 on the level and 0
    on the expectation, and only the calibrator would notice.

    Degrades to '' on any failure: a footnote is not worth failing a build.
    """
    # *** READ THE EDITION'S WINDOW, DO NOT RECOMPUTE IT. The first cut used
    # date.today() - weekday(), which on a SUNDAY build returns the week just
    # ENDED (5-9 Oct) instead of the one being published (12-16 Oct), and the
    # footnote silently rendered empty. build_check.week() already owns this
    # rule and gets it right (the F-140 fix: Sunday build -> tomorrow); a
    # third copy of a date rule is how F-140 happened in the first place.
    try:
        import build_check as _bc
        import calibrator as _cb
        _caps = sorted(glob.glob('data/raw/calendar/*_cal_full.json'))
        if not _caps:
            return ''
        _s, _e = _bc.window()
        _rows = _cb.week_rows(_caps[-1], _s, _e)
        _names = _cb.INFLATION_NAMES
    except Exception:
        return ''
    _bits = []
    for r in sorted([x for x in _rows if x.get('name') in _names],
                    key=lambda x: x['when']):
        _c = (r.get('cons') or '').strip()
        _f = (r.get('fcst') or '').strip()
        _e, _w = (_c, 'consensus') if _c else (_f, 'forecast')
        if not _e:
            continue
        _bits.append('<strong>%s %s &rarr; %s</strong> (%s, %s, scores %+d)'
                     % (esc(r['ccy']), esc((r.get('prev') or '?').strip()),
                        esc(_e), esc(r['when'].strftime('%a %d %H:%M')), _w,
                        r.get('score') or 0))
    if not _bits:
        return ''
    return ('<br><br><strong>AND A PRINT IS SCHEDULED THIS WEEK FOR %d OF '
            'THESE ROWS.</strong> %s. Those expectations are scored in the '
            'week-ahead table, not here &mdash; this table reports the LAST '
            'print, which is the standing state until the next one lands. '
            'Where the level and the expectation disagree, the calibrator '
            'carries the forward read.'
            % (len(_bits), '; '.join(_bits)))


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rate_detail(ccy):
    """(level, level_why, path, path_why, raw) for the Interest Rate row.

    LD-163 left TWO terms, equally weighted:
        level 0.50   where the rate sits vs the 1.5-2.5 corridor (LD-142)
        path  0.50   what the next decision is expected to do (LD-154)

    F-99's lesson still holds - a rate row is scored from TERMS, not from an
    actual against a threshold, so the terms have to be on the row or the
    score cannot be audited. What changed is WHICH terms, and the old
    renderer never caught up.
    """
    d = RATE[ISO[ccy]]
    lvl = d['level']
    lw = d.get('why') or ''
    pa = d['path']
    pw = d.get('path_why') or ''
    src = d.get('path_src')
    if src and src not in pw:
        pw = '%s [%s]' % (pw, src)
    return lvl, lw, pa, pw, d['raw']


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
        # *** F-149 - THE COLUMNS DESCRIBED A MODEL THAT NO LONGER RUNS.
        # "Terms averaged" was printing realised, expected and surprise -
        # ALL THREE RETIRED (LD-142, LD-163) - while LEVEL, which carries
        # half the score, did not appear at all. Three of eight rows named
        # no live term. The CPI columns were the old expected() proxy's
        # inputs and stopped feeding anything when LD-142 replaced it.
        #
        # THE COLUMNS NOW ARE THE SCORE: the two live terms, what each one
        # read, and the result. A reader can check the arithmetic from the
        # row, which is the whole point of this section.
        A('    <thead><tr><th>CCY</th><th>Bank</th><th class="num">Rate</th>'
          '<th class="num">Level</th><th>vs corridor</th>'
          '<th class="num">Path</th><th>What is expected</th>'
          '<th class="num">Score</th><th class="num">Category</th>'
          '</tr></thead>')
    elif cat == 'Inflation':
        # *** F-151 - PREVIOUS IMPLIED A RULE THAT NO LONGER RUNS. LD-155
        # reads the LEVEL against the 1.8-2.2 corridor and never looks at
        # the prior print; LD-136's direction test was retired with it. But
        # the table still printed a Previous column beside the score, so a
        # reader comparing 3.2% against 2.9% would reasonably conclude the
        # rise is what scored it. It is not - 3.2% after 3.5% scores the
        # same +1.
        #
        # The columns are now what the rule reads: the print, where it sits
        # against the corridor, and which number scored the row (an actual,
        # or a consensus/forecast when one is published).
        A('    <thead><tr><th>CCY</th><th>Indicator</th>'
          '<th class="num">Print</th><th>Ref</th>'
          '<th>vs 1.8&ndash;2.2 corridor</th><th>Scored from</th>'
          '<th class="num">Score</th><th class="num">Category</th>'
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
            if cat == 'Interest_Rate':
                # F-149 - the rate row has its own five columns now: the
                # standing rate, then the TWO LIVE TERMS with what each one
                # read, then the score. Nothing here is shared with the
                # generic actual/previous/ref shape.
                lvl, lw, pa, pw, raw = v
                _d = RATE[ISO[ccy]]
                A('        <td class="num v">%s</td>' % esc(_d['rate']))
                A('        <td class="num %s">%s</td>'
                  % ('pos' if (lvl or 0) > 0 else
                     'neg' if (lvl or 0) < 0 else 'zero',
                     '%+d' % lvl if lvl is not None else '—'))
                A('        <td class="dim sm">%s</td>' % esc(lw))
                A('        <td class="num %s">%s</td>'
                  % ('pos' if (pa or 0) > 0 else
                     'neg' if (pa or 0) < 0 else 'zero',
                     '%+d' % pa if pa is not None else '—'))
                A('        <td class="dim sm">%s</td>' % esc(pw))
                A('        <td class="num v">%+.2f</td>' % raw)
                if first:
                    A('        <td class="num %s tot" rowspan="%d">%+.2f</td>'
                      % (cls, len(rs), sc))
                A('      </tr>')
                continue
            if cat == 'Inflation':
                import derive_scores as _ds
                _act = v.get('actual', '')
                _sc2, _src2, _why2 = _ds.inflation_decision(actual=_act)
                # *** THE FACT TABLE HOLDS NO EXPECTATION, so
                # inflation_decision runs its after-the-news branch with the
                # print as its own reading and returns "exactly as expected,
                # retain" - true of the code and useless to a reader, who
                # wants to know WHERE THE PRINT SITS. Say that instead; the
                # before/after wording belongs on the calibrator rows, which
                # do carry an expectation.
                # LD-165 - WHERE A PRINT IS SCHEDULED, THE EXPECTATION IS
                # WHAT SCORED THE ROW, so the table must say so. Showing the
                # level test beside a score derived from a consensus is the
                # F-149/F-151 shape: a column describing a rule that did not
                # run.
                _sg = None
                try:
                    if not _ds.SCHED_INF:
                        _ds.load_inflation()
                    _sg = _ds.SCHED_INF.get(ccy)
                except Exception:
                    _sg = None
                if _sg:
                    _e2 = _sg[0] or _sg[1]
                    _src2 = 'consensus' if _sg[0] else 'forecast'
                    _ne = _ds.sm._num(_e2)
                    if _ne is None:
                        _why2 = 'unreadable'
                    elif _ne > _ds.NEW_HIGH:
                        _why2 = ('expects %s &mdash; ABOVE the %.1f%% ceiling'
                                 ' - hike risk' % (_e2, _ds.NEW_HIGH))
                    elif _ne < _ds.NEW_LOW:
                        _why2 = ('expects %s &mdash; BELOW the %.1f%% floor'
                                 ' - cut risk' % (_e2, _ds.NEW_LOW))
                    else:
                        _why2 = ('expects %s &mdash; inside %.1f-%.1f%% - no'
                                 ' compulsion' % (_e2, _ds.NEW_LOW,
                                                  _ds.NEW_HIGH))
                    A('        <td class="num v">%s</td>' % esc(_act or '—'))
                    A('        <td class="dim sm">%s</td>'
                      % esc(v.get('ref', '—')))
                    A('        <td class="dim sm">%s</td>' % _why2)
                    A('        <td class="dim sm">%s</td>' % esc(_src2))
                    A('        <td class="num %s">%s</td>' % (k, txt))
                    if first:
                        A('        <td class="num %s tot" rowspan="%d">%+.2f'
                          '</td>' % (cls, len(rs), sc))
                    A('      </tr>')
                    continue
                _n2 = _ds.sm._num(_act)
                if _n2 is None:
                    _why2 = 'unreadable'
                elif _n2 > _ds.NEW_HIGH:
                    _why2 = ('%.2f%% ABOVE the %.1f%% ceiling - hike risk'
                             % (_n2, _ds.NEW_HIGH))
                elif _n2 < _ds.NEW_LOW:
                    _why2 = ('%.2f%% BELOW the %.1f%% floor - cut risk'
                             % (_n2, _ds.NEW_LOW))
                else:
                    _why2 = ('%.2f%% inside %.1f-%.1f%% - no compulsion'
                             % (_n2, _ds.NEW_LOW, _ds.NEW_HIGH))
                A('        <td class="num v">%s</td>' % esc(_act or '—'))
                A('        <td class="dim sm">%s</td>' % esc(v.get('ref', '—')))
                A('        <td class="dim sm">%s</td>' % esc(_why2))
                A('        <td class="dim sm">%s</td>' % esc(_src2 or '—'))
                A('        <td class="num %s">%s</td>' % (k, txt))
                if first:
                    A('        <td class="num %s tot" rowspan="%d">%+.2f</td>'
                      % (cls, len(rs), sc))
                A('      </tr>')
                continue
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
            A('        <td class="dim sm">%s</td>' % esc(v.get('thr', '—')))
            A('        <td class="num %s">%s</td>' % (k, txt))
            if first:
                A('        <td class="num %s tot" rowspan="%d">%+.2f</td>'
                  % (cls, len(rs), sc))
            A('      </tr>')
    A('    </tbody>')
    A('  </table>')
    A('  </div>')

    if cat == 'Inflation':
        A('  <div class="note"><strong>Inflation is scored on WHERE THE '
          'PRINT SITS, not on which way it moved (LD-155).</strong> Above '
          '2.2&#37; is GOOD &mdash; the bank is behind and a hike is the '
          'risk. Below 1.8&#37; is BAD. Inside the corridor is NEUTRAL: no '
          'compulsion either way.'
          '<br><br>'
          '<strong>&#9888; THE PREVIOUS PRINT NO LONGER ENTERS IT</strong>, '
          'which is why this table does not show one. LD-136 graded '
          '<em>direction</em> &mdash; 3.2&#37; after 3.5&#37; scored 0, '
          'above target but falling &mdash; and LD-155 retired that test. '
          'Under the current rule <strong>3.2&#37; scores +1 whether it rose '
          'from 2.9&#37; or fell from 3.5&#37;</strong>. A Previous column '
          'beside the score would imply a rule that does not run.'
          '<br><br>'
          '<strong>WHEN AN EXPECTATION EXISTS, THE SURPRISE OVERRIDES THE '
          'LEVEL.</strong> A print beating its consensus scores GOOD and one '
          'missing it scores BAD &mdash; even where the level says otherwise, '
          'because the market trades the surprise. The fact table holds no '
          'expectation, so these rows are scored on the level alone; the '
          'calibrator, which grades the week ahead, is where the before-the-'
          'news half runs. Consensus supersedes forecast the moment it is '
          'published, and the <em>Scored from</em> column names which it '
          'was.' + _sched_note() + '</div>')

    if cat == 'Interest_Rate':
        A('  <div class="note"><strong>A rate row is scored from TWO '
          'WEIGHTED TERMS, not from an actual against a threshold.</strong> '
          '<code>score = (level + path) / 2</code>.'
          '<br><br>'
          '<strong>LEVEL (LD-142)</strong> asks <em>where is the rate</em>: '
          'above the 2.5&#37; ceiling and rising scores +1, below the '
          '1.5&#37; floor and falling scores &minus;1, inside the corridor '
          'scores 0 &mdash; no compulsion either way.'
          '<br><br>'
          '<strong>PATH (LD-154)</strong> asks <em>what is expected '
          'next</em>. <strong>BEFORE</strong> a scheduled decision it reads '
          'the expectation against the current rate; <strong>AFTER</strong> '
          'it reads the actual against what was expected, and a fully-priced '
          'decision <em>retains</em> its score rather than being re-paid for '
          'happening (LD-90). Consensus supersedes forecast the moment it is '
          'published, and the bracket names which one scored the row. A '
          'currency with no decision in the calendar carries its last one '
          'forward (LD-154b) &mdash; that is what takes this term from 3 of '
          '8 currencies to all 8.'
          '<br><br>'
          '<strong>&#9888; realised, expected and surprise are RETIRED</strong> '
          '(LD-142, LD-163) and no longer appear. <code>realised</code> paid '
          '+1 for having hiked at all regardless of pricing, which double-'
          'counted what <code>path</code> already measures properly. A term '
          'that cannot be read is dropped from the average rather than '
          'scored 0 &mdash; scoring 0 would assert &ldquo;no move '
          'expected&rdquo; when the truth is that we cannot see one.</div>')

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
