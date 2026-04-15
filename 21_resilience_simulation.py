import json
import glob
import networkx as nx
import numpy as np
import pandas as pd
import os

def simulate_targeted_removal(G, removal_order, metric="largest_component"):
    """Remove nodes in order and track network degradation."""
    H = G.copy()
    results = []
    n_original = H.number_of_nodes()

    for i, node in enumerate(removal_order):
        if node not in H:
            continue

        # Metrics before removal
        undirected = H.to_undirected()
        if undirected.number_of_nodes() > 0:
            components = list(nx.connected_components(undirected))
            largest = len(max(components, key=len))
            n_components = len(components)
        else:
            largest = 0
            n_components = 0

        pr = nx.pagerank(H, alpha=0.85) if H.number_of_nodes() > 1 else {}
        top_pr = max(pr.values()) if pr else 0
        top_node = max(pr, key=pr.get) if pr else ""
        top_name = H.nodes[top_node].get("name", "")[:35] if top_node else ""

        results.append({
            "step": i,
            "removed_node": node,
            "removed_name": G.nodes[node].get("name", "")[:35],
            "nodes_remaining": H.number_of_nodes(),
            "edges_remaining": H.number_of_edges(),
            "largest_component": largest,
            "largest_component_pct": round(largest / n_original * 100, 1),
            "n_components": n_components,
            "top_pagerank": round(top_pr, 4),
            "top_node_name": top_name,
        })

        H.remove_node(node)

    return results

def main():
    print("=" * 70)
    print("NETWORK RESILIENCE SIMULATION")
    print("=" * 70)

    G = nx.read_gexf("data/s230_graph.gexf")
    metrics = pd.read_csv("data/s230_metrics.csv")
    n_original = G.number_of_nodes()

    print(f"Graph: {n_original} nodes, {G.number_of_edges()} edges")

    # Build node name and PageRank lookup
    node_names = {str(row["node_id"]): row["case_name"][:40]
                  for _, row in metrics.iterrows()}
    pr_full = nx.pagerank(G, alpha=0.85)

    # --- SIMULATION 1: Targeted attack on highest-PageRank nodes ---
    print(f"\n{'=' * 70}")
    print("SIMULATION 1: Targeted removal by PageRank (highest first)")
    print("Simulates: overruling or legislative displacement of key precedents")
    print("=" * 70)

    removal_by_pagerank = sorted(pr_full.keys(),
                                  key=lambda n: pr_full[n], reverse=True)
    results_targeted = simulate_targeted_removal(G, removal_by_pagerank[:20])

    print(f"\n{'Step':<5} {'Removed Case':<37} {'Nodes':<7} {'Largest CC':<12} "
          f"{'Components':<12} {'Top PR'}")
    print("-" * 85)
    for r in results_targeted[:15]:
        print(f"{r['step']:<5} {r['removed_name']:<37} "
              f"{r['nodes_remaining']:<7} "
              f"{r['largest_component_pct']:>6.1f}%     "
              f"{r['n_components']:<12} {r['top_pagerank']:.4f}")

    # --- SIMULATION 2: Random removal (baseline) ---
    print(f"\n{'=' * 70}")
    print("SIMULATION 2: Random node removal (baseline)")
    print("Simulates: random case law development / no targeted reform")
    print("=" * 70)

    np.random.seed(42)
    random_order = list(np.random.permutation(list(G.nodes())))
    results_random = simulate_targeted_removal(G, random_order[:20])

    print(f"\n{'Step':<5} {'Nodes':<7} {'Largest CC':<12} {'Components'}")
    print("-" * 40)
    for r in results_random[:15]:
        print(f"{r['step']:<5} {r['nodes_remaining']:<7} "
              f"{r['largest_component_pct']:>6.1f}%     "
              f"{r['n_components']}")

    # --- SIMULATION 3: Reform proposal scenarios ---
    print(f"\n{'=' * 70}")
    print("SIMULATION 3: Reform proposal scenarios")
    print("=" * 70)

    # Load corpus for metadata
    files = glob.glob("raw_data/s230_validated_*.json")
    latest = max(files)
    with open(latest) as f:
        data = json.load(f)

    cases_by_id = {str(c["cluster_id"]): c for c in data["results"]}

    # Scenario A: FOSTA expansion — remove all FOSTA/e(5) cases
    fosta_nodes = [
        str(c["cluster_id"]) for c in data["results"]
        if c.get("primary_basis") == "s230e_fosta"
    ]

    # Scenario B: Algorithm liability — remove cases where platform loses
    # on algorithmic recommendation grounds
    algo_lose_nodes = [
        str(c["cluster_id"]) for c in data["results"]
        if c.get("outcome") == "platform_loses"
        and any(term in c.get("caseName","").lower()
                for term in ["tiktok", "snap", "salesforce",
                             "accusearch", "leadclick"])
    ]

    # Scenario C: Zeran overruled — remove Zeran and measure cascade
    zeran_node = "748185"

    # Scenario D: Remove all platform_loses cases
    # (simulating strong § 230 reform restoring immunity)
    platform_loses_nodes = [
        str(c["cluster_id"]) for c in data["results"]
        if c.get("outcome") == "platform_loses"
    ]

    scenarios = [
        ("A: FOSTA cases removed", fosta_nodes),
        ("B: Algorithmic liability losses removed", algo_lose_nodes),
        ("C: Zeran overruled (single node)", [zeran_node]),
        ("D: All platform-loses cases removed", platform_loses_nodes),
    ]

    scenario_results = []
    for scenario_name, nodes_to_remove in scenarios:
        H = G.copy()
        nodes_removed = 0
        for node in nodes_to_remove:
            if node in H:
                H.remove_node(node)
                nodes_removed += 1

        undirected = H.to_undirected()
        components = list(nx.connected_components(undirected))
        largest = len(max(components, key=len)) if components else 0
        pr_new = nx.pagerank(H, alpha=0.85) if H.number_of_nodes() > 1 else {}
        top_node = max(pr_new, key=pr_new.get) if pr_new else ""
        top_name = H.nodes[top_node].get("name","")[:35] if top_node else ""

        result = {
            "scenario": scenario_name,
            "nodes_removed": nodes_removed,
            "nodes_remaining": H.number_of_nodes(),
            "edges_remaining": H.number_of_edges(),
            "largest_component": largest,
            "largest_component_pct": round(largest / n_original * 100, 1),
            "n_components": len(components),
            "new_top_node": top_name,
            "new_top_pr": round(max(pr_new.values()), 4) if pr_new else 0,
        }
        scenario_results.append(result)

        print(f"\n  Scenario {scenario_name}:")
        print(f"    Nodes removed: {nodes_removed}")
        print(f"    Nodes remaining: {H.number_of_nodes()}")
        print(f"    Edges remaining: {H.number_of_edges()}")
        print(f"    Largest component: {largest} ({result['largest_component_pct']}%)")
        print(f"    Components: {len(components)}")
        print(f"    New top node: {top_name} (PR={result['new_top_pr']:.4f})")

    # Robustness comparison
    print(f"\n{'=' * 70}")
    print("ROBUSTNESS COMPARISON")
    print("(after removing top 5 nodes by PageRank)")
    print("=" * 70)

    targeted_5 = results_targeted[5]
    random_5 = results_random[5]
    print(f"  Targeted removal: largest CC = "
          f"{targeted_5['largest_component_pct']}% of original")
    print(f"  Random removal:   largest CC = "
          f"{random_5['largest_component_pct']}% of original")

    if targeted_5["largest_component_pct"] < random_5["largest_component_pct"]:
        diff = random_5["largest_component_pct"] - \
               targeted_5["largest_component_pct"]
        print(f"\n  Network is {diff:.1f}% more vulnerable to targeted attack")
        print(f"  than to random removal — consistent with scale-free")
        print(f"  network properties.")

    # Save results
    output = {
        "targeted_removal": results_targeted,
        "random_removal": results_random,
        "reform_scenarios": scenario_results,
        "robustness_summary": {
            "targeted_top5_largest_cc_pct":
                targeted_5["largest_component_pct"],
            "random_top5_largest_cc_pct":
                random_5["largest_component_pct"],
        }
    }

    os.makedirs("data", exist_ok=True)
    with open("data/resilience_simulation.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to data/resilience_simulation.json")

if __name__ == "__main__":
    main()
