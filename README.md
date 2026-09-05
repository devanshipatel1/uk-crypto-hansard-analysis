# UK Cryptoasset Regulation in Hansard (2020–2025)

MSc Business Analytics project repository for the study:

**Mapping the Evolution of UK Cryptoasset Regulation: A Computational Analysis of Parliamentary Discourse Using NLP and Network Analytics, 2020–2025**

## Research questions

1. How did the thematic priorities of UK parliamentary discourse concerning cryptoasset regulation evolve between 2020 and 2025?
2. Which parliamentary and institutional actors were most strongly associated with the dominant cryptoasset regulatory themes during this period?

## Current repository status

This repository currently contains a **pilot Hansard corpus**, not the final exhaustive dissertation dataset.

- 124 parliamentary contribution rows
- 8 verified Hansard debates/proceedings
- current verified coverage: 2022–2025
- intended final study window: 2020–2025
- primary source: UK Parliament Hansard

The 2020–2021 absence in the pilot file must **not** be interpreted as evidence that Parliament had no relevant cryptoasset discussion in those years. Before final dissertation inference, the corpus should be expanded using the documented inclusion rules and checked for complete coverage of all six years.

## Repository structure

```text
uk-crypto-hansard-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── processed/
│       └── hansard_crypto_2020_2025_pilot.csv
├── notebooks/
│   └── 01_analysis_pipeline.ipynb
├── docs/
│   └── data_dictionary.md
└── outputs/
    ├── figures/
    └── tables/
```

## Dataset fields

The pilot dataset contains date, year, House, debate title, speaker, full contribution text, word count, matched crypto keywords, a relevance flag, Hansard debate ID, and the original source URL.

See `docs/data_dictionary.md` for definitions.

## Analytical pipeline

The notebook is organised around the final dissertation methodology:

1. data loading and coverage checks;
2. cleaning and deduplication;
3. exploratory corpus statistics;
4. TF–IDF analysis;
5. LDA topic modelling;
6. topic-model validation across candidate topic counts;
7. temporal topic-prevalence analysis;
8. supplementary chi-square test and Cramér's V;
9. actor–theme network construction using Hansard speaker metadata;
10. export of tables and figures.

The notebook deliberately does not treat generic sentiment analysis as a core method. Speaker identity comes from Hansard metadata rather than Named Entity Recognition. NER can be added later only for institutions mentioned within speeches.

## Reproducibility

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Open Jupyter and run:

```bash
jupyter lab
```

Then execute `notebooks/01_analysis_pipeline.ipynb` from top to bottom.

## Data source and citation

Primary data source: **UK Parliament Hansard**. Each pilot record retains its Hansard debate identifier and source URL so the source can be verified.

For the dissertation, document the exact retrieval date, search dictionary, inclusion/exclusion rules, deduplication procedure, preprocessing parameters, package versions, and random seeds used in the final run.

## Important methodological limitation

The included CSV is a targeted pilot corpus and should not be described as an exhaustive 2020–2025 dataset. Replace or extend it with the final screened corpus before reporting final longitudinal findings or inferential statistics.
