-- IDX Ownership Change Analyzer — Schema

CREATE TABLE sectors (
    sector_id SERIAL PRIMARY KEY,
    sector_name TEXT UNIQUE NOT NULL
);

CREATE TABLE stocks (
    ticker TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    sector_id INT REFERENCES sectors(sector_id)
);

CREATE TABLE ownership_snapshots (
    id SERIAL PRIMARY KEY,
    ticker TEXT REFERENCES stocks(ticker),
    holder_name TEXT,
    custodian TEXT,
    account_name TEXT,
    nationality TEXT,
    domicile TEXT,
    status_local_foreign TEXT,
    shares_held BIGINT,
    combined_shares_per_investor BIGINT,
    ownership_pct NUMERIC,
    snapshot_date DATE
);
