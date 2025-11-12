import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\rakshitha\3rd year\5TH SEM\SNA\reddit-sna-ai\combined_raw.csv")
print(df.head())

# Create bipartite graph: Users ↔ Subreddits
B = nx.Graph()

# Add nodes
users = df['author'].unique()
subs  = df['subreddit'].unique()
B.add_nodes_from(users, bipartite='users')
B.add_nodes_from(subs,  bipartite='subs')

# Add edges (user-sub relationship)
for _, row in df.iterrows():
    B.add_edge(row['author'], row['subreddit'])

# Get only subreddit nodes
subs = [n for n, d in B.nodes(data=True) if d['bipartite'] == 'subs']

# Create projected subreddit-subnetwork
P = nx.bipartite.weighted_projected_graph(B, subs)

nx.write_gexf(P, "subreddit_network.gexf")
print("✅ Saved: subreddit_network.gexf")

deg = nx.degree_centrality(P)
bet = nx.betweenness_centrality(P, weight='weight')
eig = nx.eigenvector_centrality(P, weight='weight')

# Convert to DataFrame for saving
metrics = pd.DataFrame({
    'subreddit': list(deg.keys()),
    'degree_centrality': list(deg.values()),
    'betweenness_centrality': [bet[k] for k in deg.keys()],
    'eigenvector_centrality': [eig[k] for k in deg.keys()]
})

metrics.to_csv("subreddit_metrics.csv", index=False)
print(metrics)

pos = nx.spring_layout(P, k=0.6)
weights = [P[u][v]['weight'] for u, v in P.edges()]
nx.draw(P, pos, with_labels=True, width=weights, node_size=2000, font_size=10)
plt.title("AI Subreddit Network (User Overlaps)")
plt.show()
