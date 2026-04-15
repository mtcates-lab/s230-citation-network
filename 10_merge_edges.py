import json
import networkx as nx
import os

def main():
    # Load current graph
    G = nx.read_gexf("data/s230_graph.gexf")
    print(f"Graph before merge: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Load new edges
    with open("data/eyecite_edges.json") as f:
        data = json.load(f)

    new_edges = data["truly_new_edges"]
    print(f"New edges to add: {len(new_edges)}")

    # Add new edges
    added = 0
    skipped = 0
    for edge in new_edges:
        source = str(edge["source"])
        target = str(edge["target"])
        if source in G.nodes() and target in G.nodes():
            if not G.has_edge(source, target):
                G.add_edge(source, target)
                added += 1
        else:
            skipped += 1

    print(f"Edges added: {added}")
    print(f"Edges skipped (node not in graph): {skipped}")
    print(f"Graph after merge: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Verify still a DAG
    if nx.is_directed_acyclic_graph(G):
        print("DAG check: PASSED")
    else:
        print("DAG check: FAILED — cycles detected, reverting")
        return

    # Save updated graph
    nx.write_gexf(G, "data/s230_graph.gexf")
    nx.write_graphml(G, "data/s230_graph.graphml")
    print("Graph saved.")

if __name__ == "__main__":
    main()