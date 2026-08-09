# Stage 1: chunk inspection

Source document: `source/technova-billing-cancellation-policy.md` (10849 characters, loaded raw and unmodified).

Strategies A and B slice the raw text on character counts only. Strategy C splits on `## ` headings and leaves each section at its natural length. Chunk text below is an exact slice of the source, including leading and trailing whitespace and `---` rules.

## Totals

| Strategy | Chunks | Min chars | Max chars | Mean chars | Total chars |
|---|---:|---:|---:|---:|---:|
| A. Fixed-size, no overlap (500 chars, 0 overlap) | 22 | 349 | 500 | 493 | 10849 |
| B. Fixed-size, with overlap (500 chars, 100 overlap) | 28 | 49 | 500 | 482 | 13498 |
| C. Markdown section-aware (## headings, natural length) | 13 | 151 | 1618 | 835 | 10849 |

## A. Fixed-size, no overlap (500 chars, 0 overlap)

Total chunks: 22

### Chunk 0

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 0
- character count: 500
- source character range: [0:500]
- starts with: '# TechNova Billing and Cancellation Policy\n\n**Effective date'
- ends with: 'reement conflicts with this policy, the signed agreement tak'

````text
# TechNova Billing and Cancellation Policy

**Effective date:** August 1, 2026  
**Applies to:** Purchases made directly from the TechNova Store

---

## 1. Purpose

This policy defines billing, cancellation, refund, and restocking rules for TechNova product orders.

It applies to physical products, subscriptions, accessories, promotional purchases, and business orders unless a separate written agreement applies. If a signed business agreement conflicts with this policy, the signed agreement tak
````

### Chunk 1

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 1
- character count: 500
- source character range: [500:1000]
- starts with: 'es precedence.\n\n---\n\n## 2. Payment Terms\n\nCustomers are char'
- ends with: '’s payment method can cover the order amount. It is not a co'

````text
es precedence.

---

## 2. Payment Terms

Customers are charged when an order is confirmed.

For subscription products:

- recurring charges are billed at the start of each billing cycle
- failed payments may be retried
- access may be suspended if payment remains outstanding

For physical products:

- payment is authorized at order placement
- final capture occurs when the order ships

A payment authorization confirms that the customer’s payment method can cover the order amount. It is not a co
````

### Chunk 2

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 2
- character count: 500
- source character range: [1000:1500]
- starts with: 'mpleted charge. TechNova captures payment when the physical '
- ends with: 'offer terms at the time of purchase.\n\n---\n\n## 3. Orders Elig'

````text
mpleted charge. TechNova captures payment when the physical product ships.

If an authorization expires before shipment, TechNova may request updated payment information or attempt to reauthorize the original payment method. An order may be delayed or cancelled if TechNova cannot obtain a valid authorization.

Prices, taxes, shipping charges, and discounts are shown at checkout. Promotional discounts apply only when the order meets the offer terms at the time of purchase.

---

## 3. Orders Elig
````

### Chunk 3

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 3
- character count: 500
- source character range: [1500:2000]
- starts with: 'ible for Fee Waiver\n\nA cancellation fee or restocking fee do'
- ends with: 'equest a fee waiver, the customer must provide the order num'

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

### Chunk 4

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 4
- character count: 500
- source character range: [2000:2500]
- starts with: 'ber and a description of the issue. For damaged or incorrect'
- ends with: ', damage before delivery means damage that occurred during p'

````text
ber and a description of the issue. For damaged or incorrect products, TechNova may request photos of the product, packaging, and shipping label before approving the claim.

A verified TechNova fulfillment error includes an incorrect item, an incorrect quantity, an order sent to the wrong address because of a TechNova processing error, or a failure to ship an in-stock order within the stated handling period.

For purposes of this policy, damage before delivery means damage that occurred during p
````

### Chunk 5

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 5
- character count: 500
- source character range: [2500:3000]
- starts with: 'acking, handling, or transit and was not caused by the custo'
- ends with: 'ipment processing:\n\n- the cancellation is accepted\n- the ful'

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

### Chunk 6

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 6
- character count: 500
- source character range: [3000:3500]
- starts with: 'l payment is refunded\n- no cancellation fee applies\n\nCustome'
- ends with: '\n\nIf TechNova has only authorized payment, the authorization'

````text
l payment is refunded
- no cancellation fee applies

Customers may submit a cancellation request through the TechNova Support Portal. A request is received when it appears in the customer’s order record.

An order enters shipment processing when TechNova begins picking, packing, labeling, or assigning the order to a carrier. An order awaiting payment review, inventory allocation, or warehouse release has not entered shipment processing.

If TechNova has only authorized payment, the authorization
````

### Chunk 7

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 7
- character count: 500
- source character range: [3500:4000]
- starts with: ' will be released. If payment has already been captured, Tec'
- ends with: 'ot be stopped:\n\n- the order is treated as a post-shipment ca'

````text
 will be released. If payment has already been captured, TechNova will issue a refund to the original payment method in accordance with Section 6.

---

## 5. Cancellation During Shipment Processing

If an order has entered shipment processing but has not yet shipped, TechNova may attempt to stop fulfillment.

If fulfillment can be stopped successfully:

- the order is cancelled
- the customer receives a full refund

If fulfillment cannot be stopped:

- the order is treated as a post-shipment ca
````

### Chunk 8

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 8
- character count: 500
- source character range: [4000:4500]
- starts with: 'ncellation\n\nTechNova cannot guarantee that fulfillment can b'
- ends with: '.\n\n---\n\n## 6. Refund Processing\n\nApproved refunds are return'

````text
ncellation

TechNova cannot guarantee that fulfillment can be stopped once warehouse processing begins. Whether a request can be completed depends on the order’s current status, including picking, packing, carrier-label creation, and carrier handoff.

If TechNova cannot stop fulfillment, it will provide return instructions after delivery. The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3.

---

## 6. Refund Processing

Approved refunds are return
````

### Chunk 9

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 9
- character count: 500
- source character range: [4500:5000]
- starts with: 'ed to the original payment method.\n\nRefund timing depends on'
- ends with: 'ible shipping charges. If a restocking fee applies under Sec'

````text
ed to the original payment method.

Refund timing depends on the payment provider.

Refunds may take **5–10 business days** to appear on the customer’s account.

TechNova begins refund processing after a cancellation, return, or fee-waiver claim is approved. For returned physical products, TechNova may inspect the item before determining the final refund amount.

The final refund may include the product price, applicable taxes, and eligible shipping charges. If a restocking fee applies under Sec
````

### Chunk 10

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 10
- character count: 500
- source character range: [5000:5500]
- starts with: 'tion 7, TechNova deducts that amount before issuing the refu'
- ends with: ' price before tax and shipping charges.\n\nHowever, the restoc'

````text
tion 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellation After Shipment

Cancellation after shipment normally incurs a **15% restocking fee**.

The restocking fee is calculated using the product price before tax and shipping charges.

However, the restoc
````

### Chunk 11

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 11
- character count: 500
- source character range: [5500:6000]
- starts with: 'king fee does not apply if the order qualifies under **Secti'
- ends with: '. The customer must return the item according to TechNova’s '

````text
king fee does not apply if the order qualifies under **Section 3: Orders Eligible for Fee Waiver**.

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s 
````

### Chunk 12

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 12
- character count: 500
- source character range: [6000:6500]
- starts with: 'return instructions.\n\nThe restocking fee is based on the amo'
- ends with: 'rder already in transit.\n\n---\n\n## 8. Shipping Charges\n\nOrigi'

````text
return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---

## 8. Shipping Charges

Origi
````

### Chunk 13

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 13
- character count: 500
- source character range: [6500:7000]
- starts with: 'nal shipping charges are generally non-refundable after ship'
- ends with: ' a prepaid return label in those situations.\n\nShipping-charg'

````text
nal shipping charges are generally non-refundable after shipment.

Shipping charges may be refunded if:

- TechNova shipped the wrong product
- the product was damaged before delivery
- the shipment failure was caused by TechNova

Customers are responsible for return-shipping costs unless TechNova confirms that the return resulted from an eligible damage claim, an incorrect shipment, or a verified fulfillment error. TechNova may provide a prepaid return label in those situations.

Shipping-charg
````

### Chunk 14

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 14
- character count: 500
- source character range: [7000:7500]
- starts with: 'e eligibility is reviewed separately from restocking-fee eli'
- ends with: '| No physical inspection required before refund |\n| Product '

````text
e eligibility is reviewed separately from restocking-fee eligibility. An order may qualify for a restocking-fee waiver under Section 3 while TechNova separately reviews whether shipping charges should be refunded.

### Return Handling Matrix

| Return scenario | Restocking fee | Original shipping | Return shipping | Inspection before refund |
|---|---:|---|---|---|
| Wrong item shipped by TechNova | Waived | Refunded | Paid by TechNova | No physical inspection required before refund |
| Product 
````

### Chunk 15

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 15
- character count: 500
- source character range: [7500:8000]
- starts with: 'damaged before delivery | Waived | Refunded | Paid by TechNo'
- ends with: 'ble is a quick operational reference. If the table conflicts'

````text
damaged before delivery | Waived | Refunded | Paid by TechNova | Photo review may be required |
| Verified TechNova fulfillment error | Waived | Refunded if related to the error | Paid by TechNova | Case-by-case review |
| Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected |
| Customer cancels before shipment processing | None | Not applicable | Not applicable | No |

The table is a quick operational reference. If the table conflicts
````

### Chunk 16

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 16
- character count: 500
- source character range: [8000:8500]
- starts with: ' with the detailed rules in another section, the detailed po'
- ends with: 'n earlier termination. Cancelling a subscription does not ca'

````text
 with the detailed rules in another section, the detailed policy language governs.

---

## 9. Subscription Cancellation

Subscription customers may cancel future renewals at any time.

Cancellation:

- stops future billing
- does not automatically refund charges already processed
- does not affect physical-order restocking rules

The subscription remains active until the end of the current paid billing period unless TechNova approves an earlier termination. Cancelling a subscription does not ca
````

### Chunk 17

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 17
- character count: 500
- source character range: [8500:9000]
- starts with: 'ncel an open physical-product order.\n\nTechNova may issue a s'
- ends with: 'product price actually paid\n\nPromotional gifts, bundled acce'

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

### Chunk 18

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 18
- character count: 500
- source character range: [9000:9500]
- starts with: 'ssories, and limited-time credits must be returned when they'
- ends with: 'ss Orders\n\nBusiness orders containing more than 25 units may'

````text
ssories, and limited-time credits must be returned when they were included with the original purchase. If a required promotional item is not returned, TechNova may deduct its stated value from the refund.

An order that qualifies under Section 3 remains fee-waiver eligible even if it was purchased using a promotion. The waiver applies to the restocking fee and does not reinstate an expired promotion or discount code.

---

## 11. Business Orders

Business orders containing more than 25 units may
````

### Chunk 19

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 19
- character count: 500
- source character range: [9500:10000]
- starts with: ' be subject to separate contract terms.\n\nIf a signed busines'
- ends with: 'rder. Business customers should include their organization n'

````text
 be subject to separate contract terms.

If a signed business agreement conflicts with this policy, the signed agreement takes precedence.

TechNova may require additional review for orders involving volume pricing, custom configurations, staged delivery, or purchase orders. Those orders may have different cancellation deadlines, restocking fees, or return requirements.

If no signed business agreement applies, this policy governs the order. Business customers should include their organization n
````

### Chunk 20

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 20
- character count: 500
- source character range: [10000:10500]
- starts with: 'ame and order number when submitting a cancellation, refund,'
- ends with: 'on 3 before calculating the final refund.\n\nWhen reviewing a '

````text
ame and order number when submitting a cancellation, refund, or fee-waiver request.

---

## 12. Policy Interpretation

When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined.

For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. However, TechNova must first determine whether the order qualifies under Section 3 before calculating the final refund.

When reviewing a 
````

### Chunk 21

- strategy: A. Fixed-size, no overlap (500 chars, 0 overlap)
- chunk index: 21
- character count: 349
- source character range: [10500:10849]
- starts with: 'cancellation request, TechNova generally follows this order:'
- ends with: 'ction 8.\n5. Calculate and issue the refund under Section 6.\n'

````text
cancellation request, TechNova generally follows this order:

1. Confirm the order and shipment status.
2. Determine whether Section 4, Section 5, or Section 7 applies.
3. Evaluate whether the order qualifies for a fee waiver under Section 3.
4. Review shipping-charge eligibility under Section 8.
5. Calculate and issue the refund under Section 6.

````

## B. Fixed-size, with overlap (500 chars, 100 overlap)

Total chunks: 28

### Chunk 0

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 0
- character count: 500
- source character range: [0:500]
- starts with: '# TechNova Billing and Cancellation Policy\n\n**Effective date'
- ends with: 'reement conflicts with this policy, the signed agreement tak'

````text
# TechNova Billing and Cancellation Policy

**Effective date:** August 1, 2026  
**Applies to:** Purchases made directly from the TechNova Store

---

## 1. Purpose

This policy defines billing, cancellation, refund, and restocking rules for TechNova product orders.

It applies to physical products, subscriptions, accessories, promotional purchases, and business orders unless a separate written agreement applies. If a signed business agreement conflicts with this policy, the signed agreement tak
````

### Chunk 1

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 1
- character count: 500
- source character range: [400:900]
- starts with: 'reement applies. If a signed business agreement conflicts wi'
- ends with: 'ment\n- final capture occurs when the order ships\n\nA payment '

````text
reement applies. If a signed business agreement conflicts with this policy, the signed agreement takes precedence.

---

## 2. Payment Terms

Customers are charged when an order is confirmed.

For subscription products:

- recurring charges are billed at the start of each billing cycle
- failed payments may be retried
- access may be suspended if payment remains outstanding

For physical products:

- payment is authorized at order placement
- final capture occurs when the order ships

A payment 
````

### Chunk 2

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 2
- character count: 500
- source character range: [800:1300]
- starts with: '\n\n- payment is authorized at order placement\n- final capture'
- ends with: ' delayed or cancelled if TechNova cannot obtain a valid auth'

````text


- payment is authorized at order placement
- final capture occurs when the order ships

A payment authorization confirms that the customer’s payment method can cover the order amount. It is not a completed charge. TechNova captures payment when the physical product ships.

If an authorization expires before shipment, TechNova may request updated payment information or attempt to reauthorize the original payment method. An order may be delayed or cancelled if TechNova cannot obtain a valid auth
````

### Chunk 3

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 3
- character count: 500
- source character range: [1200:1700]
- starts with: 'original payment method. An order may be delayed or cancelle'
- ends with: 'e wrong item.\n- The product was damaged before delivery.\n- T'

````text
original payment method. An order may be delayed or cancelled if TechNova cannot obtain a valid authorization.

Prices, taxes, shipping charges, and discounts are shown at checkout. Promotional discounts apply only when the order meets the offer terms at the time of purchase.

---

## 3. Orders Eligible for Fee Waiver

A cancellation fee or restocking fee does not apply when one of the following conditions is met:

- TechNova shipped the wrong item.
- The product was damaged before delivery.
- T
````

### Chunk 4

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 4
- character count: 500
- source character range: [1600:2100]
- starts with: 'onditions is met:\n\n- TechNova shipped the wrong item.\n- The '
- ends with: 'damaged or incorrect products, TechNova may request photos o'

````text
onditions is met:

- TechNova shipped the wrong item.
- The product was damaged before delivery.
- The order was cancelled because of a verified TechNova fulfillment error.
- The customer requested cancellation before the order entered shipment processing.

Orders qualifying under this section are considered **fee-waiver eligible**.

To request a fee waiver, the customer must provide the order number and a description of the issue. For damaged or incorrect products, TechNova may request photos o
````

### Chunk 5

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 5
- character count: 500
- source character range: [2000:2500]
- starts with: 'ber and a description of the issue. For damaged or incorrect'
- ends with: ', damage before delivery means damage that occurred during p'

````text
ber and a description of the issue. For damaged or incorrect products, TechNova may request photos of the product, packaging, and shipping label before approving the claim.

A verified TechNova fulfillment error includes an incorrect item, an incorrect quantity, an order sent to the wrong address because of a TechNova processing error, or a failure to ship an in-stock order within the stated handling period.

For purposes of this policy, damage before delivery means damage that occurred during p
````

### Chunk 6

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 6
- character count: 500
- source character range: [2400:2900]
- starts with: 'ing period.\n\nFor purposes of this policy, damage before deli'
- ends with: 'tomer may cancel an order before shipment without a restocki'

````text
ing period.

For purposes of this policy, damage before delivery means damage that occurred during packing, handling, or transit and was not caused by the customer after delivery. Damage claims should be reported within 14 calendar days of delivery.

Fee-waiver eligibility applies to the restocking fee. Whether original or return shipping charges are refunded is determined under Section 8.

---

## 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocki
````

### Chunk 7

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 7
- character count: 500
- source character range: [2800:3300]
- starts with: '# 4. Cancellation Before Shipment\n\nA customer may cancel an '
- ends with: ' when TechNova begins picking, packing, labeling, or assigni'

````text
# 4. Cancellation Before Shipment

A customer may cancel an order before shipment without a restocking fee.

If the order has not entered shipment processing:

- the cancellation is accepted
- the full payment is refunded
- no cancellation fee applies

Customers may submit a cancellation request through the TechNova Support Portal. A request is received when it appears in the customer’s order record.

An order enters shipment processing when TechNova begins picking, packing, labeling, or assigni
````

### Chunk 8

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 8
- character count: 500
- source character range: [3200:3700]
- starts with: 'rd.\n\nAn order enters shipment processing when TechNova begin'
- ends with: 'ion 6.\n\n---\n\n## 5. Cancellation During Shipment Processing\n\n'

````text
rd.

An order enters shipment processing when TechNova begins picking, packing, labeling, or assigning the order to a carrier. An order awaiting payment review, inventory allocation, or warehouse release has not entered shipment processing.

If TechNova has only authorized payment, the authorization will be released. If payment has already been captured, TechNova will issue a refund to the original payment method in accordance with Section 6.

---

## 5. Cancellation During Shipment Processing


````

### Chunk 9

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 9
- character count: 500
- source character range: [3600:4100]
- starts with: 'l payment method in accordance with Section 6.\n\n---\n\n## 5. C'
- ends with: 'at fulfillment can be stopped once warehouse processing begi'

````text
l payment method in accordance with Section 6.

---

## 5. Cancellation During Shipment Processing

If an order has entered shipment processing but has not yet shipped, TechNova may attempt to stop fulfillment.

If fulfillment can be stopped successfully:

- the order is cancelled
- the customer receives a full refund

If fulfillment cannot be stopped:

- the order is treated as a post-shipment cancellation

TechNova cannot guarantee that fulfillment can be stopped once warehouse processing begi
````

### Chunk 10

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 10
- character count: 500
- source character range: [4000:4500]
- starts with: 'ncellation\n\nTechNova cannot guarantee that fulfillment can b'
- ends with: '.\n\n---\n\n## 6. Refund Processing\n\nApproved refunds are return'

````text
ncellation

TechNova cannot guarantee that fulfillment can be stopped once warehouse processing begins. Whether a request can be completed depends on the order’s current status, including picking, packing, carrier-label creation, and carrier handoff.

If TechNova cannot stop fulfillment, it will provide return instructions after delivery. The request will then be reviewed under Section 7, including the fee-waiver conditions in Section 3.

---

## 6. Refund Processing

Approved refunds are return
````

### Chunk 11

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 11
- character count: 500
- source character range: [4400:4900]
- starts with: 'g the fee-waiver conditions in Section 3.\n\n---\n\n## 6. Refund'
- ends with: 'the final refund amount.\n\nThe final refund may include the p'

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

### Chunk 12

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 12
- character count: 500
- source character range: [4800:5300]
- starts with: 'may inspect the item before determining the final refund amo'
- ends with: 'rd issuer, bank, or payment provider.\n\n---\n\n## 7. Cancellati'

````text
may inspect the item before determining the final refund amount.

The final refund may include the product price, applicable taxes, and eligible shipping charges. If a restocking fee applies under Section 7, TechNova deducts that amount before issuing the refund.

A refund confirmation email does not mean the funds have already appeared in the customer’s account. Processing times after TechNova issues the refund are determined by the card issuer, bank, or payment provider.

---

## 7. Cancellati
````

### Chunk 13

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 13
- character count: 500
- source character range: [5200:5700]
- starts with: 'sues the refund are determined by the card issuer, bank, or '
- ends with: '\n\n- the customer receives a full refund\n- the 15% restocking'

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

### Chunk 14

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 14
- character count: 500
- source character range: [5600:6100]
- starts with: '\nIf the order qualifies under Section 3:\n\n- the customer rec'
- ends with: ' is based on the amount actually paid for the product after '

````text

If the order qualifies under Section 3:

- the customer receives a full refund
- the 15% restocking fee is waived

If the order does not qualify:

- the 15% restocking fee is deducted from the refund

A post-shipment cancellation applies when an order has shipped, is in transit, has been delivered, or could not be stopped under Section 5. The customer must return the item according to TechNova’s return instructions.

The restocking fee is based on the amount actually paid for the product after 
````

### Chunk 15

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 15
- character count: 500
- source character range: [6000:6500]
- starts with: 'return instructions.\n\nThe restocking fee is based on the amo'
- ends with: 'rder already in transit.\n\n---\n\n## 8. Shipping Charges\n\nOrigi'

````text
return instructions.

The restocking fee is based on the amount actually paid for the product after any promotional discount, but before tax and shipping charges. For example, if a product was listed at $1,000 and purchased for $800 during a promotion, the restocking fee is $120.

The restocking fee is waived when TechNova confirms that the order is fee-waiver eligible under Section 3. A cancellation request by itself does not stop an order already in transit.

---

## 8. Shipping Charges

Origi
````

### Chunk 16

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 16
- character count: 500
- source character range: [6400:6900]
- starts with: 'ion request by itself does not stop an order already in tran'
- ends with: ' eligible damage claim, an incorrect shipment, or a verified'

````text
ion request by itself does not stop an order already in transit.

---

## 8. Shipping Charges

Original shipping charges are generally non-refundable after shipment.

Shipping charges may be refunded if:

- TechNova shipped the wrong product
- the product was damaged before delivery
- the shipment failure was caused by TechNova

Customers are responsible for return-shipping costs unless TechNova confirms that the return resulted from an eligible damage claim, an incorrect shipment, or a verified
````

### Chunk 17

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 17
- character count: 500
- source character range: [6800:7300]
- starts with: 'onfirms that the return resulted from an eligible damage cla'
- ends with: 'x\n\n| Return scenario | Restocking fee | Original shipping | '

````text
onfirms that the return resulted from an eligible damage claim, an incorrect shipment, or a verified fulfillment error. TechNova may provide a prepaid return label in those situations.

Shipping-charge eligibility is reviewed separately from restocking-fee eligibility. An order may qualify for a restocking-fee waiver under Section 3 while TechNova separately reviews whether shipping charges should be refunded.

### Return Handling Matrix

| Return scenario | Restocking fee | Original shipping | 
````

### Chunk 18

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 18
- character count: 500
- source character range: [7200:7700]
- starts with: ' be refunded.\n\n### Return Handling Matrix\n\n| Return scenario'
- ends with: 'ed | Refunded if related to the error | Paid by TechNova | C'

````text
 be refunded.

### Return Handling Matrix

| Return scenario | Restocking fee | Original shipping | Return shipping | Inspection before refund |
|---|---:|---|---|---|
| Wrong item shipped by TechNova | Waived | Refunded | Paid by TechNova | No physical inspection required before refund |
| Product damaged before delivery | Waived | Refunded | Paid by TechNova | Photo review may be required |
| Verified TechNova fulfillment error | Waived | Refunded if related to the error | Paid by TechNova | C
````

### Chunk 19

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 19
- character count: 500
- source character range: [7600:8100]
- starts with: 'rified TechNova fulfillment error | Waived | Refunded if rel'
- ends with: 'ion, the detailed policy language governs.\n\n---\n\n## 9. Subsc'

````text
rified TechNova fulfillment error | Waived | Refunded if related to the error | Paid by TechNova | Case-by-case review |
| Customer changes mind after shipment | 15% | Not refunded | Paid by customer | Returned product must be inspected |
| Customer cancels before shipment processing | None | Not applicable | Not applicable | No |

The table is a quick operational reference. If the table conflicts with the detailed rules in another section, the detailed policy language governs.

---

## 9. Subsc
````

### Chunk 20

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 20
- character count: 500
- source character range: [8000:8500]
- starts with: ' with the detailed rules in another section, the detailed po'
- ends with: 'n earlier termination. Cancelling a subscription does not ca'

````text
 with the detailed rules in another section, the detailed policy language governs.

---

## 9. Subscription Cancellation

Subscription customers may cancel future renewals at any time.

Cancellation:

- stops future billing
- does not automatically refund charges already processed
- does not affect physical-order restocking rules

The subscription remains active until the end of the current paid billing period unless TechNova approves an earlier termination. Cancelling a subscription does not ca
````

### Chunk 21

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 21
- character count: 500
- source character range: [8400:8900]
- starts with: 'illing period unless TechNova approves an earlier terminatio'
- ends with: '- product list price: $1,000\n- promotional price paid: $800\n'

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

### Chunk 22

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 22
- character count: 500
- source character range: [8800:9300]
- starts with: 'stocking-fee percentage.\n\nFor example:\n\n- product list price'
- ends with: 'ion 3 remains fee-waiver eligible even if it was purchased u'

````text
stocking-fee percentage.

For example:

- product list price: $1,000
- promotional price paid: $800
- applicable restocking fee: 15% of the product price actually paid

Promotional gifts, bundled accessories, and limited-time credits must be returned when they were included with the original purchase. If a required promotional item is not returned, TechNova may deduct its stated value from the refund.

An order that qualifies under Section 3 remains fee-waiver eligible even if it was purchased u
````

### Chunk 23

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 23
- character count: 500
- source character range: [9200:9700]
- starts with: 'und.\n\nAn order that qualifies under Section 3 remains fee-wa'
- ends with: 'TechNova may require additional review for orders involving '

````text
und.

An order that qualifies under Section 3 remains fee-waiver eligible even if it was purchased using a promotion. The waiver applies to the restocking fee and does not reinstate an expired promotion or discount code.

---

## 11. Business Orders

Business orders containing more than 25 units may be subject to separate contract terms.

If a signed business agreement conflicts with this policy, the signed agreement takes precedence.

TechNova may require additional review for orders involving 
````

### Chunk 24

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 24
- character count: 500
- source character range: [9600:10100]
- starts with: 'the signed agreement takes precedence.\n\nTechNova may require'
- ends with: 'ancellation, refund, or fee-waiver request.\n\n---\n\n## 12. Pol'

````text
the signed agreement takes precedence.

TechNova may require additional review for orders involving volume pricing, custom configurations, staged delivery, or purchase orders. Those orders may have different cancellation deadlines, restocking fees, or return requirements.

If no signed business agreement applies, this policy governs the order. Business customers should include their organization name and order number when submitting a cancellation, refund, or fee-waiver request.

---

## 12. Pol
````

### Chunk 25

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 25
- character count: 500
- source character range: [10000:10500]
- starts with: 'ame and order number when submitting a cancellation, refund,'
- ends with: 'on 3 before calculating the final refund.\n\nWhen reviewing a '

````text
ame and order number when submitting a cancellation, refund, or fee-waiver request.

---

## 12. Policy Interpretation

When a cancellation depends on another section of this policy, the referenced section must be evaluated before the final refund amount is determined.

For example, Section 7 sets the normal 15% restocking fee for post-shipment cancellations. However, TechNova must first determine whether the order qualifies under Section 3 before calculating the final refund.

When reviewing a 
````

### Chunk 26

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 26
- character count: 449
- source character range: [10400:10849]
- starts with: ' whether the order qualifies under Section 3 before calculat'
- ends with: 'ction 8.\n5. Calculate and issue the refund under Section 6.\n'

````text
 whether the order qualifies under Section 3 before calculating the final refund.

When reviewing a cancellation request, TechNova generally follows this order:

1. Confirm the order and shipment status.
2. Determine whether Section 4, Section 5, or Section 7 applies.
3. Evaluate whether the order qualifies for a fee waiver under Section 3.
4. Review shipping-charge eligibility under Section 8.
5. Calculate and issue the refund under Section 6.

````

### Chunk 27

- strategy: B. Fixed-size, with overlap (500 chars, 100 overlap)
- chunk index: 27
- character count: 49
- source character range: [10800:10849]
- starts with: ' Calculate and issue the refund under Section 6.\n'
- ends with: ' Calculate and issue the refund under Section 6.\n'

````text
 Calculate and issue the refund under Section 6.

````

## C. Markdown section-aware (## headings, natural length)

Total chunks: 13

### Chunk 0

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 0
- character count: 151
- source character range: [0:151]
- section heading: (front matter, before first ## heading)
- starts with: '# TechNova Billing and Cancellation Policy\n\n**Effective date'
- ends with: 'to:** Purchases made directly from the TechNova Store\n\n---\n\n'

````text
# TechNova Billing and Cancellation Policy

**Effective date:** August 1, 2026  
**Applies to:** Purchases made directly from the TechNova Store

---


````

### Chunk 1

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 1
- character count: 370
- source character range: [151:521]
- section heading: ## 1. Purpose
- starts with: '## 1. Purpose\n\nThis policy defines billing, cancellation, re'
- ends with: 'h this policy, the signed agreement takes precedence.\n\n---\n\n'

````text
## 1. Purpose

This policy defines billing, cancellation, refund, and restocking rules for TechNova product orders.

It applies to physical products, subscriptions, accessories, promotional purchases, and business orders unless a separate written agreement applies. If a signed business agreement conflicts with this policy, the signed agreement takes precedence.

---


````

### Chunk 2

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 2
- character count: 962
- source character range: [521:1483]
- section heading: ## 2. Payment Terms
- starts with: '## 2. Payment Terms\n\nCustomers are charged when an order is '
- ends with: ' order meets the offer terms at the time of purchase.\n\n---\n\n'

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

### Chunk 3

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 3
- character count: 1316
- source character range: [1483:2799]
- section heading: ## 3. Orders Eligible for Fee Waiver
- starts with: '## 3. Orders Eligible for Fee Waiver\n\nA cancellation fee or '
- ends with: 'g charges are refunded is determined under Section 8.\n\n---\n\n'

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

### Chunk 4

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 4
- character count: 854
- source character range: [2799:3653]
- section heading: ## 4. Cancellation Before Shipment
- starts with: '## 4. Cancellation Before Shipment\n\nA customer may cancel an'
- ends with: 'original payment method in accordance with Section 6.\n\n---\n\n'

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

### Chunk 5

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 5
- character count: 795
- source character range: [3653:4448]
- section heading: ## 5. Cancellation During Shipment Processing
- starts with: '## 5. Cancellation During Shipment Processing\n\nIf an order h'
- ends with: ' 7, including the fee-waiver conditions in Section 3.\n\n---\n\n'

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

### Chunk 6

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 6
- character count: 836
- source character range: [4448:5284]
- section heading: ## 6. Refund Processing
- starts with: '## 6. Refund Processing\n\nApproved refunds are returned to th'
- ends with: 'rmined by the card issuer, bank, or payment provider.\n\n---\n\n'

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

### Chunk 7

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 7
- character count: 1187
- source character range: [5284:6471]
- section heading: ## 7. Cancellation After Shipment
- starts with: '## 7. Cancellation After Shipment\n\nCancellation after shipme'
- ends with: ' by itself does not stop an order already in transit.\n\n---\n\n'

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

### Chunk 8

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 8
- character count: 1618
- source character range: [6471:8089]
- section heading: ## 8. Shipping Charges
- starts with: '## 8. Shipping Charges\n\nOriginal shipping charges are genera'
- ends with: 'nother section, the detailed policy language governs.\n\n---\n\n'

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

### Chunk 9

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 9
- character count: 642
- source character range: [8089:8731]
- section heading: ## 9. Subscription Cancellation
- starts with: '## 9. Subscription Cancellation\n\nSubscription customers may '
- ends with: 'Section 7 do not apply to subscription cancellations.\n\n---\n\n'

````text
## 9. Subscription Cancellation

Subscription customers may cancel future renewals at any time.

Cancellation:

- stops future billing
- does not automatically refund charges already processed
- does not affect physical-order restocking rules

The subscription remains active until the end of the current paid billing period unless TechNova approves an earlier termination. Cancelling a subscription does not cancel an open physical-product order.

TechNova may issue a subscription refund for a duplicate charge, billing error, or other verified issue. The restocking-fee rules in Section 7 do not apply to subscription cancellations.

---


````

### Chunk 10

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 10
- character count: 696
- source character range: [8731:9427]
- section heading: ## 10. Promotional Orders
- starts with: '## 10. Promotional Orders\n\nPromotional discounts do not chan'
- ends with: ' not reinstate an expired promotion or discount code.\n\n---\n\n'

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

### Chunk 11

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 11
- character count: 663
- source character range: [9427:10090]
- section heading: ## 11. Business Orders
- starts with: '## 11. Business Orders\n\nBusiness orders containing more than'
- ends with: 'itting a cancellation, refund, or fee-waiver request.\n\n---\n\n'

````text
## 11. Business Orders

Business orders containing more than 25 units may be subject to separate contract terms.

If a signed business agreement conflicts with this policy, the signed agreement takes precedence.

TechNova may require additional review for orders involving volume pricing, custom configurations, staged delivery, or purchase orders. Those orders may have different cancellation deadlines, restocking fees, or return requirements.

If no signed business agreement applies, this policy governs the order. Business customers should include their organization name and order number when submitting a cancellation, refund, or fee-waiver request.

---


````

### Chunk 12

- strategy: C. Markdown section-aware (## headings, natural length)
- chunk index: 12
- character count: 759
- source character range: [10090:10849]
- section heading: ## 12. Policy Interpretation
- starts with: '## 12. Policy Interpretation\n\nWhen a cancellation depends on'
- ends with: 'ction 8.\n5. Calculate and issue the refund under Section 6.\n'

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

