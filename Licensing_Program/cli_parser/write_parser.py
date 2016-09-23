"""Submodule for creating parser command 'write'.
"""


def add_command(subparser):
    """Add 'write' command to a subparser.
    """

    parser_write = subparser.add_parser(
        "write",
        help="write project license file and/or write headers to project files",
        description=("Write project license file and/or write headers to"
                     " project files."),
    )

    muex_parser_write = parser_write.add_mutually_exclusive_group()

    muex_parser_write.add_argument(
        "-l",
        "--license-only",
        action="store_true",
        help="only add license file to user project, don't write any headers",
    )
    muex_parser_write.add_argument(
        "-f",
        "--headers-only",
        metavar="FILE",
        nargs="*",
        help=("only write headers to project files or only to user specified"
              " files, don't write project license file"),
    )

    return subparser
