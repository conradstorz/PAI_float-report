#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Monitor the system download folder for new CSV and excel files.

a sample filename is: Terminal Status(w_FLOAT)automated****.csv
This example is for the automated report generated by my processor. 
The first part of the name matches what I labeled the report in their system. 
The last part is the date of the report and was tagged on by the processor.

another filename is: TerminalTrxData****.xslx
This file contains data on transactions, surcharges and withdrawl amounts.
Processing this file to calculate average withdrawl(WD) amount, surcharge per WD,
ratio of surcharge to settlement amount (for return on assets),
average daily balance based on settlement (number of days in report must be input by user),
number of non-WD transactions, WD transactions NOT SURCHARGED (usually zero).
# TODO After loading this data set allow user to choose which report to run (dupont, commission, ROI, ...)
"""

import os
from time import sleep
from loguru import logger
import cfsiv_utils.log_handling as lh
import cfsiv_utils.filehandling as fh
from pathlib import Path
from dateutil.parser import parse, ParserError
from process_surcharge import process_monthly_surcharge_report_excel
from process_float_outexcel import process_floatReport_csv
from process_simple import process_simple_summary_csv


import json
import pandas as panda

# TODO should this function be inside of cfsiv-utils-conradical?
from customize_dataframe_for_excel import set_custom_excel_formatting

# Load custom ruleset for handling data
FORMATTING_FILE = "ColumnFormatting.json"

# constants
RUNTIME_NAME = Path(__file__)
CSV_EXT = [".csv"]
EXCEL_EXT = [".xls"]
DL_DRIVE = "C:"
DL_USER_BASE = "Users"
DL_USER = "Conrad"
DL_DIRECTORY = "Downloads"
DL_PATH = Path("C:/Users/Conrad/Downloads/")

# download filename, download extension, output extension
BASENAME_BANK_STATEMENT = ["BankDepositsStatement", CSV_EXT, CSV_EXT]
EMAIL_BASENAME_FLOATREPORT = ["Terminal Status(w_FLOAT)automated", CSV_EXT, EXCEL_EXT]
MANUAL_DL_BASENAME_FLOAT_REPORT = ["TerminalStatuswFLOATautomated3", CSV_EXT, CSV_EXT]
BASENAME_SIMPLE_SUMMARY = ["TerminalTrxData", CSV_EXT, EXCEL_EXT]
BASENAME_SURCHARGE_MONTHLY_PER_TERMINAL = ["MonthlyRevenueByDevice", EXCEL_EXT, EXCEL_EXT]

OUTPUT_DIRECTORY = "Documents"
OUTPUT_PATH = Path(f"C:/Users/Conrad/{OUTPUT_DIRECTORY}")


@logger.catch
def extract_date(fname):
    """the filename contains the date the report was run
    extract and return the date string
    # TODO use function from cfsiv-utils-conradical to standardize code rather than reinvent it here.
    """
    datestring = "xxxxxxxx"
    logger.info("Processing: " + str(fname))
    parts = str(fname.stem).split()
    # TODO also need to split on '-'s to catch a different type of embeded datestring
    logger.debug(f'fname split result: {parts}')
    for part in parts:
        try:
            datestring = parse(part).strftime("%Y%m%d")
        except ParserError as e:
            logger.debug(f"Date not found Error: {e}")
    return datestring


@logger.catch
def look_for_new_data(matchName, ext):
    """Get files and return any match
    # TODO use cfsiv-utils-conradical to reduce code duplication.
    """
    logger.info(f"Looking for {matchName}")
    files = list(DL_PATH.glob("*.*"))
    # logger.debug(files)
    logger.debug(ext)

    matches = [f for f in files if f.suffix in [ext]]
    # logger.debug(matches)
    num_of_files = str(len(matches))

    for fname in matches:
        if matchName in str(fname):
            logger.info("Matched filename: " + str(fname))
            return fname
    return ""  # no match found


@logger.catch
def determine_output_filename(datestr, matchedname, ext, output_folder):
    """Assemble datecode and output folder with original basename into new filename."""
    fn = ''
    # fn = fh.check_and_validate(datestr, output_folder)  # TODO no such function?
    newfilename = Path(f"{fn}_{matchedname}{ext}")  
    # TODO check that name does not yet exist, use cfsiv-utils-conradical to avoid filename collisions and auto-renaming.
    return newfilename



@logger.catch
def process_bank_statement_csv(out_f, in_f, rundate):
    """placeholder for future develpoment of a method of importing
    deposits into quickbooks for account reconciliation. Problem is that 
    downloaded CSV may have description and memo data reversed. quickbooks needs
    data to have a descriptive name line and it will ignore memo lines while trying
    to natch transactions in it's ledger. Banks often include meaningless data in the
    description like ACH or CHK etc... that are not unique to the vendor for that charge.
    """
    return False



@logger.catch
def process_touchtunes_xls(out_f, in_f, rundate):
    """placeholder for future develpoment of a method of importing
    the 'home' report and output useful details.
    """
    return False



def Send_dataframes_to_file(frames, out_f):
    """Takes a dict of dataframes and outputs them to excel files them sends them to default printer.
    output file path is modified to create a unique filename for each dataframe.
    """
    with open(FORMATTING_FILE) as json_data:
        column_details = json.load(json_data)
    # this dictionary will contain information about individual column data type

    args = os.sys.argv
    for filename, frame in frames.items():
        # extract column names from dataframe
        columns = frame.columns
        # establish excel output object and define column formats
        writer = panda.ExcelWriter(filename, engine="xlsxwriter")
        frame.to_excel(writer, startrow=1, sheet_name="Sheet1", index=False)
        # set output formatting
        set_custom_excel_formatting(frame, writer, column_details)
        logger.info("All work done. Saving worksheet...")
        writer.save()
        # now we print
        if len(args) > 1 and args[1] == "-np":
            logger.info("bypassing print option due to '-np' option.")
            logger.info("bypassing file removal option due to '-np' option.")
            logger.info("exiting program due to '-np' option.")
        else:
            logger.info("Send processed file to printer...")
            try:
                os.startfile(filename, "print")
            except FileNotFoundError as e:
                logger.error(f"File not found: {e}")


def scan_download_folder(files, functions):
    """Loop continuosly looking for downloads to process."""
    inputfile = ""
    while inputfile == "":
        logger.info(f"Looking in directory: {DL_PATH}")
        for indx, value in enumerate(files):
            basename = value[0]
            extension = value[1]
            output_ext = value[2][0]
            for ext in extension:
                inputfile = look_for_new_data(basename, ext)
                if inputfile != "" and inputfile != None:
                    filedate = extract_date(inputfile)
                    output_file = determine_output_filename(
                        filedate, basename, output_ext, OUTPUT_PATH
                    )
                    logger.debug(filedate)
                    output_dict = functions[indx](output_file, inputfile, filedate)
                    if len(output_dict) > 0:
                        Send_dataframes_to_file(output_dict, output_file)
                        fh.remove_file(inputfile)
                    else:
                        logger.error("Input file not processed properly.")
            else:
                logger.info("Nothing found.")
        inputfile = ""  # keep the program running looking for more files
        logger.info("Sleeping 10 seconds")
        sleep(10)
    return


@logger.catch
def Main():
    lh.defineLoggers(RUNTIME_NAME.stem) # .stem returns just the filename without extension
    logger.info("Program Start.")  # log the start of the program
    logger.info(RUNTIME_NAME)
    logger.info("Scanning for download to process...")

    file_types = [
        BASENAME_BANK_STATEMENT,
        EMAIL_BASENAME_FLOATREPORT,
        MANUAL_DL_BASENAME_FLOAT_REPORT,
        BASENAME_SIMPLE_SUMMARY,
        BASENAME_SURCHARGE_MONTHLY_PER_TERMINAL,
    ]

    process_func = [
        process_bank_statement_csv,
        process_floatReport_csv,
        process_floatReport_csv,
        process_simple_summary_csv,
        process_monthly_surcharge_report_excel,
    ]

    scan_download_folder(file_types, process_func)


if __name__ == "__main__":
    Main()
