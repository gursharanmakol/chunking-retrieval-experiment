"""Frozen experiment parameters.

Every value in this file is fixed for the article "Why Fixed-Size Chunking
Breaks Retrieval". Nothing here changes between stages or between runs.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Byte-identical copy of the source document. Loaded raw, never rewritten.
SOURCE_DOCUMENT = PROJECT_ROOT / "source" / "technova-billing-cancellation-policy.md"

OUTPUT_DIR = PROJECT_ROOT / "outputs"
CHUNKS_INSPECTION_FILE = OUTPUT_DIR / "chunks_inspection.md"
RETRIEVAL_RESULTS_FILE = OUTPUT_DIR / "retrieval_results.md"

# --- Chunking strategies -------------------------------------------------
# A: fixed-size, no overlap
FIXED_CHUNK_SIZE = 500
FIXED_NO_OVERLAP = 0

# B: fixed-size, with overlap
FIXED_OVERLAP = 100

# C: markdown section-aware -- splits on "## " headings only. Sections are
# left at their natural length and are never re-cut to 500 characters.

STRATEGY_A = "A. Fixed-size, no overlap (500 chars, 0 overlap)"
STRATEGY_B = "B. Fixed-size, with overlap (500 chars, 100 overlap)"
STRATEGY_C = "C. Markdown section-aware (## headings, natural length)"

# --- Retrieval settings (used in stage 2, listed here so they stay frozen) --
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY = "cosine"
TOP_K = 3

# No BM25, no reranking, no contextual retrieval, no LLM answer generation.

# --- Frozen evaluation questions -----------------------------------------
QUESTIONS = [
    "How long can an approved refund take to appear in a customer's account?",
    "How is the restocking fee calculated for a post-shipment cancellation?",
    "A customer cancels after shipment because TechNova sent the wrong item. "
    "Does the 15% restocking fee apply?",
    "What conditions make a post-shipment cancellation eligible for a "
    "restocking-fee waiver?",
    "A customer changes their mind after shipment. Is an inspection required "
    "before the refund is issued?",
]

# --- Frozen sufficiency rubric --------------------------------------------
# One entry per question, in the same order as QUESTIONS. Committed before the
# retrieval run so sufficiency is judged against criteria written without
# knowledge of the results. retrieve.py refuses to run while this is empty or
# while its length does not match QUESTIONS.
#
# retrieve.py never applies these criteria. It copies them into the results
# file and leaves every sufficiency verdict blank for manual review.
SUFFICIENCY_RUBRIC: list[str] = [
    # Q1 -- refund timing
    "Sufficient only if the retrieved set contains the explicit '5-10 business "
    "days' window from Section 6. A set containing only 'refund timing depends "
    "on the payment provider', or only the refund-confirmation-email caveat, "
    "without the number, is insufficient.",
    # Q2 -- restocking fee calculation
    "Sufficient only if the retrieved set contains both the 15% rate and the "
    "base it is applied to: the amount actually paid after any promotional "
    "discount, before tax and shipping charges. Either half alone is "
    "insufficient.",
    # Q3 -- wrong item shipped, does the 15% fee apply
    "Sufficient only if the retrieved set contains both the statement that the "
    "restocking fee does not apply when the order qualifies under Section 3, "
    "and the Section 3 condition 'TechNova shipped the wrong item' (or the "
    "Return Handling Matrix row 'Wrong item shipped by TechNova | Waived'). A "
    "set containing only the bare 15% post-shipment rule is insufficient, "
    "because it supports the wrong answer.",
    # Q4 -- restocking-fee waiver conditions
    "Sufficient only if all four Section 3 waiver conditions appear intact in "
    "the retrieved text: wrong item shipped, product damaged before delivery, "
    "verified TechNova fulfillment error, and cancellation requested before the "
    "order entered shipment processing. A bullet list truncated by a chunk "
    "boundary is insufficient.",
    # Q5 -- inspection after a change of mind
    "Sufficient only if the retrieved set binds the 'customer changes mind "
    "after shipment' scenario to the inspection requirement: the Return "
    "Handling Matrix row together with enough of the table header to identify "
    "the inspection column, or Section 6/7 language tying that scenario to "
    "inspection. A bare table fragment without the header row or without the "
    "scenario label is insufficient, because the column meaning cannot be "
    "determined.",
]

# --- Rubric wording shown to readers -------------------------------------
# SUFFICIENCY_RUBRIC above is left exactly as it was frozen before the run, so
# rerunning retrieve.py still reproduces outputs/retrieval_results.md byte for
# byte. The Q5 entry was reworded afterwards to say plainly that the generic
# Section 6 "may inspect" sentence does not settle the question on its own.
#
# The rewording narrows the criterion and changes no recorded verdict: A passes
# on the matrix row plus the table header, B retrieves no part of the table, and
# C passes on the complete table in C-8. The generic sentence appears only in
# C-6, which C's verdict never depended on.
Q5_RUBRIC_CLARIFIED = (
    "Sufficient only if the retrieved set binds 'customer changes mind after "
    "shipment' to the requirement that the returned product must be inspected, "
    "with enough table or header context to interpret that relationship. Generic "
    "language that TechNova 'may inspect' returned products is insufficient."
)

SUFFICIENCY_RUBRIC_DISPLAY: list[str] = [*SUFFICIENCY_RUBRIC[:4], Q5_RUBRIC_CLARIFIED]

# --- Manually authored verdicts for the published run only ----------------
# Transcribed from the "Manual sufficiency review" table in
# outputs/retrieval_results.md, which was filled in by hand after that run.
# Structured here so the companion UI can display it without parsing markdown.
#
# These apply to the published configurations alone: strategy A (500 chars, 0
# overlap), B (500 chars, 100 overlap) and C (## sections), each at top-k 3.
# No verdict exists for any other parameter combination, and none is inferred.
PUBLISHED_SUFFICIENCY: dict[str, list[str]] = {
    "A": ["sufficient", "sufficient", "insufficient", "sufficient", "sufficient"],
    "B": ["sufficient", "sufficient", "insufficient", "insufficient", "insufficient"],
    "C": ["sufficient", "sufficient", "insufficient", "sufficient", "sufficient"],
}

# One hand-written sentence per published strategy and question, explaining what
# the retrieved evidence did or did not contain. Written by hand from the
# retrieved text, never generated, and shown only for the published
# configurations where a verdict exists.
PUBLISHED_OBSERVATIONS: dict[str, list[str]] = {
    "A": [
        "A-9 contains the '5-10 business days' sentence whole. The fact sits in the "
        "middle of Section 6, far from any boundary, so no cut could damage it.",
        "The rate and the base it applies to sit about 800 characters apart and "
        "landed in different chunks. Both A-10 and A-12 reached the top 3, so the "
        "answer had to be reassembled from two slots.",
        "A-10 breaks off mid-word at 'However, the restoc', cutting the clause that "
        "reverses the answer. The Section 3 condition for a wrong item is in A-3, "
        "which was not retrieved, so the set supports the 15% fee with no sign of "
        "the waiver.",
        "A-3 holds all four waiver conditions intact, because the 500-character cut "
        "landed inside the heading 'Orders Elig|ible for Fee Waiver' rather than "
        "inside the list. A different offset would have split the list.",
        "A-15 carries the 'changes mind' row and A-14 carries the table header. Both "
        "reached the top 3, so the inspection column could be interpreted across "
        "two separate chunks.",
    ],
    "B": [
        "B-11 contains the '5-10 business days' sentence whole. One slot went to "
        "B-27, a 49-character tail fragment, which did not matter here because rank "
        "1 already held the answer.",
        "All three slots landed on one contiguous 1,300-character stretch of Section "
        "7, and that stretch happens to contain both the rate and the base it "
        "applies to.",
        "B-14 states the fee is waived when an order qualifies under Section 3, but "
        "no retrieved chunk contains the Section 3 condition for a wrong item, so "
        "the qualifying fact never arrives.",
        "B-4 holds all four waiver conditions intact but never reached the top 3. "
        "Two of the three slots went to B-13 and B-14, which overlap each other, so "
        "the ranking spent its budget on one region of Section 7.",
        "No retrieved chunk contains any part of the Return Handling Matrix. B-19 "
        "holds the 'changes mind' row and B-18 holds the header, and neither was "
        "retrieved.",
    ],
    "C": [
        "C-6 is the whole of Section 6, so the '5-10 business days' sentence arrives "
        "with the surrounding refund-timing rules.",
        "C-7 is the whole of Section 7, which carries the 15% rate and the base it "
        "applies to in a single chunk.",
        "C-7 states that the fee does not apply when an order qualifies under "
        "Section 3, but Section 3 is C-3, which was not retrieved. The pointer "
        "arrived without the condition it points to.",
        "C-3 is the whole of Section 3, so all four waiver conditions arrive "
        "together with the sentence that introduces them.",
        "C-8 is the whole of Section 8, so the 'changes mind' row arrives with the "
        "table header that labels the inspection column.",
    ],
}

# --- How each published shortfall happened -------------------------------
# Three different things go wrong across this experiment, and the distinctions
# matter more than the verdicts:
#
#   BOUNDARY_CUT     a chunk boundary damaged the evidence itself
#   RANKING_MISS     a chunk that satisfies the rubric survived intact and lost
#                    its top-3 slot to other chunks. Only B/Q4 and B/Q5 qualify,
#                    and both pass under A and C on the same evidence, so ranking
#                    is the only thing that differs
#   CROSS_REFERENCE  the answer needs two distant parts of the document in the
#                    same top-3, and no chunking of this document delivered both.
#                    This is the whole Q3 row, and it is not a ranking miss: no
#                    configuration ever held a sufficient set one slot away
#
# Classified by hand from the frozen Stage 2 review and checked against the chunk
# text. Only shortfalls are listed: any strategy and question missing from this
# table either passed or has no published verdict. Never inferred at runtime.
BOUNDARY_CUT = "boundary cut"
RANKING_MISS = "ranking / top-k"
CROSS_REFERENCE = "cross-reference"

PUBLISHED_FAILURE_MODES: dict[str, dict[int, tuple[str, ...]]] = {
    "A": {2: (BOUNDARY_CUT, CROSS_REFERENCE)},
    "B": {2: (CROSS_REFERENCE,), 3: (RANKING_MISS,), 4: (RANKING_MISS,)},
    "C": {2: (CROSS_REFERENCE,)},
}

MISSED_EVIDENCE_HEADLINE = (
    "Sufficient evidence existed in the index but did not reach the top 3."
)

# The two ranking misses, with the chunk that stayed behind and the top 3 that
# displaced it named explicitly. Hand-written from the same review. Deliberately
# limited to these two cases: nowhere else in the published run did a sufficient
# set sit in the index and lose on ranking alone.
PUBLISHED_MISSED_EVIDENCE: dict[str, dict[int, str]] = {
    "B": {
        3: "The top 3 returned B-13, B-14 and B-6, all Section 7 fee mechanics. A-3 "
        "and C-3 carry the same four conditions and both reached the top 3, so the "
        "evidence was equally intact under all three configurations and only the "
        "ranking differed.",
        4: "The top 3 returned B-6, B-10 and B-26, so no part of the matrix reached "
        "the set. A retrieved it across A-15 and A-14, and C-8 carries it whole, so "
        "here too the evidence survived under all three configurations and only the "
        "ranking differed.",
    },
}

# --- Reviewed evidence spans for the companion UI ----------------------------
# Exact substrings of retrieved chunk text, written by hand from
# PUBLISHED_OBSERVATIONS and checked against the frozen chunk text. Used only
# to highlight what the reviewed Why note already names. Never inferred at
# runtime, never applied to exploratory (non-published) settings.
#
# Shape: strategy letter -> question index -> ((chunk_index, exact_span), ...)
# A missing entry means no highlight for that published cell.
#
# FAIL rows only appear when the observation names a retrieved passage that
# explains the shortfall (e.g. a truncated clause or a pointer without its
# target). Ranking misses that name evidence outside the top-3 are omitted.
_REFUND_WINDOW = (
    "Refunds may take **5\u201310 business days** to appear on the customer\u2019s account."
)
_RATE_15 = "Cancellation after shipment normally incurs a **15% restocking fee**."
_FEE_BASE = (
    "The restocking fee is based on the amount actually paid for the product "
    "after any promotional discount, but before tax and shipping charges."
)
_TRUNCATED_WAIVER = "However, the restoc"
_WAIVER_POINTER = (
    "However, the restocking fee does not apply if the order qualifies under "
    "**Section 3: Orders Eligible for Fee Waiver**."
)
_B14_SECTION3_WAIVER = (
    "If the order qualifies under Section 3:\n\n"
    "- the customer receives a full refund\n"
    "- the 15% restocking fee is waived"
)
_FOUR_CONDITIONS = (
    "- TechNova shipped the wrong item.\n"
    "- The product was damaged before delivery.\n"
    "- The order was cancelled because of a verified TechNova fulfillment error.\n"
    "- The customer requested cancellation before the order entered shipment "
    "processing."
)
_MATRIX_HEADER = (
    "| Return scenario | Restocking fee | Original shipping | Return shipping | "
    "Inspection before refund |"
)
_CHANGES_MIND_ROW = (
    "| Customer changes mind after shipment | 15% | Not refunded | Paid by "
    "customer | Returned product must be inspected |"
)

PUBLISHED_EVIDENCE_SPANS: dict[str, dict[int, tuple[tuple[int, str], ...]]] = {
    "A": {
        0: ((9, _REFUND_WINDOW),),
        1: ((10, _RATE_15), (12, _FEE_BASE)),
        2: ((10, _TRUNCATED_WAIVER),),
        3: ((3, _FOUR_CONDITIONS),),
        4: ((14, _MATRIX_HEADER), (15, _CHANGES_MIND_ROW)),
    },
    "B": {
        0: ((11, _REFUND_WINDOW),),
        1: ((13, _RATE_15), (15, _FEE_BASE)),
        2: ((14, _B14_SECTION3_WAIVER),),
        # Q4/Q5: sufficient evidence was not retrieved — no retrieved span to mark.
    },
    "C": {
        0: ((6, _REFUND_WINDOW),),
        1: ((7, _RATE_15), (7, _FEE_BASE)),
        2: ((7, _WAIVER_POINTER),),
        3: ((3, _FOUR_CONDITIONS),),
        4: ((8, _MATRIX_HEADER), (8, _CHANGES_MIND_ROW)),
    },
}

# Q3 is the one row where every configuration falls short, so a full row of Fail
# is the single place this summary could teach the wrong lesson. The author's line
# on what that row actually shows.
Q3_CROSS_REFERENCE_NOTE = (
    "Q3 is a cross-reference limit that no boundary strategy fixed: the answer "
    "needs the Section 7 rule and the Section 3 condition in the same top 3, and "
    "no chunking of this document delivered both. See the article for why this is "
    "not a chunking failure."
)

# Column headings for the verdict summary, stating each configuration's
# parameters in characters so the strip reads without the sidebar for context.
PUBLISHED_COLUMNS: dict[str, str] = {
    "A": f"A · fixed {FIXED_CHUNK_SIZE}/{FIXED_NO_OVERLAP}",
    "B": f"B · fixed {FIXED_CHUNK_SIZE}/{FIXED_OVERLAP}",
    "C": "C · section-aware",
}

VERDICT_SCOPE_NOTE = (
    "These verdicts apply only to the frozen published experiment: one document, "
    f"one embedding model, {SIMILARITY} similarity, top-k = {TOP_K}."
)
