---
license: cc-by-4.0
language:
  - en
tags:
  - finance
  - cryptocurrency
  - stablecoins
  - interest-rates
  - time-series
pretty_name: Stablecoin Flexible Yield Rates, with Venue Safety Grades
size_categories:
  - 1K<n<10K
configs:
  - config_name: default
    data_files: stablecoin_flexible_rates.csv
---

# Stablecoin flexible yield rates, with venue safety grades

A daily record of what centralised crypto venues actually pay on stablecoins,
collected by [YieldScope](https://yieldscope.io) and published with the safety
grade of the venue paying each rate.

The grade is the part you will not find in other rate datasets, and it is the
reason this one is worth joining against.

## What is in it

| | |
|---|---|
| Rows | 1,661 |
| Venue-asset pairs | 50 |
| Venues | 20 |
| Assets | DAI, FDUSD, PYUSD, TUSD, USD1, USDC, USDE, USDT |
| Period | 2026-05-25 → 2026-07-28 (53 days) |

### Columns

| Column | Meaning |
|---|---|
| `date` | Snapshot date, `YYYY-MM-DD` |
| `platform` | Venue display name |
| `platform_slug` | Stable identifier for joins |
| `asset` | Stablecoin ticker |
| `apy_percent` | Base flexible APY, in percent |
| `safety_grade` | `A`–`F`, see below |

## What `safety_grade` means

Each venue is assessed on five binary checks:

1. **Regulation** — licensed by a major regulator
2. **Proof of reserves** — publishes attested reserves
3. **Flexible withdrawal** — funds are withdrawable without a lock
4. **Insurance fund** — a named, quantified fund covering custodied assets
5. **Track record** — no major loss-of-funds incident

The grade is the count of checks passed: `A` = 5, `B` = 4, `C` = 3, `D` = 2,
`F` = 1 or 0. Each check on the site carries a written justification and a
link to its source.

## What these rates are, and are not

**Base rates only.** These are what an ordinary balance earns. They are not
the advertised headline, which is usually a promotional tier that applies to
the first few hundred dollars, or a loyalty tier that requires holding the
venue's own token.

The gap is large enough to matter. One venue in this period advertised 10% on
a coin where the rate applied to the first $15 of a deposit. Another advertised
99.99%, applying to the first $101. Datasets built from marketing pages inherit
those numbers; this one does not.

**Flexible products only.** Fixed-term and locked products are excluded, so
every row is comparable: money you can withdraw.

## A caveat worth reading before you model on this

Rates in this file are the base rates *as we published them on that date*, and
our methodology changed once inside the window. Around 28–30 June 2026 we moved
several venues from advertised tiers to true base rates. In the series that
shows up as a one-day cliff — CoinEx USDT reads 13.21% on 29 June and 3.41% on
30 June, for instance.

That is a change in what we measured, not a change in what the market paid.
Anyone computing rate volatility or drawdowns across that boundary will find a
market event that did not happen. Series after 30 June are consistent.

## Scope

This is a deliberately narrow cut of a larger archive: stablecoins only,
flexible only, one asset class. Borrow rates, perp funding, non-stablecoin
yields and the venues covered only in the private archive are not included.

## Licence and attribution

CC BY 4.0. Free to use, including commercially, with attribution to
[yieldscope.io](https://yieldscope.io).

Live rates across 37 venues, updated daily, are at
[yieldscope.io](https://yieldscope.io); a JSON feed of the current snapshot is
at [/api/rates.json](https://yieldscope.io/api/rates.json) — no key, CORS open.

## Not financial advice

Rates float and terms change. A grade is a summary of five checks, not a
guarantee, and no grade makes a deposit safe.
