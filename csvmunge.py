"""Munge CSV data from two different but similar databases. 
    Database 1 has fewer fields than database 2.
    They have fields that contain meaningful data but use different terminology in labels.
    Database 1 fields: ,Terminal ID,Terminal Name,Last Settled Transaction,Dispensed,S/C Fees,,Acc. WDs,S/C WDs,,Denied,Reversed,Other,Total
    Database 2 fields: "Bill to Business Code","Device Number","Location","SurWD Trxs","Inq Trxs","Denial Trxs","Reversal Trxs","Total Trxs","Total Surcharge","Business Surcharge","Total Interchange","Business Interchange","Business Addl Revenue","Business Credits/Debits","Business Total Income","Non-Sur WD Trxs","Total Dispensed Amount"
    Examples of names to match are "Terminal ID" is "Device Number", "Terminal Name" is "Location" and "S/C Fees" is "Total Surcharge"
    Output file should include all data from both inputs with field names changed to match database 2.
    """
import csv

# Map the old field names to the new ones
field_map = {
  "Terminal ID": "Device Number",
  "Terminal Name": "Location",
  "Last Settled Transaction": "Last Settled Transaction",
  "Dispensed": "Total Dispensed Amount",
  "S/C Fees": "Total Surcharge",
  "Acc. WDs": "Non-Sur WD Trxs",
  "S/C WDs": "SurWD Trxs",
  "Denied": "Denial Trxs",
  "Reversed": "Reversal Trxs",
  "Other": "Other",
  "Total": "Total Trxs"
}

# Set the desired output field order
output_fields = [
  "Bill to Business Code",
  "Device Number",
  "Location",
  "SurWD Trxs",
  "Inq Trxs",
  "Denial Trxs",
  "Reversal Trxs",
  "Total Trxs",
  "Total Surcharge",
  "Business Surcharge",
  "Total Interchange",
  "Business Interchange",
  "Business Addl Revenue",
  "Business Credits/Debits",
  "Business Total Income",
  "Non-Sur WD Trxs",
  "Total Dispensed Amount"
]


# Open the input CSV file for reading
with open('input.csv', 'r') as input_file:
  # Create a CSV reader
  reader = csv.reader(input_file)

  # Get the field names from the first row
  headers = next(reader)
  print(headers)
  # Rename the fields using the mapping. Use original name if no replacement is found. '.get(h, h)'
  headers = [field_map.get(h, h) for h in headers]
  print(headers)

  # Create a list to store the data
  data = []

  # Read the rows from the input file
  for row in reader:
    print(row)
    # Create a dictionary for the row
    row_data = {}
    # Add the data to the dictionary
    for i, h in enumerate(headers):
      row_data[h] = row[i]
    # Add the row data to the list
    print(row_data)
    data.append(row_data)

 
# Open the primary CSV file for reading
with open('primary.csv', 'r') as primary_file:
  # Create a CSV reader
  reader = csv.reader(primary_file)

  # Read the rows from the primary file
  for row in reader:
    # Create a dictionary for the row
    row_data = {}
    # Add the data to the dictionary
    for i, h in enumerate(headers):
      row_data[h] = row[i]
    # Add the row data to the list
    data.append(row_data)
   

  # Open the output CSV file for writing
  with open('combined.csv', 'w') as output_file:
    # Create a CSV writer
    writer = csv.writer(output_file)

    # Write the new headers to the output file
    writer.writerow(output_fields)

    # Write the data to the output file
    for row in data:
        # Create a list of values in the desired order
        values = [row.get(f, '') for f in output_fields]
        # Write the values to the output file
        writer.writerow(values)


"""
import csv

# Map the old field names to the new ones
field_map = {
  "Terminal ID": "Device Number",
  "Terminal Name": "Location",
  "Last Settled Transaction": "Last Settled Transaction",
  "Dispensed": "Total Dispensed Amount",
  "S/C Fees": "Total Surcharge",
  "Acc. WDs": "Non-Sur WD Trxs",
  "S/C WDs": "SurWD Trxs",
  "Denied": "Denial Trxs",
  "Reversed": "Reversal Trxs",
  "Other": "Other",
  "Total": "Total Trxs"
}

# Set the desired field order
output_fields = [
  "Bill to Business Code",
  "Device Number",
  "Location",
  "SurWD Trxs",
  "Inq Trxs",
  "Denial Trxs",
  "Reversal Trxs",
  "Total Trxs",
  "Total Surcharge",
  "Business Surcharge",
  "Total Interchange",
  "Business Interchange",
  "Business Addl Revenue",
  "Business Credits/Debits",
  "Business Total Income",
  "Non-Sur WD Trxs",
  "Total Dispensed Amount"
]

# Open the input CSV file for reading
with open('input.csv', 'r') as input_file:
  # Create a CSV reader
  reader = csv.reader(input_file)

  # Get the field names from the first row
  headers = next(reader)

  # Create a dictionary to store the data
  data = []

  # Read the rows from the input file
  for row in reader:
    # Create a dictionary for the row
    row_data = {}
    # Add the data to the dictionary
    for i, h in enumerate(headers):
      row_data[h] = row[i]
    # Add the row data to the list
    data.append(row_data)

# Open the output CSV file for writing
with open('output.csv', 'w') as output_file:
  # Create a CSV writer
  writer = csv.writer(output_file)

  # Write the new headers to the output file
  writer.writerow(output_fields)

  # Write the data to the output file
  for row in data:
    # Create a list of values in the desired order
    values = [row.get(f, '') for f in output_fields]
    # Write the values to the output file
    writer.writerow(values)


import csv

# Map the old field names to the new ones
field_map = {
  "Terminal ID": "Device Number",
  "Terminal Name": "Location",
  "Last Settled Transaction": "Last Settled Transaction",
  "Dispensed": "Total Dispensed Amount",
  "S/C Fees": "Total Surcharge",
  "Acc. WDs": "Non-Sur WD Trxs",
  "S/C WDs": "SurWD Trxs",
  "Denied": "Denial Trxs",
  "Reversed": "Reversal Trxs",
  "Other": "Other",
  "Total": "Total Trxs"
}

# Set the desired field order
output_fields = [
  "Bill to Business Code",
  "Device Number",
  "Location",
  "SurWD Trxs",
  "Inq Trxs",
  "Denial Trxs",
  "Reversal Trxs",
  "Total Trxs",
  "Total Surcharge",
  "Business Surcharge",
  "Total Interchange",
  "Business Interchange",
  "Business Addl Revenue",
  "Business Credits/Debits",
  "Business Total Income",
  "Non-Sur WD Trxs",
  "Total Dispensed Amount"
]

# Open the input CSV file for reading
with open('input.csv', 'r') as input_file:
  # Create a CSV reader
  reader = csv.reader(input_file)

  # Get the field names from the first row
  headers = next(reader)

  # Create a list to store the data
  data = []

  # Read the rows from the input file
  for row in reader:
    # Create a dictionary for the row
    row_data = {}
    # Add the data to the dictionary
    for i, h in enumerate(headers):
      row_data[h] = row[i]
    # Add the row data to the list
    data.append(row_data)

# Open the primary CSV file for reading
with open('primary.csv', 'r') as primary_file:
  # Create a CSV reader
  reader = csv.reader(primary_file)

  # Read the rows from the primary file
  for row in reader:
    # Create a dictionary for the row
    row_data = {}
    # Add the data to the dictionary
    for i, h in enumerate(headers):
      row_data[h] = row[i]
    # Add the row data to the list
    data.append(row_data)

# Open the output CSV file for writing
with open('combined.csv', 'w') as output_file:
  # Create a CSV writer
  writer = csv.writer(output_file)

  # Write the new headers to the output file
  writer.writerow(output_fields)

  # Write the data to the output file
  for row in data:
    # Create a list of values in the desired order
    values = [row.get(f, '') for f in output_fields]
    # Write the values to the output file
   
"""