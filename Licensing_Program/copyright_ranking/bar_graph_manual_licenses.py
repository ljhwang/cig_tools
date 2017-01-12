from itertools import islice

import matplotlib.pyplot as plt

# bar graph showing number of files per license
def bar_graph_manual_licenses(cursor, colorlist):
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
        color=list(islice(colorlist, 1)),
        edgecolor="",
    )

    files_per_license_zoomed_ax.barh(
        range(len(data_keys)),
        data_values,
        tick_label=data_keys,
        align="center",
        color=list(islice(colorlist, 1)),
        edgecolor="",
    )

    files_per_license_ax.set_xlabel("# of files")
    files_per_license_zoomed_ax.set_xlabel("# of files")

    files_per_license_ax.set_ylim(-9 / 8, len(data_keys))
    files_per_license_zoomed_ax.set_ylim(-9 / 8, len(data_keys))
    files_per_license_zoomed_ax.set_xlim(0, 35)

    files_per_license_ax.grid(axis="x")
    files_per_license_zoomed_ax.grid(axis="x")
