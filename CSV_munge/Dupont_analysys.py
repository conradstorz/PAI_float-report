"""Generate various reports using the DuPont model."""

# import win32api for printing of PDFs
import win32api
# import the report building functions
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
# import pandas and loguru
import pandas as pd
from loguru import logger
pd.options.display.max_rows = None
pd.options.display.max_columns = None
# import the custom data munging scripts
from combine_json_and_csv_into_dataframe import combine_data_and_details, build_additional_columns
# declare the details for this script
PaymentAllianceFilename = 'database2.csv'
ColumbusDataFilename = 'database1.csv'
Terminal_Details = "Terminal_Details.json"
reporting_period = 30 # days

# process the input files
result = combine_data_and_details(ColumbusDataFilename, PaymentAllianceFilename, Terminal_Details)
dupont = build_additional_columns(result)

# drop certain rows
dupont = dupont[~dupont['Location'].str.contains("De-Activated")]

# show the list of all column names from headers
column_headers = list(dupont.columns.values)
print("The Column Header names:", column_headers)

# begin the report building
""" EXAMPLE df
df = pd.DataFrame({
    'Device Number': ['RT90468', 'RT90469', 'RT90470'],
    'Location': ['De-Activated', 'Active', 'Active'],
    'Total Trxs': [100, 200, 300],
    'Total Surcharge': [1000, 2000, 3000]
})
"""
# declare the fields for this report
annual_servicing_report = ['Location', 'Comm Check Due', 'Earnings BIT', 'Processor Buyrate', 'Annual Servicing Expenses']

# trim the un-needed columns and set the precision
out_df = dupont[annual_servicing_report].round(decimals=2)

# Create a PDF document
doc = SimpleDocTemplate("dupont_df_print.pdf", pagesize=landscape(letter))

# Create a table with the contents of the dataframe
table = Table([out_df.columns.tolist()] + out_df.values.tolist())

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
win32api.ShellExecute(0, "print", "dupont_df_print.pdf", None, ".", 0)
