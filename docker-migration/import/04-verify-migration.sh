#!/usr/bin/env bash
# ===========================================================================
# docker-migration/import/04-verify-migration.sh
# ---------------------------------------------------------------------------
# Run this on the DESTINATION PC after all import scripts have completed.
# Verifies that all services are healthy and data was restored correctly.
#
# Usage:
#   bash docker-migration/import/04-verify-migration.sh
# ===========================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPORTS_DIR="${PROJECT_ROOT}/docker-migration/exports"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

PASS=0
FAIL=0
WARN_COUNT=0

log()    { echo -e "${BLUE}[verify]${NC} $*"; }
pass()   { echo -e "  ${GREEN}PASS${NC}  $*"; PASS=$((PASS + 1)); }
fail()   { echo -e "  ${RED}FAIL${NC}  $*"; FAIL=$((FAIL + 1)); }
warn()   { echo -e "  ${YELLOW}WARN${NC}  $*"; WARN_COUNT=$((WARN_COUNT + 1)); }

cd "${PROJECT_ROOT}"

echo ""
echo "=============================================="
echo "  LankaCommerce Docker Migration Verification"
echo "=============================================="
echo ""

# ---------------------------------------------------------------------------
# 1. Container health checks
# ---------------------------------------------------------------------------
log "Checking container status..."
CONTAINERS=(lcc-backend lcc-frontend lcc-postgres lcc-pgbouncer lcc-redis lcc-celery-worker lcc-celery-beat lcc-flower)

for container in "${CONTAINERS[@]}"; do
    STATUS="$(docker inspect --format='{{.State.Status}}' "${container}" 2>/dev/null || echo 'missing')"
    HEALTH="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "${container}" 2>/dev/null || echo 'missing')"

    if [[ "${STATUS}" == "running" ]]; then
        if [[ "${HEALTH}" == "healthy" || "${HEALTH}" == "no-healthcheck" ]]; then
            pass "Container ${container}: ${STATUS} (${HEALTH})"
        else
            warn "Container ${container}: ${STATUS} but health=${HEALTH} (may still be starting)"
        fi
    else
        fail "Container ${container}: ${STATUS}"
    fi
done

echo ""

# ---------------------------------------------------------------------------
# 2. PostgreSQL connectivity
# ---------------------------------------------------------------------------
log "Checking PostgreSQL connectivity..."
if docker compose exec -T db psql -U postgres -c 'SELECT 1;' > /dev/null 2>&1; then
    pass "PostgreSQL: connection successful"
else
    fail "PostgreSQL: cannot connect"
fi

echo ""

# ---------------------------------------------------------------------------
# 3. Database content
# ---------------------------------------------------------------------------
log "Checking database content..."

# Tenant schema count
SCHEMA_COUNT="$(docker compose exec -T db psql -U postgres -d lankacommerce -t \
    -c "SELECT COUNT(*) FROM pg_namespace WHERE nspname LIKE 'tenant_%';" 2>/dev/null | xargs || echo 0)"

if [[ "${SCHEMA_COUNT}" -gt 0 ]]; then
    pass "Tenant schemas found in lankacommerce: ${SCHEMA_COUNT}"
else
    fail "No tenant schemas found in lankacommerce (expected > 0)"
fi

# Compare against export metadata if available
METADATA="$(ls -t "${EXPORTS_DIR}"/export_metadata_*.txt 2>/dev/null | head -1 || true)"
if [[ -n "${METADATA}" ]]; then
    EXPECTED_SCHEMAS="$(grep tenant_schema_count "${METADATA}" 2>/dev/null | cut -d= -f2 || echo 'unknown')"
    if [[ "${EXPECTED_SCHEMAS}" != "unknown" && "${SCHEMA_COUNT}" == "${EXPECTED_SCHEMAS}" ]]; then
        pass "Tenant schema count matches export metadata: ${SCHEMA_COUNT} = ${EXPECTED_SCHEMAS}"
    elif [[ "${EXPECTED_SCHEMAS}" != "unknown" ]]; then
        fail "Tenant schema count mismatch: got ${SCHEMA_COUNT}, expected ${EXPECTED_SCHEMAS}"
    fi
fi

# Key table row counts
for table in tenants_tenant platform_platformuser; do
    COUNT="$(docker compose exec -T db psql -U postgres -d lankacommerce -t \
        -c "SELECT COUNT(*) FROM public.${table};" 2>/dev/null | xargs || echo 'ERROR')"
    if [[ "${COUNT}" != "ERROR" && "${COUNT}" -gt 0 ]]; then
        pass "public.${table}: ${COUNT} rows"
    elif [[ "${COUNT}" == "0" ]]; then
        warn "public.${table}: 0 rows (may be expected if no data was inserted)"
    else
        fail "public.${table}: query failed"
    fi
done

echo ""

# ---------------------------------------------------------------------------
# 4. Redis
# ---------------------------------------------------------------------------
log "Checking Redis..."
if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    KEY_COUNT="$(docker compose exec -T redis redis-cli DBSIZE 2>/dev/null | tr -d '\r')"
    pass "Redis: PONG received (keys: ${KEY_COUNT})"
else
    fail "Redis: not responding to PING"
fi

echo ""

# ---------------------------------------------------------------------------
# 5. Media volume contents
# ---------------------------------------------------------------------------
log "Checking media volume..."
MEDIA_FILES="$(docker run --rm -v lcc-backend-media:/source:ro alpine sh -c 'find /source -type f | wc -l' 2>/dev/null | tr -d ' ' || echo 'ERROR')"
if [[ "${MEDIA_FILES}" != "ERROR" && "${MEDIA_FILES}" -ge 0 ]]; then
    pass "lcc-backend-media volume accessible: ${MEDIA_FILES} files"
else
    fail "lcc-backend-media volume: not accessible"
fi

echo ""

# ---------------------------------------------------------------------------
# 6. Django system check
# ---------------------------------------------------------------------------
log "Running Django system check..."
if docker compose exec -T backend python manage.py check --no-input > /dev/null 2>&1; then
    pass "Django manage.py check: passed"
else
    # Try to get the error output
    CHECK_OUTPUT="$(docker compose exec -T backend python manage.py check --no-input 2>&1 | tail -5 || true)"
    fail "Django manage.py check: failed — ${CHECK_OUTPUT}"
fi

echo ""

# ---------------------------------------------------------------------------
# 7. API health endpoint
# ---------------------------------------------------------------------------
log "Checking API health endpoint..."
HTTP_STATUS="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ 2>/dev/null || echo '000')"
if [[ "${HTTP_STATUS}" == "200" ]]; then
    pass "Backend API health: HTTP ${HTTP_STATUS}"
else
    fail "Backend API health: HTTP ${HTTP_STATUS} (expected 200)"
fi

echo ""

# ---------------------------------------------------------------------------
# 8. Frontend health endpoint
# ---------------------------------------------------------------------------
log "Checking frontend health endpoint..."
FRONTEND_STATUS="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health 2>/dev/null || echo '000')"
if [[ "${FRONTEND_STATUS}" == "200" ]]; then
    pass "Frontend health: HTTP ${FRONTEND_STATUS}"
else
    warn "Frontend health: HTTP ${FRONTEND_STATUS} (may not be ready yet — check logs)"
fi

echo ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "=============================================="
echo "  VERIFICATION SUMMARY"
echo "----------------------------------------------"
echo -e "  ${GREEN}PASSED${NC}: ${PASS}"
echo -e "  ${YELLOW}WARNINGS${NC}: ${WARN_COUNT}"
echo -e "  ${RED}FAILED${NC}: ${FAIL}"
echo "=============================================="

if [[ ${FAIL} -eq 0 && ${WARN_COUNT} -eq 0 ]]; then
    echo -e "${GREEN}Migration verified successfully. The environment is ready.${NC}"
    echo ""
    echo "CLEANUP (optional):"
    echo "  rm -rf docker-migration/exports/"
    exit 0
elif [[ ${FAIL} -eq 0 ]]; then
    echo -e "${YELLOW}Migration complete with warnings. Review warnings above before proceeding.${NC}"
    exit 0
else
    echo -e "${RED}Migration verification FAILED. Review failed checks above.${NC}"
    echo "See DOCKER_MIGRATION_PROPOSAL.md section 10 (Rollback Plan) if needed."
    exit 1
fi
