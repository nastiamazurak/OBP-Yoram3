import base64
import os
import pandas as pd
from .functions import *
from timeit import default_timer as timer

UPLOAD_DIRECTORY = "utils/uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


def save_file(name, content):
    # Decode and store a file uploaded from UI.
    print("Saving file")
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(content)
    print(os.listdir(UPLOAD_DIRECTORY))


# convert time window hours to minutes, for example: 02:30 = 150
def hm_to_m(h):
    t = 0
    for u in h.split(":")[:-1]:
        t = 60 * t + int(u)
    return t


def initialize_dicts(filename):
    try:
        # read CSV
        raw_data = pd.read_csv("utils/uploads/" + filename)

        # read headers
        header_names = []
        for header in raw_data:
            header_names.append(header)

        # convert data to arrays
        data = raw_data.values.tolist()
    except:
        raise ValueError("Wrong file name!")

    # create dictionary with job id
    jobs = {}
    for row in data:
        jobs[row[0]] = {}
        # assign parameters to the job
        posit = 1
        for col in row[1:]:
            jobs[row[0]][header_names[posit]] = col
            posit += 1
        # convert duration to minutes (not necessary, but why not)
        jobs[row[0]]["duration"] /= 60
        jobs[row[0]]["tw_start"] = hm_to_m(jobs[row[0]]["tw_start"])
        jobs[row[0]]["tw_due"] = hm_to_m(jobs[row[0]]["tw_due"])

    # =============================================================================
    # Define sets
    # =============================================================================
    sets = {}
    days = header_names[-7:]
    clients = list(dict.fromkeys(raw_data.client_id.values.tolist()))

    sets["days"] = days
    sets["clients"] = clients

    return jobs, sets


def get_suggested_number_of_nurses(filename):
    jobs, sets = initialize_dicts(filename)
    # call function that returns # of nurses


# a function to call when a submit button is pressed
def run_algorithms(filename):
    jobs, sets = initialize_dicts(filename)
    days = sets["days"]
    clients = sets["clients"]

    search_previous = len(jobs) * len(days)

    # number of steps to be taken by SA
    step_max = 2000

    # time limit to stop the algorithm (in seconds), no need to change atm
    time_limit = 600

    # probability that governs neighbour generating rule:
    # prob1: closer to 1 more changes the number of nurses, less binary switches
    # prob1: closer to 0 more binary switches, less changes in the number of nurses
    prob1 = 0.9

    # prob2: closer to 0 more decrements than increments in number of nurses
    # prob2: closer to 1 more increments than decrements in number of nurses
    prob2 = 0.1

    # initial probability for simulated annealing algorithm transition
    prob_init = 0.95

    # If there is no improvement in last #stagnation steps, terminate the algorithm
    stagnation = step_max / 5

    # objective function:
    # "total": minimize the total number of nurses seen by clients
    # "minmax": minimize the max number of nurses seen by clients
    objective = "total"

    # method for finding the initial solution:
    # "worst": the worst solution
    # "heuristic": heuristic solution
    init_method = "worst"

    # =============================================================================
    # Run algorithms:
    # =============================================================================

    # algorihtms

    print("-----HEURISTIC-----")
    start = timer()
    sol, nurses = generate_initial_solution("heuristic", search_previous, jobs, days)
    obj = calculate_obj(sol, jobs, objective, clients, nurses, days)

    # number of nurses needed approximately:
    print("Approximate number of nurses needed by heuristic: ", len(nurses))
    print("Computation time:", timer() - start, "seconds")
    # print(sol)
    print("Initial objective value : ", obj)
    print("Check feasibility:", check_final_feasibility(nurses, sol, jobs, days))

    print("\n-----GREEDY ALGORITHM-----")

    start = timer()
    sol, nurses = generate_initial_solution(init_method, search_previous, jobs, days)
    obj = calculate_obj(sol, jobs, objective, clients, nurses, days)

    final_sol, obj_list = greedy_algorithm(sol, nurses, time_limit)
    print("Number of nurses found by greedy algorithm: ", len(nurses))
    # print(final_sol)

    print("Objective falue for", objective, "number of nurses seen: ", obj_list[-1])
    print(
        "Check feasibility of the final solution:",
        check_final_feasibility(nurses, final_sol, jobs, days),
    )

    print("\n-----SIMULATED ANNEALING ALGORITHM-----")

    # avg_over=10000
    # initial_temperature = find_temperature(avg_over,prob_init)
    # print(initial_temperature)

    if objective == "total":
        initial_temperature = 4.2  # :for total, found above, no need to run it again
    elif objective == "minmax":
        initial_temperature = 0.9  # :for minmax, found above, no need to run it again

    start = timer()
    sol, nurses = generate_initial_solution(init_method, search_previous, jobs, days)
    final_sol, obj_list = SA_algorithm(sol, nurses, step_max, time_limit, stagnation)
    print("Number of nurses found by simulated annealing algorithm: ", len(nurses))
    # print(final_sol)

    # check feasilbility of the final solution (not complete)
    print("Objective value for", objective, "number of nurses seen:", obj_list[-1])
    print(
        "Check feasibility of the final solution:",
        check_final_feasibility(nurses, final_sol, jobs, days),
    )

    ## TODO: return smth; If needed split this massive function into smaller one
