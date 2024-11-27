# partially generated using copilot

# goes through each folder in the path
# for each, reads the log file in it
# parses this log file for executing timing

from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ExecutionTime:
    start: datetime | float
    hmm_scan: datetime | float
    hmm_scan_save: datetime | float
    hmm_align: datetime | float
    hmm_align_save: datetime | float
    distance_calc: datetime | float
    cc_gen: datetime | float
    cc_gen_save: datetime | float
    end: datetime | float

    def __init__(self):
        self.start = None
        self.hmm_scan = None
        self.hmm_scan_save = None
        self.hmm_align = None
        self.hmm_align_save = None
        self.distance_calc = None
        self.cc_gen = None
        self.cc_gen_save = None
        self.end = None

    @classmethod
    def print_header(cls):
        return ",".join(
            [
                "start",
                "hmm_scan",
                "hmm_scan_save",
                "hmm_align",
                "hmm_align_save",
                "distance_calc",
                "cc_gen",
                "cc_gen_save",
                "total",
            ]
        )

    def to_list(self):
        return [
            self.start,
            self.hmm_scan,
            self.hmm_scan_save,
            self.hmm_align,
            self.hmm_align_save,
            self.distance_calc,
            self.cc_gen,
            self.cc_gen_save,
            self.end,
        ]

    def to_seconds(self):
        return [
            (self.start - self.start).total_seconds(),
            (self.hmm_scan - self.start).total_seconds(),
            (self.hmm_scan_save - self.hmm_scan).total_seconds(),
            (self.hmm_align - self.hmm_scan_save).total_seconds(),
            (self.hmm_align_save - self.hmm_align).total_seconds(),
            (self.distance_calc - self.hmm_align_save).total_seconds(),
            (self.cc_gen - self.distance_calc).total_seconds(),
            (self.cc_gen_save - self.cc_gen).total_seconds(),
            (self.end - self.start).total_seconds(),
        ]

    def __str__(self):
        return ",".join(
            map(
                str,
                [
                    self.start,
                    self.hmm_scan,
                    self.hmm_scan_save,
                    self.hmm_align,
                    self.hmm_align_save,
                    self.distance_calc,
                    self.cc_gen,
                    self.cc_gen_save,
                    self.end,
                ],
            )
        )


def get_folders(path: Path):
    return [folder for folder in path.iterdir() if folder.is_dir()]


def get_files(folder: Path):
    yield from filter(
        lambda file: file.suffix == ".log",
        folder.iterdir(),
    )


def get_execution_time(log_file: Path):
    execution_time = ExecutionTime()
    with open(log_file, "r") as file:
        for line in file:
            parts = line.split(maxsplit=3)
            if len(parts) != 4:
                continue
            date, time, _loglevel, log = parts

            parsed_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S,%f")

            if log.startswith("Starting BiG-SCAPE"):
                execution_time.start = parsed_time

            if log.startswith("Loading ") and log.endswith("First task: TASK.HMM_SCAN"):
                execution_time.read_files = parsed_time

            if log.startswith("scan done at "):
                execution_time.hmm_scan = parsed_time

            if log.startswith("DB: HSP save done at"):
                execution_time.hmm_scan_save = parsed_time

            if log.startswith("align done at "):
                execution_time.hmm_align = parsed_time

            if log.startswith("DB: HSP alignment save done at"):
                execution_time.hmm_align_save = parsed_time

            if log.startswith("Generating families"):
                execution_time.distance_calc = parsed_time

            if log.endswith("connected components\n"):
                execution_time.cc_gen = parsed_time

            if log.startswith("Generating GCF alignments"):
                execution_time.cc_gen_save = parsed_time

            if log.startswith("All tasks done at"):
                execution_time.end = parsed_time

    return execution_time


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", type=Path)

    # flag to have folder name be the entire sample name
    parser.add_argument("-f", "--folder_name_as_sample", action="store_true")


    args = parser.parse_args()

    print("size,sample," + ExecutionTime.print_header())

    def collate_results(path):

        for folder in get_folders(path):
            # folder is samplesize_"replicate"_sample

            if args.folder_name_as_sample:
                parts = [-1, -1, folder.name]
                size, _replicate, sample = parts
            else:
                parts = folder.name.rsplit("_", maxsplit=2)
                size, _replicate, sample = parts

                size = int(size)
                sample = int(sample)


            if len(parts) != 3:
                parts = ["unknown", "unknown", "unknown"]
            for file in get_files(folder):
                execution_time = get_execution_time(file)
                results = [size, sample, *execution_time.to_seconds()]
                yield results

    def sort_key(result):
        return result[0]

    for result in sorted(collate_results(args.path), key=sort_key):
        str_list = map(str, result)
        print(",".join(str_list))
