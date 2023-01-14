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
# No overlap
# Each job is assigned to one nurse
# 8 hours
# 5 days

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
    # This is the function to check the overlaps in nurse's schedule day, a and b jobs
    # return True if feasible 
    if max(0,min(a[1], b[1]) - max(a[0], b[0])) == 0:
        return True
    else:
        return False

def check_eight_hours_feasibility(w,nurse,check_job,check_day):
    # check for nurse i and day d
    # return True if feasible 
    # the following definitions may change
    if not w[nurse,check_day]:
        return True
    else:
        early = jobs[check_job]['tw_start'] - min(w[nurse,check_day])[0]
        late = max(w[nurse,check_day])[1] - jobs[check_job]['tw_due']
        if (early<480 and late<480):
            return True
        else:
            return False
    
def check_five_days_feasibility(w,i,day_except):
    # check for nurse i for a week
    # return True if feasible 
    count_days_busy=0
    for d in days:
        if w[i,d] and d != day_except:
            count_days_busy+=1
    if count_days_busy < 5:
        return True
    else:
        return False
  
def check_all_jobs_assigned(nurses,sol):
    # return True if feasible 
    # check if all jobs are assigned
    num_assigned = 0
    all_jobs=0
    for j in jobs:
        for d in days:
            if jobs[j][d]==1:
                all_jobs+=1
                for i in nurses:      
                    if sol['z'][i,j,d]==1:
                        num_assigned += 1

    if num_assigned == all_jobs:
        return True
    else:
        return False

    
def check_enough_nurse(number):
    # initial check if # of nurses is enough    
    return True

def check_final_feasibility(sol):
    """
    # check the feasibility of the final solution
    for j in jobs:
        for d in days:
            if jobs[j][d]==1:
    if :
        return True
    else:
        return False
    """
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


def find_x(nurses,z):
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

def find_w(nurses,z):
    # time slots that nurse i is busy on day d:
    w={}
    for i in nurses:
        for d in days:
            w[i,d]=[]
            for j in jobs:
                if z[i,j,d] == 1:
                    w[i,d].append([jobs[j]['tw_start'],jobs[j]['tw_due']])
    return w            
            
def generate_initial_solution(option=2):
    #generate initial solution 
            
    sol={}
    
    # OPTION 1: Assume that initially # nurses = # jobs and a nurse does single job assigned to her all week:
    # So, we ensure that the initial solution is feasible 100%!
    # But, not realistic. Try option 2 as long as it is feasible
    if option==1:
        
        number_nurses = len(jobs)
        nurses = generate_nurse(number_nurses)
        
        # If nurse i is assigned to job j on day d:
        z={}
        for i in nurses:
            for j in jobs:
                for d in days:
                    z[i,j,d] = 0
    
        for i in nurses:
            for d in days:
                if jobs[i][d]==1:
                    z[i,i,d] = 1
                    
        
    # OPTION 2: Use the following heuristic to generate initial solution with fewer number of nurses:
    else:
        
        # initiate dics with # nurses = # jobs
        number_nurses = len(jobs)
        nurses = generate_nurse(number_nurses)
        
        z_init={}
        for i in nurses:
            for j in jobs:
                for d in days:
                    z_init[i,j,d] = 0
        w_init = find_w(nurses,z_init) 
        
        # start from a single nurse
        number_nurses = 1
        nurses=[number_nurses]
        
        search_previous=2
        # function needed for assignment:
        def assign_to_other_nurses(number_nurses,nurses,w_init,z_init,j,d):
            found_one = False
            # if there are other nurses to check:
            if len(nurses)>1 and len(nurses)<search_previous:
                for cand in nurses:
                    if cand!=number_nurses:
                        # if this job fits the schedule of a nurse, choose her as a candidate for this job
                        feasible = check_eight_hours_feasibility(w_init,cand,j,d) and check_five_days_feasibility(w_init,cand,d)
                        if feasible:
                            tw_feasible=True
                            for tw_exist in w_init[cand,d]:
                                # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                                feasible = check_overlap(tw_new,tw_exist)                
                                if not feasible: 
                                    tw_feasible=False
                                    break
                            if tw_feasible:
                                z_init[cand,j,d] = 1
                                w_init[cand,d].append(tw_new) 
                                found_one = True
            elif len(nurses)>search_previous:
                for cand in nurses[-search_previous:]:
                    if cand!=number_nurses:
                        # if this job fits the schedule of a nurse, choose her as a candidate for this job
                        feasible = check_eight_hours_feasibility(w_init,cand,j,d) and check_five_days_feasibility(w_init,cand,d)
                        if feasible:
                            tw_feasible=True
                            for tw_exist in w_init[cand,d]:
                                # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                                feasible = check_overlap(tw_new,tw_exist)                
                                if not feasible: 
                                    tw_feasible=False
                                    break
                            if tw_feasible:
                                z_init[cand,j,d] = 1
                                w_init[cand,d].append(tw_new) 
                                found_one = True
                                
            # if there is no available nurse, add one nurse to the system
            if not found_one:
                number_nurses += 1
                nurses.append(number_nurses)
                z_init[number_nurses,j,d] = 1
                w_init[number_nurses,d].append(tw_new) 
            return number_nurses,nurses,w_init,z_init,j,d
                
        # add jobs to a nurse day by day until there is an infeasibility in her schedule
        # if there is an infeasibility for this nurse, add one nurse or check the schedule of other nurses in the "nurses" list
        for j in jobs:
            for d in days:
                if jobs[j][d] == 1:
                    # if the job j on day d is unassigned:
                    tw_new = [jobs[j]['tw_start'],jobs[j]['tw_due']]
                    #check the schedule of the current nurse for this job
                    
                    #if there are other jobs assigned to the nurse on the day job should be done:
                    if w_init[number_nurses,d]: 
                        # check if adding a new job causes infeasibility:
                        feasible = check_eight_hours_feasibility(w_init,number_nurses,j,d) and check_five_days_feasibility(w_init,number_nurses,d)
                        if feasible:
                            tw_feasible=True
                            for tw_exist in w_init[number_nurses,d]:
                                # check overlaps:
                                feasible = check_overlap(tw_new,tw_exist)    
                                if not feasible: 
                                    tw_feasible=False
                                    break
                            # if there is no overlap, assign job to the nurse:
                            if tw_feasible:
                                z_init[number_nurses,j,d] = 1
                                w_init[number_nurses,d].append(tw_new) 
                            # if there is an overlap, assign job to the other nurses:
                            else:
                                number_nurses,nurses,w_init,z_init,j,d = assign_to_other_nurses(number_nurses,nurses,w_init,z_init,j,d)
                                            
                        else: 
                            number_nurses,nurses,w_init,z_init,j,d = assign_to_other_nurses(number_nurses,nurses,w_init,z_init,j,d)
                        
                    #if there is no job assigned yet to the nurse on the day job should be done:
                    else:
                        
                        # check 5 days feasibility:
                        feasible = check_five_days_feasibility(w_init,number_nurses,d)
                        # if it is not feasible for the current nurse, select another nurse for that job
                        if not feasible: 
                            number_nurses,nurses,w_init,z_init,j,d = assign_to_other_nurses(number_nurses,nurses,w_init,z_init,j,d)
                        # if it is feasible for the current nurse, select her for the job
                        else: 
                            z_init[number_nurses,j,d] = 1
                            w_init[number_nurses,d].append(tw_new) 
     
        z={}
        for i in nurses:
            for j in jobs:
                for d in days:
                    z[i,j,d] = z_init[i,j,d]

    # time slots that nurse i is busy on day d:
    w = find_w(nurses,z) 
    
    # If client c sees nurse i during the week:
    x = find_x(nurses,z)

    sol={'z':z,'x':x,'w':w}

    if check_all_jobs_assigned(nurses,sol):
        return sol,nurses
    else:
        generate_initial_solution(option=2)

"""
def first_scenario(sol,cand_i,cand_j,cand_d):
    # not complete 
    
    nurse_candidates=[]
    
    # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
    for i in nurses:
        if sol['w'][i,cand_d]:
            if check_eight_hours_feasibility(sol['w'],i,cand_j,cand_d):
                nurse_candidates.append(i)    
        else:
            nurse_candidates.append(i)    
            
    # this nurse should not have jobs more than 5 days:
    for i in nurses:
        if check_five_days_feasibility(sol['w'],i,cand_d):
            nurse_candidates.append(i)  
             
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
"""
          
def first_scenario(sol,cand_i,cand_j,cand_d):
    # find another nurse to do job cand_j on day cand_d
    # cand_i should undertake this nurse's one job
    
    nurse_candidates=[]
    
    # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
    for i in nurses:
        if sol['w'][i,cand_d]:
            if check_eight_hours_feasibility(sol['w'],i,cand_j,cand_d):
                nurse_candidates.append(i)    
        else:
            nurse_candidates.append(i)    
            
    # this nurse should not have jobs more than 5 days:
    for i in nurses:
        if check_five_days_feasibility(sol['w'],i,cand_d):
            nurse_candidates.append(i)  
    
    # Since we will do a switch, we need to ensure that cand_i is eligible to switch to job of a candidate nurse
    assign_cand_i=False
    new_i=None
    new_job = None
    new_day = None
    for i in nurse_candidates:
        if assign_cand_i:
            break
        # find a job that the candidate nurse was previously assigned to:
        assigned_to_i=[]
        for j in jobs:   
            for d in days:
                if sol['z'][i,j,d]==1:
                    assigned_to_i.append([j,d])
        # check if cand_i can do it:
        for j,d in assigned_to_i:
            tw_new = [jobs[j]['tw_start'],jobs[j]['tw_due']]
            if check_five_days_feasibility(sol['w'],cand_i,d) and check_eight_hours_feasibility(sol['w'],cand_i,j,d):
                #if there are other jobs assigned to the nurse on the day job should be done:
                if sol['w'][cand_i,d]: 
                    for tw_exist in sol['w'][cand_i,d]:
                        # check overlaps:
                        feasible = check_overlap(tw_new,tw_exist)    
                        if feasible: 
                            assign_cand_i=True
                            new_i=i
                            new_job = j
                            new_day = d
                            break 
            if assign_cand_i:
                break
    
    if assign_cand_i:
        return new_i,new_job,new_day
    else:
        #cannot find any bit to do binary switch, don't switch
        return cand_i,cand_j,cand_d

def second_scenario(sol,cand_j_list,cand_d_list):
    # not complete   
    
    new_i_list=[]
    for index in range(len(cand_j_list)):
        cand_j = cand_j_list[index]
        cand_d = cand_d_list[index]
        
        nurse_candidates=[]
        
        # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
        for i in nurses:
            if sol['w'][i,cand_d]:
                if check_eight_hours_feasibility(sol['w'],i,cand_j,cand_d):
                    nurse_candidates.append(i)    
            else:
                nurse_candidates.append(i)    
                
        # this nurse should not have jobs more than 5 days:
        for i in nurses:
            if check_five_days_feasibility(sol['w'],i,cand_d):
                nurse_candidates.append(i)  
             
        # this nurse also should not have overlapping jobs after taking the job of deleted nurse
        for i in nurse_candidates:
            for task in sol['w'][i,cand_d]:
                if not check_overlap(task,[jobs[cand_j]['tw_start'],jobs[cand_j]['tw_due']]):
                    nurse_candidates.remove(i)
                    
        # We checked all feasibility constraints, let's finally choose one nurse candidate:
        new_i = random.choice(nurse_candidates)
        
        sol['x'] = find_x(nurses,sol['z'])
        sol['w'] = find_w(nurses,sol['z'])
    
        new_i_list.append(new_i)
    return new_i_list
               
def generate_neighbour(sol):    
    # TWO SCENARIOS (MY HYPOTHESIS...), for now let's skip the second one (a bit complex...)
    cand_i=None
    
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
            
        new_i,new_j,new_d=None,None,None
        # choose another nurse, do feasibility check::
        new_i,new_j,new_d = first_scenario(sol,cand_i,cand_j,cand_d)

        # do binary switch between matches:
        sol['z'][cand_i,cand_j,cand_d] = 0
        sol['z'][new_i,cand_j,cand_d] = 1
        
        sol['z'][new_i,new_j,new_d] = 0
        sol['z'][cand_i,new_j,new_d] = 1
        

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
    
    sol['x'] = find_x(nurses,sol['z'])
    sol['w'] = find_w(nurses,sol['z'])
    
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
              
def greedy_algorithm(sol,nurses):
    # generate initial random solution
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
        
def SA_algorithm(sol,nurses,step_max=2000, alpha=0.01, time_limit=600):
    start = timer()
    
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
        
        num_nurses = calculate_number_of_nurses(sol)
        nurse_list.append(num_nurses)
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
    
    return new_sol, obj_list


# =============================================================================
# Run algorithms:
# =============================================================================

days = sets['days']
clients = sets['clients']

sol,nurses = generate_initial_solution()
obj=calculate_obj(sol)
print(sol)
print(obj)
# number of nurses needed approximately: 
print(len(nurses))

#algorihtms (not complete yet)
#print(greedy_algorithm(sol,nurses))
final_sol, obj_list = SA_algorithm(sol,nurses)
print(nurses)
#print(final_sol)

#check feasilbility of the final solution (not complete)
print(check_all_jobs_assigned(nurses,final_sol))


