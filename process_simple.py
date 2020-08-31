#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Munge spreadsheet data.
Takes and input file Path obj, and output file Path obj,
and a rundate string and then makes calculations and returns an output version
of the spreadsheet in dataframe format.
"""

import csv
from loguru import logger
import pandas as panda
import json
from customize_dataframe_for_excel import set_custom_excel_formatting


@logger.catch
def process_simple_summary_csv(out_f, in_f, rundate):
    """Scan file and compute sums for 2 columns
    """
    df = panda.read_csv(in_f)

    FORMATTING_FILE = 'ColumnFormatting.json'
    with open(FORMATTING_FILE) as json_data:
        column_details = json.load(json_data)
    # this dictionary will contain information about individual terminals

    DAYS = 30

    try:
        df['Surch'].replace( '[\$,)]','', regex=True, inplace=True)
        df['Surch'] = df['Surch'].astype(float)
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
            return round(row['Surch'] / wd, 2)
        else:
            return 0

    try:
        df['Surcharge amt'] = df.apply(lambda row: calc(row), axis=1)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False


    def avgWD(row):
        """Calculate the average amount of withdrawls.
        """
        wd = row['WD Trxs']
        if wd > 0:
            return round(row['Settlement'] / wd, 2)
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
        return round(row['Settlement'] / DAYS, 2)
    try:
        df['Daily Vault AVG'] = df.apply(lambda row: DailyWD(row), axis=1)
    except KeyError as e:
        logger.error(f'KeyError in dataframe: {e}')
        return False

    # work is finished. Drop unneeded columns from output
    # TODO expand this to drop all columns except those desired in the report
    df = df.drop([
                'Settlement Date'
                ], axis=1)  # df.columns is zero-based panda.Index

    # sort the data
    df = df.sort_values('Surch',ascending=False)

    # define column formats
    writer = panda.ExcelWriter(out_f, engine='xlsxwriter')
    df.to_excel(writer, startrow = 1, sheet_name='Sheet1', index=False)    
    set_custom_excel_formatting(df, writer, column_details)

    logger.info('All work done. Saving worksheet...') 
    writer.save()    

    logger.info('Finished.')     
    return True
