"""This file provides functionality for using the license repository included
 in the software_dmv project.
"""

import json
import os
import re

import licenses

LICENSE_DIR = "Licenses"

DEFAULT_LICENSE = "generic"

LICENSE_EXT = ".txt"
LICENSE_HEADER_SUFFIX = "_header"


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


def format_header(header, path, config):
    """Headers use double curly braces to describe required inputs.
    Inside a set of curly braces is the name of the input.
    """
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_-]+)\s*}}")
    match = pattern.search(header)
    formatted_header = ""

    while match:
        begin, end = match.span()
        input_name = match.groups()

        formatted_header += (
            match.string[:begin]
            + str(config["LicenseParameters"][input_name])
        )

        match = pattern.search(match.string[end:])

    formatted_header += match.string[end:]

    return formatted_header
