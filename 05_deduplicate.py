import json
import glob
import pandas as pd
from datetime import datetime

def load_latest_raw_data():
    files = glob.glob("raw_data/s230_raw_*.json")
    latest = max(files)
    print(f"Loading: {latest}")
    with open(latest) as f:
        data = json.load(f)
    return data["results"], latest

def find_duplicates(cases):
    print("\n" + "=" * 60)
    print("DUPLICATE ANALYSIS")
    print("=" * 60)

    seen_names = {}
    seen_citations = {}
    duplicates = []

    for case in cases:
        cluster_id = case.get("cluster_id")
        name = case.get("caseName", "").strip().lower()
        citations = str(case.get("citation", ""))
        date = case.get("dateFiled", "")
        court = case.get("court_id", "")

        name_key = name[:40]
        if name_key in seen_names:
            duplicates.append({
                "type": "name_match",
                "keep_id": seen_names[name_key]["cluster_id"],
                "keep_name": seen_names[name_key]["caseName"],
                "drop_id": cluster_id,
                "drop_name": case.get("caseName"),
                "court": court,
                "date": date,
            })
        else:
            seen_names[name_key] = case

        if citations and citations != "[]":
            if citations in seen_citations:
                duplicates.append({
                    "type": "citation_match",
                    "keep_id": seen_citations[citations]["cluster_id"],
                    "keep_name": seen_citations[citations]["caseName"],
                    "drop_id": cluster_id,
                    "drop_name": case.get("caseName"),
                    "court": court,
                    "date": date,
                })
            else:
                seen_citations[citations] = case

    return duplicates

def print_duplicates(duplicates):
    if not duplicates:
        print("No duplicates found.")
        return

    print(f"\nFound {len(duplicates)} duplicate entries:\n")
    for i, d in enumerate(duplicates, 1):
        print(f"  {i}. [{d['type'].upper()}]")
        print(f"     KEEP: {d['keep_name'][:60]} (id: {d['keep_id']})")
        print(f"     DROP: {d['drop_name'][:60]} (id: {d['drop_id']})")
        print()

def remove_duplicates(cases, duplicates):
    drop_ids = set(d["drop_id"] for d in duplicates)
    cleaned = [c for c in cases if c.get("cluster_id") not in drop_ids]
    return cleaned

def save_cleaned_data(cases, original_file):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"raw_data/s230_cleaned_{timestamp}.json"

    output = {
        "pulled_at": timestamp,
        "total_cases": len(cases),
        "note": "Deduplicated version of raw data",
        "results": cases
    }

    with open(filename, "w") as f:
        import json
        json.dump(output, f, indent=2)

    print(f"Cleaned data saved to: {filename}")
    return filename

if __name__ == "__main__":
    print("=" * 60)
    print("§ 230 DEDUPLICATION SCRIPT")
    print("=" * 60)

    cases, source_file = load_latest_raw_data()
    print(f"Total cases before deduplication: {len(cases)}")

    duplicates = find_duplicates(cases)
    print_duplicates(duplicates)

    print("=" * 60)
    print(f"Cases before: {len(cases)}")
    print(f"Duplicates found: {len(duplicates)}")
    print(f"Cases after: {len(cases) - len(duplicates)}")
    print("=" * 60)

    confirm = input("\nRemove duplicates and save cleaned dataset? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted. No changes made.")
        exit(0)

    cleaned = remove_duplicates(cases, duplicates)
    filename = save_cleaned_data(cleaned, source_file)

    print(f"\nDone. {len(cleaned)} cases in cleaned dataset.")
    print("Next step: rerun 02_build_graph.py and 03_compute_metrics.py")
    print("on the cleaned data file.")