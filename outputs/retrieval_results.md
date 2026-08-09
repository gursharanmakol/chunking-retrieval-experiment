# Stage 2: retrieval results

## Run configuration

- run at: 2026-08-07 08:34:41 UTC
- embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- similarity metric: cosine (embeddings L2-normalized, so cosine similarity is the dot product)
- top-k: 3
- source document: `source/technova-billing-cancellation-policy.md` (10849 characters, loaded raw and unmodified)
- chunk counts: A = 22, B = 28, C = 13
- strategy A: fixed size 500 characters, overlap 0
- strategy B: fixed size 500 characters, overlap 100
- strategy C: `## ` heading sections at natural length, no fixed size, no overlap
- excluded: BM25, reranking, contextual retrieval, LLM answer generation
- sufficiency verdicts: none computed by the script; the manual review table below was filled in by hand after the run

## Frozen sufficiency rubric

Committed in `config.py` before this run. Reproduced here so the criteria sit alongside the results they will be judged against.

**Q1.** How long can an approved refund take to appear in a customer's account?

Sufficient only if the retrieved set contains the explicit '5-10 business days' window from Section 6. A set containing only 'refund timing depends on the payment provider', or only the refund-confirmation-email caveat, without the number, is insufficient.

**Q2.** How is the restocking fee calculated for a post-shipment cancellation?

Sufficient only if the retrieved set contains both the 15% rate and the base it is applied to: the amount actually paid after any promotional discount, before tax and shipping charges. Either half alone is insufficient.

**Q3.** A customer cancels after shipment because TechNova sent the wrong item. Does the 15% restocking fee apply?

Sufficient only if the retrieved set contains both the statement that the restocking fee does not apply when the order qualifies under Section 3, and the Section 3 condition 'TechNova shipped the wrong item' (or the Return Handling Matrix row 'Wrong item shipped by TechNova | Waived'). A set containing only the bare 15% post-shipment rule is insufficient, because it supports the wrong answer.

**Q4.** What conditions make a post-shipment cancellation eligible for a restocking-fee waiver?

Sufficient only if all four Section 3 waiver conditions appear intact in the retrieved text: wrong item shipped, product damaged before delivery, verified TechNova fulfillment error, and cancellation requested before the order entered shipment processing. A bullet list truncated by a chunk boundary is insufficient.

**Q5.** A customer changes their mind after shipment. Is an inspection required before the refund is issued?

Sufficient only if the retrieved set binds the 'customer changes mind after shipment' scenario to the inspection requirement: the Return Handling Matrix row together with enough of the table header to identify the inspection column, or Section 6/7 language tying that scenario to inspection. A bare table fragment without the header row or without the scenario label is insufficient, because the column meaning cannot be determined.

## Questions

1. How long can an approved refund take to appear in a customer's account?
2. How is the restocking fee calculated for a post-shipment cancellation?
3. A customer cancels after shipment because TechNova sent the wrong item. Does the 15% restocking fee apply?
4. What conditions make a post-shipment cancellation eligible for a restocking-fee waiver?
5. A customer changes their mind after shipment. Is an inspection required before the refund is issued?

## Summary: retrieved chunk IDs

Ranks 1 to 3, best first.

| Question | A | B | C |
|---|---|---|---|
| Q1 | A-9, A-5, A-10 | B-11, B-27, B-12 | C-6, C-3, C-2 |
| Q2 | A-12, A-10, A-20 | B-13, B-14, B-15 | C-7, C-12, C-4 |
| Q3 | A-10, A-17, A-12 | B-14, B-12, B-21 | C-7, C-12, C-10 |
| Q4 | A-5, A-3, A-11 | B-13, B-14, B-6 | C-7, C-3, C-5 |
| Q5 | A-15, A-5, A-14 | B-6, B-10, B-26 | C-3, C-8, C-6 |

## Manual sufficiency review

Filled in by hand after the run, by reading the retrieved text below against the
matching rubric entry. `retrieve.py` did not compute these verdicts and contains
no sufficiency logic; re-running the script regenerates this file and clears the
table back to empty.

A strategy passes a question when its three retrieved chunks *together* contain
what the rubric entry requires.

| Question | A | B | C |
|---|---|---|---|
| Q1 refund timing | sufficient | sufficient | sufficient |
| Q2 fee calculation | sufficient | sufficient | sufficient |
| Q3 wrong item | insufficient | insufficient | insufficient |
| Q4 waiver conditions | sufficient | insufficient | sufficient |
| Q5 inspection | sufficient | insufficient | sufficient |
| **Total** | **4 / 5** | **2 / 5** | **4 / 5** |

Notes on the individual calls:

- **Q1, all three sufficient.** Every strategy returned a chunk containing
  "Refunds may take **5–10 business days**" at rank 1 (A-9, B-11, C-6).
- **Q2, all three sufficient.** C-7 carried the 15% rate and the calculation base
  in one chunk. A and B needed two slots each: the base in A-12 and B-15, the
  rate in A-10 and B-13.
- **Q3, all three insufficient.** Each set contains Section 7's rule and its
  pointer to Section 3, but none contains the Section 3 condition "TechNova
  shipped the wrong item" or the matrix row "Wrong item shipped by TechNova |
  Waived". A-10 truncates mid-word at "However, the restoc", cutting the clause
  that reverses the answer. Highest scores in the run (B rank 1 = 0.8738,
  C rank 1 = 0.8422) on evidence that supports the wrong answer.
- **Q4, B insufficient.** C-3 and A-3 both carry all four conditions intact. A-3
  survives only because the cut at character 1500 landed inside the heading
  "Orders Elig|ible for Fee Waiver". B-4 ([1600:2100]) holds the four conditions
  intact but was not retrieved; B returned Section 7 fee mechanics instead
  (B-13, B-14, B-6). B's failure is a ranking failure, not a boundary failure.
- **Q5, B insufficient.** C-8 carries the whole Return Handling Matrix with its
  header. A passes across two slots: A-15 (rank 1) has the target row, A-14
  (rank 3) has the header. B retrieved no part of the table; had it done so,
  B-19 holds the "changes mind" row while the header sits in B-18, leaving the
  "Inspection before refund" column unlabeled.

## Retrieved chunks

## Q1

**Question 1:** How long can an approved refund take to appear in a customer's account?

**Rubric entry (frozen before this run):** Sufficient only if the retrieved set contains the explicit '5-10 business days' window from Section 6. A set containing only 'refund timing depends on the payment provider', or only the refund-confirmation-email caveat, without the number, is insufficient.

### Q1 — Strategy A. Fixed-size, no overlap (500 chars, 0 overlap)

#### Rank 1

- cosine score: 0.5607
- chunk ID: A-9
- chunk index: 9
- source character range: [4500:5000]
- character count: 500

````text
ed to the original payment method.

Refund timing depends on the payment provider.

Refunds may take **5–10 business days** to appear on the customer’s account.

TechNova begins refund processing after a cancellation, return, or fee-waiver claim is approved. For returned physical products, TechNova may inspect the item before determining the final refund amount.

The final refund may include the product price, applicable taxes, and eligible shipping charges. If a restocking fee applies under Sec
````

#### Rank 2

- cosine score: 0.4453
- chunk ID: A-5
- chunk index: 5
- source character range: [2500:3000]
- character count: 500

````text
acking, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---

## 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocking fee.

If the order has not entered shipment processing:

- the cancellation is accepted
- the ful
````

#### Rank 3

- cosine score: 0.3262
- chunk ID: A-10
- chunk index: 10
- source character range: [5000:5500]
- character count: 500

````text
tion 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restoc
````

### Q1 — Strategy B. Fixed-size, with overlap (500 chars, 100 overlap)

#### Rank 1

- cosine score: 0.6003
- chunk ID: B-11
- chunk index: 11
- source character range: [4400:4900]
- character count: 500

````text
g the fee-waiver conditions in Section 3.

---

## 6. Refund Processing

Approved refunds are returned to the original payment method.

Refund timing depends on the payment provider.

Refunds may take **5–10 business days** to appear on the customer’s account.

TechNova begins refund processing after a cancellation, return, or fee-waiver claim is approved. For returned physical products, TechNova may inspect the item before determining the final refund amount.

The final refund may include the p
````

#### Rank 2

- cosine score: 0.4233
- chunk ID: B-27
- chunk index: 27
- source character range: [10800:10849]
- character count: 49

````text
 Calculate and issue the refund under Section 6.

````

#### Rank 3

- cosine score: 0.3970
- chunk ID: B-12
- chunk index: 12
- source character range: [4800:5300]
- character count: 500

````text
may inspect the item before determining the final refund amount.

The final refund may include the product price, applicable taxes, and eligible shipping charges. If a restocking fee applies under Section 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellati
````

### Q1 — Strategy C. Markdown section-aware (## headings, natural length)

#### Rank 1

- cosine score: 0.6168
- chunk ID: C-6
- chunk index: 6
- source character range: [4448:5284]
- character count: 836
- section heading: ## 6. Refund Processing

````text
## 6. Refund Processing

Approved refunds are returned to the original payment method.

Refund timing depends on the payment provider.

Refunds may take **5–10 business days** to appear on the customer’s account.

TechNova begins refund processing after a cancellation, return, or fee-waiver claim is approved. For returned physical products, TechNova may inspect the item before determining the final refund amount.

The final refund may include the product price, applicable taxes, and eligible shipping charges. If a restocking fee applies under Section 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---


````

#### Rank 2

- cosine score: 0.3016
- chunk ID: C-3
- chunk index: 3
- source character range: [1483:2799]
- character count: 1316
- section heading: ## 3. Orders Eligible for Fee Waiver

````text
## 3. Orders Eligible for Fee Waiver

A cancellation fee or restocking fee does not apply when one of the following conditions is met:

- TechNova shipped the wrong item.
- The product was damaged before delivery.
- The order was cancelled because of a verified TechNova fulfillment error.
- The customer requested cancellation before the order entered shipment processing.

Orders qualifying under this section are considered **fee-waiver eligible**.

To request a fee waiver, the customer must provide the order number and a description of the issue. For damaged or incorrect products, TechNova may request photos of the product, packaging, and shipping label before approving the claim.

A verified TechNova fulfillment error includes an incorrect item, an incorrect quantity, an order sent to the wrong address because of a TechNova processing error, or a failure to ship an in-stock order within the stated handling period.

For purposes of this policy, damage before delivery means damage that occurred during packing, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---


````

#### Rank 3

- cosine score: 0.2844
- chunk ID: C-2
- chunk index: 2
- source character range: [521:1483]
- character count: 962
- section heading: ## 2. Payment Terms

````text
## 2. Payment Terms

Customers are charged when an order is confirmed.

For subscription products:

- recurring charges are billed at the start of each billing cycle
- failed payments may be retried
- access may be suspended if payment remains outstanding

For physical products:

- payment is authorized at order placement
- final capture occurs when the order ships

A payment authorization confirms that the customer’s payment method can cover the order amount. It is not a completed charge. TechNova captures payment when the physical product ships.

If an authorization expires before shipment, TechNova may request updated payment information or attempt to reauthorize the original payment method. An order may be delayed or cancelled if TechNova cannot obtain a valid authorization.

Prices, taxes, shipping charges, and discounts are shown at checkout. Promotional discounts apply only when the order meets the offer terms at the time of purchase.

---


````

## Q2

**Question 2:** How is the restocking fee calculated for a post-shipment cancellation?

**Rubric entry (frozen before this run):** Sufficient only if the retrieved set contains both the 15% rate and the base it is applied to: the amount actually paid after any promotional discount, before tax and shipping charges. Either half alone is insufficient.

### Q2 — Strategy A. Fixed-size, no overlap (500 chars, 0 overlap)

#### Rank 1

- cosine score: 0.6705
- chunk ID: A-12
- chunk index: 12
- source character range: [6000:6500]
- character count: 500

````text
return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---

## 8. Shipping Charges

Origi
````

#### Rank 2

- cosine score: 0.6490
- chunk ID: A-10
- chunk index: 10
- source character range: [5000:5500]
- character count: 500

````text
tion 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restoc
````

#### Rank 3

- cosine score: 0.6057
- chunk ID: A-20
- chunk index: 20
- source character range: [10000:10500]
- character count: 500

````text
ame and order number when submitting a cancellation, refund, or fee-waiver request.

---

## 12. Policy Interpretation

When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined.

For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. However, TechNova must first determine whether the order qualifies under Section 3 before calculating the final refund.

When reviewing a 
````

### Q2 — Strategy B. Fixed-size, with overlap (500 chars, 100 overlap)

#### Rank 1

- cosine score: 0.7927
- chunk ID: B-13
- chunk index: 13
- source character range: [5200:5700]
- character count: 500

````text
sues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**.

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking
````

#### Rank 2

- cosine score: 0.7091
- chunk ID: B-14
- chunk index: 14
- source character range: [5600:6100]
- character count: 500

````text

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s return instructions.

The restocking fee is based on the amount actually paid for the product after 
````

#### Rank 3

- cosine score: 0.6705
- chunk ID: B-15
- chunk index: 15
- source character range: [6000:6500]
- character count: 500

````text
return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---

## 8. Shipping Charges

Origi
````

### Q2 — Strategy C. Markdown section-aware (## headings, natural length)

#### Rank 1

- cosine score: 0.7467
- chunk ID: C-7
- chunk index: 7
- source character range: [5284:6471]
- character count: 1187
- section heading: ## 7. Cancellation After Shipment

````text
## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**.

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---


````

#### Rank 2

- cosine score: 0.5930
- chunk ID: C-12
- chunk index: 12
- source character range: [10090:10849]
- character count: 759
- section heading: ## 12. Policy Interpretation

````text
## 12. Policy Interpretation

When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined.

For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. However, TechNova must first determine whether the order qualifies under Section 3 before calculating the final refund.

When reviewing a cancellation request, TechNova generally follows this order:

1. Confirm the order and shipment status.
2. Determine whether Section 4, Section 5, or Section 7 applies.
3. Evaluate whether the order qualifies for a fee waiver under Section 3.
4. Review shipping-charge eligibility under Section 8.
5. Calculate and issue the refund under Section 6.

````

#### Rank 3

- cosine score: 0.5533
- chunk ID: C-4
- chunk index: 4
- source character range: [2799:3653]
- character count: 854
- section heading: ## 4. Cancellation Before Shipment

````text
## 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocking fee.

If the order has not entered shipment processing:

- the cancellation is accepted
- the full payment is refunded
- no cancellation fee applies

Customers may submit a cancellation request through the TechNova Support Portal. A request is received when it appears in the customer’s order record.

An order enters shipment processing when TechNova begins picking, packing, labeling, or assigning the order to a carrier. An order awaiting payment review, inventory allocation, or warehouse release has not entered shipment processing.

If TechNova has only authorized payment, the authorization will be released. If payment has already been captured, TechNova will issue a refund to the original payment method in accordance with Section 6.

---


````

## Q3

**Question 3:** A customer cancels after shipment because TechNova sent the wrong item. Does the 15% restocking fee apply?

**Rubric entry (frozen before this run):** Sufficient only if the retrieved set contains both the statement that the restocking fee does not apply when the order qualifies under Section 3, and the Section 3 condition 'TechNova shipped the wrong item' (or the Return Handling Matrix row 'Wrong item shipped by TechNova | Waived'). A set containing only the bare 15% post-shipment rule is insufficient, because it supports the wrong answer.

### Q3 — Strategy A. Fixed-size, no overlap (500 chars, 0 overlap)

#### Rank 1

- cosine score: 0.7817
- chunk ID: A-10
- chunk index: 10
- source character range: [5000:5500]
- character count: 500

````text
tion 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restoc
````

#### Rank 2

- cosine score: 0.7349
- chunk ID: A-17
- chunk index: 17
- source character range: [8500:9000]
- character count: 500

````text
ncel an open physical-product order.

TechNova may issue a subscription refund for a duplicate charge, billing error, or other verified issue. The restocking-fee rules in Section 7 do not apply to subscription cancellations.

---

## 10. Promotional Orders

Promotional discounts do not change the restocking-fee percentage.

For example:

- product list price: $1,000
- promotional price paid: $800
- applicable restocking fee: 15% of the product price actually paid

Promotional gifts, bundled acce
````

#### Rank 3

- cosine score: 0.7188
- chunk ID: A-12
- chunk index: 12
- source character range: [6000:6500]
- character count: 500

````text
return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---

## 8. Shipping Charges

Origi
````

### Q3 — Strategy B. Fixed-size, with overlap (500 chars, 100 overlap)

#### Rank 1

- cosine score: 0.8738
- chunk ID: B-14
- chunk index: 14
- source character range: [5600:6100]
- character count: 500

````text

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s return instructions.

The restocking fee is based on the amount actually paid for the product after 
````

#### Rank 2

- cosine score: 0.7747
- chunk ID: B-12
- chunk index: 12
- source character range: [4800:5300]
- character count: 500

````text
may inspect the item before determining the final refund amount.

The final refund may include the product price, applicable taxes, and eligible shipping charges. If a restocking fee applies under Section 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellati
````

#### Rank 3

- cosine score: 0.7638
- chunk ID: B-21
- chunk index: 21
- source character range: [8400:8900]
- character count: 500

````text
illing period unless TechNova approves an earlier termination. Cancelling a subscription does not cancel an open physical-product order.

TechNova may issue a subscription refund for a duplicate charge, billing error, or other verified issue. The restocking-fee rules in Section 7 do not apply to subscription cancellations.

---

## 10. Promotional Orders

Promotional discounts do not change the restocking-fee percentage.

For example:

- product list price: $1,000
- promotional price paid: $800

````

### Q3 — Strategy C. Markdown section-aware (## headings, natural length)

#### Rank 1

- cosine score: 0.8422
- chunk ID: C-7
- chunk index: 7
- source character range: [5284:6471]
- character count: 1187
- section heading: ## 7. Cancellation After Shipment

````text
## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**.

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---


````

#### Rank 2

- cosine score: 0.7160
- chunk ID: C-12
- chunk index: 12
- source character range: [10090:10849]
- character count: 759
- section heading: ## 12. Policy Interpretation

````text
## 12. Policy Interpretation

When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined.

For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. However, TechNova must first determine whether the order qualifies under Section 3 before calculating the final refund.

When reviewing a cancellation request, TechNova generally follows this order:

1. Confirm the order and shipment status.
2. Determine whether Section 4, Section 5, or Section 7 applies.
3. Evaluate whether the order qualifies for a fee waiver under Section 3.
4. Review shipping-charge eligibility under Section 8.
5. Calculate and issue the refund under Section 6.

````

#### Rank 3

- cosine score: 0.6969
- chunk ID: C-10
- chunk index: 10
- source character range: [8731:9427]
- character count: 696
- section heading: ## 10. Promotional Orders

````text
## 10. Promotional Orders

Promotional discounts do not change the restocking-fee percentage.

For example:

- product list price: $1,000
- promotional price paid: $800
- applicable restocking fee: 15% of the product price actually paid

Promotional gifts, bundled accessories, and limited-time credits must be returned when they were included with the original purchase. If a required promotional item is not returned, TechNova may deduct its stated value from the refund.

An order that qualifies under Section 3 remains fee-waiver eligible even if it was purchased using a promotion. The waiver applies to the restocking fee and does not reinstate an expired promotion or discount code.

---


````

## Q4

**Question 4:** What conditions make a post-shipment cancellation eligible for a restocking-fee waiver?

**Rubric entry (frozen before this run):** Sufficient only if all four Section 3 waiver conditions appear intact in the retrieved text: wrong item shipped, product damaged before delivery, verified TechNova fulfillment error, and cancellation requested before the order entered shipment processing. A bullet list truncated by a chunk boundary is insufficient.

### Q4 — Strategy A. Fixed-size, no overlap (500 chars, 0 overlap)

#### Rank 1

- cosine score: 0.7171
- chunk ID: A-5
- chunk index: 5
- source character range: [2500:3000]
- character count: 500

````text
acking, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---

## 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocking fee.

If the order has not entered shipment processing:

- the cancellation is accepted
- the ful
````

#### Rank 2

- cosine score: 0.6537
- chunk ID: A-3
- chunk index: 3
- source character range: [1500:2000]
- character count: 500

````text
ible for Fee Waiver

A cancellation fee or restocking fee does not apply when one of the following conditions is met:

- TechNova shipped the wrong item.
- The product was damaged before delivery.
- The order was cancelled because of a verified TechNova fulfillment error.
- The customer requested cancellation before the order entered shipment processing.

Orders qualifying under this section are considered **fee-waiver eligible**.

To request a fee waiver, the customer must provide the order num
````

#### Rank 3

- cosine score: 0.6482
- chunk ID: A-11
- chunk index: 11
- source character range: [5500:6000]
- character count: 500

````text
king fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**.

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s 
````

### Q4 — Strategy B. Fixed-size, with overlap (500 chars, 100 overlap)

#### Rank 1

- cosine score: 0.7153
- chunk ID: B-13
- chunk index: 13
- source character range: [5200:5700]
- character count: 500

````text
sues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**.

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking
````

#### Rank 2

- cosine score: 0.7009
- chunk ID: B-14
- chunk index: 14
- source character range: [5600:6100]
- character count: 500

````text

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s return instructions.

The restocking fee is based on the amount actually paid for the product after 
````

#### Rank 3

- cosine score: 0.6572
- chunk ID: B-6
- chunk index: 6
- source character range: [2400:2900]
- character count: 500

````text
ing period.

For purposes of this policy, damage before delivery means damage that occurred during packing, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---

## 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocki
````

### Q4 — Strategy C. Markdown section-aware (## headings, natural length)

#### Rank 1

- cosine score: 0.7203
- chunk ID: C-7
- chunk index: 7
- source character range: [5284:6471]
- character count: 1187
- section heading: ## 7. Cancellation After Shipment

````text
## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restocking fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**.

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---


````

#### Rank 2

- cosine score: 0.6413
- chunk ID: C-3
- chunk index: 3
- source character range: [1483:2799]
- character count: 1316
- section heading: ## 3. Orders Eligible for Fee Waiver

````text
## 3. Orders Eligible for Fee Waiver

A cancellation fee or restocking fee does not apply when one of the following conditions is met:

- TechNova shipped the wrong item.
- The product was damaged before delivery.
- The order was cancelled because of a verified TechNova fulfillment error.
- The customer requested cancellation before the order entered shipment processing.

Orders qualifying under this section are considered **fee-waiver eligible**.

To request a fee waiver, the customer must provide the order number and a description of the issue. For damaged or incorrect products, TechNova may request photos of the product, packaging, and shipping label before approving the claim.

A verified TechNova fulfillment error includes an incorrect item, an incorrect quantity, an order sent to the wrong address because of a TechNova processing error, or a failure to ship an in-stock order within the stated handling period.

For purposes of this policy, damage before delivery means damage that occurred during packing, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---


````

#### Rank 3

- cosine score: 0.6297
- chunk ID: C-5
- chunk index: 5
- source character range: [3653:4448]
- character count: 795
- section heading: ## 5. Cancellation During Shipment Processing

````text
## 5. Cancellation During Shipment Processing

If an order has entered shipment processing but has not yet shipped, TechNova may attempt to stop fulfillment.

If fulfillment can be stopped successfully:

- the order is cancelled
- the customer receives a full refund

If fulfillment cannot be stopped:

- the order is treated as a post-shipment cancellation

TechNova cannot guarantee that fulfillment can be stopped once warehouse processing begins. Whether a request can be completed depends on the order’s current status, including picking, packing, carrier-label creation, and carrier handoff.

If TechNova cannot stop fulfillment, it will provide return instructions after delivery. The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3.

---


````

## Q5

**Question 5:** A customer changes their mind after shipment. Is an inspection required before the refund is issued?

**Rubric entry (frozen before this run):** Sufficient only if the retrieved set binds the 'customer changes mind after shipment' scenario to the inspection requirement: the Return Handling Matrix row together with enough of the table header to identify the inspection column, or Section 6/7 language tying that scenario to inspection. A bare table fragment without the header row or without the scenario label is insufficient, because the column meaning cannot be determined.

### Q5 — Strategy A. Fixed-size, no overlap (500 chars, 0 overlap)

#### Rank 1

- cosine score: 0.5125
- chunk ID: A-15
- chunk index: 15
- source character range: [7500:8000]
- character count: 500

````text
damaged before delivery | Waived | Refunded | Paid by TechNova | Photo review may be required |
| Verified TechNova fulfillment error | Waived | Refunded if related to the error | Paid by TechNova | Case-by-case review |
| Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected |
| Customer cancels before shipment processing | None | Not applicable | Not applicable | No |

The table is a quick operational reference. If the table conflicts
````

#### Rank 2

- cosine score: 0.5053
- chunk ID: A-5
- chunk index: 5
- source character range: [2500:3000]
- character count: 500

````text
acking, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---

## 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocking fee.

If the order has not entered shipment processing:

- the cancellation is accepted
- the ful
````

#### Rank 3

- cosine score: 0.4636
- chunk ID: A-14
- chunk index: 14
- source character range: [7000:7500]
- character count: 500

````text
e eligibility is reviewed separately from restocking-fee eligibility. An order may qualify for a restocking-fee waiver under Section 3 while TechNova separately reviews whether shipping charges should be refunded.

### Return Handling Matrix

| Return scenario | Restocking fee | Original shipping | Return shipping | Inspection before refund |
|---|---:|---|---|---|
| Wrong item shipped by TechNova | Waived | Refunded | Paid by TechNova | No physical inspection required before refund |
| Product 
````

### Q5 — Strategy B. Fixed-size, with overlap (500 chars, 100 overlap)

#### Rank 1

- cosine score: 0.5083
- chunk ID: B-6
- chunk index: 6
- source character range: [2400:2900]
- character count: 500

````text
ing period.

For purposes of this policy, damage before delivery means damage that occurred during packing, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---

## 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocki
````

#### Rank 2

- cosine score: 0.4599
- chunk ID: B-10
- chunk index: 10
- source character range: [4000:4500]
- character count: 500

````text
ncellation

TechNova cannot guarantee that fulfillment can be stopped once warehouse processing begins. Whether a request can be completed depends on the order’s current status, including picking, packing, carrier-label creation, and carrier handoff.

If TechNova cannot stop fulfillment, it will provide return instructions after delivery. The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3.

---

## 6. Refund Processing

Approved refunds are return
````

#### Rank 3

- cosine score: 0.4430
- chunk ID: B-26
- chunk index: 26
- source character range: [10400:10849]
- character count: 449

````text
 whether the order qualifies under Section 3 before calculating the final refund.

When reviewing a cancellation request, TechNova generally follows this order:

1. Confirm the order and shipment status.
2. Determine whether Section 4, Section 5, or Section 7 applies.
3. Evaluate whether the order qualifies for a fee waiver under Section 3.
4. Review shipping-charge eligibility under Section 8.
5. Calculate and issue the refund under Section 6.

````

### Q5 — Strategy C. Markdown section-aware (## headings, natural length)

#### Rank 1

- cosine score: 0.4681
- chunk ID: C-3
- chunk index: 3
- source character range: [1483:2799]
- character count: 1316
- section heading: ## 3. Orders Eligible for Fee Waiver

````text
## 3. Orders Eligible for Fee Waiver

A cancellation fee or restocking fee does not apply when one of the following conditions is met:

- TechNova shipped the wrong item.
- The product was damaged before delivery.
- The order was cancelled because of a verified TechNova fulfillment error.
- The customer requested cancellation before the order entered shipment processing.

Orders qualifying under this section are considered **fee-waiver eligible**.

To request a fee waiver, the customer must provide the order number and a description of the issue. For damaged or incorrect products, TechNova may request photos of the product, packaging, and shipping label before approving the claim.

A verified TechNova fulfillment error includes an incorrect item, an incorrect quantity, an order sent to the wrong address because of a TechNova processing error, or a failure to ship an in-stock order within the stated handling period.

For purposes of this policy, damage before delivery means damage that occurred during packing, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---


````

#### Rank 2

- cosine score: 0.4677
- chunk ID: C-8
- chunk index: 8
- source character range: [6471:8089]
- character count: 1618
- section heading: ## 8. Shipping Charges

````text
## 8. Shipping Charges

Original shipping charges are generally non-refundable after shipment.

Shipping charges may be refunded if:

- TechNova shipped the wrong product
- the product was damaged before delivery
- the shipment failure was caused by TechNova

Customers are responsible for return-shipping costs unless TechNova confirms that the return resulted from an eligible damage claim, an incorrect shipment, or a verified fulfillment error. TechNova may provide a prepaid return label in those situations.

Shipping-charge eligibility is reviewed separately from restocking-fee eligibility. An order may qualify for a restocking-fee waiver under Section 3 while TechNova separately reviews whether shipping charges should be refunded.

### Return Handling Matrix

| Return scenario | Restocking fee | Original shipping | Return shipping | Inspection before refund |
|---|---:|---|---|---|
| Wrong item shipped by TechNova | Waived | Refunded | Paid by TechNova | No physical inspection required before refund |
| Product damaged before delivery | Waived | Refunded | Paid by TechNova | Photo review may be required |
| Verified TechNova fulfillment error | Waived | Refunded if related to the error | Paid by TechNova | Case-by-case review |
| Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected |
| Customer cancels before shipment processing | None | Not applicable | Not applicable | No |

The table is a quick operational reference. If the table conflicts with the detailed rules in another section, the detailed policy language governs.

---


````

#### Rank 3

- cosine score: 0.4246
- chunk ID: C-6
- chunk index: 6
- source character range: [4448:5284]
- character count: 836
- section heading: ## 6. Refund Processing

````text
## 6. Refund Processing

Approved refunds are returned to the original payment method.

Refund timing depends on the payment provider.

Refunds may take **5–10 business days** to appear on the customer’s account.

TechNova begins refund processing after a cancellation, return, or fee-waiver claim is approved. For returned physical products, TechNova may inspect the item before determining the final refund amount.

The final refund may include the product price, applicable taxes, and eligible shipping charges. If a restocking fee applies under Section 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---


````

