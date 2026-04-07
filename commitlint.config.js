// ==================================================
// LankaCommerce Cloud - commitlint Configuration
// ==================================================
// Enforces Conventional Commits specification (v1.0.0)
// https://www.conventionalcommits.org/en/v1.0.0/
// ==================================================

module.exports = {
  extends: ["@commitlint/config-conventional"],

  rules: {
    // ----------------------------------------
    // Type rules
    // ----------------------------------------
    "type-enum": [
      2,
      "always",
      [
        "feat", // New feature
        "fix", // Bug fix
        "docs", // Documentation
        "style", // Formatting
        "refactor", // Code restructuring
        "perf", // Performance
        "test", // Tests
        "build", // Build system
        "ci", // CI/CD
        "chore", // Maintenance
        "revert", // Revert commit
      ],
    ],
    "type-case": [2, "always", "lower-case"],
    "type-empty": [2, "never"],

    // ----------------------------------------
    // Scope rules
    // ----------------------------------------
    "scope-case": [2, "always", "lower-case"],
    "scope-enum": [
      1, // Warning (not error) — allows new scopes
      "always",
      [
        // Backend scopes
        "auth",
        "users",
        "tenants",
        "products",
        "inventory",
        "orders",
        "pos",
        "payments",
        "reports",
        "api",
        "models",
        "admin",
        "celery",
        "cache",

        // Frontend scopes
        "ui",
        "dashboard",
        "webstore",
        "hooks",
        "store",
        "forms",
        "layout",

        // Infrastructure scopes
        "docker",
        "ci",
        "nginx",
        "db",
        "deps",
        "config",

        // Project scopes (used during setup)
        "git",
        "quality",
        "docs",
      ],
    ],

    // ----------------------------------------
    // Subject rules
    // ----------------------------------------
    "subject-case": [2, "always", "lower-case"],
    "subject-empty": [2, "never"],
    "subject-full-stop": [2, "never", "."],
    "subject-max-length": [1, "always", 72],

    // ----------------------------------------
    // Header rules
    // ----------------------------------------
    "header-max-length": [2, "always", 72],

    // ----------------------------------------
    // Body rules
    // ----------------------------------------
    "body-leading-blank": [2, "always"],
    "body-max-line-length": [1, "always", 100],

    // ----------------------------------------
    // Footer rules
    // ----------------------------------------
    "footer-leading-blank": [2, "always"],
    "footer-max-line-length": [1, "always", 100],
  },
};
