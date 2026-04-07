<!--
LankaCommerce Cloud - Hotfix Pull Request Template
Use this template for urgent production fixes from hotfix/* branches
⚠️ HOTFIXES REQUIRE EXPEDITED REVIEW
-->

## 🚨 HOTFIX: [Critical Issue Description]

> **⚠️ PRODUCTION HOTFIX - URGENT REVIEW REQUIRED**

### Urgency

**Priority Level:**

- [ ] P0 - System completely down
- [ ] P1 - Major functionality broken
- [ ] P2 - Significant user impact

**Estimated Production Impact:**
<!-- How many users/tenants are affected? -->

**Time Since Issue Detected:**
<!-- When was the issue first reported? -->

---

## Issue Details

**Production Issue:** #

### Problem Description

<!-- What's happening in production -->

### Business Impact

<!-- How is this affecting the business/users -->

- Revenue impact:
- Users affected:
- Tenants affected:
- SLA impact:

---

## Root Cause

### Immediate Cause

<!-- What directly caused this issue -->

### Contributing Factors

<!-- Other factors that contributed -->

-

### How Detected

<!-- How was this issue discovered -->

- [ ] User report
- [ ] Monitoring alert
- [ ] Error logs
- [ ] Other:

---

## Solution

### Fix Description

<!-- What does this hotfix do -->

### Minimal Changes

<!-- Confirm this is a minimal fix -->

- [ ] Only essential changes included
- [ ] No refactoring or improvements
- [ ] Smallest possible change to fix issue

### Changes Made

-

---

## Testing

### Critical Testing

<!-- Testing performed before merge -->

- [ ] Fix verified locally
- [ ] Fix verified in staging
- [ ] Basic smoke test passed
- [ ] No obvious regressions

### Testing Limitations

<!-- What couldn't be fully tested due to urgency -->

### Post-Deploy Testing Plan

<!-- What will be tested after deploy -->

1.
2.
3.

---

## Deployment

### Deployment Order

<!-- Order of operations -->

1. Merge this PR
2. Deploy to production
3. Verify fix in production
4. Monitor for issues

### Rollback Plan

<!-- How to rollback if fix fails -->

1.
2.
3.

### Monitoring

<!-- What to monitor after deploy -->

- [ ] Error rates
- [ ] Response times
- [ ] User complaints
- [ ] System metrics

---

## Approvals

### Emergency Approval

<!-- For expedited review -->

**Approved by:** @
**Date/Time:**
**Reason for expedited approval:**

### Standard Approvers Notified

<!-- Tag team leads / on-call -->

- [ ] @
- [ ] @

---

## Post-Mortem

### Follow-up Tasks

<!-- Tasks to do after the immediate fix -->

- [ ] Proper fix in next sprint
- [ ] Add missing tests
- [ ] Update documentation
- [ ] Post-mortem meeting scheduled

### Ticket References

- Hotfix ticket: #
- Follow-up ticket: #
- Post-mortem ticket: #

---

## Checklist

### Pre-merge (Expedited)

- [ ] Fix solves the production issue
- [ ] Minimal, focused changes only
- [ ] No breaking changes
- [ ] Emergency approval obtained
- [ ] Rollback plan ready

### Post-merge (Immediate)

- [ ] Deploy to production
- [ ] Verify fix in production
- [ ] Notify stakeholders
- [ ] Close incident

### Follow-up (Within 24-48 hours)

- [ ] Merge to develop branch
- [ ] Create follow-up tasks
- [ ] Schedule post-mortem
- [ ] Document incident
