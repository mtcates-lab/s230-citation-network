# Codebook: § 230 Citation Network — Stage 1

**Project:** Computational Legal Studies: Mapping the Citation Network of US Internet Law
**Stage:** 1 — § 230(c) Core Corpus
**Last updated:** 2026-04-14
**Corresponds to:** s230_validated_20260411_030728.json, s230_graph.gexf, s230_metrics.csv

---

## Overview

This codebook documents every field in the three primary data files for the Stage 1 corpus. Researchers replicating or extending this work should consult this document alongside the research_design.md for the methodological rationale behind inclusion and coding decisions.

The three primary files are:

- **s230_validated_[date].json** — the validated case corpus with all node metadata
- **s230_graph.gexf / s230_graph.graphml** — the directed citation graph
- **s230_metrics.csv** — per-node network metrics computed from the graph

---

## 1. Validated Corpus JSON (s230_validated_[date].json)

The validated corpus is stored as a JSON object with a single key `results` containing an array of case objects. Each case object has the following fields.

---

### 1.1 Identification Fields

**cluster_id** (integer)
CourtListener cluster identifier. A cluster groups one or more opinion documents that represent the same case. This is the primary key for joining across files. The cluster ID is stable across CourtListener API versions.
*Example:* `748185`

**caseName** (string)
Full case name as returned by the CourtListener API. May include all party names in the original filing style. Not normalized; use for display only.
*Example:* `"Kenneth M. Zeran v. America Online, Incorporated"`

**absolute_url** (string)
Relative URL path to the CourtListener case page. Prepend `https://courtlistener.com` to form a complete URL.
*Example:* `"/opinion/748185/kenneth-m-zeran-v-america-online-incorporated/"`

---

### 1.2 Court and Date Fields

**court_id** (string)
CourtListener court identifier for the issuing court. Values in this corpus:

| Value | Court |
|-------|-------|
| `ca1` | United States Court of Appeals, First Circuit |
| `ca2` | United States Court of Appeals, Second Circuit |
| `ca3` | United States Court of Appeals, Third Circuit |
| `ca4` | United States Court of Appeals, Fourth Circuit |
| `ca5` | United States Court of Appeals, Fifth Circuit |
| `ca6` | United States Court of Appeals, Sixth Circuit |
| `ca7` | United States Court of Appeals, Seventh Circuit |
| `ca8` | United States Court of Appeals, Eighth Circuit |
| `ca9` | United States Court of Appeals, Ninth Circuit |
| `ca10` | United States Court of Appeals, Tenth Circuit |
| `ca11` | United States Court of Appeals, Eleventh Circuit |
| `cadc` | United States Court of Appeals, D.C. Circuit |
| `scotus` | Supreme Court of the United States |

**dateFiled** (string, ISO 8601 date)
Date the opinion was filed, as recorded by CourtListener. Format: YYYY-MM-DD.
*Example:* `"1997-11-12"`

---

### 1.3 Citation Fields

**citation** (string, JSON-encoded list)
All reporter citations for this case as returned by CourtListener, stored as a JSON-encoded Python list. May include parallel citations across multiple reporters. To parse: `ast.literal_eval(case["citation"])`.
*Example:* `"['129 F.3d 327', '10 Communications Reg. (P&F) 456', '1997 WL 701309']"`

**cite_count** (integer)
Total number of times this case has been cited across all CourtListener-indexed opinions, as reported by the CourtListener API at time of data collection. This is a global citation count, not restricted to the Stage 1 corpus.
*Example:* `299`

---

### 1.4 Corpus Metadata Fields

The following fields were added during corpus construction and validation. They are not present in the raw CourtListener API response.

**primary_basis** (string)
The primary subsection of § 230 applied in the appellate holding. Used to distinguish cases applying different provisions of the statute.

| Value | Meaning |
|-------|---------|
| `s230c_immunity` | § 230(c)(1) or § 230(c)(2) immunity applied as the primary basis |
| `s230c2_immunity` | § 230(c)(2) Good Samaritan blocking provision applied as primary basis |
| `s230e_fosta` | § 230(e)(5) FOSTA exception applied as primary basis |

Note: Cases coded `s230c2_immunity` and `s230e_fosta` are excluded from the restricted corpus used in dual-corpus sensitivity analysis (see research_design.md CBR-005 and script 20_dual_corpus_analysis.py).

**holding_status** (string)
Characterizes the definitiveness of the § 230 holding.

| Value | Meaning |
|-------|---------|
| `definitive` | Court issued a clear § 230 holding determining the rights or liabilities of the parties |
| `qualified` | Court engaged § 230 but the holding is qualified, remanded, or otherwise not fully resolved |

**publication_status** (string)
Publication status of the opinion. All cases in the Stage 1 corpus have value `published`. Unpublished opinions are excluded under CBR-002.

**outcome** (string)
Result of the § 230 immunity analysis for the platform or interactive computer service defendant.

| Value | Meaning |
|-------|---------|
| `platform_wins` | § 230 immunity granted; claims dismissed or judgment for defendant on § 230 grounds |
| `platform_loses` | § 230 immunity denied; claims survive or plaintiff prevails on the § 230 question |
| `mixed` | Some claims dismissed under § 230, others survive; or immunity granted on some grounds but denied on others |

**outcome_note** (string, optional)
Free-text annotation explaining the basis for the outcome coding, particularly for mixed or qualified cases. Not present for straightforward platform_wins cases. Researchers should consult the full opinion for cases with outcome_note entries.

---

## 2. Graph Files (s230_graph.gexf, s230_graph.graphml)

The citation graph is stored in two formats: GEXF (for Gephi and NetworkX) and GraphML (for general graph tools). Both files encode the same graph.

**Graph type:** Directed acyclic graph (DAG). Confirmed DAG at all stages of corpus construction.

**Node count:** 70
**Edge count:** 360

---

### 2.1 Node Attributes

Each node in the graph represents one case and carries the following attributes. Node IDs are the CourtListener cluster_id as a string.

**name** (string)
Full case name. Truncated from caseName in the validated JSON; may differ slightly in formatting.

**court** (string)
Court identifier. See court_id values in Section 1.2.

**date** (string, ISO 8601 date)
Date the opinion was filed. Corresponds to dateFiled in the validated JSON.

**cite_count** (integer)
Global CourtListener citation count at time of data collection. See cite_count in Section 1.3.

**citation** (string, JSON-encoded list)
All reporter citations. See citation in Section 1.3.

**url** (string)
Full URL to the CourtListener opinion page.

**label** (string)
Duplicate of the node ID. Present for compatibility with graph visualization tools.

---

### 2.2 Edge Attributes

Each directed edge (u → v) represents a citation from case u to case v — that is, case u cites case v in its opinion. The edge direction follows the convention that authority flows from cited to citing: an edge from u to v means u is a citing case and v is a cited (older) authority.

Edges in this corpus have no weight attribute at Stage 1. Multi-edges between the same pair of nodes are collapsed to a single edge.

**Edge sources:**
Edges were constructed from two sources, merged in script 10_merge_edges.py:
1. The `cites` field returned by the CourtListener API for each opinion (246 edges, 68.4% of final total)
2. Full-text citation extraction using the eyecite library applied to downloaded opinion text (114 additional edges, 31.6% of final total)

---

## 3. Metrics File (s230_metrics.csv)

The metrics file contains one row per case with network metrics computed from the citation graph. It is produced by script 03_compute_metrics.py.

---

### 3.1 Fields

**node_id** (integer)
CourtListener cluster ID. Primary key. Matches cluster_id in the validated JSON and the node ID in the graph files.

**case_name** (string)
Full case name. Sourced from the GEXF node attribute.

**court** (string)
Court identifier. See court_id values in Section 1.2.

**date** (string, ISO 8601 date)
Date the opinion was filed.

**url** (string)
Full URL to the CourtListener opinion page.

**pagerank** (float)
PageRank centrality score computed using the NetworkX implementation with damping factor α = 0.85 and convergence tolerance 1e-6. Scores sum to 1.0 across all nodes. Higher values indicate greater structural authority in the citation network.

Robustness: PageRank rankings are stable across damping factors α ∈ {0.75, 0.85, 0.90, 0.95} (mean Kendall τ = 0.997 across 6 pairwise comparisons). See script 13_pagerank_robustness.py and data/pagerank_robustness.json.

**in_degree** (integer)
Number of edges pointing to this node — the number of cases in the corpus that cite this case. Equivalent to in-degree centrality count (not normalized).

**betweenness** (float)
Approximate betweenness centrality, normalized by the number of node pairs. Computed using the NetworkX approximate betweenness algorithm with k=50 samples and seed=42. Measures the frequency with which a node lies on the shortest path between other node pairs.

**community** (integer)
Community assignment from the Leiden algorithm (ModularityVertexPartition, seed=42). Community IDs are integers starting at 0 and have no inherent ordering.

Community labels (from expert validation, see data/community_stability.json and v4 analysis):

| ID | Label | n |
|----|-------|---|
| 0 | Standard publisher immunity: defamation, reputation, and platform passivity | 20 |
| 1 | Early doctrinal consolidation: multi-circuit adoption of the Zeran framework, 2000-2010 | 19 |
| 2 | Platform design liability and algorithmic recommendations: the post-2015 contested frontier | 17 |
| 3 | ICP status, immunity exceptions, and platform-as-facilitator | 13 |
| 4 | Structural isolate: M.H. v. Omegle (FOSTA/design liability bridge node) | 1 |

Community stability: mean NMI = 0.686 (SD = 0.108) across 100 Leiden runs with different random seeds. Modularity Q = 0.238. See script 11_community_stability.py.

---

## 4. Supplementary Data Files

The following files in the data/ directory contain results from specific analyses. They are documented here for completeness.

| File | Produced by | Contents |
|------|-------------|----------|
| community_stability.json | 11_community_stability.py | NMI statistics across 100 Leiden runs |
| consensus_partition.json | 12_consensus_partition.py | Consensus community assignments at 80% co-assignment threshold |
| pagerank_robustness.json | 13_pagerank_robustness.py | Kendall τ across damping factors 0.75, 0.85, 0.90, 0.95 |
| mutual_information.json | 14_mutual_information.py | MI and NMI between community assignment and case outcome |
| jsd_circuits.json | 15_jensen_shannon.py | Pairwise Jensen-Shannon divergence between all circuit pairs |
| temporal_jsd.json | 16_temporal_jsd.py | Annual mean pairwise JSD, 2000-2025 |
| temporal_snapshots.json | 17_temporal_snapshots.py | Annual network metrics snapshots, 1997-2025 |
| temporal_snapshots.csv | 17_temporal_snapshots.py | Same as above in CSV format |
| recall_sample.json | 18_corpus_recall.py | Stratified sample of 19 cases used for recall estimation |
| recall_estimation.json | 19_recall_estimation.py | Recall rate estimate with Wilson 95% CI |
| dual_corpus_analysis.json | 20_dual_corpus_analysis.py | Full vs restricted corpus comparison |
| resilience_simulation.json | 21_resilience_simulation.py | Network resilience under targeted and random removal |
| dag_depth_analysis.json | save_dag_depth.py | DAG hierarchical level per node; Spearman correlation with PageRank |
| edge_sensitivity.json | 23_edge_sensitivity.py | PageRank and community stability under 10%, 20%, 30% edge removal |

---

## 5. Variable Coding Notes

**Outcome coding procedure:** Case outcomes were coded by a legal researcher using the full appellate opinion text. For cases with outcome_note entries, the note documents the specific basis for the coding decision. Mixed outcomes are recorded where the court granted immunity on some claims and denied it on others, or where the court remanded for further proceedings on immunity grounds.

**Community assignment for analysis:** The singleton Community 4 (M.H. v. Omegle) is treated analytically as belonging to Community 2 (platform design liability) in analyses requiring non-singleton communities, as documented in the expert validation findings (v4). The singleton designation in the metrics file reflects the raw Leiden output.

**Edge directionality:** Edge direction follows legal citation convention. An edge from node A to node B means case A cites case B. In DAG terminology, B is an ancestor of A. PageRank flows in the direction of citation — high-PageRank nodes are those cited by many others, not those doing the citing.

**Cluster ID stability:** CourtListener cluster IDs are stable identifiers but CourtListener occasionally merges or splits clusters. The cluster IDs in this corpus reflect the state of CourtListener as of the data pull date (2026-04-10). Researchers extending this corpus should verify cluster IDs against the CourtListener API before assuming continuity.