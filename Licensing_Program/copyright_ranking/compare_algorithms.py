#! /usr/bin/env python3

from collections import defaultdict
from itertools import cycle, islice, product
import math
import sqlite3 as sql

from pprint import pprint

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt

CONFIG = {
    "Specfem3dDB" : "specfem3d_license_info.db",
    "DatabaseSchema" : """
        CREATE TABLE licenses
            (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                line_amount INTEGER DEFAULT NULL
            );
        CREATE TABLE project_files
            (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                manual_license REFERENCES licenses (id)
            );
        CREATE TABLE ranking_algorithms
            (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
        CREATE TABLE calculated_license_rank
            (
                file REFERENCES project_files (id),
                algorithm REFERENCES ranking_algorithms (id),
                license REFERENCES licenses (id),
                ranking REAL NOT NULL,
                position_lineno INTEGER NOT NULL,
                PRIMARY KEY (file, algorithm, license)
            );
        """,
    "ColorList" : cycle(
        colors.hsv_to_rgb(triple)
        for triple in product(
            [i / 8 for i in range(8)],
            [5 / 6],
            [7 / 8, 5 / 8],
        )
    ),
}


if __name__ == "__main__":
    with sql.connect(
        "file:{}?mode=ro".format(CONFIG["Specfem3dDB"]),
        uri=True,
    ) as conn:
        cursor = conn.cursor()

        # bar graph showing number of files per license
        cursor = cursor.execute("""
            SELECT
              licenses.name,
              COUNT(*)
            FROM
                  project_files
              JOIN
                  licenses
                ON
                  project_files.manual_license = licenses.id
            GROUP BY
              project_files.manual_license
        """)

        data = { license : count for license, count in cursor }

        data_keys, data_values = zip(
            *sorted(
                data.items(),
                key=lambda pair: tuple(reversed(pair)),
            )
        )

        data_keys = list(data_keys)
        data_values = list(data_values)

        files_per_license_fig = plt.figure()
        files_per_license_fig.suptitle(
            "# of Files Per License (Manually Classified)"
        )

        files_per_license_fig.add_subplot(2,1,1)
        files_per_license_ax = files_per_license_fig.gca()

        files_per_license_fig.add_subplot(2,1,2)
        files_per_license_zoomed_ax = files_per_license_fig.gca()

        files_per_license_ax.barh(
            range(len(data_keys)),
            data_values,
            tick_label=data_keys,
            align="center",
            color=list(islice(CONFIG["ColorList"], 1)),
            edgecolor="",
        )

        files_per_license_zoomed_ax.barh(
            range(len(data_keys)),
            data_values,
            tick_label=data_keys,
            align="center",
            color=list(islice(CONFIG["ColorList"], 1, 2)),
            edgecolor="",
        )

        files_per_license_ax.set_xlabel("# of files")
        files_per_license_zoomed_ax.set_xlabel("# of files")

        files_per_license_ax.set_ylim(-9 / 8, len(data_keys))
        files_per_license_zoomed_ax.set_ylim(-9 / 8, len(data_keys))
        files_per_license_zoomed_ax.set_xlim(0, 35)

        files_per_license_ax.grid(axis="x")
        files_per_license_zoomed_ax.grid(axis="x")

        # histograms showing rank distribution for correctly and incorrectly
        # ranked licenses (matching or not matching manual license
        # determination)
        rank_dist_fig = plt.figure()

        rank_dist_fig.add_subplot(1,2,1)
        correctly_ranked_ax = rank_dist_fig.gca()
        rank_dist_fig.add_subplot(1,2,2)
        incorrectly_ranked_ax = rank_dist_fig.gca()

        cursor = cursor.execute("""
            SELECT
              calculated_license_rank.license = project_files.manual_license,
              ranking_algorithms.name,
              calculated_license_rank.ranking
            FROM
                  calculated_license_rank
              JOIN
                  project_files
                ON
                  calculated_license_rank.file = project_files.id
              JOIN
                  ranking_algorithms
                ON
                  calculated_license_rank.algorithm = ranking_algorithms.id
            GROUP BY
                calculated_license_rank.file,
                calculated_license_rank.algorithm
              HAVING
                MAX(calculated_license_rank.ranking)
        """)

        data_matching = defaultdict(list)
        data_not_matching = defaultdict(list)

        for match, algorithm, ranking in cursor:
            if match:
                data_matching[algorithm].append(ranking)
            else:
                data_not_matching[algorithm].append(ranking)

        data_keys_match, data_values_match = zip(*sorted(data_matching.items()))
        data_keys_nomatch, data_values_nomatch = zip(*sorted(
            data_not_matching.items()
        ))

        correctly_ranked_ax.hist(
            data_values_match,
            range=(0,1),
            bins=50,
            color=list(islice(CONFIG["ColorList"], 2, len(data_matching) + 2)),
            edgecolor="None",
            label=[
                "{} - Total: {}".format(key, len(data_matching[key]))
                for key in data_keys_match
            ],
        )

        incorrectly_ranked_ax.hist(
            data_values_nomatch,
            range=(0,1),
            bins=50,
            color=list(islice(
                CONFIG["ColorList"],
                2 + len(data_matching),
                2 + len(data_matching) + len(data_not_matching)
            )),
            edgecolor="None",
            label=[
                "{} - Total: {}".format(key, len(data_not_matching[key]))
                for key in data_keys_nomatch
            ],
        )

        correctly_ranked_ax.set_xticklabels([
            "{:.0%}".format(tick)
            for tick in correctly_ranked_ax.get_xticks()
        ])
        incorrectly_ranked_ax.set_xticklabels([
            "{:.0%}".format(tick)
            for tick in incorrectly_ranked_ax.get_xticks()
        ])

        correctly_ranked_ax.set_title(
            "Sameness Distribution of Files Correctly Ranked"
        )
        incorrectly_ranked_ax.set_title(
            "Sameness Distribution of Files Incorrectly Ranked"
        )

        correctly_ranked_ax.set_xlabel("Algorithm Result (Sameness)")
        incorrectly_ranked_ax.set_xlabel("Algorithm Result (Sameness)")

        correctly_ranked_ax.set_ylim(0, 600)
        incorrectly_ranked_ax.set_ylim(0, 600)

        correctly_ranked_ax.legend()
        incorrectly_ranked_ax.legend()

        correctly_ranked_ax.grid(True)
        incorrectly_ranked_ax.grid(True)

        plt.show()
