
import re


def filepattern_to_regex(pattern):
    """Convert config filepattern to filepath regex. Assumes POSIX path
    separator (/).
    """
    # escape regex symbols
    pattern = re.escape(pattern)

    # double star (**) recurses through directories


    # star (*) in a pattern without path separators is a basename wildcard


    # star (*) in a pattern with path separators is a directory or file name
    # wildcard


    # patterns that end with a path separator match everything under that
    # directory


    # brackets ([]) are regex brackets


# antpatterns: https://ant.apache.org/manual/dirtasks.html#patterns
def antpattern_to_regex(ignore_pattern: str):
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

    # patterns that begin with **/ match any amount of leading directories.
    pattern = re.sub(
        r"^\*\*/",
        r"(.*?/|/?)",
        pattern,
    )

    # patterns that end with /** match all files under any directories that
    # match the earlier part of the pattern.
    pattern = re.sub(
        r"/\*\*$",
        r"/.*?",
        pattern,
    )

    # patterns that contain /**/ match zero or more infix directories.
    pattern = re.sub(
        r"/\*\*/",
        r"(/|/.*?/)",
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
