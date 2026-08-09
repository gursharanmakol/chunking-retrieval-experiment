"""Serialize the frozen published experiment into a static JSON site artifact.

Read-only with respect to experiment logic: chunks come from `chunkers`,
questions/rubrics/verdicts/explanations come from `config`, and cosine scores
are parsed from the already-frozen `outputs/retrieval_results.md`.

No embeddings are recomputed. No experiment parameters are changed.

Run:  python export_site_artifact.py
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import config
from chunkers import fixed_size_chunks, markdown_section_chunks

ARTIFACT_DIR = config.PROJECT_ROOT / "site-artifact"
ARTIFACT_PATH = ARTIFACT_DIR / "chunking-retrieval.json"

# Frozen calendar date for the artifact (not wall-clock) so exports are
# byte-identical across runs.
GENERATED_AT = "2026-08-08"

STRATEGY_META = {
    "A": {
        "label": "Fixed-size",
        "chunk_size_chars": config.FIXED_CHUNK_SIZE,
        "overlap_chars": config.FIXED_NO_OVERLAP,
    },
    "B": {
        "label": "Fixed-size with overlap",
        "chunk_size_chars": config.FIXED_CHUNK_SIZE,
        "overlap_chars": config.FIXED_OVERLAP,
    },
    "C": {
        "label": "Section-aware",
        "rule": "One chunk per Markdown ## section; natural section length",
    },
}

# Match verify_preset.py / retrieval_results.md chunk IDs (1:1 with Chunk.index).
STRATEGY_BUILDERS = {
    "A": lambda raw: fixed_size_chunks(
        raw, "Fixed-size", config.FIXED_CHUNK_SIZE, config.FIXED_NO_OVERLAP
    ),
    "B": lambda raw: fixed_size_chunks(
        raw, "Fixed-size", config.FIXED_CHUNK_SIZE, config.FIXED_OVERLAP
    ),
    "C": lambda raw: markdown_section_chunks(raw, "Markdown section-aware"),
}

def source_sha256(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def parse_frozen_scores(results_md: str) -> dict[tuple[str, int], list[dict]]:
    """Map (strategy_letter, question_index0) -> top-3 hit dicts in rank order."""
    hits: dict[tuple[str, int], list[dict]] = {}
    current: tuple[str, int] | None = None

    for line_match in re.finditer(
        r"### Q(?P<q>\d+) — Strategy (?P<letter>[ABC])\.|"
        r"#### Rank (?P<rank>\d+)\s*\n"
        r"- cosine score: (?P<score>[0-9.]+)\s*\n"
        r"- chunk ID: (?P<chunk_id>[ABC]-\d+)",
        results_md,
    ):
        if line_match.group("q") is not None:
            current = (line_match.group("letter"), int(line_match.group("q")) - 1)
            hits.setdefault(current, [])
            continue
        if current is None:
            raise RuntimeError("cosine hit found before any strategy section header")
        hits[current].append(
            {
                "rank": int(line_match.group("rank")),
                "chunk_id": line_match.group("chunk_id"),
                "cosine": float(line_match.group("score")),
            }
        )

    expected_keys = {(letter, qi) for letter in "ABC" for qi in range(5)}
    if set(hits) != expected_keys:
        missing = sorted(expected_keys - set(hits))
        extra = sorted(set(hits) - expected_keys)
        raise RuntimeError(f"score parse incomplete; missing={missing} extra={extra}")

    for key, rows in hits.items():
        if len(rows) != 3:
            raise RuntimeError(f"{key}: expected 3 hits, got {len(rows)}")
        ranks = [row["rank"] for row in rows]
        if ranks != [1, 2, 3]:
            raise RuntimeError(f"{key}: ranks not 1..3 in order: {ranks}")

    return hits


def verdict_label(raw: str) -> str:
    if raw == "sufficient":
        return "PASS"
    if raw == "insufficient":
        return "FAIL"
    raise ValueError(f"unexpected sufficiency value: {raw!r}")


def build_artifact() -> dict:
    raw_bytes = config.SOURCE_DOCUMENT.read_bytes()
    raw_text = raw_bytes.decode("utf-8")
    sha = source_sha256(raw_bytes)

    results_md = config.RETRIEVAL_RESULTS_FILE.read_text(encoding="utf-8")
    frozen_hits = parse_frozen_scores(results_md)

    chunks_out: list[dict] = []
    chunk_by_id: dict[str, dict] = {}
    for letter, builder in STRATEGY_BUILDERS.items():
        for chunk in builder(raw_text):
            chunk_id = f"{letter}-{chunk.index}"
            entry = {
                "id": chunk_id,
                "strategy": letter,
                "start": chunk.start,
                "end": chunk.end,
                "heading": chunk.heading,
                "text": chunk.text,
            }
            chunks_out.append(entry)
            chunk_by_id[chunk_id] = entry

    questions_out = []
    for index, question in enumerate(config.QUESTIONS):
        questions_out.append(
            {
                "id": f"Q{index + 1}",
                "text": question,
                "rubric": config.SUFFICIENCY_RUBRIC_DISPLAY[index],
            }
        )

    results_out = []
    for letter in "ABC":
        for qi in range(5):
            top = frozen_hits[(letter, qi)]
            for hit in top:
                if hit["chunk_id"] not in chunk_by_id:
                    raise RuntimeError(
                        f"unknown chunk id in frozen results: {hit['chunk_id']}"
                    )
            verdict_raw = config.PUBLISHED_SUFFICIENCY[letter][qi]
            entry = {
                "question_id": f"Q{qi + 1}",
                "strategy": letter,
                "verdict": verdict_label(verdict_raw),
                "explanation": config.PUBLISHED_OBSERVATIONS[letter][qi],
                "top3": [
                    {
                        "rank": hit["rank"],
                        "chunk_id": hit["chunk_id"],
                        "cosine": hit["cosine"],
                    }
                    for hit in top
                ],
            }
            missed = config.PUBLISHED_MISSED_EVIDENCE.get(letter, {}).get(qi)
            if missed:
                entry["missing_evidence"] = {
                    "headline": config.MISSED_EVIDENCE_HEADLINE,
                    "detail": missed,
                }
            results_out.append(entry)

    return {
        "provenance": {
            "source_sha256": sha,
            "embedding_model": config.EMBEDDING_MODEL,
            "top_k": config.TOP_K,
            "similarity": config.SIMILARITY,
            "generated_at": GENERATED_AT,
            "strategies": STRATEGY_META,
        },
        "source": {
            "path": "source/technova-billing-cancellation-policy.md",
            "text": raw_text,
            "char_count": len(raw_text),
        },
        "chunks": chunks_out,
        "questions": questions_out,
        "results": results_out,
    }


def main() -> int:
    artifact = build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    # Deterministic serialization: sorted keys, LF newlines, stable separators.
    payload = json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ARTIFACT_PATH.write_text(payload, encoding="utf-8", newline="\n")

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    print(f"wrote {ARTIFACT_PATH}")
    print(f"json_sha256 {digest}")
    print(f"questions {len(artifact['questions'])}")
    print(f"strategies {len(artifact['provenance']['strategies'])}")
    print(f"results {len(artifact['results'])}")
    print(f"chunks {len(artifact['chunks'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
