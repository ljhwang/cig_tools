"""Submodule for creating parser command 'license'.
"""

def add_command(subparser):
    """Add 'license' command to a subparser.
    """

    parser_license = subparser.add_parser(
        "license",
        help="list supported licenses or describe a given license",
        description=("List supported licenses or, if a license name is"
                     " provided, describe the specified license."),
    )
    parser_license.add_argument(
        "license",
        metavar="LICENSE",
        nargs="?",
        dest="license_name",
        help="list information about the given license",
    )

    return subparser
