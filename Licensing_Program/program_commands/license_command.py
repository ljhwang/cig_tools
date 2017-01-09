"""Submodule for 'license' command functionality.
"""

import licenses


def main(args, config):
    """CLI program command: list
    Output each supported license by name.
    """
    for license_name in get_license_list():
        print(license_name)


def get_license_list():
    """Return a sorted list of supported license names.
    """
    return sorted(licenses.license_dict.keys())

