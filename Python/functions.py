#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:10:34 2023

@author: berkanarik
"""

# =============================================================================
# This file includes the functions that run the algorithm
# =============================================================================

import math
import random
from parameters import *

# FUNCTIONS:
def calculate_obj(sol):
    return None

def generate_initial_solution(parameters):
    #generate initial random solution 
    sol=[]
    #check feasibility 
    if check_feasibility(sol):  
        return sol
    else:
        return generate_initial_solution(parameters)

def generate_neighbour(sol):
    #do binary switch 
    return None

def check_feasibility(sol):
    return None

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
    sol=generate_initial_solution(parameters)
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
        
def SA_algorithm(step_max=1000,alpha=1):
    global parameters
    # generate initial random solution
    sol=generate_initial_solution(parameters)
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
        if new_obj<obj:
            obj=new_obj

        # if the new solution is worse than the previous solution (maximization)
        else:
            #normalization to make sure that the probability is between 0 and 1
            improvement_ratio = ( (obj-new_obj) / obj )
            #need to check again!!! T=0 is a problem
            prob=math.exp(-alpha/(improvement_ratio*T))
            # accept the worse solution:
            if prob > random.uniform(0, 1):
                obj=new_obj
        step+=1

