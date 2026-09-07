# Final quantitative analysis summary

The analytical corpus contains 339 contributions across 28 debates and proceedings.
Eligible contributions appear in 2021, 2022, 2023, 2024 and 2025.
No eligible 2020 contribution meets the documented screening protocol.

The analysis selects K=5 as the LDA topic count because it provides the highest NPMI coherence among K=4–8. Topic diversity and seed stability remain diagnostic checks.

## Top words by topic
- Topic 0: financial, services, regulators, financial services, sector, regulatory, support, important, treasury, fraud, cash, regulation
- Topic 1: crypto, cryptoassets, regulation, financial, fca, people, cryptoasset, firms, sector, regulatory, cryptocurrency, services
- Topic 2: act, crime, cryptoassets, powers, economic, regulations, economic crime, criminals, fraud, transparency, enforcement, nfts
- Topic 3: digital, cbdc, bank, crypto, people, need, technology, way, money, central, important, data
- Topic 4: law, property, digital_assets, legal, things, rights, law_commission, common, common law, personal, personal property, courts

## Chi-square test
χ²(16, N=339) = 256.553, p = 2.33901e-45, Cramér's V = 0.435.
The expected-frequency diagnostic shows 8 of 25 cells below 5, and the minimum expected count is 0.599.
The study treats this test as supplementary because contributions cluster within debates and therefore are not fully independent observations.

## Reproducibility
The script `scripts/run_final_analysis.py` generates all numeric tables, topic-probability data and figures from the final screened Hansard corpus.
