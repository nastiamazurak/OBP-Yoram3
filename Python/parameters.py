#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:10:34 2023

@author: K. B. Arik

Enjoy reading :)

"""
# =============================================================================
# This file imports parameters from the CSV file
# =============================================================================

import pandas as pd

try: 
    #read CSV
    raw_data= pd.read_csv('hhc_job_data.csv')
    
    #read headers
    header_names=[]
    for header in raw_data:
        header_names.append(header)
        
    #convert data to arrays
    data = raw_data.values.tolist()
except:    
    raise ValueError('Wrong file name!')

# convert time window hours to minutes, for example: 02:30 = 150
def hms_to_s(s):
    t = 0
    for u in s.split(':')[:-1]:
        t = 60 * t + int(u)
    return t

# create dictionary with job id
jobs = {}
for row in data:
    jobs[row[0]]={}
    # assign parameters to the job
    posit=1
    for col in row[1:]:
        jobs[row[0]][header_names[posit]] = col
        posit+=1
    # convert duration to minutes (not necessary, but why not)
    jobs[row[0]]['duration']/=60
    jobs[row[0]]['tw_start']=hms_to_s(jobs[row[0]]['tw_start'])
    jobs[row[0]]['tw_due']=hms_to_s(jobs[row[0]]['tw_due'])

# =============================================================================
# Define sets
# =============================================================================
sets={}
days=header_names[-7:]
clients = list(dict.fromkeys(raw_data.client_id.values.tolist()))

sets['days']=days
sets['clients']=clients

