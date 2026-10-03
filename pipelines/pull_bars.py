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


SETUP = """(function(){
  var c = window.TradingViewApi.activeChart();
  c.setSymbol('OANDA:%s');
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
        bars = [b for b in d['bars'] if len(b) >= 5]
        if len(bars) >= 60:
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
