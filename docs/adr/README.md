# Architecture Decision Records (ADR)

> A record of architecturally significant decisions made for LankaCommerce Cloud.

**Navigation:** [Docs Index](../index.md) · [Architecture](../architecture/)

---

## What Are ADRs?

Architecture Decision Records (ADRs) capture important technical decisions along with their context and consequences. They serve as a living log of why the project is structured the way it is.

Each ADR follows the [Michael Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) and uses a four-digit numbering scheme.

---

## ADR Status Values

| Status         | Meaning                                      |
| -------------- | -------------------------------------------- |
| **Proposed**   | Under discussion, not yet agreed upon        |
| **Accepted**   | Agreed upon and in effect                    |
| **Deprecated** | No longer in effect, replaced by a newer ADR |
| **Superseded** | Replaced by another ADR (linked)             |

---

## ADR Index

| #                                             | Title                     | Status   | Date    |
| --------------------------------------------- | ------------------------- | -------- | ------- |
| [ADR-0001](0001-monorepo-structure.md)        | Monorepo Structure        | Accepted | 2025-01 |
| [ADR-0002](0002-multi-tenancy-approach.md)    | Multi-Tenancy Approach    | Accepted | 2025-01 |
| [ADR-0003](0003-technology-stack.md)          | Technology Stack          | Accepted | 2025-01 |
| [ADR-0004](0004-per-tenant-authentication.md) | Per-Tenant Authentication | Accepted | 2026-02 |

---

## Creating a New ADR

1. Copy the [ADR template](template.md)
2. Name the file using four-digit numbering: `NNNN-short-title.md`
3. Fill in all sections: Title, Status, Context, Decision, Consequences
4. Set the status to **Proposed** initially
5. After team review, update the status to **Accepted**
6. Add an entry to the ADR Index table above
7. Commit the ADR along with any related code changes

---

## Naming Convention

| Pattern                          | Example                           |
| -------------------------------- | --------------------------------- |
| `NNNN-short-kebab-case-title.md` | `0004-api-versioning-strategy.md` |

Use sequential numbering starting from 0001. Never reuse a number, even for deprecated ADRs.

---

## Related Documentation

- [ADR Template](template.md) — Standard template for new ADRs
- [Architecture Overview](../architecture/) — System architecture documentation
- [Docs Index](../index.md) — Documentation hub
