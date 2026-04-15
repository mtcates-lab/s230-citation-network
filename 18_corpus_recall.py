import json
import glob
import networkx as nx
import pandas as pd
import random
import os

def main():
    print("=" * 60)
    print("CORPUS RECALL RATE ESTIMATION")
    print("=" * 60)

    G = nx.read_gexf("data/s230_graph.gexf")
    metrics = pd.read_csv("data/s230_metrics.csv")

    files = glob.glob("raw_data/s230_validated_*.json")
    latest = max(files)
    with open(latest) as f:
        data = json.load(f)

    corpus_ids = {str(c["cluster_id"]) for c in data["results"]}
    corpus_names = {str(c["cluster_id"]): c.get("caseName","")
                    for c in data["results"]}

    # Stratified sample — pick cases from different time periods
    # and different PageRank levels to get representative coverage
    metrics["node_id"] = metrics["node_id"].astype(str)
    metrics = metrics[metrics["node_id"].isin(corpus_ids)]

    # Sort by date and sample across periods
    files2 = glob.glob("raw_data/s230_validated_*.json")
    latest2 = max(files2)
    with open(latest2) as f:
        data2 = json.load(f)

    cases_by_period = {
        "1997-2005": [],
        "2006-2010": [],
        "2011-2015": [],
        "2016-2020": [],
        "2021-2025": [],
    }

    for case in data2["results"]:
        year = int(str(case.get("dateFiled","9999"))[:4])
        cid = str(case.get("cluster_id"))
        name = case.get("caseName","")[:60]
        url = "https://courtlistener.com" + case.get("absolute_url","")
        entry = (cid, name, url)
        if 1997 <= year <= 2005:
            cases_by_period["1997-2005"].append(entry)
        elif 2006 <= year <= 2010:
            cases_by_period["2006-2010"].append(entry)
        elif 2011 <= year <= 2015:
            cases_by_period["2011-2015"].append(entry)
        elif 2016 <= year <= 2020:
            cases_by_period["2016-2020"].append(entry)
        elif 2021 <= year <= 2025:
            cases_by_period["2021-2025"].append(entry)

    # Sample 4 cases from each period = 20 total
    random.seed(42)
    sample = []
    for period, cases in cases_by_period.items():
        n = min(4, len(cases))
        sampled = random.sample(cases, n)
        for cid, name, url in sampled:
            sample.append({
                "period": period,
                "cluster_id": cid,
                "case_name": name,
                "url": url
            })

    print(f"\nStratified sample of {len(sample)} cases for recall estimation:")
    print(f"{'Period':<12} {'Case':<55} URL")
    print("-" * 100)
    for s in sample:
        print(f"{s['period']:<12} {s['case_name']:<55}")
        print(f"             {s['url']}")
        print()

    print("=" * 60)
    print("INSTRUCTIONS FOR MANUAL RECALL CHECK")
    print("=" * 60)
    print("""
For each case above:
1. Open the CourtListener URL
2. Read the opinion
3. Identify every case it cites that is a substantive § 230 case
   (applying § 230(c)(1), § 230(c)(2), § 230(e), or § 230(f)
   to determine rights or liabilities)
4. Check whether each cited § 230 case is in our corpus

Record your findings in data/recall_check_results.json with this format:
{
  "cluster_id": "...",
  "case_name": "...",
  "s230_cases_cited": [
    {"name": "case name", "in_corpus": true/false, "notes": "..."}
  ]
}

The recall rate = (cases in corpus) / (total § 230 cases cited)
""")

    # Save sample for reference
    os.makedirs("data", exist_ok=True)
    with open("data/recall_sample.json", "w") as f:
        json.dump(sample, f, indent=2)
    print("Sample saved to data/recall_sample.json")

    # Also show which § 230 cases each sampled case already
    # cites within our corpus (from the graph)
    print("\n" + "=" * 60)
    print("CORPUS CITATIONS ALREADY CAPTURED (from graph)")
    print("=" * 60)
    for s in sample:
        cid = s["cluster_id"]
        if cid in G.nodes():
            successors = list(G.successors(cid))
            print(f"\n{s['case_name'][:55]}:")
            print(f"  Already captured: {len(successors)} corpus citations")
            for succ in successors[:5]:
                name = G.nodes[succ].get("name","")[:50]
                print(f"    → {name}")

if __name__ == "__main__":
    main()