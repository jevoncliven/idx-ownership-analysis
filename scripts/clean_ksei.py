import pandas as pd
import numpy as np

#to turn a messy Excel file into a clean, structured DataFrame
def clean_file(filepath):

    df = pd.read_excel(filepath, header=[2,3])

    df.columns = ["no", "ticker", "company_name", "custodian", "holder_name",
                "account_name", "address", "address_continued", "nationality", "domicile",
                "status_local_foreign", "shares_02jul", "combined_shares_02jul", "pct_02jul",
                "shares_03jul", "combined_shares_03jul", "pct_03jul", "change"]

    df = df.dropna(axis='index', how='any', subset='ticker')

    df['company_name'] = df['company_name'].ffill()
    df['holder_name'] = df['holder_name'].ffill()
    df['no'] = df['no'].ffill()

    df.loc[df['nationality'].isna() & (df['domicile'].str.upper() == 'INDONESIA'), 'nationality'] = 'INDONESIAN'

    df['combined_shares_02jul'] = df['combined_shares_02jul'].ffill()
    df['combined_shares_03jul'] = df['combined_shares_03jul'].ffill()
    df['pct_02jul'] = df['pct_02jul'].ffill()
    df['pct_03jul'] = df['pct_03jul'].ffill()

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

    for col in ['shares_02jul','combined_shares_02jul','pct_02jul',
                'shares_03jul','combined_shares_03jul','pct_03jul','change']:
        df[col] = df[col].replace('-', '0')

    for col in ['shares_02jul','combined_shares_02jul','shares_03jul','combined_shares_03jul']:
        df[col] = df[col].apply(clean_number)

    return df