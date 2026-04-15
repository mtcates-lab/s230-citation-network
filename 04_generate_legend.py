import pandas as pd

df = pd.read_csv("data/s230_metrics.csv")

community_names = {
    2: "Zeran core — foundational § 230(c)(1) immunity doctrine",
    0: "Early multi-circuit doctrine — pre-2008 development",
    1: "Modern Ninth Circuit — development test and Good Samaritan",
    3: "Seventh Circuit cluster — platform immunity doctrine",
    4: "Social media era — post-2008 multi-circuit applications",
    5: "Isolated — SexSearch",
    6: "SCOTUS — Gonzalez qualified engagement",
    7: "Good Samaritan — Enigma § 230(c)(2)(B)",
    8: "FOSTA — M.H. v. Omegle scienter holding",
}

print("=" * 80)
print("§ 230 CITATION NETWORK — NODE LEGEND")
print("=" * 80)

top = df[df["community"].isin(community_names.keys())].copy()
top = top.sort_values(["community", "pagerank"], ascending=[True, False])

for comm_id, group in top.groupby("community"):
    label = community_names.get(comm_id, f"Community {comm_id}")
    print(f"\nCOMMUNITY {comm_id} — {label}")
    print("-" * 60)
    for rank, (_, row) in enumerate(group.head(8).iterrows(), 1):
        year = str(row["date"])[:4] if row["date"] else "????"
        name = str(row["case_name"])[:55]
        print(f"  {rank}. [{row['court'].upper():8}] {year}  {name}")
        print(f"     PageRank: {row['pagerank']:.4f}  |  Citations received: {int(row['in_degree'])}")

print("\n" + "=" * 80)
print("TOP 15 CASES OVERALL BY PAGERANK")
print("=" * 80)
print(f"\n{'Rank':<5} {'PageRank':<10} {'Cited':<7} {'Court':<8} {'Year':<6} Case Name")
print("-" * 80)
for i, row in enumerate(df.head(15).itertuples(), 1):
    year = str(row.date)[:4] if row.date else "????"
    name = str(row.case_name)[:50]
    print(f"  {i:<4} {row.pagerank:<10.4f} {int(row.in_degree):<7} {row.court:<8} {year:<6} {name}")