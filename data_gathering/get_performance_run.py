from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path


def print_profile_matrix_line(version, parts, start, type="MULTI", adjust_mem_subprocesses=False):

    if parts[1] != type:
        return

    time = datetime.fromisoformat(parts[0])
    seconds = (time - start).total_seconds()

    cpu = float(parts[2])
    processes = int(parts[3])
    mem_used_mb = float(parts[4])

    # there seems to be a difference between the multiprocessing used in v1 vs
    # v2. in v2, the memory appears accurate on the multi type log, but in v2 this
    # appears summed for all processes. so we need to adjust this.
    if adjust_mem_subprocesses:
        mem_used_mb /= processes

    memused_percent = float(parts[5])

    print(f"{version},{seconds},{cpu},{processes},{mem_used_mb},{memused_percent}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("v1_folder", type=Path)
    parser.add_argument("v2_folder", type=Path)

    parser.add_argument("--type", default="MULTI")

    args = parser.parse_args()

    v1_folder: Path = args.v1_folder
    v2_folder: Path = args.v2_folder

    v1_profile = next(v1_folder.glob("*.profile"))
    v2_profile = next(v2_folder.glob("*.profile"))

    print("version,seconds,cpu,processes,mem_used_mb,memused_percent")

    v1_start: datetime
    with open(v1_profile) as f:
        # skip header
        f.readline()
        
        v1_start = datetime.fromisoformat(f.readline().split(",")[0])

        for line in f:
            parts = line.split(",")

            print_profile_matrix_line("v1", parts, v1_start, args.type)

    
    v2_start: datetime
    with open(v2_profile) as f:
        # skip header
        f.readline()
        
        v2_start = datetime.fromisoformat(f.readline().split(",")[0])

        for line in f:
            parts = line.split(",")

            print_profile_matrix_line("v2", parts, v2_start, args.type, True)


