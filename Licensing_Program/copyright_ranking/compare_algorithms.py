#! /usr/bin/env python3

from collections import defaultdict
from itertools import cycle, islice, product
import math
import sqlite3 as sql

from pprint import pprint

import matplotlib.colors as colors
import matplotlib.pyplot as plt

from bar_graph_manual_licenses import bar_graph_manual_licenses
from hist_sameness_distributions import hist_sameness_distributions

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
            [
                 0 / 16,  1 / 16,  2 / 16,  3 / 16,
                 4 / 16,                    7 / 16,
                 8 / 16,  9 / 16,
                12 / 16, 13 / 16, 14 / 16,
            ],
            [5 / 6],
            [14 / 16, 11 / 16],
        )
    ),
}


if __name__ == "__main__":
    with sql.connect(
        "file:{}?mode=ro".format(CONFIG["Specfem3dDB"]),
        uri=True,
    ) as conn:
        cursor = conn.cursor()
        bar_graph_manual_licenses(cursor, CONFIG["ColorList"])

        cursor = conn.cursor()
        hist_sameness_distributions(cursor, CONFIG["ColorList"])

        plt.show()
