from pathlib import Path
import base64
import gzip
import hashlib

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = ROOT / "data" / "archive" / "chunks"
OUTPUT = ROOT / "data" / "processed" / "hansard_crypto_2020_2025_pilot.csv"

EXPECTED_CHUNKS = 10
EXPECTED_RAW_SHA256 = "99bd34136c1978bccbdeb522a21090e34bb47ef0d4550fbfaec66162f60da293"
EXPECTED_ARCHIVE_SHA256 = "17509e04bdc6edd5a439bf8fe56a26d9018e913984980885a83ea7248f4c0624"

parts = sorted(ARCHIVE_DIR.glob("chunk_*.txt"))
if len(parts) != EXPECTED_CHUNKS:
    raise RuntimeError(
        f"Expected {EXPECTED_CHUNKS} archive chunks, found {len(parts)} in {ARCHIVE_DIR}"
    )

payload = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
archive_sha256 = hashlib.sha256(payload.encode("utf-8")).hexdigest()
if archive_sha256 != EXPECTED_ARCHIVE_SHA256:
    raise RuntimeError(
        "Encoded archive checksum mismatch: "
        f"expected {EXPECTED_ARCHIVE_SHA256}, got {archive_sha256}"
    )

raw = gzip.decompress(base64.b64decode(payload))
raw_sha256 = hashlib.sha256(raw).hexdigest()
if raw_sha256 != EXPECTED_RAW_SHA256:
    raise RuntimeError(
        f"Dataset checksum mismatch: expected {EXPECTED_RAW_SHA256}, got {raw_sha256}"
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_bytes(raw)

print(f"Wrote {OUTPUT} ({len(raw):,} bytes)")
print("dataset_sha256:", raw_sha256)
print("archive_sha256:", archive_sha256)
