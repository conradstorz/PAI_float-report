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
# Custom function to serialize the dictionary excluding unserializable objects
def custom_json_serializer(obj):
    # usage example: pretty_dict = json.dumps(dict, default=custom_json_serializer, indent=4)
    if isinstance(obj, (int, float, str, bool, list, tuple, dict, type(None))):
        return obj
    else:
        return str(obj)
    
from customize_dataframe_for_excel import set_custom_excel_formatting

def validate_value(value, min_value=0, max_value=float('inf')):
    """Validate if the value is within the expected range and is not negative.

    Args:
        value (float): The value to validate.
        min_value (float): The minimum acceptable value. Defaults to 0.
        max_value (float): The maximum acceptable value. Defaults to infinity.

    Returns:
        bool: True if value is valid, False otherwise.
    """
    if value < min_value or value > max_value:
        return False
    return True


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

    VALUE_FILE = "Terminal_Details.json"  # data concerning investment value and commissions due and operational expenses
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
    logger.debug(Input_df.columns)

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
    # Pretty print and log the dictionary item
    pretty_json = json.dumps(terminal_details, default=custom_json_serializer, indent=4)
    logger.debug(f'Printer details report:{pretty_json}')
    VF_KEY_Owned = "Owned"
    VF_KEY_Value = "Value"
    VF_KEY_VisitDays = "Visit Days"
    VF_KEY_TravelCost = "Travel Cost"
    VF_KEY_SurchargeEarned = "Surcharge Earned"
    VF_KEY_Commission_rate = "Comm Rate paid"

    logger.info(f"Reading formatting file..")
    with open(FORMATTING_FILE) as json_data:
        column_details = json.load(json_data)
    # this dictionary will contain information about formating output values.
    # Pretty print and log the dictionary item
    pretty_json = json.dumps(column_details, default=custom_json_serializer, indent=4)
    logger.debug(f'Printer details report:{pretty_json}')
    # Add some information to dataframe. rows are Zero based so this location is 1 past last row.
    # TODO is this working???
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
    # These names must match the input dataframe columns
    BizGrossIncome = "Business Total Income"
    TOTSUR = "Total Surcharge"
    TOTDISP = "Total Dispensed Amount"
    SURCHXACTS = "SurWD Trxs"
    TOTALXACTS = "Total Trxs"
    TOTALINTRCHANGE ="Total Interchange"

    # These names are added to the original input dataframe
    COMM = "Comm_Due"
    AnnualNetIncome = "Annual_Net_Income"
    ASURWD = "Annual_SurWDs"
    SURCH = "_surch"
    SURCHPER = "_Surch%"
    DAYDISP = "Daily_Dispense"
    CURASS = "Current_Assets"
    ASSETS = "_Assets"
    ASSETSTO = "A_T_O"
    ERNBIT = "Earnings_BIT"
    PRFTMGN = "p_Margin"
    RTNONINV = "R_O_I"

    def Commissions_due(row):
        try:
            commrate = float(
                terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_Commission_rate]
            )
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            commrate = 0
        logger.debug(f'Device: {row[DEVICE_NUMBER_TAG]}, Commrate: {commrate}, Xacts: {row[SURCHARGEABLE_WITHDRAWL_TRANSACTIONS_TAG]}')
        return round(row[SURCHARGEABLE_WITHDRAWL_TRANSACTIONS_TAG] * commrate, 2)

    logger.info("Calculating commission due...")
    logger.debug(Input_df.columns)
    Input_df[COMM] = Input_df.apply(lambda row: Commissions_due(row), axis=1)
    column_details[COMM] = "$"


    def Annual_Net_Income(row):
        try:
            ta = row[BizGrossIncome]  # Total annual income
            cm = row[COMM]  # Commission
        except KeyError as e:
            logger.error(f"Column not found: {e}")
            ta, cm = 0, 0
        annual_net_income = float((ta - cm) * 12)
        # Validate the annual net income here
        if not validate_value(annual_net_income, min_value=0):  # Assuming you don't expect negative net income
            logger.warning(f"Unexpected negative Annual Net Income for device {row[DEVICE_NUMBER_TAG]}: {annual_net_income}")
            logger.warning(f"Gross Income: {row[BizGrossIncome]}, Commission: {row[COMM]}")
        return annual_net_income


    logger.info("Calculating annual net income...")
    Input_df[AnnualNetIncome] = Input_df.apply(
        lambda row: Annual_Net_Income(row), axis=1
    )
    Input_df = moveLast2first(Input_df)
    column_details[AnnualNetIncome] = "$"

    def Annual_SurWDs(row):
        try:
            result = int(row[SURCHARGEABLE_WITHDRAWL_TRANSACTIONS_TAG] * 12)
        except ValueError as e:
            if row[DEVICE_NUMBER_TAG] == "Report ran":
                pass
            else:
                logger.error(f"{row[DEVICE_NUMBER_TAG]}, Surchargeable Xact: {row[SURCHARGEABLE_WITHDRAWL_TRANSACTIONS_TAG]}: {e}")
            return 0
        return result

    logger.info("Calculating annual surchargeable WDs...")
    Input_df[ASURWD] = Input_df.apply(lambda row: Annual_SurWDs(row), axis=1)
    column_details[ASURWD] = "#"

    def Average_Surcharge(row):
        try:
            result = round(row[AnnualNetIncome] / row[ASURWD], 2)
        except ZeroDivisionError:  # catches 'NaN' and 0
            return 0
        return result

    logger.info("Calculating average surcharge per terminal...")
    Input_df[SURCH] = Input_df.apply(lambda row: Average_Surcharge(row), axis=1)
    Input_df = moveLast2first(Input_df)
    column_details[SURCH] = "$"

    def Surcharge_Percentage(row):
        try:
            result = round(row[AnnualNetIncome] / (row[TOTSUR] * 12), 2)
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
            if terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_Owned] == "No":
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
        if not validate_value(row[AnnualNetIncome], min_value=0) or not validate_value(row[ASSETS], min_value=1):  # Ensure assets are > 0
            logger.warning(f"Invalid values for Asset Turnover calculation for device {row[DEVICE_NUMBER_TAG]}")
            logger.warning(f"Income: {row[AnnualNetIncome]}, Assets: {row[ASSETS]}")
            return 0
        try:
            result = round(row[AnnualNetIncome] / row[ASSETS], 2)
        except ZeroDivisionError as e:
            logger.error(f"Division by Zero: {e}")
            return 0
        return result

    logger.info("Calculating estimated asset turns per terminal...")
    Input_df[ASSETSTO] = Input_df.apply(lambda row: Asset_Turnover(row), axis=1)
    column_details[ASSETSTO] = "%"


    def Earnings_BIT(row):
        logger.debug(f"Row: {row}")
        try:
            Visit = float(terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_VisitDays])
            Travl = float(terminal_details[row[DEVICE_NUMBER_TAG]][VF_KEY_TravelCost])
            # Validate Visit and Travl values
            if not validate_value(Visit, min_value=1) or not validate_value(Travl, min_value=0):
                logger.warning(f"Invalid Visit or Travl values for device {row[DEVICE_NUMBER_TAG]}")
                return 0  # or handle as deemed appropriate
            annual_operating_cost = (365 / Visit) * (Travl + OPERATING_LABOR)
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            annual_operating_cost = 0
        result = round(row[AnnualNetIncome] - annual_operating_cost, 2)
        return result


    logger.info("Calculating estimated EBIT per terminal...")
    Input_df[ERNBIT] = Input_df.apply(lambda row: Earnings_BIT(row), axis=1)
    Input_df = moveLast2first(Input_df)
    column_details[ERNBIT] = "$"

    def Profit_Margin(row):
        try:
            result = round(row[ERNBIT] / row[AnnualNetIncome], 2)
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
    # Pretty print and log the dictionary item
    pretty_json = json.dumps(column_details, default=custom_json_serializer, indent=4)
    logger.debug(f'Formatting file re-written:{pretty_json}')        

    with open(REPORT_DEFINITIONS_FILE) as json_data:
        output_options = json.load(json_data)
    # this dictionary will contain information about individual reports
    # Pretty print and log the dictionary item
    pretty_json = json.dumps(output_options, default=custom_json_serializer, indent=4)
    logger.debug(f'Report Definitions File:{pretty_json}')        

    # print these reports
    CURRENT_REPORTS = ["Commission", "Surcharge", "Dupont"]

    frames = {}
    for indx, report in enumerate(CURRENT_REPORTS):
        # create a unique filename
        fn = f"Outputfile{indx}.xlsx"
        # Creating an empty Dataframe with column names only
        frames[fn] = panda.DataFrame(columns=output_options[report])
        # fill those columns with data
        for column in output_options[report]:
            try:
                frames[fn][column] = Input_df[column]
            except KeyError as e:
                logger.error(f"Key Error: {e}")
        # ??? smoething inserted at the end ???
        frames[fn].at[INPUTDF_TOTAL_ROWS + 1, LOCATION_TAG] = report
    return frames
