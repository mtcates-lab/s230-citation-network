import networkx as nx
import pandas as pd
import numpy as np
from scipy.stats import kendalltau, spearmanr
import json
import os

def main():
    print("=" * 60)
    print("PAGERANK ROBUSTNESS CHECK")
    print("=" * 60)

    G = nx.read_gexf("data/s230_graph.gexf")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    damping_factors = [0.75, 0.85, 0.90, 0.95]
    all_rankings = {}

    for alpha in damping_factors:
        pr = nx.pagerank(G, alpha=alpha)
        ranked = sorted(pr.items(), key=lambda x: x[1], reverse=True)
        all_rankings[alpha] = {node: rank+1 for rank, (node, _) in enumerate(ranked)}

    # Get node names
    case_names = {node_id: G.nodes[node_id].get('name', node_id)[:45]
                  for node_id in G.nodes()}

    # Print top 15 comparison table
    print(f"\n{'Case':<46} " + " ".join(f"α={a}" for a in damping_factors))
    print("-" * 80)

    baseline = all_rankings[0.85]
    top15_nodes = sorted(baseline.items(), key=lambda x: x[1])[:15]

    for node_id, base_rank in top15_nodes:
        name = case_names.get(node_id, node_id)
        row = f"{name:<46}"
        for alpha in damping_factors:
            rank = all_rankings[alpha].get(node_id, 99)
            row += f"  {rank:>4}"
        print(row)

    # Compute rank correlations between damping factors
    print(f"\n{'=' * 60}")
    print("RANK CORRELATIONS (Kendall's τ)")
    print("=" * 60)

    nodes = list(G.nodes())
    results = {}

    for i, alpha1 in enumerate(damping_factors):
        for alpha2 in damping_factors[i+1:]:
            ranks1 = [all_rankings[alpha1][n] for n in nodes]
            ranks2 = [all_rankings[alpha2][n] for n in nodes]
            tau, p_val = kendalltau(ranks1, ranks2)
            spear, _ = spearmanr(ranks1, ranks2)
            key = f"α={alpha1} vs α={alpha2}"
            results[key] = {
                "kendall_tau": round(tau, 4),
                "spearman_r": round(spear, 4),
                "p_value": round(p_val, 6)
            }
            print(f"  {key}: τ={tau:.4f}, ρ={spear:.4f}, p={p_val:.4f}")

    # Check top 10 stability
    print(f"\n{'=' * 60}")
    print("TOP 10 STABILITY ACROSS DAMPING FACTORS")
    print("=" * 60)

    top10_sets = {}
    for alpha in damping_factors:
        ranked = sorted(all_rankings[alpha].items(), key=lambda x: x[1])
        top10_sets[alpha] = {node for node, rank in ranked[:10]}

    baseline_top10 = top10_sets[0.85]
    print(f"Baseline top 10 (α=0.85):")
    baseline_ranked = sorted(all_rankings[0.85].items(), key=lambda x: x[1])[:10]
    for node_id, rank in baseline_ranked:
        print(f"  {rank}. {case_names.get(node_id, node_id)}")

    print(f"\nTop 10 overlap with baseline (α=0.85):")
    for alpha in damping_factors:
        if alpha == 0.85:
            continue
        overlap = len(top10_sets[alpha] & baseline_top10)
        print(f"  α={alpha}: {overlap}/10 cases in common")

    # Interpretation
    mean_tau = np.mean([v["kendall_tau"] for v in results.values()])
    print(f"\nINTERPRETATION:")
    if mean_tau >= 0.90:
        print(f"  HIGH robustness (mean τ={mean_tau:.3f})")
        print(f"  Rankings are stable across damping factors.")
    elif mean_tau >= 0.75:
        print(f"  MODERATE robustness (mean τ={mean_tau:.3f})")
        print(f"  Core rankings stable; some variation in lower ranks.")
    else:
        print(f"  LOW robustness (mean τ={mean_tau:.3f})")
        print(f"  Rankings are sensitive to damping factor choice.")

    # Save
    os.makedirs("data", exist_ok=True)
    with open("data/pagerank_robustness.json", "w") as f:
        json.dump({
            "damping_factors": damping_factors,
            "correlations": results,
            "mean_kendall_tau": round(mean_tau, 4),
            "top10_overlap": {
                str(alpha): len(top10_sets[alpha] & baseline_top10)
                for alpha in damping_factors if alpha != 0.85
            }
        }, f, indent=2)

    print(f"\nResults saved to data/pagerank_robustness.json")

if __name__ == "__main__":
    main()