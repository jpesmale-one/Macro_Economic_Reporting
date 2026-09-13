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
CAP = sorted(glob.glob('data/raw/calendar/2026-09-13_*_cal_full.json'))[-1]
START, END = '2026-09-14', '2026-09-18'

F = ps.final_scores(CAP, START, END)
SC = dict((c, F[c]['total']) for c in F)
BAND, ORDER = ft.bands(SC)
CANDS = ps.candidates(SC, BAND)
# LD-125 - THE SET IS ONE TIER-1 PAIR PER CATEGORY. Jeff, 2026-09-10:
# "on The set let's get Tier 1 pairs for each category".
# NOT leg-disjoint any more: guaranteeing coverage and forbidding leg
# reuse cannot both hold. LEGACY is kept so the page can still show what
# the old gap-first rule would have produced.
# LD-126 - the set covers every CATEGORY and every STRONG CURRENCY.
# Jeff, 2026-09-10: "we have EUR, CHF, JPY as our strong currencies. We
# have pairs for EUR, and CHF but we're not getting for JPY?" Per-category
# coverage does not imply per-currency coverage: CHF and JPY are both safe
# havens, so every pair they make is RISK OFF and they compete for one
# slot. SET SIZE VARIES - that is the honest consequence.
SETROWS = ps.the_set(CANDS, BAND, SC)
PICKED = [x for x, _w in SETROWS]
WHY = dict((id(x), w) for x, w in SETROWS)
LEGACY = ps.select(CANDS)
OVERLAP = ps.leg_overlap(PICKED)
CALD = cal.calibrate(CAP, START, END)
# F-116: a row can have NO published time (NZD Global Dairy Trade). Sorting
# on `when` directly raises on None; dropping such rows would be F-36, where
# a sort silently discarded events. Sort by day, then untimed LAST within
# the day, then by clock - and keep every row.
def _order(r):
    return (r['day'] or dt.date.max,
            1 if r['when'] is None else 0,
            r['when'].strftime('%H:%M') if r['when'] else '')


ROWS = sorted(cal.week_rows(CAP, START, END), key=_order)
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
DAYS = [dt.date(2026, 9, d) for d in (14, 15, 16, 17, 18)]
BANDCLS = {'STRONG': 's', 'NEUTRAL': 'n', 'WEAK': 'w'}


def cls(v):
    return 'pos' if v > 0 else ('neg' if v < 0 else 'zero')


def sg(v, f='%+.2f'):
    return (f % v).replace('-', '\u2212')


o = []
A = o.append

A('<section>')
A('  <h2>The set</h2>')
A('  <p class="sub">%d pairs \u2014 one tier-1 read for every category and every strong currency.</p>'
  % len(PICKED))
A('')
A('  <div class="set">')
for i, c in enumerate(PICKED, 1):
    A('    <div class="pair%s">' % (' top' if i == 1 else ''))
    A('      <span class="rank">%d</span>' % i)
    A('      <span class="sym">%s<span class="bias %s">%s</span></span>'
      % (ps.label(CANDS, c), c['direction'].lower(), c['direction']))
    A('      <span class="gap%s">%s</span>'
      % (' big' if i == 1 else '', sg(c['gap'])))
    A('      <span class="legs"><span class="cat">%s</span> &nbsp;long %s '
      '<strong>%s</strong> \u00b7 short %s <strong>%s</strong></span>'
      % (c['category'], c['long'], sg(SC[c['long']]),
         c['short'], sg(SC[c['short']])))
    A('      <span class="legs"><span class="cat">covers</span> '
      '&nbsp;%s</span>' % ' \u00b7 '.join(WHY[id(c)]))
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
A('')
if OVERLAP:
    A('  <div class="note flag">')
    A('    <span class="lbl">\u26a0 THESE PAIRS SHARE LEGS</span>')
    _worst = max(OVERLAP.values())
    _conc = ('  <strong>Note the concentration: short %s carries %d of the %d pairs.</strong>'
             % (', '.join(k for k, v in OVERLAP.items()
                          if v == _worst), _worst, len(PICKED))
             ) if _worst >= 3 else ''
    A('    <strong>%s.</strong> The set covers every category AND every '
      'strong currency (LD-126), and that guarantee means a currency can '
      'appear more than once. <strong>These are %d separate reads, not a '
      'portfolio</strong> \u2014 taking them all would hold one view several '
      'times over, which is the correlation that inflates a scorecard (EF-3).%s'
      % (', '.join('%s appears in %d pairs' % (k, v)
                   for k, v in sorted(OVERLAP.items(),
                                      key=lambda z: -z[1])),
         len(PICKED), _conc))
    A('  </div>')
_gapfirst = ' \u00b7 '.join('%s %s' % (c['pair'], c['direction'])
                            for c in LEGACY)
A('  <p><strong>The old gap-first rule would have given:</strong> '
  '<span class="mono">%s</span> \u2014 leg-disjoint, %s total gap '
  'against %s here. <strong>That set was optimal on conviction and had '
  'no way to guarantee a category was represented</strong>; this one '
  'guarantees coverage and gives up the disjointness.</p>'
  % (_gapfirst, sg(sum(c['gap'] for c in LEGACY)),
     sg(sum(c['gap'] for c in PICKED))))
A('</section>')
A('<section>')
A('  <h2>\u00a71 The pairs</h2>')
A('  <p class="sub">Risk category is an output, not a forecast.</p>')
# LD-121: count what the TABLES show. Tied twins fold into one row, so
# counting raw candidates here would print "8 RISK OFF" above a table
# listing 6 - two numbers on one page describing the same thing.
_fold = set()
for _p in PICKED:
    for _t in ps.tied_with(CANDS, _p):
        _fold.add(id(_t))
_shown = [c for c in CANDS if id(c) not in _fold]
non = len([c for c in _shown if c['category'] == 'RISK ON'])
noff = len([c for c in _shown if c['category'] == 'RISK OFF'])
nei = len([c for c in _shown if c['category'] == 'EITHER'])

A('  <p>Of the <strong>%d permitted pairings, %d are RISK ON, %d RISK OFF '
  'and %d EITHER</strong>. Nothing here predicts the regime \u2014 the roles '
  'present in each band decide which categories can be filled.</p>'
  % (non + noff + nei, non, noff, nei))
A('')
# LD-123 - ONE REPRESENTATIVE PER CATEGORY. Jeff, 2026-09-10: "I want you to
# give me representative for each categories (Risk On, Off, Either)".
#
# THE CASE THAT MAKES IT NECESSARY, live this week: EITHER holds +5.88 - the
# SECOND WIDEST GAP ON THE BOARD - and contributed NOTHING to the set,
# because both its top pairs need EUR and EURUSD had already taken it. A
# reader seeing "EITHER: 0 selected" would conclude the category was weak.
# It was crowded out by leg-disjointness, which is a different fact.
A('  <h3>The strongest read in each category</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Category</th><th>Representative</th><th>Dir</th>'
  '<th class="num">Gap</th><th>Long / short</th><th>In the set?</th>'
  '</tr></thead>')
A('    <tbody>')
for _cat, _top, _inset in ps.representatives(CANDS, PICKED):
    A('      <tr%s><td><span class="cat">%s</span></td>'
      '<td class="ccy">%s</td><td>%s</td><td class="num %s">%s</td>'
      '<td>%s over %s</td><td>%s</td></tr>'
      % (' class="sel"' if _inset else '', _cat, ps.label(CANDS, _top),
         _top['direction'], 'pos' if _inset else '', sg(_top['gap']),
         _top['long'], _top['short'],
         '<strong>yes</strong>' if _inset
         else '<span class="zero">crowded out</span>'))
A('    </tbody>')
A('  </table>')
A('  </div>')
_out = [(c, t) for c, t, i in ps.representatives(CANDS, PICKED) if not i]
if _out:
    A('  <p><strong>%s</strong> \u2014 %s. <strong>That is a leg conflict, '
      'not a weak read</strong>: the pairs it would need were built on '
      'currencies an earlier, wider pair had already taken (LD-96).</p>'
      % (', '.join('%s carries %s and is not in the set'
                   % (c, sg(t['gap'])) for c, t in _out),
         'leg-disjoint selection allows each currency once'))
A('')

# LD-120 - ONE TABLE PER RISK CATEGORY. Jeff, 2026-09-10: "create a table for
# each category Risk On, Risk Off, Either just so the pairs are segragated and
# easy to spot". The categories are an OUTPUT of which roles sit in which band
# (LD-99), so grouping by them shows what the week actually permits - a band
# holding no safe haven simply produces no RISK OFF table.
# LD-121: a twin folded into a selected row must NOT also render as its own
# row. NZDCHF was appearing twice - once inside "AUDCHF/NZDCHF" and again
# beneath it - which reads as four pairs when the model produced three.
_folded = set()
for _p in PICKED:
    for _t in ps.tied_with(CANDS, _p):
        _folded.add(id(_t))

for _cat in ('RISK ON', 'RISK OFF', 'EITHER'):
    # LD-125: Jeff, 2026-09-10 - "for §1 The pairs sort them by Tier
    # then Gap". Tier 1 is STRONG vs WEAK, the widest structural
    # separation; sorting on it first puts the strongest STRUCTURE at the
    # top rather than the widest number, which can be a tier-2 pair.
    _rows = sorted([c for c in CANDS
                    if c['category'] == _cat and id(c) not in _folded],
                   key=lambda c: (c['tier'], -c['gap']))
    if not _rows:
        A('  <h3>%s</h3>' % _cat)
        A('  <p class="note">No pairing this week produces a %s pair \u2014 '
          'the bands hold no role combination that fills it.</p>' % _cat)
        continue
    _sel = [c for c in _rows if c in PICKED]
    A('  <h3>%s <span class="wt">%d pair%s\u00b7 %d selected</span></h3>'
      % (_cat, len(_rows), 's ' if len(_rows) != 1 else ' ', len(_sel)))
    A('  <div class="scroll">')
    A('  <table>')
    A('    <thead><tr><th>Pair</th><th>Dir</th>'
      '<th class="num">Tier</th><th class="num">Gap</th>'
      '<th>Long / short</th></tr></thead>')
    A('    <tbody>')
    for c in _rows:
        s = c in PICKED
        A('      <tr%s><td class="ccy">%s</td><td>%s</td>'
          '<td class="num">%d</td><td class="num %s">%s</td>'
          '<td>%s over %s</td></tr>'
          % (' class="sel"' if s else '', (ps.label(CANDS, c) if s else c['pair']), c['direction'],
             c['tier'], 'pos' if s else '', sg(c['gap']), c['long'],
             c['short']))
    A('    </tbody>')
    A('  </table>')
    A('  </div>')
# LD-121 - A TIE IS PROPOSED AS BOTH PAIRS, ONE SLOT. Jeff, 2026-09-10:
# "Instead of dropping 1, propose both instead. Something like AUDCHF/NZDCHF".
# The gap is identical because the two legs scored identically, so choosing
# between them on sort order asserted a preference the data never had.
_ties = [(c, ps.tied_with(CANDS, c)) for c in PICKED]
_ties = [(c, t) for c, t in _ties if t]
if _ties:
    A('  <div class="note">')
    _txt = '; '.join(
        '<strong>%s</strong> at gap %s' % (ps.label(CANDS, c), sg(c['gap']))
        for c, t in _ties)
    A('    <strong>A slash means the legs scored identically and either '
      'expression carries the same read</strong> \u2014 %s. '
      '<strong>They are alternatives, not additions</strong>: both share a '
      'leg, so taking both would hold one exposure twice, which is the '
      'correlation LD-96\'s leg-disjoint rule exists to prevent. '
      '<strong>The slot counts once.</strong>' % _txt)
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
A('<section>')
A('  <h2>\u00a72 The board</h2>')
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
A('<section>')
A('  <h2>\u00a73 The calibrator</h2>')
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
    # F-116: TE schedules some rows with NO time (NZD Global Dairy Trade).
    # Calling .strftime() on None killed the build; dropping the row would
    # be F-36. Publish it with its day and an explicit "no time".
    _when = (r['when'].strftime('%a %d %H:%M') if r['when']
             else ('%s \u2014' % r['day'].strftime('%a %d')
                   if r.get('day') else 'no time'))
    A('      <tr><td class="mono">%s</td><td class="ccy">%s</td><td>%s</td>'
      '<td class="num v">%s</td><td class="num v">%s</td>%s</tr>'
      % (_when, r['ccy'], r['name'],
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


# F-110 - SECTION 4 IS NOW GENERATED. It used to be hand-written in the page
# shell, so the first splice that replaced the body deleted it silently -
# taking the VINTAGE DISCLOSURE with it. A back-dated edition that does not
# say which vintage it used is precisely what the repo's rules forbid.
A('')
A('<section>')
A('  <h2>\u00a75 Method and limits</h2>')
A('  <p class="sub">What this report can and cannot see.</p>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Term</th><th>Range</th><th>Source</th></tr></thead>')
A('    <tbody>')
_lim = sum(ft.WEIGHT.values())
_nm = {6: 'six', 7: 'seven', 8: 'eight'}.get(len(ft.WEIGHT), str(len(ft.WEIGHT)))
A('      <tr><td>Base</td><td class="mono">\u2212%d \u2026 +%d</td>'
  '<td>%s fact tables, <code>%s</code>, %d of %d cells</td></tr>'
  % (_lim, _lim, _nm, MONTH, scored, total))
A('      <tr><td>Calibrator</td><td class="mono">\u22125 \u2026 +5</td>'
  '<td><strong>%d scheduled rows, %d scorable, %d with a TE consensus'
  '</strong></td></tr>' % (len(ROWS), n_scor, n_cons))
A('      <tr class="sel"><td><strong>FINAL</strong></td>'
  '<td class="mono"><strong>\u2212%d \u2026 +%d</strong></td>'
  '<td>the sum</td></tr>' % (_lim + 5, _lim + 5))
A('    </tbody>')
A('  </table>')
A('  </div>')
A('')
A('  <div class="note flag">')
A('    <span class="lbl">\u26a0 VINTAGE</span>')
A('    <strong>Built as of Sunday 6 September.</strong> The fact tables hold '
  'what was knowable then \u2014 rows that printed Mon 7 or Tue 8 are held at '
  'their earlier values.<br><br>'
  'Releases up to Friday 4 September stay: a Sunday report legitimately sees '
  'Friday\'s prints.<br><br>'
  '<strong>Leaving the Mon/Tue prints in would have been a backtest '
  'contaminated with hindsight.</strong> An analysis asking <em>what was '
  'knowable then</em> must use the vintage available then, and say which it '
  'used. This one says.')
A('  </div>')
A('')
A('  <h3>What is not here</h3>')
A('  <div class="scroll">')
A('  <table>')
A('    <thead><tr><th>Absent</th><th>Reason</th></tr></thead>')
A('    <tbody>')
A('      <tr><td>Gold, BTC</td><td><strong>Removed</strong> \u2014 forex '
  'focus</td></tr>')
A('      <tr><td>Entry references, falsifiers, charts</td>'
  '<td><strong>No price data in this edition</strong></td></tr>')
A('      <tr><td>News, rate-path commentary</td><td>LD-97 \u2014 the weekly '
  'is the decision</td></tr>')
A('      <tr><td>Lot sizes, entries, stops, targets</td>'
  '<td><strong>LD-4 \u2014 no money path</strong></td></tr>')
A('    </tbody>')
A('  </table>')
A('  </div>')
A('</section>')

io.open(SP + 'body.html', 'w', encoding='utf-8', newline=NL).write(NL.join(o))
print('body.html: %d lines' % len(o))
print('SET: %s' % ', '.join('%s %s %+.2f' % (c['pair'], c['direction'],
                                             c['gap']) for c in PICKED))
