import json
import glob
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("COURTLISTENER_TOKEN")
HEADERS = {"Authorization": f"Token {TOKEN}"}
BASE_URL = "https://www.courtlistener.com/api/rest/v4/"

FLAGGED_IDS = [
    7052128, 745362, 755878, 7077712, 7078442, 765541,
    7080078, 185105, 7118569, 2967482, 199715, 118477,
    2996393, 782642, 8437787, 76364, 3014559, 3014331,
    200980, 3014050, 37885, 791594, 793245, 169308,
    3043679, 1201966, 1027825, 3064521, 187508, 1325,
    626941, 810371, 8478430, 1040307, 8441782, 2681572,
    8442144, 2794558, 3153481, 4387647, 7330235, 4550762,
    8443923, 4599044, 4602369, 4667066, 4668934, 7441136,
    10355247, 10647074
]

S230C_PATTERNS = [
    "230(c)", "§ 230(c)", "section 230(c)",
    "230(c)(1)", "230(c)(2)",
    "interactive computer service",
    "information content provider",
]

def check_opinion(cluster_id):
    url = f"{BASE_URL}clusters/{cluster_id}/"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return cluster_id, "ERROR", ""
    data = r.json()
    case_name = data.get("case_name", "")
    opinion_ids = data.get("sub_opinions", [])
    for op_url in opinion_ids:
        op_r = requests.get(op_url, headers=HEADERS)
        if op_r.status_code != 200:
            continue
        op_data = op_r.json()
        text = (op_data.get("plain_text") or
                op_data.get("html_with_citations") or
                op_data.get("html") or "").lower()
        for pattern in S230C_PATTERNS:
            if pattern.lower() in text:
                return cluster_id, "POSSIBLE_S230C", case_name
    return cluster_id, "NOT_S230C", case_name

if __name__ == "__main__":
    print("Checking flagged cases for § 230(c) content...")
    print("=" * 65)
    possible = []
    for cid in FLAGGED_IDS:
        cid_int, result, name = check_opinion(cid)
        if result == "POSSIBLE_S230C":
            print(f"  KEEP? {name[:55]} (id: {cid_int})")
            possible.append(cid_int)
        elif result == "ERROR":
            print(f"  ERROR checking id: {cid_int}")
        time.sleep(0.4)
    print("=" * 65)
    print(f"\nCases that may contain § 230(c): {len(possible)}")
    if possible:
        print("Review these before removing:")
        for cid in possible:
            print(f"  https://courtlistener.com/opinion/{cid}/")
    else:
        print("All flagged cases confirmed non-§ 230(c). Safe to remove all.")