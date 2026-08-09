"""Shared logic for the companion UI, with no framework imports.

Everything here delegates to the frozen experiment code: chunks come from
`chunkers`, embedding and ranking come from `retrieve`. Nothing in this module
reimplements a chunker or a similarity function, so a configuration matching the
published experiment produces the published result by construction.

`app.py` and `verify_preset.py` both import this module, so the verification
script exercises exactly the pipeline the UI runs.
"""

import statistics
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

import config
from chunkers import Chunk, fixed_size_chunks, markdown_section_chunks
from retrieve import embed, rank_chunks

FIXED_SIZE = "Fixed-size"
SECTION_AWARE = "Markdown section-aware"

CHUNK_SIZES = (300, 500, 800)
OVERLAP_PERCENTS = (0, 10, 20)
TOP_K_CHOICES = (3, 5)


@dataclass(frozen=True)
class Settings:
    """One point in the parameter space the reader can explore."""

    strategy: str
    size: int
    overlap_percent: int
    top_k: int

    @property
    def overlap(self) -> int:
        """Overlap in characters. Section-aware splitting never overlaps."""
        if self.strategy == SECTION_AWARE:
            return 0
        return round(self.size * self.overlap_percent / 100)

    @property
    def cache_key(self) -> tuple[str, int, int]:
        """Chunking identity only, so top-k changes do not force re-embedding.

        Section-aware ignores size and overlap, so they collapse to zero and
        every section-aware request shares one cache entry.
        """
        if self.strategy == SECTION_AWARE:
            return (self.strategy, 0, 0)
        return (self.strategy, self.size, self.overlap)


# The three configurations behind the published article, rebuilt from the frozen
# constants rather than retyped, so they cannot drift away from config.py.
PUBLISHED_SETTINGS: dict[str, Settings] = {
    "A": Settings(FIXED_SIZE, config.FIXED_CHUNK_SIZE, 0, config.TOP_K),
    "B": Settings(
        FIXED_SIZE,
        config.FIXED_CHUNK_SIZE,
        round(100 * config.FIXED_OVERLAP / config.FIXED_CHUNK_SIZE),
        config.TOP_K,
    ),
    "C": Settings(SECTION_AWARE, config.FIXED_CHUNK_SIZE, 0, config.TOP_K),
}

# Short labels that state the parameters, so a reader who has not memorised the
# article can tell the three configurations apart without hovering.
PUBLISHED_SHORT_LABELS: dict[str, str] = {
    "A": f"A · Fixed {config.FIXED_CHUNK_SIZE} / 0%",
    "B": f"B · Fixed {config.FIXED_CHUNK_SIZE} / "
    f"{round(100 * config.FIXED_OVERLAP / config.FIXED_CHUNK_SIZE)}%",
    "C": "C · Section-aware",
}

PUBLISHED_LABELS: dict[str, str] = {
    "A": f"A — fixed-size, {config.FIXED_CHUNK_SIZE} chars, 0 overlap, top-k {config.TOP_K}",
    "B": f"B — fixed-size, {config.FIXED_CHUNK_SIZE} chars, "
    f"{config.FIXED_OVERLAP} chars overlap, top-k {config.TOP_K}",
    "C": f"C — section-aware, ## sections, top-k {config.TOP_K}",
}

# The percentage control has to be able to express the published overlap exactly,
# otherwise preset B would only approximate the article.
assert PUBLISHED_SETTINGS["B"].overlap == config.FIXED_OVERLAP


def load_source() -> str:
    """The source document, raw and unmodified."""
    return config.SOURCE_DOCUMENT.read_text(encoding="utf-8")


def load_model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBEDDING_MODEL)


def chunks_for(strategy: str, size: int, overlap: int) -> list[Chunk]:
    """Build chunks from an already-resolved character-level configuration.

    Takes the same shape as `Settings.cache_key`, so a caller holding only a
    cache key can rebuild the chunk set without reconstructing a Settings.
    """
    raw = load_source()
    if strategy == SECTION_AWARE:
        return markdown_section_chunks(raw, SECTION_AWARE)
    return fixed_size_chunks(raw, FIXED_SIZE, size, overlap)


def build_chunks(settings: Settings) -> list[Chunk]:
    return chunks_for(settings.strategy, settings.size, settings.overlap)


def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    """Delegates to retrieve.embed, so normalization is identical."""
    return embed(model, texts)


def top_hits(
    question_vector: np.ndarray,
    chunk_matrix: np.ndarray,
    chunks: list[Chunk],
    top_k: int,
) -> list[tuple[Chunk, float]]:
    """Delegates to retrieve.rank_chunks, so tie-breaking is identical."""
    ranked = rank_chunks(question_vector, chunk_matrix, top_k)
    return [(chunks[position], score) for position, score in ranked]


def match_published(settings: Settings) -> str | None:
    """Return 'A', 'B' or 'C' when the settings reproduce a published run.

    Compared on effective chunking identity rather than on the raw control
    values, so section-aware still matches C whatever the size and overlap
    controls happen to hold while they are disabled.
    """
    identity = (settings.cache_key, settings.top_k)
    for letter, published in PUBLISHED_SETTINGS.items():
        if (published.cache_key, published.top_k) == identity:
            return letter
    return None


def chunk_stats(chunks: list[Chunk]) -> dict[str, int]:
    counts = [chunk.char_count for chunk in chunks]
    return {
        "count": len(chunks),
        "min": min(counts),
        "max": max(counts),
        "mean": round(statistics.mean(counts)),
        "indexed": sum(counts),
    }


def unique_coverage(chunks: list[Chunk]) -> tuple[int, int]:
    """(unique source characters, total characters) across a set of chunks.

    The two differ when retrieved chunks overlap each other, which is how many
    of the top-k slots resolve to distinct text rather than repeated text.
    """
    total = sum(chunk.char_count for chunk in chunks)
    unique = 0
    cursor = -1
    for chunk in sorted(chunks, key=lambda item: item.start):
        start = max(chunk.start, cursor)
        if chunk.end > start:
            unique += chunk.end - start
            cursor = chunk.end
    return unique, total


def cut_mid_word(raw: str, chunk: Chunk) -> tuple[bool, bool]:
    """Whether the chunk's start and end boundaries fall inside a word.

    Reported as a plain fact about the boundary, so a reader can see that a
    chunk may rank well while beginning or ending mid-sentence.
    """
    starts_inside = (
        chunk.start > 0
        and not raw[chunk.start - 1].isspace()
        and bool(chunk.text) and not chunk.text[0].isspace()
    )
    ends_inside = (
        chunk.end < len(raw)
        and not raw[chunk.end].isspace()
        and bool(chunk.text) and not chunk.text[-1].isspace()
    )
    return starts_inside, ends_inside
