# Reproducibility Checklist

The project uses the following reproducibility checks:

- [x] the workflow records the Hansard retrieval timestamp;
- [x] the workflow uses a fixed retrieval dictionary;
- [x] the documentation states the inclusion and exclusion rules;
- [x] the corpus builder removes duplicate records through stable identifiers and text checks;
- [x] the dataset preserves source URLs, API URLs and debate IDs;
- [x] the analysis uses fixed random seeds;
- [x] the analysis compares candidate topic counts systematically;
- [x] the analysis reports topic coherence, diversity and seed stability;
- [x] representative high-probability speeches support topic interpretation;
- [x] the analysis exports yearly topic probabilities;
- [x] the statistical analysis reports Cramér's V alongside the p-value;
- [x] the workflow saves actor–theme and institution–theme weight tables;
- [x] the workflow saves final analytical figures and tables from code;
- [x] Git records the analysis scripts, documentation and generated outputs;
- [ ] speaker aliases receive further consolidation where one person appears under both a personal name and a ministerial title;
- [ ] the final dissertation submission records the exact Git commit used for submission.

The remaining alias-normalisation item affects actor-level presentation but does not change the document-level LDA topic model or yearly topic probabilities.
