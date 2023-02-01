"""Munge CSV data from two different but similar databases. 
    Database 1 has fewer fields than database 2.
    They have fields that contain meaningful data but use different terminology in labels.
    Database 1 fields: ,Terminal ID,Terminal Name,Last Settled Transaction,Dispensed,S/C Fees,,Acc. WDs,S/C WDs,,Denied,Reversed,Other,Total
    Database 2 fields: "Bill to Business Code","Device Number","Location","SurWD Trxs","Inq Trxs","Denial Trxs","Reversal Trxs","Total Trxs","Total Surcharge","Business Surcharge","Total Interchange","Business Interchange","Business Addl Revenue","Business Credits/Debits","Business Total Income","Non-Sur WD Trxs","Total Dispensed Amount"
    Examples of names to match are "Terminal ID" is "Device Number", "Terminal Name" is "Location" and "S/C Fees" is "Total Surcharge"
    Output file should include all data from both inputs with field names changed to match database 2.
    """

import csv
from datetime import datetime

# Define a mapping of field names from database 1 to database 2
# Map the old field names to the new ones
field_map = {
  "Terminal ID": "Device Number",
  "Terminal Name": "Location",
  "Last Settled Transaction": "Last Settled Transaction",
  "Dispensed": "Total Dispensed Amount",
  "S/C Fees": "Total Surcharge",
  "Acc. WDs": "Total Trxs",
  "S/C WDs": "SurWD Trxs",
  "Denied": "Denial Trxs",
  "Reversed": "Reversal Trxs",
  "Other": "Inq Trxs",
  "Total": "Total Trxs"
}


def combine(csv1, csv2):
    print('Start combining CSV files.')

    # Get the current date to use in the file name
    today = datetime.now().strftime('%Y-%m-%d')
    out_csv = f'{today}_combined_data.csv'

    # Read in the data from the first CSV file
    with open(csv1, "r") as f:
        reader = csv.DictReader(f)
        data1 = [row for row in reader]
    print(f'Database 1 contains {len(data1)} items.')

    # Read in the data from the second CSV file
    with open(csv2, "r") as f:
        reader = csv.DictReader(f)
        data2 = [row for row in reader]
    print(f'Database 2 contains {len(data2)} items.')
 
    # Rename the fields in the data from the first CSV file
    for row in data1:
        for old_field, new_field in field_map.items():
            if old_field in row:
                row[new_field] = row.pop(old_field)

    # Combine the data from both CSV files
    combined_data = data1 + data2
    print(f'Combined database contains {len(combined_data)} items.')

    # Write the combined data to a new CSV file
    with open(out_csv, "w") as f:
        fieldnames = list(combined_data[-1].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in combined_data:
            writer.writerow(row)
    print('End combining.')
    return out_csv



if __name__ == '__main__':
    print(f"\nOutput file name is: {combine('database1.csv', 'database2.csv')}")
