import sqlite3
import matplotlib.pyplot as plt
import pandas as pd


# Connect to the KAPy database
conn = sqlite3.connect("./outputs/KAPy_database.sqlite")

# Select annual mean temperature for the ensemble median
query = """
SELECT *
FROM View_MemberArealStatistics
WHERE IndicatorCode = '101'
  AND StatisticTypeCode = 'mean'
  AND Delta = 0
  AND SeasonCode = 'ann'
"""

dat = pd.read_sql(query, conn)

conn.close()

#Drop rcp26, as we only want to compare historical+rcp85
#Drop ERA5 2011-2041, as it is incomplete
drop_these = (
    (dat["ScenarioCode"] == "historical+rcp26") |
    (
        (dat["DatasetCode"] == "ERA5") &
        (dat["TimeBinCode"] == "2011-01-01/2041-01-01")
    )
)

plot_dat = dat[~drop_these]

# And plot
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))

# Dataset colours
datasets = plot_dat["DatasetCode"].unique()
colours = {
    dataset: colour
    for dataset, colour in zip(
        datasets,
        plt.rcParams["axes.prop_cycle"].by_key()["color"]
    )
}

# Member styles
member_styles = {
    member: (linestyle, marker)
    for member, linestyle, marker in zip(
        plot_dat["MemberCode"].unique(),
        ["--", ":", "-."],
        ["o", "s", "^"]
    )
}

for (dataset, member), group in plot_dat.groupby(
    ["DatasetCode", "MemberCode"]
):
    linestyle, marker = member_styles[member]

    ax.plot(
        group["TimeBinCode"],
        group["Value"],
        color=colours[dataset],
        linestyle=linestyle,
        marker=marker,
        markersize=7,
        label=dataset,
    )

ax.set_xlabel("Time period")
ax.set_ylabel("Value")
ax.grid(True, alpha=0.3)

# Dataset legend only
handles = [
    plt.Line2D(
        [],
        [],
        color=colours[dataset],
        linestyle="-",
        marker="o",
        label=dataset,
    )
    for dataset in datasets
]

ax.legend(handles=handles, title="Dataset")

plt.tight_layout()
plt.show()