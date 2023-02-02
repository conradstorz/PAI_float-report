import pandas as pd
import json
pd.options.display.max_rows = None
pd.options.display.max_columns = None


def get_json_dataframe(input_file):
    # Load the JSON file into a dictionary
    with open(input_file) as f:
        data = json.load(f)

    # Create a pandas DataFrame from the dictionary
    df = pd.DataFrame.from_dict(data, orient='index')

    # Set the index of the DataFrame to the primary key
    df.index.name = 'Device ID'
    df = df.reset_index()
    df = df.set_index('Device ID')
    # print(df)

    # Convert the columns to floating point numbers using the astype() method
    cols = ['Value',
            'Visit Days',
            'Travel Cost',
            'Comm Rate earned',
            'Comm Rate paid']
    df[cols] = df[cols].astype(float)

    return df


if __name__ == '__main__':
    result = get_json_dataframe("Terminal_Details.json")
    print(result.dtypes, '\n', result)
