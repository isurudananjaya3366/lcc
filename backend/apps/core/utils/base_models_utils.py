"""
Base models utilities for LankaCommerce Cloud core infrastructure.

SubPhase-03, Group-A Tasks 01-14 and Group-B Tasks 15-28 and Group-C Tasks 29-44 and Group-D Tasks 45-58 and Group-E Tasks 59-74 and Group-F Tasks 75-94.

Provides base model and manager configuration helpers used by the
core application for documenting Django base models and managers setup.

Functions:
    get_models_directory_config()      -- Models directory config (Task 01).
    get_models_init_config()           -- Models __init__.py config (Task 02).
    get_base_model_file_config()       -- Base model file config (Task 03).
    get_django_models_import_config()  -- Django models import config (Task 04).
    get_managers_directory_config()    -- Managers directory config (Task 05).
    get_managers_init_config()         -- Managers __init__.py config (Task 06).
    get_base_manager_config()          -- BaseManager config (Task 07).
    get_base_queryset_config()         -- BaseQuerySet config (Task 08).
    get_mixins_directory_config()      -- Mixins directory config (Task 09).
    get_mixins_init_config()           -- Mixins __init__.py config (Task 10).
    get_model_naming_convention_config() -- Model naming convention config (Task 11).
    get_field_naming_convention_config() -- Field naming convention config (Task 12).
    get_model_documentation_template_config() -- Model documentation template config (Task 13).
    get_base_structure_verification_config() -- Base structure verification config (Task 14).
    get_timestamped_file_config()      -- Timestamped file config (Task 15).
    get_timestamped_model_config()     -- TimeStampedModel config (Task 16).
    get_created_at_field_config()      -- created_at field config (Task 17).
    get_updated_at_field_config()      -- updated_at field config (Task 18).
    get_meta_abstract_config()         -- Meta abstract config (Task 19).
    get_ordering_config()              -- Ordering config (Task 20).
    get_timestamped_manager_config()   -- TimeStampedManager config (Task 21).
    get_recent_method_config()         -- recent() method config (Task 22).
    get_today_method_config()          -- today() method config (Task 23).
    get_this_week_method_config()      -- this_week() method config (Task 24).
    get_this_month_method_config()     -- this_month() method config (Task 25).
    get_timestamped_export_config()    -- Timestamped export config (Task 26).
    get_timestamped_tests_config()     -- Timestamped tests config (Task 27).
    get_timestamped_docs_config()      -- Timestamped docs config (Task 28).
    get_soft_delete_file_config()      -- Soft delete file config (Task 29).
    get_soft_delete_model_config()     -- SoftDeleteModel config (Task 30).
    get_is_deleted_field_config()      -- is_deleted field config (Task 31).
    get_deleted_at_field_config()      -- deleted_at field config (Task 32).
    get_soft_delete_manager_config()   -- SoftDeleteManager config (Task 33).
    get_queryset_override_config()     -- Queryset override config (Task 34).
    get_all_with_deleted_manager_config() -- all_with_deleted manager config (Task 35).
    get_deleted_only_manager_config()  -- deleted_only manager config (Task 36).
    get_soft_delete_method_config()    -- soft_delete() method config (Task 37).
    get_restore_method_config()        -- restore() method config (Task 38).
    get_hard_delete_method_config()    -- hard_delete() method config (Task 39).
    get_delete_override_config()       -- delete() override config (Task 40).
    get_is_deleted_index_config()      -- is_deleted index config (Task 41).
    get_soft_delete_export_config()    -- Soft delete export config (Task 42).
    get_soft_delete_tests_config()     -- Soft delete tests config (Task 43).
    get_soft_delete_docs_config()      -- Soft delete docs config (Task 44).
    get_audit_file_config()            -- Audit file config (Task 45).
    get_audit_model_config()           -- AuditModel config (Task 46).
    get_created_by_field_config()      -- created_by field config (Task 47).
    get_updated_by_field_config()      -- updated_by field config (Task 48).
    get_on_delete_config()             -- on_delete config (Task 49).
    get_related_name_pattern_config()  -- related_name pattern config (Task 50).
    get_audit_manager_config()         -- AuditManager config (Task 51).
    get_created_by_user_filter_config() -- created_by_user() filter config (Task 52).
    get_updated_by_user_filter_config() -- updated_by_user() filter config (Task 53).
    get_audit_mixin_config()           -- AuditMixin config (Task 54).
    get_set_created_by_method_config() -- set_created_by method config (Task 55).
    get_set_updated_by_method_config() -- set_updated_by method config (Task 56).
    get_audit_tests_config()           -- Audit tests config (Task 57).
    get_audit_docs_config()            -- Audit docs config (Task 58).
    get_uuid_model_file_config()       -- UUID model file config (Task 59).
    get_uuid_model_class_config()      -- UUIDModel class config (Task 60).
    get_uuid_field_config()            -- UUID field config (Task 61).
    get_uuid_default_config()          -- UUID default config (Task 62).
    get_uuid_editable_config()         -- UUID editable config (Task 63).
    get_uuid_tests_config()            -- UUID tests config (Task 64).
    get_tenant_scoped_file_config()    -- Tenant scoped file config (Task 65).
    get_tenant_scoped_model_config()   -- TenantScopedModel config (Task 66).
    get_tenant_scoped_manager_config() -- TenantScopedManager config (Task 67).
    get_get_queryset_override_config() -- get_queryset override config (Task 68).
    get_django_tenants_integration_config() -- django-tenants integration config (Task 69).
    get_for_tenant_method_config()     -- for_tenant() method config (Task 70).
    get_tenant_field_config()          -- tenant field config (Task 71).
    get_tenant_scoped_tests_config()   -- TenantScoped tests config (Task 72).
    get_uuid_tenant_export_config()    -- UUID & TenantScoped export config (Task 73).
    get_uuid_tenant_docs_config()      -- UUID & TenantScoped docs config (Task 74).
    get_validators_file_config()       -- Validators file config (Task 75).
    get_phone_number_validator_config() -- PhoneNumberValidator config (Task 76).
    get_nic_validator_config()         -- NICValidator config (Task 77).
    get_brn_validator_config()         -- BRNValidator config (Task 78).
    get_positive_decimal_validator_config() -- PositiveDecimalValidator config (Task 79).
    get_percentage_validator_config()  -- PercentageValidator config (Task 80).
    get_fields_file_config()           -- Fields file config (Task 81).
    get_money_field_config()           -- MoneyField config (Task 82).
    get_percentage_field_config()      -- PercentageField config (Task 83).
    get_phone_number_field_config()    -- PhoneNumberField config (Task 84).
    get_slug_field_config()            -- SlugField with auto config (Task 85).
    get_utils_file_config()            -- Utils file config (Task 86).
    get_generate_unique_code_config()  -- generate_unique_code config (Task 87).
    get_current_tenant_config()        -- get_current_tenant config (Task 88).
    get_current_user_config()          -- get_current_user config (Task 89).
    get_validators_export_config()     -- Validators export config (Task 90).
    get_fields_export_config()         -- Fields export config (Task 91).
    get_initial_migration_config()     -- Initial migration config (Task 92).
    get_full_test_suite_config()       -- Full test suite config (Task 93).
    get_base_models_documentation_config() -- Base models documentation config (Task 94).

See also:
    - apps.core.utils.__init__  -- public re-exports
    - docs/architecture/base-models.md
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Group-A: Base Model Setup – Tasks 01-07 (Directory Structure)
# ---------------------------------------------------------------------------


def get_models_directory_config() -> dict:
    """Return models directory configuration.

    SubPhase-03, Group-A, Task 01.
    """
    config: dict = {
        "configured": True,
        "directory_details": [
            "models directory created at backend/apps/core/models path",
            "directory serves as package root for all core model modules",
            "base model classes and mixins organized within this directory",
            "tenant-aware model definitions reside in dedicated submodules",
            "directory structure follows Django best practices for large apps",
            "models directory replaces single models.py for better organization",
        ],
        "purpose_details": [
            "shared base models provide common fields across all apps",
            "abstract model classes enforce consistent field naming conventions",
            "timestamp mixins and soft delete patterns defined as base classes",
            "tenant-aware base model handles schema isolation transparently",
            "base models reduce code duplication across twelve application modules",
            "purpose documentation helps new developers understand model hierarchy",
        ],
        "layout_details": [
            "base.py contains the primary BaseModel abstract class definition",
            "__init__.py exports all public model classes for easy importing",
            "mixins.py holds reusable model mixin classes like TimestampMixin",
            "directory supports adding new model modules without import changes",
            "file naming follows lowercase with underscores Python convention",
            "layout matches Django community patterns for scalable model packages",
        ],
    }
    logger.debug(
        "Models directory config: directory_details=%d, purpose_details=%d",
        len(config["directory_details"]),
        len(config["purpose_details"]),
    )
    return config


def get_models_init_config() -> dict:
    """Return models __init__.py configuration.

    SubPhase-03, Group-A, Task 02.
    """
    config: dict = {
        "configured": True,
        "init_details": [
            "__init__.py created inside the models directory package",
            "init module imports BaseModel from the base submodule",
            "all public model classes re-exported for convenient access",
            "lazy imports used where possible to avoid circular dependencies",
            "__all__ list explicitly declares the public API of the package",
            "init file follows Django convention for model package initialization",
        ],
        "discovery_details": [
            "Django model discovery relies on models package being importable",
            "app registry scans models __init__.py during application startup",
            "migration framework detects model classes through package imports",
            "admin autodiscover finds models registered in admin via init exports",
            "serializer modules reference models through the package namespace",
            "test fixtures resolve model references using the app label and name",
        ],
        "export_details": [
            "BaseModel exported as the primary abstract class for inheritance",
            "TimestampMixin exported for adding created and updated fields",
            "SoftDeleteMixin exported for logical deletion support in models",
            "explicit exports prevent accidental exposure of internal helpers",
            "wildcard import from models package returns only __all__ members",
            "export list maintained alphabetically for easy scanning and diffs",
        ],
    }
    logger.debug(
        "Models init config: init_details=%d, discovery_details=%d",
        len(config["init_details"]),
        len(config["discovery_details"]),
    )
    return config


def get_base_model_file_config() -> dict:
    """Return base model file configuration.

    SubPhase-03, Group-A, Task 03.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "base.py file created inside the models directory package",
            "file contains the BaseModel abstract class used by all apps",
            "module docstring documents the purpose and usage of BaseModel",
            "file imports Django models module for field and class definitions",
            "base.py kept minimal to avoid bloating the foundational module",
            "file follows single-responsibility principle for base model logic",
        ],
        "foundation_details": [
            "BaseModel inherits from django.db.models.Model as abstract class",
            "Meta class sets abstract equals True to prevent table creation",
            "common fields like uuid and is_active defined on the base model",
            "created_at and updated_at timestamps added via mixin composition",
            "string representation method returns a human-readable identifier",
            "foundation class tested with unit tests to verify field presence",
        ],
        "organization_details": [
            "base.py placed at models/base.py within the core application",
            "other apps import BaseModel from apps.core.models.base module",
            "separation of base model from mixins keeps concerns distinct",
            "organization allows independent evolution of base and mixin logic",
            "clear file structure aids code review and onboarding processes",
            "organization documented in the project architecture guide",
        ],
    }
    logger.debug(
        "Base model file config: file_details=%d, foundation_details=%d",
        len(config["file_details"]),
        len(config["foundation_details"]),
    )
    return config


def get_django_models_import_config() -> dict:
    """Return Django models import configuration.

    SubPhase-03, Group-A, Task 04.
    """
    config: dict = {
        "configured": True,
        "import_details": [
            "from django.db import models used as the standard import form",
            "models module provides Model base class and all field types",
            "import placed at the top of each model file per PEP 8 convention",
            "django.db.models supplies CharField IntegerField and ForeignKey",
            "models import enables access to Manager and QuerySet base classes",
            "consistent import style enforced across all application modules",
        ],
        "usage_details": [
            "models.Model serves as the root class for all Django ORM objects",
            "models.CharField and models.TextField define string-based columns",
            "models.ForeignKey and models.ManyToManyField handle relationships",
            "models.Manager extended to create custom manager implementations",
            "models.Q and models.F used for complex queries and expressions",
            "usage patterns documented in project coding style guidelines",
        ],
        "dependency_details": [
            "django.db.models depends on the configured database backend",
            "database engine selected via DATABASES setting in Django config",
            "PostgreSQL backend required for tenant schema isolation support",
            "model field types map to database column types automatically",
            "dependency on Django ORM ensures migration auto-generation works",
            "third-party fields like django-money integrate through models API",
        ],
    }
    logger.debug(
        "Django models import config: import_details=%d, usage_details=%d",
        len(config["import_details"]),
        len(config["usage_details"]),
    )
    return config


def get_managers_directory_config() -> dict:
    """Return managers directory configuration.

    SubPhase-03, Group-A, Task 05.
    """
    config: dict = {
        "configured": True,
        "folder_details": [
            "managers directory created at backend/apps/core/managers path",
            "directory holds custom manager and queryset class definitions",
            "folder organized as a Python package with __init__.py module",
            "base manager module placed inside the managers directory package",
            "additional manager modules can be added without structural changes",
            "folder naming follows Django conventions for manager organization",
        ],
        "manager_purpose_details": [
            "managers encapsulate reusable query logic for model instances",
            "custom managers override default objects manager on model classes",
            "tenant-aware manager filters querysets by current schema context",
            "soft-delete manager excludes logically deleted rows by default",
            "manager classes promote DRY principles across application queries",
            "purpose of each manager documented in its module-level docstring",
        ],
        "structure_details": [
            "base.py contains the BaseManager class used across all apps",
            "__init__.py exports all public manager classes for importing",
            "queryset.py may hold custom QuerySet classes paired with managers",
            "structure mirrors the models directory for consistency",
            "each manager file contains one primary class and its helpers",
            "structure supports scalable addition of domain-specific managers",
        ],
    }
    logger.debug(
        "Managers directory config: folder_details=%d, manager_purpose_details=%d",
        len(config["folder_details"]),
        len(config["manager_purpose_details"]),
    )
    return config


def get_managers_init_config() -> dict:
    """Return managers __init__.py configuration.

    SubPhase-03, Group-A, Task 06.
    """
    config: dict = {
        "configured": True,
        "package_details": [
            "__init__.py created inside the managers directory package",
            "init module marks the managers folder as an importable package",
            "BaseManager imported and re-exported from the package namespace",
            "future manager classes added to init as the package grows",
            "__all__ list declares the public API of the managers package",
            "package init kept concise to minimize import side effects",
        ],
        "module_details": [
            "base module contains the BaseManager class definition",
            "each module in the package focuses on a single manager concern",
            "module naming uses lowercase with underscores per Python standards",
            "module docstrings describe the manager classes they contain",
            "modules tested independently to verify queryset behavior",
            "module dependencies explicitly imported at the top of each file",
        ],
        "registration_details": [
            "managers registered on model classes via objects attribute assignment",
            "default manager set as the first manager declared on the model",
            "Meta.default_manager_name overrides default manager selection if needed",
            "registration order affects admin and serializer default querysets",
            "custom managers registered alongside Django built-in managers",
            "registration patterns documented for consistency across all apps",
        ],
    }
    logger.debug(
        "Managers init config: package_details=%d, module_details=%d",
        len(config["package_details"]),
        len(config["module_details"]),
    )
    return config


def get_base_manager_config() -> dict:
    """Return BaseManager class configuration.

    SubPhase-03, Group-A, Task 07.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "BaseManager inherits from django.db.models.Manager class",
            "BaseManager provides default queryset filtering for all models",
            "get_queryset method overridden to apply global query conditions",
            "BaseManager excludes soft-deleted records from default queries",
            "manager class defined in apps/core/managers/base.py module",
            "BaseManager serves as the parent for all app-specific managers",
        ],
        "queryset_details": [
            "custom queryset returned by get_queryset includes active filter",
            "queryset chain methods like alive and deleted added for convenience",
            "queryset supports tenant-aware filtering when multi-tenancy enabled",
            "annotation and aggregation helpers provided on the base queryset",
            "queryset class paired with manager using from_queryset pattern",
            "queryset optimizations documented for large dataset operations",
        ],
        "integration_details": [
            "BaseManager assigned as objects manager on BaseModel abstract class",
            "all concrete models inherit the BaseManager through BaseModel",
            "admin classes use the default manager for changelist queries",
            "DRF viewsets respect the custom manager queryset automatically",
            "migration framework ignores managers and does not serialize them",
            "integration tested to ensure manager and model work together",
        ],
    }
    logger.debug(
        "BaseManager config: manager_details=%d, queryset_details=%d",
        len(config["manager_details"]),
        len(config["queryset_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-A: Base Model Setup – Tasks 08-14 (QuerySet, Mixins & Standards)
# ---------------------------------------------------------------------------


def get_base_queryset_config() -> dict:
    """Return BaseQuerySet configuration.

    SubPhase-03, Group-A, Task 08.
    """
    config: dict = {
        "configured": True,
        "queryset_details": [
            "BaseQuerySet extends django.db.models.QuerySet for custom methods",
            "provides alive method to filter only non-deleted records",
            "provides deleted method to retrieve soft-deleted records only",
            "supports chaining with standard Django queryset operations",
            "includes tenant-scoped filtering for multi-tenant environments",
            "BaseQuerySet defined in apps/core/querysets/base.py module",
        ],
        "helper_details": [
            "active helper returns records where is_active flag is True",
            "by_tenant helper filters records belonging to a specific tenant",
            "recent helper orders records by created_at descending",
            "search helper performs case-insensitive lookup across fields",
            "bulk_soft_delete helper marks multiple records as deleted",
            "with_related helper prefetches common related objects",
        ],
        "extension_details": [
            "app-specific querysets inherit from BaseQuerySet class",
            "custom queryset methods registered via QuerySet.as_manager pattern",
            "queryset extensions documented in querysets directory README",
            "type hints added to all queryset return values for IDE support",
            "queryset tests verify chaining behavior across all helpers",
            "extension points allow third-party queryset method injection",
        ],
    }
    logger.debug(
        "BaseQuerySet config: queryset_details=%d, helper_details=%d",
        len(config["queryset_details"]),
        len(config["helper_details"]),
    )
    return config


def get_mixins_directory_config() -> dict:
    """Return mixins directory configuration.

    SubPhase-03, Group-A, Task 09.
    """
    config: dict = {
        "configured": True,
        "directory_details": [
            "mixins directory created at backend/apps/core/mixins path",
            "directory contains reusable model mixin classes for all apps",
            "timestamp mixin provides created_at and updated_at fields",
            "soft delete mixin adds is_deleted and deleted_at fields",
            "tenant mixin attaches tenant foreign key to models",
            "directory follows Django best practices for shared behaviors",
        ],
        "content_details": [
            "timestamped.py contains TimestampMixin with auto-now fields",
            "soft_delete.py contains SoftDeleteMixin with delete override",
            "tenant_aware.py contains TenantMixin with tenant FK",
            "auditable.py contains AuditMixin with created_by updated_by",
            "sluggable.py contains SlugMixin with auto-generated slug",
            "orderable.py contains OrderMixin with sort_order field",
        ],
        "organization_details": [
            "each mixin resides in its own dedicated module file",
            "mixins __init__.py re-exports all mixin classes for convenience",
            "mixin modules follow alphabetical naming convention",
            "README.md in mixins directory documents usage examples",
            "mixins are tested in tests/core/test_mixins.py module",
            "mixin dependencies explicitly declared in module docstrings",
        ],
    }
    logger.debug(
        "Mixins directory config: directory_details=%d, content_details=%d",
        len(config["directory_details"]),
        len(config["content_details"]),
    )
    return config


def get_mixins_init_config() -> dict:
    """Return mixins __init__.py configuration.

    SubPhase-03, Group-A, Task 10.
    """
    config: dict = {
        "configured": True,
        "init_details": [
            "__init__.py created in backend/apps/core/mixins directory",
            "init module marks mixins directory as a Python package",
            "imports all mixin classes for convenient access by consumers",
            "defines __all__ list to control public mixin exports",
            "module docstring describes the purpose of the mixins package",
            "init file kept lightweight with only import statements",
        ],
        "export_details": [
            "TimestampMixin exported for created_at and updated_at fields",
            "SoftDeleteMixin exported for soft deletion behavior",
            "TenantMixin exported for multi-tenant model support",
            "AuditMixin exported for tracking created_by and updated_by",
            "SlugMixin exported for automatic slug generation on models",
            "OrderMixin exported for sortable record ordering",
        ],
        "discovery_details": [
            "Django app registry discovers mixins through package imports",
            "mixin classes auto-discovered when mixins package is imported",
            "discovery supports IDE autocompletion for mixin references",
            "circular import guards prevent issues during app startup",
            "lazy imports used where necessary to avoid load-order issues",
            "discovery mechanism documented in mixins package README",
        ],
    }
    logger.debug(
        "Mixins init config: init_details=%d, export_details=%d",
        len(config["init_details"]),
        len(config["export_details"]),
    )
    return config


def get_model_naming_convention_config() -> dict:
    """Return model naming convention configuration.

    SubPhase-03, Group-A, Task 11.
    """
    config: dict = {
        "configured": True,
        "convention_details": [
            "model class names use PascalCase with singular form",
            "model file names use snake_case matching the class name",
            "abstract model names prefixed with Base for clarity",
            "proxy model names suffixed with Proxy to indicate type",
            "through model names combine both related model names",
            "model Meta class verbose_name uses human-readable singular",
        ],
        "example_details": [
            "Product model defined in product.py as class Product",
            "BaseModel abstract class defined in base.py module",
            "OrderItem through model links Order and Product models",
            "TenantProxy proxy model inherits from Tenant model",
            "SalesInvoice model uses two-word PascalCase naming",
            "InventoryAdjustment model follows compound naming pattern",
        ],
        "enforcement_details": [
            "linting rules enforce PascalCase on model class definitions",
            "code review checklist includes model naming verification",
            "pre-commit hook validates model class naming conventions",
            "documentation template reminds developers of naming rules",
            "CI pipeline runs naming convention checks on pull requests",
            "migration files reviewed for consistent model name usage",
        ],
    }
    logger.debug(
        "Model naming convention config: convention_details=%d, example_details=%d",
        len(config["convention_details"]),
        len(config["example_details"]),
    )
    return config


def get_field_naming_convention_config() -> dict:
    """Return field naming convention configuration.

    SubPhase-03, Group-A, Task 12.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "all model field names use snake_case convention consistently",
            "foreign key fields suffixed with _id by Django automatically",
            "boolean fields prefixed with is_ or has_ for readability",
            "date fields suffixed with _at for timestamps or _date for dates",
            "related_name on foreign keys uses plural snake_case form",
            "field names kept concise but descriptive for clarity",
        ],
        "pattern_details": [
            "created_at and updated_at follow timestamp field pattern",
            "is_active and is_deleted follow boolean field pattern",
            "name and title follow short descriptive field pattern",
            "description and notes follow long text field pattern",
            "sort_order and position follow ordering field pattern",
            "slug and uuid follow identifier field naming pattern",
        ],
        "consistency_details": [
            "field naming consistency enforced across all application models",
            "shared fields use identical names in every model they appear",
            "audit trail fields created_by and updated_by always paired",
            "tenant_id field name standardized across all tenant-aware models",
            "primary key field always named id using Django auto field",
            "field names reviewed during code review for convention adherence",
        ],
    }
    logger.debug(
        "Field naming convention config: field_details=%d, pattern_details=%d",
        len(config["field_details"]),
        len(config["pattern_details"]),
    )
    return config


def get_model_documentation_template_config() -> dict:
    """Return model documentation template configuration.

    SubPhase-03, Group-A, Task 13.
    """
    config: dict = {
        "configured": True,
        "template_details": [
            "documentation template defined for every model class docstring",
            "template includes a summary line describing the model purpose",
            "template lists all fields with types and descriptions",
            "template documents relationships to other models explicitly",
            "template specifies database indexes and constraints",
            "template stored in docs/architecture/model-template.md",
        ],
        "section_details": [
            "Fields section enumerates each field with type and default",
            "Relationships section lists foreign keys and many-to-many links",
            "Indexes section describes database indexes for query performance",
            "Constraints section documents unique and check constraints",
            "Methods section summarizes custom model methods and properties",
            "Meta section records verbose_name ordering and permissions",
        ],
        "usage_details": [
            "developers copy template when creating a new model class",
            "code review verifies documentation template is filled in",
            "automated doc generator parses model docstrings for API docs",
            "template ensures consistent documentation across all models",
            "missing sections flagged by documentation linting tools",
            "template versioned alongside code in the repository",
        ],
    }
    logger.debug(
        "Model documentation template config: template_details=%d, section_details=%d",
        len(config["template_details"]),
        len(config["section_details"]),
    )
    return config


def get_base_structure_verification_config() -> dict:
    """Return base structure verification configuration.

    SubPhase-03, Group-A, Task 14.
    """
    config: dict = {
        "configured": True,
        "verification_details": [
            "verification confirms all required directories exist on disk",
            "verification checks that __init__.py files are in each package",
            "verification validates base model file is present and valid",
            "verification ensures manager directory structure is complete",
            "verification confirms mixins directory and init are created",
            "verification runs as part of the CI pipeline on every commit",
        ],
        "checklist_details": [
            "checklist item: models directory exists at expected path",
            "checklist item: models __init__.py exports base classes",
            "checklist item: managers directory exists with __init__.py",
            "checklist item: mixins directory exists with __init__.py",
            "checklist item: base.py files present in models and managers",
            "checklist item: naming conventions applied to all modules",
        ],
        "outcome_details": [
            "all directories verified and present in project structure",
            "all __init__.py files verified with correct export lists",
            "base model and manager classes importable without errors",
            "naming conventions confirmed across all checked modules",
            "documentation templates found in the expected locations",
            "verification report generated and logged for audit trail",
        ],
    }
    logger.debug(
        "Base structure verification config: verification_details=%d, checklist_details=%d",
        len(config["verification_details"]),
        len(config["checklist_details"]),
    )
    return config


def get_timestamped_file_config() -> dict:
    """Return timestamped file configuration.

    SubPhase-03, Group-B, Task 15.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "timestamped.py is created under the core models directory",
            "the file holds the TimeStampedModel abstract base class",
            "timestamped.py follows the same naming pattern as base.py",
            "the file imports Django models module at the top level",
            "timestamped.py is registered in the models __init__.py",
            "the file includes a module-level docstring for documentation",
        ],
        "purpose_details": [
            "purpose is to provide automatic timestamp tracking for models",
            "purpose includes centralising created_at and updated_at logic",
            "purpose avoids duplicating datetime fields across every model",
            "purpose ensures consistent timestamp behaviour project-wide",
            "purpose supports audit trail requirements for all entities",
            "purpose keeps timestamp concerns separated from business logic",
        ],
        "location_details": [
            "location is apps/core/models/timestamped.py in the project",
            "location follows the convention of one class per model file",
            "location is inside the core app shared models package",
            "location allows easy import from apps.core.models module",
            "location is alongside base.py in the models directory",
            "location is discoverable by Django model auto-loading",
        ],
    }
    logger.debug(
        "Timestamped file config: file_details=%d, purpose_details=%d",
        len(config["file_details"]),
        len(config["purpose_details"]),
    )
    return config


def get_timestamped_model_config() -> dict:
    """Return TimeStampedModel class configuration.

    SubPhase-03, Group-B, Task 16.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "TimeStampedModel is defined as an abstract Django model class",
            "the class inherits from django.db.models.Model as its base",
            "TimeStampedModel provides created_at and updated_at fields",
            "the class is intended to be subclassed by all project models",
            "TimeStampedModel includes an inner Meta class with abstract True",
            "the class name follows PascalCase project naming conventions",
        ],
        "inheritance_details": [
            "inheritance from models.Model gives standard Django ORM support",
            "inheritance allows subclasses to gain timestamp fields automatically",
            "inheritance chain supports multiple abstract model composition",
            "inheritance ensures Django migration system recognises the fields",
            "inheritance does not create a separate database table for this class",
            "inheritance provides a clean extension point for future mixins",
        ],
        "usage_details": [
            "usage requires subclassing TimeStampedModel instead of models.Model",
            "usage ensures every child model gets created_at and updated_at",
            "usage pattern is consistent across all application modules",
            "usage reduces boilerplate in individual model definitions",
            "usage is documented in the project architecture guide",
            "usage is enforced through code review and linting checks",
        ],
    }
    logger.debug(
        "TimeStampedModel config: class_details=%d, inheritance_details=%d",
        len(config["class_details"]),
        len(config["inheritance_details"]),
    )
    return config


def get_created_at_field_config() -> dict:
    """Return created_at field configuration.

    SubPhase-03, Group-B, Task 17.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "created_at is a DateTimeField on the TimeStampedModel class",
            "created_at uses auto_now_add=True to set on first save only",
            "created_at is not editable once the record has been created",
            "created_at stores timezone-aware datetime values in the database",
            "created_at field name follows snake_case naming conventions",
            "created_at is included in the default model serialization",
        ],
        "behavior_details": [
            "behavior sets the value automatically at object creation time",
            "behavior prevents manual override by default via auto_now_add",
            "behavior uses Django timezone.now for consistent timestamps",
            "behavior stores UTC datetime when USE_TZ is enabled",
            "behavior is inherited by every model that extends TimeStampedModel",
            "behavior does not change on subsequent save operations",
        ],
        "index_details": [
            "index is added on created_at for efficient date range queries",
            "index uses db_index=True parameter in the field definition",
            "index improves performance for ordering by creation date",
            "index supports common filtering patterns on recent records",
            "index is created as a standard B-tree index in PostgreSQL",
            "index size is proportional to total number of rows in table",
        ],
    }
    logger.debug(
        "created_at field config: field_details=%d, behavior_details=%d",
        len(config["field_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_updated_at_field_config() -> dict:
    """Return updated_at field configuration.

    SubPhase-03, Group-B, Task 18.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "updated_at is a DateTimeField on the TimeStampedModel class",
            "updated_at uses auto_now=True to refresh on every save call",
            "updated_at reflects the most recent modification timestamp",
            "updated_at stores timezone-aware datetime values in the database",
            "updated_at field name follows snake_case naming conventions",
            "updated_at is included in the default model serialization",
        ],
        "update_details": [
            "update sets the value automatically each time the model is saved",
            "update uses Django timezone.now for consistent timestamp refresh",
            "update occurs even when no other field values have changed",
            "update behaviour is inherited by all child model classes",
            "update does not require manual intervention from application code",
            "update tracks the last modification time for audit purposes",
        ],
        "tracking_details": [
            "tracking allows detection of stale or recently modified records",
            "tracking supports cache invalidation strategies based on update time",
            "tracking enables building change-log features on top of the field",
            "tracking is useful for synchronisation with external systems",
            "tracking pairs with created_at to calculate record lifespan",
            "tracking is queryable via Django ORM filter and exclude methods",
        ],
    }
    logger.debug(
        "updated_at field config: field_details=%d, update_details=%d",
        len(config["field_details"]),
        len(config["update_details"]),
    )
    return config


def get_meta_abstract_config() -> dict:
    """Return Meta abstract configuration.

    SubPhase-03, Group-B, Task 19.
    """
    config: dict = {
        "configured": True,
        "meta_details": [
            "Meta inner class is defined inside TimeStampedModel",
            "Meta class configures Django ORM behaviour for the model",
            "Meta class sets abstract and ordering options for the model",
            "Meta class follows standard Django model Meta conventions",
            "Meta class is inherited by subclasses unless explicitly overridden",
            "Meta class is required for abstract base model definitions",
        ],
        "abstract_details": [
            "abstract is set to True to prevent creating a database table",
            "abstract ensures fields are only added to child model tables",
            "abstract allows TimeStampedModel to serve as a reusable mixin",
            "abstract models cannot be instantiated or queried directly",
            "abstract setting is standard practice for shared field groups",
            "abstract flag is checked by Django during migration generation",
        ],
        "design_details": [
            "design follows the abstract base class pattern from Django docs",
            "design keeps the timestamp logic decoupled from concrete models",
            "design supports composition of multiple abstract bases if needed",
            "design avoids multi-table inheritance overhead in the database",
            "design allows adding new shared fields without altering children",
            "design is consistent with the project base model architecture",
        ],
    }
    logger.debug(
        "Meta abstract config: meta_details=%d, abstract_details=%d",
        len(config["meta_details"]),
        len(config["abstract_details"]),
    )
    return config


def get_ordering_config() -> dict:
    """Return ordering configuration.

    SubPhase-03, Group-B, Task 20.
    """
    config: dict = {
        "configured": True,
        "ordering_details": [
            "ordering is set to [\"-created_at\"] for newest-first results",
            "ordering is defined in the Meta class of TimeStampedModel",
            "ordering applies as the default for all querysets on child models",
            "ordering uses the created_at field which has a database index",
            "ordering can be overridden per-query with .order_by() calls",
            "ordering follows the descending convention for time-series data",
        ],
        "query_details": [
            "query results return most recently created records first",
            "query performance benefits from the index on created_at",
            "query behaviour is consistent across all models in the project",
            "query default ordering simplifies list views and API endpoints",
            "query ordering reduces the need for explicit sort parameters",
            "query plans use the created_at index for efficient sorting",
        ],
        "override_details": [
            "override is possible by defining Meta ordering in child models",
            "override uses standard Django Meta class inheritance rules",
            "override can specify ascending or different field combinations",
            "override at the queryset level takes precedence over Meta ordering",
            "override should be documented when deviating from the default",
            "override does not affect the parent TimeStampedModel definition",
        ],
    }
    logger.debug(
        "Ordering config: ordering_details=%d, query_details=%d",
        len(config["ordering_details"]),
        len(config["query_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-B: TimeStampedModel Manager & Methods – Tasks 21-28
# ---------------------------------------------------------------------------


def get_timestamped_manager_config() -> dict:
    """Return TimeStampedManager configuration.

    SubPhase-03, Group-B, Task 21.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "TimeStampedManager extends Django base Manager class",
            "TimeStampedManager provides time-based query helper methods",
            "TimeStampedManager is assigned as the default manager on TimeStampedModel",
            "TimeStampedManager uses created_at field for all time-based filters",
            "TimeStampedManager exposes recent, today, this_week, this_month helpers",
            "TimeStampedManager follows Django custom manager best practices",
        ],
        "query_details": [
            "query helpers filter records based on created_at timestamp",
            "query helpers accept optional day-range parameters where applicable",
            "query helpers return standard Django QuerySet instances",
            "query helpers are chainable with other queryset methods",
            "query helpers use timezone-aware datetime comparisons",
            "query helpers leverage database indexes on created_at for performance",
        ],
        "attachment_details": [
            "attachment to TimeStampedModel uses objects = TimeStampedManager()",
            "attachment replaces the default Manager only on the abstract base",
            "attachment is inherited by all concrete child models automatically",
            "attachment follows Django manager inheritance and ordering rules",
            "attachment keeps the default queryset behaviour unchanged",
            "attachment is documented in the base models architecture guide",
        ],
    }
    logger.debug(
        "TimeStampedManager config: manager_details=%d, query_details=%d",
        len(config["manager_details"]),
        len(config["query_details"]),
    )
    return config


def get_recent_method_config() -> dict:
    """Return recent() method configuration.

    SubPhase-03, Group-B, Task 22.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "recent() filters records created within the last N days",
            "recent() accepts an integer days parameter with a default of 7",
            "recent() returns a queryset filtered by created_at__gte threshold",
            "recent() computes the threshold using timezone.now() minus timedelta",
            "recent() is defined on the TimeStampedManager class",
            "recent() is the foundation for this_week and this_month helpers",
        ],
        "filter_details": [
            "filter uses created_at__gte to include records from the threshold date",
            "filter threshold is calculated as now minus the specified number of days",
            "filter is timezone-aware to handle UTC and local time correctly",
            "filter returns a standard queryset that can be further chained",
            "filter preserves the default ordering defined in Meta class",
            "filter benefits from the database index on the created_at column",
        ],
        "default_details": [
            "default value of days parameter is 7 for a one-week window",
            "default can be overridden by passing any positive integer",
            "default aligns with common dashboard last-7-days reporting pattern",
            "default is documented in the method docstring and usage guide",
            "default ensures the method is usable without any arguments",
            "default was chosen based on typical ERP reporting requirements",
        ],
    }
    logger.debug(
        "recent() method config: method_details=%d, filter_details=%d",
        len(config["method_details"]),
        len(config["filter_details"]),
    )
    return config


def get_today_method_config() -> dict:
    """Return today() method configuration.

    SubPhase-03, Group-B, Task 23.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "today() filters records created on the current calendar date",
            "today() uses timezone.now().date() for the date boundary",
            "today() returns a queryset with created_at__date equal to today",
            "today() is timezone-aware respecting the Django TIME_ZONE setting",
            "today() is defined on the TimeStampedManager class",
            "today() is commonly used in daily reports and dashboard widgets",
        ],
        "timezone_details": [
            "timezone handling uses django.utils.timezone for awareness",
            "timezone conversion ensures correct date in the active time zone",
            "timezone support prevents off-by-one day errors at midnight UTC",
            "timezone configuration respects USE_TZ and TIME_ZONE in settings",
            "timezone-aware queries work consistently across all database backends",
            "timezone utilities are imported from django.utils.timezone module",
        ],
        "usage_details": [
            "usage pattern is Model.objects.today() for daily record retrieval",
            "usage in views provides quick access to today's entries",
            "usage in serializers can embed today's count in API responses",
            "usage in admin list filters simplifies daily record inspection",
            "usage in management commands supports daily batch processing",
            "usage is documented in the TimeStampedModel usage guide",
        ],
    }
    logger.debug(
        "today() method config: method_details=%d, timezone_details=%d",
        len(config["method_details"]),
        len(config["timezone_details"]),
    )
    return config


def get_this_week_method_config() -> dict:
    """Return this_week() method configuration.

    SubPhase-03, Group-B, Task 24.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "this_week() filters records created in the last 7 days",
            "this_week() is a convenience alias that calls self.recent(7)",
            "this_week() returns a standard Django queryset instance",
            "this_week() is defined on the TimeStampedManager class",
            "this_week() requires no arguments and uses a fixed 7-day window",
            "this_week() is commonly used in weekly summary dashboards",
        ],
        "alias_details": [
            "alias delegates to recent() with days parameter set to 7",
            "alias provides a more readable and intention-revealing name",
            "alias ensures consistent behaviour with the recent() implementation",
            "alias avoids duplicating the date filtering logic",
            "alias is tested to return the same queryset as recent(7)",
            "alias follows the DRY principle for method reuse",
        ],
        "convenience_details": [
            "convenience method improves code readability in views and reports",
            "convenience method reduces magic numbers in business logic code",
            "convenience method is auto-discovered by IDE auto-completion",
            "convenience method is listed in the manager's public API",
            "convenience method pairs well with this_month for period comparisons",
            "convenience method is documented alongside other manager helpers",
        ],
    }
    logger.debug(
        "this_week() method config: method_details=%d, alias_details=%d",
        len(config["method_details"]),
        len(config["alias_details"]),
    )
    return config


def get_this_month_method_config() -> dict:
    """Return this_month() method configuration.

    SubPhase-03, Group-B, Task 25.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "this_month() filters records created in the last 30 days",
            "this_month() is a convenience alias that calls self.recent(30)",
            "this_month() returns a standard Django queryset instance",
            "this_month() is defined on the TimeStampedManager class",
            "this_month() requires no arguments and uses a fixed 30-day window",
            "this_month() is commonly used in monthly reporting dashboards",
        ],
        "range_details": [
            "range covers the last 30 calendar days from the current moment",
            "range uses a rolling window rather than calendar month boundaries",
            "range is computed via timezone.now() minus timedelta(days=30)",
            "range includes records created on the boundary day itself",
            "range is consistent with the recent() method's behaviour",
            "range can be adjusted by calling recent() directly with a custom value",
        ],
        "reporting_details": [
            "reporting use case includes monthly sales and revenue summaries",
            "reporting views benefit from the descriptive method name",
            "reporting APIs can expose this_month counts in dashboard endpoints",
            "reporting aggregates pair well with Django annotate and aggregate",
            "reporting period aligns with common 30-day business review cycles",
            "reporting documentation references this method for standard queries",
        ],
    }
    logger.debug(
        "this_month() method config: method_details=%d, range_details=%d",
        len(config["method_details"]),
        len(config["range_details"]),
    )
    return config


def get_timestamped_export_config() -> dict:
    """Return timestamped export configuration.

    SubPhase-03, Group-B, Task 26.
    """
    config: dict = {
        "configured": True,
        "export_details": [
            "export adds TimeStampedModel to the models package __init__.py",
            "export uses a standard from .timestamped import TimeStampedModel statement",
            "export makes TimeStampedModel available via apps.core.models",
            "export follows the project convention for model re-exports",
            "export is placed alphabetically among other model imports",
            "export is verified by an integration test importing from the package",
        ],
        "import_details": [
            "import path for consumers is from apps.core.models import TimeStampedModel",
            "import avoids deep module paths for better developer ergonomics",
            "import is re-exported in __all__ for explicit public API declaration",
            "import supports wildcard imports when __all__ is defined",
            "import path is documented in the models architecture guide",
            "import consistency is enforced by linting rules across the project",
        ],
        "package_details": [
            "package __init__.py acts as the public surface for the core models",
            "package re-export pattern keeps internal module structure flexible",
            "package follows the same pattern used for managers and mixins",
            "package allows refactoring internal files without breaking consumers",
            "package exports are listed in __all__ for documentation tools",
            "package structure is documented in the models directory README",
        ],
    }
    logger.debug(
        "Timestamped export config: export_details=%d, import_details=%d",
        len(config["export_details"]),
        len(config["import_details"]),
    )
    return config


def get_timestamped_tests_config() -> dict:
    """Return timestamped tests configuration.

    SubPhase-03, Group-B, Task 27.
    """
    config: dict = {
        "configured": True,
        "test_details": [
            "tests verify TimeStampedModel fields are added to child models",
            "tests confirm created_at is auto-set on record creation",
            "tests confirm updated_at is auto-updated on record save",
            "tests validate Meta abstract is True on TimeStampedModel",
            "tests check default ordering is set to -created_at",
            "tests ensure TimeStampedManager methods return correct querysets",
        ],
        "coverage_details": [
            "coverage includes unit tests for each manager helper method",
            "coverage includes field type and option assertions",
            "coverage includes timezone awareness verification",
            "coverage includes default parameter value validation",
            "coverage includes queryset chaining compatibility checks",
            "coverage targets 100 percent of TimeStampedModel public API",
        ],
        "validation_details": [
            "validation uses pytest fixtures for temporary model instances",
            "validation asserts return types are Django QuerySet instances",
            "validation checks that recent() default is 7 days",
            "validation confirms today() uses the current date boundary",
            "validation verifies this_week() and this_month() delegate correctly",
            "validation follows the project test conventions and naming standards",
        ],
    }
    logger.debug(
        "Timestamped tests config: test_details=%d, coverage_details=%d",
        len(config["test_details"]),
        len(config["coverage_details"]),
    )
    return config


def get_timestamped_docs_config() -> dict:
    """Return timestamped documentation configuration.

    SubPhase-03, Group-B, Task 28.
    """
    config: dict = {
        "configured": True,
        "docs_details": [
            "docs describe TimeStampedModel purpose and field definitions",
            "docs include usage examples for inheriting from TimeStampedModel",
            "docs explain the TimeStampedManager helper methods and parameters",
            "docs cover timezone considerations for created_at and updated_at",
            "docs reference the Meta options including abstract and ordering",
            "docs are maintained in the base models architecture markdown file",
        ],
        "guideline_details": [
            "guideline recommends inheriting TimeStampedModel for all new models",
            "guideline states created_at and updated_at should not be overridden",
            "guideline advises using manager helpers instead of raw date filters",
            "guideline requires documenting any custom ordering overrides",
            "guideline encourages using today() and this_week() for dashboard queries",
            "guideline is reviewed and updated with each base model change",
        ],
        "example_details": [
            "example shows a Product model inheriting from TimeStampedModel",
            "example demonstrates calling Product.objects.recent(14) for two weeks",
            "example illustrates Product.objects.today() for daily sales reports",
            "example includes a serializer exposing created_at as read-only",
            "example covers overriding Meta ordering in a child model",
            "example is included in the project developer onboarding guide",
        ],
    }
    logger.debug(
        "Timestamped docs config: docs_details=%d, guideline_details=%d",
        len(config["docs_details"]),
        len(config["guideline_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-C: SoftDeleteModel, Fields & Managers – Tasks 29-35
# ---------------------------------------------------------------------------


def get_soft_delete_file_config() -> dict:
    """Return soft delete file configuration.

    SubPhase-03, Group-C, Task 29.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "soft_delete.py resides in the core models directory",
            "soft_delete.py contains the SoftDeleteModel abstract base class",
            "soft_delete.py imports from django.db and django.utils modules",
            "soft_delete.py follows the project single-responsibility file convention",
            "soft_delete.py is registered in the models __init__.py for public export",
            "soft_delete.py includes module-level docstring describing its purpose",
        ],
        "purpose_details": [
            "purpose is to provide reusable soft-delete behaviour for all models",
            "purpose includes keeping deleted records in the database for auditing",
            "purpose supports recovery of accidentally deleted records",
            "purpose enables data retention policies required by regulations",
            "purpose centralises deletion logic to avoid duplication across apps",
            "purpose aligns with the project base model inheritance strategy",
        ],
        "location_details": [
            "location is apps/core/models/soft_delete.py within the backend tree",
            "location follows the established models directory structure convention",
            "location keeps soft-delete logic separate from timestamped model logic",
            "location is discoverable via the core models package __init__.py",
            "location mirrors the pattern used for base.py and timestamped.py",
            "location is documented in the base models architecture guide",
        ],
    }
    logger.debug(
        "Soft delete file config: file_details=%d, purpose_details=%d",
        len(config["file_details"]),
        len(config["purpose_details"]),
    )
    return config


def get_soft_delete_model_config() -> dict:
    """Return SoftDeleteModel class configuration.

    SubPhase-03, Group-C, Task 30.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "SoftDeleteModel is an abstract Django model providing soft-delete support",
            "SoftDeleteModel defines is_deleted and deleted_at fields on all subclasses",
            "SoftDeleteModel overrides the default delete method with a soft-delete call",
            "SoftDeleteModel provides a restore method to undo soft deletion",
            "SoftDeleteModel uses Meta abstract equals True to prevent table creation",
            "SoftDeleteModel is exported from the core models package for reuse",
        ],
        "inheritance_details": [
            "inheritance extends TimeStampedModel to include created_at and updated_at",
            "inheritance chain is Model then TimeStampedModel then SoftDeleteModel",
            "inheritance allows child models to gain both timestamp and soft-delete features",
            "inheritance uses Python MRO to resolve method and manager conflicts",
            "inheritance keeps the abstract flag so no migration is generated for SoftDeleteModel",
            "inheritance follows the project convention of composable abstract bases",
        ],
        "behavior_details": [
            "behavior sets is_deleted to True and deleted_at to current timestamp on delete",
            "behavior does not remove the database row preserving referential integrity",
            "behavior filters out soft-deleted records from default manager queries",
            "behavior provides an all_with_deleted manager for admin-level access",
            "behavior supports bulk soft-delete through custom queryset methods",
            "behavior emits a post_soft_delete signal for downstream listeners",
        ],
    }
    logger.debug(
        "Soft delete model config: class_details=%d, inheritance_details=%d",
        len(config["class_details"]),
        len(config["inheritance_details"]),
    )
    return config


def get_is_deleted_field_config() -> dict:
    """Return is_deleted boolean field configuration.

    SubPhase-03, Group-C, Task 31.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "is_deleted is a BooleanField on SoftDeleteModel marking record state",
            "is_deleted uses verbose_name 'soft deleted' for admin readability",
            "is_deleted is included in list_filter for Django admin integration",
            "is_deleted field type is BooleanField not NullBooleanField",
            "is_deleted is referenced by the SoftDeleteManager queryset filter",
            "is_deleted appears in serializer output only for admin endpoints",
        ],
        "default_details": [
            "default value for is_deleted is False indicating an active record",
            "default ensures new records are visible in standard querysets",
            "default is enforced at the database level via column default",
            "default is explicitly set in the field declaration for clarity",
            "default prevents accidental exclusion of newly created records",
            "default aligns with the convention that False means not deleted",
        ],
        "index_details": [
            "index is added via db_index equals True for query performance",
            "index speeds up the SoftDeleteManager default filter on is_deleted",
            "index is a B-tree index suitable for boolean equality lookups",
            "index is created in the migration generated for each child model",
            "index benefits admin views filtering active versus deleted records",
            "index has minimal write overhead given infrequent deletion operations",
        ],
    }
    logger.debug(
        "is_deleted field config: field_details=%d, default_details=%d",
        len(config["field_details"]),
        len(config["default_details"]),
    )
    return config


def get_deleted_at_field_config() -> dict:
    """Return deleted_at timestamp field configuration.

    SubPhase-03, Group-C, Task 32.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "deleted_at is a DateTimeField recording when soft deletion occurred",
            "deleted_at uses verbose_name 'deleted at' for admin display",
            "deleted_at is set to timezone.now when a record is soft-deleted",
            "deleted_at is reset to None when a record is restored",
            "deleted_at supports auditing by preserving the exact deletion time",
            "deleted_at is defined on SoftDeleteModel and inherited by children",
        ],
        "nullability_details": [
            "null is True allowing deleted_at to be None for active records",
            "blank is True so the admin form does not require a value",
            "default is None indicating the record has not been deleted",
            "null value distinguishes active records from soft-deleted ones",
            "nullability enables simple queryset filtering on deleted_at__isnull",
            "null handling follows Django convention for optional datetime fields",
        ],
        "timestamp_details": [
            "timestamp is timezone-aware using django.utils.timezone.now",
            "timestamp precision matches the database datetime column type",
            "timestamp is stored in UTC regardless of the active time zone",
            "timestamp supports calculating duration since deletion for reports",
            "timestamp is displayed in the user local time zone in admin views",
            "timestamp can be indexed for queries filtering by deletion date range",
        ],
    }
    logger.debug(
        "deleted_at field config: field_details=%d, nullability_details=%d",
        len(config["field_details"]),
        len(config["nullability_details"]),
    )
    return config


def get_soft_delete_manager_config() -> dict:
    """Return SoftDeleteManager configuration.

    SubPhase-03, Group-C, Task 33.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "SoftDeleteManager extends Django Manager for soft-delete filtering",
            "SoftDeleteManager is assigned as the default objects manager",
            "SoftDeleteManager overrides get_queryset to exclude deleted records",
            "SoftDeleteManager ensures ORM queries never return soft-deleted rows",
            "SoftDeleteManager is defined in the core managers module",
            "SoftDeleteManager supports chaining with other queryset methods",
        ],
        "exclusion_details": [
            "exclusion filters records where is_deleted equals True",
            "exclusion is applied automatically on every default queryset call",
            "exclusion uses filter(is_deleted=False) for clarity and performance",
            "exclusion prevents soft-deleted data from appearing in API responses",
            "exclusion can be bypassed using the all_with_deleted manager",
            "exclusion logic is centralised to avoid per-view filter duplication",
        ],
        "usage_details": [
            "usage allows Model.objects.all() to return only active records",
            "usage integrates transparently with DRF generic views and filters",
            "usage is documented in the base models architecture guide",
            "usage requires no changes in consuming code compared to default manager",
            "usage is tested with unit tests confirming excluded records are hidden",
            "usage supports related manager lookups via ForeignKey or ManyToMany",
        ],
    }
    logger.debug(
        "Soft delete manager config: manager_details=%d, exclusion_details=%d",
        len(config["manager_details"]),
        len(config["exclusion_details"]),
    )
    return config


def get_queryset_override_config() -> dict:
    """Return queryset override configuration.

    SubPhase-03, Group-C, Task 34.
    """
    config: dict = {
        "configured": True,
        "queryset_details": [
            "queryset override is implemented in SoftDeleteManager.get_queryset",
            "queryset calls super().get_queryset() to obtain the base queryset",
            "queryset applies .filter(is_deleted=False) to the base queryset",
            "queryset returns a standard Django QuerySet instance for compatibility",
            "queryset override is invoked on every Manager.all() and related lookup",
            "queryset override is unit-tested to confirm filtering behaviour",
        ],
        "filter_details": [
            "filter uses is_deleted=False as the sole exclusion criterion",
            "filter leverages the database index on the is_deleted column",
            "filter is evaluated lazily following Django queryset semantics",
            "filter can be combined with additional where clauses via chaining",
            "filter does not alter the query when is_deleted column is absent",
            "filter follows the same pattern used by django-safedelete library",
        ],
        "effect_details": [
            "effect hides soft-deleted rows from all default ORM operations",
            "effect applies to select queries but not to raw SQL statements",
            "effect is transparent to serializers and viewsets using objects manager",
            "effect reduces risk of exposing deleted data through API endpoints",
            "effect is reversible by querying through all_with_deleted manager",
            "effect is logged at debug level when soft-delete filtering is active",
        ],
    }
    logger.debug(
        "Queryset override config: queryset_details=%d, filter_details=%d",
        len(config["queryset_details"]),
        len(config["filter_details"]),
    )
    return config


def get_all_with_deleted_manager_config() -> dict:
    """Return all_with_deleted manager configuration.

    SubPhase-03, Group-C, Task 35.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "all_with_deleted is a secondary Django Manager on SoftDeleteModel",
            "all_with_deleted uses the unfiltered base queryset from models.Manager",
            "all_with_deleted is assigned as Model.all_with_deleted on child models",
            "all_with_deleted returns both active and soft-deleted records",
            "all_with_deleted is useful for admin panels and audit trail views",
            "all_with_deleted does not override get_queryset keeping default behaviour",
        ],
        "access_details": [
            "access is restricted to admin views and internal management commands",
            "access requires explicit use of Model.all_with_deleted.all() in code",
            "access is not exposed through default API serializers or viewsets",
            "access enables recovery workflows for restoring soft-deleted records",
            "access can be wrapped in permission checks for additional security",
            "access is documented with warnings about including deleted data",
        ],
        "admin_details": [
            "admin views use all_with_deleted to show deleted records with a flag",
            "admin list_display includes is_deleted and deleted_at columns",
            "admin actions allow bulk restore of soft-deleted records",
            "admin filters let staff toggle visibility of deleted records",
            "admin detail view shows deletion timestamp for audit purposes",
            "admin integration follows Django ModelAdmin best practices",
        ],
    }
    logger.debug(
        "all_with_deleted manager config: manager_details=%d, access_details=%d",
        len(config["manager_details"]),
        len(config["access_details"]),
    )
    return config


def get_deleted_only_manager_config() -> dict:
    """Return deleted_only manager configuration.

    SubPhase-03, Group-C, Task 36.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "deleted_only is a tertiary Django Manager on SoftDeleteModel",
            "deleted_only filters queryset to return only soft-deleted records",
            "deleted_only overrides get_queryset with .filter(is_deleted=True)",
            "deleted_only is assigned as Model.deleted_only on child models",
            "deleted_only enables dedicated views for reviewing deleted data",
            "deleted_only does not affect the default objects manager behaviour",
        ],
        "filter_details": [
            "filter applies is_deleted=True as the sole inclusion criterion",
            "filter leverages the database index on the is_deleted column",
            "filter is evaluated lazily following Django queryset semantics",
            "filter returns only records that have been soft-deleted previously",
            "filter can be combined with additional where clauses via chaining",
            "filter is unit-tested to confirm correct deleted-only behaviour",
        ],
        "audit_details": [
            "audit workflows use deleted_only to review recently deleted records",
            "audit reports include deleted_at timestamps for compliance tracking",
            "audit trail preserves full history of soft-deleted model instances",
            "audit queries via deleted_only are optimised by the is_deleted index",
            "audit views restrict access to staff users with appropriate permissions",
            "audit exports can serialise deleted_only querysets for external review",
        ],
    }
    logger.debug(
        "deleted_only manager config: manager_details=%d, filter_details=%d",
        len(config["manager_details"]),
        len(config["filter_details"]),
    )
    return config


def get_soft_delete_method_config() -> dict:
    """Return soft_delete() method configuration.

    SubPhase-03, Group-C, Task 37.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "soft_delete() sets is_deleted to True on the model instance",
            "soft_delete() sets deleted_at to the current timezone-aware datetime",
            "soft_delete() calls self.save() with update_fields for efficiency",
            "soft_delete() is defined on the SoftDeleteModel abstract base class",
            "soft_delete() does not trigger the post_delete signal by design",
            "soft_delete() returns None following Django model method conventions",
        ],
        "behavior_details": [
            "behavior preserves the record in the database for future recovery",
            "behavior hides the record from default manager queries immediately",
            "behavior is idempotent and can be called on already-deleted records",
            "behavior does not cascade to related models by default",
            "behavior records the exact deletion timestamp for audit compliance",
            "behavior follows the soft-delete pattern used by django-safedelete",
        ],
        "update_details": [
            "update uses save(update_fields=['is_deleted', 'deleted_at'])",
            "update avoids overwriting other fields that may have changed concurrently",
            "update triggers the pre_save and post_save signals on the model",
            "update is wrapped in a single database query for atomicity",
            "update respects any custom save logic defined in child model classes",
            "update is unit-tested with assertions on both field values after call",
        ],
    }
    logger.debug(
        "soft_delete method config: method_details=%d, behavior_details=%d",
        len(config["method_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_restore_method_config() -> dict:
    """Return restore() method configuration.

    SubPhase-03, Group-C, Task 38.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "restore() sets is_deleted back to False on the model instance",
            "restore() sets deleted_at to None clearing the deletion timestamp",
            "restore() calls self.save() with update_fields for efficiency",
            "restore() is defined on the SoftDeleteModel abstract base class",
            "restore() enables recovery workflows for accidentally deleted records",
            "restore() returns None following Django model method conventions",
        ],
        "clearing_details": [
            "clearing resets is_deleted to False restoring default visibility",
            "clearing sets deleted_at to None removing the deletion timestamp",
            "clearing makes the record visible through the default objects manager",
            "clearing is idempotent and safe to call on non-deleted records",
            "clearing does not modify any other fields on the model instance",
            "clearing is logged at debug level for observability and auditing",
        ],
        "access_details": [
            "access to restore is restricted to admin views and management commands",
            "access requires the record to be fetched via all_with_deleted manager",
            "access can be wrapped in permission checks for role-based control",
            "access is exposed through dedicated admin actions for bulk restore",
            "access is documented with guidelines for safe restoration procedures",
            "access is unit-tested to verify correct field state after restoration",
        ],
    }
    logger.debug(
        "restore method config: method_details=%d, clearing_details=%d",
        len(config["method_details"]),
        len(config["clearing_details"]),
    )
    return config


def get_hard_delete_method_config() -> dict:
    """Return hard_delete() method configuration.

    SubPhase-03, Group-C, Task 39.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "hard_delete() calls super().delete() to permanently remove the record",
            "hard_delete() bypasses the soft-delete override on SoftDeleteModel",
            "hard_delete() is defined on the SoftDeleteModel abstract base class",
            "hard_delete() accepts using and keep_parents keyword arguments",
            "hard_delete() triggers the standard pre_delete and post_delete signals",
            "hard_delete() returns the deletion tuple from Django's base delete",
        ],
        "permanent_details": [
            "permanent deletion removes the row from the database table entirely",
            "permanent deletion cannot be undone without a database backup restore",
            "permanent deletion is intended for GDPR data erasure requirements",
            "permanent deletion cascades to related objects per foreign key rules",
            "permanent deletion frees storage occupied by the deleted row and indexes",
            "permanent deletion should be restricted to superuser or system processes",
        ],
        "cleanup_details": [
            "cleanup procedures schedule hard_delete for records past retention period",
            "cleanup tasks run as periodic Celery jobs with configurable schedules",
            "cleanup logs every hard deletion with record identifiers for audit trail",
            "cleanup respects tenant isolation ensuring cross-tenant data safety",
            "cleanup is tested with fixtures to verify complete row removal",
            "cleanup documentation warns about irreversible data loss consequences",
        ],
    }
    logger.debug(
        "hard_delete method config: method_details=%d, permanent_details=%d",
        len(config["method_details"]),
        len(config["permanent_details"]),
    )
    return config


def get_delete_override_config() -> dict:
    """Return delete() override configuration.

    SubPhase-03, Group-C, Task 40.
    """
    config: dict = {
        "configured": True,
        "override_details": [
            "delete() is overridden on SoftDeleteModel to perform soft deletion",
            "delete() calls soft_delete() internally instead of removing the row",
            "delete() accepts using and keep_parents kwargs for API compatibility",
            "delete() ensures Model.objects.get(pk=x).delete() soft-deletes by default",
            "delete() preserves the standard Django delete method signature",
            "delete() is transparent to code that calls instance.delete() normally",
        ],
        "impact_details": [
            "impact ensures all default deletion paths use soft-delete semantics",
            "impact affects Django admin delete actions routing them through soft_delete",
            "impact applies to cascade deletions triggered by related object removal",
            "impact is visible in the database where is_deleted becomes True",
            "impact does not alter the return value expected by Django internals",
            "impact is verified by unit tests comparing database state after delete",
        ],
        "default_details": [
            "default behaviour can be bypassed by calling hard_delete() explicitly",
            "default soft-delete is the recommended approach for all model deletions",
            "default override is inherited by all concrete models extending SoftDeleteModel",
            "default behaviour is documented in the model class docstring and README",
            "default delete is tested to confirm is_deleted is True after invocation",
            "default override follows the template method pattern for extensibility",
        ],
    }
    logger.debug(
        "delete override config: override_details=%d, impact_details=%d",
        len(config["override_details"]),
        len(config["impact_details"]),
    )
    return config


def get_is_deleted_index_config() -> dict:
    """Return is_deleted index configuration.

    SubPhase-03, Group-C, Task 41.
    """
    config: dict = {
        "configured": True,
        "index_details": [
            "index is defined on the is_deleted field via Meta.indexes on SoftDeleteModel",
            "index uses models.Index with fields=['is_deleted'] for efficient filtering",
            "index is named following the convention idx_<model>_is_deleted",
            "index is created automatically by Django migration framework",
            "index covers the boolean column used by all soft-delete manager queries",
            "index is declared in the abstract model and inherited by concrete models",
        ],
        "performance_details": [
            "performance improvement is measurable on tables with large row counts",
            "performance of default manager queries benefits from index-only scans",
            "performance testing uses EXPLAIN ANALYZE to verify index utilisation",
            "performance overhead of maintaining the index is minimal for writes",
            "performance gains are most significant for filtered list API endpoints",
            "performance benchmarks are documented in the architecture decision record",
        ],
        "query_details": [
            "query planner uses the is_deleted index for WHERE is_deleted = false",
            "query optimisation reduces full table scans on frequently accessed tables",
            "query filtering by is_deleted is the most common predicate in the system",
            "query results are cached by Django queryset evaluation for repeated access",
            "query performance is monitored via django-debug-toolbar in development",
            "query plans are validated in integration tests against the test database",
        ],
    }
    logger.debug(
        "is_deleted index config: index_details=%d, performance_details=%d",
        len(config["index_details"]),
        len(config["performance_details"]),
    )
    return config


def get_soft_delete_export_config() -> dict:
    """Return Soft delete export configuration.

    SubPhase-03, Group-C, Task 42.
    """
    config: dict = {
        "configured": True,
        "export_details": [
            "export publishes SoftDeleteModel from the models package __init__.py",
            "export publishes SoftDeleteManager from the managers package __init__.py",
            "export publishes DeletedOnlyManager from the managers package __init__.py",
            "export publishes AllWithDeletedManager from the managers package __init__.py",
            "export ensures all soft-delete classes are importable from apps.core",
            "export follows the established pattern used by TimeStampedModel exports",
        ],
        "import_details": [
            "import path for SoftDeleteModel is apps.core.models.SoftDeleteModel",
            "import path for SoftDeleteManager is apps.core.managers.SoftDeleteManager",
            "import path for DeletedOnlyManager is apps.core.managers.DeletedOnlyManager",
            "import path uses explicit relative imports within the core package",
            "import is verified by unit tests that import from the public API surface",
            "import avoids circular dependencies by keeping managers in separate modules",
        ],
        "package_details": [
            "package __init__.py re-exports all soft-delete related public symbols",
            "package structure separates models, managers, and mixins into own files",
            "package follows Django best practices for reusable app organisation",
            "package documentation lists all exported symbols with usage examples",
            "package exports are covered by __all__ lists for explicit public API",
            "package is tested to ensure no import errors on application startup",
        ],
    }
    logger.debug(
        "soft delete export config: export_details=%d, import_details=%d",
        len(config["export_details"]),
        len(config["import_details"]),
    )
    return config


def get_soft_delete_tests_config() -> dict:
    """Return Soft delete tests configuration.

    SubPhase-03, Group-C, Task 43.
    """
    config: dict = {
        "configured": True,
        "test_details": [
            "test suite covers soft_delete(), restore(), hard_delete(), and delete()",
            "test suite uses pytest fixtures to create model instances for each case",
            "test suite verifies is_deleted and deleted_at fields after each operation",
            "test suite checks that default manager excludes soft-deleted records",
            "test suite validates all_with_deleted returns both active and deleted",
            "test suite confirms deleted_only returns only soft-deleted records",
        ],
        "coverage_details": [
            "coverage target for soft-delete module is 100 percent line coverage",
            "coverage includes positive and negative test cases for each method",
            "coverage includes edge cases such as double-delete and double-restore",
            "coverage includes manager queryset filtering verification tests",
            "coverage report is generated by pytest-cov and enforced in CI pipeline",
            "coverage gaps are flagged as warnings in pull request review checks",
        ],
        "validation_details": [
            "validation confirms soft_delete sets is_deleted to True in the database",
            "validation confirms restore sets is_deleted to False in the database",
            "validation confirms hard_delete removes the record from the database",
            "validation confirms delete override routes to soft_delete by default",
            "validation confirms index exists on is_deleted via introspection query",
            "validation uses Django TestCase with transaction rollback for isolation",
        ],
    }
    logger.debug(
        "soft delete tests config: test_details=%d, coverage_details=%d",
        len(config["test_details"]),
        len(config["coverage_details"]),
    )
    return config


def get_soft_delete_docs_config() -> dict:
    """Return Soft delete docs configuration.

    SubPhase-03, Group-C, Task 44.
    """
    config: dict = {
        "configured": True,
        "docs_details": [
            "docs describe the SoftDeleteModel abstract base class and its purpose",
            "docs explain the is_deleted and deleted_at field semantics and defaults",
            "docs cover the SoftDeleteManager and its filtered get_queryset override",
            "docs list all available managers: objects, all_with_deleted, deleted_only",
            "docs include an architecture decision record for choosing soft-delete",
            "docs are maintained in Markdown under docs/architecture/soft-delete.md",
        ],
        "guideline_details": [
            "guideline recommends using soft_delete() over hard_delete() by default",
            "guideline warns against bypassing the delete override with raw SQL",
            "guideline requires GDPR hard-delete for personally identifiable data",
            "guideline mandates unit tests for any model extending SoftDeleteModel",
            "guideline advises adding deleted_at to admin list_display for visibility",
            "guideline follows the project contribution standards in CONTRIBUTING.md",
        ],
        "example_details": [
            "example shows creating a concrete model that extends SoftDeleteModel",
            "example demonstrates calling instance.soft_delete() in a view function",
            "example demonstrates calling instance.restore() in an admin action",
            "example shows querying Model.all_with_deleted.all() for audit reports",
            "example shows querying Model.deleted_only.all() for trash bin views",
            "example includes a complete pytest test case for the soft-delete flow",
        ],
    }
    logger.debug(
        "soft delete docs config: docs_details=%d, guideline_details=%d",
        len(config["docs_details"]),
        len(config["guideline_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-D: AuditModel – Tasks 45-52 (Model, Fields & Manager)
# ---------------------------------------------------------------------------


def get_audit_file_config() -> dict:
    """Return audit file configuration.

    SubPhase-03, Group-D, Task 45.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "audit.py file is located at backend/apps/core/models/audit.py",
            "audit.py file defines the AuditModel abstract base class",
            "audit.py file imports Django models and settings for FK references",
            "audit.py file follows the single-responsibility file naming convention",
            "audit.py file is included in the models __init__.py public exports",
            "audit.py file contains module-level docstring describing its purpose",
        ],
        "structure_details": [
            "structure places audit.py alongside base.py and timestamped.py",
            "structure keeps one abstract model per file for maintainability",
            "structure uses __all__ to control public exports from the module",
            "structure imports AuditManager from the managers sub-package",
            "structure follows the project directory layout defined in docs",
            "structure separates model definition from business logic helpers",
        ],
        "documentation_details": [
            "documentation includes a module docstring explaining AuditModel purpose",
            "documentation lists all fields defined in the AuditModel class",
            "documentation references the related AuditManager and its queryset",
            "documentation links to the architecture decision record for auditing",
            "documentation follows NumPy-style docstring conventions for classes",
            "documentation is kept in sync with docs/architecture/audit-model.md",
        ],
    }
    logger.debug(
        "audit file config: file_details=%d, structure_details=%d",
        len(config["file_details"]),
        len(config["structure_details"]),
    )
    return config


def get_audit_model_config() -> dict:
    """Return AuditModel configuration.

    SubPhase-03, Group-D, Task 46.
    """
    config: dict = {
        "configured": True,
        "model_details": [
            "AuditModel tracks which user created and last updated each record",
            "AuditModel provides created_by and updated_by foreign key fields",
            "AuditModel inherits from Django models.Model as an abstract base",
            "AuditModel is designed to be mixed with TimeStampedModel via MRO",
            "AuditModel uses AUTH_USER_MODEL setting for portable user references",
            "AuditModel class name follows PascalCase Django model conventions",
        ],
        "inheritance_details": [
            "inheritance declares AuditModel as an abstract Django model class",
            "inheritance allows concrete models to extend AuditModel directly",
            "inheritance supports multiple inheritance with other abstract models",
            "inheritance chain resolves fields from all parent abstract classes",
            "inheritance avoids diamond problem by using Django MRO resolution",
            "inheritance keeps the database schema flat with no extra join tables",
        ],
        "abstraction_details": [
            "abstraction sets Meta.abstract to True so no database table is created",
            "abstraction provides reusable audit fields across all concrete models",
            "abstraction defines default ordering by created_by field for consistency",
            "abstraction attaches AuditManager as the default objects manager",
            "abstraction enables project-wide audit trail without code duplication",
            "abstraction is tested via a concrete proxy model in the test suite",
        ],
    }
    logger.debug(
        "audit model config: model_details=%d, inheritance_details=%d",
        len(config["model_details"]),
        len(config["inheritance_details"]),
    )
    return config


def get_created_by_field_config() -> dict:
    """Return created_by field configuration.

    SubPhase-03, Group-D, Task 47.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "created_by is a ForeignKey field pointing to AUTH_USER_MODEL",
            "created_by stores the user who originally created the record",
            "created_by is set once at creation time and not modified afterwards",
            "created_by allows null values for system-generated or migrated records",
            "created_by uses blank=True so admin forms do not require the field",
            "created_by field name follows the snake_case convention for Django",
        ],
        "reference_details": [
            "reference uses settings.AUTH_USER_MODEL for portability across apps",
            "reference avoids hard-coding the User model import path directly",
            "reference supports custom user models defined in the project settings",
            "reference resolves at migration time to the configured user model",
            "reference creates a database-level foreign key constraint for integrity",
            "reference is compatible with Django tenant user model configurations",
        ],
        "behavior_details": [
            "behavior automatically populates created_by via model save override",
            "behavior prevents modification of created_by after initial creation",
            "behavior allows null when the request context has no authenticated user",
            "behavior integrates with Django admin to display the creating user",
            "behavior supports serialization and deserialization in DRF serializers",
            "behavior is validated by unit tests checking field value persistence",
        ],
    }
    logger.debug(
        "created_by field config: field_details=%d, reference_details=%d",
        len(config["field_details"]),
        len(config["reference_details"]),
    )
    return config


def get_updated_by_field_config() -> dict:
    """Return updated_by field configuration.

    SubPhase-03, Group-D, Task 48.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "updated_by is a ForeignKey field pointing to AUTH_USER_MODEL",
            "updated_by stores the user who last modified the record",
            "updated_by is refreshed on every save operation with the current user",
            "updated_by allows null values for system-generated or batch updates",
            "updated_by uses blank=True so admin forms do not require the field",
            "updated_by field name follows the snake_case convention for Django",
        ],
        "reference_details": [
            "reference uses settings.AUTH_USER_MODEL for portability across apps",
            "reference avoids hard-coding the User model import path directly",
            "reference supports custom user models defined in the project settings",
            "reference resolves at migration time to the configured user model",
            "reference creates a database-level foreign key constraint for integrity",
            "reference is compatible with multi-tenant user model configurations",
        ],
        "behavior_details": [
            "behavior automatically populates updated_by via model save override",
            "behavior updates the field on every save including admin panel edits",
            "behavior allows null when the request context has no authenticated user",
            "behavior integrates with Django admin to display the last editing user",
            "behavior supports serialization and deserialization in DRF serializers",
            "behavior is validated by unit tests checking field update persistence",
        ],
    }
    logger.debug(
        "updated_by field config: field_details=%d, reference_details=%d",
        len(config["field_details"]),
        len(config["reference_details"]),
    )
    return config


def get_on_delete_config() -> dict:
    """Return on_delete SET_NULL configuration.

    SubPhase-03, Group-D, Task 49.
    """
    config: dict = {
        "configured": True,
        "config_details": [
            "on_delete is set to models.SET_NULL for created_by and updated_by",
            "on_delete SET_NULL requires the field to have null=True configured",
            "on_delete SET_NULL preserves the record when the user is deleted",
            "on_delete behavior is enforced at the database constraint level",
            "on_delete configuration is defined in the ForeignKey field arguments",
            "on_delete choice is documented in the audit model architecture record",
        ],
        "rationale_details": [
            "rationale for SET_NULL is to avoid cascading data loss on user removal",
            "rationale considers that audit records must survive user account deletion",
            "rationale aligns with GDPR requirements for anonymizing personal data",
            "rationale prefers SET_NULL over PROTECT to allow user deletion flow",
            "rationale prefers SET_NULL over CASCADE to preserve historical records",
            "rationale is reviewed and approved in the architecture decision log",
        ],
        "preservation_details": [
            "preservation ensures audit trail records remain after user deletion",
            "preservation sets the FK value to NULL instead of removing the row",
            "preservation allows reporting queries to handle NULL user references",
            "preservation maintains referential integrity at the database level",
            "preservation supports compliance auditing even for deleted user accounts",
            "preservation is validated by integration tests simulating user deletion",
        ],
    }
    logger.debug(
        "on_delete config: config_details=%d, rationale_details=%d",
        len(config["config_details"]),
        len(config["rationale_details"]),
    )
    return config


def get_related_name_pattern_config() -> dict:
    """Return related_name pattern configuration.

    SubPhase-03, Group-D, Task 50.
    """
    config: dict = {
        "configured": True,
        "pattern_details": [
            "related_name uses %(class)s_created pattern for created_by field",
            "related_name uses %(class)s_updated pattern for updated_by field",
            "related_name pattern resolves to the concrete model class name at runtime",
            "related_name avoids clashes between models inheriting AuditModel",
            "related_name follows Django documentation recommended pattern syntax",
            "related_name pattern is defined inline in the ForeignKey field arguments",
        ],
        "usage_details": [
            "usage allows reverse lookups from User to all records they created",
            "usage allows reverse lookups from User to all records they last updated",
            "usage enables querying user.modelname_created.all() for audit reports",
            "usage enables querying user.modelname_updated.all() for activity logs",
            "usage supports Django ORM select_related and prefetch_related calls",
            "usage is demonstrated in the project developer documentation examples",
        ],
        "convention_details": [
            "convention uses lowercase model name with underscore action suffix",
            "convention ensures unique related names across the entire project",
            "convention is enforced by Django system checks at startup validation",
            "convention aligns with the project field naming standards document",
            "convention avoids generic names like related_audit to prevent confusion",
            "convention is verified by linting rules in the CI pipeline checks",
        ],
    }
    logger.debug(
        "related_name pattern config: pattern_details=%d, usage_details=%d",
        len(config["pattern_details"]),
        len(config["usage_details"]),
    )
    return config


def get_audit_manager_config() -> dict:
    """Return AuditManager configuration.

    SubPhase-03, Group-D, Task 51.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "AuditManager extends Django BaseManager for audit-aware queries",
            "AuditManager is assigned as the default objects manager on AuditModel",
            "AuditManager provides helper methods for user-based record filtering",
            "AuditManager is defined in backend/apps/core/managers/audit.py module",
            "AuditManager follows the naming convention of ModelName plus Manager",
            "AuditManager is exported via the managers __init__.py public API",
        ],
        "filter_details": [
            "filter provides created_by_user method accepting a user instance",
            "filter provides updated_by_user method accepting a user instance",
            "filter returns a QuerySet scoped to records matching the given user",
            "filter methods chain with standard Django ORM queryset operations",
            "filter implementation uses self.get_queryset().filter() internally",
            "filter methods are tested with factory-generated user and record data",
        ],
        "query_details": [
            "query optimization uses select_related on created_by and updated_by",
            "query methods return standard Django QuerySet for further chaining",
            "query results respect any additional manager filters already applied",
            "query performance is monitored via django-debug-toolbar in development",
            "query methods support both synchronous and async Django ORM contexts",
            "query interface is documented in the AuditManager class docstring",
        ],
    }
    logger.debug(
        "audit manager config: manager_details=%d, filter_details=%d",
        len(config["manager_details"]),
        len(config["filter_details"]),
    )
    return config


def get_created_by_user_filter_config() -> dict:
    """Return created_by_user() filter configuration.

    SubPhase-03, Group-D, Task 52.
    """
    config: dict = {
        "configured": True,
        "filter_details": [
            "created_by_user filter accepts a Django user instance as argument",
            "created_by_user filter returns records where created_by equals the user",
            "created_by_user filter is defined on the AuditManager class",
            "created_by_user filter delegates to get_queryset().filter() internally",
            "created_by_user filter supports chaining with other queryset methods",
            "created_by_user filter raises TypeError if argument is not a user",
        ],
        "usage_details": [
            "usage allows views to scope queries to records created by current user",
            "usage integrates with DRF permission classes for object-level access",
            "usage enables dashboard widgets showing user-specific record counts",
            "usage supports admin list filters for narrowing records by creator",
            "usage is demonstrated in the project API view documentation examples",
            "usage simplifies multi-tenant record ownership verification queries",
        ],
        "reporting_details": [
            "reporting uses created_by_user to generate per-user activity summaries",
            "reporting aggregates record counts grouped by creating user identity",
            "reporting supports date-range filtering combined with user filtering",
            "reporting exports user audit data to CSV for compliance review needs",
            "reporting integrates with the project analytics dashboard components",
            "reporting is validated by end-to-end tests covering the full pipeline",
        ],
    }
    logger.debug(
        "created_by_user filter config: filter_details=%d, usage_details=%d",
        len(config["filter_details"]),
        len(config["usage_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-D: AuditModel – Tasks 53-58 (Mixin, Methods & Tests)
# ---------------------------------------------------------------------------


def get_updated_by_user_filter_config() -> dict:
    """Return updated_by_user() filter configuration.

    SubPhase-03, Group-D, Task 53.
    """
    config: dict = {
        "configured": True,
        "filter_details": [
            "updated_by_user filter accepts a Django user instance as argument",
            "updated_by_user filter returns records where updated_by equals the user",
            "updated_by_user filter is defined on the AuditManager class",
            "updated_by_user filter delegates to get_queryset().filter() internally",
            "updated_by_user filter supports chaining with other queryset methods",
            "updated_by_user filter raises TypeError if argument is not a user",
        ],
        "usage_details": [
            "usage allows views to scope queries to records updated by current user",
            "usage integrates with DRF permission classes for update-level access",
            "usage enables dashboard widgets showing user-specific update counts",
            "usage supports admin list filters for narrowing records by last editor",
            "usage is demonstrated in the project API view documentation examples",
            "usage simplifies multi-tenant record modification verification queries",
        ],
        "reporting_details": [
            "reporting uses updated_by_user to generate per-user update summaries",
            "reporting aggregates update counts grouped by modifying user identity",
            "reporting supports date-range filtering combined with updater filtering",
            "reporting exports user update audit data to CSV for compliance review",
            "reporting integrates with the project analytics dashboard components",
            "reporting is validated by end-to-end tests covering the update pipeline",
        ],
    }
    logger.debug(
        "updated_by_user filter config: filter_details=%d, usage_details=%d",
        len(config["filter_details"]),
        len(config["usage_details"]),
    )
    return config


def get_audit_mixin_config() -> dict:
    """Return AuditMixin configuration for views and serializers.

    SubPhase-03, Group-D, Task 54.
    """
    config: dict = {
        "configured": True,
        "mixin_details": [
            "AuditMixin automatically sets created_by on object creation",
            "AuditMixin automatically sets updated_by on object update",
            "AuditMixin extracts the current user from the request context",
            "AuditMixin is designed for use with DRF viewsets and serializers",
            "AuditMixin overrides perform_create to inject audit fields",
            "AuditMixin overrides perform_update to inject audit fields",
        ],
        "responsibility_details": [
            "responsibility ensures audit fields are populated transparently",
            "responsibility separates audit logic from business view logic",
            "responsibility provides a single mixin usable across all viewsets",
            "responsibility delegates field assignment to the serializer save method",
            "responsibility validates that the request user is authenticated first",
            "responsibility logs audit field assignments for debugging purposes",
        ],
        "integration_details": [
            "integration works with any model inheriting from AuditModel",
            "integration supports both ModelViewSet and generic API views",
            "integration is compatible with nested serializer workflows",
            "integration allows optional override via perform_create hook",
            "integration is tested with DRF's APIRequestFactory in unit tests",
            "integration is documented in the project mixins reference guide",
        ],
    }
    logger.debug(
        "AuditMixin config: mixin_details=%d, responsibility_details=%d",
        len(config["mixin_details"]),
        len(config["responsibility_details"]),
    )
    return config


def get_set_created_by_method_config() -> dict:
    """Return set_created_by method configuration.

    SubPhase-03, Group-D, Task 55.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "set_created_by method assigns the creating user to created_by field",
            "set_created_by method is called during the model save on creation",
            "set_created_by method accepts a user instance as its sole argument",
            "set_created_by method skips assignment if created_by is already set",
            "set_created_by method is defined on the AuditModel base class",
            "set_created_by method returns None after performing the assignment",
        ],
        "behavior_details": [
            "behavior only executes when the model instance has no primary key yet",
            "behavior raises ValueError when a None user is explicitly provided",
            "behavior preserves the original created_by if record already exists",
            "behavior is idempotent and can be called multiple times safely",
            "behavior integrates with Django signals for pre-save audit tracking",
            "behavior is covered by unit tests verifying correct user assignment",
        ],
        "trigger_details": [
            "trigger is invoked from the AuditMixin perform_create method",
            "trigger fires before the database INSERT statement is executed",
            "trigger can be manually called in management command record creation",
            "trigger supports bulk creation through iterator-based assignment",
            "trigger logs the creating user identity at the DEBUG log level",
            "trigger is documented in the AuditModel method reference guide",
        ],
    }
    logger.debug(
        "set_created_by method config: method_details=%d, behavior_details=%d",
        len(config["method_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_set_updated_by_method_config() -> dict:
    """Return set_updated_by method configuration.

    SubPhase-03, Group-D, Task 56.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "set_updated_by method assigns the modifying user to updated_by field",
            "set_updated_by method is called during the model save on every update",
            "set_updated_by method accepts a user instance as its sole argument",
            "set_updated_by method always overwrites the previous updated_by value",
            "set_updated_by method is defined on the AuditModel base class",
            "set_updated_by method returns None after performing the assignment",
        ],
        "behavior_details": [
            "behavior executes on every save regardless of whether it is an update",
            "behavior raises ValueError when a None user is explicitly provided",
            "behavior updates the updated_by field even if no other fields changed",
            "behavior is idempotent and can be called multiple times safely",
            "behavior integrates with Django signals for pre-save audit tracking",
            "behavior is covered by unit tests verifying correct user assignment",
        ],
        "trigger_details": [
            "trigger is invoked from the AuditMixin perform_update method",
            "trigger fires before the database UPDATE statement is executed",
            "trigger can be manually called in management command record updates",
            "trigger supports bulk update through iterator-based assignment",
            "trigger logs the modifying user identity at the DEBUG log level",
            "trigger is documented in the AuditModel method reference guide",
        ],
    }
    logger.debug(
        "set_updated_by method config: method_details=%d, behavior_details=%d",
        len(config["method_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_audit_tests_config() -> dict:
    """Return Audit tests configuration.

    SubPhase-03, Group-D, Task 57.
    """
    config: dict = {
        "configured": True,
        "test_details": [
            "audit tests verify that created_by is set on new record creation",
            "audit tests verify that updated_by is set on record modification",
            "audit tests confirm AuditMixin integrates with DRF viewsets properly",
            "audit tests confirm AuditManager filters by created_by user correctly",
            "audit tests confirm AuditManager filters by updated_by user correctly",
            "audit tests validate that on_delete SET_NULL protects audit references",
        ],
        "coverage_details": [
            "coverage includes unit tests for each AuditModel method independently",
            "coverage includes integration tests for mixin-to-model interaction",
            "coverage includes edge case tests for anonymous user submissions",
            "coverage includes permission tests for audit field read-only access",
            "coverage includes regression tests for cascading user deletions",
            "coverage goal is one hundred percent of audit-related code paths",
        ],
        "scenario_details": [
            "scenario tests creation with an authenticated standard user account",
            "scenario tests update by a different user than the original creator",
            "scenario tests querying records filtered by a specific creating user",
            "scenario tests querying records filtered by a specific updating user",
            "scenario tests that audit fields are excluded from serializer input",
            "scenario tests audit field presence in the API response output data",
        ],
    }
    logger.debug(
        "Audit tests config: test_details=%d, coverage_details=%d",
        len(config["test_details"]),
        len(config["coverage_details"]),
    )
    return config


def get_audit_docs_config() -> dict:
    """Return Audit documentation configuration.

    SubPhase-03, Group-D, Task 58.
    """
    config: dict = {
        "configured": True,
        "docs_details": [
            "audit docs describe the AuditModel abstract base class purpose",
            "audit docs list all audit-related fields with types and constraints",
            "audit docs explain the AuditMixin usage pattern for DRF views",
            "audit docs include a quick-start example for new model integration",
            "audit docs cover the AuditManager query helper methods reference",
            "audit docs are maintained in the architecture documentation folder",
        ],
        "guideline_details": [
            "guideline recommends always inheriting AuditModel for tracked models",
            "guideline recommends using AuditMixin on all viewsets that write data",
            "guideline recommends never setting audit fields manually in views",
            "guideline recommends using read-only serializer fields for audit data",
            "guideline recommends writing tests for audit field population logic",
            "guideline recommends reviewing audit data during code review process",
        ],
        "example_details": [
            "example shows a model class inheriting from AuditModel directly",
            "example shows a viewset class using AuditMixin for auto population",
            "example shows a serializer declaring audit fields as read-only",
            "example shows a queryset filtered by created_by_user helper method",
            "example shows a queryset filtered by updated_by_user helper method",
            "example shows admin configuration displaying audit fields inline",
        ],
    }
    logger.debug(
        "Audit docs config: docs_details=%d, guideline_details=%d",
        len(config["docs_details"]),
        len(config["guideline_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-E: UUID & TenantScoped Models – Tasks 59-66 (UUID & TenantScoped Base)
# ---------------------------------------------------------------------------


def get_uuid_model_file_config() -> dict:
    """Return UUID model file configuration.

    SubPhase-03, Group-E, Task 59.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "uuid_model.py file resides in backend/apps/core/models directory",
            "uuid_model.py defines the UUIDModel abstract base class for UUID PKs",
            "uuid_model.py imports uuid module from Python standard library",
            "uuid_model.py imports models from django.db for field definitions",
            "uuid_model.py follows single-responsibility with one model per file",
            "uuid_model.py is exported through the models __init__.py module",
        ],
        "structure_details": [
            "file structure starts with module docstring and import statements",
            "file structure places the UUIDModel class as the primary export",
            "file structure includes a Meta inner class with abstract equals True",
            "file structure defines exactly one field which is the UUID primary key",
            "file structure follows project convention of lowercase underscore naming",
            "file structure keeps the module under fifty lines for readability",
        ],
        "documentation_details": [
            "documentation includes a module-level docstring explaining UUID usage",
            "documentation includes a class-level docstring for UUIDModel purpose",
            "documentation references Django UUID field best practices and rationale",
            "documentation notes that UUID primary keys prevent enumeration attacks",
            "documentation explains when to inherit from UUIDModel in the project",
            "documentation links to the architecture decision record for UUID PKs",
        ],
    }
    logger.debug(
        "UUID model file config: file_details=%d, structure_details=%d",
        len(config["file_details"]),
        len(config["structure_details"]),
    )
    return config


def get_uuid_model_class_config() -> dict:
    """Return UUIDModel class configuration.

    SubPhase-03, Group-E, Task 60.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "UUIDModel inherits from django.db.models.Model as an abstract base",
            "UUIDModel provides a UUID version four primary key to all subclasses",
            "UUIDModel sets Meta abstract to True so no database table is created",
            "UUIDModel can be combined with TimeStampedModel via multiple inheritance",
            "UUIDModel replaces Django default auto-incrementing integer primary key",
            "UUIDModel is registered in the core models package for project-wide use",
        ],
        "usage_details": [
            "usage requires inheriting UUIDModel as the first parent in MRO order",
            "usage provides globally unique identifiers suitable for distributed systems",
            "usage eliminates the need to define id fields on each concrete model",
            "usage is recommended for all tenant-scoped models in the POS application",
            "usage simplifies API URL patterns by using UUID instead of integer PKs",
            "usage supports database sharding without primary key collision risks",
        ],
        "abstraction_details": [
            "abstraction ensures consistent primary key type across all applications",
            "abstraction centralizes UUID field definition to avoid code duplication",
            "abstraction allows subclasses to override Meta options like ordering",
            "abstraction keeps the base class minimal with only the id field defined",
            "abstraction follows the DRY principle for primary key standardization",
            "abstraction provides a single point of change for UUID configuration",
        ],
    }
    logger.debug(
        "UUIDModel class config: class_details=%d, usage_details=%d",
        len(config["class_details"]),
        len(config["usage_details"]),
    )
    return config


def get_uuid_field_config() -> dict:
    """Return UUID primary key field configuration.

    SubPhase-03, Group-E, Task 61.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "UUID field is defined as models.UUIDField with primary_key set to True",
            "UUID field replaces the default BigAutoField provided by Django models",
            "UUID field stores a 128-bit universally unique identifier value",
            "UUID field uses a hyphenated 36-character string representation",
            "UUID field is indexed automatically as the primary key of the table",
            "UUID field column is named id following Django primary key convention",
        ],
        "type_details": [
            "type uses PostgreSQL native uuid column type for efficient storage",
            "type stores exactly 16 bytes in binary format on PostgreSQL backend",
            "type is compatible with Django REST Framework UUID serializer field",
            "type supports exact lookup, in lookup, and isnull query expressions",
            "type is validated by Django to ensure proper UUID format on input",
            "type renders as a string in JSON API responses for client consumption",
        ],
        "behavior_details": [
            "behavior generates a new UUID automatically when no value is provided",
            "behavior prevents modification of the primary key after initial creation",
            "behavior ensures uniqueness across all rows without database sequences",
            "behavior supports bulk_create operations with pre-generated UUID values",
            "behavior works with Django foreign key fields referencing UUID primaries",
            "behavior is compatible with Django admin interface for record lookups",
        ],
    }
    logger.debug(
        "UUID field config: field_details=%d, type_details=%d",
        len(config["field_details"]),
        len(config["type_details"]),
    )
    return config


def get_uuid_default_config() -> dict:
    """Return uuid4 default configuration.

    SubPhase-03, Group-E, Task 62.
    """
    config: dict = {
        "configured": True,
        "default_details": [
            "default is set to uuid.uuid4 callable reference without parentheses",
            "default generates a random UUID version four on each model instantiation",
            "default uses Python standard library uuid module for generation",
            "default callable is evaluated at save time not at class definition time",
            "default ensures each new object receives a unique identifier automatically",
            "default value can be overridden by explicitly passing an id on creation",
        ],
        "rationale_details": [
            "rationale prefers uuid4 over uuid1 to avoid exposing MAC addresses",
            "rationale prefers uuid4 for its strong randomness and unpredictability",
            "rationale avoids sequential identifiers to prevent enumeration attacks",
            "rationale aligns with OWASP recommendations for resource identifiers",
            "rationale supports distributed ID generation without coordination",
            "rationale follows Django documentation recommendation for UUID fields",
        ],
        "uniqueness_details": [
            "uniqueness probability of collision is astronomically low with uuid4",
            "uniqueness is enforced at database level by the primary key constraint",
            "uniqueness holds across tables, databases, and distributed environments",
            "uniqueness does not depend on a centralized sequence or counter",
            "uniqueness is maintained even during concurrent bulk insert operations",
            "uniqueness guarantee makes UUIDs safe for cross-service references",
        ],
    }
    logger.debug(
        "UUID default config: default_details=%d, rationale_details=%d",
        len(config["default_details"]),
        len(config["rationale_details"]),
    )
    return config


def get_uuid_editable_config() -> dict:
    """Return editable=False configuration.

    SubPhase-03, Group-E, Task 63.
    """
    config: dict = {
        "configured": True,
        "setting_details": [
            "editable is set to False on the UUID primary key field definition",
            "editable False excludes the field from ModelForm fields by default",
            "editable False hides the field from Django admin add and change forms",
            "editable False prevents accidental modification through form submissions",
            "editable False is combined with primary_key True for complete protection",
            "editable setting follows Django best practice for auto-generated fields",
        ],
        "behavior_details": [
            "behavior ensures API serializers treat UUID as a read-only output field",
            "behavior prevents clients from submitting custom UUID values via forms",
            "behavior allows programmatic assignment of UUID in application code",
            "behavior does not affect queryset filter or lookup operations on the field",
            "behavior keeps the field visible in API responses as a read-only value",
            "behavior works with DRF serializer read_only_fields for explicit control",
        ],
        "immutability_details": [
            "immutability protects the primary key from being changed after creation",
            "immutability ensures foreign key relationships remain stable over time",
            "immutability prevents data integrity issues from primary key modifications",
            "immutability is enforced at the Django model layer before database access",
            "immutability applies to both admin interface and REST API update endpoints",
            "immutability supports audit trail consistency by keeping IDs permanent",
        ],
    }
    logger.debug(
        "UUID editable config: setting_details=%d, behavior_details=%d",
        len(config["setting_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_uuid_tests_config() -> dict:
    """Return UUID tests configuration.

    SubPhase-03, Group-E, Task 64.
    """
    config: dict = {
        "configured": True,
        "test_details": [
            "UUID tests verify that new instances receive a valid uuid4 primary key",
            "UUID tests verify that the id field is a UUIDField with primary_key True",
            "UUID tests verify that editable is False on the UUID primary key field",
            "UUID tests confirm the default callable is uuid.uuid4 without parentheses",
            "UUID tests confirm the model Meta class has abstract set to True",
            "UUID tests confirm UUIDModel is importable from the core models package",
        ],
        "assertion_details": [
            "assertions check that the generated id is an instance of uuid.UUID type",
            "assertions check that two instances have different primary key values",
            "assertions check that the id field is not included in editable fields",
            "assertions check that the UUID version is four for random generation",
            "assertions check that the string representation has 36 characters total",
            "assertions check that the primary key is preserved after a save and refresh",
        ],
        "coverage_details": [
            "coverage includes creation of concrete subclass for abstract model testing",
            "coverage includes field introspection tests using model _meta API access",
            "coverage includes serialization round-trip test for UUID string conversion",
            "coverage includes negative test for attempting to set editable to True",
            "coverage includes integration test with Django ORM query by UUID value",
            "coverage target is one hundred percent of UUIDModel code paths",
        ],
    }
    logger.debug(
        "UUID tests config: test_details=%d, assertion_details=%d",
        len(config["test_details"]),
        len(config["assertion_details"]),
    )
    return config


def get_tenant_scoped_file_config() -> dict:
    """Return tenant scoped file configuration.

    SubPhase-03, Group-E, Task 65.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "tenant_scoped.py file resides in backend/apps/core/models directory",
            "tenant_scoped.py defines the TenantScopedModel abstract base class",
            "tenant_scoped.py imports TenantMixin or tenant FK for schema isolation",
            "tenant_scoped.py imports models from django.db for field definitions",
            "tenant_scoped.py follows single-responsibility with one model per file",
            "tenant_scoped.py is exported through the models __init__.py module",
        ],
        "structure_details": [
            "file structure starts with module docstring and required import statements",
            "file structure places TenantScopedModel class as the primary export",
            "file structure includes a Meta inner class with abstract equals True",
            "file structure defines a tenant foreign key field for data isolation",
            "file structure follows project convention of lowercase underscore naming",
            "file structure remains concise and focused on tenant scoping concerns",
        ],
        "documentation_details": [
            "documentation includes a module-level docstring explaining tenant scoping",
            "documentation includes a class-level docstring for TenantScopedModel purpose",
            "documentation references the multi-tenancy architecture decision record",
            "documentation notes that all business data models should inherit this class",
            "documentation explains the relationship between tenant FK and schema routing",
            "documentation links to the multi-tenancy guide in project documentation",
        ],
    }
    logger.debug(
        "Tenant scoped file config: file_details=%d, structure_details=%d",
        len(config["file_details"]),
        len(config["structure_details"]),
    )
    return config


def get_tenant_scoped_model_config() -> dict:
    """Return TenantScopedModel configuration.

    SubPhase-03, Group-E, Task 66.
    """
    config: dict = {
        "configured": True,
        "model_details": [
            "TenantScopedModel inherits from django.db.models.Model as abstract base",
            "TenantScopedModel provides a tenant foreign key for data isolation",
            "TenantScopedModel sets Meta abstract to True so no table is created",
            "TenantScopedModel can be combined with UUIDModel and TimeStampedModel",
            "TenantScopedModel ensures every business record links to a specific tenant",
            "TenantScopedModel is the foundation for multi-tenant data architecture",
        ],
        "usage_details": [
            "usage requires inheriting TenantScopedModel in all tenant-specific models",
            "usage automatically associates new records with the current active tenant",
            "usage enables queryset filtering by tenant for data isolation enforcement",
            "usage is mandatory for all models storing business-specific data records",
            "usage supports custom managers that automatically filter by active tenant",
            "usage integrates with middleware that sets the current tenant context",
        ],
        "scoping_details": [
            "scoping prevents cross-tenant data leakage at the model query level",
            "scoping uses a foreign key to the Tenant model for explicit association",
            "scoping is enforced by default managers filtering on the tenant field",
            "scoping supports superuser access to all tenants via special manager method",
            "scoping works with Django admin by filtering querysets per tenant context",
            "scoping aligns with the shared-database shared-schema tenancy strategy",
        ],
    }
    logger.debug(
        "TenantScopedModel config: model_details=%d, usage_details=%d",
        len(config["model_details"]),
        len(config["usage_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-E: UUID & TenantScoped Models – Tasks 67-74 (Manager, Integration & Tests)
# ---------------------------------------------------------------------------


def get_tenant_scoped_manager_config() -> dict:
    """Return TenantScopedManager configuration.

    SubPhase-03, Group-E, Task 67.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "manager inherits from Django BaseManager to provide tenant filtering",
            "manager is assigned as the default manager on TenantScopedModel subclass",
            "manager overrides get_queryset to inject tenant filtering automatically",
            "manager provides a clean API so callers need not filter by tenant manually",
            "manager supports chaining with standard Django queryset methods seamlessly",
            "manager is defined in the managers module alongside other custom managers",
        ],
        "filtering_details": [
            "filtering restricts all querysets to the currently active tenant context",
            "filtering uses the tenant foreign key field for efficient database queries",
            "filtering is transparent to consuming code and requires no explicit calls",
            "filtering ensures data isolation between tenants at the ORM query level",
            "filtering is applied before any additional queryset filters are evaluated",
            "filtering leverages database indexes on the tenant field for performance",
        ],
        "context_details": [
            "context is retrieved from thread-local storage set by tenant middleware",
            "context holds the current tenant instance for the duration of the request",
            "context is validated to ensure a tenant is always set before querying data",
            "context supports override for management commands running outside requests",
            "context is cleared after each request to prevent tenant data leakage",
            "context integrates with django-tenants middleware for seamless operation",
        ],
    }
    logger.debug(
        "TenantScopedManager config: manager_details=%d, filtering_details=%d",
        len(config["manager_details"]),
        len(config["filtering_details"]),
    )
    return config


def get_get_queryset_override_config() -> dict:
    """Return get_queryset override configuration.

    SubPhase-03, Group-E, Task 68.
    """
    config: dict = {
        "configured": True,
        "override_details": [
            "override replaces the default get_queryset to add tenant filtering logic",
            "override calls super().get_queryset() first to preserve base queryset behavior",
            "override applies a .filter(tenant=current_tenant) clause to every query",
            "override is the single enforcement point for tenant-level data isolation",
            "override is defined on TenantScopedManager and inherited by subclasses",
            "override returns a standard Django QuerySet compatible with all ORM methods",
        ],
        "tenant_details": [
            "tenant is resolved from the current request context via middleware helper",
            "tenant value is a foreign key reference to the Tenant model primary key",
            "tenant filtering is skipped when the context indicates a superuser override",
            "tenant must be set before any queryset evaluation or an error is raised",
            "tenant field lookup uses exact match for precise data boundary enforcement",
            "tenant resolution supports both synchronous and asynchronous request flows",
        ],
        "behavior_details": [
            "behavior ensures no cross-tenant data is ever returned in normal queries",
            "behavior is automatic and does not require developer intervention per query",
            "behavior raises an exception if tenant context is missing during evaluation",
            "behavior can be bypassed using the all_tenants manager for admin operations",
            "behavior is tested with multi-tenant fixtures to verify data isolation",
            "behavior is logged at debug level for troubleshooting filtering issues",
        ],
    }
    logger.debug(
        "get_queryset override config: override_details=%d, tenant_details=%d",
        len(config["override_details"]),
        len(config["tenant_details"]),
    )
    return config


def get_django_tenants_integration_config() -> dict:
    """Return django-tenants integration configuration.

    SubPhase-03, Group-E, Task 69.
    """
    config: dict = {
        "configured": True,
        "integration_details": [
            "integration uses django-tenants library for schema-based multi-tenancy",
            "integration configures SHARED_APPS and TENANT_APPS in Django settings",
            "integration provides middleware to set the current tenant per request",
            "integration supports both shared and tenant-specific database schemas",
            "integration manages tenant lifecycle including creation and deletion",
            "integration hooks into Django URL routing for tenant-aware dispatching",
        ],
        "context_details": [
            "context middleware extracts tenant from the request hostname or header",
            "context sets connection schema to the resolved tenant for the request",
            "context is available globally through django-tenants utility functions",
            "context supports fallback to the public schema for shared resources",
            "context is thread-safe and works correctly under concurrent requests",
            "context cleanup occurs automatically at the end of each request cycle",
        ],
        "optionality_details": [
            "optionality allows running without django-tenants for single-tenant mode",
            "optionality uses feature flags to toggle tenant-aware behavior at runtime",
            "optionality provides a no-op middleware stub when multi-tenancy is disabled",
            "optionality ensures models remain functional in both single and multi modes",
            "optionality is configured through environment variables for easy switching",
            "optionality supports gradual migration from single-tenant to multi-tenant",
        ],
    }
    logger.debug(
        "django-tenants integration config: integration_details=%d, context_details=%d",
        len(config["integration_details"]),
        len(config["context_details"]),
    )
    return config


def get_for_tenant_method_config() -> dict:
    """Return for_tenant() method configuration.

    SubPhase-03, Group-E, Task 70.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "method is defined on TenantScopedManager for explicit tenant filtering",
            "method accepts a tenant instance or tenant primary key as its argument",
            "method returns a queryset filtered to the specified tenant only",
            "method allows querying data for a specific tenant outside request context",
            "method is useful in management commands and background task processing",
            "method chains with all standard Django queryset methods after filtering",
        ],
        "query_details": [
            "query uses the tenant foreign key field for efficient database lookups",
            "query benefits from the database index on the tenant field for speed",
            "query returns an empty queryset when the specified tenant has no records",
            "query supports both integer primary keys and UUID tenant identifiers",
            "query can combine with additional filters for complex data retrieval",
            "query is evaluated lazily following standard Django queryset semantics",
        ],
        "admin_details": [
            "admin views use for_tenant to scope querysets in the Django admin site",
            "admin integration ensures list views show only current tenant records",
            "admin inline models are also filtered using for_tenant for consistency",
            "admin bulk actions respect the tenant scope applied by for_tenant method",
            "admin search results are limited to the tenant context set by middleware",
            "admin export functionality respects tenant filtering to prevent leakage",
        ],
    }
    logger.debug(
        "for_tenant() method config: method_details=%d, query_details=%d",
        len(config["method_details"]),
        len(config["query_details"]),
    )
    return config


def get_tenant_field_config() -> dict:
    """Return tenant FK field configuration.

    SubPhase-03, Group-E, Task 71.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is a ForeignKey pointing to the Tenant model in the tenants app",
            "field uses on_delete=models.CASCADE to remove data when tenant is deleted",
            "field has db_index=True for efficient filtering in tenant-scoped queries",
            "field is defined on the abstract TenantScopedModel for inheritance by all",
            "field name is 'tenant' following the project naming convention for FK fields",
            "field is required and does not allow null values for data integrity",
        ],
        "reference_details": [
            "reference uses a string path 'tenants.Tenant' to avoid circular imports",
            "reference supports lazy loading through Django app registry resolution",
            "reference is validated during Django system checks at startup time",
            "reference ensures the Tenant model exists before migration is applied",
            "reference related_name uses '+' to suppress reverse relation creation",
            "reference is consistent across all tenant-scoped models in the project",
        ],
        "behavior_details": [
            "behavior automatically sets the tenant field from request context on save",
            "behavior prevents manual override of the tenant field in normal operations",
            "behavior supports explicit tenant assignment in management command context",
            "behavior raises a validation error if tenant is missing during model clean",
            "behavior is enforced at both the Django model and database constraint level",
            "behavior ensures referential integrity between tenant and scoped records",
        ],
    }
    logger.debug(
        "tenant FK field config: field_details=%d, reference_details=%d",
        len(config["field_details"]),
        len(config["reference_details"]),
    )
    return config


def get_tenant_scoped_tests_config() -> dict:
    """Return TenantScoped tests configuration.

    SubPhase-03, Group-E, Task 72.
    """
    config: dict = {
        "configured": True,
        "test_details": [
            "tests verify that TenantScopedModel is abstract and cannot be instantiated",
            "tests verify the tenant foreign key field exists with correct attributes",
            "tests verify TenantScopedManager filters queryset by current tenant",
            "tests verify for_tenant method returns data for the specified tenant only",
            "tests verify cross-tenant data isolation prevents unauthorized data access",
            "tests verify the model is importable from the core models package",
        ],
        "scenario_details": [
            "scenario creates two tenants with separate data sets for isolation testing",
            "scenario tests that default manager excludes records from other tenants",
            "scenario tests that superuser override manager can access all tenant data",
            "scenario tests that for_tenant returns empty queryset for missing tenant",
            "scenario tests that cascading delete removes all scoped model records",
            "scenario tests that concurrent requests maintain correct tenant isolation",
        ],
        "coverage_details": [
            "coverage includes unit tests for TenantScopedManager get_queryset method",
            "coverage includes integration tests with Django test client and middleware",
            "coverage includes field introspection tests using model _meta API access",
            "coverage includes edge case tests for missing or invalid tenant context",
            "coverage includes performance tests for indexed tenant field lookups",
            "coverage target is one hundred percent of TenantScopedModel code paths",
        ],
    }
    logger.debug(
        "TenantScoped tests config: test_details=%d, scenario_details=%d",
        len(config["test_details"]),
        len(config["scenario_details"]),
    )
    return config


def get_uuid_tenant_export_config() -> dict:
    """Return UUID & TenantScoped export configuration.

    SubPhase-03, Group-E, Task 73.
    """
    config: dict = {
        "configured": True,
        "export_details": [
            "export adds UUIDModel to the core models package __init__.py for access",
            "export adds TenantScopedModel to the core models package __init__.py",
            "export adds TenantScopedManager to the core managers package __init__.py",
            "export follows the established pattern of re-exporting from __init__ files",
            "export ensures all base models are discoverable through a single import path",
            "export updates __all__ lists to include the newly exported model classes",
        ],
        "import_details": [
            "import path for UUIDModel is apps.core.models.UUIDModel for consumers",
            "import path for TenantScopedModel is apps.core.models.TenantScopedModel",
            "import path for TenantScopedManager is apps.core.managers.TenantScopedManager",
            "import supports both absolute and relative import styles within the project",
            "import is tested by verifying the symbol is accessible from package level",
            "import avoids circular dependencies by using string references where needed",
        ],
        "usage_details": [
            "usage in app models requires inheriting from both UUIDModel and TenantScoped",
            "usage in serializers references exported models for type annotation clarity",
            "usage in admin classes imports models from the core package for registration",
            "usage in tests imports from the package level for consistency and brevity",
            "usage documentation lists all exported symbols with their import paths",
            "usage is verified by automated import tests in the core test suite",
        ],
    }
    logger.debug(
        "UUID & TenantScoped export config: export_details=%d, import_details=%d",
        len(config["export_details"]),
        len(config["import_details"]),
    )
    return config


def get_uuid_tenant_docs_config() -> dict:
    """Return UUID & TenantScoped documentation configuration.

    SubPhase-03, Group-E, Task 74.
    """
    config: dict = {
        "configured": True,
        "docs_details": [
            "docs describe UUIDModel purpose and usage in the architecture guide",
            "docs describe TenantScopedModel with field and manager documentation",
            "docs include class diagrams showing inheritance hierarchy of base models",
            "docs provide code examples for creating concrete models from base classes",
            "docs are maintained in the docs/architecture/base-models.md file location",
            "docs are linked from the main README for easy developer discoverability",
        ],
        "guideline_details": [
            "guidelines require all new models to inherit from UUIDModel for consistency",
            "guidelines require tenant-specific models to also inherit TenantScopedModel",
            "guidelines mandate running makemigrations after adding new model subclasses",
            "guidelines specify that custom managers must call super().get_queryset first",
            "guidelines recommend using for_tenant in management commands explicitly",
            "guidelines enforce code review checks for proper base model inheritance",
        ],
        "example_details": [
            "example shows a Product model inheriting UUIDModel and TenantScopedModel",
            "example shows a custom manager extending TenantScopedManager with filters",
            "example shows a serializer using the UUID primary key as read-only field",
            "example shows an admin class registering a tenant-scoped model correctly",
            "example shows a management command using for_tenant to process tenant data",
            "example shows a test case creating fixtures for multi-tenant isolation test",
        ],
    }
    logger.debug(
        "UUID & TenantScoped docs config: docs_details=%d, guideline_details=%d",
        len(config["docs_details"]),
        len(config["guideline_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-F: Validators & Utilities – Tasks 75-80 (Validators)
# ---------------------------------------------------------------------------


def get_validators_file_config() -> dict:
    """Return validators file configuration.

    SubPhase-03, Group-F, Task 75.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "validators.py file resides in the apps/core directory of the project",
            "validators.py file contains all custom validator classes for the application",
            "validators.py file is imported by models and serializers that need validation",
            "validators.py file follows Django validator conventions and best practices",
            "validators.py file includes comprehensive docstrings for each validator class",
            "validators.py file is covered by dedicated unit tests in the tests directory",
        ],
        "structure_details": [
            "structure begins with module-level docstring describing validator purpose",
            "structure includes standard library and Django imports at the top section",
            "structure organizes validators alphabetically by class name for readability",
            "structure uses Django ValidationError for all validation failure responses",
            "structure defines __call__ method on each validator for direct invocation",
            "structure exports all validators via __all__ for explicit public interface",
        ],
        "documentation_details": [
            "documentation explains the purpose and scope of each custom validator",
            "documentation includes usage examples showing validator integration patterns",
            "documentation lists accepted and rejected input formats for clarity",
            "documentation references Django official validator documentation links",
            "documentation describes error messages returned on validation failure",
            "documentation notes which model fields typically use each validator",
        ],
    }
    logger.debug(
        "Validators file config: file_details=%d, structure_details=%d",
        len(config["file_details"]),
        len(config["structure_details"]),
    )
    return config


def get_phone_number_validator_config() -> dict:
    """Return PhoneNumberValidator configuration for +94 format.

    SubPhase-03, Group-F, Task 76.
    """
    config: dict = {
        "configured": True,
        "validator_details": [
            "PhoneNumberValidator validates Sri Lankan phone numbers in +94 format",
            "PhoneNumberValidator raises ValidationError for invalid phone patterns",
            "PhoneNumberValidator is used on contact fields across customer and vendor models",
            "PhoneNumberValidator supports both mobile and landline number formats",
            "PhoneNumberValidator strips whitespace and dashes before validation check",
            "PhoneNumberValidator provides a clear error message with expected format",
        ],
        "format_details": [
            "format requires the +94 country code prefix for Sri Lankan numbers",
            "format expects exactly 9 digits following the +94 country code prefix",
            "format supports mobile prefixes such as 70 71 72 75 76 77 78 ranges",
            "format supports landline prefixes such as 11 21 31 for regional areas",
            "format rejects numbers that exceed the maximum allowed digit length",
            "format rejects numbers containing alphabetic or special characters",
        ],
        "variant_details": [
            "variant handles numbers provided with leading zero after country code",
            "variant handles numbers provided without the plus sign prefix symbol",
            "variant handles numbers with spaces between digit groups for readability",
            "variant handles numbers with dashes separating the area and local parts",
            "variant handles numbers provided in full international E.164 format",
            "variant handles numbers stored as strings from form or API submissions",
        ],
    }
    logger.debug(
        "PhoneNumberValidator config: validator_details=%d, format_details=%d",
        len(config["validator_details"]),
        len(config["format_details"]),
    )
    return config


def get_nic_validator_config() -> dict:
    """Return NICValidator configuration for old 9+V/X and new 12-digit formats.

    SubPhase-03, Group-F, Task 77.
    """
    config: dict = {
        "configured": True,
        "validator_details": [
            "NICValidator validates Sri Lankan National Identity Card number formats",
            "NICValidator raises ValidationError when the NIC pattern is incorrect",
            "NICValidator is used on identity fields in customer and employee models",
            "NICValidator supports both old format and new format NIC numbers",
            "NICValidator normalizes input by stripping whitespace before checking",
            "NICValidator provides descriptive error messages indicating valid formats",
        ],
        "format_details": [
            "format for old NIC consists of 9 digits followed by V or X character",
            "format for new NIC consists of exactly 12 numeric digits without letters",
            "format validation is case-insensitive for the trailing V or X letter",
            "format rejects NIC numbers that contain special characters or spaces",
            "format rejects NIC numbers with incorrect total digit count overall",
            "format ensures the numeric portion falls within valid date-based ranges",
        ],
        "acceptance_details": [
            "acceptance allows old format like 901234567V as a valid NIC number",
            "acceptance allows old format like 901234567X as a valid NIC number",
            "acceptance allows new format like 200012345678 as a valid NIC number",
            "acceptance allows lowercase v and x suffixes for old format tolerance",
            "acceptance rejects strings shorter than the minimum required NIC length",
            "acceptance rejects strings with mixed alphabetic and numeric characters",
        ],
    }
    logger.debug(
        "NICValidator config: validator_details=%d, format_details=%d",
        len(config["validator_details"]),
        len(config["format_details"]),
    )
    return config


def get_brn_validator_config() -> dict:
    """Return BRNValidator configuration for Business Registration Number.

    SubPhase-03, Group-F, Task 78.
    """
    config: dict = {
        "configured": True,
        "validator_details": [
            "BRNValidator validates Sri Lankan Business Registration Number format",
            "BRNValidator raises ValidationError for invalid registration patterns",
            "BRNValidator is used on registration fields in vendor and company models",
            "BRNValidator ensures the number follows official government format rules",
            "BRNValidator strips whitespace and normalizes separators before checking",
            "BRNValidator provides an error message describing the expected BRN format",
        ],
        "format_details": [
            "format consists of a registration type prefix and sequential number",
            "format uses alphanumeric characters with specific separator conventions",
            "format prefix indicates the type of business entity being registered",
            "format sequential portion uniquely identifies the registered business",
            "format may include a regional code component for provincial registration",
            "format validation checks overall length and character class constraints",
        ],
        "pattern_details": [
            "pattern matches common BRN formats like PV12345 for private companies",
            "pattern matches common BRN formats like GA12345 for partnerships type",
            "pattern rejects strings that contain only numeric digits without prefix",
            "pattern rejects strings that exceed the maximum allowed BRN total length",
            "pattern rejects strings with invalid special characters within the value",
            "pattern is compiled as a regular expression for efficient repeated use",
        ],
    }
    logger.debug(
        "BRNValidator config: validator_details=%d, format_details=%d",
        len(config["validator_details"]),
        len(config["format_details"]),
    )
    return config


def get_positive_decimal_validator_config() -> dict:
    """Return PositiveDecimalValidator configuration.

    SubPhase-03, Group-F, Task 79.
    """
    config: dict = {
        "configured": True,
        "validator_details": [
            "PositiveDecimalValidator ensures decimal values are strictly positive",
            "PositiveDecimalValidator raises ValidationError for zero or negative input",
            "PositiveDecimalValidator is used on price and quantity fields in models",
            "PositiveDecimalValidator accepts Python Decimal and float numeric types",
            "PositiveDecimalValidator converts string input to Decimal before checking",
            "PositiveDecimalValidator provides a clear error for non-positive values",
        ],
        "rule_details": [
            "rule requires the decimal value to be greater than zero strictly",
            "rule rejects zero as it does not qualify as a positive number value",
            "rule rejects negative numbers regardless of their magnitude or precision",
            "rule handles edge cases like very small positive decimals near zero",
            "rule validates after any rounding applied by the Decimal field context",
            "rule works consistently with max_digits and decimal_places constraints",
        ],
        "usage_details": [
            "usage on product price fields ensures no free or negative-priced items",
            "usage on order quantity fields prevents zero-quantity line item entries",
            "usage on tax amount fields guarantees only positive tax values recorded",
            "usage on discount amount fields where positive value means valid discount",
            "usage on shipping cost fields ensures carriers have a valid charge amount",
            "usage on inventory stock fields prevents negative stock level from entry",
        ],
    }
    logger.debug(
        "PositiveDecimalValidator config: validator_details=%d, rule_details=%d",
        len(config["validator_details"]),
        len(config["rule_details"]),
    )
    return config


def get_percentage_validator_config() -> dict:
    """Return PercentageValidator configuration for 0-100 range.

    SubPhase-03, Group-F, Task 80.
    """
    config: dict = {
        "configured": True,
        "validator_details": [
            "PercentageValidator ensures values fall within the 0 to 100 range",
            "PercentageValidator raises ValidationError for out-of-range input values",
            "PercentageValidator is used on discount and tax percentage model fields",
            "PercentageValidator accepts integer and decimal percentage representations",
            "PercentageValidator treats boundary values 0 and 100 as valid inclusive",
            "PercentageValidator provides an error message stating the allowed range",
        ],
        "range_details": [
            "range lower bound is zero representing no percentage applied at all",
            "range upper bound is one hundred representing the full amount total",
            "range includes both boundary values as valid percentage inputs allowed",
            "range rejects negative values as they are below the minimum boundary",
            "range rejects values above one hundred as exceeding maximum boundary",
            "range validation uses inclusive comparison operators for both bounds",
        ],
        "usage_details": [
            "usage on discount percentage fields limits discounts between 0 and 100",
            "usage on tax rate fields ensures tax percentages stay within valid range",
            "usage on profit margin fields validates margin percentage calculations",
            "usage on commission rate fields ensures agent commissions are reasonable",
            "usage on completion percentage fields tracks progress from 0 to 100",
            "usage on allocation percentage fields ensures distributions are valid",
        ],
    }
    logger.debug(
        "PercentageValidator config: validator_details=%d, range_details=%d",
        len(config["validator_details"]),
        len(config["range_details"]),
    )
    return config


def get_fields_file_config() -> dict:
    """Return fields.py file configuration for custom model fields.

    SubPhase-03, Group-F, Task 81.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "fields.py file located at backend/apps/core/models/fields.py path",
            "fields.py serves as the central module for all custom model fields",
            "fields.py is imported by model modules that need specialized field types",
            "fields.py follows Django field convention with __all__ exports defined",
            "fields.py groups related field classes by their base field type category",
            "fields.py includes comprehensive docstrings for each custom field class",
        ],
        "structure_details": [
            "structure begins with standard Django and Python library imports",
            "structure defines base classes that extend core Django field types",
            "structure organizes fields alphabetically by class name for clarity",
            "structure separates numeric fields from text and relation fields",
            "structure includes field-level validators as inner class attributes",
            "structure exports all public field classes via __all__ list at top",
        ],
        "purpose_details": [
            "purpose is to enforce LankaCommerce business rules at field level",
            "purpose is to provide reusable fields across multiple POS models",
            "purpose is to standardize data formats for Sri Lankan locale needs",
            "purpose is to reduce code duplication in model field definitions",
            "purpose is to centralize validation logic for monetary and tax values",
            "purpose is to ensure consistent field behavior across all tenant schemas",
        ],
    }
    logger.debug(
        "Fields file config: file_details=%d, structure_details=%d",
        len(config["file_details"]),
        len(config["structure_details"]),
    )
    return config


def get_money_field_config() -> dict:
    """Return MoneyField configuration with LKR precision defaults.

    SubPhase-03, Group-F, Task 82.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "MoneyField extends Django DecimalField with monetary-specific defaults",
            "MoneyField sets max_digits to 12 to handle large LKR transaction amounts",
            "MoneyField sets decimal_places to 2 matching Sri Lankan Rupee subunits",
            "MoneyField includes a PositiveDecimalValidator to prevent negative amounts",
            "MoneyField stores values as Python Decimal for precise financial math",
            "MoneyField provides a default currency attribute set to LKR by default",
        ],
        "precision_details": [
            "precision uses exactly 2 decimal places for cents in LKR currency",
            "precision max_digits of 12 supports values up to 9,999,999,999.99 LKR",
            "precision avoids floating-point errors by using Decimal internally",
            "precision rounding mode follows ROUND_HALF_UP for financial correctness",
            "precision settings are configurable per field instance if needed",
            "precision defaults align with Central Bank of Sri Lanka currency rules",
        ],
        "usage_details": [
            "usage on product unit_price field stores retail price in LKR value",
            "usage on order total_amount field stores computed order total in LKR",
            "usage on invoice line_total field stores individual line item amounts",
            "usage on payment received_amount field tracks cash and card payments",
            "usage on tax tax_amount field stores calculated tax for each order",
            "usage on refund refund_amount field records returned payment amounts",
        ],
    }
    logger.debug(
        "MoneyField config: field_details=%d, precision_details=%d",
        len(config["field_details"]),
        len(config["precision_details"]),
    )
    return config


def get_percentage_field_config() -> dict:
    """Return PercentageField configuration for 0-100 range with two decimals.

    SubPhase-03, Group-F, Task 83.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "PercentageField extends Django DecimalField with percentage defaults",
            "PercentageField sets max_digits to 5 and decimal_places to 2 by default",
            "PercentageField includes MinValueValidator of 0 and MaxValueValidator of 100",
            "PercentageField stores values as Decimal for precise percentage calculations",
            "PercentageField provides a default value of 0.00 when no percentage is set",
            "PercentageField adds a help_text indicating the valid 0-100 range for users",
        ],
        "range_details": [
            "range lower bound of 0 represents no percentage applied to the value",
            "range upper bound of 100 represents the full percentage of the value",
            "range validation includes both 0 and 100 as valid boundary values",
            "range rejects negative percentages that would invert the calculation",
            "range rejects values above 100 unless explicitly overridden by subclass",
            "range supports two decimal places for precise rates like 12.50 percent",
        ],
        "usage_details": [
            "usage on discount percentage field limits product discounts from 0 to 100",
            "usage on VAT rate field stores Sri Lanka standard VAT rate of 18 percent",
            "usage on profit margin field calculates markup percentage per product item",
            "usage on SVAT rate field handles simplified VAT for registered businesses",
            "usage on commission rate field stores agent commission for sales staff",
            "usage on NBT rate field stores Nation Building Tax rate for compliance",
        ],
    }
    logger.debug(
        "PercentageField config: field_details=%d, range_details=%d",
        len(config["field_details"]),
        len(config["range_details"]),
    )
    return config


def get_phone_number_field_config() -> dict:
    """Return PhoneNumberField configuration for Sri Lankan phone format.

    SubPhase-03, Group-F, Task 84.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "PhoneNumberField extends Django CharField with phone-specific validation",
            "PhoneNumberField sets max_length to 15 to accommodate international format",
            "PhoneNumberField includes a regex validator for Sri Lankan phone patterns",
            "PhoneNumberField stores the number in E.164 international format string",
            "PhoneNumberField strips whitespace and formatting before saving to database",
            "PhoneNumberField provides a help_text showing expected Sri Lankan format",
        ],
        "format_details": [
            "format uses +94 country code prefix for all Sri Lankan phone numbers",
            "format supports 10-digit local numbers starting with 0 for domestic use",
            "format recognizes mobile prefixes like 070 071 072 075 076 077 078",
            "format recognizes landline prefixes like 011 021 031 for major cities",
            "format strips leading zero when storing with +94 international prefix",
            "format validation rejects numbers that do not match Sri Lankan patterns",
        ],
        "usage_details": [
            "usage on customer phone field stores primary contact number for buyers",
            "usage on vendor contact_phone field stores supplier phone for ordering",
            "usage on employee mobile field stores staff contact for HR management",
            "usage on delivery driver_phone field enables delivery tracking contact",
            "usage on store branch_phone field stores physical store contact number",
            "usage on emergency contact_phone field stores employee emergency contact",
        ],
    }
    logger.debug(
        "PhoneNumberField config: field_details=%d, format_details=%d",
        len(config["field_details"]),
        len(config["format_details"]),
    )
    return config


def get_slug_field_config() -> dict:
    """Return SlugField with auto-generation from name or title fields.

    SubPhase-03, Group-F, Task 85.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "AutoSlugField extends Django SlugField with automatic slug generation",
            "AutoSlugField sets unique to True ensuring no duplicate slugs per model",
            "AutoSlugField sets db_index to True for fast URL-based lookups in queries",
            "AutoSlugField sets max_length to 255 to handle long product name slugs",
            "AutoSlugField sets editable to False preventing manual slug modification",
            "AutoSlugField provides a populate_from attribute pointing to source field",
        ],
        "auto_details": [
            "auto-generation triggers on model save when the slug field is empty",
            "auto-generation uses Django slugify to convert source text to URL-safe",
            "auto-generation appends numeric suffix when duplicate slug is detected",
            "auto-generation handles Sinhala and Tamil text by transliterating first",
            "auto-generation preserves existing slug value if already set on instance",
            "auto-generation updates slug when source field changes if configured so",
        ],
        "usage_details": [
            "usage on product slug field creates SEO-friendly URLs for webstore pages",
            "usage on category slug field enables clean category browsing URL paths",
            "usage on brand slug field provides readable brand page URLs for customers",
            "usage on blog post slug field generates URL slugs from article titles",
            "usage on store branch slug field creates location page URLs per branch",
            "usage on promotion slug field enables shareable promotion landing pages",
        ],
    }
    logger.debug(
        "SlugField auto config: field_details=%d, auto_details=%d",
        len(config["field_details"]),
        len(config["auto_details"]),
    )
    return config


def get_utils_file_config() -> dict:
    """Return utils.py file configuration for shared helper functions.

    SubPhase-03, Group-F, Task 86.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "file is located at apps/core/utils/utils.py within the core package",
            "file serves as the central module for shared utility helper functions",
            "file imports common libraries such as string, random, and uuid modules",
            "file provides reusable functions used across multiple application modules",
            "file follows the single-responsibility principle for each helper function",
            "file is documented with module-level docstring describing its purpose",
        ],
        "structure_details": [
            "structure organizes helpers into logical sections by function category",
            "structure places code generation functions at the top of the module",
            "structure places accessor functions below the code generation section",
            "structure includes type annotations on all function signatures defined",
            "structure uses module-level logger for consistent debug log messages",
            "structure follows alphabetical ordering within each logical section",
        ],
        "purpose_details": [
            "purpose is to centralize common utility logic for the entire project",
            "purpose eliminates code duplication across multiple Django applications",
            "purpose provides consistent reference code generation for all entities",
            "purpose offers tenant and user context accessors for audit operations",
            "purpose supports testability by isolating helper logic into functions",
            "purpose simplifies imports by exposing helpers from a single module",
        ],
    }
    logger.debug(
        "Utils file config: file_details=%d, structure_details=%d",
        len(config["file_details"]),
        len(config["structure_details"]),
    )
    return config


def get_generate_unique_code_config() -> dict:
    """Return generate_unique_code configuration for reference code generation.

    SubPhase-03, Group-F, Task 87.
    """
    config: dict = {
        "configured": True,
        "generator_details": [
            "generator creates unique alphanumeric codes with a configurable prefix",
            "generator uses random selection from uppercase letters and digit characters",
            "generator accepts a prefix parameter to identify the entity type clearly",
            "generator accepts a length parameter controlling the random suffix size",
            "generator produces codes suitable for invoices, orders, and receipts",
            "generator ensures uniqueness through random character combination space",
        ],
        "format_details": [
            "format starts with a string prefix such as INV, ORD, or RCP codes",
            "format appends a hyphen separator between the prefix and random part",
            "format uses uppercase alphanumeric characters for the random suffix",
            "format default length is eight characters for the random suffix portion",
            "format produces human-readable codes suitable for printed documents",
            "format avoids ambiguous characters to prevent reading errors on paper",
        ],
        "usage_details": [
            "usage on invoice model generates unique invoice reference code numbers",
            "usage on order model creates unique order reference codes for tracking",
            "usage on receipt model produces unique receipt numbers for customers",
            "usage on return model generates unique return authorization code values",
            "usage on stock transfer model creates transfer reference code strings",
            "usage on payment model produces unique payment transaction identifiers",
        ],
    }
    logger.debug(
        "generate_unique_code config: generator_details=%d, format_details=%d",
        len(config["generator_details"]),
        len(config["format_details"]),
    )
    return config


def get_current_tenant_config() -> dict:
    """Return get_current_tenant configuration for tenant context accessor.

    SubPhase-03, Group-F, Task 88.
    """
    config: dict = {
        "configured": True,
        "accessor_details": [
            "accessor retrieves the current tenant from the database connection",
            "accessor uses django_tenants connection.tenant to resolve the tenant",
            "accessor returns the tenant model instance for the active schema",
            "accessor is designed to work within the django-tenants middleware",
            "accessor provides a clean abstraction over low-level connection API",
            "accessor is importable from the core utils package for convenience",
        ],
        "behavior_details": [
            "behavior returns None when called outside a tenant-aware context",
            "behavior returns the public tenant when on the public schema scope",
            "behavior returns the specific tenant when inside a tenant schema",
            "behavior does not raise exceptions for missing tenant references",
            "behavior is safe to call in management commands and shell sessions",
            "behavior works consistently across synchronous request processing",
        ],
        "usage_details": [
            "usage in audit mixins to automatically record the tenant on save",
            "usage in manager querysets to filter records by the current tenant",
            "usage in serializers to validate tenant ownership of related objects",
            "usage in permission classes to enforce tenant-level access controls",
            "usage in signal handlers to scope post-save actions to the tenant",
            "usage in middleware to inject tenant context into request objects",
        ],
    }
    logger.debug(
        "get_current_tenant config: accessor_details=%d, behavior_details=%d",
        len(config["accessor_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_current_user_config() -> dict:
    """Return get_current_user configuration for user context accessor.

    SubPhase-03, Group-F, Task 89.
    """
    config: dict = {
        "configured": True,
        "accessor_details": [
            "accessor retrieves the current user from thread-local storage object",
            "accessor uses a threading.local instance to store per-request user",
            "accessor returns the user model instance set by the audit middleware",
            "accessor is designed to work with Django request-response lifecycle",
            "accessor provides a clean abstraction over thread-local storage API",
            "accessor is importable from the core utils package for convenience",
        ],
        "behavior_details": [
            "behavior returns None when called outside a request-aware context",
            "behavior returns None when the thread-local user has not been set",
            "behavior returns the authenticated user set by the audit middleware",
            "behavior does not raise exceptions for anonymous or missing users",
            "behavior is safe to call in management commands returning None value",
            "behavior resets the stored user at the end of each request cycle",
        ],
        "usage_details": [
            "usage in audit mixin to set created_by field on new model instances",
            "usage in audit mixin to set updated_by field on model save operations",
            "usage in signal handlers to record which user triggered the action",
            "usage in logging middleware to include user context in log entries",
            "usage in permission checks to determine the acting user identity",
            "usage in activity tracking to record user actions for audit trails",
        ],
    }
    logger.debug(
        "get_current_user config: accessor_details=%d, behavior_details=%d",
        len(config["accessor_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_validators_export_config() -> dict:
    """Return validators export configuration for package-level exports.

    SubPhase-03, Group-F, Task 90.
    """
    config: dict = {
        "configured": True,
        "export_details": [
            "export includes PhoneNumberValidator in the validators __init__ module",
            "export includes NICValidator for national identity card validation",
            "export includes BRNValidator for business registration number check",
            "export includes PositiveDecimalValidator for positive value enforcement",
            "export includes PercentageValidator for zero to one hundred range check",
            "export uses __all__ list to define the public API of validator module",
        ],
        "import_details": [
            "import path apps.core.validators provides all validators at package level",
            "import uses relative imports within the validators package internally",
            "import allows external apps to access validators with a single import",
            "import follows Django convention of exposing key classes from __init__",
            "import avoids deep module paths for cleaner application code usage",
            "import maintains alphabetical ordering of exported validator names",
        ],
        "usage_details": [
            "usage simplifies field validator assignment with short import paths",
            "usage in model field definitions references validators by class name",
            "usage in serializer validation imports validators from core package",
            "usage in form field validation accesses validators through clean API",
            "usage in admin model registration applies validators to form fields",
            "usage in test modules imports validators for unit test assertions",
        ],
    }
    logger.debug(
        "Validators export config: export_details=%d, import_details=%d",
        len(config["export_details"]),
        len(config["import_details"]),
    )
    return config


def get_fields_export_config() -> dict:
    """Return fields export configuration for package-level field exports.

    SubPhase-03, Group-F, Task 91.
    """
    config: dict = {
        "configured": True,
        "export_details": [
            "export includes MoneyField in the fields __init__ module for access",
            "export includes PercentageField for percentage value model assignments",
            "export includes PhoneNumberField for Sri Lankan phone contact fields",
            "export includes AutoSlugField for automatic slug generation on models",
            "export uses __all__ list to define the public API of fields module",
            "export places all custom field classes into a single importable path",
        ],
        "import_details": [
            "import path apps.core.fields provides all fields at package level",
            "import uses relative imports within the fields package internally",
            "import allows external apps to access custom fields with one import",
            "import follows Django convention of exposing field classes from init",
            "import avoids deep module paths for cleaner model definition usage",
            "import maintains alphabetical ordering of exported field class names",
        ],
        "usage_details": [
            "usage simplifies model field definitions with short import statements",
            "usage in product model applies MoneyField for price and cost columns",
            "usage in discount model applies PercentageField for discount rate field",
            "usage in customer model applies PhoneNumberField for contact numbers",
            "usage in category model applies AutoSlugField for URL-friendly names",
            "usage in test modules imports fields for unit test model factories",
        ],
    }
    logger.debug(
        "Fields export config: export_details=%d, import_details=%d",
        len(config["export_details"]),
        len(config["import_details"]),
    )
    return config


def get_initial_migration_config() -> dict:
    """Return initial migration configuration for core model schema setup.

    SubPhase-03, Group-F, Task 92.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "migration is generated by Django makemigrations for the core app",
            "migration creates the initial database schema for custom model fields",
            "migration includes field definitions for MoneyField decimal columns",
            "migration includes field definitions for PercentageField constraints",
            "migration registers custom validators used by field default arguments",
            "migration is numbered 0001_initial following Django naming convention",
        ],
        "scope_details": [
            "scope covers the core application models that use custom base fields",
            "scope includes abstract model field definitions inherited by children",
            "scope registers indexes defined in model Meta classes for performance",
            "scope captures default values and validators attached to model fields",
            "scope includes foreign key relationships for audit trail user fields",
            "scope documents the tenant-scoped model schema partition requirements",
        ],
        "expectation_details": [
            "expectation is zero schema errors when running migrate on clean database",
            "expectation is idempotent migration that can be applied multiple times",
            "expectation is backward-compatible schema with existing data if present",
            "expectation is all custom field types resolve to valid database columns",
            "expectation is all validator references are importable at migration time",
            "expectation is migration runs successfully in both SQLite and PostgreSQL",
        ],
    }
    logger.debug(
        "Initial migration config: migration_details=%d, scope_details=%d",
        len(config["migration_details"]),
        len(config["scope_details"]),
    )
    return config


def get_full_test_suite_config() -> dict:
    """Return full test suite configuration for validators, fields, and utils.

    SubPhase-03, Group-F, Task 93.
    """
    config: dict = {
        "configured": True,
        "coverage_details": [
            "coverage includes all five validator classes with positive and negative cases",
            "coverage includes all four custom field types with default value checks",
            "coverage includes utility functions for code generation and accessors",
            "coverage tests Sri Lankan phone number format validation thoroughly",
            "coverage tests NIC and BRN format validation with real-world examples",
            "coverage verifies percentage range boundaries at zero and one hundred",
        ],
        "scenario_details": [
            "scenario validates Sri Lankan mobile numbers starting with plus nine four",
            "scenario validates ten-digit NIC numbers and twelve-digit new format NICs",
            "scenario validates business registration numbers with district prefixes",
            "scenario tests MoneyField decimal precision with LKR currency values",
            "scenario tests SlugField auto-generation from Sinhala transliterated names",
            "scenario tests unique code generator produces non-repeating reference codes",
        ],
        "assertion_details": [
            "assertion checks that valid inputs pass validation without raising errors",
            "assertion checks that invalid inputs raise Django ValidationError type",
            "assertion checks that field default values match expected configuration",
            "assertion checks that manager querysets return correct filtered results",
            "assertion checks that export modules expose all expected public classes",
            "assertion checks that documentation references are present in docstrings",
        ],
    }
    logger.debug(
        "Full test suite config: coverage_details=%d, scenario_details=%d",
        len(config["coverage_details"]),
        len(config["scenario_details"]),
    )
    return config


def get_base_models_documentation_config() -> dict:
    """Return base models documentation configuration for all models and utilities.

    SubPhase-03, Group-F, Task 94.
    """
    config: dict = {
        "configured": True,
        "model_details": [
            "model documentation covers TimeStampedModel with created_at and updated_at",
            "model documentation covers SoftDeleteModel with is_deleted and deleted_at",
            "model documentation covers AuditModel with created_by and updated_by fields",
            "model documentation covers UUIDModel with uuid primary key field setup",
            "model documentation covers TenantScopedModel with tenant isolation logic",
            "model documentation includes inheritance diagram showing model hierarchy",
        ],
        "utility_details": [
            "utility documentation covers PhoneNumberValidator for Sri Lankan formats",
            "utility documentation covers NICValidator for national identity numbers",
            "utility documentation covers BRNValidator for business registration codes",
            "utility documentation covers MoneyField for LKR currency precision setup",
            "utility documentation covers generate_unique_code for reference generation",
            "utility documentation covers get_current_tenant and get_current_user helpers",
        ],
        "format_details": [
            "format uses Markdown for all documentation files in the docs directory",
            "format includes a table of contents at the top of each document page",
            "format provides usage examples in plain text without fenced code blocks",
            "format cross-references related models and utilities with hyperlinks",
            "format follows the project documentation template with standard headings",
            "format includes a changelog section noting when each model was introduced",
        ],
    }
    logger.debug(
        "Base models documentation config: model_details=%d, utility_details=%d",
        len(config["model_details"]),
        len(config["utility_details"]),
    )
    return config
