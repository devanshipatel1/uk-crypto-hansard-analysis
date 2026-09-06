# Research Question–Method Mapping

## RQ1

**How did the thematic priorities of UK parliamentary discourse concerning cryptoasset regulation evolve between 2020 and 2025?**

Evidence pipeline:

1. reproducible Hansard corpus construction;
2. TF–IDF as exploratory vocabulary analysis;
3. LDA as the principal topic model;
4. topic-model validation across candidate topic counts and repeated random seeds;
5. yearly aggregation of document–topic probabilities;
6. chi-square test of dominant topic by year with Cramér’s V as a supplementary inferential test.

## RQ2

**Which parliamentary and institutional actors were most strongly associated with the dominant cryptoasset regulatory themes during this period?**

Evidence pipeline:

1. Hansard speaker metadata for parliamentary actors;
2. optional Named Entity Recognition only for institutions mentioned within speeches;
3. weighted actor–theme bipartite network using cumulative LDA topic probabilities;
4. weighted degree/centrality interpreted as discursive prominence, not causal influence.

## Methodological choices

LDA is the primary model because its document–topic probabilities are transparent and directly support longitudinal and actor-level aggregation. Transformer/BERTopic approaches may be used as a robustness check in an appendix, but are not treated as a parallel central model.

Generic sentiment analysis is not a core method because regulatory language can contain risk vocabulary without indicating a negative stance. Omitting sentiment also prevents methodological overload and keeps each technique directly linked to a research objective.

## Key limitations

- bag-of-words assumptions in LDA;
- keyword retrieval bias and terminology drift;
- temporal imbalance in debate volume;
- researcher judgement in topic labelling;
- Hansard captures formal parliamentary discourse, not the complete policymaking process;
- network centrality indicates discursive prominence, not political influence or causality.
