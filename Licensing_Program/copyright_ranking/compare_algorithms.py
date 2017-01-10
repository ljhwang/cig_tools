#! /usr/bin/env python3

import collections
import sqlite3 as sql

from pprint import pprint

import matplotlib as mpl
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
    "ColorMap" : list(
        itertools.permutations((2 / 8, 3 / 8, 4 / 8, 5 / 8, 6 / 8), 3)
    ),
}

CONFIG["ColorMap"] = (
    CONFIG["ColorMap"][0::3]
    + CONFIG["ColorMap"][1::3]
    + CONFIG["ColorMap"][2::3]
)

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
                reverse=True,
            )
        )

        data_keys = list(data_keys)
        data_values = list(data_values)

        files_per_license_fig = plt.figure()
        files_per_license_fig.suptitle(
            "# of files per license (manual best-effort)"
        )

        files_per_license_fig.add_subplot(1,2,1)
        files_per_license_ax = files_per_license_fig.gca()

        files_per_license_fig.add_subplot(1,2,2)
        files_per_license_rare_ax = files_per_license_fig.gca()

        files_per_license_ax.bar(
            range(len(data_keys)),
            data_values,
            tick_label=data_keys,
            align='center',
            color='teal',
            edgecolor='',
        )

        # remove largest values, to show values for rare licenses
        # works because data is sorted
        rare_values = list(filter(lambda n: n < 100, data_values))
        rare_keys = data_keys[len(data_keys) - len(rare_values):]

        files_per_license_rare_ax.bar(
            range(len(rare_keys)),
            rare_values,
            tick_label=rare_keys,
            align='center',
            color='maroon',
            edgecolor='',
        )

        files_per_license_ax.set_xticklabels(
            files_per_license_ax.xaxis.get_majorticklabels(),
            rotation=90,
            horizontalalignment='center',
        )

        files_per_license_rare_ax.set_xticklabels(
            files_per_license_rare_ax.xaxis.get_majorticklabels(),
            rotation=90,
            horizontalalignment='center',
        )

        files_per_license_ax.set_ylabel("# of files")
        files_per_license_rare_ax.set_ylabel("# of files")

        files_per_license_ax.set_xlim(-9 / 8, len(data_keys))
        files_per_license_rare_ax.set_xlim(-9 / 8, len(data_keys))

        files_per_license_ax.grid(axis='y')
        files_per_license_rare_ax.grid(axis='y')

        files_per_license_fig.subplots_adjust(bottom=0.25)

        plt.show()

        # histogram showing ranks for when manual license matches ranked
        # licenses
        cursor = cursor.execute("""
            SELECT
              ranking_algorithms.name,
              licenses.name,
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
              JOIN
                  licenses
                ON
                  project_files.manual_license = licenses.id
            GROUP BY
                calculated_license_rank.file,
                calculated_license_rank.algorithm
              HAVING
                MAX(calculated_license_rank.ranking)
          INTERSECT
            SELECT
              ranking_algorithms.name,
              licenses.name,
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
              JOIN
                  licenses
                ON
                  project_files.manual_license = licenses.id
            WHERE
                calculated_license_rank.license = project_files.manual_license
        """)

        data = collections.defaultdict(list)

        for algorithm, license, ranking in cursor:
            data[(algorithm, license)].append(ranking)

        pprint(data)

        # histogram showing ranks for when manual license contradicts top
        # ranked license
        cursor = cursor.execute("""
            SELECT
              ranking_algorithms.name,
              project_files.manual_license,
              calculated_license_rank.license,
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
          INTERSECT
            SELECT
              ranking_algorithms.name,
              project_files.manual_license,
              calculated_license_rank.license,
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
            WHERE
                calculated_license_rank.license != project_files.manual_license
        """)

        data = collections.defaultdict(list)

        license_cursor = conn.cursor()

        for algorithm, manual_license, ranked_license, ranking in cursor:
            (manual_license,) = license_cursor.execute(
                "SELECT name FROM licenses WHERE id = ?",
                [manual_license],
            ).fetchone()

            (ranked_license,) = license_cursor.execute(
                "SELECT name FROM licenses WHERE id = ?",
                [ranked_license],
            ).fetchone()

            data[(algorithm, manual_license, ranked_license)].append(ranking)

        pprint(data)
