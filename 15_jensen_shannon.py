import json
import glob
import numpy as np
import networkx as nx
import pandas as pd
from collections import defaultdict
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy
import os

def main():
    print("=" * 60)
    print("JENSEN-SHANNON DIVERGENCE BETWEEN CIRCUITS")
    print("(JSD in bits, base 2)")
    print("=" * 60)

    G = nx.read_gexf("data/s230_graph.gexf")
    metrics = pd.read_csv("data/s230_metrics.csv")

    node_court = {}
    node_date = {}
    node_name = {}
    for _, row in metrics.iterrows():
        nid = str(row["node_id"])
        node_court[nid] = row["court"]
        node_date[nid] = str(row["date"])[:4]
        node_name[nid] = str(row["case_name"])[:40]

    circuits = ["ca1", "ca2", "ca3", "ca4", "ca5",
                "ca6", "ca7", "ca8", "ca9", "ca10",
                "ca11", "cadc", "scotus"]

    all_nodes = sorted(list(G.nodes()))
    node_to_idx = {n: i for i, n in enumerate(all_nodes)}
    n_nodes = len(all_nodes)

    circuit_distributions = {}
    circuit_case_counts = {}

    for circuit in circuits:
        circuit_cases = [n for n in G.nodes()
                        if node_court.get(n, "") == circuit]

        if len(circuit_cases) < 2:
            continue

        circuit_case_counts[circuit] = len(circuit_cases)

        citation_counts = np.zeros(n_nodes)
        total_citations = 0

        for case in circuit_cases:
            for cited in G.successors(case):
                idx = node_to_idx.get(cited, -1)
                if idx >= 0:
                    citation_counts[idx] += 1
                    total_citations += 1

        if total_citations == 0:
            continue

        dist = citation_counts / total_citations
        circuit_distributions[circuit] = dist

    active_circuits = list(circuit_distributions.keys())
    print(f"\nCircuits with sufficient cases (n >= 2): {active_circuits}")
    print(f"Cases per circuit:")
    for c in active_circuits:
        print(f"  {c:8}: {circuit_case_counts[c]} cases")

    n_circuits = len(active_circuits)
    jsd_matrix = np.zeros((n_circuits, n_circuits))

    for i, c1 in enumerate(active_circuits):
        for j, c2 in enumerate(active_circuits):
            if i != j:
                p = circuit_distributions[c1]
                q = circuit_distributions[c2]
                p_smooth = p + 1e-10
                q_smooth = q + 1e-10
                p_smooth = p_smooth / p_smooth.sum()
                q_smooth = q_smooth / q_smooth.sum()
                jsd = jensenshannon(p_smooth, q_smooth, base=2)
                jsd_matrix[i][j] = jsd

    print(f"\n{'=' * 60}")
    print("PAIRWISE JENSEN-SHANNON DIVERGENCE MATRIX")
    print("(JSD in bits, base 2; lower = more similar citation patterns)")
    print("=" * 60)

    header = f"{'':8}" + "".join(f"{c:8}" for c in active_circuits)
    print(header)
    print("-" * len(header))

    for i, c1 in enumerate(active_circuits):
        row = f"{c1:8}"
        for j, c2 in enumerate(active_circuits):
            if i == j:
                row += f"{'—':>8}"
            else:
                row += f"{jsd_matrix[i][j]:8.4f}"
        print(row)

    print(f"\n{'=' * 60}")
    print("MOST SIMILAR CIRCUIT PAIRS (lowest JSD, bits base 2)")
    print("=" * 60)

    pairs = []
    for i, c1 in enumerate(active_circuits):
        for j, c2 in enumerate(active_circuits):
            if i < j:
                pairs.append((jsd_matrix[i][j], c1, c2))

    pairs.sort()
    print("Most similar (most aligned citation patterns):")
    for jsd, c1, c2 in pairs[:5]:
        print(f"  {c1} vs {c2}: JSD={jsd:.4f} bits")

    print("\nMost divergent (most different citation patterns):")
    for jsd, c1, c2 in pairs[-5:]:
        print(f"  {c1} vs {c2}: JSD={jsd:.4f} bits")

    # Mean pairwise JSD
    all_jsd_vals = [jsd_matrix[i][j]
                    for i in range(n_circuits)
                    for j in range(n_circuits) if i != j]
    mean_jsd = np.mean(all_jsd_vals)
    print(f"\nMean pairwise JSD: {mean_jsd:.4f} bits (base 2)")
    print(f"Range: {min(all_jsd_vals):.4f} - {max(all_jsd_vals):.4f} bits")

    print(f"\n{'=' * 60}")
    print("TOP 3 MOST CITED CASES PER CIRCUIT")
    print("=" * 60)

    for circuit in active_circuits:
        dist = circuit_distributions[circuit]
        top_idx = np.argsort(dist)[::-1][:3]
        print(f"\n  {circuit}:")
        for idx in top_idx:
            if dist[idx] > 0:
                node_id = all_nodes[idx]
                name = node_name.get(node_id, node_id)
                print(f"    {dist[idx]:.3f}  {name}")

    results = {
        "units": "bits (base 2)",
        "circuits": active_circuits,
        "circuit_case_counts": circuit_case_counts,
        "mean_pairwise_jsd": round(float(mean_jsd), 4),
        "jsd_matrix": jsd_matrix.tolist(),
        "most_similar_pairs": [
            {"circuit1": c1, "circuit2": c2, "jsd_bits": round(jsd, 4)}
            for jsd, c1, c2 in pairs[:5]
        ],
        "most_divergent_pairs": [
            {"circuit1": c1, "circuit2": c2, "jsd_bits": round(jsd, 4)}
            for jsd, c1, c2 in pairs[-5:]
        ]
    }

    os.makedirs("data", exist_ok=True)
    with open("data/jsd_circuits.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to data/jsd_circuits.json")

if __name__ == "__main__":
    main()