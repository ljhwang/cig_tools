"""Submodule for creating parser command 'check-project'.
"""

def add_command(subparser):
    """Add 'check-project' command to a subparser.
    """

    parser_check = subparser.add_parser(
        "check-project",
        aliases=["check"],
        help="check all project files for licensing information",
        description="Check all project files for licensing information.",
    )
    parser_check.add_argument(
        "--no-ignore",
        action="store_true",
        help="also check files that are set to be ignored",
    )
    parser_check.add_argument(
        "-a",
        "--add-missing",
        action="store_true",
        help="add project license to files that fail the check",
    )
    parser_check.add_argument(
        "-f",
        "--files",
        metavar="FILE",
        nargs="+",
        help="check these files only",
    )

    return subparser
