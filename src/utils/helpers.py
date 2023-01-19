import base64
import os
import pandas as pd

UPLOAD_DIRECTORY = "utils/uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


def save_file(name, content):
    # Decode and store a file uploaded from UI.
    print("Saving file")
    with open(os.path.join(UPLOAD_DIRECTORY, "hhc_job_data.csv"), "wb") as fp:
        # fp.write(base64.decodebytes(content))
        fp.write(content)
    print(os.listdir(UPLOAD_DIRECTORY))


# convert time window hours to minutes, for example: 02:30 = 150
def hm_to_m(h):
    t = 0
    for u in h.split(":")[:-1]:
        t = 60 * t + int(u)
    return t


def parse_dataset(filename):
    try:
        # read CSV
        raw_data = pd.read_csv("uploads/" + filename)

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
