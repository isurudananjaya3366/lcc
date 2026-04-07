# LankaCommerce Cloud - Commit Message Conventions

<!-- =================================================================
     COMMITS.md - LankaCommerce Cloud (LCC)
     Conventional Commits specification (v1.0.0)
     ================================================================= -->

## Table of Contents

- [Overview](#overview)
- [Why Conventional Commits?](#why-conventional-commits)
- [Quick Reference](#quick-reference)
- [Commit Message Format](#commit-message-format)
- [Commit Types](#commit-types)
- [Scope Guidelines](#scope-guidelines)
- [Subject Guidelines](#subject-guidelines)
- [Body Guidelines](#body-guidelines)
- [Footer Guidelines](#footer-guidelines)
- [Commit Examples](#commit-examples)
- [Using Commitizen](#using-commitizen)

---

## Overview

LankaCommerce Cloud follows the **Conventional Commits** specification (v1.0.0)
for all commit messages. This ensures consistent, meaningful commit history
that can be used for automated changelog generation and semantic versioning.

**Specification URL:** <https://www.conventionalcommits.org/en/v1.0.0/>

---

## Why Conventional Commits?

| Benefit             | Description                        |
| ------------------- | ---------------------------------- |
| Consistent history  | Readable, structured commit log    |
| Automation          | Automated changelog and versioning |
| Clear intent        | Purpose of change is obvious       |
| Better reviews      | Easier to review organized commits |
| Semantic versioning | Automatic version bumping          |

| Feature           | Benefit                    |
| ----------------- | -------------------------- |
| Structured format | Machine and human readable |
| Type prefixes     | Quick intent understanding |
| Scope context     | Know what changed          |
| Automation        | CHANGELOG generation       |

---

## Quick Reference

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**

```
feat(auth): add JWT token refresh endpoint

Implement automatic token refresh functionality to prevent
users from being logged out unexpectedly.

Closes #123
```

---

## Commit Message Format

### Structure

Every commit message consists of three parts:

```
<header>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

### Header Format

```
<type>(<scope>): <subject>
```

**Components:**

- `type` - **Required.** The type of change.
- `scope` - **Optional.** The affected module/component.
- `subject` - **Required.** Brief description of the change.

### Rules

| Component | Rule                               |
| --------- | ---------------------------------- |
| Header    | Maximum 72 characters              |
| Header    | No period at end                   |
| Body      | Wrap at 72 characters              |
| Body      | Separate from header by blank line |
| Footer    | Reference issues, breaking changes |

### Character Limits

```
Header:  <=72 characters (recommended: 50)
Body:    Wrap at 72 characters per line
Footer:  No limit, but be concise
```

### Format Breakdown

| Part    | Required | Purpose                      |
| ------- | -------- | ---------------------------- |
| Type    | Yes      | Change category              |
| Scope   | No       | Affected area                |
| Subject | Yes      | Brief description            |
| Body    | No       | Detailed explanation         |
| Footer  | No       | References, breaking changes |

### Anatomy Example

```
feat(products): add bulk import functionality
│    │          │
│    │          └─► Subject: imperative, present tense
│    │
│    └─► Scope: affected module
│
└─► Type: category of change
```

---

## Commit Types

### Allowed Types

| Type       | Description             | Version Bump |
| ---------- | ----------------------- | ------------ |
| `feat`     | New feature             | MINOR        |
| `fix`      | Bug fix                 | PATCH        |
| `docs`     | Documentation only      | None         |
| `style`    | Formatting, whitespace  | None         |
| `refactor` | Code restructuring      | None         |
| `perf`     | Performance improvement | PATCH        |
| `test`     | Adding/fixing tests     | None         |
| `build`    | Build system changes    | None         |
| `ci`       | CI configuration        | None         |
| `chore`    | Maintenance tasks       | None         |
| `revert`   | Revert previous commit  | Depends      |

### Type Definitions

#### `feat` - Features

New functionality for the user.

```
feat(cart): add wishlist to cart conversion
feat(auth): implement social login with Google
feat(reports): add export to Excel functionality
```

#### `fix` - Bug Fixes

Fixes a bug in existing functionality.

```
fix(checkout): correct tax calculation for LKR
fix(inventory): resolve negative stock issue
fix(auth): fix token expiration handling
```

#### `docs` - Documentation

Changes to documentation only.

```
docs(api): update authentication endpoints
docs(readme): add installation instructions
docs(contributing): add code of conduct
```

#### `style` - Code Style

Formatting, missing semicolons, whitespace, etc.

```
style(utils): format according to Black
style(components): fix ESLint warnings
style(imports): sort imports with isort
```

#### `refactor` - Refactoring

Code changes that neither fix bugs nor add features.

```
refactor(models): extract base model mixin
refactor(services): simplify payment processing
refactor(hooks): consolidate API fetch logic
```

#### `perf` - Performance

Improves performance.

```
perf(queries): optimize product listing query
perf(images): add lazy loading to gallery
perf(cache): implement Redis caching for sessions
```

#### `test` - Tests

Adding or modifying tests.

```
test(auth): add JWT validation tests
test(cart): increase coverage for checkout
test(e2e): add Playwright tests for login
```

#### `build` - Build System

Changes to build process or dependencies.

```
build(docker): optimize production Dockerfile
build(deps): upgrade Django to 5.1
build(webpack): configure code splitting
```

#### `ci` - Continuous Integration

Changes to CI configuration.

```
ci(github): add automated testing workflow
ci(docker): add container build pipeline
ci(deploy): configure staging deployment
```

#### `chore` - Maintenance

Routine tasks that don't modify source code.

```
chore(deps): update development dependencies
chore(gitignore): add IDE files
chore(scripts): add database reset script
```

#### `revert` - Revert

Reverts a previous commit.

```
revert: "feat(cart): add wishlist conversion"

This reverts commit abc123.
Reason: Causes performance issues.
```

### Breaking Changes

Any type can have breaking changes. Add `!` after scope:

```
feat(api)!: change authentication response format
fix(models)!: rename User.name to User.full_name
```

### Type Selection Guide

| Change             | Type     |
| ------------------ | -------- |
| New endpoint       | feat     |
| Bug in production  | fix      |
| Update README      | docs     |
| Run formatter      | style    |
| Rename variables   | refactor |
| Speed optimization | perf     |
| Add unit test      | test     |
| Update Docker      | build    |
| GitHub Actions     | ci       |
| Update gitignore   | chore    |

---

## Scope Guidelines

### Purpose

The scope provides additional context about what part of the codebase
is affected by the change. It should be a noun describing the section.

### Format

- Lowercase
- Single word preferred
- Use kebab-case if multiple words needed

### Project-Specific Scopes

#### Backend Scopes

| Scope       | Description                      |
| ----------- | -------------------------------- |
| `auth`      | Authentication and authorization |
| `users`     | User management                  |
| `tenants`   | Multi-tenancy                    |
| `products`  | Product catalog                  |
| `inventory` | Stock management                 |
| `orders`    | Order processing                 |
| `pos`       | Point of sale                    |
| `payments`  | Payment processing               |
| `reports`   | Reporting and analytics          |
| `api`       | API infrastructure               |
| `models`    | Database models                  |
| `admin`     | Django admin                     |
| `celery`    | Background tasks                 |
| `cache`     | Caching layer                    |

#### Frontend Scopes

| Scope       | Description       |
| ----------- | ----------------- |
| `ui`        | UI components     |
| `dashboard` | ERP dashboard     |
| `pos`       | POS interface     |
| `webstore`  | Customer webstore |
| `auth`      | Authentication UI |
| `hooks`     | React hooks       |
| `store`     | State management  |
| `api`       | API client        |
| `forms`     | Form components   |
| `layout`    | Layout components |

#### Infrastructure Scopes

| Scope    | Description          |
| -------- | -------------------- |
| `docker` | Docker configuration |
| `ci`     | CI/CD pipelines      |
| `nginx`  | Nginx configuration  |
| `db`     | Database changes     |
| `deps`   | Dependencies         |
| `config` | Configuration files  |

### When to Use Scope

**Use scope when:**

- Change affects specific module
- Context helps understanding
- Multiple modules exist

**Omit scope when:**

- Change is global
- Scope is obvious from context
- Root-level configuration change

### Examples

```
# With scope
feat(products): add variant support
fix(checkout): correct total calculation
docs(api): update endpoint documentation

# Without scope (global changes)
chore: update dependencies
docs: add contributing guide
style: apply formatting to all files
```

### Scope Best Practices

| Practice      | Example                                      |
| ------------- | -------------------------------------------- |
| Be specific   | `products` not `stuff`                       |
| Be consistent | Always `auth` not sometimes `authentication` |
| Keep short    | `ui` not `user-interface`                    |

---

## Subject Guidelines

### Rules

1. **Use imperative mood** - "add" not "adds" or "added"
2. **No capitalization** - Start with lowercase
3. **No period** - Don't end with a period
4. **Be concise** - Maximum 50 characters (soft limit)
5. **Be descriptive** - Explain what the commit does

### Imperative Mood

Write subjects as commands. They should complete the sentence:
"If applied, this commit will **your subject here**"

| Good ✅               | Bad ❌                  |
| --------------------- | ----------------------- |
| add user registration | added user registration |
| fix login timeout     | fixes login timeout     |
| update documentation  | updating documentation  |
| remove deprecated API | removed deprecated API  |

### Capitalization

| Good ✅                 | Bad ❌                  |
| ----------------------- | ----------------------- |
| add user authentication | Add user authentication |
| fix cart calculation    | Fix Cart Calculation    |

### Punctuation

| Good ✅           | Bad ❌             |
| ----------------- | ------------------ |
| add login feature | add login feature. |
| fix timeout issue | fix timeout issue; |

### Length

| Length      | Status           |
| ----------- | ---------------- |
| ≤50 chars   | Ideal            |
| 50-72 chars | Acceptable       |
| >72 chars   | Too long, revise |

### Good vs Bad Examples

**Good subjects:**

```
add JWT token refresh endpoint
fix incorrect tax calculation for Sri Lanka
update API authentication documentation
refactor user service to use repository pattern
```

**Bad subjects:**

```
Added the JWT token refresh endpoint.          # Past tense, period
Fix bug                                         # Too vague
Update                                          # Not descriptive
This commit adds a new feature for refreshing   # Too long, not imperative
jwt tokens automatically when they expire
```

### Subject Checklist

Before committing, ask:

- [ ] Is it imperative? (add, fix, update)
- [ ] Is it lowercase?
- [ ] Is it under 50 characters?
- [ ] Does it describe what the commit does?
- [ ] Is it free of punctuation at the end?

---

## Body Guidelines

### Purpose

The body provides additional context when the subject alone
cannot fully explain the change. Use it to explain **what**
changed and **why**, not how.

### When to Use Body

| Scenario                 | Use Body? |
| ------------------------ | --------- |
| Simple bug fix           | No        |
| Complex feature          | Yes       |
| Breaking change          | Yes       |
| Non-obvious reasoning    | Yes       |
| Multiple related changes | Yes       |

### Format Rules

1. **Separate from subject** - Blank line after subject
2. **Wrap at 72 characters** - For readability
3. **Explain why** - Not just what
4. **Use bullet points** - For multiple items
5. **Reference context** - Related issues, discussions

### Body Content

**Good body content:**

- Motivation for the change
- Contrast with previous behavior
- Side effects or consequences
- Related changes in other parts
- Decisions and alternatives considered

**Avoid in body:**

- Implementation details (that's what code is for)
- Obvious statements
- Redundant information

### Examples

**Simple change (no body needed):**

```
fix(auth): correct token expiration calculation
```

**Complex change (body recommended):**

```
feat(payments): add LankaPay integration

Integrate LankaPay as a local payment option for Sri Lankan
customers. This provides lower transaction fees compared to
international payment gateways.

- Add LankaPay SDK integration
- Implement webhook handlers for payment status
- Add retry logic for failed transactions
- Update checkout flow to show LankaPay option

Note: Requires LankaPay merchant credentials in environment
variables. See .env.example for required keys.
```

**Non-obvious reasoning:**

```
refactor(models): change User.name to first_name and last_name

Separating the name field into first_name and last_name allows for
more accurate sorting by last name and proper formatting of formal
communications (e.g., "Dear Mr. Silva").

This change is backward compatible - a full_name property is
provided that returns the combined name.
```

### Body Checklist

- [ ] Is blank line after subject?
- [ ] Does it explain why?
- [ ] Is each line ≤72 characters?
- [ ] Is it useful (not obvious)?

---

## Footer Guidelines

### Purpose

The footer contains metadata about the commit, including:

- Issue/ticket references
- Breaking change notices
- Co-authors
- Reviewers

### Format

Footers use `token: value` or `token #value` format.

### Common Tokens

| Token             | Purpose                   | Format                         |
| ----------------- | ------------------------- | ------------------------------ |
| `Closes`          | Close issue on merge      | `Closes #123`                  |
| `Fixes`           | Fix and close issue       | `Fixes #456`                   |
| `Refs`            | Reference without closing | `Refs #789`                    |
| `BREAKING CHANGE` | Breaking change notice    | `BREAKING CHANGE: description` |
| `Co-authored-by`  | Credit co-authors         | `Co-authored-by: Name <email>` |
| `Reviewed-by`     | Credit reviewers          | `Reviewed-by: Name <email>`    |

### Issue References

**Close issues (GitHub):**

```
Closes #123
Closes #123, #124, #125
Fixes #456
Resolves #789
```

**Close issues (JIRA/Linear):**

```
Closes LCC-123
Fixes LCC-456
```

**Reference without closing:**

```
Refs #123
Related to #456
See also #789
```

### Breaking Changes

**Method 1: In footer**

```
feat(api): change authentication response format

BREAKING CHANGE: The login endpoint now returns a nested
token object instead of flat response. Clients need to
update their token extraction logic.

Before: { token: "abc123", expires: "..." }
After:  { data: { token: "abc123", expires: "..." } }
```

**Method 2: In header (with !)**

```
feat(api)!: change authentication response format

The login endpoint now returns a nested token object.

Closes #123
```

### Co-authors

Credit multiple contributors:

```
feat(dashboard): add analytics widgets

Implement new dashboard analytics widgets with charts.

Co-authored-by: Jane Dev <jane@example.com>
Co-authored-by: John Dev <john@example.com>
```

### Examples

**Standard with issue reference:**

```
fix(cart): resolve incorrect quantity calculation

The quantity was being multiplied instead of added when
updating existing cart items.

Fixes #456
```

**Multiple references:**

```
feat(reports): add sales dashboard

Add comprehensive sales reporting dashboard with
daily, weekly, and monthly views.

Closes #123
Closes #124
Refs #100
```

**Breaking change with migration:**

```
feat(models)!: rename User fields for consistency

Standardize field names across all models.

BREAKING CHANGE: The following User fields are renamed:
- name -> full_name
- phone -> phone_number
- addr -> address

Run migration: python manage.py migrate
Update queries that reference old field names.

Closes #200
```

---

## Commit Examples

### Feature Commits

**Simple feature:**

```
feat(products): add product variant support
```

**Feature with body:**

```
feat(checkout): implement multi-currency support

Add support for USD, EUR, and GBP in addition to LKR.
Exchange rates are fetched from Central Bank of Sri Lanka
API and cached for 1 hour.

- Add currency selector to checkout
- Implement exchange rate service
- Update price display components
- Add currency preference to user settings

Closes #234
```

**Feature with breaking change:**

```
feat(api)!: change product response structure

BREAKING CHANGE: Product API now returns nested category
object instead of category_id.

Before: { id: 1, category_id: 5 }
After:  { id: 1, category: { id: 5, name: "Electronics" } }

Closes #300
```

### Bug Fix Commits

**Simple fix:**

```
fix(cart): correct quantity update calculation
```

**Fix with explanation:**

```
fix(auth): resolve token refresh race condition

When multiple API calls were made simultaneously with an
expired token, each call would attempt to refresh the token,
causing duplicate refresh requests.

Implement request queuing to ensure only one refresh
request is made and other requests wait for it.

Fixes #456
```

### Documentation Commits

```
docs(api): add authentication endpoint documentation
```

```
docs(readme): update installation instructions

Add prerequisites section and troubleshooting guide for
common installation issues.
```

### Refactor Commits

```
refactor(models): extract audit fields to mixin
```

```
refactor(services): simplify order processing logic

Break down the monolithic process_order function into
smaller, testable units:

- validate_order()
- calculate_totals()
- apply_discounts()
- process_payment()
- update_inventory()

No functional changes.
```

### Test Commits

```
test(auth): add JWT validation test coverage
```

```
test(cart): improve checkout integration tests

Add tests for:
- Empty cart checkout attempt
- Out of stock items
- Discount code application
- Multi-currency checkout
```

### Build/CI Commits

```
build(docker): optimize production image size
```

```
ci(github): add automated deployment workflow

Add GitHub Actions workflow for:
- Run tests on PR
- Build Docker images on merge
- Deploy to staging on develop merge
- Deploy to production on release tags
```

### Chore Commits

```
chore(deps): update Django to 5.1
```

```
chore: update development dependencies

- black: 24.3.0 -> 24.4.0
- pytest: 8.0.0 -> 8.1.0
- eslint: 8.56.0 -> 8.57.0
```

### Revert Commits

```
revert: "feat(cart): add wishlist conversion"

This reverts commit 3a7e2f1.

Reason: Feature caused performance regression in cart
loading. Needs optimization before re-implementation.
```

### Bad Examples (Avoid These)

```
# ❌ No type
Add user authentication

# ❌ Past tense
feat(auth): added login functionality

# ❌ Too vague
fix: bug fix

# ❌ Ends with period
feat(products): add search feature.

# ❌ Capital letter
Fix(auth): resolve token issue

# ❌ Too long subject
feat(checkout): implement a new multi-step checkout process with
address validation and payment integration

# ❌ Not imperative
feat(api): this commit adds new endpoints
```

---

## Using Commitizen

### Overview

Commitizen provides an interactive CLI for creating well-formatted
commit messages. It guides you through the commit process step by step.

### Installation

Commitizen is installed as a dev dependency:

```bash
npm install
```

### Usage

```bash
# Stage your changes
git add .

# Run Commitizen
npm run commit
```

### Workflow

1. Select type (feat, fix, etc.)
2. Enter scope (optional)
3. Write subject
4. Add body (optional)
5. Add breaking change notes (if any)
6. Reference issues

### Example Session

```
? Select the type of change that you're committing:
  feat:     A new feature

? What is the scope of this change (e.g. component or file name)?
> auth

? Write a short, imperative tense description of the change:
> add JWT token refresh endpoint

? Provide a longer description of the change (optional):
> Implement automatic token refresh functionality

? Are there any breaking changes? No
? Does this change affect any open issues? Yes
? Add issue references (e.g. "fix #123", "re #123".):
> Closes #123

# Result:
feat(auth): add JWT token refresh endpoint

Implement automatic token refresh functionality

Closes #123
```

### Skipping Commitizen

You can also commit normally:

```bash
git commit -m "feat(auth): add login endpoint"
```

Commitizen is optional but recommended for:

- New team members
- Complex commits
- Breaking changes

### Bypass Commit Hooks (Emergency)

```bash
git commit --no-verify -m "emergency fix"
```

> **⚠️ Warning:** Only use `--no-verify` in emergencies. All regular
> commits should pass through the commit-msg hook validation.
