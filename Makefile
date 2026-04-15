# =============================================================================
# LankaCommerce Cloud - Makefile
# =============================================================================
# Usage: make [target]
# Run 'make help' to see all available commands
# =============================================================================

.DEFAULT_GOAL := help

# Project variables
COMPOSE = docker compose
COMPOSE_PROD = docker compose -f docker-compose.yml -f docker-compose.prod.yml
BACKEND_EXEC = $(COMPOSE) exec backend
FRONTEND_EXEC = $(COMPOSE) exec frontend
MANAGE = $(BACKEND_EXEC) python manage.py

# =============================================================================
# Help
# =============================================================================

## Show this help message
help:
	@echo ""
	@echo "LankaCommerce Cloud - Available Commands"
	@echo "========================================="
	@echo ""
	@grep -E '^## ' $(MAKEFILE_LIST) | sed -e 's/## //' | while read -r line; do \
		echo "  $$line"; \
	done
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# Docker Commands
# =============================================================================

## Docker Commands:

up: ## Start all containers in detached mode
	$(COMPOSE) up -d

down: ## Stop all containers
	$(COMPOSE) down

build: ## Build all containers
	$(COMPOSE) build

rebuild: ## Rebuild all containers from scratch
	$(COMPOSE) build --no-cache

logs: ## View container logs (follow mode)
	$(COMPOSE) logs -f

up-build: ## Start all containers with build
	$(COMPOSE) up -d --build

logs-backend: ## View backend container logs
	$(COMPOSE) logs -f backend

logs-frontend: ## View frontend container logs
	$(COMPOSE) logs -f frontend

rebuild-frontend: ## Rebuild frontend container from scratch (fixes restart loops)
	$(COMPOSE) stop frontend
	$(COMPOSE) rm -f frontend
	docker volume rm $$(docker volume ls -q --filter name=pos_) 2>/dev/null || true
	$(COMPOSE) build --no-cache frontend
	$(COMPOSE) up -d frontend

logs-service: ## View logs for a specific service (usage: make logs-service s=redis)
	$(COMPOSE) logs -f $(s)

restart: ## Restart all containers
	$(COMPOSE) restart

ps: ## List running containers
	$(COMPOSE) ps

status: ## Show detailed container status and health
	@echo ""
	@echo "Container Status:"
	@echo "================="
	$(COMPOSE) ps -a
	@echo ""
	@echo "Service Health:"
	@echo "==============="
	@docker inspect --format='{{.Name}}: {{if .State.Health}}{{.State.Health.Status}}{{else}}no healthcheck{{end}}' $$(docker compose ps -q 2>/dev/null) 2>/dev/null || echo "No containers running"
	@echo ""

# =============================================================================
# Development Commands
# =============================================================================

## Development Commands:

dev: up ## Start development environment
	@echo "Development environment started!"
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Flower:   http://localhost:5555"

dev-start: ## Start development environment using dev-start.sh
	@bash docker/scripts/dev-start.sh

dev-stop: ## Stop development environment using dev-stop.sh
	@bash docker/scripts/dev-stop.sh

shell: ## Open Django shell
	$(MANAGE) shell

shell-backend: ## Open bash shell in backend container
	$(BACKEND_EXEC) bash

shell-frontend: ## Open sh shell in frontend container
	$(FRONTEND_EXEC) sh

dbshell: ## Open database shell
	$(COMPOSE) exec db psql -U postgres -d lankacommerce

db-reset: ## Reset the development database
	@bash docker/scripts/db-reset.sh

manage: ## Run Django management command (usage: make manage cmd="check")
	$(MANAGE) $(cmd)

migrate: ## Run database migrations
	$(MANAGE) migrate

makemigrations: ## Create new database migrations
	$(MANAGE) makemigrations

createsuperuser: ## Create a Django superuser
	$(MANAGE) createsuperuser

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput

# =============================================================================
# Testing Commands
# =============================================================================

## Testing Commands:

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	$(BACKEND_EXEC) python -m pytest

test-frontend: ## Run frontend tests
	$(FRONTEND_EXEC) npm test

coverage: ## Run backend tests with coverage report
	$(BACKEND_EXEC) python -m pytest --cov --cov-report=html
	@echo "Coverage report generated in backend/htmlcov/"

# =============================================================================
# Code Quality Commands
# =============================================================================

## Code Quality Commands:

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Run Python linters (flake8, ruff, mypy)
	$(BACKEND_EXEC) flake8 .
	$(BACKEND_EXEC) ruff check .
	$(BACKEND_EXEC) mypy .

lint-stats: ## Show flake8 linting statistics
	$(BACKEND_EXEC) flake8 --statistics .

ruff: ## Run Ruff linter check
	$(BACKEND_EXEC) ruff check .

ruff-fix: ## Run Ruff with auto-fix
	$(BACKEND_EXEC) ruff check --fix .

lint-frontend: ## Run frontend linters (ESLint)
	$(FRONTEND_EXEC) npm run lint

format: ## Format all code
	$(BACKEND_EXEC) isort .
	$(BACKEND_EXEC) black .
	$(BACKEND_EXEC) ruff format .
	$(FRONTEND_EXEC) npm run format

format-check: ## Check code formatting without changes
	$(BACKEND_EXEC) isort --check-only --diff .
	$(BACKEND_EXEC) black --check --diff .
	$(BACKEND_EXEC) ruff format --check .

fmt: format ## Alias for format

sort-imports: ## Sort Python imports with isort
	$(BACKEND_EXEC) isort .

sort-imports-check: ## Check import sorting without changes
	$(BACKEND_EXEC) isort --check-only --diff .

lint-fix: ## Format, sort imports, and fix lint issues
	$(BACKEND_EXEC) isort .
	$(BACKEND_EXEC) black .
	$(BACKEND_EXEC) ruff format .
	$(BACKEND_EXEC) ruff check --fix .

typecheck: ## Run mypy type check
	@echo "Running mypy type check..."
	$(BACKEND_EXEC) mypy .
	@echo "Type check complete!"

typecheck-report: ## Generate mypy HTML report
	@echo "Generating mypy report..."
	$(BACKEND_EXEC) mypy . --html-report mypy-report
	@echo "Report generated in mypy-report/"

quality: format sort-imports lint typecheck ## Run all quality checks
	@echo "All quality checks passed!"

quality-fix: lint-fix typecheck ## Format, fix lint, and type check
	@echo "Quality fixes applied!"

# =============================================================================
# Environment Validation Commands
# =============================================================================

## Environment Validation Commands:

validate-env: validate-env-backend validate-env-frontend ## Validate all environment variables
	@echo "All environment validations passed!"

validate-env-backend: ## Validate backend environment variables
	@echo "Validating backend environment..."
	@python scripts/validate_env.py
	@echo ""

validate-env-frontend: ## Validate frontend environment variables
	@echo "Validating frontend environment..."
	@node frontend/scripts/check-env.cjs
	@echo ""

validate-env-strict: ## Validate all env variables in strict (production) mode
	@echo "Running strict environment validation..."
	@python scripts/validate_env.py --strict
	@node frontend/scripts/check-env.cjs --strict
	@echo ""

validate-env-docker: ## Validate Docker environment variables
	@echo "Validating Docker environment..."
	@python scripts/validate_env.py --env-file .env.docker
	@node frontend/scripts/check-env.cjs --env-file .env.docker
	@echo ""

# =============================================================================
# Utility Commands
# =============================================================================

## Utility Commands:

clean: ## Clean temporary files and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned temporary files and caches."

docker-clean: ## Remove all Docker resources (containers, images, volumes)
	$(COMPOSE) down -v --rmi local --remove-orphans
	@echo "Docker resources cleaned."

docker-prune: ## Prune unused Docker resources system-wide
	docker system prune -f
	docker volume prune -f
	@echo "Docker system pruned."

seed: ## Seed the database with sample data
	$(MANAGE) loaddata fixtures/*.json
	@echo "Database seeded successfully."

backup: ## Backup the database (comprehensive, with retention)
	@bash scripts/db-backup.sh
	@echo "Database backup completed. See backups/ directory."

backup-all: ## Backup all databases (main + test)
	@bash scripts/db-backup.sh --all
	@echo "All database backups completed."

restore: ## Restore the database from a backup file (usage: make restore f=backups/daily/lankacommerce_20250101_120000.dump)
	@if [ -z "$(f)" ]; then \
		echo "Usage: make restore f=<backup_file>"; \
		echo "  Latest backup: backups/latest/lankacommerce_latest.dump"; \
		exit 1; \
	fi
	@bash scripts/db-restore.sh $(f)
	@echo "Database restore completed."

restore-latest: ## Restore the database from the latest backup
	@bash scripts/db-restore.sh backups/latest/lankacommerce_latest.dump
	@echo "Database restored from latest backup."

backup-list: ## List available backup files
	@echo ""
	@echo "Available Backups:"
	@echo "=================="
	@echo ""
	@echo "Latest:"
	@ls -lh backups/latest/*.dump 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "Daily:"
	@ls -lh backups/daily/*.dump 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "Weekly:"
	@ls -lh backups/weekly/*.dump 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "Monthly:"
	@ls -lh backups/monthly/*.dump 2>/dev/null || echo "  (none)"
	@echo ""

# =============================================================================
# Tenant Management Commands
# =============================================================================

## Tenant Management Commands:

tenant-list: ## List all tenants with their details
	$(MANAGE) tenant_list

tenant-list-verbose: ## List all tenants with verbose details
	$(MANAGE) tenant_list --verbose

tenant-list-active: ## List only active tenants
	$(MANAGE) tenant_list --status active

tenant-create: ## Create a new tenant (usage: make tenant-create name="Acme" slug="acme")
	@if [ -z "$(name)" ] || [ -z "$(slug)" ]; then \
		echo "Usage: make tenant-create name=\"Business Name\" slug=\"business-slug\""; \
		echo "  Optional: domain=\"custom.domain\" status=\"active\" paid_until=\"2025-12-31\""; \
		exit 1; \
	fi
	$(MANAGE) tenant_create --name "$(name)" --slug "$(slug)" $(if $(domain),--domain "$(domain)") $(if $(status),--status "$(status)") $(if $(paid_until),--paid-until "$(paid_until)")

tenant-migrate-shared: ## Run shared schema migrations
	$(MANAGE) migrate_schemas --shared

tenant-migrate-tenant: ## Run tenant schema migrations
	$(MANAGE) migrate_schemas --tenant

tenant-migrate-all: ## Run all schema migrations (shared + tenant)
	$(MANAGE) migrate_schemas

# =============================================================================
# Production Commands
# =============================================================================

## Production Commands:

prod-up: ## Start production containers
	$(COMPOSE_PROD) up -d

prod-down: ## Stop production containers
	$(COMPOSE_PROD) down

prod-build: ## Build production containers
	$(COMPOSE_PROD) build

prod-logs: ## View production container logs
	$(COMPOSE_PROD) logs -f

# =============================================================================
# Phony Targets
# =============================================================================

.PHONY: help up down build rebuild logs logs-backend logs-frontend logs-service restart ps status \
        dev dev-start dev-stop shell shell-backend shell-frontend dbshell db-reset manage \
        migrate makemigrations createsuperuser collectstatic \
        test test-backend test-frontend coverage \
        lint lint-backend lint-frontend lint-stats ruff ruff-fix format format-check fmt sort-imports sort-imports-check lint-fix \
        typecheck typecheck-report quality quality-fix \
        validate-env validate-env-backend validate-env-frontend validate-env-strict validate-env-docker \
        clean docker-clean docker-prune seed backup restore \
        tenant-list tenant-list-verbose tenant-list-active tenant-create \
        tenant-migrate-shared tenant-migrate-tenant tenant-migrate-all \
        prod-up prod-down prod-build prod-logs up-build
