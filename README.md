# IDX 5% Ownership Analysis

A Python and PostgreSQL project for analyzing changes in shareholdings among shareholders who own 5% or more of companies listed on the Indonesia Stock Exchange (IDX).

## Data Source

Data is sourced from the official Indonesia Stock Exchange (IDX) website:

[IDX Share Ownership Data](https://www.idx.co.id/id/perusahaan-tercatat/data-kepemilikan-saham/)

## Pipeline

1. `clean_ksei.py` cleans raw Excel files and converts ownership data into a long format.
2. `load_database.py` registers new tickers and loads ownership records into PostgreSQL. Loading skips snapshot dates already in the database, making the process safe to rerun.
3. `main.py` processes every matching file in `data/` in a single run. Each file is processed independently: if a file fails, only that file's transaction is rolled back. The pipeline then reports a summary of successfully loaded and failed files.

## Schema Design

The database consists of three tables:

- `stocks` — stores IDX tickers and company names.
- `sectors` — stores industry groupings for future use.
- `ownership_snapshots` — stores shareholder-account holdings and ownership percentages for each snapshot date.

### Key Design Decisions

**Long format over wide format.**

The raw files contain a separate set of columns for each snapshot date. Reshaping the data into one row per holder and snapshot date means that new snapshots only add rows, without requiring schema changes or rewritten queries.

**Surrogate key instead of a natural key.**

Investors may hold shares through multiple broker accounts, and the source data does not always provide enough information to uniquely identify each record. Therefore, `ownership_snapshots` uses a `SERIAL` primary key instead of relying on a natural key.

**Granular storage, aggregation via query.**

Raw per-account holdings are stored in the database. Ownership totals and period-over-period changes are calculated at query time using SQL aggregation (`GROUP BY`, `SUM`) and window functions (`LAG()`).

## Setup

1. Create a PostgreSQL database and run `schema/01_schema.sql`.
2. Create a `.env` file containing your database credentials (see `.env.example`).
3. Install the required Python dependencies:

   ```bash
   pip install pandas openpyxl psycopg2-binary python-dotenv
   ```

4. Place the disclosure files in `data/`.
5. Run the pipeline:

   ```bash
   cd scripts && python main.py
   ```

## Example Query

`queries/01_ownership_changes.sql` identifies investors whose ownership stakes have changed significantly between snapshot dates. It uses the `LAG()` window function to compare ownership across periods rather than relying on a static change column.

The results update automatically as new snapshots are loaded into the database.

## Known Limitations

- Files must follow the `peng-...-lima-persen.xlsx` naming pattern to be processed.
- The pipeline currently runs manually; automated scheduling is planned for a future extension.

## Tools Used

- **Python** — data processing and pipeline orchestration.
- **pandas** — data cleaning and transformation.
- **openpyxl** — Excel file handling.
- **PostgreSQL** — relational database for storing ownership records.
- **psycopg2** — Python–PostgreSQL connectivity.
- **pgAdmin** — database management and administration.