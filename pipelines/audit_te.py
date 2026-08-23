# -*- coding: utf-8 -*-
"""Audit score_model.ROWS against TE country indicator pages (F-34 follow-up)."""
import re, io, html, os, sys, difflib

SC = os.environ.get('TE_AUDIT_DIR', os.path.dirname(os.path.abspath(__file__)))
REPO = r'c:/Users/jpesm/OneDrive/Documents/GitHub/Macro_Economic_Reporting'
sys.path.insert(0, os.path.join(REPO, 'pipelines'))
import score_model as sm

SLUG = {'US': 'united-states', 'EA': 'euro-area', 'GB': 'united-kingdom',
        'JP': 'japan', 'AU': 'australia', 'NZ': 'new-zealand',
        'CA': 'canada', 'CH': 'switzerland'}


def parse(path):
    """TE indicator rows: name | last | previous | unit | reference."""
    s = io.open(path, encoding='utf-8', errors='ignore').read()
    out = {}
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', s, re.S):
        cells = [html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c))).strip()
                 for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
        cells = [c for c in cells if c]
        if len(cells) >= 4 and re.match(r'^[A-Za-z]', cells[0]):
            # last cell that looks like a reference period
            ref = ''
            for c in cells[::-1]:
                if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Q[1-4])', c):
                    ref = c; break
            nums = [c for c in cells[1:] if re.match(r'^-?[\d.,]+%?$', c)]
            if nums:
                out[cells[0].lower()] = (nums[0], nums[1] if len(nums) > 1 else '', ref)
    return out


def norm(n):
    n = n.lower()
    for junk in (' final', ' prel', ' flash', ' yoy', ' mom', ' qoq', ' rate',
                 ' change', ' index', ' s&p global', ' ism', ' anz', ' gfk',
                 ' cb ', ' nab ', ' westpac', ' rba ', ' au ', ' procure.ch-ubs'):
        n = n.replace(junk, ' ')
    return re.sub(r'\s+', ' ', n).strip()


print('=' * 78)
print('WHITELIST AUDIT vs TradingEconomics country indicator pages')
print('=' * 78)
matched = mismatch = notfound = 0
issues = []
for r in sm.ROWS:
    cat, iso, name, act, prev, ref, thr, score = r
    ccy = sm.LABEL[iso]
    te = parse(os.path.join(SC, 'audit', SLUG[iso] + '.html'))
    key = None
    nl = name.lower()
    if nl in te:
        key = nl
    else:
        cand = difflib.get_close_matches(norm(name), [norm(k) for k in te], n=1, cutoff=0.86)
        if cand:
            for k in te:
                if norm(k) == cand[0]:
                    key = k; break
    if not key:
        notfound += 1
        continue
    tl, tp, tr_ref = te[key]

    def num(x):
        m = re.search(r'-?[\d.]+', (x or '').replace(',', ''))
        return float(m.group(0)) if m else None
    a, t = num(act), num(tl)
    ok = (a is not None and t is not None and abs(a - t) < 0.06)
    if ok:
        matched += 1
    else:
        mismatch += 1
        issues.append((ccy, cat, name, act, ref, tl, tr_ref, key))

print()
print('MATCHED %d  |  MISMATCH %d  |  NOT MATCHED ON NAME %d  (of %d)'
      % (matched, mismatch, notfound, len(sm.ROWS)))
if issues:
    print()
    print('--- ROWS WHERE OUR VALUE DIFFERS FROM TE ---')
    print('%-4s %-34s %-11s %-8s %-11s %-8s' % ('CCY', 'INDICATOR', 'OURS', 'OUR REF', 'TE', 'TE REF'))
    for ccy, cat, name, act, ref, tl, tref, key in issues:
        print('%-4s %-34s %-11s %-8s %-11s %-8s' % (ccy, name[:34], act, ref, tl, tref))
        if key.lower() != name.lower():
            print('       matched TE row: "%s"' % key)
