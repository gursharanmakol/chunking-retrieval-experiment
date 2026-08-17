# Experiment 2 — Pre-registration

Retrieval methods over a fixed chunking configuration.

Committed before the first run. Not modified afterward. If anything here turns
out to be wrong, the correction goes in the results write-up, not in this file.

## Why this exists

Experiment 1 classified the Q3 shortfall as a cross-reference limit under all
three chunking configurations, on the grounds that the answer needs Section 7
and Section 3 in the same top 3 and no chunking of this document delivered both.
Under A it additionally recorded boundary damage, where the 500-character cut at
"However, the restoc" truncated the clause that reverses the answer. See
`config.PUBLISHED_FAILURE_MODES`, where A/Q3 carries both tags and B/Q3 and
C/Q3 carry cross-reference alone.

The configuration under test here is C, whose Q3 shortfall experiment 1
attributed to cross-reference and nothing else.

That classification was made with one retrieval method. This experiment asks
whether it survives contact with a second one.

The rules below are written before any retrieval is run so that the answer
cannot be shaped by the result.

## Relationship to experiment 1

Experiment 1's artifacts are frozen and untouched. Nothing in the parent
directory changes: `config.py`, `chunkers.py`, `retrieve.py`, `verify_preset.py`,
`outputs/`, and `site-artifact/` all continue to reproduce the published run
byte for byte.

## Frozen inputs — inherited unchanged from experiment 1

- Source document: `source/technova-billing-cancellation-policy.md`
- The five questions, verbatim from `config.QUESTIONS`
- The five sufficiency rubrics, verbatim from `config.SUFFICIENCY_RUBRIC`
  (Q5 read as `config.Q5_RUBRIC_CLARIFIED`, as published)
- Chunking: markdown section-aware, splitting on `## ` headings only, sections
  left at natural length. 13 chunks, C-0 through C-12, where C-N is Section N
  and C-0 is the title block

Section-aware chunking is the single fixed configuration for all arms. Chunking
is not a variable in this experiment.

## Methods

| # | method | detail |
|---|---|---|
| 1 | Dense | `sentence-transformers/all-MiniLM-L6-v2`, cosine similarity |
| 2 | BM25 | `rank_bm25.BM25Okapi` |
| 3 | RRF | k=60, fused over the **complete** 13-chunk ranking from each base retriever |

RRF fuses full rankings, not truncated top-k lists. Fusing truncated lists would
make it structurally impossible for RRF to surface a chunk that neither base
retriever placed in its top 3, which is the mechanism under test.

## Frozen parameters — no tuning, before or after seeing results

- BM25: `k1=1.5`, `b=0.75`, `epsilon=0.25` (library defaults, stated explicitly
  because `rank_bm25`'s defaults differ from Lucene's `k1=1.2`)
- RRF: `k=60`
- Tokenizer: lowercase, replace every non-alphanumeric character with
  whitespace, split on whitespace, unigrams only. No stemming, no stopword
  list, no n-grams. Punctuation becomes a separator rather than being deleted,
  so `fee-waiver` tokenizes to `fee` + `waiver` and matches a query saying
  "fee waiver"; deleting punctuation would yield `feewaiver`, matching nothing.
  Implemented once in `term_stats.py:tokenize` and reused by the retrieval run.

The tokenizer is an experimental parameter, not an implementation detail. Under
unigram tokenization without stemming, `cancels` and `cancellation` are distinct
terms and `Section 3` becomes `section` + `3`.

### Pre-declared secondary analysis

An RRF `k` sweep, reported regardless of outcome. Reason for declaring it now:
`k=60` was calibrated on TREC lists of roughly 1,000 documents. Across 13
chunks, `1/(60+r)` varies only from 0.0164 at rank 1 to 0.0137 at rank 13, so
rank 1 is worth about 20% more than last place and RRF behaves close to plain
co-occurrence voting. This sweep is a sensitivity check, not a selection
procedure. `k=60` remains the headline.

## Recorded output — per method, per question

- The full ordered 13-chunk ranking with scores
- Rank position of each chunk the rubric requires
- For BM25: document frequency of every query term, and which terms hit the
  negative-IDF floor. At 13 chunks any term appearing in 7 or more chunks is
  floored to a single shared value, so ubiquitous terms become mutually
  indistinguishable
- For BM25, per chunk in the top 3: the **per-term score contribution**
  (`effective IDF x saturated TF factor`) for every query term, so the ranking
  is explained rather than merely reported. "BM25 found C-3" is a result;
  "BM25 found C-3 because `sent` and `because` occur nowhere else in the
  document" is an explanation. Where a driving term is incidental to the
  question rather than a domain term, the write-up says so
- The source clause in the chunk that each high-contribution term came from, so
  a term matching in an unrelated context is visible rather than assumed
  relevant
- Verdicts derived at k=3 (headline, comparable to experiment 1) and k=10
  (diagnostic), from the same run
- Whether a chunk that references the target was itself retrieved at k=3

Nothing is re-run to answer a depth question. Every k is a read-off from the
recorded ranking.

## Reachability — method-local, base retrievers only

Diagnostic depth is **10**, the same depth as the k=10 arm. No new number is
introduced.

> For a given base retriever M, a target chunk is:
>
> | rank under M | status |
> |---|---|
> | 1–3 | RETURNED — inside the headline top 3 |
> | 4–10 | within diagnostic depth but outside the top 3 |
> | 11–13 | not demonstrated reachable by M |

Reachability is a property of **one retriever's own ranking**. It is never
inferred from another retriever's success.

An earlier draft of this document defined reachability globally — a chunk was
"directly reachable" if it made the top 3 of dense *or* BM25 — and then applied
that label per method. That was wrong, and it would have contaminated the
diagnosis across methods. If BM25 ranks C-3 second and dense ranks it eleventh,
the global rule labels dense a ranking failure, which asserts that dense had the
information and ordered it badly. It did not: rank 11 of 13 means dense's
representation barely connects the query to that chunk. BM25 succeeding is not
evidence about dense's internals.

RRF is not classified at all. Its rank for every chunk is recorded, but it does
not receive a failure label and it never establishes reachability. RRF is the
treatment under evaluation; a chunk can reach the RRF top 3 while reaching
neither base retriever's, and that is the designed rescue mechanism rather than
evidence that either base retriever mis-ordered anything.

### A caveat on band width at this corpus size

With 13 chunks the bands are coarse: ranks 1–3 cover 23% of the corpus, ranks
4–10 cover 54%, and ranks 11–13 cover 23%. A chunk at rank 10 is barely better
placed than one at rank 12, yet they fall in different bands.

The label is therefore the coarse reading and **the recorded rank is the precise
quantity**. Every classification in the write-up is reported together with the
actual rank, so "ranking miss at rank 4" and "ranking miss at rank 10" are never
collapsed into the same statement.

## Cross-method recoverability — recorded as a finding, not a diagnosis

Separately from classification, and for each question and each required target
chunk, record:

- which base retrievers placed it in the top 3
- which base retrievers placed it within diagnostic depth
- whether RRF placed it in the final top 3

When one method surfaces evidence another did not, that is stated as recovery,
not as a defect in the other method:

> "BM25 placed C-3 at rank 2; dense placed it at rank 11. BM25 recovered
> evidence dense did not surface within diagnostic depth."

and never as:

> "Dense had a ranking failure, because BM25 proved the chunk was reachable."

Cross-method recovery is arguably the most useful thing this experiment can
report, which is exactly why it must be recorded as an observation rather than
smuggled into the taxonomy.

## Cross-reference table — enumerated before the run

Explicit section pointers in the source document. Pointer existence is a
property of the text, fixed here, and does not depend on what any method
retrieved.

| source | pointer text | target |
|---|---|---|
| C-3 | "return shipping charges are refunded is determined under Section 8" | C-8 |
| C-4 | "issue a refund to the original payment method in accordance with Section 6" | C-6 |
| C-5 | "reviewed under Section 7, including the fee-waiver conditions in Section 3" | C-7, C-3 |
| C-6 | "If a restocking fee applies under Section 7" | C-7 |
| C-7 | "does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**" | C-3 |
| C-7 | "If the order qualifies under Section 3:" | C-3 |
| C-7 | "waived when TechNova confirms that the order is fee-waiver eligible under Section 3" | C-3 |
| C-7 | "could not be stopped under Section 5" | C-5 |
| C-8 | "may qualify for a restocking-fee waiver under Section 3" | C-3 |
| C-9 | "The restocking-fee rules in Section 7 do not apply to subscription cancellations" | C-7 |
| C-10 | "An order that qualifies under Section 3 remains fee-waiver eligible" | C-3 |
| C-12 | "Section 7 sets the normal 15% restocking fee ... must first determine whether the order qualifies under Section 3" | C-7, C-3 |
| C-12 | "Determine whether Section 4, Section 5, or Section 7 applies" | C-4, C-5, C-7 |
| C-12 | "Evaluate whether the order qualifies for a fee waiver under Section 3" | C-3 |
| C-12 | "Review shipping-charge eligibility under Section 8" | C-8 |
| C-12 | "Calculate and issue the refund under Section 6" | C-6 |

C-3 is the most heavily referenced chunk in the document, pointed to from six
distinct sections. C-12 is a pointer hub that names seven sections and states
almost no substantive rule of its own.

## Classification — ordered decision procedure

Evaluated per question, per **base retriever** (dense and BM25). RRF is not
classified. Check in order; the first match is the label. Ordering makes the
categories exhaustive and mutually exclusive, so no outcome can be
unclassifiable and no case can carry two labels.

Every condition below reads only this retriever's own ranking. No condition
consults another retriever's result.

| # | condition | label |
|---|---|---|
| 1 | Target text absent from the index entirely | MISSING |
| 2 | Target text split across chunks so no single chunk satisfies the rubric | BOUNDARY |
| 3 | Target at rank 1–3 under this retriever | RETURNED |
| 4 | Target at rank 4–10 under this retriever | RANKING / CUTOFF MISS |
| 5 | Target at rank 11–13, and a pointer to it exists in the table above | POINTER-DEPENDENT CANDIDATE |
| 6 | Target at rank 11–13, and no pointer to it exists | NOT REACHED WITHIN DIAGNOSTIC DEPTH |

Every label is reported with the actual rank attached, per the band-width
caveat above.

Note that a question can satisfy its rubric only if *all* its required chunks
are RETURNED. Q3 requires two: C-7 plus either C-3 or C-8. A per-chunk label of
RETURNED for one required chunk does not make the question sufficient.

Notes on two of these:

**BOUNDARY** should not arise under section-aware chunking, since sections are
never re-cut. It is retained so the taxonomy stays closed.

**Labels 5 and 6 are observational, not causal.** Both name what was observed
about one retriever's ranking. Neither names a cause, and the wording was changed
to stop them implying one.

**POINTER-DEPENDENT CANDIDATE** records that a target sits outside diagnostic
depth for this retriever while another section of the document explicitly points
to it. Both halves are facts: the rank comes from the recorded ranking, the
pointer comes from the table above.

What it does not record is that the pointer structure *caused* the miss. This
experiment does not test pointer following — no arm of it resolves a reference
and re-retrieves — so it cannot establish that following the pointer would have
helped. The label identifies a plausible next intervention, not a mechanism.

It is also a stricter condition than the earlier global rule produced, which is a
deliberate consequence of the method-local fix. A target at rank 6 with a pointer
aimed at it is RANKING / CUTOFF MISS, because a retriever that ranked the chunk
sixth of thirteen did find semantic or lexical signal in it; the chunk lost a
slot to competitors, which pointer structure does not explain.

**NOT REACHED WITHIN DIAGNOSTIC DEPTH** means only that this retriever placed the
target at rank 11–13 and no pointer to it exists. It does not claim the target is
semantically impossible to retrieve. A different embedding model, a different
query phrasing, or a larger corpus could all change the rank, and none of those
were varied here. The label is a statement about this run, not about the
document.

This category has no counterpart in experiment 1's taxonomy, which recognised
only boundary cuts, ranking misses, and cross-reference limits. It is named in
advance so that if it occurs it is reported as a predicted possibility rather
than a category invented to accommodate a result.

### What may and may not be said about experiment 1

Experiment 1's record stands as history: it described Q3 as cross-reference
limited under configuration C, with one retrieval method and no visibility below
top 3. Experiment 2 may revise that diagnosis, within these limits.

If C-3 lands at rank 4–10 for a retriever, the write-up may say:

> Experiment 1 over-attributed the failure to cross-referencing. With the full
> ranking visible, the retriever had found signal for Section 3, but top-3 cut it
> off.

If C-3 lands at rank 11–13 with a pointer to it, the write-up may **not** say
experiment 2 proved a cross-reference failure. It may say only:

> The result is consistent with a pointer-dependent case, and motivates testing
> explicit reference following in a later experiment.

The difference between those two branches is not rhetorical. The first is a
claim the full ranking supports. The second would require an arm that follows
pointers, which this experiment does not have.

## What was known when the predictions were written

Recorded so the article can state exactly what information was available at the
time, and in what order:

1. `term_stats.py` was run first. It reports corpus statistics only — document
   frequency, IDF, floored terms, token lengths, length-normalisation factors.
   These are BM25 *inputs*, derivable without ranking anything.
2. Predictions below were written with those statistics in hand.
3. Only then was any retrieval run.

Writing predictions in ignorance of the corpus statistics would make them
guesses. Writing them after seeing rankings would make them worthless. Step 2
is the defensible middle, and this note exists so a reader can judge that for
themselves rather than take it on trust.

## Predictions — filled in by hand before the first run

Written by hand with the term statistics in view and no retrieval run. Every rank
below is a **prediction**, not a computed result. No BM25 score, no similarity,
and no ranking was calculated to produce any figure in this section.

The three method predictions do not carry equal weight, and the table marks which
is which:

- **BM25** predictions are informed by recorded corpus statistics — document
  frequency, IDF, and which chunks hold each term. These are BM25 inputs, so the
  predictions are reasoned rather than guessed, though the ranks are still
  predictions.
- **Dense** exact ranks are guesses. There is no inspectable pre-run input for
  the embedding model comparable to a document-frequency table, so the only prior
  is experiment 1's recorded pass/fail. Confidence in *top 3 or not* is moderate;
  confidence in the exact integer is low.
- **RRF** predictions follow from the expected complementarity of the two base
  rankings, so they inherit the uncertainty of both.

### Per question

Classification is now per retriever, so dense and BM25 each get their own
predicted label.

| Q | target chunk(s) | predicted rank: dense | predicted rank: BM25 | predicted label: dense | predicted label: BM25 | predicted cross-method recovery | k=3 verdict: dense / BM25 / RRF | does k=10 change any verdict? |
|---|---|---|---|---|---|---|---|---|
| Q1 | C-6 | 1 (guess, medium confidence) | 1 (high confidence) | RETURNED | RETURNED | None expected | PASS / PASS / PASS | No |
| Q2 | C-7 | 1 (guess, medium confidence) | 1 (high confidence) | RETURNED | RETURNED | None expected | PASS / PASS / PASS | No |
| Q3 | C-7 + C-3 | C-7: 1; C-3: 6 (C-3 low-confidence guess) | C-3: 1; C-7: 3 | C-7: RETURNED; C-3: RANKING / CUTOFF MISS | C-3: RETURNED; C-7: RETURNED | Yes. BM25 is expected to recover C-3 into top 3 while dense leaves C-3 outside top 3 | FAIL / PASS / PASS | Dense: Yes. BM25/RRF: No |
| Q4 | C-3 | 2 (guess, medium confidence) | 1 (moderate-high confidence) | RETURNED | RETURNED | None expected | PASS / PASS / PASS | No |
| Q5 | C-8 | 2 (guess, medium confidence) | 1 (high confidence) | RETURNED | RETURNED | None expected | PASS / PASS / PASS | No |

Grounds for the BM25 column, from the recorded statistics only:

- **Q1 / C-6** — `account`, `appear`, `approved` and `take` are all df=1 and all
  occur only in C-6. Four rare terms converging on one chunk.
- **Q2 / C-7** — `calculated` is df=1 and occurs only in C-7; `post` is df=3 and
  includes C-7. Most remaining query terms are common or floored.
- **Q3 / C-3** — `because` (df=1) and `sent` (df=1) occur only in C-3, and
  `wrong` (df=2) occurs in C-3 and C-8. See the caveat below: part of that signal
  is incidental wording rather than the wrong-item rule.
- **Q4 / C-3** — `conditions` is df=2, in C-3 and C-5; `eligible` includes C-3;
  and C-3 is the substantive fee-waiver section. Weaker convergence than Q1 or
  Q5, hence moderate-high rather than high.
- **Q5 / C-8** — `changes`, `inspection` and `mind` are each df=1 and occur only
  in C-8, and `required` is df=2 including C-8. One rare distractor, `their`,
  occurs only in C-11, but C-8 has several converging signals against its one.

### Q3 in detail

Q3 is the headline. Experiment 1 recorded it as a cross-reference limit under
all three chunking configurations.

- Exact question: "A customer cancels after shipment because TechNova sent the
  wrong item. Does the 15% restocking fee apply?"
- Rubric requires **both** the Section 7 statement that the fee does not apply
  when the order qualifies under Section 3, **and** the Section 3 condition
  "TechNova shipped the wrong item" (or the matrix row "Wrong item shipped by
  TechNova | Waived"). So a sufficient set needs two chunks: C-7 and one of
  C-3 or C-8.

- Predicted rank of C-3 under BM25: **1**
- Predicted rank of C-7 under BM25: **3**
- Predicted rank of C-3 under dense: **6**
- Predicted rank of C-7 under dense: **1**
- Predicted label for C-3 under dense: **RANKING / CUTOFF MISS**
- Predicted label for C-3 under BM25: **RETURNED**
- Prediction for RRF at k=3: **PASS — predicted to return a sufficient set
  containing C-7 plus C-3**

Reasoning, two sentences maximum:

> Dense is expected to rank C-3 below the top 3 but still within diagnostic depth
> because the section contains relevant waiver semantics without strongly matching
> the full query. BM25 is expected to rank C-3 highly because several rare query
> terms, especially `because`, `sent`, and `wrong`, occur there, though some of
> that lexical signal is incidental.

Two things follow from the predicted dense rank of 6, and both are consequences
of rules already fixed above rather than new choices:

- C-3 under dense is predicted **RANKING / CUTOFF MISS**, not
  POINTER-DEPENDENT CANDIDATE, because rank 6 falls inside diagnostic depth. The
  pointer from C-7 to C-3 exists either way; the band decides the label.
- Rank 6 is the weakest figure in this section. Experiment 1 establishes only
  that C-3 was outside dense's top 3 under configuration C; its full ranking was
  never recorded, so any integer from 4 to 13 was available and 6 is a guess
  within that range. If the run puts C-3 at 11–13, the predicted label is wrong
  as well as the predicted rank, and both will be reported as misses.

The RRF prediction rests on the two base predictions being complementary — dense
favouring C-7, BM25 favouring C-3 — so that fusion sees each required chunk
ranked highly by one system. It is a prediction about fusion behaviour, not a
computed fusion result, and it fails if the base rankings turn out to agree with
each other instead.

### Q3: the caveat, declared in advance

If BM25 places C-3 in its top 3, C-3 is lexically reachable and experiment 1's
"cross-reference limit" no longer explains Q3's failure — the evidence was
retrievable by a method experiment 1 did not run. That will be stated plainly
rather than softened.

Note what that does *not* license. Under the method-local rules above, BM25's
success labels BM25 and nothing else; dense's label comes from dense's own rank.
The finding is cross-method recovery, not a retroactive ranking failure charged
to dense.

But the write-up must also report *why* BM25 found it, because the term
statistics show the lexical advantage may not be a clean domain-term win.
Q3's four highest-IDF terms are `because` (df=1), `cancels` (df=1), `sent`
(df=1) and `wrong` (df=2). Of these:

- `wrong` is a legitimate match — it occurs in C-3's target bullet
  "TechNova shipped the wrong item."
- `sent` occurs exactly once in C-3, inside the clause "an order **sent** to the
  **wrong** address **because** of a TechNova processing error". Q3's "sent"
  means dispatched to the customer; C-3's means addressed incorrectly. The token
  matches, the meaning does not.
- `because` occurs twice in C-3 — in that same clause, and in "The order was
  cancelled **because** of a verified TechNova fulfillment error." Neither
  concerns wrong items. It is a conjunction carrying the maximum IDF in this
  corpus solely because the tokenizer has no stopword list.

So the single clause on source line 52 supplies three of Q3's four
highest-IDF terms — `sent`, `wrong`, `because` — while describing wrong
*addresses* rather than wrong *items*. If C-3 ranks first, BM25 will have
reached the right chunk partly for the wrong reason. The per-term contribution breakdown in the recorded
output is what makes this visible, and the write-up will present it rather than
claiming a clean lexical victory.

This does not diminish the finding — a lexical retriever surfacing the chunk a
dense retriever missed is still the result. It changes the claim from "BM25
understands identifiers better" to "BM25 matched incidental tokens that happened
to sit next to the answer," which is both more accurate and more useful to a
reader deciding whether to adopt hybrid retrieval.

### The falsifier

State, before running, the result that would show the hypothesis wrong:

> If **neither** dense **nor** BM25 brings C-3 within the pre-declared
> diagnostic depth of 10, **and** RRF does not produce a sufficient top-3 set for
> Q3 (C-7 plus C-3 or C-8), then the hypothesis that ordinary retrieval or rank
> fusion can resolve Q3 is not supported. Pointer dependence, or simple failure to
> reach the target within the methods and depths tested, becomes the stronger
> explanation.

All three conditions must hold. An earlier draft used a weaker trigger — BM25
failing to place C-3 in its top 3 — and drew a stronger conclusion from it, that
the problem sat upstream of retrieval entirely. Both halves were wrong. BM25
missing the top 3 leaves several live outcomes that the trigger ignored: either
base retriever finding C-3 at rank 4–10, or RRF promoting it into the final top 3
from two mediocre base ranks, which is precisely the mechanism this experiment
exists to test. And "upstream of retrieval" is a claim about the document and the
question, which no ranking can establish; the most this evidence supports is that
these three methods at these depths did not resolve Q3.

Three claims stay off the table even when the falsifier fires, for the same
reason: that the problem sits upstream of retrieval, that semantic retrieval
cannot reach C-3, and that cross-reference structure is the proven cause. None of
them follows from a ranking.

## A note on k=10

10 of 13 chunks is 77% of the source document. A pass at k=10 is not a
production recommendation and will not be presented as one. Rank position is the
finding; the k=10 verdict is a corollary of it. Every reported verdict at k=10
will be accompanied by the fraction of the corpus retrieved.

## Deferred — not part of this experiment

- Cross-encoder reranking. It reorders what retrieval already found, so it
  cannot surface a chunk that never entered the candidate set. Earns a third
  field note only if this experiment shows candidate ordering was the problem.
- Parent-child expansion and reference following. Both need a retrieved child or
  a retrieved pointer to expand from.
- Contextual retrieval / chunk augmentation.
- Any change to chunking.
