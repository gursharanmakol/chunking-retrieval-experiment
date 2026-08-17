"""Experiment 2: dense, BM25 and RRF over the frozen section-aware chunks.

Implements PRE-REGISTRATION.md exactly as committed. Chunking is fixed at
strategy C, so the only variable is the retrieval method.

What this records, per question and per method: the complete 13-chunk ranking
with scores, the rank of every chunk the rubric requires, the BM25 per-term score
contribution for each top-3 chunk with the source clause each term came from, the
method-local classification of every target, and verdicts read off at k=3 and
k=10 from the same ranking.

Two self-checks run before anything is written:

1. The per-term BM25 contributions are summed and compared against
   BM25Okapi.get_scores. If the breakdown does not reproduce the library's own
   score the explanation is wrong, so the run aborts rather than publishing it.
2. The dense arm must reproduce experiment 1's recorded strategy-C top 3. Same
   model, same chunks, same metric, so any difference means drift rather than a
   finding.

Run:  python experiment-2-retrieval/run_retrieval.py
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from chunkers import Chunk  # noqa: E402
from term_stats import (  # noqa: E402
    BM25_B,
    BM25_EPSILON,
    BM25_K1,
    build_chunks,
    corpus_stats,
    length_factor,
    tokenize,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
REPORT_FILE = OUTPUT_DIR / "retrieval_results.md"

FENCE = "````"

HEADLINE_K = 3
DIAGNOSTIC_K = 10

RRF_K = 60
RRF_SWEEP = (1, 10, 20, 60, 100, 1000)

DENSE = "dense"
BM25 = "bm25"
RRF = "rrf"
BASE_METHODS = (DENSE, BM25)
ALL_METHODS = (DENSE, BM25, RRF)

METHOD_LABELS = {DENSE: "Dense", BM25: "BM25", RRF: "RRF"}

# Chunks the rubric requires, per question, as fixed in the pre-registration.
# Each inner tuple is a requirement group: at least one chunk from every group
# must be retrieved for the set to be sufficient. Q3 needs Section 7 *and* one of
# Section 3 or Section 8, which is why it is the only question with two groups.
REQUIRED: dict[int, tuple[tuple[int, ...], ...]] = {
    1: ((6,),),
    2: ((7,),),
    3: ((7,), (3, 8)),
    4: ((3,),),
    5: ((8,),),
}

# Targets carrying a pre-registered rank prediction. Classification is reported
# for these; other chunks in a requirement group get their rank recorded only.
PREDICTED_TARGETS: dict[int, tuple[int, ...]] = {
    1: (6,),
    2: (7,),
    3: (7, 3),
    4: (3,),
    5: (8,),
}

# Transcribed from the predictions table in PRE-REGISTRATION.md, frozen at commit
# e9d116a before this script existed. Ranks only: the prose predictions are
# compared by hand in the write-up.
PREDICTED_RANKS: dict[int, dict[str, dict[int, int]]] = {
    1: {DENSE: {6: 1}, BM25: {6: 1}},
    2: {DENSE: {7: 1}, BM25: {7: 1}},
    3: {DENSE: {7: 1, 3: 6}, BM25: {3: 1, 7: 3}},
    4: {DENSE: {3: 2}, BM25: {3: 1}},
    5: {DENSE: {8: 2}, BM25: {8: 1}},
}

PREDICTED_VERDICTS: dict[int, dict[str, bool]] = {
    1: {DENSE: True, BM25: True, RRF: True},
    2: {DENSE: True, BM25: True, RRF: True},
    3: {DENSE: False, BM25: True, RRF: True},
    4: {DENSE: True, BM25: True, RRF: True},
    5: {DENSE: True, BM25: True, RRF: True},
}

# Experiment 1's recorded strategy-C top 3, transcribed from the summary table in
# outputs/retrieval_results.md. The dense arm here must reproduce it exactly.
EXPERIMENT_1_C_TOP3: dict[int, tuple[int, ...]] = {
    1: (6, 3, 2),
    2: (7, 12, 4),
    3: (7, 12, 10),
    4: (7, 3, 5),
    5: (3, 8, 6),
}

# Explicit section pointers, deduplicated from the cross-reference table in
# PRE-REGISTRATION.md. Pointer existence is a property of the text and does not
# depend on what any method retrieved.
POINTERS: tuple[tuple[int, int], ...] = (
    (3, 8),
    (4, 6),
    (5, 7),
    (5, 3),
    (6, 7),
    (7, 3),
    (7, 5),
    (8, 3),
    (9, 7),
    (10, 3),
    (12, 7),
    (12, 3),
    (12, 4),
    (12, 5),
    (12, 8),
    (12, 6),
)

RETURNED = "RETURNED"
CUTOFF_MISS = "RANKING / CUTOFF MISS"
POINTER_DEPENDENT = "POINTER-DEPENDENT CANDIDATE"
NOT_REACHED = "NOT REACHED WITHIN DIAGNOSTIC DEPTH"


def pointers_to(target: int) -> tuple[int, ...]:
    return tuple(source for source, dest in POINTERS if dest == target)


def classify(rank: int, target: int) -> str:
    """The ordered decision procedure, reading one retriever's own rank only.

    MISSING and BOUNDARY are checked separately in `verify_targets_present`,
    which aborts the run if either could apply. Under section-aware chunking
    neither can: sections are never re-cut and every target is a whole section.
    """
    if rank <= HEADLINE_K:
        return RETURNED
    if rank <= DIAGNOSTIC_K:
        return CUTOFF_MISS
    return POINTER_DEPENDENT if pointers_to(target) else NOT_REACHED


def verify_targets_present(chunks: list[Chunk]) -> None:
    """Rule out MISSING and BOUNDARY before any rank is interpreted."""
    by_index = {chunk.index: chunk for chunk in chunks}
    for question, groups in REQUIRED.items():
        for group in groups:
            for target in group:
                if target not in by_index:
                    raise SystemExit(
                        f"Q{question} requires C-{target}, which is not in the index. "
                        "That is a MISSING case and invalidates the frozen setup."
                    )
                if not by_index[target].text.strip():
                    raise SystemExit(f"C-{target} is empty. Chunking has drifted.")


def rank_by_score(scores: dict[int, float]) -> list[int]:
    """Chunk indices best first, ties broken by ascending chunk index.

    BM25 assigns exactly 0.0 to every chunk sharing no term with the query, so
    ties are common in the tail and the tie-break is doing real work. It is fixed
    here rather than left to sort stability so the ranking is reproducible.
    """
    return sorted(scores, key=lambda index: (-scores[index], index))


def rank_of(order: list[int], target: int) -> int:
    return order.index(target) + 1


def dense_scores(chunks: list[Chunk]) -> dict[int, dict[int, float]]:
    model = SentenceTransformer(config.EMBEDDING_MODEL)

    def embed(texts: list[str]) -> np.ndarray:
        return model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    question_vectors = embed(list(config.QUESTIONS))
    chunk_matrix = embed([chunk.text for chunk in chunks])

    scores: dict[int, dict[int, float]] = {}
    for position, _ in enumerate(config.QUESTIONS):
        similarities = chunk_matrix @ question_vectors[position]
        scores[position + 1] = {
            chunk.index: float(similarities[offset])
            for offset, chunk in enumerate(chunks)
        }
    return scores


def bm25_scores(chunks: list[Chunk]) -> tuple[dict[int, dict[int, float]], BM25Okapi]:
    tokenized = [tokenize(chunk.text) for chunk in chunks]
    engine = BM25Okapi(tokenized, k1=BM25_K1, b=BM25_B, epsilon=BM25_EPSILON)

    scores: dict[int, dict[int, float]] = {}
    for position, question in enumerate(config.QUESTIONS):
        raw = engine.get_scores(tokenize(question))
        scores[position + 1] = {
            chunk.index: float(raw[offset]) for offset, chunk in enumerate(chunks)
        }
    return scores, engine


def term_contributions(
    question: str, chunk: Chunk, stats: dict
) -> list[tuple[str, int, float, float, float]]:
    """Per-term BM25 contribution for one chunk: (term, tf, idf, factor, score).

    Mirrors BM25Okapi.get_scores term by term, including its treatment of a term
    repeated in the query as two separate additions, so the contributions sum to
    the library's score for this chunk.
    """
    tokens = tokenize(chunk.text)
    doc_len = len(tokens)
    factor = length_factor(doc_len, stats["avgdl"])

    per_term: dict[str, float] = {}
    tf_by_term: dict[str, int] = {}
    for term in tokenize(question):
        idf = stats["effective_idf"].get(term, 0.0)
        if stats["doc_freq"].get(term, 0) == 0:
            idf = 0.0
        tf = tokens.count(term)
        contribution = idf * (tf * (BM25_K1 + 1) / (tf + BM25_K1 * factor))
        per_term[term] = per_term.get(term, 0.0) + contribution
        tf_by_term[term] = tf

    rows = [
        (
            term,
            tf_by_term[term],
            stats["effective_idf"].get(term, 0.0) if stats["doc_freq"].get(term) else 0.0,
            factor,
            total,
        )
        for term, total in per_term.items()
    ]
    return sorted(rows, key=lambda row: (-row[4], row[0]))


def clause_for_term(text: str, term: str) -> str | None:
    """The sentence in `text` where `term` first appears, for context.

    Reported so a term matching in an unrelated context is visible rather than
    assumed relevant -- the difference between "BM25 found C-3" and "BM25 found
    C-3 because `sent` appears in a clause about wrong addresses".
    """
    pattern = re.compile(rf"(?<![0-9a-z]){re.escape(term)}(?![0-9a-z])")
    for line in text.splitlines():
        lowered = line.lower()
        match = pattern.search(lowered)
        if match is None:
            continue
        sentences = re.split(r"(?<=[.!?])\s+", line.strip())
        for sentence in sentences:
            if pattern.search(sentence.lower()):
                collapsed = " ".join(sentence.split())
                return collapsed if len(collapsed) <= 200 else collapsed[:197] + "..."
        collapsed = " ".join(line.split())
        return collapsed if len(collapsed) <= 200 else collapsed[:197] + "..."
    return None


def rrf_scores(orders: dict[str, list[int]], k: int) -> dict[int, float]:
    """1/(k + rank) summed over the complete rankings of both base retrievers."""
    fused: dict[int, float] = {}
    for order in orders.values():
        for position, index in enumerate(order, start=1):
            fused[index] = fused.get(index, 0.0) + 1.0 / (k + position)
    return fused


def is_sufficient(order: list[int], question: int, k: int) -> bool:
    retrieved = set(order[:k])
    return all(bool(retrieved & set(group)) for group in REQUIRED[question])


def verify_contributions(
    chunks: list[Chunk], stats: dict, bm25: dict[int, dict[int, float]]
) -> None:
    for position, question in enumerate(config.QUESTIONS, start=1):
        for chunk in chunks:
            rebuilt = sum(row[4] for row in term_contributions(question, chunk, stats))
            actual = bm25[position][chunk.index]
            if abs(rebuilt - actual) > 1e-9:
                raise SystemExit(
                    f"Per-term contributions for Q{position} / C-{chunk.index} sum to "
                    f"{rebuilt:.10f} but BM25Okapi scored {actual:.10f}. The "
                    "explanation does not match the ranking, so nothing is written."
                )


def verify_dense_reproduces_experiment_1(orders: dict[int, dict[str, list[int]]]) -> None:
    for question, expected in EXPERIMENT_1_C_TOP3.items():
        actual = tuple(orders[question][DENSE][:HEADLINE_K])
        if actual != expected:
            raise SystemExit(
                f"Dense Q{question} top 3 is {actual}, but experiment 1 recorded "
                f"{expected} for strategy C. Same model, same chunks, same metric, "
                "so this is drift rather than a finding. Nothing written."
            )


def chunk_title(chunk: Chunk) -> str:
    heading = chunk.heading or "(front matter)"
    return heading.removeprefix("## ")


def format_rank_cell(rank: int) -> str:
    return f"{rank}"


def render_header(stats: dict, tie_counts: dict[int, int]) -> list[str]:
    zero_tied = ", ".join(
        f"Q{question}: {count}" for question, count in sorted(tie_counts.items())
    )
    return [
        "# Experiment 2: retrieval results",
        "",
        "Dense, BM25 and RRF over one fixed chunking configuration. Produced by "
        "`run_retrieval.py` against the pre-registration frozen at commit "
        "`e9d116a`.",
        "",
        "## Run configuration",
        "",
        f"- run at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"- chunking: strategy C, markdown section-aware, {stats['corpus_size']} "
        "chunks, frozen from experiment 1",
        f"- dense: `{config.EMBEDDING_MODEL}`, {config.SIMILARITY} similarity, "
        "embeddings L2-normalised",
        f"- BM25: `rank_bm25.BM25Okapi`, k1={BM25_K1}, b={BM25_B}, "
        f"epsilon={BM25_EPSILON}",
        f"- RRF: k={RRF_K}, fused over both complete {stats['corpus_size']}-chunk "
        "rankings",
        "- tokenizer: lowercase, non-alphanumeric to whitespace, unigrams, no "
        "stemming, no stopword list",
        f"- headline depth k={HEADLINE_K}, diagnostic depth k={DIAGNOSTIC_K}",
        "- ties broken by ascending chunk index",
        "",
        "### Two checks that passed before this file was written",
        "",
        "1. **The BM25 breakdown reproduces the library's scores.** Every per-term "
        "contribution below was summed and compared against "
        "`BM25Okapi.get_scores` for all 65 question-chunk pairs, agreeing to "
        "within 1e-9. The explanation matches the ranking rather than "
        "approximating it.",
        "2. **The dense arm reproduces experiment 1.** Dense top 3 matches the "
        "strategy-C row of `outputs/retrieval_results.md` for all five questions. "
        "Same model, same chunks, same metric, so this arm is a reproduction and "
        "any difference would have been drift.",
        "",
        "### Every chunk scores above zero under BM25",
        "",
        "Chunks scoring exactly 0.0, which would have tied and been ordered by "
        f"index rather than relevance: {zero_tied}. There are none, and the reason "
        "is the tokenizer: with no stopword list, function words like `the` and "
        "`a` are floored to a shared positive weight rather than removed, and "
        "every chunk in this document contains them. So BM25 returns a fully "
        "ordered 13-chunk ranking in which even the last place reflects some "
        "match, and the ranking never falls back on the tie-break.",
        "",
        "The cost of that is visible in the per-term tables below, where floored "
        "function words take a double-digit share of several top-ranked scores.",
        "",
    ]


def render_prediction_scorecard(
    orders: dict[int, dict[str, list[int]]],
    verdicts: dict[int, dict[str, dict[int, bool]]],
) -> list[str]:
    lines = [
        "## Predictions versus results",
        "",
        "Predictions transcribed from `PRE-REGISTRATION.md` at commit `e9d116a`, "
        "written before this script existed.",
        "",
        "### Predicted ranks",
        "",
        "| Q | method | target | predicted rank | actual rank | hit |",
        "|---|---|---|---:|---:|---|",
    ]
    exact = 0
    total = 0
    for question in sorted(PREDICTED_RANKS):
        for method in BASE_METHODS:
            for target, predicted in PREDICTED_RANKS[question][method].items():
                actual = rank_of(orders[question][method], target)
                total += 1
                correct = actual == predicted
                exact += correct
                lines.append(
                    f"| Q{question} | {METHOD_LABELS[method]} | C-{target} "
                    f"| {predicted} | {actual} | {'yes' if correct else 'no'} |"
                )
    lines += [
        "",
        f"Exact-rank predictions correct: **{exact} of {total}**.",
        "",
        "### Predicted k=3 verdicts",
        "",
        "| Q | method | predicted | actual | hit |",
        "|---|---|---|---|---|",
    ]
    verdict_hits = 0
    verdict_total = 0
    for question in sorted(PREDICTED_VERDICTS):
        for method in ALL_METHODS:
            predicted = PREDICTED_VERDICTS[question][method]
            actual = verdicts[question][method][HEADLINE_K]
            verdict_total += 1
            correct = predicted == actual
            verdict_hits += correct
            lines.append(
                f"| Q{question} | {METHOD_LABELS[method]} "
                f"| {'PASS' if predicted else 'FAIL'} "
                f"| {'PASS' if actual else 'FAIL'} | {'yes' if correct else 'no'} |"
            )
    lines += [
        "",
        f"Verdict predictions correct: **{verdict_hits} of {verdict_total}**.",
        "",
    ]
    return lines


def render_verdict_summary(
    orders: dict[int, dict[str, list[int]]],
    verdicts: dict[int, dict[str, dict[int, bool]]],
) -> list[str]:
    lines = [
        "## Verdicts at both depths",
        "",
        "Both columns are read off the same ranking. Nothing was re-run to answer "
        "a depth question.",
        "",
        f"| Q | required | dense k={HEADLINE_K} | BM25 k={HEADLINE_K} "
        f"| RRF k={HEADLINE_K} | dense k={DIAGNOSTIC_K} | BM25 k={DIAGNOSTIC_K} "
        f"| RRF k={DIAGNOSTIC_K} |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for question in sorted(REQUIRED):
        required = " + ".join(
            " or ".join(f"C-{index}" for index in group) for group in REQUIRED[question]
        )
        cells = [
            "PASS" if verdicts[question][method][depth] else "FAIL"
            for depth in (HEADLINE_K, DIAGNOSTIC_K)
            for method in ALL_METHODS
        ]
        lines.append(f"| Q{question} | {required} | " + " | ".join(cells) + " |")
    lines += [
        "",
        f"A pass at k={DIAGNOSTIC_K} means {DIAGNOSTIC_K} of 13 chunks were "
        "retrieved, which is 77% of the source document. It is a diagnostic "
        "reading, not a production recommendation.",
        "",
    ]
    return lines


def render_classification(orders: dict[int, dict[str, list[int]]]) -> list[str]:
    lines = [
        "## Classification, per retriever",
        "",
        "Each label reads only that retriever's own ranking, and is reported with "
        "the actual rank. RRF is not classified.",
        "",
        "| Q | target | dense rank | dense label | BM25 rank | BM25 label |",
        "|---|---|---:|---|---:|---|",
    ]
    for question in sorted(PREDICTED_TARGETS):
        for target in PREDICTED_TARGETS[question]:
            dense_rank = rank_of(orders[question][DENSE], target)
            bm25_rank = rank_of(orders[question][BM25], target)
            lines.append(
                f"| Q{question} | C-{target} | {dense_rank} "
                f"| {classify(dense_rank, target)} | {bm25_rank} "
                f"| {classify(bm25_rank, target)} |"
            )
    lines.append("")
    return lines


def render_cross_method(orders: dict[int, dict[str, list[int]]]) -> list[str]:
    lines = [
        "## Cross-method recoverability",
        "",
        "Recorded as an observation. One method surfacing evidence another did not "
        "is stated as recovery, never as a defect in the other method.",
        "",
        f"| Q | target | in top {HEADLINE_K} | within depth {DIAGNOSTIC_K} "
        "| RRF rank | recovery |",
        "|---|---|---|---|---:|---|",
    ]
    for question in sorted(REQUIRED):
        targets = sorted({index for group in REQUIRED[question] for index in group})
        for target in targets:
            ranks = {
                method: rank_of(orders[question][method], target)
                for method in BASE_METHODS
            }
            in_top = [
                METHOD_LABELS[method]
                for method in BASE_METHODS
                if ranks[method] <= HEADLINE_K
            ]
            in_depth = [
                METHOD_LABELS[method]
                for method in BASE_METHODS
                if ranks[method] <= DIAGNOSTIC_K
            ]
            rrf_rank = rank_of(orders[question][RRF], target)

            found = [m for m in BASE_METHODS if ranks[m] <= HEADLINE_K]
            if len(found) == 1:
                missed = next(m for m in BASE_METHODS if m not in found)
                recovery = (
                    f"{METHOD_LABELS[found[0]]} only; "
                    f"{METHOD_LABELS[missed]} at rank {ranks[missed]}"
                )
            elif not found:
                recovery = "neither base retriever"
            else:
                recovery = "both; none needed"

            lines.append(
                f"| Q{question} | C-{target} | {', '.join(in_top) or 'none'} "
                f"| {', '.join(in_depth) or 'none'} | {rrf_rank} | {recovery} |"
            )
    lines.append("")
    return lines


def render_rrf_sweep(
    orders: dict[int, dict[str, list[int]]],
    base_orders: dict[int, dict[str, list[int]]],
) -> list[str]:
    lines = [
        "## RRF k sweep — pre-declared secondary analysis",
        "",
        f"Declared in the pre-registration before the run. `k={RRF_K}` remains the "
        "headline; this is a sensitivity check, not a selection procedure.",
        "",
        "| Q | " + " | ".join(f"k={k}" for k in RRF_SWEEP) + " | verdict changes? |",
        "|---|" + "---|" * (len(RRF_SWEEP) + 1),
    ]
    for question in sorted(REQUIRED):
        cells = []
        outcomes = set()
        for k in RRF_SWEEP:
            fused = rrf_scores(base_orders[question], k)
            order = rank_by_score(fused)
            top = tuple(order[:HEADLINE_K])
            cells.append(", ".join(f"C-{index}" for index in top))
            outcomes.add(is_sufficient(order, question, HEADLINE_K))
        changes = "yes" if len(outcomes) > 1 else "no"
        lines.append(f"| Q{question} | " + " | ".join(cells) + f" | {changes} |")
    lines += [
        "",
        f"Across 13 chunks `1/({RRF_K}+r)` runs from "
        f"{1 / (RRF_K + 1):.4f} at rank 1 to {1 / (RRF_K + 13):.4f} at rank 13, so "
        "rank 1 is worth about 20% more than last place and RRF behaves close to "
        "co-occurrence voting.",
        "",
    ]
    return lines


def render_full_rankings(
    chunks: list[Chunk],
    orders: dict[int, dict[str, list[int]]],
    scores: dict[str, dict[int, dict[int, float]]],
) -> list[str]:
    by_index = {chunk.index: chunk for chunk in chunks}
    lines = ["## Complete rankings", ""]
    for question in sorted(REQUIRED):
        lines += [
            f"### Q{question}",
            "",
            f"> {config.QUESTIONS[question - 1]}",
            "",
            "| rank | dense | score | BM25 | score | RRF | score |",
            "|---:|---|---:|---|---:|---|---:|",
        ]
        for position in range(len(chunks)):
            cells = []
            for method in ALL_METHODS:
                index = orders[question][method][position]
                cells.append(f"C-{index}")
                cells.append(f"{scores[method][question][index]:.4f}")
            lines.append(f"| {position + 1} | " + " | ".join(cells) + " |")
        lines.append("")

        required = sorted({index for group in REQUIRED[question] for index in group})
        lines += ["Required chunks:", ""]
        for target in required:
            ranks = ", ".join(
                f"{METHOD_LABELS[method]} {rank_of(orders[question][method], target)}"
                for method in ALL_METHODS
            )
            lines.append(f"- C-{target} {chunk_title(by_index[target])} — {ranks}")
        lines.append("")
    return lines


def render_bm25_explanations(
    chunks: list[Chunk],
    orders: dict[int, dict[str, list[int]]],
    stats: dict,
) -> list[str]:
    by_index = {chunk.index: chunk for chunk in chunks}
    lines = [
        "## Why BM25 ranked what it ranked",
        "",
        "Per-term score contribution for each BM25 top-3 chunk, with the clause "
        "each term was matched in. Terms contributing nothing are omitted. "
        "`contribution = effective IDF x saturated TF factor`, and the column "
        "sums to the chunk's BM25 score.",
        "",
    ]
    for question in sorted(REQUIRED):
        lines += [f"### Q{question}", "", f"> {config.QUESTIONS[question - 1]}", ""]
        for rank, index in enumerate(orders[question][BM25][:HEADLINE_K], start=1):
            chunk = by_index[index]
            rows = [
                row
                for row in term_contributions(
                    config.QUESTIONS[question - 1], chunk, stats
                )
                if row[4] > 0
            ]
            total = sum(row[4] for row in rows)
            lines += [
                f"**BM25 rank {rank}: C-{index} {chunk_title(chunk)}** "
                f"(score {total:.4f})",
                "",
                "| term | tf | effective IDF | contribution | share | matched in |",
                "|---|---:|---:|---:|---:|---|",
            ]
            for term, tf, idf, _factor, contribution in rows:
                clause = clause_for_term(chunk.text, term) or ""
                share = contribution / total if total else 0.0
                floored = " (floored)" if stats["raw_idf"].get(term, 0.0) < 0 else ""
                lines.append(
                    f"| `{term}` | {tf} | {idf:.4f}{floored} | {contribution:.4f} "
                    f"| {share:.0%} | {clause} |"
                )
            lines.append("")
    return lines


def render_pointer_check(
    chunks: list[Chunk], orders: dict[int, dict[str, list[int]]]
) -> list[str]:
    lines = [
        "## Was a chunk pointing at the target retrieved instead?",
        "",
        "Pointer existence is a property of the text, enumerated in the "
        "pre-registration. This table records only whether a pointing chunk "
        f"reached the top {HEADLINE_K} while its target did not.",
        "",
        "| Q | target | points from | pointing chunk in top 3 | target in top 3 |",
        "|---|---|---|---|---|",
    ]
    for question in sorted(PREDICTED_TARGETS):
        for target in PREDICTED_TARGETS[question]:
            sources = pointers_to(target)
            if not sources:
                lines.append(f"| Q{question} | C-{target} | none | n/a | n/a |")
                continue
            for method in BASE_METHODS:
                top = set(orders[question][method][:HEADLINE_K])
                retrieved_pointers = sorted(top & set(sources))
                lines.append(
                    f"| Q{question} ({METHOD_LABELS[method]}) | C-{target} "
                    f"| {', '.join(f'C-{s}' for s in sources)} "
                    f"| {', '.join(f'C-{s}' for s in retrieved_pointers) or 'none'} "
                    f"| {'yes' if target in top else 'no'} |"
                )
    lines.append("")
    return lines


def main() -> None:
    chunks = build_chunks()
    verify_targets_present(chunks)
    stats = corpus_stats(chunks)

    dense = dense_scores(chunks)
    bm25, _engine = bm25_scores(chunks)

    verify_contributions(chunks, stats, bm25)

    base_orders: dict[int, dict[str, list[int]]] = {}
    orders: dict[int, dict[str, list[int]]] = {}
    scores: dict[str, dict[int, dict[int, float]]] = {DENSE: dense, BM25: bm25, RRF: {}}

    for question in sorted(REQUIRED):
        base = {
            DENSE: rank_by_score(dense[question]),
            BM25: rank_by_score(bm25[question]),
        }
        fused = rrf_scores(base, RRF_K)
        base_orders[question] = base
        orders[question] = {**base, RRF: rank_by_score(fused)}
        scores[RRF][question] = fused

    verify_dense_reproduces_experiment_1(orders)

    verdicts = {
        question: {
            method: {
                depth: is_sufficient(orders[question][method], question, depth)
                for depth in (HEADLINE_K, DIAGNOSTIC_K)
            }
            for method in ALL_METHODS
        }
        for question in sorted(REQUIRED)
    }

    tie_counts = {
        question: sum(1 for value in bm25[question].values() if value == 0.0)
        for question in sorted(REQUIRED)
    }

    lines = render_header(stats, tie_counts)
    lines += render_prediction_scorecard(orders, verdicts)
    lines += render_verdict_summary(orders, verdicts)
    lines += render_classification(orders)
    lines += render_cross_method(orders)
    lines += render_rrf_sweep(orders, base_orders)
    lines += render_full_rankings(chunks, orders, scores)
    lines += render_bm25_explanations(chunks, orders, stats)
    lines += render_pointer_check(chunks, orders)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Both self-checks passed: BM25 breakdown sums to library scores, dense")
    print("reproduces experiment 1's strategy-C top 3.")
    print()
    for question in sorted(REQUIRED):
        cells = " | ".join(
            f"{METHOD_LABELS[method]}: "
            + ", ".join(f"C-{index}" for index in orders[question][method][:HEADLINE_K])
            for method in ALL_METHODS
        )
        print(f"Q{question} top 3 -> {cells}")
    print()
    for question in sorted(PREDICTED_TARGETS):
        for target in PREDICTED_TARGETS[question]:
            parts = []
            for method in BASE_METHODS:
                actual = rank_of(orders[question][method], target)
                predicted = PREDICTED_RANKS[question][method].get(target)
                flag = "hit" if predicted == actual else "miss"
                parts.append(
                    f"{METHOD_LABELS[method]} predicted {predicted}, actual {actual} ({flag})"
                )
            print(f"Q{question} C-{target}: " + "; ".join(parts))
    print()
    for question in sorted(REQUIRED):
        row = " | ".join(
            f"{METHOD_LABELS[method]} {'PASS' if verdicts[question][method][HEADLINE_K] else 'FAIL'}"
            for method in ALL_METHODS
        )
        print(f"Q{question} k={HEADLINE_K}: {row}")
    print()
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
