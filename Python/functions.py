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

# =============================================================================
# This section includes the functions that run the algorithm
# =============================================================================

def generate_nurse(number):
    nurses = []
    # i = nurse_id, can be something different
    for i in range(number):
        nurses.append(i)
    return nurses

def calculate_obj(sol):
    # min max objective:
    obj = 0
    
    for c in clients:
        count=0
        for i in nurses:
            if sol['x'][c,i] == 1:
                count+=1
        if count > obj:
            obj = count
            
    # min total objective, if you want to switch it:
    # obj = sum(sol)   
    
    return obj

def check_feasibility(sol):
    # This is the function that will mess up everything 
    return True

def update_x(z):
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

def generate_neighbour(sol):
    global nurses
    global jobs
    global days
    # do binary switch 
    cand_i = random.choice(nurses)
    cand_j = random.choice(list(jobs.keys()))
    cand_d = random.choice(days)

    if sol['z'][cand_i,cand_j,cand_d] == 1:
        sol['z'][cand_i,cand_j,cand_d] = 0
    else:
        sol['z'][cand_i,cand_j,cand_d] = 1
    
    sol['x'] = update_x(sol['z'])
    
    return sol

def generate_initial_solution():
    #generate initial random solution 
    sol={}
    # If nurse i is assigned to job j at day d:
    z={}
    for i in nurses:
        for j in jobs:
            for d in days:
                z[i,j,d] = 0
                
    # If client c sees nurse i during the week:
    x = update_x(z)
    
    sol={'z':z,'x':x}
    
    #check feasibility 
    if check_feasibility(sol):  
        return sol
    else:
        # I think we will need something smarter...
        return generate_initial_solution()

def get_neighbour(old_sol):
    # do switch
    new_sol = generate_neighbour(old_sol)
    
    #check feasibility 
    if check_feasibility(old_sol):  
        return new_sol
    else:
        return generate_neighbour(old_sol)

def greedy_algorithm(step_max=1000):
    global parameters
    # generate initial random solution
    sol=generate_initial_solution()
    step=0
    while step<step_max:
        
        # create a neighbour
        new_sol = get_neighbour(sol) 
        
        # compare objective functions
        obj = calculate_obj(sol)
        new_obj = calculate_obj(new_sol)
        # if the new solution is better than the previous solution (minimization)
        if new_obj<obj:
            obj=new_obj

        # if the new solution is worse than the previous solution (maximization)
        else:
            break
            # OR CONTINUE WITH SOMETHING FANCY???
            
        step+=1
    return obj
        
def SA_algorithm(step_max=1000, alpha=1, time_limit=10):
    global parameters
    
    start = timer()
    
    # generate initial random solution
    sol=generate_initial_solution()
    step=0
    while step<step_max:
        # define the temperature
        T=1-step/step_max
        
        # create a neighbour
        new_sol = get_neighbour(sol) 
        
        # compare objective functions
        obj = calculate_obj(sol)
        new_obj = calculate_obj(new_sol)
        # if the new solution is better than the previous solution (minimization)
        if new_obj<=obj:
            obj=new_obj

        # if the new solution is worse than the previous solution (maximization)
        else:
            # normalization to make sure that the probability is between 0 and 1
            improvement_ratio = ( (obj-new_obj) / obj )
            # need to check again!!! T=0 is a feasibility problem
            prob = alpha * math.exp(T * improvement_ratio)
            # accept the worse solution:
            if prob > random.uniform(0, 1):
                obj=new_obj
        
        current = timer()
        
        # bored of waiting ? (not necessary)
        if current-start > time_limit:
            break
        else:
            step+=1
            
    return obj


# =============================================================================
# Run algorithms:
# =============================================================================

days = sets['days']
clients = sets['clients']
nurses = generate_nurse(15)
print(greedy_algorithm())      
print(SA_algorithm()) 

