# migration_analysis notebook cell
import pandas as pd
import networkx as nx
from pathlib import Path
import community as community_louvain
from tqdm import tqdm
import math

data_path = Path(r"C:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\user_sub_month.csv")
results_dir = Path(r"C:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\results")
results_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(data_path)
print("Rows loaded:", len(df))
if 'count' not in df.columns:
    df['count'] = 1

expected = {'author','subreddit','year_month','count'}
if not expected.issubset(set(df.columns)):
    raise ValueError(f"Missing expected columns. Found: {df.columns.tolist()}")

months = sorted(df['year_month'].unique())
gexf_files = []

for month in months:
    dfm = df[df['year_month'] == month]
    B = nx.Graph()
    for _, r in dfm.iterrows():
        user_node = f"U::{r['author']}"
        sub_node = f"S::{r['subreddit']}"
        B.add_node(user_node, bipartite='user')
        B.add_node(sub_node, bipartite='subreddit')
        weight = int(r.get('count', 1)) if not (isinstance(r.get('count'), float) and math.isnan(r.get('count'))) else 1
        B.add_edge(user_node, sub_node, weight=weight)

    sub_nodes = [n for n,d in B.nodes(data=True) if d['bipartite']=='subreddit']
    if len(sub_nodes) == 0:
        print(f"[WARN] No subreddit nodes for {month}, skipping")
        continue

    P = nx.bipartite.weighted_projected_graph(B, sub_nodes)

    G = nx.Graph()
    for u,v,data in P.edges(data=True):
        subu = u.split("::",1)[1]
        subv = v.split("::",1)[1]
        w = data.get('weight',0)
        if G.has_edge(subu, subv):
            G[subu][subv]['weight'] += w
        else:
            G.add_edge(subu, subv, weight=w)
    for n in P.nodes():
        subn = n.split("::",1)[1]
        if not G.has_node(subn):
            G.add_node(subn)

    out_file = results_dir / f"subreddit_network_{month}.gexf"
    nx.write_gexf(G, out_file)
    gexf_files.append(out_file)
    print(f"Saved .gexf for {month}: nodes={G.number_of_nodes()} edges={G.number_of_edges()} -> {out_file}")

metric_frames = []
for p in gexf_files:
    month = p.stem.split("_")[-1]
    G = nx.read_gexf(p)
    deg = nx.degree_centrality(G)
    try:
        bet = nx.betweenness_centrality(G, weight='weight')
    except Exception:
        bet = {n:0.0 for n in G.nodes()}
    try:
        eig = nx.eigenvector_centrality_numpy(G, weight='weight')
    except Exception:
        eig = {n:0.0 for n in G.nodes()}
    try:
        part = community_louvain.best_partition(G, weight='weight')
    except Exception:
        part = {n:-1 for n in G.nodes()}

    rows = []
    for n in G.nodes():
        rows.append({
            "subreddit": n,
            "degree_centrality": deg.get(n, 0.0),
            "betweenness": bet.get(n, 0.0),
            "eigenvector": eig.get(n, 0.0),
            "community": part.get(n, -1),
            "node_degree": G.degree(n),
            "year_month": month
        })
    dfm = pd.DataFrame(rows)
    out_metrics = results_dir / f"metrics_{month}.csv"
    dfm.to_csv(out_metrics, index=False)
    metric_frames.append(dfm)
    print(f"Saved metrics for {month} -> {out_metrics}")

if metric_frames:
    overall = pd.concat(metric_frames, ignore_index=True)
    overall_out = results_dir / "overall_subreddit_metrics.csv"
    overall.to_csv(overall_out, index=False)
    print("Saved overall metrics ->", overall_out)

user_month = df.groupby(['author','year_month'])['subreddit'].unique().reset_index()
transitions = {}
for author, group in user_month.groupby('author'):
    g = group.sort_values('year_month')
    months_list = list(g['year_month'])
    subs_list = list(g['subreddit'])
    for i in range(len(months_list)-1):
        src_subs = subs_list[i]
        tgt_subs = subs_list[i+1]
        tgt_month = months_list[i+1]
        for s in src_subs:
            for t in tgt_subs:
                key = (s, t, tgt_month)
                transitions[key] = transitions.get(key, 0) + 1

rows = [{"source": k[0], "target": k[1], "month": k[2], "count": v} for k,v in transitions.items()]
df_trans = pd.DataFrame(rows).sort_values(['month','count'], ascending=[True, False])
out_trans = results_dir / "migration_flows.csv"
df_trans.to_csv(out_trans, index=False)
print("Saved migration flows ->", out_trans)

print("All done. Files written to:", results_dir)
