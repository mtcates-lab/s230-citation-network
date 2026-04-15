import json
import glob
import numpy as np
import networkx as nx
import pandas as pd
from collections import defaultdict
from scipy.spatial.distance import jensenshannon
import os

def build_circuit_distribution(G, circuit_cases, all_nodes, node_to_idx, year_cutoff):
    """Build citation distribution for a circuit using only cases up to year_cutoff."""
    n_nodes = len(all_nodes)
    citation_counts = np.zeros(n_nodes)
    total = 0

    for case in circuit_cases:
        case_year = int(G.nodes[case].get("date", "9999")[:4])
        if case_year > year_cutoff:
            continue
        for cited in G.successors(case):
            cited_year = int(G.nodes[cited].get("date", "9999")[:4])
            if cited_year > year_cutoff:
                continue
            idx = node_to_idx.get(cited, -1)
            if idx >= 0:
                citation_counts[idx] += 1
                total += 1

    if total == 0:
        return None
    dist = citation_counts / total
    return dist

def compute_mean_jsd(distributions):
    """Compute mean pairwise JSD across a set of distributions."""
    circuits = list(distributions.keys())
    if len(circuits) < 2:
        return None
    jsds = []
    for i, c1 in enumerate(circuits):
        for c2 in circuits[i+1:]:
            p = distributions[c1] + 1e-10
            q = distributions[c2] + 1e-10
            p = p / p.sum()
            q = q / q.sum()
            jsd = jensenshannon(p, q, base=2)
            jsds.append(jsd)
    return np.mean(jsds) if jsds else None

def main():
    print("=" * 60)
    print("TEMPORAL JENSEN-SHANNON DIVERGENCE ANALYSIS")
    print("=" * 60)

    G = nx.read_gexf("data/s230_graph.gexf")
    metrics = pd.read_csv("data/s230_metrics.csv")

    node_court = {}
    for _, row in metrics.iterrows():
        node_court[str(row["node_id"])] = row["court"]

    all_nodes = sorted(list(G.nodes()))
    node_to_idx = {n: i for i, n in enumerate(all_nodes)}

    circuits = ["ca1", "ca2", "ca3", "ca4", "ca5",
                "ca6", "ca7", "ca8", "ca9", "ca10",
                "ca11", "cadc"]

    # Group cases by circuit
    circuit_cases = defaultdict(list)
    for n in G.nodes():
        court = node_court.get(n, "")
        if court in circuits:
            circuit_cases[court].append(n)

    # Compute temporal JSD annually
    years = list(range(2000, 2026))
    temporal_results = []

    print(f"\nComputing annual JSD from 2000 to 2025...")
    print(f"{'Year':<6} {'Mean JSD':<12} {'Circuits':<10} {'Notes'}")
    print("-" * 60)

    for year in years:
        distributions = {}
        for circuit, cases in circuit_cases.items():
            dist = build_circuit_distribution(
                G, cases, all_nodes, node_to_idx, year
            )
            if dist is not None:
                distributions[circuit] = dist

        mean_jsd = compute_mean_jsd(distributions)
        n_circuits = len(distributions)

        # Identify structural break years
        notes = ""
        if year == 2008:
            notes = "<-- Roommates.com en banc"
        elif year == 2018:
            notes = "<-- FOSTA enacted"
        elif year == 2023:
            notes = "<-- Gonzalez (SCOTUS)"

        if mean_jsd is not None:
            print(f"{year:<6} {mean_jsd:<12.4f} {n_circuits:<10} {notes}")
            temporal_results.append({
                "year": year,
                "mean_jsd": round(float(mean_jsd), 4),
                "n_circuits": n_circuits
            })
        else:
            print(f"{year:<6} {'N/A':<12} {n_circuits:<10}")

    # Find structural breaks — years with largest year-over-year JSD change
    print(f"\n{'=' * 60}")
    print("YEAR-OVER-YEAR JSD CHANGES")
    print("=" * 60)

    changes = []
    for i in range(1, len(temporal_results)):
        prev = temporal_results[i-1]
        curr = temporal_results[i]
        delta = curr["mean_jsd"] - prev["mean_jsd"]
        changes.append({
            "year": curr["year"],
            "delta": round(delta, 4),
            "prev_jsd": prev["mean_jsd"],
            "curr_jsd": curr["mean_jsd"]
        })
        direction = "↑" if delta > 0 else "↓"
        print(f"  {curr['year']}: {direction} {abs(delta):.4f} "
              f"({prev['mean_jsd']:.4f} → {curr['mean_jsd']:.4f})")

    # Largest increases in divergence
    changes_sorted = sorted(changes, key=lambda x: x["delta"], reverse=True)
    print(f"\nLargest increases in circuit divergence:")
    for c in changes_sorted[:3]:
        print(f"  {c['year']}: +{c['delta']:.4f}")

    print(f"\nLargest decreases in circuit divergence (convergence):")
    for c in changes_sorted[-3:]:
        print(f"  {c['year']}: {c['delta']:.4f}")

    # Pairwise temporal JSD for key circuit pairs
    print(f"\n{'=' * 60}")
    print("TEMPORAL JSD FOR KEY CIRCUIT PAIRS")
    print("=" * 60)

    key_pairs = [("ca9", "ca7"), ("ca9", "ca4"), ("ca2", "ca9"), ("ca5", "ca9")]
    print(f"\n{'Year':<6}" + "".join(f"{p[0]}-{p[1]:>10}" for p in key_pairs))
    print("-" * 50)

    pair_results = defaultdict(list)
    for year in years:
        row = f"{year:<6}"
        for c1, c2 in key_pairs:
            d1 = build_circuit_distribution(
                G, circuit_cases[c1], all_nodes, node_to_idx, year)
            d2 = build_circuit_distribution(
                G, circuit_cases[c2], all_nodes, node_to_idx, year)
            if d1 is not None and d2 is not None:
                p = d1 + 1e-10
                q = d2 + 1e-10
                jsd = jensenshannon(p/p.sum(), q/q.sum(), base=2)
                row += f"{jsd:>12.4f}"
                pair_results[f"{c1}-{c2}"].append(
                    {"year": year, "jsd": round(float(jsd), 4)})
            else:
                row += f"{'N/A':>12}"
        print(row)

    # Save
    results = {
        "annual_mean_jsd": temporal_results,
        "year_over_year_changes": changes,
        "largest_divergence_years": [c["year"] for c in changes_sorted[:3]],
        "key_pair_temporal": dict(pair_results)
    }
    os.makedirs("data", exist_ok=True)
    with open("data/temporal_jsd.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to data/temporal_jsd.json")

if __name__ == "__main__":
    main()