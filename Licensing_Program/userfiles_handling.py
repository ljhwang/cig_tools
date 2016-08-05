"""This file provides functionality for interacting with the user's project
files.
"""

import itertools

import license_handling


HEADER_IN_FIRST_N_LINES = 20


def _find_header_start_line(path):
    with open(path, "rt") as source_file:
        fileslice = itertools.islice(source_file, HEADER_IN_FIRST_N_LINES)
        for linenum, line in enumerate(fileslice):
            if "Copyright".casefold() in line.casefold():
                return linenum

    return None


def file_has_correct_header(path, args, config):
    license_info = license_handling.get_license_info(config)

    linenum = _find_header_start_line(path)

    if linenum is not None:
        with open(path, "rt") as source_file:
            source_file = itertools.islice(source_file, linenum, None)

            header = license_handling.format_header(
                license_info["Header"], path, config)
            header_lines = (x + "\n" for x in header.splitlines())

            nonmatching_lines = [
                (header_line, file_line)
                for header_line, file_line
                in zip(header_lines, source_file)
                if header_line != file_line
            ]

            if args.info_level == "verbose" and nonmatching_lines:
                print(
                    ("In file {}: there are {} lines that do not match the"
                     " expected license header.").format(file.name,
                                                         len(nonmatching_lines))
                )

            return not bool(nonmatching_lines)

    else:
        if args.info_level == "verbose":
            print(
                "File {} does not appear to have a license header.".format(path)
            )

        return False
