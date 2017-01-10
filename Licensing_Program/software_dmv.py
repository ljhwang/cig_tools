#! /usr/bin/env python3


import utils.load_config as utils

import cli_parser.main_parser as main_parser

import program_commands.check_command as check_command
import program_commands.config_command as config_command
import program_commands.license_command as license_command
import program_commands.write_command as write_command

def main(args):
    """Program entrypoint.
    Calls requested CLI command.
    """

    if args.command == "license":
        license_command.main(args, None)
    else:
        config = utils.load_config(".")
        if args.command == "check" or args.command == "check-project":
            check_command.main(args, config)
        elif args.command == "config":
            config_command.main(args)
        elif args.command == "write":
            write_command.main(args, config)


if __name__ == "__main__":
    main(main_parser.create_main_parser().parse_args())

