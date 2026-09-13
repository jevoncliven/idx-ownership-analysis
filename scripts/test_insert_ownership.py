import psycopg2
import os
from dotenv import load_dotenv
from clean_ksei import clean_file

load_dotenv()

df = clean_file('../data/idx_5pct.xlsx')

with psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
) as conn:
    with conn.cursor() as cur:

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
                    row['pct_02jul'],'2026-07-02' 
                )
            )

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
                    row['pct_03jul'],'2026-07-03' 
                )
            )
    conn.commit()
