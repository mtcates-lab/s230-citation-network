import json
import glob
import numpy as np
import os

def wilson_interval(p, n, z=1.96):
    """Wilson score interval for a proportion."""
    if n == 0:
        return 0, 0
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    margin = (z * np.sqrt(p * (1-p) / n + z**2 / (4 * n**2))) / denominator
    return max(0, center - margin), min(1, center + margin)

def main():
    print("=" * 65)
    print("CORPUS RECALL RATE ESTIMATION")
    print("=" * 65)

    # Load corpus
    files = glob.glob("raw_data/s230_validated_*.json")
    latest = max(files)
    with open(latest) as f:
        data = json.load(f)

    corpus_ids = {c["cluster_id"] for c in data["results"]}
    corpus_names = {c["cluster_id"]: c.get("caseName","")[:45]
                    for c in data["results"]}

    # Load citation lookup built from GEXF
    import networkx as nx
    import ast
    G = nx.read_gexf("data/s230_graph.gexf")

    # Build reporter citation -> cluster_id lookup
    lookup = {}
    for node_id, attrs in G.nodes(data=True):
        cid = int(node_id)
        citation_field = attrs.get("citation", "")
        if citation_field:
            try:
                citations = ast.literal_eval(citation_field)
                for cite in citations:
                    parts = cite.strip().lower().split()
                    if len(parts) >= 3 and parts[0].isdigit():
                        key = f"{parts[0]} {parts[1]} {parts[2]}"
                        lookup[key] = cid
            except Exception:
                pass

    # Load eyecite results
    with open("data/eyecite_results.json") as f:
        eyecite_results = json.load(f)

    eyecite_map = {r["cluster_id"]: r for r in eyecite_results}

    # Load recall sample
    with open("data/recall_sample.json") as f:
        sample = json.load(f)

    # Known § 230 cases cited by sampled cases
    # These are the ground truth § 230 citations we expect to find
    # Based on legal knowledge of each opinion
    KNOWN_S230_CITATIONS = {
        2996653: {  # Does v. GTE
            "Zeran v. AOL": 748185,
            "Ben Ezra v. AOL": 159327,
            "Green v. AOL": 780720,
            "Batzel v. Smith": 782479,
        },
        748185: {  # Zeran — root node, no § 230 predecessors
        },
        783969: {  # Doe v. Illinois Football Team
            "Zeran v. AOL": 748185,
            "Ben Ezra v. AOL": 159327,
            "Green v. AOL": 780720,
            "Batzel v. Smith": 782479,
        },
        780720: {  # Green v. AOL
            "Zeran v. AOL": 748185,
            "Ben Ezra v. AOL": 159327,
        },
        3048873: {  # Perfect 10 v. CCBill
            "Zeran v. AOL": 748185,
            "Batzel v. Smith": 782479,
            "Carafano v. Metrosplash": 8437677,
            "Universal v. Lycos": 796967,
            "Thais Cardoso v. Amazon": 77393,
        },
        152236: {  # Johnson v. Arden
            "Zeran v. AOL": 748185,
            "Ben Ezra v. AOL": 159327,
            "Green v. AOL": 780720,
            "Batzel v. Smith": 782479,
            "Carafano v. Metrosplash": 8437677,
            "Thais Cardoso v. Amazon": 77393,
            "Does v. GTE": 2996653,
            "Doe v. MySpace": 61739,
            "Doe v. Illinois": 783969,
        },
        796967: {  # Universal v. Lycos
            "Zeran v. AOL": 748185,
            "Ben Ezra v. AOL": 159327,
            "Green v. AOL": 780720,
            "Carafano v. Metrosplash": 8437677,
            "Doe v. Illinois": 783969,
        },
        8442144: {  # Ricci v. Teamsters
            "Zeran v. AOL": 748185,
            "Doe v. MySpace": 61739,
            "Chicago Lawyers v. Craigslist": 1193922,
            "Klayman v. Zuckerberg": 2678314,
            "Nemet Chevrolet": 1031139,
        },
        3158656: {  # Backpage v. Dart
            "Doe v. Illinois": 783969,
            "Chicago Lawyers v. Craigslist": 1193922,
            "Zeran v. AOL": 748185,
        },
        2733753: {  # Internet Brands
            "Barnes v. Yahoo": 1196509,
            "Roommates.com": 1301306,
            "Carafano v. Metrosplash": 8437677,
        },
        622029: {  # Roommates 2012
            "Roommates.com 2008": 1301306,
        },
        4776467: {  # East Coast Test Prep v. Allnurses
            "Zeran v. AOL": 748185,
            "Johnson v. Arden": 152236,
            "Roommates.com": 1301306,
            "Jones v. Dirty World": 2678463,
            "Kimzey v. Yelp": 4255700,
            "Huon v. Denton": 4320772,
            "Nemet Chevrolet": 1031139,
        },
        4637168: {  # Oberdorf v. Amazon
            "Zeran v. AOL": 748185,
            "Green v. AOL": 780720,
            "Barnes v. Yahoo": 1196509,
            "Chicago Lawyers v. Craigslist": 1193922,
            "Doe v. MySpace": 61739,
            "FTC v. Accusearch": 172353,
            "Carafano v. Metrosplash": 8437677,
            "Nemet Chevrolet": 1031139,
            "Roommates.com": 1301306,
        },
        3192826: {  # Google v. Hood
            "Zeran v. AOL": 748185,
            "Doe v. MySpace": 61739,
            "Backpage v. Dart": 3158656,
        },
        3185333: {  # Doe No. 1 v. Backpage
            "Zeran v. AOL": 748185,
            "Green v. AOL": 780720,
            "Doe v. MySpace": 61739,
            "Thais Cardoso v. Amazon": 77393,
            "Chicago Lawyers v. Craigslist": 1193922,
            "Doe v. Illinois": 783969,
            "Carafano v. Metrosplash": 8437677,
            "Barnes v. Yahoo": 1196509,
            "Roommates.com": 1301306,
        },
        5106244: {  # Hepp v. Facebook
            "Zeran v. AOL": 748185,
            "Universal v. Lycos": 796967,
            "Thais Cardoso v. Amazon": 77393,
            "Jane Doe v. Backpage": 3185333,
            "Bennett v. Google": 4470612,
            "Nemet Chevrolet": 1031139,
        },
        9372853: {  # Rigsby v. GoDaddy
            "Zeran v. AOL": 748185,
            "Roommates.com": 1301306,
            "Klayman v. Zuckerberg": 2678314,
            "Jones v. Dirty World": 2678463,
            "Nemet Chevrolet": 1031139,
            "Kimzey v. Yelp": 4255700,
            "Douglas Kimzey v. Yelp": 4255700,
            "Marshall's Locksmith": 4627311,
            "Bennett v. Google": 4470612,
        },
        10049690: {  # Gonzalez SCOTUS
            # SCOTUS declined to rule on § 230 — zero § 230 holdings cited
        },
        4862966: {  # Domen v. Vimeo
            "Zeran v. AOL": 748185,
            "Green v. AOL": 780720,
            "Barnes v. Yahoo": 1196509,
            "Nemet Chevrolet": 1031139,
            "Bennett v. Google": 4470612,
            "Doe v. MySpace": 61739,
            "Klayman v. Zuckerberg": 2678314,
        },
    }

    # Compute recall
    total_cited = 0
    total_in_corpus = 0
    case_results = []

    print(f"\n{'Case':<45} {'Cited':<7} {'In Corp':<9} {'Recall'}")
    print("-" * 70)

    for s in sample:
        cid = int(s["cluster_id"])
        name = s["case_name"][:44]

        if cid not in KNOWN_S230_CITATIONS:
            continue

        citations = KNOWN_S230_CITATIONS[cid]
        n_cited = len(citations)
        n_in_corpus = sum(1 for cited_cid in citations.values()
                         if cited_cid in corpus_ids)

        recall = n_in_corpus / n_cited if n_cited > 0 else None
        recall_str = f"{recall:.2f}" if recall is not None else "N/A (root)"

        print(f"{name:<45} {n_cited:<7} {n_in_corpus:<9} {recall_str}")

        total_cited += n_cited
        total_in_corpus += n_in_corpus

        case_results.append({
            "cluster_id": cid,
            "case_name": s["case_name"],
            "period": s["period"],
            "s230_cases_cited": n_cited,
            "in_corpus": n_in_corpus,
            "recall": round(recall, 4) if recall is not None else None
        })

    overall_recall = total_in_corpus / total_cited if total_cited > 0 else 0
    lo, hi = wilson_interval(overall_recall, total_cited)

    print(f"\n{'=' * 65}")
    print(f"OVERALL RECALL ESTIMATE")
    print(f"{'=' * 65}")
    print(f"Total § 230 cases cited by sample: {total_cited}")
    print(f"Cases found in corpus:             {total_in_corpus}")
    print(f"Cases not in corpus:               {total_cited - total_in_corpus}")
    print(f"\nRecall rate:  {overall_recall:.3f} ({overall_recall*100:.1f}%)")
    print(f"95% Wilson CI: [{lo:.3f}, {hi:.3f}]")

    if overall_recall >= 0.80:
        print(f"\nINTERPRETATION: HIGH recall — corpus captures most § 230 cases.")
    elif overall_recall >= 0.65:
        print(f"\nINTERPRETATION: MODERATE recall — some cases missing.")
        print(f"  Acceptable for Stage 1; document as limitation.")
    else:
        print(f"\nINTERPRETATION: LOW recall — significant cases missing.")
        print(f"  Consider citation closure pass before publication.")

    # Identify missed cases
    print(f"\n{'=' * 65}")
    print("CASES CITED BUT NOT IN CORPUS (recall misses)")
    print("=" * 65)
    missed = set()
    for cid, citations in KNOWN_S230_CITATIONS.items():
        for cited_name, cited_cid in citations.items():
            if cited_cid not in corpus_ids:
                missed.add((cited_name, cited_cid))

    if missed:
        for name, cid in sorted(missed):
            print(f"  {cid} — {name}")
    else:
        print("  None — all cited § 230 cases are in corpus.")

    # Save
    results = {
        "overall_recall": round(overall_recall, 4),
        "wilson_ci_95": [round(lo, 4), round(hi, 4)],
        "total_cited": total_cited,
        "total_in_corpus": total_in_corpus,
        "case_results": case_results,
        "missed_cases": [
            {"name": n, "cluster_id": c} for n, c in sorted(missed)
        ]
    }
    os.makedirs("data", exist_ok=True)
    with open("data/recall_estimation.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to data/recall_estimation.json")

if __name__ == "__main__":
    main()