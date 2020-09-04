#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Munge spreadsheet data.
Takes and input file Path obj, and output file Path obj,
and a rundate string and then makes calculations and returns an output version
of the spreadsheet in dataframe format.
"""

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
    # this dictionary will contain information about individual column data type

    DAYS = 30

    """
    Depending on the amount of detail in the report from PAI this dataframe may include more than one row
    for each location. When only one row contains information on an individual location then the file lacks any
    indication of WHEN the report covers. We can get the date of the report being created by PAI from the
    filename but the time range covered by the report won't be included.

    When the report has MULTIPLE lines for each LOCATION then each line contains a datestring. These datestrings
    can be converted to datetimes and sorted to find the earliest and latest dates in the report.
    print(dft2) # sample dataframe of timestamps
0    2019-12-01
1    2019-12-02
2    2019-12-03
3    2019-12-04
4    2019-12-05
5    2019-12-06
6    2019-12-07
7    2019-12-08
8    2019-12-09
9    2019-12-10
10   2019-12-11
11   2019-12-12
12   2019-12-13
13   2019-12-14
14   2019-12-15
15   2019-12-16
16   2019-12-17
17   2019-12-18
18   2019-12-19
19   2019-12-20
20   2019-12-21
21   2019-12-22
22   2019-12-23
23   2019-12-24
24   2019-12-25
25   2019-12-26
26   2019-12-27
27   2019-12-28
28   2019-12-29
29   2019-12-30
30   2019-12-31
Name: Settlement Date, dtype: datetime64[ns]

dft2.astype(str).max()
'2019-12-31'
dft2.astype(str).min()
'2019-12-01'
    """


    try:
        # TODO standardize the function that strips extra characters from a numeric string
        # e.g. df[?] = strip2float(df[?])
        # try to recognize as many standard strings as possible. $1 ($1) -$1 $-1,234.876 etc
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

    indx = 0
    return {f'Outputfile{indx}.xlsx': df}
