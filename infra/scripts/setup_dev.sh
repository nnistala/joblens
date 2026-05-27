#!/usr/bin/env bash
# ── JobLens: Local Development Setup ──────────────────────────
# This script bootstraps the entire local dev environment.
# Usage: bash infra/scripts/setup_dev.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Step 1: Check prerequisites ──────────────────────────────
info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker Desktop: https://docs.docker.com/get-docker/"
fi

if ! docker compose version &> /dev/null; then
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose: https://docs.docker.com/compose/install/"
    fi
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

info "Docker and Docker Compose are available."

# ── Step 2: Environment file ─────────────────────────────────
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        info "Created .env from .env.example"
        warn "Review .env and update secrets before deploying to production."
    else
        error ".env.example not found. Cannot create .env file."
    fi
else
    info ".env already exists, skipping copy."
fi

# ── Step 3: Start services ───────────────────────────────────
info "Starting Docker services..."
$COMPOSE_CMD up -d --build

# ── Step 4: Wait for PostgreSQL to be ready ──────────────────
info "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

until $COMPOSE_CMD exec -T postgres pg_isready -U joblens -d joblens > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        error "PostgreSQL did not become ready within ${MAX_RETRIES} seconds."
    fi
    sleep 1
done

info "PostgreSQL is ready."

# ── Step 5: Wait for Redis to be ready ───────────────────────
info "Waiting for Redis to be ready..."
RETRY_COUNT=0

until $COMPOSE_CMD exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        error "Redis did not become ready within ${MAX_RETRIES} seconds."
    fi
    sleep 1
done

info "Redis is ready."

# ── Step 6: Run database migrations ──────────────────────────
info "Running Alembic database migrations..."
$COMPOSE_CMD exec -T api alembic upgrade head || {
    warn "Alembic migrations failed. This may be expected on first run if Alembic is not yet configured."
    warn "You can run migrations manually later with: make migrate"
}

# ── Step 7: Seed companies ───────────────────────────────────
info "Seeding companies into the database..."
$COMPOSE_CMD exec -T api python infra/scripts/seed_companies.py || {
    warn "Company seeding failed. You can run it manually later with: make seed"
}

# ── Step 8: Print summary ────────────────────────────────────
echo ""
echo "========================================"
echo "  JobLens Development Environment"
echo "========================================"
echo ""
info "All services are up and running!"
echo ""
echo "  Frontend:       http://localhost:3000"
echo "  API:            http://localhost:8000"
echo "  API Docs:       http://localhost:8000/docs"
echo "  PostgreSQL:     localhost:5432  (user: joblens / pass: joblens)"
echo "  Redis:          localhost:6379"
echo "  OpenSearch:     http://localhost:9200"
echo ""
echo "Useful commands:"
echo "  make dev          - Start all services (foreground)"
echo "  make down         - Stop all services"
echo "  make shell        - Open shell in API container"
echo "  make shell-db     - Open psql shell"
echo "  make migrate      - Run database migrations"
echo "  make seed         - Seed companies data"
echo "  make test-backend - Run backend tests"
echo "  make lint         - Run linters"
echo ""
