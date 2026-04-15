import json
import glob
import time
import os
import requests
from dotenv import load_dotenv
from eyecite import get_citations
from eyecite.models import FullCaseCitation

load_dotenv()
TOKEN = os.getenv("COURTLISTENER_TOKEN")
HEADERS = {"Authorization": f"Token {TOKEN}"}
BASE_URL = "https://www.courtlistener.com/api/rest/v4/"

def load_corpus():
    files = glob.glob("raw_data/s230_validated_*.json")
    latest = max(files)
    print(f"Loading corpus: {latest}")
    with open(latest) as f:
        data = json.load(f)
    return data["results"]

def get_opinion_text(cluster_id):
    url = f"{BASE_URL}clusters/{cluster_id}/"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None
    data = r.json()
    sub_opinions = data.get("sub_opinions", [])
    for op_url in sub_opinions:
        r2 = requests.get(op_url, headers=HEADERS)
        if r2.status_code != 200:
            continue
        op = r2.json()
        text = (op.get("plain_text") or
                op.get("html_with_citations") or
                op.get("html") or "")
        if text.strip():
            return text
    return None

def extract_citation_strings(text):
    """Extract citation strings from opinion text using Eyecite."""
    try:
        citations = get_citations(text)
        strings = []
        for c in citations:
            if isinstance(c, FullCaseCitation):
                groups = c.groups
                volume = groups.get('volume', '')
                reporter = groups.get('reporter', '')
                page = groups.get('page', '')
                if volume and reporter and page:
                    cite_str = f"{volume} {reporter} {page}"
                    strings.append(cite_str)
        return strings
    except Exception as e:
        print(f"  Eyecite error: {e}")
        return []

def main():
    cases = load_corpus()
    corpus_ids = {c["cluster_id"] for c in cases}
    print(f"Corpus size: {len(cases)} cases")

    results = []
    text_available = 0
    text_missing = 0

    print("\nExtracting citations from full opinion text...")
    print("=" * 60)

    for i, case in enumerate(cases):
        cid = case["cluster_id"]
        name = case.get("caseName", "")[:50]
        print(f"[{i+1:3}/{len(cases)}] {name}")

        text = get_opinion_text(cid)
        if not text:
            print(f"         No text available")
            text_missing += 1
            results.append({
                "cluster_id": cid,
                "case_name": case.get("caseName", ""),
                "citations_found": 0,
                "corpus_citations": []
            })
            time.sleep(0.3)
            continue

        text_available += 1
        citation_strings = extract_citation_strings(text)

        print(f"         {len(citation_strings)} citation strings extracted")

        results.append({
            "cluster_id": cid,
            "case_name": case.get("caseName", ""),
            "citations_found": len(citation_strings),
            "corpus_citations": citation_strings
        })
        time.sleep(0.4)

    print("\n" + "=" * 60)
    print(f"Text available: {text_available}/{len(cases)} cases")
    print(f"Text missing:   {text_missing}/{len(cases)} cases")

    os.makedirs("data", exist_ok=True)
    with open("data/eyecite_results.json", "w") as f:
        json.dump(results, f, indent=2)

    total_citations = sum(r["citations_found"] for r in results)
    print(f"Total citations extracted: {total_citations}")
    print(f"Results saved to data/eyecite_results.json")
    print("Next step: run 09_build_edges_from_eyecite.py")

if __name__ == "__main__":
    main()