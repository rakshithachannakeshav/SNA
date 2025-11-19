import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

results_dir = Path(r"/resultsC:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\results")
overall = pd.read_csv(r"C:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\results\overall_subreddit_metrics.csv")
pivot = overall.pivot_table(index="year_month", columns="subreddit", values="degree_centrality")
pivot = pivot.sort_index()

plt.figure(figsize=(10,5))
for col in pivot.columns:
    plt.plot(pivot.index, pivot[col], label=col)
plt.xlabel("Month")
plt.ylabel("Degree centrality")
plt.title("Degree centrality over time by subreddit")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
