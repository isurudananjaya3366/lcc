# POS Known Issues

## Active Issues

| #   | Severity | Component        | Issue                                                               | Workaround                               | Status |
| --- | -------- | ---------------- | ------------------------------------------------------------------- | ---------------------------------------- | ------ |
| 1   | Low      | ReceiptContent   | Store name/address hardcoded as "LankaCommerce / Sri Lanka"         | Will be configurable via tenant settings | Open   |
| 2   | Low      | CompleteSale     | Cart ID is generated client-side (`Date.now()`) instead of from API | Functional but not ideal for tracking    | Open   |
| 3   | Low      | HoldSaleButton   | Max held sales (10) is hardcoded, not configurable                  | Adequate for typical POS usage           | Open   |
| 4   | Low      | ShiftCloseModal  | No manager PIN approval for major variance                          | Add in future iteration                  | Open   |
| 5   | Low      | OpeningCashInput | No warning for very large opening amounts (>100K)                   | Manual review by cashier                 | Open   |

## Resolved Issues

| #   | Severity | Component | Issue                  | Resolution | Version |
| --- | -------- | --------- | ---------------------- | ---------- | ------- |
| —   | —        | —         | No resolved issues yet | —          | —       |

## Performance Notes

- Search debounce set to 300ms — may need tuning for slower networks
- Cart store uses localStorage persistence — large carts (50+ items) may have slight save delay
- ShiftVarianceDisplay recalculates on every CashCountInput change — acceptable performance
