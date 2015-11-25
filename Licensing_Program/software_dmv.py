import argparse
import json


def create_main_parser():
    parser = argparse.ArgumentParser(
        description="Where you go to get your software license.",
    )
    subparsers = parser.add_subparsers(
        title="Commands",
    )

    parser_check = subparsers.add_parser(
        "check",
        help="Check all project files for licensing information.",
        description="Check all project files for licensing information.",
    )
    parser_check.add_argument(
        "--no-ignore",
        action="store_true",
        help="Also check files that are set to be ignored.",
    )
    parser_check.add_argument(
        "-a",
        "--add-missing",
        action="store_true",
        help="Add project license to files that fail the check.",
    )
    parser_check.add_argument(
        "-f",
        "--files",
        nargs="+",
        help="Check these files only.",
    )

    parser_choose = subparsers.add_parser(
        "choose",
        help="Choose a license to insert into your project.",
        description="Choose a license to insert into your project.",
    )

    info_group = parser_choose.add_mutually_exclusive_group()

    info_group.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List supported licenses.",
    )
    info_group.add_argument(
        "-i",
        "--info",
        metavar="LICENSE",
        help=("Show summary of license and necessary user parameters. This flag"
              " can be combined with the verbose flag to show the complete"
              " license text."),
    )

    verbosity_group = parser_choose.add_mutually_exclusive_group()

    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Output more information about executed command.",
    )
    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Silence all non-error output.",
    )

    parser_show = subparsers.add_parser(
        "show",
        help="Show current license settings for your project.",
        description="Show current license settings for your project.",
    )

    return parser


def main(args):
    pass


if __name__ == "__main__":
    main(create_main_parser().parse_args())
