import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

# ===========================
# SETUP: PROJECT ROOT + RESULTS FOLDER
# ===========================
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ===========================
# 1. LOAD DATA
# ===========================
print("Loading data...")

df = pd.read_csv(
    os.path.join(ROOT, "combined_raw.csv")
)
print(df.head())

# ===========================
# 2. TIMESTAMP → YEAR/MONTH
# ===========================
print("Converting timestamps...")

df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
df['year'] = df['created_utc'].dt.year
df['month'] = df['created_utc'].dt.month

# ===========================
# 3. USER TIMELINE CREATION
# ===========================
print("Creating user timelines...")

df_sorted = df.sort_values(by=['author', 'created_utc'])

df_sorted.to_csv(
    os.path.join(RESULTS_DIR, "user_timeline.csv"), index=False
)

print("Saved: user_timeline.csv")

# ===========================
# 4. MIGRATION PAIR EXTRACTION
# ===========================
print("Extracting migration patterns...")

migrations = []

for user, group in df_sorted.groupby('author'):
    subs = group['subreddit'].unique()
    for i in range(len(subs) - 1):
        migrations.append([subs[i], subs[i+1]])

mig_df = pd.DataFrame(migrations, columns=['from_sub', 'to_sub'])

mig_df.to_csv(
    os.path.join(RESULTS_DIR, "user_migrations.csv"), index=False
)

print("Saved: user_migrations.csv")

# ===========================
# 5. MIGRATION FLOW COUNTS
# ===========================
print("Calculating migration flow...")

flow = mig_df.groupby(['from_sub', 'to_sub']).size().reset_index(name='count')

flow.to_csv(
    os.path.join(RESULTS_DIR, "migration_flow.csv"), index=False
)

print("Saved: migration_flow.csv")
print(flow)

# ===========================
# 6. DIRECTED MIGRATION NETWORK
# ===========================
print("Building directed migration graph...")

G = nx.DiGraph()

for _, row in flow.iterrows():
    G.add_edge(row['from_sub'], row['to_sub'], weight=row['count'])

pos = nx.spring_layout(G, k=0.7)
weights = [G[u][v]['weight'] for u, v in G.edges()]

plt.figure(figsize=(10, 7))
nx.draw(G, pos, with_labels=True, node_size=3000, width=weights, font_size=10)
plt.title("User Migration Flow Between AI Subreddits")
plt.tight_layout()

plt.savefig(
    os.path.join(RESULTS_DIR, "migration_flow_graph.png"), dpi=300
)

print("Saved: migration_flow_graph.png")
plt.close()

# ===========================
# 7. TEMPORAL TREND ANALYSIS
# ===========================
print("Analyzing trending subreddit activity...")

trend = df.groupby(['year', 'subreddit']).size().reset_index(name='posts')

trend.to_csv(
    os.path.join(RESULTS_DIR, "subreddit_trends.csv"), index=False
)

print("Saved: subreddit_trends.csv")

# Plot each subreddit's posting trend
plt.figure(figsize=(10, 7))

for sub in trend['subreddit'].unique():
    sub_data = trend[trend['subreddit'] == sub]
    plt.plot(sub_data['year'], sub_data['posts'], marker='o', label=sub)

plt.legend()
plt.title("Subreddit Activity Over Time")
plt.xlabel("Year")
plt.ylabel("Post Count")
plt.tight_layout()

plt.savefig(
    os.path.join(RESULTS_DIR, "subreddit_trend_graph.png"), dpi=300
)

print("Saved: subreddit_trend_graph.png")
plt.close()

# ===========================
# END
# ===========================
print("\n✨ Migration Analysis Completed Successfully!")
print("All files saved inside: results/")
