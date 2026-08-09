"""Integrity check for the companion UI's "Published experiment" preset.

Rebuilds strategies A, B and C through `explorer_core`, the same module the UI
uses, and compares the chunk counts and top-3 chunk indices against the values
recorded in outputs/retrieval_results.md.

Read-only: writes no files and does not touch the frozen outputs.

Run:  python verify_preset.py
"""

import sys

import config
import explorer_core as core

# Transcribed from outputs/retrieval_results.md. Chunk indices per question, in
# rank order, for each published strategy.
EXPECTED_COUNTS = {"A": 22, "B": 28, "C": 13}
EXPECTED_TOP3 = {
    "A": [[9, 5, 10], [12, 10, 20], [10, 17, 12], [5, 3, 11], [15, 5, 14]],
    "B": [[11, 27, 12], [13, 14, 15], [14, 12, 21], [13, 14, 6], [6, 10, 26]],
    "C": [[6, 3, 2], [7, 12, 4], [7, 12, 10], [7, 3, 5], [3, 8, 6]],
}
EXPECTED_SOURCE_CHARS = 10849


def main() -> int:
    failures: list[str] = []

    source_chars = len(core.load_source())
    if source_chars != EXPECTED_SOURCE_CHARS:
        failures.append(
            f"source document is {source_chars} characters, expected {EXPECTED_SOURCE_CHARS}"
        )
    print(f"source document: {source_chars} characters")

    model = core.load_model()
    question_matrix = core.embed_texts(model, list(config.QUESTIONS))

    for letter, settings in core.PUBLISHED_SETTINGS.items():
        chunks = core.build_chunks(settings)
        matrix = core.embed_texts(model, [chunk.text for chunk in chunks])

        expected_count = EXPECTED_COUNTS[letter]
        count_ok = len(chunks) == expected_count
        if not count_ok:
            failures.append(
                f"{letter}: {len(chunks)} chunks, expected {expected_count}"
            )
        print(
            f"\n{letter}  size={settings.size} overlap={settings.overlap} "
            f"top_k={settings.top_k}  chunks={len(chunks)} "
            f"({'ok' if count_ok else 'MISMATCH'}, expected {expected_count})"
        )

        for index in range(len(config.QUESTIONS)):
            hits = core.top_hits(question_matrix[index], matrix, chunks, 3)
            actual = [chunk.index for chunk, _ in hits]
            expected = EXPECTED_TOP3[letter][index]
            ok = actual == expected
            if not ok:
                failures.append(
                    f"{letter} Q{index + 1}: got {actual}, expected {expected}"
                )
            got = ", ".join(f"{letter}-{position}" for position in actual)
            print(f"  Q{index + 1}: {got}  ({'ok' if ok else 'MISMATCH, expected ' + str(expected)})")

    print()
    if failures:
        print(f"FAILED ({len(failures)} mismatch(es)):")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "PASSED: the Published experiment preset reproduces the chunk counts and "
        "top-3 chunk IDs recorded in outputs/retrieval_results.md."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
