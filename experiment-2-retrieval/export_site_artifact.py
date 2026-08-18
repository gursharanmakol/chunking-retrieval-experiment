"""Serialize frozen Experiment #2 evidence into a static JSON site artifact.

Read-only: parses already-committed markdown/JSON. Does not import the
retrieval runner, does not load the embedding model, does not run BM25,
and does not recut the source document.

Chunks and source SHA come from Experiment 1's frozen site artifact.
Questions and reader-facing rubrics come from Experiment 1 `config.py`.
Rankings and k=3 verdicts come from `outputs/retrieval_results.md`.

Run:  python experiment-2-retrieval/export_site_artifact.py
"""

from __future__ import annotations

import json
import re
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import config  # noqa: E402

EXPERIMENT_1_ARTIFACT = ROOT / "site-artifact" / "chunking-retrieval.json"
RESULTS_MD = HERE / "outputs" / "retrieval_results.md"
ARTIFACT_DIR = HERE / "site-artifact"
ARTIFACT_PATH = ARTIFACT_DIR / "retrieval-diagnosis.json"

COMMITS = {
    "preregistration": "e9d116a",
    "implementation": "ac7be30",
    "results": "3229255",
}

METHODS = ("dense", "bm25", "rrf")
QUESTION_IDS = tuple(f"Q{i}" for i in range(1, 6))
CHUNK_IDS = tuple(f"C-{i}" for i in range(13))

# Transcribed from run_retrieval.py REQUIRED, frozen at ac7be30.
# Each inner list is an OR-group; every group must be satisfied (AND).
REQUIRED = {
    "Q1": [["C-6"]],
    "Q2": [["C-7"]],
    "Q3": [["C-7"], ["C-3", "C-8"]],
    "Q4": [["C-3"]],
    "Q5": [["C-8"]],
}


def fail(message: str) -> None:
    raise SystemExit(f"export_site_artifact: {message}")


def score(text: str) -> Decimal:
    value = Decimal(text)
    if value.as_tuple().exponent != -4:
        fail(f"score {text!r} is not stored to four decimal places")
    return value


def table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or stripped.startswith("|---") or stripped.startswith("| Q |"):
        return None
    if stripped.startswith("| rank |"):
        return None
    parts = [cell.strip() for cell in stripped.strip("|").split("|")]
    return parts


def parse_results(markdown: str) -> tuple[dict, dict]:
    start = markdown.find("## Complete rankings")
    if start < 0:
        fail("could not find '## Complete rankings' in retrieval_results.md")
    rankings_block = markdown[start:]
    next_heading = re.search(r"\n## [^#]", rankings_block[len("## Complete rankings") :])
    if next_heading:
        rankings_block = rankings_block[: len("## Complete rankings") + next_heading.start()]

    rankings: dict[str, dict[str, list[dict]]] = {
        qid: {method: [] for method in METHODS} for qid in QUESTION_IDS
    }
    current: str | None = None
    for line in rankings_block.splitlines():
        header = re.match(r"^### (Q[1-5])$", line)
        if header:
            current = header.group(1)
            continue
        cells = table_cells(line)
        if not cells or len(cells) != 7:
            continue
        rank_text, dense_id, dense_score, bm25_id, bm25_score, rrf_id, rrf_score = cells
        if not rank_text.isdigit() or not dense_id.startswith("C-"):
            continue
        if current is None:
            fail("ranking row found before a question heading")
        rank = int(rank_text)
        values = {
            "dense": (dense_id, dense_score),
            "bm25": (bm25_id, bm25_score),
            "rrf": (rrf_id, rrf_score),
        }
        for method, (chunk_id, raw_score) in values.items():
            rankings[current][method].append(
                {
                    "rank": rank,
                    "chunk_id": chunk_id,
                    "score": score(raw_score),
                }
            )

    verdicts: dict[str, dict[str, str]] = {}
    for line in markdown.splitlines():
        cells = table_cells(line)
        if not cells or len(cells) != 8:
            continue
        qid, _required, dense, bm25, rrf, dense10, bm2510, rrf10 = cells
        if qid not in QUESTION_IDS:
            continue
        flags = {dense, bm25, rrf, dense10, bm2510, rrf10}
        if flags - {"PASS", "FAIL"}:
            continue
        verdicts[qid] = {"dense": dense, "bm25": bm25, "rrf": rrf}
    if set(verdicts) != set(QUESTION_IDS):
        fail(f"parsed verdicts for {sorted(verdicts)}, expected {list(QUESTION_IDS)}")
    return rankings, verdicts


def parse_classifications(markdown: str) -> dict[tuple[str, str], list[dict]]:
    start = markdown.find("## Classification, per retriever")
    end = markdown.find("## Cross-method recoverability")
    if start < 0 or end < 0:
        fail("could not find classification table in retrieval_results.md")
    out: dict[tuple[str, str], list[dict]] = {}
    for line in markdown[start:end].splitlines():
        cells = table_cells(line)
        if not cells or len(cells) != 6:
            continue
        qid, chunk, dense_rank, dense_label, bm25_rank, bm25_label = cells
        if qid not in QUESTION_IDS or not chunk.startswith("C-"):
            continue
        if not dense_rank.isdigit() or not bm25_rank.isdigit():
            continue
        out.setdefault((qid, "dense"), []).append(
            {"chunk_id": chunk, "rank": int(dense_rank), "label": dense_label}
        )
        out.setdefault((qid, "bm25"), []).append(
            {"chunk_id": chunk, "rank": int(bm25_rank), "label": bm25_label}
        )
    if not out:
        fail("classification table parsed no rows")
    return out


def load_experiment_1_chunks() -> tuple[str, list[dict]]:
    data = json.loads(EXPERIMENT_1_ARTIFACT.read_text(encoding="utf-8"))
    sha = data["provenance"]["source_sha256"]
    chunks = []
    for item in data["chunks"]:
        if item["strategy"] != "C":
            continue
        chunks.append(
            {
                "id": item["id"],
                "heading": item["heading"],
                "start": item["start"],
                "end": item["end"],
                "text": item["text"],
            }
        )
    return sha, chunks


def questions() -> list[dict]:
    texts = list(config.QUESTIONS)
    rubrics = list(config.SUFFICIENCY_RUBRIC_DISPLAY)
    if len(texts) != 5 or len(rubrics) != 5:
        fail("config.py did not yield five questions and five display rubrics")
    return [
        {
            "id": qid,
            "text": texts[i],
            "rubric": rubrics[i],
            "required": REQUIRED[qid],
        }
        for i, qid in enumerate(QUESTION_IDS)
    ]


def methods() -> list[dict]:
    return [
        {
            "id": "dense",
            "label": "Dense",
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "similarity": "cosine",
            "score_kind": "cosine",
        },
        {
            "id": "bm25",
            "label": "BM25",
            "implementation": "rank_bm25.BM25Okapi",
            "k1": 1.5,
            "b": 0.75,
            "epsilon": 0.25,
            "tokenizer": (
                "lowercase; non-alphanumeric characters become whitespace; "
                "unigrams; no stemming; no stopword list; no n-grams"
            ),
            "score_kind": "bm25",
        },
        {
            "id": "rrf",
            "label": "RRF",
            "components": ["dense", "bm25"],
            "k": 60,
            "fusion": "full_13_chunk_rankings",
            "score_kind": "rrf",
        },
    ]


def build_artifact() -> dict:
    rankings, verdicts = parse_results(RESULTS_MD.read_text(encoding="utf-8"))
    classifications = parse_classifications(RESULTS_MD.read_text(encoding="utf-8"))
    source_sha, chunks = load_experiment_1_chunks()

    results = []
    for qid in QUESTION_IDS:
        for method in METHODS:
            entry = {
                "question_id": qid,
                "method": method,
                "verdict": verdicts[qid][method],
                "ranking": rankings[qid][method],
            }
            labels = classifications.get((qid, method))
            if labels:
                entry["classification"] = labels
            results.append(entry)

    return {
        "experiment": {
            "id": "retrieval-diagnosis",
            "name": "Retrieval diagnosis",
            "chunking": "section-aware",
            "chunk_count": 13,
            "question_count": 5,
            "headline_k": 3,
            "source_sha256": source_sha,
            "commits": dict(COMMITS),
        },
        "methods": methods(),
        "questions": questions(),
        "chunks": chunks,
        "results": results,
    }


def ranking_of(artifact: dict, question_id: str, method: str) -> list[dict]:
    for entry in artifact["results"]:
        if entry["question_id"] == question_id and entry["method"] == method:
            return entry["ranking"]
    fail(f"missing result {question_id}/{method}")


def rank_of(ranking: list[dict], chunk_id: str) -> dict:
    for item in ranking:
        if item["chunk_id"] == chunk_id:
            return item
    fail(f"chunk {chunk_id} missing from ranking")


def validate(artifact: dict, experiment_1: dict) -> None:
    if artifact["experiment"]["commits"] != COMMITS:
        fail("provenance commits do not match the frozen evidence SHAs")
    if artifact["experiment"]["source_sha256"] != experiment_1["provenance"]["source_sha256"]:
        fail("source SHA does not match Experiment 1 artifact")
    if len(artifact["questions"]) != 5:
        fail("expected 5 questions")
    if len(artifact["methods"]) != 3:
        fail("expected 3 methods")
    if [m["id"] for m in artifact["methods"]] != list(METHODS):
        fail("methods are not dense, bm25, rrf in that order")
    if len(artifact["chunks"]) != 13:
        fail("expected 13 chunks")
    if [c["id"] for c in artifact["chunks"]] != list(CHUNK_IDS):
        fail("chunk ids are not C-0..C-12 in order")
    if len(artifact["results"]) != 15:
        fail("expected 15 result objects")

    expected_c = {
        item["id"]: item
        for item in experiment_1["chunks"]
        if item["strategy"] == "C"
    }
    for chunk in artifact["chunks"]:
        source = expected_c[chunk["id"]]
        for field in ("heading", "start", "end", "text"):
            if chunk[field] != source[field]:
                fail(f"{chunk['id']} {field} does not match Experiment 1 artifact")

    ranking_rows = 0
    pairs = {(qid, method) for qid in QUESTION_IDS for method in METHODS}
    seen_pairs = set()
    for entry in artifact["results"]:
        key = (entry["question_id"], entry["method"])
        if key in seen_pairs:
            fail(f"duplicate result {key}")
        seen_pairs.add(key)
        ranking = entry["ranking"]
        if len(ranking) != 13:
            fail(f"{key} ranking length is {len(ranking)}, not 13")
        ranks = [item["rank"] for item in ranking]
        if ranks != list(range(1, 14)):
            fail(f"{key} ranks are not 1..13")
        ids = [item["chunk_id"] for item in ranking]
        if len(set(ids)) != 13:
            fail(f"{key} has duplicate chunk ids")
        if set(ids) != set(CHUNK_IDS):
            fail(f"{key} does not contain each C-* chunk exactly once")
        ranking_rows += 13
    if seen_pairs != pairs:
        fail("results do not cover every question/method pair")
    if ranking_rows != 195:
        fail(f"expected 195 ranking rows, got {ranking_rows}")

    q3_dense = ranking_of(artifact, "Q3", "dense")
    q3_bm25 = ranking_of(artifact, "Q3", "bm25")
    q3_rrf = ranking_of(artifact, "Q3", "rrf")
    checks = [
        ("dense", q3_dense, "C-7", 1, Decimal("0.8422")),
        ("dense", q3_dense, "C-10", 3, Decimal("0.6969")),
        ("dense", q3_dense, "C-4", 4, Decimal("0.6966")),
        ("dense", q3_dense, "C-3", 5, Decimal("0.6715")),
        ("dense", q3_dense, "C-8", 6, None),
        ("bm25", q3_bm25, "C-3", 1, None),
        ("bm25", q3_bm25, "C-8", 2, None),
        ("bm25", q3_bm25, "C-7", 3, None),
        ("rrf", q3_rrf, "C-7", 1, None),
        ("rrf", q3_rrf, "C-3", 2, None),
        ("rrf", q3_rrf, "C-8", 3, None),
    ]
    for method, ranking, chunk_id, expected_rank, expected_score in checks:
        item = rank_of(ranking, chunk_id)
        if item["rank"] != expected_rank:
            fail(f"Q3 {method} {chunk_id} rank is {item['rank']}, expected {expected_rank}")
        if expected_score is not None and item["score"] != expected_score:
            fail(
                f"Q3 {method} {chunk_id} score is {item['score']}, expected {expected_score}"
            )

    verdict = {
        (entry["question_id"], entry["method"]): entry["verdict"]
        for entry in artifact["results"]
    }
    if verdict[("Q3", "dense")] != "FAIL":
        fail("Q3 dense verdict is not FAIL")
    if verdict[("Q3", "bm25")] != "PASS":
        fail("Q3 BM25 verdict is not PASS")
    if verdict[("Q3", "rrf")] != "PASS":
        fail("Q3 RRF verdict is not PASS")


def dumps(artifact: dict) -> str:
    """Keep four-decimal scores as written, including trailing zeros."""

    # json.dumps drops trailing zeros on floats (0.0300 -> 0.03). Stash each
    # score as a placeholder string, then restore the four-decimal literal.
    placeholders = {}

    def stash(value):
        if isinstance(value, Decimal):
            token = f"__SCORE_{len(placeholders)}__"
            placeholders[token] = format(value, "f")
            return token
        if isinstance(value, list):
            return [stash(item) for item in value]
        if isinstance(value, dict):
            return {key: stash(item) for key, item in value.items()}
        return value

    text = json.dumps(stash(artifact), indent=2, ensure_ascii=False)
    for token, literal in placeholders.items():
        text = text.replace(f'"{token}"', literal)
    return text + "\n"


def main() -> None:
    if not EXPERIMENT_1_ARTIFACT.is_file():
        fail(f"missing Experiment 1 artifact: {EXPERIMENT_1_ARTIFACT}")
    if not RESULTS_MD.is_file():
        fail(f"missing frozen results: {RESULTS_MD}")

    experiment_1 = json.loads(EXPERIMENT_1_ARTIFACT.read_text(encoding="utf-8"))
    artifact = build_artifact()
    validate(artifact, experiment_1)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(dumps(artifact), encoding="utf-8", newline="\n")

    reloaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    dense = next(
        entry
        for entry in reloaded["results"]
        if entry["question_id"] == "Q3" and entry["method"] == "dense"
    )
    if dense["ranking"][0]["chunk_id"] != "C-7" or dense["ranking"][0]["score"] != 0.8422:
        fail("written JSON failed the Q3 dense C-7 round-trip check")
    print(f"wrote {ARTIFACT_PATH.relative_to(ROOT)}")
    print("validation: PASS")


if __name__ == "__main__":
    main()
