"""This script takes 2 CSV files, cleans up the data, loads it into a dataframe, adds data from a JSON 
    file describing the characteristics of the ATMS, and then does calculations based on the data and
    adds those columns to the dataframe in preparation for output."""

import pandas as pd
from loguru import logger
pd.options.display.max_rows = None
pd.options.display.max_columns = None
from build_dataframe_from_csv import get_csv_dataframe
from build_dataframe_from_json import get_json_dataframe
from combine_csv_files import combine, clean_Columbus_ATM_CSV_file
from CONSTANTS import REPORTING_PERIOD_DAYS
from CONSTANTS import ANNUAL_BORROWING_RATE

@logger.catch
def build_additional_columns_for_dupont_analysis(df):
    """Add multiple columns to the resulting DataFrame to aid in the reporting of 'DuPont' analysis."""
    # now add columns for each part of the dupont analysis

    df['Location Share Surcharge'] = df['Total Surcharge'] - df['Business Surcharge']
    # what is the surcharge per withdrawl for the location
    df['Location Surch per xact'] = df['Location Share Surcharge'] / df['SurWD Trxs']
    # how much interchange is the processor earning
    df['Processor Interchange'] = df['Total Interchange'] - df['Business Interchange']
    df['Processor Buyrate'] = df['Processor Interchange'] / df['SurWD Trxs']
    # how much surcharge commission is due locations for this period
    df['Comm Check Due'] = df['SurWD Trxs'] * df['Comm Rate paid']
    # what is the estimated cost of labor and transportation for each ATM
    df['Annual Servicing Expenses'] = 365 / df['Visit Days'] * df['Travel Cost']
    
    # calculate the ATM vault balance needed to support ATM;
    df['Annual amount of Dispense'] = df['Total Dispensed Amount'] / REPORTING_PERIOD_DAYS * 365
    df['Balance required'] = df['Annual amount of Dispense'] / df['Visit Days'] * 2
    df['Daily income avg'] = df['Business Total Income'] / REPORTING_PERIOD_DAYS
    df['Time Value of Money'] = df['Balance required'] * ANNUAL_BORROWING_RATE / 365
    df['Daily expense avg'] = df['Annual Servicing Expenses'] / 365 + df['Time Value of Money']
    df['Ratio of income/expense'] = df['Daily income avg'] / df['Daily expense avg']

    # cross-check the field provided by the processor for total business income
    df['Biz Tot Income'] = df['SurWD Trxs'] * df['Comm Rate earned'] + df['Business Interchange']
    # EBIT is annualized here for use in the Dupont Analysis
    df['Annual Periods this Report'] = 365 / REPORTING_PERIOD_DAYS
    df['Annual Earnings BIT'] = df['Business Total Income'] * df['Annual Periods this Report'] - df['Annual Servicing Expenses']
    df['Fixed Asset Value'] = df['Value'] / 2 # TODO calculate better fixed assets (value of ATM)
    df['Current Assets'] = df['Value'] / 2 # TODO calculate better current assets (cash on hand in ATM average)
    df['Assets'] = df['Fixed Asset Value'] + df['Current Assets']
    df['Asset Turnover'] = df['Daily income avg'] * 365 / df['Assets']
    df['Profit Margin'] = df['Annual Earnings BIT'] / 365 / df['Daily income avg'] # calculate profit margin
    df['ROI'] = df['Asset Turnover'] * df['Profit Margin'] # calculate return on investment
    df['ROA'] = df['Assets'] / df['Profit Margin']  # TODO is this the right formula?
    return df


@logger.catch
def combine_data_and_details(csv_dbase1, csv_dbase2, json_terminal_data):
    """Takes 2 CSV files with similar data and combines with details from JSON file."""

    cleanfile = clean_Columbus_ATM_CSV_file(csv_dbase1)
    joinedfile = combine(cleanfile, csv_dbase2)

    # load the combined CSV data
    csv_df = get_csv_dataframe(joinedfile)
    # load the JSON file containing relevant data about the ATMs
    json_df = get_json_dataframe(json_terminal_data)

    # combine the json and the csv dataframes
    # the JSON file has details on a seperate line for each ATM    
    df_combined = pd.concat([csv_df, json_df])

    # sum the values of the columns when the dataframe has duplicate index values
    # indexes are the DeviceID of each ATM
    # Payment Alliance has one line for each month.
    # this function below results in one line (row) per ATM and adds together the monthly amounts.
    df_grouped = df_combined.groupby(level=0, dropna=False).sum(numeric_only=False)

    # print(df_grouped.dtypes, '\n', df_grouped.round(decimals=2))
    return df_grouped



if __name__ == '__main__':
    PaymentAllianceFilename = 'database2.csv'
    ColumbusDataFilename = 'database1.csv'
    Terminal_Details = "Terminal_Details.json"

    combined = combine_data_and_details(ColumbusDataFilename, PaymentAllianceFilename, Terminal_Details)

    # Get the list of all column names from headers
    column_headers = list(combined.columns.values)
    print("The Column Header names:", column_headers)

    duponted = build_additional_columns_for_dupont_analysis(combined)

    # Get the list of all column names from headers
    column_headers = list(duponted.columns.values)
    print("The Column Header names:", column_headers)

    print(f"{duponted}")
