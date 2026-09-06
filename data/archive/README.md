# Dataset Archive

The exact pilot dataset used by `notebooks/01_analysis_pipeline.ipynb` is stored losslessly in `data/archive/chunks/` as ten sequential gzip+base64 text chunks.

This format is used only for repository transport. Reconstruct the CSV before running the notebook:

```bash
python scripts/reconstruct_dataset.py
```

The script writes:

`data/processed/hansard_crypto_2020_2025_pilot.csv`

and verifies both the encoded archive and reconstructed CSV using SHA-256 checksums.

## Pilot corpus status

- parliamentary contribution rows: 124
- verified Hansard debates/proceedings: 8
- verified targeted coverage in the current pilot: 2022–2025
- intended dissertation study window: 2020–2025
- primary source: UK Parliament Hansard

The absence of 2020–2021 records in this pilot is not evidence that no relevant parliamentary discussion occurred in those years. The final dissertation corpus must be expanded and screened systematically before final longitudinal inference.

## Checksums

Raw CSV SHA-256:
`99bd34136c1978bccbdeb522a21090e34bb47ef0d4550fbfaec66162f60da293`

Encoded archive SHA-256:
`17509e04bdc6edd5a439bf8fe56a26d9018e913984980885a83ea7248f4c0624`
