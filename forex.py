""" referenced program: https://github.com/emuin/forexite """

import pandas as pd
import requests
import os
import calendar

# get user input for start and end currency
_START_CURRENCY = input("Enter start currency (e.g. EUR): ").upper()
_END_CURRENCY = input("Enter end currency (e.g. USD): ").upper()
symbol = "{}{}".format(_START_CURRENCY, _END_CURRENCY)

_START_MONTH = 1
_START_YEAR = 2021
_END_MONTH = 12
_END_YEAR = 2021

df_list = []

# loop over each month in date range
cur_year = _START_YEAR
cur_month = _START_MONTH
while cur_year < _END_YEAR or (cur_year == _END_YEAR and cur_month <= _END_MONTH):
    
    # get number of days in current month
    num_days = calendar.monthrange(cur_year, cur_month)[1]

    # construct filename and download data
    filename = "{:02d}{:02d}{}.zip".format(num_days, cur_month, str(cur_year)[2:])
    print("Processing {}".format(filename))

    url = "https://www.forexite.com/free_forex_quotes/{}/{}/{}".format(cur_year, str(cur_month).zfill(2), filename)

    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

    # read data into df
    df = pd.read_csv(filename, compression='zip', header=0, names=['TICKER', 'DATE', 'TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE'])
    os.remove(filename)

    # transform df and append to list
    df = df[df['TIME'] != 0]
    df = df.drop(['TIME', 'OPEN', 'HIGH', 'LOW'], axis=1)
    df.drop_duplicates(subset=['TICKER', 'DATE'], keep='last', inplace=True)
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')
    df = df[df['TICKER'] == symbol]

    if df.empty:
        df = pd.DataFrame([[symbol, pd.to_datetime("{}-{}-{}".format(cur_year, cur_month, num_days)), "N/A"]], columns=['TICKER', 'DATE', 'CLOSE'])
    
    df_list.append(df)
    
    cur_month += 1
    if cur_month > 12:
        cur_month = 1
        cur_year += 1

# combine list
df = pd.concat(df_list, ignore_index=True)
print(df)
