import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

#connect to database
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

#used to insert the list of tickers to database
def register_new_stocks(df, conn):
    unique_stocks = df[['ticker', 'company_name']].drop_duplicates(subset='ticker')

    with conn:
        with conn.cursor() as cur:
            for index, row in unique_stocks.iterrows():
                
                cur.execute(
                    """INSERT INTO stocks (ticker, company_name) VALUES (%s, %s) ON CONFLICT (ticker) DO NOTHING""", 
                    (row['ticker'], row['company_name'])
                )

        conn.commit()
            
    print(f"Stocks loaded. {len(unique_stocks)} tickers processed.")

def date_already_loaded(conn, snapshot_date):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM ownership_snapshots WHERE snapshot_date = %s",
            (snapshot_date,)
        )
        count = cur.fetchone()[0]
    return count > 0

#used to insert 5% ownership changes' data to database
def load_ownership_data(df, conn, previous_date, latest_date):
    with conn:
        with conn.cursor() as cur:
            if date_already_loaded(conn, previous_date):
                print(f"{previous_date} already loaded, skipping.")
            else:
            # existing insert loop for previous_date

                #Insert previous snapshot
                for index, row in df.iterrows():
                    cur.execute(
                        """INSERT INTO ownership_snapshots
                        (ticker, holder_name, custodian, account_name, nationality, 
                        domicile, status_local_foreign, shares_held, 
                        combined_shares_per_investor, ownership_pct, snapshot_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            row['ticker'], row['holder_name'], row['custodian'], row['account_name'], 
                            row['nationality'], row['domicile'], row['status_local_foreign'], 
                            row['shares_prev'], row['combined_shares_prev'], 
                            row['pct_prev'], previous_date
                        )
                    )
                print(f"Finished {previous_date} loop")

            if date_already_loaded(conn, latest_date):
                print(f"{latest_date} already loaded, skipping.")
            else:
                # existing insert loop for previous_date

                #Insert latest snapshot
                for index, row in df.iterrows():
                    cur.execute(
                        """INSERT INTO ownership_snapshots
                        (ticker, holder_name, custodian, account_name, nationality, 
                        domicile, status_local_foreign, shares_held, 
                        combined_shares_per_investor, ownership_pct, snapshot_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """,
                        (
                            row['ticker'], row['holder_name'], row['custodian'], row['account_name'], 
                            row['nationality'], row['domicile'], row['status_local_foreign'], 
                            row['shares_latest'], row['combined_shares_latest'], 
                            row['pct_latest'], latest_date
                        )
                    )
                    
                print(f"Finished {latest_date} loop")

#used to retrieve ownership changes' data (optional)
def get_changes(conn):
    query = """
        WITH holder_sum AS (
            SELECT ticker, holder_name, snapshot_date, SUM(shares_held) AS total_share_held
            FROM ownership_snapshots
            GROUP BY ticker, holder_name, snapshot_date
        ),
        holder_lag AS (
            SELECT ticker, holder_name, snapshot_date, total_share_held,
                LAG(total_share_held) OVER (
                    PARTITION BY ticker, holder_name ORDER BY snapshot_date
                ) AS previous_day_share_held
            FROM holder_sum
        )
        SELECT ticker, holder_name, snapshot_date, total_share_held, previous_day_share_held,
            total_share_held - previous_day_share_held AS share_change
        FROM holder_lag
        WHERE total_share_held != previous_day_share_held
        ORDER BY ticker;
        -- ORDER BY ABS(total_share_held - previous_day_share_held) DESC;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]  # extract column names
    
    return pd.DataFrame(results, columns=columns)