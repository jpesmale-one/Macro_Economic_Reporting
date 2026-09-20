# Rows recovered from the TE INDICATOR page, not the calendar

R-42 (`capture_gap.py`) lists every whitelist row that printed while no capture
could see it. Those rows can never be recovered from the calendar — TE's
rolling window has moved past them — so R-42 would keep reporting them forever
even after the value is safely in the fact table.

This ledger records the ones that have been recovered and from where, so R-42
can separate **still outstanding** from **already dealt with**. A row listed
here is not a gap any more; it is a gap that was closed by hand.

Format: `CCY | ROW | scheduled | actual | source URL`

Jeff, 2026-09-13: *"we cannot afford to have dirty data as we're doing
forecasting. We need to be accurate on the pulls"*

---

GBP | Industrial Production YoY | 2026-09-11 | 0.6% | https://tradingeconomics.com/united-kingdom/industrial-production
GBP | Manufacturing Production YoY | 2026-09-11 | 2.6% | https://tradingeconomics.com/united-kingdom/manufacturing-production
GBP | Balance of Trade | 2026-09-11 | GBP-3.45B | https://tradingeconomics.com/united-kingdom/balance-of-trade
USD | Inflation Rate YoY | 2026-09-11 | 3.4% | https://tradingeconomics.com/united-states/inflation-cpi
JPY | Household Spending YoY | 2026-09-05 | -3.6% | https://tradingeconomics.com/japan/household-spending

<!-- RECORDED 2026-09-21. These rows printed inside 14-18 Sep, were recovered
     from TE indicator pages during that week's corrections, and are already
     applied to the fact tables - but were never written here, so R-42 kept
     reporting them as outstanding. A ledger only closes a gap if the entry
     is actually made; leaving it out is how a guard learns to cry wolf. -->
CAD | Inflation Rate YoY | 2026-09-14 | 3% | https://tradingeconomics.com/canada/inflation-cpi
CHF | Consumer Confidence | 2026-09-14 | -33 | https://tradingeconomics.com/switzerland/consumer-confidence
EUR | Balance of Trade | 2026-09-15 | EUR14.2B | https://tradingeconomics.com/euro-area/balance-of-trade
GBP | Claimant Count Change | 2026-09-15 | 27.8K | https://tradingeconomics.com/united-kingdom/claimant-count-change
GBP | Inflation Rate YoY | 2026-09-16 | 3.1% | https://tradingeconomics.com/united-kingdom/inflation-cpi
JPY | Industrial Production YoY Final | 2026-09-14 | 3.9% | https://tradingeconomics.com/japan/industrial-production
JPY | Industrial Production YoY Final | 2026-09-15 | 3.9% | https://tradingeconomics.com/japan/industrial-production
NZD | Business NZ PMI | 2026-09-14 | 53.1 | https://tradingeconomics.com/new-zealand/manufacturing-pmi
NZD | Electronic Retail Card Spending YoY | 2026-09-14 | 0.2% | https://tradingeconomics.com/new-zealand/retail-sales-annual
NZD | Electronic Retail Card Spending YoY | 2026-09-15 | 0.2% | https://tradingeconomics.com/new-zealand/retail-sales-annual
NZD | Global Dairy Trade Price Index | 2026-09-15 | -1.1% | https://tradingeconomics.com/new-zealand/global-dairy-trade-price-index
USD | Retail Sales YoY | 2026-09-16 | 6% | https://tradingeconomics.com/united-states/retail-sales-annual
