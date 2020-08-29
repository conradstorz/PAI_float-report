#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Munge spreadsheet data.
Takes and input file Path obj, and output file Path obj,
and a rundate string and then makes calculations and returns an output version
of the spreadsheet in csv format.
"""

import csv
from loguru import logger


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

