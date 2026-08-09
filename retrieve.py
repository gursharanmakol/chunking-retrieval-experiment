"""Stage 2: dense retrieval over the strategy A/B/C chunk sets.

Embeds every chunk and every question with a single model, ranks chunks by
cosine similarity, and writes the top-k hits out verbatim. Retrieval only:
no BM25, no reranking, no contextual retrieval, no LLM answer generation, and
no automatic sufficiency verdict.

Chunks come from the frozen stage 1 chunkers, so nothing about the boundaries
under test is recomputed here.

Run:  python retrieve.py
"""

from datetime import datetime, timezone

import numpy as np
from sentence_transformers import SentenceTransformer

import config
from chunkers import Chunk
from inspect_chunks import build_all_chunks

FENCE = "````"


def require_frozen_rubric() -> list[str]:
    """Refuse to observe any result until the rubric is committed."""
    rubric = config.SUFFICIENCY_RUBRIC
    if len(rubric) != len(config.QUESTIONS) or not all(entry.strip() for entry in rubric):
        raise SystemExit(
            "config.SUFFICIENCY_RUBRIC must hold one non-empty entry per question "
            f"({len(config.QUESTIONS)} expected, {len(rubric)} found). The rubric is "
            "frozen before retrieval runs, so this script will not produce results "
            "until it is filled in."
        )
    return list(rubric)


def strategy_letter(strategy: str) -> str:
    return strategy.split(".", 1)[0]


def chunk_id(chunk: Chunk) -> str:
    return f"{strategy_letter(chunk.strategy)}-{chunk.index}"


def embed(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    """L2-normalize on the way out so a dot product is the cosine similarity."""
    return model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )


def rank_chunks(question_vector: np.ndarray, chunk_matrix: np.ndarray, k: int) -> list[tuple[int, float]]:
    scores = chunk_matrix @ question_vector
    # Stable sort so equal scores always resolve to the lower chunk index.
    order = np.argsort(-scores, kind="stable")[:k]
    return [(int(position), float(scores[position])) for position in order]


def render_run_log(chunk_sets: dict[str, list[Chunk]], raw_length: int) -> list[str]:
    counts = {strategy_letter(name): len(chunks) for name, chunks in chunk_sets.items()}
    return [
        "# Stage 2: retrieval results",
        "",
        "## Run configuration",
        "",
        f"- run at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"- embedding model: `{config.EMBEDDING_MODEL}`",
        f"- similarity metric: {config.SIMILARITY} "
        "(embeddings L2-normalized, so cosine similarity is the dot product)",
        f"- top-k: {config.TOP_K}",
        f"- source document: `source/{config.SOURCE_DOCUMENT.name}` "
        f"({raw_length} characters, loaded raw and unmodified)",
        f"- chunk counts: A = {counts['A']}, B = {counts['B']}, C = {counts['C']}",
        f"- strategy A: fixed size {config.FIXED_CHUNK_SIZE} characters, "
        f"overlap {config.FIXED_NO_OVERLAP}",
        f"- strategy B: fixed size {config.FIXED_CHUNK_SIZE} characters, "
        f"overlap {config.FIXED_OVERLAP}",
        "- strategy C: `## ` heading sections at natural length, no fixed size, no overlap",
        "- excluded: BM25, reranking, contextual retrieval, LLM answer generation",
        "- sufficiency verdicts: none computed, left blank for manual review",
        "",
    ]


def render_rubric(rubric: list[str]) -> list[str]:
    lines = [
        "## Frozen sufficiency rubric",
        "",
        "Committed in `config.py` before this run. Reproduced here so the criteria "
        "sit alongside the results they will be judged against.",
        "",
    ]
    for number, (question, criterion) in enumerate(zip(config.QUESTIONS, rubric), start=1):
        lines += [f"**Q{number}.** {question}", "", f"{criterion}", ""]
    return lines


def render_questions(strategies: list[str]) -> list[str]:
    lines = ["## Questions", ""]
    for number, question in enumerate(config.QUESTIONS, start=1):
        lines.append(f"{number}. {question}")
    lines += ["", "## Summary: retrieved chunk IDs", "", f"Ranks 1 to {config.TOP_K}, best first.", ""]
    header = " | ".join(strategy_letter(name) for name in strategies)
    lines += [f"| Question | {header} |", "|---|" + "---|" * len(strategies)]
    return lines


def render_summary_row(number: int, hits: dict[str, list[tuple[Chunk, float]]], strategies: list[str]) -> str:
    cells = [", ".join(chunk_id(chunk) for chunk, _ in hits[name]) for name in strategies]
    return f"| Q{number} | " + " | ".join(cells) + " |"


def render_manual_review(strategies: list[str]) -> list[str]:
    header = " | ".join(strategy_letter(name) for name in strategies)
    lines = [
        "## Manual sufficiency review",
        "",
        "Deliberately empty. Fill each cell in by hand after reading the retrieved "
        "text below against the matching rubric entry.",
        "",
        f"| Question | {header} |",
        "|---|" + "---|" * len(strategies),
    ]
    for number in range(1, len(config.QUESTIONS) + 1):
        lines.append(f"| Q{number} |" + " |" * len(strategies))
    lines.append("")
    return lines


def render_hit(rank: int, chunk: Chunk, score: float) -> list[str]:
    lines = [
        f"#### Rank {rank}",
        "",
        f"- cosine score: {score:.4f}",
        f"- chunk ID: {chunk_id(chunk)}",
        f"- chunk index: {chunk.index}",
        f"- source character range: [{chunk.start}:{chunk.end}]",
        f"- character count: {chunk.char_count}",
    ]
    if chunk.heading is not None:
        lines.append(f"- section heading: {chunk.heading}")
    lines += ["", f"{FENCE}text", chunk.text, FENCE, ""]
    return lines


def render_details(
    all_hits: dict[int, dict[str, list[tuple[Chunk, float]]]],
    strategies: list[str],
    rubric: list[str],
) -> list[str]:
    lines = ["## Retrieved chunks", ""]
    for number, question in enumerate(config.QUESTIONS, start=1):
        lines += [
            f"## Q{number}",
            "",
            f"**Question {number}:** {question}",
            "",
            f"**Rubric entry (frozen before this run):** {rubric[number - 1]}",
            "",
        ]
        for name in strategies:
            lines += [f"### Q{number} — Strategy {name}", ""]
            for rank, (chunk, score) in enumerate(all_hits[number][name], start=1):
                lines += render_hit(rank, chunk, score)
    return lines


def main() -> None:
    rubric = require_frozen_rubric()

    raw_length = len(config.SOURCE_DOCUMENT.read_text(encoding="utf-8"))
    chunk_sets = build_all_chunks()
    strategies = list(chunk_sets)

    model = SentenceTransformer(config.EMBEDDING_MODEL)
    question_vectors = embed(model, list(config.QUESTIONS))
    chunk_matrices = {
        name: embed(model, [chunk.text for chunk in chunks])
        for name, chunks in chunk_sets.items()
    }

    all_hits: dict[int, dict[str, list[tuple[Chunk, float]]]] = {}
    for index, _ in enumerate(config.QUESTIONS):
        per_strategy: dict[str, list[tuple[Chunk, float]]] = {}
        for name in strategies:
            ranked = rank_chunks(question_vectors[index], chunk_matrices[name], config.TOP_K)
            per_strategy[name] = [(chunk_sets[name][position], score) for position, score in ranked]
        all_hits[index + 1] = per_strategy

    lines = render_run_log(chunk_sets, raw_length)
    lines += render_rubric(rubric)
    lines += render_questions(strategies)
    for number in sorted(all_hits):
        lines.append(render_summary_row(number, all_hits[number], strategies))
    lines.append("")
    lines += render_manual_review(strategies)
    lines += render_details(all_hits, strategies, rubric)

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.RETRIEVAL_RESULTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Model: {config.EMBEDDING_MODEL} | {config.SIMILARITY} | top-k = {config.TOP_K}")
    print(f"Source: {config.SOURCE_DOCUMENT.name} ({raw_length} characters)")
    for name, chunks in chunk_sets.items():
        print(f"{name}: {len(chunks)} chunks embedded")
    for number in sorted(all_hits):
        cells = " | ".join(
            f"{strategy_letter(name)}: " + ", ".join(chunk_id(chunk) for chunk, _ in all_hits[number][name])
            for name in strategies
        )
        print(f"Q{number} -> {cells}")
    print(f"Wrote {config.RETRIEVAL_RESULTS_FILE}")


if __name__ == "__main__":
    main()
