"""This script takes 2 CSV files, cleans up the data, loads it into a dataframe, adds data from a JSON 
    file describing the characteristics of the ATMS, and then does calculations based on the data and
    adds those columns to the dataframe in preparation for output."""

import pandas as pd
pd.options.display.max_rows = None
pd.options.display.max_columns = None
from build_dataframe_from_csv import get_csv_dataframe
from build_dataframe_from_json import get_json_dataframe
from combine_csv_files import combine, clean_Columbus_ATM_CSV_file

PaymentAllianceFilename = 'MonthlyRevenueByDevice-20230106-052728AM.csv'
ColumbusDataFilename = 'rptTerminalActivitySummaryAlpha.csv'

cleanfile = clean_Columbus_ATM_CSV_file(ColumbusDataFilename)

joinedfile = combine(cleanfile, PaymentAllianceFilename)

# load the combined CSV data
csv_df = get_csv_dataframe(joinedfile)
# load the JSON file containing relevant data about the ATMs
json_df = get_json_dataframe("Terminal_Details.json")

# combine the json and the csv dataframes
df_combined = pd.concat([csv_df, json_df])

# sum the values of the columns when the dataframe has duplicate index values
# indexes are the DeviceID of each ATM
# Payment Alliance has one line for each month.
# the JSON file has details on a seperate line for each ATM
# this function below results in one line (row) per ATM and adds together the monthly amounts.
df_grouped = df_combined.groupby(level=0, dropna=False).sum(numeric_only=False)

# now add columns for each part of the dupont analysis

df_grouped['Location Share Surcharge'] = df_grouped['Total Surcharge'] - df_grouped['Business Surcharge']
# what is the surcharge per withdrawl for the location
df_grouped['Location Surch per xact'] = df_grouped['Location Share Surcharge'] / df_grouped['SurWD Trxs']
# how much interchange is the processor earning
df_grouped['Processor Interchange'] = df_grouped['Total Interchange'] - df_grouped['Business Interchange']
df_grouped['Processor Buyrate'] = df_grouped['Processor Interchange'] / df_grouped['SurWD Trxs']
# how much surcharge commission is due locations for this period
df_grouped['Comm Check Due'] = df_grouped['SurWD Trxs'] * df_grouped['Comm Rate paid']
# what is the estimated cost of labor and transportation for each ATM
df_grouped['Annual Servicing Expenses'] = 365 / df_grouped['Visit Days'] * df_grouped['Travel Cost']
# calculate the ATM vault balance needed to support ATM;
#     formula is: 'annual amount of dispense' divided by 'number of visits per year' multiplied by '2'.
# df_grouped['Visit Frequency'] =
# df_grouped['Annual Dispensed'] = 
# df_grouped['Total Vault Balance'] = df_grouped['Annual Dispensed'] / df_grouped['Visit Frequency'] * 2
# cross-check the field provided by the processor for total business income
df_grouped['Biz Tot Income'] = df_grouped['SurWD Trxs'] * df_grouped['Comm Rate earned'] + df_grouped['Business Interchange']
# EBIT is annualized here for use in the Dupont Analysis
df_grouped['Earnings BIT'] = df_grouped['Business Total Income'] * 4 - df_grouped['Annual Servicing Expenses']
# calculate fixed assets (value of ATM)
# calculate current assets (cash on hand in ATM average)
# calculate asset turn over
# calculate profit margin
# calculate return on investment
# calculate return on assets


print(df_grouped.dtypes, '\n', df_grouped.round(decimals=2))