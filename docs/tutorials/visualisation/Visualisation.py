import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect("outputs/KAPy_database.sqlite")

# Read filtered data
query = """
SELECT *
FROM View_EnsembleArealStatistics
WHERE IndicatorCode = '101'
  AND SeasonCode = 'ann'
  AND StatisticTypeCode = 'mean'
  AND Percentile = 50
  AND Delta = 0
"""

temp = pd.read_sql(query, conn)
conn.close()

# Plot
fig, ax = plt.subplots(figsize=(8, 5))

markers = ["o", "s", "^", "D", "v", "P", "X"]

for marker, (scenario, df) in zip(markers, temp.groupby("ScenarioCode")):
    ax.plot(
        df["TimeBinCode"],
        df["Value"],
        marker=marker,
        linewidth=2,
        label=scenario,
    )

ax.set_xlabel("Period")
ax.set_ylabel("Mean annual temperature")
ax.grid(True, alpha=0.3)
ax.legend(title="Scenario")

plt.tight_layout()
plt.show()