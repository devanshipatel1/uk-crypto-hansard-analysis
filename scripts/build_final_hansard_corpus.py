#!/usr/bin/env python3
"""Build a reproducible speech-level Hansard cryptoasset corpus from the debate registry.

The script downloads official Hansard debate pages listed in
`data/raw/hansard_debate_registry_2020_2025.csv`, extracts individual spoken
contributions, applies the documented relevance rules, and writes both an
unfiltered extraction and the screened analytical corpus.

It is intentionally conservative: missing years are not back-filled, failed
pages are logged, and broader Bill debates only retain contributions that
contain cryptoasset-related terminology.
"""
from __future__ import annotations

import hashlib
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/raw/hansard_debate_registry_2020_2025.csv"
RAW_OUT = ROOT / "data/processed/hansard_contributions_unfiltered_2020_2025.csv"
FINAL_OUT = ROOT / "data/processed/hansard_crypto_2020_2025_final.csv"
BUILD_LOG = ROOT / "outputs/tables/corpus_build_log.csv"
QA_OUT = ROOT / "outputs/tables/final_corpus_qa_summary.csv"

USER_AGENT = (
    "Mozilla/5.0 (compatible; MScBusinessAnalyticsResearch/1.0; "
    "+https://github.com/devanshipatel1/uk-crypto-hansard-analysis)"
)

CORE_PATTERNS = {
    "cryptoasset": r"\bcrypto[ -]?assets?\b",
    "cryptocurrency": r"\bcrypto[ -]?currenc(?:y|ies)\b",
    "crypto": r"\bcrypto\b",
    "bitcoin": r"\bbitcoin\b",
    "ethereum": r"\bethereum\b",
    "stablecoin": r"\bstablecoins?\b",
    "blockchain": r"\bblockchains?\b",
    "distributed_ledger": r"\bdistributed ledger(?: technology)?\b|\bDLT\b",
    "digital_asset": r"\bdigital assets?\b",
    "crypto_exchange": r"\bcrypto(?:asset)? exchanges?\b|\bcrypto exchanges?\b",
    "tokenised_asset": r"\btokeni[sz]ed assets?\b",
    "nft": r"\bNFTs?\b|\bnon-fungible tokens?\b",
}

REGULATORY_PATTERNS = {
    "regulation": r"\bregulat(?:e|ed|es|ing|ion|ions|ory)\b",
    "fca": r"\bFCA\b|\bFinancial Conduct Authority\b",
    "treasury": r"\bHM Treasury\b|\bTreasury\b",
    "bank_of_england": r"\bBank of England\b",
    "financial_promotion": r"\bfinancial promotions?\b",
    "aml": r"\banti-money laundering\b|\bAML\b|\bmoney laundering\b",
    "financial_stability": r"\bfinancial stability\b",
    "consumer_protection": r"\bconsumer protection\b|\bconsumers?\b",
    "fraud": r"\bfraud\b|\bscams?\b",
    "market_abuse": r"\bmarket abuse\b",
    "custody": r"\bcustod(?:y|ian|ians)\b",
    "authorisation": r"\bauthori[sz](?:e|ed|ation)\b",
    "disclosure": r"\bdisclosures?\b",
    "property_law": r"\bproperty law\b|\bpersonal property\b|\bLaw Commission\b",
}

DEDICATED_TITLE_TERMS = (
    "crypto",
    "cryptocurrency",
    "cryptoasset",
    "crypto asset",
    "property (digital assets",
    "property digital assets",
)

PARTY_CODES = [
    "Con", "Lab", "LD", "SNP", "CB", "DUP", "PC", "Green", "UUP",
    "Ind", "Lab/Co-op", "Alliance", "Reform UK", "SDLP"
]

SHARE_META_RE = re.compile(
    r"^(Share this specific contribution|Share a link to this specific contribution:?|"
    r"Share contribution \d+ on (Twitter|Facebook)|Share contribution \d+ via Email|"
    r"Copy link to contribution \d+ to clipboard Copy link)$",
    re.I,
)
CONTRIB_NO_RE = re.compile(r"Copy link to contribution (\d+)", re.I)
TIME_RE = re.compile(r"^\d{1,2}\.\d{2}(am|pm)$", re.I)
COLUMN_RE = re.compile(r"^Column \d+", re.I)


@dataclass
class Contribution:
    contribution_no: str
    speaker_raw: str
    speech_text: str


def clean_line(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def is_noise_line(line: str) -> bool:
    if not line:
        return True
    if SHARE_META_RE.match(line):
        return True
    if TIME_RE.match(line) or COLUMN_RE.match(line):
        return True
    if line in {"Question", "Asked by", "Moved by", "Motion", "Debate", "Division"}:
        return True
    if line.startswith("© UK Parliament"):
        return True
    if line in {"Cookie policy", "Cookie settings", "Privacy notice", "Accessibility statement"}:
        return True
    return False


def speaker_candidate(lines: list[str], marker_idx: int) -> tuple[int, str]:
    """Return the likely speaker line immediately before a share marker."""
    for j in range(marker_idx - 1, max(-1, marker_idx - 9), -1):
        line = lines[j]
        if is_noise_line(line):
            continue
        if line.startswith("Volume ") or line.startswith("debated on "):
            continue
        if re.fullmatch(r"\d{1,2}", line):
            continue
        return j, line
    return marker_idx - 1, "Unknown"


def parse_contributions(html: str) -> list[Contribution]:
    soup = BeautifulSoup(html, "lxml")
    lines = [clean_line(x) for x in soup.get_text("\n").splitlines()]
    lines = [x for x in lines if x]

    markers = [i for i, line in enumerate(lines) if line.lower() == "share this specific contribution"]
    if not markers:
        return []

    speaker_info = [speaker_candidate(lines, idx) for idx in markers]
    contributions: list[Contribution] = []

    for n, marker_idx in enumerate(markers):
        speaker_idx, speaker = speaker_info[n]
        next_speaker_idx = speaker_info[n + 1][0] if n + 1 < len(markers) else len(lines)

        segment = lines[marker_idx + 1 : next_speaker_idx]
        contribution_no = ""
        copy_pos = None
        for k, line in enumerate(segment):
            m = CONTRIB_NO_RE.search(line)
            if m:
                contribution_no = m.group(1)
                copy_pos = k
                break

        if copy_pos is not None:
            body_lines = segment[copy_pos + 1 :]
        else:
            body_lines = segment

        body = []
        for line in body_lines:
            if is_noise_line(line):
                continue
            if line.startswith("Back to top") or line.startswith("Previous debate") or line.startswith("Next debate"):
                continue
            body.append(line)

        text = clean_line(" ".join(body))
        if text:
            contributions.append(Contribution(contribution_no, clean_line(speaker), text))

    return contributions


def debate_id_from_url(url: str) -> str:
    parts = [p for p in urlparse(url).path.split("/") if p]
    try:
        i = [p.lower() for p in parts].index("debates")
        return parts[i + 1]
    except Exception:
        return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def matched_terms(text: str) -> list[str]:
    hits = []
    for name, pattern in {**CORE_PATTERNS, **REGULATORY_PATTERNS}.items():
        if re.search(pattern, text, flags=re.I):
            hits.append(name)
    return sorted(set(hits))


def has_core_term(text: str) -> bool:
    return any(re.search(p, text, flags=re.I) for p in CORE_PATTERNS.values())


def is_procedural(text: str) -> bool:
    t = text.lower().strip()
    procedural_starts = (
        "question put and agreed", "amendment agreed", "clause ordered", "bill accordingly",
        "i beg to move", "motion made", "the committee divided", "order."
    )
    return len(text.split()) < 12 and t.startswith(procedural_starts)


def is_dedicated_title(title: str) -> bool:
    t = title.lower()
    return any(term in t for term in DEDICATED_TITLE_TERMS)


def retain_contribution(text: str, debate_title: str, status: str) -> bool:
    wc = len(text.split())
    if wc < 8 or is_procedural(text):
        return False

    if status == "screen_contextual":
        return has_core_term(text)

    if is_dedicated_title(debate_title):
        return True

    # General financial-services / finance / committee proceedings are retained
    # only where the contribution itself contains a cryptoasset-related term.
    return has_core_term(text)


def parse_party(speaker_raw: str) -> str:
    for code in PARTY_CODES:
        if re.search(rf"\({re.escape(code)}\)", speaker_raw, flags=re.I):
            return code
    return ""


def normalise_speaker(speaker_raw: str) -> str:
    # Preserve ministerial titles but remove terminal constituency/party brackets.
    s = speaker_raw
    s = re.sub(r"\s*\((?:Con|Lab|LD|SNP|CB|DUP|PC|Green|UUP|Ind|Lab/Co-op|Alliance|Reform UK|SDLP)\)\s*(?:\[[^\]]+\])?$", "", s, flags=re.I)
    s = re.sub(r"\s*\[[^\]]+\]\s*$", "", s)
    return clean_line(s)


def main() -> int:
    if not REGISTRY.exists():
        print(f"Registry not found: {REGISTRY}", file=sys.stderr)
        return 2

    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)

    registry = pd.read_csv(REGISTRY, dtype=str).fillna("")
    eligible = registry[registry["screening_status"].str.startswith(("include", "screen_contextual"))].copy()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-GB,en;q=0.9"})

    extraction_rows: list[dict] = []
    log_rows: list[dict] = []
    retrieved_at = datetime.now(timezone.utc).isoformat()

    for _, debate in eligible.iterrows():
        url = debate["source_url"]
        debate_id = debate_id_from_url(url)
        started = time.time()
        try:
            resp = session.get(url, timeout=45)
            status_code = resp.status_code
            resp.raise_for_status()
            items = parse_contributions(resp.text)
            parse_status = "ok" if items else "no_contributions_parsed"

            for item in items:
                text = item.speech_text
                row = {
                    "speech_id": f"{debate['date']}_{debate_id}_{item.contribution_no or hashlib.sha1(text.encode()).hexdigest()[:8]}",
                    "date": debate["date"],
                    "year": int(debate["year"]),
                    "house": debate["house"],
                    "venue": debate["venue"],
                    "debate_id": debate_id,
                    "debate_title": debate["debate_title"],
                    "contribution_no": item.contribution_no,
                    "speaker": normalise_speaker(item.speaker_raw),
                    "speaker_raw": item.speaker_raw,
                    "party": parse_party(item.speaker_raw),
                    "speech_text": text,
                    "matched_terms": ";".join(matched_terms(text)),
                    "word_count": len(text.split()),
                    "source_url": url,
                    "screening_status": debate["screening_status"],
                    "retain_for_analysis": retain_contribution(text, debate["debate_title"], debate["screening_status"]),
                    "retrieved_at_utc": retrieved_at,
                }
                extraction_rows.append(row)

            log_rows.append({
                "date": debate["date"],
                "debate_title": debate["debate_title"],
                "source_url": url,
                "http_status": status_code,
                "parse_status": parse_status,
                "contributions_parsed": len(items),
                "seconds": round(time.time() - started, 2),
            })
        except Exception as exc:
            log_rows.append({
                "date": debate["date"],
                "debate_title": debate["debate_title"],
                "source_url": url,
                "http_status": getattr(locals().get("resp", None), "status_code", ""),
                "parse_status": f"ERROR: {type(exc).__name__}: {exc}",
                "contributions_parsed": 0,
                "seconds": round(time.time() - started, 2),
            })
        time.sleep(0.35)

    raw = pd.DataFrame(extraction_rows)
    if raw.empty:
        pd.DataFrame(log_rows).to_csv(BUILD_LOG, index=False)
        print("No contributions were extracted; see build log.", file=sys.stderr)
        return 1

    # Exact duplicate control at speech level.
    raw["dedupe_key"] = (
        raw["date"].astype(str) + "|" + raw["speaker"].astype(str) + "|" + raw["speech_text"].astype(str)
    ).map(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest())
    raw = raw.drop_duplicates("dedupe_key").drop(columns="dedupe_key")
    raw = raw.sort_values(["date", "debate_id", "contribution_no"], kind="stable")
    raw.to_csv(RAW_OUT, index=False)

    final = raw[raw["retain_for_analysis"]].copy()
    final = final.drop(columns="retain_for_analysis")
    final.to_csv(FINAL_OUT, index=False)

    pd.DataFrame(log_rows).to_csv(BUILD_LOG, index=False)

    by_year = final.groupby("year", dropna=False).agg(
        contributions=("speech_id", "count"),
        debates=("debate_id", "nunique"),
        speakers=("speaker", "nunique"),
        words=("word_count", "sum"),
    ).reset_index()

    all_years = pd.DataFrame({"year": list(range(2020, 2026))})
    by_year = all_years.merge(by_year, on="year", how="left").fillna(0)
    for c in ["contributions", "debates", "speakers", "words"]:
        by_year[c] = by_year[c].astype(int)
    by_year.to_csv(QA_OUT, index=False)

    print(f"Extracted {len(raw):,} unique contributions before screening")
    print(f"Retained {len(final):,} contributions in final analytical corpus")
    print(by_year.to_string(index=False))
    print(f"Final corpus: {FINAL_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
