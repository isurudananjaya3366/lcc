# Credit & Loyalty Module (`apps.credit`)

Customer credit management, loyalty points programs, store credit, and promotions for LankaCommerce Cloud POS.

## Overview

This module implements **SP09: Customer Credit & Loyalty** — a comprehensive credit and loyalty system covering:

- **Customer Credit Accounts** — Credit limits, terms, interest, aging, and suspension
- **Credit Transactions** — Purchase/payment audit trail with reversal support
- **Loyalty Programs** — Points-based programs with configurable earn/redeem rules
- **Loyalty Tiers** — Silver/Gold/Platinum tier progression with benefits
- **Points Transactions** — Full points audit trail with FIFO expiry
- **Loyalty Rewards** — Configurable rewards catalog
- **Store Credit** — Gift/promo credits with expiry and redemption
- **Points Promotions** — Multiplier, flat bonus, category bonus promotions

## Architecture

```
apps/credit/
├── models/               # 13 Django models (UUID PKs, soft-delete)
│   ├── customer_credit.py
│   ├── credit_settings.py
│   ├── credit_approval.py
│   ├── credit_transaction.py
│   ├── loyalty_program.py
│   ├── loyalty_tier.py
│   ├── customer_loyalty.py
│   ├── points_transaction.py
│   ├── loyalty_reward.py
│   ├── store_credit.py
│   └── points_promotion.py
├── services/             # Business logic layer
│   ├── credit_service.py
│   ├── loyalty_service.py
│   ├── tier_service.py
│   ├── store_credit_service.py
│   └── promotion_service.py
├── serializers/          # DRF serializers
│   ├── credit_serializer.py
│   └── loyalty_serializer.py
├── views/                # DRF viewsets
│   ├── credit_viewset.py
│   ├── loyalty_viewset.py
│   ├── store_credit_viewset.py
│   └── dashboard_views.py
├── tasks/                # Celery async tasks
│   ├── credit_tasks.py
│   ├── expiry_tasks.py
│   ├── tier_tasks.py
│   └── reward_tasks.py
├── filters.py            # django-filter FilterSets
├── urls.py               # DRF router + URL config
├── constants.py          # Enums and choices
├── signals.py            # Post-save signals
├── admin.py              # Django admin registration
└── apps.py               # App config
```

## API Endpoints

| Method               | URL                                       | Description                  |
| -------------------- | ----------------------------------------- | ---------------------------- |
| GET/POST             | `/api/v1/credit/`                         | List/create credit accounts  |
| GET/PUT/PATCH/DELETE | `/api/v1/credit/{id}/`                    | Credit account detail        |
| GET                  | `/api/v1/credit/{id}/transactions/`       | Transaction history          |
| GET                  | `/api/v1/credit/{id}/aging-report/`       | Aging buckets                |
| GET                  | `/api/v1/credit/statistics/`              | Aggregate statistics         |
| POST                 | `/api/v1/credit/{id}/approve/`            | Approve account (admin)      |
| POST                 | `/api/v1/credit/{id}/suspend/`            | Suspend account (admin)      |
| POST                 | `/api/v1/credit/{id}/adjust-limit/`       | Adjust credit limit (admin)  |
| POST                 | `/api/v1/credit/{id}/write-off/`          | Write off balance (admin)    |
| POST                 | `/api/v1/credit/{id}/record-payment/`     | Record payment               |
| GET/POST             | `/api/v1/loyalty/`                        | List/create loyalty accounts |
| GET/PUT/PATCH/DELETE | `/api/v1/loyalty/{id}/`                   | Loyalty account detail       |
| GET                  | `/api/v1/loyalty/{id}/points-history/`    | Points transaction history   |
| GET                  | `/api/v1/loyalty/{id}/tier-progress/`     | Tier progression status      |
| GET                  | `/api/v1/loyalty/dashboard/`              | Loyalty statistics           |
| POST                 | `/api/v1/loyalty/{id}/award-points/`      | Award points                 |
| POST                 | `/api/v1/loyalty/{id}/redeem-points/`     | Redeem points                |
| POST                 | `/api/v1/loyalty/{id}/upgrade-tier/`      | Upgrade tier (admin)         |
| GET                  | `/api/v1/loyalty/{id}/tier-eligibility/`  | Check tier eligibility       |
| GET                  | `/api/v1/loyalty/{id}/points-forecast/`   | Points forecast              |
| GET                  | `/api/v1/store-credit/`                   | List store credits           |
| GET                  | `/api/v1/store-credit/{id}/`              | Store credit detail          |
| GET                  | `/api/v1/store-credit/{id}/balance/`      | Check balance                |
| GET                  | `/api/v1/store-credit/{id}/transactions/` | Transaction history          |
| POST                 | `/api/v1/store-credit/{id}/issue/`        | Issue credit (admin)         |
| POST                 | `/api/v1/store-credit/{id}/redeem/`       | Redeem credit                |
| GET                  | `/api/v1/dashboard/`                      | Credit & Loyalty dashboard   |

## Services

### CreditService

Manages credit purchases, payments, balance calculations, aging analysis, interest, and account suspension.

### LoyaltyService

Handles customer enrollment, points calculation, awarding, redemption, and FIFO expiry.

### TierService

Evaluates tier eligibility, upgrades/downgrades, and provides tier progress tracking.

### StoreCreditService

Issues, redeems, and tracks store credit balances with expiry management.

### PromotionService

Fetches active promotions and calculates bonus points including multipliers and category bonuses.

## Celery Tasks

- `send_credit_payment_reminders` — Daily payment reminders for overdue accounts
- `calculate_credit_interest` — Monthly interest calculation
- `check_credit_auto_suspensions` — Daily auto-suspension check
- `expire_loyalty_points` — Daily FIFO points expiry
- `evaluate_customer_tiers` — Weekly tier evaluation
- `process_birthday_rewards` — Daily birthday reward processing
- `process_anniversary_rewards` — Daily anniversary reward processing

## Filters

- **CreditFilterSet** — Status, balance range, customer, overdue flag
- **LoyaltyFilterSet** — Status, program, tier, points range, enrollment date
- **StoreCreditFilterSet** — Source, balance range, expired/expiring flags

## Migrations

| Migration | Description                                                        |
| --------- | ------------------------------------------------------------------ |
| 0001      | CustomerCredit, CreditSettings, CreditApprovalWorkflow             |
| 0002      | CreditTransaction                                                  |
| 0003      | LoyaltyProgram, LoyaltyTier, CustomerLoyalty, PointsTransaction    |
| 0004      | LoyaltyTier expanded, LoyaltyReward, CustomerLoyalty reward fields |
| 0005      | StoreCredit, StoreCreditTransaction, PointsPromotion               |

## Testing

```bash
docker compose exec backend pytest tests/credit/ -v --skip-checks
```
