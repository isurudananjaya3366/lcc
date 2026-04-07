# Code Review Guidelines

> LankaCommerce Cloud - Code Review Standards

## Table of Contents

1. [Purpose](#purpose)
2. [Review Scope](#review-scope)
3. [Code Quality Criteria](#code-quality-criteria)
4. [Security Review](#security-review)
5. [Performance Review](#performance-review)
6. [Review Timeline](#review-timeline)
7. [Approval Requirements](#approval-requirements)
8. [Reviewer Checklist](#reviewer-checklist)
9. [Comment Guidelines](#comment-guidelines)
10. [CODEOWNERS](#codeowners)

---

## Purpose

Code reviews are a critical part of our development process. They help us:

- **Maintain Quality:** Catch bugs before they reach production
- **Share Knowledge:** Spread understanding of the codebase
- **Improve Skills:** Learn from each other's approaches
- **Ensure Security:** Identify security issues early
- **Build Consistency:** Maintain coding standards across the team

Every pull request requires a code review before merging.

---

## Review Scope

### What to Review

Every code review should examine:

| Area              | Focus Points                               |
| ----------------- | ------------------------------------------ |
| **Functionality** | Does the code do what it's supposed to do? |
| **Logic**         | Is the implementation correct?             |
| **Design**        | Is the architecture appropriate?           |
| **Readability**   | Is the code easy to understand?            |
| **Tests**         | Are tests adequate and passing?            |
| **Documentation** | Are comments and docs updated?             |
| **Dependencies**  | Are new dependencies justified?            |

### Review Depth by PR Size

| PR Size | Lines Changed | Review Approach                    |
| ------- | ------------- | ---------------------------------- |
| Small   | < 50 lines    | Quick review, focus on correctness |
| Medium  | 50-200 lines  | Thorough review, all criteria      |
| Large   | 200-500 lines | Split into sessions, take breaks   |
| XL      | 500+ lines    | Request PR split if possible       |

### What's Out of Scope

- **Automated formatting:** Handled by linters/formatters
- **Style preferences:** Unless violating standards
- **Rewriting entire files:** Unless critical issues
- **Unrelated code:** Only review changed lines + context

### Review Mindset

**Reviewers should:**

- Assume good intent from the author
- Focus on the code, not the person
- Ask questions before assuming mistakes
- Suggest improvements, not demand changes
- Approve when "good enough" for production

---

## Code Quality Criteria

### Readability

Code should be easy to read and understand:

| Criterion        | Good Example              | Bad Example                  |
| ---------------- | ------------------------- | ---------------------------- |
| Clear names      | `calculate_total_price()` | `calc()`                     |
| Short functions  | 20-30 lines max           | 200+ lines                   |
| Single purpose   | One thing per function    | Multiple responsibilities    |
| Self-documenting | Code explains itself      | Requires comments for basics |

**Questions to Ask:**

- [ ] Can I understand this code in 5 minutes?
- [ ] Would a new team member understand it?
- [ ] Are variable/function names descriptive?

### Naming Conventions

| Type      | Python Style       | TypeScript Style                  |
| --------- | ------------------ | --------------------------------- |
| Variables | `snake_case`       | `camelCase`                       |
| Functions | `snake_case`       | `camelCase`                       |
| Classes   | `PascalCase`       | `PascalCase`                      |
| Constants | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE`                |
| Files     | `snake_case.py`    | `camelCase.ts` or `kebab-case.ts` |

### Code Structure

**DRY (Don't Repeat Yourself):**

- [ ] No duplicated code blocks
- [ ] Shared logic is extracted
- [ ] Helper functions used appropriately

**SOLID Principles:**

- [ ] Single Responsibility: One reason to change
- [ ] Open/Closed: Open for extension, closed for modification
- [ ] Liskov Substitution: Subtypes substitutable
- [ ] Interface Segregation: Specific interfaces
- [ ] Dependency Inversion: Depend on abstractions

### Error Handling

**Requirements:**

- [ ] All errors are caught and handled
- [ ] Errors are logged appropriately
- [ ] User-facing errors are friendly
- [ ] No silent failures
- [ ] Specific exceptions used (not bare `except:`)

**Python Example:**

```python
# Good
try:
    result = process_order(order_id)
except OrderNotFoundError as e:
    logger.error(f"Order not found: {order_id}")
    raise

# Bad
try:
    result = process_order(order_id)
except:
    pass
```

### Code Smells to Watch

| Smell         | Description                          |
| ------------- | ------------------------------------ |
| Magic numbers | Hardcoded values without explanation |
| Long methods  | Functions > 50 lines                 |
| Deep nesting  | More than 3 levels of indentation    |
| God classes   | Classes doing too much               |
| Dead code     | Commented-out or unused code         |
| Copy-paste    | Duplicated code blocks               |

---

## Security Review

### Security Checklist

Every code review must check for security issues:

| Category    | Check Points                                        |
| ----------- | --------------------------------------------------- |
| **Secrets** | No hardcoded passwords, API keys, tokens            |
| **Input**   | All user input is validated and sanitized           |
| **SQL**     | Parameterized queries used, no string concatenation |
| **XSS**     | Output is properly escaped                          |
| **Auth**    | Authentication and authorization checked            |
| **Logging** | No sensitive data in logs                           |

### No Hardcoded Secrets

**Never commit:**

- Passwords or API keys
- Database connection strings with credentials
- JWT secrets or encryption keys
- Third-party service tokens

**Check for:**

```python
# Bad - Hardcoded secret
SECRET_KEY = "my-secret-key-123"
API_KEY = "sk_live_xxxxx"

# Good - Environment variable
SECRET_KEY = os.environ.get("SECRET_KEY")
API_KEY = settings.API_KEY
```

### Input Validation

**All user input must be validated:**

| Input Type | Validation                     |
| ---------- | ------------------------------ |
| Email      | Regex pattern, max length      |
| Phone      | +94 format for Sri Lanka       |
| Currency   | LKR format, decimal places     |
| IDs        | UUID format or integer         |
| Text       | Max length, allowed characters |
| Files      | Type, size, extension checks   |

### SQL Injection Prevention

**Always use parameterized queries:**

```python
# Bad - SQL injection risk
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good - Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# Best - ORM (Django)
User.objects.filter(id=user_id)
```

### XSS Prevention

**Escape all output in templates:**

```html
<!-- Bad - XSS risk -->
{{ user_input|safe }}

<!-- Good - Auto-escaped -->
{{ user_input }}
```

### Authentication & Authorization

**Check for:**

- [ ] Endpoints require authentication
- [ ] User can only access their own data
- [ ] Admin routes require admin role
- [ ] Multi-tenant isolation enforced

### Sensitive Data Logging

**Never log:**

- Passwords (even hashed)
- Credit card numbers
- Personal identification numbers
- Session tokens
- API keys

```python
# Bad
logger.info(f"User login: {username}, password: {password}")

# Good
logger.info(f"User login attempt: {username}")
```

### Multi-Tenant Security

**LankaCommerce-Specific:**

- [ ] Tenant isolation maintained
- [ ] Cross-tenant data access prevented
- [ ] Tenant context checked in queries
- [ ] Schema switching is secure

---

## Performance Review

### Performance Checklist

| Area           | Check Points                           |
| -------------- | -------------------------------------- |
| **Algorithms** | Appropriate time/space complexity      |
| **Database**   | Efficient queries, proper indexing     |
| **N+1**        | No N+1 query problems                  |
| **Caching**    | Cache used where appropriate           |
| **Memory**     | No memory leaks, large objects handled |
| **Async**      | Async used for I/O operations          |

### Algorithm Efficiency

**Check time complexity:**

| Complexity | Acceptable For           |
| ---------- | ------------------------ |
| O(1)       | Ideal for all operations |
| O(log n)   | Search, lookups          |
| O(n)       | Single iteration         |
| O(n log n) | Sorting                  |
| O(n²)      | Avoid for large datasets |

**Warning signs:**

- Nested loops over large datasets
- Recursive functions without memoization
- Sorting in a loop
- Multiple iterations when one suffices

### Database Query Optimization

**Avoid N+1 Queries:**

```python
# Bad - N+1 problem
for order in Order.objects.all():
    print(order.customer.name)  # Extra query per order

# Good - Prefetch related
for order in Order.objects.select_related('customer').all():
    print(order.customer.name)  # Single query
```

**Use Efficient Queries:**

- [ ] Only select needed fields
- [ ] Use `exists()` instead of `count() > 0`
- [ ] Use `values()` for aggregations
- [ ] Avoid `all()` without pagination
- [ ] Use indexes on filtered/sorted fields

### Caching Strategies

**When to Cache:**
| Data Type | Cache Strategy |
|-----------|----------------|
| Static data | Long TTL (hours/days) |
| User data | Short TTL (minutes) |
| Computed results | Medium TTL |
| Session data | Redis session store |
| Frequent queries | Query cache |

**Cache Invalidation:**

- [ ] Cache invalidated on data change
- [ ] TTL set appropriately
- [ ] Cache keys are unique and descriptive

### Memory Considerations

**Watch for:**

- [ ] Large file uploads processed in chunks
- [ ] Large querysets iterated, not loaded fully
- [ ] Images resized before storage
- [ ] Temporary objects cleaned up

```python
# Bad - Loads all into memory
data = list(LargeModel.objects.all())

# Good - Iterator for large datasets
for item in LargeModel.objects.iterator():
    process(item)
```

### Async Operations

**Use async for:**

- External API calls
- File I/O
- Database queries (where supported)
- Email sending
- Task queue operations

```python
# Consider Celery for long-running tasks
@celery_app.task
def send_order_notification(order_id):
    # This runs asynchronously
    pass
```

---

## Review Timeline

### Expected Turnaround Times

| Priority | Initial Response | Complete Review |
| -------- | ---------------- | --------------- |
| Hotfix   | < 1 hour         | < 2 hours       |
| High     | < 4 hours        | < 8 hours       |
| Normal   | < 24 hours       | < 48 hours      |
| Low      | < 48 hours       | < 72 hours      |

### Timeline Guidelines

**For Authors:**

- Tag reviewers when PR is ready
- Respond to feedback within 24 hours
- Keep PRs small to enable faster reviews
- Mark as "Ready for Review" when complete

**For Reviewers:**

- Acknowledge PR within timeline
- If busy, reassign or communicate delay
- Complete review in single session if possible
- Don't block on minor issues

### Response Time Expectations

| Action                  | Expected Time                   |
| ----------------------- | ------------------------------- |
| Initial acknowledgment  | Within 4 hours (business hours) |
| First round of comments | Within 24 hours                 |
| Re-review after changes | Within 8 hours                  |
| Final approval          | Within 4 hours of changes       |

### Escalation Process

**If review is delayed:**

1. **24 hours:** Author pings reviewer
2. **48 hours:** Author adds additional reviewer
3. **72 hours:** Escalate to team lead
4. **Emergency:** Team lead can approve or find alternate reviewer

### Business Hours

**LankaCommerce operates in:**

- Timezone: Asia/Colombo (UTC+5:30)
- Business hours: 9:00 AM - 6:00 PM
- Business days: Monday - Friday

_After-hours PRs: Response expected next business day_

---

## Approval Requirements

### Standard Approval Matrix

| PR Type             | Required Approvals | Approved By                 |
| ------------------- | ------------------ | --------------------------- |
| Feature             | 1                  | Any team member             |
| Bugfix              | 1                  | Any team member             |
| Hotfix              | 1 (expedited)      | Team lead or designated     |
| Breaking change     | 2                  | Including senior dev        |
| Security change     | 2                  | Including security reviewer |
| Infrastructure      | 2                  | Including DevOps            |
| Multi-tenant change | 2                  | Including architect         |

### Approval Levels

**Level 1 - Standard (1 approval):**

- Regular features
- Bug fixes
- Documentation updates
- Test additions
- Minor refactoring

**Level 2 - Critical (2 approvals):**

- Database schema changes
- Authentication/authorization changes
- Payment processing changes
- Multi-tenant isolation changes
- Breaking API changes
- Core infrastructure changes

### Who Can Approve

| Role             | Approval Scope                 |
| ---------------- | ------------------------------ |
| Junior Developer | Cannot approve alone           |
| Developer        | Level 1 changes                |
| Senior Developer | All changes                    |
| Tech Lead        | All changes + expedited        |
| Architect        | All changes + design decisions |

### Conditions for Approval

Before approving, ensure:

- [ ] All review criteria checked
- [ ] No blocking comments unresolved
- [ ] Tests pass
- [ ] No merge conflicts
- [ ] Documentation updated

### Cannot Approve

- Your own PR (self-approval disabled)
- If you authored any commits in the PR
- If you have conflicts of interest

### Emergency/Hotfix Process

For production emergencies:

1. Expedited review with 1 approval
2. Team lead or designated reviewer approves
3. Post-merge review by additional reviewer
4. Post-mortem within 48 hours

---

## Reviewer Checklist

Use this checklist for every code review.

### 🔴 Must Check (Blocking)

#### Functionality

- [ ] Code does what the PR description says
- [ ] Edge cases are handled
- [ ] Error handling is appropriate

#### Security (Critical)

- [ ] No hardcoded secrets or credentials
- [ ] User input is validated and sanitized
- [ ] SQL uses parameterized queries
- [ ] Output is properly escaped (XSS prevention)
- [ ] Authentication/authorization is correct
- [ ] No sensitive data in logs
- [ ] Multi-tenant isolation maintained

#### Tests

- [ ] New code has tests
- [ ] Tests actually test the functionality
- [ ] All tests pass
- [ ] Edge cases are tested

#### Breaking Changes

- [ ] Breaking changes are documented
- [ ] Migration path is provided
- [ ] Backwards compatibility considered

### 🟡 Should Check (Important)

#### Code Quality

- [ ] Code is readable and maintainable
- [ ] Naming is clear and consistent
- [ ] No unnecessary complexity
- [ ] DRY principle followed
- [ ] No code smells

#### Performance

- [ ] No N+1 query problems
- [ ] Efficient algorithms used
- [ ] Database queries are optimized
- [ ] Appropriate caching applied

#### Documentation

- [ ] Code comments where needed
- [ ] README updated if needed
- [ ] API documentation updated
- [ ] CHANGELOG updated

### 🟢 Nice to Have (Suggestions)

#### Style & Consistency

- [ ] Follows project conventions
- [ ] Consistent with existing code
- [ ] Could be improved (minor suggestions)

#### Learning & Sharing

- [ ] Knowledge sharing opportunities
- [ ] Better approaches to suggest
- [ ] Patterns to highlight

---

### Quick Checklist (Copy-Paste)

```
**Review Checklist:**
- [ ] Functionality works as described
- [ ] No security issues
- [ ] Tests added and passing
- [ ] No breaking changes (or documented)
- [ ] Code is readable
- [ ] No performance issues
- [ ] Documentation updated

**Approval:** ✅ Approved / 🔄 Request Changes / 💬 Comment
```

---

## Comment Guidelines

### Comment Types

Use prefixes to clarify intent:

| Prefix         | Meaning               | Example                                       |
| -------------- | --------------------- | --------------------------------------------- |
| `[BLOCKING]`   | Must fix before merge | `[BLOCKING] SQL injection risk here`          |
| `[SUGGESTION]` | Optional improvement  | `[SUGGESTION] Could use a list comprehension` |
| `[QUESTION]`   | Seeking clarification | `[QUESTION] Why is this async?`               |
| `[NIT]`        | Minor style issue     | `[NIT] Extra blank line`                      |
| `[PRAISE]`     | Positive feedback     | `[PRAISE] Great error handling!`              |

### Tone Guidelines

**Do:**

- Be constructive and respectful
- Focus on the code, not the person
- Explain why, not just what
- Ask questions instead of making demands
- Acknowledge good work
- Assume the author had good reasons

**Don't:**

- Use harsh or condescending language
- Make personal attacks
- Be dismissive
- Use ALL CAPS
- Leave vague comments like "This is wrong"
- Pile on with multiple reviewers saying the same thing

### Good vs Bad Comments

| ❌ Bad                   | ✅ Good                                                                         |
| ------------------------ | ------------------------------------------------------------------------------- |
| "This is wrong"          | "This might cause X because Y. Consider Z instead?"                             |
| "Why did you do this?"   | "[QUESTION] I'm curious about the reasoning here - was it for performance?"     |
| "You should know better" | "[SUGGESTION] Django provides `get_object_or_404` for this pattern"             |
| "Fix this"               | "[BLOCKING] This could expose user data. We need to add tenant filtering here." |
| No comment on good code  | "[PRAISE] Nice use of the factory pattern here!"                                |

### Providing Context

**Include:**

- The problem you see
- Why it's a problem
- A suggested solution
- Reference to documentation if applicable

**Example:**

```
[BLOCKING] Security issue

This query uses string formatting which could allow SQL injection:

    query = f"SELECT * FROM users WHERE id = {user_id}"

Please use Django ORM or parameterized queries:

    User.objects.filter(id=user_id)

See: https://docs.djangoproject.com/en/stable/topics/security/#sql-injection-protection
```

### Responding to Feedback

**As an Author:**

- Thank reviewers for their time
- Respond to all comments
- Explain your reasoning if disagreeing
- Mark resolved comments as resolved
- Request re-review when changes are made

**As a Reviewer:**

- Acknowledge when feedback is addressed
- Approve promptly when satisfied
- Don't re-review already approved items

### Comment Resolution

| Status    | Meaning                                        |
| --------- | ---------------------------------------------- |
| Open      | Needs attention                                |
| Resolved  | Addressed by author                            |
| Outdated  | Code has changed                               |
| Won't Fix | Intentionally not addressed (with explanation) |

---

## CODEOWNERS

Automatic reviewer assignment is configured in `.github/CODEOWNERS`.

See the [CODEOWNERS file](../.github/CODEOWNERS) for current ownership patterns.

### How It Works

- When a PR modifies files, GitHub automatically requests reviews from the owners defined in CODEOWNERS
- Last matching pattern takes precedence
- Uses GitHub usernames (`@user`) or team handles (`@org/team`)

### Team Handles

| Team Handle                      | Responsibility                 |
| -------------------------------- | ------------------------------ |
| @lankacommerce/core-team         | Default fallback for all files |
| @lankacommerce/backend-team      | Django backend code            |
| @lankacommerce/frontend-team     | Next.js frontend code          |
| @lankacommerce/devops-team       | Infrastructure and CI/CD       |
| @lankacommerce/security-team     | Auth, permissions, security    |
| @lankacommerce/dba-team          | Database migrations and SQL    |
| @lankacommerce/docs-team         | Documentation and markdown     |
| @lankacommerce/pos-team          | Point of sale application      |
| @lankacommerce/erp-team          | ERP dashboard application      |
| @lankacommerce/webstore-team     | Webstore application           |
| @lankacommerce/payments-team     | Payment processing             |
| @lankacommerce/architecture-team | Architecture and multi-tenant  |
