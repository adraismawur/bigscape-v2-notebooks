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
from datetime import datetime


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


def get_subfolder_stats(path: Path):

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

    # get the mtime of the network file
    network_files_folder = path / "network_files"
    if not network_files_folder.exists():
        return None

    network_cutoff_folder = next(network_files_folder.iterdir(), None)

    if not network_cutoff_folder or not network_cutoff_folder.is_dir():
        return None

    mix_folder = network_cutoff_folder / "mix"
    network_file = mix_folder / "mix_c0.30.network"
    if not network_file.exists():
        return None
    post_distance_calculation = datetime.fromtimestamp(network_file.stat().st_mtime)

    return [post_distance_calculation, last_modified_time, pre_crash_time]


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

    print("size,sample,gcf_calling_start,gcf_calling_end,pre_crash_time")
    for subfolder in path.iterdir():
        if not subfolder.is_dir():
            continue

        subfolder_samples = subfolder.name.split("_")[0]
        subfolder_replicate = subfolder.name.split("_")[2]

        stats.append(
            [subfolder_samples, subfolder_replicate] + get_subfolder_stats(subfolder)
        )

    # sort first by samples, then by replicate
    stats.sort(key=lambda x: (x[0], x[1]))

    for stat in stats:
        if stat[2] is None or stat[3] is None:
            continue

        gcf_calling_start = stat[2]
        gcf_calling_end = stat[3]
        pre_crash_time = stat[4]

        print(
            f"{stat[0]},{stat[1]},"
            f"{gcf_calling_start.isoformat()},{gcf_calling_end.isoformat()},"
            f"{pre_crash_time.isoformat() if pre_crash_time else 'None'}"
        )
