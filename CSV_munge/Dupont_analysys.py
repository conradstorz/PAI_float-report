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


@logger.catch
def main():
    # process the input files
    result = combine_data_and_details(ColumbusDataFilename, PaymentAllianceFilename, Terminal_Details)
    if result.empty:
        print(f'No useful data processed from {ColumbusDataFilename} and {PaymentAllianceFilename}')
    else:
        dupont = build_additional_columns_for_dupont_analysis(result)

    # show the list of all column names from headers
    column_headers = list(dupont.columns.values)
    print("The Column Header names:", column_headers)

    # declare columns for report and formatting
    reports = {
        'annual_servicing_report': {
                    'Location': "as-is", 
                    'Storz Surch': "currency",
                    'Comm Check Due': "currency", 
                    'Comm Rate earned': "currency",
                    'Annual Earnings BIT': "currency", 
                    'Processor Buyrate': "currency", 
                    'Annual Servicing Expenses': "currency",
        },
    }

    """
        'dupont_assets': {
                    'Location': "as-is",
                    'Annual Earnings BIT': "currency",
                    'TVM': "currency",                     
                    'Fixed Asset Value': "currency", 
                    'Current Assets': "currency", 
                    'Assets': "currency",
                    'Annual Operating Income': "currency", 
                    'Asset Turnover': "percentage",     
                },

        'dupont_annual': {
                    'Location': "as-is",
                    'ROA': "percentage",                    
                    'Profit Margin': "percentage", 
                    'Annual Dispense': "currency",                      
                    'Balance required': "currency", 
                    'Expense ratio': "percentage", 
                    'Daily income avg': "currency", 
                    'Daily expense avg': "currency",                     
                },

        'returns2': {
                    'Location': "as-is",
                    'ROA': "percentage",                    
                    'Asset Turnover': "percentage", 
                    'Expense ratio': "percentage",                                        
                    'Annual Earnings BIT': "currency",
                    'TVM': "currency",                    
                    'Profit Margin': "percentage", 
                    'Assets': "currency",
                },
    """


    # loop to build various reports
    output_dataframes = {}
    for rpt in reports.keys():
        # trim the un-needed columns and set the precision
        # out_df = dupont[annual_servicing_report].round(decimals=2)
        out_df = dupont[reports[rpt].keys()].round(decimals=2)
        # convert columns to correct display style
        for column, formating in reports[rpt].items():
            match formating:
                case 'as-is':
                    pass
                case 'currency':
                    out_df[column] = np.where( out_df[column] >= 0, '$' + out_df[column].astype(str), '($' + out_df[column].astype(str).str[1:] + ')')
                case 'percentage':
                    out_df[column] = np.where( out_df[column] >= 0, out_df[column].astype(str) + '%', '(' + out_df[column].astype(str) + '%)')
                case _:
                    pass
        output_dataframes[rpt] = out_df
            
    for rpt in output_dataframes.keys():
        print(rpt)
        headers = output_dataframes[rpt].keys()

        # define a custom function to extract the numerical value from the currency string
        def convert_to_float_if_possible(value_str):
            possible_float = value_str # strings are immutable. No need to decalre .copy()
            possible_float = possible_float.replace('$', '')  # remove any dollar sign
            possible_float = possible_float.replace(',', '')  # remove any comma
            possible_float = possible_float.replace('%', '')  # remove any percent sign
            try:
                result = float(possible_float)
            except ValueError as err:
                result = value_str
            return result

        # sort the dataframe by column #2 in ascending order
        output_dataframes[rpt] = output_dataframes[rpt].sort_values(by=headers[1], key=lambda x: x.apply(convert_to_float_if_possible))
 
        Send_to_printer(output_dataframes[rpt])
    """
    # sort the percentages (works as expected even though it is a string not a number)
    out_df = out_df.sort_values(by=['Expense ratio'], ascending=False)
    # Print the dataframe
    Send_to_printer(out_df)

    This method does not sort strings well and this column has been formatted as currency
    out_df = out_df.sort_values(by=['Daily income avg'], ascending=False)
    # Print the dataframe
    Send_to_printer(out_df)
    .str.replace('$', '', regex=True)

    # define a custom function to extract the numerical value from the currency string
    def extract_currency_value(currency_str):
        currency_str = currency_str.replace('$', '')  # remove the dollar sign
        currency_str = currency_str.replace(',', '')  # remove the comma
        return float(currency_str)

    # sort the dataframe by column 'Currency' in ascending order
    out_df = out_df.sort_values(by='Daily income avg', key=lambda x: x.apply(extract_currency_value))

    # Print the dataframe
    Send_to_printer(out_df)
    """

if __name__ == '__main__':
    main()