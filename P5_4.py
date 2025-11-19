# Use the last month's .gexf or compute overlap matrix from overall metrics
import networkx as nx
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

G = nx.read_gexf(r"C:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\results\subreddit_network_2025-09.gexf")
# build adjacency matrix (weights)
subs = sorted(G.nodes())
mat = pd.DataFrame(0, index=subs, columns=subs)
for u,v,d in G.edges(data=True):
    mat.loc[u,v] = d.get('weight',0)
    mat.loc[v,u] = d.get('weight',0)

plt.figure(figsize=(6,5))
plt.imshow(mat.values)
plt.xticks(range(len(subs)), subs, rotation=90)
plt.yticks(range(len(subs)), subs)
plt.title("User overlap heatmap (2025-03)")
plt.colorbar()
plt.tight_layout()
plt.show()

df_trans = pd.read_csv(r"C:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\results\migration_flows.csv")
# aggregate incoming to each target
incoming = df_trans.groupby("target")["count"].sum().sort_values(ascending=False).reset_index()
outgoing = df_trans.groupby("source")["count"].sum().sort_values(ascending=False).reset_index()
print("Top incoming (targets):")
print(incoming)
print("\nTop outgoing (sources):")
print(outgoing)
