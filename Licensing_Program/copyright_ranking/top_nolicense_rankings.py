#! /usr/bin/env python3

import sqlite3 as sql

CONFIG = {
    "Specfem3dDB" : "specfem3d_license_info.db",
    "RecordLimit" : 10,
}


if __name__ == "__main__":
    with sql.connect(
        "file:{}?mode=ro".format(CONFIG["Specfem3dDB"]),
        uri=True,
    ) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
              project_files.path,
              ranking_algorithms.name,
              calculated_license_rank.ranking
            FROM
                  calculated_license_rank
              JOIN
                  project_files
                ON
                  calculated_license_rank.file = project_files.id
              JOIN
                  licenses AS manu_licenses
                ON
                  project_files.manual_license = manu_licenses.id
              JOIN
                  ranking_algorithms
                ON
                  calculated_license_rank.algorithm = ranking_algorithms.id
            WHERE
                manu_licenses.name = 'NOLICENSE'
              AND
                calculated_license_rank.ranking >= 0.75
            GROUP BY
                calculated_license_rank.file,
                calculated_license_rank.algorithm
              HAVING
                MAX(calculated_license_rank.ranking)
            ORDER BY
              calculated_license_rank.ranking DESC
            LIMIT
              ?
        """, [CONFIG["RecordLimit"]])

        for filepath, algorithm, rank in cursor:
            print("{} - {} : {}".format(filepath, algorithm, rank))
