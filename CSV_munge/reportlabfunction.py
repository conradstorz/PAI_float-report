"""function to establish standard style for dataframe output"""

# import win32api for printing of PDFs
import win32api
# import the report building functions
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def Send_to_printer(df):
    """Uses ReportLab module to build a PDF and then send to the default printer."""
    # Create a PDF document
    doc = SimpleDocTemplate("temporary_print.pdf", pagesize=landscape(letter))

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
    win32api.ShellExecute(0, "print", "temporary_print.pdf", None, ".", 0)
    return
