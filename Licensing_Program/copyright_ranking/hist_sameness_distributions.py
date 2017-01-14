import math

from collections import defaultdict
from itertools import islice

import matplotlib.pyplot as plt


def hist_sameness_distributions(cursor, colorlist):
    rank_dist_fig = plt.figure()
    rank_dist_fig.suptitle(
        "Sameness Distribution"
    )
    rank_dist_license_fig = plt.figure()
    rank_dist_license_fig.suptitle(
        "Sameness Distribution per License"
    )

    rank_dist_fig.add_subplot()
    rank_dist_ax = rank_dist_fig.gca()

    cursor = cursor.execute("""
        SELECT
          calculated_license_rank.license = project_files.manual_license,
          ranking_algorithms.name,
          manu_licenses.name,
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
              licenses AS manu_licenses
            ON
              project_files.manual_license = manu_licenses.id
        GROUP BY
            calculated_license_rank.file,
            calculated_license_rank.algorithm
          HAVING
            MAX(calculated_license_rank.ranking)
    """)

    data = defaultdict(list)
    data_per_license = defaultdict(lambda: defaultdict(list))

    for match, algorithm, manual_license, ranking in cursor:
        data[(bool(match), algorithm)].append(ranking)

        data_per_license[manual_license][
            (bool(match), algorithm)
        ].append(ranking)

    data_keys, data_values = zip(*sorted(data.items()))

    rank_dist_ax.hist(
        data_values,
        bins=50,
        range=(0,1),
        color=list(islice(colorlist, len(data))),
        edgecolor="None",
        label=[
            "{} - {} {}".format(
                algorithm,
                len(data[(match, algorithm)]),
                "correctly ranked" if match else "incorrectly ranked",
            )
            for match, algorithm in data_keys
        ],
        width=1 / 200,
        rwidth=1,
    )

    rank_dist_ax.set_xlim(0,1)

    rank_dist_ax.set_xlabel("Algorithm Result (Sameness)")
    rank_dist_ax.legend(loc="best")
    rank_dist_ax.grid(True)

    data_per_license = dict(
        filter(
            lambda pair: 4 < sum(len(ranks) for ranks in pair[1].values()),
            data_per_license.items(),
        )
    )

    for index, (license, license_dict) in enumerate(
        sorted(
            data_per_license.items(),
            key=lambda pair: sum(len(ranks) for ranks in pair[1].values()),
            reverse=True,
        ),
        1,
    ):
        license_dict_keys, license_dict_values = zip(
            *sorted(license_dict.items(), reverse=True)
        )

        rank_dist_license_fig.add_subplot(
            math.floor(len(data_per_license) ** (1 / 2)),
            math.ceil(len(data_per_license) ** (1 / 2)),
            index,
        )
        ax = rank_dist_license_fig.gca()

        ax.hist(
            license_dict_values,
            bins=50,
            range=(0,1),
            label=[
                "{} - {} {}".format(
                    algorithm,
                    len(license_dict[(match, algorithm)]),
                    "correctly ranked" if match else "incorrectly ranked",
                )
                for match, algorithm in license_dict_keys
            ],
            color=list(islice(
                colorlist,
                len(license_dict) + len(license_dict) % 2,
            ))[:len(license_dict)],
            edgecolor="None",
            width=1 / 100,
            rwidth=1,
        )

        ax.set_xlim(0,1)

        ax.grid(True)
        ax.legend(loc='best', fontsize="small")
        ax.set_title("{}".format(license))
