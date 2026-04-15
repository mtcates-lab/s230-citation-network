import networkx as nx
import igraph as ig
import leidenalg
import numpy as np
import json
import os
from collections import defaultdict

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
    labels = {}
    for comm_id, members in enumerate(partition):
        for i in members:
            labels[i] = comm_id
    return labels

def build_coassignment_matrix(all_labels, n_nodes, N_RUNS):
    """Build matrix where entry [i,j] = fraction of runs where i and j are in same community."""
    matrix = np.zeros((n_nodes, n_nodes))
    for labels in all_labels:
        for i in range(n_nodes):
            for j in range(i, n_nodes):
                if labels[i] == labels[j]:
                    matrix[i][j] += 1
                    matrix[j][i] += 1
    # Diagonal
    for i in range(n_nodes):
        matrix[i][i] = N_RUNS
    matrix = matrix / N_RUNS
    return matrix

def assign_consensus_communities(coassignment_matrix, nodes, threshold=0.80):
    """
    Assign consensus communities using single-linkage clustering
    on the co-assignment matrix. Cases that co-cluster >= threshold
    fraction of the time are in the same consensus community.
    """
    n = len(nodes)
    assigned = [-1] * n
    comm_id = 0

    for i in range(n):
        if assigned[i] == -1:
            assigned[i] = comm_id
            for j in range(i + 1, n):
                if assigned[j] == -1 and coassignment_matrix[i][j] >= threshold:
                    assigned[j] = comm_id
            comm_id += 1

    return assigned

def main():
    print("=" * 60)
    print("CONSENSUS PARTITION ANALYSIS")
    print("=" * 60)

    G = nx.read_gexf("data/s230_graph.gexf")
    nodes = list(G.nodes())
    n_nodes = len(nodes)
    print(f"Graph: {n_nodes} nodes, {G.number_of_edges()} edges")

    ig_graph, nodes = nx_to_igraph(G)

    # Run Leiden 100 times
    N_RUNS = 100
    print(f"\nRunning Leiden {N_RUNS} times to build co-assignment matrix...")
    all_labels = []
    for seed in range(N_RUNS):
        labels = run_leiden(ig_graph, seed)
        all_labels.append(labels)

    # Build co-assignment matrix
    print("Building co-assignment matrix...")
    coassignment = build_coassignment_matrix(all_labels, n_nodes, N_RUNS)

    # Assign consensus communities at 80% threshold
    THRESHOLD = 0.80
    print(f"Assigning consensus communities (threshold={THRESHOLD})...")
    consensus_labels = assign_consensus_communities(coassignment, nodes, THRESHOLD)

    # Build community groups
    communities = defaultdict(list)
    for i, comm_id in enumerate(consensus_labels):
        communities[comm_id].append(nodes[i])

    # Load case names from graph
    case_names = {node_id: G.nodes[node_id].get('name', node_id)
                  for node_id in G.nodes()}
    case_courts = {node_id: G.nodes[node_id].get('court', '')
                   for node_id in G.nodes()}
    case_dates = {node_id: G.nodes[node_id].get('date', '')
                  for node_id in G.nodes()}

    # Load pagerank for sorting
    pagerank = nx.pagerank(G, alpha=0.85)

    print(f"\n{'=' * 60}")
    print(f"CONSENSUS COMMUNITY STRUCTURE (threshold={THRESHOLD})")
    print(f"{'=' * 60}")
    print(f"Number of consensus communities: {len(communities)}")

    for comm_id in sorted(communities.keys()):
        members = communities[comm_id]
        print(f"\nCommunity {comm_id} ({len(members)} cases):")
        # Sort by pagerank
        sorted_members = sorted(members, key=lambda x: pagerank.get(x, 0), reverse=True)
        for node_id in sorted_members[:5]:
            name = case_names.get(node_id, node_id)[:55]
            court = case_courts.get(node_id, '')
            year = str(case_dates.get(node_id, ''))[:4]
            pr = pagerank.get(node_id, 0)
            print(f"  [{court:6}] {year}  {name}")
            print(f"           PageRank: {pr:.4f}")

    # Identify boundary cases — low max co-assignment
    print(f"\n{'=' * 60}")
    print(f"BOUNDARY CASES (max co-assignment with any community < {THRESHOLD})")
    print(f"{'=' * 60}")
    boundary_cases = []
    for i, node_id in enumerate(nodes):
        max_coassign = max(coassignment[i][j] for j in range(n_nodes) if j != i)
        if max_coassign < THRESHOLD:
            boundary_cases.append({
                "node_id": node_id,
                "name": case_names.get(node_id, '')[:60],
                "court": case_courts.get(node_id, ''),
                "max_coassignment": round(float(max_coassign), 3)
            })

    boundary_cases.sort(key=lambda x: x["max_coassignment"])
    for bc in boundary_cases:
        print(f"  {bc['max_coassignment']:.3f}  [{bc['court']:6}]  {bc['name']}")

    # Save results
    output = {
        "threshold": THRESHOLD,
        "n_runs": N_RUNS,
        "n_communities": len(communities),
        "community_assignments": {
            nodes[i]: consensus_labels[i] for i in range(n_nodes)
        },
        "boundary_cases": boundary_cases,
        "coassignment_stats": {
            "mean": round(float(np.mean(coassignment)), 3),
            "median": round(float(np.median(coassignment)), 3),
        }
    }

    os.makedirs("data", exist_ok=True)
    with open("data/consensus_partition.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to data/consensus_partition.json")

if __name__ == "__main__":
    main()