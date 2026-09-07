# Final 2020–2025 Hansard Corpus Retrieval Log

## Purpose

This document records the systematic expansion of the pilot corpus into the final dissertation corpus for the study:

**Mapping the Evolution of UK Cryptoasset Regulation: A Computational Analysis of Parliamentary Discourse Using NLP and Network Analytics, 2020–2025**

## Study window

1 January 2020 to 31 December 2025.

## Unit of analysis

Individual spoken parliamentary contribution.

## Retrieval vocabulary

Core terms:

- cryptoasset / crypto asset / crypto assets
- cryptocurrency / cryptocurrencies / crypto currency
- Bitcoin
- Ethereum
- stablecoin / stablecoins

Contextual terms:

- blockchain
- distributed ledger / distributed ledger technology / DLT
- digital asset / digital assets
- crypto exchange
- crypto token / crypto-token

Contextual results are retained only when they substantively concern cryptoassets, token markets, digital-asset financial activity, or regulation/governance of those activities.

## Inclusion rules

Include spoken contributions from the House of Commons, Westminster Hall, House of Lords, and substantive committee proceedings where the contribution concerns cryptoasset regulation, governance, consumer protection, market integrity, financial crime, stablecoins, financial promotions, custody/trading infrastructure, reporting obligations, or the legal status of crypto/digital assets.

## Exclusion rules

Exclude:

- written-only statements;
- purely procedural text;
- generic uses of blockchain/DLT unrelated to cryptoasset or digital-asset financial policy;
- CBDC-only discussion unless it explicitly compares CBDCs with private cryptoassets or stablecoins;
- duplicate contributions or duplicate page representations of the same debate;
- generic token/digital-asset references without cryptoasset relevance.

## Current systematic search status

### 2020

A targeted search of cryptoasset, cryptocurrency, Bitcoin, stablecoin, digital asset, blockchain and DLT terminology has so far produced no verified spoken debate that meets the core cryptoasset-regulation inclusion threshold. Several DLT/fintech references were screened and excluded because they did not substantively concern cryptoasset regulation. This is recorded as a screened zero, not as proof that no relevant contribution exists until the final search audit is complete.

### 2021

New qualifying material identified beyond the pilot corpus includes:

- Financial Services Bill, House of Lords, 10 March 2021;
- Financial Services Bill, House of Lords, 19 April 2021;
- Commons financial-services debate, 2 December 2021;
- Commons financial-services debate, 9 December 2021.

These results materially improve early-period coverage and must be converted to contribution-level records before final modelling.

### 2022

The pilot corpus already includes four 2022 debates. The systematic expansion has identified additional qualifying proceedings, including:

- Financial Services and Markets Bill, 7 September 2022;
- Financial Services and Markets Bill (Fourth sitting), 25 October 2022;
- Financial Services and Markets Bill (Ninth sitting), 3 November 2022;
- Cryptocurrencies, House of Lords, 20 December 2022.

### 2023

The expansion has identified additional qualifying proceedings beyond the pilot, including:

- Financial Services and Markets Bill, 10 January 2023;
- Cryptocurrency Regulation, 25 January 2023;
- Commons and Lords consideration of the cryptoasset financial-promotion order, 2 May 2023;
- Financial Services and Markets Bill, 26 June 2023.

A CBDC debate dated 2 February 2023 is marked for contribution-level screening rather than automatic inclusion.

### 2024

Additional qualifying material includes:

- delegated legislation on cryptoasset search/recovery powers, 16 April 2024;
- Property (Digital Assets etc) Bill, 6 November 2024;
- cryptoasset proceeds-of-crime consequential legislation, 13 November 2024.

The 18 November DLT government-debt written statement is excluded from the spoken corpus.

### 2025

Additional qualifying material includes:

- Finance Bill (Fourth sitting), 30 January 2025, including the Crypto-Asset Reporting Framework;
- Property (Digital Assets etc) Bill stages on 3 February, 30 April, 16 July and 19 November 2025;
- Cryptocurrencies: US Regulation, 12 November 2025.

## Next processing stage

For every included debate, the next step is to extract individual contributions and retain:

`speech_id`, `date`, `year`, `house`, `venue`, `debate_id`, `debate_title`, `speaker_id`, `speaker`, `party`, `role`, `speech_text`, `matched_terms`, `word_count`, `source_url`, `screening_status`.

The final corpus must then be deduplicated, screened, validated against source pages, and rerun through the existing TF-IDF → LDA → temporal analysis → actor–theme network pipeline.

## Important analytical rule

No Chapter 4 result should be described as the final 2020–2025 finding until contribution-level extraction and screening are complete for all included debates and the statistical analysis has been rerun on that final corpus.
