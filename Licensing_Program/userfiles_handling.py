"""This file provides functionality for interacting with the user's project
files.
"""

import os
import itertools
import tempfile

import license_handling


HEADER_IN_FIRST_N_LINES = 20


def _find_header_start_line(path):
    with open(path, "rt") as user_file:
        fileslice = itertools.islice(user_file, HEADER_IN_FIRST_N_LINES)
        for linenum, line in enumerate(fileslice):
            if "Copyright".casefold() in line.casefold():
                return linenum

    return None


def file_has_correct_header(path, args, config):
    license_info = license_handling.get_license_info(config)

    linenum = _find_header_start_line(path)

    if linenum is not None:
        with open(path, "rt") as user_file:
            file_slice = itertools.islice(user_file, linenum, None)

            header = license_handling.format_header(
                license_info["Header"], path, config)
            header_lines = (x + "\n" for x in header.splitlines())

            nonmatching_lines = [
                (header_line, file_line)
                for header_line, file_line
                in zip(header_lines, file_slice)
                if header_line != file_line
            ]

            if args.info_level == "verbose" and nonmatching_lines:
                print(
                    ("In file {}: there are {} lines that do not match the"
                     " expected license header.").format(path,
                                                         len(nonmatching_lines))
                )

            return not bool(nonmatching_lines)

    else:
        if args.info_level == "verbose":
            print(
                "File {} does not appear to have a license header.".format(path)
            )

        return False


def insert_header(user_filepath, header, linenum=0):
    """Inserts header text into file at `user_filepath` starting at line
    `linenum`.
    """
    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as outfile:
        with open(user_filepath, "rt") as user_file:
            for i, line in enumerate(user_file):
                if i == linenum:
                    outfile.write(header)

                outfile.write(line)

    os.replace(outfile.name, user_filepath)


def replace_header(user_filepath, header, linenum=0):
    """Overwrites lines in file at `user_filepath` with header text starting at
    line `linenum`.
    """
    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as outfile:
        with open(user_filepath, "rt") as user_file:
            skip_lines = -1

            for i, line in enumerate(user_file):
                if i == linenum:
                    outfile.write(header)
                    skip_lines = len(header.splitlines()) + i

                if i > skip_lines:
                    outfile.write(line)

    os.replace(outfile.name, user_filepath)
