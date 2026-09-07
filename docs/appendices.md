# Dissertation Appendices

These appendices provide the main technical evidence that supports the methodology and findings. The complete reproducible material remains available in this public repository.

## Appendix A: Technical Documentation and Code

The project uses Python for data preparation, TF-IDF analysis, LDA topic modelling, statistical testing and actor-theme analysis.

Main files:

- `scripts/build_final_hansard_corpus.py` retrieves and screens Hansard contributions.
- `scripts/run_final_analysis.py` runs the final quantitative analysis and exports all tables and figures.
- `notebooks/01_analysis_pipeline.ipynb` provides a notebook entry point to the same final workflow.
- `requirements.txt` records the Python dependencies.

## Appendix B: Dataset and Screening

The final dataset is `data/processed/hansard_crypto_2020_2025_final.csv`.

The corpus contains 339 parliamentary contributions across 28 debates/proceedings. Eligible contributions appear in 2021, 2022, 2023, 2024 and 2025. No 2020 contribution meets the documented inclusion criteria.

The study uses individual spoken parliamentary contributions as the unit of analysis. `docs/inclusion_exclusion.md` records the search vocabulary and screening rules, while `docs/data_dictionary.md` defines the dataset fields.

## Appendix C: Topic Model and Statistical Outputs

The analysis compares LDA models from K=4 to K=8 and selects K=5 because it provides the highest NPMI coherence among the tested models while diversity and seed stability remain diagnostic checks.

The five final themes are:

1. Financial Services Regulatory Framework and Market Governance.
2. Cryptoasset Regulation, Consumer Protection and Market Supervision.
3. Economic Crime, Enforcement and Asset Recovery.
4. Digital Money, CBDCs and Financial Technology.
5. Digital Asset Property Rights and Legal Certainty.

The supplementary chi-square test produces χ²(16, N=339) = 256.553, p < .001, with Cramér's V = 0.435. Eight of 25 expected cells are below five, so the study treats this result as supporting evidence rather than the sole basis for inference.

The main statistical tables are stored in `outputs/tables/`, including model-selection diagnostics, yearly topic prevalence, chi-square results, actor-topic weights and institution-topic weights.

## Appendix D: Additional Visualisations

The main reproducible figures are stored in `outputs/figures/` and include:

- cryptoasset-related Hansard contributions by year;
- yearly LDA topic prevalence;
- actor-topic heatmap.

These figures support the descriptive, longitudinal and actor-level analysis presented in Chapter 4.

## Appendix E: Reproducibility and Public Repository

The repository preserves source URLs, Hansard debate identifiers, retrieval metadata, code, analytical outputs and methodological documentation. The analysis uses fixed random seeds and exports its results directly from code.

Public GitHub repository:

https://github.com/devanshipatel1/uk-crypto-hansard-analysis
