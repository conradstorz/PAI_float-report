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
def process_monthly_surcharge_report_excel(out_f, in_f, rundate):
    """Uses this report to determine surcharges are correct
    and I am being paid the correct amount when splitting surcharge.
    After reading the data extract: 'Total Business Surcharge',
    'SurWD Trxs', 'Total Surcharge', 'Total Dispensed Amount' and estimate the rest.
    """
    VALUE_FILE = 'TerminalValues.json'
    FORMATTING_FILE = 'ColumnFormatting.json'
    OUTPUT_FILE = 'SurchargeReportVariations.json'

    DAYS = 30 # most months are 30 days and report covers a month
    OPERATING_LABOR = 25  # estimated labor per visit.
    logger.info('Beginning process of monthly report.')
    logger.info(f'File: {in_f}')

    def moveLast2first(df):
        cols = df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        return df[cols]

    df = panda.read_excel(in_f)
    dflast = len(df) - 1
    logger.info(f'Excel file imported into dataframe with {dflast + 1} rows.')
    
    # slice the terminal numbers and write to temp storage
    t = df['Device Number']
    t.to_json('temp.json')
    # TODO use this to determine which new terminals are missing from value lookup

    with open(VALUE_FILE) as json_data:
        terminal_details = json.load(json_data)
    # this dictionary will contain information about individual terminals
    VF_KEY_Ownership = "Owned"
    VF_KEY_Value = 'Value'
    VF_KEY_VisitDays = 'Visit Days'
    VF_KEY_TravelCost = 'Travel Cost'
    VF_KEY_Commissions = 'Commission'

    with open(FORMATTING_FILE) as json_data:
        column_details = json.load(json_data)
    # this dictionary will contain information about individual terminals   

    with open(OUTPUT_FILE) as json_data:
        output_details = json.load(json_data)
    # this dictionary will contain information about individual terminals  

    # Add some information to dataframe
    df.at[dflast, 'Location'] = str(rundate)
    df.at[dflast, 'Device Number'] = 'Report ran'
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

    def Commissions_due(row):
        try:
            commrate = float(terminal_details[row['Device Number']][VF_KEY_Commissions])
        except KeyError as e:
            logger.error(f'KeyError: {e}')
            commrate = 0
        return round(row['SurWD Trxs'] * commrate, 2)
    logger.info('Calculating commission due...')
    df['Commission Due'] = df.apply(lambda row: Commissions_due(row), axis=1)
    column_details['Commission Due'] = "$"

    def Annual_Net_Income(row):
        return float((row['Business Total Income'] - row['Commission Due']) * 12)
    logger.info('Calculating annual net income...')
    df['Annual_Net_Income'] = df.apply(lambda row: Annual_Net_Income(row), axis=1)
    df = moveLast2first(df)
    column_details['Annual_Net_Income'] = "$"

    def Annual_SurWDs(row):
        return int(row['SurWD Trxs'] * 12)
    logger.info('Calculating annual surchargeable WDs...')
    df['Annual_SurWDs'] = df.apply(lambda row: Annual_SurWDs(row), axis=1)
    column_details['Annual_SurWDs'] = "#"

    def Average_Surcharge(row):
        if row['SurWD Trxs'] == 0: return 0
        return round(row['Annual_Net_Income'] / row['Annual_SurWDs'], 2)
    logger.info('Calculating average surcharge per terminal...')
    df['surch'] = df.apply(lambda row: Average_Surcharge(row), axis=1)
    df = moveLast2first(df)
    column_details['surch'] = "$"

    def Surcharge_Percentage(row):
        if row['Total Surcharge'] == 0: return 0
        return round(row['Annual_Net_Income'] / (row['Total Surcharge'] * 12), 2)
    logger.info('Calculating surcharge percentage earned per terminal...')
    df['Surcharge_Percentage'] = df.apply(lambda row: Surcharge_Percentage(row), axis=1)   
    column_details['Surcharge_Percentage'] = "%"

    def Average_Daily_Dispense(row):
        return round(row['Total Dispensed Amount'] / DAYS, 2)
    logger.info('Calculating average daily dispense per terminal...')
    df['Average_Daily_Dispense'] = df.apply(lambda row: Average_Daily_Dispense(row), axis=1)
    df = moveLast2first(df)
    column_details['Average_Daily_Dispense'] = "$"

    def Current_Assets(row):
        buffer = 1.5
        try: 
            visits = float(terminal_details[row['Device Number']][VF_KEY_VisitDays])
            if terminal_details[row['Device Number']][VF_KEY_Ownership] == 'No':
                return 0  # there are no current assets for terminal loaded with other peoples money.
            else:
                return round(row['Average_Daily_Dispense'] * visits * buffer, 2)
        except KeyError as e:
            logger.error(f'Key error: {e}')
            return 0
    logger.info('Calculating estimated vault load per terminal...')
    df['Current_Assets'] = df.apply(lambda row: Current_Assets(row), axis=1)
    column_details['Current_Assets'] = "$"

    def Assets(row):
        try:
            FA = float(terminal_details[row['Device Number']][VF_KEY_Value])
        except KeyError as e:
            logger.error(f'KeyError: {e}')
            return 0
        else:
            return round(FA + row['Current_Assets'] , 2)
    logger.info('Calculating estimated investment per terminal...')
    df['Assets'] = df.apply(lambda row: Assets(row), axis=1)
    column_details['Assets'] = "$"

    def Asset_Turnover(row):
        if row['Assets'] != 0:
            return round(row['Annual_Net_Income'] / row['Assets'], 2)
        else:
            return 0
    logger.info('Calculating estimated asset turns per terminal...')
    df['Asset_Turnover'] = df.apply(lambda row: Asset_Turnover(row), axis=1)
    column_details['Asset_Turnover'] = "%"

    def Earnings_BIT(row):
        """Use data stored in .json file to customize each terminal
        """
        try:
            Visit = float(terminal_details[row['Device Number']][VF_KEY_VisitDays])
            Travl = float(terminal_details[row['Device Number']][VF_KEY_TravelCost])
            annual_operating_cost = (365 / Visit) * (Travl + OPERATING_LABOR)
        except KeyError as e:
            logger.error(f'KeyError: {e}')
            annual_operating_cost = 0 
        result = round(row['Annual_Net_Income'] - annual_operating_cost, 2)
        return result
    logger.info('Calculating estimated EBIT per terminal...')
    df['Earnings_BIT'] = df.apply(lambda row: Earnings_BIT(row), axis=1)
    df = moveLast2first(df)
    column_details['Earnings_BIT'] = "$"

    def Profit_Margin(row):
        if row['Annual_Net_Income'] == 0: return 0
        return round(row['Earnings_BIT'] / row['Annual_Net_Income'], 2)
    logger.info('Calculating estimated profit margin per terminal...')
    df['Profit_Margin'] = df.apply(lambda row: Profit_Margin(row), axis=1)
    df = moveLast2first(df)
    column_details['Profit_Margin'] = "%"

    def R_O_I(row):
        return round(row['Asset_Turnover'] * row['Profit_Margin'], 2)
    logger.info('Calculating estimated ROI per terminal...')
    df['R_O_I'] = df.apply(lambda row: R_O_I(row), axis=1)
    df = moveLast2first(df)
    column_details['R_O_I'] = "%"

    logger.info('work is finished. Drop un-needed columns...') 
    # TODO expand this to drop all columns except those desired in the report
    df = df.drop([output_details['Standard']], axis=1)  # df.columns is zero-based panda.Index

    # sort data
    try:
        #logger.debug(df)
        df = df.sort_values('Earnings_BIT',ascending=False)
    except KeyError as e:
        logger.error(f'KeyError: {e}   # This error does not make sense.') 
        #logger.debug(df)

    # define column formats
    writer = panda.ExcelWriter(out_f, engine='xlsxwriter')
    df.to_excel(writer, startrow = 1, sheet_name='Sheet1', index=False)    
    set_custom_excel_formatting(df, writer, column_details)

    logger.info('All work done. Saving worksheet...') 
    writer.save()    

    logger.info('Finished.') 
    return True
