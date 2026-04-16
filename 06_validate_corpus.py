import json
import glob
import pandas as pd

def load_latest_cleaned_data():
    files = glob.glob("raw_data/s230_cleaned_*.json")
    latest = max(files)
    print(f"Loading: {latest}")
    with open(latest) as f:
        data = json.load(f)
    return data["results"], latest

def flag_suspicious_cases(cases):
    suspicious = []
    confirmed = []

    s230_keywords = [
        "230", "section 230", "cda", "communications decency",
        "interactive computer service", "information content provider",
        "publisher", "speaker", "third party", "user generated",
        "platform", "immunity", "safe harbor", "intermediary"
    ]

# WARNING: The non_s230_indicators list below is a pipeline heuristic used
# to flag cases for human review. It is NOT the authoritative exclusion
# criterion. Authoritative inclusion and exclusion decisions are documented
# in research_design.md (operative inclusion criterion and ten exclusion
# patterns) and in the Corpus Boundary Decisions Log (CBL).
# This list may become stale as new cases are added to CourtListener.
# Do not use it as a substitute for human review against the CBL.
print("WARNING: non_s230_indicators is a pipeline heuristic for flagging only.")
print("Authoritative exclusion decisions are in research_design.md and the CBL.")
print("Human review against the operative inclusion criterion is required.")
print()

    non_s230_indicators = [
        "packaging corp", "martinez-madera", "holder",
        "ferrell v. united states department of housing",
        "jansen v. packaging",
        "city of shoreacres", "waterworth",
        "rueth", "dotson", "hanny",
        "1000 friends of maryland",
        "cencast", "kornman v. securities",
        "ohio valley environmental",
        "audubon", "army corps",
        "nat'l parks conservation",
        "georgia muslim voter",
        "tokyo gwinnett",
        "weigand v. national labor",
        "wwc holding",
        "sopkin",
        "bell atlantic telephone",
        "thomasville furniture",
        "74 fair empl",
        "macfarlane v. walter",
        "sallen v. corinthians",
        "nielsen tyler v. armstrong",
        "nh dept. of admin",
        "diblasio v. novello",
        "united states v. rueth",
        "united states v. dodds",
        "united states v. dotson",
        "united states v. hanny",
        "united states v. thomas hanny",
        "united states v. charles johnson",
        "united states v. markette tillman",
        "united states v. bradford",
        "cgb occupational therapy",
        "rha health services",
        "zalewski v. cicero",
        "rosetta stone",
        "s.j.w. ex rel",
        "lee's summit",
        "nieman v. versuslaw",
        "clearcorrect operating",
        "international trade commission",
        "nat'l railroad passenger",
        "julie su",
        "haar v. nationwide",
        "audubon soc",
        "nat'l parks",
        "weigand v. national",
        "gristina v. merchan",
        "martinez-madera",
        "hector alon",
        "macfarlane",
        "prometheus radio",
        "mozilla corporation v. fcc",
        "united states telecom assoc",
        "bell atl tele",
        "comcast corp. v. federal communications",
        "national cable",
        "gulf power",
        "clearfield",
        "cwc holding",
	
    ]

    for case in cases:
        name = case.get("caseName", "").lower()
        case_id = case.get("cluster_id")
        court = case.get("court_id", "")
        date = case.get("dateFiled", "")

        is_suspicious = any(ind in name for ind in non_s230_indicators)

        if is_suspicious:
            suspicious.append({
                "cluster_id": case_id,
                "case_name": case.get("caseName", ""),
                "court": court,
                "date": date,
                "reason": "Name matches known non-§230 pattern",
                "url": "https://courtlistener.com" + case.get("absolute_url", "")
            })
        else:
            confirmed.append(case)

    return suspicious, confirmed

def print_suspicious(suspicious):
    print(f"\n{'='*70}")
    print(f"FLAGGED AS POTENTIALLY NOT § 230 CASES")
    print(f"{'='*70}")
    print(f"Total flagged: {len(suspicious)}\n")

    for i, case in enumerate(suspicious, 1):
        print(f"  {i:3}. {case['case_name'][:65]}")
        print(f"       Court: {case['court'].upper():8}  Year: {str(case['date'])[:4]}")
        print(f"       URL: {case['url']}")
        print()

def save_validated_data(confirmed, suspicious):
    import json
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    validated_file = f"raw_data/s230_validated_{timestamp}.json"
    output = {
        "pulled_at": timestamp,
        "total_cases": len(confirmed),
        "note": "Deduplicated and validated. Non-§230 cases removed.",
        "results": confirmed
    }
    with open(validated_file, "w") as f:
        json.dump(output, f, indent=2)

    flagged_file = f"raw_data/s230_flagged_{timestamp}.csv"
    pd.DataFrame(suspicious).to_csv(flagged_file, index=False)

    print(f"Validated data saved to: {validated_file}")
    print(f"Flagged cases saved to:  {flagged_file}")
    return validated_file

if __name__ == "__main__":
    print("=" * 70)
    print("§ 230 CORPUS VALIDATION")
    print("=" * 70)

    cases, source = load_latest_cleaned_data()
    print(f"Cases loaded: {len(cases)}")

    suspicious, confirmed = flag_suspicious_cases(cases)
    print_suspicious(suspicious)

    print(f"{'='*70}")
    print(f"Cases before validation: {len(cases)}")
    print(f"Cases flagged:           {len(suspicious)}")
    print(f"Cases remaining:         {len(confirmed)}")
    print(f"{'='*70}")

    print("\nREVIEW the flagged cases above carefully before proceeding.")
    print("Each has a URL — open it to verify it is not a § 230 case.")
    confirm = input("\nRemove flagged cases and save validated dataset? (yes/no): ")

    if confirm.lower() != "yes":
        print("Aborted. No changes made.")
        exit(0)

    validated_file = save_validated_data(confirmed, suspicious)

    print(f"\nDone. {len(confirmed)} validated § 230 cases remain.")
    print("Next: update 02_build_graph.py to load s230_validated_*.json")
    print("Then rerun 02, 03, and 04.")