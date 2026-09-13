import psycopg2
import os
from dotenv import load_dotenv
from clean_ksei import clean_file

load_dotenv()

#get cleaned dataFrame
df = clean_file('../data/idx_5pct.xlsx')

#get unique ticker/company name pairs
unique_stocks = df[['ticker', 'nama_emiten']].drop_duplicates(subset='ticker')
    
try:                                        
    with psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    ) as conn:
        with conn.cursor() as cur:
            for index, row in unique_stocks.iterrows():
                
                cur.execute(
                    """INSERT INTO stocks (ticker, company_name) VALUES (%s, %s) ON CONFLICT (ticker) DO NOTHING""", 
                    (row['ticker'], row['nama_emiten'])
                )

        conn.commit()
            
    print('Stocks loaded.')

except Exception as error:
    print(error)