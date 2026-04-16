# § 230 Citation Network — Stage 1

A computational analysis of the federal appellate citation network for 47 U.S.C. § 230 of the Communications Decency Act, 1997-2025.

## Overview

This repository contains the data, code, and documentation for a citation network analysis of 70 validated federal circuit court and Supreme Court opinions applying § 230(c). The analysis applies PageRank centrality, Leiden community detection, Jensen-Shannon divergence, and temporal network analysis to characterize the structure and evolution of § 230 doctrine.

## Key findings

- Zeran v. AOL (4th Cir. 1997) holds the highest PageRank in every annual 
  snapshot from 1997 through 2025 (PR = 0.202; α = 0.85)
- Five structural clusters identified via Leiden community detection on the 
  undirected citation projection (modularity Q = 0.238; mean NMI = 0.686 
  across 100 runs), corresponding to recognizable doctrinal traditions 
  confirmed by legal expert review
- Platform win rate under § 230 declined from 83% (2000-2004, n=6) to 41% 
  (2020-2024, n=17); 2025 cases (n=4) show 25% but cell size is too small 
  for reliable inference
- Mean pairwise Jensen-Shannon divergence between circuits: 0.65 bits 
  (base 2; range 0.43-0.86)
- DAG hierarchical level correlates with PageRank at Spearman ρ = -0.965 
  (p < 0.0001), consistent with preferential attachment dynamics
- False positive rate in automated CourtListener retrieval: 66.8% (141/211 
  candidates excluded after human review)

## Repository structure

.
├── README.md
├── requirements.txt
├── research_design.md      # Inclusion criterion, exclusion patterns, CBL
├── codebook.md             # Field-level documentation for all data files
├── replication_guide.md    # Step-by-step reproduction instructions
├── raw_data/
│   └── s230_validated_20260411_030728.json   # Validated corpus (70 cases)
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

The validated corpus and graph files are deposited at Zenodo: [DOI to be added]

## Citation

[Citation to be added upon publication]

## License

Code: MIT License
Data: Creative Commons Attribution 4.0 (CC BY 4.0)