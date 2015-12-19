#! /usr/bin/env python3

import argparse
import functools
import glob
import json
import itertools
import operator
import os
import pprint
import re

try:
    import jsonschema
except ImportError:
    jsonschema = None


_config_schema_file = "Licensing_Program/config_schema.json"
_config_file = "testConfig.json"
_license_dir = "Licenses/"
_generic_headerfile = "Licensing_Program/Licenses/generic_header.txt"

default_config = {}


# antpatterns: https://ant.apache.org/manual/dirtasks.html#patterns
def antpattern_to_regex(pattern):
    return "^(" + re.sub(
        r"\*\*+",
        r"[^/]*",  # get rid of mis-used double asterisks
        re.sub(
            r"((?<=/)|(?<=^))\*\*/?",
            r".*?",  # the directory name is '**', not 'tmp**/' etc.
            re.sub(
                r"(?<!\*)\*(?!\*)",
                r"[^/]*",  # ant '*' doesn't leave cwd
                re.sub(
                    r"\?",
                    r".",  # Convert ant '?' to re '.'
                    re.sub(
                        r"([.+^$|{}()\[\]])",
                        r"\\\1",  # Escape other regex symbols
                        pattern,
                    )
                )
            )
        )
    ) + ")$"


def get_config(args):
    config = json.load(open(_config_file, "rt"))

    # TODO: Errors
    if jsonschema:
        config_schema = json.load(open(_config_schema_file, "rt"))
        jsonschema.validate(config, config_schema)
    elif hasattr(args, "info_level") and args.info_level == "verbose":
        print("\nWARNING: The module 'jsonschema' is not available. The"
              " configuration file cannot be verified for correctness.\n")

    default_config.update(config)
    return default_config


def get_license_info(license_name):
    license_txtfile = open(
        os.path.join(_license_dir, license_name + ".txt"),
        "rt",
    )
    license_json = json.load(
        open(
            os.path.join(_license_dir, license_name + ".json"),
            "rt",
        )
    )

    try:
        header_txtfile = open(
            os.path.join(_license_dir, license_name + "_header.txt"),
            "rt",
        )
    except FileNotFoundError:
        header_txtfile = open(
            os.path.join(_license_dir, _generic_headerfile),
            "rt",
        )

    license_json["fullText"] = str(license_txtfile)
    license_json["headerText"] = str(header_txtfile)

    return license_json


def check_file(path, args, config):
    license_info = get_license_info(config)

    with open(path, "rt") as file:
        # The copyright header should be in the first 20 lines
        fileslice = itertools.islice(file, 20)
        for linenum, line in enumerate(fileslice):
            if "Copyright".casefold() in line.casefold():
                break
        else:
            return False

        header = format_header(license_info["Header"], path, config)
        # re.split keeps strings captured by regex groups
        header_lines = (x for x in re.split(r"(.*?\n)", header) if x)

        nonmatching_lines = filter(
            lambda x: operator.ne(*x),
            zip(
                header_lines,
                itertools.chain([line], file)
            )
        )

        if args.info_level == "verbose" and nonmatching_lines:
            print(
                ("In file {}: there are {} lines that do not match the"
                 " expected license header.").format(file.name,
                                                     len(nonmatching_lines))
            )

        return not bool(nonmatching_lines)


def main_check(args, config):
    if args.files:
        filepaths = set(args.files)
    else:
        filepaths = functools.reduce(
            itertools.chain,
            (map(functools.partial(os.path.join, cwd), files)
                for cwd, dirs, files in os.walk(".")),
            [],
        )

    if not args.no_ignore and config["IgnoredFiles"]:
        def ignore_to_regex(s):
            if s.startswith("re:"):
                return s.lstrip("re:")
            elif s.startswith("ant:"):
                return antpattern_to_regex(s.lstrip("ant:"))
            else:
                return antpattern_to_regex(s)

        ignore_regex = functools.reduce(
            lambda x,y: x + "|" + y,
            map(ignore_to_regex, config["IgnoredFiles"])
        )

        filepaths = filter(
            lambda x: not re.match(ignore_regex, x),
            filepaths,
        )

    for path in filepaths:
        print(path)
        #check_file(path, args, config)


def main_list(args, config):
    def get_license_name(path):
        return os.path.basename(os.path.splitext(path)[0])

    for name in sorted(set(map(get_license_name,
                               glob.iglob(_license_dir + "*")))):
        print(name)


#def main_info(args):
#    license = json.load(_license_dir + args.license)
#
#    license["name"]


def main_settings(args, config):
    if args.info_level != "verbose":
        pprint.pprint(config, depth=2)
    else:
        def dict_doc_print(d, doc, acc=""):
            indent = "  "

            if hasattr(d, "items"):
                for k, v in sorted(d.items()):
                    if doc.get(k):
                        print("\n" + acc + "# " + str(doc.get(k)))
                    print(acc + str(k) + ":")

                    if hasattr(v, "items"):
                        dict_doc_print(v, doc, acc + indent)
                    elif hasattr(v, "__iter__") and v != str(v):
                        for x in v:
                            print(acc + indent + str(x))
                    else:
                        print(acc + indent + str(v))

        config_doc = {
            "License": ("The license that will be used to generate the LICENSE"
                        " file"),
            "LicenseParameters": ("Necessary user input to be inserted into"
                                  " the license"),
        }

        dict_doc_print(config, config_doc)


def create_main_parser():
    parser = argparse.ArgumentParser(
        description="Where you go to get your software license.",
    )
    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command",
    )
    subparsers.required = True

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
        metavar="FILE",
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
        action="store_const",
        const="verbose",
        dest="info_level",
        default="",
        help="Output more information about executed command",
    )
    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const="quiet",
        dest="info_level",
        default="",
        help="Silence all non-error output",
    )

    parser_choose.add_argument(
        "-p",
        "--parameter",
        action="append",
        help=("Set a license parameter. Input is in key:value form and"
              " multiple parameters can be set by using multiple flags or by"
              " concatenating key-value pairs with commas. e.g. '--parameter="
              "project:foo,author:bar'."),
    )
    parser_choose.add_argument(
        "license",
        metavar="LICENSE",
        help=("License to be created for your project. Use the 'list' command"
              " to see all supported licenses."),
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
        "license",
        metavar="LICENSE",
        help="License name",
    )
    parser_info.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const="verbose",
        dest="info_level",
        default="",
        help="Show full license text instead of summary",
    )

    parser_settings = subparsers.add_parser(
        "settings",
        help="Show current license settings for your project",
        description="Show current license settings for your project.",
    )
    parser_settings.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const="verbose",
        dest="info_level",
        default="",
        help="Show all settings and their documentation",
    )

    return parser


def main(args):
    config = get_config(args)

    if args.command == "check":
        pass
    elif args.command == "choose":
        pass
    elif args.command == "list":
        main_list(args, config)
#    elif args.command == "info":
#        main_info(args)
    elif args.command == "settings":
        main_settings(args, config)


if __name__ == "__main__":
    main(create_main_parser().parse_args())
