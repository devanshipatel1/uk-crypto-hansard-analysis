# Final 2020–2025 Hansard Corpus Retrieval Log

## Purpose

This document records the final corpus construction for the study:

**Mapping the Evolution of UK Cryptoasset Regulation: A Computational Analysis of Parliamentary Discourse Using NLP and Network Analytics, 2020–2025**

## Study window

The study covers 1 January 2020 to 31 December 2025.

## Unit of analysis

The unit of analysis is the individual spoken parliamentary contribution.

## Retrieval vocabulary

Core terms include:

- cryptoasset / crypto asset / crypto assets
- cryptocurrency / cryptocurrencies / crypto currency
- Bitcoin
- Ethereum
- stablecoin / stablecoins

Contextual terms include:

- blockchain
- distributed ledger / distributed ledger technology / DLT
- digital asset / digital assets
- crypto exchange
- crypto token / crypto-token

The workflow retains contextual results only when they substantively concern cryptoassets, token markets, digital-asset financial activity, or regulation and governance of those activities.

## Inclusion rules

The corpus includes spoken contributions from the House of Commons, Westminster Hall, House of Lords and substantive committee proceedings when the contribution concerns cryptoasset regulation, governance, consumer protection, market integrity, financial crime, stablecoins, financial promotions, custody or trading infrastructure, reporting obligations, or the legal status of crypto and digital assets.

## Exclusion rules

The corpus excludes:

- written-only statements;
- purely procedural text;
- generic uses of blockchain or DLT unrelated to cryptoasset or digital-asset financial policy;
- CBDC-only discussion unless the contribution explicitly compares CBDCs with private cryptoassets or stablecoins;
- duplicate contributions or duplicate page representations of the same debate;
- generic token or digital-asset references without cryptoasset relevance.

## Final corpus status

The final screened corpus contains **339 contributions across 28 debates and proceedings**. Eligible contributions appear in 2021, 2022, 2023, 2024 and 2025. No contribution from 2020 meets the final inclusion threshold.

### 2020

The search covers cryptoasset, cryptocurrency, Bitcoin, stablecoin, digital asset, blockchain and DLT terminology. The screening protocol excludes broader DLT and fintech references when they do not substantively concern cryptoasset regulation. The final corpus therefore records a screened zero for 2020.

This screened zero means that no contribution passes the inclusion threshold. It does not claim that Parliament makes no reference to blockchain, fintech or related digital technologies in 2020.

### 2021

The final corpus includes qualifying contributions from:

- Financial Services Bill, House of Lords, 10 March 2021;
- Commons financial-services debate, 2 December 2021;
- Commons financial-services debate, 9 December 2021.

The final 2021 corpus contains 7 contributions across 3 debates and proceedings.

### 2022

The final corpus includes qualifying contributions from nine debates and proceedings, including:

- Crypto Currencies, 28 February 2022;
- Cryptocurrencies, 2 March 2022;
- Crypto Asset Technology, 21 July 2022;
- Cryptoassets: Regulation, 7 September 2022;
- Financial Services and Markets Bill, 7 September 2022;
- Financial Services and Markets Bill (Fourth sitting), 25 October 2022;
- Financial Services and Markets Bill (Ninth sitting), 3 November 2022;
- Cryptoasset Promotions in Sport, 8 November 2022;
- Cryptocurrencies, House of Lords, 20 December 2022.

The final 2022 corpus contains 137 contributions.

### 2023

The final corpus includes qualifying contributions from seven debates and proceedings, including:

- Financial Services and Markets Bill, 10 January 2023;
- Cryptocurrency Regulation, 25 January 2023;
- Central Bank Digital Currencies, 2 February 2023, where contribution-level screening retains only relevant comparative material;
- Commons and Lords consideration of the cryptoasset financial-promotion order, 2 May 2023;
- Cryptocurrency Regulation, 13 June 2023;
- Financial Services and Markets Bill, 26 June 2023.

The final 2023 corpus contains 53 contributions.

### 2024

The final corpus includes qualifying contributions from:

- Proceeds of Crime Act 2002 cryptoasset search and recovery regulations, 16 April 2024;
- Property (Digital Assets etc) Bill, 6 November 2024;
- cryptoasset proceeds-of-crime consequential legislation, 13 November 2024.

The final 2024 corpus contains 33 contributions.

### 2025

The final corpus includes qualifying contributions from six debates and proceedings, including:

- Finance Bill (Fourth sitting), 30 January 2025;
- Property (Digital Assets etc) Bill stages during 2025;
- Cryptocurrencies: US Regulation, 12 November 2025.

The final 2025 corpus contains 109 contributions.

## Contribution-level fields

Each retained contribution records:

`speech_id`, `date`, `year`, `house`, `venue`, `debate_id`, `debate_title`, `api_debate_title`, `item_id`, `contribution_id`, `order_in_section`, `member_id`, `speaker`, `speaker_raw`, `party`, `speech_text`, `matched_terms`, `word_count`, `source_url`, `api_url`, `screening_status`, `retrieved_at_utc`.

## Processing and validation

The corpus builder retrieves individual Hansard contributions, applies the inclusion rules, removes duplicates, preserves source metadata and exports the final screened dataset. The analysis script then applies TF–IDF, LDA topic modelling, temporal topic analysis, chi-square testing, actor–theme weighting and institution–theme weighting.

The analytical workflow uses the final screened corpus in `data/processed/hansard_crypto_2020_2025_final.csv` and generates reproducible tables and figures under `outputs/`.

## Analytical rule

The study reports 2020 as a screened zero and bases temporal topic estimates on years that contain eligible contributions. The analysis interprets all findings as patterns within the screened Hansard corpus rather than as complete measures of every UK cryptoasset policymaking activity.
