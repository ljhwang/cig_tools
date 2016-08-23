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


def get_formatted_license(license_name, config, user_filepath):
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
