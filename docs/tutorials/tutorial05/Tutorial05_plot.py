import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect("outputs/KAPy_database.sqlite")

# Read filtered data
query = """
SELECT *
FROM View_EnsembleArealStatistics
WHERE IndicatorCode = '102'
  AND SeasonCode = 'ann'
  AND StatisticTypeCode = 'mean'
  AND Percentile = 50
  AND Delta = 1
"""

temp = pd.read_sql(query, conn)
conn.close()

temp["Year"] = temp["TimeBinCode"].str[:4].astype(int) 

# Plot
fig, ax = plt.subplots(figsize=(8, 5))

markers = ["o", "s", "^", "D", "v", "P", "X"]

ax.axhline(1, linewidth=2, color="black")

for marker, (scenario, df) in zip(
    markers,
    temp.groupby("ScenarioCode"),
):
    ax.plot(
        df["Year"],
        df["Value"],
        marker=marker,
        linewidth=2,
        label=scenario,
    )

ax.set_xlabel("Year")
ax.set_ylabel("Relative number of months per year warmer than 27 C")
ax.grid(True, alpha=0.3)
ax.legend(title="Scenario")

plt.tight_layout()
plt.show()
