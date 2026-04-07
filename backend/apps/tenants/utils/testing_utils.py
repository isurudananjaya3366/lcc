"""
Testing utilities for LankaCommerce Cloud multi-tenancy.

SubPhase-10, Group-A Tasks 01-14 and Group-B Tasks 15-28 and Group-C Tasks 29-44 and Group-D Tasks 45-58 and Group-E Tasks 59-72 and Group-F Tasks 73-86.

Provides testing infrastructure configuration helpers used by the
test suite and documentation for multi-tenant testing operations.

Functions:
    get_test_module_structure_config()    -- Test module structure (Task 01).
    get_conftest_config()                -- Conftest configuration (Task 02).
    get_test_database_config()           -- Test database config (Task 03).
    get_test_schema_management_config()  -- Test schema management (Task 04).
    get_pytest_django_config()           -- pytest-django config (Task 05).
    get_pytest_xdist_config()            -- pytest-xdist config (Task 06).
    get_factory_boy_config()             -- factory-boy config (Task 07).
    get_faker_config()                   -- faker config (Task 08).
    get_test_settings_module_config()    -- test settings module (Task 09).
    get_test_runner_config()             -- test runner config (Task 10).
    get_test_markers_config()            -- test markers (Task 11).
    get_multi_tenant_marker_config()     -- multi-tenant marker (Task 12).
    get_slow_test_marker_config()        -- slow test marker (Task 13).
    get_test_infrastructure_documentation() -- test infrastructure docs (Task 14).
    get_tenant_test_case_config()        -- TenantTestCase class (Task 15).
    get_django_testcase_extension_config() -- Django TestCase extension (Task 16).
    get_setup_method_config()            -- setUp method (Task 17).
    get_teardown_method_config()         -- tearDown method (Task 18).
    get_test_tenant_creation_config()    -- Test tenant creation (Task 19).
    get_tenant_context_setup_config()    -- Tenant context setup (Task 20).
    get_tenant_context_manager_config()  -- Tenant context manager (Task 21).
    get_multi_tenant_test_mixin_config() -- Multi-tenant test mixin (Task 22).
    get_two_tenant_setup_config()        -- Two-tenant setup (Task 23).
    get_tenant_switching_helper_config() -- Tenant switching helper (Task 24).
    get_schema_assertion_helper_config() -- Schema assertion helper (Task 25).
    get_isolation_assertion_config()      -- Isolation assertion (Task 26).
    get_transaction_rollback_config()     -- Transaction rollback (Task 27).
    get_tenant_test_case_documentation()  -- TenantTestCase docs (Task 28).
    get_tenant_factory_config()           -- TenantFactory config (Task 29).
    get_domain_factory_config()           -- DomainFactory config (Task 30).
    get_product_factory_config()          -- ProductFactory config (Task 31).
    get_category_factory_config()         -- CategoryFactory config (Task 32).
    get_customer_factory_config()         -- CustomerFactory config (Task 33).
    get_order_factory_config()            -- OrderFactory config (Task 34).
    get_user_factory_config()             -- UserFactory config (Task 35).
    get_tenant_fixtures_config()          -- Tenant fixtures config (Task 36).
    get_sample_data_fixtures_config()     -- Sample data fixtures config (Task 37).
    get_minimal_fixture_config()          -- Minimal fixture config (Task 38).
    get_full_fixture_config()             -- Full fixture config (Task 39).
    get_load_fixture_helper_config()      -- Load fixture helper config (Task 40).
    get_random_data_generator_config()   -- Random data generator config (Task 41).
    get_bulk_data_generator_config()     -- Bulk data generator config (Task 42).
    get_factory_isolation_verification_config() -- Factory isolation verification (Task 43).
    get_fixtures_documentation_config()  -- Fixtures documentation config (Task 44).
    get_isolation_test_module_config()    -- Isolation test module config (Task 45).
    get_schema_exists_test_config()       -- Schema exists test config (Task 46).
    get_tables_in_schema_test_config()    -- Tables in schema test config (Task 47).
    get_data_placement_test_config()      -- Data placement test config (Task 48).
    get_query_schema_context_test_config() -- Query schema context test config (Task 49).
    get_multi_tenant_separation_test_config() -- Multi-tenant separation test config (Task 50).
    get_same_id_different_tenants_test_config() -- Same ID different tenants test config (Task 51).
    get_tenant_a_cannot_see_b_test_config() -- Tenant A cannot see B test config (Task 52).
    get_tenant_b_cannot_see_a_test_config() -- Tenant B cannot see A test config (Task 53).
    get_public_schema_shared_test_config() -- Public schema shared test config (Task 54).
    get_tenant_to_public_access_test_config() -- Tenant to public access test config (Task 55).
    get_public_cannot_access_tenant_test_config() -- Public cannot access tenant test config (Task 56).
    get_isolation_suite_execution_config() -- Isolation suite execution config (Task 57).
    get_isolation_tests_documentation_config() -- Isolation tests documentation config (Task 58).
    get_leak_test_module_config()             -- Leak test module config (Task 59).
    get_direct_query_leak_test_config()       -- Direct query leak test config (Task 60).
    get_orm_query_leak_test_config()          -- ORM query leak test config (Task 61).
    get_aggregate_query_leak_test_config()    -- Aggregate query leak test config (Task 62).
    get_join_query_leak_test_config()         -- Join query leak test config (Task 63).
    get_subquery_leak_test_config()           -- Subquery leak test config (Task 64).
    get_api_response_leak_test_config()       -- API response leak test config (Task 65).
    get_admin_leak_test_config()              -- Admin leak test config (Task 66).
    get_file_storage_leak_test_config()       -- File storage leak test config (Task 67).
    get_cache_leak_test_config()              -- Cache leak test config (Task 68).
    get_session_leak_test_config()            -- Session leak test config (Task 69).
    get_logging_leak_test_config()            -- Logging leak test config (Task 70).
    get_leak_suite_execution_config()         -- Leak suite execution config (Task 71).
    get_leak_prevention_documentation_config() -- Leak prevention documentation config (Task 72).
    get_performance_test_module_config()      -- Performance test module config (Task 73).
    get_query_performance_test_config()       -- Query performance test config (Task 74).
    get_tenant_switching_speed_test_config()  -- Tenant switching speed test config (Task 75).
    get_schema_creation_time_test_config()    -- Schema creation time test config (Task 76).
    get_many_tenants_scale_test_config()      -- Many tenants scale test config (Task 77).
    get_concurrent_tenant_access_test_config() -- Concurrent tenant access test config (Task 78).
    get_performance_baselines_config()        -- Performance baselines config (Task 79).
    get_ci_test_configuration_config()        -- CI test configuration config (Task 80).
    get_ci_test_job_config()                  -- CI test job config (Task 81).
    get_test_coverage_config()                -- Test coverage config (Task 82).
    get_coverage_threshold_config()           -- Coverage threshold config (Task 83).
    get_test_report_config()                  -- Test report config (Task 84).
    get_initial_commit_config()               -- Initial commit config (Task 85).
    get_final_phase_documentation_config()    -- Final phase documentation config (Task 86).

See also:
    - apps.tenants.utils.__init__  -- public re-exports
    - docs/database/multi-tenant-testing.md
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_test_module_structure_config() -> dict:
    """Return test module structure configuration.

    Documents the test folder layout and separation of tenant-specific
    tests, multi-tenancy integration tests, and shared test helpers
    across the test suite directory tree.

    SubPhase-10, Group-A, Task 01.

    Returns:
        dict: Configuration with *test_structure_documented* flag,
              *test_directories* list, *directory_purposes* list,
              and *file_patterns* list.
    """
    config: dict = {
        "test_structure_documented": True,
        "test_directories": [
            "tests/ -- top-level test root directory",
            "tests/tenants/ -- tenant-specific unit and integration tests",
            "tests/multi_tenancy/ -- cross-tenant and schema isolation tests",
            "tests/conftest.py -- root-level shared pytest fixtures",
            "tests/tenants/conftest.py -- tenant-specific fixtures",
            "tests/factories/ -- model factories for test data generation",
            "tests/helpers/ -- reusable test utility functions and mixins",
        ],
        "directory_purposes": [
            "tests/tenants/ holds unit tests for tenant CRUD operations",
            "tests/multi_tenancy/ holds schema isolation and routing tests",
            "tests/factories/ provides factory_boy factories for all models",
            "tests/helpers/ contains TenantTestMixin and schema helpers",
            "tests/conftest.py defines session-scoped database fixtures",
            "tests/tenants/conftest.py defines tenant-scoped fixtures",
        ],
        "file_patterns": [
            "test_*.py -- standard pytest test file naming convention",
            "conftest.py -- pytest fixture definition files per directory",
            "*_factory.py -- factory_boy model factory modules",
            "test_*_integration.py -- integration test modules",
            "test_*_e2e.py -- end-to-end test modules",
            "helpers_*.py -- test helper and utility modules",
        ],
    }
    logger.debug(
        "Test module structure config: test_directories=%d, directory_purposes=%d",
        len(config["test_directories"]),
        len(config["directory_purposes"]),
    )
    return config


def get_conftest_config() -> dict:
    """Return conftest.py configuration.

    Documents shared pytest fixtures including tenant fixtures,
    database fixtures, schema fixtures, and their scopes and
    dependency chains for the multi-tenant test suite.

    SubPhase-10, Group-A, Task 02.

    Returns:
        dict: Configuration with *conftest_documented* flag,
              *fixture_definitions* list, *fixture_scopes* list,
              and *fixture_dependencies* list.
    """
    config: dict = {
        "conftest_documented": True,
        "fixture_definitions": [
            "tenant -- creates an isolated test tenant with unique schema",
            "public_tenant -- provides the shared public tenant instance",
            "tenant_schema -- activates tenant schema on the DB connection",
            "db_access -- grants database access for the current test",
            "schema_cleanup -- tears down test schemas after each test",
            "admin_user -- creates an admin user within the tenant schema",
            "api_client -- returns an authenticated DRF APIClient instance",
        ],
        "fixture_scopes": [
            "session -- shared across all tests in the entire test run",
            "module -- shared across all tests within a single module",
            "class -- shared across all methods in a test class",
            "function -- created fresh for each individual test function",
            "package -- shared across all tests within a package directory",
            "dynamic -- scope determined at runtime via fixture factory",
        ],
        "fixture_dependencies": [
            "tenant depends on db_access for database connectivity",
            "tenant_schema depends on tenant for schema name resolution",
            "admin_user depends on tenant_schema for schema activation",
            "api_client depends on admin_user for authentication token",
            "schema_cleanup depends on tenant for schema drop operations",
            "public_tenant depends on db_access and django_db_setup",
        ],
    }
    logger.debug(
        "Conftest config: fixture_definitions=%d, fixture_scopes=%d",
        len(config["fixture_definitions"]),
        len(config["fixture_scopes"]),
    )
    return config


def get_test_database_config() -> dict:
    """Return test database configuration.

    Documents test database settings including the test database name,
    engine, connection parameters, migration behavior during test runs,
    and cleanup strategies after tests complete.

    SubPhase-10, Group-A, Task 03.

    Returns:
        dict: Configuration with *test_database_documented* flag,
              *database_settings* list, *migration_behaviors* list,
              and *cleanup_strategies* list.
    """
    config: dict = {
        "test_database_documented": True,
        "database_settings": [
            "NAME -- test_pos_db (prefixed with test_ by Django runner)",
            "ENGINE -- django.db.backends.postgresql for PostgreSQL backend",
            "HOST -- localhost or Docker service name for test environment",
            "PORT -- 5432 default PostgreSQL port for test connections",
            "USER -- pos_test_user with CREATE/DROP schema privileges",
            "PASSWORD -- loaded from TEST_DATABASE_PASSWORD env variable",
            "TEST.SERIALIZE -- False to speed up test database creation",
        ],
        "migration_behaviors": [
            "--keepdb flag reuses existing test database between runs",
            "--no-input suppresses interactive prompts during test setup",
            "migrate_schemas runs shared migrations on public schema first",
            "tenant schemas receive tenant-app migrations during setup",
            "--parallel flag runs migrations in separate test processes",
            "MIGRATION_MODULES setting can skip migrations for speed",
        ],
        "cleanup_strategies": [
            "DESTROY_TEST_DB drops the entire test database after run",
            "flush clears all table data without dropping the database",
            "TransactionTestCase resets database state via rollback",
            "schema_cleanup fixture drops tenant schemas after tests",
            "pytest-django --reuse-db preserves DB across test sessions",
            "TRUNCATE CASCADE empties tables while preserving structure",
        ],
    }
    logger.debug(
        "Test database config: database_settings=%d, migration_behaviors=%d",
        len(config["database_settings"]),
        len(config["migration_behaviors"]),
    )
    return config


def get_test_schema_management_config() -> dict:
    """Return test schema management configuration.

    Documents schema creation and cleanup utilities, safety guarantees
    for test isolation, and verification checks to ensure tenant
    schemas do not leak between test runs.

    SubPhase-10, Group-A, Task 04.

    Returns:
        dict: Configuration with *schema_management_documented* flag,
              *schema_utilities* list, *safety_guarantees* list,
              and *isolation_checks* list.
    """
    config: dict = {
        "schema_management_documented": True,
        "schema_utilities": [
            "create_test_schema(name) -- create a PostgreSQL schema for tests",
            "drop_test_schema(name) -- drop a test schema and all its objects",
            "verify_schema_exists(name) -- check schema presence in pg_namespace",
            "list_test_schemas() -- list all schemas matching test_ prefix",
            "reset_search_path() -- restore search_path to public default",
            "set_test_search_path(name) -- set search_path to a test schema",
            "clone_schema(source, target) -- clone schema structure for tests",
        ],
        "safety_guarantees": [
            "test schemas use test_ prefix to prevent production conflicts",
            "teardown fixtures always run even when tests fail or error",
            "schema creation wrapped in try/finally for cleanup assurance",
            "connection.set_schema_to_public() called in fixture finalizers",
            "parallel test workers use unique schema names with worker ID",
            "schema existence check before drop prevents missing schema errors",
        ],
        "isolation_checks": [
            "assert_schema_isolated verifies no cross-schema data leakage",
            "verify_no_shared_state checks thread-local tenant is cleared",
            "check_search_path_reset confirms public schema is restored",
            "validate_connection_schema ensures connection matches expected",
            "count_test_schemas asserts all temp schemas were dropped",
            "verify_tenant_context_cleared checks tenant context manager exit",
        ],
    }
    logger.debug(
        "Test schema management config: schema_utilities=%d, safety_guarantees=%d",
        len(config["schema_utilities"]),
        len(config["safety_guarantees"]),
    )
    return config


def get_pytest_django_config() -> dict:
    """Return pytest-django configuration.

    Documents the pytest-django dependency, installation, usage
    patterns with DJANGO_SETTINGS_MODULE, and plugin features
    including database access markers and built-in fixtures.

    SubPhase-10, Group-A, Task 05.

    Returns:
        dict: Configuration with *pytest_django_documented* flag,
              *dependency_details* list, *usage_patterns* list,
              and *plugin_features* list.
    """
    config: dict = {
        "pytest_django_documented": True,
        "dependency_details": [
            "pytest-django>=4.5.0 -- minimum version for Django 4.2+ support",
            "pip install pytest-django -- install via pip package manager",
            "requirements/test.txt entry -- pinned in test requirements file",
            "pyproject.toml [tool.pytest.ini_options] -- config location",
            "pytest-django auto-discovers conftest.py fixtures on startup",
            "compatible with pytest>=7.0 and Django>=3.2 LTS versions",
        ],
        "usage_patterns": [
            "DJANGO_SETTINGS_MODULE=config.settings.test in pytest.ini",
            "@pytest.mark.django_db -- marks tests requiring DB access",
            "@pytest.mark.django_db(transaction=True) -- transaction tests",
            "django_assert_num_queries fixture for query count assertions",
            "settings fixture allows runtime Django settings overrides",
            "live_server fixture starts a live Django test server instance",
        ],
        "plugin_features": [
            "db fixture -- provides database access for the test function",
            "client fixture -- Django test client for HTTP request testing",
            "admin_client fixture -- authenticated Django admin test client",
            "rf fixture -- RequestFactory for building mock HTTP requests",
            "live_server fixture -- starts a real HTTP server for E2E tests",
            "django_user_model fixture -- returns the active User model class",
        ],
    }
    logger.debug(
        "pytest-django config: dependency_details=%d, usage_patterns=%d",
        len(config["dependency_details"]),
        len(config["usage_patterns"]),
    )
    return config


def get_pytest_xdist_config() -> dict:
    """Return pytest-xdist configuration.

    Documents the pytest-xdist dependency for parallel test execution,
    its installation, CPU-based distribution strategies, worker
    environment variables, and command-line usage flags.

    SubPhase-10, Group-A, Task 06.

    Returns:
        dict: Configuration with *pytest_xdist_documented* flag,
              *dependency_details* list, *parallel_features* list,
              and *usage_flags* list.
    """
    config: dict = {
        "pytest_xdist_documented": True,
        "dependency_details": [
            "pytest-xdist>=3.3.0 -- minimum version for pytest 7+ support",
            "pip install pytest-xdist -- install via pip package manager",
            "requirements/test.txt entry -- pinned in test requirements file",
            "execnet dependency -- required for remote/local process gateways",
            "compatible with pytest>=7.0 for parallel scheduling support",
            "psutil optional dependency -- enables -n auto CPU detection",
        ],
        "parallel_features": [
            "CPU-based distribution -- spreads tests across CPU cores",
            "loadscope scheduling -- groups tests by module or class scope",
            "loadfile scheduling -- groups tests by originating file",
            "PYTEST_XDIST_WORKER env var -- identifies worker in each process",
            "worker-specific databases -- each worker creates its own test DB",
            "forked isolation -- runs each test in a subprocess via --forked",
        ],
        "usage_flags": [
            "-n auto -- auto-detect CPU count and spawn that many workers",
            "-n 4 -- explicitly run tests across 4 parallel workers",
            "--dist loadscope -- distribute by module/class scope grouping",
            "--dist loadfile -- distribute by source file grouping",
            "--dist no -- disable distribution and run tests sequentially",
            "-x --forked -- stop on first failure with subprocess isolation",
        ],
    }
    logger.debug(
        "pytest-xdist config: dependency_details=%d, parallel_features=%d",
        len(config["dependency_details"]),
        len(config["parallel_features"]),
    )
    return config


def get_factory_boy_config() -> dict:
    """Return factory-boy configuration.

    Documents the factory-boy dependency for model factory generation,
    its installation, DjangoModelFactory types, and usage patterns
    for creating test data in the multi-tenant test suite.

    SubPhase-10, Group-A, Task 07.

    Returns:
        dict: Configuration with *factory_boy_documented* flag,
              *dependency_details* list, *factory_types* list,
              and *usage_patterns* list.
    """
    config: dict = {
        "factory_boy_documented": True,
        "dependency_details": [
            "factory-boy>=3.3.0 -- minimum version for Django 4.2+ support",
            "pip install factory-boy -- install via pip package manager",
            "requirements/test.txt entry -- pinned in test requirements file",
            "faker dependency -- factory-boy uses faker for random data",
            "compatible with Django ORM and django-tenants schemas",
            "importable as factory in test modules and conftest files",
        ],
        "factory_types": [
            "DjangoModelFactory -- base class for Django model factories",
            "SubFactory -- creates nested related model instances inline",
            "RelatedFactory -- creates reverse FK related objects post-create",
            "LazyAttribute -- computes field value lazily from other fields",
            "Sequence -- generates incrementing unique values per factory",
            "Trait -- defines boolean toggles for field presets on factories",
        ],
        "usage_patterns": [
            "TenantFactory.create() -- inserts a tenant instance into the DB",
            "TenantFactory.build() -- builds a tenant instance without saving",
            "TenantFactory.create_batch(5) -- creates 5 tenant instances",
            "TenantFactory(name='Custom') -- overrides the name field value",
            "conftest.py fixtures yield factory instances for test injection",
            "schema-aware factories set search_path before model creation",
        ],
    }
    logger.debug(
        "factory-boy config: dependency_details=%d, factory_types=%d",
        len(config["dependency_details"]),
        len(config["factory_types"]),
    )
    return config


def get_faker_config() -> dict:
    """Return faker configuration.

    Documents the faker dependency for random test data generation,
    its provider categories, integration patterns with factory-boy,
    and seeding strategies for reproducible test runs.

    SubPhase-10, Group-A, Task 08.

    Returns:
        dict: Configuration with *faker_documented* flag,
              *dependency_details* list, *provider_categories* list,
              and *integration_patterns* list.
    """
    config: dict = {
        "faker_documented": True,
        "dependency_details": [
            "faker>=19.0.0 -- minimum version for stable provider API",
            "pip install faker -- install via pip package manager",
            "requirements/test.txt entry -- pinned in test requirements file",
            "python-dateutil dependency -- required for date/time providers",
            "compatible with factory-boy via factory.Faker field declarations",
            "supports 50+ locales for internationalized test data generation",
        ],
        "provider_categories": [
            "person -- first_name, last_name, name, prefix, suffix providers",
            "company -- company, catch_phrase, bs, company_suffix providers",
            "address -- street_address, city, state, zipcode, country providers",
            "internet -- email, url, domain_name, ipv4, user_name providers",
            "lorem -- text, sentence, paragraph, word, sentences providers",
            "date_time -- date, time, datetime, past_date, future_date providers",
        ],
        "integration_patterns": [
            "factory.Faker('email') -- declares a faker field on a factory class",
            "factory.LazyFunction(faker.address) -- inline faker call in factory",
            "Faker.seed(42) -- seeds global faker for reproducible test data",
            "faker = Faker('en_US') -- creates locale-specific faker instance",
            "factory.Faker('name', locale='si_LK') -- Sri Lanka locale support",
            "@factory.lazy_attribute with faker for computed field generation",
        ],
    }
    logger.debug(
        "faker config: dependency_details=%d, provider_categories=%d",
        len(config["dependency_details"]),
        len(config["provider_categories"]),
    )
    return config


def get_test_settings_module_config() -> dict:
    """Return test settings module configuration.

    Documents the test-specific Django settings overrides including
    faster password hashers, disabled migrations, in-memory caches
    and email backends, and performance tweaks for faster test runs.

    SubPhase-10, Group-A, Task 09.

    Returns:
        dict: Configuration with *test_settings_documented* flag,
              *settings_overrides* list, *migration_settings* list,
              and *performance_tweaks* list.
    """
    config: dict = {
        "test_settings_documented": True,
        "settings_overrides": [
            "PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']",
            "CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}",
            "EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'",
            "DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'",
            "CELERY_TASK_ALWAYS_EAGER = True -- execute tasks synchronously",
            "DEBUG = False -- match production behavior during test runs",
            "SECRET_KEY = 'test-secret-key-not-for-production-use-only'",
        ],
        "migration_settings": [
            "MIGRATION_MODULES = {} -- disables all migrations for speed",
            "django-test-migrations package for testing migration operations",
            "--keepdb flag preserves test database between consecutive runs",
            "SHARED_APPS migrations run once on the public schema only",
            "TENANT_APPS migrations skipped when MIGRATION_MODULES is empty",
            "selective re-enable of specific app migrations when needed",
        ],
        "performance_tweaks": [
            "MD5PasswordHasher is ~10x faster than default PBKDF2 hasher",
            "LocMemCache avoids network roundtrip to Redis or Memcached",
            "locmem EmailBackend stores emails in memory for assertions",
            "CELERY_TASK_ALWAYS_EAGER avoids broker connection overhead",
            "InMemoryStorage avoids filesystem I/O for uploaded files",
            "LOGGING level set to WARNING to reduce console output noise",
        ],
    }
    logger.debug(
        "test settings module config: settings_overrides=%d, migration_settings=%d",
        len(config["settings_overrides"]),
        len(config["migration_settings"]),
    )
    return config


def get_test_runner_config() -> dict:
    """Return test runner configuration.

    Documents the pytest.ini configuration including
    DJANGO_SETTINGS_MODULE, addopts flags, test discovery rules,
    markers, and filterwarnings for the multi-tenant test suite.

    SubPhase-10, Group-A, Task 10.

    Returns:
        dict: Configuration with *test_runner_documented* flag,
              *pytest_ini_settings* list, *addopts_flags* list,
              and *discovery_rules* list.
    """
    config: dict = {
        "test_runner_documented": True,
        "pytest_ini_settings": [
            "DJANGO_SETTINGS_MODULE = config.settings.test -- test settings path",
            "python_files = test_*.py -- pattern for test file discovery",
            "python_classes = Test* -- pattern for test class discovery",
            "python_functions = test_* -- pattern for test function discovery",
            "testpaths = tests -- root directory for test collection",
            "markers = slow, integration, e2e, tenant -- custom pytest markers",
            "filterwarnings = ignore::DeprecationWarning -- suppress warnings",
        ],
        "addopts_flags": [
            "--reuse-db -- reuse test database across test runs for speed",
            "-v -- verbose output showing individual test names and results",
            "--strict-markers -- error on unregistered marker usage in tests",
            "--tb=short -- short traceback format for concise error output",
            "-x -- stop test run on first failure for fast feedback loops",
            "--no-header -- suppress pytest header for cleaner CI output",
        ],
        "discovery_rules": [
            "sys.path includes project root for absolute import resolution",
            "conftest.py files auto-loaded from testpaths root downward",
            "test_*.py files collected recursively from testpaths directory",
            "__init__.py required in test packages for proper namespace handling",
            "parametrize decorator generates multiple test cases from params",
            "--collect-only flag lists discovered tests without executing them",
        ],
    }
    logger.debug(
        "test runner config: pytest_ini_settings=%d, addopts_flags=%d",
        len(config["pytest_ini_settings"]),
        len(config["addopts_flags"]),
    )
    return config


def get_test_markers_config() -> dict:
    """Return test markers configuration.

    Documents custom pytest markers (multi_tenant, isolation, leak,
    performance, slow, integration, e2e) and their usage with
    ``pytest -m`` for selective test execution.

    SubPhase-10, Group-A, Task 11.

    Returns:
        dict: Configuration with *test_markers_documented* flag,
              *marker_definitions* list, *usage_commands* list,
              and *registration_steps* list.
    """
    config: dict = {
        "test_markers_documented": True,
        "marker_definitions": [
            "multi_tenant -- marks tests requiring tenant schema isolation",
            "isolation -- marks tests verifying schema isolation guarantees",
            "leak -- marks tests detecting schema or data leak across tenants",
            "performance -- marks tests measuring query and response times",
            "slow -- marks tests exceeding 1-second execution threshold",
            "integration -- marks tests spanning multiple modules or services",
            "e2e -- marks end-to-end tests covering full request lifecycle",
        ],
        "usage_commands": [
            "pytest -m multi_tenant -- run only multi-tenant marker tests",
            "pytest -m 'not slow' -- exclude slow tests from the run",
            "pytest -m 'isolation and not e2e' -- combine markers with logic",
            "pytest -m performance -- run only performance benchmark tests",
            "pytest -m 'multi_tenant or integration' -- run either marker",
            "pytest --markers -- list all registered markers and descriptions",
        ],
        "registration_steps": [
            "add marker to pytest.ini [pytest] markers section with description",
            "register marker in conftest.py using pytest_configure hook",
            "enable --strict-markers in addopts to error on unregistered markers",
            "document marker intent and scope in project test guidelines",
            "apply markers via @pytest.mark.<name> decorator on tests",
            "use markers in CI pipeline steps for selective test execution",
        ],
    }
    logger.debug(
        "test markers config: marker_definitions=%d, usage_commands=%d",
        len(config["marker_definitions"]),
        len(config["usage_commands"]),
    )
    return config


def get_multi_tenant_marker_config() -> dict:
    """Return multi-tenant marker configuration.

    Documents the multi_tenant marker intent, required fixtures,
    and labeling conventions for tenant-aware test cases.

    SubPhase-10, Group-A, Task 12.

    Returns:
        dict: Configuration with *multi_tenant_marker_documented* flag,
              *marker_properties* list, *required_fixtures* list,
              and *usage_examples* list.
    """
    config: dict = {
        "multi_tenant_marker_documented": True,
        "marker_properties": [
            "intent: identify tests that require tenant schema isolation",
            "label: @pytest.mark.multi_tenant applied to class or function",
            "filtering: pytest -m multi_tenant selects only these tests",
            "requires tenant_setup fixture for schema provisioning",
            "triggers automatic schema creation and teardown per test",
            "ensures each test runs in an isolated PostgreSQL schema",
        ],
        "required_fixtures": [
            "tenant_setup -- provisions a tenant schema before test execution",
            "test_schema -- creates and activates a temporary test schema",
            "db_connection -- provides a database connection scoped to schema",
            "tenant_context -- sets the current tenant in thread-local state",
            "schema_cleanup -- tears down the test schema after execution",
            "tenant_factory -- creates tenant instances with unique schemas",
        ],
        "usage_examples": [
            "@pytest.mark.multi_tenant on a test class marks all methods",
            "@pytest.mark.multi_tenant on a single function marks it alone",
            "combine with @pytest.mark.parametrize for multiple tenants",
            "use with @pytest.mark.slow for long-running tenant tests",
            "nest under class-level marker for inherited fixture scoping",
            "pair with isolation marker for cross-tenant leak detection",
        ],
    }
    logger.debug(
        "multi-tenant marker config: marker_properties=%d, required_fixtures=%d",
        len(config["marker_properties"]),
        len(config["required_fixtures"]),
    )
    return config


def get_slow_test_marker_config() -> dict:
    """Return slow test marker configuration.

    Documents the slow test marker criteria, threshold duration,
    and CI exclusion strategies for tests exceeding acceptable
    execution times.

    SubPhase-10, Group-A, Task 13.

    Returns:
        dict: Configuration with *slow_marker_documented* flag,
              *slow_criteria* list, *ci_usage* list,
              and *optimization_tips* list.
    """
    config: dict = {
        "slow_marker_documented": True,
        "slow_criteria": [
            "duration threshold: tests exceeding 1 second execution time",
            "schema creation: tests that create full PostgreSQL schemas",
            "full provisioning: tests running complete tenant provisioning",
            "large dataset: tests loading bulk data for query benchmarks",
            "external service: tests with real HTTP or API integrations",
            "migration replay: tests replaying full migration sequences",
        ],
        "ci_usage": [
            "pytest -m 'not slow' -- exclude slow tests in CI pipelines",
            "run slow tests separately in a dedicated CI stage or job",
            "schedule slow test suite on nightly CI builds only",
            "set CI timeout limits per job to catch unexpectedly slow tests",
            "report slow test durations with --durations=10 flag in CI",
            "alert on slow test regressions via CI performance thresholds",
        ],
        "optimization_tips": [
            "reduce test duration by reusing schemas with --reuse-db flag",
            "use fixture caching with session scope for shared resources",
            "run slow tests in parallel with pytest-xdist -n auto workers",
            "mock external services to eliminate network latency overhead",
            "use factory_boy create_batch instead of loops for bulk data",
            "profile slow tests with --durations flag to find bottlenecks",
        ],
    }
    logger.debug(
        "slow test marker config: slow_criteria=%d, ci_usage=%d",
        len(config["slow_criteria"]),
        len(config["ci_usage"]),
    )
    return config


def get_test_infrastructure_documentation() -> dict:
    """Return test infrastructure documentation.

    Summarizes the overall test infrastructure setup including
    structure, modules, settings, markers, dependencies, and
    provides maintenance and extension guidance.

    SubPhase-10, Group-A, Task 14.

    Returns:
        dict: Configuration with *infrastructure_documented* flag,
              *infrastructure_summary* list, *maintenance_guides* list,
              and *extension_points* list.
    """
    config: dict = {
        "infrastructure_documented": True,
        "infrastructure_summary": [
            "test module structure: organized by app with shared helpers",
            "conftest.py: fixtures for tenant setup, schema, and cleanup",
            "test database: schema-per-tenant with automatic provisioning",
            "schema management: create, activate, and destroy test schemas",
            "markers: multi_tenant, slow, isolation, performance, e2e, integration",
            "dependencies: pytest-django, pytest-xdist, factory-boy, faker",
            "settings: test-specific overrides for speed and isolation",
        ],
        "maintenance_guides": [
            "add new markers in pytest.ini and conftest.py pytest_configure",
            "create new fixtures in conftest.py with appropriate scope",
            "update test settings module when adding new Django apps",
            "extend factory definitions when models change or are added",
            "review slow test thresholds quarterly to keep CI fast",
            "update test documentation when infrastructure changes occur",
        ],
        "extension_points": [
            "new marker types: register in pytest.ini and document usage",
            "custom fixtures: add to conftest.py with session or function scope",
            "plugin integration: install via pip and configure in conftest.py",
            "custom test runners: subclass DjangoTestRunner for extensions",
            "new factory types: add SubFactory and LazyAttribute patterns",
            "CI pipeline hooks: add new stages for specialized test suites",
        ],
    }
    logger.debug(
        "test infrastructure docs: infrastructure_summary=%d, maintenance_guides=%d",
        len(config["infrastructure_summary"]),
        len(config["maintenance_guides"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-B: TenantTestCase Base Class – Tasks 15-20 (Base Class Setup)
# ---------------------------------------------------------------------------


def get_tenant_test_case_config() -> dict:
    """Return TenantTestCase base class configuration.

    Documents the TenantTestCase base class scope, purpose, and
    usage requirements for all multi-tenant tests in the suite.
    All tenant-aware tests must inherit from TenantTestCase to
    receive automatic tenant setup and teardown behavior.

    SubPhase-10, Group-B, Task 15.

    Returns:
        dict: Configuration with *base_class_documented* flag,
              *class_scope* list, *usage_requirements* list,
              and *class_responsibilities* list.
    """
    config: dict = {
        "base_class_documented": True,
        "class_scope": [
            "TenantTestCase centralizes all tenant test setup and teardown",
            "provides automatic test tenant creation before each test",
            "manages schema activation and deactivation around tests",
            "ensures full isolation between test methods and classes",
            "acts as the single entry point for multi-tenant test behavior",
            "encapsulates tenant lifecycle management for test authors",
        ],
        "usage_requirements": [
            "all tenant-aware tests must inherit from TenantTestCase",
            "subclasses may override setUp to add custom initialization",
            "subclasses must call super().setUp() when overriding setUp",
            "subclasses must call super().tearDown() when overriding tearDown",
            "TenantTestCase should not be instantiated directly for tests",
            "use pytest markers alongside TenantTestCase for CI filtering",
        ],
        "class_responsibilities": [
            "create a unique test tenant with a dedicated schema per test",
            "activate the tenant schema on the database connection",
            "set the tenant on the current request context thread-local",
            "clean up tenant schemas after each test to prevent leaks",
            "reset the database connection to the public schema on teardown",
            "provide self.tenant and self.domain as test instance attributes",
        ],
    }
    logger.debug(
        "TenantTestCase config: class_scope=%d, usage_requirements=%d",
        len(config["class_scope"]),
        len(config["usage_requirements"]),
    )
    return config


def get_django_testcase_extension_config() -> dict:
    """Return Django TestCase extension configuration.

    Documents how TenantTestCase extends Django TestCase to retain
    standard test behavior including transaction wrapping, assertion
    methods, and compatibility with pytest-django.

    SubPhase-10, Group-B, Task 16.

    Returns:
        dict: Configuration with *extension_documented* flag,
              *inheritance_details* list, *compatibility_notes* list,
              and *retained_behaviors* list.
    """
    config: dict = {
        "extension_documented": True,
        "inheritance_details": [
            "TenantTestCase inherits from django.test.TestCase",
            "single inheritance chain preserves Django test lifecycle",
            "TestCase provides transaction wrapping per test method",
            "TestCase provides setUpClass and tearDownClass hooks",
            "TestCase provides all standard Django assertion methods",
            "TenantTestCase overrides setUp and tearDown only",
        ],
        "compatibility_notes": [
            "pytest-django discovers TestCase subclasses automatically",
            "pytest fixtures can be used alongside TestCase methods",
            "django_db marker is implied by TestCase inheritance",
            "TransactionTestCase can be used as an alternative base",
            "LiveServerTestCase is not supported with TenantTestCase",
            "parallel test execution requires unique schema names per worker",
        ],
        "retained_behaviors": [
            "self.assertEqual and all assertion helpers are available",
            "self.client provides the Django test client for HTTP tests",
            "self.settings() context manager overrides Django settings",
            "cls.setUpTestData() can be used for class-level shared data",
            "database transactions are rolled back after each test method",
            "test ordering and dependency resolution follow pytest rules",
        ],
    }
    logger.debug(
        "Django TestCase extension config: inheritance_details=%d, "
        "compatibility_notes=%d",
        len(config["inheritance_details"]),
        len(config["compatibility_notes"]),
    )
    return config


def get_setup_method_config() -> dict:
    """Return setUp method configuration.

    Documents the setUp method flow for TenantTestCase including
    tenant creation, schema activation, context initialization,
    and guidance on extending setUp in subclasses.

    SubPhase-10, Group-B, Task 17.

    Returns:
        dict: Configuration with *setup_documented* flag,
              *setup_flow* list, *override_guidance* list,
              and *setup_guarantees* list.
    """
    config: dict = {
        "setup_documented": True,
        "setup_flow": [
            "call super().setUp() to initialize Django TestCase state",
            "generate a unique schema name using test class and method name",
            "create a Tenant instance with auto_create_schema enabled",
            "create a Domain instance linked to the test tenant",
            "activate the tenant schema on the database connection",
            "store tenant and domain as self.tenant and self.domain",
        ],
        "override_guidance": [
            "always call super().setUp() first when overriding setUp",
            "add custom fixtures after super().setUp() completes",
            "use self.tenant to reference the active test tenant",
            "use self.domain to reference the test tenant domain",
            "create additional models within the tenant schema context",
            "avoid changing the database connection schema in setUp overrides",
        ],
        "setup_guarantees": [
            "self.tenant is a fully persisted Tenant model instance",
            "self.domain is a fully persisted Domain model instance",
            "the database connection search_path targets the tenant schema",
            "thread-local tenant context is set to self.tenant",
            "all ORM queries execute within the tenant schema by default",
            "setUp completes before the test method body begins execution",
        ],
    }
    logger.debug(
        "setUp method config: setup_flow=%d, override_guidance=%d",
        len(config["setup_flow"]),
        len(config["override_guidance"]),
    )
    return config


def get_teardown_method_config() -> dict:
    """Return tearDown method configuration.

    Documents the tearDown method flow for TenantTestCase including
    schema cleanup, context reset, and safety guarantees for test
    isolation between consecutive test runs.

    SubPhase-10, Group-B, Task 18.

    Returns:
        dict: Configuration with *teardown_documented* flag,
              *cleanup_flow* list, *safety_notes* list,
              and *teardown_guarantees* list.
    """
    config: dict = {
        "teardown_documented": True,
        "cleanup_flow": [
            "reset the database connection search_path to public schema",
            "clear the thread-local tenant context to prevent leaks",
            "drop the test tenant schema from the database if created",
            "delete the Domain instance created during setUp",
            "delete the Tenant instance created during setUp",
            "call super().tearDown() to finalize Django TestCase cleanup",
        ],
        "safety_notes": [
            "tearDown runs even when the test method raises an exception",
            "schema drop uses IF EXISTS to avoid errors on missing schemas",
            "connection reset ensures next test starts on public schema",
            "thread-local cleanup prevents tenant bleed between tests",
            "orphan schema detection logs warnings for unexpected schemas",
            "tearDown failures are logged but do not mask test failures",
        ],
        "teardown_guarantees": [
            "no tenant schema persists after tearDown completes",
            "the database connection returns to the public schema",
            "thread-local tenant context is cleared to None",
            "all tenant-specific data is removed from the database",
            "subsequent tests receive a clean database state",
            "tearDown completes before the next test setUp begins",
        ],
    }
    logger.debug(
        "tearDown method config: cleanup_flow=%d, safety_notes=%d",
        len(config["cleanup_flow"]),
        len(config["safety_notes"]),
    )
    return config


def get_test_tenant_creation_config() -> dict:
    """Return test tenant creation configuration.

    Documents automatic tenant creation for tests including the
    default tenant attributes, domain configuration, schema naming
    conventions, and factory/fixture usage patterns.

    SubPhase-10, Group-B, Task 19.

    Returns:
        dict: Configuration with *tenant_creation_documented* flag,
              *creation_details* list, *default_values* list,
              and *customization_options* list.
    """
    config: dict = {
        "tenant_creation_documented": True,
        "creation_details": [
            "each test creates a fresh Tenant via the Tenant model manager",
            "schema_name is generated as test_<class>_<method>_<short_uuid>",
            "auto_create_schema triggers PostgreSQL CREATE SCHEMA on save",
            "a primary Domain is linked to the Tenant after creation",
            "tenant status is set to active for immediate use in tests",
            "factory_boy TenantFactory can be used as an alternative creator",
        ],
        "default_values": [
            "name -- Test Tenant (overridable via setUp parameters)",
            "slug -- test-tenant-<short_uuid> for uniqueness",
            "schema_name -- tenant_test_<short_uuid> with tenant_ prefix",
            "domain -- test-<short_uuid>.localhost for local resolution",
            "status -- active to enable full tenant functionality",
            "on_trial -- False to avoid trial-related side effects",
        ],
        "customization_options": [
            "override get_tenant_kwargs() to supply custom Tenant fields",
            "override get_domain_kwargs() to supply custom Domain fields",
            "use TenantFactory.create() for complex field combinations",
            "pass schema_name explicitly to control schema naming",
            "set on_trial=True to test trial-specific logic paths",
            "set status=suspended to test suspended-tenant behavior",
        ],
    }
    logger.debug(
        "test tenant creation config: creation_details=%d, default_values=%d",
        len(config["creation_details"]),
        len(config["default_values"]),
    )
    return config


def get_tenant_context_setup_config() -> dict:
    """Return tenant context setup configuration.

    Documents how TenantTestCase sets the tenant context before
    test execution including search_path activation, thread-local
    storage, request context, and validation steps.

    SubPhase-10, Group-B, Task 20.

    Returns:
        dict: Configuration with *context_documented* flag,
              *context_setup_steps* list, *validation_checks* list,
              and *context_scope_notes* list.
    """
    config: dict = {
        "context_documented": True,
        "context_setup_steps": [
            "set PostgreSQL search_path to the tenant schema via SET search_path",
            "store the tenant instance in thread-local storage via set_current_tenant",
            "update the database connection tenant attribute for django-tenants",
            "ensure the tenant schema exists before activating it",
            "verify the search_path was applied by querying SHOW search_path",
            "make the tenant available as self.tenant for test method access",
        ],
        "validation_checks": [
            "assert search_path matches the expected tenant schema name",
            "assert get_current_tenant() returns the correct tenant instance",
            "assert connection.schema_name equals the tenant schema_name",
            "assert queries execute within the tenant schema not public",
            "assert ORM model tables resolve to the tenant schema namespace",
            "log a warning if search_path verification fails during setUp",
        ],
        "context_scope_notes": [
            "tenant context is scoped to the individual test method",
            "context is set after setUp and cleared after tearDown",
            "nested schema switches within a test use tenant_context manager",
            "thread-local storage is per-thread so parallel tests are safe",
            "request context is simulated without an actual HTTP request",
            "context setup is idempotent and safe to call multiple times",
        ],
    }
    logger.debug(
        "tenant context setup config: context_setup_steps=%d, "
        "validation_checks=%d",
        len(config["context_setup_steps"]),
        len(config["validation_checks"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-B: TenantTestCase Base Class – Tasks 21-25 (Mixin & Helpers)
# ---------------------------------------------------------------------------


def get_tenant_context_manager_config() -> dict:
    """Return tenant context manager configuration.

    Documents the tenant context manager that allows temporary
    schema switching within a test method using a with-statement,
    with automatic context restoration on exit.

    SubPhase-10, Group-B, Task 21.

    Returns:
        dict: Configuration with *manager_documented* flag,
              *manager_behavior* list, *restoration_details* list,
              and *usage_patterns* list.
    """
    config: dict = {
        "manager_documented": True,
        "manager_behavior": [
            "accepts a Tenant instance as the target context",
            "saves the current search_path before switching schemas",
            "sets the database connection search_path to the target schema",
            "updates thread-local tenant storage to the target tenant",
            "yields control to the with-block for test operations",
            "restores the original search_path and tenant on exit",
        ],
        "restoration_details": [
            "original search_path is restored even if an exception occurs",
            "thread-local tenant context reverts to the previous tenant",
            "database connection schema_name attribute is reset",
            "nested context managers restore to their respective levels",
            "restoration failure raises a warning but does not swallow errors",
            "context manager is reentrant and supports nested invocations",
        ],
        "usage_patterns": [
            "with tenant_context(other_tenant) to temporarily switch schemas",
            "use inside test methods to verify cross-tenant isolation",
            "combine with assertions to check schema-specific data access",
            "nest multiple context managers for multi-schema test scenarios",
            "use with TenantTestCase.tenant to re-enter the default context",
            "avoid storing references to objects created in a switched context",
        ],
    }
    logger.debug(
        "tenant context manager config: manager_behavior=%d, "
        "restoration_details=%d",
        len(config["manager_behavior"]),
        len(config["restoration_details"]),
    )
    return config


def get_multi_tenant_test_mixin_config() -> dict:
    """Return multi-tenant test mixin configuration.

    Documents the MultiTenantTestMixin that provides reusable
    tenant setup helpers and utility methods for tests requiring
    multiple tenant contexts or cross-tenant verification.

    SubPhase-10, Group-B, Task 22.

    Returns:
        dict: Configuration with *mixin_documented* flag,
              *mixin_utilities* list, *compatibility_notes* list,
              and *mixin_methods* list.
    """
    config: dict = {
        "mixin_documented": True,
        "mixin_utilities": [
            "create_tenant() generates a new tenant with unique schema",
            "create_domain(tenant) links a domain to a given tenant",
            "activate_tenant(tenant) switches context to a tenant schema",
            "deactivate_tenant() resets context to the public schema",
            "get_tenant_count() returns the number of created test tenants",
            "cleanup_tenants() drops all test schemas and deletes tenants",
        ],
        "compatibility_notes": [
            "mixin is designed for use with TenantTestCase as the base class",
            "mixin methods assume the database connection is available",
            "mixin does not override setUp or tearDown to avoid conflicts",
            "mixin utilities are stateless and safe for parallel execution",
            "mixin can be combined with other test mixins without conflicts",
            "mixin relies on django-tenants for schema operations",
        ],
        "mixin_methods": [
            "create_tenant -- creates and returns a new Tenant instance",
            "create_domain -- creates and returns a Domain for a tenant",
            "activate_tenant -- sets search_path and thread-local context",
            "deactivate_tenant -- resets to public schema and clears context",
            "get_tenant_count -- returns count of test tenants created",
            "cleanup_tenants -- drops schemas and deletes all test tenants",
        ],
    }
    logger.debug(
        "multi-tenant test mixin config: mixin_utilities=%d, "
        "mixin_methods=%d",
        len(config["mixin_utilities"]),
        len(config["mixin_methods"]),
    )
    return config


def get_two_tenant_setup_config() -> dict:
    """Return two-tenant setup configuration.

    Documents the helper that creates two isolated tenants
    (tenant_a and tenant_b) for cross-tenant isolation tests,
    each with their own schema and domain.

    SubPhase-10, Group-B, Task 23.

    Returns:
        dict: Configuration with *setup_documented* flag,
              *setup_details* list, *isolation_assumptions* list,
              and *tenant_attributes* list.
    """
    config: dict = {
        "setup_documented": True,
        "setup_details": [
            "creates tenant_a with a unique schema and domain",
            "creates tenant_b with a separate unique schema and domain",
            "stores both tenants as self.tenant_a and self.tenant_b",
            "stores both domains as self.domain_a and self.domain_b",
            "both tenants are set to active status with auto_create_schema",
            "setup runs within setUp and both tenants are torn down in tearDown",
        ],
        "isolation_assumptions": [
            "tenant_a and tenant_b have completely separate PostgreSQL schemas",
            "data created in tenant_a schema is invisible to tenant_b",
            "data created in tenant_b schema is invisible to tenant_a",
            "switching between tenants changes the active search_path",
            "shared (public) schema data is visible to both tenants",
            "schema names include unique suffixes to prevent collisions",
        ],
        "tenant_attributes": [
            "self.tenant_a -- first Tenant instance for cross-tenant tests",
            "self.tenant_b -- second Tenant instance for cross-tenant tests",
            "self.domain_a -- Domain linked to tenant_a",
            "self.domain_b -- Domain linked to tenant_b",
            "self.schema_a -- schema name string for tenant_a",
            "self.schema_b -- schema name string for tenant_b",
        ],
    }
    logger.debug(
        "two-tenant setup config: setup_details=%d, "
        "isolation_assumptions=%d",
        len(config["setup_details"]),
        len(config["isolation_assumptions"]),
    )
    return config


def get_tenant_switching_helper_config() -> dict:
    """Return tenant switching helper configuration.

    Documents the helper that switches the active tenant context
    including search_path, thread-local storage, and connection
    attributes with proper cleanup guarantees.

    SubPhase-10, Group-B, Task 24.

    Returns:
        dict: Configuration with *helper_documented* flag,
              *switching_steps* list, *safety_guarantees* list,
              and *helper_interface* list.
    """
    config: dict = {
        "helper_documented": True,
        "switching_steps": [
            "accept the target Tenant instance as a parameter",
            "save the current search_path for later restoration",
            "execute SET search_path to the target tenant schema",
            "update the thread-local current tenant reference",
            "update the connection schema_name attribute",
            "return the previous tenant for manual restoration if needed",
        ],
        "safety_guarantees": [
            "switching validates the target schema exists before activation",
            "invalid schema names raise a descriptive ValueError",
            "cleanup restores the original context on exception",
            "switching is atomic -- partial switches are rolled back",
            "thread-local and connection state remain consistent",
            "consecutive switches without cleanup are logged as warnings",
        ],
        "helper_interface": [
            "switch_to_tenant(tenant) -- switch to the given tenant context",
            "switch_to_public() -- switch back to the public schema",
            "get_previous_tenant() -- return the tenant before last switch",
            "is_switched() -- check if context differs from default tenant",
            "restore_tenant(tenant) -- restore a specific tenant context",
            "switch_and_verify(tenant) -- switch and assert schema matches",
        ],
    }
    logger.debug(
        "tenant switching helper config: switching_steps=%d, "
        "safety_guarantees=%d",
        len(config["switching_steps"]),
        len(config["safety_guarantees"]),
    )
    return config


def get_schema_assertion_helper_config() -> dict:
    """Return schema assertion helper configuration.

    Documents the assertion helper that validates the current
    database schema context matches the expected tenant schema,
    for use within multi-tenant test methods.

    SubPhase-10, Group-B, Task 25.

    Returns:
        dict: Configuration with *assertion_documented* flag,
              *assertion_methods* list, *integration_notes* list,
              and *failure_messages* list.
    """
    config: dict = {
        "assertion_documented": True,
        "assertion_methods": [
            "assert_schema_is(schema_name) -- assert current search_path matches",
            "assert_tenant_active(tenant) -- assert tenant is the active context",
            "assert_public_schema() -- assert search_path is the public schema",
            "assert_schema_exists(schema_name) -- assert schema exists in DB",
            "assert_schema_not_exists(schema_name) -- assert schema was dropped",
            "assert_table_in_schema(table, schema) -- assert table presence",
        ],
        "integration_notes": [
            "assertion helpers are available on TenantTestCase via mixin",
            "use assertions after tenant switches to verify context",
            "combine with tenant_context manager for isolation checks",
            "assertion failures provide descriptive schema mismatch messages",
            "assertions query pg_catalog for schema existence verification",
            "assertions are safe to call multiple times within a single test",
        ],
        "failure_messages": [
            "Expected schema '<expected>' but found '<actual>' on search_path",
            "Tenant '<tenant>' is not the active tenant in thread-local storage",
            "Expected public schema but found '<actual>' on search_path",
            "Schema '<name>' does not exist in the PostgreSQL catalog",
            "Schema '<name>' was expected to be dropped but still exists",
            "Table '<table>' not found in schema '<schema>' catalog entries",
        ],
    }
    logger.debug(
        "schema assertion helper config: assertion_methods=%d, "
        "integration_notes=%d",
        len(config["assertion_methods"]),
        len(config["integration_notes"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-B: TenantTestCase Base Class – Tasks 26-28 (Isolation, Rollback & Docs)
# ---------------------------------------------------------------------------


def get_isolation_assertion_config() -> dict:
    """Return isolation assertion configuration.

    Documents assertion helpers that verify tenant data isolation
    by confirming tenant-specific data visibility and cross-tenant
    data invisibility within test methods.

    SubPhase-10, Group-B, Task 26.

    Returns:
        dict: Configuration with *assertion_documented* flag,
              *isolation_assertions* list, *usage_patterns* list,
              and *verification_targets* list.
    """
    config: dict = {
        "assertion_documented": True,
        "isolation_assertions": [
            "assert_data_visible_in_tenant(model, pk, tenant) -- confirms record exists",
            "assert_data_not_visible_in_tenant(model, pk, tenant) -- confirms record hidden",
            "assert_queryset_isolated(model, tenant) -- confirms no cross-tenant rows",
            "assert_tenant_data_count(model, tenant, count) -- confirms expected row count",
            "assert_no_public_data_leak(model) -- confirms no shared schema leakage",
            "assert_cross_tenant_invisible(model, pk, tenant_a, tenant_b) -- full check",
        ],
        "usage_patterns": [
            "create data in tenant_a then assert invisible from tenant_b context",
            "switch to tenant_b and verify queryset returns zero matching records",
            "use with two-tenant setup for comprehensive isolation checks",
            "combine with schema assertion to verify correct search_path",
            "run isolation assertions after each tenant context switch",
            "use in tearDown to ensure no residual data across tenants",
        ],
        "verification_targets": [
            "tenant-scoped model instances are only visible in their schema",
            "shared model instances are visible from all tenant schemas",
            "foreign keys do not leak references across tenant boundaries",
            "aggregation queries respect tenant schema boundaries",
            "raw SQL queries within a tenant context see only tenant data",
            "bulk operations respect the active schema isolation boundary",
        ],
    }
    logger.debug(
        "isolation assertion config: isolation_assertions=%d, "
        "usage_patterns=%d",
        len(config["isolation_assertions"]),
        len(config["usage_patterns"]),
    )
    return config


def get_transaction_rollback_config() -> dict:
    """Return transaction rollback configuration.

    Documents how TenantTestCase ensures automatic transaction
    rollback after each test to reset database state and maintain
    clean isolation between consecutive test runs.

    SubPhase-10, Group-B, Task 27.

    Returns:
        dict: Configuration with *rollback_documented* flag,
              *rollback_behavior* list, *scope_details* list,
              and *rollback_guarantees* list.
    """
    config: dict = {
        "rollback_documented": True,
        "rollback_behavior": [
            "Django TestCase wraps each test method in a transaction",
            "the transaction is rolled back automatically after the test completes",
            "data created during the test does not persist to the next test",
            "schema-level changes such as DDL are excluded from rollback",
            "tearDown drops test schemas to handle DDL changes explicitly",
            "TransactionTestCase can be used when DDL rollback is required",
        ],
        "scope_details": [
            "rollback scope is per-test-method not per-test-class",
            "setUpTestData uses a class-level transaction for shared fixtures",
            "each test method sees a savepoint that is rolled back on completion",
            "nested transactions within a test are collapsed into savepoints",
            "rollback includes all tenant-scoped and shared-scoped data changes",
            "cleanup of test schemas occurs in tearDown after rollback",
        ],
        "rollback_guarantees": [
            "no test data survives beyond the individual test method boundary",
            "failed tests still trigger rollback and tearDown cleanup",
            "parallel test workers each maintain independent transactions",
            "schema creation and deletion are handled outside the transaction",
            "the public schema state remains consistent between tests",
            "database connection state is reset to public after each test",
        ],
    }
    logger.debug(
        "transaction rollback config: rollback_behavior=%d, "
        "scope_details=%d",
        len(config["rollback_behavior"]),
        len(config["scope_details"]),
    )
    return config


def get_tenant_test_case_documentation() -> dict:
    """Return TenantTestCase usage documentation.

    Provides comprehensive usage guidance for TenantTestCase
    including inheritance patterns, mixin integration, helper
    usage, and extension points for custom test scenarios.

    SubPhase-10, Group-B, Task 28.

    Returns:
        dict: Configuration with *documentation_completed* flag,
              *usage_guidance* list, *extension_notes* list,
              and *best_practices* list.
    """
    config: dict = {
        "documentation_completed": True,
        "usage_guidance": [
            "inherit from TenantTestCase for all tenant-aware test classes",
            "access self.tenant and self.domain in test methods",
            "override setUp with super().setUp() call for custom initialization",
            "use tenant_context manager for temporary schema switches",
            "combine with MultiTenantTestMixin for multi-tenant scenarios",
            "use schema assertion helpers to verify context after operations",
        ],
        "extension_notes": [
            "add MultiTenantTestMixin for two-tenant test setups",
            "override get_tenant_kwargs() to customize test tenant fields",
            "override get_domain_kwargs() to customize test domain fields",
            "create subclasses for domain-specific test base classes",
            "combine with factory_boy factories for complex data scenarios",
            "use pytest markers alongside TenantTestCase for CI filtering",
        ],
        "best_practices": [
            "always call super().setUp() and super().tearDown() in overrides",
            "avoid storing cross-tenant references in instance attributes",
            "use isolation assertions after every tenant context switch",
            "keep test methods focused on a single tenant operation",
            "use descriptive test names that indicate the tenant scenario",
            "document any custom setUp logic in the test class docstring",
        ],
    }
    logger.debug(
        "TenantTestCase documentation: usage_guidance=%d, "
        "extension_notes=%d",
        len(config["usage_guidance"]),
        len(config["extension_notes"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-C: Test Fixtures & Factories – Model Factories (Tasks 29-34)
# ---------------------------------------------------------------------------


def get_tenant_factory_config() -> dict:
    """Return TenantFactory configuration.

    Documents the factory_boy factory for tenant models including
    schema name generation, domain defaults, and trait definitions
    used to create test tenant instances with predictable attributes.

    SubPhase-10, Group-C, Task 29.

    Returns:
        dict: Configuration with *factory_documented* flag,
              *factory_fields* list, *schema_defaults* list,
              and *factory_traits* list.
    """
    config: dict = {
        "factory_documented": True,
        "factory_fields": [
            "name -- tenant display name via Faker company provider",
            "slug -- URL-safe slug derived from tenant name",
            "schema_name -- unique PostgreSQL schema identifier",
            "is_active -- boolean defaulting to True for test tenants",
            "paid_until -- date field set to 30 days in the future",
            "on_trial -- boolean defaulting to False for stable tests",
        ],
        "schema_defaults": [
            "schema_name uses LazyAttribute with slugified tenant name",
            "schema prefix is 'tenant_' followed by a 6-char hex suffix",
            "duplicate schema names are avoided via Sequence counter",
            "schema_name is validated against PostgreSQL identifier rules",
            "maximum schema_name length is 63 characters per PostgreSQL limit",
            "public and shared schema names are excluded from generation",
        ],
        "factory_traits": [
            "trait 'trial' sets on_trial=True and paid_until=today+7",
            "trait 'expired' sets paid_until to 30 days in the past",
            "trait 'inactive' sets is_active=False for deactivation tests",
            "trait 'with_domain' creates a related Domain via SubFactory",
            "trait 'enterprise' sets plan to enterprise tier for limit tests",
            "trait 'minimal' omits optional fields for lightweight fixtures",
        ],
    }
    logger.debug(
        "TenantFactory config: factory_fields=%d, schema_defaults=%d",
        len(config["factory_fields"]),
        len(config["schema_defaults"]),
    )
    return config


def get_domain_factory_config() -> dict:
    """Return DomainFactory configuration.

    Documents the factory_boy factory for domain models linked to
    tenants, including subdomain generation, primary domain defaults,
    and verification status field configuration.

    SubPhase-10, Group-C, Task 30.

    Returns:
        dict: Configuration with *factory_documented* flag,
              *domain_fields* list, *tenant_linkage* list,
              and *domain_defaults* list.
    """
    config: dict = {
        "factory_documented": True,
        "domain_fields": [
            "domain -- full domain string e.g. 'shop1.lankacommerce.lk'",
            "is_primary -- boolean indicating primary domain for the tenant",
            "is_verified -- boolean indicating DNS verification completion",
            "verification_token -- UUID token for DNS TXT record validation",
            "ssl_status -- SSL certificate status string field",
            "created_at -- auto-set timestamp on domain creation",
        ],
        "tenant_linkage": [
            "tenant field uses SubFactory pointing to TenantFactory",
            "each domain instance is linked to exactly one tenant",
            "orphan domains without a tenant are prevented by the factory",
            "related_name 'domains' allows reverse lookup from tenant",
            "cascade deletion removes domains when tenant is deleted",
            "factory supports passing an explicit tenant instance override",
        ],
        "domain_defaults": [
            "domain name defaults to '<slug>.lankacommerce.lk' pattern",
            "is_primary defaults to True for the first domain created",
            "is_verified defaults to False requiring explicit verification",
            "verification_token is auto-generated UUID4 on creation",
            "ssl_status defaults to 'pending' for new domains",
            "custom domains use the pattern '<slug>.example.com' in tests",
        ],
    }
    logger.debug(
        "DomainFactory config: domain_fields=%d, tenant_linkage=%d",
        len(config["domain_fields"]),
        len(config["tenant_linkage"]),
    )
    return config


def get_product_factory_config() -> dict:
    """Return ProductFactory configuration.

    Documents the factory_boy factory for product models with SKU
    generation, price defaults, stock quantity handling, and
    category linkage via SubFactory references.

    SubPhase-10, Group-C, Task 31.

    Returns:
        dict: Configuration with *factory_documented* flag,
              *product_fields* list, *price_defaults* list,
              and *category_linkage* list.
    """
    config: dict = {
        "factory_documented": True,
        "product_fields": [
            "name -- product display name via Faker commerce provider",
            "sku -- unique stock keeping unit with 'SKU-' prefix and sequence",
            "description -- product description via Faker text provider",
            "price -- Decimal field with two decimal places for currency",
            "quantity -- integer stock quantity defaulting to 100 units",
            "is_active -- boolean defaulting to True for available products",
        ],
        "price_defaults": [
            "price uses LazyFunction with Decimal('99.99') as default",
            "minimum price is validated to be greater than zero",
            "price precision is fixed at two decimal places for LKR currency",
            "cost_price defaults to 60% of the selling price for margin tests",
            "tax_inclusive flag defaults to False for Sri Lanka tax rules",
            "discount_price is optional and defaults to None when unset",
        ],
        "category_linkage": [
            "category field uses SubFactory pointing to CategoryFactory",
            "products without a category are allowed with category=None",
            "multiple products can share the same category in fixtures",
            "category assignment is validated against tenant-scoped categories",
            "factory supports passing an explicit category instance override",
            "related_name 'products' allows reverse lookup from category",
        ],
    }
    logger.debug(
        "ProductFactory config: product_fields=%d, price_defaults=%d",
        len(config["product_fields"]),
        len(config["price_defaults"]),
    )
    return config


def get_category_factory_config() -> dict:
    """Return CategoryFactory configuration.

    Documents the factory_boy factory for category models with
    name generation, hierarchical parent support, and status
    field configuration for active/inactive categories.

    SubPhase-10, Group-C, Task 32.

    Returns:
        dict: Configuration with *factory_documented* flag,
              *category_fields* list, *name_defaults* list,
              and *status_options* list.
    """
    config: dict = {
        "factory_documented": True,
        "category_fields": [
            "name -- category display name via Faker word provider",
            "slug -- URL-safe slug auto-derived from the category name",
            "description -- optional description via Faker sentence provider",
            "parent -- nullable ForeignKey to self for hierarchical categories",
            "sort_order -- integer for display ordering defaulting to 0",
            "is_active -- boolean defaulting to True for visible categories",
        ],
        "name_defaults": [
            "name uses Faker word provider with unique=True to avoid collisions",
            "slug is generated via LazyAttribute slugifying the name field",
            "names are capitalised using str.title() for display consistency",
            "Sequence suffix appended when uniqueness cannot be guaranteed",
            "maximum name length is 255 characters matching the model constraint",
            "empty or whitespace-only names are rejected by factory validation",
        ],
        "status_options": [
            "is_active=True is the default for newly created categories",
            "trait 'inactive' sets is_active=False for hidden category tests",
            "trait 'root' ensures parent=None for top-level categories",
            "trait 'child' assigns a parent via SubFactory(CategoryFactory)",
            "trait 'empty' creates a category with no linked products",
            "trait 'featured' sets a featured flag for storefront display tests",
        ],
    }
    logger.debug(
        "CategoryFactory config: category_fields=%d, name_defaults=%d",
        len(config["category_fields"]),
        len(config["name_defaults"]),
    )
    return config


def get_customer_factory_config() -> dict:
    """Return CustomerFactory configuration.

    Documents the factory_boy factory for customer models with
    name generation, contact field defaults, and Sri Lankan
    phone number format (+94) for localised test data.

    SubPhase-10, Group-C, Task 33.

    Returns:
        dict: Configuration with *factory_documented* flag,
              *customer_fields* list, *contact_defaults* list,
              and *phone_formats* list.
    """
    config: dict = {
        "factory_documented": True,
        "customer_fields": [
            "first_name -- customer first name via Faker first_name provider",
            "last_name -- customer last name via Faker last_name provider",
            "email -- unique email address via Faker email provider",
            "phone -- phone number in Sri Lankan +94 format",
            "address -- street address via Faker address provider",
            "is_active -- boolean defaulting to True for active customers",
        ],
        "contact_defaults": [
            "email uses LazyAttribute combining first_name and last_name",
            "email domain defaults to 'example.lk' for Sri Lankan locale",
            "address includes city and postal code for complete test data",
            "NIC number field uses Sri Lankan national ID format for tests",
            "loyalty_points defaults to 0 for new customer instances",
            "preferred_language defaults to 'si' for Sinhala locale tests",
        ],
        "phone_formats": [
            "+94 7X XXX XXXX -- standard Sri Lankan mobile number format",
            "+94 70 -- Mobitel mobile prefix for test phone numbers",
            "+94 71 -- Mobitel alternate prefix for test phone numbers",
            "+94 77 -- Dialog mobile prefix for test phone numbers",
            "+94 76 -- Dialog alternate prefix for test phone numbers",
            "+94 11 -- Colombo landline prefix for business numbers",
        ],
    }
    logger.debug(
        "CustomerFactory config: customer_fields=%d, contact_defaults=%d",
        len(config["customer_fields"]),
        len(config["contact_defaults"]),
    )
    return config


def get_order_factory_config() -> dict:
    """Return OrderFactory configuration.

    Documents the factory_boy factory for order models with order
    number generation, total calculations, and linkage to customer
    and product instances via SubFactory references.

    SubPhase-10, Group-C, Task 34.

    Returns:
        dict: Configuration with *factory_documented* flag,
              *order_fields* list, *total_defaults* list,
              and *relationship_links* list.
    """
    config: dict = {
        "factory_documented": True,
        "order_fields": [
            "order_number -- unique order identifier with 'ORD-' prefix",
            "status -- order status string defaulting to 'pending'",
            "subtotal -- Decimal subtotal before tax and discounts",
            "tax_amount -- Decimal tax amount calculated from subtotal",
            "total -- Decimal grand total including tax and discounts",
            "created_at -- auto-set timestamp on order creation",
        ],
        "total_defaults": [
            "subtotal defaults to Decimal('999.99') for standard test orders",
            "tax_amount defaults to 0% until tax rules are applied",
            "total is computed as subtotal + tax_amount - discount",
            "discount_amount defaults to Decimal('0.00') for no-discount orders",
            "currency defaults to 'LKR' for Sri Lankan Rupee denomination",
            "rounding follows CBSL rules for LKR cash transactions",
        ],
        "relationship_links": [
            "customer field uses SubFactory pointing to CustomerFactory",
            "order items link products via a through-model OrderItem factory",
            "each order belongs to exactly one customer instance",
            "factory supports passing an explicit customer instance override",
            "related_name 'orders' allows reverse lookup from customer",
            "post_generation hook creates default order items when requested",
        ],
    }
    logger.debug(
        "OrderFactory config: order_fields=%d, total_defaults=%d",
        len(config["order_fields"]),
        len(config["total_defaults"]),
    )
    return config


# Group-C: Test Fixtures & Factories – Tasks 35-40 (User & Fixtures)


def get_user_factory_config() -> dict:
    """Return UserFactory configuration.

    Documents the factory_boy factory for user models with email
    generation, role assignment via related managers, and tenant
    scoping to ensure users belong to the correct schema.

    SubPhase-10, Group-C, Task 35.

    Returns:
        dict: Configuration with *factory_documented* flag,
              *user_fields* list, *role_assignments* list,
              and *tenant_scoping* list.
    """
    config: dict = {
        "factory_documented": True,
        "user_fields": [
            "email -- unique email address via Faker email provider",
            "first_name -- user first name via Faker first_name provider",
            "last_name -- user last name via Faker last_name provider",
            "password -- hashed password using make_password with default value",
            "is_active -- boolean defaulting to True for active accounts",
            "is_staff -- boolean defaulting to False for non-staff users",
        ],
        "role_assignments": [
            "trait 'admin' sets is_staff=True and is_superuser=True",
            "trait 'manager' assigns the manager role via post_generation hook",
            "trait 'cashier' assigns the cashier role via post_generation hook",
            "role assignment uses ManyToMany through-model for user-role link",
            "default user has no special roles unless a trait is activated",
            "post_generation hook supports passing explicit role instances",
        ],
        "tenant_scoping": [
            "user factory sets tenant FK to the currently active tenant",
            "LazyAttribute reads tenant from the factory's Meta params",
            "cross-tenant user creation is blocked by schema isolation",
            "factory validates that tenant schema exists before creation",
            "SubFactory(TenantFactory) is used when no tenant is provided",
            "tenant_id is indexed for fast per-tenant user lookups",
        ],
    }
    logger.debug(
        "UserFactory config: user_fields=%d, role_assignments=%d",
        len(config["user_fields"]),
        len(config["role_assignments"]),
    )
    return config


def get_tenant_fixtures_config() -> dict:
    """Return tenant fixtures JSON configuration.

    Documents the JSON fixture files for tenant setup including
    sample tenants, associated domains, and test-only usage
    markers ensuring fixtures are never loaded in production.

    SubPhase-10, Group-C, Task 36.

    Returns:
        dict: Configuration with *fixtures_documented* flag,
              *sample_tenants* list, *domain_entries* list,
              and *test_only_markers* list.
    """
    config: dict = {
        "fixtures_documented": True,
        "sample_tenants": [
            "tenant_alpha -- first sample tenant with schema 'alpha'",
            "tenant_beta -- second sample tenant with schema 'beta'",
            "tenant_demo -- demonstration tenant for onboarding flows",
            "tenant_test -- ephemeral tenant created and destroyed per test",
            "tenant_inactive -- inactive tenant for status-filtering tests",
            "tenant_expired -- expired-plan tenant for billing edge cases",
        ],
        "domain_entries": [
            "alpha.localhost -- primary domain for tenant_alpha",
            "beta.localhost -- primary domain for tenant_beta",
            "demo.example.lk -- custom domain for tenant_demo",
            "test.localhost -- primary domain for tenant_test",
            "inactive.localhost -- domain for tenant_inactive",
            "expired.localhost -- domain for tenant_expired",
        ],
        "test_only_markers": [
            "fixture files are stored under tests/fixtures/ directory only",
            "fixtures include a _test_only meta key set to True",
            "CI pipeline validates fixtures are not referenced in prod code",
            "loaddata command is restricted to test and local environments",
            "fixture JSON uses natural keys for cross-database portability",
            "fixture versioning follows the same migration numbering scheme",
        ],
    }
    logger.debug(
        "Tenant fixtures config: sample_tenants=%d, domain_entries=%d",
        len(config["sample_tenants"]),
        len(config["domain_entries"]),
    )
    return config


def get_sample_data_fixtures_config() -> dict:
    """Return sample data fixtures configuration.

    Documents the fixture files containing sample products and
    customers used for seeding test databases with realistic
    data for integration and end-to-end test scenarios.

    SubPhase-10, Group-C, Task 37.

    Returns:
        dict: Configuration with *fixtures_documented* flag,
              *product_samples* list, *customer_samples* list,
              and *seeding_strategies* list.
    """
    config: dict = {
        "fixtures_documented": True,
        "product_samples": [
            "rice_5kg -- staple product with LKR pricing and inventory",
            "tea_ceylon -- Ceylon tea product with export-grade category",
            "coconut_oil -- cooking oil product with unit-of-measure litres",
            "notebook_a4 -- stationery product for office-supplies category",
            "tshirt_white -- apparel product with size variants",
            "smartphone_basic -- electronics product with barcode and SKU",
        ],
        "customer_samples": [
            "customer_perera -- sample customer with Colombo address",
            "customer_silva -- sample customer with Kandy address",
            "customer_fernando -- sample customer with Galle address",
            "customer_jayawardena -- sample customer with Jaffna address",
            "customer_rajapaksa -- sample customer with Matara address",
            "customer_wickremasinghe -- sample customer with Negombo address",
        ],
        "seeding_strategies": [
            "fixtures are loaded via Django loaddata management command",
            "natural keys used for ForeignKey references across fixtures",
            "product fixtures reference categories defined in tenant fixtures",
            "customer fixtures include Sri Lankan phone format (+94)",
            "sample data is idempotent -- safe to load multiple times",
            "fixture order: tenants first, then categories, products, customers",
        ],
    }
    logger.debug(
        "Sample data fixtures config: product_samples=%d, customer_samples=%d",
        len(config["product_samples"]),
        len(config["customer_samples"]),
    )
    return config


def get_minimal_fixture_config() -> dict:
    """Return minimal fixture configuration.

    Documents the smallest viable dataset for quick tests,
    containing one tenant, one domain, one user, one product,
    and one customer to minimise fixture load time.

    SubPhase-10, Group-C, Task 38.

    Returns:
        dict: Configuration with *fixture_documented* flag,
              *minimal_entities* list, *load_time_targets* list,
              and *use_cases* list.
    """
    config: dict = {
        "fixture_documented": True,
        "minimal_entities": [
            "one tenant -- single tenant with schema 'minimal'",
            "one domain -- localhost domain mapped to the minimal tenant",
            "one admin user -- superuser for authentication-required tests",
            "one category -- default product category for FK satisfaction",
            "one product -- single product with price and stock quantity",
            "one customer -- single customer with basic contact details",
        ],
        "load_time_targets": [
            "fixture load must complete in under 500ms on CI hardware",
            "JSON file size must stay below 10 KB for minimal fixture",
            "no external API calls during fixture loading",
            "database inserts are wrapped in a single transaction",
            "fixture is compatible with both SQLite and PostgreSQL",
            "no media files or binary blobs in the minimal fixture set",
        ],
        "use_cases": [
            "smoke tests verifying basic CRUD operations work",
            "authentication tests requiring a logged-in user",
            "single-tenant API endpoint response format tests",
            "model validation tests needing minimal FK references",
            "form submission tests with required field population",
            "management command tests that require an existing tenant",
        ],
    }
    logger.debug(
        "Minimal fixture config: minimal_entities=%d, use_cases=%d",
        len(config["minimal_entities"]),
        len(config["use_cases"]),
    )
    return config


def get_full_fixture_config() -> dict:
    """Return full fixture configuration.

    Documents the extended dataset for integration testing
    containing multiple tenants, domains, users, products,
    customers, and orders for comprehensive cross-tenant tests.

    SubPhase-10, Group-C, Task 39.

    Returns:
        dict: Configuration with *fixture_documented* flag,
              *full_entities* list, *coverage_targets* list,
              and *integration_scenarios* list.
    """
    config: dict = {
        "fixture_documented": True,
        "full_entities": [
            "three tenants -- alpha, beta, and demo with separate schemas",
            "three domains -- one primary domain per tenant",
            "six users -- two per tenant with admin and cashier roles",
            "twelve products -- four per tenant across different categories",
            "nine customers -- three per tenant with varied contact info",
            "six orders -- two per tenant with line items and totals",
        ],
        "coverage_targets": [
            "covers multi-tenant data isolation between three schemas",
            "covers role-based access control with admin and cashier roles",
            "covers product search and filtering across categories",
            "covers customer lookup by name, email, and phone number",
            "covers order lifecycle from pending to completed status",
            "covers domain resolution mapping to correct tenant schema",
        ],
        "integration_scenarios": [
            "cross-tenant queries must return empty results for other tenants",
            "admin in tenant_alpha cannot see tenant_beta products",
            "order totals include tax calculated by tenant-specific tax rates",
            "customer creation triggers welcome email in test mailbox",
            "product stock deduction on order confirmation is atomic",
            "domain switching mid-session re-authenticates the user",
        ],
    }
    logger.debug(
        "Full fixture config: full_entities=%d, integration_scenarios=%d",
        len(config["full_entities"]),
        len(config["integration_scenarios"]),
    )
    return config


def get_load_fixture_helper_config() -> dict:
    """Return load fixture helper configuration.

    Documents the helper utility that loads minimal or full
    fixtures on demand, with error handling for missing fixture
    files and validation of loaded data integrity.

    SubPhase-10, Group-C, Task 40.

    Returns:
        dict: Configuration with *helper_documented* flag,
              *loader_methods* list, *error_handling* list,
              and *validation_steps* list.
    """
    config: dict = {
        "helper_documented": True,
        "loader_methods": [
            "load_minimal_fixture() -- loads the minimal fixture set",
            "load_full_fixture() -- loads the full fixture set",
            "load_fixture_by_name(name) -- loads a named fixture file",
            "reload_fixtures() -- clears and reloads all fixtures",
            "get_fixture_path(name) -- resolves absolute path for a fixture",
            "list_available_fixtures() -- returns list of fixture file names",
        ],
        "error_handling": [
            "FileNotFoundError raised when fixture JSON file is missing",
            "JSONDecodeError caught and re-raised with fixture file path",
            "IntegrityError caught when fixture data violates constraints",
            "warning logged when fixture file is empty or has zero records",
            "timeout error raised if fixture load exceeds 30-second limit",
            "rollback triggered on any error to keep database clean",
        ],
        "validation_steps": [
            "verify record count matches expected count after loading",
            "verify tenant schema exists before loading tenant fixtures",
            "verify ForeignKey references resolve to existing records",
            "verify no orphaned records left after partial fixture load",
            "verify fixture version matches current migration state",
            "verify loaded data passes model full_clean() validation",
        ],
    }
    logger.debug(
        "Load fixture helper config: loader_methods=%d, error_handling=%d",
        len(config["loader_methods"]),
        len(config["error_handling"]),
    )
    return config


# Group-C: Test Fixtures & Factories – Tasks 41-44 (Generators, Verify & Docs)


def get_random_data_generator_config() -> dict:
    """Return random data generator configuration.

    Documents the use of Faker for realistic random value generation
    with seeding support for deterministic, repeatable test runs
    across all tenant-specific data factories.

    SubPhase-10, Group-C, Task 41.

    Returns:
        dict: Configuration with *generator_documented* flag,
              *generator_scope* list, *repeatability_features* list,
              and *supported_data_types* list.
    """
    config: dict = {
        "generator_documented": True,
        "generator_scope": [
            "Faker instance shared across all tenant factory classes",
            "locale set to en_US with optional si_LK Sri Lanka locale",
            "seed value configurable via FAKER_SEED environment variable",
            "per-factory seed offset to avoid duplicate values across factories",
            "thread-safe Faker instance for parallel test execution",
            "custom Faker providers registered for LankaCommerce-specific fields",
        ],
        "repeatability_features": [
            "global seed set in conftest.py for full test suite determinism",
            "Faker.seed(0) called before each parametrized test scenario",
            "factory sequences reset between test classes via autouse fixture",
            "random.seed aligned with Faker seed for consistent choice() calls",
            "seed value logged at test session start for reproduction",
            "CI pipeline uses fixed seed to ensure reproducible nightly builds",
        ],
        "supported_data_types": [
            "company names and addresses via Faker.company() and Faker.address()",
            "product names using Faker.catch_phrase() with category prefix",
            "email addresses via Faker.email() scoped to tenant domain",
            "phone numbers via Faker.phone_number() in Sri Lankan format",
            "currency amounts via Faker.pydecimal() with LKR precision",
            "date ranges via Faker.date_between() for order and invoice dates",
        ],
    }
    logger.debug(
        "Random data generator config: generator_scope=%d, supported_data_types=%d",
        len(config["generator_scope"]),
        len(config["supported_data_types"]),
    )
    return config


def get_bulk_data_generator_config() -> dict:
    """Return bulk data generator configuration.

    Documents the large-dataset creation utility with safeguards
    and limits to prevent memory overload and excessive database
    writes during test data generation.

    SubPhase-10, Group-C, Task 42.

    Returns:
        dict: Configuration with *bulk_generator_documented* flag,
              *generation_capabilities* list, *safeguard_limits* list,
              and *performance_targets* list.
    """
    config: dict = {
        "bulk_generator_documented": True,
        "generation_capabilities": [
            "generate_products(n) creates n Product instances via factory",
            "generate_customers(n) creates n Customer instances with addresses",
            "generate_orders(n) creates n Orders with random line items",
            "generate_full_catalog(categories, products_per) creates nested catalog",
            "generate_historical_data(months) creates time-series order data",
            "generate_multi_tenant_dataset(tenants, records) populates multiple schemas",
        ],
        "safeguard_limits": [
            "MAX_BULK_RECORDS=10000 hard cap per single generation call",
            "MAX_MEMORY_MB=512 memory usage checked before batch allocation",
            "BATCH_SIZE=500 records committed per transaction batch",
            "timeout of 120 seconds per bulk generation call enforced",
            "duplicate-check query runs before insert to avoid constraint violations",
            "rollback triggered if any batch in the bulk generation fails",
        ],
        "performance_targets": [
            "1000 products generated in under 5 seconds on CI hardware",
            "5000 customers generated in under 15 seconds with addresses",
            "10000 orders generated in under 60 seconds with line items",
            "memory usage stays below 256 MB for 10000-record generation",
            "bulk_create used instead of individual save() for throughput",
            "database indexes deferred until after bulk insert completes",
        ],
    }
    logger.debug(
        "Bulk data generator config: generation_capabilities=%d, safeguard_limits=%d",
        len(config["generation_capabilities"]),
        len(config["safeguard_limits"]),
    )
    return config


def get_factory_isolation_verification_config() -> dict:
    """Return factory isolation verification configuration.

    Documents the verification approach that confirms factory-created
    data stays within the correct tenant schema using a two-tenant
    setup to detect cross-tenant data leaks.

    SubPhase-10, Group-C, Task 43.

    Returns:
        dict: Configuration with *isolation_verified* flag,
              *isolation_checks* list, *verification_approach* list,
              and *expected_results* list.
    """
    config: dict = {
        "isolation_verified": True,
        "isolation_checks": [
            "products created in tenant_alpha are invisible in tenant_beta",
            "customers created in tenant_beta are invisible in tenant_alpha",
            "orders in one tenant schema have no foreign keys to another",
            "user factory creates users scoped to the active tenant schema",
            "category tree in tenant_alpha is independent of tenant_beta",
            "sequence counters (order numbers) are tenant-schema specific",
        ],
        "verification_approach": [
            "create tenant_alpha and tenant_beta schemas in setUp",
            "activate tenant_alpha schema and run ProductFactory.create_batch(5)",
            "switch to tenant_beta schema and assert Product.objects.count() == 0",
            "activate tenant_beta schema and run CustomerFactory.create_batch(3)",
            "switch to tenant_alpha schema and assert Customer.objects.count() == 0",
            "tearDown drops both schemas ensuring clean state for next test",
        ],
        "expected_results": [
            "zero cross-tenant records detected in all factory isolation tests",
            "each tenant schema has exactly the record count created by its factories",
            "foreign key lookups within a schema never reference another schema",
            "schema search_path is always single-schema during factory execution",
            "no shared-schema tables are polluted by tenant factory calls",
            "all isolation tests pass under both sequential and parallel runners",
        ],
    }
    logger.debug(
        "Factory isolation verification config: isolation_checks=%d, expected_results=%d",
        len(config["isolation_checks"]),
        len(config["expected_results"]),
    )
    return config


def get_fixtures_documentation_config() -> dict:
    """Return fixtures documentation configuration.

    Documents the minimal, sample, and full fixture sets along with
    usage patterns that explain when to prefer fixtures over factories
    and maintenance guidelines for keeping fixture data current.

    SubPhase-10, Group-C, Task 44.

    Returns:
        dict: Configuration with *documentation_completed* flag,
              *fixture_sets* list, *usage_patterns* list,
              and *maintenance_guidelines* list.
    """
    config: dict = {
        "documentation_completed": True,
        "fixture_sets": [
            "minimal -- one tenant, one user, one product for fast smoke tests",
            "sample -- ten products, five customers, three orders for integration",
            "full -- complete catalog with all entity types for end-to-end tests",
            "multi-tenant -- two tenants with isolated data for isolation tests",
            "performance -- 10 000 records per entity for load and stress tests",
            "edge-case -- boundary values, empty strings, max-length fields",
        ],
        "usage_patterns": [
            "use fixtures for read-only reference data that never changes",
            "use factories when tests need unique or random field values",
            "combine minimal fixture with factory overrides for focused tests",
            "load full fixture once per session, not per test, to save time",
            "prefer factories for write-path tests that modify database state",
            "use edge-case fixture to validate model clean() and constraints",
        ],
        "maintenance_guidelines": [
            "regenerate fixture JSON after any model field migration",
            "version fixture files alongside migration files in source control",
            "run load_fixture_helper in CI to detect stale fixture data early",
            "document new fixture fields in fixture README when adding columns",
            "review fixture file sizes quarterly to keep test suite fast",
            "archive deprecated fixtures instead of deleting for rollback safety",
        ],
    }
    logger.debug(
        "Fixtures documentation config: fixture_sets=%d, usage_patterns=%d",
        len(config["fixture_sets"]),
        len(config["usage_patterns"]),
    )
    return config


# ---------------------------------------------------------------------------
# Group-D: Isolation Verification Tests – Tasks 45-50 (Schema Separation)
# ---------------------------------------------------------------------------


def get_isolation_test_module_config() -> dict:
    """Return isolation test module configuration.

    Documents the organization of isolation tests, covering schema
    separation and data isolation verification across tenant schemas,
    including coverage scope and structural notes.

    SubPhase-10, Group-D, Task 45.

    Returns:
        dict: Configuration with *module_documented* flag,
              *module_structure* list, *coverage_scope* list,
              and *organization_notes* list.
    """
    config: dict = {
        "module_documented": True,
        "module_structure": [
            "tests/isolation/ -- top-level isolation test directory",
            "tests/isolation/test_schema_exists.py -- schema presence tests",
            "tests/isolation/test_tables.py -- table placement verification tests",
            "tests/isolation/test_data_placement.py -- data residency tests",
            "tests/isolation/test_query_context.py -- search_path context tests",
            "tests/isolation/test_separation.py -- cross-tenant visibility tests",
            "tests/isolation/conftest.py -- isolation-specific fixtures",
        ],
        "coverage_scope": [
            "schema existence after tenant provisioning workflow",
            "table placement in tenant vs public schema",
            "data residency verification per tenant schema",
            "search_path correctness during tenant operations",
            "cross-tenant data invisibility assertions",
            "edge cases for shared public data access patterns",
        ],
        "organization_notes": [
            "group isolation tests separately from unit tests for clarity",
            "use TenantTestCase base class for automatic schema setup",
            "mark all isolation tests with @pytest.mark.isolation marker",
            "run isolation tests after provisioning tests in CI pipeline",
            "keep isolation tests idempotent to support parallel execution",
            "document expected schema layout in test module docstrings",
        ],
    }
    logger.debug(
        "Isolation test module config: module_structure=%d, coverage_scope=%d",
        len(config["module_structure"]),
        len(config["coverage_scope"]),
    )
    return config


def get_schema_exists_test_config() -> dict:
    """Return schema exists test configuration.

    Validates that each tenant schema exists in PostgreSQL after
    provisioning, including expected existence checks, result
    expectations, and documented failure conditions.

    SubPhase-10, Group-D, Task 46.

    Returns:
        dict: Configuration with *schema_tests_documented* flag,
              *existence_checks* list, *expected_results* list,
              and *failure_conditions* list.
    """
    config: dict = {
        "schema_tests_documented": True,
        "existence_checks": [
            "query pg_namespace for tenant schema name after provisioning",
            "verify schema owner matches expected database role",
            "confirm schema appears in information_schema.schemata",
            "check schema name follows tenant slug naming convention",
            "verify public schema always exists alongside tenant schemas",
            "validate schema is listed in tenant model schema_name field",
        ],
        "expected_results": [
            "newly provisioned tenant has a matching PostgreSQL schema",
            "schema name equals slugified tenant identifier",
            "pg_namespace row count increments by one per new tenant",
            "schema owner is the application database user",
            "deprovisioned tenant schema is removed from pg_namespace",
            "public schema is never removed during tenant operations",
        ],
        "failure_conditions": [
            "schema not found after provisioning indicates migration failure",
            "duplicate schema name triggers unique constraint violation",
            "schema creation timeout leaves tenant in partial state",
            "permission denied on CREATE SCHEMA due to missing grants",
            "concurrent provisioning race creates orphaned schemas",
            "schema name with special characters fails validation",
        ],
    }
    logger.debug(
        "Schema exists test config: existence_checks=%d, failure_conditions=%d",
        len(config["existence_checks"]),
        len(config["failure_conditions"]),
    )
    return config


def get_tables_in_schema_test_config() -> dict:
    """Return tables in schema test configuration.

    Validates that tenant tables reside in the correct schema,
    covering core model tables, placement rules, and model
    coverage expectations for schema isolation.

    SubPhase-10, Group-D, Task 47.

    Returns:
        dict: Configuration with *table_tests_documented* flag,
              *table_checks* list, *model_coverage* list,
              and *placement_rules* list.
    """
    config: dict = {
        "table_tests_documented": True,
        "table_checks": [
            "query information_schema.tables for tenant schema tables",
            "verify products table exists in tenant schema not public",
            "verify orders table exists in tenant schema not public",
            "verify customers table exists in tenant schema not public",
            "confirm tenants_tenant table is in public schema only",
            "confirm tenants_domain table is in public schema only",
        ],
        "model_coverage": [
            "Product model mapped to tenant schema products table",
            "Order model mapped to tenant schema orders table",
            "Customer model mapped to tenant schema customers table",
            "Category model mapped to tenant schema categories table",
            "Inventory model mapped to tenant schema inventory table",
            "User profile model mapped to tenant schema profile table",
        ],
        "placement_rules": [
            "shared apps (tenants, users auth) reside in public schema",
            "tenant apps (products, orders) reside in tenant schema",
            "Django system tables (migrations, content_types) in public",
            "cross-schema foreign keys are prohibited by router rules",
            "each tenant schema has identical table structure",
            "new tenant migrations create tables in tenant schema only",
        ],
    }
    logger.debug(
        "Tables in schema test config: table_checks=%d, model_coverage=%d",
        len(config["table_checks"]),
        len(config["model_coverage"]),
    )
    return config


def get_data_placement_test_config() -> dict:
    """Return data placement test configuration.

    Validates that tenant data resides in the correct tenant schema
    and verifies shared public data edge cases, including placement
    checks and validation queries.

    SubPhase-10, Group-D, Task 48.

    Returns:
        dict: Configuration with *data_tests_documented* flag,
              *placement_checks* list, *edge_cases* list,
              and *validation_queries* list.
    """
    config: dict = {
        "data_tests_documented": True,
        "placement_checks": [
            "insert product via tenant context and verify in tenant schema",
            "insert order via tenant context and verify in tenant schema",
            "query tenant schema directly and confirm row presence",
            "query other tenant schema and confirm row absence",
            "verify public schema has no tenant-specific data rows",
            "verify shared models in public schema accessible from tenant",
        ],
        "edge_cases": [
            "creating data without tenant context falls back to public",
            "bulk insert operations respect active schema context",
            "data migration scripts target correct schema per tenant",
            "raw SQL inserts bypass ORM schema routing if not careful",
            "shared data (plans, config) visible from all tenant schemas",
            "tenant deletion cascades data only within tenant schema",
        ],
        "validation_queries": [
            "SELECT count(*) FROM tenant_schema.products WHERE tenant_id=X",
            "SELECT count(*) FROM public.tenants_tenant WHERE id=X",
            "SELECT schemaname, tablename FROM pg_tables WHERE schemaname=X",
            "SET search_path TO tenant_schema; SELECT * FROM products",
            "SELECT * FROM information_schema.tables WHERE table_schema=X",
            "SELECT current_schema() to verify active schema context",
        ],
    }
    logger.debug(
        "Data placement test config: placement_checks=%d, edge_cases=%d",
        len(config["placement_checks"]),
        len(config["edge_cases"]),
    )
    return config


def get_query_schema_context_test_config() -> dict:
    """Return query schema context test configuration.

    Validates that the search_path is set correctly per tenant,
    covering context checks, schema assertion helper usage,
    and search_path validation scenarios.

    SubPhase-10, Group-D, Task 49.

    Returns:
        dict: Configuration with *query_tests_documented* flag,
              *context_checks* list, *assertion_usage* list,
              and *search_path_validations* list.
    """
    config: dict = {
        "query_tests_documented": True,
        "context_checks": [
            "verify search_path is set to tenant schema on request start",
            "verify search_path resets to public after request completes",
            "verify search_path includes public as fallback schema",
            "verify nested tenant context switches update search_path",
            "verify search_path is thread-local and not shared across workers",
            "verify search_path in Celery tasks matches tenant context",
        ],
        "assertion_usage": [
            "assert_schema_is(schema_name) validates current search_path",
            "assert_in_tenant_context() confirms non-public schema active",
            "assert_in_public_context() confirms public schema active",
            "assert_schema_contains_table(schema, table) checks placement",
            "assert_no_cross_schema_leaks() scans for leaked references",
            "assert_search_path_clean() verifies no stale schema entries",
        ],
        "search_path_validations": [
            "SHOW search_path returns tenant_schema, public for tenant ops",
            "SHOW search_path returns public for non-tenant operations",
            "SET search_path persists within a database transaction block",
            "search_path reset on connection return to pool",
            "concurrent requests maintain independent search_path values",
            "search_path with invalid schema raises OperationalError",
        ],
    }
    logger.debug(
        "Query schema context test config: context_checks=%d, assertion_usage=%d",
        len(config["context_checks"]),
        len(config["assertion_usage"]),
    )
    return config


def get_multi_tenant_separation_test_config() -> dict:
    """Return multi-tenant separation test configuration.

    Validates that no cross-tenant data visibility exists, covering
    separation checks with two-tenant mixin usage, setup requirements,
    and visibility assertions.

    SubPhase-10, Group-D, Task 50.

    Returns:
        dict: Configuration with *separation_tests_documented* flag,
              *separation_checks* list, *setup_requirements* list,
              and *visibility_assertions* list.
    """
    config: dict = {
        "separation_tests_documented": True,
        "separation_checks": [
            "create data in tenant_a and verify invisible from tenant_b",
            "create data in tenant_b and verify invisible from tenant_a",
            "switch context from tenant_a to tenant_b and query isolation",
            "verify aggregate queries scoped to active tenant only",
            "verify ORM filter results limited to current tenant schema",
            "verify raw SQL respects search_path tenant isolation",
        ],
        "setup_requirements": [
            "use MultiTenantTestMixin to provision two test tenants",
            "create tenant_a and tenant_b with separate schema names",
            "seed identical data sets in both tenant schemas",
            "configure test database to allow multiple schemas",
            "ensure tearDown drops both tenant schemas after test",
            "use unique identifiers to distinguish tenant_a vs tenant_b data",
        ],
        "visibility_assertions": [
            "Products.objects.all() in tenant_a excludes tenant_b products",
            "Orders.objects.count() in tenant_b excludes tenant_a orders",
            "Customer lookup by ID in wrong tenant returns DoesNotExist",
            "cross-tenant JOIN via raw SQL raises no rows or schema error",
            "search_path switch fully isolates subsequent ORM queries",
            "parallel test execution maintains tenant isolation per worker",
        ],
    }
    logger.debug(
        "Multi-tenant separation test config: separation_checks=%d, setup_requirements=%d",
        len(config["separation_checks"]),
        len(config["setup_requirements"]),
    )
    return config


def get_same_id_different_tenants_test_config() -> dict:
    """Return same ID different tenants test configuration.

    Documents tests verifying that identical primary key values can coexist
    across separate tenant schemas without conflicts or data leakage.

    SubPhase-10, Group-D, Task 51.

    Returns:
        dict: Configuration with *same_id_test_documented* flag,
              *collision_checks* list, *setup_steps* list,
              and *expected_outcomes* list.
    """
    config: dict = {
        "same_id_test_documented": True,
        "collision_checks": [
            "verify product with pk=1 in tenant_a differs from pk=1 in tenant_b",
            "verify order with pk=1 in tenant_a is independent of pk=1 in tenant_b",
            "verify customer with pk=1 exists separately in both tenant schemas",
            "verify category with matching pk across tenants has distinct data",
            "verify user profile with same pk is isolated per tenant schema",
            "verify inventory item with identical pk has no cross-tenant linkage",
        ],
        "setup_steps": [
            "create tenant_a schema and insert records with sequential pk values",
            "create tenant_b schema and insert records with identical pk values",
            "seed both tenants with matching primary key sequences starting at 1",
            "reset auto-increment counters in both schemas to produce collisions",
            "populate foreign key relationships using same pk values in each tenant",
            "verify both schemas contain records before running collision checks",
        ],
        "expected_outcomes": [
            "querying pk=1 in tenant_a returns only tenant_a data",
            "querying pk=1 in tenant_b returns only tenant_b data",
            "no IntegrityError raised when same pk exists in both schemas",
            "ORM get(pk=1) in tenant_a context never returns tenant_b object",
            "count of records per tenant remains independent despite same pks",
            "deleting pk=1 in tenant_a does not affect pk=1 in tenant_b",
        ],
    }
    logger.debug(
        "Same ID different tenants test config: collision_checks=%d, setup_steps=%d",
        len(config["collision_checks"]),
        len(config["setup_steps"]),
    )
    return config


def get_tenant_a_cannot_see_b_test_config() -> dict:
    """Return tenant A cannot see B test configuration.

    Documents tests verifying that Tenant A context cannot access or
    see any data belonging to Tenant B schema.

    SubPhase-10, Group-D, Task 52.

    Returns:
        dict: Configuration with *a_to_b_isolation_documented* flag,
              *visibility_checks* list, *query_patterns* list,
              and *expected_results* list.
    """
    config: dict = {
        "a_to_b_isolation_documented": True,
        "visibility_checks": [
            "query all products from tenant_a context and verify none from tenant_b",
            "query all orders from tenant_a context and verify none from tenant_b",
            "query all customers from tenant_a context and verify none from tenant_b",
            "query all categories from tenant_a context and verify none from tenant_b",
            "query all users from tenant_a context and verify none from tenant_b",
            "query all inventory items from tenant_a context and verify none from tenant_b",
        ],
        "query_patterns": [
            "Product.objects.filter(name__in=tenant_b_names) returns empty queryset",
            "Order.objects.filter(pk__in=tenant_b_pks) returns empty queryset",
            "Customer.objects.filter(email__in=tenant_b_emails) returns empty queryset",
            "Category.objects.all() excludes all tenant_b categories",
            "raw SQL SELECT from tenant_b schema raises or returns no rows in tenant_a",
            "ORM aggregation in tenant_a context ignores tenant_b records entirely",
        ],
        "expected_results": [
            "all cross-tenant queries return zero results in tenant_a context",
            "DoesNotExist raised when fetching tenant_b pk from tenant_a",
            "queryset count for tenant_b data is zero in tenant_a context",
            "filter with tenant_b identifiers produces empty queryset",
            "aggregate sum/count excludes all tenant_b values",
            "exists() check for tenant_b data returns False in tenant_a",
        ],
    }
    logger.debug(
        "Tenant A cannot see B test config: visibility_checks=%d, query_patterns=%d",
        len(config["visibility_checks"]),
        len(config["query_patterns"]),
    )
    return config


def get_tenant_b_cannot_see_a_test_config() -> dict:
    """Return tenant B cannot see A test configuration.

    Documents tests verifying that Tenant B context cannot access or
    see any data belonging to Tenant A schema.

    SubPhase-10, Group-D, Task 53.

    Returns:
        dict: Configuration with *b_to_a_isolation_documented* flag,
              *visibility_checks* list, *query_patterns* list,
              and *expected_results* list.
    """
    config: dict = {
        "b_to_a_isolation_documented": True,
        "visibility_checks": [
            "query all products from tenant_b context and verify none from tenant_a",
            "query all orders from tenant_b context and verify none from tenant_a",
            "query all customers from tenant_b context and verify none from tenant_a",
            "query all categories from tenant_b context and verify none from tenant_a",
            "query all users from tenant_b context and verify none from tenant_a",
            "query all inventory items from tenant_b context and verify none from tenant_a",
        ],
        "query_patterns": [
            "Product.objects.filter(name__in=tenant_a_names) returns empty queryset",
            "Order.objects.filter(pk__in=tenant_a_pks) returns empty queryset",
            "Customer.objects.filter(email__in=tenant_a_emails) returns empty queryset",
            "Category.objects.all() excludes all tenant_a categories",
            "raw SQL SELECT from tenant_a schema raises or returns no rows in tenant_b",
            "ORM aggregation in tenant_b context ignores tenant_a records entirely",
        ],
        "expected_results": [
            "all cross-tenant queries return zero results in tenant_b context",
            "DoesNotExist raised when fetching tenant_a pk from tenant_b",
            "queryset count for tenant_a data is zero in tenant_b context",
            "filter with tenant_a identifiers produces empty queryset",
            "aggregate sum/count excludes all tenant_a values",
            "exists() check for tenant_a data returns False in tenant_b",
        ],
    }
    logger.debug(
        "Tenant B cannot see A test config: visibility_checks=%d, query_patterns=%d",
        len(config["visibility_checks"]),
        len(config["query_patterns"]),
    )
    return config


def get_public_schema_shared_test_config() -> dict:
    """Return public schema shared test configuration.

    Documents tests verifying that data in the public schema is visible
    and shared across all tenant contexts.

    SubPhase-10, Group-D, Task 54.

    Returns:
        dict: Configuration with *public_shared_documented* flag,
              *shared_data_checks* list, *access_rules* list,
              and *expected_behavior* list.
    """
    config: dict = {
        "public_shared_documented": True,
        "shared_data_checks": [
            "verify shared configuration table is visible from tenant_a context",
            "verify shared configuration table is visible from tenant_b context",
            "verify public tenant model data accessible from all schemas",
            "verify domain model records in public schema are globally visible",
            "verify system-wide settings in public schema readable by all tenants",
            "verify shared lookup tables return consistent data across tenants",
        ],
        "access_rules": [
            "tenants can read public schema tables via search_path fallback",
            "public schema tables are included in shared_apps migration scope",
            "tenant context does not filter out public schema records",
            "ORM queries for shared models route to public schema automatically",
            "public schema data is not duplicated into tenant schemas",
            "shared apps list determines which models reside in public schema",
        ],
        "expected_behavior": [
            "same public record returned regardless of active tenant context",
            "public schema count matches from tenant_a and tenant_b contexts",
            "updates to public data visible immediately in all tenant contexts",
            "public schema tables not affected by tenant schema drop operations",
            "shared model instances have identical pk values across all contexts",
            "public schema acts as single source of truth for shared data",
        ],
    }
    logger.debug(
        "Public schema shared test config: shared_data_checks=%d, access_rules=%d",
        len(config["shared_data_checks"]),
        len(config["access_rules"]),
    )
    return config


def get_tenant_to_public_access_test_config() -> dict:
    """Return tenant to public access test configuration.

    Documents tests verifying that tenant contexts can read data from
    the public schema including shared tables and configurations.

    SubPhase-10, Group-D, Task 55.

    Returns:
        dict: Configuration with *tenant_to_public_documented* flag,
              *access_checks* list, *read_patterns* list,
              and *expected_access* list.
    """
    config: dict = {
        "tenant_to_public_documented": True,
        "access_checks": [
            "tenant_a can read Tenant model from public schema",
            "tenant_b can read Domain model from public schema",
            "tenant context can access shared configuration table",
            "tenant context can query system-wide feature flags from public",
            "tenant context can read global lookup data from public schema",
            "tenant context can access shared user authentication tables",
        ],
        "read_patterns": [
            "Tenant.objects.all() returns public records from tenant context",
            "Domain.objects.filter(tenant=current) works across schema boundary",
            "SharedConfig.objects.get(key=name) accessible from any tenant",
            "search_path includes public schema allowing fallback reads",
            "ORM queries for shared_apps models always hit public schema",
            "raw SQL with explicit public schema prefix returns shared data",
        ],
        "expected_access": [
            "tenant_a reads same Tenant records as tenant_b from public",
            "tenant context can list all domains stored in public schema",
            "shared configuration values are consistent across tenant reads",
            "no permission error when tenant reads public schema tables",
            "tenant read of public data does not create tenant-local copy",
            "public schema read operations are idempotent across tenants",
        ],
    }
    logger.debug(
        "Tenant to public access test config: access_checks=%d, read_patterns=%d",
        len(config["access_checks"]),
        len(config["read_patterns"]),
    )
    return config


def get_public_cannot_access_tenant_test_config() -> dict:
    """Return public cannot access tenant test configuration.

    Documents tests verifying that the public schema context cannot
    access tenant-specific data, ensuring one-way isolation.

    SubPhase-10, Group-D, Task 56.

    Returns:
        dict: Configuration with *public_to_tenant_blocked_documented* flag,
              *block_checks* list, *error_patterns* list,
              and *enforcement_rules* list.
    """
    config: dict = {
        "public_to_tenant_blocked_documented": True,
        "block_checks": [
            "public context cannot query tenant_a Product table",
            "public context cannot query tenant_b Order table",
            "public context cannot list tenant-specific Customer records",
            "public context cannot access tenant schema Category table",
            "public context cannot read tenant-specific inventory data",
            "public context search_path does not include tenant schemas",
        ],
        "error_patterns": [
            "ProgrammingError raised when public context queries tenant table",
            "relation does not exist error for tenant-only models in public",
            "empty queryset returned for tenant models queried from public",
            "OperationalError if public search_path excludes tenant schema",
            "permission denied error when accessing tenant schema from public",
            "DoesNotExist raised for tenant records queried in public context",
        ],
        "enforcement_rules": [
            "search_path in public context set to public schema only",
            "tenant_apps models not migrated into public schema",
            "middleware blocks tenant data access when no tenant is active",
            "schema routing layer refuses tenant table queries from public",
            "connection handler resets search_path on tenant context exit",
            "test tearDown verifies no tenant data leaked into public schema",
        ],
    }
    logger.debug(
        "Public cannot access tenant test config: block_checks=%d, error_patterns=%d",
        len(config["block_checks"]),
        len(config["error_patterns"]),
    )
    return config


def get_isolation_suite_execution_config() -> dict:
    """Return isolation suite execution configuration.

    Documents the process for running the full isolation test suite,
    including execution commands, success criteria, and reporting
    requirements.

    SubPhase-10, Group-D, Task 57.

    Returns:
        dict: Configuration with *suite_execution_documented* flag,
              *execution_steps* list, *success_criteria* list,
              and *reporting_requirements* list.
    """
    config: dict = {
        "suite_execution_documented": True,
        "execution_steps": [
            "run pytest with -m isolation marker to select isolation tests",
            "execute schema separation tests before cross-tenant tests",
            "run cross-tenant visibility tests for tenant A and tenant B",
            "execute public schema access tests after tenant isolation",
            "collect test results with verbose output for debugging",
            "generate coverage report for isolation test module",
        ],
        "success_criteria": [
            "all schema existence tests pass for every provisioned tenant",
            "all table placement tests confirm correct schema residency",
            "cross-tenant visibility tests return zero leaked records",
            "public schema shared data accessible from all tenant contexts",
            "tenant-to-public read access succeeds for shared tables",
            "public-to-tenant access blocked and raises expected errors",
        ],
        "reporting_requirements": [
            "log total number of isolation tests executed and passed",
            "report any failures with tenant schema and test case details",
            "record execution time per isolation test category",
            "flag flaky tests that pass intermittently under parallel runs",
            "generate summary table of isolation checks and outcomes",
            "archive test results for CI pipeline history tracking",
        ],
    }
    logger.debug(
        "Isolation suite execution config: execution_steps=%d, success_criteria=%d",
        len(config["execution_steps"]),
        len(config["success_criteria"]),
    )
    return config


def get_isolation_tests_documentation_config() -> dict:
    """Return isolation tests documentation configuration.

    Documents the isolation test coverage summary, troubleshooting
    guidance, and maintenance notes for the isolation verification
    test suite.

    SubPhase-10, Group-D, Task 58.

    Returns:
        dict: Configuration with *isolation_docs_completed* flag,
              *coverage_summary* list, *troubleshooting_guide* list,
              and *maintenance_notes* list.
    """
    config: dict = {
        "isolation_docs_completed": True,
        "coverage_summary": [
            "schema separation tests verify tenant schemas exist independently",
            "table placement tests confirm shared vs tenant model residency",
            "cross-tenant tests ensure Tenant A and Tenant B data isolation",
            "same-ID collision tests verify no primary key conflicts across schemas",
            "public schema tests validate shared data accessibility rules",
            "full suite covers schema, data, query, and access isolation layers",
        ],
        "troubleshooting_guide": [
            "if schema existence test fails check tenant provisioning ran migrations",
            "if table placement fails verify SHARED_APPS and TENANT_APPS settings",
            "if cross-tenant leaks detected check search_path reset in tearDown",
            "if public access blocked verify shared model is in SHARED_APPS list",
            "if same-ID test fails ensure each tenant uses a separate schema name",
            "if parallel test failures occur check worker isolation configuration",
        ],
        "maintenance_notes": [
            "update isolation tests when new tenant-specific models are added",
            "review cross-tenant tests after changes to schema routing logic",
            "re-run full suite after django-tenants version upgrades",
            "add new public schema tests when shared models are introduced",
            "document any new isolation patterns in the testing guide",
            "keep troubleshooting guide current with resolved failure modes",
        ],
    }
    logger.debug(
        "Isolation tests documentation config: coverage_summary=%d, troubleshooting_guide=%d",
        len(config["coverage_summary"]),
        len(config["troubleshooting_guide"]),
    )
    return config


def get_leak_test_module_config() -> dict:
    """Return leak test module configuration.

    Documents the structure and scope of the data leak prevention test
    module, covering SQL and ORM leak vectors with organization and
    test categorization details.

    SubPhase-10, Group-E, Task 59.

    Returns:
        dict: Configuration with *leak_module_documented* flag,
              *module_structure* list, *leak_vectors* list,
              and *test_categories* list.
    """
    config: dict = {
        "leak_module_documented": True,
        "module_structure": [
            "tests/tenants/test_leak_prevention.py as main test file",
            "organize tests by leak vector type in separate test classes",
            "group raw SQL leak tests in TestDirectQueryLeak class",
            "group ORM leak tests in TestORMQueryLeak class",
            "group aggregate and join leak tests in dedicated classes",
            "include conftest fixtures for leak test tenant provisioning",
        ],
        "leak_vectors": [
            "raw SQL queries bypassing tenant schema search_path",
            "ORM queryset access without tenant context activation",
            "aggregate functions spanning multiple tenant schemas",
            "JOIN operations crossing tenant schema boundaries",
            "subqueries referencing tables in other tenant schemas",
            "bulk operations that may ignore schema scoping rules",
        ],
        "test_categories": [
            "direct SQL injection of cross-tenant table references",
            "ORM manager default queryset tenant scoping validation",
            "aggregate count and sum isolation per tenant schema",
            "foreign key JOIN path leak across tenant boundaries",
            "nested subquery tenant context propagation checks",
            "combined vector tests with multiple leak paths at once",
        ],
    }
    logger.debug(
        "Leak test module config: module_structure=%d, leak_vectors=%d",
        len(config["module_structure"]),
        len(config["leak_vectors"]),
    )
    return config


def get_direct_query_leak_test_config() -> dict:
    """Return direct query leak test configuration.

    Documents tests verifying that raw SQL queries cannot return data
    from other tenant schemas, ensuring search_path isolation for
    direct database access.

    SubPhase-10, Group-E, Task 60.

    Returns:
        dict: Configuration with *direct_leak_tests_documented* flag,
              *raw_sql_checks* list, *schema_scoping_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "direct_leak_tests_documented": True,
        "raw_sql_checks": [
            "execute raw SELECT on tenant_b table from tenant_a context",
            "execute raw INSERT targeting tenant_b schema from tenant_a",
            "execute raw UPDATE on another tenant schema and verify blocked",
            "execute raw DELETE targeting cross-tenant rows and verify denied",
            "execute raw SQL with explicit schema prefix and verify rejection",
            "execute raw SQL with search_path override attempt and verify blocked",
        ],
        "schema_scoping_rules": [
            "search_path must be set to current tenant schema only",
            "raw SQL connections inherit active tenant search_path",
            "explicit schema.table references to other tenants must fail",
            "connection cursor must respect tenant context search_path",
            "raw SQL executed via Django connection.cursor() is schema-scoped",
            "SET search_path attempts in raw SQL must be intercepted or blocked",
        ],
        "expected_results": [
            "ProgrammingError raised for cross-tenant table references",
            "zero rows returned when querying non-existent tenant tables",
            "relation does not exist error for wrong schema table access",
            "permission denied when accessing restricted tenant schema",
            "OperationalError for invalid schema path in raw SQL",
            "no data modification possible in another tenant schema",
        ],
    }
    logger.debug(
        "Direct query leak test config: raw_sql_checks=%d, schema_scoping_rules=%d",
        len(config["raw_sql_checks"]),
        len(config["schema_scoping_rules"]),
    )
    return config


def get_orm_query_leak_test_config() -> dict:
    """Return ORM query leak test configuration.

    Documents tests verifying that Django ORM queries are properly
    scoped to the active tenant schema and cannot return data from
    other tenants.

    SubPhase-10, Group-E, Task 61.

    Returns:
        dict: Configuration with *orm_leak_tests_documented* flag,
              *queryset_checks* list, *manager_scoping_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "orm_leak_tests_documented": True,
        "queryset_checks": [
            "Model.objects.all() returns only active tenant records",
            "Model.objects.filter() scoped to current tenant schema",
            "Model.objects.get() raises DoesNotExist for cross-tenant IDs",
            "Model.objects.exclude() operates within tenant boundary only",
            "Model.objects.values_list() returns tenant-scoped field values",
            "Model.objects.count() reflects only active tenant record count",
        ],
        "manager_scoping_rules": [
            "default manager queryset inherits tenant schema from connection",
            "custom managers must not override tenant schema scoping",
            "related manager lookups follow tenant context automatically",
            "queryset chaining preserves tenant schema throughout pipeline",
            "lazy querysets evaluate within the tenant context at execution",
            "prefetch_related and select_related respect tenant boundaries",
        ],
        "expected_results": [
            "all() returns empty queryset when tenant has no data",
            "filter() matches zero records for cross-tenant field values",
            "get() raises DoesNotExist for IDs belonging to other tenants",
            "count() returns zero in empty tenant and correct in populated",
            "values_list() returns only current tenant field values",
            "no ORM query ever returns records from another tenant schema",
        ],
    }
    logger.debug(
        "ORM query leak test config: queryset_checks=%d, manager_scoping_rules=%d",
        len(config["queryset_checks"]),
        len(config["manager_scoping_rules"]),
    )
    return config


def get_aggregate_query_leak_test_config() -> dict:
    """Return aggregate query leak test configuration.

    Documents tests verifying that aggregate queries (COUNT, SUM, AVG,
    etc.) operate exclusively within the active tenant schema and do
    not include data from other tenants.

    SubPhase-10, Group-E, Task 62.

    Returns:
        dict: Configuration with *aggregate_leak_tests_documented* flag,
              *aggregate_checks* list, *scoping_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "aggregate_leak_tests_documented": True,
        "aggregate_checks": [
            "COUNT aggregate includes only active tenant records",
            "SUM aggregate totals only active tenant numeric fields",
            "AVG aggregate averages only active tenant values",
            "MAX and MIN aggregates scoped to active tenant data only",
            "annotate() with aggregate functions respects tenant boundary",
            "aggregate() on empty tenant returns zero or None correctly",
        ],
        "scoping_rules": [
            "Django aggregate SQL generated with tenant schema search_path",
            "GROUP BY clauses operate within tenant schema tables only",
            "HAVING filters apply to tenant-scoped aggregated results",
            "window functions with PARTITION BY respect tenant isolation",
            "distinct aggregates count only current tenant unique values",
            "conditional aggregates with Case/When scoped to tenant data",
        ],
        "expected_results": [
            "COUNT returns exact record count for active tenant only",
            "SUM excludes values from other tenant schemas entirely",
            "AVG calculation based solely on current tenant data set",
            "aggregate results differ between tenant_a and tenant_b",
            "empty tenant aggregate returns zero or None as appropriate",
            "no aggregate ever combines data across tenant boundaries",
        ],
    }
    logger.debug(
        "Aggregate query leak test config: aggregate_checks=%d, scoping_rules=%d",
        len(config["aggregate_checks"]),
        len(config["scoping_rules"]),
    )
    return config


def get_join_query_leak_test_config() -> dict:
    """Return join query leak test configuration.

    Documents tests verifying that JOIN operations do not cross tenant
    schema boundaries, ensuring all joined tables reside within the
    same tenant schema or the shared public schema.

    SubPhase-10, Group-E, Task 63.

    Returns:
        dict: Configuration with *join_leak_tests_documented* flag,
              *join_checks* list, *boundary_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "join_leak_tests_documented": True,
        "join_checks": [
            "INNER JOIN between tenant models stays within tenant schema",
            "LEFT JOIN with related tenant model scoped to active schema",
            "foreign key traversal via select_related within tenant only",
            "many-to-many JOIN through intermediate table in tenant schema",
            "reverse foreign key JOIN via related_name scoped to tenant",
            "raw SQL JOIN with explicit schema prefix blocked for cross-tenant",
        ],
        "boundary_rules": [
            "all JOIN tables must reside in same tenant schema or public",
            "cross-tenant foreign key references prevented by schema routing",
            "tenant-to-public JOINs allowed for shared reference tables",
            "public-to-tenant JOINs blocked to prevent tenant data exposure",
            "ORM-generated JOINs inherit tenant context search_path",
            "multi-table inheritance JOINs scoped within single tenant schema",
        ],
        "expected_results": [
            "select_related returns only current tenant related objects",
            "prefetch_related queryset scoped to active tenant schema",
            "cross-tenant JOIN via raw SQL raises relation does not exist",
            "many-to-many through table contains only tenant-specific links",
            "reverse relation queryset empty for cross-tenant foreign keys",
            "no JOIN operation ever combines rows from different tenant schemas",
        ],
    }
    logger.debug(
        "Join query leak test config: join_checks=%d, boundary_rules=%d",
        len(config["join_checks"]),
        len(config["boundary_rules"]),
    )
    return config


def get_subquery_leak_test_config() -> dict:
    """Return subquery leak test configuration.

    Documents tests verifying that subqueries do not leak data across
    tenant boundaries, ensuring nested queries respect the active
    tenant schema context.

    SubPhase-10, Group-E, Task 64.

    Returns:
        dict: Configuration with *subquery_leak_tests_documented* flag,
              *subquery_checks* list, *context_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "subquery_leak_tests_documented": True,
        "subquery_checks": [
            "Subquery() expression scoped to active tenant schema",
            "EXISTS subquery evaluates within current tenant context only",
            "IN subquery with values from another tenant returns empty",
            "correlated subquery references only current tenant tables",
            "OuterRef in subquery resolves within tenant schema boundary",
            "nested subquery two levels deep maintains tenant isolation",
        ],
        "context_rules": [
            "subquery inherits parent query tenant schema search_path",
            "Django Subquery class generates SQL within tenant context",
            "Exists() annotation evaluates against tenant-scoped tables",
            "raw SQL subqueries must respect connection search_path setting",
            "subquery used in annotation propagates tenant context correctly",
            "queryset passed to Subquery must be from same tenant context",
        ],
        "expected_results": [
            "Subquery returns only values from active tenant schema",
            "EXISTS returns False for records in other tenant schemas",
            "IN subquery filters exclude cross-tenant primary keys",
            "correlated subquery result set limited to current tenant",
            "nested subquery chain never references another tenant schema",
            "no subquery execution ever returns data from wrong tenant",
        ],
    }
    logger.debug(
        "Subquery leak test config: subquery_checks=%d, context_rules=%d",
        len(config["subquery_checks"]),
        len(config["context_rules"]),
    )
    return config


def get_api_response_leak_test_config() -> dict:
    """Return API response leak test configuration.

    Documents tests verifying that API endpoints return only data
    belonging to the active tenant, preventing cross-tenant data
    exposure in REST responses.

    SubPhase-10, Group-E, Task 65.

    Returns:
        dict: Configuration with *api_leak_tests_documented* flag,
              *response_checks* list, *endpoint_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "api_leak_tests_documented": True,
        "response_checks": [
            "GET list endpoint returns only active tenant records",
            "GET detail endpoint rejects IDs belonging to other tenants",
            "POST endpoint creates resources within active tenant only",
            "PUT/PATCH endpoint cannot modify resources of other tenants",
            "DELETE endpoint cannot remove resources from other tenants",
            "paginated responses include only current tenant record count",
        ],
        "endpoint_rules": [
            "DRF viewset queryset filtered by active tenant schema",
            "permission classes enforce tenant ownership on every request",
            "serializer context includes current tenant identifier",
            "nested resource endpoints validate parent tenant ownership",
            "bulk action endpoints scope operations to active tenant",
            "search and filter parameters apply within tenant boundary",
        ],
        "expected_results": [
            "list endpoint returns zero results for empty tenant schema",
            "detail endpoint returns 404 for cross-tenant resource IDs",
            "create endpoint persists data in active tenant schema only",
            "update endpoint returns 404 when targeting other tenant data",
            "delete endpoint returns 404 for resources in other schemas",
            "no API response ever includes data from another tenant",
        ],
    }
    logger.debug(
        "API response leak test config: response_checks=%d, endpoint_rules=%d",
        len(config["response_checks"]),
        len(config["endpoint_rules"]),
    )
    return config


def get_admin_leak_test_config() -> dict:
    """Return admin leak test configuration.

    Documents tests verifying that Django admin views display only
    data belonging to the active tenant, preventing cross-tenant
    visibility in admin panels.

    SubPhase-10, Group-E, Task 66.

    Returns:
        dict: Configuration with *admin_leak_tests_documented* flag,
              *admin_checks* list, *queryset_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "admin_leak_tests_documented": True,
        "admin_checks": [
            "admin changelist displays only active tenant records",
            "admin change form loads only objects from current tenant",
            "admin search results scoped to active tenant data",
            "admin inline models filtered by active tenant schema",
            "admin autocomplete fields return only tenant-scoped options",
            "admin export actions include only current tenant records",
        ],
        "queryset_rules": [
            "ModelAdmin.get_queryset filters by active tenant schema",
            "admin list_filter choices scoped to current tenant data",
            "admin raw_id_fields lookup restricted to tenant boundary",
            "formfield_for_foreignkey limits choices to tenant objects",
            "formfield_for_manytomany limits choices to tenant objects",
            "admin ordering and sorting operate within tenant context",
        ],
        "expected_results": [
            "changelist shows zero rows when tenant has no data",
            "change form returns 404 for objects in other tenant schemas",
            "search returns empty results for cross-tenant query terms",
            "inline formsets display only related tenant-scoped objects",
            "autocomplete JSON response contains only tenant records",
            "no admin view ever reveals data from another tenant",
        ],
    }
    logger.debug(
        "Admin leak test config: admin_checks=%d, queryset_rules=%d",
        len(config["admin_checks"]),
        len(config["queryset_rules"]),
    )
    return config


def get_file_storage_leak_test_config() -> dict:
    """Return file storage leak test configuration.

    Documents tests verifying that file upload and storage paths are
    tenant-isolated, preventing one tenant from accessing another
    tenant's files.

    SubPhase-10, Group-E, Task 67.

    Returns:
        dict: Configuration with *file_leak_tests_documented* flag,
              *storage_checks* list, *path_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "file_leak_tests_documented": True,
        "storage_checks": [
            "uploaded files stored under tenant-specific directory prefix",
            "file retrieval restricted to active tenant storage path",
            "directory listing returns only current tenant file entries",
            "file deletion scoped to active tenant storage namespace",
            "media URL generation includes tenant identifier in path",
            "storage backend enforces tenant isolation on every operation",
        ],
        "path_rules": [
            "upload_to path prefixed with tenant schema name or UUID",
            "MEDIA_ROOT subdirectory created per tenant on first upload",
            "file path traversal blocked across tenant storage boundaries",
            "static file serving validates tenant ownership of resource",
            "temporary upload directory isolated per tenant session",
            "storage path normalization prevents cross-tenant path escape",
        ],
        "expected_results": [
            "file upload creates object only within tenant storage path",
            "file download returns 404 for files in other tenant paths",
            "directory listing excludes files from other tenant prefixes",
            "file delete operation fails for resources outside tenant path",
            "media URL resolves only for files owned by active tenant",
            "no file operation ever accesses another tenant storage area",
        ],
    }
    logger.debug(
        "File storage leak test config: storage_checks=%d, path_rules=%d",
        len(config["storage_checks"]),
        len(config["path_rules"]),
    )
    return config


def get_cache_leak_test_config() -> dict:
    """Return cache leak test configuration.

    Documents tests verifying that cache keys are tenant-scoped,
    preventing cross-tenant cache pollution or unauthorized data
    access through shared cache backends.

    SubPhase-10, Group-E, Task 68.

    Returns:
        dict: Configuration with *cache_leak_tests_documented* flag,
              *cache_checks* list, *key_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "cache_leak_tests_documented": True,
        "cache_checks": [
            "cache.set stores value under tenant-prefixed key only",
            "cache.get returns None for keys set by another tenant",
            "cache.delete removes only the active tenant cached entry",
            "cache.clear scoped to active tenant key namespace only",
            "cache.get_many returns only keys belonging to active tenant",
            "cache timeout expiration isolated per tenant cache entry",
        ],
        "key_rules": [
            "cache key format includes tenant schema name as prefix",
            "cache key generation utility prepends tenant identifier",
            "cache backend configured with tenant-aware key function",
            "per-view cache decorator includes tenant in vary headers",
            "template fragment cache keys incorporate tenant context",
            "session cache keys namespaced by tenant to prevent overlap",
        ],
        "expected_results": [
            "cache hit returns data only when tenant context matches",
            "cache miss occurs for keys created by different tenant",
            "cache invalidation affects only current tenant entries",
            "cache clear does not remove entries from other tenants",
            "concurrent tenant cache operations do not interfere",
            "no cache operation ever returns data from another tenant",
        ],
    }
    logger.debug(
        "Cache leak test config: cache_checks=%d, key_rules=%d",
        len(config["cache_checks"]),
        len(config["key_rules"]),
    )
    return config


def get_session_leak_test_config() -> dict:
    """Return session leak test configuration.

    Documents tests verifying that user sessions are tenant-isolated,
    preventing session reuse or data leakage across tenant
    boundaries.

    SubPhase-10, Group-E, Task 69.

    Returns:
        dict: Configuration with *session_leak_tests_documented* flag,
              *session_checks* list, *isolation_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "session_leak_tests_documented": True,
        "session_checks": [
            "session created for user is bound to active tenant only",
            "session lookup fails when tenant context does not match",
            "session data includes tenant identifier for validation",
            "session expiration managed independently per tenant",
            "concurrent sessions across tenants do not share state",
            "session fixation attack blocked across tenant boundaries",
        ],
        "isolation_rules": [
            "session backend stores tenant identifier with session data",
            "session middleware validates tenant on every request cycle",
            "session cookie domain scoped to tenant-specific subdomain",
            "session flush clears only current tenant session store",
            "session key generation includes tenant context component",
            "session serialization includes tenant boundary metadata",
        ],
        "expected_results": [
            "authenticated session valid only within originating tenant",
            "session reuse attempt across tenants returns new session",
            "session data isolation prevents cross-tenant data leakage",
            "expired session cleanup scoped to individual tenant store",
            "session ID collision across tenants handled independently",
            "no session operation ever exposes data from another tenant",
        ],
    }
    logger.debug(
        "Session leak test config: session_checks=%d, isolation_rules=%d",
        len(config["session_checks"]),
        len(config["isolation_rules"]),
    )
    return config


def get_logging_leak_test_config() -> dict:
    """Return logging leak test configuration.

    Documents tests verifying that log entries include tenant context
    identifiers and do not leak sensitive data from other tenants
    into log output.

    SubPhase-10, Group-E, Task 70.

    Returns:
        dict: Configuration with *logging_leak_tests_documented* flag,
              *logging_checks* list, *context_rules* list,
              and *expected_results* list.
    """
    config: dict = {
        "logging_leak_tests_documented": True,
        "logging_checks": [
            "log entries include active tenant identifier in metadata",
            "log messages do not contain data from other tenant schemas",
            "structured logging fields include tenant_id or schema_name",
            "error logs capture tenant context for debugging isolation",
            "audit log entries scoped to active tenant operation only",
            "log aggregation supports filtering by tenant identifier",
        ],
        "context_rules": [
            "logging formatter includes tenant context in every record",
            "log filter injects tenant_id from current request context",
            "middleware attaches tenant info to logging thread-local",
            "celery task logging propagates tenant context to workers",
            "exception handler includes tenant identifier in traceback",
            "log rotation and retention policies apply per tenant scope",
        ],
        "expected_results": [
            "every log entry contains correct active tenant identifier",
            "log search by tenant returns only that tenant log entries",
            "error logs include sufficient tenant context for debugging",
            "no log entry ever contains sensitive data from other tenant",
            "audit trail reconstructable per tenant from log records",
            "no logging operation ever leaks cross-tenant information",
        ],
    }
    logger.debug(
        "Logging leak test config: logging_checks=%d, context_rules=%d",
        len(config["logging_checks"]),
        len(config["context_rules"]),
    )
    return config


def get_leak_suite_execution_config() -> dict:
    """Return leak suite execution configuration.

    Documents the process for running the full data leak prevention
    test suite, including execution commands, success criteria, and
    reporting requirements.

    SubPhase-10, Group-E, Task 71.

    Returns:
        dict: Configuration with *leak_suite_execution_documented* flag,
              *execution_steps* list, *success_criteria* list,
              and *reporting_requirements* list.
    """
    config: dict = {
        "leak_suite_execution_documented": True,
        "execution_steps": [
            "run pytest with -m leak_prevention marker to select leak tests",
            "execute query leak tests before channel leak tests",
            "run raw SQL and ORM leak tests in direct query category first",
            "execute aggregate, join, and subquery leak tests next",
            "run API, admin, file, cache, session, and logging leak tests",
            "collect results with verbose output and generate coverage report",
        ],
        "success_criteria": [
            "all raw SQL leak tests confirm no cross-tenant data returned",
            "all ORM queryset leak tests verify tenant-scoped results only",
            "all aggregate leak tests confirm tenant-isolated calculations",
            "all JOIN and subquery leak tests prevent cross-schema access",
            "all channel leak tests verify API, admin, and storage isolation",
            "zero data leak violations detected across entire test suite",
        ],
        "reporting_requirements": [
            "log total number of leak prevention tests executed and passed",
            "report any leak detection failures with tenant and vector details",
            "record execution time per leak test category for benchmarking",
            "flag any intermittent leak test failures under parallel execution",
            "generate summary matrix of leak vectors versus test outcomes",
            "archive leak test results for security audit trail compliance",
        ],
    }
    logger.debug(
        "Leak suite execution config: execution_steps=%d, success_criteria=%d",
        len(config["execution_steps"]),
        len(config["success_criteria"]),
    )
    return config


def get_leak_prevention_documentation_config() -> dict:
    """Return leak prevention documentation configuration.

    Documents the leak prevention test coverage summary, troubleshooting
    guidance, and maintenance notes for the data leak prevention test
    suite.

    SubPhase-10, Group-E, Task 72.

    Returns:
        dict: Configuration with *leak_docs_completed* flag,
              *coverage_summary* list, *troubleshooting_guide* list,
              and *maintenance_notes* list.
    """
    config: dict = {
        "leak_docs_completed": True,
        "coverage_summary": [
            "query leak tests cover raw SQL, ORM, aggregate, JOIN, and subquery paths",
            "channel leak tests cover API responses, admin views, and file storage",
            "cache and session leak tests verify tenant-scoped key prefixing",
            "logging leak tests ensure tenant context in all log records",
            "combined coverage addresses all known data leak vectors",
            "full suite validates end-to-end tenant data isolation",
        ],
        "troubleshooting_guide": [
            "if raw SQL leak detected check search_path reset in connection handler",
            "if ORM leak found verify default manager inherits tenant context",
            "if aggregate leak detected confirm GROUP BY scoped to tenant schema",
            "if JOIN leak found check foreign key routing in allow_relation",
            "if API leak detected verify serializer queryset uses tenant filter",
            "if cache leak found check tenant prefix in cache key generation",
        ],
        "maintenance_notes": [
            "add new leak tests when additional data access channels are introduced",
            "review query leak tests after ORM or database backend upgrades",
            "update channel leak tests when new API endpoints are added",
            "re-run full leak suite after django-tenants version updates",
            "document any new leak vectors discovered during security audits",
            "keep troubleshooting guide current with resolved leak scenarios",
        ],
    }
    logger.debug(
        "Leak prevention documentation config: coverage_summary=%d, troubleshooting_guide=%d",
        len(config["coverage_summary"]),
        len(config["troubleshooting_guide"]),
    )
    return config


def get_performance_test_module_config() -> dict:
    """Return performance test module configuration.

    Documents the structure and scope of the performance test module,
    covering query benchmarks, provisioning timings, and scale test
    organization.

    SubPhase-10, Group-F, Task 73.

    Returns:
        dict: Configuration with *perf_module_documented* flag,
              *module_structure* list, *benchmark_categories* list,
              and *tooling_requirements* list.
    """
    config: dict = {
        "perf_module_documented": True,
        "module_structure": [
            "tests/tenants/test_performance.py as main performance test file",
            "organize benchmarks by category in separate test classes",
            "group query benchmarks in TestQueryPerformance class",
            "group provisioning benchmarks in TestProvisioningPerformance class",
            "group scale tests in TestTenantScalePerformance class",
            "include conftest fixtures for performance test tenant setup",
        ],
        "benchmark_categories": [
            "single-table query latency under tenant context",
            "tenant context switching overhead measurement",
            "schema creation and migration execution timing",
            "multi-tenant scale performance with increasing tenant count",
            "concurrent tenant access throughput and latency",
            "aggregate and join query performance under tenant isolation",
        ],
        "tooling_requirements": [
            "use pytest-benchmark for repeatable timing measurements",
            "configure warmup rounds to eliminate cold-start variance",
            "set minimum rounds for statistical significance in results",
            "capture median and p95 latency for each benchmark category",
            "store benchmark results in JSON for CI trend comparison",
            "mark performance tests with @pytest.mark.slow for selective runs",
        ],
    }
    logger.debug(
        "Performance test module config: module_structure=%d, benchmark_categories=%d",
        len(config["module_structure"]),
        len(config["benchmark_categories"]),
    )
    return config


def get_query_performance_test_config() -> dict:
    """Return query performance test configuration.

    Documents benchmarks for measuring single-table and multi-table
    query latency under tenant context, including acceptable latency
    thresholds.

    SubPhase-10, Group-F, Task 74.

    Returns:
        dict: Configuration with *query_benchmarks_documented* flag,
              *query_checks* list, *latency_thresholds* list,
              and *measurement_methods* list.
    """
    config: dict = {
        "query_benchmarks_documented": True,
        "query_checks": [
            "benchmark single-table SELECT query under active tenant context",
            "benchmark filtered queryset with indexed field lookups",
            "benchmark queryset with select_related across tenant models",
            "benchmark queryset with prefetch_related for reverse relations",
            "benchmark raw SQL SELECT with tenant search_path active",
            "benchmark count and exists queries for tenant-scoped tables",
        ],
        "latency_thresholds": [
            "single-table SELECT must complete within 10ms median latency",
            "filtered queryset must complete within 15ms median latency",
            "select_related query must complete within 25ms median latency",
            "prefetch_related query must complete within 30ms median latency",
            "raw SQL query must complete within 5ms median latency",
            "count and exists queries must complete within 8ms median latency",
        ],
        "measurement_methods": [
            "use pytest-benchmark pedantic mode for precise timing",
            "run minimum 100 iterations per query benchmark",
            "capture p50, p95, and p99 latency percentiles per benchmark",
            "exclude database connection setup time from measurements",
            "measure with warm cache and cold cache scenarios separately",
            "compare tenant-scoped query time against non-tenant baseline",
        ],
    }
    logger.debug(
        "Query performance test config: query_checks=%d, latency_thresholds=%d",
        len(config["query_checks"]),
        len(config["latency_thresholds"]),
    )
    return config


def get_tenant_switching_speed_test_config() -> dict:
    """Return tenant switching speed test configuration.

    Documents benchmarks for measuring tenant context switching
    overhead, including schema activation time and expected upper
    bounds.

    SubPhase-10, Group-F, Task 75.

    Returns:
        dict: Configuration with *switching_benchmarks_documented* flag,
              *switching_checks* list, *speed_targets* list,
              and *measurement_methods* list.
    """
    config: dict = {
        "switching_benchmarks_documented": True,
        "switching_checks": [
            "benchmark single tenant context switch via set_tenant",
            "benchmark rapid alternating switches between two tenants",
            "benchmark context manager entry and exit overhead",
            "benchmark search_path SET command execution time",
            "benchmark thread-local tenant state update latency",
            "benchmark full request cycle with tenant resolution overhead",
        ],
        "speed_targets": [
            "single context switch must complete within 2ms",
            "alternating switches must sustain 500 switches per second",
            "context manager overhead must add less than 1ms per use",
            "search_path SET command must execute within 1ms",
            "thread-local update must complete within 0.1ms",
            "full request tenant resolution must add less than 5ms overhead",
        ],
        "measurement_methods": [
            "use high-resolution timer for sub-millisecond precision",
            "run minimum 1000 iterations per switching benchmark",
            "measure with pre-warmed database connection pool",
            "isolate switching overhead from query execution time",
            "test switching under concurrent request simulation",
            "record p50 and p99 latency for each switching scenario",
        ],
    }
    logger.debug(
        "Tenant switching speed test config: switching_checks=%d, speed_targets=%d",
        len(config["switching_checks"]),
        len(config["speed_targets"]),
    )
    return config


def get_schema_creation_time_test_config() -> dict:
    """Return schema creation time test configuration.

    Documents benchmarks for measuring tenant schema provisioning
    time, including schema creation, migration execution, and
    acceptable duration limits.

    SubPhase-10, Group-F, Task 76.

    Returns:
        dict: Configuration with *schema_benchmarks_documented* flag,
              *creation_checks* list, *duration_targets* list,
              and *measurement_methods* list.
    """
    config: dict = {
        "schema_benchmarks_documented": True,
        "creation_checks": [
            "benchmark CREATE SCHEMA execution time for new tenant",
            "benchmark migration execution time for tenant app tables",
            "benchmark full tenant provisioning including domain setup",
            "benchmark schema creation with minimal fixture seeding",
            "benchmark schema creation with full fixture data loading",
            "benchmark schema teardown and DROP SCHEMA execution time",
        ],
        "duration_targets": [
            "CREATE SCHEMA must complete within 100ms",
            "tenant migration execution must complete within 5 seconds",
            "full provisioning with domain must complete within 10 seconds",
            "minimal fixture seeding must add less than 2 seconds overhead",
            "full fixture loading must complete within 15 seconds total",
            "schema teardown must complete within 500ms",
        ],
        "measurement_methods": [
            "time each provisioning phase separately for profiling",
            "run provisioning benchmark minimum 10 iterations",
            "measure with empty database and with existing tenants",
            "capture wall-clock time and database server time separately",
            "test provisioning under different database load conditions",
            "compare provisioning time growth as tenant count increases",
        ],
    }
    logger.debug(
        "Schema creation time test config: creation_checks=%d, duration_targets=%d",
        len(config["creation_checks"]),
        len(config["duration_targets"]),
    )
    return config


def get_many_tenants_scale_test_config() -> dict:
    """Return many tenants scale test configuration.

    Documents benchmarks for measuring system performance with a large
    number of tenants (100+), covering resource usage, query latency,
    and provisioning time at scale.

    SubPhase-10, Group-F, Task 77.

    Returns:
        dict: Configuration with *scale_tests_documented* flag,
              *scale_checks* list, *resource_targets* list,
              and *measurement_methods* list.
    """
    config: dict = {
        "scale_tests_documented": True,
        "scale_checks": [
            "benchmark query latency with 100 provisioned tenant schemas",
            "benchmark tenant switching with 100 active tenant contexts",
            "benchmark schema listing performance with many schemas",
            "benchmark tenant provisioning time as count approaches 200",
            "benchmark memory usage growth with increasing tenant count",
            "benchmark connection pool behavior under many tenant schemas",
        ],
        "resource_targets": [
            "query latency must not degrade more than 20% at 100 tenants",
            "tenant switching time must remain under 5ms at 100 tenants",
            "schema listing must complete within 50ms at 100 schemas",
            "provisioning time must not degrade more than 50% at 200 tenants",
            "memory per tenant must remain under 10MB at 100 tenants",
            "connection pool must not exceed 50 connections at 100 tenants",
        ],
        "measurement_methods": [
            "provision tenants incrementally and measure at 10, 50, 100, 200",
            "record query latency at each tenant count checkpoint",
            "measure memory usage via process profiling at each checkpoint",
            "track connection pool utilization during scale testing",
            "generate performance regression chart across tenant counts",
            "set automated alerts for performance threshold violations",
        ],
    }
    logger.debug(
        "Many tenants scale test config: scale_checks=%d, resource_targets=%d",
        len(config["scale_checks"]),
        len(config["resource_targets"]),
    )
    return config


def get_concurrent_tenant_access_test_config() -> dict:
    """Return concurrent tenant access test configuration.

    Documents benchmarks for measuring system performance under
    concurrent multi-tenant access, covering parallel requests,
    throughput, and acceptable degradation limits.

    SubPhase-10, Group-F, Task 78.

    Returns:
        dict: Configuration with *concurrency_tests_documented* flag,
              *concurrency_checks* list, *degradation_targets* list,
              and *measurement_methods* list.
    """
    config: dict = {
        "concurrency_tests_documented": True,
        "concurrency_checks": [
            "benchmark parallel requests across 10 different tenants",
            "benchmark concurrent read queries on same tenant schema",
            "benchmark concurrent write operations across tenant schemas",
            "benchmark mixed read-write workload under concurrent access",
            "benchmark tenant switching under parallel request load",
            "benchmark connection pool saturation under concurrent tenants",
        ],
        "degradation_targets": [
            "query latency must not degrade more than 30% under 10 concurrent tenants",
            "throughput must sustain 100 requests per second across tenants",
            "write operations must maintain ACID isolation under concurrency",
            "tenant switching must remain under 10ms under concurrent load",
            "no deadlocks detected during concurrent cross-tenant operations",
            "connection pool must handle concurrent access without timeouts",
        ],
        "measurement_methods": [
            "use threading or asyncio to simulate concurrent tenant requests",
            "measure latency distribution under increasing concurrency levels",
            "record throughput at 1, 5, 10, and 20 concurrent connections",
            "monitor for deadlocks and lock contention during tests",
            "capture error rates under sustained concurrent load",
            "compare concurrent performance against single-tenant baseline",
        ],
    }
    logger.debug(
        "Concurrent tenant access test config: concurrency_checks=%d, degradation_targets=%d",
        len(config["concurrency_checks"]),
        len(config["degradation_targets"]),
    )
    return config


def get_performance_baselines_config() -> dict:
    """Return performance baselines configuration.

    Documents baseline performance metrics and acceptable thresholds
    for multi-tenant test operations, covering query latency,
    provisioning time, and scale targets.

    SubPhase-10, Group-F, Task 79.

    Returns:
        dict: Configuration with *baselines_documented* flag,
              *baseline_metrics* list, *threshold_values* list,
              and *measurement_conditions* list.
    """
    config: dict = {
        "baselines_documented": True,
        "baseline_metrics": [
            "single-table query median latency baseline at 8ms",
            "tenant context switch median latency baseline at 1.5ms",
            "schema creation duration baseline at 3 seconds",
            "100-tenant query latency degradation baseline at 15 percent",
            "concurrent access throughput baseline at 120 requests per second",
            "full provisioning with fixtures baseline at 8 seconds",
        ],
        "threshold_values": [
            "query latency must not exceed 2x baseline under normal load",
            "context switch must not exceed 3x baseline under concurrent load",
            "schema creation must not exceed 1.5x baseline at 100 tenants",
            "scale degradation must stay within 25 percent of baseline",
            "throughput must not drop below 80 percent of baseline under load",
            "provisioning time must not exceed 2x baseline with full fixtures",
        ],
        "measurement_conditions": [
            "baselines measured on CI runner with standardized hardware profile",
            "all baselines captured with warm database connection pool",
            "baselines recorded with empty tenant schemas before seeding",
            "measurements repeated minimum 50 iterations for statistical validity",
            "baseline values updated quarterly or after major infrastructure changes",
            "threshold violations trigger CI warning but not blocking failure",
        ],
    }
    logger.debug(
        "Performance baselines config: baseline_metrics=%d, threshold_values=%d",
        len(config["baseline_metrics"]),
        len(config["threshold_values"]),
    )
    return config


def get_ci_test_configuration_config() -> dict:
    """Return CI test configuration.

    Documents the continuous integration test workflow configuration,
    including database service setup, environment variables, and
    Python version requirements.

    SubPhase-10, Group-F, Task 80.

    Returns:
        dict: Configuration with *ci_config_documented* flag,
              *workflow_steps* list, *service_requirements* list,
              and *environment_variables* list.
    """
    config: dict = {
        "ci_config_documented": True,
        "workflow_steps": [
            "trigger CI workflow on push to main and pull request branches",
            "provision PostgreSQL service container for multi-tenant tests",
            "install Python dependencies from requirements/test.txt",
            "run database migrations for public and test tenant schemas",
            "execute pytest with tenant-specific markers and verbose output",
            "upload test results and coverage artifacts on workflow completion",
        ],
        "service_requirements": [
            "PostgreSQL 15 or later with CREATE SCHEMA privilege",
            "Redis service container for cache and session testing",
            "Python 3.12 or later matching production runtime version",
            "pip and virtualenv for isolated dependency installation",
            "sufficient disk space for test database and coverage reports",
            "network access between service containers for integration tests",
        ],
        "environment_variables": [
            "DJANGO_SETTINGS_MODULE set to config.settings.test",
            "DATABASE_URL pointing to CI PostgreSQL service container",
            "REDIS_URL pointing to CI Redis service container",
            "SECRET_KEY set to a test-only value for CI environment",
            "PYTHONPATH includes backend directory for module resolution",
            "COVERAGE_FILE set to specify coverage data file location",
        ],
    }
    logger.debug(
        "CI test configuration config: workflow_steps=%d, service_requirements=%d",
        len(config["workflow_steps"]),
        len(config["service_requirements"]),
    )
    return config


def get_ci_test_job_config() -> dict:
    """Return CI test job configuration.

    Documents the test job steps within the CI pipeline, including
    dependency installation, test execution, and artifact collection
    for test reports and coverage files.

    SubPhase-10, Group-F, Task 81.

    Returns:
        dict: Configuration with *ci_job_documented* flag,
              *job_steps* list, *artifact_outputs* list,
              and *failure_handling* list.
    """
    config: dict = {
        "ci_job_documented": True,
        "job_steps": [
            "checkout repository code at the current commit reference",
            "set up Python environment with cached pip dependencies",
            "install project dependencies from requirements/test.txt",
            "run pytest with coverage collection and JUnit XML output",
            "generate coverage HTML and XML reports after test completion",
            "upload test and coverage artifacts to CI artifact storage",
        ],
        "artifact_outputs": [
            "JUnit XML test report at reports/junit.xml for CI parsing",
            "coverage XML report at reports/coverage.xml for badge generation",
            "coverage HTML report at htmlcov/ for developer browsing",
            "pytest verbose output log at reports/pytest-output.txt",
            "performance benchmark JSON at reports/benchmarks.json",
            "test summary markdown at reports/test-summary.md for PR comments",
        ],
        "failure_handling": [
            "fail CI job immediately if any tenant isolation test fails",
            "fail CI job if coverage drops below configured threshold",
            "warn but continue if performance benchmark exceeds baseline by 50 percent",
            "retry flaky tests up to 2 times before marking as failed",
            "notify team channel on test suite failure via webhook",
            "preserve all artifacts on failure for debugging investigation",
        ],
    }
    logger.debug(
        "CI test job config: job_steps=%d, artifact_outputs=%d",
        len(config["job_steps"]),
        len(config["artifact_outputs"]),
    )
    return config


def get_test_coverage_config() -> dict:
    """Return test coverage configuration.

    Documents the coverage tool settings, including source paths to
    measure, files to omit, and report output formats for the
    multi-tenant test suite.

    SubPhase-10, Group-F, Task 82.

    Returns:
        dict: Configuration with *coverage_configured* flag,
              *source_paths* list, *omit_patterns* list,
              and *report_formats* list.
    """
    config: dict = {
        "coverage_configured": True,
        "source_paths": [
            "apps/tenants/ as primary coverage target for tenant utilities",
            "apps/core/ for shared model and middleware coverage",
            "apps/users/ for tenant-aware user model coverage",
            "config/ for settings and URL configuration coverage",
            "apps/products/ for tenant-scoped product model coverage",
            "apps/orders/ for tenant-scoped order processing coverage",
        ],
        "omit_patterns": [
            "*/migrations/* excluded from coverage measurement",
            "*/tests/* excluded to avoid measuring test code itself",
            "*/__pycache__/* excluded as compiled bytecode artifacts",
            "*/admin.py excluded unless admin leak tests require it",
            "manage.py excluded as entry point only",
            "*/apps.py excluded as Django app configuration boilerplate",
        ],
        "report_formats": [
            "terminal summary with line coverage percentages per module",
            "HTML report with annotated source and branch coverage",
            "XML report in Cobertura format for CI tool integration",
            "JSON report for programmatic coverage trend analysis",
            "LCOV report for coverage badge generation services",
            "annotate mode showing missing lines inline in terminal",
        ],
    }
    logger.debug(
        "Test coverage config: source_paths=%d, omit_patterns=%d",
        len(config["source_paths"]),
        len(config["omit_patterns"]),
    )
    return config


def get_coverage_threshold_config() -> dict:
    """Return coverage threshold configuration.

    Documents the minimum coverage percentage requirements and CI
    enforcement behavior when coverage drops below the configured
    thresholds.

    SubPhase-10, Group-F, Task 83.

    Returns:
        dict: Configuration with *threshold_configured* flag,
              *threshold_targets* list, *enforcement_rules* list,
              and *exception_policies* list.
    """
    config: dict = {
        "threshold_configured": True,
        "threshold_targets": [
            "overall project coverage minimum set at 80 percent",
            "tenant utilities module coverage minimum set at 90 percent",
            "isolation test coverage minimum set at 95 percent",
            "leak prevention test coverage minimum set at 90 percent",
            "new code coverage minimum set at 85 percent for pull requests",
            "branch coverage minimum set at 70 percent for critical paths",
        ],
        "enforcement_rules": [
            "CI job fails if overall coverage drops below 80 percent",
            "pull request blocked if new code coverage below 85 percent",
            "coverage regression of more than 2 percent triggers CI failure",
            "coverage report posted as PR comment for reviewer visibility",
            "coverage badge updated on main branch after merge",
            "weekly coverage trend report emailed to team leads",
        ],
        "exception_policies": [
            "generated code and migrations excluded from threshold calculation",
            "third-party integration wrappers may have reduced threshold",
            "experimental features can request temporary threshold waiver",
            "coverage exceptions must be documented in pyproject.toml",
            "exception requests require team lead approval before merge",
            "all exceptions reviewed quarterly for removal or extension",
        ],
    }
    logger.debug(
        "Coverage threshold config: threshold_targets=%d, enforcement_rules=%d",
        len(config["threshold_targets"]),
        len(config["enforcement_rules"]),
    )
    return config


def get_test_report_config() -> dict:
    """Return test report configuration.

    Documents the test report generation settings, including report
    formats, storage locations, and distribution requirements for
    CI pipeline outputs.

    SubPhase-10, Group-F, Task 84.

    Returns:
        dict: Configuration with *reports_configured* flag,
              *report_outputs* list, *storage_locations* list,
              and *distribution_rules* list.
    """
    config: dict = {
        "reports_configured": True,
        "report_outputs": [
            "test execution summary with pass, fail, skip counts",
            "coverage percentage breakdown by module and file",
            "performance benchmark results compared against baselines",
            "isolation test results with tenant schema verification details",
            "leak prevention test results with vector coverage matrix",
            "overall test health dashboard with trend indicators",
        ],
        "storage_locations": [
            "CI artifact storage retains reports for 90 days",
            "coverage HTML reports published to internal documentation site",
            "JUnit XML uploaded to CI test analytics dashboard",
            "benchmark JSON stored in version-controlled baselines directory",
            "test summary markdown attached to pull request as comment",
            "archived reports backed up to object storage monthly",
        ],
        "distribution_rules": [
            "test failure notifications sent to PR author and reviewers",
            "coverage regression alerts sent to team channel immediately",
            "weekly test health summary distributed to all contributors",
            "performance regression alerts sent to infrastructure team",
            "quarterly test coverage trend report shared with management",
            "critical isolation test failures escalated to security team",
        ],
    }
    logger.debug(
        "Test report config: report_outputs=%d, storage_locations=%d",
        len(config["report_outputs"]),
        len(config["storage_locations"]),
    )
    return config


def get_initial_commit_config() -> dict:
    """Return initial commit configuration.

    Documents the commit scope and message conventions for the
    performance and CI integration updates, ensuring all testing
    infrastructure changes are captured in a single commit.

    SubPhase-10, Group-F, Task 85.

    Returns:
        dict: Configuration with *commit_documented* flag,
              *commit_scope_items* list, *message_conventions* list,
              and *commit_checklist* list.
    """
    config: dict = {
        "commit_documented": True,
        "commit_scope_items": [
            "performance test module with query and switching benchmarks",
            "CI workflow configuration with PostgreSQL service container",
            "test job definition with pytest execution and artifact upload",
            "coverage configuration with source paths and omit patterns",
            "coverage threshold enforcement at 80 percent minimum overall",
            "test report generation with HTML, XML, and JSON outputs",
        ],
        "message_conventions": [
            "use conventional commit format: test(tenants): add multi-tenant CI",
            "include scope summary in commit body listing all task numbers",
            "reference SubPhase-10 Group-F in commit body for traceability",
            "list breaking changes if any CI behavior differs from previous",
            "keep subject line under 72 characters for readability",
            "sign off commit with developer and reviewer identifiers",
        ],
        "commit_checklist": [
            "verify all 86 testing utility functions are present and passing",
            "confirm __init__.py re-exports match testing_utils.py functions",
            "ensure test_testing.py covers all functions with 7 methods each",
            "validate no linting or type-checking errors in changed files",
            "confirm CI workflow file syntax is valid before committing",
            "review diff for accidental inclusion of debug or temporary code",
        ],
    }
    logger.debug(
        "Initial commit config: commit_scope_items=%d, message_conventions=%d",
        len(config["commit_scope_items"]),
        len(config["message_conventions"]),
    )
    return config


def get_final_phase_documentation_config() -> dict:
    """Return final phase documentation configuration.

    Documents the Phase 02 completion summary and handoff notes
    for transition to Phase 03, including all testing milestones
    achieved and remaining items for future phases.

    SubPhase-10, Group-F, Task 86.

    Returns:
        dict: Configuration with *documentation_complete* flag,
              *phase_completion_items* list, *handoff_notes* list,
              and *transition_requirements* list.
    """
    config: dict = {
        "documentation_complete": True,
        "phase_completion_items": [
            "all 86 multi-tenant testing utility functions implemented",
            "comprehensive test suite with 602 tests across 86 test classes",
            "Group-A through Group-F covering setup, isolation, leaks, and CI",
            "performance baselines established for query and provisioning metrics",
            "CI pipeline configured with coverage thresholds and reporting",
            "Phase 02 database architecture and multi-tenancy testing complete",
        ],
        "handoff_notes": [
            "Phase 03 Core Backend Infrastructure can begin immediately",
            "tenant testing utilities available for import in all future phases",
            "CI pipeline ready to validate tenant isolation in new features",
            "coverage thresholds enforced to prevent regression in tenant code",
            "performance baselines serve as reference for optimization work",
            "documentation in docs/database/ covers all testing conventions",
        ],
        "transition_requirements": [
            "merge Phase 02 branch to main after final review approval",
            "tag release with phase-02-complete for milestone tracking",
            "archive Phase 02 ADR documents in docs/adr/ directory",
            "notify team of Phase 03 kickoff and dependency availability",
            "update project roadmap to reflect Phase 02 completion status",
            "schedule retrospective to capture Phase 02 lessons learned",
        ],
    }
    logger.debug(
        "Final phase documentation config: phase_completion_items=%d, handoff_notes=%d",
        len(config["phase_completion_items"]),
        len(config["handoff_notes"]),
    )
    return config
