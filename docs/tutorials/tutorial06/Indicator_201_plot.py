import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect("outputs/KAPy_database.sqlite")

# Read filtered data
query = """
SELECT *
FROM View_EnsembleArealStatistics
WHERE IndicatorCode = '201'
  AND StatisticTypeCode = 'mean'
  AND Percentile = 50
  AND Delta = 0
  AND SeasonCode IN ('DJF', 'JJA')
"""

temp = pd.read_sql(query, conn)
conn.close()

# Plot
fig, axes = plt.subplots(
    2, 1,
    figsize=(8, 8),
    sharex=True,
)

markers = ["o", "s", "^", "D", "v", "P", "X"]

for ax, season in zip(axes, ["DJF", "JJA"]):
    season_data = temp[temp["SeasonCode"] == season]

    for marker, (scenario, df) in zip(
        markers,
        season_data.groupby("ScenarioCode"),
    ):
        ax.plot(
            df["TimeBinCode"],
            df["Value"],
            marker=marker,
            linewidth=2,
            label=scenario,
        )

    ax.set_title(season)
    ax.set_ylabel("Mean precipitation (mm/day)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Scenario")

axes[-1].set_xlabel("Period")

plt.tight_layout()
plt.show()