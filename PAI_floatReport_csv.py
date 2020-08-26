""" Monitor the system download folder for new CSV files.

a sample filename is: Terminal Status(w_FLOAT)automated****.csv
This example is for the automated report generated by my processor. 
The first part of the name matches what I labeled the report in their system. 
The last part is the date of the report and was tagged on by the processor.

another filename is: TerminalTrxData****.csv
This file contains data on transactions, surcharges and withdrawl amounts.
Processing this file to calculate average withdrawl(WD) amount, surcharge per WD,
ratio of surcharge to settlement amount (for return on assets),
average daily balance based on settlement (number of days in report must be input by user),
number of non-WD transactions, WD transactions NOT SURCHARGED (usually zero).
"""

import os
import csv
from time import sleep
from loguru import logger
from filehandling import check_and_validate # removes invalid characters from proposed filenames
from pathlib import Path
from dateutil.parser import *
import pandas as panda

# constants
BASENAME_BANK_STATEMENT = "BankDepositsStatement"

RUNTIME_NAME = Path(__file__)

FILE_TYPE = ".csv"
INPUTFILE_EXTENSION = FILE_TYPE

DL_DRIVE = "C:"
DL_USER_BASE = "Users"
DL_USER = "Conrad"
DL_DIRECTORY = "Downloads"
DL_PATH = Path("C:/Users/Conrad/Downloads/")

EMAIL_BASENAME_FLOATREPORT = "Terminal Status(w_FLOAT)automated"
MANUAL_DL_BASENAME_FLOATEREPORT = 'TerminalStatuswFLOATautomated3'
BASENAME_SIMPLE_SUMMARY = "TerminalTrxData"

OUTPUT_DIRECTORY = "Documents"
OUTPUT_PATH = Path(f"C:/Users/Conrad/{OUTPUT_DIRECTORY}")


@logger.catch
def process_floatReport_csv(out_f, in_f, rundate):
    """Scan file and compute sums for 2 columns
    """
    balances = []
    floats = []
    terminals = 0
    with open(out_f, "w", newline="") as out_csv:  # supress extra newlines
        csvWriter = csv.writer(out_csv)
        with open(in_f) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            logger.debug(csvReader)
            for row in csvReader:
                logger.debug(row)
                csvWriter.writerow(row)
                if row[0] == "Terminal":
                    logger.debug('Located headers. Discarding...')
                else:
                    logger.debug('Adding terminal stats to running total.')
                    terminals += 1 # increment number of terminals reporting                    
                    if row[2] == '':
                        logger.debug('Terminal has no balance value. Adding Zero to balance list')
                        balances.append(0)
                    else:
                        balances.append(int(float(row[2].strip("$").replace(',',''))))
                    if row[3] == "":
                        logger.debug('Terminal has no float value. Adding Zero to floats list')
                        floats.append(0)
                    else:
                        logger.debug('adding ' + row[3] + ' to floats list.')
                        floats.append(int(float(row[3].strip("$").replace(',',''))))
            # gather results into tuple
            result = tuple(
                ["ATM", "VAULTS:", sum(balances), sum(floats), " = PAI FLOAT"]
            )
            logger.info(result)
            logger.info('Writing output to: ' + out_f)
            csvWriter.writerow(result)
            csvWriter.writerow([rundate, "...with", terminals, " terminals reporting"])
    return True


@logger.catch
def extract_date(fname):
    """ the filename contains the date the report was run
    extract and return the date string
    """
    datestring = 'xxxxxxxx'
    logger.info("Processing: " + str(fname))
    parts = str(fname.stem).split('-')
    for part in parts:
        try:
            datestring = parse(part).strftime("%Y%m%d")
        except ParserError as e:
            logger.debug(f'Error: {e}')

    # sample filename string "Terminal Status(w_FLOAT)automated - 20190822.csv"
    # fn = Path(fname).stem # returns just the filename without extension or folder
    # datestring = fn[-8:] # the last 8 characters represent the datecode
    return datestring


@logger.catch
def look_for_new_csv(match):
    """ Get files and return any match
    """ 
    logger.info(f'Looking for {match}')
    files = list(DL_PATH.glob('*.*'))
    # logger.debug(files)

    CSVs = [f for f in files if f.suffix in [INPUTFILE_EXTENSION]]
    # logger.debug(CSVs)
    num_of_files = str(len(CSVs))

    for fname in CSVs:
        if match in str(fname):
            logger.info("Matched filename: " + str(fname))
            return fname
    return "" # no match found


@logger.catch
def determine_output_filename(datestr, matchedname, output_folder):

    fn = check_and_validate(datestr, output_folder)

    newfilename = f'{fn}_{matchedname}{FILE_TYPE}'
    # TODO check if name already exists and do not overwrite

    return newfilename


@logger.catch
def remove_file(file_path):
    logger.info("Attempting to remove old %s file..." % str(file_path))

    if Path(file_path).exists():
        try:
            Path(file_path).unlink()
        except OSError as e:
            logger.warning("Error: %s - %s." % (e.file_path, e.strerror))
            # sys.exit(1)
        logger.info(f"Success removing {str(file_path)}")
        return 1

    else:
        logger.info("Sorry, could not find %s file." % str(file_path))

    return 0


@logger.catch
def defineLoggers():
    logger.configure(
        handlers=[{"sink": os.sys.stderr, "level": "DEBUG"}]
    )  # this method automatically suppresses the default handler to modify the message level

    #    logger.add(
    #        os.sys.stderr,
    #        format="{time} {level} {message}",
    #        filter="my_module",  # creates an entry showing module name and source code line number
    #        level="INFO",
    #    )  # set a handler

    #    logger.add(
    #        runtime_name + ".log",
    #        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    #    )  # this establishes a file log that gets appended each time the program runs

    logger.add(
        #        runtime_name + "_{time}.log", format=">> <lvl>{message}</lvl>", level="INFO"
        RUNTIME_NAME.name + "_{time}.log",
        level="DEBUG",  # above line would simplify output to message only
    )  # create a new log file for each run of the program
    return


@logger.catch
def process_simple_summary_csv(out_f, in_f, rundate):
    """Scan file and compute sums for 2 columns
    """
    df = panda.read_csv(in_f)
    DAYS = 30
    df = df.rename(columns = {"Location":"Terminal        "}) # attempt to expand columns in excel

    try:
        df['My Surch'].replace( '[\$,)]','', regex=True, inplace=True)
        df['My Surch'] = df['My Surch'].astype(float)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False

    try:
        df['Settlement'].replace( '[\$,)]','', regex=True, inplace=True)
        df['Settlement'] = df['Settlement'].astype(float)    
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False

    try:
        df['WD Trxs'] = df['WD Trxs'].astype(float)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False
    

    def calc(row):
        """Calculate the surcharge earned per withdrawl.
        """
        wd = row['WD Trxs']
        if wd > 0:
            return round(row['My Surch'] / wd, 2)
        else:
            return 0

    try:
        df['WD surch'] = df.apply(lambda row: calc(row), axis=1)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False


    def avgWD(row):
        """Calculate the average amount of withdrawls.
        """
        wd = row['WD Trxs']
        if wd > 0:
            return round(row.Settlement / wd, 2)
        else:
            return 0
    try:
        df['Average WD amount'] = df.apply(lambda row: avgWD(row), axis=1)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False


    def DailyWD(row):
        """Assuming 30 days in report data calculate daily withdrawl total.
        """
        return round(row.Settlement / DAYS, 2)
    try:
        df['Daily Vault AVG'] = df.apply(lambda row: DailyWD(row), axis=1)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False

    # work is finished. Drop unneeded columns from output
    df = df.drop(df.columns[[1, 2, 3, 4]], axis=1)  # df.columns is zero-based pd.Index
    # send output to storage
    try:
        df.to_csv(out_f, quoting=csv.QUOTE_ALL)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False

    return True


@logger.catch
def process_bank_statement_csv(out_f, in_f, rundate):
    """placeholder
    """
    return False


@logger.catch
def Main():
    defineLoggers()
    logger.info("Program Start.")  # log the start of the program
    logger.info(RUNTIME_NAME)
    logger.info("Scanning for download to process...")
    # TODO apply different transforms based on filename found.
    inputfile = ""
    file_types = [
        BASENAME_BANK_STATEMENT,
        EMAIL_BASENAME_FLOATREPORT,
        MANUAL_DL_BASENAME_FLOATEREPORT,
        BASENAME_SIMPLE_SUMMARY
    ]
    process_func = [
        process_bank_statement_csv,
        process_floatReport_csv, 
        process_floatReport_csv,
        process_simple_summary_csv
    ]
    while inputfile == "":
        logger.info(f'Looking in directory: {DL_PATH}')
        for indx, value in enumerate(file_types):
            inputfile = look_for_new_csv(value)

            if inputfile != "" and inputfile != None:

                filedate = extract_date(inputfile)
                output_file = determine_output_filename(filedate, value, OUTPUT_PATH)
                logger.debug(filedate)
                if process_func[indx](output_file, inputfile, filedate):
                    args = os.sys.argv
                    if len(args) > 1 and args[1] == "-np":
                        logger.info("bypassing print option due to '-np' option.")
                        logger.info("bypassing file removal option due to '-np' option.")
                        logger.info("exiting program due to '-np' option.")
                    else:
                        logger.info("Send processed file to printer...")
                        try:
                            os.startfile(output_file, "print")
                        except FileNotFoundError as e:
                            logger.error(f'File not found: {e}')
                        remove_file(inputfile)
                else:
                    logger.error('Input file not processed properly.')
            else:
                logger.info('Nothing found.')

        inputfile = ""  # keep the program running looking for more files
        logger.info("Sleeping 10 seconds")
        sleep(10)
    return


if __name__ == "__main__":
    Main()
