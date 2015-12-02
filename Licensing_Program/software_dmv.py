import argparse
import json

try:
    import jsonschema
except ImportError:
    jsonschema = None


def load_config(cfg_fd):
    dirty_input = json.load(cfg_fd)

    blockComments_schema = {
        "type": "object",
        "properties": {
            "BlockComments": {
                "type": "object",
                "properties": {
                    "BlockStart": {"type": "string", },
                    "BlockLine": {"type": "string", },
                    "BlockEnd": {"type": "string", },
                },
                "required": ["BlockStart", "BlockEnd", ],
            },
        },
        "required": ["BlockComments", ],
    }

    lineComments_schema = {
        "type": "object",
        "properties": {
            "LineCommentStart": {"type": "string", },
        },
        "required": ["LineCommentStart", ],
    }

    config_schema = {
        "type": "object",
        "properties": {
            "License": {
                "type": "string",
            },
            "LicenseParameters": {
                "type": "object",
                "patternProperties": {
                    "^[a-zA-Z0-9_-]+$": {},
                },
                "additionalProperties": False,
            },
            "CommentedFiles": {
                "type": "object",
                "patternProperties": {
                    "^.+$": {
                        "oneOf": [blockComments_schema, lineComments_schema, ],
                    },
                },
                "additionalProperties": False,
            },
            "IgnoredFiles": {
                "type": "array",
                "items": {"type": "string", },
            },
        },
    }

    if jsonschema:
        #TODO: Errors
        return jsonschema.validate(dirty_input, config_schema)
    else:
        return dirty_input


def create_main_parser():
    parser = argparse.ArgumentParser(
        description="Where you go to get your software license.",
    )
    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command",
    )

    parser_check = subparsers.add_parser(
        "check",
        help="Check all project files for licensing information",
        description="Check all project files for licensing information.",
    )
    parser_check.add_argument(
        "--no-ignore",
        action="store_true",
        help="Also check files that are set to be ignored",
    )
    parser_check.add_argument(
        "-a",
        "--add-missing",
        action="store_true",
        help="Add project license to files that fail the check",
    )
    parser_check.add_argument(
        "-f",
        "--files",
        nargs="+",
        help="Check these files only",
    )

    parser_choose = subparsers.add_parser(
        "choose",
        help="Choose a license to insert into your project",
        description="Choose a license to insert into your project.",
    )

    verbosity_group = parser_choose.add_mutually_exclusive_group()

    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Output more information about executed command",
    )
    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Silence all non-error output",
    )

    parser_choose.add_argument(
        "-p",
        "--parameter",
        help=("Set a license parameter. Input is in key:value form and"
              " multiple parameters can be set by using multiple flags or by"
              " concatenating key-value pairs with commas. e.g. '--parameter="
              "project:foo,author:bar'.")
    )

    parser_list = subparsers.add_parser(
        "list",
        help="List supported licenses",
        description="List supported licenses.",
    )

    parser_info = subparsers.add_parser(
        "info",
        help="Show summary of license and necessary user parameters",
        description="Show summary of license and necessary user parameters.",
    )
    parser_info.add_argument(
        "LICENSE",
        help="License name",
    )
    parser_info.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show full license text instead of summary",
    )

    parser_settings = subparsers.add_parser(
        "settings",
        help="Show current license settings for your project",
        description="Show current license settings for your project.",
    )

    return parser


def main(args):
    pass


if __name__ == "__main__":
    main(create_main_parser().parse_args())
