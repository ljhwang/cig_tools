"""This file provides functionality for getting and parsing a project's
configuration.
"""

import json
import os.path
import re
import sys

try:
    import jsonschema
except ImportError:
    jsonschema = None


CONFIG_FILENAME = ".licensing.json"

CONFIG_SCHEMA = {
    "properties": {
        "CommentedFiles": {
            "additionalProperties": False,
            "patternProperties": {
                "^.+$": {
                    "insertAtLine": {
                        "maximum": HEADER_IN_FIRST_N_LINES,
                        "type": "integer",
                    },
                    "oneOf": [
                        {
                            "properties": {
                                "BlockComments": {
                                    "properties": {
                                        "BlockEnd": {
                                            "type": "string"
                                        },
                                        "BlockLine": {
                                            "type": "string"
                                        },
                                        "BlockStart": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [
                                        "BlockStart",
                                        "BlockEnd"
                                    ],
                                    "type": "object"
                                }
                            },
                            "required": [
                                "BlockComments"
                            ],
                            "type": "object"
                        },
                        {
                            "properties": {
                                "LineCommentStart": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "LineCommentStart"
                            ],
                            "type": "object"
                        }
                    ]
                }
            },
            "type": "object"
        },
        "IgnoredFiles": {
            "items": {
                "type": "string"
            },
            "type": "array"
        },
        "License": {
            "type": "string"
        },
        "LicenseParameters": {
            "additionalProperties": False,
            "patternProperties": {
                "^[a-zA-Z0-9_-]+$": {}
            },
            "type": "object"
        }
    },
    "required": [
        "License"
    ],
    "type": "object"
}

CONFIG_DEFAULT = {

}


# antpatterns: https://ant.apache.org/manual/dirtasks.html#patterns
def antpattern_to_regex(pattern):
    """Convert an Apache antpattern to a python regex string. Assumes POSIX
    path separator ('/').
    """
    # Escape other regex symbols
    pattern = re.sub(
        r"([.+^$|{}()\[\]])",
        r"\\\1",
        pattern,
    )

    # Convert ant '?' to re '.'
    pattern = re.sub(
        r"\?",
        r".",
        pattern,
    )

    # ant '*' doesn't leave cwd
    pattern = re.sub(
        r"([^*]|^)\*([^*]|$)",
        r"\1[^/]*\2",
        pattern,
    )

    # the name for the directory wildcard is '**' with no additional chars.
    pattern = re.sub(
        r"(/|^)\*\*+(/|$)",
        r"\1.*?\2",
        pattern,
    )

    # replace misused double asterisks with single asterisk
    # TODO: maybe show a warning/error for this
    pattern = re.sub(
        r"\*\*+",
        r"[^/]*",
        pattern,
    )

    return "^(" + pattern + ")$"


def param_ignoredfiles_to_regex(ignore_string):
    """Takes a config IgnoredFiles item and converts it into a regex string.
    """
    if ignore_string.startswith("re:"):
        return ignore_string.lstrip("re:")
    elif ignore_string.startswith("ant:"):
        return antpattern_to_regex(ignore_string.lstrip("ant:"))
    else:
        return antpattern_to_regex(ignore_string)


def load_project_config(cwd=".", info_level=""):
    """Parses the project config file in 'cwd'. If the 'jsonschema' module is
    available, the config file is checked for data errors.
    """
    project_config = json.load(open(os.path.join(cwd, CONFIG_FILENAME), "rt"))

    if jsonschema:
        jsonschema.validate(project_config, CONFIG_SCHEMA)
    elif info_level == "verbose":
        print(
            "\nWARNING: 'jsonschema' module could not be found. User"
            " configuration will not be checked for errors.",
            file=sys.stderr,
        )

    return project_config
