#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Munge spreadsheet data.
Takes and input file Path obj, and output file Path obj,
and a rundate string and then makes calculations and returns an output version
of the spreadsheet in dataframe format.
"""

from loguru import logger


def set_custom_excel_formatting(df, writer, formats=False):
    """By default this will expand column widths to display all content.
    Optionally a list of strings defining formats for alpha, numeric, currency or percentage
    may be specified per column. example: ['A','#','$','%'] would set the first 4 columns.
    """
    logger.info('formatting column widths and styles...') 
    # attempt to set column widths

    #Indicate workbook and worksheet for formatting
    workbook = writer.book
    currency_format = workbook.add_format({'num_format': '$#,##0.00'})
    # Add some cell formats.
    nmbrfrmt = workbook.add_format({'num_format': '#,##0'})
    percntg = workbook.add_format({'num_format': '0%'})
    worksheet = writer.sheets['Sheet1']
    #Iterate through each column and set the width == the max length in that column. A padding length of 2 is also added.
    for i, col in enumerate(df.columns):
        # find length of column i
        column_width = df[col].astype(str).str.len().max()
        # Setting the length if the column header is larger
        # than the max column value length
        column_width = max(column_width, len(col)) + 2
        # set the column length and format
        if formats[i] == 'A':
            worksheet.set_column(i, i, column_width)
        if formats[i] == '#':
            worksheet.set_column(i, i, column_width, nmbrfrmt)
        if formats[i] == '$':
            worksheet.set_column(i, i, column_width, currency_format)
        if formats[i] == '%':    
            worksheet.set_column(i, i, column_width, percntg)      
