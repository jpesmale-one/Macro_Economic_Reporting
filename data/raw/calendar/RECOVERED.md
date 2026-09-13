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
