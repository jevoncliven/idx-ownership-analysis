# IDX 5% Ownership Analysis


## Overview
The purpose of this project is to filter and analyze changes in shareholdings among shareholders who hold 5% or more of a company's shares.
Understanding significant shareholder movements can help investors identify changes in ownership structure and potential shifts in corporate control.


## Data Source
The data is sourced from the official Indonesia Stock Exchange (IDX) website:
https://www.idx.co.id/id/perusahaan-tercatat/data-kepemilikan-saham/

The data is updated daily from Monday to Friday, excluding non-operational days.


## Schema Design

Three tables:
- `stocks` — 833 real IDX tickers and company names
- `sectors` — industry groupings (created for future use; not currently
  populated, since sector classification wasn't available in this data source)
- `ownership_snapshots` — 6,146 rows, one per shareholder-account holding
  per snapshot date


### Key design decisions

**Long format over wide format.**
The raw file stores each snapshot date as its own set of columns
(`saham_02jul`, `saham_03jul`, etc.). This was reshaped into long format —
one row per (holder, date), with a single `snapshot_date` column — so that
adding a new month's data later only requires inserting new rows, not
altering the table structure or rewriting existing queries.

**Surrogate key instead of a natural composite key.**
`(ticker, holder_name)` looked unique at first, but investors often hold
the same stock through multiple broker accounts, so that combination
wasn't. Adding `(custodian, account_name)` narrowed it further, but a
small number of rows (~85) still had identical values across every
descriptive column, just different share counts — likely unlabeled
sub-accounts the source data doesn't distinguish. Since no combination of
real columns was reliably unique, `ownership_snapshots` uses a `SERIAL`
surrogate key instead of forcing a natural key the data doesn't support.

**Granular storage, aggregation via query.**
The table stores raw per-account holdings rather than pre-computed totals
or percentage changes. Metrics like total ownership per investor or
period-over-period change are computed at query time with SQL (`GROUP BY`
+ `SUM`, and `LAG()` window functions), so the same stored data can answer
multiple questions without needing to be reshaped or recomputed.

## Setup
1. Create a PostgreSQL database
2. Run the schema files in order:
   - `schema/01_schema.sql` — creates the 3 tables
   - `schema/02_stocks.sql` — inserts all 833 tickers
   - `schema/03_ownership.sql` — inserts the 6,146 ownership rows
3. Run queries from the `queries/` folder against the loaded database

## Example Query
`queries/01_ownership_changes.sql` — identifies which investors
significantly changed their stake in a stock between the two snapshot
dates, computed via a `LAG()` window function rather than relying on a
static "change" column. Works automatically as more snapshot dates are
added over time.

## Tools Used
PostgreSQL, Python (pandas) for data cleaning, pgAdmin for query
development.
