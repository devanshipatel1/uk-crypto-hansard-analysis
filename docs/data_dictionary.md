# Data dictionary

| Field | Type | Description |
|---|---|---|
| `date` | date | Date of the parliamentary contribution. |
| `year` | integer | Calendar year derived from `date`. |
| `house` | string | Parliamentary chamber/venue label captured in the pilot extraction. |
| `debate_title` | string | Hansard debate or proceeding title. |
| `speaker` | string | Speaker label from Hansard. |
| `speech` | string | Full text of the extracted parliamentary contribution. |
| `word_count` | integer | Number of whitespace-separated words in `speech`. |
| `matched_keywords` | string | Crypto-related retrieval terms found in the contribution. |
| `crypto_relevant` | categorical | Pilot keyword-based relevance flag (`Yes`/`No`). |
| `debate_id` | string | Hansard debate identifier. |
| `source_url` | string | Original Hansard text endpoint retained for provenance. |

## Final-corpus additions recommended

For the exhaustive dataset, add where available:

- stable `speech_id` / contribution identifier;
- parliamentary member ID;
- party;
- chamber/venue standardised to Commons, Westminster Hall, Commons Committee, Lords, or Lords Grand Committee;
- retrieval timestamp;
- inclusion/exclusion decision and reason;
- source search term(s);
- cleaned text field;
- final topic probabilities after modelling.
