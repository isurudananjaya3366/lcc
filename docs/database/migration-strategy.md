# Migration Strategy

> LankaCommerce Cloud -- Multi-Tenant Migration Strategy
> SubPhase-08, Group-A (Tasks 01-14), Group-B (Tasks 15-28), Group-C (Tasks 29-44),
> Group-D (Tasks 45-58), Group-E (Tasks 59-70), Group-F (Tasks 71-84)

---

## Overview

LankaCommerce Cloud uses django-tenants migrate_schemas command
to manage database migrations across the public schema and all
tenant schemas. Public schema migrations always run first,
followed by tenant schema migrations.

---

## Review, Commands & Settings (Tasks 01-05)

Configuration helpers for reviewing django-tenants migration
behaviour, documenting commands, setting up directory structure,
configuring migration settings, and defining shared app scope.

### Review django-tenants Migrations (Task 01)

get_migration_review_config() returns migration review configuration:
reviewed (True), command (migrate_schemas), 5 key_options
(--shared, --tenant, --schema, --executor, --no-input),
4 command_patterns, behaviour dict (public_first True),
and 6 findings about migrate_schemas behaviour.

### Document Migration Commands (Task 02)

get_migration_commands_documentation() returns command documentation:
documented (True), 4 core_commands (each with name, description,
scope), 3 execution_order steps, 4 usage_notes, and
public_runs_first (True).

### Create Migration Directory (Task 03)

get_migration_directory_config() returns directory configuration:
structure_documented (True), 3 directories, expected_paths dict
(migration_files, migration_utils, migration_scripts, migration_docs),
and 4 structure_notes.

### Configure Migration Settings (Task 04)

get_migration_settings_config() returns settings configuration:
configured (True), 5 settings_entries (each with name, location,
description), 4 configuration_notes, and settings_location string.

### Define Shared Apps Migrations (Task 05)

get_shared_apps_migration_config() returns shared apps scope:
scope_defined (True), 6 shared_apps_scope items, migration_behaviour
dict (schema public, runs_first True), 5 usage_notes, and
relation_to_shared_apps string.

---

## Helpers, Naming & Template (Tasks 06-10)

Configuration helpers for defining tenant app migration scope,
migration helper modules, naming conventions, templates, and
cross-app migration dependency ordering.

### Define Tenant Apps Migrations (Task 06)

get_tenant_apps_migration_config() returns tenant apps scope:
scope_defined (True), 10 tenant_apps_scope items, migration_behaviour
dict (schema tenant, runs_after_public True), 6 usage_notes, and
relation_to_tenant_apps string.

### Create Migration Helper Module (Task 07)

get_migration_helper_module_config() returns helper module config:
module_documented (True), 3 helpers (each with name, location,
description), 4 usage_locations, 4 module_notes, and package_path
string.

### Define Migration Naming Convention (Task 08)

get_migration_naming_convention() returns naming convention config:
convention_documented (True), convention dict (format
NNNN_descriptive_name.py, prefix, separator, name_style, extension),
5 examples, and 4 enforcement steps.

### Create Migration Template (Task 09)

get_migration_template_config() returns template configuration:
template_documented (True), 4 template_sections (each with name,
description, required), 5 template_notes, and 4 usage_guidelines.

### Define Migration Dependencies (Task 10)

get_migration_dependencies_config() returns dependency configuration:
dependencies_documented (True), 5 dependency_rules (each with source,
depends_on, reason), 5 ordering_notes, and 4 rationale items.

---

## Check, Makefile, CI & Docs (Tasks 11-14)

Configuration helpers for migration check scripts, Makefile
entries, CI pipeline gates, and migration flow documentation.

### Create Migration Check Script (Task 11)

get_migration_check_script_config() returns check script config:
script_documented (True), script_config dict (name, location,
command, exit_code_pending, exit_code_clean), 5 detection_steps,
and 4 usage_locations.

### Add to Makefile (Task 12)

get_makefile_migration_config() returns Makefile configuration:
makefile_documented (True), 5 targets (each with name, description,
command), and 4 usage_notes.

### Configure CI Migration Checks (Task 13)

get_ci_migration_checks_config() returns CI checks configuration:
ci_documented (True), 4 pipeline_steps (each with name, description,
blocks_deploy), 5 gate_criteria, and 4 pipeline_notes.

### Document Migration Flow (Task 14)

get_migration_flow_documentation() returns flow documentation:
flow_documented (True), 8 flow_sequence steps, 4 responsibilities
(each with role, tasks), and 5 operational_notes.

---

## Command, Apps & Initial (Tasks 15-20)

Configuration helpers for public schema migration command,
public schema apps, initial migration, table verification,
migration scripts, and tenant table updates.

### Create Public Migration Command (Task 15)

get_public_migration_command_config() returns command configuration:
command_documented (True), command_config dict (name, full_command,
scope public, schema public, runs_first True), 5 options, and
4 usage_notes.

### Define Public Schema Apps (Task 16)

get_public_schema_apps_config() returns public apps configuration:
apps_documented (True), 7 public_apps (each with app, reason),
5 scope_notes, and total_apps count.

### Run Initial Public Migration (Task 17)

get_initial_public_migration_config() returns initial migration config:
migration_documented (True), 5 migration_steps, 6 expected_results,
and 4 completion_notes.

### Verify Public Tables Created (Task 18)

get_public_tables_verification() returns table verification config:
tables_verified (True), 12 expected_tables, 4 verification_steps,
and 4 findings.

### Create Public Migration Script (Task 19)

get_public_migration_script_config() returns script configuration:
script_documented (True), script_config dict (name, location,
purpose, idempotent True), 5 script_steps, and 5 usage_notes.

### Handle Tenant Table Updates (Task 20)

get_tenant_table_updates_config() returns update configuration:
updates_documented (True), 5 update_flow steps, 4 safety_measures,
and 5 impact_notes.

---

## Models, Data & Seed (Tasks 21-25)

Configuration helpers for domain table updates, plan table updates,
data migration templates, initial data seeding, and public tenant
creation.

### Handle Domain Table Updates (Task 21)

get_domain_table_updates_config() returns domain update configuration:
updates_documented (True), 6 update_steps, 5 resolution_effects,
and 4 safety_notes.

### Handle Plan Table Updates (Task 22)

get_plan_table_updates_config() returns plan update configuration:
updates_documented (True), 6 update_steps, 5 subscription_effects,
and 4 safety_notes.

### Create Data Migration Template (Task 23)

get_data_migration_template_config() returns template configuration:
template_documented (True), 5 template_sections, 5 usage_guidelines,
and 4 best_practices.

### Seed Initial Data (Task 24)

get_seed_initial_data_config() returns seed configuration:
seeding_documented (True), 5 seed_categories (each with category,
description), 5 fixture_sources, 6 seeding_steps, and total_categories
count.

### Create Public Tenant (Task 25)

get_public_tenant_creation_config() returns tenant creation config:
tenant_documented (True), tenant_attributes dict (schema_name public,
name, is_active True, is_public True, auto_create_schema False),
5 creation_steps, and 5 usage_notes.

---

## Verify, Backup & Docs (Tasks 26-28)

Configuration helpers for public migration verification, migration
backup strategy, and public migration documentation.

### Verify Public Migration (Task 26)

get_public_migration_verification_config() returns verification config:
migration_verified (True), 7 verification_steps, 6 validation_checks,
and 4 outcome_recording entries.

### Create Migration Backup (Task 27)

get_migration_backup_config() returns backup configuration:
backup_documented (True), 6 backup_steps, storage_config dict
(location, naming, compression, retention_days 30, max_backups 50),
and 5 retention_policy entries.

### Document Public Migrations (Task 28)

get_public_migration_documentation_config() returns documentation config:
documentation_complete (True), 7 flow_summary steps, 5 safeguards,
and 5 operational_notes.

---

## Commands & Parallel (Tasks 29-34)

Configuration helpers for tenant migration commands, tenant schema
apps, single and batch tenant migrations, parallel execution, and
concurrency limits.

### Create Tenant Migration Command (Task 29)

get_tenant_migration_command_config() returns command configuration:
command_documented (True), command_config dict (name, full_command,
scope tenant, excludes_public True), 5 options, and 4 usage_notes.

### Define Tenant Schema Apps (Task 30)

get_tenant_schema_apps_config() returns tenant apps configuration:
apps_documented (True), 8 tenant_apps (each with app, reason),
5 scope_notes, and total_apps count.

### Create Single Tenant Migration (Task 31)

get_single_tenant_migration_config() returns single tenant config:
migration_documented (True), 5 migration_flow steps, 5 use_cases,
and 4 safety_notes.

### Create Batch Tenant Migration (Task 32)

get_batch_tenant_migration_config() returns batch migration config:
batch_documented (True), 6 batch_flow steps, batch_config dict
(default_batch_size 10, ordering, skip_inactive True, stop_on_error
False, retry_failed True), and 5 behavior_notes.

### Configure Parallel Migration (Task 33)

get_parallel_migration_config() returns parallel migration config:
parallel_documented (True), parallel_config dict (enabled True,
executor ThreadPoolExecutor, max_workers 4, timeout_per_tenant 300),
5 safeguards, and 5 performance_notes.

### Set Concurrency Limit (Task 34)

get_concurrency_limit_config() returns concurrency limit config:
limit_documented (True), limit_config dict (max_concurrent 4,
max_batch_size 10, connection_pool_size 20, reserved_connections 5,
available_for_migration 15), 5 rationale entries, and
4 tuning_guidelines.

---

## Progress, Errors & Retry (Tasks 35-40)

Configuration helpers for migration ordering, progress tracking,
log tables, failure handling, retry behavior, and skipping
problematic tenants.

### Handle Migration Ordering (Task 35)

get_migration_ordering_config() returns ordering configuration:
ordering_documented (True), 5 ordering_rules, 4 enforcement_notes,
and dependency_resolution dict (strategy topological_sort,
shared_first True, detect_circular True, fail_on_missing True).

### Create Progress Tracking (Task 36)

get_progress_tracking_config() returns tracking configuration:
tracking_documented (True), 6 tracking_fields, reporting_format
dict (output console_and_log, show_percentage True, show_elapsed_time
True, show_remaining_estimate True, 3 verbosity_levels), and
5 status_values.

### Create Migration Log Table (Task 37)

get_migration_log_table_config() returns log table configuration:
log_table_documented (True), table_name tenant_migration_log,
9 columns (each with name, type, constraints), 5 query_patterns,
and retention_policy dict (keep_days 90, archive_older True,
purge_after_days 365).

### Handle Failed Tenant Migration (Task 38)

get_failed_migration_handling_config() returns failure handling config:
failure_handling_documented (True), 5 failure_actions,
threshold_config dict (max_consecutive_failures 3,
max_total_failures_percent 10, halt_on_threshold True,
alert_on_first_failure True), and 4 behavior_options.

### Retry Failed Migrations (Task 39)

get_retry_failed_migrations_config() returns retry configuration:
retry_documented (True), retry_settings dict (max_retries 3,
retry_only_failed True, reset_status_before_retry True,
log_each_attempt True), 4 delay_strategy entries, and
5 safeguards.

### Skip Problematic Tenants (Task 40)

get_skip_problematic_tenants_config() returns skip configuration:
skip_documented (True), 4 skip_criteria, 4 skip_actions, and
5 review_requirements.

---

## Data, Large, Verify & Docs (Tasks 41-44)

Configuration helpers for tenant data migrations, large tenant
handling, migration verification, and tenant migration documentation.

### Create Tenant Data Migration (Task 41)

get_tenant_data_migration_config() returns data migration config:
data_migration_documented (True), 5 migration_steps, 5 ordering_notes,
and 6 best_practices.

### Handle Large Tenants (Task 42)

get_large_tenant_handling_config() returns large tenant config:
large_tenant_documented (True), 5 threshold_criteria, scheduling_config
dict (preferred_window 02:00-06:00 UTC, avoid_peak_hours True,
notify_tenant_admin True, maintenance_mode True, max_duration_hours 4),
5 concurrency_adjustments, and 5 monitoring_notes.

### Verify Tenant Migrations (Task 43)

get_tenant_migration_verification_config() returns verification config:
verification_documented (True), 6 verification_steps, 5 integrity_checks,
and result_recording dict (store_in_log_table True, include_timestamp
True, record_pass_fail True, capture_error_details True,
generate_summary_report True).

### Document Tenant Migrations (Task 44)

get_tenant_migration_documentation_config() returns documentation config:
documentation_completed (True), 7 workflow_summary steps,
6 safeguard_notes, and 5 reference_links.

Note: Group-C (Tenant Schema Migrations) is now FULLY COMPLETE
(Tasks 29-44).

---

## Rules & Columns (Tasks 45-50)

Configuration helpers for zero-downtime rules, additive-only
policy, nullable columns, default values, no-rename policy,
and phased column removal.

### Define Zero-Downtime Rules (Task 45)

get_zero_downtime_rules_config() returns rules configuration:
rules_documented (True), 7 rules, 5 rationale entries, and
5 safety_goals.

### Additive Migrations Only (Task 46)

get_additive_migrations_policy_config() returns policy config:
policy_documented (True), 6 allowed_operations,
6 prohibited_operations, and 5 enforcement_notes.

### Nullable New Columns (Task 47)

get_nullable_new_columns_config() returns nullable config:
nullable_documented (True), 5 nullable_rules, 5 backfill_notes,
and 4 exceptions.

### Default Values Required (Task 48)

get_default_values_required_config() returns defaults config:
defaults_documented (True), 5 default_rules, 5 safe_defaults
(each with type, default, rationale), and 5 impact_notes.

### No Column Renames (Task 49)

get_no_column_renames_config() returns no-rename config:
no_rename_documented (True), 5 no_rename_rules,
6 phased_rename_steps, and 4 alternatives.

### Phased Column Removal (Task 50)

get_phased_column_removal_config() returns removal config:
phased_removal_documented (True), 5 removal_phases,
5 timeline_guidelines, and 6 safety_checks.

### Migration Linter (Task 51)

get_migration_linter_config() returns linter config:
linter_documented (True), 6 linter_rules,
5 enforcement_points, and 6 blocked_operations.

### django-pg-zero-downtime Configuration (Task 52)

get_pg_zero_downtime_config() returns tool config:
configuration_documented (True), 6 guarded_operations,
5 settings, and 5 scope_notes.

### Index Creation (Task 53)

get_index_creation_config() returns index config:
index_rules_documented (True), 6 index_rules,
5 restrictions, and 5 best_practices.

### Constraint Addition (Task 54)

get_constraint_addition_config() returns constraint config:
constraint_handling_documented (True), 6 constraint_rules,
5 validation_phases, and 5 supported_constraints.

### Migration Dry Run (Task 55)

get_migration_dry_run_config() returns dry run config:
dry_run_documented (True), 6 dry_run_steps,
5 usage_guidelines, and 5 integration_points.

### Off-Peak Migration Schedule (Task 56)

get_off_peak_migration_schedule_config() returns schedule config:
schedule_documented (True), 5 maintenance_windows,
6 scheduling_rules, and 5 communication_steps.

### Migration Monitoring (Task 57)

get_migration_monitoring_config() returns monitoring config:
monitoring_documented (True), 6 monitoring_metrics,
5 alert_thresholds, and 5 escalation_steps.

### Zero-Downtime Documentation (Task 58)

get_zero_downtime_documentation_config() returns documentation config:
documentation_completed (True), 7 rule_summaries,
5 enforcement_mechanisms, and 6 reference_links.

### Rollback Strategy (Task 59)

get_rollback_strategy_config() returns strategy config:
strategy_documented (True), 6 rollback_principles,
5 schema_scopes, and 6 safety_requirements.

### Rollback Command (Task 60)

get_rollback_command_config() returns command config:
commands_documented (True), 6 rollback_commands,
5 required_inputs, and 5 usage_examples.

### Forward/Backward Operations (Task 61)

get_forward_backward_ops_config() returns operations config:
operations_documented (True), 6 forward_ops,
5 backward_requirements, and 6 reversibility_rules.

### Rollback Testing (Task 62)

get_rollback_test_config() returns test config:
rollback_tests_documented (True), 6 test_procedures,
5 success_criteria, and 5 recording_requirements.

### Single Tenant Rollback (Task 63)

get_single_tenant_rollback_config() returns single tenant config:
single_tenant_rollback_documented (True), 6 rollback_steps,
5 tenant_selection, and 6 safety_measures.

### All Tenants Rollback (Task 64)

get_all_tenants_rollback_config() returns all tenants config:
all_tenants_rollback_documented (True), 6 rollback_process,
6 safeguards, and 5 staging_requirements.

### Non-Reversible Migration Handling (Task 65)

get_non_reversible_migration_config() returns non-reversible handling config:
non_reversible_handling_documented (True), 7 non_reversible_types,
8 manual_procedures, and 6 risk_mitigation.

### Pre-Migration Backup (Task 66)

get_pre_migration_backup_config() returns pre-migration backup config:
pre_migration_backup_documented (True), 9 backup_steps,
6 backup_types, and 6 retention_policy.

### Point-in-Time Restore (Task 67)

get_point_in_time_restore_config() returns point-in-time restore config:
point_in_time_restore_documented (True), 7 pitr_setup,
9 restore_procedure, and 6 prerequisites.

### Rollback Runbook (Task 68)

get_rollback_runbook_config() returns rollback runbook config:
rollback_runbook_documented (True), 8 runbook_sections,
7 decision_criteria, and 6 communication_plan.

### Staging Rollback Testing (Task 69)

get_staging_rollback_test_config() returns staging rollback test config:
staging_rollback_test_documented (True), 8 test_procedure,
7 validation_checks, and 6 staging_requirements.

### Rollback Procedures Documentation (Task 70)

get_rollback_procedures_documentation_config() returns rollback procedures documentation config:
rollback_procedures_documentation_documented (True), 8 documentation_sections,
6 maintenance_plan, and 6 accessibility_requirements.

### Migration Test Suite (Task 71)

get_migration_test_suite_config() returns migration test suite config:
migration_tests_documented (True), 7 test_categories,
6 coverage_targets, and 6 test_guidelines.

### Public Migration Tests (Task 72)

get_public_migration_test_config() returns public migration test config:
public_migration_tests_documented (True), 7 test_scenarios,
6 expected_outcomes, and 6 validation_queries.

### Tenant Migration Tests (Task 73)

get_tenant_migration_test_config() returns tenant migration test config:
tenant_migration_tests_documented (True), 7 test_scenarios,
6 expected_outcomes, and 6 isolation_checks.

### Parallel Migration Tests (Task 74)

get_parallel_migration_test_config() returns parallel migration test config:
parallel_migration_tests_documented (True), 7 test_scenarios,
6 performance_criteria, and 6 safety_validations.

### Rollback Test Suite (Task 75)

get_rollback_test_suite_config() returns rollback test suite config:
rollback_tests_documented (True), 7 test_scenarios,
6 pass_fail_criteria, and 6 coverage_requirements.

### Data Migration Tests (Task 76)

get_data_migration_test_config() returns data migration test config:
data_migration_tests_documented (True), 7 test_scenarios,
6 validation_criteria, and 6 edge_cases.

### Migration CI Pipeline (Task 77)

get_migration_ci_pipeline_config() returns CI pipeline config:
ci_pipeline_documented (True), 8 pipeline_steps,
6 quality_gates, and 6 pipeline_triggers.

### New Tenant Migration Tests (Task 78)

get_new_tenant_migration_test_config() returns new tenant migration test config:
new_tenant_tests_documented (True), 7 test_scenarios,
6 expected_tables, and 6 validation_steps.

### Large Scale Migration Tests (Task 79)

get_large_scale_migration_test_config() returns large scale migration test config:
large_scale_tests_documented (True), 7 test_scenarios,
6 scale_parameters, and 6 failure_handling.

### Migration Performance Tests (Task 80)

get_migration_performance_test_config() returns performance test config:
performance_tests_documented (True), 7 benchmark_scenarios,
6 acceptable_thresholds, and 6 monitoring_metrics.

### Migration Checklist (Task 81)

get_migration_checklist_config() returns migration checklist config:
checklist_documented (True), 8 pre_deployment_items,
6 post_deployment_items, and 6 checklist_usage.

---

### Migration Best Practices (Task 82)

get_migration_best_practices_config() returns best practices config:
best_practices_documented (True), 7 safety_practices,
6 ownership_roles, and 6 documentation_standards.

---

### Initial Commit Configuration (Task 83)

get_migration_initial_commit_config() returns initial commit config:
initial_commit_documented (True), 6 review_steps,
6 commit_conventions, and 6 included_artifacts.

---

### Final Verification (Task 84)

get_final_verification_config() returns final verification config:
final_verification_documented (True), 7 verification_areas,
6 sign_off_requirements, and 6 completion_criteria.

---

## Related Documentation

- [Database Router Configuration](database-routers.md) -- Schema-aware routing
- [Tenant Settings](tenant-settings.md) -- Multi-tenancy settings
- [App Classification](app-classification.md) -- SHARED vs TENANT app lists
