import json
import glob
import networkx as nx
import numpy as np
from sklearn.metrics import mutual_info_score, normalized_mutual_info_score
from collections import Counter, defaultdict
import pandas as pd

def main():
    print("=" * 60)
    print("MUTUAL INFORMATION: COMMUNITY vs OUTCOME")
    print("=" * 60)

    G = nx.read_gexf("data/s230_graph.gexf")

    files = glob.glob("raw_data/s230_validated_*.json")
    latest = max(files)
    with open(latest) as f:
        data = json.load(f)

    metrics = pd.read_csv("data/s230_metrics.csv")
    community_map = dict(zip(metrics["node_id"], metrics["community"]))

    cases = []
    for case in data["results"]:
        cid = case.get("cluster_id")
        outcome = case.get("outcome", "unknown")
        community = community_map.get(cid, -1)
        if outcome != "unknown" and community >= 0:
            cases.append({
                "cluster_id": cid,
                "case_name": case.get("caseName", "")[:45],
                "outcome": outcome,
                "community": community,
                "court": case.get("court_id", ""),
                "year": str(case.get("dateFiled", ""))[:4]
            })

    print(f"Cases with outcome and community: {len(cases)}")

    outcome_labels = {"platform_wins": 0, "platform_loses": 1, "mixed": 2}
    outcomes = [outcome_labels[c["outcome"]] for c in cases]
    communities = [c["community"] for c in cases]

    mi = mutual_info_score(communities, outcomes)
    nmi = normalized_mutual_info_score(communities, outcomes)

    print(f"\nMutual Information (MI):             {mi:.4f} bits")
    print(f"Normalized Mutual Information (NMI): {nmi:.4f}")

    print(f"\n{'=' * 60}")
    print("OUTCOME DISTRIBUTION BY COMMUNITY")
    print("=" * 60)

    comm_outcomes = defaultdict(Counter)
    for c in cases:
        comm_outcomes[c["community"]][c["outcome"]] += 1

    for comm_id in sorted(comm_outcomes.keys()):
        counts = comm_outcomes[comm_id]
        total = sum(counts.values())
        wins = counts.get("platform_wins", 0)
        loses = counts.get("platform_loses", 0)
        mixed = counts.get("mixed", 0)
        win_rate = wins / total * 100
        print(f"\n  Community {comm_id} (n={total}):")
        print(f"    platform_wins:  {wins:2d} ({win_rate:.0f}%)")
        print(f"    platform_loses: {loses:2d} ({loses/total*100:.0f}%)")
        print(f"    mixed:          {mixed:2d} ({mixed/total*100:.0f}%)")

    print(f"\n{'=' * 60}")
    print("PLATFORM WIN RATE BY PERIOD")
    print("=" * 60)

    period_outcomes = defaultdict(Counter)
    for c in cases:
        year = int(c["year"]) if c["year"].isdigit() else 0
        if year >= 1997:
            period_start = (year // 5) * 5
            period_end = min(period_start + 4, 2025)
            if period_start == period_end:
                period = f"{period_start}"
            else:
                period = f"{period_start}-{period_end}"
            period_outcomes[period][c["outcome"]] += 1

    for period in sorted(period_outcomes.keys()):
        counts = period_outcomes[period]
        total = sum(counts.values())
        wins = counts.get("platform_wins", 0)
        win_rate = wins / total * 100
        print(f"  {period}: {wins}/{total} platform wins ({win_rate:.0f}%) [n={total}]")

    print(f"\n{'=' * 60}")
    print("INTERPRETATION")
    print("=" * 60)
    if nmi >= 0.15:
        print(f"  HIGH association (NMI={nmi:.3f})")
        print(f"  Community membership is informative about case outcome.")
        print(f"  Doctrinal communities track outcome-relevant distinctions.")
    elif nmi >= 0.05:
        print(f"  MODERATE association (NMI={nmi:.3f})")
        print(f"  Some community-outcome association but substantial overlap.")
    else:
        print(f"  LOW association (NMI={nmi:.3f})")
        print(f"  Community membership is not strongly predictive of outcome.")
        print(f"  Doctrinal communities are organized by citation patterns,")
        print(f"  not by outcome-relevant distinctions.")

    results = {
        "mutual_information": round(mi, 4),
        "normalized_mutual_information": round(nmi, 4),
        "n_cases": len(cases),
        "outcome_distribution": dict(Counter(c["outcome"] for c in cases)),
        "community_outcome_breakdown": {
            str(k): dict(v) for k, v in comm_outcomes.items()
        }
    }
    with open("data/mutual_information.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to data/mutual_information.json")

if __name__ == "__main__":
    main()