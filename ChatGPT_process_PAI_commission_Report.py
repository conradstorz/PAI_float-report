import csv
import json
from datetime import datetime

print('Program Start...')
# Open the CSV file and read the contents
with open('transactions.csv', 'r') as f:
    reader = csv.DictReader(f)
   
    # Open the JSON file and read the contents
    with open('Terminal_Details.json', 'r') as g:
        terminal_details = json.load(g)
       
        # Create a dictionary to store the total dispensed, total SurWD Trxs, and total SurWD commission for each location
        totals_by_location = {}
       
        # Iterate through the rows of the CSV file
        for row in reader:
            location = row['Location']

            td = row['Total Dispensed Amount']
            td = td.replace("$", "")
            td = td.replace(",", "")
            if len(td) > 0:
                total_dispensed = float(td)
            else:
                total_dispensed = 0.0

            surwd_trxs = row['SurWD Trxs']
            if len(surwd_trxs) > 0:
                surwd_trxs  = int(surwd_trxs)
            else:
                surwd_trxs = 0

            device_number = row['Device Number']
           
            # Look up the commission for this device number
            commission = float(terminal_details[device_number]['Commission'])
           
            # Calculate the total SurWD commission
            surwd_commission = surwd_trxs * commission
           
            # Add the total dispensed, total SurWD Trxs, and total SurWD commission for this location to the dictionary
            if location in totals_by_location:
                totals_by_location[location] = (
                    totals_by_location[location][0] + total_dispensed,
                    totals_by_location[location][1] + surwd_trxs,
                    totals_by_location[location][2] + surwd_commission
                )
            else:
                totals_by_location[location] = (total_dispensed, surwd_trxs, surwd_commission)
print(f'{len(totals_by_location)} locations read and processed.')
# Get the current date to use in the file name
today = datetime.now().strftime('%Y-%m-%d')

# Open the output CSV file and write the results
out_csv = f'{today}_Revenue_Report.csv'
with open(out_csv, 'w', newline='') as h:
    fieldnames = ['Location', 'Total Dispensed', 'Total SurWD Trxs', 'Total SurWD Commission']
    writer = csv.DictWriter(h, fieldnames=fieldnames)
    writer.writeheader()
   
    # Write a row for each location
    for location, totals in totals_by_location.items():
        total_dispensed, surwd_trxs, surwd_commission = totals
        writer.writerow({
            'Location': location,
            'Total Dispensed': total_dispensed,
            'Total SurWD Trxs': surwd_trxs,
            'Total SurWD Commission': surwd_commission
        })
print(f'Output file saved as {out_csv}.')