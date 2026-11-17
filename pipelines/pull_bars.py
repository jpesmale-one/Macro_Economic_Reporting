# -*- coding: utf-8 -*-
"""Pull a year of OANDA DAILY bars per pair, straight over CDP.

Same chart the MCP drives, same TradingView, same OANDA feed (LD-5 as
amended, F-137 - Yahoo is never a fallback). Driving it from a script keeps
260 bars x N pairs out of the conversation; only the numbers land on disk.

exportData() is disabled in the desktop build ("Data export is not
supported"), so this reads the series' own store via data().each().

Usage:  python pull_bars.py GBPAUD EURAUD AUDJPY ...
Writes <PAIR>.txt as "epoch open high low close", oldest first.
"""
import json
import os
import ssl
import sys
import time
import urllib.request

from websocket import create_connection

HERE = os.path.dirname(os.path.abspath(__file__))
CDP = 'http://127.0.0.1:9222/json/list'


def chart_ws():
    tabs = json.loads(urllib.request.urlopen(CDP, timeout=5).read())
    for t in tabs:
        if '/chart/' in (t.get('url') or ''):
            return t['webSocketDebuggerUrl']
    raise SystemExit('no chart tab open - launch TradingView first')


class Page(object):
    def __init__(self):
        # CDP 403s a handshake carrying an Origin it was not told to allow.
        # We are not a browser page, so send none.
        self.ws = create_connection(chart_ws(), timeout=40,
                                    suppress_origin=True,
                                    sslopt={'cert_reqs': ssl.CERT_NONE})
        self.n = 0

    def ev(self, expr):
        self.n += 1
        self.ws.send(json.dumps({
            'id': self.n, 'method': 'Runtime.evaluate',
            'params': {'expression': expr, 'returnByValue': True,
                       'awaitPromise': True}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == self.n:
                r = m.get('result', {})
                if 'exceptionDetails' in r:
                    raise RuntimeError(str(r['exceptionDetails'])[:200])
                return r.get('result', {}).get('value')

    def close(self):
        self.ws.close()


# *** F-190 - A WEDGED BRIDGE SERVED HEIKIN-ASHI-SHAPED BARS AS PRICE.
#
# A full 28-pair pull wrote bars whose OPEN had been replaced by a 16-digit
# float that usually equalled the bar's own LOW: 3667 of 8400 (44%) against
# 122 in the committed baseline. The HIGH was untouched.
#
# The opens are exactly ha_open = (prev_ha_open + prev_ha_close)/2 -
# reconstructing that recurrence from the clean candles reproduced them to
# all 16 digits on both dates tested.
#
# *** BUT THE CHART'S STYLE WAS NOT THE CAUSE, AND THE OBVIOUS READING OF
# THAT MATCH IS WRONG. Tested directly: with the chart deliberately set to
# Heikin-Ashi (chartType 8), this puller returned 1 of 300 open==extreme -
# clean candles. getSeries().data() reads the SERIES STORE, which holds real
# OHLC; HA is a rendering layer over it. The match proved only that the bad
# opens were HA-SHAPED, which is computable from the same candles - not that
# the chart was serving HA. Two different claims.
#
# The cause is the wedged bridge. In that state quote_get returned
# BYTE-IDENTICAL payloads for OANDA:GBPNZD and TVC:VIX, both with open==low
# at 16 digits and description/exchange/type absent: one stale series,
# smoothed, relabelled per symbol. The restart fixed it; a chart-style
# change does not reproduce it.
#
# WHY IT MATTERED: a smoothed open sits inside the prior range, so a LONG's
# adverse excursion largely disappears. Regrading 2-6 Nov on those bars
# flipped FOUR of ten session states - two BEATEN became CLEAN/DRIFT - and
# lifted the set ratio from 1.98 to 2.36. Internally consistent and wrong
# (F-130).
#
# No gate caught it: F-188 and R-50 both passed, the bars were present and
# nothing errored. The style check below is kept anyway - it is nearly free
# and closes a real hole for Renko/Kagi/LineBreak, which DO change the store
# - but the defence that actually matters is the two-symbol distinctness
# probe before trusting any pull.
SETUP = """(function(){
  var c = window.TradingViewApi.activeChart();
  c.setSymbol('OANDA:%s');
  c.setResolution('1D');
  try{ c.setChartType(1); }catch(e){}   /* 1 = candles, never HA/Renko */
  return 'ok';
})()"""

READ = """(function(){
  try{
    var c = window.TradingViewApi.activeChart();
    if (c.getSeries().isLoading()) return 'LOADING';
    var sym = String(c.symbol()||'');
    var sty = null;
    try{ sty = c.getChartType(); }catch(e){}   /* F-190 - style travels with the bars */
    var d = c.getSeries().data();
    var out = [];
    d.each(function(i,b){ out.push(b); return false; });
    return JSON.stringify({sym: sym, style: sty, n: out.length,
                           bars: out.slice(-%d)});
  }catch(e){ return 'T '+String(e); }
})()"""


def pull(pg, pair, want=400, tries=14):
    pg.ev(SETUP % pair)
    for _ in range(tries):
        time.sleep(2.5)
        raw = pg.ev(READ % want)
        if not raw or raw == 'LOADING' or str(raw).startswith('T '):
            continue
        d = json.loads(raw)
        if pair not in (d.get('sym') or '').replace(':', ''):
            continue                      # still showing the previous symbol
        # *** F-190 - REFUSE ANY STYLE BUT CANDLES. A non-candle series is
        # not price: Heikin-Ashi once wrote 44% of bars with a recomputed
        # open and silently flipped four session verdicts. Returning None
        # here prints NO DATA, which is survivable; writing HA is not.
        sty = d.get('style')
        if sty is not None and sty != 1:
            print('   %s *** CHART STYLE %s, NOT CANDLES - REFUSED (F-190)'
                  % (pair, sty))
            return None
        bars = [b for b in d['bars'] if len(b) >= 5]
        if len(bars) >= 60:
            # *** F-190 - THE CHECK THAT WOULD HAVE CAUGHT IT.
            # Real OANDA opens rarely equal the bar's own extreme: the
            # committed baseline runs ~1-2%. A smoothed/synthesised open
            # ran 44%. This asks the BARS, not the bridge, so it holds
            # whatever the feed claims about itself.
            n = len(bars)
            ext = sum(1 for b in bars
                      if float(b[1]) == float(b[3])
                      or float(b[1]) == float(b[2]))
            if ext * 100 >= n * 20:       # 20% - far above noise, far below 44
                print('   %s *** %d%% of opens equal an extreme - NOT RAW '
                      'PRICE, REFUSED (F-190)' % (pair, ext * 100 // n))
                return None
            return bars
    return None


def main():
    pairs = [p.upper() for p in sys.argv[1:]]
    if not pairs:
        print(__doc__)
        return 2
    pg = Page()
    try:
        for p in pairs:
            print('%-8s' % p, end=' ')
            sys.stdout.flush()
            try:
                bars = pull(pg, p)
                if not bars:
                    print('NO DATA')
                    continue
                lines = ['%d %s %s %s %s' % (int(b[0]), b[1], b[2], b[3], b[4])
                         for b in bars]
                with open(os.path.join(HERE, '%s.txt' % p), 'w') as f:
                    f.write('\n'.join(lines) + '\n')
                print('%d bars' % len(lines))
            except Exception as e:
                print('ERR %s' % str(e)[:110])
    finally:
        pg.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
