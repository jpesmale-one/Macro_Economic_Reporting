# Fetching sources that reject default headers

**A 4xx from a plain fetch is not proof a source is closed.** Several sources
in this project return 403/418 to a bare request and 200 to an ordinary
browser request. Established 2026-08-19 (F-6) after `rba.gov.au`,
`rbnz.govt.nz` and `snb.ch` were wrongly reported as blocking automated
access across five revisions.

## The escalation ladder

Try in order; stop at the first that returns 200 **with a body** (check the
size, not just the status — RBA returns 200 to a HEAD and 403 to a GET).

**1. WebFetch** — fine for most sites. If it returns 403/418/451, go to 2.

**2. curl with browser headers.**

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

curl -s --compressed --max-time 25 \
  -H "User-Agent: $UA" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Sec-Fetch-Dest: document" \
  -H "Sec-Fetch-Mode: navigate" \
  -H "Upgrade-Insecure-Requests: 1" \
  "$URL"
```

**3. Add a `Referer`.** Some hosts reject requests with no referrer chain:

```bash
  -H "Referer: https://www.google.com/"
  -H "Sec-Fetch-Site: cross-site"
```

RBA needs this. Without it: 403. With it: 200.

**4. Add an API-style `Accept` + the site's own page as `Referer`** for JSON
endpoints:

```bash
  -H "Accept: application/json, text/plain, */*"
  -H "Referer: https://<the site's own article page>"
```

CNN's fear-and-greed endpoint needs this.

## Confirmed working (2026-08-19)

| Source | Needs | Result |
|---|---|---|
| `federalreserve.gov` | nothing | 200 on plain WebFetch |
| `rbnz.govt.nz` | browser headers | 200 — OCR + next-update date |
| `snb.ch` | browser headers | 200 — policy rate + SARON |
| `rba.gov.au` | browser headers **+ Referer** | 200 — full cash-rate table |
| `production.dataviz.cnn.io` | browser headers + Referer | 200 — index + 7 components |

## The rule

**Before writing that a source is unavailable, run the ladder and say which
step failed.** "Blocked" is an absence-type claim and carries the same
evidentiary burden as any must-NOT row: name what was tried. A source
recorded as blocked gets skipped on every future run, so a wrong entry here
removes a primary source permanently and silently.
