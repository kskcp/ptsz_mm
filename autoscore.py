from glob import glob
import traceback
import numpy as np
import sys
print("[AUTOSCORE]")

PATH_PREFIX = "zadanie3"

EXCEL = [
    132203,
    132325,
    136558,
    136674,
    136698,
    136704,
    136748,
    136751,
    136760,
    136800,
    136809,
    142192,
]


class Job:
    def __init__(self, p: list, d, w):
        self.p, self.d, self.w = p, d, w


def file_read_(path):
    with open(path, 'r') as file:
        data = file.read()
    return data


def get_solution(path):
    vec = open(path, 'r').read().split("\n")
    score, sol = float(vec[0]), vec[1]
    order = list(map(int, sol.strip().split(" ")))
    return score, order


def get_instance(instance_idx):
    owner_idx = instance_idx.split("_")[0]
    path = f"{PATH_PREFIX}/in/{owner_idx}/{instance_idx}.txt"
    data = file_read_(path).split("\n")
    N = int(data[0])
    jobs, P, D, W = [], [], [], []
    for job in data[1:]:
        if job == "":
            continue
        p1, p2, p3, d, w = list(map(int, job.split(" ")))
        P.append([p1, p2, p3])
        D.append(d)
        W.append(w)
    jobs = [Job(P[i], D[i], W[i]) for i in range(N)]
    return jobs, P, D, W


def loss(order, jobs):
    loss = 0
    m = len(jobs[0].p)
    t = [0 for _ in range(m)]
    for idx in order:
        job = jobs[idx-1]
        prev_time = 0
        for i in range(m):
            t[i] = max(t[i], prev_time)+job.p[i]
            prev_time = t[i]
        if job.d < prev_time:
            loss += job.w*(prev_time-job.d)
    return round(loss/sum([job.w for job in jobs]), 1)


def save_for_person(arr_score, person):
    path = f"score_{person}.txt"
    print(f"saving `{path}`")
    blob_arr = []
    for ref_person in EXCEL:
        for i in range(50, 500+50, 50):
            instance_idx = f"{ref_person}_{i}"
            try:
                blob_arr.append(arr_score[instance_idx])
            except:
                blob_arr.append("")
    with open(path, "w") as file:
        file.write("\n".join(map(str, blob_arr)))


status = 0
print(f"[run] path = {PATH_PREFIX}/out/*/")
status_dict = {}
for path_dir in glob(f"{PATH_PREFIX}/out/*/"):
    status_sum = 0
    status_local = 0
    dict_score = {}
    person = path_dir.split("/")[-2]
    if not person.isdigit():
        continue
    print(f"\033[92m[{person}]\033[0m verification")
    for path in glob(f"{path_dir}/*.txt") + glob(f"{path_dir}/*/*.txt"):
        instance_idx = path.replace(path_dir, "")\
            .replace(".txt_results", "").replace(".txt", "")
        if "/" in instance_idx:
            instance_idx = instance_idx.split("/")[-1]
        print(f"\t---> {instance_idx:12} | ", end="")
        try:
            jobs, P, D, W = get_instance(instance_idx)
            score, order = get_solution(path)
            score_verify = loss(order, jobs)
            status_sum += score_verify
            dict_score[instance_idx] = score_verify
            print(
                f"score_out={score:10} score_verify={score_verify:10}", end=" ")
            if abs(score - score_verify) <= 1.5:
                print("\033[92mOK\033[0m")
            else:
                print("\033[91mNO\033[0m")
                status = status_local = 1
        except AssertionError as error:
            _, _, tb = sys.exc_info()
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]

            print(f"\t[wrong format] {text} ", end="")
            print("\033[91mNO\033[0m")
            status = status_local = 1
    save_for_person(dict_score, person)
    if status_local == 1:
        status_dict[person] = 0
    else:
        status_dict[person] = round(status_sum, 1)
print("====== RESULT ======")
for person in EXCEL:
    print(f"[{person}] ", end="")
    if str(person) not in status_dict.keys():
        print("no out files")
        continue
    if status_dict[str(person)] > 0:
        print(f"\033[92mOK\033[0m sum={status_dict[str(person)]}")
    else:
        print("\033[91mNO\033[0m")
sys.exit(status)
