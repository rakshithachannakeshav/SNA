import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

results_dir = Path(r"C:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\results")
df_trans = pd.read_csv(r"C:\Users\Meghana\OneDrive\Desktop\meghna\.vs studio\reddit-sna-ai\results\migration_flows.csv")

agg = df_trans.groupby(["source","target"], as_index=False)["count"].sum()

labels = list(pd.unique(agg[["source","target"]].values.ravel()))
label_idx = {l:i for i,l in enumerate(labels)}
source_idx = [label_idx[s] for s in agg["source"]]
target_idx = [label_idx[t] for t in agg["target"]]
values = agg["count"].tolist()

fig = go.Figure(data=[go.Sankey(
    node=dict(label=labels),
    link=dict(source=source_idx, target=target_idx, value=values)
)])
fig.update_layout(title_text="Aggregated subreddit migration flows", font_size=10)
fig.show()
