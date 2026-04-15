import json
import networkx as nx
import pandas as pd
import glob
import os

def load_graph():
    path = "data/s230_graph.gexf"
    if not os.path.exists(path):
        raise FileNotFoundError("Graph not found. Run 02_build_graph.py first.")
    print(f"Loading graph from {path}")
    return nx.read_gexf(path)

def compute_metrics(G):
    print("Computing PageRank...")
    pagerank = nx.pagerank(G, alpha=0.85)

    print("Computing in-degree centrality...")
    in_degree = dict(G.in_degree())

    print("Computing betweenness centrality (approximate)...")
    betweenness = nx.betweenness_centrality(G, k=50, normalized=True)

    print("Computing community detection (Leiden algorithm)...")
    import igraph as ig
    import leidenalg

    nodes = list(G.nodes())
    node_index = {n: i for i, n in enumerate(nodes)}
    ig_edges = [(node_index[u], node_index[v]) for u, v in G.edges()]
    ig_graph = ig.Graph(n=len(nodes), edges=ig_edges, directed=False)

    leiden_partition = leidenalg.find_partition(
        ig_graph,
        leidenalg.ModularityVertexPartition,
        seed=42
    )

    partition = {}
    for comm_id, members in enumerate(leiden_partition):
        for i in members:
            partition[nodes[i]] = comm_id

    return pagerank, in_degree, betweenness, partition

def save_metrics(G, pagerank, in_degree, betweenness, partition):
    rows = []
    for node_id in G.nodes():
        attrs = G.nodes[node_id]
        rows.append({
            "node_id": node_id,
            "case_name": attrs.get("name", ""),
            "court": attrs.get("court", ""),
            "date": attrs.get("date", ""),
            "url": attrs.get("url", ""),
            "pagerank": round(pagerank.get(node_id, 0), 6),
            "in_degree": in_degree.get(node_id, 0),
            "betweenness": round(betweenness.get(node_id, 0), 6),
            "community": partition.get(node_id, -1),
        })
    df = pd.DataFrame(rows)
    df = df.sort_values("pagerank", ascending=False)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/s230_metrics.csv", index=False)
    print(f"Metrics saved to data/s230_metrics.csv")
    return df

def print_results(df):
    print("\n" + "=" * 70)
    print("TOP 20 CASES BY PAGERANK")
    print("=" * 70)
    print(f"{'Rank':<5} {'PageRank':<10} {'In-Deg':<8} {'Comm':<6} {'Court':<10} {'Year':<6} Case")
    print("-" * 70)
    for i, row in df.head(20).iterrows():
        year = str(row["date"])[:4] if row["date"] else "????"
        name = str(row["case_name"])[:45]
        print(f"  {df.index.get_loc(i)+1:<4} {row['pagerank']:<10.6f} {row['in_degree']:<8} {row['community']:<6} {row['court']:<10} {year:<6} {name}")
    print("\n" + "=" * 70)
    print("COMMUNITY STRUCTURE")
    print("=" * 70)
    communities = df.groupby("community")
    for comm_id, group in communities:
        top = group.sort_values("pagerank", ascending=False).head(3)
        print(f"\nCommunity {comm_id} ({len(group)} cases):")
        for _, row in top.iterrows():
            year = str(row["date"])[:4] if row["date"] else "????"
            print(f"  - {row['case_name'][:60]} ({row['court']}, {year})")

if __name__ == "__main__":
    print("=" * 70)
    print("COMPUTING § 230 NETWORK METRICS")
    print("=" * 70)
    G = load_graph()
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    pagerank, in_degree, betweenness, partition = compute_metrics(G)
    df = save_metrics(G, pagerank, in_degree, betweenness, partition)
    print_results(df)
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
    print("Metrics saved to: data/s230_metrics.csv")
    print("Graph files in:   data/s230_graph.gexf")
    print("\nNext step: open data/s230_graph.gexf in Gephi to visualize.")