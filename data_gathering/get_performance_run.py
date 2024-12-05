from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path


def print_profile_matrix_line_v1(version, parts, start):

    time = datetime.fromisoformat(parts[0])
    seconds = (time - start).total_seconds()

    # cpu = float(parts[2]) if parts[1] != "MULTI" else 0.0
    # processes = int(parts[3]) if parts[1] == "MULTI" else 0
    # mem_used_mb = float(parts[4]) if parts[1] == "MAIN" else 0.0

    cpu = float(parts[2]) if parts[1] != "MULTI" else 0.0
    processes = int(parts[3]) if parts[1] == "MULTI" else 0
    mem_used_mb = float(parts[4]) if parts[1] == "MAIN" else 0.0

    memused_percent = float(parts[5])

    print(f"{version},{seconds},{cpu},{processes},{mem_used_mb},{memused_percent}")


def print_profile_matrix_line_v2(version, parts, start):
    time = datetime.fromisoformat(parts[0])
    seconds = (time - start).total_seconds()

    cpu = float(parts[2]) if parts[1] != "MULTI" else 0.0
    processes = int(parts[3])
    mem_used_mb = float(parts[4]) if parts[1] == "MULTI" else 0.0

    # cpu = float(parts[2]) if "CHILD" in parts[1] else 0.0
    # processes = int(parts[3])
    # mem_used_mb = float(parts[4]) if parts[1] == "MAIN" else 0.0

    memused_percent = float(parts[5]) if parts[1] == "MAIN" else 0.0

    print(f"{version},{seconds},{cpu},{processes},{mem_used_mb},{memused_percent}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("v1_folder", type=Path)
    parser.add_argument("v2_folder", type=Path)

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

            print_profile_matrix_line_v1("v1", parts, v1_start)

    v2_start: datetime
    with open(v2_profile) as f:
        # skip header
        f.readline()

        v2_start = datetime.fromisoformat(f.readline().split(",")[0])

        for line in f:
            parts = line.split(",")

            print_profile_matrix_line_v2("v2", parts, v2_start)
