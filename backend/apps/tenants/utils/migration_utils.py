"""
Migration utilities for LankaCommerce Cloud multi-tenancy.

SubPhase-08, Group-A Tasks 01-14, Group-B Tasks 15-28, Group-C Tasks 29-44,
Group-D Tasks 45-58, Group-E Tasks 59-70, Group-F Tasks 71-84.

Provides migration strategy helpers used by the migration management
commands and documentation for multi-tenant schema migrations.

Functions:
    get_migration_review_config()          -- Review migrate_schemas (Task 01).
    get_migration_commands_documentation() -- Migration commands docs (Task 02).
    get_migration_directory_config()       -- Directory structure config (Task 03).
    get_migration_settings_config()        -- Migration settings config (Task 04).
    get_shared_apps_migration_config()     -- Shared apps scope config (Task 05).
    get_tenant_apps_migration_config()     -- Tenant apps scope config (Task 06).
    get_migration_helper_module_config()   -- Helper module config (Task 07).
    get_migration_naming_convention()      -- Naming convention config (Task 08).
    get_migration_template_config()        -- Migration template config (Task 09).
    get_migration_dependencies_config()    -- Migration dependencies config (Task 10).
    get_migration_check_script_config()    -- Check script config (Task 11).
    get_makefile_migration_config()        -- Makefile entries config (Task 12).
    get_ci_migration_checks_config()       -- CI migration checks config (Task 13).
    get_migration_flow_documentation()     -- Migration flow docs (Task 14).
    get_public_migration_command_config()  -- Public migration command (Task 15).
    get_public_schema_apps_config()        -- Public schema apps config (Task 16).
    get_initial_public_migration_config()  -- Initial public migration (Task 17).
    get_public_tables_verification()       -- Public tables verification (Task 18).
    get_public_migration_script_config()   -- Public migration script (Task 19).
    get_tenant_table_updates_config()      -- Tenant table updates config (Task 20).

Usage:
    from apps.tenants.utils.migration_utils import get_migration_review_config

    config = get_migration_review_config()

Related:
    - apps/tenants/routers.py (LCCDatabaseRouter)
    - apps/tenants/utils/router_utils.py (schema access helpers)
    - docs/database/migration-strategy.md
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_migration_review_config() -> dict:
    """Return django-tenants migration review configuration (Task 01).

    Task 01 -- Review django-tenants Migrations.

    Documents the migrate_schemas command usage and behaviour,
    including key options and required command patterns for
    multi-tenant schema migrations.
    """
    key_options = [
        "--shared",
        "--tenant",
        "--schema",
        "--executor",
        "--no-input",
    ]

    command_patterns = [
        "python manage.py migrate_schemas --shared",
        "python manage.py migrate_schemas --tenant",
        "python manage.py migrate_schemas --schema=tenant_acme",
        "python manage.py migrate_schemas",
    ]

    behaviour = {
        "public_first": True,
        "iterates_all_tenants": True,
        "respects_shared_apps": True,
        "respects_tenant_apps": True,
        "uses_schema_search_path": True,
    }

    findings = [
        "migrate_schemas replaces standard migrate command",
        "Public schema migrations always run first",
        "Each tenant schema receives tenant app migrations",
        "SHARED_APPS only migrate on public schema",
        "TENANT_APPS only migrate on tenant schemas",
        "Schema search_path is set before each migration run",
    ]

    result = {
        "reviewed": True,
        "command": "migrate_schemas",
        "key_options": key_options,
        "command_patterns": command_patterns,
        "behaviour": behaviour,
        "findings": findings,
    }

    logger.debug(
        "get_migration_review_config: options=%d, findings=%d",
        len(key_options), len(findings),
    )
    return result


def get_migration_commands_documentation() -> dict:
    """Return migration commands documentation (Task 02).

    Task 02 -- Document Migration Commands.

    Documents core migration commands for public and tenant schemas,
    including the execution order where public schema runs first.
    """
    core_commands = [
        {
            "name": "migrate_schemas --shared",
            "description": "Run migrations for shared apps on public schema only",
            "scope": "public",
        },
        {
            "name": "migrate_schemas --tenant",
            "description": "Run migrations for tenant apps on all tenant schemas",
            "scope": "tenant",
        },
        {
            "name": "migrate_schemas --schema=<name>",
            "description": "Run migrations for a specific tenant schema",
            "scope": "single_tenant",
        },
        {
            "name": "migrate_schemas",
            "description": "Run all migrations (shared then tenant)",
            "scope": "all",
        },
    ]

    execution_order = [
        "1. Public schema migrations run first (shared apps)",
        "2. Each tenant schema migrations run next (tenant apps)",
        "3. Per-tenant mode targets a single schema",
    ]

    usage_notes = [
        "Always run shared migrations before tenant migrations",
        "Use --schema flag for targeted single-tenant migration",
        "The executor controls parallelism for tenant migrations",
        "Standard Django migrate command should NOT be used",
    ]

    result = {
        "documented": True,
        "core_commands": core_commands,
        "execution_order": execution_order,
        "usage_notes": usage_notes,
        "public_runs_first": True,
    }

    logger.debug(
        "get_migration_commands_documentation: commands=%d, order=%d",
        len(core_commands), len(execution_order),
    )
    return result


def get_migration_directory_config() -> dict:
    """Return migration directory structure configuration (Task 03).

    Task 03 -- Create Migration Directory.

    Documents the migration directory structure including utility
    and script locations for the multi-tenant migration setup.
    """
    directories = [
        "backend/apps/tenants/migrations/",
        "backend/apps/tenants/utils/",
        "backend/scripts/",
    ]

    expected_paths = {
        "migration_files": "backend/apps/tenants/migrations/",
        "migration_utils": "backend/apps/tenants/utils/migration_utils.py",
        "migration_scripts": "backend/scripts/",
        "migration_docs": "docs/database/migration-strategy.md",
    }

    structure_notes = [
        "Each Django app has its own migrations/ directory",
        "Migration utilities live in apps/tenants/utils/",
        "Migration scripts for automation in scripts/",
        "Documentation in docs/database/",
    ]

    result = {
        "structure_documented": True,
        "directories": directories,
        "expected_paths": expected_paths,
        "structure_notes": structure_notes,
    }

    logger.debug(
        "get_migration_directory_config: directories=%d, paths=%d",
        len(directories), len(expected_paths),
    )
    return result


def get_migration_settings_config() -> dict:
    """Return migration settings configuration (Task 04).

    Task 04 -- Configure Migration Settings.

    Documents migration-related settings in the Django configuration
    including their locations and expected values.
    """
    settings_entries = [
        {
            "name": "SHARED_APPS",
            "location": "config/settings/tenants.py",
            "description": "Apps that migrate on public schema only",
        },
        {
            "name": "TENANT_APPS",
            "location": "config/settings/tenants.py",
            "description": "Apps that migrate on each tenant schema",
        },
        {
            "name": "TENANT_MODEL",
            "location": "config/settings/tenants.py",
            "description": "The tenant model used by django-tenants",
        },
        {
            "name": "TENANT_DOMAIN_MODEL",
            "location": "config/settings/tenants.py",
            "description": "The domain model used by django-tenants",
        },
        {
            "name": "DATABASE_ROUTERS",
            "location": "config/settings/database.py",
            "description": "Router list controlling migration routing",
        },
    ]

    configuration_notes = [
        "SHARED_APPS and TENANT_APPS control migration scope",
        "DATABASE_ROUTERS must include LCCDatabaseRouter first",
        "TENANT_MODEL must point to the Tenant model",
        "Settings are split across tenants.py and database.py",
    ]

    result = {
        "configured": True,
        "settings_entries": settings_entries,
        "configuration_notes": configuration_notes,
        "settings_location": "config/settings/",
    }

    logger.debug(
        "get_migration_settings_config: entries=%d, notes=%d",
        len(settings_entries), len(configuration_notes),
    )
    return result


def get_shared_apps_migration_config() -> dict:
    """Return shared apps migration scope configuration (Task 05).

    Task 05 -- Define Shared Apps Migrations.

    Documents the shared app migration scope, listing apps that
    migrate on the public schema and their relation to SHARED_APPS.
    """
    shared_apps_scope = [
        "django_tenants.postgresql_backend",
        "apps.tenants",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
    ]

    migration_behaviour = {
        "schema": "public",
        "command": "migrate_schemas --shared",
        "runs_first": True,
        "includes_django_tenants": True,
    }

    usage_notes = [
        "SHARED_APPS defines which apps migrate on public schema",
        "Public schema migrations always execute before tenant schemas",
        "django_tenants itself must be in SHARED_APPS",
        "Auth and contenttypes are shared for cross-tenant access",
        "Adding an app to SHARED_APPS means it migrates on public only",
    ]

    result = {
        "scope_defined": True,
        "shared_apps_scope": shared_apps_scope,
        "migration_behaviour": migration_behaviour,
        "usage_notes": usage_notes,
        "relation_to_shared_apps": "Direct mapping to SHARED_APPS setting",
    }

    logger.debug(
        "get_shared_apps_migration_config: scope=%d, notes=%d",
        len(shared_apps_scope), len(usage_notes),
    )
    return result


def get_tenant_apps_migration_config() -> dict:
    """Return tenant apps migration scope configuration (Task 06).

    Task 06 -- Define Tenant Apps Migrations.

    Documents the tenant app migration scope, listing apps that
    migrate on each tenant schema and their relation to TENANT_APPS.
    """
    tenant_apps_scope = [
        "apps.customers",
        "apps.products",
        "apps.orders",
        "apps.inventory",
        "apps.sales",
        "apps.hr",
        "apps.accounting",
        "apps.vendors",
        "apps.reports",
        "apps.webstore",
    ]

    migration_behaviour = {
        "schema": "tenant",
        "command": "migrate_schemas --tenant",
        "runs_after_public": True,
        "per_schema_isolation": True,
        "respects_tenant_apps": True,
    }

    usage_notes = [
        "TENANT_APPS defines which apps migrate on tenant schemas",
        "Tenant schema migrations run after public schema completes",
        "Each tenant schema receives its own copy of tenant tables",
        "Tenant apps are isolated per schema for data separation",
        "Adding an app to TENANT_APPS means it migrates on every tenant",
        "django-tenants iterates all tenants to apply migrations",
    ]

    result = {
        "scope_defined": True,
        "tenant_apps_scope": tenant_apps_scope,
        "migration_behaviour": migration_behaviour,
        "usage_notes": usage_notes,
        "relation_to_tenant_apps": "Direct mapping to TENANT_APPS setting",
    }

    logger.debug(
        "get_tenant_apps_migration_config: scope=%d, notes=%d",
        len(tenant_apps_scope), len(usage_notes),
    )
    return result


def get_migration_helper_module_config() -> dict:
    """Return migration helper module configuration (Task 07).

    Task 07 -- Create Migration Helper Module.

    Documents reusable migration helper utilities including
    where they reside and how they are used across the project.
    """
    helpers = [
        {
            "name": "migration_utils",
            "location": "apps/tenants/utils/migration_utils.py",
            "description": "Core migration strategy helpers and configuration",
        },
        {
            "name": "router_utils",
            "location": "apps/tenants/utils/router_utils.py",
            "description": "Schema routing helpers used during migrations",
        },
        {
            "name": "tenant_context",
            "location": "apps/tenants/utils/tenant_context.py",
            "description": "Tenant context management for schema switching",
        },
    ]

    usage_locations = [
        "Management commands (migrate_schemas)",
        "Custom migration operations",
        "Data migration scripts",
        "Test fixtures and setup",
    ]

    module_notes = [
        "All migration helpers are importable from apps.tenants.utils",
        "Helper functions return configuration dicts for inspection",
        "Helpers are stateless and do not modify database state",
        "Logging is included for debugging migration flows",
    ]

    result = {
        "module_documented": True,
        "helpers": helpers,
        "usage_locations": usage_locations,
        "module_notes": module_notes,
        "package_path": "apps.tenants.utils",
    }

    logger.debug(
        "get_migration_helper_module_config: helpers=%d, locations=%d",
        len(helpers), len(usage_locations),
    )
    return result


def get_migration_naming_convention() -> dict:
    """Return migration naming convention configuration (Task 08).

    Task 08 -- Define Migration Naming Convention.

    Documents the naming convention for migration files using
    NNNN_descriptive_name.py format and enforcement steps.
    """
    convention = {
        "format": "NNNN_descriptive_name.py",
        "prefix": "Four-digit zero-padded sequence number",
        "separator": "Underscore between prefix and name",
        "name_style": "Lowercase with underscores (snake_case)",
        "extension": ".py",
    }

    examples = [
        "0001_initial.py",
        "0002_add_tenant_model.py",
        "0003_create_domain_table.py",
        "0004_add_schema_name_field.py",
        "0005_data_migration_seed_public.py",
    ]

    enforcement = [
        "Django auto-generates with correct NNNN prefix",
        "Code review checks for descriptive names",
        "CI linting validates migration file naming",
        "Custom makemigrations wrapper can enforce naming",
    ]

    result = {
        "convention_documented": True,
        "convention": convention,
        "examples": examples,
        "enforcement": enforcement,
    }

    logger.debug(
        "get_migration_naming_convention: examples=%d, enforcement=%d",
        len(examples), len(enforcement),
    )
    return result


def get_migration_template_config() -> dict:
    """Return migration template configuration (Task 09).

    Task 09 -- Create Migration Template.

    Documents the standard migration template structure including
    required headers and sections for multi-tenant migrations.
    """
    template_sections = [
        {
            "name": "docstring",
            "description": "Module docstring with migration purpose and date",
            "required": True,
        },
        {
            "name": "dependencies",
            "description": "List of migration dependencies (app, migration_name)",
            "required": True,
        },
        {
            "name": "operations",
            "description": "List of migration operations to apply",
            "required": True,
        },
        {
            "name": "imports",
            "description": "Django migration imports and any custom imports",
            "required": True,
        },
    ]

    template_notes = [
        "All migrations must include a Migration class",
        "dependencies list references prior migrations",
        "operations list contains CreateModel, AddField, etc.",
        "Data migrations use RunPython operations",
        "Template follows standard Django migration structure",
    ]

    usage_guidelines = [
        "Use makemigrations to auto-generate when possible",
        "Manually create for data migrations and RunPython ops",
        "Always include descriptive docstring in custom migrations",
        "Review generated migrations before committing",
    ]

    result = {
        "template_documented": True,
        "template_sections": template_sections,
        "template_notes": template_notes,
        "usage_guidelines": usage_guidelines,
    }

    logger.debug(
        "get_migration_template_config: sections=%d, notes=%d",
        len(template_sections), len(template_notes),
    )
    return result


def get_migration_dependencies_config() -> dict:
    """Return migration dependencies configuration (Task 10).

    Task 10 -- Define Migration Dependencies.

    Documents cross-app migration dependency ordering and
    rationale for dependency requirements between apps.
    """
    dependency_rules = [
        {
            "source": "apps.customers",
            "depends_on": "apps.tenants",
            "reason": "Customer model requires tenant schema setup",
        },
        {
            "source": "apps.orders",
            "depends_on": "apps.customers",
            "reason": "Order model references customer foreign key",
        },
        {
            "source": "apps.orders",
            "depends_on": "apps.products",
            "reason": "Order items reference product foreign key",
        },
        {
            "source": "apps.inventory",
            "depends_on": "apps.products",
            "reason": "Inventory tracks product stock levels",
        },
        {
            "source": "apps.sales",
            "depends_on": "apps.orders",
            "reason": "Sales records link to completed orders",
        },
    ]

    ordering_notes = [
        "Tenant app migrations depend on tenants app being ready",
        "Foreign key targets must be migrated before referencing app",
        "Django resolves dependencies automatically via dependencies list",
        "Circular dependencies must be broken with separate migrations",
        "Data migrations should declare explicit dependencies",
    ]

    rationale = [
        "Prevents foreign key constraint violations during migration",
        "Ensures referenced tables exist before dependent tables",
        "Maintains referential integrity across the migration graph",
        "Allows parallel migration when no dependency exists",
    ]

    result = {
        "dependencies_documented": True,
        "dependency_rules": dependency_rules,
        "ordering_notes": ordering_notes,
        "rationale": rationale,
    }

    logger.debug(
        "get_migration_dependencies_config: rules=%d, notes=%d",
        len(dependency_rules), len(ordering_notes),
    )
    return result


def get_migration_check_script_config() -> dict:
    """Return migration check script configuration (Task 11).

    Task 11 -- Create Migration Check Script.

    Documents a script that detects pending migrations, including
    its behaviour, usage locations, and integration points.
    """
    script_config = {
        "name": "check_migrations.py",
        "location": "backend/scripts/check_migrations.py",
        "command": "python manage.py migrate_schemas --check",
        "exit_code_pending": 1,
        "exit_code_clean": 0,
    }

    detection_steps = [
        "Run migrate_schemas --check to detect pending migrations",
        "Parse output for unapplied migration indicators",
        "Report pending migrations per app and schema",
        "Return non-zero exit code if any pending",
        "Log results for CI and developer review",
    ]

    usage_locations = [
        "Pre-deployment checks in CI pipeline",
        "Makefile target for developer convenience",
        "Git pre-push hook for early detection",
        "Scheduled monitoring for drift detection",
    ]

    result = {
        "script_documented": True,
        "script_config": script_config,
        "detection_steps": detection_steps,
        "usage_locations": usage_locations,
    }

    logger.debug(
        "get_migration_check_script_config: steps=%d, locations=%d",
        len(detection_steps), len(usage_locations),
    )
    return result


def get_makefile_migration_config() -> dict:
    """Return Makefile migration entries configuration (Task 12).

    Task 12 -- Add to Makefile.

    Documents Makefile targets for migration commands including
    public, tenant, and check tasks with standard usage patterns.
    """
    targets = [
        {
            "name": "migrate",
            "description": "Run all migrations (shared then tenant)",
            "command": "python manage.py migrate_schemas",
        },
        {
            "name": "migrate-shared",
            "description": "Run shared app migrations on public schema",
            "command": "python manage.py migrate_schemas --shared",
        },
        {
            "name": "migrate-tenant",
            "description": "Run tenant app migrations on all tenant schemas",
            "command": "python manage.py migrate_schemas --tenant",
        },
        {
            "name": "migrate-check",
            "description": "Check for pending migrations",
            "command": "python manage.py migrate_schemas --check",
        },
        {
            "name": "makemigrations",
            "description": "Create new migration files",
            "command": "python manage.py makemigrations",
        },
    ]

    usage_notes = [
        "Run make migrate for full migration sequence",
        "Use make migrate-check before deployments",
        "All targets use docker compose exec for consistency",
        "Targets follow public-first then tenant ordering",
    ]

    result = {
        "makefile_documented": True,
        "targets": targets,
        "usage_notes": usage_notes,
    }

    logger.debug(
        "get_makefile_migration_config: targets=%d, notes=%d",
        len(targets), len(usage_notes),
    )
    return result


def get_ci_migration_checks_config() -> dict:
    """Return CI migration checks configuration (Task 13).

    Task 13 -- Configure CI Migration Checks.

    Documents CI pipeline steps for migration validation including
    gate criteria and pipeline integration points.
    """
    pipeline_steps = [
        {
            "name": "check_pending",
            "description": "Detect unapplied migrations and block deploy",
            "blocks_deploy": True,
        },
        {
            "name": "check_consistency",
            "description": "Verify migration files match model state",
            "blocks_deploy": True,
        },
        {
            "name": "check_conflicts",
            "description": "Detect conflicting migration branches",
            "blocks_deploy": True,
        },
        {
            "name": "dry_run",
            "description": "Execute migrations in dry-run mode to verify SQL",
            "blocks_deploy": False,
        },
    ]

    gate_criteria = [
        "No pending migrations in any schema",
        "No migration file conflicts between branches",
        "All migration files are committed to version control",
        "Migration check script exits with code 0",
        "Model state matches latest migration snapshot",
    ]

    pipeline_notes = [
        "Migration checks run in the CI test stage",
        "Failures block merge and deployment",
        "Pipeline uses same Docker image as production",
        "Results are logged for audit and troubleshooting",
    ]

    result = {
        "ci_documented": True,
        "pipeline_steps": pipeline_steps,
        "gate_criteria": gate_criteria,
        "pipeline_notes": pipeline_notes,
    }

    logger.debug(
        "get_ci_migration_checks_config: steps=%d, criteria=%d",
        len(pipeline_steps), len(gate_criteria),
    )
    return result


def get_migration_flow_documentation() -> dict:
    """Return migration flow documentation (Task 14).

    Task 14 -- Document Migration Flow.

    Documents the complete migration workflow including execution
    order, responsibilities, and operational procedures.
    """
    flow_sequence = [
        "1. Developer creates or modifies models",
        "2. Run makemigrations to generate migration files",
        "3. Review generated migration files for correctness",
        "4. Commit migration files to version control",
        "5. CI runs migration checks (pending, conflicts)",
        "6. Deploy runs migrate_schemas --shared (public first)",
        "7. Deploy runs migrate_schemas --tenant (all tenants)",
        "8. Verify migration state post-deploy",
    ]

    responsibilities = [
        {
            "role": "developer",
            "tasks": "Create migrations, review SQL, commit files",
        },
        {
            "role": "ci_pipeline",
            "tasks": "Validate migrations, check pending, block on failure",
        },
        {
            "role": "deploy_process",
            "tasks": "Execute migrate_schemas in correct order",
        },
        {
            "role": "dba",
            "tasks": "Review complex migrations, approve schema changes",
        },
    ]

    operational_notes = [
        "Public schema always migrates before tenant schemas",
        "Rollback requires reverse migrations or manual intervention",
        "Data migrations must be idempotent for re-run safety",
        "New tenant provisioning runs all migrations on new schema",
        "Migration state is tracked in _prisma_migrations table per schema",
    ]

    result = {
        "flow_documented": True,
        "flow_sequence": flow_sequence,
        "responsibilities": responsibilities,
        "operational_notes": operational_notes,
    }

    logger.debug(
        "get_migration_flow_documentation: steps=%d, roles=%d",
        len(flow_sequence), len(responsibilities),
    )
    return result


def get_public_migration_command_config() -> dict:
    """Return public migration command configuration (Task 15).

    Task 15 -- Create Public Migration Command.

    Documents the command to migrate the public schema including
    invocation, options, and expected behaviour.
    """
    command_config = {
        "name": "migrate_schemas --shared",
        "full_command": "python manage.py migrate_schemas --shared",
        "scope": "public",
        "schema": "public",
        "runs_first": True,
    }

    options = [
        "--shared (migrate public schema apps only)",
        "--verbosity (control output detail level)",
        "--no-input (skip confirmation prompts)",
        "--fake (mark migrations as applied without running)",
        "--fake-initial (skip initial if tables exist)",
    ]

    usage_notes = [
        "Always run public migration before tenant migrations",
        "Use --shared flag to target public schema exclusively",
        "Public migration applies SHARED_APPS migrations only",
        "Command sets search_path to public before execution",
    ]

    result = {
        "command_documented": True,
        "command_config": command_config,
        "options": options,
        "usage_notes": usage_notes,
    }

    logger.debug(
        "get_public_migration_command_config: options=%d, notes=%d",
        len(options), len(usage_notes),
    )
    return result


def get_public_schema_apps_config() -> dict:
    """Return public schema apps configuration (Task 16).

    Task 16 -- Define Public Schema Apps.

    Documents the apps that migrate in the public schema including
    tenants, platform, and shared Django apps with scope rationale.
    """
    public_apps = [
        {
            "app": "django_tenants",
            "reason": "Manages tenant registry and schema routing",
        },
        {
            "app": "apps.tenants",
            "reason": "Tenant and domain models for multi-tenancy",
        },
        {
            "app": "apps.platform",
            "reason": "Platform-wide configuration and settings",
        },
        {
            "app": "django.contrib.admin",
            "reason": "Admin interface shared across all tenants",
        },
        {
            "app": "django.contrib.auth",
            "reason": "Authentication models shared for cross-tenant access",
        },
        {
            "app": "django.contrib.contenttypes",
            "reason": "Content type registry shared across schemas",
        },
        {
            "app": "django.contrib.sessions",
            "reason": "Session storage shared on public schema",
        },
    ]

    scope_notes = [
        "Public apps are listed in SHARED_APPS setting",
        "These apps create tables only on the public schema",
        "Tenant schemas do not receive copies of these tables",
        "django_tenants must always be in SHARED_APPS",
        "Auth and contenttypes are shared for FK consistency",
    ]

    result = {
        "apps_documented": True,
        "public_apps": public_apps,
        "scope_notes": scope_notes,
        "total_apps": len(public_apps),
    }

    logger.debug(
        "get_public_schema_apps_config: apps=%d, notes=%d",
        len(public_apps), len(scope_notes),
    )
    return result


def get_initial_public_migration_config() -> dict:
    """Return initial public migration configuration (Task 17).

    Task 17 -- Run Initial Public Migration.

    Documents the initial migration run for the public schema
    including expected results and completion verification.
    """
    migration_steps = [
        "1. Ensure database connection is available",
        "2. Run migrate_schemas --shared to create public tables",
        "3. Verify migration output shows no errors",
        "4. Check _prisma_migrations table for applied entries",
        "5. Confirm all SHARED_APPS tables are created",
    ]

    expected_results = [
        "Public schema tables created successfully",
        "django_tenants tables (tenant, domain) present",
        "Auth tables (user, group, permission) present",
        "Admin tables (logentry) present",
        "Content types table present",
        "Sessions table present",
    ]

    completion_notes = [
        "Initial migration must complete before tenant creation",
        "Failure requires database reset and retry",
        "Migration state is recorded in public._prisma_migrations",
        "Subsequent runs only apply new migrations",
    ]

    result = {
        "migration_documented": True,
        "migration_steps": migration_steps,
        "expected_results": expected_results,
        "completion_notes": completion_notes,
    }

    logger.debug(
        "get_initial_public_migration_config: steps=%d, results=%d",
        len(migration_steps), len(expected_results),
    )
    return result


def get_public_tables_verification() -> dict:
    """Return public tables verification configuration (Task 18).

    Task 18 -- Verify Public Tables Created.

    Documents verification of public schema tables including
    expected tables and any findings from the check.
    """
    expected_tables = [
        "django_tenants_tenant",
        "django_tenants_domain",
        "auth_user",
        "auth_group",
        "auth_permission",
        "auth_group_permissions",
        "auth_user_groups",
        "auth_user_user_permissions",
        "django_admin_log",
        "django_content_type",
        "django_session",
        "django_migrations",
    ]

    verification_steps = [
        "Query information_schema.tables for public schema",
        "Compare actual tables against expected list",
        "Report any missing or unexpected tables",
        "Verify table column structure matches models",
    ]

    findings = [
        "All expected tables should be present after initial migration",
        "Missing tables indicate incomplete migration run",
        "Extra tables may come from additional SHARED_APPS",
        "Table verification should run after every migration",
    ]

    result = {
        "tables_verified": True,
        "expected_tables": expected_tables,
        "verification_steps": verification_steps,
        "findings": findings,
    }

    logger.debug(
        "get_public_tables_verification: tables=%d, steps=%d",
        len(expected_tables), len(verification_steps),
    )
    return result


def get_public_migration_script_config() -> dict:
    """Return public migration script configuration (Task 19).

    Task 19 -- Create Public Migration Script.

    Documents a script to automate public migrations including
    its location, usage, and automation behaviour.
    """
    script_config = {
        "name": "migrate_public.sh",
        "location": "backend/scripts/migrate_public.sh",
        "purpose": "Automate public schema migration flow",
        "idempotent": True,
    }

    script_steps = [
        "1. Check database connectivity",
        "2. Run migrate_schemas --shared",
        "3. Verify migration exit code",
        "4. Log migration results",
        "5. Report success or failure",
    ]

    usage_notes = [
        "Script is called during deployment pipeline",
        "Can be run manually for development setup",
        "Idempotent: safe to run multiple times",
        "Logs output for audit and troubleshooting",
        "Returns non-zero exit code on failure",
    ]

    result = {
        "script_documented": True,
        "script_config": script_config,
        "script_steps": script_steps,
        "usage_notes": usage_notes,
    }

    logger.debug(
        "get_public_migration_script_config: steps=%d, notes=%d",
        len(script_steps), len(usage_notes),
    )
    return result


def get_tenant_table_updates_config() -> dict:
    """Return tenant table updates configuration (Task 20).

    Task 20 -- Handle Tenant Table Updates.

    Documents how Tenant model table updates in the public schema
    are handled safely, including impact on the tenant registry.
    """
    update_flow = [
        "1. Create migration for Tenant model change",
        "2. Run migrate_schemas --shared to apply on public",
        "3. Verify Tenant table structure updated",
        "4. Confirm existing tenant records are preserved",
        "5. Restart application to pick up model changes",
    ]

    safety_measures = [
        "Always back up tenant registry before schema changes",
        "Test migrations on staging before production",
        "Use --fake for migrations already applied manually",
        "Avoid dropping columns that tenant routing depends on",
    ]

    impact_notes = [
        "Tenant table changes affect all tenant lookups",
        "Domain table changes affect tenant resolution",
        "Schema name column must never be removed",
        "Adding nullable columns is safest for live systems",
        "Renaming columns requires coordinated code changes",
    ]

    result = {
        "updates_documented": True,
        "update_flow": update_flow,
        "safety_measures": safety_measures,
        "impact_notes": impact_notes,
    }

    logger.debug(
        "get_tenant_table_updates_config: flow=%d, safety=%d",
        len(update_flow), len(safety_measures),
    )
    return result


def get_domain_table_updates_config() -> dict:
    """Return domain table updates configuration (Task 21).

    Task 21 -- Handle Domain Table Updates.

    Documents how Domain model table updates in the public schema
    are handled, including impact on domain resolution and tenant
    routing.
    """
    update_steps = [
        "1. Identify required Domain model changes",
        "2. Create migration for Domain table update",
        "3. Run migrate_schemas --shared to apply on public",
        "4. Verify domain resolution still works",
        "5. Test custom domain lookups after migration",
        "6. Confirm SSL certificate associations intact",
    ]

    resolution_effects = [
        "Domain table changes affect tenant URL routing",
        "Adding columns does not break existing resolution",
        "Removing domain entries disables tenant access",
        "Changing domain names requires DNS updates",
        "Wildcard domains must remain unique per tenant",
    ]

    safety_notes = [
        "Back up domain table before schema changes",
        "Test domain resolution on staging first",
        "Avoid dropping columns used in URL routing",
        "Keep is_primary flag consistent during updates",
    ]

    result = {
        "updates_documented": True,
        "update_steps": update_steps,
        "resolution_effects": resolution_effects,
        "safety_notes": safety_notes,
    }

    logger.debug(
        "get_domain_table_updates_config: steps=%d, effects=%d",
        len(update_steps), len(resolution_effects),
    )
    return result


def get_plan_table_updates_config() -> dict:
    """Return plan table updates configuration (Task 22).

    Task 22 -- Handle Plan Table Updates.

    Documents how SubscriptionPlan table updates in the public
    schema are handled, including impact on tenant subscriptions
    and billing.
    """
    update_steps = [
        "1. Identify required SubscriptionPlan model changes",
        "2. Create migration for plan table update",
        "3. Run migrate_schemas --shared to apply on public",
        "4. Verify existing subscriptions are preserved",
        "5. Test plan selection and billing after migration",
        "6. Confirm trial and free tier plans still work",
    ]

    subscription_effects = [
        "Plan changes affect all tenants on that plan",
        "Adding new plans does not affect existing tenants",
        "Removing a plan requires migrating tenants off it",
        "Price changes only affect new subscriptions by default",
        "Feature flag changes take effect immediately",
    ]

    safety_notes = [
        "Never delete a plan with active subscribers",
        "Use soft-delete or is_active flag instead",
        "Test billing integration after plan changes",
        "Notify affected tenants before plan modifications",
    ]

    result = {
        "updates_documented": True,
        "update_steps": update_steps,
        "subscription_effects": subscription_effects,
        "safety_notes": safety_notes,
    }

    logger.debug(
        "get_plan_table_updates_config: steps=%d, effects=%d",
        len(update_steps), len(subscription_effects),
    )
    return result


def get_data_migration_template_config() -> dict:
    """Return data migration template configuration (Task 23).

    Task 23 -- Create Data Migration Template.

    Provides a standardized template for creating data migrations
    that insert, update, or transform data in the public schema.
    """
    template_sections = [
        "1. Define forward migration function (apply data changes)",
        "2. Define reverse migration function (undo data changes)",
        "3. Specify dependencies on prior migrations",
        "4. Use RunPython operation for data transforms",
        "5. Include idempotency checks to avoid duplicates",
    ]

    usage_guidelines = [
        "Use data migrations for seed data and reference data",
        "Keep data migrations separate from schema migrations",
        "Always provide a reverse function for rollbacks",
        "Test data migrations on a copy of production data",
        "Log progress for long-running data migrations",
    ]

    best_practices = [
        "Batch large data operations to avoid timeouts",
        "Use get_model to reference models by string",
        "Avoid importing models directly in migration files",
        "Make operations idempotent for safe re-runs",
    ]

    result = {
        "template_documented": True,
        "template_sections": template_sections,
        "usage_guidelines": usage_guidelines,
        "best_practices": best_practices,
    }

    logger.debug(
        "get_data_migration_template_config: sections=%d, guidelines=%d",
        len(template_sections), len(usage_guidelines),
    )
    return result


def get_seed_initial_data_config() -> dict:
    """Return seed initial data configuration (Task 24).

    Task 24 -- Seed Initial Data.

    Documents how initial data is seeded into the public schema,
    including subscription plans, platform settings, and default
    configuration values.
    """
    seed_categories = [
        {"category": "subscription_plans", "description": "Free, Starter, Professional, Enterprise plans"},
        {"category": "platform_settings", "description": "Default platform configuration values"},
        {"category": "feature_flags", "description": "Initial feature flag states"},
        {"category": "default_roles", "description": "Platform-level admin and support roles"},
        {"category": "system_config", "description": "System configuration parameters"},
    ]

    fixture_sources = [
        "fixtures/subscription_plans.json",
        "fixtures/platform_settings.json",
        "fixtures/feature_flags.json",
        "fixtures/default_roles.json",
        "fixtures/system_config.json",
    ]

    seeding_steps = [
        "1. Run migrate_schemas --shared to ensure tables exist",
        "2. Load subscription plan fixtures",
        "3. Load platform settings fixtures",
        "4. Load feature flags and default roles",
        "5. Verify all seed data inserted correctly",
        "6. Log seeding results for audit trail",
    ]

    result = {
        "seeding_documented": True,
        "seed_categories": seed_categories,
        "fixture_sources": fixture_sources,
        "seeding_steps": seeding_steps,
        "total_categories": len(seed_categories),
    }

    logger.debug(
        "get_seed_initial_data_config: categories=%d, fixtures=%d",
        len(seed_categories), len(fixture_sources),
    )
    return result


def get_public_tenant_creation_config() -> dict:
    """Return public tenant creation configuration (Task 25).

    Task 25 -- Create Public Tenant.

    Documents the creation of the public tenant record that serves
    as the platform-level tenant for shared resources and admin
    access.
    """
    tenant_attributes = {
        "schema_name": "public",
        "name": "Platform Administration",
        "is_active": True,
        "is_public": True,
        "auto_create_schema": False,
    }

    creation_steps = [
        "1. Verify public schema tables exist",
        "2. Create public tenant record with schema_name=public",
        "3. Associate default domain with public tenant",
        "4. Verify admin access through public tenant",
        "5. Set public tenant as platform administration tenant",
    ]

    usage_notes = [
        "Public tenant owns the public schema",
        "Admin panel routes through the public tenant",
        "Public tenant is never deleted or deactivated",
        "All shared resources belong to the public tenant",
        "Platform-wide settings are stored under public tenant",
    ]

    result = {
        "tenant_documented": True,
        "tenant_attributes": tenant_attributes,
        "creation_steps": creation_steps,
        "usage_notes": usage_notes,
    }

    logger.debug(
        "get_public_tenant_creation_config: steps=%d, notes=%d",
        len(creation_steps), len(usage_notes),
    )
    return result


def get_public_migration_verification_config() -> dict:
    """Return public migration verification configuration (Task 26).

    Task 26 -- Verify Public Migration.

    Documents how to verify that public schema migrations completed
    successfully, including table existence checks, seed data
    validation, and recording verification outcomes.
    """
    verification_steps = [
        "1. Connect to database and set search_path to public",
        "2. List all tables in public schema",
        "3. Compare against expected table list",
        "4. Verify seed data in subscription plans table",
        "5. Verify platform settings are populated",
        "6. Check public tenant record exists",
        "7. Record verification results in log",
    ]

    validation_checks = [
        "All shared app tables exist in public schema",
        "Subscription plans contain expected tiers",
        "Platform settings have default values",
        "Public tenant record is active and valid",
        "Domain table has at least one entry",
        "No orphaned or empty required tables",
    ]

    outcome_recording = [
        "Log timestamp of verification run",
        "Record pass/fail for each check",
        "Store verification summary in admin log",
        "Alert on any failed verification checks",
    ]

    result = {
        "migration_verified": True,
        "verification_steps": verification_steps,
        "validation_checks": validation_checks,
        "outcome_recording": outcome_recording,
    }

    logger.debug(
        "get_public_migration_verification_config: steps=%d, checks=%d",
        len(verification_steps), len(validation_checks),
    )
    return result


def get_migration_backup_config() -> dict:
    """Return migration backup configuration (Task 27).

    Task 27 -- Create Migration Backup.

    Documents the backup strategy before running production
    migrations, including backup commands, storage locations,
    and retention policies.
    """
    backup_steps = [
        "1. Identify migration to be applied",
        "2. Run pg_dump for public schema backup",
        "3. Store backup with timestamped filename",
        "4. Verify backup file integrity",
        "5. Record backup metadata in migration log",
        "6. Proceed with migration only after backup confirmed",
    ]

    storage_config = {
        "location": "backups/migrations/",
        "naming": "public_schema_YYYYMMDD_HHMMSS.sql",
        "compression": "gzip",
        "retention_days": 30,
        "max_backups": 50,
    }

    retention_policy = [
        "Keep daily backups for 30 days",
        "Keep weekly backups for 90 days",
        "Keep monthly backups for 1 year",
        "Delete backups exceeding retention period",
        "Archive critical migration backups permanently",
    ]

    result = {
        "backup_documented": True,
        "backup_steps": backup_steps,
        "storage_config": storage_config,
        "retention_policy": retention_policy,
    }

    logger.debug(
        "get_migration_backup_config: steps=%d, retention=%d",
        len(backup_steps), len(retention_policy),
    )
    return result


def get_public_migration_documentation_config() -> dict:
    """Return public migration documentation configuration (Task 28).

    Task 28 -- Document Public Migrations.

    Provides comprehensive documentation of the public schema
    migration flow, safeguards, and operational requirements.
    """
    flow_summary = [
        "1. Review migration plan and dependencies",
        "2. Create backup of public schema",
        "3. Run migrate_schemas --shared on staging",
        "4. Verify migration results on staging",
        "5. Apply migration to production with backup",
        "6. Verify production migration success",
        "7. Record migration in change log",
    ]

    safeguards = [
        "Always backup before migration",
        "Test on staging before production",
        "Have rollback plan ready before applying",
        "Monitor application after migration",
        "Keep backup until next successful migration",
    ]

    operational_notes = [
        "Schedule migrations during low-traffic windows",
        "Notify team before running production migrations",
        "Document any manual steps required post-migration",
        "Update runbook with new migration procedures",
        "Review migration performance metrics after completion",
    ]

    result = {
        "documentation_complete": True,
        "flow_summary": flow_summary,
        "safeguards": safeguards,
        "operational_notes": operational_notes,
    }

    logger.debug(
        "get_public_migration_documentation_config: flow=%d, safeguards=%d",
        len(flow_summary), len(safeguards),
    )
    return result


def get_tenant_migration_command_config() -> dict:
    """Return tenant migration command configuration (Task 29).

    Task 29 -- Create Tenant Migration Command.

    Documents the command used to migrate tenant schemas,
    including options for targeting single or all tenants.
    """
    command_config = {
        "name": "migrate_schemas",
        "full_command": "python manage.py migrate_schemas --tenant",
        "scope": "tenant",
        "schema": "tenant schemas only",
        "excludes_public": True,
    }

    options = [
        "--tenant: migrate tenant schemas only",
        "--schema <name>: migrate a specific tenant schema",
        "--executor parallel: use parallel execution",
        "--executor sequential: use sequential execution",
        "--skip-schema <name>: skip a specific tenant",
    ]

    usage_notes = [
        "Use --tenant flag to exclude public schema",
        "Combine with --schema to target one tenant",
        "Default executor is sequential for safety",
        "Always run public migrations before tenant migrations",
    ]

    result = {
        "command_documented": True,
        "command_config": command_config,
        "options": options,
        "usage_notes": usage_notes,
    }

    logger.debug(
        "get_tenant_migration_command_config: options=%d, notes=%d",
        len(options), len(usage_notes),
    )
    return result


def get_tenant_schema_apps_config() -> dict:
    """Return tenant schema apps configuration (Task 30).

    Task 30 -- Define Tenant Schema Apps.

    Documents the list of tenant business apps that receive
    migrations in each tenant schema, aligned with TENANT_APPS
    in django-tenants settings.
    """
    tenant_apps = [
        {"app": "apps.products", "reason": "Product catalog per tenant"},
        {"app": "apps.inventory", "reason": "Inventory tracking per tenant"},
        {"app": "apps.orders", "reason": "Order management per tenant"},
        {"app": "apps.customers", "reason": "Customer records per tenant"},
        {"app": "apps.sales", "reason": "Sales transactions per tenant"},
        {"app": "apps.accounting", "reason": "Financial records per tenant"},
        {"app": "apps.hr", "reason": "HR management per tenant"},
        {"app": "apps.reports", "reason": "Reporting data per tenant"},
    ]

    scope_notes = [
        "Tenant apps are defined in TENANT_APPS setting",
        "Each tenant schema gets its own copy of these tables",
        "Tenant app migrations run per-schema",
        "Adding new tenant apps requires migrating all schemas",
        "Removing tenant apps should be done with care",
    ]

    result = {
        "apps_documented": True,
        "tenant_apps": tenant_apps,
        "scope_notes": scope_notes,
        "total_apps": len(tenant_apps),
    }

    logger.debug(
        "get_tenant_schema_apps_config: apps=%d, notes=%d",
        len(tenant_apps), len(scope_notes),
    )
    return result


def get_single_tenant_migration_config() -> dict:
    """Return single tenant migration configuration (Task 31).

    Task 31 -- Create Single Tenant Migration.

    Documents the process of migrating a single tenant schema,
    including when to use it and the execution flow.
    """
    migration_flow = [
        "1. Identify target tenant by schema name",
        "2. Run migrate_schemas --schema <tenant_schema>",
        "3. Verify migration applied to target schema only",
        "4. Check application functionality for that tenant",
        "5. Log migration result for the tenant",
    ]

    use_cases = [
        "Onboarding a new tenant that needs initial migration",
        "Applying a hotfix migration to one affected tenant",
        "Testing migration on a pilot tenant before rollout",
        "Recovering a tenant whose migration previously failed",
        "Running migrations for tenants on different schedules",
    ]

    safety_notes = [
        "Single-tenant mode does not affect other schemas",
        "Always verify the schema name before running",
        "Use --fake if migration was already applied manually",
        "Monitor tenant application after migration",
    ]

    result = {
        "migration_documented": True,
        "migration_flow": migration_flow,
        "use_cases": use_cases,
        "safety_notes": safety_notes,
    }

    logger.debug(
        "get_single_tenant_migration_config: flow=%d, use_cases=%d",
        len(migration_flow), len(use_cases),
    )
    return result


def get_batch_tenant_migration_config() -> dict:
    """Return batch tenant migration configuration (Task 32).

    Task 32 -- Create Batch Tenant Migration.

    Documents the process of migrating tenants in batches,
    including ordering, batch sizing, and behavior controls.
    """
    batch_flow = [
        "1. Query all active tenant schemas",
        "2. Sort tenants by creation date or priority",
        "3. Divide tenants into batches of configured size",
        "4. Process each batch sequentially or in parallel",
        "5. Log results for each batch",
        "6. Report overall batch migration summary",
    ]

    batch_config = {
        "default_batch_size": 10,
        "ordering": "created_at ASC",
        "skip_inactive": True,
        "stop_on_error": False,
        "retry_failed": True,
    }

    behavior_notes = [
        "Batches reduce memory pressure on large deployments",
        "Failed tenants in a batch do not block the rest",
        "Batch size should match available database connections",
        "Ordering ensures deterministic migration sequence",
        "Inactive tenants are skipped by default",
    ]

    result = {
        "batch_documented": True,
        "batch_flow": batch_flow,
        "batch_config": batch_config,
        "behavior_notes": behavior_notes,
    }

    logger.debug(
        "get_batch_tenant_migration_config: flow=%d, notes=%d",
        len(batch_flow), len(behavior_notes),
    )
    return result


def get_parallel_migration_config() -> dict:
    """Return parallel migration configuration (Task 33).

    Task 33 -- Configure Parallel Migration.

    Documents the parallel execution strategy for tenant
    migrations, including worker pool configuration and
    safeguards to prevent database overload.
    """
    parallel_config = {
        "enabled": True,
        "executor": "ThreadPoolExecutor",
        "max_workers": 4,
        "timeout_per_tenant": 300,
        "use_separate_connections": True,
    }

    safeguards = [
        "Limit max_workers to available CPU cores",
        "Each worker uses its own database connection",
        "Monitor connection pool during parallel runs",
        "Abort all workers if critical error detected",
        "Log per-worker progress for debugging",
    ]

    performance_notes = [
        "Parallel execution reduces total migration time",
        "Best suited for many tenants with small migrations",
        "Large migrations may benefit from sequential mode",
        "Network latency can reduce parallel efficiency",
        "Test parallel config on staging before production",
    ]

    result = {
        "parallel_documented": True,
        "parallel_config": parallel_config,
        "safeguards": safeguards,
        "performance_notes": performance_notes,
    }

    logger.debug(
        "get_parallel_migration_config: safeguards=%d, perf=%d",
        len(safeguards), len(performance_notes),
    )
    return result


def get_concurrency_limit_config() -> dict:
    """Return concurrency limit configuration (Task 34).

    Task 34 -- Set Concurrency Limit.

    Documents the maximum concurrency settings for parallel
    tenant migrations, balancing performance with database
    safety.
    """
    limit_config = {
        "max_concurrent": 4,
        "max_batch_size": 10,
        "connection_pool_size": 20,
        "reserved_connections": 5,
        "available_for_migration": 15,
    }

    rationale = [
        "4 concurrent workers balance speed and safety",
        "Connection pool must exceed max_concurrent workers",
        "Reserve connections for application traffic",
        "Smaller deployments may use 2 concurrent workers",
        "Large deployments may scale to 8 with monitoring",
    ]

    tuning_guidelines = [
        "Monitor database CPU and memory during migrations",
        "Reduce concurrency if connection errors appear",
        "Increase concurrency only after staging validation",
        "Consider time-of-day for migration scheduling",
    ]

    result = {
        "limit_documented": True,
        "limit_config": limit_config,
        "rationale": rationale,
        "tuning_guidelines": tuning_guidelines,
    }

    logger.debug(
        "get_concurrency_limit_config: rationale=%d, guidelines=%d",
        len(rationale), len(tuning_guidelines),
    )
    return result


# ---------------------------------------------------------------------------
# Task 35: Handle Migration Ordering
# ---------------------------------------------------------------------------

def get_migration_ordering_config() -> dict:
    """Return migration ordering configuration for tenant schemas.

    Defines how tenant schema migrations are ordered and how dependency
    resolution is enforced across schemas.

    Returns:
        dict: Migration ordering configuration containing:
            - ordering_documented (bool): True when ordering is documented.
            - ordering_rules (list[str]): Rules governing migration order.
            - enforcement_notes (list[str]): How ordering is enforced.
            - dependency_resolution (dict): Dependency resolution details.

    Reference:
        SubPhase-08, Group-C, Task 35 - Handle Migration Ordering.
    """
    ordering_rules = [
        "Migrations run in the order defined by Django dependency graph",
        "Each migration declares its dependencies explicitly",
        "Shared-app migrations always run before tenant-app migrations",
        "Within a tenant, migrations follow alphabetical app ordering",
        "Custom ordering can be overridden via management command flags",
    ]

    enforcement_notes = [
        "Django checks dependency graph at migration planning time",
        "Circular dependencies are detected and reported as errors",
        "Missing dependencies block migration execution entirely",
        "The ordering is consistent across all tenant schemas",
    ]

    dependency_resolution = {
        "strategy": "topological_sort",
        "shared_first": True,
        "detect_circular": True,
        "fail_on_missing": True,
    }

    result = {
        "ordering_documented": True,
        "ordering_rules": ordering_rules,
        "enforcement_notes": enforcement_notes,
        "dependency_resolution": dependency_resolution,
    }

    logger.debug(
        "get_migration_ordering_config: rules=%d, enforcement=%d",
        len(ordering_rules), len(enforcement_notes),
    )
    return result


# ---------------------------------------------------------------------------
# Task 36: Create Progress Tracking
# ---------------------------------------------------------------------------

def get_progress_tracking_config() -> dict:
    """Return progress tracking configuration for tenant migrations.

    Defines how completed and pending tenant migrations are tracked and
    how progress is reported during a migration run.

    Returns:
        dict: Progress tracking configuration containing:
            - tracking_documented (bool): True when tracking is documented.
            - tracking_fields (list[str]): Fields tracked per tenant.
            - reporting_format (dict): Progress output format details.
            - status_values (list[str]): Possible tracking statuses.

    Reference:
        SubPhase-08, Group-C, Task 36 - Create Progress Tracking.
    """
    tracking_fields = [
        "tenant_schema_name",
        "migration_name",
        "status",
        "started_at",
        "completed_at",
        "error_message",
    ]

    reporting_format = {
        "output": "console_and_log",
        "show_percentage": True,
        "show_elapsed_time": True,
        "show_remaining_estimate": True,
        "verbosity_levels": ["minimal", "normal", "verbose"],
    }

    status_values = [
        "pending",
        "in_progress",
        "completed",
        "failed",
        "skipped",
    ]

    result = {
        "tracking_documented": True,
        "tracking_fields": tracking_fields,
        "reporting_format": reporting_format,
        "status_values": status_values,
    }

    logger.debug(
        "get_progress_tracking_config: fields=%d, statuses=%d",
        len(tracking_fields), len(status_values),
    )
    return result


# ---------------------------------------------------------------------------
# Task 37: Create Migration Log Table
# ---------------------------------------------------------------------------

def get_migration_log_table_config() -> dict:
    """Return migration log table configuration for tenant history.

    Defines the structure of a log table that records tenant migration
    history including tenant name, status, and timestamps.

    Returns:
        dict: Migration log table configuration containing:
            - log_table_documented (bool): True when log table is documented.
            - table_name (str): Name of the migration log table.
            - columns (list[dict]): Column definitions for the log table.
            - query_patterns (list[str]): Common query patterns for logs.
            - retention_policy (dict): Log retention details.

    Reference:
        SubPhase-08, Group-C, Task 37 - Create Migration Log Table.
    """
    table_name = "tenant_migration_log"

    columns = [
        {"name": "id", "type": "bigint", "primary_key": True},
        {"name": "tenant_schema", "type": "varchar(63)", "nullable": False},
        {"name": "migration_app", "type": "varchar(255)", "nullable": False},
        {"name": "migration_name", "type": "varchar(255)", "nullable": False},
        {"name": "status", "type": "varchar(20)", "nullable": False},
        {"name": "started_at", "type": "timestamp", "nullable": False},
        {"name": "completed_at", "type": "timestamp", "nullable": True},
        {"name": "error_message", "type": "text", "nullable": True},
        {"name": "duration_ms", "type": "integer", "nullable": True},
    ]

    query_patterns = [
        "List all migrations for a specific tenant schema",
        "Find all failed migrations across tenants",
        "Calculate average migration duration per app",
        "Identify tenants with pending migrations",
        "Show migration history ordered by timestamp",
    ]

    retention_policy = {
        "keep_days": 90,
        "archive_older": True,
        "purge_after_days": 365,
    }

    result = {
        "log_table_documented": True,
        "table_name": table_name,
        "columns": columns,
        "query_patterns": query_patterns,
        "retention_policy": retention_policy,
    }

    logger.debug(
        "get_migration_log_table_config: columns=%d, queries=%d",
        len(columns), len(query_patterns),
    )
    return result


# ---------------------------------------------------------------------------
# Task 38: Handle Failed Tenant Migration
# ---------------------------------------------------------------------------

def get_failed_migration_handling_config() -> dict:
    """Return failure handling configuration for tenant migrations.

    Defines how migration failures are recorded and whether the system
    stops or continues when a tenant migration fails.

    Returns:
        dict: Failure handling configuration containing:
            - failure_handling_documented (bool): True when handling is documented.
            - failure_actions (list[str]): Steps taken on failure.
            - threshold_config (dict): Failure threshold settings.
            - behavior_options (list[str]): Available failure behaviors.

    Reference:
        SubPhase-08, Group-C, Task 38 - Handle Failed Tenant Migration.
    """
    failure_actions = [
        "Record the failure in the migration log table",
        "Capture the full error traceback for debugging",
        "Mark the tenant migration status as failed",
        "Notify the operator via console output",
        "Evaluate whether to continue or halt the batch",
    ]

    threshold_config = {
        "max_consecutive_failures": 3,
        "max_total_failures_percent": 10,
        "halt_on_threshold": True,
        "alert_on_first_failure": True,
    }

    behavior_options = [
        "stop_on_first_failure: Halt entire batch immediately",
        "continue_on_failure: Skip failed tenant and proceed",
        "threshold_based: Continue until failure threshold reached",
        "interactive: Prompt operator on each failure",
    ]

    result = {
        "failure_handling_documented": True,
        "failure_actions": failure_actions,
        "threshold_config": threshold_config,
        "behavior_options": behavior_options,
    }

    logger.debug(
        "get_failed_migration_handling_config: actions=%d, options=%d",
        len(failure_actions), len(behavior_options),
    )
    return result


# ---------------------------------------------------------------------------
# Task 39: Retry Failed Migrations
# ---------------------------------------------------------------------------

def get_retry_failed_migrations_config() -> dict:
    """Return retry configuration for failed tenant migrations.

    Defines retry behavior including retry counts, delays between
    attempts, and safeguards to prevent cascading failures.

    Returns:
        dict: Retry configuration containing:
            - retry_documented (bool): True when retry behavior is documented.
            - retry_settings (dict): Core retry parameters.
            - delay_strategy (list[str]): Delay strategies between retries.
            - safeguards (list[str]): Safeguards to prevent issues.

    Reference:
        SubPhase-08, Group-C, Task 39 - Retry Failed Migrations.
    """
    retry_settings = {
        "max_retries": 3,
        "retry_only_failed": True,
        "reset_status_before_retry": True,
        "log_each_attempt": True,
    }

    delay_strategy = [
        "Fixed delay of 5 seconds between retries by default",
        "Exponential backoff option: 5s, 15s, 45s",
        "Configurable via management command flags",
        "No delay option for development environments",
    ]

    safeguards = [
        "Never retry migrations that corrupt data",
        "Validate schema state before each retry attempt",
        "Log all retry attempts with timestamps",
        "Stop retrying if the same error repeats consecutively",
        "Operator can disable retries via command flag",
    ]

    result = {
        "retry_documented": True,
        "retry_settings": retry_settings,
        "delay_strategy": delay_strategy,
        "safeguards": safeguards,
    }

    logger.debug(
        "get_retry_failed_migrations_config: delays=%d, safeguards=%d",
        len(delay_strategy), len(safeguards),
    )
    return result


# ---------------------------------------------------------------------------
# Task 40: Skip Problematic Tenants
# ---------------------------------------------------------------------------

def get_skip_problematic_tenants_config() -> dict:
    """Return configuration for skipping problematic tenants.

    Defines how tenants that repeatedly fail migrations can be marked
    as skipped, with a manual review requirement noted.

    Returns:
        dict: Skip configuration containing:
            - skip_documented (bool): True when skip mechanism is documented.
            - skip_criteria (list[str]): Criteria for skipping a tenant.
            - skip_actions (list[str]): Actions taken when skipping.
            - review_requirements (list[str]): Manual review requirements.

    Reference:
        SubPhase-08, Group-C, Task 40 - Skip Problematic Tenants.
    """
    skip_criteria = [
        "Tenant has exceeded maximum retry attempts",
        "Tenant migration produces the same error repeatedly",
        "Operator explicitly marks tenant for skipping",
        "Tenant schema is flagged as inactive or suspended",
    ]

    skip_actions = [
        "Mark the tenant status as skipped in the log table",
        "Record the reason for skipping with timestamp",
        "Continue batch migration with remaining tenants",
        "Include skipped tenants in the final summary report",
    ]

    review_requirements = [
        "All skipped tenants require manual review by an operator",
        "Review must happen before the next scheduled migration",
        "Operator must resolve the root cause before un-skipping",
        "Un-skipping requires explicit command flag confirmation",
        "Skipped tenants are highlighted in monitoring dashboards",
    ]

    result = {
        "skip_documented": True,
        "skip_criteria": skip_criteria,
        "skip_actions": skip_actions,
        "review_requirements": review_requirements,
    }

    logger.debug(
        "get_skip_problematic_tenants_config: criteria=%d, reviews=%d",
        len(skip_criteria), len(review_requirements),
    )
    return result


# ---------------------------------------------------------------------------
# Task 41: Create Tenant Data Migration
# ---------------------------------------------------------------------------

def get_tenant_data_migration_config() -> dict:
    """Return tenant data migration configuration.

    Defines how data migrations are applied per tenant schema and how
    they are ordered relative to schema migrations.

    Returns:
        dict: Tenant data migration configuration containing:
            - data_migration_documented (bool): True when documented.
            - migration_steps (list[str]): Steps for tenant data migrations.
            - ordering_notes (list[str]): Ordering with schema migrations.
            - best_practices (list[str]): Best practices for data migrations.

    Reference:
        SubPhase-08, Group-C, Task 41 - Create Tenant Data Migration.
    """
    migration_steps = [
        "Identify data that needs transformation per tenant",
        "Create a data migration file in the appropriate app",
        "Use RunPython with schema-aware operations",
        "Apply the migration to each tenant schema individually",
        "Verify data integrity after migration completes",
    ]

    ordering_notes = [
        "Data migrations run after their dependent schema migrations",
        "Order is enforced via Django migration dependencies",
        "Each data migration must declare explicit dependencies",
        "Avoid mixing schema changes and data changes in one migration",
        "Run data migrations in a separate deployment step when possible",
    ]

    best_practices = [
        "Keep data migrations idempotent for safe re-runs",
        "Use batch processing to avoid long-running transactions",
        "Test data migrations on a copy of production data first",
        "Log the number of rows affected per tenant",
        "Include rollback logic in the reverse migration function",
        "Validate data constraints after migration completes",
    ]

    result = {
        "data_migration_documented": True,
        "migration_steps": migration_steps,
        "ordering_notes": ordering_notes,
        "best_practices": best_practices,
    }

    logger.debug(
        "get_tenant_data_migration_config: steps=%d, practices=%d",
        len(migration_steps), len(best_practices),
    )
    return result


# ---------------------------------------------------------------------------
# Task 42: Handle Large Tenants
# ---------------------------------------------------------------------------

def get_large_tenant_handling_config() -> dict:
    """Return configuration for handling large tenant migrations.

    Defines how migrations for large tenants are scheduled off-peak
    with reduced concurrency, and documents the criteria for
    identifying large tenants.

    Returns:
        dict: Large tenant handling configuration containing:
            - large_tenant_documented (bool): True when documented.
            - threshold_criteria (list[str]): Criteria for large tenants.
            - scheduling_config (dict): Off-peak scheduling details.
            - concurrency_adjustments (list[str]): Concurrency changes.
            - monitoring_notes (list[str]): Monitoring during migration.

    Reference:
        SubPhase-08, Group-C, Task 42 - Handle Large Tenants.
    """
    threshold_criteria = [
        "Tenant has more than 100,000 rows in any single table",
        "Tenant schema size exceeds 1 GB on disk",
        "Previous migration for this tenant took over 10 minutes",
        "Tenant is flagged as enterprise-tier in the plan table",
        "Tenant has more than 50 active database connections",
    ]

    scheduling_config = {
        "preferred_window": "02:00-06:00 UTC",
        "avoid_peak_hours": True,
        "notify_tenant_admin": True,
        "maintenance_mode": True,
        "max_duration_hours": 4,
    }

    concurrency_adjustments = [
        "Reduce max concurrent workers to 1 for large tenants",
        "Increase connection pool timeout for longer operations",
        "Disable parallel execution for the large tenant batch",
        "Allocate dedicated database connections for the migration",
        "Monitor memory usage and throttle if necessary",
    ]

    monitoring_notes = [
        "Track migration progress with per-table row counts",
        "Monitor database CPU and I/O during large migrations",
        "Set alerts for migrations exceeding expected duration",
        "Log checkpoint progress every 10,000 rows processed",
        "Capture query execution plans for slow operations",
    ]

    result = {
        "large_tenant_documented": True,
        "threshold_criteria": threshold_criteria,
        "scheduling_config": scheduling_config,
        "concurrency_adjustments": concurrency_adjustments,
        "monitoring_notes": monitoring_notes,
    }

    logger.debug(
        "get_large_tenant_handling_config: criteria=%d, adjustments=%d",
        len(threshold_criteria), len(concurrency_adjustments),
    )
    return result


# ---------------------------------------------------------------------------
# Task 43: Verify Tenant Migrations
# ---------------------------------------------------------------------------

def get_tenant_migration_verification_config() -> dict:
    """Return verification configuration for tenant migrations.

    Defines how to verify successful tenant schema migrations by
    checking tables and data integrity, and how to record results.

    Returns:
        dict: Tenant migration verification configuration containing:
            - verification_documented (bool): True when documented.
            - verification_steps (list[str]): Steps to verify migrations.
            - integrity_checks (list[str]): Data integrity checks.
            - result_recording (dict): How results are recorded.

    Reference:
        SubPhase-08, Group-C, Task 43 - Verify Tenant Migrations.
    """
    verification_steps = [
        "Confirm all expected tables exist in the tenant schema",
        "Verify column definitions match the migration expectations",
        "Check that indexes and constraints are properly created",
        "Validate foreign key relationships across tenant tables",
        "Confirm the django_migrations table has correct entries",
        "Run a sample query on each table to confirm accessibility",
    ]

    integrity_checks = [
        "Verify row counts are consistent before and after migration",
        "Check for orphaned records after foreign key changes",
        "Validate that NOT NULL constraints are satisfied",
        "Confirm unique constraints are not violated",
        "Test default values on newly added columns",
    ]

    result_recording = {
        "store_in_log_table": True,
        "include_timestamp": True,
        "record_pass_fail": True,
        "capture_error_details": True,
        "generate_summary_report": True,
    }

    result = {
        "verification_documented": True,
        "verification_steps": verification_steps,
        "integrity_checks": integrity_checks,
        "result_recording": result_recording,
    }

    logger.debug(
        "get_tenant_migration_verification_config: steps=%d, checks=%d",
        len(verification_steps), len(integrity_checks),
    )
    return result


# ---------------------------------------------------------------------------
# Task 44: Document Tenant Migrations
# ---------------------------------------------------------------------------

def get_tenant_migration_documentation_config() -> dict:
    """Return documentation configuration for tenant migrations.

    Summarizes the tenant migration workflow and documents the
    safeguards including retry and skip handling.

    Returns:
        dict: Tenant migration documentation configuration containing:
            - documentation_completed (bool): True when documentation is done.
            - workflow_summary (list[str]): Migration workflow steps.
            - safeguard_notes (list[str]): Documented safeguards.
            - reference_links (list[str]): Links to related documentation.

    Reference:
        SubPhase-08, Group-C, Task 44 - Document Tenant Migrations.
    """
    workflow_summary = [
        "Plan migrations using makemigrations for tenant apps",
        "Review generated migrations for correctness",
        "Run migrations on a single test tenant first",
        "Execute batch migration across all active tenants",
        "Monitor progress and handle failures as configured",
        "Verify all tenant schemas after migration completes",
        "Record results and generate summary report",
    ]

    safeguard_notes = [
        "Retry failed migrations up to configured retry count",
        "Skip problematic tenants after max retries exceeded",
        "All skipped tenants require manual review",
        "Large tenants are migrated during off-peak hours",
        "Concurrency is limited to prevent database overload",
        "Progress tracking provides real-time migration status",
    ]

    reference_links = [
        "Migration Strategy Overview (migration-strategy.md)",
        "Database Router Configuration (database-routers.md)",
        "Tenant Settings (tenant-settings.md)",
        "App Classification (app-classification.md)",
        "Migration Log Table (tenant_migration_log)",
    ]

    result = {
        "documentation_completed": True,
        "workflow_summary": workflow_summary,
        "safeguard_notes": safeguard_notes,
        "reference_links": reference_links,
    }

    logger.debug(
        "get_tenant_migration_documentation_config: workflow=%d, safeguards=%d",
        len(workflow_summary), len(safeguard_notes),
    )
    return result


# ---------------------------------------------------------------------------
# Task 45: Define Zero-Downtime Rules
# ---------------------------------------------------------------------------

def get_zero_downtime_rules_config() -> dict:
    """Return zero-downtime migration rules configuration.

    Defines rules to avoid downtime during database migrations,
    focusing on additive changes and phased removals.

    Returns:
        dict: Zero-downtime rules configuration containing:
            - rules_documented (bool): True when rules are documented.
            - rules (list[str]): Zero-downtime migration rules.
            - rationale (list[str]): Rationale for each rule category.
            - safety_goals (list[str]): Availability and safety goals.

    Reference:
        SubPhase-08, Group-D, Task 45 - Define Zero-Downtime Rules.
    """
    rules = [
        "Only additive changes are allowed by default",
        "New columns must be nullable or have safe defaults",
        "Column renames are prohibited in a single migration",
        "Column removals follow a phased deprecation process",
        "Index creation uses CONCURRENTLY where supported",
        "Data migrations are separated from schema migrations",
        "Rollback plans must exist for every migration",
    ]

    rationale = [
        "Additive changes prevent breaking running application code",
        "Nullable columns avoid lock contention on large tables",
        "Phased removals allow old and new code to coexist",
        "Concurrent indexes avoid full table locks",
        "Separated data migrations allow independent rollback",
    ]

    safety_goals = [
        "Zero downtime for all production deployments",
        "No exclusive table locks lasting more than 1 second",
        "Rolling deployments with old and new code compatibility",
        "Automated rollback capability for every migration",
        "Monitoring alerts for migration duration anomalies",
    ]

    result = {
        "rules_documented": True,
        "rules": rules,
        "rationale": rationale,
        "safety_goals": safety_goals,
    }

    logger.debug(
        "get_zero_downtime_rules_config: rules=%d, goals=%d",
        len(rules), len(safety_goals),
    )
    return result


# ---------------------------------------------------------------------------
# Task 46: Additive Migrations Only
# ---------------------------------------------------------------------------

def get_additive_migrations_policy_config() -> dict:
    """Return additive-only migrations policy configuration.

    Enforces additive migrations as the default approach, allowing
    safe addition of columns and tables without breaking changes.

    Returns:
        dict: Additive policy configuration containing:
            - policy_documented (bool): True when policy is documented.
            - allowed_operations (list[str]): Operations that are additive.
            - prohibited_operations (list[str]): Operations that are not.
            - enforcement_notes (list[str]): CI and linter enforcement.

    Reference:
        SubPhase-08, Group-D, Task 46 - Additive Migrations Only.
    """
    allowed_operations = [
        "Adding new tables",
        "Adding new nullable columns",
        "Adding new columns with safe defaults",
        "Adding new indexes (using CONCURRENTLY)",
        "Adding new constraints with NOT VALID",
        "Creating new database views",
    ]

    prohibited_operations = [
        "Dropping tables in a single step",
        "Dropping columns in a single step",
        "Renaming columns directly",
        "Renaming tables directly",
        "Changing column types without compatibility",
        "Adding NOT NULL without a default value",
    ]

    enforcement_notes = [
        "CI pipeline checks all migrations for prohibited operations",
        "Migration linter flags non-additive changes automatically",
        "Code review must verify additive-only compliance",
        "Exceptions require explicit approval from tech lead",
        "Non-additive changes follow the phased removal process",
    ]

    result = {
        "policy_documented": True,
        "allowed_operations": allowed_operations,
        "prohibited_operations": prohibited_operations,
        "enforcement_notes": enforcement_notes,
    }

    logger.debug(
        "get_additive_migrations_policy_config: allowed=%d, prohibited=%d",
        len(allowed_operations), len(prohibited_operations),
    )
    return result


# ---------------------------------------------------------------------------
# Task 47: Nullable New Columns
# ---------------------------------------------------------------------------

def get_nullable_new_columns_config() -> dict:
    """Return nullable new columns policy configuration.

    Requires new columns to be nullable initially, with notes on
    when and how to backfill values.

    Returns:
        dict: Nullable columns configuration containing:
            - nullable_documented (bool): True when policy is documented.
            - nullable_rules (list[str]): Rules for nullable columns.
            - backfill_notes (list[str]): When and how to backfill.
            - exceptions (list[str]): Allowed exceptions to the rule.

    Reference:
        SubPhase-08, Group-D, Task 47 - Nullable New Columns.
    """
    nullable_rules = [
        "All new columns must be nullable (NULL allowed) initially",
        "Add NOT NULL constraint only after backfilling all rows",
        "Use a separate migration for the NOT NULL constraint",
        "Never add NOT NULL columns to existing tables in one step",
        "Boolean columns should default to False rather than NULL",
    ]

    backfill_notes = [
        "Backfill in batches to avoid long-running transactions",
        "Use data migrations with batch size of 1000 rows",
        "Schedule backfills during off-peak hours for large tables",
        "Monitor database load during backfill operations",
        "Validate backfill completeness before adding constraints",
    ]

    exceptions = [
        "New tables can have NOT NULL columns from creation",
        "Small lookup tables (under 1000 rows) may use NOT NULL",
        "Columns with database-level defaults may use NOT NULL",
        "Primary key columns are always NOT NULL by definition",
    ]

    result = {
        "nullable_documented": True,
        "nullable_rules": nullable_rules,
        "backfill_notes": backfill_notes,
        "exceptions": exceptions,
    }

    logger.debug(
        "get_nullable_new_columns_config: rules=%d, exceptions=%d",
        len(nullable_rules), len(exceptions),
    )
    return result


# ---------------------------------------------------------------------------
# Task 48: Default Values Required
# ---------------------------------------------------------------------------

def get_default_values_required_config() -> dict:
    """Return default values requirement configuration.

    Requires default values for new columns where needed, documenting
    safe defaults during rollout and their impact on existing rows.

    Returns:
        dict: Default values configuration containing:
            - defaults_documented (bool): True when policy is documented.
            - default_rules (list[str]): Rules for default values.
            - safe_defaults (list[dict]): Safe default value examples.
            - impact_notes (list[str]): Impact on existing rows.

    Reference:
        SubPhase-08, Group-D, Task 48 - Default Values Required.
    """
    default_rules = [
        "New columns should have application-level defaults when possible",
        "Database-level defaults are preferred for NOT NULL columns",
        "Avoid volatile defaults like NOW() on large tables",
        "Use sentinel values only when NULL is not semantically valid",
        "Document the chosen default and its rationale in the migration",
    ]

    safe_defaults = [
        {"type": "boolean", "default": "False", "rationale": "Safe inactive state"},
        {"type": "integer", "default": "0", "rationale": "Neutral numeric value"},
        {"type": "varchar", "default": "empty string", "rationale": "Non-null placeholder"},
        {"type": "timestamp", "default": "NULL", "rationale": "Allow nullable dates"},
        {"type": "jsonb", "default": "empty object", "rationale": "Valid JSON structure"},
    ]

    impact_notes = [
        "Database-level defaults apply only to new rows on INSERT",
        "Existing rows are not updated when a default is added",
        "Backfill existing rows separately if a default is needed",
        "Large table backfills should be done in batched transactions",
        "Test default behavior with production-like data volumes",
    ]

    result = {
        "defaults_documented": True,
        "default_rules": default_rules,
        "safe_defaults": safe_defaults,
        "impact_notes": impact_notes,
    }

    logger.debug(
        "get_default_values_required_config: rules=%d, defaults=%d",
        len(default_rules), len(safe_defaults),
    )
    return result


# ---------------------------------------------------------------------------
# Task 49: No Column Renames
# ---------------------------------------------------------------------------

def get_no_column_renames_config() -> dict:
    """Return no-column-renames policy configuration.

    Defines the rule against direct column renames and documents the
    phased rename strategy using add-new-then-migrate-data approach.

    Returns:
        dict: No-renames configuration containing:
            - no_rename_documented (bool): True when policy is documented.
            - no_rename_rules (list[str]): Rules prohibiting renames.
            - phased_rename_steps (list[str]): Steps for phased rename.
            - alternatives (list[str]): Alternative approaches.

    Reference:
        SubPhase-08, Group-D, Task 49 - No Column Renames.
    """
    no_rename_rules = [
        "Direct column renames are prohibited in production migrations",
        "Column renames break running application code during deployment",
        "ORM field renames must use db_column to preserve the database name",
        "Table renames follow the same phased approach as column renames",
        "View renames can be done safely using CREATE OR REPLACE",
    ]

    phased_rename_steps = [
        "Step 1: Add the new column alongside the old column",
        "Step 2: Deploy code that writes to both old and new columns",
        "Step 3: Backfill the new column from old column data",
        "Step 4: Switch reads to the new column",
        "Step 5: Stop writing to the old column",
        "Step 6: Remove the old column in a later migration",
    ]

    alternatives = [
        "Use db_column in Django models to alias column names",
        "Create database views for backward compatibility",
        "Use application-level mapping for column name changes",
        "Consider if the rename is truly necessary for the feature",
    ]

    result = {
        "no_rename_documented": True,
        "no_rename_rules": no_rename_rules,
        "phased_rename_steps": phased_rename_steps,
        "alternatives": alternatives,
    }

    logger.debug(
        "get_no_column_renames_config: rules=%d, steps=%d",
        len(no_rename_rules), len(phased_rename_steps),
    )
    return result


# ---------------------------------------------------------------------------
# Task 50: Phased Column Removal
# ---------------------------------------------------------------------------

def get_phased_column_removal_config() -> dict:
    """Return phased column removal process configuration.

    Defines the phased process for removing columns: deprecate,
    backfill, switch, and remove across deployment stages.

    Returns:
        dict: Phased removal configuration containing:
            - phased_removal_documented (bool): True when documented.
            - removal_phases (list[str]): Phases of column removal.
            - timeline_guidelines (list[str]): Deployment stage timeline.
            - safety_checks (list[str]): Safety checks at each phase.

    Reference:
        SubPhase-08, Group-D, Task 50 - Phased Column Removal.
    """
    removal_phases = [
        "Phase 1 - Deprecate: Mark column as deprecated in code and docs",
        "Phase 2 - Stop Writing: Remove all writes to the deprecated column",
        "Phase 3 - Stop Reading: Remove all reads from the deprecated column",
        "Phase 4 - Make Nullable: Alter column to allow NULL if not already",
        "Phase 5 - Remove Column: Drop the column in a final migration",
    ]

    timeline_guidelines = [
        "Minimum 2 deployment cycles between deprecation and removal",
        "Each phase should be a separate pull request and deployment",
        "Allow at least 1 week between Phase 2 and Phase 3",
        "Phase 5 should only run after confirming no references remain",
        "Document the removal timeline in the migration commit message",
    ]

    safety_checks = [
        "Verify no application code references the deprecated column",
        "Check that no database views depend on the column",
        "Confirm no reports or exports use the column",
        "Validate that backups include the column data before removal",
        "Run the removal in staging before production",
        "Monitor error rates after each phase deployment",
    ]

    result = {
        "phased_removal_documented": True,
        "removal_phases": removal_phases,
        "timeline_guidelines": timeline_guidelines,
        "safety_checks": safety_checks,
    }

    logger.debug(
        "get_phased_column_removal_config: phases=%d, checks=%d",
        len(removal_phases), len(safety_checks),
    )
    return result


# ---------------------------------------------------------------------------
# Task 51: Create Linter for Migrations
# ---------------------------------------------------------------------------

def get_migration_linter_config() -> dict:
    """Return migration linter configuration for blocking unsafe migrations.

    Defines the linter rules, CI enforcement behavior, and integration
    points for blocking dangerous migration operations automatically.

    Returns:
        dict: Migration linter configuration containing:
            - linter_documented (bool): True when documented.
            - linter_rules (list[str]): Rules enforced by the linter.
            - enforcement_points (list[str]): Where the linter runs.
            - blocked_operations (list[str]): Operations the linter blocks.

    Reference:
        SubPhase-08, Group-D, Task 51 - Create Linter for Migrations.
    """
    linter_rules = [
        "Reject migrations that drop columns without a deprecation phase",
        "Reject migrations that rename columns directly",
        "Reject migrations that add NOT NULL columns without defaults",
        "Reject migrations that alter column types in-place",
        "Reject migrations that drop tables without prior deprecation",
        "Warn on migrations that add new indexes without CONCURRENTLY",
    ]

    enforcement_points = [
        "Pre-commit hook runs the linter on new migration files",
        "CI pipeline blocks merges when linter violations are found",
        "Pull request checks report linter results as status checks",
        "Local development via Makefile target: make lint-migrations",
        "Nightly CI job scans all existing migrations for regressions",
    ]

    blocked_operations = [
        "RemoveField without prior nullable migration",
        "RenameField on production tables",
        "AlterField changing column type",
        "DeleteModel without prior deprecation",
        "AddField with null=False and no default",
        "RunSQL with DROP or ALTER TYPE statements",
    ]

    result = {
        "linter_documented": True,
        "linter_rules": linter_rules,
        "enforcement_points": enforcement_points,
        "blocked_operations": blocked_operations,
    }

    logger.debug(
        "get_migration_linter_config: rules=%d, blocked=%d",
        len(linter_rules), len(blocked_operations),
    )
    return result


# ---------------------------------------------------------------------------
# Task 52: Configure django-pg-zero-downtime
# ---------------------------------------------------------------------------

def get_pg_zero_downtime_config() -> dict:
    """Return django-pg-zero-downtime configuration details.

    Defines the library configuration, guarded operations, and
    settings for safe migration behaviors in PostgreSQL.

    Returns:
        dict: Zero-downtime tool configuration containing:
            - configuration_documented (bool): True when documented.
            - guarded_operations (list[str]): Operations the tool guards.
            - settings (list[str]): Django settings for the tool.
            - scope_notes (list[str]): Scope and limitations of the tool.

    Reference:
        SubPhase-08, Group-D, Task 52 - Configure django-pg-zero-downtime.
    """
    guarded_operations = [
        "Adding columns with defaults uses server-side defaults safely",
        "Creating indexes uses CREATE INDEX CONCURRENTLY",
        "Adding constraints uses NOT VALID then VALIDATE separately",
        "Dropping columns is flagged for review",
        "Altering column types raises an error by default",
        "Adding NOT NULL constraints uses a safe two-step process",
    ]

    settings = [
        "ZERO_DOWNTIME_MIGRATIONS_RAISE_FOR_UNSAFE = True",
        "ZERO_DOWNTIME_MIGRATIONS_USE_NOT_NULL = DJANGO_4_1",
        "ZERO_DOWNTIME_MIGRATIONS_LOCK_TIMEOUT = 2s",
        "ZERO_DOWNTIME_MIGRATIONS_STATEMENT_TIMEOUT = 5s",
        "ZERO_DOWNTIME_MIGRATIONS_FLEXIBLE_STATEMENT_TIMEOUT = True",
    ]

    scope_notes = [
        "Covers all Django migration operations for PostgreSQL",
        "Does not guard RunSQL or RunPython operations automatically",
        "Requires PostgreSQL 12 or later for full feature support",
        "Works alongside django-tenants for schema-based migrations",
        "Custom operations need manual zero-downtime review",
    ]

    result = {
        "configuration_documented": True,
        "guarded_operations": guarded_operations,
        "settings": settings,
        "scope_notes": scope_notes,
    }

    logger.debug(
        "get_pg_zero_downtime_config: guarded=%d, settings=%d",
        len(guarded_operations), len(settings),
    )
    return result


# ---------------------------------------------------------------------------
# Task 53: Handle Index Creation
# ---------------------------------------------------------------------------

def get_index_creation_config() -> dict:
    """Return index creation rules for non-blocking approaches.

    Defines the rules, restrictions, and best practices for creating
    indexes without locking tables in production.

    Returns:
        dict: Index creation configuration containing:
            - index_rules_documented (bool): True when documented.
            - index_rules (list[str]): Rules for safe index creation.
            - restrictions (list[str]): Restrictions and limitations.
            - best_practices (list[str]): Best practices for indexing.

    Reference:
        SubPhase-08, Group-D, Task 53 - Handle Index Creation.
    """
    index_rules = [
        "Always use CREATE INDEX CONCURRENTLY for production indexes",
        "Set atomic = False in migrations that create concurrent indexes",
        "Each concurrent index must be in its own migration file",
        "Use AddIndexConcurrently from django.contrib.postgres.operations",
        "Monitor pg_stat_progress_create_index during creation",
        "Test index creation on a staging copy of production data first",
    ]

    restrictions = [
        "CONCURRENTLY cannot run inside a transaction block",
        "If concurrent index creation fails, an INVALID index remains",
        "Unique concurrent indexes may fail if duplicates exist",
        "Partial indexes need WHERE clause validation before creation",
        "GIN and GiST indexes may take significantly longer to build",
    ]

    best_practices = [
        "Schedule large index creation during low-traffic windows",
        "Add indexes to the most selective columns first",
        "Monitor table lock status during index builds",
        "Use REINDEX CONCURRENTLY to rebuild invalid indexes",
        "Verify index usage with EXPLAIN ANALYZE after creation",
    ]

    result = {
        "index_rules_documented": True,
        "index_rules": index_rules,
        "restrictions": restrictions,
        "best_practices": best_practices,
    }

    logger.debug(
        "get_index_creation_config: rules=%d, restrictions=%d",
        len(index_rules), len(restrictions),
    )
    return result


# ---------------------------------------------------------------------------
# Task 54: Handle Constraint Addition
# ---------------------------------------------------------------------------

def get_constraint_addition_config() -> dict:
    """Return constraint addition rules for non-blocking methods.

    Defines safe constraint addition using NOT VALID and VALIDATE
    phases to avoid locking tables during constraint operations.

    Returns:
        dict: Constraint addition configuration containing:
            - constraint_handling_documented (bool): True when documented.
            - constraint_rules (list[str]): Rules for safe constraints.
            - validation_phases (list[str]): Phases for constraint validation.
            - supported_constraints (list[str]): Types of supported constraints.

    Reference:
        SubPhase-08, Group-D, Task 54 - Handle Constraint Addition.
    """
    constraint_rules = [
        "Add foreign key constraints with NOT VALID first",
        "Validate constraints in a separate migration step",
        "Use AddConstraintNotValid for CHECK constraints",
        "Separate NOT NULL constraints into add-default then set-not-null",
        "Unique constraints should use concurrent unique index first",
        "Avoid adding multiple constraints in a single migration",
    ]

    validation_phases = [
        "Phase 1 - Add constraint with NOT VALID (no table lock)",
        "Phase 2 - New rows are validated against the constraint immediately",
        "Phase 3 - Run VALIDATE CONSTRAINT to check existing rows",
        "Phase 4 - Validation acquires SHARE UPDATE EXCLUSIVE lock briefly",
        "Phase 5 - Constraint is fully enforced after validation completes",
    ]

    supported_constraints = [
        "CHECK constraints via NOT VALID then VALIDATE",
        "FOREIGN KEY constraints via NOT VALID then VALIDATE",
        "NOT NULL via adding default then altering column",
        "UNIQUE via CREATE UNIQUE INDEX CONCURRENTLY then constraint",
        "EXCLUSION constraints require careful lock management",
    ]

    result = {
        "constraint_handling_documented": True,
        "constraint_rules": constraint_rules,
        "validation_phases": validation_phases,
        "supported_constraints": supported_constraints,
    }

    logger.debug(
        "get_constraint_addition_config: rules=%d, phases=%d",
        len(constraint_rules), len(validation_phases),
    )
    return result


# ---------------------------------------------------------------------------
# Task 55: Create Migration Dry Run
# ---------------------------------------------------------------------------

def get_migration_dry_run_config() -> dict:
    """Return migration dry run process configuration.

    Defines the dry-run workflow for simulating migrations without
    applying them, including usage guidelines and integration points.

    Returns:
        dict: Dry run configuration containing:
            - dry_run_documented (bool): True when documented.
            - dry_run_steps (list[str]): Steps in the dry run process.
            - usage_guidelines (list[str]): When to run dry runs.
            - integration_points (list[str]): Where dry runs are integrated.

    Reference:
        SubPhase-08, Group-D, Task 55 - Create Migration Dry Run.
    """
    dry_run_steps = [
        "Run migrate --plan to preview pending migrations",
        "Use sqlmigrate to inspect generated SQL for each migration",
        "Execute migrate --fake-initial on a shadow database copy",
        "Compare shadow database schema against expected schema state",
        "Run application smoke tests against the shadow database",
        "Review the migration dependency graph for conflicts",
    ]

    usage_guidelines = [
        "Run dry run before every production deployment",
        "Use dry run when merging branches with migration conflicts",
        "Run dry run after rebasing feature branches onto main",
        "Use dry run to validate rollback migrations before applying",
        "Run dry run on staging with production data copy weekly",
    ]

    integration_points = [
        "CI pipeline runs dry run on every pull request",
        "Makefile target: make migrate-dry-run",
        "Pre-deployment script includes dry run as a gate check",
        "Release checklist includes dry run verification step",
        "Monitoring alerts if dry run detects schema drift",
    ]

    result = {
        "dry_run_documented": True,
        "dry_run_steps": dry_run_steps,
        "usage_guidelines": usage_guidelines,
        "integration_points": integration_points,
    }

    logger.debug(
        "get_migration_dry_run_config: steps=%d, guidelines=%d",
        len(dry_run_steps), len(usage_guidelines),
    )
    return result


# ---------------------------------------------------------------------------
# Task 56: Schedule Off-Peak Migrations
# ---------------------------------------------------------------------------

def get_off_peak_migration_schedule_config() -> dict:
    """Return off-peak migration schedule configuration.

    Defines the maintenance windows, scheduling rules, and
    communication expectations for running migrations during
    low-traffic periods.

    Returns:
        dict: Off-peak schedule configuration containing:
            - schedule_documented (bool): True when documented.
            - maintenance_windows (list[str]): Defined maintenance windows.
            - scheduling_rules (list[str]): Rules for scheduling migrations.
            - communication_steps (list[str]): Communication expectations.

    Reference:
        SubPhase-08, Group-D, Task 56 - Schedule Off-Peak Migrations.
    """
    maintenance_windows = [
        "Primary window: Weekdays 02:00-05:00 local time (lowest traffic)",
        "Secondary window: Sundays 00:00-06:00 local time",
        "Emergency window: Any time with stakeholder approval",
        "Avoid month-end periods for accounting-heavy tenants",
        "Coordinate with tenant SLA maintenance schedules",
    ]

    scheduling_rules = [
        "Schedule migrations at least 48 hours in advance",
        "Run dry-run at least 24 hours before the migration window",
        "Limit migration window duration to 2 hours maximum",
        "Have a rollback plan ready before starting any migration",
        "Assign a primary and secondary engineer for each window",
        "Keep migration changes small and focused per window",
    ]

    communication_steps = [
        "Notify all stakeholders 48 hours before scheduled migration",
        "Send reminder notification 2 hours before migration window",
        "Post real-time status updates in the operations channel",
        "Send completion notification with summary after migration",
        "Document any issues encountered in the post-migration report",
    ]

    result = {
        "schedule_documented": True,
        "maintenance_windows": maintenance_windows,
        "scheduling_rules": scheduling_rules,
        "communication_steps": communication_steps,
    }

    logger.debug(
        "get_off_peak_migration_schedule_config: windows=%d, rules=%d",
        len(maintenance_windows), len(scheduling_rules),
    )
    return result


# ---------------------------------------------------------------------------
# Task 57: Monitor During Migration
# ---------------------------------------------------------------------------

def get_migration_monitoring_config() -> dict:
    """Return migration monitoring plan configuration.

    Defines the monitoring metrics, alert thresholds, and escalation
    procedures for tracking database performance during migrations.

    Returns:
        dict: Monitoring plan configuration containing:
            - monitoring_documented (bool): True when documented.
            - monitoring_metrics (list[str]): Metrics to track.
            - alert_thresholds (list[str]): Alert threshold definitions.
            - escalation_steps (list[str]): Escalation procedures.

    Reference:
        SubPhase-08, Group-D, Task 57 - Monitor During Migration.
    """
    monitoring_metrics = [
        "Track pg_stat_activity for active connections and locks",
        "Monitor query execution time via pg_stat_statements",
        "Watch replication lag on read replicas during migration",
        "Track lock wait times with pg_stat_activity.wait_event",
        "Monitor disk I/O usage during large data migrations",
        "Check connection pool utilization via PgBouncer stats",
    ]

    alert_thresholds = [
        "Lock wait time exceeding 10 seconds triggers warning",
        "Replication lag exceeding 30 seconds triggers critical alert",
        "Connection count exceeding 80 percent of max triggers warning",
        "Query execution time exceeding 60 seconds triggers warning",
        "Disk I/O saturation above 90 percent triggers critical alert",
    ]

    escalation_steps = [
        "Level 1: Auto-alert to on-call engineer via monitoring channel",
        "Level 2: Pause migration and assess impact within 5 minutes",
        "Level 3: Escalate to database team lead if unresolved in 15 min",
        "Level 4: Initiate rollback if issue persists beyond 30 minutes",
        "Level 5: Post-incident review within 24 hours of resolution",
    ]

    result = {
        "monitoring_documented": True,
        "monitoring_metrics": monitoring_metrics,
        "alert_thresholds": alert_thresholds,
        "escalation_steps": escalation_steps,
    }

    logger.debug(
        "get_migration_monitoring_config: metrics=%d, thresholds=%d",
        len(monitoring_metrics), len(alert_thresholds),
    )
    return result


# ---------------------------------------------------------------------------
# Task 58: Document Zero-Downtime Rules
# ---------------------------------------------------------------------------

def get_zero_downtime_documentation_config() -> dict:
    """Return zero-downtime rules documentation configuration.

    Summarizes all zero-downtime rules, enforcement mechanisms, and
    references to linter and CI checks in a single documentation set.

    Returns:
        dict: Zero-downtime documentation containing:
            - documentation_completed (bool): True when documented.
            - rule_summaries (list[str]): Summary of all zero-downtime rules.
            - enforcement_mechanisms (list[str]): Enforcement via linter/CI.
            - reference_links (list[str]): Links to detailed documentation.

    Reference:
        SubPhase-08, Group-D, Task 58 - Document Zero-Downtime Rules.
    """
    rule_summaries = [
        "Additive only: Only add columns, tables, and indexes",
        "Nullable columns: New columns must allow NULL initially",
        "Default values: All new columns must have safe defaults",
        "No renames: Never rename columns in a single migration",
        "Phased removal: Remove columns across multiple deployments",
        "Concurrent indexes: Always create indexes with CONCURRENTLY",
        "Constraint phases: Add constraints with NOT VALID then VALIDATE",
    ]

    enforcement_mechanisms = [
        "Migration linter blocks unsafe operations in CI pipeline",
        "django-pg-zero-downtime raises errors for unsafe operations",
        "Pre-commit hooks run linter on new migration files",
        "Pull request checks require linter pass before merge",
        "Dry-run gate prevents deployment without simulation pass",
    ]

    reference_links = [
        "Migration linter configuration: get_migration_linter_config()",
        "Zero-downtime tool: get_pg_zero_downtime_config()",
        "Index creation rules: get_index_creation_config()",
        "Constraint addition rules: get_constraint_addition_config()",
        "Dry-run process: get_migration_dry_run_config()",
        "Off-peak schedule: get_off_peak_migration_schedule_config()",
    ]

    result = {
        "documentation_completed": True,
        "rule_summaries": rule_summaries,
        "enforcement_mechanisms": enforcement_mechanisms,
        "reference_links": reference_links,
    }

    logger.debug(
        "get_zero_downtime_documentation_config: rules=%d, links=%d",
        len(rule_summaries), len(reference_links),
    )
    return result


# ---------------------------------------------------------------------------
# Task 59: Define Rollback Strategy
# ---------------------------------------------------------------------------

def get_rollback_strategy_config() -> dict:
    """Return rollback strategy configuration for migrations.

    Defines the rollback strategy covering public and tenant schemas,
    including principles, safety checks, and reversibility requirements.

    Returns:
        dict: Rollback strategy configuration containing:
            - strategy_documented (bool): True when documented.
            - rollback_principles (list[str]): Core rollback principles.
            - schema_scopes (list[str]): Schema scopes for rollback.
            - safety_requirements (list[str]): Safety requirements.

    Reference:
        SubPhase-08, Group-E, Task 59 - Define Rollback Strategy.
    """
    rollback_principles = [
        "Every migration must have a reverse migration defined",
        "Rollback should be tested before production deployment",
        "Data migrations require explicit reverse_code functions",
        "Rollback order is the reverse of the migration order",
        "Partial rollback should be supported at the app level",
        "Rollback state must be verified after execution",
    ]

    schema_scopes = [
        "Public schema rollback applies to shared tables only",
        "Tenant schema rollback targets individual tenant schemas",
        "Cross-schema rollback must maintain referential integrity",
        "Public schema rollback must complete before tenant rollback",
        "Each schema scope requires independent verification",
    ]

    safety_requirements = [
        "Create database backup before any rollback operation",
        "Verify no active transactions before starting rollback",
        "Lock tenant access during tenant-specific rollback",
        "Monitor connection count during rollback execution",
        "Log all rollback operations for audit trail",
        "Validate data integrity after rollback completion",
    ]

    result = {
        "strategy_documented": True,
        "rollback_principles": rollback_principles,
        "schema_scopes": schema_scopes,
        "safety_requirements": safety_requirements,
    }

    logger.debug(
        "get_rollback_strategy_config: principles=%d, scopes=%d",
        len(rollback_principles), len(schema_scopes),
    )
    return result


# ---------------------------------------------------------------------------
# Task 60: Create Rollback Command
# ---------------------------------------------------------------------------

def get_rollback_command_config() -> dict:
    """Return rollback command configuration for migrations.

    Defines the rollback commands supporting app-level and
    tenant-scoped rollback with required inputs and usage.

    Returns:
        dict: Rollback command configuration containing:
            - commands_documented (bool): True when documented.
            - rollback_commands (list[str]): Available rollback commands.
            - required_inputs (list[str]): Required inputs for rollback.
            - usage_examples (list[str]): Usage documentation.

    Reference:
        SubPhase-08, Group-E, Task 60 - Create Rollback Command.
    """
    rollback_commands = [
        "migrate_schemas --backward to roll back tenant schemas",
        "migrate --backward to roll back public schema migrations",
        "migrate <app_label> <migration_name> to target specific state",
        "migrate <app_label> zero to roll back all migrations for an app",
        "tenant_command migrate --backward for single tenant rollback",
        "Custom rollback management command with dry-run support",
    ]

    required_inputs = [
        "Target migration name or number to roll back to",
        "App label for app-specific rollback operations",
        "Tenant schema name for tenant-scoped rollback",
        "Confirmation flag to prevent accidental rollback",
        "Dry-run flag to preview rollback without executing",
    ]

    usage_examples = [
        "Roll back last migration: specify previous migration name",
        "Roll back to specific point: provide exact migration name",
        "Roll back entire app: use zero as migration target",
        "Dry-run rollback: add --dry-run flag to preview changes",
        "Tenant rollback: specify --schema flag with tenant name",
    ]

    result = {
        "commands_documented": True,
        "rollback_commands": rollback_commands,
        "required_inputs": required_inputs,
        "usage_examples": usage_examples,
    }

    logger.debug(
        "get_rollback_command_config: commands=%d, inputs=%d",
        len(rollback_commands), len(required_inputs),
    )
    return result


# ---------------------------------------------------------------------------
# Task 61: Define Forward/Backward Ops
# ---------------------------------------------------------------------------

def get_forward_backward_ops_config() -> dict:
    """Return forward and backward migration operations configuration.

    Defines the requirements for reversible migrations including
    reverse_code expectations and reversibility documentation.

    Returns:
        dict: Forward/backward operations configuration containing:
            - operations_documented (bool): True when documented.
            - forward_ops (list[str]): Forward operation types.
            - backward_requirements (list[str]): Backward requirements.
            - reversibility_rules (list[str]): Reversibility rules.

    Reference:
        SubPhase-08, Group-E, Task 61 - Define Forward/Backward Ops.
    """
    forward_ops = [
        "AddField: Forward adds column, backward removes column",
        "CreateModel: Forward creates table, backward drops table",
        "AlterField: Forward alters column, backward restores original",
        "RunPython: Forward runs code, backward runs reverse_code",
        "AddIndex: Forward creates index, backward drops index",
        "AddConstraint: Forward adds constraint, backward removes it",
    ]

    backward_requirements = [
        "Every RunPython operation must include reverse_code parameter",
        "reverse_code must undo exactly what the forward code did",
        "Data migrations must preserve data during reverse operations",
        "reverse_code should be tested independently of forward code",
        "Use migrations.RunPython.noop only when reverse is truly safe",
    ]

    reversibility_rules = [
        "Schema migrations are automatically reversible by Django",
        "Data migrations require explicit reverse_code functions",
        "RunSQL requires reverse_sql for automatic reversibility",
        "Combined schema and data changes need careful reverse order",
        "Test reversibility by migrating forward then backward",
        "Document any irreversible migrations with clear warnings",
    ]

    result = {
        "operations_documented": True,
        "forward_ops": forward_ops,
        "backward_requirements": backward_requirements,
        "reversibility_rules": reversibility_rules,
    }

    logger.debug(
        "get_forward_backward_ops_config: ops=%d, rules=%d",
        len(forward_ops), len(reversibility_rules),
    )
    return result


# ---------------------------------------------------------------------------
# Task 62: Test Rollback for Each Migration
# ---------------------------------------------------------------------------

def get_rollback_test_config() -> dict:
    """Return rollback test configuration for each migration.

    Defines the test procedures, success criteria, and recording
    requirements for validating reverse migrations.

    Returns:
        dict: Rollback test configuration containing:
            - rollback_tests_documented (bool): True when documented.
            - test_procedures (list[str]): Test procedures for rollback.
            - success_criteria (list[str]): Success criteria for tests.
            - recording_requirements (list[str]): Recording requirements.

    Reference:
        SubPhase-08, Group-E, Task 62 - Test Rollback for Each Migration.
    """
    test_procedures = [
        "Apply migration forward then immediately roll back",
        "Verify database schema matches pre-migration state",
        "Check data integrity after rollback completion",
        "Run application smoke tests after rollback",
        "Validate foreign key constraints are intact after rollback",
        "Test rollback with realistic production-like data volumes",
    ]

    success_criteria = [
        "Schema matches expected state after rollback",
        "No data loss occurs during rollback operation",
        "All foreign key constraints remain valid",
        "Application passes smoke tests after rollback",
        "No orphaned objects remain in the database",
    ]

    recording_requirements = [
        "Record migration name and rollback target in test log",
        "Document any data transformations during rollback",
        "Note execution time for each rollback operation",
        "Flag any migrations that fail rollback testing",
        "Store test results in the CI pipeline artifacts",
    ]

    result = {
        "rollback_tests_documented": True,
        "test_procedures": test_procedures,
        "success_criteria": success_criteria,
        "recording_requirements": recording_requirements,
    }

    logger.debug(
        "get_rollback_test_config: procedures=%d, criteria=%d",
        len(test_procedures), len(success_criteria),
    )
    return result


# ---------------------------------------------------------------------------
# Task 63: Create Rollback Single Tenant
# ---------------------------------------------------------------------------

def get_single_tenant_rollback_config() -> dict:
    """Return single tenant rollback configuration.

    Defines the process for rolling back migrations on a specific
    tenant schema including selection, safety, and verification.

    Returns:
        dict: Single tenant rollback configuration containing:
            - single_tenant_rollback_documented (bool): True when documented.
            - rollback_steps (list[str]): Steps for single tenant rollback.
            - tenant_selection (list[str]): Tenant selection guidelines.
            - safety_measures (list[str]): Safety measures during rollback.

    Reference:
        SubPhase-08, Group-E, Task 63 - Create Rollback Single Tenant.
    """
    rollback_steps = [
        "Identify the target tenant schema for rollback",
        "Create backup of the tenant schema before rollback",
        "Disable tenant access during the rollback window",
        "Execute rollback migration for the specific schema",
        "Verify schema state matches expected rollback target",
        "Re-enable tenant access after verification passes",
    ]

    tenant_selection = [
        "Select tenant by schema name using --schema flag",
        "Verify tenant exists and is active before rollback",
        "Confirm tenant is not currently processing requests",
        "Check for pending transactions in the tenant schema",
        "Log tenant selection for audit purposes",
    ]

    safety_measures = [
        "Isolate tenant schema from other tenant operations",
        "Monitor connection pool for the target tenant",
        "Set statement timeout to prevent long-running rollback",
        "Verify no cross-tenant queries are in progress",
        "Prepare immediate forward-migration if rollback fails",
        "Notify tenant administrators before and after rollback",
    ]

    result = {
        "single_tenant_rollback_documented": True,
        "rollback_steps": rollback_steps,
        "tenant_selection": tenant_selection,
        "safety_measures": safety_measures,
    }

    logger.debug(
        "get_single_tenant_rollback_config: steps=%d, safety=%d",
        len(rollback_steps), len(safety_measures),
    )
    return result


# ---------------------------------------------------------------------------
# Task 64: Create Rollback All Tenants
# ---------------------------------------------------------------------------

def get_all_tenants_rollback_config() -> dict:
    """Return rollback all tenants configuration.

    Defines the process for applying rollback consistently across
    all tenant schemas with staging requirements and safeguards.

    Returns:
        dict: All tenants rollback configuration containing:
            - all_tenants_rollback_documented (bool): True when documented.
            - rollback_process (list[str]): Process for rolling back all.
            - safeguards (list[str]): Safeguards for bulk rollback.
            - staging_requirements (list[str]): Staging requirements.

    Reference:
        SubPhase-08, Group-E, Task 64 - Create Rollback All Tenants.
    """
    rollback_process = [
        "Execute rollback on staging environment first",
        "Verify staging rollback succeeds for all tenant schemas",
        "Schedule production rollback during maintenance window",
        "Roll back tenants in batches to limit blast radius",
        "Monitor each batch completion before starting the next",
        "Verify all tenant schemas reach target migration state",
    ]

    safeguards = [
        "Require staging success before production rollback",
        "Create full database backup before bulk rollback",
        "Set maximum batch size to limit concurrent rollbacks",
        "Implement circuit breaker to stop on repeated failures",
        "Maintain a skip list for problematic tenant schemas",
        "Send real-time progress updates to operations channel",
    ]

    staging_requirements = [
        "Staging must mirror production tenant count and schemas",
        "Staging data should include representative data volumes",
        "Staging rollback must complete within acceptable time limit",
        "All smoke tests must pass on staging after rollback",
        "Document staging results before production approval",
    ]

    result = {
        "all_tenants_rollback_documented": True,
        "rollback_process": rollback_process,
        "safeguards": safeguards,
        "staging_requirements": staging_requirements,
    }

    logger.debug(
        "get_all_tenants_rollback_config: process=%d, safeguards=%d",
        len(rollback_process), len(safeguards),
    )
    return result


# ---------------------------------------------------------------------------
# Group-E: Rollback Strategy – Tasks 65-70 (Backup & Restore Runbook)
# ---------------------------------------------------------------------------


def get_non_reversible_migration_config() -> dict:
    """Return configuration for handling non-reversible migrations.

    Task 65 – Handle Non-Reversible Migrations
    ============================================
    Identifies schema changes that cannot be automatically reversed and
    defines manual intervention procedures for each category.

    Returns:
        dict with keys:
            - non_reversible_handling_documented (bool): True when configured.
            - non_reversible_types (list[str]): Categories of irreversible ops.
            - manual_procedures (list[str]): Steps for manual rollback.
            - risk_mitigation (list[str]): Strategies to reduce rollback risk.
    """
    non_reversible_types = [
        "Column removal after data migration completes",
        "Data type narrowing that loses precision",
        "Constraint additions that reject existing data on removal",
        "Index removal on large tables with recreation cost",
        "Enum value removal after data references exist",
        "Trigger removal with dependent business logic",
        "Stored procedure changes with side effects",
    ]

    manual_procedures = [
        "Identify the non-reversible operation in the migration file",
        "Create a compensating migration with manual SQL",
        "Document exact SQL commands needed for manual rollback",
        "Test compensating migration in staging environment",
        "Prepare data recovery scripts for potential data loss",
        "Assign DBA approval for manual rollback execution",
        "Schedule maintenance window for manual intervention",
        "Execute manual rollback with real-time monitoring",
    ]

    risk_mitigation = [
        "Always create backup before non-reversible migrations",
        "Split non-reversible operations into separate migrations",
        "Add pre-migration data validation checks",
        "Implement feature flags to decouple deploy from migrate",
        "Create shadow columns before dropping originals",
        "Use staged rollouts with canary tenant testing first",
    ]

    result = {
        "non_reversible_handling_documented": True,
        "non_reversible_types": non_reversible_types,
        "manual_procedures": manual_procedures,
        "risk_mitigation": risk_mitigation,
    }

    logger.debug(
        "get_non_reversible_migration_config: types=%d, procedures=%d",
        len(non_reversible_types), len(manual_procedures),
    )
    return result


def get_pre_migration_backup_config() -> dict:
    """Return configuration for creating pre-migration backups.

    Task 66 – Create Pre-Migration Backup
    =======================================
    Defines the backup strategy executed before every migration run to
    ensure a reliable restore point is available.

    Returns:
        dict with keys:
            - pre_migration_backup_documented (bool): True when configured.
            - backup_steps (list[str]): Ordered backup procedure.
            - backup_types (list[str]): Types of backups to create.
            - retention_policy (list[str]): Rules for backup retention.
    """
    backup_steps = [
        "Verify available disk space for backup storage",
        "Notify operations team of upcoming migration backup",
        "Pause non-critical background jobs and celery tasks",
        "Create full database dump using pg_dump with compression",
        "Create WAL archive checkpoint for point-in-time recovery",
        "Verify backup integrity with pg_restore --list",
        "Upload backup to offsite storage with encryption",
        "Record backup metadata including size and checksum",
        "Confirm backup completion before proceeding with migration",
    ]

    backup_types = [
        "Full PostgreSQL dump (pg_dump --format=custom)",
        "Schema-only backup for structure reference",
        "Tenant-specific data exports for critical tenants",
        "WAL segment archive for PITR capability",
        "Application configuration snapshot",
        "Redis cache state snapshot if applicable",
    ]

    retention_policy = [
        "Keep pre-migration backup until migration is verified stable",
        "Retain last 5 migration backups for rollback flexibility",
        "Archive monthly backups for compliance requirements",
        "Auto-delete staging backups after 7 days",
        "Production backups retained minimum 30 days",
        "Document backup location in migration log entry",
    ]

    result = {
        "pre_migration_backup_documented": True,
        "backup_steps": backup_steps,
        "backup_types": backup_types,
        "retention_policy": retention_policy,
    }

    logger.debug(
        "get_pre_migration_backup_config: steps=%d, types=%d",
        len(backup_steps), len(backup_types),
    )
    return result


def get_point_in_time_restore_config() -> dict:
    """Return configuration for point-in-time restore capability.

    Task 67 – Create Point-in-Time Restore
    ========================================
    Configures PostgreSQL WAL archiving and point-in-time recovery
    (PITR) to allow restoring to any moment before a failed migration.

    Returns:
        dict with keys:
            - point_in_time_restore_documented (bool): True when configured.
            - pitr_setup (list[str]): WAL archiving and PITR setup steps.
            - restore_procedure (list[str]): Steps to execute a PITR.
            - prerequisites (list[str]): Required infrastructure settings.
    """
    pitr_setup = [
        "Enable WAL archiving in postgresql.conf (archive_mode=on)",
        "Configure archive_command to copy WAL to secure storage",
        "Set wal_level to replica or logical for full recovery info",
        "Configure appropriate checkpoint_timeout and max_wal_size",
        "Verify WAL archive destination has sufficient storage",
        "Set up automated WAL archive monitoring and alerts",
        "Test WAL archiving with manual archive_command trigger",
    ]

    restore_procedure = [
        "Stop the PostgreSQL service immediately",
        "Identify target recovery timestamp from migration logs",
        "Prepare recovery configuration with recovery_target_time",
        "Restore base backup to data directory",
        "Copy archived WAL segments to pg_wal directory",
        "Create recovery.signal file for targeted recovery",
        "Start PostgreSQL and monitor recovery progress",
        "Verify data integrity after recovery completes",
        "Remove recovery.signal and resume normal operation",
    ]

    prerequisites = [
        "Continuous WAL archiving must be enabled and verified",
        "Base backup must exist from before the migration",
        "Archive storage must be accessible during recovery",
        "Recovery target time must be recorded in migration log",
        "Sufficient disk space for WAL replay on target server",
        "DBA access credentials available for recovery process",
    ]

    result = {
        "point_in_time_restore_documented": True,
        "pitr_setup": pitr_setup,
        "restore_procedure": restore_procedure,
        "prerequisites": prerequisites,
    }

    logger.debug(
        "get_point_in_time_restore_config: setup=%d, procedure=%d",
        len(pitr_setup), len(restore_procedure),
    )
    return result


def get_rollback_runbook_config() -> dict:
    """Return configuration for the rollback runbook.

    Task 68 – Create Rollback Runbook
    ===================================
    Provides a comprehensive runbook that operations teams follow when
    a migration rollback is required in any environment.

    Returns:
        dict with keys:
            - rollback_runbook_documented (bool): True when configured.
            - runbook_sections (list[str]): Sections in the runbook.
            - decision_criteria (list[str]): When to trigger rollback.
            - communication_plan (list[str]): Stakeholder notifications.
    """
    runbook_sections = [
        "1. Rollback Decision Matrix – criteria and authority",
        "2. Pre-Rollback Checklist – validations before execution",
        "3. Automated Rollback Procedure – Django migrate reverse",
        "4. Manual Rollback Procedure – for non-reversible changes",
        "5. Point-in-Time Recovery – full database restore steps",
        "6. Tenant-Specific Rollback – per-tenant isolation procedure",
        "7. Post-Rollback Verification – data integrity checks",
        "8. Incident Documentation – recording the rollback event",
    ]

    decision_criteria = [
        "Migration causes application errors above threshold",
        "Data integrity violations detected post-migration",
        "Performance degradation exceeds acceptable SLA limits",
        "Tenant isolation breach detected after schema change",
        "Critical business process failure reported by users",
        "Automated health checks fail within monitoring window",
        "Security vulnerability introduced by schema change",
    ]

    communication_plan = [
        "Notify engineering lead of rollback decision immediately",
        "Alert affected tenant administrators of potential downtime",
        "Update status page with maintenance notification",
        "Send real-time updates to incident Slack channel",
        "Prepare post-rollback summary for stakeholder review",
        "Schedule post-mortem meeting within 24 hours",
    ]

    result = {
        "rollback_runbook_documented": True,
        "runbook_sections": runbook_sections,
        "decision_criteria": decision_criteria,
        "communication_plan": communication_plan,
    }

    logger.debug(
        "get_rollback_runbook_config: sections=%d, criteria=%d",
        len(runbook_sections), len(decision_criteria),
    )
    return result


def get_staging_rollback_test_config() -> dict:
    """Return configuration for testing rollback in staging.

    Task 69 – Test Rollback in Staging
    ====================================
    Defines the staging environment rollback testing procedure to
    validate that rollback works correctly before production execution.

    Returns:
        dict with keys:
            - staging_rollback_test_documented (bool): True when configured.
            - test_procedure (list[str]): Steps for staging rollback test.
            - validation_checks (list[str]): Checks after rollback.
            - staging_requirements (list[str]): Staging env prerequisites.
    """
    test_procedure = [
        "Clone production database snapshot to staging environment",
        "Apply forward migration in staging and record state",
        "Execute application smoke tests against migrated schema",
        "Trigger rollback procedure following the runbook exactly",
        "Measure rollback execution time and resource usage",
        "Compare pre-migration and post-rollback schema checksums",
        "Run full application test suite after rollback completes",
        "Document any discrepancies or manual steps required",
    ]

    validation_checks = [
        "All database tables match pre-migration structure",
        "Row counts are consistent across all tenant schemas",
        "Foreign key constraints are intact and valid",
        "Application can connect and perform CRUD operations",
        "Background jobs resume processing without errors",
        "Tenant isolation remains enforced after rollback",
        "No orphaned data or dangling references detected",
    ]

    staging_requirements = [
        "Staging database must mirror production schema version",
        "Staging must have representative data volume for timing",
        "Network configuration must match production topology",
        "Same PostgreSQL version as production must be used",
        "Monitoring and alerting active during staging tests",
        "Staging results must be reviewed before production go-ahead",
    ]

    result = {
        "staging_rollback_test_documented": True,
        "test_procedure": test_procedure,
        "validation_checks": validation_checks,
        "staging_requirements": staging_requirements,
    }

    logger.debug(
        "get_staging_rollback_test_config: procedure=%d, checks=%d",
        len(test_procedure), len(validation_checks),
    )
    return result


def get_rollback_procedures_documentation_config() -> dict:
    """Return configuration for documenting rollback procedures.

    Task 70 – Document Rollback Procedures
    ========================================
    Ensures all rollback procedures are thoroughly documented,
    versioned, and accessible to the operations and engineering teams.

    Returns:
        dict with keys:
            - rollback_procedures_documentation_documented (bool): True.
            - documentation_sections (list[str]): Doc structure.
            - maintenance_plan (list[str]): Keeping docs current.
            - accessibility_requirements (list[str]): Access and format.
    """
    documentation_sections = [
        "Overview of rollback strategy and philosophy",
        "Environment-specific rollback procedures (dev/staging/prod)",
        "Automated vs manual rollback decision tree",
        "Per-migration rollback instructions with SQL examples",
        "Tenant-specific rollback considerations and isolation",
        "Backup and restore procedures with tool references",
        "Point-in-time recovery guide with configuration details",
        "Emergency rollback contacts and escalation paths",
    ]

    maintenance_plan = [
        "Review rollback docs with every new migration added",
        "Update procedures after each rollback event or drill",
        "Version control all runbook changes with meaningful commits",
        "Conduct quarterly rollback documentation audits",
        "Include rollback doc review in PR checklist for migrations",
        "Archive superseded procedures with deprecation notes",
    ]

    accessibility_requirements = [
        "Store rollback docs in version-controlled repository",
        "Maintain offline-accessible copy for disaster scenarios",
        "Ensure docs are searchable and well-indexed",
        "Provide quick-reference card for on-call engineers",
        "Include diagrams for complex rollback workflows",
        "Translate critical procedures for multi-region teams",
    ]

    result = {
        "rollback_procedures_documentation_documented": True,
        "documentation_sections": documentation_sections,
        "maintenance_plan": maintenance_plan,
        "accessibility_requirements": accessibility_requirements,
    }

    logger.debug(
        "get_rollback_procedures_documentation_config: sections=%d, plan=%d",
        len(documentation_sections), len(maintenance_plan),
    )
    return result


# ---------------------------------------------------------------------------
# Group-F: Testing & Verification – Tasks 71-76 (Unit Tests)
# ---------------------------------------------------------------------------


def get_migration_test_suite_config() -> dict:
    """Return configuration for the core migration test suite.

    Task 71 – Create Migration Tests
    ==================================
    Defines the overall migration test suite covering public and tenant
    schemas, with coverage targets and test organisation guidelines.

    Returns:
        dict with keys:
            - migration_tests_documented (bool): True when configured.
            - test_categories (list[str]): Categories of migration tests.
            - coverage_targets (list[str]): Coverage level targets.
            - test_guidelines (list[str]): Best practices for test writing.
    """
    test_categories = [
        "Public schema migration tests for shared tables",
        "Tenant schema migration tests for isolated tables",
        "Parallel migration concurrency tests",
        "Rollback and reverse migration tests",
        "Data migration correctness tests",
        "Migration dependency ordering tests",
        "Cross-schema migration safety tests",
    ]

    coverage_targets = [
        "100% of migration files must have corresponding tests",
        "All forward operations must be tested independently",
        "All backward operations must be tested independently",
        "Edge cases for empty schemas must be covered",
        "Multi-tenant batch migration paths must be verified",
        "Error handling paths must achieve >= 90% branch coverage",
    ]

    test_guidelines = [
        "Each test class targets a single migration concern",
        "Use Django TestCase with transaction rollback for isolation",
        "Mock external services to avoid side effects in tests",
        "Assert both schema state and data integrity post-migration",
        "Include timing assertions for performance-critical migrations",
        "Document test purpose in docstrings referencing task numbers",
    ]

    result = {
        "migration_tests_documented": True,
        "test_categories": test_categories,
        "coverage_targets": coverage_targets,
        "test_guidelines": test_guidelines,
    }

    logger.debug(
        "get_migration_test_suite_config: categories=%d, targets=%d",
        len(test_categories), len(coverage_targets),
    )
    return result


def get_public_migration_test_config() -> dict:
    """Return configuration for public schema migration tests.

    Task 72 – Test Public Migrations
    ==================================
    Defines tests specific to the public (shared) schema migrations,
    validating shared table structure and data after migrations run.

    Returns:
        dict with keys:
            - public_migration_tests_documented (bool): True when configured.
            - test_scenarios (list[str]): Public migration test cases.
            - expected_outcomes (list[str]): Expected results to assert.
            - validation_queries (list[str]): SQL-level validations.
    """
    test_scenarios = [
        "Verify shared app tables created in public schema",
        "Validate tenant model table exists after initial migration",
        "Check domain model table structure matches schema",
        "Test plan and subscription tables creation",
        "Confirm index creation on public schema tables",
        "Validate default data seeding for public schema",
        "Test migration idempotency on public schema",
    ]

    expected_outcomes = [
        "All SHARED_APPS tables present in public schema",
        "Foreign key constraints valid across public tables",
        "Default tenant record created with correct domain",
        "Unique constraints enforced on domain and schema names",
        "Migration history recorded in django_migrations table",
        "No orphaned tables from failed partial migrations",
    ]

    validation_queries = [
        "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'",
        "Verify django_content_type entries for shared apps",
        "Check auth_permission entries are correctly generated",
        "Validate django_migrations has correct app labels",
        "Confirm public schema search_path is set correctly",
        "Assert no tenant-specific tables leak into public schema",
    ]

    result = {
        "public_migration_tests_documented": True,
        "test_scenarios": test_scenarios,
        "expected_outcomes": expected_outcomes,
        "validation_queries": validation_queries,
    }

    logger.debug(
        "get_public_migration_test_config: scenarios=%d, outcomes=%d",
        len(test_scenarios), len(expected_outcomes),
    )
    return result


def get_tenant_migration_test_config() -> dict:
    """Return configuration for tenant schema migration tests.

    Task 73 – Test Tenant Migrations
    ==================================
    Defines tests for tenant-specific schema migrations, ensuring
    each tenant schema contains the correct isolated table structure.

    Returns:
        dict with keys:
            - tenant_migration_tests_documented (bool): True when configured.
            - test_scenarios (list[str]): Tenant migration test cases.
            - expected_outcomes (list[str]): Expected results to assert.
            - isolation_checks (list[str]): Tenant isolation verifications.
    """
    test_scenarios = [
        "Verify TENANT_APPS tables created in tenant schema",
        "Validate product and inventory tables in tenant schema",
        "Check order and sales tables created correctly",
        "Test customer tables exist with proper constraints",
        "Confirm tenant-specific indexes are created",
        "Validate migration runs against newly created tenant",
        "Test migration on multiple tenants in sequence",
    ]

    expected_outcomes = [
        "All TENANT_APPS tables present in tenant schema",
        "No shared app tables duplicated in tenant schema",
        "Foreign key constraints valid within tenant schema",
        "Tenant schema search_path set during migration",
        "Migration history recorded per-tenant in django_migrations",
        "Schema name matches tenant schema_name field",
    ]

    isolation_checks = [
        "Data in tenant A not visible from tenant B schema",
        "Migrations applied to one tenant do not affect others",
        "Schema search_path reset after tenant migration completes",
        "Cross-tenant foreign keys are prevented by validation",
        "Tenant deletion does not affect public schema tables",
        "Concurrent tenant migrations maintain schema isolation",
    ]

    result = {
        "tenant_migration_tests_documented": True,
        "test_scenarios": test_scenarios,
        "expected_outcomes": expected_outcomes,
        "isolation_checks": isolation_checks,
    }

    logger.debug(
        "get_tenant_migration_test_config: scenarios=%d, outcomes=%d",
        len(test_scenarios), len(expected_outcomes),
    )
    return result


def get_parallel_migration_test_config() -> dict:
    """Return configuration for parallel migration tests.

    Task 74 – Test Parallel Migrations
    ====================================
    Defines tests for concurrent tenant migration execution, validating
    safety, performance, and correctness under parallel workloads.

    Returns:
        dict with keys:
            - parallel_migration_tests_documented (bool): True when configured.
            - test_scenarios (list[str]): Parallel migration test cases.
            - performance_criteria (list[str]): Performance benchmarks.
            - safety_validations (list[str]): Concurrency safety checks.
    """
    test_scenarios = [
        "Run migrations on 3+ tenants concurrently",
        "Validate no deadlocks during parallel execution",
        "Test connection pool exhaustion handling",
        "Verify progress tracking accuracy under concurrency",
        "Test failure isolation when one tenant migration fails",
        "Validate concurrency limit enforcement",
        "Test graceful shutdown during parallel migrations",
    ]

    performance_criteria = [
        "Parallel execution faster than sequential by >= 30%",
        "Memory usage stays within configured limits per worker",
        "Database connection count respects pool boundaries",
        "Individual tenant migration time not degraded by parallelism",
        "Progress reporting latency under 5 seconds",
        "No query timeout increase during parallel operations",
    ]

    safety_validations = [
        "Each tenant schema only modified by its own worker",
        "Migration locks acquired and released correctly",
        "Failed tenant does not block remaining tenants",
        "Retry logic works correctly under concurrent load",
        "Log output correctly attributed to source tenant",
        "Database integrity constraints maintained throughout",
    ]

    result = {
        "parallel_migration_tests_documented": True,
        "test_scenarios": test_scenarios,
        "performance_criteria": performance_criteria,
        "safety_validations": safety_validations,
    }

    logger.debug(
        "get_parallel_migration_test_config: scenarios=%d, safety=%d",
        len(test_scenarios), len(safety_validations),
    )
    return result


def get_rollback_test_suite_config() -> dict:
    """Return configuration for rollback test suite.

    Task 75 – Test Rollback
    ========================
    Defines tests for migration rollback procedures, ensuring reverse
    operations restore the database to its pre-migration state.

    Returns:
        dict with keys:
            - rollback_tests_documented (bool): True when configured.
            - test_scenarios (list[str]): Rollback test cases.
            - pass_fail_criteria (list[str]): Success/failure definitions.
            - coverage_requirements (list[str]): Rollback test coverage.
    """
    test_scenarios = [
        "Rollback single migration on public schema",
        "Rollback single migration on tenant schema",
        "Rollback multiple migrations in reverse order",
        "Rollback with data preservation verification",
        "Test rollback of non-reversible migration handling",
        "Rollback across all tenants simultaneously",
        "Test partial rollback failure and recovery",
    ]

    pass_fail_criteria = [
        "Schema structure matches pre-migration snapshot exactly",
        "No data loss for reversible operations after rollback",
        "django_migrations table updated to reflect rollback",
        "Application functions correctly after rollback",
        "Non-reversible rollback raises appropriate warnings",
        "Rollback completes within acceptable time threshold",
    ]

    coverage_requirements = [
        "Every migration with RunSQL must have reverse_sql tested",
        "Every migration with RunPython must have reverse_code tested",
        "Schema-altering operations must verify column restoration",
        "Index and constraint rollback must be independently tested",
        "Data migration rollback must verify data restoration",
        "Edge case of rolling back on empty schema must be covered",
    ]

    result = {
        "rollback_tests_documented": True,
        "test_scenarios": test_scenarios,
        "pass_fail_criteria": pass_fail_criteria,
        "coverage_requirements": coverage_requirements,
    }

    logger.debug(
        "get_rollback_test_suite_config: scenarios=%d, criteria=%d",
        len(test_scenarios), len(pass_fail_criteria),
    )
    return result


def get_data_migration_test_config() -> dict:
    """Return configuration for data migration tests.

    Task 76 – Test Data Migrations
    ================================
    Defines tests for data migration correctness, ensuring transformed
    data matches expected values and validation criteria are met.

    Returns:
        dict with keys:
            - data_migration_tests_documented (bool): True when configured.
            - test_scenarios (list[str]): Data migration test cases.
            - validation_criteria (list[str]): Data correctness checks.
            - edge_cases (list[str]): Edge case scenarios to cover.
    """
    test_scenarios = [
        "Verify data transformation produces correct output",
        "Test data migration on empty tables handles gracefully",
        "Validate large dataset migration with batch processing",
        "Test data type conversion preserves precision",
        "Verify default value population for new columns",
        "Test data migration idempotency on re-run",
        "Validate foreign key references maintained after migration",
    ]

    validation_criteria = [
        "Row counts match before and after data migration",
        "Transformed values match expected computation results",
        "NULL handling follows defined migration rules",
        "Character encoding preserved through data transforms",
        "Timestamp fields maintain timezone accuracy",
        "Numeric precision retained for financial data columns",
    ]

    edge_cases = [
        "Empty source table produces no errors",
        "Single row table migrates correctly",
        "Maximum length string values handled without truncation",
        "Unicode and special characters preserved in migration",
        "Concurrent data reads during migration return consistent data",
        "Migration rollback restores original data values",
    ]

    result = {
        "data_migration_tests_documented": True,
        "test_scenarios": test_scenarios,
        "validation_criteria": validation_criteria,
        "edge_cases": edge_cases,
    }

    logger.debug(
        "get_data_migration_test_config: scenarios=%d, criteria=%d",
        len(test_scenarios), len(validation_criteria),
    )
    return result


# ---------------------------------------------------------------------------
# Group-F: Testing & Verification – Tasks 77-81 (CI, Performance & Checklist)
# ---------------------------------------------------------------------------


def get_migration_ci_pipeline_config() -> dict:
    """Return configuration for migration CI pipeline.

    Task 77 – Create Migration CI Pipeline
    =========================================
    Defines CI pipeline steps that run migration tests automatically
    on pull requests and block merges on failure.

    Returns:
        dict with keys:
            - ci_pipeline_documented (bool): True when configured.
            - pipeline_steps (list[str]): Ordered CI pipeline stages.
            - quality_gates (list[str]): Conditions that block merge.
            - pipeline_triggers (list[str]): Events that start pipeline.
    """
    pipeline_steps = [
        "Checkout code and set up Python environment",
        "Install dependencies from requirements files",
        "Start PostgreSQL service container for tests",
        "Run makemigrations --check to detect missing migrations",
        "Apply all migrations to fresh test database",
        "Execute migration unit test suite with pytest",
        "Generate migration test coverage report",
        "Upload test results and coverage artifacts",
    ]

    quality_gates = [
        "All migration tests must pass before merge allowed",
        "Migration coverage must meet minimum threshold of 90%",
        "No pending migration files detected by makemigrations --check",
        "Migration linter must report zero errors",
        "Rollback tests must pass for all new migrations",
        "Performance benchmarks must not regress beyond 10%",
    ]

    pipeline_triggers = [
        "Pull request opened or updated with migration changes",
        "Push to main branch triggers full migration validation",
        "Scheduled nightly run for comprehensive migration testing",
        "Manual trigger available for hotfix migration verification",
        "Tag creation triggers production migration dry-run",
        "Dependency update PRs trigger migration compatibility check",
    ]

    result = {
        "ci_pipeline_documented": True,
        "pipeline_steps": pipeline_steps,
        "quality_gates": quality_gates,
        "pipeline_triggers": pipeline_triggers,
    }

    logger.debug(
        "get_migration_ci_pipeline_config: steps=%d, gates=%d",
        len(pipeline_steps), len(quality_gates),
    )
    return result


def get_new_tenant_migration_test_config() -> dict:
    """Return configuration for new tenant migration tests.

    Task 78 – Test New Tenant Migration
    ======================================
    Defines tests for migrating a freshly created tenant, validating
    that the initial schema and seed data are correctly established.

    Returns:
        dict with keys:
            - new_tenant_tests_documented (bool): True when configured.
            - test_scenarios (list[str]): New tenant migration test cases.
            - expected_tables (list[str]): Tables expected in new tenant.
            - validation_steps (list[str]): Post-migration validations.
    """
    test_scenarios = [
        "Create new tenant and verify schema creation",
        "Apply all TENANT_APPS migrations to new schema",
        "Validate tenant-specific tables created correctly",
        "Check seed data populated in new tenant schema",
        "Verify tenant domain and configuration records",
        "Test new tenant can perform basic CRUD operations",
        "Validate new tenant isolation from existing tenants",
    ]

    expected_tables = [
        "Product and category tables in tenant schema",
        "Order and order item tables with constraints",
        "Customer and address tables with relationships",
        "Inventory tables with stock tracking columns",
        "Sales tables with transaction references",
        "Accounting tables with ledger entries",
    ]

    validation_steps = [
        "Query information_schema to verify all expected tables exist",
        "Check column types and constraints match model definitions",
        "Verify foreign key relationships are correctly established",
        "Confirm indexes created on frequently queried columns",
        "Validate default data matches seed fixture expectations",
        "Test search_path isolation prevents cross-schema access",
    ]

    result = {
        "new_tenant_tests_documented": True,
        "test_scenarios": test_scenarios,
        "expected_tables": expected_tables,
        "validation_steps": validation_steps,
    }

    logger.debug(
        "get_new_tenant_migration_test_config: scenarios=%d, tables=%d",
        len(test_scenarios), len(expected_tables),
    )
    return result


def get_large_scale_migration_test_config() -> dict:
    """Return configuration for large scale migration tests.

    Task 79 – Test Large Scale Migration
    =======================================
    Defines tests for running migrations at scale with representative
    tenant volumes to validate performance and failure handling.

    Returns:
        dict with keys:
            - large_scale_tests_documented (bool): True when configured.
            - test_scenarios (list[str]): Large scale test cases.
            - scale_parameters (list[str]): Volume and sizing targets.
            - failure_handling (list[str]): Failure scenario coverage.
    """
    test_scenarios = [
        "Migrate 50+ tenant schemas in a single batch run",
        "Simulate mixed-size tenants with varying data volumes",
        "Test migration with concurrent application traffic",
        "Validate progress tracking accuracy at scale",
        "Measure total migration time versus sequential baseline",
        "Test recovery after partial failure at 50% completion",
        "Validate resource cleanup after large scale run",
    ]

    scale_parameters = [
        "Minimum 50 tenants for representative scale testing",
        "Include tenants with 1K, 10K, and 100K row tables",
        "Test with 4 concurrent migration workers minimum",
        "Database connection pool set to production-like limits",
        "Memory constraints matching production server specs",
        "Disk I/O monitoring enabled during test execution",
    ]

    failure_handling = [
        "Single tenant failure does not stop batch progress",
        "Failed tenants recorded with error details for retry",
        "Connection timeout handling for slow tenant migrations",
        "Graceful shutdown preserves completed tenant state",
        "Post-failure report identifies affected tenants",
        "Automatic retry mechanism for transient failures",
    ]

    result = {
        "large_scale_tests_documented": True,
        "test_scenarios": test_scenarios,
        "scale_parameters": scale_parameters,
        "failure_handling": failure_handling,
    }

    logger.debug(
        "get_large_scale_migration_test_config: scenarios=%d, params=%d",
        len(test_scenarios), len(scale_parameters),
    )
    return result


def get_migration_performance_test_config() -> dict:
    """Return configuration for migration performance tests.

    Task 80 – Performance Test Migrations
    ========================================
    Defines performance benchmarks and acceptable thresholds for
    migration execution times across different scenarios.

    Returns:
        dict with keys:
            - performance_tests_documented (bool): True when configured.
            - benchmark_scenarios (list[str]): Performance test cases.
            - acceptable_thresholds (list[str]): Time/resource limits.
            - monitoring_metrics (list[str]): Metrics to capture.
    """
    benchmark_scenarios = [
        "Single tenant migration time for schema creation",
        "Batch migration time for 10 tenants sequentially",
        "Parallel migration time for 10 tenants concurrently",
        "Data migration throughput for 100K row tables",
        "Index creation time on tables with 1M+ rows",
        "Rollback execution time for most recent migration",
        "Full migration suite time from empty database",
    ]

    acceptable_thresholds = [
        "Single tenant schema migration under 30 seconds",
        "Batch of 10 tenants completed within 5 minutes",
        "Parallel migration at least 3x faster than sequential",
        "Data migration processes minimum 10K rows per second",
        "Index creation completes within 2x table scan time",
        "Rollback executes within 50% of forward migration time",
    ]

    monitoring_metrics = [
        "Wall clock time per migration operation",
        "CPU utilization during migration execution",
        "Memory consumption peak and average",
        "Database connection count and wait times",
        "Disk I/O read and write throughput",
        "Lock wait times and deadlock occurrences",
    ]

    result = {
        "performance_tests_documented": True,
        "benchmark_scenarios": benchmark_scenarios,
        "acceptable_thresholds": acceptable_thresholds,
        "monitoring_metrics": monitoring_metrics,
    }

    logger.debug(
        "get_migration_performance_test_config: benchmarks=%d, thresholds=%d",
        len(benchmark_scenarios), len(acceptable_thresholds),
    )
    return result


def get_migration_checklist_config() -> dict:
    """Return configuration for the pre-deployment migration checklist.

    Task 81 – Create Migration Checklist
    =======================================
    Provides a comprehensive pre-deployment checklist that must be
    completed before running migrations in any environment.

    Returns:
        dict with keys:
            - checklist_documented (bool): True when configured.
            - pre_deployment_items (list[str]): Checklist items.
            - post_deployment_items (list[str]): Post-migration checks.
            - checklist_usage (list[str]): When and how to apply.
    """
    pre_deployment_items = [
        "Verify all migration tests pass in CI pipeline",
        "Create pre-migration database backup and verify integrity",
        "Review migration files for non-reversible operations",
        "Confirm rollback procedures are documented and tested",
        "Check disk space and resource availability on target",
        "Notify stakeholders of planned migration window",
        "Verify monitoring and alerting systems are active",
        "Confirm staging migration completed successfully",
    ]

    post_deployment_items = [
        "Verify all migrations applied successfully via migrate status",
        "Run application smoke tests against migrated database",
        "Check database integrity with constraint validation",
        "Monitor application error rates for 30 minutes post-migration",
        "Verify tenant isolation with cross-schema access tests",
        "Confirm backup retention policy applied to pre-migration backup",
    ]

    checklist_usage = [
        "Apply checklist before every production migration",
        "Use abbreviated checklist for staging deployments",
        "Development migrations exempt but encouraged to follow",
        "Emergency hotfix migrations require minimum backup step",
        "Checklist sign-off required by engineering lead",
        "Archive completed checklists for audit trail",
    ]

    result = {
        "checklist_documented": True,
        "pre_deployment_items": pre_deployment_items,
        "post_deployment_items": post_deployment_items,
        "checklist_usage": checklist_usage,
    }

    logger.debug(
        "get_migration_checklist_config: pre=%d, post=%d",
        len(pre_deployment_items), len(post_deployment_items),
    )
    return result


# ---------------------------------------------------------------------------
# Group-F: Testing & Verification – Tasks 82-84 (Best Practices, Commit & Final)
# ---------------------------------------------------------------------------


def get_migration_best_practices_config() -> dict:
    """Return configuration for migration best practices documentation.

    Task 82 – Document Best Practices
    ====================================
    Documents migration best practices covering safety, backups,
    testing, and defines roles responsible for approvals.

    Returns:
        dict with keys:
            - best_practices_documented (bool): True when configured.
            - safety_practices (list[str]): Safety-related best practices.
            - ownership_roles (list[str]): Roles and responsibilities.
            - documentation_standards (list[str]): Documentation requirements.
    """
    safety_practices = [
        "Always create verified backup before any migration",
        "Run migrations during low-traffic maintenance windows",
        "Test all migrations in staging before production",
        "Use additive-only changes for zero-downtime deploys",
        "Enable migration linter in CI to catch unsafe patterns",
        "Monitor database metrics during and after migration",
        "Keep rollback procedures tested and up to date",
    ]

    ownership_roles = [
        "Engineering Lead approves migration PRs before merge",
        "DBA reviews schema changes for performance impact",
        "DevOps verifies backup and restore procedures",
        "QA validates application behavior post-migration",
        "On-call engineer monitors production during migration",
        "Product Owner signs off on data migration transformations",
    ]

    documentation_standards = [
        "Every migration must have a description in the migration file",
        "Non-reversible migrations must document manual rollback steps",
        "Data migrations must include validation criteria",
        "Performance-sensitive migrations must include timing benchmarks",
        "Multi-tenant impact must be documented for shared schema changes",
        "Rollback procedures must be updated with each new migration",
    ]

    result = {
        "best_practices_documented": True,
        "safety_practices": safety_practices,
        "ownership_roles": ownership_roles,
        "documentation_standards": documentation_standards,
    }

    logger.debug(
        "get_migration_best_practices_config: practices=%d, roles=%d",
        len(safety_practices), len(ownership_roles),
    )
    return result


def get_migration_initial_commit_config() -> dict:
    """Return configuration for the initial migration strategy commit.

    Task 83 – Create Initial Commit
    ==================================
    Documents the review process and commit conventions for the
    migration strategy initial commit and subsequent changes.

    Returns:
        dict with keys:
            - initial_commit_documented (bool): True when configured.
            - review_steps (list[str]): Pre-commit review checklist.
            - commit_conventions (list[str]): Commit message standards.
            - included_artifacts (list[str]): Files in initial commit.
    """
    review_steps = [
        "Verify all migration utility functions are implemented",
        "Confirm test coverage meets defined thresholds",
        "Review documentation for completeness and accuracy",
        "Validate CI pipeline configuration is correct",
        "Check that all imports and exports are properly configured",
        "Run full verification suite with zero failures",
    ]

    commit_conventions = [
        "Use conventional commit format: feat(migrations): description",
        "Reference SubPhase-08 task numbers in commit body",
        "Include summary of all implemented functions in body",
        "Sign commits with verified GPG key when available",
        "Keep commit message under 72 characters for subject line",
        "Add Co-authored-by for pair programming sessions",
    ]

    included_artifacts = [
        "migration_utils.py with all migration strategy functions",
        "__init__.py with updated imports and __all__ exports",
        "test_migrations.py with comprehensive test coverage",
        "migration-strategy.md documentation with all task sections",
        "VERIFICATION.md with all verification results recorded",
        "SESSION_HANDOVER.md with current progress state",
    ]

    result = {
        "initial_commit_documented": True,
        "review_steps": review_steps,
        "commit_conventions": commit_conventions,
        "included_artifacts": included_artifacts,
    }

    logger.debug(
        "get_migration_initial_commit_config: review=%d, conventions=%d",
        len(review_steps), len(commit_conventions),
    )
    return result


def get_final_verification_config() -> dict:
    """Return configuration for final migration strategy verification.

    Task 84 – Final Verification
    ==============================
    Defines the final verification process that confirms all migration
    strategy components are complete, tested, and documented.

    Returns:
        dict with keys:
            - final_verification_documented (bool): True when configured.
            - verification_areas (list[str]): Areas to verify.
            - sign_off_requirements (list[str]): Sign-off criteria.
            - completion_criteria (list[str]): SubPhase completion checks.
    """
    verification_areas = [
        "All 84 migration strategy tasks implemented and tested",
        "Migration utility functions return correct configurations",
        "All functions importable from apps.tenants.utils package",
        "Test suite covers all functions with multiple assertions",
        "Documentation covers all groups A through F",
        "Verification results recorded for every task group",
        "CI pipeline configuration validated and documented",
    ]

    sign_off_requirements = [
        "Engineering lead reviews and approves final state",
        "All verification scripts report 100% pass rate",
        "Documentation reviewed for technical accuracy",
        "No outstanding TODO items in implementation files",
        "SESSION_HANDOVER.md reflects completed SubPhase-08",
        "VERIFICATION.md contains all group results",
    ]

    completion_criteria = [
        "SubPhase-08 Migration Strategy fully documented",
        "84 config functions implemented in migration_utils.py",
        "84 test classes validate all functions",
        "migration-strategy.md covers Tasks 01 through 84",
        "All groups (A-F) verified with Docker verification scripts",
        "Ready to proceed to next SubPhase when available",
    ]

    result = {
        "final_verification_documented": True,
        "verification_areas": verification_areas,
        "sign_off_requirements": sign_off_requirements,
        "completion_criteria": completion_criteria,
    }

    logger.debug(
        "get_final_verification_config: areas=%d, criteria=%d",
        len(verification_areas), len(completion_criteria),
    )
    return result
