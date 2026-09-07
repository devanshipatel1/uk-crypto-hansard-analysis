#!/usr/bin/env python3
"""Build a reproducible speech-level UK Hansard cryptoasset corpus (2020–2025).

Data are retrieved from the official Hansard REST API rather than scraping the
Cloudflare-protected website. The debate registry controls inclusion/exclusion;
individual contributions are then screened conservatively for cryptoasset
relevance where the debate itself is broader than cryptoassets.
"""
from __future__ import annotations

import hashlib
import html
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/raw/hansard_debate_registry_2020_2025.csv"
RAW_OUT = ROOT / "data/processed/hansard_contributions_unfiltered_2020_2025.csv"
FINAL_OUT = ROOT / "data/processed/hansard_crypto_2020_2025_final.csv"
BUILD_LOG = ROOT / "outputs/tables/corpus_build_log.csv"
QA_OUT = ROOT / "outputs/tables/final_corpus_qa_summary.csv"
API_BASE = "https://hansard-api.parliament.uk"

USER_AGENT = (
    "MScBusinessAnalyticsResearch/1.0 "
    "(+https://github.com/devanshipatel1/uk-crypto-hansard-analysis)"
)

UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
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

NON_SPEECH_TAGS = {
    "hs_DebateType", "hs_ColumnNumber", "hs_TimeCode", "hs_ParaText", "hs_Clause"
}
NON_SPEECH_VALUES = {
    "question", "asked by", "moved by", "motion", "debate", "division"
}


def clean_text(value: object) -> str:
    if value is None:
        return ""
    raw = html.unescape(str(value))
    text = BeautifulSoup(raw, "lxml").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def debate_id_from_url(url: str) -> str:
    """Return the first UUID present in a Hansard URL, or blank if none exists."""
    match = UUID_RE.search(unquote(url))
    return match.group(0) if match else ""


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
        "question put and agreed", "amendment agreed", "clause ordered",
        "bill accordingly", "motion made", "the committee divided", "order."
    )
    return len(text.split()) < 12 and t.startswith(procedural_starts)


def is_dedicated_title(title: str) -> bool:
    t = title.lower()
    return any(term in t for term in DEDICATED_TITLE_TERMS)


def retain_contribution(text: str, debate_title: str, status: str) -> bool:
    if len(text.split()) < 8 or is_procedural(text):
        return False
    if status == "screen_contextual":
        return has_core_term(text)
    if is_dedicated_title(debate_title):
        return True
    return has_core_term(text)


def parse_party(speaker_raw: str) -> str:
    for code in PARTY_CODES:
        if re.search(rf"\({re.escape(code)}\)", speaker_raw, flags=re.I):
            return code
    return ""


def normalise_speaker(speaker_raw: str) -> str:
    s = speaker_raw
    s = re.sub(
        r"\s*\((?:Con|Lab|LD|SNP|CB|DUP|PC|Green|UUP|Ind|Lab/Co-op|Alliance|Reform UK|SDLP)\)\s*$",
        "", s, flags=re.I
    )
    return re.sub(r"\s+", " ", s).strip()


def iter_contribution_items(obj):
    """Yield contribution-shaped dictionaries anywhere in an API response."""
    if isinstance(obj, dict):
        if obj.get("ItemType") == "Contribution":
            yield obj
        for value in obj.values():
            if isinstance(value, (dict, list)):
                yield from iter_contribution_items(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from iter_contribution_items(value)


def substantive_api_items(data: dict) -> list[dict]:
    seen = set()
    items = []
    for item in iter_contribution_items(data):
        item_id = str(item.get("ItemId") or item.get("ExternalId") or "")
        if item_id and item_id in seen:
            continue
        if item_id:
            seen.add(item_id)

        attributed = clean_text(item.get("AttributedTo"))
        value = clean_text(item.get("Value"))
        tag = str(item.get("HRSTag") or "")

        if not attributed:
            continue
        if tag in NON_SPEECH_TAGS:
            continue
        if not value or value.lower() in NON_SPEECH_VALUES:
            continue
        if len(value.split()) < 5:
            continue
        items.append(item)
    return items


def fetch_api_debate(session: requests.Session, debate_id: str) -> tuple[dict, str, int]:
    api_url = f"{API_BASE}/debates/debate/{debate_id}.json"
    response = session.get(api_url, timeout=45)
    response.raise_for_status()
    return response.json(), api_url, response.status_code


def main() -> int:
    if not REGISTRY.exists():
        print(f"Registry not found: {REGISTRY}", file=sys.stderr)
        return 2

    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)

    registry = pd.read_csv(REGISTRY, dtype=str).fillna("")
    eligible = registry[
        registry["screening_status"].str.startswith(("include", "screen_contextual"))
    ].copy()

    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-GB,en;q=0.9",
    })

    extraction_rows: list[dict] = []
    log_rows: list[dict] = []
    retrieved_at = datetime.now(timezone.utc).isoformat()

    for _, debate in eligible.iterrows():
        source_url = debate["source_url"]
        debate_id = debate_id_from_url(source_url)
        started = time.time()

        if not debate_id:
            log_rows.append({
                "date": debate["date"],
                "debate_title": debate["debate_title"],
                "debate_id": "",
                "api_url": "",
                "source_url": source_url,
                "http_status": "",
                "parse_status": "unresolved_no_uuid_in_registry_url",
                "contributions_parsed": 0,
                "contributions_retained": 0,
                "seconds": round(time.time() - started, 2),
            })
            continue

        try:
            data, api_url, status_code = fetch_api_debate(session, debate_id)
            overview = data.get("Overview") or {}
            items = substantive_api_items(data)
            retained_count = 0

            for item in items:
                text = clean_text(item.get("Value"))
                keep = retain_contribution(
                    text, debate["debate_title"], debate["screening_status"]
                )
                retained_count += int(keep)

                speaker_raw = clean_text(item.get("AttributedTo"))
                contribution_id = str(item.get("ExternalId") or item.get("ItemId") or "")
                item_id = str(item.get("ItemId") or "")
                speech_id = contribution_id or hashlib.sha256(
                    f"{debate_id}|{speaker_raw}|{text}".encode("utf-8")
                ).hexdigest()[:24]

                api_date = str(overview.get("Date") or "")[:10]
                date = api_date if re.fullmatch(r"\d{4}-\d{2}-\d{2}", api_date) else debate["date"]
                year = int(date[:4]) if date[:4].isdigit() else int(debate["year"])

                extraction_rows.append({
                    "speech_id": speech_id,
                    "date": date,
                    "year": year,
                    "house": clean_text(overview.get("House")) or debate["house"],
                    "venue": clean_text(overview.get("Location")) or debate["venue"],
                    "debate_id": debate_id,
                    "debate_title": debate["debate_title"],
                    "api_debate_title": clean_text(overview.get("Title")),
                    "item_id": item_id,
                    "contribution_id": contribution_id,
                    "order_in_section": item.get("OrderInSection"),
                    "member_id": item.get("MemberId"),
                    "speaker": normalise_speaker(speaker_raw),
                    "speaker_raw": speaker_raw,
                    "party": parse_party(speaker_raw),
                    "speech_text": text,
                    "matched_terms": ";".join(matched_terms(text)),
                    "word_count": len(text.split()),
                    "source_url": source_url,
                    "api_url": api_url,
                    "screening_status": debate["screening_status"],
                    "retain_for_analysis": keep,
                    "retrieved_at_utc": retrieved_at,
                })

            log_rows.append({
                "date": debate["date"],
                "debate_title": debate["debate_title"],
                "debate_id": debate_id,
                "api_url": api_url,
                "source_url": source_url,
                "http_status": status_code,
                "parse_status": "ok" if items else "no_substantive_contributions_parsed",
                "contributions_parsed": len(items),
                "contributions_retained": retained_count,
                "seconds": round(time.time() - started, 2),
            })
        except Exception as exc:
            log_rows.append({
                "date": debate["date"],
                "debate_title": debate["debate_title"],
                "debate_id": debate_id,
                "api_url": f"{API_BASE}/debates/debate/{debate_id}.json",
                "source_url": source_url,
                "http_status": getattr(locals().get("response", None), "status_code", ""),
                "parse_status": f"ERROR: {type(exc).__name__}: {exc}",
                "contributions_parsed": 0,
                "contributions_retained": 0,
                "seconds": round(time.time() - started, 2),
            })
        time.sleep(0.15)

    build_log = pd.DataFrame(log_rows)
    build_log.to_csv(BUILD_LOG, index=False)

    raw = pd.DataFrame(extraction_rows)
    if raw.empty:
        print("No contributions were extracted; see build log.", file=sys.stderr)
        return 1

    raw["dedupe_key"] = (
        raw["debate_id"].astype(str) + "|" +
        raw["item_id"].astype(str) + "|" +
        raw["speaker"].astype(str) + "|" +
        raw["speech_text"].astype(str)
    ).map(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest())
    raw = raw.drop_duplicates("dedupe_key").drop(columns="dedupe_key")
    raw = raw.sort_values(["date", "debate_id", "order_in_section"], kind="stable")
    raw.to_csv(RAW_OUT, index=False)

    final = raw[raw["retain_for_analysis"]].copy()
    final = final.drop(columns="retain_for_analysis")
    final.to_csv(FINAL_OUT, index=False)

    by_year = final.groupby("year", dropna=False).agg(
        contributions=("speech_id", "count"),
        debates=("debate_id", "nunique"),
        speakers=("speaker", "nunique"),
        words=("word_count", "sum"),
    ).reset_index()
    all_years = pd.DataFrame({"year": list(range(2020, 2026))})
    by_year = all_years.merge(by_year, on="year", how="left").fillna(0)
    for col in ["contributions", "debates", "speakers", "words"]:
        by_year[col] = by_year[col].astype(int)
    by_year.to_csv(QA_OUT, index=False)

    unresolved = int((build_log["parse_status"] != "ok").sum()) if not build_log.empty else 0
    print(f"Extracted {len(raw):,} unique attributed contributions before screening")
    print(f"Retained {len(final):,} contributions in analytical corpus")
    print(f"Registry rows needing follow-up: {unresolved}")
    print(by_year.to_string(index=False))
    print(f"Final corpus: {FINAL_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
