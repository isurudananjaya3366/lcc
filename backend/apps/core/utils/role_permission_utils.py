"""
Role and permission utilities for LankaCommerce Cloud core infrastructure.

SubPhase-05, Group-A Tasks 01-14 and Group-B Tasks 15-30 and Group-C Tasks 31-46 and Group-D Tasks 47-62 and Group-E Tasks 63-78 and Group-F Tasks 79-92.

Provides role and permission configuration helpers used by the
core application for documenting Django RBAC and permission setup.

Functions:
    get_roles_app_directory_config()       -- Roles app directory config (Task 01).
    get_role_model_file_config()           -- Role model file config (Task 02).
    get_role_model_class_config()          -- Role model class config (Task 03).
    get_role_name_field_config()           -- Role name field config (Task 04).
    get_role_slug_field_config()           -- Role slug field config (Task 05).
    get_role_description_field_config()    -- Role description field config (Task 06).
    get_is_system_role_field_config()      -- is_system_role field config (Task 07).
    get_hierarchy_level_field_config()     -- Hierarchy level field config (Task 08).
    get_role_parent_foreign_key_config()   -- Role parent FK config (Task 09).
    get_role_tenant_foreign_key_config()   -- Role tenant FK config (Task 10).
    get_role_manager_config()              -- RoleManager config (Task 11).
    get_role_meta_class_config()           -- Role Meta class config (Task 12).
    get_default_roles_migration_config()   -- Default roles migration config (Task 13).
    get_role_model_documentation_config()  -- Role model documentation config (Task 14).
    get_permission_model_class_config()    -- Permission model class config (Task 15).
    get_permission_codename_field_config() -- Permission codename field config (Task 16).
    get_permission_name_field_config()     -- Permission name field config (Task 17).
    get_permission_module_field_config()   -- Permission module field config (Task 18).
    get_permission_action_field_config()   -- Permission action field config (Task 19).
    get_permission_group_model_config()    -- PermissionGroup model config (Task 20).
    get_permission_group_name_field_config() -- PermissionGroup name field config (Task 21).
    get_permission_group_m2m_field_config() -- PermissionGroup M2M field config (Task 22).
    get_module_choices_config()             -- Module choices config (Task 23).
    get_action_choices_config()            -- Action choices config (Task 24).
    get_default_permissions_migration_config() -- Default permissions migration config (Task 25).
    get_products_module_permissions_config() -- Products module permissions config (Task 26).
    get_inventory_module_permissions_config() -- Inventory module permissions config (Task 27).
    get_sales_module_permissions_config()   -- Sales module permissions config (Task 28).
    get_reports_module_permissions_config() -- Reports module permissions config (Task 29).
    get_permissions_documentation_config()  -- Permissions documentation config (Task 30).
    get_role_permission_model_class_config() -- RolePermission model class config (Task 31).
    get_role_permission_role_fk_config()    -- RolePermission role FK config (Task 32).
    get_role_permission_perm_fk_config()    -- RolePermission permission FK config (Task 33).
    get_granted_at_field_config()           -- granted_at field config (Task 34).
    get_granted_by_field_config()           -- granted_by field config (Task 35).
    get_role_permission_unique_constraint_config() -- Unique constraint config (Task 36).
    get_role_permission_manager_class_config() -- RolePermissionManager class config (Task 37).
    get_assign_permission_method_config()  -- assign_permission method config (Task 38).
    get_revoke_permission_method_config()  -- revoke_permission method config (Task 39).
    get_has_permission_method_config()     -- has_permission method config (Task 40).
    get_super_admin_permissions_config()   -- Super Admin permissions config (Task 41).
    get_tenant_admin_permissions_config()  -- Tenant Admin permissions config (Task 42).
    get_manager_permissions_config()       -- Manager permissions config (Task 43).
    get_staff_permissions_config()         -- Staff permissions config (Task 44).
    get_customer_permissions_config()      -- Customer permissions config (Task 45).
    get_role_permission_system_docs_config() -- Role-Permission system docs config (Task 46).
    get_user_role_model_class_config()     -- UserRole model class config (Task 47).
    get_user_role_user_fk_config()         -- UserRole user FK config (Task 48).
    get_user_role_role_fk_config()         -- UserRole role FK config (Task 49).
    get_user_role_assigned_at_field_config() -- UserRole assigned_at field config (Task 50).
    get_user_role_assigned_by_field_config() -- UserRole assigned_by field config (Task 51).
    get_is_primary_field_config()          -- is_primary field config (Task 52).
    get_user_role_unique_constraint_config() -- UserRole unique constraint config (Task 53).
    get_user_role_manager_class_config()   -- UserRoleManager class config (Task 54).
    get_assign_role_method_config()        -- assign_role method config (Task 55).
    get_remove_role_method_config()        -- remove_role method config (Task 56).
    get_get_roles_method_config()          -- get_roles method config (Task 57).
    get_user_has_perm_method_config()      -- User.has_perm method config (Task 58).
    get_user_has_role_method_config()      -- User.has_role method config (Task 59).
    get_user_get_all_permissions_config()  -- User.get_all_permissions config (Task 60).
    get_cache_user_permissions_config()    -- Cache user permissions config (Task 61).
    get_document_user_roles_config()       -- Document user roles config (Task 62).
    get_permissions_module_config()        -- Permissions module config (Task 63).
    get_permission_required_decorator_config() -- permission_required decorator config (Task 64).
    get_role_required_decorator_config()   -- role_required decorator config (Task 65).
    get_any_permission_required_config()   -- any_permission_required config (Task 66).
    get_all_permissions_required_config()  -- all_permissions_required config (Task 67).
    get_is_role_permission_class_config()  -- IsRolePermission base class config (Task 68).
    get_is_super_admin_permission_config() -- IsSuperAdmin permission config (Task 69).
    get_is_tenant_admin_permission_config() -- IsTenantAdmin permission config (Task 70).
    get_is_manager_permission_config()     -- IsManager permission config (Task 71).
    get_is_staff_permission_config()       -- IsStaff permission config (Task 72).
    get_permission_mixin_config()          -- PermissionMixin config (Task 73).
    get_role_mixin_config()                -- RoleMixin config (Task 74).
    get_tenant_permission_mixin_config()   -- TenantPermissionMixin config (Task 75).
    get_jwt_role_claims_config()           -- JWT role claims config (Task 76).
    get_permission_denied_response_config() -- Permission denied response config (Task 77).
    get_decorators_mixins_docs_config()    -- Decorators and mixins docs config (Task 78).
    get_role_serializers_config()          -- Role serializers config (Task 79).
    get_permission_serializers_config()    -- Permission serializers config (Task 80).
    get_role_list_view_config()            -- RoleListView config (Task 81).
    get_role_detail_view_config()          -- RoleDetailView config (Task 82).
    get_role_create_view_config()          -- RoleCreateView config (Task 83).
    get_assign_role_view_config()          -- AssignRoleView config (Task 84).
    get_revoke_role_view_config()          -- RevokeRoleView config (Task 85).
    get_my_permissions_view_config()       -- MyPermissionsView config (Task 86).
    get_role_urls_config()                 -- Role URLs config (Task 87).
    get_role_admin_config()                -- Role admin config (Task 88).
    get_role_model_tests_config()          -- Role model tests config (Task 89).
    get_permission_tests_config()          -- Permission tests config (Task 90).
    get_decorator_tests_config()           -- Decorator tests config (Task 91).
    get_role_system_docs_config()          -- Role system docs config (Task 92).

See also:
    - apps.core.utils.__init__  -- public re-exports
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_roles_app_directory_config() -> dict:
    """Return roles app directory configuration for RBAC module placement.

    SubPhase-05, Group-A, Task 01.
    """
    config: dict = {
        "configured": True,
        "directory_details": [
            "directory is created at backend/apps/roles to host role-related modules",
            "directory follows the established app layout convention used by other apps",
            "directory contains __init__.py to mark it as a Python package",
            "directory contains apps.py with RolesConfig for Django app registration",
            "directory includes models, admin, urls, and views modules for completeness",
            "directory is registered in INSTALLED_APPS as apps.roles for discovery",
        ],
        "placement_details": [
            "placement decision locates roles under a dedicated app rather than inside users",
            "placement keeps role definitions separate for clear module boundaries",
            "placement aligns with Django best practice of one concern per application",
            "placement allows independent migration management for role schema changes",
            "placement facilitates reusability across different project configurations",
            "placement is documented in the architecture decision record for future reference",
        ],
        "structure_details": [
            "structure mirrors the standard Django app template used across the project",
            "structure includes a models directory for multi-file model organization",
            "structure includes a tests directory for role-specific unit tests",
            "structure includes a serializers module for DRF role serialization",
            "structure includes a permissions module for custom permission classes",
            "structure is validated by the app structure verification tooling",
        ],
    }
    logger.debug(
        "roles app directory config: directory_details=%d, placement_details=%d",
        len(config["directory_details"]),
        len(config["placement_details"]),
    )
    return config


def get_role_model_file_config() -> dict:
    """Return role model file configuration for RBAC model definition.

    SubPhase-05, Group-A, Task 02.
    """
    config: dict = {
        "configured": True,
        "file_details": [
            "file is created at apps/roles/models/role.py for the Role model definition",
            "file imports Django models module and base model mixins from core",
            "file defines the Role class as the central RBAC entity for tenant-scoped roles",
            "file is registered in the models __init__.py for automatic discovery",
            "file follows the project convention of one model per file for clarity",
            "file includes module-level docstring describing the Role model purpose",
        ],
        "intent_details": [
            "intent is to define hierarchical tenant-scoped roles for access control",
            "intent supports multiple role levels such as owner, manager, and staff",
            "intent allows each tenant to have its own isolated set of roles",
            "intent enables permission assignment at the role level rather than per user",
            "intent follows the RBAC pattern recommended for multi-tenant SaaS platforms",
            "intent is documented in the model docstring for developer understanding",
        ],
        "location_details": [
            "location places the file under apps/roles/models for organized model storage",
            "location follows the multi-file models pattern used by the roles app",
            "location ensures the model is importable via apps.roles.models.role",
            "location is consistent with how other apps structure their model files",
            "location allows clean imports when referenced from serializers and views",
            "location is verified by the app structure checks during CI validation",
        ],
    }
    logger.debug(
        "role model file config: file_details=%d, intent_details=%d",
        len(config["file_details"]),
        len(config["intent_details"]),
    )
    return config


def get_role_model_class_config() -> dict:
    """Return role model class configuration for RBAC model hierarchy.

    SubPhase-05, Group-A, Task 03.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "class Role extends BaseModel to inherit timestamped and soft-delete fields",
            "class uses UUIDModel as a mixin to provide a UUID primary key",
            "class inherits TenantScopedModel for automatic tenant isolation",
            "class is defined in apps/roles/models/role.py as the central RBAC entity",
            "class includes Meta ordering by hierarchy_level and name for consistent display",
            "class provides a __str__ method returning the role name for admin readability",
        ],
        "hierarchy_details": [
            "hierarchy defines five levels numbered 0 through 4 for role ranking",
            "hierarchy level 0 represents Super Admin with unrestricted platform access",
            "hierarchy level 1 represents Tenant Owner who manages a single tenant",
            "hierarchy level 2 represents Manager with department-level oversight",
            "hierarchy level 3 represents Staff with day-to-day operational permissions",
            "hierarchy level 4 represents Cashier with POS-only restricted access",
        ],
        "feature_details": [
            "feature supports tenant-scoped roles so each tenant has its own role set",
            "feature marks system roles as protected to prevent accidental deletion",
            "feature enables self-referential parent for hierarchical permission inheritance",
            "feature allows custom roles to be created alongside predefined system roles",
            "feature integrates with Django permissions framework via ManyToMany relations",
            "feature exposes role data through DRF serializers for API consumption",
        ],
    }
    logger.debug(
        "role model class config: class_details=%d, hierarchy_details=%d",
        len(config["class_details"]),
        len(config["hierarchy_details"]),
    )
    return config


def get_role_name_field_config() -> dict:
    """Return role name field configuration for role display name.

    SubPhase-05, Group-A, Task 04.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is a CharField with max_length of 100 for the role display name",
            "field stores human-readable names such as Owner, Manager, or Cashier",
            "field is required and does not allow blank or null values",
            "field appears in admin list_display for quick role identification",
            "field is used as the source for automatic slug generation via slugify",
            "field value is returned by the __str__ method of the Role model",
        ],
        "constraint_details": [
            "constraint enforces unique_together on name and tenant to avoid duplicates",
            "constraint allows the same role name to exist across different tenants",
            "constraint prevents blank values to ensure every role has a meaningful name",
            "constraint disallows null to guarantee the column is always populated",
            "constraint max_length of 100 balances flexibility with database efficiency",
            "constraint is validated at both model and serializer levels for consistency",
        ],
        "indexing_details": [
            "indexing adds db_index on the name field for fast lookup queries",
            "indexing supports efficient filtering when listing roles by name",
            "indexing improves performance of autocomplete and search endpoints",
            "indexing is combined with tenant filtering for scoped queries",
            "indexing uses a B-tree index which suits prefix and equality lookups",
            "indexing overhead is minimal given the low cardinality of role records",
        ],
    }
    logger.debug(
        "role name field config: field_details=%d, constraint_details=%d",
        len(config["field_details"]),
        len(config["constraint_details"]),
    )
    return config


def get_role_slug_field_config() -> dict:
    """Return role slug field configuration for URL-safe role identifier.

    SubPhase-05, Group-A, Task 05.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is a SlugField with max_length of 100 for URL-safe identifiers",
            "field stores lowercase hyphenated versions of the role name",
            "field is used in API URLs and query parameters for role lookup",
            "field has db_index enabled for efficient slug-based retrieval",
            "field allows blank on forms since it is auto-generated before save",
            "field is immutable after creation to preserve URL stability",
        ],
        "generation_details": [
            "generation uses Django slugify utility to convert name to slug format",
            "generation is triggered in the model save method before database write",
            "generation converts spaces and special characters to hyphens",
            "generation lowercases the entire name string for URL consistency",
            "generation only runs when the slug field is empty to avoid overwrites",
            "generation is tested to ensure idempotent behavior on repeated saves",
        ],
        "uniqueness_details": [
            "uniqueness is enforced per tenant using unique_together on slug and tenant",
            "uniqueness allows identical slugs across different tenants for isolation",
            "uniqueness constraint prevents duplicate URL identifiers within a tenant",
            "uniqueness is validated at the database level via a composite unique index",
            "uniqueness errors are caught and returned as friendly API validation messages",
            "uniqueness is verified in tests covering concurrent role creation scenarios",
        ],
    }
    logger.debug(
        "role slug field config: field_details=%d, generation_details=%d",
        len(config["field_details"]),
        len(config["generation_details"]),
    )
    return config


def get_role_description_field_config() -> dict:
    """Return role description field configuration for role information.

    SubPhase-05, Group-A, Task 06.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is a TextField that stores a free-form description of the role",
            "field allows blank values so descriptions are optional for simple roles",
            "field allows null values to distinguish between empty and unset states",
            "field has no max_length constraint to allow detailed documentation",
            "field appears in admin detail view and role management API responses",
            "field is serialized as a string in the RoleSerializer for API output",
        ],
        "usage_details": [
            "usage provides context about the role purpose for tenant administrators",
            "usage documents the responsibilities and scope associated with a role",
            "usage helps onboarding administrators understand role differences",
            "usage is displayed in the role management UI for clarity",
            "usage supports multi-line text for detailed role documentation",
            "usage is optional to keep role creation workflow minimal and fast",
        ],
        "default_details": [
            "default is set to an empty string so the field is never None in output",
            "default allows creation without specifying a description explicitly",
            "default ensures serializer output always includes a string type value",
            "default simplifies frontend rendering by avoiding null-check logic",
            "default is consistent with other optional text fields in the project",
            "default can be overridden at creation time via the API or admin form",
        ],
    }
    logger.debug(
        "role description field config: field_details=%d, usage_details=%d",
        len(config["field_details"]),
        len(config["usage_details"]),
    )
    return config


def get_is_system_role_field_config() -> dict:
    """Return is_system_role field configuration for role protection.

    SubPhase-05, Group-A, Task 07.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is a BooleanField indicating whether the role is a system default",
            "field defaults to False so custom-created roles are not protected",
            "field is set to True only for predefined roles seeded during setup",
            "field is indexed with db_index for efficient filtering of system roles",
            "field is read-only in the API to prevent accidental modification",
            "field is displayed in admin with a boolean icon for quick identification",
        ],
        "protection_details": [
            "protection prevents deletion of system roles via model delete override",
            "protection raises a ValidationError when delete is attempted on system roles",
            "protection ensures predefined roles like Owner and Admin always exist",
            "protection is enforced at both the model layer and the API serializer",
            "protection allows soft-delete bypass for audit but blocks hard-delete",
            "protection is tested with dedicated test cases for delete prevention",
        ],
        "behavior_details": [
            "behavior distinguishes system roles from tenant-created custom roles",
            "behavior allows tenants to create custom roles alongside system defaults",
            "behavior filters system roles in seed commands for initial tenant setup",
            "behavior enables admin UI to visually separate system and custom roles",
            "behavior is checked in permission evaluation to apply default policies",
            "behavior is documented in the role management guide for administrators",
        ],
    }
    logger.debug(
        "is_system_role field config: field_details=%d, protection_details=%d",
        len(config["field_details"]),
        len(config["protection_details"]),
    )
    return config


def get_hierarchy_level_field_config() -> dict:
    """Return hierarchy level field configuration for role ranking.

    SubPhase-05, Group-A, Task 08.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is an IntegerField storing the numeric hierarchy level of the role",
            "field uses validators to restrict values between 0 and 4 inclusive",
            "field defaults to 4 which is the lowest privilege level (Cashier)",
            "field is indexed with db_index for fast ordering and filtering operations",
            "field appears in admin list_display for quick hierarchy visualization",
            "field is used in permission checks to enforce hierarchy-based access",
        ],
        "level_details": [
            "level 0 is Super Admin with full platform access across all tenants",
            "level 1 is Tenant Owner with complete control over a single tenant",
            "level 2 is Manager with supervisory access to departments and reports",
            "level 3 is Staff with standard operational permissions for daily tasks",
            "level 4 is Cashier with restricted POS terminal access only",
            "level values are enforced by MinValueValidator and MaxValueValidator",
        ],
        "validation_details": [
            "validation uses MinValueValidator with a minimum of 0 for Super Admin",
            "validation uses MaxValueValidator with a maximum of 4 for Cashier",
            "validation rejects any value outside the 0-4 range at model clean",
            "validation errors are surfaced as friendly messages in API responses",
            "validation is applied at both the database and serializer layers",
            "validation is covered by unit tests for boundary and invalid values",
        ],
    }
    logger.debug(
        "hierarchy level field config: field_details=%d, level_details=%d",
        len(config["field_details"]),
        len(config["level_details"]),
    )
    return config


def get_role_parent_foreign_key_config() -> dict:
    """Return role parent foreign key configuration for hierarchical inheritance.

    SubPhase-05, Group-A, Task 09.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is a ForeignKey referencing self for hierarchical role relationships",
            "field uses models.SET_NULL on delete to preserve child roles when parent is removed",
            "field allows null and blank since top-level roles have no parent",
            "field sets related_name to children for reverse lookup from parent to child roles",
            "field is optional so roles can exist independently without a parent",
            "field appears in admin as a dropdown filtered to roles within the same tenant",
        ],
        "cascade_details": [
            "cascade behavior uses SET_NULL to avoid deleting child roles on parent removal",
            "cascade ensures orphaned roles remain functional with their own permissions",
            "cascade prevents accidental data loss when restructuring role hierarchies",
            "cascade is tested with scenarios involving parent deletion and child survival",
            "cascade allows administrators to safely reorganize role trees over time",
            "cascade behavior is documented in the role management architecture guide",
        ],
        "inheritance_details": [
            "inheritance allows child roles to inherit permissions from their parent role",
            "inheritance is evaluated during permission checks by walking up the tree",
            "inheritance can be overridden by explicitly assigning permissions to child roles",
            "inheritance depth is limited by the five hierarchy levels to prevent cycles",
            "inheritance supports a tree structure enabling flexible role organization",
            "inheritance is resolved at query time using recursive permission aggregation",
        ],
    }
    logger.debug(
        "role parent FK config: field_details=%d, cascade_details=%d",
        len(config["field_details"]),
        len(config["cascade_details"]),
    )
    return config


def get_role_tenant_foreign_key_config() -> dict:
    """Return role tenant foreign key configuration for multi-tenant scoping.

    SubPhase-05, Group-A, Task 10.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "field is a ForeignKey to the tenants.Tenant model for tenant association",
            "field uses models.CASCADE on delete to remove roles when a tenant is deleted",
            "field allows null for Super Admin roles that are not bound to a tenant",
            "field sets related_name to roles for reverse lookup from tenant to its roles",
            "field is indexed with db_index for efficient tenant-scoped queries",
            "field is validated to ensure non-Super-Admin roles have a tenant assigned",
        ],
        "scoping_details": [
            "scoping ensures each tenant sees only its own roles in API responses",
            "scoping is enforced by the TenantScopedManager default queryset filter",
            "scoping allows Super Admin roles to have a null tenant for platform-wide access",
            "scoping prevents cross-tenant role leakage through strict query isolation",
            "scoping is applied consistently in views, serializers, and admin filters",
            "scoping is verified by integration tests simulating multi-tenant scenarios",
        ],
        "cascade_details": [
            "cascade uses CASCADE so all tenant roles are removed when a tenant is deleted",
            "cascade ensures no orphaned roles remain after tenant deprovisioning",
            "cascade is consistent with other tenant-scoped models in the system",
            "cascade triggers are handled within a database transaction for atomicity",
            "cascade behavior is tested with tenant deletion and role cleanup assertions",
            "cascade documentation is included in the multi-tenancy architecture guide",
        ],
    }
    logger.debug(
        "role tenant FK config: field_details=%d, scoping_details=%d",
        len(config["field_details"]),
        len(config["scoping_details"]),
    )
    return config


def get_role_manager_config() -> dict:
    """Return RoleManager configuration for custom role query methods.

    SubPhase-05, Group-A, Task 11.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "RoleManager extends models.Manager to provide custom role query methods",
            "RoleManager overrides get_queryset to apply default tenant scoping",
            "RoleManager is assigned as the default manager on the Role model",
            "RoleManager centralises reusable query logic for role retrieval",
            "RoleManager includes docstrings documenting each public method",
            "RoleManager follows the Django custom manager pattern for extensibility",
        ],
        "method_details": [
            "get_system_roles returns all roles where is_system_role is True",
            "get_custom_roles returns all roles where is_system_role is False",
            "get_by_level accepts an integer hierarchy level and filters accordingly",
            "get_hierarchical_roles returns roles ordered by hierarchy_level ascending",
            "get_available_parents excludes a given role and its descendants for parent selection",
            "get_or_create_default ensures a default role exists for new tenant provisioning",
        ],
        "query_details": [
            "queries are tenant-scoped so each tenant only retrieves its own roles",
            "queries use hierarchy-aware ordering for consistent tree-based display",
            "queries return standard Django QuerySet instances for further chaining",
            "queries leverage select_related on parent to reduce N+1 lookups",
            "queries support prefetch_related on children for bulk tree loading",
            "queries are covered by unit tests validating expected result sets",
        ],
    }
    logger.debug(
        "role manager config: manager_details=%d, method_details=%d",
        len(config["manager_details"]),
        len(config["method_details"]),
    )
    return config


def get_role_meta_class_config() -> dict:
    """Return Role Meta class configuration for database table and constraints.

    SubPhase-05, Group-A, Task 12.
    """
    config: dict = {
        "configured": True,
        "meta_details": [
            "Meta class sets db_table to roles_role for explicit table naming",
            "Meta class sets verbose_name to Role for admin display",
            "Meta class sets verbose_name_plural to Roles for admin list display",
            "Meta class defines ordering as hierarchy_level then name for consistent sorting",
            "Meta class is nested inside the Role model following Django conventions",
            "Meta class configuration is verified by model inspection tests",
        ],
        "constraint_details": [
            "unique_together constraint is set on name and tenant to prevent duplicates",
            "unique_together ensures no two roles share the same name within a tenant",
            "unique_together allows identical role names across different tenants",
            "unique_together is enforced at the database level for data integrity",
            "unique_together raises IntegrityError on duplicate role creation attempts",
            "unique_together constraint is validated in unit tests with duplicate fixtures",
        ],
        "index_details": [
            "composite index on tenant and hierarchy_level accelerates level-based queries",
            "composite index on tenant and is_system_role speeds up system role lookups",
            "indexes are defined using Meta.indexes with models.Index instances",
            "indexes use descriptive names following the idx_role_ naming convention",
            "indexes reduce full table scans for the most frequent query patterns",
            "indexes are verified by migration inspection and EXPLAIN query analysis",
        ],
    }
    logger.debug(
        "role meta class config: meta_details=%d, constraint_details=%d",
        len(config["meta_details"]),
        len(config["constraint_details"]),
    )
    return config


def get_default_roles_migration_config() -> dict:
    """Return default roles migration configuration for data seeding.

    SubPhase-05, Group-A, Task 13.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "Data migration creates the Super Admin role with tenant set to None",
            "Data migration uses RunPython operation for forward and reverse functions",
            "Data migration forward function is named create_default_roles",
            "Data migration reverse function is named remove_default_roles",
            "Data migration uses get_or_create to ensure idempotent role creation",
            "Data migration depends on the initial users migration for table schema",
        ],
        "role_data_details": [
            "DEFAULT_ROLES constant defines five system roles with hierarchy levels",
            "Super Admin role has hierarchy_level 0 and is platform-wide with null tenant",
            "Tenant Admin role has hierarchy_level 1 and is created during provisioning",
            "Manager role has hierarchy_level 2 with parent_slug referencing tenant-admin",
            "Staff role has hierarchy_level 3 for daily operations and basic CRUD access",
            "Customer role has hierarchy_level 4 for webstore-only external user access",
        ],
        "provisioning_details": [
            "Tenant provisioning service creates tenant-scoped roles after tenant setup",
            "Tenant provisioning resolves parent_slug references to actual parent instances",
            "Tenant provisioning uses get_or_create to handle repeated provisioning safely",
            "Tenant provisioning returns a dict of created role instances keyed by slug",
            "Tenant provisioning creates roles in hierarchy order for correct parent links",
            "Tenant provisioning is invoked by the tenant creation workflow automatically",
        ],
    }
    logger.debug(
        "default roles migration config: migration_details=%d, role_data_details=%d",
        len(config["migration_details"]),
        len(config["role_data_details"]),
    )
    return config


def get_role_model_documentation_config() -> dict:
    """Return Role model documentation configuration for developer reference.

    SubPhase-05, Group-A, Task 14.
    """
    config: dict = {
        "configured": True,
        "documentation_details": [
            "Role model documentation file is created at docs/models/role_model.md",
            "Documentation includes a quick reference table with model name and app label",
            "Documentation covers all five hierarchy levels with scope descriptions",
            "Documentation includes a hierarchy diagram showing parent-child relationships",
            "Documentation lists all model fields with their types and constraints",
            "Documentation provides code examples for creating and querying roles",
        ],
        "api_details": [
            "API integration section documents CRUD endpoints for role management",
            "API endpoints include GET list, POST create, GET detail, PUT update, DELETE",
            "API permissions require authentication for listing roles in a tenant",
            "API permissions require create_custom_roles permission for role creation",
            "API permissions require manage_system_roles for updating system roles",
            "API serialization considerations are documented for nested role output",
        ],
        "troubleshooting_details": [
            "Troubleshooting section covers IntegrityError for duplicate role names",
            "Troubleshooting section covers ValidationError for null tenant on non-super",
            "Troubleshooting section covers deletion restrictions on system roles",
            "Troubleshooting section recommends using RoleManager methods for queries",
            "Troubleshooting section advises always filtering by tenant except Super Admin",
            "Troubleshooting section suggests calling full_clean before saving new roles",
        ],
    }
    logger.debug(
        "role model documentation config: documentation_details=%d, api_details=%d",
        len(config["documentation_details"]),
        len(config["api_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-B: Permission Model – Tasks 15-19
# ---------------------------------------------------------------------------


def get_permission_model_class_config() -> dict:
    """Return Permission model class configuration for granular access control.

    SubPhase-05, Group-B, Task 15.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "Permission model class extends BaseModel for common fields",
            "Permission model is defined in backend/apps/users/models/permission.py",
            "Permission model provides granular access control for RBAC system",
            "Permission model uses codename format of module.action_resource",
            "Permission model is assigned to roles via ManyToMany relationship",
            "Permission model can be grouped using PermissionGroup for management",
        ],
        "feature_details": [
            "Unique codename acts as the primary identifier for each permission",
            "Human-readable name field is used for UI display in role editors",
            "Module field categorizes permissions by functional area like products",
            "Action field defines CRUD operation type such as view add change delete",
            "Permissions are organized by module and action for structured access control",
            "Permission model supports both system-defined and custom permissions",
        ],
        "usage_details": [
            "Permissions are checked throughout the application for access control",
            "Role.permissions ManyToMany links roles to their allowed permissions",
            "PermissionGroup organizes related permissions for easier assignment",
            "Module and action choices are defined in constants for validation",
            "Codename format enables programmatic permission checks in views",
            "Permission model integrates with Django REST framework permission classes",
        ],
    }
    logger.debug(
        "permission model class config: class_details=%d, feature_details=%d",
        len(config["class_details"]),
        len(config["feature_details"]),
    )
    return config


def get_permission_codename_field_config() -> dict:
    """Return Permission codename field configuration for unique identification.

    SubPhase-05, Group-B, Task 16.
    """
    config: dict = {
        "configured": True,
        "codename_details": [
            "Codename field is a CharField with max_length of 100 characters",
            "Codename field has unique constraint set to True for no duplicates",
            "Codename field has db_index set to True for fast lookups",
            "Codename follows format of module.action_resource like products.view_product",
            "Codename must contain exactly one period separating module from action",
            "Codename verbose_name is set to Permission Codename for admin display",
        ],
        "format_details": [
            "Format pattern is module.action_resource for structured identification",
            "Module prefix maps to functional areas like products sales inventory",
            "Action component is a CRUD verb like view add change or delete",
            "Resource suffix identifies the target entity like product order stock",
            "Examples include products.view_product and sales.add_order",
            "Lowercase convention is enforced for all codename components",
        ],
        "validation_details": [
            "Validation ensures codename is not empty and within length limit",
            "Validation checks uniqueness at the database level via unique constraint",
            "Validation will enforce format pattern in future validation tasks",
            "Help text documents format requirements with concrete examples",
            "Codename serves as the primary lookup key for permission checks",
            "Database index on codename accelerates permission resolution queries",
        ],
    }
    logger.debug(
        "permission codename field config: codename_details=%d, format_details=%d",
        len(config["codename_details"]),
        len(config["format_details"]),
    )
    return config


def get_permission_name_field_config() -> dict:
    """Return Permission name field configuration for human-readable display.

    SubPhase-05, Group-B, Task 17.
    """
    config: dict = {
        "configured": True,
        "name_details": [
            "Name field is a CharField with max_length of 255 characters",
            "Name field is required with blank set to False by default",
            "Name field verbose_name is set to Permission Name for admin display",
            "Name provides human-readable description for UI permission listings",
            "Name follows Title Case convention like View Product or Add Sales Order",
            "Name field does not have a database index as it is not used for lookups",
        ],
        "convention_details": [
            "Naming convention starts with the action verb like View Add Edit Delete",
            "Naming convention uses Title Case capitalizing each word in the name",
            "Naming convention is descriptive and specific like Edit Customer Details",
            "Naming convention follows consistent patterns across all permission names",
            "Examples include View Product and Create Sales Order and Delete Customer",
            "Name should clearly communicate the permission purpose to administrators",
        ],
        "display_details": [
            "Name is rendered in role editor interfaces for permission selection",
            "Name appears in permission selection dropdowns for role assignment",
            "Name is shown in user permission lists within the admin panel",
            "Name is used in audit log displays to describe granted permissions",
            "Name provides accessibility for non-technical administrators",
            "Help text documents the naming purpose with concrete UI examples",
        ],
    }
    logger.debug(
        "permission name field config: name_details=%d, convention_details=%d",
        len(config["name_details"]),
        len(config["convention_details"]),
    )
    return config


def get_permission_module_field_config() -> dict:
    """Return Permission module field configuration for functional grouping.

    SubPhase-05, Group-B, Task 18.
    """
    config: dict = {
        "configured": True,
        "module_details": [
            "Module field is a CharField with max_length of 50 characters",
            "Module field has choices parameter as empty list pending ModuleChoices",
            "Module field has db_index set to True for efficient filtering queries",
            "Module field is required with blank set to False by default",
            "Module field verbose_name is set to Module for admin display",
            "Module field help text references examples like products sales inventory",
        ],
        "organization_details": [
            "Module groups permissions by functional area of the application",
            "Products module covers view_product add_product change_product delete_product",
            "Inventory module covers view_stock adjust_stock view_stock_movement",
            "Sales module covers view_order add_order process_payment operations",
            "Customers module covers view_customer add_customer edit_customer",
            "Additional modules include vendors hr accounting reports and settings",
        ],
        "filtering_details": [
            "Database index on module enables fast filtering of permissions by area",
            "Module filtering supports queries like Permission.objects.filter(module=X)",
            "Module combined with action enables precise permission subset queries",
            "ModuleChoices will be defined in Task 23 to constrain valid module values",
            "Composite index on module and action is planned for Meta class indexes",
            "Module-based grouping simplifies role permission assignment workflows",
        ],
    }
    logger.debug(
        "permission module field config: module_details=%d, organization_details=%d",
        len(config["module_details"]),
        len(config["organization_details"]),
    )
    return config


def get_permission_action_field_config() -> dict:
    """Return Permission action field configuration for CRUD operation types.

    SubPhase-05, Group-B, Task 19.
    """
    config: dict = {
        "configured": True,
        "action_details": [
            "Action field is a CharField with max_length of 20 characters",
            "Action field has choices parameter as empty list pending ActionChoices",
            "Action field has db_index set to True for efficient filtering queries",
            "Action field is required with blank set to False by default",
            "Action field verbose_name is set to Action for admin display",
            "Action field help text references examples like view add change delete",
        ],
        "type_details": [
            "View action grants read access to resources mapping to GET and HEAD methods",
            "Add action grants create access for new resources mapping to POST method",
            "Change action grants update access for existing resources mapping to PUT PATCH",
            "Delete action grants removal access for resources mapping to DELETE method",
            "Action types follow Django CRUD conventions for consistency across the system",
            "ActionChoices will be defined in Task 24 to constrain valid action values",
        ],
        "hierarchy_details": [
            "Read-only level includes only view action for customer and viewer roles",
            "Basic user level includes view and add actions for staff creating records",
            "Editor level includes view add and change actions for department managers",
            "Full access level includes view add change and delete for admin roles",
            "Action hierarchy supports progressive permission escalation by role level",
            "Action-based filtering enables queries like Permission.objects.filter(action=X)",
        ],
    }
    logger.debug(
        "permission action field config: action_details=%d, type_details=%d",
        len(config["action_details"]),
        len(config["type_details"]),
    )
    return config


def get_permission_group_model_config() -> dict:
    """Return PermissionGroup model class configuration for grouping permissions.

    SubPhase-05, Group-B, Task 20.
    """
    config: dict = {
        "configured": True,
        "model_details": [
            "PermissionGroup model class extends BaseModel for common fields",
            "PermissionGroup is defined in backend/apps/users/models/permission.py",
            "PermissionGroup groups related permissions for easier management",
            "PermissionGroup model is defined after the Permission model in the file",
            "PermissionGroup inherits id created_at updated_at is_active from BaseModel",
            "PermissionGroup serves as a container for bulk permission assignment",
        ],
        "meta_details": [
            "Meta class sets db_table to users_permission_group for explicit naming",
            "Meta class sets verbose_name to Permission Group for admin display",
            "Meta class sets verbose_name_plural to Permission Groups for admin lists",
            "Meta class defines ordering by group_name for alphabetical display",
            "Meta class configuration follows Django conventions for model metadata",
            "Meta class ensures consistent database table naming across environments",
        ],
        "method_details": [
            "The __str__ method returns group_name for readable string representation",
            "Helper methods include add_permission for adding permissions to the group",
            "Helper methods include remove_permission for removing permissions from group",
            "Helper methods include get_permission_codenames for listing codenames",
            "Helper methods accept both Permission instances and codename strings",
            "Helper methods simplify permission management through the group interface",
        ],
    }
    logger.debug(
        "permission group model config: model_details=%d, meta_details=%d",
        len(config["model_details"]),
        len(config["meta_details"]),
    )
    return config


def get_permission_group_name_field_config() -> dict:
    """Return PermissionGroup group_name field configuration for unique naming.

    SubPhase-05, Group-B, Task 21.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "group_name field is a CharField with max_length of 100 characters",
            "group_name field has unique constraint set to True for no duplicate names",
            "group_name field has db_index set to True for efficient lookups",
            "group_name field is required with blank set to False by default",
            "group_name field verbose_name is set to Group Name for admin display",
            "group_name field help text includes examples like Product Management",
        ],
        "naming_details": [
            "Product Management group contains all product related permissions",
            "Sales Operations group contains order and payment permissions",
            "Inventory Control group contains stock and warehouse permissions",
            "Customer Service group contains customer support and refund permissions",
            "Financial Operations group contains payment accounting and tax permissions",
            "Report Access group contains all reporting and analytics permissions",
        ],
        "constraint_details": [
            "Unique constraint prevents duplicate group names in the database",
            "Database index on group_name accelerates name-based lookups",
            "CharField max_length of 100 allows descriptive group names",
            "Required field ensures every permission group has a meaningful name",
            "Ordering in Meta uses group_name for consistent alphabetical display",
            "Admin search and filter can use group_name for quick group lookup",
        ],
    }
    logger.debug(
        "permission group name field config: field_details=%d, naming_details=%d",
        len(config["field_details"]),
        len(config["naming_details"]),
    )
    return config


def get_permission_group_m2m_field_config() -> dict:
    """Return PermissionGroup permissions ManyToManyField configuration.

    SubPhase-05, Group-B, Task 22.
    """
    config: dict = {
        "configured": True,
        "m2m_details": [
            "permissions field is a ManyToManyField referencing the Permission model",
            "permissions field has related_name set to permission_groups for reverse lookup",
            "permissions field has blank set to True allowing initially empty groups",
            "permissions field verbose_name is set to Permissions for admin display",
            "permissions field help text says Select permissions to include in this group",
            "Django auto-generates an intermediate table for the M2M relationship",
        ],
        "relationship_details": [
            "M2M relationship enables assigning multiple permissions to one group",
            "M2M relationship enables a permission to belong to multiple groups",
            "Reverse lookup uses permission.permission_groups.all() from Permission side",
            "Forward lookup uses group.permissions.all() from PermissionGroup side",
            "Intermediate table stores permissiongroup_id and permission_id pairs",
            "Unique constraint on the intermediate table prevents duplicate assignments",
        ],
        "usage_details": [
            "Bulk assignment pattern adds all module permissions to a group at once",
            "Role assignment pattern copies group permissions to a role via add method",
            "Codename listing pattern uses get_permission_codenames for flat list output",
            "Prefetch_related should be used when querying groups with permissions",
            "Admin interface displays permissions as a filter_horizontal widget",
            "API serializer nests permission data within the group response payload",
        ],
    }
    logger.debug(
        "permission group m2m field config: m2m_details=%d, relationship_details=%d",
        len(config["m2m_details"]),
        len(config["relationship_details"]),
    )
    return config


def get_module_choices_config() -> dict:
    """Return ModuleChoices constants configuration for permission module types.

    SubPhase-05, Group-B, Task 23.
    """
    config: dict = {
        "configured": True,
        "choices_details": [
            "ModuleChoices class inherits from models.TextChoices for enum support",
            "ModuleChoices is defined in backend/apps/users/models/permission.py",
            "ModuleChoices defines nine constants for all system functional modules",
            "ModuleChoices constants use lowercase values and Title Case labels",
            "ModuleChoices.choices property returns list of value-label tuples",
            "ModuleChoices is used by Permission.module field for constrained input",
        ],
        "module_details": [
            "PRODUCTS constant has value products and label Products for catalog",
            "INVENTORY constant has value inventory and label Inventory for stock",
            "SALES constant has value sales and label Sales for orders and payments",
            "CUSTOMERS constant has value customers and label Customers for CRM",
            "VENDORS constant has value vendors and label Vendors for suppliers",
            "HR constant has value hr and label Human Resources for employees",
        ],
        "integration_details": [
            "ACCOUNTING constant has value accounting and label Accounting for finance",
            "REPORTS constant has value reports and label Reports for analytics",
            "SETTINGS constant has value settings and label Settings for configuration",
            "Permission model module field uses choices=ModuleChoices.choices parameter",
            "Query filtering uses ModuleChoices.PRODUCTS for type-safe module lookups",
            "Django admin displays human-readable labels via get_module_display method",
        ],
    }
    logger.debug(
        "module choices config: choices_details=%d, module_details=%d",
        len(config["choices_details"]),
        len(config["module_details"]),
    )
    return config


def get_action_choices_config() -> dict:
    """Return ActionChoices constants configuration for CRUD action types.

    SubPhase-05, Group-B, Task 24.
    """
    config: dict = {
        "configured": True,
        "choices_details": [
            "ActionChoices class inherits from models.TextChoices for enum support",
            "ActionChoices is defined in backend/apps/users/models/permission.py",
            "ActionChoices defines four constants for standard CRUD operations",
            "ActionChoices constants use lowercase values and Title Case labels",
            "ActionChoices.choices property returns list of value-label tuples",
            "ActionChoices is used by Permission.action field for constrained input",
        ],
        "action_details": [
            "VIEW constant has value view and label View mapping to GET HTTP method",
            "ADD constant has value add and label Add mapping to POST HTTP method",
            "CHANGE constant has value change and label Change mapping to PUT PATCH",
            "DELETE constant has value delete and label Delete mapping to DELETE method",
            "Action constants follow Django admin naming conventions for consistency",
            "Action values form part of the codename pattern module.action_resource",
        ],
        "pattern_details": [
            "Permission codename follows pattern module.action_resource for structure",
            "Example codenames include products.view_product and sales.add_order",
            "Action hierarchy supports progressive escalation from view to full CRUD",
            "Read-only level grants only view action for restricted access roles",
            "Full access level grants view add change and delete for admin roles",
            "Query filtering uses ActionChoices.VIEW for type-safe action lookups",
        ],
    }
    logger.debug(
        "action choices config: choices_details=%d, action_details=%d",
        len(config["choices_details"]),
        len(config["action_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-B: Permission Model – Tasks 25-30
# ---------------------------------------------------------------------------


def get_default_permissions_migration_config() -> dict:
    """Return default permissions migration configuration for data seeding.

    SubPhase-05, Group-B, Task 25.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "Migration file is 0004_create_default_permissions in users migrations",
            "Migration uses RunPython operation with forward and reverse functions",
            "Forward function is create_default_permissions using bulk_create",
            "Reverse function is delete_default_permissions using filter and delete",
            "Helper function create_permission builds codename as module.action_resource",
            "Migration depends on 0003_create_permission_model for table schema",
        ],
        "structure_details": [
            "Permission creation helper accepts module action resource and description",
            "Codename format follows pattern module.action_resource consistently",
            "Name field is auto-generated as Can action resource for readability",
            "Timestamp fields created_at and updated_at are set to timezone.now()",
            "Permissions are collected into module lists then combined for bulk_create",
            "Bulk create uses Permission.objects.bulk_create for efficient insertion",
        ],
        "coverage_details": [
            "Products module receives 17 permissions for catalog and pricing",
            "Inventory module receives 22 permissions for stock and warehouses",
            "Sales module receives 23 permissions for orders invoices and payments",
            "Reports module receives 29 permissions for analytics and dashboards",
            "Total of 91 default permissions are created across all four modules",
            "Reverse migration deletes all 91 permissions by codename filter",
        ],
    }
    logger.debug(
        "default permissions migration config: migration_details=%d, structure_details=%d",
        len(config["migration_details"]),
        len(config["structure_details"]),
    )
    return config


def get_products_module_permissions_config() -> dict:
    """Return Products module permissions configuration for catalog access control.

    SubPhase-05, Group-B, Task 26.
    """
    config: dict = {
        "configured": True,
        "crud_details": [
            "products.view_product grants read access to product list and details",
            "products.add_product grants creation of new products in the catalog",
            "products.change_product grants editing of existing product information",
            "products.delete_product grants removal of products from catalog",
            "products.view_category grants read access to product categories",
            "products.add_category grants creation of new product categories",
        ],
        "category_details": [
            "products.change_category grants editing of product categories",
            "products.delete_category grants removal of product categories",
            "products.view_pricing grants read access to product prices",
            "products.change_pricing grants ability to update product prices",
            "products.approve_pricing grants approval of product price changes",
            "products.view_product_stock grants viewing of product stock levels",
        ],
        "special_details": [
            "products.adjust_product_stock grants adjusting stock for products",
            "products.upload_product_image grants uploading of product images",
            "products.delete_product_image grants removal of product images",
            "products.import_products grants bulk import of products from files",
            "products.export_products grants exporting product data to files",
            "Products module defines 17 total permissions for catalog management",
        ],
    }
    logger.debug(
        "products module permissions config: crud_details=%d, category_details=%d",
        len(config["crud_details"]),
        len(config["category_details"]),
    )
    return config


def get_inventory_module_permissions_config() -> dict:
    """Return Inventory module permissions configuration for stock access control.

    SubPhase-05, Group-B, Task 27.
    """
    config: dict = {
        "configured": True,
        "stock_details": [
            "inventory.view_stock grants read access to stock levels and inventory",
            "inventory.add_stock grants creation of new stock entries",
            "inventory.change_stock grants updating of stock information",
            "inventory.delete_stock grants removal of stock entries",
            "inventory.view_warehouse grants read access to warehouse list and details",
            "inventory.add_warehouse grants creation of new warehouses",
        ],
        "movement_details": [
            "inventory.change_warehouse grants editing warehouse information",
            "inventory.delete_warehouse grants removal of warehouses",
            "inventory.view_stock_movement grants viewing stock movement history",
            "inventory.create_stock_movement grants recording new stock movements",
            "inventory.approve_stock_movement grants approval of stock movements",
            "inventory.create_stock_adjustment grants creating stock adjustments",
        ],
        "operations_details": [
            "inventory.approve_stock_adjustment grants approval of stock adjustments",
            "inventory.view_stock_adjustment grants viewing adjustment history",
            "inventory.create_stock_transfer grants transfers between warehouses",
            "inventory.approve_stock_transfer grants approval of stock transfers",
            "inventory.receive_stock_transfer grants receiving transferred stock",
            "Inventory module defines 22 total permissions for stock management",
        ],
    }
    logger.debug(
        "inventory module permissions config: stock_details=%d, movement_details=%d",
        len(config["stock_details"]),
        len(config["movement_details"]),
    )
    return config


def get_sales_module_permissions_config() -> dict:
    """Return Sales module permissions configuration for order access control.

    SubPhase-05, Group-B, Task 28.
    """
    config: dict = {
        "configured": True,
        "order_details": [
            "sales.view_order grants read access to sales orders and details",
            "sales.add_order grants creation of new sales orders",
            "sales.change_order grants editing of existing sales orders",
            "sales.delete_order grants removal of sales orders",
            "sales.confirm_order grants confirmation of pending orders",
            "sales.cancel_order grants cancellation of sales orders",
        ],
        "invoice_details": [
            "sales.complete_order grants marking orders as complete",
            "sales.view_invoice grants read access to invoices",
            "sales.create_invoice grants generation of customer invoices",
            "sales.void_invoice grants voiding of issued invoices",
            "sales.send_invoice grants sending invoices to customers",
            "sales.view_payment grants read access to payment records",
        ],
        "financial_details": [
            "sales.record_payment grants recording customer payments",
            "sales.void_payment grants voiding payment records",
            "sales.refund_payment grants processing payment refunds",
            "sales.view_quotation grants viewing sales quotations",
            "sales.create_quotation grants creating sales quotations",
            "Sales module defines 23 total permissions for revenue operations",
        ],
    }
    logger.debug(
        "sales module permissions config: order_details=%d, invoice_details=%d",
        len(config["order_details"]),
        len(config["invoice_details"]),
    )
    return config


def get_reports_module_permissions_config() -> dict:
    """Return Reports module permissions configuration for analytics access control.

    SubPhase-05, Group-B, Task 29.
    """
    config: dict = {
        "configured": True,
        "analytics_details": [
            "reports.view_sales_report grants viewing sales analytics and reports",
            "reports.view_revenue_report grants viewing revenue and earnings reports",
            "reports.view_sales_by_product grants product-wise sales analysis",
            "reports.view_sales_by_customer grants customer-wise sales analysis",
            "reports.view_inventory_report grants viewing inventory analysis reports",
            "reports.view_stock_level_report grants viewing current stock level reports",
        ],
        "financial_details": [
            "reports.view_stock_movement_report grants viewing movement history reports",
            "reports.view_reorder_report grants viewing reorder point alerts",
            "reports.view_financial_report grants viewing financial reports",
            "reports.view_profit_loss_report grants viewing profit and loss statements",
            "reports.view_cashflow_report grants viewing cash flow reports",
            "reports.view_tax_report grants viewing tax reports and calculations",
        ],
        "dashboard_details": [
            "reports.create_custom_report grants creating custom report definitions",
            "reports.save_report_template grants saving report templates",
            "reports.share_report grants sharing reports with other users",
            "reports.view_sales_dashboard grants viewing the sales dashboard",
            "reports.view_executive_dashboard grants viewing executive dashboard",
            "Reports module defines 29 total permissions for analytics and dashboards",
        ],
    }
    logger.debug(
        "reports module permissions config: analytics_details=%d, financial_details=%d",
        len(config["analytics_details"]),
        len(config["financial_details"]),
    )
    return config


def get_permissions_documentation_config() -> dict:
    """Return permissions documentation configuration for developer reference.

    SubPhase-05, Group-B, Task 30.
    """
    config: dict = {
        "configured": True,
        "documentation_details": [
            "Permissions guide file is created at backend/apps/users/docs/permissions_guide.md",
            "Documentation covers permission system architecture and model relationships",
            "Documentation explains codename format as module.action_resource naming",
            "Documentation lists all nine modules with their purposes and permission counts",
            "Documentation provides code examples for checking permissions in views",
            "Documentation includes template permission checks using perms context",
        ],
        "convention_details": [
            "Naming convention format is module.action_resource for all permissions",
            "Module prefix maps to functional areas like products sales inventory",
            "Action component follows Django conventions like view add change delete",
            "Resource suffix identifies the target entity like product stock order",
            "Custom actions include approve export import and schedule operations",
            "Permission groups organize related permissions for bulk role assignment",
        ],
        "guidance_details": [
            "Role-permission mapping section shows typical role configurations",
            "Best practices include always using permission checks in views",
            "Troubleshooting covers permission not found and caching issues",
            "API documentation references DRF permission classes and endpoints",
            "Migration guide explains running and verifying default permissions",
            "Total system has 91 default permissions across four core modules",
        ],
    }
    logger.debug(
        "permissions documentation config: documentation_details=%d, convention_details=%d",
        len(config["documentation_details"]),
        len(config["convention_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-C: Role-Permission Assignment – Tasks 31-36
# ---------------------------------------------------------------------------


def get_role_permission_model_class_config() -> dict:
    """Return RolePermission model class configuration for junction table.

    SubPhase-05, Group-C, Task 31.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "RolePermission model class extends BaseModel for tenant and audit support",
            "RolePermission is defined in backend/apps/users/models/role_permission.py",
            "RolePermission serves as junction table for Role-Permission many-to-many",
            "RolePermission inherits id created_at updated_at is_active from BaseModel",
            "RolePermission includes audit fields granted_at and granted_by for tracking",
            "RolePermission docstring explains junction purpose and audit tracking",
        ],
        "meta_details": [
            "Meta class sets db_table to users_role_permissions for explicit naming",
            "Meta class sets verbose_name to Role Permission for admin display",
            "Meta class sets verbose_name_plural to Role Permissions for admin lists",
            "Meta class defines ordering by role and permission for consistent display",
            "Meta class includes unique_together constraint on role and permission",
            "Meta class defines indexes for role_permission pair and granted_at field",
        ],
        "method_details": [
            "The __str__ method returns role.name arrow permission.codename format",
            "The __repr__ method returns detailed representation with granted info",
            "The __repr__ method shows granted_by username or System for null values",
            "The clean method validates permission scope matches role level",
            "Model file imports django.db.models and django.conf.settings",
            "Model is registered in users/models/__init__.py for package access",
        ],
    }
    logger.debug(
        "role permission model class config: class_details=%d, meta_details=%d",
        len(config["class_details"]),
        len(config["meta_details"]),
    )
    return config


def get_role_permission_role_fk_config() -> dict:
    """Return RolePermission role ForeignKey field configuration.

    SubPhase-05, Group-C, Task 32.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "role field is a ForeignKey linking to users.Role model via string ref",
            "role field uses on_delete CASCADE to remove assignments when role deleted",
            "role field has related_name set to role_permissions for reverse lookup",
            "role field has db_index set to True for query optimization",
            "role field help_text says The role that is granted this permission",
            "role field is required and does not allow blank or null values",
        ],
        "relationship_details": [
            "Forward lookup uses role_permission.role to access the linked Role",
            "Reverse lookup uses role.role_permissions.all() for all assignments",
            "CASCADE delete ensures no orphaned assignments when role is removed",
            "String reference users.Role avoids circular import problems",
            "Database index on role_id accelerates role-based permission queries",
            "Role field is first in the unique_together constraint pair",
        ],
        "query_details": [
            "Filter by role: RolePermission.objects.filter(role=admin_role)",
            "Prefetch related: Role.objects.prefetch_related(role_permissions)",
            "Count permissions: role.role_permissions.count() for assignment total",
            "Join query: RolePermission.objects.select_related(role) for eager load",
            "Exists check: role.role_permissions.filter(permission=perm).exists()",
            "Role deletion cascades to remove all associated RolePermission records",
        ],
    }
    logger.debug(
        "role permission role fk config: field_details=%d, relationship_details=%d",
        len(config["field_details"]),
        len(config["relationship_details"]),
    )
    return config


def get_role_permission_perm_fk_config() -> dict:
    """Return RolePermission permission ForeignKey field configuration.

    SubPhase-05, Group-C, Task 33.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "permission field is ForeignKey linking to users.Permission via string ref",
            "permission field uses on_delete CASCADE to remove when permission deleted",
            "permission field has related_name set to permission_roles for reverse lookup",
            "permission field has db_index set to True for query optimization",
            "permission field help_text says The permission being granted to the role",
            "permission field is required and does not allow blank or null values",
        ],
        "relationship_details": [
            "Forward lookup uses role_permission.permission to access Permission",
            "Reverse lookup uses permission.permission_roles.all() for all assignments",
            "CASCADE delete ensures no orphaned assignments when permission removed",
            "String reference users.Permission avoids circular import problems",
            "Database index on permission_id accelerates permission-based queries",
            "Permission field is second in the unique_together constraint pair",
        ],
        "query_details": [
            "Filter by permission: RolePermission.objects.filter(permission=perm)",
            "Prefetch: Permission.objects.prefetch_related(permission_roles)",
            "Roles with perm: Permission.objects.get(codename=X).permission_roles.all()",
            "Join query: RolePermission.objects.select_related(permission) for eager load",
            "Module filter: RolePermission.objects.filter(permission__module=products)",
            "Permission deletion cascades to remove all associated RolePermission records",
        ],
    }
    logger.debug(
        "role permission perm fk config: field_details=%d, relationship_details=%d",
        len(config["field_details"]),
        len(config["relationship_details"]),
    )
    return config


def get_granted_at_field_config() -> dict:
    """Return RolePermission granted_at DateTimeField configuration.

    SubPhase-05, Group-C, Task 34.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "granted_at field is a DateTimeField with auto_now_add set to True",
            "granted_at field has editable set to False for immutable timestamp",
            "granted_at field has db_index set to True for time-based queries",
            "granted_at field help_text says Timestamp when permission was granted",
            "granted_at field is separate from BaseModel created_at for clarity",
            "granted_at field captures the exact moment of permission assignment",
        ],
        "audit_details": [
            "Audit trail uses granted_at for when permission was assigned to role",
            "Time-based queries filter granted_at for recent assignments",
            "Compliance reporting uses granted_at for permission grant history",
            "Database index on granted_at accelerates temporal audit queries",
            "Auto_now_add ensures timestamp is set once and cannot be modified",
            "Editable False prevents accidental modification of audit timestamp",
        ],
        "usage_details": [
            "Today assignments: filter(granted_at__date=timezone.now().date())",
            "Recent 30 days: filter(granted_at__gte=now minus timedelta(days=30))",
            "Date range: filter(granted_at__range=(start_date, end_date))",
            "Ordering by granted_at shows most recent assignments first",
            "Combined with granted_by provides complete audit trail record",
            "Meta indexes include granted_at for efficient temporal queries",
        ],
    }
    logger.debug(
        "granted at field config: field_details=%d, audit_details=%d",
        len(config["field_details"]),
        len(config["audit_details"]),
    )
    return config


def get_granted_by_field_config() -> dict:
    """Return RolePermission granted_by ForeignKey field configuration.

    SubPhase-05, Group-C, Task 35.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "granted_by field is ForeignKey linking to settings.AUTH_USER_MODEL",
            "granted_by field uses on_delete SET_NULL to preserve audit records",
            "granted_by field has null and blank set to True for system assignments",
            "granted_by field has related_name set to granted_role_permissions",
            "granted_by field has db_index set to True for user-based queries",
            "granted_by field help_text explains NULL means system assignment",
        ],
        "null_handling_details": [
            "NULL granted_by indicates system-assigned permission from migrations",
            "NULL granted_by indicates automated assignment from default roles",
            "SET_NULL on_delete preserves audit record even if granting user deleted",
            "Admin UI assignments populate granted_by with the current admin user",
            "API endpoint assignments populate granted_by with authenticated user",
            "Bulk assignment scripts may set granted_by to NULL or service account",
        ],
        "relationship_details": [
            "Forward lookup uses role_permission.granted_by to access granting user",
            "Reverse lookup uses user.granted_role_permissions.all() for history",
            "User deletion sets granted_by to NULL but keeps RolePermission record",
            "Dynamic user model reference via settings.AUTH_USER_MODEL for flexibility",
            "Combined with granted_at provides who-and-when audit trail",
            "Query by user: RolePermission.objects.filter(granted_by=admin_user)",
        ],
    }
    logger.debug(
        "granted by field config: field_details=%d, null_handling_details=%d",
        len(config["field_details"]),
        len(config["null_handling_details"]),
    )
    return config


def get_role_permission_unique_constraint_config() -> dict:
    """Return RolePermission unique_together constraint configuration.

    SubPhase-05, Group-C, Task 36.
    """
    config: dict = {
        "configured": True,
        "constraint_details": [
            "unique_together constraint combines role and permission fields",
            "Constraint prevents duplicate role-permission assignment pairs",
            "Constraint is defined as unique_together = [['role', 'permission']]",
            "Database automatically creates a unique index for the constraint",
            "Duplicate insert raises IntegrityError at the database level",
            "Constraint name in database is auto-generated by Django ORM",
        ],
        "behavior_details": [
            "First assignment of role-permission pair succeeds normally",
            "Second assignment of same pair raises IntegrityError exception",
            "Different roles can share the same permission without conflict",
            "Same role can have many different permissions without conflict",
            "Unique constraint applies per tenant via BaseModel tenant field",
            "Admin interface enforces constraint via form validation",
        ],
        "index_details": [
            "Meta indexes include composite index on role and permission fields",
            "Composite index named idx_role_perm for explicit identification",
            "Additional index on granted_at named idx_granted_at for audit queries",
            "Unique constraint index accelerates lookup of existing assignments",
            "Combined indexes optimize both constraint checks and query performance",
            "PostgreSQL creates unique index automatically from unique_together",
        ],
    }
    logger.debug(
        "role permission unique constraint config: constraint_details=%d, behavior_details=%d",
        len(config["constraint_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_role_permission_manager_class_config() -> dict:
    """Return RolePermissionManager class configuration for assignment management.

    SubPhase-05, Group-C, Task 37.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "RolePermissionManager inherits from django.db.models.Manager base class",
            "Manager is defined in backend/apps/users/managers/role_permission_manager.py",
            "Manager provides methods for assigning revoking and checking permissions",
            "Manager handles permission inheritance from parent roles in hierarchy",
            "Manager supports audit trail tracking of who granted each permission",
            "Manager is set as the default manager on RolePermission model",
        ],
        "structure_details": [
            "Managers directory is created at backend/apps/users/managers/",
            "Managers __init__.py exports RolePermissionManager in __all__",
            "Module imports models from django.db and ValidationError from core.exceptions",
            "Module imports Optional and Set from typing for type annotations",
            "Class docstring documents assignment revocation and inheritance features",
            "Manager is registered on RolePermission model via objects attribute",
        ],
        "method_details": [
            "assign_permission method creates role-permission links with audit trail",
            "revoke_permission method removes role-permission links safely",
            "has_permission method checks permission existence with inheritance",
            "_get_all_parent_roles helper collects ancestor roles to avoid loops",
            "All methods include parameter validation raising ValidationError",
            "All methods include info-level logging for assignment tracking",
        ],
    }
    logger.debug(
        "role permission manager class config: class_details=%d, structure_details=%d",
        len(config["class_details"]),
        len(config["structure_details"]),
    )
    return config


def get_assign_permission_method_config() -> dict:
    """Return assign_permission method configuration for permission granting.

    SubPhase-05, Group-C, Task 38.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "assign_permission accepts role permission and optional granted_by user",
            "Method returns the RolePermission instance after creation or retrieval",
            "Method uses get_or_create for idempotent behavior on duplicate calls",
            "Method sets granted_by in defaults dict for audit trail tracking",
            "Method raises ValidationError if role or permission is None or unsaved",
            "Method signature includes full type hints for all parameters",
        ],
        "audit_details": [
            "granted_by field records the user who assigned the permission",
            "granted_at field auto-sets via auto_now_add on the DateTimeField",
            "Logging records permission codename role name and granting user",
            "Logger uses info level for successful assignment creation events",
            "System assignments have granted_by as None indicating automated action",
            "Audit trail persists even if the granting user is later deleted",
        ],
        "idempotency_details": [
            "Calling assign_permission multiple times for same pair is safe",
            "Second call returns the existing RolePermission without creating",
            "get_or_create pattern prevents IntegrityError from unique constraint",
            "Existing record is returned unchanged including original granted_by",
            "No duplicate RolePermission records can exist for the same pair",
            "Boolean created flag from get_or_create controls logging behavior",
        ],
    }
    logger.debug(
        "assign permission method config: method_details=%d, audit_details=%d",
        len(config["method_details"]),
        len(config["audit_details"]),
    )
    return config


def get_revoke_permission_method_config() -> dict:
    """Return revoke_permission method configuration for permission removal.

    SubPhase-05, Group-C, Task 39.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "revoke_permission accepts role and permission as required parameters",
            "Method returns boolean True if revoked or False if not found",
            "Method uses filter and delete pattern for safe record removal",
            "Method raises ValidationError if role or permission is None or unsaved",
            "Method signature includes full type hints for parameters and return",
            "Method docstring includes example usage with conditional check",
        ],
        "behavior_details": [
            "Revoking an assigned permission deletes the record and returns True",
            "Revoking a non-assigned permission returns False without raising error",
            "Safe to call even if the permission was never assigned to the role",
            "Deleted count from filter().delete() determines the return value",
            "Logging records permission codename and role name for revocation events",
            "Logger uses info level for successful revocation tracking",
        ],
        "validation_details": [
            "Role parameter must be a saved model instance with a primary key",
            "Permission parameter must be a saved model instance with a primary key",
            "None values for role or permission raise ValidationError immediately",
            "Unsaved instances without pk raise ValidationError for safety",
            "Validation occurs before any database queries are executed",
            "Error messages clearly describe the validation requirement",
        ],
    }
    logger.debug(
        "revoke permission method config: method_details=%d, behavior_details=%d",
        len(config["method_details"]),
        len(config["behavior_details"]),
    )
    return config


def get_has_permission_method_config() -> dict:
    """Return has_permission method configuration for permission checking.

    SubPhase-05, Group-C, Task 40.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "has_permission accepts role permission_codename and check_inheritance flag",
            "Method returns boolean True if permission found or False otherwise",
            "Method uses filter with permission__codename join for direct check",
            "Method uses exists() for efficient boolean query without loading data",
            "Method raises ValidationError if role is None or codename is empty",
            "Default value for check_inheritance is True enabling hierarchy lookup",
        ],
        "inheritance_details": [
            "When check_inheritance is True method walks up the role hierarchy",
            "Recursive call checks parent role if direct assignment not found",
            "Recursion stops at root role where parent is None returning False",
            "Staff role can inherit permissions from Manager parent role",
            "Manager role can inherit permissions from Tenant Admin parent role",
            "Setting check_inheritance to False skips parent role checking",
        ],
        "helper_details": [
            "_get_all_parent_roles helper collects all ancestor Role instances",
            "Helper uses a while loop walking current.parent until None reached",
            "Helper returns a Set of Role instances for efficient membership testing",
            "Helper avoids infinite loops by stopping when parent is None",
            "Helper is used internally by has_permission for batch checking",
            "Performance can be improved by caching permission checks per request",
        ],
    }
    logger.debug(
        "has permission method config: method_details=%d, inheritance_details=%d",
        len(config["method_details"]),
        len(config["inheritance_details"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-C: Default Role Permission Assignments – Tasks 41-46
# ---------------------------------------------------------------------------


def get_super_admin_permissions_config() -> dict:
    """Return super admin permissions migration configuration for unrestricted access.

    SubPhase-05, Group-C, Task 41.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "Migration file named assign_super_admin_permissions for clarity",
            "Forward function assign_super_admin_permissions queries all Permission objects",
            "Super Admin role queried by role_type super_admin with existence check",
            "All permissions assigned using RolePermission bulk_create for efficiency",
            "granted_at set to current timestamp via timezone.now for audit trail",
            "Migration depends on previous permission creation migrations in order",
        ],
        "permission_scope_details": [
            "Super Admin receives every permission in the system without exception",
            "Pattern is wildcard star-dot-star granting all resources all actions",
            "System level permissions included for platform-wide configuration",
            "Tenant level permissions included for all tenant operations",
            "Module level permissions included for complete CRUD on every module",
            "Special permissions like delete export and audit are all included",
        ],
        "reverse_migration_details": [
            "Reverse function remove_super_admin_permissions deletes all assignments",
            "Deletion uses RolePermission filter on role equals super_admin role",
            "Calling delete on queryset removes all assignments in single query",
            "Reverse migration is safe to run without affecting other role assignments",
            "Reverse operation is idempotent and can be run multiple times safely",
            "After reversal Super Admin role exists but has zero permissions",
        ],
    }
    logger.debug(
        "super admin permissions config: migration_details=%d, permission_scope_details=%d",
        len(config["migration_details"]),
        len(config["permission_scope_details"]),
    )
    return config


def get_tenant_admin_permissions_config() -> dict:
    """Return tenant admin permissions migration configuration for tenant-scoped access.

    SubPhase-05, Group-C, Task 42.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "Migration file named assign_tenant_admin_permissions for clarity",
            "Forward function assign_tenant_admin_permissions filters permissions",
            "Tenant Admin role queried by role_type tenant_admin with existence check",
            "Permissions filtered using exclude on resource startswith system prefix",
            "Bulk create used for efficient RolePermission record creation",
            "Migration depends on super admin permissions migration in sequence",
        ],
        "exclusion_details": [
            "system.change_settings excluded to prevent platform-wide config changes",
            "system.view_all_tenants excluded to prevent cross-tenant data access",
            "system.delete_tenant excluded to prevent tenant deletion by admins",
            "users.impersonate_user excluded to prevent identity assumption",
            "Exclusion list is checked before bulk_create to filter out restricted perms",
            "Excluded permissions remain assignable only to Super Admin role",
        ],
        "scope_details": [
            "All tenant level operations are included for full tenant management",
            "All module CRUD operations are included except system module",
            "Export and reporting permissions included for tenant-scoped data only",
            "User management within tenant is fully permitted including add and change",
            "Cross-tenant operations are explicitly excluded from assignment",
            "Permission count is approximately 180 depending on total permissions",
        ],
    }
    logger.debug(
        "tenant admin permissions config: migration_details=%d, exclusion_details=%d",
        len(config["migration_details"]),
        len(config["exclusion_details"]),
    )
    return config


def get_manager_permissions_config() -> dict:
    """Return manager permissions migration configuration for department-level access.

    SubPhase-05, Group-C, Task 43.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "Migration file named assign_manager_permissions for clarity",
            "Forward function assign_manager_permissions uses codename list filtering",
            "Manager role queried by role_type manager with existence check",
            "Permission codename list defines exact permissions for manager scope",
            "Bulk create used for efficient RolePermission record creation",
            "Migration depends on tenant admin permissions migration in sequence",
        ],
        "module_access_details": [
            "Products module grants full CRUD including add change view and delete",
            "Inventory module grants full CRUD including add change view and delete",
            "Orders module grants view and change for status updates only",
            "Customers module grants add change and view but not delete",
            "Staff module grants view only for team oversight capability",
            "Reports module grants view only for department reporting access",
        ],
        "restriction_details": [
            "Users module is completely excluded from manager permissions scope",
            "System module is completely excluded from manager permissions scope",
            "Delete on orders is restricted to prevent accidental data removal",
            "Delete on customers is restricted to preserve customer records",
            "Manager cannot manage other managers or assign roles to anyone",
            "Approximately 50 permissions assigned based on module access matrix",
        ],
    }
    logger.debug(
        "manager permissions config: migration_details=%d, module_access_details=%d",
        len(config["migration_details"]),
        len(config["module_access_details"]),
    )
    return config


def get_staff_permissions_config() -> dict:
    """Return staff permissions migration configuration for basic operational access.

    SubPhase-05, Group-C, Task 44.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "Migration file named assign_staff_permissions for clarity",
            "Forward function assign_staff_permissions uses codename list filtering",
            "Staff role queried by role_type staff with existence check",
            "Permission codename list defines exact permissions for staff scope",
            "Bulk create used for efficient RolePermission record creation",
            "Migration depends on manager permissions migration in sequence",
        ],
        "access_scope_details": [
            "Products module grants add change and view without delete access",
            "Inventory module grants add change and view without delete access",
            "Orders module grants view and limited change for status updates only",
            "Customers module grants view only for lookup during transactions",
            "Own profile change is permitted for personal information updates",
            "Own profile view is permitted for verifying personal details",
        ],
        "limitation_details": [
            "No delete permissions granted on any module to prevent data loss",
            "Reports module is completely excluded from staff access scope",
            "Users module is completely excluded except own profile operations",
            "System module is completely excluded from staff access scope",
            "Staff cannot add customers or create new user accounts",
            "Approximately 25 permissions assigned based on operational needs",
        ],
    }
    logger.debug(
        "staff permissions config: migration_details=%d, access_scope_details=%d",
        len(config["migration_details"]),
        len(config["access_scope_details"]),
    )
    return config


def get_customer_permissions_config() -> dict:
    """Return customer permissions migration configuration for minimal webstore access.

    SubPhase-05, Group-C, Task 45.
    """
    config: dict = {
        "configured": True,
        "migration_details": [
            "Migration file named assign_customer_permissions for clarity",
            "Forward function assign_customer_permissions uses codename list filtering",
            "Customer role queried by role_type customer with existence check",
            "Permission codename list defines minimal permissions for customer scope",
            "Bulk create used for efficient RolePermission record creation",
            "Migration depends on staff permissions migration in sequence",
        ],
        "webstore_access_details": [
            "orders.view_own_order allows customers to see their purchase history",
            "orders.add_order allows customers to place new orders in the webstore",
            "products.view_product allows customers to browse the product catalog",
            "cart.add_cart_item allows customers to add products to shopping cart",
            "cart.change_cart_item allows customers to update cart item quantities",
            "cart.delete_cart_item allows customers to remove items from cart",
        ],
        "data_isolation_details": [
            "users.view_own_profile allows customers to see their account details",
            "users.change_own_profile allows customers to update personal information",
            "Customers cannot view other customers orders or profiles",
            "Customers cannot access any backend ERP modules or admin pages",
            "Customers cannot view inventory reports or system settings",
            "Approximately 8 permissions assigned for minimal webstore functionality",
        ],
    }
    logger.debug(
        "customer permissions config: migration_details=%d, webstore_access_details=%d",
        len(config["migration_details"]),
        len(config["webstore_access_details"]),
    )
    return config


def get_role_permission_system_docs_config() -> dict:
    """Return role-permission system documentation configuration for comprehensive docs.

    SubPhase-05, Group-C, Task 46.
    """
    config: dict = {
        "configured": True,
        "documentation_details": [
            "ROLE_PERMISSION_SYSTEM.md created in backend/apps/users/docs directory",
            "Document includes system overview explaining RBAC architecture purpose",
            "Document includes role hierarchy listing all five system roles",
            "Document includes full permission matrix with modules as rows roles as columns",
            "Document includes usage examples for checking assigning and revoking perms",
            "Document includes default permission sets for each role with counts",
        ],
        "architecture_details": [
            "User to Role relationship is many-to-one via ForeignKey on User model",
            "Role to Permission relationship is many-to-many via RolePermission junction",
            "RolePermission model includes audit fields granted_by and granted_at",
            "Role hierarchy supports inheritance via parent ForeignKey for permission checks",
            "Multi-tenant scoping via tenant ForeignKey on Role model isolates access",
            "Permission codenames follow app_label dot action_underscore model pattern",
        ],
        "maintenance_details": [
            "New permissions require data migration following existing pattern",
            "Role permission changes use forward and reverse RunPython operations",
            "Testing strategy uses unit tests for each config function with 7 assertions",
            "Security follows principle of least privilege granting minimum access",
            "Troubleshooting section covers common permission check failures",
            "API integration section documents view decorators and model-level checks",
        ],
    }
    logger.debug(
        "role permission system docs config: documentation_details=%d, architecture_details=%d",
        len(config["documentation_details"]),
        len(config["architecture_details"]),
    )
    return config


def get_user_role_model_class_config() -> dict:
    """Return UserRole model class configuration for user-role junction table.

    SubPhase-05, Group-D, Task 47.
    """
    config: dict = {
        "configured": True,
        "model_details": [
            "UserRole class created in backend/apps/users/models/user_role.py",
            "Class inherits from BaseModel for UUID primary key and timestamps",
            "BaseModel provides created_at updated_at and deleted_at soft-delete fields",
            "Model serves as junction table linking User and Role in many-to-many",
            "Model includes additional metadata fields for audit trail tracking",
            "Model supports primary role designation for default permission context",
        ],
        "meta_details": [
            "db_table set to users_user_role for explicit table naming",
            "ordering set to negative assigned_at for newest-first default ordering",
            "verbose_name set to User Role for admin display",
            "verbose_name_plural set to User Roles for admin list display",
            "unique_together will be added in Task 53 for user-role uniqueness",
            "indexes will be added for performance on frequent query patterns",
        ],
        "str_method_details": [
            "__str__ returns format username dash role name for readable display",
            "Primary indicator appended as parenthetical when is_primary is True",
            "Format example is john.doe dash Admin with optional Primary tag",
            "Method accesses user.username via ForeignKey relation traversal",
            "Method accesses role.name via ForeignKey relation traversal",
            "Method is used in Django admin and shell for human-readable output",
        ],
    }
    logger.debug(
        "user role model class config: model_details=%d, meta_details=%d",
        len(config["model_details"]),
        len(config["meta_details"]),
    )
    return config


def get_user_role_user_fk_config() -> dict:
    """Return UserRole user ForeignKey configuration for user reference.

    SubPhase-05, Group-D, Task 48.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "Field name is user with type models.ForeignKey referencing AUTH_USER_MODEL",
            "Reference uses settings.AUTH_USER_MODEL for flexible user model swapping",
            "on_delete is CASCADE so deleting user removes all role assignments",
            "related_name is user_roles enabling user.user_roles.all() queries",
            "db_index is True for query performance on user-based lookups",
            "help_text describes the field as User to whom the role is assigned",
        ],
        "cascade_details": [
            "CASCADE means deleting a user automatically deletes all UserRole records",
            "This prevents orphaned role assignments pointing to deleted users",
            "Cascade behavior is appropriate because assignments belong to the user",
            "Soft-delete on user does not trigger cascade only hard delete does",
            "Application-level soft-delete should be preferred over hard deletion",
            "Database-level cascade is the safety net for referential integrity",
        ],
        "query_details": [
            "user.user_roles.all() returns all role assignments for a user",
            "user.user_roles.filter(is_primary=True) gets the primary role assignment",
            "user.user_roles.filter(deleted_at__isnull=True) gets active assignments",
            "select_related role can be used for efficient role data loading",
            "Queryset supports all standard Django ORM filter and exclude methods",
            "Reverse relation user_roles is registered on the User model automatically",
        ],
    }
    logger.debug(
        "user role user fk config: field_details=%d, cascade_details=%d",
        len(config["field_details"]),
        len(config["cascade_details"]),
    )
    return config


def get_user_role_role_fk_config() -> dict:
    """Return UserRole role ForeignKey configuration for role reference.

    SubPhase-05, Group-D, Task 49.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "Field name is role with type models.ForeignKey referencing Role model",
            "Reference uses string literal Role for same-app lazy reference",
            "on_delete is CASCADE so deleting role removes all user assignments",
            "related_name is user_assignments enabling role.user_assignments.all()",
            "db_index is True for query performance on role-based lookups",
            "help_text describes the field as Role assigned to the user",
        ],
        "cascade_details": [
            "CASCADE means deleting a role automatically deletes all UserRole records",
            "This prevents orphaned assignments pointing to deleted roles",
            "Cascade behavior is appropriate because assignments reference the role",
            "Role deletion should be rare as system roles are protected",
            "Application-level checks should prevent accidental role deletion",
            "Database-level cascade is the safety net for referential integrity",
        ],
        "reverse_relation_details": [
            "role.user_assignments.all() returns all users assigned this role",
            "role.user_assignments.count() efficiently counts assigned users",
            "role.user_assignments.filter(is_primary=True) gets primary holders",
            "select_related user can be used for efficient user data loading",
            "Queryset supports filtering by deleted_at for active assignments only",
            "Reverse relation user_assignments is registered on Role model automatically",
        ],
    }
    logger.debug(
        "user role role fk config: field_details=%d, cascade_details=%d",
        len(config["field_details"]),
        len(config["cascade_details"]),
    )
    return config


def get_user_role_assigned_at_field_config() -> dict:
    """Return UserRole assigned_at DateTimeField configuration for audit timestamp.

    SubPhase-05, Group-D, Task 50.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "Field name is assigned_at with type models.DateTimeField",
            "auto_now_add is True so timestamp is automatically set on creation",
            "db_index is True for efficient date-based filtering and ordering",
            "help_text describes the field as Timestamp when role was assigned",
            "Field is read-only after creation because auto_now_add prevents updates",
            "Default ordering on Meta uses negative assigned_at for newest first",
        ],
        "audit_details": [
            "assigned_at provides audit trail for compliance and accountability",
            "Timestamp enables filtering role assignments by date range queries",
            "History tracking allows reviewing when each role was granted",
            "Debugging support helps troubleshoot permission issues by date",
            "Reporting capabilities enable role assignment activity reports",
            "Field works with Django timezone utilities for timezone-aware timestamps",
        ],
        "query_details": [
            "UserRole.objects.filter(assigned_at__gte=cutoff) gets recent assignments",
            "UserRole.objects.order_by(negative assigned_at) lists newest first",
            "assigned_at__range accepts start and end date for range-based filtering",
            "Date truncation functions enable grouping by day week or month",
            "Combined with assigned_by provides complete audit trail for assignments",
            "Timezone-aware queries ensure correct results across time zones",
        ],
    }
    logger.debug(
        "user role assigned at field config: field_details=%d, audit_details=%d",
        len(config["field_details"]),
        len(config["audit_details"]),
    )
    return config


def get_user_role_assigned_by_field_config() -> dict:
    """Return UserRole assigned_by ForeignKey configuration for assigner tracking.

    SubPhase-05, Group-D, Task 51.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "Field name is assigned_by with type models.ForeignKey to AUTH_USER_MODEL",
            "Reference uses settings.AUTH_USER_MODEL for flexible user model swapping",
            "on_delete is SET_NULL preserving assignment record when assigner deleted",
            "related_name is role_assignments_made for reverse query from User",
            "null is True allowing database NULL when assigner is unknown or deleted",
            "blank is True allowing empty value in Django forms and admin interface",
        ],
        "set_null_details": [
            "SET_NULL means deleting the assigner sets assigned_by to NULL not cascade",
            "This preserves the role assignment record for audit trail continuity",
            "NULL value indicates the original assigner account no longer exists",
            "Audit record remains intact showing when and what role was assigned",
            "SET_NULL is safer than CASCADE for audit fields to prevent data loss",
            "Application code should handle None values when displaying assigner info",
        ],
        "accountability_details": [
            "assigned_by tracks which administrator made each role assignment",
            "admin.role_assignments_made.all() shows all assignments by an admin",
            "Accountability supports compliance requirements for access control",
            "Investigation capability helps trace source of incorrect permissions",
            "Historical data preserved even when assigner leaves the organization",
            "Combined with assigned_at provides complete who-when audit information",
        ],
    }
    logger.debug(
        "user role assigned by field config: field_details=%d, set_null_details=%d",
        len(config["field_details"]),
        len(config["set_null_details"]),
    )
    return config


def get_is_primary_field_config() -> dict:
    """Return is_primary BooleanField configuration for default role designation.

    SubPhase-05, Group-D, Task 52.
    """
    config: dict = {
        "configured": True,
        "field_details": [
            "Field name is is_primary with type models.BooleanField",
            "default is False so new role assignments are not primary by default",
            "db_index is True for efficient filtering of primary role assignments",
            "help_text describes the field as Mark this as the user primary role",
            "Only one UserRole per user should have is_primary set to True",
            "Enforcement of single primary is handled in save method override",
        ],
        "business_rule_details": [
            "Save method override clears is_primary on other roles for same user",
            "First role assigned to a user should be automatically set as primary",
            "Primary role cannot be deleted without designating a new primary first",
            "Every active user should have exactly one primary role at all times",
            "Auto-primary logic sets is_primary True when it is the only role",
            "UserRoleManager handles primary role transitions in assign_role method",
        ],
        "usage_details": [
            "Primary role determines default permission context on user login",
            "UI displays primary role badge next to user name in navigation",
            "Permission checks use primary role when context is ambiguous",
            "Default landing page routing based on primary role type",
            "user.user_roles.filter(is_primary=True).first() gets primary assignment",
            "Secondary roles provide additional permissions beyond primary scope",
        ],
    }
    logger.debug(
        "is primary field config: field_details=%d, business_rule_details=%d",
        len(config["field_details"]),
        len(config["business_rule_details"]),
    )
    return config


def get_user_role_unique_constraint_config() -> dict:
    """Return UserRole unique constraint configuration for duplicate prevention.

    SubPhase-05, Group-D, Task 53.
    """
    config: dict = {
        "configured": True,
        "constraint_details": [
            "unique_together on user and role fields prevents duplicate assignments",
            "UniqueConstraint with name unique_user_role provides named constraint",
            "Both unique_together and UniqueConstraint used for Django version compat",
            "Compound index on user and role added for query performance",
            "Additional index on user and is_primary for primary role lookups",
            "Additional index on role and is_primary for role holder queries",
        ],
        "database_behavior_details": [
            "Assigning same role twice to a user raises IntegrityError from database",
            "Assigning different roles to same user succeeds without constraint violation",
            "Assigning same role to different users succeeds without constraint violation",
            "Database-level enforcement is the ultimate safeguard against duplicates",
            "Application-level validation in manager should catch duplicates before DB",
            "IntegrityError should be caught and converted to user-friendly message",
        ],
        "soft_delete_details": [
            "Soft-deleted records still count toward uniqueness constraint",
            "Re-assigning a soft-deleted role requires restoring not creating new record",
            "Manager method checks for soft-deleted existing record and restores it",
            "Permanent deletion of old record would allow new assignment to succeed",
            "This design preserves audit trail by encouraging restore over recreate",
            "Unique constraint applies to active and soft-deleted records equally",
        ],
    }
    logger.debug(
        "user role unique constraint config: constraint_details=%d, database_behavior_details=%d",
        len(config["constraint_details"]),
        len(config["database_behavior_details"]),
    )
    return config


def get_user_role_manager_class_config() -> dict:
    """Return UserRoleManager class configuration for role assignment operations.

    SubPhase-05, Group-D, Task 54.
    """
    config: dict = {
        "configured": True,
        "manager_details": [
            "UserRoleManager class created in backend/apps/users/managers directory",
            "Class inherits from models.Manager for custom queryset methods",
            "Manager imported and set as objects attribute on UserRole model",
            "Manager encapsulates business logic for role assignment operations",
            "Manager uses transaction.atomic decorator for mutation safety",
            "Manager imports ValidationError for parameter validation checks",
        ],
        "purpose_details": [
            "Provides assign_role method for assigning roles to users",
            "Provides remove_role method for removing roles from users",
            "Provides get_roles method for querying user role assignments",
            "Provides get_primary_role convenience method for primary lookups",
            "Provides get_non_primary_roles convenience method for secondary roles",
            "Centralizes all role assignment business logic in one location",
        ],
        "model_integration_details": [
            "UserRole model sets objects equals UserRoleManager instance",
            "Manager replaces default Manager with custom business logic methods",
            "Manager accesses self.model to reference UserRole class dynamically",
            "Manager uses self.filter and self.create for queryset operations",
            "Manager integrates with cache invalidation on role changes",
            "Manager follows Django convention of placing managers in managers module",
        ],
    }
    logger.debug(
        "user role manager class config: manager_details=%d, purpose_details=%d",
        len(config["manager_details"]),
        len(config["purpose_details"]),
    )
    return config


def get_assign_role_method_config() -> dict:
    """Return assign_role method configuration for role assignment logic.

    SubPhase-05, Group-D, Task 55.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "assign_role accepts user role assigned_by and optional is_primary flag",
            "Method is decorated with transaction.atomic for database safety",
            "Method checks if role is already assigned and returns existing record",
            "If existing record found with different is_primary it updates the flag",
            "New UserRole record created with all fields set including assigned_at",
            "Method returns the UserRole instance after creation or update",
        ],
        "primary_role_details": [
            "When is_primary is True all other primary flags for user are cleared",
            "Clearing uses filter on user and is_primary True then update False",
            "Primary role update happens before new assignment to avoid conflicts",
            "User can have exactly one primary role at any time enforced by method",
            "Changing primary role does not require removing old primary assignment",
            "Cache invalidation runs after primary role changes for consistency",
        ],
        "validation_details": [
            "User parameter must not be None or ValidationError is raised",
            "Role parameter must not be None or ValidationError is raised",
            "assigned_by parameter must not be None or ValidationError is raised",
            "Error message clearly states that user role and assigned_by are required",
            "Validation occurs before any database queries or mutations",
            "Invalid parameter types are caught by Django field validation on save",
        ],
    }
    logger.debug(
        "assign role method config: method_details=%d, primary_role_details=%d",
        len(config["method_details"]),
        len(config["primary_role_details"]),
    )
    return config


def get_remove_role_method_config() -> dict:
    """Return remove_role method configuration for role removal logic.

    SubPhase-05, Group-D, Task 56.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "remove_role accepts user and role parameters for targeted removal",
            "Method is decorated with transaction.atomic for database safety",
            "Method queries existing UserRole record and raises error if not found",
            "Deletion uses the model instance delete method for proper signal firing",
            "Method returns True on successful removal for caller confirmation",
            "Cache invalidation runs after successful role removal",
        ],
        "constraint_details": [
            "User must have at least one role so removal of last role is blocked",
            "Total role count checked before deletion to enforce minimum constraint",
            "If count is one or less ValidationError is raised with clear message",
            "Message states Cannot remove role User must have at least one role",
            "Constraint prevents users from ending up in a no-role state",
            "Business rule ensures every active user has at least one role always",
        ],
        "promotion_details": [
            "If removed role was primary another role is promoted to primary",
            "Promotion selects oldest role by assigned_at using order_by ascending",
            "Promoted role has is_primary set to True and saved to database",
            "Promotion happens after deletion to avoid temporary two-primary state",
            "If no other roles exist after deletion promotion is skipped",
            "Promotion logic preserves the single primary role invariant",
        ],
    }
    logger.debug(
        "remove role method config: method_details=%d, constraint_details=%d",
        len(config["method_details"]),
        len(config["constraint_details"]),
    )
    return config


def get_get_roles_method_config() -> dict:
    """Return get_roles method configuration for role querying logic.

    SubPhase-05, Group-D, Task 57.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "get_roles accepts user and optional is_primary filter parameter",
            "Method validates user parameter and raises ValidationError if None",
            "Base queryset filters UserRole by user with select_related on role",
            "Optional is_primary filter narrows results to primary or non-primary",
            "Results ordered by is_primary descending then assigned_at ascending",
            "Method returns QuerySet of UserRole objects for further chaining",
        ],
        "filter_details": [
            "When is_primary is None all roles are returned without filtering",
            "When is_primary is True only the primary role assignment is returned",
            "When is_primary is False only non-primary role assignments returned",
            "select_related role reduces database queries by joining Role table",
            "Ordering places primary role first followed by chronological order",
            "QuerySet is lazy and not evaluated until iterated or sliced",
        ],
        "helper_method_details": [
            "get_primary_role is convenience method returning single Role instance",
            "get_primary_role filters is_primary True and returns role or None",
            "get_non_primary_roles is convenience method calling get_roles with False",
            "Helper methods delegate to get_roles for consistent query behavior",
            "All helper methods validate user parameter before querying database",
            "Helper methods simplify common role lookup patterns in application code",
        ],
    }
    logger.debug(
        "get roles method config: method_details=%d, filter_details=%d",
        len(config["method_details"]),
        len(config["filter_details"]),
    )
    return config


def get_user_has_perm_method_config() -> dict:
    """Return User.has_perm method configuration for permission checking.

    SubPhase-05, Group-D, Task 58.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "has_perm method added to User model accepting perm and optional obj",
            "Method signature is has_perm(self perm str obj None) returning bool",
            "Method leverages get_all_permissions to check against cached permissions",
            "Permission codename is checked for membership in permissions set",
            "obj parameter reserved for future object-level permission checks",
            "Method is compatible with Django standard permission checking pattern",
        ],
        "superuser_check_details": [
            "First check verifies user is_active and is_superuser flags",
            "Active superuser returns True immediately without database query",
            "Inactive superuser does not bypass permission check for safety",
            "Superuser check prevents unnecessary cache and database lookups",
            "Pattern follows Django built-in PermissionsMixin approach",
            "Early return optimizes performance for superuser accounts",
        ],
        "format_handling_details": [
            "Accepts codename only format like view_product for simple checks",
            "Accepts app_label.codename format like products.view_product explicit",
            "Dot presence in perm string determines which format is being used",
            "Full format uses direct set membership check for exact match",
            "Short format uses any() with endswith to find matching permission",
            "Both formats return boolean True if permission found False otherwise",
        ],
    }
    logger.debug(
        "user has perm method config: method_details=%d, superuser_check_details=%d",
        len(config["method_details"]),
        len(config["superuser_check_details"]),
    )
    return config


def get_user_has_role_method_config() -> dict:
    """Return User.has_role method configuration for role checking.

    SubPhase-05, Group-D, Task 59.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "has_role method added to User model accepting role_slug parameter",
            "Method signature is has_role(self role_slug str) returning bool",
            "Method queries UserRole model filtering by user and role slug",
            "Uses QuerySet exists() method for efficient boolean database check",
            "Returns True if user has role assignment False otherwise",
            "Method is simple direct database query without caching initially",
        ],
        "query_details": [
            "Query filters self.user_roles with role__slug equals role_slug",
            "Double underscore traversal accesses slug field on related Role model",
            "exists() returns True if at least one matching record found",
            "exists() is more efficient than count() for boolean checks",
            "Query uses indexed slug field for fast lookup performance",
            "Single database query executed per has_role invocation",
        ],
        "caching_details": [
            "Initial implementation uses direct database query without cache",
            "Future enhancement can add Redis cache using user_roles cache key",
            "Cache key pattern would be user_roles_{user_id} for consistency",
            "Cache TTL would match permission cache at 3600 seconds one hour",
            "Cache invalidation would trigger on role assignment and removal",
            "Simple implementation keeps code readable while allowing optimization",
        ],
    }
    logger.debug(
        "user has role method config: method_details=%d, query_details=%d",
        len(config["method_details"]),
        len(config["query_details"]),
    )
    return config


def get_user_get_all_permissions_config() -> dict:
    """Return User.get_all_permissions method configuration for permission collection.

    SubPhase-05, Group-D, Task 60.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "get_all_permissions method added to User model returning set of strings",
            "Method signature accepts optional include_inactive boolean defaulting False",
            "Return type is set[str] with permissions in app_label.codename format",
            "Method collects permissions from all assigned roles via UserRole",
            "Permissions include inherited permissions from parent roles in hierarchy",
            "Method delegates to _fetch_all_permissions for actual database queries",
        ],
        "collection_details": [
            "User roles queried via self.user_roles with select_related on role",
            "Active roles filtered by role__is_active True unless include_inactive set",
            "For each role RolePermission.objects.get_inherited_permissions called",
            "Inherited permissions include all parent role permissions recursively",
            "Permissions formatted as app_label.codename using content_type app_label",
            "Set data structure ensures unique permissions across multiple roles",
        ],
        "performance_details": [
            "select_related on role reduces N+1 queries for role data",
            "Set operations provide O(1) lookup time for permission checks",
            "Cache integration via Task 61 avoids repeated database queries",
            "include_inactive True bypasses cache for special admin scenarios",
            "Superuser check returns early to avoid unnecessary database work",
            "prefetch_related can further optimize queries for role permissions",
        ],
    }
    logger.debug(
        "user get all permissions config: method_details=%d, collection_details=%d",
        len(config["method_details"]),
        len(config["collection_details"]),
    )
    return config


def get_cache_user_permissions_config() -> dict:
    """Return cache user permissions configuration for Redis-based caching.

    SubPhase-05, Group-D, Task 61.
    """
    config: dict = {
        "configured": True,
        "cache_details": [
            "Permission cache module created at apps/users/cache/permission_cache.py",
            "Cache key pattern is user_permissions_{user_id} for consistent naming",
            "get_user_permissions function checks cache before querying database",
            "Cache TTL set to PERMISSION_CACHE_TTL defaulting to 3600 seconds",
            "Redis backend configured via django_redis with CACHES default setting",
            "Cache stores set of permission strings in app_label.codename format",
        ],
        "invalidation_details": [
            "invalidate_user_permissions function deletes cache key for single user",
            "invalidate_multiple_users function deletes cache keys for user list",
            "UserRoleManager.assign_role calls invalidate after role assignment",
            "UserRoleManager.remove_role calls invalidate after role removal",
            "Role permission changes trigger invalidation for all assigned users",
            "Role parent changes trigger invalidation for all affected role users",
        ],
        "fallback_details": [
            "try-except blocks catch all cache operation exceptions gracefully",
            "Cache failure falls back to direct database query via _fetch_all_permissions",
            "Cache errors are logged with logger.error for monitoring and alerts",
            "Application continues functioning even when Redis is unavailable",
            "Cache hits and misses logged with logger.debug for performance metrics",
            "Graceful degradation ensures no user-facing errors from cache issues",
        ],
    }
    logger.debug(
        "cache user permissions config: cache_details=%d, invalidation_details=%d",
        len(config["cache_details"]),
        len(config["invalidation_details"]),
    )
    return config


def get_document_user_roles_config() -> dict:
    """Return document user roles system configuration for comprehensive docs.

    SubPhase-05, Group-D, Task 62.
    """
    config: dict = {
        "configured": True,
        "documentation_details": [
            "USER_ROLES.md created in backend/docs/user-roles directory",
            "Document includes UserRole model specification with field table",
            "Document includes UserRoleManager methods with signature and examples",
            "Document includes User permission methods has_perm has_role get_all_permissions",
            "Document includes Redis caching strategy with key patterns and TTL settings",
            "Document includes troubleshooting section with common errors and solutions",
        ],
        "section_structure_details": [
            "Overview section explains User-Role system purpose and architecture",
            "Model section documents UserRole fields constraints and relationships",
            "Manager section documents assign_role remove_role and get_roles methods",
            "Permission section documents has_perm has_role and get_all_permissions",
            "Caching section documents Redis cache structure and invalidation triggers",
            "Best practices section covers role assignment and permission guidelines",
        ],
        "reference_details": [
            "Permission codename reference lists all codenames in app_label.codename format",
            "Cache key reference documents all cache key patterns and TTL values",
            "API endpoint reference documents REST endpoints for role management",
            "Code examples section provides practical usage for common scenarios",
            "Migration guide covers database and data migration procedures",
            "Appendices include error codes version history and configuration reference",
        ],
    }
    logger.debug(
        "document user roles config: documentation_details=%d, section_structure_details=%d",
        len(config["documentation_details"]),
        len(config["section_structure_details"]),
    )
    return config


def get_permissions_module_config() -> dict:
    """Return permissions module creation configuration for decorator infrastructure.

    SubPhase-05, Group-E, Task 63.
    """
    config: dict = {
        "configured": True,
        "module_details": [
            "permissions.py file created in backend/apps/core/ directory",
            "Module provides decorators for function-based view permission checks",
            "Module docstring lists all available decorators with usage examples",
            "Module serves as central location for permission enforcement utilities",
            "File location is apps/core/permissions.py alongside models and admin",
            "Module will contain decorators for Tasks 64 through 67 in Group-E",
        ],
        "import_details": [
            "functools.wraps imported for preserving decorated function metadata",
            "PermissionDenied imported from django.core.exceptions for denial",
            "typing imports included for type hints on decorator parameters",
            "logging module imported for debug and error logging in decorators",
            "No model imports at module level to prevent circular import issues",
            "All imports follow Django convention of stdlib then django then local",
        ],
        "structure_details": [
            "Module organized with function decorators section for Tasks 64-67",
            "DRF permission classes section planned for Tasks 68-72 in next doc",
            "View mixins section planned for Tasks 73-75 in subsequent document",
            "Each decorator follows consistent pattern of outer inner wrapper",
            "All decorators check authentication before permission verification",
            "All decorators raise PermissionDenied with descriptive error messages",
        ],
    }
    logger.debug(
        "permissions module config: module_details=%d, import_details=%d",
        len(config["module_details"]),
        len(config["import_details"]),
    )
    return config


def get_permission_required_decorator_config() -> dict:
    """Return permission_required decorator configuration for single permission check.

    SubPhase-05, Group-E, Task 64.
    """
    config: dict = {
        "configured": True,
        "decorator_details": [
            "permission_required function accepts single perm string parameter",
            "Returns inner decorator function that wraps the view function",
            "Uses functools.wraps to preserve original function metadata",
            "Decorator pattern is three-level: outer factory inner decorator wrapper",
            "Docstring documents perm parameter format and PermissionDenied behavior",
            "Compatible with Django function-based views accepting request as first arg",
        ],
        "check_logic_details": [
            "First check verifies request.user.is_authenticated is True",
            "Unauthenticated users get PermissionDenied with Authentication required",
            "Second check calls request.user.has_perm(perm) for permission verification",
            "has_perm supports both codename and app_label.codename formats",
            "Permission check leverages cached permissions from Task 61 cache system",
            "If permission passes the original view_func is called with all arguments",
        ],
        "edge_case_details": [
            "Anonymous users raise PermissionDenied before any permission query",
            "Invalid permission strings cause has_perm to return False and deny access",
            "Empty permission string is treated as invalid and denies access",
            "Error message includes the specific permission name for debugging",
            "Decorator can be stacked with other decorators like login_required",
            "obj parameter in has_perm is reserved for future object-level perms",
        ],
    }
    logger.debug(
        "permission required decorator config: decorator_details=%d, check_logic_details=%d",
        len(config["decorator_details"]),
        len(config["check_logic_details"]),
    )
    return config


def get_role_required_decorator_config() -> dict:
    """Return role_required decorator configuration for role-based access check.

    SubPhase-05, Group-E, Task 65.
    """
    config: dict = {
        "configured": True,
        "decorator_details": [
            "role_required function accepts single role_slug string parameter",
            "Returns inner decorator function that wraps the view function",
            "Uses functools.wraps to preserve original function metadata",
            "Decorator pattern matches permission_required three-level structure",
            "Docstring documents role_slug parameter and PermissionDenied behavior",
            "Compatible with Django function-based views accepting request as first arg",
        ],
        "check_logic_details": [
            "First check verifies request.user.is_authenticated is True",
            "Unauthenticated users get PermissionDenied with Authentication required",
            "Second check calls request.user.has_role(role_slug) for role verification",
            "has_role queries UserRole model filtering by user and role slug field",
            "Role check uses exists() for efficient boolean database lookup",
            "If role check passes the original view_func is called with all arguments",
        ],
        "comparison_details": [
            "role_required checks broader access level than permission_required",
            "permission_required checks specific action like products.add_product",
            "role_required checks general role like manager or tenant-admin",
            "Role-based checks are useful for section-level access control",
            "Permission-based checks are useful for action-level access control",
            "Both decorators can be stacked for combined role and permission checks",
        ],
    }
    logger.debug(
        "role required decorator config: decorator_details=%d, check_logic_details=%d",
        len(config["decorator_details"]),
        len(config["check_logic_details"]),
    )
    return config


def get_any_permission_required_config() -> dict:
    """Return any_permission_required decorator configuration for OR logic checks.

    SubPhase-05, Group-E, Task 66.
    """
    config: dict = {
        "configured": True,
        "decorator_details": [
            "any_permission_required function accepts variable *perms arguments",
            "Returns inner decorator function that wraps the view function",
            "Uses functools.wraps to preserve original function metadata",
            "Decorator implements OR logic requiring at least one permission match",
            "Docstring explains OR behavior and lists all checked permissions",
            "Compatible with Django function-based views accepting request as first arg",
        ],
        "or_logic_details": [
            "Uses Python any() builtin to check if any permission matches",
            "any() short-circuits on first True result for optimal performance",
            "User needs at least ONE of the listed permissions to gain access",
            "Having multiple matching permissions is allowed and still grants access",
            "OR logic is more permissive than AND allowing flexible access levels",
            "Example: add_product OR change_product allows either creator or editor",
        ],
        "validation_details": [
            "Empty permission list raises PermissionDenied with No permissions specified",
            "Unauthenticated users get PermissionDenied with Authentication required",
            "Error message lists all checked permissions for debugging clarity",
            "Permission format follows app_label.codename pattern consistently",
            "Each permission checked individually via request.user.has_perm call",
            "All permission checks leverage the cached permission system from Task 61",
        ],
    }
    logger.debug(
        "any permission required config: decorator_details=%d, or_logic_details=%d",
        len(config["decorator_details"]),
        len(config["or_logic_details"]),
    )
    return config


def get_all_permissions_required_config() -> dict:
    """Return all_permissions_required decorator configuration for AND logic checks.

    SubPhase-05, Group-E, Task 67.
    """
    config: dict = {
        "configured": True,
        "decorator_details": [
            "all_permissions_required function accepts variable *perms arguments",
            "Returns inner decorator function that wraps the view function",
            "Uses functools.wraps to preserve original function metadata",
            "Decorator implements AND logic requiring every permission to match",
            "Docstring explains AND behavior and strict security requirements",
            "Compatible with Django function-based views accepting request as first arg",
        ],
        "and_logic_details": [
            "Uses list comprehension to collect all missing permissions from list",
            "Missing permissions are those where has_perm returns False for user",
            "User must have EVERY listed permission to gain access to the view",
            "Missing even one permission results in PermissionDenied exception",
            "AND logic is more restrictive than OR for strict security needs",
            "Example: change_product AND delete_product requires both abilities",
        ],
        "error_details": [
            "Error message specifically lists which permissions are missing",
            "Missing permissions joined with comma separator for readability",
            "Empty permission list raises PermissionDenied with No permissions specified",
            "Unauthenticated users get PermissionDenied with Authentication required",
            "Specific missing permission info helps administrators debug access issues",
            "Error format is User lacks required permissions colon missing list",
        ],
    }
    logger.debug(
        "all permissions required config: decorator_details=%d, and_logic_details=%d",
        len(config["decorator_details"]),
        len(config["and_logic_details"]),
    )
    return config


def get_is_role_permission_class_config() -> dict:
    """Return IsRolePermission base DRF permission class configuration.

    SubPhase-05, Group-E, Task 68.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "IsRolePermission extends rest_framework.permissions.BasePermission",
            "Constructor accepts permission_codename string parameter for flexibility",
            "Stores permission_codename as instance variable for has_permission checks",
            "Custom message attribute includes the specific permission name in error",
            "Class can be instantiated with any app_label.codename format string",
            "Serves as foundation for permission-based access control in DRF views",
        ],
        "has_permission_details": [
            "has_permission method checks view-level permission on every request",
            "First verifies request.user exists and is_authenticated is True",
            "Then calls request.user.has_perm with stored permission_codename",
            "Returns boolean True only if both authentication and permission pass",
            "Method receives request and view as standard DRF signature arguments",
            "Short-circuit evaluation returns False immediately if not authenticated",
        ],
        "has_object_permission_details": [
            "has_object_permission delegates to has_permission for base behavior",
            "Called by DRF for object-level checks after has_permission succeeds",
            "Receives request, view, and obj parameters per DRF convention",
            "Base implementation does not add object-specific checks by default",
            "Subclasses can override to add tenant-scoped or ownership checks",
            "Returns boolean matching has_permission result for consistent behavior",
        ],
    }
    logger.debug(
        "is role permission class config: class_details=%d, has_permission_details=%d",
        len(config["class_details"]),
        len(config["has_permission_details"]),
    )
    return config


def get_is_super_admin_permission_config() -> dict:
    """Return IsSuperAdmin DRF permission class configuration.

    SubPhase-05, Group-E, Task 69.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "IsSuperAdmin extends rest_framework.permissions.BasePermission",
            "Class-level message attribute set to Only super administrators",
            "Does not require constructor parameters unlike IsRolePermission",
            "Used as permission_classes = [IsSuperAdmin] without instantiation args",
            "Represents highest access level in the permission hierarchy",
            "Checks for super-admin role slug via user.has_role method",
        ],
        "permission_check_details": [
            "has_permission verifies request.user is authenticated first",
            "Then calls request.user.has_role with super-admin slug string",
            "has_role queries UserRole model filtering by user and role slug",
            "Returns True only if user has super-admin role assigned",
            "has_object_permission delegates to has_permission directly",
            "Super admins have full access to all objects across all tenants",
        ],
        "access_scope_details": [
            "Super admins can access all tenants and system-level settings",
            "Super admins can create and delete tenants in the platform",
            "Super admins have unrestricted access to all user management",
            "Super admins bypass tenant-scoping in object permission checks",
            "Access level is above tenant-admin manager and staff roles",
            "Typically reserved for platform operators and system administrators",
        ],
    }
    logger.debug(
        "is super admin permission config: class_details=%d, permission_check_details=%d",
        len(config["class_details"]),
        len(config["permission_check_details"]),
    )
    return config


def get_is_tenant_admin_permission_config() -> dict:
    """Return IsTenantAdmin DRF permission class configuration.

    SubPhase-05, Group-E, Task 70.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "IsTenantAdmin extends rest_framework.permissions.BasePermission",
            "Class-level message attribute set to Only tenant administrators",
            "Does not require constructor parameters for simple usage pattern",
            "Used as permission_classes = [IsTenantAdmin] in DRF views",
            "Represents tenant-level administrative access in the hierarchy",
            "Checks for tenant-admin role slug via user.has_role method",
        ],
        "permission_check_details": [
            "has_permission verifies request.user is authenticated first",
            "Then calls request.user.has_role with tenant-admin slug string",
            "Returns True only if user has tenant-admin role assigned",
            "has_object_permission checks has_permission then validates tenant",
            "Object tenant check uses hasattr to verify obj.tenant attribute",
            "Compares obj.tenant with request.user.tenant for scope validation",
        ],
        "tenant_scope_details": [
            "Tenant admins have full control within their own tenant only",
            "Object-level checks ensure objects belong to admin's tenant",
            "Objects without tenant attribute are accessible by default policy",
            "Tenant admins can manage users and settings within their tenant",
            "Tenant admins cannot access other tenants data or system settings",
            "Access level is below super-admin but above manager and staff",
        ],
    }
    logger.debug(
        "is tenant admin permission config: class_details=%d, permission_check_details=%d",
        len(config["class_details"]),
        len(config["permission_check_details"]),
    )
    return config


def get_is_manager_permission_config() -> dict:
    """Return IsManager DRF permission class configuration.

    SubPhase-05, Group-E, Task 71.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "IsManager extends rest_framework.permissions.BasePermission",
            "Class-level message attribute set to Only managers can perform",
            "Does not require constructor parameters for simple usage pattern",
            "Used as permission_classes = [IsManager] in DRF views",
            "Represents operational management access level in the hierarchy",
            "Checks for manager role slug via user.has_role method",
        ],
        "permission_check_details": [
            "has_permission verifies request.user is authenticated first",
            "Then calls request.user.has_role with manager slug string",
            "Returns True only if user has manager role assigned",
            "has_object_permission checks has_permission then validates tenant",
            "Object tenant check uses hasattr to verify obj.tenant attribute",
            "Compares obj.tenant with request.user.tenant for scope validation",
        ],
        "access_scope_details": [
            "Managers can access operational features and generate reports",
            "Managers can approve orders and manage inventory within tenant",
            "Managers have limited staff management capabilities",
            "Object-level checks ensure objects belong to manager's tenant",
            "Access level is below tenant-admin but above staff members",
            "Managers handle day-to-day business operations and oversight",
        ],
    }
    logger.debug(
        "is manager permission config: class_details=%d, permission_check_details=%d",
        len(config["class_details"]),
        len(config["permission_check_details"]),
    )
    return config


def get_is_staff_permission_config() -> dict:
    """Return IsStaff DRF permission class configuration.

    SubPhase-05, Group-E, Task 72.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "IsStaff extends rest_framework.permissions.BasePermission",
            "Class-level message attribute set to Only staff members can perform",
            "Does not require constructor parameters for simple usage pattern",
            "Used as permission_classes = [IsStaff] in DRF views",
            "Represents basic operational access level in the hierarchy",
            "Checks for staff role slug via user.has_role method",
        ],
        "permission_check_details": [
            "has_permission verifies request.user is authenticated first",
            "Then calls request.user.has_role with staff slug string",
            "Returns True only if user has staff role assigned",
            "has_object_permission checks has_permission then validates tenant",
            "Object tenant check uses hasattr to verify obj.tenant attribute",
            "Compares obj.tenant with request.user.tenant for scope validation",
        ],
        "access_scope_details": [
            "Staff can view and edit products within their assigned tenant",
            "Staff can view and process orders for basic transaction handling",
            "Staff can view and edit customer records within their tenant",
            "Staff have limited report viewing capabilities for basic insight",
            "Staff cannot access system settings or tenant configuration",
            "Access level is the lowest role above unauthenticated users",
        ],
    }
    logger.debug(
        "is staff permission config: class_details=%d, permission_check_details=%d",
        len(config["class_details"]),
        len(config["permission_check_details"]),
    )
    return config


def get_permission_mixin_config() -> dict:
    """Return PermissionMixin configuration for class-based view permission checking.

    SubPhase-05, Group-E, Task 73.
    """
    config: dict = {
        "configured": True,
        "mixin_details": [
            "PermissionMixin inherits from object following Django mixin pattern",
            "Class attribute required_permissions defaults to empty list",
            "Supports single string or list of strings for permission format",
            "Created in backend/apps/core/mixins.py alongside other view mixins",
            "Works with any Django class-based view like ListView or DetailView",
            "Should be placed before the base view class in MRO inheritance order",
        ],
        "dispatch_details": [
            "dispatch method overrides parent to check permissions before processing",
            "Calls check_permissions with request object before super dispatch",
            "Raises PermissionDenied if check_permissions returns False",
            "Error message states You do not have permission to access this resource",
            "Calls super().dispatch(request, *args, **kwargs) to continue chain",
            "MRO ensures all mixins dispatch methods are called in correct order",
        ],
        "check_permissions_details": [
            "check_permissions method receives request and returns boolean result",
            "Returns True immediately if required_permissions is empty list",
            "Normalizes string permission to single-element list for consistency",
            "Uses all() builtin to enforce AND logic requiring every permission",
            "Calls request.user.has_perm for each permission in the list",
            "AND logic means user must have every listed permission to access view",
        ],
    }
    logger.debug(
        "permission mixin config: mixin_details=%d, dispatch_details=%d",
        len(config["mixin_details"]),
        len(config["dispatch_details"]),
    )
    return config


def get_role_mixin_config() -> dict:
    """Return RoleMixin configuration for class-based view role checking.

    SubPhase-05, Group-E, Task 74.
    """
    config: dict = {
        "configured": True,
        "mixin_details": [
            "RoleMixin inherits from object following Django mixin pattern",
            "Class attribute required_roles defaults to empty list",
            "Supports single string or list of strings for role slug format",
            "Created in backend/apps/core/mixins.py alongside PermissionMixin",
            "Works with any Django class-based view like UpdateView or DeleteView",
            "Should be placed before the base view class in MRO inheritance order",
        ],
        "dispatch_details": [
            "dispatch method overrides parent to check roles before processing",
            "Calls check_roles with request object before super dispatch",
            "Raises PermissionDenied if check_roles returns False",
            "Error message states You do not have the required role to access",
            "Calls super().dispatch(request, *args, **kwargs) to continue chain",
            "MRO ensures all mixins dispatch methods are called in correct order",
        ],
        "check_roles_details": [
            "check_roles method receives request and returns boolean result",
            "Returns True immediately if required_roles is empty list",
            "Normalizes string role slug to single-element list for consistency",
            "Uses any() builtin to enforce OR logic requiring at least one role",
            "Calls request.user.has_role for each role slug in the list",
            "OR logic means user needs only one of the listed roles to access view",
        ],
    }
    logger.debug(
        "role mixin config: mixin_details=%d, dispatch_details=%d",
        len(config["mixin_details"]),
        len(config["dispatch_details"]),
    )
    return config


def get_tenant_permission_mixin_config() -> dict:
    """Return TenantPermissionMixin configuration for tenant-scoped access control.

    SubPhase-05, Group-E, Task 75.
    """
    config: dict = {
        "configured": True,
        "mixin_details": [
            "TenantPermissionMixin inherits from object following mixin pattern",
            "Class attribute tenant_required defaults to True for strict enforcement",
            "Created in backend/apps/core/mixins.py alongside other view mixins",
            "Implements get_tenant method to extract tenant from request object",
            "Implements check_tenant_access method to verify user tenant match",
            "Prevents cross-tenant data leaks by enforcing tenant scope on views",
        ],
        "tenant_check_details": [
            "dispatch method checks tenant_required flag before enforcing access",
            "get_tenant uses getattr to safely extract tenant from request",
            "check_tenant_access compares request.user.tenant_id with tenant.id",
            "Returns False if no tenant is set on the request object",
            "Raises PermissionDenied with tenant-specific error message on failure",
            "Works with multi-tenancy middleware that sets tenant on each request",
        ],
        "super_admin_bypass_details": [
            "Super admins bypass tenant check via request.user.has_role super-admin",
            "Bypass allows platform operators to access any tenant for administration",
            "Bypass check runs before tenant comparison for early exit optimization",
            "Regular users without super-admin role must match tenant exactly",
            "tenant_required can be set to False for public views needing no check",
            "Combining with RoleMixin and PermissionMixin gives full access control",
        ],
    }
    logger.debug(
        "tenant permission mixin config: mixin_details=%d, tenant_check_details=%d",
        len(config["mixin_details"]),
        len(config["tenant_check_details"]),
    )
    return config


def get_jwt_role_claims_config() -> dict:
    """Return JWT token claims configuration for roles and permissions.

    SubPhase-05, Group-E, Task 76.
    """
    config: dict = {
        "configured": True,
        "serializer_details": [
            "CustomTokenObtainPairSerializer extends TokenObtainPairSerializer",
            "Overrides get_token classmethod to add custom claims to token",
            "Calls super().get_token(user) to get base token with standard claims",
            "CustomTokenObtainPairView extends TokenObtainPairView with custom serializer",
            "Created in backend/apps/core/jwt_claims.py as dedicated module",
            "TOKEN_OBTAIN_SERIALIZER setting points to custom serializer class",
        ],
        "claims_details": [
            "roles claim contains list of active role slugs from user_roles relation",
            "permissions claim contains list from user.get_all_permissions method",
            "tenant_id claim is integer tenant ID or None if no tenant assigned",
            "tenant_slug claim is string tenant slug or None if no tenant assigned",
            "username and email claims added for user display information",
            "is_superadmin boolean claim added via user.has_role super-admin check",
        ],
        "settings_details": [
            "SIMPLE_JWT config updated with TOKEN_OBTAIN_SERIALIZER path string",
            "ACCESS_TOKEN_LIFETIME set to timedelta hours for token expiration",
            "REFRESH_TOKEN_LIFETIME set to timedelta days for refresh window",
            "ROTATE_REFRESH_TOKENS enabled for automatic refresh token rotation",
            "AUTH_HEADER_TYPES set to Bearer for standard authorization header",
            "URL endpoint configured at auth/token/ for token obtain pair view",
        ],
    }
    logger.debug(
        "jwt role claims config: serializer_details=%d, claims_details=%d",
        len(config["serializer_details"]),
        len(config["claims_details"]),
    )
    return config


def get_permission_denied_response_config() -> dict:
    """Return standardized 403 permission denied response configuration.

    SubPhase-05, Group-E, Task 77.
    """
    config: dict = {
        "configured": True,
        "response_details": [
            "PermissionDeniedError class structures standard 403 error response",
            "permission_denied_response function returns DRF Response with 403 status",
            "Created in backend/apps/core/responses.py as dedicated response module",
            "Response includes error code permission_denied as string identifier",
            "Response includes human-readable message for user-facing display",
            "Response includes details dict with required and missing permissions",
        ],
        "error_format_details": [
            "Error format wraps all fields under top-level error key in JSON",
            "details object contains required_permission and missing_permissions lists",
            "details object contains required_role and user_roles when role check fails",
            "timestamp field uses ISO 8601 format with UTC timezone indicator Z",
            "path field captures request.path for the denied endpoint URL",
            "method field captures request.method as GET POST PUT DELETE string",
        ],
        "logging_details": [
            "logger.warning called for every permission denial with user context",
            "Log extra includes username or anonymous for unauthenticated users",
            "Log extra includes required_permission or required_role that was checked",
            "Log extra includes request path and HTTP method for audit trail",
            "format_missing_permissions helper calculates set difference of permissions",
            "format_missing_roles helper calculates set difference of role slugs",
        ],
    }
    logger.debug(
        "permission denied response config: response_details=%d, error_format_details=%d",
        len(config["response_details"]),
        len(config["error_format_details"]),
    )
    return config


def get_decorators_mixins_docs_config() -> dict:
    """Return documentation configuration for all decorators and mixins.

    SubPhase-05, Group-E, Task 78.
    """
    config: dict = {
        "configured": True,
        "documentation_details": [
            "Documentation created in backend/docs/permissions/ directory",
            "README.md serves as main index linking all permission documentation",
            "decorators.md documents permission_required and role_required with examples",
            "permission_classes.md documents IsSuperAdmin through IsStaff classes",
            "mixins.md documents PermissionMixin RoleMixin TenantPermissionMixin",
            "quick_reference.md provides summary tables for all components",
        ],
        "structure_details": [
            "jwt_claims.md documents token payload structure and client usage",
            "error_responses.md documents standard 403 response format and fields",
            "examples subdirectory contains function_based_views.md and viewsets.md",
            "examples subdirectory contains class_based_views.md and frontend_integration.md",
            "Each documentation file includes overview API reference and examples",
            "Cross-references link related documentation files for navigation",
        ],
        "reference_details": [
            "Quick reference includes decorator table with signature and purpose",
            "Quick reference includes DRF permission class table with role checks",
            "Quick reference includes mixin table with dispatch behavior details",
            "Quick reference includes JWT claims table with type and example values",
            "Quick reference includes error codes table with status and meaning",
            "Troubleshooting section covers common issues and debugging steps",
        ],
    }
    logger.debug(
        "decorators mixins docs config: documentation_details=%d, structure_details=%d",
        len(config["documentation_details"]),
        len(config["structure_details"]),
    )
    return config


def get_role_serializers_config() -> dict:
    """Return role serializer classes configuration for DRF API views.

    SubPhase-05, Group-F, Task 79.
    """
    config: dict = {
        "configured": True,
        "serializer_details": [
            "RoleSerializer extends ModelSerializer for basic role list views",
            "Fields include id name slug description hierarchy_level is_system_role",
            "created_at and updated_at included as read_only timestamp fields",
            "RoleSerializer used as nested serializer in RoleDetailSerializer parent",
            "Meta class sets read_only_fields for id created_at and updated_at",
            "Created in backend/apps/users/serializers/role_serializers.py file",
        ],
        "detail_serializer_details": [
            "RoleDetailSerializer extends ModelSerializer for single role detail views",
            "permissions field uses nested PermissionSerializer with many=True read_only",
            "parent field uses nested RoleSerializer with read_only=True for hierarchy",
            "permission_count SerializerMethodField counts obj.permissions.count()",
            "user_count SerializerMethodField counts obj.userrole_set.count()",
            "parent_id writable field allows setting parent role in create or update",
        ],
        "assignment_serializer_details": [
            "AssignRoleSerializer extends Serializer with user_id and role_id fields",
            "validate_user_id checks user exists and belongs to request.user.tenant",
            "validate_role_id checks role exists and belongs to request.user.tenant",
            "validate method checks assigner hierarchy level vs role being assigned",
            "create method creates UserRole instance with assigned_by from request.user",
            "RevokeRoleSerializer validates user_id and role_id for role removal",
        ],
    }
    logger.debug(
        "role serializers config: serializer_details=%d, detail_serializer_details=%d",
        len(config["serializer_details"]),
        len(config["detail_serializer_details"]),
    )
    return config


def get_permission_serializers_config() -> dict:
    """Return permission serializer classes configuration for DRF API views.

    SubPhase-05, Group-F, Task 80.
    """
    config: dict = {
        "configured": True,
        "serializer_details": [
            "PermissionSerializer extends ModelSerializer for permission list views",
            "Fields include id name codename description module and action",
            "Used as nested serializer in RoleDetailSerializer permissions field",
            "Meta class sets read_only_fields for id field as primary key",
            "Defined before RoleDetailSerializer to avoid circular import issues",
            "Created in backend/apps/users/serializers/role_serializers.py file",
        ],
        "detail_serializer_details": [
            "PermissionDetailSerializer extends ModelSerializer for detail views",
            "roles field uses nested RoleSerializer with many=True read_only",
            "role_count SerializerMethodField counts obj.roles.count()",
            "user_count SerializerMethodField counts distinct users through UserRole",
            "created_at and updated_at included as read_only timestamp fields",
            "get_user_count filters UserRole by role__permissions for distinct count",
        ],
        "bulk_serializer_details": [
            "PermissionBulkSerializer extends Serializer for bulk permission operations",
            "permission_codenames ListField of CharField validates all codenames exist",
            "validate_permission_codenames checks each codename against tenant permissions",
            "get_permission_ids returns list of IDs for validated codenames",
            "PermissionGroupSerializer groups permissions by module using groupby",
            "get_grouped_permissions static method orders by module then action field",
        ],
    }
    logger.debug(
        "permission serializers config: serializer_details=%d, detail_serializer_details=%d",
        len(config["serializer_details"]),
        len(config["detail_serializer_details"]),
    )
    return config


def get_role_list_view_config() -> dict:
    """Return RoleListView configuration for listing tenant roles via API.

    SubPhase-05, Group-F, Task 81.
    """
    config: dict = {
        "configured": True,
        "view_details": [
            "RoleListView extends generics.ListAPIView for paginated role listing",
            "serializer_class set to RoleSerializer for basic role data output",
            "permission_classes set to IsAuthenticated for authenticated users",
            "Created in backend/apps/users/views/role_views.py module file",
            "Endpoint mapped to GET /api/v1/roles/ in URL configuration",
            "Supports pagination with page and page_size query parameters",
        ],
        "queryset_details": [
            "get_queryset filters Role objects by request.user.tenant for isolation",
            "Queryset ordered by hierarchy_level ascending then name ascending",
            "Only active roles included in the listing by default filter",
            "Uses Q objects for search across name and description fields",
            "Supports chaining multiple filter parameters in single request",
            "Returns empty queryset if user has no tenant assigned to account",
        ],
        "filter_details": [
            "hierarchy_level query parameter filters roles by exact hierarchy level",
            "is_system query parameter filters by is_system_role boolean field",
            "search query parameter filters name__icontains or description__icontains",
            "All filter parameters are optional and can be combined together",
            "Invalid filter values are silently ignored returning unfiltered results",
            "Docstring documents all available query parameters with usage examples",
        ],
    }
    logger.debug(
        "role list view config: view_details=%d, queryset_details=%d",
        len(config["view_details"]),
        len(config["queryset_details"]),
    )
    return config


def get_role_detail_view_config() -> dict:
    """Return RoleDetailView configuration for retrieving role details via API.

    SubPhase-05, Group-F, Task 82.
    """
    config: dict = {
        "configured": True,
        "view_details": [
            "RoleDetailView extends generics.RetrieveAPIView for single role detail",
            "serializer_class set to RoleDetailSerializer for full role data output",
            "permission_classes set to IsAuthenticated for authenticated users",
            "lookup_field set to pk for standard primary key URL parameter",
            "Endpoint mapped to GET /api/v1/roles/{id}/ in URL configuration",
            "Returns complete role information including permissions and parent role",
        ],
        "queryset_details": [
            "get_queryset filters Role objects by request.user.tenant for isolation",
            "prefetch_related permissions loads permission objects efficiently",
            "select_related parent loads parent role in single database query",
            "get_object verifies role belongs to user tenant or raises Http404",
            "Optimized queries reduce database round trips for detail views",
            "Returns 404 Not Found if role does not exist in user tenant scope",
        ],
        "security_details": [
            "Tenant isolation enforced at queryset level filtering by tenant",
            "get_object double-checks tenant ownership before returning role object",
            "System roles marked with is_system_role flag in response data",
            "Permission visibility limited to permissions within same tenant",
            "Parent role information only included if parent exists in same tenant",
            "No write operations allowed through this read-only retrieve view",
        ],
    }
    logger.debug(
        "role detail view config: view_details=%d, queryset_details=%d",
        len(config["view_details"]),
        len(config["queryset_details"]),
    )
    return config


def get_role_create_view_config() -> dict:
    """Return RoleCreateView configuration for creating custom roles via API.

    SubPhase-05, Group-F, Task 83.
    """
    config: dict = {
        "configured": True,
        "view_details": [
            "RoleCreateView extends generics.CreateAPIView for role creation",
            "serializer_class set to RoleSerializer for input validation",
            "permission_classes set to IsAuthenticated and IsTenantAdmin",
            "Only tenant administrators can create new custom roles via API",
            "Endpoint mapped to POST /api/v1/roles/ in URL configuration",
            "Returns 201 Created with new role data on successful creation",
        ],
        "perform_create_details": [
            "perform_create auto-assigns request.user.tenant to new role",
            "is_system_role forced to False to prevent system role creation",
            "created_by field set to request.user for audit trail tracking",
            "slug auto-generated from role name using slugify utility function",
            "Permission IDs from request data assigned via role.permissions.set",
            "Only permissions belonging to same tenant are assignable to role",
        ],
        "validation_details": [
            "Role name must be unique within tenant scope to prevent duplicates",
            "hierarchy_level validated to be between 1 and 100 inclusive range",
            "Parent role must exist in same tenant if parent field is provided",
            "Parent hierarchy_level must be less than current role level value",
            "is_system_role True in request body raises ValidationError exception",
            "Returns 400 Bad Request with specific error messages on failure",
        ],
    }
    logger.debug(
        "role create view config: view_details=%d, perform_create_details=%d",
        len(config["view_details"]),
        len(config["perform_create_details"]),
    )
    return config


def get_assign_role_view_config() -> dict:
    """Return AssignRoleView configuration for assigning roles to users.

    SubPhase-05, Group-F, Task 84.
    """
    config: dict = {
        "configured": True,
        "view_details": [
            "AssignRoleView extends APIView for custom role assignment logic",
            "Uses POST method accepting user_id role_id and is_primary fields",
            "permission_classes set to IsAuthenticated and IsTenantAdmin",
            "AssignRoleSerializer validates input data before processing",
            "Endpoint mapped to POST /api/v1/roles/assign/ in URL configuration",
            "Returns 201 Created for new assignment or 200 OK for existing update",
        ],
        "hierarchy_details": [
            "Hierarchy validation prevents assigning roles above assigner level",
            "Lower hierarchy_level number means higher privilege in the system",
            "Current user max hierarchy retrieved via aggregate Max query",
            "Role hierarchy_level compared against user max level for validation",
            "Tenant admins can assign any role regardless of hierarchy level",
            "Superusers bypass all hierarchy validation checks completely",
        ],
        "primary_role_details": [
            "is_primary=True in request sets new role as user primary role",
            "Existing primary roles unset via bulk update is_primary=False",
            "User can have only one primary role per tenant at any time",
            "get_or_create handles duplicate assignment gracefully with update",
            "Permission cache cleared via delattr _cached_permissions after change",
            "Response includes user_role details with id user role and assigned_at",
        ],
    }
    logger.debug(
        "assign role view config: view_details=%d, hierarchy_details=%d",
        len(config["view_details"]),
        len(config["hierarchy_details"]),
    )
    return config


def get_revoke_role_view_config() -> dict:
    """Return RevokeRoleView configuration for removing role assignments.

    SubPhase-05, Group-F, Task 85.
    """
    config: dict = {
        "configured": True,
        "view_details": [
            "RevokeRoleView extends APIView for custom role revocation logic",
            "Uses POST method accepting user_id and role_id fields in body",
            "permission_classes set to IsAuthenticated and IsTenantAdmin",
            "RevokeRoleSerializer validates input data before processing",
            "Endpoint mapped to POST /api/v1/roles/revoke/ in URL configuration",
            "Returns 200 OK on successful revocation with descriptive message",
        ],
        "protection_details": [
            "Prevents removing user only role returning 400 Bad Request error",
            "Validates user exists in same tenant or returns 404 Not Found",
            "Validates role assignment exists or returns 404 Not Found error",
            "User role count checked before deletion to enforce minimum one role",
            "Permission cache cleared via delattr _cached_permissions after change",
            "System role assignments may have additional protection in future",
        ],
        "promotion_details": [
            "Primary role removal triggers automatic promotion of next highest",
            "Next primary selected by lowest hierarchy_level which is highest rank",
            "UserRole.objects.filter by user and tenant ordered by hierarchy_level",
            "First result from ordered queryset becomes new primary role",
            "new_primary_role name included in response if promotion occurred",
            "No promotion needed if removed role was not the primary role",
        ],
    }
    logger.debug(
        "revoke role view config: view_details=%d, protection_details=%d",
        len(config["view_details"]),
        len(config["protection_details"]),
    )
    return config


def get_my_permissions_view_config() -> dict:
    """Return MyPermissionsView configuration for current user permissions.

    SubPhase-05, Group-F, Task 86.
    """
    config: dict = {
        "configured": True,
        "view_details": [
            "MyPermissionsView extends APIView for user permission retrieval",
            "Uses GET method returning current user roles and permissions",
            "permission_classes set to IsAuthenticated for any authenticated user",
            "No IsTenantAdmin required since users view their own permissions",
            "Endpoint mapped to GET /api/v1/me/permissions/ in URL configuration",
            "Response is frontend-friendly format for client-side permission checks",
        ],
        "response_details": [
            "user object includes id email full_name is_tenant_admin is_superuser",
            "primary_role object includes id name and hierarchy_level fields",
            "roles list includes all user roles with is_primary and hierarchy_level",
            "permissions sorted list of all effective permission codenames",
            "permission_details includes codename name source_role and source_level",
            "metadata includes total_roles total_permissions and highest_hierarchy_level",
        ],
        "optimization_details": [
            "UserRole queried with select_related role for single join query",
            "prefetch_related role__permissions loads permissions without N+1",
            "Permission codenames collected in set for automatic deduplication",
            "min of hierarchy_levels calculates highest privilege level for user",
            "has_role tenant_admin checked for is_tenant_admin flag in response",
            "Response caching at 5 minutes considered for performance improvement",
        ],
    }
    logger.debug(
        "my permissions view config: view_details=%d, response_details=%d",
        len(config["view_details"]),
        len(config["response_details"]),
    )
    return config


def get_role_urls_config() -> dict:
    """Return URL routing configuration for role management API endpoints.

    SubPhase-05, Group-F, Task 87.
    """
    config: dict = {
        "configured": True,
        "url_details": [
            "URLs defined in backend/apps/users/urls.py with app_name users",
            "path roles/ maps to RoleListView for GET listing all tenant roles",
            "path roles/<int:pk>/ maps to RoleDetailView for GET role details",
            "path roles/assign/ maps to AssignRoleView for POST role assignment",
            "path roles/revoke/ maps to RevokeRoleView for POST role revocation",
            "path me/permissions/ maps to MyPermissionsView for GET user permissions",
        ],
        "endpoint_details": [
            "GET /api/v1/roles/ returns paginated list of tenant roles",
            "POST /api/v1/roles/ creates new custom role via RoleCreateView",
            "GET /api/v1/roles/<id>/ returns role details with permissions",
            "POST /api/v1/roles/assign/ assigns role to user in same tenant",
            "POST /api/v1/roles/revoke/ removes role assignment from user",
            "GET /api/v1/me/permissions/ returns current user roles and permissions",
        ],
        "namespace_details": [
            "app_name set to users for URL namespacing in reverse lookups",
            "URL pattern names follow kebab-case convention like role-list",
            "role-list name used for reverse lookup of roles listing endpoint",
            "role-detail name used for reverse lookup of role detail endpoint",
            "role-assign and role-revoke names for action endpoint lookups",
            "my-permissions name used for reverse lookup of user permissions",
        ],
    }
    logger.debug(
        "role urls config: url_details=%d, endpoint_details=%d",
        len(config["url_details"]),
        len(config["endpoint_details"]),
    )
    return config


def get_role_admin_config() -> dict:
    """Return Django admin configuration for role and permission models.

    SubPhase-05, Group-F, Task 88.
    """
    config: dict = {
        "configured": True,
        "admin_details": [
            "RoleAdmin registers Role model with list_display name slug hierarchy_level",
            "PermissionAdmin registers Permission with list_display name codename type",
            "UserRoleAdmin registers UserRole with list_display user role is_primary",
            "RolePermissionAdmin registers simple admin with list_display role permission",
            "All admin classes include search_fields for name and related field lookups",
            "All admin classes include list_filter for tenant and boolean field filtering",
        ],
        "inline_details": [
            "RolePermissionInline is TabularInline showing permissions inside RoleAdmin",
            "RolePermissionInline fields include permission and granted_at readonly",
            "RolePermissionInline extra set to 1 for one empty row to add permissions",
            "UserRoleInline is TabularInline showing user assignments inside RoleAdmin",
            "UserRoleInline fields include user is_primary and assigned_at readonly",
            "UserRoleInline extra set to 0 for no empty rows by default in listing",
        ],
        "protection_details": [
            "has_delete_permission returns False if obj.is_system_role is True",
            "get_readonly_fields adds name slug hierarchy_level for system roles",
            "save_model validates hierarchy_level between 1 and 100 range inclusive",
            "get_queryset filters by request user tenant for multi-tenancy isolation",
            "autocomplete_fields used for permission and user ForeignKey fields",
            "readonly_fields include slug created_at updated_at for all role admins",
        ],
    }
    logger.debug(
        "role admin config: admin_details=%d, inline_details=%d",
        len(config["admin_details"]),
        len(config["inline_details"]),
    )
    return config


def get_role_model_tests_config() -> dict:
    """Return configuration for Role model unit tests.

    SubPhase-05, Group-F, Task 89.
    """
    config: dict = {
        "configured": True,
        "test_details": [
            "RoleModelTests class uses TestCase with setUp creating tenant and users",
            "test_role_creation verifies name slug description and hierarchy_level fields",
            "test_role_unique_slug_per_tenant raises IntegrityError on duplicate slug",
            "test_slug_auto_generation creates role from name and checks slug value",
            "test_role_hierarchy_levels compares admin 90 and manager 70 hierarchy ordering",
            "test_role_parent_child verifies parent-child relationship and children queryset",
        ],
        "coverage_details": [
            "test_system_role_cannot_be_deleted raises ValidationError on delete call",
            "test_system_role_cannot_be_modified raises ValidationError on slug change save",
            "test_role_str_method checks __str__ returns role name string representation",
            "test_role_permissions_count creates 3 permissions and asserts count equals 3",
            "test_role_default_ordering verifies ordering by hierarchy_level descending",
            "All tests target greater than 90 percent coverage for Role model class",
        ],
        "validation_details": [
            "setUp creates test tenant via Tenant.objects.create with name and slug",
            "setUp creates test users via User.objects.create_user with tenant and email",
            "Uniqueness tested with duplicate slug in same tenant raising IntegrityError",
            "Hierarchy tested by comparing hierarchy_level integers between two roles",
            "System role protection tested by setting is_system_role True then delete",
            "Parent child tested by setting parent FK and querying children reverse relation",
        ],
    }
    logger.debug(
        "role model tests config: test_details=%d, coverage_details=%d",
        len(config["test_details"]),
        len(config["coverage_details"]),
    )
    return config


def get_permission_tests_config() -> dict:
    """Return configuration for Permission model and assignment tests.

    SubPhase-05, Group-F, Task 90.
    """
    config: dict = {
        "configured": True,
        "test_details": [
            "PermissionModelTests uses TestCase with setUp and tearDown clearing cache",
            "test_permission_creation verifies codename and name fields after create",
            "test_permission_unique_codename_per_tenant raises IntegrityError on duplicate",
            "test_assign_permission_to_role adds permission and checks role.permissions.all",
            "test_assign_multiple_permissions creates 5 permissions and asserts count is 5",
            "test_user_has_permission assigns role with permission and checks has_perm True",
        ],
        "caching_details": [
            "test_user_does_not_have_permission checks has_perm returns False for missing",
            "test_permission_inheritance_from_parent_role verifies child inherits parent perms",
            "test_user_get_all_permissions checks get_all_permissions returns 3 codenames",
            "test_permission_caching verifies cache key is set after first get_all_permissions",
            "test_permission_cache_invalidation checks cache cleared after role.permissions.add",
            "tearDown calls cache.clear to ensure clean state between all test methods",
        ],
        "inheritance_details": [
            "test_user_with_multiple_roles creates 2 roles and asserts combined permissions",
            "test_permission_with_content_type links permission to ContentType and validates",
            "Parent role at hierarchy 80 with child at 60 tested for permission inheritance",
            "User assigned child role should inherit parent role permissions automatically",
            "Multiple roles scenario verifies has_perm True for both perm_1 and perm_2",
            "Content type test uses ContentType.objects.get with app_label users model user",
        ],
    }
    logger.debug(
        "permission tests config: test_details=%d, caching_details=%d",
        len(config["test_details"]),
        len(config["caching_details"]),
    )
    return config


def get_decorator_tests_config() -> dict:
    """Return configuration for permission decorator and DRF permission tests.

    SubPhase-05, Group-F, Task 91.
    """
    config: dict = {
        "configured": True,
        "decorator_details": [
            "PermissionDecoratorTests uses TestCase with RequestFactory for view testing",
            "test_permission_required_with_permission verifies 200 status for allowed user",
            "test_permission_required_without_permission verifies 403 status for denied user",
            "test_permission_required_anonymous_user verifies 302 redirect to login page",
            "test_role_required_with_role verifies 200 status for user with editor role",
            "test_role_required_without_role verifies 403 status for user without role",
        ],
        "drf_details": [
            "DRFPermissionTests uses APITestCase with APIClient for REST framework testing",
            "test_has_permission_class_with_permission verifies access with view_data perm",
            "test_has_permission_class_without_permission verifies 403 without permission",
            "test_has_role_class_with_role verifies HasRole allows user with editor role",
            "test_is_tenant_admin_class verifies IsTenantAdmin allows tenant admin user",
            "test_is_tenant_admin_class_denies_non_admin verifies 403 for non-admin user",
        ],
        "endpoint_details": [
            "test_tenant_admin_required_as_admin sets is_tenant_admin True and checks 200",
            "test_tenant_admin_required_not_admin checks 403 for regular non-admin user",
            "test_role_list_view_requires_admin verifies 403 then 200 after admin grant",
            "test_my_permissions_view_requires_authentication checks 401 then 200 after auth",
            "test_multiple_permissions_required checks 403 with partial then success with all",
            "All tests use force_authenticate or request.user assignment for auth setup",
        ],
    }
    logger.debug(
        "decorator tests config: decorator_details=%d, drf_details=%d",
        len(config["decorator_details"]),
        len(config["drf_details"]),
    )
    return config


def get_role_system_docs_config() -> dict:
    """Return configuration for complete RBAC system documentation.

    SubPhase-05, Group-F, Task 92.
    """
    config: dict = {
        "configured": True,
        "documentation_details": [
            "RBAC_OVERVIEW.md covers architecture with Role Permission UserRole components",
            "MODELS.md documents all model fields including tenant name slug hierarchy_level",
            "API_REFERENCE.md documents all endpoints with GET POST response examples",
            "README.md in docs/rbac indexes all documentation files with descriptions",
            "Documentation directory structure created at backend/docs/rbac with 8 files",
            "All documentation follows markdown format with tables and code block examples",
        ],
        "guide_details": [
            "USAGE_GUIDE.md provides practical role creation and permission assignment code",
            "DECORATORS.md documents permission_required role_required and DRF classes",
            "TESTING.md includes test setup examples and strategies for RBAC testing",
            "BEST_PRACTICES.md covers do and don't patterns for role and permission design",
            "MIGRATION_GUIDE.md documents migration from Django Groups to custom RBAC",
            "All guides include Python code examples with import statements and usage",
        ],
        "reference_details": [
            "Role model documented with fields name slug description hierarchy_level parent",
            "Permission model documented with fields codename name content_type tenant",
            "UserRole through table documented with fields user role is_primary assigned_at",
            "API endpoints documented with URL methods permissions and response schemas",
            "Security checklist includes tenant filtering hierarchy validation audit logging",
            "Performance section covers select_related prefetch_related and cache strategies",
        ],
    }
    logger.debug(
        "role system docs config: documentation_details=%d, guide_details=%d",
        len(config["documentation_details"]),
        len(config["guide_details"]),
    )
    return config
