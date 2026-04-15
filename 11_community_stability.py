import networkx as nx
import igraph as ig
import leidenalg
import numpy as np
from sklearn.metrics import normalized_mutual_info_score
import json
import os

def nx_to_igraph(G):
    nodes = list(G.nodes())
    node_index = {n: i for i, n in enumerate(nodes)}
    ig_edges = [(node_index[u], node_index[v]) for u, v in G.edges()]
    ig_graph = ig.Graph(n=len(nodes), edges=ig_edges, directed=False)
    return ig_graph, nodes

def run_leiden(ig_graph, seed):
    partition = leidenalg.find_partition(
        ig_graph,
        leidenalg.ModularityVertexPartition,
        seed=seed
    )
    labels = [0] * ig_graph.vcount()
    for comm_id, members in enumerate(partition):
        for i in members:
            labels[i] = comm_id
    return labels

def main():
    print("=" * 60)
    print("COMMUNITY STABILITY ANALYSIS")
    print("=" * 60)

    G = nx.read_gexf("data/s230_graph.gexf")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    ig_graph, nodes = nx_to_igraph(G)

    # Run Leiden 100 times with different seeds
    N_RUNS = 100
    print(f"\nRunning Leiden {N_RUNS} times...")
    all_labels = []
    n_communities = []

    for seed in range(N_RUNS):
        labels = run_leiden(ig_graph, seed)
        all_labels.append(labels)
        n_communities.append(len(set(labels)))

    print(f"Done. Computing NMI between all pairs...")

    # Compute pairwise NMI
    nmi_scores = []
    for i in range(N_RUNS):
        for j in range(i + 1, N_RUNS):
            nmi = normalized_mutual_info_score(all_labels[i], all_labels[j])
            nmi_scores.append(nmi)

    mean_nmi = np.mean(nmi_scores)
    std_nmi = np.std(nmi_scores)
    min_nmi = np.min(nmi_scores)
    max_nmi = np.max(nmi_scores)

    print(f"\n{'=' * 60}")
    print(f"STABILITY RESULTS")
    print(f"{'=' * 60}")
    print(f"Runs: {N_RUNS}")
    print(f"Mean NMI:   {mean_nmi:.4f}")
    print(f"Std NMI:    {std_nmi:.4f}")
    print(f"Min NMI:    {min_nmi:.4f}")
    print(f"Max NMI:    {max_nmi:.4f}")
    print(f"\nCommunity count across runs:")
    print(f"  Mean:  {np.mean(n_communities):.1f}")
    print(f"  Min:   {np.min(n_communities)}")
    print(f"  Max:   {np.max(n_communities)}")
    print(f"  Std:   {np.std(n_communities):.2f}")

    # Interpret
    print(f"\nINTERPRETATION:")
    if mean_nmi >= 0.90:
        print(f"  HIGH stability (NMI >= 0.90)")
        print(f"  Community structure is robust and algorithm-independent.")
        print(f"  Strong evidence for genuine doctrinal communities.")
    elif mean_nmi >= 0.75:
        print(f"  MODERATE stability (0.75 <= NMI < 0.90)")
        print(f"  Core communities are stable; peripheral assignments vary.")
        print(f"  Report with caveat about boundary cases.")
    else:
        print(f"  LOW stability (NMI < 0.75)")
        print(f"  Community assignments are algorithm-dependent.")
        print(f"  Interpret communities with caution.")

    # Save results
    results = {
        "n_runs": N_RUNS,
        "mean_nmi": round(mean_nmi, 4),
        "std_nmi": round(std_nmi, 4),
        "min_nmi": round(min_nmi, 4),
        "max_nmi": round(max_nmi, 4),
        "mean_communities": round(float(np.mean(n_communities)), 1),
        "min_communities": int(np.min(n_communities)),
        "max_communities": int(np.max(n_communities)),
        "std_communities": round(float(np.std(n_communities)), 2),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/community_stability.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to data/community_stability.json")

if __name__ == "__main__":
    main()