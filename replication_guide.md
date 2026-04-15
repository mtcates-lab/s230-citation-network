# Replication Guide: § 230 Citation Network — Stage 1

**Project:** Computational Legal Studies: Mapping the Citation Network of US Internet Law
**Stage:** 1 — § 230(c) Core Corpus
**Last updated:** 2026-04-14

---

## Overview

This guide describes how to reproduce the Stage 1 § 230 citation network analysis from scratch. It covers environment setup, data collection, corpus validation, graph construction, and all analyses reported in the paper. Scripts are numbered in execution order.

Estimated total compute time on a modern laptop: 45-90 minutes, excluding manual corpus validation (which requires prior legal knowledge and could take several hours as there a total of 211 cases were collected).

---

## 1. System Requirements

- macOS, Linux, or Windows with WSL2
- Python 3.10 or later
- 4GB RAM minimum; 8GB recommended
- CourtListener account
- Internet connection for CourtListener API access
- Approximately 500MB disk space for data files

---

## 2. Environment Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/[username]/s230-citation-network.git
cd s230-citation-network
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The requirements.txt file pins all package versions used in the original analysis. Key dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| requests | 2.31.0 | CourtListener API access |
| networkx | 3.2.1 | Graph construction and analysis |
| python-igraph | 0.11.3 | Leiden community detection |
| leidenalg | 0.10.2 | Leiden algorithm implementation |
| eyecite | 2.6.0 | Legal citation extraction |
| pandas | 2.1.4 | Data management |
| scipy | 1.11.4 | Statistical analysis |
| scikit-learn | 1.8.0 | NMI computation |
| numpy | 2.4.4 | Numerical computation |
| matplotlib | 3.8.2 | Visualization |

Create the required directory structure:

```bash
mkdir -p raw_data data
```

---

## 3. CourtListener API Access

Data collection uses the CourtListener REST API (https://www.courtlistener.com/api/). The API is free for non-commercial research use but rate-limited. No API key is required for read-only access, though registered users receive higher rate limits.

Rate limit: 5,000 requests per hour for anonymous users; 10,000 for registered users. Script 01_collect_data.py handles rate limiting automatically with exponential backoff.

The CourtListener data used in this analysis was collected on 2026-04-10. Results may differ slightly if collected at a different date due to ongoing additions to the CourtListener database.

---

## 4. Data Collection

**Script:** `01_collect_data.py`

Queries the CourtListener search API for federal circuit court and Supreme Court opinions citing 47 U.S.C. § 230. Retrieves case metadata including case name, court, date filed, citation strings, cite count, and the cites field (CourtListener's internal citation graph).

```bash
python3 01_collect_data.py
```

**Output:** `raw_data/s230_raw_[timestamp].json`

**Expected result:** Approximately 200-220 candidate cases depending on CourtListener database state at collection time. The original analysis retrieved 211 cases on 2026-04-10.

**Note on reproducibility:** The exact case count may differ from the original analysis if CourtListener has added new opinions or corrected existing records since 2026-04-10. The validated corpus (70 cases) is included in the repository as a fixed reference point; replicators may use it directly to skip to Step 6.

---

## 5. Corpus Validation (Manual Step)

**Script:** `06_validate_corpus.py`, `06b_check_flagged.py`

This step requires prior legal knowledge and cannot be fully automated at the time of this reading.

### 5.1 Automated flagging

Run the automated flagging script to identify obvious exclusions:

```bash
python3 06_validate_corpus.py
```

This script flags cases based on court level, publication status, and name-based heuristics. It does not make final inclusion decisions.

### 5.2 Manual review

For each candidate case, open the CourtListener opinion and review the appellate holding against the operative inclusion criterion documented in research_design.md:

> A case is included if § 230(c)(1), § 230(c)(2), § 230(f), or § 230(e) are substantively applied in an appellate holding to determine the rights or liabilities of parties as interactive computer services or their users.

Apply the ten exclusion patterns documented in research_design.md Section 3. Record each decision in the validated JSON file.

### 5.3 Deduplication

After manual review, check for duplicate CourtListener entries representing the same case:

```bash
python3 05_deduplicate.py
```

The original analysis identified and removed four duplicate entries: Zeran (cluster 2966756), Batzel (cluster 8437551), Barnes (cluster 3064672), SexSearch (cluster 2977365), and Universal v. Lycos (cluster 8439626).

### 5.4 Validated corpus

The validated corpus used in the original analysis is provided as:
`raw_data/s230_validated_20260411_030728.json`

This file contains 70 cases and is the starting point for all downstream analysis. Replicators who wish to use the original validated corpus rather than constructing their own may skip Steps 4 and 5.

---

## 6. Graph Construction

**Script:** `02_build_graph.py`

Constructs a directed graph from the validated corpus using the CourtListener cites field. Nodes are cases; edges are citations.

```bash
python3 02_build_graph.py
```

**Output:** `data/s230_graph.gexf`, `data/s230_graph.graphml`

**Expected result:** 70 nodes, 246 edges, confirmed DAG.

---

## 7. Eyecite Citation Extraction

**Scripts:** `08_eyecite_extraction.py`, `09_build_edges_from_eyecite.py`, `10_merge_edges.py`

Fetches full opinion text from CourtListener for each corpus case, extracts all citation strings using eyecite, resolves citations to corpus nodes, and merges new edges into the graph.

```bash
python3 08_eyecite_extraction.py    # downloads full text.
python3 09_build_edges_from_eyecite.py
python3 10_merge_edges.py
```

**Output:** `data/eyecite_results.json`, `data/eyecite_edges.json`, updated graph files

**Expected result:** 360 edges after merge (246 from CourtListener cites field + 114 from Eyecite full-text extraction). Edge recall rate from CourtListener cites field: 68.4%.

---

## 8. Metadata Addition

**Script:** `07_add_metadata.py`

Adds the manually coded metadata fields (primary_basis, holding_status, publication_status) to each case in the validated JSON.

```bash
python3 07_add_metadata.py
```

Outcome coding is added separately via the OUTCOME_MAP in script `/tmp/add_outcomes_v2.py`. The outcome assignments for all 70 cases are documented in `data/case_outcomes_raw.json`.

---

## 9. Network Metrics

**Script:** `03_compute_metrics.py`

Computes PageRank (α=0.85), in-degree centrality, approximate betweenness centrality, and Leiden community detection (seed=42) for all nodes.

```bash
python3 03_compute_metrics.py
```

**Output:** `data/s230_metrics.csv`

**Expected result:** 70 rows, one per case. Zeran v. AOL should have the highest PageRank (approximately 0.202).

---

## 10. Validation Analyses

Run these scripts to reproduce the methodological validation results reported in the paper.

```bash
python3 11_community_stability.py    # NMI stability across 100 Leiden runs
python3 12_consensus_partition.py    # Consensus communities at 80% co-assignment
python3 13_pagerank_robustness.py    # PageRank stability across damping factors
```

**Expected results:**
- Community stability: mean NMI = 0.686 (SD = 0.108)
- PageRank robustness: mean Kendall τ = 0.997
- Consensus partition: 19 communities at 80% threshold; 6 boundary cases

---

## 11. Core Analyses

Run these scripts to reproduce the substantive analytical results.

```bash
python3 14_mutual_information.py     # MI between community and outcome
python3 15_jensen_shannon.py         # JSD between circuits
python3 16_temporal_jsd.py           # Annual JSD 2000-2025
python3 17_temporal_snapshots.py     # Annual network metrics snapshots
python3 18_corpus_recall.py          # Generate recall sample
python3 19_recall_estimation.py      # Compute recall rate with Wilson CI
python3 20_dual_corpus_analysis.py   # Full vs restricted corpus comparison
```

**Expected results:**
- Mutual information NMI: 0.122
- Mean pairwise JSD between circuits: 0.65 (range 0.43-0.86)
- Temporal JSD: peak divergence 2007; convergence 2008 after Roommates.com en banc
- Corpus recall rate: 100% (95% Wilson CI: 0.959-1.000)
- Dual corpus PageRank τ: 0.935

---

## 12. Additional Analyses

```bash
python3 21_resilience_simulation.py  # Network resilience under node removal
python3 /tmp/save_dag_depth.py       # DAG hierarchical depth analysis
python3 23_edge_sensitivity.py       # Edge sensitivity at 10%, 20%, 30% removal
```

**Expected results:**
- Resilience: 4.3% more vulnerable to targeted than random removal
- DAG depth: max 16 levels; Spearman ρ = -0.965 with PageRank (p < 0.0001)
- Edge sensitivity: PageRank τ = 0.901-0.953 at 10-30% removal; community NMI = 0.443-0.547

---

## 13. Verifying Results

To verify your results match the original analysis, compare the top 10 cases by PageRank against the expected ranking:

| Rank | Case | PageRank |
|------|------|---------|
| 1 | Zeran v. AOL (CA4, 1997) | 0.2020 |
| 2 | Ben Ezra v. AOL (CA10, 2000) | 0.0956 |
| 3 | Batzel v. Smith (CA9, 2003) | 0.0605 |
| 4 | Green v. AOL (CA3, 2003) | 0.0501 |
| 5 | Fair Housing Council v. Roommates.com (CA9, 2008) | 0.0408 |
| 6 | Carafano v. Metrosplash (CA9, 2003) | 0.0393 |
| 7 | Doe v. Illinois Football Team (CA7, 2003) | 0.0309 |
| 8 | Chicago Lawyers v. Craigslist (CA7, 2008) | 0.0271 |
| 9 | Universal v. Lycos (CA1, 2007) | 0.0264 |
| 10 | Barnes v. Yahoo (CA9, 2009) | 0.0244 |

Minor floating-point differences are expected. The rank ordering should be identical.

---

## 14. Known Reproducibility Limitations

**CourtListener coverage changes.** The CourtListener database is updated continuously. New opinions added after 2026-04-10 will not appear in a fresh retrieval that is otherwise identical to the original. Use the provided validated corpus file to ensure exact reproducibility of the graph and downstream results.

**Leiden algorithm stochasticity.** The Leiden algorithm produces different community assignments with different random seeds. All scripts use seed=42 for the primary analysis. Community stability analysis (script 11) explicitly tests sensitivity across 100 seeds.

**Eyecite version sensitivity.** Citation extraction results may differ with different versions of eyecite. The original analysis used eyecite 2.6.0. Pin this version in your environment for exact reproducibility.

**Manual corpus validation.** The corpus validation step (Step 5) requires legal expertise and involves judgment calls documented in research_design.md. Two researchers applying the same inclusion criterion to the same 211 cases may produce slightly different corpora; the ten exclusion patterns in research_design.md are designed to minimize this variance.

---

## 15. Data Availability

The following files are deposited at [Zenodo DOI to be added]:

- `raw_data/s230_validated_20260411_030728.json` — validated corpus with all metadata
- `data/s230_graph.gexf` — citation graph (GEXF format)
- `data/s230_graph.graphml` — citation graph (GraphML format)
- `data/s230_metrics.csv` — per-node network metrics
- `data/case_outcomes_raw.json` — outcome codings with notes
- All supplementary analysis files listed in codebook.md Section 4

All code is available at [GitHub URL to be added] under the MIT License.

---

## 16. Contact and Citation

For questions about replication, contact mtcates@uga.edu.

If you use this dataset or code in published research, please cite:

> [Citation to be added upon publication]