import json
import glob
import os
import ast
import networkx as nx

def load_corpus():
    files = glob.glob("raw_data/s230_validated_*.json")
    latest = max(files)
    with open(latest) as f:
        data = json.load(f)
    return data["results"]

def build_lookup_from_gexf(G):
    """Build citation string -> cluster_id lookup directly from GEXF node data."""
    lookup = {}
    for node_id, attrs in G.nodes(data=True):
        cid = int(node_id)
        citation_field = attrs.get("citation", "")
        if citation_field:
            try:
                citations = ast.literal_eval(citation_field)
                for cite in citations:
                    cite_str = cite.strip().lower()
                    # Only index standard reporter citations (volume reporter page)
                    parts = cite_str.split()
                    if len(parts) >= 3 and parts[0].isdigit():
                        key = f"{parts[0]} {parts[1]} {parts[2]}"
                        lookup[key] = cid
            except Exception:
                pass
    return lookup

def main():
    G = nx.read_gexf("data/s230_graph.gexf")
    corpus_ids = {int(n) for n in G.nodes()}
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    lookup = build_lookup_from_gexf(G)
    print(f"Citation lookup: {len(lookup)} citation strings indexed")

    sample = list(lookup.items())[:5]
    for k, v in sample:
        print(f"  '{k}' -> {v}")

    existing_edges = set()
    for u, v in G.edges():
        existing_edges.add((int(u), int(v)))
    print(f"\nExisting edges: {len(existing_edges)}")

    with open("data/eyecite_results.json") as f:
        eyecite_results = json.load(f)

    print(f"\nResolving {sum(r['citations_found'] for r in eyecite_results)} citations...")
    print("=" * 60)

    new_edges = set()
    resolved = 0
    unresolved = 0

    for case_result in eyecite_results:
        source_id = case_result["cluster_id"]
        if source_id not in corpus_ids:
            continue

        for cite_str in case_result.get("corpus_citations", []):
            parts = cite_str.strip().lower().split()
            if len(parts) < 3:
                unresolved += 1
                continue
            key = f"{parts[0]} {parts[1]} {parts[2]}"
            target_id = lookup.get(key)
            if target_id and target_id in corpus_ids and target_id != source_id:
                new_edges.add((source_id, target_id))
                resolved += 1
            else:
                unresolved += 1

    truly_new = new_edges - existing_edges
    already_captured = new_edges & existing_edges

    print(f"Resolved to corpus nodes: {resolved}")
    print(f"Unresolved: {unresolved}")
    print(f"Total edges from Eyecite: {len(new_edges)}")
    print(f"Already in graph: {len(already_captured)}")
    print(f"Genuinely new edges: {len(truly_new)}")

    # CourtListener cites field coverage rate:
    # Fraction of Eyecite-extracted edges already present in the
    # CourtListener cites field. This is an overlap ratio between
    # two extraction methods, not a recall rate against a ground truth.
    total_possible = len(existing_edges) + len(truly_new)
    coverage_rate = len(existing_edges) / total_possible if total_possible > 0 else 0
    print(f"\nCourtListener cites field coverage rate: {coverage_rate:.1%}")
    print(f"  (fraction of Eyecite-extracted edges already in CourtListener cites field)")
    print(f"  (overlap ratio between two extraction methods, not recall against ground truth)")
    print(f"Edge improvement from Eyecite full-text extraction: +{len(truly_new)} edges")

    output = {
        "stats": {
            "existing_edges": len(existing_edges),
            "eyecite_edges": len(new_edges),
            "already_captured": len(already_captured),
            "genuinely_new": len(truly_new),
            "courtlistener_cites_field_coverage_rate": round(coverage_rate, 4),
        },
        "truly_new_edges": [
            {"source": s, "target": t} for s, t in sorted(truly_new)
        ]
    }

    os.makedirs("data", exist_ok=True)
    with open("data/eyecite_edges.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to data/eyecite_edges.json")
    print("Next: run 10_merge_edges.py to add new edges to graph")

if __name__ == "__main__":
    main()