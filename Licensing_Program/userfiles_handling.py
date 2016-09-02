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
    """Find line number of line that holds the token string that signals the
    start of the license header.
    """
    with open(path, "rt") as ro_file:
        fileslice = itertools.islice(ro_file, HEADER_IN_FIRST_N_LINES)
        for linenum, line in enumerate(fileslice):
            if HEADER_SIGNAL_STRING.casefold() in line.casefold():
                return linenum

    return None


def file_has_correct_header(user_filepath, args, config):
    """Return true if file designated by `path` has the correct header.
    """
    linenum = _find_header_start_line(user_filepath)

    if linenum is not None:
        with open(user_filepath, "rt") as user_file:
            header_text = license_handling.fill_in_license(
                config["License"], config,
            )["header_text"]

            header_text = license_handling.comment_out_header(
                header_text, user_filepath, config,
            )

            header_lines = header_text.splitlines(keepends=True)

            user_file_lines = [
                line
                for line in itertools.islice(
                    user_file,
                    linenum,
                    linenum + len(header_lines),
                )
            ]

            mismatched_lines = _compare_header_lines(
                header_lines, user_file_lines
            )

            if args.info_level == "verbose" and mismatched_lines:
                print(
                    ("In file {}: there are {} lines that do not match the"
                     " expected license header.").format(user_filepath,
                                                         mismatched_lines)
                )

            return not bool(mismatched_lines)

    else:
        if args.info_level == "verbose":
            print(
                "File {} does not appear to have a license header.".format(
                    user_filepath)
            )

        return False


def write_header(header_text, user_filepath, insert_linenum=0, cut_lines=0):
    """Insert header into `user_filepath` starting at line `insert_linenum`
    (zero based). Removes `cut_lines` amount of lines after the header.
    `cut_lines` is useful for cases where existing header lines need to be
    removed.
    """
    if insert_linenum > HEADER_IN_FIRST_N_LINES:
        raise ValueError(
            (
                "Header should not be written at line {}. It should be placed"
                " near the top of the file."
            ).format(insert_linenum)
        )

    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as outfile:
        with open(user_filepath, "rt") as user_file:
            for i, line in enumerate(user_file):
                if i == insert_linenum:
                    outfile.write(header_text)

                if i < insert_linenum or i >= insert_linenum + cut_lines:
                    outfile.write(line)

    os.replace(outfile.name, user_filepath)
