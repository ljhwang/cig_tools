"""Submodule for 'config' command functionality.
"""

import json

import config_handling


def main(args):
    """'config' command entrypoint.
    """
    if args.print_default:
      config_handling.write_default_configfile()
    elif args.verify_config:
      try:
          config_handling.load_configfile()
          print("No errors detected")
      except json.decoder.JSONDecodeError as error:
          print(error)
