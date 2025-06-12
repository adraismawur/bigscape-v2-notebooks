# partially generated using copilot

# this does the following:
# - goes through each folder in the path,
#
# - grabs the modify time of this file:
# [folder]/network_files/[network cutoff folder]/mix/"mix_c0.30.network"
# this is the network file that is generated during distance calculation
#
# - grabs the **creation** time of this file:
# [folder]/html_content/networks/[network cutoff folder]/mix/bs_networks.js
# this file is created during the gcf calling step.
# bigscape v1 crashes during the creation of this file in large datasets
#
# - grabs the last modified time of this file:
# [folder]/logs/runtimes.txt
# this is the last file to be touched during the execution of bigscape v1
#
# - calculates the difference between the network file mtime and runtimes.txt file ctime
# this is the total execution time of the gcf calling step
# - calculates the difference between the creation time of the js file and the runtimes.txt file
# this is the portion that is missing in the v1 crash
#
# - after collecting all the data, calculates the missing time as a projection

from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime, timedelta
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="white")

COLORS = {
    "bigscape_blue": "#52A3A3",
    "dark_blue": "#0E75BB",
    "orange_i_found_on_bigscape_image": "#F7931E",
    "antismash_red": "#AA0000",
    "bigslice_grey": "#515154",
}

mpl.rcParams["svg.fonttype"] = "none"


def get_js_file(path: Path):
    html_networks_folder = path / "html_content" / "networks"
    if not html_networks_folder.exists():
        return None

    # should contain only one subfolder
    html_nw_cutoff_folder = next(html_networks_folder.iterdir(), None)

    if not html_nw_cutoff_folder or not html_nw_cutoff_folder.is_dir():
        return None

    html_nw_mix_folder = html_nw_cutoff_folder / "mix"

    if not html_nw_mix_folder.exists():
        return None

    js_file = html_nw_mix_folder / "bs_networks.js"

    if not js_file.exists():
        return None

    return js_file


def get_v1_hmmalign_times(folder: Path):
    # mtime for pfd or pfs folder. pfd is fine. last file is end of hmmalign
    pfd_folder = folder / "cache" / "pfd"

    return datetime.fromtimestamp(pfd_folder.stat().st_mtime)


def get_v1_start(folder: Path):
    # one of the first things written is parameters.txt under /logs
    return datetime.fromtimestamp((folder / "logs" / "parameters.txt").stat().st_mtime)


def get_v1_distance_calc(folder: Path):
    # get the mtime of the network file
    network_files_folder = folder / "network_files"
    if not network_files_folder.exists():
        return None

    network_cutoff_folder = next(network_files_folder.iterdir(), None)

    if not network_cutoff_folder or not network_cutoff_folder.is_dir():
        return None

    mix_folder = network_cutoff_folder / "mix"
    network_file = mix_folder / "mix_c0.30.network"
    if not network_file.exists():
        return None
    return datetime.fromtimestamp(network_file.stat().st_mtime)


def get_subfolder_stats(path: Path):
    start_time = get_v1_start(path)

    post_hmmalign_time = get_v1_hmmalign_times(path)

    post_distance_calculation = get_v1_distance_calc(path)

    # get the creation time of the js file
    js_file = get_js_file(path)

    pre_crash_time = (
        datetime.fromtimestamp(js_file.stat().st_ctime) if js_file else None
    )

    # get the last modified time of the runtimes.txt file
    runtimes_file = path / "logs" / "runtimes.txt"
    if not runtimes_file.exists():
        return None

    last_modified_time = datetime.fromtimestamp(runtimes_file.stat().st_mtime)

    return [
        start_time,
        post_hmmalign_time,
        post_distance_calculation,
        pre_crash_time,
        last_modified_time,
    ]


if __name__ == "__main__":
    parser = ArgumentParser(description="Get v1 post crash stats")
    parser.add_argument(
        "path", type=Path, help="Path to the folder containing the results"
    )

    args = parser.parse_args()

    path = args.path

    if not path.exists() or not path.is_dir():
        print(f"Path {path} does not exist or is not a directory.")
        exit(1)

    stats = []

    print(
        "size,sample,run_start,distance_calc_end,pre_crash_time,run_end,missing_runtime"
    )
    for subfolder in path.iterdir():
        if not subfolder.is_dir():
            continue

        subfolder_samples = subfolder.name.split("_")[0]
        subfolder_replicate = subfolder.name.split("_")[2]

        stats.append(
            [subfolder_samples, subfolder_replicate] + get_subfolder_stats(subfolder)
        )

    # sort first by samples, then by replicate
    # this is just for printing things in order
    stats.sort(key=lambda x: (int(x[0]), x[1]))

    # data for the estimate later
    post_crash_estimate_data = []
    start_50k = None
    pre_crash_50k = None

    # go through all the stats and print them
    for stat in stats:
        if stat[2] is None or stat[3] is None:
            continue

        run_start = stat[2]
        distance_calc_end = stat[4]
        pre_crash_time = stat[5]
        end_time = stat[6]
        missing_runtime = None

        # here we have to calculate the post crash time for everything under 50k samples
        if int(stat[0]) < 50000:
            missing_runtime = end_time - pre_crash_time
            post_crash_estimate_data.append(
                [float(stat[0]), float(missing_runtime.total_seconds())]
            )
        # for 50k samples, we need to store the start time and pre crash time
        else:
            start_50k = run_start
            pre_crash_50k = pre_crash_time
            end_time = None

        # convert everything to seconds
        run_start_seconds = 0
        distance_calc_end_seconds = (distance_calc_end - run_start).total_seconds()
        pre_crash_time_seconds = (pre_crash_time - run_start).total_seconds()
        end_time_seconds = (end_time - run_start).total_seconds()

        print(
            f"{stat[0]},{stat[1]},"
            f"{run_start.isoformat()},"
            f"{distance_calc_end.isoformat()},"
            f"{pre_crash_time.isoformat()},"
            f"{end_time.isoformat()},",
            f"{missing_runtime if missing_runtime else ''}",
        )
