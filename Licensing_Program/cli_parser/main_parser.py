"""Module for creating main parser for software_dmv program.
"""

import argparse

import cli_parser.check_parser
import cli_parser.config_parser
import cli_parser.license_parser


def create_main_parser():
    """Creates main parser for the commandline interface.
    """

    parser = argparse.ArgumentParser(
        description="Where you go to get your software license.",
    )

    verbosity_group = parser.add_mutually_exclusive_group()

    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const="verbose",
        dest="verbosity",
        default="",
        help="output more information about executed command",
    )
    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const="quiet",
        dest="verbosity",
        default="",
        help="silence all non-error output",
    )

    command_parser = parser.add_subparsers(
        title="commands",
        dest="command",
    )
    command_parser.required = True

    command_parser = cli_parser.check_parser.add_command(command_parser)

    command_parser = cli_parser.config_parser.add_command(command_parser)

    command_parser = cli_parser.license_parser.add_command(command_parser)

    return parser
