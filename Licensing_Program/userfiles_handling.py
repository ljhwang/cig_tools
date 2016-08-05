"""This file provides functionality for interacting with the user's project
files.
"""

import license_handling


def check_file(path, args, config):
    license_info = license_handling.get_license_info(config)

    with open(path, "rt") as file:
        # The copyright header should be in the first 20 lines
        fileslice = itertools.islice(file, 20)
        for linenum, line in enumerate(fileslice):
            if "Copyright".casefold() in line.casefold():
                break
        else:
            if args.info_level == "verbose":
                print(
                    "File {} does not appear to have a license header.".format(
                        file.name)
                )

            return False

        header = format_header(license_info["Header"], path, config)
        header_lines = (x + "\n" for x in header.splitlines())

        # pylint: disable=undefined-loop-variable
        nonmatching_lines = [
            (header_line, file_line)
            for header_line, file_line
            in zip(header_lines, itertools.chain([line], file))
            if header_line != file_line
        ]

        if args.info_level == "verbose" and nonmatching_lines:
            print(
                ("In file {}: there are {} lines that do not match the"
                 " expected license header.").format(file.name,
                                                     len(nonmatching_lines))
            )

        return not bool(nonmatching_lines)
