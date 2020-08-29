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
    DAYS = 30 # most months are 30 days
    FIXED_ASSETS = 2100 # this is cost of ATM (fixed asset)
    OPERATING_EXPENSES = (8.25 + 25) * 26  # estimated mileage plus estimated labor annualized.
    logger.info('Beginning process of monthly report.')
    logger.info(f'File: {in_f}')

    df = panda.read_excel(in_f)
    dflast = len(df) - 1
    logger.info(f'Excel file imported into dataframe with {dflast + 1} rows.')
    
    # slice the terminal numbers and write to temp storage
    t = df['Device Number']
    t.to_json('temp.json')
    # TODO use this to determine which new terminals are missing from value lookup

    with open(VALUE_FILE) as json_data:
        data = json.load(json_data)
    # this dictionary will contain information about individual terminals

    # Add some information to dataframe
    df.at[dflast, 'Location'] = str(rundate)
    df.at[dflast, 'Device Number'] = 'Report ran'
    # TODO add disclaimer that many values are estimates for comparison between terminals only.
    # TODO the numbers are estimated but the same assumptions are applied equally to all.


    """This is a cheat sheet to values used in a dupont analysis
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
        try:
            FA = float(data[row['Device Number']]['Value'])
        except KeyError as e:
            return 0
        else:
            return round(FA + Current_Assets(row), 2)

    logger.info('Calculating estimated investment per terminal...')
    df['Assets'] = df.apply(lambda row: Assets(row), axis=1)

    def Asset_Turnover(row):
        if Assets(row) != 0:
            return round((row['Business Total Income'] * 12) / Assets(row), 2)
        else:
            return 0

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

    # sort data
    df = df.sort_values('Earnings_BIT',ascending=False)

    # define column formats
    writer = panda.ExcelWriter(out_f, engine='xlsxwriter')
    df.to_excel(writer, startrow = 1, sheet_name='Sheet1', index=False)    
    a,n,c,p = 'A#$%'
    formats = [a,n,c,c,c,c,c,p,p,c,p,p]
    set_custom_excel_formatting(df, writer, formats)

    logger.info('All work done. Saving worksheet...') 
    writer.save()    

    logger.info('Finished.') 
    return True
