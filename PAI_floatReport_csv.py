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
from dateutil.parser import parse, ParserError
import pandas as panda

# constants


RUNTIME_NAME = Path(__file__)

CSV_EXT = [".csv"]
EXCEL_EXT = ['.xls']

DL_DRIVE = "C:"
DL_USER_BASE = "Users"
DL_USER = "Conrad"
DL_DIRECTORY = "Downloads"
DL_PATH = Path("C:/Users/Conrad/Downloads/")

BASENAME_BANK_STATEMENT = ["BankDepositsStatement", CSV_EXT]
EMAIL_BASENAME_FLOATREPORT = ["Terminal Status(w_FLOAT)automated", CSV_EXT]
MANUAL_DL_BASENAME_FLOATEREPORT = ['TerminalStatuswFLOATautomated3', CSV_EXT] 
BASENAME_SIMPLE_SUMMARY = ["TerminalTrxData", CSV_EXT]
BASENAME_SURCHARGE_MONTHLY_PER_TERMINAL = ['Revenue By Device', EXCEL_EXT]

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
            logger.info(f'Writing output to: {out_f}')
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
def look_for_new_csv(matchName, ext):
    """ Get files and return any match
    """ 
    logger.info(f'Looking for {matchName}')
    files = list(DL_PATH.glob('*.*'))
    # logger.debug(files)
    logger.debug(ext)

    matches = [f for f in files if f.suffix in [ext]]
    # logger.debug(matches)
    num_of_files = str(len(matches))

    for fname in matches:
        if matchName in str(fname):
            logger.info("Matched filename: " + str(fname))
            return fname
    return "" # no match found


@logger.catch
def determine_output_filename(datestr, matchedname, ext, output_folder):
    """Assemble datecode and output folder with original basename into new filename.
    """
    fn = check_and_validate(datestr, output_folder)
    newfilename = Path(f'{fn}_{matchedname}{ext}') # TODO check that name does not yet exist
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
    df = df.drop(df.columns[[1, 2, 3, 4]], axis=1)  # df.columns is zero-based panda.Index
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
def process_monthly_surcharge_report_excel(out_f, in_f, rundate):
    """Uses this report to determine surcharges are correct
    and I am being paid the correct amount when splitting surcharge.
    After reading the data extract: 'Total Business Surcharge',
    'SurWD Trxs', 'Total Surcharge', 'Total Dispensed Amount' and estimate the rest.
    """
    DAYS = 30 # most months are 30 days
    FIXED_ASSETS = 2100 # this is cost of ATM (fixed asset)
    OPERATING_EXPENSES = (8.25 + 25) * 26  # estimated mileage plus estimated labor annualized.
    logger.info('Beginning process of monthly report.')
    logger.info(f'File: {in_f}')

    df = panda.read_excel(in_f)
    dflast = len(df) - 1
    logger.info(f'Excel file imported into dataframe with {dflast + 1} rows.')
    
    # Add some information to dataframe
    df.at[dflast, 'Location'] = str(rundate)
    df.at[dflast, 'Device Number'] = 'Report ran'
    # TODO add disclaimer that many values are estimates for comparison between terminals only.
    # TODO the numbers are estimated but the same assumptions are applied equally to all.

    # these are per row
    """
    Operating_Income = df['Business Total Income'] * 12       # (annualized)
    Surchargeable_WDs = df['SurWD Trxs'] * 12
    Total_Surcharge = df['Total Surcharge'] * 12
    Total_Dispensed_Amount = df['Total Dispensed Amount']
    Average_Surcharge = Operating_Income / Surchargeable_WDs
    Surcharge_Percentage = Operating_Income / Total_Surcharge
    Average_Daily_Dispense = Total_Dispensed_Amount / DAYS
    Current_Assets = Average_Daily_Dispense * 14 # Float plus Vault
    Assets = FIXED_ASSETS + Current_Assets
    Asset_Turnover = Operating_Income / Assets
    Earnings_BIT = Operating_Income - OPERATING_EXPENSES
    Profit_Margin = Earnings_BIT / Operating_Income
    R_O_I = Asset_Turnover * Profit_Margin
    """
    # TODO trap ZeroDivisionErrors
    def Average_Surcharge(row):
        if row['SurWD Trxs'] <= 0: return 0
        return round((row['Business Total Income'] * 12) / (row['SurWD Trxs'] * 12), 2)

    logger.info('Calculating average surcharge per terminal...')
    df['Average_Surcharge'] = df.apply(lambda row: Average_Surcharge(row), axis=1)

    def Surcharge_Percentage(row):
        if row['Total Surcharge'] <= 0: return 0
        return round((row['Business Total Income'] * 12) / (row['Total Surcharge'] * 12), 2)

    logger.info('Calculating surcharge percentage earned per terminal...')
    df['Surcharge_Percentage'] = df.apply(lambda row: Surcharge_Percentage(row), axis=1)   

    def Average_Daily_Dispense(row):
        return round(row['Total Dispensed Amount'] / DAYS, 2)

    logger.info('Calculating average daily dispense per terminal...')
    df['Average_Daily_Dispense'] = df.apply(lambda row: Average_Daily_Dispense(row), axis=1)

    def Current_Assets(row):
        return round(Average_Daily_Dispense(row) * 14, 2)

    logger.info('Calculating estimated vault load per terminal...')
    df['Current_Assets'] = df.apply(lambda row: Current_Assets(row), axis=1)

    def Assets(row):
        return round(FIXED_ASSETS + Current_Assets(row), 2)

    logger.info('Calculating estimated investment per terminal...')
    df['Assets'] = df.apply(lambda row: Assets(row), axis=1)

    def Asset_Turnover(row):
        return round((row['Business Total Income'] * 12) / Assets(row), 2)

    logger.info('Calculating estimated asset turns per terminal...')
    df['Asset_Turnover'] = df.apply(lambda row: Asset_Turnover(row), axis=1)

    def Earnings_BIT(row):
        return round((row['Business Total Income'] * 12) - OPERATING_EXPENSES, 2)

    logger.info('Calculating estimated EBIT per terminal...')
    df['Earnings_BIT'] = df.apply(lambda row: Earnings_BIT(row), axis=1)

    def Profit_Margin(row):
        if row['Business Total Income'] <= 0: return 0
        return round(Earnings_BIT(row) / (row['Business Total Income'] * 12), 2)

    logger.info('Calculating estimated profit margin per terminal...')
    df['Profit_Margin'] = df.apply(lambda row: Profit_Margin(row), axis=1)
    
    def R_O_I(row):
        return round(Asset_Turnover(row) * Profit_Margin(row), 2)

    logger.info('Calculating estimated ROI per terminal...')
    df['R_O_I'] = df.apply(lambda row: R_O_I(row), axis=1)


    logger.info('work is finished. Drop un-needed columns...') 
    df = df.drop(df.columns[[0,1,4,5,6,7,8,10,13,14,18,19,20]], axis=1)  # df.columns is zero-based panda.Index

    logger.info('formatting column widths and styles...') 
    # define column formats
    a,n,c,p = 'A#$%'
    formats = [a,n,c,c,c,c,c,p,p,c,p,p]
    # attempt to set column widths
    writer = panda.ExcelWriter(out_f, engine='xlsxwriter')
    df.to_excel(writer, startrow = 1, sheet_name='Sheet1', index=False)
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

    logger.info('All work done. Saving worksheet...') 
    writer.save()    

    logger.info('Finished.') 
    return True



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
        BASENAME_SIMPLE_SUMMARY,
        BASENAME_SURCHARGE_MONTHLY_PER_TERMINAL
    ]
    process_func = [
        process_bank_statement_csv,
        process_floatReport_csv, 
        process_floatReport_csv,
        process_simple_summary_csv,
        process_monthly_surcharge_report_excel
    ]
    while inputfile == "":
        logger.info(f'Looking in directory: {DL_PATH}')
        for indx, value in enumerate(file_types):
            basename = value[0]
            extension = value[1]
            for ext in extension:
                inputfile = look_for_new_csv(basename, ext)
                if inputfile != "" and inputfile != None:
                    filedate = extract_date(inputfile)
                    output_file = determine_output_filename(filedate, basename, ext, OUTPUT_PATH)
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
