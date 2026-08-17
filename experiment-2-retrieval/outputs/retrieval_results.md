# Experiment 2: retrieval results

Dense, BM25 and RRF over one fixed chunking configuration. Produced by `run_retrieval.py` against the pre-registration frozen at commit `e9d116a`.

## Run configuration

- run at: 2026-08-17 04:30:35 UTC
- chunking: strategy C, markdown section-aware, 13 chunks, frozen from experiment 1
- dense: `sentence-transformers/all-MiniLM-L6-v2`, cosine similarity, embeddings L2-normalised
- BM25: `rank_bm25.BM25Okapi`, k1=1.5, b=0.75, epsilon=0.25
- RRF: k=60, fused over both complete 13-chunk rankings
- tokenizer: lowercase, non-alphanumeric to whitespace, unigrams, no stemming, no stopword list
- headline depth k=3, diagnostic depth k=10
- ties broken by ascending chunk index

### Two checks that passed before this file was written

1. **The BM25 breakdown reproduces the library's scores.** Every per-term contribution below was summed and compared against `BM25Okapi.get_scores` for all 65 question-chunk pairs, agreeing to within 1e-9. The explanation matches the ranking rather than approximating it.
2. **The dense arm reproduces experiment 1.** Dense top 3 matches the strategy-C row of `outputs/retrieval_results.md` for all five questions. Same model, same chunks, same metric, so this arm is a reproduction and any difference would have been drift.

### Every chunk scores above zero under BM25

Chunks scoring exactly 0.0, which would have tied and been ordered by index rather than relevance: Q1: 0, Q2: 0, Q3: 0, Q4: 0, Q5: 0. There are none, and the reason is the tokenizer: with no stopword list, function words like `the` and `a` are floored to a shared positive weight rather than removed, and every chunk in this document contains them. So BM25 returns a fully ordered 13-chunk ranking in which even the last place reflects some match, and the ranking never falls back on the tie-break.

The cost of that is visible in the per-term tables below, where floored function words take a double-digit share of several top-ranked scores.

## Predictions versus results

Predictions transcribed from `PRE-REGISTRATION.md` at commit `e9d116a`, written before this script existed.

### Predicted ranks

| Q | method | target | predicted rank | actual rank | hit |
|---|---|---|---:|---:|---|
| Q1 | Dense | C-6 | 1 | 1 | yes |
| Q1 | BM25 | C-6 | 1 | 1 | yes |
| Q2 | Dense | C-7 | 1 | 1 | yes |
| Q2 | BM25 | C-7 | 1 | 1 | yes |
| Q3 | Dense | C-7 | 1 | 1 | yes |
| Q3 | Dense | C-3 | 6 | 5 | no |
| Q3 | BM25 | C-3 | 1 | 1 | yes |
| Q3 | BM25 | C-7 | 3 | 3 | yes |
| Q4 | Dense | C-3 | 2 | 2 | yes |
| Q4 | BM25 | C-3 | 1 | 2 | no |
| Q5 | Dense | C-8 | 2 | 2 | yes |
| Q5 | BM25 | C-8 | 1 | 1 | yes |

Exact-rank predictions correct: **10 of 12**.

### Predicted k=3 verdicts

| Q | method | predicted | actual | hit |
|---|---|---|---|---|
| Q1 | Dense | PASS | PASS | yes |
| Q1 | BM25 | PASS | PASS | yes |
| Q1 | RRF | PASS | PASS | yes |
| Q2 | Dense | PASS | PASS | yes |
| Q2 | BM25 | PASS | PASS | yes |
| Q2 | RRF | PASS | PASS | yes |
| Q3 | Dense | FAIL | FAIL | yes |
| Q3 | BM25 | PASS | PASS | yes |
| Q3 | RRF | PASS | PASS | yes |
| Q4 | Dense | PASS | PASS | yes |
| Q4 | BM25 | PASS | PASS | yes |
| Q4 | RRF | PASS | PASS | yes |
| Q5 | Dense | PASS | PASS | yes |
| Q5 | BM25 | PASS | PASS | yes |
| Q5 | RRF | PASS | PASS | yes |

Verdict predictions correct: **15 of 15**.

## Verdicts at both depths

Both columns are read off the same ranking. Nothing was re-run to answer a depth question.

| Q | required | dense k=3 | BM25 k=3 | RRF k=3 | dense k=10 | BM25 k=10 | RRF k=10 |
|---|---|---|---|---|---|---|---|
| Q1 | C-6 | PASS | PASS | PASS | PASS | PASS | PASS |
| Q2 | C-7 | PASS | PASS | PASS | PASS | PASS | PASS |
| Q3 | C-7 + C-3 or C-8 | FAIL | PASS | PASS | PASS | PASS | PASS |
| Q4 | C-3 | PASS | PASS | PASS | PASS | PASS | PASS |
| Q5 | C-8 | PASS | PASS | PASS | PASS | PASS | PASS |

A pass at k=10 means 10 of 13 chunks were retrieved, which is 77% of the source document. It is a diagnostic reading, not a production recommendation.

## Classification, per retriever

Each label reads only that retriever's own ranking, and is reported with the actual rank. RRF is not classified.

| Q | target | dense rank | dense label | BM25 rank | BM25 label |
|---|---|---:|---|---:|---|
| Q1 | C-6 | 1 | RETURNED | 1 | RETURNED |
| Q2 | C-7 | 1 | RETURNED | 1 | RETURNED |
| Q3 | C-7 | 1 | RETURNED | 3 | RETURNED |
| Q3 | C-3 | 5 | RANKING / CUTOFF MISS | 1 | RETURNED |
| Q4 | C-3 | 2 | RETURNED | 2 | RETURNED |
| Q5 | C-8 | 2 | RETURNED | 1 | RETURNED |

## Cross-method recoverability

Recorded as an observation. One method surfacing evidence another did not is stated as recovery, never as a defect in the other method.

| Q | target | in top 3 | within depth 10 | RRF rank | recovery |
|---|---|---|---|---:|---|
| Q1 | C-6 | Dense, BM25 | Dense, BM25 | 1 | both; none needed |
| Q2 | C-7 | Dense, BM25 | Dense, BM25 | 1 | both; none needed |
| Q3 | C-3 | BM25 | Dense, BM25 | 2 | BM25 only; Dense at rank 5 |
| Q3 | C-7 | Dense, BM25 | Dense, BM25 | 1 | both; none needed |
| Q3 | C-8 | BM25 | Dense, BM25 | 3 | BM25 only; Dense at rank 6 |
| Q4 | C-3 | Dense, BM25 | Dense, BM25 | 2 | both; none needed |
| Q5 | C-8 | Dense, BM25 | Dense, BM25 | 1 | both; none needed |

## RRF k sweep — pre-declared secondary analysis

Declared in the pre-registration before the run. `k=60` remains the headline; this is a sensitivity check, not a selection procedure.

| Q | k=1 | k=10 | k=20 | k=60 | k=100 | k=1000 | verdict changes? |
|---|---|---|---|---|---|---|---|
| Q1 | C-6, C-3, C-2 | C-6, C-2, C-3 | C-6, C-2, C-3 | C-6, C-2, C-3 | C-6, C-2, C-3 | C-6, C-2, C-3 | no |
| Q2 | C-7, C-12, C-4 | C-7, C-12, C-4 | C-7, C-12, C-4 | C-7, C-12, C-4 | C-7, C-12, C-4 | C-7, C-12, C-4 | no |
| Q3 | C-7, C-3, C-8 | C-7, C-3, C-8 | C-7, C-3, C-8 | C-7, C-3, C-8 | C-7, C-3, C-8 | C-7, C-3, C-8 | no |
| Q4 | C-7, C-3, C-5 | C-7, C-3, C-5 | C-7, C-3, C-5 | C-7, C-3, C-5 | C-7, C-3, C-5 | C-7, C-3, C-5 | no |
| Q5 | C-8, C-3, C-4 | C-8, C-3, C-4 | C-8, C-3, C-4 | C-8, C-3, C-4 | C-8, C-3, C-4 | C-8, C-3, C-4 | no |

Across 13 chunks `1/(60+r)` runs from 0.0164 at rank 1 to 0.0137 at rank 13, so rank 1 is worth about 20% more than last place and RRF behaves close to co-occurrence voting.

## Complete rankings

### Q1

> How long can an approved refund take to appear in a customer's account?

| rank | dense | score | BM25 | score | RRF | score |
|---:|---|---:|---|---:|---|---:|
| 1 | C-6 | 0.6168 | C-6 | 13.6932 | C-6 | 0.0328 |
| 2 | C-3 | 0.3016 | C-5 | 5.6333 | C-2 | 0.0315 |
| 3 | C-2 | 0.2844 | C-4 | 3.8379 | C-3 | 0.0311 |
| 4 | C-8 | 0.2823 | C-2 | 3.7614 | C-4 | 0.0308 |
| 5 | C-12 | 0.2785 | C-7 | 3.2132 | C-8 | 0.0308 |
| 6 | C-7 | 0.2710 | C-8 | 2.8378 | C-7 | 0.0305 |
| 7 | C-4 | 0.2658 | C-3 | 2.8162 | C-5 | 0.0300 |
| 8 | C-0 | 0.2521 | C-9 | 2.7649 | C-12 | 0.0293 |
| 9 | C-10 | 0.2491 | C-10 | 1.9696 | C-9 | 0.0290 |
| 10 | C-9 | 0.2458 | C-1 | 1.7470 | C-10 | 0.0290 |
| 11 | C-1 | 0.2074 | C-11 | 1.4711 | C-0 | 0.0284 |
| 12 | C-5 | 0.1792 | C-12 | 1.2998 | C-1 | 0.0284 |
| 13 | C-11 | 0.1613 | C-0 | 0.6199 | C-11 | 0.0278 |

Required chunks:

- C-6 6. Refund Processing — Dense 1, BM25 1, RRF 1

### Q2

> How is the restocking fee calculated for a post-shipment cancellation?

| rank | dense | score | BM25 | score | RRF | score |
|---:|---|---:|---|---:|---|---:|
| 1 | C-7 | 0.7467 | C-7 | 8.2414 | C-7 | 0.0328 |
| 2 | C-12 | 0.5930 | C-12 | 5.7091 | C-12 | 0.0323 |
| 3 | C-4 | 0.5533 | C-5 | 4.7035 | C-4 | 0.0315 |
| 4 | C-10 | 0.5426 | C-4 | 4.5576 | C-5 | 0.0310 |
| 5 | C-9 | 0.4772 | C-3 | 4.5132 | C-10 | 0.0306 |
| 6 | C-5 | 0.4644 | C-8 | 3.9648 | C-3 | 0.0301 |
| 7 | C-8 | 0.4628 | C-10 | 3.5631 | C-8 | 0.0301 |
| 8 | C-3 | 0.4384 | C-6 | 3.5454 | C-9 | 0.0299 |
| 9 | C-2 | 0.4034 | C-9 | 3.5047 | C-6 | 0.0290 |
| 10 | C-6 | 0.3999 | C-11 | 3.1061 | C-2 | 0.0286 |
| 11 | C-1 | 0.3635 | C-2 | 2.9139 | C-11 | 0.0282 |
| 12 | C-11 | 0.3240 | C-1 | 2.8097 | C-1 | 0.0280 |
| 13 | C-0 | 0.3146 | C-0 | 1.2398 | C-0 | 0.0274 |

Required chunks:

- C-7 7. Cancellation After Shipment — Dense 1, BM25 1, RRF 1

### Q3

> A customer cancels after shipment because TechNova sent the wrong item. Does the 15% restocking fee apply?

| rank | dense | score | BM25 | score | RRF | score |
|---:|---|---:|---|---:|---|---:|
| 1 | C-7 | 0.8422 | C-3 | 12.8424 | C-7 | 0.0323 |
| 2 | C-12 | 0.7160 | C-8 | 9.8447 | C-3 | 0.0318 |
| 3 | C-10 | 0.6969 | C-7 | 8.7583 | C-8 | 0.0313 |
| 4 | C-4 | 0.6966 | C-6 | 5.9716 | C-10 | 0.0313 |
| 5 | C-3 | 0.6715 | C-10 | 5.6638 | C-12 | 0.0308 |
| 6 | C-8 | 0.6508 | C-9 | 5.4355 | C-4 | 0.0306 |
| 7 | C-9 | 0.6447 | C-4 | 5.2717 | C-9 | 0.0301 |
| 8 | C-5 | 0.6351 | C-12 | 5.1188 | C-6 | 0.0299 |
| 9 | C-1 | 0.6256 | C-5 | 4.7256 | C-5 | 0.0292 |
| 10 | C-6 | 0.6031 | C-2 | 4.2524 | C-1 | 0.0284 |
| 11 | C-2 | 0.5593 | C-11 | 3.1061 | C-2 | 0.0284 |
| 12 | C-0 | 0.5248 | C-1 | 2.8097 | C-11 | 0.0278 |
| 13 | C-11 | 0.5188 | C-0 | 1.9934 | C-0 | 0.0276 |

Required chunks:

- C-3 3. Orders Eligible for Fee Waiver — Dense 5, BM25 1, RRF 2
- C-7 7. Cancellation After Shipment — Dense 1, BM25 3, RRF 1
- C-8 8. Shipping Charges — Dense 6, BM25 2, RRF 3

### Q4

> What conditions make a post-shipment cancellation eligible for a restocking-fee waiver?

| rank | dense | score | BM25 | score | RRF | score |
|---:|---|---:|---|---:|---|---:|
| 1 | C-7 | 0.7203 | C-7 | 6.6367 | C-7 | 0.0328 |
| 2 | C-3 | 0.6413 | C-3 | 6.2686 | C-3 | 0.0323 |
| 3 | C-5 | 0.6297 | C-5 | 5.9729 | C-5 | 0.0317 |
| 4 | C-12 | 0.6230 | C-12 | 5.5442 | C-12 | 0.0312 |
| 5 | C-4 | 0.5818 | C-10 | 3.9818 | C-4 | 0.0303 |
| 6 | C-9 | 0.5377 | C-8 | 3.9751 | C-10 | 0.0301 |
| 7 | C-8 | 0.5282 | C-4 | 3.8811 | C-8 | 0.0301 |
| 8 | C-10 | 0.5273 | C-6 | 3.7577 | C-9 | 0.0294 |
| 9 | C-1 | 0.4845 | C-11 | 3.5418 | C-6 | 0.0286 |
| 10 | C-2 | 0.4171 | C-9 | 3.4520 | C-1 | 0.0286 |
| 11 | C-11 | 0.4086 | C-1 | 2.9627 | C-11 | 0.0286 |
| 12 | C-6 | 0.3650 | C-2 | 2.1052 | C-2 | 0.0282 |
| 13 | C-0 | 0.3598 | C-0 | 0.6199 | C-0 | 0.0274 |

Required chunks:

- C-3 3. Orders Eligible for Fee Waiver — Dense 2, BM25 2, RRF 2

### Q5

> A customer changes their mind after shipment. Is an inspection required before the refund is issued?

| rank | dense | score | BM25 | score | RRF | score |
|---:|---|---:|---|---:|---|---:|
| 1 | C-3 | 0.4681 | C-8 | 12.8565 | C-8 | 0.0325 |
| 2 | C-8 | 0.4677 | C-7 | 6.1305 | C-3 | 0.0320 |
| 3 | C-6 | 0.4246 | C-4 | 5.6775 | C-4 | 0.0315 |
| 4 | C-4 | 0.4234 | C-3 | 4.9021 | C-6 | 0.0308 |
| 5 | C-12 | 0.4191 | C-5 | 4.8113 | C-7 | 0.0304 |
| 6 | C-1 | 0.3935 | C-10 | 4.7925 | C-5 | 0.0301 |
| 7 | C-2 | 0.3767 | C-6 | 4.7526 | C-12 | 0.0297 |
| 8 | C-5 | 0.3737 | C-2 | 4.3353 | C-2 | 0.0296 |
| 9 | C-11 | 0.3550 | C-11 | 4.0384 | C-1 | 0.0290 |
| 10 | C-7 | 0.3131 | C-12 | 4.0223 | C-10 | 0.0290 |
| 11 | C-9 | 0.2462 | C-9 | 2.6295 | C-11 | 0.0290 |
| 12 | C-10 | 0.2429 | C-1 | 1.7470 | C-9 | 0.0282 |
| 13 | C-0 | 0.2384 | C-0 | 0.6199 | C-0 | 0.0274 |

Required chunks:

- C-8 8. Shipping Charges — Dense 2, BM25 1, RRF 1

## Why BM25 ranked what it ranked

Per-term score contribution for each BM25 top-3 chunk, with the clause each term was matched in. Terms contributing nothing are omitted. `contribution = effective IDF x saturated TF factor`, and the column sums to the chunk's BM25 score.

### Q1

> How long can an approved refund take to appear in a customer's account?

**BM25 rank 1: C-6 6. Refund Processing** (score 13.6932)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `account` | 2 | 2.1203 | 2.9967 | 22% | Refunds may take **5–10 business days** to appear on the customer’s account. |
| `approved` | 2 | 2.1203 | 2.9967 | 22% | Approved refunds are returned to the original payment method. |
| `appear` | 1 | 2.1203 | 2.0888 | 15% | Refunds may take **5–10 business days** to appear on the customer’s account. |
| `take` | 1 | 2.1203 | 2.0888 | 15% | Refunds may take **5–10 business days** to appear on the customer’s account. |
| `refund` | 8 | 0.3844 (floored) | 0.8061 | 6% | Refund Processing |
| `a` | 3 | 0.3844 (floored) | 0.6354 | 5% | TechNova begins refund processing after a cancellation, return, or fee-waiver claim is approved. |
| `s` | 2 | 0.4353 | 0.6153 | 4% | Refunds may take **5–10 business days** to appear on the customer’s account. |
| `customer` | 2 | 0.3844 (floored) | 0.5433 | 4% | Refunds may take **5–10 business days** to appear on the customer’s account. |
| `to` | 2 | 0.3844 (floored) | 0.5433 | 4% | Approved refunds are returned to the original payment method. |
| `in` | 1 | 0.3844 (floored) | 0.3787 | 3% | A refund confirmation email does not mean the funds have already appeared in the customer’s account. |

**BM25 rank 2: C-5 5. Cancellation During Shipment Processing** (score 5.6333)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `can` | 3 | 1.5261 | 2.5747 | 46% | If fulfillment can be stopped successfully: |
| `a` | 3 | 0.3844 (floored) | 0.6486 | 12% | - the customer receives a full refund |
| `s` | 1 | 0.4353 | 0.4450 | 8% | Whether a request can be completed depends on the order’s current status, including picking, packing, carrier-label creation, and carrier handoff. |
| `an` | 1 | 0.3844 (floored) | 0.3930 | 7% | If an order has entered shipment processing but has not yet shipped, TechNova may attempt to stop fulfillment. |
| `customer` | 1 | 0.3844 (floored) | 0.3930 | 7% | - the customer receives a full refund |
| `in` | 1 | 0.3844 (floored) | 0.3930 | 7% | The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3. |
| `refund` | 1 | 0.3844 (floored) | 0.3930 | 7% | - the customer receives a full refund |
| `to` | 1 | 0.3844 (floored) | 0.3930 | 7% | If an order has entered shipment processing but has not yet shipped, TechNova may attempt to stop fulfillment. |

**BM25 rank 3: C-4 4. Cancellation Before Shipment** (score 3.8379)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `a` | 6 | 0.3844 (floored) | 0.7650 | 20% | A customer may cancel an order before shipment without a restocking fee. |
| `an` | 3 | 0.3844 (floored) | 0.6354 | 17% | A customer may cancel an order before shipment without a restocking fee. |
| `customer` | 2 | 0.3844 (floored) | 0.5433 | 14% | A customer may cancel an order before shipment without a restocking fee. |
| `in` | 2 | 0.3844 (floored) | 0.5433 | 14% | A request is received when it appears in the customer’s order record. |
| `to` | 2 | 0.3844 (floored) | 0.5433 | 14% | An order enters shipment processing when TechNova begins picking, packing, labeling, or assigning the order to a carrier. |
| `s` | 1 | 0.4353 | 0.4289 | 11% | A request is received when it appears in the customer’s order record. |
| `refund` | 1 | 0.3844 (floored) | 0.3787 | 10% | If payment has already been captured, TechNova will issue a refund to the original payment method in accordance with Section 6. |

### Q2

> How is the restocking fee calculated for a post-shipment cancellation?

**BM25 rank 1: C-7 7. Cancellation After Shipment** (score 8.2414)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `calculated` | 1 | 2.1203 | 1.6846 | 20% | The restocking fee is calculated using the product price before tax and shipping charges. |
| `post` | 1 | 1.0986 | 0.8729 | 11% | A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. |
| `the` | 18 | 0.3844 (floored) | 0.8586 | 10% | The restocking fee is calculated using the product price before tax and shipping charges. |
| `fee` | 10 | 0.3844 (floored) | 0.7912 | 10% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `is` | 8 | 0.3844 (floored) | 0.7577 | 9% | The restocking fee is calculated using the product price before tax and shipping charges. |
| `restocking` | 8 | 0.3844 (floored) | 0.7577 | 9% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `a` | 6 | 0.3844 (floored) | 0.7078 | 9% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `cancellation` | 4 | 0.3844 (floored) | 0.6254 | 8% | Cancellation After Shipment |
| `for` | 4 | 0.3844 (floored) | 0.6254 | 8% | However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**. |
| `shipment` | 3 | 0.3844 (floored) | 0.5602 | 7% | Cancellation After Shipment |

**BM25 rank 2: C-12 12. Policy Interpretation** (score 5.7091)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `post` | 1 | 1.0986 | 1.1274 | 20% | For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. |
| `the` | 8 | 0.3844 (floored) | 0.8148 | 14% | When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined. |
| `a` | 3 | 0.3844 (floored) | 0.6499 | 11% | When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined. |
| `for` | 3 | 0.3844 (floored) | 0.6499 | 11% | For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. |
| `cancellation` | 2 | 0.3844 (floored) | 0.5594 | 10% | When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined. |
| `fee` | 2 | 0.3844 (floored) | 0.5594 | 10% | For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. |
| `shipment` | 2 | 0.3844 (floored) | 0.5594 | 10% | For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. |
| `is` | 1 | 0.3844 (floored) | 0.3945 | 7% | When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined. |
| `restocking` | 1 | 0.3844 (floored) | 0.3945 | 7% | For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. |

**BM25 rank 3: C-5 5. Cancellation During Shipment Processing** (score 4.7035)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `post` | 1 | 1.0986 | 1.1232 | 24% | - the order is treated as a post-shipment cancellation |
| `the` | 6 | 0.3844 (floored) | 0.7745 | 16% | - the order is cancelled |
| `a` | 3 | 0.3844 (floored) | 0.6486 | 14% | - the customer receives a full refund |
| `shipment` | 3 | 0.3844 (floored) | 0.6486 | 14% | Cancellation During Shipment Processing |
| `cancellation` | 2 | 0.3844 (floored) | 0.5579 | 12% | Cancellation During Shipment Processing |
| `is` | 2 | 0.3844 (floored) | 0.5579 | 12% | - the order is cancelled |
| `fee` | 1 | 0.3844 (floored) | 0.3930 | 8% | The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3. |

### Q3

> A customer cancels after shipment because TechNova sent the wrong item. Does the 15% restocking fee apply?

**BM25 rank 1: C-3 3. Orders Eligible for Fee Waiver** (score 12.8424)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `because` | 2 | 2.1203 | 2.5119 | 20% | - The order was cancelled because of a verified TechNova fulfillment error. |
| `wrong` | 2 | 1.5261 | 1.8079 | 14% | - TechNova shipped the wrong item. |
| `the` | 15 | 0.3844 (floored) | 1.6742 | 13% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `sent` | 1 | 2.1203 | 1.6459 | 13% | A verified TechNova fulfillment error includes an incorrect item, an incorrect quantity, an order sent to the wrong address because of a TechNova processing error, or a failure to ship an in-stock ... |
| `a` | 7 | 0.3844 (floored) | 0.7296 | 6% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `fee` | 7 | 0.3844 (floored) | 0.7296 | 6% | Orders Eligible for Fee Waiver |
| `technova` | 5 | 0.3844 (floored) | 0.6655 | 5% | - TechNova shipped the wrong item. |
| `apply` | 1 | 0.7472 | 0.5801 | 5% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `customer` | 3 | 0.3844 (floored) | 0.5523 | 4% | - The customer requested cancellation before the order entered shipment processing. |
| `item` | 2 | 0.4353 | 0.5157 | 4% | - TechNova shipped the wrong item. |
| `restocking` | 2 | 0.3844 (floored) | 0.4554 | 4% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `after` | 1 | 0.4353 | 0.3379 | 3% | For purposes of this policy, damage before delivery means damage that occurred during packing, handling, or transit and was not caused by the customer after delivery. |
| `does` | 1 | 0.4353 | 0.3379 | 3% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `shipment` | 1 | 0.3844 (floored) | 0.2984 | 2% | - The customer requested cancellation before the order entered shipment processing. |

**BM25 rank 2: C-8 8. Shipping Charges** (score 9.8447)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `wrong` | 2 | 1.5261 | 1.7432 | 18% | - TechNova shipped the wrong product |
| `cancels` | 1 | 2.1203 | 1.5695 | 16% | | Customer cancels before shipment processing | None | Not applicable | Not applicable | No | |
| `the` | 9 | 0.3844 (floored) | 1.5204 | 15% | - TechNova shipped the wrong product |
| `technova` | 10 | 0.3844 (floored) | 0.7764 | 8% | - TechNova shipped the wrong product |
| `shipment` | 5 | 0.3844 (floored) | 0.6513 | 7% | Original shipping charges are generally non-refundable after shipment. |
| `a` | 4 | 0.3844 (floored) | 0.6028 | 6% | Customers are responsible for return-shipping costs unless TechNova confirms that the return resulted from an eligible damage claim, an incorrect shipment, or a verified fulfillment error. |
| `15` | 1 | 0.7472 | 0.5531 | 6% | | Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected | |
| `customer` | 3 | 0.3844 (floored) | 0.5362 | 5% | | Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected | |
| `fee` | 3 | 0.3844 (floored) | 0.5362 | 5% | Shipping-charge eligibility is reviewed separately from restocking-fee eligibility. |
| `restocking` | 3 | 0.3844 (floored) | 0.5362 | 5% | Shipping-charge eligibility is reviewed separately from restocking-fee eligibility. |
| `after` | 2 | 0.4353 | 0.4972 | 5% | Original shipping charges are generally non-refundable after shipment. |
| `item` | 1 | 0.4353 | 0.3222 | 3% | | Wrong item shipped by TechNova | Waived | Refunded | Paid by TechNova | No physical inspection required before refund | |

**BM25 rank 3: C-7 7. Cancellation After Shipment** (score 8.7583)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `the` | 18 | 0.3844 (floored) | 1.7172 | 20% | The restocking fee is calculated using the product price before tax and shipping charges. |
| `15` | 3 | 0.7472 | 1.0889 | 12% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `fee` | 10 | 0.3844 (floored) | 0.7912 | 9% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `restocking` | 8 | 0.3844 (floored) | 0.7577 | 9% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `a` | 6 | 0.3844 (floored) | 0.7078 | 8% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `after` | 3 | 0.4353 | 0.6344 | 7% | Cancellation After Shipment |
| `does` | 3 | 0.4353 | 0.6344 | 7% | However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**. |
| `apply` | 1 | 0.7472 | 0.5937 | 7% | However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**. |
| `shipment` | 3 | 0.3844 (floored) | 0.5602 | 6% | Cancellation After Shipment |
| `customer` | 2 | 0.3844 (floored) | 0.4635 | 5% | - the customer receives a full refund |
| `technova` | 2 | 0.3844 (floored) | 0.4635 | 5% | The customer must return the item according to TechNova’s return instructions. |
| `item` | 1 | 0.4353 | 0.3459 | 4% | The customer must return the item according to TechNova’s return instructions. |

### Q4

> What conditions make a post-shipment cancellation eligible for a restocking-fee waiver?

**BM25 rank 1: C-7 7. Cancellation After Shipment** (score 6.6367)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `a` | 6 | 0.3844 (floored) | 1.4156 | 21% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `post` | 1 | 1.0986 | 0.8729 | 13% | A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. |
| `fee` | 10 | 0.3844 (floored) | 0.7912 | 12% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `restocking` | 8 | 0.3844 (floored) | 0.7577 | 11% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `cancellation` | 4 | 0.3844 (floored) | 0.6254 | 9% | Cancellation After Shipment |
| `for` | 4 | 0.3844 (floored) | 0.6254 | 9% | However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**. |
| `shipment` | 3 | 0.3844 (floored) | 0.5602 | 8% | Cancellation After Shipment |
| `eligible` | 2 | 0.4353 | 0.5249 | 8% | However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**. |
| `waiver` | 2 | 0.3844 (floored) | 0.4635 | 7% | However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**. |

**BM25 rank 2: C-3 3. Orders Eligible for Fee Waiver** (score 6.2686)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `a` | 7 | 0.3844 (floored) | 1.4592 | 23% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `conditions` | 1 | 1.5261 | 1.1847 | 19% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `fee` | 7 | 0.3844 (floored) | 0.7296 | 12% | Orders Eligible for Fee Waiver |
| `waiver` | 4 | 0.3844 (floored) | 0.6180 | 10% | Orders Eligible for Fee Waiver |
| `for` | 3 | 0.3844 (floored) | 0.5523 | 9% | Orders Eligible for Fee Waiver |
| `eligible` | 2 | 0.4353 | 0.5157 | 8% | Orders Eligible for Fee Waiver |
| `cancellation` | 2 | 0.3844 (floored) | 0.4554 | 7% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `restocking` | 2 | 0.3844 (floored) | 0.4554 | 7% | A cancellation fee or restocking fee does not apply when one of the following conditions is met: |
| `shipment` | 1 | 0.3844 (floored) | 0.2984 | 5% | - The customer requested cancellation before the order entered shipment processing. |

**BM25 rank 3: C-5 5. Cancellation During Shipment Processing** (score 5.9729)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `conditions` | 1 | 1.5261 | 1.5602 | 26% | The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3. |
| `a` | 3 | 0.3844 (floored) | 1.2971 | 22% | - the customer receives a full refund |
| `post` | 1 | 1.0986 | 1.1232 | 19% | - the order is treated as a post-shipment cancellation |
| `shipment` | 3 | 0.3844 (floored) | 0.6486 | 11% | Cancellation During Shipment Processing |
| `cancellation` | 2 | 0.3844 (floored) | 0.5579 | 9% | Cancellation During Shipment Processing |
| `fee` | 1 | 0.3844 (floored) | 0.3930 | 7% | The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3. |
| `waiver` | 1 | 0.3844 (floored) | 0.3930 | 7% | The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3. |

### Q5

> A customer changes their mind after shipment. Is an inspection required before the refund is issued?

**BM25 rank 1: C-8 8. Shipping Charges** (score 12.8565)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `inspection` | 2 | 2.1203 | 2.4219 | 19% | | Return scenario | Restocking fee | Original shipping | Return shipping | Inspection before refund | |
| `required` | 2 | 1.5261 | 1.7432 | 14% | | Wrong item shipped by TechNova | Waived | Refunded | Paid by TechNova | No physical inspection required before refund | |
| `changes` | 1 | 2.1203 | 1.5695 | 12% | | Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected | |
| `mind` | 1 | 2.1203 | 1.5695 | 12% | | Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected | |
| `is` | 2 | 0.3844 (floored) | 0.8782 | 7% | Shipping-charge eligibility is reviewed separately from restocking-fee eligibility. |
| `the` | 9 | 0.3844 (floored) | 0.7602 | 6% | - TechNova shipped the wrong product |
| `before` | 5 | 0.3844 (floored) | 0.6513 | 5% | - the product was damaged before delivery |
| `shipment` | 5 | 0.3844 (floored) | 0.6513 | 5% | Original shipping charges are generally non-refundable after shipment. |
| `a` | 4 | 0.3844 (floored) | 0.6028 | 5% | Customers are responsible for return-shipping costs unless TechNova confirms that the return resulted from an eligible damage claim, an incorrect shipment, or a verified fulfillment error. |
| `an` | 3 | 0.3844 (floored) | 0.5362 | 4% | Customers are responsible for return-shipping costs unless TechNova confirms that the return resulted from an eligible damage claim, an incorrect shipment, or a verified fulfillment error. |
| `customer` | 3 | 0.3844 (floored) | 0.5362 | 4% | | Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected | |
| `after` | 2 | 0.4353 | 0.4972 | 4% | Original shipping charges are generally non-refundable after shipment. |
| `refund` | 2 | 0.3844 (floored) | 0.4391 | 3% | | Return scenario | Restocking fee | Original shipping | Return shipping | Inspection before refund | |

**BM25 rank 2: C-7 7. Cancellation After Shipment** (score 6.1305)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `is` | 8 | 0.3844 (floored) | 1.5154 | 25% | The restocking fee is calculated using the product price before tax and shipping charges. |
| `the` | 18 | 0.3844 (floored) | 0.8586 | 14% | The restocking fee is calculated using the product price before tax and shipping charges. |
| `a` | 6 | 0.3844 (floored) | 0.7078 | 12% | Cancellation after shipment normally incurs a **15% restocking fee**. |
| `after` | 3 | 0.4353 | 0.6344 | 10% | Cancellation After Shipment |
| `shipment` | 3 | 0.3844 (floored) | 0.5602 | 9% | Cancellation After Shipment |
| `an` | 2 | 0.3844 (floored) | 0.4635 | 8% | A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. |
| `before` | 2 | 0.3844 (floored) | 0.4635 | 8% | The restocking fee is calculated using the product price before tax and shipping charges. |
| `customer` | 2 | 0.3844 (floored) | 0.4635 | 8% | - the customer receives a full refund |
| `refund` | 2 | 0.3844 (floored) | 0.4635 | 8% | - the customer receives a full refund |

**BM25 rank 3: C-4 4. Cancellation Before Shipment** (score 5.6775)

| term | tf | effective IDF | contribution | share | matched in |
|---|---:|---:|---:|---:|---|
| `is` | 3 | 0.3844 (floored) | 1.2707 | 22% | - the cancellation is accepted |
| `the` | 8 | 0.3844 (floored) | 0.8061 | 14% | If the order has not entered shipment processing: |
| `a` | 6 | 0.3844 (floored) | 0.7650 | 13% | A customer may cancel an order before shipment without a restocking fee. |
| `shipment` | 5 | 0.3844 (floored) | 0.7350 | 13% | Cancellation Before Shipment |
| `an` | 3 | 0.3844 (floored) | 0.6354 | 11% | A customer may cancel an order before shipment without a restocking fee. |
| `before` | 2 | 0.3844 (floored) | 0.5433 | 10% | Cancellation Before Shipment |
| `customer` | 2 | 0.3844 (floored) | 0.5433 | 10% | A customer may cancel an order before shipment without a restocking fee. |
| `refund` | 1 | 0.3844 (floored) | 0.3787 | 7% | If payment has already been captured, TechNova will issue a refund to the original payment method in accordance with Section 6. |

## Was a chunk pointing at the target retrieved instead?

Pointer existence is a property of the text, enumerated in the pre-registration. This table records only whether a pointing chunk reached the top 3 while its target did not.

| Q | target | points from | pointing chunk in top 3 | target in top 3 |
|---|---|---|---|---|
| Q1 (Dense) | C-6 | C-4, C-12 | none | yes |
| Q1 (BM25) | C-6 | C-4, C-12 | C-4 | yes |
| Q2 (Dense) | C-7 | C-5, C-6, C-9, C-12 | C-12 | yes |
| Q2 (BM25) | C-7 | C-5, C-6, C-9, C-12 | C-5, C-12 | yes |
| Q3 (Dense) | C-7 | C-5, C-6, C-9, C-12 | C-12 | yes |
| Q3 (BM25) | C-7 | C-5, C-6, C-9, C-12 | none | yes |
| Q3 (Dense) | C-3 | C-5, C-7, C-8, C-10, C-12 | C-7, C-10, C-12 | no |
| Q3 (BM25) | C-3 | C-5, C-7, C-8, C-10, C-12 | C-7, C-8 | yes |
| Q4 (Dense) | C-3 | C-5, C-7, C-8, C-10, C-12 | C-5, C-7 | yes |
| Q4 (BM25) | C-3 | C-5, C-7, C-8, C-10, C-12 | C-5, C-7 | yes |
| Q5 (Dense) | C-8 | C-3, C-12 | C-3 | yes |
| Q5 (BM25) | C-8 | C-3, C-12 | none | yes |

