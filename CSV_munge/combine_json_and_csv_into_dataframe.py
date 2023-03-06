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
    """Add multiple columns to the resulting DataFrame to aid in the reporting of 'DuPont' analysis.
        dataframe data contains data for terminals that wont appear in the input CSV so drop
        any rows that do not contain revenue or are listed as 'De-Activated'.    
    """

    # drop certain rows
    df = df[~df['Location'].str.contains("De-Activated")]
    df = df.drop(df[df['SurWD Trxs'] < 1].index)

    # cross-check the field provided by the processor for total business income
    df['Biz Tot Income'] = df['SurWD Trxs'] * df['Comm Rate earned'] + df['Business Interchange']
    # copy values from column to column for rows with index ['P608085', 'P608086', 'P608087']
    # Columbus Data does not provide these directly
    df.loc[['P608085', 'P608086', 'P608087'], 'Business Total Income'] = df.loc[['P608085', 'P608086', 'P608087'], 'Biz Tot Income']    
    
    # TODO find a way to invalidate FOEagles values that are irrelevant

    # now add columns for each part of the dupont analysis

    df['Location Share Surcharge'] = df['Total Surcharge'] - df['Business Surcharge']
    # what is the surcharge per withdrawl for the location
    df['Location Surch per xact'] = df['Location Share Surcharge'] / df['SurWD Trxs']
    # how much actual surcharge is this terminal making for Storz Cash Services
    df['Storz Surch'] = df['Business Surcharge'] / df['SurWD Trxs']
    # how much interchange is the processor earning
    df['Processor Interchange'] = df['Total Interchange'] - df['Business Interchange']
    df['Processor Buyrate'] = df['Processor Interchange'] / df['SurWD Trxs']
    # how much surcharge commission is due locations for this period
    df['Comm Check Due'] = df['SurWD Trxs'] * df['Comm Rate paid']
    # what is the estimated cost of labor and transportation for each ATM
    df['Annual Servicing Expenses'] = 365 / df['Visit Days'] * df['Travel Cost']
  
    # calculate the ATM vault balance needed to support ATM;
    df['Annual Dispense'] = df['Total Dispensed Amount'] / REPORTING_PERIOD_DAYS * 365
    df['Balance required'] = df['Annual Dispense'] / 26 # 2 weeks worth of money
    df['Daily income avg'] = df['Business Total Income'] / REPORTING_PERIOD_DAYS
    # EBIT is annualized here for use in the Dupont Analysis  
    df['Annual Periods this Report'] = 365 / REPORTING_PERIOD_DAYS
    df['Annual Operating Income'] = df['Business Total Income'] * df['Annual Periods this Report']
    df['Annual Earnings BIT'] = df['Annual Operating Income'] - df['Annual Servicing Expenses']
    df['Fixed Asset Value'] = df['Value'] / 2 # TODO calculate better fixed assets (value of ATM)
    df['Current Assets'] = df['Balance required'] # (cash on hand in ATM and bank on average)
    df['Assets'] = df['Fixed Asset Value'] + df['Current Assets']
    df['TVM'] = df['Assets'] * ANNUAL_BORROWING_RATE  # Time Value of Money  
    df['Daily expense avg'] = df['Annual Servicing Expenses'] / 365 + df['TVM'] / 365  
    df['Expense ratio'] = df['Daily expense avg'] / df['Daily income avg'] * 100        
    df['Asset Turnover'] = df['Daily income avg'] * 365 / df['Assets'] * 100
    df['Profit Margin'] = df['Annual Earnings BIT'] / 365 / df['Daily income avg'] * 100 # calculate profit margin
    df['ROI'] = df['Asset Turnover'] * df['Profit Margin'] / 100 # calculate return on investment
    df['ROA'] = df['Annual Earnings BIT'] / df['Assets'] * 100
    return df


@logger.catch
def combine_data_and_details(csv_dbase1, csv_dbase2, json_terminal_data):
    """Takes 2 CSV files with similar data and combines with details from JSON file.
    """

    cleanfile = clean_Columbus_ATM_CSV_file(csv_dbase1)

    joinedfile = combine(cleanfile, csv_dbase2)

    # load the combined CSV data
    csv_df = get_csv_dataframe(joinedfile)

    # load the JSON file containing relevant data about the ATMs
    json_df = get_json_dataframe(json_terminal_data)

    # TODO missing values from Columbus file need to be calculated using information
    #       from the JSON file combined with revenue data from Columbus file to fix
    #       the missing data

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

    # df = combined[combined['age'] >= 18]
    df = duponted.drop(index=[idx for idx in duponted.index if idx not in ['P608085', 'P608086', 'P608087']])
    print(df)
