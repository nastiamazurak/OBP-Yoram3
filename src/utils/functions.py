#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# Required libraries & modules
# =============================================================================

import math
import random
from timeit import default_timer as timer

# from parameters import jobs, sets
import matplotlib.pyplot as plt

# =============================================================================
# Variables
# =============================================================================
# z[j,d]=i: If nurse i is assigned to job j at day d (integer)
# x[c,i]=1: If client c sees nurse i during the week (binary)
# w[i,d]: Time slots that nurse i is busy on day d (list)
# t[i, d, j]: time window for nurse i on day d for job j.

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
def calculate_obj(clients, jobs, days, sol, nurses, objective="minmax"):
    # Two options of objective as parameter: "total" or "minmax"
    minmax = 0
    total = 0
    for c in clients:
        count = 0
        for i in nurses:
            assigned_to_i = False
            for j in jobs:
                # if job j belongs to client c
                if jobs[j]["client_id"] == c:
                    for d in days:
                        if jobs[j][d] == 1:
                            if sol["z"][j, d] == i:
                                assigned_to_i = True
                                count += 1
                                break
                                # Break the inner loop..., no need to search more jobs/days
                if assigned_to_i:
                    break
        total += count
        if count > minmax:
            minmax = count

    if objective == "minmax":
        # min max objective:
        return minmax
    elif objective == "total":
        # min total objective
        return total

def check_overlap(a, b):
    # This is the function to check the overlaps in nurse's schedule day, a and b jobs
    # return True if feasible
    if max(0, min(a[1], b[1]) - max(a[0], b[0])) == 0:
        return True
    else:
        return False

def check_eight_hours_feasibility(w, nurse, check_job, check_day, jobs):
    # check for nurse i and day d
    # return True if feasible

    if not w[nurse, check_day]:
        return True
    else:
        early = (
            jobs[check_job]["tw_start"]
            + jobs[check_job]["duration"]
            - min(w[nurse, check_day])[0]
        )
        late = max(w[nurse, check_day])[1] - jobs[check_job]["tw_start"]
        if early < 480 and late < 480:
            return True
        else:
            return False

def check_eight_hours_feasibility_start(w, nurse, time_window, check_day):
    if not w[nurse, check_day]:
        return True
    else:
        early = time_window[1] - min(w[nurse, check_day])[0]
        late = max(w[nurse, check_day])[1] - time_window[0]
        if (early<480 and late<480):
            return True
        else:
            return False

def check_five_days_feasibility(w, i, day_except, days):
    # check for nurse i for a week
    # return True if feasible
    count_days_busy = 0
    for d in days:
        if w[i, d]:
            if d != day_except:
                count_days_busy += 1
    if count_days_busy < 5:
        return True
    else:
        return False

def calculate_start_time(w_init, nurse, job, day, jobs):
    w = w_init[nurse, day]
    if len(w) == 0:
        return jobs[job]['tw_start']
    w = sorted(w)
    x = jobs[job]
    #first check in between jobs
    if len(w) >= 2:
        for i in range(len(w) - 1):
            x = w[i+1][0]
            y = w[i][1]
            time_period = w[i+1][0] - w[i][1]
            if time_period < jobs[job]['duration']:
                continue
            else:
                if jobs[job]['tw_start'] > w[i+1][0] or jobs[job]['tw_due'] < w[i][0]:
                    continue
                else:
                    return max(jobs[job]['tw_start'], w[i][1])

      #check after jobs
    if jobs[job]['tw_due'] >= w[len(w)-1][1]:
        return max(w[len(w)-1][1], jobs[job]['tw_start'])

    #check before jobs
    if jobs[job]['tw_start'] + jobs[job]['duration'] + traveling_time <= w[0][0]:
        if jobs[job]['tw_due'] + jobs[job]['duration'] + traveling_time <= w[0][0]:  # if there is a gap between first working times and new job
            return jobs[job]['tw_due']
        else:
                return w[0][0] - jobs[job]['duration'] - traveling_time
    return -1

def check_all_jobs_assigned(nurses, sol, jobs, days):
    # return True if feasible
    # check if all jobs are assigned
    num_assigned = 0
    all_jobs = 0
    for j in jobs:
        for d in days:
            if jobs[j][d] == 1:
                all_jobs += 1
                for i in nurses:
                    if sol["z"][j, d] == i:
                        num_assigned += 1

    if num_assigned == all_jobs:
        return True
    else:
        return False


def check_enough_nurse(
    jobs, days, clients, number, search_previous, stop_step=5000, stop_time=10
):
    start = timer()
    # initial check if # of nurses is enough
    sol, nurses = generate_initial_solution(
        "heuristic", search_previous, jobs, days, clients
    )
    nurses_heuristic = len(nurses)

    # increase until reaching target number
    found = False
    if number > nurses_heuristic:
        cont = True
        prob1 = 1
        prob2 = 1
        if number > search_previous:
            raise ValueError("Too much nurses!")
        else:
            while cont:
                sol, nurses = generate_neighbour(
                    sol, nurses, prob1, prob2, jobs, days, clients
                )
                if number == len(nurses):
                    cont = False
                    found = True
                count_full = 0
                for d in days:
                    if sol["w"][max(nurses), d]:
                        count_full += 1
                if count_full == 0:
                    cont = False
                    raise ValueError("Too much nurses!")

    # decrease until reaching target number
    elif number < nurses_heuristic:
        cont = True
        prob1 = 1
        prob2 = 0
        num_steps = 0
        while cont:
            sol, nurses = generate_neighbour(
                sol, nurses, prob1, prob2, jobs, days, clients
            )
            current = timer()
            if number == len(nurses):
                cont = False
                found = True
            elif num_steps == stop_step or current - start >= stop_time:
                cont = False
                found = False
            num_steps += 1
    else:
        found = True
    return found, sol, nurses

def check_final_feasibility(nurses, sol, jobs, days):
    no_overlap = True
    eight_hours = True
    five_days = True
    # check the feasibility of the final solution
    for i in nurses:
        for d in days:
            for a in sol["w"][i, d]:
                for b in sol["w"][i, d]:
                    if a != b:
                        if not check_overlap(a, b):
                            no_overlap = False
                            break
                if not no_overlap:
                    break
            if not no_overlap:
                break
        if not no_overlap:
            break

    for i in nurses:
        for d in days:
            if sol["w"][i, d]:
                max_tw = [0, 0]
                min_tw = [1440, 1440]
                for tw_check in sol["w"][i, d]:
                    if tw_check < min_tw:
                        min_tw = tw_check
                    if tw_check > max_tw:
                        max_tw = tw_check
                diff = max_tw[1] - min_tw[0]
                if diff > 480:
                    eight_hours = False
                    break
        if not eight_hours:
            break

    for i in nurses:
        count_days_busy = 0
        for d in days:
            if sol["w"][i, d]:
                count_days_busy += 1
        if count_days_busy > 5:
            five_days = False
            break

    if (
        no_overlap
        and check_all_jobs_assigned(nurses, sol, jobs, days)
        and eight_hours
        and five_days
    ):
        return True
    else:
        return False

def heuristic(jobs, days, clients, number, search_previous):
    found, sol, nurses = check_enough_nurse(
        jobs, days, clients, number, search_previous
    )
    if found:
        return sol, nurses
    else:
        sol_heur, nurses_heur = generate_initial_solution(
            "heuristic", search_previous, jobs, days, clients
        )
        len_nurses_heur = len(nurses_heur)
        if number < len(nurses):
            print("Too few nurses! We suggest employing", len_nurses_heur, "nurses!")
            raise ValueError(
                "Too few nurses! We suggest employing", len_nurses_heur, "nurses!"
            )
        elif number > len(nurses):
            print("Too much nurses! We suggest employing", len_nurses_heur, "nurses!")
            raise ValueError(
                "Too much nurses! We suggest employing", len_nurses_heur, "nurses!"
            )
        return sol_heur, nurses_heur


def find_x(nurses, z, clients, jobs, days):
    # If client c sees nurse i during the week:
    x = {}
    for c in clients:
        for j in jobs:
            if jobs[j]["client_id"] == c:
                for d in days:
                    if jobs[j][d] == 1:
                        for i in nurses:
                            if z[j, d] == i:
                                x[c, i] = 1
                                # Break the inner loop..., no need to search more days
                                break
                break
    return x


def find_w(nurses, z, jobs, days):
    # time slots that nurse i is busy on day d:
    w = {}
    for i in nurses:
        for d in days:
            w[i, d] = []
            for j in jobs:
                if jobs[j][d] == 1:
                    if z[j, d] == i:
                        w[i, d].append(
                            [
                                jobs[j]["tw_start"],
                                jobs[j]["tw_start"] + jobs[j]["duration"] + traveling_time,
                            ]
                        )
    return w

# nurse i works at day d for client c between tw
def give_schedule(sol, nurses, days, jobs, clients):
    schedule = {}
    for i in nurses:
        schedule[i] = {}
        for d in days:
            schedule[i][d] = {}
            for j in jobs:
                if jobs[j][d] == 1:
                    if sol["z"][j, d] == i:
                        for c in clients:
                            if jobs[j]["client_id"] == c:
                                if c in schedule[i][d]:
                                    schedule[i][d][c].append(sol["t"][i, d, j])
                                else:
                                    schedule[i][d][c] = [sol["t"][i, d, j]]
                                break
    print(schedule)
    return schedule

# function needed for assignment:
def assign_to_other_nurses(
    search_previous,
    number_nurses,
    nurses,
    w_init,
    z_init,
    t_init,
    cand_j,
    cand_d,
    jobs,
    clients,
    days,
):
    found_one = False
    found = None

    # Find the set of nurses that client having job j on day d sees:
    for c in clients:
        if jobs[cand_j]["client_id"] == c:
            cand_c = c

    cand_i_list = []
    for i in nurses:
        assigned_to_i = False
        for j in jobs:
            # if job j belongs to client c
            if jobs[j]["client_id"] == cand_c:
                for d in days:
                    if jobs[j][d] == 1:
                        if z_init[j, d] == i:
                            assigned_to_i = True
                            break
        if assigned_to_i:
            cand_i_list.append(i)
    """
    print(cand_j)
    print(cand_d)
    print(cand_c)
    print(cand_i_list)
    """

    # if there are other nurses to check:
    if len(nurses) > 1:
        if len(nurses) < search_previous:
            for cand_i in cand_i_list:
                if cand_i != number_nurses:
                    # if this job fits the schedule of a nurse, choose her as a candidate for this job
                    start_time = calculate_start_time(w_init, cand_i, cand_j, cand_d, jobs)
                    if start_time == -1:
                        feasible = False
                    else:
                        tw_new = [start_time, start_time + jobs[j]['duration'] + traveling_time]
                        feasible = check_eight_hours_feasibility_start(
                            w_init, cand_i, tw_new, cand_d
                        ) and check_five_days_feasibility(w_init, cand_i, cand_d, days)
                    if feasible:
                        tw_feasible = True
                        for tw_exist in w_init[cand_i, cand_d]:
                            # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                            feasible = check_overlap(tw_new, tw_exist)
                            if not feasible:
                                tw_feasible = False
                                found = cand_i
                                break
                        if tw_feasible:
                            found_one = True
                            found = cand_i
                            break
            # if there is an available nurse, assign the job to her
            if found_one:
                z_init[cand_j, cand_d] = found
                w_init[found, cand_d].append(tw_new)
                t_init[found, cand_d, cand_j] = tw_new
            # if there is no available nurse that clients saw before, try other nurses:
            else:
                for cand_i in nurses:
                    if cand_i != number_nurses:
                        # if this job fits the schedule of a nurse, choose her as a candidate for this job
                        start_time = calculate_start_time(w_init, cand_i, cand_j, cand_d, jobs)
                        if start_time == -1:
                            feasible = False
                        else:
                            tw_new = [start_time, start_time + jobs[j]['duration'] + traveling_time]
                            feasible = check_eight_hours_feasibility_start(
                                w_init, cand_i, tw_new, cand_d
                            ) and check_five_days_feasibility(w_init, cand_i, cand_d, days)
                        if feasible:
                            tw_feasible = True
                            for tw_exist in w_init[cand_i, cand_d]:
                                # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                                feasible = check_overlap(tw_new, tw_exist)
                                if not feasible:
                                    tw_feasible = False
                                    found = cand_i
                                    break
                            if tw_feasible:
                                found_one = True
                                found = cand_i
                                break
                # if there is an available nurse, assign the job to her
                if found_one:
                    z_init[cand_j, cand_d] = found
                    w_init[found, cand_d].append(tw_new)
                    t_init[found, cand_d, cand_j] = tw_new
                # else, add one nurse to the system
                else:
                    tw_new = [
                        jobs[cand_j]["tw_start"],
                        jobs[cand_j]["tw_start"] + jobs[cand_j]["duration"] + traveling_time,
                    ]
                    number_nurses += 1
                    nurses.append(number_nurses)
                    z_init[cand_j, cand_d] = number_nurses
                    w_init[number_nurses, cand_d].append(tw_new)
                    t_init[number_nurses, cand_d, cand_j] = tw_new
        else:
            for cand_i in nurses[-search_previous:]:
                if cand_i != number_nurses:
                    # if this job fits the schedule of a nurse, choose her as a candidate for this job
                    start_time = calculate_start_time(w_init, cand_i, cand_j, cand_d, jobs)
                    if start_time == -1:
                        feasible = False
                    else:
                        tw_new = [start_time, start_time + jobs[j]['duration'] + traveling_time]
                        feasible = check_eight_hours_feasibility_start(
                            w_init, cand_i, tw_new, cand_d
                        ) and check_five_days_feasibility(w_init, cand_i, cand_d, days)
                    if feasible:
                        tw_feasible = True
                        for tw_exist in w_init[cand_i, d]:
                            # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                            feasible = check_overlap(tw_new, tw_exist)
                            if not feasible:
                                tw_feasible = False
                                found = cand_i
                                break
                        if tw_feasible:
                            found_one = True
                            found = cand_i
                            break
            # if there is an available nurse, assign the job to her
            if found_one:
                z_init[cand_j, cand_d] = found
                w_init[found, cand_d].append(tw_new)
                t_init[found, cand_d, cand_j] = tw_new
            # else, add one nurse to the system
            else:
                tw_new = [
                    jobs[cand_j]["tw_start"],
                    jobs[cand_j]["tw_start"] + jobs[cand_j]["duration"] + traveling_time,
                ]
                number_nurses += 1
                nurses.append(number_nurses)
                z_init[cand_j, cand_d] = number_nurses
                w_init[number_nurses, cand_d].append(tw_new)
                t_init[number_nurses, cand_d, cand_j] = tw_new
    else:
        tw_new = [
            jobs[cand_j]["tw_start"],
            jobs[cand_j]["tw_start"] + jobs[cand_j]["duration"] + traveling_time,
        ]
        number_nurses += 1
        nurses.append(number_nurses)
        z_init[cand_j, cand_d] = number_nurses
        w_init[number_nurses, cand_d].append(tw_new)
        t_init[number_nurses, cand_d, cand_j] = tw_new

    return number_nurses, nurses, w_init, z_init, t_init, cand_j, cand_d

def generate_initial_solution(init_method, search_previous, jobs, days, clients):
    # generate initial solution
    z = {}
    if init_method == "worst":
        nurses = []
        number_nurses = 1
        for d in days:
            for j in jobs:
                if jobs[j][d] == 1:
                    z[j, d] = number_nurses
                    nurses.append(number_nurses)
                    number_nurses += 1

    elif init_method == "heuristic":
        # Use the following heuristic to generate initial solution with fewer number of nurses:

        nurses = []
        number_nurses = search_previous
        for n in range(number_nurses):
            nurses.append(n)

        z_init = {}
        for j in jobs:
            for d in days:
                if jobs[j][d] == 1:
                    z_init[j, d] = None
        w_init = find_w(nurses, z_init, jobs, days)
        t_init = {}

        # start from a single nurse
        number_nurses = 1
        nurses = [number_nurses]
        # add jobs to a nurse day by day until there is an infeasibility in her schedule
        # if there is an infeasibility for this nurse, add one nurse or check the schedule of other nurses in the "nurses" list
        for j in jobs:
            for d in days:
                if jobs[j][d] == 1:
                    # if the job j on day d is unassigned:
                    # check the schedule of the current nurse for this job
                    feasible = check_five_days_feasibility(
                        w_init, number_nurses, d, days
                    )
                    # if 5 days feasibility is satisfied
                    if feasible:
                        # the time window of the job
                        start_time = calculate_start_time(w_init, number_nurses, j, d, jobs)
                        if start_time == -1:
                            tw_new = [jobs[j]["tw_start"], jobs[j]["tw_start"] + jobs[j]["duration"] + traveling_time]
                        else:
                            tw_new = [start_time, start_time + jobs[j]['duration'] + traveling_time]

                        # if there are other jobs assigned to the nurse on the day job should be done:
                        if w_init[number_nurses, d]:
                            # check if adding a new job causes 8-hours infeasibility:
                            feasible = check_eight_hours_feasibility_start(w_init, number_nurses, tw_new, d)
                            if feasible:
                                tw_feasible = True
                                for tw_exist in w_init[number_nurses, d]:
                                    # check overlaps:
                                    feasible = check_overlap(tw_new, tw_exist)
                                    if not feasible:
                                        tw_feasible = False
                                        break
                                # if there is no overlap, assign job to the nurse:
                                if tw_feasible:
                                    z_init[j, d] = number_nurses
                                    w_init[number_nurses, d].append(tw_new)
                                    t_init[number_nurses, d, j] = tw_new
                                # if there is an overlap, assign job to the other nurses:
                                else:
                                    (
                                        number_nurses,
                                        nurses,
                                        w_init,
                                        z_init,
                                        t_init,
                                        j,
                                        d,
                                    ) = assign_to_other_nurses(
                                        search_previous,
                                        number_nurses,
                                        nurses,
                                        w_init,
                                        z_init,
                                        t_init,
                                        j,
                                        d,
                                        jobs,
                                        clients,
                                        days,
                                    )

                            # if 8 hours feasibility is not satisfied
                            else:
                                (
                                    number_nurses,
                                    nurses,
                                    w_init,
                                    z_init,
                                    t_init,
                                    j,
                                    d,
                                ) = assign_to_other_nurses(
                                    search_previous,
                                    number_nurses,
                                    nurses,
                                    w_init,
                                    z_init,
                                    t_init,
                                    j,
                                    d,
                                    jobs,
                                    clients,
                                    days,
                                )

                        # if there is no job assigned yet to the nurse on the day job should be done:
                        else:
                            z_init[j, d] = number_nurses
                            w_init[number_nurses, d].append(tw_new)
                            t_init[number_nurses, d, j] = tw_new
                            # if 5 days feasibility is not satisfied
                    else:
                        (
                            number_nurses,
                            nurses,
                            w_init,
                            z_init,
                            t_init,
                            j,
                            d,
                        ) = assign_to_other_nurses(
                            search_previous,
                            number_nurses,
                            nurses,
                            w_init,
                            z_init,
                            t_init,
                            j,
                            d,
                            jobs,
                            clients,
                            days,
                        )

        for j in jobs:
            for d in days:
                if jobs[j][d] == 1:
                    z[j, d] = z_init[j, d]

    sol = {"z": z, "w": w_init, "t": t_init}

    if check_all_jobs_assigned(nurses, sol, jobs, days):
        return sol, nurses
    else:
        generate_initial_solution(init_method, search_previous, jobs, days, clients)


def generate_neighbour(sol, nurses, prob1, prob2, jobs, days, clients):
    # 1) DO BINARY SWITCH BETWEEN TWO JOBS (CHANGE THE ASSIGNMENTS), KEEP NUMBER OF NURSES THE SAME
    if random.uniform(0, 1) > prob1:

        # Find the client that sees maximum number of nurses
        cand_c = 0
        minmax = 0
        which_client = {}
        for c in clients:
            which_client[c] = {}
            count = 0
            for i in nurses:
                which_client[c][i] = []
                assigned_to_i = False
                for j in jobs:
                    # if job j belongs to client c
                    if jobs[j]["client_id"] == c:
                        for d in days:
                            if jobs[j][d] == 1:
                                if sol["z"][j, d] == i:
                                    assigned_to_i = True
                                    which_client[c][i].append([j, d])
                    if assigned_to_i:
                        count += 1
                        break
            if count > minmax:
                minmax = count
                cand_c = c

        # choose one job of this client
        # (if a nurse has a single job with the client, try giving this job to other nurses)
        cand_c_list = which_client[cand_c]
        minn = 1000000000
        for i in cand_c_list:
            if len(cand_c_list[i]) < minn and len(cand_c_list[i]) > 0:
                minn = len(cand_c_list[i])
                cand_i = i
        cand_j, cand_d = random.choice(cand_c_list[cand_i])

        # try to assign it to other nurses seeing that client
        new_i_list = []
        found_one = False
        for i in cand_c_list:
            if i != cand_i and len(cand_c_list[i]) > 0:
                if check_five_days_feasibility(sol["w"], i, cand_d, days):
                    start_time = calculate_start_time(sol["w"], i, cand_j, cand_d, jobs)
                    if start_time == -1:
                        time_window = [jobs[cand_j]["tw_start"], jobs[cand_j]["tw_start"] + jobs[cand_j]["duration"] + traveling_time]
                    else:
                        time_window = [start_time, start_time + jobs[cand_j]['duration'] + traveling_time]
                    if check_eight_hours_feasibility_start(sol["w"], i, time_window, cand_d):
                        # if there are other jobs assigned to the nurse on the day job should be done:
                        tw_feasible = True
                        for tw_exist in sol["w"][i, cand_d]:
                            # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                            feasible = check_overlap(time_window, tw_exist)
                            if not feasible:
                                tw_feasible = False
                                break
                        if tw_feasible:
                            # do binary switch between matches:
                            new_i_list.append(i)
                            found_one = True

        if found_one:
            new_i = random.choice(new_i_list)
            start_time = calculate_start_time(sol["w"], new_i, cand_j, cand_d, jobs)
            time_window = [start_time, start_time + jobs[cand_j]['duration'] + traveling_time]
            sol["w"][cand_i, cand_d].remove(sol["t"][cand_i, cand_d, cand_j])
            sol["w"][new_i, cand_d].append(time_window)
            sol["z"][cand_j, cand_d] = new_i
            sol["t"].pop((cand_i, cand_d, cand_j))
            sol["t"][new_i, cand_d, cand_j] = time_window
        else:
            # assign to random nurse
            new_i_list = []

            found_one = False
            for i in nurses:
                if i != cand_i:
                    if check_five_days_feasibility(sol["w"], i, cand_d, days):
                        start_time = calculate_start_time(sol["w"], i, cand_j, cand_d, jobs)
                        if start_time == -1:
                            time_window = [jobs[cand_j]["tw_start"], jobs[cand_j]["tw_start"] + jobs[cand_j]["duration"] + traveling_time]
                        else:
                            time_window = [start_time, start_time + jobs[cand_j]['duration'] + traveling_time]
                        if sol["w"][i, cand_d]:
                            if check_eight_hours_feasibility_start(sol["w"], i, time_window, cand_d):
                                # if there are other jobs assigned to the nurse on the day job should be done:
                                tw_feasible = True
                                for tw_exist in sol["w"][i, cand_d]:
                                    # if there is an overlap in candidate nurse's schedule on day d, skip to next nurse
                                    feasible = check_overlap(time_window, tw_exist)
                                    if not feasible:
                                        tw_feasible = False
                                        break
                                if tw_feasible:
                                    # do binary switch between matches:
                                    new_i_list.append(i)
                                    found_one = True
                        else:
                            new_i_list.append(i)
                            found_one = True
            if found_one:
                new_i = random.choice(new_i_list)
                start_time = calculate_start_time(sol["w"], new_i, cand_j, cand_d, jobs)
                time_window = [start_time, start_time + jobs[cand_j]['duration'] + traveling_time]
                sol["w"][cand_i, cand_d].remove(sol["t"][cand_i, cand_d, cand_j])
                sol["w"][new_i, cand_d].append(time_window)
                sol["z"][cand_j, cand_d] = new_i
                sol["t"].pop((cand_i, cand_d, cand_j))
                sol["t"][new_i, cand_d, cand_j] = time_window

    # 2) INCREASE/DECREASE THE NUMBER OF NURSES BY ONE
    else:
        # Decrease the number of nurses:
        if random.uniform(0, 1) > prob2:
            # choose one nurse:
            cand_i = random.choice(nurses)

            # check the jobs that the candidate nurse was previously assigned to:
            cand_j_list = []
            cand_d_list = []
            cand_c_list = []
            tw_cand = []
            for j in jobs:
                for d in days:
                    if jobs[j][d] == 1:
                        if sol["z"][j, d] == cand_i:
                            cand_j_list.append(j)
                            cand_d_list.append(d)
                            tw_cand.append(sol["t"][cand_i, d, j])
                            for c in clients:
                                if jobs[j]["client_id"] == c:
                                    cand_c_list.append(c)
                                    break

            # remove nurse:
            nurses.remove(cand_i)
            # assign all these jobs to other nurses:

            # choose another nurse, do feasibility check:
            new_i_list = []
            need_nurse = False
            for index in range(len(cand_j_list)):
                cand_j = cand_j_list[index]
                cand_d = cand_d_list[index]

                cand_i_list = []
                for i in nurses:
                    assigned_to_i = False
                    for j in jobs:
                        # if job j belongs to client c
                        if jobs[j]["client_id"] == cand_c_list[index]:
                            for d in days:
                                if jobs[j][d] == 1:
                                    if sol["z"][j, d] == i:
                                        assigned_to_i = True
                                        break
                    if assigned_to_i:
                        cand_i_list.append(i)

                nurse_candidates = []
                found_one = False
                # this nurse should not have jobs more than 5 days:
                # this nurse should not have another job started 8 hours ago or will start 8 hours later that day.
                for i in cand_i_list:
                    if check_five_days_feasibility(sol["w"], i, cand_d, days):
                        if sol["w"][i, cand_d]:
                            start_time = calculate_start_time(sol["w"], i, cand_j, cand_d, jobs)
                            if start_time == -1:
                                time_window = [jobs[j]["tw_start"], jobs[j]["tw_start"] + jobs[j]["duration"] + traveling_time]
                            else:
                                time_window = [start_time, start_time + jobs[cand_j]["duration"] + traveling_time]
                            if check_eight_hours_feasibility_start(sol["w"], i, time_window, cand_d):
                                tw_feasible = True
                                for tw_exist in sol["w"][i, cand_d]:
                                    feasible = check_overlap(tw_exist, time_window)
                                    if not feasible:
                                        tw_feasible = False
                                        break
                                if tw_feasible:
                                    found_one = True
                                    nurse_candidates.append(i)
                        else:
                            found_one = True
                            time_window = [jobs[cand_j]["tw_start"], jobs[cand_j]["tw_start"] + jobs[cand_j]['duration'] + traveling_time]
                            nurse_candidates.append(i)
                # We checked all feasibility constraints, let's finally choose one nurse candidate:
                if found_one:
                    new_i = random.choice(nurse_candidates)
                    start_time = calculate_start_time(sol["w"], new_i, cand_j, cand_d, jobs)
                    time_window = [start_time, start_time + jobs[cand_j]['duration'] + traveling_time]
                    sol["w"][cand_i, cand_d].remove(tw_cand[index])
                    sol["w"][new_i, cand_d].append(time_window)
                    sol["z"][cand_j, cand_d] = new_i
                    new_i_list.append(new_i)
                    sol["t"].pop((cand_i, cand_d, cand_j))
                    sol["t"][new_i, cand_d, cand_j] = time_window
                # If no candidate left, add nurse again:
                else:
                    for i in nurses:
                        if check_five_days_feasibility(sol["w"], i, cand_d, days):
                            if sol["w"][i, cand_d]:
                                start_time = calculate_start_time(sol["w"], i, cand_j, cand_d, jobs)
                                if start_time != -1:
                                    time_window = [start_time, start_time + jobs[cand_j]['duration'] + traveling_time]
                                else:
                                    time_window = [jobs[cand_j]['tw_start'], jobs[cand_j]['tw_start'] + jobs[cand_j]['duration'] + traveling_time]
                                if check_eight_hours_feasibility_start(sol["w"], i, time_window, cand_d):
                                    tw_feasible = True
                                    for tw_exist in sol["w"][i, cand_d]:
                                        feasible = check_overlap(tw_exist, time_window)
                                        if not feasible:
                                            tw_feasible = False
                                            break
                                    if tw_feasible:
                                        found_one = True
                                        nurse_candidates.append(i)
                            else:
                                found_one = True
                                time_window = [jobs[cand_j]['tw_start'], jobs[cand_j]['tw_start'] + jobs[cand_j]['duration'] + traveling_time]
                                nurse_candidates.append(i)
                    # We checked all feasibility constraints, let's finally choose one nurse candidate:
                    if found_one:
                        new_i = random.choice(nurse_candidates)
                        start_time = calculate_start_time(sol["w"], new_i, cand_j, cand_d, jobs)
                        time_window = [start_time, start_time + jobs[cand_j]['duration'] + traveling_time]
                        sol["w"][cand_i, cand_d].remove(tw_cand[index])
                        sol["w"][new_i, cand_d].append(time_window)
                        sol["z"][cand_j, cand_d] = new_i
                        new_i_list.append(new_i)
                        sol["t"].pop((cand_i, cand_d, cand_j))
                        sol["t"][new_i, cand_d, cand_j] = time_window
                    else:
                        need_nurse = True
            if need_nurse:
                nurses.append(cand_i)

        # Increase the number of nurses:
        elif random.uniform(0, 1) <= prob2 and len(nurses) < len(jobs) * len(days):
            # add new nurse
            new_nurse = max(nurses) + 1
            for d in days:
                sol["w"][new_nurse, d] = []

            for i in nurses:
                for (j, d), nurse in sol["z"].items():
                    if i == nurse:
                        if check_five_days_feasibility(sol["w"], new_nurse, d, days):
                            start_time = calculate_start_time(sol["w"], new_nurse, j, d, jobs)
                            if start_time == -1:
                                time_window = [jobs[j]["tw_start"], jobs[j]["tw_start"] + jobs[j]["duration"] + traveling_time]
                            else:
                                time_window = [start_time, start_time + jobs[j]['duration'] + traveling_time]
                            if sol["w"][new_nurse, d]:
                                if check_eight_hours_feasibility_start(sol["w"], new_nurse, time_window, d):
                                    tw_feasible = True
                                    for tw_exist in sol["w"][new_nurse, d]:
                                        feasible = check_overlap(time_window, tw_exist)
                                        if not feasible:
                                            tw_feasible = False
                                            break
                                    if tw_feasible:
                                        is_full = 0
                                        for d_num in days:
                                            if sol["w"][i, d_num]:
                                                is_full += 1
                                        if is_full >= 2:
                                            tw_old = sol["t"][i, d, j]
                                            sol["w"][i, d].remove(tw_old)
                                            sol["w"][new_nurse, d].append(time_window)
                                            sol["z"][j, d] = new_nurse
                                            sol["t"].pop((i, d, j))
                                            sol["t"][new_nurse, d, j] = time_window
                            else:
                                is_full = 0
                                for d_num in days:
                                    if sol["w"][i, d_num]:
                                        is_full += 1
                                if is_full >= 2:
                                    tw_old = sol["t"][i, d, j]
                                    sol["w"][i, d].remove(tw_old)
                                    sol["w"][new_nurse, d].append(time_window)
                                    sol["z"][j, d] = new_nurse
                                    sol["t"].pop((i, d, j))
                                    sol["t"][new_nurse, d, j] = time_window
            nurses.append(new_nurse)
    return sol, nurses


def calculate_number_of_nurses(sol, nurses, days):
    # calculates the number of nurses works based on solution
    number_nurses = 0
    for i in nurses:
        is_working = False
        for d in days:
            if sol["w"][i, d]:
                is_working = True
                break
        if is_working:
            number_nurses += 1
    return number_nurses

def greedy_algorithm(sol, nurses, time_limit, jobs, days, clients):
    start = timer()
    current = 0
    obj = calculate_obj(clients, jobs, days, sol, nurses)
    step = 0
    obj_list = [obj]
    nurse_list = [len(nurses)]
    # create a neighbour for initial solution
    new_sol, nurses = generate_neighbour(sol, nurses, prob1, prob2, jobs, days, clients)
    # compare objective functions for initial solution
    new_obj = calculate_obj(clients, jobs, days, new_sol, nurses)

    while new_obj <= obj:
        # if the new solution is better than the previous solution (minimization)
        obj = new_obj
        obj_list.append(obj)
        nurse_list.append(len(nurses))

        # keep track of number of steps in case of comparison with SA
        current = timer()

        if current - start > time_limit:
            print("Time limit is reached!")
            break
        else:
            # create a neighbour
            new_sol, nurses = generate_neighbour(
                sol, nurses, prob1, prob2, jobs, days, clients
            )

            # compare objective functions
            new_obj = calculate_obj(clients, jobs, days, new_sol, nurses)

            step += 1


    plt.plot(nurse_list)
    plt.ylabel("number of nurses")
    plt.show()

    plt.plot(obj_list)
    plt.ylabel("obj. value")
    plt.show()

    print("Computation Time:", current - start, "seconds")

    return new_sol, obj_list


def find_temperature(
    prob1, prob2, search_previous, num, acceptProb, jobs, days, clients
):
    summ = 0
    for i in range(num):
        sol, nurses = generate_initial_solution(
            "heuristic", search_previous, jobs, days, clients
        )
        obj = calculate_obj(clients, jobs, days, sol, nurses)
        new_sol, nurses = generate_neighbour(
            sol, nurses, prob1, prob2, jobs, days, clients
        )
        new_obj = calculate_obj(clients, jobs, days, new_sol, nurses)
        summ += abs(new_obj - obj)
    return (summ / num) / math.log(1 / acceptProb)


def SA_algorithm(
    sol,
    nurses,
    step_max,
    time_limit,
    stagnation,
    initial_temperature,
    number_of_nurses,
    jobs,
    days,
    clients,
):
    prob1 = 1
    prob2 = 0
    start = timer()
    count = 0
    step = 0
    obj = calculate_obj(clients, jobs, days, sol, nurses)
    obj_list = [obj]
    nurse_list = [len(nurses)]
    T = initial_temperature
    minimum_nurse = 0
    while step < step_max:

        # create a neighbour
        new_sol, nurses = generate_neighbour(
            sol, nurses, prob1, prob2, jobs, days, clients
        )

        # compare objective functions

        new_obj = calculate_obj(clients, jobs, days, new_sol, nurses)

        # if the new solution is better than the previous solution (minimization)
        if new_obj <= obj:
            obj = new_obj

        # if the new solution is worse than the previous solution (minimization)
        else:
            # normalization to make sure that the probability is between 0 and 1
            prob = math.exp(-(new_obj - obj) / T)
            # accept the worse solution:
            if prob > random.uniform(0, 1):
                obj = new_obj

        nurse_num = len(nurses)
        nurse_list.append(nurse_num)
        obj_list.append(obj)

        current = timer()

        # decrease number of nurses until reaching minimum number of nurses
        # warm up period to decrease number of nurses
        if not (nurse_num > number_of_nurses and nurse_num < nurse_list[-2]):
            minimum_nurse += 1

        # set initial temperature after number of nurses stabilizes
        # this gives more flexibility for switches
        if minimum_nurse == 1:
            T = initial_temperature

        # then start doing switch
        if minimum_nurse > 0:
            prob1 = 0.5
            prob2 = 0.5

        # convergence
        if len(obj_list) > stagnation and obj == obj_list[-2]:
            count += 1
        else:
            count = 0

        if count == stagnation:
            print("Stagnation: No more improvement for last", int(stagnation), "steps!")
            break
        elif current - start > time_limit:
            print("Time limit is reached!")
            break
        else:
            step += 1
            T = T * 0.995

    # some plots:
    plt.plot(nurse_list)
    plt.ylabel("number of nurses")
    plt.show()

    plt.plot(obj_list)
    plt.ylabel("obj. value")
    plt.show()

    print("Computation Time:", current - start, "seconds")

    return new_sol, obj_list


# =============================================================================
# PARAMETERS:
# =============================================================================

# days = sets['days']
# clients = sets['clients']

# Number of other nurses to check when the current nurse is not feasible.
# Currently, the algorithm selects all nurses as a candidate
# If you, for example, set search_previous=5, it will check 5 nurses' schedule
# If none of them feasible, it adds one nurse to the system.
# search_previous = len(jobs) * len(days)

# number of steps to be taken by SA
# step_max = 5000

# time limit to stop the algorithm (in seconds), no need to change atm
# time_limit = 600

# probability that governs neighbour generating rule:
# prob1: closer to 1 more changes in the number of nurses, less binary switches
# prob1: closer to 0 more binary switches, less changes in the number of nurses
prob1 = 0.9

# prob2: closer to 0 more decrements than increments in number of nurses
# prob2: closer to 1 more increments than decrements in number of nurses
prob2 = 0.1

# initial probability for simulated annealing algorithm transition
prob_init = 0.95

# method for finding the initial solution:
# "worst": the worst solution
# "heuristic": heuristic solution
init_method = "heuristic"

#standard traveling time
traveling_time = 5
