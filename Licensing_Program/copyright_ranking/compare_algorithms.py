#! /usr/bin/env python3

import collections
import sqlite3 as sql

from pprint import pprint

import matplotlib as mpl
import matplotlib.pyplot as plt

CONFIG = {
    "Specfem3dDB" : "specfem3d_license_info.db",
}


"""
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
"""

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

        pprint(data)

        # bar graph showing ranks for when manual license matches ranked
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

        # bar graph showing ranks for when manual license contradicts top
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
