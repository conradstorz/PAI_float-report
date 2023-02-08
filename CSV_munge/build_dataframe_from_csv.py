import pandas as pd
pd.options.display.max_rows = None
pd.options.display.max_columns = None

def get_csv_dataframe(input_file):
    # put csv in a dataframe and index based on the device id
    df = pd.read_csv(input_file)
    df = df.set_index("Device Number")
    #print(df)

    # The dollar values are represented as formatted strings (e.g. $123,456.03)
    # Replace the comma with an empty string using the str.replace() method
    df['Total Dispensed Amount'] = df['Total Dispensed Amount'].str.replace(',', '', regex=True)
    df['Business Total Income'] = df['Business Total Income'].str.replace(',', '', regex=True)
    df['Business Credits/Debits'] = df['Business Credits/Debits'].str.replace(',', '', regex=True)
    df['Business Surcharge'] = df['Business Surcharge'].str.replace(',', '', regex=True)
    df['Total Surcharge'] = df['Total Surcharge'].str.replace(',', '', regex=True)
    df['Total Interchange'] = df['Total Interchange'].str.replace(',', '', regex=True)
    df['Business Addl Revenue'] = df['Business Addl Revenue'].str.replace(',', '', regex=True)
    df['Business Interchange'] = df['Business Interchange'].str.replace(',', '', regex=True)

    # Replace the dollar sign with an empty string using the str.replace() method
    df['Total Dispensed Amount'] = df['Total Dispensed Amount'].str.replace('$', '', regex=True)
    df['Business Total Income'] = df['Business Total Income'].str.replace('$', '', regex=True)
    df['Business Credits/Debits'] = df['Business Credits/Debits'].str.replace('$', '', regex=True)
    df['Business Surcharge'] = df['Business Surcharge'].str.replace('$', '', regex=True)
    df['Total Surcharge'] = df['Total Surcharge'].str.replace('$', '', regex=True)
    df['Total Interchange'] = df['Total Interchange'].str.replace('$', '', regex=True)
    df['Business Addl Revenue'] = df['Business Addl Revenue'].str.replace('$', '', regex=True)
    df['Business Interchange'] = df['Business Interchange'].str.replace('$', '', regex=True)


    # Convert the columns to floating point numbers using the astype() method
    cols = ['Total Dispensed Amount', 
            'Business Total Income', 
            'Business Credits/Debits',         
            'Business Surcharge', 
            'Total Surcharge', 
            'Total Interchange', 
            'Business Addl Revenue',         
            'Business Interchange'
            ]
    df[cols] = df[cols].astype(float)

    """
    df['Total Dispensed Amount'] = df['Total Dispensed Amount'].astype(float)
    df['Business Total Income'] = df['Business Total Income'].astype(float)
    df['Business Credits/Debits'] = df['Business Credits/Debits'].astype(float)
    df['Business Surcharge'] = df['Business Surcharge'].astype(float)
    df['Total Surcharge'] = df['Total Surcharge'].astype(float)
    df['Total Interchange'] = df['Total Interchange'].astype(float)
    df['Business Addl Revenue'] = df['Business Addl Revenue'].astype(float)
    df['Business Interchange'] = df['Business Interchange'].astype(float)
    
    # NOTE the code below was supposed to replace all the detail above but it didn't work
    # Replace the comma and dollar sign with an empty string using the str.replace() method
    df = df.replace({'\$': '', ',': ''}, regex=True).astype(float)

    cols = ['Total Dispensed Amount', 'Business Total Income', 'Business Credits/Debits',         'Business Surcharge', 'Total Surcharge', 'Total Interchange', 'Business Addl Revenue',         'Business Interchange']
    df[cols] = df[cols].astype(float)

    """
    # sum the values of the columns when the dataframe has duplicate index values
    df_grouped = df.groupby(level=0).sum(numeric_only=True)
    #print(df_grouped)
    return df_grouped

if __name__ == '__main__':
    result = get_csv_dataframe("2023-01-31_combined_data.csv")
    print(result.dtypes, '\n', result)