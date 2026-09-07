# Data Dictionary

The final screened Hansard corpus uses the following fields.

| Field | Type | Description |
|---|---|---|
| `speech_id` | string | Identifies the parliamentary contribution. |
| `date` | date | Records the date of the parliamentary contribution. |
| `year` | integer | Records the calendar year from `date`. |
| `house` | string | Identifies the parliamentary House. |
| `venue` | string | Identifies the parliamentary venue, such as Chamber, Westminster Hall or Grand Committee. |
| `debate_id` | string | Identifies the Hansard debate or proceeding. |
| `debate_title` | string | Records the study-standardised debate title. |
| `api_debate_title` | string | Records the debate title from the Hansard API. |
| `item_id` | string/integer | Identifies the Hansard item where available. |
| `contribution_id` | string | Identifies the contribution in the Hansard source. |
| `order_in_section` | integer | Records the contribution order within the section. |
| `member_id` | string/integer | Identifies the parliamentary member where Hansard provides an ID. |
| `speaker` | string | Records the cleaned speaker label used in the analytical corpus. |
| `speaker_raw` | string | Preserves the original Hansard speaker label. |
| `party` | string | Records party metadata where Hansard provides it. |
| `speech_text` | string | Contains the full extracted parliamentary contribution. |
| `matched_terms` | string | Records the retrieval terms that match the contribution. |
| `word_count` | integer | Records the contribution word count. |
| `source_url` | string | Retains the official Hansard webpage for provenance. |
| `api_url` | string | Retains the Hansard API endpoint used for retrieval. |
| `screening_status` | categorical | Records the contribution-level inclusion status under the screening protocol. |
| `retrieved_at_utc` | datetime | Records the UTC retrieval timestamp. |

## Analytical additions

The topic-enriched dataset adds cleaned-text variables, dominant-topic assignments and LDA topic probabilities. These fields support temporal analysis, statistical testing and actor–theme network analysis.

## Provenance

The workflow preserves the original Hansard source URL, API URL, debate identifier and contribution identifier so each analytical record remains traceable to the parliamentary source.
