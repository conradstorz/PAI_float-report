import pandas as pd
import json
pd.options.display.max_rows = None
pd.options.display.max_columns = None
from build_dataframe_from_csv import get_csv_dataframe
from build_dataframe_from_json import get_json_dataframe

csv_df = get_csv_dataframe("2023-01-31_combined_data.csv")

json_df = get_json_dataframe("Terminal_Details.json")

# combine the json and the csv dataframes
df_combined = pd.concat([csv_df, json_df])

# sum the values of the columns when the dataframe has duplicate index values
df_grouped = df_combined.groupby(level=0, dropna=False).sum(numeric_only=False)

# print(df_grouped)

# TODO add columns for each part of the dupont analysis
df_grouped['Location Share Surcharge'] = df_grouped['Total Surcharge'] - df_grouped['Business Surcharge']
df_grouped['Location Surch per xact'] = df_grouped['Location Share Surcharge'] / df_grouped['SurWD Trxs']
df_grouped['Processor Interchange'] = df_grouped['Total Interchange'] - df_grouped['Business Interchange']
df_grouped['Processor Buyrate'] = df_grouped['Processor Interchange'] / df_grouped['SurWD Trxs']
df_grouped['Comm Check Due'] = df_grouped['SurWD Trxs'] * df_grouped['Comm Rate paid']
df_grouped['Annual Servicing Expenses'] = 365 / df_grouped['Visit Days'] * df_grouped['Travel Cost']
df_grouped['Biz Tot Income'] = df_grouped['SurWD Trxs'] * df_grouped['Comm Rate earned'] + df_grouped['Business Interchange']
df_grouped['Earnings BIT'] = df_grouped['Business Total Income'] * 4 - df_grouped['Annual Servicing Expenses']

print(df_grouped.dtypes, '\n', df_grouped.round(decimals=2))