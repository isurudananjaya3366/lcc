# docker-migration

Tooling for migrating the LankaCommerce Cloud Docker environment to a new machine.

See [DOCKER_MIGRATION_PROPOSAL.md](../DOCKER_MIGRATION_PROPOSAL.md) for the full migration plan and rationale.

---

## Quick Start

### On the SOURCE PC (current machine)

```bash
# From the project root:
bash docker-migration/export/01-export-database.sh
bash docker-migration/export/02-export-redis.sh
bash docker-migration/export/03-export-volumes.sh
cp .env.docker docker-migration/exports/.env.docker
```

Transfer `docker-migration/exports/` to the destination PC.

### On the DESTINATION PC (new machine)

```bash
# From the project root:
cp docker-migration/exports/.env.docker .env.docker
docker compose up -d db pgbouncer redis
docker compose build backend frontend celery-worker celery-beat flower

bash docker-migration/import/01-import-database.sh
bash docker-migration/import/02-import-redis.sh
bash docker-migration/import/03-import-volumes.sh

docker compose up -d
docker compose exec backend python manage.py migrate --no-input
docker compose exec backend python manage.py collectstatic --no-input

bash docker-migration/import/04-verify-migration.sh
```

---

## Directory Structure

```
docker-migration/
├── README.md                  ← This file
├── .gitignore                 ← Excludes exports/ from git
├── exports/                   ← Generated export files (gitignored)
│   └── .gitkeep
├── export/                    ← Run on SOURCE PC
│   ├── 01-export-database.sh
│   ├── 02-export-redis.sh
│   └── 03-export-volumes.sh
└── import/                    ← Run on DESTINATION PC
    ├── 01-import-database.sh
    ├── 02-import-redis.sh
    ├── 03-import-volumes.sh
    └── 04-verify-migration.sh
```

---

## Cleanup After Migration

Once the migration is confirmed working on the destination PC:

```bash
# Delete sensitive export files (DB dumps contain all data)
rm -rf docker-migration/exports/
```

The `docker-migration/` scripts directory can remain for future use.
