"""
Apps structure utilities for LankaCommerce Cloud core infrastructure.

SubPhase-01, Group-A Tasks 01-08 and Group-B Tasks 09-22 and Group-C Tasks 23-36 and Group-D Tasks 37-50 and Group-E Tasks 51-64 and Group-F Tasks 65-78 and Group-G Tasks 79-92.

Provides apps directory and package configuration helpers used by the
core application for documenting Django apps structure conventions.

Functions:
    get_apps_directory_config()       -- Apps directory config (Task 01).
    get_apps_init_config()            -- Apps __init__.py config (Task 02).
    get_python_path_config()          -- Python path config (Task 03).
    get_apps_readme_config()          -- Apps README config (Task 04).
    get_app_template_config()         -- App template config (Task 05).
    get_app_naming_convention_config() -- App naming convention config (Task 06).
    get_management_command_folder_config() -- Management command folder config (Task 07).
    get_app_creation_process_config() -- App creation process config (Task 08).
    get_core_app_directory_config()   -- Core app directory config (Task 09).
    get_core_init_config()            -- Core __init__.py config (Task 10).
    get_core_apps_config()            -- Core apps.py config (Task 11).
    get_core_models_config()          -- Core models.py config (Task 12).
    get_core_admin_config()           -- Core admin.py config (Task 13).
    get_core_urls_config()            -- Core urls.py config (Task 14).
    get_core_views_config()           -- Core views.py config (Task 15).
    get_core_serializers_config()     -- Core serializers.py config (Task 16).
    get_core_utils_directory_config() -- Core utils/ directory config (Task 17).
    get_core_mixins_directory_config() -- Core mixins/ directory config (Task 18).
    get_core_exceptions_config()      -- Core exceptions.py config (Task 19).
    get_core_constants_config()       -- Core constants.py config (Task 20).
    get_core_tests_directory_config() -- Core tests/ directory config (Task 21).
    get_core_registration_config()    -- Core INSTALLED_APPS registration config (Task 22).
    get_tenants_app_directory_config() -- Tenants app directory config (Task 23).
    get_tenants_init_config()         -- Tenants __init__.py config (Task 24).
    get_tenants_apps_config()         -- Tenants apps.py config (Task 25).
    get_tenants_models_config()       -- Tenants models.py config (Task 26).
    get_tenants_admin_config()        -- Tenants admin.py config (Task 27).
    get_tenants_urls_config()         -- Tenants urls.py config (Task 28).
    get_tenants_registration_config() -- Tenants registration config (Task 29).
    get_users_app_directory_config()  -- Users app directory config (Task 30).
    get_users_init_config()           -- Users __init__.py config (Task 31).
    get_users_apps_config()           -- Users apps.py config (Task 32).
    get_users_models_config()         -- Users models.py config (Task 33).
    get_users_admin_config()          -- Users admin.py config (Task 34).
    get_users_urls_config()           -- Users urls.py config (Task 35).
    get_users_registration_config()   -- Users registration config (Task 36).
    get_products_app_directory_config() -- Products app directory config (Task 37).
    get_products_init_config()        -- Products __init__.py config (Task 38).
    get_products_apps_config()        -- Products apps.py config (Task 39).
    get_products_models_config()      -- Products models.py config (Task 40).
    get_products_admin_config()       -- Products admin.py config (Task 41).
    get_products_urls_config()        -- Products urls.py config (Task 42).
    get_products_registration_config() -- Products registration config (Task 43).
    get_inventory_app_directory_config() -- Inventory app directory config (Task 44).
    get_inventory_init_config()       -- Inventory __init__.py config (Task 45).
    get_inventory_apps_config()       -- Inventory apps.py config (Task 46).
    get_inventory_models_config()     -- Inventory models.py config (Task 47).
    get_inventory_admin_config()      -- Inventory admin.py config (Task 48).
    get_inventory_urls_config()       -- Inventory urls.py config (Task 49).
    get_inventory_registration_config() -- Inventory registration config (Task 50).
    get_sales_app_directory_config()  -- Sales app directory config (Task 51).
    get_sales_init_config()           -- Sales __init__.py config (Task 52).
    get_sales_apps_config()           -- Sales apps.py config (Task 53).
    get_sales_models_config()         -- Sales models.py config (Task 54).
    get_sales_admin_config()          -- Sales admin.py config (Task 55).
    get_sales_urls_config()           -- Sales urls.py config (Task 56).
    get_sales_registration_config()   -- Sales registration config (Task 57).
    get_customers_app_directory_config() -- Customers app directory config (Task 58).
    get_customers_init_config()       -- Customers __init__.py config (Task 59).
    get_customers_apps_config()       -- Customers apps.py config (Task 60).
    get_customers_models_config()     -- Customers models.py config (Task 61).
    get_customers_admin_config()      -- Customers admin.py config (Task 62).
    get_customers_urls_config()       -- Customers urls.py config (Task 63).
    get_customers_registration_config() -- Customers registration config (Task 64).
    get_vendors_app_config()          -- Vendors app config (Task 65).
    get_vendors_structure_config()    -- Vendors structure config (Task 66).
    get_vendors_registration_config() -- Vendors registration config (Task 67).
    get_hr_app_config()               -- HR app config (Task 68).
    get_hr_structure_config()         -- HR structure config (Task 69).
    get_hr_registration_config()      -- HR registration config (Task 70).
    get_accounting_app_config()       -- Accounting app config (Task 71).
    get_accounting_structure_config() -- Accounting structure config (Task 72).
    get_accounting_registration_config() -- Accounting registration config (Task 73).
    get_webstore_app_config()         -- Webstore app config (Task 74).
    get_webstore_structure_config()   -- Webstore structure config (Task 75).
    get_webstore_registration_config() -- Webstore registration config (Task 76).
    get_reports_app_config()           -- Reports app config (Task 77).
    get_reports_registration_config()  -- Reports registration config (Task 78).
    get_integrations_app_config()      -- Integrations app config (Task 79).
    get_integrations_structure_config() -- Integrations structure config (Task 80).
    get_integrations_registration_config() -- Integrations registration config (Task 81).
    get_main_urls_router_config()      -- Main urls.py router config (Task 82).
    get_app_urls_inclusion_config()    -- App URLs inclusion config (Task 83).
    get_api_router_config()            -- API router config (Task 84).
    get_installed_apps_order_config()  -- INSTALLED_APPS order config (Task 85).
    get_shared_apps_config()           -- SHARED_APPS config (Task 86).
    get_tenant_apps_config()           -- TENANT_APPS config (Task 87).
    get_initial_migrations_config()    -- Initial migrations config (Task 88).
    get_app_structure_verification_config() -- App structure verification config (Task 89).
    get_apps_documentation_config()    -- Apps documentation config (Task 90).
    get_initial_commit_config()        -- Initial commit config (Task 91).
    get_server_start_verification_config() -- Server start verification config (Task 92).

See also:
    - apps.core.utils.__init__  -- public re-exports
    - docs/architecture/apps-structure.md
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_apps_directory_config() -> dict:
    """Return apps directory configuration.

    Documents the base apps directory setup, including directory
    purpose, location within the project, and organizational
    conventions for housing Django applications.

    SubPhase-01, Group-A, Task 01.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_details* list, *organization_rules* list,
              and *directory_conventions* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_details": [
            "apps directory located at backend/apps/ as the root for all Django apps",
            "serves as the central container for all domain-specific applications",
            "each subdirectory represents a single Django application module",
            "directory created during Phase 03 core backend infrastructure setup",
            "maintains flat structure with no nested app directories allowed",
            "shared utilities and mixins reside in the core app subdirectory",
        ],
        "organization_rules": [
            "each app must have its own directory with __init__.py and apps.py",
            "app names use lowercase snake_case matching Python package conventions",
            "related apps grouped logically but remain as separate top-level packages",
            "cross-app imports use absolute paths from the apps root namespace",
            "app-specific templates placed in app/templates/app_name/ subdirectory",
            "app-specific static files placed in app/static/app_name/ subdirectory",
        ],
        "directory_conventions": [
            "new apps added via django-admin startapp within the apps directory",
            "app directory names must not conflict with Python standard library modules",
            "each app directory must contain a migrations/ subdirectory for schema changes",
            "test files for each app reside in backend/tests/app_name/ directory",
            "utility modules placed in app/utils/ subdirectory with own __init__.py",
            "management commands placed in app/management/commands/ subdirectory",
        ],
    }
    logger.debug(
        "Apps directory config: directory_details=%d, organization_rules=%d",
        len(config["directory_details"]),
        len(config["organization_rules"]),
    )
    return config


def get_apps_init_config() -> dict:
    """Return apps __init__.py configuration.

    Documents the apps package initialization file setup, including
    its purpose for Python package recognition, module discovery,
    and any default package-level imports.

    SubPhase-01, Group-A, Task 02.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_purpose* list, *module_discovery* list,
              and *init_conventions* list.
    """
    config: dict = {
        "init_documented": True,
        "init_purpose": [
            "__init__.py marks backend/apps/ as a Python package for imports",
            "enables absolute import paths like apps.core.models from any module",
            "required for Django to discover and register installed applications",
            "kept minimal with only essential package-level docstring content",
            "no wildcard imports or heavy initialization logic in the root init",
            "serves as the entry point for the apps namespace across the project",
        ],
        "module_discovery": [
            "Django autodiscover_modules uses apps package to find admin registrations",
            "pytest discovers test modules through the apps package namespace",
            "migration runner resolves app labels through the apps package hierarchy",
            "management commands discovered via apps.app_name.management.commands path",
            "template loaders resolve app templates through installed apps ordering",
            "signal handlers connected during app ready() via apps package imports",
        ],
        "init_conventions": [
            "root __init__.py contains only a module docstring and no executable code",
            "each app __init__.py may set default_app_config for legacy Django versions",
            "sub-package __init__.py files re-export public API for convenience imports",
            "circular import prevention by deferring heavy imports to function scope",
            "version or metadata constants may be defined at package level if needed",
            "type annotations imported under TYPE_CHECKING guard to avoid runtime cost",
        ],
    }
    logger.debug(
        "Apps init config: init_purpose=%d, module_discovery=%d",
        len(config["init_purpose"]),
        len(config["module_discovery"]),
    )
    return config


def get_python_path_config() -> dict:
    """Return Python path configuration.

    Documents the PYTHONPATH update required to include the apps
    directory, covering settings placement, environment variable
    configuration, and import resolution behavior.

    SubPhase-01, Group-A, Task 03.

    Returns:
        dict: Configuration with *path_documented* flag,
              *path_settings* list, *environment_setup* list,
              and *resolution_behavior* list.
    """
    config: dict = {
        "path_documented": True,
        "path_settings": [
            "BASE_DIR / 'apps' appended to sys.path in base settings module",
            "PYTHONPATH environment variable includes backend/apps/ in CI config",
            "Django INSTALLED_APPS entries reference apps without apps. prefix when path set",
            "wsgi.py and asgi.py ensure path is set before application initialization",
            "manage.py includes path setup for development and management commands",
            "pytest.ini or conftest.py mirrors path configuration for test execution",
        ],
        "environment_setup": [
            "development environment uses .env file with PYTHONPATH=backend/apps",
            "Docker container sets PYTHONPATH in Dockerfile or docker-compose.yml",
            "CI workflow exports PYTHONPATH before running test and lint steps",
            "production deployment sets PYTHONPATH via gunicorn or uwsgi configuration",
            "virtual environment activation script may prepend apps path automatically",
            "IDE settings configure source roots to include backend/apps/ for intellisense",
        ],
        "resolution_behavior": [
            "absolute imports resolve apps.core.models to backend/apps/core/models.py",
            "relative imports within an app use standard Python dot notation",
            "Django app label resolution uses the apps.py AppConfig.name attribute",
            "namespace packages not used to avoid ambiguity in import resolution",
            "import errors due to missing path raise clear ModuleNotFoundError messages",
            "path ordering ensures project apps take precedence over third-party packages",
        ],
    }
    logger.debug(
        "Python path config: path_settings=%d, environment_setup=%d",
        len(config["path_settings"]),
        len(config["environment_setup"]),
    )
    return config


def get_apps_readme_config() -> dict:
    """Return apps README configuration.

    Documents the README file for the apps directory, including
    content structure, app listing format, and maintenance
    guidelines for keeping documentation current.

    SubPhase-01, Group-A, Task 04.

    Returns:
        dict: Configuration with *readme_documented* flag,
              *readme_content* list, *app_listing_format* list,
              and *maintenance_guidelines* list.
    """
    config: dict = {
        "readme_documented": True,
        "readme_content": [
            "README.md placed at backend/apps/README.md for directory documentation",
            "header section explains the purpose of the apps directory structure",
            "table of contents lists all Django applications with brief descriptions",
            "architecture section describes app dependencies and communication patterns",
            "getting started section explains how to create a new application",
            "conventions section documents naming, structure, and import rules",
        ],
        "app_listing_format": [
            "each app listed with name, one-line description, and phase of creation",
            "apps grouped by domain: core, tenants, products, orders, users, etc.",
            "dependency arrows shown between apps that have cross-app imports",
            "status badge indicates whether app is stable, beta, or experimental",
            "link to each app own README for detailed module documentation",
            "last updated date shown for each app entry to track staleness",
        ],
        "maintenance_guidelines": [
            "README updated whenever a new app is added or an existing app is renamed",
            "app removal requires updating README and removing all cross-references",
            "quarterly review of README accuracy scheduled as part of documentation sprint",
            "pull request template includes checkbox to verify apps README is current",
            "automated CI check validates all listed apps exist as directories",
            "changelog section at bottom of README tracks structural changes over time",
        ],
    }
    logger.debug(
        "Apps README config: readme_content=%d, app_listing_format=%d",
        len(config["readme_content"]),
        len(config["app_listing_format"]),
    )
    return config


def get_app_template_config() -> dict:
    """Return app template configuration.

    Documents the reusable app template structure that ensures
    consistent file layout across all Django applications, including
    standard files, directories, and boilerplate content.

    SubPhase-01, Group-A, Task 05.

    Returns:
        dict: Configuration with *template_documented* flag,
              *template_files* list, *template_directories* list,
              and *template_usage* list.
    """
    config: dict = {
        "template_documented": True,
        "template_files": [
            "__init__.py with package docstring and optional default_app_config",
            "apps.py with AppConfig subclass defining name, label, and verbose_name",
            "models.py with base model imports and initial model placeholder",
            "admin.py with admin site registration imports and placeholder",
            "views.py with base view imports and initial view placeholder",
            "urls.py with app_name namespace and empty urlpatterns list",
        ],
        "template_directories": [
            "migrations/ directory with __init__.py for schema migration files",
            "templates/app_name/ directory for app-specific HTML templates",
            "static/app_name/ directory for app-specific CSS, JS, and images",
            "management/commands/ directory for custom management commands",
            "utils/ directory with __init__.py for app-level utility modules",
            "tests/ directory or tests.py file for app-level unit tests",
        ],
        "template_usage": [
            "copy template directory and rename to match new app name",
            "update AppConfig class name and attributes in apps.py",
            "register new app in INSTALLED_APPS within Django settings",
            "add URL include entry in project or tenant URL configuration",
            "create initial migration with python manage.py makemigrations",
            "update apps README.md with new app entry and description",
        ],
    }
    logger.debug(
        "App template config: template_files=%d, template_directories=%d",
        len(config["template_files"]),
        len(config["template_directories"]),
    )
    return config


def get_app_naming_convention_config() -> dict:
    """Return app naming convention configuration.

    Documents the naming rules for Django applications, including
    lowercase singular names, allowed exceptions, and label
    conventions used in INSTALLED_APPS and database tables.

    SubPhase-01, Group-A, Task 06.

    Returns:
        dict: Configuration with *conventions_documented* flag,
              *naming_rules* list, *naming_exceptions* list,
              and *label_conventions* list.
    """
    config: dict = {
        "conventions_documented": True,
        "naming_rules": [
            "app names use lowercase singular nouns like product, order, vendor",
            "multi-word app names use snake_case like web_store or sales_report",
            "app name must be a valid Python identifier without hyphens or spaces",
            "app name should clearly reflect the bounded context it represents",
            "abbreviations avoided unless universally understood like hr or api",
            "app name length kept under 20 characters for readability in imports",
        ],
        "naming_exceptions": [
            "users app uses plural form as Django convention for auth user model",
            "tenants app uses plural form to align with django-tenants library naming",
            "vendors app uses plural to match the established commerce domain language",
            "customers app uses plural to remain consistent with vendors naming",
            "orders app uses plural following e-commerce industry standard terminology",
            "products app uses plural to align with catalog domain conventions",
        ],
        "label_conventions": [
            "AppConfig.label matches directory name for consistent database table prefix",
            "database tables prefixed with app_label underscore model_name pattern",
            "verbose_name uses title case with spaces for admin display purposes",
            "INSTALLED_APPS entry uses full dotted path apps.app_name format",
            "URL namespace matches app_label for reverse URL resolution consistency",
            "migration file prefix uses app_label for cross-app dependency references",
        ],
    }
    logger.debug(
        "App naming convention config: naming_rules=%d, naming_exceptions=%d",
        len(config["naming_rules"]),
        len(config["naming_exceptions"]),
    )
    return config


def get_management_command_folder_config() -> dict:
    """Return management command folder configuration.

    Documents the management command folder structure within the
    app template, including directory layout, __init__.py files,
    and conventions for custom Django management commands.

    SubPhase-01, Group-A, Task 07.

    Returns:
        dict: Configuration with *folder_documented* flag,
              *folder_structure* list, *command_conventions* list,
              and *command_examples* list.
    """
    config: dict = {
        "folder_documented": True,
        "folder_structure": [
            "management/ directory at app root with __init__.py for package recognition",
            "management/commands/ subdirectory with __init__.py for command discovery",
            "each command file named after the command it implements in snake_case",
            "command class inherits from django.core.management.base.BaseCommand",
            "help attribute provides description shown in manage.py help output",
            "add_arguments method defines CLI parameters using argparse conventions",
        ],
        "command_conventions": [
            "command names use snake_case matching the module filename exactly",
            "each command provides a clear help string for documentation",
            "commands use self.stdout.write for output instead of print statements",
            "error conditions raise CommandError for proper exit code handling",
            "long-running commands support --verbosity flag for output control",
            "destructive commands require --no-input flag to skip confirmation",
        ],
        "command_examples": [
            "seed_tenants command to populate development tenant data",
            "cleanup_schemas command to remove orphaned tenant schemas",
            "generate_report command to create tenant usage statistics",
            "sync_permissions command to update role-based access entries",
            "validate_config command to check application configuration",
            "export_data command to serialize tenant data for backup",
        ],
    }
    logger.debug(
        "Management command folder config: folder_structure=%d, command_conventions=%d",
        len(config["folder_structure"]),
        len(config["command_conventions"]),
    )
    return config


def get_app_creation_process_config() -> dict:
    """Return app creation process configuration.

    Documents the standardized process for creating new Django
    applications, including step-by-step instructions, validation
    checks, and post-creation registration requirements.

    SubPhase-01, Group-A, Task 08.

    Returns:
        dict: Configuration with *process_documented* flag,
              *creation_steps* list, *validation_checks* list,
              and *registration_requirements* list.
    """
    config: dict = {
        "process_documented": True,
        "creation_steps": [
            "run django-admin startapp app_name inside backend/apps/ directory",
            "update apps.py with correct AppConfig name, label, and verbose_name",
            "move or create models.py, views.py, urls.py with proper imports",
            "create utils/ subdirectory with __init__.py for utility modules",
            "create management/commands/ directories with __init__.py files",
            "add initial migration with python manage.py makemigrations app_name",
        ],
        "validation_checks": [
            "verify app directory exists under backend/apps/ with __init__.py",
            "confirm AppConfig.name matches the full dotted path to the app",
            "check that app name does not conflict with existing apps or packages",
            "validate models inherit from appropriate base classes or mixins",
            "ensure URLs are properly namespaced with app_name variable set",
            "run python manage.py check to validate app configuration",
        ],
        "registration_requirements": [
            "add app dotted path to INSTALLED_APPS in base settings module",
            "include app URLs in project urlpatterns or tenant URL configuration",
            "register admin classes if app has models requiring admin interface",
            "connect signal handlers in app ready() method if signals are used",
            "update apps README.md with new app entry and description",
            "create test directory at backend/tests/app_name/ with __init__.py",
        ],
    }
    logger.debug(
        "App creation process config: creation_steps=%d, validation_checks=%d",
        len(config["creation_steps"]),
        len(config["validation_checks"]),
    )
    return config


def get_core_app_directory_config() -> dict:
    """Return core app directory configuration.

    Documents the core application directory structure, including
    its purpose as the shared utilities and base functionality
    provider for all other applications in the project.

    SubPhase-01, Group-B, Task 09.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_purpose* list, *directory_contents* list,
              and *dependency_role* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_purpose": [
            "core app located at backend/apps/core/ as the shared foundation app",
            "provides base models, mixins, and abstract classes for all other apps",
            "contains shared utility functions and helper modules used project-wide",
            "houses custom template tags and filters for common rendering needs",
            "serves as the home for project-wide management commands",
            "defines shared signal handlers and middleware components",
        ],
        "directory_contents": [
            "__init__.py marks core as a Python package with app docstring",
            "apps.py contains CoreConfig with app metadata and ready() hook",
            "models.py holds base model classes and shared abstract models",
            "admin.py registers core models with the Django admin interface",
            "views.py provides shared view mixins and base view classes",
            "urls.py defines core URL patterns under the /api/v1/core/ namespace",
        ],
        "dependency_role": [
            "all other apps may import from core but core imports from no other app",
            "core provides TenantAwareModel mixin used by tenant-scoped models",
            "core defines TimeStampedModel base with created_at and updated_at fields",
            "core houses SoftDeleteModel mixin for logical deletion support",
            "core contains permission mixins shared across all API view classes",
            "core provides pagination and filtering utilities for list endpoints",
        ],
    }
    logger.debug(
        "Core app directory config: directory_purpose=%d, directory_contents=%d",
        len(config["directory_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_core_init_config() -> dict:
    """Return core __init__.py configuration.

    Documents the core application package initialization, including
    the module docstring, package-level exports, and conventions
    for the core app __init__.py file.

    SubPhase-01, Group-B, Task 10.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_contents* list, *package_exports* list,
              and *init_guidelines* list.
    """
    config: dict = {
        "init_documented": True,
        "init_contents": [
            "module docstring describing core app purpose and responsibilities",
            "default_app_config set to apps.core.apps.CoreConfig for auto-discovery",
            "no heavy imports at package level to avoid circular dependency issues",
            "version constant may be defined for core app versioning if needed",
            "TYPE_CHECKING imports guarded for type annotation convenience",
            "package-level __all__ list defines public API surface for core app",
        ],
        "package_exports": [
            "base model classes exported for convenient import by other apps",
            "shared mixin classes available from apps.core namespace directly",
            "utility functions re-exported from apps.core.utils sub-package",
            "custom exception classes exported for project-wide error handling",
            "constant values and enumerations shared across all applications",
            "signal names exported for cross-app signal connection patterns",
        ],
        "init_guidelines": [
            "keep __init__.py lightweight to minimize import-time side effects",
            "defer model imports to function scope if used in init-time code",
            "document any package-level constants with inline comments",
            "update __all__ list when adding new public classes or functions",
            "avoid executing database queries during package initialization",
            "test that importing apps.core does not trigger unexpected side effects",
        ],
    }
    logger.debug(
        "Core init config: init_contents=%d, package_exports=%d",
        len(config["init_contents"]),
        len(config["package_exports"]),
    )
    return config


def get_core_apps_config() -> dict:
    """Return core apps.py configuration.

    Documents the CoreConfig AppConfig subclass, including the
    app name, label, verbose name, and the ready() method hook
    for signal registration and startup tasks.

    SubPhase-01, Group-B, Task 11.

    Returns:
        dict: Configuration with *config_documented* flag,
              *config_attributes* list, *ready_hook_tasks* list,
              and *config_conventions* list.
    """
    config: dict = {
        "config_documented": True,
        "config_attributes": [
            "name set to apps.core matching the full dotted Python path",
            "label set to core for database table prefix and migration references",
            "verbose_name set to Core for human-readable display in admin",
            "default_auto_field set to django.db.models.BigAutoField for primary keys",
            "AppConfig subclass named CoreConfig following Django naming convention",
            "module-level docstring documents the purpose of the config class",
        ],
        "ready_hook_tasks": [
            "import and connect signal handlers defined in apps.core.signals module",
            "register custom check framework checks for configuration validation",
            "log application startup confirmation message at info level",
            "validate required environment variables are set on app initialization",
            "register custom template tags if using autodiscovery patterns",
            "initialize any caching or connection pool warm-up on first load",
        ],
        "config_conventions": [
            "one AppConfig class per apps.py file following Django best practice",
            "ready() method kept minimal to avoid slowing down startup time",
            "signal imports placed inside ready() to prevent circular imports",
            "system checks registered with tags for selective execution",
            "verbose_name uses title case without underscores for admin display",
            "app label matches directory name for consistent ORM table naming",
        ],
    }
    logger.debug(
        "Core apps config: config_attributes=%d, ready_hook_tasks=%d",
        len(config["config_attributes"]),
        len(config["ready_hook_tasks"]),
    )
    return config


def get_core_models_config() -> dict:
    """Return core models.py configuration.

    Documents the core models placeholder file, including its intent
    to house base model classes and abstract models that will be
    extended by other applications in later subphases.

    SubPhase-01, Group-B, Task 12.

    Returns:
        dict: Configuration with *models_documented* flag,
              *placeholder_intent* list, *future_models* list,
              and *model_conventions* list.
    """
    config: dict = {
        "models_documented": True,
        "placeholder_intent": [
            "models.py created as placeholder for base model definitions",
            "initial file contains imports and docstring but no concrete models",
            "base abstract models added during SubPhase-02 base models setup",
            "placeholder ensures migration framework recognizes core app early",
            "comments document planned model hierarchy for developer reference",
            "file structure prepared for TimeStampedModel and SoftDeleteModel",
        ],
        "future_models": [
            "TimeStampedModel abstract base with created_at and updated_at fields",
            "SoftDeleteModel abstract mixin with is_deleted and deleted_at fields",
            "TenantAwareModel abstract base linking models to tenant schema",
            "UUIDModel abstract base using UUID primary key instead of integer",
            "OrderedModel abstract mixin with position field for sortable records",
            "SlugModel abstract mixin with auto-generated slug from name field",
        ],
        "model_conventions": [
            "all concrete models inherit from at least TimeStampedModel base",
            "Meta class defines ordering, verbose_name, and constraints explicitly",
            "string representation returns a meaningful human-readable value",
            "model managers defined as separate classes not inline on models",
            "field choices use TextChoices or IntegerChoices enumeration classes",
            "foreign keys specify on_delete behavior and related_name explicitly",
        ],
    }
    logger.debug(
        "Core models config: placeholder_intent=%d, future_models=%d",
        len(config["placeholder_intent"]),
        len(config["future_models"]),
    )
    return config


def get_core_admin_config() -> dict:
    """Return core admin.py configuration.

    Documents the core admin setup placeholder, including its intent
    to register core models with the Django admin interface and
    conventions for admin class configuration.

    SubPhase-01, Group-B, Task 13.

    Returns:
        dict: Configuration with *admin_documented* flag,
              *admin_intent* list, *registration_plan* list,
              and *admin_conventions* list.
    """
    config: dict = {
        "admin_documented": True,
        "admin_intent": [
            "admin.py created as placeholder for future model admin registration",
            "initial file imports django.contrib.admin but registers no models yet",
            "admin classes added when concrete core models are defined",
            "placeholder ensures admin autodiscover includes core app",
            "comments document planned admin customizations for each model",
            "tenant-aware admin filtering applied when multi-tenant models exist",
        ],
        "registration_plan": [
            "register TimeStampedModel subclasses with read-only timestamp fields",
            "register SoftDeleteModel subclasses with custom queryset filtering",
            "admin list_display includes created_at and updated_at for audit trail",
            "search_fields configured for name and identifier columns on each model",
            "list_filter includes is_active and created_at date hierarchy",
            "inline model admins defined for parent-child model relationships",
        ],
        "admin_conventions": [
            "each model gets a dedicated ModelAdmin subclass not decorator-only",
            "fieldsets group related fields under logical section headings",
            "readonly_fields used for auto-populated fields like timestamps and UUIDs",
            "custom actions defined for bulk operations on model querysets",
            "admin site header and title customized in core admin module",
            "permissions checked with has_module_permission for tenant isolation",
        ],
    }
    logger.debug(
        "Core admin config: admin_intent=%d, registration_plan=%d",
        len(config["admin_intent"]),
        len(config["registration_plan"]),
    )
    return config


def get_core_urls_config() -> dict:
    """Return core urls.py configuration.

    Documents the core URL configuration, including namespace setup,
    API versioning integration, and placeholder patterns for future
    core endpoints under the /api/v1/ prefix.

    SubPhase-01, Group-B, Task 14.

    Returns:
        dict: Configuration with *urls_documented* flag,
              *url_structure* list, *versioning_setup* list,
              and *url_conventions* list.
    """
    config: dict = {
        "urls_documented": True,
        "url_structure": [
            "app_name variable set to core for URL namespace resolution",
            "urlpatterns list initialized empty as placeholder for future routes",
            "core URLs included in project urls.py under api/v1/core/ prefix",
            "health check endpoint planned at /api/v1/core/health/ for monitoring",
            "version info endpoint planned at /api/v1/core/version/ for debugging",
            "system status endpoint planned at /api/v1/core/status/ for ops team",
        ],
        "versioning_setup": [
            "API versioning uses URL path prefix pattern /api/v1/ for version 1",
            "core URLs registered under versioned namespace core:endpoint-name",
            "future API versions add /api/v2/ prefix with separate URL module",
            "version prefix handled in project-level URL configuration not per-app",
            "deprecation headers added to responses for sunset API versions",
            "client version detection via Accept header or URL path matching",
        ],
        "url_conventions": [
            "URL patterns use path() with named routes for reverse resolution",
            "view names use lowercase-hyphenated format like health-check",
            "API endpoints return JSON responses via DRF APIView subclasses",
            "list endpoints support pagination, filtering, and ordering parameters",
            "detail endpoints use UUID or slug lookup fields not integer IDs",
            "URL patterns documented with inline comments for developer reference",
        ],
    }
    logger.debug(
        "Core urls config: url_structure=%d, versioning_setup=%d",
        len(config["url_structure"]),
        len(config["versioning_setup"]),
    )
    return config


def get_core_views_config() -> dict:
    """Return core views.py configuration.

    Documents the core views placeholder module, including its
    purpose for housing shared view classes, base API views,
    and common endpoint patterns used across applications.

    SubPhase-01, Group-B, Task 15.

    Returns:
        dict: Configuration with *views_documented* flag,
              *view_placeholders* list, *shared_views* list,
              and *view_conventions* list.
    """
    config: dict = {
        "views_documented": True,
        "view_placeholders": [
            "views.py created as placeholder for shared core view classes",
            "initial file imports DRF APIView and Django generic views",
            "concrete view implementations added in later subphases",
            "health check view planned for /api/v1/core/health/ endpoint",
            "version info view planned for /api/v1/core/version/ endpoint",
            "placeholder docstring documents intended view hierarchy",
        ],
        "shared_views": [
            "BaseAPIView providing standard response format for all endpoints",
            "TenantAwareAPIView adding automatic tenant context injection",
            "PaginatedListView with configurable page size and ordering",
            "BulkActionView for handling multi-object operations in one request",
            "ExportView for generating CSV and Excel downloads from querysets",
            "HealthCheckView returning system status and dependency checks",
        ],
        "view_conventions": [
            "all API views inherit from BaseAPIView for consistent response format",
            "permission classes applied at view level not URL level",
            "serializer_class attribute set on all views for request validation",
            "queryset filtered by tenant context in get_queryset method override",
            "pagination applied automatically to list endpoints via mixin",
            "exception handling delegated to custom exception handler function",
        ],
    }
    logger.debug(
        "Core views config: view_placeholders=%d, shared_views=%d",
        len(config["view_placeholders"]),
        len(config["shared_views"]),
    )
    return config


def get_core_serializers_config() -> dict:
    """Return core serializers.py configuration.

    Documents the core serializers placeholder module, including
    its purpose for shared DRF serializer base classes and common
    field definitions used across applications.

    SubPhase-01, Group-B, Task 16.

    Returns:
        dict: Configuration with *serializers_documented* flag,
              *serializer_placeholders* list, *shared_serializers* list,
              and *serializer_conventions* list.
    """
    config: dict = {
        "serializers_documented": True,
        "serializer_placeholders": [
            "serializers.py created as placeholder for shared serializer classes",
            "initial file imports DRF serializers module and field types",
            "concrete serializer implementations added during API development",
            "base serializers define common field patterns for all apps",
            "placeholder docstring documents intended serializer hierarchy",
            "timestamp mixin serializer planned for created_at and updated_at",
        ],
        "shared_serializers": [
            "BaseModelSerializer with automatic timestamp field inclusion",
            "TenantAwareSerializer adding tenant_id read-only field to output",
            "PaginatedResponseSerializer wrapping list results with metadata",
            "BulkOperationSerializer for validating multi-object requests",
            "ErrorResponseSerializer standardizing error output format",
            "FileUploadSerializer handling multipart file validation",
        ],
        "serializer_conventions": [
            "all serializers inherit from BaseModelSerializer for consistent fields",
            "read_only_fields includes id, created_at, and updated_at by default",
            "write-only fields like password explicitly listed in extra_kwargs",
            "nested serializer depth kept to 1 level to avoid N+1 queries",
            "validation methods prefixed with validate_ for field-level checks",
            "custom create and update methods handle nested writable fields",
        ],
    }
    logger.debug(
        "Core serializers config: serializer_placeholders=%d, shared_serializers=%d",
        len(config["serializer_placeholders"]),
        len(config["shared_serializers"]),
    )
    return config


def get_core_utils_directory_config() -> dict:
    """Return core utils/ directory configuration.

    Documents the core utilities directory structure, including
    its purpose for housing shared helper functions, formatting
    utilities, and common computation modules.

    SubPhase-01, Group-B, Task 17.

    Returns:
        dict: Configuration with *utils_documented* flag,
              *utils_purpose* list, *planned_modules* list,
              and *utils_conventions* list.
    """
    config: dict = {
        "utils_documented": True,
        "utils_purpose": [
            "utils/ directory at apps/core/utils/ for shared utility modules",
            "__init__.py re-exports public utility functions for convenience",
            "utility modules organized by domain: formatting, validation, helpers",
            "no Django model or view imports allowed in pure utility modules",
            "utility functions are stateless and side-effect free where possible",
            "shared across all apps via apps.core.utils import path",
        ],
        "planned_modules": [
            "string_utils.py for text formatting, slugification, and truncation",
            "date_utils.py for timezone-aware date parsing and formatting helpers",
            "file_utils.py for file path validation and safe filename generation",
            "crypto_utils.py for hashing, token generation, and signature helpers",
            "pagination_utils.py for cursor and offset pagination calculations",
            "import_utils.py for dynamic module loading and lazy import patterns",
        ],
        "utils_conventions": [
            "each utility module focuses on a single domain of functionality",
            "all public functions documented with docstrings and type annotations",
            "utility functions tested independently in tests/core/ test modules",
            "__init__.py __all__ list updated when adding new public functions",
            "avoid circular imports by keeping utils free of app model dependencies",
            "logging added at debug level for operation tracking in utilities",
        ],
    }
    logger.debug(
        "Core utils directory config: utils_purpose=%d, planned_modules=%d",
        len(config["utils_purpose"]),
        len(config["planned_modules"]),
    )
    return config


def get_core_mixins_directory_config() -> dict:
    """Return core mixins/ directory configuration.

    Documents the core mixins directory structure, including its
    purpose for housing shared model mixins, view mixins, and
    serializer mixins used across all applications.

    SubPhase-01, Group-B, Task 18.

    Returns:
        dict: Configuration with *mixins_documented* flag,
              *mixins_purpose* list, *planned_mixins* list,
              and *mixin_conventions* list.
    """
    config: dict = {
        "mixins_documented": True,
        "mixins_purpose": [
            "mixins/ directory at apps/core/mixins/ for shared mixin classes",
            "__init__.py re-exports all mixin classes for convenient imports",
            "model mixins provide reusable field sets and behaviors for models",
            "view mixins add common request processing logic to API views",
            "serializer mixins standardize field inclusion and validation patterns",
            "mixins follow single-responsibility principle with focused behavior",
        ],
        "planned_mixins": [
            "TimeStampedMixin adding created_at and updated_at model fields",
            "SoftDeleteMixin adding is_deleted flag and deleted_at timestamp",
            "TenantScopedMixin adding tenant foreign key and schema filtering",
            "AuditLogMixin tracking created_by and updated_by user references",
            "OrderableMixin adding position field for manual record ordering",
            "SlugMixin auto-generating URL-safe slug from a source field",
        ],
        "mixin_conventions": [
            "mixin class names end with Mixin suffix for clear identification",
            "each mixin provides a single focused behavior without side effects",
            "mixin Meta class uses abstract = True to prevent table creation",
            "mixins tested in isolation before integration with concrete models",
            "mixin fields use consistent naming conventions across all models",
            "documentation in docstring lists all fields and methods provided",
        ],
    }
    logger.debug(
        "Core mixins directory config: mixins_purpose=%d, planned_mixins=%d",
        len(config["mixins_purpose"]),
        len(config["planned_mixins"]),
    )
    return config


def get_core_exceptions_config() -> dict:
    """Return core exceptions.py configuration.

    Documents the core exceptions module, including common error
    types, exception hierarchy, and usage conventions for
    consistent error handling across all applications.

    SubPhase-01, Group-B, Task 19.

    Returns:
        dict: Configuration with *exceptions_documented* flag,
              *exception_types* list, *exception_hierarchy* list,
              and *usage_conventions* list.
    """
    config: dict = {
        "exceptions_documented": True,
        "exception_types": [
            "ApplicationError as base exception for all custom project errors",
            "ValidationError for business rule violations distinct from DRF errors",
            "NotFoundError for entity lookup failures with descriptive messages",
            "PermissionDeniedError for access control violations beyond HTTP 403",
            "ConflictError for concurrent modification and uniqueness violations",
            "ServiceUnavailableError for external dependency failures and timeouts",
        ],
        "exception_hierarchy": [
            "ApplicationError inherits from Python Exception as project root",
            "ValidationError extends ApplicationError with field-level error details",
            "NotFoundError extends ApplicationError with entity type and identifier",
            "PermissionDeniedError extends ApplicationError with required permission",
            "ConflictError extends ApplicationError with conflicting resource details",
            "all custom exceptions map to specific HTTP status codes via handler",
        ],
        "usage_conventions": [
            "raise custom exceptions in service layer not in views or serializers",
            "exception handler in DRF converts custom exceptions to JSON responses",
            "error messages use human-readable strings suitable for API consumers",
            "exception logging done at the handler level not at raise site",
            "tenant context included in exception metadata for debugging",
            "all exceptions serializable to JSON for structured error responses",
        ],
    }
    logger.debug(
        "Core exceptions config: exception_types=%d, exception_hierarchy=%d",
        len(config["exception_types"]),
        len(config["exception_hierarchy"]),
    )
    return config


def get_core_constants_config() -> dict:
    """Return core constants.py configuration.

    Documents the core constants module, including its purpose
    for housing shared constant values, enumerations, and
    configuration literals used across all applications.

    SubPhase-01, Group-B, Task 20.

    Returns:
        dict: Configuration with *constants_documented* flag,
              *constant_categories* list, *naming_conventions* list,
              and *usage_guidelines* list.
    """
    config: dict = {
        "constants_documented": True,
        "constant_categories": [
            "status constants defining lifecycle states like ACTIVE, INACTIVE, PENDING",
            "pagination defaults for page size, max page size, and ordering fields",
            "date format strings for API serialization and display formatting",
            "cache timeout values for different cache key categories in seconds",
            "file upload limits for maximum file size and allowed MIME types",
            "currency and locale constants for Sri Lankan localization defaults",
        ],
        "naming_conventions": [
            "constant names use UPPER_SNAKE_CASE following Python convention",
            "related constants grouped into frozen dataclass or IntegerChoices classes",
            "module-level constants defined at top of file after imports",
            "documentation comment above each constant group explains its purpose",
            "constant values are immutable and never modified at runtime",
            "type annotations added to all constants for IDE support and clarity",
        ],
        "usage_guidelines": [
            "import constants directly rather than using magic numbers in code",
            "prefer TextChoices and IntegerChoices for model field choices",
            "constants shared across apps defined in core, app-specific in own module",
            "environment-dependent values loaded from settings not from constants",
            "constants file kept focused and free of business logic or classes",
            "deprecated constants marked with comments noting removal timeline",
        ],
    }
    logger.debug(
        "Core constants config: constant_categories=%d, naming_conventions=%d",
        len(config["constant_categories"]),
        len(config["naming_conventions"]),
    )
    return config


def get_core_tests_directory_config() -> dict:
    """Return core tests/ directory configuration.

    Documents the core application tests directory structure,
    including test file organization, __init__.py setup, and
    conventions for test module placement and naming.

    SubPhase-01, Group-B, Task 21.

    Returns:
        dict: Configuration with *tests_documented* flag,
              *directory_structure* list, *test_scope* list,
              and *test_conventions* list.
    """
    config: dict = {
        "tests_documented": True,
        "directory_structure": [
            "tests directory at backend/tests/core/ for core app test modules",
            "__init__.py marks directory as a Python test package for pytest",
            "conftest.py contains fixtures shared across all core test modules",
            "test files named test_<module>.py matching source module being tested",
            "subdirectories allowed for grouping tests by feature or domain",
            "factory files placed alongside tests for test data generation",
        ],
        "test_scope": [
            "unit tests for utility functions in apps/core/utils/ modules",
            "unit tests for model methods and manager querysets on core models",
            "unit tests for mixin behavior when applied to test model classes",
            "unit tests for custom exception serialization and error messages",
            "integration tests for view endpoints under /api/v1/core/ routes",
            "integration tests for signal handlers and management commands",
        ],
        "test_conventions": [
            "test classes named Test<ClassName> with descriptive method names",
            "each test method tests one behavior with clear arrange-act-assert",
            "fixtures preferred over setUp/tearDown for test data preparation",
            "factory_boy factories used for complex model instance creation",
            "pytest markers applied for slow, integration, and tenant tests",
            "test coverage for core modules maintained above 90 percent",
        ],
    }
    logger.debug(
        "Core tests directory config: directory_structure=%d, test_scope=%d",
        len(config["directory_structure"]),
        len(config["test_scope"]),
    )
    return config


def get_core_registration_config() -> dict:
    """Return core INSTALLED_APPS registration configuration.

    Documents the core app registration in Django INSTALLED_APPS,
    including placement order, dependency considerations, and
    settings file location for the registration entry.

    SubPhase-01, Group-B, Task 22.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *placement_order* list,
              and *dependency_notes* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "core app registered as apps.core in INSTALLED_APPS setting",
            "registration entry placed in LOCAL_APPS section of base settings",
            "AppConfig path apps.core.apps.CoreConfig used for explicit config",
            "registration enables admin autodiscovery and migration detection",
            "core app must be registered before any app that depends on it",
            "settings file located at backend/config/settings/base.py",
        ],
        "placement_order": [
            "Django built-in apps listed first: auth, contenttypes, sessions",
            "third-party apps listed second: rest_framework, django_tenants",
            "core app listed first among LOCAL_APPS as foundation dependency",
            "tenants app listed after core for multi-tenant infrastructure",
            "feature apps like products, orders, users listed after tenants",
            "webstore and integration apps listed last as highest-level modules",
        ],
        "dependency_notes": [
            "core has no dependencies on other LOCAL_APPS by design",
            "all other LOCAL_APPS may depend on core for base models and mixins",
            "tenants app depends on core for TenantAwareModel base class",
            "changing core app label requires updating all foreign key references",
            "removing core from INSTALLED_APPS breaks all dependent applications",
            "core migrations must run before any app that references core models",
        ],
    }
    logger.debug(
        "Core registration config: registration_details=%d, placement_order=%d",
        len(config["registration_details"]),
        len(config["placement_order"]),
    )
    return config


def get_tenants_app_directory_config() -> dict:
    """Return tenants app directory configuration.

    Documents the tenants application directory structure, including
    its purpose as the home for multi-tenant models, schema management
    utilities, and tenant lifecycle functionality.

    SubPhase-01, Group-C, Task 23.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_purpose* list, *directory_contents* list,
              and *tenant_scope* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_purpose": [
            "tenants app located at backend/apps/tenants/ for multi-tenancy support",
            "houses tenant and domain models defined in Phase 02 database architecture",
            "provides schema management utilities for tenant provisioning and teardown",
            "contains tenant-aware middleware and context processors",
            "serves as the integration point for django-tenants library customizations",
            "holds tenant lifecycle management including creation and suspension",
        ],
        "directory_contents": [
            "__init__.py marks tenants as a Python package with app docstring",
            "apps.py contains TenantsConfig with metadata and ready() hook",
            "models.py holds Tenant and Domain models from Phase 02 schema",
            "admin.py registers tenant models with the Django admin interface",
            "urls.py defines tenant management endpoints under /api/v1/tenants/",
            "utils/ subdirectory contains testing, migration, and schema utilities",
        ],
        "tenant_scope": [
            "tenant model defines schema_name, name, and lifecycle status fields",
            "domain model links tenant to hostname for automatic schema routing",
            "public schema holds shared data accessible across all tenants",
            "tenant schemas isolate per-tenant data using PostgreSQL schemas",
            "tenant provisioning creates schema and runs migrations automatically",
            "tenant suspension disables access without destroying schema data",
        ],
    }
    logger.debug(
        "Tenants app directory config: directory_purpose=%d, directory_contents=%d",
        len(config["directory_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_tenants_init_config() -> dict:
    """Return tenants __init__.py configuration.

    Documents the tenants application package initialization, including
    module discovery, default app configuration, and package-level
    conventions for the tenants app.

    SubPhase-01, Group-C, Task 24.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_contents* list, *discovery_behavior* list,
              and *init_conventions* list.
    """
    config: dict = {
        "init_documented": True,
        "init_contents": [
            "module docstring describing tenants app purpose and responsibilities",
            "default_app_config set to apps.tenants.apps.TenantsConfig if needed",
            "package-level imports kept minimal to avoid circular dependencies",
            "no heavy model imports at package level for safe import ordering",
            "TYPE_CHECKING guard used for type annotation imports only",
            "package provides apps.tenants namespace for all tenant functionality",
        ],
        "discovery_behavior": [
            "Django autodiscover_modules finds admin registrations in tenants app",
            "pytest discovers test modules via apps.tenants package namespace",
            "migration runner resolves tenants app label for schema operations",
            "management command discovery uses apps.tenants.management.commands path",
            "django-tenants uses package to locate TenantModel and DomainModel",
            "signal handlers connected during TenantsConfig.ready() call",
        ],
        "init_conventions": [
            "keep __init__.py lightweight with docstring and minimal setup",
            "avoid importing models at package level to prevent AppRegistryNotReady",
            "utility re-exports handled by apps.tenants.utils sub-package init",
            "constants and enumerations may be defined at package level if simple",
            "any public API documented in __all__ list for explicit surface area",
            "version or metadata constants omitted in favor of central versioning",
        ],
    }
    logger.debug(
        "Tenants init config: init_contents=%d, discovery_behavior=%d",
        len(config["init_contents"]),
        len(config["discovery_behavior"]),
    )
    return config


def get_tenants_apps_config() -> dict:
    """Return tenants apps.py configuration.

    Documents the TenantsConfig AppConfig subclass, including the
    app name, label, verbose name, and the ready() method for
    signal registration and tenant-specific startup tasks.

    SubPhase-01, Group-C, Task 25.

    Returns:
        dict: Configuration with *config_documented* flag,
              *config_attributes* list, *ready_hook_tasks* list,
              and *config_conventions* list.
    """
    config: dict = {
        "config_documented": True,
        "config_attributes": [
            "name set to apps.tenants matching the full dotted Python path",
            "label set to tenants for database table prefix and migration references",
            "verbose_name set to Tenants for human-readable admin display",
            "default_auto_field set to django.db.models.BigAutoField for primary keys",
            "AppConfig subclass named TenantsConfig following Django convention",
            "module docstring documents tenant lifecycle and schema management scope",
        ],
        "ready_hook_tasks": [
            "import and connect tenant creation signal for automatic provisioning",
            "import and connect tenant deletion signal for schema cleanup",
            "register system checks for tenant configuration validation",
            "log tenants app startup confirmation at info level",
            "validate django-tenants required settings on application readiness",
            "initialize tenant schema cache for faster schema lookups",
        ],
        "config_conventions": [
            "one AppConfig class per apps.py following Django best practice",
            "ready() imports signals module to avoid circular import issues",
            "system checks tagged with tenants for selective check execution",
            "verbose_name uses singular Tenants matching the app directory name",
            "app label matches directory name for consistent ORM table prefixing",
            "no database queries executed during ready() to prevent migration issues",
        ],
    }
    logger.debug(
        "Tenants apps config: config_attributes=%d, ready_hook_tasks=%d",
        len(config["config_attributes"]),
        len(config["ready_hook_tasks"]),
    )
    return config


def get_tenants_models_config() -> dict:
    """Return tenants models.py configuration.

    Documents the tenants models placeholder, referencing the
    Tenant and Domain models established in Phase 02 database
    architecture as the source of truth for tenant data.

    SubPhase-01, Group-C, Task 26.

    Returns:
        dict: Configuration with *models_documented* flag,
              *placeholder_details* list, *phase02_references* list,
              and *model_conventions* list.
    """
    config: dict = {
        "models_documented": True,
        "placeholder_details": [
            "models.py in tenants app references Phase 02 tenant and domain models",
            "Tenant model inherits from django_tenants TenantMixin base class",
            "Domain model inherits from django_tenants DomainMixin base class",
            "models defined during Phase 02 SubPhase 03 schema definition tasks",
            "placeholder ensures tenants app is recognized by migration framework",
            "future model additions extend the tenant lifecycle with status fields",
        ],
        "phase02_references": [
            "TenantMixin provides schema_name field for PostgreSQL schema routing",
            "DomainMixin provides domain and is_primary fields for hostname mapping",
            "Phase 02 migrations created public schema tables for tenant metadata",
            "django-tenants middleware uses these models for request schema routing",
            "admin interface registers these models for tenant management operations",
            "test factories for Tenant and Domain defined in Phase 02 test utilities",
        ],
        "model_conventions": [
            "tenant model string representation returns tenant name for readability",
            "domain model string representation returns the fully qualified domain",
            "Meta class sets ordering by name and verbose_name for admin display",
            "custom manager filters active tenants by default in queryset methods",
            "cascade deletion rules documented for tenant-domain relationship",
            "schema_name validated for PostgreSQL identifier compliance on save",
        ],
    }
    logger.debug(
        "Tenants models config: placeholder_details=%d, phase02_references=%d",
        len(config["placeholder_details"]),
        len(config["phase02_references"]),
    )
    return config


def get_tenants_admin_config() -> dict:
    """Return tenants admin.py configuration.

    Documents the tenants admin placeholder, including planned
    registrations for Tenant and Domain models and admin
    conventions for multi-tenant management interfaces.

    SubPhase-01, Group-C, Task 27.

    Returns:
        dict: Configuration with *admin_documented* flag,
              *admin_registrations* list, *admin_features* list,
              and *admin_conventions* list.
    """
    config: dict = {
        "admin_documented": True,
        "admin_registrations": [
            "TenantAdmin registers Tenant model with list and detail views",
            "DomainAdmin registers Domain model with inline editing support",
            "DomainInline allows managing domains directly from tenant detail page",
            "admin placeholder created now with registrations added in later phase",
            "tenant admin restricted to superuser access for security by default",
            "admin autodiscovery includes tenants app when registered in settings",
        ],
        "admin_features": [
            "list_display shows tenant name, schema_name, created_at, and status",
            "list_filter includes is_active and creation date range filtering",
            "search_fields configured for tenant name and schema_name lookups",
            "readonly_fields includes schema_name after initial creation to prevent changes",
            "actions include activate, deactivate, and export tenant list options",
            "domain inline shows all associated domains with primary flag indicator",
        ],
        "admin_conventions": [
            "dedicated ModelAdmin subclass for each model not decorator-only",
            "fieldsets group tenant details, schema info, and timestamps logically",
            "custom admin actions use confirmation pages for destructive operations",
            "admin permissions checked with has_module_permission for access control",
            "admin site title customized to LankaCommerce Cloud Tenant Management",
            "tenant creation through admin triggers same signal as API creation",
        ],
    }
    logger.debug(
        "Tenants admin config: admin_registrations=%d, admin_features=%d",
        len(config["admin_registrations"]),
        len(config["admin_features"]),
    )
    return config


def get_tenants_urls_config() -> dict:
    """Return tenants urls.py configuration.

    Documents the tenants URL placeholder, including namespace
    setup, API versioning alignment, and planned endpoint patterns
    for tenant management operations.

    SubPhase-01, Group-C, Task 28.

    Returns:
        dict: Configuration with *urls_documented* flag,
              *url_structure* list, *planned_endpoints* list,
              and *url_conventions* list.
    """
    config: dict = {
        "urls_documented": True,
        "url_structure": [
            "app_name variable set to tenants for URL namespace resolution",
            "urlpatterns list initialized empty as placeholder for future routes",
            "tenants URLs included in project urls.py under api/v1/tenants/ prefix",
            "tenant management endpoints planned for CRUD operations on tenants",
            "domain management endpoints planned under tenant detail routes",
            "tenant health and status endpoints planned for monitoring dashboards",
        ],
        "planned_endpoints": [
            "GET /api/v1/tenants/ to list all tenants with pagination and filtering",
            "POST /api/v1/tenants/ to create a new tenant with schema provisioning",
            "GET /api/v1/tenants/<id>/ to retrieve tenant details and domain info",
            "PATCH /api/v1/tenants/<id>/ to update tenant metadata and status",
            "DELETE /api/v1/tenants/<id>/ to deactivate or remove a tenant",
            "GET /api/v1/tenants/<id>/domains/ to list domains for a tenant",
        ],
        "url_conventions": [
            "URL patterns use path() with named routes for reverse resolution",
            "view names use lowercase-hyphenated format like tenant-list, tenant-detail",
            "tenant endpoints require superuser or tenant-admin permissions",
            "list endpoints support ordering by name, created_at, and status fields",
            "detail endpoints use UUID lookup field not integer primary key",
            "nested domain routes follow RESTful parent-child URL conventions",
        ],
    }
    logger.debug(
        "Tenants urls config: url_structure=%d, planned_endpoints=%d",
        len(config["url_structure"]),
        len(config["planned_endpoints"]),
    )
    return config


def get_tenants_registration_config() -> dict:
    """Return tenants registration configuration.

    Documents the tenants app registration in Django settings,
    including placement in SHARED_APPS for public schema access,
    ordering requirements, and django-tenants specific settings.

    SubPhase-01, Group-C, Task 29.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *shared_apps_placement* list,
              and *django_tenants_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "tenants app registered as apps.tenants in SHARED_APPS setting",
            "registration ensures tenant models live in the public PostgreSQL schema",
            "AppConfig path apps.tenants.apps.TenantsConfig used for explicit config",
            "tenants app listed after core and before feature apps in ordering",
            "settings file located at backend/config/settings/base.py",
            "tenants also listed in TENANT_APPS if tenant-specific tables needed",
        ],
        "shared_apps_placement": [
            "SHARED_APPS contains apps whose tables exist in the public schema only",
            "django_tenants and tenants app are first entries in SHARED_APPS",
            "auth and contenttypes included in SHARED_APPS for user management",
            "admin app included in SHARED_APPS for centralized admin access",
            "SHARED_APPS ordering must match INSTALLED_APPS for consistency",
            "adding an app to SHARED_APPS requires running migrate_schemas --shared",
        ],
        "django_tenants_settings": [
            "TENANT_MODEL set to tenants.Tenant pointing to the Tenant model",
            "TENANT_DOMAIN_MODEL set to tenants.Domain pointing to the Domain model",
            "DATABASE_ROUTERS includes django_tenants router for schema routing",
            "MIDDLEWARE includes TenantMainMiddleware for request schema detection",
            "PUBLIC_SCHEMA_NAME set to public as the default shared schema",
            "DEFAULT_FILE_STORAGE configured for tenant-aware file storage paths",
        ],
    }
    logger.debug(
        "Tenants registration config: registration_details=%d, shared_apps_placement=%d",
        len(config["registration_details"]),
        len(config["shared_apps_placement"]),
    )
    return config


def get_users_app_directory_config() -> dict:
    """Return users app directory configuration.

    Documents the users application directory structure, including
    its purpose as the home for the custom user model, authentication
    helpers, and user profile functionality.

    SubPhase-01, Group-C, Task 30.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_purpose* list, *directory_contents* list,
              and *user_model_scope* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_purpose": [
            "users app located at backend/apps/users/ for user management",
            "houses the custom user model extending Django AbstractUser",
            "provides authentication and authorization helper utilities",
            "contains user profile models and related personal data storage",
            "serves as the integration point for JWT and session authentication",
            "holds user-related signals for profile creation and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks users as a Python package with app docstring",
            "apps.py contains UsersConfig with metadata and ready() hook",
            "models.py holds custom User model extending AbstractUser",
            "admin.py registers user models with custom UserAdmin class",
            "urls.py defines user management endpoints under /api/v1/users/",
            "managers.py contains custom UserManager for email-based queries",
        ],
        "user_model_scope": [
            "custom User model replaces default Django User via AUTH_USER_MODEL",
            "user model includes email as the primary identifier field",
            "tenant association handled via schema routing not foreign key",
            "profile fields like phone, avatar, and bio added to user model",
            "role-based access control fields planned for permission management",
            "soft delete support via is_active flag and deactivation timestamp",
        ],
    }
    logger.debug(
        "Users app directory config: directory_purpose=%d, directory_contents=%d",
        len(config["directory_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_users_init_config() -> dict:
    """Return users __init__.py configuration.

    Documents the users application package initialization, including
    module discovery, default app configuration, and package-level
    conventions for the users app.

    SubPhase-01, Group-C, Task 31.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_contents* list, *discovery_behavior* list,
              and *init_conventions* list.
    """
    config: dict = {
        "init_documented": True,
        "init_contents": [
            "module docstring describing users app purpose and responsibilities",
            "default_app_config set to apps.users.apps.UsersConfig if needed",
            "package-level imports kept minimal to avoid circular dependencies",
            "no model imports at package level for safe Django app loading order",
            "TYPE_CHECKING guard used for type annotation convenience imports",
            "package provides apps.users namespace for all user functionality",
        ],
        "discovery_behavior": [
            "Django autodiscover_modules finds admin registrations in users app",
            "pytest discovers test modules via apps.users package namespace",
            "migration runner resolves users app label for schema operations",
            "management command discovery uses apps.users.management.commands path",
            "AUTH_USER_MODEL setting points Django to this package for user model",
            "signal handlers connected during UsersConfig.ready() method call",
        ],
        "init_conventions": [
            "keep __init__.py lightweight with docstring and minimal code",
            "avoid importing User model at package level to prevent AppRegistryNotReady",
            "utility functions re-exported via apps.users.utils sub-package if needed",
            "authentication helpers exposed through dedicated auth module",
            "any public API documented in __all__ list for explicit surface",
            "version metadata omitted in favor of centralized project versioning",
        ],
    }
    logger.debug(
        "Users init config: init_contents=%d, discovery_behavior=%d",
        len(config["init_contents"]),
        len(config["discovery_behavior"]),
    )
    return config


def get_users_apps_config() -> dict:
    """Return users apps.py configuration.

    Documents the UsersConfig AppConfig subclass, including the
    app name, label, verbose name, and the ready() method for
    signal registration and user-specific startup tasks.

    SubPhase-01, Group-C, Task 32.

    Returns:
        dict: Configuration with *config_documented* flag,
              *config_attributes* list, *ready_hook_tasks* list,
              and *config_conventions* list.
    """
    config: dict = {
        "config_documented": True,
        "config_attributes": [
            "name set to apps.users matching the full dotted Python path",
            "label set to users for database table prefix and migration references",
            "verbose_name set to Users for human-readable admin display",
            "default_auto_field set to django.db.models.BigAutoField for primary keys",
            "AppConfig subclass named UsersConfig following Django naming convention",
            "module docstring documents user management and authentication scope",
        ],
        "ready_hook_tasks": [
            "import and connect user post_save signal for profile auto-creation",
            "import and connect user login signal for session audit logging",
            "register system checks for AUTH_USER_MODEL configuration validation",
            "log users app startup confirmation at info level",
            "validate that AUTH_USER_MODEL points to users.User on readiness",
            "connect password change signal for security notification dispatch",
        ],
        "config_conventions": [
            "one AppConfig class per apps.py following Django best practice",
            "ready() imports signals module to avoid circular import issues",
            "system checks tagged with users for selective check execution",
            "verbose_name uses plural Users matching the app directory name",
            "app label matches directory name for consistent ORM table prefixing",
            "no database queries executed during ready() to prevent migration issues",
        ],
    }
    logger.debug(
        "Users apps config: config_attributes=%d, ready_hook_tasks=%d",
        len(config["config_attributes"]),
        len(config["ready_hook_tasks"]),
    )
    return config


def get_users_models_config() -> dict:
    """Return users models.py configuration.

    Documents the custom user model placeholder based on Django
    AbstractUser, including planned fields, manager setup, and
    extension points for future authentication features.

    SubPhase-01, Group-C, Task 33.

    Returns:
        dict: Configuration with *models_documented* flag,
              *placeholder_details* list, *custom_user_features* list,
              and *model_conventions* list.
    """
    config: dict = {
        "models_documented": True,
        "placeholder_details": [
            "User model inherits from Django AbstractUser as custom user class",
            "placeholder created now with full implementation in later subphases",
            "AUTH_USER_MODEL setting points to users.User for project-wide usage",
            "custom UserManager overrides create_user and create_superuser methods",
            "email field set as unique and used as primary authentication identifier",
            "initial migration created early to avoid AUTH_USER_MODEL swap issues",
        ],
        "custom_user_features": [
            "email-based authentication replacing default username-based login",
            "phone number field for optional SMS-based verification support",
            "avatar field using ImageField with tenant-aware upload path",
            "date_of_birth field for age verification requirements",
            "preferred_language field for internationalization preferences",
            "is_verified flag for email or phone verification status tracking",
        ],
        "model_conventions": [
            "User model inherits TimeStampedModel for created_at and updated_at",
            "string representation returns user full name or email as fallback",
            "Meta class sets ordering by date_joined and verbose_name to User",
            "USERNAME_FIELD set to email for authentication identifier override",
            "REQUIRED_FIELDS includes first_name and last_name for createsuperuser",
            "custom manager handles email normalization and validation on creation",
        ],
    }
    logger.debug(
        "Users models config: placeholder_details=%d, custom_user_features=%d",
        len(config["placeholder_details"]),
        len(config["custom_user_features"]),
    )
    return config


def get_users_admin_config() -> dict:
    """Return users admin.py configuration.

    Documents the users admin placeholder, including planned
    registrations for the custom User model and admin class
    conventions for user management interfaces.

    SubPhase-01, Group-C, Task 34.

    Returns:
        dict: Configuration with *admin_documented* flag,
              *admin_registrations* list, *admin_features* list,
              and *admin_conventions* list.
    """
    config: dict = {
        "admin_documented": True,
        "admin_registrations": [
            "CustomUserAdmin registers User model extending UserAdmin base class",
            "admin placeholder created now with full registration in later phase",
            "UserAdmin inherits from django.contrib.auth.admin.UserAdmin",
            "custom fieldsets replace default to include email-based fields",
            "add_fieldsets configured for email-based user creation form",
            "admin autodiscovery includes users app when registered in settings",
        ],
        "admin_features": [
            "list_display shows email, full name, is_active, and date_joined",
            "list_filter includes is_active, is_staff, is_verified, and groups",
            "search_fields configured for email, first_name, and last_name",
            "ordering set to email for consistent list view presentation",
            "readonly_fields includes date_joined and last_login timestamps",
            "actions include activate, deactivate, and send verification email",
        ],
        "admin_conventions": [
            "custom UserAdmin class inherits from contrib auth UserAdmin base",
            "fieldsets organized into personal info, permissions, and dates groups",
            "password change handled through dedicated admin password change view",
            "inline profile admin attached if separate UserProfile model exists",
            "custom admin form validates email uniqueness across the tenant schema",
            "admin site header customized to LankaCommerce Cloud User Management",
        ],
    }
    logger.debug(
        "Users admin config: admin_registrations=%d, admin_features=%d",
        len(config["admin_registrations"]),
        len(config["admin_features"]),
    )
    return config


def get_users_urls_config() -> dict:
    """Return users urls.py configuration.

    Documents the users URL placeholder, including namespace setup,
    API versioning alignment, and planned endpoint patterns for
    user management and authentication operations.

    SubPhase-01, Group-C, Task 35.

    Returns:
        dict: Configuration with *urls_documented* flag,
              *url_structure* list, *planned_endpoints* list,
              and *url_conventions* list.
    """
    config: dict = {
        "urls_documented": True,
        "url_structure": [
            "app_name variable set to users for URL namespace resolution",
            "urlpatterns list initialized empty as placeholder for future routes",
            "users URLs included in project urls.py under api/v1/users/ prefix",
            "authentication endpoints planned for login, logout, and token refresh",
            "registration endpoint planned for self-service user account creation",
            "profile management endpoints planned for user data updates",
        ],
        "planned_endpoints": [
            "POST /api/v1/users/register/ for new user account registration",
            "POST /api/v1/users/login/ for email and password authentication",
            "POST /api/v1/users/logout/ for session and token invalidation",
            "GET /api/v1/users/me/ to retrieve current authenticated user profile",
            "PATCH /api/v1/users/me/ to update current user profile information",
            "POST /api/v1/users/password/change/ for authenticated password update",
        ],
        "url_conventions": [
            "URL patterns use path() with named routes for reverse resolution",
            "view names use lowercase-hyphenated format like user-register, user-login",
            "authentication endpoints public, profile endpoints require JWT token",
            "list endpoints support pagination and search by name or email fields",
            "detail endpoints use UUID lookup field not integer primary key",
            "rate limiting applied to authentication endpoints to prevent brute force",
        ],
    }
    logger.debug(
        "Users urls config: url_structure=%d, planned_endpoints=%d",
        len(config["url_structure"]),
        len(config["planned_endpoints"]),
    )
    return config


def get_users_registration_config() -> dict:
    """Return users registration configuration.

    Documents the users app registration in Django settings,
    including placement in TENANT_APPS for per-tenant user data,
    AUTH_USER_MODEL setting, and authentication backend configuration.

    SubPhase-01, Group-C, Task 36.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *auth_user_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "users app registered as apps.users in TENANT_APPS setting",
            "registration ensures user tables created in each tenant schema",
            "AppConfig path apps.users.apps.UsersConfig used for explicit config",
            "users app listed after tenants and before feature apps in ordering",
            "settings file located at backend/config/settings/base.py",
            "users also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "users app placed in TENANT_APPS for per-tenant user isolation",
            "each tenant schema gets its own users table for data separation",
            "shared user data like superadmins handled via public schema flag",
            "TENANT_APPS ordering places users before content apps that reference it",
            "adding users to TENANT_APPS requires running migrate_schemas for tenants",
        ],
        "auth_user_settings": [
            "AUTH_USER_MODEL set to users.User pointing to the custom user model",
            "AUTH_USER_MODEL must be set before running any migrations",
            "AUTHENTICATION_BACKENDS includes ModelBackend for email-based auth",
            "SESSION_ENGINE configured for tenant-aware session storage",
            "LOGIN_URL and LOGIN_REDIRECT_URL set for admin interface access",
            "PASSWORD_HASHERS configured with Argon2 as the preferred algorithm",
        ],
    }
    logger.debug(
        "Users registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_products_app_directory_config() -> dict:
    """Return products app directory configuration.

    Documents the products application directory structure, including
    its purpose as the home for product catalog, categories, variants,
    and pricing functionality within the multi-tenant POS system.

    SubPhase-01, Group-D, Task 37.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_purpose* list, *directory_contents* list,
              and *catalog_scope* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_purpose": [
            "products app located at backend/apps/products/ for catalog management",
            "houses product models including Product, Category, and Variant",
            "provides product catalog browsing and search functionality",
            "contains pricing logic for base prices and variant-level overrides",
            "serves as the integration point for inventory and order modules",
            "holds product-related signals for stock updates and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks products as a Python package with app docstring",
            "apps.py contains ProductsConfig with metadata and ready() hook",
            "models.py holds Product, Category, and Variant model definitions",
            "admin.py registers product models with custom admin classes",
            "urls.py defines product endpoints under /api/v1/products/",
            "serializers.py contains DRF serializers for product API responses",
        ],
        "catalog_scope": [
            "hierarchical category tree supporting unlimited nesting depth",
            "product model includes SKU, name, description, and base price fields",
            "variant model supports attributes like size, color, and weight",
            "product images managed via ImageField with tenant-aware upload paths",
            "barcode field supports EAN-13 and UPC-A formats for POS scanning",
            "soft delete support via is_active flag and deactivation timestamp",
        ],
    }
    logger.debug(
        "Products app directory config: directory_purpose=%d, directory_contents=%d",
        len(config["directory_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_products_init_config() -> dict:
    """Return products __init__.py configuration.

    Documents the products application package initialization, including
    module discovery, default app configuration, and package-level
    conventions for the products app.

    SubPhase-01, Group-D, Task 38.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_contents* list, *discovery_behavior* list,
              and *init_conventions* list.
    """
    config: dict = {
        "init_documented": True,
        "init_contents": [
            "module docstring describing products app purpose and responsibilities",
            "default_app_config set to apps.products.apps.ProductsConfig if needed",
            "package-level imports kept minimal to avoid circular dependencies",
            "no model imports at package level for safe Django app loading order",
            "TYPE_CHECKING guard used for type annotation convenience imports",
            "package provides apps.products namespace for all catalog functionality",
        ],
        "discovery_behavior": [
            "Django autodiscover_modules finds admin registrations in products app",
            "pytest discovers test modules via apps.products package namespace",
            "migration runner resolves products app label for schema operations",
            "management command discovery uses apps.products.management.commands path",
            "DRF router autodiscovery registers product viewsets from products app",
            "signal handlers connected during ProductsConfig.ready() method call",
        ],
        "init_conventions": [
            "keep __init__.py lightweight with docstring and minimal code",
            "avoid importing models at package level to prevent AppRegistryNotReady",
            "utility functions re-exported via apps.products.utils sub-package",
            "catalog helpers exposed through dedicated catalog service module",
            "any public API documented in __all__ list for explicit surface",
            "version metadata omitted in favor of centralized project versioning",
        ],
    }
    logger.debug(
        "Products init config: init_contents=%d, discovery_behavior=%d",
        len(config["init_contents"]),
        len(config["discovery_behavior"]),
    )
    return config


def get_products_apps_config() -> dict:
    """Return products apps.py configuration.

    Documents the ProductsConfig AppConfig subclass, including the
    app name, label, verbose name, and the ready() method for
    signal registration and product-specific startup tasks.

    SubPhase-01, Group-D, Task 39.

    Returns:
        dict: Configuration with *config_documented* flag,
              *config_attributes* list, *ready_hook_tasks* list,
              and *config_conventions* list.
    """
    config: dict = {
        "config_documented": True,
        "config_attributes": [
            "name set to apps.products matching the full dotted Python path",
            "label set to products for database table prefix and migration references",
            "verbose_name set to Products for human-readable admin display",
            "default_auto_field set to django.db.models.BigAutoField for primary keys",
            "AppConfig subclass named ProductsConfig following Django naming convention",
            "module docstring documents product catalog and category management scope",
        ],
        "ready_hook_tasks": [
            "import and connect product post_save signal for inventory sync",
            "import and connect category change signal for cache invalidation",
            "register system checks for product model field validation rules",
            "log products app startup confirmation at info level",
            "validate that product SKU uniqueness constraint is properly configured",
            "connect variant price change signal for order recalculation dispatch",
        ],
        "config_conventions": [
            "one AppConfig class per apps.py following Django best practice",
            "ready() imports signals module to avoid circular import issues",
            "system checks tagged with products for selective check execution",
            "verbose_name uses plural Products matching the app directory name",
            "app label matches directory name for consistent ORM table prefixing",
            "no database queries executed during ready() to prevent migration issues",
        ],
    }
    logger.debug(
        "Products apps config: config_attributes=%d, ready_hook_tasks=%d",
        len(config["config_attributes"]),
        len(config["ready_hook_tasks"]),
    )
    return config


def get_products_models_config() -> dict:
    """Return products models.py configuration.

    Documents the products models placeholder including Product,
    Category, and Variant model definitions planned for full
    implementation in Phase-04 ERP Core Modules.

    SubPhase-01, Group-D, Task 40.

    Returns:
        dict: Configuration with *models_documented* flag,
              *placeholder_details* list, *planned_models* list,
              and *model_conventions* list.
    """
    config: dict = {
        "models_documented": True,
        "placeholder_details": [
            "Product model placeholder with SKU, name, and base price fields",
            "Category model placeholder with hierarchical tree structure support",
            "Variant model placeholder with attribute-based product variations",
            "placeholder created now with full implementation in Phase-04 subphases",
            "initial migration created early to establish table structure in schemas",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
        ],
        "planned_models": [
            "Product model with SKU, barcode, name, description, and pricing fields",
            "Category model with MPTT or django-treebeard for nested categories",
            "Variant model linking to Product with size, color, and weight attributes",
            "ProductImage model for multiple product images with ordering support",
            "PriceHistory model tracking product price changes over time",
            "ProductTag model for flexible tagging and filtering capabilities",
        ],
        "model_conventions": [
            "all models inherit from core TimeStampedModel for audit timestamps",
            "string representation returns product name or SKU as identifier",
            "Meta class sets ordering by name and verbose_name for admin display",
            "UUIDField used as public-facing identifier instead of integer primary key",
            "soft delete support via is_active flag for catalog archive functionality",
            "custom managers provide active-only and category-filtered querysets",
        ],
    }
    logger.debug(
        "Products models config: placeholder_details=%d, planned_models=%d",
        len(config["placeholder_details"]),
        len(config["planned_models"]),
    )
    return config


def get_products_admin_config() -> dict:
    """Return products admin.py configuration.

    Documents the products admin placeholder, including planned
    registrations for Product, Category, and Variant models and
    admin class conventions for catalog management interfaces.

    SubPhase-01, Group-D, Task 41.

    Returns:
        dict: Configuration with *admin_documented* flag,
              *admin_registrations* list, *admin_features* list,
              and *admin_conventions* list.
    """
    config: dict = {
        "admin_documented": True,
        "admin_registrations": [
            "ProductAdmin registers Product model with custom list and filter views",
            "CategoryAdmin registers Category model with tree display support",
            "VariantAdmin registers Variant model as inline on ProductAdmin",
            "admin placeholder created now with full registration in later phase",
            "admin autodiscovery includes products app when registered in settings",
            "VariantInline provides tabular inline editing on product detail page",
        ],
        "admin_features": [
            "list_display shows SKU, product name, category, price, and is_active",
            "list_filter includes category, is_active, created_at, and price range",
            "search_fields configured for SKU, product name, and barcode values",
            "ordering set to name for consistent alphabetical list presentation",
            "readonly_fields includes created_at, updated_at, and SKU if auto-generated",
            "actions include activate, deactivate, and bulk category reassignment",
        ],
        "admin_conventions": [
            "each model gets a dedicated ModelAdmin class for customization",
            "fieldsets organized into basic info, pricing, inventory, and metadata",
            "inline admin classes used for variant editing within product forms",
            "custom admin form validates SKU uniqueness within the tenant schema",
            "list_per_page set to 25 for optimal performance with large catalogs",
            "admin site header customized to LankaCommerce Cloud Product Management",
        ],
    }
    logger.debug(
        "Products admin config: admin_registrations=%d, admin_features=%d",
        len(config["admin_registrations"]),
        len(config["admin_features"]),
    )
    return config


def get_products_urls_config() -> dict:
    """Return products urls.py configuration.

    Documents the products URL placeholder, including namespace setup,
    API versioning alignment, and planned endpoint patterns for
    product catalog and category management operations.

    SubPhase-01, Group-D, Task 42.

    Returns:
        dict: Configuration with *urls_documented* flag,
              *url_structure* list, *planned_endpoints* list,
              and *url_conventions* list.
    """
    config: dict = {
        "urls_documented": True,
        "url_structure": [
            "app_name variable set to products for URL namespace resolution",
            "urlpatterns list initialized empty as placeholder for future routes",
            "products URLs included in project urls.py under api/v1/products/ prefix",
            "category endpoints planned under api/v1/categories/ nested prefix",
            "variant endpoints planned as nested resource under products",
            "search endpoint planned for full-text product catalog search",
        ],
        "planned_endpoints": [
            "GET /api/v1/products/ for paginated product catalog listing",
            "POST /api/v1/products/ for creating new product entries",
            "GET /api/v1/products/:id/ to retrieve single product with variants",
            "PATCH /api/v1/products/:id/ to update product information",
            "GET /api/v1/categories/ for hierarchical category tree listing",
            "GET /api/v1/products/search/ for full-text product search by keyword",
        ],
        "url_conventions": [
            "URL patterns use path() with named routes for reverse resolution",
            "view names use lowercase-hyphenated format like product-list, product-detail",
            "list endpoints support pagination, filtering, and ordering parameters",
            "detail endpoints use UUID lookup field not integer primary key",
            "nested variant endpoints accessed via /products/:id/variants/ pattern",
            "rate limiting applied to search endpoints to prevent resource exhaustion",
        ],
    }
    logger.debug(
        "Products urls config: url_structure=%d, planned_endpoints=%d",
        len(config["url_structure"]),
        len(config["planned_endpoints"]),
    )
    return config


def get_products_registration_config() -> dict:
    """Return products registration configuration.

    Documents the products app registration in Django settings,
    including placement in TENANT_APPS for per-tenant product data,
    app ordering conventions, and catalog feature flags.

    SubPhase-01, Group-D, Task 43.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *catalog_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "products app registered as apps.products in TENANT_APPS setting",
            "registration ensures product tables created in each tenant schema",
            "AppConfig path apps.products.apps.ProductsConfig used for explicit config",
            "products app listed after users and before inventory in app ordering",
            "settings file located at backend/config/settings/base.py",
            "products also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "products app placed in TENANT_APPS for per-tenant catalog isolation",
            "each tenant schema gets its own product tables for data separation",
            "shared product templates handled via public schema if cross-tenant needed",
            "TENANT_APPS ordering places products after users, before inventory",
            "adding products to TENANT_APPS requires running migrate_schemas for tenants",
        ],
        "catalog_settings": [
            "PRODUCTS_DEFAULT_CURRENCY set to LKR for Sri Lankan Rupee default",
            "PRODUCTS_MAX_VARIANTS_PER_PRODUCT limits variant count per product",
            "PRODUCTS_IMAGE_MAX_SIZE limits upload file size for product images",
            "PRODUCTS_SKU_AUTO_GENERATE toggle for automatic SKU generation",
            "PRODUCTS_BARCODE_FORMAT set to EAN-13 for standard barcode support",
            "PRODUCTS_SEARCH_BACKEND configurable for Elasticsearch or database search",
        ],
    }
    logger.debug(
        "Products registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_inventory_app_directory_config() -> dict:
    """Return inventory app directory configuration.

    Documents the inventory application directory structure, including
    its purpose as the home for stock management, warehouse locations,
    and stock movement tracking within the multi-tenant POS system.

    SubPhase-01, Group-D, Task 44.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_purpose* list, *directory_contents* list,
              and *stock_scope* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_purpose": [
            "inventory app located at backend/apps/inventory/ for stock management",
            "houses stock models including Stock, Location, and StockMovement",
            "provides real-time stock level tracking across warehouse locations",
            "contains stock movement logic for transfers, adjustments, and receipts",
            "serves as the integration point for products and orders modules",
            "holds inventory-related signals for low-stock alerts and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks inventory as a Python package with app docstring",
            "apps.py contains InventoryConfig with metadata and ready() hook",
            "models.py holds Stock, Location, and StockMovement model definitions",
            "admin.py registers inventory models with custom admin classes",
            "urls.py defines inventory endpoints under /api/v1/inventory/",
            "serializers.py contains DRF serializers for inventory API responses",
        ],
        "stock_scope": [
            "stock model tracks quantity on hand per product per location",
            "location model represents warehouses, stores, and virtual stock areas",
            "stock movement model records all inventory transactions with timestamps",
            "reorder point and reorder quantity fields for automatic replenishment",
            "batch and serial number tracking for product traceability support",
            "stock valuation methods including FIFO, LIFO, and weighted average",
        ],
    }
    logger.debug(
        "Inventory app directory config: directory_purpose=%d, directory_contents=%d",
        len(config["directory_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_inventory_init_config() -> dict:
    """Return inventory __init__.py configuration.

    Documents the inventory application package initialization, including
    module discovery, default app configuration, and package-level
    conventions for the inventory app.

    SubPhase-01, Group-D, Task 45.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_contents* list, *discovery_behavior* list,
              and *init_conventions* list.
    """
    config: dict = {
        "init_documented": True,
        "init_contents": [
            "module docstring describing inventory app purpose and responsibilities",
            "default_app_config set to apps.inventory.apps.InventoryConfig if needed",
            "package-level imports kept minimal to avoid circular dependencies",
            "no model imports at package level for safe Django app loading order",
            "TYPE_CHECKING guard used for type annotation convenience imports",
            "package provides apps.inventory namespace for all stock functionality",
        ],
        "discovery_behavior": [
            "Django autodiscover_modules finds admin registrations in inventory app",
            "pytest discovers test modules via apps.inventory package namespace",
            "migration runner resolves inventory app label for schema operations",
            "management command discovery uses apps.inventory.management.commands path",
            "DRF router autodiscovery registers inventory viewsets from inventory app",
            "signal handlers connected during InventoryConfig.ready() method call",
        ],
        "init_conventions": [
            "keep __init__.py lightweight with docstring and minimal code",
            "avoid importing models at package level to prevent AppRegistryNotReady",
            "utility functions re-exported via apps.inventory.utils sub-package",
            "stock calculation helpers exposed through dedicated stock service module",
            "any public API documented in __all__ list for explicit surface",
            "version metadata omitted in favor of centralized project versioning",
        ],
    }
    logger.debug(
        "Inventory init config: init_contents=%d, discovery_behavior=%d",
        len(config["init_contents"]),
        len(config["discovery_behavior"]),
    )
    return config


def get_inventory_apps_config() -> dict:
    """Return inventory apps.py configuration.

    Documents the InventoryConfig AppConfig subclass, including the
    app name, label, verbose name, and the ready() method for
    signal registration and inventory-specific startup tasks.

    SubPhase-01, Group-D, Task 46.

    Returns:
        dict: Configuration with *config_documented* flag,
              *config_attributes* list, *ready_hook_tasks* list,
              and *config_conventions* list.
    """
    config: dict = {
        "config_documented": True,
        "config_attributes": [
            "name set to apps.inventory matching the full dotted Python path",
            "label set to inventory for database table prefix and migration references",
            "verbose_name set to Inventory for human-readable admin display",
            "default_auto_field set to django.db.models.BigAutoField for primary keys",
            "AppConfig subclass named InventoryConfig following Django naming convention",
            "module docstring documents stock management and location tracking scope",
        ],
        "ready_hook_tasks": [
            "import and connect stock post_save signal for low-stock alert dispatch",
            "import and connect stock movement signal for audit trail logging",
            "register system checks for stock model field validation rules",
            "log inventory app startup confirmation at info level",
            "validate that stock location references are properly configured",
            "connect product delete signal for cascading stock cleanup operations",
        ],
        "config_conventions": [
            "one AppConfig class per apps.py following Django best practice",
            "ready() imports signals module to avoid circular import issues",
            "system checks tagged with inventory for selective check execution",
            "verbose_name uses singular Inventory matching the app directory name",
            "app label matches directory name for consistent ORM table prefixing",
            "no database queries executed during ready() to prevent migration issues",
        ],
    }
    logger.debug(
        "Inventory apps config: config_attributes=%d, ready_hook_tasks=%d",
        len(config["config_attributes"]),
        len(config["ready_hook_tasks"]),
    )
    return config


def get_inventory_models_config() -> dict:
    """Return inventory models.py configuration.

    Documents the inventory models placeholder including Stock,
    Location, and StockMovement model definitions planned for full
    implementation in Phase-04 ERP Core Modules.

    SubPhase-01, Group-D, Task 47.

    Returns:
        dict: Configuration with *models_documented* flag,
              *placeholder_details* list, *planned_models* list,
              and *model_conventions* list.
    """
    config: dict = {
        "models_documented": True,
        "placeholder_details": [
            "Stock model placeholder tracking quantity per product per location",
            "Location model placeholder representing warehouses and store areas",
            "StockMovement model placeholder recording all inventory transactions",
            "placeholder created now with full implementation in Phase-04 subphases",
            "initial migration created early to establish table structure in schemas",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
        ],
        "planned_models": [
            "Stock model with product, location, quantity, and reorder fields",
            "Location model with name, address, type, and capacity attributes",
            "StockMovement model with source, destination, quantity, and reason fields",
            "StockAdjustment model for manual corrections with approval workflow",
            "StockCount model for periodic physical inventory counting sessions",
            "StockAlert model for configurable low-stock notification thresholds",
        ],
        "model_conventions": [
            "all models inherit from core TimeStampedModel for audit timestamps",
            "string representation returns stock identifier with location context",
            "Meta class sets unique_together for product and location combinations",
            "UUIDField used as public-facing identifier instead of integer primary key",
            "soft delete support via is_active flag for archived stock records",
            "custom managers provide location-filtered and low-stock querysets",
        ],
    }
    logger.debug(
        "Inventory models config: placeholder_details=%d, planned_models=%d",
        len(config["placeholder_details"]),
        len(config["planned_models"]),
    )
    return config


def get_inventory_admin_config() -> dict:
    """Return inventory admin.py configuration.

    Documents the inventory admin placeholder, including planned
    registrations for Stock, Location, and StockMovement models and
    admin class conventions for inventory management interfaces.

    SubPhase-01, Group-D, Task 48.

    Returns:
        dict: Configuration with *admin_documented* flag,
              *admin_registrations* list, *admin_features* list,
              and *admin_conventions* list.
    """
    config: dict = {
        "admin_documented": True,
        "admin_registrations": [
            "StockAdmin registers Stock model with product and location filters",
            "LocationAdmin registers Location model with type and capacity display",
            "StockMovementAdmin registers StockMovement model with read-only views",
            "admin placeholder created now with full registration in later phase",
            "admin autodiscovery includes inventory app when registered in settings",
            "StockInline provides tabular inline editing on location detail page",
        ],
        "admin_features": [
            "list_display shows product, location, quantity, and last updated date",
            "list_filter includes location, product category, and stock level status",
            "search_fields configured for product name, SKU, and location name",
            "ordering set to product name and location for grouped list presentation",
            "readonly_fields includes created_at, updated_at, and movement history",
            "actions include stock adjustment, bulk transfer, and export to CSV",
        ],
        "admin_conventions": [
            "each model gets a dedicated ModelAdmin class for customization",
            "fieldsets organized into stock info, location, quantities, and metadata",
            "inline admin classes used for stock entries within location forms",
            "custom admin form validates stock quantity non-negative constraints",
            "list_per_page set to 50 for inventory views with many stock records",
            "admin site header customized to LankaCommerce Cloud Inventory Management",
        ],
    }
    logger.debug(
        "Inventory admin config: admin_registrations=%d, admin_features=%d",
        len(config["admin_registrations"]),
        len(config["admin_features"]),
    )
    return config


def get_inventory_urls_config() -> dict:
    """Return inventory urls.py configuration.

    Documents the inventory URL placeholder, including namespace setup,
    API versioning alignment, and planned endpoint patterns for
    stock management and location operations.

    SubPhase-01, Group-D, Task 49.

    Returns:
        dict: Configuration with *urls_documented* flag,
              *url_structure* list, *planned_endpoints* list,
              and *url_conventions* list.
    """
    config: dict = {
        "urls_documented": True,
        "url_structure": [
            "app_name variable set to inventory for URL namespace resolution",
            "urlpatterns list initialized empty as placeholder for future routes",
            "inventory URLs included in project urls.py under api/v1/inventory/ prefix",
            "location endpoints planned under api/v1/locations/ nested prefix",
            "stock movement endpoints planned as nested resource under inventory",
            "stock count endpoint planned for physical inventory counting sessions",
        ],
        "planned_endpoints": [
            "GET /api/v1/inventory/ for paginated stock level listing by location",
            "POST /api/v1/inventory/adjust/ for creating stock adjustment entries",
            "GET /api/v1/inventory/:id/ to retrieve stock detail with movement history",
            "POST /api/v1/inventory/transfer/ for inter-location stock transfers",
            "GET /api/v1/locations/ for warehouse and store location listing",
            "GET /api/v1/inventory/low-stock/ for low-stock alert report endpoint",
        ],
        "url_conventions": [
            "URL patterns use path() with named routes for reverse resolution",
            "view names use lowercase-hyphenated format like stock-list, stock-adjust",
            "list endpoints support pagination, filtering by location and product",
            "detail endpoints use UUID lookup field not integer primary key",
            "movement history endpoints accessed via /inventory/:id/movements/ pattern",
            "rate limiting applied to adjustment endpoints to prevent data corruption",
        ],
    }
    logger.debug(
        "Inventory urls config: url_structure=%d, planned_endpoints=%d",
        len(config["url_structure"]),
        len(config["planned_endpoints"]),
    )
    return config


def get_inventory_registration_config() -> dict:
    """Return inventory registration configuration.

    Documents the inventory app registration in Django settings,
    including placement in TENANT_APPS for per-tenant inventory data,
    app ordering conventions, and inventory feature flags.

    SubPhase-01, Group-D, Task 50.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *inventory_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "inventory app registered as apps.inventory in TENANT_APPS setting",
            "registration ensures inventory tables created in each tenant schema",
            "AppConfig path apps.inventory.apps.InventoryConfig used for explicit config",
            "inventory app listed after products in app ordering for dependency",
            "settings file located at backend/config/settings/base.py",
            "inventory also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "inventory app placed in TENANT_APPS for per-tenant stock isolation",
            "each tenant schema gets its own inventory tables for data separation",
            "shared inventory data handled via public schema if cross-tenant needed",
            "TENANT_APPS ordering places inventory after products for foreign keys",
            "adding inventory to TENANT_APPS requires running migrate_schemas for tenants",
        ],
        "inventory_settings": [
            "INVENTORY_LOW_STOCK_THRESHOLD default minimum quantity for alerts",
            "INVENTORY_TRACK_SERIAL_NUMBERS toggle for serial number tracking",
            "INVENTORY_VALUATION_METHOD set to FIFO for default stock valuation",
            "INVENTORY_AUTO_REORDER toggle for automatic purchase order generation",
            "INVENTORY_COUNT_FREQUENCY set to monthly for scheduled stock counts",
            "INVENTORY_MOVEMENT_APPROVAL toggle for requiring approval on adjustments",
        ],
    }
    logger.debug(
        "Inventory registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_sales_app_directory_config() -> dict:
    """Return sales app directory configuration.

    Documents the sales application directory structure, including
    its purpose as the home for sales orders, invoices, payment
    processing, and POS transaction management.

    SubPhase-01, Group-E, Task 51.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_purpose* list, *directory_contents* list,
              and *sales_scope* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_purpose": [
            "sales app located at backend/apps/sales/ for order management",
            "houses sales models including Order, Invoice, and Payment",
            "provides POS transaction processing and checkout functionality",
            "contains invoice generation logic for completed sales orders",
            "serves as the integration point for products and customers modules",
            "holds sales-related signals for order status changes and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks sales as a Python package with app docstring",
            "apps.py contains SalesConfig with metadata and ready() hook",
            "models.py holds Order, OrderItem, Invoice, and Payment definitions",
            "admin.py registers sales models with custom admin classes",
            "urls.py defines sales endpoints under /api/v1/sales/",
            "serializers.py contains DRF serializers for sales API responses",
        ],
        "sales_scope": [
            "order model tracks customer purchases with line items and totals",
            "invoice model generates printable documents for completed orders",
            "payment model records payment methods including cash, card, and mobile",
            "order status workflow supports draft, confirmed, completed, and cancelled",
            "tax calculation integrated with Sri Lanka VAT and NBT requirements",
            "discount and promotion application supported at order and item level",
        ],
    }
    logger.debug(
        "Sales app directory config: directory_purpose=%d, directory_contents=%d",
        len(config["directory_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_sales_init_config() -> dict:
    """Return sales __init__.py configuration.

    Documents the sales application package initialization, including
    module discovery, default app configuration, and package-level
    conventions for the sales app.

    SubPhase-01, Group-E, Task 52.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_contents* list, *discovery_behavior* list,
              and *init_conventions* list.
    """
    config: dict = {
        "init_documented": True,
        "init_contents": [
            "module docstring describing sales app purpose and responsibilities",
            "default_app_config set to apps.sales.apps.SalesConfig if needed",
            "package-level imports kept minimal to avoid circular dependencies",
            "no model imports at package level for safe Django app loading order",
            "TYPE_CHECKING guard used for type annotation convenience imports",
            "package provides apps.sales namespace for all order functionality",
        ],
        "discovery_behavior": [
            "Django autodiscover_modules finds admin registrations in sales app",
            "pytest discovers test modules via apps.sales package namespace",
            "migration runner resolves sales app label for schema operations",
            "management command discovery uses apps.sales.management.commands path",
            "DRF router autodiscovery registers sales viewsets from sales app",
            "signal handlers connected during SalesConfig.ready() method call",
        ],
        "init_conventions": [
            "keep __init__.py lightweight with docstring and minimal code",
            "avoid importing models at package level to prevent AppRegistryNotReady",
            "utility functions re-exported via apps.sales.utils sub-package",
            "order processing helpers exposed through dedicated order service module",
            "any public API documented in __all__ list for explicit surface",
            "version metadata omitted in favor of centralized project versioning",
        ],
    }
    logger.debug(
        "Sales init config: init_contents=%d, discovery_behavior=%d",
        len(config["init_contents"]),
        len(config["discovery_behavior"]),
    )
    return config


def get_sales_apps_config() -> dict:
    """Return sales apps.py configuration.

    Documents the SalesConfig AppConfig subclass, including the
    app name, label, verbose name, and the ready() method for
    signal registration and sales-specific startup tasks.

    SubPhase-01, Group-E, Task 53.

    Returns:
        dict: Configuration with *config_documented* flag,
              *config_attributes* list, *ready_hook_tasks* list,
              and *config_conventions* list.
    """
    config: dict = {
        "config_documented": True,
        "config_attributes": [
            "name set to apps.sales matching the full dotted Python path",
            "label set to sales for database table prefix and migration references",
            "verbose_name set to Sales for human-readable admin display",
            "default_auto_field set to django.db.models.BigAutoField for primary keys",
            "AppConfig subclass named SalesConfig following Django naming convention",
            "module docstring documents order processing and payment management scope",
        ],
        "ready_hook_tasks": [
            "import and connect order post_save signal for inventory deduction",
            "import and connect payment signal for invoice generation trigger",
            "register system checks for order model field validation rules",
            "log sales app startup confirmation at info level",
            "validate that order number sequence generator is properly configured",
            "connect order cancellation signal for stock reversal dispatch",
        ],
        "config_conventions": [
            "one AppConfig class per apps.py following Django best practice",
            "ready() imports signals module to avoid circular import issues",
            "system checks tagged with sales for selective check execution",
            "verbose_name uses plural Sales matching the app directory name",
            "app label matches directory name for consistent ORM table prefixing",
            "no database queries executed during ready() to prevent migration issues",
        ],
    }
    logger.debug(
        "Sales apps config: config_attributes=%d, ready_hook_tasks=%d",
        len(config["config_attributes"]),
        len(config["ready_hook_tasks"]),
    )
    return config


def get_sales_models_config() -> dict:
    """Return sales models.py configuration.

    Documents the sales models placeholder including Order, Invoice,
    and Payment model definitions planned for full implementation
    in Phase-04 ERP Core Modules.

    SubPhase-01, Group-E, Task 54.

    Returns:
        dict: Configuration with *models_documented* flag,
              *placeholder_details* list, *planned_models* list,
              and *model_conventions* list.
    """
    config: dict = {
        "models_documented": True,
        "placeholder_details": [
            "Order model placeholder with customer, items, and total amount fields",
            "Invoice model placeholder with order reference and payment terms",
            "Payment model placeholder with method, amount, and transaction reference",
            "placeholder created now with full implementation in Phase-04 subphases",
            "initial migration created early to establish table structure in schemas",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
        ],
        "planned_models": [
            "Order model with order number, customer, status, and total fields",
            "OrderItem model linking orders to products with quantity and price",
            "Invoice model with invoice number, due date, and payment status",
            "Payment model with method type, amount, reference, and timestamp",
            "OrderDiscount model for percentage and fixed amount discounts",
            "OrderNote model for internal notes and customer communication history",
        ],
        "model_conventions": [
            "all models inherit from core TimeStampedModel for audit timestamps",
            "string representation returns order number or invoice number identifier",
            "Meta class sets ordering by created_at descending for recent-first lists",
            "UUIDField used as public-facing identifier instead of integer primary key",
            "order status field uses TextChoices for type-safe status transitions",
            "custom managers provide status-filtered and date-range querysets",
        ],
    }
    logger.debug(
        "Sales models config: placeholder_details=%d, planned_models=%d",
        len(config["placeholder_details"]),
        len(config["planned_models"]),
    )
    return config


def get_sales_admin_config() -> dict:
    """Return sales admin.py configuration.

    Documents the sales admin placeholder, including planned
    registrations for Order, Invoice, and Payment models and
    admin class conventions for sales management interfaces.

    SubPhase-01, Group-E, Task 55.

    Returns:
        dict: Configuration with *admin_documented* flag,
              *admin_registrations* list, *admin_features* list,
              and *admin_conventions* list.
    """
    config: dict = {
        "admin_documented": True,
        "admin_registrations": [
            "OrderAdmin registers Order model with status and customer filters",
            "InvoiceAdmin registers Invoice model with payment status display",
            "PaymentAdmin registers Payment model with method and amount filters",
            "admin placeholder created now with full registration in later phase",
            "admin autodiscovery includes sales app when registered in settings",
            "OrderItemInline provides tabular inline editing on order detail page",
        ],
        "admin_features": [
            "list_display shows order number, customer, status, total, and date",
            "list_filter includes status, payment method, date range, and customer",
            "search_fields configured for order number, customer name, and email",
            "ordering set to created_at descending for recent orders first",
            "readonly_fields includes created_at, updated_at, and order number",
            "actions include mark as paid, generate invoice, and export to CSV",
        ],
        "admin_conventions": [
            "each model gets a dedicated ModelAdmin class for customization",
            "fieldsets organized into order info, items, payment, and metadata",
            "inline admin classes used for order items within order forms",
            "custom admin form validates payment amount against order total",
            "list_per_page set to 25 for optimal order list performance",
            "admin site header customized to LankaCommerce Cloud Sales Management",
        ],
    }
    logger.debug(
        "Sales admin config: admin_registrations=%d, admin_features=%d",
        len(config["admin_registrations"]),
        len(config["admin_features"]),
    )
    return config


def get_sales_urls_config() -> dict:
    """Return sales urls.py configuration.

    Documents the sales URL placeholder, including namespace setup,
    API versioning alignment, and planned endpoint patterns for
    order management and payment processing operations.

    SubPhase-01, Group-E, Task 56.

    Returns:
        dict: Configuration with *urls_documented* flag,
              *url_structure* list, *planned_endpoints* list,
              and *url_conventions* list.
    """
    config: dict = {
        "urls_documented": True,
        "url_structure": [
            "app_name variable set to sales for URL namespace resolution",
            "urlpatterns list initialized empty as placeholder for future routes",
            "sales URLs included in project urls.py under api/v1/sales/ prefix",
            "invoice endpoints planned under api/v1/invoices/ nested prefix",
            "payment endpoints planned as nested resource under orders",
            "POS checkout endpoint planned for real-time transaction processing",
        ],
        "planned_endpoints": [
            "GET /api/v1/sales/orders/ for paginated order listing with filters",
            "POST /api/v1/sales/orders/ for creating new sales orders",
            "GET /api/v1/sales/orders/:id/ to retrieve order with items and payment",
            "POST /api/v1/sales/orders/:id/pay/ for processing order payment",
            "GET /api/v1/sales/invoices/ for invoice listing by date range",
            "POST /api/v1/sales/checkout/ for POS point-of-sale transaction",
        ],
        "url_conventions": [
            "URL patterns use path() with named routes for reverse resolution",
            "view names use lowercase-hyphenated format like order-list, order-pay",
            "list endpoints support pagination, filtering by status and date range",
            "detail endpoints use UUID lookup field not integer primary key",
            "payment endpoints accessed via /orders/:id/payments/ nested pattern",
            "rate limiting applied to checkout endpoints to prevent duplicate orders",
        ],
    }
    logger.debug(
        "Sales urls config: url_structure=%d, planned_endpoints=%d",
        len(config["url_structure"]),
        len(config["planned_endpoints"]),
    )
    return config


def get_sales_registration_config() -> dict:
    """Return sales registration configuration.

    Documents the sales app registration in Django settings,
    including placement in TENANT_APPS for per-tenant sales data,
    app ordering conventions, and sales feature flags.

    SubPhase-01, Group-E, Task 57.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *sales_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "sales app registered as apps.sales in TENANT_APPS setting",
            "registration ensures sales tables created in each tenant schema",
            "AppConfig path apps.sales.apps.SalesConfig used for explicit config",
            "sales app listed after inventory and before customers in app ordering",
            "settings file located at backend/config/settings/base.py",
            "sales also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "sales app placed in TENANT_APPS for per-tenant order isolation",
            "each tenant schema gets its own sales tables for data separation",
            "shared sales reports handled via cross-schema aggregation queries",
            "TENANT_APPS ordering places sales after inventory for stock references",
            "adding sales to TENANT_APPS requires running migrate_schemas for tenants",
        ],
        "sales_settings": [
            "SALES_ORDER_NUMBER_PREFIX configurable per tenant for order numbering",
            "SALES_TAX_RATE default rate for Sri Lanka VAT calculation",
            "SALES_INVOICE_AUTO_GENERATE toggle for automatic invoice creation",
            "SALES_PAYMENT_METHODS list of enabled payment method options",
            "SALES_RECEIPT_TEMPLATE configurable receipt format for POS printing",
            "SALES_ORDER_EXPIRY_HOURS timeout for draft orders auto-cancellation",
        ],
    }
    logger.debug(
        "Sales registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_customers_app_directory_config() -> dict:
    """Return customers app directory configuration.

    Documents the customers application directory structure, including
    its purpose as the home for customer profiles, addresses, loyalty
    points, and customer relationship management within the POS system.

    SubPhase-01, Group-E, Task 58.

    Returns:
        dict: Configuration with *directory_documented* flag,
              *directory_purpose* list, *directory_contents* list,
              and *customer_scope* list.
    """
    config: dict = {
        "directory_documented": True,
        "directory_purpose": [
            "customers app located at backend/apps/customers/ for CRM management",
            "houses customer models including Customer, Address, and LoyaltyPoints",
            "provides customer profile management and search functionality",
            "contains loyalty program logic for points earning and redemption",
            "serves as the integration point for sales and orders modules",
            "holds customer-related signals for profile updates and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks customers as a Python package with app docstring",
            "apps.py contains CustomersConfig with metadata and ready() hook",
            "models.py holds Customer, Address, and LoyaltyPoints model definitions",
            "admin.py registers customer models with custom admin classes",
            "urls.py defines customer endpoints under /api/v1/customers/",
            "serializers.py contains DRF serializers for customer API responses",
        ],
        "customer_scope": [
            "customer model stores profile data including name, email, and phone",
            "address model supports multiple addresses per customer with type labels",
            "loyalty points model tracks earning, redemption, and balance history",
            "customer groups for segmentation and targeted promotions support",
            "credit limit and payment terms configurable per customer account",
            "customer import and export via CSV for bulk data operations",
        ],
    }
    logger.debug(
        "Customers app directory config: directory_purpose=%d, directory_contents=%d",
        len(config["directory_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_customers_init_config() -> dict:
    """Return customers __init__.py configuration.

    Documents the customers application package initialization, including
    module discovery, default app configuration, and package-level
    conventions for the customers app.

    SubPhase-01, Group-E, Task 59.

    Returns:
        dict: Configuration with *init_documented* flag,
              *init_contents* list, *discovery_behavior* list,
              and *init_conventions* list.
    """
    config: dict = {
        "init_documented": True,
        "init_contents": [
            "module docstring describing customers app purpose and responsibilities",
            "default_app_config set to apps.customers.apps.CustomersConfig if needed",
            "package-level imports kept minimal to avoid circular dependencies",
            "no model imports at package level for safe Django app loading order",
            "TYPE_CHECKING guard used for type annotation convenience imports",
            "package provides apps.customers namespace for all CRM functionality",
        ],
        "discovery_behavior": [
            "Django autodiscover_modules finds admin registrations in customers app",
            "pytest discovers test modules via apps.customers package namespace",
            "migration runner resolves customers app label for schema operations",
            "management command discovery uses apps.customers.management.commands path",
            "DRF router autodiscovery registers customer viewsets from customers app",
            "signal handlers connected during CustomersConfig.ready() method call",
        ],
        "init_conventions": [
            "keep __init__.py lightweight with docstring and minimal code",
            "avoid importing models at package level to prevent AppRegistryNotReady",
            "utility functions re-exported via apps.customers.utils sub-package",
            "customer lookup helpers exposed through dedicated customer service module",
            "any public API documented in __all__ list for explicit surface",
            "version metadata omitted in favor of centralized project versioning",
        ],
    }
    logger.debug(
        "Customers init config: init_contents=%d, discovery_behavior=%d",
        len(config["init_contents"]),
        len(config["discovery_behavior"]),
    )
    return config


def get_customers_apps_config() -> dict:
    """Return customers apps.py configuration.

    Documents the CustomersConfig AppConfig subclass, including the
    app name, label, verbose name, and the ready() method for
    signal registration and customer-specific startup tasks.

    SubPhase-01, Group-E, Task 60.

    Returns:
        dict: Configuration with *config_documented* flag,
              *config_attributes* list, *ready_hook_tasks* list,
              and *config_conventions* list.
    """
    config: dict = {
        "config_documented": True,
        "config_attributes": [
            "name set to apps.customers matching the full dotted Python path",
            "label set to customers for database table prefix and migration references",
            "verbose_name set to Customers for human-readable admin display",
            "default_auto_field set to django.db.models.BigAutoField for primary keys",
            "AppConfig subclass named CustomersConfig following Django naming convention",
            "module docstring documents customer profile and loyalty management scope",
        ],
        "ready_hook_tasks": [
            "import and connect customer post_save signal for loyalty enrollment",
            "import and connect address change signal for order address sync",
            "register system checks for customer model field validation rules",
            "log customers app startup confirmation at info level",
            "validate that customer code sequence generator is properly configured",
            "connect customer merge signal for duplicate resolution operations",
        ],
        "config_conventions": [
            "one AppConfig class per apps.py following Django best practice",
            "ready() imports signals module to avoid circular import issues",
            "system checks tagged with customers for selective check execution",
            "verbose_name uses plural Customers matching the app directory name",
            "app label matches directory name for consistent ORM table prefixing",
            "no database queries executed during ready() to prevent migration issues",
        ],
    }
    logger.debug(
        "Customers apps config: config_attributes=%d, ready_hook_tasks=%d",
        len(config["config_attributes"]),
        len(config["ready_hook_tasks"]),
    )
    return config


def get_customers_models_config() -> dict:
    """Return customers models.py configuration.

    Documents the customers models placeholder including Customer,
    Address, and LoyaltyPoints model definitions planned for full
    implementation in Phase-04 ERP Core Modules.

    SubPhase-01, Group-E, Task 61.

    Returns:
        dict: Configuration with *models_documented* flag,
              *placeholder_details* list, *planned_models* list,
              and *model_conventions* list.
    """
    config: dict = {
        "models_documented": True,
        "placeholder_details": [
            "Customer model placeholder with name, email, phone, and code fields",
            "Address model placeholder with street, city, postal code, and type",
            "LoyaltyPoints model placeholder for points balance and transaction history",
            "placeholder created now with full implementation in Phase-04 subphases",
            "initial migration created early to establish table structure in schemas",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
        ],
        "planned_models": [
            "Customer model with code, name, email, phone, and tax ID fields",
            "Address model with type, street, city, district, and postal code",
            "LoyaltyPoints model with customer, points balance, and tier level",
            "CustomerGroup model for segmentation and group-based pricing rules",
            "CustomerNote model for internal CRM notes and follow-up reminders",
            "CustomerCredit model for credit limit and outstanding balance tracking",
        ],
        "model_conventions": [
            "all models inherit from core TimeStampedModel for audit timestamps",
            "string representation returns customer name or code as identifier",
            "Meta class sets ordering by name and verbose_name for admin display",
            "UUIDField used as public-facing identifier instead of integer primary key",
            "soft delete support via is_active flag for archived customer records",
            "custom managers provide group-filtered and loyalty-tier querysets",
        ],
    }
    logger.debug(
        "Customers models config: placeholder_details=%d, planned_models=%d",
        len(config["placeholder_details"]),
        len(config["planned_models"]),
    )
    return config


def get_customers_admin_config() -> dict:
    """Return customers admin.py configuration.

    Documents the customers admin placeholder, including planned
    registrations for Customer, Address, and LoyaltyPoints models
    and admin class conventions for CRM management interfaces.

    SubPhase-01, Group-E, Task 62.

    Returns:
        dict: Configuration with *admin_documented* flag,
              *admin_registrations* list, *admin_features* list,
              and *admin_conventions* list.
    """
    config: dict = {
        "admin_documented": True,
        "admin_registrations": [
            "CustomerAdmin registers Customer model with profile and group filters",
            "AddressAdmin registers Address model as inline on CustomerAdmin",
            "LoyaltyPointsAdmin registers LoyaltyPoints model with balance display",
            "admin placeholder created now with full registration in later phase",
            "admin autodiscovery includes customers app when registered in settings",
            "AddressInline provides stacked inline editing on customer detail page",
        ],
        "admin_features": [
            "list_display shows customer code, name, email, phone, and loyalty tier",
            "list_filter includes customer group, loyalty tier, is_active, and city",
            "search_fields configured for customer name, email, phone, and code",
            "ordering set to name for consistent alphabetical list presentation",
            "readonly_fields includes created_at, updated_at, and customer code",
            "actions include activate, deactivate, assign group, and export to CSV",
        ],
        "admin_conventions": [
            "each model gets a dedicated ModelAdmin class for customization",
            "fieldsets organized into profile info, contact, loyalty, and metadata",
            "inline admin classes used for address editing within customer forms",
            "custom admin form validates email uniqueness within the tenant schema",
            "list_per_page set to 25 for optimal customer list performance",
            "admin site header customized to LankaCommerce Cloud Customer Management",
        ],
    }
    logger.debug(
        "Customers admin config: admin_registrations=%d, admin_features=%d",
        len(config["admin_registrations"]),
        len(config["admin_features"]),
    )
    return config


def get_customers_urls_config() -> dict:
    """Return customers urls.py configuration.

    Documents the customers URL placeholder, including namespace setup,
    API versioning alignment, and planned endpoint patterns for
    customer profile and loyalty management operations.

    SubPhase-01, Group-E, Task 63.

    Returns:
        dict: Configuration with *urls_documented* flag,
              *url_structure* list, *planned_endpoints* list,
              and *url_conventions* list.
    """
    config: dict = {
        "urls_documented": True,
        "url_structure": [
            "app_name variable set to customers for URL namespace resolution",
            "urlpatterns list initialized empty as placeholder for future routes",
            "customers URLs included in project urls.py under api/v1/customers/ prefix",
            "address endpoints planned as nested resource under customers",
            "loyalty endpoints planned under api/v1/customers/:id/loyalty/ prefix",
            "customer search endpoint planned for name, email, and phone lookup",
        ],
        "planned_endpoints": [
            "GET /api/v1/customers/ for paginated customer listing with filters",
            "POST /api/v1/customers/ for creating new customer profiles",
            "GET /api/v1/customers/:id/ to retrieve customer with addresses",
            "PATCH /api/v1/customers/:id/ to update customer profile information",
            "GET /api/v1/customers/:id/loyalty/ for loyalty points balance and history",
            "GET /api/v1/customers/search/ for customer lookup by name, email, or phone",
        ],
        "url_conventions": [
            "URL patterns use path() with named routes for reverse resolution",
            "view names use lowercase-hyphenated format like customer-list, customer-detail",
            "list endpoints support pagination, filtering by group and loyalty tier",
            "detail endpoints use UUID lookup field not integer primary key",
            "address endpoints accessed via /customers/:id/addresses/ nested pattern",
            "rate limiting applied to search endpoints to prevent resource exhaustion",
        ],
    }
    logger.debug(
        "Customers urls config: url_structure=%d, planned_endpoints=%d",
        len(config["url_structure"]),
        len(config["planned_endpoints"]),
    )
    return config


def get_customers_registration_config() -> dict:
    """Return customers registration configuration.

    Documents the customers app registration in Django settings,
    including placement in TENANT_APPS for per-tenant customer data,
    app ordering conventions, and CRM feature flags.

    SubPhase-01, Group-E, Task 64.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *crm_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "customers app registered as apps.customers in TENANT_APPS setting",
            "registration ensures customer tables created in each tenant schema",
            "AppConfig path apps.customers.apps.CustomersConfig used for explicit config",
            "customers app listed after sales for order-customer relationship",
            "settings file located at backend/config/settings/base.py",
            "customers also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "customers app placed in TENANT_APPS for per-tenant CRM isolation",
            "each tenant schema gets its own customer tables for data separation",
            "shared customer data not supported to maintain tenant data boundaries",
            "TENANT_APPS ordering places customers after sales for reference integrity",
            "adding customers to TENANT_APPS requires running migrate_schemas for tenants",
        ],
        "crm_settings": [
            "CUSTOMERS_CODE_PREFIX configurable per tenant for customer numbering",
            "CUSTOMERS_LOYALTY_ENABLED toggle for loyalty program activation",
            "CUSTOMERS_LOYALTY_POINTS_PER_UNIT earning rate for purchase points",
            "CUSTOMERS_DEFAULT_GROUP name for newly created customer assignment",
            "CUSTOMERS_CREDIT_LIMIT_DEFAULT initial credit limit for new accounts",
            "CUSTOMERS_DUPLICATE_CHECK_FIELDS list of fields for duplicate detection",
        ],
    }
    logger.debug(
        "Customers registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_vendors_app_config() -> dict:
    """Return vendors app configuration.

    Documents the vendors application directory and purpose, including
    its role as the home for supplier management, purchase orders,
    and vendor relationship tracking within the multi-tenant POS system.

    SubPhase-01, Group-F, Task 65.

    Returns:
        dict: Configuration with *app_documented* flag,
              *app_purpose* list, *directory_contents* list,
              and *vendor_scope* list.
    """
    config: dict = {
        "app_documented": True,
        "app_purpose": [
            "vendors app located at backend/apps/vendors/ for supplier management",
            "houses vendor models including Vendor, PurchaseOrder, and VendorContact",
            "provides vendor profile management and purchase order processing",
            "contains supplier evaluation logic for performance tracking",
            "serves as the integration point for inventory and accounting modules",
            "holds vendor-related signals for order status updates and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks vendors as a Python package with app docstring",
            "apps.py contains VendorsConfig with metadata and ready() hook",
            "models.py holds Vendor, PurchaseOrder, and VendorContact definitions",
            "admin.py registers vendor models with custom admin classes",
            "urls.py defines vendor endpoints under /api/v1/vendors/",
            "serializers.py contains DRF serializers for vendor API responses",
        ],
        "vendor_scope": [
            "vendor model stores supplier profile including name, contact, and terms",
            "purchase order model tracks orders placed with vendors for restocking",
            "vendor contact model supports multiple contacts per vendor organization",
            "payment terms configurable per vendor for accounts payable management",
            "vendor rating system for delivery performance and quality assessment",
            "vendor import and export via CSV for bulk supplier data operations",
        ],
    }
    logger.debug(
        "Vendors app config: app_purpose=%d, directory_contents=%d",
        len(config["app_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_vendors_structure_config() -> dict:
    """Return vendors structure configuration.

    Documents the vendors app file structure, including apps.py,
    models.py, admin.py, and urls.py placeholders with their
    planned content and conventions.

    SubPhase-01, Group-F, Task 66.

    Returns:
        dict: Configuration with *structure_documented* flag,
              *app_config_details* list, *model_placeholders* list,
              and *admin_url_details* list.
    """
    config: dict = {
        "structure_documented": True,
        "app_config_details": [
            "VendorsConfig AppConfig subclass with name set to apps.vendors",
            "label set to vendors for database table prefix and migrations",
            "verbose_name set to Vendors for human-readable admin display",
            "ready() method connects vendor signals for order notifications",
            "default_auto_field set to BigAutoField for primary key generation",
            "module docstring documents supplier management and procurement scope",
        ],
        "model_placeholders": [
            "Vendor model placeholder with name, contact email, and phone fields",
            "PurchaseOrder model placeholder with vendor, items, and total amount",
            "VendorContact model placeholder for multiple contacts per vendor",
            "placeholder created now with full implementation in Phase-04 subphases",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
            "custom managers provide active vendor and pending order querysets",
        ],
        "admin_url_details": [
            "VendorAdmin registers Vendor model with search and filter support",
            "PurchaseOrderAdmin provides inline item editing on order detail page",
            "admin placeholder created now with full registration in later phase",
            "urls.py defines app_name vendors with empty urlpatterns placeholder",
            "vendor URLs included in project urls.py under api/v1/vendors/ prefix",
            "planned endpoints include vendor CRUD and purchase order management",
        ],
    }
    logger.debug(
        "Vendors structure config: app_config_details=%d, model_placeholders=%d",
        len(config["app_config_details"]),
        len(config["model_placeholders"]),
    )
    return config


def get_vendors_registration_config() -> dict:
    """Return vendors registration configuration.

    Documents the vendors app registration in Django settings,
    including placement in TENANT_APPS for per-tenant vendor data,
    app ordering conventions, and procurement feature flags.

    SubPhase-01, Group-F, Task 67.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *procurement_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "vendors app registered as apps.vendors in TENANT_APPS setting",
            "registration ensures vendor tables created in each tenant schema",
            "AppConfig path apps.vendors.apps.VendorsConfig used for explicit config",
            "vendors app listed after customers in app ordering for module grouping",
            "settings file located at backend/config/settings/base.py",
            "vendors also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "vendors app placed in TENANT_APPS for per-tenant supplier isolation",
            "each tenant schema gets its own vendor tables for data separation",
            "shared vendor catalogs not supported to maintain tenant boundaries",
            "TENANT_APPS ordering places vendors after customers before hr",
            "adding vendors to TENANT_APPS requires running migrate_schemas",
        ],
        "procurement_settings": [
            "VENDORS_CODE_PREFIX configurable per tenant for vendor numbering",
            "VENDORS_PO_NUMBER_FORMAT template for purchase order number generation",
            "VENDORS_DEFAULT_PAYMENT_TERMS days for default payment terms setting",
            "VENDORS_AUTO_REORDER_ENABLED toggle for automatic reorder generation",
            "VENDORS_RATING_ENABLED toggle for vendor performance rating system",
            "VENDORS_IMPORT_BATCH_SIZE limit for bulk vendor import operations",
        ],
    }
    logger.debug(
        "Vendors registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_hr_app_config() -> dict:
    """Return HR app configuration.

    Documents the HR application directory and purpose, including
    its role as the home for employee management, payroll processing,
    and attendance tracking within the multi-tenant POS system.

    SubPhase-01, Group-F, Task 68.

    Returns:
        dict: Configuration with *app_documented* flag,
              *app_purpose* list, *directory_contents* list,
              and *hr_scope* list.
    """
    config: dict = {
        "app_documented": True,
        "app_purpose": [
            "hr app located at backend/apps/hr/ for human resources management",
            "houses HR models including Employee, Department, and Payroll",
            "provides employee profile management and organizational structure",
            "contains payroll processing logic for salary and deduction calculations",
            "serves as the integration point for users and accounting modules",
            "holds HR-related signals for employee status changes and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks hr as a Python package with app docstring",
            "apps.py contains HrConfig with metadata and ready() hook",
            "models.py holds Employee, Department, and Payroll model definitions",
            "admin.py registers HR models with custom admin classes",
            "urls.py defines HR endpoints under /api/v1/hr/",
            "serializers.py contains DRF serializers for HR API responses",
        ],
        "hr_scope": [
            "employee model links to user account with additional employment data",
            "department model represents organizational units with hierarchy support",
            "payroll model tracks salary, deductions, and net pay per pay period",
            "attendance tracking for employee clock-in and clock-out records",
            "leave management for vacation, sick leave, and special leave requests",
            "employee document storage for contracts and compliance records",
        ],
    }
    logger.debug(
        "HR app config: app_purpose=%d, directory_contents=%d",
        len(config["app_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_hr_structure_config() -> dict:
    """Return HR structure configuration.

    Documents the HR app file structure, including apps.py,
    models.py, admin.py, and urls.py placeholders with their
    planned content and conventions.

    SubPhase-01, Group-F, Task 69.

    Returns:
        dict: Configuration with *structure_documented* flag,
              *app_config_details* list, *model_placeholders* list,
              and *admin_url_details* list.
    """
    config: dict = {
        "structure_documented": True,
        "app_config_details": [
            "HrConfig AppConfig subclass with name set to apps.hr",
            "label set to hr for database table prefix and migrations",
            "verbose_name set to Human Resources for admin display clarity",
            "ready() method connects employee signals for profile sync",
            "default_auto_field set to BigAutoField for primary key generation",
            "module docstring documents HR management and payroll processing scope",
        ],
        "model_placeholders": [
            "Employee model placeholder with user link, department, and position",
            "Department model placeholder with name, parent, and manager fields",
            "Payroll model placeholder with employee, period, salary, and deductions",
            "placeholder created now with full implementation in Phase-04 subphases",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
            "custom managers provide active employee and department-filtered querysets",
        ],
        "admin_url_details": [
            "EmployeeAdmin registers Employee model with department filters",
            "DepartmentAdmin provides tree display for organizational hierarchy",
            "admin placeholder created now with full registration in later phase",
            "urls.py defines app_name hr with empty urlpatterns placeholder",
            "HR URLs included in project urls.py under api/v1/hr/ prefix",
            "planned endpoints include employee CRUD and payroll management",
        ],
    }
    logger.debug(
        "HR structure config: app_config_details=%d, model_placeholders=%d",
        len(config["app_config_details"]),
        len(config["model_placeholders"]),
    )
    return config


def get_hr_registration_config() -> dict:
    """Return HR registration configuration.

    Documents the HR app registration in Django settings,
    including placement in TENANT_APPS for per-tenant HR data,
    app ordering conventions, and HR feature flags.

    SubPhase-01, Group-F, Task 70.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *hr_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "hr app registered as apps.hr in TENANT_APPS setting",
            "registration ensures HR tables created in each tenant schema",
            "AppConfig path apps.hr.apps.HrConfig used for explicit config",
            "hr app listed after vendors in app ordering for module grouping",
            "settings file located at backend/config/settings/base.py",
            "hr also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "hr app placed in TENANT_APPS for per-tenant employee isolation",
            "each tenant schema gets its own HR tables for data separation",
            "shared HR policies handled via public schema configuration tables",
            "TENANT_APPS ordering places hr after vendors before accounting",
            "adding hr to TENANT_APPS requires running migrate_schemas for tenants",
        ],
        "hr_settings": [
            "HR_EMPLOYEE_CODE_PREFIX configurable per tenant for employee numbering",
            "HR_PAYROLL_FREQUENCY set to monthly for default pay period cycle",
            "HR_LEAVE_TYPES list of configured leave categories for requests",
            "HR_ATTENDANCE_TRACKING_ENABLED toggle for clock-in/out functionality",
            "HR_OVERTIME_RATE_MULTIPLIER factor for overtime pay calculation",
            "HR_DOCUMENT_STORAGE_PATH configurable path for employee documents",
        ],
    }
    logger.debug(
        "HR registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_accounting_app_config() -> dict:
    """Return accounting app configuration.

    Documents the accounting application directory and purpose, including
    its role as the home for financial management, chart of accounts,
    journal entries, and tax reporting within the multi-tenant POS system.

    SubPhase-01, Group-F, Task 71.

    Returns:
        dict: Configuration with *app_documented* flag,
              *app_purpose* list, *directory_contents* list,
              and *accounting_scope* list.
    """
    config: dict = {
        "app_documented": True,
        "app_purpose": [
            "accounting app located at backend/apps/accounting/ for financial management",
            "houses accounting models including Account, JournalEntry, and TaxRate",
            "provides chart of accounts management and double-entry bookkeeping",
            "contains tax calculation logic for Sri Lanka VAT and NBT compliance",
            "serves as the integration point for sales, inventory, and payroll modules",
            "holds accounting-related signals for transaction posting and audit logging",
        ],
        "directory_contents": [
            "__init__.py marks accounting as a Python package with app docstring",
            "apps.py contains AccountingConfig with metadata and ready() hook",
            "models.py holds Account, JournalEntry, and TaxRate model definitions",
            "admin.py registers accounting models with custom admin classes",
            "urls.py defines accounting endpoints under /api/v1/accounting/",
            "serializers.py contains DRF serializers for accounting API responses",
        ],
        "accounting_scope": [
            "chart of accounts with hierarchical structure for asset, liability, equity",
            "journal entry model supports double-entry bookkeeping with debit and credit",
            "tax rate model configures VAT, NBT, and other Sri Lanka tax requirements",
            "fiscal period management for monthly and annual financial reporting",
            "bank reconciliation support for matching transactions with bank statements",
            "financial report generation for profit and loss and balance sheet views",
        ],
    }
    logger.debug(
        "Accounting app config: app_purpose=%d, directory_contents=%d",
        len(config["app_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_accounting_structure_config() -> dict:
    """Return accounting structure configuration.

    Documents the accounting app file structure, including apps.py,
    models.py, admin.py, and urls.py placeholders with their
    planned content and conventions.

    SubPhase-01, Group-F, Task 72.

    Returns:
        dict: Configuration with *structure_documented* flag,
              *app_config_details* list, *model_placeholders* list,
              and *admin_url_details* list.
    """
    config: dict = {
        "structure_documented": True,
        "app_config_details": [
            "AccountingConfig AppConfig subclass with name set to apps.accounting",
            "label set to accounting for database table prefix and migrations",
            "verbose_name set to Accounting for human-readable admin display",
            "ready() method connects accounting signals for transaction notifications",
            "default_auto_field set to BigAutoField for primary key generation",
            "module docstring documents financial management and reporting scope",
        ],
        "model_placeholders": [
            "Account model placeholder with code, name, type, and balance fields",
            "JournalEntry model placeholder with date, description, and line items",
            "TaxRate model placeholder with name, rate, and applicable categories",
            "placeholder created now with full implementation in Phase-04 subphases",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
            "custom managers provide account-type filtered and period-based querysets",
        ],
        "admin_url_details": [
            "AccountAdmin registers Account model with type and hierarchy filters",
            "JournalEntryAdmin provides inline line item editing on entry detail page",
            "admin placeholder created now with full registration in later phase",
            "urls.py defines app_name accounting with empty urlpatterns placeholder",
            "accounting URLs included in project urls.py under api/v1/accounting/",
            "planned endpoints include chart of accounts CRUD and journal entry posting",
        ],
    }
    logger.debug(
        "Accounting structure config: app_config_details=%d, model_placeholders=%d",
        len(config["app_config_details"]),
        len(config["model_placeholders"]),
    )
    return config


def get_accounting_registration_config() -> dict:
    """Return accounting registration configuration.

    Documents the accounting app registration in Django settings,
    including placement in TENANT_APPS for per-tenant financial data,
    app ordering conventions, and accounting feature flags.

    SubPhase-01, Group-F, Task 73.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *accounting_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "accounting app registered as apps.accounting in TENANT_APPS setting",
            "registration ensures accounting tables created in each tenant schema",
            "AppConfig path apps.accounting.apps.AccountingConfig used for explicit config",
            "accounting app listed after hr in app ordering for module grouping",
            "settings file located at backend/config/settings/base.py",
            "accounting also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "accounting app placed in TENANT_APPS for per-tenant financial isolation",
            "each tenant schema gets its own accounting tables for data separation",
            "shared chart of accounts templates available via public schema seed data",
            "TENANT_APPS ordering places accounting after hr before webstore",
            "adding accounting to TENANT_APPS requires running migrate_schemas",
        ],
        "accounting_settings": [
            "ACCOUNTING_DEFAULT_CURRENCY set to LKR for Sri Lankan Rupee",
            "ACCOUNTING_FISCAL_YEAR_START configurable month for fiscal period",
            "ACCOUNTING_VAT_RATE default rate for Sri Lanka value added tax",
            "ACCOUNTING_NBT_RATE default rate for nation building tax calculation",
            "ACCOUNTING_AUTO_POST toggle for automatic journal entry posting",
            "ACCOUNTING_DECIMAL_PLACES precision setting for monetary calculations",
        ],
    }
    logger.debug(
        "Accounting registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_webstore_app_config() -> dict:
    """Return webstore app configuration.

    Documents the webstore application directory and purpose, including
    its role as the home for e-commerce storefront API, shopping cart,
    and online ordering within the multi-tenant POS system.

    SubPhase-01, Group-F, Task 74.

    Returns:
        dict: Configuration with *app_documented* flag,
              *app_purpose* list, *directory_contents* list,
              and *webstore_scope* list.
    """
    config: dict = {
        "app_documented": True,
        "app_purpose": [
            "webstore app located at backend/apps/webstore/ for e-commerce storefront",
            "houses webstore models including Cart, CartItem, and OnlineOrder",
            "provides public-facing product catalog API for storefront clients",
            "contains shopping cart logic for session-based and user-based carts",
            "serves as the integration point for products, customers, and payments",
            "holds webstore-related signals for order placement and cart expiry",
        ],
        "directory_contents": [
            "__init__.py marks webstore as a Python package with app docstring",
            "apps.py contains WebstoreConfig with metadata and ready() hook",
            "models.py holds Cart, CartItem, and OnlineOrder model definitions",
            "admin.py registers webstore models with custom admin classes",
            "urls.py defines webstore endpoints under /api/v1/webstore/",
            "serializers.py contains DRF serializers for webstore API responses",
        ],
        "webstore_scope": [
            "cart model supports guest and authenticated user shopping sessions",
            "cart item model links cart to product variants with quantity tracking",
            "online order model extends base order with shipping and delivery fields",
            "storefront API provides public product listing with tenant branding",
            "checkout flow integrates with payment gateway for online transactions",
            "order tracking provides real-time delivery status updates for customers",
        ],
    }
    logger.debug(
        "Webstore app config: app_purpose=%d, directory_contents=%d",
        len(config["app_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_webstore_structure_config() -> dict:
    """Return webstore structure configuration.

    Documents the webstore app file structure, including apps.py,
    models.py, admin.py, and urls.py placeholders with their
    planned content and conventions.

    SubPhase-01, Group-F, Task 75.

    Returns:
        dict: Configuration with *structure_documented* flag,
              *app_config_details* list, *model_placeholders* list,
              and *admin_url_details* list.
    """
    config: dict = {
        "structure_documented": True,
        "app_config_details": [
            "WebstoreConfig AppConfig subclass with name set to apps.webstore",
            "label set to webstore for database table prefix and migrations",
            "verbose_name set to Webstore for human-readable admin display",
            "ready() method connects webstore signals for order notifications",
            "default_auto_field set to BigAutoField for primary key generation",
            "module docstring documents e-commerce storefront and cart management scope",
        ],
        "model_placeholders": [
            "Cart model placeholder with session key, user link, and expiry fields",
            "CartItem model placeholder with cart, product, quantity, and price",
            "OnlineOrder model placeholder extending order with shipping details",
            "placeholder created now with full implementation in Phase-08 subphases",
            "models use TimeStampedModel mixin for created_at and updated_at fields",
            "custom managers provide active cart and pending order querysets",
        ],
        "admin_url_details": [
            "CartAdmin registers Cart model with user and session filters",
            "OnlineOrderAdmin provides inline item editing on order detail page",
            "admin placeholder created now with full registration in later phase",
            "urls.py defines app_name webstore with empty urlpatterns placeholder",
            "webstore URLs included in project urls.py under api/v1/webstore/",
            "planned endpoints include storefront catalog, cart CRUD, and checkout",
        ],
    }
    logger.debug(
        "Webstore structure config: app_config_details=%d, model_placeholders=%d",
        len(config["app_config_details"]),
        len(config["model_placeholders"]),
    )
    return config


def get_webstore_registration_config() -> dict:
    """Return webstore registration configuration.

    Documents the webstore app registration in Django settings,
    including placement in TENANT_APPS for per-tenant webstore data,
    app ordering conventions, and e-commerce feature flags.

    SubPhase-01, Group-F, Task 76.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *ecommerce_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "webstore app registered as apps.webstore in TENANT_APPS setting",
            "registration ensures webstore tables created in each tenant schema",
            "AppConfig path apps.webstore.apps.WebstoreConfig used for explicit config",
            "webstore app listed after accounting as the last tenant app in ordering",
            "settings file located at backend/config/settings/base.py",
            "webstore also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "webstore app placed in TENANT_APPS for per-tenant storefront isolation",
            "each tenant schema gets its own webstore tables for data separation",
            "shared storefront themes handled via public schema configuration",
            "TENANT_APPS ordering places webstore after accounting as last entry",
            "adding webstore to TENANT_APPS requires running migrate_schemas",
        ],
        "ecommerce_settings": [
            "WEBSTORE_ENABLED toggle for enabling e-commerce storefront per tenant",
            "WEBSTORE_CART_EXPIRY_HOURS timeout for abandoned cart cleanup",
            "WEBSTORE_CHECKOUT_GUEST_ALLOWED toggle for guest checkout support",
            "WEBSTORE_PAYMENT_GATEWAY configurable payment processor integration",
            "WEBSTORE_SHIPPING_METHODS list of enabled delivery method options",
            "WEBSTORE_STOREFRONT_THEME configurable theme for tenant branding",
        ],
    }
    logger.debug(
        "Webstore registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_reports_app_config() -> dict:
    """Return reports app configuration.

    Documents the reports application directory and purpose, including
    its role as the home for analytics dashboards, data aggregation,
    and business intelligence reporting within the multi-tenant POS system.

    SubPhase-01, Group-F, Task 77.

    Returns:
        dict: Configuration with *app_documented* flag,
              *app_purpose* list, *directory_contents* list,
              and *reports_scope* list.
    """
    config: dict = {
        "app_documented": True,
        "app_purpose": [
            "reports app located at backend/apps/reports/ for analytics and reporting",
            "houses report models including Report, ReportSchedule, and Dashboard",
            "provides data aggregation and business intelligence report generation",
            "contains analytics logic for sales, inventory, and financial summaries",
            "serves as the integration point for all business modules via read queries",
            "holds report-related signals for schedule triggers and export logging",
        ],
        "directory_contents": [
            "__init__.py marks reports as a Python package with app docstring",
            "apps.py contains ReportsConfig with metadata and ready() hook",
            "models.py holds Report, ReportSchedule, and Dashboard definitions",
            "admin.py registers report models with custom admin classes",
            "urls.py defines report endpoints under /api/v1/reports/",
            "serializers.py contains DRF serializers for report API responses",
        ],
        "reports_scope": [
            "sales reports with daily, weekly, and monthly revenue summaries",
            "inventory reports for stock levels, movement history, and valuation",
            "financial reports including profit and loss and balance sheet views",
            "customer analytics for purchase patterns and loyalty tier distribution",
            "employee performance reports for sales targets and attendance tracking",
            "report export in PDF, CSV, and Excel formats for offline analysis",
        ],
    }
    logger.debug(
        "Reports app config: app_purpose=%d, directory_contents=%d",
        len(config["app_purpose"]),
        len(config["directory_contents"]),
    )
    return config


def get_reports_registration_config() -> dict:
    """Return reports registration configuration.

    Documents the reports app registration in Django settings,
    including placement in TENANT_APPS for per-tenant report data,
    app ordering conventions, and reporting feature flags.

    SubPhase-01, Group-F, Task 78.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *reporting_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "reports app registered as apps.reports in TENANT_APPS setting",
            "registration ensures report tables created in each tenant schema",
            "AppConfig path apps.reports.apps.ReportsConfig used for explicit config",
            "reports app listed after webstore as the final tenant app in ordering",
            "settings file located at backend/config/settings/base.py",
            "reports also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "reports app placed in TENANT_APPS for per-tenant analytics isolation",
            "each tenant schema gets its own report tables for data separation",
            "shared report templates available via public schema seed configuration",
            "TENANT_APPS ordering places reports last as it reads from all modules",
            "adding reports to TENANT_APPS requires running migrate_schemas",
        ],
        "reporting_settings": [
            "REPORTS_CACHE_TIMEOUT seconds for report data caching duration",
            "REPORTS_EXPORT_FORMATS list of enabled export format options",
            "REPORTS_SCHEDULE_ENABLED toggle for automated report generation",
            "REPORTS_MAX_ROWS_PER_EXPORT limit for exported report row count",
            "REPORTS_DASHBOARD_REFRESH_INTERVAL seconds for live dashboard updates",
            "REPORTS_RETENTION_DAYS duration for keeping generated report files",
        ],
    }
    logger.debug(
        "Reports registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-G: Integration & Configuration – Tasks 79-84 (Integrations & URLs)
# ---------------------------------------------------------------------------


def get_integrations_app_config() -> dict:
    """Return integrations app configuration.

    Documents creating the integrations app at backend/apps/integrations
    for external service integration including payment gateways, shipping
    providers, SMS, and email services.

    SubPhase-01, Group-G, Task 79.

    Returns:
        dict: Configuration with *app_documented* flag,
              *app_details* list, *purpose_details* list,
              and *directory_details* list.
    """
    config: dict = {
        "app_documented": True,
        "app_details": [
            "integrations app created at backend/apps/integrations directory",
            "app handles all external third-party service connections",
            "python manage.py startapp integrations apps/integrations creates scaffold",
            "app registered with dotted path apps.integrations in Django settings",
            "IntegrationsConfig defined in apps/integrations/apps.py as AppConfig",
            "app follows same structure conventions as other LankaCommerce apps",
        ],
        "purpose_details": [
            "centralizes all external service integrations in one app",
            "payment gateway integrations for card and mobile payments",
            "shipping provider integrations for delivery tracking and rates",
            "SMS service integrations for order notifications and OTP",
            "email service integrations for transactional and marketing emails",
            "webhook handling for inbound events from third-party services",
        ],
        "directory_details": [
            "__init__.py marks integrations as a Python package",
            "apps.py contains IntegrationsConfig with app metadata",
            "models.py defines integration-related database models",
            "admin.py registers integration models with Django admin",
            "urls.py defines URL patterns for integration endpoints",
            "tests/ directory contains unit and integration test modules",
        ],
    }
    logger.debug(
        "Integrations app config: app_details=%d, purpose_details=%d",
        len(config["app_details"]),
        len(config["purpose_details"]),
    )
    return config


def get_integrations_structure_config() -> dict:
    """Return integrations structure configuration.

    Documents the internal structure of the integrations app including
    IntegrationsConfig AppConfig, model placeholders, admin registration,
    and URL pattern definitions.

    SubPhase-01, Group-G, Task 80.

    Returns:
        dict: Configuration with *structure_documented* flag,
              *app_config_details* list, *model_placeholders* list,
              and *admin_url_details* list.
    """
    config: dict = {
        "structure_documented": True,
        "app_config_details": [
            "IntegrationsConfig extends django.apps.AppConfig base class",
            "name attribute set to apps.integrations for dotted module path",
            "label attribute set to integrations for database table prefix",
            "verbose_name set to Integrations for admin display purposes",
            "ready method used to import signal handlers on app startup",
            "default_auto_field set to django.db.models.BigAutoField globally",
        ],
        "model_placeholders": [
            "ExternalService model stores third-party service configurations",
            "APICredential model holds encrypted API keys and secrets",
            "WebhookEndpoint model defines inbound webhook URL registrations",
            "IntegrationLog model records all external API call attempts",
            "ServiceProvider model categorizes integration provider types",
            "SyncSchedule model manages periodic data synchronization tasks",
        ],
        "admin_url_details": [
            "admin.py registers ExternalService with custom list display",
            "admin.py registers APICredential with masked secret fields",
            "admin.py registers WebhookEndpoint with URL validation",
            "urls.py defines app_name as integrations for URL namespacing",
            "urls.py includes webhook callback endpoint patterns",
            "urls.py provides health-check endpoint for service status",
        ],
    }
    logger.debug(
        "Integrations structure config: app_config_details=%d, model_placeholders=%d",
        len(config["app_config_details"]),
        len(config["model_placeholders"]),
    )
    return config


def get_integrations_registration_config() -> dict:
    """Return integrations registration configuration.

    Documents registering the integrations app in TENANT_APPS for
    per-tenant integration isolation and related settings.

    SubPhase-01, Group-G, Task 81.

    Returns:
        dict: Configuration with *registration_documented* flag,
              *registration_details* list, *tenant_apps_placement* list,
              and *integration_settings* list.
    """
    config: dict = {
        "registration_documented": True,
        "registration_details": [
            "integrations app registered as apps.integrations in TENANT_APPS",
            "registration ensures integration tables exist in tenant schemas",
            "AppConfig path apps.integrations.apps.IntegrationsConfig used explicitly",
            "integrations placed after reports in TENANT_APPS ordering",
            "settings file located at backend/config/settings/base.py",
            "integrations also listed in INSTALLED_APPS for migration discovery",
        ],
        "tenant_apps_placement": [
            "TENANT_APPS contains apps whose tables exist in tenant schemas only",
            "integrations in TENANT_APPS enables per-tenant API credential isolation",
            "each tenant schema gets its own integration configuration tables",
            "shared integration templates available via public schema seed data",
            "TENANT_APPS ordering places integrations after reports app entry",
            "adding integrations to TENANT_APPS requires running migrate_schemas",
        ],
        "integration_settings": [
            "INTEGRATIONS_TIMEOUT seconds for external API request timeout",
            "INTEGRATIONS_RETRY_COUNT maximum retry attempts for failed requests",
            "INTEGRATIONS_WEBHOOK_SECRET shared secret for webhook verification",
            "INTEGRATIONS_LOG_LEVEL logging verbosity for integration calls",
            "INTEGRATIONS_CACHE_TTL seconds for caching external service responses",
            "INTEGRATIONS_RATE_LIMIT maximum requests per minute per service",
        ],
    }
    logger.debug(
        "Integrations registration config: registration_details=%d, tenant_apps_placement=%d",
        len(config["registration_details"]),
        len(config["tenant_apps_placement"]),
    )
    return config


def get_main_urls_router_config() -> dict:
    """Return main urls.py router configuration.

    Documents the main URL configuration at config/urls.py including
    Django admin URL setup and API namespace routing.

    SubPhase-01, Group-G, Task 82.

    Returns:
        dict: Configuration with *router_documented* flag,
              *router_details* list, *admin_url_details* list,
              and *api_namespace_details* list.
    """
    config: dict = {
        "router_documented": True,
        "router_details": [
            "main urls.py located at backend/config/urls.py as ROOT_URLCONF",
            "ROOT_URLCONF setting points to config.urls in Django settings",
            "urlpatterns list defines top-level URL routing for the project",
            "admin URLs mounted at admin/ path for Django admin interface",
            "API URLs mounted at api/ path prefix for all REST endpoints",
            "static and media URL patterns added in development mode only",
        ],
        "admin_url_details": [
            "admin.site.urls included at path admin/ for admin interface",
            "admin site title customized to LankaCommerce Administration",
            "admin site header set to LankaCommerce Cloud for branding",
            "admin index title configured for the dashboard landing page",
            "admin autodiscover loads admin.py from all installed apps",
            "admin URL protected by staff_member_required middleware",
        ],
        "api_namespace_details": [
            "api/ prefix groups all REST API endpoints under one path",
            "versioned routing uses api/v1/ for current API version",
            "DRF DefaultRouter auto-generates viewset URL patterns",
            "app_name set to api for top-level API namespace resolution",
            "include function maps app URL modules to sub-paths",
            "namespace parameter enables reverse URL resolution per app",
        ],
    }
    logger.debug(
        "Main urls router config: router_details=%d, admin_url_details=%d",
        len(config["router_details"]),
        len(config["admin_url_details"]),
    )
    return config


def get_app_urls_inclusion_config() -> dict:
    """Return app URLs inclusion configuration.

    Documents including all application URL modules in the main
    URL configuration covering tenants, users, core, and module apps.

    SubPhase-01, Group-G, Task 83.

    Returns:
        dict: Configuration with *inclusion_documented* flag,
              *inclusion_details* list, *app_url_patterns* list,
              and *ordering_conventions* list.
    """
    config: dict = {
        "inclusion_documented": True,
        "inclusion_details": [
            "all app URLs included via django.urls.include in config/urls.py",
            "tenants app URLs mounted for tenant management endpoints",
            "users app URLs mounted for authentication and profile endpoints",
            "core app URLs mounted for shared utility and health endpoints",
            "module app URLs mounted for products inventory sales and more",
            "each app URL module uses its own app_name for namespacing",
        ],
        "app_url_patterns": [
            "tenants/ path includes apps.tenants.urls for tenant operations",
            "users/ path includes apps.users.urls for user management",
            "core/ path includes apps.core.urls for core utility endpoints",
            "products/ path includes apps.products.urls for product catalog",
            "inventory/ path includes apps.inventory.urls for stock management",
            "sales/ path includes apps.sales.urls for sales transactions",
        ],
        "ordering_conventions": [
            "core infrastructure URLs listed first in urlpatterns order",
            "tenant and user management URLs follow core URL entries",
            "module app URLs listed alphabetically after infrastructure URLs",
            "each include call specifies namespace matching the app_name",
            "consistent trailing slash convention enforced across all patterns",
            "URL pattern naming follows verb-noun convention for clarity",
        ],
    }
    logger.debug(
        "App URLs inclusion config: inclusion_details=%d, app_url_patterns=%d",
        len(config["inclusion_details"]),
        len(config["app_url_patterns"]),
    )
    return config


def get_api_router_config() -> dict:
    """Return API router configuration.

    Documents the API v1 router at /api/v1/ namespace including
    versioning policy and namespace conventions.

    SubPhase-01, Group-G, Task 84.

    Returns:
        dict: Configuration with *router_documented* flag,
              *router_details* list, *versioning_details* list,
              and *namespace_details* list.
    """
    config: dict = {
        "router_documented": True,
        "router_details": [
            "API v1 router mounted at /api/v1/ URL path prefix",
            "router defined in dedicated api/v1/urls.py module",
            "DRF DefaultRouter provides standard CRUD URL patterns",
            "router.register binds viewsets to resource URL prefixes",
            "browsable API enabled in development for easy testing",
            "router URLs included in main config/urls.py via include",
        ],
        "versioning_details": [
            "URL prefix versioning strategy used with /api/v1/ path",
            "v1 is the current and default API version for all clients",
            "adding v2 involves creating api/v2/urls.py with new router",
            "deprecated versions return sunset header with removal date",
            "version negotiation handled by DRF URLPathVersioning class",
            "API changelog documents breaking changes between versions",
        ],
        "namespace_details": [
            "api-v1 namespace assigned to the v1 URL configuration",
            "app_name set to api-v1 in the v1 urls.py module",
            "reverse function uses api-v1:resource-list for URL resolution",
            "namespace prevents URL name collisions across API versions",
            "each app within v1 gets sub-namespace like api-v1:products",
            "URL resolution tested in integration tests for correctness",
        ],
    }
    logger.debug(
        "API router config: router_details=%d, versioning_details=%d",
        len(config["router_details"]),
        len(config["versioning_details"]),
    )
    return config


def get_installed_apps_order_config() -> dict:
    """Return INSTALLED_APPS ordering configuration.

    Documents the ordering strategy for INSTALLED_APPS,
    ensuring shared apps are listed before tenant apps
    to prevent schema misconfiguration issues.

    SubPhase-01, Group-G, Task 85.

    Returns:
        dict: Configuration with ordering_documented flag,
              ordering_details list, shared_before_tenant list,
              and misconfiguration_risks list.
    """
    config: dict = {
        "ordering_documented": True,
        "ordering_details": [
            "INSTALLED_APPS ordering follows shared-before-tenant strategy",
            "django-tenants requires specific ordering for schema creation",
            "django.contrib apps listed first as framework dependencies",
            "third-party packages placed after built-in Django apps",
            "app discovery order determines migration execution sequence",
            "base.py settings file defines canonical INSTALLED_APPS list",
        ],
        "shared_before_tenant": [
            "schema creation order requires shared apps to exist first",
            "public schema tables must be created before tenant schemas",
            "tenant_schemas middleware depends on shared apps being loaded",
            "migration ordering follows INSTALLED_APPS declaration order",
            "prevents missing table errors during tenant provisioning",
            "django-tenants documentation requires shared apps listed first",
        ],
        "misconfiguration_risks": [
            "schema sync failures when shared apps are listed after tenant apps",
            "missing foreign keys if referenced app not yet migrated",
            "migration dependency errors from incorrect app ordering",
            "tenant creation fails when public schema tables are absent",
            "app not found errors if apps not registered in correct order",
            "inconsistent data across schemas due to partial migrations",
        ],
    }
    logger.debug(
        "INSTALLED_APPS order config: ordering_details=%d, shared_before_tenant=%d",
        len(config["ordering_details"]),
        len(config["shared_before_tenant"]),
    )
    return config


def get_shared_apps_config() -> dict:
    """Return SHARED_APPS configuration.

    Documents the SHARED_APPS setting for public schema,
    including tenants app and core shared dependencies
    that exist only in the public schema.

    SubPhase-01, Group-G, Task 86.

    Returns:
        dict: Configuration with shared_apps_documented flag,
              shared_apps_list list, schema_separation list,
              and dependency_details list.
    """
    config: dict = {
        "shared_apps_documented": True,
        "shared_apps_list": [
            "django_tenants included as the multi-tenancy framework app",
            "django.contrib.contenttypes required by tenant framework",
            "django.contrib.auth provides authentication models shared globally",
            "django.contrib.admin enables management interface in public schema",
            "apps.tenants contains Tenant and Domain models for routing",
            "apps.core provides base mixins and utilities available to all",
        ],
        "schema_separation": [
            "shared tables exist in public schema only and are not duplicated",
            "tenant schemas do not duplicate shared tables to save space",
            "content types are shared across all tenants for consistency",
            "auth models reside in public schema for single sign-on support",
            "tenant routing table in public schema maps domains to schemas",
            "shared configuration data stored in public schema tables",
        ],
        "dependency_details": [
            "django_tenants must be first in SHARED_APPS for initialization",
            "contenttypes required by tenant framework for generic relations",
            "auth required for user model and permission management",
            "admin needed for management interface and model registration",
            "tenants app provides Tenant and Domain models for routing",
            "core provides base mixins available to all apps in project",
        ],
    }
    logger.debug(
        "SHARED_APPS config: shared_apps_list=%d, schema_separation=%d",
        len(config["shared_apps_list"]),
        len(config["schema_separation"]),
    )
    return config


def get_tenant_apps_config() -> dict:
    """Return TENANT_APPS configuration.

    Documents the TENANT_APPS setting for tenant schemas,
    including per-tenant apps listed in correct order
    for tenant-specific data isolation.

    SubPhase-01, Group-G, Task 87.

    Returns:
        dict: Configuration with tenant_apps_documented flag,
              tenant_apps_list list, per_tenant_details list,
              and ordering_rationale list.
    """
    config: dict = {
        "tenant_apps_documented": True,
        "tenant_apps_list": [
            "apps.users provides tenant-specific user profiles and roles",
            "apps.products manages product catalog per tenant",
            "apps.inventory tracks stock levels isolated per tenant",
            "apps.sales handles sales transactions within each tenant",
            "apps.customers stores customer data scoped to each tenant",
            "apps.vendors and other modules complete tenant app set",
        ],
        "per_tenant_details": [
            "each tenant schema contains its own set of isolated tables",
            "data isolation between tenants enforced at database level",
            "no cross-tenant data access possible through ORM queries",
            "tenant-specific migrations run independently per schema",
            "new tenant provisioning creates fresh set of all tables",
            "deleting tenant removes its schema and all associated data",
        ],
        "ordering_rationale": [
            "users app listed first as other models reference user foreign keys",
            "products placed before inventory and sales that depend on it",
            "inventory depends on products for stock tracking relationships",
            "sales depends on products and customers for transaction records",
            "customers and vendors follow after core business modules",
            "integrations and reports listed last as they read all other data",
        ],
    }
    logger.debug(
        "TENANT_APPS config: tenant_apps_list=%d, per_tenant_details=%d",
        len(config["tenant_apps_list"]),
        len(config["per_tenant_details"]),
    )
    return config


def get_initial_migrations_config() -> dict:
    """Return initial migrations configuration.

    Documents the initial migration generation scope
    for all apps, ensuring no schema errors occur
    during initial database setup.

    SubPhase-01, Group-G, Task 88.

    Returns:
        dict: Configuration with migrations_documented flag,
              migration_scope list, migration_details list,
              and error_prevention list.
    """
    config: dict = {
        "migrations_documented": True,
        "migration_scope": [
            "makemigrations generates migrations for each app in INSTALLED_APPS",
            "shared apps generate migrations applied to shared public schema",
            "tenant apps generate migrations applied to each tenant schema",
            "migrate_schemas command applies shared schema migrations first",
            "each existing tenant schema gets migrated after shared schema",
            "new tenants run full migration set automatically on creation",
        ],
        "migration_details": [
            "0001_initial.py created in each app migrations directory on first run",
            "migration dependencies reference other app migrations explicitly",
            "RunSQL operations avoided in favor of Django ORM model operations",
            "squashmigrations used periodically to reduce migration file count",
            "migration files committed to version control for reproducibility",
            "CI pipeline runs migrate_schemas to verify no errors in migrations",
        ],
        "error_prevention": [
            "test migrations with empty database before production deployment",
            "verify no circular dependencies exist between app migrations",
            "check migration ordering matches INSTALLED_APPS declaration order",
            "run showmigrations to display full migration dependency graph",
            "use --check flag to verify no pending migrations remain ungenerated",
            "automated tests include migrate_schemas in test setup procedure",
        ],
    }
    logger.debug(
        "Initial migrations config: migration_scope=%d, migration_details=%d",
        len(config["migration_scope"]),
        len(config["migration_details"]),
    )
    return config


def get_app_structure_verification_config() -> dict:
    """Return app structure verification configuration.

    Documents verification checks ensuring all apps
    are present, registered, and structurally consistent
    across the project.

    SubPhase-01, Group-G, Task 89.

    Returns:
        dict: Configuration with verification_documented flag,
              verification_checks list, registration_validation list,
              and structural_consistency list.
    """
    config: dict = {
        "verification_documented": True,
        "verification_checks": [
            "verify all expected apps exist in backend/apps directory structure",
            "check each app has __init__.py and apps.py files present",
            "confirm AppConfig.name matches the app directory path convention",
            "validate all apps listed in SHARED_APPS or TENANT_APPS settings",
            "ensure no app appears in both SHARED_APPS and TENANT_APPS lists",
            "run django check --deploy for production deployment readiness",
        ],
        "registration_validation": [
            "compare INSTALLED_APPS against apps/ directory listing for gaps",
            "verify each AppConfig.label is unique across all registered apps",
            "check default_auto_field set consistently to BigAutoField everywhere",
            "validate ready() method exists only when signal registration needed",
            "confirm verbose_name set for admin display in each AppConfig",
            "ensure app ordering matches documented convention in settings",
        ],
        "structural_consistency": [
            "each app follows standard files: models.py, admin.py, urls.py, views.py",
            "tests directory present in every app for test organization",
            "urls.py defines app_name matching the app label for namespacing",
            "migrations directory with __init__.py exists in all app directories",
            "conftest.py or fixtures directory provides test data for each app",
            "README.md documents app purpose and module scope in every app",
        ],
    }
    logger.debug(
        "App structure verification config: verification_checks=%d, registration_validation=%d",
        len(config["verification_checks"]),
        len(config["registration_validation"]),
    )
    return config


def get_apps_documentation_config() -> dict:
    """Return apps documentation configuration.

    Documents the creation of comprehensive apps documentation
    listing all apps and their responsibilities along with
    maintenance guidelines for keeping documentation current.

    SubPhase-01, Group-G, Task 90.

    Returns:
        dict: Configuration with *documentation_completed* flag,
              *app_overview* list, *documentation_details* list,
              and *maintenance_guidelines* list.
    """
    config: dict = {
        "documentation_completed": True,
        "app_overview": [
            "core app provides base models mixins and shared utilities",
            "tenants app manages multi-tenant schema routing configuration",
            "users app handles authentication and user profile management",
            "products inventory and sales apps cover commerce workflows",
            "customers and vendors apps provide relationship management",
            "integrations reports and webstore handle external and analytics features",
        ],
        "documentation_details": [
            "README.md in each app describes purpose and module scope",
            "docs/architecture/apps-structure.md lists full app inventory",
            "each app section notes models admin URLs and dependencies",
            "API endpoint documentation references the app URL namespace",
            "test coverage expectations documented per app module",
            "changelog entries track significant structural changes",
        ],
        "maintenance_guidelines": [
            "update apps-structure.md when adding or removing any app",
            "review README.md after each phase to reflect new features",
            "keep INSTALLED_APPS documentation in sync with settings file",
            "document new dependencies between apps in architecture docs",
            "run documentation linter to verify markdown format consistency",
            "include documentation updates in the same commit as code changes",
        ],
    }
    logger.debug(
        "Apps documentation config: app_overview=%d, documentation_details=%d",
        len(config["app_overview"]),
        len(config["documentation_details"]),
    )
    return config


def get_initial_commit_config() -> dict:
    """Return initial commit configuration.

    Documents the initial commit for SubPhase-01 including
    commit scope covering app structure and settings updates
    and commit message conventions.

    SubPhase-01, Group-G, Task 91.

    Returns:
        dict: Configuration with *commit_documented* flag,
              *commit_scope* list, *commit_message_details* list,
              and *version_control_details* list.
    """
    config: dict = {
        "commit_documented": True,
        "commit_scope": [
            "all app directories created under backend/apps with structure files",
            "INSTALLED_APPS and SHARED_APPS and TENANT_APPS settings configured",
            "initial migrations generated for all registered applications",
            "URL routing configured with admin and API v1 namespaces",
            "apps documentation and README files created for each module",
            "test files verifying app structure and registration correctness",
        ],
        "commit_message_details": [
            "conventional commit format feat(apps): add SubPhase-01 app structure",
            "body describes apps created and settings configured",
            "footer references SubPhase-01 task range Tasks 01-92",
            "breaking change noted if migration reset required for existing databases",
            "co-authored-by included when pair programming on structure setup",
            "commit signed with GPG key per project security policy",
        ],
        "version_control_details": [
            "feature branch named feature/phase-03-subphase-01-apps-structure",
            "all files staged with git add including migrations and docs",
            "pre-commit hooks run linting and formatting checks automatically",
            "branch protection requires pull request review before merging",
            "CI pipeline triggered on push to verify tests pass on commit",
            "tag applied after merge to mark SubPhase-01 completion milestone",
        ],
    }
    logger.debug(
        "Initial commit config: commit_scope=%d, commit_message_details=%d",
        len(config["commit_scope"]),
        len(config["commit_message_details"]),
    )
    return config


def get_server_start_verification_config() -> dict:
    """Return server start verification configuration.

    Documents the verification steps for confirming the
    Django server starts cleanly after SubPhase-01 app
    structure setup with no errors.

    SubPhase-01, Group-G, Task 92.

    Returns:
        dict: Configuration with *verification_documented* flag,
              *verification_steps* list, *acceptance_criteria* list,
              and *troubleshooting_details* list.
    """
    config: dict = {
        "verification_documented": True,
        "verification_steps": [
            "run python manage.py check to verify no system check errors",
            "run python manage.py migrate_schemas to apply all pending migrations",
            "start development server with python manage.py runserver command",
            "confirm server binds to localhost port 8000 without exceptions",
            "verify admin interface accessible at /admin/ URL path",
            "check API root responds at /api/v1/ with browsable interface",
        ],
        "acceptance_criteria": [
            "zero system check warnings or errors on startup output",
            "all migrations applied successfully across public and tenant schemas",
            "no import errors when loading any registered app module",
            "static files collected without missing file warnings",
            "logging configuration outputs to console without format errors",
            "health check endpoint returns 200 OK status within timeout",
        ],
        "troubleshooting_details": [
            "ImportError indicates missing __init__.py or circular import",
            "AppRegistryNotReady means INSTALLED_APPS ordering is incorrect",
            "ProgrammingError suggests migrations not applied to target schema",
            "ModuleNotFoundError points to wrong AppConfig.name in apps.py",
            "OperationalError on startup indicates database connection failure",
            "template syntax errors require checking TEMPLATES DIRS configuration",
        ],
    }
    logger.debug(
        "Server start verification config: verification_steps=%d, acceptance_criteria=%d",
        len(config["verification_steps"]),
        len(config["acceptance_criteria"]),
    )
    return config
