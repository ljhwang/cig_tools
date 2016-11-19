"""Module for reading and validating project config file.
"""

import pathlib

import ruamel.yaml
from voluptuous import All, Any, Length, Optional, Range, Required, Schema

CONFIG_FILEPATH = ".licensing.yaml"
INSERTAT_MAX = 20
CONFIG_SCHEMA = Schema({
    Optional("ignore"): [str],
    Required("license"): str,
    Required("license-parameters"): {str: str},
    Required("track"): [{
        Optional("insert-at", default=1): All(
            int, Range(min=1, max=INSERTAT_MAX)
        ),
        Required("patterns"): Any(str, [str]),
        Optional("prefixes", default=[]): Any(str, All([str], Length(max=3))),
    }],
})


def _apply_func_to_keyset(func, keyset, dictionary):
    """Returns new dictionary with `func` applied to all values whose keys are
    in `keyset`.
    """
    return dict(
        (key, func(value)) if key in keyset else (key, value)
        for key, value in dictionary
    )


def _string_to_singleton_list(value):
    return [value] if isinstance(str, value) else value


def validate_config_stream(stream):
    """Validate configuration string stream."""
    valid_config = CONFIG_SCHEMA(ruamel.yaml.safe_load(stream))

    valid_config['track'] = [
        _apply_func_to_keyset(
            _string_to_singleton_list,
            {'patterns', 'prefixes'},
            tracked_item,
        )
        for tracked_item
        in valid_config['track']
    ]

    return valid_config


def load_config(proj_dir):
    """Looks for user-defined config in `proj_dir` and returns a validated
    config object or `None` if no config is found.
    """
    try:
        with pathlib.Path(proj_dir, CONFIG_FILEPATH).open("rt") as config_file:
            return validate_config_stream(config_file)
    except FileNotFoundError:
        return None
