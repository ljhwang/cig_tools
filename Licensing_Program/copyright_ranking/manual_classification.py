#! /usr/bin/env python3

import csv
import itertools
import os
import pathlib

CONFIG = {
    "ProjectDir" : pathlib.Path("specfem3d").absolute(),
    "OutputFile" : "specfem3d_file_licenses.csv",
    "PreviewLines" : 32,
    "ANSIColors" : True,
}


def project_path_gen(project_dir):
    """Generate absolute paths in project_dir of non-ignored files.
    """
    for cwd, dirs, files in os.walk(str(project_dir)):
        def _sortkey(name):
            return pathlib.Path(name).suffix

        files.sort(key=_sortkey)

        for dirname in list(dirs):
            if dirname.startswith(os.extsep):
                dirs.remove(dirname)

        for filename in files:
            if not filename.startswith(os.extsep):
                filepath = pathlib.Path(os.path.join(cwd, filename)).absolute()
                try:
                    with filepath.open("rt") as userfile:
                        userfile.read()
                except UnicodeDecodeError:
                    pass
                else:
                    yield filepath


def _islice_groups(iterable, glength):
    iterable, iter_copy = itertools.tee(iterable)
    count = 0
    group = list(itertools.islice(iter_copy, glength))

    while group:
        yield group
        count += glength
        iterable, iter_copy = itertools.tee(iterable)
        group = list(
            itertools.islice(iter_copy, count, count + glength)
        )


def get_manual_license_classification(filepath):
    with filepath.open("rt") as file:
        for lines in _islice_groups(file, CONFIG["PreviewLines"]):
            print()
            for line in lines:
                print(line, end="")

            if len(lines) < CONFIG["PreviewLines"]:
                break

            response = input(
                ("\x1b[33m" if CONFIG["ANSIColors"] else "")
                + "\n<><><><><><><><><><><><><><><><><>"
                + "\n<license>/(c)ontinue/(n)one/(q)uit"
                + "\n "
                + ("\x1b[0m" if CONFIG["ANSIColors"] else "")
            )

            if response == "c" or response == "":
                pass
            elif response == "n":
                return None
            elif response == "q":
                exit()
            else:
                # TODO: check against possible license names
                return response


        print(
            ("\x1b[31;1m" if CONFIG["ANSIColors"] else "")
            + "\n <> EOF <>"
            + ("\x1b[0m" if CONFIG["ANSIColors"] else "")
        )

        response = input(
            ("\x1b[33m" if CONFIG["ANSIColors"] else "")
            + "\n<><><><><><><><><><><><"
            + "\n<license>/(n)one/(q)uit"
            + "\n "
            + ("\x1b[0m" if CONFIG["ANSIColors"] else "")
        )

        if response == "n":
            return None
        elif response == "q":
            exit()
        else:
            # TODO: check against possible license names
            return response


if __name__ == "__main__":
    completed_files_set = set()

    try:
        with open(CONFIG["OutputFile"], "rt") as output_file:
            completed_files_set = {
                row["userfile_path"] for row in csv.DictReader(output_file)
            }

    except FileNotFoundError:
        with open(CONFIG["OutputFile"], "at") as output_file:
            csv.DictWriter(
                output_file,
                ["userfile_path", "license_name"],
            ).writeheader()

    with open(CONFIG["OutputFile"], "at") as output_file:
        writer = csv.DictWriter(
            output_file,
            ["userfile_path", "license_name"],
        )

        for userfile_path in project_path_gen(CONFIG["ProjectDir"]):
            filepath = str(userfile_path.relative_to(CONFIG["ProjectDir"]))

            if filepath not in completed_files_set:
                license = get_manual_license_classification(userfile_path)
                writer.writerow({
                    "userfile_path": filepath,
                    "license_name": license if license else "NOLICENSE",
                })
