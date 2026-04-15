import json
import numpy as np
import networkx as nx
import pandas as pd
import igraph as ig
import leidenalg
from scipy.stats import kendalltau, spearmanr
from sklearn.metrics import normalized_mutual_info_score
from collections import defaultdict
import os

def get_leiden_partition(G, seed=42):
    nodes = list(G.nodes())
    node_index = {n: i for i, n in enumerate(nodes)}
    ig_edges = [(node_index[u], node_index[v]) for u, v in G.edges()]
    ig_graph = ig.Graph(n=len(nodes), edges=ig_edges, directed=False)
    try:
        partition = leidenalg.find_partition(
            ig_graph, leidenalg.ModularityVertexPartition, seed=seed)
        return {nodes[i]: comm_id
                for comm_id, members in enumerate(partition)
                for i in members}
    except Exception:
        return {n: 0 for n in nodes}

def run_sensitivity_trial(G, removal_fraction, seed):
    """Remove a fraction of edges randomly and recompute metrics."""
    np.random.seed(seed)
    edges = list(G.edges())
    n_remove = int(len(edges) * removal_fraction)
    edges_to_remove = np.random.choice(len(edges), n_remove, replace=False)
    removed = {edges[i] for i in edges_to_remove}

    H = G.copy()
    H.remove_edges_from(removed)

    pr = nx.pagerank(H, alpha=0.85)
    community = get_leiden_partition(H)

    return pr, community

def main():
    print("=" * 65)
    print("EDGE SENSITIVITY ANALYSIS")
    print("=" * 65)

    G = nx.read_gexf("data/s230_graph.gexf")
    metrics = pd.read_csv("data/s230_metrics.csv")

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Baseline
    pr_baseline = nx.pagerank(G, alpha=0.85)
    comm_baseline = get_leiden_partition(G)

    node_names = {str(row["node_id"]): row["case_name"][:35]
                  for _, row in metrics.iterrows()}

    top10_baseline = [node for node, _ in
                      sorted(pr_baseline.items(),
                             key=lambda x: x[1], reverse=True)[:10]]

    print(f"\nBaseline top 10:")
    for i, node in enumerate(top10_baseline):
        print(f"  {i+1}. {node_names.get(node, node)}")

    # Run sensitivity trials
    removal_fractions = [0.10, 0.20, 0.30]
    n_trials = 20
    results = {}

    for frac in removal_fractions:
        print(f"\n{'=' * 65}")
        print(f"Removing {int(frac*100)}% of edges ({n_trials} trials)")
        print("=" * 65)

        tau_scores = []
        nmi_scores = []
        top10_overlaps = []
        top1_stable = []

        for trial in range(n_trials):
            pr_trial, comm_trial = run_sensitivity_trial(G, frac, seed=trial)

            # PageRank rank correlation
            nodes = list(G.nodes())
            baseline_ranks = sorted(nodes,
                                    key=lambda n: pr_baseline.get(n, 0),
                                    reverse=True)
            trial_ranks = sorted(nodes,
                                 key=lambda n: pr_trial.get(n, 0),
                                 reverse=True)
            rank_pos_b = {n: i for i, n in enumerate(baseline_ranks)}
            rank_pos_t = {n: i for i, n in enumerate(trial_ranks)}
            r_b = [rank_pos_b[n] for n in nodes]
            r_t = [rank_pos_t[n] for n in nodes]
            tau, _ = kendalltau(r_b, r_t)
            tau_scores.append(tau)

            # Top 10 overlap
            top10_trial = set(sorted(pr_trial.keys(),
                                     key=lambda n: pr_trial.get(n, 0),
                                     reverse=True)[:10])
            overlap = len(set(top10_baseline) & top10_trial)
            top10_overlaps.append(overlap)

            # Top 1 stability (Zeran stays #1?)
            top1 = max(pr_trial, key=pr_trial.get)
            top1_stable.append(1 if top1 == top10_baseline[0] else 0)

            # Community NMI
            shared = [n for n in nodes
                      if n in comm_baseline and n in comm_trial]
            if shared:
                labels_b = [comm_baseline[n] for n in shared]
                labels_t = [comm_trial[n] for n in shared]
                nmi = normalized_mutual_info_score(labels_b, labels_t)
                nmi_scores.append(nmi)

        mean_tau = np.mean(tau_scores)
        std_tau = np.std(tau_scores)
        mean_nmi = np.mean(nmi_scores)
        std_nmi = np.std(nmi_scores)
        mean_overlap = np.mean(top10_overlaps)
        top1_rate = np.mean(top1_stable)

        print(f"PageRank rank correlation (τ):  {mean_tau:.4f} ± {std_tau:.4f}")
        print(f"Community NMI:                  {mean_nmi:.4f} ± {std_nmi:.4f}")
        print(f"Top 10 overlap (out of 10):     {mean_overlap:.1f} ± "
              f"{np.std(top10_overlaps):.1f}")
        print(f"Top node (#1) stability rate:   {top1_rate:.0%}")

        if mean_tau >= 0.90:
            pr_verdict = "STABLE"
        elif mean_tau >= 0.75:
            pr_verdict = "MODERATELY STABLE"
        else:
            pr_verdict = "UNSTABLE"

        if mean_nmi >= 0.70:
            comm_verdict = "STABLE"
        elif mean_nmi >= 0.50:
            comm_verdict = "MODERATELY STABLE"
        else:
            comm_verdict = "UNSTABLE"

        print(f"PageRank verdict:               {pr_verdict}")
        print(f"Community verdict:              {comm_verdict}")

        results[frac] = {
            "removal_fraction": frac,
            "n_trials": n_trials,
            "mean_kendall_tau": round(float(mean_tau), 4),
            "std_kendall_tau": round(float(std_tau), 4),
            "mean_community_nmi": round(float(mean_nmi), 4),
            "std_community_nmi": round(float(std_nmi), 4),
            "mean_top10_overlap": round(float(mean_overlap), 2),
            "top1_stability_rate": round(float(top1_rate), 4),
            "pagerank_verdict": pr_verdict,
            "community_verdict": comm_verdict
        }

    # Summary table
    print(f"\n{'=' * 65}")
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("=" * 65)
    print(f"\n{'Removal':<10} {'PR τ':<12} {'Comm NMI':<12} "
          f"{'Top10':<10} {'Top1 stable'}")
    print("-" * 55)
    for frac, r in results.items():
        print(f"{int(frac*100)}%       "
              f"{r['mean_kendall_tau']:.4f}      "
              f"{r['mean_community_nmi']:.4f}      "
              f"{r['mean_top10_overlap']:.1f}/10     "
              f"{r['top1_stability_rate']:.0%}")

    # Overall verdict
    print(f"\nOVERALL VERDICT:")
    all_tau = [r["mean_kendall_tau"] for r in results.values()]
    all_nmi = [r["mean_community_nmi"] for r in results.values()]
    if min(all_tau) >= 0.85 and min(all_nmi) >= 0.60:
        print("  ROBUST — findings are stable under edge removal up to 30%.")
        print("  Network structure is not an artifact of CourtListener coverage.")
    elif min(all_tau) >= 0.75:
        print("  MODERATELY ROBUST — core rankings stable; communities vary.")
        print("  Report sensitivity statistics and note boundary sensitivity.")
    else:
        print("  SENSITIVE — findings may be affected by edge incompleteness.")

    # Save
    os.makedirs("data", exist_ok=True)
    with open("data/edge_sensitivity.json", "w") as f:
        json.dump({
            "baseline_edges": G.number_of_edges(),
            "baseline_nodes": G.number_of_nodes(),
            "trials_per_condition": n_trials,
            "results": {str(k): v for k, v in results.items()}
        }, f, indent=2)
    print(f"\nResults saved to data/edge_sensitivity.json")

if __name__ == "__main__":
    main()