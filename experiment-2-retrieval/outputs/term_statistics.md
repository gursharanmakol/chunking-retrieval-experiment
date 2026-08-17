# Experiment 2, step 0: BM25 term statistics

Corpus statistics only. No ranking, no retrieval, no verdicts.

Chunking: markdown section-aware (`## ` headings), frozen from experiment 1. Tokenizer: lowercase, punctuation to whitespace, unigrams, no stemming.

BM25 parameters: `k1=1.5`, `b=0.75`, `epsilon=0.25` (rank_bm25 BM25Okapi defaults).

## Corpus

- chunks: 13
- vocabulary: 407 distinct terms
- total tokens: 1585
- average chunk length (avgdl): 121.9 tokens
- average IDF across the vocabulary: 1.5376
- negative-IDF floor (epsilon x average IDF): 0.3844

A term's IDF goes negative once it appears in more than half the chunks, so any term in 7 or more of 13 chunks is floored to 0.3844 and becomes indistinguishable from every other floored term.

| chunk | tokens | dl / avgdl | length factor | effect |
|---|---:|---:|---:|---|
| C-0 (front matter, before first ## heading) | 19 | 0.16 | 0.367 | boosted |
| C-1 1. Purpose | 47 | 0.39 | 0.539 | boosted |
| C-2 2. Payment Terms | 143 | 1.17 | 1.130 | penalised |
| C-3 3. Orders Eligible for Fee Waiver | 200 | 1.64 | 1.480 | penalised |
| C-4 4. Cancellation Before Shipment | 126 | 1.03 | 1.025 | penalised |
| C-5 5. Cancellation During Shipment Processing | 116 | 0.95 | 0.964 | boosted |
| C-6 6. Refund Processing | 126 | 1.03 | 1.025 | penalised |
| C-7 7. Cancellation After Shipment | 192 | 1.57 | 1.431 | penalised |
| C-8 8. Shipping Charges | 217 | 1.78 | 1.585 | penalised |
| C-9 9. Subscription Cancellation | 89 | 0.73 | 0.797 | boosted |
| C-10 10. Promotional Orders | 105 | 0.86 | 0.896 | boosted |
| C-11 11. Business Orders | 90 | 0.74 | 0.804 | boosted |
| C-12 12. Policy Interpretation | 115 | 0.94 | 0.957 | boosted |

## Terms floored across the whole corpus

30 of 407 vocabulary terms have negative raw IDF and are floored. Each contributes the same weight regardless of how common it actually is.

| term | document frequency | raw IDF |
|---|---:|---:|
| `technova` | 13 | -3.2958 |
| `the` | 13 | -3.2958 |
| `a` | 12 | -2.1203 |
| `to` | 12 | -2.1203 |
| `and` | 10 | -1.0986 |
| `cancellation` | 10 | -1.0986 |
| `fee` | 10 | -1.0986 |
| `for` | 10 | -1.0986 |
| `or` | 10 | -1.0986 |
| `order` | 10 | -1.0986 |
| `refund` | 10 | -1.0986 |
| `restocking` | 10 | -1.0986 |
| `applies` | 9 | -0.7472 |
| `be` | 9 | -0.7472 |
| `if` | 9 | -0.7472 |
| `is` | 9 | -0.7472 |
| `may` | 9 | -0.7472 |
| `not` | 9 | -0.7472 |
| `section` | 9 | -0.7472 |
| `an` | 8 | -0.4353 |
| `product` | 8 | -0.4353 |
| `waiver` | 8 | -0.4353 |
| `before` | 7 | -0.1431 |
| `customer` | 7 | -0.1431 |
| `in` | 7 | -0.1431 |
| `request` | 7 | -0.1431 |
| `shipment` | 7 | -0.1431 |
| `that` | 7 | -0.1431 |
| `under` | 7 | -0.1431 |
| `when` | 7 | -0.1431 |

## Q1

> How long can an approved refund take to appear in a customer's account?

Tokenized to 14 tokens, 14 distinct.

| term | df | raw IDF | effective IDF | floored | chunks containing it |
|---|---:|---:|---:|---|---|
| `account` | 1 | 2.1203 | 2.1203 |  | C-6 |
| `appear` | 1 | 2.1203 | 2.1203 |  | C-6 |
| `approved` | 1 | 2.1203 | 2.1203 |  | C-6 |
| `take` | 1 | 2.1203 | 2.1203 |  | C-6 |
| `can` | 2 | 1.5261 | 1.5261 |  | C-2, C-5 |
| `s` | 5 | 0.4353 | 0.4353 |  | C-2, C-4, C-5, C-6, C-7 |
| `a` | 12 | -2.1203 | 0.3844 | yes | C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `an` | 8 | -0.4353 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-7, C-8, C-9, C-10 |
| `customer` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-6, C-7, C-8 |
| `in` | 7 | -0.1431 | 0.3844 | yes | C-3, C-4, C-5, C-6, C-7, C-8, C-9 |
| `refund` | 10 | -1.0986 | 0.3844 | yes | C-1, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `to` | 12 | -2.1203 | 0.3844 | yes | C-0, C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11 |

Query terms absent from the corpus, contributing nothing: `how`, `long`

## Q2

> How is the restocking fee calculated for a post-shipment cancellation?

Tokenized to 11 tokens, 11 distinct.

| term | df | raw IDF | effective IDF | floored | chunks containing it |
|---|---:|---:|---:|---|---|
| `calculated` | 1 | 2.1203 | 2.1203 |  | C-7 |
| `post` | 3 | 1.0986 | 1.0986 |  | C-5, C-7, C-12 |
| `a` | 12 | -2.1203 | 0.3844 | yes | C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `cancellation` | 10 | -1.0986 | 0.3844 | yes | C-0, C-1, C-3, C-4, C-5, C-6, C-7, C-9, C-11, C-12 |
| `fee` | 10 | -1.0986 | 0.3844 | yes | C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `for` | 10 | -1.0986 | 0.3844 | yes | C-1, C-2, C-3, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `is` | 9 | -0.7472 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-10, C-12 |
| `restocking` | 10 | -1.0986 | 0.3844 | yes | C-1, C-3, C-4, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `shipment` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-7, C-8, C-12 |
| `the` | 13 | -3.2958 | 0.3844 | yes | C-0, C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |

Query terms absent from the corpus, contributing nothing: `how`

## Q3

> A customer cancels after shipment because TechNova sent the wrong item. Does the 15% restocking fee apply?

Tokenized to 17 tokens, 16 distinct.

| term | df | raw IDF | effective IDF | floored | chunks containing it |
|---|---:|---:|---:|---|---|
| `because` | 1 | 2.1203 | 2.1203 |  | C-3 |
| `cancels` | 1 | 2.1203 | 2.1203 |  | C-8 |
| `sent` | 1 | 2.1203 | 2.1203 |  | C-3 |
| `wrong` | 2 | 1.5261 | 1.5261 |  | C-3, C-8 |
| `15` | 4 | 0.7472 | 0.7472 |  | C-7, C-8, C-10, C-12 |
| `apply` | 4 | 0.7472 | 0.7472 |  | C-2, C-3, C-7, C-9 |
| `after` | 5 | 0.4353 | 0.4353 |  | C-3, C-5, C-6, C-7, C-8 |
| `does` | 5 | 0.4353 | 0.4353 |  | C-3, C-6, C-7, C-9, C-10 |
| `item` | 5 | 0.4353 | 0.4353 |  | C-3, C-6, C-7, C-8, C-10 |
| `a` | 12 | -2.1203 | 0.3844 | yes | C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `customer` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-6, C-7, C-8 |
| `fee` | 10 | -1.0986 | 0.3844 | yes | C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `restocking` | 10 | -1.0986 | 0.3844 | yes | C-1, C-3, C-4, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `shipment` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-7, C-8, C-12 |
| `technova` | 13 | -3.2958 | 0.3844 | yes | C-0, C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `the` | 13 | -3.2958 | 0.3844 | yes | C-0, C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |

## Q4

> What conditions make a post-shipment cancellation eligible for a restocking-fee waiver?

Tokenized to 13 tokens, 12 distinct.

| term | df | raw IDF | effective IDF | floored | chunks containing it |
|---|---:|---:|---:|---|---|
| `conditions` | 2 | 1.5261 | 1.5261 |  | C-3, C-5 |
| `post` | 3 | 1.0986 | 1.0986 |  | C-5, C-7, C-12 |
| `eligible` | 5 | 0.4353 | 0.4353 |  | C-3, C-6, C-7, C-8, C-10 |
| `a` | 12 | -2.1203 | 0.3844 | yes | C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `cancellation` | 10 | -1.0986 | 0.3844 | yes | C-0, C-1, C-3, C-4, C-5, C-6, C-7, C-9, C-11, C-12 |
| `fee` | 10 | -1.0986 | 0.3844 | yes | C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `for` | 10 | -1.0986 | 0.3844 | yes | C-1, C-2, C-3, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `restocking` | 10 | -1.0986 | 0.3844 | yes | C-1, C-3, C-4, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `shipment` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-7, C-8, C-12 |
| `waiver` | 8 | -0.4353 | 0.3844 | yes | C-3, C-5, C-6, C-7, C-8, C-10, C-11, C-12 |

Query terms absent from the corpus, contributing nothing: `make`, `what`

## Q5

> A customer changes their mind after shipment. Is an inspection required before the refund is issued?

Tokenized to 16 tokens, 15 distinct.

| term | df | raw IDF | effective IDF | floored | chunks containing it |
|---|---:|---:|---:|---|---|
| `changes` | 1 | 2.1203 | 2.1203 |  | C-8 |
| `inspection` | 1 | 2.1203 | 2.1203 |  | C-8 |
| `mind` | 1 | 2.1203 | 2.1203 |  | C-8 |
| `their` | 1 | 2.1203 | 2.1203 |  | C-11 |
| `required` | 2 | 1.5261 | 1.5261 |  | C-8, C-10 |
| `after` | 5 | 0.4353 | 0.4353 |  | C-3, C-5, C-6, C-7, C-8 |
| `a` | 12 | -2.1203 | 0.3844 | yes | C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `an` | 8 | -0.4353 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-7, C-8, C-9, C-10 |
| `before` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-6, C-7, C-8, C-12 |
| `customer` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-6, C-7, C-8 |
| `is` | 9 | -0.7472 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-10, C-12 |
| `refund` | 10 | -1.0986 | 0.3844 | yes | C-1, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |
| `shipment` | 7 | -0.1431 | 0.3844 | yes | C-2, C-3, C-4, C-5, C-7, C-8, C-12 |
| `the` | 13 | -3.2958 | 0.3844 | yes | C-0, C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 |

Query terms absent from the corpus, contributing nothing: `issued`

