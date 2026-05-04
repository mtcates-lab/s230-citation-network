import sys
import os

# PIPELINE GUARD: This script builds the baseline graph from CourtListener edges only.
# After 10_merge_edges.py has run, the graph file contains eyecite-augmented edges.
# Running this script after the merge will overwrite the augmented graph.
# If eyecite_edges.json exists and shows a merged edge count, abort.
if os.path.exists('data/eyecite_edges.json'):
    import json
    with open('data/eyecite_edges.json') as f:
        stats = json.load(f).get('stats', {})
    if stats.get('final_graph_edges', 0) > stats.get('courtlistener_edge_count', 0):
        print('ERROR: Eyecite merge already completed. Do not run 02_build_graph.py after 10_merge_edges.py.')
        print('Run 03_compute_metrics.py directly.')
        sys.exit(1)

import json
import networkx as nx
import pandas as pd
import os
import glob

def load_latest_raw_data():
    files = glob.glob("raw_data/s230_validated_*.json")
    if not files:
        raise FileNotFoundError("No raw data files found. Run 01_collect_data.py first.")
    latest = max(files)
    print(f"Loading: {latest}")
    with open(latest) as f:
        data = json.load(f)
    return data["results"]

def build_graph(cases):
    G = nx.DiGraph()

    cluster_to_case = {}
    for case in cases:
        cluster_id = case.get("cluster_id")
        if cluster_id:
            cluster_to_case[cluster_id] = case

    print(f"Adding {len(cases)} nodes...")
    for case in cases:
        cluster_id = case.get("cluster_id")
        if not cluster_id:
            continue
        G.add_node(
            cluster_id,
            name=case.get("caseName", "Unknown"),
            court=case.get("court_id", ""),
            date=case.get("dateFiled", ""),
            cite_count=case.get("citeCount", 0),
            citation=str(case.get("citation", "")),
            url="https://courtlistener.com" + case.get("absolute_url", ""),
        )

    print(f"Adding edges from citations...")
    edges_added = 0
    for case in cases:
        source_id = case.get("cluster_id")
        if not source_id:
            continue
        opinions = case.get("opinions", [])
        for opinion in opinions:
            cited_ids = opinion.get("cites", [])
            for cited_id in cited_ids:
                if cited_id in cluster_to_case:
                    G.add_edge(source_id, cited_id)
                    edges_added += 1

    print(f"Edges added: {edges_added}")
    return G

def save_graph(G):
    os.makedirs("data", exist_ok=True)
    nx.write_gexf(G, "data/s230_graph.gexf")
    nx.write_graphml(G, "data/s230_graph.graphml")
    print(f"Graph saved to data/s230_graph.gexf and data/s230_graph.graphml")

def print_summary(G):
    print("\n" + "=" * 50)
    print("GRAPH SUMMARY")
    print("=" * 50)
    print(f"Nodes (cases):     {G.number_of_nodes()}")
    print(f"Edges (citations): {G.number_of_edges()}")
    print(f"Is a DAG:          {nx.is_directed_acyclic_graph(G)}")

    in_degrees = dict(G.in_degree())
    top_cited = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\nTop 10 most cited cases:")
    for node_id, count in top_cited:
        name = G.nodes[node_id].get("name", "Unknown")
        court = G.nodes[node_id].get("court", "")
        date = G.nodes[node_id].get("date", "")
        print(f"  {count:3d} citations | {date[:4]} | {court:8} | {name[:60]}")

if __name__ == "__main__":
    print("=" * 50)
    print("BUILDING § 230 CITATION GRAPH")
    print("=" * 50)

    cases = load_latest_raw_data()
    G = build_graph(cases)
    save_graph(G)
    print_summary(G)

    print("\nNext step: run 03_compute_metrics.py")