# Research Question–Method Mapping

## RQ1

**How do the thematic priorities of UK parliamentary discourse concerning cryptoasset regulation evolve between 2020 and 2025?**

Evidence pipeline:

1. the workflow constructs a reproducible Hansard corpus;
2. TF–IDF provides exploratory vocabulary analysis;
3. LDA provides the principal topic model;
4. model diagnostics compare candidate topic counts and repeated random seeds;
5. yearly aggregation of document–topic probabilities measures thematic change;
6. a chi-square test of dominant topic by year with Cramér’s V provides supplementary inferential evidence.

## RQ2

**Which parliamentary and institutional actors are most strongly associated with the dominant cryptoasset regulatory themes during this period?**

Evidence pipeline:

1. Hansard speaker metadata identifies parliamentary actors;
2. institution matching identifies regulators and public bodies mentioned within speeches;
3. a weighted actor–theme bipartite network uses cumulative LDA topic probabilities;
4. weighted degree and topic weights indicate discursive prominence rather than causal influence.

## Methodological choices

LDA is the primary model because its document–topic probabilities are transparent and directly support longitudinal and actor-level aggregation. The analysis compares K=4 to K=8 and selects K=5 because it provides the highest NPMI coherence among the tested models while topic diversity and seed stability remain diagnostic checks.

The analysis does not use generic sentiment analysis as a core method because regulatory language often contains risk vocabulary without indicating a simple negative stance. This choice also keeps every technique directly linked to a research objective.

## Interpretation rules

The analysis treats topic prevalence as a measure of thematic prominence within the screened Hansard corpus. It treats actor and institution weights as measures of discursive association. It does not interpret these measures as evidence of causal political influence.

## Key limitations

- LDA uses a bag-of-words representation and does not fully capture word order or contextual nuance;
- keyword retrieval introduces possible search bias and terminology drift;
- annual debate volume varies across the study period;
- topic labelling requires researcher judgement;
- Hansard captures formal parliamentary discourse rather than the complete policymaking process;
- contributions cluster within debates, so the chi-square test provides supplementary rather than definitive inference;
- network centrality indicates discursive prominence rather than political influence or causality.
