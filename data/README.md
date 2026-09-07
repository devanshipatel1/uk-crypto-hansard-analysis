# Data

The dissertation uses UK Parliament Hansard as the primary data source.

## Final screened corpus

The final analytical corpus contains 339 parliamentary contributions from 28 verified Hansard debates and proceedings. Eligible contributions appear in 2021, 2022, 2023, 2024 and 2025. No 2020 contribution meets the documented inclusion rules.

The final screened dataset is stored at:

`data/processed/hansard_crypto_2020_2025_final.csv`

The topic-enriched analytical dataset is stored at:

`data/processed/hansard_crypto_2020_2025_topics.csv`

The final corpus retains provenance fields such as Hansard debate identifiers, contribution identifiers, official source URLs and Hansard API URLs.

## Data quality controls

The workflow:

- applies the documented 2020–2025 study window;
- uses the predefined cryptoasset retrieval vocabulary;
- records contribution-level inclusion decisions;
- removes duplicates through stable identifiers and text checks;
- preserves speaker and member metadata where Hansard provides it;
- retains source URLs and debate IDs for reproducibility;
- records retrieval timestamps;
- reports annual corpus coverage without inserting synthetic observations for missing years.

## Interpretation of 2020

The final screened corpus contains no eligible 2020 contribution. This result means that no contribution passes the study's inclusion threshold under the documented search and screening protocol. It does not claim that Parliament makes no reference to blockchain, digital finance or related technology in 2020.
