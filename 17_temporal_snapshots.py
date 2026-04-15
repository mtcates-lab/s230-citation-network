import json
import glob
import numpy as np
import networkx as nx
import pandas as pd
import igraph as ig
import leidenalg
from collections import defaultdict
import os

def build_snapshot(G, year_cutoff):
    nodes_in_snapshot = [
        n for n in G.nodes()
        if int(G.nodes[n].get("date", "9999")[:4]) <= year_cutoff
    ]
    return G.subgraph(nodes_in_snapshot).copy()

def gini_coefficient(values):
    n = len(values)
    if n == 0:
        return 0
    sorted_vals = sorted(values)
    total = sum(sorted_vals)
    if total == 0:
        return 0
    cumsum = sum((i + 1) * sorted_vals[i] for i in range(n))
    return (2 * cumsum) / (n * total) - (n + 1) / n

def compute_snapshot_metrics(H):
    if H.number_of_nodes() == 0:
        return None

    n_nodes = H.number_of_nodes()
    n_edges = H.number_of_edges()

    pr = nx.pagerank(H, alpha=0.85)
    pr_values = list(pr.values())
    top_pr = max(pr_values)
    top_node = max(pr, key=pr.get)
    top_name = H.nodes[top_node].get("name", top_node)[:35]
    gini = gini_coefficient(pr_values)

    nodes = list(H.nodes())
    node_index = {n: i for i, n in enumerate(nodes)}
    ig_edges = [(node_index[u], node_index[v]) for u, v in H.edges()]
    ig_graph = ig.Graph(n=len(nodes), edges=ig_edges, directed=False)
    try:
        partition = leidenalg.find_partition(
            ig_graph, leidenalg.ModularityVertexPartition, seed=42)
        n_communities = len(partition)
    except Exception:
        n_communities = 0

    density = nx.density(H)
    in_degrees = [d for _, d in H.in_degree()]
    mean_in_degree = sum(in_degrees) / len(in_degrees) if in_degrees else 0

    return {
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "density": round(density, 4),
        "mean_in_degree": round(float(mean_in_degree), 3),
        "top_pagerank": round(top_pr, 4),
        "top_pagerank_node": top_name,
        "pagerank_gini": round(float(gini), 4),
        "n_communities": n_communities,
    }

def main():
    print("=" * 70)
    print("TEMPORAL NETWORK SNAPSHOTS")
    print("=" * 70)

    G = nx.read_gexf("data/s230_graph.gexf")
    print(f"Full graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    years = list(range(1997, 2026))
    results = []

    print(f"\n{'Year':<6} {'Nodes':<7} {'Edges':<7} {'Density':<9} "
          f"{'Top PR':<9} {'Gini':<7} {'Comms':<7} Top Case")
    print("-" * 90)

    for year in years:
        H = build_snapshot(G, year)
        if H.number_of_nodes() < 2:
            continue
        m = compute_snapshot_metrics(H)
        if m is None:
            continue

        print(f"{year:<6} {m['n_nodes']:<7} {m['n_edges']:<7} "
              f"{m['density']:<9.4f} {m['top_pagerank']:<9.4f} "
              f"{m['pagerank_gini']:<7.4f} {m['n_communities']:<7} "
              f"{m['top_pagerank_node']}")

        results.append({"year": year, **m})

    print(f"\n{'=' * 70}")
    print("KEY STRUCTURAL TRANSITIONS")
    print("=" * 70)

    df = pd.DataFrame(results)

    max_density_year = df.loc[df["density"].idxmax(), "year"]
    print(f"Maximum network density: {df['density'].max():.4f} ({max_density_year})")
    print(f"PageRank Gini range: {df['pagerank_gini'].min():.4f} - "
          f"{df['pagerank_gini'].max():.4f}")

    print(f"\nCommunity count by year:")
    for _, row in df.iterrows():
        if row["year"] in [1997, 2000, 2003, 2005, 2008,
                           2010, 2015, 2018, 2020, 2023, 2025]:
            print(f"  {int(row['year'])}: {int(row['n_communities'])} communities, "
                  f"{int(row['n_nodes'])} cases, Gini={row['pagerank_gini']:.3f}")

    print(f"\nCorpus growth:")
    for yr in [2003, 2008, 2018, 2025]:
        row = df[df["year"] == yr]
        if not row.empty:
            print(f"  Through {yr}: {int(row['n_nodes'].values[0])} cases")

    os.makedirs("data", exist_ok=True)
    with open("data/temporal_snapshots.json", "w") as f:
        json.dump(results, f, indent=2)
    df.to_csv("data/temporal_snapshots.csv", index=False)
    print(f"\nResults saved to data/temporal_snapshots.json and .csv")

if __name__ == "__main__":
    main()