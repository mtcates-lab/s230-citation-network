import json
import glob
import networkx as nx
import pandas as pd
import numpy as np
import igraph as ig
import leidenalg
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import normalized_mutual_info_score
import os

def nx_to_igraph(G):
    nodes = list(G.nodes())
    node_index = {n: i for i, n in enumerate(nodes)}
    ig_edges = [(node_index[u], node_index[v]) for u, v in G.edges()]
    ig_graph = ig.Graph(n=len(nodes), edges=ig_edges, directed=False)
    return ig_graph, nodes

def get_leiden_partition(G, seed=42):
    ig_graph, nodes = nx_to_igraph(G)
    partition = leidenalg.find_partition(
        ig_graph, leidenalg.ModularityVertexPartition, seed=seed)
    community_map = {}
    for comm_id, members in enumerate(partition):
        for i in members:
            community_map[nodes[i]] = comm_id
    return community_map

def compute_pagerank_correlation(pr1, pr2):
    from scipy.stats import kendalltau
    nodes = list(set(pr1.keys()) & set(pr2.keys()))
    ranks1 = sorted(nodes, key=lambda n: pr1.get(n, 0), reverse=True)
    ranks2 = sorted(nodes, key=lambda n: pr2.get(n, 0), reverse=True)
    rank_pos1 = {n: i for i, n in enumerate(ranks1)}
    rank_pos2 = {n: i for i, n in enumerate(ranks2)}
    r1 = [rank_pos1[n] for n in nodes]
    r2 = [rank_pos2[n] for n in nodes]
    tau, _ = kendalltau(r1, r2)
    return tau

def main():
    print("=" * 65)
    print("DUAL CORPUS ANALYSIS")
    print("Full corpus vs Restricted corpus (pure § 230(c)(1) only)")
    print("=" * 65)

    # Load full corpus
    files = glob.glob("raw_data/s230_validated_*.json")
    latest = max(files)
    with open(latest) as f:
        data = json.load(f)

    all_cases = data["results"]

    # Define restricted corpus — exclude mixed and non-c1 cases
    # Restricted = platform_wins or platform_loses under § 230(c)(1)
    # Exclude: mixed outcomes, § 230(c)(2), § 230(e)/FOSTA cases
    EXCLUDE_PRIMARY_BASIS = {"s230c2_immunity", "s230e_fosta"}
    EXCLUDE_OUTCOME = {"mixed"}

    restricted_ids = set()
    excluded_cases = []
    for case in all_cases:
        cid = str(case.get("cluster_id"))
        primary_basis = case.get("primary_basis", "s230c_immunity")
        outcome = case.get("outcome", "unknown")
        holding_status = case.get("holding_status", "definitive")

        if primary_basis in EXCLUDE_PRIMARY_BASIS:
            excluded_cases.append((cid, case.get("caseName","")[:50],
                                   "non-c1 primary basis"))
        elif holding_status == "qualified":
            excluded_cases.append((cid, case.get("caseName","")[:50],
                                   "qualified holding"))
        else:
            restricted_ids.add(cid)

    # Load full graph
    G_full = nx.read_gexf("data/s230_graph.gexf")

    # Build restricted subgraph
    G_restricted = G_full.subgraph(
        [n for n in G_full.nodes() if n in restricted_ids]
    ).copy()

    print(f"\nFull corpus:       {G_full.number_of_nodes()} nodes, "
          f"{G_full.number_of_edges()} edges")
    print(f"Restricted corpus: {G_restricted.number_of_nodes()} nodes, "
          f"{G_restricted.number_of_edges()} edges")

    print(f"\nExcluded from restricted corpus ({len(excluded_cases)} cases):")
    for cid, name, reason in excluded_cases:
        print(f"  {name} — {reason}")

    # Compute PageRank on both
    pr_full = nx.pagerank(G_full, alpha=0.85)
    pr_restricted = nx.pagerank(G_restricted, alpha=0.85)

    # Top 10 comparison
    print(f"\n{'=' * 65}")
    print("TOP 10 PAGERANK COMPARISON")
    print("=" * 65)

    top10_full = sorted(pr_full.items(), key=lambda x: x[1], reverse=True)[:10]
    top10_restricted = sorted(pr_restricted.items(),
                              key=lambda x: x[1], reverse=True)[:10]

    node_names = {n: G_full.nodes[n].get("name","")[:40]
                  for n in G_full.nodes()}

    print(f"\n{'Rank':<5} {'Full Corpus':<42} {'Restricted Corpus':<42}")
    print("-" * 90)
    for i in range(10):
        f_node, f_pr = top10_full[i]
        r_node, r_pr = top10_restricted[i] if i < len(top10_restricted) else ("", 0)
        f_name = node_names.get(f_node, f_node)[:40]
        r_name = node_names.get(r_node, r_node)[:40] if r_node else ""
        print(f"{i+1:<5} {f_name:<42} {r_name:<42}")

    # Rank correlation between full and restricted
    tau = compute_pagerank_correlation(pr_full, pr_restricted)
    print(f"\nPageRank rank correlation (Kendall τ): {tau:.4f}")

    # Community comparison
    print(f"\n{'=' * 65}")
    print("COMMUNITY STRUCTURE COMPARISON")
    print("=" * 65)

    comm_full = get_leiden_partition(G_full)
    comm_restricted = get_leiden_partition(G_restricted)

    n_comm_full = len(set(comm_full.values()))
    n_comm_restricted = len(set(comm_restricted.values()))
    print(f"Full corpus communities:       {n_comm_full}")
    print(f"Restricted corpus communities: {n_comm_restricted}")

    # NMI between full and restricted community assignments
    # (on the intersection of nodes)
    shared_nodes = list(set(comm_full.keys()) & set(comm_restricted.keys()))
    labels_full = [comm_full[n] for n in shared_nodes]
    labels_restricted = [comm_restricted[n] for n in shared_nodes]
    nmi = normalized_mutual_info_score(labels_full, labels_restricted)
    print(f"Community assignment NMI (full vs restricted): {nmi:.4f}")

    if nmi >= 0.80:
        print("  HIGH agreement — community structure is robust to corpus boundaries.")
    elif nmi >= 0.60:
        print("  MODERATE agreement — core communities stable; periphery shifts.")
    else:
        print("  LOW agreement — communities sensitive to corpus boundary decisions.")

    # Key structural metrics comparison
    print(f"\n{'=' * 65}")
    print("STRUCTURAL METRICS COMPARISON")
    print("=" * 65)

    def gini(values):
        n = len(values)
        s = sorted(values)
        total = sum(s)
        if total == 0:
            return 0
        return (2 * sum((i+1)*s[i] for i in range(n))) / (n * total) - (n+1)/n

    pr_full_vals = list(pr_full.values())
    pr_rest_vals = list(pr_restricted.values())

    print(f"{'Metric':<35} {'Full':<15} {'Restricted'}")
    print("-" * 65)
    print(f"{'Nodes':<35} {G_full.number_of_nodes():<15} "
          f"{G_restricted.number_of_nodes()}")
    print(f"{'Edges':<35} {G_full.number_of_edges():<15} "
          f"{G_restricted.number_of_edges()}")
    print(f"{'Density':<35} {nx.density(G_full):<15.4f} "
          f"{nx.density(G_restricted):.4f}")
    print(f"{'PageRank Gini':<35} {gini(pr_full_vals):<15.4f} "
          f"{gini(pr_rest_vals):.4f}")
    print(f"{'Communities (Leiden)':<35} {n_comm_full:<15} "
          f"{n_comm_restricted}")
    print(f"{'Top node PageRank':<35} {max(pr_full_vals):<15.4f} "
          f"{max(pr_rest_vals):.4f}")
    print(f"{'Rank correlation (τ)':<35} {tau:<15.4f} {'(baseline)'}")

    # Interpretation
    print(f"\n{'=' * 65}")
    print("INTERPRETATION")
    print("=" * 65)
    if tau >= 0.90 and nmi >= 0.70:
        print("  ROBUST: Core findings hold across corpus boundary definitions.")
        print("  The full corpus and restricted corpus produce equivalent")
        print("  structural insights. Corpus boundary decisions do not")
        print("  materially affect conclusions.")
    elif tau >= 0.75:
        print("  MODERATELY ROBUST: Rankings stable; communities vary slightly.")
        print("  Report both corpora and note boundary sensitivity.")
    else:
        print("  SENSITIVE: Results depend on corpus boundary decisions.")
        print("  Report both analyses and discuss differences carefully.")

    # Save
    results = {
        "full_corpus": {
            "nodes": G_full.number_of_nodes(),
            "edges": G_full.number_of_edges(),
            "density": round(nx.density(G_full), 4),
            "gini": round(gini(pr_full_vals), 4),
            "communities": n_comm_full,
            "top_pagerank": round(max(pr_full_vals), 4)
        },
        "restricted_corpus": {
            "nodes": G_restricted.number_of_nodes(),
            "edges": G_restricted.number_of_edges(),
            "density": round(nx.density(G_restricted), 4),
            "gini": round(gini(pr_rest_vals), 4),
            "communities": n_comm_restricted,
            "top_pagerank": round(max(pr_rest_vals), 4)
        },
        "pagerank_kendall_tau": round(tau, 4),
        "community_nmi": round(nmi, 4),
        "excluded_cases": [
            {"cluster_id": cid, "name": name, "reason": reason}
            for cid, name, reason in excluded_cases
        ]
    }

    os.makedirs("data", exist_ok=True)
    with open("data/dual_corpus_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to data/dual_corpus_analysis.json")

if __name__ == "__main__":
    main()