"""Generate various reports using the DuPont model."""

import pandas as pd
from loguru import logger
pd.options.display.max_rows = None
pd.options.display.max_columns = None
from combine_json_and_csv_into_dataframe import combine_data_and_details

PaymentAllianceFilename = 'database2.csv'
ColumbusDataFilename = 'database1.csv'
Terminal_Details = "Terminal_Details.json"

result = combine_data_and_details(ColumbusDataFilename, PaymentAllianceFilename, Terminal_Details)

# drop certain rows
result = result[~result['Location'].str.contains("De-Activated")]


# Get the list of all column names from headers
column_headers = list(result.columns.values)
print("The Column Header names:", column_headers)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

""" EXAMPLE df
df = pd.DataFrame({
    'Device Number': ['RT90468', 'RT90469', 'RT90470'],
    'Location': ['De-Activated', 'Active', 'Active'],
    'Total Trxs': [100, 200, 300],
    'Total Surcharge': [1000, 2000, 3000]
})
"""

cols = ['Location', 'Comm Check Due', 'Earnings BIT', 'Processor Buyrate', 'Annual Servicing Expenses']
# df_selected = df[cols]
df = result[cols].round(decimals=2)

# Create a PDF document
doc = SimpleDocTemplate("dupont_df_print.pdf", pagesize=landscape(letter))

# Create a table with the contents of the dataframe
table = Table([df.columns.tolist()] + df.values.tolist())

# Apply table style
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))

# Add the table to the PDF document
doc.build([table])

# Print the PDF document

# import os
# os.startfile("dupont_df_print.pdf", "print")

# import win32api
import win32api

pdf_file = "file.pdf"
win32api.ShellExecute(0, "print", "dupont_df_print.pdf", None, ".", 0)
