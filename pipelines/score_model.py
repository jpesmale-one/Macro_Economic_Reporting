# TRTM-style provenance: this file implements LD-13 (weighted category scoring),
# locked 2026-08-19. It is DATA + ARITHMETIC only - no fetching, no I/O.
# The ROWS table is replaced each edition; W and compute() are the model.
#
# NOTE (T1 boundary): this produces numbers Jeff acts on, so if it is ever
# wired to fetch its own data it fires T1/T3 and takes the full gate ladder.
# As a pure scoring function fed by hand-verified rows, it stays LEAN.

# Weighted category scoring per Jeff's spec (2026-08-19).
#   Category weights: Inflation 3, Employment 2, Production/Spending/Trade 1.
#   Within a category, a currency's N indicators split the weight evenly:
#     each indicator is worth weight/N.  GOOD = +w/N, BAD = -w/N, NEUTRAL = 0.
#   Max possible = 3+2+1+1+1 = 8; min = -8.
# MISSING indicators do NOT score (0) but shrink the category's realised
# coverage, which is reported so a thin category is visible.

W = {"Production":1, "Spending":1, "Trade":1, "Employment":2, "Inflation":3}
# Interest Rate is category 6, weight 3 - scored in pipelines/rate_model.py (LD-23).
# Range is therefore +/-11.00, not +/-8.00.

# (category, ccy, indicator, actual, prev, ref, rule, score)  score in GOOD/BAD/NEUTRAL/MISSING
ROWS = [
 # ---------------- PRODUCTION (w=1) ----------------
 ("Production","US","ISM Manufacturing PMI","53.2","53.9","Aug/26",">50.5","GOOD"),
 ("Production","US","Industrial Production YoY","1.1%","1.29%","Jul/26",">0.5%","GOOD"),
 ("Production","US","Manufacturing Production YoY","1.2%","1.1%","Jul/26",">0.5%","GOOD"),
 ("Production","US","Durable Goods Ex Transp MoM","0.4%","0.6%","Jul/26",">0.5%","BAD"),
 ("Production","EA","S&P Global Mfg PMI Final","51.9","51.4","Jul/26",">50.5","GOOD"),
 ("Production","EA","Industrial Production YoY","0.1%","-0.1%","Jun/26","0-0.5%","NEUTRAL"),
 ("Production","GB","S&P Global Mfg PMI Final","51.9","52.5","Jul/26",">50.5","GOOD"),
 ("Production","GB","Industrial Production YoY","-0.2%","1.0%","Jun/26","<0%","BAD"),
 ("Production","GB","Manufacturing Production YoY","0.5%","2.0%","Jun/26","0-0.5%","NEUTRAL"),
 ("Production","JP","Industrial Production YoY Final","4.9%","-2.1%","Jun/26",">0.5%","GOOD"),
 ("Production","JP","Machinery Orders YoY","16.9%","-1.9%","Jun/26",">0.5%","GOOD"),
 ("Production","JP","Machine Tool Orders YoY","50.4%","52.8%","Jul/26",">0.5%","GOOD"),
 ("Production","JP","S&P Global Mfg PMI Final","54.5","54.8","Jul/26",">50.5","GOOD"),
 ("Production","AU","S&P Global Mfg PMI Final","52.0","51.5","Jul/26",">50.5","GOOD"),
 ("Production","NZ","Business NZ PMI","54.3","60.1","Jul/26",">50.5","GOOD"),
 ("Production","NZ","Global Dairy Trade Price Index","2.3%","0.1%","Aug/26",">0.5%","GOOD"),
 ("Production","CA","S&P Global Mfg PMI","53.5","53.0","Jul/26",">50.5","GOOD"),
 ("Production","CH","Procure.ch-UBS Mfg PMI","53.2","54.3","Jul/26",">50.5","GOOD"),
 ("Production","CH","Industrial Production YoY","5.5%","-7.1%","Q2/26",">0.5%","GOOD"),
 # ---------------- SPENDING (w=1) ----------------
 ("Spending","US","Building Permits MoM Final","5.0%","-2.6%","Jul/26",">0.5%","GOOD"),
 ("Spending","US","Retail Sales YoY","5.0%","6.8%","Jul/26",">0.5%","GOOD"),
 ("Spending","US","CB Consumer Confidence","89.4","90.2","Aug/26",">Prev","BAD"),
 ("Spending","US","Personal Spending MoM","0.2%","0.3%","Jul/26","0-0.5%","NEUTRAL"),
 ("Spending","EA","Retail Sales YoY","0.7%","1.9%","Jun/26",">0.5%","GOOD"),
 ("Spending","EA","Consumer Confidence Final","-15.9","-17.6","Jul/26",">Prev","GOOD"),
 ("Spending","GB","GfK Consumer Confidence","-14","-17","Aug/26",">Prev","GOOD"),
 ("Spending","GB","Retail Sales Ex Fuel YoY","2.3%","5.0%","Jul/26",">0.5%","GOOD"),
 ("Spending","JP","Household Spending YoY","-3.3%","-0.4%","Jun/26","<0%","BAD"),
 ("Spending","JP","Consumer Confidence","34.9","33.8","Jul/26",">Prev","GOOD"),
 ("Spending","JP","Retail Sales YoY","0.5%","5.0%","Jun/26","0-0.5%","NEUTRAL"),
 ("Spending","AU","Household Spending YoY","7.0%","6.0%","Jul/26",">0.5%","GOOD"),
 ("Spending","AU","Building Permits YoY Final","8.9%","5.5%","Jun/26",">0.5%","GOOD"),
 ("Spending","AU","Westpac Consumer Conf Change","6.0%","4.1%","Aug/26",">Prev","GOOD"),
 ("Spending","AU","NAB Business Confidence","-6","-6","Jul/26",">Prev","NEUTRAL"),
 ("Spending","NZ","Building Permits MoM","-3.6%","-4.9%","Jun/26","<0%","BAD"),
 ("Spending","NZ","Electronic Retail Card Spending YoY","3.4%","1.3%","Jul/26",">0.5%","GOOD"),
 ("Spending","NZ","ANZ Business Confidence","56.1","36.6","Jul/26",">Prev","GOOD"),
 ("Spending","NZ","ANZ Roy Morgan Consumer Conf","99.3","91.3","Jul/26",">Prev","GOOD"),
 ("Spending","CA","Retail Sales YoY","5.2%","5.9%","Jun/26",">0.5%","GOOD"),
 ("Spending","CA","Building Permits MoM","+18.5%","-3.0%","Jun/26",">0.5%","GOOD"),
 ("Spending","CH","Consumer Confidence","-35","-36","Jul/26",">Prev","GOOD"),
 ("Spending","CH","Retail Sales YoY","1.5%","3.4%","Jun/26",">0.5%","GOOD"),
 # ---------------- TRADE (w=1) ----------------
 ("Trade","US","Balance of Trade","-$73.26B","-$77.65B","Jun/26",">Prev","GOOD"),
 ("Trade","EA","Balance of Trade","EUR8.60B","EUR-9.00B","Jun/26",">Prev","GOOD"),
 ("Trade","GB","Balance of Trade","GBP-5.54B","GBP-3.46B","Jun/26","<Prev","BAD"),
 ("Trade","JP","Balance of Trade","JPY-634.5B","JPY-409.9B","Jul/26","<Prev","BAD"),
 ("Trade","AU","Balance of Trade","A$1.93B","A$-2.37B","Jun/26",">Prev","GOOD"),
 ("Trade","NZ","Balance of Trade","NZ$-1.95B","NZ$0.02B","Jul/26","<Prev","BAD"),
 ("Trade","CA","Balance of Trade","C$3.86B","C$3.70B","Jun/26",">Prev","GOOD"),
 ("Trade","CH","Balance of Trade","CHF8.1B","CHF3.8B","Jul/26",">Prev","GOOD"),
 # ---------------- EMPLOYMENT (w=2) ----------------
 ("Employment","US","Non Farm Payrolls","-23K","20K","Jul/26",">Cons","BAD"),
 ("Employment","US","Unemployment Rate","4.1%","4.2%","Jul/26","<Prev","GOOD"),
 ("Employment","EA","Unemployment Rate","6.3%","6.3%","Jun/26","unchanged","NEUTRAL"),
 ("Employment","GB","Claimant Count Change","-11K","-6.4K","Jul/26","<0 (LD-58)","GOOD"),
 ("Employment","JP","Unemployment Rate","2.5%","2.5%","Jun/26","unchanged","NEUTRAL"),
 ("Employment","AU","ANZ-Indeed Job Ads MoM","+0.8%","-0.1%","Jul/26",">0.5%","GOOD"),
 ("Employment","AU","Employment Change","-15.8K (FT +16.3K, PT -32.2K)","76.3K (FT +29.3K, PT +47.0K)","Jul/26","hdl BAD; FT NEUTRAL (LD-57); PT GOOD","NEUTRAL"),
 ("Employment","AU","Unemployment Rate","4.5%","4.4%","Jul/26",">Prev","BAD"),
 ("Employment","NZ","Unemployment Rate","5.6%","5.4%","Jun/26",">Prev","BAD"),
 ("Employment","CA","Unemployment Rate","6.4%","6.5%","Jul/26","<Prev","GOOD"),
 ("Employment","CA","Employment Change","75.1K (FT +38.6K, PT +36.6K)","18.2K","Jul/26","hdl>0 GOOD; FT (LD-57) needs Jun split NOT SOURCED","GOOD"),
 ("Employment","CH","Non Farm Payrolls","5.698M","5.537M","Q2/26",">Cons 5.4M","GOOD"),
 ("Employment","CH","Unemployment Rate","3.0%","2.9%","Jul/26",">Prev","BAD"),
 # ---------------- INFLATION (w=3) ----------------
 ("Inflation","US","Inflation Rate YoY","3.4%","3.5%","Jul/26",">2% & falling","NEUTRAL"),
 ("Inflation","EA","Inflation Rate YoY Final","2.9%","2.8%","Jul/26",">2% & rising","GOOD"),
 ("Inflation","GB","Inflation Rate YoY","2.9%","2.6%","Jul/26",">2% & rising","GOOD"),
 ("Inflation","JP","Inflation Rate YoY","1.9%","1.6%","Jul/26","<2% & rising","NEUTRAL"),
 ("Inflation","AU","Inflation Rate YoY","3.5%","3.8%","Jul/26",">2% & falling","NEUTRAL"),
 ("Inflation","NZ","Inflation Rate YoY","4.1%","3.1%","Jun/26",">2% & rising","GOOD"),
 ("Inflation","CA","Inflation Rate YoY","3.0%","2.8%","Jul/26",">2% & rising","GOOD"),
 ("Inflation","CH","Inflation Rate YoY","0.4%","0.5%","Jul/26","<2% & falling","BAD"),
]

CCYS = ["US","EA","GB","JP","AU","NZ","CA","CH"]
LABEL = {"US":"USD","EA":"EUR","GB":"GBP","JP":"JPY","AU":"AUD","NZ":"NZD","CA":"CAD","CH":"CHF"}

# LD-57 - FULL TIME EMPLOYMENT CHANGE, Jeff's rule, 2026-08-24.
# Applies to AUD and CAD, the two currencies whose Employment Change the
# whitelist source scores as a composite "with more weight to Full Time".
#
# WHY IT CHANGED: the previous test was a bare "Actual > Previous", which
# graded a POSITIVE full-time month BAD merely for growing more slowly than
# the month before (+16.3K after +29.3K -> BAD). Jeff: full-time growth that
# decelerates is not the same as full-time contraction, and the model should
# not call it that.
#
#   a) Actual > 0 and Actual >= Previous -> GOOD     growth, holding or better
#   b) Actual > 0 and Actual <  Previous -> NEUTRAL  growth, but slowing
#   c) Actual < 0 and Actual <= Previous -> BAD      contraction, no better
#   d) Actual < 0 and Actual >  Previous -> NEUTRAL  contraction, but easing
#   e) Actual = 0                        -> NEUTRAL  (Jeff's call - zero is
#      neither growth nor contraction, and every >Prev test in the whitelist
#      source already reads "No change is Neutral")
#
# FULL TIME STILL CARRIES MORE WEIGHT than the headline or part-time legs -
# that is unchanged from the source and from LD-56.
def full_time_grade(actual, previous):
    """Grade a Full Time Employment Change print. Returns GOOD/NEUTRAL/BAD."""
    if actual is None or previous is None:
        return None                      # un-runnable; publish as NOT SOURCED
    if actual == 0:
        return "NEUTRAL"
    if actual > 0:
        return "GOOD" if actual >= previous else "NEUTRAL"
    return "BAD" if actual <= previous else "NEUTRAL"


# LD-58 - CLAIMANT COUNT CHANGE, Jeff's rule, 2026-08-24. GBP only.
#
# The series measures the CHANGE in people claiming unemployment benefit, so
# NEGATIVE means fewer claimants and an IMPROVING labour market. The sign is
# the signal; the prior month is not.
#
#   Actual > 0 -> BAD      more claimants
#   Actual < 0 -> GOOD     fewer claimants
#   Actual = 0 -> NEUTRAL  no change
#
# WHY IT CHANGED: the previous test was "Actual < Previous", which produced
# two backwards readings. Claimants falling 2K after falling 11K scored BAD -
# the labour market improved and the model called it bad. Claimants RISING 5K
# after rising 20K scored GOOD - the market deteriorated and the model called
# it good. A change series has to be read against ZERO, not against its own
# prior change.
def claimant_grade(actual):
    """Grade a Claimant Count Change print. Returns GOOD/NEUTRAL/BAD."""
    if actual is None:
        return None
    if actual == 0:
        return "NEUTRAL"
    return "GOOD" if actual < 0 else "BAD"


def compute(include_rate=True):
    """Five scored categories plus Interest Rate (LD-23, weight 3) when
    include_rate is True. Rate scores come from pipelines/rate_model.py, which
    scores inflation-vs-own-mandate only - see that file for why steps 2-4
    (priced odds, vote splits, forward paths) were rejected."""
    from collections import defaultdict
    by = defaultdict(list)
    for r in ROWS:
        by[(r[0], r[1])].append(r)
    cat_score, totals, detail = {}, {}, {}
    for ccy in CCYS:
        tot = 0.0
        for cat, w in W.items():
            rows = by[(cat, ccy)]
            n = len(rows)
            if n == 0:
                cat_score[(cat, ccy)] = (0.0, 0, 0)
                continue
            per = w / n
            s = 0.0
            scored = 0
            for r in rows:
                v = r[7]
                if v == "GOOD":
                    s += per; scored += 1
                elif v == "BAD":
                    s -= per; scored += 1
                elif v == "NEUTRAL":
                    scored += 1
            cat_score[(cat, ccy)] = (s, n, scored)
            tot += s
        if include_rate:
            try:
                from rate_model import compute as _rate
                r = _rate().get(ccy)
                if r:
                    cat_score[("Rate", ccy)] = (r["score"], 1, 1)
                    tot += r["score"]
            except ImportError:
                pass
        totals[ccy] = tot
    return cat_score, totals
