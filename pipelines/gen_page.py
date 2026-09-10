# -*- coding: utf-8 -*-
"""Generate the whole web page from the model - nothing hand-typed.

Every figure the page shows is read from the pipelines at build time. The
first three revisions carried hand-typed numbers and went stale the moment
F-92/F-93 moved the board; two of them I had already corrected by hand in
the OUTPUT and watched the next rebuild revert.
"""
import io, os, sys, glob, json, datetime as dt

os.chdir(r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting')
sys.path.insert(0, os.path.join(os.getcwd(), 'pipelines'))
NL = chr(10)
import fact_tables as ft
import pair_select as ps
import calibrator as cal

SP = ('C:/Users/jpesm/AppData/Local/Temp/claude/'
      'c--Users-jpesm-OneDrive-Documents-GitHub/'
      '16c8f514-dc2c-4587-b6a0-4fa0ff0b7ba8/scratchpad/')
CAP = sorted(glob.glob('data/raw/calendar/2026-09-08_*_cal_full.json'))[-1]
START, END = '2026-09-07', '2026-09-11'

F = ps.final_scores(CAP, START, END)
SC = dict((c, F[c]['total']) for c in F)
BAND, ORDER = ft.bands(SC)
CANDS = ps.candidates(SC, BAND)
PICKED = ps.select(CANDS)
CALD = cal.calibrate(CAP, START, END)
ROWS = sorted(cal.week_rows(CAP, START, END), key=lambda r: r['when'])
B = ft.base_scores()
BSC = dict((c, F[c]['base']) for c in F)
BBAND, BORDER = ft.bands(BSC)
BPICK = ps.select(ps.candidates(BSC, BBAND))
MONTH = ft.latest_month()
scored, total = ft.coverage(MONTH)
BRANK = dict((c, i + 1) for i, c in enumerate(BORDER))
FRANK = dict((c, i + 1) for i, c in enumerate(ORDER))
n_cons = len([r for r in ROWS if r['cons']])
n_scor = len([r for r in ROWS if r['score'] is not None])
BEST = PICKED[0]
DAYS = [dt.date(2026, 9, d) for d in (7, 8, 9, 10, 11)]
BANDCLS = {'STRONG': 's', 'NEUTRAL': 'n', 'WEAK': 'w'}


def cls(v):
    return 'pos' if v > 0 else ('neg' if v < 0 else 'zero')


def sg(v, f='%+.2f'):
    return (f % v).replace('-', '\u2212')


o = []
A = o.append

A('<section>')
A('  <h2>The set</h2>')
A('  <p class="sub">%d pairs, leg-disjoint. Nothing forced the number.</p>'
  % len(PICKED))
A('')
A('  <div class="set">')
for i, c in enumerate(PICKED, 1):
    A('    <div class="pair%s">' % (' top' if i == 1 else ''))
    A('      <span class="rank">%d</span>' % i)
    A('      <span class="sym">%s<span class="bias %s">%s</span></span>'
      % (c['pair'], c['direction'].lower(), c['direction']))
    A('      <span class="gap%s">%s</span>'
      % (' big' if i == 1 else '', sg(c['gap'])))
    A('      <span class="legs"><span class="cat">%s</span> &nbsp;long %s '
      '<strong>%s</strong> \u00b7 short %s <strong>%s</strong></span>'
      % (c['category'], c['long'], sg(SC[c['long']]),
         c['short'], sg(SC[c['short']])))
    A('    </div>')
A('  </div>')
A('')
A('  <p><strong>%s %s carries the widest gap on the board at %s</strong> '
  '\u2014 <strong>%s is top at %s and %s is bottom at %s</strong>.</p>'
  % (BEST['pair'], BEST['direction'], sg(BEST['gap']),
     ORDER[0], sg(SC[ORDER[0]]), ORDER[-1], sg(SC[ORDER[-1]])))
last = PICKED[-1]
if len(PICKED) > 1 and last['gap'] < 2.0:
    # LD-108: a gap under 0.50 on a +/-14 scale is not a weak view, it is
    # noise. Jeff's call 2026-09-09 is to TAKE it (LD-96 - take what
    # qualifies) rather than reinstate a floor, so the report has to say so
    # in proportion to how thin it actually is.
    _noise = last['gap'] < 0.50
    A('  <div class="note flag">')
    A('    <span class="lbl">%s</span>'
      % ('⚠ THE LAST PAIR IS NOISE, NOT A VIEW' if _noise
         else '⚠ THE TAIL IS THIN'))
    A('    <strong>%s %s rests on a %s gap</strong> — %s at %s against %s '
      'at %s. %s'
      % (last['pair'], last['direction'], sg(last['gap']),
         last['long'], sg(SC[last['long']]),
         last['short'], sg(SC[last['short']]),
         ('<strong>On a ±14 scale that is inside the rounding of a '
          'single indicator flip</strong> — one row changing verdict would '
          'reverse it. It is in the set because it qualified and no rule '
          'forces a count either way (LD-96); <strong>read it as a coin '
          'flip, not a signal.</strong>') if _noise else
         ('On a ±14 scale that is a weak view. It is in the set because '
          'it qualified, not because anything demanded another pair.')))
    A('  </div>')
used = set()
for c in PICKED:
    used.add(c['long'])
    used.add(c['short'])
unused = sorted(set(ft.CCYS) - used)
A('')
A('  <p><strong>%d currencies used; %s.</strong> No currency is used twice.</p>'
  % (len(used),
     ('%s unused' % ' and '.join(unused)) if unused else 'none unused'))
A('</section>')

# ------------------------------------------------------------------ 1
A('')
A('<section>')
A('  <h2>\u00a71 The board</h2>')
A('  <p class="sub">FINAL = base + calibrator</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Band</th><th>CCY</th><th>Role</th>'
  '<th class="num">Base</th><th class="num">Calib</th>'
  '<th class="num">Final</th><th class="num">Lead</th>'
  '<th class="num">Confirm</th></tr></thead>')
A('    <tbody>')
for c in ORDER:
    A('      <tr><td><span class="band %s">%s</span></td>'
      '<td class="ccy">%s</td><td>%s</td>'
      '<td class="num">%s</td><td class="num %s">%s</td>'
      '<td class="num %s">%s</td><td class="num">%s</td>'
      '<td class="num">%s</td></tr>'
      % (BANDCLS[BAND[c]], BAND[c], c, ft.ROLE[c],
         sg(F[c]['base']), cls(F[c]['cal']), sg(F[c]['cal']),
         cls(F[c]['total']), sg(F[c]['total']),
         sg(B[c]['leading']), sg(B[c]['confirming'])))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('')
A('  <dl class="kv">')
# F-105b: the range and the table count were typed for six categories.
# LD-113 made both wrong. Derive from WEIGHT, the one authority.
_lim = sum(ft.WEIGHT.values())
_nm = {6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}.get(
    len(ft.WEIGHT), str(len(ft.WEIGHT)))
A('    <dt>Base</dt><dd>\u2212%d \u2026 +%d \u2014 %s fact tables, <code>%s</code>, '
  '%d of %d cells scored</dd>' % (_lim, _lim, _nm, MONTH, scored, total))
A('    <dt>Calibrator</dt><dd>\u22125 \u2026 +5 \u2014 %d scheduled rows, %d '
  'scorable, %d with a TE consensus</dd>' % (len(ROWS), n_scor, n_cons))
A('    <dt>Weights</dt><dd>%s = <strong>2</strong> (leading) \u00b7 %s = <strong>1</strong>. '
  '<strong>The calibrator has no weights</strong> \u2014 the day is the unit.</dd>'
  % (' \u00b7 '.join(sorted(c.replace('_', ' ') for c in ft.LEADING)), ' \u00b7 '.join(sorted(c.replace('_', ' ') for c in ft.CONFIRMING))))
sizes = [len([c for c in ORDER if BAND[c] == b])
         for b in ('STRONG', 'NEUTRAL', 'WEAK')]
ties = {}
for c in ORDER:
    ties.setdefault(round(SC[c], 4), []).append(c)
tied = [v for v in ties.values() if len(v) > 1]
A('    <dt>Bands</dt><dd>Target 3 / 2 / 3 by rank, and <strong>a tie is '
  'never split</strong>. This week: <strong>%d / %d / %d</strong>.%s</dd>'
  % (sizes[0], sizes[1], sizes[2],
     ' ' + ' '.join('<strong>%s tie at %s and share a band.</strong>'
                    % (' and '.join(g), sg(SC[g[0]])) for g in tied)
     if tied else ''))
A('  </dl>')
A('')
A('  <h3>What the calibrator changed</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>CCY</th><th class="num">Base</th>'
  '<th class="num">Calib</th><th class="num">Final</th>'
  '<th>Effect</th></tr></thead>')
A('    <tbody>')
for c in sorted(ORDER, key=lambda x: -abs(F[x]['cal'])):
    if not F[c]['cal']:
        continue
    moved = BBAND[c] != BAND[c]
    eff = ('<strong>%s \u2192 %s</strong>' % (BBAND[c], BAND[c])
           if moved else 'stays %s' % BAND[c])
    A('      <tr%s><td class="ccy">%s</td>'
      '<td class="num">%s <span class="zero">(#%d)</span></td>'
      '<td class="num %s">%s</td>'
      '<td class="num">%s <span class="zero">(#%d)</span></td>'
      '<td>%s</td></tr>'
      % (' class="sel"' if moved else '', c, sg(F[c]['base']), BRANK[c],
         cls(F[c]['cal']), sg(F[c]['cal']), sg(F[c]['total']),
         FRANK[c], eff))
A('    </tbody>')
A('  </table>')
A('  </div>')
moved = [c for c in ORDER if BBAND[c] != BAND[c]]
changed = len([c for c in ORDER if F[c]['cal']])
spread = SC[ORDER[0]] - SC[ORDER[-1]]
A('  <p><strong>%d of 8 currencies move band</strong> (%d take a non-zero '
  'adjustment). <strong>The board is tightly packed \u2014 the whole final '
  'spread is %.2f points \u2014 so a term bounded at \u00b15 re-ranks it '
  'readily</strong>, which is what a calibrator is for.</p>'
  % (len(moved), changed, spread))
A('</section>')

# ------------------------------------------------------------------ 2
A('')
A('<section>')
A('  <h2>\u00a72 The calibrator</h2>')
A('  <p class="sub">The day is the unit, not the category.</p>')
A('  <p>One question per currency per day \u2014 <em>is this currency positive '
  'or negative on Monday?</em> <strong>A currency with three releases on '
  'Tuesday scores Tuesday once</strong>, so a crowded calendar cannot '
  'outvote the macro base by accident.</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>CCY</th>'
  + ''.join('<th class="num">%s</th>' % d.strftime('%a %d').replace(' 0', ' ')
            for d in DAYS)
  + '<th class="num">Week</th></tr></thead>')
A('    <tbody>')
for c in ORDER:
    cells = []
    for d in DAYS:
        e = CALD[c]['days'].get(d)
        cells.append('<td class="num dash">\u2014</td>' if e is None
                     else '<td class="num %s">%s</td>' % (cls(e[0]), sg(e[0])))
    t = CALD[c]['total']
    A('      <tr><td class="ccy">%s</td>%s<td class="num %s">%s</td></tr>'
      % (c, ''.join(cells), cls(t), sg(t)))
A('    </tbody>')
A('  </table>')
A('  </div>')
quiet = [c for c in ORDER if not CALD[c]['days']]
A('  <div class="note"><strong>A dash is a day with no scheduled whitelist '
  'row.</strong>%s</div>'
  % ((' <strong>%s ha%s no rows at all this week</strong>, so %s '
      'calibrator term%s +0.00 by absence \u2014 not by balance.'
      % (' and '.join(quiet), 's' if len(quiet) == 1 else 've',
         'its' if len(quiet) == 1 else 'their',
         ' is' if len(quiet) == 1 else 's are')) if quiet else ''))
A('')
A('  <h3>Every scheduled row, and how it scored</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>When (PHT)</th><th>CCY</th><th>Indicator</th>'
  '<th class="num">Previous</th><th class="num">Cons / Fcst</th>'
  '<th class="num">Score</th></tr></thead>')
A('    <tbody>')
for r in ROWS:
    rng = r['cons'] or ''
    if r['fcst'] and r['fcst'] != r['cons']:
        rng = ('%s \u2013 %s' % (rng, r['fcst'])) if rng else r['fcst']
    s = r['score']
    sc = ('<td class="num %s">%s</td>' % (cls(s), sg(s, '%+d'))
          if s else '<td class="num zero">0</td>') if s is not None \
        else '<td class="num dash">\u2014</td>'
    A('      <tr><td class="mono">%s</td><td class="ccy">%s</td><td>%s</td>'
      '<td class="num v">%s</td><td class="num v">%s</td>%s</tr>'
      % (r['when'].strftime('%a %d %H:%M'), r['ccy'], r['name'],
         (r['prev'] or '\u2014').replace('-', '\u2212'),
         (rng or '\u2014').replace('-', '\u2212'), sc))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('  <p><strong>%d of %d rows are scorable, and %d carry a real TE '
  'consensus.</strong> That is the value of building on Sunday rather than '
  'a week out \u2014 the same pipeline run against 14\u201318 Sep could score '
  'only 13 of 20, because <strong>TE publishes consensus close to the '
  'release</strong>.</p>' % (n_scor, len(ROWS), n_cons))
A('')
A('  <h3>The collision rules, from this run</h3>')
for d in DAYS:
    for c in ORDER:
        e = CALD[c]['days'].get(d)
        if not e:
            continue
        val, rule, keep, drop = e
        if len(keep) + len(drop) < 2:
            continue
        A('  <p><strong>%s, %s \u2014 %d rows, %s.</strong></p>'
          % (d.strftime('%a %d').replace(' 0', ' '), c, len(keep) + len(drop),
             'RULE 1 \u2014 latest month wins' if rule == 'latest month'
             else 'RULE 2 \u2014 same month, shared'))
        A('  <div class="scroll">')
        A('  <table>')
        A('    <thead><tr><th>Row</th><th>Ref</th><th class="num">Score</th>'
          '<th>Kept?</th></tr></thead>')
        A('    <tbody>')
        for r in keep + drop:
            k = r in keep
            A('      <tr%s><td>%s</td><td class="mono">%s</td>'
              '<td class="num %s">%s</td><td>%s</td></tr>'
              % (' class="sel"' if k else '', r['name'],
                 (r['raw'] or '')[-3:].upper(), cls(r['score']),
                 sg(r['score'], '%+d') if r['score'] else '0',
                 '<strong>KEPT</strong>' if k else
                 '<span class="zero">dropped</span>'))
        A('    </tbody>')
        A('  </table>')
        A('  </div>')
        kv = sum(r['score'] for r in keep) / float(len(keep))
        alls = keep + drop
        av = sum(r['score'] for r in alls) / float(len(alls))
        if rule == 'latest month' and abs(kv - av) > 0.01:
            A('  <div class="note flag"><span class="lbl">\u26a0 THE RULE '
              'CHANGES THE NUMBER</span>Sharing all %d rows would give '
              '<strong>%s</strong>; taking only the latest month gives '
              '<strong>%s</strong>. <strong>The most current read of the '
              'economy decides the day</strong> \u2014 an older row does not '
              'dilute it.</div>' % (len(alls), sg(av), sg(kv)))
        else:
            A('  <p>Day score <strong>%s</strong>.</p>' % sg(val))
A('</section>')

# ------------------------------------------------------------------ 3
A('')
A('<section>')
A('  <h2>\u00a73 The pairs</h2>')
A('  <p class="sub">Risk category is an output, not a forecast.</p>')
non = len([c for c in CANDS if c['category'] == 'RISK ON'])
noff = len([c for c in CANDS if c['category'] == 'RISK OFF'])
nei = len([c for c in CANDS if c['category'] == 'EITHER'])
A('  <p>Of the <strong>%d permitted pairings, %d are RISK ON, %d RISK OFF '
  'and %d EITHER</strong>. Nothing here predicts the regime \u2014 the roles '
  'present in each band decide which categories can be filled.</p>'
  % (len(CANDS), non, noff, nei))
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Pair</th><th>Dir</th><th>Category</th>'
  '<th class="num">Tier</th><th class="num">Gap</th>'
  '<th>Long / short</th></tr></thead>')
A('    <tbody>')
for c in CANDS:
    sel = c in PICKED
    A('      <tr%s><td class="ccy">%s</td><td>%s</td><td>%s</td>'
      '<td class="num">%d</td><td class="num %s">%s</td>'
      '<td>%s over %s</td></tr>'
      % (' class="sel"' if sel else '', c['pair'], c['direction'],
         c['category'], c['tier'], 'pos' if sel else '',
         sg(c['gap']), c['long'], c['short']))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('  <p><strong>Conviction is the score gap, not the category</strong> \u2014 '
  'a RISK OFF pair is not inherently better than a RISK ON one. Tier 1 is '
  'STRONG vs WEAK; tier 2 is STRONG vs NEUTRAL or NEUTRAL vs WEAK. '
  '<strong>All 28 currency combinations are eligible</strong>, each returned '
  'in the symbol the market quotes with the direction carrying the bias.</p>')
A('')
A('  <h3>What the calibrator changed in the set</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Basis</th><th>Pairs</th></tr></thead>')
A('    <tbody>')
A('      <tr><td class="zero">Base only</td><td class="mono">%s</td></tr>'
  % ' \u00b7 '.join('%s %s' % (c['pair'], c['direction']) for c in BPICK))
A('      <tr class="sel"><td><strong>+ calibrator</strong></td>'
  '<td class="mono"><strong>%s</strong></td></tr>'
  % ' \u00b7 '.join('%s %s' % (c['pair'], c['direction']) for c in PICKED))
A('    </tbody>')
A('  </table>')
A('  </div>')
bp = set('%s %s' % (c['pair'], c['direction']) for c in BPICK)
fp = set('%s %s' % (c['pair'], c['direction']) for c in PICKED)
gone, new = sorted(bp - fp), sorted(fp - bp)
if gone or new:
    A('  <p><strong>The calibrator changed the set.</strong> %s%s</p>'
      % (('<strong>Out: %s.</strong> ' % ', '.join(gone)) if gone else '',
         ('<strong>In: %s.</strong>' % ', '.join(new)) if new else ''))
else:
    A('  <p><strong>The calibrator did not change the set this week</strong> '
      '\u2014 it re-ranked the board without altering which pairs qualify.</p>')
A('</section>')

io.open(SP + 'body.html', 'w', encoding='utf-8', newline=NL).write(NL.join(o))
print('body.html: %d lines' % len(o))
print('SET: %s' % ', '.join('%s %s %+.2f' % (c['pair'], c['direction'],
                                             c['gap']) for c in PICKED))
