import pandas as pd
import numpy as np

def detect_dates(filepath):
    df = pd.read_excel(filepath, header=[2,3])

    #get non-duplicate dates 
    dates = (
        pd.Series(df.columns.get_level_values(0))
        .str.extract(r'(\d{2}-[A-Z]{3}-\d{4})')[0]
        .dropna()
        .drop_duplicates()
    )

    #change format to YY-MM-DD
    dates = pd.to_datetime(dates, format='%d-%b-%Y').dt.date

    #sort date from earliest to latest
    dates = dates.sort_values().reset_index(drop=True)
    previous_date = dates.iloc[0]
    latest_date = dates.iloc[1]

    return previous_date, latest_date
    

#to turn a messy Excel file into a clean, structured DataFrame
def clean_file(filepath):

    df = pd.read_excel(filepath, header=[2,3])

    df.columns = ['no', 'ticker', 'company_name', 'custodian', 'holder_name',
                'account_name', 'address', 'address_continued', 'nationality', 'domicile',
                'status_local_foreign', 'shares_prev', 'combined_shares_prev', 'pct_prev',
                'shares_latest', 'combined_shares_latest', 'pct_latest', 'change']

    df = df.dropna(axis='index', how='any', subset='ticker')

    df['company_name'] = df['company_name'].ffill()
    df['holder_name'] = df['holder_name'].ffill()
    df['no'] = df['no'].ffill()

    df.loc[df['nationality'].isna() & (df['domicile'].str.upper() == 'INDONESIA'), 'nationality'] = 'INDONESIAN'

    df['combined_shares_prev'] = df['combined_shares_prev'].ffill()
    df['combined_shares_latest'] = df['combined_shares_latest'].ffill()
    df['pct_prev'] = df['pct_prev'].ffill()
    df['pct_latest'] = df['pct_latest'].ffill()

    def clean_number(value):
        value = str(value)
        last_comma = value.rfind(',')
        if last_comma == -1:
            return float(value)
        after = value[last_comma+1:]
        if len(after) == 3 and after.isdigit():
            new_value = value.replace(',', '')
        else:
            new_value = value[:last_comma] + '.' + after
        return float(new_value)

    for col in ['shares_prev','combined_shares_prev','pct_prev',
                'shares_latest','combined_shares_latest','pct_latest','change']:
        df[col] = df[col].replace('-', '0')

    for col in ['shares_prev','combined_shares_prev','shares_latest','combined_shares_latest']:
        df[col] = df[col].apply(clean_number)

    return df