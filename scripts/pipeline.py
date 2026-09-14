import psycopg2
import os
from dotenv import load_dotenv
from clean_ksei import clean_file

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

    with conn as conn:
        with conn.cursor() as cur:
            for index, row in unique_stocks.iterrows():
                
                cur.execute(
                    """INSERT INTO stocks (ticker, company_name) VALUES (%s, %s) ON CONFLICT (ticker) DO NOTHING""", 
                    (row['ticker'], row['company_name'])
                )

        conn.commit()
            
    print(f"Stocks loaded. {len(unique_stocks)} tickers processed.")

#used to insert 5% changes' data to database
def load_ownership_data(df, conn, date1, date2):
    with conn as conn:
        with conn.cursor() as cur:
            print("Starting insert loop...")

            #Insert 02-Jul data
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
                        row['shares_02jul'], row['combined_shares_02jul'], 
                        row['pct_02jul'], date1
                    )
                )
            print("Finished 02-Jul loop")

            #Insert 03-Jul data
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
                        row['shares_03jul'], row['combined_shares_03jul'], 
                        row['pct_03jul'], date2
                    )
                )
            print("Finished 03-Jul loop")

def main(filepath, date1, date2):
    conn = get_connection()
    df = clean_file(filepath)
    register_new_stocks(df, conn)
    load_ownership_data(df, conn, date1, date2)
    
if __name__ == "__main__":
    main("../data/idx_5pct.xlsx", "2026-07-02", "2026-07-03")