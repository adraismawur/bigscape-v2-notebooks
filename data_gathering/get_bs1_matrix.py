# partially generated using copilot

# goes through each folder in the path
# for each, reads the log file in it
# parses this log file for executing timing

from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ExecutionTime:
    start: datetime | float
    read_files: datetime | float
    hmm_scan: datetime | float
    hmm_align: datetime | float
    distance_calc: datetime | float
    cc_gen: datetime | float
    end: datetime | float

    def __init__(self):
        self.start = None
        self.read_files = None
        self.hmm_scan = None
        self.hmm_align = None
        self.distance_calc = None
        self.cc_gen = None
        self.end = None

    @classmethod
    def print_header(cls):
        return ",".join(
            [
                "start",
                "read_files",
                "hmm_scan",
                "hmm_align",
                "distance_calc",
                "cc_gen",
                "total",
            ]
        )

    def to_list(self):
        return [
            self.start,
            self.read_files,
            self.hmm_scan,
            self.hmm_align,
            self.distance_calc,
            self.cc_gen,
            self.end,
        ]

    def to_seconds(self):
        result = []

        if self.start is not None and self.start is not None:
            result.append((self.start - self.start).total_seconds())
        else:
            result.append(None)

        if self.read_files is not None and self.start is not None:
            result.append((self.read_files - self.start).total_seconds())
        else:
            result.append(None)

        if self.hmm_scan is not None and self.read_files is not None:
            result.append((self.hmm_scan - self.read_files).total_seconds())
        else:
            result.append(None)

        if self.hmm_align is not None and self.hmm_scan is not None:
            result.append((self.hmm_align - self.hmm_scan).total_seconds())
        else:
            result.append(None)

        if self.distance_calc is not None and self.hmm_align is not None:
            result.append((self.distance_calc - self.hmm_align).total_seconds())
        else:
            result.append(None)

        if self.cc_gen is not None and self.distance_calc is not None:
            result.append((self.cc_gen - self.distance_calc).total_seconds())
        else:
            result.append(None)

        if self.end is not None and self.start is not None:
            result.append((self.end - self.start).total_seconds())
        else:
            result.append(None)

        return result

    def __str__(self):
        return ",".join(
            map(
                str,
                [
                    self.start,
                    self.read_files,
                    self.hmm_scan,
                    self.hmm_align,
                    self.distance_calc,
                    self.cc_gen,
                    self.end,
                ],
            )
        )


def get_folders(path: Path):
    return [folder for folder in path.iterdir() if folder.is_dir()]


def get_v1_logfile(folder: Path):
    return folder / "logs" / "runtimes.txt"


def get_v1_start(folder: Path):
    # one of the first things written is parameters.txt under /logs
    return datetime.fromtimestamp((folder / "logs" / "parameters.txt").stat().st_mtime)


def get_v1_read_files(folder: Path):
    # fasta folder mtime should be equal to when the last file was written there.
    # this is done after the data is read in as one of the last steps relevant to input parsing
    return datetime.fromtimestamp((folder / "cache" / "fasta").stat().st_mtime)


def get_v1_hmmscan_times(folder: Path):
    # mtime for domtable folder. last file in this is the end of this step
    domtable_folder = folder / "cache" / "domtable"

    return datetime.fromtimestamp(domtable_folder.stat().st_mtime)


def get_v1_hmmalign_times(folder: Path):
    # mtime for pfd or pfs folder. pfd is fine. last file is end of hmmalign
    pfd_folder = folder / "cache" / "pfd"

    return datetime.fromtimestamp(pfd_folder.stat().st_mtime)


def get_v1_distance_calc(folder: Path):
    # after much thought, in mix mode the modify time of the results/network_files/[timestamp]/mix/mix_c0.30.network file
    # is the better way of measuring this one. the runtime log only reports the execution of the generate_networks function,
    # but there is more to only that function that is relevant to the distance calculation step

    network_files_subfolder = folder / "network_files"
    # just get the first subfolder
    network_files_result_folder = list(network_files_subfolder.iterdir())[0]
    # network file will be under that folder / mix / mix_c0.30.network
    network_file = network_files_result_folder / "mix" / "mix_c0.30.network"
    # mtime of that
    return datetime.fromtimestamp(network_file.stat().st_mtime)


def get_execution_time(result_path: Path):
    execution_time = ExecutionTime()

    execution_time.start = get_v1_start(result_path)
    execution_time.read_files = get_v1_read_files(result_path)
    execution_time.hmm_scan = get_v1_hmmscan_times(result_path)
    execution_time.hmm_align = get_v1_hmmalign_times(result_path)
    execution_time.distance_calc = get_v1_distance_calc(result_path)

    with open(get_v1_logfile(result_path)) as f:
        for line in f:
            if line.strip().startswith("Main function took"):
                execution_time.end = execution_time.start + timedelta(
                    seconds=float(line.split()[-2])
                )
                # we can't determine output generation, so it will be included in gcf calling
                # this is end of distance calculation to end of the program
                execution_time.cc_gen = execution_time.end

    return execution_time


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", type=Path)

    args = parser.parse_args()

    print("size,sample," + ExecutionTime.print_header())

    def collate_results(path):

        for folder in get_folders(path):
            # folder is samplesize_"replicate"_sample
            parts = folder.name.split("_")

            size, _replicate, sample = parts
            size = int(size)
            sample = int(sample)

            if len(parts) != 3:
                parts = ["unknown", "unknown", "unknown"]
            execution_time = get_execution_time(folder)
            # print(execution_time)
            results = [size, sample, *execution_time.to_seconds()]
            yield results

    def sort_key(result):
        return result[0]

    for result in sorted(collate_results(args.path), key=sort_key):
        str_list = map(str, result)
        print(",".join(str_list))
