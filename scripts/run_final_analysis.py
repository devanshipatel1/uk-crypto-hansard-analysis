#!/usr/bin/env python3
"""Run the final quantitative analysis for the Hansard cryptoasset corpus.

Outputs are designed to map directly to the dissertation research questions:
RQ1: thematic evolution over time via TF-IDF, LDA and yearly topic prevalence.
RQ2: actor/institution–theme associations via weighted topic probabilities.

The script avoids generic sentiment analysis and reports model diagnostics,
statistical assumptions and representative speeches for transparent topic
interpretation.
"""
from __future__ import annotations

import math
import re
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csc_matrix
from scipy.stats import chi2_contingency
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/hansard_crypto_2020_2025_final.csv"
TOPIC_DATA = ROOT / "data/processed/hansard_crypto_2020_2025_topics.csv"
TABLE_DIR = ROOT / "outputs/tables"
FIG_DIR = ROOT / "outputs/figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEEDS = [7, 21, 42, 84]
CANDIDATE_K = list(range(4, 9))
TOP_N_WORDS = 12

# Remove parliamentary boilerplate but preserve substantive regulatory vocabulary.
CUSTOM_STOP = {
    "hon", "right", "friend", "noble", "lord", "lords", "member", "members",
    "minister", "government", "house", "committee", "amendment", "clause",
    "bill", "question", "debate", "say", "said", "says", "thank", "think",
    "like", "just", "really", "also", "would", "could", "should", "one",
    "us", "uk", "united", "kingdom", "new", "make", "made", "may", "must",
    "many", "much", "well", "time", "today", "point", "issue", "issues",
}
STOP_WORDS = sorted(set(ENGLISH_STOP_WORDS).union(CUSTOM_STOP))

INSTITUTIONS = {
    "FCA": r"\bFCA\b|\bFinancial Conduct Authority\b",
    "HM Treasury": r"\bHM Treasury\b|\bHis Majesty'?s Treasury\b|\bHer Majesty'?s Treasury\b",
    "Bank of England": r"\bBank of England\b",
    "Law Commission": r"\bLaw Commission\b",
    "Treasury Committee": r"\bTreasury Committee\b",
    "FSB": r"\bFinancial Stability Board\b|\bFSB\b",
    "FATF": r"\bFinancial Action Task Force\b|\bFATF\b",
}


def normalise_text(text: object) -> str:
    text = "" if pd.isna(text) else str(text)
    text = text.lower()
    text = text.replace("crypto-assets", "cryptoassets").replace("crypto-assets", "cryptoassets")
    text = text.replace("crypto asset", "cryptoasset").replace("crypto-assets", "cryptoassets")
    text = text.replace("financial conduct authority", "fca")
    text = text.replace("bank of england", "bank_of_england")
    text = text.replace("law commission", "law_commission")
    text = text.replace("financial stability", "financial_stability")
    text = text.replace("financial promotion", "financial_promotion")
    text = text.replace("consumer protection", "consumer_protection")
    text = text.replace("money laundering", "money_laundering")
    text = text.replace("distributed ledger", "distributed_ledger")
    text = text.replace("digital asset", "digital_asset")
    text = re.sub(r"[^a-z0-9_\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def topic_top_indices(model: LatentDirichletAllocation, n: int = TOP_N_WORDS) -> list[np.ndarray]:
    return [np.argsort(comp)[::-1][:n] for comp in model.components_]


def topic_diversity(model: LatentDirichletAllocation, n: int = TOP_N_WORDS) -> float:
    tops = topic_top_indices(model, n)
    flat = np.concatenate(tops)
    return len(np.unique(flat)) / len(flat)


def npmi_coherence(model: LatentDirichletAllocation, X_binary, n: int = 10) -> float:
    """Mean topic NPMI over top-word pairs using document co-occurrence."""
    Xb = csc_matrix(X_binary.astype(bool).astype(np.int8))
    n_docs = Xb.shape[0]
    if n_docs == 0:
        return float("nan")
    df = np.asarray(Xb.sum(axis=0)).ravel().astype(float)
    scores = []
    for inds in topic_top_indices(model, n):
        pair_scores = []
        for i, j in combinations(inds, 2):
            p_i = df[i] / n_docs
            p_j = df[j] / n_docs
            both = Xb[:, i].multiply(Xb[:, j]).sum()
            p_ij = float(both) / n_docs
            if p_ij <= 0 or p_i <= 0 or p_j <= 0:
                continue
            pmi = math.log(p_ij / (p_i * p_j))
            denom = -math.log(p_ij)
            if denom > 0:
                pair_scores.append(pmi / denom)
        if pair_scores:
            scores.append(float(np.mean(pair_scores)))
    return float(np.mean(scores)) if scores else float("nan")


def aligned_topic_similarity(a: LatentDirichletAllocation, b: LatentDirichletAllocation) -> float:
    sim = cosine_similarity(a.components_, b.components_)
    rows, cols = linear_sum_assignment(-sim)
    return float(np.mean(sim[rows, cols]))


def fit_lda(X, k: int, seed: int) -> LatentDirichletAllocation:
    model = LatentDirichletAllocation(
        n_components=k,
        learning_method="batch",
        max_iter=100,
        evaluate_every=-1,
        random_state=seed,
        n_jobs=-1,
    )
    return model.fit(X)


def safe_speaker(s: object) -> str:
    s = "" if pd.isna(s) else str(s).strip()
    return s or "Unknown"


def main() -> int:
    if not DATA.exists():
        raise SystemExit(f"Final corpus not found: {DATA}")

    df = pd.read_csv(DATA)
    if df.empty:
        raise SystemExit("Final corpus is empty.")

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["speaker"] = df["speaker"].map(safe_speaker)
    df["clean_text"] = df["speech_text"].map(normalise_text)
    df = df[df["clean_text"].str.split().str.len() >= 5].reset_index(drop=True)

    # -------- Descriptive corpus statistics --------
    yearly = df.groupby("year").agg(
        contributions=("speech_id", "count"),
        debates=("debate_id", "nunique"),
        speakers=("speaker", "nunique"),
        words=("word_count", "sum"),
    ).reset_index()
    years = pd.DataFrame({"year": list(range(2020, 2026))})
    yearly = years.merge(yearly, on="year", how="left").fillna(0)
    for c in ["contributions", "debates", "speakers", "words"]:
        yearly[c] = yearly[c].astype(int)
    yearly.to_csv(TABLE_DIR / "analysis_corpus_by_year.csv", index=False)

    by_house = df.groupby("house").agg(
        contributions=("speech_id", "count"),
        debates=("debate_id", "nunique"),
        speakers=("speaker", "nunique"),
    ).reset_index().sort_values("contributions", ascending=False)
    by_house.to_csv(TABLE_DIR / "analysis_corpus_by_house.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(yearly["year"].astype(str), yearly["contributions"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Parliamentary contributions")
    ax.set_title("Cryptoasset-related Hansard contributions by year")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "corpus_contributions_by_year.png", dpi=200)
    plt.close(fig)

    # -------- Exploratory TF-IDF --------
    tfidf = TfidfVectorizer(
        stop_words=STOP_WORDS,
        min_df=2,
        max_df=0.90,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_\-]{2,}\b",
    )
    tfidf_matrix = tfidf.fit_transform(df["clean_text"])
    tfidf_terms = np.asarray(tfidf.get_feature_names_out())
    mean_scores = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
    top = np.argsort(mean_scores)[::-1][:40]
    tfidf_out = pd.DataFrame({"term": tfidf_terms[top], "mean_tfidf": mean_scores[top]})
    tfidf_out.to_csv(TABLE_DIR / "analysis_tfidf_top_terms.csv", index=False)

    tfidf_year_rows = []
    for year, idx in df.groupby("year").groups.items():
        scores = np.asarray(tfidf_matrix[list(idx)].mean(axis=0)).ravel()
        for rank, term_idx in enumerate(np.argsort(scores)[::-1][:20], start=1):
            tfidf_year_rows.append({
                "year": int(year), "rank": rank,
                "term": tfidf_terms[term_idx], "mean_tfidf": scores[term_idx],
            })
    pd.DataFrame(tfidf_year_rows).to_csv(TABLE_DIR / "analysis_tfidf_terms_by_year.csv", index=False)

    # -------- Count representation and candidate LDA models --------
    vectorizer = CountVectorizer(
        stop_words=STOP_WORDS,
        min_df=3,
        max_df=0.88,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_\-]{2,}\b",
    )
    X = vectorizer.fit_transform(df["clean_text"])
    vocab = np.asarray(vectorizer.get_feature_names_out())
    if X.shape[1] < 20:
        raise SystemExit(f"Vocabulary too small for LDA: {X.shape}")

    model_rows = []
    baseline_models = {}
    for k in CANDIDATE_K:
        models = [fit_lda(X, k, seed) for seed in RANDOM_SEEDS]
        baseline = models[RANDOM_SEEDS.index(42)]
        baseline_models[k] = baseline
        stability_scores = [
            aligned_topic_similarity(baseline, m)
            for seed, m in zip(RANDOM_SEEDS, models)
            if seed != 42
        ]
        model_rows.append({
            "k": k,
            "npmi_coherence": npmi_coherence(baseline, X, n=10),
            "topic_diversity_top12": topic_diversity(baseline, TOP_N_WORDS),
            "mean_seed_stability": float(np.mean(stability_scores)),
            "perplexity": float(baseline.perplexity(X)),
        })

    model_selection = pd.DataFrame(model_rows)
    # Primary selection criterion = highest NPMI coherence. Stability and diversity
    # are retained as diagnostics rather than blended into an opaque score.
    best_k = int(model_selection.sort_values(
        ["npmi_coherence", "mean_seed_stability", "topic_diversity_top12"],
        ascending=[False, False, False]
    ).iloc[0]["k"])
    model_selection["selected"] = model_selection["k"].eq(best_k)
    model_selection.to_csv(TABLE_DIR / "analysis_model_selection.csv", index=False)

    lda = baseline_models[best_k]
    doc_topic = lda.transform(X)

    # Topic terms and probabilities.
    topic_term_rows = []
    for topic_id, comp in enumerate(lda.components_):
        inds = np.argsort(comp)[::-1][:20]
        probs = comp / comp.sum()
        for rank, idx in enumerate(inds, start=1):
            topic_term_rows.append({
                "topic": topic_id,
                "rank": rank,
                "term": vocab[idx],
                "term_probability": probs[idx],
            })
    pd.DataFrame(topic_term_rows).to_csv(TABLE_DIR / "analysis_topic_terms.csv", index=False)

    for t in range(best_k):
        df[f"topic_{t}"] = doc_topic[:, t]
    df["dominant_topic"] = np.argmax(doc_topic, axis=1)
    df["dominant_topic_probability"] = np.max(doc_topic, axis=1)
    df.to_csv(TOPIC_DATA, index=False)

    # -------- RQ1: topic prevalence over time --------
    topic_cols = [f"topic_{t}" for t in range(best_k)]
    annual_prev = df.groupby("year")[topic_cols].mean().reset_index()
    all_years = pd.DataFrame({"year": list(range(2020, 2026))})
    annual_prev = all_years.merge(annual_prev, on="year", how="left")
    annual_prev.to_csv(TABLE_DIR / "analysis_topic_prevalence_by_year.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    observed = annual_prev.dropna(subset=topic_cols, how="all")
    for t in range(best_k):
        ax.plot(observed["year"], observed[f"topic_{t}"], marker="o", label=f"Topic {t}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean document-topic probability")
    ax.set_title("Evolution of cryptoasset regulatory themes in Hansard")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "topic_prevalence_by_year.png", dpi=200)
    plt.close(fig)

    dominant_counts = pd.crosstab(df["year"], df["dominant_topic"])
    dominant_counts.to_csv(TABLE_DIR / "analysis_dominant_topic_counts_by_year.csv")

    # Exclude years with no documents automatically. Report assumption diagnostics.
    chi2, p_value, dof, expected = chi2_contingency(dominant_counts.values)
    n = int(dominant_counts.values.sum())
    min_dim = min(dominant_counts.shape[0] - 1, dominant_counts.shape[1] - 1)
    cramers_v = math.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else float("nan")
    chi_out = pd.DataFrame([{
        "n": n,
        "years_in_test": ";".join(map(str, dominant_counts.index.tolist())),
        "topics_in_test": dominant_counts.shape[1],
        "chi_square": chi2,
        "degrees_of_freedom": dof,
        "p_value": p_value,
        "cramers_v": cramers_v,
        "expected_cells_below_5": int((expected < 5).sum()),
        "expected_cells_total": int(expected.size),
        "minimum_expected_count": float(expected.min()),
        "note": "2020 excluded automatically because no eligible contributions remained after screening.",
    }])
    chi_out.to_csv(TABLE_DIR / "analysis_chi_square.csv", index=False)

    # Representative high-probability contributions for transparent topic labelling.
    rep_rows = []
    for t in range(best_k):
        for rank, idx in enumerate(np.argsort(doc_topic[:, t])[::-1][:5], start=1):
            row = df.iloc[idx]
            rep_rows.append({
                "topic": t,
                "rank": rank,
                "topic_probability": doc_topic[idx, t],
                "date": row["date"],
                "year": row["year"],
                "debate_title": row["debate_title"],
                "speaker": row["speaker"],
                "speech_id": row["speech_id"],
                "source_url": row["source_url"],
                "speech_excerpt": re.sub(r"\s+", " ", str(row["speech_text"]))[:500],
            })
    pd.DataFrame(rep_rows).to_csv(TABLE_DIR / "analysis_representative_speeches.csv", index=False)

    # -------- RQ2: weighted actor-topic associations --------
    actor_sum = df.groupby("speaker")[topic_cols].sum()
    actor_mean = df.groupby("speaker")[topic_cols].mean()
    actor_counts = df.groupby("speaker").size().rename("contributions")
    actor_words = df.groupby("speaker")["word_count"].sum().rename("words")
    actor = pd.concat([actor_counts, actor_words, actor_sum.add_prefix("weight_"), actor_mean.add_prefix("mean_")], axis=1)
    actor["total_topic_weight"] = actor[[f"weight_topic_{t}" for t in range(best_k)]].sum(axis=1)
    actor = actor.reset_index().sort_values(["contributions", "total_topic_weight"], ascending=False)
    actor.to_csv(TABLE_DIR / "analysis_actor_topic_weights.csv", index=False)

    # Actor-topic long form for network construction / plotting.
    actor_long = []
    for _, row in actor.iterrows():
        for t in range(best_k):
            actor_long.append({
                "speaker": row["speaker"],
                "contributions": int(row["contributions"]),
                "topic": t,
                "weight": row[f"weight_topic_{t}"],
                "mean_probability": row[f"mean_topic_{t}"],
            })
    pd.DataFrame(actor_long).to_csv(TABLE_DIR / "analysis_actor_topic_network_edges.csv", index=False)

    # Visualise topic profiles for the most active actors, not political influence.
    top_actors = actor.head(15).copy()
    heat = top_actors[[f"mean_topic_{t}" for t in range(best_k)]].to_numpy()
    fig, ax = plt.subplots(figsize=(8, max(5, len(top_actors) * 0.38)))
    image = ax.imshow(heat, aspect="auto")
    ax.set_xticks(range(best_k), [f"Topic {t}" for t in range(best_k)])
    ax.set_yticks(range(len(top_actors)), top_actors["speaker"])
    ax.set_title("Mean topic association of most active parliamentary actors")
    fig.colorbar(image, ax=ax, label="Mean topic probability")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "actor_topic_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Institutional mention-topic relationships.
    institution_rows = []
    original_text = df["speech_text"].fillna("")
    for institution, pattern in INSTITUTIONS.items():
        mask = original_text.str.contains(pattern, flags=re.I, regex=True)
        subset = df.loc[mask]
        result = {
            "institution": institution,
            "mentions_in_contributions": int(mask.sum()),
            "unique_debates": int(subset["debate_id"].nunique()) if not subset.empty else 0,
        }
        for t in range(best_k):
            result[f"mean_topic_{t}"] = float(subset[f"topic_{t}"].mean()) if not subset.empty else np.nan
            result[f"weight_topic_{t}"] = float(subset[f"topic_{t}"].sum()) if not subset.empty else 0.0
        institution_rows.append(result)
    institutions = pd.DataFrame(institution_rows).sort_values("mentions_in_contributions", ascending=False)
    institutions.to_csv(TABLE_DIR / "analysis_institution_topic_weights.csv", index=False)

    # -------- Human-readable machine-generated results summary --------
    topic_terms = pd.read_csv(TABLE_DIR / "analysis_topic_terms.csv")
    lines = [
        "# Final quantitative analysis summary",
        "",
        f"Analytical corpus: {len(df)} contributions across {df['debate_id'].nunique()} debates/proceedings.",
        f"Observed study years with eligible contributions: {', '.join(map(str, sorted(df['year'].dropna().unique())))}.",
        "No eligible 2020 contribution remained after the documented screening protocol.",
        "",
        f"Selected LDA topic count: K={best_k}, chosen primarily by highest NPMI coherence among K={CANDIDATE_K[0]}–{CANDIDATE_K[-1]}, with diversity and seed stability retained as diagnostics.",
        "",
        "## Top words by topic",
    ]
    for t in range(best_k):
        words = topic_terms[topic_terms["topic"] == t].sort_values("rank").head(12)["term"].tolist()
        lines.append(f"- Topic {t}: {', '.join(words)}")
    lines += [
        "",
        "## Chi-square test",
        f"χ²({int(dof)}, N={n}) = {chi2:.3f}, p = {p_value:.6g}, Cramér's V = {cramers_v:.3f}.",
        f"Expected-frequency diagnostic: {(expected < 5).sum()} of {expected.size} cells below 5; minimum expected count = {expected.min():.3f}.",
        "Interpret this test as supplementary because contributions are clustered within debates and therefore are not fully independent observations.",
        "",
        "## Reproducibility",
        "All numeric tables, topic-probability data and figures are generated by scripts/run_final_analysis.py from the final screened Hansard corpus.",
    ]
    (TABLE_DIR / "FINAL_ANALYSIS_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
