"""Stage 1: build the chunks for strategies A, B and C and write them out for
manual inspection. No embeddings, no retrieval -- this stage only makes the
chunk boundaries visible.

Run:  python inspect_chunks.py
"""

import statistics

import config
from chunkers import Chunk, fixed_size_chunks, markdown_section_chunks

# Chunk text is wrapped in a four-backtick fence so the markdown tables and
# "---" rules inside the source document render as literal text.
FENCE = "````"
PREVIEW_CHARS = 60


def build_all_chunks() -> dict[str, list[Chunk]]:
    raw = config.SOURCE_DOCUMENT.read_text(encoding="utf-8")
    return {
        config.STRATEGY_A: fixed_size_chunks(
            raw, config.STRATEGY_A, config.FIXED_CHUNK_SIZE, config.FIXED_NO_OVERLAP
        ),
        config.STRATEGY_B: fixed_size_chunks(
            raw, config.STRATEGY_B, config.FIXED_CHUNK_SIZE, config.FIXED_OVERLAP
        ),
        config.STRATEGY_C: markdown_section_chunks(raw, config.STRATEGY_C),
    }


def summary_row(strategy: str, chunks: list[Chunk]) -> str:
    counts = [chunk.char_count for chunk in chunks]
    return (
        f"| {strategy} | {len(chunks)} | {min(counts)} | {max(counts)} "
        f"| {round(statistics.mean(counts))} | {sum(counts)} |"
    )


def render_chunk(chunk: Chunk) -> list[str]:
    head = repr(chunk.text[:PREVIEW_CHARS])
    tail = repr(chunk.text[-PREVIEW_CHARS:])
    lines = [
        f"### Chunk {chunk.index}",
        "",
        f"- strategy: {chunk.strategy}",
        f"- chunk index: {chunk.index}",
        f"- character count: {chunk.char_count}",
        f"- source character range: [{chunk.start}:{chunk.end}]",
    ]
    if chunk.heading is not None:
        lines.append(f"- section heading: {chunk.heading}")
    lines += [
        f"- starts with: {head}",
        f"- ends with: {tail}",
        "",
        f"{FENCE}text",
        chunk.text,
        FENCE,
        "",
    ]
    return lines


def render_report(chunk_sets: dict[str, list[Chunk]], raw_length: int) -> str:
    lines = [
        "# Stage 1: chunk inspection",
        "",
        'Source document: `source/technova-billing-cancellation-policy.md` '
        f"({raw_length} characters, loaded raw and unmodified).",
        "",
        "Strategies A and B slice the raw text on character counts only. "
        "Strategy C splits on `## ` headings and leaves each section at its "
        "natural length. Chunk text below is an exact slice of the source, "
        "including leading and trailing whitespace and `---` rules.",
        "",
        "## Totals",
        "",
        "| Strategy | Chunks | Min chars | Max chars | Mean chars | Total chars |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for strategy, chunks in chunk_sets.items():
        lines.append(summary_row(strategy, chunks))
    lines.append("")

    for strategy, chunks in chunk_sets.items():
        lines += [f"## {strategy}", "", f"Total chunks: {len(chunks)}", ""]
        for chunk in chunks:
            lines += render_chunk(chunk)

    return "\n".join(lines) + "\n"


def main() -> None:
    raw_length = len(config.SOURCE_DOCUMENT.read_text(encoding="utf-8"))
    chunk_sets = build_all_chunks()

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.CHUNKS_INSPECTION_FILE.write_text(
        render_report(chunk_sets, raw_length), encoding="utf-8"
    )

    print(f"Source: {config.SOURCE_DOCUMENT} ({raw_length} characters)")
    for strategy, chunks in chunk_sets.items():
        counts = [chunk.char_count for chunk in chunks]
        print(
            f"{strategy}: {len(chunks)} chunks "
            f"(min {min(counts)}, max {max(counts)}, mean {round(statistics.mean(counts))} chars)"
        )
    print(f"Wrote {config.CHUNKS_INSPECTION_FILE}")


if __name__ == "__main__":
    main()
