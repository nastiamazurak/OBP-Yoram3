import ast
import base64
import os

import pandas as pd

# from src.utils.functions import *
from timeit import default_timer as timer
import matplotlib
from utils.functions import *

matplotlib.use("Agg")

q = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main_path = os.path.dirname(os.getcwd()) + "/src/utils/uploads/"
UPLOAD_DIRECTORY = os.path.dirname(os.getcwd()) + "/utils/uploads/"
main_path = q + "/utils/uploads/"
UPLOAD_DIRECTORY = q + "/utils/uploads/"


if not os.path.exists(main_path):
    os.makedirs(main_path)


def save_file(content):
    # Decode and store a file uploaded from UI.
    print("Saving file")
    with open(os.path.join(main_path, "user_upload.csv"), "wb") as fp:
        fp.write(content)
    print(os.listdir(main_path))


def check_if_saved():
    if os.path.exists(main_path + "/user_upload.csv"):
        print("File has been saved. " + main_path + "/user_upload.csv")
        return True
    else:
        print("File has not been saved. " + main_path + "/user_upload.csv")
        return False


# convert time window hours to minutes, for example: 02:30 = 150
def hm_to_m(h):
    t = 0
    for u in h.split(":")[:-1]:
        t = 60 * t + int(u)
    return t


def initialize_dicts():
    try:
        # read CSV
        raw_data = pd.read_csv(main_path + "/user_upload.csv")

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


def get_suggested_number_of_nurses():
    jobs, sets = initialize_dicts()
    days = sets["days"]
    clients = sets["clients"]
    search_previous = len(jobs) * len(days)
    sol, nurses = generate_initial_solution(
        "heuristic", search_previous, jobs, days, clients
    )
    print(len(nurses))
    return len(nurses)

    # call function that returns # of nurses


# a function to call when a submit button is pressed
def run_algorithms(number_of_nurses):
    print("Running algorithm!!!")
    jobs, sets = initialize_dicts()
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
    # number_of_nurses = nurses
    sol_heuristic, nurses_heuristic = heuristic(
        jobs, days, clients, number_of_nurses, search_previous
    )
    obj_heuristic = calculate_obj(clients, jobs, days, sol_heuristic, nurses_heuristic)

    sol_approx, nurses_approx = generate_initial_solution(
        "heuristic", search_previous, jobs, days, clients
    )
    obj_approx = calculate_obj(clients, jobs, days, sol_approx, nurses_approx)
    # number of nurses needed approximately:
    print("Approximate number of nurses needed by heuristic: ", len(nurses_approx))
    print("Computation time:", timer() - start, "seconds")

    # print(sol)
    print(
        "Initial objective value for", len(nurses_heuristic), "nurses : ", obj_heuristic
    )
    print(
        "Check feasibility:",
        check_final_feasibility(nurses_heuristic, sol_heuristic, jobs, days),
    )

    # schedule = give_schedule(final_sol, nurses, days, jobs, clients)
    schedule = give_schedule(sol_heuristic, nurses_heuristic, days, jobs, clients)

    # if objective == "total":
    #     initial_temperature = 4.2  # :for total, found above, no need to run it again
    # elif objective == "minmax":
    #     initial_temperature = 0.9  # :for minmax, found above, no need to run it again
    print("The end of the algorithm")
    return sol_heuristic, nurses_heuristic, schedule

## Code for datasets: should be rewritten like that: def get_nurse_jobs(sol, nurses)


def get_nurse_jobs(sol, nurses):
    newList = list(sol["z"].items())

    justList = list(newList)

    # display(justList[0][1])

    ### [0][0][0] --> job id
    ### [0][0][1] --> day
    ### [0][1] --> nurse id

    df = pd.DataFrame(justList, columns=["Tuple", "Nurses"])

    # tup = tuple(list(df['Tuple']))
    # df['Tuple'] = tup
    # df['length'] = len(tup)
    # print('type is, ',df.Tuple.apply(type))
    # df[["job id", "day"]] = pd.DataFrame(df.Tuple.tolist(), index=df.index)
    df[["job id", "day"]] = df["Tuple"].str.split(",", expand=True)
    df["job id"] = df["job id"].str.extract("(\d+)").astype(int)
    df["day"] = df["day"].str.replace("'", "").str.strip()

    df = df.drop(columns="Tuple")
    # display(df)

    dataset = pd.read_csv(main_path + "user_upload.csv")

    dataset = dataset.iloc[:, :2]

    bigdf = pd.merge(dataset, df, left_on="job_id", right_on="job id", how="right")

    bigdf = bigdf.drop(columns="job_id")
    # display(bigdf)

    grouped = bigdf.groupby(["client_id", "day"])["Nurses"].nunique()
    grouped = grouped.reset_index()

    return grouped


def get_nurse_shifts(sol, nurses, schedule):
    def mins_to_hrs(minutes):
        hours, minutes = divmod(int(minutes), 60)
        return f"{hours:02d}:{minutes:02d}"

    nurse_id = []
    day = []
    client_id = []
    start_time = []
    end_time = []


    for n_id, days in schedule.items():
        for day_name, clients in days.items():
            for c_id, times in clients.items():
                for i in range(len(times)):
                    nurse_id.append(n_id)
                    day.append(day_name)
                    client_id.append(c_id)
                    start_time.append(times[i][0])
                    end_time.append(times[i][1])

    df = pd.DataFrame(
        {
            "nurse id": nurse_id,
            "day": day,
            "client_id": client_id,
            "start_time": start_time,
            "end_time": end_time,
        }
    )

    df["start_time"] = df["start_time"].apply(mins_to_hrs)
    df["end_time"] = df["end_time"].apply(mins_to_hrs)
    #print("this is Berkans new function output: ", df)

    return df


def get_hrs_worked(sol, nurses, schedule):
    q = get_nurse_shifts(sol, nurses, schedule)

    df = pd.DataFrame(q)

    df["start_time"] = pd.to_datetime(df["start_time"], format="%H:%M")

    df["end_time"] = pd.to_datetime(df["end_time"], format="%H:%M")
    first = df.groupby(["day", "nurse id"])["start_time"].min().reset_index()
    last = df.groupby(["day", "nurse id"])["end_time"].max().reset_index()
    shifts = pd.merge(
        first, last, left_on=["day", "nurse id"], right_on=["day", "nurse id"]
    )
    # shifts[["n", "nurse_id"]] = shifts["nurse"].str.split(" ", 1, expand=True)
    # shifts = shifts.drop(columns=["n", "task"])
    shifts["hrs_worked"] = shifts["end_time"] - shifts["start_time"]
    shifts["start_time"] = shifts["start_time"].dt.time
    shifts["end_time"] = shifts["end_time"].dt.time
    shifts["total_shift"] = shifts["hrs_worked"].apply(
        lambda x: x.total_seconds() / 3600
    )

    return shifts
