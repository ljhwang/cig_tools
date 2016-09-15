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
# TODO: figure out config features/options

    return subparser
