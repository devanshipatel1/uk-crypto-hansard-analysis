# UK Cryptoasset Regulation in Hansard (2020–2025)

This repository supports the MSc Business Analytics study:

**Mapping the Evolution of UK Cryptoasset Regulation: A Computational Analysis of Parliamentary Discourse Using NLP and Network Analytics, 2020–2025**

## Research questions

1. How do the thematic priorities of UK parliamentary discourse concerning cryptoasset regulation evolve between 2020 and 2025?
2. Which parliamentary and institutional actors are most strongly associated with the dominant cryptoasset regulatory themes during this period?

## Current repository status

This repository contains the final screened Hansard corpus and the reproducible quantitative analysis.

- 339 parliamentary contributions
- 28 debates/proceedings
- eligible contributions in 2021, 2022, 2023, 2024 and 2025
- no 2020 contribution meets the documented inclusion criteria
- primary source: UK Parliament Hansard

The absence of eligible 2020 observations means that no contribution meets the predefined retrieval and screening rules. It does not mean that Parliament never discusses blockchain, digital finance or related technologies in 2020.

## Repository structure

```text
uk-crypto-hansard-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── README.md
│   ├── raw/
│   └── processed/
│       ├── hansard_crypto_2020_2025_final.csv
│       └── hansard_crypto_2020_2025_topics.csv
├── notebooks/
│   └── 01_analysis_pipeline.ipynb
├── scripts/
│   ├── build_final_hansard_corpus.py
│   └── run_final_analysis.py
├── docs/
│   ├── data_dictionary.md
│   ├── inclusion_exclusion.md
│   ├── methodology_mapping.md
│   ├── final_corpus_retrieval_log.md
│   └── reproducibility_checklist.md
└── outputs/
    ├── figures/
    └── tables/
```

## Dataset

The final screened dataset is stored at:

`data/processed/hansard_crypto_2020_2025_final.csv`

Each contribution retains provenance and analytical metadata, including the speech identifier, date, year, House, venue, debate identifier, debate title, member identifier where available, speaker label, party where available, full speech text, matched retrieval terms, word count, source URL, API URL, screening status and retrieval timestamp.

See `docs/data_dictionary.md` for definitions.

## Analytical pipeline

The analysis uses the following workflow:

1. the corpus builder retrieves and screens Hansard contributions;
2. quality checks examine coverage, duplicates and metadata consistency;
3. TF–IDF provides exploratory vocabulary analysis;
4. LDA provides the principal topic model;
5. candidate topic counts from K=4 to K=8 are compared using NPMI coherence, topic diversity, seed stability and perplexity;
6. the analysis selects K=5 because it provides the highest NPMI coherence among the tested models;
7. yearly mean topic probabilities measure thematic change over time;
8. a chi-square test with Cramér's V provides supplementary inferential evidence;
9. actor–theme and institution–theme weights measure discursive prominence;
10. the scripts export all final tables and figures reproducibly.

The analysis does not use generic sentiment analysis as a core method because regulatory language often contains risk vocabulary without expressing a simple negative stance. Hansard speaker metadata identifies parliamentary actors, while institutional references support the institution–theme analysis.

## Reproducibility

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the final analysis with:

```bash
python scripts/run_final_analysis.py
```

The notebook `notebooks/01_analysis_pipeline.ipynb` provides the notebook entry point for the same reproducible workflow.

## Final analytical results

The final corpus contains 339 contributions across 28 debates/proceedings. The LDA analysis selects five topics. The chi-square test shows an association between year and dominant topic: χ²(16, N=339) = 256.553, p < .001, with Cramér's V = 0.435.

The analysis treats the chi-square test as supplementary because some expected cells contain fewer than five observations and contributions cluster within debates.

## Data source and provenance

UK Parliament Hansard provides the primary source. The dataset retains debate identifiers, official source URLs and API URLs so each contribution remains traceable to the parliamentary record.

## Methodological limitations

The analysis recognises keyword-retrieval bias, terminology drift, unequal debate volume across years, LDA's bag-of-words assumptions, researcher judgement in topic labelling and clustering of contributions within debates. Network weights indicate discursive prominence within the corpus and do not measure causal political influence.
