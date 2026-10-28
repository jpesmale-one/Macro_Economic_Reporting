# -*- coding: utf-8 -*-
"""Pull daily bars for the LD-174 risk-tone index legs, over CDP.

Same mechanism as pull_yields_cdp.py - same chart, same TradingView, and
nothing but a summary line reaches the conversation.

LD-5 AS AMENDED: TradingView is the authority. Yahoo is NEVER a fallback.
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
import risk_index as RI

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
    """Bars for one symbol, or None. The symbol guard is not optional:
    setSymbol is async, so a read can return the PREVIOUS instrument's bars
    and they would be filed under the new key."""
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
        b = [x for x in d['bars'] if len(x) >= 5]
        if len(b) >= 60:
            return b
    return None


def main():
    want = [a.upper() for a in sys.argv[1:]]
    todo = [s for s in RI.SERIES if not want or s[0] in want]
    pg = Page()
    ok = 0
    try:
        for key, sym, name, region, inv in todo:
            print('%-6s %-12s' % (key, sym), end=' ')
            sys.stdout.flush()
            try:
                bars = pull(pg, sym)
                if not bars:
                    print('NO DATA')
                    continue
                rows = [{'time': int(x[0]), 'open': x[1], 'high': x[2],
                         'low': x[3], 'close': x[4]} for x in bars]
                n = RI.save(key, sym, rows,
                            'inverted - a RISE is risk-off' if inv else '')
                d = RI.load(key)
                print('%d bars, latest %s close %.2f'
                      % (n, d['bars'][-1]['session'],
                         d['bars'][-1]['close']))
                ok += 1
            except Exception as e:
                print('ERR %s' % str(e)[:110])
    finally:
        pg.close()
    print()
    for key, sym, n, last in RI.status():
        print('  %-6s %-12s %5d bars  latest %s' % (key, sym, n, last))
    return 0 if ok == len(todo) else 1


if __name__ == '__main__':
    sys.exit(main())
