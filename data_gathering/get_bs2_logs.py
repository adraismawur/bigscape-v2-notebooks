# generated with copilot

# - get all folders at a certain path
# for each folder:
# - get files withing folder with .profile*
# - get files ending in .log but not .config.log

from pathlib import Path
from argparse import ArgumentParser
import shutil


def get_folders(path: Path):
    return [folder for folder in path.iterdir() if folder.is_dir()]


def get_files(folder: Path):
    yield from filter(
        lambda file: file.suffix == ".png" or file.suffix == ".profile",
        folder.iterdir(),
    )
    # log but no .config.log
    yield from filter(
        lambda file: file.suffix == ".log" and not file.stem.endswith(".config"),
        folder.iterdir(),
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", type=Path)
    # output
    parser.add_argument("output", type=Path)
    parser.add_argument("-c", "--copy", action="store_true")
    args = parser.parse_args()

    for folder in get_folders(args.path):
        folder_name = folder.name
        for file in get_files(folder):
            print(f"{file} -> {args.output / folder_name / file.name}")
            if args.copy:
                (args.output / folder_name).mkdir(parents=True, exist_ok=True)
                # copy file
                shutil.copy(file, args.output / folder_name / file.name)
