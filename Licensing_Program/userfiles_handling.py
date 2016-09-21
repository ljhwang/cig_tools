"""This file provides functionality for interacting with the user's project
files.
"""

import os
import itertools
import re
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


def _compare_header_lines(correct_lines, test_lines):
    """Return a list of `test_lines` that do not match `correct_lines` at the
    same index.
    """
    return [
        t_line
        for c_line, t_line in zip(correct_lines, test_lines)
        if c_line != t_line
    ]


def file_has_correct_header(user_filepath, args, config):
    """Return true if file designated by `path` has the correct header.
    """
    try:
        linenum = _find_header_start_line(user_filepath)
    except UnicodeDecodeError:
        if args.info_level == "verbose":
            print(
                "File {} is not standard utf-8. It may be a binary.".format(
                    user_filepath
                )
            )

        return False

    if linenum is not None:
        with open(user_filepath, "rt") as user_file:
            header_text = license_handling.fill_in_license(
                config["License"], config,
            )["header_text"]

            header_text, comment_format = license_handling.comment_out_header(
                header_text, user_filepath, args, config,
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

    try:
        with open(user_filepath, "rt") as user_file:
            with tempfile.NamedTemporaryFile(
                mode="wt",
                delete=False) as outfile:
                for i, line in enumerate(user_file):
                    if i == insert_linenum:
                        outfile.write(header_text)

                    if i < insert_linenum or i >= insert_linenum + cut_lines:
                        outfile.write(line)

        os.replace(outfile.name, user_filepath)
    except UnicodeDecodeError:
        print((
            "WARNING: File {} is not standard unicode and has been skipped. It"
            " may be a binary."
        ).format(user_filepath))


def commentformat_userfile_pairing(userproject_dir, config):
    """Returns an iterator of tuples of comment patterns and file paths.
    """
    userfile_iter = iter(
        os.path.relpath(os.path.join(cwd, file))
        for cwd, dirs, files in os.walk(userproject_dir)
        for file in files
    )

    ignoredfiles_filter_iter = iter(
        userfile_path
        for userfile_path in userfile_iter
        if not any(
            re.match(ignore_pattern, userfile_path)
            for ignore_pattern in config["IgnoredFiles"]
        )
    )

    pairing_iter = iter(
        tuple(
            next(
                comment_pattern
                for comment_pattern in config["CommentedFiles"]
                if re.match(comment_pattern, userfile_path),
                None
            ),
            userfile_path
        )
        for userfile_path in ignoredfiles_filter_iter
    )

    return pairing_iter
