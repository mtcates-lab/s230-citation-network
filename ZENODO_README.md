# Citation Network of Section 230 of the Communications Decency Act
## A Validated Corpus of Published Federal Circuit Appellate Holdings, 1997–2025

**Version:** 1.0.0  
**Date of data collection:** 2026-04-10  
**Zenodo DOI:** [reserved — fill in after deposit]  
**GitHub repository:** https://github.com/mtcates-lab/s230-citation-network  
**Contact:** mtcates@uga.edu

---

## What This Deposit Is

This deposit provides the data and code underlying a computational legal study of Section 230 of the Communications Decency Act (47 U.S.C. § 230) — the federal statute that governs the liability of online platforms for third-party content. The deposit includes a validated corpus of 70 published federal circuit and Supreme Court opinions that substantively applied § 230 immunity doctrine between 1997 and 2025, the citation network constructed from those opinions, all derived network metrics, and the complete analysis pipeline.

The corpus was constructed by retrieving 211 candidate opinions from CourtListener (courtlistener.com) and subjecting each to systematic human review against a documented operative inclusion criterion and a ten-pattern exclusion taxonomy. The false positive rate in automated retrieval was 66.8% — a methodological finding with implications for corpus construction in empirical legal studies.

---

## Inclusion Criterion

A case is included in the corpus if § 230(c)(1), § 230(c)(2), § 230(f), or § 230(e) are substantively applied in an appellate holding to determine the rights or liabilities of parties as interactive computer services or their users.

All four elements are necessary: the immunity-operative subsection must be engaged (not merely cited for background), the provision must be analyzed rather than mentioned in passing, the ruling must issue from a federal circuit court or the Supreme Court, and the § 230 analysis must be dispositive or meaningfully dispositive of the outcome.

---

## Corpus Statistics

| Metric | Value |
|--------|-------|
| Cases retrieved from CourtListener | 211 |
| Cases reviewed | 211 |
| Cases included | 70 |
| Cases excluded | 141 |
| False positive rate | 66.8% |
| Citation edges (CourtListener cites field) | 246 |
| Citation edges (after eyecite full-text extraction) | 360 |
| Edge recall rate (CourtListener cites field) | 68.4% |
| Corpus recall rate (stratified sample, n=19) | 100% (95% CI: 0.960–1.000) |
| Date range | 1997-11-12 to 2025 |
| Statute | 47 U.S.C. § 230 |

---

## File Inventory

### Core corpus files

**`raw_data/s230_validated_20260411_030728.json`**  
The validated corpus. 70 cases meeting the operative inclusion criterion, with full CourtListener metadata including case name, citation, court, date filed, docket number, and the CourtListener cites field for each opinion. This is the starting point for all downstream analysis.

**`data/s230_graph.gexf`**  
The citation network in GEXF format. 70 nodes (cases), 360 directed edges (citations), confirmed directed acyclic graph. Compatible with Gephi and networkx.

**`data/s230_graph.graphml`**  
The citation network in GraphML format. Identical graph, alternative format for interoperability.

**`data/s230_metrics.csv`**  
Per-node network metrics for all 70 cases. Columns: cluster_id, case_name, pagerank, in_degree, betweenness_centrality, community_leiden, dag_depth, outcome, circuit, year.

**`data/case_outcomes_raw.json`**  
Outcome codings for all 70 cases with annotations. Values: immunity_granted, immunity_denied, immunity_partial.

**`data/eyecite_edges.json`**  
Citation edges extracted by eyecite full-text parsing, including the 119 edges not captured by the CourtListener cites field.

**`data/eyecite_results.json`**  
Raw eyecite output for all 70 corpus opinions.

**`data/citation_lookup.json`**  
Lookup table mapping citation strings to corpus cluster IDs, used for edge resolution.

### Analysis output files

**`data/community_stability.json`** — NMI stability across 100 Leiden runs (mean NMI = 0.686, SD = 0.108)  
**`data/consensus_partition.json`** — Consensus communities at 80% co-assignment threshold (19 communities, 6 boundary cases)  
**`data/pagerank_robustness.json`** — PageRank stability across damping factors α = 0.70–0.95 (mean Kendall τ = 0.997)  
**`data/mutual_information.json`** — Mutual information between community membership and immunity outcome (NMI = 0.122)  
**`data/jsd_circuits.json`** — Pairwise Jensen-Shannon divergence between circuit citation distributions (mean JSD = 0.65)  
**`data/temporal_jsd.json`** — Annual JSD 2000–2025, tracking doctrinal divergence over time  
**`data/temporal_snapshots.json`** / **`data/temporal_snapshots.csv`** — Annual network metrics snapshots  
**`data/recall_estimation.json`** — Corpus recall estimation with Wilson confidence intervals  
**`data/recall_sample.json`** — Stratified sample of 19 cases used for recall estimation  
**`data/dual_corpus_analysis.json`** — Comparison of full corpus vs. restricted corpus (PageRank τ = 0.935)  
**`data/resilience_simulation.json`** — Network resilience under targeted vs. random node removal  
**`data/dag_depth_analysis.json`** — DAG hierarchical depth analysis (max depth 16; Spearman ρ = −0.965 with PageRank)  
**`data/edge_sensitivity.json`** — Edge sensitivity at 10%, 20%, 30% removal rates  

### Code

All scripts are numbered in execution order. See `replication_guide.md` for full usage instructions.

| Script | Purpose |
|--------|---------|
| `01_collect_data.py` | CourtListener API retrieval |
| `02_build_graph.py` | Citation network construction |
| `03_compute_metrics.py` | PageRank, centrality, Leiden communities |
| `05_deduplicate.py` | Duplicate cluster detection |
| `06_validate_corpus.py` | Automated candidate flagging |
| `07_add_metadata.py` | Metadata and outcome coding |
| `08_eyecite_extraction.py` | Full-text citation extraction |
| `09_build_edges_from_eyecite.py` | Edge construction from eyecite output |
| `10_merge_edges.py` | Edge list consolidation |
| `11_community_stability.py` | NMI stability across Leiden seeds |
| `12_consensus_partition.py` | Consensus community detection |
| `13_pagerank_robustness.py` | PageRank damping factor sensitivity |
| `14_mutual_information.py` | MI between community and outcome |
| `15_jensen_shannon.py` | JSD between circuit distributions |
| `16_temporal_jsd.py` | Temporal JSD analysis |
| `17_temporal_snapshots.py` | Annual network snapshots |
| `18_corpus_recall.py` | Recall sample generation |
| `19_recall_estimation.py` | Wilson CI recall computation |
| `20_dual_corpus_analysis.py` | Full vs. restricted corpus comparison |
| `21_resilience_simulation.py` | Resilience simulation |
| `23_edge_sensitivity.py` | Edge sensitivity analysis |

### Documentation

**`research_design.md`** — Complete methodology document: operative inclusion criterion, ten corpus boundary decisions, ten exclusion patterns with rationale and network-science implications, case-by-case Corpus Boundary Log (CBL), and corpus statistics.

**`replication_guide.md`** — Step-by-step reproduction instructions for all analyses.

**`codebook.md`** — Variable definitions and coding rules for all data files.

**`requirements.txt`** — Pinned Python dependencies.

---

## How to Cite This Deposit

> Cates, M. (2026). *Citation Network of Section 230 of the Communications Decency Act: A Validated Corpus of Published Federal Circuit Appellate Holdings, 1997–2025* (Version 1.0.0) [Dataset]. Zenodo. https://doi.org/[DOI to be added]

---

## Data Availability Statement

For use in papers citing this dataset:

> All data and code supporting this analysis are publicly available at Zenodo (DOI: [to be added]). The deposit includes the validated corpus of 70 included cases, the citation network in GEXF and GraphML formats, all derived network metrics, and the complete analysis pipeline. The corpus was constructed from CourtListener (courtlistener.com), maintained by the Free Law Project.

---

## License

Data and documentation: Creative Commons Attribution 4.0 International (CC BY 4.0).  
Code: MIT License.

---

## Key Finding for Verification

Replicators running the full pipeline from scratch should obtain PageRank = 0.2020 for Zeran v. AOL (4th Cir. 1997), which ranks first among all 70 corpus nodes. The top-10 PageRank ranking is documented in `replication_guide.md` Section 13.
