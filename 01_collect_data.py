import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("COURTLISTENER_TOKEN")

if not TOKEN:
    raise ValueError("No API token found. Check your .env file.")

HEADERS = {"Authorization": f"Token {TOKEN}"}
BASE_URL = "https://www.courtlistener.com/api/rest/v4/"

SEARCH_PARAMS = {
    "q": '"47 U.S.C. § 230" OR "47 U.S.C. 230" OR "section 230" OR "CDA 230"',
    "type": "o",
    "stat_Precedential": "on",
    "court": "scotus ca1 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 ca10 ca11 cadc cafc",
    "filed_after": "1996-01-01",
    "order_by": "dateFiled asc",
    "page_size": 20,
}

def fetch_all_results(params):
    all_results = []
    url = BASE_URL + "search/"
    page = 1

    print(f"Starting data collection...")
    print(f"Query: {params['q']}")
    print(f"Courts: {params['court']}")
    print("-" * 50)

    while url:
        print(f"  Fetching page {page}...", end=" ")

        response = requests.get(
            url,
            headers=HEADERS,
            params=params if page == 1 else {}
        )

        if response.status_code == 429:
            print("Rate limited. Waiting 30 seconds...")
            time.sleep(30)
            continue

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text[:300])
            break

        data = response.json()
        results = data.get("results", [])
        all_results.extend(results)

        print(f"got {len(results)} cases. Total: {len(all_results)}")

        url = data.get("next")
        page += 1
        time.sleep(0.5)

    return all_results

def save_results(results, params):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"raw_data/s230_raw_{timestamp}.json"

    output = {
        "pulled_at": timestamp,
        "total_cases": len(results),
        "query_params": params,
        "results": results
    }

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(results)} cases to {filename}")
    return filename

def run_test_query():
    test_params = SEARCH_PARAMS.copy()
    test_params["page_size"] = 3

    print("Running test query (3 results)...")
    response = requests.get(
        BASE_URL + "search/",
        headers=HEADERS,
        params=test_params
    )

    if response.status_code != 200:
        print(f"Test failed: {response.status_code}")
        print(response.text)
        return False

    data = response.json()
    print(f"\nTest succeeded.")
    print(f"Total available: {data.get('count', 'unknown')}")
    print(f"\nFirst case fields:")

    if data["results"]:
        first = data["results"][0]
        for key, val in first.items():
            preview = str(val)[:80] if val else "None"
            print(f"  {key}: {preview}")

    return True

if __name__ == "__main__":
    print("=" * 50)
    print("PHASE 1: TEST QUERY")
    print("=" * 50)

    success = run_test_query()

    if not success:
        print("Test failed. Check your API token and connection.")
        exit(1)

    print("\n" + "=" * 50)
    print("PHASE 2: FULL COLLECTION")
    print("=" * 50)

    confirm = input("\nTest passed. Run full collection? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        exit(0)

    results = fetch_all_results(SEARCH_PARAMS)
    filename = save_results(results, SEARCH_PARAMS)

    print("\n" + "=" * 50)
    print("COLLECTION COMPLETE")
    print("=" * 50)
    print(f"Cases collected: {len(results)}")
    print(f"Saved to: {filename}")
    print("\nNext step: run 02_build_graph.py")