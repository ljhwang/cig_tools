#! /usr/bin/env python3

import collections
import difflib
import itertools
import os
import pathlib
import sys


CONFIG = {
    "LinesChecked" : 50,
    "HeaderToken" : "copyright".casefold(),
    "LicenseSampleFiles" : list(
        pathlib.Path(".").glob("license_samples/*.header")
    ),
}


def project_path_gen(project_dir):
    """Generate absolute paths in project_dir of non-ignored files.
    """
    for cwd, dirs, files in os.walk(str(project_dir)):
        for dirname in list(dirs):
            if dirname.startswith(os.extsep):
                dirs.remove(dirname)

        for filename in files:
            if not filename.startswith(os.extsep):
                filepath = pathlib.Path(os.path.join(cwd, filename)).absolute()
                try:
                    filepath.open("rt").read()
                except UnicodeDecodeError:
                    pass
                else:
                    yield filepath


def find_header_start_line(path):
    """Find line number of line that holds the token string that signals the
    start of the license header.
    """
    with path.open("rt") as ro_file:
        for linenum, line in enumerate(ro_file, 1):
            if CONFIG["HeaderToken"] in line.casefold():
                return linenum
            elif CONFIG["LinesChecked"] < linenum:
                return None

    return None


def rank_license_text(userfile_path, project_dir):
    """Returns a list of licenses sorted based on their percentage chance of
    matching the current header in the userfile.
    """
    header_start_line = find_header_start_line(userfile_path)

    if header_start_line is not None:
        with userfile_path.open("rt") as userfile:
            userfile_iter = iter(
                line
                for index, line in enumerate(userfile, 1)
                if index >= header_start_line
            )

            license_userfileiter_pair = zip(
                CONFIG["LicenseSampleFiles"],
                itertools.tee(userfile_iter,
                              len(CONFIG["LicenseSampleFiles"])),
            )

            def _license_sequence_matcher_gen():
                for license_path, userfile_iter in license_userfileiter_pair:
                    license = license_path.open("rt").read()
                    yield (
                        difflib.SequenceMatcher(
                            a=license,
                            b="".join(
                                itertools.islice(
                                    userfile_iter,
                                    len(license.splitlines())
                                )
                            ),
                        ),
                        license_path.stem,
                    )

            def _fst_ratio_call(pair):
                return (pair[0].ratio(), pair[1])

            return (
                userfile_path.suffix, (
                    str(userfile_path.relative_to(project_dir)),
                    sorted(
                        map(_fst_ratio_call, _license_sequence_matcher_gen()),
                        reverse=True,
                    )
                )
            )

    else:
        return (
            userfile_path.suffix, (
                str(userfile_path.relative_to(project_dir)),
                [(0.0, "no_license")]
            )
        )


def print_ranking():
    result = collections.defaultdict(list)

    for userfile_path in project_path_gen(sys.argv[1]):
        suffix, (path, ranks) = rank_license_text(userfile_path, sys.argv[1])

        result[suffix] += [(path, ranks)]

    print("{")
    for suffix in sorted(result.keys()):
        print("  {!r} :".format(suffix))
        print("    [")

        for path, ranks in sorted(result[suffix], key=lambda pair: pair[::-1]):
            print("      {} : {!r}".format(
                [(round(val, 5), lice) for val, lice in ranks],
                path,
            ))

        print("    ],")
        print("  ,")

    print("}")


if __name__ == "__main__":
    sys.argv[1] = pathlib.Path(sys.argv[1]).absolute()
    print_ranking()
