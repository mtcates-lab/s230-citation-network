import json
import numpy as np
import networkx as nx
import pandas as pd
import os
from collections import defaultdict

def poincare_distance(u, v):
    """Compute hyperbolic distance between two points in Poincaré disk."""
    norm_u = np.dot(u, u)
    norm_v = np.dot(v, v)
    diff = u - v
    norm_diff = np.dot(diff, diff)
    arg = 1 + 2 * norm_diff / ((1 - norm_u) * (1 - norm_v) + 1e-10)
    return np.arccosh(np.clip(arg, 1 + 1e-10, None))

def poincare_grad(u, v, connected=True):
    """Riemannian gradient for Poincaré embedding."""
    norm_u_sq = np.dot(u, u)
    norm_v_sq = np.dot(v, v)
    diff = u - v
    norm_diff_sq = np.dot(diff, diff)

    alpha = 1 - norm_u_sq
    beta = 1 - norm_v_sq
    gamma = 1 + 2 * norm_diff_sq / (alpha * beta + 1e-10)
    gamma = np.clip(gamma, 1 + 1e-10, None)

    # Euclidean gradient
    if connected:
        grad = (4 / (beta * np.sqrt(gamma**2 - 1) + 1e-10)) * (
            (norm_v_sq - 2*np.dot(u, v) + 1) / (alpha**2 + 1e-10) * u - v / alpha
        )
    else:
        grad = -(4 / (beta * np.sqrt(gamma**2 - 1) + 1e-10)) * (
            (norm_v_sq - 2*np.dot(u, v) + 1) / (alpha**2 + 1e-10) * u - v / alpha
        )

    # Riemannian correction
    riemannian_factor = (alpha**2) / 4
    return riemannian_factor * grad

def project_to_disk(x, eps=1e-5):
    """Project point back into Poincaré disk (norm < 1)."""
    norm = np.linalg.norm(x)
    if norm >= 1:
        x = x / norm * (1 - eps)
    return x

def embed_poincare(G, dim=2, epochs=500, lr=0.01, n_negatives=5, seed=42):
    """Embed graph nodes in Poincaré disk using SGD."""
    np.random.seed(seed)
    nodes = list(G.nodes())
    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    # Initialize embeddings near origin
    embeddings = np.random.uniform(-0.001, 0.001, (n, dim))

    # Build edge list
    edges = [(node_idx[u], node_idx[v]) for u, v in G.edges()
             if u in node_idx and v in node_idx]

    # Also add reverse edges (undirected for embedding)
    all_edges = set()
    for u, v in edges:
        all_edges.add((u, v))
        all_edges.add((v, u))

    edge_list = list(all_edges)
    all_node_ids = list(range(n))

    print(f"Embedding {n} nodes with {len(edge_list)} edges...")
    print(f"Running {epochs} epochs...")

    losses = []
    for epoch in range(epochs):
        np.random.shuffle(edge_list)
        total_loss = 0

        for u_idx, v_idx in edge_list:
            # Positive pair
            u = embeddings[u_idx].copy()
            v = embeddings[v_idx].copy()

            d_pos = poincare_distance(u, v)
            loss = np.log(np.exp(-d_pos) + 1e-10)

            # Negative samples
            neg_losses = []
            for _ in range(n_negatives):
                neg_idx = np.random.choice(all_node_ids)
                if neg_idx != v_idx:
                    neg = embeddings[neg_idx].copy()
                    d_neg = poincare_distance(u, neg)
                    neg_losses.append(np.exp(-d_neg))

            if neg_losses:
                loss -= np.log(sum(neg_losses) + 1e-10)

            total_loss += loss

            # Gradient update for u
            grad_u = poincare_grad(u, v, connected=True)
            embeddings[u_idx] = project_to_disk(
                embeddings[u_idx] - lr * grad_u)

        losses.append(total_loss / len(edge_list))

        if (epoch + 1) % 100 == 0:
            print(f"  Epoch {epoch+1}/{epochs}: loss={losses[-1]:.4f}")

    return embeddings, nodes, losses

def compute_hyperbolic_depth(embeddings):
    """Distance from origin = depth in hierarchy."""
    return np.linalg.norm(embeddings, axis=1)

def main():
    print("=" * 65)
    print("HYPERBOLIC EMBEDDING OF § 230 CITATION NETWORK")
    print("Poincaré Disk Embedding")
    print("=" * 65)

    G = nx.read_gexf("data/s230_graph.gexf")
    metrics = pd.read_csv("data/s230_metrics.csv")
    pr = nx.pagerank(G, alpha=0.85)

    node_names = {str(row["node_id"]): row["case_name"][:40]
                  for _, row in metrics.iterrows()}
    node_courts = {str(row["node_id"]): row["court"]
                   for _, row in metrics.iterrows()}
    node_dates = {str(row["node_id"]): str(row["date"])[:4]
                  for _, row in metrics.iterrows()}
    node_community = {str(row["node_id"]): row["community"]
                      for _, row in metrics.iterrows()}

    # Run embedding
    embeddings, nodes, losses = embed_poincare(
        G, dim=2, epochs=300, lr=0.005, n_negatives=10, seed=42)

    # Compute hyperbolic depth (distance from origin)
    depths = compute_hyperbolic_depth(embeddings)

    print(f"\n{'=' * 65}")
    print("HYPERBOLIC DEPTH ANALYSIS")
    print("(Distance from origin = hierarchical depth)")
    print("(Closer to center = more foundational)")
    print("=" * 65)

    # Rank by depth
    depth_ranking = sorted(zip(nodes, depths, embeddings),
                           key=lambda x: x[1])

    print(f"\n{'Rank':<5} {'Depth':<8} {'Court':<7} {'Year':<6} Case")
    print("-" * 70)

    print("\nMOST FOUNDATIONAL (closest to center of Poincaré disk):")
    for i, (node, depth, emb) in enumerate(depth_ranking[:10]):
        name = node_names.get(node, node)[:45]
        court = node_courts.get(node, "")
        year = node_dates.get(node, "")
        pr_val = pr.get(node, 0)
        print(f"{i+1:<5} {depth:<8.4f} {court:<7} {year:<6} {name}")
        print(f"       PageRank: {pr_val:.4f}")

    print("\nMOST PERIPHERAL (furthest from center):")
    for i, (node, depth, emb) in enumerate(depth_ranking[-10:][::-1]):
        name = node_names.get(node, node)[:45]
        court = node_courts.get(node, "")
        year = node_dates.get(node, "")
        pr_val = pr.get(node, 0)
        print(f"{i+1:<5} {depth:<8.4f} {court:<7} {year:<6} {name}")

    # Correlation between PageRank and hyperbolic depth
    pr_values = np.array([pr.get(node, 0) for node in nodes])
    from scipy.stats import spearmanr
    corr, pval = spearmanr(-depths, pr_values)
    print(f"\n{'=' * 65}")
    print(f"PAGERANK vs HYPERBOLIC DEPTH CORRELATION")
    print(f"{'=' * 65}")
    print(f"Spearman correlation (depth vs PageRank): {corr:.4f} (p={pval:.4f})")
    print(f"Interpretation: {'Strong' if abs(corr) > 0.6 else 'Moderate' if abs(corr) > 0.4 else 'Weak'} "
          f"{'positive' if corr > 0 else 'negative'} association")
    print(f"Cases closer to center tend to have "
          f"{'higher' if corr > 0 else 'lower'} PageRank")

    # Community analysis in hyperbolic space
    print(f"\n{'=' * 65}")
    print("MEAN HYPERBOLIC DEPTH BY COMMUNITY")
    print("=" * 65)

    comm_depths = defaultdict(list)
    for node, depth in zip(nodes, depths):
        comm = node_community.get(node, -1)
        comm_depths[comm].append(depth)

    for comm_id in sorted(comm_depths.keys()):
        d = comm_depths[comm_id]
        print(f"  Community {comm_id}: mean depth={np.mean(d):.4f}, "
              f"std={np.std(d):.4f}, n={len(d)}")

    # Save results
    results = {
        "embedding_params": {
            "dim": 2,
            "epochs": 300,
            "lr": 0.005,
            "n_negatives": 10,
            "seed": 42
        },
        "node_embeddings": [
            {
                "node_id": node,
                "case_name": node_names.get(node, ""),
                "court": node_courts.get(node, ""),
                "year": node_dates.get(node, ""),
                "community": int(node_community.get(node, -1)),
                "embedding_x": float(embeddings[i][0]),
                "embedding_y": float(embeddings[i][1]),
                "hyperbolic_depth": float(depths[i]),
                "pagerank": float(pr.get(node, 0))
            }
            for i, node in enumerate(nodes)
        ],
        "depth_pagerank_correlation": round(float(corr), 4),
        "depth_pagerank_pvalue": round(float(pval), 4),
        "community_depth_stats": {
            str(k): {
                "mean_depth": round(float(np.mean(v)), 4),
                "std_depth": round(float(np.std(v)), 4),
                "n": len(v)
            }
            for k, v in comm_depths.items()
        }
    }

    os.makedirs("data", exist_ok=True)
    with open("data/hyperbolic_embedding.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nEmbedding saved to data/hyperbolic_embedding.json")
    print("Final training loss:", round(losses[-1], 4))

if __name__ == "__main__":
    main()