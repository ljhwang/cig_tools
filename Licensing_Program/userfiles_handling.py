"""This file provides functionality for interacting with the user's project
files.
"""

import os
import itertools
import tempfile

import license_handling


HEADER_SIGNAL_STRING = "Copyright"
HEADER_IN_FIRST_N_LINES = 20


def _find_header_start_line(path):
    with open(path, "rt") as user_file:
        fileslice = itertools.islice(user_file, HEADER_IN_FIRST_N_LINES)
        for linenum, line in enumerate(fileslice):
            if HEADER_SIGNAL_STRING.casefold() in line.casefold():
                return linenum

    return None


def file_has_correct_header(path, args, config):
    """Return true if file designated by `path` has the correct header.
    """
    linenum = _find_header_start_line(path)

    if linenum is not None:
        with open(path, "rt") as user_file:
            file_slice = itertools.islice(user_file, linenum, None)

            formatted_text = license_handling.get_formatted_license(
                config["License"], config, path
            )

            header_lines = (
                x + "\n"
                for x in formatted_text["header"].splitlines()
            )

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


def write_header(header_text, user_filepath, insert_linenum=0, cut_lines=0):
    """Insert header into `user_filepath` starting at line `insert_linenum`
    (zero based). Removes `cut_lines` amount of lines after the header.
    `cut_lines` is useful for cases where existing header lines need to be
    removed.
    """
    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as outfile:
        with open(user_filepath, "rt") as user_file:
            for i, line in enumerate(user_file):
                if i == insert_linenum:
                    outfile.write(header_text)

                if i < insert_linenum or i >= insert_linenum + cut_lines:
                    outfile.write(line)

    os.replace(outfile.name, user_filepath)
