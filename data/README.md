# Data

The dissertation uses UK Parliament Hansard as the primary data source.

## Pilot dataset

The local pilot corpus contains 124 parliamentary contribution rows from 8 verified Hansard debates/proceedings, with current verified coverage from 2022–2025. It is a targeted pilot and must not be described as an exhaustive 2020–2025 dataset.

The intended final dataset should be stored at:

`data/processed/hansard_crypto_2020_2025.csv`

The final corpus should include all screened, relevant parliamentary contributions between 1 January 2020 and 31 December 2025 and retain provenance fields such as Hansard debate ID and source URL.

## Required quality checks

- verify all six years (2020–2025) after systematic retrieval;
- document search terms and retrieval date;
- retain inclusion/exclusion decisions;
- deduplicate records;
- standardise speaker and institutional names;
- preserve source URLs for reproducibility.
