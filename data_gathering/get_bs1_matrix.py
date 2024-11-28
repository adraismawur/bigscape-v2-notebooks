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
    hmm_scan: datetime | float
    hmm_align: datetime | float
    distance_calc: datetime | float
    cc_gen: datetime | float
    end: datetime | float

    def __init__(self):
        self.start = None
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
            self.hmm_scan,
            self.hmm_align,
            self.distance_calc,
            self.cc_gen,
            self.end,
        ]

    def to_seconds(self):
        return [
            (self.start - self.start).total_seconds(),
            (self.hmm_scan - self.start).total_seconds(),
            (self.hmm_align - self.hmm_scan).total_seconds(),
            (self.distance_calc - self.hmm_align).total_seconds(),
            (self.cc_gen - self.distance_calc).total_seconds(),
            (self.end - self.start).total_seconds(),
        ]

    def __str__(self):
        return ",".join(
            map(
                str,
                [
                    self.start,
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
    # can be based on the creation time of the fasta folder
    return datetime.fromtimestamp((folder / "cache" / "fasta").stat().st_mtime)


def get_v1_hmmscan_times(folder: Path):
    # mtime for domtable folder
    domtable_folder = folder / "cache" / "domtable"

    return domtable_folder.stat().st_mtime


def get_v1_hmmalign_times(folder: Path):
    # mtime for pfd or pfs folder. pfd is fine
    pfd_folder = folder / "cache" / "pfd"

    return pfd_folder.stat().st_mtime


def get_distance_times(folder: Path):
    # folder called network_files will have subfolders. take the oldest

    network_files_folder = folder / "network_files"
    oldest = sorted(network_files_folder.iterdir(), key=lambda x: x.stat().st_mtime)[0]
    return datetime.fromtimestamp(oldest.stat().st_mtime)


def get_execution_time(result_path: Path):
    execution_time = ExecutionTime()

    execution_time.start = get_v1_start(result_path)

    execution_time.hmm_scan = get_v1_hmmscan_times(result_path)
    execution_time.hmm_align = get_v1_hmmalign_times(result_path)
    execution_time.distance_calc = get_distance_times(result_path)

    with open(get_v1_logfile(result_path)) as f:
        for line in f:
            if line.strip().startswith("Main function took"):
                execution_time.end = execution_time.start + timedelta(
                    0, float(line.split()[-2])
                )
            if line.strip().startswith("generate_network took"):
                execution_time.cc_gen = execution_time.distance_calc + timedelta(
                    0, float(line.split()[-2])
                )

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
            try:
                results = [size, sample, *execution_time.to_seconds()]
                yield results
            except:
                # don't care about this error
                pass

    def sort_key(result):
        return result[0]

    for result in sorted(collate_results(args.path), key=sort_key):
        str_list = map(str, result)
        print(",".join(str_list))
