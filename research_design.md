# Research Design: § 230 Citation Network — Stage 1

**Project:** Computational Legal Studies: Mapping the Citation Network of US Internet Law
**Stage:** 1 — § 230(c) Core Corpus
**Last updated:** 2026-04-14

---

## 1. Operative Inclusion Criterion

A case is included in the Stage 1 corpus if § 230(c)(1), § 230(c)(2), § 230(f), or § 230(e) are substantively applied in an appellate holding to determine the rights or liabilities of parties as interactive computer services or their users.

All four elements are necessary:

- **§ 230(c), (f), or (e)** — the immunity-operative subsections. Policy findings (§ 230(a)) and congressional purposes (§ 230(b)) alone are not sufficient.
- **Substantively applied** — the provision must be analyzed, not merely cited for background, definition, or dicta. Block citations without independent analysis do not satisfy this element.
- **In an appellate holding** — the ruling must issue from a federal circuit court or the Supreme Court. District court analysis is excluded at Stage 1.
- **To determine the rights or liabilities of parties** — the § 230 analysis must be dispositive or meaningfully dispositive of the outcome. Alternative-ground applications relegated to dicta are excluded.

**Positive examples:** *Zeran v. AOL* (4th Cir. 1997); *Carafano v. Metrosplash* (9th Cir. 2003); *Fair Housing Council v. Roommates.com* (9th Cir. 2008) (en banc); *Force v. Facebook* (2d Cir. 2020); *Enigma Software Group USA v. Malwarebytes* (9th Cir. 2023).

---

## 2. Corpus Boundary Decisions

### CBR-001: Court Level — Circuit and Supreme Court Only (Stage 1)

**Decision:** Stage 1 includes only published opinions from the federal circuit courts of appeals and the Supreme Court. District court opinions are excluded.

**Rationale:** Citation in the American common-law system carries hierarchical weight. Circuit opinions bind district courts within the circuit and persuade courts elsewhere; district opinions are neither binding nor uniformly reported. Including district courts would require modeling two qualitatively different node types in the same graph, would introduce CourtListener coverage heterogeneity at the district level, and would complicate interpretation of centrality measures. A circuit-level graph in which every node is a binding precedential act and every edge connects legally equivalent authority types is methodologically cleaner and more interpretable.

**Methods section language:** "We restricted the corpus to published opinions issued by the United States Courts of Appeals and the Supreme Court. District court opinions were excluded to maintain consistency in the precedential weight of nodes and to avoid coverage heterogeneity in the CourtListener database at the district level."

**JAIL reviewer note:** Ardia (2010) included district courts. This corpus is not directly comparable to Ardia's at the district level. The difference is methodologically justified and should be stated explicitly in the paper.

### CBR-002: Publication Status — Published Opinions Only

**Decision:** Only opinions designated as "published" (or "for publication") by the issuing circuit are included. Unpublished memoranda dispositions are excluded.

**Rationale:** Post-FRAP 32.1 (2007), unpublished opinions are technically citeable but carry no precedential weight. Pre-2007, unpublished opinions were prohibited from citation in many circuits. Including unpublished opinions would introduce nodes that cannot legally function as authority in the citation network and would contaminate the DAG structure with edges that courts are not required to acknowledge.

### CBR-003: Date Range — 1997 to Present

**Decision:** The corpus begins with *Zeran v. AOL*, 129 F.3d 327 (4th Cir. 1997), the first published circuit opinion applying § 230(c)(1). The end date is the date of data collection.

**Rationale:** § 230 was enacted in February 1996. The first circuit-level application is *Zeran* (November 1997). Starting at *Zeran* is appropriate because it establishes the doctrinal framework that all subsequent cases engage with; starting at enactment would add cases with no network edges.

### CBR-004: State Courts — Excluded from Stage 1; Flagged for Stage 4

**Decision:** State appellate court opinions are excluded from Stage 1 regardless of whether they substantively apply § 230. Flagged for potential inclusion in Stage 4.

### CBR-005: Edge Typing — Directed, Unweighted at Stage 1

**Decision:** Edges are directed (citing case → cited case) and unweighted at Stage 1. Multi-edges are collapsed to single edges. The authority-differential weight schema from Coupette et al. (2024) is reserved for Stage 2 analysis.

---

## 3. Exclusion Patterns

The following ten patterns describe categories of cases that contain a textual reference to § 230 but do not satisfy the operative inclusion criterion. Every case retrieved by the automated pipeline must be reviewed against these patterns before inclusion.

The patterns were developed inductively by reviewing 211 cases retrieved from CourtListener. They are mutually exclusive in design but can overlap in application; the first applicable pattern is recorded for coding purposes.

---

### Pattern 1: § 230(b) as Legislative Background or Policy Context

**Description:** The case cites § 230(a) or § 230(b) to establish legislative background or support a policy argument, without invoking § 230(c) immunity doctrine. The § 230 reference functions as contextual framing rather than as an operative legal rule.

**Why excluded:** Subsections (a) and (b) are non-operative legislative findings. A case that recites Congress's intent to preserve the Internet as a competitive free market has not adjudicated any party's immunity, has not determined whether any defendant qualifies as an interactive computer service, and has not applied any element of the three-part § 230(c)(1) test. Including these cases would insert nodes with outbound edges to § 230 policy text but no doctrinal weight as § 230 holdings.

**Network science implication:** Mistaken inclusion creates phantom policy nodes — cases that appear connected to the § 230 doctrine cluster through statutory citation but share no doctrinal content with the immunity cases. This distorts community detection, inflates betweenness centrality for cases straddling policy and immunity clusters, and contaminates information-theoretic analysis by introducing non-doctrine signal.

**Concrete examples:** *Gulf Power Co. v. FCC* (11th Cir. 2000) — § 230(b) cited for deregulatory policy in a pole attachment dispute; *Bell Atlantic v. FCC* (D.C. Cir. 1999) — § 230(b) cited for broadband policy context in a common carrier proceeding; *Mozilla Corp. v. FCC* (D.C. Cir. 2019) — § 230(b) cited in a net neutrality challenge; *Howard v. AOL* (5th Cir. 2000) — § 230(b) in dicta to explain CDA background, primary holding on other grounds.

---

### Pattern 2: § 230(c) Cited at District Level but Not Adjudicated on Appeal

**Description:** The district court applied § 230(c) and the issue was before the circuit court, but the circuit court disposed of the appeal on other grounds. The appellate record contains a substantive § 230 analysis, but it is in the district court opinion, not in the appellate holding.

**Why excluded:** The corpus is limited to appellate holdings. A district court opinion, however thorough, is excluded under CBR-001. An appellate opinion that affirms without reaching § 230 does not constitute an appellate § 230 holding.

**Network science implication:** Including such a case inserts a node whose doctrinal content sits at a different court level than the edge type implies. The resulting edge would suggest circuit-level endorsement of § 230 doctrine where only district-level analysis exists — an edge-validity problem.

**Concrete examples:** *Rosetta Stone Ltd. v. Google Inc.* (4th Cir. 2012) — district court granted § 230 immunity; Fourth Circuit resolved on trademark law grounds; *Knapke v. PeopleConnect, Inc.* (9th Cir. 2022) — § 230 upheld at district level; circuit court resolved on arbitration grounds.

---

### Pattern 3: § 230(c) as Alternative Ground — Appeal Decided Primarily Elsewhere

**Description:** The appellate court acknowledges § 230 as a potentially available defense but affirms or reverses on independent, non-§ 230 grounds. The § 230 analysis, if it appears at all, is dicta.

**Why excluded:** A § 230 analysis in dicta does not determine the rights or liabilities of parties. Courts sometimes include brief § 230 observations without examining all three elements of the § 230(c)(1) test, making dicta-only cases unreliable as doctrine. Including them would add nodes that generate outbound edges toward true § 230 doctrine nodes while contributing no § 230 holding of their own.

**Network science implication:** This is the most consequential false-positive pattern for corpus validity. Pattern 3 cases generate outbound citation edges toward the core § 230 precedent cluster without constituting § 230 applications. In the citation DAG they would appear as legitimate precursors to the doctrine cluster, inflating in-degree of core cases and distorting PageRank throughout the network. Human review at this decision point is irreplaceable.

**Concrete examples:** *Nieman v. VersusLaw, Inc.* (9th Cir. 2013) — resolves on contract grounds; *Seaton v. TripAdvisor, LLC* (6th Cir. 2013) — resolved on opinion doctrine; *Levitt v. Yelp! Inc.* (9th Cir. 2014) — dismissed on antitrust pleading failure; *Hiam v. Homeaway.com, Inc.* (1st Cir. 2018) — affirmed on FHA standing grounds; *Fields v. Twitter, Inc.* (9th Cir. 2018) — ATA proximate cause fails before § 230; *Crosby v. Twitter, Inc.* (6th Cir. 2019) — primary holding on ATA causation; *Baldino's Lock & Key Service v. Google LLC* (D.C. Cir. 2018) — antitrust pleading failure; *Garcia v. Google, Inc.* (9th Cir. 2015) — copyright preliminary injunction, § 230 in dissent only.

---

### Pattern 4: § 230(b) Adjudicated as Putative Agency Authority

**Description:** A federal agency invoked § 230(b)'s policy language as a source of rulemaking authority or statutory support for a regulatory program. The court adjudicates whether § 230(b) can ground regulatory power, typically concluding it cannot.

**Why excluded:** These cases adjudicate the administrative law question of what § 230(b) means for agency power, not whether any party is immune from civil liability as a publisher or speaker. The judicial analysis is structurally an APA/Chevron/major-questions analysis, not a tort or civil liability analysis. These cases belong to the telecommunications regulatory corpus (Stage 5).

**Network science implication:** Pattern 4 cases form a coherent but distinct doctrinal cluster — the telecommunications-regulatory interpretation of § 230 rather than the civil immunity interpretation. Including them would create a false community connecting the civil immunity cluster with the administrative law cluster, suggesting doctrinal integration that does not exist.

**Concrete examples:** *Comcast Corp. v. FCC* (D.C. Cir. 2010) — § 230(b) cannot serve as source of FCC ancillary jurisdiction; *United States Telecom Ass'n v. FCC* (D.C. Cir. 2016, en banc) — § 230(b) addressed in Title II reclassification context; *Ohio Telecom Ass'n v. FCC* (6th Cir. 2022) — § 230(b) in broadband regulatory classification.

---

### Pattern 5: State § 230 Homonym

**Description:** The case cites a state statute numbered § 230 in its statutory scheme, with no reference to 47 U.S.C. § 230. The numerical coincidence creates a false positive when queries are not filtered by statutory title and section.

**Why excluded:** The case does not cite or apply 47 U.S.C. § 230. The § 230 reference is to a different statute in an unrelated subject-matter area. Inclusion would be a category error.

**Network science implication:** A Pattern 5 case would inject a node from a completely unrelated doctrinal area into the § 230 citation network. Any edges from this node would carry zero legal signal and would distort every network metric.

**Concrete examples:** *Tyler v. Armstrong* (3d Cir. 2004) — § 230 cited is California Civil Code § 230, a repealed legitimation statute; the case is a Virgin Islands inheritance dispute; *United States v. Dotson* (5th Cir. 2009) — § 230 cited is Louisiana Revised Statute § 22:230(C), an insurance regulation; *National Railroad Passenger Corp. v. Julie Su* (9th Cir. 2022) — § 230 cited is California Labor Code § 230, a domestic violence employee protection statute.

---

### Pattern 6: Definitional Borrowing of § 230(f)(2)

**Description:** The court imports the § 230(f)(2) definition of "interactive computer service" into an unrelated statutory or regulatory context without applying § 230 immunity doctrine. The citation is to the definitional subsection as a statutory shorthand, not as part of a § 230(c) analysis.

**Why excluded:** Borrowing a definition from § 230(f)(2) is not an application of § 230 immunity. The three-part § 230(c)(1) analysis is not engaged. Including such cases would suggest that § 230's definitional reach has network significance that it does not have as a matter of doctrine.

**Network science implication:** Pattern 6 cases function as definitional bridges between the § 230 immunity cluster and unrelated clusters. Inclusion would create spurious inter-cluster edges, inflate betweenness centrality for § 230(f)(2)-related nodes, and falsely suggest the ICS definition is a doctrinal conduit between immunity doctrine and unrelated areas.

**Concrete examples:** *United States v. Dodds* (9th Cir. 2011) — § 230(f)(2) borrowed to define "interactive computer service" for child pornography jurisdiction; *United States v. Hanny* (9th Cir. 2012) — § 230(f)(2) consulted in sentencing guidelines interpretation; *Ohio Telecom Ass'n v. FCC* (6th Cir. 2022) — § 230(f)(2) used in Title II classification analysis.

---

### Pattern 7: § 230 Raised and Expressly Reserved

**Description:** The appellate court explicitly acknowledges § 230 immunity was argued but declines to reach it, resolving on other grounds. Unlike Pattern 3, Pattern 7 cases include an explicit statement that § 230 is being left open.

**Why excluded:** An express reservation is the court's affirmative statement that no § 230 holding is being made. Pattern 7 cases carry negative information about § 230 — they mark the boundary of existing holdings — but they do not extend the doctrine.

**Network science implication:** Pattern 7 cases are among the more dangerous false positives because their explicit § 230 discussion makes them appear substantive on text-based retrieval. Including them would create high-degree nodes that are doctrinally empty and would corrupt betweenness centrality by inserting phantom bridge nodes between true doctrine nodes.

**Concrete examples:** *S.J.W. v. Lee's Summit R-7 School District* (8th Cir. 2011) — § 230 raised, court resolves on First Amendment grounds and reserves § 230; *NetChoice, LLC v. Bonta* (9th Cir. 2023) — § 230 preemption raised, court resolves on First Amendment grounds and expressly reserves; *Boshears v. PeopleConnect, Inc.* (9th Cir. 2023) — § 230 raised, court resolves on state law grounds.

---

### Pattern 8: Doctrinal Adjacency

**Description:** The case concerns internet platforms, content moderation, or online speech, but § 230(c) immunity doctrine does not appear in the appellate holding. The case may reference the CDA or involve the same defendant platforms as core § 230 cases, but its legal analysis proceeds on other grounds entirely: First Amendment, APA, antitrust, or statutory interpretation of a different provision.

**Why excluded:** Doctrinal adjacency is not doctrinal connection. Two cases that both involve Facebook as a defendant, or both concern content moderation, do not share § 230 doctrine on that basis alone. Pattern 8 cases satisfy none of the four elements of the inclusion criterion and represent the largest false-positive category by volume.

**Network science implication:** Because Pattern 8 cases often involve the same defendants and factual settings as true § 230 cases, they cite many of the same precedents on unrelated grounds and appear highly connected to the § 230 cluster in a naive citation analysis. Inclusion would merge the First Amendment platform-regulation cluster with the § 230 immunity cluster, producing a single mega-community that conflates two doctrinally separate areas of internet law.

**Concrete examples:** *Reno v. ACLU* (SCOTUS 1997) — First Amendment challenge to CDA indecency provisions; *Ashcroft v. ACLU* (SCOTUS 2004) — First Amendment COPA challenge; *Moody v. NetChoice, LLC* (SCOTUS 2024) — First Amendment platform editorial discretion; *Murthy v. Missouri* (SCOTUS 2024) — First Amendment government coercion; *Knight First Amendment Institute v. Trump* (2d Cir. 2019) — public forum doctrine; *AAPS v. Schiff* (D.C. Cir. 2022) — First Amendment; *NetChoice, LLC v. AG of Florida* (11th Cir. 2022) — First Amendment; *NetChoice, LLC v. Paxton* (5th Cir. 2023) — First Amendment compelled speech; *IMDb.com Inc. v. Becerra* (9th Cir. 2020) — First Amendment age disclosure; *La Liberte v. Reid* (2d Cir. 2020) — First Amendment anti-SLAPP; *Fox v. Amazon.com, Inc.* (6th Cir. 2019) — products liability; *Freedom Watch, Inc. v. Google LLC* (D.C. Cir. 2019) — antitrust.

---

### Pattern 9: Vacated Appellate Opinion

**Description:** The appellate opinion was issued and may have applied § 230(c) substantively, but the judgment was subsequently vacated by a higher court. A vacated judgment carries no precedential effect and cannot function as a doctrine-generating node in the citation network.

**Why excluded:** The corpus represents the network of binding doctrine. A vacated opinion has been formally annulled. It cannot ground legal argument in subsequent cases. Including vacated opinions would insert nodes that appear doctrinally authoritative in text but are legally inert.

**Network science implication:** A vacated opinion that applied § 230 would appear as a well-connected precedent node but would receive no further citation inflows after vacatur. Its temporal citation profile would show an abrupt cessation of inbound citations that could be mistaken for declining doctrinal relevance rather than legal nullification.

**Concrete examples:** *Knight First Amendment Institute v. Trump*, 928 F.3d 226 (2d Cir. 2019), vacated, 141 S. Ct. 1220 (2021) — Second Circuit held Trump's blocking of critics violated the First Amendment's public forum doctrine; Supreme Court vacated as moot. This case is already excluded under Pattern 8; Pattern 9 provides an independent ground and illustrates the category for future cases where a § 230-applying circuit opinion is later vacated.

---

### Pattern 10: § 230(c)(1) Held Affirmatively Inapplicable to Claim Type

**Description:** The court affirmatively rules that § 230(c)(1) is inapplicable to the type of liability at issue because the claim does not depend on the defendant's role as a publisher or speaker of third-party content. This is a holding about § 230's reach, not an application of the immunity.

**Why excluded:** The inclusion criterion requires § 230(c)(1) to be substantively applied to determine the rights or liabilities of parties. A ruling that § 230(c)(1) has no application to a given claim type is a ruling about the statute's scope. No party receives immunity. The holding generates a boundary condition on § 230's domain rather than an instance of its operation. Pattern 10 is analytically distinct from Pattern 3 (§ 230 could apply but the court takes another path), Pattern 7 (court expressly reserves the question), and Pattern 8 (§ 230 absent from the holding).

**Network science implication:** Pattern 10 cases are boundary-condition nodes that define the outer edge of the § 230 immunity graph. Including them would mislocate the corpus boundary and connect cases from adjacent legal contexts via a "scope ruling" edge qualitatively different from an "immunity granted" or "immunity denied" edge. If the project eventually models § 230's scope as a variable, Pattern 10 cases would be the appropriate dataset for that analysis, modeled as a distinct node type.

**Concrete examples:** *City of Chicago v. StubHub!, Inc.*, 624 F.3d 363 (7th Cir. 2010) (Easterbrook, J.) — Seventh Circuit held § 230(c) "irrelevant" to a tax collection dispute because "the amusement tax does not depend on who 'publishes' information." StubHub's liability turns on whether it is a ticket seller, not on its role as a publisher of third-party content. The ruling is authoritative on § 230's scope but constitutes no application of § 230 immunity.

---

## 4. Exclusion Patterns Summary Table

| # | Pattern Name | Trigger | Inclusion Criterion Element Failed | Canonical Examples |
|---|---|---|---|---|
| 1 | § 230(b) legislative background | Cites § 230(a)/(b) for policy context only | Not § 230(c)/(f)/(e) | *Gulf Power*, *Bell Atlantic*, *Mozilla v. FCC*, *Howard v. AOL* |
| 2 | § 230(c) district-only, not reached on appeal | District court applied § 230; circuit resolves elsewhere | Not an appellate holding | *Rosetta Stone* (4th Cir.), *Knapke v. PeopleConnect* |
| 3 | § 230(c) as alternative/dicta ground | Circuit resolves on independent non-§ 230 grounds | Not substantively applied / not dispositive | *Nieman*, *Seaton*, *Levitt*, *Hiam*, *Fields*, *Crosby*, *Baldino's*, *Garcia* |
| 4 | § 230(b) as putative agency authority | Agency invokes § 230(b) as rulemaking authority | Not § 230(c)/(f)/(e) | *Comcast v. FCC*, *US Telecom v. FCC*, *Ohio Telecom v. FCC* |
| 5 | State § 230 homonym | Case cites state statute numbered § 230, not 47 U.S.C. § 230 | Not § 230 of the CDA | *Tyler v. Armstrong*, *US v. Dotson*, *Nat'l Railroad v. Su* |
| 6 | Definitional borrowing of § 230(f)(2) | Court borrows ICS definition for unrelated statutory purpose | Not substantively applied | *US v. Dodds*, *US v. Hanny*, *Ohio Telecom v. FCC* |
| 7 | § 230 raised and expressly reserved | Court acknowledges § 230 argument, explicitly declines to reach it | Not substantively applied / not a holding | *S.J.W. v. Lee's Summit*, *NetChoice v. Bonta*, *Boshears v. PeopleConnect* |
| 8 | Doctrinal adjacency | Same legislative environment, overlapping platform defendants, zero § 230 in appellate holding | Not applied at all | *Reno v. ACLU*, *Ashcroft v. ACLU*, *Moody v. NetChoice*, *Murthy v. Missouri*, *Knight v. Trump*, *AAPS v. Schiff*, *NetChoice v. AG FL*, *NetChoice v. Paxton*, *IMDb v. Becerra*, *La Liberte v. Reid*, *Fox v. Amazon*, *Freedom Watch v. Google* |
| 9 | Vacated appellate opinion | Judgment vacated by higher court | Not a valid holding | *Knight v. Trump* (2d Cir. 2019, vacated 2021) |
| 10 | § 230(c)(1) held affirmatively inapplicable | Court rules § 230(c) is the wrong legal tool for the claim type | Not applied (scope-boundary ruling) | *City of Chicago v. StubHub!* (7th Cir. 2010) |

---

## 5. Stage Flags for Excluded Cases

The following cases are excluded from Stage 1 but flagged for potential inclusion in later stages. Stage assignment reflects the doctrinal cluster that best characterizes each excluded case.

**Stage 2 — DMCA § 512 cases:**

| Case | Exclusion Pattern | Stage 2 Inclusion Note |
|---|---|---|
| *Garcia v. Google, Inc.* (9th Cir. 2015) | Pattern 3 | DMCA § 512 copyright claim was the primary ground |

**Stage 3 — First Amendment digital doctrine and government jawboning cases:**

| Case | Exclusion Pattern | Stage 3 Inclusion Note |
|---|---|---|
| *Reno v. ACLU* (SCOTUS 1997) | Pattern 8 | First Amendment anchor case for internet speech doctrine |
| *Ashcroft v. ACLU* (SCOTUS 2004) | Pattern 8 | First Amendment / COPA challenge |
| *Knight First Amendment Institute v. Trump* (2d Cir. 2019, vacated 2021) | Patterns 8 + 9 | Public forum doctrine; vacated as moot — historical-only node |
| *AAPS v. Schiff* (D.C. Cir. 2022) | Pattern 8 | First Amendment / government speech pressure |
| *NetChoice, LLC v. AG of Florida* (11th Cir. 2022) | Pattern 8 | First Amendment platform regulation |
| *NetChoice, LLC v. Paxton* (5th Cir. 2023) | Pattern 8 | First Amendment compelled speech |
| *NetChoice, LLC v. Bonta* (9th Cir. 2023) | Pattern 7 | § 230 raised and reserved; First Amendment primary ground |
| *X Corp. v. Bonta* | Pattern 7 | First Amendment / § 230 reserved |
| *Moody v. NetChoice, LLC* (SCOTUS 2024) | Pattern 8 | First Amendment platform editorial discretion |
| *Murthy v. Missouri* (SCOTUS 2024) | Pattern 8 | First Amendment government coercion / jawboning |
| *Volokh v. James* (2d Cir. 2025) | Pattern 8 | First Amendment / NY HALT Act challenge |
| *Free Speech Coalition, Inc. v. Paxton* (SCOTUS 2025) | Pattern 8 | First Amendment / online age verification |
| *Freedom Watch, Inc. v. Google LLC* (D.C. Cir. 2019) | Pattern 8 | Antitrust / First Amendment; no § 230 engagement |
| *Baldino's Lock & Key Service v. Google LLC* (D.C. Cir. 2018) | Pattern 3 | Antitrust; government contracting context |
| *IMDb.com Inc. v. Becerra* (9th Cir. 2020) | Pattern 8 | First Amendment / California age disclosure law |
| *La Liberte v. Reid* (2d Cir. 2020) | Pattern 8 | First Amendment anti-SLAPP |
| *Kutchinski v. Freeland Community School District* (6th Cir. 2023) | Pattern 8 | First Amendment student speech |
| *S.J.W. v. Lee's Summit R-7 School District* (8th Cir. 2011) | Pattern 7 | First Amendment student speech; § 230 expressly reserved |
| *Boshears v. PeopleConnect, Inc.* (9th Cir. 2023) | Pattern 7 | § 230 raised and reserved; arbitration primary ground |

**Stage 4 — State court decisions:**

*(No state cases reviewed for Stage 1. Stage 4 entries will be added as the corpus expansion proceeds.)*

**Stage 5 — Telecommunications regulatory cases:**

| Case | Exclusion Pattern | Stage 5 Inclusion Note |
|---|---|---|
| *Comcast Corp. v. FCC* (D.C. Cir. 2010) | Pattern 4 | FCC ancillary jurisdiction / broadband |
| *United States Telecom Ass'n v. FCC* (D.C. Cir. 2016) | Pattern 4 | Net neutrality / Title II reclassification |
| *Ohio Telecom Ass'n v. FCC* (6th Cir. 2022) | Patterns 4 + 6 | Broadband classification; § 230(f)(2) borrowed |
| *Mozilla Corp. v. FCC* (D.C. Cir. 2019) | Pattern 1 | Net neutrality; § 230(b) policy context only |
| *Gulf Power Co. v. FCC* (11th Cir. 2000) | Pattern 1 | Pole attachment / broadband policy |
| *Bell Atlantic v. FCC* (D.C. Cir. 1999) | Pattern 1 | Common carrier / broadband policy |

**No stage flag — excluded without forward assignment:**

| Case | Pattern | Reason |
|---|---|---|
| *Tyler v. Armstrong* (3d Cir. 2004) | Pattern 5 | Cal. Civ. Code § 230 homonym; Virgin Islands inheritance |
| *United States v. Dotson* (5th Cir.) | Pattern 5 | La. Rev. Stat. § 22:230(C) homonym; criminal case |
| *National Railroad Passenger Corp. v. Su* (9th Cir.) | Pattern 5 | Cal. Lab. Code § 230 homonym; RUIA preemption |
| *United States v. Dodds* (9th Cir.) | Pattern 6 | § 230(f)(2) borrowed for child pornography jurisdiction |
| *United States v. Hanny* (9th Cir.) | Pattern 6 | § 230(f)(2) borrowed for sentencing guidelines |
| *Nieman v. VersusLaw, Inc.* (9th Cir.) | Pattern 3 | Contract grounds; no § 230 holding |
| *Seaton v. TripAdvisor, LLC* (6th Cir.) | Pattern 3 | Opinion doctrine; no forward flag |
| *Levitt v. Yelp! Inc.* (9th Cir.) | Pattern 3 | Antitrust pleading; no forward flag |
| *Hiam v. Homeaway.com* (1st Cir.) | Pattern 3 | FHA standing; no forward flag |
| *Fields v. Twitter, Inc.* (9th Cir.) | Pattern 3 | ATA causation; no forward flag |
| *Crosby v. Twitter, Inc.* (6th Cir.) | Pattern 3 | ATA causation; no forward flag |
| *Fox v. Amazon.com, Inc.* (6th Cir.) | Pattern 8 | Products liability; no platform-specific doctrine |
| *Howard v. AOL* (5th Cir.) | Pattern 1 | § 230(b) dicta; no forward flag |
| *City of Chicago v. StubHub!* (7th Cir.) | Pattern 10 | § 230 scope boundary ruling; tax/commercial dispute |

---

## 6. Corpus Evolution

### 6.1 Methodological Finding: False Positive Rate in Automated Retrieval

The Stage 1 corpus construction began with automated retrieval from the CourtListener API using queries targeting federal circuit court and Supreme Court opinions citing 47 U.S.C. § 230. The initial retrieval returned 211 candidate cases.

Each candidate was then subjected to full-text review against the operative inclusion criterion and the ten exclusion patterns. This review was conducted by a human annotator with legal expertise, examining the appellate holding of each case to determine whether § 230(c)(1), § 230(c)(2), § 230(f), or § 230(e) was substantively applied to determine the rights or liabilities of parties.

Following review, 70 cases were confirmed as meeting the inclusion criterion.

**False positive rate: 66.8%** ((211 − 70) / 211 = 141 / 211 ≈ 0.668).

This false positive rate has three implications:

1. **Automated retrieval alone is insufficient for corpus construction in empirical legal studies.** A corpus built without human review would contain approximately two-thirds non-§ 230 cases, corrupting all downstream network metrics.

2. **The dominant false positive mechanism is doctrinal adjacency (Pattern 8).** Cases from First Amendment platform-regulation doctrine, government jawboning, and net neutrality share defendants, legislative context, and citation environments with § 230 cases, making them difficult to distinguish by automated text analysis. NLP classifiers trained on term frequency would likely reproduce a similar false positive rate.

3. **The second dominant mechanism is the alternative-ground exclusion (Pattern 3).** This is the most legally subtle category: cases where § 230 was genuinely at issue but was not reached by the appellate court. Exclusion requires doctrinal judgment about what constitutes a holding versus dicta, a judgment not reducible to text features.

### 6.2 Corpus Statistics (Stage 1, as of data collection)

| Metric | Value |
|---|---|
| Cases retrieved from CourtListener | 211 |
| Cases reviewed | 211 |
| Cases included (meeting operative criterion) | 70 |
| Cases excluded | 141 |
| False positive rate | 66.8% |
| Citation edges (CourtListener cites field) | 246 |
| Citation edges (after Eyecite full-text extraction) | 360 |
| Edge recall rate (CourtListener cites field) | 68.4% |
| Corpus recall rate (stratified sample, n=19) | 100% (95% CI: 0.959, 1.000) |
| Date of data pull | 2026-04-10 |
| eyecite version | 2.6.0 |

### 6.3 Comparison with Ardia (2010)

Cross-referencing our corpus against Ardia (2010) confirms that our corpus contains all published federal circuit opinions in Ardia's corpus that substantively applied § 230 in an appellate holding. Two cases in Ardia's corpus are absent from ours for methodologically justified reasons: *Almeida v. Amazon.com*, 456 F.3d 1316 (11th Cir. 2006), where the Eleventh Circuit dismissed on the merits without reaching § 230 (Pattern 3 exclusion), and the vacated *Roommates.com* panel opinion, 489 F.3d 921 (9th Cir. 2007), superseded by the en banc decision already in our corpus.

Our corpus extends Ardia's temporal coverage by approximately fifteen years, adding 55 cases decided after his September 2009 cutoff. The methodological difference between Ardia's invocation-based inclusion criterion and our holding-based criterion accounts for the two-case discrepancy; this difference is a feature, not a limitation, and should be described explicitly in the paper.

### 6.4 Implications for Publication

The 66.8% false positive rate should be presented in the methods section and discussed in the results section as a substantive finding about the difference between citation-presence and doctrinal application in US internet law. Reviewers at JAIL and Scientific Data will recognize this as a genuine empirical contribution to the methodology of computational legal studies: we demonstrate that the set of cases citing § 230 and the set of § 230 doctrine cases are substantially different, and we provide a validated ten-pattern taxonomy explaining why.

The ten-pattern exclusion taxonomy is a reusable instrument for future empirical legal studies of statutory citation networks.

### 6.5 Future Corpus Evolution Tracking

As the research program advances through Stages 2–5, this section will record the number of cases flagged from Stage 1 exclusions that were subsequently included in later stages, false positive rates at each subsequent stage, any new exclusion patterns identified, and changes to the total corpus size as additional doctrinal areas are added.

---

## 7. Corpus Boundary Decisions Log (CBL)

Individual case-level inclusion/exclusion decisions are documented here in chronological order as they are made.

### CBL-001 — *Tyler v. Armstrong*, No. 02-3961 (3d Cir. 2004)
**Status:** EXCLUDED | **Pattern:** 5 | **Date:** 2026-04-10
Cal. Civ. Code § 230 homonym; Virgin Islands legitimation/inheritance dispute with no internet law content. Demonstrates why structured citation parsing is required.

### CBL-002 — *Roskowski v. Corvallis Police Officers' Ass'n*, No. 05-35737 (9th Cir. 2007)
**Status:** EXCLUDED | **Pattern:** 3 | **Date:** 2026-04-10
Unpublished memorandum. § 230 cited in block citation without independent doctrinal analysis; primary holdings turn on actual malice doctrine. Also excluded under CBR-002 (unpublished).

### CBL-003 — *United States Telecom Ass'n v. FCC*, 825 F.3d 674 (D.C. Cir. 2016)
**Status:** EXCLUDED | **Pattern:** 4 | **Stage flag:** 5 | **Date:** 2026-04-10
Net neutrality / Title II reclassification. § 230(b) cited for deregulatory policy; § 230(f)(2) borrowed for definitional purposes. No § 230(c) immunity analysis. Flagged for Stage 5 telecommunications corpus.

### CBL-004 — *National Railroad Passenger Corp. v. Su*, (9th Cir.)
**Status:** EXCLUDED | **Pattern:** 5 | **Date:** 2026-04-10
Cal. Lab. Code § 230 homonym; RUIA preemption case with no internet law content.

### CBL-005 — *City of Chicago v. StubHub!, Inc.*, 624 F.3d 363 (7th Cir. 2010)
**Status:** EXCLUDED | **Pattern:** 10 | **Date:** 2026-04-11
Judge Easterbrook holds § 230(c) "irrelevant" to tax collection dispute because liability does not depend on defendant's role as publisher or speaker. Canonical Pattern 10 case.

### CBL-006 — *Knight First Amendment Institute v. Trump*, 928 F.3d 226 (2d Cir. 2019), vacated, 141 S. Ct. 1220 (2021)
**Status:** EXCLUDED | **Patterns:** 8 + 9 | **Stage flag:** 3 (historical only, vacated) | **Date:** 2026-04-11
Public forum doctrine / First Amendment; no § 230 engagement. Vacated by SCOTUS as moot. Double exclusion: Pattern 8 (no § 230) and Pattern 9 (vacated judgment). Flagged for Stage 3 as historical-context-only node.

### CBL-007 — *Reno v. ACLU*, 521 U.S. 844 (1997)
**Status:** EXCLUDED | **Pattern:** 8 | **Stage flag:** 3 | **Date:** 2026-04-11
Concerns §§ 223(a) and 223(d), not § 230(c). No § 230 holding. Deferred to Stage 3 as mandatory seed node. Citations from corpus nodes to Reno preserved as external-authority out-edges.

### CBL-008 — *Ashcroft v. ACLU*, 542 U.S. 656 (2004)
**Status:** EXCLUDED | **Pattern:** 8 | **Stage flag:** 3 | **Date:** 2026-04-11
Concerns COPA (47 U.S.C. § 231), not § 230. Zero § 230 engagement. Mandatory Stage 3 seed node.

### CBL-009 — *Zeran v. AOL* (duplicate cluster 2966756)
**Status:** REMOVED — DUPLICATE | **Date:** 2026-04-11
CourtListener cluster 2966756 is a duplicate of cluster 748185. Removed during deduplication. One node per case rule applied.

### CBL-010 — *Gonzalez v. Google LLC*, 598 U.S. 617 (2023)
**Status:** EXCLUDED | **Pattern:** 7 | **Date:** 2026-04-14
SCOTUS granted certiorari on the § 230(c)(1) algorithmic recommendation question but vacated and remanded on ATA grounds without issuing a § 230 holding. The SCOTUS opinion cites itself and *Twitter v. Taamneh* and does not engage § 230 substantively. The Ninth Circuit merits opinion (2 F.4th 871) is not separately captured in CourtListener as a distinct cluster in our retrieval. Excluded under Pattern 7 (§ 230 raised and expressly reserved by SCOTUS).

### CBL-011 — *Ricci v. Teamsters Union Local 456*, 781 F.3d 701 (2d Cir. 2015)
**Status:** INCLUDED | **Date:** 2026-04-11
Second Circuit's first published § 230(c)(1) immunity ruling. Court explicitly notes it has not previously construed the immunity provisions of the Communications Decency Act. GoDaddy held immune for hosting third-party defamatory content.

### CBL-012 — *Enigma Software Group USA v. Malwarebytes*, 946 F.3d 1040 (9th Cir. 2023)
**Status:** INCLUDED | **Date:** 2026-04-11
One of the few published circuit opinions applying § 230(c)(2)(B). Creates an anti-competitive animus exception to § 230(c)(2) immunity. High value for identifying the (c)(1)/(c)(2) community structure.

### CBL-013 — *Woodhull Freedom Foundation v. United States* (D.C. Cir. 2023)
**Status:** INCLUDED | **Date:** 2026-04-11
Applies § 230(e)(5) FOSTA exception substantively in an appellate holding. One of the only published circuit opinions engaging § 230(e)(5). Anchor node for the FOSTA sub-cluster.

### CBL-014 — *M.H. v. Omegle.com LLC* (11th Cir. 2024)
**Status:** INCLUDED | **Date:** 2026-04-11
Applies § 230(c)(1) and § 230(e)(5)(A). Resolves the contested question of scienter standard under FOSTA — actual knowledge required under the § 1591 criminal standard. High value for FOSTA sub-cluster and scienter doctrine.

### CBL-015 — *Universal Communication Systems v. Lycos*, 478 F.3d 413 (1st Cir. 2007)
**Status:** INCLUDED | **Date:** 2026-04-11
Originally identified in corpus as No. 06-1826 with incorrect cluster ID. Confirmed as First Circuit § 230(c)(1) immunity case; Lycos immune for third-party defamatory financial message board content. Case name and cluster ID corrected in validated dataset.

### CBL-016 — *Universal Communication Systems v. Lycos* (companion, cluster 8439626)
**Status:** REMOVED — DUPLICATE | **Date:** 2026-04-14
CourtListener cluster 8439626 is a near-identical entry to cluster 796967 (the published First Circuit opinion). Eyecite citation analysis confirmed both entries share 43 of 44 citation strings. Cluster 796967 retained as the canonical entry; cluster 8439626 removed.

### CBL-017 — *Thais Cardoso Almeida v. Amazon.com, Inc.*, 456 F.3d 1316 (11th Cir. 2006)
**Status:** INCLUDED | **Date:** 2026-04-14
CourtListener cluster 77393. Confirmed as the same case cited by Ardia (2010) as "Almeida v. Amazon.com." The full plaintiff name is Thais Cardoso Almeida. The Eleventh Circuit applied § 230(c)(1) substantively in its holding, affirming dismissal of right-of-publicity claims against Amazon for third-party seller content. Present in both Ardia's corpus and ours. No gap exists between Ardia's circuit-level corpus and ours for cases through September 2009.

---

*End of research_design.md — Stage 1 active. Last updated: 2026-04-14.*