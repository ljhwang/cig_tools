
import re


def _bracket_tagged_partitions(string):
    """Partitions `string` into pairs of tags and non-bracketed or bracketed
    strings. Tags are either `None` or `'brackets'`. Raises an error if
    brackets are not closed.
    """
    ret = []
    bracket_begin = r"^|[^\\]\["
    bracket_end = r"[^\\]\]"

    def _bracket_parse(string):
        """Partitions on first bracket pair.
        """
        begin_match = re.search(bracket_begin, string)

        if begin_match:
            end_match = re.search(bracket_end, string[begin_match.end():])
            if end_match:
                prefix = string[:begin_match.end() - 1]
                brackets = string[begin.match.end() - 1:end_match.end()]
                suffix = string[end_match.end():]

                return (
                    [(None, prefix)] if prefix else []
                    + [('brackets', brackets)]
                    + [(None, suffix)] if suffix else []
                )

            else:
                raise ValueError("'string' did not contain closing bracket.")

        else:
            return [(None, string)]

    parsed = _bracket_parse(string)

    while len(parsed) > 1 and parsed[-1][0] is None:
        tag, string = parsed.pop(-1)
        ret += parsed
        parsed = _bracket_parse(string)

    return ret + parsed


def filepattern_to_regex(pattern):
    """Convert config filepattern to filepath regex. Assumes POSIX path
    separator (/).
    """
    # escaped symbols: \ . ? $ ^ ( ) { } + |
    # used symbols: [ ] * **
    # path symbol: /



    # double stars connected to path separators (**/) (/**/) (/**) recurse
    # through directories


    # a pattern without path separators is a basename pattern
    if "/" not in pattern:
        pattern = re.sub(
            r"^",
            r"^|(?:.*?/)",
            pattern,
        )

    # star (*) is a path part wildcard (unless in brackets)
    pattern = re.sub(
        r"*",
        r"[^/]*?",
        pattern,
    )


    # patterns that end with a path separator recurse through all
    # subdirectories
    pattern = re.sub(
        r"/$",
        r"/.*",
        pattern,
    )

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
