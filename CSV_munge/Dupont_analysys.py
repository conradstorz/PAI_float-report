"""Generate various reports using the DuPont model."""

# import pandas and loguru
import pandas as pd
import numpy as np
from loguru import logger
pd.options.display.max_rows = None
pd.options.display.max_columns = None
# import the custom data munging scripts
from combine_json_and_csv_into_dataframe import combine_data_and_details
from combine_json_and_csv_into_dataframe import build_additional_columns_for_dupont_analysis
from CONSTANTS import ColumbusDataFilename, PaymentAllianceFilename, Terminal_Details
# import the reportlab function
from reportlabfunction import Send_to_printer

# process the input files
result = combine_data_and_details(ColumbusDataFilename, PaymentAllianceFilename, Terminal_Details)
dupont = build_additional_columns_for_dupont_analysis(result)

# drop certain rows
dupont = dupont[~dupont['Location'].str.contains("De-Activated")]

# show the list of all column names from headers
column_headers = list(dupont.columns.values)
print("The Column Header names:", column_headers)

# declare the fields for this report
annual_servicing_report = ['Location', 'Comm Check Due', 'Annual Earnings BIT', 'Processor Buyrate', 'Annual Servicing Expenses']
# declare columns for report and formatting
returns = {
            'Location': "as-is",
            'Daily income avg': "currency",
            'Annual Servicing Expenses': "currency",
            'Annual Earnings BIT': "currency",
            'Asset Turnover': "percentage", 
            'Profit Margin': "percentage", 
            'ROI': "percentage", 
        }

# trim the un-needed columns and set the precision
# out_df = dupont[annual_servicing_report].round(decimals=2)
out_df = dupont[returns.keys()].round(decimals=2)
# convert columns to correct display style
for k,v in returns.items():
    match v:
        case 'as-is':
            pass
        case 'currency':
            out_df[k] = np.where( out_df[k] >= 0, '$' + out_df[k].astype(str), '($' + out_df[k].astype(str).str[1:] + ')')
        case 'percentage':
            out_df[k] = np.where( out_df[k] >= 0, out_df[k].astype(str) + '%', '(' + out_df[k].astype(str) + '%)')
        case _:
            pass
# convert a column to a string representing currency
# out_df['Annual Servicing Expenses'] = np.where( out_df['Annual Servicing Expenses'] < 0, '-$' + out_df['Annual Servicing Expenses'].astype(str).str[1:], '$' + out_df['Annual Servicing Expenses'].astype(str))

# Print the dataframe
Send_to_printer(out_df)
