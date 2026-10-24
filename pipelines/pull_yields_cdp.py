# -*- coding: utf-8 -*-
"""Pull daily 2-YEAR GOVERNMENT YIELD bars for all eight, straight over CDP.

Same mechanism as pull_bars.py - same chart, same TradingView, nothing in
the conversation but the summary line. The only difference is the symbol
prefix: TVC: rather than OANDA:, because these are vendor yield series and
not broker FX feeds.

LD-5 AS AMENDED: TradingView is the authority. Yahoo is NEVER a fallback -
if TradingView will not start, say so and stop.
LD-171: this WRITES DATA AND NOTHING ELSE. No board reads it. F-3 - adding
it to the indicator set is Jeff's call alone.

Usage:  python pull_yields_cdp.py            (all eight)
        python pull_yields_cdp.py USD EUR    (named only)
"""
import json
import os
import ssl
import sys
import time
import urllib.request

from websocket import create_connection

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pull_yields as py

CDP = 'http://127.0.0.1:9222/json/list'


def chart_ws():
    tabs = json.loads(urllib.request.urlopen(CDP, timeout=5).read())
    for t in tabs:
        if '/chart/' in (t.get('url') or ''):
            return t['webSocketDebuggerUrl']
    raise SystemExit('no chart tab open - launch TradingView first')


class Page(object):
    def __init__(self):
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


SETUP = """(function(){
  var c = window.TradingViewApi.activeChart();
  c.setSymbol('%s');
  c.setResolution('1D');
  return 'ok';
})()"""

READ = """(function(){
  try{
    var c = window.TradingViewApi.activeChart();
    if (c.getSeries().isLoading()) return 'LOADING';
    var sym = String(c.symbol()||'');
    var d = c.getSeries().data();
    var out = [];
    d.each(function(i,b){ out.push(b); return false; });
    return JSON.stringify({sym: sym, n: out.length, bars: out.slice(-%d)});
  }catch(e){ return 'T '+String(e); }
})()"""


def pull(pg, symbol, want=400, tries=14):
    """[[epoch,o,h,l,c], ...] for one TVC symbol, or None.

    The symbol guard matters: setSymbol is async, so a read can return the
    PREVIOUS instrument's bars and they would be filed under the new
    currency. Checking the ticker the chart reports is what prevents a
    silent cross-contamination - the same failure shape as the five stale
    files that quietly shrank breadth in R-50.
    """
    tick = symbol.split(':')[-1].upper()
    pg.ev(SETUP % symbol)
    for _ in range(tries):
        time.sleep(2.5)
        raw = pg.ev(READ % want)
        if not raw or raw == 'LOADING' or str(raw).startswith('T '):
            continue
        d = json.loads(raw)
        if tick not in (d.get('sym') or '').upper().replace(':', ''):
            continue
        bars = [b for b in d['bars'] if len(b) >= 5]
        if len(bars) >= 60:
            return bars
    return None


def main():
    want = [a.upper() for a in sys.argv[1:]]
    todo = [s for s in py.SYMBOLS if not want or s[0] in want]
    if not todo:
        print(__doc__)
        return 2
    pg = Page()
    ok = 0
    try:
        for ccy, sym, desc, note in todo:
            print('%-4s %-12s' % (ccy, sym), end=' ')
            sys.stdout.flush()
            try:
                bars = pull(pg, sym)
                if not bars:
                    print('NO DATA')
                    continue
                rows = [{'time': int(b[0]), 'open': b[1], 'high': b[2],
                         'low': b[3], 'close': b[4]} for b in bars]
                n = py.save(ccy, sym, rows, note)
                d = py.load(ccy)
                print('%d bars, latest %s close %.3f%s'
                      % (n, d['bars'][-1]['session'], d['bars'][-1]['close'],
                         '  [PROXY]' if note else ''))
                ok += 1
            except Exception as e:
                print('ERR %s' % str(e)[:110])
    finally:
        pg.close()
    print()
    print(py.report())
    return 0 if ok == len(todo) else 1


if __name__ == '__main__':
    sys.exit(main())
