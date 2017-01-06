#! /usr/bin/env python3

import csv
import sqlite3 as sql


CONFIG = {
    "HeaderLinesCSV" : "header_info.csv",
    "CalculatedRankingsCSV" : "specfem3d_info.csv",
    "ManualCheckCSV" : "specfem3d_file_licenses.csv",
    "Specfem3dDB" : "specfem3d_license_info.db",
}

with sql.connect(CONFIG["Specfem3dDB"]) as conn:
    conn.execute(
        "CREATE TABLE licenses"
        " ("
            " id INTEGER PRIMARY KEY,"
            " name TEXT NOT NULL UNIQUE,"
            " line_amount INTEGER DEFAULT NULL"
        " )"
    )

    conn.execute(
        "CREATE TABLE project_files"
        " ("
            " id INTEGER PRIMARY KEY,"
            " path TEXT NOT NULL UNIQUE,"
            " manual_license REFERENCES licenses (id)"
        " )"
    )

    conn.execute(
        "CREATE TABLE ranking_algorithms"
        " ("
            " id INTEGER PRIMARY KEY,"
            " name TEXT NOT NULL UNIQUE"
        " )"
    )

    conn.execute(
        "CREATE TABLE calculated_license_rank"
        " ("
            " file REFERENCES project_files (id),"
            " algorithm REFERENCES ranking_algorithms (id),"
            " license REFERENCES licenses (id),"
            " ranking REAL NOT NULL,"
            " position_lineno INTEGER NOT NULL,"
            " PRIMARY KEY (file, algorithm, license)"
        " )"
    )

    with open(CONFIG["HeaderLinesCSV"], "rt") as header_file:
        header_csv = csv.DictReader(header_file)

        conn.executemany(
            "INSERT INTO licenses(name, line_amount) VALUES (?, ?)",
            ((row["header_name"], row["total_lines"]) for row in header_csv),
        )

    with open(CONFIG["ManualCheckCSV"], "rt") as manual_check_file:
        manual_csv = csv.DictReader(manual_check_file)

        for row in manual_csv:
            conn.execute(
                "INSERT OR IGNORE INTO licenses (name, line_amount)"
                " VALUES (?, NULL)",
                [row["license_name"]],
            )

            (license_id,) = conn.execute(
                "SELECT id FROM licenses WHERE name = ?",
                [row["license_name"]]
            ).fetchone()

            conn.execute(
                "INSERT INTO project_files (path, manual_license)"
                " VALUES (?, ?)",
                [
                    row["userfile_path"],
                    license_id,
                ],
            )

    conn.executemany(
        "INSERT INTO ranking_algorithms (name) VALUES (?)",
        [["ratcliff-obershelp"], ["levenshtein"]],
    )

    (ratcliff_obershelp_id,) = conn.execute(
        "SELECT id FROM ranking_algorithms WHERE name == 'ratcliff-obershelp'"
    ).fetchone()

    (levenshtein_id,) = conn.execute(
        "SELECT id FROM ranking_algorithms WHERE name == 'levenshtein'"
    ).fetchone()

    with open(CONFIG["CalculatedRankingsCSV"], "rt") as ranking_file:
        ranking_csv = csv.DictReader(ranking_file)

        for row in ranking_csv:
            (license_id,) = conn.execute(
                "SELECT id FROM licenses WHERE name == ?",
                [row["license_name"]],
            ).fetchone()

            (userfile_id,) = conn.execute(
                "SELECT id FROM project_files WHERE path == ?",
                [row["userfile_path"]],
            ).fetchone()

            conn.execute(
                "INSERT INTO calculated_license_rank"
                " (file, algorithm, license, ranking, position_lineno) VALUES"
                " (:file, :algorithm, :license, :ranking, :position_lineno)",
                {
                    "file" : userfile_id,
                    "algorithm" : ratcliff_obershelp_id,
                    "license" : license_id,
                    "ranking" : row["diff_ratio"],
                    "position_lineno" : row["diff_lineno"],
                }
            )

            conn.execute(
                "INSERT INTO calculated_license_rank"
                " (file, algorithm, license, ranking, position_lineno) VALUES"
                " (:file, :algorithm, :license, :ranking, :position_lineno)",
                {
                    "file" : userfile_id,
                    "algorithm" : levenshtein_id,
                    "license" : license_id,
                    "ranking" : row["levenshtein_ratio"],
                    "position_lineno" : row["levenshtein_lineno"],
                }
            )
