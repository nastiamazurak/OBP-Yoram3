#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:10:34 2023

@author: berkanarik
"""
# =============================================================================
# This file imports parameters from the CSV file
# =============================================================================

import csv

try: 
    #read CSV
    file = open('hhc_job_data.csv')
    csvreader = csv.reader(file)
    header = []
    header = next(csvreader)
    print(header)
    rows = []
    for row in csvreader:
            rows.append(row)
    print(rows)
except:    
    """
    data = excel.iloc[:, 0:]
    data = data.values.tolist()
    """