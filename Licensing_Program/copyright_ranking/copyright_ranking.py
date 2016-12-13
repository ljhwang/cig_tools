#! /usr/bin/env python3

import collections
import difflib
import itertools
import multiprocessing
import os
import pathlib
import sys


CONFIG = {
    "LinesChecked" : 32,
    "MaxHeaderLines" : 16,
    "RankMin" : 0.2,
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
                    with filepath.open("rt") as userfile:
                        userfile.read()
                except UnicodeDecodeError:
                    pass
                else:
                    yield filepath


def rank_license_text(args):
    """Returns a list of userfiles and the probability of matching licenses
    in the license sample directory.
    """
    userfile_path, project_dir = args

    def _license_rank_gen():
        with userfile_path.open("rt") as userfile:
            for license_path, userfile_iter in zip(
                CONFIG["LicenseSampleFiles"],
                itertools.tee(
                    userfile,
                    len(CONFIG["LicenseSampleFiles"]) * CONFIG["LinesChecked"]
                )
            ):
                license = license_path.open("rt").read()
                license_len = len(license.splitlines())

                diff_rank, lineno = max(
                    (
                        (
                            difflib.SequenceMatcher(
                                a=license,
                                b="".join(
                                    itertools.islice(
                                        userfile_iter,
                                        lineno,
                                        lineno + license_len,
                                    )
                                ),
                            ).ratio(),
                            lineno + 1,  # line numbers one-based
                        )
                        for lineno in range(CONFIG["LinesChecked"])
                    ),
                    key=lambda pair: pair[0],
                )

                # formula to lessen rank of short headers
                rank = diff_rank ** (
                    max(
                        CONFIG["MaxHeaderLines"]
                            / len(license_path.open("rt").read().splitlines()),
                        1,
                    ) ** (1 / 4))

                yield (rank, diff_rank, lineno, license_path.stem)

    return (
        userfile_path.suffix,
        (
            str(userfile_path.relative_to(project_dir)),
            sorted(_license_rank_gen(), reverse=True),
        )
    )


def print_ranking():
    pool = multiprocessing.Pool()
    result = collections.defaultdict(list)

    for suffix, (path, ranks) in pool.imap_unordered(
        rank_license_text,
        zip(project_path_gen(sys.argv[1]), itertools.repeat(sys.argv[1]))
    ):
        result[suffix] += [(path, ranks)]

    print("{")
    for suffix in sorted(result.keys()):
        empty_ranks = False

        print("  {!r} :".format(suffix))
        print("    [")

        for path, ranks in sorted(result[suffix], key=lambda pair: pair[::-1]):
            ranks = [
                (rank, diff_rank, lineno, license)
                for rank, diff_rank, lineno, license in ranks
                if rank >= CONFIG["RankMin"] or True
            ]

            if ranks:
                if empty_ranks:
                    print("\n\n\n")
                    empty_ranks = False

                print("      {!r} : [".format(path))

                for rank, diff_rank, lineno, license in ranks:
                    print(
                        "        {:6.1%} ({:6.1%}) : {:12} line: {:2}".format(
                            rank, diff_rank, license, lineno)
                    )

                print("      ],")

            else:
                empty_ranks = True
                print("      {!r},".format(path))

        print("    ],")
        print("  ,")

    print("}")


if __name__ == "__main__":
    sys.argv[1] = pathlib.Path(sys.argv[1]).absolute()
    print_ranking()
