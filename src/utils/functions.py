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
# z[j,d]=i: If nurse i is assigned to job j at day d (integer)
# x[c,i]=1: If client c sees nurse i during the week (binary)
# w[i,d]: Time slots that nurse i is busy on day d (list)

# =============================================================================
# Feasibility checks
# =============================================================================
# No overlap
# Each job is assigned to one nurse
# 8 hours
# 5 days

# =============================================================================
# This section includes the functions that run the algorithm
# =============================================================================

def calculate_obj(sol):
    global objective
    #Two options of objective as parameter: "total" or "minmax"
    minmax = 0
    total = 0
    for c in clients:
        count=0
        for i in nurses:  
            assigned_to_i=False
            for j in jobs:    
                # if job j belongs to client c 
                if jobs[j]['client_id'] == c:
                    for d in days:
                        if jobs[j][d] == 1:                     
                            if sol['z'][j,d] == i:
                                assigned_to_i=True
                                count+=1    
                                break
                                # Break the inner loop..., no need to search more jobs/days
                if assigned_to_i:
                    break    
        total+=count
        if count > minmax:
            minmax = count
            
    if objective=="minmax":
        # min max objective:
        return minmax
    elif objective=="total":
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
        early = jobs[check_job]['tw_due'] - min(w[nurse,check_day])[0]
        late = max(w[nurse,check_day])[1] - jobs[check_job]['tw_start']
        if (early<480 and late<480):
            return True
        else:
            return False
    
def check_five_days_feasibility(w,i,day_except):
    # check for nurse i for a week
    # return True if feasible 
    count_days_busy=0
    for d in days:
        if w[i,d]:
            if d != day_except:
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
                    if sol['z'][j,d]==i:
                        num_assigned += 1

    if num_assigned == all_jobs:
        return True
    else:
        return False

    
def check_enough_nurse(number,search_previous,stop_step=5000,stop_time=10):
    start = timer()
    # initial check if # of nurses is enough    
    sol,nurses = generate_initial_solution("heuristic",search_previous)
    nurses_heuristic = len(nurses)

    # increase until reaching target number 
    found=False
    if number > nurses_heuristic:
        cont=True
        prob1 = 1
        prob2 = 1
        if number>search_previous:
            raise ValueError("Too much nurses!")
            return found
        else:
            while cont:
                sol,nurses = generate_neighbour(sol,nurses,prob1,prob2) 
                if number == len(nurses):
                    cont=False
                    found=True
    # decrease until reaching target number 
    elif number < nurses_heuristic:
        cont=True
        prob1 = 1
        prob2 = 0
        num_steps=0
        while cont:
            sol,nurses = generate_neighbour(sol,nurses,prob1,prob2)
            current=timer()
            if number == len(nurses):
                cont=False
                found=True 
            elif num_steps==stop_step or current-start>=stop_time:
                cont=False
                found=False 
            num_steps+=1
    else: 
        found=True
    return found,sol,nurses

def check_final_feasibility(nurses,sol):
    no_overlap=True
    eight_hours = True
    five_days=True
    # check the feasibility of the final solution
    for i in nurses:
        for d in days:
            for a in sol['w'][i,d]:
                for b in sol['w'][i,d]:
                    if a!=b:
                        if not check_overlap(a,b):
                            no_overlap=False                        
                            break
                if not no_overlap:
                    break
            if not no_overlap:
                break
        if not no_overlap:
            break
        
    for i in nurses:
        for d in days:
            if sol['w'][i,d]:
                max_tw=[0,0] 
                min_tw=[1440,1440]
                for tw_check in sol['w'][i,d]:
                    if tw_check < min_tw:
                        min_tw = tw_check
                    if tw_check > max_tw:
                        max_tw = tw_check
                diff = max_tw[1]-min_tw[0]
                if (diff>480):
                    eight_hours=False  
                    break
        if not eight_hours:
            break
         
    for d in days:
        if not check_five_days_feasibility:
            five_days=False 
            break
        if not five_days:
            break
    
    if no_overlap and check_all_jobs_assigned(nurses,sol) and eight_hours and five_days:
        return True
    else:
        return False

def heuristic(number,search_previous):
    found,sol,nurses = check_enough_nurse(number,search_previous)
    if found:
        return sol,nurses
    else:
        raise ValueError('Change the number of nurses!')

def find_x(nurses,z):
    # If client c sees nurse i during the week:
    x={}
    for c in clients: 
        for j in jobs:
            if jobs[j]['client_id'] == c:
                for d in days:
                    if jobs[j][d] == 1:
                        for i in nurses:   
                            if z[j,d] == i:
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
                if jobs[j][d] == 1:
                    if z[j,d] == i:
                        w[i,d].append([jobs[j]['tw_start'],jobs[j]['tw_due']])
    return w            

# function needed for assignment:
def assign_to_other_nurses(search_previous,number_nurses,nurses,w_init,z_init,j,d):
    tw_new = [jobs[j]['tw_start'],jobs[j]['tw_due']]
    found_one = False
    found=None
    # if there are other nurses to check:
    if len(nurses)>1:
        if len(nurses)<search_previous:
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
                                found=cand
                                break
                        if tw_feasible: 
                            found_one = True
                            found=cand
                            break
        else:
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
                                found=cand
                                break
                        if tw_feasible:
                            found_one = True
                            found=cand
                            break
    # if there is an available nurse, assign the job to her
    if found_one:  
        z_init[j,d] = found
        w_init[found,d].append(tw_new)
    # if there is no available nurse, add one nurse to the system
    else:
        number_nurses += 1
        nurses.append(number_nurses)
        z_init[j,d] = number_nurses
        w_init[number_nurses,d].append(tw_new) 
    return number_nurses,nurses,w_init,z_init,j,d
            
def generate_initial_solution(init_method,search_previous):
    #generate initial solution 
    z={}
    w={}
    sol={}
    if init_method == "worst":
        nurses=[]
        number_nurses=1
        for d in days:
            for j in jobs:
                if jobs[j][d] == 1:
                    z[j,d]=number_nurses
                    nurses.append(number_nurses)
                    number_nurses += 1
                
    elif init_method == "heuristic":
        # Use the following heuristic to generate initial solution with fewer number of nurses:

        nurses=[]
        number_nurses = search_previous
        for n in range(number_nurses):
            nurses.append(n)

        w_init={}
        z_init={}
        for j in jobs:
            for d in days:
                if jobs[j][d] == 1:
                    z_init[j,d] = None
        w_init = find_w(nurses,z_init) 
        
        # start from a single nurse
        number_nurses = 1
        nurses=[number_nurses]
        # add jobs to a nurse day by day until there is an infeasibility in her schedule
        # if there is an infeasibility for this nurse, add one nurse or check the schedule of other nurses in the "nurses" list
        for j in jobs:
            for d in days:
                if jobs[j][d] == 1:
                    # if the job j on day d is unassigned:
                    #check the schedule of the current nurse for this job
                    feasible = check_five_days_feasibility(w_init,number_nurses,d)
                    #if 5 days feasibility is satisfied
                    if feasible:
                        # the time window of the job
                        tw_new = [jobs[j]['tw_start'],jobs[j]['tw_due']]
                        #if there are other jobs assigned to the nurse on the day job should be done:
                        if w_init[number_nurses,d]: 
                            # check if adding a new job causes 8-hours infeasibility:
                            feasible = check_eight_hours_feasibility(w_init,number_nurses,j,d)
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
                                    z_init[j,d] = number_nurses
                                    w_init[number_nurses,d].append(tw_new) 
    
                                # if there is an overlap, assign job to the other nurses:
                                else:
                                    number_nurses,nurses,w_init,z_init,j,d = assign_to_other_nurses(search_previous,number_nurses,nurses,w_init,z_init,j,d)
                                
                            #if 8 hours feasibility is not satisfied         
                            else: 
                                number_nurses,nurses,w_init,z_init,j,d = assign_to_other_nurses(search_previous,number_nurses,nurses,w_init,z_init,j,d)
                            
                        #if there is no job assigned yet to the nurse on the day job should be done:
                        else:                
                            z_init[j,d] = number_nurses
                            w_init[number_nurses,d].append(tw_new) 
         
                    #if 5 days feasibility is not satisfied   
                    else: 
                        number_nurses,nurses,w_init,z_init,j,d = assign_to_other_nurses(search_previous,number_nurses,nurses,w_init,z_init,j,d)
                     
        for j in jobs:
            for d in days:
                if jobs[j][d] == 1:
                    z[j,d] = z_init[j,d]
    # time slots that nurse i is busy on day d:
    w = find_w(nurses,z) 

    sol={'z':z,'w':w}

    if check_all_jobs_assigned(nurses,sol):
        return sol,nurses
    else:
        generate_initial_solution(init_method,search_previous)
     
def first_scenario(sol,nurses,cand_i,cand_j,cand_d,cand_c):
    # find another nurse to do job cand_j on day cand_d
    # cand_i should undertake this nurse's one job
    nurse_candidates=[]
    found_one_seen_before=False
    seen_before=[]
    # this nurse should not have jobs more than 5 days:
    # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
    for i in nurses:
        if check_five_days_feasibility(sol['w'],i,cand_d):
            if sol['w'][i,cand_d]:
                if check_eight_hours_feasibility(sol['w'],i,cand_j,cand_d):
                    tw_new = [jobs[cand_j]['tw_start'],jobs[cand_j]['tw_due']]       
                    # if there are other jobs assigned to the nurse on the day job should be done:       
                    tw_feasible=True
                    for tw_exist in sol['w'][i,cand_d]:
                        # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                        feasible = check_overlap(tw_new,tw_exist)                
                        if not feasible: 
                            tw_feasible=False
                            break
                    if tw_feasible: 
                        if jobs[cand_j]['client_id'] == cand_c: 
                            found_one_seen_before = True
                            seen_before.append(i)
                        nurse_candidates.append(i)     
            else:
                if jobs[cand_j]['client_id'] == cand_c: 
                    found_one_seen_before = True
                    seen_before.append(i)
                nurse_candidates.append(i)     
        
    # Since we will do a switch, we need to ensure that cand_i is eligible to switch to job of a candidate nurse
    found_one=False
    new_i=None
    new_job = None
    new_day = None
    cand_i_list=[]
    cand_j_list=[]
    cand_d_list=[]
    if found_one_seen_before:
        for i in seen_before:
            # find a job that the candidate nurse was previously assigned to:
            for j in jobs:   
                for d in days:
                    if jobs[j][d] == 1:
                        if sol['z'][j,d]==i:
                            # check if cand_i can do it:        
                            if check_five_days_feasibility(sol['w'],cand_i,d):
                                if sol['w'][cand_i,d]: 
                                    if check_eight_hours_feasibility(sol['w'],cand_i,j,d):
                                        tw_new = [jobs[j]['tw_start'],jobs[j]['tw_due']]       
                                        # if there are other jobs assigned to the nurse on the day job should be done:       
                                        tw_feasible=True
                                        for tw_exist in sol['w'][cand_i,d]:
                                            # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                                            feasible = check_overlap(tw_new,tw_exist)                
                                            if not feasible: 
                                                tw_feasible=False
                                                break
                                        if tw_feasible: 
                                            found_one = True  
                                            cand_i_list.append(i)
                                            cand_j_list.append(j)
                                            cand_d_list.append(d)
                                else:
                                    found_one=True
                                    cand_i_list.append(i)
                                    cand_j_list.append(j)
                                    cand_d_list.append(d)                     

    elif not found_one_seen_before or not found_one:
        for i in nurse_candidates:
            # find a job that the candidate nurse was previously assigned to:
            for j in jobs:   
                for d in days:
                    if jobs[j][d] == 1:
                        if sol['z'][j,d]==i:
                            # check if cand_i can do it:        
                            if check_five_days_feasibility(sol['w'],cand_i,d):
                                if sol['w'][cand_i,d]: 
                                    if check_eight_hours_feasibility(sol['w'],cand_i,j,d):
                                        tw_new = [jobs[j]['tw_start'],jobs[j]['tw_due']]       
                                        # if there are other jobs assigned to the nurse on the day job should be done:       
                                        tw_feasible=True
                                        for tw_exist in sol['w'][cand_i,d]:
                                            # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                                            feasible = check_overlap(tw_new,tw_exist)                
                                            if not feasible: 
                                                tw_feasible=False
                                                break
                                        if tw_feasible: 
                                            found_one = True   
                                            cand_i_list.append(i)
                                            cand_j_list.append(j)
                                            cand_d_list.append(d)
                                else:
                                    found_one=True
                                    cand_i_list.append(i)
                                    cand_j_list.append(j)
                                    cand_d_list.append(d)                                  

    if found_one: 
        new_i = random.choice(cand_i_list)
        index = cand_i_list.index(new_i)
        new_job = cand_j_list[index]
        new_day = cand_d_list[index]
        return new_i,new_job,new_day
    else:
        #cannot find any bit to do binary switch, don't switch
        return cand_i,cand_j,cand_d

def first_scenario_old(sol,cand_i,cand_j,cand_d,cand_c):
    # find another nurse to do job cand_j on day cand_d
    # cand_i should undertake this nurse's one job
    
    nurse_candidates=[]
    # this nurse should not have jobs more than 5 days:
    # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
    for i in nurses:
        if check_five_days_feasibility(sol['w'],i,cand_d):
            if sol['w'][i,cand_d]:
                if check_eight_hours_feasibility(sol['w'],i,cand_j,cand_d):
                    tw_new = [jobs[cand_j]['tw_start'],jobs[cand_j]['tw_due']]       
                    # if there are other jobs assigned to the nurse on the day job should be done:       
                    tw_feasible=True
                    for tw_exist in sol['w'][i,cand_d]:
                        # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                        feasible = check_overlap(tw_new,tw_exist)                
                        if not feasible: 
                            tw_feasible=False
                            break
                    if tw_feasible: 
                        nurse_candidates.append(i)     
            else:
                nurse_candidates.append(i)     
        
    # Since we will do a switch, we need to ensure that cand_i is eligible to switch to job of a candidate nurse
    found_one=False
    new_i=None
    new_job = None
    new_day = None
    
    
    for i in nurse_candidates:
        # find a job that the candidate nurse was previously assigned to:
        for j in jobs:   
            for d in days:
                if jobs[j][d] == 1:
                    if sol['z'][j,d]==i:
                        # check if cand_i can do it:        
                        if check_five_days_feasibility(sol['w'],cand_i,d):
                            if sol['w'][cand_i,d]: 
                                if check_eight_hours_feasibility(sol['w'],cand_i,j,d):
                                    tw_new = [jobs[j]['tw_start'],jobs[j]['tw_due']]       
                                    # if there are other jobs assigned to the nurse on the day job should be done:       
                                    tw_feasible=True
                                    for tw_exist in sol['w'][cand_i,d]:
                                        # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                                        feasible = check_overlap(tw_new,tw_exist)                
                                        if not feasible: 
                                            tw_feasible=False
                                            break
                                    if tw_feasible: 
                                        found_one = True   
                                        new_i=i
                                        new_job = j
                                        new_day = d
                            else:
                                found_one=True
                                new_i=i
                                new_job = j
                                new_day = d                              
                if found_one:
                    break
            if found_one:
                break
        if found_one:
            break
    
    if found_one:
        return new_i,new_job,new_day
    else:
        #cannot find any bit to do binary switch, don't switch
        return cand_i,cand_j,cand_d


def second_scenario(sol,nurses,cand_i,cand_j_list,cand_d_list):
    new_i_list=[]
    need_nurse=False
    for index in range(len(cand_j_list)):
        cand_j = cand_j_list[index]
        cand_d = cand_d_list[index]
        nurse_candidates=[]
        found_one=False
        # this nurse should not have jobs more than 5 days:
        # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
        for i in nurses:
            if check_five_days_feasibility(sol['w'],i,cand_d):
                if sol['w'][i,cand_d]:
                    if check_eight_hours_feasibility(sol['w'],i,cand_j,cand_d):
                        tw_new = [jobs[cand_j]['tw_start'],jobs[cand_j]['tw_due']]     
                        for tw_exist in sol['w'][i,cand_d]:   
                            tw_feasible=True
                            feasible = check_overlap(tw_exist,tw_new)
                            if not feasible:
                                tw_feasible=False
                                break
                        if tw_feasible:
                            found_one=True
                            nurse_candidates.append(i)    
                else:
                    found_one=True
                    nurse_candidates.append(i)
        # We checked all feasibility constraints, let's finally choose one nurse candidate:
        if found_one:
            new_i = random.choice(nurse_candidates)  
            new_i_list.append(new_i)
        # If no candidate left, add nurse again:
        else:
            need_nurse=True
            new_i_list.append(cand_i)
    if need_nurse:
        nurses.append(cand_i)
    return new_i_list,nurses
               
def generate_neighbour(sol,nurses,prob1,prob2):    
    # TWO SCENARIOS (MY HYPOTHESIS...), for now let's skip the second one (a bit complex...)
    cand_i=None
    # 1) DO BINARY SWITCH BETWEEN TWO JOBS (CHANGE THE ASSIGNMENTS), KEEP NUMBER OF NURSES THE SAME
    if random.uniform(0, 1) > prob1:    
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
            if sol['z'][cand_j,cand_d]==i:
                cand_i = i
                break
            
        for c in clients:
            if jobs[cand_j]['client_id'] == c: 
                cand_c=c
        
            
        new_i,new_j,new_d=None,None,None
        # choose another nurse, do feasibility check::
        new_i,new_j,new_d = first_scenario(sol,nurses,cand_i,cand_j,cand_d,cand_c)

        # do binary switch between matches:
        sol['z'][cand_j,cand_d] = new_i
        sol['z'][new_j,new_d] = cand_i
        

    # 2) INCREASE/DECREASE THE NUMBER OF NURSES BY ONE 
    else:           
        if random.uniform(0, 1) > prob2:    
            #choose one nurse:
            cand_i = random.choice(nurses)
            
            # check the jobs that the candidate nurse was previously assigned to:
            cand_j_list=[]    
            cand_d_list=[]    
            for j in jobs:   
                for d in days:
                    if jobs[j][d] == 1:
                        if sol['z'][j,d]==cand_i:
                            cand_j_list.append(j)
                            cand_d_list.append(d)
                        
            # remove nurse:
            nurses.remove(cand_i)
            # assign all these jobs to other nurses:
    
            # choose another nurse, do feasibility check:
            new_i_list,nurses = second_scenario(sol,nurses,cand_i,cand_j_list,cand_d_list)
    
            # do nurse elimination and switches:
            for ind in range(len(new_i_list)):   
                sol['z'][cand_j_list[ind],cand_d_list[ind]] = new_i_list[ind]
        elif len(nurses)<len(jobs)*len(days):
            # add new nurse
            new_nurse=max(nurses)+1
            nurses.append(new_nurse)
            
    sol['w'] = find_w(nurses,sol['z'])
    
    return sol,nurses



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
              
def greedy_algorithm(sol,nurses,time_limit):    
    start = timer()
    current = 0
    obj=calculate_obj(sol)
    step=0
    obj_list=[obj]
    nurse_list=[len(nurses)]
    # create a neighbour for initial solution
    new_sol,nurses = generate_neighbour(sol,nurses,prob1,prob2) 
    # compare objective functions for initial solution
    new_obj = calculate_obj(new_sol)

    while new_obj<=obj:
        # if the new solution is better than the previous solution (minimization)
        obj = new_obj
        obj_list.append(obj)
        nurse_list.append(len(nurses))

        #keep track of number of steps in case of comparison with SA
        current = timer()
        # bored of waiting ? (not necessary)
        if current-start > time_limit:
            print("Time limit is reached!")
            break
        else:
            # create a neighbour
            new_sol,nurses = generate_neighbour(sol,nurses,prob1,prob2) 
            
            # compare objective functions
            new_obj = calculate_obj(new_sol)
            
            step+=1   
            
    #some plots:
    plt.plot(nurse_list)
    plt.ylabel('number of nurses')
    plt.show()

    plt.plot(obj_list)
    plt.ylabel('obj. value')
    plt.show()
    

    print("Computation Time:",current-start,"seconds")
    
    return new_sol, obj_list

def find_temperature(prob1,prob2,search_previous,num,acceptProb):
    summ=0
    for i in range(num):    
        sol,nurses = generate_initial_solution("heuristic",search_previous)
        obj=calculate_obj(sol)
        new_sol,nurses = generate_neighbour(sol,nurses,prob1,prob2) 
        new_obj = calculate_obj(new_sol) 
        summ += abs(new_obj-obj)
    return (summ/num) / math.log(1/acceptProb)

def SA_algorithm(sol,nurses, step_max, time_limit,stagnation,initial_temperature):
    start = timer()
    prob1=1
    prob2=0
    count=0
    step=0
    obj=calculate_obj(sol)
    obj_list=[obj]
    nurse_list=[len(nurses)]
    minimum_nurse=False
    while step<step_max:
        # define the temperature (can be logartihmic, too)
        T=initial_temperature*(0.995**step)
        
        # T = 1-step/step_max
        # create a neighbour
        new_sol,nurses = generate_neighbour(sol,nurses,prob1,prob2) 
        
        # compare objective functions
        
        new_obj = calculate_obj(new_sol)
        
        # if the new solution is better than the previous solution (minimization)
        if new_obj<=obj:
            obj=new_obj
        
        # if the new solution is worse than the previous solution (minimization)
        else:
            # normalization to make sure that the probability is between 0 and 1
            prob = math.exp(-(new_obj-obj)/T)
            # accept the worse solution:
            print(prob)
            if prob > random.uniform(0, 1):    
                obj=new_obj

        nurse_num=len(nurses)
        nurse_list.append(nurse_num)
        obj_list.append(obj)
        
        current = timer()
        
        # decrease number of nurses until reaching minimum number of nurses
        if nurse_num < nurse_list[-2] and not minimum_nurse:
            prob1=1
            prob2=0
        else:
            minimum_nurse=True
            
        # then do switch
        if minimum_nurse:
            prob1=0.01
            prob2=0.1

        # convergence
        if len(obj_list)>stagnation and obj == obj_list[-2]:
            count+=1
        else:
            count=0
            
        if count==stagnation:
            print("Stagnation: No more improvement for last",int(stagnation),"steps!")
            break 
        elif current-start > time_limit:
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
    

    print("Computation Time:",current-start,"seconds")
    
    return new_sol, obj_list



# =============================================================================
# PARAMETERS:
# =============================================================================

days = sets['days']
clients = sets['clients']

# Number of other nurses to check when the current nurse is not feasible. 
# Currently, the algorihtm selects all nurses as a candidate
# If you, for example, set search_previous=5, it will check 5 nurses' schedule
# If none of them feasible, it adds one nurse to the system.
# No need to change, but you can try some other values.
search_previous=len(jobs)*len(days)

# number of steps to be taken by SA
step_max=2000

#time limit to stop the algorithm (in seconds), no need to change atm
time_limit=600

# probability that governs neighbour generating rule: 
# prob1: closer to 1 more changes the number of nurses, less binary switches
# prob1: closer to 0 more binary switches, less changes in the number of nurses
prob1=0.9


# prob2: closer to 0 more decrements than increments in number of nurses 
# prob2: closer to 1 more increments than decrements in number of nurses 
prob2=0.1

# initial probability for simulated annealing algorithm transition
prob_init=0.95

# If there is no improvement in last #stagnation steps, terminate the algorithm
stagnation=step_max/5

# objective function: 
# "total": minimize the total number of nurses seen by clients
# "minmax": minimize the max number of nurses seen by clients
objective = "total"

# method for finding the initial solution: 
# "worst": the worst solution 
# "heuristic": heuristic solution 
init_method="heuristic"

# =============================================================================
# Run algorithms:
# =============================================================================

#algorihtms 

print("-----HEURISTIC-----")
start = timer()
number_of_nurses=25
sol,nurses = heuristic(number_of_nurses,search_previous)
obj=calculate_obj(sol)

# number of nurses needed approximately: 
print("Approximate number of nurses needed by heuristic: ", len(nurses))
print("Computation time:",timer()-start,"seconds")
#print(sol)
print("Initial objective value : ",obj)
print("Check feasibility:",check_final_feasibility(nurses,sol))


"""
print("\n-----GREEDY ALGORITHM-----")

start = timer()
sol,nurses = generate_initial_solution(init_method,search_previous)
obj=calculate_obj(sol)

final_sol, obj_list = greedy_algorithm(sol,nurses,time_limit)
print("Number of nurses found by greedy algorithm: ", len(nurses))
#print(final_sol)

print("Objective falue for", objective,"number of nurses seen: ", obj_list[-1])
print("Check feasibility of the final solution:", check_final_feasibility(nurses,final_sol))



print("\n-----SIMULATED ANNEALING ALGORITHM-----")

#avg_over=1000
#initial_temperature = find_temperature(prob1,prob2,search_previous,avg_over,prob_init)
#print(initial_temperature)

if objective == "total":    
    initial_temperature=30 # :for total, found above, no need to run it again
elif objective == "minmax":
    initial_temperature=2.5 # :for minmax, found above, no need to run it again
    
start = timer()
sol,nurses = generate_initial_solution(init_method,search_previous)
final_sol, obj_list = SA_algorithm(sol,nurses, step_max, time_limit,stagnation,initial_temperature)
print("Number of nurses found by simulated annealing algorithm: ", len(nurses))
#print(final_sol)

#check feasilbility of the final solution (not complete)
print("Objective value for",objective,"number of nurses seen:", obj_list[-1])
print("Check feasibility of the final solution:",check_final_feasibility(nurses,final_sol))
"""




