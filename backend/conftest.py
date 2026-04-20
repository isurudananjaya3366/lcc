"""
Root conftest.py — session-level housekeeping for all pytest runs.

When ``--reuse-db`` is used, tenant records from previous (possibly
interrupted) test sessions can remain in the ``tenants_tenant`` table
even though their PostgreSQL schemas no longer exist.  When
``migrate_schemas`` runs at DB setup time it iterates every tenant
record and tries to create the ``django_migrations`` table inside each
schema; orphan records cause a
``MigrationSchemaMissing: no schema has been selected to create in``
error that makes ALL subsequent test suites fail with 1680+ ERRORs.

The ``django_db_modify_db_settings`` fixture runs just before
``django_db_setup`` actually touches the database; we use it to
connect to the already-existing test database and purge any tenant
rows whose PostgreSQL schema is absent from pg_catalog.pg_namespace.
"""

import pytest
import psycopg
from django.conf import settings


def _purge_orphan_tenants():
    """Connect directly to the test DB and delete orphan tenant rows."""
    db = settings.DATABASES["default"]
    test_name = db.get("TEST", {}).get("NAME") or ("test_" + db["NAME"])

    conn_kwargs = {
        "host": db["HOST"],
        "port": int(db.get("PORT", 5432)),
        "user": db["USER"],
        "password": db["PASSWORD"],
        "dbname": test_name,
    }
    try:
        conn = psycopg.connect(**conn_kwargs, autocommit=True)
    except Exception:
        # DB may not exist yet on a --create-db run — that's fine
        return

    try:
        with conn.cursor() as cur:
            # Get schemas that actually exist in PostgreSQL
            cur.execute("SELECT nspname FROM pg_catalog.pg_namespace")
            existing = {row[0] for row in cur.fetchall()}

            # Check if tenants table is present yet
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name='tenants_tenant')"
            )
            if not cur.fetchone()[0]:
                return

            # Fetch tenant records whose schema is gone
            cur.execute(
                "SELECT id, schema_name FROM tenants_tenant "
                "WHERE schema_name != 'public'"
            )
            orphans = [
                (row[0], row[1])
                for row in cur.fetchall()
                if row[1] not in existing
            ]

            for tenant_id, schema_name in orphans:
                # Delete domain rows (FK)
                cur.execute(
                    "DELETE FROM tenants_domain WHERE tenant_id = %s",
                    (tenant_id,),
                )
                # Delete optional tenant settings
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' "
                    "AND table_name='tenants_tenantsettings')"
                )
                if cur.fetchone()[0]:
                    cur.execute(
                        "DELETE FROM tenants_tenantsettings "
                        "WHERE tenant_id = %s",
                        (tenant_id,),
                    )
                # Delete tenant row
                cur.execute(
                    "DELETE FROM tenants_tenant WHERE id = %s",
                    (tenant_id,),
                )
    finally:
        conn.close()


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Purge orphan tenant records before migrate_schemas runs."""
    _purge_orphan_tenants()
