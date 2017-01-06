#! /usr/bin/env python3

import collections
import csv

import matplotlib as mpl
import matplotlib.pyplot as plt

CONFIG = {}
CONFIG["FairTotalLines"] = 16


def adjust_ratio_by_total_header_lines(ratio, total_lines):
    if total_lines >= CONFIG["FairTotalLines"]:
        return ratio
    else:
        return ratio ** ((CONFIG["FairTotalLines"] / total_lines) ** (1 / 4))


if __name__ == "__main__":
    with open("header_info.csv", "rt") as header_csv:
        header_info = csv.DictReader(header_csv)

        header_info = dict(
            (row["header_name"], int(row["total_lines"]))
            for row in header_info
        )

    with open("specfem3d_info.csv", "rt") as specfem3d_csv:
        specfem3d_info = csv.DictReader(specfem3d_csv)

        data = {
            license : collections.defaultdict(list) for license in header_info
        }

        for row in specfem3d_info:
            data[row["license_name"]]["diff"].append(float(row["diff_ratio"]))
            data[row["license_name"]]["levenshtein"].append(
                float(row["levenshtein_ratio"])
            )

            if header_info[row["license_name"]] < CONFIG["FairTotalLines"]:
                data[row["license_name"]]["adjusted_diff"].append(
                    adjust_ratio_by_total_header_lines(
                        float(row["diff_ratio"]),
                        header_info[row["license_name"]],
                    )
                )
                data[row["license_name"]]["adjusted_levenshtein"].append(
                    adjust_ratio_by_total_header_lines(
                        float(row["levenshtein_ratio"]),
                        header_info[row["license_name"]],
                    )
                )

    license_figs = {license : plt.figure() for license in header_info}

    for license, data_types in sorted(data.items()):
        for index, data_name in enumerate(sorted(data_types, reverse=True), 1):
            fig = license_figs[license]

            if header_info[license] < CONFIG["FairTotalLines"]:
                fig.add_subplot(2,2,index)
            else:
                fig.add_subplot(1,2,index)

            ax = fig.gca()
            ax.hist(
                data_types[data_name],
                bins=100,
                range=(0.0, 1.0),
                normed=True,
                cumulative=-1,
                color="teal",
                edgecolor="none",
            )
            ax.set_title("{}: {}".format(license, data_name))
            ax.set_ylim(0.0, 1.0)
            ax.grid(True)

    plt.show()


# plotting ideas:
# plot difference in ratio of diff and leven
# plot how often lineno is difference between diff and leven
