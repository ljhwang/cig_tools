import math

from collections import defaultdict
from itertools import islice

import matplotlib.pyplot as plt


def hist_cecill_deltaerror_rank_distribution(cursor, colorlist):
    cursor = cursor.execute("""
            SELECT
              max_ranking.ranking
              - cecill_ranking.ranking,
              ranking_algorithms.name
            FROM
                  (
                    SELECT
                      calculated_license_rank.file,
                      calculated_license_rank.algorithm,
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
                          calculated_license_rank.algorithm
                          = ranking_algorithms.id
                      JOIN
                          licenses AS manu_licenses
                        ON
                          project_files.manual_license = manu_licenses.id
                      JOIN
                          licenses AS calc_licenses
                        ON
                          calculated_license_rank.license = calc_licenses.id
                    WHERE
                      manu_licenses.name = 'cecill-c-1'
                    GROUP BY
                        calculated_license_rank.file,
                        calculated_license_rank.algorithm
                      HAVING
                        MAX(calculated_license_rank.ranking)
                  ) AS max_ranking
              JOIN
                  (
                    SELECT
                      calculated_license_rank.file,
                      calculated_license_rank.algorithm,
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
                          calculated_license_rank.algorithm
                          = ranking_algorithms.id
                      JOIN
                          licenses AS manu_licenses
                        ON
                          project_files.manual_license = manu_licenses.id
                      JOIN
                          licenses AS calc_licenses
                        ON
                          calculated_license_rank.license = calc_licenses.id
                    WHERE
                        manu_licenses.name = 'cecill-c-1'
                      AND
                        calc_licenses.name = 'cecill-c-1'
                  ) AS cecill_ranking
                ON
                    max_ranking.file
                    = cecill_ranking.file
                  AND
                    max_ranking.algorithm
                    = cecill_ranking.algorithm
              JOIN
                  ranking_algorithms
                ON
                  max_ranking.algorithm = ranking_algorithms.id
    """)

    data = defaultdict(list)

    for difference, algorithm in cursor:
        data[algorithm].append(difference)

    cecill_deltaerror_rank_fig = plt.figure()
    cecill_deltaerror_rank_fig.suptitle(
        "Diff Distribution for Cecill-C-1 License Ranking"
    )

    cecill_deltaerror_rank_fig.add_subplot()
    cecill_deltaerror_rank_ax = cecill_deltaerror_rank_fig.gca()

    data_keys, data_values = zip(*sorted(data.items()))

    cecill_deltaerror_rank_ax.hist(
        data_values,
        bins=50,
        range=(0,1),
        color=list(islice(colorlist, len(data_keys))),
        edgecolor="None",
        label=["{}".format(algorithm) for algorithm in data_keys],
        width=1 / 100,
        rwidth=1,
    )

    cecill_deltaerror_rank_ax.set_xlim(0,1)

    cecill_deltaerror_rank_ax.set_xlabel(
        "Difference Between Highest Ranked License & Correct License"
    )
    cecill_deltaerror_rank_ax.legend(loc="best")
    cecill_deltaerror_rank_ax.grid(True)
