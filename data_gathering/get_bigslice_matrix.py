# partially generated using copilot

# goes through each folder in the path
# for each, reads the log file in it
# parses this log file for executing timing

from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime, timedelta
from dataclasses import dataclass
import sqlite3


@dataclass
class ExecutionTime:
    start: datetime | float
    end: datetime | float

    def __init__(self):
        self.start = None
        self.end = None

    @classmethod
    def print_header(cls):
        return ",".join(
            [
                "start",
                "total",
            ]
        )

    def to_list(self):
        return [
            self.start,
            self.end,
        ]

    def to_seconds(self):
        return [
            (self.start - self.start).total_seconds(),
            (self.end - self.start).total_seconds(),
        ]

    def __str__(self):
        return ",".join(
            map(
                str,
                [
                    self.start,
                    self.end,
                ],
            )
        )


def get_folders(path: Path):
    return [folder for folder in path.iterdir() if folder.is_dir()]


def get_execution_time(result_path: Path):
    execution_time = ExecutionTime()

    with sqlite3.connect(result_path / "result" / "data.db") as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM run_log")
        rows = cursor.fetchall()

        for row in rows:
            if row[-1].startswith("run created"):
                execution_time.start = datetime.fromisoformat(row[1])
            if row[-1].startswith("run finished"):
                execution_time.end = datetime.fromisoformat(row[1])

    return execution_time


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", type=Path)

    args = parser.parse_args()

    def collate_results(path):

        for folder in get_folders(path):
            # folder is samplesize_"replicate"_sample
            parts = folder.name.split("_")

            size, _replicate, sample = parts
            size = int(size)
            sample = int(sample)

            if len(parts) != 3:
                parts = ["unknown", "unknown", "unknown"]
            try:
                execution_time = get_execution_time(folder)
                # print(execution_time)

                results = [size, sample, *execution_time.to_seconds()]

                yield results
            except:
                print("Error in folder:" + str(folder))
                continue

    def sort_key(result):
        return result[0]

    print("size,sample," + ExecutionTime.print_header())

    for result in sorted(collate_results(args.path), key=sort_key):
        str_list = map(str, result)
        print(",".join(str_list))
