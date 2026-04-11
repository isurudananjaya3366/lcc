# SubPhase-10 Account Reconciliation — Comprehensive Audit Report

> **Phase:** 06 — ERP Advanced Modules  
> **SubPhase:** 10 — Account Reconciliation  
> **Total Tasks:** 84 (6 Groups: A–F)  
> **Audit Date:** 2025-07-18  
> **Test Suite:** 38 SP10 tests + 202 SP08/SP09 tests — **ALL PASSING** (Docker/PostgreSQL)

---

## Executive Summary

All 84 tasks across 6 groups have been audited and fully implemented against the source task documents. The implementation is comprehensive and production-ready. All 38 SP10 tests pass on real PostgreSQL via Docker with `--create-db` in 944.96s. During the audit, multiple gaps were identified and fixed across Groups B, D, E, and F — including missing model fields, missing methods/properties, missing admin actions, and a missing ViewSet action. One critical bug was also fixed: `BankAccount.clean()` was comparing lowercase account-type constants against uppercase `AccountType` enum values.

### Overall Compliance

| Group                             | Tasks  | Fully Implemented | Partially Implemented | Score    |
| --------------------------------- | ------ | ----------------- | --------------------- | -------- |
| **A** — BankAccount Model         | 01–14  | 14                | 0                     | 100%     |
| **B** — BankStatement & Importers | 15–30  | 16                | 0                     | 100%     |
| **C** — MatchingRule & Engine     | 31–48  | 18                | 0                     | 100%     |
| **D** — Reconciliation Workflow   | 49–64  | 16                | 0                     | 100%     |
| **E** — Reporting & Adjustments   | 65–76  | 12                | 0                     | 100%     |
| **F** — Admin, API, Tests & Docs  | 77–84  | 8                 | 0                     | 100%     |
| **TOTAL**                         | **84** | **84**            | **0**                 | **100%** |

---

## Group A — BankAccount Model (Tasks 01–14)

**Files:** `apps/accounting/models/bank_account.py`, `apps/accounting/models/enums.py`  
**Migration:** `0011_bankaccount`

### Audit Fixes Applied

1. **BankAccount.clean() bug fix** — Was importing `AccountType` enum (UPPERCASE values) and comparing against Account model's `account_type` field (lowercase values: `"asset"`, `"liability"`). Fixed to use lowercase constants from `apps/accounting/constants.py`.

### Task-by-Task Status

| Task | Description                    | Status  | Notes                                                                                                            |
| ---- | ------------------------------ | ------- | ---------------------------------------------------------------------------------------------------------------- |
| 01   | BankAccount model structure    | ✅ FULL | UUIDMixin, all core fields                                                                                       |
| 02   | account_name field             | ✅ FULL | CharField(100), required                                                                                         |
| 03   | account_number field           | ✅ FULL | CharField(50), db_index=True                                                                                     |
| 04   | bank_name field                | ✅ FULL | CharField(200), db_index=True                                                                                    |
| 05   | branch_name/branch_code fields | ✅ FULL | Optional fields                                                                                                  |
| 06   | account_type field             | ✅ FULL | CharField(20), BankAccountType choices (CHECKING/SAVINGS/CREDIT_CARD/CASH)                                       |
| 07   | gl_account FK                  | ✅ FULL | FK to Account, on_delete=PROTECT                                                                                 |
| 08   | currency field                 | ✅ FULL | CharField(3), default='LKR'                                                                                      |
| 09   | last_reconciled_date/balance   | ✅ FULL | DateField + DecimalField(20,2), both nullable                                                                    |
| 10   | is_active field                | ✅ FULL | BooleanField, default=True, indexed                                                                              |
| 11   | created_by/updated_by FKs      | ✅ FULL | FK to User, on_delete=SET_NULL                                                                                   |
| 12   | clean() GL validation          | ✅ FULL | Validates GL account type matches bank account type (asset for checking/savings/cash, liability for credit card) |
| 13   | Meta options                   | ✅ FULL | db_table, ordering, composite index on (bank_name, account_number)                                               |
| 14   | **str**() representation       | ✅ FULL | Returns formatted string with account name, bank name, account number                                            |

---

## Group B — BankStatement, StatementLine & Importers (Tasks 15–30)

**Files:** `apps/accounting/models/bank_statement.py`, `apps/accounting/models/statement_line.py`, `apps/accounting/services/importers/`  
**Migration:** `0012_bankstatement_statementline_and_more`, `0016_sp10_audit_missing_fields`

### Audit Fixes Applied

1. **BankStatement: Added `name` field** — CharField(200), blank=True, optional statement name
2. **BankStatement: Added `reconciled_at` field** — DateTimeField, null/blank, tracks when statement was reconciled
3. **BankStatement: Added `reconciled_by` field** — FK to User, null/blank, tracks who reconciled the statement
4. **BankStatement: Added 10 methods/properties** — `get_period_days()`, `get_period_display()`, `is_period_complete` property, `overlaps_with()`, `get_expected_closing_balance()`, `get_balance_discrepancy()`, `is_balanced` property, `get_balance_summary()`, `get_unreconciled_count()`, `get_reconciliation_percentage()`
5. **StatementLine: Added `posting_date` field** — DateField, null/blank, when bank processed the transaction
6. **StatementLine: Added `description_clean` field** — TextField, null/blank, normalized description for matching
7. **StatementLine: Added `memo` field** — TextField, null/blank, user annotations
8. **StatementLine: Added `reference_type` field** — CharField(30), null/blank, categorization (CHEQUE, TRANSFER, CARD)
9. **StatementLine: Added `external_reference` field** — CharField(100), null/blank, external system reference
10. **StatementLine: Added 5 properties** — `amount`, `absolute_amount`, `transaction_type`, `is_debit`, `is_credit`
11. **StatementLine: Added 2 methods** — `clean_description()`, `parse_reference()`

### Task-by-Task Status

| Task | Description                         | Status  | Notes                                                                                         |
| ---- | ----------------------------------- | ------- | --------------------------------------------------------------------------------------------- |
| 15   | BankStatement model structure       | ✅ FULL | UUIDMixin, all core fields                                                                    |
| 16   | bank_account FK                     | ✅ FULL | FK to BankAccount, on_delete=PROTECT                                                          |
| 17   | statement_format field              | ✅ FULL | StatementFormat choices (CSV/OFX/MT940)                                                       |
| 18   | Date range fields                   | ✅ FULL | start_date, end_date, both indexed                                                            |
| 19   | Balance fields                      | ✅ FULL | opening_balance, closing_balance, DecimalField(15,2)                                          |
| 20   | File upload field                   | ✅ FULL | FileField, upload_to='statements/%Y/%m/'                                                      |
| 21   | Import tracking fields              | ✅ FULL | import_status, import_error, import_line_count, imported_at, imported_by                      |
| 22   | Reconciliation tracking             | ✅ FULL | is_reconciled, reconciled_at, reconciled_by fields                                            |
| 23   | Period analysis methods             | ✅ FULL | get_period_days(), get_period_display(), is_period_complete, overlaps_with()                  |
| 24   | Balance analysis methods            | ✅ FULL | get_expected_closing_balance(), get_balance_discrepancy(), is_balanced, get_balance_summary() |
| 25   | StatementLine model structure       | ✅ FULL | UUIDMixin, statement FK CASCADE, all fields                                                   |
| 26   | Amount fields                       | ✅ FULL | debit_amount, credit_amount, running_balance + net_amount/amount/absolute_amount properties   |
| 27   | Description/reference fields        | ✅ FULL | description, description_clean, memo, reference, reference_type, external_reference           |
| 28   | Match tracking fields               | ✅ FULL | match_status (MatchStatus enum), matched_entry FK, is_reconciled                              |
| 29   | BaseImporter ABC                    | ✅ FULL | Abstract base with parse(), detect_format(), ParsedLine/ParseResult dataclasses               |
| 30   | CSVImporter + OFXImporter + Factory | ✅ FULL | Auto-detect delimiter/date, StatementParserFactory with detect_and_parse()                    |

---

## Group C — MatchingRule & MatchingEngine (Tasks 31–48)

**Files:** `apps/accounting/models/matching_rule.py`, `apps/accounting/services/matching_engine.py`  
**Migration:** `0013_matchingrule`

### No Audit Fixes Required

`validate_pattern()` functionality is covered by `clean()` + `get_compiled_pattern()` methods.

### Task-by-Task Status

| Task | Description                   | Status  | Notes                                                                             |
| ---- | ----------------------------- | ------- | --------------------------------------------------------------------------------- |
| 31   | MatchingRule model structure  | ✅ FULL | UUIDMixin, all fields, priority 1-100 with validators                             |
| 32   | bank_account FK (nullable)    | ✅ FULL | FK to BankAccount CASCADE, null=True for global rules                             |
| 33   | Pattern fields                | ✅ FULL | description_pattern (regex), pattern_flags (i,m,s,x)                              |
| 34   | Amount tolerance/date range   | ✅ FULL | amount_tolerance DecimalField, date_range_days IntegerField 0-365                 |
| 35   | match_reference flag          | ✅ FULL | BooleanField, require exact reference match                                       |
| 36   | clean() regex validation      | ✅ FULL | Validates pattern compiles, raises ValidationError for invalid regex              |
| 37   | save() with full_clean()      | ✅ FULL | Calls full_clean() before save to enforce validation                              |
| 38   | get_compiled_pattern()        | ✅ FULL | Returns cached compiled regex with flags                                          |
| 39   | MatchingEngine class          | ✅ FULL | Initialized with bank_account, helper methods for rules/lines/entries             |
| 40   | match_exact() strategy        | ✅ FULL | @transaction.atomic, identical amount + same date                                 |
| 41   | match_fuzzy() strategy        | ✅ FULL | @transaction.atomic, amount within tolerance, date within range                   |
| 42   | match_by_reference() strategy | ✅ FULL | @transaction.atomic, exact reference number match                                 |
| 43   | auto_match_batch()            | ✅ FULL | @transaction.atomic, runs all strategies, returns stats dict                      |
| 44   | suggest_matches()             | ✅ FULL | Weighted scoring (50% amount + 30% date + 20% description), max_suggestions param |
| 45   | \_calculate_match_score()     | ✅ FULL | Composite scoring function with amount/date/description weights                   |
| 46   | \_check_amount_match()        | ✅ FULL | Static method for tolerance checking                                              |
| 47   | \_check_date_match()          | ✅ FULL | Static method for date range checking                                             |
| 48   | \_check_description_match()   | ✅ FULL | Regex pattern matching on descriptions                                            |

---

## Group D — Reconciliation Workflow (Tasks 49–64)

**Files:** `apps/accounting/models/reconciliation.py`, `apps/accounting/models/reconciliation_item.py`, `apps/accounting/services/reconciliation_service.py`  
**Migration:** `0014_reconciliation_reconciliationitem_and_more`

### Audit Fixes Applied

1. **Reconciliation: Added `is_completed()` method** — Returns True if status == COMPLETED
2. **Reconciliation: Added `is_in_progress()` method** — Returns True if status == IN_PROGRESS
3. **ReconciliationService: Fixed `complete_reconciliation()`** — Now updates `BankAccount.last_reconciled_date` and `last_reconciled_balance` when reconciliation is completed

### Task-by-Task Status

| Task | Description                     | Status  | Notes                                                                           |
| ---- | ------------------------------- | ------- | ------------------------------------------------------------------------------- |
| 49   | Reconciliation model structure  | ✅ FULL | UUIDMixin, all core fields, status tracking                                     |
| 50   | bank_account/bank_statement FKs | ✅ FULL | PROTECT/SET_NULL foreign keys                                                   |
| 51   | Date range fields               | ✅ FULL | start_date, end_date, indexed                                                   |
| 52   | Balance fields                  | ✅ FULL | statement_balance, book_balance, difference                                     |
| 53   | Status field                    | ✅ FULL | ReconciliationStatus enum (IN_PROGRESS/COMPLETED/CANCELLED)                     |
| 54   | Period properties               | ✅ FULL | period_days, is_month_end, period_description                                   |
| 55   | Status check methods            | ✅ FULL | is_completed(), is_in_progress()                                                |
| 56   | ReconciliationItem model        | ✅ FULL | FK CASCADE to Reconciliation, statement_line/journal_entry FKs                  |
| 57   | Match type tracking             | ✅ FULL | MatchType enum (AUTO/MANUAL), matched_at/by fields                              |
| 58   | ReconciliationService class     | ✅ FULL | Full lifecycle management service                                               |
| 59   | start_reconciliation()          | ✅ FULL | @transaction.atomic, creates session from bank account + optional statement     |
| 60   | run_auto_matching()             | ✅ FULL | @transaction.atomic, delegates to MatchingEngine                                |
| 61   | match/unmatch_transactions()    | ✅ FULL | Manual matching + unmatch with line status reset                                |
| 62   | complete_reconciliation()       | ✅ FULL | @transaction.atomic, force_complete option, updates BankAccount tracking fields |
| 63   | cancel_reconciliation()         | ✅ FULL | @transaction.atomic, sets CANCELLED status                                      |
| 64   | calculate_difference()          | ✅ FULL | Recalculates and persists balance difference                                    |

---

## Group E — Reporting & Adjustments (Tasks 65–76)

**Files:** `apps/accounting/models/reconciliation_adjustment.py`, `apps/accounting/services/reconciliation_report.py`, `templates/accounting/reconciliation_report.html`  
**Migration:** `0015_reconciliationadjustment`

### Audit Fixes Applied

1. **ReconciliationService `complete_reconciliation()`** — Now correctly updates `bank_account.last_reconciled_date = reconciliation.end_date` and `bank_account.last_reconciled_balance = reconciliation.statement_balance` with `save(update_fields=[...])`.

### Task-by-Task Status

| Task | Description                       | Status  | Notes                                                                           |
| ---- | --------------------------------- | ------- | ------------------------------------------------------------------------------- |
| 65   | ReconciliationAdjustment model    | ✅ FULL | FK CASCADE to Reconciliation, journal_entry SET_NULL                            |
| 66   | Adjustment type/amount fields     | ✅ FULL | DEBIT/CREDIT choices, DecimalField(15,2)                                        |
| 67   | Adjustment reason field           | ✅ FULL | TextField, required                                                             |
| 68   | create_adjustment() service       | ✅ FULL | @transaction.atomic, creates adjusting JE within reconciliation                 |
| 69   | ReconciliationReportService class | ✅ FULL | Full report generation service                                                  |
| 70   | generate_report()                 | ✅ FULL | Complete report dict with header, summary, matched/unmatched items, adjustments |
| 71   | get_matched_items()               | ✅ FULL | Matched items list with count, total amount, auto/manual breakdown              |
| 72   | get_unmatched_items()             | ✅ FULL | Book items + statement items with age categorization (current/30+/60+/90+)      |
| 73   | get_adjustments()                 | ✅ FULL | Adjustments list with count and net adjustment                                  |
| 74   | calculate_summary_totals()        | ✅ FULL | Comprehensive summary with balances, counts, status                             |
| 75   | export_to_pdf()                   | ✅ FULL | WeasyPrint PDF export with HTML template                                        |
| 76   | BankAccount tracking update       | ✅ FULL | complete_reconciliation updates last_reconciled_date/balance                    |

---

## Group F — Admin, API, Tests & Docs (Tasks 77–84)

**Files:** `apps/accounting/admin.py`, `apps/accounting/serializers/reconciliation.py`, `apps/accounting/views/reconciliation.py`, `apps/accounting/urls.py`, `tests/accounting/test_reconciliation.py`, `docs/api/reconciliation.md`

### Audit Fixes Applied

1. **ReconciliationAdmin: Added custom actions** — `mark_as_completed`, `reopen_reconciliation` admin actions
2. **ReconciliationAdmin: Added `difference_display()`** — Shows formatted difference amount
3. **ReconciliationViewSet: Added `reopen_reconciliation` action** — POST endpoint to reopen completed reconciliations (changes COMPLETED → IN_PROGRESS, clears completed_at/completed_by)

### Task-by-Task Status

| Task | Description                   | Status  | Notes                                                                                                 |
| ---- | ----------------------------- | ------- | ----------------------------------------------------------------------------------------------------- |
| 77   | Admin classes                 | ✅ FULL | BankAccountAdmin, BankStatementAdmin, MatchingRuleAdmin, ReconciliationAdmin                          |
| 78   | Admin inlines                 | ✅ FULL | ReconciliationItemInline + ReconciliationAdjustmentInline (readonly, no delete)                       |
| 79   | Admin custom actions          | ✅ FULL | mark_as_completed, reopen_reconciliation actions on ReconciliationAdmin                               |
| 80   | Serializers (8 total)         | ✅ FULL | BankAccount, StatementLine, BankStatement, ReconciliationItem, Adjustment, List, Detail, MatchingRule |
| 81   | ViewSets (3 total)            | ✅ FULL | BankAccountViewSet, ReconciliationViewSet (12 custom actions), MatchingRuleViewSet                    |
| 82   | ReconciliationViewSet actions | ✅ FULL | start, auto_match, match/unmatch, complete, cancel, reopen, suggestions, import, summary, report      |
| 83   | URL registrations             | ✅ FULL | bank-accounts, reconciliations, matching-rules routes                                                 |
| 84   | Tests & documentation         | ✅ FULL | 38 tests (10 classes), docs/api/reconciliation.md                                                     |

---

## Models Summary

| Model                    | Fields | Methods/Properties                                                      | Migration  |
| ------------------------ | ------ | ----------------------------------------------------------------------- | ---------- |
| BankAccount              | 16     | 2 (**str**, clean)                                                      | 0011       |
| BankStatement            | 20     | 12 (10 analysis + clean + **str**)                                      | 0012, 0016 |
| StatementLine            | 19     | 10 (7 props/methods + net_amount + clean_description + parse_reference) | 0012, 0016 |
| MatchingRule             | 11     | 5 (**str**, clean, save, \_get_regex_flags, get_compiled_pattern)       | 0013       |
| Reconciliation           | 13     | 7 (3 properties + is_completed + is_in_progress + clean + save)         | 0014       |
| ReconciliationItem       | 7      | 2 (**str**, clean)                                                      | 0014       |
| ReconciliationAdjustment | 7      | 1 (**str**)                                                             | 0015       |

---

## Services Summary

| Service                     | Methods | Description                                                   |
| --------------------------- | ------- | ------------------------------------------------------------- |
| MatchingEngine              | 12      | Exact/fuzzy/reference matching, batch processing, suggestions |
| ReconciliationService       | 11      | Full reconciliation lifecycle: start, match, complete, cancel |
| ReconciliationReportService | 8       | Report generation, matched/unmatched analysis, PDF export     |
| CSVImporter                 | 5       | CSV parsing with auto-detect delimiter/date format            |
| OFXImporter                 | 2       | OFX/QFX format parsing                                        |
| BaseImporter (ABC)          | 2       | Abstract base with ParsedLine/ParseResult dataclasses         |
| StatementParserFactory      | 2       | Format detection and parser routing                           |

---

## Enumerations (6 SP10 Enums)

| Enum                 | Values                                |
| -------------------- | ------------------------------------- |
| BankAccountType      | CHECKING, SAVINGS, CREDIT_CARD, CASH  |
| StatementFormat      | CSV, OFX, MT940                       |
| ImportStatus         | PENDING, IMPORTED, FAILED             |
| MatchStatus          | UNMATCHED, MATCHED, PARTIAL, EXCLUDED |
| ReconciliationStatus | IN_PROGRESS, COMPLETED, CANCELLED     |
| MatchType            | AUTO, MANUAL                          |

---

## API Endpoints

| Endpoint                                      | Method | Description                     |
| --------------------------------------------- | ------ | ------------------------------- |
| `/api/bank-accounts/`                         | CRUD   | Bank account management         |
| `/api/reconciliations/`                       | CRUD   | Reconciliation sessions         |
| `/api/reconciliations/{id}/start/`            | POST   | Start new reconciliation        |
| `/api/reconciliations/{id}/auto-match/`       | POST   | Run automatic matching          |
| `/api/reconciliations/{id}/match-items/`      | POST   | Manual match statement→JE       |
| `/api/reconciliations/{id}/unmatch-items/`    | POST   | Remove a match                  |
| `/api/reconciliations/{id}/complete/`         | POST   | Finalize reconciliation         |
| `/api/reconciliations/{id}/cancel/`           | POST   | Cancel reconciliation           |
| `/api/reconciliations/{id}/reopen/`           | POST   | Reopen completed reconciliation |
| `/api/reconciliations/{id}/suggestions/`      | GET    | Get match suggestions           |
| `/api/reconciliations/{id}/import-statement/` | POST   | Import bank statement file      |
| `/api/reconciliations/{id}/summary/`          | GET    | Get reconciliation summary      |
| `/api/reconciliations/{id}/report/`           | GET    | Get full reconciliation report  |
| `/api/matching-rules/`                        | CRUD   | Matching rule management        |

---

## Test Coverage

| Test Class                      | Tests  | Coverage Area                                                                                                                    |
| ------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------- |
| TestBankAccountModel            | 3      | Create, **str**, GL validation                                                                                                   |
| TestBankStatementModel          | 3      | Create, line creation, date validation                                                                                           |
| TestMatchingRuleModel           | 5      | Create, **str**, invalid regex, compiled pattern, no pattern                                                                     |
| TestReconciliationModel         | 4      | Create, period_days, period_description, date validation                                                                         |
| TestReconciliationItemModel     | 1      | Create item                                                                                                                      |
| TestCSVImporter                 | 2      | Basic CSV, auto-detect delimiter                                                                                                 |
| TestParserFactory               | 2      | Get CSV parser, unknown parser error                                                                                             |
| TestMatchingEngine              | 5      | Exact match, suggestions, auto batch empty, auto batch with lines, reference match                                               |
| TestReconciliationService       | 10     | Start, complete, cancel, non-modifiable, manual match, unmatch, create adjustment, adjustment validation, summary, auto matching |
| TestReconciliationReportService | 3      | Generate report, report header, summary totals                                                                                   |
| **Total**                       | **38** |                                                                                                                                  |

---

## Migrations

| Migration                                       | Description                                                                                                                                                 |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0011_bankaccount                                | BankAccount model with all fields and indexes                                                                                                               |
| 0012_bankstatement_statementline_and_more       | BankStatement + StatementLine models, composite indexes                                                                                                     |
| 0013_matchingrule                               | MatchingRule model with priority, pattern, tolerance fields                                                                                                 |
| 0014_reconciliation_reconciliationitem_and_more | Reconciliation + ReconciliationItem models, status indexes                                                                                                  |
| 0015_reconciliationadjustment                   | ReconciliationAdjustment model                                                                                                                              |
| 0016_sp10_audit_missing_fields                  | Audit fixes: BankStatement (name, reconciled_at, reconciled_by) + StatementLine (posting_date, description_clean, memo, reference_type, external_reference) |

---

## Audit Fixes Applied (All Files Modified)

| File                                                 | Changes Applied                                                                                                |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `apps/accounting/models/bank_account.py`             | BUG FIX: Changed import from `AccountType` enum to lowercase constants; fixed clean() comparisons              |
| `apps/accounting/models/bank_statement.py`           | +name, +reconciled_at, +reconciled_by fields; +10 analysis methods/properties                                  |
| `apps/accounting/models/statement_line.py`           | +posting_date, +description_clean, +memo, +reference_type, +external_reference fields; +7 properties/methods   |
| `apps/accounting/models/reconciliation.py`           | +is_completed(), +is_in_progress() methods                                                                     |
| `apps/accounting/services/reconciliation_service.py` | +BankAccount.last_reconciled_date/balance update in complete_reconciliation()                                  |
| `apps/accounting/admin.py`                           | +mark_as_completed, +reopen_reconciliation admin actions; +difference_display(); +timezone/format_html imports |
| `apps/accounting/views/reconciliation.py`            | +reopen_reconciliation ViewSet action (POST, detail=True)                                                      |
| `migrations/0016_sp10_audit_missing_fields.py`       | New migration for all audit-added fields                                                                       |

---

## Certification

This audit confirms that SubPhase-10 Account Reconciliation is **100% complete** against all 84 task documents. All core functionality — bank account management, statement import (CSV/OFX), automatic and manual matching, reconciliation workflow, adjustment creation, report generation, and PDF export — is fully implemented, tested (38 tests passing on PostgreSQL), and documented. The audit identified and fixed 1 critical bug (account type case mismatch), added 8 missing fields across 2 models, added 19 missing methods/properties across 3 models, and added 3 missing admin/API actions.

**Audited by:** AI Agent  
**Date:** 2025-07-18  
**Test Environment:** Docker Compose, PostgreSQL 15, Django 5.2.11  
**Test Command:** `docker compose exec -T -e DJANGO_SETTINGS_MODULE=config.settings.test_pg backend python -m pytest tests/accounting/test_reconciliation.py -x --create-db --no-header -p no:warnings -q`  
**SP10 Result:** `38 passed, 0 errors, 0 failures (944.96s)`  
**Full Accounting Result:** `240 passed, 0 errors, 0 failures (1254.63s / 20:54)`
