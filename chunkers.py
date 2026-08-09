"""The three chunking strategies, written as plainly as possible.

No framework, no tokenizer, no text cleaning. A chunk's text is always an
exact slice of the raw document, so every boundary in the inspection output
can be traced back to a character offset in the source file.
"""

import re
from dataclasses import dataclass

# Matches a line that starts with exactly two hashes and a space, so "### "
# subsection headings (such as "### Return Handling Matrix") stay inside the
# section they belong to.
SECTION_HEADING = re.compile(r"^## .*$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    strategy: str
    index: int
    text: str
    start: int
    end: int
    heading: str | None = None

    @property
    def char_count(self) -> int:
        return len(self.text)


def fixed_size_chunks(text: str, strategy: str, size: int, overlap: int) -> list[Chunk]:
    """Slide a fixed character window across the raw text.

    Boundaries land wherever the character count runs out, including mid-word
    and mid-table-row. That is the behaviour under test, not a bug to fix.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be >= 0 and smaller than size")

    step = size - overlap
    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(
            Chunk(strategy=strategy, index=len(chunks), text=text[start:end], start=start, end=end)
        )
        start += step
    return chunks


def markdown_section_chunks(text: str, strategy: str) -> list[Chunk]:
    """One chunk per "## " section, heading kept with its own content.

    Anything before the first "## " heading (document title, effective date)
    becomes a leading chunk so no source text is silently dropped.
    """
    headings = list(SECTION_HEADING.finditer(text))
    chunks: list[Chunk] = []

    if not headings:
        return [Chunk(strategy=strategy, index=0, text=text, start=0, end=len(text))]

    preamble_end = headings[0].start()
    if text[:preamble_end].strip():
        chunks.append(
            Chunk(
                strategy=strategy,
                index=0,
                text=text[:preamble_end],
                start=0,
                end=preamble_end,
                heading="(front matter, before first ## heading)",
            )
        )

    for position, heading in enumerate(headings):
        start = heading.start()
        end = headings[position + 1].start() if position + 1 < len(headings) else len(text)
        chunks.append(
            Chunk(
                strategy=strategy,
                index=len(chunks),
                text=text[start:end],
                start=start,
                end=end,
                heading=heading.group(0).strip(),
            )
        )
    return chunks
