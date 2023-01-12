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
import matplotlib.pyplot as plt

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
    elif which=="total":
        #min total objective, if you want to switch it:
        return total

def check_overlap(a,b):
    # This is the function to check the overlaps in nurse's schedule
    # if there is any overlap between job a and b, give True
    if a[1] < b[0] or a[0] > b[1] or (a[0] < b[0] and a[1] > b[1]) or (a[0] > b[0] and a[1] < b[1]):
        return True
    return False

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

def check_time_feasibility(sol,cand_j,cand_d):
    # choose once nurse for empty job, so that each job is done by one nurse!
    nurse_candidates=[]
    
    # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
    for i in nurses:
        if sol['w'][i,cand_d]:
            # the following definitions may change
            early = jobs[cand_j]['tw_start'] - min(sol['w'][i,cand_d])[0]
            late = max(sol['w'][i,cand_d])[1] - jobs[cand_j]['tw_due']
            if early<8 and late<8:
                nurse_candidates.append(i)    
        else:
            nurse_candidates.append(i)    
            
    # this nurse should not have jobs more than 5 days:
    for i in nurses:
        count_days_busy=0
        for d in days:
            if sol['w'][i,d]:
                count_days_busy+=1
        if count_days_busy > 5:
            nurse_candidates.append(i)  
            
    return nurse_candidates
            
def first_scenario(sol,cand_j,cand_d):
    # not complete 
    
    nurse_candidates = check_time_feasibility(sol,cand_j,cand_d)
             
    # We checked all feasibility constraints, let's finally choose one nurse candidate:
    new_i = random.choice(nurse_candidates)
    
    # find the job that the candidate nurse was previously assigned to:
    for j in jobs:   
        for d in days:
            if sol['z'][new_i,j,d]==1:
                new_job = j
                new_day = d
                break
            
    return new_i,new_job,new_day

def second_scenario(sol,cand_j_list,cand_d_list):
    # not complete   
    
    new_i_list=[]
    for index in range(len(cand_j_list)):
        cand_j = cand_j_list[index]
        cand_d = cand_d_list[index]
        
        nurse_candidates = check_time_feasibility(sol,cand_j,cand_d)
             
        # this nurse also should not have overlapping jobs after taking the job of deleted nurse
        for i in nurse_candidates:
            for task in sol['w'][i,cand_d]:
                if check_overlap(task,[jobs[cand_j]['tw_start'],jobs[cand_j]['tw_due']]):
                    nurse_candidates.remove(i)
                    
        # We checked all feasibility constraints, let's finally choose one nurse candidate:
        new_i = random.choice(nurse_candidates)
        
        sol['x'] = find_x(sol['z'])
        sol['w'] = find_w(sol['z'])
    
        new_i_list.append(new_i)
    return new_i_list
               
def generate_neighbour(sol):
    global nurses
    global jobs
    global days
    
    # TWO SCENARIOS (MY HYPOTHESIS...), for now let's skip the second one (a bit complex...)

    # 1) DO BINARY SWITCH BETWEEN TWO JOBS (CHANGE THE PAIRINGS), KEEP NUMBER OF CLIENTS THE SAME
    if random.uniform(0, 1) > 0:    
        # choose one job and a day that this job needs to be done:
        cand_j = random.choice(list(jobs.keys()))
        # choose candidate days:
        day_candidates=[]
        for d in days:
            if jobs[cand_j][d] == 1:
                day_candidates.append(d)
        cand_d = random.choice(day_candidates)
        
        # check which nurse does this job:
        for i in nurses:
            if sol['z'][i,cand_j,cand_d]==1:
                cand_i = i
                break
            
        # choose another nurse, do feasibility check::
        new_i,new_j,new_d = first_scenario(sol,cand_j,cand_d)

         
        # do binary switch between matches:
        sol['z'][cand_i,cand_j,cand_d] = 0
        sol['z'][new_i,cand_j,cand_d] = 1
        
        sol['z'][cand_i,new_j,new_d] = 1
        sol['z'][new_i,new_j,new_d] = 0

    # 2) DECREASE THE NUMBER OF CLIENTS BY ONE 
    else:           
        #choose one nurse:
        cand_i = random.choice(nurses)
        
        # check the jobs that the candidate nurse was previously assigned to:
        cand_j_list=[]    
        cand_d_list=[]    
        for j in jobs:   
            for d in days:
                if sol['z'][cand_i,j,d]==1:
                    cand_j_list.append(j)
                    cand_d_list.append(d)
        # assign all these jobs to other nurses:
        
        # choose another nurse, do feasibility check:
        new_i_list = second_scenario(sol,cand_j_list,cand_d_list)
        
        # do nurse elimination and switches:
        for cand_j in cand_j_list:   
            for cand_d in cand_j_list:
                sol['z'][cand_i,cand_j,cand_d] = 0
                for new_i in new_i_list:
                    sol['z'][new_i,cand_j,cand_d] = 1
    
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
    
    return sol

def get_neighbour(sol):
    # do switch
    new_sol = generate_neighbour(sol)
    
    #check feasibility  
    return new_sol


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
        
def SA_algorithm(step_max=100, alpha=0.01, time_limit=100):
    start = timer()
    
    # generate initial random solution
    sol=generate_initial_solution()
    step=0
    obj_list=[]
    nurse_list=[]
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
        
        nurses = calculate_number_of_nurses(sol)
        nurse_list.append(nurses)
        obj_list.append(obj)
        
        current = timer()
        # bored of waiting ? (not necessary)
        if current-start > time_limit:
            print("Time limit is reached!")
            break
        else:
            step+=1     
    
    #some plots:
    plt.plot(nurse_list)
    plt.ylabel('number of nurses')
    plt.show()
    
    plt.plot(obj_list)
    plt.ylabel('obj. value')
    plt.show()
    

    print("Computation Time:",current-start)
    print("Objective Value:",obj)
    
    return obj_list


# =============================================================================
# Run algorithms:
# =============================================================================

days = sets['days']
clients = sets['clients']

#Initially let's say number of nurses equal to number of jobs to ensure feasibility:
number_nurses = len(jobs)
nurses = generate_nurse(number_nurses)
#print(greedy_algorithm())
print(SA_algorithm())


