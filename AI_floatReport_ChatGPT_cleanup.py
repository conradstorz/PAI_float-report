#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import pandas as pd
from time import sleep
from pathlib import Path
from dateutil.parser import parse, ParserError
from loguru import logger

# Constants
DL_PATH = Path("D:/Users/Conrad/Downloads")
OUTPUT_PATH = Path(f"D:/Users/Conrad/Documents")
FORMATTING_FILE = "ColumnFormatting.json"
RUNTIME_NAME = Path(__file__)

# File extensions
CSV_EXT = [".csv"]
EXCEL_EXT = [".xls"]

# File patterns
FILE_PATTERNS = [
    {"basename": "BankDepositsStatement", "extensions": CSV_EXT, "output_ext": CSV_EXT},
    {"basename": "Terminal Status(w_FLOAT)automated", "extensions": CSV_EXT, "output_ext": EXCEL_EXT},
    {"basename": "TerminalStatuswFLOATautomated3", "extensions": CSV_EXT, "output_ext": CSV_EXT},
    {"basename": "TerminalTrxData", "extensions": CSV_EXT, "output_ext": EXCEL_EXT},
    {"basename": "MonthlyRevenueByDevice", "extensions": EXCEL_EXT, "output_ext": EXCEL_EXT},
]

# Load custom ruleset for handling data
with open(FORMATTING_FILE) as json_data:
    COLUMN_DETAILS = json.load(json_data)

# Logging setup
logger.add(RUNTIME_NAME.stem + ".log")

def extract_date(fname):
    """Extract and return the date string from the filename."""
    datestring = "xxxxxxxx"
    logger.info(f"Processing: {fname}")
    parts = str(fname.stem).split()
    logger.debug(f"Filename split result: {parts}")
    for part in parts:
        try:
            datestring = parse(part).strftime("%Y%m%d")
        except ParserError as e:
            logger.debug(f"Date not found Error: {e}")
    return datestring

def look_for_new_data(match_name, ext):
    """Search for files in the download folder that match the given name and extension."""
    logger.info(f"Looking for {match_name}")
    files = list(DL_PATH.glob("*.*"))
    matches = [f for f in files if f.suffix in ext]

    for fname in matches:
        if match_name in str(fname):
            logger.info(f"Matched filename: {fname}")
            return fname
    return ""

def determine_output_filename(datestr, matchedname, ext, output_folder):
    """Assemble datecode and output folder with original basename into a new filename."""
    fn = ""
    newfilename = Path(f"{fn}_{matchedname}{ext}")
    return newfilename

def process_bank_statement_csv(out_f, in_f, rundate):
    """Placeholder for future development of a method to import deposits into QuickBooks for account reconciliation."""
    return False

def process_touchtunes_xls(out_f, in_f, rundate):
    """Placeholder for future development of a method to import the 'home' report and output useful details."""
    return False

def send_dataframes_to_file(frames, out_f):
    """Write dataframes to Excel files and send them to the default printer."""
    for filename, frame in frames.items():
        writer = pd.ExcelWriter(filename, engine="xlsxwriter")
        frame.to_excel(writer, startrow=1, sheet_name="Sheet1", index=False)
        writer.save()
        logger.info("Saved worksheet: " + filename)
        os.startfile(filename, "print")

def process_files(file_patterns):
    """Loop continuously looking for downloads to process."""
    input_file = ""
    while input_file == "":
        logger.info(f"Looking in directory: {DL_PATH}")
        for pattern in file_patterns:
            basename = pattern["basename"]
            extensions = pattern["extensions"]
            output_ext = pattern["output_ext"][0]
            for ext in extensions:
                input_file = look_for_new_data(basename, ext)
                if input_file:
                    file_date = extract_date(input_file)
                    output_file = determine_output_filename(file_date, basename, output_ext, OUTPUT_PATH)
                    logger.debug(f"Found Date: {file_date}")
                    output_dict = process_file(output_file, input_file, file_date)
                    if output_dict:
                        send_dataframes_to_file(output_dict, output_file)
                        if not remove_file(input_file):
                            logger.error(f"Could not remove file: {input_file}")
                            sys.exit(1)
                    else:
                        logger.error("Input file not processed properly.")
        input_file = ""
        logger.info("Sleeping for 10 seconds")
        sleep(10)

def process_file(output_file, input_file, file_date):
    """Process a file based on its type and return a dictionary of dataframes."""
    output_dict = {}
    if "BankDepositsStatement" in output_file.name:
        # Process bank statement CSV file
        result = process_bank_statement_csv(output_file, input_file, file_date)
        if result:
            output_dict[output_file] = result
    elif "Terminal Status(w_FLOAT)automated" in output_file.name:
        # Process Terminal Status CSV file
        result = process_floatReport_csv(output_file, input_file, file_date)
        if result:
            output_dict[output_file] = result
    # Add more file type handling here as needed
    return output_dict

def remove_file(file_path):
    """Remove a file from the file system."""
    try:
        os.remove(file_path)
        return True
    except OSError as e:
        logger.error(f"Error removing file: {e}")
        return False

if __name__ == "__main__":
    process_files(FILE_PATTERNS)
