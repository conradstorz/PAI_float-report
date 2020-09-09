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
def process_floatReport_csv(out_f, in_f, RUNDATE):
    """Scan file and compute sums for 2 columns"""
    df = panda.read_csv(in_f)
    DF_LAST_ROW = len(df)
    logger.info(f"Excel file imported into dataframe with {DF_LAST_ROW} rows.")
    # Fields: "Location","Reject Balance","Balance","Today's Float","Route"

    # Add some information to dataframe
    df.at[DF_LAST_ROW, "Reject Balance"] = str(RUNDATE)
    df.at[DF_LAST_ROW, "Location"] = "Report ran"

    FORMATTING_FILE = "ColumnFormatting.json"
    with open(FORMATTING_FILE) as json_data:
        column_details = json.load(json_data)
    # this dictionary will contain information about individual column data type

    DAYS = 30

    try:
        df["Balance"].replace("[\$,)]", "", regex=True, inplace=True)
        df["Balance"] = df["Balance"].astype(float)
    except KeyError as e:
        logger.error(f"KeyError in dataframe: {e}")
        return False

    try:
        df["Today's Float"].replace("[\$,)]", "", regex=True, inplace=True)
        df["Today's Float"] = df["Today's Float"].astype(float)
    except KeyError as e:
        logger.error(f"KeyError in dataframe: {e}")
        return False

    try:
        df["Reject Balance"] = df["Reject Balance"].astype(float)
    except KeyError as e:
        logger.error(f"KeyError in dataframe: {e}")
        return False

    # sum the columns
    df.loc["Totals"] = df.select_dtypes(panda.np.number).sum()
    df.at["Totals", "Location"] = "               Route Totals"

    # work is finished. Drop unneeded columns from output
    # TODO expand this to drop all columns except those desired in the report
    df = df.drop(["Route"], axis=1)  # df.columns is zero-based panda.Index

    # sort the data
    df = df.sort_values("Balance", ascending=False)

    indx = 0
    return {f"Outputfile{indx}.xlsx": df}
