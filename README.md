# § 230 Citation Network

A computational analysis of the federal appellate citation network for 47 U.S.C. § 230 of the Communications Decency Act, 1997-2025.

## Overview

This repository contains the data, code, and documentation for a citation network analysis of 63 validated federal circuit court and Supreme Court opinions applying § 230(c). The analysis applies PageRank centrality, Leiden community detection, Jensen-Shannon divergence, and temporal network analysis to characterize the structure and evolution of § 230 doctrine.

## Key findings

- Zeran v. AOL (4th Cir. 1997) holds the highest PageRank in every annual
  snapshot from 1997 through 2025 (PR = 0.200; α = 0.85)
- Seven structural clusters identified via Leiden community detection on the
  undirected citation projection (mean NMI = 0.621 across 100 runs),
  corresponding to recognizable doctrinal traditions confirmed by legal
  expert review
- Platform win rate under § 230 declined from 80% (2000-2004, n=5) to 38%
  (2020-2024, n=16); temporal trend is consistent with increasing judicial
  skepticism toward broad immunity claims
- Mean pairwise Jensen-Shannon divergence between circuits: 0.66 bits
  (base 2; range 0.47-0.85)
- DAG hierarchical level correlates with PageRank at Spearman ρ = -0.666
  among cases with at least one inbound citation (n=41, p < 0.0001);
  full corpus ρ = -0.460 is inflated by 22 dangling nodes sharing
  identical PageRank floor values
- False positive rate in automated CourtListener retrieval: 70.1% (148/211
  candidates excluded after review)

## Repository structure

.
├── README.md
├── requirements.txt
├── research_design.md      # Inclusion criterion, exclusion patterns, CBL
├── codebook.md             # Field-level documentation for all data files
├── replication_guide.md    # Step-by-step reproduction instructions
├── raw_data/
│   └── s230_validated_20260411_030728.json   # Validated corpus (63 cases)
├── data/
│   ├── s230_graph.gexf           # Citation graph (Gephi/NetworkX)
│   ├── s230_graph.graphml        # Citation graph (GraphML)
│   ├── s230_metrics.csv          # Per-node network metrics
│   ├── case_outcomes_raw.json    # Outcome codings
│   └── [supplementary analysis files]
└── [01-23]_*.py                  # Analysis scripts in execution order

## Reproducing the analysis

See replication_guide.md for complete instructions. Quick start:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 02_build_graph.py && python3 10_merge_edges.py && python3 03_compute_metrics.py
```

## Data

The validated corpus and graph files are deposited at Zenodo: https://doi.org/10.5281/zenodo.20055182

## Citation

[Citation to be added upon publication]

## License

Code: MIT License
Data: Creative Commons Attribution 4.0 (CC BY 4.0)