"""function to establish standard style for dataframe output"""

from datetime import datetime
from time import sleep
# import win32api for printing of PDFs
import win32api
# import the report building functions
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def Send_to_printer(Dataframe_to_be_printed):
    """Uses ReportLab module to build a PDF and then send to the default printer."""
    # Get the current date to use in the file name
    today = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    pdffile = f'temporary_{today}_pdf_data.pdf'
    # Create a PDF document
    doc = SimpleDocTemplate(pdffile, pagesize=landscape(letter))

    # Create a table with the contents of the dataframe
    table = Table([Dataframe_to_be_printed.columns.tolist()] + Dataframe_to_be_printed.values.tolist())

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
    status = win32api.ShellExecute(0, "print", pdffile, None, ".", 0)
    print(status)
    print('Pausing 30 seconds to allow PDF to print...')
    sleep(30) # provide time for output PDF to be processed
    return
