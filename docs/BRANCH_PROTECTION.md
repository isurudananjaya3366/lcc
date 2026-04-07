# Branch Protection & Merge Requirements

> LankaCommerce Cloud - Branch Protection Rules, Status Checks, and Merge Strategy

## Table of Contents

1. [Overview](#overview)
2. [Main Branch Protection](#main-branch-protection)
3. [Develop Branch Protection](#develop-branch-protection)
4. [Required Status Checks](#required-status-checks)
5. [Merge Requirements](#merge-requirements)
6. [Merge Strategy](#merge-strategy)
7. [Emergency/Hotfix Process](#emergencyhotfix-process)
8. [Template Verification](#template-verification)

---

## Overview

Branch protection rules are essential for maintaining code quality, ensuring auditability, and preventing accidental or unauthorized changes to critical branches. These rules enforce that all changes go through a proper review and validation process before being merged.

### Why Branch Protection?

- **Stability:** Prevents broken code from reaching production
- **Auditability:** Every change has a review trail
- **Compliance:** Supports SOC 2 and GDPR compliance requirements
- **Quality:** Enforces testing and review standards
- **Safety:** Prevents accidental force pushes and branch deletions

---

## Main Branch Protection

The `main` branch is the production-ready branch. It has the strictest protection rules.

### Rules

| Rule | Setting | Rationale |
|------|---------|-----------|
| **Require pull request reviews** | ✅ Enabled | All changes must be reviewed |
| **Required approving reviews** | 1 (2 for critical) | At least one approval before merge |
| **Dismiss stale reviews** | ✅ Enabled | New pushes invalidate old approvals |
| **Require review from CODEOWNERS** | ✅ Enabled | Relevant owners must approve |
| **Require status checks to pass** | ✅ Enabled | All CI checks must pass |
| **Require branches to be up to date** | ✅ Enabled | Branch must be current with main |
| **Require signed commits** | ⚠️ Recommended | Enable when team GPG keys are set up |
| **Require linear history** | ❌ Disabled | Merge commits are allowed |
| **Include administrators** | ✅ Enabled | Admins also follow the rules |
| **Allow force pushes** | ❌ Disabled | Never force push to main |
| **Allow deletions** | ❌ Disabled | Main branch cannot be deleted |

### Who Can Merge to Main

| Role | Can Merge |
|------|-----------|
| Regular Developer | ❌ No (only through approved PR) |
| Senior Developer | ✅ Yes (with approved PR) |
| Tech Lead | ✅ Yes (with approved PR) |
| Admin | ✅ Yes (with approved PR, rules enforced) |

---

## Develop Branch Protection

The `develop` branch is the integration branch for features. It has slightly relaxed rules compared to `main`.

### Rules

| Rule | Setting | Rationale |
|------|---------|-----------|
| **Require pull request reviews** | ✅ Enabled | All changes must be reviewed |
| **Required approving reviews** | 1 | One approval is sufficient |
| **Dismiss stale reviews** | ✅ Enabled | New pushes invalidate old approvals |
| **Require review from CODEOWNERS** | ⚠️ Optional | Recommended but not required |
| **Require status checks to pass** | ✅ Enabled | CI checks must pass |
| **Require branches to be up to date** | ❌ Disabled | Not required for develop |
| **Include administrators** | ✅ Enabled | Admins also follow the rules |
| **Allow force pushes** | ❌ Disabled | Never force push to develop |
| **Allow deletions** | ❌ Disabled | Develop branch cannot be deleted |

### Who Can Merge to Develop

| Role | Can Merge |
|------|-----------|
| Regular Developer | ✅ Yes (with approved PR) |
| Senior Developer | ✅ Yes (with approved PR) |
| Tech Lead | ✅ Yes (with approved PR) |

---

## Required Status Checks

The following status checks must pass before a PR can be merged.

### Checks for Main Branch

| Check | Description | Owner | Required |
|-------|-------------|-------|----------|
| **backend-lint** | Python linting (Ruff, flake8) | Backend Team | ✅ Yes |
| **backend-typecheck** | mypy type checking | Backend Team | ✅ Yes |
| **backend-tests** | Django pytest suite | Backend Team | ✅ Yes |
| **frontend-lint** | ESLint + Prettier check | Frontend Team | ✅ Yes |
| **frontend-typecheck** | TypeScript type checking | Frontend Team | ✅ Yes |
| **frontend-tests** | Jest test suite | Frontend Team | ✅ Yes |
| **frontend-build** | Next.js production build | Frontend Team | ✅ Yes |
| **security-scan** | Dependency vulnerability scan | DevOps Team | ✅ Yes |
| **docker-build** | Docker image build validation | DevOps Team | ⚠️ Recommended |

### Checks for Develop Branch

| Check | Description | Owner | Required |
|-------|-------------|-------|----------|
| **backend-lint** | Python linting (Ruff, flake8) | Backend Team | ✅ Yes |
| **backend-tests** | Django pytest suite | Backend Team | ✅ Yes |
| **frontend-lint** | ESLint + Prettier check | Frontend Team | ✅ Yes |
| **frontend-tests** | Jest test suite | Frontend Team | ✅ Yes |
| **frontend-build** | Next.js production build | Frontend Team | ⚠️ Recommended |

### Future Checks (to be added)

| Check | Description | When |
|-------|-------------|------|
| **integration-tests** | End-to-end test suite | Phase 03+ |
| **coverage-check** | Minimum code coverage threshold | Phase 03+ |
| **migration-check** | Database migration validation | Phase 02+ |
| **tenant-isolation** | Multi-tenant isolation tests | Phase 02+ |
| **performance-check** | Performance regression tests | Phase 05+ |

> **Note:** Status checks will be enforced via GitHub Actions workflows. Until workflows are created, these are documented as the intended configuration.

---

## Merge Requirements

### Prerequisites for All PRs

Before any PR can be merged, the following must be true:

- [ ] All required status checks pass (green)
- [ ] Required number of approvals received
- [ ] No unresolved blocking review comments
- [ ] No merge conflicts with target branch
- [ ] PR description is complete and follows template
- [ ] Relevant documentation is updated

### Additional Requirements by PR Type

| PR Type | Extra Requirements |
|---------|-------------------|
| **Feature** | Tests added, documentation updated |
| **Bugfix** | Regression test added, root cause documented |
| **Hotfix** | Expedited review (1 approval), post-mortem planned |
| **Breaking Change** | 2 approvals, migration guide provided |
| **Database Migration** | 2 approvals (including DBA), rollback tested |
| **Security Change** | 2 approvals (including security reviewer) |

---

## Merge Strategy

### Allowed Merge Methods

| Method | Main Branch | Develop Branch | When to Use |
|--------|-------------|----------------|-------------|
| **Merge Commit** | ✅ Allowed | ✅ Allowed | Default for feature branches |
| **Squash and Merge** | ✅ Allowed | ✅ Allowed | Small PRs, cleanup messy history |
| **Rebase and Merge** | ❌ Not Allowed | ⚠️ Discouraged | Avoid to preserve merge history |

### Recommended Strategy

- **Feature → Develop:** Squash and merge (clean history)
- **Develop → Main:** Merge commit (preserve feature grouping)
- **Hotfix → Main:** Merge commit (auditability)
- **Release → Main:** Merge commit (release milestone)

### Commit Message on Merge

When using squash and merge, the final commit message must follow [Conventional Commits](../docs/COMMITS.md):

```
feat(scope): description of the feature (#PR-number)
```

When using merge commit, the default merge message is acceptable:

```
Merge pull request #123 from branch-name
```

---

## Emergency/Hotfix Process

For production emergencies that require immediate deployment:

### Expedited Merge Rules

| Rule | Standard | Emergency |
|------|----------|-----------|
| Required approvals | 1-2 | 1 (Tech Lead or designated) |
| Status checks | All must pass | Critical checks only |
| Branch up to date | Required | Not required |
| Documentation | Required | Can follow after merge |

### Emergency Process

1. **Create hotfix branch** from `main`
2. **Implement minimal fix** — smallest change possible
3. **Get expedited review** — Tech Lead or designated reviewer
4. **Merge to main** — after 1 approval and critical checks pass
5. **Deploy immediately** — follow deployment runbook
6. **Back-merge to develop** — within 4 hours
7. **Post-mortem** — within 48 hours
8. **Follow-up PR** — comprehensive fix if hotfix was minimal

### Who Can Approve Emergency Merges

- Tech Lead
- Senior Developer (designated)
- Project Architect

---

## Template Verification

### Verification Record

| Template | Location | Status | Verified By | Date |
|----------|----------|--------|-------------|------|
| Default PR | `.github/PULL_REQUEST_TEMPLATE.md` | ✅ Created | AI Agent | 2026-02-12 |
| Feature PR | `.github/PULL_REQUEST_TEMPLATE/feature.md` | ✅ Created | AI Agent | 2026-02-12 |
| Bugfix PR | `.github/PULL_REQUEST_TEMPLATE/bugfix.md` | ✅ Created | AI Agent | 2026-02-12 |
| Hotfix PR | `.github/PULL_REQUEST_TEMPLATE/hotfix.md` | ✅ Created | AI Agent | 2026-02-12 |
| Bug Report | `.github/ISSUE_TEMPLATE/bug_report.md` | ✅ Created | AI Agent | 2026-02-12 |
| Feature Request | `.github/ISSUE_TEMPLATE/feature_request.md` | ✅ Created | AI Agent | 2026-02-12 |
| Task | `.github/ISSUE_TEMPLATE/task.md` | ✅ Created | AI Agent | 2026-02-12 |
| Issue Config | `.github/ISSUE_TEMPLATE/config.yml` | ✅ Created | AI Agent | 2026-02-12 |
| CODEOWNERS | `.github/CODEOWNERS` | ✅ Created | AI Agent | 2026-02-12 |

### Verification Notes

- All templates follow GitHub's expected format and file locations
- Issue template chooser (`config.yml`) disables blank issues and provides contact links
- PR templates include comprehensive checklists for different PR types
- CODEOWNERS maps paths to team handles for automatic reviewer assignment

### Post-Push Verification (Manual)

After pushing to GitHub, verify the following:

- [ ] Creating a new issue shows the template chooser with Bug Report, Feature Request, and Task options
- [ ] Blank issues are disabled (redirected to contact links)
- [ ] Creating a new PR auto-fills the default template
- [ ] PR template dropdown shows feature, bugfix, and hotfix options
- [ ] CODEOWNERS triggers automatic reviewer requests on PRs

> **Note:** Full GitHub UI verification should be performed after the repository is pushed to the remote.
