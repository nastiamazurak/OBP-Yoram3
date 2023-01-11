#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:10:34 2023

@author: berkanarik
"""
# =============================================================================
# This file imports parameters from the CSV file
# =============================================================================

import pandas as pd

try: 
    #read CSV
    data= pd.read_csv('hhc_job_data.csv')
    
    #read headers
    header_names=[]
    for header in data:
        header_names.append(header)
        
    #convert data to arrays
    data = data.values.tolist()
except:    
    raise ValueError('Wrong file name!')

# create dictionary with job id
jobs = {}
for row in data:
    jobs[row[0]]={}
    # assign parameters to the job
    for col in row[1:]:
        jobs[row[0]][header_names[row.index(col)]] = col
    jobs[row[0]]['duration']/=60


print(jobs)

        


"""
for row in data.client_id:
    jobs[row]['client_id']=
"""