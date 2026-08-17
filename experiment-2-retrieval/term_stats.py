"""Experiment 2, step 0: BM25 term statistics for the frozen section-aware chunks.

Computes corpus statistics only. No ranking, no retrieval, no verdicts. Every
number here is an *input* to BM25 that can be derived without running it:
document frequency, IDF, which terms hit the negative-IDF floor, token lengths,
and the length-normalisation factor per chunk.

Running this before writing predictions is deliberate and is recorded in
PRE-REGISTRATION.md. Knowing your inputs before predicting is what separates an
informed prediction from a guess; what would compromise the pre-registration is
computing the actual rankings first, which this script does not do.

The IDF calculation mirrors rank_bm25.BM25Okapi._calc_idf exactly, including the
epsilon floor applied to negative values, so the reported numbers are the ones
BM25Okapi will use rather than a textbook approximation.

Run:  python experiment-2-retrieval/term_stats.py
"""

import math
import re
import sys
from collections import Counter
from pathlib import Path

# This directory's name contains a hyphen, so it cannot be imported as a package
# and `python -m` will not reach it. config.py and chunkers.py live one level up,
# frozen by experiment 1 and reused here unchanged.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from chunkers import Chunk, markdown_section_chunks  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
REPORT_FILE = OUTPUT_DIR / "term_statistics.md"

# rank_bm25.BM25Okapi defaults. Stated here rather than imported so the report is
# readable without the library installed, and because these differ from Lucene's
# k1=1.2 -- a difference that matters when quoting scores.
BM25_K1 = 1.5
BM25_B = 0.75
BM25_EPSILON = 0.25

# Section-aware chunking of this document yields the front matter plus 12
# sections. If this ever changes, the frozen experiment has drifted.
EXPECTED_CHUNKS = 13


def tokenize(text: str) -> list[str]:
    """The frozen tokenizer: lowercase, punctuation to whitespace, unigrams.

    Every character that is not a digit or an ASCII letter becomes a separator.
    That covers markdown syntax (``##``, ``**``, ``|``), the table rules, and the
    non-ASCII punctuation in the source (en dash in "5-10", curly apostrophe in
    "customer's"), which a `string.punctuation` filter would miss.

    Punctuation becomes a space rather than being deleted, so "fee-waiver"
    tokenizes to ("fee", "waiver") and matches a query saying "fee waiver".
    Deleting it instead would produce "feewaiver", which matches nothing.
    """
    return re.sub(r"[^0-9a-z]+", " ", text.lower()).split()


def build_chunks() -> list[Chunk]:
    raw = config.SOURCE_DOCUMENT.read_text(encoding="utf-8")
    chunks = markdown_section_chunks(raw, config.STRATEGY_C)
    if len(chunks) != EXPECTED_CHUNKS:
        raise SystemExit(
            f"Expected {EXPECTED_CHUNKS} section-aware chunks, got {len(chunks)}. "
            "The frozen configuration has changed."
        )
    return chunks


def robertson_idf(corpus_size: int, doc_freq: int) -> float:
    """IDF exactly as rank_bm25.BM25Okapi computes it, before any flooring.

    This is the original Robertson form, which goes negative once a term appears
    in more than half the corpus. Lucene wraps it so the result is always
    positive; rank_bm25 does not, and floors the negatives instead.
    """
    return math.log(corpus_size - doc_freq + 0.5) - math.log(doc_freq + 0.5)


def corpus_stats(chunks: list[Chunk]) -> dict:
    tokenized = [tokenize(chunk.text) for chunk in chunks]
    doc_freq: Counter[str] = Counter()
    for tokens in tokenized:
        doc_freq.update(set(tokens))

    corpus_size = len(chunks)
    raw_idf = {term: robertson_idf(corpus_size, freq) for term, freq in doc_freq.items()}

    # rank_bm25 averages over the whole vocabulary including the negative values,
    # then floors every negative term to epsilon * that average. All floored
    # terms therefore share one weight and become indistinguishable.
    average_idf = sum(raw_idf.values()) / len(raw_idf)
    floor = BM25_EPSILON * average_idf
    effective_idf = {
        term: (floor if value < 0 else value) for term, value in raw_idf.items()
    }

    doc_len = [len(tokens) for tokens in tokenized]
    avgdl = sum(doc_len) / corpus_size

    return {
        "chunks": chunks,
        "tokenized": tokenized,
        "doc_freq": doc_freq,
        "raw_idf": raw_idf,
        "effective_idf": effective_idf,
        "average_idf": average_idf,
        "floor": floor,
        "doc_len": doc_len,
        "avgdl": avgdl,
        "corpus_size": corpus_size,
    }


def length_factor(doc_len: int, avgdl: float) -> float:
    """The denominator term BM25 applies for document length.

    Above 1.0 suppresses a chunk's score, below 1.0 boosts it. For fixed-size
    chunking every chunk sits near 1.0 and b is close to inert; section-aware
    chunks vary widely, so b does real work here.
    """
    return 1 - BM25_B + BM25_B * doc_len / avgdl


def chunk_label(chunk: Chunk) -> str:
    heading = chunk.heading or "(front matter)"
    return f"C-{chunk.index} {heading.removeprefix('## ')}"


def render_corpus_section(stats: dict) -> list[str]:
    lines = [
        "## Corpus",
        "",
        f"- chunks: {stats['corpus_size']}",
        f"- vocabulary: {len(stats['doc_freq'])} distinct terms",
        f"- total tokens: {sum(stats['doc_len'])}",
        f"- average chunk length (avgdl): {stats['avgdl']:.1f} tokens",
        f"- average IDF across the vocabulary: {stats['average_idf']:.4f}",
        f"- negative-IDF floor (epsilon x average IDF): {stats['floor']:.4f}",
        "",
        "A term's IDF goes negative once it appears in more than half the chunks, "
        f"so any term in {stats['corpus_size'] // 2 + 1} or more of "
        f"{stats['corpus_size']} chunks is floored to "
        f"{stats['floor']:.4f} and becomes indistinguishable from every other "
        "floored term.",
        "",
        "| chunk | tokens | dl / avgdl | length factor | effect |",
        "|---|---:|---:|---:|---|",
    ]
    for chunk, tokens in zip(stats["chunks"], stats["doc_len"]):
        ratio = tokens / stats["avgdl"]
        factor = length_factor(tokens, stats["avgdl"])
        effect = "penalised" if factor > 1 else "boosted"
        lines.append(
            f"| {chunk_label(chunk)} | {tokens} | {ratio:.2f} | {factor:.3f} | {effect} |"
        )
    lines.append("")
    return lines


def render_floored_terms(stats: dict) -> list[str]:
    floored = sorted(
        (term for term, value in stats["raw_idf"].items() if value < 0),
        key=lambda term: (-stats["doc_freq"][term], term),
    )
    lines = [
        "## Terms floored across the whole corpus",
        "",
        f"{len(floored)} of {len(stats['doc_freq'])} vocabulary terms have negative "
        "raw IDF and are floored. Each contributes the same weight regardless of "
        "how common it actually is.",
        "",
        "| term | document frequency | raw IDF |",
        "|---|---:|---:|",
    ]
    for term in floored:
        lines.append(
            f"| `{term}` | {stats['doc_freq'][term]} | {stats['raw_idf'][term]:.4f} |"
        )
    lines.append("")
    return lines


def render_question_section(index: int, question: str, stats: dict) -> list[str]:
    query_tokens = tokenize(question)
    seen: list[str] = []
    for token in query_tokens:
        if token not in seen:
            seen.append(token)

    lines = [
        f"## Q{index + 1}",
        "",
        f"> {question}",
        "",
        f"Tokenized to {len(query_tokens)} tokens, {len(seen)} distinct.",
        "",
        "| term | df | raw IDF | effective IDF | floored | chunks containing it |",
        "|---|---:|---:|---:|---|---|",
    ]

    # Highest effective IDF first: these are the terms that actually decide the
    # BM25 ranking for this question.
    def sort_key(term: str) -> tuple[float, str]:
        return (-stats["effective_idf"].get(term, 0.0), term)

    absent: list[str] = []
    for term in sorted(seen, key=sort_key):
        freq = stats["doc_freq"].get(term, 0)
        if freq == 0:
            absent.append(term)
            continue
        holders = [
            f"C-{chunk.index}"
            for chunk, tokens in zip(stats["chunks"], stats["tokenized"])
            if term in tokens
        ]
        raw = stats["raw_idf"][term]
        effective = stats["effective_idf"][term]
        lines.append(
            f"| `{term}` | {freq} | {raw:.4f} | {effective:.4f} "
            f"| {'yes' if raw < 0 else ''} | {', '.join(holders)} |"
        )

    lines.append("")
    if absent:
        lines += [
            "Query terms absent from the corpus, contributing nothing: "
            + ", ".join(f"`{term}`" for term in absent),
            "",
        ]
    return lines


def render_report(stats: dict) -> str:
    lines = [
        "# Experiment 2, step 0: BM25 term statistics",
        "",
        "Corpus statistics only. No ranking, no retrieval, no verdicts.",
        "",
        "Chunking: markdown section-aware (`## ` headings), frozen from "
        "experiment 1. Tokenizer: lowercase, punctuation to whitespace, "
        "unigrams, no stemming.",
        "",
        f"BM25 parameters: `k1={BM25_K1}`, `b={BM25_B}`, "
        f"`epsilon={BM25_EPSILON}` (rank_bm25 BM25Okapi defaults).",
        "",
    ]
    lines += render_corpus_section(stats)
    lines += render_floored_terms(stats)
    for index, question in enumerate(config.QUESTIONS):
        lines += render_question_section(index, question, stats)
    return "\n".join(lines) + "\n"


def main() -> None:
    stats = corpus_stats(build_chunks())

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(render_report(stats), encoding="utf-8")

    floored = sum(1 for value in stats["raw_idf"].values() if value < 0)
    print(f"Chunks: {stats['corpus_size']}   vocabulary: {len(stats['doc_freq'])} terms")
    print(f"avgdl: {stats['avgdl']:.1f} tokens")
    print(f"average IDF: {stats['average_idf']:.4f}   floor: {stats['floor']:.4f}")
    print(f"Floored terms: {floored} of {len(stats['doc_freq'])}")
    print()

    for index, question in enumerate(config.QUESTIONS):
        terms = {term for term in tokenize(question) if stats["doc_freq"].get(term)}
        # Tie-break on the term itself: many terms share df=1 and therefore an
        # identical IDF, and set iteration order is not stable across runs.
        ranked = sorted(terms, key=lambda t: (-stats["effective_idf"][t], t))
        top = ", ".join(
            f"{term} (df={stats['doc_freq'][term]}, idf={stats['effective_idf'][term]:.2f})"
            for term in ranked[:3]
        )
        print(f"Q{index + 1} highest-IDF terms: {top}")

    print()
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
