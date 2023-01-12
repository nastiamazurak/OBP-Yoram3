#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:10:34 2023

@author: K. B. Arik

Enjoy reading :)

"""

# =============================================================================
# Required libraries & modules
# =============================================================================

import math
import random
from timeit import default_timer as timer
from parameters import jobs, sets
from itertools import combinations


# =============================================================================
# Variables
# =============================================================================
# z[i,j,d]: If nurse i is assigned to job j at day d (binary)
# x[c,i]: If client c sees nurse i during the week (binary)
# w[i,d]: Time slots that nurse i is busy on day d (list)

# =============================================================================
# Feasbility checks 
# =============================================================================
# Overlap is done
# Each job is assigned to one nurse

# =============================================================================
# This section includes the functions that run the algorithm
# =============================================================================

def calculate_obj(sol,which="total"):
    #Two options of objective as parameter: "total" or "minmax"
    minmax = 0
    total = 0
    for c in clients:
        count=0
        for i in nurses:
            if sol['x'][c,i] == 1:
                count += 1
                total += 1
        if count > minmax:
            minmax = count
                
    if which=="minmax":
        # min max objective:
        return minmax
    else:  
        #min total objective, if you want to switch it:
        return total

def check_overlap(sol):
    # This is the function to check the overlaps in nurse's schedule
    for i in nurses:
        for d in days:
            for a,b in list(combinations(sol['w'][i,d], 2)):
                # if there is any overlap, give False
                if a[1] < b[0] or a[0] > b[1] or (a[0] < b[0] and a[1] > b[1]) or (a[0] > b[0] and a[1] < b[1]):
                    return False
    return True
                    
def check_feasibility(sol):
    # This is the function that will mess up everything...
    
    # if check_overlap(sol) and ........(other constraint controller functions):
    """
    # for example:
    if check_overlap(sol):
        return True
    else:
        return False
    """
    return True

def check_enough_nurse(number):
    # initial check if # of nurses is enough    
    return True

def generate_nurse(number):
    if check_enough_nurse(number):
        nurses = []
        # i = nurse_id, can be something different
        for i in range(number):
            nurses.append(i+1)
        return nurses
    else:
        raise ValueError('Number of healthcare professionals is insufficient!')


def find_x(z):
    # If client c sees nurse i during the week:
    x={}
    for c in clients:
        for i in nurses:   
            x[c,i] = 0
            for j in jobs:
                if jobs[j]['client_id'] == c:
                    for d in days:
                        if z[i,j,d] == 1:
                            x[c,i] = 1
                            # Break the inner loop..., no need to search more days
                            break  
                    break  
    return x

def find_w(z):
    # time slots that nurse i is busy on day d:
    w={}
    for i in nurses:
        for d in days:
            w[i,d]=[]
            for j in jobs:
                if z[i,j,d] == 1:
                    w[i,d].append([jobs[j]['tw_start'],jobs[j]['tw_due']])
    return w
                    
                    
def generate_neighbour(sol):
    global nurses
    global jobs
    global days
    
    # choose one job and a day that this job needs to be done:
    cand_j = random.choice(list(jobs.keys()))
    # silly method to choose candidate days, but I will improve it:
    candidates=[]
    for d in days:
        if jobs[cand_j][d] == 1:
            candidates.append(d)
    cand_d = random.choice(candidates)
    
    # check which nurse does this job:
    for i in nurses:
        if sol['z'][i,cand_j,cand_d]==1:
            which_nurse = i
            break
        
    # feasibility trick:
    # choose another nurse for this job, so that each job is done by one nurse!
    cand_i = random.choice(nurses)
    
    # find the job that the candidate nurse is assigned to:
    for j in jobs:   
        for d in days:
            if sol['z'][cand_i,j,d]==1:
                which_job = j
                which_day = d
                break
     
    # do binary switch 
    sol['z'][which_nurse,cand_j,cand_d] = 0
    sol['z'][cand_i,cand_j,cand_d] = 1
    
    sol['z'][cand_i,which_job,which_day] = 0
    sol['z'][which_nurse,which_job,which_day] = 1

    
    sol['x'] = find_x(sol['z'])
    sol['w'] = find_w(sol['z'])
    
    return sol

def generate_initial_solution():
    #generate initial random solution 
    sol={}
    # If nurse i is assigned to job j on day d:
    
    # Let's assume that initially # nurses = # jobs and a nurse does single job assigned to her all week:
    # So, we ensure that the initial solution is feasible 100%!
    z={}
    for i in nurses:
        for j in jobs:
            for d in days:
                z[i,j,d] = 0

    for i in nurses:
        for d in days:
            if jobs[i][d]==1:
                z[i,i,d] = 1
                
    # If client c sees nurse i during the week:
    x = find_x(z)
    
    # time slots that nurse i is busy on day d:
    w = find_w(z)
    
    sol={'z':z,'x':x,'w':w}
    
    #check feasibility 
    if check_feasibility(sol):  
        return sol
    else:
        # I think we will need something smarter...
        return generate_initial_solution()

def get_neighbour(sol):
    # do switch
    new_sol = generate_neighbour(sol)
    
    #check feasibility 
    if check_feasibility(new_sol):  
        return new_sol
    else:
        return get_neighbour(sol)

def calculate_number_of_nurses(sol):
    #calculates the number of nurses works based on solution
    number_nurses=0
    for i in nurses:
        is_working = False
        for d in days:
            if sol['w'][i,d]:
                is_working = True
                break
        if is_working:
            number_nurses+=1
    return number_nurses
              
def greedy_algorithm():
    # generate initial random solution
    sol=generate_initial_solution()
    obj=calculate_obj(sol)

    # create a neighbour for initial solution
    new_sol = get_neighbour(sol) 
    # compare objective functions for initial solution
    new_obj = calculate_obj(new_sol)
    """
    print(sol['z'])
    print(obj)
    print(new_obj)
    """
    step=0
    obj_list=[]
    
    while new_obj<obj:
        # if the new solution is better than the previous solution (minimization)
        obj = new_obj
        obj_list.append(obj)
        
        # create a neighbour
        new_sol = get_neighbour(sol) 
        
        # compare objective functions
        new_obj = calculate_obj(new_sol)
        
        #keep track of number of steps in case of comparison with SA
        step+=1
        
    return obj_list
        
def SA_algorithm(step_max=100, alpha=1, time_limit=10):
    start = timer()
    
    # generate initial random solution
    sol=generate_initial_solution()
    step=0
    obj_list=[]
    obj=calculate_obj(sol)
    while step<step_max:
        # define the temperature (can be logartihmic, too)
        T=1-step/step_max
        
        # create a neighbour
        new_sol = get_neighbour(sol) 
        
        # compare objective functions
        new_obj = calculate_obj(new_sol)
        
        # if the new solution is better than the previous solution (minimization)
        if new_obj<=obj:
            obj=new_obj

        # if the new solution is worse than the previous solution (minimization)
        else:
            # normalization to make sure that the probability is between 0 and 1
            worsening_ratio = ( (new_obj-obj) / obj )
            # alpha should be determined/tested!!!
            prob = math.exp(-alpha/(T*worsening_ratio))
            # accept the worse solution:

            if prob > random.uniform(0, 1):    
                obj=new_obj
        
        obj_list.append(obj)
        
        current = timer()
        # bored of waiting ? (not necessary)
        if current-start > time_limit:
            break
        else:
            step+=1
    return obj_list


# =============================================================================
# Run algorithms:
# =============================================================================

days = sets['days']
clients = sets['clients']

#Initially let's say number of nurses equal to number of jobs to ensure feasibility:
number_nurses = len(jobs)
nurses = generate_nurse(number_nurses)
print(greedy_algorithm())
#print(SA_algorithm())
