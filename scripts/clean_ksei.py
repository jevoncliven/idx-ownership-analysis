#this file is used to turn a messy Excel file into a clean, structured DataFrame

import pandas as pd
import numpy as np

df = pd.read_excel("../data/idx_5pct.xlsx", header=[2,3])

df.columns = ["no", "ticker", "nama_emiten", "sekuritas", "nama_pemegang_saham",
              "nama_rekening", "alamat", "alamat_lanjutan", "kebangsaan", "domisili",
              "status_lokal_asing", "saham_02jul", "saham_gabungan_02jul", "pct_02jul",
              "saham_03jul", "saham_gabungan_03jul", "pct_03jul", "perubahan"]

df = df.dropna(axis='index', how='any', subset='ticker')

df['nama_emiten'] = df['nama_emiten'].ffill()
df['nama_pemegang_saham'] = df['nama_pemegang_saham'].ffill()
df['no'] = df['no'].ffill()

df.loc[df['kebangsaan'].isna() & (df['domisili'].str.upper() == 'INDONESIA'), 'kebangsaan'] = 'INDONESIAN'

df['saham_gabungan_02jul'] = df['saham_gabungan_02jul'].ffill()
df['saham_gabungan_03jul'] = df['saham_gabungan_03jul'].ffill()
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

for col in ['saham_02jul','saham_gabungan_02jul','pct_02jul',
            'saham_03jul','saham_gabungan_03jul','pct_03jul','perubahan']:
    df[col] = df[col].replace('-', '0')

for col in ['saham_02jul','saham_gabungan_02jul','saham_03jul','saham_gabungan_03jul']:
    df[col] = df[col].apply(clean_number)

