#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Munge spreadsheet data.
Takes an input file Path obj, and a rundate string 
and then makes calculations and returns an output version
of the spreadsheet in dataframe format.
"""
# TODO Place ALL dataframe tags into CONSTANTS to avoid errors when updating tags.

from loguru import logger
import pandas as panda
import json
from customize_dataframe_for_excel import set_custom_excel_formatting


@logger.catch
def process_monthly_surcharge_report_excel(_out_f, in_f, RUNDATE):
    """Uses this "Payment Alliance International (PAI) website" report to determine surcharges are correct
    and I am being paid the correct amount when splitting surcharge. If a location earns commission it is calculated.
    After reading the data extract:
    'Total Business Surcharge', 'SurWD Trxs', 'Total Surcharge', 'Total Dispensed Amount' and estimate the rest.
    """
    # TODO Create list of immutable keys from imported data and mutable keys from this script.
    # pandas tags:
    LOCATION_TAG = "Location"
    DEVICE_NUMBER_TAG = "Device Number"
    SURCHARGEABLE_WITHDRAWL_TRANSACTIONS_TAG = "SurWD Trxs"

    VALUE_FILE = "TerminalValues.json"  # data concerning investment value and commissions due and operational expenses
    FORMATTING_FILE = "ColumnFormatting.json"  # data describing formatting of data such as integer, date, float, string
    REPORT_DEFINITIONS_FILE = "SurchargeReportVariations.json"  # this dictionary will contain information about individual reports layouts

    DAYS = 30  # most months are 30 days and report covers a month
    # TODO not all reports are 30 days. Some are 90 days. Try to determine actual number of days.
    OPERATING_LABOR = 25  # estimated labor per visit in dollars.
    logger.info("Beginning process of monthly report.")
    logger.info(f"File: {in_f}")

    def moveLast2first(df):
        cols = df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        return df[cols]

    Input_df = panda.read_excel(in_f)

    INPUTDF_TOTAL_ROWS = len(Input_df)

    logger.info(f"Excel file imported into dataframe with {INPUTDF_TOTAL_ROWS} rows.")

    # TODO combine entries that reference the same terminal in different months.
    #       ...Reports that cover more than 1 month have seperate lines for each monthly period.
    Input_df = Input_df.groupby(
        [Input_df[LOCATION_TAG], Input_df[DEVICE_NUMBER_TAG]], as_index=False
    ).sum(numeric_only=True)
    INPUTDF_TOTAL_ROWS = len(Input_df)
    logger.info(
        f"{INPUTDF_TOTAL_ROWS} rows remain after combining identical locations."
    )

    # slice the terminal numbers and write to temp storage
    try:
        t = Input_df[DEVICE_NUMBER_TAG]
        t.to_json("temp.json", indent=4)
        # TODO use this to determine which new terminals are missing from value lookup
    except KeyError as e:
        logger.error(f"Error {e}")

    with open(VALUE_FILE) as json_data:
        terminal_details = json.load(json_data)
    # this dictionary will contain information about individual terminals
    VF_KEY_Ownership = "Owned"
    VF_KEY_Value = "Value"
    VF_KEY_VisitDays = "Visit Days"
    VF_KEY_TravelCost = "Travel Cost"
    VF_KEY_Commissions = "Commission"

    with open(FORMATTING_FILE) as json_data:
        column_details = json.load(json_data)
    # this dictionary will contain information about formating output values.

    # Add some information to dataframe. rows are Zero based so this location is 1 past last row.
    Input_df.at[INPUTDF_TOTAL_ROWS, LOCATION_TAG] = str(RUNDATE)
    Input_df.at[INPUTDF_TOTAL_ROWS, DEVICE_NUMBER_TAG] = "Report ran"
    # TODO add disclaimer that many values are estimates for comparison between terminals only.
    # TODO the numbers are estimated but the same assumptions are applied equally to all.

    """
    Commission_due = df['SurWD Trxs'] * terminal_details[VF_KEY_Commissions]
    ***This is a cheat sheet to values used in a dupont analysis
    Annual_Net_Income = (df['Business Total Income'] - Commission_due) * 12       # (annualized)
    Annual_WDs = df['SurWD Trxs'] * 12
    Annual_Gross_Surcharge = df['Total Surcharge'] * 12
    Period_Dispensed_Amount = df['Total Dispensed Amount']
    Average_Surcharge = Annual_Net_Income / Annual_WDs
    Surcharge_Percentage = Annual_Net_Income / Annual_Gross_Surcharge
    Average_Daily_Dispense = Period_Dispensed_Amount / DAYS
    Current_Assets = Average_Daily_Dispense * 14 # Float plus Vault
    Assets = FIXED_ASSETS + Current_Assets
    Asset_Turnover = Annual_Net_Income / Assets
    Earnings_BIT = Annual_Net_Income - OPERATING_EXPENSES
    Profit_Margin = Earnings_BIT / Annual_Net_Income
    R_O_I = Asset_Turnover * Profit_Margin
    """
    BIZTA = "Business Total Income"
    COMM = "Comm Due"
    ANETI = "Annual_Net_Income"
    ASURWD = "Annual_SurWDs"
    SURCH = "surch"
    TOTSUR = "Total Surcharge"
    SURCHPER = "Surch%"
    TOTDISP = "Total Dispensed Amount"
    DAYDISP = "Daily_Dispense"
    CURASS = "Current_Assets"
    ASSETS = "Assets"
    ASSETSTO = "A_T_O"
    ERNBIT = "Earnings_BIT"
    PRFTMGN = "p_Margin"
    RTNONINV = "R_O_I"

    def Commissions_due(row):
        try:
            commrate = float(
                terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_Commissions]
            )
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            commrate = 0
        return round(row[SURCHARGEABLE_WITHDRAWL_TRANSACTIONS_TAG] * commrate, 2)

    logger.info("Calculating commission due...")
    Input_df[COMM] = Input_df.apply(lambda row: Commissions_due(row), axis=1)
    column_details[COMM] = "$"

    def Annual_Net_Income(row):
        return float((row[BIZTA] - row[COMM]) * 12)

    logger.info("Calculating annual net income...")
    Input_df[ANETI] = Input_df.apply(
        lambda row: Annual_Net_Income(row), axis=1
    )
    Input_df = moveLast2first(Input_df)
    column_details[ANETI] = "$"

    def Annual_SurWDs(row):
        try:
            result = int(row[SURCHARGEABLE_WITHDRAWL_TRANSACTIONS_TAG] * 12)
        except ValueError:
            return 0
        return result

    logger.info("Calculating annual surchargeable WDs...")
    Input_df[ASURWD] = Input_df.apply(lambda row: Annual_SurWDs(row), axis=1)
    column_details[ASURWD] = "#"

    def Average_Surcharge(row):
        try:
            result = round(row[ANETI] / row[ASURWD], 2)
        except ZeroDivisionError:  # catches 'NaN' and 0
            return 0
        return result

    logger.info("Calculating average surcharge per terminal...")
    Input_df[SURCH] = Input_df.apply(lambda row: Average_Surcharge(row), axis=1)
    Input_df = moveLast2first(Input_df)
    column_details[SURCH] = "$"

    def Surcharge_Percentage(row):
        try:
            result = round(row[ANETI] / (row[TOTSUR] * 12), 2)
        except ZeroDivisionError:  # catches 'NaN' and 0
            return 0
        return result

    logger.info("Calculating surcharge percentage earned per terminal...")
    Input_df[SURCHPER] = Input_df.apply(lambda row: Surcharge_Percentage(row), axis=1)
    column_details[SURCHPER] = "%"

    def Average_Daily_Dispense(row):
        return round(row[TOTDISP] / DAYS, 2)

    logger.info("Calculating average daily dispense per terminal...")
    Input_df[DAYDISP] = Input_df.apply(
        lambda row: Average_Daily_Dispense(row), axis=1
    )
    Input_df = moveLast2first(Input_df)
    column_details[DAYDISP] = "$"

    def Current_Assets(row):
        buffer = 1.5
        try:
            # TODO look for missing terminal details and create a placeholder for those.
            # that will fix this issue of try/except need.
            visits = float(terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_VisitDays])
            if terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_Ownership] == "No":
                return 0  # there are no current assets for terminal loaded with other peoples money.
            else:
                return round(row[DAYDISP] * visits * buffer, 2)
        except KeyError as e:
            logger.error(f"Key error: {e}")
            return 0

    logger.info("Calculating estimated vault load per terminal...")
    Input_df[CURASS] = Input_df.apply(lambda row: Current_Assets(row), axis=1)
    column_details[CURASS] = "$"

    def Assets(row):
        try:
            FA = float(terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_Value])
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            return 0
        else:
            return round(FA + row[CURASS], 2)

    logger.info("Calculating estimated investment per terminal...")
    Input_df[ASSETS] = Input_df.apply(lambda row: Assets(row), axis=1)
    column_details[ASSETS] = "$"

    def Asset_Turnover(row):
        try:
            result = round(row[ANETI] / row[ASSETS], 2)
        except ZeroDivisionError:  # catches 'NaN' and 0
            return 0
        return result

    logger.info("Calculating estimated asset turns per terminal...")
    Input_df[ASSETSTO] = Input_df.apply(lambda row: Asset_Turnover(row), axis=1)
    column_details[ASSETSTO] = "%"

    def Earnings_BIT(row):
        """Use data stored in .json file to customize each terminal"""
        # TODO sort the entire DF on this field.
        try:
            Visit = float(terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_VisitDays])
            Travl = float(terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_TravelCost])
            annual_operating_cost = (365 / Visit) * (Travl + OPERATING_LABOR)
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            annual_operating_cost = 0
        result = round(row[ANETI] - annual_operating_cost, 2)
        return result

    logger.info("Calculating estimated EBIT per terminal...")
    Input_df[ERNBIT] = Input_df.apply(lambda row: Earnings_BIT(row), axis=1)
    Input_df = moveLast2first(Input_df)
    column_details[ERNBIT] = "$"

    def Profit_Margin(row):
        try:
            result = round(row[ERNBIT] / row[ANETI], 2)
        except ZeroDivisionError:  # catches 'NaN' and 0
            return 0
        return result

    logger.info("Calculating estimated profit margin per terminal...")
    Input_df[PRFTMGN] = Input_df.apply(lambda row: Profit_Margin(row), axis=1)
    Input_df = moveLast2first(Input_df)
    column_details[PRFTMGN] = "%"

    def R_O_I(row):
        return round(row[ASSETSTO] * row[PRFTMGN], 2)

    logger.info("Calculating estimated ROI per terminal...")
    Input_df[RTNONINV] = Input_df.apply(lambda row: R_O_I(row), axis=1)
    Input_df = moveLast2first(Input_df)
    column_details[RTNONINV] = "%"

    logger.info("work is finished. Create outputs...")

    # update the column output formatting rules
    with open(FORMATTING_FILE, "w") as json_data:
        json.dump(column_details, json_data, indent=4)

    with open(REPORT_DEFINITIONS_FILE) as json_data:
        output_options = json.load(json_data)
    # this dictionary will contain information about individual reports
    CURRENT_REPORTS = ["Commission", "Surcharge", "Dupont"]

    frames = {}
    for indx, report in enumerate(CURRENT_REPORTS):
        # create a unique filename
        fn = f"Outputfile{indx}.xlsx"
        # Creating an empty Dataframe with column names only
        frames[fn] = panda.DataFrame(columns=output_options[report])
        for column in output_options[report]:
            frames[fn][column] = Input_df[column]
        frames[fn].at[INPUTDF_TOTAL_ROWS + 1, LOCATION_TAG] = report
    return frames
