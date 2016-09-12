"""This file provides functionality for using the license repository included
 in the software_dmv project.
"""

import re
import string

import licenses
import config_handling

DEFAULT_LICENSE = "generic"


def get_license_list():
    """Return a sorted list of supported license names.
    """
    return sorted(licenses.license_dict.keys())


def get_license_parameters_list(license_name):
    """Return a list of parameter names required for the license text.
    """
    return [
        name
        for _, name, _, _ in string.Formatter().parse(
            licenses.license_dict[license_name].license)
        if name is not None
    ] + [
        name
        for _, name, _, _ in string.Formatter().parse(
            licenses.license_dict[license_name].header)
        if name is not None
    ]


def fill_in_license(license_name, config):
    """Return a dictionary containing the formatted text of the license and
    header.
    """
    user_license = licenses.license_dict[license_name]

    license_text = user_license.license.format(**config["LicenseParameters"])
    header_text = user_license.header.format(**config["LicenseParameters"])

    return {
        "license_text" : license_text,
        "header_text" : header_text,
    }


def comment_out_header(header_text, user_filepath, config):
    """Add user's commenting syntax to each line of the header's text.
    Commenting syntax is chosen by `user_filepath` matching a configured regex.
    Comment tokens added to empty lines will be stripped of trailing whitespace.
    """
    header_lines = header_text.splitlines(keepends=True)

    if "CommentedFiles" in config:
        matched_comment_formats = [
            regex
            for regex in config["CommentedFiles"]
            if re.match(
                config_handling.param_ignoredfiles_to_regex(regex),
                user_filepath
            )
        ]

        if len(matched_comment_formats) > 1:
            print((
                "WARNING: {} matches more than one commenting format. Using"
                " first match."
            ).format(user_filepath))
            print("  List of matches:")
            for filepattern in matched_comment_formats:
                print("    " + filepattern)

        if matched_comment_formats:
            comment_format = (
                config["CommentedFiles"][matched_comment_formats[0]]
            )

            if "BlockComments" in comment_format:
                block_format = comment_format["BlockComments"]

                header_lines = [
                    block_format["BlockStart"] + header_lines[0]
                ] + [
                    block_format.get("BlockLine", "") + line
                    if not line.isspace()
                    else block_format.get("BlockLine", "").rstrip() + line
                    for line in header_lines[1:]
                ] + [
                    block_format["BlockEnd"] + "\n"
                ]

            else:  # elif "LineCommentStart" in comment_format:
                header_lines = [
                    comment_format["LineCommentStart"] + line
                    if not line.isspace()
                    else comment_format["LineCommentStart"].rstrip() + line
                    for line in header_lines
                ]

    if matched_comment_formats:
        comment_format = config["CommentedFiles"][matched_comment_formats[0]]
    else:
        comment_format = None

    header_text = "".join(header_lines)
    return header_text, comment_format
