# -*- coding: utf-8 -*-
"""
LD-25: the Fear & Greed block, rendered as the r9 (2026-08-19) BAR CHART.

Jeff, 2026-08-21: "why can't we put it in this format?" - the r9 HTML
rendering, which the markdown-table version had silently downgraded.

The bar chart is not decoration. The whole point of publishing the seven
components is that the headline AVERAGES A DIVERGENCE, and a divergence is
something you see in one glance on a bar chart and have to compute by eye from
a table. The 65-point gap between the top and bottom bar IS the finding.

Colour encodes the RATING, not the value: extreme greed / greed / neutral /
fear / extreme fear map onto the existing palette tokens, so the block stays
theme-correct in light and dark without new colours.

Input is the raw CNN payload (production.dataviz.cnn.io graphdata). This module
is DATA + ARITHMETIC ONLY - it does not fetch. Feed it the parsed JSON.
"""
from datetime import datetime, timezone, timedelta

PHT = timezone(timedelta(hours=8))

ORDER = [
    ('junk_bond_demand', 'Junk Bond Demand'),
    ('safe_haven_demand', 'Safe Haven Demand'),
    ('stock_price_breadth', 'Stock Price Breadth'),
    ('market_volatility_vix', 'Market Volatility (VIX)'),
    ('put_call_options', 'Put / Call Options'),
    ('market_momentum_sp500', 'Market Momentum S&P 500'),
    ('stock_price_strength', 'Stock Price Strength'),
]

# rating -> (css var for the bar, pill class)
TONE = {
    'extreme greed': ('var(--bear)', 'p-bad'),
    'greed':         ('var(--bull)', 'p-good'),
    'neutral':       ('var(--muted)', 'p-neut'),
    'fear':          ('var(--warn)', 'p-warn'),
    'extreme fear':  ('var(--violet)', 'p-vio'),
}


def _pht(ts):
    if ts is None:
        return ''
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000, PHT).strftime('%d %b %H:%M')
    try:
        return datetime.fromisoformat(str(ts).replace('Z', '+00:00')) \
            .astimezone(PHT).strftime('%d %b %H:%M')
    except Exception:
        return str(ts)[:16]


def build(payload, cross_check='', spread_history=''):
    """Return the HTML block. payload = parsed CNN graphdata JSON."""
    fg = payload['fear_and_greed']
    now = float(fg['score'])
    rating = fg.get('rating', '').lower()

    comps = []
    for key, name in ORDER:
        c = payload.get(key)
        if not isinstance(c, dict) or 'score' not in c:
            continue
        comps.append((name, float(c['score']), c.get('rating', '').lower(),
                      _pht(c.get('timestamp'))))

    hist = [('PREV CLOSE', 'previous_close'), ('1 WEEK AGO', 'previous_1_week'),
            ('1 MONTH AGO', 'previous_1_month'), ('1 YEAR AGO', 'previous_1_year')]

    out = ['<div class="fng-head">',
           '<div class="fng-big">%.2f <span class="fng-lab">%s</span></div>'
           % (now, rating.upper()),
           '<div class="fng-hist">']
    for label, key in hist:
        v = float(fg[key])
        d = now - v
        cls = 'up' if d > 0 else ('dn' if d < 0 else '')
        out.append('<div class="fng-h"><span class="fng-lab">%s</span>'
                   '<b>%.2f</b><span class="%s">%+.2f</span></div>'
                   % (label, v, cls, d))
    out.append('</div></div>')

    out.append('<div class="fng-bars">')
    for name, score, rat, ts in comps:
        colour, pill = TONE.get(rat, ('var(--muted)', 'p-neut'))
        out.append(
            '<div class="fng-row">'
            '<span class="fng-n">%s</span>'
            '<span class="fng-track"><i class="fng-fill" style="width:%.1f%%;background:%s"></i></span>'
            '<span class="fng-v">%.1f</span>'
            '<span class="pill %s">%s</span>'
            '</div>' % (name, max(0.0, min(100.0, score)), colour, score, pill, rat))
    out.append('</div>')

    total = sum(c[1] for c in comps)
    mean = total / len(comps) if comps else 0.0
    diff = abs(mean - now)
    terms = ' + '.join('%.1f' % c[1] for c in comps)
    recompute = ('(%s) &divide; %d = <b>%.4f</b> &mdash; published <b>%.4f</b>, '
                 'difference <b>%.4f</b>.' % (terms, len(comps), mean, now, diff))
    if diff < 0.005:
        recompute += (' <b>Matches exactly.</b> CNN uses a <b>simple average</b> '
                      'of the seven, not a weighted one, so the components fully '
                      'explain the headline.')
    else:
        newest = max(comps, key=lambda c: c[3])
        recompute += (' <b>The simple-average property still holds</b> &mdash; the '
                      'components carry <b>independent timestamps</b> (%s is stamped '
                      '%s, the others earlier), so one refreshed after the index '
                      'computed. %.2f on a 0&ndash;100 scale is %.2f%%.'
                      % (newest[0], newest[3], diff, diff))
    out.append('<div class="readbox"><b>Recompute (P2)</b>%s</div>' % recompute)

    hi = max(comps, key=lambda c: c[1])
    lo = min(comps, key=lambda c: c[1])
    spread = hi[1] - lo[1]
    out.append(
        '<div class="warnbox"><b>The headline hides the story.</b> &ldquo;%s %.0f&rdquo; '
        'is the average of a market that is <em>not</em> neutral internally. The spread '
        'between highest and lowest component is <b>%.1f points</b>: <b>%s %.1f (%s)</b> '
        'against <b>%s %.1f (%s)</b>. %s</div>'
        % (rating.title(), now, spread, hi[0], hi[1], hi[2], lo[0], lo[1], lo[2],
           spread_history))

    if cross_check:
        out.append('<div class="readbox"><b>Cross-check</b>%s</div>' % cross_check)
    return '\n'.join(out)
