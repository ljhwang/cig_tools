"""Submodule for creating parser command 'config'.
"""

def add_command(subparser):
    """Add 'config' command to a subparser.
    """

    parser_config = subparser.add_parser(
        "config",
        help="create or validate a configuration file for a software project",
        description=("Create or validate a configuration file for a software"
                     " project."),
    )
    parser_config.add_argument(
        "-d",
        "--print-default",
        action="store_true",
        help="output a standard config json string",
    )
    parser_config.add_argument(
        "-c",
        "--verify-config",
        action="store_true",
        help="check that config file is syntactically correct",
    )

    return subparser
