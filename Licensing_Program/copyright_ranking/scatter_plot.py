#! /usr/bin/env python3

import collections
import csv
import math

import matplotlib as mpl
import matplotlib.pyplot as plt

CONFIG = {
    "FairTotalLines" : 16,
}


def adjust_ratio_by_total_header_lines(ratio, total_lines):
    if total_lines >= CONFIG["FairTotalLines"]:
        return ratio
    else:
        return ratio ** ((CONFIG["FairTotalLines"] / total_lines) ** (1 / 4))


def round_base(x, ndigits=0, base=10):
    if ndigits >= 0:
        for _ in range(ndigits):
            x *= base
    else:
        for _ in range(ndigits, 0):
            x /= base

    x = float(int(x))

    if ndigits >= 0:
        for _ in range(ndigits):
            x /= base
    else:
        for _ in range(ndigits, 0):
            x *= base

    return x


def bucket_pairs(pairs):
    return [
        (x, y, 20 * size ** 0.625)
        for (x, y), size in collections.Counter(
            (round_base(x, 6, 2), round_base(y, 6, 2)) for x, y in pairs
        ).items()
    ]


if __name__ == "__main__":
    with open("header_info.csv", "rt") as header_csv:
        header_info = csv.DictReader(header_csv)

        header_info = dict(
            (row["header_name"], int(row["total_lines"]))
            for row in header_info
        )

    with open("specfem3d_info.csv", "rt") as specfem3d_csv:
        specfem3d_info = csv.DictReader(specfem3d_csv)

        data_eq = {
            license : collections.defaultdict(list) for license in header_info
        }
        data_neq = {
            license : collections.defaultdict(list) for license in header_info
        }

        for row in specfem3d_info:
            if row["diff_lineno"] == row["levenshtein_lineno"]:
                data_eq[row["license_name"]]["ratio_pair"].append((
                    float(row["diff_ratio"]),
                    float(row["levenshtein_ratio"]),
                ))
                if header_info[row["license_name"]] < CONFIG["FairTotalLines"]:
                    data_eq[
                        row["license_name"]
                    ]["adjusted_ratio_pair"].append(
                        (
                            adjust_ratio_by_total_header_lines(
                                float(row["diff_ratio"]),
                                header_info[row["license_name"]],
                            ),
                            adjust_ratio_by_total_header_lines(
                                float(row["levenshtein_ratio"]),
                                header_info[row["license_name"]],
                            ),
                        )
                    )
            else:
                data_neq[row["license_name"]]["ratio_pair"].append((
                    float(row["diff_ratio"]),
                    float(row["levenshtein_ratio"]),
                ))
                if header_info[row["license_name"]] < CONFIG["FairTotalLines"]:
                    data_neq[
                        row["license_name"]
                    ]["adjusted_ratio_pair"].append(
                        (
                            adjust_ratio_by_total_header_lines(
                                float(row["diff_ratio"]),
                                header_info[row["license_name"]],
                            ),
                            adjust_ratio_by_total_header_lines(
                                float(row["levenshtein_ratio"]),
                                header_info[row["license_name"]],
                            ),
                        )
                    )

    license_figs = {license : plt.figure() for license in header_info}

    for license, data_types in sorted(data_eq.items()):
        for index, data_name in enumerate(sorted(data_types, reverse=True), 1):
            fig = license_figs[license]

            if header_info[license] < CONFIG["FairTotalLines"]:
                fig.add_subplot(2,2,index)
            else:
                fig.add_subplot(1,2,index)

            ax = fig.gca()
            ax.scatter(
                *zip(*bucket_pairs(data_types[data_name])),
                alpha=0.375,
                color="teal",
                edgecolor="none",
            )
            ax.set_title("Eq Line# : {}: {}".format(license, data_name))
            ax.set_xlim(0.0, 1.0)
            ax.set_ylim(0.0, 1.0)
            ax.set_xlabel("Diff Ratio")
            ax.set_ylabel("Levenshtein Ratio")
            ax.grid(True)

    for license, data_types in sorted(data_neq.items()):
        for index, data_name in enumerate(sorted(data_types, reverse=True), 1):
            fig = license_figs[license]

            if header_info[license] < CONFIG["FairTotalLines"]:
                fig.add_subplot(2,2,index+2)
            else:
                fig.add_subplot(1,2,index+1)

            ax = fig.gca()
            ax.scatter(
                *zip(*bucket_pairs(data_types[data_name])),
                alpha=0.375,
                color="maroon",
                edgecolor="none",
            )
            ax.set_title("Neq Line# : {}: {}".format(license, data_name))
            ax.set_xlim(0.0, 1.0)
            ax.set_ylim(0.0, 1.0)
            ax.set_xlabel("Diff Ratio")
            ax.set_ylabel("Levenshtein Ratio")
            ax.grid(True)

    plt.show()


# plotting ideas:
# plot difference in ratio of diff and leven
# plot how often lineno is difference between diff and leven
